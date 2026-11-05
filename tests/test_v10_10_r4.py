# -*- coding: utf-8 -*-
"""Taxo 10.10-r4 — canonical version in all current and future UI windows."""
import sys
import re
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "taxo"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from release_naming import version_from_file  # noqa: E402
from version_identity import _canonicalize_text, pin_application_version  # noqa: E402


class FakeWidget:
    def __init__(self, title="", text=None, children=None):
        self._title = title
        self._text = text
        self._children = list(children or [])
        self._bindings = []

    def title(self, value=None):
        if value is None:
            return self._title
        self._title = value

    def cget(self, key):
        if key != "text" or self._text is None:
            raise RuntimeError("no text")
        return self._text

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._text = kwargs["text"]

    def winfo_children(self):
        return list(self._children)

    def bind_all(self, sequence, callback, add=None):
        self._bindings.append((sequence, callback, add))


class TestVersionUiR4(unittest.TestCase):
    def test_branding_replacement_does_not_rewrite_historical_prose(self):
        self.assertEqual(_canonicalize_text("Taxo 10.8-r5 — Працівники", "10.10-r4"),
                         "Taxo 10.10-r4 — Працівники")
        self.assertEqual(_canonicalize_text("v10.8-r5", "10.10-r4"), "v10.10-r4")
        self.assertEqual(_canonicalize_text("Версія: 10.9-r9", "10.10-r4"),
                         "Версія: 10.10-r4")
        self.assertEqual(_canonicalize_text("Історія змін 10.8-r5", "10.10-r4"),
                         "Історія змін 10.8-r5")

    def test_existing_widget_tree_uses_canonical_version(self):
        core = types.SimpleNamespace(APP_VERSION="10.10-r4")
        child = FakeWidget(text="v10.8-r5")

        class App(FakeWidget):
            def __init__(self):
                super().__init__(
                    title="Taxo 10.8-r5 — Працівники, графіки та шляхівки",
                    children=[child],
                )
                core.APP_VERSION = "10.8-r5"

        pin_application_version(core, App, "10.10-r4")
        app = App()
        self.assertEqual(core.APP_VERSION, "10.10-r4")
        self.assertEqual(app.title(), "Taxo 10.10-r4 — Працівники, графіки та шляхівки")
        self.assertEqual(child._text, "v10.10-r4")

    def test_later_mapped_dialog_is_normalized(self):
        core = types.SimpleNamespace(APP_VERSION="10.10-r4")

        class App(FakeWidget):
            pass

        pin_application_version(core, App, "10.10-r4")
        app = App(title="Taxo 10.8-r5 — main")
        self.assertEqual(len(app._bindings), 1)

        late_label = FakeWidget(text="Version: 10.9-r9")
        late = FakeWidget(title="Taxo 10.8-r5 — Довідка", children=[late_label])
        event = types.SimpleNamespace(widget=late)
        app._bindings[0][1](event)

        self.assertEqual(late.title(), "Taxo 10.10-r4 — Довідка")
        self.assertEqual(late_label._text, "Version: 10.10-r4")
        self.assertEqual(core.APP_VERSION, "10.10-r4")

    def test_repository_version_identity_is_r4_or_later(self):
        version = version_from_file(ROOT / "VERSION.txt")
        match = re.fullmatch(r"10\.10-r(\d+)", version)
        self.assertIsNotNone(match, version)
        self.assertGreaterEqual(int(match.group(1)), 4)
        self.assertIn(f'APP_VERSION = "{version}"', (ROOT / "main.py").read_text("utf-8"))


if __name__ == "__main__":
    unittest.main()
