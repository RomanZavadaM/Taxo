# -*- coding: utf-8 -*-
"""Taxo 10.9-r6 — personnel balance / P-5 safety corrections.

This layer keeps issued historical personnel code intact and narrows two risky
behaviours at runtime:
- planned weekend/rest markers are non-working overrides, but do not reduce the
  legal/calendar norm like vacation or sickness;
- legacy monthly driver balance overlays absences by dated employee rows rather
  than by a lossy ``{driver_id: employee_id}`` dictionary.
"""
from __future__ import annotations

from datetime import date

import personnel_v91 as personnel

FEATURE_VERSION = "10.9-r6"

# These values may suppress work for a day, but they are not absence reasons
# that reduce the employee's legal/calendar norm.
NON_REDUCING_NONWORK_TYPES = {"Вихідний", "Відпочинок"}


def norm_reduction_day_type(day_type) -> bool:
    value = str(day_type or "").strip()
    return value in personnel.NONWORK_OVERRIDE_TYPES and value not in NON_REDUCING_NONWORK_TYPES


def employee_employed_on_row(row, target_date) -> bool:
    """Date-aware employment check for raw sqlite rows.

    Mirrors the current Taxo employment semantics without depending on current
    ``active`` state, so historical rows remain eligible after dismissal/rehire.
    """
    if isinstance(target_date, str):
        target_date = date.fromisoformat(target_date)
    started = str(row["employment_date"] or "").strip() if "employment_date" in row.keys() else ""
    ended = str(row["dismissal_date"] or "").strip() if "dismissal_date" in row.keys() else ""
    try:
        if started and target_date < date.fromisoformat(started):
            return False
    except ValueError:
        pass
    try:
        if ended and target_date > date.fromisoformat(ended):
            return False
    except ValueError:
        pass
    return True


def dated_absence_rows(con, start_day, end_day, driver_ids):
    """Return one dated absence row per driver/day without collapsing employees.

    If historical data somehow contains more than one linked employee candidate,
    only a row whose employment period covers that date is considered. This is
    deliberately date-aware and never prefers today's ``active`` flag.
    """
    driver_ids = [int(value) for value in driver_ids if value is not None]
    if not driver_ids:
        return {}
    if isinstance(start_day, str):
        start_day = date.fromisoformat(start_day)
    if isinstance(end_day, str):
        end_day = date.fromisoformat(end_day)
    q = ",".join("?" for _ in driver_ids)
    rows = con.execute(
        f"""SELECT e.id AS employee_id,e.driver_id,e.employment_date,e.dismissal_date,
                   t.work_date,t.day_type
              FROM employee_time_entries t
              JOIN employees e ON e.id=t.employee_id
             WHERE t.work_date BETWEEN ? AND ?
               AND e.driver_id IN ({q})
             ORDER BY t.work_date,e.id""",
        (start_day.isoformat(), end_day.isoformat(), *driver_ids),
    ).fetchall()
    result = {}
    for row in rows:
        day = date.fromisoformat(row["work_date"])
        if not employee_employed_on_row(row, day):
            continue
        if str(row["day_type"] or "") not in personnel.NONWORK_OVERRIDE_TYPES:
            continue
        result.setdefault((int(row["driver_id"]), row["work_date"]), row)
    return result


def _safe_absence_adjustment(core, original):
    def adjusted(con, employee, work_date, regime, base_norm):
        entry = con.execute(
            "SELECT day_type FROM employee_time_entries WHERE employee_id=? AND work_date=?",
            (employee["id"], work_date.isoformat()),
        ).fetchone()
        if entry and not norm_reduction_day_type(entry["day_type"]):
            return 0
        return original(core, con, employee, work_date, regime, base_norm)
    return adjusted


def _install_monthly_balance_overlay(core):
    previous = core.collect_monthly_work_balance

    def collect_monthly_work_balance_r6(year, month, active_only=True):
        # Obtain the canonical driver balance without either historical absence
        # overlay, then apply one date-aware overlay below.
        old_personnel_types = personnel.NONWORK_OVERRIDE_TYPES
        old_core_types = getattr(core, "TAXO_NONWORK_OVERRIDE_TYPES", set())
        try:
            personnel.NONWORK_OVERRIDE_TYPES = set()
            core.TAXO_NONWORK_OVERRIDE_TYPES = set()
            data = previous(year, month, active_only)
        finally:
            personnel.NONWORK_OVERRIDE_TYPES = old_personnel_types
            core.TAXO_NONWORK_OVERRIDE_TYPES = old_core_types

        days = list(data.get("days") or [])
        drivers = list(data.get("drivers") or [])
        if not days or not drivers:
            data["absence_overlay_applied"] = True
            return data

        con = core.db()
        try:
            driver_ids = [int(row["driver_id"]) for row in drivers if row.get("driver_id") is not None]
            entries = dated_absence_rows(con, days[0], days[-1], driver_ids)
            work_rows = con.execute(
                "SELECT driver_id,work_date,work_hours,overtime_hours FROM worklog "
                "WHERE work_date BETWEEN ? AND ?",
                (days[0].isoformat(), days[-1].isoformat()),
            ).fetchall()
            work_by = {(int(row["driver_id"]), row["work_date"]): row for row in work_rows}
        finally:
            con.close()

        for driver in drivers:
            driver_id = int(driver["driver_id"])
            for idx, day in enumerate(days):
                entry = entries.get((driver_id, day.isoformat()))
                if not entry:
                    continue
                driver["cells"][idx] = personnel._legacy_absence_cell(entry["day_type"])
                work = work_by.get((driver_id, day.isoformat()))
                if work is None:
                    continue
                wm = core.hours_value_to_minutes(work["work_hours"])
                om = core.hours_value_to_minutes(work["overtime_hours"])
                driver["work_min"] = max(0, int(driver.get("work_min") or 0) - wm)
                driver["over_min"] = max(0, int(driver.get("over_min") or 0) - om)
                if wm > 0:
                    driver["work_days"] = max(0, int(driver.get("work_days") or 0) - 1)
        data["absence_overlay_applied"] = True
        return data

    core.collect_monthly_work_balance = collect_monthly_work_balance_r6


def install(core, base_app):
    """Install additive r6 safety behaviour without schema changes."""
    original = personnel._employee_absence_adjustment_minutes
    personnel._employee_absence_adjustment_minutes = _safe_absence_adjustment(core, original)
    _install_monthly_balance_overlay(core)
    return base_app
