# -*- coding: utf-8 -*-
"""Isolate the whole regression suite from any real Taxo working storage.

10.10-r2 incident: ``main.py`` resolves the working storage on import from
``TAXO_WORKSPACE_ROOT`` or the pointer in the user's config directory
(``%APPDATA%\\Taxo\\workspace.json``). Several historical tests import
``main`` without isolating it, so a regression run on a workstation wrote test
drivers/employees into the real working database.

``unittest`` discovery imports test modules in sorted order, so this module
(``test_00_*``) is imported before every ``test_v*`` module. It points the
workspace pointer and the config directory at a throw-away directory before
anything imports ``main``. The application itself is not changed.

Regression must still run in CI only; never against a machine with real data.
"""
import atexit
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

_SANDBOX = Path(tempfile.mkdtemp(prefix="taxo_test_isolation_"))
_WORKSPACE = _SANDBOX / "workspace"
_CONFIG = _SANDBOX / "config"
_CONFIG.mkdir(parents=True, exist_ok=True)

# Explicit values win over anything inherited from the environment.
os.environ["TAXO_WORKSPACE_ROOT"] = str(_WORKSPACE)
os.environ["TAXO_CONFIG_DIR"] = str(_CONFIG)

atexit.register(shutil.rmtree, _SANDBOX, True)

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "taxo"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _inside(path, root):
    try:
        Path(os.path.abspath(str(path))).relative_to(Path(os.path.abspath(str(root))))
        return True
    except ValueError:
        return False


class TestSuiteIsolation(unittest.TestCase):
    def test_isolation_module_is_discovered_first(self):
        names = sorted(p.name for p in (ROOT / "tests").glob("test*.py"))
        self.assertEqual(names[0], Path(__file__).name)

    def test_workspace_pointer_and_config_are_sandboxed(self):
        import workspace

        self.assertTrue(_inside(workspace.config_dir(), _SANDBOX))
        self.assertTrue(_inside(workspace.load_workspace_root(), _SANDBOX))

    def test_main_database_points_into_sandbox(self):
        import main

        if _inside(main.DATA_ROOT, _SANDBOX):
            self.assertTrue(_inside(main.DB_PATH, _SANDBOX))
        else:
            # ``main`` was imported before this module (e.g. a single test file
            # run directly). It must at least never be the default real storage.
            import workspace

            self.assertNotEqual(
                Path(os.path.abspath(str(main.DATA_ROOT))),
                Path(os.path.abspath(str(workspace.default_workspace_root()))),
            )


if __name__ == "__main__":
    unittest.main()
