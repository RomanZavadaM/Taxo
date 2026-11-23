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
from correspondence_cases import (
    FORMAT,
    add_correspondence_to_case,
    add_linked_correspondence_to_case,
    case_for_correspondence,
    create_case,
    get_case,
    linked_correspondence_candidates,
    list_case_correspondence,
    list_cases,
    move_correspondence_to_case,
    read_cases,
    remove_correspondence_from_case,
    rename_case,
    set_case_archived,
)
from correspondence_registry import (
    DIRECTION_INCOMING,
    DIRECTION_OUTGOING,
    get_correspondence,
)
from correspondence_service import (
    mark_received,
    register_incoming,
    register_outgoing,
    register_response,
)


class CorrespondenceCasesR5DomainTests(unittest.TestCase):
    def test_candidate_identity_and_start_guards(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.24-r5\n",
        )
        self.assertIn(
            'APP_VERSION = "10.24-r5"',
            (root / "main.py").read_text("utf-8"),
        )
        start = (root / "START.bat").read_text("utf-8")
        self.assertIn("Taxo 10.24-r5", start)
        self.assertIn("correspondence_cases.py", start)
        self.assertEqual(
            (root / ".release" / "full-current").read_text("utf-8"),
            "10.24-r5\n",
        )

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "work"
        workspace.ensure_workspace(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def _incoming(self, subject="Incoming", related_ids=()):
        return register_incoming(
            self.root,
            registration_date="2026-11-23",
            correspondent="A",
            subject=subject,
            related_ids=related_ids,
        )

    def _outgoing(self, subject="Outgoing", response_to_ids=(), related_ids=()):
        return register_outgoing(
            self.root,
            registration_date="2026-11-23",
            correspondent="B",
            subject=subject,
            response_to_ids=response_to_ids,
            related_ids=related_ids,
        )

    def test_start_requires_correspondence_cases_module(self):
        root = Path(__file__).resolve().parents[1]
        start = (root / "START.bat").read_text("utf-8")
        self.assertIn(
            'src\\taxo\\correspondence_cases.py',
            start,
        )

    def test_case_membership_is_logical_and_preserves_letter_identity(self):
        incoming = self._incoming()
        before = get_correspondence(self.root, incoming.correspondence_id)
        case = create_case(self.root, "Договір 2026", notes="Переписка")
        case = add_correspondence_to_case(
            self.root, case.case_id, incoming.correspondence_id
        )

        after = get_correspondence(self.root, incoming.correspondence_id)
        self.assertEqual(before, after)
        self.assertEqual(case.correspondence_ids, (incoming.correspondence_id,))
        self.assertEqual(
            case_for_correspondence(self.root, incoming.correspondence_id).case_id,
            case.case_id,
        )

        data = json.loads(
            (self.root / "Data" / "CorrespondenceCases" / "cases.json").read_text(
                "utf-8"
            )
        )
        self.assertEqual(data["format"], FORMAT)
        self.assertEqual(
            data["cases"][0]["correspondence_ids"],
            [incoming.correspondence_id],
        )
        self.assertNotIn("document_ref", data["cases"][0])
        self.assertNotIn("file", data["cases"][0])

    def test_one_letter_cannot_belong_to_two_cases(self):
        incoming = self._incoming()
        first = create_case(self.root, "Перша")
        second = create_case(self.root, "Друга")
        add_correspondence_to_case(
            self.root, first.case_id, incoming.correspondence_id
        )
        with self.assertRaises(ValueError):
            add_correspondence_to_case(
                self.root, second.case_id, incoming.correspondence_id
            )
        self.assertEqual(
            case_for_correspondence(self.root, incoming.correspondence_id).case_id,
            first.case_id,
        )

    def test_case_titles_are_unique_casefolded(self):
        create_case(self.root, "Замовник А")
        with self.assertRaises(ValueError):
            create_case(self.root, "замовник а")

    def test_rename_and_archive_keep_case_id_and_members(self):
        incoming = self._incoming()
        case = create_case(self.root, "Стара назва")
        case = add_correspondence_to_case(
            self.root, case.case_id, incoming.correspondence_id
        )
        original_id = case.case_id

        case = rename_case(
            self.root, case.case_id, "Нова назва", notes="Оновлено"
        )
        self.assertEqual(case.case_id, original_id)
        self.assertEqual(case.correspondence_ids, (incoming.correspondence_id,))
        self.assertEqual(case.notes, "Оновлено")

        case = set_case_archived(self.root, case.case_id, True)
        self.assertTrue(case.archived)
        self.assertEqual(list_cases(self.root), ())
        self.assertEqual(len(list_cases(self.root, include_archived=True)), 1)

        other = self._incoming("Other")
        with self.assertRaises(ValueError):
            add_correspondence_to_case(
                self.root, case.case_id, other.correspondence_id
            )
        with self.assertRaises(ValueError):
            rename_case(self.root, case.case_id, "Не можна")
        with self.assertRaises(ValueError):
            remove_correspondence_from_case(
                self.root, case.case_id, incoming.correspondence_id
            )
        with self.assertRaises(ValueError):
            move_correspondence_to_case(
                self.root, incoming.correspondence_id, None
            )

        case = set_case_archived(self.root, case.case_id, False)
        case = add_correspondence_to_case(
            self.root, case.case_id, other.correspondence_id
        )
        self.assertEqual(len(case.correspondence_ids), 2)

    def test_remove_membership_never_deletes_or_changes_letter(self):
        incoming = self._incoming()
        mark_received(
            self.root, incoming.correspondence_id, received_date="2026-11-23"
        )
        before = get_correspondence(self.root, incoming.correspondence_id)

        case = create_case(self.root, "Тема")
        add_correspondence_to_case(
            self.root, case.case_id, incoming.correspondence_id
        )
        case = remove_correspondence_from_case(
            self.root, case.case_id, incoming.correspondence_id
        )

        self.assertEqual(case.correspondence_ids, ())
        self.assertIsNone(
            case_for_correspondence(self.root, incoming.correspondence_id)
        )
        self.assertEqual(
            get_correspondence(self.root, incoming.correspondence_id),
            before,
        )

    def test_case_thread_follows_explicit_response_and_related_links(self):
        incoming = self._incoming("Request")
        response = register_response(
            self.root,
            incoming.correspondence_id,
            registration_date="2026-11-23",
            subject="Answer",
        )
        follow_up = register_incoming(
            self.root,
            registration_date="2026-11-24",
            correspondent="A",
            subject="Follow-up",
            related_ids=(response.correspondence_id,),
        )

        case = create_case(self.root, "Request thread")
        add_correspondence_to_case(
            self.root, case.case_id, incoming.correspondence_id
        )

        candidates = linked_correspondence_candidates(
            self.root, case.case_id
        )
        self.assertEqual(
            {row.correspondence_id for row in candidates},
            {response.correspondence_id, follow_up.correspondence_id},
        )

        case = add_linked_correspondence_to_case(self.root, case.case_id)
        self.assertEqual(
            set(case.correspondence_ids),
            {
                incoming.correspondence_id,
                response.correspondence_id,
                follow_up.correspondence_id,
            },
        )
        thread = list_case_correspondence(self.root, case.case_id)
        self.assertEqual(
            [row.correspondence_id for row in thread],
            [
                incoming.correspondence_id,
                response.correspondence_id,
                follow_up.correspondence_id,
            ],
        )

    def test_linked_add_fails_if_candidate_belongs_to_other_case(self):
        incoming = self._incoming("Request")
        response = register_response(
            self.root,
            incoming.correspondence_id,
            registration_date="2026-11-23",
            subject="Answer",
        )
        first = create_case(self.root, "First")
        second = create_case(self.root, "Second")
        add_correspondence_to_case(
            self.root, first.case_id, incoming.correspondence_id
        )
        add_correspondence_to_case(
            self.root, second.case_id, response.correspondence_id
        )

        with self.assertRaises(ValueError):
            add_linked_correspondence_to_case(self.root, first.case_id)
        self.assertEqual(
            get_case(self.root, first.case_id).correspondence_ids,
            (incoming.correspondence_id,),
        )

    def test_tampered_missing_letter_fails_closed(self):
        incoming = self._incoming()
        case = create_case(self.root, "Tamper")
        add_correspondence_to_case(
            self.root, case.case_id, incoming.correspondence_id
        )

        path = self.root / "Data" / "CorrespondenceCases" / "cases.json"
        data = json.loads(path.read_text("utf-8"))
        data["cases"][0]["correspondence_ids"] = [
            "cr-" + ("f" * 32)
        ]
        path.write_text(
            json.dumps(data, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            read_cases(self.root)
        with self.assertRaises(ValueError):
            create_case(self.root, "Must not overwrite tamper")

    def test_full_backup_restore_preserves_cases_and_membership(self):
        main_db = workspace.paths_for(self.root)["main_db"]
        con = sqlite3.connect(str(main_db))
        try:
            con.execute("CREATE TABLE backup_probe (id INTEGER PRIMARY KEY)")
            con.commit()
        finally:
            con.close()

        incoming = self._incoming()
        response = register_response(
            self.root,
            incoming.correspondence_id,
            registration_date="2026-11-24",
            subject="Answer",
        )
        case = create_case(self.root, "Backup case", notes="Keep me")
        add_correspondence_to_case(
            self.root, case.case_id, incoming.correspondence_id
        )
        add_correspondence_to_case(
            self.root, case.case_id, response.correspondence_id
        )

        archive = workspace.create_workspace_backup_archive(
            self.root,
            self.base / "backup.zip",
            app_version="10.24-r4",
        )
        restored = self.base / "restored"
        workspace.restore_workspace_backup_archive(archive, restored)

        restored_case = get_case(restored, case.case_id)
        self.assertEqual(restored_case.title, "Backup case")
        self.assertEqual(restored_case.notes, "Keep me")
        self.assertEqual(
            set(restored_case.correspondence_ids),
            {incoming.correspondence_id, response.correspondence_id},
        )
        self.assertEqual(
            case_for_correspondence(
                restored, incoming.correspondence_id
            ).case_id,
            case.case_id,
        )


def _walk(widget):
    for child in widget.winfo_children():
        yield child
        yield from _walk(child)


def _button_by_text(root, text):
    for widget in _walk(root):
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


class CorrespondenceCasesR5UiTests(unittest.TestCase):
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

    def _incoming(self, subject="Incoming"):
        return register_incoming(
            self.workspace,
            registration_date="2026-11-23",
            correspondent="A",
            subject=subject,
        )

    def test_center_has_cases_tab_create_and_assign_flow(self):
        incoming = self._incoming("Request")
        win = correspondence_ui.open_correspondence_center(
            self.root, self.core, self.workspace
        )
        self._show(win)

        book = win._taxo_correspondence_notebook
        self.assertEqual(len(book.tabs()), 3)
        self.assertEqual(book.tab(2, "text"), "Справи")

        dialog = win._taxo_correspondence_new_case()
        self.assertIsNotNone(dialog)
        self._show(dialog)
        dialog._taxo_correspondence_case_title.set("Замовник А — договір")
        dialog._taxo_correspondence_case_notes.insert(
            "1.0", "Переписка по договору"
        )
        dialog._taxo_correspondence_case_save()
        self._show(win)

        case_tree = win._taxo_correspondence_case_tree
        case_ids = case_tree.get_children("")
        self.assertEqual(len(case_ids), 1)
        case_id = case_ids[0]
        self.assertEqual(
            case_tree.set(case_id, "title"), "Замовник А — договір"
        )

        book.select(0)
        self._show(win)
        incoming_tree = win._taxo_correspondence_trees[DIRECTION_INCOMING]
        incoming_tree.selection_set(incoming.correspondence_id)
        incoming_tree.focus(incoming.correspondence_id)
        self._show(win)

        assign = win._taxo_correspondence_assign_incoming_case()
        self.assertIsNotNone(assign)
        self._show(assign)
        assign._taxo_correspondence_case_choice.set("Замовник А — договір")
        assign._taxo_correspondence_case_save()
        self._show(win)

        owner = case_for_correspondence(
            self.workspace, incoming.correspondence_id
        )
        self.assertIsNotNone(owner)
        self.assertEqual(owner.case_id, case_id)
        self.assertIn(
            "Справа: Замовник А — договір",
            win._taxo_correspondence_details[DIRECTION_INCOMING].get(),
        )

    def test_case_thread_ui_adds_explicit_links_and_opens_member(self):
        incoming = self._incoming("Request")
        response = register_response(
            self.workspace,
            incoming.correspondence_id,
            registration_date="2026-11-23",
            subject="Answer",
        )
        follow_up = register_incoming(
            self.workspace,
            registration_date="2026-11-24",
            correspondent="A",
            subject="Follow-up",
            related_ids=(response.correspondence_id,),
        )
        case = create_case(self.workspace, "Thread")
        add_correspondence_to_case(
            self.workspace, case.case_id, incoming.correspondence_id
        )

        win = correspondence_ui.open_correspondence_center(
            self.root, self.core, self.workspace
        )
        self._show(win)
        book = win._taxo_correspondence_notebook
        book.select(2)
        self._show(win)

        case_tree = win._taxo_correspondence_case_tree
        case_tree.selection_set(case.case_id)
        case_tree.focus(case.case_id)
        self._show(win)

        result = win._taxo_correspondence_add_case_linked()
        self.assertIsNotNone(result)
        self._show(win)

        members = win._taxo_correspondence_case_member_tree
        self.assertEqual(
            set(members.get_children("")),
            {
                incoming.correspondence_id,
                response.correspondence_id,
                follow_up.correspondence_id,
            },
        )

        members.selection_set(response.correspondence_id)
        members.focus(response.correspondence_id)
        self._show(win)
        opened = win._taxo_correspondence_open_case_member()
        self.assertEqual(opened.correspondence_id, response.correspondence_id)
        self._show(win)
        self.assertEqual(book.index(book.select()), 1)
        outgoing_tree = win._taxo_correspondence_trees[DIRECTION_OUTGOING]
        self.assertEqual(
            tuple(outgoing_tree.selection()),
            (response.correspondence_id,),
        )

    def test_archived_case_is_read_only_until_restored(self):
        incoming = self._incoming()
        case = create_case(self.workspace, "Archive me")
        add_correspondence_to_case(
            self.workspace, case.case_id, incoming.correspondence_id
        )
        set_case_archived(self.workspace, case.case_id, True)

        win = correspondence_ui.open_correspondence_center(
            self.root, self.core, self.workspace
        )
        self._show(win)
        win._taxo_correspondence_notebook.select(2)
        self._show(win)

        case_tree = win._taxo_correspondence_case_tree
        case_tree.selection_set(case.case_id)
        case_tree.focus(case.case_id)
        self._show(win)
        members = win._taxo_correspondence_case_member_tree
        members.selection_set(incoming.correspondence_id)
        members.focus(incoming.correspondence_id)
        self._show(win)

        buttons = win._taxo_correspondence_case_buttons
        self.assertEqual(str(buttons["rename"].cget("state")), "disabled")
        self.assertEqual(str(buttons["linked"].cget("state")), "disabled")
        self.assertEqual(str(buttons["remove"].cget("state")), "disabled")
        self.assertEqual(str(buttons["archive"].cget("state")), "normal")
        self.assertEqual(str(buttons["archive"].cget("text")), "Відновити")

        restored = win._taxo_correspondence_toggle_case_archive()
        self.assertFalse(restored.archived)
        self._show(win)
        self.assertEqual(str(buttons["rename"].cget("state")), "normal")

    def test_case_editor_x_and_cancel_protect_unsaved_changes(self):
        win = correspondence_ui.open_correspondence_center(
            self.root, self.core, self.workspace
        )
        self._show(win)
        dialog = win._taxo_correspondence_new_case()
        self._show(dialog)
        dialog._taxo_correspondence_case_title.set("Незбережена справа")

        self.messages.askyesno.return_value = False
        dialog._taxo_correspondence_case_cancel()
        self._show(dialog)
        self.assertTrue(dialog.winfo_exists())

        self.messages.askyesno.return_value = True
        dialog._taxo_correspondence_case_cancel()
        self.root.update_idletasks()
        self.assertFalse(dialog.winfo_exists())
        self.assertEqual(list_cases(self.workspace), ())

    def test_minimum_window_keeps_case_actions_reachable(self):
        incoming = self._incoming("Reachability")
        case = create_case(self.workspace, "Reachability case")
        add_correspondence_to_case(
            self.workspace, case.case_id, incoming.correspondence_id
        )

        core = _core(self.messages, size=(760, 520))
        win = correspondence_ui.open_correspondence_center(
            self.root, core, self.workspace
        )
        self._show(win)
        win.geometry("760x520+20+20")
        win._taxo_correspondence_notebook.select(2)
        self._show(win)

        for text in (
            "Нова справа…",
            "Перейменувати…",
            "Архівувати",
            "Додати пов'язані",
            "Відкрити лист",
            "Вилучити зі справи",
            "Оновити справи",
            "Закрити",
        ):
            button = _button_by_text(win, text)
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
