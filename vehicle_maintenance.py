# -*- coding: utf-8 -*-
"""СТОІР: пробіг, планове ТО, заявки на ремонт і технічний контроль."""
from __future__ import annotations

from datetime import date, datetime, timedelta

PROFILE_PASSENGER_BUS = "passenger_bus"
PROFILE_TRUCK_BASED = "truck_or_truck_based_bus"
PROFILE_CUSTOM = "custom"

PROFILE_LABELS = {
    PROFILE_PASSENGER_BUS: "Легковий автомобіль / автобус",
    PROFILE_TRUCK_BASED: "Вантажний / автобус на вантажній базі / причіп",
    PROFILE_CUSTOM: "За документацією виробника / локальний профіль",
}

DEFAULT_INTERVALS_KM = {
    PROFILE_PASSENGER_BUS: {"to1": 5000, "to2": 20000},
    PROFILE_TRUCK_BASED: {"to1": 4000, "to2": 16000},
}

MAINTENANCE_TO1 = "TO-1"
MAINTENANCE_TO2 = "TO-2"
MAINTENANCE_SEASONAL = "STO"
MAINTENANCE_REPAIR = "REPAIR"

REQUEST_OPEN = "open"
REQUEST_IN_PROGRESS = "in_progress"
REQUEST_CLOSED = "closed"
REQUEST_STATUSES = (REQUEST_OPEN, REQUEST_IN_PROGRESS, REQUEST_CLOSED)
REQUEST_STATUS_LABELS = {
    REQUEST_OPEN: "Відкрита",
    REQUEST_IN_PROGRESS: "У роботі",
    REQUEST_CLOSED: "Закрита",
}
REQUEST_PRIORITIES = ("low", "normal", "high", "critical")
REQUEST_PRIORITY_LABELS = {
    "low": "Низький",
    "normal": "Звичайний",
    "high": "Високий",
    "critical": "Критичний",
}


def ensure_schema_on_connection(con):
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS vehicle_maintenance_profiles (
            vehicle_id INTEGER PRIMARY KEY REFERENCES vehicles(id) ON DELETE CASCADE,
            profile_kind TEXT NOT NULL DEFAULT 'passenger_bus',
            to1_interval_km INTEGER,
            to2_interval_km INTEGER,
            source_kind TEXT NOT NULL DEFAULT 'regulation_102',
            source_note TEXT DEFAULT '',
            warning_km INTEGER NOT NULL DEFAULT 1000,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS vehicle_maintenance_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
            event_type TEXT NOT NULL,
            event_date TEXT NOT NULL,
            odometer_km INTEGER,
            description TEXT DEFAULT '',
            performer TEXT DEFAULT '',
            document_ref TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_vehicle_maintenance_events_vehicle_date
            ON vehicle_maintenance_events(vehicle_id,event_date,id);
        CREATE TABLE IF NOT EXISTS vehicle_repair_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
            reported_at TEXT NOT NULL,
            defect TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'normal',
            status TEXT NOT NULL DEFAULT 'open',
            reporter TEXT DEFAULT '',
            assignee TEXT DEFAULT '',
            resolution TEXT DEFAULT '',
            closed_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_vehicle_repair_requests_vehicle_status
            ON vehicle_repair_requests(vehicle_id,status,reported_at DESC,id DESC);
        """
    )


def ensure_schema(core):
    con = core.db()
    try:
        ensure_schema_on_connection(con)
        con.commit()
    finally:
        con.close()


def _value(row, key, default=None):
    if row is None:
        return default
    try:
        return row[key]
    except Exception:
        return getattr(row, key, default)


def _as_iso_date(value):
    text = str(value or "").strip()
    if not text:
        return date.today().isoformat()
    if "." in text:
        return datetime.strptime(text, "%d.%m.%Y").date().isoformat()
    return date.fromisoformat(text[:10]).isoformat()


def get_profile(con, vehicle_id):
    ensure_schema_on_connection(con)
    row = con.execute("SELECT * FROM vehicle_maintenance_profiles WHERE vehicle_id=?", (int(vehicle_id),)).fetchone()
    if row:
        return row
    return {
        "vehicle_id": int(vehicle_id), "profile_kind": PROFILE_PASSENGER_BUS,
        "to1_interval_km": 5000, "to2_interval_km": 20000,
        "source_kind": "regulation_102",
        "source_note": "Положення №102; якщо виробник установив іншу періодичність, застосовується документація виробника",
        "warning_km": 1000,
    }


def save_profile(con, vehicle_id, *, profile_kind, to1_interval_km=None, to2_interval_km=None,
                 source_kind="regulation_102", source_note="", warning_km=1000):
    ensure_schema_on_connection(con)
    vehicle_id = int(vehicle_id)
    if profile_kind in DEFAULT_INTERVALS_KM:
        defaults = DEFAULT_INTERVALS_KM[profile_kind]
        to1_interval_km = int(to1_interval_km or defaults["to1"])
        to2_interval_km = int(to2_interval_km or defaults["to2"])
    else:
        if not to1_interval_km or not to2_interval_km:
            raise ValueError("Для індивідуального профілю задайте інтервали ТО-1 і ТО-2.")
        to1_interval_km, to2_interval_km = int(to1_interval_km), int(to2_interval_km)
    if to1_interval_km <= 0 or to2_interval_km <= 0:
        raise ValueError("Інтервали ТО мають бути додатними.")
    if to2_interval_km < to1_interval_km:
        raise ValueError("Інтервал ТО-2 не може бути меншим за ТО-1.")
    warning_km = max(0, int(warning_km or 0))
    con.execute(
        """INSERT INTO vehicle_maintenance_profiles(
               vehicle_id,profile_kind,to1_interval_km,to2_interval_km,source_kind,source_note,warning_km,updated_at
           ) VALUES(?,?,?,?,?,?,?,?)
           ON CONFLICT(vehicle_id) DO UPDATE SET
               profile_kind=excluded.profile_kind,to1_interval_km=excluded.to1_interval_km,
               to2_interval_km=excluded.to2_interval_km,source_kind=excluded.source_kind,
               source_note=excluded.source_note,warning_km=excluded.warning_km,updated_at=excluded.updated_at""",
        (vehicle_id, profile_kind, to1_interval_km, to2_interval_km, source_kind,
         str(source_note or ""), warning_km, datetime.now().isoformat(timespec="seconds")),
    )


def latest_odometer(con, vehicle_id):
    """Останній фактичний одометр без залежності від необов'язкових legacy-колонок."""
    return con.execute(
        """SELECT reading_km,reading_at,source_type
           FROM vehicle_odometer_readings
           WHERE vehicle_id=? AND reading_km IS NOT NULL
           ORDER BY CASE WHEN COALESCE(reading_at,'')='' THEN 1 ELSE 0 END, reading_at DESC,id DESC LIMIT 1""",
        (int(vehicle_id),),
    ).fetchone()


def record_event(con, vehicle_id, event_type, event_date, *, odometer_km=None,
                 description="", performer="", document_ref="", notes=""):
    ensure_schema_on_connection(con)
    con.execute(
        """INSERT INTO vehicle_maintenance_events(
               vehicle_id,event_type,event_date,odometer_km,description,performer,document_ref,notes
           ) VALUES(?,?,?,?,?,?,?,?)""",
        (int(vehicle_id), str(event_type), _as_iso_date(event_date),
         None if odometer_km in (None, "") else int(odometer_km), str(description or ""),
         str(performer or ""), str(document_ref or ""), str(notes or "")),
    )


def last_event(con, vehicle_id, event_type):
    ensure_schema_on_connection(con)
    return con.execute(
        "SELECT * FROM vehicle_maintenance_events WHERE vehicle_id=? AND event_type=? ORDER BY event_date DESC,id DESC LIMIT 1",
        (int(vehicle_id), str(event_type)),
    ).fetchone()


def next_due_by_mileage(current_odometer, last_service_odometer, interval_km):
    if current_odometer is None or last_service_odometer is None or not interval_km:
        return None
    due = int(last_service_odometer) + int(interval_km)
    return {"due_odometer_km": due, "remaining_km": due - int(current_odometer)}


def maintenance_status(remaining_km, warning_km=1000):
    if remaining_km is None:
        return "unknown"
    if int(remaining_km) < 0:
        return "overdue"
    if int(remaining_km) <= int(warning_km or 0):
        return "due_soon"
    return "ok"


def average_daily_mileage(con, vehicle_id, *, lookback_days=60):
    """Середній фактичний пробіг/день між найстарішим і найновішим показником у вікні."""
    rows = con.execute(
        """SELECT reading_km,reading_at FROM vehicle_odometer_readings
           WHERE vehicle_id=? AND reading_km IS NOT NULL AND COALESCE(reading_at,'')<>''
           ORDER BY reading_at DESC,id DESC LIMIT 250""", (int(vehicle_id),)
    ).fetchall()
    points = []
    cutoff = date.today() - timedelta(days=max(7, int(lookback_days or 60)))
    for row in rows:
        try:
            day = date.fromisoformat(str(row["reading_at"])[:10])
            km = int(row["reading_km"])
        except Exception:
            continue
        if day >= cutoff:
            points.append((day, km))
    if len(points) < 2:
        return None
    newest = max(points, key=lambda p: (p[0], p[1]))
    oldest = min(points, key=lambda p: (p[0], p[1]))
    days = (newest[0] - oldest[0]).days
    distance = newest[1] - oldest[1]
    if days <= 0 or distance <= 0:
        return None
    return distance / float(days)


def forecast_due_date(remaining_km, avg_daily_km, *, from_date=None):
    if remaining_km is None or not avg_daily_km or avg_daily_km <= 0:
        return None
    start = from_date or date.today()
    if int(remaining_km) <= 0:
        return start
    days = max(1, int(round(float(remaining_km) / float(avg_daily_km))))
    return start + timedelta(days=days)


def vehicle_plan(con, vehicle_id):
    profile = get_profile(con, vehicle_id)
    od = latest_odometer(con, vehicle_id)
    current = _value(od, "reading_km")
    warning = int(_value(profile, "warning_km", 1000) or 0)
    avg_daily = average_daily_mileage(con, vehicle_id)
    result = {"vehicle_id": int(vehicle_id), "current_odometer_km": current,
              "profile": profile, "average_daily_km": avg_daily}
    for event_type, key, field in ((MAINTENANCE_TO1, "to1", "to1_interval_km"), (MAINTENANCE_TO2, "to2", "to2_interval_km")):
        event = last_event(con, vehicle_id, event_type)
        due = next_due_by_mileage(current, _value(event, "odometer_km"), _value(profile, field))
        result[key] = {
            "last_event": event, "due": due,
            "status": maintenance_status(due["remaining_km"], warning) if due else "unknown",
            "forecast_date": forecast_due_date(due["remaining_km"], avg_daily) if due else None,
        }
    return result


def create_repair_request(con, vehicle_id, defect, *, priority="normal", reporter="", assignee="", reported_at=None):
    ensure_schema_on_connection(con)
    defect = str(defect or "").strip()
    if not defect:
        raise ValueError("Опишіть несправність або потрібний ремонт.")
    priority = str(priority or "normal")
    if priority not in REQUEST_PRIORITIES:
        raise ValueError("Невідомий пріоритет заявки.")
    stamp = str(reported_at or datetime.now().isoformat(timespec="seconds"))
    cur = con.execute(
        """INSERT INTO vehicle_repair_requests(vehicle_id,reported_at,defect,priority,status,reporter,assignee,updated_at)
           VALUES(?,?,?,?,?,?,?,?)""",
        (int(vehicle_id), stamp, defect, priority, REQUEST_OPEN, str(reporter or ""), str(assignee or ""), datetime.now().isoformat(timespec="seconds")),
    )
    return cur.lastrowid


def update_repair_request(con, request_id, *, status=None, assignee=None, resolution=None):
    ensure_schema_on_connection(con)
    row = con.execute("SELECT * FROM vehicle_repair_requests WHERE id=?", (int(request_id),)).fetchone()
    if row is None:
        raise ValueError("Заявку не знайдено.")
    new_status = str(status or row["status"])
    if new_status not in REQUEST_STATUSES:
        raise ValueError("Невідомий статус заявки.")
    new_assignee = row["assignee"] if assignee is None else str(assignee or "")
    new_resolution = row["resolution"] if resolution is None else str(resolution or "")
    closed_at = row["closed_at"]
    if new_status == REQUEST_CLOSED and not closed_at:
        closed_at = datetime.now().isoformat(timespec="seconds")
    elif new_status != REQUEST_CLOSED:
        closed_at = None
    con.execute(
        """UPDATE vehicle_repair_requests SET status=?,assignee=?,resolution=?,closed_at=?,updated_at=? WHERE id=?""",
        (new_status, new_assignee, new_resolution, closed_at, datetime.now().isoformat(timespec="seconds"), int(request_id)),
    )


def repair_requests(con, vehicle_id=None, *, include_closed=True):
    ensure_schema_on_connection(con)
    where, args = [], []
    if vehicle_id is not None:
        where.append("vehicle_id=?"); args.append(int(vehicle_id))
    if not include_closed:
        where.append("status<>?"); args.append(REQUEST_CLOSED)
    sql = "SELECT * FROM vehicle_repair_requests"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY CASE priority WHEN 'critical' THEN 0 WHEN 'high' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END, reported_at DESC,id DESC"
    return con.execute(sql, tuple(args)).fetchall()


def fleet_maintenance_report(con):
    """Компактне зведення СТОІР по всіх активних ТЗ для екрану/експорту."""
    ensure_schema_on_connection(con)
    vehicles = con.execute("SELECT id,plate,name,make_model FROM vehicles WHERE COALESCE(active,1)=1 ORDER BY COALESCE(plate,''),id").fetchall()
    rows = []
    for vehicle in vehicles:
        plan = vehicle_plan(con, int(vehicle["id"]))
        open_count = con.execute("SELECT COUNT(*) FROM vehicle_repair_requests WHERE vehicle_id=? AND status<>?", (int(vehicle["id"]), REQUEST_CLOSED)).fetchone()[0]
        rows.append({"vehicle": vehicle, "plan": plan, "open_requests": int(open_count or 0)})
    return rows
