# -*- coding: utf-8 -*-
"""Preparation rules and supplementary lists for safety briefings."""
from datetime import date, datetime
import csv
from pathlib import Path


BRIEFING_KINDS = {
    "БДР": (
        "Вступний",
        "Первинний",
        "Передрейсовий (цільовий)",
        "Періодичний (повторний)",
        "Позаплановий (спеціальний)",
    ),
    "Охорона праці": (
        "Вступний",
        "Первинний",
        "Повторний",
        "Позаплановий",
        "Цільовий",
    ),
}

PREPARATION_NOTICE = (
    "ПІДГОТОВЧИЙ МАТЕРІАЛ. НЕ Є ЖУРНАЛОМ ІНСТРУКТАЖІВ І НЕ ПІДТВЕРДЖУЄ ЙОГО ПРОВЕДЕННЯ. "
    "Паперові записи та особисті підписи оформлює відповідальна особа."
)


def quarter_for(day=None):
    day = day or date.today()
    return (day.year, (day.month - 1) // 3 + 1)


def shift_quarter(year, quarter, delta):
    index = int(year) * 4 + int(quarter) - 1 + int(delta)
    if index < 0:
        raise ValueError("Некоректний квартал")
    return divmod(index, 4)[0], divmod(index, 4)[1] + 1


def quarter_caption(year, quarter):
    if int(quarter) not in (1, 2, 3, 4):
        raise ValueError("Квартал має бути від 1 до 4")
    return "%d квартал %d року" % (int(quarter), int(year))


def prepare_list(
    direction,
    kind,
    day_text,
    topic,
    people,
    reason="",
    people_records=None,
    program_text="",
    template_id="",
    source_note="",
):
    direction = str(direction or "").strip()
    if direction not in BRIEFING_KINDS:
        raise ValueError("Виберіть напрям інструктажу")
    kind = str(kind or "").strip()
    if kind not in BRIEFING_KINDS[direction]:
        raise ValueError("Виберіть вид інструктажу")
    try:
        parsed_date = datetime.strptime(str(day_text).strip(), "%d.%m.%Y").date()
    except (ValueError, TypeError):
        raise ValueError("Дата має бути у форматі ДД.ММ.РРРР")
    topic = str(topic or "").strip()
    if not topic:
        raise ValueError("Вкажіть тему або назву затвердженої програми")
    reason = str(reason or "").strip()
    if kind.startswith("Позаплановий") and not reason:
        raise ValueError("Для позапланового інструктажу потрібна підстава")
    names = tuple(dict.fromkeys(str(person).strip() for person in people if str(person).strip()))
    if not names:
        raise ValueError("Виберіть хоча б одного працівника")

    records = []
    seen_ids = set()
    for record in people_records or ():
        if not isinstance(record, dict):
            continue
        try:
            employee_id = int(record.get("id"))
        except (TypeError, ValueError):
            continue
        if employee_id in seen_ids:
            continue
        seen_ids.add(employee_id)
        records.append({
            "id": employee_id,
            "name": str(record.get("name") or record.get("label") or "").strip(),
            "personnel_no": str(record.get("personnel_no") or "").strip(),
        })

    return {
        "direction": direction,
        "kind": kind,
        "day": parsed_date,
        "topic": topic,
        "reason": reason,
        "program_text": str(program_text or "").strip(),
        "template_id": str(template_id or "").strip(),
        "source_note": str(source_note or "").strip(),
        "people": names,
        "people_records": tuple(records),
    }


def preparation_filename(prepared):
    kind = prepared["kind"].split(" ", 1)[0].lower().replace("(", "")
    return "Список_інструктажу_%s_%s_%s_%d-осіб.csv" % (
        "БДР" if prepared["direction"] == "БДР" else "ОП",
        kind,
        prepared["day"].isoformat(),
        len(prepared["people"]),
    )


def write_preparation_csv(path, prepared):
    """Create a new supplementary CSV; never overwrite another preparation."""
    target = Path(path)
    with target.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream, delimiter=";")
        writer.writerow([PREPARATION_NOTICE])
        writer.writerow(["Напрям", prepared["direction"]])
        writer.writerow(["Вид", prepared["kind"]])
        writer.writerow(["Дата", prepared["day"].strftime("%d.%m.%Y")])
        writer.writerow(["Тема / програма", prepared["topic"]])
        writer.writerow(["Підстава", prepared["reason"]])
        writer.writerow(["Шаблон", prepared.get("template_id", "")])
        writer.writerow(["Нормативний орієнтир", prepared.get("source_note", "")])
        writer.writerow(["Зміст програми", prepared.get("program_text", "")])
        writer.writerow([])
        records = tuple(prepared.get("people_records") or ())
        if records:
            writer.writerow(["№", "Працівник", "Табельний №", "Код Taxo"])
            for number, record in enumerate(records, 1):
                writer.writerow([
                    number,
                    record.get("name", ""),
                    record.get("personnel_no", ""),
                    record.get("id", ""),
                ])
        else:
            writer.writerow(["№", "Працівник"])
            for number, name in enumerate(prepared["people"], 1):
                writer.writerow([number, name])
    return target


