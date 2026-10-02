# -*- coding: utf-8 -*-
"""Low-level SQLite runtime connection helpers for Taxo.

This module owns infrastructure policy for opening the current Taxo SQLite
workspace database.  Taxo 10.9-r9 introduces the first explicit SQLite schema
compatibility baseline through ``PRAGMA user_version``.

Important compatibility rule:
- historical databases with ``user_version=0`` remain readable and are upgraded
  by the established ``init_db`` path before being stamped;
- r9+ refuses to open a database whose schema version is newer than this build
  supports;
- simply opening a legacy/unversioned database never stamps it as migrated.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Union

DatabasePath = Union[str, Path]

# Schema numbering is deliberately independent from the application version.
# Version 1 means: the legacy Taxo init_db path completed successfully under
# the r9 compatibility regime. Future incompatible schema migrations increment
# this integer and must be centralized through this module.
SUPPORTED_SCHEMA_VERSION = 1
LEGACY_SCHEMA_VERSION = 0


class SchemaTooNewError(RuntimeError):
    """Raised when this Taxo build cannot safely understand the database."""

    def __init__(self, actual: int, supported: int = SUPPORTED_SCHEMA_VERSION):
        self.actual = int(actual)
        self.supported = int(supported)
        super().__init__(
            "База даних створена новішою версією Taxo "
            f"(схема {self.actual}); ця збірка підтримує схему до {self.supported}. "
            "Відкрийте базу новішою версією програми."
        )


def schema_version(con: sqlite3.Connection) -> int:
    row = con.execute("PRAGMA user_version").fetchone()
    return int(row[0] if row else 0)


def assert_schema_compatible(
    con: sqlite3.Connection, *, supported: int = SUPPORTED_SCHEMA_VERSION
) -> int:
    """Return current schema version or raise before domain code touches it."""
    current = schema_version(con)
    if current > int(supported):
        raise SchemaTooNewError(current, supported)
    return current


def mark_schema_version(
    con: sqlite3.Connection, version: int = SUPPORTED_SCHEMA_VERSION
) -> int:
    """Stamp a successfully migrated database without allowing downgrade.

    Callers must invoke this only after the established schema initialization /
    migration path has completed successfully.
    """
    version = int(version)
    if version < 0:
        raise ValueError("Версія схеми не може бути від'ємною.")
    current = schema_version(con)
    if current > version:
        raise SchemaTooNewError(current, version)
    if current < version:
        con.execute(f"PRAGMA user_version={version}")
    return schema_version(con)


def connect_database(path: DatabasePath) -> sqlite3.Connection:
    """Open a Taxo SQLite connection with durability and compatibility guards.

    The settings mirror the historical ``main.db()`` contract:
    - 30 second connection/busy timeout;
    - ``sqlite3.Row`` rows;
    - foreign keys enabled;
    - rollback journal (safe for workspace locations that may be networked);
    - FULL synchronous durability;
    - refuse a schema newer than this build supports.
    """
    con = sqlite3.connect(path, timeout=30)
    try:
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA busy_timeout=30000")
        con.execute("PRAGMA journal_mode=DELETE")
        con.execute("PRAGMA synchronous=FULL")
        assert_schema_compatible(con)
        return con
    except Exception:
        con.close()
        raise
