# -*- coding: utf-8 -*-
"""Live geometry and selection regression for the attestation workspace."""
import tkinter as tk
from tkinter import ttk
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
import main
from runtime_reachability import runtime_routes, activate_widget

def walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from walk(child)

class AttestationResizeTests(TestCase):
    @runtime_routes("documents.attestation_resize")
    def test_real_workspace_resizes_without_rebuilding_form_or_history(self):
        root=tk.Tk()
        root.geometry("1100x760")
        try:
            host=SimpleNamespace(tab_att=ttk.Frame(root))
            host.tab_att.pack(fill="both",expand=True)
            for name in (
                "on_att_driver_change","create_attestation","show_attestation_gap_control",
                "open_att_file","preview_selected_attestation","open_att_folder",
                "open_att_archive_folder","edit_selected_attestation","delete_selected_attestation",
                "restore_selected_attestation","purge_selected_attestation","show_attestation_audit",
                "load_att_history","reset_att_history_filters",
            ):
                setattr(host,name,lambda *a,**k:None)
            host._make_scrollable_tab_body=lambda tab,key,**kw: main.App._make_scrollable_tab_body(host,tab,key,**kw)
            with patch.object(main,"get_setting",return_value=""):
                main.App.build_attestation(host)
            root.update()
            panes=host.att_workspace_panes
            self.assertEqual(len(panes.panes()),2)
            host.att_place.set("Незбережене місце")
            host.att_tree.insert("","end",iid="test",values=("test",))
            host.att_tree.selection_set("test")
            def button(label):
                return next(w for w in walk(root) if isinstance(w,ttk.Button) and w.cget("text")==label)
            # Start with a divider that leaves usable space on both sides.
            panes.sashpos(0,220)
            root.update_idletasks()
            before=panes.sashpos(0)
            activate_widget(button("Більша історія"),"documents.attestation_resize",container=root)
            root.update_idletasks()
            self.assertLess(panes.sashpos(0),before)
            button("Більша форма").invoke()
            root.update_idletasks()
            self.assertEqual(panes.sashpos(0),before)
            for size in ("900x600","1024x700","1366x768"):
                root.geometry(size)
                root.update()
                self.assertTrue(host.att_tree.winfo_exists())
                self.assertEqual(host.att_tree.selection(),("test",))
                self.assertEqual(host.att_place.get(),"Незбережене місце")
                self.assertEqual(len(panes.panes()),2)
        finally:
            root.destroy()
