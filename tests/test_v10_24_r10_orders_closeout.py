# -*- coding: utf-8 -*-
"""10.25-r1 prep: one isolated end-to-end gate for the full orders contour."""
import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from docx import Document

import operations_orders as ops
import workspace
from order_document_formats import build_order_docx, pdf_page_count, render_order_jpg_pages
from pdf_test_utils import open_pdf
from v1073_features import export_order_pdf_with_appendices


class OrdersCloseoutR10PrepTests(unittest.TestCase):
    def test_candidate_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / "VERSION.txt").read_text("utf-8"), "Version: 10.25-r1\n")
        self.assertIn('APP_VERSION = "10.25-r1"', (root / "main.py").read_text("utf-8"))
        self.assertIn("Taxo 10.25-r1 - START", (root / "START.bat").read_text("utf-8"))
        self.assertEqual((root / ".release" / "full-current").read_text("utf-8"), "10.25-r1\n")
        self.assertEqual((root / ".release" / "stable-current").read_text("utf-8"), "10.24-r9\n")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="taxo_r10_orders_")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"
        self.paths = workspace.ensure_workspace(self.root)
        con = self.connect()
        con.executescript(
            """
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY,
                last_name TEXT, first_name TEXT, middle_name TEXT,
                position TEXT, personnel_no TEXT, rnokpp TEXT,
                active INTEGER DEFAULT 1, driver_id INTEGER
            );
            CREATE TABLE employee_roles (employee_id INTEGER, role TEXT);
            CREATE TABLE drivers (
                id INTEGER PRIMARY KEY, active INTEGER DEFAULT 1,
                driver_end_date TEXT DEFAULT ''
            );
            CREATE TABLE employee_military_profile (
                employee_id INTEGER PRIMARY KEY,
                registry_person_id TEXT DEFAULT ''
            );
            CREATE TABLE vehicles (
                id INTEGER PRIMARY KEY, name TEXT, plate TEXT,
                make_model TEXT, vin TEXT, garage_no TEXT,
                active INTEGER DEFAULT 1
            );

            INSERT INTO employees VALUES
                (1,'Ivanenko','Ivan','','Driver','001','1111111111',1,11),
                (2,'Petrenko','Petro','','Driver','002','2222222222',1,12),
                (3,'Sydorenko','Sydir','','Driver','003','3333333333',1,13);
            INSERT INTO employee_roles VALUES
                (1,'Driver'),(2,'Driver'),(3,'Driver');
            INSERT INTO drivers VALUES
                (11,1,''),(12,1,''),(13,1,'');
            INSERT INTO vehicles VALUES
                (10,'Bus 10','BC0010AA','MAN Lion','VIN000000000010','10',1),
                (20,'Bus 20','BC0020AA','Mercedes','VIN000000000020','20',1),
                (30,'Bus 30','BC0030AA','Volvo','VIN000000000030','30',1);
            """
        )
        ops.ensure_schema_on_connection(con)

        self.general_order_id = ops.create_order(
            con,
            order_type=ops.TYPE_OCCUPATIONAL_SAFETY,
            order_no="R10-GEN",
            order_date="27.11.2026",
            subject="Orders closeout general order",
            body_text="Synthetic end-to-end acceptance.",
        )
        created = ops.add_order_entities(
            con,
            self.general_order_id,
            ops.ORDER_ENTITY_EMPLOYEE,
            [1, 2],
            role="Participant",
            note="Initial",
        )
        self.assertEqual(len(created), 2)
        vehicle_link = ops.add_order_entity(
            con,
            self.general_order_id,
            ops.ORDER_ENTITY_VEHICLE,
            20,
            role="Vehicle",
            note="Synthetic",
        )
        employee_link = created[0]
        frozen_before = ops.get_order_entity(con, employee_link)["snapshot_json"]
        self.assertTrue(
            ops.update_order_entity_fields(
                con,
                employee_link,
                role="Responsible",
                note="Updated in r10 closeout",
            )
        )
        self.assertEqual(
            ops.get_order_entity(con, employee_link)["snapshot_json"],
            frozen_before,
        )
        ops.delete_order_entity(
            con,
            created[1],
            history_note="Synthetic remove before re-add",
        )
        readded = ops.add_order_entities(
            con,
            self.general_order_id,
            ops.ORDER_ENTITY_EMPLOYEE,
            [3],
            role="Participant",
            note="Re-added replacement",
        )
        self.assertEqual(len(readded), 1)
        self.assertIsNotNone(ops.get_order_entity(con, vehicle_link))

        self.assignment_order_id = ops.create_order(
            con,
            order_type=ops.TYPE_VEHICLE_ASSIGNMENT,
            order_no="R10-PAIR",
            order_date="27.11.2026",
            subject="Orders closeout vehicle assignment",
            body_text="Synthetic pair control.",
        )
        ops.add_vehicle_assignments_bulk(
            con,
            self.assignment_order_id,
            [(10, 1), (20, 2)],
            valid_from="27.11.2026",
            note="Initial pair set",
        )
        rows = list(ops.order_assignments(con, self.assignment_order_id))
        self.assertEqual(len(rows), 2)
        second = next(row for row in rows if int(row["vehicle_id"]) == 20)
        ops.update_vehicle_assignment(
            con,
            int(second["id"]),
            vehicle_id=30,
            employee_id=3,
            valid_from="27.11.2026",
            note="Edited pair",
            history_note="Synthetic r10 edit",
        )
        first = next(
            row for row in ops.order_assignments(con, self.assignment_order_id)
            if int(row["vehicle_id"]) == 10
        )
        ops.delete_vehicle_assignment(
            con,
            int(first["id"]),
            history_note="Synthetic r10 delete",
        )
        ops.add_vehicle_assignments_bulk(
            con,
            self.assignment_order_id,
            [(10, 1)],
            valid_from="27.11.2026",
            note="Re-added pair",
        )

        ops.approve_order(con, self.general_order_id)
        ops.approve_order(con, self.assignment_order_id)
        con.commit()
        con.close()

    def connect(self, root=None):
        target = workspace.paths_for(root or self.root)["main_db"]
        con = sqlite3.connect(str(target))
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        return con

    @staticmethod
    def sha256(path):
        digest = hashlib.sha256()
        with Path(path).open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def docx_text(path):
        doc = Document(str(path))
        return "\n".join(
            [paragraph.text for paragraph in doc.paragraphs]
            + [
                cell.text
                for table in doc.tables
                for row in table.rows
                for cell in row.cells
            ]
        )

    def _pdf_text(self, path):
        with open_pdf(path) as pdf:
            return "\n".join(page.get_text() for page in pdf)

    def test_orders_round_trip_from_db_to_documents_and_full_restore(self):
        # A true reopen: all source data must come from persisted SQLite.
        con = self.connect()
        try:
            general = ops.get_order(con, self.general_order_id)
            entities = tuple(ops.list_order_entities(con, self.general_order_id))
            assignment = ops.get_order(con, self.assignment_order_id)
            pairs = tuple(ops.order_assignments(con, self.assignment_order_id))
        finally:
            con.close()

        self.assertEqual(general["status"], ops.ORDER_APPROVED)
        self.assertEqual(assignment["status"], ops.ORDER_APPROVED)
        entity_text = "\n".join(
            "%s %s %s" % (
                row["entity_type"],
                row["role"] or "",
                row["snapshot_json"] or "",
            )
            for row in entities
        )
        self.assertIn("Responsible", entity_text)
        self.assertIn("Ivanenko", entity_text)
        self.assertIn("Sydorenko", entity_text)
        self.assertIn("BC0020AA", entity_text)

        final_pairs = {
            (int(row["vehicle_id"]), int(row["employee_id"]))
            for row in pairs
        }
        self.assertEqual(final_pairs, {(10, 1), (30, 3)})

        output = self.paths["output"] / "R10OrdersAcceptance"
        output.mkdir(parents=True, exist_ok=True)
        general_docx = output / "general.docx"
        general_pdf = output / "general.pdf"
        assignment_docx = output / "assignment.docx"
        assignment_pdf = output / "assignment.pdf"

        build_order_docx(
            general_docx,
            ops,
            general,
            entities=entities,
            company={"name": "Synthetic Company"},
        )

        class Core:
            def db(inner_self):
                return self.connect()

        export_order_pdf_with_appendices(
            Core(),
            general_pdf,
            general,
            assignments=(),
            company={"name": "Synthetic Company"},
        )

        build_order_docx(
            assignment_docx,
            ops,
            assignment,
            assignments=pairs,
            company={"name": "Synthetic Company"},
        )
        ops.export_order_pdf(
            assignment_pdf,
            assignment,
            assignments=pairs,
            company={"name": "Synthetic Company"},
        )

        general_docx_text = self.docx_text(general_docx)
        general_pdf_text = self._pdf_text(general_pdf)
        for marker in ("Ivanenko Ivan", "Sydorenko Sydir", "BC0020AA"):
            self.assertIn(marker, general_docx_text)
            self.assertIn(marker, general_pdf_text)

        assignment_docx_text = self.docx_text(assignment_docx)
        assignment_pdf_text = self._pdf_text(assignment_pdf)
        for marker in ("Ivanenko Ivan", "Sydorenko Sydir", "BC0010AA", "BC0030AA"):
            self.assertIn(marker, assignment_docx_text)
            self.assertIn(marker, assignment_pdf_text)

        generated = [general_docx, general_pdf, assignment_docx, assignment_pdf]
        for pdf in (general_pdf, assignment_pdf):
            pages = pdf_page_count(pdf)
            self.assertGreaterEqual(pages, 1)
            targets = [
                output / ("%s_page_%02d.jpg" % (pdf.stem, index))
                for index in range(1, pages + 1)
            ]
            render_order_jpg_pages(pdf, targets)
            generated.extend(targets)

        before_hashes = {
            str(path.relative_to(self.root)): self.sha256(path)
            for path in generated
        }

        archive = workspace.create_workspace_backup_archive(
            self.root,
            Path(self.temp.name) / "orders-r10-full.zip",
            app_version="10.25-r1",
            include_output=True,
        )
        manifest = workspace.validate_workspace_backup_archive(archive)
        self.assertTrue(manifest["includes"]["output"])

        restored = Path(self.temp.name) / "restored"
        workspace.restore_workspace_backup_archive(archive, restored)

        restored_con = self.connect(restored)
        try:
            restored_general = ops.get_order(restored_con, self.general_order_id)
            restored_entities = tuple(
                ops.list_order_entities(restored_con, self.general_order_id)
            )
            restored_assignment = ops.get_order(
                restored_con, self.assignment_order_id
            )
            restored_pairs = tuple(
                ops.order_assignments(restored_con, self.assignment_order_id)
            )
        finally:
            restored_con.close()

        self.assertEqual(dict(restored_general), dict(general))
        self.assertEqual(
            [dict(row) for row in restored_entities],
            [dict(row) for row in entities],
        )
        self.assertEqual(dict(restored_assignment), dict(assignment))
        self.assertEqual(
            [dict(row) for row in restored_pairs],
            [dict(row) for row in pairs],
        )

        for relative, expected_hash in before_hashes.items():
            restored_file = restored / relative
            self.assertTrue(restored_file.is_file(), relative)
            self.assertEqual(self.sha256(restored_file), expected_hash, relative)


if __name__ == "__main__":
    unittest.main()
