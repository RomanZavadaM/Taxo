# -*- coding: utf-8 -*-
"""Базовий UI каталогу транспортних засобів.

10.15-r9: реалізацію винесено з main.py, а методи App лишено як сумісні
adapter-и для історичних шарів, які розширюють їх через super().
"""

from __future__ import annotations

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
from vehicle_form_ui import vehicle_form
from table_sorting import sort_treeview


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
    app.vehicle_sort = getattr(app, "vehicle_sort", None)

    def sort_by_header(column):
        previous = app.vehicle_sort
        descending = not previous[1] if previous and previous[0] == column else False
        app.vehicle_sort = (column, descending)
        sort_treeview(app.vehicle_tree, column, descending)
        update_sort_headings(app.vehicle_tree, heads, app.vehicle_sort)

    for col in cols:
        app.vehicle_tree.heading(
            col, text=heads[col], command=lambda name=col: sort_by_header(name)
        )
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


def update_sort_headings(tree, headings, current_sort):
    """Show the active sort direction without changing the column identifiers."""
    for column, label in headings.items():
        suffix = ""
        if current_sort and current_sort[0] == column:
            suffix = " ▼" if current_sort[1] else " ▲"
        tree.heading(column, text=label + suffix)


def _selected_vehicle_ids(tree):
    """Remember the selected vehicle across an ordinary Refresh operation."""
    result = set()
    for iid in tree.selection():
        try:
            result.add(int(tree.set(iid, "id")))
        except (ValueError, TypeError):
            continue
    return result


def load_vehicles(app, db_factory):
    if not hasattr(app, "vehicle_tree"):
        return
    selected_ids = _selected_vehicle_ids(app.vehicle_tree)
    for item in app.vehicle_tree.get_children():
        app.vehicle_tree.delete(item)
    con = db_factory()
    try:
        ensure_vehicle_documents_schema(con)
        rows = con.execute("SELECT * FROM vehicles ORDER BY active DESC, name, plate").fetchall()
        data = [(row, vehicle_document_summary_text(con, row["id"])) for row in rows]
    finally:
        con.close()
    restored = []
    for row, doc_state in data:
        iid = app.vehicle_tree.insert(
            "",
            "end",
            values=(
                row["id"], row["name"], row["plate"], row["garage_no"], row["make_model"],
                row["year"] or "", row["ownership_type"] or "", "Так" if row["active"] else "Ні",
                doc_state, row["notes"],
            ),
        )
        if row["id"] in selected_ids:
            restored.append(iid)

    if restored:
        app.vehicle_tree.selection_set(restored)
    selected_sort = getattr(app, "vehicle_sort", None)
    if selected_sort:
        sort_treeview(app.vehicle_tree, *selected_sort)
        update_sort_headings(app.vehicle_tree, {
            "id": "ID", "name": "Назва", "plate": "Держ. №",
            "garage": "Гар. №", "make": "Марка / модель",
            "year": "Рік", "ownership": "Власність / користування",
            "active": "Статус", "documents": "Документи", "notes": "Примітка",
        }, selected_sort)


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
