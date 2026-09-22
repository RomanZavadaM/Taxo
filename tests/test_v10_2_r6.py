# -*- coding: utf-8 -*-
import inspect
import unittest

import main


class TestTaxo102R6SecondaryWindowStyle(unittest.TestCase):
    def test_r6_or_later_keeps_secondary_window_style(self):
        # This is a persistence test for the r6 UI rule, not a restriction
        # that the whole project must forever stay on 10.2.
        self.assertTrue(main.APP_VERSION.startswith("10."))

    def test_secondary_window_helper_uses_dynamic_branding(self):
        source=inspect.getsource(main.App._decorate_secondary_window)
        self.assertIn("configure_toplevel(win)", source)
        self.assertIn("draw_brand_header", source)
        self.assertIn("self._company_name_value()", source)
        self.assertIn("APP_VERSION", source)

    def test_major_secondary_windows_use_approved_decorator(self):
        functions=(
            main.App.show_vehicle_documents_report,
            main.App.manual_backup,
            main.App.show_workspace_manager,
            main.App.show_employee_registry,
            main.App.show_monthly_work_balance,
            main.App.show_schedule_integrity_audit,
            main.App.show_monthly_shift_schedule,
            main.App.show_dispatch_staff_schedule,
            main.App.show_waybills_for_schedule,
            main.App.show_work_analysis,
            main.App.show_attestation_gap_control,
            main.App.show_attestation_audit,
        )
        for fn in functions:
            with self.subTest(function=fn.__name__):
                self.assertIn(
                    "self._decorate_secondary_window(",
                    inspect.getsource(fn),
                )

    def test_secondary_ui_step_does_not_change_schema_initialization(self):
        helper=inspect.getsource(main.App._decorate_secondary_window)
        self.assertNotIn("ALTER TABLE", helper)
        self.assertNotIn("CREATE TABLE", helper)
        self.assertNotIn("UPDATE ", helper)
        self.assertNotIn("DELETE ", helper)


if __name__=="__main__":
    unittest.main()
