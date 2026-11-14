# -*- coding: utf-8 -*-
"""Reusable Tk controls for typed CompanyTemplates facts.

Controls are created and read only on the Tk UI thread. They hold plain
registry snapshots already loaded by the caller; they never open databases or
write business data.
"""
from __future__ import annotations

from dataclasses import dataclass
from tkinter import END, StringVar, Text, ttk

from company_template_fact_choices import FactChoiceCatalog, by_label
from company_template_fact_codec import (
    add_unique_pair,
    choice_snapshot,
    parse_date,
    parse_integer,
    parse_sections,
    parse_table_rows,
    parse_text,
    selected_snapshots,
)


@dataclass
class FactControl:
    """One rendered form control plus its UI-thread value reader."""

    frame: object
    get_value: object
    focus_widget: object = None


def _label_text(variable):
    text = variable.label
    if variable.required:
        text += " *"
    return text


def _help(parent, variable):
    text = str(variable.description or "").strip()
    if not text:
        return
    ttk.Label(
        parent,
        text=text,
        justify="left",
        wraplength=760,
    ).pack(fill="x", pady=(3, 0))


def scalar_control(parent, variable):
    frame = ttk.Frame(parent)
    ttk.Label(frame, text=_label_text(variable)).pack(anchor="w")
    value = StringVar(value="")
    entry = ttk.Entry(frame, textvariable=value)
    entry.pack(fill="x", pady=(2, 0))
    _help(frame, variable)

    if variable.variable_type == "text":
        getter = lambda: parse_text(value.get())
    elif variable.variable_type == "date":
        getter = lambda: (
            parse_date(value.get()) if value.get().strip() else None
        )
    elif variable.variable_type == "integer":
        getter = lambda: (
            parse_integer(value.get()) if value.get().strip() else None
        )
    else:
        raise ValueError("Непідтримуваний scalar control")
    return FactControl(frame=frame, get_value=getter, focus_widget=entry)


def choice_control(parent, variable, rows):
    frame = ttk.Frame(parent)
    ttk.Label(frame, text=_label_text(variable)).pack(anchor="w")
    mapping = by_label(rows)
    value = StringVar(value="")
    box = ttk.Combobox(
        frame,
        textvariable=value,
        values=tuple(mapping),
        state="readonly",
    )
    box.pack(fill="x", pady=(2, 0))
    _help(frame, variable)

    def getter():
        label = value.get()
        if not label:
            return None
        item = mapping.get(label)
        if item is None:
            raise ValueError("Вибраний запис більше не доступний")
        return choice_snapshot(item)

    return FactControl(frame=frame, get_value=getter, focus_widget=box)


def participants_control(parent, variable, rows):
    frame = ttk.Frame(parent)
    ttk.Label(frame, text=_label_text(variable)).pack(anchor="w")
    ttk.Label(
        frame,
        text="Ctrl/Shift — вибір кількох працівників.",
    ).pack(anchor="w", pady=(2, 2))

    area = ttk.Frame(frame)
    area.pack(fill="both", expand=True)
    from tkinter import Listbox
    box = Listbox(
        area,
        selectmode="extended",
        exportselection=False,
        height=5,
    )
    ybar = ttk.Scrollbar(area, orient="vertical", command=box.yview)
    box.configure(yscrollcommand=ybar.set)
    box.pack(side="left", fill="both", expand=True)
    ybar.pack(side="right", fill="y")
    for item in rows:
        box.insert(END, item.label)
    _help(frame, variable)

    def getter():
        return selected_snapshots(rows, box.curselection())

    return FactControl(frame=frame, get_value=getter, focus_widget=box)


def long_text_control(parent, variable):
    frame = ttk.Frame(parent)
    ttk.Label(frame, text=_label_text(variable)).pack(anchor="w")
    hint = (
        "Розділяйте розділи порожнім рядком."
        if variable.variable_type == "sections"
        else "Один рядок таблиці — один рядок тексту; клітинки розділяйте Tab."
    )
    ttk.Label(frame, text=hint).pack(anchor="w", pady=(2, 2))

    area = ttk.Frame(frame)
    area.pack(fill="both", expand=True)
    text = Text(area, wrap="word", height=7, undo=True)
    ybar = ttk.Scrollbar(area, orient="vertical", command=text.yview)
    text.configure(yscrollcommand=ybar.set)
    text.pack(side="left", fill="both", expand=True)
    ybar.pack(side="right", fill="y")
    _help(frame, variable)

    if variable.variable_type == "sections":
        getter = lambda: parse_sections(text.get("1.0", "end-1c"))
    elif variable.variable_type == "table_rows":
        getter = lambda: parse_table_rows(text.get("1.0", "end-1c"))
    else:
        raise ValueError("Непідтримуваний long-text control")
    return FactControl(frame=frame, get_value=getter, focus_widget=text)


class PairControl:
    """Manual stable driver/vehicle pair editor for one fact variable."""

    def __init__(self, parent, variable, drivers, vehicles):
        self.frame = ttk.Frame(parent)
        self._pairs = []
        self._drivers = tuple(drivers)
        self._vehicles = tuple(vehicles)
        self._drivers_by_label = by_label(self._drivers)
        self._vehicles_by_label = by_label(self._vehicles)

        ttk.Label(
            self.frame, text=_label_text(variable)
        ).pack(anchor="w")
        ttk.Label(
            self.frame,
            text=(
                "Додавайте конкретні пари водій–ТЗ. "
                "У preview зберігаються стабільні ID та snapshot-реквізити."
            ),
            justify="left",
            wraplength=760,
        ).pack(fill="x", pady=(2, 4))

        pick = ttk.Frame(self.frame)
        pick.pack(fill="x")
        pick.columnconfigure(0, weight=1)
        pick.columnconfigure(1, weight=1)

        self.driver_value = StringVar(value="")
        self.vehicle_value = StringVar(value="")
        self.driver_box = ttk.Combobox(
            pick,
            textvariable=self.driver_value,
            values=tuple(self._drivers_by_label),
            state="readonly",
        )
        self.vehicle_box = ttk.Combobox(
            pick,
            textvariable=self.vehicle_value,
            values=tuple(self._vehicles_by_label),
            state="readonly",
        )
        self.driver_box.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.vehicle_box.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        controls = ttk.Frame(self.frame)
        controls.pack(fill="x", pady=(4, 4))
        ttk.Button(
            controls, text="Додати пару", command=self._add
        ).pack(side="left")
        ttk.Button(
            controls, text="Прибрати вибрану", command=self._remove
        ).pack(side="left", padx=(6, 0))

        table = ttk.Frame(self.frame)
        table.pack(fill="both", expand=True)
        table.columnconfigure(0, weight=1)
        table.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(
            table,
            columns=("driver", "vehicle"),
            show="headings",
            selectmode="browse",
            height=5,
        )
        self.tree.heading("driver", text="Водій")
        self.tree.heading("vehicle", text="Транспортний засіб")
        self.tree.column("driver", width=330, minwidth=160, stretch=True)
        self.tree.column("vehicle", width=330, minwidth=160, stretch=True)
        ybar = ttk.Scrollbar(
            table, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=ybar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        _help(self.frame, variable)

    def _add(self):
        from tkinter import messagebox

        driver = self._drivers_by_label.get(self.driver_value.get())
        vehicle = self._vehicles_by_label.get(self.vehicle_value.get())
        if driver is None or vehicle is None:
            messagebox.showerror(
                "Пара водій–ТЗ",
                "Виберіть водія і транспортний засіб.",
                parent=self.frame.winfo_toplevel(),
            )
            return
        try:
            self._pairs = add_unique_pair(self._pairs, driver, vehicle)
        except ValueError as exc:
            messagebox.showerror(
                "Пара водій–ТЗ",
                str(exc),
                parent=self.frame.winfo_toplevel(),
            )
            return
        self._refresh()

    def _remove(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = int(selected[0])
        if 0 <= index < len(self._pairs):
            del self._pairs[index]
            self._refresh()

    def _refresh(self):
        self.tree.delete(*self.tree.get_children())
        for index, pair in enumerate(self._pairs):
            person = pair["person"]
            vehicle = pair["vehicle"]
            driver_label = (
                person.get("label")
                or person.get("name")
                or ("ID %s" % person.get("id"))
            )
            vehicle_label = (
                vehicle.get("label")
                or " · ".join(
                    part for part in (
                        vehicle.get("plate"),
                        vehicle.get("name"),
                    ) if part
                )
                or ("ID %s" % vehicle.get("id"))
            )
            self.tree.insert(
                "", "end", iid=str(index),
                values=(driver_label, vehicle_label),
            )

    def get_value(self):
        return [
            {
                "person": dict(item["person"]),
                "vehicle": dict(item["vehicle"]),
            }
            for item in self._pairs
        ]


def pair_control(parent, variable, catalog: FactChoiceCatalog):
    widget = PairControl(
        parent, variable, catalog.drivers, catalog.vehicles
    )
    return FactControl(
        frame=widget.frame,
        get_value=widget.get_value,
        focus_widget=widget.driver_box,
    )


def build_fact_control(parent, variable, catalog: FactChoiceCatalog):
    """Create one UI-thread control for a declared DraftVariable."""
    typ = variable.variable_type
    if typ in ("text", "date", "integer"):
        return scalar_control(parent, variable)
    if typ == "person_ref":
        return choice_control(parent, variable, catalog.employees)
    if typ == "vehicle_ref":
        return choice_control(parent, variable, catalog.vehicles)
    if typ == "participants":
        return participants_control(parent, variable, catalog.employees)
    if typ == "pairs":
        return pair_control(parent, variable, catalog)
    if typ in ("sections", "table_rows"):
        return long_text_control(parent, variable)
    raise ValueError("Для типу %s ще немає UI-контролу" % typ)
