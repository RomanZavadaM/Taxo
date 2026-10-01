# -*- coding: utf-8 -*-
"""Small data-access foundation for new Taxo modules.

The historical application still contains many direct SQL calls.  New modules
should not import ``main`` merely to obtain a connection.  This module provides
a narrow, domain-neutral boundary on top of the established SQLite runtime
policy.  It does not know table names, schemas, UI objects or business rules.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Callable, Iterable, Iterator, Optional, Sequence


class DataAccess:
    """Fresh-connection query/transaction helpers.

    ``connection_factory`` is resolved for every operation, so switching the
    active Taxo workspace cannot leave a repository bound to the old database.
    Domain repositories may depend on this class without depending on ``main``.
    """

    def __init__(self, connection_factory: Callable[[], Any]):
        self._connection_factory = connection_factory

    def fetch_one(self, sql: str, params: Sequence[Any] = ()) -> Optional[Any]:
        con = self._connection_factory()
        try:
            return con.execute(sql, tuple(params)).fetchone()
        finally:
            con.close()

    def fetch_all(self, sql: str, params: Sequence[Any] = ()) -> list[Any]:
        con = self._connection_factory()
        try:
            return list(con.execute(sql, tuple(params)).fetchall())
        finally:
            con.close()

    def execute(self, sql: str, params: Sequence[Any] = ()) -> int:
        """Execute one write atomically and return the cursor rowcount."""
        con = self._connection_factory()
        try:
            cur = con.execute(sql, tuple(params))
            con.commit()
            return int(cur.rowcount)
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def executemany(self, sql: str, rows: Iterable[Sequence[Any]]) -> int:
        """Execute a batch atomically and return SQLite's rowcount when known."""
        con = self._connection_factory()
        try:
            cur = con.executemany(sql, rows)
            con.commit()
            return int(cur.rowcount)
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    @contextmanager
    def transaction(self) -> Iterator[Any]:
        """Yield one connection and commit/rollback exactly once at the boundary."""
        con = self._connection_factory()
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
