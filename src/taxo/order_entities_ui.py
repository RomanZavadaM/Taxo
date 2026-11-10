# -*- coding: utf-8 -*-
"""People and vehicles associated with an operations order."""


def install_order_entities_tab(core, ops, win, entities_tab, order_tree,
                               selected_order, require_mutable_order):
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

    return refresh_order_entities

