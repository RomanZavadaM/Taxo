# -*- coding: utf-8 -*-
"""Create and edit operations orders, including initial driver assignments."""
from datetime import date

import order_editor_persistence


def open_order_editor(core, ops, win, existing, force_type, personnel_order_next_var,
                      work_order_next_var, place_var, emp_by_id, operations_resp_var,
                      type_labels, type_by_label, employee_labels, emp_by_label,
                      book, assignments_tab, orders_tab, refresh_assignments,
                      add_assignments_bulk, refresh_orders, refresh_open_order_previews,
                      order_cache, preview_order):
    dialog=core.tk.Toplevel(win); dialog.title("Редагувати наказ" if existing else "Створити наказ")
    try:
        core.fit_window_to_screen(dialog, 900, 760, 760, 560)
        core.configure_toplevel(dialog,title=dialog.title(),minsize=(760,560))
    except Exception: pass
    frm=core.ttk.Frame(dialog,padding=14); frm.pack(fill="both",expand=True); frm.columnconfigure(1,weight=1); frm.rowconfigure(10,weight=1)
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

    preset_var=core.tk.StringVar(value="")
    preset_frame=core.ttk.Frame(frm)
    preset_frame.grid(row=7,column=0,columnspan=2,sticky="ew",pady=(3,2))
    preset_frame.columnconfigure(1,weight=1)
    core.ttk.Label(preset_frame,text="Типова заготовка").grid(row=0,column=0,sticky="w",padx=(0,8))
    preset_box=core.ttk.Combobox(preset_frame,textvariable=preset_var,values=(),state="readonly")
    preset_box.grid(row=0,column=1,sticky="ew")
    core.ttk.Label(
        preset_frame,
        text="Заготовка змінює тему, вступ і пункти лише після кнопки «Вставити заготовку».",
        style="Muted.TLabel",wraplength=760,justify="left",
    ).grid(row=1,column=0,columnspan=2,sticky="w",pady=(2,0))

    core.ttk.Label(frm,text="Підстава / вступ").grid(row=9,column=0,sticky="nw",pady=5)
    preamble=core.tk.Text(frm,height=3,wrap="word"); preamble.grid(row=9,column=1,sticky="nsew",pady=5)
    preamble.insert("1.0",str(existing["preamble"] if existing else ops.DEFAULT_PREAMBLES.get(initial_type,"")))
    core.ttk.Label(frm,text="Текст пунктів").grid(row=10,column=0,sticky="nw",pady=5)
    body_text=core.tk.Text(frm,height=5,wrap="word"); body_text.grid(row=10,column=1,sticky="nsew",pady=5)
    body_text.insert("1.0",str(existing["body_text"] if existing else ops.DEFAULT_BODY_TEMPLATES.get(initial_type,"")))

    initial_vehicles=[]
    initial_drivers=[]
    initial_vehicle_list=None
    initial_driver_list=None
    assignment_box=None
    assignment_count_var=core.tk.StringVar(value="")
    staged_initial_pairs=[]
    staged_pair_tree=None
    if existing is None:
        con_choices=core.db()
        try:
            initial_vehicles=ops.list_vehicle_choices(con_choices,active_only=True)
            initial_drivers=ops.list_driver_choices(con_choices,active_only=True)
        finally:
            con_choices.close()
        assignment_box=core.ttk.LabelFrame(frm,text="Закріплення в цьому наказі",padding=8)
        assignment_box.grid(row=8,column=0,columnspan=2,sticky="ew",pady=(8,2))
        assignment_box.columnconfigure(0,weight=1); assignment_box.columnconfigure(1,weight=1)

        left=core.ttk.Frame(assignment_box); left.grid(row=0,column=0,sticky="nsew",padx=(0,4))
        right=core.ttk.Frame(assignment_box); right.grid(row=0,column=1,sticky="nsew",padx=(4,0))
        core.ttk.Label(left,text="Транспортний засіб").pack(anchor="w")
        initial_vehicle_list=core.tk.Listbox(left,selectmode="extended",exportselection=False,height=5)
        initial_vehicle_list.pack(fill="both",expand=True,pady=(3,0))
        for row in initial_vehicles: initial_vehicle_list.insert("end",row["label"])
        core.ttk.Label(right,text="Водій із бази водіїв").pack(anchor="w")
        initial_driver_list=core.tk.Listbox(right,selectmode="extended",exportselection=False,height=5)
        initial_driver_list.pack(fill="both",expand=True,pady=(3,0))
        for row in initial_drivers: initial_driver_list.insert("end",row["label"])
        # Stable live-test hooks for the critical bulk assignment controls.
        # These are widget references only; no business logic depends on them.
        dialog._taxo_assignment_box = assignment_box
        dialog._taxo_assignment_vehicle_list = initial_vehicle_list
        dialog._taxo_assignment_driver_list = initial_driver_list

        staged_pair_tree=core.ttk.Treeview(
            assignment_box,columns=("vehicle","driver"),show="headings",height=3,selectmode="none"
        )
        staged_pair_tree.heading("vehicle",text="Підготовлений ТЗ")
        staged_pair_tree.heading("driver",text="Підготовлений водій")
        staged_pair_tree.column("vehicle",width=350,anchor="w")
        staged_pair_tree.column("driver",width=350,anchor="w")
        staged_pair_tree.grid(row=2,column=0,columnspan=2,sticky="ew",pady=(4,2))
        dialog._taxo_staged_assignment_tree = staged_pair_tree
        dialog._taxo_staged_assignment_pairs = staged_initial_pairs

        def render_staged_pairs():
            for iid in staged_pair_tree.get_children():
                staged_pair_tree.delete(iid)
            vehicle_by_id={int(row["id"]):row for row in initial_vehicles}
            driver_by_id={int(row["id"]):row for row in initial_drivers}
            for seq,(vehicle_id,driver_id) in enumerate(staged_initial_pairs,1):
                vehicle=vehicle_by_id.get(int(vehicle_id),{})
                driver=driver_by_id.get(int(driver_id),{})
                staged_pair_tree.insert(
                    "","end",iid=str(seq),values=(
                        vehicle.get("label") or ("ТЗ #%s" % vehicle_id),
                        driver.get("label") or ("Працівник #%s" % driver_id),
                    )
                )

        def stage_current_selection(_event=None, *, show_error=False):
            vehicle_ids=[initial_vehicles[int(index)]["id"] for index in initial_vehicle_list.curselection()]
            driver_ids=[initial_drivers[int(index)]["id"] for index in initial_driver_list.curselection()]
            if not vehicle_ids and not driver_ids:
                assignment_count_var.set(
                    "Підготовлено пар: %d. Поточне виділення порожнє." % len(staged_initial_pairs)
                )
                return list(staged_initial_pairs)
            try:
                pairs=ops.build_assignment_pairs(vehicle_ids,driver_ids)
            except Exception as exc:
                assignment_count_var.set(
                    "Підготовлено пар: %d. Поточний вибір потребує уточнення." % len(staged_initial_pairs)
                )
                if show_error:
                    core.messagebox.showerror("Наказ про закріплення",str(exc),parent=dialog)
                return None
            staged_initial_pairs[:]=[(int(vehicle_id),int(driver_id)) for vehicle_id,driver_id in pairs]
            render_staged_pairs()
            assignment_count_var.set(
                "Вибрано: ТЗ — %d; водіїв — %d. Підготовлено пар: %d."
                % (len(vehicle_ids),len(driver_ids),len(staged_initial_pairs))
            )
            return list(staged_initial_pairs)

        def clear_staged_pairs():
            staged_initial_pairs.clear()
            try:
                initial_vehicle_list.selection_clear(0,"end")
                initial_driver_list.selection_clear(0,"end")
            except Exception:
                pass
            render_staged_pairs()
            assignment_count_var.set("Підготовлено пар: 0.")

        initial_vehicle_list.bind("<<ListboxSelect>>",stage_current_selection)
        initial_driver_list.bind("<<ListboxSelect>>",stage_current_selection)
        core.ttk.Label(
            assignment_box,textvariable=assignment_count_var,style="Subtitle.TLabel"
        ).grid(row=1,column=0,columnspan=2,sticky="w",pady=(6,2))
        controls=core.ttk.Frame(assignment_box)
        controls.grid(row=3,column=0,columnspan=2,sticky="ew",pady=(2,0))
        core.ttk.Button(
            controls,text="Зафіксувати поточний вибір",
            command=lambda:stage_current_selection(show_error=True),
        ).pack(side="left")
        core.ttk.Button(
            controls,text="Очистити підготовлені пари",command=clear_staged_pairs
        ).pack(side="left",padx=6)
        assignment_count_var.set("Підготовлено пар: 0.")
        core.ttk.Label(
            assignment_box,
            text=("Пари, які реально підуть у наказ, показані в таблиці вище. "
                  "Вибір зберігається окремо від підсвічування списків, тому не зникає при зміні фокусу. "
                  "Правило: 1 ТЗ + кілька водіїв або однакова кількість ТЗ і водіїв."),
            style="Muted.TLabel",wraplength=700,justify="left",
        ).grid(row=4,column=0,columnspan=2,sticky="w",pady=(4,0))
    elif initial_type==ops.TYPE_VEHICLE_ASSIGNMENT:
        con_existing=core.db()
        try:
            existing_assignments=ops.order_assignments(con_existing,existing["id"])
        finally:
            con_existing.close()
        assignment_box=core.ttk.LabelFrame(frm,text="Водії і ТЗ цього наказу",padding=8)
        assignment_box.grid(row=7,column=0,columnspan=2,sticky="ew",pady=(8,2))
        assignment_box.columnconfigure(0,weight=1)
        core.ttk.Label(
            assignment_box,
            text="Поточні закріплення: %d" % len(existing_assignments),
            style="Subtitle.TLabel",
        ).grid(row=0,column=0,sticky="w",pady=(0,4))
        existing_tree=core.ttk.Treeview(
            assignment_box,columns=("vehicle","plate","driver"),show="headings",
            height=max(1,min(4,len(existing_assignments))),selectmode="browse",
        )
        for key,label,width in (
            ("vehicle","Транспортний засіб",300),
            ("plate","Держ. номер",130),
            ("driver","Водій",320),
        ):
            existing_tree.heading(key,text=label)
            existing_tree.column(key,width=width,anchor="w")
        existing_tree.grid(row=1,column=0,sticky="ew",pady=(0,6))
        for item in existing_assignments:
            driver=" ".join(
                str(item[k] or "").strip()
                for k in ("last_name","first_name","middle_name")
                if str(item[k] or "").strip()
            )
            existing_tree.insert(
                "","end",values=(
                    item["make_model"] or item["vehicle_name"],
                    item["plate"] or "—",
                    driver or "—",
                )
            )
        existing_buttons=core.ttk.Frame(assignment_box)
        existing_buttons.grid(row=2,column=0,sticky="ew")
        def open_existing_assignment_manager(open_bulk=False):
            dialog.destroy()
            book.select(assignments_tab)
            refresh_assignments()
            if open_bulk:
                try:
                    win.after_idle(add_assignments_bulk)
                except Exception:
                    add_assignments_bulk()
        bulk_button=core.ttk.Button(
            existing_buttons,text="Додати багато…",style="Accent.TButton",
            command=lambda:open_existing_assignment_manager(True),
        )
        bulk_button.pack(side="left")
        manage_button=core.ttk.Button(
            existing_buttons,text="Керувати закріпленнями",
            command=lambda:open_existing_assignment_manager(False),
        )
        manage_button.pack(side="left",padx=6)
        core.ttk.Label(
            assignment_box,
            text=("Закріплення є частиною цього наказу. Тут видно поточний перелік; "
                  "для додавання кількох водіїв/ТЗ натисніть «Додати багато…», "
                  "для редагування або видалення окремих пар — «Керувати закріпленнями»."),
            style="Muted.TLabel",wraplength=700,justify="left",
        ).grid(row=3,column=0,sticky="w",pady=(6,0))
        dialog._taxo_existing_assignment_tree=existing_tree
        dialog._taxo_existing_assignment_bulk_button=bulk_button
        dialog._taxo_existing_assignment_manage_button=manage_button

    def show_assignment_box(order_type):
        if assignment_box is None:
            return
        if order_type==ops.TYPE_VEHICLE_ASSIGNMENT:
            assignment_box.grid()
        else:
            assignment_box.grid_remove()

    show_assignment_box(initial_type)

    preset_rows=[]
    def refresh_order_presets(order_type, select_first=True):
        preset_rows[:] = list(getattr(ops,"ORDER_TEXT_PRESETS",{}).get(order_type,()))
        titles=[str(row.get("title") or row.get("id") or "Заготовка") for row in preset_rows]
        preset_box.configure(values=titles)
        if titles:
            preset_frame.grid()
            if select_first or preset_var.get() not in titles:
                preset_var.set(titles[0])
        else:
            preset_var.set("")
            preset_frame.grid_remove()

    refresh_order_presets(initial_type, select_first=True)
    dialog._taxo_order_preset_box=preset_box
    dialog._taxo_order_preset_var=preset_var

    if existing and int(existing["paper_original_signed"] or 0):
        core.ttk.Label(frm,text="Увага: паперовий оригінал позначено як підписаний. Після змін звірте його і, за потреби, передрукуйте.",
                       style="Muted.TLabel",wraplength=620,justify="left").grid(row=11,column=0,columnspan=2,sticky="w",pady=(4,2))
    def sync_type(_event=None):
        if existing: return
        key=type_by_label.get(type_var.get(),ops.TYPE_GENERIC)
        subject_var.set(ops.DEFAULT_SUBJECTS.get(key,""))
        preamble.delete("1.0","end"); preamble.insert("1.0",ops.DEFAULT_PREAMBLES.get(key,""))
        body_text.delete("1.0","end"); body_text.insert("1.0",ops.DEFAULT_BODY_TEMPLATES.get(key,""))
        refresh_order_presets(key, select_first=True)
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
        selected_title=preset_var.get()
        preset=next(
            (row for row in preset_rows if str(row.get("title") or row.get("id") or "Заготовка")==selected_title),
            None,
        )
        if preset is None:
            template=ops.DEFAULT_BODY_TEMPLATES.get(key,"")
            if not template:
                core.messagebox.showinfo("Типова заготовка","Для цього типу наказу заготовку не задано.",parent=dialog); return
            preset={
                "subject":ops.DEFAULT_SUBJECTS.get(key,""),
                "preamble":ops.DEFAULT_PREAMBLES.get(key,""),
                "body":template,
            }
        new_subject=str(preset.get("subject") or subject_var.get())
        new_preamble=str(preset.get("preamble") or "")
        new_body=str(preset.get("body") or "")
        current_body=body_text.get("1.0","end-1c").strip()
        current_preamble=preamble.get("1.0","end-1c").strip()
        changed=(
            (current_body and current_body != new_body.strip())
            or (current_preamble and current_preamble != new_preamble.strip())
            or (subject_var.get().strip() and subject_var.get().strip() != new_subject.strip())
        )
        if changed and not core.messagebox.askyesno(
            "Вставити заготовку?",
            "Поточні тема, вступ і текст пунктів будуть замінені вибраною заготовкою. Продовжити?",
            parent=dialog,
        ):
            return
        subject_var.set(new_subject)
        preamble.delete("1.0","end"); preamble.insert("1.0",new_preamble)
        body_text.delete("1.0","end"); body_text.insert("1.0",new_body)
    def save():
        order_type=force_type or type_by_label.get(type_var.get(),ops.TYPE_GENERIC)
        series_key=next((key for key,label in ops.ORDER_SERIES_LABELS.items() if label==series_var.get()),ops.ORDER_SERIES_WORK)
        initial_pairs=[]
        if existing is None and order_type==ops.TYPE_VEHICLE_ASSIGNMENT and assignment_box is not None:
            current_vehicle_ids=[initial_vehicles[int(index)]["id"] for index in initial_vehicle_list.curselection()]
            current_driver_ids=[initial_drivers[int(index)]["id"] for index in initial_driver_list.curselection()]
            if current_vehicle_ids or current_driver_ids:
                staged=stage_current_selection(show_error=True)
                if staged is None:
                    return
            initial_pairs=list(staged_initial_pairs)
            if not initial_pairs:
                if not core.messagebox.askyesno(
                    "Порожній наказ про закріплення?",
                    "Жодної пари ТЗ / водій не підготовлено. Створити порожній наказ без закріплень?",
                    parent=dialog,
                ):
                    return
        connection = core.db()
        try:
            oid = order_editor_persistence.save_order(
                ops,
                connection,
                existing=existing,
                order_type=order_type,
                order_series=series_key,
                order_no=no_var.get(),
                order_date=date_var.get(),
                place=place_local.get(),
                subject=subject_var.get(),
                preamble=preamble.get("1.0", "end-1c"),
                body_text=body_text.get("1.0", "end-1c"),
                control_employee_id=emp_by_label.get(control_var.get()),
                initial_pairs=initial_pairs,
            )
            connection.commit()
        except Exception as exc:
            connection.rollback()
            core.messagebox.showerror("Наказ", str(exc), parent=dialog)
            return
        finally:
            connection.close()

        dialog.destroy(); refresh_orders(oid)
        refresh_open_order_previews(oid)
        created_order=order_cache.get(int(oid))
        if order_type==ops.TYPE_VEHICLE_ASSIGNMENT and not initial_pairs:
            book.select(assignments_tab)
            refresh_assignments()
        else:
            book.select(orders_tab)
            if created_order is not None:
                preview_order(created_order)
    bar=core.ttk.Frame(frm); bar.grid(row=12,column=0,columnspan=2,sticky="ew",pady=(10,0))
    core.ttk.Button(bar,text="Скасувати",command=dialog.destroy).pack(side="right")
    core.ttk.Button(bar,text="Вставити заготовку",command=apply_template).pack(side="left")
    core.ttk.Button(bar,text="Зберегти" if existing else "Створити",style="Accent.TButton",command=save).pack(side="right",padx=(0,6)); dialog.transient(win)

