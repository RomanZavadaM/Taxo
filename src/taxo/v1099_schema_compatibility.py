# -*- coding: utf-8 -*-
"""Taxo 10.9-r9: centralized SQLite schema compatibility baseline."""
from __future__ import annotations

from database_runtime import SUPPORTED_SCHEMA_VERSION, mark_schema_version

FEATURE_VERSION = "10.9-r9"


def install(core, App):
    """Wrap the established init path without rewriting historical migrations.

    The legacy ``init_db`` remains the source of schema creation/upgrades for
    baseline schema 1. Only after it returns successfully do we stamp
    ``PRAGMA user_version``. A failed init therefore can never advertise a
    migration that did not complete.
    """
    original_init_db = core.init_db

    def init_db_with_schema_baseline(*args, **kwargs):
        result = original_init_db(*args, **kwargs)
        con = core.db()
        try:
            mark_schema_version(con, SUPPORTED_SCHEMA_VERSION)
            con.commit()
        finally:
            con.close()
        return result

    core.init_db = init_db_with_schema_baseline

    class App1099(App):
        pass

    core.APP_VERSION = FEATURE_VERSION
    return App1099
