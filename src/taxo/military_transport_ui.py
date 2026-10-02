# -*- coding: utf-8 -*-
"""Tk UI for Taxo military-transport vehicle accounting (10.4-r10)."""
from __future__ import annotations

from datetime import date, datetime

import military_transport_2026 as mt


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


def _configure_window(core, win, title, width=1220, height=760):
    win.title(title)
    try:
        core.fit_window_to_screen(win, width, height, min(width, 860), min(height, 560))
    except Exception:
        win.geometry("%dx%d" % (width, height))
        win.minsize(min(width, 860), min(height, 560))
    try:
        core.configure_toplevel(win, title=title, minsize=(min(width, 860), min(height, 560)))
    except Exception:
        pass


def _fmt_day(value):
    text = str(value or "").strip()
    if not text:
        return ""
    try:
        return datetime.strptime(text[:10], "%Y-%m-%d").strftime("%d.%m.%Y")
    except ValueError:
        return text


def _parse_day(value):
    text = str(value or "").strip()
    if not text:
        return ""
    for pattern in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            pass
    raise ValueError("Дата має бути у форматі ДД.ММ.РРРР.")


def _selected_tree_id(tree):
    sel = tree.selection() if tree is not None else ()
    if not sel:
        return None
    return sel[0]


def _dialog(core, parent, title, fields, save_label="Зберегти"):
    """Small reusable modal field editor.

    fields: list of dicts: key, label, value, values(optional), width(optional).
    Returns dict or None.
    """
    result = {"value": None}
    win = core.tk.Toplevel(parent)
    _configure_window(core, win, title, 720, min(680, 180 + len(fields) * 48))
    body = core.ttk.Frame(win, padding=14)
    body.pack(fill="both", expand=True)
    body.columnconfigure(1, weight=1)
    variables = {}
    for row, spec in enumerate(fields):
        core.ttk.Label(body, text=spec["label"]).grid(row=row, column=0, sticky="w", padx=(0,8), pady=5)
        var = core.tk.StringVar(value=str(spec.get("value", "") or ""))
        variables[spec["key"]] = var
        if spec.get("values"):
            widget = core.ttk.Combobox(
                body, textvariable=var, state="readonly", values=spec["values"],
                width=spec.get("width", 48),
            )
        else:
            widget = core.ttk.Entry(body, textvariable=var, width=spec.get("width", 52))
        widget.grid(row=row, column=1, sticky="ew", pady=5)
    buttons = core.ttk.Frame(body)
    buttons.grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=(14,0))

    def save():
        result["value"] = {key: var.get().strip() for key, var in variables.items()}
        win.destroy()

    core.ttk.Button(buttons, text="Скасувати", command=win.destroy).pack(side="right")
    core.ttk.Button(buttons, text=save_label, style="Accent.TButton", command=save).pack(side="right", padx=(0,8))
    win.transient(parent)
    try:
        win.grab_set()
    except Exception:
        pass
    win.wait_window()
    return result["value"]


def install(core, base_app):
    if getattr(core, "_TAXO_10410_MILITARY_TRANSPORT_UI_INSTALLED", False):
        return core.App

    class MilitaryTransportApp(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            mt.ensure_schema(core)
            con = core.db()
            try:
                mt.ensure_next_reporting_action(con, today=date.today())
                con.commit()
            finally:
                con.close()
            self._install_military_transport_action()

        def _install_military_transport_action(self):
            if getattr(self, "_military_transport_action_installed", False):
                return
            root = getattr(self, "tab_vehicles", None)
            anchor = _find_button(root, "Дані «Шлях»") or _find_button(root, "Контроль документів")
            if anchor is None:
                return
            parent = anchor.master
            self._military_transport_button = core.ttk.Button(
                parent,
                text="Військово-транспортний облік",
                command=self.open_military_transport_dashboard,
            )
            self._military_transport_button.pack(side="left", padx=4)
            self._military_transport_action_installed = True

        def open_military_transport_dashboard(self):
            existing = getattr(self, "_military_transport_window", None)
            if _alive(existing):
                existing.lift()
                existing.focus_force()
                return

            win = core.tk.Toplevel(self)
            self._military_transport_window = win
            _configure_window(core, win, "Військово-транспортний облік ТЗ", 1280, 800)
            body = core.ttk.Frame(win, padding=12)
            body.pack(fill="both", expand=True)
            core.ttk.Label(body, text="Військово-транспортний облік ТЗ", style="Title.TLabel").pack(anchor="w")
            core.ttk.Label(
                body,
                text=(mt.LEGAL_BASIS + ". Окремий контур: не замінює «Шлях» і контроль страхування/реєстрації/діагностики. "
                      "Статус «не визначено» означає потребу уточнення, а не автоматичне порушення."),
                wraplength=1220, justify="left",
            ).pack(anchor="w", pady=(3,8))

            summary_var = core.tk.StringVar(value="")
            core.ttk.Label(body, textvariable=summary_var, style="Muted.TLabel").pack(anchor="w", pady=(0,8))

            upper = core.ttk.Panedwindow(body, orient="horizontal")
            upper.pack(fill="both", expand=True)
            left = core.ttk.Frame(upper, padding=(0,0,6,0))
            right = core.ttk.Frame(upper, padding=(6,0,0,0))
            upper.add(left, weight=3); upper.add(right, weight=2)
            left.rowconfigure(0, weight=1); left.columnconfigure(0, weight=1)

            vehicle_cols = ("plate", "name", "status", "readiness", "basis", "next")
            vehicle_tree = core.ttk.Treeview(left, columns=vehicle_cols, show="headings", selectmode="browse")
            for key,label,width in (
                ("plate","Держ. номер",110),("name","ТЗ",210),("status","Військовий статус",220),
                ("readiness","Готовність",140),("basis","Підстава",150),("next","Наступна дія",120),
            ):
                vehicle_tree.heading(key,text=label); vehicle_tree.column(key,width=width,anchor="w")
            vy = core.ttk.Scrollbar(left, orient="vertical", command=vehicle_tree.yview)
            vx = core.ttk.Scrollbar(left, orient="horizontal", command=vehicle_tree.xview)
            vehicle_tree.configure(yscrollcommand=vy.set, xscrollcommand=vx.set)
            vehicle_tree.grid(row=0,column=0,sticky="nsew"); vy.grid(row=0,column=1,sticky="ns"); vx.grid(row=1,column=0,sticky="ew")
            vehicle_tree.tag_configure("clarify", foreground="#7A5B00")
            vehicle_tree.tag_configure("transferred", foreground="#8A1C1C")
            vehicle_tree.tag_configure("normal", foreground="#0B5D1E")

            selected = {"vehicle_id": None}
            detail_var = core.tk.StringVar(value="Виберіть транспортний засіб")
            core.ttk.Label(right, textvariable=detail_var, style="Subtitle.TLabel", wraplength=440, justify="left").pack(anchor="w")
            profile_text = core.tk.Text(right, height=13, wrap="word")
            profile_text.pack(fill="both", expand=True, pady=(6,8))
            profile_text.configure(state="disabled")
            profile_buttons = core.ttk.Frame(right); profile_buttons.pack(fill="x")

            notebook = core.ttk.Notebook(body)
            notebook.pack(fill="both", expand=True, pady=(10,0))
            order_tab = core.ttk.Frame(notebook, padding=8)
            action_tab = core.ttk.Frame(notebook, padding=8)
            report_tab = core.ttk.Frame(notebook, padding=8)
            worker_tab = core.ttk.Frame(notebook, padding=8)
            notebook.add(order_tab, text="Наряди")
            notebook.add(action_tab, text="Події / 7 днів")
            notebook.add(report_tab, text="Відомості 20.06 / 20.12")
            notebook.add(worker_tab, text="Працівники ТЗ")

            # Orders
            order_tab.rowconfigure(0,weight=1); order_tab.columnconfigure(0,weight=1)
            order_tree = core.ttk.Treeview(order_tab, columns=("kind","no","date","due","status","point"), show="headings", height=7)
            for key,label,width in (
                ("kind","Наряд",150),("no","№",100),("date","Дата",100),("due","Передати до",110),
                ("status","Стан",150),("point","Пункт передачі",280),
            ):
                order_tree.heading(key,text=label); order_tree.column(key,width=width,anchor="w")
            oy=core.ttk.Scrollbar(order_tab,orient="vertical",command=order_tree.yview); order_tree.configure(yscrollcommand=oy.set)
            order_tree.grid(row=0,column=0,sticky="nsew"); oy.grid(row=0,column=1,sticky="ns")
            order_buttons=core.ttk.Frame(order_tab); order_buttons.grid(row=1,column=0,columnspan=2,sticky="ew",pady=(8,0))

            # Actions
            action_tab.rowconfigure(0,weight=1); action_tab.columnconfigure(0,weight=1)
            action_tree = core.ttk.Treeview(action_tab, columns=("vehicle","action","event","due","status","ref"), show="headings", height=7)
            for key,label,width in (
                ("vehicle","ТЗ",170),("action","Дія",280),("event","Подія",105),("due","Строк",105),
                ("status","Стан",90),("ref","Вихідний / примітка",220),
            ):
                action_tree.heading(key,text=label); action_tree.column(key,width=width,anchor="w")
            ay=core.ttk.Scrollbar(action_tab,orient="vertical",command=action_tree.yview); action_tree.configure(yscrollcommand=ay.set)
            action_tree.grid(row=0,column=0,sticky="nsew"); ay.grid(row=0,column=1,sticky="ns")
            action_buttons=core.ttk.Frame(action_tab); action_buttons.grid(row=1,column=0,columnspan=2,sticky="ew",pady=(8,0))

            # Reports
            report_info = core.tk.StringVar(value="")
            core.ttk.Label(report_tab,textvariable=report_info,wraplength=1080,justify="left").pack(anchor="w",pady=(0,8))
            report_frame=core.ttk.Frame(report_tab); report_frame.pack(fill="both",expand=True)
            report_frame.rowconfigure(0,weight=1); report_frame.columnconfigure(0,weight=1)
            report_tree=core.ttk.Treeview(report_frame,columns=("date","submitted","authority","reference"),show="headings",height=6)
            for key,label,width in (("date","Контрольна дата",140),("submitted","Подано",170),("authority","Куди",280),("reference","Реквізит",220)):
                report_tree.heading(key,text=label); report_tree.column(key,width=width,anchor="w")
            ry=core.ttk.Scrollbar(report_frame,orient="vertical",command=report_tree.yview); report_tree.configure(yscrollcommand=ry.set)
            report_tree.grid(row=0,column=0,sticky="nsew"); ry.grid(row=0,column=1,sticky="ns")
            report_buttons=core.ttk.Frame(report_tab); report_buttons.pack(fill="x",pady=(8,0))

            # Workers
            worker_tab.rowconfigure(0,weight=1); worker_tab.columnconfigure(0,weight=1)
            worker_tree=core.ttk.Treeview(worker_tab,columns=("name","from","until","note"),show="headings",height=6)
            for key,label,width in (("name","Працівник",320),("from","Від",110),("until","До",110),("note","Зв'язок / примітка",360)):
                worker_tree.heading(key,text=label); worker_tree.column(key,width=width,anchor="w")
            wy=core.ttk.Scrollbar(worker_tab,orient="vertical",command=worker_tree.yview); worker_tree.configure(yscrollcommand=wy.set)
            worker_tree.grid(row=0,column=0,sticky="nsew"); wy.grid(row=0,column=1,sticky="ns")
            worker_buttons=core.ttk.Frame(worker_tab); worker_buttons.grid(row=1,column=0,columnspan=2,sticky="ew",pady=(8,0))
            core.ttk.Label(worker_buttons,text="Зв'язок задається явно; Taxo не вгадує його зі старих шляхових листів.",style="Muted.TLabel").pack(side="left")

            maps = {"vehicles":{}, "orders":{}, "actions":{}}

            def current_vehicle_id(require=True):
                vid=selected["vehicle_id"]
                if vid is None and require:
                    core.messagebox.showinfo("Військово-транспортний облік","Виберіть транспортний засіб.",parent=win)
                return vid

            def refresh_profile():
                vid=current_vehicle_id(False)
                profile_text.configure(state="normal"); profile_text.delete("1.0","end")
                if vid is None:
                    detail_var.set("Виберіть транспортний засіб")
                    profile_text.insert("end","Статус військово-транспортного обліку не визначає operational active/inactive картки ТЗ.")
                    profile_text.configure(state="disabled"); return
                con=core.db()
                try:
                    row=mt.get_profile(con,vid); state=mt.profile_state(con,vid)
                    history=mt.profile_history(con,vid)
                finally: con.close()
                vehicle=maps["vehicles"].get(str(vid),{})
                detail_var.set("%s · %s" % (vehicle.get("plate") or "без номера", vehicle.get("name") or "ТЗ"))
                values=[
                    ("Статус",state["label"]),
                    ("Готовність",mt.READINESS_LABELS.get((row["readiness_status"] if row else mt.READINESS_UNKNOWN),"Не визначено")),
                    ("Орган обліку",(row["accounting_authority"] if row else "") or "—"),
                    ("Внутрішній №",(row["local_reference"] if row else "") or "—"),
                    ("Підстава",("%s %s" % ((row["basis_type"] if row else "") or "",(row["basis_document_no"] if row else "") or "")).strip() or "—"),
                    ("Дата підстави",_fmt_day(row["basis_document_date"] if row else "") or "—"),
                    ("Підстава винятку",(row["exemption_basis"] if row else "") or "—"),
                    ("Історія змін",str(len(history))),
                ]
                for label,value in values: profile_text.insert("end","%s: %s\n"%(label,value))
                if state["needs_clarification"]:
                    profile_text.insert("end","\nІнформаційно: первинної підстави ще немає. Це не позначається як порушення.")
                profile_text.configure(state="disabled")

            def refresh_orders():
                for iid in order_tree.get_children(): order_tree.delete(iid)
                maps["orders"].clear(); vid=current_vehicle_id(False)
                if vid is None: return
                con=core.db()
                try: rows=mt.list_orders(con,vid)
                finally: con.close()
                for row in rows:
                    iid=str(row["id"]); maps["orders"][iid]=row
                    order_tree.insert("","end",iid=iid,values=(
                        mt.ORDER_LABELS.get(row["order_kind"],row["order_kind"]),row["document_no"] or "—",
                        _fmt_day(row["document_date"]),_fmt_day(row["transfer_due_date"]) or "—",
                        mt.ORDER_STATUS_LABELS.get(row["status"],row["status"]),row["transfer_point"] or "—",
                    ))

            def refresh_actions():
                for iid in action_tree.get_children(): action_tree.delete(iid)
                maps["actions"].clear()
                con=core.db()
                try: rows=mt.list_actions(con)
                finally: con.close()
                for row in rows:
                    iid=str(row["id"]); maps["actions"][iid]=row
                    vehicle=(row["vehicle_plate"] or row["vehicle_name"] or "Усі ТЗ")
                    action_tree.insert("","end",iid=iid,values=(
                        vehicle,mt.ACTION_LABELS.get(row["action_type"],row["action_type"]),
                        _fmt_day(row["event_date"]),_fmt_day(row["due_date"]),
                        {mt.ACTION_OPEN:"Відкрита",mt.ACTION_DONE:"Виконано",mt.ACTION_CANCELLED:"Скасовано"}.get(row["status"],row["status"]),
                        row["reference"] or row["note"] or "—",
                    ),tags=(row["status"],))
                action_tree.tag_configure(mt.ACTION_OPEN,foreground="#7A5B00")
                action_tree.tag_configure(mt.ACTION_DONE,foreground="#0B5D1E")

            def refresh_reports():
                deadline=mt.next_reporting_deadline(date.today())
                report_info.set(
                    "Наступна контрольна дата: %s. Taxo не backfill-ить минулі строки до запуску r10; факт подання фіксується вручну."
                    % deadline.strftime("%d.%m.%Y")
                )
                for iid in report_tree.get_children(): report_tree.delete(iid)
                con=core.db()
                try: rows=mt.list_submissions(con)
                finally: con.close()
                for row in rows:
                    report_tree.insert("","end",values=(
                        _fmt_day(row["report_date"]),str(row["submitted_at"] or "").replace("T"," "),
                        row["authority"] or "—",row["reference"] or "—",
                    ))

            def refresh_workers():
                for iid in worker_tree.get_children(): worker_tree.delete(iid)
                vid=current_vehicle_id(False)
                if vid is None: return
                con=core.db()
                try: rows=mt.workers_for_vehicle(con,vid,date.today())
                finally: con.close()
                for row in rows:
                    name=row["worker_name"] or " ".join(filter(None,[row["last_name"],row["first_name"],row["middle_name"]]))
                    worker_tree.insert("","end",values=(name or "—",_fmt_day(row["valid_from"]) or "—",_fmt_day(row["valid_until"]) or "—",row["relation_note"] or "—"))

            def refresh_vehicles(select_id=None):
                for iid in vehicle_tree.get_children(): vehicle_tree.delete(iid)
                maps["vehicles"].clear()
                con=core.db()
                try:
                    mt.ensure_next_reporting_action(con,date.today()); con.commit()
                    rows=mt.overview_rows(con,date.today())
                    open_actions=len(mt.list_actions(con,mt.ACTION_OPEN))
                finally: con.close()
                clarify=sum(1 for r in rows if r["needs_clarification"])
                summary_var.set("ТЗ: %d · потребує уточнення підстави: %d · відкритих дій: %d · контрольні дати: 20 червня / 20 грудня"%(len(rows),clarify,open_actions))
                for row in rows:
                    iid=str(row["vehicle_id"]); maps["vehicles"][iid]=row
                    readiness=mt.READINESS_LABELS.get(row["readiness_status"],row["readiness_status"])
                    basis=(row["basis_document_no"] or "—")
                    next_due=_fmt_day(row["next_due_date"]) or "—"
                    tag="clarify" if row["needs_clarification"] else ("transferred" if row["status"]==mt.STATUS_TRANSFERRED else "normal")
                    vehicle_tree.insert("","end",iid=iid,values=(row["plate"] or "—",row["name"],row["status_label"],readiness,basis,next_due),tags=(tag,))
                target=str(select_id or selected["vehicle_id"] or "")
                if target and target in vehicle_tree.get_children():
                    vehicle_tree.selection_set(target); vehicle_tree.see(target)
                refresh_profile(); refresh_orders(); refresh_actions(); refresh_reports(); refresh_workers()

            def choose_vehicle(_event=None):
                iid=_selected_tree_id(vehicle_tree)
                selected["vehicle_id"]=int(iid) if iid else None
                refresh_profile(); refresh_orders(); refresh_workers()

            vehicle_tree.bind("<<TreeviewSelect>>",choose_vehicle)

            def edit_profile():
                vid=current_vehicle_id()
                if vid is None: return
                con=core.db()
                try: row=mt.get_profile(con,vid)
                finally: con.close()
                status_rev={v:k for k,v in mt.STATUS_LABELS.items()}; ready_rev={v:k for k,v in mt.READINESS_LABELS.items()}
                data=_dialog(core,win,"Профіль військово-транспортного обліку",[
                    {"key":"status","label":"Статус","value":mt.STATUS_LABELS.get(row["status"] if row else mt.STATUS_UNKNOWN,mt.STATUS_LABELS[mt.STATUS_UNKNOWN]),"values":tuple(mt.STATUS_LABELS.values())},
                    {"key":"readiness","label":"Готовність","value":mt.READINESS_LABELS.get(row["readiness_status"] if row else mt.READINESS_UNKNOWN,mt.READINESS_LABELS[mt.READINESS_UNKNOWN]),"values":tuple(mt.READINESS_LABELS.values())},
                    {"key":"authority","label":"Орган обліку / ТЦК","value":row["accounting_authority"] if row else ""},
                    {"key":"reference","label":"Внутрішній № / посилання","value":row["local_reference"] if row else ""},
                    {"key":"basis_type","label":"Вид підстави","value":row["basis_type"] if row else ""},
                    {"key":"basis_no","label":"№ документа-підстави","value":row["basis_document_no"] if row else ""},
                    {"key":"basis_date","label":"Дата підстави, ДД.ММ.РРРР","value":_fmt_day(row["basis_document_date"] if row else "")},
                    {"key":"exemption","label":"Підстава винятку (якщо є)","value":row["exemption_basis"] if row else ""},
                    {"key":"note","label":"Примітка","value":row["note"] if row else ""},
                ])
                if not data: return
                try:
                    con=core.db()
                    mt.set_profile(con,vid,status=status_rev[data["status"]],readiness_status=ready_rev[data["readiness"]],
                                   accounting_authority=data["authority"],local_reference=data["reference"],basis_type=data["basis_type"],
                                   basis_document_no=data["basis_no"],basis_document_date=_parse_day(data["basis_date"]) if data["basis_date"] else "",
                                   exemption_basis=data["exemption"],note=data["note"],source="ui")
                    con.commit(); con.close()
                except Exception as exc:
                    try: con.close()
                    except Exception: pass
                    core.messagebox.showerror("Профіль ТЗ",str(exc),parent=win); return
                refresh_vehicles(vid)

            core.ttk.Button(profile_buttons,text="Редагувати профіль",style="Accent.TButton",command=edit_profile).pack(side="left")
            core.ttk.Button(profile_buttons,text="Оновити",command=lambda:refresh_vehicles(selected["vehicle_id"])).pack(side="left",padx=6)

            def add_order():
                vid=current_vehicle_id()
                if vid is None:return
                kind_rev={v:k for k,v in mt.ORDER_LABELS.items()}
                data=_dialog(core,win,"Новий наряд",[
                    {"key":"kind","label":"Вид","value":mt.ORDER_LABELS[mt.ORDER_CONSOLIDATED],"values":tuple(mt.ORDER_LABELS.values())},
                    {"key":"no","label":"№ документа","value":""},
                    {"key":"date","label":"Дата документа","value":date.today().strftime("%d.%m.%Y")},
                    {"key":"authority","label":"Орган / підстава","value":""},
                    {"key":"point","label":"Пункт передачі","value":""},
                    {"key":"due","label":"Передати до, ДД.ММ.РРРР","value":""},
                    {"key":"note","label":"Примітка","value":""},
                ],"Додати")
                if not data:return
                try:
                    con=core.db(); mt.record_order(con,vid,kind_rev[data["kind"]],_parse_day(data["date"]),document_no=data["no"],authority=data["authority"],transfer_point=data["point"],transfer_due_date=_parse_day(data["due"]) if data["due"] else "",note=data["note"]); con.commit(); con.close()
                except Exception as exc:
                    try: con.close()
                    except Exception: pass
                    core.messagebox.showerror("Наряд",str(exc),parent=win);return
                refresh_orders(); refresh_vehicles(vid)

            def change_order(status):
                iid=_selected_tree_id(order_tree)
                if not iid:
                    core.messagebox.showinfo("Наряд","Виберіть наряд.",parent=win);return
                label=mt.ORDER_STATUS_LABELS[status]
                if not core.messagebox.askyesno("Наряд","Зафіксувати стан «%s»?"%label,parent=win):return
                ref=""
                if status==mt.ORDER_RETURNED:
                    ref=core.simpledialog.askstring("Повернення","Реквізит акта/документа повернення (необов'язково):",parent=win) or ""
                con=core.db()
                try: mt.set_order_status(con,int(iid),status,return_reference=ref); con.commit()
                except Exception as exc:
                    con.rollback(); core.messagebox.showerror("Наряд",str(exc),parent=win)
                finally: con.close()
                refresh_orders(); refresh_vehicles(selected["vehicle_id"])

            core.ttk.Button(order_buttons,text="Додати наряд",style="Accent.TButton",command=add_order).pack(side="left")
            core.ttk.Button(order_buttons,text="Підготовка",command=lambda:change_order(mt.ORDER_PREPARING)).pack(side="left",padx=5)
            core.ttk.Button(order_buttons,text="Передано",command=lambda:change_order(mt.ORDER_TRANSFERRED)).pack(side="left",padx=5)
            core.ttk.Button(order_buttons,text="Повернуто",command=lambda:change_order(mt.ORDER_RETURNED)).pack(side="left",padx=5)
            core.ttk.Button(order_buttons,text="Скасовано",command=lambda:change_order(mt.ORDER_CANCELLED)).pack(side="left",padx=5)

            def add_notice_event():
                vid=current_vehicle_id()
                if vid is None:return
                rev={v:k for k,v in mt.EVENT_LABELS.items()}
                data=_dialog(core,win,"Подія для 7-денного повідомлення",[
                    {"key":"event","label":"Подія","value":next(iter(mt.EVENT_LABELS.values())),"values":tuple(mt.EVENT_LABELS.values())},
                    {"key":"date","label":"Дата події","value":date.today().strftime("%d.%m.%Y")},
                    {"key":"details","label":"Підстава / деталі","value":""},
                ],"Зафіксувати")
                if not data:return
                try:
                    con=core.db(); _event_id,due=mt.record_notice_event(con,vid,rev[data["event"]],_parse_day(data["date"]),data["details"]); con.commit(); con.close()
                    core.messagebox.showinfo("Строк","Створено дію зі строком до %s."%due.strftime("%d.%m.%Y"),parent=win)
                except Exception as exc:
                    try: con.close()
                    except Exception: pass
                    core.messagebox.showerror("Подія",str(exc),parent=win);return
                refresh_actions(); refresh_vehicles(vid)

            def complete_selected_action():
                iid=_selected_tree_id(action_tree)
                if not iid:
                    core.messagebox.showinfo("Дія","Виберіть дію.",parent=win);return
                row=maps["actions"].get(iid)
                if row and row["status"]!=mt.ACTION_OPEN:
                    core.messagebox.showinfo("Дія","Ця дія вже не відкрита.",parent=win);return
                ref=core.simpledialog.askstring("Виконано","Вихідний № / реквізит підтвердження (необов'язково):",parent=win) or ""
                con=core.db()
                try: mt.complete_action(con,int(iid),reference=ref); con.commit()
                finally: con.close()
                refresh_actions(); refresh_vehicles(selected["vehicle_id"])

            core.ttk.Button(action_buttons,text="Зафіксувати подію (7 днів)",style="Accent.TButton",command=add_notice_event).pack(side="left")
            core.ttk.Button(action_buttons,text="Позначити виконаною",command=complete_selected_action).pack(side="left",padx=6)

            def record_report():
                deadline=mt.next_reporting_deadline(date.today())
                data=_dialog(core,win,"Фіксація подання відомості",[
                    {"key":"date","label":"Контрольна дата","value":deadline.strftime("%d.%m.%Y")},
                    {"key":"authority","label":"Куди подано","value":""},
                    {"key":"reference","label":"Вихідний № / квитанція","value":""},
                    {"key":"note","label":"Примітка","value":""},
                ],"Зафіксувати подання")
                if not data:return
                try:
                    con=core.db(); mt.record_submission(con,_parse_day(data["date"]),authority=data["authority"],reference=data["reference"],note=data["note"]); con.commit(); con.close()
                except Exception as exc:
                    try: con.close()
                    except Exception: pass
                    core.messagebox.showerror("Відомість",str(exc),parent=win);return
                refresh_reports(); refresh_actions(); refresh_vehicles(selected["vehicle_id"])

            core.ttk.Button(report_buttons,text="Зафіксувати подання",style="Accent.TButton",command=record_report).pack(side="left")

            def add_worker():
                vid=current_vehicle_id()
                if vid is None:return
                con=core.db()
                try:
                    rows=con.execute("SELECT id,last_name,first_name,middle_name FROM employees WHERE active=1 ORDER BY last_name,first_name,middle_name").fetchall()
                finally: con.close()
                names=[]; ids={}
                for row in rows:
                    name=" ".join(filter(None,[row["last_name"],row["first_name"],row["middle_name"]]))
                    label="%s [#%s]"%(name,row["id"]); names.append(label); ids[label]=row["id"]
                data=_dialog(core,win,"Працівник, пов'язаний з ТЗ",[
                    {"key":"employee","label":"Працівник","value":names[0] if names else "","values":tuple(names) if names else None},
                    {"key":"name","label":"Або ПІБ вручну","value":""},
                    {"key":"from","label":"Від, ДД.ММ.РРРР","value":""},
                    {"key":"until","label":"До, ДД.ММ.РРРР","value":""},
                    {"key":"note","label":"Характер зв'язку / примітка","value":""},
                ],"Додати")
                if not data:return
                try:
                    con=core.db(); mt.add_worker_link(con,vid,employee_id=ids.get(data["employee"]),worker_name=data["name"],relation_note=data["note"],valid_from=_parse_day(data["from"]) if data["from"] else "",valid_until=_parse_day(data["until"]) if data["until"] else ""); con.commit(); con.close()
                except Exception as exc:
                    try: con.close()
                    except Exception: pass
                    core.messagebox.showerror("Працівник ТЗ",str(exc),parent=win);return
                refresh_workers()

            core.ttk.Button(worker_buttons,text="Додати явний зв'язок",command=add_worker).pack(side="right")

            refresh_vehicles()
            win.transient(self)

    core._TAXO_10410_MILITARY_TRANSPORT_UI_INSTALLED = True
    core.App = MilitaryTransportApp
    return MilitaryTransportApp
