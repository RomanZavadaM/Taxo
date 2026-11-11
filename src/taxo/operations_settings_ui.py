# -*- coding: utf-8 -*-
"""Налаштування експлуатації та нумерації наказів.

Модуль відповідає лише за вкладку налаштувань: відповідальних осіб,
місце складання наказів і два незалежні журнали нумерації.
"""
from __future__ import annotations

from dataclasses import dataclass

import operations_orders as ops


@dataclass
class OperationsSettingsState:
    """Значення налаштувань, потрібні іншим частинам центру експлуатації."""

    employee_labels: list
    employee_by_label: dict
    employee_by_id: dict
    operations_responsible_var: object
    military_responsible_var: object
    order_place_var: object
    work_order_next_var: object
    personnel_order_next_var: object
    work_order_next_entry: object


def _employee_maps(con):
    rows = ops.list_employee_choices(con, active_only=False)
    by_label = {row["label"]: row["id"] for row in rows}
    by_id = {row["id"]: row["label"] for row in rows}
    return rows, by_label, by_id


def install_operations_settings(core, tab, win):
    """Побудувати вкладку налаштувань і повернути її робочий стан."""
    container = core.ttk.Frame(tab, padding=14)
    container.pack(fill="both", expand=True)
    container.columnconfigure(1, weight=1)

    con = core.db()
    try:
        config = ops.settings(con)
        employees, employee_by_label, employee_by_id = _employee_maps(con)
    finally:
        con.close()

    employee_labels = [row["label"] for row in employees]
    operations_responsible_var = core.tk.StringVar(
        value=employee_by_id.get(
            config["operations_responsible_employee_id"],
            "",
        )
        if config
        else ""
    )
    military_responsible_var = core.tk.StringVar(
        value=employee_by_id.get(
            config["military_transport_responsible_employee_id"],
            "",
        )
        if config
        else ""
    )
    order_place_var = core.tk.StringVar(
        value=(config["order_place"] if config else "") or ""
    )

    config_keys = (
        set(config.keys())
        if config is not None and hasattr(config, "keys")
        else set()
    )
    work_order_next_var = core.tk.StringVar(
        value=str(
            (
                config["work_order_next_no"]
                if "work_order_next_no" in config_keys
                else 1
            )
            or 1
        )
    )
    personnel_order_next_var = core.tk.StringVar(
        value=str(
            (
                config["personnel_order_next_no"]
                if "personnel_order_next_no" in config_keys
                else 1
            )
            or 1
        )
    )

    responsible_rows = (
        ("Відповідальний за експлуатацію", operations_responsible_var),
        (
            "Відповідальний за військово-транспортний обов'язок",
            military_responsible_var,
        ),
    )
    for row_index, (label, variable) in enumerate(responsible_rows):
        core.ttk.Label(container, text=label).grid(
            row=row_index,
            column=0,
            sticky="w",
            padx=(0, 10),
            pady=7,
        )
        core.ttk.Combobox(
            container,
            textvariable=variable,
            values=employee_labels,
            state="readonly",
        ).grid(row=row_index, column=1, sticky="ew", pady=7)

    core.ttk.Label(container, text="Місце складання наказів").grid(
        row=2,
        column=0,
        sticky="w",
        padx=(0, 10),
        pady=7,
    )
    core.ttk.Entry(container, textvariable=order_place_var).grid(
        row=2,
        column=1,
        sticky="ew",
        pady=7,
    )

    core.ttk.Separator(container, orient="horizontal").grid(
        row=3,
        column=0,
        columnspan=2,
        sticky="ew",
        pady=(12, 8),
    )
    core.ttk.Label(
        container,
        text="Нумерація наказів",
        style="Title.TLabel",
    ).grid(
        row=4,
        column=0,
        columnspan=2,
        sticky="w",
        pady=(0, 4),
    )

    core.ttk.Label(
        container,
        text="Наступний № робочого / експлуатаційного наказу",
    ).grid(row=5, column=0, sticky="w", padx=(0, 10), pady=7)
    work_order_next_entry = core.ttk.Entry(
        container,
        textvariable=work_order_next_var,
        width=12,
    )
    work_order_next_entry.grid(row=5, column=1, sticky="w", pady=7)

    core.ttk.Label(
        container,
        text="Наступний № кадрового наказу",
    ).grid(row=6, column=0, sticky="w", padx=(0, 10), pady=7)
    core.ttk.Entry(
        container,
        textvariable=personnel_order_next_var,
        width=12,
    ).grid(row=6, column=1, sticky="w", pady=7)

    core.ttk.Label(
        container,
        text=(
            "Це початок / наступний номер для двох незалежних журналів. "
            "Робочі накази: 1, 2, 3…; кадрові: 1-К, 2-К, 3-К…. "
            "Якщо паперовий журнал уже ведеться, введіть тут номер, "
            "з якого Taxo має продовжити."
        ),
        style="Muted.TLabel",
        wraplength=900,
        justify="left",
    ).grid(
        row=7,
        column=0,
        columnspan=2,
        sticky="w",
        pady=(4, 8),
    )
    core.ttk.Label(
        container,
        text=(
            "Відомість ТЦК перед друком затверджується відповідальним у Taxo. "
            "Службові позначки про джерело імпорту у затверджену форму не друкуються."
        ),
        style="Muted.TLabel",
        wraplength=900,
        justify="left",
    ).grid(
        row=8,
        column=0,
        columnspan=2,
        sticky="w",
        pady=(8, 12),
    )

    def save_settings():
        con2 = core.db()
        try:
            ops.save_settings(
                con2,
                operations_responsible_employee_id=employee_by_label.get(
                    operations_responsible_var.get()
                ),
                military_transport_responsible_employee_id=employee_by_label.get(
                    military_responsible_var.get()
                ),
                order_place=order_place_var.get(),
                work_order_next_no=work_order_next_var.get(),
                personnel_order_next_no=personnel_order_next_var.get(),
            )
            con2.commit()
        except Exception as exc:
            con2.rollback()
            core.messagebox.showerror(
                "Експлуатація",
                str(exc),
                parent=win,
            )
            return
        finally:
            con2.close()

        core.messagebox.showinfo(
            "Експлуатація",
            "Налаштування експлуатації та нумерації наказів збережено.",
            parent=win,
        )

    core.ttk.Button(
        container,
        text="Зберегти",
        style="Accent.TButton",
        command=save_settings,
    ).grid(row=9, column=1, sticky="e")

    return OperationsSettingsState(
        employee_labels=employee_labels,
        employee_by_label=employee_by_label,
        employee_by_id=employee_by_id,
        operations_responsible_var=operations_responsible_var,
        military_responsible_var=military_responsible_var,
        order_place_var=order_place_var,
        work_order_next_var=work_order_next_var,
        personnel_order_next_var=personnel_order_next_var,
        work_order_next_entry=work_order_next_entry,
    )
