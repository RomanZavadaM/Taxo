# -*- coding: utf-8 -*-
"""Taxo 10.7-r6 — retention safety identity layer.

The functional fix is deliberately small and lives in main.init_db(): the
automatic SQLite backup is taken before the 48-month retention purge.  This
layer keeps the revision explicit in the runtime chain without duplicating
storage logic.
"""
from __future__ import annotations

APP_VERSION = "10.7-r6"


def install(core, base_app):
    if getattr(core, "_TAXO_V1076_INSTALLED", False):
        return base_app
    core.APP_VERSION = APP_VERSION
    core._TAXO_V1076_INSTALLED = True
    return base_app
