# -*- coding: utf-8 -*-
"""UI для документів транспортних засобів.

Дані, строки дії, копіювання файлів і контрольні правила залишаються
у vehicle_documents.py. Цей модуль відповідає тільки за робочі вікна.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from document_viewer import open_document
from workspace import resolved_path
from vehicle_documents import (
    DOCUMENT_TYPES,
    EXPIRY_REQUIRED,
    _vehicle_label,
    archive_current_document_slot,
    control_rows,
    copy_document_file,
    display_date,
    document_status,
    ensure_vehicle_documents_schema,
    fit_window_to_screen,
    iso_date,
    open_external,
    parse_date,
    status_rank,
    vehicle_document_summary,
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
        fit_window_to_screen(self.win, 1120, 680, 820, 500)
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
        fit_window_to_screen(win, 720, 650, 580, 520)
        win.transient(self.win)
        win.grab_set()

        current_type = row["doc_type"] if row is not None else "insurance"
        type_var = tk.StringVar(value=DOCUMENT_TYPES.get(current_type, DOCUMENT_TYPES["insurance"]))
        no_var = tk.StringVar(value=(row["document_no"] or "") if row is not None else "")
        issuer_var = tk.StringVar(value=(row["issuer"] or "") if row is not None else "")
        from_var = tk.StringVar(value=display_date(row["valid_from"]) if row is not None else "")
        until_var = tk.StringVar(value=display_date(row["valid_until"]) if row is not None else "")
        copy_var = tk.StringVar(value="")
        current_copy = (row["copy_path"] or "") if row is not None else ""
        archive_previous = tk.BooleanVar(value=False)

        entries = [
            ("Тип документа", type_var),
            ("Номер / серія", no_var),
            ("Ким видано / страхова", issuer_var),
            ("Дата від, ДД.ММ.РРРР", from_var),
            ("Діє до, ДД.ММ.РРРР", until_var),
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

        notes_row = len(entries)
        ttk.Label(win, text="Примітка").grid(row=notes_row, column=0, sticky="nw", padx=10, pady=7)
        notes_text = tk.Text(win, height=4, wrap="word")
        notes_text.grid(row=notes_row, column=1, sticky="nsew", padx=10, pady=7)
        if row is not None and (row["notes"] or ""):
            notes_text.insert("1.0", row["notes"] or "")

        archive_row = notes_row + 1
        ttk.Checkbutton(
            win,
            text="Вивести інші активні документи цього типу в архів",
            variable=archive_previous,
        ).grid(row=archive_row, column=1, sticky="w", padx=10, pady=(2, 2))
        ttk.Label(
            win,
            text=(
                "За замовчуванням попередні документи не архівуються. "
                "Це дозволяє мати одночасно кілька тимчасових талонів або інших документів одного типу."
            ),
            wraplength=520,
            justify="left",
        ).grid(row=archive_row + 1, column=1, sticky="w", padx=10, pady=(0, 6))

        copy_row = archive_row + 2
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
        win.rowconfigure(notes_row, weight=1)

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
                except (OSError, ValueError) as exc:
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
                    notes_text.get("1.0", "end-1c").strip(),
                    now,
                )
                # Several active documents of the same type may coexist.
                # Archiving siblings is an explicit user choice, never an automatic side effect.
                if archive_previous.get():
                    archive_current_document_slot(
                        con,
                        self.vehicle["id"],
                        dtype,
                        keep_id=(row["id"] if row is not None else None),
                        now=now,
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
                               copy_path=?,notes=?,archived=0,updated_at=?
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
            open_document(self.win, path, external_opener=open_external)
        except OSError as exc:
            messagebox.showerror("Копія документа", f"Не вдалося відкрити файл:\n{exc}", parent=self.win)


def open_vehicle_documents(parent, db_factory, data_root, vehicle, on_change=None):
    return VehicleDocumentsWindow(parent, db_factory, data_root, vehicle, on_change=on_change)


def open_vehicle_document_control(parent, db_factory, data_root, on_open_vehicle=None):
    # Operational control uses only local Taxo vehicle_documents.
    # State-registry reconciliation (e.g. «Шлях») is a separate subsystem and must not alter these statuses.
    win = tk.Toplevel(parent)
    win.title("Контроль документів транспортних засобів")
    fit_window_to_screen(win, 1180, 700, 850, 500)
    win.transient(parent)

    info_var = tk.StringVar(value="")
    only_issues = tk.BooleanVar(value=True)

    top = ttk.Frame(win)
    top.pack(fill="x", padx=10, pady=8)
    ttk.Checkbutton(top, text="Показувати тільки проблеми", variable=only_issues).pack(side="left")
    ttk.Label(top, textvariable=info_var).pack(side="right")

    cols = ("vehicle", "type", "number", "until", "status", "copy")
    table = ttk.Frame(win)
    table.pack(fill="both", expand=True, padx=10, pady=6)
    table.rowconfigure(0, weight=1)
    table.columnconfigure(0, weight=1)
    tree = ttk.Treeview(table, columns=cols, show="headings", height=23)
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
    ybar = ttk.Scrollbar(table, orient="vertical", command=tree.yview)
    xbar = ttk.Scrollbar(table, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
    tree.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    xbar.grid(row=1, column=0, sticky="ew")

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
