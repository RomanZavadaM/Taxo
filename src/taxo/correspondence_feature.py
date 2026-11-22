# -*- coding: utf-8 -*-
"""Visible Taxo navigation entry for the correspondence center."""
from __future__ import annotations

import sys

import correspondence_ui


NAV_LABEL = "Кореспонденція"


def _alive(widget):
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def install(core, base_app):
    """Add one permanent sidebar entry without changing legacy navigation code."""

    class TaxoCorrespondenceApp(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._install_correspondence_nav()

        def open_correspondence_center(self):
            from workspace import load_workspace_root

            return correspondence_ui.open_correspondence_center(
                self,
                core,
                load_workspace_root(),
            )

        def _install_correspondence_nav(self):
            named = getattr(self, "_nav_named_buttons", {})
            if NAV_LABEL in named:
                return
            anchor = (
                named.get("СТОІР")
                or named.get("Експлуатація")
                or named.get("Маршрути")
            )
            if not _alive(anchor):
                return

            parent = anchor.master
            icon = core.nav_photo(parent, "document", 24)
            self._nav_icons[NAV_LABEL] = icon

            def invoke(_event=None):
                self.open_correspondence_center()
                return "break"

            if sys.platform == "darwin":
                btn = core.tk.Label(
                    parent,
                    image=icon,
                    text=NAV_LABEL,
                    compound="left",
                    anchor="w",
                    takefocus=1,
                    bg=core.PALETTE["sidebar"],
                    fg="#FFFFFF",
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                    padx=28,
                    pady=8,
                    font=("TkDefaultFont", 10, "bold"),
                    cursor="pointinghand",
                )
                btn.bind("<Button-1>", invoke, add="+")
                btn.bind("<Return>", invoke, add="+")
                btn.bind("<space>", invoke, add="+")
            else:
                btn = core.tk.Button(
                    parent,
                    image=icon,
                    text=NAV_LABEL,
                    compound="left",
                    command=self.open_correspondence_center,
                    anchor="w",
                    bg=core.PALETTE["sidebar"],
                    fg="#FFFFFF",
                    activebackground=core.PALETTE["blue_dark"],
                    activeforeground="#FFFFFF",
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                    padx=28,
                    pady=7,
                    font=("TkDefaultFont", 9, "bold"),
                    cursor="hand2",
                )
            try:
                btn.pack(fill="x", after=anchor)
            except Exception:
                btn.pack(fill="x")
            named[NAV_LABEL] = btn

    TaxoCorrespondenceApp.__name__ = "App"
    TaxoCorrespondenceApp.__qualname__ = "App"
    core.App = TaxoCorrespondenceApp
    return TaxoCorrespondenceApp
