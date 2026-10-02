# -*- coding: utf-8 -*-
"""Taxo 10.4-r4: visible schedule audit and route-boundary input checks."""
from datetime import datetime, timedelta

APP_VERSION = "10.4-r4"


def _value(row, key, default=""):
    if row is None:
        return default
    try:
        if key in row.keys():
            return row[key]
    except Exception:
        pass
    if isinstance(row, dict):
        return row.get(key, default)
    return default


def _clock_minutes(value, day_offset=0):
    text=str(value or "").strip()
    if not text:
        return None
    try:
        hh, mm = [int(x) for x in text.split(":", 1)]
    except Exception:
        return None
    return int(day_offset or 0) * 1440 + hh * 60 + mm


def _route_boundary_times(stops, start_direction="outbound"):
    """Read entered route boundary times for audit only; never alter waybill data."""
    rows=list(stops or [])
    direction=str(start_direction or "outbound").strip().lower()
    if direction not in ("outbound", "return"):
        direction="outbound"
    finish="return" if direction=="outbound" else "outbound"
    starts=[r for r in rows if str(_value(r,"direction","")).strip()==direction]
    ends=[r for r in rows if str(_value(r,"direction","")).strip()==finish]
    starts.sort(key=lambda r:int(_value(r,"stop_no",0) or 0))
    ends.sort(key=lambda r:int(_value(r,"stop_no",0) or 0))
    result={
        "start_time":"", "start_day_offset":0, "start_stop":"",
        "end_time":"", "end_day_offset":0, "end_stop":"",
    }
    if starts:
        row=starts[0]
        dep=str(_value(row,"departure_time","") or "").strip()
        arr=str(_value(row,"arrival_time","") or "").strip()
        if dep:
            result["start_time"]=dep
            result["start_day_offset"]=int(_value(row,"departure_day_offset",_value(row,"day_offset",0)) or 0)
        elif arr:
            result["start_time"]=arr
            result["start_day_offset"]=int(_value(row,"arrival_day_offset",_value(row,"day_offset",0)) or 0)
        result["start_stop"]=str(_value(row,"stop_name","") or "").strip()
    if ends:
        row=ends[-1]
        arr=str(_value(row,"arrival_time","") or "").strip()
        dep=str(_value(row,"departure_time","") or "").strip()
        if arr:
            result["end_time"]=arr
            result["end_day_offset"]=int(_value(row,"arrival_day_offset",_value(row,"day_offset",0)) or 0)
        elif dep:
            result["end_time"]=dep
            result["end_day_offset"]=int(_value(row,"departure_day_offset",_value(row,"day_offset",0)) or 0)
        result["end_stop"]=str(_value(row,"stop_name","") or "").strip()
    return result


def _segment_boundary(segments, fallback=None, start_offset=0, end_offset=0):
    rows=list(segments or [])
    starts=[]; ends=[]
    for row in rows:
        s=str(_value(row,"start_time","") or "").strip()
        e=str(_value(row,"end_time","") or "").strip()
        if s: starts.append(s)
        if e: ends.append(e)
    if starts and ends:
        return {
            "start_time":starts[0], "start_day_offset":int(start_offset or 0),
            "end_time":ends[-1], "end_day_offset":int(end_offset or 0),
        }
    fallback=fallback or {}
    return {
        "start_time":str(_value(fallback,"start_time","") or "").strip(),
        "start_day_offset":int(start_offset or 0),
        "end_time":str(_value(fallback,"end_time","") or "").strip(),
        "end_day_offset":int(end_offset or 0),
    }


def _boundary_mismatch_findings(segment_boundary, stop_boundary, base):
    findings=[]
    for side,label,kind in (
        ("start","Виїзд із АТП","route_start_boundary_mismatch"),
        ("end","Заїзд в АТП","route_end_boundary_mismatch"),
    ):
        seg_time=segment_boundary.get(side+"_time","")
        stop_time=stop_boundary.get(side+"_time","")
        if not seg_time or not stop_time:
            continue
        seg_offset=int(segment_boundary.get(side+"_day_offset",0) or 0)
        stop_offset=int(stop_boundary.get(side+"_day_offset",0) or 0)
        seg_min=_clock_minutes(seg_time,seg_offset)
        stop_min=_clock_minutes(stop_time,stop_offset)
        if seg_min is None or stop_min is None or seg_min==stop_min:
            continue
        delta=abs(seg_min-stop_min)
        point=stop_boundary.get(side+"_stop","") or "крайня точка маршруту"
        item=dict(base)
        item.update({
            "kind":kind,
            "label":label+" не збігається",
            "minutes":delta,
            "message":(
                "%s: часові частини маршруту дають %s, а таблиця точок (%s) — %s. "
                "Перевірте введення графіка маршруту."
                % (label, seg_time, point, stop_time)
            ),
        })
        findings.append(item)
    return findings


def _period_bounds(year, month, work_date=None):
    if work_date:
        day=work_date.isoformat() if hasattr(work_date,"isoformat") else str(work_date)
        return day, day
    start="%04d-%02d-01" % (int(year),int(month))
    if int(month)==12:
        next_month=datetime(int(year)+1,1,1)
    else:
        next_month=datetime(int(year),int(month)+1,1)
    return start,(next_month-timedelta(days=1)).strftime("%Y-%m-%d")


def augment_schedule_audit(core, original, year, month, active_routes_only=True,
                           work_date=None, include_days=True, include_routes=True):
    data=original(year,month,active_routes_only=active_routes_only,work_date=work_date,
                  include_days=include_days,include_routes=include_routes)
    findings=list(data.get("findings") or [])
    con=core.db()
    try:
        if include_days:
            start,end=_period_bounds(year,month,work_date)
            rows=con.execute(
                """SELECT w.id,w.driver_id,w.work_date,w.route_id,w.route_name,w.start_time,w.end_time,
                          d.last_name,d.first_name,d.middle_name,
                          r.name AS catalog_name,r.code AS route_code,
                          r.start_direction,r.start_day_offset,r.end_day_offset
                     FROM worklog w
                     JOIN drivers d ON d.id=w.driver_id
                LEFT JOIN routes r ON r.id=w.route_id
                    WHERE w.work_date BETWEEN ? AND ? AND w.route_id IS NOT NULL
                 ORDER BY w.work_date,w.id""",(start,end)
            ).fetchall()
            for row in rows:
                route_id=_value(row,"route_id",None)
                if not route_id:
                    continue
                segs=con.execute(
                    "SELECT * FROM work_segments WHERE worklog_id=? ORDER BY segment_no",(row["id"],)
                ).fetchall()
                stops=con.execute(
                    "SELECT * FROM route_stops WHERE route_id=? ORDER BY direction,stop_no",(route_id,)
                ).fetchall()
                seg=_segment_boundary(segs,row,_value(row,"start_day_offset",0),_value(row,"end_day_offset",0))
                stop=_route_boundary_times(stops,_value(row,"start_direction","outbound"))
                driver=" ".join(x for x in (
                    str(_value(row,"last_name","") or "").strip(),
                    str(_value(row,"first_name","") or "").strip(),
                    str(_value(row,"middle_name","") or "").strip()) if x)
                route_name=str(_value(row,"catalog_name","") or _value(row,"route_name","") or "").strip()
                route_code=str(_value(row,"route_code","") or "").strip()
                base={
                    "source_kind":"worklog","source":"День водія","worklog_id":row["id"],
                    "driver_id":row["driver_id"],"route_id":route_id,"date":row["work_date"],
                    "subject":driver,"route":" / ".join(x for x in (route_code,route_name) if x),
                }
                findings.extend(_boundary_mismatch_findings(seg,stop,base))

        if include_routes:
            where="WHERE active=1" if active_routes_only else ""
            routes=con.execute(
                "SELECT id,name,code,active,start_direction,start_day_offset,end_day_offset FROM routes %s ORDER BY code,name,id" % where
            ).fetchall()
            for route_row in routes:
                segs=con.execute(
                    "SELECT * FROM route_segments WHERE route_id=? ORDER BY segment_no",(route_row["id"],)
                ).fetchall()
                stops=con.execute(
                    "SELECT * FROM route_stops WHERE route_id=? ORDER BY direction,stop_no",(route_row["id"],)
                ).fetchall()
                if not segs or not stops:
                    continue
                seg=_segment_boundary(segs,None,_value(route_row,"start_day_offset",0),_value(route_row,"end_day_offset",0))
                stop=_route_boundary_times(stops,_value(route_row,"start_direction","outbound"))
                route=" / ".join(x for x in (
                    str(_value(route_row,"code","") or "").strip(),
                    str(_value(route_row,"name","") or "").strip()) if x)
                base={
                    "source_kind":"route","source":"Шаблон маршруту","worklog_id":None,
                    "driver_id":None,"route_id":route_row["id"],"date":"",
                    "subject":route,"route":route,
                }
                findings.extend(_boundary_mismatch_findings(seg,stop,base))
    finally:
        con.close()

    unique=[]; seen=set()
    for item in findings:
        key=(item.get("source_kind"),item.get("worklog_id"),item.get("route_id"),
             item.get("kind"),item.get("date"),item.get("message"))
        if key in seen:
            continue
        seen.add(key); unique.append(item)
    data["findings"]=unique
    data["day_findings"]=sum(1 for x in unique if x.get("source_kind")=="worklog")
    data["route_findings"]=sum(1 for x in unique if x.get("source_kind")=="route")
    return data


def install(core, base_app):
    if getattr(core,"_TAXO_1044_INSTALLED",False):
        return core.App
    core.APP_VERSION=APP_VERSION
    original_audit=core.collect_schedule_integrity_audit

    def collect_schedule_integrity_audit(year,month,active_routes_only=True,work_date=None,
                                         include_days=True,include_routes=True):
        return augment_schedule_audit(
            core,original_audit,year,month,active_routes_only,work_date,include_days,include_routes
        )
    core.collect_schedule_integrity_audit=collect_schedule_integrity_audit

    class Taxo1044App(base_app):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

        def refresh_schedule_integrity_audit(self):
            try:
                result=super().refresh_schedule_integrity_audit()
            except Exception as exc:
                if hasattr(self,"schedule_audit_result"):
                    self.schedule_audit_result.set("⚠ Помилка виконання аудиту")
                if hasattr(self,"schedule_audit_summary"):
                    self.schedule_audit_summary.set("Перевірка не завершена: %s" % exc)
                tree=getattr(self,"schedule_audit_tree",None)
                if tree is not None and tree.winfo_exists():
                    for item in tree.get_children(): tree.delete(item)
                    tree.insert("","end",values=(
                        "Система","—","—","—","Помилка аудиту","—",str(exc)
                    ),tags=("audit-error",))
                    tree.tag_configure("audit-error",foreground="#8A1C1C")
                return None
            tree=getattr(self,"schedule_audit_tree",None)
            if tree is not None and tree.winfo_exists() and not tree.get_children():
                status=(self.schedule_audit_result.get() if hasattr(self,"schedule_audit_result") else "Перевірку завершено")
                summary=(self.schedule_audit_summary.get() if hasattr(self,"schedule_audit_summary") else "")
                ok=status.startswith("✓")
                tree.insert("","end",values=(
                    "Перевірка","—","—","—",status.lstrip("✓○ "),"—",summary
                ),tags=("audit-ok" if ok else "audit-info",))
                tree.tag_configure("audit-ok",foreground="#1B5E20")
                tree.tag_configure("audit-info",foreground="#555555")
            return result

    Taxo1044App.__name__="App"
    Taxo1044App.__qualname__="App"
    core.App=Taxo1044App
    core._TAXO_1044_INSTALLED=True
    return Taxo1044App
