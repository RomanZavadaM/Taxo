# -*- coding: utf-8 -*-
"""Taxo 10.1-r3 — модуль «Персонал», режими й табелі.

Модуль:
- додає окремий верхній розділ «Персонал»;
- залишає стару вкладку водіїв як «Водії»;
- додає загальне масове планування робочих змін для будь-якого працівника;
- додає масове внесення відсутностей/відпусток у табель;
- надає PDF/XLSX типової форми № П-5; план замість відсутнього факту підставляється лише після явного підтвердження користувача;
- не видаляє історичні графіки при внесенні відсутності.
"""
from __future__ import annotations

import calendar
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path

from work_regime import (
    REGIME_FIVE_DAY,
    REGIME_SIX_DAY,
    REGIME_SUMMARIZED,
    REGIME_CUSTOM,
    REGIME_LABELS,
    REGIME_BY_LABEL,
    PERIOD_LABELS,
    PERIOD_BY_LABEL,
    PERIOD_WEEK,
    PRESETS,
    WEEKDAY_LABELS as REGIME_WEEKDAY_LABELS,
    accounting_period_bounds,
    day_norm_minutes,
    ensure_schema as ensure_work_regime_schema,
    hhmm as regime_hhmm,
    latest_regime,
    parse_hhmm as regime_parse_hhmm,
    regime_for_date,
    save_regime,
    validate_regime,
    week_start as regime_week_start,
)

from v91_features import (
    PATTERN_DAILY,
    PATTERN_WEEKDAYS,
    PATTERN_SELECTED,
    PATTERN_ALTERNATE,
    PATTERN_2_2,
    PATTERN_7_7,
    PATTERN_CUSTOM,
    PATTERNS,
    WEEKDAY_NAMES,
    parse_clock,
    shift_span_minutes,
    pattern_dates,
    widget_alive,
)


APP_VERSION = "10.1-r3"
WINDOW_TITLE = f"Taxo {APP_VERSION} — персонал, водії, графіки та шляхівки"

ABSENCE_RANGE_PLANNED = "Лише дні з робочим планом"
ABSENCE_RANGE_WEEKDAYS = "Пн–Пт"
ABSENCE_RANGE_ALL = "Усі календарні дні"

# Типи, які в ручному табелі мають пріоритет над автоматичним робочим планом.
# Старі значення «Відпустка»/«Лікарняний» лишаються сумісними.
ABSENCE_TYPES = (
    "Основна щорічна відпустка",
    "Щорічна додаткова відпустка",
    "Додаткова відпустка постраждалим внаслідок Чорнобильської катастрофи",
    "Додаткова оплачувана відпустка працівникам з дітьми",
    "Творча відпустка",
    "Додаткова відпустка у зв’язку з навчанням",
    "Відпустка без збереження зарплати у зв’язку з навчанням",
    "Відпустка без збереження зарплати в обов’язковому порядку",
    "Відпустка без збереження зарплати за згодою сторін",
    "Інші відпустки без збереження зарплати",
    "Неявки у зв’язку з переведенням за ініціативою роботодавця на неповний робочий день (тиждень)",
    "Неявки у зв’язку з тимчасовим переведенням на роботу на інше підприємство",
    "Відпустка у зв’язку з вагітністю і пологами / догляд до 3 років",
    "Відпустка для догляду за дитиною до 6 років",
    "Оплачувана тимчасова непрацездатність",
    "Неоплачувана тимчасова непрацездатність",
    "Відрядження",
    "Простій",
    "Прогул",
    "Страйк",
    "Інший невідпрацьований час",
    "Інші види неявок за колективними договорами",
    "Неявка з нез’ясованих причин",
    "Інша причина неявки",
)

P5_CODES = {
    "Робота": ("Р", "01", "Години роботи, передбачені колективним договором"),
    "Неповний робочий день": ("РС", "02", "Години роботи при неповному робочому дні (тижні) згідно із законодавством"),
    "Відрядження": ("ВД", "07", "Відрядження"),
    "Основна щорічна відпустка": ("В", "08", "Основна щорічна відпустка"),
    "Відпустка": ("В", "08", "Основна щорічна відпустка"),
    "Щорічна додаткова відпустка": ("Д", "09", "Щорічна додаткова відпустка"),
    "Додаткова відпустка постраждалим внаслідок Чорнобильської катастрофи": ("Ч", "10", "Додаткова відпустка, передбачена ст. 20, 21, 30 Закону України про статус і соціальний захист громадян, які постраждали внаслідок Чорнобильської катастрофи"),
    "Творча відпустка": ("ТВ", "11", "Творча відпустка"),
    "Додаткова відпустка у зв’язку з навчанням": ("Н", "12", "Додаткова відпустка у зв’язку з навчанням"),
    "Відпустка без збереження зарплати у зв’язку з навчанням": ("НБ", "13", "Відпустка без збереження зарплати у зв’язку з навчанням"),
    "Відпустка без збереження зарплати в обов’язковому порядку": ("ДБ", "14", "Додаткова відпустка без збереження зарплати в обов’язковому порядку"),
    "Додаткова оплачувана відпустка працівникам з дітьми": ("ДО", "15", "Додаткова оплачувана відпустка працівникам з дітьми"),
    "Відпустка у зв’язку з вагітністю і пологами / догляд до 3 років": ("ВП", "16", "Відпустка у зв’язку з вагітністю і пологами / догляд до 3 років"),
    "Відпустка для догляду за дитиною до 6 років": ("ДД", "17", "Відпустка для догляду за дитиною до 6 років"),
    "Відпустка без збереження зарплати за згодою сторін": ("НА", "18", "Відпустка без збереження зарплати за згодою сторін"),
    "Інші відпустки без збереження зарплати": ("БЗ", "19", "Інші відпустки без збереження зарплати"),
    "Неявки у зв’язку з переведенням за ініціативою роботодавця на неповний робочий день (тиждень)": ("НД", "20", "Неявки у зв’язку з переведенням за ініціативою роботодавця на неповний робочий день (тиждень)"),
    "Неявки у зв’язку з тимчасовим переведенням на роботу на інше підприємство": ("НП", "21", "Неявки у зв’язку з тимчасовим переведенням на роботу на інше підприємство"),
    "Інший невідпрацьований час": ("ІН", "22", "Інший невідпрацьований час"),
    "Простій": ("П", "23", "Простій"),
    "Прогул": ("ПР", "24", "Прогул"),
    "Страйк": ("С", "25", "Масові невиходи на роботу (страйки)"),
    "Оплачувана тимчасова непрацездатність": ("ТН", "26", "Оплачувана тимчасова непрацездатність"),
    "Лікарняний": ("ТН", "26", "Оплачувана тимчасова непрацездатність"),
    "Неоплачувана тимчасова непрацездатність": ("НН", "27", "Неоплачувана тимчасова непрацездатність"),
    "Неявка з нез’ясованих причин": ("НЗ", "28", "Неявка з нез’ясованих причин"),
    "Інші види неявок за колективними договорами": ("ІВ", "29", "Інші види неявок за колективними договорами"),
    "Інша причина неявки": ("І", "30", "Інші причини неявок"),
}

# Повна таблиця умовних позначень типової форми № П-5.
# Вона окрема від P5_CODES, бо не всі види робочого часу зараз є окремими
# типами дня у Taxo, але у друкованій формі легенда має бути повною.
P5_LEGEND = (
    ("Години роботи, передбачені колдоговором", "Р", "01"),
    ("Години роботи працівників, яким встановлено неповний робочий день (тиждень) згідно з законодавством", "РС", "02"),
    ("Вечірні години роботи", "ВЧ", "03"),
    ("Нічні години роботи", "РН", "04"),
    ("Надурочні години роботи", "НУ", "05"),
    ("Години роботи у вихідні та святкові дні", "РВ", "06"),
    ("Відрядження", "ВД", "07"),
    ("Основна щорічна відпустка", "В", "08"),
    ("Щорічна додаткова відпустка", "Д", "09"),
    ("Додаткова відпустка постраждалим внаслідок Чорнобильської катастрофи", "Ч", "10"),
    ("Творча відпустка", "ТВ", "11"),
    ("Додаткова відпустка у зв’язку з навчанням", "Н", "12"),
    ("Відпустка без збереження заробітної плати у зв’язку з навчанням", "НБ", "13"),
    ("Додаткова відпустка без збереження заробітної плати в обов’язковому порядку", "ДБ", "14"),
    ("Додаткова оплачувана відпустка працівникам, які мають дітей", "ДО", "15"),
    ("Відпустка у зв’язку з вагітністю і пологами / догляд за дитиною до 3 років", "ВП", "16"),
    ("Відпустка для догляду за дитиною до досягнення нею 6-річного віку", "ДД", "17"),
    ("Відпустка без збереження заробітної плати за згодою сторін", "НА", "18"),
    ("Інші відпустки без збереження заробітної плати (на період припинення виконання робіт)", "БЗ", "19"),
    ("Неявки у зв’язку з переведенням за ініціативою роботодавця на неповний робочий день (тиждень)", "НД", "20"),
    ("Неявки у зв’язку з тимчасовим переведенням на роботу на інше підприємство", "НП", "21"),
    ("Інший невідпрацьований час, передбачений законодавством", "ІН", "22"),
    ("Простої", "П", "23"),
    ("Прогули", "ПР", "24"),
    ("Масові невиходи на роботу (страйки)", "С", "25"),
    ("Оплачувана тимчасова непрацездатність", "ТН", "26"),
    ("Неоплачувана тимчасова непрацездатність", "НН", "27"),
    ("Неявки з нез’ясованих причин", "НЗ", "28"),
    ("Інші види неявок, передбачені колективними договорами, угодами", "ІВ", "29"),
    ("Інші причини неявок", "І", "30"),
)

NONWORK_OVERRIDE_TYPES = (set(ABSENCE_TYPES) - {"Відрядження"}) | {"Відпустка", "Лікарняний", "Вихідний", "Відпочинок"}

# Групи підсумкових колонок праворуч, як у наданому зразку П-5.
P5_ABSENCE_GROUPS = (
    ("8-10", {"08", "09", "10"}),
    ("11-15,17,22", {"11", "12", "13", "14", "15", "17", "22"}),
    ("18", {"18"}),
    ("19", {"19"}),
    ("20", {"20"}),
    ("21", {"21"}),
    ("23", {"23"}),
    ("24", {"24"}),
    ("25", {"25"}),
    ("26-27", {"26", "27"}),
    ("28-30", {"28", "29", "30"}),
)


def p5_code(day_type: str):
    return P5_CODES.get(str(day_type or "").strip(), ("", "", ""))


def _safe_hours_to_minutes(core, value):
    if value is None:
        return None
    return core.hours_value_to_minutes(value)


def _employee_label(row):
    full = " ".join(str(row[k] or "").strip() for k in ("last_name", "first_name", "middle_name") if str(row[k] or "").strip())
    personnel = str(row["personnel_no"] or "").strip()
    position = str(row["position"] or "").strip()
    prefix = f"{personnel} | " if personnel else ""
    suffix = f" — {position}" if position else ""
    return prefix + full + suffix


def _all_employee_rows(core, active_only=False):
    con = core.db()
    sql = """SELECT e.*,GROUP_CONCAT(er.role, ', ') roles
             FROM employees e
             LEFT JOIN employee_roles er ON er.employee_id=e.id"""
    if active_only:
        sql += " WHERE e.active=1"
    sql += " GROUP BY e.id ORDER BY e.active DESC,e.last_name,e.first_name,e.middle_name"
    rows = con.execute(sql).fetchall()
    con.close()
    return rows


def _employee_role_choices(row):
    roles = []
    raw = str(row["roles"] or "") if "roles" in row.keys() else ""
    for item in raw.split(","):
        item = item.strip()
        if item and item not in roles:
            roles.append(item)
    position = str(row["position"] or "").strip()
    if position and position not in roles:
        roles.append(position)
    if not roles:
        roles.append("Працівник")
    return roles


def _canonical_segment_intervals(core, segments, pair="work"):
    """Compatibility wrapper for canonical interval normalization.

    Production Taxo exposes normalized_segment_intervals from main.py. Tests,
    older embedding adapters, and lightweight cores may not; keep the same
    algorithm locally instead of requiring every caller to implement it.
    """
    fn=getattr(core,"normalized_segment_intervals",None)
    if callable(fn):
        return fn(segments,pair)

    out=[]
    previous_start=None
    for index,row in enumerate(segments or []):
        keys=set(row.keys()) if hasattr(row,"keys") else set()
        if pair=="drive":
            start_text=(row["start_time"] if "start_time" in keys else "") or ""
            end_text=(row["end_time"] if "end_time" in keys else "") or ""
        else:
            start_text=(row["work_start_time"] if "work_start_time" in keys else "") or ""
            end_text=(row["work_end_time"] if "work_end_time" in keys else "") or ""
            if not start_text:
                start_text=(row["start_time"] if "start_time" in keys else "") or ""
            if not end_text:
                end_text=(row["end_time"] if "end_time" in keys else "") or ""
        start_text=str(start_text).strip(); end_text=str(end_text).strip()
        if not start_text or not end_text:
            continue
        start=parse_clock(start_text)
        while previous_start is not None and start<previous_start:
            start+=1440
        end=parse_clock(end_text)+(start//1440)*1440
        while end<=start:
            end+=1440
        out.append({
            "index":index,"start":start,"end":end,
            "start_text":start_text,"end_text":end_text,
        })
        previous_start=start
    return out


def _canonical_segments_union_minutes(core, segments, pair="work"):
    fn=getattr(core,"segments_union_minutes",None)
    if callable(fn):
        return int(fn(segments,pair) or 0)
    intervals=_canonical_segment_intervals(core,segments,pair)
    if not intervals:
        return 0
    merged=[]
    for item in intervals:
        start=item["start"]; end=item["end"]
        if not merged or start>merged[-1][1]:
            merged.append([start,end])
        else:
            merged[-1][1]=max(merged[-1][1],end)
    return sum(end-start for start,end in merged)


def linked_route_plan_minutes(core, con, driver_id, target_date):
    """Fallback for old/incomplete driver-day rows linked to a route.

    Normal current records already carry copied work_segments/work_hours.  If
    those fields are empty but worklog.route_id exists, use the route's own
    exact work scenario so personnel/P-5 does not lose planned hours.
    """
    if not driver_id:
        return 0
    row = con.execute(
        """SELECT route_id,work_hours,work_start_time,work_end_time
             FROM worklog
            WHERE driver_id=? AND work_date=?""",
        (driver_id, target_date.isoformat()),
    ).fetchone()
    if row is None or not row["route_id"]:
        return 0
    segs = con.execute(
        """SELECT * FROM route_segments
            WHERE route_id=?
            ORDER BY segment_no""",
        (row["route_id"],),
    ).fetchall()
    if segs:
        exact = _canonical_segments_union_minutes(core,segs,"work")
        if exact > 0:
            return int(exact)

    # No exact route scenario available: only then fall back to the stored
    # aggregate duration. Never prefer a legacy aggregate over exact intervals.
    stored = core.hours_value_to_minutes(row["work_hours"] or 0)
    if stored > 0:
        return stored
    return int(sum(
        core.hours_value_to_minutes(seg["work_hours"] or 0) for seg in segs
    ))


def _interval_datetimes(day, start_text, end_text):
    start_text = str(start_text or "").strip()
    end_text = str(end_text or "").strip()
    if not start_text or not end_text:
        return None
    start_dt = datetime.combine(day, datetime.min.time()) + timedelta(
        minutes=parse_clock(start_text)
    )
    end_dt = datetime.combine(day, datetime.min.time()) + timedelta(
        minutes=parse_clock(end_text)
    )
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)
    return start_dt, end_dt


def driver_work_intervals(core, con, driver_id, around_date):
    """Known driver work intervals around a date, without inventing clock time.

    Exact work_segments/route_segments are normalized with the same canonical
    interval algorithm as the driver tab and schedule. Overlaps remain visible
    as overlaps; a clock rollback means next day only when the next segment
    start itself rolls back.
    """
    if not driver_id:
        return [], []
    rows = con.execute(
        """SELECT * FROM worklog
            WHERE driver_id=? AND work_date BETWEEN ? AND ?
            ORDER BY work_date,id""",
        (
            driver_id,
            (around_date - timedelta(days=1)).isoformat(),
            (around_date + timedelta(days=1)).isoformat(),
        ),
    ).fetchall()
    intervals=[]
    unresolved=[]

    def span_minutes(span):
        return int((span[1]-span[0]).total_seconds()//60)

    def normalized_maps(items):
        work_map={x["index"]:x for x in _canonical_segment_intervals(core,items,"work")}
        drive_map={x["index"]:x for x in _canonical_segment_intervals(core,items,"drive")}
        return work_map,drive_map

    def dt_span(base,item):
        origin=datetime.combine(base,datetime.min.time())
        return (
            origin+timedelta(minutes=item["start"]),
            origin+timedelta(minutes=item["end"]),
        )

    def union_minutes(spans):
        if not spans:
            return 0
        ordered=sorted(spans,key=lambda x:x[0])
        merged=[]
        for s,e in ordered:
            if not merged or s>merged[-1][1]:
                merged.append([s,e])
            else:
                merged[-1][1]=max(merged[-1][1],e)
        return sum(int((e-s).total_seconds()//60) for s,e in merged)

    for row in rows:
        base=date.fromisoformat(row["work_date"])
        row_keys=set(row.keys()) if hasattr(row,"keys") else set()
        planned_total=core.hours_value_to_minutes(
            row["work_hours"] if "work_hours" in row_keys else 0
        )

        segs=con.execute(
            """SELECT * FROM work_segments
                WHERE worklog_id=? ORDER BY segment_no""",
            (row["id"],),
        ).fetchall()

        if segs:
            work_map,drive_map=normalized_maps(segs)
            local_exact=[]
            fallback_busy=[]
            unresolved_part=False
            for idx,seg in enumerate(segs):
                seg_keys=set(seg.keys()) if hasattr(seg,"keys") else set()
                expected=core.hours_value_to_minutes(
                    seg["work_hours"] if "work_hours" in seg_keys else 0
                )
                if idx in work_map:
                    span=dt_span(base,work_map[idx])
                    intervals.append((span[0],span[1],row,seg))
                    local_exact.append(span)
                    continue
                if idx in drive_map:
                    span=dt_span(base,drive_map[idx])
                    intervals.append((span[0],span[1],row,seg))
                    fallback_busy.append(span)
                    if expected>span_minutes(span):
                        unresolved_part=True
                elif expected>0:
                    unresolved_part=True

            exact_expected=core.segments_union_minutes(segs,"work")
            known=union_minutes(local_exact)
            if exact_expected>known:
                unresolved_part=True
            # If exact work is unavailable, retain the legacy aggregate only as
            # evidence that some unplaced work exists.
            if exact_expected<=0 and planned_total>union_minutes(fallback_busy):
                unresolved_part=True
            if unresolved_part:
                unresolved.append(base)
            continue

        wstart=(row["work_start_time"] if "work_start_time" in row_keys else "") or ""
        wend=(row["work_end_time"] if "work_end_time" in row_keys else "") or ""
        span=_interval_datetimes(base,wstart,wend)
        if span:
            intervals.append((span[0],span[1],row,None))
            if planned_total>span_minutes(span):
                unresolved.append(base)
            continue

        route_id=row["route_id"] if "route_id" in row_keys else None
        if route_id:
            route_segs=con.execute(
                """SELECT * FROM route_segments
                    WHERE route_id=? ORDER BY segment_no""",
                (route_id,),
            ).fetchall()
            if route_segs:
                work_map,drive_map=normalized_maps(route_segs)
                local_exact=[]
                fallback_busy=[]
                unresolved_part=False
                for idx,seg in enumerate(route_segs):
                    seg_keys=set(seg.keys()) if hasattr(seg,"keys") else set()
                    expected=core.hours_value_to_minutes(
                        seg["work_hours"] if "work_hours" in seg_keys else 0
                    )
                    if idx in work_map:
                        span=dt_span(base,work_map[idx])
                        intervals.append((span[0],span[1],row,seg))
                        local_exact.append(span)
                    elif idx in drive_map:
                        span=dt_span(base,drive_map[idx])
                        intervals.append((span[0],span[1],row,seg))
                        fallback_busy.append(span)
                        if expected>span_minutes(span):
                            unresolved_part=True
                    elif expected>0:
                        unresolved_part=True

                exact_expected=_canonical_segments_union_minutes(core,route_segs,"work")
                if exact_expected>union_minutes(local_exact):
                    unresolved_part=True
                if exact_expected<=0 and planned_total>union_minutes(fallback_busy):
                    unresolved_part=True
                if unresolved_part:
                    unresolved.append(base)
                if local_exact or fallback_busy:
                    continue

        dstart=(row["start_time"] if "start_time" in row_keys else "") or ""
        dend=(row["end_time"] if "end_time" in row_keys else "") or ""
        span=_interval_datetimes(base,dstart,dend)
        if span:
            intervals.append((span[0],span[1],row,None))
            if planned_total>span_minutes(span):
                unresolved.append(base)
            continue

        if planned_total>0:
            unresolved.append(base)

    unresolved=list(dict.fromkeys(unresolved))
    return intervals,unresolved

def _is_driver_role(value):
    text = str(value or "").strip().lower()
    return text == "водій" or text.startswith("водій ") or "водій автотранспорт" in text


def driver_plan_conflict(core, con, employee, start_dt, end_dt):
    """Check another-role shift against the employee's driver schedule.

    Non-overlapping internal concurrent work is allowed.  If driver work has
    positive duration but no exact clock boundaries, Taxo must not invent a
    time-of-day. Such a day is advisory only: planning is allowed with a warning.
    """
    driver_id = employee["driver_id"]
    if not driver_id:
        return None
    intervals, unresolved = driver_work_intervals(
        core, con, driver_id, start_dt.date()
    )
    for work_start, work_end, row, _seg in intervals:
        if start_dt < work_end and work_start < end_dt:
            return {
                "kind": "overlap",
                "date": row["work_date"],
                "start": work_start,
                "end": work_end,
                "route": (row["route_name"] if "route_name" in row.keys() else "") or "",
            }
    if unresolved:
        return {
            "kind": "unknown_time",
            "date": unresolved[0].isoformat(),
            "start": None,
            "end": None,
            "route": "",
        }
    return None


def _legacy_absence_cell(day_type):
    code, numeric, _label = p5_code(day_type)
    if numeric in {"08","09","10","11","12","13","14","15","16","17","18","19"}:
        return "Відп"
    if numeric in {"26","27"}:
        return "Лік"
    if numeric == "23":
        return "Прст"
    if numeric == "24":
        return "Прог"
    if numeric == "25":
        return "Стр"
    if numeric in {"28","29","30"}:
        return "Неяв"
    return code or str(day_type or "")[:4]


def _employee_absence_adjustment_minutes(core, con, employee, work_date, regime, base_norm):
    entry = con.execute(
        "SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",
        (employee["id"], work_date.isoformat()),
    ).fetchone()
    if not entry or str(entry["day_type"] or "") not in NONWORK_OVERRIDE_TYPES:
        return 0

    # Fixed schedules: the legal/calendar norm of that workday is the amount
    # removed from the norm. For summarized accounting, prefer the approved
    # work schedule for that day because shifts may vary across the period.
    if regime.regime_type != REGIME_SUMMARIZED:
        return int(base_norm)

    driver_plan = core._driver_plan_minutes_for_day(
        con, employee["driver_id"], work_date
    )
    shift_plan, _shift_actual, _shift_found = core._employee_shift_minutes_for_day(
        con, employee["id"], work_date
    )
    scheduled = int(driver_plan + shift_plan)
    if scheduled <= 0 and employee["driver_id"]:
        scheduled = linked_route_plan_minutes(
            core, con, employee["driver_id"], work_date
        )
    return int(scheduled or base_norm)


def insert_regime_month_plan_if_empty(core, con, employee, work_date, norm_minutes, now=None):
    """Insert one regime-based monthly plan row only if the day is still empty.

    This is deliberately called immediately before the write, after UI preview/
    confirmation, so a route, personnel shift, or manual timesheet row created
    in the meantime is not overwritten or duplicated.
    """
    if isinstance(work_date, str):
        work_date = date.fromisoformat(work_date)
    norm_minutes = int(norm_minutes or 0)
    if norm_minutes <= 0:
        return False

    entry = con.execute(
        "SELECT id FROM employee_time_entries WHERE employee_id=? AND work_date=?",
        (employee["id"], work_date.isoformat()),
    ).fetchone()
    if entry:
        return False

    driver_plan = core._driver_plan_minutes_for_day(
        con, employee["driver_id"], work_date
    )
    shift_plan, _shift_actual, _shift_found = core._employee_shift_minutes_for_day(
        con, employee["id"], work_date
    )
    if int(driver_plan or 0) > 0 or int(shift_plan or 0) > 0:
        return False

    stamp = now or datetime.now().isoformat(timespec="seconds")
    cur = con.execute(
        """INSERT INTO employee_time_entries(
             employee_id,work_date,day_type,planned_hours,actual_hours,
             notes,created_at,updated_at
           ) VALUES(?,?,?, ?,NULL,?,?,?)
           ON CONFLICT(employee_id,work_date) DO NOTHING""",
        (
            employee["id"], work_date.isoformat(), "Робота",
            norm_minutes / 60.0, "План за режимом робочого часу",
            stamp, stamp,
        ),
    )
    return cur.rowcount > 0


def collect_personnel_week_balance(core, anchor_date, active_only=True):
    """Weekly personnel norm/plan/fact balance.

    For summarized accounting the weekly difference is informational only:
    overtime is determined at the end of the configured accounting period.
    """
    monday = regime_week_start(anchor_date)
    days = [monday + timedelta(days=i) for i in range(7)]
    con = core.db()
    sql = """SELECT e.*,GROUP_CONCAT(er.role, ', ') roles
             FROM employees e
             LEFT JOIN employee_roles er ON er.employee_id=e.id"""
    if active_only:
        sql += " WHERE e.active=1"
    sql += " GROUP BY e.id ORDER BY e.active DESC,e.last_name,e.first_name,e.middle_name"
    employees = con.execute(sql).fetchall()
    out = []
    for employee in employees:
        if not any(core.employee_employed_on(employee, d) for d in days):
            continue
        base_norm = adjusted_norm = absence_reduction = 0
        planned = actual = missing = 0
        regimes = []
        explicit = False
        summarized = False
        accounting_labels = set()
        for d in days:
            if not core.employee_employed_on(employee, d):
                continue
            norm, regime = day_norm_minutes(con, employee["id"], d)
            regimes.append(regime)
            explicit = explicit or regime.explicit
            summarized = summarized or regime.regime_type == REGIME_SUMMARIZED
            accounting_labels.add(regime.accounting_label)
            base_norm += int(norm)
            reduction = _employee_absence_adjustment_minutes(
                core, con, employee, d, regime, norm
            )
            absence_reduction += int(reduction)
            adjusted_norm += max(0, int(norm) - int(reduction))

            row = core.employee_day_time(con, employee["id"], d)
            planned += int(row["planned_minutes"] or 0)
            if row["actual_minutes"] is not None:
                actual += int(row["actual_minutes"] or 0)
            elif row["planned_minutes"] > 0:
                missing += 1

        current_regime = regimes[-1] if regimes else latest_regime(con, employee["id"])
        note_parts = []
        if not explicit:
            note_parts.append("режим не задано: типово 5/40")
        if summarized:
            note_parts.append(
                "підсумований облік: тижневий Δ довідковий; надурочні визначаються за обліковий період"
            )
        out.append({
            "employee_id": employee["id"],
            "personnel_no": employee["personnel_no"] or "",
            "name": core.employee_name(employee),
            "roles": employee["roles"] or employee["position"] or "",
            "regime": current_regime.label,
            "weekly_norm": current_regime.weekly_norm_minutes,
            "base_norm": base_norm,
            "absence_reduction": absence_reduction,
            "adjusted_norm": adjusted_norm,
            "planned": planned,
            "actual": actual,
            "difference": actual - adjusted_norm,
            "missing": missing,
            "summarized": summarized,
            "accounting_period": ", ".join(sorted(accounting_labels)),
            "note": "; ".join(note_parts),
        })
    con.close()
    return {"start": monday, "end": monday + timedelta(days=6), "days": days, "employees": out}


def _p5_entry_minutes(core, entry, key):
    if entry is None or not hasattr(entry, "keys") or key not in entry.keys():
        return 0
    value=entry[key]
    if value is None:
        return 0
    return int(core.hours_value_to_minutes(value) or 0)


def _p5_absence_minutes(core, con, employee, work_date, fallback_planned=0):
    """Scheduled hours lost to an absence, for the P-5 reason columns."""
    try:
        base_norm, regime=day_norm_minutes(con, employee["id"], work_date)
        value=_employee_absence_adjustment_minutes(
            core, con, employee, work_date, regime, base_norm
        )
        if value is not None:
            return int(value or 0)
    except Exception:
        pass
    return int(fallback_planned or 0)


def collect_p5_data(core, year, month, active_only=True, use_plan_when_fact_missing=False):
    """Collect factual data for the recommended standard form № P-5.

    Planned route/shift time is never silently promoted to fact. If the caller
    explicitly confirms use_plan_when_fact_missing=True, the planned value is
    used only for otherwise-missing factual work days and is visibly marked in
    the exported document.
    """
    y, m = int(year), int(month)
    days = core.month_dates(y, m)
    employees = _all_employee_rows(core, active_only=active_only)
    con = core.db()
    company = con.execute("SELECT * FROM company WHERE id=1").fetchone()
    out = []
    missing_fact_total=0
    planned_substituted_total=0
    missing_profile_fields=0

    for employee in employees:
        if not any(core.employee_employed_on(employee, d) for d in days):
            continue
        ekeys=set(employee.keys()) if hasattr(employee,"keys") else set()
        gender=(str(employee["gender"] or "").strip().lower() if "gender" in ekeys else "")
        tariff=employee["tariff_rate"] if "tariff_rate" in ekeys else None
        if not gender or tariff in (None,""):
            missing_profile_fields += 1

        cells = []
        work_days = 0
        work_minutes = 0
        missing_fact = 0
        planned_substituted = 0
        overtime_minutes = 0
        night_minutes = 0
        evening_minutes = 0
        holiday_minutes = 0
        total_absence_days=0
        total_absence_minutes=0
        absence_details = {
            label: {"days":0,"minutes":0} for label,_codes in P5_ABSENCE_GROUPS
        }

        for d in days:
            if not core.employee_employed_on(employee, d):
                cells.append({
                    "code":"","numeric":"","hours":None,"day_type":"—",
                    "missing":False,"planned_minutes":0,
                })
                continue

            row = core.employee_day_time(con, employee["id"], d)
            dtype = str(row["day_type"] or "")
            actual = row["actual_minutes"]
            planned = int(row["planned_minutes"] or 0)

            entry=con.execute(
                "SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",
                (employee["id"],d.isoformat())
            ).fetchone()
            entry_keys=set(entry.keys()) if entry is not None and hasattr(entry,"keys") else set()

            day_over=_p5_entry_minutes(core,entry,"overtime_hours")
            day_night=_p5_entry_minutes(core,entry,"night_hours")
            day_evening=_p5_entry_minutes(core,entry,"evening_hours")
            day_holiday=_p5_entry_minutes(core,entry,"weekend_holiday_hours")

            code, numeric, _label = p5_code(dtype)
            hours=None
            missing=False
            substituted_plan=False

            if dtype in NONWORK_OVERRIDE_TYPES:
                # An absence is itself factual when entered in the personnel
                # timesheet. Its cell carries the P-5 reason code; the reason
                # summary uses scheduled lost hours where that schedule is known.
                absence_minutes=_p5_absence_minutes(
                    core,con,employee,d,fallback_planned=planned
                )
                if numeric:
                    total_absence_days += 1
                    total_absence_minutes += max(0,absence_minutes)
                    for label,codes in P5_ABSENCE_GROUPS:
                        if numeric in codes:
                            absence_details[label]["days"] += 1
                            absence_details[label]["minutes"] += max(0,absence_minutes)
                            break
                # Any non-zero work fact on an absence day is a conflict that
                # must remain visible rather than being hidden by the code.
                if actual not in (None,0):
                    hours=int(actual)
                    missing=True
                    missing_fact += 1
            elif actual is not None:
                actual=int(actual or 0)
                if actual>0:
                    # Weekend/holiday work is only code 06 when explicitly
                    # classified as such; shift workers may normally work Sat/Sun.
                    if day_holiday>0:
                        code,numeric="РВ","06"
                    elif dtype=="Неповний робочий день":
                        code,numeric="РС","02"
                    elif dtype=="Відрядження":
                        code,numeric="ВД","07"
                    else:
                        code,numeric="Р","01"
                    hours=actual
                    work_days += 1
                    work_minutes += actual
                elif dtype not in ("Робота","Вихідний","Відпочинок",""):
                    # Preserve an explicitly entered factual code (e.g. business
                    # trip) even when no worked-hour quantity accompanies it.
                    code,numeric,_label=p5_code(dtype)
                else:
                    code=""
                    numeric=""
            elif planned>0:
                missing_fact += 1
                if use_plan_when_fact_missing:
                    if dtype=="Неповний робочий день":
                        code,numeric="РС","02"
                    elif dtype=="Відрядження":
                        code,numeric="ВД","07"
                    else:
                        code,numeric="Р","01"
                    hours=planned
                    work_days += 1
                    work_minutes += planned
                    substituted_plan=True
                    planned_substituted += 1
                else:
                    code=""
                    numeric=""
                    hours=None
                    missing=True
            else:
                # Ordinary empty/weekend day has no annual-leave code.
                if dtype in ("Вихідний","Відпочинок","Робота",""):
                    code=""; numeric=""
                else:
                    code,numeric,_label=p5_code(dtype)

            if actual is not None:
                overtime_minutes += day_over
                night_minutes += day_night
                evening_minutes += day_evening
                holiday_minutes += day_holiday

            cells.append({
                "code":code,
                "numeric":numeric,
                "hours":hours,
                "day_type":dtype,
                "missing":missing,
                "planned_minutes":planned,
                "substituted_plan":substituted_plan,
            })

        missing_fact_total += missing_fact
        planned_substituted_total += planned_substituted
        absence_counts={label:item["days"] for label,item in absence_details.items()}
        out.append({
            "employee_id": employee["id"],
            "personnel_no": employee["personnel_no"] or "",
            "name": core.employee_name(employee),
            "position": employee["position"] or employee["roles"] or "",
            "gender": gender,
            "cells": cells,
            "work_days": work_days,
            "work_minutes": work_minutes,
            "overtime_minutes": overtime_minutes,
            "night_minutes": night_minutes,
            "evening_minutes": evening_minutes,
            "holiday_minutes": holiday_minutes,
            "total_absence_days":total_absence_days,
            "total_absence_minutes":total_absence_minutes,
            "absence_details": absence_details,
            "absence_counts":absence_counts,  # backward-compatible API
            "missing_fact": missing_fact,
            "planned_substituted": planned_substituted,
            "tariff_rate": "" if tariff in (None,"") else tariff,
        })

    con.close()
    return {
        "year": y, "month": m, "days": days, "employees": out, "company": company,
        "missing_fact_total":missing_fact_total,
        "planned_substituted_total":planned_substituted_total,
        "missing_profile_fields":missing_profile_fields,
        "strict_fact_only":not bool(use_plan_when_fact_missing),
        "used_plan_for_missing_fact":bool(use_plan_when_fact_missing and planned_substituted_total),
        "form_reference":"Типова форма № П-5, наказ Держкомстату України 05.12.2008 № 489",
    }


def _report_font(core):
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    font = "Helvetica"
    font_path = next((p for p in core.report_font_candidates() if os.path.exists(p)), None)
    if font_path:
        try:
            if "TaxoP5Font" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("TaxoP5Font", font_path))
            if "TaxoP5FontBold" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("TaxoP5FontBold", font_path))
            font = "TaxoP5Font"
        except Exception:
            pass
    return font


def _p5_reason_caption(label):
    return {
        "8-10":"Основна та дод. відпустки",
        "11-15,17,22":"Навч., творчі, обов. та інші",
        "18":"Без з/п за згодою сторін",
        "19":"Без з/п на період припинення робіт",
        "20":"Неповний роб. день/тиждень",
        "21":"Тимчас. переведення",
        "23":"Простої",
        "24":"Прогули",
        "25":"Страйки",
        "26-27":"Тимчас. непрацездатність",
        "28-30":"Інші",
    }.get(label,label)


def _p5_hhmm(core, minutes):
    minutes=int(minutes or 0)
    return core.minutes_hhmm(minutes) if minutes else ""


def _p5_day_text(core, cell):
    if cell.get("missing"):
        return "*"
    code=str(cell.get("code") or "")
    hours=cell.get("hours")
    if hours is None:
        return code
    value=core.minutes_hhmm(int(hours))
    return f"{code}\n{value}" if code else value


def export_p5_pdf(core, year, month, out_path, active_only=True, form_date=None, department="", edrpou="", use_plan_when_fact_missing=False):
    """A4 landscape rendering preserving all indicators of standard form № P-5."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.pdfbase.pdfmetrics import stringWidth

    data=collect_p5_data(core,year,month,active_only,use_plan_when_fact_missing)
    page_w,page_h=landscape(A4)
    pdf=canvas.Canvas(str(out_path),pagesize=(page_w,page_h))
    font=_report_font(core)
    company=(data["company"]["name"] if data["company"] else "") or ""
    form_date=form_date or date.today()

    def txt(x,y,value,size=6,align="left"):
        pdf.setFont(font,size)
        value=str(value or "")
        if align=="center":
            pdf.drawCentredString(x,y,value)
        elif align=="right":
            pdf.drawRightString(x,y,value)
        else:
            pdf.drawString(x,y,value)

    def wrap(value,size,max_w):
        words=str(value or "").split()
        lines=[]; current=""
        for word in words:
            trial=(current+" "+word).strip()
            if not current or stringWidth(trial,font,size)<=max_w:
                current=trial
            else:
                lines.append(current); current=word
        if current:
            lines.append(current)
        return lines or [""]

    def header(title_suffix=""):
        txt(20,page_h-20,company,9)
        if department:
            txt(20,page_h-32,department,6)
        txt(20,page_h-44,f"Ідентифікаційний код ЄДРПОУ: {edrpou or ''}",6)
        txt(page_w-20,page_h-18,"Типова форма № П-5",6.5,"right")
        txt(page_w-20,page_h-29,"ЗАТВЕРДЖЕНО",5.5,"right")
        txt(page_w-20,page_h-40,"Наказ Держкомстату України 05.12.2008 № 489",5.3,"right")
        txt(page_w/2,page_h-57,"ТАБЕЛЬ ОБЛІКУ ВИКОРИСТАННЯ РОБОЧОГО ЧАСУ",11.5,"center")
        txt(page_w/2,page_h-69,f"{core.month_name_ua(data['month'])} {data['year']} року{title_suffix}",7,"center")
        txt(
            page_w-20,page_h-55,
            f"Дата заповнення: {form_date.strftime('%d.%m.%Y')}",
            5.5,"right"
        )
        txt(
            page_w-20,page_h-66,
            f"Звітний період: {data['days'][0].strftime('%d.%m.%Y')} – {data['days'][-1].strftime('%d.%m.%Y')}",
            5.2,"right"
        )

    # Page 1: official legend of 30 codes.
    header(" — умовні позначення")
    legend=[(label,letter,numeric) for label,letter,numeric in P5_LEGEND]
    gap=14
    margin=22
    col_w=(page_w-2*margin-gap)/2
    top=page_h-86
    half=(len(legend)+1)//2
    for col in range(2):
        y=top
        for label,letter,numeric in legend[col*half:(col+1)*half]:
            x=margin+col*(col_w+gap)
            lines=wrap(label,5.0,col_w-65)
            h=max(17,7+len(lines)*5.6)
            pdf.rect(x,y-h,col_w,h)
            pdf.line(x+col_w-64,y-h,x+col_w-64,y)
            pdf.line(x+col_w-31,y-h,x+col_w-31,y)
            for ii,line in enumerate(lines):
                txt(x+3,y-8-ii*5.6,line,5.0)
            txt(x+col_w-47,y-h/2-2,letter,6,"center")
            txt(x+col_w-15.5,y-h/2-2,numeric,6,"center")
            y-=h
    txt(
        margin,18,
        "П-5 є рекомендованою типовою формою; Taxo зберігає всі передбачені нею показники. "
        "Офіційний табель нижче використовує лише підтверджений фактичний час.",
        5.2
    )
    pdf.showPage()

    # Main form: 16 calendar slots, upper half 01–15 + X, lower half 16–31.
    employees=data["employees"]
    per_page=10
    chunks=[employees[i:i+per_page] for i in range(0,len(employees),per_page)] or [[]]

    fixed=[18,44,18,95]
    day_widths=[10.5]*16
    summary=[20,25,20,20,20,22]
    absence_total=[29]
    abs_widths=[19.3]*len(P5_ABSENCE_GROUPS)
    tariff=[34]
    widths=fixed+day_widths+summary+absence_total+abs_widths+tariff
    scale=min(1.0,(page_w-24)/sum(widths))
    widths=[w*scale for w in widths]

    for page_index,chunk in enumerate(chunks):
        header(f" — стор. {page_index+1}/{len(chunks)}")
        margin=12
        top_y=page_h-80
        header_h=70
        row_half=15
        row_h=row_half*2
        xs=[margin]
        for w in widths:
            xs.append(xs[-1]+w)
        bottom=top_y-header_h
        pdf.setLineWidth(.35)

        # Fixed headers.
        fixed_labels=["№","Таб. №","Стать","ПІБ, посада"]
        for idx,label in enumerate(fixed_labels):
            pdf.rect(xs[idx],bottom,widths[idx],header_h)
            txt(xs[idx]+widths[idx]/2,bottom+header_h/2-2,label,4.1,"center")

        day_start=4
        day_end=day_start+16
        pdf.rect(xs[day_start],bottom,sum(widths[day_start:day_end]),header_h)
        txt(
            xs[day_start]+sum(widths[day_start:day_end])/2,
            top_y-9,
            "Відмітки про явки та неявки за числами місяця (код / годин)",
            4.2,"center"
        )
        slot_y=bottom
        slot_h=header_h-18
        for slot in range(16):
            idx=day_start+slot
            if slot>0:
                pdf.line(xs[idx],bottom,xs[idx],top_y-18)
            upper=f"{slot+1:02d}" if slot<15 else "X"
            lower=f"{slot+16:02d}" if slot<16 else ""
            txt(xs[idx]+widths[idx]/2,bottom+31,upper,4.7,"center")
            txt(xs[idx]+widths[idx]/2,bottom+10,lower,4.7,"center")
        pdf.line(xs[day_start],bottom+slot_h/2,xs[day_end],bottom+slot_h/2)

        summary_start=day_end
        summary_end=summary_start+6
        pdf.rect(xs[summary_start],bottom,sum(widths[summary_start:summary_end]),header_h)
        txt(
            xs[summary_start]+sum(widths[summary_start:summary_end])/2,
            top_y-9,"Відпрацьовано за місяць",4.4,"center"
        )
        sum_labels=["днів","годин","надур.","нічних","вечірніх","вих./свят."]
        for off,label in enumerate(sum_labels):
            idx=summary_start+off
            if off>0:
                pdf.line(xs[idx],bottom,xs[idx],top_y-18)
            for ll,line in enumerate(wrap(label,3.7,widths[idx]-2)[:3]):
                txt(xs[idx]+widths[idx]/2,bottom+31-ll*5,line,3.7,"center")

        total_abs_idx=summary_end
        pdf.rect(xs[total_abs_idx],bottom,widths[total_abs_idx],header_h)
        for ll,line in enumerate(("Всього","неявок","дні/год.")):
            txt(xs[total_abs_idx]+widths[total_abs_idx]/2,bottom+43-ll*9,line,3.8,"center")

        abs_start=total_abs_idx+1
        abs_end=abs_start+len(P5_ABSENCE_GROUPS)
        pdf.rect(xs[abs_start],bottom,sum(widths[abs_start:abs_end]),header_h)
        txt(
            xs[abs_start]+sum(widths[abs_start:abs_end])/2,
            top_y-9,"З причин за місяць — дні / години",4.1,"center"
        )
        for off,(label,_codes) in enumerate(P5_ABSENCE_GROUPS):
            idx=abs_start+off
            if off>0:
                pdf.line(xs[idx],bottom,xs[idx],top_y-18)
            pdf.saveState()
            pdf.translate(xs[idx]+widths[idx]/2+1,bottom+3)
            pdf.rotate(90)
            pdf.setFont(font,3.2)
            pdf.drawString(0,0,f"{_p5_reason_caption(label)} [{label}]")
            pdf.restoreState()

        tariff_idx=abs_end
        pdf.rect(xs[tariff_idx],bottom,widths[tariff_idx],header_h)
        for ll,line in enumerate(("Оклад /","тарифна","ставка, грн")):
            txt(xs[tariff_idx]+widths[tariff_idx]/2,bottom+43-ll*9,line,3.8,"center")

        y=bottom
        chunk_totals={
            "work_days":0,"work_minutes":0,"overtime":0,"night":0,
            "evening":0,"holiday":0,"absence_days":0,"absence_minutes":0,
            "reasons":{label:{"days":0,"minutes":0} for label,_ in P5_ABSENCE_GROUPS},
        }

        for seq,emp in enumerate(chunk,start=page_index*per_page+1):
            y-=row_h
            # Fixed merged columns.
            fixed_values=[seq,emp["personnel_no"],emp["gender"],f"{emp['name']}\n{emp['position']}"]
            for idx,value in enumerate(fixed_values):
                pdf.rect(xs[idx],y,widths[idx],row_h)
                if idx==3:
                    parts=str(value).split("\n")
                    txt(xs[idx]+2,y+19,parts[0],4.4)
                    if len(parts)>1:
                        txt(xs[idx]+2,y+7,parts[1],3.8)
                else:
                    txt(xs[idx]+widths[idx]/2,y+row_h/2-2,value,4.4,"center")

            # Day slots: top 01–15; bottom 16–31.
            for slot in range(16):
                idx=day_start+slot
                pdf.rect(xs[idx],y,widths[idx],row_half)
                pdf.rect(xs[idx],y+row_half,widths[idx],row_half)
                day1=slot+1
                day2=slot+16
                for cell_y,day_no in ((y+row_half,day1),(y,day2)):
                    if day_no>len(emp["cells"]):
                        continue
                    cell=emp["cells"][day_no-1]
                    if cell.get("missing") or cell.get("substituted_plan"):
                        pdf.setFillColor(colors.HexColor("#FFF2CC" if cell.get("missing") else "#EAF2FF"))
                        pdf.rect(xs[idx],cell_y,widths[idx],row_half,fill=1,stroke=0)
                        pdf.setFillColor(colors.black)
                        pdf.rect(xs[idx],cell_y,widths[idx],row_half,fill=0,stroke=1)
                    value=_p5_day_text(core,cell)
                    parts=str(value).split("\n")
                    if len(parts)==1:
                        txt(xs[idx]+widths[idx]/2,cell_y+5,parts[0],3.8,"center")
                    else:
                        txt(xs[idx]+widths[idx]/2,cell_y+8,parts[0],3.6,"center")
                        txt(xs[idx]+widths[idx]/2,cell_y+2,parts[1],3.4,"center")

            # Worked summary.
            summary_values=[
                emp["work_days"],_p5_hhmm(core,emp["work_minutes"]),
                _p5_hhmm(core,emp["overtime_minutes"]),
                _p5_hhmm(core,emp["night_minutes"]),
                _p5_hhmm(core,emp["evening_minutes"]),
                _p5_hhmm(core,emp["holiday_minutes"]),
            ]
            for off,value in enumerate(summary_values):
                idx=summary_start+off
                pdf.rect(xs[idx],y,widths[idx],row_h)
                txt(xs[idx]+widths[idx]/2,y+row_h/2-2,value,4.0,"center")

            pdf.rect(xs[total_abs_idx],y,widths[total_abs_idx],row_h)
            absence_value=(
                f"{emp['total_absence_days']}/"
                f"{_p5_hhmm(core,emp['total_absence_minutes']) or '0:00'}"
                if emp["total_absence_days"] or emp["total_absence_minutes"] else ""
            )
            txt(xs[total_abs_idx]+widths[total_abs_idx]/2,y+row_h/2-2,absence_value,3.8,"center")

            for off,(label,_codes) in enumerate(P5_ABSENCE_GROUPS):
                idx=abs_start+off
                item=emp["absence_details"][label]
                value=(
                    f"{item['days']}/{_p5_hhmm(core,item['minutes']) or '0:00'}"
                    if item["days"] or item["minutes"] else ""
                )
                pdf.rect(xs[idx],y,widths[idx],row_h)
                txt(xs[idx]+widths[idx]/2,y+row_h/2-2,value,3.5,"center")

            pdf.rect(xs[tariff_idx],y,widths[tariff_idx],row_h)
            tariff_value=emp["tariff_rate"]
            if tariff_value not in ("",None):
                try:
                    tariff_value=f"{float(tariff_value):.2f}"
                except Exception:
                    pass
            txt(xs[tariff_idx]+widths[tariff_idx]/2,y+row_h/2-2,tariff_value,3.9,"center")

            chunk_totals["work_days"]+=emp["work_days"]
            chunk_totals["work_minutes"]+=emp["work_minutes"]
            chunk_totals["overtime"]+=emp["overtime_minutes"]
            chunk_totals["night"]+=emp["night_minutes"]
            chunk_totals["evening"]+=emp["evening_minutes"]
            chunk_totals["holiday"]+=emp["holiday_minutes"]
            chunk_totals["absence_days"]+=emp["total_absence_days"]
            chunk_totals["absence_minutes"]+=emp["total_absence_minutes"]
            for label,_codes in P5_ABSENCE_GROUPS:
                chunk_totals["reasons"][label]["days"]+=emp["absence_details"][label]["days"]
                chunk_totals["reasons"][label]["minutes"]+=emp["absence_details"][label]["minutes"]

        # Page total.
        y-=20
        pdf.rect(margin,y,sum(widths[:day_end]),20)
        txt(margin+3,y+7,"РАЗОМ НА СТОРІНЦІ",4.7)
        total_values=[
            chunk_totals["work_days"],_p5_hhmm(core,chunk_totals["work_minutes"]),
            _p5_hhmm(core,chunk_totals["overtime"]),_p5_hhmm(core,chunk_totals["night"]),
            _p5_hhmm(core,chunk_totals["evening"]),_p5_hhmm(core,chunk_totals["holiday"]),
        ]
        for off,value in enumerate(total_values):
            idx=summary_start+off
            pdf.rect(xs[idx],y,widths[idx],20)
            txt(xs[idx]+widths[idx]/2,y+7,value,3.8,"center")
        pdf.rect(xs[total_abs_idx],y,widths[total_abs_idx],20)
        abs_total=(
            f"{chunk_totals['absence_days']}/{_p5_hhmm(core,chunk_totals['absence_minutes']) or '0:00'}"
            if chunk_totals["absence_days"] or chunk_totals["absence_minutes"] else ""
        )
        txt(xs[total_abs_idx]+widths[total_abs_idx]/2,y+7,abs_total,3.5,"center")
        for off,(label,_codes) in enumerate(P5_ABSENCE_GROUPS):
            idx=abs_start+off
            item=chunk_totals["reasons"][label]
            value=(
                f"{item['days']}/{_p5_hhmm(core,item['minutes']) or '0:00'}"
                if item["days"] or item["minutes"] else ""
            )
            pdf.rect(xs[idx],y,widths[idx],20)
            txt(xs[idx]+widths[idx]/2,y+7,value,3.2,"center")
        pdf.rect(xs[tariff_idx],y,widths[tariff_idx],20)

        if page_index==len(chunks)-1:
            footer_y=max(18,y-62)
            if data["used_plan_for_missing_fact"]:
                txt(
                    margin,footer_y+50,
                    f"Примітка: за рішенням відповідальної особи у {data['planned_substituted_total']} дн. "
                    "планові години підставлено замість відсутнього факту (виділено блакитним).",
                    5.0
                )
            elif data["missing_fact_total"]:
                txt(
                    margin,footer_y+50,
                    f"* Увага: {data['missing_fact_total']} дн. мають план, але не мають підтвердженого факту; "
                    "у відпрацьовані години П-5 вони не включені.",
                    5.0
                )
            if data["missing_profile_fields"]:
                txt(
                    margin,footer_y+40,
                    f"Контроль реквізитів: у {data['missing_profile_fields']} працівн. не заповнено стать та/або оклад/ставку.",
                    4.8
                )

            sig_y=footer_y+24
            blocks=[
                ("Відповідальна особа",margin),
                ("Керівник структурного підрозділу",page_w/3+8),
                ("Працівник кадрової служби",2*page_w/3+4),
            ]
            for label,x in blocks:
                txt(x,sig_y,label,4.9)
                txt(x,sig_y-10,"посада ____________  підпис ____________  ПІБ __________________",4.1)
                txt(x,sig_y-20,'"___" __________ 20__ р.',4.1)

            txt(
                margin,10,
                "Примітка: для підсумованого обліку фонд часу визначається за встановленим обліковим періодом "
                "у межах нормальної тривалості. Форма має рекомендаційний характер і може доповнюватися показниками підприємства.",
                4.0
            )

        pdf.showPage()

    pdf.save()
    return data


def export_p5_xlsx(core, year, month, out_path, active_only=True, form_date=None, department="", edrpou="", use_plan_when_fact_missing=False):
    """Editable A4-landscape workbook preserving the standard P-5 indicators."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    data=collect_p5_data(core,year,month,active_only,use_plan_when_fact_missing)
    form_date=form_date or date.today()
    wb=Workbook()
    ws=wb.active
    ws.title="Табель П-5"
    legend_ws=wb.create_sheet("Умовні позначення")
    company=(data["company"]["name"] if data["company"] else "") or ""

    thin=Side(style="thin",color="555555")
    border=Border(left=thin,right=thin,top=thin,bottom=thin)
    header_fill=PatternFill("solid",fgColor="D9E6F2")
    missing_fill=PatternFill("solid",fgColor="FFF2CC")
    total_fill=PatternFill("solid",fgColor="EAF2F8")

    fixed_count=4
    day_start=5
    day_end=day_start+16-1
    summary_start=day_end+1
    total_abs_col=summary_start+6
    absence_start=total_abs_col+1
    tariff_col=absence_start+len(P5_ABSENCE_GROUPS)
    last_col=tariff_col

    # Header metadata.
    ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=last_col)
    ws["A1"]=company
    ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=last_col)
    ws["A2"]="ТАБЕЛЬ ОБЛІКУ ВИКОРИСТАННЯ РОБОЧОГО ЧАСУ"
    ws.merge_cells(start_row=3,start_column=1,end_row=3,end_column=last_col)
    ws["A3"]=(
        f"Типова форма № П-5; наказ Держкомстату України 05.12.2008 № 489    "
        f"Підрозділ: {department or '—'}    ЄДРПОУ: {edrpou or '—'}    "
        f"Дата заповнення: {form_date.strftime('%d.%m.%Y')}    "
        f"Звітний період: {data['days'][0].strftime('%d.%m.%Y')}–{data['days'][-1].strftime('%d.%m.%Y')}"
    )
    for rr in (1,2,3):
        ws.cell(rr,1).font=Font(bold=(rr<3),size=13 if rr==2 else 10 if rr==1 else 8)
        ws.cell(rr,1).alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)

    # Two-row header preserving the official 01–15/X and 16–31 structure.
    fixed_headers=["№","Табельний номер","Стать (ч/ж)","ПІБ, посада"]
    for col,label in enumerate(fixed_headers,1):
        ws.merge_cells(start_row=4,start_column=col,end_row=5,end_column=col)
        cell=ws.cell(4,col,label); cell.font=Font(bold=True,size=8); cell.fill=header_fill
        cell.border=border; cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)

    ws.merge_cells(start_row=4,start_column=day_start,end_row=4,end_column=day_end)
    ws.cell(4,day_start,"Відмітки про явки та неявки за числами місяця (код / годин)")
    for slot in range(16):
        col=day_start+slot
        upper=f"{slot+1:02d}" if slot<15 else "X"
        lower=f"{slot+16:02d}"
        cell=ws.cell(5,col,f"{upper}\n{lower}")
        cell.font=Font(bold=True,size=7); cell.fill=header_fill; cell.border=border
        cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)

    ws.merge_cells(start_row=4,start_column=summary_start,end_row=4,end_column=summary_start+5)
    ws.cell(4,summary_start,"Відпрацьовано за місяць")
    for off,label in enumerate(("днів","годин","надурочно","нічних","вечірніх","вих./свят.")):
        cell=ws.cell(5,summary_start+off,label)
        cell.font=Font(bold=True,size=7); cell.fill=header_fill; cell.border=border
        cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)

    ws.merge_cells(start_row=4,start_column=total_abs_col,end_row=5,end_column=total_abs_col)
    ws.cell(4,total_abs_col,"Всього неявок\nдні / години")

    ws.merge_cells(start_row=4,start_column=absence_start,end_row=4,end_column=absence_start+len(P5_ABSENCE_GROUPS)-1)
    ws.cell(4,absence_start,"З причин за місяць — дні / години")
    for off,(label,_codes) in enumerate(P5_ABSENCE_GROUPS):
        cell=ws.cell(5,absence_start+off,f"{_p5_reason_caption(label)}\n[{label}]")
        cell.font=Font(bold=True,size=6); cell.fill=header_fill; cell.border=border
        cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)

    ws.merge_cells(start_row=4,start_column=tariff_col,end_row=5,end_column=tariff_col)
    ws.cell(4,tariff_col,"Оклад / тарифна ставка, грн")

    for row in (4,5):
        for col in range(1,last_col+1):
            cell=ws.cell(row,col)
            cell.fill=header_fill
            cell.border=border
            cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
            if cell.font is None or not cell.font.bold:
                cell.font=Font(bold=True,size=7)

    row=6
    for seq,emp in enumerate(data["employees"],1):
        upper=row
        lower=row+1
        fixed_values=[seq,emp["personnel_no"],emp["gender"],f"{emp['name']}\n{emp['position']}"]
        for col,value in enumerate(fixed_values,1):
            ws.merge_cells(start_row=upper,start_column=col,end_row=lower,end_column=col)
            cell=ws.cell(upper,col,value)
            cell.border=border
            cell.alignment=Alignment(
                horizontal="left" if col==4 else "center",
                vertical="center",wrap_text=True
            )

        for slot in range(16):
            col=day_start+slot
            for target_row,day_no in ((upper,slot+1),(lower,slot+16)):
                cell=ws.cell(target_row,col)
                cell.border=border
                cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
                if day_no>len(emp["cells"]):
                    continue
                info=emp["cells"][day_no-1]
                cell.value=_p5_day_text(core,info)
                if info.get("missing"):
                    cell.fill=missing_fill
                elif info.get("substituted_plan"):
                    cell.fill=PatternFill("solid",fgColor="D9EAF7")

        summary_values=[
            emp["work_days"],emp["work_minutes"]/60.0 if emp["work_minutes"] else None,
            emp["overtime_minutes"]/60.0 if emp["overtime_minutes"] else None,
            emp["night_minutes"]/60.0 if emp["night_minutes"] else None,
            emp["evening_minutes"]/60.0 if emp["evening_minutes"] else None,
            emp["holiday_minutes"]/60.0 if emp["holiday_minutes"] else None,
        ]
        for off,value in enumerate(summary_values):
            col=summary_start+off
            ws.merge_cells(start_row=upper,start_column=col,end_row=lower,end_column=col)
            cell=ws.cell(upper,col,value); cell.border=border
            cell.alignment=Alignment(horizontal="center",vertical="center")

        ws.merge_cells(start_row=upper,start_column=total_abs_col,end_row=lower,end_column=total_abs_col)
        total_abs=(
            f"{emp['total_absence_days']} / {_p5_hhmm(core,emp['total_absence_minutes']) or '0:00'}"
            if emp["total_absence_days"] or emp["total_absence_minutes"] else ""
        )
        ws.cell(upper,total_abs_col,total_abs).border=border
        ws.cell(upper,total_abs_col).alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)

        for off,(label,_codes) in enumerate(P5_ABSENCE_GROUPS):
            col=absence_start+off
            item=emp["absence_details"][label]
            value=(
                f"{item['days']} / {_p5_hhmm(core,item['minutes']) or '0:00'}"
                if item["days"] or item["minutes"] else ""
            )
            ws.merge_cells(start_row=upper,start_column=col,end_row=lower,end_column=col)
            ws.cell(upper,col,value).border=border
            ws.cell(upper,col).alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)

        ws.merge_cells(start_row=upper,start_column=tariff_col,end_row=lower,end_column=tariff_col)
        ws.cell(upper,tariff_col,emp["tariff_rate"] if emp["tariff_rate"] not in ("",None) else "").border=border
        ws.cell(upper,tariff_col).alignment=Alignment(horizontal="center",vertical="center")
        row+=2

    # Overall totals.
    total_row=row
    ws.merge_cells(start_row=total_row,start_column=1,end_row=total_row,end_column=day_end)
    ws.cell(total_row,1,"РАЗОМ")
    totals={
        "work_days":sum(e["work_days"] for e in data["employees"]),
        "work_minutes":sum(e["work_minutes"] for e in data["employees"]),
        "overtime":sum(e["overtime_minutes"] for e in data["employees"]),
        "night":sum(e["night_minutes"] for e in data["employees"]),
        "evening":sum(e["evening_minutes"] for e in data["employees"]),
        "holiday":sum(e["holiday_minutes"] for e in data["employees"]),
        "absence_days":sum(e["total_absence_days"] for e in data["employees"]),
        "absence_minutes":sum(e["total_absence_minutes"] for e in data["employees"]),
    }
    vals=[
        totals["work_days"],totals["work_minutes"]/60.0 if totals["work_minutes"] else None,
        totals["overtime"]/60.0 if totals["overtime"] else None,
        totals["night"]/60.0 if totals["night"] else None,
        totals["evening"]/60.0 if totals["evening"] else None,
        totals["holiday"]/60.0 if totals["holiday"] else None,
    ]
    for off,value in enumerate(vals):
        ws.cell(total_row,summary_start+off,value)
    ws.cell(
        total_row,total_abs_col,
        f"{totals['absence_days']} / {_p5_hhmm(core,totals['absence_minutes']) or '0:00'}"
        if totals["absence_days"] or totals["absence_minutes"] else ""
    )
    for off,(label,_codes) in enumerate(P5_ABSENCE_GROUPS):
        days_total=sum(e["absence_details"][label]["days"] for e in data["employees"])
        min_total=sum(e["absence_details"][label]["minutes"] for e in data["employees"])
        ws.cell(
            total_row,absence_start+off,
            f"{days_total} / {_p5_hhmm(core,min_total) or '0:00'}"
            if days_total or min_total else ""
        )
    for col in range(1,last_col+1):
        cell=ws.cell(total_row,col); cell.border=border; cell.fill=total_fill
        cell.font=Font(bold=True,size=8); cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)

    info_row=total_row+2
    if data["used_plan_for_missing_fact"]:
        ws.merge_cells(start_row=info_row,start_column=1,end_row=info_row,end_column=last_col)
        ws.cell(info_row,1).value=(
            f"Примітка: за рішенням відповідальної особи у {data['planned_substituted_total']} дн. "
            "планові години підставлено замість відсутнього факту (блакитні клітинки)."
        )
        ws.cell(info_row,1).fill=PatternFill("solid",fgColor="D9EAF7")
        ws.cell(info_row,1).alignment=Alignment(wrap_text=True)
        info_row+=1
    elif data["missing_fact_total"]:
        ws.merge_cells(start_row=info_row,start_column=1,end_row=info_row,end_column=last_col)
        ws.cell(info_row,1).value=(
            f"* Увага: {data['missing_fact_total']} дн. мають план, але не мають підтвердженого факту; "
            "вони не включені до відпрацьованих годин П-5."
        )
        ws.cell(info_row,1).fill=missing_fill
        ws.cell(info_row,1).alignment=Alignment(wrap_text=True)
        info_row+=1
    if data["missing_profile_fields"]:
        ws.merge_cells(start_row=info_row,start_column=1,end_row=info_row,end_column=last_col)
        ws.cell(info_row,1).value=(
            f"Контроль реквізитів: у {data['missing_profile_fields']} працівн. "
            "не заповнено стать та/або оклад/тарифну ставку."
        )
        ws.cell(info_row,1).alignment=Alignment(wrap_text=True)
        info_row+=1

    # Signature blocks required by the standard form.
    sig_row=info_row+1
    spans=[
        (1,13,"Відповідальна особа"),
        (14,26,"Керівник структурного підрозділу"),
        (27,last_col,"Працівник кадрової служби"),
    ]
    for c1,c2,label in spans:
        ws.merge_cells(start_row=sig_row,start_column=c1,end_row=sig_row,end_column=c2)
        ws.cell(sig_row,c1,label).font=Font(bold=True,size=8)
        ws.merge_cells(start_row=sig_row+1,start_column=c1,end_row=sig_row+1,end_column=c2)
        ws.cell(sig_row+1,c1,"посада ____________   підпис ____________   ПІБ __________________")
        ws.merge_cells(start_row=sig_row+2,start_column=c1,end_row=sig_row+2,end_column=c2)
        ws.cell(sig_row+2,c1,'"___" __________ 20__ р.')

    note_row=sig_row+4
    ws.merge_cells(start_row=note_row,start_column=1,end_row=note_row+1,end_column=last_col)
    ws.cell(note_row,1).value=(
        "Примітка. Для підсумованого обліку фонд часу визначається за встановленим обліковим періодом "
        "у межах нормальної тривалості. Форма має рекомендаційний характер і може доповнюватися "
        "іншими показниками, необхідними підприємству."
    )
    ws.cell(note_row,1).alignment=Alignment(wrap_text=True,vertical="top")

    # Widths / printing.
    widths={
        1:5,2:12,3:7,4:28,
    }
    for col in range(day_start,day_end+1):
        widths[col]=4.6
    for col in range(summary_start,summary_start+6):
        widths[col]=7.5
    widths[total_abs_col]=9
    for col in range(absence_start,tariff_col):
        widths[col]=9.0
    widths[tariff_col]=11
    for col,width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width=width
    ws.row_dimensions[4].height=24
    ws.row_dimensions[5].height=42
    ws.freeze_panes="E6"
    ws.sheet_view.showGridLines=False
    ws.page_setup.orientation="landscape"
    ws.page_setup.paperSize=ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth=1
    ws.page_setup.fitToHeight=0
    ws.sheet_properties.pageSetUpPr.fitToPage=True
    ws.print_title_rows="1:5"
    ws.print_area=f"A1:{get_column_letter(last_col)}{note_row+1}"

    # Official legend sheet.
    legend_ws.merge_cells("A1:C1")
    legend_ws["A1"]=company
    legend_ws["A1"].font=Font(bold=True,size=11)
    legend_ws["A1"].alignment=Alignment(horizontal="center")
    legend_ws.merge_cells("A2:C2")
    legend_ws["A2"]="ТАБЕЛЬ ОБЛІКУ ВИКОРИСТАННЯ РОБОЧОГО ЧАСУ — УМОВНІ ПОЗНАЧЕННЯ П-5"
    legend_ws["A2"].font=Font(bold=True,size=12)
    legend_ws["A2"].alignment=Alignment(horizontal="center")
    legend_ws.merge_cells("A3:C3")
    legend_ws["A3"]=(
        f"Типова форма № П-5; наказ Держкомстату України 05.12.2008 № 489; "
        f"Дата заповнення: {form_date.strftime('%d.%m.%Y')}"
    )
    legend_ws["A3"].alignment=Alignment(horizontal="center",wrap_text=True)
    legend_ws.cell(6,1,"Умовне позначення")
    legend_ws.cell(6,2,"Буквений код")
    legend_ws.cell(6,3,"Цифровий код")
    for label,letter,numeric in P5_LEGEND:
        legend_ws.append([label,letter,numeric])
    for cells in legend_ws.iter_rows(min_row=6):
        for cell in cells:
            cell.border=border
            cell.alignment=Alignment(vertical="top",wrap_text=True)
    for cell in legend_ws[6]:
        cell.font=Font(bold=True); cell.fill=header_fill
    legend_ws.column_dimensions["A"].width=90
    legend_ws.column_dimensions["B"].width=16
    legend_ws.column_dimensions["C"].width=16
    legend_ws.page_setup.orientation="landscape"
    legend_ws.page_setup.paperSize=legend_ws.PAPERSIZE_A4
    legend_ws.page_setup.fitToWidth=1
    legend_ws.sheet_properties.pageSetUpPr.fitToPage=True

    wb.save(str(out_path))
    return data


def install(core, base_app):
    if getattr(core, "_TAXO_PERSONNEL_R3_INSTALLED", False):
        return core.App

    original_employee_day_time = core.employee_day_time
    original_collect_monthly_work_balance = core.collect_monthly_work_balance

    def collect_monthly_work_balance_with_absence(year, month, active_only=True):
        data = original_collect_monthly_work_balance(year, month, active_only)
        # r9: base collector already uses the canonical driver-day view and
        # applies personnel absence overlays. Do not subtract stored
        # work_hours a second time (they may differ from exact interval union).
        if data.get("absence_overlay_applied"):
            return data
        con = core.db()
        start = data["days"][0].isoformat()
        end = data["days"][-1].isoformat()
        links = con.execute(
            """SELECT id,driver_id FROM employees
                WHERE driver_id IS NOT NULL"""
        ).fetchall()
        employee_by_driver = {
            int(row["driver_id"]): int(row["id"]) for row in links
            if row["driver_id"] is not None
        }
        entries = con.execute(
            """SELECT * FROM employee_time_entries
                WHERE work_date BETWEEN ? AND ?""",
            (start, end),
        ).fetchall()
        entry_by = {(int(row["employee_id"]), row["work_date"]): row for row in entries}
        work_rows = con.execute(
            """SELECT * FROM worklog
                WHERE work_date BETWEEN ? AND ?""",
            (start, end),
        ).fetchall()
        work_by = {(int(row["driver_id"]), row["work_date"]): row for row in work_rows}
        con.close()

        for driver in data["drivers"]:
            employee_id = employee_by_driver.get(int(driver["driver_id"]))
            if not employee_id:
                continue
            for idx, day in enumerate(data["days"]):
                entry = entry_by.get((employee_id, day.isoformat()))
                if not entry or str(entry["day_type"] or "") not in NONWORK_OVERRIDE_TYPES:
                    continue
                driver["cells"][idx] = _legacy_absence_cell(entry["day_type"])
                work = work_by.get((int(driver["driver_id"]), day.isoformat()))
                if work is not None:
                    wm = core.hours_value_to_minutes(work["work_hours"])
                    om = core.hours_value_to_minutes(work["overtime_hours"])
                    driver["work_min"] = max(0, driver["work_min"] - wm)
                    driver["over_min"] = max(0, driver["over_min"] - om)
                    if wm > 0:
                        driver["work_days"] = max(0, driver["work_days"] - 1)
        return data

    core.collect_monthly_work_balance = collect_monthly_work_balance_with_absence

    def employee_day_time_with_absence(con, employee_id, target_date):
        if isinstance(target_date, str):
            target_date = date.fromisoformat(target_date)
        entry = con.execute(
            "SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",
            (employee_id, target_date.isoformat()),
        ).fetchone()
        if entry and str(entry["day_type"] or "") in NONWORK_OVERRIDE_TYPES:
            actual = (
                core.hours_value_to_minutes(entry["actual_hours"])
                if entry["actual_hours"] is not None else 0
            )
            return {
                "day_type": entry["day_type"],
                "planned_minutes": 0,
                "actual_minutes": actual,
                "source": "масова/ручна відсутність",
                "notes": entry["notes"] or "",
                "manual": True,
            }
        result = original_employee_day_time(con, employee_id, target_date)
        if int(result.get("planned_minutes") or 0) <= 0:
            employee = con.execute(
                "SELECT driver_id FROM employees WHERE id=?", (employee_id,)
            ).fetchone()
            driver_id = employee["driver_id"] if employee else None
            route_minutes = linked_route_plan_minutes(
                core, con, driver_id, target_date
            )
            if route_minutes > 0:
                result = dict(result)
                result["planned_minutes"] = route_minutes
                if str(result.get("day_type") or "") in ("", "Вихідний"):
                    result["day_type"] = "Робота"
                source = str(result.get("source") or "").strip()
                result["source"] = (
                    source + " + графік маршруту"
                    if source and source != "—"
                    else "графік маршруту"
                )
        return result

    core.employee_day_time = employee_day_time_with_absence
    core.TAXO_NONWORK_OVERRIDE_TYPES = set(NONWORK_OVERRIDE_TYPES)

    class PersonnelApp(base_app):
        def build_ui(self):
            super().build_ui()
            nb = self.main_notebook
            try:
                nb.tab(self.tab_drivers, text="Водії")
            except core.tk.TclError:
                pass
            self.tab_personnel = core.ttk.Frame(nb)
            nb.insert(1, self.tab_personnel, text="Персонал")
            self._build_personnel_section()

            # In the approved shell «Працівники» must open the personnel
            # registry, not the legacy driver-card list.
            nav_buttons=getattr(self,"_nav_buttons",{})
            driver_key=str(self.tab_drivers)
            personnel_button=nav_buttons.pop(driver_key,None)
            if personnel_button is not None:
                personnel_button.configure(
                    command=lambda:self.show_tab(self.tab_personnel)
                )
                nav_buttons[str(self.tab_personnel)]=personnel_button

            # Numeric tab indexes became unstable after adding «Персонал».
            # Keep a label-based preference from r3 onward.
            def remember_section(_event=None):
                try:
                    current = nb.select()
                    core.set_setting("main_last_tab_label_r3", nb.tab(current, "text"))
                except Exception:
                    pass
            nb.bind("<<NotebookTabChanged>>", remember_section, add="+")
            saved_label = core.get_setting("main_last_tab_label_r3", "")
            if saved_label:
                try:
                    for index in range(nb.index("end")):
                        if nb.tab(index, "text") == saved_label:
                            nb.select(index)
                            break
                except core.tk.TclError:
                    pass
            else:
                try:
                    nb.select(self.tab_personnel)
                except core.tk.TclError:
                    pass
            try:
                self._refresh_nav_selection()
            except Exception:
                pass

        def build_menu(self):
            result = super().build_menu()
            try:
                menu_name = self.cget("menu")
                menubar = self.nametowidget(menu_name)
                sections = None
                end = menubar.index("end")
                for index in range((end or -1) + 1):
                    if menubar.type(index) == "cascade" and menubar.entrycget(index, "label") == "Розділи":
                        sections = self.nametowidget(menubar.entrycget(index, "menu"))
                        break
                if sections is not None:
                    sections.insert_command(1, label="Персонал", accelerator="Alt+2", command=lambda: self.show_tab(self.tab_personnel))
                    # Після додавання нового верхнього розділу зсуваємо підписи
                    # Alt+... так, щоб вони відповідали фактичним індексам вкладок.
                    menu_end = sections.index("end")
                    for item_index in range((menu_end or -1) + 1):
                        if sections.type(item_index) == "command":
                            sections.entryconfigure(item_index, accelerator=f"Alt+{item_index+1}")
                    self.bind_all(
                        "<Alt-Key-9>",
                        lambda _event: (self.main_notebook.select(8), "break")[1],
                        add="+",
                    )
            except Exception:
                pass
            return result

        def __init__(self, *args, **kwargs):
            # App() is created only after core.init_db(), so this is the safe
            # point for the additive r6 schema migration.
            ensure_work_regime_schema(core)
            super().__init__(*args, **kwargs)
            self.title(WINDOW_TITLE)

        def _build_personnel_section(self):
            root = self.tab_personnel
            # The approved shell shows the personnel registry as the page
            # itself; the internal notebook stays only as a hidden container
            # for legacy planning/report panels.
            book = core.ttk.Notebook(root, style="Shell.TNotebook")
            book.pack(fill="both", expand=True, padx=10, pady=10)
            self.personnel_book = book
            overview = core.ttk.Frame(book)
            planning = core.ttk.Frame(book)
            timesheet = core.ttk.Frame(book)
            reports = core.ttk.Frame(book)
            book.add(overview, text="Реєстр")
            book.add(planning, text="Планування")
            book.add(timesheet, text="Табель")
            book.add(reports, text="Звіти")

            # Реєстр — основна сторінка «Працівники» у затвердженому shell.
            hero = core.ttk.Frame(overview, padding=(16,14,16,8))
            hero.pack(fill="x")
            hero_left = core.ttk.Frame(hero)
            hero_left.pack(side="left", fill="x", expand=True)
            core.ttk.Label(
                hero_left, text="Реєстр працівників", style="HeroTitle.TLabel"
            ).pack(anchor="w")
            core.ttk.Label(
                hero_left,
                text="Єдиний реєстр персоналу, посад, ролей та режимів робочого часу",
                style="Muted.TLabel",
            ).pack(anchor="w", pady=(3,0))
            core.ttk.Button(
                hero, text="＋  Новий працівник", style="Accent.TButton",
                command=self.employee_form
            ).pack(side="right", padx=(8,0))
            core.ttk.Button(
                hero, text="Відкрити картку", command=self._open_personnel_overview_employee
            ).pack(side="right")

            stats = core.ttk.Frame(overview, padding=(16,0,16,8))
            stats.pack(fill="x")
            self.personnel_stat_vars = {
                "all": core.tk.StringVar(value="0"),
                "active": core.tk.StringVar(value="0"),
                "drivers": core.tk.StringVar(value="0"),
                "inactive": core.tk.StringVar(value="0"),
            }
            def personnel_stat_card(parent, title, variable, bg, fg):
                card = core.tk.Frame(
                    parent, bg=bg, highlightthickness=1,
                    highlightbackground=core.PALETTE["line"]
                )
                core.tk.Label(
                    card, text=title, bg=bg, fg=core.PALETTE["navy"],
                    font=("TkDefaultFont",9,"bold")
                ).pack(anchor="w", padx=12, pady=(7,0))
                core.tk.Label(
                    card, textvariable=variable, bg=bg, fg=fg,
                    font=("TkDefaultFont",16,"bold")
                ).pack(anchor="w", padx=12, pady=(1,7))
                return card
            for idx,(key,title,bg,fg) in enumerate((
                ("all","Всього",core.PALETTE["info_soft"],core.PALETTE["navy"]),
                ("active","Працюють",core.PALETTE["success_soft"],core.PALETTE["success"]),
                ("drivers","Водії",core.PALETTE["info_soft"],core.PALETTE["blue"]),
                ("inactive","Звільнені",core.PALETTE["warning_soft"],core.PALETTE["warning"]),
            )):
                stats.columnconfigure(idx,weight=1)
                personnel_stat_card(
                    stats,title,self.personnel_stat_vars[key],bg,fg
                ).grid(
                    row=0,column=idx,sticky="ew",
                    padx=(0 if idx==0 else 4,4 if idx<3 else 0)
                )

            tools = core.ttk.Frame(overview, padding=(16,4,16,8))
            tools.pack(fill="x")
            tool_left = core.ttk.Frame(tools)
            tool_left.pack(side="left", fill="x", expand=True)
            core.ttk.Button(
                tool_left, text="Звільнити / поновити", command=self.toggle_employee_active
            ).pack(side="left", padx=(0,4))
            core.ttk.Button(
                tool_left, text="Режим робочого часу…", command=self.show_employee_work_regime
            ).pack(side="left", padx=4)
            core.ttk.Button(
                tool_left, text="Планування змін…", command=self.show_general_personnel_shift_planner
            ).pack(side="left", padx=4)
            core.ttk.Button(
                tool_left, text="Відсутності…", command=self.show_personnel_absence_planner
            ).pack(side="left", padx=4)
            core.ttk.Button(
                tool_left, text="Тижневий баланс…", command=self.show_personnel_week_balance
            ).pack(side="left", padx=4)
            core.ttk.Button(
                tool_left, text="Оновити", command=self._refresh_personnel_overview
            ).pack(side="left", padx=4)

            search_box=core.ttk.Frame(tools)
            search_box.pack(side="right", padx=(12,0))
            core.ttk.Label(search_box,text="Пошук").pack(side="left",padx=(0,5))
            self.personnel_search_var=core.tk.StringVar()
            search_entry=core.ttk.Entry(
                search_box,textvariable=self.personnel_search_var,width=28
            )
            search_entry.pack(side="left")
            self.personnel_search_var.trace_add(
                "write",lambda *_args:self._refresh_personnel_overview()
            )

            frame = core.ttk.Frame(overview); frame.pack(fill="both", expand=True, padx=12, pady=(0,8))
            frame.rowconfigure(0, weight=1); frame.columnconfigure(0, weight=1)
            cols = ("personnel","name","position","roles","regime","weeknorm","employment","status")
            tree = core.ttk.Treeview(frame, columns=cols, show="headings")
            self.personnel_overview_tree = tree
            for key,label,width in (
                ("personnel","Таб. №",90),("name","ПІБ",270),("position","Посада",175),
                ("roles","Спеціальні ролі",175),("regime","Режим",180),("weeknorm","Норма/тиж.",90),
                ("employment","Прийнятий",100),("status","Стан",90),
            ):
                tree.heading(key,text=label); tree.column(key,width=width,anchor="w")
            sy=core.ttk.Scrollbar(frame,orient="vertical",command=tree.yview)
            sx=core.ttk.Scrollbar(frame,orient="horizontal",command=tree.xview)
            tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set)
            tree.grid(row=0,column=0,sticky="nsew"); sy.grid(row=0,column=1,sticky="ns"); sx.grid(row=1,column=0,sticky="ew")
            tree.tag_configure("inactive",foreground=core.PALETTE["muted"])
            tree.bind("<Double-1>",lambda _event:self._open_personnel_overview_employee())
            tree.bind("<Return>",lambda _event:self._open_personnel_overview_employee())

            footer=core.ttk.Frame(overview,padding=(12,2,12,10))
            footer.pack(fill="x")
            core.ttk.Label(
                footer,
                text="Підказка: подвійний клік по працівнику відкриває його картку.",
                style="Muted.TLabel",
            ).pack(side="left")
            self.personnel_count_var=core.tk.StringVar(value="Всього: 0")
            core.ttk.Label(
                footer,textvariable=self.personnel_count_var,style="Muted.TLabel"
            ).pack(side="right")
            self._refresh_personnel_overview()

            # Планування
            panel = core.ttk.Frame(planning, padding=16); panel.pack(fill="x")
            core.ttk.Label(panel, text="Планування персоналу", font=("TkDefaultFont", 13, "bold")).pack(anchor="w")
            core.ttk.Label(
                panel,
                text="Робочі зміни плануються для будь-якого працівника. Відсутність позначає день як відсутній у табелі, але зберігає історичний робочий графік.",
                foreground="gray", wraplength=950, justify="left"
            ).pack(anchor="w", pady=(4,12))
            core.ttk.Button(panel, text="Режими робочого часу працівників…", command=self.show_employee_work_regime).pack(anchor="w", pady=4)
            core.ttk.Button(panel, text="Норма за режимом → план місяця…", command=self.show_regime_month_plan_filler).pack(anchor="w", pady=4)
            core.ttk.Button(panel, text="Робочі зміни — масово…", command=self.show_general_personnel_shift_planner).pack(anchor="w", pady=4)
            core.ttk.Button(panel, text="Відпустки / лікарняні / інші відсутності…", command=self.show_personnel_absence_planner).pack(anchor="w", pady=4)
            core.ttk.Button(panel, text="Лікар / механік для випуску на лінію…", command=self.show_dispatch_month_planner).pack(anchor="w", pady=4)

            # Табель
            tpanel = core.ttk.Frame(timesheet, padding=16); tpanel.pack(fill="x")
            core.ttk.Label(tpanel, text="Табель персоналу", font=("TkDefaultFont",13,"bold")).pack(anchor="w")
            core.ttk.Label(tpanel, text="Щоденний табель, місячний баланс, ручний факт і контроль відсутнього факту.", foreground="gray").pack(anchor="w", pady=(4,12))
            core.ttk.Button(tpanel, text="Відкрити табель персоналу", command=self.show_employee_timesheet).pack(anchor="w", pady=4)
            core.ttk.Button(tpanel, text="Тижневий баланс усього персоналу…", command=self.show_personnel_week_balance).pack(anchor="w", pady=4)
            core.ttk.Button(tpanel, text="Масово внести відсутність…", command=self.show_personnel_absence_planner).pack(anchor="w", pady=4)

            # Звіти
            rpanel = core.ttk.Frame(reports, padding=16); rpanel.pack(fill="x")
            now = date.today()
            self.personnel_report_month = core.tk.StringVar(value=str(now.month))
            self.personnel_report_year = core.tk.StringVar(value=str(now.year))
            self.personnel_report_form_date = core.tk.StringVar(value=now.strftime("%d.%m.%Y"))
            self.personnel_report_department = core.tk.StringVar(value=core.get_setting("personnel_report_department",""))
            self.personnel_report_edrpou = core.tk.StringVar(value=core.get_setting("company_edrpou",""))
            self.personnel_report_active = core.tk.BooleanVar(value=True)
            self.personnel_last_p5_pdf = None
            self.personnel_last_p5_xlsx = None
            row = core.ttk.Frame(rpanel); row.pack(fill="x")
            core.ttk.Label(row,text="Місяць").pack(side="left")
            core.ttk.Spinbox(row,textvariable=self.personnel_report_month,from_=1,to=12,width=5).pack(side="left",padx=(4,10))
            core.ttk.Label(row,text="Рік").pack(side="left")
            core.ttk.Spinbox(row,textvariable=self.personnel_report_year,from_=2020,to=2100,width=7).pack(side="left",padx=(4,10))
            core.ttk.Label(row,text="Дата заповнення").pack(side="left")
            core.ttk.Entry(row,textvariable=self.personnel_report_form_date,width=12).pack(side="left",padx=(4,4))
            core.calendar_button(row,self.personnel_report_form_date).pack(side="left",padx=(0,10))
            core.ttk.Checkbutton(row,text="Тільки активні працівники",variable=self.personnel_report_active).pack(side="left",padx=10)
            meta = core.ttk.Frame(rpanel); meta.pack(fill="x",pady=(8,0))
            core.ttk.Label(meta,text="Структурний підрозділ").pack(side="left")
            core.ttk.Entry(meta,textvariable=self.personnel_report_department,width=34).pack(side="left",padx=(4,12))
            core.ttk.Label(meta,text="ЄДРПОУ").pack(side="left")
            core.ttk.Entry(meta,textvariable=self.personnel_report_edrpou,width=16).pack(side="left",padx=(4,0))
            core.ttk.Label(
                rpanel,
                text=(
                    "Типова форма № П-5 (наказ Держкомстату України 05.12.2008 № 489): "
                    "умовні позначення 01–30, календарні дні, відпрацьований час, "
                    "причини неявок і підсумкові показники. Якщо є план без факту, Taxo "
                    "перед формуванням окремо запитає, чи підставляти план."
                ),
                foreground="gray",wraplength=980,justify="left"
            ).pack(anchor="w",pady=(12,8))
            b = core.ttk.Frame(rpanel); b.pack(fill="x")
            core.ttk.Button(b,text="Табель П-5 — PDF",command=lambda:self._save_p5("pdf")).pack(side="left",padx=(0,5))
            core.ttk.Button(b,text="Відкрити останній PDF",command=lambda:self._open_last_p5("pdf")).pack(side="left",padx=5)
            core.ttk.Button(b,text="Табель П-5 — Excel",command=lambda:self._save_p5("xlsx")).pack(side="left",padx=(16,5))
            core.ttk.Button(b,text="Відкрити останній Excel",command=lambda:self._open_last_p5("xlsx")).pack(side="left",padx=5)
            core.ttk.Button(b,text="Звичайний місячний табель",command=self.show_employee_timesheet).pack(side="left",padx=(16,5))

        def _open_personnel_overview_employee(self):
            tree=getattr(self,"personnel_overview_tree",None)
            if not widget_alive(tree) or not tree.selection():
                core.messagebox.showinfo(
                    "Працівники","Виберіть працівника у реєстрі.",parent=self
                )
                return
            try:
                employee_id=int(tree.selection()[0])
            except (TypeError,ValueError):
                return
            con=core.db()
            try:
                row=con.execute(
                    "SELECT * FROM employees WHERE id=?",(employee_id,)
                ).fetchone()
            finally:
                con.close()
            if row is not None:
                self.employee_form(row)

        def _refresh_personnel_overview(self):
            tree = getattr(self, "personnel_overview_tree", None)
            if not widget_alive(tree):
                return
            for item in tree.get_children(): tree.delete(item)
            query=""
            search_var=getattr(self,"personnel_search_var",None)
            if search_var is not None:
                try:
                    query=search_var.get().strip().casefold()
                except core.tk.TclError:
                    query=""
            con = core.db()
            count=0
            active_count=0
            driver_count=0
            inactive_count=0
            try:
                for row in _all_employee_rows(core, active_only=False):
                    name=core.employee_name(row)
                    roles=row["roles"] or ""
                    haystack=" ".join((
                        str(row["personnel_no"] or ""),name,
                        str(row["position"] or ""),str(roles),
                    )).casefold()
                    if query and query not in haystack:
                        continue
                    regime = latest_regime(con, row["id"])
                    regime_text = regime.label + ("" if regime.explicit else " (типово)")
                    tree.insert(
                        "", "end", iid=str(row["id"]),
                        values=(
                            row["personnel_no"] or "",
                            name,
                            row["position"] or "",
                            roles,
                            regime_text,
                            regime_hhmm(regime.weekly_norm_minutes),
                            core.fmt_date(row["employment_date"]),
                            "Працює" if row["active"] else "Звільнений",
                        ),
                        tags=(() if row["active"] else ("inactive",)),
                    )
                    count+=1
                    if row["active"]:
                        active_count+=1
                    else:
                        inactive_count+=1
                    if "Водій" in roles:
                        driver_count+=1
            finally:
                con.close()
            count_var=getattr(self,"personnel_count_var",None)
            if count_var is not None:
                count_var.set(f"Всього: {count}")
            stat_vars=getattr(self,"personnel_stat_vars",{})
            for key,value in (
                ("all",count),("active",active_count),
                ("drivers",driver_count),("inactive",inactive_count),
            ):
                variable=stat_vars.get(key)
                if variable is not None:
                    variable.set(str(value))

        def _active_employee_map(self):
            rows = _all_employee_rows(core, active_only=True)
            return {_employee_label(row): row for row in rows}

        def show_employee_timesheet(self):
            result = super().show_employee_timesheet()

            def walk(widget):
                yield widget
                try:
                    for child in widget.winfo_children():
                        yield from walk(child)
                except Exception:
                    return

            # Legacy code had a dangerous mass-fill action with a hard-coded
            # Mon-Fri 8:00 assumption. r6 disables it; planning is regime-based.
            for widget in walk(self):
                try:
                    if isinstance(widget, core.ttk.Button):
                        text_value = str(widget.cget("text") or "")
                        if "Порожні будні" in text_value and "8 год" in text_value:
                            widget.configure(
                                text="План за режимом — Персонал → Планування",
                                state="disabled",
                            )
                except Exception:
                    pass
            return result

        def show_employee_work_regime(self):
            existing = getattr(self, "_work_regime_win", None)
            if widget_alive(existing):
                existing.lift()
                return
            win = core.tk.Toplevel(self)
            self._work_regime_win = win
            win.title("Режим робочого часу працівника")
            core.fit_window_to_screen(win, 1040, 760, 820, 600)
            body = core.ttk.Frame(win, padding=10)
            body.pack(fill="both", expand=True)
            body.columnconfigure(1, weight=1)
            body.rowconfigure(11, weight=1)

            rows = _all_employee_rows(core, active_only=False)
            employees = {_employee_label(row): row for row in rows}
            selected_id = None
            tree = getattr(self, "personnel_overview_tree", None)
            if widget_alive(tree) and tree.selection():
                try:
                    selected_id = int(tree.selection()[0])
                except Exception:
                    selected_id = None
            initial = next(
                (label for label, row in employees.items() if row["id"] == selected_id),
                next(iter(employees), ""),
            )

            employee_var = core.tk.StringVar(value=initial)
            effective_from = core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
            effective_to = core.tk.StringVar()
            regime_label = core.tk.StringVar(value=REGIME_LABELS[REGIME_FIVE_DAY])
            period_label = core.tk.StringVar(value=PERIOD_LABELS[PERIOD_WEEK])
            weekly_norm = core.tk.StringVar(value="40:00")
            weekday_vars = [core.tk.StringVar(value=v) for v in ("8:00","8:00","8:00","8:00","8:00","0:00","0:00")]
            notes = core.tk.StringVar()

            def field(row_no, label, variable, calendar=False):
                core.ttk.Label(body, text=label).grid(row=row_no, column=0, sticky="w", pady=4, padx=(0,8))
                core.ttk.Entry(body, textvariable=variable).grid(row=row_no, column=1, sticky="ew", pady=4)
                if calendar:
                    core.calendar_button(body, variable).grid(row=row_no, column=2, sticky="w", padx=4)

            core.ttk.Label(body, text="Працівник").grid(row=0, column=0, sticky="w", pady=4)
            employee_combo = core.ttk.Combobox(
                body, textvariable=employee_var, values=list(employees),
                state="readonly", width=55
            )
            employee_combo.grid(row=0, column=1, sticky="ew", pady=4)
            field(1, "Діє з", effective_from, True)
            field(2, "Діє до (порожньо = безстроково)", effective_to, True)

            core.ttk.Label(body, text="Режим").grid(row=3, column=0, sticky="w", pady=4)
            core.ttk.Combobox(
                body, textvariable=regime_label, values=list(REGIME_BY_LABEL),
                state="readonly"
            ).grid(row=3, column=1, sticky="ew", pady=4)

            core.ttk.Label(body, text="Обліковий період").grid(row=4, column=0, sticky="w", pady=4)
            core.ttk.Combobox(
                body, textvariable=period_label, values=list(PERIOD_BY_LABEL),
                state="readonly"
            ).grid(row=4, column=1, sticky="ew", pady=4)

            field(5, "Тижнева норма, ГГ:ХХ", weekly_norm)

            days = core.ttk.LabelFrame(body, text="Норма за днями тижня", padding=8)
            days.grid(row=6, column=0, columnspan=3, sticky="ew", pady=8)
            for idx, label in enumerate(REGIME_WEEKDAY_LABELS):
                core.ttk.Label(days, text=label).grid(row=0, column=idx, padx=3)
                core.ttk.Entry(days, textvariable=weekday_vars[idx], width=8).grid(row=1, column=idx, padx=3, pady=3)

            presets = core.ttk.Frame(body)
            presets.grid(row=7, column=0, columnspan=3, sticky="w", pady=4)

            def apply_preset(key):
                day_values, weekly = PRESETS[key]()
                regime_label.set(
                    REGIME_LABELS[REGIME_FIVE_DAY if key.startswith("5/") else REGIME_SIX_DAY]
                )
                period_label.set(PERIOD_LABELS[PERIOD_WEEK])
                weekly_norm.set(regime_hhmm(weekly))
                for var, value in zip(weekday_vars, day_values):
                    var.set(regime_hhmm(value))

            core.ttk.Label(presets, text="Шаблони:").pack(side="left", padx=(0,4))
            for key, label in (
                ("5/40","5 днів / 40 год"),
                ("6/40","6 днів / 40 год"),
                ("6/36","6 днів / 36 год"),
                ("6/24","6 днів / 24 год"),
            ):
                core.ttk.Button(
                    presets, text=label, command=lambda k=key: apply_preset(k)
                ).pack(side="left", padx=3)

            field(8, "Примітка / підстава", notes)
            info_var = core.tk.StringVar()
            core.ttk.Label(
                body, textvariable=info_var, foreground="gray",
                wraplength=940, justify="left"
            ).grid(row=9, column=0, columnspan=3, sticky="w", pady=(2,6))

            history_frame = core.ttk.LabelFrame(body, text="Історія режимів", padding=6)
            history_frame.grid(row=11, column=0, columnspan=3, sticky="nsew", pady=(8,0))
            history_frame.rowconfigure(0, weight=1)
            history_frame.columnconfigure(0, weight=1)
            history = core.ttk.Treeview(
                history_frame,
                columns=("from","to","regime","period","weekly","schedule","notes"),
                show="headings",
            )
            for key, label, width in (
                ("from","З",90),("to","До",90),("regime","Режим",170),
                ("period","Облік",100),("weekly","Норма",75),
                ("schedule","Пн–Нд",280),("notes","Примітка",260),
            ):
                history.heading(key, text=label)
                history.column(key, width=width, anchor="w")
            sy = core.ttk.Scrollbar(history_frame, orient="vertical", command=history.yview)
            sx = core.ttk.Scrollbar(history_frame, orient="horizontal", command=history.xview)
            history.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
            history.grid(row=0, column=0, sticky="nsew")
            sy.grid(row=0, column=1, sticky="ns")
            sx.grid(row=1, column=0, sticky="ew")

            def selected_employee():
                row = employees.get(employee_var.get())
                if not row:
                    raise ValueError("Виберіть працівника.")
                return row

            def load_history(_event=None):
                for item in history.get_children():
                    history.delete(item)
                try:
                    employee = selected_employee()
                except ValueError:
                    return
                con = core.db()
                records = con.execute(
                    """SELECT * FROM employee_work_regimes
                       WHERE employee_id=?
                       ORDER BY effective_from DESC,id DESC""",
                    (employee["id"],),
                ).fetchall()
                latest = latest_regime(con, employee["id"])
                con.close()
                if records:
                    for row in records:
                        schedule = " ".join(
                            f"{REGIME_WEEKDAY_LABELS[i]} {regime_hhmm(row[f'{key}_minutes'])}"
                            for i, key in enumerate(("mon","tue","wed","thu","fri","sat","sun"))
                            if int(row[f"{key}_minutes"] or 0) > 0
                        )
                        history.insert("", "end", iid=str(row["id"]), values=(
                            core.fmt_date(row["effective_from"]),
                            core.fmt_date(row["effective_to"]),
                            REGIME_LABELS.get(row["regime_type"], row["regime_type"]),
                            PERIOD_LABELS.get(row["accounting_period"], row["accounting_period"]),
                            regime_hhmm(row["weekly_norm_minutes"]),
                            schedule, row["notes"] or "",
                        ))
                else:
                    history.insert("", "end", values=(
                        "—","—",latest.label + " (типово)", latest.accounting_label,
                        regime_hhmm(latest.weekly_norm_minutes),
                        "Пн–Пт 8:00","Режим ще не задано явно",
                    ))
                info_var.set(
                    "Звичайна норма за КЗпП — до 40:00/тиждень. Для 6-денного тижня "
                    "Taxo контролює денні межі 7:00 при 40:00, 6:00 при 36:00 і 4:00 при 24:00. "
                    "Для підсумованого обліку тижневий баланс довідковий; надурочні визначаються "
                    "за підсумком установленого облікового періоду."
                )

            def load_selected_history(_event=None):
                sel = history.selection()
                if not sel:
                    return
                try:
                    regime_id = int(sel[0])
                except ValueError:
                    return
                con = core.db()
                row = con.execute(
                    "SELECT * FROM employee_work_regimes WHERE id=?", (regime_id,)
                ).fetchone()
                con.close()
                if not row:
                    return
                effective_from.set(core.fmt_date(row["effective_from"]))
                effective_to.set(core.fmt_date(row["effective_to"]))
                regime_label.set(REGIME_LABELS.get(row["regime_type"], row["regime_type"]))
                period_label.set(PERIOD_LABELS.get(row["accounting_period"], row["accounting_period"]))
                weekly_norm.set(regime_hhmm(row["weekly_norm_minutes"]))
                for idx, key in enumerate(("mon","tue","wed","thu","fri","sat","sun")):
                    weekday_vars[idx].set(regime_hhmm(row[f"{key}_minutes"]))
                notes.set(row["notes"] or "")

            def new_period():
                effective_from.set(date.today().strftime("%d.%m.%Y"))
                effective_to.set("")
                notes.set("")
                apply_preset("5/40")

            def save_current():
                try:
                    employee = selected_employee()
                    start = datetime.strptime(effective_from.get().strip(), "%d.%m.%Y").date()
                    end_text = effective_to.get().strip()
                    end = datetime.strptime(end_text, "%d.%m.%Y").date() if end_text else None
                    if end is not None and end < start:
                        raise ValueError("Дата «до» раніше дати «з».")
                    regime_type = REGIME_BY_LABEL[regime_label.get()]
                    period = PERIOD_BY_LABEL[period_label.get()]
                    weekly = regime_parse_hhmm(weekly_norm.get())
                    day_values = tuple(regime_parse_hhmm(var.get()) for var in weekday_vars)
                    errors, warnings = validate_regime(regime_type, weekly, day_values)
                    if errors:
                        raise ValueError("\n".join(errors))
                except Exception as exc:
                    core.messagebox.showerror("Режим робочого часу", str(exc), parent=win)
                    return

                if warnings and not core.messagebox.askyesno(
                    "Перевірте правову підставу",
                    "\n".join(warnings) + "\n\nЗберегти цей режим?",
                    parent=win,
                ):
                    return

                con = core.db()
                try:
                    # Close an older open-ended period when a genuinely new
                    # effective date is inserted, preserving history.
                    existing_same = con.execute(
                        """SELECT id FROM employee_work_regimes
                           WHERE employee_id=? AND effective_from=?""",
                        (employee["id"], start.isoformat()),
                    ).fetchone()
                    if existing_same is None:
                        previous = con.execute(
                            """SELECT id,effective_from,effective_to
                               FROM employee_work_regimes
                               WHERE employee_id=? AND effective_from<?
                               ORDER BY effective_from DESC,id DESC LIMIT 1""",
                            (employee["id"], start.isoformat()),
                        ).fetchone()
                        if previous and (
                            not (previous["effective_to"] or "").strip()
                            or previous["effective_to"] >= start.isoformat()
                        ):
                            con.execute(
                                "UPDATE employee_work_regimes SET effective_to=?,updated_at=? WHERE id=?",
                                (
                                    (start - timedelta(days=1)).isoformat(),
                                    datetime.now().isoformat(timespec="seconds"),
                                    previous["id"],
                                ),
                            )
                    save_regime(
                        con,
                        employee_id=employee["id"],
                        effective_from=start,
                        effective_to=end,
                        regime_type=regime_type,
                        accounting_period=period,
                        weekly_norm_minutes=weekly,
                        weekday_minutes=day_values,
                        notes=notes.get().strip(),
                    )
                    con.commit()
                finally:
                    con.close()
                load_history()
                self._refresh_personnel_overview()
                core.messagebox.showinfo(
                    "Режим робочого часу",
                    "Режим збережено. Історичні табелі використовують режим, що діяв на відповідну дату.",
                    parent=win,
                )

            actions = core.ttk.Frame(body)
            actions.grid(row=10, column=0, columnspan=3, sticky="ew", pady=4)
            core.ttk.Button(actions, text="Новий період", command=new_period).pack(side="left", padx=3)
            core.ttk.Button(actions, text="Зберегти режим", command=save_current).pack(side="left", padx=3)
            core.ttk.Button(actions, text="Закрити", command=win.destroy).pack(side="right", padx=3)
            employee_combo.bind("<<ComboboxSelected>>", load_history)
            history.bind("<<TreeviewSelect>>", load_selected_history)
            load_history()

        def show_personnel_week_balance(self):
            existing = getattr(self, "_personnel_week_balance_win", None)
            if widget_alive(existing):
                existing.lift()
                return
            win = core.tk.Toplevel(self)
            self._personnel_week_balance_win = win
            win.title("Тижневий баланс робочого часу — весь персонал")
            core.fit_window_to_screen(win, 1500, 760, 980, 560)
            top = core.ttk.Frame(win, padding=8)
            top.pack(fill="x")
            anchor = core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
            active_only = core.tk.BooleanVar(value=True)
            core.ttk.Label(top, text="Дата у тижні").pack(side="left")
            core.ttk.Entry(top, textvariable=anchor, width=12).pack(side="left", padx=(4,3))
            core.calendar_button(top, anchor).pack(side="left", padx=(0,8))
            core.ttk.Checkbutton(
                top, text="Тільки активні працівники", variable=active_only
            ).pack(side="left", padx=8)

            frame = core.ttk.Frame(win)
            frame.pack(fill="both", expand=True, padx=8, pady=(0,6))
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            cols = (
                "personnel","name","roles","regime","norm","absence","adjusted",
                "plan","fact","difference","missing","note"
            )
            tree = core.ttk.Treeview(frame, columns=cols, show="headings")
            for key, label, width in (
                ("personnel","Таб. №",80),("name","Працівник",260),("roles","Посада/ролі",180),
                ("regime","Режим",170),("norm","Норма",75),("absence","− відсутн.",85),
                ("adjusted","Скориг.",80),("plan","План",75),("fact","Факт",75),
                ("difference","Δ",75),("missing","Без факту",75),("note","Примітка",390),
            ):
                tree.heading(key, text=label)
                tree.column(key, width=width, anchor="w" if key in ("name","roles","regime","note") else "center")
            sy = core.ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            sx = core.ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
            tree.grid(row=0, column=0, sticky="nsew")
            sy.grid(row=0, column=1, sticky="ns")
            sx.grid(row=1, column=0, sticky="ew")
            status = core.tk.StringVar()
            core.ttk.Label(win, textvariable=status, font=("TkDefaultFont",9,"bold")).pack(
                fill="x", padx=10, pady=(0,3)
            )
            core.ttk.Label(
                win,
                text=(
                    "Норма = календарна норма працівника за його режимом. "
                    "«− відсутн.» коригує норму на законну відпустку/лікарняний у години, "
                    "які за графіком мали бути робочими. Для підсумованого обліку тижневий Δ "
                    "інформаційний — надурочні визначаються наприкінці облікового періоду."
                ),
                foreground="gray", wraplength=1450, justify="left",
            ).pack(fill="x", padx=10, pady=(0,7))

            def read_anchor():
                try:
                    return datetime.strptime(anchor.get().strip(), "%d.%m.%Y").date()
                except ValueError:
                    core.messagebox.showerror(
                        "Тижневий баланс", "Дата має бути у форматі ДД.ММ.РРРР.", parent=win
                    )
                    return None

            def refresh():
                current = read_anchor()
                if not current:
                    return
                data = collect_personnel_week_balance(core, current, active_only.get())
                for item in tree.get_children():
                    tree.delete(item)
                for row in data["employees"]:
                    tree.insert("", "end", values=(
                        row["personnel_no"], row["name"], row["roles"], row["regime"],
                        regime_hhmm(row["base_norm"]),
                        ("-" + regime_hhmm(row["absence_reduction"])) if row["absence_reduction"] else "0:00",
                        regime_hhmm(row["adjusted_norm"]),
                        regime_hhmm(row["planned"]),
                        regime_hhmm(row["actual"]),
                        regime_hhmm(row["difference"]),
                        row["missing"], row["note"],
                    ))
                status.set(
                    f"{data['start'].strftime('%d.%m.%Y')}–{data['end'].strftime('%d.%m.%Y')}: "
                    f"працівників {len(data['employees'])}"
                )

            def move_week(delta):
                current = read_anchor()
                if not current:
                    return
                anchor.set((current + timedelta(days=delta * 7)).strftime("%d.%m.%Y"))
                refresh()

            core.ttk.Button(top, text="← Тиждень", command=lambda: move_week(-1)).pack(side="left", padx=3)
            core.ttk.Button(top, text="Оновити", command=refresh).pack(side="left", padx=3)
            core.ttk.Button(top, text="Тиждень →", command=lambda: move_week(1)).pack(side="left", padx=3)
            active_only.trace_add("write", lambda *_: refresh())
            refresh()

        def show_regime_month_plan_filler(self):
            existing = getattr(self, "_regime_fill_win", None)
            if widget_alive(existing):
                existing.lift()
                return
            win = core.tk.Toplevel(self)
            self._regime_fill_win = win
            win.title("Заповнити план за режимом робочого часу")
            core.fit_window_to_screen(win, 900, 650, 720, 520)
            body = core.ttk.Frame(win, padding=10)
            body.pack(fill="both", expand=True)
            body.columnconfigure(1, weight=1)
            body.rowconfigure(5, weight=1)

            employees = self._active_employee_map()
            employee_var = core.tk.StringVar(value=next(iter(employees), ""))
            today = date.today()
            month_var = core.tk.StringVar(value=str(today.month))
            year_var = core.tk.StringVar(value=str(today.year))
            core.ttk.Label(body, text="Працівник").grid(row=0,column=0,sticky="w",pady=4)
            core.ttk.Combobox(
                body,textvariable=employee_var,values=list(employees),state="readonly"
            ).grid(row=0,column=1,sticky="ew",pady=4)
            core.ttk.Label(body,text="Місяць").grid(row=1,column=0,sticky="w",pady=4)
            mr=core.ttk.Frame(body); mr.grid(row=1,column=1,sticky="w")
            core.ttk.Spinbox(mr,textvariable=month_var,from_=1,to=12,width=5).pack(side="left")
            core.ttk.Label(mr,text="Рік").pack(side="left",padx=(10,3))
            core.ttk.Spinbox(mr,textvariable=year_var,from_=2020,to=2100,width=7).pack(side="left")

            info = core.tk.StringVar()
            core.ttk.Label(
                body,textvariable=info,foreground="gray",wraplength=820,justify="left"
            ).grid(row=2,column=0,columnspan=2,sticky="w",pady=(4,8))

            tree = core.ttk.Treeview(
                body,columns=("date","weekday","norm","action"),show="headings"
            )
            for key,label,width in (
                ("date","Дата",100),("weekday","День",70),
                ("norm","Норма",90),("action","Дія",520),
            ):
                tree.heading(key,text=label); tree.column(key,width=width,anchor="w")
            tree.grid(row=5,column=0,columnspan=2,sticky="nsew")
            sy=core.ttk.Scrollbar(body,orient="vertical",command=tree.yview)
            tree.configure(yscrollcommand=sy.set); sy.grid(row=5,column=2,sticky="ns")

            def evaluate():
                employee = employees.get(employee_var.get())
                if not employee:
                    raise ValueError("Виберіть працівника.")
                y=int(year_var.get()); m=int(month_var.get())
                con=core.db(); rows=[]
                summarized=False
                for day_no in range(1,calendar.monthrange(y,m)[1]+1):
                    d=date(y,m,day_no)
                    if not core.employee_employed_on(employee,d):
                        continue
                    norm, regime = day_norm_minutes(con,employee["id"],d)
                    summarized = summarized or regime.regime_type == REGIME_SUMMARIZED
                    if norm<=0:
                        continue
                    entry=con.execute(
                        "SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",
                        (employee["id"],d.isoformat())
                    ).fetchone()
                    driver=core._driver_plan_minutes_for_day(con,employee["driver_id"],d)
                    shift,_actual,_found=core._employee_shift_minutes_for_day(con,employee["id"],d)
                    if entry:
                        action="Є ручний запис — не змінювати"
                    elif driver>0 or shift>0:
                        action="Є графік/зміна — не дублювати"
                    else:
                        action="Додати план за режимом"
                    rows.append((d,norm,action))
                con.close()
                return employee,rows,summarized

            def preview():
                for item in tree.get_children(): tree.delete(item)
                try:
                    employee,rows,summarized=evaluate()
                except Exception as exc:
                    core.messagebox.showerror("План за режимом",str(exc),parent=win); return
                for d,norm,action in rows:
                    tree.insert("", "end", values=(
                        d.strftime("%d.%m.%Y"),REGIME_WEEKDAY_LABELS[d.weekday()],
                        regime_hhmm(norm),action
                    ))
                info.set(
                    ("Підсумований облік: цей режим визначає норму, але робочі зміни мають задаватися затвердженим графіком. "
                     "Автоматичне заповнення за тижневим шаблоном вимкнено."
                     if summarized else
                     "Заповнюються лише порожні нормативні робочі дні. Існуючі маршрути, зміни, ручні записи та факт не змінюються.")
                )

            def apply():
                try:
                    employee,rows,summarized=evaluate()
                except Exception as exc:
                    core.messagebox.showerror("План за режимом",str(exc),parent=win); return
                if summarized:
                    core.messagebox.showwarning(
                        "Підсумований облік",
                        "Для підсумованого обліку плануйте фактичний графік змін/маршрутів. "
                        "Taxo використовує режим для норми облікового періоду, але не вигадує розподіл змін.",
                        parent=win,
                    )
                    return
                writable=[x for x in rows if x[2]=="Додати план за режимом"]
                if not writable:
                    core.messagebox.showinfo("План за режимом","Немає порожніх днів для запису.",parent=win); return
                if not core.messagebox.askyesno(
                    "План за режимом",
                    f"Записати план за режимом на {len(writable)} дн. для {core.employee_name(employee)}?",
                    parent=win,
                ):
                    return
                con=core.db(); now=datetime.now().isoformat(timespec="seconds"); added=0
                try:
                    for d,norm,_action in writable:
                        if insert_regime_month_plan_if_empty(
                            core, con, employee, d, norm, now
                        ):
                            added+=1
                    con.commit()
                finally:
                    con.close()
                preview()
                core.messagebox.showinfo("План за режимом",f"Додано планових днів: {added}.",parent=win)

            actions=core.ttk.Frame(body); actions.grid(row=4,column=0,columnspan=2,sticky="w",pady=5)
            core.ttk.Button(actions,text="Переглянути",command=preview).pack(side="left",padx=3)
            core.ttk.Button(actions,text="Застосувати",command=apply).pack(side="left",padx=3)
            preview()

        def show_general_personnel_shift_planner(self):
            existing = getattr(self, "_personnel_shift_win", None)
            if widget_alive(existing):
                existing.lift(); return
            win = core.tk.Toplevel(self); self._personnel_shift_win = win
            win.title("Масове планування робочих змін персоналу")
            core.fit_window_to_screen(win, 980, 720, 780, 560)
            body = core.ttk.Frame(win, padding=10); body.pack(fill="both", expand=True)
            body.columnconfigure(1, weight=1); body.rowconfigure(11, weight=1)

            employees = self._active_employee_map()
            employee_var = core.tk.StringVar(value=next(iter(employees), ""))
            role_var = core.tk.StringVar()
            start_var = core.tk.StringVar(value=date.today().replace(day=1).strftime("%d.%m.%Y"))
            last = date.today().replace(day=calendar.monthrange(date.today().year,date.today().month)[1])
            end_var = core.tk.StringVar(value=last.strftime("%d.%m.%Y"))
            pattern_var = core.tk.StringVar(value=PATTERN_WEEKDAYS)
            shift_var = core.tk.StringVar(value="I")
            start_time = core.tk.StringVar(value="08:00")
            end_time = core.tk.StringVar(value="17:00")
            end_day = core.tk.StringVar(value="0")
            location = core.tk.StringVar()
            note = core.tk.StringVar(value="Місячний план персоналу")
            replace = core.tk.BooleanVar(value=False)
            cycle_work = core.tk.StringVar(value="2")
            cycle_rest = core.tk.StringVar(value="2")
            weekdays = [core.tk.BooleanVar(value=(i<5)) for i in range(7)]

            def field(row,label,var,calendar_btn=False):
                core.ttk.Label(body,text=label).grid(row=row,column=0,sticky="w",pady=4,padx=(0,8))
                core.ttk.Entry(body,textvariable=var).grid(row=row,column=1,sticky="ew",pady=4)
                if calendar_btn: core.calendar_button(body,var).grid(row=row,column=2,sticky="w",padx=4)

            core.ttk.Label(body,text="Працівник").grid(row=0,column=0,sticky="w",pady=4)
            emp_combo=core.ttk.Combobox(body,textvariable=employee_var,values=list(employees),state="readonly")
            emp_combo.grid(row=0,column=1,sticky="ew",pady=4)
            core.ttk.Label(body,text="Роль / посада").grid(row=1,column=0,sticky="w",pady=4)
            role_combo=core.ttk.Combobox(body,textvariable=role_var,state="readonly")
            role_combo.grid(row=1,column=1,sticky="ew",pady=4)
            field(2,"Період з",start_var,True); field(3,"Період до",end_var,True)
            core.ttk.Label(body,text="Схема").grid(row=4,column=0,sticky="w",pady=4)
            core.ttk.Combobox(body,textvariable=pattern_var,values=PATTERNS,state="readonly").grid(row=4,column=1,sticky="w",pady=4)

            times=core.ttk.Frame(body); times.grid(row=5,column=0,columnspan=3,sticky="ew",pady=4)
            for label,var,width in (("Зміна",shift_var,5),("Початок",start_time,8),("D+",end_day,4),("Кінець",end_time,8),("Місце",location,20)):
                core.ttk.Label(times,text=label).pack(side="left",padx=(0,3))
                if label=="Зміна":
                    core.ttk.Combobox(times,textvariable=var,values=("I","II"),state="readonly",width=width).pack(side="left",padx=(0,10))
                elif label=="D+":
                    core.ttk.Spinbox(times,textvariable=var,from_=0,to=7,width=width).pack(side="left",padx=(0,10))
                else:
                    core.ttk.Entry(times,textvariable=var,width=width).pack(side="left",padx=(0,10))

            wf=core.ttk.Frame(body); wf.grid(row=6,column=0,columnspan=3,sticky="w",pady=4)
            core.ttk.Label(wf,text="Дні тижня").pack(side="left",padx=(0,6))
            for i,label in enumerate(WEEKDAY_NAMES):
                core.ttk.Checkbutton(wf,text=label,variable=weekdays[i]).pack(side="left")

            cycle=core.ttk.Frame(body); cycle.grid(row=7,column=0,columnspan=3,sticky="w",pady=4)
            core.ttk.Label(cycle,text="Власний цикл: робота").pack(side="left")
            core.ttk.Spinbox(cycle,textvariable=cycle_work,from_=1,to=31,width=4).pack(side="left",padx=4)
            core.ttk.Label(cycle,text="дн. / відпочинок").pack(side="left")
            core.ttk.Spinbox(cycle,textvariable=cycle_rest,from_=1,to=31,width=4).pack(side="left",padx=4)
            core.ttk.Label(cycle,text="дн.").pack(side="left")

            field(8,"Примітка",note)
            core.ttk.Checkbutton(body,text="Замінювати існуючий ПЛАН цього працівника (факт не змінювати)",variable=replace).grid(row=9,column=0,columnspan=3,sticky="w",pady=4)

            tree=core.ttk.Treeview(body,columns=("date","action","current"),show="headings")
            for k,l,w in (("date","Дата",95),("action","Дія",220),("current","Поточне / конфлікт",520)):
                tree.heading(k,text=l); tree.column(k,width=w,anchor="w")
            sy=core.ttk.Scrollbar(body,orient="vertical",command=tree.yview); tree.configure(yscrollcommand=sy.set)
            tree.grid(row=11,column=0,columnspan=2,sticky="nsew",pady=(8,0)); sy.grid(row=11,column=2,sticky="ns",pady=(8,0))

            def refresh_roles(_event=None):
                emp=employees.get(employee_var.get())
                choices=_employee_role_choices(emp) if emp else []
                role_combo["values"]=choices
                if role_var.get() not in choices: role_var.set(choices[0] if choices else "")

            def parse():
                emp=employees.get(employee_var.get())
                if not emp: raise ValueError("Виберіть працівника.")
                start=datetime.strptime(start_var.get().strip(),"%d.%m.%Y").date()
                end=datetime.strptime(end_var.get().strip(),"%d.%m.%Y").date()
                wd=[i for i,v in enumerate(weekdays) if v.get()]
                dates=pattern_dates(
                    start,end,pattern_var.get(),weekdays=wd,
                    work_days=int(cycle_work.get()),rest_days=int(cycle_rest.get())
                )
                if pattern_var.get()==PATTERN_SELECTED and not wd: raise ValueError("Виберіть дні тижня.")
                dplus=int(end_day.get()); minutes=shift_span_minutes(start_time.get(),end_time.get(),dplus)
                return emp,dates,dplus,minutes

            def evaluate(show_error=True):
                try:
                    emp,dates,dplus,minutes=parse()
                except Exception as exc:
                    if show_error: core.messagebox.showerror("Планування",str(exc),parent=win)
                    return None,[]
                con=core.db(); rows=[]
                if emp["driver_id"] and _is_driver_role(role_var.get()):
                    for d in dates:
                        rows.append((
                            d,
                            "Водій — планувати у «Графік водіїв»",
                            "Щоб не дублювати маршрут/робочий час у employee_shifts",
                        ))
                    con.close()
                    return (emp,dates,dplus,minutes),rows
                for d in dates:
                    if not core.employee_employed_on(emp,d):
                        rows.append((d,"Поза періодом роботи","")); continue
                    absence=con.execute(
                        "SELECT day_type,notes FROM employee_time_entries WHERE employee_id=? AND work_date=?",
                        (emp["id"],d.isoformat())
                    ).fetchone()
                    if absence and str(absence["day_type"] or "") in NONWORK_OVERRIDE_TYPES:
                        rows.append((d,"Відсутність — не планувати",f"{absence['day_type']} · {absence['notes'] or ''}")); continue
                    own=con.execute("""SELECT * FROM employee_shifts WHERE employee_id=? AND role=? AND work_date=? AND shift_no=? ORDER BY id""",
                                    (emp["id"],role_var.get(),d.isoformat(),1 if shift_var.get()=="I" else 2)).fetchall()
                    if any(r["actual_hours"] is not None for r in own):
                        rows.append((d,"Факт — не змінювати","")); continue
                    if own and not replace.get():
                        rows.append((d,"Вже заплановано — пропустити",f"{own[0]['start_time']}–{own[0]['end_time']}")); continue
                    # Any overlapping shift of the same employee (even another role) is conflict.
                    any_rows=con.execute("SELECT * FROM employee_shifts WHERE employee_id=? AND work_date BETWEEN ? AND ?",
                                         (emp["id"],(d-timedelta(days=1)).isoformat(),(d+timedelta(days=1)).isoformat())).fetchall()
                    start_dt=datetime.combine(d,datetime.min.time())+timedelta(minutes=parse_clock(start_time.get()))
                    end_dt=datetime.combine(d+timedelta(days=dplus),datetime.min.time())+timedelta(minutes=parse_clock(end_time.get()))
                    conflict=None
                    for rr in any_rows:
                        if own and rr["id"] in {x["id"] for x in own}: continue
                        base=date.fromisoformat(rr["work_date"])
                        rs=datetime.combine(base,datetime.min.time())+timedelta(minutes=parse_clock(rr["start_time"]))
                        re=datetime.combine(base+timedelta(days=int(rr["end_day_offset"] or 0)),datetime.min.time())+timedelta(minutes=parse_clock(rr["end_time"]))
                        if start_dt < re and rs < end_dt: conflict=rr; break
                    if conflict:
                        rows.append((d,"Конфлікт з іншою зміною",f"{conflict['role']} {conflict['start_time']}–{conflict['end_time']}")); continue

                    driver_conflict = driver_plan_conflict(
                        core, con, emp, start_dt, end_dt
                    )
                    if driver_conflict:
                        if driver_conflict["kind"] == "overlap":
                            rows.append((
                                d,
                                "Конфлікт з графіком водія",
                                f"{driver_conflict['start'].strftime('%H:%M')}–"
                                f"{driver_conflict['end'].strftime('%H:%M')}"
                                + (f" · {driver_conflict['route']}" if driver_conflict['route'] else ""),
                            ))
                        else:
                            rows.append((
                                d,
                                "Замінити план ⚠" if own else "Додати ⚠",
                                "Є план водія лише за тривалістю; точний час не задано, перетин не перевіряється",
                            ))
                            continue
                        continue
                    rows.append((d,"Замінити план" if own else "Додати",""))
                con.close(); return (emp,dates,dplus,minutes),rows

            def preview():
                for x in tree.get_children(): tree.delete(x)
                _plan,rows=evaluate()
                for d,a,curr in rows: tree.insert("","end",values=(d.strftime("%d.%m.%Y"),a,curr))

            def apply():
                plan,rows=evaluate()
                if not plan: return
                writable=[x for x in rows if x[1] in ("Додати","Замінити план","Додати ⚠","Замінити план ⚠")]
                if not writable:
                    core.messagebox.showinfo("Планування","Немає дат для запису.",parent=win); return
                if not core.messagebox.askyesno("Планування",f"Записати {len(writable)} змін(и)?",parent=win): return
                emp,dates,dplus,minutes=plan; con=core.db(); added=0; skipped=0
                now_note=note.get().strip()
                for d,action,_curr in rows:
                    if action not in ("Додати","Замінити план","Додати ⚠","Замінити план ⚠"): skipped+=1; continue
                    absence=con.execute(
                        "SELECT day_type FROM employee_time_entries WHERE employee_id=? AND work_date=?",
                        (emp["id"],d.isoformat())
                    ).fetchone()
                    if absence and str(absence["day_type"] or "") in NONWORK_OVERRIDE_TYPES:
                        skipped+=1; continue
                    own=con.execute("SELECT * FROM employee_shifts WHERE employee_id=? AND role=? AND work_date=? AND shift_no=?",
                                    (emp["id"],role_var.get(),d.isoformat(),1 if shift_var.get()=="I" else 2)).fetchall()
                    if any(r["actual_hours"] is not None for r in own): skipped+=1; continue
                    start_dt=datetime.combine(d,datetime.min.time())+timedelta(minutes=parse_clock(start_time.get()))
                    end_dt=datetime.combine(d+timedelta(days=dplus),datetime.min.time())+timedelta(minutes=parse_clock(end_time.get()))
                    driver_conflict=driver_plan_conflict(core, con, emp, start_dt, end_dt)
                    if driver_conflict and driver_conflict["kind"]=="overlap":
                        skipped+=1; continue
                    if own and replace.get():
                        con.executemany("DELETE FROM employee_shifts WHERE id=? AND actual_hours IS NULL",[(r["id"],) for r in own])
                    elif own:
                        skipped+=1; continue
                    try:
                        con.execute("""INSERT INTO employee_shifts(employee_id,role,work_date,shift_no,start_time,end_day_offset,end_time,location,planned_hours,actual_hours,status,notes)
                                      VALUES(?,?,?,?,?,?,?,?,?,NULL,'planned',?)""",
                                    (emp["id"],role_var.get(),d.isoformat(),1 if shift_var.get()=="I" else 2,start_time.get(),dplus,end_time.get(),location.get().strip(),minutes/60.0,now_note))
                        added+=1
                    except Exception:
                        skipped+=1
                con.commit(); con.close(); preview()
                core.messagebox.showinfo("Планування",f"Записано: {added}. Пропущено: {skipped}.",parent=win)

            core.ttk.Label(
                body,
                text=(
                    "Сумісництво: кілька ролей в один день дозволені, якщо точні часові "
                    "інтервали не перетинаються. План лише «8 год» не означає 08:00–16:00 "
                    "і дає попередження, а не автоматичний конфлікт."
                ),
                foreground="gray", wraplength=900, justify="left",
            ).grid(row=9,column=0,columnspan=3,sticky="w",pady=(2,6))
            buttons=core.ttk.Frame(body); buttons.grid(row=10,column=0,columnspan=3,sticky="ew")
            core.ttk.Button(buttons,text="Переглянути",command=preview).pack(side="left",padx=3)
            core.ttk.Button(buttons,text="Застосувати",command=apply).pack(side="left",padx=3)
            emp_combo.bind("<<ComboboxSelected>>",refresh_roles)
            refresh_roles(); preview()

        def show_personnel_absence_planner(self):
            existing=getattr(self,"_personnel_absence_win",None)
            if widget_alive(existing): existing.lift(); return
            win=core.tk.Toplevel(self); self._personnel_absence_win=win
            win.title("Масове внесення відпусток / лікарняних / відсутностей")
            core.fit_window_to_screen(win,980,700,760,540)
            body=core.ttk.Frame(win,padding=10); body.pack(fill="both",expand=True)
            body.columnconfigure(1,weight=1); body.rowconfigure(9,weight=1)
            employees=self._active_employee_map()
            employee_var=core.tk.StringVar(value=next(iter(employees),""))
            dtype=core.tk.StringVar(value=ABSENCE_TYPES[0])
            start_var=core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
            end_var=core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
            notes=core.tk.StringVar()
            fill_mode=core.tk.StringVar(value=ABSENCE_RANGE_PLANNED)
            replace=core.tk.BooleanVar(value=False)

            core.ttk.Label(body,text="Працівник").grid(row=0,column=0,sticky="w",pady=5)
            core.ttk.Combobox(body,textvariable=employee_var,values=list(employees),state="readonly").grid(row=0,column=1,sticky="ew",pady=5)
            core.ttk.Label(body,text="Вид відсутності").grid(row=1,column=0,sticky="w",pady=5)
            core.ttk.Combobox(body,textvariable=dtype,values=ABSENCE_TYPES,state="readonly").grid(row=1,column=1,sticky="ew",pady=5)
            for row,label,var in ((2,"Період з",start_var),(3,"Період до",end_var),(4,"Примітка",notes)):
                core.ttk.Label(body,text=label).grid(row=row,column=0,sticky="w",pady=5)
                core.ttk.Entry(body,textvariable=var).grid(row=row,column=1,sticky="ew",pady=5)
                if row in (2,3): core.calendar_button(body,var).grid(row=row,column=2,sticky="w",padx=4)
            core.ttk.Label(body,text="Заповнювати").grid(row=5,column=0,sticky="w",pady=5)
            core.ttk.Combobox(
                body,textvariable=fill_mode,
                values=(ABSENCE_RANGE_PLANNED,ABSENCE_RANGE_WEEKDAYS,ABSENCE_RANGE_ALL),
                state="readonly"
            ).grid(row=5,column=1,sticky="ew",pady=5)
            core.ttk.Checkbutton(body,text="Замінювати існуючий ручний запис, якщо в ньому немає фактичних годин",variable=replace).grid(row=6,column=0,columnspan=3,sticky="w",pady=5)
            code_label=core.tk.StringVar()
            core.ttk.Label(body,textvariable=code_label,foreground="gray").grid(row=7,column=0,columnspan=3,sticky="w",pady=(0,5))

            tree=core.ttk.Treeview(body,columns=("date","before","action"),show="headings")
            for k,l,w in (("date","Дата",100),("before","Було",520),("action","Результат",250)):
                tree.heading(k,text=l); tree.column(k,width=w,anchor="w")
            sy=core.ttk.Scrollbar(body,orient="vertical",command=tree.yview); tree.configure(yscrollcommand=sy.set)
            tree.grid(row=9,column=0,columnspan=2,sticky="nsew"); sy.grid(row=9,column=2,sticky="ns")

            def selected_period():
                emp=employees.get(employee_var.get())
                if not emp: raise ValueError("Виберіть працівника.")
                a=datetime.strptime(start_var.get().strip(),"%d.%m.%Y").date()
                b=datetime.strptime(end_var.get().strip(),"%d.%m.%Y").date()
                if b<a: raise ValueError("Кінцева дата раніше початкової.")
                return emp,[a+timedelta(days=i) for i in range((b-a).days+1)]

            def evaluate(show_error=True):
                try: emp,dates=selected_period()
                except Exception as exc:
                    if show_error: core.messagebox.showerror("Відсутність",str(exc),parent=win)
                    return None,[]
                con=core.db(); rows=[]
                for d in dates:
                    if not core.employee_employed_on(emp,d):
                        rows.append((d,"поза періодом роботи","Пропустити")); continue
                    driver_plan=core._driver_plan_minutes_for_day(con,emp["driver_id"],d)
                    shift_plan,_shift_actual,_shift_found=core._employee_shift_minutes_for_day(con,emp["id"],d)
                    current=original_employee_day_time(con,emp["id"],d)
                    regime_norm, regime = day_norm_minutes(con,emp["id"],d)
                    fixed_regime_norm = 0 if regime.regime_type == REGIME_SUMMARIZED else regime_norm
                    automatic_plan=max(
                        int(driver_plan+shift_plan),
                        int(current["planned_minutes"] or 0),
                        int(fixed_regime_norm or 0),
                    )
                    if fill_mode.get()==ABSENCE_RANGE_WEEKDAYS and d.weekday()>=5:
                        rows.append((d,"вихідний день","Поза схемою")); continue
                    if fill_mode.get()==ABSENCE_RANGE_PLANNED and automatic_plan<=0:
                        rows.append((d,"немає робочого плану","Немає робочого плану — пропустити")); continue
                    entry=con.execute("SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",(emp["id"],d.isoformat())).fetchone()
                    if current["actual_minutes"] not in (None,0):
                        rows.append((d,f"{current['day_type']}; факт {core.minutes_hhmm(current['actual_minutes'])}","Є факт — ручне рішення")); continue
                    if entry and not replace.get():
                        rows.append((d,f"{entry['day_type']} — {entry['notes'] or ''}","Вже є ручний запис — пропустити")); continue
                    before=f"{current['day_type']}; план {core.minutes_hhmm(current['planned_minutes'])}"
                    rows.append((d,before,"Замінити ручний запис" if entry else "Додати відсутність"))
                con.close(); return (emp,dates),rows

            def preview(_event=None):
                code,num,_=p5_code(dtype.get()); code_label.set(f"Код П-5: {code or '—'} / {num or '—'}")
                for x in tree.get_children(): tree.delete(x)
                _plan,rows=evaluate(show_error=False)
                for d,before,action in rows: tree.insert("","end",values=(d.strftime("%d.%m.%Y"),before,action))

            def apply():
                plan,rows=evaluate()
                if not plan: return
                writable=[x for x in rows if x[2] in ("Додати відсутність","Замінити ручний запис")]
                if not writable:
                    core.messagebox.showinfo("Відсутність","Немає дат для запису.",parent=win); return
                if not core.messagebox.askyesno("Відсутність",f"Записати «{dtype.get()}» на {len(writable)} дн.?",parent=win): return
                emp,_dates=plan; con=core.db(); now=datetime.now().isoformat(timespec="seconds"); added=0
                for d,_before,action in rows:
                    if action not in ("Додати відсутність","Замінити ручний запис"): continue
                    driver_plan=core._driver_plan_minutes_for_day(con,emp["driver_id"],d)
                    shift_plan,_shift_actual,_shift_found=core._employee_shift_minutes_for_day(con,emp["id"],d)
                    current=original_employee_day_time(con,emp["id"],d)
                    regime_norm, regime = day_norm_minutes(con,emp["id"],d)
                    fixed_regime_norm = 0 if regime.regime_type == REGIME_SUMMARIZED else regime_norm
                    automatic_plan=max(
                        int(driver_plan+shift_plan),
                        int(current["planned_minutes"] or 0),
                        int(fixed_regime_norm or 0),
                    )
                    if fill_mode.get()==ABSENCE_RANGE_WEEKDAYS and d.weekday()>=5: continue
                    if fill_mode.get()==ABSENCE_RANGE_PLANNED and automatic_plan<=0: continue
                    if current["actual_minutes"] not in (None,0): continue
                    entry=con.execute("SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",(emp["id"],d.isoformat())).fetchone()
                    if entry and entry["actual_hours"] not in (None,0): continue
                    if entry and not replace.get(): continue
                    note_text=notes.get().strip()
                    con.execute("""INSERT INTO employee_time_entries(employee_id,work_date,day_type,planned_hours,actual_hours,notes,created_at,updated_at)
                                   VALUES(?,?,?,0,NULL,?,?,?)
                                   ON CONFLICT(employee_id,work_date) DO UPDATE SET
                                     day_type=excluded.day_type,planned_hours=0,
                                     actual_hours=employee_time_entries.actual_hours,
                                     notes=excluded.notes,updated_at=excluded.updated_at
                                   WHERE employee_time_entries.actual_hours IS NULL OR employee_time_entries.actual_hours=0""",
                                (emp["id"],d.isoformat(),dtype.get(),note_text,now,now))
                    added+=1
                con.commit(); con.close(); preview()
                core.messagebox.showinfo("Відсутність",f"Записано днів: {added}. Робочі графіки фізично не видалялися.",parent=win)

            btn=core.ttk.Frame(body); btn.grid(row=8,column=0,columnspan=3,sticky="ew",pady=5)
            core.ttk.Button(btn,text="Переглянути",command=preview).pack(side="left",padx=3)
            core.ttk.Button(btn,text="Застосувати",command=apply).pack(side="left",padx=3)
            dtype.trace_add("write",lambda *_args:preview())
            fill_mode.trace_add("write",lambda *_args:preview())
            preview()

        def _duty_staff_for_interval(self, start_dt, end_dt, location="", con=None):
            """Лікар/механік для шляхівки з урахуванням табельної відсутності."""
            own = con is None
            if own:
                con = core.db()
            from_date=(start_dt.date()-timedelta(days=7)).isoformat()
            rows=con.execute(
                """SELECT sh.*,e.last_name||' '||e.first_name||
                          CASE WHEN COALESCE(e.middle_name,'')<>'' THEN ' '||e.middle_name ELSE '' END full_name
                   FROM employee_shifts sh
                   JOIN employees e ON e.id=sh.employee_id
                   WHERE sh.work_date BETWEEN ? AND ? AND e.active=1
                     AND sh.role IN ('Лікар','Механік')
                   ORDER BY sh.work_date,sh.start_time""",
                (from_date,end_dt.date().isoformat()),
            ).fetchall()
            result={"doctor_1":"","doctor_2":"","mechanic_1":"","mechanic_2":""}
            ranked=[]
            for row in rows:
                base=datetime.strptime(row["work_date"],"%Y-%m-%d")
                row_start=base+timedelta(minutes=parse_clock(row["start_time"]))
                row_end=base+timedelta(days=int(row["end_day_offset"] or 0),minutes=parse_clock(row["end_time"]))
                if row_end <= start_dt or row_start >= end_dt:
                    continue
                # Any absence day touched by the staffing interval suppresses
                # this assignment operationally, while the historical shift remains.
                cursor=row_start.date()
                unavailable=False
                while cursor <= row_end.date():
                    entry=con.execute(
                        "SELECT day_type FROM employee_time_entries WHERE employee_id=? AND work_date=?",
                        (row["employee_id"],cursor.isoformat()),
                    ).fetchone()
                    if entry and str(entry["day_type"] or "") in NONWORK_OVERRIDE_TYPES:
                        unavailable=True
                        break
                    cursor += timedelta(days=1)
                if unavailable:
                    continue
                exact_location=1 if location and (row["location"] or "").strip().casefold()==location.strip().casefold() else 0
                ranked.append((exact_location,row_start,row))
            if own:
                con.close()
            for _match,_start,row in sorted(ranked,key=lambda x:(x[0],x[1]),reverse=True):
                prefix="doctor" if row["role"]=="Лікар" else "mechanic"
                key=f"{prefix}_{row['shift_no']}"
                if not result[key]:
                    result[key]=row["full_name"]
            return result

        def refresh_month(self):
            """Legacy driver timesheet with personnel absence overlay."""
            super().refresh_month()
            tree = getattr(self, "work_tree", None)
            driver_id = getattr(self, "driver_id", None)
            if not widget_alive(tree) or not driver_id:
                return
            con = core.db()
            employee = con.execute(
                "SELECT id FROM employees WHERE driver_id=? ORDER BY active DESC,id LIMIT 1",
                (driver_id,),
            ).fetchone()
            if employee is None:
                con.close()
                return
            entries = {
                row["work_date"]: row
                for row in con.execute(
                    """SELECT * FROM employee_time_entries
                        WHERE employee_id=? AND substr(work_date,1,7)=?""",
                    (
                        employee["id"],
                        f"{int(self.year_var.get()):04d}-{int(self.month_var.get()):02d}",
                    ),
                ).fetchall()
            }
            con.close()
            for item in tree.get_children():
                values = list(tree.item(item, "values"))
                if len(values) < 13:
                    continue
                try:
                    day = datetime.strptime(values[1], "%d.%m.%Y").date()
                except Exception:
                    continue
                entry = entries.get(day.isoformat())
                if not entry or str(entry["day_type"] or "") not in NONWORK_OVERRIDE_TYPES:
                    continue
                values[3] = entry["day_type"]
                values[4] = "План збережено; день позначено як відсутність"
                values[5] = ""
                values[6] = "0:00"
                values[7] = "0:00"
                values[8] = "0:00"
                note = str(entry["notes"] or "").strip()
                values[11] = (
                    f"Відсутність: {note}" if note else "Відсутність із табеля персоналу"
                )
                if len(values) > 12:
                    values[12] = "ВІДСУТНІСТЬ"
                tree.item(item, values=values)

        def _open_last_p5(self, kind):
            path = (
                self.personnel_last_p5_xlsx
                if kind == "xlsx"
                else self.personnel_last_p5_pdf
            )
            if not path or not Path(path).exists():
                core.messagebox.showinfo(
                    "Табель П-5",
                    "Ще немає сформованого файла цього типу.",
                    parent=self,
                )
                return
            try:
                core.open_external(path)
            except Exception as exc:
                core.messagebox.showerror(
                    "Табель П-5",
                    f"Не вдалося відкрити файл:\n{exc}",
                    parent=self,
                )

        def _save_p5(self, kind):
            try:
                month=int(self.personnel_report_month.get()); year=int(self.personnel_report_year.get())
                if not 1<=month<=12: raise ValueError
                form_date=datetime.strptime(self.personnel_report_form_date.get().strip(),"%d.%m.%Y").date()
            except Exception:
                core.messagebox.showerror("Табель П-5","Перевірте місяць, рік і дату заповнення.",parent=self); return
            department=self.personnel_report_department.get().strip()
            edrpou=self.personnel_report_edrpou.get().strip()
            core.set_setting("personnel_report_department",department)
            core.set_setting("company_edrpou",edrpou)
            preview=collect_p5_data(
                core,year,month,self.personnel_report_active.get(),
                use_plan_when_fact_missing=False
            )
            use_plan=False
            if preview["missing_fact_total"]>0:
                decision=core.messagebox.askyesnocancel(
                    "Табель П-5 — план замість факту?",
                    (
                        f"Знайдено {preview['missing_fact_total']} дн., де є план робочого часу, "
                        "але немає внесеного факту.\n\n"
                        "Так — підставити планові години замість відсутнього факту у цьому П-5.\n"
                        "Ні — сформувати П-5 лише за внесеним фактом; такі дні залишаться незаповненими.\n"
                        "Скасувати — не формувати документ.\n\n"
                        "Якщо план буде підставлено, Taxo додасть до документа явну примітку."
                    ),
                    parent=self,
                )
                if decision is None:
                    return
                use_plan=bool(decision)

            suffix=".xlsx" if kind=="xlsx" else ".pdf"
            filename=f"Табель_П5_{year}_{month:02d}{suffix}"
            path=core.filedialog.asksaveasfilename(
                parent=self,title="Зберегти табель П-5",initialdir=str(core.OUTPUT_DIR),
                initialfile=filename,defaultextension=suffix,
                filetypes=[("Excel","*.xlsx")] if kind=="xlsx" else [("PDF","*.pdf")],
            )
            if not path: return
            writer=(
                (lambda out:export_p5_xlsx(
                    core,year,month,out,self.personnel_report_active.get(),
                    form_date,department,edrpou,use_plan
                ))
                if kind=="xlsx" else
                (lambda out:export_p5_pdf(
                    core,year,month,out,self.personnel_report_active.get(),
                    form_date,department,edrpou,use_plan
                ))
            )
            actual=core.write_output_file(writer,path,parent=self,kind="Excel табеля П-5" if kind=="xlsx" else "PDF табеля П-5",error_title="Табель П-5")
            if actual is not None:
                if kind == "xlsx":
                    self.personnel_last_p5_xlsx = Path(actual)
                else:
                    self.personnel_last_p5_pdf = Path(actual)
                if core.messagebox.askyesno(
                    "Табель П-5",
                    f"Файл створено:\n{actual}\n\nВідкрити зараз?",
                    parent=self,
                ):
                    try:
                        core.open_external(actual)
                    except Exception as exc:
                        core.messagebox.showerror(
                            "Табель П-5",
                            f"Файл створено, але не вдалося його відкрити:\n{exc}",
                            parent=self,
                        )

    PersonnelApp.__name__="App"
    PersonnelApp.__qualname__="App"
    core.App=PersonnelApp
    core._TAXO_PERSONNEL_R3_INSTALLED=True
    return PersonnelApp
