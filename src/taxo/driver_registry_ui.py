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

from driver_form_ui import driver_form
from table_sorting import sort_treeview


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
    app.driver_registry_sort = None
    app.driver_registry_column_types = {
        "id": "number",
        "name": "text",
        "birth": "date",
        "license": "text",
        "employment": "date",
        "active": "status",
    }
    app.driver_registry_status_order = ("Так", "Ні")
    app.driver_registry_headings = headings

    def update_sort_headings():
        current = getattr(app, "driver_registry_sort", None)
        for key, label in headings.items():
            suffix = ""
            if current and current[0] == key:
                suffix = " ▼" if current[1] else " ▲"
            app.driver_tree.heading(key, text=label + suffix)

    def sort_by_header(column):
        current = getattr(app, "driver_registry_sort", None)
        descending = (
            not current[1] if current and current[0] == column else False
        )
        app.driver_registry_sort = (column, descending)
        sort_treeview(
            app.driver_tree,
            column,
            descending,
            value_type=app.driver_registry_column_types[column],
            status_order=(
                app.driver_registry_status_order
                if column == "active" else None
            ),
        )
        update_sort_headings()

    app._update_driver_registry_sort_headings = update_sort_headings
    for key in columns:
        app.driver_tree.heading(
            key,
            text=headings[key],
            command=lambda name=key: sort_by_header(name),
        )
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
    selected_ids = tuple(app.driver_tree.selection())
    selected_sort = getattr(app, "driver_registry_sort", None)
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
            iid=str(driver["id"]),
            values=(
                driver["id"],
                name,
                fmt_date(driver["birth_date"]),
                licence,
                fmt_date(driver["employment_date"]),
                "Так" if driver["active"] else "Ні",
            ),
        )

    if selected_sort:
        column, descending = selected_sort
        value_type = getattr(app, "driver_registry_column_types", {}).get(
            column, "text"
        )
        sort_treeview(
            app.driver_tree,
            column,
            descending,
            value_type=value_type,
            status_order=(
                getattr(app, "driver_registry_status_order", None)
                if column == "active" else None
            ),
        )
        update_headings = getattr(
            app, "_update_driver_registry_sort_headings", None
        )
        if callable(update_headings):
            update_headings()

    visible_ids = set(app.driver_tree.get_children(""))
    retained = [iid for iid in selected_ids if iid in visible_ids]
    if retained:
        app.driver_tree.selection_set(retained)
        app.driver_tree.focus(retained[0])
        app.driver_tree.see(retained[0])

    # Ці списки належать іншим робочим екранам, але мають оновитися
    # одразу після зміни картки водія.
    app.refresh_att_driver_choices()
    app.refresh_work_driver_choices()
