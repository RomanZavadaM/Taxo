# -*- coding: utf-8 -*-
"""
Облік водіїв: база водіїв, 48 місяців робочого часу,
табелі та бланки підтвердження діяльності.

Запуск: py -3.13 main.py
"""
import calendar
import os
import sqlite3
import subprocess
import sys
import shutil
import tempfile
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

try:
    from docx.shared import Pt
except ImportError:
    Pt = None

try:
    from tachograph import TachographModule
except ImportError:
    TachographModule = None

try:
    from attestation_render import build_attestation_pdf, pdf_to_jpg_pages
except ImportError:
    build_attestation_pdf = None
    pdf_to_jpg_pages = None

APP_DIR = Path(__file__).resolve().parent

# Постійне сховище даних НЕ залежить від версії програми.
# Завдяки цьому при оновленні програми база не переноситься вручну.
DOCUMENTS_DIR = Path.home() / "Documents"
DATA_ROOT = DOCUMENTS_DIR / "DriverWorktime"
DATA_DIR = DATA_ROOT / "Data"
BACKUP_DIR = DATA_ROOT / "Backups"
OUTPUT_DIR = DATA_ROOT / "Output"
ATT_ARCHIVE_DIR = OUTPUT_DIR / "AttestationArchive"
ATT_REPLACED_DIR = ATT_ARCHIVE_DIR / "Replaced"
ATT_DELETED_DIR = ATT_ARCHIVE_DIR / "Deleted"
DB_PATH = DATA_DIR / "driver_worktime.sqlite3"
TEMPLATE_PATH = APP_DIR / "Бланк підтвердження.docx"
ATT_VISUAL_TEMPLATE_PATH = APP_DIR / "attestation_visual_template.pdf"

for _p in (DATA_DIR, BACKUP_DIR, OUTPUT_DIR, ATT_ARCHIVE_DIR, ATT_REPLACED_DIR, ATT_DELETED_DIR):
    _p.mkdir(parents=True, exist_ok=True)


def find_legacy_database():
    """Знаходить стару локальну БД першого запуску для одноразової міграції."""
    candidates = [
        APP_DIR / "driver_worktime.sqlite3",
        APP_DIR.parent / "driver_worktime.sqlite3",
    ]
    # Найчастіші сусідні папки попередніх версій. Не чіпаємо інші дані.
    for base in (APP_DIR.parent, APP_DIR.parent / "blank"):
        for name in ("driver_worktime_app_v2", "driver_worktime_app_v3", "driver_worktime_app_v4", "driver_worktime_app"):
            candidates.append(base / name / "driver_worktime.sqlite3")
    seen=set()
    for p in candidates:
        p=p.resolve()
        if p in seen:
            continue
        seen.add(p)
        if p.exists() and p.resolve() != DB_PATH.resolve():
            return p
    return None


def migrate_legacy_database():
    """Одноразово копіює існуючу БД у постійний каталог."""
    if DB_PATH.exists():
        return False, None
    old = find_legacy_database()
    if not old:
        return False, None
    tmp = DB_PATH.with_suffix(".sqlite3.migrating")
    shutil.copy2(old, tmp)
    tmp.replace(DB_PATH)
    return True, old


def backup_database(label="auto"):
    """Створює узгоджену SQLite-копію та зберігає останні 30 резервних копій."""
    if not DB_PATH.exists():
        return None
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target = BACKUP_DIR / f"driver_worktime_{label}_{stamp}.sqlite3"
    src_con = sqlite3.connect(DB_PATH)
    dst_con = sqlite3.connect(target)
    try:
        src_con.backup(dst_con)
        dst_con.commit()
    finally:
        dst_con.close()
        src_con.close()
    backups = sorted(BACKUP_DIR.glob("driver_worktime_*.sqlite3"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in backups[30:]:
        try:
            old.unlink()
        except OSError:
            pass
    return target


def auto_backup_database():
    """Не частіше одного разу на добу при запуску."""
    if not DB_PATH.exists():
        return None
    recent = [p for p in BACKUP_DIR.glob("driver_worktime_auto_*.sqlite3") if (datetime.now().timestamp() - p.stat().st_mtime) < 86400]
    if recent:
        return recent[0]
    return backup_database("auto")


def validate_database_file(path):
    """Перевіряє, що файл є справною та сумісною БД Taxo."""
    path=Path(path)
    if not path.exists() or not path.is_file():
        return False, "Файл не знайдено."

    con=None
    try:
        uri=f"file:{path.as_posix()}?mode=ro"
        con=sqlite3.connect(uri,uri=True)
        quick=con.execute("PRAGMA quick_check").fetchone()
        if not quick or str(quick[0]).lower()!="ok":
            return False, f"SQLite quick_check: {quick[0] if quick else 'невідомий результат'}"

        tables={
            r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        required={"drivers","worklog","company"}
        missing=sorted(required-tables)
        if missing:
            return False, "Не схожа на базу Taxo. Відсутні таблиці: " + ", ".join(missing)

        driver_count=con.execute("SELECT COUNT(*) FROM drivers").fetchone()[0]
        work_count=con.execute("SELECT COUNT(*) FROM worklog").fetchone()[0]
        return True, f"База справна. Водіїв: {driver_count}; записів табеля: {work_count}."
    except Exception as e:
        return False, str(e)
    finally:
        if con is not None:
            con.close()


def restore_database_from_file(source_path):
    """Атомарно відновлює основну БД із вибраної резервної копії."""
    source=Path(source_path)
    ok,details=validate_database_file(source)
    if not ok:
        raise ValueError(f"Обрана резервна копія не пройшла перевірку:\n{details}")

    safety_backup=backup_database("before_restore") if DB_PATH.exists() else None
    temp_target=DB_PATH.with_suffix(".sqlite3.restore_tmp")

    try:
        if temp_target.exists():
            temp_target.unlink()

        src_con=sqlite3.connect(f"file:{source.as_posix()}?mode=ro",uri=True)
        dst_con=sqlite3.connect(temp_target)
        try:
            src_con.backup(dst_con)
            dst_con.commit()
        finally:
            dst_con.close()
            src_con.close()

        ok2,details2=validate_database_file(temp_target)
        if not ok2:
            raise ValueError(f"Копія після перенесення не пройшла перевірку:\n{details2}")

        os.replace(temp_target,DB_PATH)
        init_db()

        final_ok,final_details=validate_database_file(DB_PATH)
        if not final_ok:
            raise ValueError(f"Відновлена база не пройшла фінальну перевірку:\n{final_details}")

        return safety_backup, final_details

    except Exception:
        try:
            if temp_target.exists():
                temp_target.unlink()
        except OSError:
            pass

        if safety_backup and Path(safety_backup).exists():
            try:
                shutil.copy2(safety_backup,DB_PATH)
                init_db()
            except Exception:
                pass
        raise

ACTIVITIES = {
    14: "Тимчасова непрацездатність",
    15: "Щорічна відпустка",
    16: "Відсутність / відпочинок",
    17: "Керування ТЗ, що не підпадає під дію Положення",
    18: "Інша робота",
    19: "Готовий і доступний для виконання професійних обов'язків",
}
DAY_TYPES = ["Робота", "Вихідний", "Відпустка", "Лікарняний", "Відпочинок", "Інша робота", "Доступний", "Інше"]

WORK_MODE_TACHO = "tacho"
WORK_MODE_NO_TACHO = "no_tacho_8h"
WORK_MODE_MANUAL = "manual"

WORK_MODE_LABELS = {
    WORK_MODE_TACHO: "ТАХО — маршрут / шаблон",
    WORK_MODE_NO_TACHO: "Без тахо — стандартні 8 год",
    WORK_MODE_MANUAL: "Інше / ручний облік",
}
WORK_MODE_BY_LABEL = {v:k for k,v in WORK_MODE_LABELS.items()}


def work_mode_label(value):
    return WORK_MODE_LABELS.get((value or "").strip(), WORK_MODE_LABELS[WORK_MODE_MANUAL])


TRANSPORT_PROFILES = [
    "Регулярні пасажирські перевезення",
    "Нерегулярні пасажирські перевезення",
    "Внутрішні вантажні перевезення",
    "Міжнародні вантажні перевезення",
    "Інші / змішані перевезення",
]
DEFAULT_TRANSPORT_PROFILE = TRANSPORT_PROFILES[0]


def current_transport_profile():
    value=get_setting("transport_profile", DEFAULT_TRANSPORT_PROFILE)
    return value if value in TRANSPORT_PROFILES else DEFAULT_TRANSPORT_PROFILE


def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con


def get_setting(key, default=""):
    try:
        con=db(); r=con.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone(); con.close()
        return (r[0] if r and r[0] is not None else default)
    except Exception:
        return default


def set_setting(key, value):
    con=db(); con.execute("INSERT INTO app_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value))); con.commit(); con.close()


def init_db():
    migrated, old_db = migrate_legacy_database()
    con = db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS app_settings (
        key TEXT PRIMARY KEY,
        value TEXT DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS company (
        id INTEGER PRIMARY KEY CHECK (id=1),
        name TEXT DEFAULT '',
        address TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        fax TEXT DEFAULT '',
        email TEXT DEFAULT '',
        signer_name TEXT DEFAULT '',
        signer_position TEXT DEFAULT '',
        name_en TEXT DEFAULT '',
        address_en TEXT DEFAULT '',
        signer_name_en TEXT DEFAULT '',
        signer_position_en TEXT DEFAULT '',
        place_en TEXT DEFAULT ''
    );
    INSERT OR IGNORE INTO company(id) VALUES (1);

    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        plate TEXT DEFAULT '',
        make_model TEXT DEFAULT '',
        year INTEGER,
        notes TEXT DEFAULT '',
        active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS drivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        last_name TEXT NOT NULL,
        first_name TEXT NOT NULL,
        middle_name TEXT DEFAULT '',
        last_name_en TEXT DEFAULT '',
        first_name_en TEXT DEFAULT '',
        middle_name_en TEXT DEFAULT '',
        birth_date TEXT DEFAULT '',
        license_series TEXT DEFAULT '',
        license_number TEXT DEFAULT '',
        license_issue_date TEXT DEFAULT '',
        license_issued_by TEXT DEFAULT '', -- legacy для старих баз
        employment_date TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS worklog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        driver_id INTEGER NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
        work_date TEXT NOT NULL,
        day_type TEXT NOT NULL DEFAULT 'Робота',
        start_time TEXT DEFAULT '',
        end_time TEXT DEFAULT '',
        work_hours REAL DEFAULT 0,
        driving_hours REAL DEFAULT 0,
        overtime_hours REAL DEFAULT 0,
        vehicle TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        UNIQUE(driver_id, work_date)
    );

    CREATE TABLE IF NOT EXISTS routes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        code TEXT DEFAULT '',
        description TEXT DEFAULT '',
        active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS route_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        route_name TEXT DEFAULT '',
        vehicle TEXT DEFAULT '',
        vehicle_id INTEGER,
        shift_type TEXT DEFAULT 'Безперервна',
        notes TEXT DEFAULT '',
        active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS route_template_segments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_id INTEGER NOT NULL REFERENCES route_templates(id) ON DELETE CASCADE,
        segment_no INTEGER NOT NULL,
        start_time TEXT DEFAULT '',
        end_time TEXT DEFAULT '',
        work_hours REAL DEFAULT 0,
        driving_hours REAL DEFAULT 0,
        activity_type TEXT DEFAULT 'Робота',
        note TEXT DEFAULT '',
        UNIQUE(template_id, segment_no)
    );

    CREATE TABLE IF NOT EXISTS work_segments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worklog_id INTEGER NOT NULL REFERENCES worklog(id) ON DELETE CASCADE,
        segment_no INTEGER NOT NULL,
        start_time TEXT DEFAULT '',
        end_time TEXT DEFAULT '',
        work_hours REAL DEFAULT 0,
        driving_hours REAL DEFAULT 0,
        activity_type TEXT DEFAULT 'Робота',
        note TEXT DEFAULT '',
        UNIQUE(worklog_id, segment_no)
    );

    CREATE TABLE IF NOT EXISTS attestations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        driver_id INTEGER NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
        period_from TEXT NOT NULL,
        period_to TEXT NOT NULL,
        activity_no INTEGER NOT NULL,
        place TEXT DEFAULT '',
        form_date TEXT DEFAULT '',
        file_path TEXT DEFAULT '',
        pdf_path TEXT DEFAULT '',
        jpg_page1_path TEXT DEFAULT '',
        jpg_page2_path TEXT DEFAULT '',
        status TEXT NOT NULL DEFAULT 'active',
        revision INTEGER NOT NULL DEFAULT 1,
        updated_at TEXT DEFAULT '',
        deleted_at TEXT DEFAULT '',
        delete_reason TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS attestation_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attestation_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        revision INTEGER NOT NULL DEFAULT 1,
        period_from TEXT NOT NULL,
        period_to TEXT NOT NULL,
        activity_no INTEGER NOT NULL,
        place TEXT DEFAULT '',
        form_date TEXT DEFAULT '',
        file_path TEXT DEFAULT '',
        pdf_path TEXT DEFAULT '',
        jpg_page1_path TEXT DEFAULT '',
        jpg_page2_path TEXT DEFAULT '',
        status TEXT DEFAULT 'active',
        note TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_attestation_audit_attestation
        ON attestation_audit(attestation_id, id);
    """)
    # Безпечна міграція старої БД v5: додаємо лише нові поля, не видаляючи старі.
    cols = {r[1] for r in con.execute("PRAGMA table_info(worklog)").fetchall()}
    for name, ddl in [
        ("route_name", "TEXT DEFAULT ''"),
        ("route_id", "INTEGER"),
        ("template_id", "INTEGER"),
        ("shift_type", "TEXT DEFAULT 'Безперервна'"),
        ("vehicle_id", "INTEGER"),
        ("accounting_mode", "TEXT DEFAULT 'manual'"),
    ]:
        if name not in cols:
            con.execute(f"ALTER TABLE worklog ADD COLUMN {name} {ddl}")

    # v8.50: старі явно розділені маршрутні записи трактуємо як тахографний режим.
    # Це відповідає нашому внутрішньому правилу: шаблонні поділені зміни
    # мають повне покриття тахокартою + бланками поза інтервалами маршруту.
    con.execute("""
        UPDATE worklog
           SET accounting_mode=?
         WHERE COALESCE(accounting_mode,'') IN ('','manual')
           AND COALESCE(route_name,'') <> ''
           AND COALESCE(shift_type,'')='Розділена на частини'
           AND id IN (
               SELECT worklog_id
                 FROM work_segments
                GROUP BY worklog_id
               HAVING COUNT(*) > 1
           )
    """,(WORK_MODE_TACHO,))
    # v8.39: окреме поле дати видачі посвідчення.
    # v8.58: окремі англомовні реквізити підприємства для зворотного боку бланка.
    # Порожнє англійське поле означає автоматичний fallback на українське.
    ccols = {r[1] for r in con.execute("PRAGMA table_info(company)").fetchall()}
    for name, ddl in [
        ("name_en", "TEXT DEFAULT ''"),
        ("address_en", "TEXT DEFAULT ''"),
        ("signer_name_en", "TEXT DEFAULT ''"),
        ("signer_position_en", "TEXT DEFAULT ''"),
        ("place_en", "TEXT DEFAULT ''"),
    ]:
        if name not in ccols:
            con.execute(f"ALTER TABLE company ADD COLUMN {name} {ddl}")

    dcols = {r[1] for r in con.execute("PRAGMA table_info(drivers)").fetchall()}
    for name, ddl in [
        ("last_name_en", "TEXT DEFAULT ''"),
        ("first_name_en", "TEXT DEFAULT ''"),
        ("middle_name_en", "TEXT DEFAULT ''"),
    ]:
        if name not in dcols:
            con.execute(f"ALTER TABLE drivers ADD COLUMN {name} {ddl}")
    if "license_issue_date" not in dcols:
        con.execute("ALTER TABLE drivers ADD COLUMN license_issue_date TEXT DEFAULT ''")

    # Якщо у старому legacy-полі вже була введена дата, переносимо її автоматично.
    old_rows = con.execute(
        "SELECT id, license_issued_by, license_issue_date FROM drivers"
    ).fetchall()
    for dr in old_rows:
        if (dr["license_issue_date"] or "").strip():
            continue
        raw = (dr["license_issued_by"] or "").strip()
        if not raw:
            continue
        parsed = None
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                parsed = datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
                break
            except ValueError:
                pass
        if parsed:
            con.execute(
                "UPDATE drivers SET license_issue_date=? WHERE id=?",
                (parsed, dr["id"])
            )

    rcols = {r[1] for r in con.execute("PRAGMA table_info(route_templates)").fetchall()}
    if "vehicle_id" not in rcols:
        con.execute("ALTER TABLE route_templates ADD COLUMN vehicle_id INTEGER")
    if "route_id" not in rcols:
        con.execute("ALTER TABLE route_templates ADD COLUMN route_id INTEGER")

    # v8.57: Бланки підтвердження мають керований життєвий цикл.
    # Старі записи автоматично вважаються активними ревізії 1.
    acols = {r[1] for r in con.execute("PRAGMA table_info(attestations)").fetchall()}
    for name, ddl in [
        ("status", "TEXT NOT NULL DEFAULT 'active'"),
        ("revision", "INTEGER NOT NULL DEFAULT 1"),
        ("updated_at", "TEXT DEFAULT ''"),
        ("deleted_at", "TEXT DEFAULT ''"),
        ("delete_reason", "TEXT DEFAULT ''"),
        ("pdf_path", "TEXT DEFAULT ''"),
        ("jpg_page1_path", "TEXT DEFAULT ''"),
        ("jpg_page2_path", "TEXT DEFAULT ''"),
    ]:
        if name not in acols:
            con.execute(f"ALTER TABLE attestations ADD COLUMN {name} {ddl}")
    con.execute("UPDATE attestations SET status='active' WHERE COALESCE(status,'')=''")
    con.execute("UPDATE attestations SET revision=1 WHERE COALESCE(revision,0)<1")

    # v8.61: журнал змін зберігає шляхи всіх форматів Бланка.
    audit_cols = {r[1] for r in con.execute("PRAGMA table_info(attestation_audit)").fetchall()}
    for name, ddl in [
        ("pdf_path", "TEXT DEFAULT ''"),
        ("jpg_page1_path", "TEXT DEFAULT ''"),
        ("jpg_page2_path", "TEXT DEFAULT ''"),
    ]:
        if name not in audit_cols:
            con.execute(f"ALTER TABLE attestation_audit ADD COLUMN {name} {ddl}")

    con.commit()
    con.close()
    purge_old()
    # Після міграції одразу робимо резервну копію старої бази в новому сховищі.
    auto_backup_database()
    return migrated, old_db


def purge_old():
    # Зберігаємо рівно 48 місяців від початку поточного місяця.
    today = date.today()
    y, m = today.year, today.month
    total = y * 12 + (m - 1) - 47
    min_y, min_m = divmod(total, 12)
    cutoff_date = date(min_y, min_m + 1, 1)
    cutoff = cutoff_date.isoformat()
    con = db()
    con.execute("DELETE FROM worklog WHERE work_date < ?", (cutoff,))

    # v8.62: Бланки підтвердження та їх журнал більше НЕ очищаються автоматично.
    # 48-місячне вікно лишається для робочого табеля, але юридичні/архівні
    # документи зберігаються безстроково, доки користувач сам не натисне
    # «Видалити назавжди». Це усуває непомітне зникнення старих бланків.
    con.commit()
    con.close()


def fmt_date(s):
    if not s:
        return ""
    try:
        return datetime.strptime(s, "%Y-%m-%d").strftime("%d.%m.%Y")
    except ValueError:
        return s


def parse_hours(start, end):
    try:
        a = datetime.strptime(start, "%H:%M")
        b = datetime.strptime(end, "%H:%M")
        if b < a:
            b += timedelta(days=1)
        return round((b - a).seconds / 3600, 2)
    except Exception:
        return 0.0


def time_to_minutes(value):
    try:
        h, m = map(int, value.strip().split(":"))
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError
        return h * 60 + m
    except Exception:
        raise ValueError(f"Невірний час: {value}")


def duration_minutes(start, end):
    a = time_to_minutes(start)
    b = time_to_minutes(end)
    if b <= a:
        b += 24 * 60
    return b - a


def segment_duration(start, end):
    return round(duration_minutes(start, end) / 60.0, 2)


def hours_value_to_minutes(value):
    """Єдина внутрішня міра тривалості — цілі хвилини.

    Приймає:
    - десяткові години: 2.5, 2,5, 2.42;
    - формат ГГ:ХХ: 2:30, 8:55.
    Старі значення 2.42 / 8.92 трактуються як десяткові години
    і округлюються до найближчої хвилини.
    """
    if value is None:
        return 0
    s = str(value).strip().lower()
    if not s:
        return 0
    if ":" in s:
        try:
            h, m = s.split(":", 1)
            h = int(h.strip())
            m = int(m.strip())
            if h < 0 or not (0 <= m <= 59):
                raise ValueError
            return h * 60 + m
        except Exception:
            raise ValueError(f"Невірна тривалість: {value}")
    s = s.replace(",", ".")
    try:
        dec = Decimal(s)
        if dec < 0:
            raise ValueError
        return int((dec * Decimal(60)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    except Exception:
        raise ValueError(f"Невірна тривалість: {value}")


def minutes_to_db_hours(minutes):
    return round(int(minutes) / 60.0, 6)


def minutes_hhmm(minutes):
    m = max(0, int(round(minutes)))
    return f"{m // 60}:{m % 60:02d}"


def minutes_decimal(minutes):
    return round(int(round(minutes)) / 60.0, 2)


def minutes_dual(minutes):
    m = max(0, int(round(minutes)))
    return f"{minutes_hhmm(m)} ({minutes_decimal(m):.2f} год)"


def hours_value_hhmm(value):
    try:
        return minutes_hhmm(hours_value_to_minutes(value))
    except Exception:
        return str(value or "")


def format_hours(value):
    try:
        return f"{float(value):.2f}".rstrip("0").rstrip(".")
    except Exception:
        return "0"


def segments_summary(segments):
    if not segments:
        return ""
    return " / ".join(f"{r['start_time']}-{r['end_time']}" for r in segments)


def gaps_minutes(segments):
    if len(segments) < 2:
        return []
    out=[]
    ordered=sorted(segments, key=lambda r: time_to_minutes(r['start_time']))
    for a,b in zip(ordered, ordered[1:]):
        end=time_to_minutes(a['end_time'])
        start=time_to_minutes(b['start_time'])
        if start <= end:
            start += 24*60
        gap=start-end
        if gap > 0:
            out.append(gap)
    return out


def gaps_summary(segments):
    return ", ".join(minutes_hhmm(x) for x in gaps_minutes(segments))


def month_dates(year, month):
    days = calendar.monthrange(year, month)[1]
    return [date(year, month, d) for d in range(1, days + 1)]


def set_paragraph_text(p, new_text):
    # Імпорт тут теж робимо явно: це гарантує роботу навіть якщо python-docx
    # завантажився нестандартно у середовищі користувача.
    from docx.shared import Pt as DocxPt
    if not p.runs:
        run = p.add_run(new_text)
    else:
        # Зберігаємо стиль першого run, але робимо текст одним run.
        run = p.runs[0]
        run.text = new_text
        for r in p.runs[1:]:
            r.text = ""
    # Довгі автоматично підставлені поля трохи ущільнюємо,
    # щоб вони не виштовхували наступні блоки на нову сторінку.
    n = len(new_text)
    if n > 155:
        run.font.size = DocxPt(10)
    elif n > 105:
        run.font.size = DocxPt(10.5)

def set_paragraph_label_value(p, label, value, bold_value=True, reference_run=None):
    """Підпис окремо, значення з нового рядка.
    Значення бере розмір шрифту з reference_run (зазвичай з наступного поля шаблону),
    щоб назва підприємства виглядала в тому самому форматі, що й решта бланка.
    """
    from docx.shared import Pt as DocxPt
    from copy import copy
    ref_size = None
    ref_name = None
    ref_bold = None
    if reference_run is not None:
        try:
            ref_size = reference_run.font.size
            ref_name = reference_run.font.name
            ref_bold = reference_run.bold
        except Exception:
            pass
    p.clear()
    r1 = p.add_run(label)
    r2 = p.add_run()
    r2.add_break()
    r3 = p.add_run(value or "")
    r3.bold = bold_value
    if ref_size is not None:
        r3.font.size = copy(ref_size)
    elif ref_name:
        r3.font.name = ref_name
    # Якщо шаблон не дав розмір, використовуємо читабельний розмір полів бланка.
    if r3.font.size is None:
        r3.font.size = DocxPt(11)
    if ref_name:
        r3.font.name = ref_name
    # Не стискаємо назву до 10 pt: краще переносити її на кілька рядків.


def set_top_block_value(p, label, value, value_size=14, italic=False):
    """Верх українського бланка: підпис на першому рядку,
    значення з наступного рядка, збільшене та жирне.
    """
    from docx.shared import Pt as DocxPt
    p.clear()
    r1 = p.add_run(label)
    r1.font.size = DocxPt(11)
    br = p.add_run()
    br.add_break()
    r2 = p.add_run(value or "")
    r2.bold = True
    r2.italic = italic
    r2.font.size = DocxPt(value_size)

def set_inline_bold_value(p, label, value, value_size=12, italic=False):
    """Пункти 3–5: назва поля звичайна, підставлене значення жирне."""
    from docx.shared import Pt as DocxPt
    p.clear()
    r1 = p.add_run(label)
    r1.font.size = DocxPt(11)
    r2 = p.add_run(value or "")
    r2.bold = True
    r2.italic = italic
    r2.font.size = DocxPt(value_size)


def remove_standalone_underline_lines(cell):
    """Прибирає службові лінії з шаблону, які після автозаповнення
    залишають непотрібне підкреслення під пунктами 1–2.
    """
    from docx.oxml import OxmlElement
    for p in list(cell.paragraphs):
        text = p.text.strip().replace("\u00a0", " ")
        compact = text.replace(" ", "")
        if compact and set(compact) == {"_"}:
            p_el = p._element
            p_el.getparent().remove(p_el)


def replace_in_cell(cell, replacements):
    for p in cell.paragraphs:
        txt = p.text
        new = txt
        for old, repl in replacements.items():
            new = new.replace(old, repl)
        if new != txt:
            set_paragraph_text(p, new)


def _att_set_text(paragraph, text, size=12, bold=False, italic=False):
    """Записує один фрагмент у рядок бланка."""
    from docx.shared import Pt as DocxPt
    paragraph.clear()
    run=paragraph.add_run(text or "")
    run.font.size=DocxPt(size)
    run.bold=bold
    run.italic=italic


def _att_set_runs(paragraph, parts, size=12):
    """Записує рядок частинами.

    parts: [(текст, жирний), ...]
    Статичний текст офіційної форми лишається звичайним,
    а значення, які підставляє Taxo, виділяються жирним.
    """
    from docx.shared import Pt as DocxPt
    paragraph.clear()
    for part_text, is_bold in parts:
        run=paragraph.add_run(str(part_text or ""))
        run.font.size=DocxPt(size)
        run.bold=bool(is_bold)


def _att_set_checkbox(paragraph, number, checked, text, size=12):
    """Один рядок позиції 14-19; вибраний прапорець виділено жирним."""
    _att_set_runs(
        paragraph,
        [
            (f"{number}. ", False),
            ("☒" if checked else "☐", checked),
            (f" {text}", False),
        ],
        size=size
    )


def fill_attestation(driver, period_from, period_to, activity_no, place, form_date, out_path):
    """Заповнює чинний Додаток 3 до Положення №340.

    Структура офіційного бланка не перебудовується.
    Усі значення, які вносить Taxo, друкуються жирним шрифтом.
    """
    try:
        from docx import Document
    except ImportError:
        raise RuntimeError("Не встановлено python-docx. Запустіть START.bat ще раз.")

    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Не знайдено шаблон: {TEMPLATE_PATH}")

    con = db()
    company = con.execute("SELECT * FROM company WHERE id=1").fetchone()
    con.close()

    driver_full = " ".join(
        x for x in [driver["last_name"], driver["first_name"], driver["middle_name"]] if x
    ).strip()
    # v8.60: англійська сторона використовує англійські ПІБ водія,
    # якщо вони заповнені. Кожне поле має окремий fallback на українське.
    driver_last_en=((driver["last_name_en"] or "").strip() or (driver["last_name"] or "").strip())
    driver_first_en=((driver["first_name_en"] or "").strip() or (driver["first_name"] or "").strip())
    driver_middle_en=((driver["middle_name_en"] or "").strip() or (driver["middle_name"] or "").strip())
    driver_full_en=" ".join(x for x in [driver_last_en,driver_first_en,driver_middle_en] if x).strip()
    license_issue_date = fmt_date(driver["license_issue_date"])
    employment = fmt_date(driver["employment_date"])
    birth_date = fmt_date(driver["birth_date"])
    series=(driver["license_series"] or "").strip()
    number=(driver["license_number"] or "").strip()
    license_number_en=" ".join(x for x in [series,number] if x).strip()
    form_date_fmt=fmt_date(form_date)
    # Єдине джерело місця в бланку — місце директора/представника перевізника.
    # Поле водія завжди автоматично дублює саме це значення.
    director_place=(place or "").strip()

    # v8.58: англійська сторона має власні реквізити підприємства.
    # Якщо конкретне англійське поле порожнє, беремо українське значення.
    company_name_en=((company["name_en"] or "").strip() or (company["name"] or "").strip())
    company_address_en=((company["address_en"] or "").strip() or (company["address"] or "").strip())
    signer_name_en=((company["signer_name_en"] or "").strip() or (company["signer_name"] or "").strip())
    signer_position_en=((company["signer_position_en"] or "").strip() or (company["signer_position"] or "").strip())
    director_place_en=((company["place_en"] or "").strip() or director_place)

    doc = Document(str(TEMPLATE_PATH))
    if len(doc.tables) < 2:
        raise RuntimeError("Шаблон бланка пошкоджений: очікується лицьова та зворотна таблиця.")

    ua = doc.tables[0].cell(0,0)
    en = doc.tables[1].cell(0,0)

    # ----------------------- ЛИЦЬОВИЙ БІК -----------------------
    up=ua.paragraphs

    # 1. Найменування та 2. адреса мають окремі рядки значення.
    if len(up) > 2:
        _att_set_text(up[2], company["name"] or "", bold=True)
    if len(up) > 5:
        _att_set_text(up[4], company["address"] or "", bold=True)
        _att_set_text(up[5], "")

    # 3-5.
    if len(up) > 8:
        _att_set_runs(up[6], [
            ("3. Номер телефону: ", False),
            (company["phone"] or "", True),
        ])
        _att_set_runs(up[7], [
            ("4. Номер факсу: ", False),
            (company["fax"] or "", True),
        ])
        _att_set_runs(up[8], [
            ("5. Електронна адреса ", False),
            (company["email"] or "", True),
        ])

    # 6-9.
    if len(up) > 14:
        _att_set_runs(up[10], [
            ("6. Прізвище та власне ім’я: ", False),
            (company["signer_name"] or "", True),
        ])
        _att_set_runs(up[11], [
            ("7. Посада на підприємстві: ", False),
            (company["signer_position"] or "", True),
        ])
        _att_set_runs(up[13], [
            ("8. Прізвище та власне ім’я: ", False),
            (driver_full, True),
        ])
        _att_set_runs(up[14], [
            ("9. Дата народження: ", False),
            (birth_date, True),
        ])

    # 10. Усі внесені реквізити посвідчення виділяємо жирним.
    if len(up) > 15:
        _att_set_runs(up[15], [
            ("10. Посвідчення водія: серія ", False),
            (series, True),
            (" № ", False),
            (number, True),
            (", видане ", False),
            (license_issue_date, True),
        ])

    # 11. Зберігаємо структуру чинного українського Додатка 3.
    if len(up) > 17:
        _att_set_runs(up[16], [
            ("11. Почав працювати на підприємстві з ", False),
            (employment, True),
            ("/серія водійського посвідчення ", False),
            (series, True),
        ])
        _att_set_runs(up[17], [
            ("№ ", False),
            (number, True),
            (", виданого ", False),
            (license_issue_date, True),
        ])

    # 12-13.
    if len(up) > 20:
        _att_set_runs(up[19], [
            ("12. з (година/день/місяць/рік): ", False),
            (period_from, True),
        ])
        _att_set_runs(up[20], [
            ("13. по (година/день/місяць/рік): ", False),
            (period_to, True),
        ])

    # 14-19 — одна позиція.
    if len(up) > 27:
        _att_set_checkbox(up[21],14,activity_no==14,"перебував у стані тимчасової непрацездатності;")
        _att_set_checkbox(up[22],15,activity_no==15,"перебував у щорічній відпустці;")
        _att_set_checkbox(up[23],16,activity_no==16,"був відсутній або перебував на відпочинку;")
        _att_set_checkbox(
            up[24],17,activity_no==17,
            "керував ТЗ, які не підпадають під підпункти 1 та 2 пункту 3 розділу І Положення,"
        )
        # up[25] — офіційне продовження п.17; не переписуємо.
        _att_set_checkbox(up[26],18,activity_no==18,"виконував іншу роботу;")
        _att_set_checkbox(up[27],19,activity_no==19,"був готовий і доступний для виконання професійних обов’язків;")

    # 20.
    if len(up) > 29:
        _att_set_runs(up[28], [
            ("20. Місце ", False),
            (director_place, True),
            ("    Дата ", False),
            (form_date_fmt, True),
        ])
        _att_set_text(up[29], "Підпис ______________________________")

    # ----------------------- ЗВОРОТНИЙ БІК -----------------------
    ep=en.paragraphs

    if len(ep) > 1:
        _att_set_runs(ep[1], [
            ("1. Name of the undertaking: ", False),
            (company_name_en, True),
        ])

    if len(ep) > 4:
        _att_set_text(ep[3], company_address_en, bold=True)
        _att_set_text(ep[4], "")

    if len(ep) > 9:
        # У шаблоні 3 і 4 мають окремі рядки для значень.
        _att_set_text(ep[6], company["phone"] or "", bold=True)
        _att_set_text(ep[8], company["fax"] or "", bold=True)
        _att_set_runs(ep[9], [
            ("5. E-mail address: ", False),
            (company["email"] or "", True),
        ])

    if len(ep) > 18:
        _att_set_runs(ep[11], [
            ("6. Name and first name: ", False),
            (signer_name_en, True),
        ])
        _att_set_runs(ep[12], [
            ("7. Position in the undertaking: ", False),
            (signer_position_en, True),
        ])
        _att_set_runs(ep[14], [
            ("8. Name and first name: ", False),
            (driver_full_en, True),
        ])
        _att_set_text(ep[16], birth_date, bold=True)
        _att_set_runs(ep[17], [
            ("10. Driving license or identity card or passport number: ", False),
            (license_number_en, True),
        ])
        _att_set_runs(ep[18], [
            ("11. who has started to work at the undertaking on (day/month/year): ", False),
            (employment, True),
        ])

    if len(ep) > 21:
        _att_set_runs(ep[20], [
            ("12. from (hour/day/month/year): ", False),
            (period_from, True),
        ])
        _att_set_runs(ep[21], [
            ("13. to (hour/day/month/year): ", False),
            (period_to, True),
        ])

    if len(ep) > 30:
        _att_set_checkbox(ep[22],14,activity_no==14,"was on sick leave;")
        _att_set_checkbox(ep[23],15,activity_no==15,"was on annual leave;")
        _att_set_checkbox(ep[24],16,activity_no==16,"was on leave or rest;")
        _att_set_checkbox(
            ep[25],17,activity_no==17,
            "drove a vehicle exempted from the scope of paragraphs 1 and 2 of item 3 of section I of the"
        )
        # ep[26] — офіційне продовження п.17.
        _att_set_checkbox(ep[27],18,activity_no==18,"performed other work than driving;")
        _att_set_checkbox(ep[28],19,activity_no==19,"was available;")
        _att_set_runs(ep[29], [
            ("20. Place ", False),
            (director_place_en, True),
            ("    Date ", False),
            (form_date_fmt, True),
        ])
        _att_set_text(ep[30], "Signature ______________________________")

    # Окремі поля місця і дати для ВОДІЯ розташовані нижче основної таблиці.
    # Використовуємо ті самі місце та дату бланка, які вводяться користувачем.
    # Підпис водія не заповнюємо.
    for p in doc.paragraphs:
        t=(p.text or "").strip()
        if t.startswith("Місце ") and "Дата" in t:
            _att_set_runs(p, [
                ("Місце ", False),
                (director_place, True),
                ("    Дата ", False),
                (form_date_fmt, True),
            ])
        elif t.startswith("Place ") and "Date" in t:
            _att_set_runs(p, [
                ("Place ", False),
                (director_place_en, True),
                ("    Date ", False),
                (form_date_fmt, True),
            ])

    doc.save(str(out_path))


def _attestation_render_context(driver, period_from, period_to, activity_no, place, form_date):
    """Готує єдиний набір даних для PDF/JPG без залежності від Word."""
    con=db()
    company=con.execute("SELECT * FROM company WHERE id=1").fetchone()
    con.close()
    keys=set(driver.keys()) if hasattr(driver,"keys") else set()
    def dg(name):
        return (driver[name] or "").strip() if name in keys and driver[name] is not None else ""
    ckeys=set(company.keys()) if company is not None and hasattr(company,"keys") else set()
    def cg(name):
        return (company[name] or "").strip() if company is not None and name in ckeys and company[name] is not None else ""

    driver_last=dg("last_name")
    driver_first=dg("first_name")
    driver_middle=dg("middle_name")
    driver_full=" ".join(x for x in (driver_last,driver_first,driver_middle) if x)
    driver_full_en=" ".join(x for x in (
        dg("last_name_en") or driver_last,
        dg("first_name_en") or driver_first,
        dg("middle_name_en") or driver_middle,
    ) if x)
    series=dg("license_series")
    number=dg("license_number")
    director_place=(place or "").strip()
    return {
        "company_name": cg("name"),
        "company_address": cg("address"),
        "phone": cg("phone"),
        "fax": cg("fax"),
        "email": cg("email"),
        "signer_name": cg("signer_name"),
        "signer_position": cg("signer_position"),
        "company_name_en": cg("name_en") or cg("name"),
        "company_address_en": cg("address_en") or cg("address"),
        "signer_name_en": cg("signer_name_en") or cg("signer_name"),
        "signer_position_en": cg("signer_position_en") or cg("signer_position"),
        "director_place": director_place,
        "director_place_en": cg("place_en") or director_place,
        "driver_full": driver_full,
        "driver_full_en": driver_full_en,
        "birth_date": fmt_date(dg("birth_date")),
        "employment": fmt_date(dg("employment_date")),
        "license_series": series,
        "license_number": number,
        "license_number_en": " ".join(x for x in (series,number) if x),
        "license_issue_date": fmt_date(dg("license_issue_date")),
        "period_from": period_from,
        "period_to": period_to,
        "activity_no": int(activity_no),
        "form_date": fmt_date(form_date),
    }


def _generate_attestation_files(driver, period_from, period_to, activity_no, place, form_date, paths, formats):
    """Генерує вибрані формати одного Бланка та повертає фактичні шляхи.

    v8.64: DOCX і PDF/JPG формуються паралельно з одних даних. PDF більше НЕ
    конвертується через Microsoft Word або LibreOffice. Статичний макет PDF —
    точний двосторінковий знімок нашого офіційного DOCX-шаблона, а Taxo накладає
    лише змінні поля. JPG створюється з цього PDF. Тому PDF/JPG працюють навіть
    на комп'ютері, де взагалі немає програми для DOCX.
    """
    formats=tuple(dict.fromkeys(str(x).lower() for x in formats))
    unknown=set(formats)-{"docx","pdf","jpg"}
    if unknown:
        raise ValueError(f"Невідомий формат Бланка: {', '.join(sorted(unknown))}")
    created={"file_path":"","pdf_path":"","jpg_page1_path":"","jpg_page2_path":""}

    # DOCX — окремий формат. Для його створення Word не потрібен.
    if "docx" in formats:
        fill_attestation(driver,period_from,period_to,int(activity_no),place,form_date,paths["docx"])
        created["file_path"]=str(paths["docx"])

    need_visual=("pdf" in formats or "jpg" in formats)
    if not need_visual:
        return created
    if build_attestation_pdf is None:
        raise RuntimeError("Не завантажено автономний модуль формування PDF/JPG.")
    if not ATT_VISUAL_TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Не знайдено візуальний шаблон Бланка: {ATT_VISUAL_TEMPLATE_PATH}")

    context=_attestation_render_context(
        driver,period_from,period_to,int(activity_no),place,form_date
    )
    temporary_pdf=False
    pdf_source=paths["pdf"]
    try:
        if "pdf" not in formats and "jpg" in formats:
            pdf_source=paths["pdf"].with_name(paths["pdf"].stem+"_jpg_source.pdf")
            temporary_pdf=True

        build_attestation_pdf(context,pdf_source,ATT_VISUAL_TEMPLATE_PATH)
        if "pdf" in formats:
            created["pdf_path"]=str(paths["pdf"])

        if "jpg" in formats:
            if pdf_to_jpg_pages is None:
                raise RuntimeError("Не завантажено модуль формування JPG. Перевстановіть залежності Taxo.")
            pdf_to_jpg_pages(pdf_source,paths["jpg1"],paths["jpg2"])
            created["jpg_page1_path"]=str(paths["jpg1"])
            created["jpg_page2_path"]=str(paths["jpg2"])
    finally:
        if temporary_pdf:
            try:
                pdf_source.unlink()
            except OSError:
                pass
    return created


def _month_export_items(year, month, rows):
    """Повертає кожний календарний день місяця.
    Якщо запису worklog немає, день однаково потрапляє у звіт.
    """
    existing = {r["work_date"]: r for r in rows}
    return [(d, existing.get(d.isoformat())) for d in month_dates(year, month)]


def _default_export_day_type(d):
    # Не вигадуємо роботу, якщо запису немає.
    return "Вихідний" if d.weekday() >= 5 else ""


def _safe_num(row, key):
    if row is None:
        return 0.0
    try:
        return float(row[key] or 0)
    except Exception:
        return 0.0


def _row_segments(con, row):
    if row is None:
        return []
    return con.execute(
        "SELECT * FROM work_segments WHERE worklog_id=? ORDER BY segment_no",
        (row["id"],)
    ).fetchall()


def _export_row_values(con, d, r):
    segs = _row_segments(con, r)
    schedule = segments_summary(segs) if segs else (
        f"{r['start_time']}-{r['end_time']}" if r is not None and r["start_time"] else ""
    )
    return {
        "date": d.strftime("%d.%m.%Y"),
        "weekday": ["Пн","Вт","Ср","Чт","Пт","Сб","Нд"][d.weekday()],
        "day_type": r["day_type"] if r is not None else _default_export_day_type(d),
        "schedule": schedule,
        "breaks": gaps_summary(segs),
        "work": _safe_num(r, "work_hours"),
        "drive": _safe_num(r, "driving_hours"),
        "over": _safe_num(r, "overtime_hours"),
        "route": (r["route_name"] if r is not None and "route_name" in r.keys() else "") or "",
        "vehicle": (r["vehicle"] if r is not None else "") or "",
        "notes": (r["notes"] if r is not None else "") or "",
    }


def export_xlsx(driver, year, month, rows, out_path):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    wb = Workbook()
    ws = wb.active
    ws.title = f"{year}-{month:02d}"
    headers = ["Дата", "День", "Вид діяльності", "Графік", "Перерви",
               "Робота, год", "Керування, год", "Надурочні, год",
               "Маршрут", "Автомобіль", "Примітка"]
    ws.append([f"Табель робочого часу — {driver['last_name']} {driver['first_name']} — {month:02d}.{year}"])
    ws.append(headers)
    for c in ws[1]:
        c.font = Font(bold=True, size=14)
    for c in ws[2]:
        c.font = Font(bold=True)

    con = db()
    total_work = total_drive = total_over = 0.0
    work_days = 0
    for d, r in _month_export_items(year, month, rows):
        v = _export_row_values(con, d, r)
        if v["work"] > 0:
            work_days += 1
        total_work += v["work"]
        total_drive += v["drive"]
        total_over += v["over"]
        ws.append([
            v["date"], v["weekday"], v["day_type"], v["schedule"], v["breaks"],
            v["work"], v["drive"], v["over"], v["route"], v["vehicle"], v["notes"]
        ])
    con.close()

    ws.append([])
    ws.append(["ПІДСУМОК", "", f"Робочих днів: {work_days}", "", "",
               round(total_work,2), round(total_drive,2), round(total_over,2), "", "", ""])
    for c in ws[ws.max_row]:
        c.font = Font(bold=True)

    ws.freeze_panes = "A3"
    widths = {"A":13,"B":8,"C":19,"D":30,"E":18,"F":12,"G":14,"H":14,"I":34,"J":26,"K":34}
    for col,w in widths.items():
        ws.column_dimensions[col].width=w
    for row in ws.iter_rows():
        for c in row:
            c.alignment = Alignment(vertical="top", wrap_text=True)
    wb.save(out_path)


def export_pdf(driver, year, month, rows, out_path):
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from xml.sax.saxutils import escape

    candidates = [r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\calibri.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    font_path = next((p for p in candidates if os.path.exists(p)), None)
    font_name = "Helvetica"
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont("AppFont", font_path))
            font_name = "AppFont"
        except Exception:
            pass

    styles = getSampleStyleSheet()
    styles["Normal"].fontName = font_name
    styles["Title"].fontName = font_name

    cell_style = ParagraphStyle(
        "CellSmall", parent=styles["Normal"], fontName=font_name,
        fontSize=6.5, leading=7.7, alignment=TA_LEFT,
        spaceAfter=0, spaceBefore=0
    )
    cell_center = ParagraphStyle(
        "CellCenter", parent=cell_style, alignment=TA_CENTER
    )
    head_style = ParagraphStyle(
        "HeadSmall", parent=cell_style, fontName=font_name,
        fontSize=6.5, leading=7.5, alignment=TA_CENTER
    )
    total_style = ParagraphStyle(
        "TotalSmall", parent=cell_style, fontName=font_name,
        fontSize=6.7, leading=8
    )

    def P(value, style=cell_style):
        s = escape("" if value is None else str(value)).replace("\n", "<br/>")
        return Paragraph(s, style)

    doc = SimpleDocTemplate(
        str(out_path), pagesize=landscape(A4),
        leftMargin=14, rightMargin=14, topMargin=14, bottomMargin=14
    )
    story = [
        Paragraph(f"Табель робочого часу — {driver['last_name']} {driver['first_name']}", styles["Title"]),
        Paragraph(f"Місяць: {month:02d}.{year}", styles["Normal"]),
        Spacer(1, 7)
    ]

    headers = ["Дата","Вид","Графік","Перерви","Робота","Кер.","Надуроч.","Маршрут","Авто","Примітка"]
    data = [[P(x, head_style) for x in headers]]

    con = db()
    total_work = total_drive = total_over = 0.0
    work_days = 0

    for d, r in _month_export_items(year, month, rows):
        v = _export_row_values(con, d, r)
        total_work += v["work"]
        total_drive += v["drive"]
        total_over += v["over"]
        if v["work"] > 0:
            work_days += 1

        data.append([
            P(v["date"], cell_center),
            P(v["day_type"]),
            P(v["schedule"]),
            P(v["breaks"]),
            P(format_hours(v["work"]), cell_center),
            P(format_hours(v["drive"]), cell_center),
            P(format_hours(v["over"]), cell_center),
            P(v["route"]),
            P(v["vehicle"]),
            P(v["notes"]),
        ])

    con.close()

    data.append([
        P("ПІДСУМОК", total_style),
        P(f"Робочих днів: {work_days}", total_style),
        P(""), P(""),
        P(format_hours(total_work), cell_center),
        P(format_hours(total_drive), cell_center),
        P(format_hours(total_over), cell_center),
        P(""), P(""), P("")
    ])

    # Ширини підібрані під landscape A4. Paragraph-и примусово переносять
    # довгі назви маршруту/автомобіля, тому вони більше не накладаються.
    col_widths = [52, 67, 106, 58, 44, 44, 52, 120, 96, 132]
    tbl = Table(data, repeatRows=1, colWidths=col_widths, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("FONTNAME",(0,0),(-1,-1),font_name),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("BACKGROUND",(0,-1),(-1,-1),colors.whitesmoke),
        ("GRID",(0,0),(-1,-1),0.35,colors.grey),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),3),
        ("RIGHTPADDING",(0,0),(-1,-1),3),
        ("TOPPADDING",(0,0),(-1,-1),3),
        ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ]))
    story.append(tbl)
    doc.build(story)


def build_work_analysis_report_items(data):
    """Структурований звіт аналізу.

    kind:
      title/heading/subheading/normal/note/info/warn/error/ok
    """
    items=[]

    profile=data.get("transport_profile",DEFAULT_TRANSPORT_PROFILE)
    items.append(("heading","ПРОФІЛЬ ПЕРЕВЕЗЕНЬ"))
    if profile==DEFAULT_TRANSPORT_PROFILE:
        items.append(("ok",f"• {profile} — поточний основний профіль аналізу."))
    else:
        items.append(("warn",f"• {profile}."))
        items.append((
            "warn",
            "Для цього профілю поки застосовуються базові перевірки №340. "
            "Спеціальні винятки та додаткові правила цього виду перевезень "
            "ще не підключені до автоматичного висновку."
        ))

    items.append(("heading","ПОТРЕБУЄ УВАГИ"))
    if data["warnings"]:
        for x in data["warnings"]:
            items.append(("error","• "+x))
    else:
        items.append(("ok","• За перевіреними автоматично показниками перевищень не знайдено."))

    items.append(("heading","ПЕРЕРВИ У КЕРУВАННІ — ЗА НАШИМИ ЧАСТИНАМИ ЗМІНИ"))
    items.append((
        "note",
        "Наші «частини зміни» — технічне розбиття дня для точного обліку поля «Кер.» "
        "і проміжків між частинами. Це НЕ є автоматично «розділеним щоденним відпочинком» "
        "у термінах Положення №340."
    ))
    if data["driving_break_days"]:
        for day in data["driving_break_days"]:
            items.append((
                "subheading",
                f"{day['date'].strftime('%d.%m.%Y')}: всього керування "
                f"{minutes_hhmm(day['total_drive'])}; максимальне накопичення без завершеної "
                f"перерви {minutes_hhmm(day['max_continuous_drive'])}."
            ))
            for b in day["breaks"]:
                status=(b["status"] or "").lower()
                if b.get("resets"):
                    kind="ok"
                elif "15+30 виконана" in status or "повна перерва" in status:
                    kind="ok"
                elif "перша частина" in status or "ще одна перерва" in status:
                    kind="warn"
                elif "<15" in status:
                    kind="note"
                else:
                    kind="info"
                items.append((
                    kind,
                    f"    {b['after']} → {b['before']}: {minutes_hhmm(b['minutes'])} — {b['status']}."
                ))

    items.append(("heading","ЩОДЕННИЙ / МІЖЗМІННИЙ ВІДПОЧИНОК"))
    if data["daily_rests"]:
        for ev in data["daily_rests"]:
            d=ev["next_date"].strftime("%d.%m.%Y")
            if ev["kind"]=="daily_regular":
                kind="ok"; label="звичайний"
            elif ev["kind"]=="daily_reduced":
                kind="warn"; label="скорочений"
            else:
                kind="error"; label="недостатній"
            items.append((kind,f"• Перед {d}: {minutes_hhmm(ev['minutes'])} — {label}."))
    else:
        items.append(("note","• Немає міжзмінних інтервалів для показу."))

    items.append(("heading","ЩОТИЖНЕВИЙ ВІДПОЧИНОК"))
    if data["weekly_rests"]:
        for ev in data["weekly_rests"]:
            if ev["kind"]=="weekly_regular":
                kind="ok"; label="звичайний (≥45:00)"
            else:
                kind="warn"; label="скорочений (24:00–44:59)"
            items.append((
                kind,
                f"• {ev['start'].strftime('%d.%m %H:%M')} → {ev['end'].strftime('%d.%m %H:%M')}: "
                f"{minutes_hhmm(ev['minutes'])} — {label}."
            ))
    else:
        items.append(("warn","• За вибраний період не знайдено безперервного відпочинку ≥24:00."))

    if data["info"]:
        items.append(("heading","ІНФОРМАЦІЙНІ ПОЗНАЧКИ"))
        for x in data["info"]:
            items.append(("warn","• "+x))

    items.append(("heading","ЩО ПЕРЕВІРЯЄТЬСЯ АВТОМАТИЧНО"))
    checks=[
        "• щоденне керування 9:00; до 10:00 — не більше двох разів на тиждень;",
        "• тижневе керування до 56:00; два послідовні тижні — до 90:00;",
        "• робочий час до 60:00 на окремому тижні та середньо до 48:00/тиждень за 4 календарні місяці;",
        "• нічна робота — контроль 10:00 робочого часу;",
        "• безперервний робочий відрізок понад 6:00;",
        "• час КЕРУВАННЯ між перервами: після накопичення 4:30 потрібна перерва 45 хв "
        "або послідовність щонайменше 15 хв + щонайменше 30 хв;",
        "• міжзмінний відпочинок: звичайний ≥11:00, скорочений 9:00–10:59;",
        "• не більше трьох скорочених щоденних відпочинків між щотижневими;",
        "• щотижневий відпочинок: звичайний ≥45:00, скорочений ≥24:00;",
        "• початок наступного щотижневого відпочинку не пізніше шести послідовних 24-годинних періодів.",
    ]
    items.extend(("normal",x) for x in checks)

    items.append((
        "note",
        "ВАЖЛИВО: внутрішні проміжки між нашими частинами зміни використовуються для "
        "контролю ПЕРЕРВ У КЕРУВАННІ, а не для автоматичного формування щоденного відпочинку 3+9. "
        "Компенсація скороченого щотижневого відпочинку поки показується як строк/нестача, "
        "але автоматично не підтверджується."
    ))
    items.append((
        "note",
        "Це попередній автоматичний контроль за даними табеля, а не юридичний висновок. "
        "Правила налаштовано за Положенням №340 у редакції, чинній з 26.07.2026."
    ))
    return items


def export_work_analysis_pdf(data, driver_name, out_path):
    """Кольоровий PDF звіту «Підсумки / контроль»."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
    from xml.sax.saxutils import escape

    candidates=[
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    font_path=next((p for p in candidates if os.path.exists(p)),None)
    font_name="Helvetica"
    if font_path:
        try:
            # У межах одного процесу шрифт може бути вже зареєстрований.
            if "AnalysisFont" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("AnalysisFont",font_path))
            font_name="AnalysisFont"
        except Exception:
            pass

    styles=getSampleStyleSheet()
    base=ParagraphStyle(
        "AnalysisBase",parent=styles["Normal"],fontName=font_name,
        fontSize=9,leading=12,spaceAfter=3,alignment=TA_LEFT
    )
    title_style=ParagraphStyle(
        "AnalysisTitle",parent=base,fontSize=15,leading=18,spaceAfter=7
    )
    summary_style=ParagraphStyle(
        "AnalysisSummary",parent=base,fontSize=9.5,leading=13
    )
    heading_style=ParagraphStyle(
        "AnalysisHeading",parent=base,fontSize=10.5,leading=13,
        textColor=colors.HexColor("#1F4E79"),spaceBefore=7,spaceAfter=4
    )

    palette={
        "error":("#FDE8E8","#8A1C1C"),
        "warn":("#FFF4CC","#7A4A00"),
        "ok":("#E6F4EA","#1B5E20"),
        "info":("#EAF2FF","#174EA6"),
        "note":("#F3F4F6","#555555"),
        "normal":("#FFFFFF","#222222"),
        "subheading":("#EEF3F8","#243B53"),
    }

    doc=SimpleDocTemplate(
        str(out_path),pagesize=A4,
        leftMargin=28,rightMargin=28,topMargin=26,bottomMargin=26,
        title=f"Підсумки та контроль №340 - {driver_name} - {data['month']:02d}.{data['year']}"
    )
    story=[
        Paragraph("Підсумки та контроль №340",title_style),
        Paragraph(escape(driver_name),summary_style),
        Paragraph(
            f"Профіль перевезень: {escape(data.get('transport_profile', DEFAULT_TRANSPORT_PROFILE))}",
            summary_style
        ),
        Paragraph(
            f"Період: {data['month']:02d}.{data['year']} &nbsp;&nbsp; "
            f"Робочих днів: {data['work_days']} &nbsp;&nbsp; "
            f"Робота: {escape(minutes_dual(data['total_work_min']))} &nbsp;&nbsp; "
            f"Керування: {escape(minutes_dual(data['total_drive_min']))} &nbsp;&nbsp; "
            f"Надурочні: {escape(minutes_dual(data['total_over_min']))}",
            summary_style
        ),
        Paragraph(
            f"Середнє за 4 міс.: {escape(minutes_hhmm(data['avg4_min']))}/тиж. "
            "Усі нормативні порівняння виконуються в цілих хвилинах.",
            summary_style
        ),
        Spacer(1,5),
    ]

    for kind,content in build_work_analysis_report_items(data):
        if kind=="heading":
            story.append(Paragraph(escape(content),heading_style))
            continue

        bg,fg=palette.get(kind,palette["normal"])
        style=ParagraphStyle(
            f"Analysis_{kind}_{len(story)}",
            parent=base,
            textColor=colors.HexColor(fg),
            fontSize=9.2 if kind in ("error","warn","ok","info") else 9,
            leading=12,
        )
        p=Paragraph(escape(content).replace("\n","<br/>"),style)
        if kind=="normal":
            story.append(p)
        else:
            box=Table([[p]],colWidths=[A4[0]-56])
            box.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),colors.HexColor(bg)),
                ("BOX",(0,0),(-1,-1),0.35,colors.HexColor("#D0D5DD")),
                ("LEFTPADDING",(0,0),(-1,-1),6),
                ("RIGHTPADDING",(0,0),(-1,-1),6),
                ("TOPPADDING",(0,0),(-1,-1),4),
                ("BOTTOMPADDING",(0,0),(-1,-1),4),
            ]))
            story.append(box)
            story.append(Spacer(1,2))

    doc.build(story)



SHIFT_DAY_CODES = {
    "Вихідний": "В",
    "Відпустка": "Відп",
    "Лікарняний": "Лік",
    "Відпочинок": "Відпч",
    "Доступний": "Гот",
    "Інша робота": "Інш",
    "Інше": "Інш",
}


def _monthly_shift_cell(row, segments):
    """Короткий напис для клітинки місячного графіка."""
    if row is None:
        return ""
    day_type=(row["day_type"] or "").strip()
    if day_type != "Робота":
        return SHIFT_DAY_CODES.get(day_type, day_type[:4])

    if segments:
        ordered=sorted(segments,key=lambda s:(s["segment_no"],time_to_minutes(s["start_time"])))
        start=ordered[0]["start_time"]
        end=ordered[-1]["end_time"]
        parts=len(ordered)
    else:
        start=(row["start_time"] or "").strip()
        end=(row["end_time"] or "").strip()
        parts=1 if start and end else 0

    if not start and not end:
        return "Р"
    if parts>1:
        return f"{start}\n{end}\n{parts}ч"
    return f"{start}\n{end}"




def parse_attestation_period(value):
    """Розбирає дату/час періоду бланка у відомих форматах."""
    raw=(value or "").strip()
    if not raw:
        return None
    for fmt in (
        "%H:%M %d.%m.%Y",
        "%d.%m.%Y %H:%M",
        "%Y-%m-%d %H:%M",
        "%d.%m.%Y",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(raw,fmt)
        except ValueError:
            pass
    return None


def format_attestation_period(value):
    return value.strftime("%H:%M %d.%m.%Y")


def _attestation_is_active(row):
    if row is None:
        return False
    try:
        value=row["status"]
    except Exception:
        value="active"
    return (value or "active").strip().lower()=="active"


def _audit_attestation_snapshot(con, row, action, note="", file_path_override=None):
    """Фіксує стан бланка в журналі змін. Працює і зі старими sqlite.Row."""
    if row is None:
        return
    keys=set(row.keys()) if hasattr(row,"keys") else set()
    def g(name, default=""):
        return row[name] if name in keys and row[name] is not None else default
    con.execute(
        """INSERT INTO attestation_audit(
            attestation_id,action,revision,period_from,period_to,activity_no,
            place,form_date,file_path,pdf_path,jpg_page1_path,jpg_page2_path,
            status,note,created_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            g("id",0),action,int(g("revision",1) or 1),g("period_from"),g("period_to"),
            int(g("activity_no",16) or 16),g("place"),g("form_date"),
            file_path_override if file_path_override is not None else g("file_path"),
            g("pdf_path"),g("jpg_page1_path"),g("jpg_page2_path"),
            g("status","active") or "active",note,datetime.now().isoformat(timespec="seconds")
        )
    )


def _ensure_attestation_audit_baseline(con, row):
    if row is None:
        return
    exists=con.execute(
        "SELECT 1 FROM attestation_audit WHERE attestation_id=? LIMIT 1",
        (row["id"],)
    ).fetchone()
    if not exists:
        _audit_attestation_snapshot(con,row,"BASELINE","Стан до першої зміни у v8.57")


def _safe_archive_file(path_text, target_dir, label):
    """Переміщує файл Бланка у контрольний архів без перезапису."""
    raw=(path_text or "").strip()
    if not raw:
        return raw
    src=Path(raw)
    if not src.exists() or not src.is_file():
        return raw
    target_dir.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
    stem=src.stem
    suffix=src.suffix or ".dat"
    target=target_dir/f"{stem}_{label}_{stamp}{suffix}"
    n=2
    while target.exists():
        target=target_dir/f"{stem}_{label}_{stamp}_{n}{suffix}"
        n+=1
    shutil.move(str(src),str(target))
    return str(target)


def _unique_attestation_output_paths(driver, st, en, activity_no):
    """Повертає один узгоджений набір імен DOCX/PDF/JPG для ревізії Бланка."""
    safe=f"{driver['last_name']}_{driver['first_name']}".replace(" ","_")
    stamp_from=st.strftime("%Y%m%d_%H%M")
    stamp_to=en.strftime("%Y%m%d_%H%M")
    stem=f"Підтвердження_{safe}_{stamp_from}-{stamp_to}_п{int(activity_no)}"
    candidate=OUTPUT_DIR/stem
    n=1
    while any((OUTPUT_DIR/f"{candidate.name}{ext}").exists() for ext in (".docx",".pdf","_page1.jpg","_page2.jpg")):
        n+=1
        candidate=OUTPUT_DIR/f"{stem}_v{n}"
    return {
        "docx": OUTPUT_DIR/f"{candidate.name}.docx",
        "pdf": OUTPUT_DIR/f"{candidate.name}.pdf",
        "jpg1": OUTPUT_DIR/f"{candidate.name}_page1.jpg",
        "jpg2": OUTPUT_DIR/f"{candidate.name}_page2.jpg",
    }


def _unique_attestation_output_path(driver, st, en, activity_no):
    # Сумісність зі старим кодом/тестами: основний шлях лишається DOCX.
    return _unique_attestation_output_paths(driver,st,en,activity_no)["docx"]


def _archive_attestation_files(row, target_dir, label):
    """Архівує всі наявні формати одного Бланка та повертає нові шляхи."""
    keys=set(row.keys()) if hasattr(row,"keys") else set()
    result={}
    for field in ("file_path","pdf_path","jpg_page1_path","jpg_page2_path"):
        raw=row[field] if field in keys and row[field] is not None else ""
        result[field]=_safe_archive_file(raw,target_dir,label) if raw else ""
    return result


def _attestation_existing_formats(row):
    keys=set(row.keys()) if hasattr(row,"keys") else set()
    out=[]
    if "file_path" in keys and (row["file_path"] or "").strip():
        out.append("docx")
    if "pdf_path" in keys and (row["pdf_path"] or "").strip():
        out.append("pdf")
    if (("jpg_page1_path" in keys and (row["jpg_page1_path"] or "").strip()) or
        ("jpg_page2_path" in keys and (row["jpg_page2_path"] or "").strip())):
        out.append("jpg")
    return tuple(out) or ("docx",)


def _restore_attestation_files(row):
    """Повертає всі архівовані файли Бланка в Output, не перезаписуючи наявні."""
    keys=set(row.keys()) if hasattr(row,"keys") else set()
    result={}
    for field in ("file_path","pdf_path","jpg_page1_path","jpg_page2_path"):
        raw=row[field] if field in keys and row[field] is not None else ""
        raw=(raw or "").strip()
        if not raw:
            result[field]=""
            continue
        src=Path(raw)
        if not src.exists() or not src.is_file() or src.parent.resolve()==OUTPUT_DIR.resolve():
            result[field]=raw
            continue
        target=OUTPUT_DIR/src.name
        n=2
        while target.exists():
            target=OUTPUT_DIR/f"{src.stem}_restored_{n}{src.suffix}"
            n+=1
        shutil.move(str(src),str(target))
        result[field]=str(target)
    return result


def _merge_dt_intervals(intervals):
    cleaned=sorted(
        [(a,b) for a,b in intervals if a is not None and b is not None and b>a],
        key=lambda x:x[0]
    )
    if not cleaned:
        return []
    out=[list(cleaned[0])]
    for a,b in cleaned[1:]:
        if a <= out[-1][1]:
            if b > out[-1][1]:
                out[-1][1]=b
        else:
            out.append([a,b])
    return [(a,b) for a,b in out]


def _subtract_dt_intervals(base_start, base_end, covered):
    """Повертає частини base, які не перекриті covered."""
    pieces=[(base_start,base_end)]
    for ca,cb in _merge_dt_intervals(covered):
        new=[]
        for a,b in pieces:
            if cb<=a or ca>=b:
                new.append((a,b))
                continue
            if ca>a:
                new.append((a,min(ca,b)))
            if cb<b:
                new.append((max(cb,a),b))
        pieces=[x for x in new if x[1]>x[0]]
        if not pieces:
            break
    return pieces


def _worklog_route_intervals(row, segments):
    """Інтервали, які в режимі ТАХО закриваються маршрутом/тахокартою."""
    work_day=datetime.strptime(row["work_date"],"%Y-%m-%d").date()
    out=[]
    source=segments
    if not source and (row["start_time"] or "").strip() and (row["end_time"] or "").strip():
        source=[row]
    for s in source:
        try:
            sm=time_to_minutes(s["start_time"])
            em=time_to_minutes(s["end_time"])
        except Exception:
            continue
        start=datetime.combine(work_day,datetime.min.time())+timedelta(minutes=sm)
        end=datetime.combine(work_day,datetime.min.time())+timedelta(minutes=em)
        if em<=sm:
            end += timedelta(days=1)
        if end>start:
            out.append((start,end))
    return out


def _attestation_activity_for_calendar_day(row):
    """Автоматична позиція 14–19 для календарного дня без ТАХО.

    Це внутрішня політика підприємства для автоматичного формування бланків.
    Користувач завжди може вручну змінити запропоновану позицію перед друком.
    """
    if row is None:
        return 16

    mode=(row["accounting_mode"] if "accounting_mode" in row.keys() else WORK_MODE_MANUAL) or WORK_MODE_MANUAL
    day_type=(row["day_type"] or "").strip()

    if mode==WORK_MODE_NO_TACHO:
        return 18

    if day_type=="Лікарняний":
        return 14
    if day_type=="Відпустка":
        return 15
    if day_type in ("Вихідний","Відпочинок"):
        return 16
    if day_type in ("Інша робота","Робота","Інше"):
        return 18
    if day_type=="Доступний":
        return 19

    return 16


def _build_attestation_required_segments(prev_block, next_block, row_by_day):
    """Будує лише ті частини між двома ТАХО-днями, які треба закрити бланком.

    Правило v8.54:
    - між двома послідовними календарними ТАХО-днями бланк не потрібен;
      міжзмінний відпочинок видно з двох добових тахокарт;
    - якщо між ТАХО-днями є хоча б один інший календарний день, бланк
      починається від завершення попереднього ТАХО-блоку і закінчується
      початком наступного;
    - усередині такого проміжку код визначається за видом календарного дня;
      однакові сусідні коди об'єднуються в один бланк.
    """
    prev_day=prev_block["work_date"]
    next_day=next_block["work_date"]
    if next_day <= prev_day + timedelta(days=1):
        return []

    ga=prev_block["end"]
    gb=next_block["start"]
    if gb<=ga:
        return []

    pieces=[]
    cursor=ga
    while cursor < gb:
        day=cursor.date()
        midnight=datetime.combine(day+timedelta(days=1),datetime.min.time())
        piece_end=min(midnight,gb)

        # Після завершення ТАХО в його календарний день і перед початком
        # наступного ТАХО в його календарний день це відпочинок (позиція 16).
        if day==prev_day or day==next_day:
            activity_no=16
        else:
            activity_no=_attestation_activity_for_calendar_day(row_by_day.get(day))

        if pieces and pieces[-1][2]==activity_no and pieces[-1][1]==cursor:
            pieces[-1]=(pieces[-1][0],piece_end,activity_no)
        else:
            pieces.append((cursor,piece_end,activity_no))
        cursor=piece_end

    return [(a,b,n) for a,b,n in pieces if b>a]


def collect_attestation_gap_control(driver_id, control_date=None, previous_days=56):
    """Контроль Бланків підтвердження за внутрішнім правилом v8.57.

    Ключові правила:
    - усі частини одного маршрутного ТАХО-дня = один ТАХО-блок від першого
      виїзду до останнього повернення;
    - якщо наступний ТАХО-день є наступним календарним днем, міжзмінний
      відпочинок окремим бланком НЕ закриваємо;
    - якщо між двома ТАХО-днями є один або більше інших календарних днів,
      проміжок від кінця попереднього ТАХО до початку наступного закриваємо
      бланком(ами);
    - крім історичних «аварійних» пропусків, контроль показує ПОТОЧНИЙ
      період відпочинку до найближчого наступного виїзду, якщо цей виїзд уже
      є у графіку. Такий бланк можна підготувати ДО виїзду;
    - автоматичні позиції: лікарняний=14, відпустка=15,
      вихідний/відпочинок=16, «Без тахо — 8 год»/інша робота=18,
      доступний=19;
    - сусідні частини з однаковою позицією об'єднуються;
    - 56 днів — лише вікно контролю минулих записів. Для поточного періоду
      додатково дивимось уперед у графік, щоб знайти найближчий виїзд.
    """
    if isinstance(control_date,str):
        try:
            control_date=datetime.strptime(control_date,"%d.%m.%Y").date()
        except ValueError:
            control_date=datetime.strptime(control_date,"%Y-%m-%d").date()
    if control_date is None:
        control_date=date.today()

    start_day=control_date-timedelta(days=int(previous_days))
    end_day=control_date
    range_start=datetime.combine(start_day,datetime.min.time())
    range_end=datetime.combine(end_day+timedelta(days=1),datetime.min.time())

    # Для сьогоднішнього контролю «поточний» означає фактичний момент зараз.
    # Для довільної контрольної дати беремо кінець вибраного дня — так можна
    # відтворити стан контролю на минулу дату без залежності від годинника ПК.
    if control_date==date.today():
        reference_moment=datetime.now()
    else:
        reference_moment=range_end-timedelta(microseconds=1)

    con=db()

    # Назад потрібен запас для зв'язку першого ТАХО-дня у 56-денному вікні.
    # Уперед дивимось лише для пошуку найближчого запланованого виїзду.
    query_start=start_day-timedelta(days=62)
    query_end=end_day+timedelta(days=62)
    rows=con.execute(
        """SELECT * FROM worklog
           WHERE driver_id=? AND work_date BETWEEN ? AND ?
           ORDER BY work_date""",
        (int(driver_id),query_start.isoformat(),query_end.isoformat())
    ).fetchall()

    seg_by={}
    if rows:
        ids=[r["id"] for r in rows]
        q=",".join("?" for _ in ids)
        segs=con.execute(
            f"""SELECT * FROM work_segments
                WHERE worklog_id IN ({q})
                ORDER BY worklog_id,segment_no""",
            ids
        ).fetchall()
        for s in segs:
            seg_by.setdefault(s["worklog_id"],[]).append(s)

    att_rows=con.execute(
        """SELECT * FROM attestations
           WHERE driver_id=? AND COALESCE(status,'active')='active'
           ORDER BY id""",
        (int(driver_id),)
    ).fetchall()
    con.close()

    row_by_day={
        datetime.strptime(r["work_date"],"%Y-%m-%d").date():r
        for r in rows
    }

    duty_blocks=[]
    no_tacho_days=[]
    for r in rows:
        mode=(r["accounting_mode"] if "accounting_mode" in r.keys() else WORK_MODE_MANUAL) or WORK_MODE_MANUAL
        d=datetime.strptime(r["work_date"],"%Y-%m-%d").date()

        if mode==WORK_MODE_NO_TACHO and start_day<=d<=end_day:
            no_tacho_days.append(d)

        if mode!=WORK_MODE_TACHO:
            continue

        route_parts=_worklog_route_intervals(r,seg_by.get(r["id"],[]))
        if not route_parts:
            continue

        block_start=min(a for a,b in route_parts)
        block_end=max(b for a,b in route_parts)
        duty_blocks.append({
            "work_date":d,
            "start":block_start,
            "end":block_end,
            "worklog_id":r["id"],
        })

    duty_blocks.sort(key=lambda x:x["start"])

    required_segments=[]
    ignored_consecutive_minutes=0
    current_pair_found=False
    current_departure=None

    for prev,nxt in zip(duty_blocks,duty_blocks[1:]):
        ga=prev["end"]
        gb=nxt["start"]
        if gb<=ga:
            continue

        is_current=(ga <= reference_moment < gb)
        is_historical=(range_start <= gb < range_end)
        if not is_current and not is_historical:
            continue

        segs=_build_attestation_required_segments(prev,nxt,row_by_day)
        if not segs:
            ignored_consecutive_minutes += max(0,int((gb-ga).total_seconds()//60))
            continue

        if is_current:
            current_pair_found=True
            current_departure=gb

        for a,b,n in segs:
            required_segments.append((a,b,n,is_current))

    att_intervals=[]
    invalid_attestations=[]
    for a in att_rows:
        st=parse_attestation_period(a["period_from"])
        en=parse_attestation_period(a["period_to"])
        if not st or not en or en<=st:
            invalid_attestations.append(a["id"])
            continue
        att_intervals.append((st,en,a["id"],a["activity_no"]))

    # Наявний бланк вважаємо свідомим рішенням користувача незалежно від коду.
    # Автоматичний код використовується для НОВИХ бланків і може бути змінений вручну.
    att_merged=_merge_dt_intervals([(a,b) for a,b,_,_ in att_intervals])

    rows_out=[]
    required_minutes=0
    covered_minutes=0
    missing_minutes=0
    current_required_minutes=0
    current_missing_minutes=0

    for ga,gb,suggested_no,is_current in required_segments:
        dur=max(0,int((gb-ga).total_seconds()//60))
        required_minutes += dur
        if is_current:
            current_required_minutes += dur

        missing=_subtract_dt_intervals(ga,gb,att_merged)
        miss=sum(max(0,int((b-a).total_seconds()//60)) for a,b in missing)
        missing_minutes += miss
        covered_minutes += max(0,dur-miss)
        if is_current:
            current_missing_minutes += miss

        if not missing:
            rows_out.append({
                "kind":"covered",
                "status":"ПОТОЧНИЙ — БЛАНК ГОТОВИЙ" if is_current else "ЗАКРИТО БЛАНКОМ",
                "from":ga,
                "to":gb,
                "minutes":dur,
                "activity_no":suggested_no,
                "is_current":is_current,
                "reason":(
                    f"Поточний період до виїзду за графіком уже перекритий бланком. Автокод: {suggested_no}."
                    if is_current else
                    f"Проміжок перекритий наявним бланком. Автокод для цього виду дня: {suggested_no}."
                ),
            })
        else:
            if is_current:
                status="ПОТОЧНИЙ — ПІДГОТУВАТИ"
            else:
                status="НЕМАЄ БЛАНКА" if miss==dur else "ЧАСТКОВО НЕ ЗАКРИТО"
            for ma,mb in missing:
                mdur=max(0,int((mb-ma).total_seconds()//60))
                rows_out.append({
                    "kind":"missing",
                    "status":status,
                    "from":ma,
                    "to":mb,
                    "minutes":mdur,
                    "activity_no":suggested_no,
                    "is_current":is_current,
                    "reason":(
                        f"Поточний період відпочинку/діяльності до наступного виїзду за графіком. "
                        f"Підготувати бланк ДО виїзду. Автопозиція {suggested_no}: {ACTIVITIES[suggested_no]}."
                        if is_current else
                        f"Автоматично запропонована позиція {suggested_no}: {ACTIVITIES[suggested_no]}."
                    ),
                })

    rank={"missing":0,"covered":1}
    rows_out.sort(key=lambda r:(r["from"],0 if r.get("is_current") else 1,rank.get(r["kind"],9),r.get("activity_no",0)))

    tacho_days_in_window={
        b["work_date"] for b in duty_blocks if start_day<=b["work_date"]<=end_day
    }

    return {
        "driver_id":int(driver_id),
        "control_date":control_date,
        "start_day":start_day,
        "end_day":end_day,
        "previous_days":int(previous_days),
        "tacho_days":len(tacho_days_in_window),
        "tacho_blocks":len([
            b for b in duty_blocks if start_day<=b["work_date"]<=end_day
        ]),
        "no_tacho_days":len(set(no_tacho_days)),
        "required_minutes":required_minutes,
        "covered_minutes":covered_minutes,
        "missing_minutes":missing_minutes,
        "current_pair_found":current_pair_found,
        "current_departure":current_departure,
        "current_required_minutes":current_required_minutes,
        "current_missing_minutes":current_missing_minutes,
        "ignored_consecutive_minutes":ignored_consecutive_minutes,
        "invalid_attestations":invalid_attestations,
        "rows":rows_out,
    }



def _work_balance_cell(row, day):
    """Клітинка місячного робочого табеля: тільки години або код дня."""
    if row is None:
        return "В" if day.weekday() >= 5 else ""

    day_type=(row["day_type"] or "").strip()
    if day_type and day_type != "Робота":
        return SHIFT_DAY_CODES.get(day_type, day_type[:4])

    work_min=hours_value_to_minutes(row["work_hours"])
    if work_min <= 0:
        return ""
    return minutes_hhmm(work_min)


def collect_monthly_work_balance(year, month, active_only=True):
    """Місячний робочий табель / баланс часу по всіх водіях."""
    y=int(year); m=int(month)
    days=month_dates(y,m)
    con=db()

    if active_only:
        drivers=con.execute(
            "SELECT * FROM drivers WHERE active=1 ORDER BY last_name,first_name,middle_name"
        ).fetchall()
    else:
        drivers=con.execute(
            "SELECT * FROM drivers ORDER BY active DESC,last_name,first_name,middle_name"
        ).fetchall()

    rows=con.execute(
        """SELECT * FROM worklog
           WHERE work_date BETWEEN ? AND ?
           ORDER BY driver_id,work_date""",
        (days[0].isoformat(),days[-1].isoformat())
    ).fetchall()
    company=con.execute("SELECT * FROM company WHERE id=1").fetchone()
    con.close()

    row_by={(r["driver_id"],r["work_date"]):r for r in rows}
    out=[]
    for dr in drivers:
        cells=[]
        total_work_min=0
        total_over_min=0
        work_days=0
        for d in days:
            r=row_by.get((dr["id"],d.isoformat()))
            cells.append(_work_balance_cell(r,d))
            if r is not None:
                wm=hours_value_to_minutes(r["work_hours"])
                om=hours_value_to_minutes(r["overtime_hours"])
                total_work_min += wm
                total_over_min += om
                if wm > 0:
                    work_days += 1

        out.append({
            "driver_id":dr["id"],
            "name":" ".join(
                x for x in [dr["last_name"],dr["first_name"],dr["middle_name"]] if x
            ).strip(),
            "cells":cells,
            "work_days":work_days,
            "work_min":total_work_min,
            "over_min":total_over_min,
        })

    return {
        "year":y,
        "month":m,
        "days":days,
        "drivers":out,
        "company":company,
    }


def export_monthly_work_balance_pdf(year, month, out_path, active_only=True):
    """Місячний табель робочого часу на A4 landscape.

    У клітинках робочих днів друкуються ТІЛЬКИ години.
    Місяць ділиться на три читабельні частини.
    """
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from xml.sax.saxutils import escape

    data=collect_monthly_work_balance(year,month,active_only=active_only)

    candidates=[
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    font_path=next((p for p in candidates if os.path.exists(p)),None)
    font_name="Helvetica"
    if font_path:
        try:
            if "WorkBalanceFont" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("WorkBalanceFont",font_path))
            font_name="WorkBalanceFont"
        except Exception:
            pass

    doc=SimpleDocTemplate(
        str(out_path),pagesize=landscape(A4),
        leftMargin=14,rightMargin=14,topMargin=14,bottomMargin=14,
        title=f"Табель робочого часу {month_name_ua(data['month'])} {data['year']}"
    )
    styles=getSampleStyleSheet()
    title=ParagraphStyle(
        "BalanceTitle",parent=styles["Title"],fontName=font_name,
        fontSize=14,leading=16,alignment=TA_CENTER,spaceAfter=4
    )
    normal=ParagraphStyle(
        "BalanceNormal",parent=styles["Normal"],fontName=font_name,
        fontSize=8.8,leading=10.2,alignment=TA_LEFT
    )
    center=ParagraphStyle(
        "BalanceCenter",parent=normal,alignment=TA_CENTER,fontSize=9.2,leading=10.5
    )
    head=ParagraphStyle(
        "BalanceHead",parent=center,fontSize=9.1,leading=10.2
    )
    driver_style=ParagraphStyle(
        "BalanceDriver",parent=normal,fontSize=9.2,leading=10.5
    )

    story=[]
    company_name=(data["company"]["name"] if data["company"] else "") or ""
    chunks=_split_month_days_a4(data["days"])

    for page_no,chunk in enumerate(chunks,1):
        if page_no>1:
            story.append(PageBreak())

        if company_name:
            story.append(Paragraph(
                f"<b>{escape(company_name)}</b>",
                ParagraphStyle(
                    f"BalanceCompany{page_no}",parent=normal,
                    fontSize=16.5,leading=19,alignment=TA_CENTER,
                    spaceAfter=2
                )
            ))

        story.append(Paragraph(
            f"ТАБЕЛЬ РОБОЧОГО ЧАСУ — {month_name_ua(data['month']).upper()} "
            f"{data['year']} РОКУ — ДНІ {chunk[0].day}–{chunk[-1].day}",
            title
        ))
        story.append(Spacer(1,4))

        header1=[Paragraph("Водій",head)]
        header2=[Paragraph("",head)]
        for d in chunk:
            header1.append(Paragraph(str(d.day),head))
            header2.append(Paragraph(
                ["Пн","Вт","Ср","Чт","Пт","Сб","Нд"][d.weekday()],head
            ))
        header1 += [
            Paragraph("Роб.<br/>днів",head),
            Paragraph("Відпрацьовано",head),
            Paragraph("Надурочні",head),
        ]
        header2 += [
            Paragraph("",head),
            Paragraph("год:хв",head),
            Paragraph("год:хв",head),
        ]

        rows=[header1,header2]
        day_indexes=[d.day-1 for d in chunk]

        for dr in data["drivers"]:
            row=[Paragraph(escape(dr["name"]),driver_style)]
            for idx in day_indexes:
                row.append(Paragraph(escape(dr["cells"][idx]),center))
            row += [
                Paragraph(str(dr["work_days"]),center),
                Paragraph(minutes_hhmm(dr["work_min"]),center),
                Paragraph(minutes_hhmm(dr["over_min"]),center),
            ]
            rows.append(row)

        day_width=min(52,545/max(1,len(chunk)))
        col_widths=[128]+[day_width]*len(chunk)+[42,68,58]
        table=Table(rows,colWidths=col_widths,repeatRows=2,hAlign="CENTER")
        ts=[
            ("FONTNAME",(0,0),(-1,-1),font_name),
            ("GRID",(0,0),(-1,-1),0.45,colors.HexColor("#666666")),
            ("BACKGROUND",(0,0),(-1,1),colors.HexColor("#D9E6F2")),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("ALIGN",(1,0),(-1,-1),"CENTER"),
            ("LEFTPADDING",(0,0),(-1,-1),2),
            ("RIGHTPADDING",(0,0),(-1,-1),2),
            ("TOPPADDING",(0,0),(-1,-1),4),
            ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ]

        for i,d in enumerate(chunk,start=1):
            if d.weekday()>=5:
                ts.append(("BACKGROUND",(i,0),(i,1),colors.HexColor("#ECECEC")))

        for rr,dr in enumerate(data["drivers"],start=2):
            for cc,idx in enumerate(day_indexes,start=1):
                val=dr["cells"][idx]
                if val=="В":
                    ts.append(("BACKGROUND",(cc,rr),(cc,rr),colors.HexColor("#F2F2F2")))
                elif val in ("Відп","Лік","Відпч","Гот","Інш"):
                    ts.append(("BACKGROUND",(cc,rr),(cc,rr),colors.HexColor("#FFF7D6")))

        table.setStyle(TableStyle(ts))
        story.append(table)
        story.append(Spacer(1,6))
        story.append(Paragraph(
            "У робочій клітинці: тільки фактично відпрацьований час. "
            "В — вихідний; Відп — відпустка; Лік — лікарняний; "
            "Відпч — відпочинок; Гот — готовність; Інш — інша робота.",
            normal
        ))

    doc.build(story)
    return data


def export_monthly_work_balance_xlsx(year, month, out_path, active_only=True):
    """Редагований місячний табель/баланс на A4 landscape."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    data=collect_monthly_work_balance(year,month,active_only=active_only)
    wb=Workbook()
    wb.remove(wb.active)

    thin=Side(style="thin",color="777777")
    border=Border(left=thin,right=thin,top=thin,bottom=thin)
    header_fill=PatternFill("solid",fgColor="D9E6F2")
    weekend_fill=PatternFill("solid",fgColor="F2F2F2")
    nonwork_fill=PatternFill("solid",fgColor="FFF7D6")

    chunks=_split_month_days_a4(data["days"])
    company_name=(data["company"]["name"] if data["company"] else "") or ""

    for chunk in chunks:
        ws=wb.create_sheet(f"{chunk[0].day}-{chunk[-1].day}")
        ncols=1+len(chunk)+3

        ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=ncols)
        ws.cell(1,1,company_name)
        ws.cell(1,1).font=Font(size=16,bold=True)
        ws.cell(1,1).alignment=Alignment(horizontal="center",vertical="center")
        ws.row_dimensions[1].height=24

        ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=ncols)
        ws.cell(
            2,1,
            f"ТАБЕЛЬ РОБОЧОГО ЧАСУ — {month_name_ua(data['month']).upper()} "
            f"{data['year']} РОКУ — ДНІ {chunk[0].day}–{chunk[-1].day}"
        )
        ws.cell(2,1).font=Font(size=14,bold=True)
        ws.cell(2,1).alignment=Alignment(horizontal="center")

        headers=["Водій"]
        for d in chunk:
            headers.append(f"{d.day}\n{['Пн','Вт','Ср','Чт','Пт','Сб','Нд'][d.weekday()]}")
        headers += ["Роб. днів","Відпрацьовано","Надурочні"]

        for c,h in enumerate(headers,1):
            cell=ws.cell(4,c,h)
            cell.font=Font(size=10,bold=True)
            cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
            cell.fill=header_fill
            cell.border=border

        day_indexes=[d.day-1 for d in chunk]
        for r_idx,dr in enumerate(data["drivers"],5):
            c=ws.cell(r_idx,1,dr["name"])
            c.font=Font(size=10,bold=True)
            c.alignment=Alignment(vertical="center",wrap_text=True)
            c.border=border

            for offset,idx in enumerate(day_indexes,2):
                val=dr["cells"][idx]
                c=ws.cell(r_idx,offset,val)
                c.font=Font(size=10)
                c.alignment=Alignment(horizontal="center",vertical="center")
                c.border=border
                if val=="В":
                    c.fill=weekend_fill
                elif val in ("Відп","Лік","Відпч","Гот","Інш"):
                    c.fill=nonwork_fill

            summary_col=2+len(chunk)
            for j,val in enumerate([
                dr["work_days"],
                minutes_hhmm(dr["work_min"]),
                minutes_hhmm(dr["over_min"]),
            ],summary_col):
                c=ws.cell(r_idx,j,val)
                c.font=Font(size=10,bold=True)
                c.alignment=Alignment(horizontal="center",vertical="center")
                c.border=border

            ws.row_dimensions[r_idx].height=28

        ws.column_dimensions["A"].width=25
        for col in range(2,2+len(chunk)):
            ws.column_dimensions[get_column_letter(col)].width=9
        for col in range(2+len(chunk),2+len(chunk)+3):
            ws.column_dimensions[get_column_letter(col)].width=13

        ws.row_dimensions[4].height=30
        ws.freeze_panes="B5"
        ws.sheet_view.showGridLines=False

        ws.page_setup.orientation="landscape"
        ws.page_setup.paperSize=ws.PAPERSIZE_A4
        ws.page_setup.fitToWidth=1
        ws.page_setup.fitToHeight=0
        ws.sheet_properties.pageSetUpPr.fitToPage=True
        ws.print_title_rows="1:4"
        ws.print_options.horizontalCentered=True
        ws.page_margins.left=0.25
        ws.page_margins.right=0.25
        ws.page_margins.top=0.35
        ws.page_margins.bottom=0.35

        last_row=max(5,4+len(data["drivers"]))
        ws.print_area=f"A1:{get_column_letter(ncols)}{last_row}"

    wb.save(str(out_path))
    return data


def collect_monthly_shift_schedule(year, month, active_only=True):
    """Збирає дані графіка змінності для всіх водіїв за місяць."""
    y=int(year); m=int(month)
    days=month_dates(y,m)
    con=db()

    if active_only:
        drivers=con.execute(
            "SELECT * FROM drivers WHERE active=1 ORDER BY last_name,first_name,middle_name"
        ).fetchall()
    else:
        drivers=con.execute(
            "SELECT * FROM drivers ORDER BY active DESC,last_name,first_name,middle_name"
        ).fetchall()

    rows=con.execute(
        """SELECT * FROM worklog
           WHERE work_date BETWEEN ? AND ?
           ORDER BY driver_id,work_date""",
        (days[0].isoformat(),days[-1].isoformat())
    ).fetchall()

    row_by={(r["driver_id"],r["work_date"]):r for r in rows}
    seg_by={}
    if rows:
        ids=[r["id"] for r in rows]
        q=",".join("?" for _ in ids)
        segs=con.execute(
            f"SELECT * FROM work_segments WHERE worklog_id IN ({q}) ORDER BY worklog_id,segment_no",
            ids
        ).fetchall()
        for s in segs:
            seg_by.setdefault(s["worklog_id"],[]).append(s)

    company=con.execute("SELECT * FROM company WHERE id=1").fetchone()
    con.close()

    driver_rows=[]
    details=[]
    for dr in drivers:
        cells=[]
        work_days=0
        work_min=0
        drive_min=0
        for d in days:
            r=row_by.get((dr["id"],d.isoformat()))
            segs=seg_by.get(r["id"],[]) if r else []
            cell=_monthly_shift_cell(r,segs)
            cells.append(cell)

            if r:
                if (r["day_type"] or "")=="Робота":
                    work_days+=1
                if segs:
                    dm_work=sum(hours_value_to_minutes(s["work_hours"]) for s in segs)
                    dm_drive=sum(hours_value_to_minutes(s["driving_hours"]) for s in segs)
                else:
                    dm_work=hours_value_to_minutes(r["work_hours"])
                    dm_drive=hours_value_to_minutes(r["driving_hours"])
                work_min+=dm_work
                drive_min+=dm_drive

                if (r["day_type"] or "")=="Робота":
                    schedule=segments_summary(segs) if segs else (
                        f"{r['start_time']}-{r['end_time']}" if r["start_time"] else ""
                    )
                    details.append({
                        "driver": f"{dr['last_name']} {dr['first_name']} {dr['middle_name']}".strip(),
                        "date": d,
                        "day_type": r["day_type"],
                        "schedule": schedule,
                        "breaks": gaps_summary(segs),
                        "work_min": dm_work,
                        "drive_min": dm_drive,
                        "route": (r["route_name"] if "route_name" in r.keys() else "") or "",
                        "vehicle": (r["vehicle"] if "vehicle" in r.keys() else "") or "",
                        "notes": (r["notes"] if "notes" in r.keys() else "") or "",
                    })

        driver_rows.append({
            "id":dr["id"],
            "name":f"{dr['last_name']} {dr['first_name']} {dr['middle_name']}".strip(),
            "cells":cells,
            "work_days":work_days,
            "work_min":work_min,
            "drive_min":drive_min,
        })

    return {
        "year":y,
        "month":m,
        "days":days,
        "drivers":driver_rows,
        "details":details,
        "company":company,
    }


MONTH_NAMES_UA = [
    "Січень","Лютий","Березень","Квітень","Травень","Червень",
    "Липень","Серпень","Вересень","Жовтень","Листопад","Грудень"
]


def month_name_ua(month):
    try:
        return MONTH_NAMES_UA[int(month)-1]
    except Exception:
        return str(month)


def _monthly_shift_print_cell(cell):
    """Читабельний друк клітинки.

    Час навмисно ставимо у два окремі рядки:
        06:30
        20:00
        3ч
    Так цифри не стискаються і не переносяться посеред часу.
    """
    if not cell:
        return ""
    parts=str(cell).splitlines()
    if len(parts)>=2 and ":" in parts[0] and ":" in parts[1]:
        out=[parts[0],parts[1]]
        if len(parts)>=3 and parts[2]:
            out.append(parts[2])
        return "\n".join(out)
    return str(cell)


def _split_month_days_a4(days):
    """Ділить місяць на 3 читабельні частини для A4 landscape.

    31 день -> 11 + 10 + 10
    30 днів -> 10 + 10 + 10
    29 днів -> 10 + 10 + 9
    28 днів -> 10 + 9 + 9
    """
    days=list(days)
    if not days:
        return []
    q, r = divmod(len(days), 3)
    sizes=[q + (1 if i < r else 0) for i in range(3)]
    out=[]
    pos=0
    for size in sizes:
        if size:
            out.append(days[pos:pos+size])
            pos += size
    return out


def export_monthly_shift_schedule_pdf(year, month, out_path, active_only=True):
    """Читабельний PDF графіка змінності на звичайному офісному A4.

    Місяць ділиться на 3 частини, щоб не стискати шрифт:
    31 день -> 11 + 10 + 10; 30 днів -> 10 + 10 + 10.
    Орієнтація A4 — альбомна.
    """
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from xml.sax.saxutils import escape

    data=collect_monthly_shift_schedule(year,month,active_only=active_only)

    candidates=[
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    font_path=next((p for p in candidates if os.path.exists(p)),None)
    font_name="Helvetica"
    if font_path:
        try:
            if "ShiftScheduleFont" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("ShiftScheduleFont",font_path))
            font_name="ShiftScheduleFont"
        except Exception:
            pass

    page=landscape(A4)
    doc=SimpleDocTemplate(
        str(out_path),pagesize=page,
        leftMargin=14,rightMargin=14,topMargin=14,bottomMargin=14,
        title=f"Графік змінності {month_name_ua(data['month'])} {data['year']}"
    )

    styles=getSampleStyleSheet()
    title=ParagraphStyle(
        "ShiftTitleReadable",parent=styles["Title"],fontName=font_name,
        fontSize=14,leading=16,alignment=TA_CENTER,spaceAfter=3
    )
    normal=ParagraphStyle(
        "ShiftNormalReadable",parent=styles["Normal"],fontName=font_name,
        fontSize=8.8,leading=10.5,alignment=TA_LEFT
    )
    center=ParagraphStyle(
        "ShiftCenterReadable",parent=normal,alignment=TA_CENTER,
        fontSize=9.0,leading=10.2
    )
    head=ParagraphStyle(
        "ShiftHeadReadable",parent=center,fontSize=9.1,leading=10.2
    )
    driver_style=ParagraphStyle(
        "ShiftDriverReadable",parent=normal,fontSize=9.1,leading=10.5
    )
    detail=ParagraphStyle(
        "ShiftDetailReadable",parent=normal,fontSize=8.3,leading=9.8
    )

    story=[]
    company_name=(data["company"]["name"] if data["company"] else "") or ""
    days=data["days"]
    chunks=_split_month_days_a4(days)

    def add_matrix(chunk, page_no):
        if company_name:
            story.append(Paragraph(
                escape(company_name),
                ParagraphStyle(
                    f"Company{page_no}",parent=normal,fontSize=10.5,
                    leading=12.5,alignment=TA_CENTER
                )
            ))
        story.append(Paragraph(
            f"ГРАФІК ЗМІННОСТІ ВОДІЇВ НА {month_name_ua(data['month']).upper()} {data['year']} РОКУ "
            f"— ДНІ {chunk[0].day}–{chunk[-1].day}",
            title
        ))
        story.append(Spacer(1,5))

        header1=[Paragraph("Водій",head)]
        header2=[Paragraph("",head)]
        for d in chunk:
            header1.append(Paragraph(str(d.day),head))
            header2.append(Paragraph(
                ["Пн","Вт","Ср","Чт","Пт","Сб","Нд"][d.weekday()],head
            ))
        header1 += [
            Paragraph("Роб.<br/>днів",head),
            Paragraph("Робота",head),
            Paragraph("Кер.",head),
        ]
        header2 += [
            Paragraph("",head),
            Paragraph("год:хв",head),
            Paragraph("год:хв",head),
        ]

        matrix=[header1,header2]
        cell_meta=[]
        day_indexes=[d.day-1 for d in chunk]

        for r_index,dr in enumerate(data["drivers"],start=2):
            row=[Paragraph(escape(dr["name"]),driver_style)]
            meta=[]
            for idx in day_indexes:
                cell=dr["cells"][idx]
                printed=_monthly_shift_print_cell(cell)
                row.append(Paragraph(escape(printed).replace("\n","<br/>"),center))
                if not cell:
                    kind="empty"
                elif cell in ("В","Відп","Лік","Відпч","Гот","Інш"):
                    kind=cell
                else:
                    kind="work"
                meta.append(kind)
            row += [
                Paragraph(str(dr["work_days"]),center),
                Paragraph(minutes_hhmm(dr["work_min"]),center),
                Paragraph(minutes_hhmm(dr["drive_min"]),center),
            ]
            matrix.append(row)
            cell_meta.append(meta)

        # A4 landscape: після ПІБ та підсумків залишається приблизно
        # 545 pt на дні. При 11 днях це майже 50 pt на один день.
        day_width=min(52, 545/max(1,len(chunk)))
        col_widths=[128]+[day_width]*len(chunk)+[42,48,48]

        table=Table(
            matrix,colWidths=col_widths,repeatRows=2,hAlign="CENTER",
            rowHeights=None
        )
        ts=[
            ("FONTNAME",(0,0),(-1,-1),font_name),
            ("GRID",(0,0),(-1,-1),0.45,colors.HexColor("#666666")),
            ("BACKGROUND",(0,0),(-1,1),colors.HexColor("#D9E6F2")),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("ALIGN",(1,0),(-1,-1),"CENTER"),
            ("LEFTPADDING",(0,0),(-1,-1),2),
            ("RIGHTPADDING",(0,0),(-1,-1),2),
            ("TOPPADDING",(0,0),(-1,-1),3),
            ("BOTTOMPADDING",(0,0),(-1,-1),3),
        ]

        for i,d in enumerate(chunk,start=1):
            if d.weekday()>=5:
                ts.append(("BACKGROUND",(i,0),(i,1),colors.HexColor("#ECECEC")))

        palette={
            "work":"#EAF2FF",
            "В":"#ECECEC",
            "Відп":"#FFF4CC",
            "Лік":"#FDE8E8",
            "Відпч":"#E6F4EA",
            "Гот":"#F4E8FF",
            "Інш":"#F4E8FF",
        }
        for rr,meta in enumerate(cell_meta,start=2):
            for cc,kind in enumerate(meta,start=1):
                if kind in palette:
                    ts.append(("BACKGROUND",(cc,rr),(cc,rr),colors.HexColor(palette[kind])))

        table.setStyle(TableStyle(ts))
        story.append(table)
        story.append(Spacer(1,7))
        story.append(Paragraph(
            "У клітинці робочого дня: початок–кінець зміни; «3ч» — три частини зміни. "
            "В — вихідний; Відп — відпустка; Лік — лікарняний; "
            "Відпч — відпочинок; Гот — готовність.",
            normal
        ))

    for i,chunk in enumerate(chunks,1):
        if not chunk:
            continue
        if story:
            story.append(PageBreak())
        add_matrix(chunk,i)

    # Деталізацію навмисно не додаємо до друкованого PDF.
    # Вона доступна в редагованому Excel на окремому аркуші «Деталізація».

    doc.build(story)
    return data


def export_monthly_shift_detail_pdf(year, month, out_path, active_only=True):
    """Окремий читабельний PDF деталізації графіка змінності.

    Формат: A4 landscape.
    Дані згруповані по водіях. Для кожного водія показуємо:
    дата, частини зміни, перерви, робочий час, час керування,
    маршрут, автомобіль і примітку.
    """
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph,
        Spacer, PageBreak, KeepTogether
    )
    from xml.sax.saxutils import escape

    data=collect_monthly_shift_schedule(year,month,active_only=active_only)

    candidates=[
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    font_path=next((p for p in candidates if os.path.exists(p)),None)
    font_name="Helvetica"
    if font_path:
        try:
            if "ShiftDetailFont" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("ShiftDetailFont",font_path))
            font_name="ShiftDetailFont"
        except Exception:
            pass

    page=landscape(A4)
    doc=SimpleDocTemplate(
        str(out_path),
        pagesize=page,
        leftMargin=16,rightMargin=16,topMargin=16,bottomMargin=16,
        title=f"Деталізація графіка змінності {month_name_ua(data['month'])} {data['year']}"
    )

    styles=getSampleStyleSheet()
    title=ParagraphStyle(
        "ShiftDetailTitle",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=14,
        leading=17,
        alignment=TA_CENTER,
        spaceAfter=5,
    )
    normal=ParagraphStyle(
        "ShiftDetailNormal",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=8.8,
        leading=10.5,
        alignment=TA_LEFT,
    )
    head=ParagraphStyle(
        "ShiftDetailHead",
        parent=normal,
        fontSize=8.5,
        leading=9.5,
        alignment=TA_CENTER,
    )
    center=ParagraphStyle(
        "ShiftDetailCenter",
        parent=normal,
        fontSize=8.6,
        leading=10,
        alignment=TA_CENTER,
    )
    driver_head=ParagraphStyle(
        "ShiftDetailDriver",
        parent=normal,
        fontSize=10.5,
        leading=13,
        spaceBefore=4,
        spaceAfter=4,
    )
    small=ParagraphStyle(
        "ShiftDetailSmall",
        parent=normal,
        fontSize=7.7,
        leading=9,
    )

    story=[]
    company_name=(data["company"]["name"] if data["company"] else "") or ""

    if company_name:
        story.append(Paragraph(
            escape(company_name),
            ParagraphStyle(
                "ShiftDetailCompany",
                parent=normal,
                fontSize=10.5,
                leading=12,
                alignment=TA_CENTER,
            )
        ))
    story.append(Paragraph(
        f"ДЕТАЛІЗАЦІЯ ГРАФІКА ЗМІННОСТІ - {month_name_ua(data['month']).upper()} {data['year']} РОКУ",
        title
    ))
    story.append(Paragraph(
        "Точні частини зміни, проміжки між частинами, робочий час і плановий час керування.",
        ParagraphStyle(
            "ShiftDetailIntro",
            parent=normal,
            alignment=TA_CENTER,
            fontSize=8.6,
        )
    ))
    story.append(Spacer(1,7))

    details_by_driver={}
    for item in data["details"]:
        details_by_driver.setdefault(item["driver"],[]).append(item)

    drivers_by_name={d["name"]:d for d in data["drivers"]}

    if not data["drivers"]:
        story.append(Paragraph("Немає водіїв для формування деталізації.",normal))
    else:
        first_driver=True
        for driver in data["drivers"]:
            name=driver["name"]
            rows=details_by_driver.get(name,[])

            if not first_driver:
                story.append(Spacer(1,6))
            first_driver=False

            # Заголовок водія + підсумок.
            story.append(Paragraph(
                f"<b>{escape(name)}</b> &nbsp;&nbsp; "
                f"Робочих днів: <b>{driver['work_days']}</b> &nbsp;&nbsp; "
                f"Робота: <b>{escape(minutes_hhmm(driver['work_min']))}</b> &nbsp;&nbsp; "
                f"Керування: <b>{escape(minutes_hhmm(driver['drive_min']))}</b>",
                driver_head
            ))

            headers=[
                "Дата","Графік / частини","Перерви",
                "Робота","Кер.","Маршрут","Авто","Примітка"
            ]
            table_rows=[[Paragraph(h,head) for h in headers]]

            if rows:
                for item in rows:
                    table_rows.append([
                        Paragraph(item["date"].strftime("%d.%m.%Y"),center),
                        Paragraph(escape(item["schedule"]).replace("\n","<br/>"),normal),
                        Paragraph(escape(item["breaks"]).replace("\n","<br/>"),center),
                        Paragraph(minutes_hhmm(item["work_min"]),center),
                        Paragraph(minutes_hhmm(item["drive_min"]),center),
                        Paragraph(escape(item["route"]).replace("\n","<br/>"),small),
                        Paragraph(escape(item["vehicle"]).replace("\n","<br/>"),small),
                        Paragraph(escape(item["notes"]).replace("\n","<br/>"),small),
                    ])
            else:
                table_rows.append([
                    Paragraph("За вибраний місяць робочих змін немає.",normal)
                ] + [""]*7)

            # Сумарна ширина < робочої ширини A4 landscape (~810 pt).
            col_widths=[58,154,74,48,48,190,92,130]
            table=Table(
                table_rows,
                colWidths=col_widths,
                repeatRows=1,
                hAlign="CENTER"
            )
            table.setStyle(TableStyle([
                ("FONTNAME",(0,0),(-1,-1),font_name),
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#D9E6F2")),
                ("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#1F2937")),
                ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#777777")),
                ("VALIGN",(0,0),(-1,-1),"TOP"),
                ("ALIGN",(0,0),(-1,0),"CENTER"),
                ("LEFTPADDING",(0,0),(-1,-1),3),
                ("RIGHTPADDING",(0,0),(-1,-1),3),
                ("TOPPADDING",(0,0),(-1,-1),3),
                ("BOTTOMPADDING",(0,0),(-1,-1),3),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[
                    colors.white,
                    colors.HexColor("#F8FAFC")
                ]),
            ]))
            story.append(table)

    story.append(Spacer(1,8))
    story.append(Paragraph(
        f"Сформовано: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        ParagraphStyle(
            "ShiftDetailGenerated",
            parent=small,
            textColor=colors.HexColor("#666666"),
            alignment=TA_LEFT,
        )
    ))

    doc.build(story)
    return data


def export_monthly_shift_schedule_xlsx(year, month, out_path, active_only=True):
    """Редагований Excel графіка змінності під стандартний A4.

    Місяць ділиться на три аркуші/друковані частини, як і PDF.
    Окремий аркуш «Деталізація» лишається для ручного редагування.
    """
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    data=collect_monthly_shift_schedule(year,month,active_only=active_only)
    wb=Workbook()
    wb.remove(wb.active)

    thin=Side(style="thin",color="777777")
    border=Border(left=thin,right=thin,top=thin,bottom=thin)
    fills={
        "header":PatternFill("solid",fgColor="D9E6F2"),
        "weekend":PatternFill("solid",fgColor="ECECEC"),
        "work":PatternFill("solid",fgColor="EAF2FF"),
        "В":PatternFill("solid",fgColor="ECECEC"),
        "Відп":PatternFill("solid",fgColor="FFF4CC"),
        "Лік":PatternFill("solid",fgColor="FDE8E8"),
        "Відпч":PatternFill("solid",fgColor="E6F4EA"),
        "Гот":PatternFill("solid",fgColor="F4E8FF"),
        "Інш":PatternFill("solid",fgColor="F4E8FF"),
    }

    days=data["days"]
    chunks=_split_month_days_a4(days)
    company_name=(data["company"]["name"] if data["company"] else "") or ""

    for chunk in chunks:
        if not chunk:
            continue
        ws=wb.create_sheet(f"{chunk[0].day}-{chunk[-1].day}")
        ncols=1+len(chunk)+3

        ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=ncols)
        ws.cell(1,1,company_name)
        ws.cell(1,1).font=Font(size=11,bold=True)
        ws.cell(1,1).alignment=Alignment(horizontal="center")

        ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=ncols)
        ws.cell(
            2,1,
            f"ГРАФІК ЗМІННОСТІ ВОДІЇВ НА {month_name_ua(data['month']).upper()} {data['year']} РОКУ "
            f"— ДНІ {chunk[0].day}–{chunk[-1].day}"
        )
        ws.cell(2,1).font=Font(size=14,bold=True)
        ws.cell(2,1).alignment=Alignment(horizontal="center")

        headers=["Водій"]
        for d in chunk:
            headers.append(f"{d.day}\n{['Пн','Вт','Ср','Чт','Пт','Сб','Нд'][d.weekday()]}")
        headers += ["Роб. днів","Робота","Кер."]

        for c,h in enumerate(headers,1):
            cell=ws.cell(4,c,h)
            cell.font=Font(size=10,bold=True)
            cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
            cell.fill=fills["header"]
            cell.border=border

        for col,d in enumerate(chunk,2):
            if d.weekday()>=5:
                ws.cell(4,col).fill=fills["weekend"]

        start_row=5
        day_indexes=[d.day-1 for d in chunk]

        for r_idx,dr in enumerate(data["drivers"],start_row):
            ws.cell(r_idx,1,dr["name"])
            ws.cell(r_idx,1).font=Font(size=10,bold=True)
            ws.cell(r_idx,1).alignment=Alignment(vertical="center",wrap_text=True)
            ws.cell(r_idx,1).border=border

            for offset,day_index in enumerate(day_indexes,2):
                raw=dr["cells"][day_index]
                value=_monthly_shift_print_cell(raw)
                c=ws.cell(r_idx,offset,value)
                c.font=Font(size=10)
                c.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
                c.border=border

                if not raw:
                    pass
                elif raw in ("В","Відп","Лік","Відпч","Гот","Інш"):
                    c.fill=fills.get(raw,fills["work"])
                else:
                    c.fill=fills["work"]

            summary_col=2+len(chunk)
            values=[
                dr["work_days"],
                minutes_hhmm(dr["work_min"]),
                minutes_hhmm(dr["drive_min"]),
            ]
            for j,val in enumerate(values,summary_col):
                c=ws.cell(r_idx,j,val)
                c.font=Font(size=10,bold=(j==summary_col))
                c.alignment=Alignment(horizontal="center",vertical="center")
                c.border=border

            ws.row_dimensions[r_idx].height=42

        ws.column_dimensions["A"].width=25
        for col in range(2,2+len(chunk)):
            ws.column_dimensions[get_column_letter(col)].width=10.5
        for col in range(2+len(chunk),2+len(chunk)+3):
            ws.column_dimensions[get_column_letter(col)].width=11

        ws.row_dimensions[4].height=30
        ws.freeze_panes="B5"
        ws.sheet_view.showGridLines=False

        ws.page_setup.orientation="landscape"
        ws.page_setup.paperSize=ws.PAPERSIZE_A4
        ws.page_setup.fitToWidth=1
        ws.page_setup.fitToHeight=0
        ws.sheet_properties.pageSetUpPr.fitToPage=True
        ws.print_title_rows="1:4"
        ws.print_options.horizontalCentered=True
        ws.page_margins.left=0.25
        ws.page_margins.right=0.25
        ws.page_margins.top=0.35
        ws.page_margins.bottom=0.35

        last_row=max(5,start_row+len(data["drivers"])-1)
        ws.print_area=f"A1:{get_column_letter(ncols)}{last_row}"

    # Повна редагована деталізація.
    ws=wb.create_sheet("Деталізація")
    headers=["Водій","Дата","Графік / частини","Перерви","Робота","Кер.","Маршрут","Авто","Примітка"]
    for c,h in enumerate(headers,1):
        cell=ws.cell(1,c,h)
        cell.font=Font(size=10,bold=True)
        cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
        cell.fill=fills["header"]
        cell.border=border

    for r,item in enumerate(data["details"],2):
        vals=[
            item["driver"],
            item["date"].strftime("%d.%m.%Y"),
            item["schedule"],
            item["breaks"],
            minutes_hhmm(item["work_min"]),
            minutes_hhmm(item["drive_min"]),
            item["route"],
            item["vehicle"],
            item["notes"],
        ]
        for c,val in enumerate(vals,1):
            cell=ws.cell(r,c,val)
            cell.font=Font(size=10)
            cell.alignment=Alignment(
                horizontal="center" if c in (2,4,5,6) else "left",
                vertical="top",
                wrap_text=True
            )
            cell.border=border
        ws.row_dimensions[r].height=30

    widths=[28,12,28,16,10,10,36,20,28]
    for i,w in enumerate(widths,1):
        ws.column_dimensions[get_column_letter(i)].width=w
    ws.freeze_panes="A2"
    ws.sheet_view.showGridLines=False
    ws.auto_filter.ref=f"A1:I{max(1,len(data['details'])+1)}"
    ws.page_setup.orientation="landscape"
    ws.page_setup.paperSize=ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth=1
    ws.page_setup.fitToHeight=0
    ws.sheet_properties.pageSetUpPr.fitToPage=True

    wb.save(str(out_path))
    return data


UA_MONTHS = ["Січень","Лютий","Березень","Квітень","Травень","Червень",
             "Липень","Серпень","Вересень","Жовтень","Листопад","Грудень"]
UA_WEEKDAYS = ["Пн","Вт","Ср","Чт","Пт","Сб","Нд"]

def _extract_date_from_ui(value):
    s = (value or "").strip()
    # Full datetime field HH:MM DD.MM.YYYY
    if len(s) >= 16 and s[2] == ":":
        tail = s[-10:]
        try:
            return datetime.strptime(tail, "%d.%m.%Y").date()
        except ValueError:
            pass
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return date.today()

def _apply_date_to_ui(variable, chosen):
    old = (variable.get() or "").strip()
    if len(old) >= 16 and old[2] == ":":
        variable.set(f"{old[:5]} {chosen.strftime('%d.%m.%Y')}")
    else:
        variable.set(chosen.strftime("%d.%m.%Y"))

def show_calendar_picker(parent, variable, title="Вибір дати"):
    selected = _extract_date_from_ui(variable.get())
    state = {"year": selected.year, "month": selected.month}

    win = tk.Toplevel(parent)
    win.title(title)
    win.transient(parent)
    win.resizable(False, False)
    win.grab_set()

    header = ttk.Frame(win, padding=(10, 8, 10, 4))
    header.pack(fill="x")
    month_title = tk.StringVar()

    body = ttk.Frame(win, padding=(10, 4, 10, 10))
    body.pack()

    def choose(d):
        _apply_date_to_ui(variable, d)
        win.destroy()

    def move(delta):
        y, m = state["year"], state["month"]
        m += delta
        if m < 1:
            m = 12
            y -= 1
        elif m > 12:
            m = 1
            y += 1
        state["year"], state["month"] = y, m
        redraw()

    ttk.Button(header, text="◀", width=4, command=lambda: move(-1)).pack(side="left")
    ttk.Label(header, textvariable=month_title, width=20, anchor="center",
              font=("TkDefaultFont", 10, "bold")).pack(side="left", padx=6)
    ttk.Button(header, text="▶", width=4, command=lambda: move(1)).pack(side="left")
    ttk.Button(header, text="Сьогодні", command=lambda: choose(date.today())).pack(side="left", padx=(8, 0))

    def redraw():
        for child in body.winfo_children():
            child.destroy()
        y, m = state["year"], state["month"]
        month_title.set(f"{UA_MONTHS[m-1]} {y}")
        for col, wd in enumerate(UA_WEEKDAYS):
            ttk.Label(body, text=wd, width=4, anchor="center").grid(row=0, column=col, padx=1, pady=1)

        first = date(y, m, 1)
        days = calendar.monthrange(y, m)[1]
        for dnum in range(1, days + 1):
            pos = first.weekday() + dnum - 1
            row, col = divmod(pos, 7)
            d = date(y, m, dnum)
            ttk.Button(body, text=str(dnum), width=4,
                       command=lambda dd=d: choose(dd)).grid(row=row+1, column=col, padx=1, pady=1)

    redraw()
    win.wait_window()

def calendar_button(parent, variable):
    # Text label instead of an emoji so the button is visible on every Windows font setup.
    return ttk.Button(parent, text="Дата…", width=7,
                      command=lambda: show_calendar_picker(parent, variable))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Taxo v8.64 — Облік водіїв — 48 місяців")
        self.geometry("1200x760")
        self.minsize(1050, 650)
        self.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.bind("<Control-q>", lambda e: self.exit_app())
        self.driver_id = None
        self.att_driver_id = None
        self.att_driver_map = {}
        self.build_ui()
        self.load_company()
        self.load_drivers()
        self.refresh_month()

    def build_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Зберегти реквізити підприємства", command=self.save_company)
        file_menu.add_separator()
        file_menu.add_command(label="Резервна копія", command=self.manual_backup)
        file_menu.add_command(label="Відновити з резервної копії…", command=self.restore_backup)
        file_menu.add_command(label="Відкрити папку даних", command=self.open_data_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Вийти", command=self.exit_app)
        menubar.add_cascade(label="Файл", menu=file_menu)
        service_menu = tk.Menu(menubar, tearoff=0)
        service_menu.add_command(label="Оновити табель", command=self.refresh_month)
        service_menu.add_command(label="Графік водіїв", command=lambda: self.show_tab(self.tab_schedule))
        service_menu.add_command(label="Місячний графік змінності", command=self.show_monthly_shift_schedule)
        service_menu.add_command(label="Місячний табель / баланс часу", command=self.show_monthly_work_balance)
        service_menu.add_command(label="Контроль бланків — 56 днів + поточний", command=self.show_attestation_gap_control)
        service_menu.add_command(label="Маршрути", command=lambda: self.show_tab(self.tab_route_catalog))
        service_menu.add_command(label="Шаблони маршрутів", command=lambda: self.show_tab(self.tab_routes))
        service_menu.add_command(label="Автомобілі", command=lambda: self.show_tab(self.tab_vehicles))
        if TachographModule:
            service_menu.add_command(label="Тахограф — шайби", command=lambda: self.show_tab(self.tab_tacho))
        menubar.add_cascade(label="Сервіс", menu=service_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Про програму", command=lambda: messagebox.showinfo("Облік водіїв", "Облік водіїв та робочого часу — 48 місяців."))
        menubar.add_cascade(label="Довідка", menu=help_menu)
        self.config(menu=menubar)

    def show_tab(self, tab):
        for child in self.winfo_children():
            if isinstance(child, ttk.Notebook):
                child.select(tab)
                return

    def exit_app(self):
        if messagebox.askyesno("Вихід", "Вийти з програми?", parent=self):
            self.destroy()

    def build_ui(self):
        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except Exception:
            pass

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        self.tab_company = ttk.Frame(nb)
        self.tab_drivers = ttk.Frame(nb)
        self.tab_vehicles = ttk.Frame(nb)
        self.tab_work = ttk.Frame(nb)
        self.tab_schedule = ttk.Frame(nb)
        self.tab_routes = ttk.Frame(nb)
        self.tab_route_catalog = ttk.Frame(nb)
        self.tab_att = ttk.Frame(nb)
        self.tab_tacho = ttk.Frame(nb)
        nb.add(self.tab_company, text="Підприємство")
        nb.add(self.tab_drivers, text="Водії")
        nb.add(self.tab_vehicles, text="Автомобілі")
        nb.add(self.tab_work, text="Табель")
        nb.add(self.tab_schedule, text="Графік водіїв")
        nb.add(self.tab_routes, text="Шаблони маршрутів")
        nb.add(self.tab_route_catalog, text="Маршрути")
        nb.add(self.tab_att, text="Підтвердження діяльності")
        nb.add(self.tab_tacho, text="Тахограф — шайби")

        self.build_company()
        self.build_drivers()
        self.build_vehicles()
        self.build_work()
        self.build_schedule()
        self.build_routes()
        self.build_route_catalog()
        self.build_attestation()
        if TachographModule:
            # v8.53: тахокарти — тільки контроль. Модуль не отримує callback,
            # який міг би змінювати основний графік/табель.
            self.tacho_module = TachographModule(
                self.tab_tacho, self.tacho_drivers, self.tacho_vehicles
            )
            self.tacho_module.seed_examples([APP_DIR / "tachograph_test_scan_01.jpg", APP_DIR / "tachograph_test_scan_02.jpg"])
        else:
            ttk.Label(self.tab_tacho, text="Модуль тахографа не завантажено. Запустіть START.bat для встановлення залежностей.").pack(padx=20, pady=20)

    def _make_scrollable_tab_body(self, tab, key):
        """Створює двонапрямно прокручувану область для всього вмісту вкладки."""
        shell = ttk.Frame(tab)
        shell.pack(fill="both", expand=True)
        shell.rowconfigure(0, weight=1)
        shell.columnconfigure(0, weight=1)

        canvas = tk.Canvas(shell, highlightthickness=0, borderwidth=0)
        ybar = ttk.Scrollbar(shell, orient="vertical", command=canvas.yview)
        xbar = ttk.Scrollbar(shell, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")

        body = ttk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=body, anchor="nw")

        def sync_region(_event=None):
            try:
                canvas.configure(scrollregion=canvas.bbox("all"))
            except tk.TclError:
                pass

        def fit_minimum_width(event):
            try:
                body.update_idletasks()
                requested=max(1, body.winfo_reqwidth())
                canvas.itemconfigure(window_id, width=max(event.width, requested))
                sync_region()
            except tk.TclError:
                pass

        body.bind("<Configure>", sync_region, add="+")
        canvas.bind("<Configure>", fit_minimum_width, add="+")

        def wheel(event):
            delta=getattr(event, "delta", 0)
            if delta:
                canvas.yview_scroll(int(-delta/120) or (-1 if delta>0 else 1), "units")
            return "break"

        def shift_wheel(event):
            delta=getattr(event, "delta", 0)
            if delta:
                canvas.xview_scroll(int(-delta/120) or (-1 if delta>0 else 1), "units")
            return "break"

        def bind_wheel(_event=None):
            canvas.bind_all("<MouseWheel>", wheel)
            canvas.bind_all("<Shift-MouseWheel>", shift_wheel)

        def unbind_wheel(_event=None):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Shift-MouseWheel>")

        canvas.bind("<Enter>", bind_wheel)
        canvas.bind("<Leave>", unbind_wheel)
        body.bind("<Enter>", bind_wheel)
        body.bind("<Leave>", unbind_wheel)

        setattr(self, f"_{key}_scroll_canvas", canvas)
        return body

    def build_company(self):
        host = self._make_scrollable_tab_body(self.tab_company, "company")
        f = ttk.LabelFrame(host, text="Реквізити підприємства — українською")
        f.pack(fill="x", padx=12, pady=(12,6))
        self.company_vars = {}
        labels = [
            ("name", "Найменування / ПІБ суб'єкта господарювання"),
            ("address", "Адреса"),
            ("phone", "Телефон"),
            ("fax", "Факс"),
            ("email", "E-mail"),
            ("signer_name", "Підписант (ПІБ)"),
            ("signer_position", "Посада підписанта"),
        ]
        for i, (key, label) in enumerate(labels):
            ttk.Label(f, text=label).grid(row=i, column=0, sticky="w", padx=8, pady=5)
            v = tk.StringVar()
            self.company_vars[key] = v
            ttk.Entry(f, textvariable=v, width=90).grid(row=i, column=1, sticky="ew", padx=8, pady=5)
        f.columnconfigure(1, weight=1)

        en_box = ttk.LabelFrame(host, text="Реквізити для англійської сторони Бланка")
        en_box.pack(fill="x", padx=12, pady=(0,10))
        self.company_en_vars = {}
        en_labels = [
            ("name_en", "Name of the undertaking"),
            ("address_en", "Address"),
            ("signer_name_en", "Name and first name of representative"),
            ("signer_position_en", "Position in the undertaking"),
            ("place_en", "Place (місце у бланку)"),
        ]
        ttk.Label(
            en_box,
            text=(
                "Заповнюйте тільки ті поля, для яких потрібен окремий англійський текст. "
                "Якщо поле порожнє — в англійську сторону автоматично підставляється українське значення. "
                "Телефон, факс та E-mail копіюються без змін."
            ),
            foreground="gray", wraplength=1050, justify="left"
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(7,4))
        for i, (key, label) in enumerate(en_labels, start=1):
            ttk.Label(en_box, text=label).grid(row=i, column=0, sticky="w", padx=8, pady=5)
            v = tk.StringVar()
            self.company_en_vars[key] = v
            ttk.Entry(en_box, textvariable=v, width=90).grid(row=i, column=1, sticky="ew", padx=8, pady=5)
        en_box.columnconfigure(1, weight=1)

        company_save_bar = ttk.Frame(host)
        company_save_bar.pack(fill="x", padx=12, pady=(0,10))
        ttk.Button(
            company_save_bar,
            text="Зберегти реквізити підприємства",
            command=self.save_company
        ).pack(side="left")
        ttk.Label(
            company_save_bar,
            text=(
                "Під час створення або редагування Бланка поточні реквізити "
                "також зберігаються автоматично."
            ),
            foreground="gray"
        ).pack(side="left", padx=(12,0))

        transport_box = ttk.LabelFrame(
            host,
            text="Профіль перевезень для контролю Положення №340"
        )
        transport_box.pack(fill="x", padx=12, pady=(0, 10))

        ttk.Label(transport_box, text="Вид перевезень:").grid(
            row=0, column=0, sticky="w", padx=8, pady=7
        )
        self.transport_profile_var = tk.StringVar(value=DEFAULT_TRANSPORT_PROFILE)
        ttk.Combobox(
            transport_box,
            textvariable=self.transport_profile_var,
            values=TRANSPORT_PROFILES,
            state="readonly",
            width=42
        ).grid(row=0, column=1, sticky="w", padx=8, pady=7)

        ttk.Label(
            transport_box,
            text=(
                "Зараз основний робочий профіль — регулярні пасажирські перевезення. "
                "Вибір зберігається в базі та використовується у «Підсумки / контроль». "
                "Для інших профілів спеціальні винятки №340 будемо підключати окремо."
            ),
            foreground="gray",
            wraplength=850,
            justify="left"
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=8, pady=(0, 8))
        transport_box.columnconfigure(1, weight=1)

        btns = ttk.Frame(host)
        btns.pack(fill="x", padx=12, pady=(0, 8))
        ttk.Button(btns, text="Резервна копія", command=self.manual_backup).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="Відновити з копії…", command=self.restore_backup).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="Відкрити папку даних", command=self.open_data_folder).pack(side="left")
        ttk.Button(btns, text="Вийти", command=self.exit_app).pack(side="right")
        ttk.Label(host, text=f"База: {DB_PATH}", foreground="gray").pack(anchor="w", padx=12)
        ttk.Label(host, text=f"Резервні копії: {BACKUP_DIR}", foreground="gray").pack(anchor="w", padx=12)
        ttk.Label(host, text="Дані зберігаються окремо від програми. Оновлення версій не потребують перенесення бази.", foreground="gray").pack(anchor="w", padx=12)

    def manual_backup(self):
        try:
            path = backup_database("manual")
            if path:
                messagebox.showinfo("Резервна копія", f"Резервну копію створено:\n{path}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося створити резервну копію:\n{e}")

    def open_data_folder(self):
        try:
            os.startfile(DATA_ROOT) if os.name == "nt" else subprocess.Popen(["xdg-open", str(DATA_ROOT)])
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def restore_backup(self):
        path=filedialog.askopenfilename(
            parent=self,
            title="Виберіть резервну копію Taxo",
            initialdir=str(BACKUP_DIR),
            filetypes=[
                ("Резервна копія Taxo","*.sqlite3"),
                ("SQLite база","*.db *.sqlite *.sqlite3"),
                ("Усі файли","*.*"),
            ]
        )
        if not path:
            return

        ok,details=validate_database_file(path)
        if not ok:
            messagebox.showerror(
                "Відновлення бази",
                f"Цей файл не можна використати для відновлення:\n\n{details}",
                parent=self
            )
            return

        p=Path(path)
        try:
            modified=datetime.fromtimestamp(p.stat().st_mtime).strftime("%d.%m.%Y %H:%M")
            size_mb=p.stat().st_size/(1024*1024)
        except Exception:
            modified="—"; size_mb=0

        if not messagebox.askyesno(
            "Відновлення бази",
            "Відновити дані з цієї резервної копії?\n\n"
            f"Файл: {p.name}\n"
            f"Дата файлу: {modified}\n"
            f"Розмір: {size_mb:.2f} МБ\n"
            f"{details}\n\n"
            "Перед відновленням програма автоматично створить страхову копію "
            "поточної бази. Після підтвердження поточні дані буде замінено даними з копії.",
            parent=self
        ):
            return

        try:
            safety,final_details=restore_database_from_file(path)

            self.driver_id=None
            self.att_driver_id=None
            if hasattr(self,"work_driver_var"):
                self.work_driver_var.set("")
            if hasattr(self,"att_driver_var"):
                self.att_driver_var.set("")

            self.load_company()
            self.load_drivers()
            self.load_vehicles()
            self.load_route_catalog()
            self.load_route_templates()
            self.refresh_month()
            self.refresh_schedule()
            self.load_att_history()

            msg="Базу успішно відновлено.\n\n"+final_details
            if safety:
                msg += f"\n\nСтрахова копія попереднього стану:\n{safety}"
            messagebox.showinfo("Відновлення завершено",msg,parent=self)
        except Exception as e:
            messagebox.showerror(
                "Помилка відновлення",
                "Базу не відновлено. Поточні дані залишено/повернено зі страхової копії.\n\n"
                f"{e}",
                parent=self
            )

    def build_drivers(self):
        top = ttk.Frame(self.tab_drivers)
        top.pack(fill="x", padx=10, pady=8)
        ttk.Button(top, text="Новий водій", command=self.new_driver).pack(side="left", padx=4)
        ttk.Button(top, text="Редагувати", command=self.edit_driver).pack(side="left", padx=4)
        ttk.Button(top, text="Видалити", command=self.delete_driver).pack(side="left", padx=4)
        ttk.Button(top, text="Оновити", command=self.load_drivers).pack(side="left", padx=4)

        cols = ("id","name","birth","license","employment","active")
        self.driver_tree = ttk.Treeview(self.tab_drivers, columns=cols, show="headings", height=24)
        headings = {"id":"ID","name":"ПІБ","birth":"Дата народження","license":"Посвідчення","employment":"Прийнятий з","active":"Статус"}
        widths = {"id":50,"name":330,"birth":120,"license":200,"employment":120,"active":80}
        for c in cols:
            self.driver_tree.heading(c, text=headings[c])
            self.driver_tree.column(c, width=widths[c], anchor="w")
        driver_y=ttk.Scrollbar(self.tab_drivers,orient="vertical",command=self.driver_tree.yview)
        driver_x=ttk.Scrollbar(self.tab_drivers,orient="horizontal",command=self.driver_tree.xview)
        self.driver_tree.configure(yscrollcommand=driver_y.set,xscrollcommand=driver_x.set)
        driver_x.pack(side="bottom",fill="x",padx=10,pady=(0,5))
        driver_y.pack(side="right",fill="y",pady=5)
        self.driver_tree.pack(side="left",fill="both", expand=True, padx=(10,0), pady=5)
        self.driver_tree.bind("<<TreeviewSelect>>", self.on_driver_select)

    def driver_form(self, driver=None):
        win = tk.Toplevel(self)
        win.title("Картка водія")
        win.geometry("760x720")
        win.minsize(700,650)
        win.transient(self)

        outer=ttk.Frame(win,padding=10)
        outer.pack(fill="both",expand=True)

        ua=ttk.LabelFrame(outer,text="Дані водія — українською",padding=8)
        ua.pack(fill="x",pady=(0,8))
        en=ttk.LabelFrame(outer,text="Дані для англійської сторони Бланка",padding=8)
        en.pack(fill="x",pady=(0,8))
        extra=ttk.LabelFrame(outer,text="Інші дані",padding=8)
        extra.pack(fill="x",pady=(0,8))

        vars_={}

        ua_fields=[
            ("last_name","Прізвище"),("first_name","Ім'я"),("middle_name","По батькові"),
        ]
        for i,(k,lbl) in enumerate(ua_fields):
            ttk.Label(ua,text=lbl).grid(row=i,column=0,sticky="w",padx=6,pady=5)
            v=tk.StringVar(value=(driver[k] if driver else ""))
            vars_[k]=v
            ttk.Entry(ua,textvariable=v,width=62).grid(row=i,column=1,sticky="ew",padx=6,pady=5)
        ua.columnconfigure(1,weight=1)

        en_fields=[
            ("last_name_en","Surname / прізвище англійською"),
            ("first_name_en","First name / ім'я англійською"),
            ("middle_name_en","Middle name / по батькові англійською"),
        ]
        for i,(k,lbl) in enumerate(en_fields):
            ttk.Label(en,text=lbl).grid(row=i,column=0,sticky="w",padx=6,pady=5)
            raw=(driver[k] if driver and k in driver.keys() else "")
            v=tk.StringVar(value=raw or "")
            vars_[k]=v
            ttk.Entry(en,textvariable=v,width=62).grid(row=i,column=1,sticky="ew",padx=6,pady=5)
        ttk.Label(
            en,
            text="Якщо англійське поле порожнє, у англійську сторону Бланка автоматично підставляється відповідне українське поле.",
            foreground="gray",wraplength=680,justify="left"
        ).grid(row=len(en_fields),column=0,columnspan=2,sticky="w",padx=6,pady=(5,2))
        en.columnconfigure(1,weight=1)

        other_fields=[
            ("birth_date","Дата народження (ДД.ММ.РРРР)"),
            ("license_series","Серія посвідчення"),("license_number","Номер посвідчення"),
            ("license_issue_date","Дата видачі посвідчення (ДД.ММ.РРРР)"),
            ("employment_date","Дата прийняття (ДД.ММ.РРРР)"),
            ("notes","Примітка")
        ]
        for i,(k,lbl) in enumerate(other_fields):
            ttk.Label(extra,text=lbl).grid(row=i,column=0,sticky="w",padx=6,pady=5)
            raw=(driver[k] if driver else "")
            if k in ("birth_date","license_issue_date","employment_date") and raw:
                try:
                    raw=datetime.strptime(str(raw),"%Y-%m-%d").strftime("%d.%m.%Y")
                except ValueError:
                    pass
            v=tk.StringVar(value=raw)
            vars_[k]=v
            ttk.Entry(extra,textvariable=v,width=62).grid(row=i,column=1,sticky="ew",padx=6,pady=5)
            if k in ("birth_date","license_issue_date","employment_date"):
                calendar_button(extra,v).grid(row=i,column=2,sticky="w",padx=(0,6),pady=5)
        extra.columnconfigure(1,weight=1)

        active=tk.BooleanVar(value=bool(driver["active"]) if driver else True)
        ttk.Checkbutton(outer,text="Активний водій",variable=active).pack(anchor="w",padx=8,pady=5)

        def save():
            order=[
                "last_name","first_name","middle_name",
                "last_name_en","first_name_en","middle_name_en",
                "birth_date","license_series","license_number",
                "license_issue_date","employment_date","notes"
            ]
            vals={k:vars_[k].get().strip() for k in order}
            for k in ("birth_date","license_issue_date","employment_date"):
                if vals[k]:
                    try:
                        vals[k]=datetime.strptime(vals[k],"%d.%m.%Y").strftime("%Y-%m-%d")
                    except ValueError:
                        messagebox.showerror("Помилка","Дата має бути у форматі ДД.ММ.РРРР.",parent=win)
                        return
            if not vals["last_name"] or not vals["first_name"]:
                messagebox.showerror("Помилка","Прізвище та ім'я обов'язкові.",parent=win)
                return
            con=db()
            if driver:
                con.execute("""UPDATE drivers SET
                    last_name=?,first_name=?,middle_name=?,
                    last_name_en=?,first_name_en=?,middle_name_en=?,
                    birth_date=?,license_series=?,license_number=?,license_issue_date=?,
                    employment_date=?,notes=?,active=? WHERE id=?""",
                    (vals["last_name"],vals["first_name"],vals["middle_name"],
                     vals["last_name_en"],vals["first_name_en"],vals["middle_name_en"],
                     vals["birth_date"],vals["license_series"],vals["license_number"],
                     vals["license_issue_date"],vals["employment_date"],vals["notes"],
                     int(active.get()),driver["id"]))
            else:
                con.execute("""INSERT INTO drivers(
                    last_name,first_name,middle_name,last_name_en,first_name_en,middle_name_en,
                    birth_date,license_series,license_number,license_issue_date,employment_date,
                    notes,active,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (vals["last_name"],vals["first_name"],vals["middle_name"],
                     vals["last_name_en"],vals["first_name_en"],vals["middle_name_en"],
                     vals["birth_date"],vals["license_series"],vals["license_number"],
                     vals["license_issue_date"],vals["employment_date"],vals["notes"],
                     int(active.get()),datetime.now().isoformat(timespec="seconds")))
            con.commit(); con.close()
            self.load_drivers(); win.destroy()

        ttk.Button(outer,text="Зберегти",command=save).pack(anchor="e",padx=8,pady=8)

    def new_driver(self): self.driver_form()
    def edit_driver(self):
        d=self.selected_driver()
        if d: self.driver_form(d)
    def delete_driver(self):
        d=self.selected_driver()
        if not d: return
        if not messagebox.askyesno("Підтвердження","Видалити водія та його історію?"): return
        con=db(); con.execute("DELETE FROM drivers WHERE id=?",(d["id"],)); con.commit(); con.close(); self.load_drivers()
    def selected_driver(self):
        sel=self.driver_tree.selection()
        if not sel: return None
        did=int(self.driver_tree.item(sel[0],"values")[0])
        con=db(); d=con.execute("SELECT * FROM drivers WHERE id=?",(did,)).fetchone(); con.close(); return d

    def driver_by_id(self, driver_id):
        """Повертає водія за ID незалежно від виділення у вкладці «Водії»."""
        if not driver_id:
            return None
        con=db()
        try:
            return con.execute("SELECT * FROM drivers WHERE id=?",(int(driver_id),)).fetchone()
        finally:
            con.close()

    def driver_full_name(self, d):
        if not d: return ""
        return " ".join(x for x in (d["last_name"], d["first_name"], d["middle_name"]) if x).strip()

    def on_driver_select(self,_=None):
        d=self.selected_driver()
        if d:
            self.driver_id=d["id"]
            if hasattr(self, "work_driver_map"):
                label=next((k for k,v in self.work_driver_map.items() if v==d["id"]), self.driver_full_name(d))
                self.work_driver_var.set(label)
            else:
                self.work_driver_var.set(self.driver_full_name(d))
            self.att_driver_id=d["id"]
            self.att_driver_var.set(self.driver_full_name(d))
            self.refresh_month()
            self.load_att_history()

    def refresh_work_driver_choices(self):
        if not hasattr(self, "work_driver_cb"):
            return
        con=db()
        rows=con.execute(
            "SELECT * FROM drivers ORDER BY active DESC, last_name, first_name, middle_name"
        ).fetchall()
        con.close()

        self.work_driver_map={}
        values=[]
        name_counts={}
        for d in rows:
            base=self.driver_full_name(d)
            name_counts[base]=name_counts.get(base,0)+1

        used={}
        for d in rows:
            base=self.driver_full_name(d)
            if name_counts.get(base,0)>1:
                label=f"{base} [ID {d['id']}]"
            else:
                label=base
            self.work_driver_map[label]=d["id"]
            values.append(label)
            if self.driver_id == d["id"]:
                self.work_driver_var.set(label)

        self.work_driver_cb["values"]=values

        # Якщо водій ще не вибраний — зручно підставити першого активного.
        if not self.driver_id and rows:
            first=rows[0]
            label=next((k for k,v in self.work_driver_map.items() if v==first["id"]), "")
            if label:
                self.driver_id=first["id"]
                self.work_driver_var.set(label)

    def on_work_driver_change(self, _=None):
        label=self.work_driver_var.get().strip()
        did=self.work_driver_map.get(label)
        if not did:
            return
        self.driver_id=did

        # Синхронізуємо вибір у вкладці «Водії», якщо запис там є.
        if hasattr(self, "driver_tree"):
            for item in self.driver_tree.get_children():
                vals=self.driver_tree.item(item, "values")
                if vals and int(vals[0]) == did:
                    self.driver_tree.selection_set(item)
                    self.driver_tree.focus(item)
                    break

        self.refresh_month()

    def refresh_att_driver_choices(self):
        if not hasattr(self, "att_driver_cb"):
            return
        con=db(); rows=con.execute("SELECT * FROM drivers ORDER BY last_name, first_name").fetchall(); con.close()
        self.att_driver_map={}
        vals=[]
        for d in rows:
            name=self.driver_full_name(d)
            self.att_driver_map[name]=d["id"]
            vals.append(name)
        self.att_driver_cb["values"]=vals
        if self.att_driver_var.get() not in vals:
            self.att_driver_var.set("")
            self.att_driver_id=None

    def on_att_driver_change(self, _=None):
        name=self.att_driver_var.get().strip()
        self.att_driver_id=self.att_driver_map.get(name)
        if self.att_driver_id:
            self.load_att_history()

    def load_drivers(self):
        for x in getattr(self,"driver_tree",ttk.Treeview(self)).get_children():
            self.driver_tree.delete(x)
        con=db(); rows=con.execute("SELECT * FROM drivers ORDER BY last_name, first_name").fetchall(); con.close()
        for d in rows:
            name=" ".join(x for x in [d["last_name"],d["first_name"],d["middle_name"]] if x)
            lic=f"{d['license_series']} {d['license_number']}".strip()
            issue=fmt_date(d["license_issue_date"])
            if issue:
                lic=f"{lic}, вид. {issue}" if lic else f"вид. {issue}"
            self.driver_tree.insert("", "end", values=(d["id"],name,fmt_date(d["birth_date"]),lic,fmt_date(d["employment_date"]), "Так" if d["active"] else "Ні"))
        self.refresh_att_driver_choices()
        self.refresh_work_driver_choices()

    def load_company(self):
        con=db(); r=con.execute("SELECT * FROM company WHERE id=1").fetchone(); con.close()
        if r:
            for k in self.company_vars:
                self.company_vars[k].set(r[k] or "")
            for k in getattr(self,"company_en_vars",{}):
                self.company_en_vars[k].set(r[k] or "")
        if hasattr(self,"transport_profile_var"):
            self.transport_profile_var.set(current_transport_profile())

    def save_company(self, show_message=True):
        """Зберігає українські та англійські реквізити підприємства.

        v8.59: цей метод викликається не лише кнопкою/меню, а й автоматично
        перед створенням або редагуванням Бланка підтвердження. Це гарантує,
        що щойно введені англійські поля потрапляють у DOCX навіть якщо
        користувач не натиснув окремо «Зберегти реквізити».
        """
        ua={k:v.get().strip() for k,v in self.company_vars.items()}
        en={k:v.get().strip() for k,v in getattr(self,"company_en_vars",{}).items()}
        con=db()
        try:
            con.execute(
                """UPDATE company SET
                       name=?,address=?,phone=?,fax=?,email=?,signer_name=?,signer_position=?,
                       name_en=?,address_en=?,signer_name_en=?,signer_position_en=?,place_en=?
                   WHERE id=1""",
                (
                    ua.get("name",""),ua.get("address",""),ua.get("phone",""),ua.get("fax",""),
                    ua.get("email",""),ua.get("signer_name",""),ua.get("signer_position",""),
                    en.get("name_en",""),en.get("address_en",""),en.get("signer_name_en",""),
                    en.get("signer_position_en",""),en.get("place_en","")
                )
            )
            con.commit()
        finally:
            con.close()

        if hasattr(self,"transport_profile_var"):
            profile=self.transport_profile_var.get().strip()
            if profile not in TRANSPORT_PROFILES:
                profile=DEFAULT_TRANSPORT_PROFILE
                self.transport_profile_var.set(profile)
            set_setting("transport_profile", profile)

        if show_message:
            messagebox.showinfo("Готово","Реквізити підприємства та профіль перевезень збережено.")
        return True

    def build_vehicles(self):
        top = ttk.Frame(self.tab_vehicles)
        top.pack(fill="x", padx=10, pady=8)
        ttk.Button(top, text="Нове авто", command=self.vehicle_form).pack(side="left", padx=4)
        ttk.Button(top, text="Редагувати", command=self.edit_vehicle).pack(side="left", padx=4)
        ttk.Button(top, text="Видалити", command=self.delete_vehicle).pack(side="left", padx=4)
        ttk.Button(top, text="Оновити", command=self.load_vehicles).pack(side="left", padx=4)
        ttk.Label(self.tab_vehicles, text="Каталог автомобілів. Одного водія можна щодня призначати на різні автомобілі та маршрути.", foreground="gray").pack(anchor="w", padx=12)
        cols=("id","name","plate","make","year","active","notes")
        self.vehicle_tree=ttk.Treeview(self.tab_vehicles,columns=cols,show="headings",height=25)
        heads={"id":"ID","name":"Назва","plate":"Держ. №","make":"Марка / модель","year":"Рік","active":"Статус","notes":"Примітка"}
        widths={"id":45,"name":180,"plate":120,"make":180,"year":70,"active":80,"notes":300}
        for c in cols:
            self.vehicle_tree.heading(c,text=heads[c]); self.vehicle_tree.column(c,width=widths[c],anchor="w")
        vehicle_y=ttk.Scrollbar(self.tab_vehicles,orient="vertical",command=self.vehicle_tree.yview)
        vehicle_x=ttk.Scrollbar(self.tab_vehicles,orient="horizontal",command=self.vehicle_tree.xview)
        self.vehicle_tree.configure(yscrollcommand=vehicle_y.set,xscrollcommand=vehicle_x.set)
        vehicle_x.pack(side="bottom",fill="x",padx=10,pady=(0,5))
        vehicle_y.pack(side="right",fill="y",pady=5)
        self.vehicle_tree.pack(side="left",fill="both",expand=True,padx=(10,0),pady=5)
        self.load_vehicles()

    def load_vehicles(self):
        if not hasattr(self,"vehicle_tree"): return
        for x in self.vehicle_tree.get_children(): self.vehicle_tree.delete(x)
        con=db(); rows=con.execute("SELECT * FROM vehicles ORDER BY active DESC, name, plate").fetchall(); con.close()
        for r in rows:
            self.vehicle_tree.insert("","end",values=(r["id"],r["name"],r["plate"],r["make_model"],r["year"] or "","Так" if r["active"] else "Ні",r["notes"]))

    def selected_vehicle(self):
        sel=self.vehicle_tree.selection()
        if not sel: return None
        vid=int(self.vehicle_tree.item(sel[0],"values")[0])
        con=db(); r=con.execute("SELECT * FROM vehicles WHERE id=?",(vid,)).fetchone(); con.close(); return r

    def vehicle_label(self, r):
        if not r: return ""
        parts=[r["name"], r["plate"]]
        if r["make_model"]: parts.append(r["make_model"])
        return " — ".join(x for x in parts if x)

    def vehicle_form(self, vehicle=None):
        win=tk.Toplevel(self); win.title("Автомобіль"); win.geometry("620x430"); win.transient(self); win.grab_set()
        fields=[("name","Назва / інвентарний номер"),("plate","Державний номер"),("make_model","Марка / модель"),("year","Рік"),("notes","Примітка")]
        vv={}
        for i,(k,lbl) in enumerate(fields):
            ttk.Label(win,text=lbl).grid(row=i,column=0,sticky="w",padx=10,pady=8)
            v=tk.StringVar(value=str(vehicle[k] or "") if vehicle else ""); vv[k]=v
            ttk.Entry(win,textvariable=v,width=55).grid(row=i,column=1,sticky="ew",padx=10,pady=8)
        active=tk.BooleanVar(value=bool(vehicle["active"]) if vehicle else True)
        ttk.Checkbutton(win,text="Активний автомобіль",variable=active).grid(row=len(fields),column=1,sticky="w",padx=10,pady=8)
        def save():
            name=vv["name"].get().strip()
            if not name:
                messagebox.showerror("Помилка","Вкажіть назву автомобіля.",parent=win); return
            year=vv["year"].get().strip()
            if year:
                try: year=int(year)
                except ValueError: messagebox.showerror("Помилка","Рік має бути числом.",parent=win); return
            else: year=None
            con=db()
            vals=(name,vv["plate"].get().strip(),vv["make_model"].get().strip(),year,vv["notes"].get().strip(),int(active.get()))
            if vehicle:
                con.execute("UPDATE vehicles SET name=?,plate=?,make_model=?,year=?,notes=?,active=? WHERE id=?",(*vals,vehicle["id"]))
            else:
                con.execute("INSERT INTO vehicles(name,plate,make_model,year,notes,active,created_at) VALUES(?,?,?,?,?,?,?)",(*vals,datetime.now().isoformat(timespec="seconds")))
            con.commit(); con.close(); self.load_vehicles(); win.destroy()
        ttk.Button(win,text="Зберегти",command=save).grid(row=len(fields)+1,column=1,sticky="e",padx=10,pady=14)

    def edit_vehicle(self):
        v=self.selected_vehicle()
        if v: self.vehicle_form(v)

    def delete_vehicle(self):
        v=self.selected_vehicle()
        if not v: return
        if not messagebox.askyesno("Підтвердження","Видалити автомобіль з каталогу? Історичні записи табеля залишаться."): return
        con=db(); con.execute("UPDATE vehicles SET active=0 WHERE id=?",(v["id"],)); con.commit(); con.close(); self.load_vehicles()

    def build_work(self):
        bar=ttk.Frame(self.tab_work); bar.pack(fill="x",padx=10,pady=8)
        self.work_driver_var=tk.StringVar(value="")
        self.work_driver_map={}
        ttk.Label(bar,text="Водій:").pack(side="left")
        self.work_driver_cb=ttk.Combobox(
            bar,
            textvariable=self.work_driver_var,
            state="readonly",
            width=34
        )
        self.work_driver_cb.pack(side="left",padx=5)
        self.work_driver_cb.bind("<<ComboboxSelected>>", self.on_work_driver_change)
        self.year_var=tk.IntVar(value=date.today().year)
        self.month_var=tk.IntVar(value=date.today().month)
        ttk.Spinbox(bar,from_=2020,to=2100,textvariable=self.year_var,width=7,command=self.refresh_month).pack(side="left",padx=4)
        ttk.Spinbox(bar,from_=1,to=12,textvariable=self.month_var,width=4,command=self.refresh_month).pack(side="left",padx=4)
        ttk.Button(bar,text="Новий / редагувати",command=self.save_work_row).pack(side="left",padx=5)
        ttk.Button(bar,text="Копіювати день",command=self.copy_work_day).pack(side="left",padx=5)
        ttk.Button(bar,text="Вставити день",command=self.paste_work_day).pack(side="left",padx=5)
        ttk.Button(bar,text="Excel",command=lambda:self.export_current("xlsx")).pack(side="left",padx=5)
        ttk.Button(bar,text="PDF",command=lambda:self.export_current("pdf")).pack(side="left",padx=5)
        ttk.Button(bar,text="Підсумки / контроль",command=self.show_work_analysis).pack(side="left",padx=5)
        ttk.Button(
            bar,text="Місячний табель / баланс",
            command=self.show_monthly_work_balance
        ).pack(side="left",padx=5)
        ttk.Button(
            bar,
            text="⚠ Без тахо — робочі дні 8 год",
            command=self.autofill
        ).pack(side="left",padx=(18,5))
        ttk.Label(
            self.tab_work,
            text=(
                "«Частини зміни» в програмі — наш технічний поділ дня: для кожної частини задаємо "
                "точний час роботи та «Кер.». Проміжки між частинами використовуються для контролю "
                "перерв у керуванні 4:30 → 45 хв або 15+30."
            ),
            foreground="gray"
        ).pack(anchor="w",padx=12)
        cols=("id","date","weekday","type","schedule","breaks","work","drive","over","route","vehicle","notes","mode")
        self.work_tree=ttk.Treeview(self.tab_work,columns=cols,show="headings",height=24,selectmode="extended")
        heads={"id":"ID","date":"Дата","weekday":"День","type":"Вид","schedule":"Графік","breaks":"Перерви","work":"Робота","drive":"Кер.","over":"Надуроч.","route":"Маршрут","vehicle":"Авто","notes":"Примітка","mode":"Режим"}
        widths={"id":40,"date":85,"weekday":55,"type":120,"schedule":170,"breaks":90,"work":65,"drive":65,"over":75,"route":150,"vehicle":100,"notes":180,"mode":190}
        for c in cols:
            self.work_tree.heading(c,text=heads[c]); self.work_tree.column(c,width=widths[c],anchor="w")
        work_y=ttk.Scrollbar(self.tab_work,orient="vertical",command=self.work_tree.yview)
        work_x=ttk.Scrollbar(self.tab_work,orient="horizontal",command=self.work_tree.xview)
        self.work_tree.configure(yscrollcommand=work_y.set,xscrollcommand=work_x.set)
        work_x.pack(side="bottom",fill="x",padx=10,pady=(0,5))
        work_y.pack(side="right",fill="y",pady=5)
        self.work_tree.pack(side="left",fill="both",expand=True,padx=(10,0),pady=5)
        self.work_tree.bind("<Double-1>",self.edit_work_row)
        self.work_tree.bind("<Control-c>",lambda e:self.copy_work_day())
        self.work_tree.bind("<Control-v>",lambda e:self.paste_work_day())
        self.work_clipboard=None

    def show_monthly_work_balance(self):
        """Місячний робочий табель / баланс часу по всіх водіях."""
        if hasattr(self,"monthly_balance_win") and self.monthly_balance_win.winfo_exists():
            self.monthly_balance_win.lift()
            self.refresh_monthly_work_balance()
            return

        win=tk.Toplevel(self)
        self.monthly_balance_win=win
        win.title("Місячний табель / баланс робочого часу")
        win.geometry("1450x760")
        win.minsize(950,520)
        win.resizable(True,True)

        top=ttk.Frame(win,padding=8)
        top.pack(fill="x")

        today=date.today()
        self.monthly_balance_year=tk.IntVar(
            value=int(self.year_var.get()) if hasattr(self,"year_var") else today.year
        )
        self.monthly_balance_month=tk.IntVar(
            value=int(self.month_var.get()) if hasattr(self,"month_var") else today.month
        )
        self.monthly_balance_active_only=tk.BooleanVar(value=True)
        self.monthly_balance_last_pdf=None
        self.monthly_balance_last_xlsx=None

        ttk.Label(top,text="Рік:").pack(side="left")
        ttk.Spinbox(
            top,from_=2020,to=2100,textvariable=self.monthly_balance_year,width=7,
            command=self.refresh_monthly_work_balance
        ).pack(side="left",padx=(3,8))

        ttk.Label(top,text="Місяць:").pack(side="left")
        ttk.Spinbox(
            top,from_=1,to=12,textvariable=self.monthly_balance_month,width=4,
            command=self.refresh_monthly_work_balance
        ).pack(side="left",padx=(3,8))

        ttk.Checkbutton(
            top,text="Тільки активні водії",
            variable=self.monthly_balance_active_only,
            command=self.refresh_monthly_work_balance
        ).pack(side="left",padx=(4,10))

        ttk.Button(
            top,text="Оновити",command=self.refresh_monthly_work_balance
        ).pack(side="left",padx=3)
        ttk.Button(
            top,text="Excel — редагувати",command=self.save_monthly_work_balance_xlsx
        ).pack(side="left",padx=(12,3))
        ttk.Button(
            top,text="PDF — друк",command=self.save_monthly_work_balance_pdf
        ).pack(side="left",padx=3)
        ttk.Button(
            top,text="Відкрити PDF",command=self.open_monthly_work_balance_pdf
        ).pack(side="left",padx=3)

        ttk.Label(
            win,
            text=(
                "У клітинках робочих днів показуються тільки фактично відпрацьовані години "
                "(наприклад 8:00 або 7:30). Без часу початку/закінчення зміни. "
                "PDF та Excel розраховані на A4, альбомна орієнтація, з поділом місяця на три частини."
            ),
            foreground="gray",
            wraplength=1350,
            justify="left"
        ).pack(fill="x",padx=10,pady=(0,6))

        frame=ttk.Frame(win)
        frame.pack(fill="both",expand=True,padx=10,pady=5)

        style=ttk.Style(win)
        style.configure("MonthlyBalance.Treeview",font=("TkDefaultFont",10),rowheight=28)
        style.configure("MonthlyBalance.Treeview.Heading",font=("TkDefaultFont",10,"bold"))

        self.monthly_balance_tree=ttk.Treeview(
            frame,show="headings",style="MonthlyBalance.Treeview"
        )
        ybar=ttk.Scrollbar(frame,orient="vertical",command=self.monthly_balance_tree.yview)
        xbar=ttk.Scrollbar(frame,orient="horizontal",command=self.monthly_balance_tree.xview)
        self.monthly_balance_tree.configure(yscrollcommand=ybar.set,xscrollcommand=xbar.set)

        self.monthly_balance_tree.grid(row=0,column=0,sticky="nsew")
        ybar.grid(row=0,column=1,sticky="ns")
        xbar.grid(row=1,column=0,sticky="ew")
        frame.rowconfigure(0,weight=1)
        frame.columnconfigure(0,weight=1)

        self.monthly_balance_summary_var=tk.StringVar()
        ttk.Label(
            win,textvariable=self.monthly_balance_summary_var,
            font=("TkDefaultFont",9,"bold")
        ).pack(fill="x",padx=10,pady=(2,2))

        ttk.Label(
            win,
            text="Позначення: В - вихідний; Відп - відпустка; Лік - лікарняний; Відпч - відпочинок; Гот - готовність; Інш - інша робота.",
            foreground="gray"
        ).pack(fill="x",padx=10,pady=(0,8))

        self.refresh_monthly_work_balance()

    def refresh_monthly_work_balance(self):
        if not hasattr(self,"monthly_balance_tree") or not self.monthly_balance_tree.winfo_exists():
            return
        try:
            y=int(self.monthly_balance_year.get())
            m=int(self.monthly_balance_month.get())
            if not 1<=m<=12:
                raise ValueError
        except Exception:
            return

        data=collect_monthly_work_balance(
            y,m,active_only=bool(self.monthly_balance_active_only.get())
        )
        days=data["days"]

        columns=["driver"]+[f"d{d.day}" for d in days]+["days","work","over"]
        self.monthly_balance_tree["columns"]=columns

        self.monthly_balance_tree.heading("driver",text="Водій")
        self.monthly_balance_tree.column(
            "driver",width=220,minwidth=170,anchor="w",stretch=False
        )

        for d in days:
            c=f"d{d.day}"
            wd=["Пн","Вт","Ср","Чт","Пт","Сб","Нд"][d.weekday()]
            self.monthly_balance_tree.heading(c,text=f"{d.day} {wd}")
            self.monthly_balance_tree.column(
                c,width=66,minwidth=58,anchor="center",stretch=False
            )

        for c,label,width in [
            ("days","Роб. днів",75),
            ("work","Відпрацьовано",100),
            ("over","Надурочні",90),
        ]:
            self.monthly_balance_tree.heading(c,text=label)
            self.monthly_balance_tree.column(
                c,width=width,minwidth=width,anchor="center",stretch=False
            )

        for item in self.monthly_balance_tree.get_children():
            self.monthly_balance_tree.delete(item)

        total_work_days=0
        total_work_min=0
        total_over_min=0
        for idx,dr in enumerate(data["drivers"]):
            vals=[dr["name"]]+dr["cells"]+[
                dr["work_days"],
                minutes_hhmm(dr["work_min"]),
                minutes_hhmm(dr["over_min"]),
            ]
            tag="even" if idx%2==0 else "odd"
            self.monthly_balance_tree.insert("","end",values=vals,tags=(tag,))
            total_work_days += dr["work_days"]
            total_work_min += dr["work_min"]
            total_over_min += dr["over_min"]

        self.monthly_balance_tree.tag_configure("even",background="#FAFAFA")
        self.monthly_balance_tree.tag_configure("odd",background="#FFFFFF")

        self.monthly_balance_summary_var.set(
            f"{month_name_ua(m)} {y}: водіїв {len(data['drivers'])}    "
            f"Робочих днів сумарно: {total_work_days}    "
            f"Відпрацьовано: {minutes_hhmm(total_work_min)}    "
            f"Надурочні: {minutes_hhmm(total_over_min)}"
        )

    def save_monthly_work_balance_pdf(self):
        y=int(self.monthly_balance_year.get())
        m=int(self.monthly_balance_month.get())
        path=filedialog.asksaveasfilename(
            parent=self.monthly_balance_win,
            title="Зберегти місячний табель робочого часу",
            initialdir=str(OUTPUT_DIR),
            initialfile=f"Табель_робочого_часу_{y}_{m:02d}.pdf",
            defaultextension=".pdf",
            filetypes=[("PDF","*.pdf")]
        )
        if not path:
            return
        try:
            export_monthly_work_balance_pdf(
                y,m,path,active_only=bool(self.monthly_balance_active_only.get())
            )
            self.monthly_balance_last_pdf=Path(path)
            messagebox.showinfo(
                "Місячний табель",
                f"PDF створено:\n{path}",
                parent=self.monthly_balance_win
            )
        except Exception as e:
            messagebox.showerror(
                "Помилка PDF",
                str(e),
                parent=self.monthly_balance_win
            )

    def open_monthly_work_balance_pdf(self):
        path=getattr(self,"monthly_balance_last_pdf",None)
        if not path or not Path(path).exists():
            y=int(self.monthly_balance_year.get())
            m=int(self.monthly_balance_month.get())
            path=OUTPUT_DIR/f"Табель_робочого_часу_{y}_{m:02d}.pdf"
            try:
                export_monthly_work_balance_pdf(
                    y,m,path,active_only=bool(self.monthly_balance_active_only.get())
                )
                self.monthly_balance_last_pdf=Path(path)
            except Exception as e:
                messagebox.showerror(
                    "Помилка PDF",str(e),parent=self.monthly_balance_win
                )
                return
        try:
            if os.name=="nt":
                os.startfile(str(path))
            else:
                open_external(path)
        except Exception as e:
            messagebox.showerror(
                "Помилка",str(e),parent=self.monthly_balance_win
            )

    def save_monthly_work_balance_xlsx(self):
        y=int(self.monthly_balance_year.get())
        m=int(self.monthly_balance_month.get())
        path=filedialog.asksaveasfilename(
            parent=self.monthly_balance_win,
            title="Зберегти редагований місячний табель",
            initialdir=str(OUTPUT_DIR),
            initialfile=f"Табель_робочого_часу_{y}_{m:02d}.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Excel","*.xlsx")]
        )
        if not path:
            return
        try:
            export_monthly_work_balance_xlsx(
                y,m,path,active_only=bool(self.monthly_balance_active_only.get())
            )
            self.monthly_balance_last_xlsx=Path(path)
            if os.name=="nt":
                os.startfile(str(path))
            else:
                open_external(path)
        except Exception as e:
            messagebox.showerror(
                "Помилка Excel",str(e),parent=self.monthly_balance_win
            )

    def build_schedule(self):
        """Графічний планувальник одного календарного дня по всіх активних водіях."""
        top=ttk.Frame(self.tab_schedule); top.pack(fill="x",padx=10,pady=8)
        self.schedule_date_var=tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
        ttk.Label(top,text="Дата:").pack(side="left")
        ttk.Entry(top,textvariable=self.schedule_date_var,width=13).pack(side="left",padx=5)
        calendar_button(top,self.schedule_date_var).pack(side="left",padx=2)
        ttk.Button(top,text="◀ День",command=lambda:self.shift_schedule_day(-1)).pack(side="left",padx=3)
        ttk.Button(top,text="Сьогодні",command=self.schedule_today).pack(side="left",padx=3)
        ttk.Button(top,text="День ▶",command=lambda:self.shift_schedule_day(1)).pack(side="left",padx=3)
        ttk.Button(top,text="Оновити",command=self.refresh_schedule).pack(side="left",padx=5)
        ttk.Button(top,text="Додати / редагувати період",command=self.schedule_add_period).pack(side="left",padx=5)
        ttk.Button(
            top,
            text="Місячний графік змінності",
            command=self.show_monthly_shift_schedule
        ).pack(side="left",padx=5)
        ttk.Label(self.tab_schedule,text="План дня по всіх активних водіях. Періоди відпочинку, роботи, керування та готовності відображаються на одній часовій шкалі.",foreground="gray").pack(anchor="w",padx=12)

        legend=ttk.Frame(self.tab_schedule); legend.pack(fill="x",padx=12,pady=(4,2))
        for txt in ("Робота","Керування","Відпочинок","Готовність","Інше"):
            ttk.Label(legend,text=f"■ {txt}").pack(side="left",padx=8)

        body=ttk.Frame(self.tab_schedule); body.pack(fill="both",expand=True,padx=10,pady=5)
        self.schedule_canvas=tk.Canvas(body,background="white",highlightthickness=1)
        yscroll=ttk.Scrollbar(body,orient="vertical",command=self.schedule_canvas.yview)
        xscroll=ttk.Scrollbar(body,orient="horizontal",command=self.schedule_canvas.xview)
        self.schedule_canvas.configure(yscrollcommand=yscroll.set,xscrollcommand=xscroll.set)
        self.schedule_canvas.grid(row=0,column=0,sticky="nsew")
        yscroll.grid(row=0,column=1,sticky="ns")
        xscroll.grid(row=1,column=0,sticky="ew")
        body.rowconfigure(0,weight=1); body.columnconfigure(0,weight=1)
        self.schedule_canvas.bind("<Configure>",lambda e:self.refresh_schedule())
        self.schedule_canvas.bind("<Double-1>",self.schedule_double_click)
        self.schedule_canvas.bind("<Button-1>",self.schedule_click)
        self.schedule_hitboxes=[]
        self.schedule_driver_rows=[]
        self.after(100,self.refresh_schedule)

    def show_monthly_shift_schedule(self):
        """Місячний графік змінності по всіх активних водіях."""
        if hasattr(self,"monthly_shift_win") and self.monthly_shift_win.winfo_exists():
            self.monthly_shift_win.lift()
            self.refresh_monthly_shift_schedule()
            return

        win=tk.Toplevel(self)
        self.monthly_shift_win=win
        win.title("Місячний графік змінності водіїв")
        win.geometry("1450x760")
        win.minsize(950,520)
        win.resizable(True,True)

        top=ttk.Frame(win,padding=8)
        top.pack(fill="x")

        today=date.today()
        self.monthly_shift_year=tk.IntVar(
            value=int(self.year_var.get()) if hasattr(self,"year_var") else today.year
        )
        self.monthly_shift_month=tk.IntVar(
            value=int(self.month_var.get()) if hasattr(self,"month_var") else today.month
        )
        self.monthly_shift_active_only=tk.BooleanVar(value=True)
        self.monthly_shift_last_pdf=None
        self.monthly_shift_last_detail_pdf=None
        self.monthly_shift_last_xlsx=None

        ttk.Label(top,text="Рік:").pack(side="left")
        ttk.Spinbox(
            top,from_=2020,to=2100,textvariable=self.monthly_shift_year,width=7,
            command=self.refresh_monthly_shift_schedule
        ).pack(side="left",padx=(3,8))

        ttk.Label(top,text="Місяць:").pack(side="left")
        ttk.Spinbox(
            top,from_=1,to=12,textvariable=self.monthly_shift_month,width=4,
            command=self.refresh_monthly_shift_schedule
        ).pack(side="left",padx=(3,8))

        ttk.Checkbutton(
            top,text="Тільки активні водії",
            variable=self.monthly_shift_active_only,
            command=self.refresh_monthly_shift_schedule
        ).pack(side="left",padx=(4,10))

        ttk.Button(
            top,text="Оновити",command=self.refresh_monthly_shift_schedule
        ).pack(side="left",padx=3)
        ttk.Button(
            top,text="Excel — редагувати",command=self.save_monthly_shift_schedule_xlsx
        ).pack(side="left",padx=(12,3))
        ttk.Button(
            top,text="PDF — графік",command=self.save_monthly_shift_schedule_pdf
        ).pack(side="left",padx=3)
        ttk.Button(
            top,text="PDF — деталізація",command=self.save_monthly_shift_detail_pdf
        ).pack(side="left",padx=3)
        ttk.Button(
            top,text="Відкрити графік PDF",command=self.open_monthly_shift_schedule_pdf
        ).pack(side="left",padx=3)

        ttk.Label(
            win,
            text=(
                "Місячна матриця формується з уже введених табелів. "
                "Графік розрахований на стандартний офісний папір A4, альбомна орієнтація. "
                "PDF графіка автоматично ділить місяць на три читабельні частини (для 31 дня: 1–11, 12–21, 22–31). "
                "«PDF — деталізація» формує окремий A4-документ з точними частинами змін, перервами, "
                "робочим часом, часом керування, маршрутом та автомобілем. "
                "Для ручного редагування використовуйте «Excel — редагувати»."
            ),
            foreground="gray",
            wraplength=1350,
            justify="left"
        ).pack(fill="x",padx=10,pady=(0,6))

        frame=ttk.Frame(win)
        frame.pack(fill="both",expand=True,padx=10,pady=5)

        style=ttk.Style(win)
        style.configure("MonthlyShift.Treeview",font=("TkDefaultFont",10),rowheight=30)
        style.configure("MonthlyShift.Treeview.Heading",font=("TkDefaultFont",10,"bold"))
        self.monthly_shift_tree=ttk.Treeview(frame,show="headings",style="MonthlyShift.Treeview")
        ybar=ttk.Scrollbar(frame,orient="vertical",command=self.monthly_shift_tree.yview)
        xbar=ttk.Scrollbar(frame,orient="horizontal",command=self.monthly_shift_tree.xview)
        self.monthly_shift_tree.configure(yscrollcommand=ybar.set,xscrollcommand=xbar.set)

        self.monthly_shift_tree.grid(row=0,column=0,sticky="nsew")
        ybar.grid(row=0,column=1,sticky="ns")
        xbar.grid(row=1,column=0,sticky="ew")
        frame.rowconfigure(0,weight=1)
        frame.columnconfigure(0,weight=1)

        self.monthly_shift_summary_var=tk.StringVar()
        ttk.Label(
            win,textvariable=self.monthly_shift_summary_var,
            font=("TkDefaultFont",9,"bold")
        ).pack(fill="x",padx=10,pady=(2,2))

        ttk.Label(
            win,
            text="Позначення: В - вихідний; Відп - відпустка; Лік - лікарняний; Відпч - відпочинок; Гот - готовність.",
            foreground="gray"
        ).pack(fill="x",padx=10,pady=(0,8))

        self.refresh_monthly_shift_schedule()

    def refresh_monthly_shift_schedule(self):
        if not hasattr(self,"monthly_shift_tree") or not self.monthly_shift_tree.winfo_exists():
            return
        try:
            y=int(self.monthly_shift_year.get())
            m=int(self.monthly_shift_month.get())
            if not 1<=m<=12:
                raise ValueError
        except Exception:
            return

        data=collect_monthly_shift_schedule(
            y,m,active_only=bool(self.monthly_shift_active_only.get())
        )
        days=data["days"]

        columns=["driver"]+[f"d{d.day}" for d in days]+["days","work","drive"]
        self.monthly_shift_tree["columns"]=columns

        self.monthly_shift_tree.heading("driver",text="Водій")
        self.monthly_shift_tree.column("driver",width=220,minwidth=170,anchor="w",stretch=False)

        for d in days:
            c=f"d{d.day}"
            wd=["Пн","Вт","Ср","Чт","Пт","Сб","Нд"][d.weekday()]
            self.monthly_shift_tree.heading(c,text=f"{d.day} {wd}")
            self.monthly_shift_tree.column(c,width=82,minwidth=65,anchor="center",stretch=False)

        for c,label,width in [
            ("days","Роб. днів",75),
            ("work","Робота",80),
            ("drive","Кер.",80),
        ]:
            self.monthly_shift_tree.heading(c,text=label)
            self.monthly_shift_tree.column(c,width=width,minwidth=width,anchor="center",stretch=False)

        for item in self.monthly_shift_tree.get_children():
            self.monthly_shift_tree.delete(item)

        total_work_days=0
        total_work_min=0
        total_drive_min=0
        for idx,dr in enumerate(data["drivers"]):
            vals=[dr["name"]]
            for cell in dr["cells"]:
                vals.append(cell.replace("\n"," / "))
            vals += [
                dr["work_days"],
                minutes_hhmm(dr["work_min"]),
                minutes_hhmm(dr["drive_min"]),
            ]
            tag="even" if idx%2==0 else "odd"
            self.monthly_shift_tree.insert("","end",values=vals,tags=(tag,))
            total_work_days+=dr["work_days"]
            total_work_min+=dr["work_min"]
            total_drive_min+=dr["drive_min"]

        self.monthly_shift_tree.tag_configure("even",background="#FAFAFA")
        self.monthly_shift_tree.tag_configure("odd",background="#FFFFFF")

        self.monthly_shift_summary_var.set(
            f"Водіїв: {len(data['drivers'])}    "
            f"Робочих днів сумарно: {total_work_days}    "
            f"Робота: {minutes_hhmm(total_work_min)}    "
            f"Керування: {minutes_hhmm(total_drive_min)}"
        )

    def save_monthly_shift_schedule_xlsx(self):
        y=int(self.monthly_shift_year.get())
        m=int(self.monthly_shift_month.get())
        path=filedialog.asksaveasfilename(
            parent=self.monthly_shift_win,
            title="Зберегти редагований графік змінності",
            initialdir=str(OUTPUT_DIR),
            initialfile=f"Графік_змінності_{y}_{m:02d}.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Excel","*.xlsx")]
        )
        if not path:
            return
        try:
            export_monthly_shift_schedule_xlsx(
                y,m,path,active_only=bool(self.monthly_shift_active_only.get())
            )
            self.monthly_shift_last_xlsx=Path(path)
            if os.name=="nt":
                os.startfile(str(path))
            else:
                open_external(path)
        except Exception as e:
            messagebox.showerror(
                "Помилка Excel",
                str(e),
                parent=self.monthly_shift_win
            )

    def save_monthly_shift_detail_pdf(self):
        y=int(self.monthly_shift_year.get())
        m=int(self.monthly_shift_month.get())
        path=filedialog.asksaveasfilename(
            parent=self.monthly_shift_win,
            title="Зберегти деталізацію графіка змінності",
            initialdir=str(OUTPUT_DIR),
            initialfile=f"Деталізація_графіка_змінності_{y}_{m:02d}.pdf",
            defaultextension=".pdf",
            filetypes=[("PDF","*.pdf")]
        )
        if not path:
            return
        try:
            export_monthly_shift_detail_pdf(
                y,m,path,active_only=bool(self.monthly_shift_active_only.get())
            )
            self.monthly_shift_last_detail_pdf=Path(path)
            messagebox.showinfo(
                "Деталізація графіка",
                f"PDF деталізації створено:\n{path}",
                parent=self.monthly_shift_win
            )
        except Exception as e:
            messagebox.showerror(
                "Помилка PDF деталізації",
                str(e),
                parent=self.monthly_shift_win
            )

    def _monthly_shift_default_pdf(self):
        y=int(self.monthly_shift_year.get())
        m=int(self.monthly_shift_month.get())
        return OUTPUT_DIR / f"Графік_змінності_{y}_{m:02d}.pdf"

    def save_monthly_shift_schedule_pdf(self):
        y=int(self.monthly_shift_year.get())
        m=int(self.monthly_shift_month.get())
        path=filedialog.asksaveasfilename(
            parent=self.monthly_shift_win,
            title="Зберегти місячний графік змінності",
            initialdir=str(OUTPUT_DIR),
            initialfile=f"Графік_змінності_{y}_{m:02d}.pdf",
            defaultextension=".pdf",
            filetypes=[("PDF","*.pdf")]
        )
        if not path:
            return
        try:
            export_monthly_shift_schedule_pdf(
                y,m,path,active_only=bool(self.monthly_shift_active_only.get())
            )
            self.monthly_shift_last_pdf=Path(path)
            messagebox.showinfo("Графік змінності",f"PDF створено:\n{path}",parent=self.monthly_shift_win)
        except Exception as e:
            messagebox.showerror("Помилка PDF",str(e),parent=self.monthly_shift_win)

    def open_monthly_shift_schedule_pdf(self):
        y=int(self.monthly_shift_year.get())
        m=int(self.monthly_shift_month.get())
        path=self.monthly_shift_last_pdf or self._monthly_shift_default_pdf()
        path=Path(path)
        try:
            if not path.exists():
                export_monthly_shift_schedule_pdf(
                    y,m,path,active_only=bool(self.monthly_shift_active_only.get())
                )
            self.monthly_shift_last_pdf=path
            if os.name=="nt":
                os.startfile(str(path))
            else:
                open_external(path)
        except Exception as e:
            messagebox.showerror(
                "Графік змінності",
                f"Не вдалося відкрити PDF:\n{e}",
                parent=self.monthly_shift_win
            )

    def _schedule_parse_date(self):
        try:
            return datetime.strptime(self.schedule_date_var.get().strip(),"%d.%m.%Y").date()
        except ValueError:
            messagebox.showerror("Помилка","Дата має бути у форматі ДД.ММ.РРРР.",parent=self)
            return None

    def schedule_today(self):
        self.schedule_date_var.set(date.today().strftime("%d.%m.%Y")); self.refresh_schedule()

    def shift_schedule_day(self,delta):
        d=self._schedule_parse_date()
        if not d: return
        self.schedule_date_var.set((d+timedelta(days=delta)).strftime("%d.%m.%Y")); self.refresh_schedule()

    def _schedule_activity_group(self, activity):
        a=(activity or "").strip().lower()
        if "керув" in a:
            return "Керування"
        if "відпоч" in a or "перерв" in a:
            return "Відпочинок"
        if "готов" in a or "доступ" in a:
            return "Готовність"
        if "робот" in a or "інш" in a:
            return "Робота"
        return "Інше"

    def _schedule_fill(self, group):
        # Tkinter Canvas uses the default palette; these are only activity categories.
        return {"Робота":"#9ec5fe","Керування":"#80d8a8","Відпочинок":"#d9d9d9","Готовність":"#f4c77a","Інше":"#c7b7e8"}.get(group,"#c7b7e8")

    def refresh_schedule(self):
        if not hasattr(self,"schedule_canvas"): return
        d=self._schedule_parse_date()
        if not d: return
        c=self.schedule_canvas; c.delete("all"); self.schedule_hitboxes=[]; self.schedule_driver_rows=[]
        con=db()
        drivers=con.execute("SELECT * FROM drivers WHERE active=1 ORDER BY last_name,first_name,middle_name").fetchall()
        rows=con.execute("SELECT * FROM worklog WHERE work_date=?",(d.isoformat(),)).fetchall()
        by_driver={r["driver_id"]:r for r in rows}
        seg_by={}
        if rows:
            ids=[r["id"] for r in rows]
            q=",".join("?" for _ in ids)
            segs=con.execute(f"SELECT * FROM work_segments WHERE worklog_id IN ({q}) ORDER BY segment_no",ids).fetchall()
            for seg in segs: seg_by.setdefault(seg["worklog_id"],[]).append(seg)
        con.close()
        left=185; hour_w=72; top=48; row_h=54; width=left+24*hour_w+20
        height=max(top+len(drivers)*row_h+30,300)
        c.configure(scrollregion=(0,0,width,height))
        c.create_rectangle(0,0,width,top,fill="#f3f3f3",outline="")
        c.create_text(12,top/2,text=d.strftime("%d.%m.%Y"),anchor="w",font=("TkDefaultFont",10,"bold"))
        for h in range(25):
            x=left+h*hour_w
            c.create_line(x,0,x,height,fill="#d0d0d0")
            if h<24:
                c.create_text(x+3,top/2,text=f"{h:02d}:00",anchor="w",font=("TkDefaultFont",9))
        c.create_line(0,top,width,top,fill="#999")
        for idx,dr in enumerate(drivers):
            y=top+idx*row_h; self.schedule_driver_rows.append((y,y+row_h,dr["id"],dr))
            if idx%2==0: c.create_rectangle(0,y,width,y+row_h,fill="#fafafa",outline="")
            full=(f"{dr['last_name']} {dr['first_name']} {dr['middle_name']}").strip()
            c.create_text(12,y+row_h/2,text=full,anchor="w",font=("TkDefaultFont",9,"bold"))
            wl=by_driver.get(dr["id"])
            segs=seg_by.get(wl["id"],[]) if wl else []
            if not segs and wl and wl["start_time"] and wl["end_time"]:
                segs=[{"start_time":wl["start_time"],"end_time":wl["end_time"],"activity_type":wl["day_type"],"work_hours":wl["work_hours"],"driving_hours":wl["driving_hours"],"note":wl["notes"]}]
            for seg in segs:
                try: sm=time_to_minutes(seg["start_time"]); em=time_to_minutes(seg["end_time"])
                except Exception: continue
                if em<=sm: em+=1440
                # For a day view, show only the part intersecting 00:00–24:00.
                for base_sm,base_em in ((sm,em),(sm-1440,em-1440)):
                    vis_s=max(0,base_sm); vis_e=min(1440,base_em)
                    if vis_e<=vis_s: continue
                    x1=left+vis_s/60*hour_w; x2=left+vis_e/60*hour_w
                    group=self._schedule_activity_group(seg["activity_type"])
                    c.create_rectangle(x1,y+9,x2,y+row_h-9,fill=self._schedule_fill(group),outline="#777")
                    label=f"{seg['start_time']}–{seg['end_time']} {group}"
                    if x2-x1>95: c.create_text((x1+x2)/2,y+row_h/2,text=label,anchor="center",font=("TkDefaultFont",8))
                    seg_id = seg["id"] if "id" in seg.keys() else None
                    self.schedule_hitboxes.append((x1,y+9,x2,y+row_h-9,dr["id"],d,seg_id,wl["id"] if wl else None))
        c.create_line(0,top+len(drivers)*row_h,width,top+len(drivers)*row_h,fill="#999")

    def _schedule_hit(self,event):
        c=self.schedule_canvas; x=c.canvasx(event.x); y=c.canvasy(event.y)
        for hb in self.schedule_hitboxes:
            x1,y1,x2,y2,driver_id,d,seg_id,wl_id=hb
            if x1<=x<=x2 and y1<=y<=y2: return hb
        return None

    def schedule_click(self,event):
        hb=self._schedule_hit(event)
        if hb: self.schedule_canvas.configure(cursor="hand2")
        else: self.schedule_canvas.configure(cursor="arrow")

    def schedule_double_click(self,event):
        hb=self._schedule_hit(event)
        if hb:
            _,_,_,_,driver_id,d,_,wl_id=hb
            self.open_schedule_worklog(driver_id,d)
            return
        d=self._schedule_parse_date()
        if not d: return
        # Double click on a driver's empty row opens that day's editor.
        y=self.schedule_canvas.canvasy(event.y)
        for y1,y2,driver_id,dr in self.schedule_driver_rows:
            if y1<=y<=y2:
                self.open_schedule_worklog(driver_id,d)
                return

    def open_schedule_worklog(self,driver_id,work_date):
        self.driver_id=driver_id
        con=db()
        d=con.execute("SELECT * FROM drivers WHERE id=?",(driver_id,)).fetchone()
        con.close()
        if d:
            label=next((k for k,v in getattr(self,"work_driver_map",{}).items() if v==driver_id), self.driver_full_name(d))
            self.work_driver_var.set(label)
        self.year_var.set(work_date.year); self.month_var.set(work_date.month)
        self.refresh_month()
        target=work_date.strftime("%d.%m.%Y")
        for item in self.work_tree.get_children():
            if self.work_tree.item(item,"values")[1]==target:
                self.work_tree.selection_set(item); self.work_tree.focus(item); self.work_tree.see(item); self.edit_work_row(); break
        # Keep the graphical planner visible after closing the editor.
        self.refresh_schedule()

    def schedule_add_period(self):
        d=self._schedule_parse_date()
        if not d: return
        # If a driver is currently selected, use it; otherwise ask from active drivers.
        if self.driver_id:
            self.open_schedule_worklog(self.driver_id,d)
            return
        con=db(); drivers=con.execute("SELECT * FROM drivers WHERE active=1 ORDER BY last_name,first_name").fetchall(); con.close()
        if not drivers:
            messagebox.showwarning("Графік","Спочатку додайте активного водія.",parent=self); return
        win=tk.Toplevel(self); win.title("Вибір водія"); win.geometry("430x170"); win.transient(self); win.grab_set()
        var=tk.StringVar(value=self.driver_full_name(drivers[0])); labels=[self.driver_full_name(x) for x in drivers]; mapping={self.driver_full_name(x):x["id"] for x in drivers}
        ttk.Label(win,text="Водій").pack(anchor="w",padx=12,pady=(15,5)); ttk.Combobox(win,textvariable=var,values=labels,state="readonly",width=42).pack(padx=12)
        def go():
            did=mapping.get(var.get()); win.destroy()
            if did: self.open_schedule_worklog(did,d)
        ttk.Button(win,text="Відкрити",command=go).pack(anchor="e",padx=12,pady=14)

    def get_work_segments(self, worklog_id):
        if not worklog_id: return []
        con=db(); rows=con.execute("SELECT * FROM work_segments WHERE worklog_id=? ORDER BY segment_no",(worklog_id,)).fetchall(); con.close()
        return rows

    def refresh_month(self):
        if not hasattr(self,"work_tree") or not self.driver_id: return
        for x in self.work_tree.get_children(): self.work_tree.delete(x)
        y,m=int(self.year_var.get()),int(self.month_var.get())
        con=db(); rows=con.execute("SELECT * FROM worklog WHERE driver_id=? AND substr(work_date,1,7)=? ORDER BY work_date",(self.driver_id,f"{y:04d}-{m:02d}")).fetchall(); con.close()
        existing={r["work_date"]:r for r in rows}
        for d in month_dates(y,m):
            r=existing.get(d.isoformat())
            segs=self.get_work_segments(r["id"]) if r else []
            schedule=segments_summary(segs) if segs else (f"{r['start_time']}-{r['end_time']}" if r and r["start_time"] else "")
            breaks=gaps_summary(segs)
            vals=(r["id"] if r else "",d.strftime("%d.%m.%Y"),["Пн","Вт","Ср","Чт","Пт","Сб","Нд"][d.weekday()],r["day_type"] if r else ("Вихідний" if d.weekday()>=5 else "Робота"),schedule,breaks,
                  hours_value_hhmm(r["work_hours"]) if r else "0:00",
                  hours_value_hhmm(r["driving_hours"]) if r else "0:00",
                  hours_value_hhmm(r["overtime_hours"]) if r else "0:00",
                  r["route_name"] if r and "route_name" in r.keys() else "",r["vehicle"] if r else "",r["notes"] if r else "",
                  work_mode_label(r["accounting_mode"] if r and "accounting_mode" in r.keys() else WORK_MODE_MANUAL))
            self.work_tree.insert("","end",values=vals)

    def edit_work_row(self,_=None):
        sel=self.work_tree.selection()
        if not sel or not self.driver_id: return
        vals=self.work_tree.item(sel[0],"values")
        work_id=int(vals[0]) if vals[0] else None
        date_text=vals[1]
        con=db(); existing=con.execute("SELECT * FROM worklog WHERE id=?",(work_id,)).fetchone() if work_id else None
        templates=con.execute("SELECT * FROM route_templates WHERE active=1 ORDER BY name").fetchall()
        routes=con.execute("SELECT * FROM routes WHERE active=1 ORDER BY name").fetchall()
        vehicles=con.execute("SELECT * FROM vehicles WHERE active=1 ORDER BY name,plate").fetchall()
        con.close()
        old_segments=self.get_work_segments(work_id) if work_id else []
        win=tk.Toplevel(self); win.title("Запис робочого часу"); win.geometry("930x600"); win.transient(self); win.grab_set()
        top=ttk.Frame(win); top.pack(fill="x",padx=10,pady=8)
        day_var=tk.StringVar(value=date_text); type_var=tk.StringVar(value=(existing["day_type"] if existing else vals[3]))
        existing_route_id=(existing["route_id"] if existing and "route_id" in existing.keys() else None)
        route_map={self.route_label(r):r for r in routes}
        route_var=tk.StringVar(value=next((self.route_label(r) for r in routes if r["id"]==existing_route_id), (existing["route_name"] if existing and "route_name" in existing.keys() else vals[9])))
        existing_vehicle_id=(existing["vehicle_id"] if existing and "vehicle_id" in existing.keys() else None)
        vehicle_var=tk.StringVar(value=(existing["vehicle"] if existing else vals[10]))
        vehicle_labels=[self.vehicle_label(v) for v in vehicles]
        vehicle_map={self.vehicle_label(v):v for v in vehicles}
        vehicle_label_var=tk.StringVar(value=next((self.vehicle_label(v) for v in vehicles if v["id"]==existing_vehicle_id), vehicle_var.get()))
        notes_var=tk.StringVar(value=(existing["notes"] if existing else vals[11]))
        shift_var=tk.StringVar(value=(existing["shift_type"] if existing and "shift_type" in existing.keys() else ("Розділена на частини" if len(old_segments)>1 else "Безперервна")))
        existing_mode=(existing["accounting_mode"] if existing and "accounting_mode" in existing.keys() else WORK_MODE_MANUAL) or WORK_MODE_MANUAL
        mode_var=tk.StringVar(value=work_mode_label(existing_mode))
        template_id_var=tk.IntVar(value=(existing["template_id"] if existing and "template_id" in existing.keys() and existing["template_id"] else 0))
        ttk.Label(top,text="Дата").grid(row=0,column=0,padx=4,pady=4,sticky="w")
        ttk.Entry(top,textvariable=day_var,width=14).grid(row=0,column=1,padx=4,sticky="w")
        calendar_button(top,day_var).grid(row=0,column=2,padx=(0,8),sticky="w")

        ttk.Label(top,text="Вид").grid(row=0,column=3,padx=(8,4),sticky="w")
        ttk.Combobox(
            top,textvariable=type_var,values=DAY_TYPES,state="readonly",width=18
        ).grid(row=0,column=4,padx=4,sticky="w")

        ttk.Label(top,text="Тип зміни").grid(row=0,column=5,padx=(8,4),sticky="w")
        ttk.Combobox(
            top,textvariable=shift_var,
            values=["Безперервна","Розділена на частини"],
            state="readonly",width=22
        ).grid(row=0,column=6,padx=4,sticky="w")

        ttk.Label(top,text="Маршрут").grid(row=1,column=0,padx=4,pady=4,sticky="w")
        ttk.Combobox(
            top,textvariable=route_var,values=list(route_map.keys()),
            state="readonly",width=28
        ).grid(row=1,column=1,columnspan=2,padx=4,sticky="ew")

        ttk.Label(top,text="Автомобіль").grid(row=1,column=3,padx=(8,4),sticky="w")
        ttk.Combobox(
            top,textvariable=vehicle_label_var,values=vehicle_labels,
            state="readonly",width=30
        ).grid(row=1,column=4,padx=4,sticky="ew")

        ttk.Label(top,text="Примітка").grid(row=1,column=5,padx=(8,4),sticky="w")
        ttk.Entry(top,textvariable=notes_var,width=28).grid(row=1,column=6,padx=4,sticky="ew")

        ttk.Label(top,text="Режим обліку").grid(row=2,column=0,padx=4,pady=4,sticky="w")
        ttk.Combobox(
            top,textvariable=mode_var,
            values=list(WORK_MODE_BY_LABEL.keys()),
            state="readonly",width=34
        ).grid(row=2,column=1,columnspan=2,padx=4,sticky="w")
        ttk.Label(
            top,
            text="ТАХО: весь час поза інтервалами маршруту контролюється бланками. Без тахо: лише 8 год у табелі.",
            foreground="gray"
        ).grid(row=2,column=3,columnspan=4,padx=(8,4),sticky="w")

        top.columnconfigure(1,weight=1)
        top.columnconfigure(4,weight=1)
        top.columnconfigure(6,weight=1)

        apply_frame=ttk.Frame(win); apply_frame.pack(fill="x",padx=10,pady=(2,6))
        template_names=[t["name"] for t in templates]; template_var=tk.StringVar()
        ttk.Label(apply_frame,text="Шаблон маршруту:").pack(side="left")
        tcb=ttk.Combobox(apply_frame,textvariable=template_var,values=template_names,state="readonly",width=34); tcb.pack(side="left",padx=6)

        cols=("no","start","end","work","drive","activity","note")
        tree=ttk.Treeview(win,columns=cols,show="headings",height=11)
        heads={"no":"№","start":"Початок","end":"Кінець","work":"Робота, год","drive":"Керування, год","activity":"Тип","note":"Примітка"}
        widths={"no":40,"start":90,"end":90,"work":100,"drive":110,"activity":150,"note":280}
        for c in cols: tree.heading(c,text=heads[c]); tree.column(c,width=widths[c],anchor="w")
        tree.pack(fill="both",expand=True,padx=10,pady=5)
        summary_var=tk.StringVar(value="")
        ttk.Label(win,textvariable=summary_var,foreground="gray").pack(anchor="w",padx=12,pady=3)

        seg_data=[]
        def load_segments(items):
            seg_data.clear()
            for r in items:
                seg_data.append({"start_time":r["start_time"],"end_time":r["end_time"],"work_hours":r["work_hours"],"driving_hours":r["driving_hours"],"activity_type":r["activity_type"],"note":r["note"]})
            redraw()
        def redraw():
            for x in tree.get_children(): tree.delete(x)
            total_min=0; drive_min=0
            for i,r in enumerate(seg_data,1):
                tree.insert("","end",values=(i,r["start_time"],r["end_time"],
                    hours_value_hhmm(r["work_hours"]),hours_value_hhmm(r["driving_hours"]),
                    r["activity_type"],r["note"]))
                total_min += hours_value_to_minutes(r["work_hours"])
                drive_min += hours_value_to_minutes(r["driving_hours"])
            br=gaps_summary(seg_data)
            summary_var.set(
                f"Всього роботи: {minutes_dual(total_min)} | "
                f"керування: {minutes_dual(drive_min)} | "
                f"перерви між частинами: {br or '—'}"
            )
        def segment_form(item=None, index=None):
            sw=tk.Toplevel(win); sw.title("Частина робочої зміни"); sw.geometry("520x390"); sw.transient(win); sw.grab_set()
            vals=item or {"start_time":"08:00","end_time":"17:00","work_hours":"8","driving_hours":"0","activity_type":"Робота","note":""}
            vv={}
            for k in ["start_time","end_time","work_hours","driving_hours","activity_type","note"]:
                val=vals.get(k,"")
                if k in ("work_hours","driving_hours"):
                    val=hours_value_hhmm(val)
                vv[k]=tk.StringVar(value=str(val))
            fields=[("Початок (ГГ:ХХ)","start_time"),("Кінець (ГГ:ХХ)","end_time"),
                    ("Робота (ГГ:ХХ або десяткові)","work_hours"),
                    ("Керування (ГГ:ХХ або десяткові)","driving_hours"),
                    ("Тип роботи","activity_type"),("Примітка","note")]
            for i,(lbl,key) in enumerate(fields):
                ttk.Label(sw,text=lbl).grid(row=i,column=0,sticky="w",padx=10,pady=7)
                w=ttk.Combobox(sw,textvariable=vv[key],values=DAY_TYPES,state="readonly",width=34) if key=="activity_type" else ttk.Entry(sw,textvariable=vv[key],width=36)
                w.grid(row=i,column=1,padx=10,pady=7)
            def calc(_=None):
                try: vv["work_hours"].set(minutes_hhmm(duration_minutes(vv["start_time"].get(),vv["end_time"].get())))
                except Exception: pass
            ttk.Button(sw,text="Розрахувати години з часу",command=calc).grid(row=6,column=1,sticky="w",padx=10,pady=6)
            def save_seg():
                try:
                    time_to_minutes(vv["start_time"].get()); time_to_minutes(vv["end_time"].get())
                    wh_min=hours_value_to_minutes(vv["work_hours"].get())
                    dh_min=hours_value_to_minutes(vv["driving_hours"].get())
                except Exception:
                    messagebox.showerror(
                        "Помилка",
                        "Перевірте час і тривалість. Можна вводити 2:30 або 2.5.",
                        parent=sw
                    ); return
                data={k:vv[k].get().strip() for k in vv}
                data["work_hours"]=minutes_to_db_hours(wh_min)
                data["driving_hours"]=minutes_to_db_hours(dh_min)
                if index is None: seg_data.append(data)
                else: seg_data[index]=data
                redraw(); sw.destroy()
            ttk.Button(sw,text="Зберегти",command=save_seg).grid(row=7,column=1,sticky="e",padx=10,pady=12)
        def selected_seg_index():
            s=tree.selection()
            return int(tree.item(s[0],"values")[0])-1 if s else None
        btns=ttk.Frame(win); btns.pack(fill="x",padx=10,pady=5)
        ttk.Button(btns,text="Додати частину",command=lambda:segment_form()).pack(side="left",padx=3)
        ttk.Button(btns,text="Редагувати частину",command=lambda:(segment_form(seg_data[selected_seg_index()],selected_seg_index()) if selected_seg_index() is not None else None)).pack(side="left",padx=3)
        def delete_seg():
            i=selected_seg_index()
            if i is not None: seg_data.pop(i); redraw()
        ttk.Button(btns,text="Видалити частину",command=delete_seg).pack(side="left",padx=3)
        def apply_template():
            name=template_var.get()
            t=next((x for x in templates if x["name"]==name),None)
            if not t: return
            con=db(); ts=con.execute("SELECT * FROM route_template_segments WHERE template_id=? ORDER BY segment_no",(t["id"],)).fetchall(); con.close()
            route_var.set(next((self.route_label(r) for r in routes if r["id"]==t["route_id"]), t["route_name"] or "")) if "route_id" in t.keys() else route_var.set(t["route_name"] or "")
            tv=next((v for v in vehicles if v["id"]==(t["vehicle_id"] if "vehicle_id" in t.keys() else None)),None)
            vehicle_label_var.set(self.vehicle_label(tv) if tv else (t["vehicle"] or ""))
            vehicle_var.set(t["vehicle"] or "")
            shift_var.set(t["shift_type"] or ("Розділена на частини" if len(ts)>1 else "Безперервна"))
            template_id_var.set(t["id"])
            mode_var.set(WORK_MODE_LABELS[WORK_MODE_TACHO])
            load_segments(ts)

        def set_no_tacho_8h():
            mode_var.set(WORK_MODE_LABELS[WORK_MODE_NO_TACHO])
            type_var.set("Робота")
            template_id_var.set(0)
            template_var.set("")
            route_var.set("")
            shift_var.set("Безперервна")
            seg_data.clear()
            redraw()
            summary_var.set("Без тахографа: стандартний робочий день 8:00. Час маршруту та керування не деталізуються.")

        ttk.Button(apply_frame,text="Застосувати шаблон",command=apply_template).pack(side="left")
        ttk.Button(
            apply_frame,text="Без тахо — 8 год",command=set_no_tacho_8h
        ).pack(side="left",padx=(10,3))
        if old_segments:
            load_segments(old_segments)
        elif existing and existing["start_time"]:
            load_segments([{"start_time":existing["start_time"],"end_time":existing["end_time"],"work_hours":existing["work_hours"],"driving_hours":existing["driving_hours"],"activity_type":existing["day_type"],"note":existing["notes"]}])
        else:
            redraw()
        def save():
            try: work_date=datetime.strptime(day_var.get().strip(),"%d.%m.%Y").strftime("%Y-%m-%d")
            except ValueError: messagebox.showerror("Помилка","Дата має бути у форматі ДД.ММ.РРРР.",parent=win); return
            if seg_data:
                try:
                    for r in seg_data:
                        time_to_minutes(r["start_time"]); time_to_minutes(r["end_time"])
                        hours_value_to_minutes(r["work_hours"]); hours_value_to_minutes(r["driving_hours"])
                except Exception: messagebox.showerror("Помилка","Перевірте частини зміни.",parent=win); return
            mode_code=WORK_MODE_BY_LABEL.get(mode_var.get(),WORK_MODE_MANUAL)
            if mode_code==WORK_MODE_NO_TACHO:
                # Без тахографа — не вигадуємо години маршруту.
                # У табелі зберігаємо лише стандартні 8 год роботи.
                seg_data.clear()
                total_work_min=8*60
                total_drive_min=0
                start=""
                end=""
                type_var.set("Робота")
                template_id_var.set(0)
                shift_var.set("Безперервна")
            else:
                total_work_min=sum(hours_value_to_minutes(r["work_hours"]) for r in seg_data)
                total_drive_min=sum(hours_value_to_minutes(r["driving_hours"]) for r in seg_data)
                start=seg_data[0]["start_time"] if seg_data else ""
                end=seg_data[-1]["end_time"] if seg_data else ""

            total_work=minutes_to_db_hours(total_work_min)
            total_drive=minutes_to_db_hours(total_drive_min)
            selected_vehicle=vehicle_map.get(vehicle_label_var.get())
            vehicle_text=self.vehicle_label(selected_vehicle) if selected_vehicle else vehicle_label_var.get().strip()
            vehicle_id=selected_vehicle["id"] if selected_vehicle else None

            # Не читаємо надурочні з відформатованої клітинки Treeview
            # ("0:00", "1:30" тощо). Для наявного запису зберігаємо
            # точне значення з БД; для нового дня — 0.
            overtime_value=(existing["overtime_hours"] if existing else 0) or 0

            con=db()
            route_text=route_var.get().strip() if mode_code!=WORK_MODE_NO_TACHO else ""
            route_id_value=(route_map[route_var.get()]["id"] if route_var.get() in route_map else None) if mode_code!=WORK_MODE_NO_TACHO else None
            vehicle_text=vehicle_text if mode_code!=WORK_MODE_NO_TACHO else vehicle_text

            con.execute("""INSERT INTO worklog(
                driver_id,work_date,day_type,start_time,end_time,work_hours,driving_hours,
                overtime_hours,vehicle,notes,route_name,route_id,template_id,shift_type,
                vehicle_id,accounting_mode
            )
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(driver_id,work_date) DO UPDATE SET
                    day_type=excluded.day_type,
                    start_time=excluded.start_time,
                    end_time=excluded.end_time,
                    work_hours=excluded.work_hours,
                    driving_hours=excluded.driving_hours,
                    overtime_hours=excluded.overtime_hours,
                    vehicle=excluded.vehicle,
                    notes=excluded.notes,
                    route_name=excluded.route_name,
                    route_id=excluded.route_id,
                    template_id=excluded.template_id,
                    shift_type=excluded.shift_type,
                    vehicle_id=excluded.vehicle_id,
                    accounting_mode=excluded.accounting_mode""",
                (
                    self.driver_id,work_date,type_var.get(),start,end,total_work,total_drive,
                    overtime_value,vehicle_text,notes_var.get().strip(),route_text,
                    route_id_value,template_id_var.get() or None,shift_var.get(),
                    vehicle_id,mode_code
                ))
            wl=con.execute("SELECT id FROM worklog WHERE driver_id=? AND work_date=?",(self.driver_id,work_date)).fetchone()[0]
            con.execute("DELETE FROM work_segments WHERE worklog_id=?",(wl,))
            for i,r in enumerate(seg_data,1):
                con.execute("INSERT INTO work_segments(worklog_id,segment_no,start_time,end_time,work_hours,driving_hours,activity_type,note) VALUES(?,?,?,?,?,?,?,?)",(wl,i,r["start_time"],r["end_time"],float(r["work_hours"]),float(r["driving_hours"]),r["activity_type"],r["note"]))
            con.commit(); con.close(); win.destroy(); self.refresh_month(); self.refresh_schedule()
        ttk.Button(win,text="Зберегти запис",command=save).pack(side="right",padx=12,pady=10)

    def _worklog_by_id(self, wid):
        if not wid: return None
        con=db(); r=con.execute("SELECT * FROM worklog WHERE id=?",(wid,)).fetchone(); con.close(); return r

    def copy_work_day(self):
        sel=self.work_tree.selection()
        if not sel:
            messagebox.showwarning("Копіювання","Виберіть день у табелі."); return
        vals=self.work_tree.item(sel[0],"values")
        wid=int(vals[0]) if vals[0] else None
        r=self._worklog_by_id(wid)
        if not r:
            self.work_clipboard={"empty":True,"day_type":vals[3]}
        else:
            segs=self.get_work_segments(wid)
            self.work_clipboard={
                "day_type":r["day_type"],"start_time":r["start_time"],"end_time":r["end_time"],
                "work_hours":r["work_hours"],"driving_hours":r["driving_hours"],
                "overtime_hours":r["overtime_hours"],"vehicle":r["vehicle"],
                "vehicle_id":r["vehicle_id"] if "vehicle_id" in r.keys() else None,
                "notes":r["notes"],
                "route_name":r["route_name"] if "route_name" in r.keys() else "",
                "route_id":r["route_id"] if "route_id" in r.keys() else None,
                "template_id":r["template_id"] if "template_id" in r.keys() else None,
                "shift_type":r["shift_type"] if "shift_type" in r.keys() else "Безперервна",
                "accounting_mode":r["accounting_mode"] if "accounting_mode" in r.keys() else WORK_MODE_MANUAL,
                "segments":[dict(x) for x in segs]
            }
        self.clipboard_clear(); self.clipboard_append("driver_worktime_day")
        messagebox.showinfo("Копіювання","День скопійовано. Виберіть одну або кілька дат і натисніть Ctrl+V / «Вставити день».")

    def paste_work_day(self):
        if not self.work_clipboard:
            try:
                if self.clipboard_get() != "driver_worktime_day": return
            except Exception: return
        sel=self.work_tree.selection()
        if not sel:
            messagebox.showwarning("Вставлення","Виберіть одну або кілька дат у табелі."); return
        clip=self.work_clipboard
        dates=[self.work_tree.item(i,"values")[1] for i in sel]
        con=db()
        for date_text in dates:
            try: wd=datetime.strptime(date_text,"%d.%m.%Y").strftime("%Y-%m-%d")
            except ValueError: continue
            con.execute("""INSERT INTO worklog(
                driver_id,work_date,day_type,start_time,end_time,work_hours,driving_hours,
                overtime_hours,vehicle,notes,route_name,route_id,template_id,shift_type,
                vehicle_id,accounting_mode
            )
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(driver_id,work_date) DO UPDATE SET
                    day_type=excluded.day_type,start_time=excluded.start_time,end_time=excluded.end_time,
                    work_hours=excluded.work_hours,driving_hours=excluded.driving_hours,
                    overtime_hours=excluded.overtime_hours,vehicle=excluded.vehicle,
                    notes=excluded.notes,route_name=excluded.route_name,route_id=excluded.route_id,
                    template_id=excluded.template_id,shift_type=excluded.shift_type,
                    vehicle_id=excluded.vehicle_id,accounting_mode=excluded.accounting_mode""",
                (
                    self.driver_id,wd,clip.get("day_type","Робота"),clip.get("start_time",""),
                    clip.get("end_time",""),clip.get("work_hours",0),clip.get("driving_hours",0),
                    clip.get("overtime_hours",0),clip.get("vehicle",""),clip.get("notes",""),
                    clip.get("route_name",""),clip.get("route_id"),clip.get("template_id"),
                    clip.get("shift_type","Безперервна"),clip.get("vehicle_id"),
                    clip.get("accounting_mode",WORK_MODE_MANUAL)
                ))
            wid=con.execute("SELECT id FROM worklog WHERE driver_id=? AND work_date=?",(self.driver_id,wd)).fetchone()[0]
            con.execute("DELETE FROM work_segments WHERE worklog_id=?",(wid,))
            for i,r in enumerate(clip.get("segments",[]),1):
                con.execute("INSERT INTO work_segments(worklog_id,segment_no,start_time,end_time,work_hours,driving_hours,activity_type,note) VALUES(?,?,?,?,?,?,?,?)",(wid,i,r["start_time"],r["end_time"],r["work_hours"],r["driving_hours"],r["activity_type"],r["note"]))
        con.commit(); con.close(); self.refresh_month()

    def save_work_row(self): self.edit_work_row()

    def autofill(self):
        if not self.driver_id:
            messagebox.showwarning("Увага","Спочатку виберіть водія.")
            return

        y,m=int(self.year_var.get()),int(self.month_var.get())

        if not messagebox.askyesno(
            "Небезпечна масова дія",
            f"Позначити робочі дні {m:02d}.{y} як «Без тахо — стандартні 8 год»?\n\n"
            "Час маршруту/керування не задається: у табелі буде лише 8:00.\n"
            "УВАГА: існуючі записи робочих днів цього водія можуть бути змінені.\n"
            "Продовжити?",
            parent=self
        ):
            return

        con=db()
        for d in month_dates(y,m):
            if d.weekday()<5:
                con.execute("""INSERT INTO worklog(
                    driver_id,work_date,day_type,start_time,end_time,work_hours,driving_hours,
                    route_name,route_id,template_id,shift_type,accounting_mode
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(driver_id,work_date) DO UPDATE SET
                        day_type=excluded.day_type,
                        start_time=excluded.start_time,
                        end_time=excluded.end_time,
                        work_hours=excluded.work_hours,
                        driving_hours=excluded.driving_hours,
                        route_name=excluded.route_name,
                        route_id=excluded.route_id,
                        template_id=excluded.template_id,
                        shift_type=excluded.shift_type,
                        accounting_mode=excluded.accounting_mode""",
                    (
                        self.driver_id,d.isoformat(),"Робота","","",8,0,
                        "",None,None,"Безперервна",WORK_MODE_NO_TACHO
                    ))
                wl=con.execute(
                    "SELECT id FROM worklog WHERE driver_id=? AND work_date=?",
                    (self.driver_id,d.isoformat())
                ).fetchone()[0]
                con.execute("DELETE FROM work_segments WHERE worklog_id=?",(wl,))
        con.commit(); con.close(); self.refresh_month()

    def current_rows(self):
        con=db(); rows=con.execute("SELECT * FROM worklog WHERE driver_id=? AND substr(work_date,1,7)=? ORDER BY work_date",(self.driver_id,f"{int(self.year_var.get()):04d}-{int(self.month_var.get()):02d}")).fetchall(); con.close(); return rows

    def export_current(self,kind):
        if not self.driver_id:
            messagebox.showwarning("Увага","Спочатку виберіть водія.")
            return

        # Водій у вкладці «Табель» вибирається власним списком.
        # Тому не можна залежати від того, чи виділений той самий рядок
        # у вкладці «Водії»: на старті driver_id вже може бути заданий,
        # а Treeview ще не має selection().
        d=self.driver_by_id(self.driver_id)
        if not d:
            messagebox.showerror(
                "Помилка",
                "Не вдалося знайти вибраного водія у базі. Оновіть список водіїв."
            )
            return

        rows=self.current_rows()
        y,m=int(self.year_var.get()),int(self.month_var.get())
        safe_last=(d["last_name"] or "Водій").strip()
        name=f"Табель_{safe_last}_{y}_{m:02d}"
        path=OUTPUT_DIR/(name+(".xlsx" if kind=="xlsx" else ".pdf"))
        try:
            if kind=="xlsx":
                export_xlsx(d,y,m,rows,path)
            else:
                export_pdf(d,y,m,rows,path)
            messagebox.showinfo("Готово",f"Файл створено:\n{path}")
        except Exception as e:
            messagebox.showerror("Помилка",str(e))

    def _analysis_segments_map(self, con, rows):
        ids=[r["id"] for r in rows if r and r["id"]]
        result={}
        if not ids:
            return result
        q=",".join("?" for _ in ids)
        for s in con.execute(
            f"SELECT * FROM work_segments WHERE worklog_id IN ({q}) ORDER BY worklog_id, segment_no",
            ids
        ).fetchall():
            result.setdefault(s["worklog_id"], []).append(s)
        return result

    def _row_start_end_dt(self, row, segments):
        if row is None:
            return None, None
        d=datetime.strptime(row["work_date"], "%Y-%m-%d").date()
        pieces=[]
        if segments:
            for s in segments:
                try:
                    sm=time_to_minutes(s["start_time"])
                    em=time_to_minutes(s["end_time"])
                except Exception:
                    continue
                st=datetime.combine(d, datetime.min.time()) + timedelta(minutes=sm)
                en=datetime.combine(d, datetime.min.time()) + timedelta(minutes=em)
                if em <= sm:
                    en += timedelta(days=1)
                pieces.append((st,en))
        elif row["start_time"] and row["end_time"]:
            try:
                sm=time_to_minutes(row["start_time"]); em=time_to_minutes(row["end_time"])
                st=datetime.combine(d, datetime.min.time()) + timedelta(minutes=sm)
                en=datetime.combine(d, datetime.min.time()) + timedelta(minutes=em)
                if em <= sm:
                    en += timedelta(days=1)
                pieces.append((st,en))
            except Exception:
                pass
        if not pieces:
            return None, None
        return min(x[0] for x in pieces), max(x[1] for x in pieces)

    @staticmethod
    def _segment_overlaps_night(start_time, end_time):
        try:
            sm=time_to_minutes(start_time); em=time_to_minutes(end_time)
        except Exception:
            return False
        if em <= sm:
            em += 1440
        # 22:00-24:00 or 00:00-06:00, with overnight normalization.
        ranges=[(1320,1440),(0,360),(1440,1800)]
        return any(max(sm,a) < min(em,b) for a,b in ranges)

    @staticmethod
    def _segment_is_work(activity):
        a=(activity or "").lower()
        return not any(x in a for x in ("відпоч", "вихід", "відпуст", "лікар", "готов", "доступ"))

    @staticmethod
    def _segment_is_driving(activity):
        a=(activity or "").lower()
        return "керув" in a

    def _row_minutes_exact(self, row, segments=None):
        segments = segments or []
        if segments:
            work=sum(hours_value_to_minutes(s["work_hours"]) for s in segments)
            drive=sum(hours_value_to_minutes(s["driving_hours"]) for s in segments)
        else:
            work=hours_value_to_minutes(row["work_hours"])
            drive=hours_value_to_minutes(row["driving_hours"])
        over=hours_value_to_minutes(row["overtime_hours"])
        return work,drive,over

    def _row_internal_rest_minutes(self, segments):
        return gaps_minutes(segments)

    def _driving_break_control_for_row(self, row, segments):
        """Контроль перерв у КЕРУВАННІ за нашими частинами зміни.

        Наші частини — технічний спосіб розбити день на відрізки,
        щоб задати точний час керування та проміжки між відрізками.
        Вони НЕ означають автоматично "розділений щоденний відпочинок"
        у термінах Положення №340.
        """
        if not segments:
            drive=hours_value_to_minutes(row["driving_hours"])
            return {"max_continuous_drive":drive,"warnings":[],"breaks":[]}

        ordered=sorted(segments,key=lambda s:time_to_minutes(s["start_time"]))
        accumulated=0
        max_accum=0
        split15=False
        warnings=[]
        break_rows=[]

        for i,s in enumerate(ordered):
            if i>0:
                prev=ordered[i-1]
                prev_end=time_to_minutes(prev["end_time"])
                cur_start=time_to_minutes(s["start_time"])
                if cur_start<=prev_end:
                    cur_start+=24*60
                gap=cur_start-prev_end

                status="не зараховуємо"
                resets=False
                if gap>=45:
                    status="повна перерва у керуванні ≥45 хв"
                    accumulated=0
                    split15=False
                    resets=True
                elif split15 and gap>=30:
                    status="друга частина ≥30 хв; схема 15+30 виконана"
                    accumulated=0
                    split15=False
                    resets=True
                elif gap>=15:
                    if not split15:
                        status="перша частина перерви ≥15 хв"
                        split15=True
                    else:
                        status="ще одна перерва 15–29 хв; 15+30 ще не завершено"
                else:
                    status="<15 хв; для перерви у керуванні не зараховується"

                break_rows.append({
                    "after":prev["end_time"],
                    "before":s["start_time"],
                    "minutes":gap,
                    "status":status,
                    "resets":resets,
                })

            drive_min=hours_value_to_minutes(s["driving_hours"])
            span=duration_minutes(s["start_time"],s["end_time"])
            if drive_min>span:
                warnings.append(
                    f"{row['work_date']}: у частині {s['start_time']}–{s['end_time']} "
                    f"керування {minutes_hhmm(drive_min)} більше тривалості самої частини "
                    f"{minutes_hhmm(span)}."
                )

            accumulated+=drive_min
            max_accum=max(max_accum,accumulated)

            if accumulated>270:
                warnings.append(
                    f"{row['work_date']}: накопичено {minutes_hhmm(accumulated)} керування "
                    f"до/в межах частини {s['start_time']}–{s['end_time']} без завершеної "
                    "перерви 45 хв або 15+30."
                )

        return {
            "max_continuous_drive":max_accum,
            "warnings":warnings,
            "breaks":break_rows,
        }

    def calculate_work_analysis(self):
        """Попередній автоматичний контроль за Положенням №340.
        Розрахунки виконуються у хвилинах, а не у сотих частках години.
        """
        if not self.driver_id:
            return None

        y,m=int(self.year_var.get()), int(self.month_var.get())
        month_start=date(y,m,1)
        month_end=month_dates(y,m)[-1]

        # Для тижневих показників — повні календарні тижні навколо місяця.
        range_start=month_start - timedelta(days=month_start.weekday())
        range_end=month_end + timedelta(days=(6-month_end.weekday()))

        # Для пошуку попереднього/наступного щотижневого відпочинку беремо ширше вікно.
        rest_start=month_start-timedelta(days=45)
        rest_end=month_end+timedelta(days=14)

        con=db()
        rows=con.execute(
            "SELECT * FROM worklog WHERE driver_id=? AND work_date BETWEEN ? AND ? ORDER BY work_date",
            (self.driver_id, rest_start.isoformat(), rest_end.isoformat())
        ).fetchall()
        seg_map=self._analysis_segments_map(con, rows)

        month_rows=[r for r in rows if month_start.isoformat() <= r["work_date"] <= month_end.isoformat()]

        total_work_min=total_drive_min=total_over_min=0
        work_days=0
        for r in month_rows:
            w,dv,ov=self._row_minutes_exact(r,seg_map.get(r["id"],[]))
            total_work_min+=w; total_drive_min+=dv; total_over_min+=ov
            if w>0: work_days+=1

        warnings=[]
        info=[]
        extended_by_week={}
        week_totals={}

        for r in rows:
            d=datetime.strptime(r["work_date"], "%Y-%m-%d").date()
            if not (range_start <= d <= range_end):
                continue
            work_min,drive_min,_=self._row_minutes_exact(r,seg_map.get(r["id"],[]))
            segs=seg_map.get(r["id"],[])

            monday=d-timedelta(days=d.weekday())
            w=week_totals.setdefault(monday,{"work":0,"drive":0})
            w["work"]+=work_min
            w["drive"]+=drive_min

            if drive_min>600:
                warnings.append(f"{d.strftime('%d.%m.%Y')}: керування {minutes_hhmm(drive_min)} — понад 10:00.")
            elif drive_min>540:
                extended_by_week[monday]=extended_by_week.get(monday,0)+1
                info.append(f"{d.strftime('%d.%m.%Y')}: подовжене керування {minutes_hhmm(drive_min)} (понад 9:00).")

            night=any(
                self._segment_is_work(s["activity_type"]) and
                self._segment_overlaps_night(s["start_time"],s["end_time"])
                for s in segs
            )
            if night and work_min>600:
                warnings.append(
                    f"{d.strftime('%d.%m.%Y')}: робота зачіпає нічний час; "
                    f"робочий час {minutes_hhmm(work_min)} > 10:00."
                )

            for s in segs:
                if not self._segment_is_work(s["activity_type"]):
                    continue
                try:
                    dur=duration_minutes(s["start_time"],s["end_time"])
                except Exception:
                    continue
                if dur>360:
                    warnings.append(
                        f"{d.strftime('%d.%m.%Y')}: безперервний робочий відрізок "
                        f"{s['start_time']}–{s['end_time']} = {minutes_hhmm(dur)} (>6:00); перевірити перерву."
                    )

            # Контроль 4:30 ведемо за числом у полі «Кер.» кожної
            # нашої частини зміни, а не за назвою типу роботи.
            drive_control=self._driving_break_control_for_row(r,segs)
            for msg in drive_control["warnings"]:
                warnings.append(msg.replace(r["work_date"],d.strftime("%d.%m.%Y")))

        for monday,n in sorted(extended_by_week.items()):
            if n>2:
                warnings.append(
                    f"Тиждень від {monday.strftime('%d.%m.%Y')}: {n} днів із керуванням понад 9:00; "
                    "потрібна перевірка ліміту двох подовжень."
                )

        sorted_weeks=sorted(week_totals)
        for monday in sorted_weeks:
            w=week_totals[monday]
            if w["work"]>3600:
                warnings.append(
                    f"Тиждень від {monday.strftime('%d.%m.%Y')}: робочий час "
                    f"{minutes_hhmm(w['work'])} > 60:00."
                )
            if w["drive"]>3360:
                warnings.append(
                    f"Тиждень від {monday.strftime('%d.%m.%Y')}: керування "
                    f"{minutes_hhmm(w['drive'])} > 56:00."
                )

        for a,b in zip(sorted_weeks,sorted_weeks[1:]):
            if b-a!=timedelta(days=7):
                continue
            drive2=week_totals[a]["drive"]+week_totals[b]["drive"]
            if drive2>5400:
                warnings.append(
                    f"Два тижні {a.strftime('%d.%m')}–{(b+timedelta(days=6)).strftime('%d.%m.%Y')}: "
                    f"керування {minutes_hhmm(drive2)} > 90:00."
                )

        # Фактичні/планові межі робочих змін.
        actual=[]
        for r in rows:
            st,en=self._row_start_end_dt(r,seg_map.get(r["id"],[]))
            if st and en:
                actual.append({
                    "start":st,"end":en,"row":r,
                    "segments":seg_map.get(r["id"],[])
                })
        actual.sort(key=lambda x:x["start"])

        daily_rests=[]
        weekly_rests=[]
        rest_events=[]

        for prev,next_ in zip(actual,actual[1:]):
            rest_min=int(round((next_["start"]-prev["end"]).total_seconds()/60))
            if rest_min<0:
                continue

            next_date=next_["start"].date()
            event={
                "start":prev["end"],"end":next_["start"],"minutes":rest_min,
                "next_date":next_date
            }

            # Внутрішні проміжки між НАШИМИ частинами зміни не є
            # автоматично частиною щоденного відпочинку 3+9.
            if rest_min>=24*60:
                event["kind"]="weekly_regular" if rest_min>=45*60 else "weekly_reduced"
                weekly_rests.append(event)
            elif rest_min>=11*60:
                event["kind"]="daily_regular"
                daily_rests.append(event)
            elif rest_min>=9*60:
                event["kind"]="daily_reduced"
                daily_rests.append(event)
            else:
                event["kind"]="daily_too_short"
                daily_rests.append(event)

            rest_events.append(event)

        # Щоденні відпочинки для вибраного місяця.
        reduced_since_weekly=0
        for ev in rest_events:
            if ev["kind"].startswith("weekly_"):
                reduced_since_weekly=0
                continue

            nd=ev["next_date"]
            if ev["kind"]=="daily_reduced":
                reduced_since_weekly+=1
                if month_start<=nd<=month_end:
                    info.append(
                        f"Перед {nd.strftime('%d.%m.%Y')}: скорочений щоденний відпочинок "
                        f"{minutes_hhmm(ev['minutes'])}; номер {reduced_since_weekly} після останнього щотижневого."
                    )
                    if reduced_since_weekly>3:
                        warnings.append(
                            f"Перед {nd.strftime('%d.%m.%Y')}: це вже {reduced_since_weekly}-й "
                            "скорочений щоденний відпочинок між щотижневими періодами (>3)."
                        )
            elif ev["kind"]=="daily_too_short" and month_start<=nd<=month_end:
                warnings.append(
                    f"Перед {nd.strftime('%d.%m.%Y')}: міжзмінний відпочинок "
                    f"{minutes_hhmm(ev['minutes'])} — менше 9:00."
                )

        # Щотижневий відпочинок: класифікація + правило шести 24-годинних періодів.
        for ev in weekly_rests:
            if ev["kind"]=="weekly_reduced":
                deficit=45*60-ev["minutes"]
                monday=ev["start"].date()-timedelta(days=ev["start"].date().weekday())
                due=monday+timedelta(days=27)
                if ev["end"].date()>=month_start and ev["start"].date()<=month_end:
                    info.append(
                        f"Щотижневий відпочинок {ev['start'].strftime('%d.%m %H:%M')}–"
                        f"{ev['end'].strftime('%d.%m %H:%M')}: {minutes_hhmm(ev['minutes'])}, скорочений. "
                        f"Нестача до 45:00 = {minutes_hhmm(deficit)}; компенсацію треба проконтролювати до {due.strftime('%d.%m.%Y')}."
                    )

        for prev,next_ in zip(weekly_rests,weekly_rests[1:]):
            span=int(round((next_["start"]-prev["end"]).total_seconds()/60))
            if span>6*24*60:
                # Показуємо лише якщо порушення стосується обраного місяця.
                if next_["start"].date()>=month_start and prev["end"].date()<=month_end:
                    warnings.append(
                        f"Між завершенням щотижневого відпочинку {prev['end'].strftime('%d.%m %H:%M')} "
                        f"і початком наступного {next_['start'].strftime('%d.%m %H:%M')} минуло "
                        f"{minutes_hhmm(span)} — більше шести 24-годинних періодів."
                    )

        # Вибрані для показу періоди відпочинку.
        daily_display=[
            ev for ev in daily_rests
            if month_start<=ev["next_date"]<=month_end
        ]
        weekly_display=[
            ev for ev in weekly_rests
            if ev["end"].date()>=month_start and ev["start"].date()<=month_end
        ]

        # Деталізація перерв у КЕРУВАННІ по днях вибраного місяця.
        driving_break_days=[]
        for r in month_rows:
            segs=seg_map.get(r["id"],[])
            ctl=self._driving_break_control_for_row(r,segs)
            driving_break_days.append({
                "date":datetime.strptime(r["work_date"],"%Y-%m-%d").date(),
                "total_drive":self._row_minutes_exact(r,segs)[1],
                "max_continuous_drive":ctl["max_continuous_drive"],
                "breaks":ctl["breaks"],
            })

        # Середня тривалість робочого часу за 4 календарні місяці — також у хвилинах.
        total_month_index=y*12+(m-1)-3
        y4=total_month_index//12
        m4=total_month_index%12+1
        four_start=date(y4,m4,1)
        four_rows=con.execute(
            "SELECT * FROM worklog WHERE driver_id=? AND work_date BETWEEN ? AND ? ORDER BY work_date",
            (self.driver_id,four_start.isoformat(),month_end.isoformat())
        ).fetchall()
        four_map=self._analysis_segments_map(con,four_rows)
        four_work_min=0
        for r in four_rows:
            w,_,_=self._row_minutes_exact(r,four_map.get(r["id"],[]))
            four_work_min+=w

        weeks=((month_end-four_start).days+1)/7
        avg4_min=(four_work_min/weeks) if weeks else 0
        if avg4_min>48*60:
            warnings.append(
                f"Середній робочий час за 4 календарні місяці ≈ "
                f"{minutes_hhmm(avg4_min)} на тиждень > 48:00."
            )

        con.close()

        transport_profile=current_transport_profile()

        return {
            "year":y,"month":m,
            "transport_profile":transport_profile,
            "work_days":work_days,
            "total_work_min":total_work_min,
            "total_drive_min":total_drive_min,
            "total_over_min":total_over_min,
            "avg4_min":avg4_min,
            "warnings":warnings,
            "info":info,
            "daily_rests":daily_display,
            "weekly_rests":weekly_display,
            "driving_break_days":driving_break_days,
        }

    def show_work_analysis(self):
        data=self.calculate_work_analysis()
        if data is None:
            messagebox.showwarning("Підсумки","Спочатку виберіть водія.",parent=self)
            return

        con=db()
        driver=con.execute("SELECT * FROM drivers WHERE id=?",(self.driver_id,)).fetchone()
        con.close()
        driver_name=self.driver_full_name(driver) if driver else self.work_driver_var.get()

        win=tk.Toplevel(self)
        win.title("Підсумки та контроль №340")
        win.geometry("980x760")
        win.minsize(760,520)
        win.transient(self)
        win.resizable(True,True)

        head=ttk.Frame(win,padding=10)
        head.pack(fill="x")

        title_frame=ttk.Frame(head)
        title_frame.pack(fill="x")
        ttk.Label(
            title_frame,
            text=f"Підсумки за {data['month']:02d}.{data['year']}",
            font=("TkDefaultFont",11,"bold")
        ).pack(side="left")

        def save_pdf():
            safe="".join(c if c.isalnum() or c in " _-" else "_" for c in driver_name).strip().replace(" ","_")
            default=f"Аналіз_340_{safe}_{data['year']}_{data['month']:02d}.pdf"
            path=filedialog.asksaveasfilename(
                parent=win,
                title="Зберегти аналіз у PDF",
                initialdir=str(OUTPUT_DIR),
                initialfile=default,
                defaultextension=".pdf",
                filetypes=[("PDF","*.pdf")]
            )
            if not path:
                return
            try:
                export_work_analysis_pdf(data,driver_name,path)
                messagebox.showinfo("PDF",f"Збережено:\n{path}",parent=win)
            except Exception as e:
                messagebox.showerror("Помилка PDF",str(e),parent=win)

        ttk.Button(title_frame,text="Зберегти PDF",command=save_pdf).pack(side="right",padx=(8,0))

        ttk.Label(
            head,
            text=(
                f"Водій: {driver_name}    "
                f"Профіль: {data.get('transport_profile', DEFAULT_TRANSPORT_PROFILE)}    "
                f"Робочих днів: {data['work_days']}    "
                f"Робота: {minutes_dual(data['total_work_min'])}    "
                f"Керування: {minutes_dual(data['total_drive_min'])}    "
                f"Надурочні: {minutes_dual(data['total_over_min'])}    "
                f"Середнє за 4 міс.: {minutes_hhmm(data['avg4_min'])}/тиж."
            )
        ).pack(anchor="w",pady=(5,0))

        legend=ttk.Frame(head)
        legend.pack(anchor="w",pady=(7,1))
        tk.Label(legend,text="  Норма  ",bg="#E6F4EA",fg="#1B5E20").pack(side="left",padx=(0,5))
        tk.Label(legend,text="  Увага  ",bg="#FFF4CC",fg="#7A4A00").pack(side="left",padx=5)
        tk.Label(legend,text="  Помилка / перевищення  ",bg="#FDE8E8",fg="#8A1C1C").pack(side="left",padx=5)
        tk.Label(legend,text="  Інформація  ",bg="#EAF2FF",fg="#174EA6").pack(side="left",padx=5)

        ttk.Label(
            head,
            text="Усі нормативні порівняння виконуються в цілих хвилинах. "
                 "Наприклад: 8:55 = 8.92 десяткових год; 8:30 = 8.50, а не 8.30.",
            foreground="gray"
        ).pack(anchor="w",pady=(5,0))

        body=ttk.Frame(win)
        body.pack(fill="both",expand=True,padx=10,pady=(0,10))
        txt=tk.Text(body,wrap="word",padx=8,pady=8)
        scr=ttk.Scrollbar(body,orient="vertical",command=txt.yview)
        txt.configure(yscrollcommand=scr.set)
        txt.grid(row=0,column=0,sticky="nsew")
        scr.grid(row=0,column=1,sticky="ns")
        body.rowconfigure(0,weight=1)
        body.columnconfigure(0,weight=1)

        # Кольорова схема.
        txt.tag_configure("heading",foreground="#1F4E79",font=("TkDefaultFont",10,"bold"),spacing1=9,spacing3=4)
        txt.tag_configure("subheading",foreground="#243B53",background="#EEF3F8",font=("TkDefaultFont",9,"bold"),spacing1=2,spacing3=2)
        txt.tag_configure("error",foreground="#8A1C1C",background="#FDE8E8",spacing1=2,spacing3=2,lmargin1=5,lmargin2=5)
        txt.tag_configure("warn",foreground="#7A4A00",background="#FFF4CC",spacing1=2,spacing3=2,lmargin1=5,lmargin2=5)
        txt.tag_configure("ok",foreground="#1B5E20",background="#E6F4EA",spacing1=2,spacing3=2,lmargin1=5,lmargin2=5)
        txt.tag_configure("info",foreground="#174EA6",background="#EAF2FF",spacing1=2,spacing3=2,lmargin1=5,lmargin2=5)
        txt.tag_configure("note",foreground="#555555",background="#F3F4F6",spacing1=2,spacing3=2,lmargin1=5,lmargin2=5)
        txt.tag_configure("normal",foreground="#222222",spacing1=1,spacing3=1,lmargin1=5,lmargin2=5)

        for kind,content in build_work_analysis_report_items(data):
            tag=kind if kind in ("heading","subheading","error","warn","ok","info","note","normal") else "normal"
            txt.insert("end",content+"\n",tag)

        txt.configure(state="disabled")

    def build_route_catalog(self):
        top=ttk.Frame(self.tab_route_catalog); top.pack(fill="x",padx=10,pady=8)
        ttk.Button(top,text="Новий маршрут",command=self.route_catalog_form).pack(side="left",padx=4)
        ttk.Button(top,text="Редагувати",command=self.edit_route_catalog).pack(side="left",padx=4)
        ttk.Button(top,text="Вимкнути",command=self.delete_route_catalog).pack(side="left",padx=4)
        ttk.Button(top,text="Оновити",command=self.load_route_catalog).pack(side="left",padx=4)
        ttk.Label(self.tab_route_catalog,text="Маршрути зберігаються в каталозі та вибираються у табелі й шаблонах. Історичні записи не змінюються при редагуванні каталогу.",foreground="gray").pack(anchor="w",padx=12,pady=(0,6))
        cols=("id","code","name","description","active")
        self.route_catalog_tree=ttk.Treeview(self.tab_route_catalog,columns=cols,show="headings",height=25)
        heads={"id":"ID","code":"Код / №","name":"Маршрут","description":"Опис / напрямок","active":"Статус"}
        widths={"id":45,"code":110,"name":230,"description":450,"active":90}
        for c in cols: self.route_catalog_tree.heading(c,text=heads[c]); self.route_catalog_tree.column(c,width=widths[c],anchor="w")
        routecat_y=ttk.Scrollbar(self.tab_route_catalog,orient="vertical",command=self.route_catalog_tree.yview)
        routecat_x=ttk.Scrollbar(self.tab_route_catalog,orient="horizontal",command=self.route_catalog_tree.xview)
        self.route_catalog_tree.configure(yscrollcommand=routecat_y.set,xscrollcommand=routecat_x.set)
        routecat_x.pack(side="bottom",fill="x",padx=10,pady=(0,5))
        routecat_y.pack(side="right",fill="y",pady=5)
        self.route_catalog_tree.pack(side="left",fill="both",expand=True,padx=(10,0),pady=5)
        self.load_route_catalog()

    def route_label(self,r):
        return " — ".join(x for x in [r["code"],r["name"]] if x) if r else ""

    def load_route_catalog(self):
        if not hasattr(self,"route_catalog_tree"): return
        for x in self.route_catalog_tree.get_children(): self.route_catalog_tree.delete(x)
        con=db(); rows=con.execute("SELECT * FROM routes ORDER BY active DESC,name").fetchall(); con.close()
        for r in rows: self.route_catalog_tree.insert("","end",values=(r["id"],r["code"],r["name"],r["description"],"Так" if r["active"] else "Ні"))

    def selected_route_catalog(self):
        sel=self.route_catalog_tree.selection()
        if not sel: return None
        rid=int(self.route_catalog_tree.item(sel[0],"values")[0])
        con=db(); r=con.execute("SELECT * FROM routes WHERE id=?",(rid,)).fetchone(); con.close(); return r

    def route_catalog_form(self,route=None):
        win=tk.Toplevel(self); win.title("Маршрут"); win.geometry("650x350"); win.transient(self); win.grab_set()
        fields=[("name","Назва маршруту"),("code","Код / № маршруту"),("description","Опис / напрямок")]
        vv={k:tk.StringVar(value=str(route[k] or "") if route else "") for k,_ in fields}
        for i,(k,lbl) in enumerate(fields):
            ttk.Label(win,text=lbl).grid(row=i,column=0,sticky="w",padx=10,pady=10); ttk.Entry(win,textvariable=vv[k],width=58).grid(row=i,column=1,padx=10,pady=10)
        active=tk.BooleanVar(value=bool(route["active"]) if route else True)
        ttk.Checkbutton(win,text="Активний маршрут",variable=active).grid(row=3,column=1,sticky="w",padx=10,pady=8)
        def save():
            if not vv["name"].get().strip(): messagebox.showerror("Помилка","Вкажіть назву маршруту.",parent=win); return
            con=db()
            try:
                data=(vv["name"].get().strip(),vv["code"].get().strip(),vv["description"].get().strip(),int(active.get()))
                if route: con.execute("UPDATE routes SET name=?,code=?,description=?,active=? WHERE id=?",data+(route["id"],))
                else: con.execute("INSERT INTO routes(name,code,description,active,created_at) VALUES(?,?,?,?,?)",data+(datetime.now().isoformat(timespec="seconds"),))
                con.commit()
            except sqlite3.IntegrityError: con.rollback(); messagebox.showerror("Помилка","Такий маршрут уже існує.",parent=win); return
            finally: con.close()
            win.destroy(); self.load_route_catalog(); self.load_route_templates()
        ttk.Button(win,text="Зберегти",command=save).grid(row=4,column=1,sticky="e",padx=10,pady=15)

    def edit_route_catalog(self):
        r=self.selected_route_catalog()
        if r: self.route_catalog_form(r)

    def delete_route_catalog(self):
        r=self.selected_route_catalog()
        if not r: return
        if messagebox.askyesno("Підтвердження","Вимкнути маршрут у каталозі? Історичні записи табеля залишаться.",parent=self):
            con=db(); con.execute("UPDATE routes SET active=0 WHERE id=?",(r["id"],)); con.commit(); con.close(); self.load_route_catalog()

    def build_routes(self):
        top=ttk.Frame(self.tab_routes); top.pack(fill="x",padx=10,pady=8)
        ttk.Button(top,text="Новий шаблон",command=self.route_template_form).pack(side="left",padx=4)
        ttk.Button(top,text="Редагувати",command=self.edit_route_template).pack(side="left",padx=4)
        ttk.Button(top,text="Видалити",command=self.delete_route_template).pack(side="left",padx=4)
        ttk.Button(top,text="Оновити",command=self.load_route_templates).pack(side="left",padx=4)
        ttk.Label(self.tab_routes,text="Шаблон зберігає маршрут, автомобіль і готові частини робочої зміни. У табелі його можна застосувати до конкретного дня та після цього змінити вручну.",foreground="gray").pack(anchor="w",padx=12,pady=(0,6))
        cols=("id","name","route","vehicle","shift","segments","notes")
        self.route_tree=ttk.Treeview(self.tab_routes,columns=cols,show="headings",height=25)
        heads={"id":"ID","name":"Назва шаблону","route":"Маршрут","vehicle":"Автомобіль","shift":"Тип зміни","segments":"Частини","notes":"Примітка"}
        for c in cols: self.route_tree.heading(c,text=heads[c]); self.route_tree.column(c,width={"id":45,"name":190,"route":180,"vehicle":130,"shift":150,"segments":260,"notes":250}[c],anchor="w")
        route_y=ttk.Scrollbar(self.tab_routes,orient="vertical",command=self.route_tree.yview)
        route_x=ttk.Scrollbar(self.tab_routes,orient="horizontal",command=self.route_tree.xview)
        self.route_tree.configure(yscrollcommand=route_y.set,xscrollcommand=route_x.set)
        route_x.pack(side="bottom",fill="x",padx=10,pady=(0,5))
        route_y.pack(side="right",fill="y",pady=5)
        self.route_tree.pack(side="left",fill="both",expand=True,padx=(10,0),pady=5)
        self.load_route_templates()

    def load_route_templates(self):
        if not hasattr(self,"route_tree"): return
        for x in self.route_tree.get_children(): self.route_tree.delete(x)
        con=db(); ts=con.execute("SELECT * FROM route_templates WHERE active=1 ORDER BY name").fetchall()
        for t in ts:
            segs=con.execute("SELECT * FROM route_template_segments WHERE template_id=? ORDER BY segment_no",(t["id"],)).fetchall()
            summary=" / ".join(f"{r['start_time']}-{r['end_time']} ({format_hours(r['work_hours'])} год)" for r in segs)
            self.route_tree.insert("","end",values=(t["id"],t["name"],t["route_name"],t["vehicle"],t["shift_type"],summary,t["notes"]))
        con.close()

    def selected_route_template(self):
        sel=self.route_tree.selection()
        if not sel: return None
        rid=int(self.route_tree.item(sel[0],"values")[0]); con=db(); t=con.execute("SELECT * FROM route_templates WHERE id=?",(rid,)).fetchone(); segs=con.execute("SELECT * FROM route_template_segments WHERE template_id=? ORDER BY segment_no",(rid,)).fetchall(); con.close(); return t,segs

    def route_template_form(self, existing=None):
        win=tk.Toplevel(self); win.title("Шаблон маршруту"); win.geometry("850x540"); win.transient(self); win.grab_set()
        vals={k:(existing[0][k] if existing else "") for k in ["name","route_name","vehicle","shift_type","notes"]}
        existing_route_id=(existing[0]["route_id"] if existing and "route_id" in existing[0].keys() else None)
        con=db(); routes=con.execute("SELECT * FROM routes WHERE active=1 ORDER BY name").fetchall(); vehicles=con.execute("SELECT * FROM vehicles WHERE active=1 ORDER BY name,plate").fetchall(); con.close()
        vehicle_map={self.vehicle_label(v):v for v in vehicles}
        existing_vid=(existing[0]["vehicle_id"] if existing and "vehicle_id" in existing[0].keys() else None)
        if not vals["shift_type"]: vals["shift_type"]="Безперервна"
        vv={k:tk.StringVar(value=vals[k] or "") for k in vals}
        fields=[("Назва шаблону","name"),("Примітка","notes")]
        for i,(lbl,key) in enumerate(fields):
            ttk.Label(win,text=lbl).grid(row=i,column=0,sticky="w",padx=10,pady=6); ttk.Entry(win,textvariable=vv[key],width=60).grid(row=i,column=1,columnspan=2,sticky="ew",padx=10,pady=6)
        ttk.Label(win,text="Маршрут").grid(row=2,column=0,sticky="w",padx=10,pady=6)
        route_map={self.route_label(r):r for r in routes}
        route_select=tk.StringVar(value=next((self.route_label(r) for r in routes if r["id"]==existing_route_id), vals["route_name"] or ""))
        ttk.Combobox(win,textvariable=route_select,values=list(route_map.keys()),state="readonly",width=57).grid(row=2,column=1,columnspan=2,sticky="ew",padx=10,pady=6)
        ttk.Label(win,text="Автомобіль").grid(row=3,column=0,sticky="w",padx=10,pady=6)
        vehicle_default=next((self.vehicle_label(v) for v in vehicles if v["id"]==existing_vid), vals["vehicle"] or "")
        vehicle_select=tk.StringVar(value=vehicle_default)
        ttk.Combobox(win,textvariable=vehicle_select,values=list(vehicle_map.keys()),state="readonly",width=57).grid(row=3,column=1,columnspan=2,sticky="ew",padx=10,pady=6)
        ttk.Label(win,text="Тип зміни").grid(row=4,column=0,sticky="w",padx=10,pady=6); ttk.Combobox(win,textvariable=vv["shift_type"],values=["Безперервна","Розділена на частини"],state="readonly",width=30).grid(row=4,column=1,sticky="w",padx=10)
        ttk.Label(win,text="Частини робочої зміни").grid(row=5,column=0,sticky="nw",padx=10,pady=8)
        cols=("no","start","end","work","drive","activity","note")
        tree=ttk.Treeview(win,columns=cols,show="headings",height=10)
        for c,h,w in [("no","№",40),("start","Поч.",75),("end","Кін.",75),("work","Робота",80),("drive","Кер.",80),("activity","Тип",120),("note","Примітка",240)]: tree.heading(c,text=h); tree.column(c,width=w)
        tree.grid(row=5,column=1,columnspan=2,sticky="nsew",padx=10,pady=8)
        seg_data=[]
        if existing:
            for r in existing[1]: seg_data.append({"start_time":r["start_time"],"end_time":r["end_time"],"work_hours":r["work_hours"],"driving_hours":r["driving_hours"],"activity_type":r["activity_type"],"note":r["note"]})
        def redraw():
            for x in tree.get_children(): tree.delete(x)
            for i,r in enumerate(seg_data,1):
                tree.insert("","end",values=(i,r["start_time"],r["end_time"],
                    hours_value_hhmm(r["work_hours"]),hours_value_hhmm(r["driving_hours"]),
                    r["activity_type"],r["note"]))
        def edit_seg(index=None):
            sw=tk.Toplevel(win); sw.title("Частина шаблону"); sw.geometry("500x360"); sw.transient(win); sw.grab_set()
            base=seg_data[index] if index is not None else {"start_time":"08:00","end_time":"17:00","work_hours":8,"driving_hours":0,"activity_type":"Робота","note":""}
            x={}
            for k in base:
                val=base[k]
                if k in ("work_hours","driving_hours"):
                    val=hours_value_hhmm(val)
                x[k]=tk.StringVar(value=str(val))
            for i,(lbl,key) in enumerate([("Початок","start_time"),("Кінець","end_time"),
                ("Робота (ГГ:ХХ або десяткові)","work_hours"),
                ("Керування (ГГ:ХХ або десяткові)","driving_hours"),
                ("Тип","activity_type"),("Примітка","note")]):
                ttk.Label(sw,text=lbl).grid(row=i,column=0,sticky="w",padx=10,pady=6); w=ttk.Combobox(sw,textvariable=x[key],values=DAY_TYPES,state="readonly",width=32) if key=="activity_type" else ttk.Entry(sw,textvariable=x[key],width=34); w.grid(row=i,column=1,padx=10,pady=6)
            def calc():
                try: x["work_hours"].set(minutes_hhmm(duration_minutes(x["start_time"].get(),x["end_time"].get())))
                except Exception: pass
            ttk.Button(sw,text="Розрахувати години",command=calc).grid(row=6,column=1,sticky="w",padx=10,pady=5)
            def save_seg():
                try:
                    time_to_minutes(x["start_time"].get()); time_to_minutes(x["end_time"].get())
                    wh_min=hours_value_to_minutes(x["work_hours"].get())
                    dh_min=hours_value_to_minutes(x["driving_hours"].get())
                except Exception:
                    messagebox.showerror("Помилка","Перевірте час. Тривалість можна вводити як 2:30 або 2.5.",parent=sw); return
                item={k:x[k].get().strip() for k in x}
                item["work_hours"]=minutes_to_db_hours(wh_min)
                item["driving_hours"]=minutes_to_db_hours(dh_min)
                if index is None: seg_data.append(item)
                else: seg_data[index]=item
                redraw(); sw.destroy()
            ttk.Button(sw,text="Зберегти",command=save_seg).grid(row=7,column=1,sticky="e",padx=10,pady=10)
        b=ttk.Frame(win); b.grid(row=6,column=1,columnspan=2,sticky="w",padx=10,pady=5)
        ttk.Button(b,text="Додати частину",command=lambda:edit_seg()).pack(side="left",padx=3)
        def edit_selected():
            sel=tree.selection();
            if sel: edit_seg(int(tree.item(sel[0],"values")[0])-1)
        ttk.Button(b,text="Редагувати",command=edit_selected).pack(side="left",padx=3)
        def del_selected():
            sel=tree.selection();
            if sel: seg_data.pop(int(tree.item(sel[0],"values")[0])-1); redraw()
        ttk.Button(b,text="Видалити",command=del_selected).pack(side="left",padx=3)
        redraw()
        def save():
            if not vv["name"].get().strip(): messagebox.showerror("Помилка","Вкажіть назву шаблону.",parent=win); return
            if not seg_data: messagebox.showerror("Помилка","Додайте хоча б одну частину робочої зміни.",parent=win); return
            con=db()
            try:
                if existing:
                    tid=existing[0]["id"]; con.execute("UPDATE route_templates SET name=?,route_name=?,route_id=?,vehicle=?,vehicle_id=?,shift_type=?,notes=? WHERE id=?",(vv["name"].get().strip(),route_select.get().strip(),route_map[route_select.get()]["id"] if route_select.get() in route_map else None,vehicle_select.get().strip(),vehicle_map[vehicle_select.get()]["id"] if vehicle_select.get() in vehicle_map else None,vv["shift_type"].get(),vv["notes"].get().strip(),tid))
                    con.execute("DELETE FROM route_template_segments WHERE template_id=?",(tid,))
                else:
                    cur=con.execute("INSERT INTO route_templates(name,route_name,route_id,vehicle,vehicle_id,shift_type,notes,created_at) VALUES(?,?,?,?,?,?,?,?)",(vv["name"].get().strip(),route_select.get().strip(),route_map[route_select.get()]["id"] if route_select.get() in route_map else None,vehicle_select.get().strip(),vehicle_map[vehicle_select.get()]["id"] if vehicle_select.get() in vehicle_map else None,vv["shift_type"].get(),vv["notes"].get().strip(),datetime.now().isoformat(timespec="seconds"))); tid=cur.lastrowid
                for i,r in enumerate(seg_data,1): con.execute("INSERT INTO route_template_segments(template_id,segment_no,start_time,end_time,work_hours,driving_hours,activity_type,note) VALUES(?,?,?,?,?,?,?,?)",(tid,i,r["start_time"],r["end_time"],r["work_hours"],r["driving_hours"],r["activity_type"],r["note"]))
                con.commit()
            except sqlite3.IntegrityError as e:
                con.rollback(); messagebox.showerror("Помилка",f"Не вдалося зберегти шаблон. Назва має бути унікальною.\n{e}",parent=win); return
            finally: con.close()
            win.destroy(); self.load_route_templates()
        ttk.Button(win,text="Зберегти шаблон",command=save).grid(row=8,column=2,sticky="e",padx=10,pady=10)

    def edit_route_template(self):
        item=self.selected_route_template()
        if item: self.route_template_form(item)

    def delete_route_template(self):
        item=self.selected_route_template()
        if not item: return
        if not messagebox.askyesno("Підтвердження","Видалити цей шаблон маршруту?"): return
        con=db(); con.execute("DELETE FROM route_templates WHERE id=?",(item[0]["id"],)); con.commit(); con.close(); self.load_route_templates()

    def tacho_drivers(self):
        con=db(); rows=con.execute("SELECT * FROM drivers WHERE active=1 ORDER BY last_name, first_name").fetchall(); con.close(); return rows

    def tacho_vehicles(self):
        con=db(); rows=con.execute("SELECT * FROM vehicles WHERE active=1 ORDER BY name").fetchall(); con.close(); return rows

    def tacho_to_worklog(self, driver_id, vehicle_id, work_date, intervals):
        """Застарілий канал імпорту відключено.

        Починаючи з v8.53 тахокарти використовуються тільки як вибірковий
        контроль. Результат розпізнавання зберігається у протоколі контролю
        окремої тахографічної БД і НІКОЛИ не змінює worklog/work_segments.
        """
        raise RuntimeError(
            "Передача тахокарти в основний графік/табель відключена. "
            "Використовуйте «Зберегти протокол контролю»."
        )


    def build_attestation(self):
        host=self._make_scrollable_tab_body(self.tab_att, "attestation")
        f=ttk.Frame(host); f.pack(fill="x",padx=12,pady=12)
        self.att_driver_var=tk.StringVar()
        ttk.Label(f,text="Водій:").grid(row=0,column=0,sticky="w",padx=6,pady=6)
        self.att_driver_cb=ttk.Combobox(f,textvariable=self.att_driver_var,state="readonly",width=45)
        self.att_driver_cb.grid(row=0,column=1,sticky="w",padx=6,pady=6)
        self.att_driver_cb.bind("<<ComboboxSelected>>", self.on_att_driver_change)
        self.att_from=tk.StringVar(value=datetime.now().strftime("%H:%M %d.%m.%Y"))
        self.att_to=tk.StringVar(value=datetime.now().strftime("%H:%M %d.%m.%Y"))
        self.att_place=tk.StringVar(value=get_setting("attestation_place", ""))
        self.att_date=tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
        self.att_activity=tk.StringVar(value="16 — Відсутність / відпочинок")

        # v8.55: дата Бланка підтвердження завжди дорівнює календарній
        # даті завершення періоду. Поле лише показує розраховане значення.
        def _sync_attestation_date(*_):
            en=parse_attestation_period(self.att_to.get().strip())
            if en:
                self.att_date.set(en.strftime("%d.%m.%Y"))

        self.att_to.trace_add("write", _sync_attestation_date)
        _sync_attestation_date()

        fields=[("Період з (година/дата/місяць/рік)",self.att_from),("Період по (година/дата/місяць/рік)",self.att_to),("Місце директора / представника",self.att_place),("Дата бланка (авто = дата завершення періоду)",self.att_date)]
        for i,(l,v) in enumerate(fields,1):
            ttk.Label(f,text=l).grid(row=i,column=0,sticky="w",padx=6,pady=6)
            state="readonly" if v is self.att_date else "normal"
            ttk.Entry(f,textvariable=v,width=45,state=state).grid(row=i,column=1,sticky="w",padx=6,pady=6)
            if v in (self.att_from, self.att_to):
                calendar_button(f,v).grid(row=i,column=2,sticky="w",padx=(2,6),pady=6)
        ttk.Label(
            f,
            text="Місце водія в нижньому блоці заповнюється автоматично тим самим місцем, що й у директора.",
            foreground="gray"
        ).grid(row=4,column=3,sticky="w",padx=(8,6),pady=6)
        ttk.Label(f,text="Позиція 14–19").grid(row=5,column=0,sticky="w",padx=6,pady=6)
        cb=ttk.Combobox(f,state="readonly",width=55,textvariable=self.att_activity,
                        values=[f"{n} — {ACTIVITIES[n]}" for n in ACTIVITIES])
        cb.current(2); cb.grid(row=5,column=1,sticky="w",padx=6,pady=6)
        # Зручніше зберігати номер у прихованому/текстовому комбобоксі.
        self.att_activity_text=cb
        format_bar=ttk.Frame(f)
        format_bar.grid(row=6,column=1,columnspan=2,sticky="w",padx=6,pady=12)
        ttk.Button(format_bar,text="Створити DOCX",command=lambda:self.create_attestation(("docx",))).pack(side="left",padx=(0,4))
        ttk.Button(format_bar,text="Створити PDF",command=lambda:self.create_attestation(("pdf",))).pack(side="left",padx=4)
        ttk.Button(format_bar,text="Створити JPG",command=lambda:self.create_attestation(("jpg",))).pack(side="left",padx=4)
        ttk.Button(format_bar,text="Створити все",command=lambda:self.create_attestation(("docx","pdf","jpg"))).pack(side="left",padx=4)
        ttk.Button(
            f,text="Контроль бланків — 56 днів + поточний",
            command=self.show_attestation_gap_control
        ).grid(row=7,column=1,columnspan=2,sticky="w",padx=6,pady=(0,12))

        hist=ttk.LabelFrame(host,text="Історія та контроль сформованих бланків")
        hist.pack(fill="both",expand=True,padx=12,pady=8)

        hbar=ttk.Frame(hist)
        hbar.pack(fill="x",padx=6,pady=(6,2))
        ttk.Button(hbar,text="DOCX",command=lambda:self.open_att_file("docx")).pack(side="left",padx=3)
        ttk.Button(hbar,text="PDF",command=lambda:self.open_att_file("pdf")).pack(side="left",padx=3)
        ttk.Button(hbar,text="JPG",command=lambda:self.open_att_file("jpg")).pack(side="left",padx=3)
        ttk.Button(hbar,text="Папка файла",command=self.open_att_folder).pack(side="left",padx=3)
        ttk.Button(hbar,text="Архів файлів",command=self.open_att_archive_folder).pack(side="left",padx=3)
        ttk.Button(hbar,text="Редагувати",command=self.edit_selected_attestation).pack(side="left",padx=3)
        ttk.Button(hbar,text="Вилучити з контролю",command=self.delete_selected_attestation).pack(side="left",padx=3)
        ttk.Button(hbar,text="Відновити",command=self.restore_selected_attestation).pack(side="left",padx=3)
        ttk.Button(hbar,text="Видалити назавжди",command=self.purge_selected_attestation).pack(side="left",padx=3)
        ttk.Button(hbar,text="Історія змін",command=self.show_attestation_audit).pack(side="left",padx=3)

        filter_bar=ttk.Frame(hist)
        filter_bar.pack(fill="x",padx=6,pady=(2,4))
        ttk.Label(filter_bar,text="Показати:").pack(side="left",padx=(0,4))
        self.att_filter=tk.StringVar(value="Активні")
        att_filter_cb=ttk.Combobox(
            filter_bar,textvariable=self.att_filter,state="readonly",width=15,
            values=("Активні","Вилучені","Усі")
        )
        att_filter_cb.pack(side="left")
        att_filter_cb.bind("<<ComboboxSelected>>",lambda e:self.load_att_history())
        ttk.Button(filter_bar,text="Оновити список",command=self.load_att_history).pack(side="left",padx=6)
        self.att_list_summary=tk.StringVar(value="")
        ttk.Label(filter_bar,textvariable=self.att_list_summary,foreground="gray").pack(side="right",padx=6)

        cols=("id","driver","from","to","activity","place","date","status","revision","formats","file")
        tree_frame=ttk.Frame(hist)
        tree_frame.pack(fill="both",expand=True,padx=6,pady=6)
        self.att_tree=ttk.Treeview(tree_frame,columns=cols,show="headings",selectmode="browse")
        heads={
            "id":"ID","driver":"Водій","from":"З","to":"По","activity":"Позиція",
            "place":"Місце","date":"Дата","status":"Статус","revision":"Ред.",
            "formats":"Формати","file":"Основний файл"
        }
        widths={
            "id":55,"driver":205,"from":140,"to":140,"activity":65,"place":140,
            "date":90,"status":95,"revision":50,"formats":105,"file":270
        }
        for c in cols:
            self.att_tree.heading(c,text=heads[c])
            self.att_tree.column(c,width=widths[c],anchor="w",stretch=(c=="file"))
        self.att_tree.tag_configure("deleted",foreground="gray")
        att_y=ttk.Scrollbar(tree_frame,orient="vertical",command=self.att_tree.yview)
        att_x=ttk.Scrollbar(tree_frame,orient="horizontal",command=self.att_tree.xview)
        self.att_tree.configure(yscrollcommand=att_y.set,xscrollcommand=att_x.set)
        self.att_tree.grid(row=0,column=0,sticky="nsew")
        att_y.grid(row=0,column=1,sticky="ns")
        att_x.grid(row=1,column=0,sticky="ew")
        tree_frame.rowconfigure(0,weight=1)
        tree_frame.columnconfigure(0,weight=1)
        self.att_tree.bind("<Double-1>",lambda e:self.edit_selected_attestation())

    def show_attestation_gap_control(self):
        if not getattr(self,"att_driver_id",None):
            messagebox.showwarning(
                "Контроль бланків",
                "Спочатку виберіть водія у вкладці «Підтвердження діяльності».",
                parent=self
            )
            return

        if hasattr(self,"att_gap_win") and self.att_gap_win.winfo_exists():
            self.att_gap_win.lift()
            self.refresh_attestation_gap_control()
            return

        win=tk.Toplevel(self)
        self.att_gap_win=win
        win.title("Контроль бланків — 56 днів + поточний період до виїзду")
        win.geometry("1250x650")
        win.minsize(900,500)
        win.resizable(True,True)

        top=ttk.Frame(win,padding=8)
        top.pack(fill="x")

        self.att_gap_control_date=tk.StringVar(
            value=self.att_date.get().strip() if hasattr(self,"att_date") else date.today().strftime("%d.%m.%Y")
        )
        ttk.Label(top,text="День контролю:").pack(side="left")
        ttk.Entry(top,textvariable=self.att_gap_control_date,width=13).pack(side="left",padx=5)
        calendar_button(top,self.att_gap_control_date).pack(side="left",padx=2)
        ttk.Button(
            top,text="Перевірити",command=self.refresh_attestation_gap_control
        ).pack(side="left",padx=8)
        ttk.Button(
            top,text="Підставити у форму",
            command=self.use_selected_attestation_gap
        ).pack(side="left",padx=8)

        self.att_gap_activity=tk.StringVar(value=f"16 — {ACTIVITIES[16]}")
        ttk.Label(top,text="Позиція:").pack(side="left",padx=(8,3))
        ttk.Combobox(
            top,textvariable=self.att_gap_activity,state="readonly",width=31,
            values=[f"{n} — {ACTIVITIES[n]}" for n in ACTIVITIES]
        ).pack(side="left",padx=3)

        ttk.Button(
            top,text="Сформувати Бланк підтвердження",
            command=self.create_selected_gap_attestation
        ).pack(side="left",padx=8)

        ttk.Label(
            win,
            text=(
                "Правило v8.58: контроль враховує лише активні бланки; відредаговані та вилучені ревізії зберігаються в журналі. "
                "Окремо програма дивиться вперед у графік і показує ПОТОЧНИЙ період відпочинку/діяльності "
                "до найближчого наступного виїзду — такий бланк треба підготувати до виїзду. Між двома "
                "ТАХО-робочими днями підряд окремий бланк не потрібен. Автокоди: 14 лікарняний, "
                "15 відпустка, 16 вихідний/відпочинок, 18 «Без тахо — 8 год»/інша робота, 19 доступний. "
                "Сусідні частини з однаковим кодом об'єднуються; код можна змінити вручну. Дата кожного "
                "бланка автоматично дорівнює даті закінчення його періоду, навіть якщо бланк друкується заздалегідь."
            ),
            foreground="gray",wraplength=1200,justify="left"
        ).pack(fill="x",padx=10,pady=(0,6))

        frame=ttk.Frame(win)
        frame.pack(fill="both",expand=True,padx=10,pady=5)

        cols=("status","from","to","duration","suggest","reason")
        self.att_gap_tree=ttk.Treeview(frame,columns=cols,show="headings",selectmode="browse")
        heads={
            "status":"Статус","from":"З","to":"По","duration":"Тривалість",
            "suggest":"Позиція","reason":"Пояснення"
        }
        widths={
            "status":220,"from":145,"to":145,"duration":90,
            "suggest":75,"reason":520
        }
        for c in cols:
            self.att_gap_tree.heading(c,text=heads[c])
            self.att_gap_tree.column(c,width=widths[c],anchor="w",stretch=(c=="reason"))

        ybar=ttk.Scrollbar(frame,orient="vertical",command=self.att_gap_tree.yview)
        xbar=ttk.Scrollbar(frame,orient="horizontal",command=self.att_gap_tree.xview)
        self.att_gap_tree.configure(yscrollcommand=ybar.set,xscrollcommand=xbar.set)
        self.att_gap_tree.grid(row=0,column=0,sticky="nsew")
        self.att_gap_tree.bind("<<TreeviewSelect>>",self.on_attestation_gap_select)
        ybar.grid(row=0,column=1,sticky="ns")
        xbar.grid(row=1,column=0,sticky="ew")
        frame.rowconfigure(0,weight=1)
        frame.columnconfigure(0,weight=1)

        self.att_gap_tree.tag_configure("missing",background="#FDE8E8")
        self.att_gap_tree.tag_configure("covered",background="#E6F4EA")
        self.att_gap_tree.tag_configure("current_missing",background="#FFF2CC")
        self.att_gap_tree.tag_configure("current_covered",background="#DDEBF7")
        self.att_gap_tree.tag_configure("no_tacho",background="#EAF2FF")

        self.att_gap_summary=tk.StringVar()
        ttk.Label(
            win,textvariable=self.att_gap_summary,
            font=("TkDefaultFont",9,"bold")
        ).pack(fill="x",padx=10,pady=(2,8))

        self.att_gap_items={}
        self.refresh_attestation_gap_control()

    def refresh_attestation_gap_control(self):
        if not getattr(self,"att_driver_id",None):
            return
        if not hasattr(self,"att_gap_tree") or not self.att_gap_tree.winfo_exists():
            return
        try:
            control_day=datetime.strptime(
                self.att_gap_control_date.get().strip(),"%d.%m.%Y"
            ).date()
        except ValueError:
            messagebox.showerror(
                "Контроль бланків","Дата має бути у форматі ДД.ММ.РРРР.",
                parent=self.att_gap_win
            )
            return

        data=collect_attestation_gap_control(
            self.att_driver_id,control_day,previous_days=56
        )
        for x in self.att_gap_tree.get_children():
            self.att_gap_tree.delete(x)
        self.att_gap_items={}

        for idx,r in enumerate(data["rows"],1):
            iid=f"g{idx}"
            self.att_gap_items[iid]=r
            self.att_gap_tree.insert(
                "","end",iid=iid,
                values=(
                    r["status"],
                    format_attestation_period(r["from"]),
                    format_attestation_period(r["to"]),
                    minutes_hhmm(r["minutes"]),
                    str(r["activity_no"]) if r["activity_no"] else "",
                    r["reason"],
                ),
                tags=(("current_"+r["kind"]) if r.get("is_current") else r["kind"],)
            )

        bad=""
        if data["invalid_attestations"]:
            bad=f"    ⚠ Нечитабельні періоди бланків ID: {', '.join(map(str,data['invalid_attestations']))}"

        current_text=(
            f"    ПОТОЧНИЙ до виїзду {data['current_departure'].strftime('%d.%m.%Y %H:%M')}: "
            f"{minutes_hhmm(data['current_required_minutes'])}, не закрито {minutes_hhmm(data['current_missing_minutes'])}"
            if data.get("current_pair_found") and data.get("current_departure") else
            "    ПОТОЧНИЙ: бланк до найближчого виїзду за графіком не потрібен/не визначений"
        )
        self.att_gap_summary.set(
            f"Період історичного контролю: {data['start_day'].strftime('%d.%m.%Y')}–{data['end_day'].strftime('%d.%m.%Y')}    "
            f"ТАХО-днів: {data['tacho_days']}    Без тахо 8 год: {data['no_tacho_days']}    "
            f"Усього потрібно: {minutes_hhmm(data['required_minutes'])}    "
            f"Закрито: {minutes_hhmm(data['covered_minutes'])}    "
            f"НЕ ЗАКРИТО: {minutes_hhmm(data['missing_minutes'])}{current_text}{bad}"
        )

    def on_attestation_gap_select(self, _=None):
        if not hasattr(self,"att_gap_tree"):
            return
        sel=self.att_gap_tree.selection()
        if not sel:
            return
        r=self.att_gap_items.get(sel[0])
        if not r or r.get("kind")!="missing":
            return
        suggested=int(r.get("activity_no") or 16)
        self.att_gap_activity.set(f"{suggested} — {ACTIVITIES[suggested]}")

    def use_selected_attestation_gap(self):
        if not hasattr(self,"att_gap_tree"):
            return
        sel=self.att_gap_tree.selection()
        if not sel:
            messagebox.showwarning(
                "Контроль бланків","Виберіть незакритий проміжок (минулий або поточний).",
                parent=self.att_gap_win
            )
            return
        r=self.att_gap_items.get(sel[0])
        if not r or r.get("kind")!="missing":
            messagebox.showwarning(
                "Контроль бланків",
                "Для підстановки виберіть незакритий рядок: минулий або «ПОТОЧНИЙ — ПІДГОТУВАТИ».",
                parent=self.att_gap_win
            )
            return

        self.att_from.set(format_attestation_period(r["from"]))
        self.att_to.set(format_attestation_period(r["to"]))
        # v8.55: бланк датується днем, яким закінчується саме цей період,
        # а не днем перевірки 56-денного вікна.
        self.att_date.set(r["to"].strftime("%d.%m.%Y"))

        # За замовчуванням беремо автокод рядка, але залишаємо можливість
        # вручну змінити його у спадному списку перед підстановкою.
        suggested_no=int(r.get("activity_no") or 16)
        try:
            chosen_no=int(self.att_gap_activity.get().split(" ",1)[0])
        except Exception:
            chosen_no=suggested_no
        self.att_activity.set(f"{chosen_no} — {ACTIVITIES[chosen_no]}")

        # Закриваємо контрольне вікно, щоб користувач одразу бачив реально
        # заповнені поля основної форми.
        try:
            self.att_gap_win.destroy()
        except Exception:
            pass

        messagebox.showinfo(
            "Проміжок підставлено",
            "Поля «Період з / по» та позиція 14–19 вже заповнені у формі "
            "«Підтвердження діяльності». Перевірте їх і виберіть потрібний формат: DOCX, PDF, JPG або «Створити все».",
            parent=self
        )

    def _create_attestation_record(
        self, period_from, period_to, activity_no, form_date_text=None,
        parent=None, show_message=True, formats=("docx",)
    ):
        if not self.att_driver_id:
            raise ValueError("Виберіть водія.")

        con=db()
        d=con.execute(
            "SELECT * FROM drivers WHERE id=?",(self.att_driver_id,)
        ).fetchone()
        con.close()
        if not d:
            raise ValueError("Водія не знайдено.")

        st=parse_attestation_period(period_from)
        en=parse_attestation_period(period_to)
        if not st or not en or en<=st:
            raise ValueError("Невірний період бланка.")

        # v8.55 — дата завжди дорівнює даті завершення періоду.
        dt=en.date()
        form_date_text=dt.strftime("%d.%m.%Y")
        if hasattr(self,"att_date"):
            self.att_date.set(form_date_text)

        place_value=self.att_place.get().strip()
        if place_value:
            set_setting("attestation_place",place_value)

        # v8.59/v8.60 — перед формуванням використовуємо актуальні
        # англійські реквізити підприємства та водія.
        self.save_company(show_message=False)

        paths=_unique_attestation_output_paths(d,st,en,activity_no)
        created=_generate_attestation_files(
            d,period_from,period_to,int(activity_no),place_value,form_date_text,paths,formats
        )

        con=db()
        now=datetime.now().isoformat(timespec="seconds")
        cur=con.execute(
            """INSERT INTO attestations(
                driver_id,period_from,period_to,activity_no,place,form_date,
                file_path,pdf_path,jpg_page1_path,jpg_page2_path,
                status,revision,updated_at,deleted_at,delete_reason,created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                d["id"],period_from,period_to,int(activity_no),place_value,dt.isoformat(),
                created["file_path"],created["pdf_path"],created["jpg_page1_path"],created["jpg_page2_path"],
                "active",1,now,"","",now
            )
        )
        att_id=cur.lastrowid
        row=con.execute("SELECT * FROM attestations WHERE id=?",(att_id,)).fetchone()
        fmt_note=", ".join(x.upper() for x in formats)
        _audit_attestation_snapshot(con,row,"CREATE",f"Створено бланк: {fmt_note}")
        con.commit()
        con.close()

        self.load_att_history()
        if hasattr(self,"att_gap_win") and self.att_gap_win.winfo_exists():
            self.refresh_attestation_gap_control()

        paths_created=[v for v in created.values() if v]
        if show_message:
            messagebox.showinfo(
                "Готово",
                "Бланк створено:\n"+"\n".join(paths_created),
                parent=parent or self
            )
        return created

    def create_selected_gap_attestation(self):
        if not hasattr(self,"att_gap_tree"):
            return
        sel=self.att_gap_tree.selection()
        if not sel:
            messagebox.showwarning(
                "Контроль бланків",
                "Виберіть незакритий проміжок (минулий або поточний).",
                parent=self.att_gap_win
            )
            return

        r=self.att_gap_items.get(sel[0])
        if not r or r.get("kind")!="missing":
            messagebox.showwarning(
                "Контроль бланків",
                "Бланк можна сформувати тільки для незакритого проміжку.",
                parent=self.att_gap_win
            )
            return

        suggested_no=int(r.get("activity_no") or 16)
        try:
            activity_no=int(self.att_gap_activity.get().split(" ",1)[0])
        except Exception:
            activity_no=suggested_no

        period_from=format_attestation_period(r["from"])
        period_to=format_attestation_period(r["to"])

        try:
            # Одразу синхронізуємо і основну форму — користувач бачить,
            # які саме дані пішли в DOCX.
            self.att_from.set(period_from)
            self.att_to.set(period_to)
            self.att_activity.set(f"{activity_no} — {ACTIVITIES[activity_no]}")
            # Дата документа всередині _create_attestation_record буде
            # автоматично взята з period_to (правило v8.55).
            created=self._create_attestation_record(
                period_from,period_to,activity_no,
                parent=self.att_gap_win,
                show_message=False,
                formats=("docx",)
            )
            out=created.get("file_path") or created.get("pdf_path") or created.get("jpg_page1_path") or ""
            self.refresh_attestation_gap_control()
            messagebox.showinfo(
                "Бланк сформовано",
                f"Створено бланк на вибрану частину проміжку:\n\n"
                f"{period_from}\n→ {period_to}\n\n"
                f"Позиція: {activity_no}\n\nФайл:\n{out}",
                parent=self.att_gap_win
            )
        except Exception as e:
            messagebox.showerror(
                "Помилка",str(e),parent=self.att_gap_win
            )

    def create_attestation(self, formats=("docx",)):
        if not self.att_driver_id:
            messagebox.showwarning(
                "Увага","Виберіть водія у спадному меню «Водій»."
            )
            return
        try:
            activity_text=self.att_activity_text.get()
            activity_no=int(activity_text.split(" ",1)[0])
            self._create_attestation_record(
                self.att_from.get().strip(),
                self.att_to.get().strip(),
                activity_no,
                parent=self,
                show_message=True,
                formats=formats
            )
        except Exception as e:
            messagebox.showerror("Помилка",str(e))



    def _selected_attestation_id(self):
        if not hasattr(self,"att_tree"):
            return None
        sel=self.att_tree.selection()
        if not sel:
            return None
        vals=self.att_tree.item(sel[0],"values")
        try:
            return int(vals[0])
        except Exception:
            return None

    def _update_attestation_record(self, attestation_id, period_from, period_to, activity_no, place):
        st=parse_attestation_period(period_from)
        en=parse_attestation_period(period_to)
        if not st or not en or en<=st:
            raise ValueError("Невірний період бланка.")
        if int(activity_no) not in ACTIVITIES:
            raise ValueError("Позиція має бути від 14 до 19.")

        con=db()
        current=con.execute("SELECT * FROM attestations WHERE id=?",(int(attestation_id),)).fetchone()
        if not current:
            con.close(); raise ValueError("Бланк не знайдено.")
        if not _attestation_is_active(current):
            con.close(); raise ValueError("Вилучений бланк спочатку треба відновити.")
        driver=con.execute("SELECT * FROM drivers WHERE id=?",(current["driver_id"],)).fetchone()
        con.close()
        if not driver:
            raise ValueError("Водія не знайдено.")

        form_date_text=en.strftime("%d.%m.%Y")
        formats=_attestation_existing_formats(current)
        paths=_unique_attestation_output_paths(driver,st,en,activity_no)

        # v8.59/v8.60: перед перегенерацією використовуємо поточні реквізити.
        self.save_company(show_message=False)
        created=_generate_attestation_files(
            driver,period_from,period_to,int(activity_no),place,form_date_text,paths,formats
        )

        backup_database("before_attestation_edit")
        archived_old=_archive_attestation_files(current,ATT_REPLACED_DIR,"replaced")
        now=datetime.now().isoformat(timespec="seconds")

        con=db()
        try:
            current=con.execute("SELECT * FROM attestations WHERE id=?",(int(attestation_id),)).fetchone()
            _ensure_attestation_audit_baseline(con,current)
            new_revision=int(current["revision"] or 1)+1
            con.execute(
                """UPDATE attestations
                       SET period_from=?,period_to=?,activity_no=?,place=?,form_date=?,
                           file_path=?,pdf_path=?,jpg_page1_path=?,jpg_page2_path=?,
                           status='active',revision=?,updated_at=?,deleted_at='',delete_reason=''
                     WHERE id=?""",
                (period_from,period_to,int(activity_no),place,en.date().isoformat(),
                 created["file_path"],created["pdf_path"],created["jpg_page1_path"],created["jpg_page2_path"],
                 new_revision,now,int(attestation_id))
            )
            updated=con.execute("SELECT * FROM attestations WHERE id=?",(int(attestation_id),)).fetchone()
            moved=[v for k,v in archived_old.items() if v and v != ((current[k] or "") if k in current.keys() else "")]
            note="Відредаговано після зміни графіка/періоду; перегенеровано: " + ", ".join(x.upper() for x in formats)
            if moved:
                note += ". Попередні файли перенесено в архів."
            _audit_attestation_snapshot(con,updated,"EDIT",note)
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

        if place:
            set_setting("attestation_place",place)
        self.load_att_history()
        if hasattr(self,"att_gap_win") and self.att_gap_win.winfo_exists():
            self.refresh_attestation_gap_control()
        return (created.get("pdf_path") or created.get("file_path") or
                created.get("jpg_page1_path") or created.get("jpg_page2_path") or "")

    def edit_selected_attestation(self):
        att_id=self._selected_attestation_id()
        if not att_id:
            messagebox.showwarning("Бланки","Виберіть бланк у таблиці.",parent=self)
            return
        con=db()
        r=con.execute("SELECT * FROM attestations WHERE id=?",(att_id,)).fetchone()
        con.close()
        if not r:
            return
        if not _attestation_is_active(r):
            messagebox.showwarning(
                "Бланки","Цей бланк вилучений. Спочатку натисніть «Відновити».",parent=self
            )
            return

        win=tk.Toplevel(self)
        win.title(f"Редагування Бланка підтвердження №{att_id}")
        win.geometry("760x390")
        win.transient(self)
        win.grab_set()

        from_var=tk.StringVar(value=r["period_from"])
        to_var=tk.StringVar(value=r["period_to"])
        place_var=tk.StringVar(value=r["place"] or "")
        activity_var=tk.StringVar(value=f"{int(r['activity_no'])} — {ACTIVITIES.get(int(r['activity_no']),'')}")
        date_var=tk.StringVar()

        def sync_date(*_):
            en=parse_attestation_period(to_var.get().strip())
            date_var.set(en.strftime("%d.%m.%Y") if en else "")
        to_var.trace_add("write",sync_date)
        sync_date()

        ttk.Label(win,text="Період з").grid(row=0,column=0,sticky="w",padx=12,pady=10)
        ttk.Entry(win,textvariable=from_var,width=32).grid(row=0,column=1,sticky="w",padx=6,pady=10)
        calendar_button(win,from_var).grid(row=0,column=2,sticky="w",padx=4,pady=10)
        ttk.Label(win,text="Період по").grid(row=1,column=0,sticky="w",padx=12,pady=10)
        ttk.Entry(win,textvariable=to_var,width=32).grid(row=1,column=1,sticky="w",padx=6,pady=10)
        calendar_button(win,to_var).grid(row=1,column=2,sticky="w",padx=4,pady=10)
        ttk.Label(win,text="Позиція 14–19").grid(row=2,column=0,sticky="w",padx=12,pady=10)
        ttk.Combobox(
            win,textvariable=activity_var,state="readonly",width=48,
            values=[f"{n} — {ACTIVITIES[n]}" for n in ACTIVITIES]
        ).grid(row=2,column=1,columnspan=2,sticky="w",padx=6,pady=10)
        ttk.Label(win,text="Місце директора / представника").grid(row=3,column=0,sticky="w",padx=12,pady=10)
        ttk.Entry(win,textvariable=place_var,width=52).grid(row=3,column=1,columnspan=2,sticky="ew",padx=6,pady=10)
        ttk.Label(win,text="Дата бланка").grid(row=4,column=0,sticky="w",padx=12,pady=10)
        ttk.Entry(win,textvariable=date_var,state="readonly",width=18).grid(row=4,column=1,sticky="w",padx=6,pady=10)
        ttk.Label(
            win,
            text=(
                "Після збереження старий DOCX не знищується: він переноситься у контрольний архів, "
                "а в журналі змін залишається попередня ревізія. Контроль 56 днів одразу перерахується."
            ),
            foreground="gray",wraplength=700,justify="left"
        ).grid(row=5,column=0,columnspan=3,sticky="w",padx=12,pady=(8,12))

        def save_edit():
            try:
                activity_no=int(activity_var.get().split(" ",1)[0])
                out=self._update_attestation_record(
                    att_id,from_var.get().strip(),to_var.get().strip(),activity_no,place_var.get().strip()
                )
                win.destroy()
                messagebox.showinfo(
                    "Бланк оновлено",
                    f"Створено нову ревізію бланка №{att_id}.\n\nНовий файл:\n{out}",
                    parent=self
                )
            except Exception as e:
                messagebox.showerror("Помилка редагування",str(e),parent=win)

        buttons=ttk.Frame(win)
        buttons.grid(row=6,column=0,columnspan=3,sticky="e",padx=12,pady=12)
        ttk.Button(buttons,text="Скасувати",command=win.destroy).pack(side="right",padx=4)
        ttk.Button(buttons,text="Зберегти зміни",command=save_edit).pack(side="right",padx=4)
        win.columnconfigure(1,weight=1)

    def delete_selected_attestation(self):
        att_id=self._selected_attestation_id()
        if not att_id:
            messagebox.showwarning("Бланки","Виберіть бланк у таблиці.",parent=self)
            return
        con=db(); r=con.execute("SELECT * FROM attestations WHERE id=?",(att_id,)).fetchone(); con.close()
        if not r:
            return
        if not _attestation_is_active(r):
            messagebox.showinfo("Бланки","Цей бланк уже вилучений.",parent=self)
            return

        reason=simpledialog.askstring(
            "Причина вилучення",
            "Вкажіть причину (наприклад: змінено графік / помилковий початковий графік).\nПоле можна залишити порожнім.",
            parent=self
        )
        if reason is None:
            return
        if not messagebox.askyesno(
            "Вилучити бланк",
            f"Вилучити Бланк підтвердження №{att_id} з активного контролю?\n\n"
            "Запис не буде фізично стертий: він залишиться у журналі, а всі наявні DOCX/PDF/JPG буде перенесено в архів. "
            "Після цього контроль проміжків перерахується.",
            parent=self
        ):
            return

        backup_database("before_attestation_delete")
        archived=_archive_attestation_files(r,ATT_DELETED_DIR,"deleted")
        now=datetime.now().isoformat(timespec="seconds")
        con=db()
        try:
            r=con.execute("SELECT * FROM attestations WHERE id=?",(att_id,)).fetchone()
            _ensure_attestation_audit_baseline(con,r)
            rev=int(r["revision"] or 1)+1
            con.execute(
                """UPDATE attestations
                       SET status='deleted',revision=?,updated_at=?,deleted_at=?,delete_reason=?,
                           file_path=?,pdf_path=?,jpg_page1_path=?,jpg_page2_path=?
                     WHERE id=?""",
                (rev,now,now,(reason or "").strip(),
                 archived["file_path"],archived["pdf_path"],archived["jpg_page1_path"],archived["jpg_page2_path"],att_id)
            )
            deleted=con.execute("SELECT * FROM attestations WHERE id=?",(att_id,)).fetchone()
            _audit_attestation_snapshot(con,deleted,"DELETE",(reason or "").strip())
            con.commit()
        except Exception:
            con.rollback(); raise
        finally:
            con.close()

        self.load_att_history()
        if hasattr(self,"att_gap_win") and self.att_gap_win.winfo_exists():
            self.refresh_attestation_gap_control()
        messagebox.showinfo(
            "Бланк вилучено",
            "Бланк вилучено з активного контролю. Запис і всі його файли збережені в архіві; за потреби його можна відновити.",
            parent=self
        )

    def restore_selected_attestation(self):
        att_id=self._selected_attestation_id()
        if not att_id:
            messagebox.showwarning("Бланки","Виберіть вилучений бланк у таблиці.",parent=self)
            return
        con=db(); r=con.execute("SELECT * FROM attestations WHERE id=?",(att_id,)).fetchone(); con.close()
        if not r:
            return
        if _attestation_is_active(r):
            messagebox.showinfo("Бланки","Цей бланк уже активний.",parent=self)
            return
        if not messagebox.askyesno(
            "Відновити бланк",
            f"Повернути Бланк підтвердження №{att_id} до активного контролю?",
            parent=self
        ):
            return

        restored=_restore_attestation_files(r)
        backup_database("before_attestation_restore")
        now=datetime.now().isoformat(timespec="seconds")
        con=db()
        try:
            r=con.execute("SELECT * FROM attestations WHERE id=?",(att_id,)).fetchone()
            _ensure_attestation_audit_baseline(con,r)
            rev=int(r["revision"] or 1)+1
            con.execute(
                """UPDATE attestations
                       SET status='active',revision=?,updated_at=?,deleted_at='',delete_reason='',
                           file_path=?,pdf_path=?,jpg_page1_path=?,jpg_page2_path=?
                     WHERE id=?""",
                (rev,now,restored["file_path"],restored["pdf_path"],
                 restored["jpg_page1_path"],restored["jpg_page2_path"],att_id)
            )
            restored_row=con.execute("SELECT * FROM attestations WHERE id=?",(att_id,)).fetchone()
            _audit_attestation_snapshot(con,restored_row,"RESTORE","Відновлено користувачем")
            con.commit()
        except Exception:
            con.rollback(); raise
        finally:
            con.close()

        self.load_att_history()
        if hasattr(self,"att_gap_win") and self.att_gap_win.winfo_exists():
            self.refresh_attestation_gap_control()
        messagebox.showinfo("Бланки","Бланк і всі наявні формати повернуто до активного контролю.",parent=self)

    def open_att_archive_folder(self):
        ATT_ARCHIVE_DIR.mkdir(parents=True,exist_ok=True)
        if os.name=="nt":
            os.startfile(str(ATT_ARCHIVE_DIR))
        else:
            subprocess.Popen(["xdg-open",str(ATT_ARCHIVE_DIR)])

    def purge_selected_attestation(self):
        """Фізично видаляє вже вилучений бланк, його аудит і файли.

        Це окрема дія від «Вилучити з контролю». Для безпеки активний бланк
        спочатку треба вилучити з контролю, а перед очищенням створюється backup БД.
        """
        att_id=self._selected_attestation_id()
        if not att_id:
            messagebox.showwarning("Бланки","Виберіть бланк у таблиці.",parent=self)
            return
        con=db()
        row=con.execute("SELECT * FROM attestations WHERE id=?",(att_id,)).fetchone()
        audits=con.execute("SELECT * FROM attestation_audit WHERE attestation_id=?",(att_id,)).fetchall()
        con.close()
        if not row:
            return
        if _attestation_is_active(row):
            messagebox.showwarning(
                "Видалення назавжди",
                "Активний бланк не можна стерти одразу. Спочатку натисніть «Вилучити з контролю», "
                "перевірте результат, а потім — «Видалити назавжди».",parent=self
            )
            return
        if not messagebox.askyesno(
            "Видалити назавжди",
            f"Бланк №{att_id} буде ФІЗИЧНО видалено з бази, журналу змін та архіву файлів.\n\n"
            "Після цього він не відображатиметься навіть у режимі «Усі». Перед видаленням Taxo створить резервну копію БД.\n\nПродовжити?",
            icon="warning",parent=self
        ):
            return
        token=simpledialog.askstring(
            "Підтвердження остаточного видалення",
            "Для остаточного видалення введіть слово ВИДАЛИТИ:",parent=self
        )
        if (token or "").strip().upper()!="ВИДАЛИТИ":
            messagebox.showinfo("Скасовано","Остаточне видалення скасовано.",parent=self)
            return

        backup_database("before_attestation_purge")
        root=DATA_ROOT.resolve()
        paths=set()
        for r in [row,*audits]:
            keys=set(r.keys()) if hasattr(r,"keys") else set()
            for field in ("file_path","pdf_path","jpg_page1_path","jpg_page2_path"):
                raw=(r[field] or "").strip() if field in keys else ""
                if raw:
                    paths.add(raw)

        removed_files=0
        for raw in sorted(paths):
            try:
                fp=Path(raw)
                if not fp.exists() or not fp.is_file():
                    continue
                resolved=fp.resolve()
                # Ніколи не стираємо файл за межами каталогу даних Taxo.
                if resolved==root or root not in resolved.parents:
                    continue
                fp.unlink()
                removed_files+=1
            except OSError:
                pass

        con=db()
        try:
            con.execute("DELETE FROM attestation_audit WHERE attestation_id=?",(att_id,))
            con.execute("DELETE FROM attestations WHERE id=?",(att_id,))
            con.commit()
        except Exception:
            con.rollback(); raise
        finally:
            con.close()

        self.load_att_history()
        if hasattr(self,"att_gap_win") and self.att_gap_win.winfo_exists():
            self.refresh_attestation_gap_control()
        messagebox.showinfo(
            "Видалено назавжди",
            f"Бланк №{att_id} повністю видалено. Файлів стерто: {removed_files}.\n"
            "Страхова резервна копія БД створена перед операцією.",parent=self
        )

    def show_attestation_audit(self):
        att_id=self._selected_attestation_id()
        if not att_id:
            messagebox.showwarning("Бланки","Виберіть бланк у таблиці.",parent=self)
            return
        con=db()
        current=con.execute("SELECT * FROM attestations WHERE id=?",(att_id,)).fetchone()
        rows=con.execute(
            "SELECT * FROM attestation_audit WHERE attestation_id=? ORDER BY id",(att_id,)
        ).fetchall()
        con.close()

        win=tk.Toplevel(self)
        win.title(f"Історія змін Бланка №{att_id}")
        win.geometry("1350x520")
        win.transient(self)

        cols=("when","action","revision","from","to","activity","status","note","files")
        audit_frame=ttk.Frame(win)
        audit_frame.pack(fill="both",expand=True,padx=10,pady=10)
        tree=ttk.Treeview(audit_frame,columns=cols,show="headings")
        heads={
            "when":"Коли","action":"Дія","revision":"Ред.","from":"З","to":"По",
            "activity":"Позиція","status":"Статус","note":"Примітка","files":"Файли"
        }
        widths={
            "when":145,"action":95,"revision":55,"from":145,"to":145,"activity":70,
            "status":90,"note":250,"files":430
        }
        for c in cols:
            tree.heading(c,text=heads[c]); tree.column(c,width=widths[c],anchor="w",stretch=(c in ("note","files")))
        audit_y=ttk.Scrollbar(audit_frame,orient="vertical",command=tree.yview)
        audit_x=ttk.Scrollbar(audit_frame,orient="horizontal",command=tree.xview)
        tree.configure(yscrollcommand=audit_y.set,xscrollcommand=audit_x.set)
        tree.grid(row=0,column=0,sticky="nsew")
        audit_y.grid(row=0,column=1,sticky="ns")
        audit_x.grid(row=1,column=0,sticky="ew")
        audit_frame.rowconfigure(0,weight=1)
        audit_frame.columnconfigure(0,weight=1)

        def paths_text(row):
            keys=set(row.keys()) if hasattr(row,"keys") else set()
            parts=[]
            for label,field in (("DOCX","file_path"),("PDF","pdf_path"),("JPG1","jpg_page1_path"),("JPG2","jpg_page2_path")):
                val=(row[field] or "") if field in keys else ""
                if val:
                    parts.append(f"{label}: {val}")
            return " | ".join(parts)

        if rows:
            for a in rows:
                tree.insert("","end",values=(
                    (a["created_at"] or "").replace("T"," "),a["action"],a["revision"],
                    a["period_from"],a["period_to"],a["activity_no"],a["status"],a["note"],paths_text(a)
                ))
        elif current:
            tree.insert("","end",values=(
                (current["created_at"] or "").replace("T"," "),"CURRENT",current["revision"],
                current["period_from"],current["period_to"],current["activity_no"],current["status"],
                "Старий запис: змін ще не було",paths_text(current)
            ))

        ttk.Button(win,text="Закрити",command=win.destroy).pack(anchor="e",padx=10,pady=(0,10))

    def load_att_history(self):
        if not hasattr(self,"att_tree"):
            return
        selected_id=self._selected_attestation_id() if self.att_tree.selection() else None
        for x in self.att_tree.get_children():
            self.att_tree.delete(x)

        mode=(self.att_filter.get().strip() if hasattr(self,"att_filter") else "Активні")
        con=db()
        total=con.execute("SELECT COUNT(*) FROM attestations").fetchone()[0]
        active_count=con.execute("SELECT COUNT(*) FROM attestations WHERE COALESCE(status,'active')='active'").fetchone()[0]
        deleted_count=con.execute("SELECT COUNT(*) FROM attestations WHERE COALESCE(status,'active')<>'active'").fetchone()[0]
        sql="""SELECT a.*, d.last_name||' '||d.first_name AS driver_name
                 FROM attestations a JOIN drivers d ON d.id=a.driver_id"""
        params=[]
        if mode=="Активні":
            sql += " WHERE COALESCE(a.status,'active')='active'"
        elif mode=="Вилучені":
            sql += " WHERE COALESCE(a.status,'active')<>'active'"
        # mode == "Усі": жодного прихованого фільтра і жодного LIMIT.
        sql += " ORDER BY a.id DESC"
        rows=con.execute(sql,params).fetchall()
        con.close()

        if hasattr(self,"att_list_summary"):
            self.att_list_summary.set(
                f"Показано: {len(rows)} з {total} | активних: {active_count} | вилучених: {deleted_count}"
            )

        selected_iid=None
        for r in rows:
            active=_attestation_is_active(r)
            status_text="Активний" if active else "Вилучений"
            tags=() if active else ("deleted",)
            formats=[]
            if (r["file_path"] or "").strip(): formats.append("DOCX")
            if (r["pdf_path"] or "").strip(): formats.append("PDF")
            if (r["jpg_page1_path"] or "").strip() or (r["jpg_page2_path"] or "").strip(): formats.append("JPG")
            primary=(r["pdf_path"] or r["file_path"] or r["jpg_page1_path"] or r["jpg_page2_path"] or "")
            iid=self.att_tree.insert(
                "","end",
                values=(
                    r["id"],r["driver_name"],r["period_from"],r["period_to"],r["activity_no"],
                    r["place"],r["form_date"],status_text,r["revision"]," / ".join(formats),primary
                ),
                tags=tags
            )
            if selected_id and int(r["id"])==int(selected_id):
                selected_iid=iid
        if selected_iid:
            self.att_tree.selection_set(selected_iid)
            self.att_tree.see(selected_iid)

    def _selected_attestation_row(self):
        att_id=self._selected_attestation_id()
        if not att_id:
            return None
        con=db(); row=con.execute("SELECT * FROM attestations WHERE id=?",(att_id,)).fetchone(); con.close()
        return row

    def _open_path(self, path):
        path=(path or "").strip()
        if not path or not os.path.exists(path):
            messagebox.showerror("Помилка","Файл не знайдено.",parent=self)
            return
        os.startfile(path) if os.name=="nt" else subprocess.Popen(["xdg-open",path])

    def open_att_file(self, kind=None):
        row=self._selected_attestation_row()
        if row is None:
            messagebox.showwarning("Бланки","Виберіть бланк у таблиці.",parent=self)
            return
        if kind=="docx":
            path=row["file_path"]
        elif kind=="pdf":
            path=row["pdf_path"]
        elif kind=="jpg":
            path=row["jpg_page1_path"] or row["jpg_page2_path"]
        else:
            path=row["pdf_path"] or row["file_path"] or row["jpg_page1_path"] or row["jpg_page2_path"]
        if not (path or "").strip():
            messagebox.showinfo("Бланки",f"Для цього запису формат {str(kind or '').upper()} не створювався.",parent=self)
            return
        self._open_path(path)

    def open_att_folder(self):
        row=self._selected_attestation_row()
        if row is None:
            messagebox.showwarning("Бланки","Виберіть бланк у таблиці.",parent=self)
            return
        path=row["pdf_path"] or row["file_path"] or row["jpg_page1_path"] or row["jpg_page2_path"]
        if not (path or "").strip():
            messagebox.showinfo("Бланки","Для цього запису немає збереженого файлу.",parent=self)
            return
        folder=str(Path(path).parent)
        if os.name=="nt":
            os.startfile(folder)
        else:
            subprocess.Popen(["xdg-open",folder])

if __name__ == "__main__":
    migrated, old_db = init_db()
    app = App()
    if migrated and old_db:
        app.after(300, lambda: messagebox.showinfo(
            "Дані перенесено автоматично",
            "Існуючу базу водіїв знайдено та один раз скопійовано у постійне сховище:\n\n"
            f"{DB_PATH}\n\nСтара база залишена без змін. Надалі оновлення програми не вимагатимуть перенесення даних."
        ))
    app.mainloop()
