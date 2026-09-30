# -*- coding: utf-8 -*-
"""Taxo 10.8-r1 — preserve critical UI entry points after layered UI patches.

The 10.6-r6 responsive vehicle toolbar converted the original core controls from
``pack`` to ``grid``. Later registry/TCC controls were added to the same parent
with ``pack``. Tk does not allow both geometry managers in one parent; after the
core controls were forgotten, the attempted grid layout could fail and leave
New/Edit/Documents/Document control/Deactivate/Refresh invisible.

This outer compatibility layer gives the vehicle core actions their own stable
container. Registry/Diia/TCC actions stay in their existing toolbar. No business
logic or database schema is changed.
"""
from __future__ import annotations

APP_VERSION = "10.8-r1"

VEHICLE_CORE_ACTIONS = (
    ("Нове авто", "vehicle_form"),
    ("Редагувати", "edit_vehicle"),
    ("Документи ТЗ", "vehicle_documents"),
    ("Контроль документів", "vehicle_document_control"),
    ("Вивести з експлуатації", "delete_vehicle"),
    ("Оновити", "load_vehicles"),
)

CRITICAL_APP_METHODS = (
    "vehicle_form",
    "edit_vehicle",
    "vehicle_documents",
    "vehicle_document_control",
    "delete_vehicle",
    "load_vehicles",
    "show_waybills_for_schedule",
    "open_military_transport_statement",
    "show_employee_registry",
    "open_operations_center",
)

CRITICAL_NAV_SECTIONS = (
    "Працівники", "Табель обліку", "Графіки", "Транспорт", "Експлуатація",
    "Маршрути", "Документи", "Тахограф", "Звіти", "Налаштування",
)


def missing_methods(obj, names=CRITICAL_APP_METHODS):
    return tuple(name for name in names if not callable(getattr(obj, name, None)))


def missing_labels(actual, required):
    present = {str(value) for value in actual}
    return tuple(label for label in required if label not in present)


def _widget_text(widget):
    try:
        return str(widget.cget("text") or "")
    except Exception:
        return ""


def _walk(widget):
    try:
        children = widget.winfo_children()
    except Exception:
        return
    for child in children:
        yield child
        yield from _walk(child)


def _hide_legacy_core_actions(app):
    """Hide only old duplicate core buttons; keep registry/TCC actions intact."""
    root = getattr(app, "tab_vehicles", None)
    if root is None:
        return
    legacy_labels = {label for label, _method in VEHICLE_CORE_ACTIONS}
    legacy_labels.add("Документи")
    for widget in _walk(root):
        if widget is getattr(app, "vehicle_core_toolbar", None):
            continue
        if _widget_text(widget) not in legacy_labels:
            continue
        # Do not touch controls in the new dedicated toolbar.
        try:
            if widget.master is getattr(app, "vehicle_core_toolbar", None):
                continue
        except Exception:
            pass
        try:
            widget.pack_forget()
        except Exception:
            pass
        try:
            widget.grid_forget()
        except Exception:
            pass


def _layout_toolbar(app, available_width=None):
    frame = getattr(app, "vehicle_core_toolbar", None)
    buttons = getattr(app, "vehicle_core_action_buttons", ())
    inactive = getattr(app, "vehicle_core_inactive_check", None)
    controls = list(buttons) + ([inactive] if inactive is not None else [])
    if frame is None or not controls:
        return 0
    try:
        frame.update_idletasks()
        width = int(available_width or frame.winfo_width() or 0)
        if width <= 1:
            width = max(420, int(app.winfo_width()) - 30)
        widths = [max(1, int(control.winfo_reqwidth())) for control in controls]
        rows = []
        current = []
        used = 0
        gap = 8
        for index, item_width in enumerate(widths):
            extra = item_width if not current else item_width + gap
            if current and used + extra > width:
                rows.append(current)
                current = [index]
                used = item_width
            else:
                current.append(index)
                used += extra
        if current:
            rows.append(current)
        for control in controls:
            control.grid_forget()
        for row_no, row in enumerate(rows):
            for col_no, index in enumerate(row):
                controls[index].grid(row=row_no, column=col_no, sticky="w", padx=4, pady=2)
        return len(rows)
    except Exception:
        return 0


def _install_stable_vehicle_toolbar(app, core):
    if getattr(app, "_taxo_v1081_vehicle_toolbar", False):
        return
    tab = getattr(app, "tab_vehicles", None)
    tree = getattr(app, "vehicle_tree", None)
    if tab is None:
        return

    frame = core.ttk.LabelFrame(tab, text="Картка транспортного засобу", padding=(6, 4))
    pack_args = {"fill": "x", "padx": 10, "pady": (4, 5)}
    if tree is not None:
        pack_args["before"] = tree
    frame.pack(**pack_args)

    buttons = []
    for label, method_name in VEHICLE_CORE_ACTIONS:
        callback = getattr(app, method_name, None)
        if callable(callback):
            button = core.ttk.Button(frame, text=label, command=callback)
            buttons.append(button)

    inactive = None
    flag = getattr(app, "vehicle_hide_inactive", None)
    if flag is not None:
        inactive = core.ttk.Checkbutton(
            frame,
            text="Сховати неактивні автомобілі",
            variable=flag,
            command=getattr(app, "load_vehicles", None),
        )

    app.vehicle_core_toolbar = frame
    app.vehicle_core_action_buttons = tuple(buttons)
    app.vehicle_core_inactive_check = inactive
    app._taxo_v1081_vehicle_toolbar = True
    _hide_legacy_core_actions(app)

    state = {"pending": False, "width": None}
    def reflow(event=None):
        try:
            width = int(getattr(event, "width", 0) or frame.winfo_width() or 0)
            if width <= 1:
                width = max(420, int(app.winfo_width()) - 30)
            if state["pending"] or state["width"] == width:
                return
            state["pending"] = True
            def apply():
                state["pending"] = False
                state["width"] = width
                _layout_toolbar(app, width)
            frame.after_idle(apply)
        except Exception:
            state["pending"] = False
    try:
        frame.bind("<Configure>", reflow, add="+")
    except TypeError:
        frame.bind("<Configure>", reflow)
    frame.after_idle(reflow)


def install(core, base_app):
    if getattr(core, "_TAXO_1081_INSTALLED", False):
        return core.App

    core.APP_VERSION = APP_VERSION

    class Taxo1081App(base_app):
        def build_vehicles(self):
            result = super().build_vehicles()
            _install_stable_vehicle_toolbar(self, core)
            return result

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

    Taxo1081App.__name__ = "App"
    Taxo1081App.__qualname__ = "App"
    core._TAXO_1081_INSTALLED = True
    core.App = Taxo1081App
    return Taxo1081App
