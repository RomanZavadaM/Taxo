# -*- coding: utf-8 -*-
import inspect
import unittest

import branding
import main


class TestTaxo101R2UiRefresh(unittest.TestCase):
    def test_r2_release_notes_remain_historical(self):
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]
        notes=(root/"docs/releases/RELEASE_NOTES_v10_1_r2.md").read_text("utf-8")
        self.assertIn("Taxo 10.1-r2",notes)
        self.assertIn("135 tests / OK",notes)

    def test_timesheet_exposes_reports_and_detail_actions(self):
        source = inspect.getsource(main.App.show_employee_timesheet)
        for marker in (
            "Відкрити деталізацію",
            "PDF звіт",
            "Excel звіт",
            "Підсумки / контроль",
            "Місячний табель / баланс",
            'text="П-5"',
        ):
            self.assertIn(marker, source)

    def test_timesheet_has_live_summary_and_daily_cards(self):
        source = inspect.getsource(main.App.show_employee_timesheet)
        self.assertIn("summary_stat_vars", source)
        self.assertIn("daily_stat_vars", source)
        self.assertIn('summary_tree.tag_configure("missing"', source)
        self.assertIn('daily_tree.tag_configure("missing"', source)
        self.assertIn('"Немає факту"', source)

    def test_unsafe_mass_fill_button_is_not_exposed(self):
        source = inspect.getsource(main.App.show_employee_timesheet)
        self.assertNotIn('text="⚠ Порожні будні — план 8 год"', source)
        self.assertIn(
            "Масове «8 год у порожні будні» прибрано",
            source,
        )

    def test_about_window_is_branded_and_dynamic(self):
        source = inspect.getsource(main.App.show_about)
        self.assertIn("brand_photo", source)
        self.assertIn("self._company_name_value()", source)
        self.assertIn("Робоче сховище", source)
        self.assertIn("Резервні копії", source)
        self.assertIn("GitHub / поточний реліз", source)

    def test_help_window_has_search_topics_and_f1_menu(self):
        help_source = inspect.getsource(main.App.show_help)
        menu_source = inspect.getsource(main.App.build_menu)
        for topic in (
            "Початок роботи",
            "Працівники й ролі",
            "Табелі",
            "Маршрути і транспорт",
            "Документи і П-5",
            "Тахограф",
            "Резервні копії",
            "Гарячі клавіші",
            "FAQ",
        ):
            self.assertIn(topic, help_source)
        self.assertIn('accelerator="F1"', menu_source)
        self.assertIn('self.bind_all("<F1>"', menu_source)

    def test_employee_card_visually_separates_employment_and_roles(self):
        source = inspect.getsource(main.App.employee_form)
        self.assertIn("Спеціальні ролі", source)
        self.assertIn("Стан працівника", source)
        self.assertIn("Роль і статус працевлаштування не змішуються", source)
        self.assertIn("current_driver_end", source)
        self.assertIn("stored_driver_end", source)

    def test_company_settings_has_live_header_preview(self):
        source = inspect.getsource(main.App.build_company)
        self.assertIn("Попередній перегляд шапки", source)
        self.assertIn("_refresh_company_preview", source)
        self.assertIn("Назва підприємства", source)

    def test_brand_art_is_text_free_and_uses_approved_palette(self):
        source = inspect.getsource(branding)
        self.assertNotIn("АТП Завада", source)
        image = branding.create_brand_image(128)
        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(image.size, (128, 128))
        self.assertIsNotNone(image.getbbox())


if __name__ == "__main__":
    unittest.main()
