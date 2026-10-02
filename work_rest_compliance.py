# -*- coding: utf-8 -*-
"""Taxo 10.9-r4 — stronger PLAN work/rest compliance analysis.

This module closes edge cases left by the historical 10.4-r6 rest timeline:
analysis-window boundaries are part of the control, overlapping duties are
reported instead of silently merged, absence of any qualifying rest is visible,
and a conservative two-consecutive-week weekly-rest check is added.

The runtime adapter deliberately reads the same PLAN work intervals as r6.
It never promotes route/waybill plan to FACT and never rewrites user data.
"""
from __future__ import annotations

from datetime import datetime, time, timedelta

from v1046_features import classify_rest_gaps, merge_intervals

APP_VERSION = "10.9-r4"


def _minutes(delta):
    return max(0, int(round(delta.total_seconds() / 60.0)))


def detect_overlaps(intervals):
    """Return real overlaps from raw duty intervals before any union/merge."""
    ordered = sorted(
        (start, end) for start, end in intervals
        if start is not None and end is not None and end > start
    )
    overlaps = []
    if not ordered:
        return overlaps
    active_start, active_end = ordered[0]
    for start, end in ordered[1:]:
        if start < active_end:
            overlaps.append({
                "start": start,
                "end": min(active_end, end),
                "left_start": active_start,
                "left_end": active_end,
                "right_start": start,
                "right_end": end,
                "minutes": _minutes(min(active_end, end) - start),
            })
            if end > active_end:
                active_end = end
            continue
        active_start, active_end = start, end
    return overlaps


def bounded_free_gaps(intervals, control_start, control_end):
    """Free-time gaps including both analysis-window edges."""
    if control_end <= control_start:
        raise ValueError("control_end must be after control_start")
    clipped = []
    for start, end in intervals:
        if start is None or end is None or end <= start:
            continue
        start = max(start, control_start)
        end = min(end, control_end)
        if end > start:
            clipped.append((start, end))
    merged = merge_intervals(clipped)
    if not merged:
        return [{
            "start": control_start,
            "end": control_end,
            "minutes": _minutes(control_end - control_start),
            "next_date": control_end.date(),
            "boundary": "both",
        }]
    gaps = []
    if merged[0][0] > control_start:
        gaps.append({
            "start": control_start,
            "end": merged[0][0],
            "minutes": _minutes(merged[0][0] - control_start),
            "next_date": merged[0][0].date(),
            "boundary": "start",
        })
    for left, right in zip(merged, merged[1:]):
        if right[0] > left[1]:
            gaps.append({
                "start": left[1],
                "end": right[0],
                "minutes": _minutes(right[0] - left[1]),
                "next_date": right[0].date(),
                "boundary": "internal",
            })
    if merged[-1][1] < control_end:
        gaps.append({
            "start": merged[-1][1],
            "end": control_end,
            "minutes": _minutes(control_end - merged[-1][1]),
            "next_date": control_end.date(),
            "boundary": "end",
        })
    return gaps


def _week_key(day):
    iso = day.isocalendar()
    return int(iso[0]), int(iso[1])


def _week_start(day):
    return day - timedelta(days=day.weekday())


def fortnight_weekly_rest_warnings(weekly, display_start, display_end, hhmm):
    """Conservative two-consecutive-week check."""
    by_week = {}
    for event in weekly:
        key = _week_key(event["end"].date())
        by_week.setdefault(key, []).append(event)

    warnings = []
    first = _week_start(display_start) - timedelta(days=7)
    last = _week_start(display_end)
    cursor = first
    while cursor <= last:
        next_week = cursor + timedelta(days=7)
        pair_end = cursor + timedelta(days=13)
        if pair_end < display_start or cursor > display_end:
            cursor = next_week
            continue
        keys = (_week_key(cursor), _week_key(next_week))
        events = [ev for key in keys for ev in by_week.get(key, [])]
        if len(events) < 2:
            warnings.append(
                "ПЛАН: у двотижневому періоді %s–%s знайдено лише %d "
                "кваліфікованих щотижневих відпочинків; потрібно перевірити правило двох тижнів."
                % (cursor.strftime("%d.%m.%Y"), pair_end.strftime("%d.%m.%Y"), len(events))
            )
        elif not any(int(ev["minutes"]) >= 45 * 60 for ev in events):
            warnings.append(
                "ПЛАН: у двотижневому періоді %s–%s є два щотижневі відпочинки, "
                "але жоден не досягає 45:00; перевірити регулярний щотижневий відпочинок і компенсацію."
                % (cursor.strftime("%d.%m.%Y"), pair_end.strftime("%d.%m.%Y"))
            )
        cursor = next_week
    return warnings


def rest_compliance_report(intervals, control_start, control_end, display_start, display_end, hhmm):
    """Analyze PLAN duty intervals without hiding boundary or overlap defects."""
    raw = [
        (start, end) for start, end in intervals
        if start is not None and end is not None and end > start
    ]
    overlaps = detect_overlaps(raw)
    gaps = bounded_free_gaps(raw, control_start, control_end)
    daily, weekly = classify_rest_gaps(gaps)
    events = sorted([*daily, *weekly], key=lambda item: item["end"])
    warnings = []
    info = []

    for overlap in overlaps:
        if overlap["end"].date() >= display_start and overlap["start"].date() <= display_end:
            warnings.append(
                "ПЛАН: перекриття робочих інтервалів %s–%s (%s). Це помилка даних, "
                "інтервали не можна тихо зливати для контролю відпочинку."
                % (
                    overlap["start"].strftime("%d.%m.%Y %H:%M"),
                    overlap["end"].strftime("%d.%m.%Y %H:%M"),
                    hhmm(overlap["minutes"]),
                )
            )

    if raw and not events:
        work_start = min(start for start, _ in raw)
        work_end = max(end for _, end in raw)
        if work_end - work_start > timedelta(hours=24):
            warnings.append(
                "ПЛАН: у контрольному вікні немає жодного кваліфікованого щоденного або "
                "щотижневого відпочинку >=9:00 при роботі довше 24 годин; перевірити графік."
            )

    for left, right in zip(events, events[1:]):
        anchor = left["end"]
        next_start = right.get("qualifying_start") or right.get("second_start") or right["start"]
        if next_start > anchor + timedelta(hours=15):
            if anchor.date() <= display_end and next_start.date() >= display_start:
                warnings.append(
                    "ПЛАН: після завершення кваліфікованого відпочинку %s наступний "
                    "період >=9:00 починається лише %s; перевірити 24-годинне правило."
                    % (anchor.strftime("%d.%m.%Y %H:%M"), next_start.strftime("%d.%m.%Y %H:%M"))
                )

    reduced_since_weekly = 0
    for event in events:
        if event["kind"].startswith("weekly_"):
            reduced_since_weekly = 0
        elif event["kind"] == "daily_reduced":
            reduced_since_weekly += 1
            if display_start <= event["next_date"] <= display_end and reduced_since_weekly > 3:
                warnings.append(
                    "ПЛАН: перед %s це %d-й скорочений щоденний відпочинок між "
                    "щотижневими періодами (>3)."
                    % (event["next_date"].strftime("%d.%m.%Y"), reduced_since_weekly)
                )

    weekly_sorted = sorted(weekly, key=lambda item: item["start"])
    if raw and not weekly_sorted:
        active_start = min(start for start, _ in raw)
        active_end = max(end for _, end in raw)
        if active_end - active_start > timedelta(days=6):
            warnings.append(
                "ПЛАН: у контрольному вікні немає кваліфікованого щотижневого "
                "відпочинку >=24:00 при робочому періоді довше шести 24-годинних періодів."
            )
    for left, right in zip(weekly_sorted, weekly_sorted[1:]):
        span = right["start"] - left["end"]
        if span > timedelta(days=6) and right["start"].date() >= display_start and left["end"].date() <= display_end:
            warnings.append(
                "ПЛАН: між завершенням щотижневого відпочинку %s і початком наступного %s "
                "минуло %s — більше шести 24-годинних періодів."
                % (left["end"].strftime("%d.%m %H:%M"), right["start"].strftime("%d.%m %H:%M"), hhmm(_minutes(span)))
            )

    warnings.extend(fortnight_weekly_rest_warnings(weekly_sorted, display_start, display_end, hhmm))

    for event in daily:
        if event.get("split") and display_start <= event["next_date"] <= display_end:
            info.append(
                "ПЛАН: перед %s звичайний щоденний відпочинок %s + %s (модель 3+9)."
                % (
                    event["next_date"].strftime("%d.%m.%Y"),
                    hhmm(event["first_minutes"]),
                    hhmm(event["second_minutes"]),
                )
            )
    for event in weekly_sorted:
        if event["kind"] == "weekly_reduced" and event["end"].date() >= display_start and event["start"].date() <= display_end:
            info.append(
                "ПЛАН: щотижневий відпочинок %s–%s = %s, скорочений; компенсацію "
                "потрібно контролювати окремо за фактичними даними."
                % (event["start"].strftime("%d.%m %H:%M"), event["end"].strftime("%d.%m %H:%M"), hhmm(event["minutes"]))
            )

    return {
        "daily_rests": [ev for ev in daily if display_start <= ev["next_date"] <= display_end],
        "weekly_rests": [ev for ev in weekly_sorted if ev["end"].date() >= display_start and ev["start"].date() <= display_end],
        "warnings": warnings,
        "info": info,
        "gaps": gaps,
        "overlaps": overlaps,
        "control_basis": "plan",
    }


def _rest_message(text):
    value = str(text or "")
    tokens = (
        "щоденн", "щотижнев", "24-годин", "24 год", "шести 24", "3+9",
        "двотижнев", "кваліфікованого відпочинку", "перекриття робочих інтервалів",
    )
    return value.startswith("ПЛАН:") and any(token in value for token in tokens)


def install(core, base_app):
    if getattr(core, "_TAXO_1094_INSTALLED", False):
        return base_app
    core.APP_VERSION = APP_VERSION

    class Taxo1094App(base_app):
        def calculate_work_analysis(self):
            data = super().calculate_work_analysis()
            if data is None or not getattr(self, "driver_id", None):
                return data

            year = int(self.year_var.get())
            month = int(self.month_var.get())
            display_start = datetime(year, month, 1).date()
            display_end = core.month_dates(year, month)[-1]
            query_start = display_start - timedelta(days=45)
            query_end = display_end + timedelta(days=14)

            con = core.db()
            try:
                rows = con.execute(
                    "SELECT * FROM worklog WHERE driver_id=? AND work_date BETWEEN ? AND ? ORDER BY work_date",
                    (self.driver_id, query_start.isoformat(), query_end.isoformat()),
                ).fetchall()
                seg_map = self._analysis_segments_map(con, rows)
            finally:
                con.close()

            intervals = []
            for row in rows:
                intervals.extend(core._worklog_work_intervals(row, seg_map.get(row["id"], [])))

            control_start = datetime.combine(query_start, time.min)
            control_end = datetime.combine(query_end + timedelta(days=1), time.min)
            report = rest_compliance_report(
                intervals, control_start, control_end, display_start, display_end, core.minutes_hhmm
            )

            data["warnings"] = [item for item in data.get("warnings", []) if not _rest_message(item)]
            data["info"] = [item for item in data.get("info", []) if not _rest_message(item)]
            for item in report["warnings"]:
                if item not in data["warnings"]:
                    data["warnings"].append(item)
            for item in report["info"]:
                if item not in data["info"]:
                    data["info"].append(item)
            data["daily_rests"] = report["daily_rests"]
            data["weekly_rests"] = report["weekly_rests"]
            data["rest_overlaps"] = report["overlaps"]
            data["control_basis"] = "plan"
            return data

    core._TAXO_1094_INSTALLED = True
    core.App = Taxo1094App
    return Taxo1094App
