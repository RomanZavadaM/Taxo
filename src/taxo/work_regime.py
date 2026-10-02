# -*- coding: utf-8 -*-
"""Employee work-time regimes and legal-norm helpers for Taxo 9.1.

This module stores effective-dated work-time regimes separately from employee
identity data.  It never converts a duration (for example "8 hours") into an
invented clock interval.

Legal model used by the UI/calculations:
- ordinary weekly norm defaults to 40:00;
- fixed 5-day / 6-day schedules carry an explicit per-weekday norm;
- summarized accounting has an explicit accounting period and weekly/calendar
  norm, while overtime is not determined from an isolated week;
- lawful absence can reduce the adjusted norm by the hours that the employee
  would otherwise have been scheduled to work.

The user remains responsible for selecting the regime actually established by
the employer/collective agreement.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta


REGIME_FIVE_DAY = "five_day"
REGIME_SIX_DAY = "six_day"
REGIME_SUMMARIZED = "summarized"
REGIME_CUSTOM = "custom"

REGIME_LABELS = {
    REGIME_FIVE_DAY: "5-денний робочий тиждень",
    REGIME_SIX_DAY: "6-денний робочий тиждень",
    REGIME_SUMMARIZED: "Підсумований облік",
    REGIME_CUSTOM: "Індивідуальний / інший режим",
}
REGIME_BY_LABEL = {v: k for k, v in REGIME_LABELS.items()}

PERIOD_WEEK = "week"
PERIOD_MONTH = "month"
PERIOD_QUARTER = "quarter"
PERIOD_HALF_YEAR = "half_year"
PERIOD_YEAR = "year"
PERIOD_LABELS = {
    PERIOD_WEEK: "Тиждень",
    PERIOD_MONTH: "Місяць",
    PERIOD_QUARTER: "Квартал",
    PERIOD_HALF_YEAR: "Півріччя",
    PERIOD_YEAR: "Рік",
}
PERIOD_BY_LABEL = {v: k for k, v in PERIOD_LABELS.items()}

WEEKDAY_KEYS = ("mon","tue","wed","thu","fri","sat","sun")
WEEKDAY_LABELS = ("Пн","Вт","Ср","Чт","Пт","Сб","Нд")


def parse_hhmm(value) -> int:
    raw = str(value or "").strip()
    if not raw:
        return 0
    if ":" not in raw:
        try:
            return int(round(float(raw.replace(",", ".")) * 60))
        except ValueError as exc:
            raise ValueError("Години мають бути у форматі ГГ:ХХ.") from exc
    parts = raw.split(":")
    if len(parts) != 2:
        raise ValueError("Години мають бути у форматі ГГ:ХХ.")
    try:
        hours = int(parts[0])
        minutes = int(parts[1])
    except ValueError as exc:
        raise ValueError("Години мають бути у форматі ГГ:ХХ.") from exc
    if hours < 0 or minutes < 0 or minutes >= 60:
        raise ValueError("Некоректна тривалість.")
    return hours * 60 + minutes


def hhmm(minutes) -> str:
    value = int(round(minutes or 0))
    sign = "-" if value < 0 else ""
    value = abs(value)
    h, m = divmod(value, 60)
    return f"{sign}{h}:{m:02d}"


def preset_five_day_40():
    return (480,480,480,480,480,0,0), 2400


def preset_six_day_40():
    # Common 40-hour six-day template.  The 5-hour Saturday is a template,
    # not a claim that wartime legislation universally requires it.
    return (420,420,420,420,420,300,0), 2400


def preset_six_day_36():
    return (360,360,360,360,360,360,0), 2160


def preset_six_day_24():
    return (240,240,240,240,240,240,0), 1440


PRESETS = {
    "5/40": preset_five_day_40,
    "6/40": preset_six_day_40,
    "6/36": preset_six_day_36,
    "6/24": preset_six_day_24,
}


@dataclass
class WorkRegime:
    employee_id: int
    regime_type: str = REGIME_FIVE_DAY
    accounting_period: str = PERIOD_WEEK
    weekly_norm_minutes: int = 2400
    weekday_minutes: tuple = (480,480,480,480,480,0,0)
    effective_from: str = "1900-01-01"
    effective_to: str = ""
    notes: str = ""
    explicit: bool = False

    @property
    def label(self):
        return REGIME_LABELS.get(self.regime_type, self.regime_type)

    @property
    def accounting_label(self):
        return PERIOD_LABELS.get(self.accounting_period, self.accounting_period)


def ensure_schema(core):
    con = core.db()
    try:
        con.execute(
            """CREATE TABLE IF NOT EXISTS employee_work_regimes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
                effective_from TEXT NOT NULL,
                effective_to TEXT DEFAULT '',
                regime_type TEXT NOT NULL DEFAULT 'five_day',
                accounting_period TEXT NOT NULL DEFAULT 'week',
                weekly_norm_minutes INTEGER NOT NULL DEFAULT 2400,
                mon_minutes INTEGER NOT NULL DEFAULT 480,
                tue_minutes INTEGER NOT NULL DEFAULT 480,
                wed_minutes INTEGER NOT NULL DEFAULT 480,
                thu_minutes INTEGER NOT NULL DEFAULT 480,
                fri_minutes INTEGER NOT NULL DEFAULT 480,
                sat_minutes INTEGER NOT NULL DEFAULT 0,
                sun_minutes INTEGER NOT NULL DEFAULT 0,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT DEFAULT '',
                UNIQUE(employee_id,effective_from)
            )"""
        )
        con.execute(
            """CREATE INDEX IF NOT EXISTS idx_employee_work_regimes_dates
               ON employee_work_regimes(employee_id,effective_from,effective_to)"""
        )
        con.commit()
    finally:
        con.close()


def _default(employee_id):
    days, weekly = preset_five_day_40()
    return WorkRegime(
        employee_id=int(employee_id),
        regime_type=REGIME_FIVE_DAY,
        accounting_period=PERIOD_WEEK,
        weekly_norm_minutes=weekly,
        weekday_minutes=days,
        explicit=False,
    )


def _row_regime(row):
    return WorkRegime(
        employee_id=int(row["employee_id"]),
        regime_type=row["regime_type"] or REGIME_FIVE_DAY,
        accounting_period=row["accounting_period"] or PERIOD_WEEK,
        weekly_norm_minutes=int(row["weekly_norm_minutes"] or 0),
        weekday_minutes=tuple(int(row[f"{key}_minutes"] or 0) for key in WEEKDAY_KEYS),
        effective_from=row["effective_from"] or "1900-01-01",
        effective_to=row["effective_to"] or "",
        notes=row["notes"] or "",
        explicit=True,
    )


def regime_for_date(con, employee_id, target_date):
    if isinstance(target_date, str):
        target_date = date.fromisoformat(target_date)
    row = con.execute(
        """SELECT * FROM employee_work_regimes
           WHERE employee_id=?
             AND effective_from<=?
             AND (COALESCE(effective_to,'')='' OR effective_to>=?)
           ORDER BY effective_from DESC,id DESC
           LIMIT 1""",
        (int(employee_id), target_date.isoformat(), target_date.isoformat()),
    ).fetchone()
    return _row_regime(row) if row else _default(employee_id)


def latest_regime(con, employee_id):
    row = con.execute(
        """SELECT * FROM employee_work_regimes
           WHERE employee_id=?
           ORDER BY effective_from DESC,id DESC
           LIMIT 1""",
        (int(employee_id),),
    ).fetchone()
    return _row_regime(row) if row else _default(employee_id)


def day_norm_minutes(con, employee_id, target_date):
    regime = regime_for_date(con, employee_id, target_date)
    if isinstance(target_date, str):
        target_date = date.fromisoformat(target_date)
    return int(regime.weekday_minutes[target_date.weekday()] or 0), regime


def validate_regime(regime_type, weekly_norm_minutes, weekday_minutes):
    weekly = int(weekly_norm_minutes)
    days = tuple(int(x) for x in weekday_minutes)
    errors = []
    warnings = []
    if weekly <= 0:
        errors.append("Тижнева норма має бути більшою за нуль.")
    if any(x < 0 for x in days):
        errors.append("Норма дня не може бути від’ємною.")
    total = sum(days)
    if total != weekly:
        errors.append(
            f"Сума норм Пн–Нд ({hhmm(total)}) не дорівнює тижневій нормі ({hhmm(weekly)})."
        )

    if regime_type == REGIME_SIX_DAY:
        if days[6] != 0:
            warnings.append("Для 6-денного шаблону неділя зазвичай є вихідною; перевірте встановлений режим.")
        # Article 52 daily maxima for ordinary 40/36/24-hour six-day weeks.
        if weekly <= 1440:
            cap = 240
        elif weekly <= 2160:
            cap = 360
        elif weekly <= 2400:
            cap = 420
        else:
            cap = None
            warnings.append(
                "Тижнева норма понад 40:00 потребує окремої правової підстави; Taxo її не встановлює автоматично."
            )
        if cap is not None and any(x > cap for x in days[:6]):
            errors.append(
                f"Для вибраної 6-денної норми денна тривалість перевищує {hhmm(cap)}."
            )

    if weekly > 2400:
        warnings.append(
            "Норма понад 40:00 не є звичайною нормою за КЗпП; перевірте спеціальну підставу та наказ/режим підприємства."
        )
    return errors, list(dict.fromkeys(warnings))


def save_regime(
    con,
    *,
    employee_id,
    effective_from,
    effective_to,
    regime_type,
    accounting_period,
    weekly_norm_minutes,
    weekday_minutes,
    notes="",
):
    if isinstance(effective_from, date):
        effective_from = effective_from.isoformat()
    if isinstance(effective_to, date):
        effective_to = effective_to.isoformat()
    effective_to = str(effective_to or "").strip()
    weekly = int(weekly_norm_minutes)
    days = tuple(int(x) for x in weekday_minutes)
    errors, warnings = validate_regime(regime_type, weekly, days)
    if errors:
        raise ValueError("\n".join(errors))
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        """INSERT INTO employee_work_regimes(
             employee_id,effective_from,effective_to,regime_type,accounting_period,
             weekly_norm_minutes,mon_minutes,tue_minutes,wed_minutes,thu_minutes,
             fri_minutes,sat_minutes,sun_minutes,notes,created_at,updated_at
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(employee_id,effective_from) DO UPDATE SET
             effective_to=excluded.effective_to,
             regime_type=excluded.regime_type,
             accounting_period=excluded.accounting_period,
             weekly_norm_minutes=excluded.weekly_norm_minutes,
             mon_minutes=excluded.mon_minutes,tue_minutes=excluded.tue_minutes,
             wed_minutes=excluded.wed_minutes,thu_minutes=excluded.thu_minutes,
             fri_minutes=excluded.fri_minutes,sat_minutes=excluded.sat_minutes,
             sun_minutes=excluded.sun_minutes,notes=excluded.notes,
             updated_at=excluded.updated_at""",
        (
            int(employee_id), str(effective_from), effective_to, regime_type,
            accounting_period, weekly, *days, str(notes or "").strip(), now, now,
        ),
    )
    return warnings


def week_start(target_date):
    if isinstance(target_date, str):
        target_date = date.fromisoformat(target_date)
    return target_date - timedelta(days=target_date.weekday())


def accounting_period_bounds(regime, target_date):
    """Calendar accounting-period bounds for summarized balance display."""
    if isinstance(target_date, str):
        target_date = date.fromisoformat(target_date)
    if regime.accounting_period == PERIOD_WEEK:
        start = week_start(target_date)
        return start, start + timedelta(days=6)
    if regime.accounting_period == PERIOD_MONTH:
        start = target_date.replace(day=1)
        if start.month == 12:
            next_month = date(start.year + 1, 1, 1)
        else:
            next_month = date(start.year, start.month + 1, 1)
        return start, next_month - timedelta(days=1)
    if regime.accounting_period == PERIOD_QUARTER:
        month = ((target_date.month - 1) // 3) * 3 + 1
        start = date(target_date.year, month, 1)
        end_month = month + 2
        if end_month == 12:
            next_period = date(target_date.year + 1, 1, 1)
        else:
            next_period = date(target_date.year, end_month + 1, 1)
        return start, next_period - timedelta(days=1)
    if regime.accounting_period == PERIOD_HALF_YEAR:
        month = 1 if target_date.month <= 6 else 7
        start = date(target_date.year, month, 1)
        next_period = date(target_date.year + (1 if month == 7 else 0), 1 if month == 7 else 7, 1)
        return start, next_period - timedelta(days=1)
    start = date(target_date.year, 1, 1)
    return start, date(target_date.year, 12, 31)
