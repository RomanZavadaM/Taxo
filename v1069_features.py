# -*- coding: utf-8 -*-
"""Taxo 10.6-r9 — адаптивний header картки документів ТЗ.

Базове вікно пакує назву автомобіля зліва, а summary стану документів справа в
одному рядку. При довгих текстах вони конкурують за ширину. Цей шар працює
лише з уже створеними label widgets: при достатній ширині тримає їх в одному
рядку, а при нестачі переносить summary на другий рядок і дає йому безпечний
wraplength. Значення ``summary_var`` і логіка його розрахунку не змінюються.
"""
from __future__ import annotations

import vehicle_documents as vehicle_docs

APP_VERSION = "10.6-r9"
HEADER_GAP = 12
HEADER_SIDE_PADDING = 8


def header_layout(vehicle_width, summary_width, available_width, gap=HEADER_GAP):
    """Return ``wide`` or ``stacked`` for measured label widths."""
    vehicle_width = max(0, int(vehicle_width or 0))
    summary_width = max(0, int(summary_width or 0))
    available_width = max(1, int(available_width or 1))
    need = vehicle_width + summary_width + max(0, int(gap or 0))
    return "wide" if need <= available_width else "stacked"


def header_wraplength(available_width):
    """Keep wrapped summary readable inside the header frame."""
    available_width = max(1, int(available_width or 1))
    return max(240, min(900, available_width - 2 * HEADER_SIDE_PADDING))


def _find_header_widgets(owner):
    """Find the original header frame and its two labels without relying on order."""
    expected_vehicle = vehicle_docs._vehicle_label(owner.vehicle)
    try:
        frames = [child for child in owner.win.winfo_children() if child.winfo_class() in ("TFrame", "Frame")]
    except Exception:
        return None, None, None

    for frame in frames:
        try:
            labels = [child for child in frame.winfo_children() if child.winfo_class() in ("TLabel", "Label")]
        except Exception:
            continue
        vehicle_label = None
        summary_label = None
        for label in labels:
            try:
                if str(label.cget("text") or "") == expected_vehicle:
                    vehicle_label = label
                textvariable = str(label.cget("textvariable") or "")
                if textvariable and textvariable == str(owner.summary_var):
                    summary_label = label
            except Exception:
                continue
        if vehicle_label is not None and summary_label is not None:
            return frame, vehicle_label, summary_label
    return None, None, None


def _install_header_adaptation(owner):
    if getattr(owner, "_taxo_vehicle_document_header_r9", False):
        return
    frame, vehicle_label, summary_label = _find_header_widgets(owner)
    if frame is None:
        return
    setattr(owner, "_taxo_vehicle_document_header_r9", True)

    try:
        vehicle_label.pack_forget()
    except Exception:
        pass
    try:
        summary_label.pack_forget()
    except Exception:
        pass

    state = {"layout": None, "size": None, "pending": False}

    def apply(width):
        available = max(1, int(width or 1))
        try:
            vehicle_width = int(vehicle_label.winfo_reqwidth() or 0)
        except Exception:
            vehicle_width = 0
        try:
            summary_width = int(summary_label.winfo_reqwidth() or 0)
        except Exception:
            summary_width = 0
        layout = header_layout(vehicle_width, summary_width, available)
        wrap = header_wraplength(available)

        if state["layout"] != layout:
            try:
                vehicle_label.grid_forget()
                summary_label.grid_forget()
            except Exception:
                pass
            if layout == "wide":
                frame.grid_columnconfigure(0, weight=0)
                frame.grid_columnconfigure(1, weight=1)
                vehicle_label.grid(row=0, column=0, sticky="w", padx=(0, HEADER_GAP))
                summary_label.grid(row=0, column=1, sticky="e")
            else:
                frame.grid_columnconfigure(0, weight=1)
                frame.grid_columnconfigure(1, weight=0)
                vehicle_label.grid(row=0, column=0, sticky="w")
                summary_label.grid(row=1, column=0, sticky="ew", pady=(3, 0))
            state["layout"] = layout

        try:
            if layout == "stacked":
                summary_label.configure(wraplength=wrap, justify="left", anchor="w")
            else:
                summary_label.configure(wraplength=0, justify="right", anchor="e")
        except Exception:
            pass

    def reflow(event=None):
        try:
            width = int(getattr(event, "width", 0) or frame.winfo_width() or 0)
            if width <= 1:
                width = max(320, int(owner.win.winfo_width() or 820) - 20)
            if state["pending"] or state["size"] == width:
                return
            state["pending"] = True

            def later():
                state["pending"] = False
                state["size"] = width
                apply(width)

            frame.after_idle(later)
        except Exception:
            state["pending"] = False

    try:
        frame.bind("<Configure>", reflow, add="+")
    except TypeError:
        frame.bind("<Configure>", reflow)
    frame.after_idle(reflow)


def _patch_vehicle_document_header():
    cls = vehicle_docs.VehicleDocumentsWindow
    if getattr(cls, "_taxo_r9_header_patched", False):
        return
    original_build = cls._build

    def responsive_build(self):
        result = original_build(self)
        _install_header_adaptation(self)
        return result

    cls._build = responsive_build
    cls._taxo_r9_header_patched = True
    cls._taxo_r9_original_build = original_build


def install(core, base_app):
    if getattr(core, "_TAXO_1069_INSTALLED", False):
        return core.App

    _patch_vehicle_document_header()
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
