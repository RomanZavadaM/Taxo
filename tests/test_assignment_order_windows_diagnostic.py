# -*- coding: utf-8 -*-
"""Diagnostic: real Windows UI -> SQLite -> Preview -> DOCX/PDF assignment flow."""
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(sys.platform == "win32", "Windows-only owner-scenario diagnostic")
class AssignmentOrderWindowsDiagnosticTests(unittest.TestCase):
    def test_real_bulk_assignment_survives_and_is_printed(self):
        with tempfile.TemporaryDirectory(prefix="taxo_assignment_e2e_") as td:
            env = os.environ.copy()
            env["TAXO_WORKSPACE_ROOT"] = str(Path(td) / "workspace")
            env["TAXO_CONFIG_DIR"] = str(Path(td) / "config")
            src = str(ROOT / "src" / "taxo")
            env["PYTHONPATH"] = src + os.pathsep + str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
            code = textwrap.dedent(r'''
                import os
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

                now = datetime.now().isoformat(timespec="seconds")
                con = main.db()
                con.execute("UPDATE company SET name=?,signer_name=?,signer_position=? WHERE id=1",
                            ("Тестове АТП", "Тестовий Директор", "Директор"))
                for row in (
                    (101,"D001","Коваль","Андрій"),
                    (102,"D002","Мельник","Богдан"),
                    (103,"D003","Шевчук","Василь"),
                ):
                    con.execute(
                        "INSERT INTO employees(id,personnel_no,last_name,first_name,middle_name,position,active,created_at) "
                        "VALUES(?,?,?,?,?,'Водій',1,?)",
                        (row[0],row[1],row[2],row[3],"",now),
                    )
                    con.execute("INSERT OR REPLACE INTO employee_roles(employee_id,role) VALUES(?,'Водій')", (row[0],))
                for row in (
                    (201,"Автобус MAN","BC1001AA","MAN Lion City","A-01"),
                    (202,"Автобус Mercedes","BC1002AA","Mercedes Citaro","A-02"),
                ):
                    con.execute(
                        "INSERT INTO vehicles(id,name,plate,make_model,year,notes,active,created_at,garage_no) "
                        "VALUES(?,?,?,?,2020,'',1,?,?)",
                        (row[0],row[1],row[2],row[3],now,row[4]),
                    )
                con.commit(); con.close()

                errors = []
                main.messagebox.showinfo = lambda *a, **k: None
                main.messagebox.showwarning = lambda *a, **k: None
                main.messagebox.showerror = lambda title,msg,**k: errors.append((title,str(msg)))
                main.messagebox.askyesno = lambda *a, **k: True
                main.open_document = lambda *a, **k: None
                main.open_external = lambda *a, **k: None

                class App(tk.Tk):
                    def __init__(self):
                        tk.Tk.__init__(self)
                        self._operations_center_window = None
                    def _company_name_value(self):
                        return "Тестове АТП"

                def walk(widget):
                    for child in widget.winfo_children():
                        yield child
                        for nested in walk(child):
                            yield nested

                def button(root, text):
                    for widget in walk(root):
                        try:
                            if widget.winfo_class() in ("TButton","Button") and str(widget.cget("text")) == text:
                                return widget
                        except Exception:
                            pass
                    raise AssertionError("Button not found: " + text)

                def top_levels(root, prefix):
                    result = []
                    for widget in walk(root):
                        if isinstance(widget, tk.Toplevel):
                            try:
                                if str(widget.title()).startswith(prefix):
                                    result.append(widget)
                            except Exception:
                                pass
                    return result

                def notebook(root):
                    return next(widget for widget in walk(root) if isinstance(widget, ttk.Notebook))

                def select_tab(book, text):
                    tab_id = next(tab for tab in book.tabs() if str(book.tab(tab,"text")) == text)
                    book.select(tab_id)

                def order_tree(root):
                    return next(
                        widget for widget in walk(root)
                        if isinstance(widget, ttk.Treeview)
                        and "date" in tuple(str(x) for x in widget.cget("columns"))
                        and "no" in tuple(str(x) for x in widget.cget("columns"))
                    )

                def preview_text(win):
                    values = []
                    for widget in walk(win):
                        if isinstance(widget, tk.Text):
                            try:
                                values.append(widget.get("1.0","end").strip())
                            except Exception:
                                pass
                    return max(values, key=len) if values else ""

                app = App(); app.geometry("1280x850+0+0"); app.withdraw()
                win = operations_orders_ui.open_operations_center(app, main)
                app.update_idletasks(); app.update()
                book = notebook(win)

                # Owner scenario: create assignment order EMPTY, then bulk-select 2 vehicles + 2 drivers.
                select_tab(book, "Каталог наказів"); app.update()
                button(win, "Закріпити ТЗ за водіями").invoke(); app.update()
                create = top_levels(win, "Створити наказ")[0]
                button(create, "Створити").invoke(); app.update()

                con = main.db()
                order = con.execute("SELECT * FROM operations_orders ORDER BY id DESC LIMIT 1").fetchone()
                oid = int(order["id"])
                assert ops.vehicle_assignment_pairs(con, oid) == []
                con.close()

                button(win, "Додати багато…").invoke(); app.update()
                bulk = top_levels(win, "Додати кілька закріплень")[0]
                lists = [widget for widget in walk(bulk) if isinstance(widget, tk.Listbox)]
                assert len(lists) == 2, len(lists)
                for box in lists:
                    box.selection_set(0, 1)
                button(bulk, "Додати вибрані пари").invoke(); app.update()

                con = main.db()
                pairs = ops.vehicle_assignment_pairs(con, oid)
                con.close()
                assert pairs == [(201,101),(202,102)], pairs

                select_tab(book, "Накази"); app.update()
                tree = order_tree(win)
                tree.selection_set(str(oid)); tree.focus(str(oid)); tree.event_generate("<<TreeviewSelect>>"); app.update()
                button(win, "Переглянути / друк").invoke(); app.update()
                preview = top_levels(win, "Перегляд наказу №")[-1]
                text = preview_text(preview)
                markers = ("MAN Lion City","BC1001AA","Коваль Андрій","Mercedes Citaro","BC1002AA","Мельник Богдан")
                for marker in markers:
                    assert marker in text, ("preview missing", marker, text)

                button(preview, "Створити все").invoke(); app.update_idletasks(); app.update()
                output = Path(main.OUTPUT_DIR)
                docx = next(output.glob("Наказ_*.docx"))
                pdf = next(output.glob("Наказ_*.pdf"))
                jpg = next(output.glob("Наказ_*_сторінка_*.jpg"))

                from docx import Document
                document = Document(str(docx))
                docx_text = "\n".join(
                    [p.text for p in document.paragraphs]
                    + [cell.text for table in document.tables for row in table.rows for cell in row.cells]
                )
                from pypdf import PdfReader
                pdf_text = "\n".join((page.extract_text() or "") for page in PdfReader(str(pdf)).pages)
                for marker in markers:
                    assert marker in docx_text, ("DOCX missing", marker, docx_text)
                    assert marker in pdf_text, ("PDF missing", marker, pdf_text)
                assert jpg.stat().st_size > 1000

                preview.destroy(); win.destroy(); app.update(); app.destroy()
                con = main.db()
                reopened = ops.vehicle_assignment_pairs(con, oid)
                con.close()
                assert reopened == pairs, (reopened, pairs)
                assert not errors, errors
                print("ASSIGNMENT_E2E_WINDOWS_OK")
            ''')
            completed = subprocess.run(
                [sys.executable, "-c", code],
                cwd=str(ROOT), env=env,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, timeout=60,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout)
            self.assertIn("ASSIGNMENT_E2E_WINDOWS_OK", completed.stdout)


if __name__ == "__main__":
    unittest.main()
