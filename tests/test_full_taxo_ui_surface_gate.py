# -*- coding: utf-8 -*-
"""Cross-module UI surface regression gate for Taxo.

Detect accidental removal of literal Tk buttons, menu entries, tabs and table
headings compared to the Git base. Covers all current and future modules,
without a manually maintained list of every new action.

This is a tripwire, not a substitute for live widget reachability or
end-to-end workflow tests. Dynamically generated labels require dedicated
function_registry routes and runtime smoke checks.
"""
from collections import Counter
from pathlib import Path
import ast
import subprocess
import unittest


PROJECT = Path(__file__).resolve().parents[1]
UI_METHODS = {
    "Button", "Checkbutton", "Radiobutton", "Menubutton",
    "add_command", "add_cascade", "add_checkbutton", "add_radiobutton",
    "heading",
}
UI_PARENT_PATHS = ("src/taxo/", "main.py", "taxo_app.py")


def _method_name(call):
    func = call.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return ""


def _literal_text(call):
    for keyword in call.keywords:
        if keyword.arg not in ("text", "label"):
            continue
        if isinstance(keyword.value, ast.Constant) and isinstance(
            keyword.value.value, str
        ):
            return keyword.value.value.strip()
    return ""


def visible_static_actions(source):
    """Collect only literal text attached directly to real UI-building calls."""
    try:
        tree = ast.parse(source)
    except (SyntaxError, TypeError):
        raise
    result = Counter()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _method_name(node)
        if name not in UI_METHODS:
            continue
        label = _literal_text(node)
        if label:
            result[(name, label)] += 1
    return result


def removed_actions(before, after):
    """Report disappearance, even if another unrelated action still exists."""
    return before - after


def _git(*args):
    return subprocess.check_output(
        ["git", *args], cwd=str(PROJECT), stderr=subprocess.DEVNULL
    ).decode("utf-8").strip()


def _base_commit():
    try:
        head = _git("rev-parse", "HEAD")
    except (OSError, subprocess.CalledProcessError):
        return None
    try:
        base = _git("merge-base", "HEAD", "refs/remotes/origin/main")
        if base and base != head:
            return base
    except subprocess.CalledProcessError:
        pass
    try:
        return _git("rev-parse", "HEAD^")
    except subprocess.CalledProcessError:
        return None


def _source_at(revision, filename):
    try:
        return _git("show", "%s:%s" % (revision, filename))
    except subprocess.CalledProcessError:
        return None


def _is_ui_module(path):
    return path.endswith(".py") and (
        path.startswith("src/taxo/")
        or path in ("main.py", "taxo_app.py")
    )


class FullTaxoButtonSurfaceGateTests(unittest.TestCase):
    def test_source_changes_preserve_previous_visible_actions(self):
        base = _base_commit()
        if not base:
            self.skipTest("Git history is unavailable in this package")
        paths = _git("diff", "--no-renames", "--name-only", base, "HEAD")
        missing = []
        for filename in sorted(set(paths.splitlines())):
            if not _is_ui_module(filename):
                continue
            old = _source_at(base, filename)
            if old is None:  # Newly added source has no prior UI to preserve.
                continue
            new_path = PROJECT / filename
            new = new_path.read_text(encoding="utf-8") if new_path.is_file() else ""
            for (kind, label), count in removed_actions(
                visible_static_actions(old),
                visible_static_actions(new) if new else Counter(),
            ).items():
                missing.append("%s: %s %r x%d" % (filename, kind, label, count))
        self.assertEqual(
            missing, [],
            "User-visible actions disappeared since Git base. Restore them, "
            "or document an explicitly approved replacement route and "
            "update this safeguard intentionally:\n" + "\n".join(missing),
        )

    def test_negative_mutation_catches_removed_button_and_menu(self):
        before = visible_static_actions(
            'ttk.Button(parent, text="Зберегти", command=save)\n'
            'menu.add_command(label="Експорт", command=export)\n'
        )
        after = visible_static_actions(
            'ttk.Button(parent, text="Зберегти", command=save)\n'
        )
        self.assertEqual(
            removed_actions(before, after),
            Counter({("add_command", "Експорт"): 1}),
        )

    def test_negative_mutation_catches_button_that_is_renamed(self):
        before = visible_static_actions(
            'ttk.Button(parent, text="Керувати парами", command=edit)'
        )
        after = visible_static_actions(
            'ttk.Button(parent, text="Невідомо", command=edit)'
        )
        self.assertEqual(
            removed_actions(before, after),
            Counter({("Button", "Керувати парами"): 1}),
        )


if __name__ == "__main__":
    unittest.main()
