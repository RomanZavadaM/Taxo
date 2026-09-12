# -*- coding: utf-8 -*-
"""Контрольний модуль аналогових тахографічних шайб.

Окрема SQLite-БД. Модуль НІКОЛИ не змінює основний графік,
табель або worklog. Результат вибіркової перевірки фіксується
тільки у протоколі контролю тахокарти.
"""
import math
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

try:
    from PIL import Image, ImageTk, ImageDraw
except ImportError:
    Image = ImageTk = ImageDraw = None


def _data_root():
    root = Path.home() / "Documents" / "DriverWorktime"
    (root / "Data").mkdir(parents=True, exist_ok=True)
    (root / "Data" / "TachographScans").mkdir(parents=True, exist_ok=True)
    return root

DATA_ROOT = _data_root()
TACHO_DB = DATA_ROOT / "Data" / "tachograph_test.sqlite3"
SCAN_DIR = DATA_ROOT / "Data" / "TachographScans"


def tdb():
    con = sqlite3.connect(TACHO_DB)
    con.row_factory = sqlite3.Row
    return con


def init_tacho_db():
    con = tdb()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS discs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_path TEXT NOT NULL,
        scan_name TEXT NOT NULL,
        disc_no INTEGER DEFAULT 1,
        driver_id INTEGER,
        vehicle_id INTEGER,
        disc_date TEXT DEFAULT '',
        cx REAL DEFAULT 0,
        cy REAL DEFAULT 0,
        radius REAL DEFAULT 0,
        rotation_deg REAL DEFAULT 0,
        status TEXT DEFAULT 'Новий',
        notes TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS intervals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disc_id INTEGER NOT NULL REFERENCES discs(id) ON DELETE CASCADE,
        start_min INTEGER NOT NULL,
        end_min INTEGER NOT NULL,
        activity TEXT NOT NULL,
        confidence REAL DEFAULT 0,
        source TEXT DEFAULT 'auto',
        note TEXT DEFAULT ''
    );
    CREATE INDEX IF NOT EXISTS idx_intervals_disc ON intervals(disc_id);

    CREATE TABLE IF NOT EXISTS control_protocols (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disc_id INTEGER NOT NULL REFERENCES discs(id) ON DELETE CASCADE,
        driver_id INTEGER,
        vehicle_id INTEGER,
        disc_date TEXT DEFAULT '',
        scan_name TEXT DEFAULT '',
        interval_count INTEGER DEFAULT 0,
        driving_min INTEGER DEFAULT 0,
        other_work_min INTEGER DEFAULT 0,
        rest_min INTEGER DEFAULT 0,
        availability_min INTEGER DEFAULT 0,
        undefined_min INTEGER DEFAULT 0,
        max_speed_est INTEGER,
        status TEXT DEFAULT 'Контрольний протокол',
        snapshot_text TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_control_protocols_disc
        ON control_protocols(disc_id);
    """)
    con.commit(); con.close()


def detect_discs(path):
    """Швидке визначення круглих шайб. Результат — кандидати (x,y,r)."""
    if cv2 is None:
        return []
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return []
    h, w = img.shape[:2]
    scale = 0.4 if max(h, w) > 1600 else 0.6
    small = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    small = cv2.medianBlur(small, 5)
    min_r = int(min(h, w) * 0.17 * scale)
    max_r = int(min(h, w) * 0.30 * scale)
    circles = cv2.HoughCircles(small, cv2.HOUGH_GRADIENT, dp=1.4, minDist=max(120, int(min(h,w)*0.16*scale)),
                               param1=120, param2=45, minRadius=min_r, maxRadius=max_r)
    if circles is None:
        return []
    cand = []
    for x, y, r in np.round(circles[0]).astype(int):
        cand.append((x/scale, y/scale, r/scale))
    # Відсіюємо дублікати/хибні кола та залишаємо найбільш реалістичні розміри.
    cand.sort(key=lambda z: abs(z[2] - min(h,w)*0.285))
    selected=[]
    for c in cand:
        if c[2] < min(h,w)*0.20 or c[2] > min(h,w)*0.32:
            continue
        if any(math.hypot(c[0]-s[0], c[1]-s[1]) < min(c[2],s[2])*1.25 for s in selected):
            continue
        selected.append(c)
    return selected


def _polar_signal(path, cx, cy, radius, rotation_deg=0):
    """Чернеткова оцінка темних слідів у внутрішній зоні шайби.
    Не є юридичною автоматичною інтерпретацією: повертає кандидати для перевірки людиною.
    """
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None: return []
    n = 1440
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    # Беремо кілька вузьких радіальних кілець у зоні записів активності.
    rs = np.linspace(radius*0.42, radius*0.63, 24)
    xx=[]; yy=[]
    for rr in rs:
        a = angles + math.radians(rotation_deg)
        xx.append(cx + rr*np.cos(a)); yy.append(cy + rr*np.sin(a))
    mapx=np.array(xx,dtype=np.float32); mapy=np.array(yy,dtype=np.float32)
    vals=cv2.remap(img,mapx,mapy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=255)
    # Для кожного кута рахуємо частку темних пікселів; приглушуємо паперову сітку.
    darkness=(vals<135).mean(axis=0)
    smooth=cv2.GaussianBlur(darkness.reshape(1,-1),(1,0),0).ravel()
    # Порогова кластеризація. Це лише кандидати.
    mask=smooth>max(0.13, float(np.percentile(smooth,72))*0.78)
    runs=[]; start=None
    for i,v in enumerate(np.r_[mask,mask[:1]]):
        if v and start is None: start=i
        if not v and start is not None:
            end=i
            if end-start>=8: runs.append((start,end))
            start=None
    if runs and runs[0][0]==0 and runs[-1][1]>=n:
        runs=[(runs[-1][0], runs[0][1]+n)]
    out=[]
    for a,b in runs:
        if b-a>500: continue
        sm=(a/n*1440 + rotation_deg/360*1440) % 1440
        em=(b/n*1440 + rotation_deg/360*1440) % 1440
        # Чернеткове віднесення: темніший/щільніший слід в цій зоні позначаємо як "Керування".
        # Інші періоди користувач підтверджує/змінює вручну.
        if em <= sm: em += 1440
        out.append((int(sm)%1440, int(em)%1440, "Керування", round(float(smooth[a:b].mean()),2)))
    return out


def estimate_max_speed(path, cx, cy, radius, rotation_deg=0):
    """Технічна приблизна оцінка максимальної швидкості зі сліду.
    Це не юридичний висновок; значення потребує перевірки оператором.
    """
    if cv2 is None or radius <= 0:
        return None
    img=cv2.imread(str(path),cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    rings=np.linspace(radius*0.60, radius*0.88, 60)
    angles=np.linspace(0, 2*np.pi, 720, endpoint=False) + math.radians(rotation_deg)
    best=None
    for rr in rings:
        x=(cx+rr*np.cos(angles)).astype(np.float32)
        y=(cy+rr*np.sin(angles)).astype(np.float32)
        vals=cv2.remap(img,x.reshape(1,-1),y.reshape(1,-1),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=255).ravel()
        score=float((vals<110).mean())
        if best is None or score>best[0]:
            best=(score,rr)
    if best is None or best[0] < 0.025:
        return None
    kmh=(best[1]/radius-0.60)/(0.88-0.60)*125.0
    return int(round(max(0.0,min(125.0,kmh))))


class TachographModule:
    def __init__(self, parent, drivers_provider=None, vehicles_provider=None, send_callback=None):
        self.parent=parent
        self.drivers_provider=drivers_provider
        self.vehicles_provider=vehicles_provider
        # send_callback лишено тільки для сумісності старого виклику.
        # Навіть якщо його передадуть, модуль v8.53 його не викликає.
        self.send_callback=None
        self.driver_map={}
        self.vehicle_map={}
        # parent вже є вкладкою Notebook; будуємо інтерфейс безпосередньо в ній.
        self.tab=parent
        self.current_id=None
        self.photo=None
        init_tacho_db()
        self.build()
        self.load()

    def build(self):
        top=ttk.Frame(self.tab); top.pack(fill="x",padx=10,pady=8)
        ttk.Button(top,text="Імпортувати скан",command=self.import_scan).pack(side="left",padx=3)
        ttk.Button(top,text="Розпізнати шайбу",command=self.recognize_selected).pack(side="left",padx=3)
        ttk.Button(top,text="Розпізнати всі",command=self.recognize_all).pack(side="left",padx=3)
        ttk.Button(top,text="Відкрити скан",command=self.open_scan).pack(side="left",padx=3)
        ttk.Button(top,text="Видалити тест",command=self.delete_selected).pack(side="left",padx=3)
        ttk.Button(top,text="Оновити",command=self.load).pack(side="left",padx=3)
        ttk.Label(
            top,
            text="КОНТРОЛЬНИЙ режим: тахокарта не змінює графік/табель",
            foreground="gray"
        ).pack(side="right")
        ttk.Label(self.tab,text="Тестовий модуль аналогових шайб. Оберіть запис зліва або імпортуйте свій скан.",foreground="gray").pack_forget()

        pan=ttk.Panedwindow(self.tab,orient="horizontal"); pan.pack(fill="both",expand=True,padx=10,pady=5)
        left=ttk.Frame(pan); right=ttk.Frame(pan); pan.add(left,weight=1); pan.add(right,weight=2)
        cols=("id","name","disc","date","status")
        self.tree=ttk.Treeview(left,columns=cols,show="headings",selectmode="browse")
        heads={"id":"ID","name":"Скан","disc":"Шайба","date":"Дата","status":"Стан"}
        for c in cols:
            self.tree.heading(c,text=heads[c]); self.tree.column(c,width=80 if c in ("id","disc") else 150)
        left_y=ttk.Scrollbar(left,orient="vertical",command=self.tree.yview)
        left_x=ttk.Scrollbar(left,orient="horizontal",command=self.tree.xview)
        self.tree.configure(yscrollcommand=left_y.set,xscrollcommand=left_x.set)
        left_y.pack(side="right",fill="y")
        left_x.pack(side="bottom",fill="x")
        self.tree.pack(side="left",fill="both",expand=True); self.tree.bind("<<TreeviewSelect>>",lambda e:self.select())

        # Верхня панель даних має залишатися видимою при виборі будь-якої шайби.
        # Не поміщаємо її в область зображення, яка розтягується.
        meta=ttk.LabelFrame(right,text="Дані шайби")
        meta.pack(side="top",fill="x",pady=(0,5))
        meta.pack_propagate(True)
        self.v_driver=tk.StringVar(); self.v_vehicle=tk.StringVar(); self.v_date=tk.StringVar(); self.v_rot=tk.StringVar(value="0")
        ttk.Label(meta,text="Водій").grid(row=0,column=0,sticky="w",padx=6,pady=4)
        self.driver_cb=ttk.Combobox(meta,textvariable=self.v_driver,state="readonly",width=42); self.driver_cb.grid(row=0,column=1,sticky="w",padx=6,pady=4)
        ttk.Label(meta,text="Автомобіль").grid(row=1,column=0,sticky="w",padx=6,pady=4)
        self.vehicle_cb=ttk.Combobox(meta,textvariable=self.v_vehicle,state="readonly",width=42); self.vehicle_cb.grid(row=1,column=1,sticky="w",padx=6,pady=4)
        ttk.Label(meta,text="Дата шайби (ДД.ММ.РРРР)").grid(row=2,column=0,sticky="w",padx=6,pady=4)
        ttk.Entry(meta,textvariable=self.v_date,width=25).grid(row=2,column=1,sticky="w",padx=6,pady=4)
        ttk.Label(meta,text="Поворот 0 год, °").grid(row=3,column=0,sticky="w",padx=6,pady=4)
        ttk.Entry(meta,textvariable=self.v_rot,width=12).grid(row=3,column=1,sticky="w",padx=6,pady=4)
        ttk.Button(meta,text="Зберегти дані / поворот",command=self.save_meta).grid(row=3,column=2,padx=6,pady=4)
        self.refresh_catalogs()

        # Нижня частина окремо розділяє зображення та результати розпізнавання.
        # Великий скан більше не може “витиснути” поля даних шайби.
        body=ttk.Panedwindow(right,orient="vertical")
        body.pack(fill="both",expand=True,pady=5)
        image_frame=ttk.Frame(body)
        result_frame=ttk.Frame(body)
        body.add(image_frame,weight=3)
        body.add(result_frame,weight=1)

        image_wrap=ttk.Frame(image_frame)
        image_wrap.pack(fill="both",expand=True)
        self.image_canvas=tk.Canvas(image_wrap,background="white",highlightthickness=1)
        self.image_vbar=ttk.Scrollbar(image_wrap,orient="vertical",command=self.image_canvas.yview)
        self.image_hbar=ttk.Scrollbar(image_wrap,orient="horizontal",command=self.image_canvas.xview)
        self.image_canvas.configure(yscrollcommand=self.image_vbar.set,xscrollcommand=self.image_hbar.set)
        self.image_vbar.pack(side="right",fill="y")
        self.image_hbar.pack(side="bottom",fill="x")
        self.image_canvas.pack(side="left",fill="both",expand=True)
        self.image_canvas.create_text(20,20,anchor="nw",text="Оберіть скан",fill="gray")

        timeline_box=ttk.LabelFrame(image_frame,text="24-годинна шкала розпізнаних періодів")
        timeline_box.pack(fill="x",pady=(6,0))
        self.timeline_canvas=tk.Canvas(timeline_box,height=115,background="white",highlightthickness=1)
        self.timeline_canvas.pack(fill="x",padx=4,pady=4)
        self.timeline_canvas.bind("<Double-1>",self._timeline_double_click)
        self.timeline_hint=tk.StringVar(value="Оберіть шайбу")
        ttk.Label(timeline_box,textvariable=self.timeline_hint,foreground="gray").pack(anchor="w",padx=6,pady=(0,4))

        ib=ttk.Frame(result_frame); ib.pack(fill="x")
        self.candidate_var=tk.StringVar(value="Кандидатів: 0")
        ttk.Label(ib,textvariable=self.candidate_var,foreground="gray").pack(side="left",padx=(0,10))
        ttk.Button(ib,text="Розпізнати / оновити",command=self.recognize_selected).pack(side="left",padx=3)
        ttk.Button(ib,text="Додати інтервал",command=self.add_interval).pack(side="left",padx=3)
        ttk.Button(ib,text="Редагувати",command=self.edit_interval).pack(side="left",padx=3)
        ttk.Button(ib,text="Видалити",command=self.delete_interval).pack(side="left",padx=3)
        ttk.Button(
            ib,text="Протоколи контролю",command=self.show_control_protocols
        ).pack(side="right",padx=3)
        ttk.Button(
            ib,text="Зберегти протокол контролю",command=self.save_control_protocol
        ).pack(side="right",padx=3)
        icols=("id","start","end","activity","confidence","source")
        itree_wrap=ttk.Frame(result_frame)
        itree_wrap.pack(fill="both",expand=True,pady=5)
        self.itree=ttk.Treeview(itree_wrap,columns=icols,show="headings",height=6)
        ih={"id":"ID","start":"Початок","end":"Кінець","activity":"Активність","confidence":"Впевненість","source":"Джерело"}
        for c in icols:
            self.itree.heading(c,text=ih[c]); self.itree.column(c,width=85 if c in ("id","confidence") else 120)
        itree_y=ttk.Scrollbar(itree_wrap,orient="vertical",command=self.itree.yview)
        itree_x=ttk.Scrollbar(itree_wrap,orient="horizontal",command=self.itree.xview)
        self.itree.configure(yscrollcommand=itree_y.set,xscrollcommand=itree_x.set)
        self.itree.grid(row=0,column=0,sticky="nsew")
        itree_y.grid(row=0,column=1,sticky="ns")
        itree_x.grid(row=1,column=0,sticky="ew")
        itree_wrap.rowconfigure(0,weight=1); itree_wrap.columnconfigure(0,weight=1)
        ttk.Label(
            result_frame,
            text=(
                "Автоматичне розпізнавання — лише чернетка. Перевірте/відредагуйте інтервали "
                "і збережіть «Протокол контролю». Основний графік та табель не змінюються."
            ),
            foreground="gray",wraplength=760
        ).pack(anchor="w")

        self.stats_var=tk.StringVar(value="Оберіть шайбу")

    def refresh_catalogs(self):
        if self.drivers_provider:
            self.driver_map={}
            vals=[]
            for r in self.drivers_provider() or []:
                name=" ".join(x for x in (r["last_name"],r["first_name"],r["middle_name"]) if x)
                self.driver_map[name]=r["id"]; vals.append(name)
            self.driver_cb["values"]=vals
        if self.vehicles_provider:
            self.vehicle_map={}
            vals=[]
            for r in self.vehicles_provider() or []:
                name=r["name"] if not r["plate"] else f"{r['name']} [{r['plate']}]"
                self.vehicle_map[name]=r["id"]; vals.append(name)
            self.vehicle_cb["values"]=vals

    def _selected(self):
        s=self.tree.selection()
        if not s: return None
        return tdb().execute("SELECT * FROM discs WHERE id=?",(self.tree.item(s[0],"values")[0],)).fetchone()

    def load(self):
        for x in self.tree.get_children(): self.tree.delete(x)
        con=tdb(); rows=con.execute("SELECT * FROM discs ORDER BY id DESC").fetchall(); con.close()
        for r in rows: self.tree.insert("","end",values=(r["id"],r["scan_name"],r["disc_no"],r["disc_date"],r["status"]))

    def select(self):
        r=self._selected()
        if not r:return
        self.current_id=r["id"]; self.v_date.set(self.fdate(r["disc_date"] or "")); self.v_rot.set(str(r["rotation_deg"] or 0))
        self.refresh_catalogs()
        did=r["driver_id"]; vid=r["vehicle_id"]
        self.v_driver.set(next((k for k,v in self.driver_map.items() if str(v)==str(did)), ""))
        self.v_vehicle.set(next((k for k,v in self.vehicle_map.items() if str(v)==str(vid)), ""))
        self.show_image(r)
        self.load_intervals()
        # Старі тестові записи могли мати статус «Розпізнано», але не містити
        # рядків інтервалів. У такому разі одразу добудовуємо кандидати.
        if r["radius"] and not self.itree.get_children():
            try:
                items=_polar_signal(r["source_path"],r["cx"],r["cy"],r["radius"],float(r["rotation_deg"] or 0))
                con=tdb(); con.execute("DELETE FROM intervals WHERE disc_id=?",(r["id"],))
                for a,b,act,conf in items:
                    con.execute("INSERT INTO intervals(disc_id,start_min,end_min,activity,confidence,source) VALUES(?,?,?,?,?,?)",(r["id"],a,b,act,conf,"auto"))
                con.execute("UPDATE discs SET status=? WHERE id=?",(f"Розпізнано — {len(items)} кандидатів",r["id"]))
                con.commit(); con.close()
                self.load_intervals()
            except Exception:
                pass
        self.candidate_var.set(f"Кандидатів: {len(self.itree.get_children())}")
        if hasattr(self,"stats_var"): self.update_stats()

    def show_image(self,r):
        if Image is None: return
        try:
            im=Image.open(r["source_path"]).convert("RGB")
            # Не зменшуємо скан до фіксованої області: для великих сканів
            # користувач отримує вертикальну і горизонтальну прокрутку.
            draw=ImageDraw.Draw(im)
            if r["cx"] and r["radius"]:
                draw.ellipse((r["cx"]-r["radius"],r["cy"]-r["radius"],
                              r["cx"]+r["radius"],r["cy"]+r["radius"]),
                             outline=(220,30,30),width=max(3,int(r["radius"]*0.01)))
            self.photo=ImageTk.PhotoImage(im)
            self.image_canvas.delete("all")
            self.image_canvas.create_image(0,0,anchor="nw",image=self.photo)
            self.image_canvas.configure(scrollregion=(0,0,im.width,im.height))
            # Починаємо з верхнього лівого кута; нижче можна вільно рухатись
            # обома бігунками, коли на скані декілька шайб.
            self.image_canvas.xview_moveto(0)
            self.image_canvas.yview_moveto(0)
        except Exception as e:
            self.image_canvas.delete("all")
            self.image_canvas.create_text(20,20,anchor="nw",text=str(e),fill="red")

    def import_scan(self):
        paths=filedialog.askopenfilenames(parent=self.parent,title="Виберіть скани шайб",filetypes=[("Зображення","*.jpg *.jpeg *.png *.bmp"),("Усі файли","*.*")])
        if not paths:return
        for p in paths:
            self._import_one(Path(p))
        self.load()
        self.recognize_all()

    def _import_one(self,p):
        dest=SCAN_DIR/f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{p.name}"
        shutil.copy2(p,dest)
        circles=detect_discs(dest)
        con=tdb()
        if not circles: circles=[(0,0,0)]
        for i,(cx,cy,r) in enumerate(circles,1):
            con.execute("INSERT INTO discs(source_path,scan_name,disc_no,cx,cy,radius,created_at) VALUES(?,?,?,?,?,?,?)",(str(dest),p.name,i,cx,cy,r,datetime.now().isoformat(timespec="seconds")))
        con.commit();con.close()
        if not circles: messagebox.showwarning("Шайба",f"Не вдалося автоматично знайти коло у {p.name}. Її можна буде налаштувати вручну.",parent=self.parent)

    def recognize_all(self, silent=False):
        rows=tdb().execute("SELECT * FROM discs WHERE radius IS NOT NULL AND radius>0 ORDER BY id").fetchall()
        if not rows:
            messagebox.showwarning("Розпізнавання","Немає шайб із знайденим колом.",parent=self.parent); return
        total=0
        con=tdb()
        for r in rows:
            rot=float(r["rotation_deg"] or 0)
            items=_polar_signal(r["source_path"],r["cx"],r["cy"],r["radius"],rot)
            con.execute("DELETE FROM intervals WHERE disc_id=?",(r["id"],))
            for a,b,act,conf in items:
                con.execute("INSERT INTO intervals(disc_id,start_min,end_min,activity,confidence,source) VALUES(?,?,?,?,?,?)",(r["id"],a,b,act,conf,"auto"))
            con.execute("UPDATE discs SET status=? WHERE id=?",(f"Розпізнано — {len(items)} кандидатів",r["id"]))
            total += len(items)
        con.commit(); con.close(); self.load();
        if not silent:
            messagebox.showinfo("Розпізнавання",f"Оброблено шайб: {len(rows)}. Створено кандидатів інтервалів: {total}.\n\nЦе попереднє розпізнавання: результати потрібно перевірити по зображенню.",parent=self.parent)

    def recognize_selected(self):
        r=self._selected()
        if not r:return
        if not r["radius"]: messagebox.showwarning("Розпізнавання","Для цієї шайби не знайдено коло.",parent=self.parent);return
        try: rot=float(self.v_rot.get().replace(",","."))
        except: rot=0
        items=_polar_signal(r["source_path"],r["cx"],r["cy"],r["radius"],rot)
        con=tdb(); con.execute("DELETE FROM intervals WHERE disc_id=?",(r["id"],))
        for a,b,act,conf in items: con.execute("INSERT INTO intervals(disc_id,start_min,end_min,activity,confidence,source) VALUES(?,?,?,?,?,?)",(r["id"],a,b,act,conf,"auto"))
        con.execute("UPDATE discs SET rotation_deg=?,status=? WHERE id=?",(rot,"Розпізнано — перевірити",r["id"])); con.commit();con.close()
        self.select()
        messagebox.showinfo("Розпізнавання",f"Створено кандидатів інтервалів: {len(items)}. Це чернетка, її потрібно перевірити по зображенню.",parent=self.parent)

    def save_meta(self):
        if not self.current_id:return
        try: rot=float(self.v_rot.get().replace(",","."))
        except: messagebox.showerror("Помилка","Поворот має бути числом.",parent=self.parent);return
        did=self.driver_map.get(self.v_driver.get()) or None; vid=self.vehicle_map.get(self.v_vehicle.get()) or None
        try: disc_date=self.pdate(self.v_date.get()) if self.v_date.get().strip() else ""
        except ValueError:
            messagebox.showerror("Помилка","Дата шайби має бути у форматі ДД.ММ.РРРР.",parent=self.parent); return
        con=tdb(); con.execute("UPDATE discs SET driver_id=?,vehicle_id=?,disc_date=?,rotation_deg=? WHERE id=?",(did,vid,disc_date,rot,self.current_id)); con.commit();con.close();self.load();self.select()

    def load_intervals(self):
        for x in self.itree.get_children(): self.itree.delete(x)
        if not self.current_id:return
        con=tdb(); rows=con.execute("SELECT * FROM intervals WHERE disc_id=? ORDER BY start_min",(self.current_id,)).fetchall(); con.close()
        for r in rows:self.itree.insert("","end",values=(r["id"],self.fm(r["start_min"]),self.fm(r["end_min"]),r["activity"],r["confidence"],r["source"]))
        if hasattr(self,"candidate_var"):
            self.candidate_var.set(f"Кандидатів: {len(rows)}")
        if hasattr(self,"stats_var"): self.update_stats()
        self.draw_timeline(rows)

    @staticmethod
    def fm(m): return f"{(int(m)%1440)//60:02d}:{int(m)%60:02d}"

    @staticmethod
    def fdate(s):
        if not s: return ""
        try: return datetime.strptime(s, "%Y-%m-%d").strftime("%d.%m.%Y")
        except ValueError: return s

    @staticmethod
    def pdate(s):
        return datetime.strptime(s.strip(), "%d.%m.%Y").date().isoformat()
    @staticmethod
    def parse(t):
        h,m=map(int,t.strip().split(":")); return h*60+m


    def update_stats(self):
        if not hasattr(self,"stats_var"):
            return "Оберіть шайбу"
        if not self.current_id:
            self.stats_var.set("Оберіть шайбу")
            return "Оберіть шайбу"
        r=self._selected()
        if not r:
            self.stats_var.set("Оберіть шайбу")
            return "Оберіть шайбу"
        rows=tdb().execute("SELECT * FROM intervals WHERE disc_id=? ORDER BY start_min",(self.current_id,)).fetchall()
        totals={"Керування":0,"Інша робота":0,"Відпочинок":0,"Готовність":0,"Невизначено":0}
        for x in rows:
            dur=(int(x["end_min"])-int(x["start_min"]))%1440
            totals[x["activity"]]=totals.get(x["activity"],0)+dur
        def hh(mm): return f"{mm//60} год {mm%60:02d} хв"
        max_speed=estimate_max_speed(r["source_path"],r["cx"],r["cy"],r["radius"],float(r["rotation_deg"] or 0)) if r["radius"] else None
        max_txt=f"{max_speed} км/год (орієнтовно)" if max_speed is not None else "не визначено"
        msg=(f"Кандидатів/інтервалів: {len(rows)}\n"
             f"Час керування: {hh(totals.get('Керування',0))}\n"
             f"Інша робота: {hh(totals.get('Інша робота',0))}\n"
             f"Відпочинок: {hh(totals.get('Відпочинок',0))}\n"
             f"Готовність: {hh(totals.get('Готовність',0))}\n"
             f"Невизначено: {hh(totals.get('Невизначено',0))}\n"
             f"Максимальна швидкість: {max_txt}\n"
             f"Стан шайби: {r['status']}")
        self.stats_var.set(msg)
        return msg

    def show_stats_popup(self):
        msg = self.update_stats()
        win = tk.Toplevel(self.parent)
        win.title("Підсумкова статистика тахокарти")
        win.geometry("560x390")
        win.transient(self.parent)
        win.resizable(True, True)

        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)
        ttk.Label(
            frame,
            text="Підсумкова статистика шайби",
            font=("TkDefaultFont", 11, "bold")
        ).pack(anchor="w", pady=(0, 10))

        txt = tk.Text(frame, wrap="word", height=14, width=60)
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", str(msg or "Немає даних для статистики."))
        txt.configure(state="disabled")

        ttk.Button(frame, text="Закрити", command=win.destroy).pack(
            anchor="e", pady=(10, 0)
        )

    @staticmethod
    def _activity_style(activity):
        # Візуальні позначення лише для орієнтації оператора.
        return {
            "Керування": ("#d9ecff", "#1f4e79"),
            "Інша робота": ("#fff0c2", "#7a5200"),
            "Відпочинок": ("#dff3df", "#2f6b2f"),
            "Готовність": ("#eadcf8", "#5d3f7d"),
            "Невизначено": ("#f0f0f0", "#555555"),
        }.get(activity, ("#ececec", "#555555"))

    def draw_timeline(self, rows=None):
        if not hasattr(self, "timeline_canvas"):
            return
        c=self.timeline_canvas
        c.delete("all")
        width=max(720, c.winfo_width())
        if width < 100:
            width=900
        height=115
        left=42
        right=16
        top=24
        bottom=26
        usable=max(100,width-left-right)
        axis_y=top+32
        c.create_text(left, 10, anchor="w", text="00:00")
        for h in range(25):
            x=left + usable*h/24
            c.create_line(x, axis_y-8, x, axis_y+8, fill="#888888")
            if h < 24:
                label=f"{h:02d}"
                c.create_text(x, axis_y+18, anchor="n", text=label, fill="#555555")
        c.create_line(left,axis_y,left+usable,axis_y,fill="#555555",width=2)

        if rows is None and getattr(self,"current_id",None):
            rows=tdb().execute(
                "SELECT * FROM intervals WHERE disc_id=? ORDER BY start_min",
                (self.current_id,)
            ).fetchall()
        rows=rows or []

        if not self.current_id:
            c.create_text(width/2, 66, text="Оберіть шайбу", fill="#888888")
            self.timeline_hint.set("Оберіть шайбу")
            return

        # Two visual lanes: the first for activity, the second for overlaps/conflicts.
        lane_top=axis_y-3
        lane_h=18
        drawn=0
        for r in rows:
            start=int(r["start_min"]) % 1440
            end=int(r["end_min"]) % 1440
            if end == start:
                end = start + 1
            segments=[(start,min(end,1440))]
            if end > 1440:
                segments.append((0,end-1440))
            fill, outline=self._activity_style(r["activity"])
            for a,b in segments:
                x1=left + usable*a/1440
                x2=left + usable*b/1440
                if x2-x1 < 2:
                    x2=x1+2
                c.create_rectangle(x1,lane_top,x2,lane_top+lane_h,fill=fill,outline=outline)
                if x2-x1 >= 42:
                    c.create_text((x1+x2)/2,lane_top+lane_h/2,text=r["activity"],fill=outline,font=("TkDefaultFont",8))
            drawn += 1

        legend_y=94
        x=left
        seen=[]
        for r in rows:
            act=r["activity"]
            if act in seen: continue
            seen.append(act)
            fill, outline=self._activity_style(act)
            c.create_rectangle(x,legend_y,x+14,legend_y+12,fill=fill,outline=outline)
            c.create_text(x+18,legend_y+6,anchor="w",text=act,fill=outline,font=("TkDefaultFont",8))
            x += 110 + len(act)*3
            if x > width-120: break

        self.timeline_hint.set(
            f"Періодів: {len(rows)}. Подвійний клік по шкалі — відкрити редактор інтервалу."
        )

    def _timeline_double_click(self, event):
        if not self.current_id:
            return
        rows=tdb().execute(
            "SELECT * FROM intervals WHERE disc_id=? ORDER BY start_min",
            (self.current_id,)
        ).fetchall()
        if not rows:
            return
        width=max(720, self.timeline_canvas.winfo_width())
        left=42
        right=16
        usable=max(100,width-left-right)
        minute=int(round((event.x-left)*1440/usable))
        minute=max(0,min(1439,minute))
        chosen=None
        for r in rows:
            s=int(r["start_min"])%1440
            e=int(r["end_min"])%1440
            if e <= s: e += 1440
            m=minute if minute >= s else minute+1440
            if s <= m <= e:
                chosen=r
                break
        if chosen:
            self.interval_form(chosen)

    def add_interval(self): self.interval_form()
    def edit_interval(self):
        s=self.itree.selection()
        if s:
            rid=int(self.itree.item(s[0],"values")[0]); con=tdb();r=con.execute("SELECT * FROM intervals WHERE id=?",(rid,)).fetchone();con.close();self.interval_form(r)
    def interval_form(self,r=None):
        if not self.current_id:return
        w=tk.Toplevel(self.parent);w.title("Інтервал шайби");w.geometry("460x300");w.transient(self.parent);w.grab_set()
        sv=tk.StringVar(value=self.fm(r["start_min"]) if r else "08:00");ev=tk.StringVar(value=self.fm(r["end_min"]) if r else "17:00");av=tk.StringVar(value=r["activity"] if r else "Керування");nv=tk.StringVar(value=r["note"] if r else "")
        for i,(lab,var) in enumerate((("Початок",sv),("Кінець",ev),("Активність",av),("Примітка",nv))):
            ttk.Label(w,text=lab).grid(row=i,column=0,sticky="w",padx=10,pady=8)
            if lab=="Активність": ttk.Combobox(w,textvariable=var,state="readonly",values=("Керування","Інша робота","Відпочинок","Готовність","Невизначено"),width=28).grid(row=i,column=1,padx=10,pady=8)
            else: ttk.Entry(w,textvariable=var,width=32).grid(row=i,column=1,padx=10,pady=8)
        def save():
            try:a=self.parse(sv.get());b=self.parse(ev.get())
            except:messagebox.showerror("Помилка","Час у форматі ГГ:ХХ",parent=w);return
            if r:
                rid=r["id"];con=tdb();con.execute("UPDATE intervals SET start_min=?,end_min=?,activity=?,source='manual',note=? WHERE id=?",(a,b,av.get(),nv.get(),rid))
            else:
                con=tdb();con.execute("INSERT INTO intervals(disc_id,start_min,end_min,activity,confidence,source,note) VALUES(?,?,?,?,?,?,?)",(self.current_id,a,b,av.get(),1.0,"manual",nv.get()))
            con.commit();con.close();w.destroy();self.load_intervals()
        ttk.Button(w,text="Зберегти",command=save).grid(row=5,column=1,sticky="e",padx=10,pady=12)

    def delete_interval(self):
        s=self.itree.selection()
        if not s:return
        rid=int(self.itree.item(s[0],"values")[0]);con=tdb();con.execute("DELETE FROM intervals WHERE id=?",(rid,));con.commit();con.close();self.load_intervals()

    def delete_selected(self):
        r=self._selected()
        if not r:return
        if not messagebox.askyesno("Підтвердження","Видалити цей тестовий запис?",parent=self.parent):return
        con=tdb();con.execute("DELETE FROM discs WHERE id=?",(r["id"],));con.commit();con.close();self.current_id=None;self.load()

    def open_scan(self):
        """Відкрити скан в окремому вікні, не замінюючи поле розпізнавання."""
        r=self._selected()
        if not r:return
        if Image is None:
            try: os.startfile(r["source_path"])
            except Exception: pass
            return
        try:
            win=tk.Toplevel(self.parent)
            win.title(f"Скан шайби — {r['scan_name']} №{r['disc_no']}")
            win.geometry("1000x800")
            win.transient(self.parent)
            outer=ttk.Frame(win); outer.pack(fill="both",expand=True,padx=8,pady=8)
            canvas=tk.Canvas(outer,background="white")
            vs=ttk.Scrollbar(outer,orient="vertical",command=canvas.yview)
            hs=ttk.Scrollbar(outer,orient="horizontal",command=canvas.xview)
            canvas.configure(yscrollcommand=vs.set,xscrollcommand=hs.set)
            vs.pack(side="right",fill="y"); hs.pack(side="bottom",fill="x"); canvas.pack(side="left",fill="both",expand=True)
            im=Image.open(r["source_path"]).convert("RGB")
            draw=ImageDraw.Draw(im)
            if r["cx"] and r["radius"]:
                draw.ellipse((r["cx"]-r["radius"],r["cy"]-r["radius"],r["cx"]+r["radius"],r["cy"]+r["radius"]),outline=(220,30,30),width=max(3,int(r["radius"]*0.01)))
            photo=ImageTk.PhotoImage(im)
            canvas.create_image(0,0,anchor="nw",image=photo)
            canvas.configure(scrollregion=(0,0,im.width,im.height))
            canvas.image=photo
            ttk.Button(win,text="Закрити",command=win.destroy).pack(pady=(0,6))
        except Exception as e:
            messagebox.showerror("Скан",str(e),parent=self.parent)

    @staticmethod
    def _duration_minutes(row):
        start=int(row["start_min"])
        end=int(row["end_min"])
        dur=(end-start)%1440
        return dur if dur else 0

    def _protocol_snapshot(self, disc_row, rows):
        totals={
            "Керування":0,
            "Інша робота":0,
            "Відпочинок":0,
            "Готовність":0,
            "Невизначено":0,
        }
        lines=[]
        for x in rows:
            dur=self._duration_minutes(x)
            totals[x["activity"]]=totals.get(x["activity"],0)+dur
            lines.append(
                f"{self.fm(x['start_min'])}–{self.fm(x['end_min'])} | "
                f"{x['activity']} | {dur//60}:{dur%60:02d} | "
                f"джерело: {x['source']} | впевненість: {x['confidence']}"
            )

        max_speed=estimate_max_speed(
            disc_row["source_path"],disc_row["cx"],disc_row["cy"],
            disc_row["radius"],float(disc_row["rotation_deg"] or 0)
        ) if disc_row["radius"] else None

        driver_name=self.v_driver.get().strip()
        vehicle_name=self.v_vehicle.get().strip()
        disc_date=self.v_date.get().strip()

        header=[
            "ПРОТОКОЛ КОНТРОЛЮ ТАХОКАРТИ",
            f"Скан: {disc_row['scan_name']} / шайба №{disc_row['disc_no']}",
            f"Водій: {driver_name or 'не вказано'}",
            f"Автомобіль: {vehicle_name or 'не вказано'}",
            f"Дата тахокарти: {disc_date or 'не вказано'}",
            "",
            f"Інтервалів: {len(rows)}",
            f"Керування: {totals.get('Керування',0)//60}:{totals.get('Керування',0)%60:02d}",
            f"Інша робота: {totals.get('Інша робота',0)//60}:{totals.get('Інша робота',0)%60:02d}",
            f"Відпочинок: {totals.get('Відпочинок',0)//60}:{totals.get('Відпочинок',0)%60:02d}",
            f"Готовність: {totals.get('Готовність',0)//60}:{totals.get('Готовність',0)%60:02d}",
            f"Невизначено: {totals.get('Невизначено',0)//60}:{totals.get('Невизначено',0)%60:02d}",
            f"Максимальна швидкість: {max_speed if max_speed is not None else 'не визначено'}"
                + (" км/год (орієнтовно)" if max_speed is not None else ""),
            "",
            "ІНТЕРВАЛИ:",
        ]
        snapshot="\n".join(header+lines)
        return totals,max_speed,snapshot

    def save_control_protocol(self):
        """Зберігає контрольний знімок тахокарти. Основний графік не змінює."""
        if not self.current_id:
            messagebox.showwarning(
                "Протокол контролю","Оберіть тахокарту.",parent=self.parent
            )
            return

        disc=tdb().execute(
            "SELECT * FROM discs WHERE id=?",(self.current_id,)
        ).fetchone()
        rows=tdb().execute(
            "SELECT * FROM intervals WHERE disc_id=? ORDER BY start_min",
            (self.current_id,)
        ).fetchall()

        if not rows:
            messagebox.showwarning(
                "Протокол контролю",
                "Спочатку створіть/перевірте інтервали тахокарти.",
                parent=self.parent
            )
            return

        did=self.driver_map.get(self.v_driver.get()) or None
        vid=self.vehicle_map.get(self.v_vehicle.get()) or None

        if not did or not self.v_date.get().strip():
            messagebox.showwarning(
                "Протокол контролю",
                "Для протоколу виберіть водія та вкажіть дату тахокарти.",
                parent=self.parent
            )
            return

        # Спочатку зберігаємо метадані самої шайби.
        try:
            disc_date=self.pdate(self.v_date.get())
        except ValueError:
            messagebox.showerror(
                "Протокол контролю",
                "Дата тахокарти має бути у форматі ДД.ММ.РРРР.",
                parent=self.parent
            )
            return

        auto_count=sum(1 for x in rows if (x["source"] or "")=="auto")
        if auto_count:
            if not messagebox.askyesno(
                "Протокол контролю",
                f"У протоколі ще є автоматично розпізнані інтервали: {auto_count}.\n\n"
                "Вони є чернетковими. Зберегти контрольний протокол у такому вигляді?",
                parent=self.parent
            ):
                return

        totals,max_speed,snapshot=self._protocol_snapshot(disc,rows)

        con=tdb()
        try:
            con.execute(
                """UPDATE discs
                      SET driver_id=?,vehicle_id=?,disc_date=?,
                          status='Контрольний протокол збережено'
                    WHERE id=?""",
                (did,vid,disc_date,self.current_id)
            )
            cur=con.execute(
                """INSERT INTO control_protocols(
                    disc_id,driver_id,vehicle_id,disc_date,scan_name,
                    interval_count,driving_min,other_work_min,rest_min,
                    availability_min,undefined_min,max_speed_est,status,
                    snapshot_text,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    self.current_id,did,vid,disc_date,disc["scan_name"],
                    len(rows),
                    totals.get("Керування",0),
                    totals.get("Інша робота",0),
                    totals.get("Відпочинок",0),
                    totals.get("Готовність",0),
                    totals.get("Невизначено",0),
                    max_speed,
                    "Контрольний — без зміни графіка",
                    snapshot,
                    datetime.now().isoformat(timespec="seconds")
                )
            )
            protocol_id=cur.lastrowid
            con.commit()
        finally:
            con.close()

        self.load()
        messagebox.showinfo(
            "Протокол контролю",
            f"Протокол №{protocol_id} збережено.\n\n"
            "Основний графік і табель НЕ змінювалися.",
            parent=self.parent
        )

    def show_control_protocols(self):
        win=tk.Toplevel(self.parent)
        win.title("Протоколи контролю тахокарт")
        win.geometry("1000x560")
        win.transient(self.parent)
        win.resizable(True,True)

        outer=ttk.Frame(win,padding=8)
        outer.pack(fill="both",expand=True)

        cols=("id","created","date","scan","intervals","drive","speed","status")
        tree=ttk.Treeview(outer,columns=cols,show="headings",selectmode="browse")
        heads={
            "id":"№","created":"Створено","date":"Дата тахокарти","scan":"Скан",
            "intervals":"Інтервали","drive":"Керування","speed":"Max швидк.",
            "status":"Статус"
        }
        widths={
            "id":55,"created":145,"date":105,"scan":200,
            "intervals":80,"drive":90,"speed":100,"status":210
        }
        for c in cols:
            tree.heading(c,text=heads[c])
            tree.column(c,width=widths[c],anchor="w")

        y=ttk.Scrollbar(outer,orient="vertical",command=tree.yview)
        x=ttk.Scrollbar(outer,orient="horizontal",command=tree.xview)
        tree.configure(yscrollcommand=y.set,xscrollcommand=x.set)
        tree.grid(row=0,column=0,sticky="nsew")
        y.grid(row=0,column=1,sticky="ns")
        x.grid(row=1,column=0,sticky="ew")
        outer.rowconfigure(0,weight=1)
        outer.columnconfigure(0,weight=1)

        con=tdb()
        protocols=con.execute(
            "SELECT * FROM control_protocols ORDER BY id DESC"
        ).fetchall()
        con.close()

        by_id={}
        for p in protocols:
            by_id[str(p["id"])]=p
            created=(p["created_at"] or "").replace("T"," ")[:19]
            drive=f"{int(p['driving_min'] or 0)//60}:{int(p['driving_min'] or 0)%60:02d}"
            speed=(f"{p['max_speed_est']} км/год" if p["max_speed_est"] is not None else "")
            tree.insert(
                "","end",iid=str(p["id"]),
                values=(
                    p["id"],created,self.fdate(p["disc_date"] or ""),
                    p["scan_name"],p["interval_count"],drive,speed,p["status"]
                )
            )

        detail=tk.Text(outer,wrap="word",height=11)
        detail.grid(row=1,column=0,columnspan=2,sticky="nsew",pady=(8,0))
        outer.rowconfigure(1,weight=1)

        def show_selected(event=None):
            sel=tree.selection()
            if not sel:
                return
            p=by_id.get(sel[0])
            detail.configure(state="normal")
            detail.delete("1.0","end")
            detail.insert(
                "1.0",
                (p["snapshot_text"] or "Немає тексту протоколу.")
                + "\n\nРезультат контрольний. Основний графік/табель не змінювався."
            )
            detail.configure(state="disabled")

        tree.bind("<<TreeviewSelect>>",show_selected)
        if protocols:
            tree.selection_set(str(protocols[0]["id"]))
            show_selected()

        ttk.Button(
            outer,text="Закрити",command=win.destroy
        ).grid(row=2,column=0,columnspan=2,sticky="e",pady=(8,0))


    def seed_examples(self, paths):
        """Додає лише наявні тестові скани, не дублюючи їх за ім'ям."""
        if not paths:return
        con=tdb(); existing={r[0] for r in con.execute("SELECT scan_name FROM discs").fetchall()}; con.close()
        for p in paths:
            p=Path(p)
            if p.exists() and p.name not in existing:self._import_one(p)
        self.load()
        # Тестові шайби одразу проходять первинне розпізнавання, щоб модуль не виглядав порожнім.
        self.recognize_all(silent=True)
