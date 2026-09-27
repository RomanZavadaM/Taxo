# -*- coding: utf-8 -*-
"""Taxo 10.4-r9 — employee registry reconciliation and military-accounting view."""
from __future__ import annotations

from datetime import date, datetime

import personnel_registry as registry
import personnel_reconciliation as reconcile
from v1048_features import _create_unmatched_employees

APP_VERSION = "10.4-r9"


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


def _text(value):
    return str(value or "").strip()


def _configure_window(core, win, title, width=1180, height=760):
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


def _employee_name(row_plan):
    return _text(row_plan.get("employee_name")) or _text((row_plan.get("item") or {}).get("full_name"))


def _field_label(scope, field_name):
    labels = registry.EMPLOYEE_FIELD_LABELS if scope == "employee" else registry.MILITARY_FIELD_LABELS
    return labels.get(field_name, field_name)


def install(core, base_app):
    if getattr(core, "_TAXO_1049_INSTALLED", False):
        return core.App
    core.APP_VERSION = APP_VERSION

    class Taxo1049App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            reconcile.ensure_schema(core)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)
            self._install_r9_actions()

        def _install_r9_actions(self):
            if getattr(self, "_r9_actions_installed", False):
                return
            root = getattr(self, "personnel_overview_page", None)
            anchor = _find_button(root, "Дні народження") or _find_button(root, "Новий працівник")
            if anchor is not None:
                parent = anchor.master
                core.ttk.Button(
                    parent,
                    text="Військовий облік 2026",
                    command=self.open_military_accounting_overview,
                ).pack(side="right", padx=(8,0))
                self._r9_actions_installed = True

        # ------------------------------------------------------------------
        # Registry preview / field-level reconciliation
        # ------------------------------------------------------------------
        def _show_registry_import_preview(self, preview):
            con = core.db()
            try:
                reconcile.sync_preview_state(con, preview)
                con.commit()
            finally:
                con.close()

            win = core.tk.Toplevel(self)
            _configure_window(core, win, "Звірка працівників з держреєстром — по полях", 1260, 780)
            body = core.ttk.Frame(win, padding=12)
            body.pack(fill="both", expand=True)

            parsed = preview["parsed"]
            plan = preview["plan"]
            core.ttk.Label(body, text="Державний реєстр працівників — покомпонентна звірка", style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text=("%s  ·  файл: %s  ·  квартальна звірка — політика Taxo, не назва законодавчого строку"
                      % (reconcile.LEGAL_BASIS, parsed.get("source_name", ""))),
                style="Muted.TLabel", wraplength=1200, justify="left",
            ).pack(anchor="w", pady=(3,6))
            core.ttk.Label(
                body,
                text=("Порожнє поле у витягу не очищає Taxo і не є автоматичним порушенням. "
                      "Синім показано, що можна доповнити; жовтим — розбіжність; червоним — критичний ідентифікаційний конфлікт."),
                wraplength=1200, justify="left",
            ).pack(anchor="w", pady=(0,8))

            top = core.ttk.Frame(body)
            top.pack(fill="x", pady=(0,8))
            filter_var = core.tk.StringVar(value="Усе")
            core.ttk.Label(top, text="Фільтр полів:").pack(side="left")
            filter_box = core.ttk.Combobox(
                top, textvariable=filter_var, state="readonly", width=24,
                values=("Усе", "Відповідає", "Можна доповнити", "Розбіжність", "Критичний конфлікт", "Немає у витягу", "Активні рішення"),
            )
            filter_box.pack(side="left", padx=(4,12))

            create_var = core.tk.BooleanVar(value=True)
            core.ttk.Checkbutton(
                top,
                text="Дозволити створити відсутні картки з реєстру",
                variable=create_var,
            ).pack(side="left", padx=8)

            split = core.ttk.Panedwindow(body, orient="horizontal")
            split.pack(fill="both", expand=True)
            left = core.ttk.Frame(split, padding=(0,0,6,0))
            right = core.ttk.Frame(split, padding=(6,0,0,0))
            split.add(left, weight=1)
            split.add(right, weight=2)

            # Employees / registry rows.
            left.rowconfigure(0, weight=1); left.columnconfigure(0, weight=1)
            emp_cols = ("status", "employee", "match")
            emp_tree = core.ttk.Treeview(left, columns=emp_cols, show="headings", selectmode="browse")
            for key,label,width in (
                ("status","Стан",135),("employee","Працівник",260),("match","Зіставлення",100),
            ):
                emp_tree.heading(key,text=label); emp_tree.column(key,width=width,anchor="w")
            emp_y = core.ttk.Scrollbar(left, orient="vertical", command=emp_tree.yview)
            emp_tree.configure(yscrollcommand=emp_y.set)
            emp_tree.grid(row=0,column=0,sticky="nsew"); emp_y.grid(row=0,column=1,sticky="ns")

            row_map = {}
            for idx,row_plan in enumerate(plan):
                status = row_plan.get("status", "")
                label = {
                    "no_changes":"Відповідає", "update":"Є зміни", "unmatched":"Нова картка",
                    "ambiguous":"Неоднозначно", "conflict":"Конфлікт",
                }.get(status,status)
                iid = "p%d" % idx
                row_map[iid] = row_plan
                emp_tree.insert("","end",iid=iid,values=(label,_employee_name(row_plan),row_plan.get("match_quality", "")),tags=(status,))
            for idx,row in enumerate(preview.get("local_only") or []):
                iid = "l%d" % idx
                row_map[iid] = None
                emp_tree.insert("","end",iid=iid,values=("Є лише в Taxo",row["employee_name"],"—"),tags=("local_only",))
            emp_tree.tag_configure("no_changes", foreground="#0B5D1E")
            emp_tree.tag_configure("update", foreground="#7A5B00")
            emp_tree.tag_configure("unmatched", foreground="#005B96")
            emp_tree.tag_configure("ambiguous", foreground="#8A1C1C")
            emp_tree.tag_configure("conflict", foreground="#8A1C1C")
            emp_tree.tag_configure("local_only", foreground="#666666")

            # Field details.
            right.rowconfigure(1, weight=1); right.columnconfigure(0, weight=1)
            detail_var = core.tk.StringVar(value="Виберіть працівника")
            core.ttk.Label(right,textvariable=detail_var,style="Subtitle.TLabel").grid(row=0,column=0,sticky="w",pady=(0,5))
            field_frame = core.ttk.Frame(right)
            field_frame.grid(row=1,column=0,sticky="nsew")
            field_frame.rowconfigure(0,weight=1); field_frame.columnconfigure(0,weight=1)
            cols = ("state","field","taxo","registry","decision")
            field_tree = core.ttk.Treeview(field_frame,columns=cols,show="headings",selectmode="browse")
            for key,label,width in (
                ("state","Стан",135),("field","Поле",220),("taxo","Taxo",230),
                ("registry","Держреєстр",230),("decision","Рішення",190),
            ):
                field_tree.heading(key,text=label); field_tree.column(key,width=width,anchor="w",stretch=key in ("taxo","registry"))
            fy=core.ttk.Scrollbar(field_frame,orient="vertical",command=field_tree.yview)
            fx=core.ttk.Scrollbar(field_frame,orient="horizontal",command=field_tree.xview)
            field_tree.configure(yscrollcommand=fy.set,xscrollcommand=fx.set)
            field_tree.grid(row=0,column=0,sticky="nsew"); fy.grid(row=0,column=1,sticky="ns"); fx.grid(row=1,column=0,sticky="ew")
            field_tree.tag_configure(reconcile.STATE_MATCH, foreground="#0B5D1E")
            field_tree.tag_configure(reconcile.STATE_FILL, foreground="#005B96")
            field_tree.tag_configure(reconcile.STATE_DIFFERENCE, foreground="#7A5B00")
            field_tree.tag_configure(reconcile.STATE_CRITICAL, foreground="#8A1C1C")
            field_tree.tag_configure(reconcile.STATE_UNAVAILABLE, foreground="#666666")

            field_map = {}
            selected_employee = {"id": None, "row_plan": None}

            def states_for_filter():
                return {
                    "Відповідає": [reconcile.STATE_MATCH],
                    "Можна доповнити": [reconcile.STATE_FILL],
                    "Розбіжність": [reconcile.STATE_DIFFERENCE],
                    "Критичний конфлікт": [reconcile.STATE_CRITICAL],
                    "Немає у витягу": [reconcile.STATE_UNAVAILABLE],
                }.get(filter_var.get())

            def refresh_fields(*_):
                for iid in field_tree.get_children(): field_tree.delete(iid)
                field_map.clear()
                employee_id = selected_employee["id"]
                if employee_id is None:
                    return
                con = core.db()
                try:
                    rows = reconcile.current_fields(
                        con, employee_id=employee_id,
                        states=states_for_filter(),
                        active_decisions_only=(filter_var.get()=="Активні рішення"),
                    )
                finally:
                    con.close()
                for n,row in enumerate(rows):
                    iid="f%d" % n
                    field_map[iid]=(row["scope"],row["field_name"])
                    decision = reconcile.DECISION_LABELS.get(_text(row["decision"]), _text(row["decision"])) or "—"
                    field_tree.insert("","end",iid=iid,values=(
                        reconcile.STATE_LABELS.get(row["state"],row["state"]),
                        _field_label(row["scope"],row["field_name"]),
                        row["local_value"] or "—", row["registry_value"] or "—", decision,
                    ),tags=(row["state"],))

            def choose_employee(_event=None):
                sel=emp_tree.selection()
                if not sel: return
                row_plan=row_map.get(sel[0])
                if not row_plan or row_plan.get("employee_id") is None:
                    selected_employee.update(id=None,row_plan=row_plan)
                    detail_var.set(_employee_name(row_plan or {}) if row_plan else "Запис є лише в Taxo")
                    refresh_fields(); return
                selected_employee.update(id=int(row_plan["employee_id"]),row_plan=row_plan)
                detail_var.set(_employee_name(row_plan))
                refresh_fields()

            emp_tree.bind("<<TreeviewSelect>>",choose_employee)
            filter_box.bind("<<ComboboxSelected>>",refresh_fields)

            actions = core.ttk.Frame(body)
            actions.pack(fill="x", pady=(10,0))

            def selected_field():
                sel=field_tree.selection()
                if not sel or sel[0] not in field_map:
                    core.messagebox.showinfo("Звірка", "Виберіть поле у правій таблиці.", parent=win); return None
                scope,field_name=field_map[sel[0]]
                return selected_employee["id"],scope,field_name

            def decide(decision):
                picked=selected_field()
                if not picked: return
                employee_id,scope,field_name=picked
                con=core.db()
                try:
                    if decision==reconcile.DECISION_ACCEPT_REGISTRY:
                        reconcile.accept_registry_value(con,employee_id,scope,field_name)
                    else:
                        reconcile.set_decision(con,employee_id,scope,field_name,decision)
                    con.commit()
                except Exception as exc:
                    con.rollback(); core.messagebox.showerror("Звірка",str(exc),parent=win); return
                finally:
                    con.close()
                refresh_fields()
                try: self.refresh_personnel_registry()
                except Exception: pass

            def fill_empty_all():
                if not core.messagebox.askyesno(
                    "Доповнити з реєстру",
                    "Заповнити тільки порожні поля Taxo непорожніми значеннями цього витягу?\n\nНаявні значення не буде замінено.",
                    parent=win,
                ): return
                try:
                    result=registry.apply_registry_import(core,preview,mode=registry.IMPORT_FILL_EMPTY)
                    created=0
                    if create_var.get():
                        created=_create_unmatched_employees(core,preview)
                    con=core.db()
                    try:
                        reconcile.sync_preview_state(con,preview); con.commit()
                    finally: con.close()
                    core.messagebox.showinfo(
                        "Звірка", "Доповнено карток: %d. Створено нових: %d." % (result.get("updated",0),created), parent=win
                    )
                    refresh_fields()
                    try: self.refresh_personnel_registry()
                    except Exception: pass
                except Exception as exc:
                    core.messagebox.showerror("Звірка",str(exc),parent=win)

            core.ttk.Button(actions,text="Доповнити порожні",command=fill_empty_all).pack(side="left",padx=(0,8))
            core.ttk.Button(actions,text="Прийняти реєстр для поля",command=lambda:decide(reconcile.DECISION_ACCEPT_REGISTRY)).pack(side="left",padx=4)
            core.ttk.Button(actions,text="Залишити Taxo",command=lambda:decide(reconcile.DECISION_KEEP_TAXO)).pack(side="left",padx=4)
            core.ttk.Button(actions,text="Виправити в реєстрі",command=lambda:decide(reconcile.DECISION_FIX_REGISTRY)).pack(side="left",padx=4)
            core.ttk.Button(actions,text="Відкласти",command=lambda:decide(reconcile.DECISION_DEFER)).pack(side="left",padx=4)
            core.ttk.Button(actions,text="Закрити",command=win.destroy).pack(side="right")

            if emp_tree.get_children():
                first=emp_tree.get_children()[0]; emp_tree.selection_set(first); emp_tree.focus(first); choose_employee()
            win.transient(self)

        # ------------------------------------------------------------------
        # Military-accounting overview — completeness is informational.
        # ------------------------------------------------------------------
        def open_military_accounting_overview(self):
            win=core.tk.Toplevel(self)
            _configure_window(core,win,"Військовий облік працівників — 2026",1120,700)
            body=core.ttk.Frame(win,padding=12); body.pack(fill="both",expand=True)
            core.ttk.Label(body,text="Військовий облік працівників",style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text=(reconcile.LEGAL_BASIS + ". Порожнє поле тут означає «потрібно уточнити / джерело не надало», "
                      "а не автоматично «порушення». Квартальне нагадування про свіжий витяг — внутрішня політика Taxo."),
                wraplength=1060,justify="left",
            ).pack(anchor="w",pady=(3,8))

            con=core.db()
            try:
                registry.ensure_schema_on_connection(con); reconcile.ensure_schema_on_connection(con)
                quarter=registry.registry_quarter_status(con,today=date.today())
                employees=con.execute(
                    "SELECT * FROM employees WHERE COALESCE(active,1)=1 ORDER BY last_name,first_name,middle_name,id"
                ).fetchall()
            finally: con.close()
            core.ttk.Label(
                body,
                text="Реєстрова звірка: %s · %s%s" % (
                    quarter["label"], quarter["quarter"],
                    (" · остання: "+quarter["last_date"]) if quarter["last_date"] else "",
                ),
                style="Subtitle.TLabel",
            ).pack(anchor="w",pady=(0,8))

            frame=core.ttk.Frame(body); frame.pack(fill="both",expand=True)
            frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
            cols=("employee","rnokpp","account","booking","missing","mismatch","active")
            tree=core.ttk.Treeview(frame,columns=cols,show="headings",selectmode="browse")
            for key,label,width in (
                ("employee","Працівник",260),("rnokpp","РНОКПП",110),("account","Статус обліку",160),
                ("booking","Бронювання",150),("missing","Уточнити полів",105),("mismatch","Розбіжностей",110),("active","Активних рішень",120),
            ):
                tree.heading(key,text=label); tree.column(key,width=width,anchor="w")
            y=core.ttk.Scrollbar(frame,orient="vertical",command=tree.yview)
            tree.configure(yscrollcommand=y.set); tree.grid(row=0,column=0,sticky="nsew"); y.grid(row=0,column=1,sticky="ns")

            con=core.db()
            try:
                for employee in employees:
                    military=con.execute("SELECT * FROM employee_military_profile WHERE employee_id=?",(employee["id"],)).fetchone()
                    missing=registry.missing_appendix5_fields(employee,military)
                    summary=reconcile.employee_summary(con,employee["id"])
                    counts=summary["counts"]
                    mismatches=counts.get(reconcile.STATE_DIFFERENCE,0)+counts.get(reconcile.STATE_CRITICAL,0)
                    name=" ".join(x for x in (employee["last_name"],employee["first_name"],employee["middle_name"]) if x)
                    tree.insert("","end",iid=str(employee["id"]),values=(
                        name, employee["rnokpp"] or "—",
                        military["account_status"] if military is not None and military["account_status"] else "—",
                        military["booking_status"] if military is not None and military["booking_status"] else "—",
                        len(missing),mismatches,summary["active_decisions"],
                    ),tags=("attention" if mismatches or summary["active_decisions"] else "normal",))
            finally: con.close()
            tree.tag_configure("attention",foreground="#7A5B00")

            foot=core.ttk.Frame(body); foot.pack(fill="x",pady=(8,0))
            core.ttk.Label(
                foot,text="«Уточнити полів» — інформаційний індикатор повноти, а не автоматичний висновок про порушення.",
                style="Muted.TLabel",
            ).pack(side="left")
            core.ttk.Button(foot,text="Закрити",command=win.destroy).pack(side="right")
            win.transient(self)

    core._TAXO_1049_INSTALLED = True
    core.App = Taxo1049App
    return Taxo1049App
