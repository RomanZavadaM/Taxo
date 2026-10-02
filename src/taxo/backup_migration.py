# -*- coding: utf-8 -*-
"""Low-level Taxo database backup, restore and legacy migration infrastructure.

This module deliberately owns only filesystem/SQLite mechanics. UI decisions,
retention-of-worktime policy and application business rules stay outside it.
The public wrappers in ``main.py`` preserve historical call sites.
"""
from __future__ import annotations

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, Tuple


LEGACY_APP_NAMES = (
    "driver_worktime_app_v2",
    "driver_worktime_app_v3",
    "driver_worktime_app_v4",
    "driver_worktime_app",
)


def find_legacy_database(app_dir, db_path) -> Optional[Path]:
    """Find the old local database used by the one-time first-run migration."""

    app_dir = Path(app_dir)
    db_path = Path(db_path)
    candidates = [
        app_dir / "driver_worktime.sqlite3",
        app_dir.parent / "driver_worktime.sqlite3",
    ]
    for base in (app_dir.parent, app_dir.parent / "blank"):
        for name in LEGACY_APP_NAMES:
            candidates.append(base / name / "driver_worktime.sqlite3")

    seen = set()
    current = db_path.resolve()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.exists() and candidate != current:
            return candidate
    return None


def migrate_legacy_database(app_dir, db_path) -> Tuple[bool, Optional[Path]]:
    """Copy an existing legacy database into the current workspace once."""

    db_path = Path(db_path)
    if db_path.exists():
        return False, None
    old = find_legacy_database(app_dir, db_path)
    if not old:
        return False, None
    tmp = db_path.with_suffix(".sqlite3.migrating")
    shutil.copy2(old, tmp)
    tmp.replace(db_path)
    return True, old


def backup_database(db_path, backup_dir, label="auto") -> Optional[Path]:
    """Create a consistent SQLite copy and keep the historical last-30 rule."""

    db_path = Path(db_path)
    backup_dir = Path(backup_dir)
    if not db_path.exists():
        return None
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target = backup_dir / f"driver_worktime_{label}_{stamp}.sqlite3"
    src_con = sqlite3.connect(str(db_path), timeout=30)
    dst_con = sqlite3.connect(str(target), timeout=30)
    try:
        src_con.execute("PRAGMA busy_timeout=30000")
        src_con.backup(dst_con)
        dst_con.commit()
    finally:
        dst_con.close()
        src_con.close()

    backups = sorted(
        backup_dir.glob("driver_worktime_*.sqlite3"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for old in backups[30:]:
        try:
            old.unlink()
        except OSError:
            pass
    return target


def auto_backup_database(db_path, backup_dir) -> Optional[Path]:
    """Create the startup backup no more than once per 24 hours."""

    db_path = Path(db_path)
    backup_dir = Path(backup_dir)
    if not db_path.exists():
        return None
    now = datetime.now().timestamp()
    recent = [
        path
        for path in backup_dir.glob("driver_worktime_auto_*.sqlite3")
        if (now - path.stat().st_mtime) < 86400
    ]
    if recent:
        return recent[0]
    return backup_database(db_path, backup_dir, "auto")


def validate_database_file(path):
    """Validate that a file is a healthy and compatible Taxo SQLite database."""

    path = Path(path)
    if not path.exists() or not path.is_file():
        return False, "Файл не знайдено."

    con = None
    try:
        con = sqlite3.connect(str(path), timeout=30)
        con.execute("PRAGMA query_only=ON")
        con.execute("PRAGMA busy_timeout=30000")
        quick = con.execute("PRAGMA quick_check").fetchone()
        if not quick or str(quick[0]).lower() != "ok":
            return False, f"SQLite quick_check: {quick[0] if quick else 'невідомий результат'}"

        tables = {
            row[0]
            for row in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        required = {"drivers", "worklog", "company"}
        missing = sorted(required - tables)
        if missing:
            return False, "Не схожа на базу Taxo. Відсутні таблиці: " + ", ".join(missing)

        driver_count = con.execute("SELECT COUNT(*) FROM drivers").fetchone()[0]
        work_count = con.execute("SELECT COUNT(*) FROM worklog").fetchone()[0]
        return True, f"База справна. Водіїв: {driver_count}; записів табеля: {work_count}."
    except Exception as exc:
        return False, str(exc)
    finally:
        if con is not None:
            con.close()


def restore_database_from_file(
    source_path,
    db_path,
    backup_dir,
    init_db: Callable[[], object],
):
    """Atomically restore the main DB while preserving the safety-backup flow."""

    source = Path(source_path)
    db_path = Path(db_path)
    backup_dir = Path(backup_dir)
    ok, details = validate_database_file(source)
    if not ok:
        raise ValueError(f"Обрана резервна копія не пройшла перевірку:\n{details}")

    safety_backup = backup_database(db_path, backup_dir, "before_restore") if db_path.exists() else None
    temp_target = db_path.with_suffix(".sqlite3.restore_tmp")

    try:
        if temp_target.exists():
            temp_target.unlink()

        src_con = sqlite3.connect(str(source), timeout=30)
        dst_con = sqlite3.connect(str(temp_target), timeout=30)
        try:
            src_con.execute("PRAGMA query_only=ON")
            src_con.execute("PRAGMA busy_timeout=30000")
            src_con.backup(dst_con)
            dst_con.commit()
        finally:
            dst_con.close()
            src_con.close()

        ok2, details2 = validate_database_file(temp_target)
        if not ok2:
            raise ValueError(f"Копія після перенесення не пройшла перевірку:\n{details2}")

        os.replace(temp_target, db_path)
        init_db()

        final_ok, final_details = validate_database_file(db_path)
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
                shutil.copy2(safety_backup, db_path)
                init_db()
            except Exception:
                pass
        raise
