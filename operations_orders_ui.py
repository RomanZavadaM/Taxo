# -*- coding: utf-8 -*-
"""Taxo 10.7-r2 — UI розділу «Експлуатація»."""
from __future__ import annotations

from datetime import date

import operations_orders as ops


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
        existing.lift()
        existing.focus_force()
        return existing

    ops.ensure_schema(core)
    win = core.tk.Toplevel(app)
    app._operations_center_window = win
    try:
        core.fit_window_to_screen(win, 1260, 780, 940, 600)
        core.configure_toplevel(win, title="Експлуатація", minsize=(940, 600))
    except Exception:
        win.geometry("1260x780")
    win.title("Taxo / %s — Експлуатація" % app._company_name_value())

    body = core.ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)
    core.ttk.Label(body, text="Експлуатація", style="HeroTitle.TLabel").pack(anchor="w")
    core.ttk.Label(
        body,
        text=(
            "Накази, закріплення водіїв за транспортними засобами та відповідальні особи. "
            "Цей розділ є основою для подальших модулів ТО, ремонтів та інших експлуатаційних документів."
        ),
        style="Muted.TLabel", wraplength=1180, justify="left",
    ).pack(anchor="w", pady=(2, 8))

    book = core.ttk.Notebook(body)
    book.pack(fill="both", expand=True)
    orders_tab = core.ttk.Frame(book)
    assignments_tab = core.ttk.Frame(book)
    settings_tab = core.ttk.Frame(book)
    maintenance_tab = core.ttk.Frame(book)
    book.add(orders_tab, text="Накази")
    book.add(assignments_tab, text="Закріплення водіїв")
    book.add(settings_tab, text="Відповідальні")
    book.add(maintenance_tab, text="ТО / ремонти")

    # ------------------------------------------------------------------
    # Settings / responsible persons
    # ------------------------------------------------------------------
    settings_box = core.ttk.Frame(settings_tab, padding=14)
    settings_box.pack(fill="both", expand=True)
    settings_box.columnconfigure(1, weight=1)
    con = core.db()
    try:
        cfg = ops.settings(con)
        employees, emp_by_label, emp_by_id = _employee_maps(con)
    finally:
        con.close()
    employee_labels = [row["label"] for row in employees]
    operations_resp_var = core.tk.StringVar(value=emp_by_id.get(cfg["operations_responsible_employee_id"], "") if cfg else "")
    military_resp_var = core.tk.StringVar(value=emp_by_id.get(cfg["military_transport_responsible_employee_id"], "") if cfg else "")
    place_var = core.tk.StringVar(value=(cfg["order_place"] if cfg else "") or "")
    for row, (label, var) in enumerate((
        ("Відповідальний за експлуатацію", operations_resp_var),
        ("Відповідальний за військово-транспортний обов'язок", military_resp_var),
    )):
        core.ttk.Label(settings_box, text=label).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=7)
        core.ttk.Combobox(settings_box, textvariable=var, values=employee_labels, state="readonly").grid(
            row=row, column=1, sticky="ew", pady=7
        )
    core.ttk.Label(settings_box, text="Місце складання наказів").grid(row=2, column=0, sticky="w", padx=(0,10), pady=7)
    core.ttk.Entry(settings_box, textvariable=place_var).grid(row=2, column=1, sticky="ew", pady=7)
    core.ttk.Label(
        settings_box,
        text=(
            "Відомість ТЦК перед друком затверджується відповідальним у Taxo. "
            "Службові позначки про джерело імпорту у затверджену форму не друкуються."
        ),
        style="Muted.TLabel", wraplength=900, justify="left",
    ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 12))

    def save_settings():
        con2 = core.db()
        try:
            ops.save_settings(
                con2,
                operations_responsible_employee_id=emp_by_label.get(operations_resp_var.get()),
                military_transport_responsible_employee_id=emp_by_label.get(military_resp_var.get()),
                order_place=place_var.get(),
            )
            con2.commit()
        except Exception as exc:
            con2.rollback()
            core.messagebox.showerror("Експлуатація", str(exc), parent=win)
            return
        finally:
            con2.close()
        core.messagebox.showinfo("Експлуатація", "Відповідальних збережено.", parent=win)

    core.ttk.Button(settings_box, text="Зберегти", style="Accent.TButton", command=save_settings).grid(
        row=4, column=1, sticky="e"
    )

    # ------------------------------------------------------------------
    # Orders register
    # ------------------------------------------------------------------
    order_top = core.ttk.Frame(orders_tab, padding=(10,10,10,4))
    order_top.pack(fill="x")
    order_frame = core.ttk.Frame(orders_tab)
    order_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))
    order_frame.rowconfigure(0, weight=1)
    order_frame.columnconfigure(0, weight=1)
    cols = ("date","no","type","subject","status","control")
    order_tree = core.ttk.Treeview(order_frame, columns=cols, show="headings", selectmode="browse")
    for key, label, width in (
        ("date","Дата",105),("no","№",70),("type","Група",230),
        ("subject","Тема",360),("status","Стан",120),("control","Контроль",220),
    ):
        order_tree.heading(key, text=label)
        order_tree.column(key, width=width, anchor="w")
    sy = core.ttk.Scrollbar(order_frame, orient="vertical", command=order_tree.yview)
    sx = core.ttk.Scrollbar(order_frame, orient="horizontal", command=order_tree.xview)
    order_tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
    order_tree.grid(row=0,column=0,sticky="nsew"); sy.grid(row=0,column=1,sticky="ns"); sx.grid(row=1,column=0,sticky="ew")
    order_cache = {}

    def refresh_orders(select_id=None):
        for iid in order_tree.get_children():
            order_tree.delete(iid)
        order_cache.clear()
        con2 = core.db()
        try:
            rows = ops.list_orders(con2)
        finally:
            con2.close()
        for row in rows:
            oid = int(row["id"])
            order_cache[oid] = row
            control = " ".join(str(row[k] or "").strip() for k in ("last_name","first_name","middle_name") if str(row[k] or "").strip())
            order_tree.insert("","end",iid=str(oid),values=(
                ops.display_day(row["order_date"]), row["order_no"],
                ops.ORDER_TYPE_LABELS.get(row["order_type"], row["order_type"]),
                row["subject"], ops.ORDER_STATUS_LABELS.get(row["status"],row["status"]), control or "—",
            ), tags=(row["status"],))
        order_tree.tag_configure(ops.ORDER_APPROVED, foreground="#0B5D1E")
        order_tree.tag_configure(ops.ORDER_CANCELLED, foreground="#777777")
        if select_id and str(select_id) in order_tree.get_children():
            order_tree.selection_set(str(select_id)); order_tree.focus(str(select_id)); order_tree.see(str(select_id))
        refresh_assignments()

    def selected_order():
        sel = order_tree.selection()
        if not sel:
            core.messagebox.showinfo("Накази", "Виберіть наказ.", parent=win)
            return None
        return order_cache.get(int(sel[0]))

    type_labels = list(ops.ORDER_TYPE_LABELS.values())
    type_by_label = {label:key for key,label in ops.ORDER_TYPE_LABELS.items()}

    def new_order():
        dialog = core.tk.Toplevel(win)
        dialog.title("Новий наказ")
        try: core.configure_toplevel(dialog,title="Новий наказ",minsize=(760,520))
        except Exception: pass
        frm = core.ttk.Frame(dialog,padding=14); frm.pack(fill="both",expand=True); frm.columnconfigure(1,weight=1)
        type_var = core.tk.StringVar(value=ops.ORDER_TYPE_LABELS[ops.TYPE_VEHICLE_ASSIGNMENT])
        no_var = core.tk.StringVar(value="")
        date_var = core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
        place_local = core.tk.StringVar(value=place_var.get())
        subject_var = core.tk.StringVar(value=ops.DEFAULT_SUBJECTS[ops.TYPE_VEHICLE_ASSIGNMENT])
        control_var = core.tk.StringVar(value=operations_resp_var.get())
        core.ttk.Label(frm,text="Тип наказу").grid(row=0,column=0,sticky="w",pady=5)
        type_box = core.ttk.Combobox(frm,textvariable=type_var,values=type_labels,state="readonly")
        type_box.grid(row=0,column=1,sticky="ew",pady=5)
        for r,(label,var) in enumerate((("Номер",no_var),("Дата",date_var),("Місце",place_local),("Тема",subject_var),("Контроль",control_var)),start=1):
            core.ttk.Label(frm,text=label).grid(row=r,column=0,sticky="nw",padx=(0,8),pady=5)
            if label=="Контроль":
                widget=core.ttk.Combobox(frm,textvariable=var,values=employee_labels,state="readonly")
            else:
                widget=core.ttk.Entry(frm,textvariable=var)
            widget.grid(row=r,column=1,sticky="ew",pady=5)
        core.ttk.Label(frm,text="Підстава / вступ").grid(row=6,column=0,sticky="nw",pady=5)
        preamble = core.tk.Text(frm,height=4,wrap="word"); preamble.grid(row=6,column=1,sticky="nsew",pady=5)
        preamble.insert("1.0",ops.DEFAULT_PREAMBLES[ops.TYPE_VEHICLE_ASSIGNMENT])
        core.ttk.Label(frm,text="Текст пунктів (для довільного наказу)").grid(row=7,column=0,sticky="nw",pady=5)
        body_text = core.tk.Text(frm,height=7,wrap="word"); body_text.grid(row=7,column=1,sticky="nsew",pady=5)
        frm.rowconfigure(7,weight=1)

        def sync_type(_event=None):
            key=type_by_label.get(type_var.get(),ops.TYPE_GENERIC)
            subject_var.set(ops.DEFAULT_SUBJECTS.get(key,""))
            preamble.delete("1.0","end"); preamble.insert("1.0",ops.DEFAULT_PREAMBLES.get(key,""))
        type_box.bind("<<ComboboxSelected>>",sync_type)

        def save_new():
            con3=core.db()
            try:
                oid=ops.create_order(
                    con3, order_type=type_by_label.get(type_var.get(),ops.TYPE_GENERIC),
                    order_no=no_var.get(), order_date=date_var.get(), place=place_local.get(),
                    subject=subject_var.get(), preamble=preamble.get("1.0","end-1c"),
                    body_text=body_text.get("1.0","end-1c"), control_employee_id=emp_by_label.get(control_var.get()),
                )
                con3.commit()
            except Exception as exc:
                con3.rollback(); core.messagebox.showerror("Наказ",str(exc),parent=dialog); return
            finally: con3.close()
            dialog.destroy(); refresh_orders(oid)
            if type_by_label.get(type_var.get())==ops.TYPE_VEHICLE_ASSIGNMENT:
                book.select(assignments_tab)
        buttons=core.ttk.Frame(frm); buttons.grid(row=8,column=0,columnspan=2,sticky="ew",pady=(10,0))
        core.ttk.Button(buttons,text="Скасувати",command=dialog.destroy).pack(side="right")
        core.ttk.Button(buttons,text="Створити",style="Accent.TButton",command=save_new).pack(side="right",padx=(0,6))
        dialog.transient(win)

    def approve_selected():
        row=selected_order()
        if row is None: return
        if row["status"]==ops.ORDER_APPROVED:
            core.messagebox.showinfo("Накази","Наказ уже затверджено.",parent=win); return
        if not core.messagebox.askyesno("Затвердити наказ?","Після затвердження закріплення почне діяти як структурований факт Taxo.",parent=win): return
        con2=core.db()
        try:
            ops.approve_order(con2,row["id"]); con2.commit()
        except Exception as exc:
            con2.rollback(); core.messagebox.showerror("Накази",str(exc),parent=win); return
        finally: con2.close()
        refresh_orders(row["id"])

    def export_selected():
        row=selected_order()
        if row is None: return
        con2=core.db()
        try:
            assignments=ops.order_assignments(con2,row["id"])
            company_row=con2.execute("SELECT * FROM company WHERE id=1").fetchone()
            company={key:company_row[key] for key in company_row.keys()} if company_row else {}
            control=ops.employee_name(con2,row["control_employee_id"])
        finally: con2.close()
        out=core.OUTPUT_DIR / ("Наказ_%s_%s.pdf" % (str(row["order_no"]).replace("/","-"),row["order_date"]))
        font=next((p for p in core.report_font_candidates() if core.Path(p).exists()),None)
        try:
            ops.export_order_pdf(out,row,assignments,company,control,font_path=font)
        except Exception as exc:
            core.messagebox.showerror("Наказ PDF",str(exc),parent=win); return
        core.messagebox.showinfo("Наказ PDF","Сформовано:\n%s" % out,parent=win)
        try: core.open_external(out)
        except Exception: pass

    core.ttk.Button(order_top,text="Новий наказ",style="Accent.TButton",command=new_order).pack(side="left")
    core.ttk.Button(order_top,text="Затвердити",command=approve_selected).pack(side="left",padx=6)
    core.ttk.Button(order_top,text="Сформувати PDF",command=export_selected).pack(side="left",padx=6)

    # ------------------------------------------------------------------
    # Vehicle/driver assignment tab
    # ------------------------------------------------------------------
    at = core.ttk.Frame(assignments_tab,padding=(10,10,10,4)); at.pack(fill="x")
    selected_order_var=core.tk.StringVar(value="Виберіть наказ про закріплення у вкладці «Накази».")
    core.ttk.Label(at,textvariable=selected_order_var,style="Subtitle.TLabel").pack(side="left")
    aframe=core.ttk.Frame(assignments_tab); aframe.pack(fill="both",expand=True,padx=10,pady=(0,10)); aframe.rowconfigure(0,weight=1); aframe.columnconfigure(0,weight=1)
    acols=("seq","vehicle","plate","driver","from","until")
    atree=core.ttk.Treeview(aframe,columns=acols,show="headings",selectmode="browse")
    for key,label,width in (("seq","№",50),("vehicle","ТЗ",260),("plate","Держ. номер",120),("driver","Водій",300),("from","З",100),("until","До",100)):
        atree.heading(key,text=label); atree.column(key,width=width,anchor="w")
    asy=core.ttk.Scrollbar(aframe,orient="vertical",command=atree.yview); asx=core.ttk.Scrollbar(aframe,orient="horizontal",command=atree.xview)
    atree.configure(yscrollcommand=asy.set,xscrollcommand=asx.set); atree.grid(row=0,column=0,sticky="nsew"); asy.grid(row=0,column=1,sticky="ns"); asx.grid(row=1,column=0,sticky="ew")
    assignment_cache={}

    def current_assignment_order():
        row=selected_order()
        if row is None or row["order_type"]!=ops.TYPE_VEHICLE_ASSIGNMENT:
            return None
        return row

    def refresh_assignments():
        for iid in atree.get_children(): atree.delete(iid)
        assignment_cache.clear()
        row=current_assignment_order()
        if row is None:
            selected_order_var.set("Виберіть наказ про закріплення у вкладці «Накази».")
            return
        selected_order_var.set("Наказ №%s від %s — %s" % (row["order_no"],ops.display_day(row["order_date"]),ops.ORDER_STATUS_LABELS.get(row["status"],row["status"])))
        con2=core.db()
        try: items=ops.order_assignments(con2,row["id"])
        finally: con2.close()
        for item in items:
            aid=int(item["id"]); assignment_cache[aid]=item
            driver=" ".join(str(item[k] or "").strip() for k in ("last_name","first_name","middle_name") if str(item[k] or "").strip())
            atree.insert("","end",iid=str(aid),values=(item["sequence_no"],item["make_model"] or item["vehicle_name"],item["plate"],driver,ops.display_day(item["valid_from"]),ops.display_day(item["valid_until"])))

    order_tree.bind("<<TreeviewSelect>>",lambda _e:refresh_assignments(),add="+")

    def add_assignment():
        order=current_assignment_order()
        if order is None:
            core.messagebox.showinfo("Закріплення","Спочатку виберіть наказ типу «Закріплення транспортних засобів за водіями».",parent=win); return
        if order["status"]!=ops.ORDER_DRAFT:
            core.messagebox.showinfo("Закріплення","Змінювати склад затвердженого наказу не можна. Створіть новий наказ/зміну.",parent=win); return
        con2=core.db()
        try:
            vehicles=ops.list_vehicle_choices(con2,active_only=False); emps=ops.list_employee_choices(con2,active_only=True)
        finally: con2.close()
        dlg=core.tk.Toplevel(win); dlg.title("Додати закріплення")
        frm=core.ttk.Frame(dlg,padding=14); frm.pack(fill="both",expand=True); frm.columnconfigure(1,weight=1)
        vlabels=[x["label"] for x in vehicles]; elabels=[x["label"] for x in emps]
        vmap={x["label"]:x["id"] for x in vehicles}; emap={x["label"]:x["id"] for x in emps}
        vv=core.tk.StringVar(); ev=core.tk.StringVar(); fv=core.tk.StringVar(value=ops.display_day(order["order_date"])); uv=core.tk.StringVar(value="")
        for r,(label,var,values) in enumerate((("Транспортний засіб",vv,vlabels),("Водій",ev,elabels),("Діє з",fv,None),("Діє до (необов'язково)",uv,None))):
            core.ttk.Label(frm,text=label).grid(row=r,column=0,sticky="w",padx=(0,8),pady=6)
            widget=core.ttk.Combobox(frm,textvariable=var,values=values,state="readonly") if values is not None else core.ttk.Entry(frm,textvariable=var)
            widget.grid(row=r,column=1,sticky="ew",pady=6)
        def save_assignment():
            if vv.get() not in vmap or ev.get() not in emap:
                core.messagebox.showerror("Закріплення","Виберіть ТЗ і водія.",parent=dlg); return
            con3=core.db()
            try:
                ops.add_vehicle_assignment(con3,order["id"],vmap[vv.get()],emap[ev.get()],valid_from=fv.get(),valid_until=uv.get()); con3.commit()
            except Exception as exc:
                con3.rollback(); core.messagebox.showerror("Закріплення",str(exc),parent=dlg); return
            finally: con3.close()
            dlg.destroy(); refresh_assignments()
        bar=core.ttk.Frame(frm); bar.grid(row=4,column=0,columnspan=2,sticky="ew",pady=(10,0))
        core.ttk.Button(bar,text="Скасувати",command=dlg.destroy).pack(side="right")
        core.ttk.Button(bar,text="Додати",style="Accent.TButton",command=save_assignment).pack(side="right",padx=(0,6))
        dlg.transient(win)

    def remove_assignment():
        order=current_assignment_order()
        if order is None or order["status"]!=ops.ORDER_DRAFT:
            return
        sel=atree.selection()
        if not sel: return
        con2=core.db()
        try: ops.delete_vehicle_assignment(con2,int(sel[0])); con2.commit()
        finally: con2.close()
        refresh_assignments()

    abar=core.ttk.Frame(assignments_tab,padding=(10,0,10,10)); abar.pack(fill="x")
    core.ttk.Button(abar,text="Додати ТЗ / водія",style="Accent.TButton",command=add_assignment).pack(side="left")
    core.ttk.Button(abar,text="Прибрати",command=remove_assignment).pack(side="left",padx=6)

    # ------------------------------------------------------------------
    # Future maintenance container
    # ------------------------------------------------------------------
    mbody=core.ttk.Frame(maintenance_tab,padding=18); mbody.pack(fill="both",expand=True)
    core.ttk.Label(mbody,text="ТО / ремонти",style="Title.TLabel").pack(anchor="w")
    core.ttk.Label(
        mbody,
        text=(
            "Розділ зарезервовано у контурі «Експлуатація». Після додавання ваших форм по ТО, ремонтам та іншим експлуатаційним документам "
            "вони будуть зведені сюди без створення окремих розрізнених вікон."
        ),
        wraplength=900,justify="left",
    ).pack(anchor="w",pady=(5,0))

    refresh_orders()
    return win
