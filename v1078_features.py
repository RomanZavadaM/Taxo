# -*- coding: utf-8 -*-
"""Taxo 10.7-r8 — grouped operations-order catalog identity layer."""
from __future__ import annotations

APP_VERSION = "10.7-r8"

def install(core, base_app):
    if getattr(core, "_TAXO_V1078_INSTALLED", False):
        return base_app
    core.APP_VERSION = APP_VERSION
    core._TAXO_V1078_INSTALLED = True
    return base_app
