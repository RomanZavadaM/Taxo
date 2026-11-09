# -*- coding: utf-8 -*-
"""10.14-r10 — cold-start regression after the real Windows r9 crash."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest

import main


class ColdStartupR10Tests(unittest.TestCase):
    def test_r10_identity(self):
        self.assertEqual(main.APP_VERSION, "10.14-r10")

    def test_shlyakh_actions_use_a_dedicated_vehicle_registry_toolbar(self):
        source = Path("src/taxo/v1048_features.py").read_text(encoding="utf-8")
        self.assertIn("def _ensure_vehicle_registry_toolbar", source)
        self.assertIn('text="Реєстри та облік ТЗ"', source)
        self.assertIn("app.vehicle_registry_toolbar = frame", source)
        self.assertNotIn(
            'anchor = _find_button(getattr(self, "tab_vehicles", None), "Контроль документів")',
            source,
        )

    def test_full_layered_application_cold_starts_in_isolated_process(self):
        """Exercise the real App without mutating the parent regression process.

        Importing taxo_app applies every historical feature installer to the
        main module.  Running that in the same interpreter would intentionally
        mutate core.APP_VERSION and installer flags used by later historical
        tests.  A child process matches a real START launch and keeps those
        side effects isolated.
        """
        with tempfile.TemporaryDirectory(prefix="taxo_r10_cold_start_") as td:
            root = Path(td)
            workspace = root / "workspace"
            config = root / "config"
            workspace.mkdir(parents=True, exist_ok=True)
            config.mkdir(parents=True, exist_ok=True)

            script = textwrap.dedent(
                r"""
                import os
                os.environ["TAXO_WORKSPACE_ROOT"] = os.environ["TAXO_R10_WORKSPACE"]
                os.environ["TAXO_CONFIG_DIR"] = os.environ["TAXO_R10_CONFIG"]

                import main
                main.init_db()

                import taxo_app
                app = None
                try:
                    app = taxo_app.App()
                    app.withdraw()
                    app.update_idletasks()
                    app.update()

                    bar = getattr(app, "vehicle_registry_toolbar", None)
                    if bar is None or not bar.winfo_exists():
                        raise RuntimeError("vehicle_registry_toolbar missing")

                    shlyakh = getattr(app, "_shlyakh_button", None)
                    if shlyakh is None or shlyakh.master is not bar:
                        raise RuntimeError("Shlyakh button is not isolated in registry toolbar")

                    labels = []
                    for child in bar.winfo_children():
                        try:
                            labels.append(str(child.cget("text")))
                        except Exception:
                            pass
                    if not any(label.startswith("Реєстр «Шлях»") for label in labels):
                        raise RuntimeError("Shlyakh registry action missing: %r" % (labels,))
                    if "Дані «Шлях»" not in labels:
                        raise RuntimeError("Shlyakh data action missing: %r" % (labels,))

                    print("TAXO_R10_COLD_START_OK")
                finally:
                    if app is not None:
                        try:
                            app.destroy()
                        except Exception:
                            pass
                """
            )

            env = os.environ.copy()
            env["TAXO_R10_WORKSPACE"] = str(workspace)
            env["TAXO_R10_CONFIG"] = str(config)
            env["TAXO_WORKSPACE_ROOT"] = str(workspace)
            env["TAXO_CONFIG_DIR"] = str(config)

            result = subprocess.run(
                [sys.executable, "-c", script],
                cwd=str(Path.cwd()),
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=120,
            )
            self.assertEqual(
                result.returncode,
                0,
                "Cold-start child process failed:\n%s" % result.stdout,
            )
            self.assertIn("TAXO_R10_COLD_START_OK", result.stdout)

    def test_old_test_no_longer_requires_the_known_geometry_bug(self):
        source = Path("tests/test_v10_8_r1.py").read_text(encoding="utf-8")
        self.assertNotIn("test_known_legacy_geometry_conflict_remains_covered", source)
        self.assertIn("test_legacy_geometry_conflict_is_removed_not_preserved", source)


if __name__ == "__main__":
    unittest.main()
