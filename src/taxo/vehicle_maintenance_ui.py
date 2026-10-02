# -*- coding: utf-8 -*-
"""СТОІР 10.8-r5: прогноз ТО, заявки на несправності та компактні реєстри."""
from __future__ import annotations

from datetime import date

import vehicle_maintenance as maint
from vehicle_documents import best_current_document, document_status, display_date


def _vehicle_rows(con):
    return con.execute(
        """SELECT id,name,plate,make_model,COALESCE(active,1) AS active
             FROM vehicles ORDER BY COALESCE(active,1) DESC,COALESCE(plate,''),COALESCE(name,'')"""
    ).fetchall()


def _vehicle_label(row):
    bits = [str(row["plate"] or "").strip(), str(row["name"] or row["make_model"] or "").strip()]
    return " — ".join(x for x in bits if x) or f"ТЗ #{row['id']}"


def _tree_with_scrollbars(core, parent, columns, specs, *, height=15):
    frame = core.ttk.Frame(parent)
    frame.pack(fill="both", expand=True)
    tree = core.ttk.Treeview(frame, columns=columns, show="headings", height=height)
    ybar = core.ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    xbar = core.ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
    tree.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    xbar.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1); frame.columnconfigure(0, weight=1)
    for key, label, width in specs:
        tree.heading(key, text=label)
        tree.column(key, width=width, minwidth=70, anchor="w", stretch=(key == columns[-1]))
    return tree


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
        core.fit_window_to_screen(win, 1260, 780, 920, 600)
    except Exception:
        win.geometry("1260x780")

    body = core.ttk.Frame(win, padding=12); body.pack(fill="both", expand=True)
    core.ttk.Label(body, text="СТОІР — експлуатація та технічна готовність", style="HeroTitle.TLabel").pack(anchor="w")
    core.ttk.Label(
        body,
        text=("Пробіг, прогноз ТО, заявки на несправності та ОТК ведуться окремо. "
              "Прогноз є розрахунковим і не підмінює фактичний запис виконаного ТО."),
        style="Muted.TLabel", wraplength=1180, justify="left",
    ).pack(anchor="w", pady=(2, 8))

    selector = core.ttk.Frame(body); selector.pack(fill="x", pady=(0, 8))
    core.ttk.Label(selector, text="Транспортний засіб:").pack(side="left")
    con = core.db()
    try:
        vehicles = _vehicle_rows(con)
    finally:
        con.close()
    labels = {_vehicle_label(row): int(row["id"]) for row in vehicles}
    vehicle_var = core.tk.StringVar(value=(next(iter(labels)) if labels else ""))
    box = core.ttk.Combobox(selector, textvariable=vehicle_var, values=list(labels), state="readonly", width=48)
    box.pack(side="left", padx=(8, 8))

    book = core.ttk.Notebook(body); book.pack(fill="both", expand=True)
    overview = core.ttk.Frame(book); mileage = core.ttk.Frame(book); service = core.ttk.Frame(book)
    requests = core.ttk.Frame(book); report = core.ttk.Frame(book); inspection = core.ttk.Frame(book)
    book.add(overview, text="Огляд / прогноз")
    book.add(mileage, text="Пробіг / одометр")
    book.add(service, text="ТО і ремонти")
    book.add(requests, text="Заявки на несправності")
    book.add(report, text="Зведення")
    book.add(inspection, text="Технічний контроль (ОТК)")

    overview_box = core.ttk.Frame(overview, padding=14); overview_box.pack(fill="both", expand=True)
    overview_text = core.tk.Text(overview_box, wrap="word", height=12, state="disabled")
    overview_text.pack(fill="both", expand=True)

    mileage_frame = core.ttk.Frame(mileage, padding=10); mileage_frame.pack(fill="both", expand=True)
    mileage_tree = _tree_with_scrollbars(
        core, mileage_frame, ("at", "km", "source", "note"),
        (("at", "Дата / час", 180), ("km", "Одометр, км", 120), ("source", "Джерело", 150), ("note", "Примітка", 500)),
    )

    service_top = core.ttk.Frame(service, padding=10); service_top.pack(fill="x")
    service_frame = core.ttk.Frame(service, padding=(10, 0, 10, 10)); service_frame.pack(fill="both", expand=True)
    service_tree = _tree_with_scrollbars(
        core, service_frame, ("date", "type", "km", "description", "document"),
        (("date", "Дата", 100), ("type", "Подія", 110), ("km", "Одометр", 110),
         ("description", "Роботи / опис", 420), ("document", "Документ", 220)),
    )

    request_top = core.ttk.Frame(requests, padding=10); request_top.pack(fill="x")
    request_frame = core.ttk.Frame(requests, padding=(10, 0, 10, 10)); request_frame.pack(fill="both", expand=True)
    request_tree = _tree_with_scrollbars(
        core, request_frame, ("id", "reported", "priority", "status", "defect", "assignee", "resolution"),
        (("id", "№", 60), ("reported", "Зареєстровано", 150), ("priority", "Пріоритет", 100),
         ("status", "Статус", 100), ("defect", "Несправність / заявка", 330),
         ("assignee", "Виконавець", 150), ("resolution", "Результат", 260)),
    )

    report_frame = core.ttk.Frame(report, padding=10); report_frame.pack(fill="both", expand=True)
    report_tree = _tree_with_scrollbars(
        core, report_frame, ("vehicle", "odometer", "avg", "to1", "to2", "requests"),
        (("vehicle", "ТЗ", 220), ("odometer", "Одометр", 110), ("avg", "Сер. км/день", 110),
         ("to1", "ТО-1", 230), ("to2", "ТО-2", 230), ("requests", "Відкриті заявки", 120)),
    )

    inspection_box = core.ttk.Frame(inspection, padding=14); inspection_box.pack(fill="both", expand=True)
    inspection_status = core.tk.StringVar(value="")
    core.ttk.Label(inspection_box, textvariable=inspection_status, justify="left", wraplength=1000).pack(anchor="w")
    core.ttk.Label(
        inspection_box,
        text=("Копія протоколу зберігається в «Документи ТЗ». Тут показується лише експлуатаційний контроль його чинності. "
              "ОТК не є ТО-1/ТО-2."),
        style="Muted.TLabel", justify="left", wraplength=1000,
    ).pack(anchor="w", pady=(12, 0))

    def selected_vehicle_id():
        return labels.get(vehicle_var.get())

    def add_event(event_type):
        vehicle_id = selected_vehicle_id()
        if not vehicle_id:
            return
        dialog = core.tk.Toplevel(win); dialog.title("Запис ТО / ремонту")
        frm = core.ttk.Frame(dialog, padding=12); frm.pack(fill="both", expand=True); frm.columnconfigure(1, weight=1)
        date_var = core.tk.StringVar(value=date.today().strftime("%d.%m.%Y"))
        km_var = core.tk.StringVar(); desc_var = core.tk.StringVar(); doc_var = core.tk.StringVar()
        for row, (label, var) in enumerate((("Дата", date_var), ("Одометр, км", km_var), ("Опис робіт", desc_var), ("Документ / наряд", doc_var))):
            core.ttk.Label(frm, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=5)
            core.ttk.Entry(frm, textvariable=var).grid(row=row, column=1, sticky="ew", pady=5)
        def save():
            con2 = core.db()
            try:
                maint.record_event(con2, vehicle_id, event_type, date_var.get(), odometer_km=km_var.get(), description=desc_var.get(), document_ref=doc_var.get())
                con2.commit()
            except Exception as exc:
                con2.rollback(); core.messagebox.showerror("СТОІР", str(exc), parent=dialog); return
            finally:
                con2.close()
            dialog.destroy(); refresh()
        core.ttk.Button(frm, text="Зберегти", style="Accent.TButton", command=save).grid(row=4, column=1, sticky="e", pady=(10, 0))

    for text, event in (("Додати ТО-1", maint.MAINTENANCE_TO1), ("Додати ТО-2", maint.MAINTENANCE_TO2),
                        ("Сезонне ТО", maint.MAINTENANCE_SEASONAL), ("Ремонт", maint.MAINTENANCE_REPAIR)):
        core.ttk.Button(service_top, text=text, command=lambda e=event: add_event(e)).pack(side="left", padx=(0, 6))

    def add_request():
        vehicle_id = selected_vehicle_id()
        if not vehicle_id:
            return
        dialog = core.tk.Toplevel(win); dialog.title("Нова заявка на несправність / ремонт")
        frm = core.ttk.Frame(dialog, padding=12); frm.pack(fill="both", expand=True); frm.columnconfigure(1, weight=1)
        defect = core.tk.StringVar(); priority = core.tk.StringVar(value="normal"); reporter = core.tk.StringVar(); assignee = core.tk.StringVar()
        core.ttk.Label(frm, text="Несправність / що потрібно зробити").grid(row=0, column=0, sticky="w", padx=(0,8), pady=5)
        core.ttk.Entry(frm, textvariable=defect, width=58).grid(row=0, column=1, sticky="ew", pady=5)
        core.ttk.Label(frm, text="Пріоритет").grid(row=1, column=0, sticky="w", pady=5)
        core.ttk.Combobox(frm, textvariable=priority, values=list(maint.REQUEST_PRIORITIES), state="readonly").grid(row=1, column=1, sticky="ew", pady=5)
        core.ttk.Label(frm, text="Хто повідомив").grid(row=2, column=0, sticky="w", pady=5)
        core.ttk.Entry(frm, textvariable=reporter).grid(row=2, column=1, sticky="ew", pady=5)
        core.ttk.Label(frm, text="Виконавець").grid(row=3, column=0, sticky="w", pady=5)
        core.ttk.Entry(frm, textvariable=assignee).grid(row=3, column=1, sticky="ew", pady=5)
        def save():
            con2 = core.db()
            try:
                maint.create_repair_request(con2, vehicle_id, defect.get(), priority=priority.get(), reporter=reporter.get(), assignee=assignee.get())
                con2.commit()
            except Exception as exc:
                con2.rollback(); core.messagebox.showerror("СТОІР", str(exc), parent=dialog); return
            finally:
                con2.close()
            dialog.destroy(); refresh()
        core.ttk.Button(frm, text="Створити заявку", style="Accent.TButton", command=save).grid(row=4, column=1, sticky="e", pady=(10,0))

    def set_request_status(status):
        selected = request_tree.selection()
        if not selected:
            return
        values = request_tree.item(selected[0], "values")
        if not values:
            return
        con2 = core.db()
        try:
            maint.update_repair_request(con2, int(values[0]), status=status)
            con2.commit()
        finally:
            con2.close()
        refresh()

    core.ttk.Button(request_top, text="Нова заявка", style="Accent.TButton", command=add_request).pack(side="left", padx=(0,6))
    core.ttk.Button(request_top, text="В роботу", command=lambda: set_request_status(maint.REQUEST_IN_PROGRESS)).pack(side="left", padx=(0,6))
    core.ttk.Button(request_top, text="Закрити", command=lambda: set_request_status(maint.REQUEST_CLOSED)).pack(side="left", padx=(0,6))
    core.ttk.Label(request_top, text="Дії застосовуються до вибраного рядка; кнопок усередині таблиці немає.", style="Muted.TLabel").pack(side="left", padx=(12,0))

    def _due_text(item):
        due = item.get("due")
        if not due:
            return "немає базового ТО"
        forecast = item.get("forecast_date")
        tail = f"; ≈ {forecast.strftime('%d.%m.%Y')}" if forecast else ""
        return f"{due['remaining_km']} км ({item['status']}){tail}"

    def refresh():
        vid = selected_vehicle_id()
        if not vid:
            return
        con2 = core.db()
        try:
            plan = maint.vehicle_plan(con2, vid)
            rows = con2.execute("""SELECT reading_at,reading_km,source_type,COALESCE(notes,'') AS notes
                                  FROM vehicle_odometer_readings WHERE vehicle_id=? ORDER BY reading_at DESC,id DESC LIMIT 500""", (vid,)).fetchall()
            events = con2.execute("SELECT * FROM vehicle_maintenance_events WHERE vehicle_id=? ORDER BY event_date DESC,id DESC", (vid,)).fetchall()
            reqs = maint.repair_requests(con2, vid, include_closed=True)
            fleet = maint.fleet_maintenance_report(con2)
            otk = best_current_document(con2, vid, "inspection")
        finally:
            con2.close()

        avg = plan.get("average_daily_km")
        lines = [f"Поточний підтверджений одометр: {plan['current_odometer_km'] if plan['current_odometer_km'] is not None else 'немає даних'} км"]
        lines.append(f"Середній фактичний пробіг за останні 60 днів: {avg:.1f} км/день" if avg else "Середній пробіг: недостатньо фактичних показників для прогнозу")
        profile = plan["profile"]
        lines.append(f"Профіль ТО: ТО-1 кожні {profile['to1_interval_km']} км; ТО-2 кожні {profile['to2_interval_km']} км")
        lines.append(f"ТО-1: {_due_text(plan['to1'])}")
        lines.append(f"ТО-2: {_due_text(plan['to2'])}")
        lines.append("Прогнозована дата змінюється разом із фактичним середнім пробігом і не є записом про виконане ТО.")
        overview_text.configure(state="normal"); overview_text.delete("1.0", "end"); overview_text.insert("1.0", "\n".join(lines)); overview_text.configure(state="disabled")

        for tree in (mileage_tree, service_tree, request_tree, report_tree):
            for iid in tree.get_children():
                tree.delete(iid)
        for row in rows:
            mileage_tree.insert("", "end", values=(row["reading_at"], row["reading_km"], row["source_type"], row["notes"]))
        for row in events:
            service_tree.insert("", "end", values=(row["event_date"], row["event_type"], row["odometer_km"] or "", row["description"], row["document_ref"]))
        for row in reqs:
            request_tree.insert("", "end", values=(row["id"], row["reported_at"], maint.REQUEST_PRIORITY_LABELS.get(row["priority"], row["priority"]),
                                                       maint.REQUEST_STATUS_LABELS.get(row["status"], row["status"]), row["defect"], row["assignee"], row["resolution"]))
        for item in fleet:
            vehicle = item["vehicle"]; fplan = item["plan"]
            label = " — ".join(x for x in (str(vehicle["plate"] or "").strip(), str(vehicle["name"] or vehicle["make_model"] or "").strip()) if x)
            favg = fplan.get("average_daily_km")
            report_tree.insert("", "end", values=(label or f"ТЗ #{vehicle['id']}", fplan["current_odometer_km"] or "", f"{favg:.1f}" if favg else "—",
                                                    _due_text(fplan["to1"]), _due_text(fplan["to2"]), item["open_requests"]))
        if otk is None:
            inspection_status.set("Протокол ОТК: відсутній у реєстрі документів ТЗ.")
        else:
            status = document_status("inspection", otk["valid_until"])
            inspection_status.set("Протокол ОТК / перевірки технічного стану\n"
                                  f"№ {otk['document_no'] or '—'}\nчинний до: {display_date(otk['valid_until']) or 'дата не зазначена'}\n"
                                  f"статус: {status}\nвиконавець/видавець: {otk['issuer'] or '—'}")

    box.bind("<<ComboboxSelected>>", lambda _e: refresh())
    core.ttk.Button(selector, text="Оновити", command=refresh).pack(side="left")
    refresh()
    return win
