# -*- coding: utf-8 -*-
"""Taxo 10.4-r10 feature layer — military-transport vehicle accounting."""
from __future__ import annotations

from military_transport_ui import install as install_military_transport_ui

APP_VERSION = "10.4-r10"


def install(core, base_app):
    if getattr(core, "_TAXO_10410_INSTALLED", False):
        return core.App
    core.APP_VERSION = APP_VERSION
    app = install_military_transport_ui(core, base_app)
    core._TAXO_10410_INSTALLED = True
    core.App = app
    return app
