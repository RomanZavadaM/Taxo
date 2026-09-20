# -*- coding: utf-8 -*-
import inspect
import unittest

import branding
import branding_asset
import main
import personnel_v91


class TestTaxo101R3ApprovedShell(unittest.TestCase):
    def test_version_marker_is_r3(self):
        self.assertRegex(main.APP_VERSION, r"^10\.1-r\d+(?:\.\d+)*$")

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

    def test_workers_sidebar_opens_personnel_registry_not_legacy_driver_list(self):
        # PersonnelApp wraps the core App at runtime. The approved shell must
        # remap the existing «Працівники» navigation button to tab_personnel.
        personnel_source=inspect.getsource(personnel_v91)
        self.assertIn('nav_buttons.pop(driver_key,None)',personnel_source)
        self.assertTrue(
            'command=lambda:self.show_tab(self.tab_personnel)' in personnel_source
            or 'command=self.show_personnel_overview' in personnel_source
        )
        self.assertIn('nb.select(self.tab_personnel)',personnel_source)

    def test_legacy_registry_action_routes_to_embedded_personnel_page(self):
        source=inspect.getsource(main.App.show_employee_registry)
        selected=inspect.getsource(main.App.selected_employee)
        self.assertIn('personnel_tab=getattr(self,"tab_personnel",None)',source)
        self.assertIn('self.show_tab(personnel_tab)',source)
        self.assertIn('personnel_overview_tree',selected)

    def test_personnel_registry_matches_approved_main_page(self):
        personnel_source=inspect.getsource(personnel_v91)
        self.assertIn('style="Shell.TNotebook"',personnel_source)
        self.assertIn('text="Реєстр працівників"',personnel_source)
        self.assertIn('text="＋  Новий працівник"',personnel_source)
        self.assertIn('text="Відкрити картку"',personnel_source)
        self.assertIn('text="Звільнити / поновити"',personnel_source)
        self.assertIn('text="Пошук"',personnel_source)
        self.assertIn("personnel_search_var",personnel_source)
        self.assertIn("personnel_count_var",personnel_source)
        self.assertIn("_open_personnel_overview_employee",personnel_source)

    def test_personnel_timesheet_remains_branded_and_operational(self):
        source=inspect.getsource(main.App.show_employee_timesheet)
        self.assertIn("draw_brand_header",source)
        self.assertIn("timesheet_status",source)
        self.assertIn("База даних: Підключено",source)
        self.assertIn("Підсумок місяця",source)
        self.assertIn("Щоденний табель",source)

    def test_dynamic_enterprise_name_is_used_in_window_titles(self):
        header=inspect.getsource(main.App._refresh_brand_header)
        timesheet=inspect.getsource(main.App.show_employee_timesheet)
        employee_card=inspect.getsource(main.App.employee_form)
        self.assertIn('self.title(f"Taxo / {company_name} — Облік персоналу")',header)
        self.assertIn('Taxo / {self._company_name_value()} — Табель робочого часу',timesheet)
        self.assertIn('Taxo / {self._company_name_value()} — Картка працівника',employee_card)

    def test_dynamic_enterprise_name_remains_separate_from_logo(self):
        header=inspect.getsource(main.App._refresh_brand_header)
        branding_source=inspect.getsource(branding)
        self.assertIn('title_var.set(f"Taxo / {company_name}")',header)
        self.assertNotIn("АТП Завада",branding_source)
        self.assertIn("create_nav_icon",branding_source)
        self.assertIn("APPROVED_LOGO_PNG_BASE64",branding_source)
        self.assertGreater(len(branding_asset.APPROVED_LOGO_PNG_BASE64),8000)
        image=branding.create_brand_image(256)
        self.assertEqual(image.size,(256,256))


if __name__=="__main__":
    unittest.main()
