# -*- coding: utf-8 -*-
"""Taxo 10.9-r7: safe odometer chronology and STOIR forecasting.

This additive layer fixes date/odometer selection without changing the DB schema.
``reading_at`` remains authoritative when present; ``work_date`` is a fallback.
Undated readings are not used to invent a forecast date.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from statistics import median

import vehicle_maintenance as maint

FEATURE_VERSION = "10.9-r7"


def _as_day(value):
    text = str(value or "").strip()
    if not text:
        return None
    try:
        if "." in text[:10]:
            return datetime.strptime(text[:10], "%d.%m.%Y").date()
        return date.fromisoformat(text[:10])
    except (TypeError, ValueError):
        return None


def _reading_columns(con):
    return {str(row[1]) for row in con.execute("PRAGMA table_info(vehicle_odometer_readings)")}


def odometer_points(con, vehicle_id, *, limit=250):
    """Return dated odometer facts with reading_at -> work_date fallback.

    Rows that have no reliable date stay outside chronology-based forecasting.
    This function never mutates the source table.
    """
    columns = _reading_columns(con)
    if not {"id", "vehicle_id", "reading_km", "reading_at"} <= columns:
        return []
    optional = [name for name in ("work_date", "source_type", "source_id") if name in columns]
    select = ["id", "reading_km", "reading_at"] + optional
    rows = con.execute(
        "SELECT " + ",".join(select) +
        " FROM vehicle_odometer_readings WHERE vehicle_id=? AND reading_km IS NOT NULL ORDER BY id DESC LIMIT ?",
        (int(vehicle_id), max(1, int(limit or 250))),
    ).fetchall()
    points = []
    for row in rows:
        try:
            km = int(row["reading_km"])
        except (TypeError, ValueError):
            continue
        reading_at = row["reading_at"]
        work_date = row["work_date"] if "work_date" in columns else None
        day = _as_day(reading_at) or _as_day(work_date)
        if day is None:
            continue
        points.append({
            "id": int(row["id"]),
            "reading_km": km,
            "reading_at": reading_at,
            "work_date": work_date,
            "source_type": row["source_type"] if "source_type" in columns else "",
            "source_id": row["source_id"] if "source_id" in columns else None,
            "effective_date": day,
        })
    return points


def latest_odometer(con, vehicle_id):
    """Newest reliably dated odometer fact, including waybill work_date fallback."""
    points = odometer_points(con, vehicle_id)
    if not points:
        return None
    return max(points, key=lambda item: (item["effective_date"], item["id"]))


def _daily_points(points):
    """Collapse same-day readings to the latest database fact for that day."""
    by_day = {}
    for point in points:
        day = point["effective_date"]
        current = by_day.get(day)
        if current is None or int(point["id"]) > int(current["id"]):
            by_day[day] = point
    return [by_day[day] for day in sorted(by_day)]


def _robust_segments(points):
    """Positive chronological mileage segments with obvious single spikes removed.

    The filter is deliberately statistical, not a vehicle-specific legal/business
    threshold: with >=3 segments it uses the median absolute deviation. If the
    normal segments are identical (MAD=0), only a >4x isolated rate is treated
    as an obvious spike. Sparse histories are left untouched rather than guessed.
    """
    segments = []
    for left, right in zip(points, points[1:]):
        days = (right["effective_date"] - left["effective_date"]).days
        distance = int(right["reading_km"]) - int(left["reading_km"])
        if days > 0 and distance > 0:
            segments.append({"days": days, "distance": distance, "rate": distance / float(days)})
    if len(segments) < 3:
        return segments
    rates = [item["rate"] for item in segments]
    center = median(rates)
    deviations = [abs(rate - center) for rate in rates]
    mad = median(deviations)
    if mad > 0:
        limit = 6.0 * mad
        kept = [item for item in segments if abs(item["rate"] - center) <= limit]
    elif center > 0:
        kept = [item for item in segments if item["rate"] <= center * 4.0]
    else:
        kept = segments
    return kept or segments


def average_daily_mileage(con, vehicle_id, *, lookback_days=60):
    points = odometer_points(con, vehicle_id)
    if len(points) < 2:
        return None
    newest_day = max(item["effective_date"] for item in points)
    cutoff = newest_day - timedelta(days=max(7, int(lookback_days or 60)))
    daily = _daily_points([item for item in points if item["effective_date"] >= cutoff])
    if len(daily) < 2:
        return None
    segments = _robust_segments(daily)
    if not segments:
        return None
    days = sum(item["days"] for item in segments)
    distance = sum(item["distance"] for item in segments)
    return (distance / float(days)) if days > 0 and distance > 0 else None


def forecast_due_date(remaining_km, avg_daily_km, *, from_date=None):
    if remaining_km is None or not avg_daily_km or avg_daily_km <= 0 or from_date is None:
        return None
    start = from_date if isinstance(from_date, date) else _as_day(from_date)
    if start is None:
        return None
    if int(remaining_km) <= 0:
        return start
    days = max(1, int(round(float(remaining_km) / float(avg_daily_km))))
    return start + timedelta(days=days)


def vehicle_plan(con, vehicle_id):
    """STOIR plan anchored to the newest reliable odometer fact date."""
    profile = maint.get_profile(con, vehicle_id)
    od = latest_odometer(con, vehicle_id)
    current = maint._value(od, "reading_km")
    last_fact_date = maint._value(od, "effective_date")
    warning = int(maint._value(profile, "warning_km", 1000) or 0)
    avg_daily = average_daily_mileage(con, vehicle_id)
    result = {
        "vehicle_id": int(vehicle_id),
        "current_odometer_km": current,
        "current_odometer_date": last_fact_date,
        "profile": profile,
        "average_daily_km": avg_daily,
    }
    # Preserve the established model: TO-1 and TO-2 use their own last service
    # events. r7 does not silently decide that TO-2 resets the TO-1 cycle.
    for event_type, key, field in (
        (maint.MAINTENANCE_TO1, "to1", "to1_interval_km"),
        (maint.MAINTENANCE_TO2, "to2", "to2_interval_km"),
    ):
        event = maint.last_event(con, vehicle_id, event_type)
        due = maint.next_due_by_mileage(current, maint._value(event, "odometer_km"), maint._value(profile, field))
        result[key] = {
            "last_event": event,
            "due": due,
            "status": maint.maintenance_status(due["remaining_km"], warning) if due else "unknown",
            "forecast_date": forecast_due_date(due["remaining_km"], avg_daily, from_date=last_fact_date) if due else None,
        }
    return result


def install(core, App):
    """Install r7 without schema migration or rewriting historical modules."""
    maint.latest_odometer = latest_odometer
    maint.average_daily_mileage = average_daily_mileage
    maint.forecast_due_date = forecast_due_date
    maint.vehicle_plan = vehicle_plan
    # main.py historically imports these helpers directly; keep those aliases in
    # sync so every existing entry point uses the same corrected behavior.
    for name, func in (
        ("latest_odometer", latest_odometer),
        ("average_daily_mileage", average_daily_mileage),
        ("forecast_due_date", forecast_due_date),
        ("vehicle_plan", vehicle_plan),
    ):
        if hasattr(core, name):
            setattr(core, name, func)

    class App1097(App):
        pass

    core.APP_VERSION = FEATURE_VERSION
    return App1097
