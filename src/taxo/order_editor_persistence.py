# -*- coding: utf-8 -*-
"""Persistence boundary for the operations order editor.

The Tk editor owns field widgets, selection state, and user prompts. This
service owns database writes and verification of driver/vehicle pairs. The
caller controls the transaction and must roll back on any exception.
"""
from __future__ import annotations


def save_order(
    operations,
    connection,
    *,
    existing,
    order_type,
    order_series,
    order_no,
    order_date,
    place,
    subject,
    preamble,
    body_text,
    control_employee_id,
    initial_pairs,
):
    """Persist an order and return its ID without committing the transaction.

    Vehicle-assignment creation checks the exact set of requested pairs before
    the caller commits. A partial write must never be reported as a success.
    """
    values = dict(
        order_type=order_type,
        order_no=order_no,
        order_date=order_date,
        place=place,
        subject=subject,
        preamble=preamble,
        body_text=body_text,
        control_employee_id=control_employee_id,
    )

    if existing is not None:
        operations.update_order(
            connection,
            existing["id"],
            history_note="Редагування через інтерфейс",
            **values
        )
        return int(existing["id"])

    if order_type == operations.TYPE_VEHICLE_ASSIGNMENT:
        order_id = operations.create_vehicle_assignment_order(
            connection,
            initial_pairs=initial_pairs,
            order_series=order_series,
            **{key: value for key, value in values.items() if key != "order_type"}
        )
        if initial_pairs:
            stored_count = operations.verify_vehicle_assignment_pairs(
                connection, order_id, initial_pairs
            )
            expected_count = len(
                {(int(vehicle_id), int(driver_id))
                 for vehicle_id, driver_id in initial_pairs}
            )
            if stored_count != expected_count:
                raise RuntimeError(
                    "Taxo не підтвердив повний запис пар у новому наказі: "
                    "очікувалось %d, у наказі %d."
                    % (expected_count, stored_count)
                )
        return order_id

    return operations.create_order(
        connection, order_series=order_series, **values
    )
