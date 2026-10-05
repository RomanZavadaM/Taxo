# -*- coding: utf-8 -*-
"""Taxo 10.10-r3 — one runtime version (A1) and DB-only backup warning (A5).

Audit A1: historical feature layers overwrote ``core.APP_VERSION`` with their
own issued revision, so the running window, About dialog, PDF headers and the
backup manifest showed "10.8-r5". The entry point now pins the canonical
``main.APP_VERSION`` after composing the layers.
"""
import ast
import re
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "taxo"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from release_naming import version_from_file  # noqa: E402
from version_identity import pin_application_version  # noqa: E402


def _historical_chain(core):
    """Mimic issued layers: each overwrites core.APP_VERSION and the title."""

    class Base:
        def __init__(self):
            self.seen_by_base = core.APP_VERSION
            self._title = f"Taxo {core.APP_VERSION} — Driver Worktime"

        def title(self, value=None):
            if value is None:
                return self._title
            self._title = value
            return None

    class Layer1085(Base):
        def __init__(self):
            super().__init__()
            core.APP_VERSION = "10.8-r5"
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

    class Layer1099(Layer1085):
        pass

    core.APP_VERSION = "10.9-r9"  # install-time overwrite by the last layer
    return Layer1099


class TestPinApplicationVersion(unittest.TestCase):
    def test_runtime_version_title_and_base_ui_use_canonical_version(self):
        core = types.SimpleNamespace(APP_VERSION="10.10-r3")
        canonical = core.APP_VERSION
        app_cls = _historical_chain(core)
        self.assertEqual(core.APP_VERSION, "10.9-r9")

        returned = pin_application_version(core, app_cls, canonical)
        self.assertIs(returned, app_cls)
        self.assertEqual(core.APP_VERSION, canonical)

        app = app_cls()
        self.assertEqual(core.APP_VERSION, canonical)
        self.assertEqual(app.seen_by_base, canonical)
        self.assertEqual(app.title(), f"Taxo {canonical} — Працівники, графіки та шляхівки")

    def test_pinning_is_idempotent(self):
        core = types.SimpleNamespace(APP_VERSION="10.10-r3")
        app_cls = _historical_chain(core)
        pin_application_version(core, app_cls, "10.10-r3")
        first = app_cls.__init__
        pin_application_version(core, app_cls, "10.10-r3")
        self.assertIs(app_cls.__init__, first)

    def test_title_failure_never_blocks_start(self):
        core = types.SimpleNamespace(APP_VERSION="x")

        class Broken:
            def title(self, value=None):
                raise RuntimeError("no window")

        pin_application_version(core, Broken, "10.10-r3")
        Broken()
        self.assertEqual(core.APP_VERSION, "10.10-r3")


class TestEntrypointPinsVersion(unittest.TestCase):
    def test_entrypoint_captures_before_layers_and_pins_after(self):
        source = (ROOT / "taxo_app.py").read_text("utf-8")
        capture = source.index("CANONICAL_APP_VERSION = core.APP_VERSION")
        install = source.index("App = install_feature_layers(core, services=SERVICES)")
        pin = source.index("pin_application_version(core, App, CANONICAL_APP_VERSION)")
        self.assertLess(capture, source.index("from feature_layers import install_feature_layers"))
        self.assertLess(install, pin)
        # still exactly one App assignment (10.8-r7 entry-point contract)
        tree = ast.parse(source)
        assignments = [n for n in tree.body if isinstance(n, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == "App" for t in n.targets)]
        self.assertEqual(len(assignments), 1)

    def test_version_identity_is_packaged(self):
        for spec in sorted((ROOT / "packaging").glob("*.spec")):
            self.assertIn("'version_identity'", spec.read_text("utf-8"), spec.name)

    def test_revision_is_10_10_r3_or_later(self):
        version = version_from_file(ROOT / "VERSION.txt")
        match = re.fullmatch(r"10\.(\d+)(?:-r(\d+))?", version)
        self.assertIsNotNone(match, version)
        revision = int(match.group(2)) if match.group(2) else 999  # stable promotion
        self.assertGreaterEqual((int(match.group(1)), revision), (10, 3))
        self.assertIn(f'APP_VERSION = "{version}"', (ROOT / "main.py").read_text("utf-8"))


class TestDatabaseOnlyBackupWarning(unittest.TestCase):
    def test_success_message_warns_when_no_file_attachments(self):
        source = (ROOT / "main.py").read_text("utf-8")
        self.assertIn("ця копія містить лише бази даних", source)
        self.assertIn('"" if extras else', source)
        # historical wording of the composition line is kept
        self.assertIn('f"Склад: обидві БД; {extra_text}."', source)


if __name__ == "__main__":
    unittest.main()
