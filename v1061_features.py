# -*- coding: utf-8 -*-
"""Taxo 10.6-r1 — фільтр неактивних ТЗ у реєстрі документів.

Неактивні автомобілі не видаляються і не змінюються. За замовчуванням вони
лише приховані у робочому списку «Транспортні засоби — реєстр документів».
Користувач може зняти прапорець і одразу побачити весь історичний парк.
"""
from __future__ import annotations

APP_VERSION = "10.6-r1"


def vehicle_row_visible(active_value, hide_inactive=True):
    """Return whether a vehicle row should be visible under the UI filter."""
    if not hide_inactive:
        return True
    if isinstance(active_value, str):
        normalized = active_value.strip().casefold()
        if normalized in {"ні", "no", "false", "0", "неактивний", "inactive"}:
            return False
        if normalized in {"так", "yes", "true", "1", "активний", "active"}:
            return True
    return bool(active_value)


def install(core, base_app):
    if getattr(core, "_TAXO_1061_INSTALLED", False):
        return core.App

    core.APP_VERSION = APP_VERSION

    class Taxo1061App(base_app):
        def build_vehicles(self):
            # Set before super(): base build_vehicles() calls self.load_vehicles(),
            # so the very first render already applies the requested default.
            self.vehicle_hide_inactive = core.tk.BooleanVar(value=True)
            result = super().build_vehicles()

            toolbar = None
            for child in self.tab_vehicles.winfo_children():
                try:
                    if child.winfo_class() != "TFrame":
                        continue
                    button_labels = []
                    for widget in child.winfo_children():
                        try:
                            if widget.winfo_class() not in {"TButton", "Button"}:
                                continue
                            text = str(widget.cget("text") or "")
                        except core.tk.TclError:
                            continue
                        if text:
                            button_labels.append(text)
                    # The add-vehicle caption changed historically, so identify
                    # the existing action bar by its stable Refresh action and
                    # number of vehicle actions instead of one old caption.
                    if "Оновити" in button_labels and len(button_labels) >= 4:
                        toolbar = child
                        break
                except core.tk.TclError:
                    continue

            if toolbar is None:
                # Defensive fallback: keep the filter visible even if a later UI
                # skin changes the action bar layout again.
                toolbar = core.ttk.Frame(self.tab_vehicles)
                tree = getattr(self, "vehicle_tree", None)
                kwargs = {"fill": "x", "padx": 10, "pady": (0, 6)}
                if tree is not None:
                    kwargs["before"] = tree
                toolbar.pack(**kwargs)

            core.ttk.Checkbutton(
                toolbar,
                text="Сховати неактивні автомобілі",
                variable=self.vehicle_hide_inactive,
                command=self.load_vehicles,
            ).pack(side="right", padx=(12, 4))
            self.vehicle_hide_inactive_control = toolbar
            return result

        def load_vehicles(self):
            result = super().load_vehicles()
            tree = getattr(self, "vehicle_tree", None)
            flag = getattr(self, "vehicle_hide_inactive", None)
            if tree is None or flag is None or not bool(flag.get()):
                return result

            for item in list(tree.get_children()):
                try:
                    active_value = tree.set(item, "active")
                except core.tk.TclError:
                    continue
                if not vehicle_row_visible(active_value, hide_inactive=True):
                    tree.delete(item)
            return result

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

    Taxo1061App.__name__ = "App"
    Taxo1061App.__qualname__ = "App"
    core._TAXO_1061_INSTALLED = True
    core.App = Taxo1061App
    return Taxo1061App
