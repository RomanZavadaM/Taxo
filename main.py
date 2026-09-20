# -*- coding: utf-8 -*-
"""
Облік водіїв: база водіїв, 48 місяців робочого часу,
табелі та бланки підтвердження діяльності.

Запуск: py -3.13 main.py
"""
import calendar
import os
import platform
import re
import sqlite3
import subprocess
import sys
import shutil
import tempfile
import traceback
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

from branding import (
    PALETTE,
    apply_theme,
    brand_photo,
    configure_toplevel,
    draw_brand_header,
    install_runtime_icon,
)
from workspace import (
    WorkspaceBusyError,
    WorkspaceLock,
    clone_workspace,
    describe_lock,
    ensure_workspace,
    load_workspace_root,
    normalize_database_paths,
    normalize_root,
    paths_for,
    probe_workspace,
    read_lock_info,
    resolved_path,
    save_workspace_root,
    storage_kind,
    stored_path,
    workspace_has_data,
)

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

try:
    from waybill import build_waybill_pdf
except ImportError:
    build_waybill_pdf = None

APP_VERSION = "10.1-r2"
APP_DIR = Path(__file__).resolve().parent

# Постійне робоче сховище не залежить від версії програми. Його адресу можна
# змінити на локальну, мережеву або синхронізовану папку. У локальному профілі
# залишається лише покажчик на сховище; усі робочі дані лежать у DATA_ROOT.
DOCUMENTS_DIR = Path.home() / "Documents"
DATA_ROOT = load_workspace_root()
_WORKSPACE_PATHS = paths_for(DATA_ROOT)
DATA_DIR = _WORKSPACE_PATHS["data"]
BACKUP_DIR = _WORKSPACE_PATHS["backups"]
OUTPUT_DIR = _WORKSPACE_PATHS["output"]
LOG_DIR = _WORKSPACE_PATHS["logs"]
ATT_ARCHIVE_DIR = _WORKSPACE_PATHS["att_archive"]
ATT_REPLACED_DIR = _WORKSPACE_PATHS["att_replaced"]
ATT_DELETED_DIR = _WORKSPACE_PATHS["att_deleted"]
WAYBILL_DIR = _WORKSPACE_PATHS["waybills"]
DB_PATH = _WORKSPACE_PATHS["main_db"]
TEMPLATE_PATH = APP_DIR / "Бланк підтвердження.docx"
ATT_VISUAL_TEMPLATE_PATH = APP_DIR / "attestation_visual_template.pdf"

ACTIVE_WORKSPACE_LOCK = None


def configure_runtime_workspace(root):
    """Оновити модульні шляхи до створення БД/інтерфейсу."""
    global DATA_ROOT,DATA_DIR,BACKUP_DIR,OUTPUT_DIR,LOG_DIR
    global ATT_ARCHIVE_DIR,ATT_REPLACED_DIR,ATT_DELETED_DIR,WAYBILL_DIR,DB_PATH
    DATA_ROOT=normalize_root(root)
    p=paths_for(DATA_ROOT)
    DATA_DIR=p["data"]; BACKUP_DIR=p["backups"]; OUTPUT_DIR=p["output"]; LOG_DIR=p["logs"]
    ATT_ARCHIVE_DIR=p["att_archive"]; ATT_REPLACED_DIR=p["att_replaced"]
    ATT_DELETED_DIR=p["att_deleted"]; WAYBILL_DIR=p["waybills"]; DB_PATH=p["main_db"]
    try:
        import tachograph
        tachograph.configure_workspace(DATA_ROOT)
    except Exception:
        pass


def attestation_history_query(mode="Активні", driver_id=None, year=None, month=None):
    """Build the archive query with explicit filters and newest periods first."""
    sql="""SELECT a.*, d.last_name||' '||d.first_name AS driver_name
             FROM attestations a JOIN drivers d ON d.id=a.driver_id"""
    where=[]
    params=[]
    if mode=="Активні":
        where.append("COALESCE(a.status,'active')='active'")
    elif mode=="Вилучені":
        where.append("COALESCE(a.status,'active')<>'active'")
    if driver_id:
        where.append("a.driver_id=?")
        params.append(int(driver_id))
    if year is not None and month is not None:
        ym=f"{int(year):04d}-{int(month):02d}"
        where.append(
            "(CASE WHEN length(COALESCE(a.form_date,''))>=7 "
            "THEN substr(a.form_date,1,7) ELSE substr(a.period_to,1,7) END)=?"
        )
        params.append(ym)
    if where:
        sql += " WHERE " + " AND ".join(where)
    # period_to is ISO YYYY-MM-DDTHH:MM, so lexical DESC is chronological DESC.
    # form_date/id are stable fallbacks for old records.
    sql += (
        " ORDER BY COALESCE(NULLIF(a.period_to,''),NULLIF(a.form_date,''),a.created_at) DESC,"
        " a.form_date DESC, a.id DESC"
    )
    return sql, params


def db_stored_path(path):
    return stored_path(path,DATA_ROOT)


def real_data_path(value):
    return resolved_path(value,DATA_ROOT)


def open_external(path):
    """Open a file or directory with the platform's default application."""
    target = str(path)
    if os.name == "nt":
        os.startfile(target)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", target])
    else:
        subprocess.Popen(["xdg-open", target])


def report_font_candidates():
    """System fonts suitable for Ukrainian text in generated PDF reports."""
    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
    ]
    if sys.platform == "darwin":
        candidates.extend([
            str(Path.home() / "Library/Fonts/Arial.ttf"),
            "/Library/Fonts/Arial.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        ])
    candidates.append("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return candidates


def _append_error_log(context, exc, tb=None):
    """Записує технічні подробиці локально, не засмічуючи діалог користувача traceback-ом."""
    try:
        LOG_DIR.mkdir(parents=True,exist_ok=True)
        log_path=LOG_DIR / "Taxo_errors.log"
        stamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if tb is None:
            details="".join(traceback.format_exception(type(exc),exc,exc.__traceback__))
        else:
            details="".join(traceback.format_exception(type(exc),exc,tb))
        with log_path.open("a",encoding="utf-8") as fh:
            fh.write(f"\n[{stamp}] {context}\n{details}\n")
        return log_path
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Єдина обробка помилок під час створення/перезапису вихідних файлів.
# На Windows PDF/Excel часто блокують файл, поки він відкритий у переглядачі.
# Замість сирого [Errno 13] користувач отримує зрозумілий вибір:
# повторити, створити копію з новою назвою або скасувати операцію.
# ---------------------------------------------------------------------------

def _is_file_access_error(exc, path=None):
    """Повертає True для типових помилок блокування/доступу до файла."""
    if isinstance(exc, PermissionError):
        return True
    if not isinstance(exc, OSError):
        return False
    if getattr(exc, "winerror", None) in (5, 32, 33):
        return True
    if getattr(exc, "errno", None) in (1, 13, 16):
        return True
    return False


def _next_output_copy_path(path):
    """Підбирає вільну назву поруч із зайнятим файлом."""
    path=Path(path)
    stamp=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    candidate=path.with_name(f"{path.stem}_{stamp}{path.suffix}")
    if not candidate.exists():
        return candidate
    for n in range(2,1000):
        candidate=path.with_name(f"{path.stem}_{stamp}_{n}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError("Не вдалося підібрати вільну назву вихідного файла.")


def _ask_locked_file_action(parent, path, kind="файл"):
    """Модальний діалог: retry / copy / cancel."""
    result={"value":"cancel"}
    win=tk.Toplevel(parent) if parent is not None else tk.Toplevel()
    win.title("Файл використовується іншою програмою")
    win.resizable(False,False)
    if parent is not None:
        try:
            win.transient(parent)
        except Exception:
            pass
    body=ttk.Frame(win,padding=16)
    body.pack(fill="both",expand=True)
    ttk.Label(
        body,
        text=f"Не вдалося перезаписати {kind}:",
        font=("TkDefaultFont",10,"bold")
    ).pack(anchor="w")
    ttk.Label(
        body,
        text=str(path),
        wraplength=620,
        justify="left"
    ).pack(anchor="w",pady=(6,10))
    ttk.Label(
        body,
        text=(
            "Найчастіше це означає, що файл зараз відкритий у PDF-переглядачі, "
            "Excel або іншій програмі. Закрийте його і натисніть «Повторити».\n\n"
            "Якщо не хочете закривати відкритий файл, Taxo може створити нову копію "
            "поруч із ним з унікальною назвою."
        ),
        wraplength=620,
        justify="left"
    ).pack(anchor="w")

    buttons=ttk.Frame(body)
    buttons.pack(fill="x",pady=(16,0))

    def choose(value):
        result["value"]=value
        win.destroy()

    ttk.Button(buttons,text="Скасувати",command=lambda:choose("cancel")).pack(side="right",padx=(6,0))
    ttk.Button(buttons,text="Створити копію",command=lambda:choose("copy")).pack(side="right",padx=6)
    ttk.Button(buttons,text="Повторити",command=lambda:choose("retry")).pack(side="right")
    win.protocol("WM_DELETE_WINDOW",lambda:choose("cancel"))
    try:
        win.grab_set()
        win.update_idletasks()
        if parent is not None:
            x=parent.winfo_rootx()+max(0,(parent.winfo_width()-win.winfo_reqwidth())//2)
            y=parent.winfo_rooty()+max(0,(parent.winfo_height()-win.winfo_reqheight())//2)
            win.geometry(f"+{x}+{y}")
    except Exception:
        pass
    win.wait_window()
    return result["value"]


def _friendly_file_error(exc, path, kind="файл"):
    path=Path(path)
    if isinstance(exc, FileNotFoundError):
        return f"Не знайдено файл або папку для створення {kind}:\n{path}"
    if isinstance(exc, IsADirectoryError):
        return f"Замість файла вибрано папку:\n{path}"
    if isinstance(exc, OSError) and getattr(exc, "errno", None)==28:
        return f"Недостатньо вільного місця для створення {kind}:\n{path}"
    if _is_file_access_error(exc,path):
        return (
            f"Немає доступу до {kind}:\n{path}\n\n"
            "Перевірте права доступу до папки або закрийте програму, яка використовує файл."
        )
    return f"Не вдалося створити {kind}:\n{path}\n\n{type(exc).__name__}: {exc}"


def write_output_file(writer, target_path, parent=None, kind="файл", error_title="Помилка файла"):
    """Виконує writer(path) з нормальною обробкою блокування файла.

    Повертає фактичний Path. Якщо користувач скасував операцію — None.
    Інші помилки показуються один раз у зрозумілому вигляді і теж повертають None.
    """
    current=Path(target_path)
    while True:
        try:
            current.parent.mkdir(parents=True,exist_ok=True)
            writer(current)
            return current
        except Exception as exc:
            # Відкритий існуючий файл — найтиповіший випадок на Windows.
            # Якщо файла ще немає, PermissionError швидше означає права на папку,
            # тому не пропонуємо безглуздо створювати копію в тій самій папці.
            locked_existing=(current.exists() and _is_file_access_error(exc,current))
            if locked_existing:
                action=_ask_locked_file_action(parent,current,kind)
                if action=="retry":
                    continue
                if action=="copy":
                    current=_next_output_copy_path(current)
                    continue
                return None
            log_path=_append_error_log(f"Створення {kind}: {current}",exc)
            msg=_friendly_file_error(exc,current,kind)
            if log_path is not None:
                msg += f"\n\nТехнічні подробиці записано у:\n{log_path}"
            messagebox.showerror(
                error_title,
                msg,
                parent=parent
            )
            return None


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
    src_con = sqlite3.connect(str(DB_PATH),timeout=30)
    dst_con = sqlite3.connect(str(target),timeout=30)
    try:
        src_con.execute("PRAGMA busy_timeout=30000")
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
        con=sqlite3.connect(str(path),timeout=30)
        con.execute("PRAGMA query_only=ON")
        con.execute("PRAGMA busy_timeout=30000")
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

        src_con=sqlite3.connect(str(source),timeout=30)
        dst_con=sqlite3.connect(str(temp_target),timeout=30)
        try:
            src_con.execute("PRAGMA query_only=ON")
            src_con.execute("PRAGMA busy_timeout=30000")
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
DAY_TYPES = [
    "Робота", "Вихідний", "Відпустка", "Лікарняний", "Відпочинок",
    "Основна щорічна відпустка", "Щорічна додаткова відпустка",
    "Додаткова оплачувана відпустка працівникам з дітьми",
    "Творча відпустка", "Додаткова відпустка у зв’язку з навчанням",
    "Відпустка без збереження зарплати у зв’язку з навчанням",
    "Відпустка без збереження зарплати в обов’язковому порядку",
    "Відпустка без збереження зарплати за згодою сторін",
    "Інші відпустки без збереження зарплати",
    "Відпустка у зв’язку з вагітністю і пологами / догляд до 3 років",
    "Відпустка для догляду за дитиною до 6 років",
    "Оплачувана тимчасова непрацездатність",
    "Неоплачувана тимчасова непрацездатність",
    "Відрядження", "Простій", "Прогул", "Страйк",
    "Інший невідпрацьований час",
    "Інші види неявок за колективними договорами",
    "Неявка з нез’ясованих причин", "Інша причина неявки",
    "Інша робота", "Доступний", "Інше"
]

WORK_MODE_TACHO = "tacho"
WORK_MODE_NO_TACHO = "no_tacho_8h"
WORK_MODE_MANUAL = "manual"

WORK_MODE_LABELS = {
    WORK_MODE_TACHO: "Маршрут — план керування",
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
    con = sqlite3.connect(DB_PATH,timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA busy_timeout=30000")
    # WAL не є безпечним вибором для мережевих файлових систем. Звичайний
    # rollback journal разом із блокуванням всього сховища підтримує почергову
    # роботу встановлених копій Taxo.
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("PRAGMA synchronous=FULL")
    return con


def finish_driver_role(con, employee_id, driver_id, end_date):
    """Завершити лише роль водія, не видаляючи працівника чи історію."""
    con.execute(
        "UPDATE drivers SET active=0,driver_end_date=? WHERE id=?",
        (end_date,driver_id),
    )
    con.execute(
        "DELETE FROM employee_roles WHERE employee_id=? AND role='Водій'",
        (employee_id,),
    )


def sync_legacy_driver_employee(con, dr):
    """Synchronize legacy driver identity without mixing employment and role state.

    drivers.active means only that the current driver role is active.
    employees.active means that the person is employed.  Existing personnel
    status is authoritative and must never be overwritten from drivers.active.
    """
    driver_end=(dr["driver_end_date"] or "").strip() if "driver_end_date" in dr.keys() else ""
    driver_active=bool(dr["active"]) and not bool(driver_end)
    employee=con.execute(
        "SELECT id,active,dismissal_date FROM employees WHERE driver_id=?",
        (dr["id"],),
    ).fetchone()
    if employee:
        eid=employee["id"]
        con.execute(
            """UPDATE employees SET personnel_no=?,last_name=?,first_name=?,middle_name=?,
                   employment_date=?,notes=? WHERE id=?""",
            (
                dr["personnel_no"] or "",dr["last_name"],dr["first_name"],dr["middle_name"] or "",
                dr["employment_date"] or "",dr["notes"] or "",eid,
            ),
        )
        # Repair the exact legacy corruption produced by old startup sync:
        # role was ended (driver_end_date exists), dismissal was never recorded,
        # but employees.active was copied from drivers.active and became 0.
        if driver_end and not (employee["dismissal_date"] or "").strip() and not bool(employee["active"]):
            con.execute("UPDATE employees SET active=1 WHERE id=?",(eid,))
    else:
        # A stored driver role end date is not an employee dismissal date.
        employee_active=1 if driver_end else int(bool(dr["active"]))
        cur=con.execute(
            """INSERT INTO employees(personnel_no,last_name,first_name,middle_name,position,
                   employment_date,notes,active,driver_id,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (
                dr["personnel_no"] or "",dr["last_name"],dr["first_name"],dr["middle_name"] or "",
                "Водій",dr["employment_date"] or "",dr["notes"] or "",employee_active,dr["id"],
                dr["created_at"] or datetime.now().isoformat(timespec="seconds"),
            ),
        )
        eid=cur.lastrowid

    if driver_active:
        con.execute(
            "INSERT OR IGNORE INTO employee_roles(employee_id,role) VALUES(?,?)",
            (eid,"Водій"),
        )
    else:
        con.execute(
            "DELETE FROM employee_roles WHERE employee_id=? AND role='Водій'",
            (eid,),
        )
    return eid


def get_setting(key, default=""):
    try:
        con=db(); r=con.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone(); con.close()
        return (r[0] if r and r[0] is not None else default)
    except Exception:
        return default


def set_setting(key, value):
    con=db(); con.execute("INSERT INTO app_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value))); con.commit(); con.close()


def init_db():
    ensure_workspace(DATA_ROOT)
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
        driver_end_date TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS worklog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        driver_id INTEGER NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
        work_date TEXT NOT NULL,
        day_type TEXT NOT NULL DEFAULT 'Робота',
        start_time TEXT DEFAULT '', -- план керування: початок (legacy name)
        end_time TEXT DEFAULT '',   -- план керування: кінець (legacy name)
        work_start_time TEXT DEFAULT '',
        work_end_time TEXT DEFAULT '',
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
        vehicle TEXT DEFAULT '',
        vehicle_id INTEGER,
        shift_type TEXT DEFAULT 'Безперервна',
        notes TEXT DEFAULT '',
        planned_distance_km INTEGER,
        legacy_template_id INTEGER,
        active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS route_segments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id INTEGER NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
        segment_no INTEGER NOT NULL,
        start_time TEXT DEFAULT '', -- план керування: початок
        end_time TEXT DEFAULT '',   -- план керування: кінець
        work_start_time TEXT DEFAULT '',
        work_end_time TEXT DEFAULT '',
        work_hours REAL DEFAULT 0,
        driving_hours REAL DEFAULT 0,
        activity_type TEXT DEFAULT 'Робота',
        note TEXT DEFAULT '',
        UNIQUE(route_id, segment_no)
    );

    CREATE TABLE IF NOT EXISTS route_stops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id INTEGER NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
        direction TEXT NOT NULL CHECK(direction IN ('outbound','return')),
        stop_no INTEGER NOT NULL,
        stop_name TEXT NOT NULL,
        arrival_time TEXT DEFAULT '',
        departure_time TEXT DEFAULT '',
        note TEXT DEFAULT '',
        day_offset INTEGER NOT NULL DEFAULT 0,
        arrival_day_offset INTEGER NOT NULL DEFAULT 0,
        departure_day_offset INTEGER NOT NULL DEFAULT 0,
        point_type TEXT DEFAULT 'Зупинка',
        UNIQUE(route_id, direction, stop_no)
    );

    CREATE TABLE IF NOT EXISTS dispatch_staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Лікар','Механік')),
        personnel_no TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS dispatch_shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id INTEGER NOT NULL REFERENCES dispatch_staff(id) ON DELETE CASCADE,
        work_date TEXT NOT NULL,
        shift_no INTEGER NOT NULL DEFAULT 1 CHECK(shift_no IN (1,2)),
        start_time TEXT DEFAULT '',
        end_time TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        UNIQUE(staff_id, work_date, shift_no)
    );
    CREATE INDEX IF NOT EXISTS idx_dispatch_shifts_date ON dispatch_shifts(work_date, shift_no);

    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        personnel_no TEXT DEFAULT '',
        last_name TEXT NOT NULL,
        first_name TEXT NOT NULL,
        middle_name TEXT DEFAULT '',
        position TEXT DEFAULT '',
        gender TEXT DEFAULT '',
        tariff_rate REAL,
        phone TEXT DEFAULT '',
        employment_date TEXT DEFAULT '',
        dismissal_date TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        active INTEGER NOT NULL DEFAULT 1,
        driver_id INTEGER UNIQUE REFERENCES drivers(id) ON DELETE SET NULL,
        created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_employees_name ON employees(last_name,first_name,middle_name);

    CREATE TABLE IF NOT EXISTS employee_roles (
        employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
        role TEXT NOT NULL,
        PRIMARY KEY(employee_id, role)
    );

    CREATE TABLE IF NOT EXISTS employee_shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
        role TEXT NOT NULL,
        work_date TEXT NOT NULL,
        shift_no INTEGER NOT NULL DEFAULT 1 CHECK(shift_no IN (1,2)),
        start_time TEXT NOT NULL,
        end_day_offset INTEGER NOT NULL DEFAULT 0 CHECK(end_day_offset BETWEEN 0 AND 7),
        end_time TEXT NOT NULL,
        location TEXT DEFAULT '',
        planned_hours REAL NOT NULL DEFAULT 0,
        actual_hours REAL,
        status TEXT NOT NULL DEFAULT 'planned',
        notes TEXT DEFAULT '',
        UNIQUE(employee_id, role, work_date, shift_no)
    );
    CREATE INDEX IF NOT EXISTS idx_employee_shifts_date ON employee_shifts(work_date, role);

    CREATE TABLE IF NOT EXISTS employee_time_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
        work_date TEXT NOT NULL,
        day_type TEXT NOT NULL DEFAULT 'Робота',
        planned_hours REAL,
        actual_hours REAL,
        overtime_hours REAL,
        night_hours REAL,
        evening_hours REAL,
        weekend_holiday_hours REAL,
        notes TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT DEFAULT '',
        UNIQUE(employee_id, work_date)
    );
    CREATE INDEX IF NOT EXISTS idx_employee_time_entries_date
        ON employee_time_entries(work_date, employee_id);

    CREATE TABLE IF NOT EXISTS waybill_number_pools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series TEXT NOT NULL,
        start_number INTEGER NOT NULL,
        end_number INTEGER NOT NULL,
        next_number INTEGER NOT NULL,
        number_width INTEGER NOT NULL DEFAULT 6,
        valid_from TEXT NOT NULL,
        valid_until TEXT DEFAULT '',
        mode TEXT NOT NULL DEFAULT 'auto' CHECK(mode IN ('auto','manual')),
        status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','closed')),
        notes TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_waybill_pools_dates ON waybill_number_pools(valid_from,valid_until,status);

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
        start_time TEXT DEFAULT '', -- план керування: початок (legacy name)
        end_time TEXT DEFAULT '',   -- план керування: кінець (legacy name)
        work_start_time TEXT DEFAULT '',
        work_end_time TEXT DEFAULT '',
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
        start_time TEXT DEFAULT '', -- план керування: початок (legacy name)
        end_time TEXT DEFAULT '',   -- план керування: кінець (legacy name)
        work_start_time TEXT DEFAULT '',
        work_end_time TEXT DEFAULT '',
        work_hours REAL DEFAULT 0,
        driving_hours REAL DEFAULT 0,
        activity_type TEXT DEFAULT 'Робота',
        note TEXT DEFAULT '',
        UNIQUE(worklog_id, segment_no)
    );

    CREATE TABLE IF NOT EXISTS waybills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worklog_id INTEGER NOT NULL REFERENCES worklog(id) ON DELETE CASCADE,
        driver_id INTEGER NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
        work_date TEXT NOT NULL,
        work_end_date TEXT DEFAULT '',
        issue_year INTEGER NOT NULL,
        issue_seq INTEGER NOT NULL,
        waybill_no TEXT NOT NULL UNIQUE,
        route_id INTEGER,
        route_label TEXT DEFAULT '',
        vehicle_id INTEGER,
        vehicle_label TEXT DEFAULT '',
        planned_departure TEXT DEFAULT '',
        planned_return TEXT DEFAULT '',
        planned_distance_km INTEGER,
        pdf_path TEXT DEFAULT '',
        revision INTEGER NOT NULL DEFAULT 1,
        status TEXT NOT NULL DEFAULT 'active',
        issued_at TEXT NOT NULL,
        updated_at TEXT DEFAULT '',
        UNIQUE(worklog_id),
        UNIQUE(issue_year, issue_seq)
    );
    CREATE INDEX IF NOT EXISTS idx_waybills_date ON waybills(work_date);

    CREATE TABLE IF NOT EXISTS vehicle_odometer_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
        driver_id INTEGER REFERENCES drivers(id) ON DELETE SET NULL,
        work_date TEXT NOT NULL,
        reading_at TEXT DEFAULT '',
        reading_kind TEXT NOT NULL CHECK(reading_kind IN ('start','end','single')),
        reading_km INTEGER NOT NULL CHECK(reading_km >= 0),
        source_type TEXT NOT NULL DEFAULT 'manual',
        source_id INTEGER,
        notes TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT DEFAULT '',
        UNIQUE(source_type, source_id, reading_kind)
    );
    CREATE INDEX IF NOT EXISTS idx_vehicle_odometer_history
        ON vehicle_odometer_readings(vehicle_id, reading_at, id);

    CREATE TABLE IF NOT EXISTS waybill_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        waybill_id INTEGER NOT NULL REFERENCES waybills(id) ON DELETE CASCADE,
        event_type TEXT NOT NULL,
        document_series TEXT DEFAULT '',
        document_number TEXT DEFAULT '',
        internal_no TEXT DEFAULT '',
        revision INTEGER NOT NULL DEFAULT 1,
        pdf_path TEXT DEFAULT '',
        reason TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_waybill_events_waybill ON waybill_events(waybill_id,id);

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
        ("work_start_time", "TEXT DEFAULT ''"),
        ("work_end_time", "TEXT DEFAULT ''"),
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
        ("driver_end_date", "TEXT DEFAULT ''"),
    ]:
        if name not in dcols:
            con.execute(f"ALTER TABLE drivers ADD COLUMN {name} {ddl}")
    if "license_issue_date" not in dcols:
        con.execute("ALTER TABLE drivers ADD COLUMN license_issue_date TEXT DEFAULT ''")
    if "personnel_no" not in dcols:
        con.execute("ALTER TABLE drivers ADD COLUMN personnel_no TEXT DEFAULT ''")

    vcols = {r[1] for r in con.execute("PRAGMA table_info(vehicles)").fetchall()}
    if "garage_no" not in vcols:
        con.execute("ALTER TABLE vehicles ADD COLUMN garage_no TEXT DEFAULT ''")

    for name, ddl in [
        ("waybill_series", "TEXT DEFAULT 'АААТ'"),
        ("transport_column", "TEXT DEFAULT ''"),
        ("brigade", "TEXT DEFAULT ''"),
    ]:
        if name not in ccols:
            con.execute(f"ALTER TABLE company ADD COLUMN {name} {ddl}")

    wbcols = {r[1] for r in con.execute("PRAGMA table_info(waybills)").fetchall()}
    for name in ("doctor_1", "doctor_2", "mechanic_1", "mechanic_2"):
        if name not in wbcols:
            con.execute(f"ALTER TABLE waybills ADD COLUMN {name} TEXT DEFAULT ''")
    for name, ddl in [
        ("work_end_date", "TEXT DEFAULT ''"),
        ("number_pool_id", "INTEGER"),
        ("document_series", "TEXT DEFAULT ''"),
        ("document_number", "TEXT DEFAULT ''"),
        ("internal_no", "TEXT DEFAULT ''"),
        ("start_location", "TEXT DEFAULT ''"),
        ("end_location", "TEXT DEFAULT ''"),
        ("voided_at", "TEXT DEFAULT ''"),
        ("void_reason", "TEXT DEFAULT ''"),
        ("odometer_start", "INTEGER"),
        ("odometer_end", "INTEGER"),
        ("distance_km", "INTEGER"),
        ("planned_distance_km", "INTEGER"),
    ]:
        if name not in wbcols:
            con.execute(f"ALTER TABLE waybills ADD COLUMN {name} {ddl}")
    con.execute("UPDATE waybills SET work_end_date=work_date WHERE COALESCE(work_end_date,'')=''")
    con.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_waybills_document_no "
        "ON waybills(document_series,document_number) WHERE COALESCE(document_number,'')<>''"
    )

    # v9.1 r9.3: реквізити типової форми П-5.
    # Поля додаються без зміни/перезапису існуючих карток працівників.
    ecols = {r[1] for r in con.execute("PRAGMA table_info(employees)").fetchall()}
    for name, ddl in [
        ("gender", "TEXT DEFAULT ''"),
        ("tariff_rate", "REAL"),
    ]:
        if name not in ecols:
            con.execute(f"ALTER TABLE employees ADD COLUMN {name} {ddl}")

    tcols = {r[1] for r in con.execute("PRAGMA table_info(employee_time_entries)").fetchall()}
    for name, ddl in [
        ("overtime_hours", "REAL"),
        ("night_hours", "REAL"),
        ("evening_hours", "REAL"),
        ("weekend_holiday_hours", "REAL"),
    ]:
        if name not in tcols:
            con.execute(f"ALTER TABLE employee_time_entries ADD COLUMN {name} {ddl}")

    # v8.70 r3: єдиний реєстр працівників. Старі водії та працівники
    # випуску не дублюються при кожному запуску і не видаляються.
    def _split_full_name(raw):
        parts=(raw or "").strip().split()
        return (
            parts[0] if parts else "",
            parts[1] if len(parts)>1 else "Без імені",
            " ".join(parts[2:]) if len(parts)>2 else "",
        )

    for dr in con.execute("SELECT * FROM drivers ORDER BY id").fetchall():
        sync_legacy_driver_employee(con, dr)

    staff_map={}
    for st in con.execute("SELECT * FROM dispatch_staff ORDER BY id").fetchall():
        last,first,middle=_split_full_name(st["full_name"])
        employee=con.execute(
            """SELECT e.id FROM employees e JOIN employee_roles er ON er.employee_id=e.id
                 WHERE er.role=? AND lower(e.last_name||' '||e.first_name||' '||e.middle_name)=lower(?)
                 ORDER BY e.active DESC,e.id LIMIT 1""",
            (st["role"]," ".join(x for x in (last,first,middle) if x))
        ).fetchone()
        if employee:
            eid=employee["id"]
        else:
            cur=con.execute(
                """INSERT INTO employees(personnel_no,last_name,first_name,middle_name,position,
                       notes,active,created_at) VALUES(?,?,?,?,?,?,?,?)""",
                (st["personnel_no"] or "",last,first,middle,st["role"],st["notes"] or "",
                 int(st["active"]),st["created_at"] or datetime.now().isoformat(timespec="seconds"))
            )
            eid=cur.lastrowid
        con.execute("INSERT OR IGNORE INTO employee_roles(employee_id,role) VALUES(?,?)",(eid,st["role"]))
        staff_map[st["id"]]=eid

    for sh in con.execute("SELECT * FROM dispatch_shifts ORDER BY id").fetchall():
        eid=staff_map.get(sh["staff_id"])
        if not eid:
            continue
        role_row=con.execute("SELECT role FROM dispatch_staff WHERE id=?",(sh["staff_id"],)).fetchone()
        role=role_row["role"] if role_row else ""
        start=(sh["start_time"] or "").strip() or "00:00"
        end=(sh["end_time"] or "").strip() or "23:59"
        try:
            sm=sum(int(x)*m for x,m in zip(start.split(":"),(60,1)))
            em=sum(int(x)*m for x,m in zip(end.split(":"),(60,1)))
            offset=1 if em<=sm else 0
            planned=round(((em+offset*1440)-sm)/60.0,6)
        except Exception:
            offset=0; planned=0
        con.execute(
            """INSERT OR IGNORE INTO employee_shifts(employee_id,role,work_date,shift_no,start_time,
                   end_day_offset,end_time,planned_hours,status,notes) VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (eid,role,sh["work_date"],sh["shift_no"],start,offset,end,planned,"planned",sh["notes"] or "")
        )

    if not con.execute("SELECT 1 FROM waybill_number_pools LIMIT 1").fetchone():
        company_row=con.execute("SELECT waybill_series FROM company WHERE id=1").fetchone()
        series=((company_row["waybill_series"] if company_row else "") or "АААТ").strip()
        next_no=int(con.execute("SELECT COALESCE(MAX(issue_seq),0)+1 FROM waybills").fetchone()[0])
        con.execute(
            """INSERT INTO waybill_number_pools(series,start_number,end_number,next_number,number_width,
                   valid_from,mode,status,notes,created_at) VALUES(?,?,?,?,?,'1900-01-01','auto','active',?,?)""",
            (series,1,999999,max(1,next_no),6,"Автоматично створено під час переходу на v8.70 r3",
             datetime.now().isoformat(timespec="seconds"))
        )

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

    # v8.66 r9: функціонально об'єднуємо «Маршрути» і «Шаблони маршрутів».
    # Старі таблиці route_templates/route_template_segments НЕ видаляємо — це
    # страховочний legacy-шар. Новий інтерфейс працює тільки з routes +
    # route_segments: один маршрут = один конкретний часовий сценарій.
    route_cols = {r[1] for r in con.execute("PRAGMA table_info(routes)").fetchall()}
    for name, ddl in [
        ("vehicle", "TEXT DEFAULT ''"),
        ("vehicle_id", "INTEGER"),
        ("shift_type", "TEXT DEFAULT 'Безперервна'"),
        ("notes", "TEXT DEFAULT ''"),
        ("legacy_template_id", "INTEGER"),
        ("start_location", "TEXT DEFAULT ''"),
        ("end_location", "TEXT DEFAULT ''"),
        ("start_direction", "TEXT DEFAULT 'outbound'"),
        ("start_day_offset", "INTEGER NOT NULL DEFAULT 0"),
        ("end_day_offset", "INTEGER NOT NULL DEFAULT 0"),
        ("planned_distance_km", "INTEGER"),
    ]:
        if name not in route_cols:
            con.execute(f"ALTER TABLE routes ADD COLUMN {name} {ddl}")

    stop_cols={r[1] for r in con.execute("PRAGMA table_info(route_stops)").fetchall()}
    added_arrival_day="arrival_day_offset" not in stop_cols
    added_departure_day="departure_day_offset" not in stop_cols
    for name,ddl in [
        ("day_offset","INTEGER NOT NULL DEFAULT 0"),
        ("arrival_day_offset","INTEGER NOT NULL DEFAULT 0"),
        ("departure_day_offset","INTEGER NOT NULL DEFAULT 0"),
        ("point_type","TEXT DEFAULT 'Зупинка'"),
    ]:
        if name not in stop_cols:
            con.execute(f"ALTER TABLE route_stops ADD COLUMN {name} {ddl}")
    if added_arrival_day:
        con.execute("UPDATE route_stops SET arrival_day_offset=day_offset")
    if added_departure_day:
        con.execute("UPDATE route_stops SET departure_day_offset=day_offset")
    con.execute("""
        CREATE TABLE IF NOT EXISTS route_segments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_id INTEGER NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
            segment_no INTEGER NOT NULL,
            start_time TEXT DEFAULT '',
            end_time TEXT DEFAULT '',
            work_start_time TEXT DEFAULT '',
            work_end_time TEXT DEFAULT '',
            work_hours REAL DEFAULT 0,
            driving_hours REAL DEFAULT 0,
            activity_type TEXT DEFAULT 'Робота',
            note TEXT DEFAULT '',
            UNIQUE(route_id, segment_no)
        )
    """)

    unify_key = "routes_unified_v8_66_r9"
    unified = con.execute("SELECT value FROM app_settings WHERE key=?", (unify_key,)).fetchone()
    if not unified:
        templates = con.execute("SELECT * FROM route_templates ORDER BY id").fetchall()
        for t in templates:
            target = None
            if "route_id" in t.keys() and t["route_id"]:
                target = con.execute("SELECT * FROM routes WHERE id=?", (t["route_id"],)).fetchone()

            route_name = (t["route_name"] or "").strip() if "route_name" in t.keys() else ""
            if target is None and route_name:
                # У старих шаблонах route_name часто зберігався як відображуваний
                # «код — назва». Спочатку намагаємося знайти відповідний каталог.
                candidates = con.execute("SELECT * FROM routes ORDER BY id").fetchall()
                for r in candidates:
                    label = " — ".join(x for x in ((r["code"] or "").strip(), (r["name"] or "").strip()) if x)
                    if route_name in {(r["name"] or "").strip(), label}:
                        target = r
                        break

            # Якщо до одного legacy-маршруту було прив'язано кілька шаблонів,
            # не втрачаємо жоден: перший наповнює маршрут, наступний стає
            # окремим маршрутом з назвою старого шаблону.
            if target is not None:
                has_segments = con.execute(
                    "SELECT 1 FROM route_segments WHERE route_id=? LIMIT 1", (target["id"],)
                ).fetchone()
                if has_segments:
                    target = None

            if target is None:
                code = ""
                name = route_name or (t["name"] or "").strip() or f"Маршрут {t['id']}"
                if " — " in name:
                    maybe_code, maybe_name = name.split(" — ", 1)
                    if maybe_code.strip() and maybe_name.strip():
                        code, name = maybe_code.strip(), maybe_name.strip()
                existing_name = con.execute("SELECT id FROM routes WHERE name=?", (name,)).fetchone()
                if existing_name:
                    base = (t["name"] or "").strip() or name
                    candidate = base
                    suffix = 2
                    while con.execute("SELECT 1 FROM routes WHERE name=?", (candidate,)).fetchone():
                        candidate = f"{base} ({suffix})"
                        suffix += 1
                    name = candidate
                cur = con.execute(
                    """INSERT INTO routes(
                           name,code,description,vehicle,vehicle_id,shift_type,notes,
                           legacy_template_id,active,created_at
                       ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (
                        name, code, "",
                        (t["vehicle"] or "") if "vehicle" in t.keys() else "",
                        t["vehicle_id"] if "vehicle_id" in t.keys() else None,
                        (t["shift_type"] or "Безперервна") if "shift_type" in t.keys() else "Безперервна",
                        (t["notes"] or "") if "notes" in t.keys() else "",
                        t["id"], int(t["active"] if "active" in t.keys() else 1),
                        t["created_at"] or datetime.now().isoformat(timespec="seconds"),
                    )
                )
                target = con.execute("SELECT * FROM routes WHERE id=?", (cur.lastrowid,)).fetchone()
            else:
                con.execute(
                    """UPDATE routes
                          SET vehicle=?, vehicle_id=?, shift_type=?, notes=?, legacy_template_id=?
                        WHERE id=?""",
                    (
                        (t["vehicle"] or "") if "vehicle" in t.keys() else "",
                        t["vehicle_id"] if "vehicle_id" in t.keys() else None,
                        (t["shift_type"] or "Безперервна") if "shift_type" in t.keys() else "Безперервна",
                        (t["notes"] or "") if "notes" in t.keys() else "",
                        t["id"], target["id"],
                    )
                )

            legacy_segments = con.execute(
                "SELECT * FROM route_template_segments WHERE template_id=? ORDER BY segment_no", (t["id"],)
            ).fetchall()
            for s in legacy_segments:
                ds = (s["start_time"] or "").strip()
                de = (s["end_time"] or "").strip()
                ws = (s["work_start_time"] or "").strip() or ds
                we = (s["work_end_time"] or "").strip() or de
                con.execute(
                    """INSERT OR REPLACE INTO route_segments(
                           route_id,segment_no,start_time,end_time,work_start_time,work_end_time,
                           work_hours,driving_hours,activity_type,note
                       ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (
                        target["id"], s["segment_no"], ds, de, ws, we,
                        s["work_hours"], s["driving_hours"], s["activity_type"], s["note"],
                    )
                )

        con.execute(
            "INSERT INTO app_settings(key,value) VALUES(?,?)",
            (unify_key, datetime.now().isoformat(timespec="seconds"))
        )

    # v8.65 r2: кожен інтервал має окрему пару початок/кінець для
    # робочого часу та для керування. Старі start_time/end_time НЕ
    # перейменовуємо у БД для сумісності: відтепер це саме інтервал
    # КЕРУВАННЯ. Для роботи додаємо work_start_time/work_end_time.
    for table in ("work_segments", "route_template_segments", "route_segments"):
        scols={r[1] for r in con.execute(f"PRAGMA table_info({table})").fetchall()}
        if "work_start_time" not in scols:
            con.execute(f"ALTER TABLE {table} ADD COLUMN work_start_time TEXT DEFAULT ''")
        if "work_end_time" not in scols:
            con.execute(f"ALTER TABLE {table} ADD COLUMN work_end_time TEXT DEFAULT ''")

    # v8.65: розділяємо ПЛАНОВИЙ час керування та робочий час.
    # Історично інтервали маршрутних графіків вводилися саме як час керування,
    # хоча поле/підсумки могли називати його робочим часом. Одноразово
    # нормалізуємо старі записи: джерелом вважаємо driving_hours, якщо воно
    # вже було заповнене, інакше старе work_hours. На старті нового обліку
    # робочий час = часу керування; надалі користувач редагує work_hours
    # незалежно, додаючи іншу роботу. Режим «Без тахо — 8 год» не чіпаємо:
    # там 8 год — саме робочий час, а не керування.
    tm_key="time_model_v8_65_migrated"
    tm_row=con.execute("SELECT value FROM app_settings WHERE key=?",(tm_key,)).fetchone()
    if not tm_row:
        old_count=con.execute("SELECT COUNT(*) FROM worklog").fetchone()[0]
        con.commit()
        if old_count:
            try:
                backup_database("before_v8_65_time_model")
            except Exception:
                # Міграцію не блокуємо через проблему лише з резервною копією;
                # штатний auto-backup усе одно виконується нижче.
                pass

        for table in ("work_segments","route_template_segments","route_segments"):
            con.execute(f"""
                UPDATE {table}
                   SET driving_hours = CASE
                         WHEN COALESCE(driving_hours,0) > 0 THEN driving_hours
                         ELSE COALESCE(work_hours,0)
                       END,
                       work_hours = CASE
                         WHEN COALESCE(driving_hours,0) > 0 THEN driving_hours
                         ELSE COALESCE(work_hours,0)
                       END
            """)

        # Записи без тахографа лишаються 8 год робочого часу / 0 год керування.
        con.execute("""
            UPDATE worklog
               SET driving_hours = CASE
                     WHEN COALESCE(driving_hours,0) > 0 THEN driving_hours
                     ELSE COALESCE(work_hours,0)
                   END,
                   work_hours = CASE
                     WHEN COALESCE(driving_hours,0) > 0 THEN driving_hours
                     ELSE COALESCE(work_hours,0)
                   END
             WHERE COALESCE(accounting_mode,'manual') <> ?
        """,(WORK_MODE_NO_TACHO,))

        # Якщо день має деталізацію, денні підсумки повинні точно дорівнювати
        # сумі його частин після нормалізації.
        con.execute("""
            UPDATE worklog
               SET work_hours = COALESCE((
                       SELECT SUM(ws.work_hours) FROM work_segments ws
                        WHERE ws.worklog_id=worklog.id
                   ),work_hours),
                   driving_hours = COALESCE((
                       SELECT SUM(ws.driving_hours) FROM work_segments ws
                        WHERE ws.worklog_id=worklog.id
                   ),driving_hours)
             WHERE id IN (SELECT DISTINCT worklog_id FROM work_segments)
        """)
        con.execute(
            "INSERT INTO app_settings(key,value) VALUES(?,?)",
            (tm_key,datetime.now().isoformat(timespec="seconds"))
        )
        con.execute(
            "INSERT INTO app_settings(key,value) VALUES('time_model_version','2') "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value"
        )

    # v8.65 r2: часові межі є первинними, тривалості — похідними.
    # Історичні start_time/end_time користувач вводив з графіків саме як
    # час КЕРУВАННЯ. На старті робочі межі копіюємо з них 1:1; надалі
    # користувач розширює/змінює робочий інтервал незалежно.
    interval_key="time_interval_model_v8_65_r2_migrated"
    interval_row=con.execute("SELECT value FROM app_settings WHERE key=?",(interval_key,)).fetchone()
    if not interval_row:
        con.commit()
        try:
            backup_database("before_v8_65_interval_model")
        except Exception:
            pass

        def _legacy_duration_minutes(a,b):
            a=(a or "").strip(); b=(b or "").strip()
            if not a or not b:
                return 0
            try:
                ah,am=map(int,a.split(":")); bh,bm=map(int,b.split(":"))
                x=ah*60+am; y=bh*60+bm
                if y<=x: y+=1440
                return max(0,y-x)
            except Exception:
                return 0

        for table in ("work_segments","route_template_segments","route_segments"):
            rows_i=con.execute(f"SELECT id,start_time,end_time,work_start_time,work_end_time FROM {table}").fetchall()
            for rr in rows_i:
                ds=(rr["start_time"] or "").strip(); de=(rr["end_time"] or "").strip()
                ws=(rr["work_start_time"] or "").strip() or ds
                we=(rr["work_end_time"] or "").strip() or de
                dm=_legacy_duration_minutes(ds,de)
                wm=_legacy_duration_minutes(ws,we)
                con.execute(
                    f"UPDATE {table} SET work_start_time=?,work_end_time=?,work_hours=?,driving_hours=? WHERE id=?",
                    (ws,we,round(wm/60.0,6),round(dm/60.0,6),rr["id"])
                )

        # Денний запис: для маршрутного обліку старі start/end = керування;
        # робочі межі спочатку ті самі. Для «Без тахо — 8 год» start/end
        # лишаємо legacy-полями, а нові робочі межі заповнюємо лише якщо вони
        # були відомі.
        day_rows=con.execute("SELECT * FROM worklog").fetchall()
        for rr in day_rows:
            wid=rr["id"]
            segs_i=con.execute("SELECT * FROM work_segments WHERE worklog_id=? ORDER BY segment_no",(wid,)).fetchall()
            if segs_i:
                drive_segs=[x for x in segs_i if (x["start_time"] or "").strip() and (x["end_time"] or "").strip()]
                work_segs=[x for x in segs_i if (x["work_start_time"] or "").strip() and (x["work_end_time"] or "").strip()]
                ds=drive_segs[0]["start_time"] if drive_segs else ""
                de=drive_segs[-1]["end_time"] if drive_segs else ""
                ws=work_segs[0]["work_start_time"] if work_segs else ""
                we=work_segs[-1]["work_end_time"] if work_segs else ""
                wm=sum(_legacy_duration_minutes(x["work_start_time"],x["work_end_time"]) for x in work_segs)
                dm=sum(_legacy_duration_minutes(x["start_time"],x["end_time"]) for x in drive_segs)
                con.execute("UPDATE worklog SET start_time=?,end_time=?,work_start_time=?,work_end_time=?,work_hours=?,driving_hours=? WHERE id=?",
                            (ds,de,ws,we,round(wm/60.0,6),round(dm/60.0,6),wid))
            else:
                ds=(rr["start_time"] or "").strip(); de=(rr["end_time"] or "").strip()
                ws=(rr["work_start_time"] or "").strip() or ds
                we=(rr["work_end_time"] or "").strip() or de
                if (rr["accounting_mode"] or "manual")==WORK_MODE_NO_TACHO:
                    # Стандартні 8 год не перетворюємо на керування.
                    wm=_legacy_duration_minutes(ws,we)
                    con.execute("UPDATE worklog SET work_start_time=?,work_end_time=?,work_hours=CASE WHEN ?>0 THEN ? ELSE work_hours END,driving_hours=0 WHERE id=?",
                                (ws,we,wm,round(wm/60.0,6),wid))
                else:
                    dm=_legacy_duration_minutes(ds,de)
                    wm=_legacy_duration_minutes(ws,we)
                    con.execute("UPDATE worklog SET work_start_time=?,work_end_time=?,work_hours=?,driving_hours=? WHERE id=?",
                                (ws,we,round(wm/60.0,6),round(dm/60.0,6),wid))

        con.execute("INSERT INTO app_settings(key,value) VALUES(?,?)",
                    (interval_key,datetime.now().isoformat(timespec="seconds")))
        con.execute("INSERT INTO app_settings(key,value) VALUES('time_model_version','3') "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value")

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
    normalize_database_paths(DB_PATH,DATA_ROOT,{
        "waybills":("pdf_path",),
        "waybill_events":("pdf_path",),
        "attestations":("file_path","pdf_path","jpg_page1_path","jpg_page2_path"),
        "attestation_audit":("file_path","pdf_path","jpg_page1_path","jpg_page2_path"),
    })
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
    con.execute("DELETE FROM employee_time_entries WHERE work_date < ?", (cutoff,))

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


def parse_hhmm(value):
    """Перевірити HH:MM і повернути кількість хвилин від початку доби."""
    return time_to_minutes(value)


def waybill_date_range_label(start_date, end_date=None):
    """Дата або повний інтервал дат однієї багатодобової шляхівки."""
    if isinstance(start_date, str):
        start_date=datetime.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date=datetime.strptime(end_date, "%Y-%m-%d").date()
    end_date=end_date or start_date
    if end_date <= start_date:
        return start_date.strftime("%d.%m.%Y")
    return f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"


def waybill_time_label(work_date, day_offset, time_value, show_date=False, separator=" "):
    """Фактична календарна дата й час для друку замість службового D+N."""
    if not time_value:
        return ""
    if isinstance(work_date, str):
        work_date=datetime.strptime(work_date, "%Y-%m-%d").date()
    day_offset=int(day_offset or 0)
    actual_date=work_date+timedelta(days=day_offset)
    if show_date or day_offset:
        return f"{actual_date.strftime('%d.%m.%Y')}{separator}{time_value}"
    return time_value


ROUTE_POINT_TYPES=("АТП","Зупинка","Автостанція","Відпочинок","Нічліг","Інше")


def parse_route_schedule_text(raw, start_day=0, previous_absolute=None):
    """Вставлені рядки маршруту з автоматичним обчисленням D+.

    Формат рядка: назва; прибуття; відправлення; тип; примітка.
    Роздільником може бути Tab, крапка з комою або вертикальна риска.
    Явний день необов'язковий: D+1 00:40. Без нього перехід через
    північ визначається за зменшенням часу.
    """
    rows=[]
    current_day=max(0,int(start_day or 0))
    previous_abs=previous_absolute

    def parse_moment(token):
        nonlocal current_day,previous_abs
        token=(token or "").strip()
        if token in {"","-","—"}:
            return current_day,""
        match=re.fullmatch(r"(?:D\+\s*(\d+)\s+)?(\d{1,2}:\d{2})",token,re.IGNORECASE)
        if not match:
            raise ValueError(f"Невірний час «{token}». Використовуйте ГГ:ХХ або D+1 ГГ:ХХ.")
        explicit=match.group(1)
        value=match.group(2)
        minutes=time_to_minutes(value)
        day=int(explicit) if explicit is not None else current_day
        absolute=day*1440+minutes
        if explicit is None and previous_abs is not None and absolute<previous_abs:
            day=previous_abs//1440+1
            absolute=day*1440+minutes
        if not 0<=day<=7:
            raise ValueError("Автоматичний день вийшов за межі D+0…D+7.")
        current_day=day
        previous_abs=absolute
        return day,value

    for line_no,line in enumerate((raw or "").splitlines(),1):
        line=line.strip()
        if not line:
            continue
        separator="\t" if "\t" in line else ";" if ";" in line else "|" if "|" in line else None
        parts=[part.strip() for part in (line.split(separator) if separator else [line])]
        name=parts[0] if parts else ""
        if name.casefold() in {"назва","зупинка","назва точки","точка маршруту"}:
            continue
        if not name:
            raise ValueError(f"Рядок {line_no}: немає назви точки.")
        single_time=len(parts)==2
        arrival_token=parts[1] if len(parts)>1 else ""
        departure_token=parts[1] if single_time else parts[2] if len(parts)>2 else ""
        point_type=parts[3] if len(parts)>3 else "Зупинка"
        note=parts[4] if len(parts)>4 else ""
        if point_type not in ROUTE_POINT_TYPES:
            note="; ".join(x for x in (point_type,note) if x)
            point_type="Зупинка"
        arrival_day,arrival_time=parse_moment(arrival_token)
        departure_day,departure_time=parse_moment(departure_token)
        rows.append({
            "stop_name":name,
            "arrival_time":arrival_time,
            "departure_time":departure_time,
            "note":note,
            "day_offset":arrival_day if arrival_time else departure_day,
            "arrival_day_offset":arrival_day,
            "departure_day_offset":departure_day,
            "point_type":point_type,
            "_single_time":single_time,
        })
        if len(rows)>15:
            raise ValueError("У напрямку може бути не більше 15 точок форми № 1-АП.")
    if not rows:
        raise ValueError("Вставте хоча б одну точку маршруту.")
    # У найпростішому двоколонковому варіанті «Точка | Час» перша
    # точка має лише відправлення, остання — лише прибуття, а проміжні
    # використовують один плановий час для обох граф форми.
    for index,row in enumerate(rows):
        if row.pop("_single_time",False):
            if index==0:
                row["arrival_time"]=""
            if index==len(rows)-1:
                row["departure_time"]=""
            row["day_offset"]=row["arrival_day_offset"] if row["arrival_time"] else row["departure_day_offset"]
    return rows


def route_schedule_to_text(rows):
    def moment(day,value):
        return f"D+{int(day or 0)} {value}" if value else ""
    return "\n".join(
        "\t".join((
            str(row.get("stop_name","")),
            moment(row.get("arrival_day_offset",0),row.get("arrival_time","")),
            moment(row.get("departure_day_offset",0),row.get("departure_time","")),
            str(row.get("point_type","Зупинка")),
            str(row.get("note","")),
        ))
        for row in rows
    )


def duration_minutes(start, end):
    a = time_to_minutes(start)
    b = time_to_minutes(end)
    if b <= a:
        b += 24 * 60
    return b - a


def segment_duration(start, end):
    return round(duration_minutes(start, end) / 60.0, 2)


def interval_within(inner_start, inner_end, outer_start, outer_end):
    """True, якщо внутрішній HH:MM-інтервал повністю лежить у зовнішньому.

    Коректно працює і для переходу через північ. Порожній внутрішній
    інтервал означає відсутність керування і теж є допустимим.
    """
    if not (inner_start or "").strip() and not (inner_end or "").strip():
        return True
    if not (inner_start or "").strip() or not (inner_end or "").strip():
        return False
    os=time_to_minutes(outer_start); oe=time_to_minutes(outer_end)
    if oe<=os: oe+=1440
    ins=time_to_minutes(inner_start); ine=time_to_minutes(inner_end)
    if ine<=ins: ine+=1440
    for shift in (0,1440,-1440):
        a=ins+shift; b=ine+shift
        if os <= a and b <= oe:
            return True
    return False


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


def signed_hours_hhmm(value):
    try:
        minutes=int((Decimal(str(value).replace(",","."))*Decimal(60)).quantize(Decimal("1"),rounding=ROUND_HALF_UP))
        sign="-" if minutes<0 else "+" if minutes>0 else ""
        minutes=abs(minutes)
        return f"{sign}{minutes//60}:{minutes%60:02d}"
    except Exception:
        return str(value or "")


def parse_optional_odometer(value):
    """Порожнє значення дозволене; введений показник має бути цілими км."""
    raw=str(value or "").strip().replace(" ", "")
    if not raw:
        return None
    if not raw.isdigit():
        raise ValueError("Показник спідометра має бути цілим невід'ємним числом кілометрів.")
    return int(raw)


def parse_optional_route_distance(value):
    """Плановий пробіг маршруту необов'язковий і зберігається у цілих км."""
    raw=str(value or "").strip().replace(" ", "")
    if not raw:
        return None
    if not raw.isdigit() or int(raw)<=0:
        raise ValueError("Плановий пробіг має бути цілим додатним числом кілометрів або порожнім.")
    return int(raw)


def planned_odometer_end(start_value, planned_distance_km):
    """Обчислити прогноз, не перетворюючи його на фактичний показник."""
    if start_value is None or planned_distance_km is None:
        return None
    return int(start_value)+int(planned_distance_km)


def odometer_display(start_value, end_value):
    if start_value is None and end_value is None:
        return "—"
    left="—" if start_value is None else f"{int(start_value):,}".replace(",", " ")
    right="—" if end_value is None else f"{int(end_value):,}".replace(",", " ")
    suffix=""
    if start_value is not None and end_value is not None:
        suffix=f" ({int(end_value)-int(start_value):+d} км)"
    return f"{left} → {right}{suffix}"


def waybill_mileage_display(start_value, end_value, planned_distance_km=None):
    actual=odometer_display(start_value,end_value)
    plan=(f"план {int(planned_distance_km)} км" if planned_distance_km is not None else "")
    if actual=="—":
        return plan or "—"
    return f"{actual}; {plan}" if plan else actual


def odometer_consistency_warnings(con, vehicle_id, start_value=None, end_value=None,
                                  reading_at="", exclude_source_id=None,
                                  planned_distance_km=None):
    """Лише діагностика: жодне попередження не блокує збереження."""
    warnings=[]
    if start_value is not None and end_value is not None and end_value < start_value:
        warnings.append("Кінцевий показник менший за початковий.")
    if (start_value is not None and end_value is not None and
            planned_distance_km is not None and int(planned_distance_km)>0 and
            int(end_value)>=int(start_value)):
        actual_distance=int(end_value)-int(start_value)
        planned_distance=int(planned_distance_km)
        deviation=actual_distance-planned_distance
        tolerance=max(10,planned_distance*0.10)
        if abs(deviation)>tolerance:
            warnings.append(
                f"Фактичний пробіг {actual_distance} км відрізняється від планового "
                f"{planned_distance} км на {deviation:+d} км."
            )
    if not vehicle_id:
        return warnings
    probe=start_value if start_value is not None else end_value
    if probe is None:
        return warnings
    params=[vehicle_id]
    sql="""SELECT reading_km,reading_at,source_type FROM vehicle_odometer_readings
             WHERE vehicle_id=?"""
    if reading_at:
        sql+=" AND (COALESCE(reading_at,'')='' OR reading_at<=?)"
        params.append(reading_at)
    if exclude_source_id is not None:
        sql+=" AND NOT (source_type='waybill' AND source_id=?)"
        params.append(exclude_source_id)
    sql+=" ORDER BY COALESCE(reading_at,'' ) DESC,id DESC LIMIT 1"
    previous=con.execute(sql,params).fetchone()
    if previous and int(probe)<int(previous["reading_km"]):
        label=(previous["reading_at"] or "раніше").replace("T", " ")
        warnings.append(
            f"Новий показник {int(probe)} км менший за попередній "
            f"{int(previous['reading_km'])} км ({label}, джерело: {previous['source_type']})."
        )
    return warnings


def save_waybill_odometer_readings(con, worklog_id, vehicle_id, driver_id, work_date,
                                    start_value=None, end_value=None,
                                    start_at="", end_at="", notes=""):
    """Зберегти або очистити необов'язкові показники, прив'язані до графіка."""
    now=datetime.now().isoformat(timespec="seconds")
    for kind,value,stamp in (("start",start_value,start_at),("end",end_value,end_at)):
        if value is None:
            con.execute(
                "DELETE FROM vehicle_odometer_readings WHERE source_type='waybill' AND source_id=? AND reading_kind=?",
                (worklog_id,kind),
            )
            continue
        con.execute(
            """INSERT INTO vehicle_odometer_readings(
                   vehicle_id,driver_id,work_date,reading_at,reading_kind,reading_km,
                   source_type,source_id,notes,created_at,updated_at
               ) VALUES(?,?,?,?,?,?,'waybill',?,?,?,?)
               ON CONFLICT(source_type,source_id,reading_kind) DO UPDATE SET
                   vehicle_id=excluded.vehicle_id,driver_id=excluded.driver_id,
                   work_date=excluded.work_date,reading_at=excluded.reading_at,
                   reading_km=excluded.reading_km,notes=excluded.notes,
                   updated_at=excluded.updated_at""",
            (vehicle_id,driver_id,work_date,stamp,kind,int(value),worklog_id,notes,now,now),
        )
    distance=(int(end_value)-int(start_value)) if start_value is not None and end_value is not None else None
    con.execute(
        """UPDATE waybills SET odometer_start=?,odometer_end=?,distance_km=?,updated_at=?
             WHERE worklog_id=?""",
        (start_value,end_value,distance,now,worklog_id),
    )


def get_waybill_odometer_readings(con, worklog_id):
    rows=con.execute(
        """SELECT reading_kind,reading_km FROM vehicle_odometer_readings
             WHERE source_type='waybill' AND source_id=?""",(worklog_id,)
    ).fetchall()
    values={row["reading_kind"]:int(row["reading_km"]) for row in rows}
    return values.get("start"),values.get("end")


def _interval_overlap_minutes(start_dt, end_dt, target_date):
    day_start=datetime.combine(target_date,datetime.min.time())
    day_end=day_start+timedelta(days=1)
    return max(0,int((min(end_dt,day_end)-max(start_dt,day_start)).total_seconds()//60))


def _driver_plan_minutes_for_day(con, driver_id, target_date):
    if not driver_id:
        return 0
    rows=con.execute(
        "SELECT * FROM worklog WHERE driver_id=? AND work_date BETWEEN ? AND ? ORDER BY work_date,id",
        (driver_id,(target_date-timedelta(days=7)).isoformat(),target_date.isoformat()),
    ).fetchall()
    exact=[]
    duration_only=0
    for work in rows:
        base=datetime.strptime(work["work_date"],"%Y-%m-%d")
        segments=con.execute(
            "SELECT * FROM work_segments WHERE worklog_id=? ORDER BY segment_no",(work["id"],)
        ).fetchall()
        intervals=normalized_segment_intervals(segments,"work") if segments else []
        if not intervals:
            start=(work["work_start_time"] or work["start_time"] or "").strip()
            end=(work["work_end_time"] or work["end_time"] or "").strip()
            if start and end:
                intervals=[{
                    "start":parse_hhmm(start),
                    "end":parse_hhmm(end),
                }]
                while intervals[0]["end"]<=intervals[0]["start"]:
                    intervals[0]["end"]+=1440
        if intervals:
            for item in intervals:
                exact.append((
                    base+timedelta(minutes=item["start"]),
                    base+timedelta(minutes=item["end"]),
                ))
        elif work["work_date"]==target_date.isoformat():
            duration_only+=hours_value_to_minutes(work["work_hours"] or 0)

    day_start=datetime.combine(target_date,datetime.min.time())
    day_end=day_start+timedelta(days=1)
    clipped=[]
    for start_dt,end_dt in exact:
        start=max(start_dt,day_start); end=min(end_dt,day_end)
        if end>start:
            clipped.append((start,end))
    clipped.sort(key=lambda x:x[0])
    merged=[]
    for start,end in clipped:
        if not merged or start>merged[-1][1]:
            merged.append([start,end])
        else:
            merged[-1][1]=max(merged[-1][1],end)
    exact_minutes=sum(int((end-start).total_seconds()//60) for start,end in merged)
    return exact_minutes+duration_only


def _employee_shift_minutes_for_day(con, employee_id, target_date):
    planned=0; actual=0.0; actual_known=True; found=False
    rows=con.execute(
        "SELECT * FROM employee_shifts WHERE employee_id=? AND work_date BETWEEN ? AND ?",
        (employee_id,(target_date-timedelta(days=7)).isoformat(),target_date.isoformat()),
    ).fetchall()
    for row in rows:
        base=datetime.strptime(row["work_date"],"%Y-%m-%d")
        start_dt=base+timedelta(minutes=parse_hhmm(row["start_time"]))
        end_dt=base+timedelta(days=int(row["end_day_offset"] or 0),minutes=parse_hhmm(row["end_time"]))
        overlap=_interval_overlap_minutes(start_dt,end_dt,target_date)
        if overlap<=0:
            continue
        found=True; planned+=overlap
        if row["actual_hours"] is None:
            actual_known=False
        else:
            duration=max((end_dt-start_dt).total_seconds()/60.0,1.0)
            actual+=hours_value_to_minutes(row["actual_hours"])*overlap/duration
    return planned,(int(round(actual)) if found and actual_known else None),found


def employee_day_time(con, employee_id, target_date):
    """Єдиний рядок табеля: автоматичний план + необов'язковий ручний факт."""
    if isinstance(target_date,str):
        target_date=datetime.strptime(target_date,"%Y-%m-%d").date()
    employee=con.execute("SELECT * FROM employees WHERE id=?",(employee_id,)).fetchone()
    if employee is None:
        raise ValueError("Працівника не знайдено.")
    driver_minutes=_driver_plan_minutes_for_day(con,employee["driver_id"],target_date)
    shift_minutes,shift_actual,shift_found=_employee_shift_minutes_for_day(con,employee_id,target_date)
    automatic_plan=driver_minutes+shift_minutes
    entry=con.execute(
        "SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",
        (employee_id,target_date.isoformat()),
    ).fetchone()
    plan=hours_value_to_minutes(entry["planned_hours"]) if entry and entry["planned_hours"] is not None else automatic_plan
    actual=hours_value_to_minutes(entry["actual_hours"]) if entry and entry["actual_hours"] is not None else shift_actual
    sources=[]
    if driver_minutes: sources.append("графік водія")
    if shift_found: sources.append("зміна персоналу")
    if entry: sources.append("ручний табель")
    return {
        "day_type":entry["day_type"] if entry else ("Робота" if automatic_plan else "Вихідний"),
        "planned_minutes":int(plan),"actual_minutes":actual,
        "source":" + ".join(sources) or "—",
        "notes":entry["notes"] if entry else "","manual":bool(entry),
    }


def employee_employed_on(employee, target_date):
    """Whether an employee belongs to the personnel timesheet on a date."""
    if isinstance(target_date,str):
        target_date=date.fromisoformat(target_date)
    try:
        started=date.fromisoformat((employee["employment_date"] or "").strip())
    except (ValueError,TypeError,KeyError,IndexError):
        started=None
    try:
        finished=date.fromisoformat((employee["dismissal_date"] or "").strip())
    except (ValueError,TypeError,KeyError,IndexError):
        finished=None
    return (started is None or target_date>=started) and (finished is None or target_date<=finished)


def employee_name(employee):
    return " ".join(
        x for x in (employee["last_name"],employee["first_name"],employee["middle_name"]) if x
    ).strip()


def collect_employee_timesheet(employee_id, year, month):
    """Daily plan/fact rows and totals for one employee and one month."""
    y=int(year); m=int(month); days=month_dates(y,m)
    con=db()
    employee=con.execute(
        """SELECT e.*,GROUP_CONCAT(er.role, ', ') roles FROM employees e
           LEFT JOIN employee_roles er ON er.employee_id=e.id
           WHERE e.id=? GROUP BY e.id""",
        (employee_id,),
    ).fetchone()
    if employee is None:
        con.close(); raise ValueError("Працівника не знайдено.")
    company=con.execute("SELECT * FROM company WHERE id=1").fetchone()
    rows=[]; planned=actual=missing=work_days=0
    weekday_names=("Пн","Вт","Ср","Чт","Пт","Сб","Нд")
    for work_date in days:
        employed=employee_employed_on(employee,work_date)
        row=employee_day_time(con,employee_id,work_date) if employed else {
            "day_type":"—","planned_minutes":0,"actual_minutes":None,
            "source":"поза періодом роботи","notes":"","manual":False,
        }
        difference=(row["actual_minutes"]-row["planned_minutes"]) if row["actual_minutes"] is not None else None
        rows.append({
            "date":work_date,"weekday":weekday_names[work_date.weekday()],
            "day_type":row["day_type"],"planned_minutes":row["planned_minutes"],
            "actual_minutes":row["actual_minutes"],"difference_minutes":difference,
            "source":row["source"],"notes":row["notes"],"manual":row["manual"],
            "employed":employed,
        })
        if employed:
            planned+=row["planned_minutes"]
            if row["actual_minutes"] is not None:
                actual+=row["actual_minutes"]
            elif row["planned_minutes"]>0:
                missing+=1
            if row["planned_minutes"]>0 or (row["actual_minutes"] or 0)>0:
                work_days+=1
    con.close()
    return {
        "year":y,"month":m,"employee":employee,"company":company,"rows":rows,
        "planned_minutes":planned,"actual_minutes":actual,
        "difference_minutes":actual-planned,"missing_days":missing,"work_days":work_days,
    }


def collect_personnel_monthly_balance(year, month, active_only=True):
    """Monthly actual-hours grid for all personnel, including missing-fact control."""
    y=int(year); m=int(month); days=month_dates(y,m); con=db()
    sql="""SELECT e.*,GROUP_CONCAT(er.role, ', ') roles FROM employees e
           LEFT JOIN employee_roles er ON er.employee_id=e.id"""
    if active_only:
        sql += " WHERE e.active=1"
    sql += " GROUP BY e.id ORDER BY e.active DESC,e.last_name,e.first_name,e.middle_name"
    employees=con.execute(sql).fetchall()
    company=con.execute("SELECT * FROM company WHERE id=1").fetchone()
    out=[]
    codes={
        "Вихідний":"Вих","Відпустка":"В","Основна щорічна відпустка":"В",
        "Щорічна додаткова відпустка":"Д","Додаткова оплачувана відпустка працівникам з дітьми":"ДО",
        "Творча відпустка":"ТВ","Додаткова відпустка у зв’язку з навчанням":"Н",
        "Відпустка без збереження зарплати у зв’язку з навчанням":"НБ",
        "Відпустка без збереження зарплати в обов’язковому порядку":"ДБ",
        "Відпустка без збереження зарплати за згодою сторін":"НА",
        "Інші відпустки без збереження зарплати":"БЗ",
        "Відпустка у зв’язку з вагітністю і пологами / догляд до 3 років":"ВП",
        "Відпустка для догляду за дитиною до 6 років":"ДД",
        "Лікарняний":"ТН","Оплачувана тимчасова непрацездатність":"ТН",
        "Неоплачувана тимчасова непрацездатність":"НН",
        "Відрядження":"ВД","Простій":"П","Прогул":"ПР","Страйк":"С",
        "Інший невідпрацьований час":"ІН","Інші види неявок за колективними договорами":"ІВ",
        "Неявка з нез’ясованих причин":"НЗ","Інша причина неявки":"І",
        "Відпочинок":"Відпч","Доступний":"Гот","Інша робота":"Інш","Інше":"Інш"
    }
    for employee in employees:
        if not any(employee_employed_on(employee,d) for d in days):
            continue
        cells=[]; planned=actual=missing=work_days=0
        for d in days:
            if not employee_employed_on(employee,d):
                cells.append(""); continue
            row=employee_day_time(con,employee["id"],d)
            planned += row["planned_minutes"]
            if row["actual_minutes"] is not None:
                actual += row["actual_minutes"]
                cells.append(minutes_hhmm(row["actual_minutes"]) if row["actual_minutes"]>0 else codes.get(row["day_type"],"0:00"))
            elif row["planned_minutes"]>0:
                missing += 1; cells.append("—")
            else:
                cells.append(codes.get(row["day_type"],"В" if d.weekday()>=5 else ""))
            if row["planned_minutes"]>0 or (row["actual_minutes"] or 0)>0:
                work_days += 1
        out.append({
            "employee_id":employee["id"],"personnel_no":employee["personnel_no"] or "",
            "name":employee_name(employee),"roles":employee["roles"] or employee["position"] or "",
            "cells":cells,"work_days":work_days,"planned_min":planned,"actual_min":actual,
            "difference_min":actual-planned,"missing_days":missing,
        })
    con.close()
    return {"year":y,"month":m,"days":days,"employees":out,"company":company}


def export_employee_timesheet_xlsx(employee_id, year, month, out_path):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    data=collect_employee_timesheet(employee_id,year,month)
    wb=Workbook(); ws=wb.active; ws.title="Щоденний табель"
    headers=["Дата","День","Вид дня","План","Факт","Відхилення","Джерело","Примітка"]
    ws.merge_cells("A1:H1"); ws["A1"]=(data["company"]["name"] if data["company"] else "") or ""
    ws.merge_cells("A2:H2"); ws["A2"]=f"ТАБЕЛЬ РОБОЧОГО ЧАСУ — {employee_name(data['employee'])} — {month_name_ua(data['month'])} {data['year']}"
    for cell in (ws["A1"],ws["A2"]):
        cell.font=Font(bold=True,size=14); cell.alignment=Alignment(horizontal="center")
    thin=Side(style="thin",color="777777"); border=Border(left=thin,right=thin,top=thin,bottom=thin)
    for col,label in enumerate(headers,1):
        c=ws.cell(4,col,label); c.font=Font(bold=True); c.fill=PatternFill("solid",fgColor="D9E6F2"); c.border=border; c.alignment=Alignment(horizontal="center")
    for row_no,row in enumerate(data["rows"],5):
        values=[row["date"].strftime("%d.%m.%Y"),row["weekday"],row["day_type"],minutes_hhmm(row["planned_minutes"]),
                minutes_hhmm(row["actual_minutes"]) if row["actual_minutes"] is not None else "—",
                signed_hours_hhmm(row["difference_minutes"]/60) if row["difference_minutes"] is not None else "—",row["source"],row["notes"]]
        for col,value in enumerate(values,1):
            c=ws.cell(row_no,col,value); c.border=border; c.alignment=Alignment(vertical="top",wrap_text=True)
        if not row["employed"]:
            for col in range(1,9): ws.cell(row_no,col).fill=PatternFill("solid",fgColor="EEEEEE")
        elif row["planned_minutes"]>0 and row["actual_minutes"] is None:
            ws.cell(row_no,5).fill=PatternFill("solid",fgColor="FFF2CC")
    total_row=5+len(data["rows"])
    ws.cell(total_row,1,"РАЗОМ"); ws.cell(total_row,4,minutes_hhmm(data["planned_minutes"])); ws.cell(total_row,5,minutes_hhmm(data["actual_minutes"])); ws.cell(total_row,6,signed_hours_hhmm(data["difference_minutes"]/60)); ws.cell(total_row,7,f"Без факту: {data['missing_days']}")
    for col in range(1,9): ws.cell(total_row,col).font=Font(bold=True); ws.cell(total_row,col).border=border
    widths=[13,8,18,10,10,13,25,34]
    for col,width in enumerate(widths,1): ws.column_dimensions[get_column_letter(col)].width=width
    ws.freeze_panes="A5"; ws.auto_filter.ref=f"A4:H{total_row-1}"; ws.sheet_view.showGridLines=False
    ws.page_setup.orientation="landscape"; ws.page_setup.paperSize=ws.PAPERSIZE_A4; ws.page_setup.fitToWidth=1; ws.page_setup.fitToHeight=0; ws.sheet_properties.pageSetUpPr.fitToPage=True
    ws.print_title_rows="1:4"; ws.print_area=f"A1:H{total_row}"
    wb.save(str(out_path)); return data


def export_employee_timesheet_pdf(employee_id, year, month, out_path):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from xml.sax.saxutils import escape
    data=collect_employee_timesheet(employee_id,year,month)
    font_name="Helvetica"; font_path=next((p for p in report_font_candidates() if os.path.exists(p)),None)
    if font_path:
        try:
            if "PersonnelTimesheetFont" not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont("PersonnelTimesheetFont",font_path))
            font_name="PersonnelTimesheetFont"
        except Exception: pass
    doc=SimpleDocTemplate(str(out_path),pagesize=landscape(A4),leftMargin=14,rightMargin=14,topMargin=14,bottomMargin=14)
    styles=getSampleStyleSheet(); normal=ParagraphStyle("PersonnelNormal",parent=styles["Normal"],fontName=font_name,fontSize=7.7,leading=9)
    center=ParagraphStyle("PersonnelCenter",parent=normal,alignment=1); title=ParagraphStyle("PersonnelTitle",parent=center,fontSize=13,leading=15,spaceAfter=5)
    story=[]; company=(data["company"]["name"] if data["company"] else "") or ""
    if company: story.append(Paragraph(f"<b>{escape(company)}</b>",title))
    story.append(Paragraph(f"<b>ТАБЕЛЬ РОБОЧОГО ЧАСУ — {escape(employee_name(data['employee']))}</b><br/>{month_name_ua(data['month'])} {data['year']}",title)); story.append(Spacer(1,3))
    headers=["Дата","День","Вид дня","План","Факт","Відх.","Джерело","Примітка"]
    rows=[[Paragraph(f"<b>{escape(h)}</b>",center) for h in headers]]
    for row in data["rows"]:
        vals=[row["date"].strftime("%d.%m.%Y"),row["weekday"],row["day_type"],minutes_hhmm(row["planned_minutes"]),minutes_hhmm(row["actual_minutes"]) if row["actual_minutes"] is not None else "—",signed_hours_hhmm(row["difference_minutes"]/60) if row["difference_minutes"] is not None else "—",row["source"],row["notes"]]
        rows.append([Paragraph(escape(str(v)),center if i<6 else normal) for i,v in enumerate(vals)])
    rows.append([Paragraph("<b>РАЗОМ</b>",normal),"","",Paragraph(f"<b>{minutes_hhmm(data['planned_minutes'])}</b>",center),Paragraph(f"<b>{minutes_hhmm(data['actual_minutes'])}</b>",center),Paragraph(f"<b>{signed_hours_hhmm(data['difference_minutes']/60)}</b>",center),Paragraph(f"Без факту: {data['missing_days']}",normal),""])
    table=Table(rows,colWidths=[54,34,72,42,42,48,120,220],repeatRows=1)
    style=[("FONTNAME",(0,0),(-1,-1),font_name),("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#777777")),("BACKGROUND",(0,0),(-1,0),colors.HexColor("#D9E6F2")),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),2),("RIGHTPADDING",(0,0),(-1,-1),2),("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),("BACKGROUND",(0,len(rows)-1),(-1,len(rows)-1),colors.HexColor("#EAF2F8"))]
    for idx,row in enumerate(data["rows"],1):
        if not row["employed"]: style.append(("BACKGROUND",(0,idx),(-1,idx),colors.HexColor("#EEEEEE")))
        elif row["planned_minutes"]>0 and row["actual_minutes"] is None: style.append(("BACKGROUND",(4,idx),(4,idx),colors.HexColor("#FFF2CC")))
    table.setStyle(TableStyle(style)); story.append(table); doc.build(story); return data


def format_hours(value):
    try:
        return f"{float(value):.2f}".rstrip("0").rstrip(".")
    except Exception:
        return "0"


def _segment_work_pair(r):
    ws=(r["work_start_time"] if "work_start_time" in r.keys() else "") or r["start_time"]
    we=(r["work_end_time"] if "work_end_time" in r.keys() else "") or r["end_time"]
    return ws,we


def segments_summary(segments):
    if not segments:
        return ""
    parts=[]
    for r in segments:
        ws,we=_segment_work_pair(r)
        ds=(r["start_time"] or "").strip(); de=(r["end_time"] or "").strip()
        work=f"роб. {ws}-{we}" if ws and we else "роб. —"
        drive=f"кер. {ds}-{de}" if ds and de else "кер. —"
        parts.append(f"{work}; {drive}")
    return " / ".join(parts)


def normalized_segment_intervals(segments, pair="work"):
    """Return exact segment intervals as absolute minutes in editor order.

    Day rollover is inferred from a rollback of the *start* clock relative to
    the previous segment start. Crucially, a start such as 15:30 after a
    14:10–15:45 segment stays on the same day and is therefore recognized as
    a 15-minute overlap instead of being turned into a fake 23:45 gap.
    """
    out=[]
    previous_start=None
    for index,r in enumerate(segments or []):
        if pair=="drive":
            a=str(_record_value(r,"start_time","") or "").strip()
            b=str(_record_value(r,"end_time","") or "").strip()
        else:
            a,b=_segment_work_pair(r)
            a=str(a or "").strip(); b=str(b or "").strip()
        if not a or not b:
            continue
        start=time_to_minutes(a)
        while previous_start is not None and start < previous_start:
            start += 24*60
        end=time_to_minutes(b)+(start//(24*60))*(24*60)
        while end <= start:
            end += 24*60
        out.append({
            "index":index,
            "start":start,
            "end":end,
            "start_text":a,
            "end_text":b,
        })
        previous_start=start
    return out


def segment_overlap_details(segments, pair="work"):
    intervals=normalized_segment_intervals(segments,pair=pair)
    if len(intervals)<2:
        return []
    overlaps=[]
    active=intervals[0]
    active_end=active["end"]
    for current in intervals[1:]:
        if current["start"] < active_end:
            overlaps.append({
                "left_index":active["index"],
                "right_index":current["index"],
                "left_start":active["start_text"],
                "left_end":active["end_text"],
                "right_start":current["start_text"],
                "right_end":current["end_text"],
                "minutes":min(active_end,current["end"])-current["start"],
            })
        if current["end"] > active_end:
            active=current
            active_end=current["end"]
    return overlaps


def segments_union_minutes(segments, pair="work"):
    intervals=normalized_segment_intervals(segments,pair=pair)
    if not intervals:
        return 0
    merged=[]
    for item in intervals:
        start=item["start"]; end=item["end"]
        if not merged or start > merged[-1][1]:
            merged.append([start,end])
        else:
            merged[-1][1]=max(merged[-1][1],end)
    return sum(end-start for start,end in merged)


def segments_overlap_minutes(segments, pair="work"):
    intervals=normalized_segment_intervals(segments,pair=pair)
    raw=sum(item["end"]-item["start"] for item in intervals)
    return max(0,raw-segments_union_minutes(segments,pair=pair))


def gaps_minutes(segments, pair="work"):
    intervals=normalized_segment_intervals(segments,pair=pair)
    if len(intervals)<2:
        return []
    out=[]
    current_end=intervals[0]["end"]
    for item in intervals[1:]:
        if item["start"] > current_end:
            out.append(item["start"]-current_end)
        current_end=max(current_end,item["end"])
    return out


def gaps_summary(segments, pair="work"):
    return ", ".join(minutes_hhmm(x) for x in gaps_minutes(segments,pair=pair))


def segment_overlap_message(segments, pair="work"):
    details=segment_overlap_details(segments,pair=pair)
    if not details:
        return ""
    first=details[0]
    return (
        f"частини №{first['left_index']+1} "
        f"({first['left_start']}–{first['left_end']}) і "
        f"№{first['right_index']+1} "
        f"({first['right_start']}–{first['right_end']}) "
        f"перекриваються на {minutes_hhmm(first['minutes'])}"
    )


def segment_integrity_issues(segments):
    """Validate one exact multi-part scenario without changing stored data."""
    segments=list(segments or [])
    issues=[]

    for pair,label in (("work","Робочий час"),("drive","Керування")):
        try:
            overlaps=segment_overlap_details(segments,pair=pair)
        except Exception as exc:
            issues.append({
                "kind":"invalid_time",
                "label":label,
                "minutes":0,
                "message":f"{label}: некоректний час ({exc})",
            })
            continue
        for item in overlaps:
            issues.append({
                "kind":f"{pair}_overlap",
                "label":label,
                "minutes":int(item["minutes"]),
                "message":(
                    f"{label}: частини №{item['left_index']+1} "
                    f"({item['left_start']}–{item['left_end']}) і "
                    f"№{item['right_index']+1} "
                    f"({item['right_start']}–{item['right_end']}) "
                    f"перекриваються на {minutes_hhmm(item['minutes'])}"
                ),
            })

    for index,row in enumerate(segments,1):
        ds=str(_record_value(row,"start_time","") or "").strip()
        de=str(_record_value(row,"end_time","") or "").strip()
        ws,we=_segment_work_pair(row)
        ws=str(ws or "").strip(); we=str(we or "").strip()

        if not any((ds,de,ws,we)):
            issues.append({
                "kind":"empty_segment",
                "label":"Порожня частина",
                "minutes":0,
                "message":f"Частина №{index}: не задано жодних часових меж.",
            })
            continue

        if bool(ds) != bool(de):
            issues.append({
                "kind":"incomplete_drive",
                "label":"Керування",
                "minutes":0,
                "message":f"Частина №{index}: неповна пара часу керування ({ds or '—'}–{de or '—'}).",
            })
        if bool(ws) != bool(we):
            issues.append({
                "kind":"incomplete_work",
                "label":"Робочий час",
                "minutes":0,
                "message":f"Частина №{index}: неповна пара робочого часу ({ws or '—'}–{we or '—'}).",
            })
        if ds and de and ws and we:
            try:
                if not interval_within(ds,de,ws,we):
                    issues.append({
                        "kind":"drive_outside_work",
                        "label":"Керування поза роботою",
                        "minutes":0,
                        "message":(
                            f"Частина №{index}: керування {ds}–{de} "
                            f"не повністю лежить у робочому інтервалі {ws}–{we}."
                        ),
                    })
            except Exception as exc:
                issues.append({
                    "kind":"invalid_time",
                    "label":"Некоректний час",
                    "minutes":0,
                    "message":f"Частина №{index}: {exc}",
                })

    # Keep messages stable and unique if one malformed interval is noticed by
    # more than one validation rule.
    unique=[]
    seen=set()
    for issue in issues:
        key=(issue["kind"],issue["message"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(issue)
    return unique


def collect_schedule_integrity_audit(
        year, month, active_routes_only=True, work_date=None,
        include_days=True, include_routes=True):
    """Scan stored driver days and/or route templates for input-time defects.

    This is deliberately a technical data-integrity audit. It does not claim
    to replace the separate regulatory control under Regulation №340.

    work_date limits the driver-day scan to one ISO/date value while route
    templates remain independently controlled through include_routes.
    Legacy worklog rows without work_segments are still inspected whenever
    they contain exact clock fields.
    """
    y=int(year); m=int(month)
    days=month_dates(y,m)
    month_start=days[0].isoformat(); month_end=days[-1].isoformat()
    if isinstance(work_date,date):
        day_iso=work_date.isoformat()
    elif work_date:
        day_iso=str(work_date)
    else:
        day_iso=None
    start=day_iso or month_start
    end=day_iso or month_end

    con=db()
    findings=[]
    worklogs=[]
    routes=[]
    inspected_day_records=0
    exact_day_records=0
    legacy_exact_day_records=0
    inspected_route_records=0

    if include_days:
        worklogs=con.execute(
            """SELECT w.*,
                      d.last_name,d.first_name,d.middle_name,
                      COALESCE(r.name,w.route_name,'') AS audit_route_name,
                      COALESCE(r.code,'') AS audit_route_code
                 FROM worklog w
                 JOIN drivers d ON d.id=w.driver_id
                 LEFT JOIN routes r ON r.id=w.route_id
                WHERE w.work_date BETWEEN ? AND ?
                ORDER BY w.work_date,d.last_name,d.first_name,w.id""",
            (start,end),
        ).fetchall()

        for row in worklogs:
            inspected_day_records += 1
            segs=con.execute(
                "SELECT * FROM work_segments WHERE worklog_id=? ORDER BY segment_no",
                (row["id"],),
            ).fetchall()

            check_segments=list(segs)
            if check_segments:
                exact_day_records += 1
            else:
                ds=str(_record_value(row,"start_time","") or "").strip()
                de=str(_record_value(row,"end_time","") or "").strip()
                ws=str(_record_value(row,"work_start_time","") or "").strip()
                we=str(_record_value(row,"work_end_time","") or "").strip()
                if any((ds,de,ws,we)):
                    legacy_exact_day_records += 1
                    exact_day_records += 1
                    check_segments=[{
                        "start_time":ds,
                        "end_time":de,
                        "work_start_time":ws or ds,
                        "work_end_time":we or de,
                    }]

            driver=" ".join(
                x for x in (row["last_name"],row["first_name"],row["middle_name"]) if x
            ).strip()
            route_name=(row["audit_route_name"] or "").strip()
            route_code=(row["audit_route_code"] or "").strip()
            route_label=" / ".join(x for x in (route_code,route_name) if x)

            for issue in segment_integrity_issues(check_segments):
                findings.append({
                    **issue,
                    "source_kind":"worklog",
                    "source":"День водія",
                    "worklog_id":row["id"],
                    "driver_id":row["driver_id"],
                    "route_id":row["route_id"] if "route_id" in row.keys() else None,
                    "date":row["work_date"],
                    "subject":driver,
                    "route":route_label,
                })

    if include_routes:
        route_sql="SELECT * FROM routes"
        if active_routes_only:
            route_sql += " WHERE active=1"
        route_sql += " ORDER BY code,name,id"
        routes=con.execute(route_sql).fetchall()
        for route in routes:
            inspected_route_records += 1
            segs=con.execute(
                "SELECT * FROM route_segments WHERE route_id=? ORDER BY segment_no",
                (route["id"],),
            ).fetchall()
            code=str(route["code"] or "").strip() if "code" in route.keys() else ""
            name=str(route["name"] or "").strip()
            subject=" / ".join(x for x in (code,name) if x) or f"Маршрут #{route['id']}"
            if not segs:
                findings.append({
                    "kind":"route_no_segments",
                    "label":"Немає часових частин",
                    "minutes":0,
                    "message":"Активний маршрут не має жодної часової частини; його не можна надійно застосувати до графіка.",
                    "source_kind":"route",
                    "source":"Шаблон маршруту",
                    "worklog_id":None,
                    "driver_id":None,
                    "route_id":route["id"],
                    "date":"",
                    "subject":subject,
                    "route":subject,
                })
                continue
            for issue in segment_integrity_issues(segs):
                findings.append({
                    **issue,
                    "source_kind":"route",
                    "source":"Шаблон маршруту",
                    "worklog_id":None,
                    "driver_id":None,
                    "route_id":route["id"],
                    "date":"",
                    "subject":subject,
                    "route":subject,
                })

    con.close()
    day_findings=sum(1 for x in findings if x["source_kind"]=="worklog")
    route_findings=sum(1 for x in findings if x["source_kind"]=="route")
    return {
        "year":y,
        "month":m,
        "period_start":start,
        "period_end":end,
        "work_date":day_iso,
        "active_routes_only":bool(active_routes_only),
        "include_days":bool(include_days),
        "include_routes":bool(include_routes),
        "findings":findings,
        "day_findings":day_findings,
        "route_findings":route_findings,
        "worklog_count":len(worklogs),
        "route_count":len(routes),
        "inspected_day_records":inspected_day_records,
        "exact_day_records":exact_day_records,
        "legacy_exact_day_records":legacy_exact_day_records,
        "inspected_route_records":inspected_route_records,
    }


def schedule_audit_day_status_text(data):
    """Human-readable one-line status for the currently visible schedule day."""
    data=data or {}
    findings=list(data.get("findings") or [])
    inspected=int(data.get("inspected_day_records") or 0)
    if findings:
        return f"⚠ день: {len(findings)} помилк."
    if inspected<=0:
        return "○ день: записів для аудиту немає"
    exact=int(data.get("exact_day_records") or 0)
    if exact<=0:
        return "○ день: є запис, але точний час не задано"
    return "✓ день: помилок введення немає"


def _record_value(record, key, default=""):
    """Read sqlite Row/dict values without forcing callers to care about the row type."""
    if record is None:
        return default
    try:
        if key in record.keys():
            return record[key]
    except Exception:
        pass
    if isinstance(record, dict):
        return record.get(key, default)
    return default


def driver_day_view(work_day, worklog=None, segments=None, day_type_override=None,
                    suppress_plan=False):
    """Canonical state for one driver's day used by all driver-time views.

    Exact intervals are the source of truth when available. Their UNION, not
    the raw sum, defines work/driving duration, so overlapping parts cannot
    double-count minutes. Historical rows stay unchanged in the database.
    """
    segments=list(segments or [])
    raw_type=str(_record_value(worklog, "day_type", "") or "").strip()
    default_type="Вихідний" if work_day.weekday() >= 5 else "Робота"
    day_type=str(day_type_override or raw_type or default_type).strip()

    effective_segments=[] if suppress_plan else segments
    schedule=""
    breaks=""
    bands=[]
    work_overlap_minutes=0
    driving_overlap_minutes=0
    exact_work_minutes=None
    exact_driving_minutes=None

    if effective_segments:
        schedule=segments_summary(effective_segments)
        gap_text=gaps_summary(effective_segments)
        work_overlap_minutes=segments_overlap_minutes(effective_segments,"work")
        driving_overlap_minutes=segments_overlap_minutes(effective_segments,"drive")
        warning=(
            f"⚠ перекриття {minutes_hhmm(work_overlap_minutes)}"
            if work_overlap_minutes>0 else ""
        )
        breaks="; ".join(x for x in (warning,gap_text) if x)
        exact_work_minutes=segments_union_minutes(effective_segments,"work")
        exact_driving_minutes=segments_union_minutes(effective_segments,"drive")
        for seg in effective_segments:
            ws,we=_segment_work_pair(seg)
            ds=str(_record_value(seg, "start_time", "") or "").strip()
            de=str(_record_value(seg, "end_time", "") or "").strip()
            if ws and we:
                bands.append(("Робота", ws, we))
            if ds and de:
                bands.append(("Керування", ds, de))
    elif worklog is not None and not suppress_plan:
        ws=(str(_record_value(worklog, "work_start_time", "") or "").strip()
            or str(_record_value(worklog, "start_time", "") or "").strip())
        we=(str(_record_value(worklog, "work_end_time", "") or "").strip()
            or str(_record_value(worklog, "end_time", "") or "").strip())
        ds=str(_record_value(worklog, "start_time", "") or "").strip()
        de=str(_record_value(worklog, "end_time", "") or "").strip()
        drive=f"кер. {ds}-{de}" if ds and de else "кер. —"
        schedule=f"роб. {ws}-{we}; {drive}" if ws and we else drive
        if ws and we:
            bands.append(("Робота", ws, we))
            try:
                exact_work_minutes=duration_minutes(ws,we)
            except Exception:
                exact_work_minutes=None
        if ds and de:
            bands.append(("Керування", ds, de))
            try:
                exact_driving_minutes=duration_minutes(ds,de)
            except Exception:
                exact_driving_minutes=None

    explicit=worklog is not None
    if bands:
        status_label=""
    elif suppress_plan and day_type:
        status_label=day_type
    elif day_type and day_type != "Робота":
        status_label=day_type
    elif explicit:
        status_label="Робота · час не задано"
    elif work_day.weekday() >= 5:
        status_label="Вихідний"
    else:
        status_label="Немає плану"

    if suppress_plan:
        work_minutes=driving_minutes=overtime_minutes=0
    else:
        work_minutes=(
            exact_work_minutes if exact_work_minutes is not None
            else hours_value_to_minutes(_record_value(worklog, "work_hours", 0))
        )
        driving_minutes=(
            exact_driving_minutes if exact_driving_minutes is not None
            else hours_value_to_minutes(_record_value(worklog, "driving_hours", 0))
        )
        overtime_minutes=hours_value_to_minutes(
            _record_value(worklog, "overtime_hours", 0)
        )

    return {
        "day_type": day_type,
        "schedule": schedule,
        "breaks": breaks,
        "bands": bands,
        "status_label": status_label,
        "work_minutes": int(work_minutes or 0),
        "driving_minutes": int(driving_minutes or 0),
        "overtime_minutes": int(overtime_minutes or 0),
        "work_overlap_minutes":int(work_overlap_minutes or 0),
        "driving_overlap_minutes":int(driving_overlap_minutes or 0),
        "suppressed_plan": bool(suppress_plan),
        "explicit_worklog": explicit,
    }


def month_dates(year, month):
    days = calendar.monthrange(year, month)[1]
    return [date(year, month, d) for d in range(1, days + 1)]


def driver_employment_start(driver):
    """Повертає дату прийняття; порожня/стара некоректна дата не ламає історію."""
    if not driver:
        return None
    try:
        value=(driver["employment_date"] or "").strip()
    except (KeyError, TypeError, AttributeError):
        return None
    if not value:
        return None
    try:
        return datetime.strptime(value,"%Y-%m-%d").date()
    except ValueError:
        return None


def driver_employed_on(driver, work_day):
    """Чи вже був водій прийнятий на роботу у вказаний календарний день."""
    start=driver_employment_start(driver)
    return start is None or work_day>=start


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


def _driver_absence_for_day(con, driver_id, d):
    override_types=set(globals().get("TAXO_NONWORK_OVERRIDE_TYPES",set()) or ())
    if not driver_id or not override_types:
        return None
    rows=con.execute(
        """SELECT t.day_type
           FROM employee_time_entries t
           JOIN employees e ON e.id=t.employee_id
           WHERE e.driver_id=? AND t.work_date=?
           ORDER BY e.active DESC,e.id""",
        (driver_id,d.isoformat())
    ).fetchall()
    for row in rows:
        if str(row["day_type"] or "") in override_types:
            return row["day_type"]
    return None


def _export_row_values(con, d, r, driver_id=None):
    segs=_row_segments(con,r)
    effective_driver_id=driver_id or (_record_value(r,"driver_id",None) if r is not None else None)
    override=_driver_absence_for_day(con,effective_driver_id,d)
    state=driver_day_view(
        d,r,segs,
        day_type_override=override,
        suppress_plan=bool(override),
    )
    return {
        "date": d.strftime("%d.%m.%Y"),
        "weekday": ["Пн","Вт","Ср","Чт","Пт","Сб","Нд"][d.weekday()],
        "day_type": state["day_type"] if r is not None or override else _default_export_day_type(d),
        "schedule": state["schedule"],
        "breaks": state["breaks"],
        "work": minutes_to_db_hours(state["work_minutes"]),
        "drive": minutes_to_db_hours(state["driving_minutes"]),
        "over": minutes_to_db_hours(state["overtime_minutes"]),
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
        v = _export_row_values(con, d, r, driver["id"])
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

    candidates = report_font_candidates()
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

    headers = ["Дата","Вид","Графік","Перерви","Робота (план)","Керування (план)","Надуроч.","Маршрут","Авто","Примітка"]
    data = [[P(x, head_style) for x in headers]]

    con = db()
    total_work = total_drive = total_over = 0.0
    work_days = 0

    for d, r in _month_export_items(year, month, rows):
        v = _export_row_values(con, d, r, driver["id"])
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

    items.append(("heading","МОДЕЛЬ ДАНИХ v8.65 — ПЛАН / ФАКТ"))
    items.append((
        "note",
        "Поля «Керування» і «Робота» у цьому звіті зараз є ПЛАНОВИМИ. "
        "Після переходу на v8.65 старі маршрутні дані одноразово трактуються як план керування, "
        "а план робочого часу спочатку копіюється з них. Надалі робочий час редагується окремо. "
        "Майбутні дані тахокарт мають відображатися як ФАКТИЧНЕ керування окремим шаром і не перезаписувати план."
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

    candidates=report_font_candidates()
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
            f"Робота, план: {escape(minutes_dual(data['total_work_min']))} &nbsp;&nbsp; "
            f"Керування, план: {escape(minutes_dual(data['total_drive_min']))} &nbsp;&nbsp; "
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
    src=real_data_path(raw)
    if src is None:
        return raw
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
    return db_stored_path(target)


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
        src=real_data_path(raw)
        if src is None:
            result[field]=raw
            continue
        if not src.exists() or not src.is_file() or src.parent.resolve()==OUTPUT_DIR.resolve():
            result[field]=db_stored_path(src) if src.exists() else raw
            continue
        target=OUTPUT_DIR/src.name
        n=2
        while target.exists():
            target=OUTPUT_DIR/f"{src.stem}_restored_{n}{src.suffix}"
            n+=1
        shutil.move(str(src),str(target))
        result[field]=db_stored_path(target)
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



def _work_balance_cell(state, day):
    """Клітинка місячного робочого табеля: тільки години або код дня."""
    if state is None:
        return "В" if day.weekday() >= 5 else ""
    day_type=(state["day_type"] or "").strip()
    if day_type and day_type != "Робота":
        return SHIFT_DAY_CODES.get(day_type, day_type[:4])
    work_min=int(state["work_minutes"] or 0)
    return minutes_hhmm(work_min) if work_min>0 else ""


def collect_monthly_work_balance(year, month, active_only=True):
    """Місячний баланс на тому самому канонічному стані дня, що й графік."""
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
    drivers=[dr for dr in drivers if driver_employed_on(dr,days[-1])]

    rows=con.execute(
        """SELECT * FROM worklog
           WHERE work_date BETWEEN ? AND ?
           ORDER BY driver_id,work_date""",
        (days[0].isoformat(),days[-1].isoformat())
    ).fetchall()
    row_by={(r["driver_id"],r["work_date"]):r for r in rows}

    segment_by={}
    if rows:
        ids=[r["id"] for r in rows]
        q=",".join("?" for _ in ids)
        for seg in con.execute(
            f"SELECT * FROM work_segments WHERE worklog_id IN ({q}) ORDER BY worklog_id,segment_no",
            ids
        ).fetchall():
            segment_by.setdefault(seg["worklog_id"],[]).append(seg)

    override_types=set(globals().get("TAXO_NONWORK_OVERRIDE_TYPES",set()) or ())
    absence_by={}
    if override_types and drivers:
        driver_ids=[dr["id"] for dr in drivers]
        q=",".join("?" for _ in driver_ids)
        params=[days[0].isoformat(),days[-1].isoformat(),*driver_ids]
        for entry in con.execute(
            f"""SELECT e.driver_id,t.work_date,t.day_type
                FROM employee_time_entries t
                JOIN employees e ON e.id=t.employee_id
                WHERE t.work_date BETWEEN ? AND ?
                  AND e.driver_id IN ({q})
                ORDER BY e.active DESC,e.id""",
            params
        ).fetchall():
            if (entry["driver_id"] is not None
                    and str(entry["day_type"] or "") in override_types):
                absence_by.setdefault(
                    (int(entry["driver_id"]),entry["work_date"]),
                    entry["day_type"],
                )

    company=con.execute("SELECT * FROM company WHERE id=1").fetchone()
    con.close()

    out=[]
    for dr in drivers:
        cells=[]
        total_work_min=0
        total_over_min=0
        work_days=0
        overlap_min=0
        for d in days:
            if not driver_employed_on(dr,d):
                cells.append("")
                continue
            r=row_by.get((dr["id"],d.isoformat()))
            segs=segment_by.get(r["id"],[]) if r else []
            override=absence_by.get((int(dr["id"]),d.isoformat()))
            state=driver_day_view(
                d,r,segs,
                day_type_override=override,
                suppress_plan=bool(override),
            )
            cells.append(_work_balance_cell(state,d))
            total_work_min += state["work_minutes"]
            total_over_min += state["overtime_minutes"]
            overlap_min += state["work_overlap_minutes"]
            if state["work_minutes"]>0:
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
            "overlap_min":overlap_min,
        })

    return {
        "year":y,
        "month":m,
        "days":days,
        "drivers":out,
        "company":company,
        "absence_overlay_applied":bool(override_types),
        "canonical_driver_day_view":True,
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

    candidates=report_font_candidates()
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


def export_personnel_monthly_balance_xlsx(year, month, out_path, active_only=True):
    """Editable A4 monthly actual-hours grid for all personnel."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    data=collect_personnel_monthly_balance(year,month,active_only=active_only)
    wb=Workbook(); wb.remove(wb.active)
    thin=Side(style="thin",color="777777"); border=Border(left=thin,right=thin,top=thin,bottom=thin)
    header_fill=PatternFill("solid",fgColor="D9E6F2"); warning_fill=PatternFill("solid",fgColor="FFF2CC"); nonwork_fill=PatternFill("solid",fgColor="F2F2F2")
    company=(data["company"]["name"] if data["company"] else "") or ""
    for chunk in _split_month_days_a4(data["days"]):
        ws=wb.create_sheet(f"{chunk[0].day}-{chunk[-1].day}"); ncols=3+len(chunk)+5
        ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=ncols); ws.cell(1,1,company)
        ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=ncols); ws.cell(2,1,f"ТАБЕЛЬ УСЬОГО ПЕРСОНАЛУ — {month_name_ua(data['month']).upper()} {data['year']} — ДНІ {chunk[0].day}–{chunk[-1].day}")
        for cell in (ws.cell(1,1),ws.cell(2,1)):
            cell.font=Font(size=14,bold=True); cell.alignment=Alignment(horizontal="center")
        headers=["Таб. №","Працівник","Ролі"]+[f"{d.day}\n{['Пн','Вт','Ср','Чт','Пт','Сб','Нд'][d.weekday()]}" for d in chunk]+["Роб. днів","План","Факт","Відх.","Без факту"]
        for col,label in enumerate(headers,1):
            c=ws.cell(4,col,label); c.font=Font(size=9,bold=True); c.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True); c.fill=header_fill; c.border=border
        indexes=[d.day-1 for d in chunk]
        for row_no,employee in enumerate(data["employees"],5):
            values=[employee["personnel_no"],employee["name"],employee["roles"]]+[employee["cells"][i] for i in indexes]+[employee["work_days"],minutes_hhmm(employee["planned_min"]),minutes_hhmm(employee["actual_min"]),signed_hours_hhmm(employee["difference_min"]/60),employee["missing_days"]]
            for col,value in enumerate(values,1):
                c=ws.cell(row_no,col,value); c.border=border; c.alignment=Alignment(horizontal="center" if col!=2 else "left",vertical="center",wrap_text=True)
                if value=="—": c.fill=warning_fill
                elif value in ("В","Відп","Лік","Відпч","Гот","Інш"): c.fill=nonwork_fill
        ws.column_dimensions["A"].width=10; ws.column_dimensions["B"].width=24; ws.column_dimensions["C"].width=18
        for col in range(4,4+len(chunk)): ws.column_dimensions[get_column_letter(col)].width=8
        for col in range(4+len(chunk),ncols+1): ws.column_dimensions[get_column_letter(col)].width=11
        ws.freeze_panes="D5"; ws.sheet_view.showGridLines=False; ws.row_dimensions[4].height=30
        ws.page_setup.orientation="landscape"; ws.page_setup.paperSize=ws.PAPERSIZE_A4; ws.page_setup.fitToWidth=1; ws.page_setup.fitToHeight=0; ws.sheet_properties.pageSetUpPr.fitToPage=True
        ws.print_title_rows="1:4"; ws.print_area=f"A1:{get_column_letter(ncols)}{max(5,4+len(data['employees']))}"
    wb.save(str(out_path)); return data


def export_personnel_monthly_balance_pdf(year, month, out_path, active_only=True):
    """Printable A4 monthly actual-hours grid for all personnel."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from xml.sax.saxutils import escape
    data=collect_personnel_monthly_balance(year,month,active_only=active_only)
    font_name="Helvetica"; font_path=next((p for p in report_font_candidates() if os.path.exists(p)),None)
    if font_path:
        try:
            if "PersonnelBalanceFont" not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont("PersonnelBalanceFont",font_path))
            font_name="PersonnelBalanceFont"
        except Exception: pass
    doc=SimpleDocTemplate(str(out_path),pagesize=landscape(A4),leftMargin=10,rightMargin=10,topMargin=12,bottomMargin=12)
    styles=getSampleStyleSheet(); normal=ParagraphStyle("PersonnelBalanceNormal",parent=styles["Normal"],fontName=font_name,fontSize=6.8,leading=8)
    center=ParagraphStyle("PersonnelBalanceCenter",parent=normal,alignment=1); title=ParagraphStyle("PersonnelBalanceTitle",parent=center,fontSize=12.5,leading=14)
    story=[]; company=(data["company"]["name"] if data["company"] else "") or ""
    for page_no,chunk in enumerate(_split_month_days_a4(data["days"]),1):
        if page_no>1: story.append(PageBreak())
        if company: story.append(Paragraph(f"<b>{escape(company)}</b>",title))
        story.append(Paragraph(f"<b>ТАБЕЛЬ УСЬОГО ПЕРСОНАЛУ — {month_name_ua(data['month']).upper()} {data['year']} — ДНІ {chunk[0].day}–{chunk[-1].day}</b>",title)); story.append(Spacer(1,3))
        headers=["Таб. №","Працівник","Ролі"]+[f"{d.day}<br/>{['Пн','Вт','Ср','Чт','Пт','Сб','Нд'][d.weekday()]}" for d in chunk]+["Днів","План","Факт","Відх.","Без<br/>факту"]
        rows=[[Paragraph(f"<b>{h}</b>",center) for h in headers]]; indexes=[d.day-1 for d in chunk]
        for employee in data["employees"]:
            vals=[employee["personnel_no"],employee["name"],employee["roles"]]+[employee["cells"][i] for i in indexes]+[employee["work_days"],minutes_hhmm(employee["planned_min"]),minutes_hhmm(employee["actual_min"]),signed_hours_hhmm(employee["difference_min"]/60),employee["missing_days"]]
            rows.append([Paragraph(escape(str(v)),normal if i in (1,2) else center) for i,v in enumerate(vals)])
        day_width=min(39,410/max(1,len(chunk))); widths=[43,108,75]+[day_width]*len(chunk)+[34,42,42,43,37]
        table=Table(rows,colWidths=widths,repeatRows=1); style=[("FONTNAME",(0,0),(-1,-1),font_name),("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#777777")),("BACKGROUND",(0,0),(-1,0),colors.HexColor("#D9E6F2")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),1.5),("RIGHTPADDING",(0,0),(-1,-1),1.5),("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2)]
        for rr,employee in enumerate(data["employees"],1):
            for cc,idx in enumerate(indexes,3):
                value=employee["cells"][idx]
                if value=="—": style.append(("BACKGROUND",(cc,rr),(cc,rr),colors.HexColor("#FFF2CC")))
                elif value in ("В","Відп","Лік","Відпч","Гот","Інш"): style.append(("BACKGROUND",(cc,rr),(cc,rr),colors.HexColor("#F2F2F2")))
        table.setStyle(TableStyle(style)); story.append(table); story.append(Spacer(1,4)); story.append(Paragraph("— = є план, але факт ще не внесено. В — вихідний; Відп — відпустка; Лік — лікарняний; Відпч — відпочинок; Гот — готовність; Інш — інша робота.",normal))
    doc.build(story); return data


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
    drivers=[dr for dr in drivers if driver_employed_on(dr,days[-1])]

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

    override_types=set(globals().get("TAXO_NONWORK_OVERRIDE_TYPES",set()) or ())
    absence_by={}
    if override_types and drivers:
        driver_ids=[dr["id"] for dr in drivers]
        q=",".join("?" for _ in driver_ids)
        params=[days[0].isoformat(),days[-1].isoformat(),*driver_ids]
        for entry in con.execute(
            f"""SELECT e.driver_id,t.work_date,t.day_type
                FROM employee_time_entries t
                JOIN employees e ON e.id=t.employee_id
                WHERE t.work_date BETWEEN ? AND ?
                  AND e.driver_id IN ({q})
                ORDER BY e.active DESC,e.id""",
            params
        ).fetchall():
            if (entry["driver_id"] is not None
                    and str(entry["day_type"] or "") in override_types):
                absence_by.setdefault(
                    (int(entry["driver_id"]),entry["work_date"]),
                    entry["day_type"],
                )

    company=con.execute("SELECT * FROM company WHERE id=1").fetchone()
    con.close()

    driver_rows=[]
    details=[]
    for dr in drivers:
        cells=[]
        work_days=0
        work_min=0
        drive_min=0
        overlap_min=0
        for d in days:
            if not driver_employed_on(dr,d):
                cells.append("")
                continue
            r=row_by.get((dr["id"],d.isoformat()))
            segs=seg_by.get(r["id"],[]) if r else []
            override=absence_by.get((int(dr["id"]),d.isoformat()))
            state=driver_day_view(
                d,r,segs,
                day_type_override=override,
                suppress_plan=bool(override),
            )
            if override:
                cell=SHIFT_DAY_CODES.get(str(override),str(override)[:4])
            else:
                cell=_monthly_shift_cell(r,segs)
            cells.append(cell)

            if r or override:
                if state["day_type"]=="Робота" and state["work_minutes"]>0:
                    work_days+=1
                work_min+=state["work_minutes"]
                drive_min+=state["driving_minutes"]
                overlap_min+=state["work_overlap_minutes"]

                if state["day_type"]=="Робота" and state["work_minutes"]>0:
                    details.append({
                        "driver": f"{dr['last_name']} {dr['first_name']} {dr['middle_name']}".strip(),
                        "date": d,
                        "day_type": state["day_type"],
                        "schedule": state["schedule"],
                        "breaks": state["breaks"],
                        "work_min": state["work_minutes"],
                        "drive_min": state["driving_minutes"],
                        "route": (r["route_name"] if r is not None and "route_name" in r.keys() else "") or "",
                        "vehicle": (r["vehicle"] if r is not None and "vehicle" in r.keys() else "") or "",
                        "notes": (r["notes"] if r is not None and "notes" in r.keys() else "") or "",
                    })

        driver_rows.append({
            "id":dr["id"],
            "name":f"{dr['last_name']} {dr['first_name']} {dr['middle_name']}".strip(),
            "cells":cells,
            "work_days":work_days,
            "work_min":work_min,
            "drive_min":drive_min,
            "overlap_min":overlap_min,
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

    candidates=report_font_candidates()
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

    candidates=report_font_candidates()
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
        headers += ["Роб. днів","Робота, план","Керування, план"]

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
    headers=["Водій","Дата","Графік / частини","Перерви","Робота, план","Керування, план","Маршрут","Авто","Примітка"]
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
    # r9: width=6 keeps the button inside 900 px layouts without changing its label.
    return ttk.Button(parent, text="Дата…", width=6,
                      command=lambda: show_calendar_picker(parent, variable))


def fit_window_to_screen(win, width, height, min_width=420, min_height=260):
    """Не дозволяє діалогам виходити за межі робочого екрана.

    На невеликих ноутбуках старі фіксовані розміри 1450x760 або 980x760
    ховали нижні кнопки за панеллю Windows. Вікно лишається змінюваним.
    """
    win.update_idletasks()
    screen_w=max(640, int(win.winfo_screenwidth()))
    screen_h=max(480, int(win.winfo_screenheight()))
    max_w=max(520, screen_w-80)
    max_h=max(360, screen_h-120)
    final_w=max(420, min(int(width), max_w))
    final_h=max(260, min(int(height), max_h))
    win.geometry(f"{final_w}x{final_h}")
    win.minsize(min(int(min_width), final_w), min(int(min_height), final_h))
    win.resizable(True, True)


def ctrl_shortcut_action(keysym, keycode=None):
    """Розпізнає Ctrl-команди також при українській розкладці клавіатури."""
    key=(keysym or "").lower()
    aliases={
        "c":"copy", "с":"copy", "cyrillic_es":"copy",
        "v":"paste", "м":"paste", "cyrillic_em":"paste",
        "x":"cut", "ч":"cut", "cyrillic_che":"cut",
        "a":"select_all", "ф":"select_all", "cyrillic_ef":"select_all",
        "z":"undo", "я":"undo", "cyrillic_ya":"undo",
        "y":"redo", "н":"redo", "cyrillic_en":"redo",
    }
    action=aliases.get(key)
    if action:
        return action
    # На Windows keycode є кодом фізичної клавіші й не залежить від розкладки.
    if sys.platform.startswith("win"):
        return {65:"select_all",67:"copy",86:"paste",88:"cut",89:"redo",90:"undo"}.get(keycode)
    return None

def _select_workspace_folder(parent,title="Виберіть робочу папку Taxo"):
    selected=filedialog.askdirectory(parent=parent,title=title,mustexist=True)
    return normalize_root(selected) if selected else None


def prepare_workspace_interactively():
    """Перевірити сховище до відкриття БД та отримати єдиний активний lock."""
    global ACTIVE_WORKSPACE_LOCK
    root=DATA_ROOT
    chooser=tk.Tk(); chooser.withdraw()
    try:
        while True:
            configure_runtime_workspace(root)
            try:
                probe_workspace(root)
                ensure_workspace(root)
                lock=WorkspaceLock(root,"v8.70-r9")
                lock.acquire()
                try:
                    save_workspace_root(root)
                except Exception:
                    lock.release()
                    raise
                ACTIVE_WORKSPACE_LOCK=lock
                return lock
            except WorkspaceBusyError as exc:
                info=exc.info
                if info.get("stale"):
                    recover=messagebox.askyesno(
                        "Залишкове блокування Taxo",
                        "Сховище має старий файл блокування:\n\n"
                        f"{root}\n\n{describe_lock(info)}\n\n"
                        "Інша копія, ймовірно, завершилася аварійно. Зняти старе блокування?\n\n"
                        "Робіть це лише якщо Taxo точно не працює на іншому комп’ютері.",
                        icon="warning",parent=chooser
                    )
                    if recover:
                        try:
                            lock=WorkspaceLock(root,"v8.70-r9"); lock.acquire(force=True)
                            try:
                                save_workspace_root(root)
                            except Exception:
                                lock.release()
                                raise
                            ACTIVE_WORKSPACE_LOCK=lock
                            return lock
                        except Exception as recovery_error:
                            messagebox.showerror("Робоче сховище",str(recovery_error),parent=chooser)
                            continue
                action=messagebox.askyesnocancel(
                    "Сховище зараз використовується",
                    "Інша копія Taxo вже працює з цими даними:\n\n"
                    f"{root}\n\n{describe_lock(info)}\n\n"
                    "Так — перевірити ще раз\nНі — вибрати інше сховище\nСкасувати — закрити програму",
                    icon="warning",parent=chooser
                )
                if action is True:
                    continue
                if action is None:
                    return None
                selected=_select_workspace_folder(chooser)
                if selected is None:
                    return None
                root=selected
            except Exception as exc:
                choose=messagebox.askyesno(
                    "Робоче сховище недоступне",
                    f"Taxo не може прочитати або записати робочу папку:\n\n{root}\n\n{exc}\n\n"
                    "Вибрати іншу папку?",
                    icon="error",parent=chooser
                )
                if not choose:
                    return None
                selected=_select_workspace_folder(chooser)
                if selected is None:
                    return None
                root=selected
    finally:
        chooser.destroy()


class App(tk.Tk):
    def report_callback_exception(self, exc_type, exc_value, exc_tb):
        """Остання лінія захисту для неперехоплених помилок Tkinter callback-ів."""
        log_path=_append_error_log("Неперехоплена помилка інтерфейсу",exc_value,exc_tb)
        if _is_file_access_error(exc_value):
            filename=getattr(exc_value,"filename",None)
            if filename:
                msg=(
                    f"Не вдалося отримати доступ до файла:\n{filename}\n\n"
                    "Ймовірно, файл відкритий в іншій програмі або папка недоступна для запису."
                )
            else:
                msg=(
                    "Не вдалося отримати доступ до файла або папки. "
                    "Перевірте, чи файл не відкритий в іншій програмі, та права доступу."
                )
        else:
            text=str(exc_value).strip()
            msg="Сталася неочікувана помилка у вікні програми."
            if text:
                msg += f"\n\n{text}"
        if log_path is not None:
            msg += f"\n\nТехнічні подробиці збережено у:\n{log_path}"
        try:
            messagebox.showerror("Помилка Taxo",msg,parent=self)
        except Exception:
            pass

    @staticmethod
    def _is_text_input(widget):
        return widget is not None and widget.winfo_class() in {
            "Entry", "TEntry", "Text", "Spinbox", "TSpinbox", "TCombobox"
        }

    @staticmethod
    def _widget_is_readonly(widget):
        try:
            return str(widget.cget("state")) in {"disabled", "readonly"}
        except (tk.TclError, AttributeError):
            return False

    def _select_all_widget(self, widget):
        try:
            if widget.winfo_class()=="Text":
                widget.tag_add("sel", "1.0", "end-1c")
                widget.mark_set("insert", "end-1c")
                widget.see("insert")
            else:
                widget.selection_range(0, "end")
                widget.icursor("end")
            return True
        except (tk.TclError, AttributeError):
            return False

    def _copy_tree_rows(self, tree):
        selected=list(tree.selection())
        if not selected and tree.focus():
            selected=[tree.focus()]
        if not selected:
            return False
        lines=[]
        for item in selected:
            values=tree.item(item, "values")
            lines.append("\t".join(str(value) for value in values))
        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))
        self.update_idletasks()
        if hasattr(self, "ui_status_var"):
            self.ui_status_var.set(f"Скопійовано рядків: {len(lines)}")
        return True

    def _text_selection(self, widget):
        """Повертає виділений текст без залежності від стандартних Tk virtual events."""
        try:
            if widget.winfo_class()=="Text":
                if not widget.tag_ranges("sel"):
                    return ""
                return widget.get("sel.first", "sel.last")
            if hasattr(widget, "selection_present") and widget.selection_present():
                return widget.get()[widget.index("sel.first"):widget.index("sel.last")]
        except (tk.TclError, AttributeError):
            pass
        return ""

    def _copy_text_widget(self, widget):
        try:
            text=self._text_selection(widget)
            # Для readonly Combobox корисніше скопіювати поточне значення,
            # навіть якщо користувач не зміг явно виділити його мишею.
            if not text and widget.winfo_class()=="TCombobox":
                text=widget.get()
            if not text:
                return False
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update_idletasks()
            if hasattr(self, "ui_status_var"):
                self.ui_status_var.set("Скопійовано в буфер обміну")
            return True
        except tk.TclError:
            return False

    def _delete_text_selection(self, widget):
        try:
            if widget.winfo_class()=="Text":
                if widget.tag_ranges("sel"):
                    widget.delete("sel.first", "sel.last")
                    return True
                return False
            if hasattr(widget, "selection_present") and widget.selection_present():
                widget.delete("sel.first", "sel.last")
                return True
        except (tk.TclError, AttributeError):
            return False
        return False

    def _paste_text_widget(self, widget):
        try:
            text=self.clipboard_get()
        except tk.TclError:
            return False
        try:
            self._delete_text_selection(widget)
            if widget.winfo_class()=="Text":
                widget.insert("insert", text)
                widget.see("insert")
            else:
                widget.insert("insert", text)
            if hasattr(self, "ui_status_var"):
                self.ui_status_var.set("Вставлено з буфера обміну")
            return True
        except (tk.TclError, AttributeError):
            return False

    def _run_edit_action(self, widget, action):
        if widget is None:
            return False
        if isinstance(widget, ttk.Treeview):
            if widget is getattr(self, "work_tree", None):
                if action=="copy":
                    self.copy_work_day()
                    return True
                if action=="paste":
                    self.paste_work_day()
                    return True
            if action=="copy":
                return self._copy_tree_rows(widget)
            if action=="select_all":
                widget.selection_set(widget.get_children())
                return True
            return False
        if not self._is_text_input(widget):
            return False
        if action=="select_all":
            return self._select_all_widget(widget)
        if action=="copy":
            return self._copy_text_widget(widget)
        if action in {"cut", "paste", "undo", "redo"} and self._widget_is_readonly(widget):
            return False
        if action=="cut":
            if not self._copy_text_widget(widget):
                return False
            return self._delete_text_selection(widget)
        if action=="paste":
            return self._paste_text_widget(widget)
        virtual={"undo":"<<Undo>>", "redo":"<<Redo>>"}.get(action)
        if not virtual:
            return False
        try:
            widget.event_generate(virtual)
            return True
        except tk.TclError:
            return False

    def _edit_focused(self, action):
        self._run_edit_action(self.focus_get(), action)

    def _global_ctrl_shortcut(self, event):
        action=ctrl_shortcut_action(getattr(event, "keysym", ""), getattr(event, "keycode", None))
        if not action:
            return None
        widget=getattr(event, "widget", None)
        key=(getattr(event, "keysym", "") or "").lower()
        # r7: і латинські, і українські Ctrl/Cmd-команди йдуть через один
        # прямий обробник. Це прибирає залежність від нестабільних <<Paste>>/<<Copy>>
        # у ttk.Entry/Spinbox/Combobox на Windows.
        if self._run_edit_action(widget, action):
            return "break"
        return None

    def _show_context_menu(self, event):
        widget=getattr(event, "widget", None)
        if not (self._is_text_input(widget) or isinstance(widget, ttk.Treeview)):
            return None
        if isinstance(widget, ttk.Treeview):
            row=widget.identify_row(event.y)
            if row and row not in widget.selection():
                widget.selection_set(row)
                widget.focus(row)
        menu=tk.Menu(self, tearoff=0)
        if isinstance(widget, ttk.Treeview):
            copy_label="Копіювати день" if widget is getattr(self, "work_tree", None) else "Копіювати рядок(и)"
            menu.add_command(label=copy_label, command=lambda:self._run_edit_action(widget,"copy"))
            if widget is getattr(self, "work_tree", None):
                menu.add_command(label="Вставити день", command=lambda:self._run_edit_action(widget,"paste"))
            menu.add_separator()
            menu.add_command(label="Виділити все", command=lambda:self._run_edit_action(widget,"select_all"))
        else:
            readonly=self._widget_is_readonly(widget)
            menu.add_command(label="Вирізати", state="disabled" if readonly else "normal", command=lambda:self._run_edit_action(widget,"cut"))
            menu.add_command(label="Копіювати", command=lambda:self._run_edit_action(widget,"copy"))
            menu.add_command(label="Вставити", state="disabled" if readonly else "normal", command=lambda:self._run_edit_action(widget,"paste"))
            menu.add_separator()
            menu.add_command(label="Виділити все", command=lambda:self._run_edit_action(widget,"select_all"))
        try:
            x_root=getattr(event,"x_root",0) or widget.winfo_rootx()+12
            y_root=getattr(event,"y_root",0) or widget.winfo_rooty()+widget.winfo_height()
            menu.tk_popup(x_root, y_root)
        finally:
            menu.grab_release()
        return "break"

    def _install_ui_accessibility(self):
        # bind_all поширює меню та українські Ctrl/Cmd-команди на поля у всіх Toplevel.
        self.bind_all("<Control-KeyPress>", self._global_ctrl_shortcut, add="+")
        if sys.platform == "darwin":
            self.bind_all("<Command-KeyPress>", self._global_ctrl_shortcut, add="+")
            # На Mac контекстне меню відкривається також Control-click.
            self.bind_all("<Control-Button-1>", self._show_context_menu, add="+")
        self.bind_all("<Button-3>", self._show_context_menu, add="+")
        self.bind_all("<Shift-F10>", self._show_context_menu, add="+")

    def _restore_main_window(self):
        saved=get_setting("main_window_geometry", "")
        match=re.fullmatch(r"(\d+)x(\d+)([+-]\d+)([+-]\d+)", saved or "")
        if match:
            try:
                screen_w=max(640,self.winfo_screenwidth())
                screen_h=max(480,self.winfo_screenheight())
                width=min(int(match.group(1)),max(520,screen_w-80))
                height=min(int(match.group(2)),max(360,screen_h-120))
                x=max(0,min(int(match.group(3)),screen_w-width))
                y=max(0,min(int(match.group(4)),screen_h-height))
                self.geometry(f"{width}x{height}+{x}+{y}")
            except tk.TclError:
                pass
        if get_setting("main_window_state", "normal")=="zoomed":
            def apply_zoomed():
                try:
                    self.state("zoomed")
                except tk.TclError:
                    pass
            self.after_idle(apply_zoomed)

    def __init__(self):
        super().__init__()
        self.title("Taxo 10.1-r2 — Працівники, графіки та шляхівки")
        fit_window_to_screen(self,1200,760,900,600)
        self.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.bind("<Control-q>", lambda e: self.exit_app())
        if sys.platform == "darwin":
            self.bind("<Command-q>", lambda e: self.exit_app())
        self.driver_id = None
        self.att_driver_id = None
        self.att_driver_map = {}
        self._workspace_lock=ACTIVE_WORKSPACE_LOCK
        self._workspace_lock_failures=0
        self._install_ui_accessibility()
        self.build_ui()
        self.build_menu()
        self._restore_main_window()
        self.load_company()
        self.load_drivers()
        self.refresh_month()
        self.after(30000,self._refresh_workspace_lock)

    def _refresh_workspace_lock(self):
        lock=getattr(self,"_workspace_lock",None)
        if lock is None:
            return
        if lock.refresh():
            self._workspace_lock_failures=0
            self.after(30000,self._refresh_workspace_lock)
            return
        self._workspace_lock_failures+=1
        if self._workspace_lock_failures<3:
            self.after(5000,self._refresh_workspace_lock)
            return
        messagebox.showerror(
            "Втрачено блокування сховища",
            "Taxo більше не може підтвердити виключний доступ до робочих даних. "
            "Щоб не пошкодити спільну базу, програма буде закрита.\n\n"
            f"Сховище: {DATA_ROOT}",parent=self
        )
        self.destroy()

    def build_menu(self):
        shortcut = "Command+" if sys.platform == "darwin" else "Ctrl+"
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Зберегти реквізити підприємства", command=self.save_company)
        file_menu.add_separator()
        file_menu.add_command(label="Резервна копія", command=self.manual_backup)
        file_menu.add_command(label="Відновити з резервної копії…", command=self.restore_backup)
        file_menu.add_command(label="Робоче сховище…", command=self.show_workspace_manager)
        file_menu.add_command(label="Відкрити папку даних", command=self.open_data_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Вийти", command=self.exit_app)
        menubar.add_cascade(label="Файл", menu=file_menu)
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Вирізати", accelerator=f"{shortcut}X", command=lambda:self._edit_focused("cut"))
        edit_menu.add_command(label="Копіювати", accelerator=f"{shortcut}C", command=lambda:self._edit_focused("copy"))
        edit_menu.add_command(label="Вставити", accelerator=f"{shortcut}V", command=lambda:self._edit_focused("paste"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Виділити все", accelerator=f"{shortcut}A", command=lambda:self._edit_focused("select_all"))
        menubar.add_cascade(label="Правка", menu=edit_menu)
        # Notebook не має штатної прокрутки заголовків вкладок у Tk. На вузьких
        # екранах крайні вкладки можуть фізично не вміститись, тому всі розділи
        # дублюємо у меню й робимо їх доступними незалежно від ширини вікна.
        sections_menu = tk.Menu(menubar, tearoff=0)
        for section_index, (label, tab) in enumerate((
            ("Підприємство", self.tab_company),
            ("Водії", self.tab_drivers),
            ("Автомобілі", self.tab_vehicles),
            ("Табель", self.tab_work),
            ("Графік водіїв", self.tab_schedule),
            ("Маршрути", self.tab_route_catalog),
            ("Підтвердження діяльності", self.tab_att),
            ("Тахограф — шайби", self.tab_tacho),
        ), start=1):
            sections_menu.add_command(
                label=label, accelerator=f"Alt+{section_index}",
                command=lambda t=tab:self.show_tab(t)
            )
        menubar.add_cascade(label="Розділи", menu=sections_menu)
        service_menu = tk.Menu(menubar, tearoff=0)
        service_menu.add_command(label="Оновити табель", command=self.refresh_month)
        service_menu.add_command(label="Графік водіїв", command=lambda: self.show_tab(self.tab_schedule))
        service_menu.add_command(label="Місячний графік змінності", command=self.show_monthly_shift_schedule)
        service_menu.add_command(label="Шляхівки на день", command=self.show_waybills_for_schedule)
        service_menu.add_command(label="Реєстр усіх працівників", command=self.show_employee_registry)
        service_menu.add_command(label="Випуск на лінію — зміни персоналу", command=self.show_dispatch_staff_schedule)
        service_menu.add_command(label="Табель персоналу", command=self.show_employee_timesheet)
        service_menu.add_command(label="Місячний табель / баланс часу", command=self.show_monthly_work_balance)
        service_menu.add_command(label="Контроль бланків — 56 днів + поточний", command=self.show_attestation_gap_control)
        service_menu.add_command(label="Маршрути", command=lambda: self.show_tab(self.tab_route_catalog))
        service_menu.add_command(label="Автомобілі", command=lambda: self.show_tab(self.tab_vehicles))
        if TachographModule:
            service_menu.add_command(label="Тахограф — шайби", command=lambda: self.show_tab(self.tab_tacho))
        menubar.add_cascade(label="Сервіс", menu=service_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="Про програму",
            command=lambda: messagebox.showinfo(
                "Taxo 10.1-r2",
                "Облік водіїв та робочого часу — 48 місяців.\n\n"
                "10.1-r2: UI refresh, новий табель, «Про програму» та вбудована довідка; "
                "почергова робота кількох копій Taxo.\n"
                "База, резервні копії, документи, журнали та скани зберігаються разом.",
                parent=self
            )
        )
        menubar.add_cascade(label="Довідка", menu=help_menu)
        self.config(menu=menubar)

    def show_tab(self, tab):
        for child in self.winfo_children():
            if isinstance(child, ttk.Notebook):
                child.select(tab)
                return

    def exit_app(self):
        if messagebox.askyesno("Вихід", "Вийти з програми?", parent=self):
            try:
                state=self.state()
                if state in {"normal", "zoomed"}:
                    set_setting("main_window_state", state)
                if state=="normal":
                    set_setting("main_window_geometry", self.geometry())
            except Exception:
                pass
            lock=getattr(self,"_workspace_lock",None)
            if lock is not None:
                lock.release()
            self.destroy()

    def _refresh_brand_header(self):
        canvas=getattr(self,"brand_canvas",None)
        if canvas is None:
            return
        company_name=""
        vars_=getattr(self,"company_vars",{})
        if "name" in vars_:
            try:
                company_name=vars_["name"].get().strip()
            except tk.TclError:
                company_name=""
        draw_brand_header(canvas, company_name, "Taxo 10.1-r2 / Driver Worktime")

    def build_ui(self):
        apply_theme(self, ttk)
        try:
            install_runtime_icon(self)
        except Exception:
            # Branding must never prevent access to operational data.
            pass

        self.brand_canvas=tk.Canvas(
            self,height=92,bg=PALETTE["navy"],highlightthickness=0,borderwidth=0
        )
        self.brand_canvas.pack(fill="x",padx=8,pady=(8,0))
        self.brand_canvas.bind(
            "<Configure>",lambda _event:self._refresh_brand_header(),add="+"
        )
        self.after_idle(self._refresh_brand_header)

        modifier="Command" if sys.platform=="darwin" else "Ctrl"
        self.ui_status_var=tk.StringVar(
            value=f"Підказка: контекстне меню у полі — Вирізати / Копіювати / Вставити; {modifier}-команди працюють і в українській розкладці."
        )
        ttk.Label(
            self,
            textvariable=self.ui_status_var,
            anchor="w",
            relief="sunken",
            padding=(8, 3)
        ).pack(side="bottom", fill="x")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)
        self.notebook=nb

        self.tab_company = ttk.Frame(nb)
        self.tab_drivers = ttk.Frame(nb)
        self.tab_vehicles = ttk.Frame(nb)
        self.tab_work = ttk.Frame(nb)
        self.tab_schedule = ttk.Frame(nb)
        self.tab_route_catalog = ttk.Frame(nb)
        self.tab_att = ttk.Frame(nb)
        self.tab_tacho = ttk.Frame(nb)
        nb.add(self.tab_company, text="Підприємство")
        nb.add(self.tab_drivers, text="Працівники")
        nb.add(self.tab_vehicles, text="Автомобілі")
        nb.add(self.tab_work, text="Табель")
        nb.add(self.tab_schedule, text="Графік водіїв")
        nb.add(self.tab_route_catalog, text="Маршрути")
        nb.add(self.tab_att, text="Підтвердження діяльності")
        nb.add(self.tab_tacho, text="Тахограф — шайби")

        def remember_tab(_event=None):
            try:
                set_setting("main_last_tab", str(nb.index(nb.select())))
            except (tk.TclError, ValueError):
                pass
        nb.bind("<<NotebookTabChanged>>", remember_tab, add="+")
        self.main_notebook=nb
        # Alt+1…Alt+8 — швидкий перехід між розділами, навіть якщо вкладка
        # фізично не помістилась у рядку Notebook.
        for tab_index in range(8):
            self.bind_all(
                f"<Alt-Key-{tab_index+1}>",
                lambda _event, idx=tab_index: (nb.select(idx), "break")[1],
                add="+"
            )
        try:
            saved_tab=int(get_setting("main_last_tab", "0") or 0)
            # r9 прибрав окрему вкладку «Шаблони маршрутів». Переносимо
            # індекс останньої вкладки зі старої 9-вкладкової схеми.
            if not get_setting("main_tabs_r9_migrated", ""):
                saved_tab={5:5, 6:5, 7:6, 8:7}.get(saved_tab, saved_tab)
                set_setting("main_last_tab", saved_tab)
                set_setting("main_tabs_r9_migrated", "1")
            if 0 <= saved_tab < nb.index("end"):
                nb.select(saved_tab)
        except (ValueError, tk.TclError):
            pass

        self.build_company()
        self.build_drivers()
        self.build_vehicles()
        self.build_work()
        self.build_schedule()
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

        def owns_event(event):
            widget=getattr(event, "widget", None)
            while widget is not None:
                if widget in (body, canvas):
                    return True
                widget=getattr(widget, "master", None)
            return False

        def wheel(event):
            if not owns_event(event):
                return None
            if event.widget.winfo_class() in {"Treeview", "Text", "Canvas"} and event.widget is not canvas:
                return None
            delta=getattr(event, "delta", 0)
            if delta:
                canvas.yview_scroll(int(-delta/120) or (-1 if delta>0 else 1), "units")
            return "break"

        def shift_wheel(event):
            if not owns_event(event):
                return None
            if event.widget.winfo_class() in {"Treeview", "Text", "Canvas"} and event.widget is not canvas:
                return None
            delta=getattr(event, "delta", 0)
            if delta:
                canvas.xview_scroll(int(-delta/120) or (-1 if delta>0 else 1), "units")
            return "break"

        # Не використовуємо небезпечне глобальне зняття: старий варіант міг зняти
        # прив'язки інших вкладок. Безпечний глобальний обробник перевіряє,
        # чи подія справді належить цій вкладці, і не забирає колесо у таблиць.
        canvas.bind_all("<MouseWheel>", wheel, add="+")
        canvas.bind_all("<Shift-MouseWheel>", shift_wheel, add="+")

        setattr(self, f"_{key}_scroll_canvas", canvas)
        return body

    def build_company(self):
        host = self._make_scrollable_tab_body(self.tab_company, "company")
        f = ttk.LabelFrame(host, text="Реквізити підприємства — українською")
        f.pack(fill="x", padx=12, pady=(12,6))
        self.company_vars = {}
        labels = [
            ("name", "Назва підприємства"),
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
            if key=="name":
                v.trace_add("write",lambda *_args:self._refresh_brand_header())
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

        waybill_box = ttk.LabelFrame(host, text="Постійні реквізити автобусної шляхівки")
        waybill_box.pack(fill="x", padx=12, pady=(0,10))
        self.company_waybill_vars = {}
        for i, (key, label, default) in enumerate([
            ("waybill_series", "Серія за замовчуванням", "АААТ"),
            ("transport_column", "Колона", ""),
            ("brigade", "Бригада", ""),
        ]):
            ttk.Label(waybill_box, text=label).grid(row=i, column=0, sticky="w", padx=8, pady=5)
            value=tk.StringVar(value=default); self.company_waybill_vars[key]=value
            ttk.Entry(waybill_box, textvariable=value, width=45).grid(row=i, column=1, sticky="ew", padx=8, pady=5)
        ttk.Button(waybill_box,text="Пули серій і номерів…",command=self.show_waybill_number_pools).grid(row=3,column=1,sticky="w",padx=8,pady=5)
        ttk.Label(
            waybill_box,
            text="Офіційний номер береться з активного пулу за датою роботи. Перегляд не витрачає номер; повторний друк зберігає номер і збільшує ревізію.",
            foreground="gray",wraplength=850,justify="left"
        ).grid(row=4,column=0,columnspan=2,sticky="w",padx=8,pady=(2,7))
        waybill_box.columnconfigure(1,weight=1)

        company_save_bar = ttk.Frame(host)
        company_save_bar.pack(fill="x", padx=12, pady=(0,10))
        ttk.Button(
            company_save_bar,
            text="Зберегти реквізити підприємства",
            command=self.save_company,
            style="Accent.TButton"
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
        ttk.Button(btns, text="Робоче сховище…", command=self.show_workspace_manager).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="Відкрити папку даних", command=self.open_data_folder).pack(side="left")
        ttk.Button(btns, text="Вийти", command=self.exit_app).pack(side="right")
        kind_label={"local":"локальне","network":"мережеве","cloud":"синхронізована хмара"}.get(storage_kind(DATA_ROOT),"інше")
        ttk.Label(host, text=f"Робоче сховище ({kind_label}): {DATA_ROOT}", foreground="gray").pack(anchor="w", padx=12)
        ttk.Label(host, text=f"База: {DB_PATH}", foreground="gray").pack(anchor="w", padx=12)
        ttk.Label(host, text=f"Резервні копії: {BACKUP_DIR}", foreground="gray").pack(anchor="w", padx=12)
        ttk.Label(host, text="Усі змінні дані зберігаються тут окремо від програми. Одночасно сховище відкриває лише одна копія Taxo.", foreground="gray").pack(anchor="w", padx=12)

    def manual_backup(self):
        try:
            path = backup_database("manual")
            if path:
                messagebox.showinfo("Резервна копія", f"Резервну копію створено:\n{path}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося створити резервну копію:\n{e}")

    def open_data_folder(self):
        try:
            open_external(DATA_ROOT)
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def _close_after_workspace_switch(self,target,operation):
        save_workspace_root(target)
        messagebox.showinfo(
            "Робоче сховище змінено",
            f"{operation}\n\nНове сховище:\n{target}\n\n"
            "Taxo зараз закриється. Запустіть програму знову — вона відкриє нове сховище. "
            "Попередня папка залишається без змін як страхова копія.",parent=self
        )
        lock=getattr(self,"_workspace_lock",None)
        if lock is not None:
            lock.release()
        self._workspace_lock=None
        self.destroy()

    def show_workspace_manager(self):
        win=tk.Toplevel(self)
        win.title("Робоче сховище Taxo")
        fit_window_to_screen(win,820,540,680,480)
        win.transient(self); win.grab_set()
        body=ttk.Frame(win,padding=14); body.pack(fill="both",expand=True)
        kind=storage_kind(DATA_ROOT)
        kind_label={"local":"Локальна папка","network":"Мережева папка / NAS","cloud":"Синхронізована хмарна папка"}.get(kind,"Папка")
        ttk.Label(body,text="Поточне робоче сховище",font=("TkDefaultFont",11,"bold")).pack(anchor="w")
        ttk.Label(body,text=str(DATA_ROOT),wraplength=760,justify="left").pack(anchor="w",pady=(5,2))
        ttk.Label(body,text=kind_label,foreground="gray").pack(anchor="w")

        ttk.Separator(body).pack(fill="x",pady=12)
        ttk.Label(
            body,
            text=(
                "У цій папці разом зберігаються основна БД, тахографічна БД і скани, "
                "резервні копії, шляхівки, бланки, звіти та журнали помилок. "
                "Після зміни папки програма закриється; новий шлях застосовується при наступному запуску."
            ),wraplength=760,justify="left"
        ).pack(anchor="w")

        warning=ttk.LabelFrame(body,text="Почергова робота кількох копій")
        warning.pack(fill="x",pady=12)
        ttk.Label(
            warning,
            text=(
                "Мережева папка (SMB/NAS) дає безпосереднє блокування. У OneDrive, Dropbox, "
                "Google Drive чи іншій синхронізованій хмарі запускайте Taxo лише почергово: "
                "після закриття на першому комп’ютері дочекайтеся завершення синхронізації, "
                "і тільки тоді відкривайте на другому. Taxo створює файл блокування та не дозволяє "
                "штатно відкрити одне сховище двом копіям r9 або новішим одночасно. Старі версії "
                "до r9 не знають про це блокування — не підключайте їх до спільної робочої папки."
            ),wraplength=730,justify="left",foreground="#7A4E00"
        ).pack(anchor="w",padx=10,pady=8)

        def check_target(target,require_existing=False):
            if target is None:
                return False
            if normalize_root(target)==normalize_root(DATA_ROOT):
                messagebox.showinfo("Робоче сховище","Це вже поточне сховище.",parent=win)
                return False
            try:
                info=probe_workspace(target)
                lock_info=read_lock_info(target)
                if lock_info and not lock_info.get("stale"):
                    raise RuntimeError("Це сховище вже відкрите іншою копією Taxo:\n\n"+describe_lock(lock_info))
                if require_existing and not workspace_has_data(target):
                    if not messagebox.askyesno(
                        "Порожнє сховище",
                        "У вибраній папці не знайдено даних Taxo. Підключити її як нове порожнє сховище?",
                        parent=win
                    ):
                        return False
                return info
            except Exception as exc:
                messagebox.showerror("Робоче сховище",f"Не вдалося використати папку:\n\n{target}\n\n{exc}",parent=win)
                return False

        def attach_existing():
            target=_select_workspace_folder(win,"Підключити існуюче сховище Taxo")
            info=check_target(target,require_existing=True)
            if not info:
                return
            main_db=paths_for(target)["main_db"]
            if main_db.exists():
                ok,details=validate_database_file(main_db)
                if not ok:
                    messagebox.showerror("Робоче сховище",f"Основна база не пройшла перевірку:\n\n{details}",parent=win)
                    return
            ensure_workspace(target)
            self._close_after_workspace_switch(target,"Існуюче сховище підключено.")

        def copy_current():
            target=_select_workspace_folder(win,"Куди перенести всі робочі дані Taxo")
            info=check_target(target)
            if not info:
                return
            if workspace_has_data(target):
                messagebox.showerror(
                    "Перенесення даних",
                    "У вибраній папці вже є дані Taxo. Щоб відкрити їх без перезапису, використайте «Підключити існуюче».",
                    parent=win
                ); return
            if not messagebox.askyesno(
                "Перенести всі робочі дані",
                f"Створити перевірену копію всього поточного сховища?\n\nЗвідки:\n{DATA_ROOT}\n\nКуди:\n{target}\n\n"
                "Основна та тахографічна SQLite-БД будуть скопійовані узгоджено. Старе сховище не видаляється.",
                parent=win
            ):
                return
            destination_lock=WorkspaceLock(target,"v8.70-r9-transfer")
            try:
                destination_lock.acquire(force=bool(read_lock_info(target) and read_lock_info(target).get("stale")))
                clone_workspace(DATA_ROOT,target)
            except Exception as exc:
                messagebox.showerror("Перенесення даних",f"Перенесення не завершено:\n\n{exc}\n\nПоточне сховище не змінено.",parent=win)
                return
            finally:
                destination_lock.release()
            self._close_after_workspace_switch(target,"Усі робочі дані перевірено й скопійовано.")

        buttons=ttk.Frame(body); buttons.pack(fill="x",pady=(8,0))
        ttk.Button(buttons,text="Перенести поточні дані…",command=copy_current).pack(side="left")
        ttk.Button(buttons,text="Підключити існуюче…",command=attach_existing).pack(side="left",padx=8)
        ttk.Button(buttons,text="Відкрити поточну папку",command=self.open_data_folder).pack(side="left")
        ttk.Button(buttons,text="Закрити",command=win.destroy).pack(side="right")

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
        ttk.Button(top, text="Реєстр усіх працівників", command=self.show_employee_registry).pack(side="left", padx=4)
        ttk.Button(top, text="Табель персоналу", command=self.show_employee_timesheet).pack(side="left", padx=4)
        ttk.Separator(top,orient="vertical").pack(side="left",fill="y",padx=6)
        ttk.Button(top, text="Новий водій", command=self.new_driver).pack(side="left", padx=4)
        ttk.Button(top, text="Редагувати", command=self.edit_driver).pack(side="left", padx=4)
        ttk.Button(top, text="Завершити роль водія", command=self.delete_driver).pack(side="left", padx=4)
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
        self.driver_tree.bind("<Double-1>",lambda _event:self.edit_driver())
        self.driver_tree.bind("<Return>",lambda _event:self.edit_driver())

    def employee_full_name(self, row):
        return " ".join(x for x in (row["last_name"],row["first_name"],row["middle_name"]) if x).strip()

    def show_employee_registry(self):
        if hasattr(self,"employee_win") and self.employee_win.winfo_exists():
            self.employee_win.lift(); self.load_employee_registry(); return
        win=tk.Toplevel(self); self.employee_win=win; win.title("Реєстр усіх працівників")
        fit_window_to_screen(win,1080,650,820,500)
        top=ttk.Frame(win,padding=8); top.pack(fill="x")
        ttk.Button(top,text="Новий працівник",command=self.employee_form).pack(side="left",padx=3)
        ttk.Button(top,text="Редагувати",command=self.edit_employee).pack(side="left",padx=3)
        ttk.Button(top,text="Звільнити / поновити",command=self.toggle_employee_active).pack(side="left",padx=3)
        ttk.Button(top,text="Зміни випуску",command=self.show_dispatch_staff_schedule).pack(side="left",padx=3)
        ttk.Button(top,text="Табель персоналу",command=self.show_employee_timesheet).pack(side="left",padx=3)
        ttk.Label(win,text="Водій є працівником із додатковою водійською карткою. Лікаря, механіка, диспетчера та інших вводьте тут один раз.",foreground="gray",wraplength=1020,justify="left").pack(fill="x",padx=10,pady=(0,6))
        frame=ttk.Frame(win); frame.pack(fill="both",expand=True,padx=10,pady=6)
        frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
        cols=("id","personnel","name","gender","roles","position","tariff","employment","dismissal","phone","status")
        self.employee_tree=ttk.Treeview(frame,columns=cols,show="headings")
        heads={"id":"ID","personnel":"Таб. №","name":"ПІБ","gender":"Стать","roles":"Ролі","position":"Посада","tariff":"Оклад / ставка","employment":"Прийнятий","dismissal":"Звільнений","phone":"Телефон","status":"Стан"}
        widths={"id":45,"personnel":75,"name":220,"gender":55,"roles":170,"position":145,"tariff":105,"employment":90,"dismissal":90,"phone":120,"status":80}
        for key in cols: self.employee_tree.heading(key,text=heads[key]); self.employee_tree.column(key,width=widths[key],anchor="w")
        y=ttk.Scrollbar(frame,orient="vertical",command=self.employee_tree.yview); x=ttk.Scrollbar(frame,orient="horizontal",command=self.employee_tree.xview)
        self.employee_tree.configure(yscrollcommand=y.set,xscrollcommand=x.set)
        self.employee_tree.grid(row=0,column=0,sticky="nsew"); y.grid(row=0,column=1,sticky="ns"); x.grid(row=1,column=0,sticky="ew")
        self.employee_tree.bind("<Double-1>",lambda _e:self.edit_employee())
        self.load_employee_registry()

    def load_employee_registry(self):
        if not hasattr(self,"employee_tree") or not self.employee_tree.winfo_exists(): return
        for item in self.employee_tree.get_children(): self.employee_tree.delete(item)
        con=db(); rows=con.execute("""SELECT e.*,GROUP_CONCAT(er.role, ', ') roles FROM employees e
             LEFT JOIN employee_roles er ON er.employee_id=e.id GROUP BY e.id
             ORDER BY e.active DESC,e.last_name,e.first_name,e.middle_name""").fetchall(); con.close()
        for row in rows:
            tariff="" if "tariff_rate" not in row.keys() or row["tariff_rate"] is None else f"{float(row['tariff_rate']):.2f}"
            gender=(row["gender"] if "gender" in row.keys() else "") or ""
            self.employee_tree.insert("","end",values=(row["id"],row["personnel_no"],self.employee_full_name(row),gender,row["roles"] or "",row["position"],tariff,fmt_date(row["employment_date"]),fmt_date(row["dismissal_date"]),row["phone"],"Працює" if row["active"] else "Звільнений"))

    def selected_employee(self):
        sel=getattr(self,"employee_tree",None).selection() if hasattr(self,"employee_tree") else ()
        if not sel: return None
        eid=int(self.employee_tree.item(sel[0],"values")[0]); con=db()
        row=con.execute("SELECT * FROM employees WHERE id=?",(eid,)).fetchone(); con.close(); return row

    def employee_form(self, employee=None):
        parent=getattr(self,"employee_win",self); win=tk.Toplevel(parent); win.title("Картка працівника")
        fit_window_to_screen(win,700,650,610,520); win.transient(parent); win.grab_set()
        con=db(); current_roles={r[0] for r in con.execute("SELECT role FROM employee_roles WHERE employee_id=?",(employee["id"],)).fetchall()} if employee else set(); con.close()
        fields=(("personnel_no","Табельний номер"),("last_name","Прізвище"),("first_name","Ім'я"),("middle_name","По батькові"),("position","Основна посада"),("gender","Стать для П-5 (ч/ж)"),("tariff_rate","Оклад / тарифна ставка, грн"),("phone","Телефон"),("employment_date","Дата прийняття"),("dismissal_date","Дата звільнення"),("notes","Примітка"))
        values={}
        for i,(key,label) in enumerate(fields):
            if employee and key in employee.keys():
                raw=employee[key]
            else:
                raw=""
            if raw is None:
                raw=""
            if key=="tariff_rate" and raw!="":
                try: raw=f"{float(raw):.2f}".rstrip("0").rstrip(".")
                except Exception: raw=str(raw)
            if key in {"employment_date","dismissal_date"}: raw=fmt_date(raw)
            values[key]=tk.StringVar(value=raw)
            ttk.Label(win,text=label).grid(row=i,column=0,sticky="w",padx=10,pady=5)
            if key=="gender":
                widget=ttk.Combobox(win,textvariable=values[key],values=("", "ч", "ж"),state="readonly",width=12)
            else:
                widget=ttk.Entry(win,textvariable=values[key],width=48)
            widget.grid(row=i,column=1,sticky="ew",padx=10,pady=5)
            if key in {"employment_date","dismissal_date"}: calendar_button(win,values[key]).grid(row=i,column=2,sticky="w",padx=(0,8))
        win.columnconfigure(1,weight=1)
        role_box=ttk.LabelFrame(win,text="Спеціальні ролі працівника (необов'язково)",padding=8); role_box.grid(row=len(fields),column=0,columnspan=3,sticky="ew",padx=10,pady=8)
        role_vars={}
        for i,role in enumerate(("Водій","Лікар","Механік","Диспетчер","Кондуктор","Інше")):
            role_vars[role]=tk.BooleanVar(value=role in current_roles)
            ttk.Checkbutton(role_box,text=role,variable=role_vars[role]).grid(row=i//3,column=i%3,sticky="w",padx=8,pady=3)
        ttk.Label(
            role_box,
            text="Щоб зняти роль водія: приберіть прапорець «Водій» і натисніть «Зберегти». Історія графіка не видаляється.",
            foreground="gray",wraplength=610,justify="left"
        ).grid(row=2,column=0,columnspan=3,sticky="w",padx=8,pady=(7,2))
        active=tk.BooleanVar(value=bool(employee["active"]) if employee else True)
        ttk.Checkbutton(win,text="Працює",variable=active).grid(row=len(fields)+1,column=1,sticky="w",padx=10,pady=3)
        def save():
            vals={k:v.get().strip() for k,v in values.items()}
            if not vals["last_name"] or not vals["first_name"]:
                messagebox.showerror("Працівник","Прізвище та ім'я обов'язкові.",parent=win); return
            roles=[r for r,v in role_vars.items() if v.get()]
            closing_driver=bool(employee and employee["driver_id"] and "Водій" in current_roles and "Водій" not in roles)
            driver_end_date=""
            if closing_driver:
                if not messagebox.askyesno(
                    "Завершити роль водія",
                    "Зняти роль «Водій»? Водійська картка стане неактивною, але весь старий графік, табель і шляхівки залишаться.",
                    parent=win,
                ):
                    return
                raw_end=simpledialog.askstring(
                    "Дата завершення ролі",
                    "Дата завершення роботи водієм (ДД.ММ.РРРР):",
                    initialvalue=date.today().strftime("%d.%m.%Y"),parent=win,
                )
                if raw_end is None:
                    return
                try:
                    driver_end_date=datetime.strptime(raw_end.strip(),"%d.%m.%Y").strftime("%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Працівник","Дата завершення ролі має бути у форматі ДД.ММ.РРРР.",parent=win); return
            for key in ("employment_date","dismissal_date"):
                if vals[key]:
                    try: vals[key]=datetime.strptime(vals[key],"%d.%m.%Y").strftime("%Y-%m-%d")
                    except ValueError:
                        messagebox.showerror("Працівник","Дата має бути у форматі ДД.ММ.РРРР.",parent=win); return
            vals["gender"]=vals["gender"].lower()
            if vals["gender"] not in ("","ч","ж"):
                messagebox.showerror("Працівник","Стать для П-5: залиште порожньо або виберіть «ч» / «ж».",parent=win); return
            tariff_rate=None
            if vals["tariff_rate"]:
                try:
                    tariff_rate=float(vals["tariff_rate"].replace(",","."))
                    if tariff_rate < 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Працівник","Оклад / тарифна ставка мають бути невід'ємним числом.",parent=win); return
            con=db()
            if vals["personnel_no"] and con.execute("SELECT 1 FROM employees WHERE personnel_no=? AND id<>?",(vals["personnel_no"],employee["id"] if employee else -1)).fetchone():
                con.close(); messagebox.showerror("Працівник","Такий табельний номер уже використовується.",parent=win); return
            driver_id=employee["driver_id"] if employee else None
            if "Водій" in roles and not driver_id:
                cur=con.execute("""INSERT INTO drivers(last_name,first_name,middle_name,personnel_no,employment_date,notes,active,created_at)
                    VALUES(?,?,?,?,?,?,?,?)""",(vals["last_name"],vals["first_name"],vals["middle_name"],vals["personnel_no"],vals["employment_date"],vals["notes"],int(active.get()),datetime.now().isoformat(timespec="seconds")))
                driver_id=cur.lastrowid
            if employee:
                eid=employee["id"]
                con.execute("""UPDATE employees SET personnel_no=?,last_name=?,first_name=?,middle_name=?,position=?,gender=?,tariff_rate=?,phone=?,employment_date=?,dismissal_date=?,notes=?,active=?,driver_id=? WHERE id=?""",
                    (vals["personnel_no"],vals["last_name"],vals["first_name"],vals["middle_name"],vals["position"],vals["gender"],tariff_rate,vals["phone"],vals["employment_date"],vals["dismissal_date"],vals["notes"],int(active.get()),driver_id,eid))
            else:
                cur=con.execute("""INSERT INTO employees(personnel_no,last_name,first_name,middle_name,position,gender,tariff_rate,phone,employment_date,dismissal_date,notes,active,driver_id,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(vals["personnel_no"],vals["last_name"],vals["first_name"],vals["middle_name"],vals["position"],vals["gender"],tariff_rate,vals["phone"],vals["employment_date"],vals["dismissal_date"],vals["notes"],int(active.get()),driver_id,datetime.now().isoformat(timespec="seconds"))); eid=cur.lastrowid
            con.execute("DELETE FROM employee_roles WHERE employee_id=?",(eid,))
            con.executemany("INSERT INTO employee_roles(employee_id,role) VALUES(?,?)",[(eid,r) for r in roles])
            if driver_id:
                driver_row=con.execute(
                    "SELECT driver_end_date FROM drivers WHERE id=?",(driver_id,)
                ).fetchone()
                stored_driver_end=((driver_row["driver_end_date"] if driver_row else "") or "").strip()
                if "Водій" in roles:
                    next_driver_end=""
                elif closing_driver:
                    next_driver_end=driver_end_date
                else:
                    next_driver_end=stored_driver_end
                driver_active=int(active.get() and "Водій" in roles)
                con.execute("""UPDATE drivers SET last_name=?,first_name=?,middle_name=?,personnel_no=?,employment_date=?,driver_end_date=?,notes=?,active=? WHERE id=?""",
                    (vals["last_name"],vals["first_name"],vals["middle_name"],vals["personnel_no"],vals["employment_date"],next_driver_end,vals["notes"],driver_active,driver_id))
                if closing_driver:
                    finish_driver_role(con,eid,driver_id,driver_end_date)
            con.commit(); con.close(); self.load_employee_registry(); self.load_drivers(); win.destroy()
        ttk.Button(win,text="Зберегти",command=save).grid(row=len(fields)+2,column=1,sticky="e",padx=10,pady=12)

    def edit_employee(self):
        row=self.selected_employee()
        if row: self.employee_form(row)

    def toggle_employee_active(self):
        row=self.selected_employee()
        if not row: return
        new_state=0 if row["active"] else 1
        today=date.today().isoformat()
        con=db()
        con.execute(
            "UPDATE employees SET active=?,dismissal_date=CASE WHEN ?=0 AND COALESCE(dismissal_date,'')='' THEN ? WHEN ?=1 THEN '' ELSE dismissal_date END WHERE id=?",
            (new_state,new_state,today,new_state,row["id"]),
        )
        if row["driver_id"] and new_state==0:
            # Dismissal ends the current driver role. Re-employment is separate
            # and must not silently restore that role.
            driver=con.execute(
                "SELECT active,driver_end_date FROM drivers WHERE id=?",(row["driver_id"],)
            ).fetchone()
            if driver and bool(driver["active"]):
                end_date=(driver["driver_end_date"] or "").strip() or today
                finish_driver_role(con,row["id"],row["driver_id"],end_date)
        con.commit(); con.close(); self.load_employee_registry(); self.load_drivers()

    def show_employee_timesheet(self):
        parent=getattr(self,"employee_win",self); win=tk.Toplevel(parent); win.title("Табель робочого часу всіх працівників")
        fit_window_to_screen(win,1360,760,960,560)
        top=ttk.Frame(win,padding=8); top.pack(fill="x")
        today=date.today(); month=tk.StringVar(value=str(today.month)); year=tk.StringVar(value=str(today.year))
        ttk.Label(top,text="Місяць").pack(side="left"); ttk.Spinbox(top,textvariable=month,from_=1,to=12,width=5).pack(side="left",padx=4)
        ttk.Label(top,text="Рік").pack(side="left"); ttk.Spinbox(top,textvariable=year,from_=2020,to=2100,width=7).pack(side="left",padx=4)
        notebook=ttk.Notebook(win); notebook.pack(fill="both",expand=True,padx=8,pady=(0,8))
        summary_tab=ttk.Frame(notebook); daily_tab=ttk.Frame(notebook)
        notebook.add(summary_tab,text="Підсумок місяця"); notebook.add(daily_tab,text="Щоденний табель")

        summary_frame=ttk.Frame(summary_tab); summary_frame.pack(fill="both",expand=True,padx=4,pady=6)
        summary_frame.rowconfigure(0,weight=1); summary_frame.columnconfigure(0,weight=1)
        summary_cols=("id","personnel","name","roles","planned","actual","difference","missing")
        summary_tree=ttk.Treeview(summary_frame,columns=summary_cols,show="headings")
        for key,label,width in (("id","ID",45),("personnel","Таб. №",80),("name","ПІБ",270),("roles","Ролі",210),("planned","План",85),("actual","Факт",85),("difference","Відхилення",90),("missing","Без факту",90)):
            summary_tree.heading(key,text=label); summary_tree.column(key,width=width,anchor="w")
        sy=ttk.Scrollbar(summary_frame,orient="vertical",command=summary_tree.yview); sx=ttk.Scrollbar(summary_frame,orient="horizontal",command=summary_tree.xview)
        summary_tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set)
        summary_tree.grid(row=0,column=0,sticky="nsew"); sy.grid(row=0,column=1,sticky="ns"); sx.grid(row=1,column=0,sticky="ew")

        daily_top=ttk.Frame(daily_tab,padding=(4,6)); daily_top.pack(fill="x")
        employee_choice=tk.StringVar(); ttk.Label(daily_top,text="Працівник").pack(side="left")
        employee_combo=ttk.Combobox(daily_top,textvariable=employee_choice,state="readonly",width=48); employee_combo.pack(side="left",padx=6)
        ttk.Label(daily_top,text="План — із графіка або зміни; факт і уточнення — з ручного табеля.",foreground="gray").pack(side="left",padx=8)

        edit_bar=ttk.Frame(daily_tab,padding=(4,0,4,3)); edit_bar.pack(fill="x")
        report_bar=ttk.Frame(daily_tab,padding=(4,0,4,5)); report_bar.pack(fill="x")
        daily_frame=ttk.Frame(daily_tab); daily_frame.pack(fill="both",expand=True,padx=4,pady=(0,6)); daily_frame.rowconfigure(0,weight=1); daily_frame.columnconfigure(0,weight=1)
        daily_cols=("date","weekday","day_type","planned","actual","difference","source","notes")
        daily_tree=ttk.Treeview(daily_frame,columns=daily_cols,show="headings",selectmode="extended")
        for key,label,width in (("date","Дата",90),("weekday","День",75),("day_type","Вид дня",115),("planned","План",70),("actual","Факт",70),("difference","Відхилення",85),("source","Джерело",190),("notes","Примітка",260)):
            daily_tree.heading(key,text=label); daily_tree.column(key,width=width,anchor="w")
        dy=ttk.Scrollbar(daily_frame,orient="vertical",command=daily_tree.yview); dx=ttk.Scrollbar(daily_frame,orient="horizontal",command=daily_tree.xview)
        daily_tree.configure(yscrollcommand=dy.set,xscrollcommand=dx.set)
        daily_tree.grid(row=0,column=0,sticky="nsew"); dy.grid(row=0,column=1,sticky="ns"); dx.grid(row=1,column=0,sticky="ew")

        employee_map={}; clipboard={"value":None}; last_files={"pdf":None,"xlsx":None}
        def selected_month():
            try:
                m=int(month.get()); yy=int(year.get())
                return date(yy,m,1),calendar.monthrange(yy,m)[1]
            except Exception:
                messagebox.showerror("Табель","Перевірте місяць і рік.",parent=win); return None,None

        def load_employees():
            nonlocal employee_map
            con=db(); rows=con.execute("""SELECT e.*,GROUP_CONCAT(er.role, ', ') roles FROM employees e
                LEFT JOIN employee_roles er ON er.employee_id=e.id GROUP BY e.id ORDER BY e.active DESC,e.last_name,e.first_name""").fetchall(); con.close()
            employee_map={f"{row['personnel_no'] or '—'} | {self.employee_full_name(row)}":row for row in rows}
            employee_combo["values"]=list(employee_map)
            if employee_choice.get() not in employee_map and employee_map:
                employee_choice.set(next(iter(employee_map)))
            return rows

        def refresh_daily():
            start,days=selected_month()
            if not start: return
            employee=employee_map.get(employee_choice.get())
            for item in daily_tree.get_children(): daily_tree.delete(item)
            if not employee: return
            con=db()
            weekday_names=("Пн","Вт","Ср","Чт","Пт","Сб","Нд")
            for day_no in range(1,days+1):
                work_date=start.replace(day=day_no)
                if employee_employed_on(employee,work_date):
                    row=employee_day_time(con,employee["id"],work_date)
                else:
                    row={"day_type":"—","planned_minutes":0,"actual_minutes":None,"source":"поза періодом роботи","notes":""}
                actual=row["actual_minutes"]
                difference=(actual-row["planned_minutes"]) if actual is not None else None
                daily_tree.insert("","end",iid=work_date.isoformat(),values=(
                    work_date.strftime("%d.%m.%Y"),weekday_names[work_date.weekday()],row["day_type"],
                    minutes_hhmm(row["planned_minutes"]),minutes_hhmm(actual) if actual is not None else "—",
                    signed_hours_hhmm((difference or 0)/60) if difference is not None else "—",
                    row["source"],row["notes"],
                ))
            con.close()

        def refresh_summary():
            start,days=selected_month()
            if not start: return
            rows=load_employees()
            for item in summary_tree.get_children(): summary_tree.delete(item)
            con=db()
            for employee in rows:
                planned=actual=missing=0
                for day_no in range(1,days+1):
                    work_date=start.replace(day=day_no)
                    if not employee_employed_on(employee,work_date):
                        continue
                    row=employee_day_time(con,employee["id"],work_date)
                    planned+=row["planned_minutes"]
                    if row["actual_minutes"] is not None: actual+=row["actual_minutes"]
                    elif row["planned_minutes"]>0: missing+=1
                summary_tree.insert("","end",values=(employee["id"],employee["personnel_no"],self.employee_full_name(employee),employee["roles"] or employee["position"] or "",
                    minutes_hhmm(planned),minutes_hhmm(actual),signed_hours_hhmm((actual-planned)/60),str(missing)))
            con.close(); refresh_daily()

        def selected_days():
            return [datetime.strptime(item,"%Y-%m-%d").date() for item in daily_tree.selection()]

        def selected_day():
            days=selected_days(); return days[0] if days else None

        def edit_day():
            employee=employee_map.get(employee_choice.get()); work_date=selected_day()
            if not employee or not work_date:
                messagebox.showinfo("Табель","Виберіть день у щоденному табелі.",parent=win); return
            if not employee_employed_on(employee,work_date):
                messagebox.showwarning("Табель","Ця дата поза періодом роботи працівника.",parent=win); return
            con=db(); current=employee_day_time(con,employee["id"],work_date)
            entry=con.execute("SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",(employee["id"],work_date.isoformat())).fetchone(); con.close()
            dialog=tk.Toplevel(win); dialog.title(f"Табель: {self.employee_full_name(employee)}, {work_date.strftime('%d.%m.%Y')}")
            fit_window_to_screen(dialog,720,650,620,540); dialog.transient(win); dialog.grab_set()
            entry_keys=set(entry.keys()) if entry is not None and hasattr(entry,"keys") else set()
            day_type=tk.StringVar(value=entry["day_type"] if entry else current["day_type"])
            plan=tk.StringVar(value=hours_value_hhmm(entry["planned_hours"]) if entry and entry["planned_hours"] is not None else "")
            actual=tk.StringVar(value=hours_value_hhmm(entry["actual_hours"]) if entry and entry["actual_hours"] is not None else "")
            overtime=tk.StringVar(value=hours_value_hhmm(entry["overtime_hours"]) if entry and "overtime_hours" in entry_keys and entry["overtime_hours"] is not None else "")
            night=tk.StringVar(value=hours_value_hhmm(entry["night_hours"]) if entry and "night_hours" in entry_keys and entry["night_hours"] is not None else "")
            evening=tk.StringVar(value=hours_value_hhmm(entry["evening_hours"]) if entry and "evening_hours" in entry_keys and entry["evening_hours"] is not None else "")
            weekend_holiday=tk.StringVar(value=hours_value_hhmm(entry["weekend_holiday_hours"]) if entry and "weekend_holiday_hours" in entry_keys and entry["weekend_holiday_hours"] is not None else "")
            notes=tk.StringVar(value=entry["notes"] if entry else "")
            ttk.Label(dialog,text="Вид дня").grid(row=0,column=0,sticky="w",padx=10,pady=7)
            ttk.Combobox(dialog,textvariable=day_type,values=DAY_TYPES,state="readonly",width=38).grid(row=0,column=1,sticky="ew",padx=10,pady=7)
            ttk.Label(dialog,text="План, ГГ:ХХ").grid(row=1,column=0,sticky="w",padx=10,pady=7)
            ttk.Entry(dialog,textvariable=plan).grid(row=1,column=1,sticky="ew",padx=10,pady=7)
            ttk.Label(dialog,text=f"Порожньо = автоматично {minutes_hhmm(current['planned_minutes'])}",foreground="gray").grid(row=2,column=1,sticky="w",padx=10)
            ttk.Label(dialog,text="Факт — відпрацьовано всього, ГГ:ХХ").grid(row=3,column=0,sticky="w",padx=10,pady=7)
            ttk.Entry(dialog,textvariable=actual).grid(row=3,column=1,sticky="ew",padx=10,pady=7)

            fact_box=ttk.LabelFrame(dialog,text="Фактичні категорії для типової форми П-5",padding=8)
            fact_box.grid(row=4,column=0,columnspan=2,sticky="ew",padx=10,pady=8)
            fact_box.columnconfigure(1,weight=1)
            for rr,(label,var) in enumerate((
                ("Надурочні години (НУ 05), ГГ:ХХ",overtime),
                ("Нічні години 22:00–06:00 (РН 04), ГГ:ХХ",night),
                ("Вечірні години (ВЧ 03), ГГ:ХХ",evening),
                ("Робота у вихідні / святкові (РВ 06), ГГ:ХХ",weekend_holiday),
            )):
                ttk.Label(fact_box,text=label).grid(row=rr,column=0,sticky="w",padx=(0,8),pady=4)
                ttk.Entry(fact_box,textvariable=var,width=14).grid(row=rr,column=1,sticky="w",pady=4)
            ttk.Label(
                fact_box,
                text=("Ці поля — фактичні складові загального факту. Вечірні години Taxo не вигадує автоматично: "
                      "їх вносять за правилом/колективним договором підприємства."),
                foreground="gray",wraplength=620,justify="left"
            ).grid(row=4,column=0,columnspan=2,sticky="w",pady=(5,0))

            ttk.Label(dialog,text="Примітка").grid(row=5,column=0,sticky="w",padx=10,pady=7)
            ttk.Entry(dialog,textvariable=notes).grid(row=5,column=1,sticky="ew",padx=10,pady=7)
            dialog.columnconfigure(1,weight=1)

            def save_entry():
                try:
                    plan_value=minutes_to_db_hours(hours_value_to_minutes(plan.get())) if plan.get().strip() else None
                    actual_value=minutes_to_db_hours(hours_value_to_minutes(actual.get())) if actual.get().strip() else None
                    special_vars=(overtime,night,evening,weekend_holiday)
                    special_values=[
                        minutes_to_db_hours(hours_value_to_minutes(v.get())) if v.get().strip() else None
                        for v in special_vars
                    ]
                    special_minutes=[
                        hours_value_to_minutes(v.get()) if v.get().strip() else 0
                        for v in special_vars
                    ]
                except ValueError as exc:
                    messagebox.showerror("Табель",str(exc),parent=dialog); return
                if actual_value is None and any(special_minutes):
                    messagebox.showerror(
                        "Табель",
                        "Спочатку внесіть загальний фактично відпрацьований час. Спеціальні категорії П-5 не можуть існувати без факту.",
                        parent=dialog
                    ); return
                if actual_value is not None:
                    total_actual=hours_value_to_minutes(actual.get())
                    labels=("Надурочні","Нічні","Вечірні","Вихідні/святкові")
                    for label,mins in zip(labels,special_minutes):
                        if mins>total_actual:
                            messagebox.showerror("Табель",f"{label} години не можуть перевищувати загальний факт.",parent=dialog); return
                con=db(); now=datetime.now().isoformat(timespec="seconds")
                con.execute("""INSERT INTO employee_time_entries(
                        employee_id,work_date,day_type,planned_hours,actual_hours,
                        overtime_hours,night_hours,evening_hours,weekend_holiday_hours,
                        notes,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(employee_id,work_date) DO UPDATE SET
                        day_type=excluded.day_type,planned_hours=excluded.planned_hours,
                        actual_hours=excluded.actual_hours,overtime_hours=excluded.overtime_hours,
                        night_hours=excluded.night_hours,evening_hours=excluded.evening_hours,
                        weekend_holiday_hours=excluded.weekend_holiday_hours,
                        notes=excluded.notes,updated_at=excluded.updated_at""",
                    (employee["id"],work_date.isoformat(),day_type.get(),plan_value,actual_value,
                     special_values[0],special_values[1],special_values[2],special_values[3],
                     notes.get().strip(),now,now))
                con.commit(); con.close(); dialog.destroy(); refresh_summary()
            ttk.Button(dialog,text="Зберегти",command=save_entry).grid(row=6,column=1,sticky="e",padx=10,pady=14)

        def copy_day():
            employee=employee_map.get(employee_choice.get()); work_date=selected_day()
            if not employee or not work_date:
                messagebox.showwarning("Копіювання","Виберіть один день у щоденному табелі.",parent=win); return
            con=db()
            current=employee_day_time(con,employee["id"],work_date)
            manual=con.execute(
                "SELECT * FROM employee_time_entries WHERE employee_id=? AND work_date=?",
                (employee["id"],work_date.isoformat())
            ).fetchone()
            con.close()
            manual_keys=set(manual.keys()) if manual is not None and hasattr(manual,"keys") else set()
            clipboard["value"]={
                "day_type":current["day_type"],
                "planned_hours":minutes_to_db_hours(current["planned_minutes"]),
                "actual_hours":minutes_to_db_hours(current["actual_minutes"]) if current["actual_minutes"] is not None else None,
                "overtime_hours":manual["overtime_hours"] if manual is not None and "overtime_hours" in manual_keys else None,
                "night_hours":manual["night_hours"] if manual is not None and "night_hours" in manual_keys else None,
                "evening_hours":manual["evening_hours"] if manual is not None and "evening_hours" in manual_keys else None,
                "weekend_holiday_hours":manual["weekend_holiday_hours"] if manual is not None and "weekend_holiday_hours" in manual_keys else None,
                "notes":current["notes"],"source_date":work_date
            }
            try: win.clipboard_clear(); win.clipboard_append("taxo_personnel_day")
            except tk.TclError: pass
            messagebox.showinfo("Копіювання","День скопійовано. Виділіть одну або кілька дат і натисніть «Вставити день».",parent=win)

        def paste_day():
            employee=employee_map.get(employee_choice.get()); days=selected_days(); clip=clipboard["value"]
            if not employee or not days:
                messagebox.showwarning("Вставлення","Виберіть одну або кілька дат.",parent=win); return
            if not clip:
                messagebox.showwarning("Вставлення","Спочатку скопіюйте день.",parent=win); return
            con=db(); existing=con.execute(
                f"SELECT COUNT(*) FROM employee_time_entries WHERE employee_id=? AND work_date IN ({','.join('?' for _ in days)})",
                (employee["id"],*[d.isoformat() for d in days]),
            ).fetchone()[0]
            if existing and not messagebox.askyesno("Вставлення",f"Для {existing} вибраних дат уже є ручні записи. Замінити їх скопійованими даними?",parent=win):
                con.close(); return
            now=datetime.now().isoformat(timespec="seconds")
            for work_date in days:
                if not employee_employed_on(employee,work_date): continue
                con.execute("""INSERT INTO employee_time_entries(
                        employee_id,work_date,day_type,planned_hours,actual_hours,
                        overtime_hours,night_hours,evening_hours,weekend_holiday_hours,
                        notes,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(employee_id,work_date) DO UPDATE SET
                        day_type=excluded.day_type,planned_hours=excluded.planned_hours,
                        actual_hours=excluded.actual_hours,overtime_hours=excluded.overtime_hours,
                        night_hours=excluded.night_hours,evening_hours=excluded.evening_hours,
                        weekend_holiday_hours=excluded.weekend_holiday_hours,
                        notes=excluded.notes,updated_at=excluded.updated_at""",
                    (employee["id"],work_date.isoformat(),clip["day_type"],clip["planned_hours"],clip["actual_hours"],
                     clip.get("overtime_hours"),clip.get("night_hours"),clip.get("evening_hours"),clip.get("weekend_holiday_hours"),
                     clip["notes"],now,now))
            con.commit(); con.close(); refresh_summary()

        def plan_to_fact():
            employee=employee_map.get(employee_choice.get()); days=selected_days()
            if not employee or not days:
                messagebox.showwarning("Табель","Виберіть одну або кілька дат.",parent=win); return
            con=db(); now=datetime.now().isoformat(timespec="seconds")
            for work_date in days:
                if not employee_employed_on(employee,work_date): continue
                current=employee_day_time(con,employee["id"],work_date)
                con.execute("""INSERT INTO employee_time_entries(employee_id,work_date,day_type,actual_hours,notes,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?) ON CONFLICT(employee_id,work_date) DO UPDATE SET actual_hours=excluded.actual_hours,updated_at=excluded.updated_at""",
                    (employee["id"],work_date.isoformat(),current["day_type"],minutes_to_db_hours(current["planned_minutes"]),current["notes"],now,now))
            con.commit(); con.close(); refresh_summary()

        def clear_manual():
            employee=employee_map.get(employee_choice.get()); days=selected_days()
            if not employee or not days:
                messagebox.showwarning("Табель","Виберіть одну або кілька дат.",parent=win); return
            if not messagebox.askyesno("Табель",f"Прибрати ручні записи для вибраних дат ({len(days)}) і повернути автоматичні дані?",parent=win): return
            con=db(); con.executemany("DELETE FROM employee_time_entries WHERE employee_id=? AND work_date=?",[(employee["id"],d.isoformat()) for d in days]); con.commit(); con.close(); refresh_summary()

        def autofill_empty_weekdays():
            employee=employee_map.get(employee_choice.get()); start,days_count=selected_month()
            if not employee or not start: return
            if not messagebox.askyesno(
                "Небезпечна масова дія",
                f"Заповнити ПОРОЖНІ будні {month.get()}.{year.get()} для {self.employee_full_name(employee)} планом 8:00?\n\n"
                "Існуючі ручні записи, графік водія та зміни персоналу не змінюються. Факт залишиться порожнім.\nПродовжити?",
                parent=win,
            ): return
            con=db(); now=datetime.now().isoformat(timespec="seconds"); added=0
            for day_no in range(1,days_count+1):
                work_date=start.replace(day=day_no)
                if work_date.weekday()>=5 or not employee_employed_on(employee,work_date): continue
                current=employee_day_time(con,employee["id"],work_date)
                exists=con.execute("SELECT 1 FROM employee_time_entries WHERE employee_id=? AND work_date=?",(employee["id"],work_date.isoformat())).fetchone()
                if exists or current["planned_minutes"]>0: continue
                con.execute("INSERT INTO employee_time_entries(employee_id,work_date,day_type,planned_hours,actual_hours,notes,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
                            (employee["id"],work_date.isoformat(),"Робота",8.0,None,"Масове заповнення порожнього будня",now,now)); added+=1
            con.commit(); con.close(); refresh_summary(); messagebox.showinfo("Табель",f"Додано план 8:00 для {added} порожніх буднів.",parent=win)

        def export_selected(kind):
            employee=employee_map.get(employee_choice.get()); start,_days=selected_month()
            if not employee or not start:
                messagebox.showwarning("Табель","Виберіть працівника.",parent=win); return
            suffix=".xlsx" if kind=="xlsx" else ".pdf"; safe=re.sub(r"[^0-9A-Za-zА-Яа-яІіЇїЄє_-]+","_",employee["last_name"] or "Працівник")
            path=filedialog.asksaveasfilename(parent=win,title="Зберегти табель",initialdir=str(OUTPUT_DIR),initialfile=f"Табель_{safe}_{start.year}_{start.month:02d}{suffix}",defaultextension=suffix,filetypes=[("Excel","*.xlsx")] if kind=="xlsx" else [("PDF","*.pdf")])
            if not path: return
            writer=(lambda out:export_employee_timesheet_xlsx(employee["id"],start.year,start.month,out)) if kind=="xlsx" else (lambda out:export_employee_timesheet_pdf(employee["id"],start.year,start.month,out))
            actual=write_output_file(writer,path,parent=win,kind="Excel-файл табеля" if kind=="xlsx" else "PDF табеля",error_title="Помилка Excel" if kind=="xlsx" else "Помилка PDF")
            if actual is not None: last_files[kind]=actual; messagebox.showinfo("Готово",f"Файл створено:\n{actual}",parent=win)

        def show_control():
            employee=employee_map.get(employee_choice.get()); start,_days=selected_month()
            if not employee or not start: return
            data=collect_employee_timesheet(employee["id"],start.year,start.month)
            dialog=tk.Toplevel(win); dialog.title("Підсумки / контроль персоналу"); fit_window_to_screen(dialog,720,500,600,420)
            text=tk.Text(dialog,wrap="word",font=("TkDefaultFont",10)); scroll=ttk.Scrollbar(dialog,command=text.yview); text.configure(yscrollcommand=scroll.set); scroll.pack(side="right",fill="y"); text.pack(fill="both",expand=True,padx=10,pady=10)
            lines=[f"Працівник: {employee_name(data['employee'])}",f"Період: {month_name_ua(data['month'])} {data['year']}","",f"План: {minutes_hhmm(data['planned_minutes'])}",f"Факт: {minutes_hhmm(data['actual_minutes'])}",f"Відхилення: {signed_hours_hhmm(data['difference_minutes']/60)}",f"Робочих днів: {data['work_days']}",f"Днів із планом без факту: {data['missing_days']}",""]
            missing=[r["date"].strftime("%d.%m.%Y") for r in data["rows"] if r["planned_minutes"]>0 and r["actual_minutes"] is None]
            lines.append("Потрібно внести факт: "+(", ".join(missing) if missing else "немає"))
            types={}
            for row in data["rows"]: types[row["day_type"]]=types.get(row["day_type"],0)+1
            lines.extend(["","Дні за видами:"]+[f"  {key}: {value}" for key,value in sorted(types.items())])
            text.insert("1.0","\n".join(lines)); text.configure(state="disabled")

        def show_personnel_balance():
            start,_days=selected_month()
            if not start: return
            dialog=tk.Toplevel(win); dialog.title("Місячний табель / баланс усього персоналу"); fit_window_to_screen(dialog,1500,760,960,520)
            bar=ttk.Frame(dialog,padding=8); bar.pack(fill="x"); active_only=tk.BooleanVar(value=True); last={"pdf":None}
            ttk.Checkbutton(bar,text="Тільки активні працівники",variable=active_only).pack(side="left")
            frame=ttk.Frame(dialog); frame.pack(fill="both",expand=True,padx=8,pady=(0,6)); frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
            tree=ttk.Treeview(frame,show="headings"); yscroll=ttk.Scrollbar(frame,orient="vertical",command=tree.yview); xscroll=ttk.Scrollbar(frame,orient="horizontal",command=tree.xview); tree.configure(yscrollcommand=yscroll.set,xscrollcommand=xscroll.set); tree.grid(row=0,column=0,sticky="nsew"); yscroll.grid(row=0,column=1,sticky="ns"); xscroll.grid(row=1,column=0,sticky="ew")
            status=tk.StringVar(); ttk.Label(dialog,textvariable=status,font=("TkDefaultFont",9,"bold")).pack(fill="x",padx=10,pady=(0,6))
            def refresh_balance():
                data=collect_personnel_monthly_balance(start.year,start.month,active_only.get()); columns=["personnel","employee","roles"]+[f"d{d.day}" for d in data["days"]]+["days","plan","actual","difference","missing"]; tree["columns"]=columns
                labels={"personnel":"Таб. №","employee":"Працівник","roles":"Ролі","days":"Днів","plan":"План","actual":"Факт","difference":"Відх.","missing":"Без факту"}
                for col in columns:
                    label=labels.get(col,col[1:]); tree.heading(col,text=label); tree.column(col,width=210 if col=="employee" else 140 if col=="roles" else 70,anchor="w" if col in ("employee","roles") else "center",stretch=False)
                for item in tree.get_children(): tree.delete(item)
                for employee_row in data["employees"]:
                    tree.insert("","end",values=[employee_row["personnel_no"],employee_row["name"],employee_row["roles"],*employee_row["cells"],employee_row["work_days"],minutes_hhmm(employee_row["planned_min"]),minutes_hhmm(employee_row["actual_min"]),signed_hours_hhmm(employee_row["difference_min"]/60),employee_row["missing_days"]])
                status.set(f"{month_name_ua(start.month)} {start.year}: працівників {len(data['employees'])}; без факту загалом {sum(e['missing_days'] for e in data['employees'])}")
            def save_balance(kind):
                suffix=".xlsx" if kind=="xlsx" else ".pdf"; path=filedialog.asksaveasfilename(parent=dialog,title="Зберегти табель усього персоналу",initialdir=str(OUTPUT_DIR),initialfile=f"Табель_усього_персоналу_{start.year}_{start.month:02d}{suffix}",defaultextension=suffix,filetypes=[("Excel","*.xlsx")] if kind=="xlsx" else [("PDF","*.pdf")])
                if not path: return
                writer=(lambda out:export_personnel_monthly_balance_xlsx(start.year,start.month,out,active_only.get())) if kind=="xlsx" else (lambda out:export_personnel_monthly_balance_pdf(start.year,start.month,out,active_only.get()))
                actual=write_output_file(writer,path,parent=dialog,kind="Excel-файл місячного табеля" if kind=="xlsx" else "PDF місячного табеля",error_title="Помилка Excel" if kind=="xlsx" else "Помилка PDF")
                if actual is not None: last[kind]=actual; messagebox.showinfo("Місячний табель",f"Файл створено:\n{actual}",parent=dialog)
            ttk.Button(bar,text="Оновити",command=refresh_balance).pack(side="left",padx=5); ttk.Button(bar,text="Excel — редагувати",command=lambda:save_balance("xlsx")).pack(side="left",padx=(12,3)); ttk.Button(bar,text="PDF — друк",command=lambda:save_balance("pdf")).pack(side="left",padx=3)
            active_only.trace_add("write",lambda *_args:refresh_balance()); refresh_balance()

        def open_summary_employee(_event=None):
            sel=summary_tree.selection()
            if not sel: return
            eid=int(summary_tree.item(sel[0],"values")[0])
            for label,row in employee_map.items():
                if row["id"]==eid: employee_choice.set(label); break
            notebook.select(daily_tab); refresh_daily()

        ttk.Button(top,text="Оновити",command=refresh_summary).pack(side="left",padx=8)
        ttk.Button(edit_bar,text="Новий / редагувати день",command=edit_day).pack(side="left",padx=3)
        ttk.Button(edit_bar,text="Копіювати день",command=copy_day).pack(side="left",padx=3)
        ttk.Button(edit_bar,text="Вставити день",command=paste_day).pack(side="left",padx=3)
        ttk.Button(edit_bar,text="План → факт",command=plan_to_fact).pack(side="left",padx=(12,3))
        ttk.Button(edit_bar,text="Очистити ручний запис",command=clear_manual).pack(side="left",padx=3)
        ttk.Button(edit_bar,text="⚠ Порожні будні — план 8 год",command=autofill_empty_weekdays).pack(side="right",padx=3)
        ttk.Label(report_bar,text="Звіти:").pack(side="left",padx=(0,3))
        ttk.Button(report_bar,text="Excel",command=lambda:export_selected("xlsx")).pack(side="left",padx=3)
        ttk.Button(report_bar,text="PDF",command=lambda:export_selected("pdf")).pack(side="left",padx=3)
        ttk.Button(report_bar,text="Підсумки / контроль",command=show_control).pack(side="left",padx=3)
        ttk.Button(report_bar,text="Місячний табель / баланс",command=show_personnel_balance).pack(side="left",padx=3)
        employee_combo.bind("<<ComboboxSelected>>",lambda _e:refresh_daily())
        daily_tree.bind("<Double-1>",lambda _e:edit_day())
        daily_tree.bind("<Control-c>",lambda _e:copy_day())
        daily_tree.bind("<Control-v>",lambda _e:paste_day())
        if sys.platform=="darwin":
            daily_tree.bind("<Command-c>",lambda _e:copy_day()); daily_tree.bind("<Command-v>",lambda _e:paste_day())
        summary_tree.bind("<Double-1>",open_summary_employee)
        refresh_summary()

    def driver_form(self, driver=None):
        win = tk.Toplevel(self)
        win.title("Картка водія")
        fit_window_to_screen(win,760,720,700,540)
        win.transient(self)

        # Картка містить багато полів і на ноутбучному екрані не вміщується
        # по висоті. Весь вміст, включно з прапорцем і кнопкою збереження,
        # розміщуємо у вертикально прокручуваному полотні.
        shell=ttk.Frame(win)
        shell.pack(fill="both",expand=True)
        shell.rowconfigure(0,weight=1)
        shell.columnconfigure(0,weight=1)
        form_canvas=tk.Canvas(shell,highlightthickness=0,borderwidth=0)
        form_scroll=ttk.Scrollbar(shell,orient="vertical",command=form_canvas.yview)
        form_canvas.configure(yscrollcommand=form_scroll.set)
        form_canvas.grid(row=0,column=0,sticky="nsew")
        form_scroll.grid(row=0,column=1,sticky="ns")

        outer=ttk.Frame(form_canvas,padding=10)
        form_window=form_canvas.create_window((0,0),window=outer,anchor="nw")

        def sync_driver_form(_event=None):
            try:
                form_canvas.configure(scrollregion=form_canvas.bbox("all"))
            except tk.TclError:
                pass

        def fit_driver_form_width(event):
            try:
                form_canvas.itemconfigure(form_window,width=max(1,event.width))
                sync_driver_form()
            except tk.TclError:
                pass

        def scroll_driver_form(event):
            if getattr(event,"num",None)==4:
                step=-1
            elif getattr(event,"num",None)==5:
                step=1
            else:
                delta=getattr(event,"delta",0)
                if not delta:
                    return None
                step=int(-delta/120) or (-1 if delta>0 else 1)
            form_canvas.yview_scroll(step,"units")
            return "break"

        outer.bind("<Configure>",sync_driver_form,add="+")
        form_canvas.bind("<Configure>",fit_driver_form_width,add="+")
        win.bind("<MouseWheel>",scroll_driver_form,add="+")
        win.bind("<Button-4>",scroll_driver_form,add="+")
        win.bind("<Button-5>",scroll_driver_form,add="+")

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
            ("personnel_no","Табельний номер"),
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
                "personnel_no","birth_date","license_series","license_number",
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
            role_end_date=""
            if driver and bool(driver["active"]) and not active.get():
                raw_end=simpledialog.askstring(
                    "Дата завершення ролі",
                    "Дата завершення роботи водієм (ДД.ММ.РРРР):",
                    initialvalue=date.today().strftime("%d.%m.%Y"),
                    parent=win,
                )
                if raw_end is None:
                    return
                try:
                    role_end_date=datetime.strptime(raw_end.strip(),"%d.%m.%Y").strftime("%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Роль водія","Дата має бути у форматі ДД.ММ.РРРР.",parent=win)
                    return
            con=db()
            if driver:
                saved_driver_id=driver["id"]
                next_driver_end="" if active.get() else (
                    role_end_date or (driver["driver_end_date"] or "").strip()
                )
                con.execute("""UPDATE drivers SET
                    last_name=?,first_name=?,middle_name=?,
                    last_name_en=?,first_name_en=?,middle_name_en=?,
                    personnel_no=?,birth_date=?,license_series=?,license_number=?,license_issue_date=?,
                    employment_date=?,notes=?,active=?,driver_end_date=? WHERE id=?""",
                    (vals["last_name"],vals["first_name"],vals["middle_name"],
                     vals["last_name_en"],vals["first_name_en"],vals["middle_name_en"],
                     vals["personnel_no"],vals["birth_date"],vals["license_series"],vals["license_number"],
                     vals["license_issue_date"],vals["employment_date"],vals["notes"],
                     int(active.get()),next_driver_end,saved_driver_id))
            else:
                cur=con.execute("""INSERT INTO drivers(
                    last_name,first_name,middle_name,last_name_en,first_name_en,middle_name_en,
                    personnel_no,birth_date,license_series,license_number,license_issue_date,employment_date,
                    notes,active,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (vals["last_name"],vals["first_name"],vals["middle_name"],
                     vals["last_name_en"],vals["first_name_en"],vals["middle_name_en"],
                     vals["personnel_no"],vals["birth_date"],vals["license_series"],vals["license_number"],
                     vals["license_issue_date"],vals["employment_date"],vals["notes"],
                     int(active.get()),datetime.now().isoformat(timespec="seconds")))
                saved_driver_id=cur.lastrowid
            emp=con.execute("SELECT id FROM employees WHERE driver_id=?",(saved_driver_id,)).fetchone()
            if emp:
                employee_id=emp["id"]
                con.execute("""UPDATE employees SET personnel_no=?,last_name=?,first_name=?,middle_name=?,employment_date=?,notes=? WHERE id=?""",
                    (vals["personnel_no"],vals["last_name"],vals["first_name"],vals["middle_name"],vals["employment_date"],vals["notes"],employee_id))
            else:
                cur=con.execute("""INSERT INTO employees(personnel_no,last_name,first_name,middle_name,position,employment_date,notes,active,driver_id,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?)""",(vals["personnel_no"],vals["last_name"],vals["first_name"],vals["middle_name"],"Водій",vals["employment_date"],vals["notes"],int(active.get()),saved_driver_id,datetime.now().isoformat(timespec="seconds")))
                employee_id=cur.lastrowid
            if active.get():
                con.execute("INSERT OR IGNORE INTO employee_roles(employee_id,role) VALUES(?,?)",(employee_id,"Водій"))
                con.execute("UPDATE drivers SET driver_end_date='' WHERE id=?",(saved_driver_id,))
            else:
                con.execute("DELETE FROM employee_roles WHERE employee_id=? AND role='Водій'",(employee_id,))
            con.commit(); con.close()
            self.load_drivers(); self.load_employee_registry(); win.destroy()

        ttk.Button(outer,text="Зберегти",command=save).pack(anchor="e",padx=8,pady=8)

    def new_driver(self): self.driver_form()
    def edit_driver(self):
        d=self.selected_driver()
        if d: self.driver_form(d)
    def delete_driver(self):
        d=self.selected_driver()
        if not d: return
        if not messagebox.askyesno("Завершити роль водія","Зняти роль «Водій»? Працівник залишиться в реєстрі, а історія графіка, табеля та шляхівок не видалиться."): return
        raw_end=simpledialog.askstring("Дата завершення ролі","Дата завершення роботи водієм (ДД.ММ.РРРР):",initialvalue=date.today().strftime("%d.%m.%Y"),parent=self)
        if raw_end is None: return
        try: end_date=datetime.strptime(raw_end.strip(),"%d.%m.%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Роль водія","Дата має бути у форматі ДД.ММ.РРРР.",parent=self); return
        con=db()
        employee=con.execute("SELECT id FROM employees WHERE driver_id=?",(d["id"],)).fetchone()
        if employee: finish_driver_role(con,employee["id"],d["id"],end_date)
        else: con.execute("UPDATE drivers SET active=0,driver_end_date=? WHERE id=?",(end_date,d["id"]))
        con.commit(); con.close(); self.load_drivers(); self.load_employee_registry()
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
            if hasattr(self,"work_driver_cb"):
                # Список табеля залежить від вибраного місяця: водій до дати
                # прийняття не може бути примусово підставлений з каталогу.
                self.refresh_work_driver_choices()
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

        try:
            period_end=month_dates(int(self.year_var.get()),int(self.month_var.get()))[-1]
        except Exception:
            period_end=date.today()
        rows=[d for d in rows if driver_employed_on(d,period_end)]

        available_ids={d["id"] for d in rows}
        if self.driver_id not in available_ids:
            self.driver_id=None
            self.work_driver_var.set("")

        self.work_driver_map={}
        values=[]
        name_counts={}
        for d in rows:
            base=self.driver_full_name(d)
            name_counts[base]=name_counts.get(base,0)+1

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

    def refresh_work_period(self):
        """Оновлює список водіїв і табель після зміни місяця або року."""
        self.refresh_work_driver_choices()
        self.refresh_month()

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

    def show_waybill_number_pools(self):
        if hasattr(self,"pool_win") and self.pool_win.winfo_exists():
            self.pool_win.lift(); self.load_waybill_number_pools(); return
        win=tk.Toplevel(self); self.pool_win=win; win.title("Пули серій і номерів шляхівок")
        fit_window_to_screen(win,1050,590,800,460)
        top=ttk.Frame(win,padding=8); top.pack(fill="x")
        ttk.Button(top,text="Новий пул",command=self.waybill_number_pool_form).pack(side="left",padx=3)
        ttk.Button(top,text="Редагувати",command=self.edit_waybill_number_pool).pack(side="left",padx=3)
        ttk.Button(top,text="Закрити / активувати",command=self.toggle_waybill_number_pool).pack(side="left",padx=3)
        ttk.Label(win,text="Taxo вибирає пул за датою роботи. Для готових пронумерованих бланків використовуйте ручний режим.",foreground="gray",wraplength=990,justify="left").pack(fill="x",padx=10,pady=(0,6))
        frame=ttk.Frame(win); frame.pack(fill="both",expand=True,padx=10,pady=6); frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
        cols=("id","series","range","next","dates","mode","status","notes")
        self.pool_tree=ttk.Treeview(frame,columns=cols,show="headings")
        for key,label,width in (("id","ID",45),("series","Серія",85),("range","Діапазон",150),("next","Наступний",95),("dates","Діє за датою роботи",185),("mode","Режим",100),("status","Стан",85),("notes","Примітка",250)):
            self.pool_tree.heading(key,text=label); self.pool_tree.column(key,width=width,anchor="w")
        y=ttk.Scrollbar(frame,orient="vertical",command=self.pool_tree.yview); x=ttk.Scrollbar(frame,orient="horizontal",command=self.pool_tree.xview); self.pool_tree.configure(yscrollcommand=y.set,xscrollcommand=x.set)
        self.pool_tree.grid(row=0,column=0,sticky="nsew"); y.grid(row=0,column=1,sticky="ns"); x.grid(row=1,column=0,sticky="ew")
        self.pool_tree.bind("<Double-1>",lambda _e:self.edit_waybill_number_pool())
        self.load_waybill_number_pools()

    def load_waybill_number_pools(self):
        if not hasattr(self,"pool_tree") or not self.pool_tree.winfo_exists(): return
        for item in self.pool_tree.get_children(): self.pool_tree.delete(item)
        con=db(); rows=con.execute("SELECT * FROM waybill_number_pools ORDER BY valid_from DESC,id DESC").fetchall(); con.close()
        for row in rows:
            width=int(row["number_width"] or 6); rng=f"{row['start_number']:0{width}d}–{row['end_number']:0{width}d}"
            dates=f"{fmt_date(row['valid_from'])} – {fmt_date(row['valid_until']) or 'без обмеження'}"
            self.pool_tree.insert("","end",values=(row["id"],row["series"],rng,f"{row['next_number']:0{width}d}",dates,"Авто" if row["mode"]=="auto" else "Ручний","Активний" if row["status"]=="active" else "Закритий",row["notes"]))

    def selected_waybill_number_pool(self):
        sel=getattr(self,"pool_tree",None).selection() if hasattr(self,"pool_tree") else ()
        if not sel: return None
        pid=int(self.pool_tree.item(sel[0],"values")[0]); con=db(); row=con.execute("SELECT * FROM waybill_number_pools WHERE id=?",(pid,)).fetchone(); con.close(); return row

    def waybill_number_pool_form(self, pool=None):
        parent=getattr(self,"pool_win",self); win=tk.Toplevel(parent); win.title("Пул номерів шляхівок")
        fit_window_to_screen(win,650,560,570,480); win.transient(parent); win.grab_set()
        defaults={"series":pool["series"] if pool else "","start":pool["start_number"] if pool else 1,"end":pool["end_number"] if pool else 999999,"next":pool["next_number"] if pool else 1,"width":pool["number_width"] if pool else 6,"from":fmt_date(pool["valid_from"]) if pool else date.today().strftime("%d.%m.%Y"),"until":fmt_date(pool["valid_until"]) if pool else "","mode":"Автоматичний" if not pool or pool["mode"]=="auto" else "Готові бланки / ручний номер","notes":pool["notes"] if pool else ""}
        vars_={k:tk.StringVar(value=str(v or "")) for k,v in defaults.items()}
        fields=(("series","Серія"),("start","Початковий номер"),("end","Кінцевий номер"),("next","Наступний номер"),("width","Кількість цифр"),("from","Діє з дати роботи"),("until","Діє до (необов'язково)"),("mode","Режим"),("notes","Примітка"))
        for i,(key,label) in enumerate(fields):
            ttk.Label(win,text=label).grid(row=i,column=0,sticky="w",padx=10,pady=6)
            widget=ttk.Combobox(win,textvariable=vars_[key],values=("Автоматичний","Готові бланки / ручний номер"),state="readonly",width=38) if key=="mode" else ttk.Entry(win,textvariable=vars_[key],width=42)
            widget.grid(row=i,column=1,sticky="ew",padx=10,pady=6)
            if key in {"from","until"}: calendar_button(win,vars_[key]).grid(row=i,column=2,sticky="w",padx=(0,8))
        win.columnconfigure(1,weight=1)
        def save():
            try:
                start=int(vars_["start"].get()); end=int(vars_["end"].get()); nxt=int(vars_["next"].get()); width=int(vars_["width"].get())
                valid_from=datetime.strptime(vars_["from"].get().strip(),"%d.%m.%Y").strftime("%Y-%m-%d")
                valid_until=datetime.strptime(vars_["until"].get().strip(),"%d.%m.%Y").strftime("%Y-%m-%d") if vars_["until"].get().strip() else ""
            except Exception:
                messagebox.showerror("Пул номерів","Перевірте числа і дати у форматі ДД.ММ.РРРР.",parent=win); return
            series=vars_["series"].get().strip()
            if not series or start<0 or end<start or not start<=nxt<=end+1 or not 1<=width<=12 or (valid_until and valid_until<valid_from):
                messagebox.showerror("Пул номерів","Некоректний діапазон, наступний номер, ширина або період дії.",parent=win); return
            mode="auto" if vars_["mode"].get()=="Автоматичний" else "manual"
            con=db()
            overlap=con.execute("""SELECT id FROM waybill_number_pools WHERE status='active' AND id<>?
                AND valid_from<=COALESCE(NULLIF(?,''),'9999-12-31') AND COALESCE(NULLIF(valid_until,''),'9999-12-31')>=? LIMIT 1""",(pool["id"] if pool else -1,valid_until,valid_from)).fetchone()
            if overlap:
                con.close(); messagebox.showerror("Пул номерів","У ці дати вже діє інший активний пул. Періоди активних пулів не можуть перетинатися.",parent=win); return
            vals=(series,start,end,nxt,width,valid_from,valid_until,mode,vars_["notes"].get().strip())
            if pool: con.execute("UPDATE waybill_number_pools SET series=?,start_number=?,end_number=?,next_number=?,number_width=?,valid_from=?,valid_until=?,mode=?,notes=? WHERE id=?",vals+(pool["id"],))
            else: con.execute("INSERT INTO waybill_number_pools(series,start_number,end_number,next_number,number_width,valid_from,valid_until,mode,status,notes,created_at) VALUES(?,?,?,?,?,?,?,?, 'active',?,?)",vals+(datetime.now().isoformat(timespec="seconds"),))
            con.commit(); con.close(); self.load_waybill_number_pools(); win.destroy()
        ttk.Button(win,text="Зберегти",command=save).grid(row=len(fields),column=1,sticky="e",padx=10,pady=12)

    def edit_waybill_number_pool(self):
        row=self.selected_waybill_number_pool()
        if row: self.waybill_number_pool_form(row)

    def toggle_waybill_number_pool(self):
        row=self.selected_waybill_number_pool()
        if not row: return
        status="closed" if row["status"]=="active" else "active"
        con=db()
        if status=="active":
            overlap=con.execute("""SELECT id FROM waybill_number_pools WHERE status='active' AND id<>?
                AND valid_from<=COALESCE(NULLIF(?,''),'9999-12-31') AND COALESCE(NULLIF(valid_until,''),'9999-12-31')>=? LIMIT 1""",
                (row["id"],row["valid_until"],row["valid_from"])).fetchone()
            if overlap:
                con.close(); messagebox.showerror("Пул номерів","Період перетинається з іншим активним пулом. Спочатку закрийте або змініть його.",parent=self.pool_win); return
        con.execute("UPDATE waybill_number_pools SET status=? WHERE id=?",(status,row["id"])); con.commit(); con.close(); self.load_waybill_number_pools()

    def load_company(self):
        con=db(); r=con.execute("SELECT * FROM company WHERE id=1").fetchone(); con.close()
        if r:
            for k in self.company_vars:
                self.company_vars[k].set(r[k] or "")
            for k in getattr(self,"company_en_vars",{}):
                self.company_en_vars[k].set(r[k] or "")
            for k in getattr(self,"company_waybill_vars",{}):
                self.company_waybill_vars[k].set(r[k] or ("АААТ" if k=="waybill_series" else ""))
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
        wb={k:v.get().strip() for k,v in getattr(self,"company_waybill_vars",{}).items()}
        con=db()
        try:
            con.execute(
                """UPDATE company SET
                       name=?,address=?,phone=?,fax=?,email=?,signer_name=?,signer_position=?,
                       name_en=?,address_en=?,signer_name_en=?,signer_position_en=?,place_en=?,
                       waybill_series=?,transport_column=?,brigade=?
                   WHERE id=1""",
                (
                    ua.get("name",""),ua.get("address",""),ua.get("phone",""),ua.get("fax",""),
                    ua.get("email",""),ua.get("signer_name",""),ua.get("signer_position",""),
                    en.get("name_en",""),en.get("address_en",""),en.get("signer_name_en",""),
                    en.get("signer_position_en",""),en.get("place_en",""),wb.get("waybill_series","АААТ"),
                    wb.get("transport_column",""),wb.get("brigade","")
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
        cols=("id","name","plate","garage","make","year","active","notes")
        self.vehicle_tree=ttk.Treeview(self.tab_vehicles,columns=cols,show="headings",height=25)
        heads={"id":"ID","name":"Назва","plate":"Держ. №","garage":"Гар. №","make":"Марка / модель","year":"Рік","active":"Статус","notes":"Примітка"}
        widths={"id":45,"name":165,"plate":110,"garage":85,"make":170,"year":65,"active":75,"notes":280}
        for c in cols:
            self.vehicle_tree.heading(c,text=heads[c]); self.vehicle_tree.column(c,width=widths[c],anchor="w")
        vehicle_y=ttk.Scrollbar(self.tab_vehicles,orient="vertical",command=self.vehicle_tree.yview)
        vehicle_x=ttk.Scrollbar(self.tab_vehicles,orient="horizontal",command=self.vehicle_tree.xview)
        self.vehicle_tree.configure(yscrollcommand=vehicle_y.set,xscrollcommand=vehicle_x.set)
        vehicle_x.pack(side="bottom",fill="x",padx=10,pady=(0,5))
        vehicle_y.pack(side="right",fill="y",pady=5)
        self.vehicle_tree.pack(side="left",fill="both",expand=True,padx=(10,0),pady=5)
        self.vehicle_tree.bind("<Double-1>",lambda _event:self.edit_vehicle())
        self.vehicle_tree.bind("<Return>",lambda _event:self.edit_vehicle())
        self.load_vehicles()

    def load_vehicles(self):
        if not hasattr(self,"vehicle_tree"): return
        for x in self.vehicle_tree.get_children(): self.vehicle_tree.delete(x)
        con=db(); rows=con.execute("SELECT * FROM vehicles ORDER BY active DESC, name, plate").fetchall(); con.close()
        for r in rows:
            self.vehicle_tree.insert("","end",values=(r["id"],r["name"],r["plate"],r["garage_no"],r["make_model"],r["year"] or "","Так" if r["active"] else "Ні",r["notes"]))

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
        win=tk.Toplevel(self); win.title("Автомобіль"); fit_window_to_screen(win,620,430,520,360); win.transient(self); win.grab_set()
        fields=[("name","Назва / інвентарний номер"),("plate","Державний номер"),("garage_no","Гаражний номер"),("make_model","Марка / модель"),("year","Рік"),("notes","Примітка")]
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
            vals=(name,vv["plate"].get().strip(),vv["garage_no"].get().strip(),vv["make_model"].get().strip(),year,vv["notes"].get().strip(),int(active.get()))
            if vehicle:
                con.execute("UPDATE vehicles SET name=?,plate=?,garage_no=?,make_model=?,year=?,notes=?,active=? WHERE id=?",(*vals,vehicle["id"]))
            else:
                con.execute("INSERT INTO vehicles(name,plate,garage_no,make_model,year,notes,active,created_at) VALUES(?,?,?,?,?,?,?,?)",(*vals,datetime.now().isoformat(timespec="seconds")))
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
        controls=ttk.Frame(self.tab_work)
        controls.pack(fill="x",padx=10,pady=(8,3))
        select_bar=ttk.Frame(controls)
        select_bar.pack(fill="x")
        self.work_driver_var=tk.StringVar(value="")
        self.work_driver_map={}
        ttk.Label(select_bar,text="Водій:").pack(side="left")
        self.work_driver_cb=ttk.Combobox(
            select_bar,
            textvariable=self.work_driver_var,
            state="readonly",
            width=34
        )
        self.work_driver_cb.pack(side="left",padx=5)
        self.work_driver_cb.bind("<<ComboboxSelected>>", self.on_work_driver_change)
        self.year_var=tk.IntVar(value=date.today().year)
        self.month_var=tk.IntVar(value=date.today().month)
        ttk.Label(select_bar,text="Рік:").pack(side="left",padx=(8,2))
        ttk.Spinbox(select_bar,from_=2020,to=2100,textvariable=self.year_var,width=7,command=self.refresh_work_period).pack(side="left",padx=(0,4))
        ttk.Label(select_bar,text="Місяць:").pack(side="left",padx=(8,2))
        ttk.Spinbox(select_bar,from_=1,to=12,textvariable=self.month_var,width=4,command=self.refresh_work_period).pack(side="left",padx=(0,8))
        ttk.Button(select_bar,text="Оновити",command=self.refresh_work_period).pack(side="left",padx=4)

        edit_bar=ttk.Frame(controls)
        edit_bar.pack(fill="x",pady=(5,0))
        ttk.Button(edit_bar,text="Новий / редагувати день",command=self.save_work_row).pack(side="left",padx=(0,5))
        ttk.Button(edit_bar,text="Копіювати день",command=self.copy_work_day).pack(side="left",padx=5)
        ttk.Button(edit_bar,text="Вставити день",command=self.paste_work_day).pack(side="left",padx=5)

        report_bar=ttk.Frame(controls)
        report_bar.pack(fill="x",pady=(5,0))
        ttk.Label(report_bar,text="Звіти:").pack(side="left",padx=(0,3))
        ttk.Button(report_bar,text="Excel",command=lambda:self.export_current("xlsx")).pack(side="left",padx=4)
        ttk.Button(report_bar,text="PDF",command=lambda:self.export_current("pdf")).pack(side="left",padx=4)
        ttk.Button(report_bar,text="Підсумки / контроль",command=self.show_work_analysis).pack(side="left",padx=4)
        ttk.Button(
            report_bar,text="Місячний табель / баланс",
            command=self.show_monthly_work_balance
        ).pack(side="left",padx=4)
        ttk.Button(
            report_bar,
            text="⚠ Без тахо — робочі дні 8 год",
            command=self.autofill
        ).pack(side="right",padx=(18,0))
        ttk.Label(
            self.tab_work,
            text=(
                "«Частини зміни» в програмі — наш технічний поділ дня: для кожної частини задаємо "
                "окремо ПЛАНОВИЙ час керування і ПЛАНОВИЙ робочий час. На старті v8.65 "
                "робочий час дорівнює керуванню; далі його можна збільшити/уточнити окремо. "
                "Проміжки між частинами використовуються для контролю перерв у керуванні 4:30 → 45 хв або 15+30."
            ),
            foreground="gray",wraplength=1080,justify="left"
        ).pack(anchor="w",padx=12,pady=(2,0))
        cols=("id","date","weekday","type","schedule","breaks","work","drive","over","route","vehicle","notes","mode")
        self.work_tree=ttk.Treeview(self.tab_work,columns=cols,show="headings",height=24,selectmode="extended")
        heads={"id":"ID","date":"Дата","weekday":"День","type":"Вид","schedule":"Графік","breaks":"Перерви","work":"Робота (план)","drive":"Керування (план)","over":"Надуроч.","route":"Маршрут","vehicle":"Авто","notes":"Примітка","mode":"Режим"}
        widths={"id":40,"date":85,"weekday":55,"type":120,"schedule":170,"breaks":90,"work":105,"drive":125,"over":75,"route":150,"vehicle":100,"notes":180,"mode":190}
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
        if sys.platform=="darwin":
            self.work_tree.bind("<Command-c>",lambda e:self.copy_work_day())
            self.work_tree.bind("<Command-v>",lambda e:self.paste_work_day())
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
        fit_window_to_screen(win,1450,760,900,500)

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
        actual=write_output_file(
            lambda out: export_monthly_work_balance_pdf(
                y,m,out,active_only=bool(self.monthly_balance_active_only.get())
            ),
            path,
            parent=self.monthly_balance_win,
            kind="PDF місячного табеля",
            error_title="Помилка PDF"
        )
        if actual is None:
            return
        self.monthly_balance_last_pdf=actual
        messagebox.showinfo(
            "Місячний табель",
            f"PDF створено:\n{actual}",
            parent=self.monthly_balance_win
        )

    def open_monthly_work_balance_pdf(self):
        path=getattr(self,"monthly_balance_last_pdf",None)
        if not path or not Path(path).exists():
            y=int(self.monthly_balance_year.get())
            m=int(self.monthly_balance_month.get())
            path=OUTPUT_DIR/f"Табель_робочого_часу_{y}_{m:02d}.pdf"
            actual=write_output_file(
                lambda out: export_monthly_work_balance_pdf(
                    y,m,out,active_only=bool(self.monthly_balance_active_only.get())
                ),
                path,
                parent=self.monthly_balance_win,
                kind="PDF місячного табеля",
                error_title="Помилка PDF"
            )
            if actual is None:
                return
            path=actual
            self.monthly_balance_last_pdf=actual
        try:
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
        actual=write_output_file(
            lambda out: export_monthly_work_balance_xlsx(
                y,m,out,active_only=bool(self.monthly_balance_active_only.get())
            ),
            path,
            parent=self.monthly_balance_win,
            kind="Excel-файл місячного табеля",
            error_title="Помилка Excel"
        )
        if actual is None:
            return
        self.monthly_balance_last_xlsx=actual
        try:
            open_external(actual)
        except Exception as exc:
            messagebox.showwarning(
                "Файл створено",
                f"Excel-файл створено, але не вдалося відкрити його автоматично:\n{actual}\n\n{exc}",
                parent=self.monthly_balance_win
            )

    def build_schedule(self):
        """Графічний планувальник одного календарного дня по всіх активних водіях."""
        top=ttk.Frame(self.tab_schedule); top.pack(fill="x",padx=10,pady=(8,3))
        nav=ttk.Frame(top); nav.pack(fill="x")
        self.schedule_date_var=tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
        ttk.Label(nav,text="Дата:").pack(side="left")
        ttk.Entry(nav,textvariable=self.schedule_date_var,width=13).pack(side="left",padx=5)
        calendar_button(nav,self.schedule_date_var).pack(side="left",padx=2)
        ttk.Button(nav,text="◀ День",command=lambda:self.shift_schedule_day(-1)).pack(side="left",padx=3)
        ttk.Button(nav,text="Сьогодні",command=self.schedule_today).pack(side="left",padx=3)
        ttk.Button(nav,text="День ▶",command=lambda:self.shift_schedule_day(1)).pack(side="left",padx=3)
        ttk.Button(nav,text="Оновити",command=self.refresh_schedule).pack(side="left",padx=5)

        actions=ttk.Frame(top); actions.pack(fill="x",pady=(5,0))
        ttk.Button(actions,text="Додати / редагувати період",command=self.schedule_add_period).pack(side="left")
        ttk.Button(
            actions,
            text="Місячний графік змінності",
            command=self.show_monthly_shift_schedule
        ).pack(side="left",padx=5)
        ttk.Button(
            actions,
            text="Аудит графіків…",
            command=self.show_schedule_integrity_audit
        ).pack(side="left",padx=5)
        self.schedule_audit_day_status=tk.StringVar(value="Аудит дня: …")
        self.schedule_audit_day_status_label=ttk.Label(
            actions,textvariable=self.schedule_audit_day_status,
            foreground="#555555"
        )
        self.schedule_audit_day_status_label.pack(side="left",padx=(4,10))
        ttk.Button(
            actions,
            text="Шляхівки на день",
            command=self.show_waybills_for_schedule
        ).pack(side="left",padx=5)
        ttk.Label(
            self.tab_schedule,
            text="План дня по всіх активних водіях. Подвійний клік по смузі або рядку відкриває день для редагування.",
            foreground="gray",wraplength=1080,justify="left"
        ).pack(anchor="w",padx=12)

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
        def schedule_wheel(event):
            delta=getattr(event,"delta",0)
            if delta:
                self.schedule_canvas.yview_scroll(int(-delta/120) or (-1 if delta>0 else 1),"units")
            elif getattr(event,"num",None) in (4,5):
                self.schedule_canvas.yview_scroll(-1 if event.num==4 else 1,"units")
            return "break"
        def schedule_shift_wheel(event):
            delta=getattr(event,"delta",0)
            if delta:
                self.schedule_canvas.xview_scroll(int(-delta/120) or (-1 if delta>0 else 1),"units")
            return "break"
        self.schedule_canvas.bind("<MouseWheel>",schedule_wheel,add="+")
        self.schedule_canvas.bind("<Shift-MouseWheel>",schedule_shift_wheel,add="+")
        self.schedule_canvas.bind("<Button-4>",schedule_wheel,add="+")
        self.schedule_canvas.bind("<Button-5>",schedule_wheel,add="+")
        self.schedule_hitboxes=[]
        self.schedule_driver_rows=[]
        self.after(100,self.refresh_schedule)

    def show_schedule_integrity_audit(self):
        """Open a visible, scoped audit of stored schedule input defects."""
        source_date=self._monthly_shift_source_date()
        if hasattr(self,"schedule_audit_win") and self.schedule_audit_win.winfo_exists():
            self.schedule_audit_win.deiconify()
            self.schedule_audit_win.lift()
            self.schedule_audit_win.after_idle(self.schedule_audit_win.focus_force)
            self.refresh_schedule_integrity_audit()
            return

        win=tk.Toplevel(self)
        self.schedule_audit_win=win
        win.title("Аудит графіків — перевірка помилок введення")
        fit_window_to_screen(win,1320,720,900,520)
        win.transient(self)
        win.lift()
        win.after_idle(win.focus_force)

        top=ttk.Frame(win,padding=8)
        top.pack(fill="x")
        self.schedule_audit_scope=tk.StringVar(value="Поточний день")
        self.schedule_audit_all_routes=tk.BooleanVar(value=False)
        self.schedule_audit_period=tk.StringVar(value=source_date.strftime("%d.%m.%Y"))
        self.schedule_audit_summary=tk.StringVar(value="Перевірка…")
        self.schedule_audit_result=tk.StringVar(value="")

        ttk.Label(top,text="Перевірити:",font=("TkDefaultFont",9,"bold")).pack(side="left")
        scope=ttk.Combobox(
            top,textvariable=self.schedule_audit_scope,state="readonly",width=22,
            values=("Поточний день","Весь місяць","Шаблони маршрутів","Місяць + маршрути")
        )
        scope.pack(side="left",padx=(5,12))
        scope.bind("<<ComboboxSelected>>",lambda _e:self._schedule_audit_scope_changed())
        ttk.Label(top,text="Період:").pack(side="left")
        ttk.Label(top,textvariable=self.schedule_audit_period,font=("TkDefaultFont",9,"bold")).pack(side="left",padx=(4,12))
        self.schedule_audit_all_routes_cb=ttk.Checkbutton(
            top,text="включити неактивні маршрути",
            variable=self.schedule_audit_all_routes,
            command=self.refresh_schedule_integrity_audit
        )
        self.schedule_audit_all_routes_cb.pack(side="left",padx=(0,8))
        ttk.Button(top,text="Перевірити зараз",command=self.refresh_schedule_integrity_audit).pack(side="left",padx=3)

        actions=ttk.Frame(win,padding=(8,0,8,5))
        actions.pack(fill="x")
        ttk.Button(actions,text="Відкрити запис",command=self.open_schedule_audit_finding).pack(side="left",padx=(0,5))
        ttk.Button(actions,text="Контроль №340 для вибраного дня",command=self.open_schedule_audit_regulatory).pack(side="left",padx=5)
        ttk.Label(
            actions,
            text="Це аудит помилок введення. Норми Положення №340 перевіряються окремим контролем.",
            foreground="#555555"
        ).pack(side="left",padx=(15,0))

        result_bar=ttk.Frame(win,padding=(10,2,10,5))
        result_bar.pack(fill="x")
        self.schedule_audit_result_label=ttk.Label(
            result_bar,textvariable=self.schedule_audit_result,
            font=("TkDefaultFont",10,"bold")
        )
        self.schedule_audit_result_label.pack(anchor="w")
        ttk.Label(result_bar,textvariable=self.schedule_audit_summary,foreground="#444444").pack(anchor="w",pady=(2,0))

        notebook=ttk.Notebook(win)
        notebook.pack(fill="both",expand=True,padx=10,pady=(0,10))

        problems=ttk.Frame(notebook)
        notebook.add(problems,text="Знайдені проблеми")
        problems.rowconfigure(0,weight=1); problems.columnconfigure(0,weight=1)
        cols=("source","date","subject","route","type","duration","detail")
        tree=ttk.Treeview(problems,columns=cols,show="headings",selectmode="browse")
        self.schedule_audit_tree=tree
        heads={
            "source":"Джерело","date":"Дата","subject":"Водій / маршрут",
            "route":"Маршрут","type":"Проблема","duration":"Тривалість","detail":"Деталі"
        }
        widths={
            "source":115,"date":95,"subject":220,"route":190,
            "type":155,"duration":85,"detail":500
        }
        for key in cols:
            tree.heading(key,text=heads[key])
            tree.column(key,width=widths[key],anchor="w",stretch=(key in {"subject","route","detail"}))
        tree.tag_configure("problem",foreground="#8A1C1C")
        ybar=ttk.Scrollbar(problems,orient="vertical",command=tree.yview)
        xbar=ttk.Scrollbar(problems,orient="horizontal",command=tree.xview)
        tree.configure(yscrollcommand=ybar.set,xscrollcommand=xbar.set)
        tree.grid(row=0,column=0,sticky="nsew")
        ybar.grid(row=0,column=1,sticky="ns")
        xbar.grid(row=1,column=0,sticky="ew")
        tree.bind("<Double-1>",lambda _e:self.open_schedule_audit_finding())

        info_tab=ttk.Frame(notebook)
        notebook.add(info_tab,text="Що саме перевірено")
        info_frame=ttk.Frame(info_tab)
        info_frame.pack(fill="both",expand=True,padx=8,pady=8)
        info_frame.rowconfigure(0,weight=1); info_frame.columnconfigure(0,weight=1)
        info=tk.Text(info_frame,wrap="word",padx=10,pady=10,height=16)
        self.schedule_audit_info_text=info
        info_scroll=ttk.Scrollbar(info_frame,orient="vertical",command=info.yview)
        info.configure(yscrollcommand=info_scroll.set)
        info.grid(row=0,column=0,sticky="nsew")
        info_scroll.grid(row=0,column=1,sticky="ns")

        self.schedule_audit_rows={}
        self._schedule_audit_scope_changed()
        def refocus_refresh(event):
            if event.widget is win:
                win.after_idle(self.refresh_schedule_integrity_audit)
        win.bind("<FocusIn>",refocus_refresh,add="+")

    def _schedule_audit_scope_changed(self):
        """Keep route-only controls relevant to the selected audit scope."""
        if hasattr(self,"schedule_audit_all_routes_cb"):
            scope=(self.schedule_audit_scope.get().strip()
                   if hasattr(self,"schedule_audit_scope") else "Поточний день")
            includes_routes=scope in ("Шаблони маршрутів","Активні маршрути","Місяць + маршрути")
            self.schedule_audit_all_routes_cb.configure(
                state="normal" if includes_routes else "disabled"
            )
        self.refresh_schedule_integrity_audit()

    def _schedule_audit_scope_args(self):
        source_date=self._monthly_shift_source_date()
        scope=(self.schedule_audit_scope.get().strip() if hasattr(self,"schedule_audit_scope") else "Поточний день")
        include_days=scope in ("Поточний день","Весь місяць","Місяць + маршрути")
        include_routes=scope in ("Шаблони маршрутів","Активні маршрути","Місяць + маршрути")
        one_day=source_date if scope=="Поточний день" else None
        return source_date,scope,include_days,include_routes,one_day

    def refresh_schedule_integrity_audit(self):
        if not hasattr(self,"schedule_audit_tree") or not self.schedule_audit_tree.winfo_exists():
            return
        source_date,scope,include_days,include_routes,one_day=self._schedule_audit_scope_args()
        active_routes_only=not bool(self.schedule_audit_all_routes.get())
        data=collect_schedule_integrity_audit(
            source_date.year,source_date.month,
            active_routes_only=active_routes_only,
            work_date=one_day,
            include_days=include_days,
            include_routes=include_routes,
        )

        if scope=="Поточний день":
            period_text=source_date.strftime("%d.%m.%Y")
        elif scope in ("Шаблони маршрутів","Активні маршрути"):
            period_text="шаблони маршрутів"
        else:
            period_text=f"{month_name_ua(source_date.month)} {source_date.year}"
        self.schedule_audit_period.set(period_text)

        tree=self.schedule_audit_tree
        for item in tree.get_children():
            tree.delete(item)
        self.schedule_audit_rows={}
        day_problem_ids=set()
        route_problem_ids=set()
        for finding in data["findings"]:
            if finding["source_kind"]=="worklog":
                day_problem_ids.add(finding["worklog_id"])
            elif finding["source_kind"]=="route":
                route_problem_ids.add(finding["route_id"])
            iid=tree.insert("","end",values=(
                finding["source"],
                (datetime.strptime(finding["date"],"%Y-%m-%d").strftime("%d.%m.%Y")
                 if finding["date"] else "—"),
                finding["subject"],
                finding["route"] or "—",
                finding["label"],
                minutes_hhmm(finding["minutes"]) if finding["minutes"] else "—",
                finding["message"],
            ),tags=("problem",))
            self.schedule_audit_rows[iid]=finding

        if data["findings"]:
            self.schedule_audit_result.set(f"⚠ Знайдено проблем: {len(data['findings'])}")
            self.schedule_audit_result_label.configure(foreground="#8A1C1C")
            self.schedule_audit_summary.set(
                f"Днів із проблемами: {len(day_problem_ids)}; шаблонів маршрутів із проблемами: {len(route_problem_ids)}. "
                "Подвійний клік відкриває запис для ручного виправлення."
            )
        else:
            inspected_total=(data["inspected_day_records"]+data["inspected_route_records"])
            if inspected_total==0:
                self.schedule_audit_result.set("○ Немає записів у вибраній області")
                self.schedule_audit_result_label.configure(foreground="#555555")
            else:
                self.schedule_audit_result.set("✓ Помилок введення не знайдено")
                self.schedule_audit_result_label.configure(foreground="#1B5E20")
            self.schedule_audit_summary.set(
                f"Перевірено записів днів: {data['inspected_day_records']} "
                f"(з точним часом: {data['exact_day_records']}); "
                f"шаблонів маршрутів: {data['inspected_route_records']}."
            )

        info=self.schedule_audit_info_text
        info.configure(state="normal")
        info.delete("1.0","end")
        info_lines=[
            "ЩО ПЕРЕВІРЯЄ ЦЕЙ АУДИТ\n",
            "• перекриття частин робочого часу;\n",
            "• перекриття інтервалів керування;\n",
            "• неповні пари часу «від–до»;\n",
            "• керування, яке виходить за межі робочого інтервалу;\n",
            "• порожні часові частини;\n",
            "• активні маршрути без часового сценарію;\n",
            "• старі записи без work_segments, якщо в них збережено точні години.\n\n",
            "ЩО ЦЕЙ АУДИТ НЕ ЗАМІНЮЄ\n",
            "Контроль Положення №340: 4:30 без належної перерви, добове/тижневе керування, "
            "міжзмінний і щотижневий відпочинок та інші нормативні обмеження перевіряються "
            "окремим вікном «Підсумки та контроль №340».\n\n",
            "ПОЛІТИКА ВИПРАВЛЕННЯ\n",
            "Аудит нічого не переписує автоматично. Нові перекриття блокуються під час збереження; "
            "старі помилки показуються для ручного виправлення. Після закриття редактора список "
            "перевіряється повторно.\n\n",
            f"ПОТОЧНА ОБЛАСТЬ: {scope}.\n",
            f"Перевірено записів днів: {data['inspected_day_records']}; з точним часом: {data['exact_day_records']}; "
            f"legacy-точних записів: {data['legacy_exact_day_records']}; маршрутів: {data['inspected_route_records']}.\n",
        ]
        info.insert("end","".join(info_lines))
        info.configure(state="disabled")

    def refresh_schedule_audit_day_status(self, work_date=None):
        if not hasattr(self,"schedule_audit_day_status"):
            return
        d=work_date or self._schedule_parse_date()
        if not d:
            self.schedule_audit_day_status.set("Аудит дня: —")
            return
        try:
            data=collect_schedule_integrity_audit(
                d.year,d.month,work_date=d,include_days=True,include_routes=False
            )
            text=schedule_audit_day_status_text(data)
            self.schedule_audit_day_status.set(text)
            if hasattr(self,"schedule_audit_day_status_label"):
                color=("#8A1C1C" if text.startswith("⚠")
                       else "#1B5E20" if text.startswith("✓")
                       else "#555555")
                self.schedule_audit_day_status_label.configure(foreground=color)
        except Exception:
            self.schedule_audit_day_status.set("Аудит дня: помилка перевірки")
            if hasattr(self,"schedule_audit_day_status_label"):
                self.schedule_audit_day_status_label.configure(foreground="#8A1C1C")

    def _selected_schedule_audit_finding(self):
        tree=getattr(self,"schedule_audit_tree",None)
        if tree is None:
            return None
        sel=tree.selection()
        return self.schedule_audit_rows.get(sel[0]) if sel else None

    def open_schedule_audit_finding(self):
        finding=self._selected_schedule_audit_finding()
        if not finding:
            messagebox.showinfo(
                "Аудит графіків","Виберіть проблему у списку.",
                parent=getattr(self,"schedule_audit_win",self)
            )
            return
        if finding["source_kind"]=="worklog":
            try:
                work_date=datetime.strptime(finding["date"],"%Y-%m-%d").date()
            except Exception:
                return
            self.open_schedule_worklog(finding["driver_id"],work_date)
            return

        route_id=finding.get("route_id")
        if not route_id:
            return
        con=db()
        route=con.execute("SELECT * FROM routes WHERE id=?",(route_id,)).fetchone()
        segs=con.execute(
            "SELECT * FROM route_segments WHERE route_id=? ORDER BY segment_no",(route_id,)
        ).fetchall()
        stops=con.execute(
            "SELECT * FROM route_stops WHERE route_id=? ORDER BY direction,stop_no",(route_id,)
        ).fetchall()
        con.close()
        if route:
            self.route_catalog_form((route,segs,stops))
            self.load_route_catalog()

    def open_schedule_audit_regulatory(self):
        """Open №340 analysis only for an explicitly selected driver-day finding."""
        finding=self._selected_schedule_audit_finding()
        if not finding or finding.get("source_kind")!="worklog" or not finding.get("driver_id"):
            messagebox.showinfo(
                "Контроль №340",
                "Виберіть у списку проблему конкретного дня водія. "
                "Для загального контролю водія використовуйте «Підсумки / контроль» у вкладці «Табель».",
                parent=getattr(self,"schedule_audit_win",self)
            )
            return
        driver_id=finding["driver_id"]
        try:
            source_date=datetime.strptime(finding["date"],"%Y-%m-%d").date()
        except Exception:
            source_date=self._monthly_shift_source_date()
        self.driver_id=driver_id
        self.year_var.set(source_date.year)
        self.month_var.set(source_date.month)
        self.refresh_work_driver_choices()
        driver=self.driver_by_id(driver_id)
        if driver:
            label=next(
                (k for k,v in getattr(self,"work_driver_map",{}).items() if v==driver_id),
                self.driver_full_name(driver)
            )
            self.work_driver_var.set(label)
        self.refresh_month()
        self.show_work_analysis()


    def _monthly_shift_source_date(self):
        """Дата, від якої відкриваємо місячний графік змінності."""
        try:
            return datetime.strptime(self.schedule_date_var.get().strip(),"%d.%m.%Y").date()
        except Exception:
            return date.today()

    def _sync_monthly_shift_period_from_schedule(self):
        d=self._monthly_shift_source_date()
        if hasattr(self,"monthly_shift_year"):
            self.monthly_shift_year.set(d.year)
        if hasattr(self,"monthly_shift_month"):
            self.monthly_shift_month.set(d.month)
        if hasattr(self,"monthly_shift_pdf_dirty"):
            self.monthly_shift_pdf_dirty=True

    def show_monthly_shift_schedule(self):
        """Місячний графік змінності по всіх активних водіях."""
        if hasattr(self,"monthly_shift_win") and self.monthly_shift_win.winfo_exists():
            self._sync_monthly_shift_period_from_schedule()
            self.monthly_shift_win.lift()
            self.refresh_monthly_shift_schedule()
            return

        win=tk.Toplevel(self)
        self.monthly_shift_win=win
        win.title("Місячний графік змінності водіїв")
        fit_window_to_screen(win,1450,760,900,500)

        top=ttk.Frame(win,padding=8)
        top.pack(fill="x")
        filters=ttk.Frame(top)
        filters.pack(fill="x")
        exports=ttk.Frame(top)
        exports.pack(fill="x",pady=(6,0))

        source_date=self._monthly_shift_source_date()
        self.monthly_shift_year=tk.IntVar(value=source_date.year)
        self.monthly_shift_month=tk.IntVar(value=source_date.month)
        self.monthly_shift_active_only=tk.BooleanVar(value=True)
        self.monthly_shift_last_pdf=None
        self.monthly_shift_last_pdf_key=None
        self.monthly_shift_pdf_dirty=True
        self.monthly_shift_last_detail_pdf=None
        self.monthly_shift_last_xlsx=None

        ttk.Label(filters,text="Рік:").pack(side="left")
        ttk.Spinbox(
            filters,from_=2020,to=2100,textvariable=self.monthly_shift_year,width=7,
            command=self.refresh_monthly_shift_schedule
        ).pack(side="left",padx=(3,8))

        ttk.Label(filters,text="Місяць:").pack(side="left")
        ttk.Spinbox(
            filters,from_=1,to=12,textvariable=self.monthly_shift_month,width=4,
            command=self.refresh_monthly_shift_schedule
        ).pack(side="left",padx=(3,8))

        ttk.Checkbutton(
            filters,text="Тільки активні водії",
            variable=self.monthly_shift_active_only,
            command=self.refresh_monthly_shift_schedule
        ).pack(side="left",padx=(4,10))

        ttk.Button(
            filters,text="Оновити",command=self.refresh_monthly_shift_schedule
        ).pack(side="left",padx=3)

        ttk.Button(
            exports,text="Excel — редагувати",command=self.save_monthly_shift_schedule_xlsx
        ).pack(side="left",padx=(0,3))
        ttk.Button(
            exports,text="PDF — графік",command=self.save_monthly_shift_schedule_pdf
        ).pack(side="left",padx=3)
        ttk.Button(
            exports,text="Відкрити графік PDF",command=self.open_monthly_shift_schedule_pdf
        ).pack(side="left",padx=3)
        ttk.Button(
            exports,text="PDF — деталізація",command=self.save_monthly_shift_detail_pdf
        ).pack(side="left",padx=(10,3))
        ttk.Button(
            exports,text="Відкрити деталізацію",command=self.open_monthly_shift_detail_pdf
        ).pack(side="left",padx=3)

        ttk.Label(
            win,
            text=(
                "Місячна матриця формується з уже введених табелів. "
                "Графік розрахований на стандартний офісний папір A4, альбомна орієнтація. "
                "PDF графіка автоматично ділить місяць на три читабельні частини (для 31 дня: 1–11, 12–21, 22–31). "
                "«PDF — деталізація» формує окремий A4-документ з точними частинами змін, перервами, "
                "робочим часом, часом керування, маршрутом та автомобілем. "
                "«Відкрити деталізацію» формує актуальний PDF без діалогу збереження та одразу відкриває його. "
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
            f"Робота, план: {minutes_hhmm(total_work_min)}    "
            f"Керування, план: {minutes_hhmm(total_drive_min)}"
        )
        # Матриця могла змінитися після редагування табеля/графіка або просто
        # після натискання «Оновити». Старий PDF більше не вважаємо актуальним.
        if hasattr(self,"monthly_shift_pdf_dirty"):
            self.monthly_shift_pdf_dirty=True

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
        actual=write_output_file(
            lambda out: export_monthly_shift_schedule_xlsx(
                y,m,out,active_only=bool(self.monthly_shift_active_only.get())
            ),
            path,
            parent=self.monthly_shift_win,
            kind="Excel-файл графіка змінності",
            error_title="Помилка Excel"
        )
        if actual is None:
            return
        self.monthly_shift_last_xlsx=actual
        try:
            open_external(actual)
        except Exception as exc:
            messagebox.showwarning(
                "Файл створено",
                f"Excel-файл створено, але не вдалося відкрити його автоматично:\n{actual}\n\n{exc}",
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
        actual=write_output_file(
            lambda out: export_monthly_shift_detail_pdf(
                y,m,out,active_only=bool(self.monthly_shift_active_only.get())
            ),
            path,
            parent=self.monthly_shift_win,
            kind="PDF деталізації графіка змінності",
            error_title="Помилка PDF деталізації"
        )
        if actual is None:
            return
        self.monthly_shift_last_detail_pdf=actual
        messagebox.showinfo(
            "Деталізація графіка",
            f"PDF деталізації створено:\n{actual}",
            parent=self.monthly_shift_win
        )

    def _monthly_shift_default_detail_pdf(self):
        y=int(self.monthly_shift_year.get())
        m=int(self.monthly_shift_month.get())
        return OUTPUT_DIR / f"Деталізація_графіка_змінності_{y}_{m:02d}.pdf"

    def open_monthly_shift_detail_pdf(self):
        """Сформувати актуальну деталізацію місячного графіка і одразу відкрити PDF."""
        y=int(self.monthly_shift_year.get())
        m=int(self.monthly_shift_month.get())
        path=self._monthly_shift_default_detail_pdf()
        try:
            actual=write_output_file(
                lambda out: export_monthly_shift_detail_pdf(
                    y,m,out,active_only=bool(self.monthly_shift_active_only.get())
                ),
                path,
                parent=self.monthly_shift_win,
                kind="PDF деталізації графіка змінності",
                error_title="Помилка PDF деталізації"
            )
            if actual is None:
                return
            self.monthly_shift_last_detail_pdf=Path(actual)
            open_external(actual)
        except Exception as exc:
            messagebox.showerror(
                "Деталізація графіка",
                f"Не вдалося відкрити деталізацію:\n{exc}",
                parent=self.monthly_shift_win
            )

    def _monthly_shift_default_pdf(self):
        y=int(self.monthly_shift_year.get())
        m=int(self.monthly_shift_month.get())
        return OUTPUT_DIR / f"Графік_змінності_{y}_{m:02d}.pdf"

    def _monthly_shift_pdf_key(self):
        return (
            int(self.monthly_shift_year.get()),
            int(self.monthly_shift_month.get()),
            bool(self.monthly_shift_active_only.get()),
        )

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
        actual=write_output_file(
            lambda out: export_monthly_shift_schedule_pdf(
                y,m,out,active_only=bool(self.monthly_shift_active_only.get())
            ),
            path,
            parent=self.monthly_shift_win,
            kind="PDF графіка змінності",
            error_title="Помилка PDF"
        )
        if actual is None:
            return
        self.monthly_shift_last_pdf=Path(actual)
        self.monthly_shift_last_pdf_key=self._monthly_shift_pdf_key()
        self.monthly_shift_pdf_dirty=False
        messagebox.showinfo("Графік змінності",f"PDF створено:\n{actual}",parent=self.monthly_shift_win)

    def open_monthly_shift_schedule_pdf(self):
        y=int(self.monthly_shift_year.get())
        m=int(self.monthly_shift_month.get())
        key=self._monthly_shift_pdf_key()
        use_last=(
            self.monthly_shift_last_pdf is not None
            and self.monthly_shift_last_pdf_key==key
            and not self.monthly_shift_pdf_dirty
            and Path(self.monthly_shift_last_pdf).exists()
        )
        path=Path(self.monthly_shift_last_pdf) if use_last else self._monthly_shift_default_pdf()
        try:
            if not use_last:
                actual=write_output_file(
                    lambda out: export_monthly_shift_schedule_pdf(
                        y,m,out,active_only=bool(self.monthly_shift_active_only.get())
                    ),
                    path,
                    parent=self.monthly_shift_win,
                    kind="PDF графіка змінності",
                    error_title="Помилка PDF"
                )
                if actual is None:
                    return
                path=Path(actual)
                self.monthly_shift_last_pdf=path
                self.monthly_shift_last_pdf_key=key
                self.monthly_shift_pdf_dirty=False
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
        drivers=[dr for dr in drivers if driver_employed_on(dr,d)]
        rows=con.execute("SELECT * FROM worklog WHERE work_date=?",(d.isoformat(),)).fetchall()
        by_driver={r["driver_id"]:r for r in rows}
        seg_by={}
        if rows:
            ids=[r["id"] for r in rows]
            q=",".join("?" for _ in ids)
            segs=con.execute(f"SELECT * FROM work_segments WHERE worklog_id IN ({q}) ORDER BY worklog_id,segment_no",ids).fetchall()
            for seg in segs: seg_by.setdefault(seg["worklog_id"],[]).append(seg)

        absence_by_driver={}
        override_types=set(globals().get("TAXO_NONWORK_OVERRIDE_TYPES", set()) or ())
        if override_types and drivers:
            driver_ids=[dr["id"] for dr in drivers]
            q=",".join("?" for _ in driver_ids)
            params=[d.isoformat(),*driver_ids]
            for entry in con.execute(
                f"""SELECT e.driver_id,t.day_type
                    FROM employee_time_entries t
                    JOIN employees e ON e.id=t.employee_id
                    WHERE t.work_date=? AND e.driver_id IN ({q})
                    ORDER BY e.active DESC,e.id""",
                params
            ).fetchall():
                if (entry["driver_id"] is not None
                        and str(entry["day_type"] or "") in override_types
                        and entry["driver_id"] not in absence_by_driver):
                    absence_by_driver[entry["driver_id"]]=entry["day_type"]
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

            wl=by_driver.get(dr["id"])
            segs=seg_by.get(wl["id"],[]) if wl else []
            override=absence_by_driver.get(dr["id"])
            state=driver_day_view(
                d,wl,segs,
                day_type_override=override,
                suppress_plan=bool(override),
            )
            name_text=full
            if state["work_overlap_minutes"]>0:
                name_text += f"\n⚠ перекриття {minutes_hhmm(state['work_overlap_minutes'])}"
            c.create_text(
                12,y+row_h/2,text=name_text,anchor="w",
                font=("TkDefaultFont",8 if state["work_overlap_minutes"] else 9,"bold")
            )

            band_rows={
                "Робота":(y+6,y+25),
                "Керування":(y+29,y+48),
            }
            for group,a,b in state["bands"]:
                y1,y2=band_rows.get(group,(y+6,y+25))
                if not a or not b: continue
                try: sm=time_to_minutes(a); em=time_to_minutes(b)
                except Exception: continue
                if em<=sm: em+=1440
                for base_sm,base_em in ((sm,em),(sm-1440,em-1440)):
                    vis_s=max(0,base_sm); vis_e=min(1440,base_em)
                    if vis_e<=vis_s: continue
                    x1=left+vis_s/60*hour_w; x2=left+vis_e/60*hour_w
                    c.create_rectangle(x1,y1,x2,y2,fill=self._schedule_fill(group),outline="#777")
                    band_w=x2-x1
                    if band_w>=125:
                        label=f"{a}–{b} {group}"
                        font=("TkDefaultFont",8)
                    elif band_w>=72:
                        label=f"{a}–{b}"
                        font=("TkDefaultFont",8)
                    elif band_w>=38:
                        label="Роб." if group=="Робота" else ("Кер." if group=="Керування" else group[:4]+".")
                        font=("TkDefaultFont",8)
                    else:
                        label="Р" if group=="Робота" else ("К" if group=="Керування" else "•")
                        font=("TkDefaultFont",8,"bold")
                    c.create_text((x1+x2)/2,(y1+y2)/2,text=label,anchor="center",font=font)
                    self.schedule_hitboxes.append(
                        (x1,y1,x2,y2,dr["id"],d,None,wl["id"] if wl else None)
                    )

            if state["status_label"]:
                status=state["status_label"]
                c.create_text(
                    left+12,y+row_h/2,
                    text=status,anchor="w",
                    font=("TkDefaultFont",9,"bold" if override else "normal"),
                    fill="#666666",
                )

        c.create_line(0,top+len(drivers)*row_h,width,top+len(drivers)*row_h,fill="#999")
        self.refresh_schedule_audit_day_status(d)

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
        self.year_var.set(work_date.year); self.month_var.set(work_date.month)
        self.refresh_work_driver_choices()
        if not d or not bool(d["active"]) or not driver_employed_on(d,work_date):
            messagebox.showwarning(
                "Графік","Водій не був прийнятий як активний працівник на цю дату.",parent=self
            )
            self.refresh_month()
            return
        label=next((k for k,v in getattr(self,"work_driver_map",{}).items() if v==driver_id), self.driver_full_name(d))
        self.driver_id=driver_id
        self.work_driver_var.set(label)
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
            selected=self.driver_by_id(self.driver_id)
            if selected and bool(selected["active"]) and driver_employed_on(selected,d):
                self.open_schedule_worklog(self.driver_id,d)
                return
        con=db(); drivers=con.execute("SELECT * FROM drivers WHERE active=1 ORDER BY last_name,first_name").fetchall(); con.close()
        drivers=[dr for dr in drivers if driver_employed_on(dr,d)]
        if not drivers:
            messagebox.showwarning("Графік","На цю дату немає прийнятих активних водіїв.",parent=self); return
        win=tk.Toplevel(self); win.title("Вибір водія"); fit_window_to_screen(win,430,170,400,170); win.transient(self); win.grab_set()
        var=tk.StringVar(value=self.driver_full_name(drivers[0])); labels=[self.driver_full_name(x) for x in drivers]; mapping={self.driver_full_name(x):x["id"] for x in drivers}
        ttk.Label(win,text="Водій").pack(anchor="w",padx=12,pady=(15,5)); ttk.Combobox(win,textvariable=var,values=labels,state="readonly",width=42).pack(padx=12)
        def go():
            did=mapping.get(var.get()); win.destroy()
            if did: self.open_schedule_worklog(did,d)
        ttk.Button(win,text="Відкрити",command=go).pack(anchor="e",padx=12,pady=14)

    def show_dispatch_staff_schedule(self):
        """План/факт змін зареєстрованих працівників випуску."""
        if hasattr(self,"dispatch_win") and self.dispatch_win.winfo_exists():
            self.dispatch_win.lift(); self.refresh_dispatch_shifts(); return
        win=tk.Toplevel(self); self.dispatch_win=win; win.title("Випуск на лінію — зміни персоналу")
        fit_window_to_screen(win,980,620,780,500)
        top=ttk.Frame(win,padding=8); top.pack(fill="x")
        ttk.Label(top,text="Дата:").pack(side="left")
        try: initial=self._schedule_parse_date().strftime("%d.%m.%Y")
        except Exception: initial=date.today().strftime("%d.%m.%Y")
        self.dispatch_date_var=tk.StringVar(value=initial)
        ttk.Entry(top,textvariable=self.dispatch_date_var,width=12).pack(side="left",padx=(4,2))
        calendar_button(top,self.dispatch_date_var).pack(side="left",padx=(0,8))
        ttk.Button(top,text="Показати",command=self.refresh_dispatch_shifts).pack(side="left",padx=3)
        ttk.Button(top,text="Додати зміну",command=self.dispatch_shift_form).pack(side="left",padx=3)
        ttk.Button(top,text="Редагувати",command=self.edit_dispatch_shift).pack(side="left",padx=3)
        ttk.Button(top,text="Видалити",command=self.delete_dispatch_shift).pack(side="left",padx=3)
        ttk.Label(
            win,text=("Це окремий облік роботи персоналу випуску. ПІБ чергового автоматично переходить у шляхівки цієї дати; "
                      "фактична відмітка і власноручний підпис залишаються у паперовому документі."),
            foreground="gray",wraplength=930,justify="left"
        ).pack(fill="x",padx=10,pady=(0,6))
        frame=ttk.Frame(win); frame.pack(fill="both",expand=True,padx=10,pady=5)
        frame.columnconfigure(0,weight=1); frame.rowconfigure(0,weight=1)
        cols=("id","role","name","personnel","shift","start","end","location","planned","actual","notes")
        self.dispatch_tree=ttk.Treeview(frame,columns=cols,show="headings")
        heads={"id":"ID","role":"Роль","name":"ПІБ","personnel":"Таб. №","shift":"Зміна","start":"Початок","end":"Кінець","location":"Місце","planned":"План","actual":"Факт","notes":"Примітка"}
        widths={"id":45,"role":90,"name":230,"personnel":75,"shift":60,"start":72,"end":95,"location":150,"planned":70,"actual":70,"notes":220}
        for key in cols: self.dispatch_tree.heading(key,text=heads[key]); self.dispatch_tree.column(key,width=widths[key],anchor="w")
        ybar=ttk.Scrollbar(frame,orient="vertical",command=self.dispatch_tree.yview); xbar=ttk.Scrollbar(frame,orient="horizontal",command=self.dispatch_tree.xview)
        self.dispatch_tree.configure(yscrollcommand=ybar.set,xscrollcommand=xbar.set)
        self.dispatch_tree.grid(row=0,column=0,sticky="nsew"); ybar.grid(row=0,column=1,sticky="ns"); xbar.grid(row=1,column=0,sticky="ew")
        self.dispatch_tree.bind("<Double-1>",lambda _e:self.edit_dispatch_shift())
        self.refresh_dispatch_shifts()

    def _dispatch_selected_date(self):
        try: return datetime.strptime(self.dispatch_date_var.get().strip(),"%d.%m.%Y").date()
        except Exception:
            messagebox.showerror("Зміни персоналу","Дата має бути у форматі ДД.ММ.РРРР.",parent=getattr(self,"dispatch_win",self)); return None

    def refresh_dispatch_shifts(self):
        if not hasattr(self,"dispatch_tree") or not self.dispatch_tree.winfo_exists(): return
        work_date=self._dispatch_selected_date()
        if not work_date: return
        for item in self.dispatch_tree.get_children(): self.dispatch_tree.delete(item)
        con=db(); rows=con.execute(
            """SELECT sh.*,e.last_name||' '||e.first_name||CASE WHEN COALESCE(e.middle_name,'')<>'' THEN ' '||e.middle_name ELSE '' END full_name,
                      e.personnel_no FROM employee_shifts sh JOIN employees e ON e.id=sh.employee_id
                WHERE sh.work_date=? AND sh.role IN ('Лікар','Механік','Диспетчер')
                ORDER BY sh.shift_no,sh.role,e.last_name,e.first_name""",(work_date.isoformat(),)
        ).fetchall(); con.close()
        for row in rows:
            self.dispatch_tree.insert("","end",values=(row["id"],row["role"],row["full_name"],row["personnel_no"],
                "I" if row["shift_no"]==1 else "II",row["start_time"],f"D+{row['end_day_offset']} {row['end_time']}",row["location"],
                hours_value_hhmm(row["planned_hours"]),hours_value_hhmm(row["actual_hours"]) if row["actual_hours"] is not None else "—",row["notes"]))
        if hasattr(self,"waybill_win") and self.waybill_win.winfo_exists(): self.refresh_waybill_issue_list()

    def _selected_dispatch_shift(self):
        sel=getattr(self,"dispatch_tree",None).selection() if hasattr(self,"dispatch_tree") else ()
        if not sel: return None
        sid=int(self.dispatch_tree.item(sel[0],"values")[0]); con=db()
        row=con.execute("""SELECT sh.*,e.last_name||' '||e.first_name||CASE WHEN COALESCE(e.middle_name,'')<>'' THEN ' '||e.middle_name ELSE '' END full_name,
                              e.personnel_no FROM employee_shifts sh JOIN employees e ON e.id=sh.employee_id WHERE sh.id=?""",(sid,)).fetchone(); con.close(); return row

    def dispatch_shift_form(self, existing=None):
        parent=getattr(self,"dispatch_win",self); win=tk.Toplevel(parent); win.title("Зміна працівника випуску")
        fit_window_to_screen(win,680,650,590,520); win.transient(parent); win.grab_set()
        default_date=(existing["work_date"] if existing else (self._dispatch_selected_date() or date.today()).isoformat())
        try: default_date=datetime.strptime(default_date,"%Y-%m-%d").strftime("%d.%m.%Y")
        except Exception: pass
        values={
            "date":tk.StringVar(value=default_date),"role":tk.StringVar(value=existing["role"] if existing else "Лікар"),
            "name":tk.StringVar(value=existing["full_name"] if existing else ""),"personnel":tk.StringVar(value=existing["personnel_no"] if existing else ""),
            "shift":tk.StringVar(value=("I" if existing and existing["shift_no"]==1 else "II" if existing else "I")),
            "start":tk.StringVar(value=existing["start_time"] if existing else ""),"end":tk.StringVar(value=existing["end_time"] if existing else ""),
            "end_day":tk.StringVar(value=str(existing["end_day_offset"] if existing else 0)),
            "location":tk.StringVar(value=existing["location"] if existing else ""),
            "actual":tk.StringVar(value=(hours_value_hhmm(existing["actual_hours"]) if existing and existing["actual_hours"] is not None else "")),
            "notes":tk.StringVar(value=existing["notes"] if existing else "")
        }
        fields=(("date","Дата початку"),("role","Роль"),("name","Працівник з реєстру"),("personnel","Табельний №"),("shift","Зміна"),("start","Початок роботи"),("end_day","Кінець, день D+"),("end","Кінець роботи"),("location","Місце випуску"),("actual","Фактично відпрацьовано ГГ:ХХ"),("notes","Примітка"))
        widgets={}
        for row,(key,label) in enumerate(fields):
            ttk.Label(win,text=label).grid(row=row,column=0,sticky="w",padx=10,pady=6)
            if key=="role": widget=ttk.Combobox(win,textvariable=values[key],values=("Лікар","Механік","Диспетчер"),state="readonly",width=39)
            elif key=="shift": widget=ttk.Combobox(win,textvariable=values[key],values=("I","II"),state="readonly",width=39)
            elif key=="name":
                con=db(); names=[r[0] for r in con.execute("""SELECT DISTINCT e.last_name||' '||e.first_name||CASE WHEN COALESCE(e.middle_name,'')<>'' THEN ' '||e.middle_name ELSE '' END FROM employees e JOIN employee_roles er ON er.employee_id=e.id WHERE e.active=1 AND er.role IN ('Лікар','Механік','Диспетчер') ORDER BY 1""")]; con.close()
                widget=ttk.Combobox(win,textvariable=values[key],values=names,state="readonly",width=39)
            elif key=="personnel": widget=ttk.Entry(win,textvariable=values[key],width=42,state="readonly")
            elif key=="end_day": widget=ttk.Spinbox(win,textvariable=values[key],from_=0,to=7,width=8)
            else: widget=ttk.Entry(win,textvariable=values[key],width=42)
            widget.grid(row=row,column=1,sticky="ew",padx=10,pady=6); widgets[key]=widget
            if key=="date": calendar_button(win,values[key]).grid(row=row,column=2,sticky="w",padx=(0,8),pady=6)
        def refresh_staff_choices(_event=None):
            con=db(); rows=con.execute("""SELECT e.personnel_no,e.last_name||' '||e.first_name||CASE WHEN COALESCE(e.middle_name,'')<>'' THEN ' '||e.middle_name ELSE '' END full_name
                FROM employees e JOIN employee_roles er ON er.employee_id=e.id WHERE e.active=1 AND er.role=? ORDER BY e.last_name,e.first_name""",(values["role"].get(),)).fetchall(); con.close()
            mapping={r["full_name"]:r["personnel_no"] or "" for r in rows}; widgets["name"]["values"]=list(mapping)
            if values["name"].get() not in mapping: values["name"].set("")
            values["personnel"].set(mapping.get(values["name"].get(),""))
        def refresh_personnel(_event=None):
            con=db(); row=con.execute("""SELECT e.personnel_no FROM employees e JOIN employee_roles er ON er.employee_id=e.id WHERE e.active=1 AND er.role=? AND e.last_name||' '||e.first_name||CASE WHEN COALESCE(e.middle_name,'')<>'' THEN ' '||e.middle_name ELSE '' END=? LIMIT 1""",(values["role"].get(),values["name"].get())).fetchone(); con.close()
            values["personnel"].set((row["personnel_no"] if row else "") or "")
        widgets["role"].bind("<<ComboboxSelected>>",refresh_staff_choices,add="+")
        widgets["name"].bind("<<ComboboxSelected>>",refresh_personnel,add="+")
        refresh_staff_choices()
        if existing:
            values["name"].set(existing["full_name"]); refresh_personnel()
        win.columnconfigure(1,weight=1)
        def save():
            try: work_date=datetime.strptime(values["date"].get().strip(),"%d.%m.%Y").date()
            except ValueError:
                messagebox.showerror("Зміна персоналу","Дата має бути у форматі ДД.ММ.РРРР.",parent=win); return
            name=values["name"].get().strip(); role=values["role"].get(); shift_no=1 if values["shift"].get()=="I" else 2
            if not name:
                messagebox.showerror("Зміна персоналу","Вкажіть ПІБ працівника.",parent=win); return
            for key in ("start","end"):
                raw=values[key].get().strip()
                if raw:
                    try: parse_hhmm(raw)
                    except Exception:
                        messagebox.showerror("Зміна персоналу","Час має бути у форматі ГГ:ХХ.",parent=win); return
            try: end_day=int(values["end_day"].get())
            except ValueError: end_day=-1
            if not 0 <= end_day <= 7:
                messagebox.showerror("Зміна персоналу","День завершення має бути від D+0 до D+7.",parent=win); return
            try:
                start_min=parse_hhmm(values["start"].get().strip()); end_min=parse_hhmm(values["end"].get().strip())+end_day*1440
                if end_min<=start_min: raise ValueError
                planned=(end_min-start_min)/60.0
            except Exception:
                messagebox.showerror("Зміна персоналу","Кінець зміни має бути пізніше початку з урахуванням D+.",parent=win); return
            actual=None
            if values["actual"].get().strip():
                try:
                    ah,am=map(int,values["actual"].get().strip().split(":"))
                    if ah<0 or not 0<=am<=59: raise ValueError
                    actual=ah+am/60.0
                except Exception:
                    messagebox.showerror("Зміна персоналу","Факт задається у форматі ГГ:ХХ.",parent=win); return
            con=db()
            employee=con.execute("""SELECT e.id,e.personnel_no FROM employees e JOIN employee_roles er ON er.employee_id=e.id
                    WHERE er.role=? AND e.active=1 AND e.last_name||' '||e.first_name||CASE WHEN COALESCE(e.middle_name,'')<>'' THEN ' '||e.middle_name ELSE '' END=? LIMIT 1""",(role,name)).fetchone()
            if not employee:
                con.close(); messagebox.showerror("Зміна персоналу",f"Працівник не має активної ролі «{role}». Спочатку виправте картку у реєстрі працівників.",parent=win); return
            duplicate=con.execute(
                "SELECT id FROM employee_shifts WHERE work_date=? AND shift_no=? AND role=? AND id<>?",
                (work_date.isoformat(),shift_no,role,existing["id"] if existing else -1)
            ).fetchone()
            if duplicate:
                con.close(); messagebox.showerror("Зміна персоналу",f"На цю дату для ролі «{role}», зміна {values['shift'].get()}, уже є призначення.",parent=win); return
            new_start=datetime.combine(work_date,datetime.min.time())+timedelta(minutes=start_min)
            new_end=datetime.combine(work_date+timedelta(days=end_day),datetime.min.time())+timedelta(minutes=parse_hhmm(values["end"].get().strip()))
            candidates=con.execute("""SELECT * FROM employee_shifts WHERE role=? AND lower(COALESCE(location,''))=lower(?)
                    AND work_date BETWEEN ? AND ? AND id<>?""",(role,values["location"].get().strip(),(work_date-timedelta(days=7)).isoformat(),(work_date+timedelta(days=end_day)).isoformat(),existing["id"] if existing else -1)).fetchall()
            for other in candidates:
                other_date=datetime.strptime(other["work_date"],"%Y-%m-%d").date()
                other_start=datetime.combine(other_date,datetime.min.time())+timedelta(minutes=parse_hhmm(other["start_time"]))
                other_end=datetime.combine(other_date+timedelta(days=int(other["end_day_offset"] or 0)),datetime.min.time())+timedelta(minutes=parse_hhmm(other["end_time"]))
                if new_start<other_end and other_start<new_end:
                    con.close(); messagebox.showerror("Зміна персоналу",f"Час перетинається з іншою зміною ролі «{role}» у цьому місці.",parent=win); return
            vals=(employee["id"],role,work_date.isoformat(),shift_no,values["start"].get().strip(),end_day,values["end"].get().strip(),values["location"].get().strip(),planned,actual,"actual" if actual is not None else "planned",values["notes"].get().strip())
            if existing: con.execute("UPDATE employee_shifts SET employee_id=?,role=?,work_date=?,shift_no=?,start_time=?,end_day_offset=?,end_time=?,location=?,planned_hours=?,actual_hours=?,status=?,notes=? WHERE id=?",vals+(existing["id"],))
            else: con.execute("INSERT INTO employee_shifts(employee_id,role,work_date,shift_no,start_time,end_day_offset,end_time,location,planned_hours,actual_hours,status,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",vals)
            con.commit(); con.close(); self.dispatch_date_var.set(work_date.strftime("%d.%m.%Y")); self.refresh_dispatch_shifts(); win.destroy()
        ttk.Button(win,text="Зберегти",command=save).grid(row=len(fields),column=1,sticky="e",padx=10,pady=12)

    def edit_dispatch_shift(self):
        row=self._selected_dispatch_shift()
        if row: self.dispatch_shift_form(row)

    def delete_dispatch_shift(self):
        row=self._selected_dispatch_shift()
        if not row: return
        if messagebox.askyesno("Зміни персоналу","Видалити це призначення?",parent=self.dispatch_win):
            con=db(); con.execute("DELETE FROM employee_shifts WHERE id=?",(row["id"],)); con.commit(); con.close(); self.refresh_dispatch_shifts()

    def _duty_staff_for_work_date(self, work_date, con=None):
        """Єдиний лікар/механік для I/II зміни конкретної дати графіка.

        Шляхівка може переходити через 00:00, але її поля «I/II зміна»
        належать даті графіка. Тому наступний календарний день не має права
        перезаписувати персонал тієї самої зміни у нічному рейсі.
        """
        own=con is None
        if own:
            con=db()
        rows=con.execute(
            """SELECT sh.*,e.last_name||' '||e.first_name||
                      CASE WHEN COALESCE(e.middle_name,'')<>'' THEN ' '||e.middle_name ELSE '' END full_name
               FROM employee_shifts sh
               JOIN employees e ON e.id=sh.employee_id
               WHERE sh.work_date=? AND e.active=1
                 AND sh.role IN ('Лікар','Механік')
               ORDER BY sh.role,sh.shift_no,sh.id""",
            (work_date.isoformat(),),
        ).fetchall()

        override_types=set(globals().get("TAXO_NONWORK_OVERRIDE_TYPES",set()) or ())
        grouped={}
        for row in rows:
            base=datetime.strptime(row["work_date"],"%Y-%m-%d")
            sh,sm=map(int,row["start_time"].split(":"))
            eh,em=map(int,row["end_time"].split(":"))
            row_start=base.replace(hour=sh,minute=sm)
            row_end=(base+timedelta(days=int(row["end_day_offset"] or 0))).replace(hour=eh,minute=em)

            unavailable=False
            cursor=row_start.date()
            while override_types and cursor<=row_end.date():
                entry=con.execute(
                    "SELECT day_type FROM employee_time_entries WHERE employee_id=? AND work_date=?",
                    (row["employee_id"],cursor.isoformat()),
                ).fetchone()
                if entry and str(entry["day_type"] or "") in override_types:
                    unavailable=True
                    break
                cursor+=timedelta(days=1)
            if unavailable:
                continue

            key=(row["role"],int(row["shift_no"]))
            grouped.setdefault(key,[]).append(row)

        result={
            "doctor_1":"","doctor_2":"",
            "mechanic_1":"","mechanic_2":"",
            "staff_conflicts":[],
        }
        for (role,shift_no),slot_rows in grouped.items():
            prefix="doctor" if role=="Лікар" else "mechanic"
            key=f"{prefix}_{shift_no}"
            if len(slot_rows)==1:
                result[key]=slot_rows[0]["full_name"]
                continue
            names=", ".join(row["full_name"] for row in slot_rows)
            roman="I" if shift_no==1 else "II"
            result["staff_conflicts"].append(
                f"{role} {roman}: {len(slot_rows)} призначення ({names})"
            )
        if own:
            con.close()
        return result

    def _duty_staff_for_interval(self, start_dt, end_dt, location="", con=None):
        """Працівники, чиї зміни реально перекривають випуск/рейс."""
        own=con is None
        if own: con=db()
        from_date=(start_dt.date()-timedelta(days=7)).isoformat()
        rows=con.execute("""SELECT sh.*,e.last_name||' '||e.first_name||CASE WHEN COALESCE(e.middle_name,'')<>'' THEN ' '||e.middle_name ELSE '' END full_name
             FROM employee_shifts sh JOIN employees e ON e.id=sh.employee_id
             WHERE sh.work_date BETWEEN ? AND ? AND e.active=1 AND sh.role IN ('Лікар','Механік')
             ORDER BY sh.work_date,sh.start_time""",(from_date,end_dt.date().isoformat())).fetchall()
        if own: con.close()
        result={"doctor_1":"","doctor_2":"","mechanic_1":"","mechanic_2":""}
        ranked=[]
        for row in rows:
            base=datetime.strptime(row["work_date"],"%Y-%m-%d")
            sh,sm=map(int,row["start_time"].split(":")); eh,em=map(int,row["end_time"].split(":"))
            row_start=base.replace(hour=sh,minute=sm)
            row_end=(base+timedelta(days=int(row["end_day_offset"] or 0))).replace(hour=eh,minute=em)
            if row_end <= start_dt or row_start >= end_dt:
                continue
            exact_location=1 if location and (row["location"] or "").strip().casefold()==location.strip().casefold() else 0
            ranked.append((exact_location,row_start,row))
        for _match,_start,row in sorted(ranked,key=lambda x:(x[0],x[1]),reverse=True):
            prefix="doctor" if row["role"]=="Лікар" else "mechanic"
            key=f"{prefix}_{row['shift_no']}"
            if not result[key]: result[key]=row["full_name"]
        return result

    def _duty_staff_for_date(self, work_date, con=None):
        start=datetime.combine(work_date,datetime.min.time())
        return self._duty_staff_for_interval(start,start+timedelta(days=1),con=con)

    def _waybill_schedule_rows(self, work_date):
        """Rows eligible for waybill issuance for the selected schedule day."""
        con=db()
        rows=con.execute(
            """SELECT w.*, d.last_name,d.first_name,d.middle_name,d.personnel_no AS driver_personnel_no,
                      r.code AS route_code, r.name AS route_catalog_name,
                      r.start_location AS route_start_location,r.end_location AS route_end_location,
                      r.start_day_offset AS route_start_day,r.end_day_offset AS route_end_day,
                      r.start_direction AS route_start_direction,r.planned_distance_km AS route_planned_distance_km,
                      v.name AS vehicle_name, v.plate AS vehicle_plate, v.make_model AS vehicle_make_model,v.garage_no AS vehicle_garage_no,
                      wb.id AS waybill_id,
                      CASE WHEN COALESCE(wb.document_number,'')<>'' THEN trim(COALESCE(wb.document_series,'')||' '||wb.document_number) ELSE wb.waybill_no END AS waybill_no,
                      wb.pdf_path AS waybill_pdf, wb.revision AS waybill_revision,wb.status AS waybill_status,
                      wb.odometer_start AS waybill_odometer_start,wb.odometer_end AS waybill_odometer_end,
                      wb.planned_distance_km AS waybill_planned_distance_km
                 FROM worklog w
                 JOIN drivers d ON d.id=w.driver_id
            LEFT JOIN routes r ON r.id=w.route_id
            LEFT JOIN vehicles v ON v.id=w.vehicle_id
            LEFT JOIN waybills wb ON wb.worklog_id=w.id
                WHERE w.work_date=?
             ORDER BY d.last_name,d.first_name,d.middle_name""",
            (work_date.isoformat(),)
        ).fetchall()
        out=[]
        day_duty=self._duty_staff_for_work_date(work_date,con)
        for r in rows:
            stored_segments=con.execute(
                "SELECT * FROM work_segments WHERE worklog_id=? ORDER BY segment_no",(r["id"],)
            ).fetchall()
            override=_driver_absence_for_day(con,r["driver_id"],work_date)
            state=driver_day_view(
                work_date,r,stored_segments,
                day_type_override=override,
                suppress_plan=bool(override),
            )
            if override:
                continue
            if state["day_type"] not in {"Робота","Готовність","Інше"} and state["work_minutes"]<=0:
                continue
            segs=stored_segments if stored_segments else [r]
            drive_pairs=[]; work_pairs=[]
            for sg in segs:
                ds=(sg["start_time"] or "").strip(); de=(sg["end_time"] or "").strip()
                ws=(sg["work_start_time"] or "").strip() or ds
                we=(sg["work_end_time"] or "").strip() or de
                if ws and we: work_pairs.append((ws,we))
                if ds and de: drive_pairs.append((ds,de))
            dep=drive_pairs[0][0] if drive_pairs else (work_pairs[0][0] if work_pairs else "")
            ret=drive_pairs[-1][1] if drive_pairs else (work_pairs[-1][1] if work_pairs else "")
            start_day=int(r["route_start_day"] or 0); end_day=int(r["route_end_day"] or 0)
            def at_day(day_no,time_value):
                if not time_value: return datetime.combine(work_date+timedelta(days=day_no),datetime.min.time())
                hh,mm=map(int,time_value.split(":")); return datetime.combine(work_date+timedelta(days=day_no),datetime.min.time()).replace(hour=hh,minute=mm)
            start_dt=at_day(start_day,dep); end_dt=at_day(end_day,ret)
            if end_dt<=start_dt: end_dt+=timedelta(days=1)
            multiday=end_dt.date()>work_date
            start_location=(r["route_start_location"] or "").strip()
            end_location=(r["route_end_location"] or "").strip()
            duty=day_duty
            stop_counts={x["direction"]:x["n"] for x in con.execute("SELECT direction,COUNT(*) n FROM route_stops WHERE route_id=? GROUP BY direction",(r["route_id"],)).fetchall()} if r["route_id"] else {}
            route_code=(r["route_code"] or "").strip()
            route_name=(r["route_catalog_name"] or "").strip() or (r["route_name"] or "").strip()
            route_label=(f"{route_code} / {route_name}" if route_code and route_name else route_code or route_name)
            vehicle_parts=[]
            vm=(r["vehicle_make_model"] or "").strip()
            vn=(r["vehicle_name"] or "").strip() or (r["vehicle"] or "").strip()
            vp=(r["vehicle_plate"] or "").strip()
            if vm: vehicle_parts.append(vm)
            elif vn: vehicle_parts.append(vn)
            if vp: vehicle_parts.append(vp)
            if (r["vehicle_garage_no"] or "").strip(): vehicle_parts.append(f"гар. № {r['vehicle_garage_no'].strip()}")
            vehicle_label=" / ".join(vehicle_parts) or (r["vehicle"] or "").strip()
            odometer_start,odometer_end=get_waybill_odometer_readings(con,r["id"])
            if odometer_start is None and r["waybill_odometer_start"] is not None:
                odometer_start=int(r["waybill_odometer_start"])
            if odometer_end is None and r["waybill_odometer_end"] is not None:
                odometer_end=int(r["waybill_odometer_end"])
            planned_distance_km=(
                r["waybill_planned_distance_km"]
                if r["waybill_id"] and (r["waybill_status"] or "active")=="active" and r["waybill_planned_distance_km"] is not None
                else r["route_planned_distance_km"]
            )
            out.append({
                "worklog_id":r["id"],"driver_id":r["driver_id"],
                "driver":f"{r['last_name']} {r['first_name']} {r['middle_name']}".strip(),
                "date":work_date,"end_date":end_dt.date(),"route_id":r["route_id"],"route":route_label,
                "route_code":route_code,"driver_personnel_no":r["driver_personnel_no"] or "",
                "vehicle_id":r["vehicle_id"],"vehicle":vehicle_label,
                "vehicle_garage_no":r["vehicle_garage_no"] or "",
                "planned_departure":waybill_time_label(work_date,start_day,dep,multiday),
                "planned_return":waybill_time_label(work_date,end_day,ret,multiday),
                "start_time_raw":dep,"end_time_raw":ret,"start_day_offset":start_day,"end_day_offset":end_day,
                "start_location":start_location,"end_location":end_location,
                "start_direction":r["route_start_direction"] or "outbound",
                "outbound_stop_count":int(stop_counts.get("outbound",0)),"return_stop_count":int(stop_counts.get("return",0)),
                "work_span":f"{work_pairs[0][0]}-{work_pairs[-1][1]}" if work_pairs else "",
                "drive_span":f"{drive_pairs[0][0]}-{drive_pairs[-1][1]}" if drive_pairs else "",
                "work_hours":minutes_to_db_hours(state["work_minutes"]),
                "driving_hours":minutes_to_db_hours(state["driving_minutes"]),
                "schedule_conflict":state["work_overlap_minutes"]>0,
                "schedule_conflict_minutes":state["work_overlap_minutes"],
                "schedule_conflict_message":segment_overlap_message(stored_segments,"work"),
                "waybill_id":r["waybill_id"],"waybill_no":r["waybill_no"] or "",
                "waybill_pdf":r["waybill_pdf"] or "","waybill_revision":r["waybill_revision"] or 0,
                "waybill_status":r["waybill_status"] or "",
                "odometer_start":odometer_start,"odometer_end":odometer_end,
                "planned_distance_km":int(planned_distance_km) if planned_distance_km is not None else None,
                **duty,
            })
        con.close()
        return out

    def show_waybills_for_schedule(self):
        d=self._schedule_parse_date()
        if not d:
            return
        if hasattr(self,"waybill_win") and self.waybill_win.winfo_exists():
            self.waybill_date=d
            self.waybill_win.title(f"Шляхівки на {d.strftime('%d.%m.%Y')}")
            self.waybill_win.lift(); self.refresh_waybill_issue_list(); return
        win=tk.Toplevel(self); self.waybill_win=win; self.waybill_date=d
        win.title(f"Шляхівки на {d.strftime('%d.%m.%Y')}")
        fit_window_to_screen(win,1120,600,850,480)
        top=ttk.Frame(win,padding=8); top.pack(fill="x")
        self.waybill_date_label=tk.StringVar(value=d.strftime("%d.%m.%Y"))
        ttk.Label(top,text="Дата графіка:",font=("TkDefaultFont",9,"bold")).pack(side="left")
        ttk.Label(top,textvariable=self.waybill_date_label).pack(side="left",padx=(4,12))
        actions=ttk.Frame(win,padding=(8,0,8,5)); actions.pack(fill="x")
        ttk.Button(actions,text="Оновити",command=self.refresh_waybill_issue_list).pack(side="left",padx=3)
        ttk.Button(actions,text="Сформувати / видати PDF",command=self.issue_selected_waybill).pack(side="left",padx=3)
        ttk.Button(actions,text="Відкрити PDF",command=self.open_selected_waybill).pack(side="left",padx=3)
        ttk.Button(actions,text="Анулювати номер",command=self.void_selected_waybill).pack(side="left",padx=3)
        ttk.Button(actions,text="Папка шляхівок",command=lambda:open_external(WAYBILL_DIR)).pack(side="left",padx=3)
        ttk.Button(actions,text="Спідометр / пробіг",command=self.edit_waybill_odometer).pack(side="left",padx=3)
        ttk.Button(actions,text="Історія пробігу",command=self.show_vehicle_odometer_history).pack(side="left",padx=3)
        ttk.Button(actions,text="Зміни лікаря/механіка",command=self.show_dispatch_staff_schedule).pack(side="left",padx=3)
        ttk.Label(
            win,
            text=("Планові реквізити беруться безпосередньо з графіка: водій, маршрут, автомобіль, "
                  "графік зупинок прямого/зворотного напрямку та чергові лікар/механік. Фактичні, паливні й підписні поля залишаються порожніми."),
            foreground="gray",wraplength=1050,justify="left"
        ).pack(fill="x",padx=10,pady=(0,6))
        frame=ttk.Frame(win); frame.pack(fill="both",expand=True,padx=10,pady=5)
        cols=("driver","route","vehicle","depart","return","odometer","doctor","mechanic","work","drive","status")
        self.waybill_tree=ttk.Treeview(frame,columns=cols,show="headings")
        heads={"driver":"Водій","route":"Маршрут","vehicle":"Автомобіль","depart":"Виїзд план","return":"Заїзд план","odometer":"Пробіг / спідометр","doctor":"Лікар","mechanic":"Механік","work":"Робота","drive":"Керування","status":"Шляхівка"}
        widths={"driver":210,"route":150,"vehicle":190,"depart":100,"return":100,"odometer":220,"doctor":180,"mechanic":180,"work":80,"drive":90,"status":130}
        for c in cols:
            self.waybill_tree.heading(c,text=heads[c]); self.waybill_tree.column(c,width=widths[c],anchor="w")
        y=ttk.Scrollbar(frame,orient="vertical",command=self.waybill_tree.yview)
        x=ttk.Scrollbar(frame,orient="horizontal",command=self.waybill_tree.xview)
        self.waybill_tree.configure(yscrollcommand=y.set,xscrollcommand=x.set)
        self.waybill_tree.grid(row=0,column=0,sticky="nsew"); y.grid(row=0,column=1,sticky="ns"); x.grid(row=1,column=0,sticky="ew")
        frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
        self.waybill_tree.bind("<Double-1>",lambda _e:self.issue_selected_waybill())
        self.waybill_rows={}
        self.refresh_waybill_issue_list()

    def refresh_waybill_issue_list(self):
        if not hasattr(self,"waybill_tree") or not self.waybill_tree.winfo_exists():
            return
        d=getattr(self,"waybill_date",self._schedule_parse_date())
        if not d: return
        self.waybill_date_label.set(d.strftime("%d.%m.%Y"))
        for item in self.waybill_tree.get_children(): self.waybill_tree.delete(item)
        self.waybill_rows={}
        for row in self._waybill_schedule_rows(d):
            missing=[]
            if not row["route"]: missing.append("маршрут")
            if not row["vehicle"]: missing.append("авто")
            if not row["planned_departure"] or not row["planned_return"]: missing.append("час")
            if not row["start_location"] or not row["end_location"]: missing.append("точки початку/завершення")
            if not row["outbound_stop_count"] or not row["return_stop_count"]: missing.append("прямий/зворотний графік")
            if row.get("schedule_conflict"): missing.append(f"перекриття часу {minutes_hhmm(row['schedule_conflict_minutes'])}")
            if row.get("staff_conflicts"):
                missing.append("конфлікт чергових: "+"; ".join(row["staff_conflicts"]))
            if row["waybill_no"] and row["waybill_status"]=="void":
                status=f"АНУЛЬОВАНА № {row['waybill_no']}"
            elif row["waybill_no"]:
                status=f"№ {row['waybill_no']}" + (f" r{row['waybill_revision']}" if row['waybill_revision']>1 else "")
            elif missing:
                status="Немає: "+", ".join(missing)
            else:
                status="Не видана"
            iid=self.waybill_tree.insert("","end",values=(
                row["driver"],row["route"],row["vehicle"],row["planned_departure"],row["planned_return"],
                waybill_mileage_display(row["odometer_start"],row["odometer_end"],row["planned_distance_km"]),
                row["doctor_1"] or "—",row["mechanic_1"] or "—",hours_value_hhmm(row["work_hours"]),hours_value_hhmm(row["driving_hours"]),status
            ))
            self.waybill_rows[iid]=row

    def _selected_waybill_data(self):
        if not hasattr(self,"waybill_tree"): return None
        sel=self.waybill_tree.selection()
        return self.waybill_rows.get(sel[0]) if sel else None

    def edit_waybill_odometer(self):
        row=self._selected_waybill_data()
        if not row:
            messagebox.showinfo("Спідометр","Виберіть рядок графіка.",parent=getattr(self,"waybill_win",self)); return
        if not row.get("vehicle_id"):
            messagebox.showwarning("Спідометр","Спочатку прив'яжіть автомобіль у графіку. Показник без автомобіля зберегти неможливо.",parent=self.waybill_win); return
        win=tk.Toplevel(self.waybill_win); win.title("Показники спідометра — необов'язково")
        fit_window_to_screen(win,650,455,560,390); win.transient(self.waybill_win); win.grab_set()
        start=tk.StringVar(value="" if row["odometer_start"] is None else str(row["odometer_start"]))
        end=tk.StringVar(value="" if row["odometer_end"] is None else str(row["odometer_end"]))
        notes=tk.StringVar()
        ttk.Label(win,text=row["vehicle"],font=("TkDefaultFont",10,"bold"),wraplength=600).grid(row=0,column=0,columnspan=2,sticky="w",padx=12,pady=(12,4))
        ttk.Label(win,text=f"Рейс: {waybill_date_range_label(row['date'],row['end_date'])}; {row['driver']}",foreground="gray").grid(row=1,column=0,columnspan=2,sticky="w",padx=12,pady=(0,10))
        ttk.Label(win,text="На початок рейсу, км").grid(row=2,column=0,sticky="w",padx=12,pady=7)
        ttk.Entry(win,textvariable=start,width=28).grid(row=2,column=1,sticky="ew",padx=12,pady=7)
        ttk.Label(win,text="На завершення рейсу, км").grid(row=3,column=0,sticky="w",padx=12,pady=7)
        ttk.Entry(win,textvariable=end,width=28).grid(row=3,column=1,sticky="ew",padx=12,pady=7)
        plan_text=(f"{row['planned_distance_km']} км" if row.get("planned_distance_km") is not None else "не задано")
        ttk.Label(win,text="Плановий пробіг маршруту").grid(row=4,column=0,sticky="w",padx=12,pady=7)
        ttk.Label(win,text=plan_text,font=("TkDefaultFont",9,"bold")).grid(row=4,column=1,sticky="w",padx=12,pady=7)
        forecast=tk.StringVar()
        ttk.Label(win,textvariable=forecast,foreground="#2255aa").grid(row=5,column=0,columnspan=2,sticky="w",padx=12,pady=4)
        def refresh_forecast(*_):
            try:
                start_value=parse_optional_odometer(start.get())
            except ValueError:
                start_value=None
            predicted=planned_odometer_end(start_value,row.get("planned_distance_km"))
            forecast.set(f"Прогноз кінцевого показника: {predicted} км" if predicted is not None else "Прогноз з'явиться після введення початкового показника і планового пробігу маршруту.")
        start.trace_add("write",refresh_forecast); refresh_forecast()
        ttk.Label(win,text="Примітка").grid(row=6,column=0,sticky="w",padx=12,pady=7)
        ttk.Entry(win,textvariable=notes,width=42).grid(row=6,column=1,sticky="ew",padx=12,pady=7)
        ttk.Label(win,text="Обидва фактичні показники можна лишити порожніми. Прогноз не записується як факт; перевірки лише попереджають і не блокують збереження чи видачу.",foreground="gray",wraplength=600,justify="left").grid(row=7,column=0,columnspan=2,sticky="w",padx=12,pady=8)
        win.columnconfigure(1,weight=1)
        def save_readings():
            try:
                start_value=parse_optional_odometer(start.get()); end_value=parse_optional_odometer(end.get())
            except ValueError as exc:
                messagebox.showerror("Спідометр",str(exc),parent=win); return
            start_at=f"{(row['date']+timedelta(days=int(row['start_day_offset'] or 0))).isoformat()}T{row['start_time_raw'] or '00:00'}:00"
            end_at=f"{(row['date']+timedelta(days=int(row['end_day_offset'] or 0))).isoformat()}T{row['end_time_raw'] or '23:59'}:00"
            con=db(); warnings=odometer_consistency_warnings(
                con,row["vehicle_id"],start_value,end_value,start_at,row["worklog_id"],row.get("planned_distance_km")
            )
            save_waybill_odometer_readings(con,row["worklog_id"],row["vehicle_id"],row["driver_id"],row["date"].isoformat(),start_value,end_value,start_at,end_at,notes.get().strip())
            con.commit(); con.close(); win.destroy(); self.refresh_waybill_issue_list()
            if warnings:
                messagebox.showwarning("Спідометр — перевірте дані","\n\n".join(warnings)+"\n\nДані збережено; шляхівку не заблоковано.",parent=self.waybill_win)
            elif row.get("waybill_id"):
                messagebox.showinfo("Спідометр","Дані збережено. Щоб вони з'явилися у PDF, сформуйте шляхівку повторно; номер збережеться, ревізія збільшиться.",parent=self.waybill_win)
        ttk.Button(win,text="Зберегти",command=save_readings).grid(row=8,column=1,sticky="e",padx=12,pady=12)

    def show_vehicle_odometer_history(self):
        row=self._selected_waybill_data()
        if not row or not row.get("vehicle_id"):
            messagebox.showinfo("Історія пробігу","Виберіть графік із прив'язаним автомобілем.",parent=getattr(self,"waybill_win",self)); return
        win=tk.Toplevel(self.waybill_win); win.title(f"Історія пробігу — {row['vehicle']}")
        fit_window_to_screen(win,880,520,700,420)
        frame=ttk.Frame(win,padding=8); frame.pack(fill="both",expand=True); frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
        cols=("date","kind","value","source","driver","notes")
        tree=ttk.Treeview(frame,columns=cols,show="headings")
        for key,label,width in (("date","Дата й час",145),("kind","Точка",80),("value","Показник, км",110),("source","Джерело",105),("driver","Водій",210),("notes","Примітка",190)):
            tree.heading(key,text=label); tree.column(key,width=width,anchor="w")
        y=ttk.Scrollbar(frame,orient="vertical",command=tree.yview); x=ttk.Scrollbar(frame,orient="horizontal",command=tree.xview); tree.configure(yscrollcommand=y.set,xscrollcommand=x.set)
        tree.grid(row=0,column=0,sticky="nsew"); y.grid(row=0,column=1,sticky="ns"); x.grid(row=1,column=0,sticky="ew")
        con=db(); readings=con.execute("""SELECT o.*,d.last_name,d.first_name,d.middle_name FROM vehicle_odometer_readings o
            LEFT JOIN drivers d ON d.id=o.driver_id WHERE o.vehicle_id=? ORDER BY COALESCE(o.reading_at,''),o.id""",(row["vehicle_id"],)).fetchall(); con.close()
        kind_labels={"start":"початок","end":"кінець","single":"одиночний"}
        for item in readings:
            driver=" ".join(x for x in (item["last_name"],item["first_name"],item["middle_name"]) if x)
            tree.insert("","end",values=((item["reading_at"] or item["work_date"]).replace("T"," "),kind_labels.get(item["reading_kind"],item["reading_kind"]),item["reading_km"],item["source_type"],driver,item["notes"]))
        ttk.Label(win,text="Журнал уже підтримує різні джерела. Майбутнє зчитування з тахокарти додаватиме записи з джерелом tachograph.",foreground="gray").pack(anchor="w",padx=10,pady=(0,8))

    def _waybill_pool_for_date(self, con, work_date):
        return con.execute("""SELECT * FROM waybill_number_pools WHERE status='active' AND valid_from<=?
            AND (COALESCE(valid_until,'')='' OR valid_until>=?) ORDER BY valid_from DESC,id DESC LIMIT 1""",
            (work_date.isoformat(),work_date.isoformat())).fetchone()

    def _next_waybill_internal_number(self, con, issue_year):
        seq=int(con.execute("SELECT COALESCE(MAX(issue_seq),0)+1 FROM waybills WHERE issue_year=?",(issue_year,)).fetchone()[0])
        return seq,f"{issue_year}-{seq:04d}"

    def issue_selected_waybill(self):
        row=self._selected_waybill_data()
        if not row:
            messagebox.showwarning("Шляхівка","Виберіть водія у списку.",parent=getattr(self,"waybill_win",self)); return
        missing=[]
        if not row["route"]: missing.append("маршрут")
        if not row["vehicle"]: missing.append("автомобіль")
        if not row["planned_departure"] or not row["planned_return"]: missing.append("плановий час виїзду/заїзду")
        if not row["start_location"] or not row["end_location"]: missing.append("точка початку/завершення маршруту")
        if not row["outbound_stop_count"] or not row["return_stop_count"]: missing.append("графік прямого і зворотного напрямків")
        if row.get("schedule_conflict"):
            missing.append(
                "перекриття частин робочого часу "
                + minutes_hhmm(row["schedule_conflict_minutes"])
            )
        if row.get("staff_conflicts"):
            missing.append(
                "конфлікт чергових: " + "; ".join(row["staff_conflicts"])
            )
        if missing:
            messagebox.showerror(
                "Шляхівка",
                "Бракує або конфліктують дані: "+", ".join(missing)+".\n\n"
                "Перевірте маршрут і часові частини дня. Для графіка зупинок відкрийте «Маршрути → Заповнити маршрут для шляхівки…».",
                parent=self.waybill_win,
            ); return
        if build_waybill_pdf is None:
            messagebox.showerror("Шляхівка","Модуль формування шляхівки недоступний.",parent=self.waybill_win); return
        # Щойно відредаговані реквізити шляхівки не повинні вимагати окремого
        # натискання «Зберегти» перед видачею документа.
        self.save_company(show_message=False)
        con=db()
        existing=con.execute("SELECT * FROM waybills WHERE worklog_id=?",(row["worklog_id"],)).fetchone()
        company=con.execute("SELECT * FROM company WHERE id=1").fetchone()
        reprint=bool(existing and (existing["status"] or "active")=="active")
        if reprint:
            issue_seq=existing["issue_seq"]; internal_no=(existing["internal_no"] or existing["waybill_no"])
            document_series=(existing["document_series"] or (company["waybill_series"] if company else "АААТ"))
            document_number=(existing["document_number"] or existing["waybill_no"])
            pool=None; revision=int(existing["revision"] or 1)+1
        else:
            pool=self._waybill_pool_for_date(con,row["date"])
            if not pool:
                con.close(); messagebox.showerror("Шляхівка","Для цієї дати роботи немає активного пулу номерів. Налаштуйте його у «Підприємство → Пули серій і номерів».",parent=self.waybill_win); return
            if pool["mode"]=="auto":
                number_value=int(pool["next_number"])
                if number_value>int(pool["end_number"]):
                    con.close(); messagebox.showerror("Шляхівка","Активний пул номерів вичерпано.",parent=self.waybill_win); return
            else:
                raw=simpledialog.askstring("Номер готового бланка",f"Введіть номер із бланка серії {pool['series']} ({pool['start_number']}–{pool['end_number']}):",parent=self.waybill_win)
                if raw is None: con.close(); return
                try: number_value=int(raw.strip())
                except ValueError: con.close(); messagebox.showerror("Шляхівка","Номер має бути цілим числом.",parent=self.waybill_win); return
                if not int(pool["start_number"])<=number_value<=int(pool["end_number"]):
                    con.close(); messagebox.showerror("Шляхівка","Номер поза діапазоном вибраного пулу.",parent=self.waybill_win); return
            width=int(pool["number_width"] or 6); document_series=pool["series"]; document_number=f"{number_value:0{width}d}"
            if con.execute("SELECT 1 FROM waybills WHERE document_series=? AND document_number=?",(document_series,document_number)).fetchone():
                con.close(); messagebox.showerror("Шляхівка","Цю пару серія + номер уже використано.",parent=self.waybill_win); return
            issue_seq,internal_no=self._next_waybill_internal_number(con,row["date"].year); revision=1
        waybill_no=f"{document_series}-{document_number}" if document_series else document_number
        out_dir=WAYBILL_DIR/f"{row['date'].year:04d}"/f"{row['date'].month:02d}"; out_dir.mkdir(parents=True,exist_ok=True)
        safe_driver=re.sub(r"[^0-9A-Za-zА-Яа-яІіЇїЄєҐґ_-]+","_",row["driver"]).strip("_")
        target=out_dir/f"Шляхівка_{waybill_no}_{row['date'].isoformat()}_{safe_driver}.pdf"
        stops=con.execute("SELECT * FROM route_stops WHERE route_id=? ORDER BY direction,stop_no",(row["route_id"],)).fetchall()
        payload={
            "waybill_no":document_number,"internal_no":internal_no,
            "date":waybill_date_range_label(row["date"],row["end_date"]),"work_date":row["date"].isoformat(),"route":row["route"],
            "vehicle":row["vehicle"],"driver":row["driver"],
            "planned_departure":waybill_time_label(row["date"],row["start_day_offset"],row["start_time_raw"],row["end_date"]>row["date"],"\n"),
            "planned_return":waybill_time_label(row["date"],row["end_day_offset"],row["end_time_raw"],row["end_date"]>row["date"],"\n"),
            "work_span":row["work_span"],"drive_span":row["drive_span"],
            "route_code":row["route_code"],"driver_personnel_no":row["driver_personnel_no"],
            "company_name":company["name"] if company else "","waybill_series":document_series,
            "transport_column":company["transport_column"] if company else "","brigade":company["brigade"] if company else "",
            "start_location":row["start_location"],"end_location":row["end_location"],
            "start_direction":row["start_direction"],
            "planned_route_time":hours_value_hhmm(row["driving_hours"]),"planned_duty_time":hours_value_hhmm(row["work_hours"]),
            "odometer_start":row["odometer_start"],"odometer_end":row["odometer_end"],
            "distance_km":(row["odometer_end"]-row["odometer_start"]) if row["odometer_start"] is not None and row["odometer_end"] is not None else None,
            "planned_distance_km":row["planned_distance_km"],
            "doctor_1":row["doctor_1"],"doctor_2":row["doctor_2"],"mechanic_1":row["mechanic_1"],"mechanic_2":row["mechanic_2"],
            "outbound_stops":[dict(s) for s in stops if s["direction"]=="outbound"],
            "return_stops":[dict(s) for s in stops if s["direction"]=="return"],
        }
        actual=write_output_file(
            lambda out: build_waybill_pdf(None,out,payload),target,
            parent=self.waybill_win,kind="PDF шляхівки",error_title="Помилка шляхівки"
        )
        if actual is None:
            con.close(); return
        actual_db_path=db_stored_path(actual)
        now=datetime.now().isoformat(timespec="seconds")
        if not reprint and pool["mode"]=="auto":
            con.execute("UPDATE waybill_number_pools SET next_number=? WHERE id=?",(number_value+1,pool["id"]))
        if existing:
            con.execute(
                """UPDATE waybills SET work_end_date=?,issue_year=?,issue_seq=?,waybill_no=?,route_id=?,route_label=?,vehicle_id=?,vehicle_label=?,planned_departure=?,planned_return=?,
                       doctor_1=?,doctor_2=?,mechanic_1=?,mechanic_2=?,number_pool_id=?,document_series=?,document_number=?,internal_no=?,
                       start_location=?,end_location=?,odometer_start=?,odometer_end=?,distance_km=?,planned_distance_km=?,pdf_path=?,revision=?,status='active',voided_at='',void_reason='',updated_at=? WHERE id=?""",
                (row["end_date"].isoformat(),row["date"].year,issue_seq,waybill_no,row["route_id"],row["route"],row["vehicle_id"],row["vehicle"],row["planned_departure"],row["planned_return"],
                 row["doctor_1"],row["doctor_2"],row["mechanic_1"],row["mechanic_2"],pool["id"] if pool else existing["number_pool_id"],document_series,document_number,internal_no,
                 row["start_location"],row["end_location"],row["odometer_start"],row["odometer_end"],payload["distance_km"],row["planned_distance_km"],actual_db_path,revision,now,existing["id"])
            )
        else:
            con.execute(
                """INSERT INTO waybills(worklog_id,driver_id,work_date,work_end_date,issue_year,issue_seq,waybill_no,route_id,route_label,vehicle_id,vehicle_label,
                   planned_departure,planned_return,doctor_1,doctor_2,mechanic_1,mechanic_2,number_pool_id,document_series,document_number,internal_no,
                   start_location,end_location,odometer_start,odometer_end,distance_km,planned_distance_km,pdf_path,revision,status,issued_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'active',?,?)""",
                (row["worklog_id"],row["driver_id"],row["date"].isoformat(),row["end_date"].isoformat(),row["date"].year,issue_seq,waybill_no,
                 row["route_id"],row["route"],row["vehicle_id"],row["vehicle"],row["planned_departure"],row["planned_return"],
                 row["doctor_1"],row["doctor_2"],row["mechanic_1"],row["mechanic_2"],pool["id"],document_series,document_number,internal_no,
                 row["start_location"],row["end_location"],row["odometer_start"],row["odometer_end"],payload["distance_km"],row["planned_distance_km"],actual_db_path,revision,now,now)
            )
        waybill_id=existing["id"] if existing else con.execute("SELECT id FROM waybills WHERE worklog_id=?",(row["worklog_id"],)).fetchone()[0]
        con.execute("""INSERT INTO waybill_events(waybill_id,event_type,document_series,document_number,internal_no,revision,pdf_path,created_at)
            VALUES(?,?,?,?,?,?,?,?)""",(waybill_id,"reprint" if reprint else "issued",document_series,document_number,internal_no,revision,actual_db_path,now))
        con.commit(); con.close(); self.refresh_waybill_issue_list()
        try: open_external(actual)
        except Exception: pass

    def void_selected_waybill(self):
        row=self._selected_waybill_data()
        if not row or not row.get("waybill_id"):
            messagebox.showinfo("Шляхівка","Для вибраного графіка номер ще не видавався.",parent=getattr(self,"waybill_win",self)); return
        if row.get("waybill_status")=="void":
            messagebox.showinfo("Шляхівка","Ця шляхівка вже анульована. Наступне формування отримає новий номер.",parent=self.waybill_win); return
        reason=simpledialog.askstring("Анулювання шляхівки","Причина анулювання (обов'язково):",parent=self.waybill_win)
        if reason is None: return
        reason=reason.strip()
        if not reason:
            messagebox.showerror("Шляхівка","Вкажіть причину анулювання.",parent=self.waybill_win); return
        if not messagebox.askyesno("Анулювання шляхівки",f"Анулювати № {row['waybill_no']}? Номер не буде повернений у пул.",parent=self.waybill_win): return
        con=db(); wb=con.execute("SELECT * FROM waybills WHERE id=?",(row["waybill_id"],)).fetchone(); now=datetime.now().isoformat(timespec="seconds")
        con.execute("UPDATE waybills SET status='void',voided_at=?,void_reason=?,updated_at=? WHERE id=?",(now,reason,now,row["waybill_id"]))
        con.execute("""INSERT INTO waybill_events(waybill_id,event_type,document_series,document_number,internal_no,revision,pdf_path,reason,created_at)
            VALUES(?,?,?,?,?,?,?,?,?)""",(row["waybill_id"],"void",wb["document_series"],wb["document_number"],wb["internal_no"],wb["revision"],wb["pdf_path"],reason,now))
        con.commit(); con.close(); self.refresh_waybill_issue_list()

    def open_selected_waybill(self):
        row=self._selected_waybill_data()
        if not row or not row.get("waybill_pdf"):
            messagebox.showinfo("Шляхівка","Для вибраного запису PDF ще не сформовано.",parent=getattr(self,"waybill_win",self)); return
        path=real_data_path(row["waybill_pdf"])
        if path is None:
            messagebox.showerror("Шляхівка","Файл шляхівки не знайдено.",parent=self.waybill_win); return
        if not path.exists():
            messagebox.showerror("Шляхівка","Файл шляхівки не знайдено. Сформуйте його повторно.",parent=self.waybill_win); return
        open_external(path)

    def get_work_segments(self, worklog_id):
        if not worklog_id: return []
        con=db(); rows=con.execute("SELECT * FROM work_segments WHERE worklog_id=? ORDER BY segment_no",(worklog_id,)).fetchall(); con.close()
        return rows

    def refresh_month(self):
        if not hasattr(self,"work_tree"): return
        for x in self.work_tree.get_children(): self.work_tree.delete(x)
        if not self.driver_id: return
        y,m=int(self.year_var.get()),int(self.month_var.get())
        driver=self.driver_by_id(self.driver_id)
        if not driver or not driver_employed_on(driver,month_dates(y,m)[-1]):
            return

        con=db()
        rows=con.execute(
            "SELECT * FROM worklog WHERE driver_id=? AND substr(work_date,1,7)=? ORDER BY work_date",
            (self.driver_id,f"{y:04d}-{m:02d}")
        ).fetchall()
        existing={r["work_date"]:r for r in rows}

        absence_overrides={}
        override_types=set(globals().get("TAXO_NONWORK_OVERRIDE_TYPES", set()) or ())
        if override_types:
            employee=con.execute(
                "SELECT id FROM employees WHERE driver_id=? ORDER BY active DESC,id LIMIT 1",
                (self.driver_id,)
            ).fetchone()
            if employee is not None:
                for entry in con.execute(
                    """SELECT work_date,day_type FROM employee_time_entries
                       WHERE employee_id=? AND substr(work_date,1,7)=?""",
                    (employee["id"],f"{y:04d}-{m:02d}")
                ).fetchall():
                    if str(entry["day_type"] or "") in override_types:
                        absence_overrides[entry["work_date"]]=entry["day_type"]

        segment_map={}
        if rows:
            ids=[r["id"] for r in rows]
            q=",".join("?" for _ in ids)
            for seg in con.execute(
                f"SELECT * FROM work_segments WHERE worklog_id IN ({q}) ORDER BY worklog_id,segment_no",
                ids
            ).fetchall():
                segment_map.setdefault(seg["worklog_id"],[]).append(seg)
        con.close()

        for d in month_dates(y,m):
            if not driver_employed_on(driver,d):
                continue
            r=existing.get(d.isoformat())
            segs=segment_map.get(r["id"],[]) if r else []
            override=absence_overrides.get(d.isoformat())
            state=driver_day_view(
                d,r,segs,
                day_type_override=override,
                suppress_plan=bool(override),
            )
            vals=(
                r["id"] if r else "",
                d.strftime("%d.%m.%Y"),
                ["Пн","Вт","Ср","Чт","Пт","Сб","Нд"][d.weekday()],
                state["day_type"],
                state["schedule"],
                state["breaks"],
                minutes_hhmm(state["work_minutes"]),
                minutes_hhmm(state["driving_minutes"]),
                minutes_hhmm(state["overtime_minutes"]),
                r["route_name"] if r and "route_name" in r.keys() else "",
                r["vehicle"] if r else "",
                (f"Відсутність із табеля персоналу"
                 if override and not (r and r["notes"])
                 else (r["notes"] if r else "")),
                ("ВІДСУТНІСТЬ" if override else
                 work_mode_label(
                     r["accounting_mode"] if r and "accounting_mode" in r.keys()
                     else WORK_MODE_MANUAL
                 )),
            )
            self.work_tree.insert("","end",values=vals)

    def edit_work_row(self,_=None):
        sel=self.work_tree.selection()
        if not sel or not self.driver_id: return
        vals=self.work_tree.item(sel[0],"values")
        work_id=int(vals[0]) if vals[0] else None
        date_text=vals[1]
        con=db(); existing=con.execute("SELECT * FROM worklog WHERE id=?",(work_id,)).fetchone() if work_id else None
        routes=con.execute("SELECT * FROM routes WHERE active=1 ORDER BY name").fetchall()
        vehicles=con.execute("SELECT * FROM vehicles WHERE active=1 ORDER BY name,plate").fetchall()
        con.close()
        old_segments=self.get_work_segments(work_id) if work_id else []
        win=tk.Toplevel(self); win.title("Запис робочого часу"); fit_window_to_screen(win,1180,650,900,520); win.transient(self); win.grab_set()
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
        route_combo=ttk.Combobox(
            top,textvariable=route_var,values=list(route_map.keys()),
            state="readonly",width=28
        )
        route_combo.grid(row=1,column=1,columnspan=2,padx=4,sticky="ew")

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
            text="Маршрут = готовий ПЛАН з точними годинами. Після застосування його можна змінити для конкретного дня. Тахокарта дає окремий ФАКТ.",
            foreground="gray"
        ).grid(row=2,column=3,columnspan=4,padx=(8,4),sticky="w")

        top.columnconfigure(1,weight=1)
        top.columnconfigure(4,weight=1)
        top.columnconfigure(6,weight=1)

        apply_frame=ttk.Frame(win); apply_frame.pack(fill="x",padx=10,pady=(2,6))
        ttk.Label(
            apply_frame,
            text="Виберіть маршрут вище та застосуйте його точний часовий сценарій:",
            foreground="gray"
        ).pack(side="left")

        cols=("no","work_start","work_end","drive_start","drive_end","work","drive","activity","note")
        tree=ttk.Treeview(win,columns=cols,show="headings",height=11)
        heads={
            "no":"№",
            "work_start":"Робота від", "work_end":"Робота до",
            "drive_start":"Керування від", "drive_end":"Керування до",
            "work":"Робота", "drive":"Керування",
            "activity":"Тип", "note":"Примітка"
        }
        widths={"no":36,"work_start":82,"work_end":82,"drive_start":92,"drive_end":92,"work":78,"drive":82,"activity":135,"note":220}
        for c in cols: tree.heading(c,text=heads[c]); tree.column(c,width=widths[c],anchor="w")
        tree.pack(fill="both",expand=True,padx=10,pady=5)
        summary_var=tk.StringVar(value="")
        ttk.Label(win,textvariable=summary_var,foreground="gray").pack(anchor="w",padx=12,pady=3)

        seg_data=[]
        def _value(r,key,default=""):
            try:
                return r[key] if key in r.keys() else default
            except Exception:
                return r.get(key,default) if isinstance(r,dict) else default

        def load_segments(items):
            seg_data.clear()
            for r in items:
                ds=(_value(r,"start_time","") or "").strip()
                de=(_value(r,"end_time","") or "").strip()
                ws=(_value(r,"work_start_time","") or "").strip() or ds
                we=(_value(r,"work_end_time","") or "").strip() or de
                try: wh=minutes_to_db_hours(duration_minutes(ws,we)) if ws and we else float(_value(r,"work_hours",0) or 0)
                except Exception: wh=float(_value(r,"work_hours",0) or 0)
                try: dh=minutes_to_db_hours(duration_minutes(ds,de)) if ds and de else 0.0
                except Exception: dh=float(_value(r,"driving_hours",0) or 0)
                seg_data.append({
                    "start_time":ds,"end_time":de,
                    "work_start_time":ws,"work_end_time":we,
                    "work_hours":wh,"driving_hours":dh,
                    "activity_type":_value(r,"activity_type","Робота") or "Робота",
                    "note":_value(r,"note","") or ""
                })
            redraw()

        def redraw():
            for x in tree.get_children(): tree.delete(x)
            for i,r in enumerate(seg_data,1):
                tree.insert("","end",values=(
                    i,r.get("work_start_time",""),r.get("work_end_time",""),
                    r.get("start_time",""),r.get("end_time",""),
                    hours_value_hhmm(r["work_hours"]),hours_value_hhmm(r["driving_hours"]),
                    r["activity_type"],r["note"]
                ))
            total_min=segments_union_minutes(seg_data,"work")
            drive_min=segments_union_minutes(seg_data,"drive")
            overlap_min=segments_overlap_minutes(seg_data,"work")
            br=gaps_summary(seg_data,pair="work")
            warning=(
                f" | ⚠ перекриття робочих частин: {minutes_hhmm(overlap_min)}"
                if overlap_min>0 else ""
            )
            summary_var.set(
                f"План роботи: {minutes_dual(total_min)} | "
                f"план керування: {minutes_dual(drive_min)} | "
                f"перерви між робочими частинами: {br or '—'}"
                + warning
            )

        def segment_form(item=None, index=None):
            sw=tk.Toplevel(win); sw.title("Частина робочої зміни"); fit_window_to_screen(sw,570,455,520,410); sw.transient(win); sw.grab_set()
            vals=item or {
                "work_start_time":"08:00","work_end_time":"09:00",
                "start_time":"08:00","end_time":"09:00",
                "activity_type":"Робота","note":""
            }
            vv={}
            defaults={
                "work_start_time":vals.get("work_start_time") or vals.get("start_time", ""),
                "work_end_time":vals.get("work_end_time") or vals.get("end_time", ""),
                "start_time":vals.get("start_time", ""), "end_time":vals.get("end_time", ""),
                "activity_type":vals.get("activity_type","Робота"), "note":vals.get("note","")
            }
            for k,val in defaults.items(): vv[k]=tk.StringVar(value=str(val or ""))

            fields=[
                ("Робочий час — початок (ГГ:ХХ)","work_start_time"),
                ("Робочий час — кінець (ГГ:ХХ)","work_end_time"),
                ("Керування — початок (ГГ:ХХ)","start_time"),
                ("Керування — кінець (ГГ:ХХ)","end_time"),
                ("Тип роботи","activity_type"),("Примітка","note")
            ]
            for i,(lbl,key) in enumerate(fields):
                ttk.Label(sw,text=lbl).grid(row=i,column=0,sticky="w",padx=10,pady=7)
                w=ttk.Combobox(sw,textvariable=vv[key],values=DAY_TYPES,state="readonly",width=36) if key=="activity_type" else ttk.Entry(sw,textvariable=vv[key],width=38)
                w.grid(row=i,column=1,padx=10,pady=7,sticky="ew")

            duration_var=tk.StringVar(value="")
            ttk.Label(sw,textvariable=duration_var,foreground="gray").grid(row=6,column=0,columnspan=2,sticky="w",padx=10,pady=(3,5))
            def refresh_durations(*_):
                try:
                    wm=duration_minutes(vv["work_start_time"].get(),vv["work_end_time"].get())
                    wtxt=minutes_hhmm(wm)
                except Exception: wtxt="—"
                ds=vv["start_time"].get().strip(); de=vv["end_time"].get().strip()
                if not ds and not de: dtxt="0:00"
                else:
                    try: dtxt=minutes_hhmm(duration_minutes(ds,de))
                    except Exception: dtxt="—"
                duration_var.set(f"Похідні тривалості: робота {wtxt}; керування {dtxt}")
            for v in (vv["work_start_time"],vv["work_end_time"],vv["start_time"],vv["end_time"]):
                v.trace_add("write",refresh_durations)
            refresh_durations()

            def copy_drive_to_work():
                vv["work_start_time"].set(vv["start_time"].get())
                vv["work_end_time"].set(vv["end_time"].get())
            def copy_work_to_drive():
                vv["start_time"].set(vv["work_start_time"].get())
                vv["end_time"].set(vv["work_end_time"].get())
            calcbar=ttk.Frame(sw); calcbar.grid(row=7,column=0,columnspan=2,sticky="w",padx=10,pady=5)
            ttk.Button(calcbar,text="Керування → робочий інтервал",command=copy_drive_to_work).pack(side="left")
            ttk.Button(calcbar,text="Робочий інтервал → керування",command=copy_work_to_drive).pack(side="left",padx=(6,0))

            def save_seg():
                ws=vv["work_start_time"].get().strip(); we=vv["work_end_time"].get().strip()
                ds=vv["start_time"].get().strip(); de=vv["end_time"].get().strip()
                try:
                    if not ws or not we:
                        raise ValueError
                    wh_min=duration_minutes(ws,we)
                    if bool(ds) != bool(de):
                        raise ValueError
                    dh_min=duration_minutes(ds,de) if ds and de else 0
                except Exception:
                    messagebox.showerror(
                        "Помилка",
                        "Для робочого часу вкажіть початок і кінець. Для керування — або обидва поля, або обидва порожні.",
                        parent=sw
                    ); return
                if ds and not interval_within(ds,de,ws,we):
                    messagebox.showerror(
                        "Помилка",
                        "Інтервал керування повинен повністю міститися в робочому інтервалі цієї частини.",
                        parent=sw
                    ); return
                data={
                    "work_start_time":ws,"work_end_time":we,
                    "start_time":ds,"end_time":de,
                    "work_hours":minutes_to_db_hours(wh_min),
                    "driving_hours":minutes_to_db_hours(dh_min),
                    "activity_type":vv["activity_type"].get().strip(),
                    "note":vv["note"].get().strip()
                }
                if index is None: seg_data.append(data)
                else: seg_data[index]=data
                redraw(); sw.destroy()
            ttk.Button(sw,text="Зберегти",command=save_seg).grid(row=8,column=1,sticky="e",padx=10,pady=12)
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
        def apply_route():
            route=route_map.get(route_var.get())
            if not route:
                messagebox.showwarning("Маршрут","Виберіть маршрут.",parent=win); return
            con=db()
            ts=con.execute(
                "SELECT * FROM route_segments WHERE route_id=? ORDER BY segment_no",(route["id"],)
            ).fetchall()
            con.close()
            if not ts:
                messagebox.showwarning(
                    "Маршрут",
                    "Для цього маршруту ще не налаштовано точний часовий сценарій. Відредагуйте його у розділі «Маршрути».",
                    parent=win
                ); return
            tv=next((v for v in vehicles if v["id"]==(route["vehicle_id"] if "vehicle_id" in route.keys() else None)),None)
            vehicle_label_var.set(self.vehicle_label(tv) if tv else (route["vehicle"] or ""))
            vehicle_var.set(route["vehicle"] or "")
            shift_var.set(route["shift_type"] or ("Розділена на частини" if len(ts)>1 else "Безперервна"))
            if "notes" in route.keys() and (route["notes"] or "").strip():
                notes_var.set(route["notes"].strip())
            # template_id лишається тільки legacy-полем старих записів.
            template_id_var.set(0)
            mode_var.set(WORK_MODE_LABELS[WORK_MODE_TACHO])
            load_segments(ts)

        def set_no_tacho_8h():
            mode_var.set(WORK_MODE_LABELS[WORK_MODE_NO_TACHO])
            type_var.set("Робота")
            template_id_var.set(0)
            route_var.set("")
            shift_var.set("Безперервна")
            seg_data.clear()
            redraw()
            summary_var.set("Без тахографа: стандартний робочий день 8:00. План керування не задається; це саме робочий час.")

        ttk.Button(apply_frame,text="Застосувати маршрут",command=apply_route).pack(side="left",padx=(8,0))
        ttk.Button(
            apply_frame,text="Без тахо — 8 год",command=set_no_tacho_8h
        ).pack(side="left",padx=(10,3))
        if old_segments:
            load_segments(old_segments)
        elif existing and ((existing["start_time"] or "") or (existing["work_start_time"] or "")):
            load_segments([{
                "start_time":existing["start_time"],"end_time":existing["end_time"],
                "work_start_time":existing["work_start_time"],"work_end_time":existing["work_end_time"],
                "work_hours":existing["work_hours"],"driving_hours":existing["driving_hours"],
                "activity_type":existing["day_type"],"note":existing["notes"]
            }])
        else:
            redraw()
        def save():
            try: work_date=datetime.strptime(day_var.get().strip(),"%d.%m.%Y").strftime("%Y-%m-%d")
            except ValueError: messagebox.showerror("Помилка","Дата має бути у форматі ДД.ММ.РРРР.",parent=win); return
            if seg_data:
                try:
                    for r in seg_data:
                        ws=r.get("work_start_time",""); we=r.get("work_end_time","")
                        ds=r.get("start_time",""); de=r.get("end_time","")
                        if not ws or not we: raise ValueError
                        r["work_hours"]=minutes_to_db_hours(duration_minutes(ws,we))
                        if bool(ds) != bool(de): raise ValueError
                        r["driving_hours"]=minutes_to_db_hours(duration_minutes(ds,de)) if ds and de else 0.0
                        if ds and not interval_within(ds,de,ws,we): raise ValueError
                except Exception:
                    messagebox.showerror("Помилка","Перевірте пари початок/кінець для роботи і керування.",parent=win); return
            mode_code=WORK_MODE_BY_LABEL.get(mode_var.get(),WORK_MODE_MANUAL)
            if mode_code==WORK_MODE_NO_TACHO:
                # Без тахографа — не вигадуємо години маршруту.
                # У табелі зберігаємо лише стандартні 8 год роботи.
                seg_data.clear()
                total_work_min=8*60
                total_drive_min=0
                start=""
                end=""
                work_start=""
                work_end=""
                type_var.set("Робота")
                template_id_var.set(0)
                shift_var.set("Безперервна")
            else:
                overlap_text=segment_overlap_message(seg_data,"work")
                if overlap_text:
                    messagebox.showerror(
                        "Перекриття робочого часу",
                        "Частини робочої зміни не можуть накладатися одна на одну.\n\n"
                        + overlap_text
                        + "\n\nВиправте часові межі перед збереженням.",
                        parent=win
                    ); return
                total_work_min=segments_union_minutes(seg_data,"work")
                total_drive_min=segments_union_minutes(seg_data,"drive")
                if total_drive_min > total_work_min:
                    messagebox.showerror(
                        "Помилка",
                        "Сумарний плановий час керування не може перевищувати плановий робочий час.",
                        parent=win
                    ); return
                drive_parts=[r for r in seg_data if r.get("start_time") and r.get("end_time")]
                start=drive_parts[0]["start_time"] if drive_parts else ""
                end=drive_parts[-1]["end_time"] if drive_parts else ""
                work_start=seg_data[0]["work_start_time"] if seg_data else ""
                work_end=seg_data[-1]["work_end_time"] if seg_data else ""

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
                driver_id,work_date,day_type,start_time,end_time,work_start_time,work_end_time,work_hours,driving_hours,
                overtime_hours,vehicle,notes,route_name,route_id,template_id,shift_type,
                vehicle_id,accounting_mode
            )
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(driver_id,work_date) DO UPDATE SET
                    day_type=excluded.day_type,
                    start_time=excluded.start_time,
                    end_time=excluded.end_time,
                    work_start_time=excluded.work_start_time,
                    work_end_time=excluded.work_end_time,
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
                    self.driver_id,work_date,type_var.get(),start,end,work_start,work_end,total_work,total_drive,
                    overtime_value,vehicle_text,notes_var.get().strip(),route_text,
                    route_id_value,template_id_var.get() or None,shift_var.get(),
                    vehicle_id,mode_code
                ))
            wl=con.execute("SELECT id FROM worklog WHERE driver_id=? AND work_date=?",(self.driver_id,work_date)).fetchone()[0]
            con.execute("DELETE FROM work_segments WHERE worklog_id=?",(wl,))
            for i,r in enumerate(seg_data,1):
                con.execute("INSERT INTO work_segments(worklog_id,segment_no,start_time,end_time,work_start_time,work_end_time,work_hours,driving_hours,activity_type,note) VALUES(?,?,?,?,?,?,?,?,?,?)",
                            (wl,i,r["start_time"],r["end_time"],r["work_start_time"],r["work_end_time"],float(r["work_hours"]),float(r["driving_hours"]),r["activity_type"],r["note"]))
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
                "work_start_time":r["work_start_time"] if "work_start_time" in r.keys() else r["start_time"],
                "work_end_time":r["work_end_time"] if "work_end_time" in r.keys() else r["end_time"],
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
        clip_segments=list(clip.get("segments",[]) or [])
        overlap_text=segment_overlap_message(clip_segments,"work")
        if overlap_text:
            messagebox.showerror(
                "Вставлення дня",
                "Скопійований день містить перекриття частин робочого часу.\n\n"
                + overlap_text
                + "\n\nСпочатку виправте вихідний день; поширювати такий конфлікт на інші дати заборонено.",
                parent=self
            ); return
        canonical_work=(
            minutes_to_db_hours(segments_union_minutes(clip_segments,"work"))
            if clip_segments else clip.get("work_hours",0)
        )
        canonical_drive=(
            minutes_to_db_hours(segments_union_minutes(clip_segments,"drive"))
            if clip_segments else clip.get("driving_hours",0)
        )
        dates=[self.work_tree.item(i,"values")[1] for i in sel]
        con=db()
        for date_text in dates:
            try: wd=datetime.strptime(date_text,"%d.%m.%Y").strftime("%Y-%m-%d")
            except ValueError: continue
            con.execute("""INSERT INTO worklog(
                driver_id,work_date,day_type,start_time,end_time,work_start_time,work_end_time,work_hours,driving_hours,
                overtime_hours,vehicle,notes,route_name,route_id,template_id,shift_type,
                vehicle_id,accounting_mode
            )
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(driver_id,work_date) DO UPDATE SET
                    day_type=excluded.day_type,start_time=excluded.start_time,end_time=excluded.end_time,
                    work_start_time=excluded.work_start_time,work_end_time=excluded.work_end_time,
                    work_hours=excluded.work_hours,driving_hours=excluded.driving_hours,
                    overtime_hours=excluded.overtime_hours,vehicle=excluded.vehicle,
                    notes=excluded.notes,route_name=excluded.route_name,route_id=excluded.route_id,
                    template_id=excluded.template_id,shift_type=excluded.shift_type,
                    vehicle_id=excluded.vehicle_id,accounting_mode=excluded.accounting_mode""",
                (
                    self.driver_id,wd,clip.get("day_type","Робота"),clip.get("start_time",""),
                    clip.get("end_time",""),clip.get("work_start_time",clip.get("start_time","")),
                    clip.get("work_end_time",clip.get("end_time","")),canonical_work,canonical_drive,
                    clip.get("overtime_hours",0),clip.get("vehicle",""),clip.get("notes",""),
                    clip.get("route_name",""),clip.get("route_id"),clip.get("template_id"),
                    clip.get("shift_type","Безперервна"),clip.get("vehicle_id"),
                    clip.get("accounting_mode",WORK_MODE_MANUAL)
                ))
            wid=con.execute("SELECT id FROM worklog WHERE driver_id=? AND work_date=?",(self.driver_id,wd)).fetchone()[0]
            con.execute("DELETE FROM work_segments WHERE worklog_id=?",(wid,))
            for i,r in enumerate(clip.get("segments",[]),1):
                con.execute("INSERT INTO work_segments(worklog_id,segment_no,start_time,end_time,work_start_time,work_end_time,work_hours,driving_hours,activity_type,note) VALUES(?,?,?,?,?,?,?,?,?,?)",
                            (wid,i,r.get("start_time",""),r.get("end_time",""),r.get("work_start_time",r.get("start_time","")),r.get("work_end_time",r.get("end_time","")),r.get("work_hours",0),r.get("driving_hours",0),r.get("activity_type","Робота"),r.get("note","")))
        con.commit(); con.close(); self.refresh_month()

    def save_work_row(self): self.edit_work_row()

    def autofill(self):
        if not self.driver_id:
            messagebox.showwarning("Увага","Спочатку виберіть водія.")
            return

        y,m=int(self.year_var.get()),int(self.month_var.get())
        driver=self.driver_by_id(self.driver_id)
        if not driver or not driver_employed_on(driver,month_dates(y,m)[-1]):
            messagebox.showwarning(
                "Увага","Водій ще не прийнятий на роботу в обраному місяці.",parent=self
            )
            return

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
            if d.weekday()<5 and driver_employed_on(driver,d):
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
        con=db(); rows=con.execute("SELECT * FROM worklog WHERE driver_id=? AND substr(work_date,1,7)=? ORDER BY work_date",(self.driver_id,f"{int(self.year_var.get()):04d}-{int(self.month_var.get()):02d}")).fetchall(); con.close()
        driver=self.driver_by_id(self.driver_id)
        if not driver:
            return []
        return [r for r in rows if driver_employed_on(driver,date.fromisoformat(r["work_date"]))]

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

        y,m=int(self.year_var.get()),int(self.month_var.get())
        if not driver_employed_on(d,month_dates(y,m)[-1]):
            messagebox.showwarning(
                "Увага","Водій ще не був прийнятий на роботу в обраному місяці.",parent=self
            )
            return

        rows=self.current_rows()
        safe_last=(d["last_name"] or "Водій").strip()
        name=f"Табель_{safe_last}_{y}_{m:02d}"
        path=OUTPUT_DIR/(name+(".xlsx" if kind=="xlsx" else ".pdf"))
        if kind=="xlsx":
            actual=write_output_file(
                lambda out: export_xlsx(d,y,m,rows,out),
                path,
                parent=self,
                kind="Excel-файл табеля",
                error_title="Помилка Excel"
            )
        else:
            actual=write_output_file(
                lambda out: export_pdf(d,y,m,rows,out),
                path,
                parent=self,
                kind="PDF табеля",
                error_title="Помилка PDF"
            )
        if actual is not None:
            messagebox.showinfo("Готово",f"Файл створено:\n{actual}")

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
        """Початок/кінець саме РОБОЧОГО дня для контролю відпочинку."""
        if row is None:
            return None, None
        d=datetime.strptime(row["work_date"], "%Y-%m-%d").date()
        pieces=[]
        if segments:
            base=datetime.combine(d,datetime.min.time())
            for item in normalized_segment_intervals(segments,"work"):
                pieces.append((
                    base+timedelta(minutes=item["start"]),
                    base+timedelta(minutes=item["end"]),
                ))
        else:
            ws=(row["work_start_time"] if "work_start_time" in row.keys() else "") or row["start_time"]
            we=(row["work_end_time"] if "work_end_time" in row.keys() else "") or row["end_time"]
            if ws and we:
                try:
                    sm=time_to_minutes(ws); em=time_to_minutes(we)
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
        """Тривалості завжди виводимо з часових меж, якщо вони є."""
        segments = segments or []
        if segments:
            work=segments_union_minutes(segments,"work")
            drive=segments_union_minutes(segments,"drive")
        else:
            ws=(row["work_start_time"] if "work_start_time" in row.keys() else "") or ""
            we=(row["work_end_time"] if "work_end_time" in row.keys() else "") or ""
            ds=(row["start_time"] or "").strip(); de=(row["end_time"] or "").strip()
            try: work=duration_minutes(ws,we) if ws and we else hours_value_to_minutes(row["work_hours"])
            except Exception: work=hours_value_to_minutes(row["work_hours"])
            try: drive=duration_minutes(ds,de) if ds and de and (row["accounting_mode"] if "accounting_mode" in row.keys() else "")!=WORK_MODE_NO_TACHO else hours_value_to_minutes(row["driving_hours"])
            except Exception: drive=hours_value_to_minutes(row["driving_hours"])
        over=hours_value_to_minutes(row["overtime_hours"])
        return work,drive,over

    def _row_internal_rest_minutes(self, segments):
        return gaps_minutes(segments)

    def _driving_break_control_for_row(self, row, segments):
        """Контроль 4:30 за КЕРУВАННЯМ із урахуванням ІНШОЇ РОБОТИ.

        Ключове правило v8.65 r2: сама відсутність керування ще не є
        перервою. Якщо між двома інтервалами керування водій продовжує
        працювати, цей час НЕ скидає накопичене керування. Для 45 хв або
        15+30 враховуємо лише реальний проміжок ПОЗА робочими інтервалами.
        """
        if not segments:
            drive=hours_value_to_minutes(row["driving_hours"])
            return {"max_continuous_drive":drive,"warnings":[],"breaks":[]}

        driving_segments=[s for s in segments if (s["start_time"] or "").strip() and (s["end_time"] or "").strip()]
        if not driving_segments:
            return {"max_continuous_drive":0,"warnings":[],"breaks":[]}

        def abs_interval(a,b,anchor=None):
            sm=time_to_minutes(a); em=time_to_minutes(b)
            if em<=sm: em+=1440
            if anchor is None:
                return sm,em
            candidates=[]
            for shift in (-2880,-1440,0,1440,2880):
                x=sm+shift; y=em+shift
                if x <= anchor <= y:
                    return x,y
                candidates.append((abs(x-anchor),x,y))
            _,x,y=min(candidates,key=lambda z:z[0])
            return x,y

        timeline=[]
        prev_drive_start=None
        for s in driving_segments:
            ds=time_to_minutes(s["start_time"]); de=time_to_minutes(s["end_time"])
            if prev_drive_start is not None:
                while ds < prev_drive_start:
                    ds += 1440
            while de <= ds:
                de += 1440
            ws,we=_segment_work_pair(s)
            try:
                was,wae=abs_interval(ws,we,ds)
            except Exception:
                # Старий/неповний запис: консервативно вважаємо, що весь
                # проміжок керування є робочим.
                was,wae=ds,de
            timeline.append((s,ds,de,was,wae))
            prev_drive_start=ds

        accumulated=0
        max_accum=0
        split15=False
        warnings=[]
        break_rows=[]

        for i,(s,ds,de,ws,we) in enumerate(timeline):
            if i>0:
                prev,pds,pde,pws,pwe=timeline[i-1]
                drive_gap=max(0,ds-pde)
                rest_gap=max(0,ws-pwe)

                status="немає кваліфікованої перерви"
                resets=False
                if rest_gap>=45:
                    status="перерва поза роботою ≥45 хв"
                    accumulated=0
                    split15=False
                    resets=True
                elif split15 and rest_gap>=30:
                    status="друга частина перерви поза роботою ≥30 хв; 15+30 виконано"
                    accumulated=0
                    split15=False
                    resets=True
                elif rest_gap>=15:
                    if not split15:
                        status="перша частина перерви поза роботою ≥15 хв"
                        split15=True
                    else:
                        status="ще одна перерва 15–29 хв; 15+30 ще не завершено"
                elif drive_gap>=15 and rest_gap<15:
                    status=f"без керування {minutes_hhmm(drive_gap)}, але поза роботою лише {minutes_hhmm(rest_gap)} — це не перерва 340"
                else:
                    status=f"поза роботою {minutes_hhmm(rest_gap)} (<15 хв)"

                pws_txt,pwe_txt=_segment_work_pair(prev)
                ws_txt,we_txt=_segment_work_pair(s)
                break_rows.append({
                    "after":pwe_txt,
                    "before":ws_txt,
                    "minutes":rest_gap,
                    "driving_gap_minutes":drive_gap,
                    "status":status,
                    "resets":resets,
                })

            drive_min=max(0,de-ds)
            accumulated+=drive_min
            max_accum=max(max_accum,accumulated)

            if accumulated>270:
                warnings.append(
                    f"{row['work_date']}: накопичено {minutes_hhmm(accumulated)} керування "
                    f"до/в межах {s['start_time']}–{s['end_time']} без завершеної "
                    "перерви поза роботою 45 хв або 15+30."
                )

        return {
            "max_continuous_drive":max_accum,
            "warnings":warnings,
            "breaks":break_rows,
        }

    def calculate_work_analysis(self):
        """Попередній автоматичний контроль за чинною моделлю Положення №340.

        v8.65 принципово розділяє ПЛАНОВИЙ час керування та ПЛАНОВИЙ
        робочий час. Тахографічні дані надалі мають бути окремим фактичним
        шаром і не повинні перезаписувати план. Розрахунки виконуються у
        хвилинах, а не у сотих частках години.
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

            if drive_min > work_min and work_min >= 0:
                warnings.append(
                    f"{d.strftime('%d.%m.%Y')}: план керування {minutes_hhmm(drive_min)} "
                    f"перевищує план робочого часу {minutes_hhmm(work_min)} — перевірити графік."
                )

            if drive_min>600:
                warnings.append(f"{d.strftime('%d.%m.%Y')}: керування {minutes_hhmm(drive_min)} — понад 10:00.")
            elif drive_min>540:
                extended_by_week[monday]=extended_by_week.get(monday,0)+1
                info.append(f"{d.strftime('%d.%m.%Y')}: подовжене керування {minutes_hhmm(drive_min)} (понад 9:00).")

            night=any(
                self._segment_is_work(s["activity_type"]) and
                self._segment_overlaps_night(*_segment_work_pair(s))
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
                ws,we=_segment_work_pair(s)
                try:
                    dur=duration_minutes(ws,we)
                except Exception:
                    continue
                if dur>360:
                    warnings.append(
                        f"{d.strftime('%d.%m.%Y')}: безперервний робочий відрізок "
                        f"{ws}–{we} = {minutes_hhmm(dur)} (>6:00); перевірити перерву."
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

        # r9.3: compact day-by-day dashboard for the analysis window.
        # It deliberately uses the same canonical driver_day_view as the
        # driver timesheet and graphical schedule.
        month_by_date={r["work_date"]:r for r in month_rows}
        absence_by_date={}
        override_types=set(globals().get("TAXO_NONWORK_OVERRIDE_TYPES",set()) or ())
        if override_types:
            try:
                employee=con.execute(
                    "SELECT id FROM employees WHERE driver_id=? ORDER BY active DESC,id LIMIT 1",
                    (self.driver_id,)
                ).fetchone()
                if employee:
                    entries=con.execute(
                        """SELECT work_date,day_type FROM employee_time_entries
                           WHERE employee_id=? AND work_date BETWEEN ? AND ?""",
                        (employee["id"],month_start.isoformat(),month_end.isoformat())
                    ).fetchall()
                    for entry in entries:
                        if str(entry["day_type"] or "") in override_types:
                            absence_by_date[entry["work_date"]]=entry["day_type"]
            except Exception:
                # Older/minimal databases may not yet expose personnel tables.
                absence_by_date={}

        day_rows=[]
        for day in month_dates(y,m):
            row=month_by_date.get(day.isoformat())
            segs=seg_map.get(row["id"],[]) if row else []
            override=absence_by_date.get(day.isoformat())
            state=driver_day_view(
                day,row,segs,
                day_type_override=override,
                suppress_plan=bool(override),
            )

            issues=[]
            if state["work_overlap_minutes"]>0:
                issues.append(f"перекриття {minutes_hhmm(state['work_overlap_minutes'])}")
            if state["driving_overlap_minutes"]>0:
                issues.append(f"керування перекрито {minutes_hhmm(state['driving_overlap_minutes'])}")
            if state["driving_minutes"]>state["work_minutes"] and state["driving_minutes"]>0:
                issues.append("керування > робочого часу")
            if state["driving_minutes"]>600:
                issues.append("керування >10:00")
            elif state["driving_minutes"]>540:
                issues.append("керування >9:00")

            break_ctl=self._driving_break_control_for_row(row,segs) if row else {
                "warnings":[],"max_continuous_drive":0
            }
            if break_ctl.get("warnings"):
                issues.append("контроль 4:30")
            if break_ctl.get("max_continuous_drive",0)>270:
                issues.append(
                    f"без завершеної перерви {minutes_hhmm(break_ctl['max_continuous_drive'])}"
                )

            result="; ".join(dict.fromkeys(issues))
            if not result:
                if override:
                    result="Відсутність"
                elif state["work_minutes"]>0:
                    result="Норма"
                elif state["status_label"]:
                    result=state["status_label"]
                else:
                    result="—"

            day_rows.append({
                "date":day,
                "weekday":["Пн","Вт","Ср","Чт","Пт","Сб","Нд"][day.weekday()],
                "day_type":state["day_type"],
                "schedule":state["schedule"] or state["status_label"] or "—",
                "breaks":state["breaks"] or "—",
                "work_min":state["work_minutes"],
                "drive_min":state["driving_minutes"],
                "over_min":state["overtime_minutes"],
                "route":(
                    (row["route_name"] if row is not None and "route_name" in row.keys() else "")
                    or "—"
                ),
                "result":result,
                "has_issue":bool(issues),
                "worklog_id":row["id"] if row else None,
            })

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
            "day_rows":day_rows,
        }

    def open_work_month_detail_pdf(self, parent=None):
        """Generate and open the detailed monthly PDF for the selected driver."""
        if not self.driver_id:
            messagebox.showwarning("Деталізація","Спочатку виберіть водія.",parent=parent or self)
            return
        y,m=int(self.year_var.get()),int(self.month_var.get())
        driver=self.driver_by_id(self.driver_id)
        if driver is None:
            messagebox.showerror("Деталізація","Водія не знайдено.",parent=parent or self)
            return
        con=db()
        rows=con.execute(
            """SELECT * FROM worklog
               WHERE driver_id=? AND work_date BETWEEN ? AND ?
               ORDER BY work_date""",
            (self.driver_id,date(y,m,1).isoformat(),month_dates(y,m)[-1].isoformat())
        ).fetchall()
        con.close()

        driver_name=self.driver_full_name(driver)
        safe="".join(ch if ch.isalnum() or ch in " _-" else "_" for ch in driver_name)
        safe=safe.strip().replace(" ","_") or f"driver_{self.driver_id}"
        target=OUTPUT_DIR / f"Деталізація_{safe}_{y}_{m:02d}.pdf"
        actual=write_output_file(
            lambda out: export_pdf(driver,y,m,rows,out),
            target,
            parent=parent or self,
            kind="PDF деталізації робочого часу",
            error_title="Помилка деталізації"
        )
        if actual is not None:
            open_external(actual)

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
        fit_window_to_screen(win,1220,790,900,580)
        win.transient(self)

        head=ttk.Frame(win,padding=10)
        head.pack(fill="x")

        title_frame=ttk.Frame(head)
        title_frame.pack(fill="x")
        ttk.Label(
            title_frame,
            text=f"{driver_name} — {month_name_ua(data['month'])} {data['year']}",
            font=("TkDefaultFont",12,"bold")
        ).pack(side="left")

        def save_pdf():
            safe="".join(ch if ch.isalnum() or ch in " _-" else "_" for ch in driver_name).strip().replace(" ","_")
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
            actual=write_output_file(
                lambda out: export_work_analysis_pdf(data,driver_name,out),
                path,
                parent=win,
                kind="PDF аналізу №340",
                error_title="Помилка PDF"
            )
            if actual is not None:
                messagebox.showinfo("PDF",f"Збережено:\n{actual}",parent=win)

        ttk.Button(
            title_frame,text="Відкрити деталізацію",
            command=lambda:self.open_work_month_detail_pdf(win)
        ).pack(side="right",padx=(8,0))
        ttk.Button(title_frame,text="Зберегти PDF контролю",command=save_pdf).pack(side="right",padx=(8,0))

        # Compact dashboard: the most useful month figures remain visible on
        # both notebook pages instead of being buried in a long sentence.
        cards=ttk.Frame(head)
        cards.pack(fill="x",pady=(8,4))
        metrics=[
            ("Робочих днів",str(data["work_days"])),
            ("Робота, план",minutes_hhmm(data["total_work_min"])),
            ("Керування, план",minutes_hhmm(data["total_drive_min"])),
            ("Надурочні",minutes_hhmm(data["total_over_min"])),
            ("Середнє за 4 міс.",minutes_hhmm(data["avg4_min"])+"/тиж."),
            ("Зауважень",str(len(data.get("warnings") or []))),
        ]
        for col,(label,value) in enumerate(metrics):
            box=ttk.LabelFrame(cards,text=label,padding=(8,5))
            box.grid(row=0,column=col,sticky="nsew",padx=3)
            ttk.Label(box,text=value,font=("TkDefaultFont",10,"bold")).pack()
            cards.columnconfigure(col,weight=1)

        ttk.Label(
            head,
            text=f"Профіль контролю: {data.get('transport_profile',DEFAULT_TRANSPORT_PROFILE)}",
            foreground="gray"
        ).pack(anchor="w",pady=(2,0))

        notebook=ttk.Notebook(win)
        notebook.pack(fill="both",expand=True,padx=10,pady=(2,10))

        # Day-by-day table: quick operational view.
        day_tab=ttk.Frame(notebook)
        notebook.add(day_tab,text="Дні місяця")
        day_tools=ttk.Frame(day_tab,padding=(6,6,6,2))
        day_tools.pack(fill="x")
        ttk.Label(
            day_tools,
            text="Подвійний клік — відкрити день для редагування.",
            foreground="gray"
        ).pack(side="left")

        day_frame=ttk.Frame(day_tab)
        day_frame.pack(fill="both",expand=True,padx=6,pady=6)
        day_frame.rowconfigure(0,weight=1); day_frame.columnconfigure(0,weight=1)
        cols=("date","weekday","type","schedule","breaks","work","drive","over","route","result")
        tree=ttk.Treeview(day_frame,columns=cols,show="headings",selectmode="browse")
        heads={
            "date":"Дата","weekday":"День","type":"Вид","schedule":"Графік / частини",
            "breaks":"Перерви","work":"Робота","drive":"Керування","over":"Надур.",
            "route":"Маршрут","result":"Результат"
        }
        widths={
            "date":90,"weekday":50,"type":100,"schedule":260,"breaks":150,
            "work":75,"drive":80,"over":70,"route":210,"result":230
        }
        for key in cols:
            tree.heading(key,text=heads[key])
            tree.column(key,width=widths[key],anchor="w",stretch=(key in {"schedule","route","result"}))
        ybar=ttk.Scrollbar(day_frame,orient="vertical",command=tree.yview)
        xbar=ttk.Scrollbar(day_frame,orient="horizontal",command=tree.xview)
        tree.configure(yscrollcommand=ybar.set,xscrollcommand=xbar.set)
        tree.grid(row=0,column=0,sticky="nsew")
        ybar.grid(row=0,column=1,sticky="ns")
        xbar.grid(row=1,column=0,sticky="ew")
        tree.tag_configure("issue",background="#FDE8E8",foreground="#8A1C1C")
        tree.tag_configure("absence",background="#FFF4CC")
        tree.tag_configure("weekend",background="#F3F4F6")
        tree.tag_configure("ok",background="#EAF7EA")

        row_by_iid={}
        for row in data.get("day_rows",[]):
            tag=(
                "issue" if row["has_issue"] else
                "absence" if row["result"]=="Відсутність" else
                "ok" if row["work_min"]>0 else
                "weekend"
            )
            iid=tree.insert("","end",values=(
                row["date"].strftime("%d.%m.%Y"),row["weekday"],row["day_type"],
                row["schedule"],row["breaks"],minutes_hhmm(row["work_min"]),
                minutes_hhmm(row["drive_min"]),minutes_hhmm(row["over_min"]),
                row["route"],row["result"]
            ),tags=(tag,))
            row_by_iid[iid]=row

        def edit_selected_day(_event=None):
            sel=tree.selection()
            if not sel:
                messagebox.showinfo("Підсумки","Виберіть день у таблиці.",parent=win)
                return
            row=row_by_iid.get(sel[0])
            if row is None:
                return
            self.open_schedule_worklog(self.driver_id,row["date"])

        ttk.Button(day_tools,text="Редагувати вибраний день",command=edit_selected_day).pack(side="right",padx=3)
        tree.bind("<Double-1>",edit_selected_day)

        # Full explanatory protocol.
        control_tab=ttk.Frame(notebook)
        notebook.add(control_tab,text="Контроль №340")
        legend=ttk.Frame(control_tab,padding=(8,6,8,2))
        legend.pack(fill="x")
        tk.Label(legend,text="  Норма  ",bg="#E6F4EA",fg="#1B5E20").pack(side="left",padx=(0,5))
        tk.Label(legend,text="  Увага  ",bg="#FFF4CC",fg="#7A4A00").pack(side="left",padx=5)
        tk.Label(legend,text="  Помилка / перевищення  ",bg="#FDE8E8",fg="#8A1C1C").pack(side="left",padx=5)
        tk.Label(legend,text="  Інформація  ",bg="#EAF2FF",fg="#174EA6").pack(side="left",padx=5)

        body=ttk.Frame(control_tab)
        body.pack(fill="both",expand=True,padx=6,pady=(2,6))
        txt=tk.Text(body,wrap="word",padx=8,pady=8)
        scr=ttk.Scrollbar(body,orient="vertical",command=txt.yview)
        txt.configure(yscrollcommand=scr.set)
        txt.grid(row=0,column=0,sticky="nsew")
        scr.grid(row=0,column=1,sticky="ns")
        body.rowconfigure(0,weight=1)
        body.columnconfigure(0,weight=1)

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

        if data.get("warnings"):
            notebook.select(control_tab)


    def build_route_catalog(self):
        top=ttk.Frame(self.tab_route_catalog); top.pack(fill="x",padx=10,pady=8)
        ttk.Button(top,text="Новий маршрут",command=self.route_catalog_form).pack(side="left",padx=4)
        ttk.Button(top,text="Редагувати",command=self.edit_route_catalog).pack(side="left",padx=4)
        ttk.Button(top,text="Вимкнути",command=self.delete_route_catalog).pack(side="left",padx=4)
        ttk.Button(top,text="Оновити",command=self.load_route_catalog).pack(side="left",padx=4)
        ttk.Label(
            self.tab_route_catalog,
            text=(
                "Один маршрут = один точний часовий сценарій. Номер / назва використовується у списках; "
                "автомобіль, робочі інтервали та керування зберігаються всередині маршруту."
            ),
            foreground="gray",wraplength=1050,justify="left"
        ).pack(anchor="w",padx=12,pady=(0,6))
        cols=("id","label","vehicle","distance","shift","segments","description","active")
        self.route_catalog_tree=ttk.Treeview(self.tab_route_catalog,columns=cols,show="headings",height=25)
        heads={
            "id":"ID","label":"№ / назва","vehicle":"Автомобіль","distance":"План, км","shift":"Тип зміни",
            "segments":"Точний часовий сценарій","description":"Опис / примітка","active":"Статус"
        }
        widths={"id":45,"label":230,"vehicle":150,"distance":80,"shift":145,"segments":410,"description":280,"active":80}
        for c in cols:
            self.route_catalog_tree.heading(c,text=heads[c])
            self.route_catalog_tree.column(c,width=widths[c],anchor="w")
        routecat_y=ttk.Scrollbar(self.tab_route_catalog,orient="vertical",command=self.route_catalog_tree.yview)
        routecat_x=ttk.Scrollbar(self.tab_route_catalog,orient="horizontal",command=self.route_catalog_tree.xview)
        self.route_catalog_tree.configure(yscrollcommand=routecat_y.set,xscrollcommand=routecat_x.set)
        routecat_x.pack(side="bottom",fill="x",padx=10,pady=(0,5))
        routecat_y.pack(side="right",fill="y",pady=5)
        self.route_catalog_tree.pack(side="left",fill="both",expand=True,padx=(10,0),pady=5)
        self.route_catalog_tree.bind("<Double-1>",lambda _event:self.edit_route_catalog())
        self.route_catalog_tree.bind("<Return>",lambda _event:self.edit_route_catalog())
        self.load_route_catalog()

    def route_label(self,r):
        if not r:
            return ""
        code=(r["code"] or "").strip()
        name=(r["name"] or "").strip()
        return " / ".join(x for x in (code,name) if x)

    def route_segments(self, route_id):
        if not route_id:
            return []
        con=db()
        rows=con.execute(
            "SELECT * FROM route_segments WHERE route_id=? ORDER BY segment_no", (route_id,)
        ).fetchall()
        con.close()
        return rows

    def route_stops(self, route_id):
        if not route_id:
            return []
        con=db()
        rows=con.execute(
            "SELECT * FROM route_stops WHERE route_id=? ORDER BY direction, stop_no", (route_id,)
        ).fetchall()
        con.close()
        return rows

    def load_route_catalog(self):
        if not hasattr(self,"route_catalog_tree"):
            return
        for x in self.route_catalog_tree.get_children():
            self.route_catalog_tree.delete(x)
        con=db()
        rows=con.execute("SELECT * FROM routes ORDER BY active DESC, code, name").fetchall()
        for r in rows:
            segs=con.execute(
                "SELECT * FROM route_segments WHERE route_id=? ORDER BY segment_no", (r["id"],)
            ).fetchall()
            stop_counts={x["direction"]:x["n"] for x in con.execute(
                "SELECT direction,COUNT(*) AS n FROM route_stops WHERE route_id=? GROUP BY direction",(r["id"],)
            ).fetchall()}
            summary=" / ".join(
                f"роб. {(sg['work_start_time'] or sg['start_time'])}-{(sg['work_end_time'] or sg['end_time'])}; "
                f"кер. {sg['start_time'] or '—'}-{sg['end_time'] or '—'}"
                for sg in segs
            ) or "— не налаштовано —"
            route_plan=(f"зупинки: прямий {stop_counts.get('outbound',0)}, "
                        f"зворотний {stop_counts.get('return',0)}")
            description="; ".join(x for x in ((r["description"] or "").strip(), route_plan, (r["notes"] or "").strip()) if x)
            self.route_catalog_tree.insert("","end",values=(
                r["id"],self.route_label(r),r["vehicle"],r["planned_distance_km"] or "—",r["shift_type"],summary,description,
                "Так" if r["active"] else "Ні"
            ))
        con.close()

    def selected_route_catalog(self):
        sel=self.route_catalog_tree.selection()
        if not sel:
            return None
        rid=int(self.route_catalog_tree.item(sel[0],"values")[0])
        con=db()
        route=con.execute("SELECT * FROM routes WHERE id=?",(rid,)).fetchone()
        segs=con.execute("SELECT * FROM route_segments WHERE route_id=? ORDER BY segment_no",(rid,)).fetchall()
        stops=con.execute("SELECT * FROM route_stops WHERE route_id=? ORDER BY direction,stop_no",(rid,)).fetchall()
        con.close()
        return (route,segs,stops) if route else None

    def route_catalog_form(self, existing=None):
        route=existing[0] if existing else None
        existing_segments=existing[1] if existing else []
        existing_stops=existing[2] if existing and len(existing)>2 else []
        win=tk.Toplevel(self)
        win.title("Маршрут")
        fit_window_to_screen(win,1100,650,850,520)
        win.transient(self); win.grab_set()
        win.columnconfigure(1,weight=1)
        win.rowconfigure(9,weight=1)

        con=db()
        vehicles=con.execute("SELECT * FROM vehicles WHERE active=1 ORDER BY name,plate").fetchall()
        con.close()
        vehicle_map={self.vehicle_label(v):v for v in vehicles}
        existing_vid=(route["vehicle_id"] if route and "vehicle_id" in route.keys() else None)
        vehicle_default=next(
            (self.vehicle_label(v) for v in vehicles if v["id"]==existing_vid),
            (route["vehicle"] if route else "") or ""
        )

        vv={
            "code":tk.StringVar(value=(route["code"] if route else "") or ""),
            "name":tk.StringVar(value=(route["name"] if route else "") or ""),
            "description":tk.StringVar(value=(route["description"] if route else "") or ""),
            "notes":tk.StringVar(value=(route["notes"] if route and "notes" in route.keys() else "") or ""),
            "shift_type":tk.StringVar(value=(route["shift_type"] if route and "shift_type" in route.keys() else "Безперервна") or "Безперервна"),
            "vehicle":tk.StringVar(value=vehicle_default),
            "start_location":tk.StringVar(value=(route["start_location"] if route and "start_location" in route.keys() else "") or ""),
            "end_location":tk.StringVar(value=(route["end_location"] if route and "end_location" in route.keys() else "") or ""),
            "start_direction":tk.StringVar(value=(route["start_direction"] if route and "start_direction" in route.keys() else "outbound") or "outbound"),
            "start_day_offset":tk.StringVar(value=str(route["start_day_offset"] if route and "start_day_offset" in route.keys() else 0)),
            "end_day_offset":tk.StringVar(value=str(route["end_day_offset"] if route and "end_day_offset" in route.keys() else 0)),
            "planned_distance_km":tk.StringVar(value=str(route["planned_distance_km"] or "") if route and "planned_distance_km" in route.keys() else ""),
        }
        active=tk.BooleanVar(value=bool(route["active"]) if route else True)
        stop_data={"outbound":[],"return":[]}
        for stop in existing_stops:
            stop_data[stop["direction"]].append({
                "stop_name":stop["stop_name"],"arrival_time":stop["arrival_time"] or "",
                "departure_time":stop["departure_time"] or "","note":stop["note"] or "",
                "day_offset":int(stop["day_offset"] or 0) if "day_offset" in stop.keys() else 0,
                "arrival_day_offset":int(stop["arrival_day_offset"] or 0) if "arrival_day_offset" in stop.keys() else int(stop["day_offset"] or 0),
                "departure_day_offset":int(stop["departure_day_offset"] or 0) if "departure_day_offset" in stop.keys() else int(stop["day_offset"] or 0),
                "point_type":(stop["point_type"] or "Зупинка") if "point_type" in stop.keys() else "Зупинка",
            })

        fields=[
            ("Код / № маршруту","code"),
            ("Назва маршруту","name"),
            ("Опис / напрямок","description"),
            ("Примітка","notes"),
        ]
        for row,(label,key) in enumerate(fields):
            ttk.Label(win,text=label).grid(row=row,column=0,sticky="w",padx=10,pady=5)
            ttk.Entry(win,textvariable=vv[key],width=65).grid(row=row,column=1,columnspan=3,sticky="ew",padx=10,pady=5)

        ttk.Label(win,text="Точка початку роботи").grid(row=4,column=0,sticky="w",padx=10,pady=5)
        ttk.Entry(win,textvariable=vv["start_location"],width=38).grid(row=4,column=1,sticky="ew",padx=10,pady=5)
        ttk.Label(win,text="Напрямок / день").grid(row=4,column=2,sticky="e",padx=(10,4),pady=5)
        start_box=ttk.Frame(win); start_box.grid(row=4,column=3,sticky="ew",padx=(4,10),pady=5)
        ttk.Combobox(start_box,textvariable=vv["start_direction"],values=("outbound","return"),state="readonly",width=11).pack(side="left")
        ttk.Label(start_box,text="D+").pack(side="left",padx=(6,1))
        ttk.Spinbox(start_box,textvariable=vv["start_day_offset"],from_=0,to=7,width=4).pack(side="left")

        ttk.Label(win,text="Точка завершення роботи").grid(row=5,column=0,sticky="w",padx=10,pady=5)
        ttk.Entry(win,textvariable=vv["end_location"],width=38).grid(row=5,column=1,sticky="ew",padx=10,pady=5)
        ttk.Label(win,text="День завершення D+").grid(row=5,column=2,sticky="e",padx=(10,4),pady=5)
        ttk.Spinbox(win,textvariable=vv["end_day_offset"],from_=0,to=7,width=5).grid(row=5,column=3,sticky="w",padx=(4,10),pady=5)

        ttk.Label(win,text="Автомобіль за замовчуванням").grid(row=6,column=0,sticky="w",padx=10,pady=5)
        ttk.Combobox(
            win,textvariable=vv["vehicle"],values=list(vehicle_map.keys()),state="readonly",width=40
        ).grid(row=6,column=1,sticky="ew",padx=10,pady=5)
        ttk.Label(win,text="Тип зміни").grid(row=6,column=2,sticky="e",padx=(10,4),pady=5)
        ttk.Combobox(
            win,textvariable=vv["shift_type"],values=["Безперервна","Розділена на частини"],
            state="readonly",width=24
        ).grid(row=6,column=3,sticky="w",padx=(4,10),pady=5)
        ttk.Label(win,text="Плановий пробіг за повним графіком, км").grid(row=7,column=0,sticky="w",padx=10,pady=5)
        ttk.Entry(win,textvariable=vv["planned_distance_km"],width=18).grid(row=7,column=1,sticky="w",padx=10,pady=5)
        ttk.Checkbutton(win,text="Активний маршрут",variable=active).grid(row=7,column=2,sticky="e",padx=10,pady=(3,5))
        stops_summary=tk.StringVar()
        def refresh_stops_summary():
            stops_summary.set(f"Графік зупинок: прямий {len(stop_data['outbound'])}, зворотний {len(stop_data['return'])}")

        def edit_stop_schedule():
            sw=tk.Toplevel(win); sw.title("Графік руху маршруту — зворотна сторона шляхівки")
            fit_window_to_screen(sw,1080,650,850,520); sw.transient(win); sw.grab_set()
            ttk.Label(
                sw,text=("До 15 рядків у кожному напрямку. Планові прибуття/відправлення друкуються на звороті; "
                         "фактичний час, підпис і особливі відмітки залишаються порожніми."),
                foreground="gray",wraplength=1020,justify="left"
            ).pack(fill="x",padx=10,pady=(10,5))
            body=ttk.Frame(sw); body.pack(fill="both",expand=True,padx=8,pady=5)
            body.columnconfigure(0,weight=1); body.columnconfigure(1,weight=1); body.rowconfigure(0,weight=1)
            trees={}

            def redraw_stops(direction):
                tree=trees[direction]
                for item in tree.get_children(): tree.delete(item)
                for i,item in enumerate(stop_data[direction],1):
                    arrive=(f"D+{item['arrival_day_offset']} {item['arrival_time']}" if item["arrival_time"] else "")
                    depart=(f"D+{item['departure_day_offset']} {item['departure_time']}" if item["departure_time"] else "")
                    tree.insert("","end",values=(i,item["point_type"],item["stop_name"],arrive,depart,item["note"]))

            def route_days():
                days=[]
                for direction in ("outbound","return"):
                    for item in stop_data[direction]:
                        if item.get("arrival_time"): days.append(int(item.get("arrival_day_offset",0)))
                        if item.get("departure_time"): days.append(int(item.get("departure_day_offset",0)))
                return days

            def sync_route_bounds(force=True):
                first_direction=vv["start_direction"].get() or "outbound"
                last_direction="return" if first_direction=="outbound" else "outbound"
                first_rows=stop_data[first_direction]
                last_rows=stop_data[last_direction] or first_rows
                if first_rows and (force or not vv["start_location"].get().strip()):
                    vv["start_location"].set(first_rows[0]["stop_name"])
                if last_rows and (force or not vv["end_location"].get().strip()):
                    vv["end_location"].set(last_rows[-1]["stop_name"])
                days=route_days()
                if days:
                    vv["start_day_offset"].set(str(min(days)))
                    vv["end_day_offset"].set(str(max(days)))

            def quick_fill(direction):
                qw=tk.Toplevel(sw)
                qw.title("Швидке заповнення — "+("прямий напрямок" if direction=="outbound" else "зворотний напрямок"))
                fit_window_to_screen(qw,850,600,680,470); qw.transient(sw); qw.grab_set()
                ttk.Label(
                    qw,
                    text=("Один рядок — одна точка. Вставляйте з Excel або використовуйте «;». "
                          "Колонки: Назва | Прибуття | Відправлення | Тип | Примітка.\n"
                          "D+ вводити не потрібно: після 23:55 → 00:40 програма поставить D+1 сама. "
                          "Порожній час позначайте «-»."),
                    wraplength=800,justify="left",foreground="gray"
                ).pack(fill="x",padx=10,pady=(10,6))
                host=ttk.Frame(qw); host.pack(fill="both",expand=True,padx=10,pady=5)
                host.rowconfigure(0,weight=1); host.columnconfigure(0,weight=1)
                editor=tk.Text(host,wrap="none",undo=True,font=("Consolas",10))
                ybar=ttk.Scrollbar(host,orient="vertical",command=editor.yview)
                xbar=ttk.Scrollbar(host,orient="horizontal",command=editor.xview)
                editor.configure(yscrollcommand=ybar.set,xscrollcommand=xbar.set)
                editor.grid(row=0,column=0,sticky="nsew"); ybar.grid(row=0,column=1,sticky="ns"); xbar.grid(row=1,column=0,sticky="ew")
                editor.insert("1.0",route_schedule_to_text(stop_data[direction]))
                buttons=ttk.Frame(qw); buttons.pack(fill="x",padx=10,pady=(4,10))
                ttk.Button(
                    buttons,text="Вставити приклад",
                    command=lambda:(
                        editor.delete("1.0","end"),
                        editor.insert("1.0","Львів АС-2;-;22:40;Автостанція;Початок\nСтрий АС;23:55;00:40;Автостанція;\nУжгород АС;05:35;-;Нічліг;")
                    )
                ).pack(side="left")
                def apply_quick():
                    try:
                        start_day=int(vv["start_day_offset"].get() or 0)
                        first_direction=vv["start_direction"].get() or "outbound"
                        previous_absolute=None
                        if direction!=first_direction and stop_data[first_direction]:
                            source_moments=[
                                int(item.get(key,0))*1440+time_to_minutes(item[time_key])
                                for item in stop_data[first_direction]
                                for key,time_key in (("arrival_day_offset","arrival_time"),("departure_day_offset","departure_time"))
                                if item.get(time_key)
                            ]
                            if source_moments:
                                previous_absolute=max(source_moments); start_day=previous_absolute//1440
                        parsed=parse_route_schedule_text(editor.get("1.0","end-1c"),start_day,previous_absolute)
                    except ValueError as exc:
                        messagebox.showerror("Швидке заповнення",str(exc),parent=qw); return
                    stop_data[direction]=parsed
                    redraw_stops(direction); refresh_stops_summary(); sync_route_bounds(force=False)
                    qw.destroy()
                ttk.Button(buttons,text="Замінити графік цим списком",command=apply_quick).pack(side="right")

            def quick_fill_both():
                qw=tk.Toplevel(sw); qw.title("Швидке заповнення маршруту")
                fit_window_to_screen(qw,1080,650,850,520); qw.transient(sw); qw.grab_set()
                ttk.Label(
                    qw,
                    text=("Найпростіше: скопіюйте з Excel дві колонки — Точка | Час. "
                          "Програма сама поставить перший час як відправлення, останній як прибуття і визначить D+ після півночі.\n"
                          "Якщо потрібна стоянка, використайте три колонки: Точка | Прибуття | Відправлення."),
                    wraplength=1020,justify="left",foreground="gray"
                ).pack(fill="x",padx=10,pady=(10,6))
                body2=ttk.Frame(qw); body2.pack(fill="both",expand=True,padx=8,pady=5)
                body2.columnconfigure(0,weight=1); body2.columnconfigure(1,weight=1); body2.rowconfigure(0,weight=1)
                editors={}
                for col,(direction,title) in enumerate((("outbound","Прямий напрямок"),("return","Зворотний напрямок"))):
                    box=ttk.LabelFrame(body2,text=title); box.grid(row=0,column=col,sticky="nsew",padx=5)
                    box.rowconfigure(0,weight=1); box.columnconfigure(0,weight=1)
                    editor=tk.Text(box,wrap="none",undo=True,font=("Consolas",10))
                    ybar=ttk.Scrollbar(box,orient="vertical",command=editor.yview)
                    xbar=ttk.Scrollbar(box,orient="horizontal",command=editor.xview)
                    editor.configure(yscrollcommand=ybar.set,xscrollcommand=xbar.set)
                    editor.grid(row=0,column=0,sticky="nsew"); ybar.grid(row=0,column=1,sticky="ns"); xbar.grid(row=1,column=0,sticky="ew")
                    editor.insert("1.0",route_schedule_to_text(stop_data[direction]))
                    editors[direction]=editor
                buttons=ttk.Frame(qw); buttons.pack(fill="x",padx=10,pady=(4,10))
                def insert_simple_example():
                    examples={
                        "outbound":"Львів АС-2\t22:40\nСтрий АС\t23:55\nУжгород АС\t05:35",
                        "return":"Ужгород АС\t07:10\nСтрий АС\t12:15\nЛьвів АС-2\t14:20",
                    }
                    for direction,editor in editors.items():
                        editor.delete("1.0","end"); editor.insert("1.0",examples[direction])
                ttk.Button(buttons,text="Показати простий приклад",command=insert_simple_example).pack(side="left")
                def apply_both():
                    try:
                        start_day=int(vv["start_day_offset"].get() or 0)
                        outbound=parse_route_schedule_text(editors["outbound"].get("1.0","end-1c"),start_day)
                        outbound_moments=[
                            int(item.get(key,0))*1440+time_to_minutes(item[time_key]) for item in outbound
                            for key,time_key in (("arrival_day_offset","arrival_time"),("departure_day_offset","departure_time"))
                            if item.get(time_key)
                        ]
                        previous_absolute=max(outbound_moments) if outbound_moments else None
                        return_start=previous_absolute//1440 if previous_absolute is not None else start_day
                        returning=parse_route_schedule_text(editors["return"].get("1.0","end-1c"),return_start,previous_absolute)
                    except ValueError as exc:
                        messagebox.showerror("Швидке заповнення",str(exc),parent=qw); return
                    stop_data["outbound"]=outbound; stop_data["return"]=returning
                    redraw_stops("outbound"); redraw_stops("return")
                    refresh_stops_summary(); sync_route_bounds(force=True); qw.destroy()
                ttk.Button(buttons,text="Зберегти обидва напрямки",command=apply_both).pack(side="right")

            def copy_reverse_names():
                if not stop_data["outbound"]:
                    messagebox.showinfo("Зворотний напрямок","Спочатку заповніть прямий напрямок.",parent=sw); return
                if stop_data["return"] and not messagebox.askyesno(
                    "Зворотний напрямок","Замінити наявні точки зворотного напрямку?",parent=sw
                ):
                    return
                days=route_days()
                seed=max(days) if days else int(vv["start_day_offset"].get() or 0)
                stop_data["return"]=[
                    {
                        "stop_name":item["stop_name"],"arrival_time":"","departure_time":"",
                        "note":"","day_offset":seed,"arrival_day_offset":seed,
                        "departure_day_offset":seed,"point_type":item.get("point_type","Зупинка"),
                    }
                    for item in reversed(stop_data["outbound"])
                ]
                redraw_stops("return"); refresh_stops_summary(); sync_route_bounds(force=False)

            def stop_form(direction,index=None):
                if index is None and len(stop_data[direction])>=15:
                    messagebox.showwarning("Графік маршруту","У формі № 1-АП передбачено 15 рядків на напрямок.",parent=sw); return
                base=stop_data[direction][index] if index is not None else {"stop_name":"","arrival_time":"","departure_time":"","note":"","arrival_day_offset":0,"departure_day_offset":0,"point_type":"Зупинка"}
                fw=tk.Toplevel(sw); fw.title("Точка маршруту"); fit_window_to_screen(fw,600,430,530,380); fw.transient(sw); fw.grab_set()
                values={k:tk.StringVar(value=str(base.get(k,""))) for k in ("stop_name","point_type","arrival_day_offset","arrival_time","departure_day_offset","departure_time","note")}
                for row,(key,label) in enumerate((("stop_name","Назва точки / автостанції"),("point_type","Тип точки"),("arrival_day_offset","Прибуття, день D+"),("arrival_time","Прибуття за графіком"),("departure_day_offset","Відправлення, день D+"),("departure_time","Відправлення за графіком"),("note","Примітка"))):
                    ttk.Label(fw,text=label).grid(row=row,column=0,sticky="w",padx=10,pady=7)
                    widget=(ttk.Combobox(fw,textvariable=values[key],values=("АТП","Зупинка","Автостанція","Відпочинок","Нічліг","Інше"),state="readonly",width=39)
                            if key=="point_type" else ttk.Spinbox(fw,textvariable=values[key],from_=0,to=7,width=8)
                            if key in {"arrival_day_offset","departure_day_offset"} else ttk.Entry(fw,textvariable=values[key],width=42))
                    widget.grid(row=row,column=1,sticky="ew",padx=10,pady=7)
                fw.columnconfigure(1,weight=1)
                def save_stop():
                    name=values["stop_name"].get().strip()
                    if not name:
                        messagebox.showerror("Зупинка","Вкажіть назву зупинки.",parent=fw); return
                    for key in ("arrival_time","departure_time"):
                        raw=values[key].get().strip()
                        if raw:
                            try: parse_hhmm(raw)
                            except Exception:
                                messagebox.showerror("Зупинка","Час має бути у форматі ГГ:ХХ.",parent=fw); return
                    try:
                        arrival_day=int(values["arrival_day_offset"].get()); departure_day=int(values["departure_day_offset"].get())
                    except ValueError: arrival_day=departure_day=-1
                    if not (0 <= arrival_day <= 7 and 0 <= departure_day <= 7):
                        messagebox.showerror("Точка маршруту","Дні мають бути від D+0 до D+7.",parent=fw); return
                    if values["arrival_time"].get().strip() and values["departure_time"].get().strip():
                        if departure_day*1440+time_to_minutes(values["departure_time"].get()) < arrival_day*1440+time_to_minutes(values["arrival_time"].get()):
                            messagebox.showerror("Точка маршруту","Відправлення не може бути раніше прибуття.",parent=fw); return
                    item={k:values[k].get().strip() for k in values}
                    item["arrival_day_offset"]=arrival_day; item["departure_day_offset"]=departure_day
                    item["day_offset"]=arrival_day if item["arrival_time"] else departure_day
                    if index is None: stop_data[direction].append(item)
                    else: stop_data[direction][index]=item
                    redraw_stops(direction); refresh_stops_summary(); fw.destroy()
                ttk.Button(fw,text="Зберегти",command=save_stop).grid(row=4,column=1,sticky="e",padx=10,pady=12)

            for col,(direction,title) in enumerate((("outbound","Прямий напрямок"),("return","Зворотний напрямок"))):
                frame=ttk.LabelFrame(body,text=title); frame.grid(row=0,column=col,sticky="nsew",padx=5,pady=3)
                frame.columnconfigure(0,weight=1); frame.rowconfigure(0,weight=1)
                tree=ttk.Treeview(frame,columns=("no","type","name","arrive","depart","note"),show="headings")
                trees[direction]=tree
                for key,label,width in (("no","№",32),("type","Тип",75),("name","Точка",155),("arrive","Прибуття",105),("depart","Відправлення",110),("note","Примітка",120)):
                    tree.heading(key,text=label); tree.column(key,width=width,anchor="w")
                ybar=ttk.Scrollbar(frame,orient="vertical",command=tree.yview); xbar=ttk.Scrollbar(frame,orient="horizontal",command=tree.xview)
                tree.configure(yscrollcommand=ybar.set,xscrollcommand=xbar.set)
                tree.grid(row=0,column=0,sticky="nsew"); ybar.grid(row=0,column=1,sticky="ns"); xbar.grid(row=1,column=0,sticky="ew")
                bar=ttk.Frame(frame); bar.grid(row=2,column=0,columnspan=2,sticky="w",pady=5)
                ttk.Button(bar,text="Додати",command=lambda d=direction:stop_form(d)).pack(side="left",padx=2)
                ttk.Button(bar,text="Вставити список",command=lambda d=direction:quick_fill(d)).pack(side="left",padx=2)
                def edit_selected(d=direction):
                    sel=trees[d].selection()
                    if sel: stop_form(d,int(trees[d].item(sel[0],"values")[0])-1)
                ttk.Button(bar,text="Редагувати",command=edit_selected).pack(side="left",padx=2)
                def delete_selected(d=direction):
                    sel=trees[d].selection()
                    if sel:
                        stop_data[d].pop(int(trees[d].item(sel[0],"values")[0])-1); redraw_stops(d); refresh_stops_summary()
                ttk.Button(bar,text="Видалити",command=delete_selected).pack(side="left",padx=2)
                if direction=="return":
                    ttk.Button(bar,text="Назви ← прямий",command=copy_reverse_names).pack(side="left",padx=2)
                tree.bind("<Double-1>",lambda _e,d=direction: (lambda s=trees[d].selection(): stop_form(d,int(trees[d].item(s[0],"values")[0])-1) if s else None)())
            redraw_stops("outbound"); redraw_stops("return")
            bottom=ttk.Frame(sw); bottom.pack(fill="x",padx=12,pady=8)
            ttk.Button(bottom,text="Швидко вставити обидва напрямки",command=quick_fill_both).pack(side="left",padx=(0,6))
            ttk.Button(bottom,text="Підтягнути точки й дні з графіка",command=lambda:sync_route_bounds(force=True)).pack(side="left")
            ttk.Button(bottom,text="Готово",command=sw.destroy).pack(side="right")

        refresh_stops_summary()
        ttk.Label(win,textvariable=stops_summary,foreground="gray").grid(row=8,column=1,columnspan=2,sticky="e",padx=(10,3),pady=(3,5))
        ttk.Button(win,text="Заповнити маршрут для шляхівки…",command=edit_stop_schedule).grid(row=8,column=3,sticky="e",padx=10,pady=(3,5))
        ttk.Label(win,text="Частини робочої зміни").grid(row=9,column=0,sticky="nw",padx=10,pady=8)

        cols=("no","work_start","work_end","drive_start","drive_end","work","drive","activity","note")
        tree=ttk.Treeview(win,columns=cols,show="headings",height=10)
        for c,h,w in [
            ("no","№",35),("work_start","Роб. від",75),("work_end","Роб. до",75),
            ("drive_start","Кер. від",75),("drive_end","Кер. до",75),
            ("work","Робота",75),("drive","Керування",80),
            ("activity","Тип",110),("note","Примітка",180)
        ]:
            tree.heading(c,text=h); tree.column(c,width=w)
        tree.grid(row=9,column=1,columnspan=3,sticky="nsew",padx=10,pady=8)

        seg_data=[]
        for r in existing_segments:
            ds=(r["start_time"] or "").strip(); de=(r["end_time"] or "").strip()
            ws=(r["work_start_time"] or "").strip() or ds
            we=(r["work_end_time"] or "").strip() or de
            seg_data.append({
                "start_time":ds,"end_time":de,"work_start_time":ws,"work_end_time":we,
                "work_hours":minutes_to_db_hours(duration_minutes(ws,we)) if ws and we else 0,
                "driving_hours":minutes_to_db_hours(duration_minutes(ds,de)) if ds and de else 0,
                "activity_type":r["activity_type"],"note":r["note"]
            })

        def redraw():
            for x in tree.get_children():
                tree.delete(x)
            for i,r in enumerate(seg_data,1):
                tree.insert("","end",values=(
                    i,r["work_start_time"],r["work_end_time"],r["start_time"],r["end_time"],
                    hours_value_hhmm(r["work_hours"]),hours_value_hhmm(r["driving_hours"]),
                    r["activity_type"],r["note"]
                ))

        def edit_seg(index=None):
            sw=tk.Toplevel(win); sw.title("Частина маршруту")
            fit_window_to_screen(sw,570,455,520,410); sw.transient(win); sw.grab_set()
            base=seg_data[index] if index is not None else {
                "work_start_time":"08:00","work_end_time":"09:00",
                "start_time":"08:00","end_time":"09:00",
                "activity_type":"Робота","note":""
            }
            x={}
            defaults={
                "work_start_time":base.get("work_start_time") or base.get("start_time",""),
                "work_end_time":base.get("work_end_time") or base.get("end_time",""),
                "start_time":base.get("start_time",""),"end_time":base.get("end_time",""),
                "activity_type":base.get("activity_type","Робота"),"note":base.get("note","")
            }
            for k,v in defaults.items():
                x[k]=tk.StringVar(value=str(v or ""))
            for row,(lbl,key) in enumerate([
                ("Робота — початок","work_start_time"),("Робота — кінець","work_end_time"),
                ("Керування — початок","start_time"),("Керування — кінець","end_time"),
                ("Тип","activity_type"),("Примітка","note")
            ]):
                ttk.Label(sw,text=lbl).grid(row=row,column=0,sticky="w",padx=10,pady=6)
                widget=(
                    ttk.Combobox(sw,textvariable=x[key],values=DAY_TYPES,state="readonly",width=34)
                    if key=="activity_type" else ttk.Entry(sw,textvariable=x[key],width=36)
                )
                widget.grid(row=row,column=1,padx=10,pady=6,sticky="ew")
            duration_var=tk.StringVar()
            ttk.Label(sw,textvariable=duration_var,foreground="gray").grid(
                row=6,column=0,columnspan=2,sticky="w",padx=10,pady=4
            )
            def refresh(*_):
                try:
                    wt=minutes_hhmm(duration_minutes(x["work_start_time"].get(),x["work_end_time"].get()))
                except Exception:
                    wt="—"
                ds=x["start_time"].get().strip(); de=x["end_time"].get().strip()
                if not ds and not de:
                    dt="0:00"
                else:
                    try:
                        dt=minutes_hhmm(duration_minutes(ds,de))
                    except Exception:
                        dt="—"
                duration_var.set(f"Тривалість: робота {wt}; керування {dt}")
            for v in (x["work_start_time"],x["work_end_time"],x["start_time"],x["end_time"]):
                v.trace_add("write",refresh)
            refresh()
            bar=ttk.Frame(sw); bar.grid(row=7,column=0,columnspan=2,sticky="w",padx=10,pady=5)
            ttk.Button(
                bar,text="Керування → робота",
                command=lambda:(x["work_start_time"].set(x["start_time"].get()),x["work_end_time"].set(x["end_time"].get()))
            ).pack(side="left")
            ttk.Button(
                bar,text="Робота → керування",
                command=lambda:(x["start_time"].set(x["work_start_time"].get()),x["end_time"].set(x["work_end_time"].get()))
            ).pack(side="left",padx=(6,0))
            def save_seg():
                ws=x["work_start_time"].get().strip(); we=x["work_end_time"].get().strip()
                ds=x["start_time"].get().strip(); de=x["end_time"].get().strip()
                try:
                    if not ws or not we:
                        raise ValueError
                    wh_min=duration_minutes(ws,we)
                    if bool(ds)!=bool(de):
                        raise ValueError
                    dh_min=duration_minutes(ds,de) if ds and de else 0
                except Exception:
                    messagebox.showerror(
                        "Помилка","Перевірте пари початок/кінець для роботи і керування.",parent=sw
                    ); return
                if ds and not interval_within(ds,de,ws,we):
                    messagebox.showerror(
                        "Помилка","Інтервал керування повинен міститися всередині робочого інтервалу.",parent=sw
                    ); return
                item={
                    "work_start_time":ws,"work_end_time":we,"start_time":ds,"end_time":de,
                    "work_hours":minutes_to_db_hours(wh_min),"driving_hours":minutes_to_db_hours(dh_min),
                    "activity_type":x["activity_type"].get().strip(),"note":x["note"].get().strip()
                }
                if index is None:
                    seg_data.append(item)
                else:
                    seg_data[index]=item
                redraw(); sw.destroy()
            ttk.Button(sw,text="Зберегти",command=save_seg).grid(row=8,column=1,sticky="e",padx=10,pady=10)

        button_row=ttk.Frame(win); button_row.grid(row=10,column=1,columnspan=3,sticky="w",padx=10,pady=5)
        ttk.Button(button_row,text="Додати частину",command=lambda:edit_seg()).pack(side="left",padx=3)
        def edit_selected():
            sel=tree.selection()
            if sel:
                edit_seg(int(tree.item(sel[0],"values")[0])-1)
        ttk.Button(button_row,text="Редагувати",command=edit_selected).pack(side="left",padx=3)
        def del_selected():
            sel=tree.selection()
            if sel:
                seg_data.pop(int(tree.item(sel[0],"values")[0])-1); redraw()
        ttk.Button(button_row,text="Видалити",command=del_selected).pack(side="left",padx=3)
        redraw()

        def save():
            name=vv["name"].get().strip()
            if not name:
                messagebox.showerror("Помилка","Вкажіть назву маршруту.",parent=win); return
            try:
                planned_distance_km=parse_optional_route_distance(vv["planned_distance_km"].get())
            except ValueError as exc:
                messagebox.showerror("Маршрут",str(exc),parent=win); return
            if active.get() and not seg_data:
                messagebox.showerror(
                    "Помилка","Активний маршрут повинен мати хоча б одну точну частину робочої зміни.",parent=win
                ); return
            overlap_text=segment_overlap_message(seg_data,"work")
            if overlap_text:
                messagebox.showerror(
                    "Перекриття робочого часу",
                    "Частини маршруту не можуть накладатися одна на одну.\n\n"
                    + overlap_text
                    + "\n\nВиправте часові межі перед збереженням маршруту.",
                    parent=win
                ); return
            try:
                start_day=int(vv["start_day_offset"].get()); end_day=int(vv["end_day_offset"].get())
            except ValueError:
                start_day=end_day=-1
            if not (0 <= start_day <= 7 and start_day <= end_day <= 7):
                messagebox.showerror("Маршрут","Дні мають бути від D+0 до D+7, а завершення не раніше початку.",parent=win); return
            start_location=vv["start_location"].get().strip()
            end_location=vv["end_location"].get().strip()
            if active.get() and (not start_location or not end_location):
                messagebox.showerror("Маршрут","Для активного маршруту вкажіть точку початку і завершення роботи.",parent=win); return
            for direction,label in (("outbound","прямому"),("return","зворотному")):
                previous=-1
                for stop in stop_data[direction]:
                    arrival_day=int(stop.get("arrival_day_offset",stop.get("day_offset",0))); departure_day=int(stop.get("departure_day_offset",stop.get("day_offset",0)))
                    if min(arrival_day,departure_day) < start_day or max(arrival_day,departure_day) > end_day:
                        messagebox.showerror("Маршрут",f"У {label} напрямку точка «{stop['stop_name']}» має день поза межами маршруту.",parent=win); return
                    moments=[]
                    if stop.get("arrival_time"): moments.append(arrival_day*1440+time_to_minutes(stop["arrival_time"]))
                    if stop.get("departure_time"): moments.append(departure_day*1440+time_to_minutes(stop["departure_time"]))
                    if moments and (moments!=sorted(moments) or moments[0]<previous):
                        messagebox.showerror("Маршрут",f"У {label} напрямку порушена послідовність днів/часу біля точки «{stop['stop_name']}».",parent=win); return
                    if moments: previous=moments[-1]
            vehicle=vehicle_map.get(vv["vehicle"].get())
            vehicle_text=self.vehicle_label(vehicle) if vehicle else vv["vehicle"].get().strip()
            vehicle_id=vehicle["id"] if vehicle else None
            con=db()
            try:
                if route:
                    rid=route["id"]
                    con.execute(
                        """UPDATE routes SET
                               name=?,code=?,description=?,vehicle=?,vehicle_id=?,shift_type=?,notes=?,active=?,
                               start_location=?,end_location=?,start_direction=?,start_day_offset=?,end_day_offset=?,planned_distance_km=?
                             WHERE id=?""",
                        (name,vv["code"].get().strip(),vv["description"].get().strip(),
                         vehicle_text,vehicle_id,vv["shift_type"].get(),vv["notes"].get().strip(),
                         int(active.get()),start_location,end_location,vv["start_direction"].get(),start_day,end_day,planned_distance_km,rid)
                    )
                    con.execute("DELETE FROM route_segments WHERE route_id=?",(rid,))
                    con.execute("DELETE FROM route_stops WHERE route_id=?",(rid,))
                else:
                    cur=con.execute(
                        """INSERT INTO routes(
                               name,code,description,vehicle,vehicle_id,shift_type,notes,active,created_at,
                               start_location,end_location,start_direction,start_day_offset,end_day_offset,planned_distance_km
                           ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (name,vv["code"].get().strip(),vv["description"].get().strip(),
                         vehicle_text,vehicle_id,vv["shift_type"].get(),vv["notes"].get().strip(),
                         int(active.get()),datetime.now().isoformat(timespec="seconds"),start_location,end_location,
                         vv["start_direction"].get(),start_day,end_day,planned_distance_km)
                    )
                    rid=cur.lastrowid
                for i,r in enumerate(seg_data,1):
                    con.execute(
                        """INSERT INTO route_segments(
                               route_id,segment_no,start_time,end_time,work_start_time,work_end_time,
                               work_hours,driving_hours,activity_type,note
                           ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
                        (rid,i,r["start_time"],r["end_time"],r["work_start_time"],r["work_end_time"],
                        r["work_hours"],r["driving_hours"],r["activity_type"],r["note"])
                    )
                for direction in ("outbound","return"):
                    for i,stop in enumerate(stop_data[direction],1):
                        con.execute(
                            """INSERT INTO route_stops(route_id,direction,stop_no,stop_name,arrival_time,departure_time,note,day_offset,arrival_day_offset,departure_day_offset,point_type)
                               VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                            (rid,direction,i,stop["stop_name"],stop["arrival_time"],stop["departure_time"],stop["note"],
                             int(stop.get("day_offset",0)),int(stop.get("arrival_day_offset",stop.get("day_offset",0))),
                             int(stop.get("departure_day_offset",stop.get("day_offset",0))),stop.get("point_type","Зупинка"))
                        )
                con.commit()
            except sqlite3.IntegrityError as e:
                con.rollback()
                messagebox.showerror(
                    "Помилка",f"Не вдалося зберегти маршрут. Назва має бути унікальною.\n{e}",parent=win
                ); return
            finally:
                con.close()
            win.destroy(); self.load_route_catalog()

        ttk.Button(win,text="Зберегти маршрут",command=save).grid(row=11,column=3,sticky="e",padx=10,pady=10)

    def edit_route_catalog(self):
        item=self.selected_route_catalog()
        if item:
            self.route_catalog_form(item)

    def delete_route_catalog(self):
        item=self.selected_route_catalog()
        if not item:
            return
        route=item[0]
        if messagebox.askyesno(
            "Підтвердження",
            "Вимкнути цей маршрут? Історичні записи табеля та його часовий сценарій залишаться.",
            parent=self
        ):
            con=db(); con.execute("UPDATE routes SET active=0 WHERE id=?",(route["id"],)); con.commit(); con.close()
            self.load_route_catalog()

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
        open_bar=ttk.Frame(hbar)
        open_bar.pack(fill="x")
        ttk.Label(open_bar,text="Відкрити:").pack(side="left",padx=(3,1))
        ttk.Button(open_bar,text="DOCX",command=lambda:self.open_att_file("docx")).pack(side="left",padx=3)
        ttk.Button(open_bar,text="PDF",command=lambda:self.open_att_file("pdf")).pack(side="left",padx=3)
        ttk.Button(open_bar,text="JPG",command=lambda:self.open_att_file("jpg")).pack(side="left",padx=3)
        ttk.Button(open_bar,text="Папка файла",command=self.open_att_folder).pack(side="left",padx=3)
        ttk.Button(open_bar,text="Архів файлів",command=self.open_att_archive_folder).pack(side="left",padx=3)

        manage_bar=ttk.Frame(hbar)
        manage_bar.pack(fill="x",pady=(4,0))
        ttk.Label(manage_bar,text="Дії:").pack(side="left",padx=(3,1))
        ttk.Button(manage_bar,text="Редагувати",command=self.edit_selected_attestation).pack(side="left",padx=3)
        ttk.Button(manage_bar,text="Вилучити з контролю",command=self.delete_selected_attestation).pack(side="left",padx=3)
        ttk.Button(manage_bar,text="Відновити",command=self.restore_selected_attestation).pack(side="left",padx=3)
        ttk.Button(manage_bar,text="Видалити назавжди",command=self.purge_selected_attestation).pack(side="left",padx=3)
        ttk.Button(manage_bar,text="Історія змін",command=self.show_attestation_audit).pack(side="left",padx=3)

        filter_bar=ttk.Frame(hist)
        filter_bar.pack(fill="x",padx=6,pady=(2,2))
        ttk.Label(filter_bar,text="Показати:").pack(side="left",padx=(0,4))
        self.att_filter=tk.StringVar(value="Активні")
        att_filter_cb=ttk.Combobox(
            filter_bar,textvariable=self.att_filter,state="readonly",width=12,
            values=("Активні","Вилучені","Усі")
        )
        att_filter_cb.pack(side="left")
        att_filter_cb.bind("<<ComboboxSelected>>",lambda e:self.load_att_history())

        self.att_filter_driver_only=tk.BooleanVar(value=True)
        ttk.Checkbutton(
            filter_bar,text="Тільки вибраний водій",
            variable=self.att_filter_driver_only,
            command=self.load_att_history
        ).pack(side="left",padx=(12,4))

        self.att_filter_month_enabled=tk.BooleanVar(value=False)
        ttk.Checkbutton(
            filter_bar,text="За місяць",
            variable=self.att_filter_month_enabled,
            command=self.load_att_history
        ).pack(side="left",padx=(10,3))
        today=date.today()
        self.att_filter_month=tk.StringVar(value=str(today.month))
        self.att_filter_year=tk.StringVar(value=str(today.year))
        month_box=ttk.Spinbox(filter_bar,textvariable=self.att_filter_month,from_=1,to=12,width=4)
        month_box.pack(side="left",padx=(1,2))
        ttk.Label(filter_bar,text="/").pack(side="left")
        year_box=ttk.Spinbox(filter_bar,textvariable=self.att_filter_year,from_=2020,to=2100,width=6)
        year_box.pack(side="left",padx=(2,5))
        month_box.bind("<Return>",lambda _e:self.load_att_history())
        year_box.bind("<Return>",lambda _e:self.load_att_history())

        ttk.Button(filter_bar,text="Оновити",command=self.load_att_history).pack(side="left",padx=4)
        ttk.Button(filter_bar,text="Скинути відбір",command=self.reset_att_history_filters).pack(side="left",padx=4)
        ttk.Label(filter_bar,text="Новіші ↑",foreground="gray").pack(side="left",padx=(10,2))

        summary_bar=ttk.Frame(hist)
        summary_bar.pack(fill="x",padx=6,pady=(0,3))
        self.att_list_summary=tk.StringVar(value="")
        ttk.Label(summary_bar,textvariable=self.att_list_summary,foreground="gray").pack(side="left",padx=2)

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
        fit_window_to_screen(win,1250,650,900,500)

        top=ttk.Frame(win,padding=8)
        top.pack(fill="x")
        control_bar=ttk.Frame(top)
        control_bar.pack(fill="x")

        self.att_gap_control_date=tk.StringVar(
            value=self.att_date.get().strip() if hasattr(self,"att_date") else date.today().strftime("%d.%m.%Y")
        )
        ttk.Label(control_bar,text="День контролю:").pack(side="left")
        ttk.Entry(control_bar,textvariable=self.att_gap_control_date,width=13).pack(side="left",padx=5)
        calendar_button(control_bar,self.att_gap_control_date).pack(side="left",padx=2)
        ttk.Button(
            control_bar,text="Перевірити",command=self.refresh_attestation_gap_control
        ).pack(side="left",padx=8)

        self.att_gap_activity=tk.StringVar(value=f"16 — {ACTIVITIES[16]}")
        ttk.Label(control_bar,text="Позиція:").pack(side="left",padx=(8,3))
        ttk.Combobox(
            control_bar,textvariable=self.att_gap_activity,state="readonly",width=31,
            values=[f"{n} — {ACTIVITIES[n]}" for n in ACTIVITIES]
        ).pack(side="left",padx=3)

        action_bar=ttk.Frame(top)
        action_bar.pack(fill="x",pady=(5,0))
        ttk.Button(
            action_bar,text="Підставити у форму",
            command=self.use_selected_attestation_gap
        ).pack(side="left",padx=(0,8))
        ttk.Button(
            action_bar,text="Сформувати Бланк підтвердження",
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
        stored_created={key:db_stored_path(value) if value else "" for key,value in created.items()}

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
                stored_created["file_path"],stored_created["pdf_path"],stored_created["jpg_page1_path"],stored_created["jpg_page2_path"],
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
        stored_created={key:db_stored_path(value) if value else "" for key,value in created.items()}

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
                 stored_created["file_path"],stored_created["pdf_path"],stored_created["jpg_page1_path"],stored_created["jpg_page2_path"],
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
        fit_window_to_screen(win,760,390,650,360)
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
        open_external(ATT_ARCHIVE_DIR)

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
                fp=real_data_path(raw)
                if fp is None:
                    continue
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
        fit_window_to_screen(win,1350,520,850,440)
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
                    actual=real_data_path(val)
                    parts.append(f"{label}: {actual or val}")
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

    def reset_att_history_filters(self):
        """Show the normal active archive without driver/month restrictions."""
        if hasattr(self,"att_filter"):
            self.att_filter.set("Активні")
        if hasattr(self,"att_filter_driver_only"):
            self.att_filter_driver_only.set(False)
        if hasattr(self,"att_filter_month_enabled"):
            self.att_filter_month_enabled.set(False)
        today=date.today()
        if hasattr(self,"att_filter_month"):
            self.att_filter_month.set(str(today.month))
        if hasattr(self,"att_filter_year"):
            self.att_filter_year.set(str(today.year))
        self.load_att_history()

    def load_att_history(self):
        if not hasattr(self,"att_tree"):
            return
        selected_id=self._selected_attestation_id() if self.att_tree.selection() else None
        for x in self.att_tree.get_children():
            self.att_tree.delete(x)

        mode=(self.att_filter.get().strip() if hasattr(self,"att_filter") else "Активні")
        driver_filter_enabled=bool(
            hasattr(self,"att_filter_driver_only") and self.att_filter_driver_only.get()
        )
        driver_id=(getattr(self,"att_driver_id",None) if driver_filter_enabled else None)

        filter_year=filter_month=None
        month_filter_enabled=bool(
            hasattr(self,"att_filter_month_enabled") and self.att_filter_month_enabled.get()
        )
        if month_filter_enabled:
            try:
                filter_month=int(self.att_filter_month.get())
                filter_year=int(self.att_filter_year.get())
                if not 1<=filter_month<=12 or not 1900<=filter_year<=2200:
                    raise ValueError
            except Exception:
                messagebox.showerror(
                    "Відбір бланків",
                    "Перевірте місяць (1–12) і рік.",
                    parent=self
                )
                return

        con=db()
        total=con.execute("SELECT COUNT(*) FROM attestations").fetchone()[0]
        active_count=con.execute("SELECT COUNT(*) FROM attestations WHERE COALESCE(status,'active')='active'").fetchone()[0]
        deleted_count=con.execute("SELECT COUNT(*) FROM attestations WHERE COALESCE(status,'active')<>'active'").fetchone()[0]
        sql,params=attestation_history_query(
            mode=mode,
            driver_id=driver_id,
            year=filter_year,
            month=filter_month,
        )
        rows=con.execute(sql,params).fetchall()
        con.close()

        if hasattr(self,"att_list_summary"):
            filters=[]
            if driver_filter_enabled:
                if driver_id:
                    filters.append(f"водій: {self.att_driver_var.get().strip()}")
                else:
                    filters.append("водій: не вибраний (показано всіх)")
            if month_filter_enabled:
                filters.append(f"місяць: {filter_month:02d}.{filter_year}")
            filter_text=(" | відбір: "+", ".join(filters)) if filters else ""
            self.att_list_summary.set(
                f"Показано: {len(rows)} з {total} | активних: {active_count} | вилучених: {deleted_count}"
                + filter_text
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
            primary=str(real_data_path(primary) or primary) if primary else ""
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
        raw=(path or "").strip()
        path=real_data_path(raw)
        if path is None or not path.exists():
            messagebox.showerror("Помилка","Файл не знайдено.",parent=self)
            return
        open_external(path)

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
        resolved=real_data_path(path)
        if resolved is None:
            messagebox.showerror("Помилка","Папку файла не знайдено.",parent=self)
            return
        folder=str(resolved.parent)
        open_external(folder)

if __name__ == "__main__":
    workspace_lock=prepare_workspace_interactively()
    if workspace_lock is not None:
        try:
            migrated, old_db = init_db()
            app = App()
            if migrated and old_db:
                app.after(300, lambda: messagebox.showinfo(
                    "Дані перенесено автоматично",
                    "Існуючу базу водіїв знайдено та один раз скопійовано у робоче сховище:\n\n"
                    f"{DB_PATH}\n\nСтара база залишена без змін."
                ))
            app.mainloop()
        finally:
            workspace_lock.release()
