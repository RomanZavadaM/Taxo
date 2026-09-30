# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import unittest
from datetime import date
from pathlib import Path

import main as core
import personnel_v91 as personnel
import v1075_features as r5


class HistoricalPersonnelScopeTests(unittest.TestCase):
    def test_employee_employed_on_uses_dated_employment_not_current_active_flag(self):
        employee = {
            "employment_date": "2026-01-10",
            "dismissal_date": "2026-06-30",
            "active": 0,
        }
        self.assertTrue(core.employee_employed_on(employee, date(2026, 5, 15)))
        self.assertTrue(core.employee_employed_on(employee, date(2026, 6, 30)))
        self.assertFalse(core.employee_employed_on(employee, date(2026, 7, 1)))

    def test_report_storage_filter_must_not_drop_currently_inactive_employee(self):
        self.assertFalse(r5.historical_report_active_only(True))
        self.assertFalse(r5.historical_report_active_only(False))

    def test_install_wraps_report_collectors_but_not_active_ui_helper(self):
        original_week = personnel.collect_personnel_week_balance
        original_audit = personnel.collect_personnel_timesheet_audit
        original_p5 = personnel.collect_p5_data
        original_all_rows = personnel._all_employee_rows
        old_flag = getattr(core, "_TAXO_V1075_INSTALLED", None)
        old_version = core.APP_VERSION
        calls = []
        try:
            if hasattr(core, "_TAXO_V1075_INSTALLED"):
                delattr(core, "_TAXO_V1075_INSTALLED")

            personnel.collect_personnel_week_balance = (
                lambda core_arg, anchor_date, active_only=True:
                calls.append(("week", active_only)) or {"ok": True}
            )
            personnel.collect_personnel_timesheet_audit = (
                lambda core_arg, year, month, active_only=True:
                calls.append(("audit", active_only)) or {"ok": True}
            )
            personnel.collect_p5_data = (
                lambda core_arg, year, month, active_only=True, use_plan_when_fact_missing=False:
                calls.append(("p5", active_only, use_plan_when_fact_missing)) or {"ok": True}
            )
            preserved_helper = personnel._all_employee_rows

            r5.install(core, object)
            personnel.collect_personnel_week_balance(core, date(2026, 5, 1), True)
            personnel.collect_personnel_timesheet_audit(core, 2026, 5, True)
            personnel.collect_p5_data(core, 2026, 5, True, True)

            self.assertEqual(calls[0], ("week", False))
            self.assertEqual(calls[1], ("audit", False))
            self.assertEqual(calls[2], ("p5", False, True))
            self.assertIs(personnel._all_employee_rows, preserved_helper)
            self.assertEqual(core.APP_VERSION, "10.7-r5")
        finally:
            personnel.collect_personnel_week_balance = original_week
            personnel.collect_personnel_timesheet_audit = original_audit
            personnel.collect_p5_data = original_p5
            personnel._all_employee_rows = original_all_rows
            core.APP_VERSION = old_version
            if old_flag is None:
                if hasattr(core, "_TAXO_V1075_INSTALLED"):
                    delattr(core, "_TAXO_V1075_INSTALLED")
            else:
                core._TAXO_V1075_INSTALLED = old_flag

    def test_runtime_entrypoint_contains_r5_layer(self):
        text = Path("taxo_app.py").read_text(encoding="utf-8")
        self.assertIn("from v1075_features import install as install_v1075", text)
        self.assertIn("App = install_v1075(core, App)", text)

    def test_r5_identity_is_historical_while_current_version_may_advance(self):
        release = Path("docs/releases/RELEASE_NOTES_v10.7-r5.md").read_text(encoding="utf-8")
        self.assertIn("Taxo 10.7-r5", release)
        self.assertIn('APP_VERSION = "10.7-r5"', Path("v1075_features.py").read_text(encoding="utf-8"))

        current = Path("VERSION.txt").read_text(encoding="utf-8")
        m = re.search(r"Version:\s*(\d+)\.(\d+)-r(\d+)", current)
        self.assertIsNotNone(m)
        self.assertGreaterEqual(tuple(map(int, m.groups())), (10, 7, 5))


if __name__ == "__main__":
    unittest.main()
