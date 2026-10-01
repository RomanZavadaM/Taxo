# -*- coding: utf-8 -*-
"""Low-level SQLite runtime connection helpers for Taxo.

This module owns only infrastructure policy for opening the current Taxo
SQLite database.  It intentionally contains no Tk/UI code and no domain
rules.  Callers provide the database path explicitly so workspace selection
remains outside this module.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Union

DatabasePath = Union[str, Path]


def connect_database(path: DatabasePath) -> sqlite3.Connection:
    """Open a Taxo SQLite connection with the established safety settings.

    The settings mirror the historical ``main.db()`` contract:
    - 30 second connection/busy timeout;
    - ``sqlite3.Row`` rows;
    - foreign keys enabled;
    - rollback journal (safe for workspace locations that may be networked);
    - FULL synchronous durability.
    """
    con = sqlite3.connect(path, timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA busy_timeout=30000")
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("PRAGMA synchronous=FULL")
    return con
