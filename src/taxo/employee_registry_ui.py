# -*- coding: utf-8 -*-
"""UI реєстру працівників.

Цей модуль відповідає за список працівників, картку працівника та базові
дії зі статусом працевлаштування. Бізнес-дані лишаються у чинній БД Taxo.

Методи App у main.py збережені як сумісні адаптери: старі feature layers
можуть і надалі викликати їх або розширювати через super().
"""
from __future__ import annotations

from datetime import date, datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from branding import PALETTE, configure_toplevel, draw_brand_header


def employee_full_name(row):
    """Повернути ПІБ працівника без порожніх складових."""
    return " ".join(
        value
        for value in (row["last_name"], row["first_name"], row["middle_name"])
        if value
    ).strip()


def show_employee_registry(app, fit_window_to_screen):
    """Відкрити основний розділ персоналу або сумісне старе вікно реєстру."""
    personnel_tab = getattr(app, "tab_personnel", None)
    if personnel_tab is not None:
        overview_action = getattr(app, "show_personnel_overview", None)
        if callable(overview_action):
            overview_action()
        else:
            app.show_tab(personnel_tab)
            refresh = getattr(app, "_refresh_personnel_overview", None)
            if callable(refresh):
                refresh()
        return

    if hasattr(app, "employee_win") and app.employee_win.winfo_exists():
        app.employee_win.lift()
        app.load_employee_registry()
        return

    win = tk.Toplevel(app)
    app.employee_win = win
    fit_window_to_screen(win, 1080, 650, 820, 500)
    app._decorate_secondary_window(
        win,
        "Реєстр усіх працівників",
        "Персонал, ролі та статус працевлаштування",
    )

    top = ttk.Frame(win, padding=8)
    top.pack(fill="x")
    ttk.Button(top, text="Новий працівник", command=app.employee_form).pack(
        side="left", padx=3
    )
    ttk.Button(top, text="Редагувати", command=app.edit_employee).pack(
        side="left", padx=3
    )
    ttk.Button(
        top,
        text="Звільнити / поновити",
        command=app.toggle_employee_active,
    ).pack(side="left", padx=3)
    ttk.Button(
        top,
        text="Зміни випуску",
        command=app.show_dispatch_staff_schedule,
    ).pack(side="left", padx=3)
    ttk.Button(
        top,
        text="Табель персоналу",
        command=app.show_employee_timesheet,
    ).pack(side="left", padx=3)

    ttk.Label(
        win,
        text=(
            "Водій є працівником із додатковою водійською карткою. "
            "Лікаря, механіка, диспетчера та інших вводьте тут один раз."
        ),
        foreground=PALETTE["muted"],
        wraplength=1020,
        justify="left",
    ).pack(fill="x", padx=10, pady=(0, 6))

    frame = ttk.Frame(win)
    frame.pack(fill="both", expand=True, padx=10, pady=6)
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    columns = (
        "id",
        "personnel",
        "name",
        "gender",
        "roles",
        "position",
        "tariff",
        "employment",
        "dismissal",
        "phone",
        "status",
    )
    app.employee_tree = ttk.Treeview(frame, columns=columns, show="headings")
    headings = {
        "id": "ID",
        "personnel": "Таб. №",
        "name": "ПІБ",
        "gender": "Стать",
        "roles": "Ролі",
        "position": "Посада",
        "tariff": "Оклад / ставка",
        "employment": "Прийнятий",
        "dismissal": "Звільнений",
        "phone": "Телефон",
        "status": "Стан",
    }
    widths = {
        "id": 45,
        "personnel": 75,
        "name": 220,
        "gender": 55,
        "roles": 170,
        "position": 145,
        "tariff": 105,
        "employment": 90,
        "dismissal": 90,
        "phone": 120,
        "status": 80,
    }
    for key in columns:
        app.employee_tree.heading(key, text=headings[key])
        app.employee_tree.column(key, width=widths[key], anchor="w")

    ybar = ttk.Scrollbar(frame, orient="vertical", command=app.employee_tree.yview)
    xbar = ttk.Scrollbar(frame, orient="horizontal", command=app.employee_tree.xview)
    app.employee_tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
    app.employee_tree.grid(row=0, column=0, sticky="nsew")
    ybar.grid(row=0, column=1, sticky="ns")
    xbar.grid(row=1, column=0, sticky="ew")
    app.employee_tree.bind("<Double-1>", lambda _event: app.edit_employee())
    app.load_employee_registry()


def load_employee_registry(app, db_factory, fmt_date):
    """Перечитати реєстр працівників без зміни даних."""
    if not hasattr(app, "employee_tree") or not app.employee_tree.winfo_exists():
        return

    for item in app.employee_tree.get_children():
        app.employee_tree.delete(item)

    con = db_factory()
    try:
        rows = con.execute(
            """SELECT e.*,GROUP_CONCAT(er.role, ', ') roles FROM employees e
               LEFT JOIN employee_roles er ON er.employee_id=e.id GROUP BY e.id
               ORDER BY e.active DESC,e.last_name,e.first_name,e.middle_name"""
        ).fetchall()
    finally:
        con.close()

    for row in rows:
        tariff = (
            ""
            if "tariff_rate" not in row.keys() or row["tariff_rate"] is None
            else f"{float(row['tariff_rate']):.2f}"
        )
        gender = (row["gender"] if "gender" in row.keys() else "") or ""
        app.employee_tree.insert(
            "",
            "end",
            values=(
                row["id"],
                row["personnel_no"],
                app.employee_full_name(row),
                gender,
                row["roles"] or "",
                row["position"],
                tariff,
                fmt_date(row["employment_date"]),
                fmt_date(row["dismissal_date"]),
                row["phone"],
                "Працює" if row["active"] else "Звільнений",
            ),
        )


def selected_employee(app, db_factory):
    """Повернути вибраного працівника з реєстру або головної сторінки персоналу."""
    tree = getattr(app, "employee_tree", None)
    selection = tree.selection() if tree is not None and tree.winfo_exists() else ()
    employee_id = None
    if selection:
        try:
            employee_id = int(tree.item(selection[0], "values")[0])
        except (TypeError, ValueError, IndexError):
            employee_id = None

    if employee_id is None:
        tree = getattr(app, "personnel_overview_tree", None)
        selection = tree.selection() if tree is not None and tree.winfo_exists() else ()
        if selection:
            try:
                employee_id = int(selection[0])
            except (TypeError, ValueError):
                employee_id = None

    if employee_id is None:
        return None

    con = db_factory()
    try:
        return con.execute(
            "SELECT * FROM employees WHERE id=?",
            (employee_id,),
        ).fetchone()
    finally:
        con.close()


def employee_form(
    app,
    employee=None,
    *,
    db_factory,
    fmt_date,
    calendar_button,
    fit_window_to_screen,
    finish_driver_role,
    void_legacy_driver_role,
    activate_driver_role,
):
    parent=getattr(app,"employee_win",app)
    win=tk.Toplevel(parent)
    win.title(f"Taxo / {app._company_name_value()} — Картка працівника")
    fit_window_to_screen(win,1040,740,860,620)
    configure_toplevel(win)
    win.transient(parent)
    win.grab_set()

    banner=tk.Canvas(win,height=82,bg=PALETTE["header"],highlightthickness=0)
    banner.pack(fill="x")
    draw_brand_header(banner,app._company_name_value(),"Картка працівника")
    banner.bind(
        "<Configure>",
        lambda _e:draw_brand_header(
            banner,app._company_name_value(),"Картка працівника"
        ),
        add="+",
    )

    con=db_factory()
    current_roles={
        r[0] for r in con.execute(
            "SELECT role FROM employee_roles WHERE employee_id=?",
            (employee["id"],),
        ).fetchall()
    } if employee else set()
    current_driver_end=""
    if employee and employee["driver_id"]:
        driver_row=con.execute(
            "SELECT driver_end_date FROM drivers WHERE id=?",(employee["driver_id"],)
        ).fetchone()
        if driver_row:
            current_driver_end=(driver_row["driver_end_date"] or "").strip()
    con.close()

    title=ttk.Frame(win,padding=(14,10,14,4))
    title.pack(fill="x")
    ttk.Label(
        title,
        text="Картка працівника" if employee else "Новий працівник",
        style="HeroTitle.TLabel",
    ).pack(side="left")
    state_text="Працює" if (not employee or bool(employee["active"])) else "Звільнений"
    state_color=PALETTE["success"] if state_text=="Працює" else PALETTE["danger"]
    tk.Label(
        title,text=state_text,bg=PALETTE["paper"],fg=state_color,
        font=("TkDefaultFont",11,"bold")
    ).pack(side="right",padx=6)

    fields=(
        ("personnel_no","Табельний номер"),
        ("last_name","Прізвище"),
        ("first_name","Ім'я"),
        ("middle_name","По батькові"),
        ("position","Основна посада"),
        ("gender","Стать для П-5"),
        ("tariff_rate","Оклад / тарифна ставка, грн"),
        ("phone","Телефон"),
        ("employment_date","Дата прийняття"),
        ("dismissal_date","Дата звільнення"),
        ("notes","Примітка"),
    )
    values={}
    for key,_label in fields:
        raw=employee[key] if employee and key in employee.keys() else ""
        if raw is None:
            raw=""
        if key=="tariff_rate" and raw!="":
            try:
                raw=f"{float(raw):.2f}".rstrip("0").rstrip(".")
            except Exception:
                raw=str(raw)
        if key in {"employment_date","dismissal_date"}:
            raw=fmt_date(raw)
        values[key]=tk.StringVar(value=raw)

    body=ttk.Frame(win,padding=(14,4,14,8))
    body.pack(fill="both",expand=True)
    body.columnconfigure(0,weight=3)
    body.columnconfigure(1,weight=2)
    body.rowconfigure(0,weight=1)

    basic=ttk.LabelFrame(body,text="Основні дані",padding=10)
    basic.grid(row=0,column=0,sticky="nsew",padx=(0,7))
    basic.columnconfigure(1,weight=1)

    def field(frame,row,key,label,calendar_field=False):
        ttk.Label(frame,text=label).grid(
            row=row,column=0,sticky="w",padx=(0,8),pady=5
        )
        if key=="gender":
            widget=ttk.Combobox(
                frame,textvariable=values[key],
                values=("", "ч", "ж"),state="readonly",width=12
            )
        else:
            widget=ttk.Entry(frame,textvariable=values[key])
        widget.grid(row=row,column=1,sticky="ew",pady=5)
        if calendar_field:
            calendar_button(frame,values[key]).grid(
                row=row,column=2,sticky="w",padx=(5,0),pady=5
            )
        return widget

    field(basic,0,"personnel_no","Табельний номер")
    field(basic,1,"last_name","Прізвище")
    field(basic,2,"first_name","Ім'я")
    field(basic,3,"middle_name","По батькові")
    field(basic,4,"position","Основна посада")
    field(basic,5,"phone","Телефон")
    ttk.Label(
        basic,
        text="Телефон необов'язково; залиште порожнім, якщо контакт не потрібен.",
        foreground=PALETTE["muted"],
    ).grid(row=5,column=2,sticky="w",padx=(5,0),pady=5)
    field(basic,6,"gender","Стать для П-5")
    field(basic,7,"employment_date","Дата прийняття",True)
    field(basic,8,"dismissal_date","Дата звільнення",True)

    extra=ttk.LabelFrame(basic,text="Додаткова інформація",padding=8)
    extra.grid(row=9,column=0,columnspan=3,sticky="ew",pady=(10,0))
    extra.columnconfigure(1,weight=1)
    ttk.Label(extra,text="Оклад / тарифна ставка, грн").grid(
        row=0,column=0,sticky="w",padx=(0,8),pady=4
    )
    ttk.Entry(extra,textvariable=values["tariff_rate"]).grid(
        row=0,column=1,sticky="ew",pady=4
    )
    ttk.Label(extra,text="Примітка").grid(
        row=1,column=0,sticky="w",padx=(0,8),pady=4
    )
    ttk.Entry(extra,textvariable=values["notes"]).grid(
        row=1,column=1,sticky="ew",pady=4
    )

    side=ttk.Frame(body)
    side.grid(row=0,column=1,sticky="nsew",padx=(7,0))

    role_box=ttk.LabelFrame(side,text="Спеціальні ролі",padding=10)
    role_box.pack(fill="x")
    role_vars={}
    for i,role in enumerate(("Водій","Лікар","Механік","Диспетчер","Кондуктор","Інше")):
        role_vars[role]=tk.BooleanVar(value=role in current_roles)
        ttk.Checkbutton(
            role_box,text=role,variable=role_vars[role]
        ).grid(row=i//2,column=i%2,sticky="w",padx=6,pady=5)

    ttk.Label(
        role_box,
        text=(
            "Роль і статус працевлаштування не змішуються. "
            "Щоб завершити роль водія, зніміть «Водій» і збережіть картку."
        ),
        foreground=PALETTE["muted"],wraplength=330,justify="left"
    ).grid(row=3,column=0,columnspan=2,sticky="w",padx=6,pady=(8,3))

    driver_box=ttk.LabelFrame(side,text="Роль водія",padding=10)
    driver_box.pack(fill="x",pady=(10,0))
    if current_driver_end:
        ttk.Label(
            driver_box,
            text=f"Історична дата завершення: {fmt_date(current_driver_end)}",
            foreground=PALETTE["warning"],
            font=("TkDefaultFont",10,"bold"),
        ).pack(anchor="w")
    else:
        ttk.Label(
            driver_box,
            text="Дата завершення ролі зберігається окремо від звільнення.",
            foreground=PALETTE["muted"],wraplength=330,justify="left",
        ).pack(anchor="w")

    status_box=ttk.LabelFrame(side,text="Стан працівника",padding=10)
    status_box.pack(fill="x",pady=(10,0))
    active=tk.BooleanVar(value=bool(employee["active"]) if employee else True)
    ttk.Checkbutton(
        status_box,text="Працює",variable=active
    ).pack(anchor="w")
    ttk.Label(
        status_box,
        text=(
            "Зняття прапорця «Працює» означає звільнення працівника. "
            "Це не те саме, що зняти лише роль «Водій»."
        ),
        foreground=PALETTE["muted"],wraplength=330,justify="left",
    ).pack(anchor="w",pady=(6,0))

    quick=ttk.LabelFrame(side,text="Пов'язані дані",padding=10)
    quick.pack(fill="x",pady=(10,0))
    if employee:
        ttk.Button(
            quick,text="Відкрити табель персоналу",
            command=lambda:(win.destroy(),app.show_employee_timesheet())
        ).pack(fill="x",pady=3)
        ttk.Button(
            quick,text="Режим робочого часу…",
            command=lambda:(win.destroy(),app.show_employee_work_regime())
        ).pack(fill="x",pady=3)
    else:
        ttk.Label(
            quick,text="Після першого збереження стануть доступні табель і режим.",
            foreground=PALETTE["muted"],wraplength=320,justify="left"
        ).pack(anchor="w")

    def save():
        vals={k:v.get().strip() for k,v in values.items()}
        if not vals["last_name"] or not vals["first_name"]:
            messagebox.showerror(
                "Працівник","Прізвище та ім'я обов'язкові.",parent=win
            )
            return
        roles=[r for r,v in role_vars.items() if v.get()]
        closing_driver=bool(
            employee and employee["driver_id"]
            and "Водій" in current_roles and "Водій" not in roles
        )
        opening_driver=bool(
            "Водій" in roles
            and (not employee or "Водій" not in current_roles)
        )
        driver_end_date=""
        driver_start_date=""
        closing_driver_mode=""
        if closing_driver:
            choice=messagebox.askyesnocancel(
                "Завершити роль водія / виправити спадкову роль",
                "Це реальне завершення роботи водієм чи виправлення старої помилкової ролі?\n\n"
                "ТАК — працівник реально був водієм: зберегти історію та дату завершення.\n"
                "НІ — це спадщина старих версій, де всі були записані як водії: "
                "позначити роль як помилкову і не враховувати старий driver-графік у табелі.\n"
                "СКАСУВАТИ — нічого не змінювати.",
                parent=win,
            )
            if choice is None:
                return
            if choice:
                closing_driver_mode="finish"
                raw_end=simpledialog.askstring(
                    "Дата завершення ролі",
                    "Дата завершення роботи водієм (ДД.ММ.РРРР):",
                    initialvalue=date.today().strftime("%d.%m.%Y"),parent=win,
                )
                if raw_end is None:
                    return
                try:
                    driver_end_date=datetime.strptime(
                        raw_end.strip(),"%d.%m.%Y"
                    ).strftime("%Y-%m-%d")
                except ValueError:
                    messagebox.showerror(
                        "Працівник",
                        "Дата завершення ролі має бути у форматі ДД.ММ.РРРР.",
                        parent=win,
                    )
                    return
            else:
                closing_driver_mode="void"
        if opening_driver:
            if employee and employee["driver_id"]:
                raw_start=simpledialog.askstring(
                    "Початок ролі водія",
                    "Дата початку / відновлення реальної ролі водія (ДД.ММ.РРРР):",
                    initialvalue=date.today().strftime("%d.%m.%Y"),parent=win,
                )
                if raw_start is None:
                    return
                try:
                    driver_start_date=datetime.strptime(
                        raw_start.strip(),"%d.%m.%Y"
                    ).strftime("%Y-%m-%d")
                except ValueError:
                    messagebox.showerror(
                        "Працівник",
                        "Дата початку ролі має бути у форматі ДД.ММ.РРРР.",
                        parent=win,
                    )
                    return
            else:
                driver_start_date=vals.get("employment_date") or date.today().isoformat()
        for key in ("employment_date","dismissal_date"):
            if vals[key]:
                try:
                    vals[key]=datetime.strptime(
                        vals[key],"%d.%m.%Y"
                    ).strftime("%Y-%m-%d")
                except ValueError:
                    messagebox.showerror(
                        "Працівник","Дата має бути у форматі ДД.ММ.РРРР.",parent=win
                    )
                    return
        vals["gender"]=vals["gender"].lower()
        if vals["gender"] not in ("","ч","ж"):
            messagebox.showerror(
                "Працівник",
                "Стать для П-5: залиште порожньо або виберіть «ч» / «ж».",
                parent=win,
            )
            return
        tariff_rate=None
        if vals["tariff_rate"]:
            try:
                tariff_rate=float(vals["tariff_rate"].replace(",","."))
                if tariff_rate < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Працівник",
                    "Оклад / тарифна ставка мають бути невід'ємним числом.",
                    parent=win,
                )
                return
        con=db_factory()
        if vals["personnel_no"] and con.execute(
            "SELECT 1 FROM employees WHERE personnel_no=? AND id<>?",
            (vals["personnel_no"],employee["id"] if employee else -1)
        ).fetchone():
            con.close()
            messagebox.showerror(
                "Працівник","Такий табельний номер уже використовується.",parent=win
            )
            return
        driver_id=employee["driver_id"] if employee else None
        if "Водій" in roles and not driver_id:
            cur=con.execute(
                """INSERT INTO drivers(
                       last_name,first_name,middle_name,personnel_no,
                       employment_date,notes,active,created_at
                   ) VALUES(?,?,?,?,?,?,?,?)""",
                (
                    vals["last_name"],vals["first_name"],vals["middle_name"],
                    vals["personnel_no"],vals["employment_date"],vals["notes"],
                    0,datetime.now().isoformat(timespec="seconds"),
                ),
            )
            driver_id=cur.lastrowid
        if employee:
            eid=employee["id"]
            con.execute(
                """UPDATE employees SET
                       personnel_no=?,last_name=?,first_name=?,middle_name=?,
                       position=?,gender=?,tariff_rate=?,phone=?,
                       employment_date=?,dismissal_date=?,notes=?,active=?,driver_id=?
                   WHERE id=?""",
                (
                    vals["personnel_no"],vals["last_name"],vals["first_name"],
                    vals["middle_name"],vals["position"],vals["gender"],tariff_rate,
                    vals["phone"],vals["employment_date"],vals["dismissal_date"],
                    vals["notes"],int(active.get()),driver_id,eid,
                ),
            )
        else:
            cur=con.execute(
                """INSERT INTO employees(
                       personnel_no,last_name,first_name,middle_name,position,
                       gender,tariff_rate,phone,employment_date,dismissal_date,
                       notes,active,driver_id,created_at
                   ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    vals["personnel_no"],vals["last_name"],vals["first_name"],
                    vals["middle_name"],vals["position"],vals["gender"],tariff_rate,
                    vals["phone"],vals["employment_date"],vals["dismissal_date"],
                    vals["notes"],int(active.get()),driver_id,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            eid=cur.lastrowid
        con.execute("DELETE FROM employee_roles WHERE employee_id=?",(eid,))
        con.executemany(
            "INSERT INTO employee_roles(employee_id,role) VALUES(?,?)",
            [(eid,r) for r in roles],
        )
        if driver_id:
            driver_row=con.execute(
                "SELECT driver_end_date FROM drivers WHERE id=?",(driver_id,)
            ).fetchone()
            stored_driver_end=(
                (driver_row["driver_end_date"] if driver_row else "") or ""
            ).strip()
            if "Водій" in roles:
                next_driver_end=""
            elif closing_driver_mode=="finish":
                next_driver_end=driver_end_date
            elif closing_driver_mode=="void":
                next_driver_end=""
            else:
                next_driver_end=stored_driver_end
            driver_active=int(active.get() and "Водій" in roles)
            con.execute(
                """UPDATE drivers SET
                       last_name=?,first_name=?,middle_name=?,personnel_no=?,
                       employment_date=?,driver_end_date=?,notes=?,active=?
                   WHERE id=?""",
                (
                    vals["last_name"],vals["first_name"],vals["middle_name"],
                    vals["personnel_no"],vals["employment_date"],next_driver_end,
                    vals["notes"],driver_active,driver_id,
                ),
            )
            if closing_driver_mode=="finish":
                finish_driver_role(con,eid,driver_id,driver_end_date)
            elif closing_driver_mode=="void":
                void_legacy_driver_role(con,eid,driver_id)
            elif opening_driver:
                activate_driver_role(con,eid,driver_id,driver_start_date)
        con.commit()
        con.close()
        app.load_employee_registry()
        app.load_drivers()
        win.destroy()

    actions=ttk.Frame(win,padding=(14,4,14,12))
    actions.pack(fill="x")
    ttk.Button(actions,text="Закрити",command=win.destroy).pack(side="right",padx=(6,0))
    ttk.Button(
        actions,text="Зберегти",style="Accent.TButton",command=save
    ).pack(side="right")

def edit_employee(app):
    """Відкрити картку вибраного працівника."""
    row = app.selected_employee()
    if row:
        app.employee_form(row)


def toggle_employee_active(app, db_factory, finish_driver_role):
    """Звільнити або поновити працівника, не відновлюючи роль водія мовчки."""
    row = app.selected_employee()
    if not row:
        return

    new_state = 0 if row["active"] else 1
    today = date.today().isoformat()
    con = db_factory()
    con.execute(
        "UPDATE employees SET active=?,dismissal_date=CASE "
        "WHEN ?=0 AND COALESCE(dismissal_date,'')='' THEN ? "
        "WHEN ?=1 THEN '' ELSE dismissal_date END WHERE id=?",
        (new_state, new_state, today, new_state, row["id"]),
    )
    if row["driver_id"] and new_state == 0:
        # Звільнення завершує поточну роль водія. Поновлення працівника —
        # окрема дія і не повинно непомітно повертати роль водія.
        driver = con.execute(
            "SELECT active,driver_end_date FROM drivers WHERE id=?",
            (row["driver_id"],),
        ).fetchone()
        if driver and bool(driver["active"]):
            end_date = (driver["driver_end_date"] or "").strip() or today
            finish_driver_role(
                con,
                row["id"],
                row["driver_id"],
                end_date,
            )
    con.commit()
    con.close()
    app.load_employee_registry()
    app.load_drivers()

