# -*- coding: utf-8 -*-
from datetime import date, datetime
from pathlib import Path
import unittest

import v1083_features as r3


class StatementDateNormalizationTests(unittest.TestCase):
    def test_accepts_taxo_display_date(self):
        self.assertEqual(r3.normalize_statement_day("30.09.2026"), "2026-09-30")

    def test_accepts_iso_date(self):
        self.assertEqual(r3.normalize_statement_day("2026-09-30"), "2026-09-30")

    def test_accepts_date_objects(self):
        self.assertEqual(r3.normalize_statement_day(date(2026, 9, 30)), "2026-09-30")
        self.assertEqual(r3.normalize_statement_day(datetime(2026, 9, 30, 12, 0)), "2026-09-30")

    def test_rejects_invalid_date_with_user_friendly_message(self):
        with self.assertRaisesRegex(ValueError, "ДД.ММ.РРРР"):
            r3.normalize_statement_day("31.02.2026")


class RuntimeIdentityTests(unittest.TestCase):
    def test_r3_is_outermost_runtime_layer(self):
        source = Path("taxo_app.py").read_text("utf-8")
        self.assertIn("from v1083_features import install as install_v1083", source)
        self.assertLess(source.index("App = install_v1082(core, App)"), source.index("App = install_v1083(core, App)"))

    def test_r3_identity(self):
        self.assertEqual(r3.APP_VERSION, "10.8-r3")
        self.assertIn("10.8-r3", Path("VERSION.txt").read_text("utf-8"))


if __name__ == "__main__":
    unittest.main()
