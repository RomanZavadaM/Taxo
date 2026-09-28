# -*- coding: utf-8 -*-
"""Taxo 10.6-r5 — адаптивні фільтри звіту документів ТЗ.

Вікно «Стан документів транспортних засобів» історично створює панель
фільтрів одним горизонтальним ``pack``-рядком: дата, кнопка календаря і два
довгі прапорці. На вузьких або масштабованих екранах крайні елементи могли
виходити за доступну ширину. Цей runtime-шар не змінює дані, SQL, правила
комплектності документів, експорт чи значення фільтрів: він лише переводить
вже створені контролі в адаптивну ``grid``-розкладку.
"""
from __future__ import annotations

APP_VERSION = "10.6-r5"

REPORT_DATE_LABEL = "Стан документів на дату:"
REPORT_ACTIVE_LABEL = "Тільки авто в експлуатації"
REPORT_ISSUES_LABEL = "Тільки проблемні / попередження"


def compute_group_rows(group_widths, available_width, gap=12):
    """Розбити групи контролів на рядки без втрати порядку."""
    available = max(1, int(available_width or 1))
    rows = []
    current = []
    used = 0
    for index, raw_width in enumerate(group_widths):
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


def _find_filter_bar(win):
    """Знайти верхню панель звіту за стабільними підписами контролів."""
    expected = {REPORT_DATE_LABEL, REPORT_ACTIVE_LABEL, REPORT_ISSUES_LABEL}
    for child in win.winfo_children():
        try:
            widgets = list(child.winfo_children())
        except Exception:
            continue
        texts = {_widget_text(widget) for widget in widgets}
        if expected.issubset(texts):
            return child, widgets
    return None, []


def _control_groups(widgets):
    """Дата+поле+календар лишаються разом; кожен прапорець — окрема група."""
    if len(widgets) < 5:
        return [tuple(widgets)] if widgets else []
    return [tuple(widgets[:3]), (widgets[3],), (widgets[4],)] + [
        (widget,) for widget in widgets[5:]
    ]


def _group_requested_width(group, inner_gap=5):
    widths = []
    for widget in group:
        try:
            widths.append(max(1, int(widget.winfo_reqwidth())))
        except Exception:
            widths.append(1)
    return sum(widths) + int(inner_gap) * max(0, len(widths) - 1)


def _grid_filter_bar(frame, widgets, available_width=None):
    """Перекомпонувати вже створені фільтри без зміни callback/variables."""
    if not frame or not widgets:
        return 0
    try:
        frame.update_idletasks()
        if available_width is None:
            available_width = frame.winfo_width()
        if not available_width or int(available_width) <= 1:
            available_width = frame.winfo_toplevel().winfo_width() - 20
        available_width = max(360, int(available_width))

        groups = _control_groups(widgets)
        group_widths = [_group_requested_width(group) for group in groups]
        rows = compute_group_rows(group_widths, available_width, gap=12)

        for widget in widgets:
            try:
                widget.pack_forget()
            except Exception:
                pass
            try:
                widget.grid_forget()
            except Exception:
                pass

        for row_no, row in enumerate(rows):
            col = 0
            for group_position, group_index in enumerate(row):
                group = groups[group_index]
                for item_position, widget in enumerate(group):
                    left_pad = 0
                    if group_position > 0 and item_position == 0:
                        left_pad = 12
                    elif item_position > 0:
                        left_pad = 5
                    widget.grid(
                        row=row_no,
                        column=col,
                        sticky="w",
                        padx=(left_pad, 0),
                        pady=3,
                    )
                    col += 1
        return len(rows)
    except Exception:
        return 0


def _install_vehicle_doc_report_layout(win):
    if not win or getattr(win, "_taxo_vehicle_doc_filters_r5", False):
        return
    frame, widgets = _find_filter_bar(win)
    if not frame or not widgets:
        return
    setattr(win, "_taxo_vehicle_doc_filters_r5", True)
    state = {"pending": False, "width": None}

    def reflow(event=None):
        try:
            width = int(getattr(event, "width", 0) or frame.winfo_width() or 0)
            if width <= 1:
                width = max(360, win.winfo_width() - 20)
            if state["pending"] or state["width"] == width:
                return
            state["pending"] = True

            def apply():
                state["pending"] = False
                state["width"] = width
                _grid_filter_bar(frame, widgets, width)

            frame.after_idle(apply)
        except Exception:
            state["pending"] = False

    try:
        frame.bind("<Configure>", reflow, add="+")
    except TypeError:
        frame.bind("<Configure>", reflow)
    frame.after_idle(reflow)


def install(core, base_app):
    if getattr(core, "_TAXO_1065_INSTALLED", False):
        return core.App

    core.APP_VERSION = APP_VERSION

    class Taxo1065App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

        def show_vehicle_documents_report(self):
            result = super().show_vehicle_documents_report()
            win = getattr(self, "vehicle_documents_report_win", None)
            if win is not None:
                _install_vehicle_doc_report_layout(win)
            return result

    Taxo1065App.__name__ = "App"
    Taxo1065App.__qualname__ = "App"
    core._TAXO_1065_INSTALLED = True
    core.App = Taxo1065App
    return Taxo1065App
