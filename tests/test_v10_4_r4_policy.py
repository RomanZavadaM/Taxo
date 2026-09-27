# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

import v1044_features


class TestTaxo104R4AuditPolicy(unittest.TestCase):
    def test_r4_never_rewrites_waybill_boundary_times(self):
        source=Path(v1044_features.__file__).read_text("utf-8")
        self.assertNotIn("def _waybill_schedule_rows",source)
        self.assertIn("Перевірте введення графіка маршруту.",source)
        self.assertIn("Помилка виконання аудиту",source)


if __name__=="__main__":
    unittest.main()
