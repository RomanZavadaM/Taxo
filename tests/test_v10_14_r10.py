# -*- coding: utf-8 -*-
"""10.14-r10 — cold-start regression after the real Windows r9 crash."""
import atexit
import os
import shutil
import tempfile
import unittest
from unittest import mock

# Direct execution of this test must never touch a user's real Taxo workspace.
_DIRECT_SANDBOX = None
if not os.environ.get("TAXO_WORKSPACE_ROOT"):
    _DIRECT_SANDBOX = tempfile.mkdtemp(prefix="taxo_r10_startup_")
    os.environ["TAXO_WORKSPACE_ROOT"] = os.path.join(_DIRECT_SANDBOX, "workspace")
    os.environ["TAXO_CONFIG_DIR"] = os.path.join(_DIRECT_SANDBOX, "config")
    os.makedirs(os.environ["TAXO_CONFIG_DIR"], exist_ok=True)
    atexit.register(shutil.rmtree, _DIRECT_SANDBOX, True)

import main
import taxo_app
import v1048_features


class ColdStartupR10Tests(unittest.TestCase):
    def test_r10_identity(self):
        self.assertEqual(main.APP_VERSION, "10.14-r10")

    def test_shlyakh_actions_use_a_dedicated_vehicle_registry_toolbar(self):
        source = open("src/taxo/v1048_features.py", encoding="utf-8").read()
        self.assertIn("def _ensure_vehicle_registry_toolbar", source)
        self.assertIn('text="Реєстри та облік ТЗ"', source)
        self.assertIn("app.vehicle_registry_toolbar = frame", source)
        self.assertNotIn(
            'anchor = _find_button(getattr(self, "tab_vehicles", None), "Контроль документів")',
            source,
        )

    def test_full_layered_application_constructs_and_completes_first_tk_update(self):
        # This is intentionally a real App construction.  The r9 Windows crash
        # happened inside App.__init__ before the main window became usable.
        main.init_db()
        app = None
        with mock.patch.object(main.messagebox, "showinfo", return_value=None),              mock.patch.object(main.messagebox, "showwarning", return_value=None),              mock.patch.object(main.messagebox, "showerror", return_value=None),              mock.patch.object(main.messagebox, "askyesno", return_value=False):
            try:
                app = taxo_app.App()
                app.withdraw()
                app.update_idletasks()
                app.update()

                self.assertTrue(app.winfo_exists())
                registry_bar = getattr(app, "vehicle_registry_toolbar", None)
                self.assertIsNotNone(registry_bar)
                self.assertTrue(registry_bar.winfo_exists())

                shlyakh = getattr(app, "_shlyakh_button", None)
                self.assertIsNotNone(shlyakh)
                self.assertIs(shlyakh.master, registry_bar)

                labels = []
                for child in registry_bar.winfo_children():
                    try:
                        labels.append(str(child.cget("text")))
                    except Exception:
                        pass
                self.assertTrue(
                    any(label.startswith("Реєстр «Шлях»") for label in labels),
                    labels,
                )
                self.assertIn("Дані «Шлях»", labels)

                # The dedicated registry toolbar itself is packed into the
                # vehicle tab, while its children may safely use pack without
                # sharing a parent with the grid-reflowed legacy core toolbar.
                self.assertEqual(registry_bar.winfo_manager(), "pack")
            finally:
                if app is not None:
                    try:
                        app.destroy()
                    except Exception:
                        pass

    def test_old_test_no_longer_requires_the_known_geometry_bug(self):
        source = open("tests/test_v10_8_r1.py", encoding="utf-8").read()
        self.assertNotIn("test_known_legacy_geometry_conflict_remains_covered", source)
        self.assertIn("test_legacy_geometry_conflict_is_removed_not_preserved", source)


if __name__ == "__main__":
    unittest.main()
