# -*- coding: utf-8 -*-
"""Taxo 10.5-r1 UI for the official own-fleet military transport statement."""
from __future__ import annotations

from datetime import date, datetime

import military_transport_statement as statement


def _alive(widget):
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def _walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from _walk(child)


def _find_button(root, text):
    if not _alive(root):
        return None
    for widget in _walk(root):
        try:
            if widget.winfo_class() in ("TButton", "Button") and str(widget.cget("text")) == text:
                return widget
        except Exception:
            pass
    return None


def _parse_day(value):
    text = str(value or "").strip()
    for pattern in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            pass
    raise ValueError("Дата має бути у форматі ДД.ММ.РРРР.")


def _edit_dialog(core, parent, row):
    result = {"value": None}
    win = core.tk.Toplevel(parent)
    win.title("Реквізити ТЗ для відомості")
    try:
        core.fit_window_to_screen(win, 720, 500, 620, 430)
    except Exception:
        win.geometry("720x500")
    body = core.ttk.Frame(win, padding=14)
    body.pack(fill="both", expand=True)
    body.columnconfigure(1, weight=1)
    scope_labels = tuple(statement.SCOPE_LABELS.values())
    scope_rev = {v: k for k, v in statement.SCOPE_LABELS.items()}
    scope_var = core.tk.StringVar(value=statement.SCOPE_LABELS.get(row.get("report_scope"), statement.SCOPE_LABELS[statement.SCOPE_UNKNOWN]))
    type_var = core.tk.StringVar(value=row.get("vehicle_type", ""))
    condition_var = core.tk.StringVar(value=row.get("technical_condition", ""))
    value_var = core.tk.StringVar(value=row.get("residual_value", ""))
    note_var = core.tk.StringVar(value=row.get("statement_note", ""))
    specs = (
        ("Належність до відомості", scope_var, scope_labels),
        ("Тип ТЗ/техніки", type_var, None),
        ("Технічний стан", condition_var, None),
        ("Залишкова балансова вартість, тис. грн", value_var, None),
        ("Примітка", note_var, None),
    )
    for idx, (label, var, values) in enumerate(specs):
        core.ttk.Label(body, text=label).grid(row=idx, column=0, sticky="w", padx=(0, 10), pady=6)
        if values:
            widget = core.ttk.Combobox(body, textvariable=var, values=values, state="readonly")
        else:
            widget = core.ttk.Entry(body, textvariable=var)
        widget.grid(row=idx, column=1, sticky="ew", pady=6)
    core.ttk.Label(
        body,
        text=(
            "Належність до власного/балансового парку задається явно. Taxo не визначає її "
            "за active, «Шлях», нарядом або військовим статусом."
        ),
        style="Muted.TLabel", wraplength=650, justify="left",
    ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 4))
    buttons = core.ttk.Frame(body)
    buttons.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(12, 0))

    def save():
        result["value"] = {
            "report_scope": scope_rev[scope_var.get()],
            "vehicle_type": type_var.get().strip(),
            "technical_condition": condition_var.get().strip(),
            "residual_book_value_thousand_uah": value_var.get().strip(),
            "note": note_var.get().strip(),
        }
        win.destroy()

    core.ttk.Button(buttons, text="Скасувати", command=win.destroy).pack(side="right")
    core.ttk.Button(buttons, text="Зберегти", style="Accent.TButton", command=save).pack(side="right", padx=(0, 8))
    win.transient(parent)
    try:
        win.grab_set()
    except Exception:
        pass
    win.wait_window()
    return result["value"]


def install(core, base_app):
    if getattr(core, "_TAXO_1051_STATEMENT_UI_INSTALLED", False):
        return core.App

    statement.ensure_schema(core)

    class MilitaryTransportStatementApp(base_app):
        def open_military_transport_dashboard(self):
            result = super().open_military_transport_dashboard()
            win = getattr(self, "_military_transport_window", None)
            if _alive(win) and not getattr(win, "_taxo_statement_button_installed", False):
                anchor = _find_button(win, "Зафіксувати подання")
                if anchor is not None:
                    core.ttk.Button(
                        anchor.master,
                        text="Відомість (додаток 1)",
                        command=self.open_military_transport_statement,
                    ).pack(side="left", padx=6)
                    win._taxo_statement_button_installed = True
            return result

        def open_military_transport_statement(self):
            existing = getattr(self, "_military_transport_statement_window", None)
            if _alive(existing):
                existing.lift()
                existing.focus_force()
                return
            win = core.tk.Toplevel(self)
            self._military_transport_statement_window = win
            win.title("Відомість військово-транспортного обліку — додаток 1")
            try:
                core.fit_window_to_screen(win, 1280, 780, 900, 580)
                core.configure_toplevel(win, title=win.title(), minsize=(900, 580))
            except Exception:
                win.geometry("1280x780")
                win.minsize(900, 580)

            body = core.ttk.Frame(win, padding=12)
            body.pack(fill="both", expand=True)
            core.ttk.Label(body, text="Відомість по власному транспорту", style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text=(
                    statement.FORM_REFERENCE + ". До відомості потрапляють тільки ТЗ, для яких явно "
                    "встановлено «Власний / балансовий парк». Наряд або статус «визначено» для цього не потрібні."
                ),
                wraplength=1200, justify="left",
            ).pack(anchor="w", pady=(3, 8))

            top = core.ttk.Frame(body)
            top.pack(fill="x", pady=(0, 8))
            core.ttk.Label(top, text="Станом на:").pack(side="left")
            date_var = core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
            core.ttk.Entry(top, textvariable=date_var, width=14).pack(side="left", padx=(6, 12))
            summary_var = core.tk.StringVar(value="")
            core.ttk.Label(top, textvariable=summary_var, style="Muted.TLabel").pack(side="left")

            table = core.ttk.Frame(body)
            table.pack(fill="both", expand=True)
            table.rowconfigure(0, weight=1)
            table.columnconfigure(0, weight=1)
            cols = ("plate", "name", "scope", "type", "condition", "value", "workers")
            tree = core.ttk.Treeview(table, columns=cols, show="headings", selectmode="browse")
            for key, label, width in (
                ("plate", "Держ. номер", 110),
                ("name", "ТЗ", 220),
                ("scope", "Власний парк", 200),
                ("type", "Тип", 150),
                ("condition", "Технічний стан", 170),
                ("value", "Балансова вартість, тис. грн", 180),
                ("workers", "Працівників", 90),
            ):
                tree.heading(key, text=label)
                tree.column(key, width=width, anchor="w")
            sy = core.ttk.Scrollbar(table, orient="vertical", command=tree.yview)
            sx = core.ttk.Scrollbar(table, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
            tree.grid(row=0, column=0, sticky="nsew")
            sy.grid(row=0, column=1, sticky="ns")
            sx.grid(row=1, column=0, sticky="ew")
            tree.tag_configure("unknown", foreground="#7A5B00")
            tree.tag_configure("own", foreground="#0B5D1E")

            buttons = core.ttk.Frame(body)
            buttons.pack(fill="x", pady=(8, 0))
            rows_by_id = {}

            def report_date():
                return _parse_day(date_var.get())

            def refresh():
                try:
                    day = report_date()
                except Exception as exc:
                    core.messagebox.showerror("Відомість", str(exc), parent=win)
                    return
                for iid in tree.get_children():
                    tree.delete(iid)
                rows_by_id.clear()
                con = core.db()
                try:
                    rows = statement.statement_overview(con, day)
                finally:
                    con.close()
                counts = {statement.SCOPE_UNKNOWN: 0, statement.SCOPE_OWN: 0, statement.SCOPE_EXCLUDED: 0}
                for row in rows:
                    counts[row["report_scope"]] = counts.get(row["report_scope"], 0) + 1
                    iid = str(row["vehicle_id"])
                    rows_by_id[iid] = row
                    tree.insert(
                        "", "end", iid=iid,
                        values=(
                            row["plate"] or "—", row["name"], row["scope_label"],
                            row["vehicle_type"] or "—", row["technical_condition"] or "—",
                            row["residual_value"] or "—", row["worker_count"],
                        ),
                        tags=(row["report_scope"],),
                    )
                summary_var.set(
                    "власних: %d · не включати: %d · потрібно визначити: %d"
                    % (
                        counts.get(statement.SCOPE_OWN, 0),
                        counts.get(statement.SCOPE_EXCLUDED, 0),
                        counts.get(statement.SCOPE_UNKNOWN, 0),
                    )
                )

            def selected_row():
                sel = tree.selection()
                if not sel:
                    core.messagebox.showinfo("Відомість", "Виберіть транспортний засіб.", parent=win)
                    return None, None
                iid = sel[0]
                return int(iid), rows_by_id.get(iid)

            def edit():
                vehicle_id, row = selected_row()
                if vehicle_id is None:
                    return
                data = _edit_dialog(core, win, row)
                if not data:
                    return
                con = core.db()
                try:
                    statement.set_vehicle_statement_data(con, vehicle_id, **data)
                    con.commit()
                except Exception as exc:
                    con.rollback()
                    core.messagebox.showerror("Відомість", str(exc), parent=win)
                    return
                finally:
                    con.close()
                refresh()
                if str(vehicle_id) in tree.get_children():
                    tree.selection_set(str(vehicle_id))
                    tree.see(str(vehicle_id))

            def set_scope(scope):
                vehicle_id, row = selected_row()
                if vehicle_id is None:
                    return
                con = core.db()
                try:
                    current = statement.get_vehicle_statement_data(con, vehicle_id)
                    statement.set_vehicle_statement_data(
                        con,
                        vehicle_id,
                        report_scope=scope,
                        vehicle_type=(current["vehicle_type"] if current else row.get("vehicle_type", "")),
                        technical_condition=(current["technical_condition"] if current else row.get("technical_condition", "")),
                        residual_book_value_thousand_uah=(current["residual_book_value_thousand_uah"] if current else row.get("residual_value", "")),
                        note=(current["note"] if current else row.get("statement_note", "")),
                    )
                    con.commit()
                finally:
                    con.close()
                refresh()

            def export(kind):
                try:
                    day = report_date()
                except Exception as exc:
                    core.messagebox.showerror("Відомість", str(exc), parent=win)
                    return
                con = core.db()
                try:
                    rows = statement.collect_statement_rows(con, day)
                    issues = statement.statement_issues(con, day)
                    company = statement.company_details(con)
                finally:
                    con.close()
                if not rows:
                    core.messagebox.showinfo(
                        "Відомість",
                        "Немає жодного ТЗ, явно позначеного як «Власний / балансовий парк».",
                        parent=win,
                    )
                    return
                if issues:
                    preview = "\n".join("• " + item for item in issues[:12])
                    if len(issues) > 12:
                        preview += "\n• … ще %d" % (len(issues) - 12)
                    if not core.messagebox.askyesno(
                        "Неповні дані",
                        "У відомості є незаповнені або невизначені дані:\n\n%s\n\nСформувати документ з порожніми полями?" % preview,
                        parent=win,
                    ):
                        return
                stamp = day
                out_dir = core.OUTPUT_DIR
                out_dir.mkdir(parents=True, exist_ok=True)
                if kind == "xlsx":
                    path = out_dir / ("Відомість_ВТО_додаток_1_%s.xlsx" % stamp)
                    try:
                        statement.export_statement_xlsx(path, day, company, rows)
                    except Exception as exc:
                        core.messagebox.showerror("Відомість XLSX", str(exc), parent=win)
                        return
                else:
                    path = out_dir / ("Відомість_ВТО_додаток_1_%s.pdf" % stamp)
                    font_path = next((p for p in core.report_font_candidates() if core.Path(p).exists()), None)
                    try:
                        statement.export_statement_pdf(path, day, company, rows, font_path=font_path)
                    except Exception as exc:
                        core.messagebox.showerror("Відомість PDF", str(exc), parent=win)
                        return
                core.messagebox.showinfo("Відомість", "Сформовано:\n%s" % path, parent=win)
                try:
                    core.open_external(path)
                except Exception:
                    pass

            core.ttk.Button(buttons, text="Редагувати реквізити", style="Accent.TButton", command=edit).pack(side="left")
            core.ttk.Button(buttons, text="Власний / балансовий", command=lambda: set_scope(statement.SCOPE_OWN)).pack(side="left", padx=5)
            core.ttk.Button(buttons, text="Не включати", command=lambda: set_scope(statement.SCOPE_EXCLUDED)).pack(side="left", padx=5)
            core.ttk.Button(buttons, text="Оновити", command=refresh).pack(side="left", padx=5)
            core.ttk.Button(buttons, text="XLSX", command=lambda: export("xlsx")).pack(side="right")
            core.ttk.Button(buttons, text="PDF", command=lambda: export("pdf")).pack(side="right", padx=(0, 6))
            core.ttk.Label(
                body,
                text=(
                    "Формування документа не означає, що його подано. Факт подання й вихідний реквізит "
                    "фіксуються окремо у вкладці «Відомості 20.06 / 20.12»."
                ),
                style="Muted.TLabel", wraplength=1200, justify="left",
            ).pack(anchor="w", pady=(8, 0))
            tree.bind("<Double-1>", lambda _event: edit())
            refresh()
            win.transient(self)

    core._TAXO_1051_STATEMENT_UI_INSTALLED = True
    core.App = MilitaryTransportStatementApp
    return MilitaryTransportStatementApp
