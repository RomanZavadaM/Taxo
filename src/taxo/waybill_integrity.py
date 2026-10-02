# -*- coding: utf-8 -*-
"""Taxo 10.9-r2 — незнищувана історія виданих шляхових листів.

Модуль навмисно не містить UI. Він захищає три інваріанти:
- 48-місячне очищення табеля не видаляє worklog, на який посилається видана шляхівка;
- пара серія+номер після першої видачі ніколи не стає доступною повторно, навіть після анулювання;
- водія/worklog з історією виданих шляхівок не можна фізично видалити каскадом.
"""
from __future__ import annotations

from datetime import date

APP_VERSION = "10.9-r2"


def retention_cutoff(today=None, months=48):
    """Початок найстарішого місяця, який залишається у звичайному табелі."""
    current = today or date.today()
    keep = max(1, int(months or 48))
    total = current.year * 12 + (current.month - 1) - (keep - 1)
    year, month0 = divmod(total, 12)
    return date(year, month0 + 1, 1)


def purge_old_preserving_issued_waybills(core, *, today=None):
    """Застосувати 48-місячний retention, не торкаючись джерел виданих шляхівок."""
    cutoff = retention_cutoff(today).isoformat()
    con = core.db()
    try:
        con.execute(
            """DELETE FROM worklog
                 WHERE work_date < ?
                   AND NOT EXISTS (
                       SELECT 1 FROM waybills w WHERE w.worklog_id=worklog.id
                   )""",
            (cutoff,),
        )
        con.execute("DELETE FROM employee_time_entries WHERE work_date < ?", (cutoff,))
        con.commit()
    finally:
        con.close()


def ensure_schema_on_connection(con):
    """Додати незворотний реєстр номерів і DB-level guards без втрати старих даних."""
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS waybill_number_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_series TEXT NOT NULL DEFAULT '',
            document_number TEXT NOT NULL,
            waybill_id INTEGER,
            first_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            source TEXT NOT NULL DEFAULT 'issued',
            UNIQUE(document_series, document_number)
        );
        CREATE INDEX IF NOT EXISTS idx_waybill_number_history_waybill
            ON waybill_number_history(waybill_id);
        """
    )

    # Спочатку відновлюємо історію з append-only журналу подій: саме там могли
    # залишитися номери, які вже були перезаписані в поточному рядку waybills.
    con.execute(
        """INSERT OR IGNORE INTO waybill_number_history(
               document_series,document_number,waybill_id,first_seen_at,source
           )
           SELECT COALESCE(document_series,''),document_number,waybill_id,
                  COALESCE(NULLIF(created_at,''),CURRENT_TIMESTAMP),event_type
             FROM waybill_events
            WHERE COALESCE(document_number,'')<>''
              AND event_type IN ('issued','reprint','void')
            ORDER BY id"""
    )
    con.execute(
        """INSERT OR IGNORE INTO waybill_number_history(
               document_series,document_number,waybill_id,first_seen_at,source
           )
           SELECT COALESCE(document_series,''),document_number,id,
                  COALESCE(NULLIF(issued_at,''),NULLIF(updated_at,''),CURRENT_TIMESTAMP),'current'
             FROM waybills
            WHERE COALESCE(document_number,'')<>''"""
    )

    con.executescript(
        """
        DROP TRIGGER IF EXISTS trg_waybills_number_insert_guard;
        CREATE TRIGGER trg_waybills_number_insert_guard
        BEFORE INSERT ON waybills
        WHEN COALESCE(NEW.document_number,'')<>''
         AND EXISTS (
             SELECT 1 FROM waybill_number_history h
              WHERE h.document_series=COALESCE(NEW.document_series,'')
                AND h.document_number=NEW.document_number
         )
        BEGIN
            SELECT RAISE(ABORT,'WAYBILL_NUMBER_ALREADY_USED');
        END;

        DROP TRIGGER IF EXISTS trg_waybills_number_update_guard;
        CREATE TRIGGER trg_waybills_number_update_guard
        BEFORE UPDATE OF document_series,document_number ON waybills
        WHEN COALESCE(NEW.document_number,'')<>''
         AND (COALESCE(OLD.document_series,'')<>COALESCE(NEW.document_series,'')
              OR COALESCE(OLD.document_number,'')<>COALESCE(NEW.document_number,''))
         AND EXISTS (
             SELECT 1 FROM waybill_number_history h
              WHERE h.document_series=COALESCE(NEW.document_series,'')
                AND h.document_number=NEW.document_number
         )
        BEGIN
            SELECT RAISE(ABORT,'WAYBILL_NUMBER_ALREADY_USED');
        END;

        DROP TRIGGER IF EXISTS trg_waybills_number_insert_record;
        CREATE TRIGGER trg_waybills_number_insert_record
        AFTER INSERT ON waybills
        WHEN COALESCE(NEW.document_number,'')<>''
        BEGIN
            INSERT OR IGNORE INTO waybill_number_history(
                document_series,document_number,waybill_id,first_seen_at,source
            ) VALUES(
                COALESCE(NEW.document_series,''),NEW.document_number,NEW.id,
                COALESCE(NULLIF(NEW.issued_at,''),CURRENT_TIMESTAMP),'issued'
            );
        END;

        DROP TRIGGER IF EXISTS trg_waybills_number_update_record;
        CREATE TRIGGER trg_waybills_number_update_record
        AFTER UPDATE OF document_series,document_number ON waybills
        WHEN COALESCE(NEW.document_number,'')<>''
         AND (COALESCE(OLD.document_series,'')<>COALESCE(NEW.document_series,'')
              OR COALESCE(OLD.document_number,'')<>COALESCE(NEW.document_number,''))
        BEGIN
            INSERT OR IGNORE INTO waybill_number_history(
                document_series,document_number,waybill_id,first_seen_at,source
            ) VALUES(
                COALESCE(NEW.document_series,''),NEW.document_number,NEW.id,
                COALESCE(NULLIF(NEW.updated_at,''),CURRENT_TIMESTAMP),'reissued'
            );
        END;

        DROP TRIGGER IF EXISTS trg_worklog_preserve_issued_waybill;
        CREATE TRIGGER trg_worklog_preserve_issued_waybill
        BEFORE DELETE ON worklog
        WHEN EXISTS (SELECT 1 FROM waybills w WHERE w.worklog_id=OLD.id)
        BEGIN
            SELECT RAISE(ABORT,'WORKLOG_HAS_ISSUED_WAYBILL');
        END;

        DROP TRIGGER IF EXISTS trg_driver_preserve_issued_waybill;
        CREATE TRIGGER trg_driver_preserve_issued_waybill
        BEFORE DELETE ON drivers
        WHEN EXISTS (SELECT 1 FROM waybills w WHERE w.driver_id=OLD.id)
        BEGIN
            SELECT RAISE(ABORT,'DRIVER_HAS_ISSUED_WAYBILL');
        END;
        """
    )


def number_was_issued(con, document_series, document_number):
    """True, якщо серія+номер присутні в незворотній історії видачі."""
    number = str(document_number or "").strip()
    if not number:
        return False
    row = con.execute(
        """SELECT 1 FROM waybill_number_history
            WHERE document_series=? AND document_number=? LIMIT 1""",
        (str(document_series or "").strip(), number),
    ).fetchone()
    return row is not None


def install(core, App):
    """Підключити r2 до legacy runtime без дублювання UI-коду."""
    if getattr(core, "_WAYBILL_INTEGRITY_R2_INSTALLED", False):
        return App

    original_init_db = core.init_db

    def safe_purge_old():
        return purge_old_preserving_issued_waybills(core)

    def init_db_with_waybill_integrity():
        result = original_init_db()
        con = core.db()
        try:
            ensure_schema_on_connection(con)
            con.commit()
        finally:
            con.close()
        return result

    # original init_db resolves purge_old from the module globals at runtime,
    # therefore replacing it before init_db() runs protects startup retention.
    core.purge_old = safe_purge_old
    core.init_db = init_db_with_waybill_integrity
    core.waybill_number_was_issued = number_was_issued
    core.APP_VERSION = APP_VERSION
    core._WAYBILL_INTEGRITY_R2_INSTALLED = True
    return App
