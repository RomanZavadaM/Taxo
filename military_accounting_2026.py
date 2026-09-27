# -*- coding: utf-8 -*-
"""Taxo 10.4-r9 — official military-accounting journal for the 2026 model.

Registry XLSX freshness and statutory military-accounting actions are intentionally
separate.  A quarterly Taxo import never marks an official reconciliation as done.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

APP_VERSION = "10.4-r9"
LEGAL_BASIS = "Порядок №1487, редакція 27.06.2026"
FEATURE_START = date(2026, 9, 27)

HIRE_DOCUMENT_MAX_AGE_HOURS = 72
EMPLOYMENT_NOTICE_DAYS = 7
PERSONAL_LIST_UPDATE_DAYS = 5
ANNUAL_RECONCILIATION_MINIMUM = 1

ACTION_HIRE_NOTICE = "hire_notice"
ACTION_DISMISSAL_NOTICE = "dismissal_notice"
ACTION_PERSONAL_DATA_UPDATE = "personal_data_update"
ACTION_MONTHLY_CHANGE_REPORT = "monthly_change_report"
ACTION_HIRE_DOCUMENT_CHECK = "hire_document_check"

ACTION_LABELS = {
    ACTION_HIRE_NOTICE: "Повідомлення про прийняття на роботу",
    ACTION_DISMISSAL_NOTICE: "Повідомлення про звільнення",
    ACTION_PERSONAL_DATA_UPDATE: "Внести зміни до списку персонального обліку",
    ACTION_MONTHLY_CHANGE_REPORT: "Щомісячне повідомлення про зміни",
    ACTION_HIRE_DOCUMENT_CHECK: "Перевірка військово-облікового документа при прийнятті",
}

STATUS_OPEN = "open"
STATUS_DONE = "done"
STATUS_CANCELLED = "cancelled"

RECONCILIATION_DOCUMENTS = "documents"
RECONCILIATION_AUTHORITY = "authority"
RECONCILIATION_OTHER_TERRITORY = "other_territory"
RECONCILIATION_DIIA = "diia_registry"

RECONCILIATION_LABELS = {
    RECONCILIATION_DOCUMENTS: "З військово-обліковими документами працівників",
    RECONCILIATION_AUTHORITY: "З ТЦК / СБУ / розвідувальним органом",
    RECONCILIATION_OTHER_TERRITORY: "З ТЦК іншої адміністративно-територіальної одиниці",
    RECONCILIATION_DIIA: "Електронне звіряння через Дію / кабінет персонального обліку",
}


def _iso_day(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip()
    if not text:
        return ""
    return date.fromisoformat(text[:10]).isoformat()


def _iso_time(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.isoformat(timespec="minutes")
    text = str(value).strip()
    if not text:
        return ""
    return datetime.fromisoformat(text).isoformat(timespec="minutes")


def ensure_schema_on_connection(con):
    con.executescript("""
        CREATE TABLE IF NOT EXISTS military_accounting_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
            action_type TEXT NOT NULL,
            event_date TEXT NOT NULL,
            due_date TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'open',
            completed_at TEXT DEFAULT '',
            channel TEXT DEFAULT '',
            reference TEXT DEFAULT '',
            note TEXT DEFAULT '',
            source TEXT DEFAULT 'manual',
            created_at TEXT NOT NULL,
            UNIQUE(employee_id,action_type,event_date,source)
        );
        CREATE INDEX IF NOT EXISTS idx_military_accounting_actions_status_due
            ON military_accounting_actions(status,due_date,event_date);

        CREATE TABLE IF NOT EXISTS military_official_reconciliations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reconciliation_date TEXT NOT NULL,
            kind TEXT NOT NULL,
            method TEXT DEFAULT '',
            authority TEXT DEFAULT '',
            result TEXT DEFAULT '',
            reference TEXT DEFAULT '',
            note TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_military_official_reconciliation_date
            ON military_official_reconciliations(reconciliation_date DESC,id DESC);

        CREATE TABLE IF NOT EXISTS military_hire_document_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            employment_date TEXT NOT NULL,
            document_formed_at TEXT DEFAULT '',
            checked_at TEXT NOT NULL,
            method TEXT DEFAULT '',
            result TEXT DEFAULT '',
            note TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_military_hire_document_checks_employee
            ON military_hire_document_checks(employee_id,checked_at DESC,id DESC);
    """)


def ensure_schema(core):
    con = core.db()
    try:
        ensure_schema_on_connection(con)
        con.commit()
    finally:
        con.close()


def _insert_action(con, employee_id, action_type, event_date, due_date="", source="manual", note=""):
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        """INSERT OR IGNORE INTO military_accounting_actions(
               employee_id,action_type,event_date,due_date,status,note,source,created_at
           ) VALUES(?,?,?,?,?,?,?,?)""",
        (employee_id, action_type, _iso_day(event_date), _iso_day(due_date), STATUS_OPEN,
         str(note or "").strip(), source, now),
    )


def sync_recent_employment_actions(con, feature_start=FEATURE_START):
    """Create notice tasks only for personnel events on/after feature activation.

    Historical hires/dismissals are deliberately not backfilled as overdue because
    Taxo cannot know whether the employer already fulfilled those duties.
    """
    ensure_schema_on_connection(con)
    start = feature_start if isinstance(feature_start, date) else date.fromisoformat(str(feature_start))
    rows = con.execute(
        """SELECT id,employment_date,dismissal_date FROM employees
           WHERE COALESCE(employment_date,'')<>'' OR COALESCE(dismissal_date,'')<>''"""
    ).fetchall()
    created_before = con.total_changes
    for row in rows:
        for field_name, action_type in (
            ("employment_date", ACTION_HIRE_NOTICE),
            ("dismissal_date", ACTION_DISMISSAL_NOTICE),
        ):
            raw = (row[field_name] or "").strip()
            if not raw:
                continue
            try:
                event = date.fromisoformat(raw[:10])
            except ValueError:
                continue
            if event < start:
                continue
            _insert_action(
                con, row["id"], action_type, event,
                event + timedelta(days=EMPLOYMENT_NOTICE_DAYS), source="employment_event",
            )
    return con.total_changes - created_before


def add_personal_data_update_action(con, employee_id, event_date, note=""):
    event = event_date if isinstance(event_date, date) else date.fromisoformat(str(event_date)[:10])
    _insert_action(
        con, int(employee_id), ACTION_PERSONAL_DATA_UPDATE, event,
        event + timedelta(days=PERSONAL_LIST_UPDATE_DAYS), source="manual_change", note=note,
    )


def add_monthly_change_report_action(con, event_date, note=""):
    """Record a monthly reporting task explicitly; do not infer a legal event."""
    event = event_date if isinstance(event_date, date) else date.fromisoformat(str(event_date)[:10])
    _insert_action(con, None, ACTION_MONTHLY_CHANGE_REPORT, event, event, source="manual_monthly", note=note)


def complete_action(con, action_id, channel="", reference="", note="", completed_at=None):
    when = completed_at or datetime.now()
    when_text = _iso_time(when)
    con.execute(
        """UPDATE military_accounting_actions
           SET status=?,completed_at=?,channel=?,reference=?,note=CASE WHEN ?<>'' THEN ? ELSE note END
           WHERE id=?""",
        (STATUS_DONE, when_text, str(channel or "").strip(), str(reference or "").strip(),
         str(note or "").strip(), str(note or "").strip(), int(action_id)),
    )


def cancel_action(con, action_id, note=""):
    con.execute(
        "UPDATE military_accounting_actions SET status=?,note=? WHERE id=?",
        (STATUS_CANCELLED, str(note or "").strip(), int(action_id)),
    )


def list_actions(con, status=None, employee_id=None):
    ensure_schema_on_connection(con)
    where = []
    params = []
    if status:
        where.append("status=?")
        params.append(status)
    if employee_id is not None:
        where.append("employee_id=?")
        params.append(int(employee_id))
    sql = """SELECT a.*,e.last_name,e.first_name,e.middle_name
             FROM military_accounting_actions a
             LEFT JOIN employees e ON e.id=a.employee_id"""
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY CASE WHEN a.status='open' THEN 0 ELSE 1 END,COALESCE(NULLIF(a.due_date,''),a.event_date),a.id"
    return con.execute(sql, params).fetchall()


def record_hire_document_check(con, employee_id, employment_date, checked_at,
                               document_formed_at="", method="", result="", note=""):
    ensure_schema_on_connection(con)
    employment = date.fromisoformat(_iso_day(employment_date))
    checked = datetime.fromisoformat(_iso_time(checked_at))
    formed_text = _iso_time(document_formed_at)
    if formed_text:
        formed = datetime.fromisoformat(formed_text)
        employment_end = datetime.combine(employment, datetime.max.time()).replace(microsecond=0)
        age_hours = (employment_end - formed).total_seconds() / 3600.0
        if age_hours < 0 or age_hours > HIRE_DOCUMENT_MAX_AGE_HOURS:
            raise ValueError("Електронний військово-обліковий документ має бути сформований не раніше ніж за 72 години до дати прийняття.")
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        """INSERT INTO military_hire_document_checks(
               employee_id,employment_date,document_formed_at,checked_at,method,result,note,created_at
           ) VALUES(?,?,?,?,?,?,?,?)""",
        (int(employee_id), employment.isoformat(), formed_text, checked.isoformat(timespec="minutes"),
         str(method or "").strip(), str(result or "").strip(), str(note or "").strip(), now),
    )


def record_official_reconciliation(con, reconciliation_date, kind, method="", authority="",
                                   result="", reference="", note=""):
    ensure_schema_on_connection(con)
    if kind not in RECONCILIATION_LABELS:
        raise ValueError("Невідомий вид офіційного звіряння.")
    con.execute(
        """INSERT INTO military_official_reconciliations(
               reconciliation_date,kind,method,authority,result,reference,note,created_at
           ) VALUES(?,?,?,?,?,?,?,?)""",
        (_iso_day(reconciliation_date), kind, str(method or "").strip(),
         str(authority or "").strip(), str(result or "").strip(),
         str(reference or "").strip(), str(note or "").strip(),
         datetime.now().isoformat(timespec="seconds")),
    )


def reconciliation_history(con, year=None):
    ensure_schema_on_connection(con)
    if year is None:
        return con.execute(
            "SELECT * FROM military_official_reconciliations ORDER BY reconciliation_date DESC,id DESC"
        ).fetchall()
    return con.execute(
        """SELECT * FROM military_official_reconciliations
           WHERE substr(reconciliation_date,1,4)=?
           ORDER BY reconciliation_date DESC,id DESC""", (str(int(year)),)
    ).fetchall()


def annual_reconciliation_status(con, today=None):
    """Informational annual status, deliberately independent of XLSX import dates."""
    today = today or date.today()
    rows = reconciliation_history(con, today.year)
    kinds = {row["kind"] for row in rows}
    return {
        "year": today.year,
        "has_document_reconciliation": RECONCILIATION_DOCUMENTS in kinds,
        "has_authority_reconciliation": bool(kinds & {
            RECONCILIATION_AUTHORITY, RECONCILIATION_DIIA, RECONCILIATION_OTHER_TERRITORY,
        }),
        "count": len(rows),
        "last_date": rows[0]["reconciliation_date"] if rows else "",
    }
