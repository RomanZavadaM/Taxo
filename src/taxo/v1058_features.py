# -*- coding: utf-8 -*-
"""Taxo 10.5-r8 — Windows 7 / openpyxl tabId compatibility checkpoint.

The functional compatibility patch lives in the existing registry parser layer;
this outer layer advances the issued application identity without changing r7
business workflows.
"""
from __future__ import annotations

APP_VERSION = "10.5-r8"


def install(core, base_app):
    if getattr(core, "_TAXO_1058_INSTALLED", False):
        return core.App
    core.APP_VERSION = APP_VERSION

    class Taxo1058App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

    Taxo1058App.__name__ = "App"
    Taxo1058App.__qualname__ = "App"
    core._TAXO_1058_INSTALLED = True
    core.App = Taxo1058App
    return Taxo1058App
