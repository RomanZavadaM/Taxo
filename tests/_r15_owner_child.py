from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk

import main
main.ensure_workspace(main.DATA_ROOT)
main.init_db()
import taxo_app
import operations_orders as ops
import operations_orders_ui
ops.ensure_schema(main)

now=datetime.now().isoformat(timespec="seconds")
con=main.db()
con.execute("UPDATE company SET name=?,signer_name=?,signer_position=? WHERE id=1",("Тестове АТП","Тестовий Директор","Директор"))
for i in range(12):
    eid=101+i
    con.execute(
        "INSERT INTO employees(id,personnel_no,last_name,first_name,middle_name,position,active,created_at) VALUES(?,?,?,?,?,'Водій',1,?)",
        (eid,"D%03d"%(i+1),"Водій%02d"%(i+1),"Тестовий","",now),
    )
    con.execute("INSERT OR REPLACE INTO employee_roles(employee_id,role) VALUES(?,'Водій')",(eid,))
    vid=201+i
    con.execute(
        "INSERT INTO vehicles(id,name,plate,make_model,year,notes,active,created_at,garage_no) VALUES(?,?,?,?,2020,'',1,?,?)",
        (vid,"Автобус %02d"%(i+1),"BC%04dAA"%(1001+i),"MODEL-%02d"%(i+1),now,"A-%02d"%(i+1)),
    )
con.commit(); con.close()

errors=[]
main.messagebox.showinfo=lambda *a,**k: None
main.messagebox.showwarning=lambda *a,**k: None
main.messagebox.showerror=lambda title,msg,**k: errors.append((title,str(msg)))
main.messagebox.askyesno=lambda *a,**k: True
main.open_document=lambda *a,**k: None
main.open_external=lambda *a,**k: None

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self); self._operations_center_window=None
    def _company_name_value(self): return "Тестове АТП"

def walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from walk(child)

def button(root,text):
    for widget in walk(root):
        try:
            if widget.winfo_class() in ("TButton","Button") and str(widget.cget("text"))==text:
                return widget
        except Exception:
            pass
    raise AssertionError("button not found: "+text)

def tops(root,prefix):
    result=[]
    for widget in walk(root):
        if isinstance(widget,tk.Toplevel):
            try:
                if str(widget.title()).startswith(prefix): result.append(widget)
            except Exception:
                pass
    return result

def notebook(root): return next(w for w in walk(root) if isinstance(w,ttk.Notebook))
def select_tab(book,text): book.select(next(t for t in book.tabs() if str(book.tab(t,"text"))==text))
def preview_text(win):
    values=[]
    for widget in walk(win):
        if isinstance(widget,tk.Text):
            try: values.append(widget.get("1.0","end").strip())
            except Exception: pass
    return max(values,key=len) if values else ""

app=App(); app.geometry("1280x900+0+0"); app.withdraw()
win=operations_orders_ui.open_operations_center(app,main)
app.update_idletasks(); app.update()
book=notebook(win); select_tab(book,"Каталог наказів"); app.update()
button(win,"Закріпити ТЗ за водіями").invoke(); app.update_idletasks(); app.update()
dialog=tops(win,"Створити наказ")[-1]
boxes=[w for w in walk(dialog) if isinstance(w,tk.Listbox)]
assert len(boxes)==2 and boxes[0].size()==12 and boxes[1].size()==12
boxes[0].selection_set(0,11); boxes[1].selection_set(0,11)
boxes[0].event_generate("<<ListboxSelect>>"); boxes[1].event_generate("<<ListboxSelect>>")
app.update_idletasks(); app.update()
staged=getattr(dialog,"_taxo_staged_assignment_pairs")
staged_tree=getattr(dialog,"_taxo_staged_assignment_tree")
assert len(staged)==12, staged
assert len(staged_tree.get_children())==12
expected=list(staged)

# Reproduce the dangerous condition observed in the owner's real DB.
boxes[0].selection_clear(0,"end"); boxes[1].selection_clear(0,"end")
app.update_idletasks(); app.update()
assert not boxes[0].curselection() and not boxes[1].curselection()
button(dialog,"Створити").invoke(); app.update_idletasks(); app.update()

con=main.db()
order=con.execute("SELECT * FROM operations_orders ORDER BY id DESC LIMIT 1").fetchone()
oid=int(order["id"])
pairs=ops.vehicle_assignment_pairs(con,oid)
con.close()
assert pairs==expected,(pairs,expected)

preview=tops(win,"Перегляд наказу №")[-1]
text=preview_text(preview)
for marker in ("MODEL-01","BC1001AA","Водій01 Тестовий","MODEL-12","BC1012AA","Водій12 Тестовий"):
    assert marker in text,("preview missing",marker,text)

button(preview,"Створити все").invoke(); app.update_idletasks(); app.update()
output=Path(main.OUTPUT_DIR)
docx=next(output.glob("Наказ_*.docx"))
pdf=next(output.glob("Наказ_*.pdf"))
jpg=next(output.glob("Наказ_*_сторінка_*.jpg"))
from docx import Document
document=Document(str(docx))
docx_text="\n".join([p.text for p in document.paragraphs]+[cell.text for table in document.tables for row in table.rows for cell in row.cells])
from pypdf import PdfReader
pdf_text="\n".join((page.extract_text() or "") for page in PdfReader(str(pdf)).pages)
for marker in ("MODEL-01","BC1001AA","Водій01 Тестовий","MODEL-12","BC1012AA","Водій12 Тестовий"):
    assert marker in docx_text,("DOCX missing",marker)
    assert marker in pdf_text,("PDF missing",marker)
assert jpg.stat().st_size>1000

preview.destroy(); win.destroy(); app.update(); app.destroy()
con=main.db(); reopened=ops.vehicle_assignment_pairs(con,oid); con.close()
assert reopened==expected,(reopened,expected)
assert not errors,errors
print("ASSIGNMENT_STAGE_OWNER_SCENARIO_OK")
