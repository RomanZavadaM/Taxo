# -*- coding: utf-8 -*-
"""Taxo 10.7-r4 — UI розділу «Експлуатація»."""
from __future__ import annotations

from datetime import date

import operations_orders as ops
from order_pdf_workflow import (save_and_preview_order, generate_order_formats, open_order_format)
from safety_instructions_ui import install_instruction_tab


def _alive(widget):
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def _employee_maps(con):
    rows = ops.list_employee_choices(con, active_only=False)
    by_label = {row["label"]: row["id"] for row in rows}
    by_id = {row["id"]: row["label"] for row in rows}
    return rows, by_label, by_id


def open_operations_center(app, core):
    existing = getattr(app, "_operations_center_window", None)
    if _alive(existing):
        existing.lift(); existing.focus_force(); return existing

    ops.ensure_schema(core)
    win = core.tk.Toplevel(app)
    app._operations_center_window = win
    try:
        core.fit_window_to_screen(win, 1260, 780, 940, 600)
        core.configure_toplevel(win, title="Експлуатація", minsize=(940, 600))
    except Exception:
        win.geometry("1260x780")
    win.title("Taxo / %s — Експлуатація" % app._company_name_value())

    body = core.ttk.Frame(win, padding=12); body.pack(fill="both", expand=True)
    core.ttk.Label(body, text="Експлуатація", style="HeroTitle.TLabel").pack(anchor="w")
    core.ttk.Label(
        body,
        text=("Робочий центр експлуатації: щоденні документи, технічна готовність, накази, "
              "закріплення ТЗ і відповідальні особи. Починайте з вкладки «Документи» — "
              "там зібрані найчастіші дії; реєстри нижче зберігають історію та деталі."),
        style="Muted.TLabel", wraplength=1180, justify="left",
    ).pack(anchor="w", pady=(2, 8))

    book = core.ttk.Notebook(body); book.pack(fill="both", expand=True)
    orders_tab = core.ttk.Frame(book); assignments_tab = core.ttk.Frame(book)
    entities_tab = core.ttk.Frame(book)
    settings_tab = core.ttk.Frame(book); maintenance_tab = core.ttk.Frame(book)
    book.add(orders_tab, text="Накази"); book.add(assignments_tab, text="Закріплення водіїв")
    book.add(entities_tab, text="Учасники / ТЗ")
    book.add(settings_tab, text="Відповідальні"); book.add(maintenance_tab, text="Каталог наказів")

    # Settings
    settings_box = core.ttk.Frame(settings_tab, padding=14); settings_box.pack(fill="both", expand=True); settings_box.columnconfigure(1, weight=1)
    con = core.db()
    try:
        cfg = ops.settings(con); employees, emp_by_label, emp_by_id = _employee_maps(con)
    finally:
        con.close()
    employee_labels = [row["label"] for row in employees]
    install_instruction_tab(app, core, book)
    operations_resp_var = core.tk.StringVar(value=emp_by_id.get(cfg["operations_responsible_employee_id"], "") if cfg else "")
    military_resp_var = core.tk.StringVar(value=emp_by_id.get(cfg["military_transport_responsible_employee_id"], "") if cfg else "")
    place_var = core.tk.StringVar(value=(cfg["order_place"] if cfg else "") or "")
    cfg_keys = set(cfg.keys()) if cfg is not None and hasattr(cfg, "keys") else set()
    work_order_next_var = core.tk.StringVar(
        value=str((cfg["work_order_next_no"] if "work_order_next_no" in cfg_keys else 1) or 1)
    )
    personnel_order_next_var = core.tk.StringVar(
        value=str((cfg["personnel_order_next_no"] if "personnel_order_next_no" in cfg_keys else 1) or 1)
    )
    for row, (label, var) in enumerate((("Відповідальний за експлуатацію", operations_resp_var),
                                        ("Відповідальний за військово-транспортний обов'язок", military_resp_var))):
        core.ttk.Label(settings_box, text=label).grid(row=row, column=0, sticky="w", padx=(0,10), pady=7)
        core.ttk.Combobox(settings_box, textvariable=var, values=employee_labels, state="readonly").grid(row=row, column=1, sticky="ew", pady=7)
    core.ttk.Label(settings_box, text="Місце складання наказів").grid(row=2,column=0,sticky="w",padx=(0,10),pady=7)
    core.ttk.Entry(settings_box, textvariable=place_var).grid(row=2,column=1,sticky="ew",pady=7)

    core.ttk.Separator(settings_box,orient="horizontal").grid(row=3,column=0,columnspan=2,sticky="ew",pady=(12,8))
    core.ttk.Label(settings_box, text="Нумерація наказів", style="Title.TLabel").grid(row=4,column=0,columnspan=2,sticky="w",pady=(0,4))
    core.ttk.Label(settings_box, text="Наступний № робочого / експлуатаційного наказу").grid(row=5,column=0,sticky="w",padx=(0,10),pady=7)
    work_order_next_entry=core.ttk.Entry(settings_box, textvariable=work_order_next_var, width=12)
    work_order_next_entry.grid(row=5,column=1,sticky="w",pady=7)
    core.ttk.Label(settings_box, text="Наступний № кадрового наказу").grid(row=6,column=0,sticky="w",padx=(0,10),pady=7)
    personnel_order_next_entry=core.ttk.Entry(settings_box, textvariable=personnel_order_next_var, width=12)
    personnel_order_next_entry.grid(row=6,column=1,sticky="w",pady=7)
    core.ttk.Label(
        settings_box,
        text=("Це початок / наступний номер для двох незалежних журналів. "
              "Робочі накази: 1, 2, 3…; кадрові: 1-К, 2-К, 3-К…. "
              "Якщо паперовий журнал уже ведеться, введіть тут номер, з якого Taxo має продовжити."),
        style="Muted.TLabel",wraplength=900,justify="left",
    ).grid(row=7,column=0,columnspan=2,sticky="w",pady=(4,8))
    core.ttk.Label(settings_box, text=("Відомість ТЦК перед друком затверджується відповідальним у Taxo. "
                                      "Службові позначки про джерело імпорту у затверджену форму не друкуються."),
                   style="Muted.TLabel", wraplength=900, justify="left").grid(row=8,column=0,columnspan=2,sticky="w",pady=(8,12))

    def save_settings():
        con2 = core.db()
        try:
            ops.save_settings(
                con2,
                operations_responsible_employee_id=emp_by_label.get(operations_resp_var.get()),
                military_transport_responsible_employee_id=emp_by_label.get(military_resp_var.get()),
                order_place=place_var.get(),
                work_order_next_no=work_order_next_var.get(),
                personnel_order_next_no=personnel_order_next_var.get(),
            ); con2.commit()
        except Exception as exc:
            con2.rollback(); core.messagebox.showerror("Експлуатація", str(exc), parent=win); return
        finally:
            con2.close()
        core.messagebox.showinfo("Експлуатація", "Налаштування експлуатації та нумерації наказів збережено.", parent=win)
    core.ttk.Button(settings_box,text="Зберегти",style="Accent.TButton",command=save_settings).grid(row=9,column=1,sticky="e")

    # Orders register
    order_top = core.ttk.Frame(orders_tab,padding=(10,10,10,4)); order_top.pack(fill="x")
    order_filter_bar = core.ttk.Frame(order_top)
    order_filter_bar.pack(fill="x")
    order_action_bar = core.ttk.Frame(order_top)
    order_action_bar.pack(fill="x", pady=(6, 0))
    order_hint = core.ttk.Label(
        orders_tab,
        text=("Робочий порядок: виберіть, що потрібно оформити → створіть чернетку → "
              "перевірте реквізити → за потреби додайте ТЗ/водія → введіть наказ у дію в Taxo → "
              "після фактичного підписання позначте паперовий оригінал."),
        style="Muted.TLabel", wraplength=1100, justify="left",
    )
    order_hint.pack(anchor="w", padx=12, pady=(0,4))
    order_frame = core.ttk.Frame(orders_tab); order_frame.pack(fill="both",expand=True,padx=10,pady=(0,10)); order_frame.rowconfigure(0,weight=1); order_frame.columnconfigure(0,weight=1)
    cols=("date","no","series","group","type","subject","status","paper","control")
    order_tree=core.ttk.Treeview(order_frame,columns=cols,show="headings",selectmode="browse")
    for key,label,width in (("date","Дата",100),("no","№",75),("series","Серія",150),("group","Група",220),("type","Тип наказу",250),("subject","Тема",340),
                            ("status","Стан",110),("paper","Паперовий оригінал",140),("control","Контроль",210)):
        order_tree.heading(key,text=label); order_tree.column(key,width=width,anchor="w")
    sy=core.ttk.Scrollbar(order_frame,orient="vertical",command=order_tree.yview); sx=core.ttk.Scrollbar(order_frame,orient="horizontal",command=order_tree.xview)
    order_tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set); order_tree.grid(row=0,column=0,sticky="nsew"); sy.grid(row=0,column=1,sticky="ns"); sx.grid(row=1,column=0,sticky="ew")
    order_cache={}
    group_filter_var=core.tk.StringVar(value="Усі групи")
    group_filter_labels=["Усі групи"]+list(ops.ORDER_GROUP_LABELS.values())
    group_filter_by_label={label:key for key,label in ops.ORDER_GROUP_LABELS.items()}
    core.ttk.Label(order_filter_bar,text="Група:").pack(side="right",padx=(8,4))
    group_filter_box=core.ttk.Combobox(order_filter_bar,textvariable=group_filter_var,values=group_filter_labels,state="readonly",width=31)
    group_filter_box.pack(side="right")

    def refresh_orders(select_id=None):
        for iid in order_tree.get_children(): order_tree.delete(iid)
        order_cache.clear(); con2=core.db()
        try: rows=ops.list_orders(con2)
        finally: con2.close()
        selected_group=group_filter_by_label.get(group_filter_var.get())
        if selected_group:
            rows=[row for row in rows if ops.ORDER_TYPE_GROUP.get(str(row["order_type"]),ops.ORDER_GROUP_OTHER)==selected_group]
        for row in rows:
            oid=int(row["id"]); order_cache[oid]=row
            control=" ".join(str(row[k] or "").strip() for k in ("last_name","first_name","middle_name") if str(row[k] or "").strip())
            paper="підписано" if int(row["paper_original_signed"] or 0) else "—"
            order_type=str(row["order_type"])
            group_key=ops.ORDER_TYPE_GROUP.get(order_type,ops.ORDER_GROUP_OTHER)
            series_key=str(row["order_series"] or ops.ORDER_SERIES_WORK) if "order_series" in row.keys() else ops.ORDER_SERIES_WORK
            order_tree.insert("","end",iid=str(oid),values=(ops.display_day(row["order_date"]),row["order_no"],
                ops.ORDER_SERIES_LABELS.get(series_key,series_key),
                ops.ORDER_GROUP_LABELS.get(group_key,group_key),ops.ORDER_TYPE_LABELS.get(order_type,order_type),row["subject"],
                ("Діє в Taxo" if row["status"]==ops.ORDER_APPROVED else ops.ORDER_STATUS_LABELS.get(row["status"],row["status"])),
                paper,control or "—"),tags=(row["status"],))
        order_tree.tag_configure(ops.ORDER_APPROVED,foreground="#0B5D1E"); order_tree.tag_configure(ops.ORDER_CANCELLED,foreground="#777777")
        if rows: order_hint.pack_forget()
        elif not order_hint.winfo_manager(): order_hint.pack(anchor="w",padx=12,pady=(0,4),before=order_frame)
        if select_id and str(select_id) in order_tree.get_children():
            order_tree.selection_set(str(select_id)); order_tree.focus(str(select_id)); order_tree.see(str(select_id))
        refresh_assignments()
        refresh_order_entities()

    group_filter_box.bind("<<ComboboxSelected>>",lambda _e:refresh_orders())

    def selected_order(quiet=False):
        sel=order_tree.selection()
        if not sel:
            if not quiet: core.messagebox.showinfo("Накази","Виберіть наказ.",parent=win)
            return None
        return order_cache.get(int(sel[0]))

    type_labels=list(ops.ORDER_TYPE_LABELS.values()); type_by_label={label:key for key,label in ops.ORDER_TYPE_LABELS.items()}

    def order_dialog(existing=None, force_type=None):
        dialog=core.tk.Toplevel(win); dialog.title("Редагувати наказ" if existing else "Створити наказ")
        try: core.configure_toplevel(dialog,title=dialog.title(),minsize=(760,540))
        except Exception: pass
        frm=core.ttk.Frame(dialog,padding=14); frm.pack(fill="both",expand=True); frm.columnconfigure(1,weight=1); frm.rowconfigure(8,weight=1)
        initial_type=force_type or (existing["order_type"] if existing else ops.TYPE_VEHICLE_ASSIGNMENT)
        type_var=core.tk.StringVar(value=ops.ORDER_TYPE_LABELS.get(initial_type,ops.ORDER_TYPE_LABELS[ops.TYPE_GENERIC]))
        initial_series=(str(existing["order_series"] or ops.ORDER_SERIES_WORK) if existing and "order_series" in existing.keys() else ops.ORDER_SERIES_WORK)
        series_var=core.tk.StringVar(value=ops.ORDER_SERIES_LABELS.get(initial_series,ops.ORDER_SERIES_LABELS[ops.ORDER_SERIES_WORK]))
        if existing:
            initial_number=str(existing["order_no"])
        else:
            try:
                counter = personnel_order_next_var.get() if initial_series==ops.ORDER_SERIES_PERSONNEL else work_order_next_var.get()
                initial_number=ops.format_order_number(initial_series,int(counter))
            except Exception:
                initial_number=""
        no_var=core.tk.StringVar(value=initial_number)
        date_var=core.tk.StringVar(value=ops.display_day(existing["order_date"]) if existing else date.today().strftime("%d.%m.%Y"))
        place_local=core.tk.StringVar(value=str(existing["place"] if existing else place_var.get()))
        subject_var=core.tk.StringVar(value=str(existing["subject"] if existing else ops.DEFAULT_SUBJECTS.get(initial_type,"")))
        control_var=core.tk.StringVar(value=emp_by_id.get(existing["control_employee_id"],"") if existing else operations_resp_var.get())
        core.ttk.Label(frm,text="Тип наказу").grid(row=0,column=0,sticky="w",pady=5)
        type_box=core.ttk.Combobox(frm,textvariable=type_var,values=type_labels,state="disabled" if force_type else "readonly"); type_box.grid(row=0,column=1,sticky="ew",pady=5)
        core.ttk.Label(frm,text="Серія нумерації").grid(row=1,column=0,sticky="w",padx=(0,8),pady=5)
        series_box=core.ttk.Combobox(
            frm,textvariable=series_var,values=list(ops.ORDER_SERIES_LABELS.values()),
            state="disabled" if existing else "readonly"
        ); series_box.grid(row=1,column=1,sticky="ew",pady=5)
        for rr,(label,var) in enumerate((("Номер",no_var),("Дата",date_var),("Місце",place_local),("Тема",subject_var),("Контроль",control_var)),start=2):
            core.ttk.Label(frm,text=label).grid(row=rr,column=0,sticky="nw",padx=(0,8),pady=5)
            widget=core.ttk.Combobox(frm,textvariable=var,values=employee_labels,state="readonly") if label=="Контроль" else core.ttk.Entry(frm,textvariable=var)
            widget.grid(row=rr,column=1,sticky="ew",pady=5)
        core.ttk.Label(frm,text="Підстава / вступ").grid(row=7,column=0,sticky="nw",pady=5)
        preamble=core.tk.Text(frm,height=4,wrap="word"); preamble.grid(row=7,column=1,sticky="nsew",pady=5)
        preamble.insert("1.0",str(existing["preamble"] if existing else ops.DEFAULT_PREAMBLES.get(initial_type,"")))
        core.ttk.Label(frm,text="Текст пунктів").grid(row=8,column=0,sticky="nw",pady=5)
        body_text=core.tk.Text(frm,height=7,wrap="word"); body_text.grid(row=8,column=1,sticky="nsew",pady=5)
        body_text.insert("1.0",str(existing["body_text"] if existing else ops.DEFAULT_BODY_TEMPLATES.get(initial_type,"")))

        initial_vehicles=[]
        initial_drivers=[]
        initial_vehicle_list=None
        initial_driver_list=None
        assignment_box=None
        assignment_count_var=core.tk.StringVar(value="")
        if existing is None:
            con_choices=core.db()
            try:
                initial_vehicles=ops.list_vehicle_choices(con_choices,active_only=True)
                initial_drivers=ops.list_driver_choices(con_choices,active_only=True)
            finally:
                con_choices.close()
            assignment_box=core.ttk.LabelFrame(frm,text="Закріплення в цьому наказі",padding=8)
            assignment_box.grid(row=9,column=0,columnspan=2,sticky="ew",pady=(8,2))
            assignment_box.columnconfigure(0,weight=1); assignment_box.columnconfigure(1,weight=1)

            left=core.ttk.Frame(assignment_box); left.grid(row=0,column=0,sticky="nsew",padx=(0,4))
            right=core.ttk.Frame(assignment_box); right.grid(row=0,column=1,sticky="nsew",padx=(4,0))
            core.ttk.Label(left,text="Транспортний засіб").pack(anchor="w")
            initial_vehicle_list=core.tk.Listbox(left,selectmode="extended",exportselection=False,height=6)
            initial_vehicle_list.pack(fill="both",expand=True,pady=(3,0))
            for row in initial_vehicles: initial_vehicle_list.insert("end",row["label"])
            core.ttk.Label(right,text="Водій із бази водіїв").pack(anchor="w")
            initial_driver_list=core.tk.Listbox(right,selectmode="extended",exportselection=False,height=6)
            initial_driver_list.pack(fill="both",expand=True,pady=(3,0))
            for row in initial_drivers: initial_driver_list.insert("end",row["label"])

            def update_assignment_count(_event=None):
                vc=len(initial_vehicle_list.curselection()) if initial_vehicle_list is not None else 0
                dc=len(initial_driver_list.curselection()) if initial_driver_list is not None else 0
                assignment_count_var.set("Вибрано: ТЗ — %d; водіїв — %d" % (vc,dc))
            initial_vehicle_list.bind("<<ListboxSelect>>",update_assignment_count)
            initial_driver_list.bind("<<ListboxSelect>>",update_assignment_count)
            update_assignment_count()
            core.ttk.Label(
                assignment_box,textvariable=assignment_count_var,style="Subtitle.TLabel"
            ).grid(row=1,column=0,columnspan=2,sticky="w",pady=(6,2))
            core.ttk.Label(
                assignment_box,
                text=("Правило пар: 1 ТЗ + кілька водіїв → усі водії до цього ТЗ; "
                      "однакова кількість ТЗ і водіїв → пари за порядком вибору. "
                      "Один водій не закріплюється одночасно за кількома ТЗ. "
                      "Якщо кількість різна з обох боків — Taxo попросить уточнити. Можна лишити обидва списки порожніми."),
                style="Muted.TLabel",wraplength=700,justify="left",
            ).grid(row=2,column=0,columnspan=2,sticky="w",pady=(2,0))

        def show_assignment_box(order_type):
            if assignment_box is None:
                return
            if order_type==ops.TYPE_VEHICLE_ASSIGNMENT:
                assignment_box.grid()
            else:
                assignment_box.grid_remove()

        show_assignment_box(initial_type)
        if existing and int(existing["paper_original_signed"] or 0):
            core.ttk.Label(frm,text="Увага: паперовий оригінал позначено як підписаний. Після змін звірте його і, за потреби, передрукуйте.",
                           style="Muted.TLabel",wraplength=620,justify="left").grid(row=9,column=0,columnspan=2,sticky="w",pady=(4,2))
        def sync_type(_event=None):
            if existing: return
            key=type_by_label.get(type_var.get(),ops.TYPE_GENERIC)
            subject_var.set(ops.DEFAULT_SUBJECTS.get(key,""))
            preamble.delete("1.0","end"); preamble.insert("1.0",ops.DEFAULT_PREAMBLES.get(key,""))
            body_text.delete("1.0","end"); body_text.insert("1.0",ops.DEFAULT_BODY_TEMPLATES.get(key,""))
            show_assignment_box(key)
        type_box.bind("<<ComboboxSelected>>",sync_type)
        def sync_series(_event=None):
            if existing:
                return
            series_key=next((key for key,label in ops.ORDER_SERIES_LABELS.items() if label==series_var.get()),ops.ORDER_SERIES_WORK)
            try:
                counter = personnel_order_next_var.get() if series_key==ops.ORDER_SERIES_PERSONNEL else work_order_next_var.get()
                no_var.set(ops.format_order_number(series_key,int(counter)))
            except Exception:
                no_var.set("")
        series_box.bind("<<ComboboxSelected>>",sync_series)
        def apply_template():
            key=force_type or type_by_label.get(type_var.get(),ops.TYPE_GENERIC)
            template=ops.DEFAULT_BODY_TEMPLATES.get(key,"")
            if not template:
                core.messagebox.showinfo("Типовий текст","Для цього типу наказу типовий текст не задано.",parent=dialog); return
            current=body_text.get("1.0","end-1c").strip()
            if current and current != template and not core.messagebox.askyesno("Замінити текст?","Поточний текст пунктів буде замінено типовою заготовкою. Продовжити?",parent=dialog): return
            body_text.delete("1.0","end"); body_text.insert("1.0",template)
        def save():
            order_type=force_type or type_by_label.get(type_var.get(),ops.TYPE_GENERIC)
            series_key=next((key for key,label in ops.ORDER_SERIES_LABELS.items() if label==series_var.get()),ops.ORDER_SERIES_WORK)
            initial_pairs=[]
            if existing is None and order_type==ops.TYPE_VEHICLE_ASSIGNMENT and assignment_box is not None:
                vehicle_ids=[initial_vehicles[int(index)]["id"] for index in initial_vehicle_list.curselection()]
                driver_ids=[initial_drivers[int(index)]["id"] for index in initial_driver_list.curselection()]
                try:
                    initial_pairs=ops.build_assignment_pairs(vehicle_ids,driver_ids)
                except Exception as exc:
                    core.messagebox.showerror("Наказ про закріплення",str(exc),parent=dialog)
                    return
            con3=core.db()
            try:
                if existing:
                    ops.update_order(con3,existing["id"],order_type=order_type,order_no=no_var.get(),order_date=date_var.get(),place=place_local.get(),
                                     subject=subject_var.get(),preamble=preamble.get("1.0","end-1c"),body_text=body_text.get("1.0","end-1c"),
                                     control_employee_id=emp_by_label.get(control_var.get()),history_note="Редагування через інтерфейс")
                    oid=int(existing["id"])
                elif order_type==ops.TYPE_VEHICLE_ASSIGNMENT:
                    oid=ops.create_vehicle_assignment_order(
                        con3,order_no=no_var.get(),order_date=date_var.get(),place=place_local.get(),
                        subject=subject_var.get(),preamble=preamble.get("1.0","end-1c"),
                        body_text=body_text.get("1.0","end-1c"),
                        control_employee_id=emp_by_label.get(control_var.get()),
                        initial_pairs=initial_pairs,order_series=series_key,
                    )
                else:
                    oid=ops.create_order(con3,order_type=order_type,order_no=no_var.get(),order_date=date_var.get(),place=place_local.get(),
                                         subject=subject_var.get(),preamble=preamble.get("1.0","end-1c"),body_text=body_text.get("1.0","end-1c"),
                                         control_employee_id=emp_by_label.get(control_var.get()),order_series=series_key)
                con3.commit()
            except Exception as exc:
                con3.rollback(); core.messagebox.showerror("Наказ",str(exc),parent=dialog); return
            finally: con3.close()
            dialog.destroy(); refresh_orders(oid)
            book.select(orders_tab)
            created_order=order_cache.get(int(oid))
            if created_order is not None:
                preview_order(created_order)
        bar=core.ttk.Frame(frm); bar.grid(row=10,column=0,columnspan=2,sticky="ew",pady=(10,0))
        core.ttk.Button(bar,text="Скасувати",command=dialog.destroy).pack(side="right")
        core.ttk.Button(bar,text="Типовий текст",command=apply_template).pack(side="left")
        core.ttk.Button(bar,text="Зберегти" if existing else "Створити",style="Accent.TButton",command=save).pack(side="right",padx=(0,6)); dialog.transient(win)

    def order_mutability_message(row):
        # Status and paper signature are information, not edit restrictions.
        return "" if row is not None else "Наказ не вибрано."

    def require_mutable_order(row, title="Накази"):
        return row is not None

    def new_order():
        book.select(maintenance_tab)

    def open_numbering_settings():
        book.select(settings_tab)
        try:
            win.after_idle(work_order_next_entry.focus_set)
        except Exception:
            pass

    def edit_order():
        row=selected_order()
        if row is not None and require_mutable_order(row):
            order_dialog(row)

    def create_assignment_order():
        order_dialog(force_type=ops.TYPE_VEHICLE_ASSIGNMENT)

    def mark_paper_signed():
        row=selected_order()
        if row is None:
            return
        signed=not bool(int(row["paper_original_signed"] or 0))
        if not core.messagebox.askyesno(
            "Позначка про паперовий підпис",
            ("Позначити цей наказ як підписаний на папері?"
             if signed else "Зняти позначку про паперовий підпис?") +
            "\\n\\nЦе лише допоміжна позначка Taxo; паперовий примірник контролює користувач.",
            parent=win,
        ):
            return
        con2=core.db()
        try:
            ops.set_paper_original_signed(
                con2,row["id"],signed,
                history_note="Змінено позначку паперового підпису через UI"
            )
            con2.commit()
        except Exception as exc:
            con2.rollback(); core.messagebox.showerror("Накази",str(exc),parent=win); return
        finally:
            con2.close()
        refresh_orders(row["id"])

    def approve_selected():
        row=selected_order()
        if row is None:
            return
        if row["status"]==ops.ORDER_APPROVED:
            core.messagebox.showinfo(
                "Накази","Наказ уже діє в Taxo.",parent=win
            )
            return
        if not core.messagebox.askyesno(
            "Ввести наказ у дію в Taxo?",
            "Після цієї дії структуровані дані наказу почнуть діяти в Taxo. "
            "Наприклад, закріплення ТЗ/водія стане чинним для системи.\n\n"
            "Це НЕ означає юридичне підписання документа і не замінює паперовий оригінал.",
            parent=win,
        ):
            return
        con2=core.db()
        try:
            ops.approve_order(con2,row["id"]); con2.commit()
        except Exception as exc:
            con2.rollback(); core.messagebox.showerror("Накази",str(exc),parent=win); return
        finally:
            con2.close()
        refresh_orders(row["id"])

    def cancel_draft():
        row=selected_order()
        if row is None:
            return
        if not core.messagebox.askyesno(
            "Скасувати наказ?",
            "Позначити наказ №%s як скасований? Це не видаляє файл чи паперовий документ.\\n"
            "Наказ можна буде знову відредагувати або ввести в дію." % row["order_no"],
            parent=win,
        ):
            return
        con2=core.db()
        try:
            ops.cancel_order(con2,row["id"]); con2.commit()
        except Exception as exc:
            con2.rollback(); core.messagebox.showerror("Накази",str(exc),parent=win); return
        finally:
            con2.close()
        refresh_orders(row["id"])

    def delete_selected_order():
        row=selected_order()
        if row is None:
            return
        if not core.messagebox.askyesno(
            "Видалити наказ?",
            "Видалити наказ №%s від %s із робочого реєстру Taxo?\\n\\n"
            "Пов'язані з ним закріплення та учасники теж будуть вилучені з обліку Taxo. "
            "Паперові примірники й уже створені DOCX/PDF/JPG залишаться на диску. "
            "Відомості про видалення зберігатимуться в журналі." %
            (row["order_no"],ops.display_day(row["order_date"])),
            parent=win,
        ):
            return
        from order_edit_actions import delete_order
        con2=core.db()
        try:
            delete_order(con2,row["id"])
            con2.commit()
        except Exception as exc:
            con2.rollback(); core.messagebox.showerror("Накази",str(exc),parent=win); return
        finally:
            con2.close()
        refresh_orders()

    def show_history():
        row=selected_order()
        if row is None:
            return
        con2=core.db()
        try:
            history=list(ops.order_history(con2,row["id"]))
        finally:
            con2.close()
        dlg=core.tk.Toplevel(win)
        dlg.title("Історія наказу №%s" % row["order_no"])
        try:
            core.configure_toplevel(dlg,title=dlg.title(),minsize=(760,420))
        except Exception:
            dlg.geometry("900x520")
        frm=core.ttk.Frame(dlg,padding=12); frm.pack(fill="both",expand=True)
        core.ttk.Label(
            frm,
            text="Історія змін наказу та пов'язаних закріплень. Старі записи не переписуються.",
            style="Muted.TLabel",
        ).pack(anchor="w",pady=(0,8))
        tree_frame=core.ttk.Frame(frm); tree_frame.pack(fill="both",expand=True)
        tree_frame.rowconfigure(0,weight=1); tree_frame.columnconfigure(0,weight=1)
        htree=core.ttk.Treeview(
            tree_frame,columns=("at","entity","action","note"),show="headings"
        )
        for key,label,width in (
            ("at","Коли",170),("entity","Об'єкт",120),
            ("action","Дія",150),("note","Примітка",420)
        ):
            htree.heading(key,text=label); htree.column(key,width=width,anchor="w")
        hy=core.ttk.Scrollbar(tree_frame,orient="vertical",command=htree.yview)
        hx=core.ttk.Scrollbar(tree_frame,orient="horizontal",command=htree.xview)
        htree.configure(yscrollcommand=hy.set,xscrollcommand=hx.set)
        htree.grid(row=0,column=0,sticky="nsew"); hy.grid(row=0,column=1,sticky="ns"); hx.grid(row=1,column=0,sticky="ew")
        action_labels={
            "create":"Створено","update":"Змінено","approve":"Введено в дію",
            "cancel":"Скасовано","paper_signed":"Паперовий оригінал підписано",
            "paper_unmarked":"Знято позначку","delete":"Видалено",
            "superseded":"Замінено новим наказом",
            "entity_add":"Додано учасника / ТЗ",
            "entity_remove":"Прибрано учасника / ТЗ",
        }
        entity_labels={"order":"Наказ","assignment":"Закріплення","order_entity":"Учасник / ТЗ"}
        for item in history:
            htree.insert("", "end", values=(
                item["changed_at"], entity_labels.get(item["entity_type"],item["entity_type"]),
                action_labels.get(item["action"],item["action"]), item["note"] or "—"
            ))
        if not history:
            core.ttk.Label(frm,text="Історії змін ще немає.").pack(anchor="w",pady=8)

    def _order_print_data(row):
        con2=core.db()
        try:
            assignments=ops.order_assignments(con2,row["id"])
            entities=ops.list_order_entities(con2,row["id"]) if hasattr(ops,"list_order_entities") else []
            company_row=con2.execute("SELECT * FROM company WHERE id=1").fetchone()
            company={key:company_row[key] for key in company_row.keys()} if company_row else {}
            control=ops.employee_name(con2,row["control_employee_id"])
        finally:
            con2.close()
        return assignments,entities,company,control

    def export_order(row,parent=None):
        assignments,_entities,company,control=_order_print_data(row)
        return save_and_preview_order(
            core,ops,row,assignments,company,control,parent or win
        )

    def export_selected():
        row=selected_order()
        if row is not None:
            export_order(row,win)

    def preview_order(row=None):
        row=row or selected_order()
        if row is None:
            return
        assignments,entities,company,control=_order_print_data(row)
        preview=ops.order_preview_text(
            row,assignments=assignments,entities=entities,company=company,control_name=control
        )
        dlg=core.tk.Toplevel(win)
        dlg.title("Перегляд наказу №%s" % row["order_no"])
        try:
            core.configure_toplevel(dlg,title=dlg.title(),minsize=(760,560))
        except Exception:
            dlg.geometry("900x700")
        frm=core.ttk.Frame(dlg,padding=12); frm.pack(fill="both",expand=True)
        core.ttk.Label(
            frm,
            text=("Перевірте зміст наказу. Оберіть формат: Word, PDF, JPG "
                  "(для кожної сторінки) або створіть усі. "
                  "Перегляд доступний у Taxo, відкриття — у програмі комп'ютера."),
            style="Muted.TLabel",wraplength=820,justify="left",
        ).pack(anchor="w",pady=(0,8))
        text_frame=core.ttk.Frame(frm); text_frame.pack(fill="both",expand=True)
        text_frame.rowconfigure(0,weight=1); text_frame.columnconfigure(0,weight=1)
        viewer=core.tk.Text(text_frame,wrap="word",font=("TkDefaultFont",11),padx=12,pady=12)
        sy=core.ttk.Scrollbar(text_frame,orient="vertical",command=viewer.yview)
        viewer.configure(yscrollcommand=sy.set)
        viewer.grid(row=0,column=0,sticky="nsew"); sy.grid(row=0,column=1,sticky="ns")
        viewer.insert("1.0",preview); viewer.configure(state="disabled")

        generated={}
        status_var=core.tk.StringVar(value="Файли ще не створено.")
        def make_formats(formats):
            try:
                results=generate_order_formats(
                    core,ops,row,assignments,entities,company,control,
                    formats=formats,parent=dlg,
                )
            except Exception as exc:
                core.messagebox.showerror("Формування наказу",str(exc),parent=dlg)
                return
            generated.update(results)
            if not results:
                status_var.set("Файл не створено.")
                return
            summary=", ".join(
                "%s: %d" % (kind.upper(), len(paths))
                for kind,paths in results.items()
            )
            status_var.set("Збережено: "+summary)
            preferred=next((kind for kind in ("pdf","docx","jpg") if kind in results),None)
            if preferred:
                view_format(preferred)

        def view_format(kind,external=False):
            paths=generated.get(kind,())
            if not paths:
                core.messagebox.showinfo(
                    "Документи наказу",
                    "Спочатку створіть %s для цього наказу." % kind.upper(),parent=dlg
                )
                return
            try:
                open_order_format(core,paths,dlg,external=external)
                if external and len(paths)>1:
                    core.messagebox.showinfo(
                        "Сторінки JPG",
                        "Відкрито першу сторінку. Інші JPG-сторінки збережено поруч:\n%s"
                        % paths[0].parent,parent=dlg
                    )
            except Exception as exc:
                core.messagebox.showwarning(
                    "Відкриття документа",
                    "Файл збережено, але його не вдалося відкрити:\n%s" % exc,
                    parent=dlg
                )

        formats_box=core.ttk.LabelFrame(frm,text="Документи наказу",padding=(8,6))
        formats_box.pack(fill="x",pady=(8,0))
        for col in range(4):
            formats_box.columnconfigure(col,weight=1)
        for col,(title,kinds) in enumerate((
            ("Створити DOCX",("docx",)),("Створити PDF",("pdf",)),
            ("Створити JPG",("jpg",)),("Створити все",("docx","pdf","jpg"))
        )):
            core.ttk.Button(
                formats_box,text=title,command=lambda f=kinds:make_formats(f)
            ).grid(row=0,column=col,sticky="ew",padx=3,pady=3)
        for col,kind in enumerate(("docx","pdf","jpg")):
            core.ttk.Button(
                formats_box,text="Перегляд "+kind.upper(),
                command=lambda f=kind:view_format(f)
            ).grid(row=1,column=col,sticky="ew",padx=3,pady=3)
            core.ttk.Button(
                formats_box,text="Відкрити у програмі: "+kind.upper(),
                command=lambda f=kind:view_format(f,external=True)
            ).grid(row=2,column=col,sticky="ew",padx=3,pady=3)
        core.ttk.Label(
            formats_box,textvariable=status_var,style="Muted.TLabel",
            wraplength=810,justify="left"
        ).grid(row=3,column=0,columnspan=4,sticky="w",padx=4,pady=(4,0))
        bar=core.ttk.Frame(frm); bar.pack(fill="x",pady=(8,0))
        core.ttk.Button(bar,text="Закрити",command=dlg.destroy).pack(side="right")
        core.ttk.Button(
            bar,text="Сформувати PDF / друк",style="Accent.TButton",
            command=lambda:make_formats(("pdf",))
        ).pack(side="right",padx=(0,6))
        if not order_mutability_message(row):
            core.ttk.Button(
                bar,text="Редагувати чернетку",
                command=lambda:(dlg.destroy(),order_dialog(row))
            ).pack(side="left")
        dlg.transient(win)
        try:
            dlg.lift(); dlg.focus_force()
        except Exception:
            pass
        return dlg

    order_actions = (
        ("Новий наказ…", new_order, "Accent.TButton"),
        ("Переглянути / друк", preview_order, "Accent.TButton"),
        ("Нумерація наказів…", open_numbering_settings, None),
        ("Редагувати чернетку", edit_order, None),
        ("Ввести в дію в Taxo", approve_selected, None),
        ("Історія…", show_history, None),
        ("Скасувати наказ", cancel_draft, None),\n        ("Видалити наказ", delete_selected_order, None),
        ("Сформувати PDF", export_selected, None),
        ("Підпис на папері: так / ні", mark_paper_signed, None),
    )
    for col in range(3):
        order_action_bar.columnconfigure(col, weight=1)
    for index, (label, command, style) in enumerate(order_actions):
        kwargs = {"text": label, "command": command}
        if style:
            kwargs["style"] = style
        core.ttk.Button(order_action_bar, **kwargs).grid(
            row=index // 3,
            column=index % 3,
            sticky="ew",
            padx=(0 if index % 3 == 0 else 4, 4 if index % 3 != 2 else 0),
            pady=3,
        )
    order_tree.bind("<Double-1>",lambda _e:preview_order(),add="+")

    # Assignments
    at=core.ttk.Frame(assignments_tab,padding=(10,10,10,4)); at.pack(fill="x")
    selected_order_var=core.tk.StringVar(value="Виберіть наказ про закріплення або створіть новий.")
    core.ttk.Label(at,textvariable=selected_order_var,style="Subtitle.TLabel").pack(side="left")
    core.ttk.Button(at,text="Створити наказ про закріплення",style="Accent.TButton",command=create_assignment_order).pack(side="right")
    aframe=core.ttk.Frame(assignments_tab); aframe.pack(fill="both",expand=True,padx=10,pady=(0,10)); aframe.rowconfigure(0,weight=1); aframe.columnconfigure(0,weight=1)
    acols=("seq","vehicle","plate","driver","from","until"); atree=core.ttk.Treeview(aframe,columns=acols,show="headings",selectmode="browse")
    for key,label,width in (("seq","№",50),("vehicle","ТЗ",260),("plate","Держ. номер",120),("driver","Водій",300),("from","З",100),("until","До",100)):
        atree.heading(key,text=label); atree.column(key,width=width,anchor="w")
    asy=core.ttk.Scrollbar(aframe,orient="vertical",command=atree.yview); asx=core.ttk.Scrollbar(aframe,orient="horizontal",command=atree.xview)
    atree.configure(yscrollcommand=asy.set,xscrollcommand=asx.set); atree.grid(row=0,column=0,sticky="nsew"); asy.grid(row=0,column=1,sticky="ns"); asx.grid(row=1,column=0,sticky="ew")
    assignment_cache={}

    def current_assignment_order():
        row=selected_order(quiet=True)
        return row if row is not None and row["order_type"]==ops.TYPE_VEHICLE_ASSIGNMENT else None
    def refresh_assignments():
        for iid in atree.get_children(): atree.delete(iid)
        assignment_cache.clear(); row=current_assignment_order()
        if row is None: selected_order_var.set("Виберіть наказ про закріплення або створіть новий."); return
        state_label = "Діє в Taxo" if row["status"]==ops.ORDER_APPROVED else ops.ORDER_STATUS_LABELS.get(row["status"],row["status"])
        selected_order_var.set("Наказ №%s від %s — %s"%(row["order_no"],ops.display_day(row["order_date"]),state_label))
        con2=core.db()
        try: items=ops.order_assignments(con2,row["id"])
        finally: con2.close()
        for item in items:
            aid=int(item["id"]); assignment_cache[aid]=item; driver=" ".join(str(item[k] or "").strip() for k in ("last_name","first_name","middle_name") if str(item[k] or "").strip())
            atree.insert("","end",iid=str(aid),values=(item["sequence_no"],item["make_model"] or item["vehicle_name"],item["plate"],driver,ops.display_day(item["valid_from"]),ops.display_day(item["valid_until"])))
    order_tree.bind("<<TreeviewSelect>>",lambda _e:refresh_assignments(),add="+")

    def assignment_dialog(existing=None):
        order=current_assignment_order()
        if order is None: core.messagebox.showinfo("Закріплення","Спочатку виберіть або створіть наказ про закріплення.",parent=win); return
        if not require_mutable_order(order, "Закріплення"):
            return
        con2=core.db()
        try:
            vehicles=ops.list_vehicle_choices(con2,active_only=existing is None)
            emps=ops.list_driver_choices(con2,active_only=existing is None)
        finally: con2.close()
        vlabels=[x["label"] for x in vehicles]; elabels=[x["label"] for x in emps]; vmap={x["label"]:x["id"] for x in vehicles}; emap={x["label"]:x["id"] for x in emps}; vid_to_label={x["id"]:x["label"] for x in vehicles}; eid_to_label={x["id"]:x["label"] for x in emps}
        dlg=core.tk.Toplevel(win); dlg.title("Редагувати закріплення" if existing else "Додати закріплення"); frm=core.ttk.Frame(dlg,padding=14); frm.pack(fill="both",expand=True); frm.columnconfigure(1,weight=1)
        vv=core.tk.StringVar(value=vid_to_label.get(existing["vehicle_id"],"") if existing else ""); ev=core.tk.StringVar(value=eid_to_label.get(existing["employee_id"],"") if existing else ""); fv=core.tk.StringVar(value=ops.display_day(existing["valid_from"]) if existing else ops.display_day(order["order_date"])); uv=core.tk.StringVar(value=ops.display_day(existing["valid_until"]) if existing else "")
        for r,(label,var,values) in enumerate((("Транспортний засіб",vv,vlabels),("Водій із бази водіїв",ev,elabels),("Діє з",fv,None),("Діє до (необов'язково)",uv,None))):
            core.ttk.Label(frm,text=label).grid(row=r,column=0,sticky="w",padx=(0,8),pady=6); widget=core.ttk.Combobox(frm,textvariable=var,values=values,state="readonly") if values is not None else core.ttk.Entry(frm,textvariable=var); widget.grid(row=r,column=1,sticky="ew",pady=6)
        def save_assignment():
            if vv.get() not in vmap or ev.get() not in emap: core.messagebox.showerror("Закріплення","Виберіть ТЗ і водія.",parent=dlg); return
            con3=core.db()
            try:
                if existing: ops.update_vehicle_assignment(con3,existing["id"],vehicle_id=vmap[vv.get()],employee_id=emap[ev.get()],valid_from=fv.get(),valid_until=uv.get(),history_note="Редагування через інтерфейс")
                else: ops.add_vehicle_assignment(con3,order["id"],vmap[vv.get()],emap[ev.get()],valid_from=fv.get(),valid_until=uv.get())
                con3.commit()
            except Exception as exc: con3.rollback(); core.messagebox.showerror("Закріплення",str(exc),parent=dlg); return
            finally: con3.close()
            dlg.destroy(); refresh_assignments()
        bar=core.ttk.Frame(frm); bar.grid(row=4,column=0,columnspan=2,sticky="ew",pady=(10,0)); core.ttk.Button(bar,text="Скасувати",command=dlg.destroy).pack(side="right"); core.ttk.Button(bar,text="Зберегти" if existing else "Додати",style="Accent.TButton",command=save_assignment).pack(side="right",padx=(0,6)); dlg.transient(win)
    def add_assignment(): assignment_dialog()

    def add_assignments_bulk():
        order=current_assignment_order()
        if order is None:
            core.messagebox.showinfo("Закріплення","Спочатку виберіть або створіть наказ про закріплення.",parent=win); return
        if not require_mutable_order(order,"Закріплення"):
            return
        con2=core.db()
        try:
            vehicles=ops.list_vehicle_choices(con2,active_only=True)
            drivers=ops.list_driver_choices(con2,active_only=True)
        finally: con2.close()
        dlg=core.tk.Toplevel(win); dlg.title("Додати кілька закріплень")
        try: core.configure_toplevel(dlg,title=dlg.title(),minsize=(820,560))
        except Exception: dlg.geometry("900x620")
        frm=core.ttk.Frame(dlg,padding=14); frm.pack(fill="both",expand=True)
        frm.columnconfigure(0,weight=1); frm.columnconfigure(1,weight=1); frm.rowconfigure(1,weight=1)
        core.ttk.Label(frm,text="Транспортні засоби").grid(row=0,column=0,sticky="w")
        core.ttk.Label(frm,text="Водії").grid(row=0,column=1,sticky="w")
        vlist=core.tk.Listbox(frm,selectmode="extended",exportselection=False,height=14)
        dlist=core.tk.Listbox(frm,selectmode="extended",exportselection=False,height=14)
        vlist.grid(row=1,column=0,sticky="nsew",padx=(0,4),pady=4)
        dlist.grid(row=1,column=1,sticky="nsew",padx=(4,0),pady=4)
        for item in vehicles: vlist.insert("end",item["label"])
        for item in drivers: dlist.insert("end",item["label"])
        count_var=core.tk.StringVar(value="Вибрано: ТЗ — 0; водіїв — 0")
        def update_count(_event=None):
            count_var.set("Вибрано: ТЗ — %d; водіїв — %d" % (len(vlist.curselection()),len(dlist.curselection())))
        vlist.bind("<<ListboxSelect>>",update_count); dlist.bind("<<ListboxSelect>>",update_count)
        core.ttk.Label(frm,textvariable=count_var,style="Subtitle.TLabel").grid(row=2,column=0,columnspan=2,sticky="w",pady=(4,2))
        core.ttk.Label(
            frm,
            text=("1 ТЗ + кілька водіїв або однакова кількість ТЗ і водіїв. "
                  "При однаковій кількості пари формуються за порядком вибору. "
                  "Один водій не закріплюється одночасно за кількома ТЗ."),
            style="Muted.TLabel",wraplength=760,justify="left",
        ).grid(row=3,column=0,columnspan=2,sticky="w",pady=(0,6))
        dates=core.ttk.Frame(frm); dates.grid(row=4,column=0,columnspan=2,sticky="ew"); dates.columnconfigure(1,weight=1); dates.columnconfigure(3,weight=1)
        from_var=core.tk.StringVar(value=ops.display_day(order["order_date"]))
        until_var=core.tk.StringVar(value="")
        core.ttk.Label(dates,text="Діє з").grid(row=0,column=0,sticky="w",padx=(0,6))
        core.ttk.Entry(dates,textvariable=from_var).grid(row=0,column=1,sticky="ew",padx=(0,10))
        core.ttk.Label(dates,text="Діє до (необов'язково)").grid(row=0,column=2,sticky="w",padx=(0,6))
        core.ttk.Entry(dates,textvariable=until_var).grid(row=0,column=3,sticky="ew")
        bar=core.ttk.Frame(frm); bar.grid(row=5,column=0,columnspan=2,sticky="ew",pady=(10,0))
        def save_bulk():
            vehicle_ids=[vehicles[int(i)]["id"] for i in vlist.curselection()]
            driver_ids=[drivers[int(i)]["id"] for i in dlist.curselection()]
            try:
                pairs=ops.build_assignment_pairs(vehicle_ids,driver_ids)
                if not pairs:
                    raise ValueError("Виберіть транспорт і водіїв.")
            except Exception as exc:
                core.messagebox.showerror("Закріплення",str(exc),parent=dlg); return
            con3=core.db()
            try:
                ops.add_vehicle_assignments_bulk(
                    con3,order["id"],pairs,valid_from=from_var.get(),valid_until=until_var.get()
                )
                con3.commit()
            except Exception as exc:
                con3.rollback(); core.messagebox.showerror("Закріплення",str(exc),parent=dlg); return
            finally: con3.close()
            dlg.destroy(); refresh_assignments()
        core.ttk.Button(bar,text="Скасувати",command=dlg.destroy).pack(side="right")
        core.ttk.Button(bar,text="Додати вибрані пари",style="Accent.TButton",command=save_bulk).pack(side="right",padx=(0,6))
        dlg.transient(win)

    def edit_assignment():
        sel=atree.selection()
        if not sel: core.messagebox.showinfo("Закріплення","Виберіть рядок ТЗ / водія.",parent=win); return
        assignment_dialog(assignment_cache.get(int(sel[0])))
    def remove_assignment():
        order=current_assignment_order(); sel=atree.selection()
        if order is None or not sel:return
        if not require_mutable_order(order, "Закріплення"):
            return
        con2=core.db()
        try: ops.delete_vehicle_assignment(con2,int(sel[0]),history_note="Видалення через інтерфейс"); con2.commit()
        except Exception as exc: con2.rollback(); core.messagebox.showerror("Закріплення",str(exc),parent=win); return
        finally: con2.close()
        refresh_assignments()
    abar=core.ttk.Frame(assignments_tab,padding=(10,0,10,10)); abar.pack(fill="x")
    core.ttk.Button(abar,text="Додати багато…",style="Accent.TButton",command=add_assignments_bulk).pack(side="left")
    core.ttk.Button(abar,text="Додати одну пару",command=add_assignment).pack(side="left",padx=6)
    core.ttk.Button(abar,text="Редагувати",command=edit_assignment).pack(side="left",padx=6)
    core.ttk.Button(abar,text="Прибрати",command=remove_assignment).pack(side="left",padx=6)

    # Structured employees / vehicles for non-assignment orders.
    ehead=core.ttk.Frame(entities_tab,padding=(10,10,10,4)); ehead.pack(fill="x")
    selected_entity_order_var=core.tk.StringVar(value="Виберіть наказ.")
    core.ttk.Label(ehead,textvariable=selected_entity_order_var,style="Subtitle.TLabel").pack(anchor="w")
    core.ttk.Label(
        ehead,
        text=("Тут зберігаються конкретні працівники та ТЗ, яких стосується наказ. "
              "Taxo фіксує знімок реквізитів на момент додавання, тому подальша зміна картки "
              "не переписує історичний перелік. Для наказу про закріплення використовуйте окрему вкладку."),
        style="Muted.TLabel",wraplength=1080,justify="left",
    ).pack(anchor="w",pady=(3,6))

    eframe=core.ttk.Frame(entities_tab); eframe.pack(fill="both",expand=True,padx=10,pady=(0,8))
    eframe.rowconfigure(0,weight=1); eframe.columnconfigure(0,weight=1)
    ecols=("seq","kind","role","name","identity","note")
    etree=core.ttk.Treeview(eframe,columns=ecols,show="headings",selectmode="extended")
    for key,label,width in (
        ("seq","№",45),("kind","Тип",90),("role","Роль у наказі",200),
        ("name","Працівник / ТЗ",340),("identity","Однозначний реквізит",250),
        ("note","Примітка",220),
    ):
        etree.heading(key,text=label); etree.column(key,width=width,anchor="w")
    esy=core.ttk.Scrollbar(eframe,orient="vertical",command=etree.yview)
    esx=core.ttk.Scrollbar(eframe,orient="horizontal",command=etree.xview)
    etree.configure(yscrollcommand=esy.set,xscrollcommand=esx.set)
    etree.grid(row=0,column=0,sticky="nsew"); esy.grid(row=0,column=1,sticky="ns"); esx.grid(row=1,column=0,sticky="ew")
    entity_cache={}

    def current_entity_order():
        return selected_order(quiet=True)

    def refresh_order_entities():
        for iid in etree.get_children(): etree.delete(iid)
        entity_cache.clear()
        order=current_entity_order()
        if order is None:
            selected_entity_order_var.set("Виберіть наказ.")
            return
        state_label="Діє в Taxo" if order["status"]==ops.ORDER_APPROVED else ops.ORDER_STATUS_LABELS.get(order["status"],order["status"])
        selected_entity_order_var.set(
            "Наказ №%s від %s — %s" % (order["order_no"],ops.display_day(order["order_date"]),state_label)
        )
        if str(order["order_type"])==ops.TYPE_VEHICLE_ASSIGNMENT:
            selected_entity_order_var.set(
                "Наказ №%s — для пар ТЗ/водій використовуйте вкладку «Закріплення водіїв»." % order["order_no"]
            )
            return
        con2=core.db()
        try: items=ops.list_order_entities(con2,order["id"])
        finally: con2.close()
        for item in items:
            link_id=int(item["id"]); entity_cache[link_id]=item; view=ops.order_entity_view(item)
            etree.insert(
                "","end",iid=str(link_id),
                values=(
                    item["sequence_no"],view["type_label"],view["role"] or "—",
                    view["display"],view["identifier"],item["note"] or "—",
                ),
            )

    order_tree.bind("<<TreeviewSelect>>",lambda _e:refresh_order_entities(),add="+")

    def entity_picker(entity_type):
        order=current_entity_order()
        if order is None:
            core.messagebox.showinfo("Учасники / ТЗ","Спочатку виберіть наказ.",parent=win); return
        if str(order["order_type"])==ops.TYPE_VEHICLE_ASSIGNMENT:
            core.messagebox.showinfo(
                "Учасники / ТЗ",
                "Для цього типу наказу пари ТЗ/водій ведуться у вкладці «Закріплення водіїв».",
                parent=win,
            ); return
        if not require_mutable_order(order,"Учасники / ТЗ"):
            return
        con2=core.db()
        try:
            if entity_type==ops.ORDER_ENTITY_EMPLOYEE:
                choices=ops.order_employee_choices(con2,order["order_type"],active_only=True)
            else:
                choices=ops.list_vehicle_choices(con2,active_only=True)
        finally: con2.close()
        if not choices:
            core.messagebox.showinfo(
                "Учасники / ТЗ",
                "У базі немає активних записів для цього вибору.",
                parent=win,
            ); return

        dlg=core.tk.Toplevel(win)
        dlg.title("Додати працівників" if entity_type==ops.ORDER_ENTITY_EMPLOYEE else "Додати транспортні засоби")
        try: core.configure_toplevel(dlg,title=dlg.title(),minsize=(760,520))
        except Exception: dlg.geometry("860x600")
        frm=core.ttk.Frame(dlg,padding=14); frm.pack(fill="both",expand=True)
        frm.columnconfigure(0,weight=1); frm.rowconfigure(2,weight=1)
        core.ttk.Label(
            frm,
            text=("Виберіть один або кілька записів. Пошук працює за ПІБ/табельним №/ідентифікатором "
                  "або за держномером/VIN."),
            style="Muted.TLabel",wraplength=760,justify="left",
        ).grid(row=0,column=0,sticky="ew",pady=(0,6))
        search_var=core.tk.StringVar(value="")
        search_entry=core.ttk.Entry(frm,textvariable=search_var)
        search_entry.grid(row=1,column=0,sticky="ew",pady=(0,6))
        list_frame=core.ttk.Frame(frm); list_frame.grid(row=2,column=0,sticky="nsew")
        list_frame.rowconfigure(0,weight=1); list_frame.columnconfigure(0,weight=1)
        lb=core.tk.Listbox(list_frame,selectmode="extended",exportselection=False)
        lsy=core.ttk.Scrollbar(list_frame,orient="vertical",command=lb.yview)
        lb.configure(yscrollcommand=lsy.set); lb.grid(row=0,column=0,sticky="nsew"); lsy.grid(row=0,column=1,sticky="ns")
        visible=[]

        def refill(*_args):
            query=str(search_var.get() or "").strip().lower()
            lb.delete(0,"end"); visible.clear()
            for choice in choices:
                hay=str(choice.get("search_text") or choice.get("label") or "").lower()
                if query and query not in hay:
                    continue
                visible.append(choice); lb.insert("end",choice["label"])
        search_var.trace_add("write",refill); refill()

        fields=core.ttk.Frame(frm); fields.grid(row=3,column=0,sticky="ew",pady=(8,0)); fields.columnconfigure(1,weight=1)
        role_var=core.tk.StringVar(value=ops.default_order_entity_role(order["order_type"],entity_type))
        note_var=core.tk.StringVar(value="")
        core.ttk.Label(fields,text="Роль / призначення").grid(row=0,column=0,sticky="w",padx=(0,8),pady=4)
        core.ttk.Entry(fields,textvariable=role_var).grid(row=0,column=1,sticky="ew",pady=4)
        core.ttk.Label(fields,text="Примітка").grid(row=1,column=0,sticky="w",padx=(0,8),pady=4)
        core.ttk.Entry(fields,textvariable=note_var).grid(row=1,column=1,sticky="ew",pady=4)
        bar=core.ttk.Frame(frm); bar.grid(row=4,column=0,sticky="ew",pady=(10,0))

        def save_entities():
            selected=[visible[int(index)] for index in lb.curselection() if int(index)<len(visible)]
            if not selected:
                core.messagebox.showerror("Учасники / ТЗ","Виберіть хоча б один запис.",parent=dlg); return
            con3=core.db()
            try:
                created=ops.add_order_entities(
                    con3,order["id"],entity_type,[row["id"] for row in selected],
                    role=role_var.get(),note=note_var.get(),
                )
                con3.commit()
            except Exception as exc:
                con3.rollback(); core.messagebox.showerror("Учасники / ТЗ",str(exc),parent=dlg); return
            finally: con3.close()
            dlg.destroy(); refresh_order_entities()
            if len(created)<len(selected):
                core.messagebox.showinfo(
                    "Учасники / ТЗ",
                    "Нові записи додано. Частина вибраних уже була в наказі з такою самою роллю.",
                    parent=win,
                )

        core.ttk.Button(bar,text="Скасувати",command=dlg.destroy).pack(side="right")
        core.ttk.Button(bar,text="Додати вибрані",style="Accent.TButton",command=save_entities).pack(side="right",padx=(0,6))
        dlg.transient(win); search_entry.focus_set()

    def remove_order_entities():
        order=current_entity_order(); selected=tuple(etree.selection())
        if order is None or not selected:
            core.messagebox.showinfo("Учасники / ТЗ","Виберіть один або кілька рядків.",parent=win); return
        if not require_mutable_order(order,"Учасники / ТЗ"):
            return
        if not core.messagebox.askyesno(
            "Прибрати з наказу?",
            "Прибрати вибрані записи зі структурованого переліку чернетки?",
            parent=win,
        ): return
        con2=core.db()
        try:
            for iid in selected:
                ops.delete_order_entity(
                    con2,int(iid),history_note="Прибрано через вкладку «Учасники / ТЗ»",
                )
            con2.commit()
        except Exception as exc:
            con2.rollback(); core.messagebox.showerror("Учасники / ТЗ",str(exc),parent=win); return
        finally: con2.close()
        refresh_order_entities()

    ebar=core.ttk.Frame(entities_tab,padding=(10,0,10,10)); ebar.pack(fill="x")
    core.ttk.Button(
        ebar,text="Додати працівників…",style="Accent.TButton",
        command=lambda:entity_picker(ops.ORDER_ENTITY_EMPLOYEE),
    ).pack(side="left")
    core.ttk.Button(
        ebar,text="Додати ТЗ…",command=lambda:entity_picker(ops.ORDER_ENTITY_VEHICLE),
    ).pack(side="left",padx=6)
    core.ttk.Button(ebar,text="Прибрати вибрані",command=remove_order_entities).pack(side="left",padx=6)
    core.ttk.Button(ebar,text="Оновити",command=refresh_order_entities).pack(side="right")

    mbody=core.ttk.Frame(maintenance_tab,padding=14); mbody.pack(fill="both",expand=True)
    core.ttk.Label(mbody,text="Що потрібно оформити?",style="Title.TLabel").pack(anchor="w")
    core.ttk.Label(
        mbody,
        text=("Почніть не з порожнього бланка, а з потрібної дії. Taxo підставить типову тему, вступ і редаговану заготовку пунктів. "
              "Це робоча заготовка, а не юридичне твердження: перед підписанням перевірте фактичні реквізити й зміст."),
        style="Muted.TLabel",wraplength=1040,justify="left"
    ).pack(anchor="w",pady=(4,8))
    quick=core.ttk.LabelFrame(mbody,text="Найчастіші дії",padding=8); quick.pack(fill="x",pady=(0,10))
    quick_types=[
        ("Закріпити ТЗ за водіями", ops.TYPE_VEHICLE_ASSIGNMENT),
        ("Організувати ТО / ремонти", ops.TYPE_MAINTENANCE_REPAIR),
    ]
    if hasattr(ops,"TYPE_RESPONSIBLE_PERSONS"):
        quick_types.append(("Призначити відповідальних",ops.TYPE_RESPONSIBLE_PERSONS))
    if hasattr(ops,"TYPE_VEHICLE_RELEASE_RETURN"):
        quick_types.append(("Порядок випуску / повернення ТЗ",ops.TYPE_VEHICLE_RELEASE_RETURN))
    for col in range(2):
        quick.columnconfigure(col, weight=1)
    for index,(label,order_type) in enumerate(quick_types):
        core.ttk.Button(
            quick,text=label,command=lambda t=order_type:order_dialog(force_type=t)
        ).grid(
            row=index // 2,
            column=index % 2,
            sticky="ew",
            padx=(0 if index % 2 == 0 else 4, 4 if index % 2 == 1 else 0),
            pady=3,
        )
    core.ttk.Label(
        mbody,
        text="Повний каталог типів наказів",
        style="Subtitle.TLabel",
    ).pack(anchor="w",pady=(2,4))
    catalog_frame=core.ttk.Frame(mbody); catalog_frame.pack(fill="both",expand=True); catalog_frame.rowconfigure(0,weight=1); catalog_frame.columnconfigure(0,weight=1)
    catalog_tree=core.ttk.Treeview(catalog_frame,columns=("group","type","subject"),show="headings",selectmode="browse")
    for key,label,width in (("group","Група",250),("type","Тип наказу",320),("subject","Типова тема",430)):
        catalog_tree.heading(key,text=label); catalog_tree.column(key,width=width,anchor="w")
    csy=core.ttk.Scrollbar(catalog_frame,orient="vertical",command=catalog_tree.yview)
    csx=core.ttk.Scrollbar(catalog_frame,orient="horizontal",command=catalog_tree.xview)
    catalog_tree.configure(yscrollcommand=csy.set,xscrollcommand=csx.set)
    catalog_tree.grid(row=0,column=0,sticky="nsew"); csy.grid(row=0,column=1,sticky="ns"); csx.grid(row=1,column=0,sticky="ew")
    catalog_type_by_iid={}
    catalog_index=0
    for group_key,group_label in ops.ORDER_GROUP_LABELS.items():
        for order_type in ops.ORDER_GROUP_TYPES.get(group_key,()):
            catalog_index+=1; iid=str(catalog_index); catalog_type_by_iid[iid]=order_type
            catalog_tree.insert("","end",iid=iid,values=(group_label,ops.ORDER_TYPE_LABELS[order_type],ops.DEFAULT_SUBJECTS.get(order_type,"") or "—"))
    def create_from_catalog():
        sel=catalog_tree.selection()
        if not sel:
            core.messagebox.showinfo("Каталог наказів","Виберіть тип наказу.",parent=win); return
        order_type=catalog_type_by_iid.get(sel[0])
        if order_type: order_dialog(force_type=order_type)
    cbar=core.ttk.Frame(mbody); cbar.pack(fill="x",pady=(8,0))
    core.ttk.Button(cbar,text="Створити наказ за вибраним типом",style="Accent.TButton",command=create_from_catalog).pack(side="left")
    catalog_tree.bind("<Double-1>",lambda _e:create_from_catalog())

    refresh_orders(); return win
