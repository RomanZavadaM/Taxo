# -*- coding: utf-8 -*-
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

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
from correspondence_registry import get_correspondence
from correspondence_service import (
    mark_received,
    register_incoming,
    register_outgoing,
    register_response,
)


class CorrespondenceCasesR5DomainTests(unittest.TestCase):
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
            (self.root / "Data" / "Correspondence" / "cases.json").read_text(
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

        path = self.root / "Data" / "Correspondence" / "cases.json"
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


if __name__ == "__main__":
    unittest.main()
