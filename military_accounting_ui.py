# -*- coding: utf-8 -*-
"""Taxo 10.4-r9 — UI for statutory military-accounting actions.

The dashboard deliberately distinguishes internal quarterly registry imports from
formal military-accounting reconciliation under Cabinet Resolution No. 1487.
"""
from __future__ import annotations

from datetime import date
from tkinter import simpledialog

import military_accounting_2026 as military
import personnel_registry as registry

APP_VERSION = "10.4-r9"


def _configure_window(core, win, title, width=1100, height=700):
    win.title(title)
    try:
        core.fit_window_to_screen(win, width, height, min(width, 820), min(height, 540))
    except Exception:
        win.geometry("%dx%d" % (width, height))
        win.minsize(min(width, 820), min(height, 540))
    try:
        core.configure_toplevel(win, title=title, minsize=(min(width, 820), min(height, 540)))
    except Exception:
        pass


def _name(row):
    return " ".join(
        x for x in (
            (row["last_name"] or "") if "last_name" in row.keys() else "",
            (row["first_name"] or "") if "first_name" in row.keys() else "",
            (row["middle_name"] or "") if "middle_name" in row.keys() else "",
        ) if x
    ) or "—"


def install(core, base_app):
    if getattr(core, "_TAXO_1049_MILITARY_UI_INSTALLED", False):
        return core.App

    class MilitaryAccounting2026App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            military.ensure_schema(core)
            con = core.db()
            try:
                military.sync_recent_employment_actions(con)
                con.commit()
            finally:
                con.close()

        def open_military_accounting_overview(self):
            win = core.tk.Toplevel(self)
            _configure_window(core, win, "Військовий облік 2026 — контроль і журнал", 1120, 700)
            body = core.ttk.Frame(win, padding=14)
            body.pack(fill="both", expand=True)

            core.ttk.Label(body, text="Військовий облік 2026", style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text=(military.LEGAL_BASIS + ". Реєстровий XLSX і офіційне звіряння — різні процеси. "
                      "Квартальний імпорт є політикою Taxo та не підтверджує виконання офіційного звіряння."),
                wraplength=1060, justify="left",
            ).pack(anchor="w", pady=(4,12))

            con = core.db()
            try:
                registry.ensure_schema_on_connection(con)
                military.ensure_schema_on_connection(con)
                quarter = registry.registry_quarter_status(con, today=date.today())
                annual = military.annual_reconciliation_status(con, today=date.today())
                open_actions = military.list_actions(con, status=military.STATUS_OPEN)
            finally:
                con.close()

            registry_box = core.ttk.LabelFrame(body, text="1. Державний XLSX — внутрішня політика Taxo", padding=12)
            registry_box.pack(fill="x", pady=(0,10))
            registry_text = "Актуально" if quarter["current"] else "Потрібне свіже звіряння"
            core.ttk.Label(
                registry_box,
                text=("Квартал: %s · %s%s" % (
                    quarter["quarter"], registry_text,
                    (" · останній імпорт: " + quarter["last_date"]) if quarter["last_date"] else "",
                )),
                style="Subtitle.TLabel",
            ).pack(anchor="w")
            core.ttk.Label(
                registry_box,
                text="Цей статус означає лише актуальність завантаженого витягу в Taxo.",
                style="Muted.TLabel",
            ).pack(anchor="w", pady=(3,0))

            official_box = core.ttk.LabelFrame(body, text="2. Офіційне військове звіряння — Порядок №1487", padding=12)
            official_box.pack(fill="x", pady=(0,10))
            doc_state = "запис є" if annual["has_document_reconciliation"] else "немає запису за поточний рік"
            authority_state = "запис є" if annual["has_authority_reconciliation"] else "немає запису за поточний рік"
            core.ttk.Label(
                official_box,
                text=("%s: з документами працівників — %s; з ТЦК/реєстром/уповноваженим органом — %s."
                      % (annual["year"], doc_state, authority_state)),
                style="Subtitle.TLabel", wraplength=1020, justify="left",
            ).pack(anchor="w")
            core.ttk.Label(
                official_box,
                text=("Відсутність запису означає «потрібно перевірити журнал/внести виконане», а не автоматичний висновок про порушення. "
                      "Офіційні звіряння проводяться за графіком або погодженими строками та не рідше одного разу на рік."),
                wraplength=1020, justify="left",
            ).pack(anchor="w", pady=(4,0))

            action_box = core.ttk.LabelFrame(body, text="3. Поточні дії", padding=12)
            action_box.pack(fill="both", expand=True)
            core.ttk.Label(
                action_box,
                text="Відкритих дій: %d. Старі кадрові події до 27.09.2026 автоматично не створюються як прострочені." % len(open_actions),
                style="Subtitle.TLabel",
            ).pack(anchor="w")
            core.ttk.Label(
                action_box,
                text=("Опорні строки поточної редакції: повідомлення про прийняття/звільнення — 7 днів; "
                      "зміни до списків після подання документів — 5 днів; електронний військово-обліковий документ при прийнятті — не старше 72 годин."),
                wraplength=1020, justify="left",
            ).pack(anchor="w", pady=(4,10))

            buttons = core.ttk.Frame(action_box)
            buttons.pack(fill="x")
            core.ttk.Button(buttons, text="Дії та строки", command=self.open_military_actions_journal).pack(side="left", padx=(0,8))
            core.ttk.Button(buttons, text="Журнал офіційних звірянь", command=self.open_official_reconciliation_log).pack(side="left", padx=4)
            core.ttk.Button(
                buttons,
                text="Повнота карток працівників",
                command=lambda: super(MilitaryAccounting2026App, self).open_military_accounting_overview(),
            ).pack(side="left", padx=4)
            core.ttk.Button(buttons, text="Закрити", command=win.destroy).pack(side="right")
            win.transient(self)

        def open_military_actions_journal(self):
            win = core.tk.Toplevel(self)
            _configure_window(core, win, "Військовий облік — дії та строки", 1120, 680)
            body = core.ttk.Frame(win, padding=12)
            body.pack(fill="both", expand=True)
            core.ttk.Label(body, text="Дії та строки військового обліку", style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text="Автоматично створюються лише нові кадрові події від 27.09.2026. Історичні події не позначаються простроченими без підтвердження.",
                wraplength=1060, justify="left",
            ).pack(anchor="w", pady=(3,8))

            frame = core.ttk.Frame(body)
            frame.pack(fill="both", expand=True)
            frame.rowconfigure(0, weight=1); frame.columnconfigure(0, weight=1)
            cols = ("status", "due", "employee", "action", "event", "channel", "reference")
            tree = core.ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
            for key, label, width in (
                ("status", "Стан", 90), ("due", "Строк", 95), ("employee", "Працівник", 220),
                ("action", "Дія", 260), ("event", "Подія", 95), ("channel", "Канал", 120), ("reference", "Реквізит", 150),
            ):
                tree.heading(key, text=label); tree.column(key, width=width, anchor="w")
            y = core.ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=y.set)
            tree.grid(row=0, column=0, sticky="nsew"); y.grid(row=0, column=1, sticky="ns")

            def refresh():
                for iid in tree.get_children(): tree.delete(iid)
                con = core.db()
                try:
                    rows = military.list_actions(con)
                finally:
                    con.close()
                today = date.today().isoformat()
                for row in rows:
                    state = {military.STATUS_OPEN:"Відкрита", military.STATUS_DONE:"Виконано", military.STATUS_CANCELLED:"Скасовано"}.get(row["status"], row["status"])
                    tag = "late" if row["status"] == military.STATUS_OPEN and row["due_date"] and row["due_date"] < today else row["status"]
                    tree.insert("", "end", iid=str(row["id"]), values=(
                        state, row["due_date"] or "—", _name(row), military.ACTION_LABELS.get(row["action_type"], row["action_type"]),
                        row["event_date"], row["channel"] or "—", row["reference"] or "—",
                    ), tags=(tag,))
                tree.tag_configure("late", foreground="#8A1C1C")
                tree.tag_configure(military.STATUS_DONE, foreground="#0B5D1E")
                tree.tag_configure(military.STATUS_CANCELLED, foreground="#666666")

            def complete_selected():
                sel = tree.selection()
                if not sel:
                    core.messagebox.showinfo("Військовий облік", "Виберіть дію.", parent=win); return
                con = core.db()
                try:
                    military.complete_action(con, int(sel[0])); con.commit()
                finally:
                    con.close()
                refresh()

            def set_order_date():
                sel = tree.selection()
                if not sel:
                    core.messagebox.showinfo("Військовий облік", "Виберіть повідомлення про прийняття/звільнення.", parent=win); return
                value = simpledialog.askstring(
                    "Дата наказу",
                    "Дата наказу (YYYY-MM-DD). Саме від цієї дати рахується 7-денний строк:",
                    initialvalue=date.today().isoformat(), parent=win,
                )
                if not value:
                    return
                con = core.db()
                try:
                    military.set_notice_order_date(con, int(sel[0]), value); con.commit()
                except Exception as exc:
                    con.rollback(); core.messagebox.showerror("Військовий облік", str(exc), parent=win); return
                finally:
                    con.close()
                refresh()

            def add_monthly():
                con = core.db()
                try:
                    military.add_monthly_change_report_action(con); con.commit()
                finally:
                    con.close()
                refresh()

            controls = core.ttk.Frame(body); controls.pack(fill="x", pady=(8,0))
            core.ttk.Button(controls, text="Позначити виконаною", command=complete_selected).pack(side="left", padx=(0,8))
            core.ttk.Button(controls, text="Вказати дату наказу", command=set_order_date).pack(side="left", padx=4)
            core.ttk.Button(controls, text="Додати щомісячне повідомлення", command=add_monthly).pack(side="left", padx=4)
            core.ttk.Button(controls, text="Закрити", command=win.destroy).pack(side="right")
            refresh(); win.transient(self)

        def open_official_reconciliation_log(self):
            win = core.tk.Toplevel(self)
            _configure_window(core, win, "Журнал офіційних звірянь №1487", 1120, 680)
            body = core.ttk.Frame(win, padding=12); body.pack(fill="both", expand=True)
            core.ttk.Label(body, text="Журнал офіційних звірянь", style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text="Цей журнал не заповнюється автоматично з квартального XLSX. Вноситься фактично проведене офіційне звіряння.",
                wraplength=1060, justify="left",
            ).pack(anchor="w", pady=(3,8))

            form = core.ttk.Frame(body); form.pack(fill="x", pady=(0,8))
            date_var = core.tk.StringVar(value=date.today().isoformat())
            kind_var = core.tk.StringVar(value=military.RECONCILIATION_DOCUMENTS)
            method_var = core.tk.StringVar(value="")
            authority_var = core.tk.StringVar(value="")
            ref_var = core.tk.StringVar(value="")
            core.ttk.Label(form, text="Дата (YYYY-MM-DD)").grid(row=0,column=0,sticky="w")
            core.ttk.Entry(form,textvariable=date_var,width=14).grid(row=1,column=0,sticky="w",padx=(0,8))
            core.ttk.Label(form, text="Вид").grid(row=0,column=1,sticky="w")
            core.ttk.Combobox(form,textvariable=kind_var,state="readonly",width=28,values=tuple(military.RECONCILIATION_LABELS.keys())).grid(row=1,column=1,sticky="w",padx=(0,8))
            core.ttk.Label(form, text="Спосіб").grid(row=0,column=2,sticky="w")
            core.ttk.Entry(form,textvariable=method_var,width=20).grid(row=1,column=2,sticky="ew",padx=(0,8))
            core.ttk.Label(form, text="Орган / ТЦК").grid(row=0,column=3,sticky="w")
            core.ttk.Entry(form,textvariable=authority_var,width=24).grid(row=1,column=3,sticky="ew",padx=(0,8))
            core.ttk.Label(form, text="Реквізит").grid(row=0,column=4,sticky="w")
            core.ttk.Entry(form,textvariable=ref_var,width=20).grid(row=1,column=4,sticky="ew")
            form.columnconfigure(2,weight=1); form.columnconfigure(3,weight=1); form.columnconfigure(4,weight=1)

            frame = core.ttk.Frame(body); frame.pack(fill="both", expand=True)
            frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
            cols=("date","kind","method","authority","reference")
            tree=core.ttk.Treeview(frame,columns=cols,show="headings")
            for key,label,width in (("date","Дата",95),("kind","Вид",300),("method","Спосіб",160),("authority","Орган",220),("reference","Реквізит",180)):
                tree.heading(key,text=label); tree.column(key,width=width,anchor="w")
            y=core.ttk.Scrollbar(frame,orient="vertical",command=tree.yview); tree.configure(yscrollcommand=y.set)
            tree.grid(row=0,column=0,sticky="nsew"); y.grid(row=0,column=1,sticky="ns")

            def refresh():
                for iid in tree.get_children(): tree.delete(iid)
                con=core.db()
                try: rows=military.reconciliation_history(con)
                finally: con.close()
                for row in rows:
                    tree.insert("","end",values=(row["reconciliation_date"],military.RECONCILIATION_LABELS.get(row["kind"],row["kind"]),row["method"] or "—",row["authority"] or "—",row["reference"] or "—"))

            def add_record():
                try:
                    con=core.db()
                    try:
                        military.record_official_reconciliation(con,date_var.get(),kind_var.get(),method_var.get(),authority_var.get(),reference=ref_var.get()); con.commit()
                    finally: con.close()
                except Exception as exc:
                    core.messagebox.showerror("Журнал звірянь",str(exc),parent=win); return
                refresh()

            controls=core.ttk.Frame(body); controls.pack(fill="x",pady=(8,0))
            core.ttk.Button(controls,text="Додати запис",command=add_record).pack(side="left")
            core.ttk.Button(controls,text="Закрити",command=win.destroy).pack(side="right")
            refresh(); win.transient(self)

    core._TAXO_1049_MILITARY_UI_INSTALLED = True
    core.App = MilitaryAccounting2026App
    return MilitaryAccounting2026App
