# -*- coding: utf-8 -*-
"""UI-звіт стану документів транспортних засобів.

Винесено з main.py у 10.15-r8 без зміни схеми, форматів даних або правил
визначення стану документів. main.py лишається тонкою точкою підключення.
"""

from __future__ import annotations

from datetime import date, datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from document_viewer import open_document
from output_files import open_external
from vehicle_documents import (
    display_date,
    ensure_vehicle_documents_schema,
    export_vehicle_document_report_pdf,
    export_vehicle_document_report_xlsx,
    vehicle_document_report_rows,
)


def parse_report_date(value):
    try:
        return datetime.strptime(str(value).strip(), "%d.%m.%Y").date()
    except ValueError as exc:
        raise ValueError("Дата має бути у форматі ДД.ММ.РРРР.") from exc


def report_snapshot(rows, only_issues=False):
    rows = list(rows)
    visible = [row for row in rows if not only_issues or row["rank"] < 3]
    vehicles = {}
    for row in rows:
        vehicles[row["vehicle_id"]] = row["overall"]
    problems = sum(1 for value in vehicles.values() if value == "Проблема")
    warnings = sum(1 for value in vehicles.values() if value == "Увага")
    actual = sum(1 for value in vehicles.values() if value == "Актуально")
    summary = (
        f"Авто: {len(vehicles)}   Проблема: {problems}   "
        f"Увага: {warnings}   Актуально: {actual}   "
        f"Позицій у таблиці: {len(visible)}"
    )
    return visible, summary


def open_vehicle_documents_report(
    app,
    db_factory,
    output_dir,
    *,
    calendar_button,
    fit_window_to_screen,
    write_output_file,
):
    existing = getattr(app, "vehicle_documents_report_win", None)
    if existing is not None:
        try:
            if existing.winfo_exists():
                existing.lift()
                return
        except tk.TclError:
            pass

    win = tk.Toplevel(app)
    app.vehicle_documents_report_win = win
    fit_window_to_screen(win, 1320, 760, 900, 540)
    app._decorate_secondary_window(
        win,
        "Стан документів транспортних засобів",
        "Контроль строків і комплектності документів",
    )

    top = ttk.Frame(win, padding=(10, 8))
    top.pack(fill="x")
    report_date = tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
    active_only = tk.BooleanVar(value=True)
    only_issues = tk.BooleanVar(value=False)
    summary = tk.StringVar(value="")
    cache = {"rows": [], "date": date.today()}

    ttk.Label(top, text="Стан документів на дату:").pack(side="left")
    ttk.Entry(top, textvariable=report_date, width=12).pack(side="left", padx=(5, 3))
    calendar_button(top, report_date).pack(side="left", padx=(0, 10))
    ttk.Checkbutton(top, text="Тільки авто в експлуатації", variable=active_only).pack(side="left", padx=8)
    ttk.Checkbutton(top, text="Тільки проблемні / попередження", variable=only_issues).pack(side="left", padx=8)

    table_frame = ttk.Frame(win, padding=(10, 0, 10, 6))
    table_frame.pack(fill="both", expand=True)
    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)
    cols = ("vehicle", "overall", "document", "number", "from", "until", "status", "copy")
    tree = ttk.Treeview(table_frame, columns=cols, show="headings")
    heads = {
        "vehicle": "Автомобіль", "overall": "Загальний стан", "document": "Документ",
        "number": "№ / серія", "from": "Від", "until": "Діє до", "status": "Стан", "copy": "Копія",
    }
    widths = {
        "vehicle": 250, "overall": 115, "document": 285, "number": 130,
        "from": 90, "until": 90, "status": 160, "copy": 70,
    }
    for key in cols:
        tree.heading(key, text=heads[key])
        tree.column(key, width=widths[key], anchor="w")
    ybar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    xbar = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
    tree.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    xbar.grid(row=1, column=0, sticky="ew")
    tree.tag_configure("problem", background="#FCE8E6")
    tree.tag_configure("warning", background="#FFF4D6")

    footer = ttk.Frame(win, padding=(10, 4, 10, 10))
    footer.pack(fill="x")
    ttk.Label(footer, textvariable=summary).pack(side="left")

    def load_rows(show_error=True):
        try:
            target = parse_report_date(report_date.get())
        except ValueError as exc:
            if show_error:
                messagebox.showerror("Звіт документів авто", str(exc), parent=win)
            return None
        con = db_factory()
        try:
            ensure_vehicle_documents_schema(con)
            rows = vehicle_document_report_rows(con, target, active_only=bool(active_only.get()))
        finally:
            con.close()
        cache["rows"] = rows
        cache["date"] = target
        return rows

    def refresh():
        rows = load_rows()
        if rows is None:
            return
        for item in tree.get_children():
            tree.delete(item)
        visible, summary_text = report_snapshot(rows, bool(only_issues.get()))
        for index, row in enumerate(visible):
            tag = "problem" if row["rank"] <= 1 else ("warning" if row["rank"] == 2 else "")
            tree.insert(
                "", "end", iid=f"v{index}",
                values=(
                    row["vehicle"], row["overall"], row["type_label"], row["document_no"],
                    display_date(row["valid_from"]), display_date(row["valid_until"]), row["status"],
                    "Є" if row["copy"] else "Немає",
                ),
                tags=((tag,) if tag else ()),
            )
        summary.set(summary_text)

    def export_report(kind):
        rows = load_rows()
        if rows is None:
            return
        if only_issues.get():
            rows = [row for row in rows if row["rank"] < 3]
        target = cache["date"]
        suffix = ".pdf" if kind == "pdf" else ".xlsx"
        initial = f"Стан_документів_авто_{target.isoformat()}{suffix}"
        path = filedialog.asksaveasfilename(
            parent=win,
            title="Зберегти звіт стану документів авто",
            initialdir=str(output_dir),
            initialfile=initial,
            defaultextension=suffix,
            filetypes=[("PDF", "*.pdf")] if kind == "pdf" else [("Excel", "*.xlsx")],
        )
        if not path:
            return
        company = app._company_name_value()
        writer = (
            (lambda out: export_vehicle_document_report_pdf(rows, target, out, company_name=company))
            if kind == "pdf"
            else (lambda out: export_vehicle_document_report_xlsx(rows, target, out, company_name=company))
        )
        actual_path = write_output_file(
            writer, path, parent=win,
            kind="PDF звіту документів авто" if kind == "pdf" else "Excel звіту документів авто",
            error_title="Звіт документів авто",
        )
        if actual_path is None:
            return
        try:
            if kind == "pdf":
                open_document(win, actual_path, external_opener=open_external)
            else:
                open_external(actual_path)
        except Exception as exc:
            messagebox.showwarning(
                "Звіт документів авто",
                f"Файл створено, але не вдалося відкрити його автоматично:\n{actual_path}\n\n{exc}",
                parent=win,
            )

    ttk.Button(footer, text="Оновити", command=refresh).pack(side="right", padx=3)
    ttk.Button(footer, text="Excel", command=lambda: export_report("xlsx")).pack(side="right", padx=3)
    ttk.Button(footer, text="PDF", style="Accent.TButton", command=lambda: export_report("pdf")).pack(side="right", padx=3)
    ttk.Button(footer, text="Закрити", command=win.destroy).pack(side="right", padx=(10, 3))

    active_only.trace_add("write", lambda *_args: refresh())
    only_issues.trace_add("write", lambda *_args: refresh())
    refresh()
    return None
