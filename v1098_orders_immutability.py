# -*- coding: utf-8 -*-
"""Taxo 10.9-r8: immutable approved/signed orders and safe assignments.

The layer is additive: historical 10.7 order code stays untouched.  It adds an
operational termination fact for superseded driver assignments instead of
rewriting rows that belong to an already approved order.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

import operations_orders as ops

FEATURE_VERSION = "10.9-r8"
_UNSET = object()

_ORIGINAL_ACTIVE_ASSIGNMENTS = ops.active_driver_assignments


def ensure_schema_on_connection(con):
    ops.ensure_schema_on_connection(con)
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS vehicle_driver_assignment_endings (
            assignment_id INTEGER PRIMARY KEY
                REFERENCES vehicle_driver_assignments(id) ON DELETE CASCADE,
            ended_by_order_id INTEGER NOT NULL
                REFERENCES operations_orders(id) ON DELETE RESTRICT,
            effective_until TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_assignment_endings_order
            ON vehicle_driver_assignment_endings(ended_by_order_id,assignment_id);
        """
    )


def _row(con, order_id):
    ensure_schema_on_connection(con)
    return con.execute("SELECT * FROM operations_orders WHERE id=?", (int(order_id),)).fetchone()


def _order_locked(row):
    if row is None:
        return False
    return str(row["status"] or "") == ops.ORDER_APPROVED or bool(int(row["paper_original_signed"] or 0))


def _require_order_mutable(con, order_id):
    row = _row(con, order_id)
    if row is None:
        raise ValueError("Наказ не знайдено.")
    if _order_locked(row):
        raise ValueError("Затверджений або підписаний наказ незмінний. Оформіть новий наказ про зміну.")
    if str(row["status"] or "") == ops.ORDER_CANCELLED:
        raise ValueError("Скасований наказ незмінний. Оформіть новий наказ.")
    return row


def update_order(con, order_id, *, order_type=_UNSET, order_no=_UNSET, order_date=_UNSET,
                 place=_UNSET, subject=_UNSET, preamble=_UNSET, body_text=_UNSET,
                 control_employee_id=_UNSET, note=_UNSET, history_note=""):
    """Update draft order while preserving omitted control_employee_id.

    Explicit ``control_employee_id=None`` still means the user intentionally
    clears the field; merely omitting it preserves the existing controller.
    """
    row = _require_order_mutable(con, order_id)
    before = dict(row)
    new_type = str(row["order_type"] if order_type is _UNSET else order_type)
    if new_type not in ops.ORDER_TYPE_LABELS:
        raise ValueError("Невідомий тип наказу.")
    number = str(row["order_no"] if order_no is _UNSET else order_no or "").strip()
    if not number:
        raise ValueError("Вкажіть номер наказу.")
    day = ops._day(row["order_date"] if order_date is _UNSET else order_date)
    controller = row["control_employee_id"] if control_employee_id is _UNSET else control_employee_id
    values = (
        new_type, number, day,
        str(row["place"] if place is _UNSET else place or "").strip(),
        str(row["subject"] if subject is _UNSET else subject or "").strip(),
        str(row["preamble"] if preamble is _UNSET else preamble or "").strip(),
        str(row["body_text"] if body_text is _UNSET else body_text or "").strip(),
        int(controller) if controller else None,
        str(row["note"] if note is _UNSET else note or "").strip(),
        datetime.now().isoformat(timespec="seconds"), int(order_id),
    )
    con.execute(
        """UPDATE operations_orders
              SET order_type=?,order_no=?,order_date=?,place=?,subject=?,preamble=?,body_text=?,
                  control_employee_id=?,note=?,updated_at=? WHERE id=?""",
        values,
    )
    after = dict(ops.get_order(con, order_id))
    if before != after:
        ops._write_history(con, "order", order_id, "update", before=before, after=after, note=history_note)
    return after


def set_paper_original_signed(con, order_id, signed=True, *, signed_at=None, history_note=""):
    row = _row(con, order_id)
    if row is None:
        raise ValueError("Наказ не знайдено.")
    if int(row["paper_original_signed"] or 0):
        if signed:
            return row
        raise ValueError("Позначку про підписаний паперовий оригінал не можна знімати. Оформіть новий наказ про зміну.")
    if str(row["status"] or "") == ops.ORDER_CANCELLED:
        raise ValueError("Скасований наказ не можна позначати як підписаний.")
    return ops.set_paper_original_signed(con, order_id, signed=signed, signed_at=signed_at, history_note=history_note)


def add_vehicle_assignment(con, order_id, vehicle_id, employee_id, *, valid_from,
                           valid_until="", sequence_no=None, note=""):
    _require_order_mutable(con, order_id)
    return ops.add_vehicle_assignment(
        con, order_id, vehicle_id, employee_id, valid_from=valid_from,
        valid_until=valid_until, sequence_no=sequence_no, note=note,
    )


def update_vehicle_assignment(con, assignment_id, **kwargs):
    ensure_schema_on_connection(con)
    row = ops.get_vehicle_assignment(con, assignment_id)
    if row is None:
        raise ValueError("Закріплення не знайдено.")
    _require_order_mutable(con, row["order_id"])
    return ops.update_vehicle_assignment(con, assignment_id, **kwargs)


def delete_vehicle_assignment(con, assignment_id, *, history_note=""):
    ensure_schema_on_connection(con)
    row = ops.get_vehicle_assignment(con, assignment_id)
    if row is None:
        return
    _require_order_mutable(con, row["order_id"])
    return ops.delete_vehicle_assignment(con, assignment_id, history_note=history_note)


def _end_day(start_iso):
    return (date.fromisoformat(str(start_iso)[:10]) - timedelta(days=1)).isoformat()


def _overlap(start_a, end_a, start_b, end_b):
    a1 = date.fromisoformat(str(start_a)[:10])
    b1 = date.fromisoformat(str(start_b)[:10])
    a2 = date.max if not str(end_a or "").strip() else date.fromisoformat(str(end_a)[:10])
    b2 = date.max if not str(end_b or "").strip() else date.fromisoformat(str(end_b)[:10])
    return a1 <= b2 and b1 <= a2


def _effective_until(con, assignment_row):
    original = str(assignment_row["valid_until"] or "").strip()
    ending = con.execute(
        "SELECT effective_until FROM vehicle_driver_assignment_endings WHERE assignment_id=?",
        (int(assignment_row["id"]),),
    ).fetchone()
    extra = str(ending["effective_until"] or "").strip() if ending else ""
    values = [value for value in (original, extra) if value]
    return min(values) if values else ""


def _prepare_assignment_supersession(con, order_id):
    """Validate new assignment order and end one unambiguous prior assignment.

    Conflicts inside the new order or already-corrupt simultaneous prior driver
    assignments are rejected rather than silently guessed.
    """
    new_rows = list(ops.order_assignments(con, order_id))
    for index, left in enumerate(new_rows):
        for right in new_rows[index + 1:]:
            if int(left["employee_id"]) == int(right["employee_id"]) and int(left["vehicle_id"]) != int(right["vehicle_id"]):
                if _overlap(left["valid_from"], left["valid_until"], right["valid_from"], right["valid_until"]):
                    raise ValueError("Один водій не може бути одночасно закріплений за різними ТЗ у межах одного наказу.")

    for new in new_rows:
        start = str(new["valid_from"])
        prior = con.execute(
            """SELECT a.* FROM vehicle_driver_assignments a
                 JOIN operations_orders o ON o.id=a.order_id
                WHERE a.employee_id=? AND a.order_id<>? AND o.status=?
                  AND a.valid_from<=?
                ORDER BY a.valid_from DESC,a.id DESC""",
            (int(new["employee_id"]), int(order_id), ops.ORDER_APPROVED, start),
        ).fetchall()
        overlapping = [row for row in prior if _overlap(row["valid_from"], _effective_until(con, row), start, new["valid_until"])]
        if len(overlapping) > 1:
            raise ValueError("Виявлено кілька одночасних чинних закріплень цього водія. Спершу усуньте конфлікт історичних даних.")
        if len(overlapping) == 1:
            old = overlapping[0]
            until = _end_day(start)
            if until < str(old["valid_from"]):
                raise ValueError("Нове закріплення конфліктує з майбутнім затвердженим закріпленням водія.")
            con.execute(
                """INSERT INTO vehicle_driver_assignment_endings(
                       assignment_id,ended_by_order_id,effective_until,created_at
                   ) VALUES(?,?,?,?)
                   ON CONFLICT(assignment_id) DO UPDATE SET
                       ended_by_order_id=excluded.ended_by_order_id,
                       effective_until=MIN(vehicle_driver_assignment_endings.effective_until,excluded.effective_until),
                       created_at=excluded.created_at""",
                (int(old["id"]), int(order_id), until, datetime.now().isoformat(timespec="seconds")),
            )
            ops._write_history(
                con, "assignment", int(old["id"]), "superseded",
                before=dict(old),
                after={"effective_until": until, "ended_by_order_id": int(order_id)},
                note="Попереднє закріплення припинено новим затвердженим наказом без переписування старого наказу.",
            )


def approve_order(con, order_id):
    ensure_schema_on_connection(con)
    row = _row(con, order_id)
    if row is None:
        raise ValueError("Наказ не знайдено.")
    status = str(row["status"] or "")
    if status == ops.ORDER_CANCELLED:
        raise ValueError("Скасований наказ не можна повторно затвердити. Оформіть новий наказ.")
    if status == ops.ORDER_APPROVED:
        return row
    if row["order_type"] == ops.TYPE_VEHICLE_ASSIGNMENT:
        if not ops.order_assignments(con, order_id):
            raise ValueError("До наказу про закріплення не додано жодного ТЗ/водія.")
        _prepare_assignment_supersession(con, order_id)
    before = dict(row)
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        "UPDATE operations_orders SET status=?,approved_at=?,updated_at=? WHERE id=?",
        (ops.ORDER_APPROVED, now, now, int(order_id)),
    )
    after = dict(ops.get_order(con, order_id))
    ops._write_history(con, "order", order_id, "approve", before=before, after=after)
    return after


def cancel_order(con, order_id):
    ensure_schema_on_connection(con)
    row = _row(con, order_id)
    if row is None:
        raise ValueError("Наказ не знайдено.")
    if str(row["status"] or "") == ops.ORDER_CANCELLED:
        return row
    before = dict(row)
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        "UPDATE operations_orders SET status=?,cancelled_at=?,updated_at=? WHERE id=?",
        (ops.ORDER_CANCELLED, now, now, int(order_id)),
    )
    after = dict(ops.get_order(con, order_id))
    ops._write_history(con, "order", order_id, "cancel", before=before, after=after)
    return after


def active_driver_assignments(con, vehicle_id, on_date=None):
    ensure_schema_on_connection(con)
    day = ops._day(on_date or date.today())
    rows = list(_ORIGINAL_ACTIVE_ASSIGNMENTS(con, vehicle_id, day))
    return [row for row in rows if not _effective_until(con, row) or _effective_until(con, row) >= day]


def install(core, App):
    # Patch the shared domain module used by operations_orders_ui.py.
    for name, func in (
        ("ensure_schema_on_connection", ensure_schema_on_connection),
        ("update_order", update_order),
        ("set_paper_original_signed", set_paper_original_signed),
        ("add_vehicle_assignment", add_vehicle_assignment),
        ("update_vehicle_assignment", update_vehicle_assignment),
        ("delete_vehicle_assignment", delete_vehicle_assignment),
        ("approve_order", approve_order),
        ("cancel_order", cancel_order),
        ("active_driver_assignments", active_driver_assignments),
    ):
        setattr(ops, name, func)
        if hasattr(core, name):
            setattr(core, name, func)

    class App1098(App):
        pass

    core.APP_VERSION = FEATURE_VERSION
    return App1098
