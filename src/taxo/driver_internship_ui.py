# -*- coding: utf-8 -*-
"""Driver internship / control-drive paper sheet editor."""
from __future__ import annotations

from datetime import date

import entity_choices as ops
import paper_documents as paperwork
import paper_document_store as document_store
from paper_documents_ui import open_paper_document_catalog
from workspace import load_workspace_root


def install_internship_tab(app, core, book):
    for tab_id in book.tabs():
        if str(book.tab(tab_id, "text")) == "Стажування водіїв":
            return book.nametowidget(tab_id)
    tab = core.ttk.Frame(book, padding=12)
    book.add(tab, text="Стажування водіїв")
    tab.columnconfigure(1, weight=1)
    core.ttk.Label(tab, text="Лист стажування водія", style="HeroTitle.TLabel").grid(
        row=0, column=0, columnspan=2, sticky="w")
    core.ttk.Label(tab, text=(
        "Форма за структурою додатка 3 до наказу №975: інструктаж на території, "
        "робота на маршруті, контрольна поїздка, зауваження та рішення про допуск. "
        "Це підготовка паперового листа — години, підписи й рішення фіксуються за фактом."
    ), style="Muted.TLabel", wraplength=900, justify="left").grid(
        row=1, column=0, columnspan=2, sticky="ew", pady=(3, 10))
    try:
        con = core.db()
        try:
            drivers = list(ops.list_driver_choices(con, active_only=True))
            vehicles = list(ops.list_vehicle_choices(con, active_only=True))
        finally:
            con.close()
    except Exception:
        drivers, vehicles = [], []
    driver_var = core.tk.StringVar()
    instructor_var = core.tk.StringVar()
    vehicle_var = core.tk.StringVar()
    kind_var = core.tk.StringVar(value="Стажування")
    order_var = core.tk.StringVar()
    period_var = core.tk.StringVar(value=date.today().strftime("%d.%m.%Y") + " — ")
    hours_var = core.tk.StringVar()
    licence_var = core.tk.StringVar()
    experience_var = core.tk.StringVar()
    choices_by_label = {str(x["label"]): x for x in drivers}
    vehicles_by_label = {str(x["label"]): x for x in vehicles}
    def field(row, title, var, values=None):
        core.ttk.Label(tab, text=title).grid(row=row, column=0, sticky="w", pady=3, padx=(0, 8))
        if values is None:
            control = core.ttk.Entry(tab, textvariable=var)
        else:
            control = core.ttk.Combobox(tab, textvariable=var,
                values=tuple(values), state="readonly")
        control.grid(row=row, column=1, sticky="ew", pady=3)
        return control
    field(2, "Водій-стажист", driver_var, choices_by_label)
    field(3, "Водій-інструктор", instructor_var, choices_by_label)
    field(4, "Транспортний засіб", vehicle_var, vehicles_by_label)
    field(5, "Вид роботи", kind_var, ("Стажування", "Контрольна поїздка"))
    field(6, "Наказ № та дата", order_var)
    field(7, "Період від — до", period_var)
    field(8, "Запланована кількість годин", hours_var)
    field(9, "Посвідчення водія (серія, №, категорії)", licence_var)
    field(10, "Стаж керування з року", experience_var)

    def generate():
        if not driver_var.get() or not instructor_var.get() or not vehicle_var.get():
            core.messagebox.showerror(
                "Лист стажування", "Виберіть стажиста, водія-інструктора і ТЗ.",
                parent=tab)
            return
        if driver_var.get() == instructor_var.get():
            core.messagebox.showerror(
                "Лист стажування", "Стажист і водій-інструктор мають бути різними особами.",
                parent=tab)
            return
        driver = choices_by_label[driver_var.get()]
        vehicle = vehicles_by_label[vehicle_var.get()]
        data = {
            "driver": str(driver.get("name") or driver_var.get()),
            "personnel_no": driver.get("personnel_no", ""),
            "instructor": instructor_var.get(),
            "vehicle": vehicle_var.get(),
            "training_kind": kind_var.get(),
            "order": order_var.get(),
            "period": period_var.get(),
            "hours": hours_var.get(),
            "licence": licence_var.get(),
            "experience_since": experience_var.get(),
            "driver_id": driver.get("id"),
            "vehicle_id": vehicle.get("id"),
        }
        try:
            target = document_store.save_document(
                load_workspace_root(), paperwork.build_training_docx(data),
                "Стажування", kind_var.get() + ": " + data["driver"],
                date.today().isoformat(), data["driver"])
        except Exception as exc:
            core.messagebox.showerror("Лист стажування", str(exc), parent=tab)
            return
        try:
            document_store.open_file(target)
        except OSError as exc:
            core.messagebox.showwarning(
                "Лист стажування збережено",
                "Файл створено, але його не вдалося відкрити автоматично.\n\n%s\n\n%s" % (target, exc),
                parent=tab,
            )
    buttons = core.ttk.Frame(tab)
    buttons.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(14, 8))
    core.ttk.Button(buttons, text="Створити лист стажування DOCX",
        style="Accent.TButton", command=generate).pack(side="left")
    core.ttk.Button(buttons, text="Каталог документів…",
        command=lambda: open_paper_document_catalog(tab, core, load_workspace_root())
    ).pack(side="left", padx=8)
    tab._taxo_internship_generate = generate
    return tab
