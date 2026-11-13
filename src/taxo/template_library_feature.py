# -*- coding: utf-8 -*-
"""Attach the template library browser via the normal Taxo feature registry.

The application shell only delegates a command. Workspace resolution, catalog
reading and the Tk window all live in separately documented feature modules.
There is no business logic in main.py and no mutable document operations.
"""
from __future__ import annotations

import tkinter as tk

from template_library_ui import open_template_library


def install(_core, base_app, services):
    """Return an App extension with a single read-only menu entry.

    The context comes from ApplicationServices and tracks the *selected*
    workspace. No absolute user path is stored in application code.
    """
    class TaxoTemplateLibraryApp(base_app):
        def build_menu(self):
            super().build_menu()
            template_menu = tk.Menu(self._app_menu, tearoff=0)
            template_menu.add_command(
                label="Бібліотека шаблонів…",
                command=self.show_template_library,
            )
            self._app_menu.add_cascade(label="Шаблони", menu=template_menu)

        def show_template_library(self):
            """Open a child window; never replace or close the main Taxo app."""
            return open_template_library(self, services)

    return TaxoTemplateLibraryApp
