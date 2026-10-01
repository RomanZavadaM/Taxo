# -*- coding: utf-8 -*-
"""Taxo 10.8-r4 — окремий центр СТОІР: пробіг, ТО, ремонти та ОТК."""
from __future__ import annotations

import sys

import vehicle_maintenance as maintenance
import vehicle_maintenance_ui as maintenance_ui

APP_VERSION = "10.8-r4"
NAV_LABEL = "СТОІР"


def _alive(widget):
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def install(core, base_app):
    if getattr(core, "_TAXO_1084_INSTALLED", False):
        return core.App
    core.APP_VERSION = APP_VERSION
    maintenance.ensure_schema(core)

    class Taxo1084App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)
            self._install_stoir_nav()

        def open_vehicle_maintenance(self):
            return maintenance_ui.open_maintenance_center(self, core)

        def _install_stoir_nav(self):
            named = getattr(self, "_nav_named_buttons", {})
            if NAV_LABEL in named:
                return
            anchor = named.get("Експлуатація") or named.get("Маршрути")
            if not _alive(anchor):
                return
            parent = anchor.master
            icon = core.nav_photo(parent, "gear", 24)
            self._nav_icons[NAV_LABEL] = icon

            def invoke(_event=None):
                self.open_vehicle_maintenance()
                return "break"

            if sys.platform == "darwin":
                btn = core.tk.Label(
                    parent, image=icon, text=NAV_LABEL, compound="left", anchor="w",
                    takefocus=1, bg=core.PALETTE["sidebar"], fg="#FFFFFF",
                    relief="flat", bd=0, highlightthickness=0,
                    padx=28, pady=8, font=("TkDefaultFont",10,"bold"), cursor="pointinghand",
                )
                btn.bind("<Button-1>", invoke, add="+")
                btn.bind("<Return>", invoke, add="+")
                btn.bind("<space>", invoke, add="+")
            else:
                btn = core.tk.Button(
                    parent, image=icon, text=NAV_LABEL, compound="left",
                    command=self.open_vehicle_maintenance, anchor="w",
                    bg=core.PALETTE["sidebar"], fg="#FFFFFF",
                    activebackground=core.PALETTE["blue_dark"], activeforeground="#FFFFFF",
                    relief="flat", bd=0, highlightthickness=0,
                    padx=28, pady=7, font=("TkDefaultFont",9,"bold"), cursor="hand2",
                )
            # Розміщуємо як окрему підточку біля «Експлуатації», а не додаємо
            # нові вкладки до вже перевантаженого центру наказів.
            try:
                btn.pack(fill="x", after=anchor)
            except Exception:
                btn.pack(fill="x")
            named[NAV_LABEL] = btn

    Taxo1084App.__name__ = "App"
    Taxo1084App.__qualname__ = "App"
    core._TAXO_1084_INSTALLED = True
    core.App = Taxo1084App
    return Taxo1084App
