# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ShlyakhFieldUiR2Tests(unittest.TestCase):
    def test_ui_declares_field_level_colours_and_decisions(self):
        ui = (ROOT / "v1052_features.py").read_text("utf-8")
        for text in (
            "Зелений = відповідає",
            "синій = можна доповнити",
            "жовтий = розбіжність",
            "червоний = критичний",
            "Прийняти реєстр",
            "Залишити Taxo",
            "Виправити у реєстрі",
            "Відкласти",
            "Історія поля",
        ):
            self.assertIn(text, ui)

    def test_ui_explicitly_preserves_local_only_and_blank_registry_data(self):
        ui = (ROOT / "v1052_features.py").read_text("utf-8")
        self.assertIn("Порожнє або відсутнє у витягу значення ніколи не очищає Taxo", ui)
        self.assertIn("Нічого не видаляється і не деактивується", ui)
        self.assertIn("«Знятий з обліку» не вимикає ТЗ", ui)

    def test_update_all_mode_has_explicit_warning(self):
        ui = (ROOT / "v1052_features.py").read_text("utf-8")
        self.assertIn("цей режим замінить усі непорожні розбіжні поля", ui)
        self.assertIn("Для вибіркового рішення використовуйте кнопки праворуч", ui)

    def test_vehicle_data_window_keeps_other_controls_separate(self):
        ui = (ROOT / "v1052_features.py").read_text("utf-8")
        self.assertIn("Локальні документи ТЗ і військово-транспортний облік — окремі контури", ui)
        self.assertNotIn("import vehicle_documents", ui)
        self.assertNotIn("import military_transport", ui)

    def test_feature_identity_is_r2(self):
        ui = (ROOT / "v1052_features.py").read_text("utf-8")
        self.assertIn('APP_VERSION = "10.5-r2"', ui)
        self.assertIn("import vehicle_reconciliation as reconciliation", ui)


if __name__ == "__main__":
    unittest.main()
