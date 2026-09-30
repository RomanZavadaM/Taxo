# -*- coding: utf-8 -*-
"""Окремий робочий центр СТОІР без перевантаження розділу «Експлуатація»."""
from __future__ import annotations

from datetime import date

import vehicle_maintenance as maint
from vehicle_documents import best_current_document, document_status, display_date


def _vehicle_rows(con):
    return con.execute(
        """SELECT id,name,plate,make_model,COALESCE(active,1) AS active
             FROM vehicles
            ORDER BY COALESCE(active,1) DESC,COALESCE(plate,''),COALESCE(name,'')"""
    ).fetchall()


def _vehicle_label(row):
    bits = [str(row["plate"] or "").strip(), str(row["name"] or row["make_model"] or "").strip()]
    label = " — ".join(x for x in bits if x)
    return label or f"ТЗ #{row['id']}"


def open_maintenance_center(app, core):
    existing = getattr(app, "_maintenance_center_window", None)
    try:
        if existing is not None and existing.winfo_exists():
            existing.lift(); existing.focus_force(); return existing
    except Exception:
        pass

    maint.ensure_schema(core)
    win = core.tk.Toplevel(app)
    app._maintenance_center_window = win
    try:
        core.configure_toplevel(win, title="СТОІР — технічне обслуговування і ремонт", minsize=(920, 600))
        core.fit_window_to_screen(win, 1240, 760, 920, 600)
    except Exception:
        win.geometry("1240x760")
    body = core.ttk.Frame(win, padding=12); body.pack(fill="both", expand=True)
    core.ttk.Label(body, text="СТОІР — експлуатація та технічна готовність", style="HeroTitle.TLabel").pack(anchor="w")
    core.ttk.Label(
        body,
        text=("Пробіг, план ТО та обов'язковий технічний контроль ведуться окремими блоками. "
              "ОТК не замінює ТО-1/ТО-2 і не змішується з ними."),
        style="Muted.TLabel", wraplength=1160, justify="left",
    ).pack(anchor="w", pady=(2, 8))

    selector = core.ttk.Frame(body); selector.pack(fill="x", pady=(0,8))
    core.ttk.Label(selector, text="Транспортний засіб:").pack(side="left")
    con = core.db()
    try: vehicles = _vehicle_rows(con)
    finally: con.close()
    labels = {_vehicle_label(row): int(row["id"]) for row in vehicles}
    vehicle_var = core.tk.StringVar(value=(next(iter(labels)) if labels else ""))
    box = core.ttk.Combobox(selector, textvariable=vehicle_var, values=list(labels), state="readonly", width=48)
    box.pack(side="left", padx=(8,8))

    book = core.ttk.Notebook(body); book.pack(fill="both", expand=True)
    overview = core.ttk.Frame(book); mileage = core.ttk.Frame(book); service = core.ttk.Frame(book); inspection = core.ttk.Frame(book)
    book.add(overview, text="Огляд")
    book.add(mileage, text="Пробіг / одометр")
    book.add(service, text="ТО і ремонти")
    book.add(inspection, text="Технічний контроль (ОТК)")

    # Огляд
    overview_box = core.ttk.Frame(overview, padding=14); overview_box.pack(fill="both", expand=True)
    overview_text = core.tk.Text(overview_box, wrap="word", height=12, state="disabled")
    overview_text.pack(fill="both", expand=True)

    # Пробіг
    mileage_frame = core.ttk.Frame(mileage, padding=10); mileage_frame.pack(fill="both", expand=True)
    mileage_cols = ("at","km","source","note")
    mileage_tree = core.ttk.Treeview(mileage_frame, columns=mileage_cols, show="headings")
    for key,label,width in (("at","Дата / час",180),("km","Одометр, км",120),("source","Джерело",150),("note","Примітка",500)):
        mileage_tree.heading(key,text=label); mileage_tree.column(key,width=width,anchor="w")
    mileage_tree.pack(fill="both",expand=True)

    # ТО і ремонти
    service_top = core.ttk.Frame(service, padding=10); service_top.pack(fill="x")
    service_frame = core.ttk.Frame(service, padding=(10,0,10,10)); service_frame.pack(fill="both",expand=True)
    service_cols=("date","type","km","description","document")
    service_tree=core.ttk.Treeview(service_frame,columns=service_cols,show="headings")
    for key,label,width in (("date","Дата",100),("type","Подія",110),("km","Одометр",110),("description","Роботи / опис",420),("document","Документ",220)):
        service_tree.heading(key,text=label); service_tree.column(key,width=width,anchor="w")
    service_tree.pack(fill="both",expand=True)

    def selected_vehicle_id():
        return labels.get(vehicle_var.get())

    def add_event(event_type):
        vehicle_id=selected_vehicle_id()
        if not vehicle_id: return
        dialog=core.tk.Toplevel(win); dialog.title("Запис ТО / ремонту")
        frm=core.ttk.Frame(dialog,padding=12); frm.pack(fill="both",expand=True); frm.columnconfigure(1,weight=1)
        date_var=core.tk.StringVar(value=date.today().strftime("%d.%m.%Y")); km_var=core.tk.StringVar(); desc_var=core.tk.StringVar(); doc_var=core.tk.StringVar()
        for row,(label,var) in enumerate((("Дата",date_var),("Одометр, км",km_var),("Опис робіт",desc_var),("Документ / наряд",doc_var))):
            core.ttk.Label(frm,text=label).grid(row=row,column=0,sticky="w",padx=(0,8),pady=5)
            core.ttk.Entry(frm,textvariable=var).grid(row=row,column=1,sticky="ew",pady=5)
        def save():
            con2=core.db()
            try:
                maint.record_event(con2,vehicle_id,event_type,date_var.get(),odometer_km=km_var.get(),description=desc_var.get(),document_ref=doc_var.get())
                con2.commit()
            except Exception as exc:
                con2.rollback(); core.messagebox.showerror("СТОІР",str(exc),parent=dialog); return
            finally: con2.close()
            dialog.destroy(); refresh()
        core.ttk.Button(frm,text="Зберегти",style="Accent.TButton",command=save).grid(row=4,column=1,sticky="e",pady=(10,0))
    for text,event in (("Додати ТО-1",maint.MAINTENANCE_TO1),("Додати ТО-2",maint.MAINTENANCE_TO2),("Сезонне ТО",maint.MAINTENANCE_SEASONAL),("Ремонт",maint.MAINTENANCE_REPAIR)):
        core.ttk.Button(service_top,text=text,command=lambda e=event:add_event(e)).pack(side="left",padx=(0,6))

    # ОТК — читає юридичний документ із реєстру документів ТЗ, не дублює файл.
    inspection_box=core.ttk.Frame(inspection,padding=14); inspection_box.pack(fill="both",expand=True)
    inspection_status=core.tk.StringVar(value="")
    core.ttk.Label(inspection_box,textvariable=inspection_status,justify="left",wraplength=1000).pack(anchor="w")
    core.ttk.Label(
        inspection_box,
        text=("Копія протоколу зберігається в «Документи ТЗ». Тут показується лише експлуатаційний контроль його чинності. "
              "Негативний результат ОТК не слід оформляти як чинний протокол."),
        style="Muted.TLabel",justify="left",wraplength=1000,
    ).pack(anchor="w",pady=(12,0))

    def refresh():
        vid=selected_vehicle_id()
        if not vid: return
        con2=core.db()
        try:
            plan=maint.vehicle_plan(con2,vid)
            rows=con2.execute("""SELECT reading_at,reading_km,source_type,COALESCE(notes,'') AS notes
                                  FROM vehicle_odometer_readings WHERE vehicle_id=?
                                  ORDER BY reading_at DESC,id DESC LIMIT 500""",(vid,)).fetchall()
            events=con2.execute("""SELECT * FROM vehicle_maintenance_events WHERE vehicle_id=? ORDER BY event_date DESC,id DESC""",(vid,)).fetchall()
            otk=best_current_document(con2,vid,"inspection")
        finally: con2.close()
        current=plan["current_odometer_km"]
        lines=[f"Поточний підтверджений одометр: {current if current is not None else 'немає даних'} км"]
        profile=plan["profile"]
        lines.append(f"Профіль ТО: ТО-1 кожні {profile['to1_interval_km']} км; ТО-2 кожні {profile['to2_interval_km']} км")
        for key,label in (("to1","ТО-1"),("to2","ТО-2")):
            item=plan[key]; due=item["due"]
            if due:
                lines.append(f"{label}: наступне на {due['due_odometer_km']} км; залишок {due['remaining_km']} км; статус {item['status']}")
            else:
                lines.append(f"{label}: немає базового факту останнього {label}; план не вигадується")
        overview_text.configure(state="normal"); overview_text.delete("1.0","end"); overview_text.insert("1.0","\n".join(lines)); overview_text.configure(state="disabled")
        for tree in (mileage_tree,service_tree):
            for iid in tree.get_children(): tree.delete(iid)
        for row in rows: mileage_tree.insert("","end",values=(row["reading_at"],row["reading_km"],row["source_type"],row["notes"]))
        for row in events: service_tree.insert("","end",values=(row["event_date"],row["event_type"],row["odometer_km"] or "",row["description"],row["document_ref"]))
        if otk is None:
            inspection_status.set("Протокол ОТК: відсутній у реєстрі документів ТЗ.")
        else:
            status=document_status("inspection",otk["valid_until"])
            inspection_status.set(
                "Протокол ОТК / перевірки технічного стану\n"
                f"№ {otk['document_no'] or '—'}\n"
                f"чинний до: {display_date(otk['valid_until']) or 'дата не зазначена'}\n"
                f"статус: {status}\n"
                f"виконавець/видавець: {otk['issuer'] or '—'}"
            )
    box.bind("<<ComboboxSelected>>",lambda _e:refresh())
    core.ttk.Button(selector,text="Оновити",command=refresh).pack(side="left")
    refresh()
    return win
