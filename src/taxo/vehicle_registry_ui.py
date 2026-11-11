# -*- coding: utf-8 -*-
"""Базовий UI каталогу транспортних засобів.

10.15-r9: реалізацію винесено з main.py, а методи App лишено як сумісні
adapter-и для історичних шарів, які розширюють їх через super().
"""

from __future__ import annotations

from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from branding import PALETTE
from vehicle_documents import (
    ensure_vehicle_documents_schema,
    vehicle_document_summary_text,
)
from vehicle_documents_ui import (
    open_vehicle_document_control,
    open_vehicle_documents,
)


def build_vehicles(app):
    top = ttk.Frame(app.tab_vehicles)
    top.pack(fill="x", padx=10, pady=8)
    ttk.Button(top, text="Нове авто", command=app.vehicle_form).pack(side="left", padx=4)
    ttk.Button(top, text="Редагувати", command=app.edit_vehicle).pack(side="left", padx=4)
    ttk.Button(top, text="Документи", command=app.vehicle_documents).pack(side="left", padx=4)
    ttk.Button(top, text="Контроль документів", command=app.vehicle_document_control).pack(side="left", padx=4)
    ttk.Button(top, text="Вивести з експлуатації", command=app.delete_vehicle).pack(side="left", padx=4)
    ttk.Button(top, text="Оновити", command=app.load_vehicles).pack(side="left", padx=4)
    ttk.Label(
        app.tab_vehicles,
        text="Каталог транспортних засобів. Документи зберігаються з копіями та контролем строків дії.",
        foreground=PALETTE["muted"],
    ).pack(anchor="w", padx=12)
    cols = ("id", "name", "plate", "garage", "make", "year", "ownership", "active", "documents", "notes")
    app.vehicle_tree = ttk.Treeview(app.tab_vehicles, columns=cols, show="headings", height=25)
    heads = {
        "id": "ID", "name": "Назва", "plate": "Держ. №", "garage": "Гар. №",
        "make": "Марка / модель", "year": "Рік", "ownership": "Власність / користування",
        "active": "Статус", "documents": "Документи", "notes": "Примітка",
    }
    widths = {
        "id": 45, "name": 145, "plate": 105, "garage": 80, "make": 150,
        "year": 60, "ownership": 155, "active": 75, "documents": 260, "notes": 200,
    }
    for col in cols:
        app.vehicle_tree.heading(col, text=heads[col])
        app.vehicle_tree.column(col, width=widths[col], anchor="w")
    vehicle_y = ttk.Scrollbar(app.tab_vehicles, orient="vertical", command=app.vehicle_tree.yview)
    vehicle_x = ttk.Scrollbar(app.tab_vehicles, orient="horizontal", command=app.vehicle_tree.xview)
    app.vehicle_tree.configure(yscrollcommand=vehicle_y.set, xscrollcommand=vehicle_x.set)
    vehicle_x.pack(side="bottom", fill="x", padx=10, pady=(0, 5))
    vehicle_y.pack(side="right", fill="y", pady=5)
    app.vehicle_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)
    app.vehicle_tree.bind("<Double-1>", lambda _event: app.edit_vehicle())
    app.vehicle_tree.bind("<Return>", lambda _event: app.edit_vehicle())
    app.load_vehicles()


def load_vehicles(app, db_factory):
    if not hasattr(app, "vehicle_tree"):
        return
    for item in app.vehicle_tree.get_children():
        app.vehicle_tree.delete(item)
    con = db_factory()
    try:
        ensure_vehicle_documents_schema(con)
        rows = con.execute("SELECT * FROM vehicles ORDER BY active DESC, name, plate").fetchall()
        data = [(row, vehicle_document_summary_text(con, row["id"])) for row in rows]
    finally:
        con.close()
    for row, doc_state in data:
        app.vehicle_tree.insert(
            "",
            "end",
            values=(
                row["id"], row["name"], row["plate"], row["garage_no"], row["make_model"],
                row["year"] or "", row["ownership_type"] or "", "Так" if row["active"] else "Ні",
                doc_state, row["notes"],
            ),
        )


def selected_vehicle(app, db_factory):
    selected = app.vehicle_tree.selection()
    if not selected:
        return None
    vehicle_id = int(app.vehicle_tree.item(selected[0], "values")[0])
    con = db_factory()
    try:
        return con.execute("SELECT * FROM vehicles WHERE id=?", (vehicle_id,)).fetchone()
    finally:
        con.close()


def vehicle_label(row):
    if not row:
        return ""
    parts = [row["name"], row["plate"]]
    if row["make_model"]:
        parts.append(row["make_model"])
    return " — ".join(value for value in parts if value)


def vehicle_form(app, db_factory, fit_window_to_screen, vehicle=None):
    win = tk.Toplevel(app)
    win.title("Автомобіль")
    fit_window_to_screen(win, 680, 560, 560, 460)
    win.transient(app)
    win.grab_set()
    fields = [
        ("name", "Назва / інвентарний номер"),
        ("plate", "Державний номер"),
        ("garage_no", "Гаражний номер"),
        ("make_model", "Марка / модель"),
        ("year", "Рік"),
    ]
    values = {}
    for index, (key, label) in enumerate(fields):
        ttk.Label(win, text=label).grid(row=index, column=0, sticky="w", padx=10, pady=8)
        var = tk.StringVar(value=str(vehicle[key] or "") if vehicle else "")
        values[key] = var
        ttk.Entry(win, textvariable=var, width=55).grid(row=index, column=1, sticky="ew", padx=10, pady=8)

    ownership_row = len(fields)
    ttk.Label(win, text="Форма власності / користування").grid(
        row=ownership_row, column=0, sticky="w", padx=10, pady=8
    )
    ownership = tk.StringVar(value=str(vehicle["ownership_type"] or "") if vehicle else "Власний")
    ttk.Combobox(
        win,
        textvariable=ownership,
        values=("Власний", "Оренда", "Лізинг", "Позичка / інше користування", "Інше"),
        width=52,
    ).grid(row=ownership_row, column=1, sticky="ew", padx=10, pady=8)

    temporary_required = tk.BooleanVar(
        value=bool(vehicle["temporary_registration_required"]) if vehicle else False
    )
    ttk.Checkbutton(
        win,
        text="Потрібен тимчасовий реєстраційний документ",
        variable=temporary_required,
    ).grid(row=ownership_row + 1, column=1, sticky="w", padx=10, pady=(2, 8))

    notes_row = ownership_row + 2
    ttk.Label(win, text="Примітка").grid(row=notes_row, column=0, sticky="w", padx=10, pady=8)
    notes = tk.StringVar(value=str(vehicle["notes"] or "") if vehicle else "")
    ttk.Entry(win, textvariable=notes, width=55).grid(row=notes_row, column=1, sticky="ew", padx=10, pady=8)

    active = tk.BooleanVar(value=bool(vehicle["active"]) if vehicle else True)
    ttk.Checkbutton(win, text="Активний автомобіль", variable=active).grid(
        row=notes_row + 1, column=1, sticky="w", padx=10, pady=8
    )

    def save():
        name = values["name"].get().strip()
        if not name:
            messagebox.showerror("Помилка", "Вкажіть назву автомобіля.", parent=win)
            return
        year = values["year"].get().strip()
        if year:
            try:
                year = int(year)
            except ValueError:
                messagebox.showerror("Помилка", "Рік має бути числом.", parent=win)
                return
        else:
            year = None
        con = db_factory()
        db_values = (
            name,
            values["plate"].get().strip(),
            values["garage_no"].get().strip(),
            values["make_model"].get().strip(),
            year,
            ownership.get().strip(),
            int(temporary_required.get()),
            notes.get().strip(),
            int(active.get()),
        )
        if vehicle:
            con.execute(
                "UPDATE vehicles SET name=?,plate=?,garage_no=?,make_model=?,year=?,ownership_type=?,temporary_registration_required=?,notes=?,active=? WHERE id=?",
                (*db_values, vehicle["id"]),
            )
        else:
            con.execute(
                "INSERT INTO vehicles(name,plate,garage_no,make_model,year,ownership_type,temporary_registration_required,notes,active,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (*db_values, datetime.now().isoformat(timespec="seconds")),
            )
        con.commit()
        con.close()
        app.load_vehicles()
        win.destroy()

    ttk.Button(win, text="Зберегти", command=save).grid(
        row=notes_row + 2, column=1, sticky="e", padx=10, pady=14
    )


def edit_vehicle(app):
    vehicle = app.selected_vehicle()
    if vehicle:
        app.vehicle_form(vehicle)


def vehicle_documents(app, db_factory, data_root):
    vehicle = app.selected_vehicle()
    if not vehicle:
        messagebox.showinfo("Документи авто", "Виберіть транспортний засіб.", parent=app)
        return
    open_vehicle_documents(app, db_factory, data_root, vehicle, on_change=app.load_vehicles)


def open_vehicle_documents_by_id(app, db_factory, data_root, vehicle_id):
    con = db_factory()
    try:
        vehicle = con.execute("SELECT * FROM vehicles WHERE id=?", (int(vehicle_id),)).fetchone()
    finally:
        con.close()
    if vehicle:
        open_vehicle_documents(app, db_factory, data_root, vehicle, on_change=app.load_vehicles)


def vehicle_document_control(app, db_factory, data_root):
    open_vehicle_document_control(
        app,
        db_factory,
        data_root,
        on_open_vehicle=app.open_vehicle_documents_by_id,
    )


def delete_vehicle(app, db_factory):
    vehicle = app.selected_vehicle()
    if not vehicle:
        return
    if not messagebox.askyesno(
        "Підтвердження",
        "Вивести транспортний засіб з експлуатації? Історичні записи та документи залишаться.",
        parent=app,
    ):
        return
    con = db_factory()
    con.execute("UPDATE vehicles SET active=0 WHERE id=?", (vehicle["id"],))
    con.commit()
    con.close()
    app.load_vehicles()
