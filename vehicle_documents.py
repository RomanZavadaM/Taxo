# -*- coding: utf-8 -*-
"""Документи транспортних засобів: копії, строки дії та контроль актуальності."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from workspace import paths_for, resolved_path, stored_path


DOCUMENT_TYPES = {
    "insurance": "Страховка",
    "inspection": "Діагностика / техконтроль",
    "temporary_registration": "Тимчасовий реєстраційний документ",
    "registration_certificate": "Техпаспорт / свідоцтво про реєстрацію",
}

EXPIRY_REQUIRED = {"insurance", "inspection", "temporary_registration"}
WARNING_DAYS = 30


def parse_date(value):
    text = str(value or "").strip()
    if not text:
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError("Дата має бути у форматі ДД.ММ.РРРР.")


def iso_date(value):
    parsed = parse_date(value)
    return parsed.isoformat() if parsed else ""


def display_date(value):
    parsed = parse_date(value)
    return parsed.strftime("%d.%m.%Y") if parsed else ""


def document_status(doc_type, valid_until, today=None, warning_days=WARNING_DAYS):
    today = today or date.today()
    text = str(valid_until or "").strip()
    if not text:
        if doc_type in EXPIRY_REQUIRED:
            return "Немає дати дії"
        return "Актуальний"
    try:
        deadline = parse_date(text)
    except ValueError:
        return "Помилка дати"
    days = (deadline - today).days
    if days < 0:
        return "Прострочений"
    if days <= int(warning_days):
        return f"Закінчується: {days} дн."
    return "Актуальний"


def status_rank(status):
    value = str(status or "")
    if value == "Прострочений":
        return 0
    if value in ("Відсутній", "Немає дати дії", "Помилка дати"):
        return 1
    if value.startswith("Закінчується:"):
        return 2
    return 3


def ensure_vehicle_documents_schema(con):
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS vehicle_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
            doc_type TEXT NOT NULL,
            document_no TEXT DEFAULT '',
            issuer TEXT DEFAULT '',
            valid_from TEXT DEFAULT '',
            valid_until TEXT DEFAULT '',
            copy_path TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            archived INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_vehicle_documents_vehicle
            ON vehicle_documents(vehicle_id, doc_type, archived, id);
        """
    )


def latest_documents(con, vehicle_id):
    rows = con.execute(
        """
        SELECT *
          FROM vehicle_documents
         WHERE vehicle_id=? AND COALESCE(archived,0)=0
         ORDER BY id DESC
        """,
        (int(vehicle_id),),
    ).fetchall()
    latest = {}
    for row in rows:
        dtype = row["doc_type"]
        if dtype not in latest:
            latest[dtype] = row
    return latest


def vehicle_document_summary(con, vehicle_id, today=None):
    latest = latest_documents(con, vehicle_id)
    details = []
    for dtype, label in DOCUMENT_TYPES.items():
        row = latest.get(dtype)
        status = "Відсутній" if row is None else document_status(dtype, row["valid_until"], today=today)
        details.append((dtype, label, row, status))
    worst = min((status_rank(x[3]) for x in details), default=3)
    if worst <= 1:
        overall = "Проблема"
    elif worst == 2:
        overall = "Увага"
    else:
        overall = "Актуально"
    return overall, details


def vehicle_document_summary_text(con, vehicle_id, today=None):
    overall, details = vehicle_document_summary(con, vehicle_id, today=today)
    issues = [label for _dtype, label, _row, status in details if status_rank(status) < 3]
    return overall if not issues else f"{overall}: {', '.join(issues)}"


def control_rows(con, active_only=True, today=None):
    sql = "SELECT * FROM vehicles"
    if active_only:
        sql += " WHERE active=1"
    sql += " ORDER BY active DESC,name,plate"
    vehicles = con.execute(sql).fetchall()
    rows = []
    for vehicle in vehicles:
        _overall, details = vehicle_document_summary(con, vehicle["id"], today=today)
        vehicle_name = " — ".join(
            x for x in (vehicle["name"], vehicle["plate"], vehicle["make_model"]) if str(x or "").strip()
        )
        for dtype, label, doc, status in details:
            rows.append(
                {
                    "vehicle_id": vehicle["id"],
                    "vehicle": vehicle_name,
                    "doc_type": dtype,
                    "type_label": label,
                    "document_no": "" if doc is None else (doc["document_no"] or ""),
                    "valid_until": "" if doc is None else (doc["valid_until"] or ""),
                    "status": status,
                    "copy_path": "" if doc is None else (doc["copy_path"] or ""),
                    "rank": status_rank(status),
                }
            )
    rows.sort(key=lambda x: (x["rank"], x["vehicle"].casefold(), x["type_label"].casefold()))
    return rows


def _safe_name(value):
    text = re.sub(r"[^0-9A-Za-zА-Яа-яІіЇїЄє._ -]+", "_", str(value or "").strip())
    text = re.sub(r"\s+", " ", text).strip(" .")
    return text or "document"


def copy_document_file(data_root, vehicle_id, doc_type, source):
    source = Path(source)
    if not source.is_file():
        raise FileNotFoundError(str(source))
    root = paths_for(data_root)["vehicle_documents"] / str(int(vehicle_id)) / str(doc_type)
    root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    target = root / f"{stamp}_{_safe_name(source.name)}"
    shutil.copy2(source, target)
    return stored_path(target, data_root)


def open_external(path):
    target = str(path)
    if os.name == "nt":
        os.startfile(target)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", target])
    else:
        subprocess.Popen(["xdg-open", target])


def _vehicle_label(vehicle):
    return " — ".join(
        x for x in (vehicle["name"], vehicle["plate"], vehicle["make_model"]) if str(x or "").strip()
    )


class VehicleDocumentsWindow:
    def __init__(self, parent, db_factory, data_root, vehicle, on_change=None):
        self.parent = parent
        self.db_factory = db_factory
        self.data_root = data_root
        self.vehicle = vehicle
        self.on_change = on_change
        self.show_archived = tk.BooleanVar(value=False)

        self.win = tk.Toplevel(parent)
        self.win.title(f"Документи авто — {_vehicle_label(vehicle)}")
        self.win.geometry("1050x650")
        self.win.minsize(820, 500)
        self.win.transient(parent)

        self.summary_var = tk.StringVar(value="")
        self._build()
        self.load()

    def _build(self):
        header = ttk.Frame(self.win)
        header.pack(fill="x", padx=10, pady=(10, 4))
        ttk.Label(header, text=_vehicle_label(self.vehicle), font=("TkDefaultFont", 11, "bold")).pack(side="left")
        ttk.Label(header, textvariable=self.summary_var).pack(side="right")

        actions = ttk.Frame(self.win)
        actions.pack(fill="x", padx=10, pady=4)
        ttk.Button(actions, text="Додати документ", command=self.add_document).pack(side="left", padx=3)
        ttk.Button(actions, text="Редагувати", command=self.edit_document).pack(side="left", padx=3)
        ttk.Button(actions, text="Архівувати", command=self.archive_document).pack(side="left", padx=3)
        ttk.Button(actions, text="Відкрити копію", command=self.open_copy).pack(side="left", padx=3)
        ttk.Button(actions, text="Оновити", command=self.load).pack(side="left", padx=3)
        ttk.Checkbutton(
            actions,
            text="Показувати архів",
            variable=self.show_archived,
            command=self.load,
        ).pack(side="right", padx=3)

        cols = ("id", "type", "number", "issuer", "from", "until", "status", "copy", "notes")
        self.tree = ttk.Treeview(self.win, columns=cols, show="headings", height=20)
        heads = {
            "id": "ID",
            "type": "Документ",
            "number": "№",
            "issuer": "Ким видано / страхова",
            "from": "Від",
            "until": "Діє до",
            "status": "Стан",
            "copy": "Копія",
            "notes": "Примітка",
        }
        widths = {
            "id": 45,
            "type": 235,
            "number": 120,
            "issuer": 190,
            "from": 90,
            "until": 90,
            "status": 145,
            "copy": 80,
            "notes": 220,
        }
        for col in cols:
            self.tree.heading(col, text=heads[col])
            self.tree.column(col, width=widths[col], anchor="w")
        ybar = ttk.Scrollbar(self.win, orient="vertical", command=self.tree.yview)
        xbar = ttk.Scrollbar(self.win, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        xbar.pack(side="bottom", fill="x", padx=10, pady=(0, 8))
        ybar.pack(side="right", fill="y", pady=6)
        self.tree.pack(fill="both", expand=True, padx=(10, 0), pady=6)
        self.tree.bind("<Double-1>", lambda _event: self.edit_document())
        self.tree.bind("<Return>", lambda _event: self.edit_document())

    def _selected_id(self):
        selected = self.tree.selection()
        if not selected:
            return None
        return int(self.tree.item(selected[0], "values")[0])

    def _selected_row(self):
        rid = self._selected_id()
        if not rid:
            return None
        con = self.db_factory()
        try:
            return con.execute("SELECT * FROM vehicle_documents WHERE id=?", (rid,)).fetchone()
        finally:
            con.close()

    def load(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        con = self.db_factory()
        try:
            ensure_vehicle_documents_schema(con)
            overall, details = vehicle_document_summary(con, self.vehicle["id"])
            issues = [label for _dtype, label, _row, status in details if status_rank(status) < 3]
            self.summary_var.set(overall if not issues else f"{overall}: {', '.join(issues)}")
            sql = "SELECT * FROM vehicle_documents WHERE vehicle_id=?"
            params = [self.vehicle["id"]]
            if not self.show_archived.get():
                sql += " AND COALESCE(archived,0)=0"
            sql += " ORDER BY archived,id DESC"
            rows = con.execute(sql, params).fetchall()
        finally:
            con.close()

        for row in rows:
            archived = bool(row["archived"])
            status = "Архів" if archived else document_status(row["doc_type"], row["valid_until"])
            self.tree.insert(
                "",
                "end",
                values=(
                    row["id"],
                    DOCUMENT_TYPES.get(row["doc_type"], row["doc_type"]),
                    row["document_no"] or "",
                    row["issuer"] or "",
                    display_date(row["valid_from"]),
                    display_date(row["valid_until"]),
                    status,
                    "Є" if row["copy_path"] else "Немає",
                    row["notes"] or "",
                ),
            )

    def add_document(self):
        self._form()

    def edit_document(self):
        row = self._selected_row()
        if row is not None:
            self._form(row)

    def _form(self, row=None):
        win = tk.Toplevel(self.win)
        win.title("Документ транспортного засобу")
        win.geometry("660x520")
        win.minsize(560, 460)
        win.transient(self.win)
        win.grab_set()

        current_type = row["doc_type"] if row is not None else "insurance"
        type_var = tk.StringVar(value=DOCUMENT_TYPES.get(current_type, DOCUMENT_TYPES["insurance"]))
        no_var = tk.StringVar(value=(row["document_no"] or "") if row is not None else "")
        issuer_var = tk.StringVar(value=(row["issuer"] or "") if row is not None else "")
        from_var = tk.StringVar(value=display_date(row["valid_from"]) if row is not None else "")
        until_var = tk.StringVar(value=display_date(row["valid_until"]) if row is not None else "")
        notes_var = tk.StringVar(value=(row["notes"] or "") if row is not None else "")
        copy_var = tk.StringVar(value="")
        current_copy = (row["copy_path"] or "") if row is not None else ""

        entries = [
            ("Тип документа", type_var),
            ("Номер / серія", no_var),
            ("Ким видано / страхова", issuer_var),
            ("Дата від, ДД.ММ.РРРР", from_var),
            ("Діє до, ДД.ММ.РРРР", until_var),
            ("Примітка", notes_var),
        ]
        for i, (label, var) in enumerate(entries):
            ttk.Label(win, text=label).grid(row=i, column=0, sticky="w", padx=10, pady=7)
            if i == 0:
                ttk.Combobox(
                    win,
                    textvariable=var,
                    values=list(DOCUMENT_TYPES.values()),
                    state="readonly",
                    width=46,
                ).grid(row=i, column=1, sticky="ew", padx=10, pady=7)
            else:
                ttk.Entry(win, textvariable=var, width=50).grid(row=i, column=1, sticky="ew", padx=10, pady=7)

        copy_row = len(entries)
        ttk.Label(win, text="Копія документа").grid(row=copy_row, column=0, sticky="w", padx=10, pady=7)
        copy_frame = ttk.Frame(win)
        copy_frame.grid(row=copy_row, column=1, sticky="ew", padx=10, pady=7)
        ttk.Entry(copy_frame, textvariable=copy_var, state="readonly").pack(side="left", fill="x", expand=True)

        def choose_copy():
            path = filedialog.askopenfilename(
                parent=win,
                title="Виберіть копію документа",
                filetypes=[
                    ("Документи та зображення", "*.pdf *.jpg *.jpeg *.png *.tif *.tiff"),
                    ("Усі файли", "*.*"),
                ],
            )
            if path:
                copy_var.set(path)

        ttk.Button(copy_frame, text="Вибрати…", command=choose_copy).pack(side="left", padx=(5, 0))
        if current_copy:
            ttk.Label(
                win,
                text="Поточна копія збережена. Виберіть новий файл лише якщо потрібно її замінити.",
            ).grid(row=copy_row + 1, column=1, sticky="w", padx=10, pady=(0, 5))

        win.columnconfigure(1, weight=1)

        def save():
            dtype = next((k for k, v in DOCUMENT_TYPES.items() if v == type_var.get()), None)
            if not dtype:
                messagebox.showerror("Документ", "Виберіть тип документа.", parent=win)
                return
            try:
                valid_from = iso_date(from_var.get())
                valid_until = iso_date(until_var.get())
            except ValueError as exc:
                messagebox.showerror("Документ", str(exc), parent=win)
                return
            if dtype in EXPIRY_REQUIRED and not valid_until:
                messagebox.showerror("Документ", "Для цього документа вкажіть дату «Діє до».", parent=win)
                return
            if valid_from and valid_until and valid_until < valid_from:
                messagebox.showerror("Документ", "Дата закінчення не може бути раніше дати початку.", parent=win)
                return

            copy_path = current_copy
            if copy_var.get().strip():
                try:
                    copy_path = copy_document_file(
                        self.data_root,
                        self.vehicle["id"],
                        dtype,
                        copy_var.get().strip(),
                    )
                except OSError as exc:
                    messagebox.showerror("Документ", f"Не вдалося зберегти копію:\n{exc}", parent=win)
                    return

            now = datetime.now().isoformat(timespec="seconds")
            con = self.db_factory()
            try:
                ensure_vehicle_documents_schema(con)
                values = (
                    dtype,
                    no_var.get().strip(),
                    issuer_var.get().strip(),
                    valid_from,
                    valid_until,
                    copy_path,
                    notes_var.get().strip(),
                    now,
                )
                if row is None:
                    con.execute(
                        """
                        INSERT INTO vehicle_documents(
                            vehicle_id,doc_type,document_no,issuer,valid_from,valid_until,
                            copy_path,notes,archived,created_at,updated_at
                        ) VALUES(?,?,?,?,?,?,?,?,0,?,?)
                        """,
                        (self.vehicle["id"],) + values[:-1] + (now, now),
                    )
                else:
                    con.execute(
                        """
                        UPDATE vehicle_documents
                           SET doc_type=?,document_no=?,issuer=?,valid_from=?,valid_until=?,
                               copy_path=?,notes=?,updated_at=?
                         WHERE id=?
                        """,
                        values + (row["id"],),
                    )
                con.commit()
            finally:
                con.close()
            win.destroy()
            self.load()
            if self.on_change:
                self.on_change()

        ttk.Button(win, text="Зберегти", command=save).grid(
            row=copy_row + 2, column=1, sticky="e", padx=10, pady=16
        )

    def archive_document(self):
        row = self._selected_row()
        if row is None:
            return
        if not messagebox.askyesno(
            "Архів",
            "Перенести цей запис документа в архів? Копія файла залишиться у сховищі.",
            parent=self.win,
        ):
            return
        con = self.db_factory()
        try:
            con.execute(
                "UPDATE vehicle_documents SET archived=1,updated_at=? WHERE id=?",
                (datetime.now().isoformat(timespec="seconds"), row["id"]),
            )
            con.commit()
        finally:
            con.close()
        self.load()
        if self.on_change:
            self.on_change()

    def open_copy(self):
        row = self._selected_row()
        if row is None:
            return
        if not row["copy_path"]:
            messagebox.showinfo("Копія документа", "Для цього запису копія не збережена.", parent=self.win)
            return
        path = resolved_path(row["copy_path"], self.data_root)
        if not path or not Path(path).is_file():
            messagebox.showerror("Копія документа", "Файл копії не знайдено у робочому сховищі.", parent=self.win)
            return
        try:
            open_external(path)
        except OSError as exc:
            messagebox.showerror("Копія документа", f"Не вдалося відкрити файл:\n{exc}", parent=self.win)


def open_vehicle_documents(parent, db_factory, data_root, vehicle, on_change=None):
    return VehicleDocumentsWindow(parent, db_factory, data_root, vehicle, on_change=on_change)


def open_vehicle_document_control(parent, db_factory, data_root, on_open_vehicle=None):
    win = tk.Toplevel(parent)
    win.title("Контроль документів транспортних засобів")
    win.geometry("1100x680")
    win.minsize(850, 500)
    win.transient(parent)

    info_var = tk.StringVar(value="")
    only_issues = tk.BooleanVar(value=True)

    top = ttk.Frame(win)
    top.pack(fill="x", padx=10, pady=8)
    ttk.Checkbutton(top, text="Показувати тільки проблеми", variable=only_issues).pack(side="left")
    ttk.Label(top, textvariable=info_var).pack(side="right")

    cols = ("vehicle", "type", "number", "until", "status", "copy")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=23)
    heads = {
        "vehicle": "Автомобіль",
        "type": "Документ",
        "number": "№",
        "until": "Діє до",
        "status": "Стан",
        "copy": "Копія",
    }
    widths = {"vehicle": 260, "type": 250, "number": 130, "until": 100, "status": 150, "copy": 80}
    for col in cols:
        tree.heading(col, text=heads[col])
        tree.column(col, width=widths[col], anchor="w")
    ybar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=ybar.set)
    ybar.pack(side="right", fill="y", pady=6)
    tree.pack(fill="both", expand=True, padx=(10, 0), pady=6)

    row_map = {}

    def load():
        for item in tree.get_children():
            tree.delete(item)
        row_map.clear()
        con = db_factory()
        try:
            ensure_vehicle_documents_schema(con)
            rows = control_rows(con, active_only=True)
        finally:
            con.close()
        visible = [r for r in rows if (r["rank"] < 3 or not only_issues.get())]
        for idx, row in enumerate(visible):
            iid = f"r{idx}"
            row_map[iid] = row
            tree.insert(
                "",
                "end",
                iid=iid,
                values=(
                    row["vehicle"],
                    row["type_label"],
                    row["document_no"],
                    display_date(row["valid_until"]),
                    row["status"],
                    "Є" if row["copy_path"] else "Немає",
                ),
            )
        issue_count = sum(1 for r in rows if r["rank"] < 3)
        info_var.set(f"Проблемних позицій: {issue_count}")

    def open_selected_vehicle():
        selected = tree.selection()
        if not selected or not on_open_vehicle:
            return
        row = row_map.get(selected[0])
        if row:
            on_open_vehicle(row["vehicle_id"])

    buttons = ttk.Frame(win)
    buttons.pack(fill="x", padx=10, pady=(0, 10))
    ttk.Button(buttons, text="Відкрити документи авто", command=open_selected_vehicle).pack(side="left", padx=3)
    ttk.Button(buttons, text="Оновити", command=load).pack(side="left", padx=3)
    ttk.Button(buttons, text="Закрити", command=win.destroy).pack(side="right", padx=3)
    tree.bind("<Double-1>", lambda _event: open_selected_vehicle())
    only_issues.trace_add("write", lambda *_args: load())
    load()
    return win
