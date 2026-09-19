import inspect
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main


class _Var:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class TestR97MonthlyShiftDetailOpen(unittest.TestCase):
    def test_monthly_shift_window_exposes_open_detail_button(self):
        source = inspect.getsource(main.App.show_monthly_shift_schedule)
        self.assertIn('text="Відкрити деталізацію"', source)
        self.assertIn("command=self.open_monthly_shift_detail_pdf", source)

    def test_open_detail_regenerates_current_pdf_and_opens_it(self):
        app = object.__new__(main.App)
        app.monthly_shift_year = _Var(2026)
        app.monthly_shift_month = _Var(9)
        app.monthly_shift_active_only = _Var(True)
        app.monthly_shift_win = object()
        app.monthly_shift_last_detail_pdf = None

        with tempfile.TemporaryDirectory() as folder:
            output_dir = Path(folder)
            generated = output_dir / "opened-detail.pdf"

            def fake_write(writer, path, **kwargs):
                self.assertEqual(
                    Path(path).name,
                    "Деталізація_графіка_змінності_2026_09.pdf",
                )
                writer(generated)
                return generated

            with (
                patch.object(main, "OUTPUT_DIR", output_dir),
                patch.object(main, "write_output_file", side_effect=fake_write),
                patch.object(main, "export_monthly_shift_detail_pdf") as export_detail,
                patch.object(main, "open_external") as open_external,
            ):
                main.App.open_monthly_shift_detail_pdf(app)

            export_detail.assert_called_once_with(
                2026, 9, generated, active_only=True
            )
            open_external.assert_called_once_with(generated)
            self.assertEqual(app.monthly_shift_last_detail_pdf, generated)


if __name__ == "__main__":
    unittest.main()
