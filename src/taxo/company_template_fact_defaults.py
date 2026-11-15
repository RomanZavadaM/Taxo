# -*- coding: utf-8 -*-
"""Current database-backed defaults for CompanyTemplates fact-entry forms.

Defaults are conveniences for one draft form only. They never modify the
read-only TemplateLibrary or a CompanyTemplates revision, and the user may edit
the prefilled value before rendering the concrete document.
"""
from __future__ import annotations

import sqlite3


def load_fact_defaults(services, variable_names):
    """Load only explicitly supported live facts requested by this template."""
    names = {str(name) for name in variable_names}
    if "company.name" not in names:
        return {}

    con = services.workspace.connect_main_db()
    try:
        try:
            row = con.execute(
                "SELECT name FROM company WHERE id=1"
            ).fetchone()
        except sqlite3.OperationalError as exc:
            if "no such table" in str(exc).lower():
                return {}
            raise
    finally:
        con.close()

    if row is None:
        return {}
    value = str(row[0] or "").strip()
    return {"company.name": value} if value else {}
