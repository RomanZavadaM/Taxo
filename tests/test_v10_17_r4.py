# -*- coding: utf-8 -*-
"""10.17-r4: STOIR child dialogs must have a non-saving Cancel action."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path

import main
import vehicle_maintenance_ui

ROOT = Path(__file__).resolve().parents[1]


class StoirDialogCancellationR4Tests(unittest.TestCase):
    def test_revision_identity(self):
        self.assertIn(main.APP_VERSION, ("10.17-r4", "10.17-r5", "10.17-r6", "10.17-r7", "10.17-r8", "10.17-r9"))
        self.assertEqual((ROOT / "VERSION.txt").read_text("utf-8"),
                         "Version: " + main.APP_VERSION + "\n")
        self.assertIn("Taxo " + main.APP_VERSION, (ROOT / "START.bat").read_text("utf-8"))

    def test_each_stoir_dialog_has_cancel_and_explicit_save(self):
        source = inspect.getsource(vehicle_maintenance_ui.open_maintenance_center)
        sections = [
            (source.split("    def edit_profile(", 1)[1].split("    overview_actions =", 1)[0],
             "Зберегти профіль"),
            (source.split("    def add_event(", 1)[1].split("    for text, event in", 1)[0],
             "Зберегти"),
            (source.split("    def add_request(", 1)[1].split("    def selected_request_row(", 1)[0],
             "Створити заявку"),
            (source.split("    def request_update_dialog(", 1)[1].split("    core.ttk.Button(\n        request_top,", 1)[0],
             "Закрити заявку"),
        ]
        for body, positive_action in sections:
            with self.subTest(action=positive_action):
                self.assertIn('text="Скасувати", command=dialog.destroy', body)
                self.assertIn(positive_action, body)
                self.assertIn("dialog.destroy()", body)
        # One Cancel on each of four forms, with no connection to Save.
        self.assertEqual(source.count('text="Скасувати", command=dialog.destroy'), 4)

    def test_write_paths_are_only_explicit_save_callbacks(self):
        source = inspect.getsource(vehicle_maintenance_ui.open_maintenance_center)
        self.assertIn("maint.save_profile(", source)
        self.assertIn("maint.record_event(", source)
        self.assertIn("maint.create_repair_request(", source)
        self.assertIn("maint.update_repair_request(", source)
        for save_action in ("save_profile", "save", "save_request"):
            self.assertIn("command=" + save_action, source)
        self.assertNotIn('text="Скасувати", command=save', source)
        self.assertNotIn('text="Скасувати", command=refresh', source)


if __name__ == "__main__":
    unittest.main()
