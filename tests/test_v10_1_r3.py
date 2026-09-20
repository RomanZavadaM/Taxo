# -*- coding: utf-8 -*-
import inspect
import unittest

import branding
import main


class TestTaxo101R3ApprovedShell(unittest.TestCase):
    def test_version_marker_is_r3(self):
        self.assertEqual(main.APP_VERSION, "10.1-r3")

    def test_main_window_uses_approved_shell_not_native_tab_row(self):
        source=inspect.getsource(main.App.build_ui)
        self.assertIn('style.layout("Shell.TNotebook.Tab",[])',source)
        self.assertIn('sidebar=tk.Frame(shell,bg=PALETTE["sidebar"],width=176)',source)
        self.assertIn('text="Рухаємо людей\\nдо кращого завтра!"',source)
        for label in (
            "Працівники","Табель обліку","Графіки","Транспорт",
            "Маршрути","Документи","Тахограф","Звіти","Налаштування",
        ):
            self.assertIn(label,source)
        self.assertIn("header_clock_var",source)
        self.assertIn("footer_company_var",source)
        self.assertIn("Робоче місце",source)

    def test_windows_menu_moves_into_header_overflow(self):
        source=inspect.getsource(main.App.build_menu)
        self.assertIn("self._app_menu=menubar",source)
        self.assertIn('self.config(menu="")',source)
        popup_source=inspect.getsource(main.App._show_app_menu)
        self.assertIn('getattr(self,"header_menu_button",None)',popup_source)

    def test_personnel_timesheet_uses_same_sidebar_shell(self):
        source=inspect.getsource(main.App.show_employee_timesheet)
        self.assertIn('sidebar=tk.Frame(shell,bg=PALETTE["sidebar"],width=176)',source)
        self.assertIn('"Табель обліку","calendar",lambda:None,active=True',source)
        self.assertIn("timesheet_status",source)
        self.assertIn("База даних: Підключено",source)
        self.assertIn("nav_photo",source)

    def test_dynamic_enterprise_name_remains_separate_from_logo(self):
        header=inspect.getsource(main.App._refresh_brand_header)
        branding_source=inspect.getsource(branding)
        self.assertIn('title_var.set(f"Taxo / {company_name}")',header)
        self.assertNotIn("АТП Завада",branding_source)
        self.assertIn("create_nav_icon",branding_source)


if __name__=="__main__":
    unittest.main()
