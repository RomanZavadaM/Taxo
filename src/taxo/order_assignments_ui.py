# -*- coding: utf-8 -*-
"""Driver and vehicle assignment management for operations orders."""


def install_assignment_tab(core, ops, win, assignments_tab, order_tree,
                           create_assignment_order, selected_order,
                           require_mutable_order, refresh_open_order_previews):
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
        con2=core.db()
        try: items=ops.order_assignments(con2,row["id"])
        finally: con2.close()
        selected_order_var.set(
            "Наказ №%s від %s — %s — закріплень: %d"
            % (row["order_no"],ops.display_day(row["order_date"]),state_label,len(items))
        )
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
                target_pair=(int(vmap[vv.get()]),int(emap[ev.get()]))
                if existing:
                    ops.update_vehicle_assignment(con3,existing["id"],vehicle_id=target_pair[0],employee_id=target_pair[1],valid_from=fv.get(),valid_until=uv.get(),history_note="Редагування через інтерфейс")
                else:
                    ops.add_vehicle_assignment(con3,order["id"],target_pair[0],target_pair[1],valid_from=fv.get(),valid_until=uv.get())
                ops.verify_vehicle_assignment_pairs(con3,order["id"],[target_pair])
                con3.commit()
            except Exception as exc: con3.rollback(); core.messagebox.showerror("Закріплення",str(exc),parent=dlg); return
            finally: con3.close()
            dlg.destroy(); refresh_assignments(); refresh_open_order_previews(order["id"])
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
                ops.verify_vehicle_assignment_pairs(con3,order["id"],pairs)
                con3.commit()
            except Exception as exc:
                con3.rollback(); core.messagebox.showerror("Закріплення",str(exc),parent=dlg); return
            finally: con3.close()
            dlg.destroy(); refresh_assignments(); refresh_open_order_previews(order["id"])
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
        refresh_assignments(); refresh_open_order_previews(order["id"])
    abar=core.ttk.Frame(assignments_tab,padding=(10,0,10,10)); abar.pack(fill="x")
    core.ttk.Button(abar,text="Додати багато…",style="Accent.TButton",command=add_assignments_bulk).pack(side="left")
    core.ttk.Button(abar,text="Додати одну пару",command=add_assignment).pack(side="left",padx=6)
    core.ttk.Button(abar,text="Редагувати",command=edit_assignment).pack(side="left",padx=6)
    core.ttk.Button(abar,text="Прибрати",command=remove_assignment).pack(side="left",padx=6)

    return refresh_assignments, add_assignments_bulk

