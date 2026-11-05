# -*- coding: utf-8 -*-
"""Taxo 10.10-r7 — employee document requirements, storage and control."""
from __future__ import annotations

import re
import shutil
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

import personnel_registry as registry
import workspace

APP_VERSION = "10.10-r7"
EXPIRING_SOON_DAYS = 30

STATE_OK = "ok"
STATE_NO_DOCUMENT = "no_document"
STATE_DATE_REQUIRED = "date_required"
STATE_EXPIRED = "expired"
STATE_EXPIRING = "expiring"
STATE_NOT_CONTROLLED = "not_controlled"

STATE_LABELS = {
    STATE_OK: "Чинний",
    STATE_NO_DOCUMENT: "Немає чинного документа",
    STATE_DATE_REQUIRED: "Потрібна дата закінчення",
    STATE_EXPIRED: "Прострочений",
    STATE_EXPIRING: "Закінчується ≤30 днів",
    STATE_NOT_CONTROLLED: "Строк не контролюється",
}

PROBLEM_STATES = {
    STATE_NO_DOCUMENT,
    STATE_DATE_REQUIRED,
    STATE_EXPIRED,
    STATE_EXPIRING,
}


def _text(value):
    return str(value or "").strip()


def _date_value(value):
    text = _text(value)
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return False


def ensure_schema_on_connection(con):
    registry.ensure_schema_on_connection(con)
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS employee_document_requirements (
            employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            doc_type TEXT NOT NULL,
            required INTEGER NOT NULL DEFAULT 0,
            expiry_control INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY(employee_id,doc_type)
        );
        CREATE INDEX IF NOT EXISTS idx_employee_document_requirements_control
            ON employee_document_requirements(required,expiry_control,employee_id,doc_type);
        """
    )

    # Preserve the old expiry-warning behavior for existing records that already
    # carried an expiry date. Required remains false until the user explicitly
    # decides it for this employee/document type.
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        """
        INSERT OR IGNORE INTO employee_document_requirements(
            employee_id,doc_type,required,expiry_control,created_at,updated_at
        )
        SELECT employee_id,doc_type,0,1,?,?
          FROM employee_documents
         WHERE TRIM(COALESCE(doc_type,''))<>''
           AND TRIM(COALESCE(expiry_date,''))<>''
         GROUP BY employee_id,doc_type
        """,
        (now, now),
    )


def get_requirement(con, employee_id, doc_type):
    ensure_schema_on_connection(con)
    return con.execute(
        """SELECT * FROM employee_document_requirements
            WHERE employee_id=? AND doc_type=?""",
        (int(employee_id), _text(doc_type)),
    ).fetchone()


def save_requirement(con, employee_id, doc_type, *, required=False, expiry_control=False):
    ensure_schema_on_connection(con)
    doc_type = _text(doc_type)
    if not doc_type:
        raise ValueError("Вкажіть тип документа.")
    now = datetime.now().isoformat(timespec="seconds")
    con.execute(
        """
        INSERT INTO employee_document_requirements(
            employee_id,doc_type,required,expiry_control,created_at,updated_at
        ) VALUES(?,?,?,?,?,?)
        ON CONFLICT(employee_id,doc_type) DO UPDATE SET
            required=excluded.required,
            expiry_control=excluded.expiry_control,
            updated_at=excluded.updated_at
        """,
        (
            int(employee_id),
            doc_type,
            1 if required else 0,
            1 if expiry_control else 0,
            now,
            now,
        ),
    )


def employee_document_storage_root(core):
    paths = workspace.paths_for(core.DATA_ROOT)
    root = paths["employee_documents"]
    root.mkdir(parents=True, exist_ok=True)
    return root


def _safe_filename(name):
    name = Path(str(name or "document")).name
    stem = re.sub(r"[^0-9A-Za-zА-Яа-яІіЇїЄєҐґ._ -]+", "_", name).strip(" .")
    return stem or "document"


def _is_url(value):
    text = _text(value).lower()
    return text.startswith("http://") or text.startswith("https://")


def stored_document_path(core, employee_id, source_value):
    """Copy a local document into Taxo workspace and return a portable DB path.

    Existing workspace copies are reused. HTTP(S) references are returned
    unchanged and reported as not-backed-up to the caller.
    """
    raw = _text(source_value)
    if not raw:
        return "", False
    if _is_url(raw):
        return raw, False

    try:
        source = Path(core.real_data_path(raw))
    except Exception:
        source = Path(raw).expanduser()
    source = source.resolve()
    if not source.is_file():
        raise FileNotFoundError("Файл документа не знайдено: %s" % source)

    root = employee_document_storage_root(core).resolve()
    try:
        source.relative_to(root)
        return core.db_stored_path(source), True
    except ValueError:
        pass

    employee_dir = root / ("employee_%06d" % int(employee_id))
    employee_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = employee_dir / (
        "%s_%s_%s" % (stamp, uuid.uuid4().hex[:8], _safe_filename(source.name))
    )
    shutil.copy2(source, target)
    return core.db_stored_path(target), True


def is_workspace_document(core, value):
    raw = _text(value)
    if not raw or _is_url(raw):
        return False
    try:
        path = Path(core.real_data_path(raw)).resolve()
        root = employee_document_storage_root(core).resolve()
        path.relative_to(root)
        return path.is_file()
    except Exception:
        return False


def migrate_external_document_files(core, con):
    """Copy existing local employee-document files into Taxo workspace."""
    ensure_schema_on_connection(con)
    rows = con.execute(
        """SELECT id,employee_id,file_path FROM employee_documents
            WHERE TRIM(COALESCE(file_path,''))<>'' ORDER BY id"""
    ).fetchall()
    copied = missing = external = already = 0
    for row in rows:
        raw = _text(row["file_path"])
        if _is_url(raw):
            external += 1
            continue
        if is_workspace_document(core, raw):
            already += 1
            continue
        try:
            stored, backed_up = stored_document_path(core, row["employee_id"], raw)
        except FileNotFoundError:
            missing += 1
            continue
        if backed_up:
            con.execute(
                "UPDATE employee_documents SET file_path=?,updated_at=? WHERE id=?",
                (stored, datetime.now().isoformat(timespec="seconds"), row["id"]),
            )
            copied += 1
        else:
            external += 1
    return {
        "copied": copied,
        "missing": missing,
        "external": external,
        "already": already,
    }


def _employee_name(row):
    return " ".join(
        _text(row[key])
        for key in ("last_name", "first_name", "middle_name")
        if _text(row[key])
    )


def _best_active_document(rows, expiry_control, today):
    if not rows:
        return None, STATE_NO_DOCUMENT

    if not expiry_control:
        return rows[0], STATE_NOT_CONTROLLED

    valid_dates = []
    invalid_or_blank = []
    for row in rows:
        expiry = _date_value(row["expiry_date"])
        if isinstance(expiry, date):
            valid_dates.append((expiry, row))
        else:
            invalid_or_blank.append(row)

    if valid_dates:
        valid_dates.sort(key=lambda x: x[0], reverse=True)
        expiry, row = valid_dates[0]
        if expiry < today:
            return row, STATE_EXPIRED
        if expiry <= today + timedelta(days=EXPIRING_SOON_DAYS):
            return row, STATE_EXPIRING
        return row, STATE_OK

    return invalid_or_blank[0], STATE_DATE_REQUIRED


def document_control_rows(con, today=None, problems_only=False):
    ensure_schema_on_connection(con)
    today = today or date.today()
    reqs = con.execute(
        """SELECT r.*,e.last_name,e.first_name,e.middle_name,e.personnel_no,e.active AS employee_active
             FROM employee_document_requirements r
             JOIN employees e ON e.id=r.employee_id
            WHERE COALESCE(r.required,0)=1 OR COALESCE(r.expiry_control,0)=1
         ORDER BY e.active DESC,e.last_name,e.first_name,e.middle_name,r.doc_type"""
    ).fetchall()
    result = []
    for req in reqs:
        docs = con.execute(
            """SELECT * FROM employee_documents
                WHERE employee_id=? AND doc_type=? AND active=1
             ORDER BY expiry_date DESC,id DESC""",
            (req["employee_id"], req["doc_type"]),
        ).fetchall()
        document, state = _best_active_document(
            docs,
            bool(req["expiry_control"]),
            today,
        )
        # Missing optional-but-controlled document is still a control problem;
        # required determines why it matters, not whether it is visible.
        if problems_only and state not in PROBLEM_STATES:
            continue
        result.append({
            "employee_id": int(req["employee_id"]),
            "employee_name": _employee_name(req),
            "personnel_no": _text(req["personnel_no"]),
            "doc_type": _text(req["doc_type"]),
            "required": bool(req["required"]),
            "expiry_control": bool(req["expiry_control"]),
            "document_id": int(document["id"]) if document is not None else None,
            "number": _text(document["number"]) if document is not None else "",
            "expiry_date": _text(document["expiry_date"]) if document is not None else "",
            "file_path": _text(document["file_path"]) if document is not None else "",
            "state": state,
            "state_label": STATE_LABELS[state],
        })
    return result


def install(core, base_app):
    if getattr(core, "_TAXO_1010_R7_EMPLOYEE_DOCUMENT_CONTROL", False):
        return core.App
    core.APP_VERSION = APP_VERSION

    class Taxo1010R7App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            con = core.db()
            try:
                ensure_schema_on_connection(con)
                con.commit()
            finally:
                con.close()
            employee_document_storage_root(core)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

        def open_required_employee_documents_r7(self):
            existing = getattr(self, "_required_employee_documents_r7_window", None)
            try:
                if existing is not None and existing.winfo_exists():
                    existing.lift()
                    return
            except Exception:
                pass

            win = core.tk.Toplevel(self)
            self._required_employee_documents_r7_window = win
            try:
                core.fit_window_to_screen(win, 1240, 760, 860, 560)
            except Exception:
                win.geometry("1240x760")
            win.title("Контроль документів працівників")
            body = core.ttk.Frame(win, padding=12)
            body.pack(fill="both", expand=True)

            core.ttk.Label(
                body,
                text="Контроль обов'язкових документів і строків",
                style="Title.TLabel",
            ).pack(anchor="w")
            core.ttk.Label(
                body,
                text=(
                    "Обов'язковість і контроль строку задаються окремо для кожного працівника та типу документа. "
                    "Архівування старої копії не скасовує вимогу. Якщо строк контролюється, чинна дата закінчення обов'язкова."
                ),
                style="Muted.TLabel",
                wraplength=1180,
                justify="left",
            ).pack(anchor="w", pady=(4, 8))

            problems_only = core.tk.BooleanVar(value=True)
            top = core.ttk.Frame(body)
            top.pack(fill="x", pady=(0, 8))
            core.ttk.Checkbutton(
                top,
                text="Показувати лише проблеми",
                variable=problems_only,
            ).pack(side="left")

            frame = core.ttk.Frame(body)
            frame.pack(fill="both", expand=True)
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            cols = ("employee", "type", "required", "control", "number", "expiry", "state")
            tree = core.ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
            for key, label, width in (
                ("employee", "Працівник", 250),
                ("type", "Документ", 220),
                ("required", "Обов'язк.", 85),
                ("control", "Строк", 85),
                ("number", "Номер", 120),
                ("expiry", "Чинний до", 105),
                ("state", "Стан", 260),
            ):
                tree.heading(key, text=label)
                tree.column(key, width=width, anchor="w")
            sy = core.ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            sx = core.ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
            tree.grid(row=0, column=0, sticky="nsew")
            sy.grid(row=0, column=1, sticky="ns")
            sx.grid(row=1, column=0, sticky="ew")

            for state, color in (
                (STATE_NO_DOCUMENT, "#8A1C1C"),
                (STATE_DATE_REQUIRED, "#8A1C1C"),
                (STATE_EXPIRED, "#8A1C1C"),
                (STATE_EXPIRING, "#7A5B00"),
                (STATE_OK, "#0B5D1E"),
                (STATE_NOT_CONTROLLED, "#365A7A"),
            ):
                tree.tag_configure(state, foreground=color)

            summary_var = core.tk.StringVar(value="")
            core.ttk.Label(body, textvariable=summary_var, style="Muted.TLabel").pack(anchor="w", pady=(6, 0))
            cache = {}

            def refresh():
                for iid in tree.get_children(""):
                    tree.delete(iid)
                cache.clear()
                con = core.db()
                try:
                    rows = document_control_rows(
                        con,
                        problems_only=problems_only.get(),
                    )
                finally:
                    con.close()
                problems = 0
                for idx, row in enumerate(rows):
                    iid = str(idx)
                    cache[iid] = row
                    if row["state"] in PROBLEM_STATES:
                        problems += 1
                    tree.insert(
                        "", "end", iid=iid,
                        values=(
                            row["employee_name"],
                            row["doc_type"],
                            "Так" if row["required"] else "Ні",
                            "Так" if row["expiry_control"] else "Ні",
                            row["number"] or "—",
                            registry.display_date(row["expiry_date"]) if row["expiry_date"] else "—",
                            row["state_label"],
                        ),
                        tags=(row["state"],),
                    )
                summary_var.set("Показано: %d · проблем: %d" % (len(rows), problems))

            def open_employee_document():
                sel = tree.selection()
                if not sel:
                    core.messagebox.showinfo("Документи", "Виберіть рядок.", parent=win)
                    return
                row = cache.get(sel[0])
                if not row:
                    return
                overview = getattr(self, "personnel_overview_tree", None)
                iid = str(row["employee_id"])
                try:
                    if overview is not None and iid in overview.get_children(""):
                        overview.selection_set(iid)
                        overview.focus(iid)
                        overview.see(iid)
                        self.open_personnel_data_center()
                        return
                except Exception:
                    pass
                core.messagebox.showinfo(
                    "Документи",
                    "Відкрийте картку працівника у реєстрі та перейдіть на вкладку «Документи».",
                    parent=win,
                )

            def migrate_files():
                if not core.messagebox.askyesno(
                    "Зібрати файли у сховище Taxo?",
                    "Taxo скопіює знайдені локальні файли документів працівників у власне робоче сховище. "
                    "Оригінали не видаляються. Перед зміною буде створено резервну копію БД.",
                    parent=win,
                ):
                    return
                try:
                    backup = getattr(core, "backup_database", None)
                    if callable(backup):
                        backup("before_employee_document_storage")
                except Exception as exc:
                    core.messagebox.showerror(
                        "Резервна копія",
                        "Не вдалося створити резервну копію. Перенесення скасовано:\n%s" % exc,
                        parent=win,
                    )
                    return

                con = core.db()
                try:
                    result = migrate_external_document_files(core, con)
                    con.commit()
                except Exception as exc:
                    con.rollback()
                    core.messagebox.showerror("Документи", str(exc), parent=win)
                    return
                finally:
                    con.close()
                refresh()
                core.messagebox.showinfo(
                    "Документи",
                    "Скопійовано у сховище: %d\nВже у сховищі: %d\nФайл не знайдено: %d\nЗовнішніх посилань: %d"
                    % (
                        result["copied"],
                        result["already"],
                        result["missing"],
                        result["external"],
                    ),
                    parent=win,
                )

            actions = core.ttk.Frame(body)
            actions.pack(fill="x", pady=(8, 0))
            core.ttk.Button(actions, text="Оновити", command=refresh).pack(side="left")
            core.ttk.Button(actions, text="Відкрити картку / документ", command=open_employee_document).pack(side="left", padx=6)
            core.ttk.Button(actions, text="Зібрати локальні файли у сховище Taxo…", command=migrate_files).pack(side="left", padx=6)
            core.ttk.Button(actions, text="Закрити", command=win.destroy).pack(side="right")
            problems_only.trace_add("write", lambda *_args: refresh())
            refresh()
            win.transient(self)

    Taxo1010R7App.__name__ = "App"
    Taxo1010R7App.__qualname__ = "App"
    core.App = Taxo1010R7App
    core._TAXO_1010_R7_EMPLOYEE_DOCUMENT_CONTROL = True
    return Taxo1010R7App
