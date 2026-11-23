# -*- coding: utf-8 -*-
import json
import sqlite3
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from tkinter import ttk

import correspondence_ui
import workspace
from correspondence_registry import (
    DIRECTION_INCOMING,
    DIRECTION_OUTGOING,
    FORMAT,
    FORMAT_V1,
    get_correspondence,
    read_registry,
)
from correspondence_service import (
    available_status_transitions,
    change_correspondence_status,
    correspondence_state_history,
    is_overdue,
    mark_received,
    mark_sent,
    next_outgoing_number,
    overdue_correspondence,
    register_incoming,
    register_outgoing,
)


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


class CorrespondenceStateR4DomainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "work"
        workspace.ensure_workspace(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_registration_does_not_invent_sent_or_received(self):
        incoming = register_incoming(
            self.root,
            registration_date="2026-11-23",
            correspondent="A",
            subject="Incoming",
        )
        outgoing = register_outgoing(
            self.root,
            registration_date="2026-11-23",
            correspondent="B",
            subject="Outgoing",
        )
        self.assertEqual(incoming.status, "new")
        self.assertEqual(incoming.received_date, "")
        self.assertEqual(outgoing.status, "registered")
        self.assertEqual(outgoing.sent_date, "")
        self.assertEqual(correspondence_state_history(
            self.root, incoming.correspondence_id
        ), ())
        self.assertEqual(correspondence_state_history(
            self.root, outgoing.correspondence_id
        ), ())

    def test_explicit_received_or_sent_date_at_registration_is_a_fact(self):
        incoming = register_incoming(
            self.root,
            registration_date="2026-11-23",
            received_date="2026-11-22",
            correspondent="A",
            subject="Already received",
        )
        outgoing = register_outgoing(
            self.root,
            registration_date="2026-11-23",
            sent_date="2026-11-23",
            correspondent="B",
            subject="Already sent",
        )
        self.assertEqual(incoming.status, "received")
        self.assertEqual(incoming.received_date, "2026-11-22")
        self.assertEqual(outgoing.status, "sent")
        self.assertEqual(outgoing.sent_date, "2026-11-23")

    def test_mark_received_and_mark_sent_are_dated_atomic_transitions(self):
        incoming = register_incoming(
            self.root,
            registration_date="2026-11-23",
            correspondent="A",
            subject="Incoming",
        )
        outgoing = register_outgoing(
            self.root,
            registration_date="2026-11-23",
            correspondent="B",
            subject="Outgoing",
        )

        received = mark_received(
            self.root,
            incoming.correspondence_id,
            received_date="2026-11-23",
        )
        sent = mark_sent(
            self.root,
            outgoing.correspondence_id,
            sent_date="2026-11-23",
        )

        self.assertEqual((received.status, received.received_date), (
            "received", "2026-11-23"
        ))
        self.assertEqual((sent.status, sent.sent_date), (
            "sent", "2026-11-23"
        ))

        incoming_history = correspondence_state_history(
            self.root, incoming.correspondence_id
        )
        outgoing_history = correspondence_state_history(
            self.root, outgoing.correspondence_id
        )
        self.assertEqual(
            [(event.from_status, event.to_status, event.action_date)
             for event in incoming_history],
            [("new", "received", "2026-11-23")],
        )
        self.assertEqual(
            [(event.from_status, event.to_status, event.action_date)
             for event in outgoing_history],
            [("registered", "sent", "2026-11-23")],
        )

    def test_delivery_transitions_require_explicit_dates(self):
        incoming = register_incoming(
            self.root,
            registration_date="2026-11-23",
            correspondent="A",
            subject="Incoming",
        )
        outgoing = register_outgoing(
            self.root,
            registration_date="2026-11-23",
            correspondent="B",
            subject="Outgoing",
        )
        with self.assertRaises(ValueError):
            mark_received(
                self.root, incoming.correspondence_id, received_date=""
            )
        with self.assertRaises(ValueError):
            mark_sent(
                self.root, outgoing.correspondence_id, sent_date=""
            )
        with self.assertRaises(ValueError):
            change_correspondence_status(
                self.root, incoming.correspondence_id, "received"
            )
        with self.assertRaises(ValueError):
            change_correspondence_status(
                self.root, outgoing.correspondence_id, "sent"
            )

    def test_only_forward_safe_transitions_are_offered_and_applied(self):
        incoming = register_incoming(
            self.root,
            registration_date="2026-11-23",
            correspondent="A",
            subject="Workflow",
        )
        self.assertEqual(
            available_status_transitions(incoming),
            ("received", "cancelled"),
        )

        incoming = mark_received(
            self.root,
            incoming.correspondence_id,
            received_date="2026-11-23",
        )
        self.assertIn("in_progress", available_status_transitions(incoming))

        incoming = change_correspondence_status(
            self.root, incoming.correspondence_id, "in_progress"
        )
        incoming = change_correspondence_status(
            self.root, incoming.correspondence_id, "closed"
        )
        self.assertEqual(available_status_transitions(incoming), ())

        with self.assertRaises(ValueError):
            change_correspondence_status(
                self.root, incoming.correspondence_id, "in_progress"
            )
        with self.assertRaises(ValueError):
            mark_received(
                self.root,
                incoming.correspondence_id,
                received_date="2026-11-23",
            )

        history = correspondence_state_history(
            self.root, incoming.correspondence_id
        )
        self.assertEqual(
            [(event.from_status, event.to_status) for event in history],
            [
                ("new", "received"),
                ("received", "in_progress"),
                ("in_progress", "closed"),
            ],
        )

    def test_history_survives_registration_of_another_letter(self):
        outgoing = register_outgoing(
            self.root,
            registration_date="2026-11-23",
            correspondent="A",
            subject="First",
        )
        mark_sent(
            self.root, outgoing.correspondence_id, sent_date="2026-11-23"
        )
        before = correspondence_state_history(
            self.root, outgoing.correspondence_id
        )
        self.assertEqual(len(before), 1)

        register_incoming(
            self.root,
            registration_date="2026-11-23",
            correspondent="B",
            subject="Second",
        )

        after = correspondence_state_history(
            self.root, outgoing.correspondence_id
        )
        self.assertEqual(after, before)

    def test_legacy_v1_registry_is_read_and_migrates_without_number_loss(self):
        outgoing = register_outgoing(
            self.root,
            registration_date="2026-11-23",
            correspondent="A",
            subject="Legacy",
        )
        path = self.root / "Data" / "Correspondence" / "registry.json"
        data = json.loads(path.read_text("utf-8"))
        data["format"] = FORMAT_V1
        data.pop("state_events")
        path.write_text(
            json.dumps(data, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )

        legacy = read_registry(self.root)
        self.assertEqual(len(legacy.records), 1)
        self.assertEqual(legacy.state_events, ())
        self.assertEqual(
            next_outgoing_number(self.root, "2026-11-23"),
            "Вих. № 0002/2026",
        )

        mark_sent(
            self.root, outgoing.correspondence_id, sent_date="2026-11-23"
        )
        migrated = json.loads(path.read_text("utf-8"))
        self.assertEqual(migrated["format"], FORMAT)
        self.assertEqual(len(migrated["state_events"]), 1)
        self.assertEqual(
            next_outgoing_number(self.root, "2026-11-23"),
            "Вих. № 0002/2026",
        )

    def test_tampered_state_history_fails_closed(self):
        outgoing = register_outgoing(
            self.root,
            registration_date="2026-11-23",
            correspondent="A",
            subject="Tamper",
        )
        mark_sent(
            self.root, outgoing.correspondence_id, sent_date="2026-11-23"
        )
        path = self.root / "Data" / "Correspondence" / "registry.json"
        data = json.loads(path.read_text("utf-8"))
        data["state_events"][0]["to_status"] = "closed"
        path.write_text(
            json.dumps(data, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
        with self.assertRaises(ValueError):
            read_registry(self.root)
        with self.assertRaises(ValueError):
            register_incoming(
                self.root,
                registration_date="2026-11-23",
                correspondent="B",
                subject="Must not overwrite tamper",
            )

    def test_overdue_uses_explicit_due_date_and_open_business_state(self):
        incoming = register_incoming(
            self.root,
            registration_date="2026-11-20",
            correspondent="A",
            subject="Due",
            due_date="2026-11-21",
        )
        outgoing = register_outgoing(
            self.root,
            registration_date="2026-11-20",
            correspondent="B",
            subject="Due outgoing",
            due_date="2026-11-21",
        )
        no_due = register_incoming(
            self.root,
            registration_date="2026-11-20",
            correspondent="C",
            subject="No due",
        )
        self.assertTrue(is_overdue(incoming, "2026-11-23"))
        self.assertTrue(is_overdue(outgoing, "2026-11-23"))
        self.assertFalse(is_overdue(no_due, "2026-11-23"))
        self.assertEqual(
            {row.correspondence_id for row in overdue_correspondence(
                self.root, "2026-11-23"
            )},
            {incoming.correspondence_id, outgoing.correspondence_id},
        )

        mark_sent(
            self.root, outgoing.correspondence_id, sent_date="2026-11-22"
        )
        incoming = mark_received(
            self.root, incoming.correspondence_id, received_date="2026-11-20"
        )
        incoming = change_correspondence_status(
            self.root, incoming.correspondence_id, "closed"
        )
        self.assertFalse(is_overdue(
            get_correspondence(self.root, outgoing.correspondence_id),
            "2026-11-23",
        ))
        self.assertFalse(is_overdue(incoming, "2026-11-23"))

    def test_full_backup_restore_preserves_state_history_and_next_number(self):
        main_db = workspace.paths_for(self.root)["main_db"]
        con = sqlite3.connect(str(main_db))
        try:
            con.execute("CREATE TABLE backup_probe (id INTEGER PRIMARY KEY)")
            con.commit()
        finally:
            con.close()

        outgoing = register_outgoing(
            self.root,
            registration_date="2026-11-23",
            correspondent="A",
            subject="Backup",
        )
        mark_sent(
            self.root, outgoing.correspondence_id, sent_date="2026-11-23"
        )

        archive = workspace.create_workspace_backup_archive(
            self.root,
            self.base / "backup.zip",
            app_version="10.24-r3",
        )
        restored = self.base / "restored"
        workspace.restore_workspace_backup_archive(archive, restored)

        record = get_correspondence(
            restored, outgoing.correspondence_id
        )
        history = correspondence_state_history(
            restored, outgoing.correspondence_id
        )
        self.assertEqual(record.status, "sent")
        self.assertEqual(record.sent_date, "2026-11-23")
        self.assertEqual(
            [(event.from_status, event.to_status) for event in history],
            [("registered", "sent")],
        )
        self.assertEqual(
            next_outgoing_number(restored, "2026-11-23"),
            "Вих. № 0002/2026",
        )


class CorrespondenceStateR4UiTests(unittest.TestCase):
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

    def test_center_shows_overdue_and_explicit_state_actions(self):
        incoming = register_incoming(
            self.workspace,
            registration_date="2026-11-20",
            correspondent="A",
            subject="Incoming overdue",
            due_date="2000-01-01",
        )
        outgoing = register_outgoing(
            self.workspace,
            registration_date="2026-11-20",
            correspondent="B",
            subject="Outgoing overdue",
            due_date="2000-01-01",
        )

        win = correspondence_ui.open_correspondence_center(
            self.root, self.core, self.workspace
        )
        self._show(win)

        incoming_tree = win._taxo_correspondence_trees[DIRECTION_INCOMING]
        outgoing_tree = win._taxo_correspondence_trees[DIRECTION_OUTGOING]
        self.assertEqual(
            incoming_tree.set(incoming.correspondence_id, "control"),
            "Прострочено",
        )
        self.assertEqual(
            outgoing_tree.set(outgoing.correspondence_id, "control"),
            "Прострочено",
        )
        self.assertIn("прострочено: 2", win._taxo_correspondence_status.get())

        for text in ("Отримано…", "Змінити стан…", "Історія…"):
            self.assertIsNotNone(button_by_text(win, text), text)

        book = win._taxo_correspondence_notebook
        book.select(1)
        self._show(win)
        self.assertIsNotNone(button_by_text(win, "Надіслано…"))

    def test_explicit_mark_sent_dialog_records_date_and_history(self):
        outgoing = register_outgoing(
            self.workspace,
            registration_date="2026-11-23",
            correspondent="B",
            subject="Send me",
        )
        win = correspondence_ui.open_correspondence_center(
            self.root, self.core, self.workspace
        )
        self._show(win)
        win._taxo_correspondence_notebook.select(1)
        self._show(win)

        dialog = win._taxo_correspondence_mark_sent()
        self.assertIsNotNone(dialog)
        self._show(dialog)
        dialog._taxo_correspondence_action_date.set("23.11.2026")
        dialog._taxo_correspondence_apply()
        self._show(win)

        record = get_correspondence(
            self.workspace, outgoing.correspondence_id
        )
        self.assertEqual(record.status, "sent")
        self.assertEqual(record.sent_date, "2026-11-23")
        self.assertEqual(
            [(event.from_status, event.to_status)
             for event in correspondence_state_history(
                 self.workspace, outgoing.correspondence_id
             )],
            [("registered", "sent")],
        )

        history = win._taxo_correspondence_open_outgoing_history()
        self.assertIsNotNone(history)
        self._show(history)
        content = history._taxo_correspondence_history_text.get(
            "1.0", "end-1c"
        )
        self.assertIn("Зареєстровано", content)
        self.assertIn("Надіслано", content)

    def test_minimum_window_keeps_state_actions_reachable(self):
        register_incoming(
            self.workspace,
            registration_date="2026-11-23",
            correspondent="A",
            subject="Reachability",
        )
        core = _core(self.messages, size=(760, 520))
        win = correspondence_ui.open_correspondence_center(
            self.root, core, self.workspace
        )
        self._show(win)
        win.geometry("760x520+20+20")
        self._show(win)

        for text in (
            "Отримано…",
            "Змінити стан…",
            "Історія…",
            "Відповісти…",
            "Вкладення…",
            "Закрити",
        ):
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


if __name__ == "__main__":
    unittest.main()
