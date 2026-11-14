# -*- coding: utf-8 -*-
"""Pure codecs for CompanyTemplates fact-entry controls.

The UI stores plain strings and stable registry snapshots. This module converts
those control values into the typed fact contract consumed by
company_template_draft. It has no Tk, database, filesystem or document writes.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Iterable, List, Sequence

from company_template_fact_choices import FactChoice


def parse_text(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Очікується текст")
    return value.replace("\r\n", "\n").replace("\r", "\n")


def parse_date(value: object) -> date:
    """Accept ISO or familiar Ukrainian DD.MM.YYYY input."""
    text = str(value or "").strip()
    if not text:
        raise ValueError("Вкажіть дату")
    for pattern in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            pass
    raise ValueError("Дата має бути у форматі ДД.ММ.РРРР або YYYY-MM-DD")


def parse_integer(value: object) -> int:
    text = str(value or "").strip()
    if not text:
        raise ValueError("Вкажіть ціле число")
    try:
        number = int(text)
    except ValueError:
        raise ValueError("Вкажіть ціле число")
    if str(number) != text and text not in ("+%d" % number, "-%d" % abs(number)):
        # Avoid silently accepting decimal-looking or mixed values.
        if not (text.startswith("+") and text[1:].isdigit()):
            raise ValueError("Вкажіть ціле число")
    return number


def parse_sections(value: object):
    """Split a long-form control into sections separated by blank lines."""
    text = parse_text(value).strip()
    if not text:
        return []
    result = []
    buffer = []
    for line in text.split("\n"):
        if line.strip():
            buffer.append(line)
        elif buffer:
            result.append("\n".join(buffer).strip())
            buffer = []
    if buffer:
        result.append("\n".join(buffer).strip())
    return result


def parse_table_rows(value: object):
    """Parse one row per line and tab-separated cells.

    Tabs are explicit so commas, semicolons and ordinary prose remain literal.
    """
    text = parse_text(value).strip()
    if not text:
        return []
    rows = []
    for number, line in enumerate(text.split("\n"), 1):
        if not line.strip():
            continue
        cells = [cell.strip() for cell in line.split("\t")]
        if not cells or all(not cell for cell in cells):
            raise ValueError("Порожній рядок таблиці №%d" % number)
        rows.append(cells)
    return rows


def choice_snapshot(choice: FactChoice):
    if not isinstance(choice, FactChoice):
        raise ValueError("Не вибрано запис довідника")
    return dict(choice.snapshot)


def selected_snapshots(
    rows: Sequence[FactChoice], indexes: Iterable[int]
) -> List[dict]:
    result = []
    seen = set()
    for raw in indexes:
        index = int(raw)
        if index < 0 or index >= len(rows):
            raise ValueError("Некоректний вибір у довіднику")
        item = rows[index]
        key = (item.entity_type, item.entity_id)
        if key in seen:
            continue
        seen.add(key)
        result.append(choice_snapshot(item))
    return result


def pair_snapshot(driver: FactChoice, vehicle: FactChoice) -> dict:
    if driver.entity_type not in ("employee", "driver", "person"):
        raise ValueError("Для пари вибрано некоректного водія")
    if vehicle.entity_type != "vehicle":
        raise ValueError("Для пари вибрано некоректний транспортний засіб")
    return {
        "person": choice_snapshot(driver),
        "vehicle": choice_snapshot(vehicle),
    }


def add_unique_pair(existing, driver: FactChoice, vehicle: FactChoice):
    """Append one stable pair, rejecting only the exact duplicate."""
    pair = pair_snapshot(driver, vehicle)
    key = (pair["person"]["id"], pair["vehicle"]["id"])
    for item in existing:
        old = (
            item.get("person", {}).get("id"),
            item.get("vehicle", {}).get("id"),
        )
        if old == key:
            raise ValueError("Ця пара водій–ТЗ вже додана")
    return list(existing) + [pair]
