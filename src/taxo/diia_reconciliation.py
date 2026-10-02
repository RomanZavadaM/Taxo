# -*- coding: utf-8 -*-
"""Taxo 10.5-r7 — local preparation cycle for official reconciliation via Diia.

Taxo does not submit data to Diia or the Oberih registry.  This module only
tracks the employer-side preparation steps and records an official reconciliation
*after* the user confirms that the external Diia fixation actually completed.
"""
from __future__ import annotations

from datetime import date, datetime

import military_accounting_2026 as military

APP_VERSION = "10.5-r7"

DIIA_GET_URL = (
    "https://diia.gov.ua/services/"
    "otrymannia-vidomostei-personalnoho-obliku-z-reiestru-viiskovozoboviazanykh"
)
DIIA_UPDATE_URL = (
    "https://diia.gov.ua/services/"
    "aktualizatsiia-vidomostei-personalnoho-obliku-pratsivnykiv"
)
DIIA_FIX_URL = "https://diia.gov.ua/services/fiksatsiia-vidomostei-personalnoho-obliku"

STATUS_DRAFT = "draft"
STATUS_DATA_RECEIVED = "data_received"
STATUS_UPDATES_COMPLETED = "updates_completed"
STATUS_FIXED = "fixed"
STATUS_CANCELLED = "cancelled"

STATUS_LABELS = {
    STATUS_DRAFT: "Підготовка",
    STATUS_DATA_RECEIVED: "Відомості отримано та імпортовано",
    STATUS_UPDATES_COMPLETED: "Актуалізації завершено / не потрібні",
    STATUS_FIXED: "Фіксацію в Дії підтверджено",
    STATUS_CANCELLED: "Скасовано",
}


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _iso_day(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return date.fromisoformat(str(value).strip()[:10]).isoformat()


def ensure_schema_on_connection(con):
    con.executescript("""
        CREATE TABLE IF NOT EXISTS military_diia_reconciliation_cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft',
            edrpou_snapshot TEXT DEFAULT '',
            registry_import_id INTEGER REFERENCES employee_registry_imports(id) ON DELETE SET NULL,
            started_at TEXT NOT NULL,
            data_received_at TEXT DEFAULT '',
            updates_completed_at TEXT DEFAULT '',
            fixation_date TEXT DEFAULT '',
            confirmation_reference TEXT DEFAULT '',
            result TEXT DEFAULT '',
            note TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_military_diia_cycles_year
            ON military_diia_reconciliation_cycles(year,status,id DESC);
    """)


def ensure_schema(core):
    con = core.db()
    try:
        ensure_schema_on_connection(con)
        con.commit()
    finally:
        con.close()


def latest_personnel_import(con):
    """Return the latest state-registry import, if the personnel registry exists."""
    ensure_schema_on_connection(con)
    try:
        return con.execute(
            """SELECT * FROM employee_registry_imports
               ORDER BY imported_at DESC,id DESC LIMIT 1"""
        ).fetchone()
    except Exception:
        return None


def latest_cycle(con, year=None, include_cancelled=False):
    ensure_schema_on_connection(con)
    where = []
    params = []
    if year is not None:
        where.append("year=?")
        params.append(int(year))
    if not include_cancelled:
        where.append("status<>?")
        params.append(STATUS_CANCELLED)
    sql = "SELECT * FROM military_diia_reconciliation_cycles"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC LIMIT 1"
    return con.execute(sql, params).fetchone()


def start_cycle(con, edrpou="", year=None, note=""):
    """Start/resume a local preparation cycle.

    There can be more than one historical cycle per year, but an unfinished cycle
    is resumed instead of duplicated.  This local row has no legal effect by itself.
    """
    ensure_schema_on_connection(con)
    year = int(year or date.today().year)
    existing = latest_cycle(con, year=year)
    if existing is not None and existing["status"] != STATUS_FIXED:
        return existing
    now = _now()
    cur = con.execute(
        """INSERT INTO military_diia_reconciliation_cycles(
               year,status,edrpou_snapshot,started_at,note,created_at,updated_at
           ) VALUES(?,?,?,?,?,?,?)""",
        (year, STATUS_DRAFT, str(edrpou or "").strip(), now,
         str(note or "").strip(), now, now),
    )
    return con.execute(
        "SELECT * FROM military_diia_reconciliation_cycles WHERE id=?", (cur.lastrowid,)
    ).fetchone()


def _cycle(con, cycle_id):
    ensure_schema_on_connection(con)
    row = con.execute(
        "SELECT * FROM military_diia_reconciliation_cycles WHERE id=?", (int(cycle_id),)
    ).fetchone()
    if row is None:
        raise ValueError("Цикл звіряння через Дію не знайдено.")
    return row


def mark_data_received(con, cycle_id, import_id=None):
    """Mark that downloaded state data were imported/compared in Taxo.

    A real registry import is required. Opening the Diia service alone is not enough.
    """
    row = _cycle(con, cycle_id)
    if row["status"] in {STATUS_FIXED, STATUS_CANCELLED}:
        raise ValueError("Завершений або скасований цикл не можна змінювати.")
    imported = None
    if import_id is not None:
        imported = con.execute(
            "SELECT * FROM employee_registry_imports WHERE id=?", (int(import_id),)
        ).fetchone()
    else:
        imported = latest_personnel_import(con)
    if imported is None:
        raise ValueError(
            "Спочатку отримайте відомості з Дії та імпортуйте/звірте XLSX у Taxo. "
            "Саме відкриття сервісу Дії не є отриманням або звірянням даних."
        )
    now = _now()
    con.execute(
        """UPDATE military_diia_reconciliation_cycles
           SET status=?,registry_import_id=?,data_received_at=?,updated_at=?
           WHERE id=?""",
        (STATUS_DATA_RECEIVED, int(imported["id"]), now, now, int(cycle_id)),
    )
    return _cycle(con, cycle_id)


def mark_updates_completed(con, cycle_id, note=""):
    """Record only the employer's local preparation state, not official fixation."""
    row = _cycle(con, cycle_id)
    if row["status"] in {STATUS_FIXED, STATUS_CANCELLED}:
        raise ValueError("Завершений або скасований цикл не можна змінювати.")
    if not str(row["data_received_at"] or "").strip():
        raise ValueError("Спочатку зафіксуйте отримання та імпорт відомостей з Дії.")
    now = _now()
    final_note = str(note or "").strip() or str(row["note"] or "").strip()
    con.execute(
        """UPDATE military_diia_reconciliation_cycles
           SET status=?,updates_completed_at=?,note=?,updated_at=? WHERE id=?""",
        (STATUS_UPDATES_COMPLETED, now, final_note, now, int(cycle_id)),
    )
    return _cycle(con, cycle_id)


def record_external_fixation(con, cycle_id, fixation_date, reference="", result="", note=""):
    """Record a fact that already happened in the external Diia service.

    This is the only r7 operation that writes RECONCILIATION_DIIA into the existing
    official journal.  Taxo never calls the state service from here.
    """
    row = _cycle(con, cycle_id)
    if row["status"] == STATUS_FIXED:
        raise ValueError("Цей цикл уже зафіксовано як завершений.")
    if row["status"] == STATUS_CANCELLED:
        raise ValueError("Скасований цикл не можна завершити.")
    if not str(row["data_received_at"] or "").strip():
        raise ValueError("Немає локального підтвердження, що відомості отримано та імпортовано.")
    if not str(row["updates_completed_at"] or "").strip():
        raise ValueError("Спочатку підтвердьте, що необхідні актуалізації завершено або вони не потрібні.")
    reference = str(reference or "").strip()
    result = str(result or "").strip()
    note = str(note or "").strip()
    if not (reference or result):
        raise ValueError(
            "Вкажіть номер/реквізит заяви або короткий опис фактичного результату фіксації в Дії."
        )
    day = _iso_day(fixation_date)
    military.record_official_reconciliation(
        con,
        day,
        military.RECONCILIATION_DIIA,
        method="Портал Дія — Фіксація відомостей персонального обліку",
        authority="Портал Дія / Реєстр військовозобов'язаних",
        result=result,
        reference=reference,
        note=("Taxo лише зафіксував повідомлений користувачем результат зовнішньої процедури. " + note).strip(),
    )
    now = _now()
    con.execute(
        """UPDATE military_diia_reconciliation_cycles
           SET status=?,fixation_date=?,confirmation_reference=?,result=?,note=?,updated_at=?
           WHERE id=?""",
        (STATUS_FIXED, day, reference, result, note, now, int(cycle_id)),
    )
    return _cycle(con, cycle_id)


def cancel_cycle(con, cycle_id, note=""):
    row = _cycle(con, cycle_id)
    if row["status"] == STATUS_FIXED:
        raise ValueError("Фактично завершений цикл не скасовується локально.")
    now = _now()
    con.execute(
        """UPDATE military_diia_reconciliation_cycles
           SET status=?,note=?,updated_at=? WHERE id=?""",
        (STATUS_CANCELLED, str(note or "").strip(), now, int(cycle_id)),
    )
    return _cycle(con, cycle_id)


def readiness(con, edrpou="", today=None):
    """Informational readiness for the external Diia workflow.

    Missing values are warnings for the operator. They do not manufacture legal
    conclusions about a person and do not change state-registry data.
    """
    ensure_schema_on_connection(con)
    today = today or date.today()
    latest_import = latest_personnel_import(con)
    try:
        employees = con.execute(
            "SELECT id,rnokpp FROM employees WHERE COALESCE(active,1)=1"
        ).fetchall()
    except Exception:
        employees = []
    active_count = len(employees)
    with_rnokpp = sum(1 for row in employees if str(row["rnokpp"] or "").strip())
    try:
        profile_count = con.execute(
            """SELECT COUNT(*) FROM employee_military_profile p
               JOIN employees e ON e.id=p.employee_id
               WHERE COALESCE(e.active,1)=1"""
        ).fetchone()[0]
    except Exception:
        profile_count = 0
    cycle = latest_cycle(con, year=today.year)
    return {
        "year": today.year,
        "edrpou": str(edrpou or "").strip(),
        "has_edrpou": bool(str(edrpou or "").strip()),
        "latest_import_id": int(latest_import["id"]) if latest_import is not None else None,
        "latest_imported_at": str(latest_import["imported_at"] or "") if latest_import is not None else "",
        "latest_source_name": str(latest_import["source_name"] or "") if latest_import is not None else "",
        "has_registry_import": latest_import is not None,
        "active_employees": active_count,
        "employees_with_rnokpp": with_rnokpp,
        "employees_with_military_profile": int(profile_count or 0),
        "cycle": cycle,
    }


def service_steps():
    return (
        {
            "key": "get",
            "title": "1. Отримати відомості персонального обліку",
            "url": DIIA_GET_URL,
            "hint": "Завантажити актуальний файл з Реєстру для перевірки та щорічної звірки.",
        },
        {
            "key": "update",
            "title": "2. Актуалізувати відомості працівників",
            "url": DIIA_UPDATE_URL,
            "hint": "За потреби додати/уточнити доступні дані або прибрати запис про трудові відносини після звільнення.",
        },
        {
            "key": "fix",
            "title": "3. Фіксація відомостей персонального обліку",
            "url": DIIA_FIX_URL,
            "hint": "Після перевірки й завершення необхідних актуалізацій виконати офіційну фіксацію в Дії.",
        },
    )
