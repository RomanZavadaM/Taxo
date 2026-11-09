# -*- coding: utf-8 -*-
"""10.14-r10 — cold-start regression after the real Windows r9 crash."""
import atexit
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Direct execution of this test must never touch a user's real Taxo workspace.
_DIRECT_SANDBOX = None
if not os.environ.get("TAXO_WORKSPACE_ROOT"):
    _DIRECT_SANDBOX = tempfile.mkdtemp(prefix="taxo_r10_startup_")
    os.environ["TAXO_WORKSPACE_ROOT"] = os.path.join(_DIRECT_SANDBOX, "workspace")
    os.environ["TAXO_CONFIG_DIR"] = os.path.join(_DIRECT_SANDBOX, "config")
    os.makedirs(os.environ["TAXO_CONFIG_DIR"], exist_ok=True)
    atexit.register(shutil.rmtree, _DIRECT_SANDBOX, True)

import main
import v1048_features

ROOT = Path(__file__).resolve().parents[1]


class ColdStartupR10Tests(unittest.TestCase):
    def test_r10_identity(self):
        self.assertEqual(main.APP_VERSION, "10.14-r10")

    def test_shlyakh_actions_use_a_dedicated_vehicle_registry_toolbar(self):
        source = (ROOT / "src" / "taxo" / "v1048_features.py").read_text(encoding="utf-8")
        self.assertIn("def _ensure_vehicle_registry_toolbar", source)
        self.assertIn('text="Реєстри та облік ТЗ"', source)
        self.assertIn("app.vehicle_registry_toolbar = frame", source)
        self.assertNotIn(
            'anchor = _find_button(getattr(self, "tab_vehicles", None), "Контроль документів")',
            source,
        )

    def test_full_layered_application_constructs_and_completes_first_tk_update(self):
        # Run the real startup in a child process. Importing taxo_app applies
        # all historical feature layers and mutates main.App; keeping that in
        # this subprocess prevents a failed startup from contaminating the
        # remaining regression suite.
        with tempfile.TemporaryDirectory(prefix="taxo_r10_child_") as td:
            workspace = Path(td) / "workspace"
            config = Path(td) / "config"
            config.mkdir(parents=True, exist_ok=True)
            env = os.environ.copy()
            env["TAXO_WORKSPACE_ROOT"] = str(workspace)
            env["TAXO_CONFIG_DIR"] = str(config)
            src = str(ROOT / "src" / "taxo")
            env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
            code = r"""
import main
main.init_db()
import taxo_app
app = None
try:
    app = taxo_app.App()
    app.withdraw()
    app.update_idletasks()
    app.update()
    assert app.winfo_exists()
    registry_bar = getattr(app, "vehicle_registry_toolbar", None)
    assert registry_bar is not None and registry_bar.winfo_exists()
    shlyakh = getattr(app, "_shlyakh_button", None)
    assert shlyakh is not None and shlyakh.master is registry_bar
    labels = []
    for child in registry_bar.winfo_children():
        try:
            labels.append(str(child.cget("text")))
        except Exception:
            pass
    assert any(label.startswith("Реєстр «Шлях»") for label in labels), labels
    assert "Дані «Шлях»" in labels, labels
    assert registry_bar.winfo_manager() == "pack"
    print("TAXO_COLD_START_OK")
finally:
    if app is not None:
        app.destroy()
"""
            completed = subprocess.run(
                [sys.executable, "-c", code],
                cwd=str(ROOT),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=90,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout)
            self.assertIn("TAXO_COLD_START_OK", completed.stdout)

    def test_old_test_no_longer_requires_the_known_geometry_bug(self):
        source = (ROOT / "tests" / "test_v10_8_r1.py").read_text(encoding="utf-8")
        self.assertNotIn("test_known_legacy_geometry_conflict_remains_covered", source)
        self.assertIn("test_legacy_geometry_conflict_is_removed_not_preserved", source)


if __name__ == "__main__":
    unittest.main()
