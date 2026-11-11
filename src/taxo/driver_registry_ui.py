# -*- coding: utf-8 -*-
"""UI реєстру й картки водія.

Модуль відповідає за каталог водіїв, картку водія та життєвий цикл ролі
«Водій». Табель робочого часу й атестація лише користуються цим реєстром
і залишаються у своїх модулях/методах App.

App у main.py зберігає сумісні методи-адаптери, тому історичні виклики
не залежать від фізичного розташування реалізації.
"""
from __future__ import annotations

from datetime import date, datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from branding import PALETTE


def build_drivers(app):
    """Побудувати вкладку реєстру водіїв."""
    toolbar = ttk.Frame(app.tab_drivers)
    toolbar.pack(fill="x", padx=10, pady=8)

    ttk.Button(
        toolbar,
        text="Реєстр усіх працівників",
        command=app.show_employee_registry,
    ).pack(side="left", padx=4)
    ttk.Button(
        toolbar,
        text="Табель персоналу",
        command=app.show_employee_timesheet,
    ).pack(side="left", padx=4)

    ttk.Separator(toolbar, orient="vertical").pack(
        side="left",
        fill="y",
        padx=6,
    )

    for label, command in (
        ("Новий водій", app.new_driver),
        ("Редагувати", app.edit_driver),
        ("Завершити роль водія", app.delete_driver),
        ("Оновити", app.load_drivers),
    ):
        ttk.Button(
            toolbar,
            text=label,
            command=command,
        ).pack(side="left", padx=4)

    columns = ("id", "name", "birth", "license", "employment", "active")
    headings = {
        "id": "ID",
        "name": "ПІБ",
        "birth": "Дата народження",
        "license": "Посвідчення",
        "employment": "Прийнятий з",
        "active": "Статус",
    }
    widths = {
        "id": 50,
        "name": 330,
        "birth": 120,
        "license": 200,
        "employment": 120,
        "active": 80,
    }

    app.driver_tree = ttk.Treeview(
        app.tab_drivers,
        columns=columns,
        show="headings",
        height=24,
    )
    for key in columns:
        app.driver_tree.heading(key, text=headings[key])
        app.driver_tree.column(key, width=widths[key], anchor="w")

    ybar = ttk.Scrollbar(
        app.tab_drivers,
        orient="vertical",
        command=app.driver_tree.yview,
    )
    xbar = ttk.Scrollbar(
        app.tab_drivers,
        orient="horizontal",
        command=app.driver_tree.xview,
    )
    app.driver_tree.configure(
        yscrollcommand=ybar.set,
        xscrollcommand=xbar.set,
    )

    xbar.pack(side="bottom", fill="x", padx=10, pady=(0, 5))
    ybar.pack(side="right", fill="y", pady=5)
    app.driver_tree.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(10, 0),
        pady=5,
    )

    app.driver_tree.bind("<<TreeviewSelect>>", app.on_driver_select)
    app.driver_tree.bind("<Double-1>", lambda _event: app.edit_driver())
    app.driver_tree.bind("<Return>", lambda _event: app.edit_driver())


def driver_form(
    app,
    driver=None,
    *,
    db_factory,
    fit_window_to_screen,
    calendar_button,
    finish_driver_role,
    void_legacy_driver_role,
    activate_driver_role,
):
    """Відкрити картку водія, зберігаючи історію його ролі."""
    win = tk.Toplevel(app)
    win.title("Картка водія")
    fit_window_to_screen(win, 760, 720, 700, 540)
    win.transient(app)

    # Картка довга, тому всі поля, прапорець і кнопка збереження
    # розміщені у вертикально прокручуваній області.
    shell = ttk.Frame(win)
    shell.pack(fill="both", expand=True)
    shell.rowconfigure(0, weight=1)
    shell.columnconfigure(0, weight=1)

    form_canvas = tk.Canvas(shell, highlightthickness=0, borderwidth=0)
    form_scroll = ttk.Scrollbar(
        shell,
        orient="vertical",
        command=form_canvas.yview,
    )
    form_canvas.configure(yscrollcommand=form_scroll.set)
    form_canvas.grid(row=0, column=0, sticky="nsew")
    form_scroll.grid(row=0, column=1, sticky="ns")

    outer = ttk.Frame(form_canvas, padding=10)
    form_window = form_canvas.create_window(
        (0, 0),
        window=outer,
        anchor="nw",
    )

    def sync_driver_form(_event=None):
        try:
            form_canvas.configure(scrollregion=form_canvas.bbox("all"))
        except tk.TclError:
            pass

    def fit_driver_form_width(event):
        try:
            form_canvas.itemconfigure(
                form_window,
                width=max(1, event.width),
            )
            sync_driver_form()
        except tk.TclError:
            pass

    def scroll_driver_form(event):
        if getattr(event, "num", None) == 4:
            step = -1
        elif getattr(event, "num", None) == 5:
            step = 1
        else:
            delta = getattr(event, "delta", 0)
            if not delta:
                return None
            step = int(-delta / 120) or (-1 if delta > 0 else 1)

        form_canvas.yview_scroll(step, "units")
        return "break"

    outer.bind("<Configure>", sync_driver_form, add="+")
    form_canvas.bind("<Configure>", fit_driver_form_width, add="+")
    win.bind("<MouseWheel>", scroll_driver_form, add="+")
    win.bind("<Button-4>", scroll_driver_form, add="+")
    win.bind("<Button-5>", scroll_driver_form, add="+")

    ua = ttk.LabelFrame(
        outer,
        text="Дані водія — українською",
        padding=8,
    )
    en = ttk.LabelFrame(
        outer,
        text="Дані для англійської сторони Бланка",
        padding=8,
    )
    extra = ttk.LabelFrame(
        outer,
        text="Інші дані",
        padding=8,
    )
    ua.pack(fill="x", pady=(0, 8))
    en.pack(fill="x", pady=(0, 8))
    extra.pack(fill="x", pady=(0, 8))

    values = {}

    ua_fields = (
        ("last_name", "Прізвище"),
        ("first_name", "Ім'я"),
        ("middle_name", "По батькові"),
    )
    for row_index, (key, label) in enumerate(ua_fields):
        ttk.Label(ua, text=label).grid(
            row=row_index,
            column=0,
            sticky="w",
            padx=6,
            pady=5,
        )
        variable = tk.StringVar(value=driver[key] if driver else "")
        values[key] = variable
        ttk.Entry(
            ua,
            textvariable=variable,
            width=62,
        ).grid(
            row=row_index,
            column=1,
            sticky="ew",
            padx=6,
            pady=5,
        )
    ua.columnconfigure(1, weight=1)

    en_fields = (
        ("last_name_en", "Surname / прізвище англійською"),
        ("first_name_en", "First name / ім'я англійською"),
        ("middle_name_en", "Middle name / по батькові англійською"),
    )
    for row_index, (key, label) in enumerate(en_fields):
        ttk.Label(en, text=label).grid(
            row=row_index,
            column=0,
            sticky="w",
            padx=6,
            pady=5,
        )
        raw_value = driver[key] if driver and key in driver.keys() else ""
        variable = tk.StringVar(value=raw_value or "")
        values[key] = variable
        ttk.Entry(
            en,
            textvariable=variable,
            width=62,
        ).grid(
            row=row_index,
            column=1,
            sticky="ew",
            padx=6,
            pady=5,
        )

    ttk.Label(
        en,
        text=(
            "Якщо англійське поле порожнє, у англійську сторону Бланка "
            "автоматично підставляється відповідне українське поле."
        ),
        foreground=PALETTE["muted"],
        wraplength=680,
        justify="left",
    ).grid(
        row=len(en_fields),
        column=0,
        columnspan=2,
        sticky="w",
        padx=6,
        pady=(5, 2),
    )
    en.columnconfigure(1, weight=1)

    other_fields = (
        ("personnel_no", "Табельний номер"),
        ("birth_date", "Дата народження (ДД.ММ.РРРР)"),
        ("license_series", "Серія посвідчення"),
        ("license_number", "Номер посвідчення"),
        ("license_issue_date", "Дата видачі посвідчення (ДД.ММ.РРРР)"),
        ("employment_date", "Дата прийняття (ДД.ММ.РРРР)"),
        ("notes", "Примітка"),
    )
    date_fields = {
        "birth_date",
        "license_issue_date",
        "employment_date",
    }

    for row_index, (key, label) in enumerate(other_fields):
        ttk.Label(extra, text=label).grid(
            row=row_index,
            column=0,
            sticky="w",
            padx=6,
            pady=5,
        )

        raw_value = driver[key] if driver else ""
        if key in date_fields and raw_value:
            try:
                raw_value = datetime.strptime(
                    str(raw_value),
                    "%Y-%m-%d",
                ).strftime("%d.%m.%Y")
            except ValueError:
                pass

        variable = tk.StringVar(value=raw_value)
        values[key] = variable
        ttk.Entry(
            extra,
            textvariable=variable,
            width=62,
        ).grid(
            row=row_index,
            column=1,
            sticky="ew",
            padx=6,
            pady=5,
        )

        if key in date_fields:
            calendar_button(
                extra,
                variable,
            ).grid(
                row=row_index,
                column=2,
                sticky="w",
                padx=(0, 6),
                pady=5,
            )
    extra.columnconfigure(1, weight=1)

    active = tk.BooleanVar(
        value=bool(driver["active"]) if driver else True
    )
    ttk.Checkbutton(
        outer,
        text="Активний водій",
        variable=active,
    ).pack(anchor="w", padx=8, pady=5)

    def parse_display_date(raw_value, *, error_title="Помилка"):
        if not raw_value:
            return ""
        try:
            return datetime.strptime(
                raw_value,
                "%d.%m.%Y",
            ).strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                error_title,
                "Дата має бути у форматі ДД.ММ.РРРР.",
                parent=win,
            )
            return None

    def save():
        field_order = (
            "last_name",
            "first_name",
            "middle_name",
            "last_name_en",
            "first_name_en",
            "middle_name_en",
            "personnel_no",
            "birth_date",
            "license_series",
            "license_number",
            "license_issue_date",
            "employment_date",
            "notes",
        )
        payload = {
            key: values[key].get().strip()
            for key in field_order
        }

        for key in date_fields:
            parsed = parse_display_date(payload[key])
            if parsed is None:
                return
            payload[key] = parsed

        if not payload["last_name"] or not payload["first_name"]:
            messagebox.showerror(
                "Помилка",
                "Прізвище та ім'я обов'язкові.",
                parent=win,
            )
            return

        role_end_date = ""
        role_start_date = ""
        role_action = ""

        if driver and bool(driver["active"]) and not active.get():
            choice = messagebox.askyesnocancel(
                "Зняти роль «Водій»",
                "ТАК — це реальне завершення роботи водієм і треба зберегти дату.\n"
                "НІ — це помилкова спадкова роль зі старих версій; "
                "не вважати працівника водієм історично.\n"
                "СКАСУВАТИ — повернутися без змін.",
                parent=win,
            )
            if choice is None:
                return

            if choice:
                role_action = "finish"
                raw_end = simpledialog.askstring(
                    "Дата завершення ролі",
                    "Дата завершення роботи водієм (ДД.ММ.РРРР):",
                    initialvalue=date.today().strftime("%d.%m.%Y"),
                    parent=win,
                )
                if raw_end is None:
                    return
                role_end_date = parse_display_date(
                    raw_end.strip(),
                    error_title="Роль водія",
                )
                if role_end_date is None:
                    return
            else:
                role_action = "void"

        elif driver and not bool(driver["active"]) and active.get():
            raw_start = simpledialog.askstring(
                "Початок ролі водія",
                "Дата початку / відновлення ролі водія (ДД.ММ.РРРР):",
                initialvalue=date.today().strftime("%d.%m.%Y"),
                parent=win,
            )
            if raw_start is None:
                return

            role_start_date = parse_display_date(
                raw_start.strip(),
                error_title="Роль водія",
            )
            if role_start_date is None:
                return
            role_action = "activate"

        elif not driver and active.get():
            role_action = "activate"
            role_start_date = (
                payload.get("employment_date")
                or date.today().isoformat()
            )

        con = db_factory()

        if driver:
            saved_driver_id = driver["id"]
            next_driver_end = (
                ""
                if active.get() or role_action == "void"
                else (
                    role_end_date
                    or (driver["driver_end_date"] or "").strip()
                )
            )
            con.execute(
                """UPDATE drivers SET
                    last_name=?,first_name=?,middle_name=?,
                    last_name_en=?,first_name_en=?,middle_name_en=?,
                    personnel_no=?,birth_date=?,license_series=?,license_number=?,
                    license_issue_date=?,employment_date=?,notes=?,active=?,
                    driver_end_date=? WHERE id=?""",
                (
                    payload["last_name"],
                    payload["first_name"],
                    payload["middle_name"],
                    payload["last_name_en"],
                    payload["first_name_en"],
                    payload["middle_name_en"],
                    payload["personnel_no"],
                    payload["birth_date"],
                    payload["license_series"],
                    payload["license_number"],
                    payload["license_issue_date"],
                    payload["employment_date"],
                    payload["notes"],
                    int(active.get()),
                    next_driver_end,
                    saved_driver_id,
                ),
            )
        else:
            cursor = con.execute(
                """INSERT INTO drivers(
                    last_name,first_name,middle_name,
                    last_name_en,first_name_en,middle_name_en,
                    personnel_no,birth_date,license_series,license_number,
                    license_issue_date,employment_date,notes,active,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    payload["last_name"],
                    payload["first_name"],
                    payload["middle_name"],
                    payload["last_name_en"],
                    payload["first_name_en"],
                    payload["middle_name_en"],
                    payload["personnel_no"],
                    payload["birth_date"],
                    payload["license_series"],
                    payload["license_number"],
                    payload["license_issue_date"],
                    payload["employment_date"],
                    payload["notes"],
                    0,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            saved_driver_id = cursor.lastrowid

        employee = con.execute(
            "SELECT id FROM employees WHERE driver_id=?",
            (saved_driver_id,),
        ).fetchone()

        if employee:
            employee_id = employee["id"]
            con.execute(
                """UPDATE employees SET
                    personnel_no=?,last_name=?,first_name=?,middle_name=?,
                    employment_date=?,notes=? WHERE id=?""",
                (
                    payload["personnel_no"],
                    payload["last_name"],
                    payload["first_name"],
                    payload["middle_name"],
                    payload["employment_date"],
                    payload["notes"],
                    employee_id,
                ),
            )
        else:
            cursor = con.execute(
                """INSERT INTO employees(
                    personnel_no,last_name,first_name,middle_name,position,
                    employment_date,notes,active,driver_id,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (
                    payload["personnel_no"],
                    payload["last_name"],
                    payload["first_name"],
                    payload["middle_name"],
                    "Водій",
                    payload["employment_date"],
                    payload["notes"],
                    1,
                    saved_driver_id,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            employee_id = cursor.lastrowid

        if role_action == "finish":
            finish_driver_role(
                con,
                employee_id,
                saved_driver_id,
                role_end_date,
            )
        elif role_action == "void":
            void_legacy_driver_role(
                con,
                employee_id,
                saved_driver_id,
            )
        elif role_action == "activate":
            activate_driver_role(
                con,
                employee_id,
                saved_driver_id,
                role_start_date,
            )
        elif active.get():
            con.execute(
                "INSERT OR IGNORE INTO employee_roles(employee_id,role) "
                "VALUES(?,?)",
                (employee_id, "Водій"),
            )
            con.execute(
                "UPDATE drivers SET active=1,driver_end_date='' WHERE id=?",
                (saved_driver_id,),
            )
        else:
            con.execute(
                "DELETE FROM employee_roles "
                "WHERE employee_id=? AND role='Водій'",
                (employee_id,),
            )

        con.commit()
        con.close()
        app.load_drivers()
        app.load_employee_registry()
        win.destroy()

    ttk.Button(
        outer,
        text="Зберегти",
        command=save,
    ).pack(anchor="e", padx=8, pady=8)


def new_driver(app):
    """Створити нову картку водія."""
    app.driver_form()


def edit_driver(app):
    """Відкрити картку вибраного водія."""
    driver = app.selected_driver()
    if driver:
        app.driver_form(driver)


def delete_driver(
    app,
    *,
    db_factory,
    finish_driver_role,
    void_legacy_driver_role,
):
    """Завершити або виправити роль «Водій» без видалення історії."""
    driver = app.selected_driver()
    if not driver:
        return

    choice = messagebox.askyesnocancel(
        "Зняти роль «Водій»",
        "ТАК — реальне завершення ролі з датою.\n"
        "НІ — виправити помилкову спадкову роль старих версій.\n"
        "СКАСУВАТИ — нічого не змінювати.",
        parent=app,
    )
    if choice is None:
        return

    end_date = ""
    if choice:
        raw_end = simpledialog.askstring(
            "Дата завершення ролі",
            "Дата завершення роботи водієм (ДД.ММ.РРРР):",
            initialvalue=date.today().strftime("%d.%m.%Y"),
            parent=app,
        )
        if raw_end is None:
            return
        try:
            end_date = datetime.strptime(
                raw_end.strip(),
                "%d.%m.%Y",
            ).strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Роль водія",
                "Дата має бути у форматі ДД.ММ.РРРР.",
                parent=app,
            )
            return

    con = db_factory()
    employee = con.execute(
        "SELECT id FROM employees WHERE driver_id=?",
        (driver["id"],),
    ).fetchone()

    if employee:
        if choice:
            finish_driver_role(
                con,
                employee["id"],
                driver["id"],
                end_date,
            )
        else:
            void_legacy_driver_role(
                con,
                employee["id"],
                driver["id"],
            )
    elif choice:
        con.execute(
            "UPDATE drivers SET active=0,driver_end_date=? WHERE id=?",
            (end_date, driver["id"]),
        )
    else:
        columns = {
            row[1]
            for row in con.execute("PRAGMA table_info(drivers)").fetchall()
        }
        if "driver_role_mode" in columns:
            con.execute(
                "UPDATE drivers SET active=0,driver_end_date='',"
                "driver_role_mode='invalid' WHERE id=?",
                (driver["id"],),
            )
        else:
            con.execute(
                "UPDATE drivers SET active=0,driver_end_date='' WHERE id=?",
                (driver["id"],),
            )

    con.commit()
    con.close()
    app.load_drivers()
    app.load_employee_registry()


def selected_driver(app, db_factory):
    """Повернути водія, вибраного у реєстрі."""
    selection = app.driver_tree.selection()
    if not selection:
        return None

    driver_id = int(
        app.driver_tree.item(selection[0], "values")[0]
    )
    con = db_factory()
    try:
        return con.execute(
            "SELECT * FROM drivers WHERE id=?",
            (driver_id,),
        ).fetchone()
    finally:
        con.close()


def driver_by_id(driver_id, db_factory):
    """Повернути водія за ID незалежно від виділення у реєстрі."""
    if not driver_id:
        return None

    con = db_factory()
    try:
        return con.execute(
            "SELECT * FROM drivers WHERE id=?",
            (int(driver_id),),
        ).fetchone()
    finally:
        con.close()


def driver_full_name(driver):
    """Повернути ПІБ водія без порожніх складових."""
    if not driver:
        return ""
    return " ".join(
        value
        for value in (
            driver["last_name"],
            driver["first_name"],
            driver["middle_name"],
        )
        if value
    ).strip()


def load_drivers(app, db_factory, fmt_date):
    """Оновити реєстр водіїв і залежні списки вибору."""
    for item in app.driver_tree.get_children():
        app.driver_tree.delete(item)

    con = db_factory()
    try:
        rows = con.execute(
            "SELECT * FROM drivers ORDER BY last_name, first_name"
        ).fetchall()
    finally:
        con.close()

    for driver in rows:
        name = driver_full_name(driver)
        licence = (
            f"{driver['license_series']} {driver['license_number']}"
        ).strip()
        issue_date = fmt_date(driver["license_issue_date"])
        if issue_date:
            licence = (
                f"{licence}, вид. {issue_date}"
                if licence
                else f"вид. {issue_date}"
            )

        app.driver_tree.insert(
            "",
            "end",
            values=(
                driver["id"],
                name,
                fmt_date(driver["birth_date"]),
                licence,
                fmt_date(driver["employment_date"]),
                "Так" if driver["active"] else "Ні",
            ),
        )

    # Ці списки належать іншим робочим екранам, але мають оновитися
    # одразу після зміни картки водія.
    app.refresh_att_driver_choices()
    app.refresh_work_driver_choices()
