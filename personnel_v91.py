# -*- coding: utf-8 -*-
"""Taxo 9.1 candidate r3 — окремий модуль «Персонал».

Модуль:
- додає окремий верхній розділ «Персонал»;
- залишає стару вкладку водіїв як «Водії»;
- додає загальне масове планування робочих змін для будь-якого працівника;
- додає масове внесення відсутностей/відпусток у табель;
- надає PDF/XLSX табеля у форматі, наближеному до П-5 за наданим зразком;
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


APP_VERSION = "9.1 candidate r6"
WINDOW_TITLE = f"Taxo {APP_VERSION} — персонал, водії, графіки та шляхівки"

ABSENCE_RANGE_PLANNED = "Лише дні з робочим планом"
ABSENCE_RANGE_WEEKDAYS = "Пн–Пт"
ABSENCE_RANGE_ALL = "Усі календарні дні"

# Типи, які в ручному табелі перекривають автоматичний робочий план.
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

# Повна таблиця умовних позначень із наданого користувачем зразка П-5.
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
    if core.hours_value_to_minutes(row["work_hours"] or 0) > 0:
        return core.hours_value_to_minutes(row["work_hours"] or 0)

    segs = con.execute(
        """SELECT * FROM route_segments
            WHERE route_id=?
            ORDER BY segment_no""",
        (row["route_id"],),
    ).fetchall()
    total = 0
    for seg in segs:
        ws = (seg["work_start_time"] or seg["start_time"] or "").strip()
        we = (seg["work_end_time"] or seg["end_time"] or "").strip()
        if ws and we:
            try:
                total += int(core.duration_minutes(ws, we))
                continue
            except Exception:
                pass
        total += core.hours_value_to_minutes(seg["work_hours"] or 0)
    return int(total)


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

    Returns (intervals, unresolved_days).  An unresolved day means Taxo knows
    positive work duration but cannot place all of it on the clock.  Known
    intervals are still returned, so an actual overlap with a known driving or
    work interval is blocked while non-overlapping extra work is only warned.
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
    intervals = []
    unresolved = []

    def span_minutes(span):
        return int((span[1] - span[0]).total_seconds() // 60)

    for row in rows:
        base = date.fromisoformat(row["work_date"])
        row_keys = set(row.keys()) if hasattr(row, "keys") else set()
        planned_total = core.hours_value_to_minutes(
            row["work_hours"] if "work_hours" in row_keys else 0
        )

        segs = con.execute(
            """SELECT * FROM work_segments
                WHERE worklog_id=? ORDER BY segment_no""",
            (row["id"],),
        ).fetchall()

        if segs:
            known_minutes = 0
            expected_minutes = 0
            for seg in segs:
                seg_keys = set(seg.keys()) if hasattr(seg, "keys") else set()
                seg_expected = core.hours_value_to_minutes(
                    seg["work_hours"] if "work_hours" in seg_keys else 0
                )
                expected_minutes += seg_expected

                # Exact work interval is best. Legacy driving interval is only
                # a known busy interval, not proof that the entire work day
                # starts/ends there.
                wstart = (seg["work_start_time"] if "work_start_time" in seg_keys else "") or ""
                wend = (seg["work_end_time"] if "work_end_time" in seg_keys else "") or ""
                span = _interval_datetimes(base, wstart, wend)
                exact_work = bool(span)
                if not span:
                    dstart = (seg["start_time"] if "start_time" in seg_keys else "") or ""
                    dend = (seg["end_time"] if "end_time" in seg_keys else "") or ""
                    span = _interval_datetimes(base, dstart, dend)
                if span:
                    intervals.append((span[0], span[1], row, seg))
                    known_minutes += span_minutes(span)
                    if not exact_work and seg_expected > span_minutes(span):
                        # Part of the segment's work time exists outside the
                        # known driving interval but has no exact placement.
                        unresolved.append(base)

            expected = expected_minutes or planned_total
            if expected > known_minutes and base not in unresolved:
                unresolved.append(base)
            elif expected > 0 and known_minutes == 0 and base not in unresolved:
                unresolved.append(base)
            continue

        # No copied work_segments: prefer exact daily work boundaries.
        wstart = (row["work_start_time"] if "work_start_time" in row_keys else "") or ""
        wend = (row["work_end_time"] if "work_end_time" in row_keys else "") or ""
        span = _interval_datetimes(base, wstart, wend)
        if span:
            intervals.append((span[0], span[1], row, None))
            if planned_total > span_minutes(span):
                unresolved.append(base)
            continue

        # Older/incomplete worklog can have route_id only. Use exact route
        # work boundaries where available. If only driving boundaries exist,
        # they are known busy intervals but the remaining work duration stays
        # unresolved.
        route_id = row["route_id"] if "route_id" in row_keys else None
        if route_id:
            route_segs = con.execute(
                """SELECT * FROM route_segments
                    WHERE route_id=? ORDER BY segment_no""",
                (route_id,),
            ).fetchall()
            known_minutes = 0
            expected_minutes = 0
            route_found = False
            route_unresolved = False
            for seg in route_segs:
                seg_keys = set(seg.keys()) if hasattr(seg, "keys") else set()
                seg_expected = core.hours_value_to_minutes(
                    seg["work_hours"] if "work_hours" in seg_keys else 0
                )
                expected_minutes += seg_expected
                rws = (seg["work_start_time"] if "work_start_time" in seg_keys else "") or ""
                rwe = (seg["work_end_time"] if "work_end_time" in seg_keys else "") or ""
                rspan = _interval_datetimes(base, rws, rwe)
                exact_work = bool(rspan)
                if not rspan:
                    rds = (seg["start_time"] if "start_time" in seg_keys else "") or ""
                    rde = (seg["end_time"] if "end_time" in seg_keys else "") or ""
                    rspan = _interval_datetimes(base, rds, rde)
                if rspan:
                    intervals.append((rspan[0], rspan[1], row, seg))
                    route_found = True
                    known_minutes += span_minutes(rspan)
                    if not exact_work and seg_expected > span_minutes(rspan):
                        route_unresolved = True

            expected = expected_minutes or planned_total
            if route_found:
                if route_unresolved or expected > known_minutes:
                    unresolved.append(base)
                continue

        # Last resort: legacy daily start/end is known driving/busy time.  It
        # is not expanded to match a duration such as "8 hours".
        dstart = (row["start_time"] if "start_time" in row_keys else "") or ""
        dend = (row["end_time"] if "end_time" in row_keys else "") or ""
        span = _interval_datetimes(base, dstart, dend)
        if span:
            intervals.append((span[0], span[1], row, None))
            if planned_total > span_minutes(span):
                unresolved.append(base)
            continue

        if planned_total > 0:
            unresolved.append(base)

    # Keep warning dates stable and unique.
    unresolved = list(dict.fromkeys(unresolved))
    return intervals, unresolved


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


def collect_p5_data(core, year, month, active_only=True):
    y, m = int(year), int(month)
    days = core.month_dates(y, m)
    employees = _all_employee_rows(core, active_only=active_only)
    con = core.db()
    company = con.execute("SELECT * FROM company WHERE id=1").fetchone()
    out = []
    for employee in employees:
        if not any(core.employee_employed_on(employee, d) for d in days):
            continue
        cells = []
        work_days = 0
        work_minutes = 0
        missing_fact = 0
        absence_counts = {label: 0 for label, _codes in P5_ABSENCE_GROUPS}
        overtime_minutes = 0
        for d in days:
            if not core.employee_employed_on(employee, d):
                cells.append({"code": "", "hours": None, "day_type": "—", "missing": False})
                continue
            row = core.employee_day_time(con, employee["id"], d)
            dtype = str(row["day_type"] or "")
            code, numeric, _label = p5_code(dtype)
            actual = row["actual_minutes"]
            planned = row["planned_minutes"]
            if dtype in NONWORK_OVERRIDE_TYPES:
                hours = actual if actual not in (None, 0) else None
                # A non-zero actual on an absence day is deliberately visible as conflict.
                if hours:
                    missing_fact += 1
            elif actual is not None and actual > 0:
                hours = int(actual)
                code = "РВ" if d.weekday() >= 5 else "Р"
                numeric = "06" if d.weekday() >= 5 else "01"
                work_days += 1
                work_minutes += int(actual)
            elif planned > 0:
                # Для експлуатаційного П-5 план із графіка/маршруту є
                # робочим джерелом до появи факту. Факт, коли він з'явиться,
                # автоматично має пріоритет.
                hours = int(planned)
                code = "РВ" if d.weekday() >= 5 else "Р"
                numeric = "06" if d.weekday() >= 5 else "01"
                work_days += 1
                work_minutes += int(planned)
                missing_fact += 1
            else:
                hours = None
                # Ordinary weekend / empty day is not annual-leave code «В».
                code = "" if dtype in ("Вихідний", "Відпочинок", "") else code

            if numeric:
                for label, codes in P5_ABSENCE_GROUPS:
                    if numeric in codes:
                        absence_counts[label] += 1
                        break

            if employee["driver_id"]:
                wl = con.execute(
                    "SELECT overtime_hours FROM worklog WHERE driver_id=? AND work_date=?",
                    (employee["driver_id"], d.isoformat()),
                ).fetchone()
                if wl:
                    overtime_minutes += core.hours_value_to_minutes(wl["overtime_hours"] or 0)

            cells.append({
                "code": code,
                "numeric": numeric,
                "hours": hours,
                "day_type": dtype,
                "missing": bool(actual is None and planned > 0 and dtype not in NONWORK_OVERRIDE_TYPES),
            })
        out.append({
            "employee_id": employee["id"],
            "personnel_no": employee["personnel_no"] or "",
            "name": core.employee_name(employee),
            "position": employee["position"] or employee["roles"] or "",
            "gender": "",  # у поточній БД поле не ведеться
            "cells": cells,
            "work_days": work_days,
            "work_minutes": work_minutes,
            "overtime_minutes": overtime_minutes,
            "night_minutes": 0,
            "holiday_minutes": 0,
            "absence_counts": absence_counts,
            "missing_fact": missing_fact,
            "tariff_rate": "",  # у поточній БД поле не ведеться
        })
    con.close()
    return {"year": y, "month": m, "days": days, "employees": out, "company": company}


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


def export_p5_pdf(core, year, month, out_path, active_only=True, form_date=None, department="", edrpou=""):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics

    data = collect_p5_data(core, year, month, active_only)
    page_w, page_h = landscape(A4)
    c = canvas.Canvas(str(out_path), pagesize=(page_w, page_h))
    font = _report_font(core)
    bold = font
    company = (data["company"]["name"] if data["company"] else "") or ""

    def text(x, y, value, size=6, align="left", font_name=None):
        c.setFont(font_name or font, size)
        s = str(value or "")
        if align == "center":
            c.drawCentredString(x, y, s)
        elif align == "right":
            c.drawRightString(x, y, s)
        else:
            c.drawString(x, y, s)

    # Page 1: header + legend
    form_date = form_date or date.today()
    first = data["days"][0].strftime("%d.%m.%Y")
    last = data["days"][-1].strftime("%d.%m.%Y")
    text(24, page_h - 22, company, 9.5, "left")
    if department:
        text(24, page_h - 34, department, 6.2, "left")
    text(24, page_h - 46, f"Ідентифікаційний код ЄДРПОУ: {edrpou or ''}", 6.2, "left")
    text(page_w / 2, page_h - 58, "ТАБЕЛЬ ОБЛІКУ ВИКОРИСТАННЯ РОБОЧОГО ЧАСУ", 12, "center")
    text(page_w - 24, page_h - 20, "Типова форма № П-5", 6.5, "right")
    text(page_w - 24, page_h - 31, "ЗАТВЕРДЖЕНО", 5.8, "right")
    text(page_w - 24, page_h - 42, "Наказ Держкомстату України 05.12.2008 № 489", 5.5, "right")
    text(page_w - 24, page_h - 55, f"Дата заповнення: {form_date.strftime('%d.%m.%Y')}", 6.2, "right")
    text(page_w - 24, page_h - 67, f"Звітний період: {first} — {last}", 6.2, "right")

    legend = [(letter, numeric, label) for label, letter, numeric in P5_LEGEND]
    col_gap = 20
    x0 = 24
    total_w = page_w - 48
    col_w = (total_w - col_gap) / 2
    row_h = 17
    top = page_h - 92
    from reportlab.pdfbase.pdfmetrics import stringWidth

    def wrapped_lines(value, size, max_w):
        words = str(value).split()
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if not cur or stringWidth(trial, font, size) <= max_w:
                cur = trial
            else:
                lines.append(cur); cur = w
        if cur: lines.append(cur)
        return lines or [""]

    half = (len(legend) + 1) // 2
    for col in range(2):
        subset = legend[col * half:(col + 1) * half]
        x = x0 + col * (col_w + col_gap)
        y = top
        c.setLineWidth(.5)
        for letter, numeric, label in subset:
            lines = wrapped_lines(label, 5.2, col_w - 58)
            h = max(row_h, 7 + len(lines) * 6)
            c.rect(x, y - h, col_w, h)
            c.line(x + col_w - 56, y - h, x + col_w - 56, y)
            c.line(x + col_w - 28, y - h, x + col_w - 28, y)
            for i, ln in enumerate(lines):
                text(x + 3, y - 8 - i * 6, ln, 5.2)
            text(x + col_w - 42, y - h / 2 - 2, letter, 6.5, "center")
            text(x + col_w - 14, y - h / 2 - 2, numeric, 6.5, "center")
            y -= h
    c.showPage()

    # Page 2+: timesheet table
    employees = data["employees"]
    per_page = 18
    chunks = [employees[i:i + per_page] for i in range(0, len(employees), per_page)] or [[]]
    for page_index, chunk in enumerate(chunks):
        margin = 12
        top_y = page_h - 16
        text(margin, top_y, company, 7)
        text(page_w / 2, top_y, f"ТАБЕЛЬ — {core.month_name_ua(data['month']).upper()} {data['year']}", 9, "center")
        text(page_w - margin, top_y, f"Дата заповнення: {form_date.strftime('%d.%m.%Y')}", 5, "right")
        top_y -= 16

        fixed = [18, 49, 18, 98]
        day_w = 10.0
        summary = [22, 28, 22, 22, 22]
        abs_w = [13.2] * len(P5_ABSENCE_GROUPS)
        widths = fixed + [day_w] * len(data["days"]) + summary + abs_w + [30]
        table_w = sum(widths)
        scale = min(1.0, (page_w - 2 * margin) / table_w)
        widths = [w * scale for w in widths]
        header_h = 48
        row_h = 24

        x_positions = [margin]
        for w in widths:
            x_positions.append(x_positions[-1] + w)
        y_header_bottom = top_y - header_h
        c.setStrokeColor(colors.black)
        c.setLineWidth(.35)

        labels = ["№", "Таб. №", "Ст.", "ПІБ, посада"]
        for i, label in enumerate(labels):
            c.rect(x_positions[i], y_header_bottom, widths[i], header_h)
            text(x_positions[i] + widths[i]/2, y_header_bottom + header_h/2 - 2, label, 4.6, "center")

        base = len(fixed)
        for j, d in enumerate(data["days"]):
            idx = base + j
            c.rect(x_positions[idx], y_header_bottom, widths[idx], header_h)
            text(x_positions[idx] + widths[idx]/2, y_header_bottom + 28, f"{d.day:02d}", 4.5, "center")
            text(x_positions[idx] + widths[idx]/2, y_header_bottom + 17, WEEKDAY_NAMES[d.weekday()], 4.1, "center")

        idx = base + len(data["days"])
        sum_labels = ["дні", "год.", "НУ", "РН", "РВ"]
        for label, w in zip(sum_labels, summary):
            c.rect(x_positions[idx], y_header_bottom, widths[idx], header_h)
            text(x_positions[idx] + widths[idx]/2, y_header_bottom + 20, label, 4.2, "center")
            idx += 1
        for label, _codes in P5_ABSENCE_GROUPS:
            c.rect(x_positions[idx], y_header_bottom, widths[idx], header_h)
            c.saveState()
            c.translate(x_positions[idx] + widths[idx]/2 + 1, y_header_bottom + 3)
            c.rotate(90)
            c.setFont(font, 3.8)
            c.drawString(0, 0, label)
            c.restoreState()
            idx += 1
        c.rect(x_positions[idx], y_header_bottom, widths[idx], header_h)
        text(x_positions[idx] + widths[idx]/2, y_header_bottom + 17, "Оклад", 4.2, "center")

        y = y_header_bottom
        page_work_days = page_work_min = 0
        for n, emp in enumerate(chunk, start=page_index * per_page + 1):
            y -= row_h
            values = [n, emp["personnel_no"], emp["gender"], f"{emp['name']}\n{emp['position']}"]
            for i, value in enumerate(values):
                c.rect(x_positions[i], y, widths[i], row_h)
                if i == 3:
                    parts = str(value).split("\n")
                    text(x_positions[i] + 2, y + 14, parts[0], 4.7)
                    if len(parts) > 1:
                        text(x_positions[i] + 2, y + 6, parts[1], 4.0)
                else:
                    text(x_positions[i] + widths[i]/2, y + 9, value, 4.7, "center")

            for j, cell in enumerate(emp["cells"]):
                pos = base + j
                c.rect(x_positions[pos], y, widths[pos], row_h)
                if cell["code"]:
                    text(x_positions[pos] + widths[pos]/2, y + 14, cell["code"], 4.5, "center")
                if cell["hours"] is not None:
                    hours = core.minutes_hhmm(cell["hours"]).replace(":00", "")
                    text(x_positions[pos] + widths[pos]/2, y + 5, hours, 4.5, "center")
            pos = base + len(data["days"])
            summary_vals = [
                emp["work_days"],
                core.minutes_hhmm(emp["work_minutes"]),
                core.minutes_hhmm(emp["overtime_minutes"]) if emp["overtime_minutes"] else "",
                "",
                "",
            ]
            for value in summary_vals:
                c.rect(x_positions[pos], y, widths[pos], row_h)
                text(x_positions[pos] + widths[pos]/2, y + 9, value, 4.4, "center"); pos += 1
            for label, _codes in P5_ABSENCE_GROUPS:
                c.rect(x_positions[pos], y, widths[pos], row_h)
                value = emp["absence_counts"][label]
                text(x_positions[pos] + widths[pos]/2, y + 9, value if value else "", 4.4, "center"); pos += 1
            c.rect(x_positions[pos], y, widths[pos], row_h)
            text(x_positions[pos] + widths[pos]/2, y + 9, emp["tariff_rate"], 4.2, "center")
            page_work_days += emp["work_days"]
            page_work_min += emp["work_minutes"]

        y -= row_h
        c.rect(margin, y, sum(widths[:4]), row_h)
        text(margin + 2, y + 9, "Всього на сторінці", 5.0)
        pos = 4
        # Blank day totals: report totals are shown in summary columns.
        for _ in data["days"]:
            c.rect(x_positions[pos], y, widths[pos], row_h); pos += 1
        totals = [page_work_days, core.minutes_hhmm(page_work_min), "", "", ""]
        for value in totals:
            c.rect(x_positions[pos], y, widths[pos], row_h)
            text(x_positions[pos] + widths[pos]/2, y + 9, value, 4.5, "center"); pos += 1
        while pos < len(widths):
            c.rect(x_positions[pos], y, widths[pos], row_h); pos += 1

        text(margin, 18, "Якщо факт ще не внесено, П-5 використовує планові години з графіка/маршруту; після внесення факту він має пріоритет. Поля статі та окладу поки не ведуться в Taxo.", 4.8)
        c.showPage()

    c.save()
    return data


def export_p5_xlsx(core, year, month, out_path, active_only=True, form_date=None, department="", edrpou=""):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    data = collect_p5_data(core, year, month, active_only)
    form_date = form_date or date.today()
    wb = Workbook()
    ws = wb.active
    ws.title = "Табель П-5"
    legend_ws = wb.create_sheet("Умовні позначення")
    company = (data["company"]["name"] if data["company"] else "") or ""

    thin = Side(style="thin", color="333333")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    header_fill = PatternFill("solid", fgColor="D9E6F2")
    conflict_fill = PatternFill("solid", fgColor="FFF2CC")

    day_start_col = 5
    summary_start = day_start_col + len(data["days"])
    abs_start = summary_start + 5
    last_col = abs_start + len(P5_ABSENCE_GROUPS)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_col)
    ws.cell(1, 1, company)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=last_col)
    ws.cell(2, 1, f"ТАБЕЛЬ ОБЛІКУ ВИКОРИСТАННЯ РОБОЧОГО ЧАСУ — {core.month_name_ua(data['month']).upper()} {data['year']}")
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=last_col)
    ws.cell(3, 1, (
        f"Структурний підрозділ: {department or '—'}    "
        f"ЄДРПОУ: {edrpou or '—'}    "
        f"Дата заповнення: {form_date.strftime('%d.%m.%Y')}    "
        f"Звітний період: {data['days'][0].strftime('%d.%m.%Y')} — {data['days'][-1].strftime('%d.%m.%Y')}"
    ))
    for row in (1, 2, 3):
        ws.cell(row, 1).font = Font(bold=(row != 3), size=13 if row == 2 else 11 if row == 1 else 8)
        ws.cell(row, 1).alignment = Alignment(horizontal="center", wrap_text=True)

    fixed_headers = ["№", "Табельний номер", "Стать", "ПІБ, посада"]
    for col, label in enumerate(fixed_headers, 1):
        c = ws.cell(4, col, label); c.font = Font(bold=True); c.fill = header_fill; c.border = border
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for j, d in enumerate(data["days"], day_start_col):
        c = ws.cell(4, j, f"{d.day:02d}\n{WEEKDAY_NAMES[d.weekday()]}")
        c.font = Font(bold=True, size=8); c.fill = header_fill; c.border = border
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    summary_headers = ["Роб. дні", "Години", "Надур.", "Нічні", "Вих./святк."]
    for off, label in enumerate(summary_headers):
        c = ws.cell(4, summary_start + off, label); c.font = Font(bold=True, size=8); c.fill = header_fill; c.border = border
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for off, (label, _codes) in enumerate(P5_ABSENCE_GROUPS):
        c = ws.cell(4, abs_start + off, label); c.font = Font(bold=True, size=7); c.fill = header_fill; c.border = border
        c.alignment = Alignment(horizontal="center", vertical="center", text_rotation=90, wrap_text=True)
    c = ws.cell(4, last_col, "Оклад / тарифна ставка")
    c.font = Font(bold=True, size=8); c.fill = header_fill; c.border = border
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    row = 5
    for seq, emp in enumerate(data["employees"], 1):
        code_row = row
        hour_row = row + 1
        for col, value in enumerate([seq, emp["personnel_no"], emp["gender"], f"{emp['name']}\n{emp['position']}"], 1):
            ws.merge_cells(start_row=code_row, start_column=col, end_row=hour_row, end_column=col)
            c = ws.cell(code_row, col, value); c.border = border
            c.alignment = Alignment(horizontal="left" if col == 4 else "center", vertical="center", wrap_text=True)

        for j, cell in enumerate(emp["cells"], day_start_col):
            cc = ws.cell(code_row, j, cell["code"])
            hc = ws.cell(hour_row, j, (cell["hours"] / 60.0) if cell["hours"] is not None else None)
            for cell_obj in (cc, hc):
                cell_obj.border = border
                cell_obj.alignment = Alignment(horizontal="center", vertical="center")
            if cell["missing"]:
                cc.fill = conflict_fill
        first_letter = get_column_letter(day_start_col)
        last_letter = get_column_letter(day_start_col + len(data["days"]) - 1)
        # Формули працюють на нижньому (годинному) рядку.
        ws.cell(code_row, summary_start, "дні")
        ws.cell(hour_row, summary_start, f"=COUNT({first_letter}{hour_row}:{last_letter}{hour_row})")
        ws.cell(code_row, summary_start + 1, "год.")
        ws.cell(hour_row, summary_start + 1, f"=SUM({first_letter}{hour_row}:{last_letter}{hour_row})")
        ws.cell(hour_row, summary_start + 2, emp["overtime_minutes"] / 60.0 if emp["overtime_minutes"] else None)
        ws.cell(hour_row, summary_start + 3, None)
        ws.cell(hour_row, summary_start + 4, None)
        for col in range(summary_start, summary_start + 5):
            for rr in (code_row, hour_row):
                ws.cell(rr, col).border = border
                ws.cell(rr, col).alignment = Alignment(horizontal="center", vertical="center")

        code_range = f"{first_letter}{code_row}:{last_letter}{code_row}"
        for off, (_label, codes) in enumerate(P5_ABSENCE_GROUPS):
            formula = "+".join(f'COUNTIF({code_range},"{letter}")' for dtype, (letter, num, _desc) in P5_CODES.items() if num in codes and letter)
            # Deduplicate repeated legacy aliases such as «Відпустка»/«Лікарняний».
            unique_letters = []
            for dtype, (letter, num, _desc) in P5_CODES.items():
                if num in codes and letter and letter not in unique_letters:
                    unique_letters.append(letter)
            formula = "+".join(f'COUNTIF({code_range},"{letter}")' for letter in unique_letters) or "0"
            ws.merge_cells(start_row=code_row, start_column=abs_start + off, end_row=hour_row, end_column=abs_start + off)
            cell = ws.cell(code_row, abs_start + off, f"={formula}")
            cell.border = border; cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.merge_cells(start_row=code_row, start_column=last_col, end_row=hour_row, end_column=last_col)
        ws.cell(code_row, last_col, emp["tariff_rate"]).border = border
        row += 2

    # Total row
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
    ws.cell(row, 1, "Всього")
    for col in range(1, last_col + 1):
        ws.cell(row, col).border = border
    ws.cell(row, summary_start, f"=SUM({get_column_letter(summary_start)}6:{get_column_letter(summary_start)}{row-1})")
    ws.cell(row, summary_start + 1, f"=SUM({get_column_letter(summary_start+1)}6:{get_column_letter(summary_start+1)}{row-1})")

    ws.column_dimensions["A"].width = 5
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 7
    ws.column_dimensions["D"].width = 30
    for col in range(day_start_col, day_start_col + len(data["days"])):
        ws.column_dimensions[get_column_letter(col)].width = 4.1
    for col in range(summary_start, last_col + 1):
        ws.column_dimensions[get_column_letter(col)].width = 7.5
    ws.row_dimensions[4].height = 72
    ws.freeze_panes = "E5"
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = "1:4"
    ws.print_area = f"A1:{get_column_letter(last_col)}{row}"

    legend_ws.merge_cells("A1:C1")
    legend_ws["A1"] = company
    legend_ws["A1"].font = Font(bold=True, size=11)
    legend_ws["A1"].alignment = Alignment(horizontal="center")
    legend_ws.merge_cells("A2:C2")
    legend_ws["A2"] = "ТАБЕЛЬ ОБЛІКУ ВИКОРИСТАННЯ РОБОЧОГО ЧАСУ — УМОВНІ ПОЗНАЧЕННЯ"
    legend_ws["A2"].font = Font(bold=True, size=12)
    legend_ws["A2"].alignment = Alignment(horizontal="center")
    legend_ws.merge_cells("A3:C3")
    legend_ws["A3"] = (
        f"Структурний підрозділ: {department or '—'}    ЄДРПОУ: {edrpou or '—'}    "
        f"Дата заповнення: {form_date.strftime('%d.%m.%Y')}"
    )
    legend_ws["A3"].alignment = Alignment(horizontal="center", wrap_text=True)
    legend_ws.append([])
    legend_ws.append([])
    legend_ws.cell(6,1,"Умовне позначення")
    legend_ws.cell(6,2,"Буквений код")
    legend_ws.cell(6,3,"Цифровий код")
    for label, letter, numeric in P5_LEGEND:
        legend_ws.append([label, letter, numeric])
    for row_cells in legend_ws.iter_rows(min_row=6):
        for c in row_cells:
            c.border = border; c.alignment = Alignment(vertical="top", wrap_text=True)
    for c in legend_ws[6]:
        c.font = Font(bold=True); c.fill = header_fill
    legend_ws.column_dimensions["A"].width = 85
    legend_ws.column_dimensions["B"].width = 16
    legend_ws.column_dimensions["C"].width = 16
    legend_ws.page_setup.orientation = "landscape"
    legend_ws.page_setup.paperSize = legend_ws.PAPERSIZE_A4
    legend_ws.page_setup.fitToWidth = 1
    legend_ws.sheet_properties.pageSetUpPr.fitToPage = True

    wb.save(str(out_path))
    return data


def install(core, base_app):
    if getattr(core, "_TAXO_PERSONNEL_R3_INSTALLED", False):
        return core.App

    original_employee_day_time = core.employee_day_time
    original_collect_monthly_work_balance = core.collect_monthly_work_balance

    def collect_monthly_work_balance_with_absence(year, month, active_only=True):
        data = original_collect_monthly_work_balance(year, month, active_only)
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
            book = core.ttk.Notebook(root)
            book.pack(fill="both", expand=True, padx=8, pady=8)
            overview = core.ttk.Frame(book)
            planning = core.ttk.Frame(book)
            timesheet = core.ttk.Frame(book)
            reports = core.ttk.Frame(book)
            book.add(overview, text="Реєстр")
            book.add(planning, text="Планування")
            book.add(timesheet, text="Табель")
            book.add(reports, text="Звіти")

            # Реєстр
            bar = core.ttk.Frame(overview, padding=8); bar.pack(fill="x")
            core.ttk.Button(bar, text="Відкрити картки працівників", command=self.show_employee_registry).pack(side="left", padx=3)
            core.ttk.Button(bar, text="Режим робочого часу…", command=self.show_employee_work_regime).pack(side="left", padx=(12,3))
            core.ttk.Button(bar, text="Тижневий баланс…", command=self.show_personnel_week_balance).pack(side="left", padx=3)
            core.ttk.Button(bar, text="Оновити", command=self._refresh_personnel_overview).pack(side="left", padx=3)
            frame = core.ttk.Frame(overview); frame.pack(fill="both", expand=True, padx=8, pady=(0,8))
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
            self._refresh_personnel_overview()

            # Планування
            panel = core.ttk.Frame(planning, padding=16); panel.pack(fill="x")
            core.ttk.Label(panel, text="Планування персоналу", font=("TkDefaultFont", 13, "bold")).pack(anchor="w")
            core.ttk.Label(
                panel,
                text="Робочі зміни плануються для будь-якого працівника. Відсутності вносяться інтервалом і перекривають автоматичний план у табелі, не видаляючи історичний графік.",
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
            core.ttk.Label(rpanel,text="Табель П-5 — за структурою наданого зразка: умовні позначення, 1–31 число, відпрацьований час і причини неявок.",foreground="gray",wraplength=980,justify="left").pack(anchor="w",pady=(12,8))
            b = core.ttk.Frame(rpanel); b.pack(fill="x")
            core.ttk.Button(b,text="Табель П-5 — PDF",command=lambda:self._save_p5("pdf")).pack(side="left",padx=(0,5))
            core.ttk.Button(b,text="Відкрити останній PDF",command=lambda:self._open_last_p5("pdf")).pack(side="left",padx=5)
            core.ttk.Button(b,text="Табель П-5 — Excel",command=lambda:self._save_p5("xlsx")).pack(side="left",padx=(16,5))
            core.ttk.Button(b,text="Відкрити останній Excel",command=lambda:self._open_last_p5("xlsx")).pack(side="left",padx=5)
            core.ttk.Button(b,text="Звичайний місячний табель",command=self.show_employee_timesheet).pack(side="left",padx=(16,5))

        def _refresh_personnel_overview(self):
            tree = getattr(self, "personnel_overview_tree", None)
            if not widget_alive(tree):
                return
            for item in tree.get_children(): tree.delete(item)
            con = core.db()
            try:
                for row in _all_employee_rows(core, active_only=False):
                    regime = latest_regime(con, row["id"])
                    regime_text = regime.label + ("" if regime.explicit else " (типово)")
                    tree.insert("", "end", iid=str(row["id"]), values=(
                        row["personnel_no"] or "",
                        core.employee_name(row),
                        row["position"] or "",
                        row["roles"] or "",
                        regime_text,
                        regime_hhmm(regime.weekly_norm_minutes),
                        core.fmt_date(row["employment_date"]),
                        "Працює" if row["active"] else "Звільнений",
                    ))
            finally:
                con.close()

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
                        con.execute(
                            """INSERT INTO employee_time_entries(
                                 employee_id,work_date,day_type,planned_hours,actual_hours,
                                 notes,created_at,updated_at
                               ) VALUES(?,?,?, ?,NULL,?,?,?)""",
                            (
                                employee["id"],d.isoformat(),"Робота",
                                norm/60.0,"План за режимом робочого часу",now,now
                            ),
                        )
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
                values[4] = "план перекрито відсутністю"
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
            suffix=".xlsx" if kind=="xlsx" else ".pdf"
            filename=f"Табель_П5_{year}_{month:02d}{suffix}"
            path=core.filedialog.asksaveasfilename(
                parent=self,title="Зберегти табель П-5",initialdir=str(core.OUTPUT_DIR),
                initialfile=filename,defaultextension=suffix,
                filetypes=[("Excel","*.xlsx")] if kind=="xlsx" else [("PDF","*.pdf")],
            )
            if not path: return
            writer=(
                (lambda out:export_p5_xlsx(core,year,month,out,self.personnel_report_active.get(),form_date,department,edrpou))
                if kind=="xlsx" else
                (lambda out:export_p5_pdf(core,year,month,out,self.personnel_report_active.get(),form_date,department,edrpou))
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
