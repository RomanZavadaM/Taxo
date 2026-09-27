# -*- coding: utf-8 -*-
"""Taxo 10.4-r10 — military-transport accounting for vehicles.

This module is deliberately independent from:
- the «Шлях» licence/registry enrichment;
- operational vehicle documents (insurance, registration, diagnostics, tachograph);
- the ordinary active/inactive state of a Taxo vehicle card.

Legal marker used by the 2026 model:
Положення про військово-транспортний обов'язок №1921, чинна редакція 25.12.2025.

The module records primary facts and deadlines only when Taxo has an explicit basis.
Missing information is a clarification state, not an automatic legal violation.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

APP_VERSION = "10.4-r10"
LEGAL_BASIS = "Положення про військово-транспортний обов'язок №1921, чинна редакція 25.12.2025"
FEATURE_START = date(2026, 9, 27)
NOTICE_DAYS = 7
REPORT_DATES = ((6, 20), (12, 20))

STATUS_UNKNOWN = "unknown"
STATUS_NOT_DESIGNATED = "not_designated"
STATUS_DESIGNATED = "designated"
STATUS_ORDERED = "ordered"
STATUS_TRANSFERRED = "transferred"
STATUS_RETURNED = "returned"
STATUS_EXEMPT = "exempt"

STATUS_LABELS = {
    STATUS_UNKNOWN: "Не визначено / потрібне уточнення",
    STATUS_NOT_DESIGNATED: "Не визначено для передачі",
    STATUS_DESIGNATED: "Визначено для військових потреб",
    STATUS_ORDERED: "Є наряд / очікується виконання",
    STATUS_TRANSFERRED: "Передано",
    STATUS_RETURNED: "Повернуто",
    STATUS_EXEMPT: "Є зафіксована підстава винятку",
}
VALID_STATUSES = frozenset(STATUS_LABELS)

READINESS_UNKNOWN = "unknown"
READINESS_READY = "ready"
READINESS_LIMITED = "limited"
READINESS_NOT_READY = "not_ready"
READINESS_LABELS = {
    READINESS_UNKNOWN: "Не визначено",
    READINESS_READY: "Готовий",
    READINESS_LIMITED: "Обмежена готовність",
    READINESS_NOT_READY: "Не готовий",
}

ORDER_CONSOLIDATED = "consolidated"
ORDER_PARTIAL = "partial"
ORDER_LABELS = {
    ORDER_CONSOLIDATED: "Зведений наряд",
    ORDER_PARTIAL: "Частковий наряд",
}
ORDER_RECEIVED = "received"
ORDER_PREPARING = "preparing"
ORDER_TRANSFERRED = "transferred"
ORDER_CANCELLED = "cancelled"
ORDER_RETURNED = "returned"
ORDER_STATUS_LABELS = {
    ORDER_RECEIVED: "Отримано",
    ORDER_PREPARING: "Підготовка",
    ORDER_TRANSFERRED: "Передано",
    ORDER_CANCELLED: "Скасовано / втратило чинність",
    ORDER_RETURNED: "Повернуто",
}

ACTION_REPORT = "semiannual_statement"
ACTION_NOTICE = "seven_day_notice"
ACTION_LABELS = {
    ACTION_REPORT: "Відомість про наявність і технічний стан",
    ACTION_NOTICE: "Повідомлення про подію щодо ТЗ",
}
ACTION_OPEN = "open"
ACTION_DONE = "done"
ACTION_CANCELLED = "cancelled"

EVENT_COMPANY_DETAILS = "company_details_change"
EVENT_OUT_OF_REGION = "long_term_out_of_region"
EVENT_ABROAD = "long_term_abroad"
EVENT_OWNERSHIP = "ownership_transfer"
EVENT_LEASE = "long_term_lease_or_leasing"
EVENT_COLLATERAL = "collateral"
EVENT_OTHER_BLOCKING = "other_prevents_transfer"
EVENT_LABELS = {
    EVENT_COMPANY_DETAILS: "Зміна найменування / організаційних реквізитів",
    EVENT_OUT_OF_REGION: "Тривале направлення ТЗ в інший регіон",
    EVENT_ABROAD: "Тривале направлення ТЗ за межі України",
    EVENT_OWNERSHIP: "Зміна власника / відчуження",
    EVENT_LEASE: "Тривала оренда / лізинг",
    EVENT_COLLATERAL: "Передача в заставу",
    EVENT_OTHER_BLOCKING: "Інша обставина, що може унеможливити передачу",
}


def _day(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value or "").strip()
    if not text:
        raise ValueError("Потрібна дата.")
    return date.fromisoformat(text[:10])


def _day_text(value):
    if value in (None, ""):
        return ""
    return _day(value).isoformat()


def _time_text(value):
    if value in (None, ""):
        return ""
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime.combine(value, datetime.min.time()).isoformat(timespec="minutes")
    if isinstance(value, datetime):
        return value.isoformat(timespec="minutes")
    return datetime.fromisoformat(str(value).strip()).isoformat(timespec="minutes")


def ensure_schema_on_connection(con):
    con.executescript("""
        CREATE TABLE IF NOT EXISTS vehicle_military_transport_profile (
            vehicle_id INTEGER PRIMARY KEY REFERENCES vehicles(id) ON DELETE CASCADE,
            status TEXT NOT NULL DEFAULT 'unknown',
            accounting_authority TEXT DEFAULT '',
            local_reference TEXT DEFAULT '',
            readiness_status TEXT NOT NULL DEFAULT 'unknown',
            technical_note TEXT DEFAULT '',
            basis_type TEXT DEFAULT '',
            basis_document_no TEXT DEFAULT '',
            basis_document_date TEXT DEFAULT '',
            exemption_basis TEXT DEFAULT '',
            note TEXT DEFAULT '',
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS vehicle_military_transport_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
            status TEXT NOT NULL,
            accounting_authority TEXT DEFAULT '',
            local_reference TEXT DEFAULT '',
            readiness_status TEXT NOT NULL DEFAULT 'unknown',
            technical_note TEXT DEFAULT '',
            basis_type TEXT DEFAULT '',
            basis_document_no TEXT DEFAULT '',
            basis_document_date TEXT DEFAULT '',
            exemption_basis TEXT DEFAULT '',
            note TEXT DEFAULT '',
            source TEXT NOT NULL DEFAULT 'manual',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_vehicle_military_transport_history
            ON vehicle_military_transport_history(vehicle_id,id DESC);

        CREATE TABLE IF NOT EXISTS vehicle_military_transport_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
            order_kind TEXT NOT NULL,
            document_no TEXT DEFAULT '',
            document_date TEXT NOT NULL,
            authority TEXT DEFAULT '',
            transfer_point TEXT DEFAULT '',
            transfer_due_date TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'received',
            actual_transfer_at TEXT DEFAULT '',
            returned_at TEXT DEFAULT '',
            return_reference TEXT DEFAULT '',
            note TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS idx_vehicle_military_transport_orders
            ON vehicle_military_transport_orders(vehicle_id,document_date DESC,id DESC);

        CREATE TABLE IF NOT EXISTS vehicle_military_transport_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
            event_type TEXT NOT NULL,
            event_date TEXT NOT NULL,
            details TEXT DEFAULT '',
            source TEXT NOT NULL DEFAULT 'manual',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_vehicle_military_transport_events
            ON vehicle_military_transport_events(vehicle_id,event_date DESC,id DESC);

        CREATE TABLE IF NOT EXISTS vehicle_military_transport_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER REFERENCES vehicles(id) ON DELETE SET NULL,
            action_type TEXT NOT NULL,
            event_id INTEGER REFERENCES vehicle_military_transport_events(id) ON DELETE SET NULL,
            event_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            completed_at TEXT DEFAULT '',
            reference TEXT DEFAULT '',
            note TEXT DEFAULT '',
            source TEXT NOT NULL DEFAULT 'manual',
            created_at TEXT NOT NULL,
            UNIQUE(action_type,event_id,due_date,source)
        );
        CREATE INDEX IF NOT EXISTS idx_vehicle_military_transport_actions_due
            ON vehicle_military_transport_actions(status,due_date,id);

        CREATE TABLE IF NOT EXISTS vehicle_military_transport_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date TEXT NOT NULL,
            submitted_at TEXT NOT NULL,
            authority TEXT DEFAULT '',
            reference TEXT DEFAULT '',
            note TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            UNIQUE(report_date)
        );

        CREATE TABLE IF NOT EXISTS vehicle_military_transport_workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
            employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
            worker_name TEXT DEFAULT '',
            relation_note TEXT DEFAULT '',
            valid_from TEXT DEFAULT '',
            valid_until TEXT DEFAULT '',
            source TEXT NOT NULL DEFAULT 'manual',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_vehicle_military_transport_workers
            ON vehicle_military_transport_workers(vehicle_id,valid_from,valid_until,id);
    """)


def ensure_schema(core):
    con = core.db()
    try:
        ensure_schema_on_connection(con)
        con.commit()
    finally:
        con.close()


def get_profile(con, vehicle_id):
    ensure_schema_on_connection(con)
    return con.execute(
        "SELECT * FROM vehicle_military_transport_profile WHERE vehicle_id=?",
        (int(vehicle_id),),
    ).fetchone()


def profile_state(con, vehicle_id):
    row = get_profile(con, vehicle_id)
    if row is None:
        return {
            "status": STATUS_UNKNOWN,
            "label": STATUS_LABELS[STATUS_UNKNOWN],
            "needs_clarification": True,
            "violation": False,
        }
    status = row["status"] if row["status"] in VALID_STATUSES else STATUS_UNKNOWN
    return {
        "status": status,
        "label": STATUS_LABELS.get(status, status),
        "needs_clarification": status == STATUS_UNKNOWN,
        "violation": False,
    }


def set_profile(con, vehicle_id, *, status=STATUS_UNKNOWN, accounting_authority="",
                local_reference="", readiness_status=READINESS_UNKNOWN,
                technical_note="", basis_type="", basis_document_no="",
                basis_document_date="", exemption_basis="", note="", source="manual"):
    ensure_schema_on_connection(con)
    if status not in VALID_STATUSES:
        raise ValueError("Невідомий статус військово-транспортного обліку.")
    if readiness_status not in READINESS_LABELS:
        raise ValueError("Невідомий стан готовності ТЗ.")
    if basis_document_date:
        basis_document_date = _day_text(basis_document_date)
    now = datetime.now().isoformat(timespec="seconds")
    values = (
        status, str(accounting_authority or "").strip(), str(local_reference or "").strip(),
        readiness_status, str(technical_note or "").strip(), str(basis_type or "").strip(),
        str(basis_document_no or "").strip(), basis_document_date,
        str(exemption_basis or "").strip(), str(note or "").strip(), now,
    )
    con.execute(
        """INSERT INTO vehicle_military_transport_profile(
               vehicle_id,status,accounting_authority,local_reference,readiness_status,
               technical_note,basis_type,basis_document_no,basis_document_date,
               exemption_basis,note,updated_at
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(vehicle_id) DO UPDATE SET
               status=excluded.status,
               accounting_authority=excluded.accounting_authority,
               local_reference=excluded.local_reference,
               readiness_status=excluded.readiness_status,
               technical_note=excluded.technical_note,
               basis_type=excluded.basis_type,
               basis_document_no=excluded.basis_document_no,
               basis_document_date=excluded.basis_document_date,
               exemption_basis=excluded.exemption_basis,
               note=excluded.note,
               updated_at=excluded.updated_at""",
        (int(vehicle_id),) + values,
    )
    con.execute(
        """INSERT INTO vehicle_military_transport_history(
               vehicle_id,status,accounting_authority,local_reference,readiness_status,
               technical_note,basis_type,basis_document_no,basis_document_date,
               exemption_basis,note,source,created_at
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (int(vehicle_id),) + values[:-1] + (str(source or "manual").strip() or "manual", now),
    )


def profile_history(con, vehicle_id):
    ensure_schema_on_connection(con)
    return con.execute(
        "SELECT * FROM vehicle_military_transport_history WHERE vehicle_id=? ORDER BY id DESC",
        (int(vehicle_id),),
    ).fetchall()


def record_order(con, vehicle_id, order_kind, document_date, *, document_no="", authority="",
                 transfer_point="", transfer_due_date="", note=""):
    ensure_schema_on_connection(con)
    if order_kind not in ORDER_LABELS:
        raise ValueError("Невідомий вид наряду.")
    doc_date = _day_text(document_date)
    due = _day_text(transfer_due_date) if transfer_due_date else ""
    now = datetime.now().isoformat(timespec="seconds")
    cur = con.execute(
        """INSERT INTO vehicle_military_transport_orders(
               vehicle_id,order_kind,document_no,document_date,authority,transfer_point,
               transfer_due_date,status,note,created_at,updated_at
           ) VALUES(?,?,?,?,?,?,?,? ,?,?,?)""",
        (int(vehicle_id), order_kind, str(document_no or "").strip(), doc_date,
         str(authority or "").strip(), str(transfer_point or "").strip(), due,
         ORDER_RECEIVED, str(note or "").strip(), now, now),
    )
    return int(cur.lastrowid)


def list_orders(con, vehicle_id=None):
    ensure_schema_on_connection(con)
    sql = "SELECT * FROM vehicle_military_transport_orders"
    params = []
    if vehicle_id is not None:
        sql += " WHERE vehicle_id=?"
        params.append(int(vehicle_id))
    sql += " ORDER BY document_date DESC,id DESC"
    return con.execute(sql, params).fetchall()


def set_order_status(con, order_id, status, *, actual_at=None, return_reference=""):
    if status not in ORDER_STATUS_LABELS:
        raise ValueError("Невідомий стан наряду.")
    row = con.execute(
        "SELECT * FROM vehicle_military_transport_orders WHERE id=?", (int(order_id),)
    ).fetchone()
    if row is None:
        raise ValueError("Наряд не знайдено.")
    now = datetime.now().isoformat(timespec="seconds")
    transfer_at = row["actual_transfer_at"] or ""
    returned_at = row["returned_at"] or ""
    if status == ORDER_TRANSFERRED:
        transfer_at = _time_text(actual_at or datetime.now())
    elif status == ORDER_RETURNED:
        returned_at = _time_text(actual_at or datetime.now())
    con.execute(
        """UPDATE vehicle_military_transport_orders
           SET status=?,actual_transfer_at=?,returned_at=?,return_reference=?,updated_at=?
           WHERE id=?""",
        (status, transfer_at, returned_at, str(return_reference or row["return_reference"] or "").strip(), now, int(order_id)),
    )
    if status == ORDER_TRANSFERRED:
        _copy_profile_with_status(con, row["vehicle_id"], STATUS_TRANSFERRED, "order_transfer")
    elif status == ORDER_RETURNED:
        _copy_profile_with_status(con, row["vehicle_id"], STATUS_RETURNED, "order_return")


def _copy_profile_with_status(con, vehicle_id, status, source):
    current = get_profile(con, vehicle_id)
    kwargs = {}
    if current is not None:
        for key in (
            "accounting_authority", "local_reference", "readiness_status", "technical_note",
            "basis_type", "basis_document_no", "basis_document_date", "exemption_basis", "note",
        ):
            kwargs[key] = current[key]
    set_profile(con, vehicle_id, status=status, source=source, **kwargs)


def next_reporting_deadline(today=None):
    today = today or date.today()
    if not isinstance(today, date) or isinstance(today, datetime):
        today = _day(today)
    for month, day_no in REPORT_DATES:
        candidate = date(today.year, month, day_no)
        if candidate >= today:
            return candidate
    return date(today.year + 1, REPORT_DATES[0][0], REPORT_DATES[0][1])


def ensure_next_reporting_action(con, today=None, feature_start=FEATURE_START):
    """Create only the next report task; never backfill an already missed period."""
    ensure_schema_on_connection(con)
    today = _day(today or date.today())
    feature_start = _day(feature_start)
    effective = max(today, feature_start)
    deadline = next_reporting_deadline(effective)
    now = datetime.now().isoformat(timespec="seconds")
    before = con.total_changes
    con.execute(
        """INSERT OR IGNORE INTO vehicle_military_transport_actions(
               vehicle_id,action_type,event_id,event_date,due_date,status,note,source,created_at
           ) VALUES(NULL,?,NULL,?,?,?,'','semiannual_schedule',?)""",
        (ACTION_REPORT, effective.isoformat(), deadline.isoformat(), ACTION_OPEN, now),
    )
    return con.total_changes - before, deadline


def record_notice_event(con, vehicle_id, event_type, event_date, details=""):
    """Record an explicit qualifying event and create its seven-day action.

    Nothing is inferred from old vehicle-card edits; without this explicit event no
    seven-day task exists.
    """
    ensure_schema_on_connection(con)
    if event_type not in EVENT_LABELS:
        raise ValueError("Невідомий вид події для повідомлення.")
    event_day = _day(event_date)
    now = datetime.now().isoformat(timespec="seconds")
    cur = con.execute(
        """INSERT INTO vehicle_military_transport_events(
               vehicle_id,event_type,event_date,details,source,created_at
           ) VALUES(?,?,?,?,?,?)""",
        (int(vehicle_id), event_type, event_day.isoformat(), str(details or "").strip(), "manual", now),
    )
    event_id = int(cur.lastrowid)
    due = event_day + timedelta(days=NOTICE_DAYS)
    con.execute(
        """INSERT INTO vehicle_military_transport_actions(
               vehicle_id,action_type,event_id,event_date,due_date,status,note,source,created_at
           ) VALUES(?,?,?,?,?,?,?,?,?)""",
        (int(vehicle_id), ACTION_NOTICE, event_id, event_day.isoformat(), due.isoformat(),
         ACTION_OPEN, EVENT_LABELS[event_type], "explicit_event", now),
    )
    return event_id, due


def list_events(con, vehicle_id=None):
    ensure_schema_on_connection(con)
    sql = "SELECT * FROM vehicle_military_transport_events"
    params = []
    if vehicle_id is not None:
        sql += " WHERE vehicle_id=?"
        params.append(int(vehicle_id))
    sql += " ORDER BY event_date DESC,id DESC"
    return con.execute(sql, params).fetchall()


def list_actions(con, status=None, vehicle_id=None):
    ensure_schema_on_connection(con)
    where = []
    params = []
    if status:
        where.append("a.status=?")
        params.append(status)
    if vehicle_id is not None:
        where.append("a.vehicle_id=?")
        params.append(int(vehicle_id))
    sql = """SELECT a.*,v.name AS vehicle_name,v.plate AS vehicle_plate
             FROM vehicle_military_transport_actions a
             LEFT JOIN vehicles v ON v.id=a.vehicle_id"""
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY CASE WHEN a.status='open' THEN 0 ELSE 1 END,a.due_date,a.id"
    return con.execute(sql, params).fetchall()


def complete_action(con, action_id, reference="", note="", completed_at=None):
    when = _time_text(completed_at or datetime.now())
    con.execute(
        """UPDATE vehicle_military_transport_actions
           SET status=?,completed_at=?,reference=?,note=CASE WHEN ?<>'' THEN ? ELSE note END
           WHERE id=?""",
        (ACTION_DONE, when, str(reference or "").strip(), str(note or "").strip(),
         str(note or "").strip(), int(action_id)),
    )


def cancel_action(con, action_id, note=""):
    con.execute(
        "UPDATE vehicle_military_transport_actions SET status=?,note=? WHERE id=?",
        (ACTION_CANCELLED, str(note or "").strip(), int(action_id)),
    )


def record_submission(con, report_date, submitted_at=None, authority="", reference="", note=""):
    ensure_schema_on_connection(con)
    report_day = _day(report_date)
    if (report_day.month, report_day.day) not in REPORT_DATES:
        raise ValueError("Контрольна дата відомості має бути 20 червня або 20 грудня.")
    submitted = _time_text(submitted_at or datetime.now())
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        """INSERT INTO vehicle_military_transport_submissions(
               report_date,submitted_at,authority,reference,note,created_at
           ) VALUES(?,?,?,?,?,?)
           ON CONFLICT(report_date) DO UPDATE SET
               submitted_at=excluded.submitted_at,authority=excluded.authority,
               reference=excluded.reference,note=excluded.note""",
        (report_day.isoformat(), submitted, str(authority or "").strip(),
         str(reference or "").strip(), str(note or "").strip(), now),
    )
    con.execute(
        """UPDATE vehicle_military_transport_actions
           SET status=?,completed_at=?,reference=?
           WHERE action_type=? AND due_date=? AND status=?""",
        (ACTION_DONE, submitted, str(reference or "").strip(), ACTION_REPORT,
         report_day.isoformat(), ACTION_OPEN),
    )


def list_submissions(con):
    ensure_schema_on_connection(con)
    return con.execute(
        "SELECT * FROM vehicle_military_transport_submissions ORDER BY report_date DESC,id DESC"
    ).fetchall()


def add_worker_link(con, vehicle_id, *, employee_id=None, worker_name="", relation_note="",
                    valid_from="", valid_until="", source="manual"):
    ensure_schema_on_connection(con)
    if employee_id is None and not str(worker_name or "").strip():
        raise ValueError("Потрібно вибрати працівника або вказати ПІБ вручну.")
    now = datetime.now().isoformat(timespec="seconds")
    cur = con.execute(
        """INSERT INTO vehicle_military_transport_workers(
               vehicle_id,employee_id,worker_name,relation_note,valid_from,valid_until,source,created_at
           ) VALUES(?,?,?,?,?,?,?,?)""",
        (int(vehicle_id), int(employee_id) if employee_id is not None else None,
         str(worker_name or "").strip(), str(relation_note or "").strip(),
         _day_text(valid_from) if valid_from else "", _day_text(valid_until) if valid_until else "",
         str(source or "manual").strip() or "manual", now),
    )
    return int(cur.lastrowid)


def workers_for_vehicle(con, vehicle_id, on_date=None):
    ensure_schema_on_connection(con)
    day_text = _day_text(on_date or date.today())
    return con.execute(
        """SELECT w.*,e.last_name,e.first_name,e.middle_name
           FROM vehicle_military_transport_workers w
           LEFT JOIN employees e ON e.id=w.employee_id
           WHERE w.vehicle_id=?
             AND (COALESCE(w.valid_from,'')='' OR w.valid_from<=?)
             AND (COALESCE(w.valid_until,'')='' OR w.valid_until>=?)
           ORDER BY w.id""",
        (int(vehicle_id), day_text, day_text),
    ).fetchall()


def overview_rows(con, today=None):
    """Return informational rows without creating any legal conclusion."""
    ensure_schema_on_connection(con)
    today = _day(today or date.today())
    rows = con.execute(
        """SELECT v.id,v.name,v.plate,v.make_model,v.active,
                  p.status,p.readiness_status,p.accounting_authority,p.basis_document_no,
                  p.basis_document_date,p.updated_at
           FROM vehicles v
           LEFT JOIN vehicle_military_transport_profile p ON p.vehicle_id=v.id
           ORDER BY v.active DESC,v.plate,v.name"""
    ).fetchall()
    result = []
    for row in rows:
        status = row["status"] or STATUS_UNKNOWN
        if status not in VALID_STATUSES:
            status = STATUS_UNKNOWN
        due = con.execute(
            """SELECT due_date,action_type FROM vehicle_military_transport_actions
               WHERE status='open' AND (vehicle_id=? OR vehicle_id IS NULL)
               ORDER BY due_date,id LIMIT 1""",
            (row["id"],),
        ).fetchone()
        result.append({
            "vehicle_id": row["id"],
            "name": row["name"],
            "plate": row["plate"] or "",
            "make_model": row["make_model"] or "",
            "operational_active": bool(row["active"]),
            "status": status,
            "status_label": STATUS_LABELS[status],
            "readiness_status": row["readiness_status"] or READINESS_UNKNOWN,
            "accounting_authority": row["accounting_authority"] or "",
            "basis_document_no": row["basis_document_no"] or "",
            "basis_document_date": row["basis_document_date"] or "",
            "needs_clarification": status == STATUS_UNKNOWN,
            "violation": False,
            "next_due_date": due["due_date"] if due else "",
            "next_action_type": due["action_type"] if due else "",
        })
    return result
