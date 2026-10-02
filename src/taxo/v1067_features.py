# -*- coding: utf-8 -*-
"""Taxo 10.6-r7 — адаптивні дії картки документів ТЗ.

У ``VehicleDocumentsWindow`` п'ять кнопок і прапорець «Показувати архів»
історично розміщуються одним горизонтальним ``pack``-рядком. На вузьких або
масштабованих екранах крайні контроли можуть виходити за видиму область.
Цей runtime-шар не змінює document schema, archive semantics, copy storage,
строки дії або callbacks: він лише перекладає вже створені контроли у
responsive ``grid`` в тому самому action-frame.
"""
from __future__ import annotations

import vehicle_documents as vehicle_docs

APP_VERSION = "10.6-r7"

DOCUMENT_ACTION_LABELS = (
    "Додати документ",
    "Редагувати",
    "Архівувати",
    "Відкрити копію",
    "Оновити",
    "Показувати архів",
)


def compute_wrapped_rows(widths, available_width, gap=6):
    """Розбити існуючі контроли на рядки без зміни порядку."""
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


def _find_document_action_bar(win):
    expected = set(DOCUMENT_ACTION_LABELS)
    for child in win.winfo_children():
        try:
            widgets = list(child.winfo_children())
        except Exception:
            continue
        by_text = {_widget_text(widget): widget for widget in widgets}
        if expected.issubset(by_text):
            return child, [by_text[label] for label in DOCUMENT_ACTION_LABELS]
    return None, []


def _grid_document_actions(frame, controls, available_width=None):
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
        return 0


def _install_document_action_layout(win):
    if not win or getattr(win, "_taxo_vehicle_document_actions_r7", False):
        return
    frame, controls = _find_document_action_bar(win)
    if not frame or not controls:
        return
    setattr(win, "_taxo_vehicle_document_actions_r7", True)
    state = {"pending": False, "width": None}

    def reflow(event=None):
        try:
            width = int(getattr(event, "width", 0) or frame.winfo_width() or 0)
            if width <= 1:
                width = max(360, win.winfo_width() - 24)
            if state["pending"] or state["width"] == width:
                return
            state["pending"] = True

            def apply():
                state["pending"] = False
                state["width"] = width
                _grid_document_actions(frame, controls, width)

            frame.after_idle(apply)
        except Exception:
            state["pending"] = False

    try:
        frame.bind("<Configure>", reflow, add="+")
    except TypeError:
        frame.bind("<Configure>", reflow)
    frame.after_idle(reflow)


def _patch_vehicle_documents_window():
    cls = vehicle_docs.VehicleDocumentsWindow
    if getattr(cls, "_taxo_r7_build_patched", False):
        return
    original_build = cls._build

    def responsive_build(self):
        result = original_build(self)
        _install_document_action_layout(self.win)
        return result

    cls._build = responsive_build
    cls._taxo_r7_build_patched = True
    cls._taxo_r7_original_build = original_build


def install(core, base_app):
    if getattr(core, "_TAXO_1067_INSTALLED", False):
        return core.App

    _patch_vehicle_documents_window()
    core.APP_VERSION = APP_VERSION

    class Taxo1067App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

    Taxo1067App.__name__ = "App"
    Taxo1067App.__qualname__ = "App"
    core._TAXO_1067_INSTALLED = True
    core.App = Taxo1067App
    return Taxo1067App
