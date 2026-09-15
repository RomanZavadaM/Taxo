# -*- coding: utf-8 -*-
"""Робоче сховище Taxo.

У сховищі лежать усі змінні робочі дані. Невеликий локальний JSON зберігає
лише адресу вибраного сховища, щоб різні інсталяції могли підключатися до
однієї локальної, мережевої або синхронізованої папки.
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import sqlite3
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path


WORKSPACE_FORMAT = 1
WORKSPACE_POINTER_ENV = "TAXO_WORKSPACE_ROOT"
WORKSPACE_CONFIG_ENV = "TAXO_CONFIG_DIR"
MARKER_NAME = ".taxo_workspace.json"
LOCK_NAME = ".taxo_workspace.lock"
STALE_LOCK_MINUTES = 5


def _now():
    return datetime.now(timezone.utc)


def _iso_now():
    return _now().isoformat(timespec="seconds")


def default_workspace_root():
    return Path.home() / "Documents" / "DriverWorktime"


def config_dir():
    override=os.environ.get(WORKSPACE_CONFIG_ENV," ").strip()
    if override:
        return Path(override).expanduser()
    if os.name=="nt":
        base=os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA")
        return Path(base).expanduser()/"Taxo" if base else Path.home()/"AppData"/"Roaming"/"Taxo"
    if sys.platform=="darwin":
        return Path.home()/"Library"/"Application Support"/"Taxo"
    base=os.environ.get("XDG_CONFIG_HOME")
    return (Path(base).expanduser() if base else Path.home()/".config")/"Taxo"


def pointer_path():
    return config_dir()/"workspace.json"


def normalize_root(value):
    path=Path(os.path.expandvars(str(value))).expanduser()
    if not path.is_absolute():
        path=Path.cwd()/path
    return Path(os.path.abspath(str(path)))


def load_workspace_root():
    env=os.environ.get(WORKSPACE_POINTER_ENV," ").strip()
    if env:
        return normalize_root(env)
    try:
        data=json.loads(pointer_path().read_text("utf-8"))
        raw=str(data.get("workspace_root") or "").strip()
        if raw:
            return normalize_root(raw)
    except (OSError,ValueError,TypeError):
        pass
    return normalize_root(default_workspace_root())


def save_workspace_root(root):
    """Атомарно зберегти локальний покажчик; робочих даних у ньому немає."""
    root=normalize_root(root)
    target=pointer_path()
    target.parent.mkdir(parents=True,exist_ok=True)
    temp=target.with_name(target.name+f".{uuid.uuid4().hex}.tmp")
    payload={
        "format":WORKSPACE_FORMAT,
        "workspace_root":str(root),
        "updated_at":_iso_now(),
    }
    temp.write_text(json.dumps(payload,ensure_ascii=False,indent=2),"utf-8")
    os.replace(temp,target)
    return target


def paths_for(root):
    root=normalize_root(root)
    data=root/"Data"
    output=root/"Output"
    archive=output/"AttestationArchive"
    return {
        "root":root,
        "data":data,
        "backups":root/"Backups",
        "output":output,
        "logs":root/"Logs",
        "att_archive":archive,
        "att_replaced":archive/"Replaced",
        "att_deleted":archive/"Deleted",
        "waybills":output/"Waybills",
        "main_db":data/"driver_worktime.sqlite3",
        "tacho_db":data/"tachograph_test.sqlite3",
        "tacho_scans":data/"TachographScans",
    }


def ensure_workspace(root):
    root=normalize_root(root)
    p=paths_for(root)
    for key in ("data","backups","output","logs","att_archive","att_replaced","att_deleted","waybills","tacho_scans"):
        p[key].mkdir(parents=True,exist_ok=True)
    marker=root/MARKER_NAME
    if not marker.exists():
        marker.write_text(json.dumps({
            "format":WORKSPACE_FORMAT,
            "application":"Taxo",
            "created_at":_iso_now(),
        },ensure_ascii=False,indent=2),"utf-8")
    return p


def probe_workspace(root):
    """Перевірити створення, запис/читання/видалення і повернути короткий стан."""
    root=normalize_root(root)
    root.mkdir(parents=True,exist_ok=True)
    probe=root/f".taxo_probe_{uuid.uuid4().hex}.tmp"
    token=uuid.uuid4().hex
    try:
        with probe.open("x",encoding="utf-8") as fh:
            fh.write(token)
            fh.flush()
            os.fsync(fh.fileno())
        if probe.read_text("utf-8")!=token:
            raise OSError("контрольний запис не прочитано без змін")
    finally:
        try:
            probe.unlink()
        except OSError:
            pass
    free=shutil.disk_usage(root).free
    return {"root":root,"free_bytes":free,"kind":storage_kind(root)}


def storage_kind(root):
    text=str(root).lower().replace("\\","/")
    cloud_tokens=("onedrive","dropbox","google drive","googledrive","icloud drive","nextcloud","syncthing")
    if any(token in text for token in cloud_tokens):
        return "cloud"
    if str(root).startswith(("\\\\","//")):
        return "network"
    return "local"


def workspace_has_data(root):
    p=paths_for(root)
    if p["main_db"].exists() or p["tacho_db"].exists():
        return True
    for key in ("tacho_scans","output","backups"):
        folder=p[key]
        try:
            if folder.exists() and any(folder.iterdir()):
                return True
        except OSError:
            return True
    return False


def _pid_alive(pid):
    try:
        pid=int(pid)
        if pid<=0:
            return False
    except (ValueError,TypeError):
        return False
    if pid==os.getpid():
        return True
    if os.name=="nt":
        # On Windows os.kill(pid, 0) can deliver a console CTRL_C_EVENT instead
        # of performing the harmless POSIX existence probe.
        import ctypes
        process_query_limited_information=0x1000
        still_active=259
        kernel32=ctypes.windll.kernel32
        handle=kernel32.OpenProcess(process_query_limited_information,False,pid)
        if not handle:
            return False
        try:
            exit_code=ctypes.c_ulong()
            if not kernel32.GetExitCodeProcess(handle,ctypes.byref(exit_code)):
                return False
            return exit_code.value==still_active
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid,0)
        return True
    except OSError:
        return False


def read_lock_info(root):
    path=normalize_root(root)/LOCK_NAME
    if not path.exists():
        return None
    try:
        info=json.loads(path.read_text("utf-8"))
    except (OSError,ValueError,TypeError):
        info={"unreadable":True}
    info["path"]=str(path)
    host=str(info.get("host") or "")
    same_host=host.casefold()==socket.gethostname().casefold()
    heartbeat=info.get("heartbeat_at") or info.get("started_at")
    age=None
    try:
        parsed=datetime.fromisoformat(str(heartbeat))
        if parsed.tzinfo is None:
            parsed=parsed.replace(tzinfo=timezone.utc)
        age=_now()-parsed.astimezone(timezone.utc)
    except (ValueError,TypeError):
        pass
    info["same_host"]=same_host
    info["same_process_alive"]=bool(same_host and _pid_alive(info.get("pid")))
    info["age_seconds"]=age.total_seconds() if age is not None else None
    info["stale"]=bool(
        (same_host and not info["same_process_alive"])
        or (age is not None and age>timedelta(minutes=STALE_LOCK_MINUTES))
    )
    return info


class WorkspaceBusyError(RuntimeError):
    def __init__(self,root,info):
        self.root=normalize_root(root)
        self.info=info or {}
        super().__init__(describe_lock(self.info))


def describe_lock(info):
    if not info:
        return "Відомості про інший запуск недоступні."
    if info.get("unreadable"):
        return "Файл блокування існує, але його неможливо прочитати."
    def local_time(value):
        try:
            parsed=datetime.fromisoformat(str(value))
            if parsed.tzinfo is None:
                parsed=parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone().strftime("%d.%m.%Y %H:%M:%S")
        except (ValueError,TypeError):
            return "невідомо"
    started=local_time(info.get("started_at"))
    heartbeat=local_time(info.get("heartbeat_at"))
    return (
        f"Комп’ютер: {info.get('host') or 'невідомо'}\n"
        f"Користувач: {info.get('user') or 'невідомо'}\n"
        f"PID: {info.get('pid') or 'невідомо'}\n"
        f"Запущено: {started}\n"
        f"Останній сигнал: {heartbeat}"
    )


class WorkspaceLock:
    """Кооперативне блокування для почергового доступу до одного сховища."""
    def __init__(self,root,version=""):
        self.root=normalize_root(root)
        self.path=self.root/LOCK_NAME
        self.version=str(version or "")
        self.token=uuid.uuid4().hex
        self.acquired=False

    def _payload(self,started_at=None):
        return {
            "format":WORKSPACE_FORMAT,
            "token":self.token,
            "host":socket.gethostname(),
            "user":os.environ.get("USERNAME") or os.environ.get("USER") or "",
            "pid":os.getpid(),
            "version":self.version,
            "started_at":started_at or _iso_now(),
            "heartbeat_at":_iso_now(),
        }

    def _archive_existing(self):
        if not self.path.exists():
            return
        logs=paths_for(self.root)["logs"]
        logs.mkdir(parents=True,exist_ok=True)
        stamp=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archived=logs/f"recovered_workspace_lock_{stamp}_{uuid.uuid4().hex[:8]}.json"
        os.replace(self.path,archived)

    def acquire(self,force=False):
        ensure_workspace(self.root)
        for _ in range(2):
            payload=self._payload()
            try:
                fd=os.open(self.path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
                with os.fdopen(fd,"w",encoding="utf-8") as fh:
                    json.dump(payload,fh,ensure_ascii=False,indent=2)
                    fh.flush(); os.fsync(fh.fileno())
                self.acquired=True
                return payload
            except FileExistsError:
                info=read_lock_info(self.root)
                auto_recover=bool(info and info.get("same_host") and not info.get("same_process_alive"))
                if force or auto_recover:
                    self._archive_existing()
                    force=False
                    continue
                raise WorkspaceBusyError(self.root,info)
        raise WorkspaceBusyError(self.root,read_lock_info(self.root))

    def refresh(self):
        if not self.acquired:
            return False
        try:
            current=json.loads(self.path.read_text("utf-8"))
            if current.get("token")!=self.token:
                self.acquired=False
                return False
            payload=self._payload(started_at=current.get("started_at"))
            with self.path.open("w",encoding="utf-8") as fh:
                json.dump(payload,fh,ensure_ascii=False,indent=2)
                fh.flush(); os.fsync(fh.fileno())
            return True
        except (OSError,ValueError,TypeError):
            return False

    def release(self):
        if not self.acquired:
            return False
        try:
            current=json.loads(self.path.read_text("utf-8"))
            if current.get("token")!=self.token:
                self.acquired=False
                return False
            self.path.unlink()
            self.acquired=False
            return True
        except (OSError,ValueError,TypeError):
            self.acquired=False
            return False


def stored_path(path,root):
    """Зберігати внутрішні файли переносимо як workspace:// відносні адреси."""
    if path is None or str(path).strip()=="":
        return ""
    raw=str(path).strip()
    if raw.startswith("workspace://"):
        return raw
    resolved=normalize_root(raw)
    base=normalize_root(root)
    try:
        relative=resolved.relative_to(base)
    except ValueError:
        return raw
    return "workspace://"+relative.as_posix()


def resolved_path(value,root):
    if value is None or str(value).strip()=="":
        return None
    raw=str(value).strip()
    base=normalize_root(root)
    if raw.startswith("workspace://"):
        candidate=normalize_root(base/Path(raw[len("workspace://"):]))
        try:
            candidate.relative_to(base)
        except ValueError:
            return None
        return candidate
    path=Path(raw).expanduser()
    foreign_windows_absolute=(len(raw)>=3 and raw[1]==":" and raw[2] in ("\\","/")) or raw.startswith("\\\\")
    if path.exists():
        return path
    if not path.is_absolute() and not foreign_windows_absolute:
        return base/path
    # Старі абсолютні адреси з іншого комп'ютера: відновлюємо від одного з
    # каталогів стандартної структури Taxo.
    portable=raw.replace("\\","/")
    for name in ("Data","Output","Backups","Logs"):
        marker=f"/{name}/"
        pos=portable.casefold().find(marker.casefold())
        if pos>=0:
            suffix=portable[pos+1:]
            return base/Path(suffix)
    return path


def _sqlite_backup(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    src=sqlite3.connect(str(source),timeout=30)
    dst=sqlite3.connect(str(target),timeout=30)
    try:
        src.execute("PRAGMA query_only=ON")
        src.execute("PRAGMA busy_timeout=30000")
        src.backup(dst)
        dst.commit()
    finally:
        dst.close(); src.close()


def validate_sqlite(path):
    if not path.exists():
        return
    con=sqlite3.connect(str(path),timeout=30)
    try:
        con.execute("PRAGMA query_only=ON")
        con.execute("PRAGMA busy_timeout=30000")
        result=con.execute("PRAGMA quick_check").fetchone()
        if not result or str(result[0]).lower()!="ok":
            raise ValueError(f"SQLite quick_check: {result[0] if result else 'немає результату'}")
    finally:
        con.close()


def _copy_tree_without_databases(source,target):
    excluded={"driver_worktime.sqlite3","tachograph_test.sqlite3",LOCK_NAME}
    for child in source.iterdir():
        if child.name in excluded or child.name.startswith(".taxo_probe_"):
            continue
        if child.name.endswith(("-wal","-shm","-journal")):
            continue
        dest=target/child.name
        if child.is_dir():
            shutil.copytree(
                child,dest,dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(
                    "driver_worktime.sqlite3","tachograph_test.sqlite3",
                    "*-wal","*-shm","*-journal",LOCK_NAME
                )
            )
        elif child.name!=MARKER_NAME:
            shutil.copy2(child,dest)


def clone_workspace(source_root,target_root):
    """Створити перевірену копію сховища; оригінал лишається страховою копією."""
    source=normalize_root(source_root); target=normalize_root(target_root)
    if source==target:
        raise ValueError("Нове сховище збігається з поточним.")
    try:
        target.relative_to(source)
        raise ValueError("Нове сховище не можна створювати всередині поточного.")
    except ValueError as exc:
        if str(exc).startswith("Нове сховище"):
            raise
    try:
        source.relative_to(target)
        raise ValueError("Поточне сховище не може бути вкладене в нове.")
    except ValueError as exc:
        if str(exc).startswith("Поточне сховище"):
            raise
    probe_workspace(target)
    if workspace_has_data(target):
        raise ValueError("У вибраній папці вже є дані Taxo. Для них використайте «Підключити існуюче».")
    stage=target/f".taxo_transfer_{uuid.uuid4().hex}"
    stage.mkdir(parents=False,exist_ok=False)
    try:
        _copy_tree_without_databases(source,stage)
        srcp=paths_for(source); stagep=paths_for(stage)
        if srcp["main_db"].exists():
            _sqlite_backup(srcp["main_db"],stagep["main_db"])
        if srcp["tacho_db"].exists():
            _sqlite_backup(srcp["tacho_db"],stagep["tacho_db"])
        validate_sqlite(stagep["main_db"])
        validate_sqlite(stagep["tacho_db"])
        # Після перевірки переносимо вміст staging до вибраної папки.
        for child in list(stage.iterdir()):
            dest=target/child.name
            if child.is_dir() and dest.exists():
                shutil.copytree(child,dest,dirs_exist_ok=True)
                shutil.rmtree(child)
            else:
                os.replace(child,dest)
        ensure_workspace(target)
        return paths_for(target)
    except Exception:
        # staging не є даними користувача і видаляється лише в точній цільовій папці.
        shutil.rmtree(stage,ignore_errors=True)
        raise
    finally:
        if stage.exists():
            shutil.rmtree(stage,ignore_errors=True)


def normalize_database_paths(db_path,root,table_fields):
    """Перевести внутрішні файлові адреси старої БД у переносимий формат."""
    if not Path(db_path).exists():
        return 0
    con=sqlite3.connect(db_path,timeout=30)
    changed=0
    try:
        tables={r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for table,fields in table_fields.items():
            if table not in tables:
                continue
            cols={r[1] for r in con.execute(f"PRAGMA table_info({table})")}
            usable=[field for field in fields if field in cols]
            if not usable:
                continue
            rows=con.execute(f"SELECT rowid,{','.join(usable)} FROM {table}").fetchall()
            for row in rows:
                updates=[]; values=[]
                for index,field in enumerate(usable,1):
                    old=row[index]
                    if not old:
                        continue
                    real=resolved_path(old,root)
                    new=stored_path(real,root) if real is not None else old
                    if new!=old:
                        updates.append(f"{field}=?"); values.append(new)
                if updates:
                    values.append(row[0])
                    con.execute(f"UPDATE {table} SET {','.join(updates)} WHERE rowid=?",values)
                    changed+=1
        con.commit()
    finally:
        con.close()
    return changed
