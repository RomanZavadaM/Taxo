# -*- coding: utf-8 -*-
"""10.15-r1 — selected assignment pairs survive UI selection loss and reach documents."""
import atexit
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_DIRECT_SANDBOX = None
if not os.environ.get("TAXO_WORKSPACE_ROOT"):
    _DIRECT_SANDBOX = tempfile.mkdtemp(prefix="taxo_r15_stage_")
    os.environ["TAXO_WORKSPACE_ROOT"] = os.path.join(_DIRECT_SANDBOX, "workspace")
    os.environ["TAXO_CONFIG_DIR"] = os.path.join(_DIRECT_SANDBOX, "config")
    os.makedirs(os.environ["TAXO_CONFIG_DIR"], exist_ok=True)
    atexit.register(shutil.rmtree, _DIRECT_SANDBOX, True)

import main

ROOT = Path(__file__).resolve().parents[1]


class AssignmentStagingR1Tests(unittest.TestCase):
    def test_r1_identity(self):
        self.assertIn(main.APP_VERSION, ("10.15-r1", "10.15-r2", "10.15-r3", "10.15-r4", "10.15-r5", "10.15-r7", "10.15-r8", "10.15-r9", "10.15-r10", "10.16-r1"))
        self.assertIn(main.APP_VERSION, (ROOT / "VERSION.txt").read_text("utf-8"))
        self.assertIn("Taxo " + main.APP_VERSION, (ROOT / "START.bat").read_text("utf-8"))

    def test_owner_scenario_pairs_survive_selection_loss_and_reach_docx_pdf(self):
        with tempfile.TemporaryDirectory(prefix="taxo_r15_owner_") as td:
            workspace = Path(td) / "workspace"
            config = Path(td) / "config"
            config.mkdir(parents=True, exist_ok=True)
            env = os.environ.copy()
            env["TAXO_WORKSPACE_ROOT"] = str(workspace)
            env["TAXO_CONFIG_DIR"] = str(config)
            src = str(ROOT / "src" / "taxo")
            env["PYTHONPATH"] = src + os.pathsep + str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
            child = ROOT / "tests" / "_r15_owner_child.py"
            code = child.read_text("utf-8")
            completed = subprocess.run(
                [sys.executable, "-c", code], cwd=str(ROOT), env=env,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, timeout=60,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout)
            self.assertIn("ASSIGNMENT_STAGE_OWNER_SCENARIO_OK", completed.stdout)


if __name__ == "__main__":
    unittest.main()
