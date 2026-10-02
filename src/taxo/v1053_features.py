# -*- coding: utf-8 -*-
"""Taxo 10.5-r3 — unified employee document register UI."""
from __future__ import annotations

from pathlib import Path

import employee_document_register as docreg
import personnel_registry as personnel
from v1045_features import _document_editor

APP_VERSION = "10.5-r3"


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
    for widget in _walk(root):
        try:
            if widget.winfo_class() in ("TButton", "Button") and str(widget.cget("text")) == text:
                return widget
        except Exception:
            pass
    return None


def _configure_window(core, win, title, width=1320, height=780):
    win.title(title)
    try:
        core.fit_window_to_screen(win, width, height, min(width, 860), min(height, 540))
    except Exception:
        win.geometry("%dx%d" % (width, height))
        win.minsize(min(width, 860), min(height, 540))
    try:
        core.configure_toplevel(win, title=title, minsize=(min(width, 860), min(height, 540)))
    except Exception:
        pass


def install(core, base_app):
    if getattr(core, "_TAXO_1053_INSTALLED", False):
        return core.App
    core.APP_VERSION = APP_VERSION

    class Taxo1053App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            personnel.ensure_schema(core)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)
            self._install_employee_document_register_action()

        def _install_employee_document_register_action(self):
            root = getattr(self, "personnel_overview_page", None)
            if not _alive(root) or getattr(self, "_employee_document_register_installed", False):
                return
            anchor = _find_button(root, "Дані та документи…") or _find_button(root, "Новий працівник")
            if anchor is None:
                return
            core.ttk.Button(
                anchor.master,
                text="Реєстр документів",
                command=self.open_employee_document_register,
            ).pack(side="right", padx=(8, 0))
            self._employee_document_register_installed = True

        def open_employee_document_register(self):
            win = core.tk.Toplevel(self)
            _configure_window(core, win, "Реєстр документів працівників", 1360, 800)
            body = core.ttk.Frame(win, padding=12)
            body.pack(fill="both", expand=True)

            core.ttk.Label(body, text="Реєстр документів працівників", style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text=("Один реєстр для ручних документів і реквізитів, отриманих з державних XLSX. "
                      "Відсутність документа у наступному державному витягу не видаляє і не архівує запис Taxo. "
                      "Стан строку є інформаційним контролем; «закінчується» означає ≤30 днів."),
                style="Muted.TLabel", wraplength=1280, justify="left",
            ).pack(anchor="w", pady=(3, 10))

            filters = core.ttk.LabelFrame(body, text="Пошук і фільтри", padding=8)
            filters.pack(fill="x", pady=(0, 8))
            filters.columnconfigure(1, weight=1)

            search_var = core.tk.StringVar(value="")
            type_var = core.tk.StringVar(value="Усі типи")
            state_var = core.tk.StringVar(value="Усі стани")
            source_var = core.tk.StringVar(value=docreg.SOURCE_LABELS[docreg.SOURCE_ALL])
            archived_var = core.tk.BooleanVar(value=False)

            core.ttk.Label(filters, text="Пошук").grid(row=0, column=0, sticky="w", padx=(0, 6))
            search_entry = core.ttk.Entry(filters, textvariable=search_var)
            search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
            core.ttk.Label(filters, text="Тип").grid(row=0, column=2, sticky="w", padx=(0, 6))
            type_box = core.ttk.Combobox(filters, textvariable=type_var, state="readonly", width=27)
            type_box.grid(row=0, column=3, sticky="ew", padx=(0, 10))
            core.ttk.Label(filters, text="Стан").grid(row=0, column=4, sticky="w", padx=(0, 6))
            state_values = ["Усі стани"] + [docreg.STATE_LABELS[key] for key in (
                docreg.STATE_VALID, docreg.STATE_EXPIRING, docreg.STATE_EXPIRED,
                docreg.STATE_NO_EXPIRY, docreg.STATE_DATE_REVIEW, docreg.STATE_ARCHIVED,
            )]
            state_box = core.ttk.Combobox(filters, textvariable=state_var, values=state_values, state="readonly", width=27)
            state_box.grid(row=0, column=5, sticky="ew", padx=(0, 10))
            core.ttk.Label(filters, text="Джерело").grid(row=0, column=6, sticky="w", padx=(0, 6))
            source_box = core.ttk.Combobox(
                filters, textvariable=source_var,
                values=[docreg.SOURCE_LABELS[key] for key in (docreg.SOURCE_ALL, docreg.SOURCE_MANUAL, docreg.SOURCE_REGISTRY)],
                state="readonly", width=20,
            )
            source_box.grid(row=0, column=7, sticky="ew")
            core.ttk.Checkbutton(filters, text="Показати архівні", variable=archived_var).grid(
                row=1, column=0, columnspan=2, sticky="w", pady=(7, 0)
            )

            summary_var = core.tk.StringVar(value="")
            core.ttk.Label(filters, textvariable=summary_var, style="Muted.TLabel").grid(
                row=1, column=2, columnspan=6, sticky="e", pady=(7, 0)
            )

            table = core.ttk.Frame(body)
            table.pack(fill="both", expand=True)
            table.rowconfigure(0, weight=1)
            table.columnconfigure(0, weight=1)
            cols = ("employee", "type", "series", "number", "issue", "expiry", "issuer", "source", "state")
            tree = core.ttk.Treeview(table, columns=cols, show="headings", selectmode="browse")
            for key, label, width in (
                ("employee", "Працівник", 240), ("type", "Тип документа", 215),
                ("series", "Серія", 75), ("number", "Номер", 125),
                ("issue", "Виданий", 95), ("expiry", "Чинний до", 105),
                ("issuer", "Ким виданий", 180), ("source", "Джерело", 190),
                ("state", "Стан", 190),
            ):
                tree.heading(key, text=label)
                tree.column(key, width=width, anchor="w")
            sy = core.ttk.Scrollbar(table, orient="vertical", command=tree.yview)
            sx = core.ttk.Scrollbar(table, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
            tree.grid(row=0, column=0, sticky="nsew")
            sy.grid(row=0, column=1, sticky="ns")
            sx.grid(row=1, column=0, sticky="ew")

            tree.tag_configure(docreg.STATE_VALID, foreground="#0B5D1E")
            tree.tag_configure(docreg.STATE_EXPIRING, foreground="#7A5B00")
            tree.tag_configure(docreg.STATE_EXPIRED, foreground="#8A1C1C")
            tree.tag_configure(docreg.STATE_NO_EXPIRY, foreground="#365A7A")
            tree.tag_configure(docreg.STATE_DATE_REVIEW, foreground="#8A5A00")
            tree.tag_configure(docreg.STATE_ARCHIVED, foreground="#777777")

            cache = {}
            label_to_state = {label: key for key, label in docreg.STATE_LABELS.items()}
            label_to_source = {label: key for key, label in docreg.SOURCE_LABELS.items()}

            def load_types():
                con = core.db()
                try:
                    values = docreg.distinct_document_types(con)
                finally:
                    con.close()
                type_box.configure(values=["Усі типи"] + values)
                if type_var.get() not in ["Усі типи"] + values:
                    type_var.set("Усі типи")

            def refresh():
                for iid in tree.get_children(""):
                    tree.delete(iid)
                cache.clear()
                state_key = label_to_state.get(state_var.get(), "")
                source_key = label_to_source.get(source_var.get(), docreg.SOURCE_ALL)
                doc_type = "" if type_var.get() == "Усі типи" else type_var.get()
                con = core.db()
                try:
                    rows = docreg.list_documents(
                        con, query=search_var.get(), doc_type=doc_type, state=state_key,
                        source=source_key, include_archived=archived_var.get(),
                    )
                finally:
                    con.close()
                for row in rows:
                    cache[int(row["id"])] = row
                    tree.insert(
                        "", "end", iid=str(row["id"]),
                        values=(
                            row["employee_name"], row["doc_type"], row["series"] or "",
                            row["number"] or "", personnel.display_date(row["issue_date"]),
                            personnel.display_date(row["expiry_date"]), row["issuer"] or "",
                            row["source_display"], row["state_label"],
                        ), tags=(row["state"],),
                    )
                counts = docreg.summary(rows)
                summary_var.set(
                    "Показано: %d  ·  прострочено: %d  ·  ≤30 днів: %d  ·  без строку: %d" % (
                        counts["total"], counts[docreg.STATE_EXPIRED], counts[docreg.STATE_EXPIRING],
                        counts[docreg.STATE_NO_EXPIRY],
                    )
                )

            def selected():
                if not tree.selection():
                    return None
                try:
                    return cache.get(int(tree.selection()[0]))
                except Exception:
                    return None

            def require_selected():
                row = selected()
                if row is None:
                    core.messagebox.showinfo("Реєстр документів", "Виберіть документ.", parent=win)
                return row

            def edit_document():
                row = require_selected()
                if row is None:
                    return
                _document_editor(self, core, int(row["employee_id"]), row, lambda: (load_types(), refresh()))

            def open_file():
                row = require_selected()
                if row is None:
                    return
                raw = str(row.get("file_path") or "").strip()
                if not raw:
                    core.messagebox.showinfo("Реєстр документів", "Для вибраного документа файл не вказано.", parent=win)
                    return
                try:
                    target = core.real_data_path(raw)
                except Exception:
                    target = Path(raw)
                if not Path(target).exists():
                    core.messagebox.showerror("Реєстр документів", "Файл не знайдено:\n" + str(target), parent=win)
                    return
                core.open_external(target)

            def archive_document():
                row = require_selected()
                if row is None:
                    return
                if row["state"] == docreg.STATE_ARCHIVED:
                    core.messagebox.showinfo("Реєстр документів", "Документ уже в архіві.", parent=win)
                    return
                if not core.messagebox.askyesno(
                    "Архівувати документ?",
                    "Документ залишиться в історії та в реєстрі при ввімкненому фільтрі архівних.",
                    parent=win,
                ):
                    return
                con = core.db()
                try:
                    personnel.archive_employee_document(con, int(row["employee_id"]), int(row["id"]))
                    con.commit()
                finally:
                    con.close()
                refresh()

            def open_employee_card():
                row = require_selected()
                if row is None:
                    return
                overview = getattr(self, "personnel_overview_tree", None)
                iid = str(row["employee_id"])
                if not _alive(overview) or iid not in overview.get_children(""):
                    core.messagebox.showinfo(
                        "Працівники",
                        "Працівник не показаний у поточному списку працівників. Змініть фільтр списку і відкрийте картку повторно.",
                        parent=win,
                    )
                    return
                overview.selection_set(iid)
                overview.focus(iid)
                overview.see(iid)
                self.open_personnel_data_center()

            actions = core.ttk.Frame(body)
            actions.pack(fill="x", pady=(8, 0))
            core.ttk.Button(actions, text="Оновити", command=lambda: (load_types(), refresh())).pack(side="left")
            core.ttk.Button(actions, text="Редагувати документ", style="Accent.TButton", command=edit_document).pack(side="left", padx=(6, 0))
            core.ttk.Button(actions, text="Відкрити файл", command=open_file).pack(side="left", padx=(6, 0))
            core.ttk.Button(actions, text="Картка працівника", command=open_employee_card).pack(side="left", padx=(6, 0))
            core.ttk.Button(actions, text="В архів", command=archive_document).pack(side="left", padx=(6, 0))
            core.ttk.Button(actions, text="Закрити", command=win.destroy).pack(side="right")

            def filter_changed(_event=None):
                refresh()

            search_entry.bind("<Return>", filter_changed)
            type_box.bind("<<ComboboxSelected>>", filter_changed)
            state_box.bind("<<ComboboxSelected>>", filter_changed)
            source_box.bind("<<ComboboxSelected>>", filter_changed)
            archived_var.trace_add("write", lambda *_args: refresh())
            tree.bind("<Double-1>", lambda _event: edit_document())

            load_types()
            refresh()
            win.transient(self)

    Taxo1053App.__name__ = "App"
    Taxo1053App.__qualname__ = "App"
    core.App = Taxo1053App
    core._TAXO_1053_INSTALLED = True
    return Taxo1053App
