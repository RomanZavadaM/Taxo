import inspect
import unittest
from pathlib import Path

import v10710_features as feature


class Taxo107R10Tests(unittest.TestCase):
    def test_version_identity(self):
        self.assertEqual(feature.APP_VERSION, "10.7-r10")
        root = Path(__file__).resolve().parents[1]
        self.assertIn("Version: 10.7-r10", (root / "VERSION.txt").read_text("utf-8"))
        self.assertIn('APP_VERSION = "10.7-r10"', (root / "main.py").read_text("utf-8"))

    def test_runtime_layer_is_outermost(self):
        source = (Path(__file__).resolve().parents[1] / "taxo_app.py").read_text("utf-8")
        self.assertIn("from v10710_features import install as install_v10710", source)
        self.assertGreater(source.index("App = install_v10710(core, App)"), source.index("App = install_v1079(core, App)"))

    def test_document_center_groups_are_explicit(self):
        groups = dict(feature.DOCUMENT_CENTER_GROUPS)
        self.assertEqual(set(groups), {"Операційні документи", "Транспорт", "Військовий облік", "Персонал"})
        self.assertIn(("Шляхові листи на день", "show_waybills_for_schedule"), groups["Операційні документи"])
        self.assertIn(("Контроль документів ТЗ", "vehicle_document_control"), groups["Транспорт"])
        self.assertIn(("Відомість ТЦК — транспорт підприємства", "open_military_transport_statement"), groups["Військовий облік"])
        self.assertIn(("Реєстр усіх працівників", "show_employee_registry"), groups["Персонал"])

    def test_document_center_reuses_existing_operations_tabs(self):
        source = inspect.getsource(feature._install_document_tab)
        self.assertIn('text="Документи"', source)
        self.assertIn('text="Накази та розпорядження"', source)
        for title in ("Накази", "Закріплення водіїв", "Відповідальні", "Каталог наказів"):
            self.assertIn(title, source)

    def test_ui_layer_does_not_mutate_business_tables(self):
        source = Path(feature.__file__).read_text("utf-8").upper()
        self.assertNotIn("INSERT INTO", source)
        self.assertNotIn("DELETE FROM", source)
        self.assertNotIn("UPDATE OPERATIONS_", source)

    def test_start_guard_requires_r10_runtime(self):
        start = (Path(__file__).resolve().parents[1] / "START.bat").read_text("ascii")
        self.assertIn("v10710_features.py", start)

    def test_tab_selector_finds_exact_title(self):
        class FakeBook:
            def __init__(self):
                self.selected = None
            def tabs(self):
                return ("a", "b")
            def tab(self, tab_id, key):
                return {"a": "Накази", "b": "Відповідальні"}[tab_id]
            def select(self, tab_id):
                self.selected = tab_id
        book = FakeBook()
        self.assertTrue(feature._select_tab(book, "Відповідальні"))
        self.assertEqual(book.selected, "b")
        self.assertFalse(feature._select_tab(book, "Немає"))


if __name__ == "__main__":
    unittest.main()
