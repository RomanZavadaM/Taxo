import unittest
from datetime import date
from pathlib import Path

import work_analysis_ext as ext


class WorkAnalysisR10Tests(unittest.TestCase):
    def test_signed_minutes_hhmm(self):
        self.assertEqual(ext.signed_minutes_hhmm(690), "+11:30")
        self.assertEqual(ext.signed_minutes_hhmm(-75), "-01:15")
        self.assertEqual(ext.signed_minutes_hhmm(0), "+00:00")

    def test_week_balance_rows_keep_work_and_driving_limits_separate(self):
        monday = date(2026, 9, 7)
        rows = ext.week_balance_rows_from_totals({
            monday: {"work": 49 * 60 + 30, "drive": 42 * 60},
        })
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["work_min"], 49 * 60 + 30)
        self.assertEqual(row["work_balance_min"], 10 * 60 + 30)
        self.assertEqual(row["drive_min"], 42 * 60)
        self.assertEqual(row["drive_balance_min"], 14 * 60)
        self.assertEqual(row["end"], date(2026, 9, 13))

    def test_week_balance_reports_overrun_as_negative_balance(self):
        monday = date(2026, 9, 14)
        rows = ext.week_balance_rows_from_totals({
            monday: {"work": 61 * 60, "drive": 56 * 60 + 20},
        })
        self.assertEqual(rows[0]["work_balance_min"], -60)
        self.assertEqual(rows[0]["drive_balance_min"], -20)

    def test_report_section_is_inserted_before_driving_break_details(self):
        original = [
            ("heading", "ПОТРЕБУЄ УВАГИ"),
            ("ok", "• Немає перевищень."),
            ("heading", "ПЕРЕРВИ У КЕРУВАННІ — ЗА НАШИМИ ЧАСТИНАМИ ЗМІНИ"),
        ]
        data = {
            "week_balances": ext.week_balance_rows_from_totals({
                date(2026, 9, 7): {"work": 48 * 60, "drive": 40 * 60},
            })
        }
        items = ext.extend_report_items(original, data, lambda m: f"{m // 60:02d}:{m % 60:02d}")
        headings = [text for kind, text in items if kind == "heading"]
        self.assertEqual(headings[1], "ТИЖНЕВИЙ ПОГОДИННИЙ БАЛАНС — 60:00 РОБОТА / 56:00 КЕРУВАННЯ")
        self.assertEqual(headings[2], "ПЕРЕРВИ У КЕРУВАННІ — ЗА НАШИМИ ЧАСТИНАМИ ЗМІНИ")
        body = "\n".join(text for _, text in items)
        self.assertIn("баланс до 60:00 +12:00", body)
        self.assertIn("баланс до 56:00 +16:00", body)

    def test_default_pdf_path_is_stable_and_safe(self):
        path = ext.analysis_pdf_default_path(
            Path("Output"),
            "Завада/Роман",
            {"year": 2026, "month": 9},
        )
        self.assertEqual(path.name, "Аналіз_340_Завада_Роман_2026_09.pdf")


if __name__ == "__main__":
    unittest.main()
