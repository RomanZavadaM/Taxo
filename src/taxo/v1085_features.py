# -*- coding: utf-8 -*-
"""Taxo 10.8-r5 — STOIR forecast, repair requests and compact registry UX."""
from __future__ import annotations

import vehicle_maintenance as maintenance
import vehicle_maintenance_ui as maintenance_ui

APP_VERSION = "10.8-r5"


def install(core, base_app):
    if getattr(core, "_TAXO_1085_INSTALLED", False):
        return core.App
    core.APP_VERSION = APP_VERSION
    maintenance.ensure_schema(core)

    class Taxo1085App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % APP_VERSION)
            # У r5 Treeview є базовим віджетом реєстрів: один запис = один
            # компактний рядок. Файлові/редагувальні дії не повинні збільшувати
            # висоту рядків, як у старому grid-реєстрі зі скріншотів.
            try:
                style = core.ttk.Style(self)
                style.configure("Treeview", rowheight=26)
            except Exception:
                pass

        def open_vehicle_maintenance(self):
            return maintenance_ui.open_maintenance_center(self, core)

    Taxo1085App.__name__ = "App"
    Taxo1085App.__qualname__ = "App"
    core._TAXO_1085_INSTALLED = True
    core.App = Taxo1085App
    return Taxo1085App
