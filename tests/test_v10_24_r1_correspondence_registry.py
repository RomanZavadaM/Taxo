# -*- coding: utf-8 -*-
import json
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import workspace
from correspondence_registry import (
    DIRECTION_INCOMING,
    DIRECTION_OUTGOING,
    read_registry,
    register_correspondence,
)
from correspondence_service import (
    incoming_journal,
    is_overdue,
    next_incoming_number,
    next_outgoing_number,
    outgoing_journal,
    register_incoming,
    register_outgoing,
    register_response,
    responses_for,
)


class CorrespondenceRegistryR1Tests(unittest.TestCase):
    def test_candidate_identity_and_start_guards(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.25-r6\n",
        )
        self.assertIn(
            'APP_VERSION = "10.25-r6"',
            (root / "main.py").read_text("utf-8"),
        )
        start = (root / "START.bat").read_text("utf-8")
        self.assertIn("Taxo 10.25-r6", start)
        self.assertIn("correspondence_registry.py", start)
        self.assertIn("correspondence_service.py", start)
        self.assertEqual(
            (root / ".release" / "full-current").read_text("utf-8"),
            "10.25-r6\n",
        )

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "work"
        workspace.ensure_workspace(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_incoming_and_outgoing_have_independent_sequences(self):
        first_in = register_incoming(
            self.root,
            registration_date="2026-11-22",
            correspondent="ТОВ Альфа",
            subject="Перший вхідний",
            external_number="A-77",
        )
        first_out = register_outgoing(
            self.root,
            registration_date="2026-11-22",
            correspondent="ТОВ Бета",
            subject="Перший вихідний",
        )
        second_in = register_incoming(
            self.root,
            registration_date="2026-11-22",
            correspondent="ТОВ Гамма",
            subject="Другий вхідний",
        )
        second_out = register_outgoing(
            self.root,
            registration_date="2026-11-22",
            correspondent="ТОВ Дельта",
            subject="Другий вихідний",
        )

        self.assertEqual(first_in.registration_number, "Вх. № 0001/2026")
        self.assertEqual(second_in.registration_number, "Вх. № 0002/2026")
        self.assertEqual(first_out.registration_number, "Вих. № 0001/2026")
        self.assertEqual(second_out.registration_number, "Вих. № 0002/2026")
        self.assertEqual(first_in.external_number, "A-77")

    def test_preview_does_not_reserve_number_and_years_are_independent(self):
        self.assertEqual(
            next_incoming_number(self.root, "2026-12-31"),
            "Вх. № 0001/2026",
        )
        self.assertEqual(
            next_incoming_number(self.root, "2026-12-31"),
            "Вх. № 0001/2026",
        )
        register_incoming(
            self.root,
            registration_date="2026-12-31",
            correspondent="A",
            subject="2026",
        )
        register_incoming(
            self.root,
            registration_date="2027-01-01",
            correspondent="B",
            subject="2027",
        )
        self.assertEqual(
            next_incoming_number(self.root, "2026-12-31"),
            "Вх. № 0002/2026",
        )
        self.assertEqual(
            next_incoming_number(self.root, "2027-01-01"),
            "Вх. № 0002/2027",
        )
        self.assertEqual(
            next_outgoing_number(self.root, "2026-12-31"),
            "Вих. № 0001/2026",
        )

    def test_external_numbers_do_not_collide_with_taxo_numbers(self):
        a = register_incoming(
            self.root,
            registration_date="2026-11-22",
            correspondent="A",
            subject="One",
            external_number="0001/2026",
        )
        b = register_incoming(
            self.root,
            registration_date="2026-11-22",
            correspondent="B",
            subject="Two",
            external_number="0001/2026",
        )
        self.assertNotEqual(a.registration_number, b.registration_number)
        self.assertEqual(a.external_number, b.external_number)

    def test_response_is_outgoing_and_links_to_existing_incoming(self):
        incoming = register_incoming(
            self.root,
            registration_date="2026-11-22",
            correspondent="Управління",
            subject="Запит",
            due_date="2026-11-30",
        )
        response = register_response(
            self.root,
            incoming.correspondence_id,
            registration_date="2026-11-23",
            document_ref="paper:reply-001",
        )

        self.assertEqual(response.direction, DIRECTION_OUTGOING)
        self.assertEqual(response.correspondent, incoming.correspondent)
        self.assertEqual(response.subject, incoming.subject)
        self.assertEqual(
            response.response_to_ids, (incoming.correspondence_id,)
        )
        self.assertEqual(responses_for(
            self.root, incoming.correspondence_id
        ), (response,))

    def test_registration_does_not_require_file_or_delivery(self):
        incoming = register_incoming(
            self.root,
            registration_date="2026-11-22",
            correspondent="Паперовий відправник",
            subject="Лист без скана",
        )
        outgoing = register_outgoing(
            self.root,
            registration_date="2026-11-22",
            correspondent="Адресат",
            subject="Зареєстровано, але не відправлено",
        )
        self.assertEqual(incoming.document_ref, "")
        self.assertEqual(outgoing.document_ref, "")
        self.assertEqual(outgoing.sent_date, "")
        self.assertEqual(outgoing.status, "registered")

    def test_sent_outgoing_is_distinct_from_registered_only(self):
        registered = register_outgoing(
            self.root,
            registration_date="2026-11-22",
            correspondent="A",
            subject="Registered",
        )
        sent = register_outgoing(
            self.root,
            registration_date="2026-11-22",
            correspondent="B",
            subject="Sent",
            sent_date="2026-11-23",
            delivery_method="mail",
        )
        self.assertEqual(registered.status, "registered")
        self.assertEqual(sent.status, "sent")
        self.assertEqual(sent.sent_date, "2026-11-23")

    def test_semantic_dates_are_kept_separate(self):
        incoming = register_incoming(
            self.root,
            registration_date="2026-11-22",
            document_date="2026-11-18",
            received_date="2026-11-21",
            correspondent="A",
            subject="Dates",
        )
        self.assertEqual(incoming.document_date, "2026-11-18")
        self.assertEqual(incoming.received_date, "2026-11-21")
        self.assertEqual(incoming.registration_date, "2026-11-22")

    def test_invalid_direction_specific_date_fails(self):
        with self.assertRaises(ValueError):
            register_correspondence(
                self.root,
                direction=DIRECTION_INCOMING,
                registration_date="2026-11-22",
                correspondent="A",
                subject="Bad",
                sent_date="2026-11-22",
            )
        with self.assertRaises(ValueError):
            register_correspondence(
                self.root,
                direction=DIRECTION_OUTGOING,
                registration_date="2026-11-22",
                correspondent="A",
                subject="Bad",
                received_date="2026-11-22",
            )

    def test_overdue_uses_only_explicit_due_date_and_open_state(self):
        open_item = register_incoming(
            self.root,
            registration_date="2026-11-20",
            correspondent="A",
            subject="Control",
            due_date="2026-11-21",
        )
        no_due = register_incoming(
            self.root,
            registration_date="2026-11-20",
            correspondent="B",
            subject="No due",
        )
        sent = register_outgoing(
            self.root,
            registration_date="2026-11-20",
            correspondent="C",
            subject="Done",
            due_date="2026-11-21",
            sent_date="2026-11-21",
        )
        self.assertTrue(is_overdue(open_item, "2026-11-22"))
        self.assertFalse(is_overdue(no_due, "2026-11-22"))
        self.assertFalse(is_overdue(sent, "2026-11-22"))

    def test_backup_restore_preserves_registry_and_next_numbers(self):
        # A Taxo full backup is valid only when at least one Taxo SQLite DB is
        # present. Keep that production safety rule; make the fixture realistic.
        main_db = workspace.paths_for(self.root)["main_db"]
        con = sqlite3.connect(str(main_db))
        try:
            con.execute("CREATE TABLE backup_probe (id INTEGER PRIMARY KEY)")
            con.commit()
        finally:
            con.close()

        register_incoming(
            self.root,
            registration_date="2026-11-22",
            correspondent="A",
            subject="Incoming",
        )
        register_outgoing(
            self.root,
            registration_date="2026-11-22",
            correspondent="B",
            subject="Outgoing",
        )
        archive = workspace.create_workspace_backup_archive(
            self.root,
            self.base / "backup.zip",
            app_version="10.25-r6",
        )
        restored = self.base / "restored"
        workspace.restore_workspace_backup_archive(archive, restored)

        self.assertEqual(
            len(incoming_journal(restored)), 1
        )
        self.assertEqual(
            len(outgoing_journal(restored)), 1
        )
        self.assertEqual(
            next_incoming_number(restored, "2026-11-22"),
            "Вх. № 0002/2026",
        )
        self.assertEqual(
            next_outgoing_number(restored, "2026-11-22"),
            "Вих. № 0002/2026",
        )

    def test_tampered_sequence_fails_closed_before_number_reuse(self):
        register_incoming(
            self.root,
            registration_date="2026-11-22",
            correspondent="A",
            subject="One",
        )
        path = (
            self.root / "Data" / "Correspondence" / "registry.json"
        )
        data = json.loads(path.read_text("utf-8"))
        data["sequences"][0]["next_number"] = 1
        path.write_text(
            json.dumps(data, ensure_ascii=False),
            encoding="utf-8",
        )
        with self.assertRaises(ValueError):
            read_registry(self.root)
        with self.assertRaises(ValueError):
            register_incoming(
                self.root,
                registration_date="2026-11-22",
                correspondent="B",
                subject="Two",
            )

    def test_parallel_registration_never_reuses_number(self):
        def add(index):
            return register_incoming(
                self.root,
                registration_date="2026-11-22",
                correspondent="C%d" % index,
                subject="S%d" % index,
            )

        with ThreadPoolExecutor(max_workers=6) as pool:
            records = list(pool.map(add, range(18)))

        numbers = sorted(row.sequence_number for row in records)
        self.assertEqual(numbers, list(range(1, 19)))
        self.assertEqual(len({
            row.registration_number for row in records
        }), 18)
        self.assertEqual(
            next_incoming_number(self.root, "2026-11-22"),
            "Вх. № 0019/2026",
        )

    def test_document_link_is_reference_only(self):
        record = register_outgoing(
            self.root,
            registration_date="2026-11-22",
            correspondent="A",
            subject="Linked",
            document_ref="vault:vd-1234",
        )
        self.assertEqual(record.document_ref, "vault:vd-1234")
        root = self.root / "Data" / "Correspondence"
        self.assertEqual(
            sorted(path.name for path in root.iterdir()),
            ["registry.json"],
        )

    def test_unknown_related_id_and_bad_document_ref_fail(self):
        with self.assertRaises(ValueError):
            register_incoming(
                self.root,
                registration_date="2026-11-22",
                correspondent="A",
                subject="Bad relation",
                related_ids=("cr-" + "1" * 32,),
            )
        with self.assertRaises(ValueError):
            register_outgoing(
                self.root,
                registration_date="2026-11-22",
                correspondent="A",
                subject="Bad document",
                document_ref="../../outside.docx",
            )


if __name__ == "__main__":
    unittest.main()
