# -*- coding: utf-8 -*-
"""10.23-r1: clearing catalog filters must restore the full, safe view."""
from __future__ import annotations

import unittest
from pathlib import Path

from document_catalog_ui import _reset_catalog_filters


class FakeVar:
    def __init__(self, value):
        self.value = value
        self.set_calls = 0

    def get(self):
        return self.value

    def set(self, value):
        self.value = value
        self.set_calls += 1


class DocumentCatalogClearFiltersR3Tests(unittest.TestCase):
    def test_every_filter_returns_to_unrestricted_view(self):
        values = {
            key: FakeVar("обмежено")
            for key in (
                "search", "source", "scan", "date_from", "date_to",
                "kind", "category", "year", "month", "employee", "vehicle",
            )
        }
        state = {
            "sort_field": "number",
            "date_sort": "oldest",
            "number_sort": "descending",
            "page": 3,
        }
        _reset_catalog_filters(values, state)
        expected = {
            "search": "", "source": "Усі — за датою",
            "scan": "Усі", "date_from": "", "date_to": "",
            "kind": "Усі типи", "category": "Усі категорії",
            "year": "Усі роки", "month": "Усі місяці",
            "employee": "Усі працівники", "vehicle": "Усі ТЗ",
        }
        self.assertEqual({key: var.get() for key, var in values.items()}, expected)
        self.assertTrue(all(var.set_calls == 1 for var in values.values()))
        self.assertEqual(
            {key: state[key] for key in ("sort_field", "date_sort", "number_sort", "page")},
            {"sort_field": "date", "date_sort": "newest",
             "number_sort": "ascending", "page": 0},
        )

    def test_reset_is_idempotent(self):
        values = {
            key: FakeVar(value) for key, value in {
                "search": "", "source": "Усі — за датою",
                "scan": "Усі", "date_from": "", "date_to": "",
                "kind": "Усі типи", "category": "Усі категорії",
                "year": "Усі роки", "month": "Усі місяці",
                "employee": "Усі працівники", "vehicle": "Усі ТЗ",
            }.items()
        }
        state = {"sort_field": "date", "date_sort": "newest",
                 "number_sort": "ascending", "page": 0}
        _reset_catalog_filters(values, state)
        self.assertEqual(values["search"].get(), "")
        self.assertEqual(state["page"], 0)

    def test_ui_has_single_refresh_and_suppresses_debounced_search(self):
        root = Path(__file__).resolve().parents[1]
        code = (root / "src/taxo/document_catalog_ui.py").read_text("utf-8")
        self.assertIn('text="Скинути фільтри"', code)
        self.assertIn('command=clear_filters', code)
        self.assertIn('if state["resetting"]:', code)
        self.assertIn('state["after"] = None', code)
        self.assertIn('refresh(reset=True)', code)
        self.assertIn('win._taxo_catalog_clear_filters_button', code)

    def test_current_version(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / "VERSION.txt").read_text("utf-8"), "Version: 10.25-r6\n")
        self.assertIn('APP_VERSION = "10.25-r6"', (root / "main.py").read_text("utf-8"))
        self.assertIn("Taxo 10.25-r6", (root / "START.bat").read_text("utf-8"))


if __name__ == "__main__":
    unittest.main()
