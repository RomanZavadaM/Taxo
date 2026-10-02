# -*- coding: utf-8 -*-
"""Taxo 10.7-r3 — structured appendices for operations orders."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import operations_orders as ops

APP_VERSION = "10.7-r3"


def ensure_appendix_schema_on_connection(con):
    con.executescript("""
        CREATE TABLE IF NOT EXISTS operations_order_appendices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL REFERENCES operations_orders(id) ON DELETE CASCADE,
            sequence_no INTEGER NOT NULL DEFAULT 1,
            title TEXT NOT NULL DEFAULT '',
            content TEXT NOT NULL DEFAULT '',
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_operations_order_appendices_order
            ON operations_order_appendices(order_id, sequence_no, id);
    """)


def ensure_appendix_schema(core):
    con = core.db()
    try:
        ensure_appendix_schema_on_connection(con)
        con.commit()
    finally:
        con.close()


def list_appendices(con, order_id):
    ensure_appendix_schema_on_connection(con)
    return con.execute(
        "SELECT * FROM operations_order_appendices WHERE order_id=? ORDER BY sequence_no,id",
        (int(order_id),),
    ).fetchall()


def _require_draft(con, order_id):
    row = ops.get_order(con, order_id)
    if row is None:
        raise ValueError("Наказ не знайдено.")
    if str(row["status"]) != ops.ORDER_DRAFT:
        raise ValueError("Додатки затвердженого або скасованого наказу не редагуються. Оформіть новий наказ.")
    return row


def save_appendix(con, order_id, *, title, content, note="", appendix_id=None, sequence_no=None):
    ensure_appendix_schema_on_connection(con)
    _require_draft(con, order_id)
    title = str(title or "").strip()
    content = str(content or "").strip()
    if not title:
        raise ValueError("Вкажіть назву додатка.")
    if not content:
        raise ValueError("Додаток не може бути порожнім.")
    now = datetime.now().isoformat(timespec="seconds")
    if appendix_id:
        current = con.execute(
            "SELECT * FROM operations_order_appendices WHERE id=? AND order_id=?",
            (int(appendix_id), int(order_id)),
        ).fetchone()
        if current is None:
            raise ValueError("Додаток не знайдено.")
        seq = int(sequence_no if sequence_no is not None else current["sequence_no"])
        con.execute(
            """UPDATE operations_order_appendices
                  SET sequence_no=?,title=?,content=?,note=?,updated_at=?
                WHERE id=? AND order_id=?""",
            (seq, title, content, str(note or "").strip(), now, int(appendix_id), int(order_id)),
        )
        return int(appendix_id)
    if sequence_no is None:
        row = con.execute(
            "SELECT COALESCE(MAX(sequence_no),0)+1 AS n FROM operations_order_appendices WHERE order_id=?",
            (int(order_id),),
        ).fetchone()
        sequence_no = int(row["n"])
    cur = con.execute(
        """INSERT INTO operations_order_appendices(
               order_id,sequence_no,title,content,note,created_at,updated_at
           ) VALUES(?,?,?,?,?,?,?)""",
        (int(order_id), int(sequence_no), title, content, str(note or "").strip(), now, now),
    )
    return int(cur.lastrowid)


def delete_appendix(con, order_id, appendix_id):
    ensure_appendix_schema_on_connection(con)
    _require_draft(con, order_id)
    con.execute(
        "DELETE FROM operations_order_appendices WHERE id=? AND order_id=?",
        (int(appendix_id), int(order_id)),
    )


def _font_name(font_path=None):
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    resolved = ops._font_path(font_path)
    if resolved:
        try:
            pdfmetrics.registerFont(TTFont("TaxoOrderR3", resolved))
            return "TaxoOrderR3"
        except Exception:
            pass
    return "Times-Roman"


def export_order_pdf_with_appendices(core, path, order, assignments=(), company=None, control_name="", font_path=None):
    """Render the r2 order layout and append structured appendices as separate pages."""
    con = core.db()
    try:
        appendices = list_appendices(con, int(order["id"]))
    finally:
        con.close()
    if not appendices:
        return _BASE_EXPORT(path, order, assignments, company, control_name, font_path=font_path)

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, PageBreak

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    font_name = _font_name(font_path)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle("OrderR3Normal", parent=styles["Normal"], fontName=font_name,
                            fontSize=11.5, leading=15, alignment=TA_LEFT)
    center = ParagraphStyle("OrderR3Center", parent=normal, alignment=TA_CENTER)
    right = ParagraphStyle("OrderR3Right", parent=normal, alignment=TA_RIGHT, fontSize=10.5, leading=13)
    title = ParagraphStyle("OrderR3Title", parent=center, fontSize=15, leading=18, spaceAfter=2)
    bold_center = ParagraphStyle("OrderR3BoldCenter", parent=center, fontSize=12.5, leading=15)

    doc = SimpleDocTemplate(str(path), pagesize=A4,
                            leftMargin=20*mm, rightMargin=18*mm,
                            topMargin=17*mm, bottomMargin=17*mm)
    company = company or {}
    company_name = str(company.get("name") or "").strip() or "Підприємство"
    signer_position = str(company.get("signer_position") or "").strip() or "Керівник"
    signer_name = str(company.get("signer_name") or "").strip()
    story = [Paragraph("<b>Н А К А З</b>", title), Paragraph("по %s" % company_name, center), Spacer(1, 7*mm)]
    meta = Table([[ops.display_day(order["order_date"]), "<b>№ %s</b>" % str(order["order_no"] or ""), str(order["place"] or "")]],
                 colWidths=[55*mm,55*mm,55*mm])
    meta.setStyle(TableStyle([
        ("FONTNAME",(0,0),(-1,-1),font_name),("FONTSIZE",(0,0),(-1,-1),11.5),
        ("ALIGN",(0,0),(0,0),"LEFT"),("ALIGN",(1,0),(1,0),"CENTER"),("ALIGN",(2,0),(2,0),"RIGHT"),
    ]))
    story += [meta, Spacer(1,8*mm)]
    subject = str(order["subject"] or "").strip()
    if subject:
        story += [Paragraph("<b>%s</b>" % subject, normal), Spacer(1,5*mm)]
    preamble = str(order["preamble"] or "").strip()
    if preamble:
        story += [Paragraph(preamble, normal), Spacer(1,6*mm)]
    story += [Paragraph("<b>Н А К А З У Ю:</b>", bold_center), Spacer(1,5*mm)]

    if str(order["order_type"]) == ops.TYPE_VEHICLE_ASSIGNMENT:
        first_from = ops.display_day(assignments[0]["valid_from"]) if assignments else ops.display_day(order["order_date"])
        story.append(Paragraph("1. Закріпити з %s транспортні засоби підприємства за водіями згідно з наведеною таблицею:" % first_from, normal))
        data = [["№","Транспортний засіб","Держ. номер","Водій"]]
        for idx,item in enumerate(assignments,1):
            name = " ".join(str(item[k] or "").strip() for k in ("last_name","first_name","middle_name") if str(item[k] or "").strip())
            vehicle = str(item["make_model"] or item["vehicle_name"] or "").strip()
            data.append([idx,vehicle,str(item["plate"] or "").strip(),name])
        table = Table(data,colWidths=[10*mm,52*mm,38*mm,65*mm],repeatRows=1)
        table.setStyle(TableStyle([
            ("FONTNAME",(0,0),(-1,-1),font_name),("FONTSIZE",(0,0),(-1,-1),10.5),
            ("GRID",(0,0),(-1,-1),0.45,colors.black),("ALIGN",(0,0),(-1,0),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3),
            ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ]))
        story += [Spacer(1,3*mm),table,Spacer(1,5*mm)]
        if str(control_name or "").strip():
            story.append(Paragraph("2. Контроль за виконанням даного наказу покласти на %s." % str(control_name).strip(), normal))
    else:
        for paragraph in [p.strip() for p in str(order["body_text"] or "").splitlines() if p.strip()]:
            story += [Paragraph(paragraph, normal), Spacer(1,2*mm)]
        if str(control_name or "").strip():
            story.append(Paragraph("Контроль за виконанням даного наказу покласти на %s." % str(control_name).strip(), normal))

    story += [Spacer(1,15*mm)]
    signature = Table([[signer_position,"________________",signer_name]],colWidths=[60*mm,45*mm,55*mm])
    signature.setStyle(TableStyle([
        ("FONTNAME",(0,0),(-1,-1),font_name),("FONTSIZE",(0,0),(-1,-1),11.5),
        ("ALIGN",(0,0),(0,0),"LEFT"),("ALIGN",(1,0),(1,0),"CENTER"),("ALIGN",(2,0),(2,0),"RIGHT"),
    ]))
    story.append(signature)

    for idx, appendix in enumerate(appendices, 1):
        story += [PageBreak()]
        seq = int(appendix["sequence_no"] or idx)
        story += [Paragraph(
            "Додаток %d<br/>до наказу від %s № %s" % (seq, ops.display_day(order["order_date"]), str(order["order_no"] or "")),
            right,
        ), Spacer(1, 10*mm)]
        story += [Paragraph("<b>%s</b>" % str(appendix["title"] or "Додаток"), bold_center), Spacer(1, 7*mm)]
        for paragraph in [p.strip() for p in str(appendix["content"] or "").splitlines() if p.strip()]:
            story += [Paragraph(paragraph, normal), Spacer(1, 2.5*mm)]
    doc.build(story)
    return path


def _find_notebook(widget):
    try:
        if widget.winfo_class() == "TNotebook":
            return widget
        for child in widget.winfo_children():
            found = _find_notebook(child)
            if found is not None:
                return found
    except Exception:
        pass
    return None


def _install_appendix_tab(app, core, win):
    if getattr(win, "_taxo_v1073_appendix_tab", False):
        return
    book = _find_notebook(win)
    if book is None:
        return
    tab = core.ttk.Frame(book)
    book.add(tab, text="Додатки до наказів")
    top = core.ttk.Frame(tab, padding=(10,10,10,4)); top.pack(fill="x")
    core.ttk.Label(top, text="Наказ").pack(side="left")
    order_var = core.tk.StringVar(value="")
    order_box = core.ttk.Combobox(top, textvariable=order_var, state="readonly", width=72)
    order_box.pack(side="left", fill="x", expand=True, padx=(8,0))
    hint = core.ttk.Label(tab, text="Додатки зберігаються структуровано. Після затвердження наказу вони не редагуються.", style="Muted.TLabel")
    hint.pack(fill="x", padx=10, pady=(2,6))
    frame = core.ttk.Frame(tab); frame.pack(fill="both", expand=True, padx=10, pady=(0,10)); frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
    tree = core.ttk.Treeview(frame, columns=("seq","title","note"), show="headings", selectmode="browse")
    for key,label,width in (("seq","№",60),("title","Назва додатка",500),("note","Примітка",360)):
        tree.heading(key,text=label); tree.column(key,width=width,anchor="w")
    sy=core.ttk.Scrollbar(frame,orient="vertical",command=tree.yview); sx=core.ttk.Scrollbar(frame,orient="horizontal",command=tree.xview)
    tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set); tree.grid(row=0,column=0,sticky="nsew"); sy.grid(row=0,column=1,sticky="ns"); sx.grid(row=1,column=0,sticky="ew")
    buttons=core.ttk.Frame(tab,padding=(10,0,10,10)); buttons.pack(fill="x")
    order_map={}; appendix_cache={}

    def reload_orders():
        con=core.db()
        try: rows=ops.list_orders(con)
        finally: con.close()
        order_map.clear(); labels=[]
        for row in rows:
            label="%s · № %s · %s · %s" % (ops.display_day(row["order_date"]),row["order_no"],str(row["subject"] or ""),ops.ORDER_STATUS_LABELS.get(row["status"],row["status"]))
            labels.append(label); order_map[label]=int(row["id"])
        order_box.configure(values=labels)
        if labels and order_var.get() not in order_map:
            order_var.set(labels[0])
        refresh()

    def selected_order_id():
        return order_map.get(order_var.get())

    def refresh(_event=None):
        for iid in tree.get_children(): tree.delete(iid)
        appendix_cache.clear(); oid=selected_order_id()
        if not oid: return
        con=core.db()
        try: rows=list_appendices(con,oid)
        finally: con.close()
        for row in rows:
            appendix_cache[int(row["id"])]=row
            tree.insert("","end",iid=str(row["id"]),values=(row["sequence_no"],row["title"],row["note"] or ""))

    def editor(row=None):
        oid=selected_order_id()
        if not oid:
            core.messagebox.showinfo("Додатки","Виберіть наказ.",parent=win); return
        con=core.db()
        try:
            order=ops.get_order(con,oid)
        finally: con.close()
        if order is None or order["status"] != ops.ORDER_DRAFT:
            core.messagebox.showinfo("Додатки","Редагувати додатки можна лише у чернетці наказу.",parent=win); return
        dlg=core.tk.Toplevel(win); dlg.title("Додаток до наказу");
        try: core.configure_toplevel(dlg,title="Додаток до наказу",minsize=(760,520))
        except Exception: pass
        body=core.ttk.Frame(dlg,padding=14); body.pack(fill="both",expand=True); body.columnconfigure(1,weight=1); body.rowconfigure(2,weight=1)
        seq=core.tk.StringVar(value=str(row["sequence_no"] if row is not None else "")); title=core.tk.StringVar(value=str(row["title"] if row is not None else "")); note=core.tk.StringVar(value=str(row["note"] if row is not None else ""))
        core.ttk.Label(body,text="Номер додатка").grid(row=0,column=0,sticky="w",pady=5); core.ttk.Entry(body,textvariable=seq,width=10).grid(row=0,column=1,sticky="w",pady=5)
        core.ttk.Label(body,text="Назва").grid(row=1,column=0,sticky="w",pady=5); core.ttk.Entry(body,textvariable=title).grid(row=1,column=1,sticky="ew",pady=5)
        core.ttk.Label(body,text="Зміст").grid(row=2,column=0,sticky="nw",pady=5); text=core.tk.Text(body,wrap="word",height=16); text.grid(row=2,column=1,sticky="nsew",pady=5); text.insert("1.0",str(row["content"] if row is not None else ""))
        core.ttk.Label(body,text="Примітка").grid(row=3,column=0,sticky="w",pady=5); core.ttk.Entry(body,textvariable=note).grid(row=3,column=1,sticky="ew",pady=5)
        bar=core.ttk.Frame(body); bar.grid(row=4,column=0,columnspan=2,sticky="ew",pady=(10,0))
        def save():
            try: seq_value=int(seq.get()) if str(seq.get()).strip() else None
            except Exception: core.messagebox.showerror("Додаток","Номер додатка має бути цілим числом.",parent=dlg); return
            con2=core.db()
            try:
                save_appendix(con2,oid,title=title.get(),content=text.get("1.0","end-1c"),note=note.get(),appendix_id=(row["id"] if row is not None else None),sequence_no=seq_value); con2.commit()
            except Exception as exc:
                con2.rollback(); core.messagebox.showerror("Додаток",str(exc),parent=dlg); return
            finally: con2.close()
            dlg.destroy(); refresh()
        core.ttk.Button(bar,text="Скасувати",command=dlg.destroy).pack(side="right")
        core.ttk.Button(bar,text="Зберегти",style="Accent.TButton",command=save).pack(side="right",padx=(0,6))
        dlg.transient(win)

    def edit_selected():
        sel=tree.selection()
        if not sel: core.messagebox.showinfo("Додатки","Виберіть додаток.",parent=win); return
        editor(appendix_cache.get(int(sel[0])))

    def delete_selected():
        sel=tree.selection(); oid=selected_order_id()
        if not sel or not oid: core.messagebox.showinfo("Додатки","Виберіть додаток.",parent=win); return
        if not core.messagebox.askyesno("Видалити додаток?","Видалити вибраний додаток з чернетки наказу?",parent=win): return
        con=core.db()
        try: delete_appendix(con,oid,int(sel[0])); con.commit()
        except Exception as exc: con.rollback(); core.messagebox.showerror("Додатки",str(exc),parent=win); return
        finally: con.close()
        refresh()

    core.ttk.Button(buttons,text="Додати додаток",style="Accent.TButton",command=lambda:editor(None)).pack(side="left")
    core.ttk.Button(buttons,text="Редагувати",command=edit_selected).pack(side="left",padx=(6,0))
    core.ttk.Button(buttons,text="Видалити",command=delete_selected).pack(side="left",padx=(6,0))
    core.ttk.Button(buttons,text="Оновити",command=reload_orders).pack(side="right")
    order_box.bind("<<ComboboxSelected>>",refresh)
    reload_orders(); win._taxo_v1073_appendix_tab=True


_BASE_EXPORT = ops.export_order_pdf


def install(core, base_app):
    if getattr(core,"_TAXO_1073_INSTALLED",False):
        return core.App
    core.APP_VERSION=APP_VERSION
    ensure_appendix_schema(core)
    if not getattr(ops,"_taxo_v1073_export",False):
        ops.export_order_pdf=lambda path,order,assignments=(),company=None,control_name="",font_path=None: export_order_pdf_with_appendices(core,path,order,assignments,company,control_name,font_path)
        ops._taxo_v1073_export=True

    class Taxo1073App(base_app):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

        def open_operations_center(self):
            result=super().open_operations_center()
            win=getattr(self,"_operations_center_window",None)
            if win is not None:
                try: _install_appendix_tab(self,core,win)
                except Exception as exc:
                    core.messagebox.showerror("Експлуатація",str(exc),parent=win)
            return result

    Taxo1073App.__name__="App"; Taxo1073App.__qualname__="App"
    core.App=Taxo1073App; core._TAXO_1073_INSTALLED=True
    return Taxo1073App
