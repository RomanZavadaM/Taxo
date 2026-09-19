# -*- coding: utf-8 -*-
"""Taxo 10.0 — планування персоналу випуску та UI.

Модуль не змінює схему БД. Він працює поверх наявної таблиці employee_shifts,
додаючи безпечне масове планування лікарів/механіків на місяць, і усуває
звернення до вже знищеного вікна реєстру працівників при відкритті табеля.
"""
from __future__ import annotations

import calendar
import sqlite3
from datetime import date, datetime, timedelta


APP_VERSION = "10.0"
WINDOW_TITLE = f"Taxo {APP_VERSION} — Працівники, графіки та шляхівки"
ABOUT_TITLE = f"Taxo {APP_VERSION}"
ABOUT_TEXT = (
    "Облік роботи водіїв і персоналу, графіків, шляхових листів, табелів, "
    "бланків підтвердження діяльності та аналогових тахокарт.\n\n"
    "Taxo 10.0: стабільний реліз після експлуатаційної перевірки лінії 9.1. "
    "Шляхівки використовують єдиний склад лікаря/механіка для дати та номера зміни; "
    "нічний рейс не підхоплює наступну дату."
)

PATTERN_DAILY = "Щодня"
PATTERN_WEEKDAYS = "Пн–Пт"
PATTERN_SELECTED = "Вибрані дні тижня"
PATTERN_ALTERNATE = "Через день"
PATTERN_2_2 = "2/2"
PATTERN_7_7 = "7/7"
PATTERN_CUSTOM = "Власний цикл"
PATTERNS = (
    PATTERN_DAILY,
    PATTERN_WEEKDAYS,
    PATTERN_SELECTED,
    PATTERN_ALTERNATE,
    PATTERN_2_2,
    PATTERN_7_7,
    PATTERN_CUSTOM,
)
WEEKDAY_NAMES = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд")


def parse_clock(value: str) -> int:
    raw = str(value or "").strip()
    parts = raw.split(":")
    if len(parts) != 2:
        raise ValueError("Час має бути у форматі ГГ:ХХ")
    hour, minute = (int(parts[0]), int(parts[1]))
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError("Некоректний час")
    return hour * 60 + minute


def shift_span_minutes(start_time: str, end_time: str, end_day_offset: int = 0) -> int:
    start_min = parse_clock(start_time)
    end_min = parse_clock(end_time) + int(end_day_offset) * 1440
    if end_min <= start_min:
        raise ValueError("Кінець зміни має бути пізніше початку")
    return end_min - start_min


def month_bounds(year: int, month: int):
    first = date(int(year), int(month), 1)
    last = first.replace(day=calendar.monthrange(first.year, first.month)[1])
    return first, last


def pattern_dates(
    start_day: date,
    end_day: date,
    pattern: str,
    *,
    weekdays=None,
    work_days: int = 1,
    rest_days: int = 1,
):
    """Return dates selected by a monthly planning rule.

    Cycle patterns are anchored at start_day. This makes the result predictable
    when the operator starts a 2/2 or custom cycle from a specific date.
    """
    if end_day < start_day:
        raise ValueError("Кінцева дата раніше початкової")
    weekday_set = set(int(x) for x in (weekdays or []))
    work_days = int(work_days)
    rest_days = int(rest_days)
    if pattern == PATTERN_ALTERNATE:
        work_days, rest_days = 1, 1
    elif pattern == PATTERN_2_2:
        work_days, rest_days = 2, 2
    elif pattern == PATTERN_7_7:
        work_days, rest_days = 7, 7
    if pattern in (PATTERN_ALTERNATE, PATTERN_2_2, PATTERN_7_7, PATTERN_CUSTOM):
        if work_days < 1 or rest_days < 1:
            raise ValueError("Робочі та вихідні дні циклу мають бути більші за нуль")
        cycle = work_days + rest_days
    else:
        cycle = None

    result = []
    current = start_day
    while current <= end_day:
        include = False
        if pattern == PATTERN_DAILY:
            include = True
        elif pattern == PATTERN_WEEKDAYS:
            include = current.weekday() < 5
        elif pattern == PATTERN_SELECTED:
            include = current.weekday() in weekday_set
        elif cycle:
            include = ((current - start_day).days % cycle) < work_days
        else:
            raise ValueError(f"Невідомий шаблон: {pattern}")
        if include:
            result.append(current)
        current += timedelta(days=1)
    return result


def widget_alive(widget) -> bool:
    if widget is None:
        return False
    try:
        return bool(widget.winfo_exists())
    except Exception:
        return False


def _row_value(row, key, default=None):
    try:
        return row[key]
    except Exception:
        return getattr(row, key, default)


def monthly_plan_action(own_rows, slot_rows, *, replace=False):
    """Classify one target date before writing a monthly dispatch plan.

    Operational slot uniqueness is role + work_date + shift_no for one ATP.
    Location is descriptive and must not create a second doctor/mechanic for the
    same numbered shift. Existing legacy duplicates are treated as conflicts.
    """
    own_rows = list(own_rows or [])
    own_ids = {int(_row_value(row, "id", -1)) for row in own_rows}
    other_slot = [
        row for row in (slot_rows or [])
        if int(_row_value(row, "id", -1)) not in own_ids
    ]
    if any(_row_value(row, "actual_hours") is not None for row in own_rows):
        return "Факт — не змінювати"
    if own_rows and not replace:
        return "Вже є зміна працівника — пропустити"
    if other_slot:
        return "Зміна зайнята іншим працівником"
    if own_rows and replace:
        return "Замінити план"
    return "Додати"


def _replace_about_command(core, app):
    try:
        menu_name = app.cget("menu")
        if not menu_name:
            return False
        menubar = app.nametowidget(menu_name)
        end = menubar.index("end")
        if end is None:
            return False
        for index in range(end + 1):
            if menubar.type(index) != "cascade":
                continue
            if menubar.entrycget(index, "label") != "Довідка":
                continue
            submenu = app.nametowidget(menubar.entrycget(index, "menu"))
            sub_end = submenu.index("end")
            if sub_end is None:
                return False
            for sub_index in range(sub_end + 1):
                if submenu.type(sub_index) == "command" and submenu.entrycget(sub_index, "label") == "Про програму":
                    submenu.entryconfigure(
                        sub_index,
                        command=lambda: core.messagebox.showinfo(
                            ABOUT_TITLE,
                            ABOUT_TEXT,
                            parent=app,
                        ),
                    )
                    return True
    except core.tk.TclError:
        return False
    return False


def _full_name(row) -> str:
    return " ".join(
        str(row[key] or "").strip()
        for key in ("last_name", "first_name", "middle_name")
        if key in row.keys() and str(row[key] or "").strip()
    )


def _row_interval(row):
    base = datetime.strptime(row["work_date"], "%Y-%m-%d").date()
    start = datetime.combine(base, datetime.min.time()) + timedelta(minutes=parse_clock(row["start_time"]))
    end = datetime.combine(
        base + timedelta(days=int(row["end_day_offset"] or 0)),
        datetime.min.time(),
    ) + timedelta(minutes=parse_clock(row["end_time"]))
    return start, end


def install(core, base_app):
    """Install Taxo 10.0 behavior."""
    if getattr(core, "_TAXO_V91_INSTALLED", False):
        return core.App

    class Taxo91App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title(WINDOW_TITLE)

        def build_menu(self):
            result = super().build_menu()
            _replace_about_command(core, self)
            return result

        def _v91_drop_dead_window(self, attr_name):
            widget = getattr(self, attr_name, None)
            if widget is not None and not widget_alive(widget):
                try:
                    delattr(self, attr_name)
                except Exception:
                    setattr(self, attr_name, None)

        def show_employee_timesheet(self):
            # main.py historically retained self.employee_win after that window
            # was destroyed. Creating Toplevel(stale_widget) then raises:
            # TclError: bad window path name ".!toplevel...".
            self._v91_drop_dead_window("employee_win")
            return super().show_employee_timesheet()

        def show_dispatch_staff_schedule(self):
            self._v91_drop_dead_window("dispatch_win")
            result = super().show_dispatch_staff_schedule()
            self._v91_ensure_month_planner_button()
            return result

        def _v91_ensure_month_planner_button(self):
            win = getattr(self, "dispatch_win", None)
            if not widget_alive(win):
                return
            button = getattr(self, "_v91_month_planner_button", None)
            if widget_alive(button):
                return
            top = next(
                (child for child in win.winfo_children() if isinstance(child, core.ttk.Frame)),
                None,
            )
            if top is None:
                return
            button = core.ttk.Button(
                top,
                text="План на місяць",
                command=self.show_dispatch_month_planner,
            )
            button.pack(side="left", padx=(12, 3))
            self._v91_month_planner_button = button

        def _v91_staff_rows(self, role):
            con = core.db()
            rows = con.execute(
                """SELECT e.* FROM employees e
                   JOIN employee_roles er ON er.employee_id=e.id
                   WHERE e.active=1 AND er.role=?
                   ORDER BY e.last_name,e.first_name,e.middle_name""",
                (role,),
            ).fetchall()
            con.close()
            return rows

        def _v91_existing_overlap(
            self,
            con,
            *,
            role,
            location,
            work_date,
            start_time,
            end_time,
            end_day_offset,
            ignore_ids=(),
        ):
            start_dt = datetime.combine(work_date, datetime.min.time()) + timedelta(
                minutes=parse_clock(start_time)
            )
            end_dt = datetime.combine(
                work_date + timedelta(days=int(end_day_offset)),
                datetime.min.time(),
            ) + timedelta(minutes=parse_clock(end_time))
            rows = con.execute(
                """SELECT sh.*,e.last_name,e.first_name,e.middle_name
                   FROM employee_shifts sh
                   JOIN employees e ON e.id=sh.employee_id
                   WHERE sh.role=?
                     AND lower(COALESCE(sh.location,''))=lower(?)
                     AND sh.work_date BETWEEN ? AND ?
                   ORDER BY sh.work_date,sh.start_time""",
                (
                    role,
                    location,
                    (work_date - timedelta(days=7)).isoformat(),
                    (end_dt.date() + timedelta(days=1)).isoformat(),
                ),
            ).fetchall()
            ignored = {int(x) for x in ignore_ids}
            for row in rows:
                if int(row["id"]) in ignored:
                    continue
                other_start, other_end = _row_interval(row)
                if start_dt < other_end and other_start < end_dt:
                    return row
            return None

        def show_dispatch_month_planner(self):
            existing_win = getattr(self, "_v91_month_plan_win", None)
            if widget_alive(existing_win):
                existing_win.lift()
                return

            parent = getattr(self, "dispatch_win", self)
            if not widget_alive(parent):
                parent = self
            win = core.tk.Toplevel(parent)
            self._v91_month_plan_win = win
            win.title("План лікаря / механіка на місяць")
            core.fit_window_to_screen(win, 1280, 780, 920, 600)
            try:
                win.transient(parent)
            except core.tk.TclError:
                pass

            current = date.today()
            if hasattr(self, "dispatch_date_var"):
                try:
                    current = datetime.strptime(
                        self.dispatch_date_var.get().strip(), "%d.%m.%Y"
                    ).date()
                except Exception:
                    pass

            month_var = core.tk.StringVar(value=str(current.month))
            year_var = core.tk.StringVar(value=str(current.year))
            start_var = core.tk.StringVar()
            end_var = core.tk.StringVar()
            role_var = core.tk.StringVar(value="Лікар")
            employee_var = core.tk.StringVar()
            shift_var = core.tk.StringVar(value="I")
            start_time_var = core.tk.StringVar()
            end_time_var = core.tk.StringVar()
            end_day_var = core.tk.StringVar(value="0")
            location_var = core.tk.StringVar()
            pattern_var = core.tk.StringVar(value=PATTERN_WEEKDAYS)
            work_days_var = core.tk.StringVar(value="2")
            rest_days_var = core.tk.StringVar(value="2")
            notes_var = core.tk.StringVar(value="")
            replace_var = core.tk.BooleanVar(value=False)
            weekday_vars = [
                core.tk.BooleanVar(value=(i < 5)) for i in range(7)
            ]
            staff_map = {}

            month_bar = core.ttk.Frame(win, padding=8)
            month_bar.pack(fill="x")
            core.ttk.Label(month_bar, text="Місяць").pack(side="left")
            core.ttk.Spinbox(
                month_bar, textvariable=month_var, from_=1, to=12, width=5
            ).pack(side="left", padx=(4, 10))
            core.ttk.Label(month_bar, text="Рік").pack(side="left")
            core.ttk.Spinbox(
                month_bar, textvariable=year_var, from_=2020, to=2100, width=7
            ).pack(side="left", padx=(4, 10))

            notebook = core.ttk.Notebook(win)
            notebook.pack(fill="both", expand=True, padx=8, pady=(0, 8))
            overview_tab = core.ttk.Frame(notebook)
            plan_tab = core.ttk.Frame(notebook)
            notebook.add(overview_tab, text="Огляд місяця")
            notebook.add(plan_tab, text="Масове планування")

            overview_frame = core.ttk.Frame(overview_tab, padding=6)
            overview_frame.pack(fill="both", expand=True)
            overview_frame.rowconfigure(0, weight=1)
            overview_frame.columnconfigure(0, weight=1)
            overview_cols = ("date", "day", "doctor1", "doctor2", "mechanic1", "mechanic2")
            overview_tree = core.ttk.Treeview(
                overview_frame, columns=overview_cols, show="headings"
            )
            for key, label, width in (
                ("date", "Дата", 95),
                ("day", "День", 60),
                ("doctor1", "Лікар I", 245),
                ("doctor2", "Лікар II", 245),
                ("mechanic1", "Механік I", 245),
                ("mechanic2", "Механік II", 245),
            ):
                overview_tree.heading(key, text=label)
                overview_tree.column(key, width=width, anchor="w")
            oy = core.ttk.Scrollbar(
                overview_frame, orient="vertical", command=overview_tree.yview
            )
            ox = core.ttk.Scrollbar(
                overview_frame, orient="horizontal", command=overview_tree.xview
            )
            overview_tree.configure(yscrollcommand=oy.set, xscrollcommand=ox.set)
            overview_tree.grid(row=0, column=0, sticky="nsew")
            oy.grid(row=0, column=1, sticky="ns")
            ox.grid(row=1, column=0, sticky="ew")

            plan_outer = core.ttk.Frame(plan_tab, padding=8)
            plan_outer.pack(fill="both", expand=True)
            plan_outer.columnconfigure(1, weight=1)

            def add_entry(row, label, variable, *, width=28, calendar_btn=False):
                core.ttk.Label(plan_outer, text=label).grid(
                    row=row, column=0, sticky="w", padx=(0, 8), pady=4
                )
                entry = core.ttk.Entry(plan_outer, textvariable=variable, width=width)
                entry.grid(row=row, column=1, sticky="ew", pady=4)
                if calendar_btn:
                    core.calendar_button(plan_outer, variable).grid(
                        row=row, column=2, sticky="w", padx=(4, 0), pady=4
                    )
                return entry

            add_entry(0, "Період з", start_var, calendar_btn=True)
            add_entry(1, "Період до", end_var, calendar_btn=True)

            core.ttk.Label(plan_outer, text="Роль").grid(
                row=2, column=0, sticky="w", padx=(0, 8), pady=4
            )
            role_combo = core.ttk.Combobox(
                plan_outer,
                textvariable=role_var,
                values=("Лікар", "Механік"),
                state="readonly",
                width=26,
            )
            role_combo.grid(row=2, column=1, sticky="w", pady=4)

            core.ttk.Label(plan_outer, text="Працівник").grid(
                row=3, column=0, sticky="w", padx=(0, 8), pady=4
            )
            employee_combo = core.ttk.Combobox(
                plan_outer, textvariable=employee_var, state="readonly", width=46
            )
            employee_combo.grid(row=3, column=1, sticky="ew", pady=4)

            row4 = core.ttk.Frame(plan_outer)
            row4.grid(row=4, column=0, columnspan=3, sticky="ew", pady=4)
            core.ttk.Label(row4, text="Зміна").pack(side="left")
            core.ttk.Combobox(
                row4, textvariable=shift_var, values=("I", "II"), state="readonly", width=5
            ).pack(side="left", padx=(4, 14))
            core.ttk.Label(row4, text="Початок").pack(side="left")
            core.ttk.Entry(row4, textvariable=start_time_var, width=8).pack(
                side="left", padx=(4, 14)
            )
            core.ttk.Label(row4, text="Кінець D+").pack(side="left")
            core.ttk.Spinbox(
                row4, textvariable=end_day_var, from_=0, to=7, width=4
            ).pack(side="left", padx=(4, 2))
            core.ttk.Entry(row4, textvariable=end_time_var, width=8).pack(
                side="left", padx=(2, 14)
            )
            core.ttk.Label(row4, text="Місце").pack(side="left")
            core.ttk.Entry(row4, textvariable=location_var, width=24).pack(
                side="left", padx=(4, 0), fill="x", expand=True
            )

            core.ttk.Label(plan_outer, text="Схема").grid(
                row=5, column=0, sticky="w", padx=(0, 8), pady=4
            )
            pattern_combo = core.ttk.Combobox(
                plan_outer,
                textvariable=pattern_var,
                values=PATTERNS,
                state="readonly",
                width=30,
            )
            pattern_combo.grid(row=5, column=1, sticky="w", pady=4)

            weekday_frame = core.ttk.Frame(plan_outer)
            weekday_frame.grid(row=6, column=0, columnspan=3, sticky="w", pady=3)
            core.ttk.Label(weekday_frame, text="Дні тижня:").pack(side="left", padx=(0, 6))
            for idx, label in enumerate(WEEKDAY_NAMES):
                core.ttk.Checkbutton(
                    weekday_frame, text=label, variable=weekday_vars[idx]
                ).pack(side="left", padx=2)

            cycle_frame = core.ttk.Frame(plan_outer)
            cycle_frame.grid(row=7, column=0, columnspan=3, sticky="w", pady=3)
            core.ttk.Label(cycle_frame, text="Власний цикл: робота").pack(side="left")
            core.ttk.Spinbox(
                cycle_frame, textvariable=work_days_var, from_=1, to=31, width=4
            ).pack(side="left", padx=4)
            core.ttk.Label(cycle_frame, text="дн. / відпочинок").pack(side="left")
            core.ttk.Spinbox(
                cycle_frame, textvariable=rest_days_var, from_=1, to=31, width=4
            ).pack(side="left", padx=4)
            core.ttk.Label(cycle_frame, text="дн.").pack(side="left")

            add_entry(8, "Примітка до плану", notes_var)
            core.ttk.Checkbutton(
                plan_outer,
                text=(
                    "Замінювати існуючий ПЛАН цього працівника для цієї ролі/зміни "
                    "(місце може змінитися; записи з фактом не змінюються)"
                ),
                variable=replace_var,
            ).grid(row=9, column=0, columnspan=3, sticky="w", pady=(5, 7))

            preview_frame = core.ttk.Frame(plan_outer)
            preview_frame.grid(
                row=11, column=0, columnspan=3, sticky="nsew", pady=(7, 0)
            )
            plan_outer.rowconfigure(11, weight=1)
            preview_frame.rowconfigure(0, weight=1)
            preview_frame.columnconfigure(0, weight=1)
            preview_cols = ("date", "day", "action", "current")
            preview_tree = core.ttk.Treeview(
                preview_frame, columns=preview_cols, show="headings"
            )
            for key, label, width in (
                ("date", "Дата", 95),
                ("day", "День", 60),
                ("action", "Дія", 190),
                ("current", "Поточне призначення / конфлікт", 620),
            ):
                preview_tree.heading(key, text=label)
                preview_tree.column(key, width=width, anchor="w")
            py = core.ttk.Scrollbar(
                preview_frame, orient="vertical", command=preview_tree.yview
            )
            px = core.ttk.Scrollbar(
                preview_frame, orient="horizontal", command=preview_tree.xview
            )
            preview_tree.configure(yscrollcommand=py.set, xscrollcommand=px.set)
            preview_tree.grid(row=0, column=0, sticky="nsew")
            py.grid(row=0, column=1, sticky="ns")
            px.grid(row=1, column=0, sticky="ew")
            status_var = core.tk.StringVar()
            core.ttk.Label(
                plan_outer, textvariable=status_var, font=("TkDefaultFont", 9, "bold")
            ).grid(row=12, column=0, columnspan=3, sticky="w", pady=(4, 0))

            def selected_month():
                try:
                    yy = int(year_var.get())
                    mm = int(month_var.get())
                    return month_bounds(yy, mm)
                except Exception:
                    core.messagebox.showerror(
                        "План на місяць", "Перевірте місяць і рік.", parent=win
                    )
                    return None, None

            def set_month_range():
                first, last = selected_month()
                if not first:
                    return
                start_var.set(first.strftime("%d.%m.%Y"))
                end_var.set(last.strftime("%d.%m.%Y"))
                refresh_overview()

            def refresh_overview():
                first, last = selected_month()
                if not first:
                    return
                for item in overview_tree.get_children():
                    overview_tree.delete(item)
                con = core.db()
                rows = con.execute(
                    """SELECT sh.*,e.last_name,e.first_name,e.middle_name
                       FROM employee_shifts sh
                       JOIN employees e ON e.id=sh.employee_id
                       WHERE sh.work_date BETWEEN ? AND ?
                         AND sh.role IN ('Лікар','Механік')
                       ORDER BY sh.work_date,sh.role,sh.shift_no,e.last_name,e.first_name""",
                    (first.isoformat(), last.isoformat()),
                ).fetchall()
                con.close()
                by_date = {}
                for row in rows:
                    key = ("d" if row["role"] == "Лікар" else "m") + str(
                        int(row["shift_no"])
                    )
                    end_label = (
                        f"D+{int(row['end_day_offset'])} {row['end_time']}"
                        if int(row["end_day_offset"] or 0)
                        else row["end_time"]
                    )
                    value = (
                        f"{_full_name(row)} · {row['start_time']}–{end_label}"
                        + (f" · {row['location']}" if (row["location"] or "").strip() else "")
                    )
                    by_date.setdefault(row["work_date"], {})[key] = value
                current_day = first
                while current_day <= last:
                    values = by_date.get(current_day.isoformat(), {})
                    overview_tree.insert(
                        "",
                        "end",
                        iid=current_day.isoformat(),
                        values=(
                            current_day.strftime("%d.%m.%Y"),
                            WEEKDAY_NAMES[current_day.weekday()],
                            values.get("d1", ""),
                            values.get("d2", ""),
                            values.get("m1", ""),
                            values.get("m2", ""),
                        ),
                    )
                    current_day += timedelta(days=1)

            def load_staff(_event=None):
                nonlocal staff_map
                rows = self._v91_staff_rows(role_var.get())
                staff_map = {_full_name(row): row for row in rows}
                employee_combo["values"] = list(staff_map)
                if employee_var.get() not in staff_map:
                    employee_var.set(next(iter(staff_map), ""))
                preview_plan(silent=True)

            def use_last_shift():
                employee = staff_map.get(employee_var.get())
                if not employee:
                    return
                con = core.db()
                row = con.execute(
                    """SELECT * FROM employee_shifts
                       WHERE employee_id=? AND role=?
                       ORDER BY work_date DESC,id DESC LIMIT 1""",
                    (employee["id"], role_var.get()),
                ).fetchone()
                con.close()
                if not row:
                    core.messagebox.showinfo(
                        "Шаблон зміни",
                        "Для цього працівника ще немає попередньої зміни.",
                        parent=win,
                    )
                    return
                shift_var.set("I" if int(row["shift_no"]) == 1 else "II")
                start_time_var.set(row["start_time"])
                end_time_var.set(row["end_time"])
                end_day_var.set(str(int(row["end_day_offset"] or 0)))
                location_var.set(row["location"] or "")
                preview_plan(silent=True)

            def parse_plan_inputs(show_error=True):
                try:
                    first = datetime.strptime(
                        start_var.get().strip(), "%d.%m.%Y"
                    ).date()
                    last = datetime.strptime(end_var.get().strip(), "%d.%m.%Y").date()
                    end_day = int(end_day_var.get())
                    minutes = shift_span_minutes(
                        start_time_var.get().strip(),
                        end_time_var.get().strip(),
                        end_day,
                    )
                    work_days = int(work_days_var.get())
                    rest_days = int(rest_days_var.get())
                    weekdays = [
                        idx for idx, var in enumerate(weekday_vars) if var.get()
                    ]
                    targets = pattern_dates(
                        first,
                        last,
                        pattern_var.get(),
                        weekdays=weekdays,
                        work_days=work_days,
                        rest_days=rest_days,
                    )
                    if pattern_var.get() == PATTERN_SELECTED and not weekdays:
                        raise ValueError("Для вибраних днів тижня позначте хоча б один день.")
                    employee = staff_map.get(employee_var.get())
                    if employee is None:
                        raise ValueError(
                            f"Для ролі «{role_var.get()}» виберіть працівника."
                        )
                    if not 0 <= end_day <= 7:
                        raise ValueError("D+ має бути від 0 до 7.")
                    return {
                        "first": first,
                        "last": last,
                        "end_day": end_day,
                        "minutes": minutes,
                        "targets": targets,
                        "employee": employee,
                        "role": role_var.get(),
                        "shift_no": 1 if shift_var.get() == "I" else 2,
                        "start_time": start_time_var.get().strip(),
                        "end_time": end_time_var.get().strip(),
                        "location": location_var.get().strip(),
                    }
                except Exception as exc:
                    if show_error:
                        core.messagebox.showerror(
                            "План на місяць", str(exc), parent=win
                        )
                    return None

            def evaluate_plan(show_error=True):
                plan = parse_plan_inputs(show_error=show_error)
                if not plan:
                    return None, []
                con = core.db()
                rows = []
                for work_date in plan["targets"]:
                    if hasattr(core, "employee_employed_on") and not core.employee_employed_on(
                        plan["employee"], work_date
                    ):
                        rows.append(
                            (work_date, "Поза періодом роботи", "Працівник не працює на цю дату")
                        )
                        continue

                    absence = con.execute(
                        "SELECT day_type,notes FROM employee_time_entries WHERE employee_id=? AND work_date=?",
                        (plan["employee"]["id"], work_date.isoformat()),
                    ).fetchone()
                    if absence and str(absence["day_type"] or "") in getattr(core, "TAXO_NONWORK_OVERRIDE_TYPES", set()):
                        rows.append(
                            (
                                work_date,
                                "Відсутність — не планувати",
                                f"{absence['day_type']} · {absence['notes'] or ''}",
                            )
                        )
                        continue

                    own = con.execute(
                        """SELECT sh.*,e.last_name,e.first_name,e.middle_name
                           FROM employee_shifts sh
                           JOIN employees e ON e.id=sh.employee_id
                           WHERE sh.employee_id=? AND sh.work_date=?
                             AND sh.role=? AND sh.shift_no=?
                           ORDER BY sh.id""",
                        (
                            plan["employee"]["id"],
                            work_date.isoformat(),
                            plan["role"],
                            plan["shift_no"],
                        ),
                    ).fetchall()
                    slot = con.execute(
                        """SELECT sh.*,e.last_name,e.first_name,e.middle_name
                           FROM employee_shifts sh
                           JOIN employees e ON e.id=sh.employee_id
                           WHERE sh.work_date=? AND sh.role=? AND sh.shift_no=?
                           ORDER BY sh.id""",
                        (
                            work_date.isoformat(),
                            plan["role"],
                            plan["shift_no"],
                        ),
                    ).fetchall()

                    action = monthly_plan_action(
                        own, slot, replace=replace_var.get()
                    )
                    detail_rows = own if own else slot
                    current = "; ".join(
                        f"{_full_name(row)} {row['start_time']}–"
                        + (
                            f"D+{int(row['end_day_offset'])} {row['end_time']}"
                            if int(row["end_day_offset"] or 0)
                            else row["end_time"]
                        )
                        + (
                            f" · {row['location']}"
                            if (row["location"] or "").strip()
                            else ""
                        )
                        for row in detail_rows
                    )

                    if action not in ("Додати", "Замінити план"):
                        rows.append((work_date, action, current))
                        continue

                    ignore_ids = [row["id"] for row in own] if replace_var.get() else []
                    overlap = self._v91_existing_overlap(
                        con,
                        role=plan["role"],
                        location=plan["location"],
                        work_date=work_date,
                        start_time=plan["start_time"],
                        end_time=plan["end_time"],
                        end_day_offset=plan["end_day"],
                        ignore_ids=ignore_ids,
                    )
                    if overlap:
                        rows.append(
                            (
                                work_date,
                                "Конфлікт часу",
                                f"{_full_name(overlap)} · {overlap['start_time']}–"
                                f"D+{int(overlap['end_day_offset'] or 0)} {overlap['end_time']}"
                                + (
                                    f" · {overlap['location']}"
                                    if (overlap["location"] or "").strip()
                                    else ""
                                ),
                            )
                        )
                    else:
                        rows.append((work_date, action, current))
                con.close()
                return plan, rows

            def preview_plan(silent=False):
                for item in preview_tree.get_children():
                    preview_tree.delete(item)
                try:
                    plan, rows = evaluate_plan(show_error=not silent)
                except Exception:
                    if not silent:
                        raise
                    status_var.set("")
                    return
                if not plan:
                    status_var.set("")
                    return
                for work_date, action, current_text in rows:
                    preview_tree.insert(
                        "",
                        "end",
                        values=(
                            work_date.strftime("%d.%m.%Y"),
                            WEEKDAY_NAMES[work_date.weekday()],
                            action,
                            current_text,
                        ),
                    )
                add_count = sum(
                    action in ("Додати", "Замінити план")
                    for _day, action, _current in rows
                )
                status_var.set(
                    f"Дат за схемою: {len(rows)}; буде записано: {add_count}; "
                    f"пропущено/конфліктів: {len(rows) - add_count}"
                )

            def apply_plan():
                plan, rows = evaluate_plan()
                if not plan:
                    return
                writable = [
                    item for item in rows if item[1] in ("Додати", "Замінити план")
                ]
                if not writable:
                    core.messagebox.showinfo(
                        "План на місяць",
                        "Немає дат, які можна записати за поточними параметрами.",
                        parent=win,
                    )
                    return
                replacing = sum(item[1] == "Замінити план" for item in writable)
                if not core.messagebox.askyesno(
                    "Застосувати місячний план",
                    f"Записати {len(writable)} змін(и) для {employee_var.get()}?\n"
                    f"Заміна існуючого плану: {replacing}.\n\n"
                    "Записи, де вже є факт, не змінюються.",
                    parent=win,
                ):
                    return

                con = core.db()
                added = replaced = skipped = conflicts = 0
                note = notes_var.get().strip() or "Місячний план Taxo 9.1"
                try:
                    for work_date, _action, _current in rows:
                        if _action not in ("Додати", "Замінити план"):
                            skipped += 1
                            continue

                        # Re-read immediately before each write. Preview may be stale.
                        # Табельна відсутність має вищий пріоритет за робочий план.
                        absence = con.execute(
                            "SELECT day_type FROM employee_time_entries WHERE employee_id=? AND work_date=?",
                            (plan["employee"]["id"], work_date.isoformat()),
                        ).fetchone()
                        if absence and str(absence["day_type"] or "") in getattr(core, "TAXO_NONWORK_OVERRIDE_TYPES", set()):
                            skipped += 1
                            continue

                        # SQLite uniqueness ignores location.
                        own = con.execute(
                            """SELECT * FROM employee_shifts
                               WHERE employee_id=? AND work_date=?
                                 AND role=? AND shift_no=?
                               ORDER BY id""",
                            (
                                plan["employee"]["id"],
                                work_date.isoformat(),
                                plan["role"],
                                plan["shift_no"],
                            ),
                        ).fetchall()
                        slot = con.execute(
                            """SELECT * FROM employee_shifts
                               WHERE work_date=? AND role=? AND shift_no=?
                               ORDER BY id""",
                            (
                                work_date.isoformat(),
                                plan["role"],
                                plan["shift_no"],
                            ),
                        ).fetchall()

                        action = monthly_plan_action(
                            own, slot, replace=replace_var.get()
                        )
                        if action not in ("Додати", "Замінити план"):
                            skipped += 1
                            continue

                        own_ids = [row["id"] for row in own]
                        overlap = self._v91_existing_overlap(
                            con,
                            role=plan["role"],
                            location=plan["location"],
                            work_date=work_date,
                            start_time=plan["start_time"],
                            end_time=plan["end_time"],
                            end_day_offset=plan["end_day"],
                            ignore_ids=own_ids if replace_var.get() else [],
                        )
                        if overlap:
                            conflicts += 1
                            continue

                        savepoint = f"v91_day_{work_date.strftime('%Y%m%d')}"
                        con.execute(f"SAVEPOINT {savepoint}")
                        removed = 0
                        try:
                            if own and replace_var.get():
                                con.executemany(
                                    "DELETE FROM employee_shifts WHERE id=? AND actual_hours IS NULL",
                                    [(row["id"],) for row in own],
                                )
                                removed = len(own)
                            con.execute(
                                """INSERT INTO employee_shifts(
                                       employee_id,role,work_date,shift_no,start_time,
                                       end_day_offset,end_time,location,planned_hours,
                                       actual_hours,status,notes
                                   ) VALUES(?,?,?,?,?,?,?,?,?,NULL,'planned',?)""",
                                (
                                    plan["employee"]["id"],
                                    plan["role"],
                                    work_date.isoformat(),
                                    plan["shift_no"],
                                    plan["start_time"],
                                    plan["end_day"],
                                    plan["end_time"],
                                    plan["location"],
                                    plan["minutes"] / 60.0,
                                    note,
                                ),
                            )
                            con.execute(f"RELEASE SAVEPOINT {savepoint}")
                        except sqlite3.IntegrityError:
                            con.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                            con.execute(f"RELEASE SAVEPOINT {savepoint}")
                            conflicts += 1
                            continue

                        replaced += removed
                        added += 1
                    con.commit()
                except Exception:
                    con.rollback()
                    con.close()
                    raise
                con.close()
                refresh_overview()
                preview_plan(silent=True)
                if hasattr(self, "refresh_dispatch_shifts") and widget_alive(
                    getattr(self, "dispatch_win", None)
                ):
                    self.refresh_dispatch_shifts()
                if hasattr(self, "refresh_waybill_issue_list") and widget_alive(
                    getattr(self, "waybill_win", None)
                ):
                    self.refresh_waybill_issue_list()
                core.messagebox.showinfo(
                    "План на місяць",
                    f"Записано змін: {added}.\n"
                    f"Замінено старих планових записів: {replaced}.\n"
                    f"Пропущено: {skipped}. Конфліктів часу/унікальності: {conflicts}.",
                    parent=win,
                )

            core.ttk.Button(
                month_bar, text="Показати місяць", command=set_month_range
            ).pack(side="left", padx=4)
            core.ttk.Button(
                month_bar, text="Оновити огляд", command=refresh_overview
            ).pack(side="left", padx=4)
            core.ttk.Button(
                month_bar,
                text="Масове планування",
                command=lambda: notebook.select(plan_tab),
            ).pack(side="left", padx=(12, 4))

            action_bar = core.ttk.Frame(plan_outer)
            action_bar.grid(row=10, column=0, columnspan=3, sticky="ew", pady=(2, 4))
            core.ttk.Button(
                action_bar, text="Взяти останню зміну", command=use_last_shift
            ).pack(side="left", padx=(0, 4))
            core.ttk.Button(
                action_bar, text="Переглянути", command=preview_plan
            ).pack(side="left", padx=4)
            core.ttk.Button(
                action_bar, text="Застосувати план", command=apply_plan
            ).pack(side="left", padx=(12, 4))

            role_combo.bind("<<ComboboxSelected>>", load_staff, add="+")
            employee_combo.bind(
                "<<ComboboxSelected>>", lambda _event: preview_plan(silent=True), add="+"
            )
            pattern_combo.bind(
                "<<ComboboxSelected>>", lambda _event: preview_plan(silent=True), add="+"
            )

            set_month_range()
            load_staff()

    Taxo91App.__name__ = "App"
    Taxo91App.__qualname__ = "App"
    core.App = Taxo91App
    core._TAXO_V91_INSTALLED = True
    return Taxo91App
