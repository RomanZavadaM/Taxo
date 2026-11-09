# -*- coding: utf-8 -*-
"""Operator-controlled order removal with an audit snapshot.

Taxo prepares paperwork; a paper original is controlled outside the app.
Signed/approved/cancelled are informative, not deletion permissions.
"""
from __future__ import annotations

from datetime import datetime

import operations_orders as ops


def delete_order(con, order_id, *, note="Видалено користувачем"):
    """Remove an order and its internal links in one caller transaction.

    Does not delete employee/vehicle records or exported DOCX/PDF/JPG files.
    Save a complete snapshot in operations_change_log before removal.
    """
    ops.ensure_schema_on_connection(con)
    row = ops.get_order(con, order_id)
    if row is None:
        raise ValueError("Наказ не знайдено.")
    oid = int(order_id)
    assignments = [dict(r) for r in con.execute(
        "SELECT * FROM vehicle_driver_assignments WHERE order_id=? ORDER BY id",
        (oid,),
    ).fetchall()]
    entities = [dict(r) for r in con.execute(
        "SELECT * FROM operations_order_entities WHERE order_id=? ORDER BY id",
        (oid,),
    ).fetchall()]
    before = {
        "order": dict(row),
        "assignments": assignments,
        "entities": entities,
    }
    # Assignment endings may refer either to rows owned by the removed order
    # or to rows ended by the removed order. Remove those relations as well.
    con.execute(
        "DELETE FROM vehicle_driver_assignment_endings WHERE ended_by_order_id=?",
        (oid,),
    ) if con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' "
        "AND name='vehicle_driver_assignment_endings'"
    ).fetchone() else None
    if assignments:
        marks = ",".join("?" for _ in assignments)
        ids = [row["id"] for row in assignments]
        if con.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' "
            "AND name='vehicle_driver_assignment_endings'"
        ).fetchone():
            con.execute(
                "DELETE FROM vehicle_driver_assignment_endings "
                "WHERE assignment_id IN (" + marks + ")", ids
            )
    con.execute("DELETE FROM vehicle_driver_assignments WHERE order_id=?", (oid,))
    con.execute("DELETE FROM operations_order_entities WHERE order_id=?", (oid,))
    con.execute("DELETE FROM operations_orders WHERE id=?", (oid,))
    ops._write_history(
        con, "order", oid, "delete",
        before=before, after={},
        note=str(note or "Видалено користувачем"),
    )
    return before

