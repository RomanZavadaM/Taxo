# -*- coding: utf-8 -*-
"""СТОІР: пробіг, планове ТО та обов'язковий технічний контроль.

Модуль не замінює юридичний реєстр документів ТЗ. Він використовує фактичний
журнал одометра як джерело пробігу та будує експлуатаційний план. ОТК ведеться
як окрема контрольна вісь: протокол/строк придатності не є ТО-1/ТО-2.
"""
from __future__ import annotations

from datetime import date, datetime

PROFILE_PASSENGER_BUS = "passenger_bus"
PROFILE_TRUCK_BASED = "truck_or_truck_based_bus"
PROFILE_CUSTOM = "custom"

PROFILE_LABELS = {
    PROFILE_PASSENGER_BUS: "Легковий автомобіль / автобус",
    PROFILE_TRUCK_BASED: "Вантажний / автобус на вантажній базі / причіп",
    PROFILE_CUSTOM: "За документацією виробника / локальний профіль",
}

# Базові інтервали Положення №102. Якщо документація виробника встановлює
# іншу періодичність, у Taxo створюється індивідуальний профіль.
DEFAULT_INTERVALS_KM = {
    PROFILE_PASSENGER_BUS: {"to1": 5000, "to2": 20000},
    PROFILE_TRUCK_BASED: {"to1": 4000, "to2": 16000},
}

MAINTENANCE_TO1 = "TO-1"
MAINTENANCE_TO2 = "TO-2"
MAINTENANCE_SEASONAL = "STO"
MAINTENANCE_REPAIR = "REPAIR"


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


def get_profile(con, vehicle_id):
    ensure_schema_on_connection(con)
    row = con.execute(
        "SELECT * FROM vehicle_maintenance_profiles WHERE vehicle_id=?",
        (int(vehicle_id),),
    ).fetchone()
    if row:
        return row
    return {
        "vehicle_id": int(vehicle_id),
        "profile_kind": PROFILE_PASSENGER_BUS,
        "to1_interval_km": 5000,
        "to2_interval_km": 20000,
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
        to1_interval_km = int(to1_interval_km)
        to2_interval_km = int(to2_interval_km)
    if to1_interval_km <= 0 or to2_interval_km <= 0:
        raise ValueError("Інтервали ТО мають бути додатними.")
    if to2_interval_km < to1_interval_km:
        raise ValueError("Інтервал ТО-2 не може бути меншим за ТО-1.")
    warning_km = max(0, int(warning_km or 0))
    con.execute(
        """INSERT INTO vehicle_maintenance_profiles(
               vehicle_id,profile_kind,to1_interval_km,to2_interval_km,
               source_kind,source_note,warning_km,updated_at
           ) VALUES(?,?,?,?,?,?,?,?)
           ON CONFLICT(vehicle_id) DO UPDATE SET
               profile_kind=excluded.profile_kind,
               to1_interval_km=excluded.to1_interval_km,
               to2_interval_km=excluded.to2_interval_km,
               source_kind=excluded.source_kind,
               source_note=excluded.source_note,
               warning_km=excluded.warning_km,
               updated_at=excluded.updated_at""",
        (vehicle_id, profile_kind, to1_interval_km, to2_interval_km,
         source_kind, str(source_note or ""), warning_km,
         datetime.now().isoformat(timespec="seconds")),
    )


def latest_odometer(con, vehicle_id):
    """Повернути останній фактичний показник з наявного журналу шляхівок."""
    return con.execute(
        """SELECT reading_km,reading_at,source_type,worklog_id
           FROM vehicle_odometer_readings
           WHERE vehicle_id=? AND reading_km IS NOT NULL
           ORDER BY CASE WHEN COALESCE(reading_at,'')='' THEN 1 ELSE 0 END,
                    reading_at DESC,id DESC
           LIMIT 1""",
        (int(vehicle_id),),
    ).fetchone()


def record_event(con, vehicle_id, event_type, event_date, *, odometer_km=None,
                 description="", performer="", document_ref="", notes=""):
    ensure_schema_on_connection(con)
    text = str(event_date or "").strip()
    event_date_iso = datetime.strptime(text, "%d.%m.%Y").date().isoformat() if "." in text else date.fromisoformat(text).isoformat()
    con.execute(
        """INSERT INTO vehicle_maintenance_events(
               vehicle_id,event_type,event_date,odometer_km,description,
               performer,document_ref,notes
           ) VALUES(?,?,?,?,?,?,?,?)""",
        (int(vehicle_id), str(event_type), event_date_iso,
         None if odometer_km in (None, "") else int(odometer_km),
         str(description or ""), str(performer or ""), str(document_ref or ""), str(notes or "")),
    )


def last_event(con, vehicle_id, event_type):
    ensure_schema_on_connection(con)
    return con.execute(
        """SELECT * FROM vehicle_maintenance_events
           WHERE vehicle_id=? AND event_type=?
           ORDER BY event_date DESC,id DESC LIMIT 1""",
        (int(vehicle_id), str(event_type)),
    ).fetchone()


def next_due_by_mileage(current_odometer, last_service_odometer, interval_km):
    """Розрахувати наступний пробіг і залишок до ТО.

    Якщо попереднє ТО невідоме, нічого не вигадуємо — повертаємо None.
    """
    if current_odometer is None or last_service_odometer is None or not interval_km:
        return None
    current = int(current_odometer)
    last = int(last_service_odometer)
    due = last + int(interval_km)
    return {"due_odometer_km": due, "remaining_km": due - current}


def maintenance_status(remaining_km, warning_km=1000):
    if remaining_km is None:
        return "unknown"
    if int(remaining_km) < 0:
        return "overdue"
    if int(remaining_km) <= int(warning_km or 0):
        return "due_soon"
    return "ok"


def vehicle_plan(con, vehicle_id):
    profile = get_profile(con, vehicle_id)
    od = latest_odometer(con, vehicle_id)
    current = _value(od, "reading_km")
    warning = int(_value(profile, "warning_km", 1000) or 0)
    result = {"vehicle_id": int(vehicle_id), "current_odometer_km": current, "profile": profile}
    for event_type, key, field in (
        (MAINTENANCE_TO1, "to1", "to1_interval_km"),
        (MAINTENANCE_TO2, "to2", "to2_interval_km"),
    ):
        event = last_event(con, vehicle_id, event_type)
        due = next_due_by_mileage(current, _value(event, "odometer_km"), _value(profile, field))
        result[key] = {
            "last_event": event,
            "due": due,
            "status": maintenance_status(due["remaining_km"], warning) if due else "unknown",
        }
    return result
