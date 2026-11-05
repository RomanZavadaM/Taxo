# -*- coding: utf-8 -*-
"""Taxo 10.10-r8 — simple monthly personnel schedule.

The simple planner is intentionally additive. Driver work remains owned by the
specialized driver schedule. For other personnel, the planner writes the same
employee_shifts rows already used by the detailed personnel planner.

Employee-facing exports are privacy-filtered: they contain only the selected
employees and never include internal staffing warnings or missing-role notes.
"""
from __future__ import annotations

import calendar
from datetime import date, datetime, timedelta
from pathlib import Path

from v91_features import (
    PATTERN_DAILY,
    PATTERN_WEEKDAYS,
    PATTERN_SELECTED,
    PATTERN_2_2,
    PATTERN_CUSTOM,
    WEEKDAY_NAMES,
    pattern_dates,
    parse_clock,
    shift_span_minutes,
)
from personnel_v91 import (
    NONWORK_OVERRIDE_TYPES,
    driver_plan_conflict,
)
from output_files import report_font_candidates

APP_VERSION = "10.10-r8"

PATTERN_3_3 = "3/3"
SIMPLE_PATTERNS = (
    PATTERN_WEEKDAYS,
    PATTERN_2_2,
    PATTERN_3_3,
    PATTERN_DAILY,
    PATTERN_SELECTED,
)

VIEW_INTERNAL = "internal"
VIEW_EMPLOYEE = "employee"

ABSENCE_CODES = {
    "Вихідний": "Вих",
    "Відпустка": "В",
    "Основна щорічна відпустка": "В",
    "Щорічна додаткова відпустка": "Д",
    "Додаткова оплачувана відпустка працівникам з дітьми": "ДО",
    "Творча відпустка": "ТВ",
    "Додаткова відпустка у зв’язку з навчанням": "Н",
    "Відпустка без збереження зарплати у зв’язку з навчанням": "НБ",
    "Відпустка без збереження зарплати в обов’язковому порядку": "ДБ",
    "Відпустка без збереження зарплати за згодою сторін": "НА",
    "Інші відпустки без збереження зарплати": "БЗ",
    "Відпустка у зв’язку з вагітністю і пологами / догляд до 3 років": "ВП",
    "Відпустка для догляду за дитиною до 6 років": "ДД",
    "Лікарняний": "ТН",
    "Оплачувана тимчасова непрацездатність": "ТН",
    "Неоплачувана тимчасова непрацездатність": "НН",
    "Відрядження": "ВД",
    "Простій": "П",
    "Прогул": "ПР",
    "Страйк": "С",
    "Неявка з нез’ясованих причин": "НЗ",
    "Інша причина неявки": "І",
    "Відпочинок": "Відп",
}


def _text(value):
    return str(value or "").strip()


def _employee_name(row):
    return " ".join(
        _text(row[key])
        for key in ("last_name", "first_name", "middle_name")
        if _text(row[key])
    )


def _employee_rows(con, active_only=True):
    sql = """SELECT e.*, GROUP_CONCAT(er.role, ', ') AS roles
               FROM employees e
          LEFT JOIN employee_roles er ON er.employee_id=e.id"""
    if active_only:
        sql += " WHERE COALESCE(e.active,1)=1"
    sql += " GROUP BY e.id ORDER BY e.active DESC,e.last_name,e.first_name,e.middle_name,e.id"
    return con.execute(sql).fetchall()


def _roles(row):
    values = []
    for item in _text(row["roles"]).split(","):
        item = item.strip()
        if item and item not in values:
            values.append(item)
    position = _text(row["position"]) if "position" in row.keys() else ""
    if position and position not in values:
        values.append(position)
    return values


def simple_plan_role(row):
    """Return one safe non-driver role for the simple planner.

    Driver-only employees stay in the monthly view but are planned in the
    specialized driver schedule, so the simple planner never duplicates their
    route/worklog plan.
    """
    # Linked drivers use the dedicated driver schedule, not a parallel bulk plan.
    # The position title can differ from the historical role name.
    if row["driver_id"] is not None:
        return "", "Водій — робочі зміни беруться з графіка водіїв"
    roles = _roles(row)
    non_driver = [role for role in roles if role != "Водій"]
    if len(non_driver) == 1:
        return non_driver[0], ""
    if len(non_driver) > 1:
        return "", "Кілька ролей — використайте детальний планувальник"
    if "Водій" in roles or row["driver_id"]:
        return "", "Водій — робочі зміни беруться з графіка водіїв"
    return "", "Не визначено роль працівника"


def month_days(year, month):
    count = calendar.monthrange(int(year), int(month))[1]
    return [date(int(year), int(month), d) for d in range(1, count + 1)]


def selected_pattern_dates(year, month, pattern, *, anchor_day=1, weekdays=None):
    days = month_days(year, month)
    first = days[0]
    last = days[-1]
    anchor_day = max(1, min(int(anchor_day), last.day))
    start = date(first.year, first.month, anchor_day)

    result = []
    # Before the anchor there is intentionally no generated cycle.
    if pattern == PATTERN_3_3:
        result = pattern_dates(
            start, last, PATTERN_CUSTOM, work_days=3, rest_days=3
        )
    else:
        result = pattern_dates(
            start,
            last,
            pattern,
            weekdays=weekdays,
        )
    return result


def _interval(start_day, start_time, end_time):
    start_min = parse_clock(start_time)
    end_min = parse_clock(end_time)
    end_offset = 0 if end_min > start_min else 1
    start_dt = datetime.combine(start_day, datetime.min.time()) + timedelta(minutes=start_min)
    end_dt = (
        datetime.combine(start_day + timedelta(days=end_offset), datetime.min.time())
        + timedelta(minutes=end_min)
    )
    return start_dt, end_dt, end_offset


def _other_shift_conflict(con, employee_id, start_dt, end_dt, ignore_ids=()):
    rows = con.execute(
        """SELECT * FROM employee_shifts
            WHERE employee_id=? AND work_date BETWEEN ? AND ?""",
        (
            int(employee_id),
            (start_dt.date() - timedelta(days=1)).isoformat(),
            end_dt.date().isoformat(),
        ),
    ).fetchall()
    ignored = {int(x) for x in ignore_ids}
    for row in rows:
        if int(row["id"]) in ignored:
            continue
        base = date.fromisoformat(row["work_date"])
        row_start = datetime.combine(base, datetime.min.time()) + timedelta(
            minutes=parse_clock(row["start_time"])
        )
        row_end = datetime.combine(
            base + timedelta(days=int(row["end_day_offset"] or 0)),
            datetime.min.time(),
        ) + timedelta(minutes=parse_clock(row["end_time"]))
        if start_dt < row_end and row_start < end_dt:
            return row
    return None


def apply_simple_month_plan(
    core,
    con,
    employee_ids,
    year,
    month,
    *,
    pattern=PATTERN_WEEKDAYS,
    anchor_day=1,
    weekdays=None,
    start_time="08:00",
    end_time="17:00",
    unpaid_break_minutes=60,
    replace=False,
):
    """Create simple monthly shifts for selected non-driver personnel.

    Existing fact, absences, driver-route conflicts and another-role overlaps
    are never overwritten. Driver-only personnel are intentionally skipped.
    """
    selected = {int(x) for x in employee_ids}
    rows = {int(row["id"]): row for row in _employee_rows(con, active_only=True) if int(row["id"]) in selected}
    dates = selected_pattern_dates(
        year,
        month,
        pattern,
        anchor_day=anchor_day,
        weekdays=weekdays,
    )
    span = shift_span_minutes(start_time, end_time, 0 if parse_clock(end_time) > parse_clock(start_time) else 1)
    unpaid = int(unpaid_break_minutes or 0)
    if unpaid < 0 or unpaid >= span:
        raise ValueError("Неоплачувана перерва має бути меншою за тривалість зміни.")
    planned_hours = (span - unpaid) / 60.0
    stamp = datetime.now().isoformat(timespec="seconds")

    result = {
        "selected_employees": len(selected),
        "work_dates": len(dates),
        "added": 0,
        "replaced": 0,
        "skipped_driver": 0,
        "skipped_role": 0,
        "skipped_absence": 0,
        "skipped_fact": 0,
        "skipped_existing": 0,
        "skipped_conflict": 0,
    }

    for employee_id in sorted(selected):
        employee = rows.get(employee_id)
        if employee is None:
            result["skipped_role"] += len(dates)
            continue
        role, reason = simple_plan_role(employee)
        if not role:
            key = "skipped_driver" if "Водій" in reason else "skipped_role"
            result[key] += len(dates)
            continue

        for work_date in dates:
            if hasattr(core, "employee_employed_on") and not core.employee_employed_on(employee, work_date):
                result["skipped_role"] += 1
                continue

            absence = con.execute(
                """SELECT day_type FROM employee_time_entries
                    WHERE employee_id=? AND work_date=?""",
                (employee_id, work_date.isoformat()),
            ).fetchone()
            if absence and _text(absence["day_type"]) in NONWORK_OVERRIDE_TYPES:
                result["skipped_absence"] += 1
                continue

            own = con.execute(
                """SELECT * FROM employee_shifts
                    WHERE employee_id=? AND role=? AND work_date=? AND shift_no=1
                 ORDER BY id""",
                (employee_id, role, work_date.isoformat()),
            ).fetchall()
            if any(row["actual_hours"] is not None for row in own):
                result["skipped_fact"] += 1
                continue
            if own and not replace:
                result["skipped_existing"] += 1
                continue

            start_dt, end_dt, end_offset = _interval(work_date, start_time, end_time)
            own_ids = [row["id"] for row in own]
            conflict = _other_shift_conflict(
                con, employee_id, start_dt, end_dt, ignore_ids=own_ids
            )
            if conflict is not None:
                result["skipped_conflict"] += 1
                continue

            driver_conflict = driver_plan_conflict(core, con, employee, start_dt, end_dt)
            if driver_conflict is not None:
                # Unknown driver clock time is not safe enough for automatic bulk plan.
                result["skipped_conflict"] += 1
                continue

            if own and replace:
                con.executemany(
                    "DELETE FROM employee_shifts WHERE id=? AND actual_hours IS NULL",
                    [(row["id"],) for row in own],
                )

            con.execute(
                """INSERT INTO employee_shifts(
                       employee_id,role,work_date,shift_no,start_time,end_day_offset,end_time,
                       location,unpaid_break_minutes,planned_hours,actual_hours,status,notes
                   ) VALUES(?,?,?,?,?,?,?,?,?,?,NULL,'planned',?)""",
                (
                    employee_id,
                    role,
                    work_date.isoformat(),
                    1,
                    start_time,
                    end_offset,
                    end_time,
                    "",
                    unpaid,
                    planned_hours,
                    "Простий місячний графік",
                ),
            )
            if own and replace:
                result["replaced"] += 1
            else:
                result["added"] += 1

    return result


def _short_day_cell(core, con, employee, work_date):
    if hasattr(core, "employee_employed_on") and not core.employee_employed_on(employee, work_date):
        return ""

    entry = con.execute(
        """SELECT * FROM employee_time_entries
            WHERE employee_id=? AND work_date=?""",
        (employee["id"], work_date.isoformat()),
    ).fetchone()
    if entry and _text(entry["day_type"]) in ABSENCE_CODES:
        return ABSENCE_CODES[_text(entry["day_type"])]

    row = core.employee_day_time(con, employee["id"], work_date)
    if row["planned_minutes"] > 0:
        return "Р"
    if entry and _text(entry["day_type"]) and _text(entry["day_type"]) != "Робота":
        return ABSENCE_CODES.get(_text(entry["day_type"]), _text(entry["day_type"])[:3])
    return "Вих"


def collect_month_schedule(core, con, year, month, employee_ids=None, *, view=VIEW_INTERNAL):
    """Collect a privacy-filtered schedule grid.

    view=employee deliberately omits every internal note and every employee not
    explicitly selected by employee_ids.
    """
    all_rows = _employee_rows(con, active_only=True)
    selected = None if employee_ids is None else {int(x) for x in employee_ids}
    if view == VIEW_EMPLOYEE and selected is None:
        raise ValueError("Для графіка працівників потрібно явно вибрати працівників.")

    employees = []
    days = month_days(year, month)
    for employee in all_rows:
        employee_id = int(employee["id"])
        if selected is not None and employee_id not in selected:
            continue
        cells = [_short_day_cell(core, con, employee, d) for d in days]
        employees.append(
            {
                "employee_id": employee_id,
                "personnel_no": _text(employee["personnel_no"]),
                "name": _employee_name(employee),
                "roles": ", ".join(_roles(employee)),
                "cells": cells,
            }
        )

    return {
        "year": int(year),
        "month": int(month),
        "days": days,
        "employees": employees,
        "view": view,
        # Reserved for manager-only diagnostics. Employee-facing views always
        # receive an empty list by contract.
        "internal_notes": [] if view == VIEW_EMPLOYEE else _internal_schedule_notes(con, year, month),
    }


def _internal_schedule_notes(con, year, month):
    """Return only real scheduling conflicts, never guessed staffing shortages."""
    first = date(int(year), int(month), 1)
    last = date(int(year), int(month), calendar.monthrange(int(year), int(month))[1])
    rows = con.execute(
        """SELECT work_date,role,shift_no,COUNT(*) AS n
             FROM employee_shifts
            WHERE work_date BETWEEN ? AND ?
         GROUP BY work_date,role,shift_no
           HAVING COUNT(*)>1
         ORDER BY work_date,role,shift_no""",
        (first.isoformat(), last.isoformat()),
    ).fetchall()
    notes = []
    for row in rows:
        notes.append(
            "%s · %s · зміна %s: %s призначень"
            % (
                row["work_date"],
                row["role"],
                "I" if int(row["shift_no"] or 1) == 1 else "II",
                row["n"],
            )
        )
    return notes


def export_employee_schedule_xlsx(data, out_path):
    """Export selected employee schedule; internal notes are intentionally omitted."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Графік"
    days = data["days"]
    ws.cell(1, 1, "ГРАФІК РОБОТИ")
    ws.cell(2, 1, "%02d.%04d" % (data["month"], data["year"]))
    ws.cell(4, 1, "Таб. №")
    ws.cell(4, 2, "Працівник")
    ws.cell(4, 3, "Роль")
    for idx, day in enumerate(days, start=4):
        ws.cell(4, idx, day.day)
        ws.cell(5, idx, WEEKDAY_NAMES[day.weekday()])
    for col in range(1, 4 + len(days)):
        ws.cell(4, col).font = Font(bold=True)
        ws.cell(4, col).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(5, col).alignment = Alignment(horizontal="center", vertical="center")

    row_no = 6
    for employee in data["employees"]:
        ws.cell(row_no, 1, employee["personnel_no"])
        ws.cell(row_no, 2, employee["name"])
        ws.cell(row_no, 3, employee["roles"])
        for offset, value in enumerate(employee["cells"], start=4):
            ws.cell(row_no, offset, value)
            ws.cell(row_no, offset).alignment = Alignment(horizontal="center")
        row_no += 1

    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 22
    for col in range(4, 4 + len(days)):
        ws.column_dimensions[get_column_letter(col)].width = 4.2
    ws.freeze_panes = "D6"
    ws.sheet_view.showGridLines = False
    wb.save(str(out_path))
    return out_path


def export_employee_schedule_pdf(data, out_path):
    """Export selected employee schedule without internal staffing diagnostics."""
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from xml.sax.saxutils import escape

    font_name = "Helvetica"
    font_path = next((p for p in report_font_candidates() if Path(p).exists()), None)
    if font_path:
        try:
            if "TaxoScheduleFont" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("TaxoScheduleFont", str(font_path)))
            font_name = "TaxoScheduleFont"
        except Exception:
            pass

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=landscape(A4),
        leftMargin=14,
        rightMargin=14,
        topMargin=14,
        bottomMargin=14,
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TaxoScheduleTitle", parent=styles["Heading2"], fontName=font_name,
        fontSize=11, leading=13, alignment=1
    )
    normal = ParagraphStyle(
        "TaxoScheduleNormal", parent=styles["Normal"], fontName=font_name,
        fontSize=6.8, leading=8
    )
    center = ParagraphStyle(
        "TaxoScheduleCenter", parent=normal, alignment=1
    )
    story = [
        Paragraph("<b>ГРАФІК РОБОТИ</b>", title),
        Paragraph("%02d.%04d" % (data["month"], data["year"]), title),
        Spacer(1, 5),
    ]
    days = data["days"]

    # Split the month into two readable blocks instead of squeezing 31 days.
    for start_index, end_index in ((0, 16), (16, len(days))):
        if start_index >= len(days):
            continue
        block_days = days[start_index:end_index]
        headers = [
            Paragraph("<b>Працівник</b>", center),
            Paragraph("<b>Роль</b>", center),
        ] + [Paragraph("<b>%02d<br/>%s</b>" % (d.day, WEEKDAY_NAMES[d.weekday()]), center) for d in block_days]
        rows = [headers]
        for employee in data["employees"]:
            values = [
                Paragraph(escape(employee["name"]), normal),
                Paragraph(escape(employee["roles"]), normal),
            ]
            values += [
                Paragraph(escape(str(value)), center)
                for value in employee["cells"][start_index:end_index]
            ]
            rows.append(values)

        page_width = landscape(A4)[0] - 28
        fixed = 135 + 90
        day_width = max(18, (page_width - fixed) / max(1, len(block_days)))
        table = Table(rows, colWidths=[135, 90] + [day_width] * len(block_days), repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 7))

    doc.build(story)
    return out_path


def install(core, base_app):
    if getattr(core, "_TAXO_1010_R8_SIMPLE_MONTH_SCHEDULE", False):
        return core.App
    core.APP_VERSION = APP_VERSION

    class Taxo1010R8App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)
            self._install_simple_schedule_action_r8()

        def _install_simple_schedule_action_r8(self):
            root = getattr(self, "personnel_planning_page", None)
            if root is None:
                # Older composition keeps a reference only to the main personnel page.
                root = getattr(self, "personnel_overview_page", None)
            if root is None or getattr(self, "_simple_schedule_r8_installed", False):
                return

            def walk(widget):
                for child in widget.winfo_children():
                    yield child
                    yield from walk(child)

            anchor = None
            for widget in walk(root):
                try:
                    if widget.winfo_class() in ("TButton", "Button") and str(widget.cget("text")) == "Робочі зміни персоналу — масово…":
                        anchor = widget
                        break
                except Exception:
                    pass
            if anchor is None:
                # The planning tab may not be reachable from the overview widget tree.
                for widget in walk(self):
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
            self._simple_schedule_r8_installed = True

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
            try:
                core.fit_window_to_screen(win, 1380, 820, 900, 600)
            except Exception:
                win.geometry("1380x820")
            win.title("Простий місячний графік роботи")
            body = core.ttk.Frame(win, padding=10)
            body.pack(fill="both", expand=True)
            body.columnconfigure(1, weight=1)
            body.rowconfigure(3, weight=1)

            today = date.today()
            year_var = core.tk.StringVar(value=str(today.year))
            month_var = core.tk.StringVar(value=str(today.month))
            view_var = core.tk.StringVar(value=VIEW_INTERNAL)
            pattern_var = core.tk.StringVar(value=PATTERN_WEEKDAYS)
            anchor_var = core.tk.StringVar(value="1")
            start_var = core.tk.StringVar(value="08:00")
            end_var = core.tk.StringVar(value="17:00")
            break_var = core.tk.StringVar(value="60")
            replace_var = core.tk.BooleanVar(value=False)
            weekdays = [core.tk.BooleanVar(value=(i < 5)) for i in range(7)]

            header = core.ttk.Frame(body)
            header.grid(row=0, column=0, columnspan=2, sticky="ew")
            core.ttk.Label(header, text="Простий місячний графік роботи", style="Title.TLabel").pack(side="left")
            core.ttk.Label(header, text="Місяць").pack(side="left", padx=(18, 4))
            core.ttk.Spinbox(header, textvariable=month_var, from_=1, to=12, width=5).pack(side="left")
            core.ttk.Label(header, text="Рік").pack(side="left", padx=(8, 4))
            core.ttk.Spinbox(header, textvariable=year_var, from_=2020, to=2100, width=7).pack(side="left")

            left = core.ttk.LabelFrame(body, text="Працівники", padding=8)
            left.grid(row=1, column=0, rowspan=3, sticky="nsw", padx=(0, 8), pady=(8, 0))
            employee_list = core.tk.Listbox(left, selectmode="extended", width=39, height=25, exportselection=False)
            employee_list.pack(fill="both", expand=True)
            list_scroll = core.ttk.Scrollbar(left, orient="vertical", command=employee_list.yview)
            employee_list.configure(yscrollcommand=list_scroll.set)
            list_scroll.pack(side="right", fill="y")
            employee_map = {}

            def load_employees():
                employee_list.delete(0, "end")
                employee_map.clear()
                con = core.db()
                try:
                    rows = _employee_rows(con, active_only=True)
                finally:
                    con.close()
                for idx, row in enumerate(rows):
                    employee_map[idx] = row
                    roles = ", ".join(_roles(row))
                    employee_list.insert("end", "%s · %s" % (_employee_name(row), roles or "без ролі"))

            select_buttons = core.ttk.Frame(left)
            select_buttons.pack(fill="x", pady=(6, 0))
            core.ttk.Button(
                select_buttons,
                text="Усі",
                command=lambda: employee_list.selection_set(0, "end"),
            ).pack(side="left")
            core.ttk.Button(
                select_buttons,
                text="Очистити",
                command=lambda: employee_list.selection_clear(0, "end"),
            ).pack(side="left", padx=4)

            settings = core.ttk.LabelFrame(body, text="Заповнення вибраних працівників", padding=8)
            settings.grid(row=1, column=1, sticky="ew", pady=(8, 0))
            row1 = core.ttk.Frame(settings); row1.pack(fill="x")
            core.ttk.Label(row1, text="Шаблон").pack(side="left")
            core.ttk.Combobox(
                row1, textvariable=pattern_var, values=SIMPLE_PATTERNS, state="readonly", width=22
            ).pack(side="left", padx=(4, 10))
            core.ttk.Label(row1, text="Початок циклу, число").pack(side="left")
            core.ttk.Spinbox(row1, textvariable=anchor_var, from_=1, to=31, width=5).pack(side="left", padx=(4, 10))
            core.ttk.Label(row1, text="Початок").pack(side="left")
            core.ttk.Entry(row1, textvariable=start_var, width=7).pack(side="left", padx=(4, 8))
            core.ttk.Label(row1, text="Кінець").pack(side="left")
            core.ttk.Entry(row1, textvariable=end_var, width=7).pack(side="left", padx=(4, 8))
            core.ttk.Label(row1, text="Перерва, хв").pack(side="left")
            core.ttk.Entry(row1, textvariable=break_var, width=6).pack(side="left", padx=(4, 0))

            wd_frame = core.ttk.Frame(settings); wd_frame.pack(fill="x", pady=(6, 0))
            core.ttk.Label(wd_frame, text="Для «Вибрані дні»:").pack(side="left")
            for i, label in enumerate(WEEKDAY_NAMES):
                core.ttk.Checkbutton(wd_frame, text=label, variable=weekdays[i]).pack(side="left", padx=2)
            core.ttk.Checkbutton(
                wd_frame,
                text="Перепланувати існуючий план без факту",
                variable=replace_var,
            ).pack(side="right")

            viewbox = core.ttk.LabelFrame(body, text="Кому показуємо", padding=8)
            viewbox.grid(row=2, column=1, sticky="ew", pady=(8, 0))
            core.ttk.Radiobutton(
                viewbox,
                text="Внутрішній робочий перегляд",
                variable=view_var,
                value=VIEW_INTERNAL,
            ).pack(side="left")
            core.ttk.Radiobutton(
                viewbox,
                text="Графік для вибраних працівників",
                variable=view_var,
                value=VIEW_EMPLOYEE,
            ).pack(side="left", padx=12)
            core.ttk.Label(
                viewbox,
                text="У графік для працівників не потрапляють службові проблеми інших ролей.",
                style="Muted.TLabel",
            ).pack(side="left", padx=8)

            table_frame = core.ttk.Frame(body)
            table_frame.grid(row=3, column=1, sticky="nsew", pady=(8, 0))
            table_frame.rowconfigure(0, weight=1)
            table_frame.columnconfigure(0, weight=1)
            tree = core.ttk.Treeview(table_frame, show="headings")
            sy = core.ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            sx = core.ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
            tree.grid(row=0, column=0, sticky="nsew")
            sy.grid(row=0, column=1, sticky="ns")
            sx.grid(row=1, column=0, sticky="ew")
            last_data = {"value": None}

            def selected_ids(require=True):
                ids = [int(employee_map[idx]["id"]) for idx in employee_list.curselection() if idx in employee_map]
                if require and not ids:
                    core.messagebox.showinfo("Графік", "Виберіть працівників.", parent=win)
                return ids

            def parse_month():
                year = int(year_var.get())
                month = int(month_var.get())
                if not 1 <= month <= 12:
                    raise ValueError("Некоректний місяць.")
                return year, month

            def refresh():
                try:
                    year, month = parse_month()
                except Exception as exc:
                    core.messagebox.showerror("Графік", str(exc), parent=win)
                    return
                ids = selected_ids(require=(view_var.get() == VIEW_EMPLOYEE))
                con = core.db()
                try:
                    data = collect_month_schedule(
                        core,
                        con,
                        year,
                        month,
                        employee_ids=ids if ids else None,
                        view=view_var.get(),
                    )
                finally:
                    con.close()
                last_data["value"] = data

                days = data["days"]
                cols = ["employee", "roles"] + ["d%02d" % d.day for d in days]
                tree.configure(columns=cols)
                tree.heading("employee", text="Працівник"); tree.column("employee", width=220, anchor="w", stretch=False)
                tree.heading("roles", text="Роль"); tree.column("roles", width=150, anchor="w", stretch=False)
                for d in days:
                    key = "d%02d" % d.day
                    tree.heading(key, text="%02d\n%s" % (d.day, WEEKDAY_NAMES[d.weekday()]))
                    tree.column(key, width=48, anchor="center", stretch=False)
                for iid in tree.get_children(""):
                    tree.delete(iid)
                for row in data["employees"]:
                    tree.insert(
                        "",
                        "end",
                        values=[row["name"], row["roles"]] + row["cells"],
                    )

            def apply():
                ids = selected_ids()
                if not ids:
                    return
                try:
                    year, month = parse_month()
                    break_minutes = int(break_var.get() or 0)
                    anchor = int(anchor_var.get() or 1)
                    wd = [i for i, var in enumerate(weekdays) if var.get()]
                    if pattern_var.get() == PATTERN_SELECTED and not wd:
                        raise ValueError("Для вибраних днів тижня позначте хоча б один день.")
                    # Validate clock values before backup.
                    shift_span_minutes(
                        start_var.get(),
                        end_var.get(),
                        0 if parse_clock(end_var.get()) > parse_clock(start_var.get()) else 1,
                    )
                except Exception as exc:
                    core.messagebox.showerror("Графік", str(exc), parent=win)
                    return
                if not core.messagebox.askyesno(
                    "Записати простий графік?",
                    "Буде змінено план лише вибраних працівників. Факт, відсутності, графік водіїв "
                    "і конфліктні зміни не перезаписуються. Продовжити?",
                    parent=win,
                ):
                    return
                try:
                    backup = getattr(core, "backup_database", None)
                    if callable(backup):
                        backup("before_simple_month_schedule")
                except Exception as exc:
                    core.messagebox.showerror(
                        "Резервна копія",
                        "Не вдалося створити резервну копію перед масовим плануванням:\n%s" % exc,
                        parent=win,
                    )
                    return
                con = core.db()
                try:
                    result = apply_simple_month_plan(
                        core,
                        con,
                        ids,
                        year,
                        month,
                        pattern=pattern_var.get(),
                        anchor_day=anchor,
                        weekdays=wd,
                        start_time=start_var.get().strip(),
                        end_time=end_var.get().strip(),
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
                refresh()
                core.messagebox.showinfo(
                    "Графік",
                    (
                        "Додано змін: %(added)d\n"
                        "Переплановано: %(replaced)d\n"
                        "Водіїв залишено у спеціальному графіку: %(skipped_driver)d днів\n"
                        "Пропущено через відсутність/факт/наявний план/конфлікт: %(skipped)d"
                    )
                    % {
                        **result,
                        "skipped": (
                            result["skipped_absence"]
                            + result["skipped_fact"]
                            + result["skipped_existing"]
                            + result["skipped_conflict"]
                            + result["skipped_role"]
                        ),
                    },
                    parent=win,
                )

            def employee_export_data():
                ids = selected_ids()
                if not ids:
                    return None
                try:
                    year, month = parse_month()
                except Exception as exc:
                    core.messagebox.showerror("Графік", str(exc), parent=win)
                    return None
                con = core.db()
                try:
                    return collect_month_schedule(
                        core, con, year, month, employee_ids=ids, view=VIEW_EMPLOYEE
                    )
                finally:
                    con.close()

            def save_export(kind):
                data = employee_export_data()
                if data is None:
                    return
                suffix = ".xlsx" if kind == "xlsx" else ".pdf"
                name = "Графік_працівників_%04d_%02d%s" % (data["year"], data["month"], suffix)
                path = core.filedialog.asksaveasfilename(
                    parent=win,
                    title="Зберегти графік для працівників",
                    initialdir=str(core.OUTPUT_DIR),
                    initialfile=name,
                    defaultextension=suffix,
                    filetypes=[("Excel", "*.xlsx")] if kind == "xlsx" else [("PDF", "*.pdf")],
                )
                if not path:
                    return
                # Employee-facing exports are deliberately built from VIEW_EMPLOYEE
                # data above, so internal staffing diagnostics cannot leak into them.
                if kind == "xlsx":
                    actual = core.write_output_file(
                        lambda target: export_employee_schedule_xlsx(data, target),
                        path,
                        parent=win,
                        kind="Excel графіка",
                        error_title="Графік",
                    )
                else:
                    actual = core.write_output_file(
                        lambda target: export_employee_schedule_pdf(data, target),
                        path,
                        parent=win,
                        kind="PDF графіка",
                        error_title="Графік",
                    )
                if actual is not None and core.messagebox.askyesno(
                    "Графік",
                    "Файл створено:\n%s\n\nВідкрити?" % actual,
                    parent=win,
                ):
                    try:
                        core.open_external(actual)
                    except Exception as exc:
                        core.messagebox.showerror("Графік", str(exc), parent=win)

            footer = core.ttk.Frame(body)
            footer.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0))
            core.ttk.Button(footer, text="Переглянути", command=refresh).pack(side="left")
            core.ttk.Button(
                footer, text="Записати план", style="Accent.TButton", command=apply
            ).pack(side="left", padx=6)
            core.ttk.Button(
                footer, text="PDF для вибраних працівників", command=lambda: save_export("pdf")
            ).pack(side="left", padx=(18, 6))
            core.ttk.Button(
                footer, text="Excel для вибраних працівників", command=lambda: save_export("xlsx")
            ).pack(side="left", padx=6)
            core.ttk.Button(footer, text="Закрити", command=win.destroy).pack(side="right")

            load_employees()
            win.transient(self)

    Taxo1010R8App.__name__ = "App"
    Taxo1010R8App.__qualname__ = "App"
    core.App = Taxo1010R8App
    core._TAXO_1010_R8_SIMPLE_MONTH_SCHEDULE = True
    return Taxo1010R8App
