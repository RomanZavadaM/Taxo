# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

import main
from release_naming import start_archive_stem, version_from_file


ROOT=Path(__file__).resolve().parents[1]


class TestTaxo103R8MacSidebar(unittest.TestCase):
    def test_candidate_identity_is_r8(self):
        self.assertEqual(main.APP_VERSION,"10.3-r8")
        self.assertEqual(main.APP_VERSION,version_from_file(ROOT/"VERSION.txt"))
        self.assertEqual(
            start_archive_stem("10.3-r8"),
            "Taxo_v10_3_candidate_r8_START",
        )

    def test_macos_navigation_avoids_native_aqua_button_surface(self):
        source=(ROOT/"main.py").read_text("utf-8")
        start=source.index("        def add_nav(label,kind,tab=None,command=None):")
        end=source.index('        add_nav("Працівники"',start)
        section=source[start:end]

        self.assertIn('if sys.platform=="darwin":',section)
        self.assertIn("btn=tk.Label(",section)
        self.assertIn('bg=PALETTE["sidebar"],fg="#FFFFFF"',section)
        self.assertIn('cursor="pointinghand"',section)
        self.assertIn('btn.bind("<Button-1>",invoke_nav',section)
        self.assertIn('btn.bind("<Return>",invoke_nav',section)
        self.assertIn('btn.bind("<space>",invoke_nav',section)

    def test_macos_navigation_has_explicit_hover_and_focus_states(self):
        source=(ROOT/"main.py").read_text("utf-8")
        start=source.index("        def add_nav(label,kind,tab=None,command=None):")
        end=source.index('        add_nav("Працівники"',start)
        section=source[start:end]

        self.assertIn('widget.configure(bg=PALETTE["blue_dark"],fg="#FFFFFF")',section)
        self.assertIn('btn.bind("<Enter>",highlight_nav',section)
        self.assertIn('btn.bind("<FocusIn>",highlight_nav',section)
        self.assertIn('btn.bind("<Leave>",restore_nav',section)
        self.assertIn('btn.bind("<FocusOut>",restore_nav',section)

    def test_selected_state_is_high_contrast_on_macos(self):
        source=(ROOT/"main.py").read_text("utf-8")
        start=source.index("    def _refresh_nav_selection(self):")
        end=source.index("    def show_tab(self, tab):",start)
        section=source[start:end]

        self.assertIn('if sys.platform=="darwin":',section)
        self.assertIn('bg=PALETTE["navy"] if active else PALETTE["sidebar"]',section)
        self.assertIn('fg="#FFFFFF"',section)

    def test_windows_linux_keep_existing_button_navigation(self):
        source=(ROOT/"main.py").read_text("utf-8")
        start=source.index("        def add_nav(label,kind,tab=None,command=None):")
        end=source.index('        add_nav("Працівники"',start)
        section=source[start:end]

        self.assertIn("else:\n                btn=tk.Button(",section)
        self.assertIn('activebackground=PALETTE["blue_dark"]',section)


if __name__=="__main__":
    unittest.main()
