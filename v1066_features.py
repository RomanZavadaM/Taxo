# -*- coding: utf-8 -*-
"""Taxo 10.6-r6 — адаптивна панель команд реєстру ТЗ.

Базовий реєстр транспортних засобів створює шість кнопок одним горизонтальним
``pack``-рядком, а r1 додає праворуч довгий прапорець приховування неактивних
автомобілів. На вузьких або масштабованих екранах крайні елементи можуть
виходити за видиму область. Цей runtime-шар лише перекладає вже створені
контроли у responsive ``grid``; callback-и, змінні фільтра та дані не змінює.
"""
from __future__ import annotations

APP_VERSION = "10.6-r6"

VEHICLE_ACTION_LABELS = (
    "Нове авто",
    "Редагувати",
    "Документи",
    "Контроль документів",
    "Вивести з експлуатації",
    "Оновити",
    "Сховати неактивні автомобілі",
)


def compute_wrapped_rows(widths, available_width, gap=6):
    """Розбити контроли на рядки без втрати порядку або елементів."""
    available = max(1, int(available_width or 1))
    rows = []
    current = []
    used = 0
    for index, raw_width in enumerate(widths):
        width = max(1, int(raw_width or 1))
        extra = width if not current else int(gap) + width
        if current and used + extra > available:
            rows.append(tuple(current))
            current = [index]
            used = width
        else:
            current.append(index)
            used += extra
    if current:
        rows.append(tuple(current))
    return tuple(rows)


def _widget_text(widget):
    try:
        return str(widget.cget("text") or "")
    except Exception:
        return ""


def _find_vehicle_toolbar(app):
    """Повернути r1/base toolbar і контроли у стабільному логічному порядку."""
    frame = getattr(app, "vehicle_hide_inactive_control", None)
    candidates = []
    if frame is not None:
        candidates.append(frame)
    tab = getattr(app, "tab_vehicles", None)
    if tab is not None:
        try:
            candidates.extend(child for child in tab.winfo_children() if child not in candidates)
        except Exception:
            pass

    expected = set(VEHICLE_ACTION_LABELS)
    for candidate in candidates:
        try:
            widgets = list(candidate.winfo_children())
        except Exception:
            continue
        by_text = {_widget_text(widget): widget for widget in widgets}
        if expected.issubset(by_text):
            return candidate, [by_text[label] for label in VEHICLE_ACTION_LABELS]
    return None, []


def _grid_vehicle_toolbar(frame, controls, available_width=None):
    """Перекомпонувати існуючі кнопки/прапорець відповідно до ширини toolbar."""
    if not frame or not controls:
        return 0
    try:
        frame.update_idletasks()
        if available_width is None:
            available_width = frame.winfo_width()
        if not available_width or int(available_width) <= 1:
            available_width = frame.winfo_toplevel().winfo_width() - 24
        available_width = max(360, int(available_width))
        widths = [max(1, int(control.winfo_reqwidth())) for control in controls]
        rows = compute_wrapped_rows(widths, available_width, gap=6)

        for control in controls:
            try:
                control.pack_forget()
            except Exception:
                pass
            try:
                control.grid_forget()
            except Exception:
                pass

        for row_no, row in enumerate(rows):
            for col_no, index in enumerate(row):
                controls[index].grid(
                    row=row_no,
                    column=col_no,
                    sticky="w",
                    padx=3,
                    pady=2,
                )
        return len(rows)
    except Exception:
        # UI-polish не повинен блокувати роботу реєстру ТЗ.
        return 0


def _install_vehicle_toolbar_layout(app):
    if getattr(app, "_taxo_vehicle_toolbar_r6", False):
        return
    frame, controls = _find_vehicle_toolbar(app)
    if not frame or not controls:
        return
    setattr(app, "_taxo_vehicle_toolbar_r6", True)
    state = {"pending": False, "width": None}

    def reflow(event=None):
        try:
            width = int(getattr(event, "width", 0) or frame.winfo_width() or 0)
            if width <= 1:
                width = max(360, app.winfo_width() - 24)
            if state["pending"] or state["width"] == width:
                return
            state["pending"] = True

            def apply():
                state["pending"] = False
                state["width"] = width
                _grid_vehicle_toolbar(frame, controls, width)

            frame.after_idle(apply)
        except Exception:
            state["pending"] = False

    try:
        frame.bind("<Configure>", reflow, add="+")
    except TypeError:
        frame.bind("<Configure>", reflow)
    frame.after_idle(reflow)


def install(core, base_app):
    if getattr(core, "_TAXO_1066_INSTALLED", False):
        return core.App

    core.APP_VERSION = APP_VERSION

    class Taxo1066App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

        def build_vehicles(self):
            result = super().build_vehicles()
            _install_vehicle_toolbar_layout(self)
            return result

    Taxo1066App.__name__ = "App"
    Taxo1066App.__qualname__ = "App"
    core._TAXO_1066_INSTALLED = True
    core.App = Taxo1066App
    return Taxo1066App
