# -*- coding: utf-8 -*-
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from tkinter import ttk

import correspondence_feature
import correspondence_ui
import function_registry
import workspace
from correspondence_attachments import add_correspondence_file
from correspondence_registry import (
    DIRECTION_INCOMING,
    DIRECTION_OUTGOING,
)
from correspondence_service import register_incoming, register_outgoing
from runtime_reachability import activate_widget, runtime_routes


def walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from walk(child)


def button_by_text(root, text):
    for widget in walk(root):
        try:
            if widget.winfo_class() in ("TButton", "Button"):
                if str(widget.cget("text")) == text:
                    return widget
        except Exception:
            pass
    return None


class _Messages:
    def __init__(self):
        self.showinfo = mock.Mock()
        self.showerror = mock.Mock()
        self.askyesno = mock.Mock(return_value=True)


def _core(messages=None, *, size=(1180, 760)):
    messages = messages or _Messages()

    def fit(win, _width, _height, _min_width, _min_height):
        win.geometry("%dx%d" % size)

    def configure(win, title="", minsize=None):
        if title:
            win.title(title)
        if minsize:
            win.minsize(*minsize)

    return SimpleNamespace(
        tk=tk,
        ttk=ttk,
        messagebox=messages,
        filedialog=SimpleNamespace(askopenfilename=lambda **_kwargs: ""),
        fit_window_to_screen=fit,
        configure_toplevel=configure,
        calendar_button=lambda parent, _var: ttk.Button(parent, text="Дата…"),
        PALETTE={"sidebar": "#000000", "blue_dark": "#111111"},
        nav_photo=lambda parent, *_args: tk.PhotoImage(
            master=parent, width=1, height=1
        ),
    )


class _BaseNav:
    def __init__(self, root):
        self.root = root
        nav = tk.Frame(root)
        nav.pack(fill="x")
        self._nav_icons = {}
        self._nav_named_buttons = {}
        anchor = tk.Button(nav, text="Експлуатація")
        anchor.pack(fill="x")
        self._nav_named_buttons["Експлуатація"] = anchor

    def winfo_children(self):
        return self.root.winfo_children()


class CorrespondenceUiR3Tests(unittest.TestCase):
    def test_candidate_identity_and_start_guards(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.25-r4\n",
        )
        self.assertIn(
            'APP_VERSION = "10.25-r4"',
            (root / "main.py").read_text("utf-8"),
        )
        start = (root / "START.bat").read_text("utf-8")
        self.assertIn("Taxo 10.25-r4", start)
        self.assertIn("correspondence_ui.py", start)
        self.assertIn("correspondence_feature.py", start)
        self.assertEqual(
            (root / ".release" / "full-current").read_text("utf-8"),
            "10.25-r4\n",
        )

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name) / "work"
        workspace.ensure_workspace(self.workspace)
        self.root = tk.Tk()
        self.root.geometry("1000x700+0+0")
        self.root._company_name_value = lambda: "Тестове АТП"
        self.messages = _Messages()
        self.core = _core(self.messages)

    def tearDown(self):
        try:
            for child in tuple(self.root.winfo_children()):
                if isinstance(child, tk.Toplevel):
                    child.destroy()
            self.root.destroy()
        finally:
            self.temp.cleanup()

    def _show(self, widget=None):
        self.root.deiconify()
        self.root.update_idletasks()
        self.root.update()
        if widget is not None:
            widget.update_idletasks()
            widget.update()

    def test_function_registry_protects_correspondence_route(self):
        route = next(
            row for row in function_registry.FUNCTION_ROUTES
            if row.function_id == "correspondence.center"
        )
        self.assertTrue(route.required)
        self.assertTrue(route.runtime_smoke)
        self.assertEqual(route.action_label, "Кореспонденція")
        self.assertEqual(route.callback, "open_correspondence_center")

    @runtime_routes("correspondence.center")
    def test_sidebar_entry_is_mapped_and_invokes_callback(self):
        calls = []
        core = _core()
        App = correspondence_feature.install(core, _BaseNav)
        App.open_correspondence_center = lambda self: calls.append("opened")
        root = tk.Tk()
        root.geometry("900x600+0+0")
        try:
            app = App(root)
            root.deiconify()
            root.update()
            button = app._nav_named_buttons.get("Кореспонденція")
            self.assertIsNotNone(button)
            activate_widget(button, "correspondence.center", container=root)
            self.assertEqual(calls, ["opened"])
        finally:
            root.destroy()

    @runtime_routes(
        "correspondence.new_incoming",
        "correspondence.new_outgoing",
        "correspondence.reply",
        "correspondence.attachments",
        "correspondence.open_document",
    )
    def test_core_correspondence_actions_are_live_and_activatable(self):
        incoming = register_incoming(
            self.workspace,
            registration_date="2026-11-23",
            correspondent="A",
            subject="Incoming route",
            document_ref="order:test-route",
        )
        register_outgoing(
            self.workspace,
            registration_date="2026-11-23",
            correspondent="B",
            subject="Outgoing route",
        )
        win = correspondence_ui.open_correspondence_center(
            self.root, self.core, self.workspace
        )
        self._show(win)

        def activate_and_close(button, route_id):
            before = {
                child for child in walk(self.root)
                if isinstance(child, tk.Toplevel)
            }
            activate_widget(button, route_id, container=win)
            self._show(win)
            for child in tuple(walk(self.root)):
                if (
                    child not in before
                    and child is not win
                    and isinstance(child, tk.Toplevel)
                    and child.winfo_exists()
                ):
                    child.destroy()
            self._show(win)

        activate_and_close(
            button_by_text(win, "Новий вхідний…"),
            "correspondence.new_incoming",
        )
        activate_and_close(
            button_by_text(win, "Новий вихідний…"),
            "correspondence.new_outgoing",
        )

        tree = win._taxo_correspondence_trees[DIRECTION_INCOMING]
        tree.selection_set(incoming.correspondence_id)
        tree.focus(incoming.correspondence_id)
        self._show(win)
        buttons = win._taxo_correspondence_buttons[DIRECTION_INCOMING]

        activate_and_close(
            buttons["response"], "correspondence.reply"
        )
        activate_and_close(
            buttons["attachments"], "correspondence.attachments"
        )
        activate_widget(
            buttons["open"],
            "correspondence.open_document",
            container=win,
        )
        self._show(win)
        self.messages.showinfo.assert_called()

    def test_center_shows_two_real_journals_card_attachments_and_filters(self):
        incoming = register_incoming(
            self.workspace,
            registration_date="2026-11-21",
            document_date="2026-11-20",
            received_date="2026-11-21",
            correspondent="ТОВ Альфа",
            subject="Запит щодо перевезень",
            external_number="A-15",
            due_date="2026-11-25",
        )
        outgoing = register_outgoing(
            self.workspace,
            registration_date="2026-11-22",
            correspondent="ТОВ Бета",
            subject="Інформаційний лист",
        )
        pdf = Path(self.temp.name) / "scan.pdf"
        pdf.write_bytes(b"%PDF-1.7\ncorrespondence UI test\n%%EOF\n")
        add_correspondence_file(
            self.workspace, incoming.correspondence_id, pdf
        )

        win = correspondence_ui.open_correspondence_center(
            self.root, self.core, self.workspace
        )
        self._show(win)

        book = win._taxo_correspondence_notebook
        self.assertEqual(
            [str(book.tab(tab, "text")) for tab in book.tabs()],
            ["Вхідні", "Вихідні", "Справи"],
        )
        incoming_tree = win._taxo_correspondence_trees[DIRECTION_INCOMING]
        outgoing_tree = win._taxo_correspondence_trees[DIRECTION_OUTGOING]
        self.assertEqual(incoming_tree.get_children(""), (incoming.correspondence_id,))
        self.assertEqual(outgoing_tree.get_children(""), (outgoing.correspondence_id,))
        self.assertEqual(
            incoming_tree.set(incoming.correspondence_id, "attachments"), "1"
        )
        card = win._taxo_correspondence_details[DIRECTION_INCOMING].get()
        self.assertIn("Запит щодо перевезень", card)
        self.assertIn("Зовнішній №: A-15", card)
        self.assertIn("Активних вкладень: 1", card)

        win._taxo_correspondence_search.set("Бета")
        win._taxo_correspondence_refresh()
        self.assertEqual(incoming_tree.get_children(""), ())
        self.assertEqual(outgoing_tree.get_children(""), (outgoing.correspondence_id,))

        win._taxo_correspondence_search.set("")
        win._taxo_correspondence_date_filter.set("21.11.2026")
        win._taxo_correspondence_refresh()
        self.assertEqual(incoming_tree.get_children(""), (incoming.correspondence_id,))
        self.assertEqual(outgoing_tree.get_children(""), ())

        again = correspondence_ui.open_correspondence_center(
            self.root, self.core, self.workspace
        )
        self.assertIs(again, win)

    def test_minimum_window_keeps_primary_controls_on_screen(self):
        core = _core(self.messages, size=(760, 520))
        win = correspondence_ui.open_correspondence_center(
            self.root, core, self.workspace
        )
        self._show(win)
        win.geometry("760x520+20+20")
        self._show(win)

        for text in ("Новий вхідний…", "Новий вихідний…", "Закрити"):
            button = button_by_text(win, text)
            self.assertIsNotNone(button, text)
            self.assertTrue(button.winfo_ismapped(), text)
            x = button.winfo_rootx() - win.winfo_rootx()
            y = button.winfo_rooty() - win.winfo_rooty()
            self.assertGreaterEqual(x, 0, text)
            self.assertGreaterEqual(y, 0, text)
            self.assertLessEqual(
                x + button.winfo_width(), win.winfo_width() + 2, text
            )
            self.assertLessEqual(
                y + button.winfo_height(), win.winfo_height() + 2, text
            )

        self.assertIsNotNone(button_by_text(win, "Сьогодні"))
        self.assertIsNotNone(button_by_text(win, "Усі дати"))

    def test_outgoing_form_without_sent_date_stays_registered(self):
        saved = []
        form = correspondence_ui.open_correspondence_form(
            self.root,
            self.core,
            self.workspace,
            DIRECTION_OUTGOING,
            saved.append,
        )
        self._show(form)
        variables = form._taxo_correspondence_vars
        variables["correspondent"].set("ТОВ Адресат")
        variables["subject"].set("Зареєстровано, але ще не відправлено")
        self.assertEqual(variables["action_date"].get(), "")

        form._taxo_correspondence_save()
        self._show()

        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].status, "registered")
        self.assertEqual(saved[0].sent_date, "")
        self.assertFalse(form.winfo_exists())

    def test_unsaved_form_x_and_cancel_require_explicit_confirmation(self):
        form = correspondence_ui.open_correspondence_form(
            self.root,
            self.core,
            self.workspace,
            DIRECTION_INCOMING,
            lambda _record: None,
        )
        self._show(form)
        form._taxo_correspondence_vars["subject"].set("Незбережена тема")
        self.messages.askyesno.return_value = False

        form._taxo_correspondence_cancel()
        self._show(form)
        self.assertTrue(form.winfo_exists())
        self.messages.askyesno.assert_called_once()

        self.messages.askyesno.return_value = True
        form._taxo_correspondence_cancel()
        self._show()
        self.assertFalse(form.winfo_exists())

    def test_attachment_dialog_has_active_history_and_does_not_change_status(self):
        incoming = register_incoming(
            self.workspace,
            registration_date="2026-11-22",
            correspondent="A",
            subject="Attachment card",
        )
        pdf = Path(self.temp.name) / "a.pdf"
        pdf.write_bytes(b"%PDF-1.7\nattachment dialog\n%%EOF\n")
        add_correspondence_file(
            self.workspace, incoming.correspondence_id, pdf
        )

        dialog = correspondence_ui.open_attachments_dialog(
            self.root, self.core, self.workspace, incoming
        )
        self._show(dialog)
        notebooks = [
            item for item in walk(dialog)
            if isinstance(item, ttk.Notebook)
        ]
        self.assertEqual(len(notebooks), 1)
        self.assertEqual(
            [str(notebooks[0].tab(tab, "text")) for tab in notebooks[0].tabs()],
            ["Активні", "Історія"],
        )
        self.assertEqual(
            len(dialog._taxo_correspondence_attachment_tree.get_children("")),
            1,
        )
        for text in (
            "Додати файл…",
            "Додати готовий документ…",
            "Відкрити",
            "Прибрати",
            "Закрити",
        ):
            self.assertIsNotNone(button_by_text(dialog, text), text)

        current = correspondence_ui.get_correspondence(
            self.workspace, incoming.correspondence_id
        )
        self.assertEqual(current.status, "new")
        self.assertEqual(current.received_date, "")


if __name__ == "__main__":
    unittest.main()
