# -*- coding: utf-8 -*-
"""Employee reminders for Taxo 10.4-r8.

Birthdays are read from the single employees.birth_date field.  That field may
be entered manually or filled from an approved state-registry XLSX import.
The engine never duplicates employee data and does not need internet access.
"""
from __future__ import annotations

from calendar import isleap
from datetime import date, datetime

APP_VERSION = "10.4-r8"
BIRTHDAY_TRIGGER_DAYS = (5, 1, 0)


def _text(value):
    return str(value or "").strip()


def parse_birth_date(value):
    """Accept Taxo ISO dates plus the human DD.MM.YYYY form."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = _text(value)
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def birthday_in_year(born, year):
    """Return the reminder date for a birthday in a selected year.

    29 February is represented as 28 February in non-leap years.  This policy
    is intentionally limited to friendly reminders; the stored birth date is
    never changed.
    """
    born = parse_birth_date(born)
    if born is None:
        return None
    if born.month == 2 and born.day == 29 and not isleap(int(year)):
        return date(int(year), 2, 28)
    return date(int(year), born.month, born.day)


def next_birthday(born, today=None):
    today = today or date.today()
    candidate = birthday_in_year(born, today.year)
    if candidate is None:
        return None
    if candidate < today:
        candidate = birthday_in_year(born, today.year + 1)
    return candidate


def ensure_schema_on_connection(con):
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS employee_birthday_reminder_log (
            employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            birthday_date TEXT NOT NULL,
            trigger_days INTEGER NOT NULL,
            shown_on TEXT NOT NULL,
            shown_at TEXT NOT NULL,
            PRIMARY KEY(employee_id,birthday_date,trigger_days,shown_on)
        )
        """
    )
    con.execute(
        "CREATE INDEX IF NOT EXISTS idx_employee_birthday_reminder_log_date "
        "ON employee_birthday_reminder_log(shown_on,employee_id)"
    )


def ensure_schema(core):
    con = core.db()
    try:
        ensure_schema_on_connection(con)
        con.commit()
    finally:
        con.close()


def _employee_columns(con):
    return {row[1] for row in con.execute("PRAGMA table_info(employees)").fetchall()}


def collect_birthdays(con, today=None, max_days=30, active_only=True):
    """Return upcoming birthdays sorted by distance from today."""
    today = today or date.today()
    if "birth_date" not in _employee_columns(con):
        return []
    sql = (
        "SELECT id,last_name,first_name,middle_name,birth_date,active "
        "FROM employees"
    )
    params = []
    if active_only:
        sql += " WHERE COALESCE(active,1)=1"
    sql += " ORDER BY last_name,first_name,middle_name,id"
    result = []
    for row in con.execute(sql, params).fetchall():
        born = parse_birth_date(row["birth_date"])
        if born is None:
            continue
        event_date = next_birthday(born, today=today)
        if event_date is None:
            continue
        days = (event_date - today).days
        if days < 0 or days > int(max_days):
            continue
        full_name = " ".join(
            x for x in (row["last_name"], row["first_name"], row["middle_name"]) if _text(x)
        )
        result.append({
            "employee_id": int(row["id"]),
            "employee_name": full_name,
            "birth_date": born.isoformat(),
            "birthday_date": event_date.isoformat(),
            "days_until": days,
            "age": event_date.year - born.year,
        })
    result.sort(key=lambda item: (item["days_until"], item["employee_name"].casefold()))
    return result


def due_birthday_reminders(con, today=None, triggers=BIRTHDAY_TRIGGER_DAYS):
    """Return birthdays due exactly at configured reminder thresholds."""
    today = today or date.today()
    trigger_set = {int(x) for x in triggers}
    horizon = max(trigger_set) if trigger_set else 0
    rows = collect_birthdays(con, today=today, max_days=horizon, active_only=True)
    result = []
    for row in rows:
        if row["days_until"] not in trigger_set:
            continue
        item = dict(row)
        item["trigger_days"] = int(row["days_until"])
        if item["trigger_days"] == 0:
            item["message"] = "Сьогодні день народження"
        elif item["trigger_days"] == 1:
            item["message"] = "День народження завтра"
        else:
            item["message"] = "До дня народження %d днів" % item["trigger_days"]
        result.append(item)
    return result


def unseen_due_birthday_reminders(con, today=None, triggers=BIRTHDAY_TRIGGER_DAYS):
    """Return due reminders that have not yet been shown today."""
    today = today or date.today()
    ensure_schema_on_connection(con)
    result = []
    for item in due_birthday_reminders(con, today=today, triggers=triggers):
        exists = con.execute(
            """SELECT 1 FROM employee_birthday_reminder_log
               WHERE employee_id=? AND birthday_date=? AND trigger_days=? AND shown_on=?""",
            (
                item["employee_id"], item["birthday_date"], item["trigger_days"],
                today.isoformat(),
            ),
        ).fetchone()
        if not exists:
            result.append(item)
    return result


def mark_reminders_shown(con, reminders, today=None, now=None):
    today = today or date.today()
    now = now or datetime.now()
    ensure_schema_on_connection(con)
    for item in reminders:
        con.execute(
            """INSERT OR IGNORE INTO employee_birthday_reminder_log(
                   employee_id,birthday_date,trigger_days,shown_on,shown_at
               ) VALUES(?,?,?,?,?)""",
            (
                int(item["employee_id"]), _text(item["birthday_date"]),
                int(item["trigger_days"]), today.isoformat(),
                now.isoformat(timespec="seconds"),
            ),
        )


def birthday_summary_text(reminders):
    lines = []
    for item in reminders:
        lines.append(
            "%s — %s (%s)" % (
                item["employee_name"], item["message"],
                datetime.fromisoformat(item["birthday_date"]).strftime("%d.%m.%Y"),
            )
        )
    return "\n".join(lines)
