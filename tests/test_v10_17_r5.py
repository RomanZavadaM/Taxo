# -*- coding: utf-8 -*-
"""10.17-r5: tachograph child windows keep explicit non-saving exits."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path

import main
import tachograph

ROOT = Path(__file__).resolve().parents[1]


class TachographDialogCancellationR5Tests(unittest.TestCase):
    def test_revision_identity(self):
        self.assertEqual(main.APP_VERSION, "10.17-r5")
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text("utf-8"),
            "Version: 10.17-r5\n",
        )
        self.assertIn(
            "Taxo 10.17-r5",
            (ROOT / "START.bat").read_text("utf-8"),
        )

    def test_interval_form_has_separate_cancel_and_save_actions(self):
        source = inspect.getsource(tachograph.TachographModule.interval_form)
        self.assertIn('text="Скасувати",command=w.destroy', source)
        self.assertIn('text="Зберегти",command=save', source)
        self.assertNotIn('text="Скасувати",command=save', source)
        self.assertNotIn("WM_DELETE_WINDOW", source)

        save_body = source.split("def save():", 1)[1]
        self.assertIn("UPDATE intervals SET", save_body)
        self.assertIn("INSERT INTO intervals", save_body)
        self.assertIn("con.commit()", save_body)
        self.assertIn("self.load_intervals()", save_body)

    def test_other_tachograph_toplevels_already_have_close_actions(self):
        for method_name in (
            "show_stats_popup",
            "open_scan",
            "show_control_protocols",
        ):
            with self.subTest(method=method_name):
                source = inspect.getsource(
                    getattr(tachograph.TachographModule, method_name)
                )
                self.assertIn('text="Закрити"', source)
                self.assertIn("command=win.destroy", source)


if __name__ == "__main__":
    unittest.main()
