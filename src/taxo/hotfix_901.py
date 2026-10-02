# -*- coding: utf-8 -*-
"""Taxo 9.0.1 operational hotfix.

Keeps the stable 9.0 functionality intact while correcting stale v8.70 r9
labels that remained in the inherited main window and About dialog.
"""

APP_VERSION = "9.0.1"
WINDOW_TITLE = f"Taxo {APP_VERSION} — Працівники, графіки та шляхівки"
ABOUT_TITLE = f"Taxo {APP_VERSION}"
ABOUT_TEXT = (
    "Облік роботи водіїв, табелів, шляхових листів, бланків підтвердження "
    "діяльності та аналогових тахокарт.\n\n"
    "Taxo 9.0.1 — стабільне експлуатаційне виправлення гілки 9.0.\n"
    "Робоча база, резервні копії, документи, журнали та скани зберігаються "
    "у вибраному робочому сховищі окремо від програми."
)


def _replace_about_command(core, app):
    """Replace the legacy v8.70 About command created by the base UI."""
    try:
        menu_name = app.cget("menu")
        if not menu_name:
            return False
        menubar = app.nametowidget(menu_name)
        end = menubar.index("end")
        if end is None:
            return False
        for index in range(end + 1):
            if menubar.type(index) != "cascade":
                continue
            if menubar.entrycget(index, "label") != "Довідка":
                continue
            submenu = app.nametowidget(menubar.entrycget(index, "menu"))
            sub_end = submenu.index("end")
            if sub_end is None:
                return False
            for sub_index in range(sub_end + 1):
                if submenu.type(sub_index) == "command" and submenu.entrycget(sub_index, "label") == "Про програму":
                    submenu.entryconfigure(
                        sub_index,
                        command=lambda: core.messagebox.showinfo(
                            ABOUT_TITLE,
                            ABOUT_TEXT,
                            parent=app,
                        ),
                    )
                    return True
    except core.tk.TclError:
        return False
    return False


def install(core, base_app):
    """Install the 9.0.1 UI-label correction on the current application class."""
    if getattr(core, "_TAXO_901_INSTALLED", False):
        return core.App

    class Taxo901App(base_app):
        def build_menu(self):
            result = super().build_menu()
            _replace_about_command(core, self)
            return result

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title(WINDOW_TITLE)

    Taxo901App.__name__ = "App"
    Taxo901App.__qualname__ = "App"
    core.App = Taxo901App
    core._TAXO_901_INSTALLED = True
    return Taxo901App
