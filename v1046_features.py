# -*- coding: utf-8 -*-
"""Taxo 10.4-r6: 2026 regulation-340 rest timeline and plan/fact semantics.

The legacy control treated every worklog row as one solid duty envelope and
then measured only the gap between adjacent rows.  That creates false daily
rest findings for split duties, especially when a qualifying night rest sits
between two work parts stored in the same worklog day.

This layer keeps the existing planning calculations, but replaces the daily /
weekly rest part with an exact interval timeline and labels plan-derived legal
checks as PLAN.  It also supports the current ordinary daily-rest split model
3h + 9h.  It never invents factual data from a route/waybill plan.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

APP_VERSION = "10.4-r6"


def _minutes(delta):
    return max(0, int(round(delta.total_seconds() / 60.0)))


def merge_intervals(intervals):
    """Merge overlapping/touching datetime intervals without filling real gaps."""
    ordered=sorted((a,b) for a,b in intervals if a is not None and b is not None and b>a)
    merged=[]
    for start,end in ordered:
        if not merged or start>merged[-1][1]:
            merged.append([start,end])
        elif end>merged[-1][1]:
            merged[-1][1]=end
    return [(a,b) for a,b in merged]


def free_gaps(intervals):
    """Return every real non-work gap between exact work intervals."""
    merged=merge_intervals(intervals)
    result=[]
    for left,right in zip(merged,merged[1:]):
        if right[0] <= left[1]:
            continue
        result.append({
            "start":left[1],
            "end":right[0],
            "minutes":_minutes(right[0]-left[1]),
            "next_date":right[0].date(),
        })
    return result


def classify_rest_gaps(gaps):
    """Classify exact gaps under the 2026 daily-rest model.

    Important: a short gap is not automatically a failed daily rest.  Gaps of
    3..8:59 are kept as possible first parts of an ordinary split daily rest;
    a later >=9h second part can complete the 3+9 model.  Therefore we do not
    reproduce the legacy false positive "every gap <9h is an error".
    """
    daily=[]
    weekly=[]
    pending=[]

    for raw in sorted(gaps,key=lambda x:x["start"]):
        gap=dict(raw)
        minutes=int(gap["minutes"])

        # Drop stale first-parts.  A 3+9 pair must belong to the same daily
        # cycle; this conservative 24h cap prevents pairing unrelated days.
        pending=[p for p in pending if gap["start"]-p["start"] <= timedelta(hours=24)]

        if minutes>=24*60:
            gap["kind"]="weekly_regular" if minutes>=45*60 else "weekly_reduced"
            weekly.append(gap)
            pending=[]
            continue

        if minutes>=11*60:
            gap["kind"]="daily_regular"
            gap["split"]=False
            daily.append(gap)
            pending=[]
            continue

        if minutes>=9*60:
            first=pending[-1] if pending else None
            if first is not None:
                # Current ordinary daily rest may be split: first >=3h,
                # second >=9h.  Keep exact components for audit/explanation.
                event={
                    "start":first["start"],
                    "end":gap["end"],
                    "minutes":int(first["minutes"])+minutes,
                    "next_date":gap["next_date"],
                    "kind":"daily_regular",
                    "split":True,
                    "first_start":first["start"],
                    "first_end":first["end"],
                    "first_minutes":int(first["minutes"]),
                    "second_start":gap["start"],
                    "second_end":gap["end"],
                    "second_minutes":minutes,
                    "qualifying_start":gap["start"],
                }
                daily.append(event)
                pending=[]
            else:
                gap["kind"]="daily_reduced"
                gap["split"]=False
                daily.append(gap)
            continue

        if minutes>=3*60:
            pending.append(gap)
            continue

        # <3h is simply an internal break/gap here.  It may matter for other
        # controls, but it is not by itself evidence of a daily-rest violation.

    return daily,weekly


def _event_qualifying_start(event):
    return event.get("qualifying_start") or event["start"]


def rest_timeline_report(intervals, month_start, month_end, hhmm):
    """Build daily/weekly rest events and conservative planning findings."""
    gaps=free_gaps(intervals)
    daily,weekly=classify_rest_gaps(gaps)
    events=sorted([*daily,*weekly],key=lambda x:x["end"])
    warnings=[]
    info=[]

    # Explain split 3+9 explicitly; the legacy UI renderer only knows the
    # generic daily_regular kind.
    for ev in daily:
        if ev.get("split") and month_start<=ev["next_date"]<=month_end:
            info.append(
                "ПЛАН: перед %s звичайний щоденний відпочинок сформовано як "
                "%s + %s (модель 3+9)." % (
                    ev["next_date"].strftime("%d.%m.%Y"),
                    hhmm(ev["first_minutes"]),
                    hhmm(ev["second_minutes"]),
                )
            )

    # Reduced daily rests: no more than three between weekly rests.
    reduced_since_weekly=0
    for ev in events:
        if ev["kind"].startswith("weekly_"):
            reduced_since_weekly=0
            continue
        if ev["kind"]=="daily_reduced":
            reduced_since_weekly+=1
            if month_start<=ev["next_date"]<=month_end:
                info.append(
                    "ПЛАН: перед %s скорочений щоденний відпочинок %s; номер %d "
                    "після останнього щотижневого." % (
                        ev["next_date"].strftime("%d.%m.%Y"),
                        hhmm(ev["minutes"]),
                        reduced_since_weekly,
                    )
                )
                if reduced_since_weekly>3:
                    warnings.append(
                        "ПЛАН: перед %s це вже %d-й скорочений щоденний відпочинок "
                        "між щотижневими періодами (>3)." % (
                            ev["next_date"].strftime("%d.%m.%Y"),
                            reduced_since_weekly,
                        )
                    )

    # 24h rule.  We do NOT call a 3h/4h daytime gap itself a violation.  A
    # warning appears only when, after a known qualifying daily/weekly rest,
    # the next >=9h qualifying part starts too late to provide 9h inside the
    # following 24h period.
    for prev,next_ in zip(events,events[1:]):
        anchor=prev["end"]
        next_start=_event_qualifying_start(next_)
        latest_start=anchor+timedelta(hours=15)
        if next_start>latest_start:
            deadline=anchor+timedelta(hours=24)
            if deadline.date()>=month_start and anchor.date()<=month_end:
                warnings.append(
                    "ПЛАН: після завершення відпочинку %s наступний кваліфікований "
                    "період >=9:00 починається лише %s; перевірити 24-годинне правило "
                    "щоденного відпочинку." % (
                        anchor.strftime("%d.%m.%Y %H:%M"),
                        next_start.strftime("%d.%m.%Y %H:%M"),
                    )
                )

    # Weekly reduced rest and six-24h planning check, now from exact gaps.
    for ev in weekly:
        if ev["kind"]=="weekly_reduced":
            deficit=45*60-int(ev["minutes"])
            monday=ev["start"].date()-timedelta(days=ev["start"].date().weekday())
            due=monday+timedelta(days=27)
            if ev["end"].date()>=month_start and ev["start"].date()<=month_end:
                info.append(
                    "ПЛАН: щотижневий відпочинок %s-%s: %s, скорочений. "
                    "Нестача до 45:00 = %s; компенсацію проконтролювати до %s." % (
                        ev["start"].strftime("%d.%m %H:%M"),
                        ev["end"].strftime("%d.%m %H:%M"),
                        hhmm(ev["minutes"]),hhmm(deficit),due.strftime("%d.%m.%Y"),
                    )
                )

    for prev,next_ in zip(weekly,weekly[1:]):
        span=_minutes(next_["start"]-prev["end"])
        if span>6*24*60 and next_["start"].date()>=month_start and prev["end"].date()<=month_end:
            warnings.append(
                "ПЛАН: між завершенням щотижневого відпочинку %s і початком наступного %s "
                "минуло %s — більше шести 24-годинних періодів." % (
                    prev["end"].strftime("%d.%m %H:%M"),
                    next_["start"].strftime("%d.%m %H:%M"),hhmm(span),
                )
            )

    daily_display=[ev for ev in daily if month_start<=ev["next_date"]<=month_end]
    weekly_display=[ev for ev in weekly if ev["end"].date()>=month_start and ev["start"].date()<=month_end]
    return {
        "daily_rests":daily_display,
        "weekly_rests":weekly_display,
        "warnings":warnings,
        "info":info,
        "gaps":gaps,
    }


def _is_old_rest_warning(text):
    value=str(text or "")
    return (
        (value.startswith("Перед ") and ("міжзмінний відпочинок" in value or "скорочений щоденний відпочинок" in value))
        or "Між завершенням щотижневого відпочинку" in value
    )


def _is_old_rest_info(text):
    value=str(text or "")
    return (
        (value.startswith("Перед ") and "скорочений щоденний відпочинок" in value)
        or value.startswith("Щотижневий відпочинок ")
    )


def _prefix_plan(text):
    value=str(text or "")
    if not value or value.startswith(("ПЛАН:","ФАКТ:")):
        return value
    return "ПЛАН: "+value


def install(core, base_app):
    if getattr(core,"_TAXO_1046_INSTALLED",False):
        return core.App
    core.APP_VERSION=APP_VERSION

    class Taxo1046App(base_app):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

        def calculate_work_analysis(self):
            data=super().calculate_work_analysis()
            if data is None or not getattr(self,"driver_id",None):
                return data

            year=int(self.year_var.get()); month=int(self.month_var.get())
            month_start=date(year,month,1)
            month_end=core.month_dates(year,month)[-1]
            rest_start=month_start-timedelta(days=45)
            rest_end=month_end+timedelta(days=14)

            con=core.db()
            try:
                rows=con.execute(
                    "SELECT * FROM worklog WHERE driver_id=? AND work_date BETWEEN ? AND ? ORDER BY work_date",
                    (self.driver_id,rest_start.isoformat(),rest_end.isoformat()),
                ).fetchall()
                seg_map=self._analysis_segments_map(con,rows)
            finally:
                con.close()

            # IMPORTANT: this is the planning timeline.  It uses exact work
            # pieces, never one min(start)..max(end) envelope.  Thus a real
            # night-sized gap inside a split planned duty remains visible.
            intervals=[]
            factual_rows=0
            for row in rows:
                segs=seg_map.get(row["id"],[])
                intervals.extend(core._worklog_work_intervals(row,segs))
                if core._worklog_has_fact_override(row):
                    factual_rows+=1

            rest=rest_timeline_report(intervals,month_start,month_end,core.minutes_hhmm)

            # Remove only the obsolete rest messages from the legacy result;
            # keep driving/work-time checks, but identify them honestly as PLAN.
            warnings=[w for w in data.get("warnings",[]) if not _is_old_rest_warning(w)]
            info=[i for i in data.get("info",[]) if not _is_old_rest_info(i)]
            data["warnings"]=[_prefix_plan(w) for w in warnings]
            data["warnings"].extend(rest["warnings"])
            data["info"]=[_prefix_plan(i) for i in info]
            data["info"].insert(0,
                "ПЛАНОВА ПЕРЕВІРКА: графік/маршрут і зворот шляхівки є планом. "
                "Ці зауваження не встановлюють фактичного порушення. Факт має походити "
                "з фактичних полів, тахографа та підтверджених фактичних документів; "
                "рукописний факт шляхівки Taxo не може вважати цифровим фактом, доки його не внесено."
            )
            if factual_rows:
                data["info"].insert(1,
                    "У %d записах є окремі fact_work_* межі. Вони збережені окремо від плану; "
                    "плановий контроль не підміняє ними маршрут." % factual_rows
                )
            data["info"].extend(rest["info"])
            data["daily_rests"]=rest["daily_rests"]
            data["weekly_rests"]=rest["weekly_rests"]
            data["control_basis"]="plan"
            data["factual_rows"]=factual_rows
            return data

    core._TAXO_1046_INSTALLED=True
    core.App=Taxo1046App
    return Taxo1046App
