# -*- coding: utf-8 -*-
"""10.14-r1: order PDF output must retain earlier prints and use Taxo preview."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import main
from order_pdf_workflow import order_pdf_path, save_and_preview_order


class OrderPdfWorkflowTests(unittest.TestCase):
    def test_version_and_package_identity(self):
        self.assertIn(main.APP_VERSION, ("10.14-r1", "10.14-r2", "10.14-r3", "10.14-r4", "10.14-r5", "10.14-r6", "10.14-r7", "10.14-r8", "10.14-r9", "10.14-r10", "10.15-r1", "10.15-r2", "10.15-r3", "10.15-r4", "10.15-r5"))
        self.assertIn(main.APP_VERSION, Path("VERSION.txt").read_text(encoding="utf-8"))
        start = Path("START.bat").read_text(encoding="utf-8")
        self.assertIn("Taxo " + main.APP_VERSION, start)
        self.assertIn("order_pdf_workflow.py", start)

    def test_new_print_does_not_overwrite_existing_document(self):
        order = {"order_no": "1-К", "order_date": "09.11.2026"}
        with tempfile.TemporaryDirectory() as root:
            original = Path(root) / "Наказ_1-К_09.11.2026.pdf"
            original.write_bytes(b"previous signed version")
            new_path = order_pdf_path(root, order)
            self.assertNotEqual(new_path, original)
            self.assertEqual(original.read_bytes(), b"previous signed version")
            self.assertEqual(new_path.suffix, ".pdf")

    def test_saved_pdf_is_opened_by_internal_viewer(self):
        with tempfile.TemporaryDirectory() as root:
            viewer = Mock()
            os_open = Mock()
            warning = Mock()
            def save(writer, target, **_kw):
                writer(Path(target))
                return Path(target)
            def fake_export(path, *_args, **_kw):
                Path(path).write_bytes(b"%PDF-1.4 test")
            core = SimpleNamespace(
                OUTPUT_DIR=Path(root), Path=Path,
                report_font_candidates=lambda: [],
                write_output_file=save,
                open_document=viewer,
                open_external=os_open,
                messagebox=SimpleNamespace(showwarning=warning),
            )
            ops = SimpleNamespace(export_order_pdf=fake_export)
            order = {"order_no": "5", "order_date": "2026-11-09"}
            first = save_and_preview_order(core, ops, order, [], {}, "", None)
            self.assertTrue(first.exists())
            viewer.assert_called_once_with(None, first, external_opener=os_open)
            self.assertFalse(os_open.called)
            self.assertFalse(warning.called)
            second = save_and_preview_order(core, ops, order, [], {}, "", None)
            self.assertNotEqual(first, second)
            self.assertTrue(first.exists())
            self.assertTrue(second.exists())

    def test_cancelled_save_never_opens_old_pdf(self):
        with tempfile.TemporaryDirectory() as root:
            viewer = Mock()
            core = SimpleNamespace(
                OUTPUT_DIR=Path(root), Path=Path,
                report_font_candidates=lambda: [],
                write_output_file=lambda *_a, **_kw: None,
                open_document=viewer, open_external=Mock(),
                messagebox=SimpleNamespace(showwarning=Mock()),
            )
            result = save_and_preview_order(
                core, SimpleNamespace(export_order_pdf=Mock()),
                {"order_no": "5", "order_date": "2026-11-09"},
                [], {}, "", None,
            )
            self.assertIsNone(result)
            viewer.assert_not_called()

    def test_orders_ui_keeps_preview_and_print_entry_points(self):
        source = Path("src/taxo/operations_orders_ui.py").read_text(encoding="utf-8")
        self.assertIn("preview_order(created_order)", source)
        self.assertIn('("Переглянути / друк", preview_order', source)
        self.assertIn("save_and_preview_order(", source)


if __name__ == "__main__":
    unittest.main()
