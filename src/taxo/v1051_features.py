# -*- coding: utf-8 -*-
"""Taxo 10.5-r1 feature layer — official military transport statement."""
from __future__ import annotations

from military_transport_statement_ui import install as install_statement_ui

APP_VERSION = "10.5-r1"


def install(core, base_app):
    # Keep runtime identity synchronized even before the final source-marker bump.
    core.APP_VERSION = APP_VERSION
    return install_statement_ui(core, base_app)
