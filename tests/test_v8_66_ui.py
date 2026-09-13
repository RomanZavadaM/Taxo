import inspect
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock


_temporary_home = tempfile.TemporaryDirectory()
_original_path_home = Path.home
Path.home = classmethod(lambda cls: Path(_temporary_home.name))
try:
    import main
    import tachograph
finally:
    Path.home = _original_path_home


class FakeWindow:
    def __init__(self, screen=(1366, 768)):
        self.screen = screen
        self.geometry_value = None
        self.minimum = None
        self.resize_value = None

    def update_idletasks(self):
        pass

    def winfo_screenwidth(self):
        return self.screen[0]

    def winfo_screenheight(self):
        return self.screen[1]

    def geometry(self, value):
        self.geometry_value = value

    def minsize(self, width, height):
        self.minimum = (width, height)

    def resizable(self, width, height):
        self.resize_value = (width, height)


class FakeTextInput:
    def __init__(self, widget_class="TEntry", state="normal"):
        self.widget_class = widget_class
        self.state = state
        self.events = []
        self.selection = None
        self.cursor = None

    def winfo_class(self):
        return self.widget_class

    def cget(self, name):
        if name == "state":
            return self.state
        raise KeyError(name)

    def event_generate(self, event):
        self.events.append(event)

    def selection_range(self, start, end):
        self.selection = (start, end)

    def icursor(self, where):
        self.cursor = where


class UiInfrastructureTests(unittest.TestCase):
    def setUp(self):
        self.app = object.__new__(main.App)

    def test_shortcuts_work_with_latin_ukrainian_and_windows_keycodes(self):
        cases = {
            "c": "copy",
            "Cyrillic_es": "copy",
            "с": "copy",
            "Cyrillic_em": "paste",
            "м": "paste",
            "Cyrillic_che": "cut",
            "ф": "select_all",
            "я": "undo",
            "н": "redo",
        }
        for key, expected in cases.items():
            with self.subTest(key=key):
                self.assertEqual(main.ctrl_shortcut_action(key), expected)
        with mock.patch.object(main.sys, "platform", "win32"):
            self.assertEqual(main.ctrl_shortcut_action("unknown", 86), "paste")

    def test_virtual_paste_is_sent_to_editable_field(self):
        widget = FakeTextInput()
        self.assertTrue(main.App._run_edit_action(self.app, widget, "paste"))
        self.assertEqual(widget.events, ["<<Paste>>"])

    def test_readonly_field_can_copy_but_cannot_paste(self):
        widget = FakeTextInput(state="readonly")
        self.assertFalse(main.App._run_edit_action(self.app, widget, "paste"))
        self.assertTrue(main.App._run_edit_action(self.app, widget, "copy"))
        self.assertEqual(widget.events, ["<<Copy>>"])

    def test_select_all_entry(self):
        widget = FakeTextInput()
        self.assertTrue(main.App._run_edit_action(self.app, widget, "select_all"))
        self.assertEqual(widget.selection, (0, "end"))
        self.assertEqual(widget.cursor, "end")

    def test_large_dialog_is_clamped_to_laptop_screen(self):
        win = FakeWindow((1366, 768))
        main.fit_window_to_screen(win, 1450, 760, 900, 500)
        self.assertEqual(win.geometry_value, "1286x648")
        self.assertEqual(win.minimum, (900, 500))
        self.assertEqual(win.resize_value, (True, True))

    def test_driver_form_has_vertical_scrollbar_and_mouse_wheel(self):
        source = inspect.getsource(main.App.driver_form)
        self.assertIn('orient="vertical",command=form_canvas.yview', source)
        self.assertIn('win.bind("<MouseWheel>",scroll_driver_form', source)
        self.assertIn('form_canvas.configure(scrollregion=form_canvas.bbox("all"))', source)

    def test_driver_employment_date_controls_work_period_visibility(self):
        future={"employment_date":"2026-10-01"}
        current={"employment_date":"2026-09-15"}
        legacy={"employment_date":""}
        self.assertFalse(main.driver_employed_on(future,date(2026,9,30)))
        self.assertTrue(main.driver_employed_on(future,date(2026,10,1)))
        self.assertFalse(main.driver_employed_on(current,date(2026,9,14)))
        self.assertTrue(main.driver_employed_on(current,date(2026,9,15)))
        self.assertTrue(main.driver_employed_on(legacy,date(2020,1,1)))

    def test_monthly_reports_exclude_not_yet_hired_drivers(self):
        main.init_db()
        con=main.db()
        marker="test-employment-filter"
        try:
            con.execute(
                "INSERT INTO drivers(last_name,first_name,employment_date,active,created_at) VALUES(?,?,?,?,?)",
                ("FutureTest","Driver","2026-10-01",1,marker)
            )
            con.execute(
                "INSERT INTO drivers(last_name,first_name,employment_date,active,created_at) VALUES(?,?,?,?,?)",
                ("CurrentTest","Driver","2026-09-15",1,marker)
            )
            con.commit()
            balance=main.collect_monthly_work_balance(2026,9)
            schedule=main.collect_monthly_shift_schedule(2026,9)
            balance_names={d["name"] for d in balance["drivers"]}
            schedule_names={d["name"] for d in schedule["drivers"]}
            self.assertNotIn("FutureTest Driver",balance_names)
            self.assertNotIn("FutureTest Driver",schedule_names)
            self.assertIn("CurrentTest Driver",balance_names)
            current=next(d for d in balance["drivers"] if d["name"]=="CurrentTest Driver")
            self.assertEqual(current["cells"][4],"")
            self.assertEqual(current["cells"][18],"В")
        finally:
            con.execute("DELETE FROM drivers WHERE created_at=?",(marker,))
            con.commit()
            con.close()

    def test_daily_schedule_and_autofill_use_employment_boundary(self):
        schedule_source=inspect.getsource(main.App.refresh_schedule)
        add_source=inspect.getsource(main.App.schedule_add_period)
        fill_source=inspect.getsource(main.App.autofill)
        month_source=inspect.getsource(main.App.refresh_month)
        self.assertIn("driver_employed_on(dr,d)",schedule_source)
        self.assertIn("driver_employed_on(dr,d)",add_source)
        self.assertIn("driver_employed_on(driver,d)",fill_source)
        self.assertIn("driver_employed_on(driver,d)",month_source)

    def test_main_menu_is_really_built(self):
        source = inspect.getsource(main.App.__init__)
        self.assertIn("self.build_menu()", source)

    def test_scrollable_tabs_do_not_remove_global_bindings(self):
        source = inspect.getsource(main.App._make_scrollable_tab_body)
        self.assertNotIn("unbind_all", source)

    def test_tachograph_timeline_precedes_expandable_image_body(self):
        source = inspect.getsource(tachograph.TachographModule.build)
        self.assertLess(source.index("self.timeline_box=timeline_box"), source.index("body=ttk.Panedwindow"))
        self.assertIn('text="Підсумкова статистика"', source)

    def test_tachograph_preview_is_visible_and_opens_full_scan(self):
        source = inspect.getsource(tachograph.TachographModule.build)
        self.assertIn('text="Перегляд тахокарти — подвійний клік відкриває велике вікно"', source)
        self.assertIn('text="Вмістити"', source)
        self.assertIn('text="100%"', source)
        self.assertIn('text="Збільшити перегляд"', source)
        self.assertIn('body.bind("<Map>"', source)

    def test_full_scan_window_starts_fitted_and_keeps_actual_size_mode(self):
        source = inspect.getsource(tachograph.TachographModule.open_scan)
        self.assertIn('view_mode=tk.StringVar(value="fit")', source)
        self.assertIn('text="Вмістити повністю"', source)
        self.assertIn('text="100%"', source)
        self.assertIn('canvas.bind("<Configure>",schedule_render)', source)

    def test_preview_can_expand_without_closing_recognition_results(self):
        source = inspect.getsource(tachograph.TachographModule.toggle_preview_space)
        self.assertIn('text="Показати результати"', source)
        self.assertIn('self.detail_paned.sashpos(0,desired)', source)

    def test_large_tachograph_scan_fits_preview_without_enlarging(self):
        width,height,scale=tachograph.preview_dimensions(4000,3000,820,520,fit=True)
        self.assertEqual((width,height),(667,500))
        self.assertAlmostEqual(scale,1/6)
        self.assertEqual(tachograph.preview_dimensions(640,480,1200,900,fit=True),(640,480,1.0))
        self.assertEqual(tachograph.preview_dimensions(4000,3000,820,520,fit=False),(4000,3000,1.0))

    def test_v8_65_time_schema_is_preserved(self):
        main.init_db()
        con = main.db()
        try:
            columns = {row[1] for row in con.execute("PRAGMA table_info(work_segments)")}
        finally:
            con.close()
        self.assertTrue({"start_time", "end_time", "work_start_time", "work_end_time"} <= columns)

    def test_tachograph_database_remains_separate(self):
        tachograph.init_tacho_db()
        self.assertNotEqual(main.DB_PATH, tachograph.TACHO_DB)
        self.assertEqual(tachograph.TACHO_DB.name, "tachograph_test.sqlite3")

    def test_macos_opens_files_with_native_open_command(self):
        with mock.patch.object(main.os, "name", "posix"), \
             mock.patch.object(main.sys, "platform", "darwin"), \
             mock.patch.object(main.subprocess, "Popen") as popen:
            main.open_external(Path("/tmp/Табель.pdf"))
        popen.assert_called_once_with(["open", "/tmp/Табель.pdf"])

    def test_macos_pdf_font_candidates_include_system_locations(self):
        with mock.patch.object(main.sys, "platform", "darwin"):
            candidates = main.report_font_candidates()
        self.assertIn("/System/Library/Fonts/Supplemental/Arial.ttf", candidates)

    def test_macos_packaging_defines_two_native_architectures(self):
        root = Path(__file__).resolve().parents[1]
        spec = (root / "Taxo_macos.spec").read_text(encoding="utf-8")
        workflow = (root / ".github/workflows/build-macos-v8.66.yml").read_text(encoding="utf-8")
        self.assertIn("app = BUNDLE(", spec)
        self.assertIn("bundle_identifier='com.romanzavadam.taxo'", spec)
        self.assertIn("runner: macos-15\n            arch: arm64", workflow)
        self.assertIn("runner: macos-15-intel\n            arch: x86_64", workflow)

    def test_windows_r5_candidate_build_is_available_for_preview_check(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/build-windows-v8.66.yml").read_text(encoding="utf-8")
        self.assertIn("Taxo_v8_66_TEST_r5_Windows_x64_Portable.zip", workflow)
        self.assertIn("python -m unittest discover -s tests -v", workflow)
        self.assertIn("Database unexpectedly bundled", workflow)

    def test_portable_archives_have_unique_versioned_top_level_folders(self):
        root = Path(__file__).resolve().parents[1]
        windows = (root / ".github/workflows/build-windows-v8.66.yml").read_text(encoding="utf-8")
        macos = (root / ".github/workflows/build-macos-v8.66.yml").read_text(encoding="utf-8")
        installer = (root / "installer/Taxo.iss").read_text(encoding="utf-8")
        self.assertIn("dist/Taxo_v8_66_TEST_r5_Windows_x64", windows)
        self.assertIn("Compress-Archive -Path $bundle", windows)
        self.assertIn('bundle_dir="Taxo_v8_66_TEST_r5_macOS_${{ matrix.arch }}"', macos)
        self.assertIn('keepParent "${bundle_dir}"', macos)
        self.assertIn("dist\\Taxo_v8_66_TEST_r5_Windows_x64\\*", installer)


if __name__ == "__main__":
    unittest.main()
