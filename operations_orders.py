# -*- coding: utf-8 -*-
"""Taxo 10.7-r4 — експлуатація, накази та закріплення водіїв.

Наказ і пов'язані з ним дані зберігаються як структуровані записи. Друкований
PDF є представленням даних, а не єдиним джерелом. Внутрішній статус
«Затверджено» не блокує виправлення: паперовий оригінал залишається юридично
значущим примірником, а Taxo веде історію змін і попереджає про необхідність
звірити/перевидати друкований документ після редагування.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from xml.sax.saxutils import escape

APP_VERSION = "10.7-r4"

ORDER_DRAFT = "draft"
ORDER_APPROVED = "approved"
ORDER_CANCELLED = "cancelled"
ORDER_STATUS_LABELS = {
    ORDER_DRAFT: "Чернетка",
    ORDER_APPROVED: "Затверджено",
    ORDER_CANCELLED: "Скасовано",
}

TYPE_VEHICLE_ASSIGNMENT = "vehicle_assignment"
TYPE_STORAGE = "vehicle_storage"
TYPE_WORKTIME = "summarized_worktime"
TYPE_REST_PLACES = "driver_rest_places"
TYPE_DRIVER_TRAINING = "driver_training"
TYPE_SAFETY_TRAINING = "safety_training"
TYPE_ROAD_SAFETY = "road_safety"
TYPE_TECHNICAL_CONTROL = "technical_control"
TYPE_MAINTENANCE_REPAIR = "maintenance_repair"
TYPE_ACCIDENT_COMMISSION = "accident_commission"
TYPE_OCCUPATIONAL_SAFETY = "occupational_safety"
TYPE_FIRE_SAFETY = "fire_safety"
TYPE_GENERIC = "generic"

ORDER_TYPE_LABELS = {
    TYPE_VEHICLE_ASSIGNMENT: "Закріплення транспортних засобів за водіями",
    TYPE_STORAGE: "Зберігання транспортних засобів",
    TYPE_WORKTIME: "Організація / підсумований облік робочого часу",
    TYPE_REST_PLACES: "Місця відпочинку водіїв",
    TYPE_DRIVER_TRAINING: "Спеціальна підготовка / стажування водіїв",
    TYPE_SAFETY_TRAINING: "Навчання / перевірка знань з безпеки",
    TYPE_ROAD_SAFETY: "Безпека дорожнього руху",
    TYPE_TECHNICAL_CONTROL: "Технічний стан / передрейсовий контроль",
    TYPE_MAINTENANCE_REPAIR: "ТО / ремонти / технічні огляди",
    TYPE_ACCIDENT_COMMISSION: "ДТП / комісія / службове розслідування",
    TYPE_OCCUPATIONAL_SAFETY: "Охорона праці",
    TYPE_FIRE_SAFETY: "Пожежна безпека",
    TYPE_GENERIC: "Інший наказ з експлуатації",
}

DEFAULT_SUBJECTS = {
    TYPE_VEHICLE_ASSIGNMENT: "Про закріплення автотранспортних засобів",
    TYPE_STORAGE: "Про зберігання транспортних засобів на території підприємства",
    TYPE_WORKTIME: "Про організацію обліку робочого часу",
    TYPE_REST_PLACES: "Про встановлення місць для відпочинку водіїв та зберігання автобусів",
    TYPE_DRIVER_TRAINING: "Про спеціальну підготовку та стажування водіїв",
    TYPE_SAFETY_TRAINING: "Про проведення навчання та перевірку знань",
    TYPE_ROAD_SAFETY: "Про організацію роботи з безпеки дорожнього руху",
    TYPE_TECHNICAL_CONTROL: "Про організацію контролю технічного стану транспортних засобів",
    TYPE_MAINTENANCE_REPAIR: "Про організацію технічного обслуговування та ремонту транспортних засобів",
    TYPE_ACCIDENT_COMMISSION: "Про створення комісії та розгляд дорожньо-транспортної пригоди",
    TYPE_OCCUPATIONAL_SAFETY: "Про організацію роботи з охорони праці",
    TYPE_FIRE_SAFETY: "Про організацію пожежної безпеки",
    TYPE_GENERIC: "",
}

DEFAULT_PREAMBLES = {
    TYPE_VEHICLE_ASSIGNMENT: "Для виконання виробничих завдань по перевезенню пасажирів на маршрутах підприємства —",
    TYPE_STORAGE: "З метою впорядкування експлуатації та зберігання транспортних засобів підприємства —",
    TYPE_WORKTIME: "З метою впорядкування режиму та обліку робочого часу працівників підприємства —",
    TYPE_REST_PLACES: "З метою організації відпочинку водіїв та зберігання автобусів під час виконання маршрутів —",
    TYPE_DRIVER_TRAINING: "З метою забезпечення належної підготовки та стажування водіїв підприємства —",
    TYPE_SAFETY_TRAINING: "З метою організації навчання та перевірки знань працівників підприємства —",
    TYPE_ROAD_SAFETY: "З метою організації системної роботи з безпеки дорожнього руху на підприємстві —",
    TYPE_TECHNICAL_CONTROL: "З метою забезпечення належного технічного стану та контролю транспортних засобів перед виїздом —",
    TYPE_MAINTENANCE_REPAIR: "З метою планування та обліку технічного обслуговування, ремонту і технічних оглядів транспортних засобів —",
    TYPE_ACCIDENT_COMMISSION: "З метою документування обставин дорожньо-транспортної пригоди та визначення необхідних заходів —",
    TYPE_OCCUPATIONAL_SAFETY: "З метою організації роботи з охорони праці, навчання та інструктажів працівників —",
    TYPE_FIRE_SAFETY: "З метою організації пожежної безпеки та виконання протипожежних заходів —",
    TYPE_GENERIC: "",
}


def _day(value):
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value or "").strip()
    if not text:
        return date.today().isoformat()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(text[:10], fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError("Дата має бути у форматі ДД.ММ.РРРР або РРРР-ММ-ДД.")


def display_day(value):
    text = str(value or "").strip()
    try:
        return date.fromisoformat(text[:10]).strftime("%d.%m.%Y")
    except Exception:
        return text


def _ptext(value):
    """Plain text safe for ReportLab Paragraph markup."""
    return escape(str(value or ""))


def _json_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _write_history(con, entity_type, entity_id, action, before=None, after=None, note=""):
    con.execute(
        """INSERT INTO operations_change_log(
               entity_type,entity_id,action,before_json,after_json,note,changed_at
           ) VALUES(?,?,?,?,?,?,?)""",
        (
            str(entity_type), int(entity_id), str(action),
            json.dumps(before or {}, ensure_ascii=False, sort_keys=True, default=_json_value),
            json.dumps(after or {}, ensure_ascii=False, sort_keys=True, default=_json_value),
            str(note or "").strip(), datetime.now().isoformat(timespec="seconds"),
        ),
    )


def ensure_schema_on_connection(con):
    con.executescript("""
        CREATE TABLE IF NOT EXISTS operations_settings (
            id INTEGER PRIMARY KEY CHECK(id=1),
            operations_responsible_employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
            military_transport_responsible_employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
            order_place TEXT DEFAULT '',
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS operations_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_type TEXT NOT NULL,
            order_no TEXT NOT NULL,
            order_date TEXT NOT NULL,
            place TEXT DEFAULT '',
            subject TEXT DEFAULT '',
            preamble TEXT DEFAULT '',
            body_text TEXT DEFAULT '',
            control_employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
            status TEXT NOT NULL DEFAULT 'draft',
            approved_at TEXT DEFAULT '',
            cancelled_at TEXT DEFAULT '',
            note TEXT DEFAULT '',
            paper_original_signed INTEGER NOT NULL DEFAULT 0,
            paper_original_signed_at TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(order_no, order_date)
        );
        CREATE INDEX IF NOT EXISTS idx_operations_orders_date
            ON operations_orders(order_date DESC,id DESC);

        CREATE TABLE IF NOT EXISTS vehicle_driver_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL REFERENCES operations_orders(id) ON DELETE CASCADE,
            vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
            employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
            valid_from TEXT NOT NULL,
            valid_until TEXT DEFAULT '',
            sequence_no INTEGER NOT NULL DEFAULT 1,
            note TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT DEFAULT '',
            UNIQUE(order_id, vehicle_id, employee_id, valid_from)
        );
        CREATE INDEX IF NOT EXISTS idx_vehicle_driver_assignments_active
            ON vehicle_driver_assignments(vehicle_id,valid_from,valid_until,employee_id);

        CREATE TABLE IF NOT EXISTS military_statement_approvals (
            report_date TEXT PRIMARY KEY,
            responsible_employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
            fingerprint TEXT NOT NULL,
            row_count INTEGER NOT NULL DEFAULT 0,
            approved_at TEXT NOT NULL,
            note TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS operations_change_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            before_json TEXT NOT NULL DEFAULT '{}',
            after_json TEXT NOT NULL DEFAULT '{}',
            note TEXT DEFAULT '',
            changed_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_operations_change_log_entity
            ON operations_change_log(entity_type,entity_id,id DESC);
    """)
    # Safe additive migrations for databases created by r2/r3.
    cols = {row[1] for row in con.execute("PRAGMA table_info(operations_orders)").fetchall()}
    if "paper_original_signed" not in cols:
        con.execute("ALTER TABLE operations_orders ADD COLUMN paper_original_signed INTEGER NOT NULL DEFAULT 0")
    if "paper_original_signed_at" not in cols:
        con.execute("ALTER TABLE operations_orders ADD COLUMN paper_original_signed_at TEXT DEFAULT ''")
    acols = {row[1] for row in con.execute("PRAGMA table_info(vehicle_driver_assignments)").fetchall()}
    if "updated_at" not in acols:
        con.execute("ALTER TABLE vehicle_driver_assignments ADD COLUMN updated_at TEXT DEFAULT ''")
    now = datetime.now().isoformat(timespec="seconds")
    con.execute("INSERT OR IGNORE INTO operations_settings(id,updated_at) VALUES(1,?)", (now,))


def ensure_schema(core):
    con = core.db()
    try:
        ensure_schema_on_connection(con)
        con.commit()
    finally:
        con.close()


def settings(con):
    ensure_schema_on_connection(con)
    return con.execute("SELECT * FROM operations_settings WHERE id=1").fetchone()


def save_settings(con, *, operations_responsible_employee_id=None,
                  military_transport_responsible_employee_id=None, order_place=""):
    ensure_schema_on_connection(con)
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        """UPDATE operations_settings
              SET operations_responsible_employee_id=?,
                  military_transport_responsible_employee_id=?,
                  order_place=?,updated_at=?
            WHERE id=1""",
        (
            int(operations_responsible_employee_id) if operations_responsible_employee_id else None,
            int(military_transport_responsible_employee_id) if military_transport_responsible_employee_id else None,
            str(order_place or "").strip(), now,
        ),
    )


def employee_name(con, employee_id):
    if not employee_id:
        return ""
    row = con.execute(
        "SELECT last_name,first_name,middle_name FROM employees WHERE id=?", (int(employee_id),)
    ).fetchone()
    if row is None:
        return ""
    return " ".join(str(row[k] or "").strip() for k in ("last_name", "first_name", "middle_name") if str(row[k] or "").strip())


def list_employee_choices(con, active_only=True):
    sql = "SELECT id,last_name,first_name,middle_name,position,active FROM employees"
    if active_only:
        sql += " WHERE COALESCE(active,1)=1"
    sql += " ORDER BY last_name,first_name,middle_name,id"
    result = []
    for row in con.execute(sql).fetchall():
        name = " ".join(str(row[k] or "").strip() for k in ("last_name", "first_name", "middle_name") if str(row[k] or "").strip())
        position = str(row["position"] or "").strip()
        result.append({"id": int(row["id"]), "name": name, "position": position,
                       "label": name + ((" — " + position) if position else "")})
    return result


def list_vehicle_choices(con, active_only=False):
    sql = "SELECT id,name,plate,make_model,active FROM vehicles"
    if active_only:
        sql += " WHERE COALESCE(active,1)=1"
    sql += " ORDER BY COALESCE(plate,''),name,id"
    result = []
    for row in con.execute(sql).fetchall():
        plate = str(row["plate"] or "").strip()
        name = str(row["make_model"] or row["name"] or "").strip()
        label = " · ".join(x for x in (plate, name) if x) or ("ТЗ #%d" % int(row["id"]))
        result.append({"id": int(row["id"]), "name": name, "plate": plate, "label": label})
    return result


def create_order(con, *, order_type, order_no, order_date, place="", subject="",
                 preamble="", body_text="", control_employee_id=None, note=""):
    ensure_schema_on_connection(con)
    if order_type not in ORDER_TYPE_LABELS:
        raise ValueError("Невідомий тип наказу.")
    number = str(order_no or "").strip()
    if not number:
        raise ValueError("Вкажіть номер наказу.")
    day = _day(order_date)
    now = datetime.now().isoformat(timespec="seconds")
    cur = con.execute(
        """INSERT INTO operations_orders(
               order_type,order_no,order_date,place,subject,preamble,body_text,
               control_employee_id,status,note,created_at,updated_at
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            order_type, number, day, str(place or "").strip(),
            str(subject or DEFAULT_SUBJECTS.get(order_type, "")).strip(),
            str(preamble or DEFAULT_PREAMBLES.get(order_type, "")).strip(),
            str(body_text or "").strip(),
            int(control_employee_id) if control_employee_id else None,
            ORDER_DRAFT, str(note or "").strip(), now, now,
        ),
    )
    oid = int(cur.lastrowid)
    _write_history(con, "order", oid, "create", after=dict(get_order(con, oid)))
    return oid


def update_order(con, order_id, *, order_type=None, order_no=None, order_date=None,
                 place=None, subject=None, preamble=None, body_text=None,
                 control_employee_id=None, note=None, history_note=""):
    ensure_schema_on_connection(con)
    row = get_order(con, order_id)
    if row is None:
        raise ValueError("Наказ не знайдено.")
    before = dict(row)
    new_type = str(order_type if order_type is not None else row["order_type"])
    if new_type not in ORDER_TYPE_LABELS:
        raise ValueError("Невідомий тип наказу.")
    number = str(order_no if order_no is not None else row["order_no"]).strip()
    if not number:
        raise ValueError("Вкажіть номер наказу.")
    day = _day(order_date if order_date is not None else row["order_date"])
    values = (
        new_type, number, day,
        str(place if place is not None else row["place"] or "").strip(),
        str(subject if subject is not None else row["subject"] or "").strip(),
        str(preamble if preamble is not None else row["preamble"] or "").strip(),
        str(body_text if body_text is not None else row["body_text"] or "").strip(),
        int(control_employee_id) if control_employee_id else None,
        str(note if note is not None else row["note"] or "").strip(),
        datetime.now().isoformat(timespec="seconds"), int(order_id),
    )
    con.execute(
        """UPDATE operations_orders
              SET order_type=?,order_no=?,order_date=?,place=?,subject=?,preamble=?,body_text=?,
                  control_employee_id=?,note=?,updated_at=?
            WHERE id=?""", values,
    )
    after = dict(get_order(con, order_id))
    if before != after:
        _write_history(con, "order", order_id, "update", before=before, after=after, note=history_note)
    return after


def set_paper_original_signed(con, order_id, signed=True, *, signed_at=None, history_note=""):
    ensure_schema_on_connection(con)
    row = get_order(con, order_id)
    if row is None:
        raise ValueError("Наказ не знайдено.")
    before = dict(row)
    when = ""
    if signed:
        when = str(signed_at or datetime.now().isoformat(timespec="seconds"))
    con.execute(
        "UPDATE operations_orders SET paper_original_signed=?,paper_original_signed_at=?,updated_at=? WHERE id=?",
        (1 if signed else 0, when, datetime.now().isoformat(timespec="seconds"), int(order_id)),
    )
    after = dict(get_order(con, order_id))
    _write_history(con, "order", order_id, "paper_signed" if signed else "paper_unmarked",
                   before=before, after=after, note=history_note)
    return after


def list_orders(con, limit=1000):
    ensure_schema_on_connection(con)
    return con.execute(
        """SELECT o.*,e.last_name,e.first_name,e.middle_name
             FROM operations_orders o
             LEFT JOIN employees e ON e.id=o.control_employee_id
            ORDER BY o.order_date DESC,o.id DESC LIMIT ?""", (int(limit),)
    ).fetchall()


def get_order(con, order_id):
    ensure_schema_on_connection(con)
    return con.execute("SELECT * FROM operations_orders WHERE id=?", (int(order_id),)).fetchone()


def add_vehicle_assignment(con, order_id, vehicle_id, employee_id, *, valid_from,
                           valid_until="", sequence_no=None, note=""):
    ensure_schema_on_connection(con)
    order = get_order(con, order_id)
    if order is None:
        raise ValueError("Наказ не знайдено.")
    if order["order_type"] != TYPE_VEHICLE_ASSIGNMENT:
        raise ValueError("Закріплення ТЗ можна додавати лише до наказу про закріплення.")
    start = _day(valid_from)
    end = _day(valid_until) if valid_until else ""
    if end and end < start:
        raise ValueError("Дата завершення не може бути раніше дати початку.")
    if sequence_no is None:
        row = con.execute(
            "SELECT COALESCE(MAX(sequence_no),0)+1 AS n FROM vehicle_driver_assignments WHERE order_id=?",
            (int(order_id),),
        ).fetchone()
        sequence_no = int(row["n"])
    now = datetime.now().isoformat(timespec="seconds")
    cur = con.execute(
        """INSERT INTO vehicle_driver_assignments(
               order_id,vehicle_id,employee_id,valid_from,valid_until,sequence_no,note,created_at,updated_at
           ) VALUES(?,?,?,?,?,?,?,?,?)""",
        (int(order_id), int(vehicle_id), int(employee_id), start, end,
         int(sequence_no), str(note or "").strip(), now, now),
    )
    aid = int(cur.lastrowid)
    _write_history(con, "assignment", aid, "create", after=dict(get_vehicle_assignment(con, aid)))
    return aid


def get_vehicle_assignment(con, assignment_id):
    ensure_schema_on_connection(con)
    return con.execute("SELECT * FROM vehicle_driver_assignments WHERE id=?", (int(assignment_id),)).fetchone()


def update_vehicle_assignment(con, assignment_id, *, vehicle_id=None, employee_id=None,
                              valid_from=None, valid_until=None, sequence_no=None, note=None,
                              history_note=""):
    ensure_schema_on_connection(con)
    row = get_vehicle_assignment(con, assignment_id)
    if row is None:
        raise ValueError("Закріплення не знайдено.")
    before = dict(row)
    start = _day(valid_from if valid_from is not None else row["valid_from"])
    raw_end = row["valid_until"] if valid_until is None else valid_until
    end = _day(raw_end) if str(raw_end or "").strip() else ""
    if end and end < start:
        raise ValueError("Дата завершення не може бути раніше дати початку.")
    con.execute(
        """UPDATE vehicle_driver_assignments
              SET vehicle_id=?,employee_id=?,valid_from=?,valid_until=?,sequence_no=?,note=?,updated_at=?
            WHERE id=?""",
        (
            int(vehicle_id if vehicle_id is not None else row["vehicle_id"]),
            int(employee_id if employee_id is not None else row["employee_id"]),
            start, end,
            int(sequence_no if sequence_no is not None else row["sequence_no"]),
            str(note if note is not None else row["note"] or "").strip(),
            datetime.now().isoformat(timespec="seconds"), int(assignment_id),
        ),
    )
    after = dict(get_vehicle_assignment(con, assignment_id))
    if before != after:
        _write_history(con, "assignment", assignment_id, "update", before=before, after=after, note=history_note)
    return after


def delete_vehicle_assignment(con, assignment_id, *, history_note=""):
    ensure_schema_on_connection(con)
    row = get_vehicle_assignment(con, assignment_id)
    if row is None:
        return
    before = dict(row)
    con.execute("DELETE FROM vehicle_driver_assignments WHERE id=?", (int(assignment_id),))
    _write_history(con, "assignment", assignment_id, "delete", before=before, note=history_note)


def order_assignments(con, order_id):
    ensure_schema_on_connection(con)
    return con.execute(
        """SELECT a.*,v.name AS vehicle_name,v.plate,v.make_model,
                  e.last_name,e.first_name,e.middle_name,e.position
             FROM vehicle_driver_assignments a
             JOIN vehicles v ON v.id=a.vehicle_id
             JOIN employees e ON e.id=a.employee_id
            WHERE a.order_id=?
            ORDER BY a.sequence_no,a.id""", (int(order_id),)
    ).fetchall()


def active_driver_assignments(con, vehicle_id, on_date=None):
    ensure_schema_on_connection(con)
    day = _day(on_date or date.today())
    return con.execute(
        """SELECT a.*,o.order_no,o.order_date,
                  e.last_name,e.first_name,e.middle_name,e.birth_date,
                  e.actual_address,e.registered_address,
                  m.military_specialty,m.military_rank
             FROM vehicle_driver_assignments a
             JOIN operations_orders o ON o.id=a.order_id AND o.status='approved'
             JOIN employees e ON e.id=a.employee_id
             LEFT JOIN employee_military_profile m ON m.employee_id=e.id
            WHERE a.vehicle_id=?
              AND a.valid_from<=?
              AND (COALESCE(a.valid_until,'')='' OR a.valid_until>=?)
            ORDER BY a.sequence_no,a.id""", (int(vehicle_id), day, day)
    ).fetchall()


def approve_order(con, order_id):
    ensure_schema_on_connection(con)
    row = get_order(con, order_id)
    if row is None:
        raise ValueError("Наказ не знайдено.")
    if row["order_type"] == TYPE_VEHICLE_ASSIGNMENT and not order_assignments(con, order_id):
        raise ValueError("До наказу про закріплення не додано жодного ТЗ/водія.")
    before = dict(row)
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        "UPDATE operations_orders SET status=?,approved_at=?,updated_at=? WHERE id=?",
        (ORDER_APPROVED, now, now, int(order_id)),
    )
    _write_history(con, "order", order_id, "approve", before=before, after=dict(get_order(con, order_id)))


def cancel_order(con, order_id):
    ensure_schema_on_connection(con)
    row = get_order(con, order_id)
    if row is None:
        raise ValueError("Наказ не знайдено.")
    before = dict(row)
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        "UPDATE operations_orders SET status=?,cancelled_at=?,updated_at=? WHERE id=?",
        (ORDER_CANCELLED, now, now, int(order_id)),
    )
    _write_history(con, "order", order_id, "cancel", before=before, after=dict(get_order(con, order_id)))


def order_history(con, order_id, limit=500):
    ensure_schema_on_connection(con)
    order_id = int(order_id)
    assignment_ids = [int(r[0]) for r in con.execute(
        "SELECT id FROM vehicle_driver_assignments WHERE order_id=?", (order_id,)
    ).fetchall()]
    if assignment_ids:
        marks = ",".join("?" for _ in assignment_ids)
        sql = (
            "SELECT * FROM operations_change_log WHERE "
            "(entity_type='order' AND entity_id=?) OR "
            f"(entity_type='assignment' AND entity_id IN ({marks})) "
            "ORDER BY id DESC LIMIT ?"
        )
        return con.execute(sql, [order_id] + assignment_ids + [int(limit)]).fetchall()
    return con.execute(
        """SELECT * FROM operations_change_log
            WHERE entity_type='order' AND entity_id=?
            ORDER BY id DESC LIMIT ?""", (order_id, int(limit))
    ).fetchall()


def statement_fingerprint(report_date, company, rows):
    payload = {
        "report_date": _day(report_date),
        "company": {
            key: str((company or {}).get(key) or "").strip()
            for key in ("name", "address", "phone", "email", "signer_name", "signer_position")
        },
        "rows": [dict(row) for row in rows],
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def approve_military_statement(con, report_date, company, rows, responsible_employee_id, note=""):
    ensure_schema_on_connection(con)
    employee_id = int(responsible_employee_id or 0)
    if not employee_id or con.execute("SELECT 1 FROM employees WHERE id=?", (employee_id,)).fetchone() is None:
        raise ValueError("Не вибрано відповідального за військово-транспортний обов'язок.")
    day = _day(report_date)
    fingerprint = statement_fingerprint(day, company, rows)
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        """INSERT INTO military_statement_approvals(
               report_date,responsible_employee_id,fingerprint,row_count,approved_at,note
           ) VALUES(?,?,?,?,?,?)
           ON CONFLICT(report_date) DO UPDATE SET
               responsible_employee_id=excluded.responsible_employee_id,
               fingerprint=excluded.fingerprint,row_count=excluded.row_count,
               approved_at=excluded.approved_at,note=excluded.note""",
        (day, employee_id, fingerprint, len(rows), now, str(note or "").strip()),
    )
    return fingerprint


def military_statement_approval(con, report_date):
    ensure_schema_on_connection(con)
    return con.execute(
        """SELECT a.*,e.last_name,e.first_name,e.middle_name,e.position
             FROM military_statement_approvals a
             LEFT JOIN employees e ON e.id=a.responsible_employee_id
            WHERE a.report_date=?""", (_day(report_date),)
    ).fetchone()


def military_statement_is_approved(con, report_date, company, rows):
    approval = military_statement_approval(con, report_date)
    if approval is None:
        return False, None
    current = statement_fingerprint(report_date, company, rows)
    return current == str(approval["fingerprint"] or ""), approval


def _font_path(preferred=None):
    candidates = [
        str(preferred or ""), r"C:\Windows\Fonts\times.ttf", r"C:\Windows\Fonts\arial.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ]
    for item in candidates:
        if item and Path(item).exists():
            return item
    return ""


def export_order_pdf(path, order, assignments=(), company=None, control_name="", font_path=None):
    """Друк наказу у стилі наданих підприємством зразків."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    font_name = "Times-Roman"
    resolved = _font_path(font_path)
    if resolved:
        font_name = "TaxoOrder"
        try:
            pdfmetrics.registerFont(TTFont(font_name, resolved))
        except Exception:
            font_name = "Times-Roman"

    styles = getSampleStyleSheet()
    normal = ParagraphStyle("OrderNormal", parent=styles["Normal"], fontName=font_name,
                            fontSize=11.5, leading=15, alignment=TA_LEFT)
    center = ParagraphStyle("OrderCenter", parent=normal, alignment=TA_CENTER)
    right = ParagraphStyle("OrderRight", parent=normal, alignment=TA_RIGHT)
    title = ParagraphStyle("OrderTitle", parent=center, fontSize=15, leading=18, spaceAfter=2)
    bold_center = ParagraphStyle("OrderBoldCenter", parent=center, fontSize=12.5, leading=15)

    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=20*mm, rightMargin=18*mm,
                            topMargin=17*mm, bottomMargin=17*mm)
    company = company or {}
    company_name = str(company.get("name") or "").strip() or "Підприємство"
    signer_position = str(company.get("signer_position") or "").strip() or "Керівник"
    signer_name = str(company.get("signer_name") or "").strip()
    story = [
        Paragraph("<b>Н А К А З</b>", title),
        Paragraph("по %s" % _ptext(company_name), center),
        Spacer(1, 7*mm),
    ]
    meta = Table([[
        Paragraph(_ptext(display_day(order["order_date"])), normal),
        Paragraph("<b>№ %s</b>" % _ptext(order["order_no"]), center),
        Paragraph(_ptext(order["place"]), right),
    ]], colWidths=[55*mm, 55*mm, 55*mm])
    meta.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name), ("FONTSIZE", (0,0), (-1,-1), 11.5),
        ("ALIGN", (0,0), (0,0), "LEFT"), ("ALIGN", (1,0), (1,0), "CENTER"),
        ("ALIGN", (2,0), (2,0), "RIGHT"),
    ]))
    story += [meta, Spacer(1, 8*mm)]
    subject = str(order["subject"] or "").strip()
    if subject:
        story += [Paragraph("<b>%s</b>" % _ptext(subject), normal), Spacer(1, 5*mm)]
    preamble = str(order["preamble"] or "").strip()
    if preamble:
        story += [Paragraph(_ptext(preamble), normal), Spacer(1, 6*mm)]
    story += [Paragraph("<b>Н А К А З У Ю:</b>", bold_center), Spacer(1, 5*mm)]

    if str(order["order_type"]) == TYPE_VEHICLE_ASSIGNMENT:
        first_from = display_day(assignments[0]["valid_from"]) if assignments else display_day(order["order_date"])
        story.append(Paragraph(
            "1. Закріпити з %s транспортні засоби підприємства за водіями згідно з наведеною таблицею:" % first_from,
            normal,
        ))
        data = [["№", "Транспортний засіб", "Держ. номер", "Водій"]]
        for idx, item in enumerate(assignments, 1):
            name = " ".join(str(item[k] or "").strip() for k in ("last_name", "first_name", "middle_name") if str(item[k] or "").strip())
            vehicle = str(item["make_model"] or item["vehicle_name"] or "").strip()
            data.append([idx, vehicle, str(item["plate"] or "").strip(), name])
        table = Table(data, colWidths=[10*mm, 52*mm, 38*mm, 65*mm], repeatRows=1)
        table.setStyle(TableStyle([
            ("FONTNAME", (0,0), (-1,-1), font_name), ("FONTSIZE", (0,0), (-1,-1), 10.5),
            ("GRID", (0,0), (-1,-1), 0.45, colors.black), ("ALIGN", (0,0), (-1,0), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (0,0), (-1,-1), 3),
            ("RIGHTPADDING", (0,0), (-1,-1), 3), ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        story += [Spacer(1, 3*mm), table, Spacer(1, 5*mm)]
        control = str(control_name or "").strip()
        if control:
            story.append(Paragraph("2. Контроль за виконанням даного наказу покласти на %s." % _ptext(control), normal))
    else:
        body = str(order["body_text"] or "").strip()
        if body:
            for paragraph in [p.strip() for p in body.split("\n") if p.strip()]:
                story.append(Paragraph(_ptext(paragraph), normal))
                story.append(Spacer(1, 2*mm))
        control = str(control_name or "").strip()
        if control:
            story.append(Paragraph("Контроль за виконанням даного наказу покласти на %s." % _ptext(control), normal))

    story += [Spacer(1, 15*mm)]
    signature = Table([[signer_position, "________________", signer_name]], colWidths=[60*mm, 45*mm, 55*mm])
    signature.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name), ("FONTSIZE", (0,0), (-1,-1), 11.5),
        ("ALIGN", (0,0), (0,0), "LEFT"), ("ALIGN", (1,0), (1,0), "CENTER"),
        ("ALIGN", (2,0), (2,0), "RIGHT"),
    ]))
    story.append(signature)
    doc.build(story)
    return path
