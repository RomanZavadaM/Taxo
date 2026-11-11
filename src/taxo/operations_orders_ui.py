# -*- coding: utf-8 -*-
"""Координатор центру «Експлуатація» та реєстру наказів."""
from __future__ import annotations

import operations_orders as ops
from order_pdf_workflow import save_and_preview_order
from order_preview_ui import open_order_preview
from order_editor_ui import open_order_editor
from order_assignments_ui import install_assignment_tab
from order_entities_ui import install_order_entities_tab
from safety_instructions_ui import install_instruction_tab
from driver_internship_ui import install_internship_tab
from operations_settings_ui import install_operations_settings
from order_type_catalog_ui import install_order_type_catalog


def _alive(widget):
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


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
    header = core.ttk.Frame(body)
    header.pack(fill="x")
    core.ttk.Label(header, text="Експлуатація", style="HeroTitle.TLabel").pack(side="left")
    core.ttk.Button(
        header, text="Лист стажування…",
        command=lambda: book.select(internship_tab)
    ).pack(side="right")
    def open_documents_catalog():
        from document_catalog_ui import open_document_catalog
        from workspace import load_workspace_root
        open_document_catalog(win, core, load_workspace_root())

    core.ttk.Button(header, text="Документи…",
                    command=open_documents_catalog).pack(side="right", padx=(8, 0))

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

    settings = install_operations_settings(core, settings_tab, win)
    employee_labels = settings.employee_labels
    emp_by_label = settings.employee_by_label
    emp_by_id = settings.employee_by_id
    operations_resp_var = settings.operations_responsible_var
    place_var = settings.order_place_var
    work_order_next_var = settings.work_order_next_var
    personnel_order_next_var = settings.personnel_order_next_var
    work_order_next_entry = settings.work_order_next_entry

    install_instruction_tab(app, core, book)
    internship_tab = install_internship_tab(app, core, book)

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
    preview_refreshers={}

    def register_order_preview(order_id, dialog, callback):
        oid=int(order_id)
        preview_refreshers.setdefault(oid, []).append((dialog, callback))
        def cleanup(event=None):
            if event is not None and getattr(event, "widget", None) is not dialog:
                return
            current=preview_refreshers.get(oid, [])
            current=[item for item in current if item[0] is not dialog]
            if current:
                preview_refreshers[oid]=current
            else:
                preview_refreshers.pop(oid, None)
        try:
            dialog.bind("<Destroy>", cleanup, add="+")
        except Exception:
            pass

    def refresh_open_order_previews(order_id):
        oid=int(order_id)
        current=list(preview_refreshers.get(oid, []))
        alive=[]
        refreshed=0
        for dialog,callback in current:
            try:
                if not dialog.winfo_exists():
                    continue
                callback()
                alive.append((dialog,callback))
                refreshed+=1
            except Exception:
                try:
                    if dialog.winfo_exists():
                        alive.append((dialog,callback))
                except Exception:
                    pass
        if alive:
            preview_refreshers[oid]=alive
        else:
            preview_refreshers.pop(oid, None)
        return refreshed

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
        return open_order_editor(
            core, ops, win, existing, force_type, personnel_order_next_var,
            work_order_next_var, place_var, emp_by_id, operations_resp_var,
            type_labels, type_by_label, employee_labels, emp_by_label,
            book, assignments_tab, orders_tab, refresh_assignments,
            add_assignments_bulk, refresh_orders, refresh_open_order_previews,
            order_cache, preview_order,
        )

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
            latest=ops.get_order(con2,row["id"]) or row
            assignments=ops.order_assignments(con2,latest["id"])
            entities=ops.list_order_entities(con2,latest["id"]) if hasattr(ops,"list_order_entities") else []
            company_row=con2.execute("SELECT * FROM company WHERE id=1").fetchone()
            company={key:company_row[key] for key in company_row.keys()} if company_row else {}
            control=ops.employee_name(con2,latest["control_employee_id"])
        finally:
            con2.close()
        return latest,assignments,entities,company,control

    def export_order(row,parent=None):
        latest,assignments,_entities,company,control=_order_print_data(row)
        return save_and_preview_order(
            core,ops,latest,assignments,company,control,parent or win
        )

    def export_selected():
        row=selected_order()
        if row is not None:
            export_order(row,win)

    def preview_order(row=None):
        row = row or selected_order()
        if row is None:
            return
        return open_order_preview(core, ops, win, row, _order_print_data,
                                  register_order_preview, order_mutability_message, order_dialog)

    order_actions = (
        ("Новий наказ…", new_order, "Accent.TButton"),
        ("Переглянути / друк", preview_order, "Accent.TButton"),
        ("Нумерація наказів…", open_numbering_settings, None),
        ("Редагувати наказ", edit_order, None),
        ("Ввести в дію в Taxo", approve_selected, None),
        ("Історія…", show_history, None),
        ("Скасувати наказ", cancel_draft, None),
        ("Видалити наказ", delete_selected_order, None),
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

    refresh_assignments, add_assignments_bulk = install_assignment_tab(
        core, ops, win, assignments_tab, order_tree, create_assignment_order,
        selected_order, require_mutable_order, refresh_open_order_previews,
    )

    refresh_order_entities = install_order_entities_tab(
        core, ops, win, entities_tab, order_tree, selected_order, require_mutable_order,
    )

    install_order_type_catalog(
        core,
        maintenance_tab,
        win,
        order_dialog,
    )

    def preview_catalog_order(order_id):
        # Reuse the existing live preview without depending on the visible
        # first 1000 rows in the orders table.
        con2 = core.db()
        try:
            row = ops.get_order(con2, order_id)
        finally:
            con2.close()
        if row is None:
            raise ValueError("Наказ більше не існує в робочій базі.")
        preview_order(row)

    win._taxo_preview_catalog_order = preview_catalog_order
    refresh_orders(); return win
