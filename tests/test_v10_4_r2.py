# -*- coding: utf-8 -*-
import inspect
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

import main
import personnel_v91
import vehicle_documents
import waybill
from release_naming import start_archive_stem, version_from_file

ROOT=Path(__file__).resolve().parents[1]


class TestTaxo104R2UiDocsWaybill(unittest.TestCase):
    def test_r2_checkpoint_stays_immutable_after_later_revisions(self):
        self.assertEqual(main.APP_VERSION,version_from_file(ROOT/"VERSION.txt"))
        self.assertEqual(start_archive_stem("10.4-r2"),"Taxo_v10_4_candidate_r2_START")

    def test_additional_liability_insurance_is_optional(self):
        self.assertEqual(
            vehicle_documents.DOCUMENT_TYPES["additional_liability_insurance"],
            "ДЦВ страхування",
        )
        self.assertNotIn("additional_liability_insurance",vehicle_documents.EXPIRY_REQUIRED)
        self.assertEqual(
            vehicle_documents.document_status("additional_liability_insurance","",today=date(2026,9,26)),
            "Актуальний",
        )

    def test_multiple_same_type_documents_can_coexist(self):
        con=sqlite3.connect(":memory:")
        con.row_factory=sqlite3.Row
        con.executescript("""
            CREATE TABLE vehicles(id INTEGER PRIMARY KEY, temporary_registration_required INTEGER DEFAULT 0);
            INSERT INTO vehicles(id,temporary_registration_required) VALUES(1,1);
        """)
        vehicle_documents.ensure_vehicle_documents_schema(con)
        now="2026-09-26T12:00:00"
        for no,until in (("ТАЛОН-1","2026-12-31"),("ТАЛОН-2","2027-02-01")):
            con.execute("""INSERT INTO vehicle_documents(
                vehicle_id,doc_type,document_no,issuer,valid_from,valid_until,copy_path,notes,archived,created_at,updated_at
            ) VALUES(1,'temporary_registration',?,'','2026-09-01',?,'','',0,?,?)""",(no,until,now,now))
        con.commit()
        active=vehicle_documents.active_documents_of_type(con,1,"temporary_registration")
        self.assertEqual(len(active),2)
        self.assertEqual(vehicle_documents.best_current_document(con,1,"temporary_registration",date(2026,9,26))["document_no"],"ТАЛОН-2")
        con.close()

    def test_archive_is_explicit_not_save_side_effect(self):
        source=inspect.getsource(vehicle_documents.VehicleDocumentsWindow._form)
        self.assertIn("archive_previous = tk.BooleanVar(value=False)",source)
        self.assertIn("Вивести інші активні документи цього типу в архів",source)
        self.assertIn("if archive_previous.get():",source)

    def test_waybill_inserted_data_scale_and_corner_stamp(self):
        self.assertEqual(waybill.DATA_FONT_SCALE,1.20)
        source=inspect.getsource(waybill)
        self.assertIn("def _corner_stamp",source)
        self.assertIn('data.get("company_address"',source)
        self.assertIn('data.get("company_phone"',source)
        self.assertIn('data.get("company_email"',source)
        main_source=inspect.getsource(main.App)
        self.assertIn('"company_address":company["address"] if company else ""',main_source)

    def test_ui_remediation_markers(self):
        source=inspect.getsource(main.App)
        personnel=inspect.getsource(personnel_v91)
        viewer=(ROOT/"document_viewer.py").read_text("utf-8")
        self.assertIn('compact_shell = (',source)
        self.assertIn('row=7,column=0,columnspan=2',source)
        self.assertIn('<Button-4>',source)
        self.assertIn('_make_scrollable_tab_body(reports, "personnel_reports")',personnel)
        self.assertIn('orient="horizontal",command=tree.xview',personnel)
        self.assertIn('fit_window_to_screen(self.win, 1050, 780',viewer)

    def test_packaging_identities(self):
        win=(ROOT/"installer"/"Taxo_v10_4_r2.iss").read_text("utf-8")
        win7=(ROOT/"installer"/"Taxo_v10_4_r2_win7.iss").read_text("utf-8")
        mac=(ROOT/"Taxo_macos_v10_4_r2.spec").read_text("utf-8")
        self.assertIn('#define MyAppVersion "10.4-r2"',win)
        self.assertIn('Taxo_v10_4_candidate_r2_Setup_Windows_x64',win)
        self.assertIn('MinVersion=6.1sp1',win7)
        self.assertIn('Taxo_v10_4_candidate_r2_Setup_Windows7_x64',win7)
        self.assertIn("version='10.4.2'",mac)
        self.assertIn("'CFBundleVersion': '2'",mac)


if __name__=="__main__":
    unittest.main()
