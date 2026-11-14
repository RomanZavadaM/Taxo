# -*- coding: utf-8 -*-
"""Read-only registry choices for CompanyTemplates fact-entry UI.

The adapter deliberately reuses Taxo's existing entity_choices contract. It
opens a fresh main-database connection through ApplicationServices, reads stable
ID-aware employee/driver/vehicle rows, converts them to plain snapshots, and
closes the connection. No schema migration, insert, update or document creation
belongs here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import entity_choices


@dataclass(frozen=True)
class FactChoice:
    """One stable registry option shown in a template fact form."""

    entity_type: str
    entity_id: int
    label: str
    snapshot: Dict[str, object]


@dataclass(frozen=True)
class FactChoiceCatalog:
    """Read-only choice pools for one fact-entry window."""

    employees: Tuple[FactChoice, ...]
    drivers: Tuple[FactChoice, ...]
    vehicles: Tuple[FactChoice, ...]


def _choice(row) -> FactChoice:
    if not isinstance(row, dict):
        raise ValueError("Некоректний запис довідника")
    identity = row.get("id")
    label = str(row.get("label") or "").strip()
    entity_type = str(row.get("entity_type") or "").strip()
    if type(identity) is not int or identity < 1 or not label or not entity_type:
        raise ValueError("Запис довідника не має стабільної ідентичності")
    snapshot = entity_choices.choice_snapshot(row)
    if not snapshot:
        raise ValueError("Не вдалося підготувати snapshot запису довідника")
    return FactChoice(
        entity_type=entity_type,
        entity_id=identity,
        label=label,
        snapshot=snapshot,
    )


def _unique(rows) -> Tuple[FactChoice, ...]:
    seen = set()
    result = []
    for row in rows:
        item = _choice(row)
        key = (item.entity_type, item.entity_id)
        if key in seen:
            raise ValueError("Довідник містить дубльований стабільний ID")
        seen.add(key)
        result.append(item)
    return tuple(result)


def load_fact_choice_catalog(services) -> FactChoiceCatalog:
    """Read current active registry choices without modifying business data."""
    con = services.workspace.connect_main_db()
    try:
        employees = entity_choices.list_employee_choices(con, active_only=True)
        drivers = entity_choices.list_driver_choices(con, active_only=True)
        vehicles = entity_choices.list_vehicle_choices(con, active_only=True)
    finally:
        con.close()

    return FactChoiceCatalog(
        employees=_unique(employees),
        drivers=_unique(drivers),
        vehicles=_unique(vehicles),
    )


def by_label(rows: Tuple[FactChoice, ...]) -> Dict[str, FactChoice]:
    """Map labels to choices; entity_choices already disambiguates duplicates."""
    result = {}
    for item in rows:
        if item.label in result:
            raise ValueError("Довідник містить неоднозначні підписи")
        result[item.label] = item
    return result
