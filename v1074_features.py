# -*- coding: utf-8 -*-
"""Taxo 10.7-r4 — final runtime identity for editable operations orders.

The actual r4 operations UI lives in ``operations_orders_ui.py`` and already
routes order/assignment edits through the audited model API.  This outer layer
therefore only owns the current application identity.  Keeping it deliberately
thin avoids adding a second set of buttons/dialogs on top of the real operations
window and prevents raw-SQL UI updates from bypassing ``operations_change_log``.
"""
from __future__ import annotations

APP_VERSION = "10.7-r4"


def install(core, base_app):
    if getattr(core, "_TAXO_1074_INSTALLED", False):
        return core.App

    core.APP_VERSION = APP_VERSION

    class Taxo1074App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

    Taxo1074App.__name__ = "App"
    Taxo1074App.__qualname__ = "App"
    core.App = Taxo1074App
    core._TAXO_1074_INSTALLED = True
    return Taxo1074App
