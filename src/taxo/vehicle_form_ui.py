# -*- coding: utf-8 -*-
"""Vehicle card editor separated from the vehicle registry table.

The editor owns the vehicle details and validation. The application injects
the database factory and window-sizing helper so the existing App adapter and
registry callbacks remain unchanged.
"""
from __future__ import annotations

from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk


def vehicle_form(app, db_factory, fit_window_to_screen, vehicle=None):
    """Open the vehicle card without changing the existing storage contract."""
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
