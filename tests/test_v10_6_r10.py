# -*- coding: utf-8 -*-
import pathlib
import unittest

import personnel_v91 as personnel
import v10610_features as r10


class P5EdrpouNormalizationTests(unittest.TestCase):
    def test_positional_edrpou_is_not_duplicated(self):
        args = (object(), 2026, 10, "out.pdf", True, "28.09.2026", "", "32764314")
        call_args, call_kwargs = r10.normalize_edrpou_call(args, {}, "99999999")
        self.assertEqual(call_args[7], "32764314")
        self.assertNotIn("edrpou", call_kwargs)

    def test_blank_positional_edrpou_gets_company_fallback(self):
        args = (object(), 2026, 10, "out.pdf", True, None, "", "")
        call_args, call_kwargs = r10.normalize_edrpou_call(args, {}, "32764314")
        self.assertEqual(call_args[7], "32764314")
        self.assertNotIn("edrpou", call_kwargs)

    def test_keyword_edrpou_is_preserved(self):
        args = (object(), 2026, 10, "out.pdf")
        call_args, call_kwargs = r10.normalize_edrpou_call(
            args, {"edrpou": "12345678"}, "32764314"
        )
        self.assertEqual(call_kwargs["edrpou"], "12345678")

    def test_missing_keyword_edrpou_gets_company_fallback(self):
        args = (object(), 2026, 10, "out.pdf")
        _call_args, call_kwargs = r10.normalize_edrpou_call(args, {}, "32764314")
        self.assertEqual(call_kwargs["edrpou"], "32764314")

    def test_positional_value_wins_over_duplicate_keyword(self):
        args = (object(), 2026, 10, "out.pdf", True, None, "", "32764314")
        call_args, call_kwargs = r10.normalize_edrpou_call(
            args, {"edrpou": "SHOULD_NOT_SURVIVE"}, "99999999"
        )
        self.assertEqual(call_args[7], "32764314")
        self.assertNotIn("edrpou", call_kwargs)


class P5ExporterPatchTests(unittest.TestCase):
    def setUp(self):
        self.old_pdf = personnel.export_p5_pdf
        self.old_xlsx = personnel.export_p5_xlsx
        self.old_marker = getattr(personnel, "_taxo_v10610_p5_patched", None)
        self.old_company = r10.company_edrpou
        if hasattr(personnel, "_taxo_v10610_p5_patched"):
            delattr(personnel, "_taxo_v10610_p5_patched")
        r10.company_edrpou = lambda _core: "32764314"
        self.calls = []

        def base_export(self_obj, year, month, out_path, active_only=True,
                        form_date=None, department="", edrpou="",
                        use_plan_when_fact_missing=False, include_summary=False):
            self.calls.append((out_path, edrpou))
            return edrpou

        personnel.export_p5_pdf = base_export
        personnel.export_p5_xlsx = base_export
        r10._patch_p5_exporters(object())

    def tearDown(self):
        personnel.export_p5_pdf = self.old_pdf
        personnel.export_p5_xlsx = self.old_xlsx
        r10.company_edrpou = self.old_company
        for name in (
            "_taxo_v10610_p5_patched",
            "_taxo_v10610_base_p5_pdf",
            "_taxo_v10610_base_p5_xlsx",
        ):
            if hasattr(personnel, name):
                delattr(personnel, name)
        if self.old_marker is not None:
            personnel._taxo_v10610_p5_patched = self.old_marker

    def test_pdf_accepts_positional_edrpou_without_typeerror(self):
        result = personnel.export_p5_pdf(
            object(), 2026, 10, "out.pdf", True, "28.09.2026", "", "32764314"
        )
        self.assertEqual(result, "32764314")
        self.assertEqual(self.calls[-1], ("out.pdf", "32764314"))

    def test_xlsx_accepts_positional_edrpou_without_typeerror(self):
        result = personnel.export_p5_xlsx(
            object(), 2026, 10, "out.xlsx", True, "28.09.2026", "", "32764314"
        )
        self.assertEqual(result, "32764314")
        self.assertEqual(self.calls[-1], ("out.xlsx", "32764314"))

    def test_pdf_blank_positional_edrpou_uses_company_value(self):
        result = personnel.export_p5_pdf(
            object(), 2026, 10, "out.pdf", True, None, "", ""
        )
        self.assertEqual(result, "32764314")


class R10IdentityTests(unittest.TestCase):
    def test_version_file_is_r10(self):
        text = pathlib.Path("VERSION.txt").read_text(encoding="utf-8")
        self.assertIn("Version: 10.6-r10", text)

    def test_taxo_app_installs_r10_outermost(self):
        text = pathlib.Path("taxo_app.py").read_text(encoding="utf-8")
        self.assertIn("from v10610_features import install as install_v10610", text)
        self.assertIn("App = install_v10610(core, App)", text)


if __name__ == "__main__":
    unittest.main()
