# -*- coding: utf-8 -*-
"""Taxo 10.6-r9 — адаптивний заголовок картки документів ТЗ.

У базовому ``VehicleDocumentsWindow._build`` назва автомобіля пакується зліва,
а довгий підсумок стану документів — справа в тому самому рядку. Якщо назва
автомобіля довга або одночасно є кілька проблемних документів, обидва тексти
конкурують за ширину й можуть обрізатися.

Цей runtime-шар не змінює ``summary_var`` і не перераховує стан документів.
Він лише переводить уже створені labels заголовка в адаптивний ``grid``:
широкий header лишається в один ряд, вузький переходить у два рядки, а
підсумок отримує безпечний динамічний ``wraplength``.
"""
from __future__ import annotations

import vehicle_documents as vehicle_docs

APP_VERSION = "10.6-r9"


def header_layout_metrics(title_width, summary_width, available_width):
    """Повернути режим header без зміни його тексту або джерел даних."""
    title = max(1, int(title_width or 1))
    summary = max(1, int(summary_width or 1))
    available = max(320, int(available_width or 1))
    gap = 12
    stacked = title + summary + gap > available
    return {
        "stacked": stacked,
        "wraplength": max(260, min(760, available - 12)) if stacked else 0,
        "gap": gap,
    }


def _widget_text(widget):
    try:
        return str(widget.cget("text") or "")
    except Exception:
        return ""


def _widget_textvariable(widget):
    try:
        return str(widget.cget("textvariable") or "")
    except Exception:
        return ""


def _find_document_header(owner):
    try:
        expected_title = vehicle_docs._vehicle_label(owner.vehicle)
        expected_var = str(owner.summary_var)
        frames = list(owner.win.winfo_children())
    except Exception:
        return None, None, None

    for frame in frames:
        try:
            widgets = list(frame.winfo_children())
        except Exception:
            continue
        title = next((w for w in widgets if _widget_text(w) == expected_title), None)
        summary = next((w for w in widgets if _widget_textvariable(w) == expected_var), None)
        if title is not None and summary is not None:
            return frame, title, summary
    return None, None, None


def _grid_document_header(frame, title, summary, available_width=None):
    if not frame or title is None or summary is None:
        return False
    try:
        frame.update_idletasks()
        if available_width is None:
            available_width = frame.winfo_width()
        if not available_width or int(available_width) <= 1:
            available_width = frame.winfo_toplevel().winfo_width() - 20
        available_width = max(320, int(available_width))
        metrics = header_layout_metrics(
            title.winfo_reqwidth(),
            summary.winfo_reqwidth(),
            available_width,
        )

        for widget in (title, summary):
            try:
                widget.pack_forget()
            except Exception:
                pass
            try:
                widget.grid_forget()
            except Exception:
                pass

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
        if metrics["stacked"]:
            title.grid(row=0, column=0, columnspan=2, sticky="w")
            summary.configure(
                wraplength=metrics["wraplength"],
                justify="left",
                anchor="w",
            )
            summary.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 0))
        else:
            title.grid(row=0, column=0, sticky="w")
            summary.configure(wraplength=0, justify="right", anchor="e")
            summary.grid(row=0, column=1, sticky="e", padx=(metrics["gap"], 0))
        return bool(metrics["stacked"])
    except Exception:
        return False


def _install_document_header_layout(owner):
    if not owner or getattr(owner, "_taxo_vehicle_document_header_r9", False):
        return
    frame, title, summary = _find_document_header(owner)
    if not frame or title is None or summary is None:
        return
    setattr(owner, "_taxo_vehicle_document_header_r9", True)
    state = {"pending": False, "width": None}

    def reflow(event=None):
        try:
            width = int(getattr(event, "width", 0) or frame.winfo_width() or 0)
            if width <= 1:
                width = max(320, owner.win.winfo_width() - 20)
            if state["pending"] or state["width"] == width:
                return
            state["pending"] = True

            def apply():
                state["pending"] = False
                state["width"] = width
                _grid_document_header(frame, title, summary, width)

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
    if getattr(cls, "_taxo_r9_header_patched", False):
        return
    original_build = cls._build

    def responsive_build(self):
        result = original_build(self)
        _install_document_header_layout(self)
        return result

    cls._build = responsive_build
    cls._taxo_r9_header_patched = True
    cls._taxo_r9_original_build = original_build


def install(core, base_app):
    if getattr(core, "_TAXO_1069_INSTALLED", False):
        return core.App

    _patch_vehicle_documents_window()
    core.APP_VERSION = APP_VERSION

    class Taxo1069App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

    Taxo1069App.__name__ = "App"
    Taxo1069App.__qualname__ = "App"
    core._TAXO_1069_INSTALLED = True
    core.App = Taxo1069App
    return Taxo1069App
