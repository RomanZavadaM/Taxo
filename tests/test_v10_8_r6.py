import ast
import tempfile
import unittest
from pathlib import Path

import main
import output_files


ROOT = Path(__file__).resolve().parents[1]


class MainModularizationR6Tests(unittest.TestCase):
    def test_r6_identity_is_historical_anchor(self):
        notes = (ROOT / "docs/releases/RELEASE_NOTES_v10.8-r6.md").read_text(encoding="utf-8")
        self.assertIn("10.8-r6", notes)
        self.assertGreaterEqual(tuple(int(part) for part in main.APP_VERSION.replace("10.8-r", "").split(".")), (6,))

    def test_output_helpers_are_no_longer_implemented_in_main(self):
        source = (ROOT / "main.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        top_functions = {
            node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        for name in (
            "open_external",
            "report_font_candidates",
            "_is_file_access_error",
            "_next_output_copy_path",
            "_ask_locked_file_action",
            "_friendly_file_error",
        ):
            self.assertNotIn(name, top_functions)
        self.assertIn("from output_files import", source)

    def test_main_keeps_public_compatibility_names(self):
        self.assertIs(main.open_external, output_files.open_external)
        self.assertIs(main.report_font_candidates, output_files.report_font_candidates)
        self.assertIs(main._is_file_access_error, output_files.is_file_access_error)
        self.assertIs(main._friendly_file_error, output_files.friendly_file_error)

    def test_start_guard_requires_r6_runtime_modules(self):
        start = (ROOT / "START.bat").read_text(encoding="ascii")
        self.assertIn('if not exist "output_files.py" goto :package_incomplete', start)
        self.assertIn('if not exist "v1085_features.py" goto :package_incomplete', start)
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text(encoding="utf-8")
        self.assertIn("output_files.py", workflow)
        self.assertIn("v1085_features.py", workflow)

    def test_unique_copy_name_stays_human_readable(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "report.pdf"
            target.write_bytes(b"busy")
            candidate = output_files.next_output_copy_path(target)
            self.assertEqual(candidate.parent, target.parent)
            self.assertEqual(candidate.suffix, ".pdf")
            self.assertTrue(candidate.name.startswith("report_"))
            self.assertNotIn("(1)", candidate.name)

    def test_permission_error_stays_classified(self):
        self.assertTrue(output_files.is_file_access_error(PermissionError("busy")))
        msg = output_files.friendly_file_error(PermissionError("busy"), "x.pdf", "PDF")
        self.assertIn("Немає доступу", msg)


if __name__ == "__main__":
    unittest.main()
