# -*- coding: utf-8 -*-
"""Taxo 10.5-r6 — editable working data derived from state registries.

Official imported snapshots remain immutable audit/provenance records.  This module
edits only the local Taxo working fields that are used for documents and reports.
A later registry reconciliation can therefore still show any difference between the
latest official snapshot and the locally corrected/expanded working copy.
"""
from __future__ import annotations

from datetime import datetime

import personnel_registry as personnel
import personnel_registry_lossless as personnel_lossless
import vehicle_reconciliation as vehicle_reconciliation
import vehicle_registry

APP_VERSION = "10.5-r6"

PERSONAL_FIELDS = tuple(personnel.EMPLOYEE_FIELD_LABELS.keys())
MILITARY_FIELDS = (
    "registry_person_id",
    "account_type",
    "account_status",
    "reservist_status",
    "booking_status",
    "booking_until",
    "deferment_reason",
    "deferment_until",
    "military_rank",
    "military_specialty",
    "account_authority",
    "military_service_status",
    "reserve_category",
    "military_document",
    "education_specialty",
    "foreign_passport",
    "fitness",
    "family_info",
    "appointment_act",
    "notification_requisites",
    "registry_note",
)
VEHICLE_FIELDS = tuple(vehicle_registry.FIELD_LABELS.keys())


def _text(value):
    return str(value or "").strip()


def _row_dict(row):
    if row is None:
        return {}
    return {key: row[key] for key in row.keys()}


def ensure_personnel_schema(con):
    # r4 adds registry_note and raw snapshot storage on top of the base schema.
    personnel_lossless.ensure_schema_on_connection(con)


def employee_working_data(con, employee_id):
    ensure_personnel_schema(con)
    employee, military = personnel.employee_profile(con, int(employee_id))
    if employee is None:
        raise ValueError("Картку працівника не знайдено.")
    emp = _row_dict(employee)
    mil = _row_dict(military)
    personal_values = {field: _text(emp.get(field, "")) for field in PERSONAL_FIELDS}
    military_values = {field: _text(mil.get(field, "")) for field in MILITARY_FIELDS}
    return {
        "employee_id": int(employee_id),
        "name": " ".join(
            value for value in (
                _text(emp.get("last_name")),
                _text(emp.get("first_name")),
                _text(emp.get("middle_name")),
            ) if value
        ),
        "personal": personal_values,
        "military": military_values,
        "last_source_kind": _text(mil.get("last_source_kind")),
        "last_source_name": _text(mil.get("last_source_name")),
        "last_verified_at": _text(mil.get("last_verified_at")),
    }


def save_employee_working_data(con, employee_id, *, personal_values=None, military_values=None):
    """Save local working values without rewriting the imported raw snapshot."""
    ensure_personnel_schema(con)
    employee_id = int(employee_id)
    if con.execute("SELECT 1 FROM employees WHERE id=?", (employee_id,)).fetchone() is None:
        raise ValueError("Картку працівника не знайдено.")

    personal_values = dict(personal_values or {})
    military_values = dict(military_values or {})
    invalid_personal = set(personal_values) - set(PERSONAL_FIELDS)
    invalid_military = set(military_values) - set(MILITARY_FIELDS)
    if invalid_personal or invalid_military:
        raise ValueError("Спроба змінити поле, яке не належить до робочих даних реєстру.")

    if personal_values:
        fields = list(personal_values)
        con.execute(
            "UPDATE employees SET " + ", ".join(field + "=?" for field in fields) + " WHERE id=?",
            [_text(personal_values[field]) for field in fields] + [employee_id],
        )

    con.execute("INSERT OR IGNORE INTO employee_military_profile(employee_id) VALUES(?)", (employee_id,))
    if military_values:
        fields = list(military_values)
        con.execute(
            "UPDATE employee_military_profile SET "
            + ", ".join(field + "=?" for field in fields)
            + ", updated_at=? WHERE employee_id=?",
            [_text(military_values[field]) for field in fields]
            + [datetime.now().isoformat(timespec="seconds"), employee_id],
        )
    else:
        con.execute(
            "UPDATE employee_military_profile SET updated_at=? WHERE employee_id=?",
            (datetime.now().isoformat(timespec="seconds"), employee_id),
        )


def employee_copy_text(con, employee_id):
    data = employee_working_data(con, employee_id)
    lines = [data["name"] or "Працівник"]
    for field in PERSONAL_FIELDS:
        value = data["personal"].get(field, "")
        if value:
            lines.append("%s: %s" % (personnel.EMPLOYEE_FIELD_LABELS.get(field, field), value))
    for field in MILITARY_FIELDS:
        value = data["military"].get(field, "")
        if value:
            lines.append("%s: %s" % (personnel.MILITARY_FIELD_LABELS.get(field, field), value))
    return "\n".join(lines)


def ensure_vehicle_schema(con):
    vehicle_reconciliation.ensure_schema_on_connection(con)


def vehicle_working_data(con, vehicle_id):
    ensure_vehicle_schema(con)
    vehicle_id = int(vehicle_id)
    vehicle = con.execute("SELECT * FROM vehicles WHERE id=?", (vehicle_id,)).fetchone()
    if vehicle is None:
        raise ValueError("Картку транспортного засобу не знайдено.")
    local = _row_dict(vehicle)
    current = {
        row["field_name"]: row
        for row in vehicle_reconciliation.current_fields(con, vehicle_id=vehicle_id)
    }
    fields = []
    for field in VEHICLE_FIELDS:
        state_row = current.get(field)
        fields.append({
            "field": field,
            "label": vehicle_registry.FIELD_LABELS.get(field, field),
            "working_value": _text(local.get(field, "")),
            "registry_value": _text(state_row["registry_value"]) if state_row is not None else "",
            "state": _text(state_row["state"]) if state_row is not None else "",
            "decision": _text(state_row["decision"]) if state_row is not None else "",
            "source_name": _text(state_row["source_name"]) if state_row is not None else _text(local.get("registry_last_source_name", "")),
        })
    return {
        "vehicle_id": vehicle_id,
        "name": _text(local.get("name")),
        "plate": _text(local.get("plate")),
        "last_source_name": _text(local.get("registry_last_source_name")),
        "last_verified_at": _text(local.get("registry_last_verified_at")),
        "fields": fields,
    }


def _normalize_vehicle_value(field, value):
    value = _text(value)
    if field == "plate":
        return value.upper()
    if field == "vin":
        return vehicle_registry.normalize_vin(value)
    if field == "gross_mass_kg":
        return vehicle_registry._number_text(value)
    if field == "ecmt_valid_from" and value:
        return vehicle_registry._iso_date(value)
    return value


def save_vehicle_working_value(con, vehicle_id, field, value):
    """Edit one local working field and refresh its comparison to the last snapshot."""
    ensure_vehicle_schema(con)
    vehicle_id = int(vehicle_id)
    if field not in VEHICLE_FIELDS:
        raise ValueError("Поле ТЗ не дозволене для редагування у робочих даних.")
    if con.execute("SELECT 1 FROM vehicles WHERE id=?", (vehicle_id,)).fetchone() is None:
        raise ValueError("Картку транспортного засобу не знайдено.")
    value = _normalize_vehicle_value(field, value)
    con.execute("UPDATE vehicles SET %s=? WHERE id=?" % field, (value, vehicle_id))

    state_row = con.execute(
        "SELECT * FROM vehicle_registry_field_state WHERE vehicle_id=? AND field_name=?",
        (vehicle_id, field),
    ).fetchone()
    if state_row is not None:
        now = datetime.now().isoformat(timespec="seconds")
        incoming = _text(state_row["registry_value"])
        state = vehicle_reconciliation.field_state(field, value, incoming)
        vehicle_reconciliation._upsert_current_state(
            con,
            {
                "vehicle_id": vehicle_id,
                "field": field,
                "local": value,
                "registry": incoming,
                "state": state,
                "source_kind": _text(state_row["source_kind"]),
                "source_name": _text(state_row["source_name"]),
                "file_sha256": _text(state_row["file_sha256"]),
                "source_row": state_row["source_row"],
            },
            now,
        )
    return value


def vehicle_copy_text(con, vehicle_id):
    data = vehicle_working_data(con, vehicle_id)
    lines = [data["plate"] or data["name"] or "Транспортний засіб"]
    for row in data["fields"]:
        if row["working_value"]:
            lines.append("%s: %s" % (row["label"], row["working_value"]))
    return "\n".join(lines)
