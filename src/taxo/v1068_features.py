# -*- coding: utf-8 -*-
"""Taxo 10.6-r8 — адаптивна форма документа транспортного засобу.

Базова форма додавання/редагування документа має багато вертикальних рядків,
фіксований ``wraplength=520`` і кнопку «Зберегти» в останньому рядку. На
невисокому або масштабованому екрані це створює ризик обрізання нижньої дії,
а пояснювальний текст може бути ширшим за фактичну праву колонку.

Цей runtime-шар не переписує форму і не торкається її ``save()`` closure,
валідації, архівації, копій або SQL. Він лише адаптує вже створені widgets:
ущільнює стандартні вертикальні відступи на невисокому вікні, зменшує висоту
поля примітки на один рядок та підлаштовує ``wraplength`` пояснень.
"""
from __future__ import annotations

import tkinter as tk

import vehicle_documents as vehicle_docs

APP_VERSION = "10.6-r8"

ARCHIVE_HELP_PREFIX = "За замовчуванням попередні документи не архівуються."
CURRENT_COPY_PREFIX = "Поточна копія збережена."
SAVE_LABEL = "Зберегти"


def form_layout_metrics(width, height):
    """Повернути безпечні UI-метрики для поточного розміру форми."""
    width = max(1, int(width or 1))
    height = max(1, int(height or 1))
    compact = height < 620
    wraplength = max(240, min(520, width - 210))
    return {
        "compact": compact,
        "wraplength": wraplength,
        "field_pady": 4 if compact else 7,
        "save_pady": 8 if compact else 16,
        "notes_height": 3 if compact else 4,
    }


def _widget_text(widget):
    try:
        return str(widget.cget("text") or "")
    except Exception:
        return ""


def _is_document_form(win):
    try:
        return str(win.title()) == "Документ транспортного засобу"
    except Exception:
        return False


def _find_new_document_form(owner, before):
    try:
        for child in owner.winfo_children():
            if child not in before and _is_document_form(child):
                return child
    except Exception:
        return None
    return None


def _install_form_adaptation(win):
    if not win or getattr(win, "_taxo_vehicle_document_form_r8", False):
        return
    setattr(win, "_taxo_vehicle_document_form_r8", True)

    notes = None
    help_labels = []
    save_button = None
    grid_widgets = []
    original_pady = {}

    try:
        children = list(win.winfo_children())
    except Exception:
        return

    for child in children:
        text = _widget_text(child)
        if isinstance(child, tk.Text):
            notes = child
        if text.startswith(ARCHIVE_HELP_PREFIX) or text.startswith(CURRENT_COPY_PREFIX):
            help_labels.append(child)
        if text == SAVE_LABEL:
            save_button = child
        try:
            info = child.grid_info()
        except Exception:
            info = {}
        if info:
            grid_widgets.append(child)
            original_pady[child] = info.get("pady", 0)

    state = {"pending": False, "size": None}

    def apply_layout(width, height):
        metrics = form_layout_metrics(width, height)
        for label in help_labels:
            try:
                label.configure(wraplength=metrics["wraplength"], justify="left")
            except Exception:
                pass
        if notes is not None:
            try:
                notes.configure(height=metrics["notes_height"])
            except Exception:
                pass

        for child in grid_widgets:
            original = original_pady.get(child, 0)
            text = str(original).strip()
            try:
                if metrics["compact"] and text == "7":
                    child.grid_configure(pady=metrics["field_pady"])
                elif metrics["compact"] and child is save_button:
                    child.grid_configure(pady=metrics["save_pady"])
                elif not metrics["compact"]:
                    child.grid_configure(pady=original)
            except Exception:
                pass

    def reflow(event=None):
        try:
            width = int(getattr(event, "width", 0) or win.winfo_width() or 0)
            height = int(getattr(event, "height", 0) or win.winfo_height() or 0)
            if width <= 1:
                width = 580
            if height <= 1:
                height = 520
            size = (width, height)
            if state["pending"] or state["size"] == size:
                return
            state["pending"] = True

            def apply():
                state["pending"] = False
                state["size"] = size
                apply_layout(width, height)

            win.after_idle(apply)
        except Exception:
            state["pending"] = False

    try:
        win.resizable(True, True)
    except Exception:
        pass
    try:
        win.bind("<Configure>", reflow, add="+")
    except TypeError:
        win.bind("<Configure>", reflow)
    win.after_idle(reflow)


def _patch_vehicle_document_form():
    cls = vehicle_docs.VehicleDocumentsWindow
    if getattr(cls, "_taxo_r8_form_patched", False):
        return
    original_form = cls._form

    def responsive_form(self, row=None):
        try:
            before = set(self.win.winfo_children())
        except Exception:
            before = set()
        result = original_form(self, row)
        form = _find_new_document_form(self.win, before)
        if form is not None:
            _install_form_adaptation(form)
        return result

    cls._form = responsive_form
    cls._taxo_r8_form_patched = True
    cls._taxo_r8_original_form = original_form


def install(core, base_app):
    if getattr(core, "_TAXO_1068_INSTALLED", False):
        return core.App

    _patch_vehicle_document_form()
    core.APP_VERSION = APP_VERSION

    class Taxo1068App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

    Taxo1068App.__name__ = "App"
    Taxo1068App.__qualname__ = "App"
    core._TAXO_1068_INSTALLED = True
    core.App = Taxo1068App
    return Taxo1068App
