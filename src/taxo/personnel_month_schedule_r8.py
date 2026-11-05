# -*- coding: utf-8 -*-
"""Taxo 10.10-r8 — simple monthly personnel schedule and filtered views.

One plan remains the source of truth. This module reads driver worklog and
ordinary employee_shifts into one month grid. It never copies unrelated staffing
information into role/personal views.
"""
from __future__ import annotations

import calendar
from datetime import date, datetime, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

from personnel_v91 import NONWORK_OVERRIDE_TYPES
from v91_features import parse_clock, shift_span_minutes

APP_VERSION = "10.10-r8"

VIEW_INTERNAL = "Внутрішній повний"
VIEW_SELECTED = "Вибрані працівники"
VIEW_ROLE = "За роллю"
VIEW_PERSONAL = "Особистий"
VIEW_MODES = (VIEW_INTERNAL, VIEW_SELECTED, VIEW_ROLE, VIEW_PERSONAL)

PATTERN_5_2 = "5/2 (Пн–Пт)"
PATTERN_2_2 = "2/2"
PATTERN_3_3 = "3/3"
SIMPLE_PATTERNS = (PATTERN_5_2, PATTERN_2_2, PATTERN_3_3)


def _text(value):
    return str(value or "").strip()


def _keys(row):
    try:
        return set(row.keys())
    except Exception:
        return set()


def employee_name(row):
    return " ".join(
        _text(row[k]) for k in ("last_name", "first_name", "middle_name")
        if k in _keys(row) and _text(row[k])
    )


def employee_roles(row):
    roles = []
    raw = _text(row["roles"]) if "roles" in _keys(row) else ""
    for role in raw.split(","):
        role = role.strip()
        if role and role not in roles:
            roles.append(role)
    position = _text(row["position"]) if "position" in _keys(row) else ""
    if position and position not in roles:
        roles.append(position)
    if not roles:
        roles.append("Працівник")
    return roles


def active_employee_rows(con):
    cols = {row[1] for row in con.execute("PRAGMA table_info(employees)").fetchall()}
    driver_expr = "" if "driver_id" in cols else ", NULL AS driver_id"
    rows = con.execute(
        f"""SELECT e.*{driver_expr},
                   GROUP_CONCAT(er.role, ', ') AS roles
              FROM employees e
         LEFT JOIN employee_roles er ON er.employee_id=e.id
             WHERE COALESCE(e.active,1)=1
          GROUP BY e.id
          ORDER BY e.last_name,e.first_name,e.middle_name,e.id"""
    ).fetchall()
    return rows


def filtered_employee_rows(con, mode=VIEW_INTERNAL, selected_ids=None, role="", personal_id=None):
    rows = active_employee_rows(con)
    selected = {int(x) for x in (selected_ids or [])}
    if mode == VIEW_INTERNAL:
        return rows
    if mode == VIEW_SELECTED:
        return [row for row in rows if int(row["id"]) in selected]
    if mode == VIEW_ROLE:
        wanted = _text(role).casefold()
        if not wanted:
            return []
        return [
            row for row in rows
            if any(_text(item).casefold() == wanted for item in employee_roles(row))
        ]
    if mode == VIEW_PERSONAL:
        if personal_id is None:
            return []
        return [row for row in rows if int(row["id"]) == int(personal_id)]
    raise ValueError("Невідомий режим графіка.")


def simple_pattern_dates(year, month, pattern):
    year = int(year)
    month = int(month)
    last_day = calendar.monthrange(year, month)[1]
    days = [date(year, month, d) for d in range(1, last_day + 1)]
    if pattern == PATTERN_5_2:
        return [d for d in days if d.weekday() < 5]
    if pattern in (PATTERN_2_2, PATTERN_3_3):
        work = 2 if pattern == PATTERN_2_2 else 3
        rest = work
        cycle = work + rest
        return [d for index, d in enumerate(days) if (index % cycle) < work]
    raise ValueError("Невідома схема простого графіка.")


def _month_range(year, month):
    last = calendar.monthrange(int(year), int(month))[1]
    return (
        date(int(year), int(month), 1),
        date(int(year), int(month), last),
        last,
    )


def _absence_code(day_type):
    text = _text(day_type)
    if not text:
        return ""
    mapping = {
        "Відпустка": "В",
        "Основна щорічна відпустка": "В",
        "Лікарняний": "Л",
        "Оплачувана тимчасова непрацездатність": "Л",
        "Неоплачувана тимчасова непрацездатність": "Л",
        "Відрядження": "ВД",
        "Вихідний": "Вих",
        "Відпочинок": "Вих",
    }
    return mapping.get(text, text[:3])


def _driver_cells(con, driver_id, start, end):
    if not driver_id:
        return {}
    rows = con.execute(
        """SELECT work_date,start_time,end_time,route_name,work_hours
             FROM worklog
            WHERE driver_id=? AND work_date BETWEEN ? AND ?
         ORDER BY work_date,id""",
        (int(driver_id), start.isoformat(), end.isoformat()),
    ).fetchall()
    cells = {}
    for row in rows:
        day = date.fromisoformat(row["work_date"])
        detail = " – ".join(
            x for x in (
                ("%s–%s" % (_text(row["start_time"]), _text(row["end_time"])))
                if _text(row["start_time"]) or _text(row["end_time"]) else "",
                _text(row["route_name"]),
            ) if x
        )
        current = cells.get(day.day)
        if current:
            current["detail"] = "; ".join(x for x in (current["detail"], detail) if x)
            current["code"] = "Р"
        else:
            cells[day.day] = {"code": "Р", "detail": detail, "source": "driver"}
    return cells


def _personnel_shift_cells(con, employee_id, start, end):
    rows = con.execute(
        """SELECT work_date,shift_no,start_time,end_time,role,location,actual_hours,planned_hours
             FROM employee_shifts
            WHERE employee_id=? AND work_date BETWEEN ? AND ?
         ORDER BY work_date,shift_no,id""",
        (int(employee_id), start.isoformat(), end.isoformat()),
    ).fetchall()
    cells = {}
    for row in rows:
        day = date.fromisoformat(row["work_date"])
        shift = "I" if int(row["shift_no"] or 1) == 1 else "II"
        time_text = ""
        if _text(row["start_time"]) or _text(row["end_time"]):
            time_text = "%s–%s" % (_text(row["start_time"]), _text(row["end_time"]))
        detail = " · ".join(
            x for x in (shift, time_text, _text(row["role"]), _text(row["location"])) if x
        )
        current = cells.get(day.day)
        if current:
            current["detail"] = "; ".join(x for x in (current["detail"], detail) if x)
            current["code"] = "Р"
        else:
            cells[day.day] = {"code": "Р", "detail": detail, "source": "personnel"}
    return cells


def _absence_cells(con, employee_id, start, end):
    rows = con.execute(
        """SELECT work_date,day_type,notes
             FROM employee_time_entries
            WHERE employee_id=? AND work_date BETWEEN ? AND ?
         ORDER BY work_date,id""",
        (int(employee_id), start.isoformat(), end.isoformat()),
    ).fetchall()
    cells = {}
    for row in rows:
        day_type = _text(row["day_type"])
        if day_type not in NONWORK_OVERRIDE_TYPES:
            continue
        day = date.fromisoformat(row["work_date"])
        cells[day.day] = {
            "code": _absence_code(day_type),
            "detail": " · ".join(x for x in (day_type, _text(row["notes"])) if x),
            "source": "absence",
        }
    return cells


def month_schedule_rows(con, year, month, *, mode=VIEW_INTERNAL, selected_ids=None, role="", personal_id=None):
    start, end, last_day = _month_range(year, month)
    employees = filtered_employee_rows(
        con,
        mode=mode,
        selected_ids=selected_ids,
        role=role,
        personal_id=personal_id,
    )
    result = []
    for employee in employees:
        cells = {}
        driver_id = employee["driver_id"] if "driver_id" in _keys(employee) else None
        # Driver worklog and ordinary personnel shifts are read into one view.
        cells.update(_driver_cells(con, driver_id, start, end))
        for day_no, cell in _personnel_shift_cells(con, employee["id"], start, end).items():
            if day_no in cells:
                cells[day_no]["detail"] = "; ".join(
                    x for x in (cells[day_no]["detail"], cell["detail"]) if x
                )
            else:
                cells[day_no] = cell
        # Absence wins in the displayed schedule, but the underlying plan remains.
        cells.update(_absence_cells(con, employee["id"], start, end))
        result.append({
            "employee_id": int(employee["id"]),
            "employee_name": employee_name(employee),
            "personnel_no": _text(employee["personnel_no"]) if "personnel_no" in _keys(employee) else "",
            "position": _text(employee["position"]) if "position" in _keys(employee) else "",
            "roles": employee_roles(employee),
            "driver_id": int(driver_id) if driver_id else None,
            "cells": {day: cells.get(day, {"code": "", "detail": "", "source": ""}) for day in range(1, last_day + 1)},
        })
    return result


def apply_simple_plan(
    con,
    employee_ids,
    year,
    month,
    *,
    pattern=PATTERN_5_2,
    start_time="08:00",
    end_time="17:00",
    unpaid_break_minutes=60,
    replace=False,
    note="Простий місячний графік",
):
    """Write simple planned shifts for selected non-driver employees only.

    Driver planning stays in the dedicated driver/route schedule to avoid a
    second competing plan. Existing fact and absences are never overwritten.
    """
    dates = simple_pattern_dates(year, month, pattern)
    selected = {int(x) for x in employee_ids}
    employees = [row for row in active_employee_rows(con) if int(row["id"]) in selected]
    span = shift_span_minutes(_text(start_time), _text(end_time), 0)
    break_minutes = int(unpaid_break_minutes or 0)
    if break_minutes < 0 or break_minutes >= span:
        raise ValueError("Перерва має бути від 0 до тривалості зміни.")
    planned_hours = (span - break_minutes) / 60.0

    added = replaced = skipped = skipped_drivers = 0
    for employee in employees:
        driver_id = employee["driver_id"] if "driver_id" in _keys(employee) else None
        if driver_id:
            skipped_drivers += 1
            continue
        role = employee_roles(employee)[0]
        for work_date in dates:
            absence = con.execute(
                """SELECT day_type FROM employee_time_entries
                    WHERE employee_id=? AND work_date=?""",
                (employee["id"], work_date.isoformat()),
            ).fetchone()
            if absence is not None and _text(absence["day_type"]) in NONWORK_OVERRIDE_TYPES:
                skipped += 1
                continue

            existing = con.execute(
                """SELECT * FROM employee_shifts
                    WHERE employee_id=? AND work_date=?
                 ORDER BY id""",
                (employee["id"], work_date.isoformat()),
            ).fetchall()
            if any(row["actual_hours"] is not None for row in existing):
                skipped += 1
                continue
            if existing and not replace:
                skipped += 1
                continue
            if existing and replace:
                con.executemany(
                    "DELETE FROM employee_shifts WHERE id=? AND actual_hours IS NULL",
                    [(row["id"],) for row in existing],
                )
                replaced += 1

            con.execute(
                """INSERT INTO employee_shifts(
                    employee_id,role,work_date,shift_no,start_time,end_day_offset,end_time,
                    location,unpaid_break_minutes,planned_hours,actual_hours,status,notes
                ) VALUES(?,?,?,?,?,?,?,?,?,?,NULL,'planned',?)""",
                (
                    employee["id"], role, work_date.isoformat(), 1,
                    _text(start_time), 0, _text(end_time), "",
                    break_minutes, planned_hours, _text(note),
                ),
            )
            added += 1

    return {
        "added": added,
        "replaced_days": replaced,
        "skipped": skipped,
        "skipped_drivers": skipped_drivers,
    }


def export_month_schedule_xlsx(path, rows, year, month, title):
    path = Path(path)
    wb = Workbook()
    ws = wb.active
    ws.title = "Графік"
    last_day = calendar.monthrange(int(year), int(month))[1]
    ws.append([title])
    ws.append(["Місяць", "%02d.%04d" % (int(month), int(year))])
    ws.append([])
    headers = ["Працівник", "Посада"] + [str(day) for day in range(1, last_day + 1)]
    ws.append(headers)
    for cell in ws[4]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for row in rows:
        values = [row["employee_name"], row["position"]]
        values.extend(row["cells"][day]["code"] or "" for day in range(1, last_day + 1))
        ws.append(values)
    ws.freeze_panes = "C5"
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 22
    for col in range(3, 3 + last_day):
        ws.column_dimensions[ws.cell(4, col).column_letter].width = 4
    for row in ws.iter_rows(min_row=5, min_col=3):
        for cell in row:
            cell.alignment = Alignment(horizontal="center", vertical="center")
    wb.save(path)
    return path


def install(core, base_app):
    if getattr(core, "_TAXO_1010_R8_SIMPLE_MONTH_SCHEDULE", False):
        return core.App
    core.APP_VERSION = APP_VERSION

    class Taxo1010R8App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)
            self._install_simple_month_schedule_r8()

        def _install_simple_month_schedule_r8(self):
            root = getattr(self, "personnel_planning_page", None)
            if root is None:
                root = getattr(self, "personnel_overview_page", None)
            if root is None or getattr(self, "_simple_month_schedule_r8_installed", False):
                return
            anchor = None
            stack = [root]
            while stack:
                widget = stack.pop()
                try:
                    children = widget.winfo_children()
                except Exception:
                    continue
                stack.extend(children)
                try:
                    if widget.winfo_class() in ("TButton", "Button") and str(widget.cget("text")) == "Робочі зміни персоналу — масово…":
                        anchor = widget
                        break
                except Exception:
                    pass
            if anchor is None:
                return
            core.ttk.Button(
                anchor.master,
                text="Простий місячний графік…",
                style="Accent.TButton",
                command=self.open_simple_month_schedule_r8,
            ).pack(anchor="w", pady=4)
            self._simple_month_schedule_r8_installed = True

        def open_simple_month_schedule_r8(self):
            existing = getattr(self, "_simple_month_schedule_r8_window", None)
            try:
                if existing is not None and existing.winfo_exists():
                    existing.lift()
                    return
            except Exception:
                pass

            win = core.tk.Toplevel(self)
            self._simple_month_schedule_r8_window = win
            win.title("Простий місячний графік працівників")
            core.fit_window_to_screen(win, 1420, 820, 980, 620)
            body = core.ttk.Frame(win, padding=10)
            body.pack(fill="both", expand=True)
            body.rowconfigure(2, weight=1)
            body.columnconfigure(0, weight=1)

            now = date.today()
            month_var = core.tk.StringVar(value=str(now.month))
            year_var = core.tk.StringVar(value=str(now.year))
            mode_var = core.tk.StringVar(value=VIEW_INTERNAL)
            role_var = core.tk.StringVar(value="")
            pattern_var = core.tk.StringVar(value=PATTERN_5_2)
            start_var = core.tk.StringVar(value="08:00")
            end_var = core.tk.StringVar(value="17:00")
            break_var = core.tk.StringVar(value="60")
            replace_var = core.tk.BooleanVar(value=False)

            header = core.ttk.Frame(body)
            header.grid(row=0, column=0, sticky="ew")
            core.ttk.Label(header, text="Простий місячний графік", style="Title.TLabel").pack(side="left")
            core.ttk.Label(header, text="Місяць").pack(side="left", padx=(18, 3))
            core.ttk.Spinbox(header, textvariable=month_var, from_=1, to=12, width=4).pack(side="left")
            core.ttk.Label(header, text="Рік").pack(side="left", padx=(8, 3))
            core.ttk.Spinbox(header, textvariable=year_var, from_=2020, to=2100, width=6).pack(side="left")
            core.ttk.Label(header, text="Вид").pack(side="left", padx=(12, 3))
            core.ttk.Combobox(header, textvariable=mode_var, values=VIEW_MODES, state="readonly", width=22).pack(side="left")
            role_box = core.ttk.Combobox(header, textvariable=role_var, state="readonly", width=22)
            role_box.pack(side="left", padx=6)

            core.ttk.Label(
                body,
                text=(
                    "«Внутрішній повний» показує весь склад. «За роллю», «Вибрані працівники» та «Особистий» "
                    "показують тільки відповідних людей — службова нестача інших посад у такі графіки не потрапляє. "
                    "Водійський план читається з чинного графіка водіїв і тут не дублюється."
                ),
                style="Muted.TLabel", wraplength=1360, justify="left",
            ).grid(row=1, column=0, sticky="ew", pady=(5, 8))

            split = core.ttk.Panedwindow(body, orient="horizontal")
            split.grid(row=2, column=0, sticky="nsew")
            left = core.ttk.Frame(split, padding=(0, 0, 7, 0))
            right = core.ttk.Frame(split, padding=(7, 0, 0, 0))
            split.add(left, weight=1)
            split.add(right, weight=4)
            left.rowconfigure(1, weight=1)
            left.columnconfigure(0, weight=1)
            right.rowconfigure(0, weight=1)
            right.columnconfigure(0, weight=1)

            core.ttk.Label(left, text="Працівники — Ctrl/Shift для кількох").grid(row=0, column=0, sticky="w")
            emp_tree = core.ttk.Treeview(left, columns=("name", "role"), show="headings", selectmode="extended", height=20)
            emp_tree.heading("name", text="Працівник")
            emp_tree.heading("role", text="Роль / посада")
            emp_tree.column("name", width=220, anchor="w")
            emp_tree.column("role", width=150, anchor="w")
            ey = core.ttk.Scrollbar(left, orient="vertical", command=emp_tree.yview)
            emp_tree.configure(yscrollcommand=ey.set)
            emp_tree.grid(row=1, column=0, sticky="nsew")
            ey.grid(row=1, column=1, sticky="ns")

            schedule_frame = core.ttk.Frame(right)
            schedule_frame.grid(row=0, column=0, sticky="nsew")
            schedule_frame.rowconfigure(0, weight=1)
            schedule_frame.columnconfigure(0, weight=1)
            schedule_tree = None
            employee_cache = {}
            current_rows = []

            def load_employees():
                nonlocal employee_cache
                for iid in emp_tree.get_children(""):
                    emp_tree.delete(iid)
                con = core.db()
                try:
                    rows = active_employee_rows(con)
                finally:
                    con.close()
                employee_cache = {int(row["id"]): row for row in rows}
                roles = sorted({role for row in rows for role in employee_roles(row)})
                role_box.configure(values=roles)
                if role_var.get() not in roles:
                    role_var.set(roles[0] if roles else "")
                for row in rows:
                    emp_tree.insert(
                        "", "end", iid=str(row["id"]),
                        values=(employee_name(row), ", ".join(employee_roles(row))),
                    )

            def selected_ids():
                out = []
                for iid in emp_tree.selection():
                    try:
                        out.append(int(iid))
                    except ValueError:
                        pass
                return out

            def view_parameters():
                mode = mode_var.get()
                ids = selected_ids()
                personal_id = ids[0] if ids else None
                return mode, ids, role_var.get(), personal_id

            def render():
                nonlocal schedule_tree, current_rows
                try:
                    year = int(year_var.get())
                    month = int(month_var.get())
                    calendar.monthrange(year, month)
                except Exception:
                    core.messagebox.showerror("Графік", "Перевірте місяць і рік.", parent=win)
                    return
                mode, ids, role, personal_id = view_parameters()
                if mode in (VIEW_SELECTED, VIEW_PERSONAL) and not ids:
                    core.messagebox.showinfo("Графік", "Виберіть працівника або кількох працівників ліворуч.", parent=win)
                    return
                con = core.db()
                try:
                    current_rows = month_schedule_rows(
                        con, year, month, mode=mode,
                        selected_ids=ids, role=role, personal_id=personal_id,
                    )
                finally:
                    con.close()

                if schedule_tree is not None:
                    schedule_tree.destroy()
                for child in schedule_frame.grid_slaves():
                    child.destroy()

                last_day = calendar.monthrange(year, month)[1]
                cols = ("employee",) + tuple("d%d" % d for d in range(1, last_day + 1))
                schedule_tree = core.ttk.Treeview(
                    schedule_frame, columns=cols, show="headings", selectmode="browse"
                )
                schedule_tree.heading("employee", text="Працівник")
                schedule_tree.column("employee", width=230, anchor="w", stretch=False)
                for day in range(1, last_day + 1):
                    key = "d%d" % day
                    schedule_tree.heading(key, text=str(day))
                    schedule_tree.column(key, width=42, anchor="center", stretch=False)
                sy = core.ttk.Scrollbar(schedule_frame, orient="vertical", command=schedule_tree.yview)
                sx = core.ttk.Scrollbar(schedule_frame, orient="horizontal", command=schedule_tree.xview)
                schedule_tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
                schedule_tree.grid(row=0, column=0, sticky="nsew")
                sy.grid(row=0, column=1, sticky="ns")
                sx.grid(row=1, column=0, sticky="ew")
                for row in current_rows:
                    values = [row["employee_name"]]
                    values.extend(row["cells"][day]["code"] or "·" for day in range(1, last_day + 1))
                    schedule_tree.insert("", "end", iid=str(row["employee_id"]), values=values)

            planner = core.ttk.LabelFrame(body, text="Швидко запланувати вибраних працівників", padding=8)
            planner.grid(row=3, column=0, sticky="ew", pady=(8, 0))
            core.ttk.Label(planner, text="Схема").pack(side="left")
            core.ttk.Combobox(planner, textvariable=pattern_var, values=SIMPLE_PATTERNS, state="readonly", width=15).pack(side="left", padx=4)
            core.ttk.Label(planner, text="Початок").pack(side="left", padx=(8, 3))
            core.ttk.Entry(planner, textvariable=start_var, width=7).pack(side="left")
            core.ttk.Label(planner, text="Кінець").pack(side="left", padx=(8, 3))
            core.ttk.Entry(planner, textvariable=end_var, width=7).pack(side="left")
            core.ttk.Label(planner, text="Перерва, хв").pack(side="left", padx=(8, 3))
            core.ttk.Entry(planner, textvariable=break_var, width=5).pack(side="left")
            core.ttk.Checkbutton(planner, text="Замінити лише існуючий план (факт не чіпати)", variable=replace_var).pack(side="left", padx=8)

            def apply_plan():
                ids = selected_ids()
                if not ids:
                    core.messagebox.showinfo("Графік", "Виберіть працівників ліворуч.", parent=win)
                    return
                try:
                    year = int(year_var.get())
                    month = int(month_var.get())
                    break_minutes = int(break_var.get() or 0)
                except ValueError:
                    core.messagebox.showerror("Графік", "Перевірте рік, місяць і перерву.", parent=win)
                    return
                if not core.messagebox.askyesno(
                    "Записати простий план?",
                    "Запланувати вибраних працівників за схемою %s?\n\n"
                    "Фактичні зміни та відсутності не перезаписуються. Водії будуть пропущені, "
                    "бо їхній план ведеться у «Графіку водіїв»." % pattern_var.get(),
                    parent=win,
                ):
                    return
                try:
                    backup = getattr(core, "backup_database", None)
                    if callable(backup):
                        backup("before_simple_month_schedule")
                except Exception as exc:
                    if not core.messagebox.askyesno(
                        "Резервна копія",
                        "Не вдалося створити резервну копію перед масовою зміною:\n%s\n\nПродовжити без неї?" % exc,
                        parent=win,
                    ):
                        return
                con = core.db()
                try:
                    result = apply_simple_plan(
                        con, ids, year, month,
                        pattern=pattern_var.get(),
                        start_time=start_var.get(),
                        end_time=end_var.get(),
                        unpaid_break_minutes=break_minutes,
                        replace=replace_var.get(),
                    )
                    con.commit()
                except Exception as exc:
                    con.rollback()
                    core.messagebox.showerror("Графік", str(exc), parent=win)
                    return
                finally:
                    con.close()
                render()
                core.messagebox.showinfo(
                    "Графік",
                    "Додано змін: %d\nЗамінено планових днів: %d\nПропущено: %d\n"
                    "Водіїв не дубльовано: %d"
                    % (
                        result["added"], result["replaced_days"],
                        result["skipped"], result["skipped_drivers"],
                    ),
                    parent=win,
                )

            core.ttk.Button(planner, text="Запланувати вибраних", style="Accent.TButton", command=apply_plan).pack(side="right")

            footer = core.ttk.Frame(body)
            footer.grid(row=4, column=0, sticky="ew", pady=(8, 0))
            core.ttk.Button(footer, text="Оновити графік", command=render).pack(side="left")

            def export_xlsx():
                if not current_rows:
                    render()
                if not current_rows:
                    return
                mode, ids, role, personal_id = view_parameters()
                path = core.filedialog.asksaveasfilename(
                    parent=win,
                    title="Зберегти місячний графік",
                    defaultextension=".xlsx",
                    filetypes=(("Excel XLSX", "*.xlsx"),),
                    initialfile="Taxo_графік_%s_%s.xlsx" % (year_var.get(), month_var.get()),
                )
                if not path:
                    return
                title = "Місячний графік — %s" % mode
                export_month_schedule_xlsx(path, current_rows, int(year_var.get()), int(month_var.get()), title)
                core.messagebox.showinfo("Графік", "Файл збережено:\n%s" % path, parent=win)

            core.ttk.Button(footer, text="Зберегти цей вигляд у Excel…", command=export_xlsx).pack(side="left", padx=6)
            core.ttk.Button(footer, text="Закрити", command=win.destroy).pack(side="right")

            mode_var.trace_add("write", lambda *_args: render())
            role_box.bind("<<ComboboxSelected>>", lambda _e: render())
            emp_tree.bind("<<TreeviewSelect>>", lambda _e: render() if mode_var.get() in (VIEW_SELECTED, VIEW_PERSONAL) else None)
            load_employees()
            render()
            win.transient(self)

    Taxo1010R8App.__name__ = "App"
    Taxo1010R8App.__qualname__ = "App"
    core.App = Taxo1010R8App
    core._TAXO_1010_R8_SIMPLE_MONTH_SCHEDULE = True
    return Taxo1010R8App
