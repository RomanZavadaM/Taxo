# -*- coding: utf-8 -*-
"""People and vehicles associated with an operations order."""


def install_order_entities_tab(core, ops, win, entities_tab, order_tree,
                               selected_order, require_mutable_order, open_assignments=None,
                               refresh_open_order_previews=None):
    # Structured employees / vehicles for non-assignment orders.
    ehead=core.ttk.Frame(entities_tab,padding=(10,10,10,4)); ehead.pack(fill="x")
    selected_entity_order_var=core.tk.StringVar(value="Виберіть наказ.")
    identity_label=core.ttk.Label(ehead,textvariable=selected_entity_order_var,style="Subtitle.TLabel",justify="left")
    identity_label.pack(fill="x",anchor="w")
    hint=core.ttk.Label(
        ehead,
        text=("Тут зберігаються конкретні працівники та ТЗ, яких стосується наказ. "
              "Taxo фіксує знімок реквізитів на момент додавання, тому подальша зміна картки "
              "не переписує історичний перелік. Для наказу про закріплення використовуйте окрему вкладку."),
        style="Muted.TLabel",wraplength=1080,justify="left",
    )
    hint.pack(fill="x",anchor="w",pady=(3,6))
    def adjust_wrap(event):
        for label in (identity_label,hint):
            label.configure(wraplength=max(160,event.width-24))
    ehead.bind("<Configure>",adjust_wrap,add="+")
    assignment_button=None
    if open_assignments is not None:
        assignment_button=core.ttk.Button(ehead,text="Перейти до закріплення водіїв",command=open_assignments)

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
    current_order_id=None

    def current_entity_order():
        return selected_order(quiet=True)

    def refresh_live_preview(order_id):
        if refresh_open_order_previews is None:
            return 0
        try:
            return int(refresh_open_order_previews(order_id) or 0)
        except Exception:
            # Preview refresh must never roll back an already committed entity
            # change. The next manual preview refresh still reads current DB data.
            return 0

    def refresh_order_entities():
        nonlocal current_order_id
        previous=tuple(etree.selection())
        for iid in etree.get_children(): etree.delete(iid)
        entity_cache.clear()
        order=current_entity_order()
        same_order=order is not None and current_order_id==order["id"]
        current_order_id=order["id"] if order is not None else None
        if assignment_button is not None:
            assignment_button.pack_forget()
        if order is None:
            selected_entity_order_var.set("Виберіть наказ.")
            return
        state_label="Діє в Taxo" if order["status"]==ops.ORDER_APPROVED else ops.ORDER_STATUS_LABELS.get(order["status"],order["status"])
        selected_entity_order_var.set(
            "Наказ №%s від %s — %s\n%s" % (order["order_no"],ops.display_day(order["order_date"]),state_label,order["subject"] or "Без теми")
        )
        if str(order["order_type"])==ops.TYPE_VEHICLE_ASSIGNMENT:
            selected_entity_order_var.set(
                selected_entity_order_var.get()+"\nПари водій–ТЗ ведуться у вкладці «Закріплення водіїв»."
            )
            if assignment_button is not None:
                assignment_button.pack(anchor="w",pady=(0,6))
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

        if same_order:
            remaining=tuple(iid for iid in previous if etree.exists(iid))
            if remaining:
                etree.selection_set(remaining)
                etree.see(remaining[0])

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
        selected_ids=set()
        selected_count=core.tk.StringVar(value="Вибрано: 0")
        count_bar=core.ttk.Frame(frm)
        count_bar.grid(row=5,column=0,sticky="ew",pady=(5,0))
        core.ttk.Label(count_bar,textvariable=selected_count).pack(side="left")

        def capture_selection():
            selected_ids.difference_update(row["id"] for row in visible)
            selected_ids.update(visible[int(i)]["id"] for i in lb.curselection() if int(i)<len(visible))
            selected_count.set("Вибрано: %d (із різних результатів пошуку)" % len(selected_ids))

        def clear_selection():
            selected_ids.clear()
            lb.selection_clear(0,"end")
            selected_count.set("Вибрано: 0")

        core.ttk.Button(count_bar,text="Очистити весь вибір",command=clear_selection).pack(side="right")
        lb.bind("<<ListboxSelect>>",lambda _e:capture_selection(),add="+")

        def refill(*_args):
            capture_selection()
            query=str(search_var.get() or "").strip().lower()
            lb.delete(0,"end"); visible.clear()
            for choice in choices:
                hay=str(choice.get("search_text") or choice.get("label") or "").lower()
                if query and query not in hay:
                    continue
                visible.append(choice); lb.insert("end",choice["label"])
                if choice["id"] in selected_ids:
                    lb.selection_set(len(visible)-1)
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
            capture_selection()
            selected=[row for row in choices if row["id"] in selected_ids]
            if not selected:
                core.messagebox.showerror("Учасники / ТЗ","Виберіть хоча б один запис.",parent=dlg); return
            active=current_entity_order()
            if active is None or active["id"]!=order["id"] or not require_mutable_order(active,"Учасники / ТЗ"):
                core.messagebox.showinfo("Учасники / ТЗ","Активний наказ змінився. Відкрийте вибір повторно.",parent=dlg)
                return
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
            dlg.destroy(); refresh_order_entities(); refresh_live_preview(order["id"])
            core.messagebox.showinfo(
                "Учасники / ТЗ",
                "До наказу №%s додано: %d. Уже були з тією самою роллю: %d." % (order["order_no"],len(created),len(selected)-len(created)),
                parent=win,
            )

        core.ttk.Button(bar,text="Скасувати",command=dlg.destroy).pack(side="right")
        core.ttk.Button(bar,text="Додати вибрані",style="Accent.TButton",command=save_entities).pack(side="right",padx=(0,6))
        dlg.transient(win); search_entry.focus_set()
        dlg.grab_set()

    def edit_order_entity():
        order=current_entity_order()
        selected=tuple(etree.selection())
        if order is None or len(selected)!=1:
            core.messagebox.showinfo(
                "Учасники / ТЗ",
                "Виберіть один рядок працівника або ТЗ для редагування.",
                parent=win,
            )
            return
        if not require_mutable_order(order, "Редагування учасника наказу"):
            return
        link_id=int(selected[0])
        item=entity_cache.get(link_id)
        if item is None:
            refresh_order_entities()
            core.messagebox.showinfo(
                "Учасники / ТЗ",
                "Список оновлено. Виберіть потрібний рядок ще раз.",
                parent=win,
            )
            return

        dlg=core.tk.Toplevel(win)
        dlg.title("Змінити роль / примітку")
        try:
            core.configure_toplevel(dlg,title=dlg.title(),minsize=(520,240))
        except Exception:
            dlg.geometry("620x280")
        form=core.ttk.Frame(dlg,padding=14)
        form.pack(fill="both",expand=True)
        form.columnconfigure(1,weight=1)
        view=ops.order_entity_view(item)
        core.ttk.Label(
            form,
            text="%s: %s" % (view["type_label"],view["display"]),
            wraplength=560,justify="left",
        ).grid(row=0,column=0,columnspan=2,sticky="w",pady=(0,12))
        role_var=core.tk.StringVar(value=str(item["role"] or ""))
        note_var=core.tk.StringVar(value=str(item["note"] or ""))
        core.ttk.Label(form,text="Роль / призначення").grid(row=1,column=0,sticky="w",padx=(0,8),pady=5)
        role_entry=core.ttk.Entry(form,textvariable=role_var)
        role_entry.grid(row=1,column=1,sticky="ew",pady=5)
        core.ttk.Label(form,text="Примітка").grid(row=2,column=0,sticky="w",padx=(0,8),pady=5)
        core.ttk.Entry(form,textvariable=note_var).grid(row=2,column=1,sticky="ew",pady=5)
        bar=core.ttk.Frame(form)
        bar.grid(row=3,column=0,columnspan=2,sticky="e",pady=(16,0))

        def save_edit():
            con=core.db()
            try:
                changed=ops.update_order_entity_fields(
                    con,link_id,role=role_var.get(),note=note_var.get(),
                )
                con.commit()
            except Exception as exc:
                con.rollback()
                core.messagebox.showerror("Учасники / ТЗ",str(exc),parent=dlg)
                return
            finally:
                con.close()
            dlg.destroy()
            refresh_order_entities()
            refresh_live_preview(order["id"])
            if etree.exists(str(link_id)):
                etree.selection_set(str(link_id))
                etree.see(str(link_id))
            if changed:
                core.messagebox.showinfo(
                    "Учасники / ТЗ",
                    "Зміни збережено у наказі. Історичні реквізити не переписано.",
                    parent=win,
                )

        core.ttk.Button(bar,text="Скасувати",command=dlg.destroy).pack(side="right")
        core.ttk.Button(
            bar,text="Зберегти зміни",style="Accent.TButton",
            command=save_edit,
        ).pack(side="right",padx=(0,6))
        dlg.transient(win)
        role_entry.focus_set()

    def remove_order_entities():
        order=current_entity_order(); selected=tuple(etree.selection())
        if order is None or not selected:
            core.messagebox.showinfo("Учасники / ТЗ","Виберіть один або кілька рядків.",parent=win); return
        if not require_mutable_order(order,"Учасники / ТЗ"):
            return
        if not core.messagebox.askyesno(
            "Прибрати з наказу?",
            "Прибрати вибрані записи зі структурованого переліку наказу?",
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
        refresh_live_preview(order["id"])

    ebar=core.ttk.Frame(entities_tab,padding=(10,0,10,10))
    ebar.pack(fill="x")
    # Two compact rows keep every action visible on narrow/high-DPI screens.
    for col in range(3):
        ebar.columnconfigure(col,weight=1)
    core.ttk.Button(
        ebar,text="Додати працівників…",style="Accent.TButton",
        command=lambda:entity_picker(ops.ORDER_ENTITY_EMPLOYEE),
    ).grid(row=0,column=0,sticky="ew",padx=3,pady=3)
    core.ttk.Button(
        ebar,text="Додати ТЗ…",command=lambda:entity_picker(ops.ORDER_ENTITY_VEHICLE),
    ).grid(row=0,column=1,sticky="ew",padx=3,pady=3)
    core.ttk.Button(
        ebar,text="Прибрати вибрані",command=remove_order_entities,
    ).grid(row=0,column=2,sticky="ew",padx=3,pady=3)
    core.ttk.Button(
        ebar,text="Змінити роль / примітку…",command=edit_order_entity,
    ).grid(row=1,column=0,columnspan=2,sticky="ew",padx=3,pady=3)
    core.ttk.Button(
        ebar,text="Оновити",command=refresh_order_entities,
    ).grid(row=1,column=2,sticky="ew",padx=3,pady=3)

    return refresh_order_entities

