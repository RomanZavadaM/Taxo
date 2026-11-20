# -*- coding: utf-8 -*-
"""10.23-r4 — narrow-window order UI remains fully reachable."""
import tkinter as tk
from tkinter import ttk
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import main
import operations_orders_ui
import order_preview_ui
from runtime_reachability import runtime_routes, activate_widget, assert_widget_reachable


def walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from walk(child)


def button(root, text):
    return next(
        (w for w in walk(root)
         if isinstance(w, ttk.Button) and str(w.cget("text")) == text),
        None,
    )


class _App(tk.Tk):
    def __init__(self):
        super().__init__()
        self._operations_center_window = None

    def _company_name_value(self):
        return "Тестове підприємство"


class OrderSmallWindowR4Tests(TestCase):
    @runtime_routes("operations.order_preview_formats")
    def test_order_preview_format_controls_fit_760px_and_are_usable(self):
        root=tk.Tk()
        root.geometry("900x700+10+10")
        row={"id":41,"order_no":"41"}
        ops=SimpleNamespace(
            order_preview_text=lambda *_a,**_k:"Тестовий зміст наказу\nРядок 2",
        )
        messages=SimpleNamespace(
            showinfo=lambda *a,**k:None,
            showerror=lambda *a,**k:self.fail("Unexpected format error: %r" % (a,)),
            showwarning=lambda *a,**k:None,
        )
        def configure(win,title=None,minsize=None,**_kwargs):
            if minsize:
                win.minsize(*minsize)
        core=SimpleNamespace(tk=tk,ttk=ttk,configure_toplevel=configure,messagebox=messages)
        try:
            with patch.object(order_preview_ui,"generate_order_formats",return_value={}):
                dlg=order_preview_ui.open_order_preview(
                    core,ops,root,row,
                    lambda current:(current,[],[],{"name":"Тест"},""),
                    lambda *_a,**_k:None,
                    lambda *_a,**_k:"read-only",
                    lambda *_a,**_k:None,
                )
                dlg.geometry("760x560+30+30")
                root.update()
                expected=(
                    "Створити DOCX","Створити PDF","Створити JPG","Створити все",
                    "Перегляд DOCX","Перегляд PDF","Перегляд JPG",
                    "Відкрити у програмі: DOCX","Відкрити у програмі: PDF",
                    "Відкрити у програмі: JPG",
                )
                controls=[]
                for label in expected:
                    widget=button(dlg,label)
                    self.assertIsNotNone(widget,label)
                    assert_widget_reachable(
                        widget,"operations.order_preview_formats",container=dlg
                    )
                    controls.append(widget)
                # The format area is deliberately limited to two columns so
                # long external-open labels do not get squeezed off-screen.
                self.assertLessEqual(
                    max(int(w.grid_info()["column"]) for w in controls),1
                )
                left=dlg.winfo_rootx()
                right=left+dlg.winfo_width()
                for widget in controls:
                    self.assertGreaterEqual(widget.winfo_rootx(),left)
                    self.assertLessEqual(
                        widget.winfo_rootx()+widget.winfo_width(),right+2
                    )
                activate_widget(
                    button(dlg,"Створити DOCX"),
                    "operations.order_preview_formats",
                    container=dlg,
                )
                root.update_idletasks()
                self.assertTrue(button(dlg,"Закрити").winfo_ismapped())
        finally:
            root.destroy()

    def test_operations_center_hint_wraps_to_real_940px_viewport(self):
        app=_App()
        app.geometry("1000x700+10+10")
        core=SimpleNamespace(
            tk=tk,ttk=ttk,
            fit_window_to_screen=lambda win,*_a:win.geometry("940x600+20+20"),
            configure_toplevel=lambda win,title=None,minsize=None,**_k:(
                win.minsize(*minsize) if minsize else None
            ),
        )
        def fake_register(*_a,**_k):
            return SimpleNamespace(
                order_dialog=lambda *_a,**_k:None,
                preview_catalog_order=lambda *_a,**_k:None,
                refresh_orders=lambda:None,
            )
        try:
            with patch.object(operations_orders_ui.ops,"ensure_schema"), \
                 patch.object(operations_orders_ui,"install_operations_settings",return_value={}), \
                 patch.object(operations_orders_ui,"install_instruction_tab",return_value=None), \
                 patch.object(
                     operations_orders_ui,"install_internship_tab",
                     side_effect=lambda _app,_core,book:ttk.Frame(book),
                 ), \
                 patch.object(operations_orders_ui,"install_order_register",side_effect=fake_register), \
                 patch.object(operations_orders_ui,"install_order_type_catalog",return_value=None):
                win=operations_orders_ui.open_operations_center(app,core)
                win.geometry("940x600+20+20")
                app.update()
                hint=next(
                    w for w in walk(win)
                    if isinstance(w,ttk.Label)
                    and str(w.cget("text")).startswith("Робочий центр експлуатації:")
                )
                first=int(float(hint.cget("wraplength")))
                self.assertLess(first,940)
                self.assertLessEqual(hint.winfo_width(),win.winfo_width()-20)
                win.geometry("1100x650+20+20")
                app.update()
                second=int(float(hint.cget("wraplength")))
                self.assertGreater(second,first)
                self.assertLessEqual(second,win.winfo_width())
        finally:
            app.destroy()


if __name__ == "__main__":
    import unittest
    unittest.main()
