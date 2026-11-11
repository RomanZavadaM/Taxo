# -*- coding: utf-8 -*-
"""10.16-r9: order text presets have an isolated UI controller."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import main
import order_editor_presets_ui
import order_editor_ui

ROOT = Path(__file__).resolve().parents[1]


class FakeText:
    def __init__(self, value):
        self.value = value

    def get(self, start, end):
        return self.value

    def delete(self, start, end):
        self.value = ""

    def insert(self, start, value):
        self.value = value


class OrderEditorPresetsR9Tests(unittest.TestCase):
    def setUp(self):
        self.ops = SimpleNamespace(
            TYPE_GENERIC="generic",
            ORDER_TEXT_PRESETS={
                "assignment": [{
                    "title": "Стандартна",
                    "subject": "Нова тема",
                    "preamble": "Новий вступ",
                    "body": "Нові пункти",
                }],
            },
            DEFAULT_BODY_TEMPLATES={"assignment": "Типові пункти"},
            DEFAULT_SUBJECTS={"assignment": "Типова тема"},
            DEFAULT_PREAMBLES={"assignment": "Типовий вступ"},
        )
        section = order_editor_presets_ui.OrderEditorPresetsSection.__new__(
            order_editor_presets_ui.OrderEditorPresetsSection
        )
        section.core = SimpleNamespace(
            messagebox=SimpleNamespace(
                askyesno=mock.Mock(return_value=False),
                showinfo=mock.Mock(),
            )
        )
        section.ops = self.ops
        section.dialog = object()
        section.force_type = None
        section.type_var = SimpleNamespace(get=lambda: "Закріплення")
        section.type_by_label = {"Закріплення": "assignment"}
        section.subject_var = SimpleNamespace(
            get=mock.Mock(return_value="Моя тема"),
            set=mock.Mock(),
        )
        section.preamble = FakeText("Мій вступ")
        section.body_text = FakeText("Мої пункти")
        section.preset_var = SimpleNamespace(
            get=mock.Mock(return_value="Стандартна"),
            set=mock.Mock(),
        )
        section.preset_rows = list(self.ops.ORDER_TEXT_PRESETS["assignment"])
        section.preset_box = mock.Mock()
        section.frame = mock.Mock()
        self.section = section

    def test_version_and_start_package_guard(self):
        self.assertEqual(main.APP_VERSION, "10.16-r9")
        self.assertEqual(
            (ROOT / "VERSION.txt").read_text(encoding="utf-8"),
            "Version: 10.16-r9\n",
        )
        start = (ROOT / "START.bat").read_text(encoding="utf-8")
        self.assertIn("Taxo 10.16-r9", start)
        self.assertIn("order_editor_presets_ui.py", start)

    def test_editor_delegates_presets_and_keeps_persistence(self):
        source = inspect.getsource(order_editor_ui.open_order_editor)
        self.assertIn(
            "order_editor_presets_ui.install_order_editor_presets(", source
        )
        self.assertIn("preset_section.refresh(", source)
        self.assertIn("command=preset_section.apply", source)
        self.assertNotIn("def apply_template(", source)
        self.assertIn("order_editor_persistence.save_order(", source)

    def test_rejected_replacement_preserves_every_edit(self):
        self.assertFalse(self.section.apply())
        self.assertEqual(self.section.preamble.value, "Мій вступ")
        self.assertEqual(self.section.body_text.value, "Мої пункти")
        self.section.subject_var.set.assert_not_called()
        self.section.core.messagebox.askyesno.assert_called_once()

    def test_accepted_replacement_updates_all_fields(self):
        self.section.core.messagebox.askyesno.return_value = True
        self.assertTrue(self.section.apply())
        self.section.subject_var.set.assert_called_once_with("Нова тема")
        self.assertEqual(self.section.preamble.value, "Новий вступ")
        self.assertEqual(self.section.body_text.value, "Нові пункти")

    def test_refresh_changes_choices_but_not_user_text(self):
        self.section.refresh("assignment", select_first=True)
        self.section.preset_box.configure.assert_called_with(
            values=["Стандартна"]
        )
        self.section.preset_var.set.assert_called_with("Стандартна")
        self.assertEqual(self.section.body_text.value, "Мої пункти")
        self.assertEqual(self.section.preamble.value, "Мій вступ")
        self.section.refresh("generic")
        self.section.frame.grid_remove.assert_called_once()

    def test_missing_preset_without_fallback_does_not_edit(self):
        self.section.preset_rows = []
        self.section.ops.DEFAULT_BODY_TEMPLATES = {}
        self.assertFalse(self.section.apply())
        self.section.core.messagebox.showinfo.assert_called_once()
        self.section.core.messagebox.askyesno.assert_not_called()
        self.assertEqual(self.section.body_text.value, "Мої пункти")

    def test_missing_preset_uses_existing_default_template(self):
        self.section.preset_rows = []
        self.section.core.messagebox.askyesno.return_value = True
        self.assertTrue(self.section.apply())
        self.section.subject_var.set.assert_called_once_with("Типова тема")
        self.assertEqual(self.section.preamble.value, "Типовий вступ")
        self.assertEqual(self.section.body_text.value, "Типові пункти")


if __name__ == "__main__":
    unittest.main()
