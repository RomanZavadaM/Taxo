# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
import unittest

import v1081_features as r1
import v1082_features as r2


class _DummyApp:
    def __init__(self, root):
        self.root = root
        self.tab_vehicles = ttk.Frame(root)
        self.tab_vehicles.pack(fill="both", expand=True)
        self.vehicle_hide_inactive = tk.BooleanVar(master=root, value=True)
        self.calls = []

        legacy = ttk.Frame(self.tab_vehicles)
        legacy.pack(fill="x")
        ttk.Button(legacy, text="Реєстр «Шлях»").pack(side="left")
        ttk.Button(legacy, text="Відомість ТЦК 20.06 / 20.12").pack(side="left")

        self.vehicle_tree = ttk.Treeview(self.tab_vehicles, columns=("id",), show="headings")
        self.vehicle_tree.heading("id", text="ID")
        self.vehicle_tree.pack(fill="both", expand=True)

    def winfo_width(self):
        return self.root.winfo_width()

    def vehicle_form(self): self.calls.append("vehicle_form")
    def edit_vehicle(self): self.calls.append("edit_vehicle")
    def vehicle_documents(self): self.calls.append("vehicle_documents")
    def vehicle_document_control(self): self.calls.append("vehicle_document_control")
    def delete_vehicle(self): self.calls.append("delete_vehicle")
    def load_vehicles(self): self.calls.append("load_vehicles")


class RuntimeVehicleToolbarSmokeTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.geometry("900x600")
        self.app = _DummyApp(self.root)
        self.root.update_idletasks()

    def tearDown(self):
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def test_toolbar_builds_without_pack_grid_conflict(self):
        r1._install_stable_vehicle_toolbar(self.app, type("Core", (), {"ttk": ttk}))
        self.root.update_idletasks()
        labels = tuple(button.cget("text") for button in self.app.vehicle_core_action_buttons)
        self.assertEqual(labels, r2.CRITICAL_UI_CONTRACT["vehicle_core"])
        self.assertTrue(self.app.vehicle_core_toolbar.winfo_ismapped())
        for button in self.app.vehicle_core_action_buttons:
            self.assertTrue(button.winfo_ismapped(), button.cget("text"))

    def test_every_vehicle_core_button_executes_its_original_callback(self):
        r1._install_stable_vehicle_toolbar(self.app, type("Core", (), {"ttk": ttk}))
        self.root.update_idletasks()
        for button in self.app.vehicle_core_action_buttons:
            button.invoke()
        self.assertEqual(
            self.app.calls,
            ["vehicle_form", "edit_vehicle", "vehicle_documents", "vehicle_document_control", "delete_vehicle", "load_vehicles"],
        )

    def test_toolbar_wraps_but_keeps_all_actions_visible_on_narrow_width(self):
        r1._install_stable_vehicle_toolbar(self.app, type("Core", (), {"ttk": ttk}))
        self.root.geometry("520x600")
        self.root.update_idletasks()
        r1._layout_toolbar(self.app, 480)
        self.root.update_idletasks()
        labels = [button.cget("text") for button in self.app.vehicle_core_action_buttons if button.winfo_ismapped()]
        self.assertEqual(tuple(labels), r2.CRITICAL_UI_CONTRACT["vehicle_core"])
        rows = {int(button.grid_info().get("row", 0)) for button in self.app.vehicle_core_action_buttons}
        self.assertGreaterEqual(len(rows), 2)


class RuntimeContractHelperTests(unittest.TestCase):
    def test_missing_contract_labels_reports_exact_loss(self):
        required = r2.CRITICAL_UI_CONTRACT["vehicle_documents"]
        actual = tuple(label for label in required if label != "Додати документ")
        self.assertEqual(r2.missing_contract_labels(actual, required), ("Додати документ",))

    def test_r2_remains_in_runtime_chain(self):
        from pathlib import Path
        source = Path("taxo_app.py").read_text("utf-8")
        self.assertIn("from v1082_features import install as install_v1082", source)
        self.assertIn("App = install_v1082(core, App)", source)

    def test_r2_identity_is_historical_anchor(self):
        from pathlib import Path
        self.assertEqual(r2.APP_VERSION, "10.8-r2")
        self.assertIn('APP_VERSION = "10.8-r2"', Path("v1082_features.py").read_text("utf-8"))
        self.assertIn("v1082_features.py", Path("START.bat").read_text("utf-8"))


if __name__ == "__main__":
    unittest.main()
