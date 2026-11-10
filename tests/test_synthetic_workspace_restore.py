# -*- coding: utf-8 -*-
"""Isolated end-to-end workspace backup with synthetic linked Taxo records."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Executed in a fresh process whose Taxo workspace/config variables are set
# before importing the application. The existing owner scenario creates an
# actual order with 12 driver/vehicle pairs and renders DOCX/PDF/JPG.
FOLLOWUP = r'''
import sqlite3
import zipfile
from datetime import date
from pathlib import Path
from docx import Document
from pypdf import PdfReader
import paper_documents as paper
import safety_instructions_ui as brief
import tachograph
import workspace

root = Path(main.DATA_ROOT)
paths = workspace.paths_for(root)
con = main.db()
con.execute(
    "INSERT INTO employee_time_entries(employee_id,work_date,day_type,planned_hours,actual_hours,notes,created_at) VALUES(101,?,'Робота',8.0,9.5,?,?)",
    ("2026-11-10", "Тест план і факт", now),
)
con.commit()
order_id = oid
before_pairs = ops.vehicle_assignment_pairs(con, order_id)
con.close()

tachograph.init_tacho_db()
tcon = tachograph.tdb()
tcon.execute(
    "INSERT INTO discs(source_path,scan_name,driver_id,vehicle_id,disc_date,created_at) VALUES(?,?,?,?,?,?)",
    ("workspace://Data/TachographScans/scan-test.jpg", "scan-test.jpg", 101, 201, "2026-11-10", now),
)
tcon.commit()
tcon.close()

samples = {
    "Data/EmployeeDocuments/test-employee.pdf": b"synthetic employee document",
    "Data/VehicleDocuments/test-vehicle.pdf": b"synthetic vehicle document",
    "Data/TachographScans/scan-test.jpg": b"synthetic tachograph scan",
}
for relative, payload in samples.items():
    dest = root / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(payload)

prepared = brief.prepare_list(
    "БДР", "Передрейсовий (цільовий)", "10.11.2026", "Тест безпечного руху",
    ["Водій01 Тестовий", "Водій02 Тестовий"],
    people_records=(
        {"id": 101, "name": "Водій01 Тестовий", "personnel_no": "D001"},
        {"id": 102, "name": "Водій02 Тестовий", "personnel_no": "D002"},
    ),
    program_text="Тестова програма безпечного руху.",
)
brief_path = paper.save_document(root, paper.build_briefing_docx(prepared),
    "Інструктаж", "Тест безпечного руху", "2026-11-10", "Водій01 Тестовий")
training_path = paper.save_document(root, paper.build_training_docx({
    "driver": "Водій01 Тестовий", "instructor": "Водій02 Тестовий",
    "vehicle": "MODEL-01 BC1001AA",
}), "Стажування", "Тестове стажування", "2026-11-10", "Водій01 Тестовий")

folder = root.parent
archive = workspace.create_workspace_backup_archive(
    root, folder / "synthetic-full.zip", app_version=main.APP_VERSION,
    include_vehicle_documents=True, include_tacho_scans=True, include_output=True)
manifest = workspace.validate_workspace_backup_archive(archive)
assert all(manifest["includes"][key] for key in (
    "databases", "employee_documents", "vehicle_documents", "tachograph_scans", "output"))
assert set(manifest["excludes"]) >= {"Backups", "Logs"}

restored = folder / "restored"
restored_paths = workspace.restore_workspace_backup_archive(archive, restored)
con = sqlite3.connect(str(restored_paths["main_db"]))
con.row_factory = sqlite3.Row
assert con.execute("PRAGMA quick_check").fetchone()[0] == "ok"
assert con.execute("SELECT count(*) FROM employees WHERE id BETWEEN 101 AND 112").fetchone()[0] == 12
assert con.execute("SELECT count(*) FROM vehicles WHERE id BETWEEN 201 AND 212").fetchone()[0] == 12
row = con.execute("SELECT planned_hours,actual_hours,notes FROM employee_time_entries WHERE employee_id=101 AND work_date='2026-11-10'").fetchone()
assert tuple(row) == (8.0, 9.5, "Тест план і факт"), tuple(row)
assert ops.vehicle_assignment_pairs(con, order_id) == before_pairs
con.close()
tcon = sqlite3.connect(str(restored_paths["tacho_db"]))
assert tcon.execute("PRAGMA quick_check").fetchone()[0] == "ok"
assert tcon.execute("SELECT scan_name,driver_id,vehicle_id FROM discs").fetchone() == ("scan-test.jpg", 101, 201)
tcon.close()
for relative, payload in samples.items():
    assert (restored / relative).read_bytes() == payload, relative
records = paper.list_documents(restored)
assert len(records) == 2
assert {r["kind"] for r in records} == {"Інструктаж", "Стажування"}
for rec in records:
    actual = paper.document_path(restored, rec)
    original = root / actual.relative_to(restored)
    assert actual.read_bytes() == original.read_bytes()
    text = "\n".join(
        [p.text for p in Document(str(actual)).paragraphs] +
        [cell.text for table in Document(str(actual)).tables for r in table.rows for cell in r.cells]
    )
    assert "Водій01 Тестовий" in text
    if rec["kind"] == "Інструктаж":
        assert "Тестова програма безпечного руху." in text
        assert "Водій02 Тестовий" in text

source_output = Path(main.OUTPUT_DIR)
for source_file in source_output.glob("Наказ_*"):
    assert (restored / source_file.relative_to(root)).read_bytes() == source_file.read_bytes()
docx = next((restored / "Output").glob("Наказ_*.docx"))
pdf = next((restored / "Output").glob("Наказ_*.pdf"))
assert next((restored / "Output").glob("Наказ_*_сторінка_*.jpg")).stat().st_size > 1000
doc = Document(str(docx))
docx_text = "\n".join([p.text for p in doc.paragraphs] + [
    cell.text for table in doc.tables for r in table.rows for cell in r.cells])
pdf_text = "\n".join((p.extract_text() or "") for p in PdfReader(str(pdf)).pages)
for marker in ("MODEL-01", "BC1001AA", "Водій01 Тестовий", "MODEL-12", "BC1012AA"):
    assert marker in docx_text, marker
    assert marker in pdf_text, marker

# Refuse an occupied target and preserve its content.
occupied = folder / "occupied"
occupied.mkdir()
(occupied / "keep.txt").write_text("keep", encoding="utf-8")
try:
    workspace.restore_workspace_backup_archive(archive, occupied)
except ValueError:
    pass
else:
    raise AssertionError("nonempty destination was accepted")
assert (occupied / "keep.txt").read_text(encoding="utf-8") == "keep"

# Verify optional groups are excluded when not explicitly selected.
small = workspace.create_workspace_backup_archive(root, folder / "selected.zip")
with zipfile.ZipFile(small) as zf:
    names = set(zf.namelist())
assert "Data/EmployeeDocuments/test-employee.pdf" in names
assert "Data/PaperDocuments/" + brief_path.name in names
for relative in ("Data/VehicleDocuments/test-vehicle.pdf", "Data/TachographScans/scan-test.jpg"):
    assert relative not in names
assert not any(name.startswith("Output/") for name in names)

broken = folder / "broken.zip"
broken.write_bytes(b"not a zip archive")
try:
    workspace.restore_workspace_backup_archive(broken, folder / "broken-restore")
except (ValueError, zipfile.BadZipFile):
    pass
else:
    raise AssertionError("invalid archive was accepted")
print("SYNTHETIC_WORKSPACE_RESTORE_OK")
'''


class SyntheticWorkspaceRestoreTests(unittest.TestCase):
    def test_order_documents_schedule_and_selected_attachments_survive_restore(self):
        with tempfile.TemporaryDirectory(prefix="taxo_backup_e2e_") as td:
            env = os.environ.copy()
            env["TAXO_WORKSPACE_ROOT"] = str(Path(td) / "workspace")
            env["TAXO_CONFIG_DIR"] = str(Path(td) / "config")
            Path(env["TAXO_CONFIG_DIR"]).mkdir()
            env["PYTHONPATH"] = os.pathsep.join(
                (str(ROOT / "src" / "taxo"), str(ROOT), env.get("PYTHONPATH", "")))
            owner = (ROOT / "tests" / "_r15_owner_child.py").read_text("utf-8")
            result = subprocess.run(
                [sys.executable, "-c", owner + "\n" + FOLLOWUP],
                cwd=str(ROOT), env=env, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, timeout=180)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("SYNTHETIC_WORKSPACE_RESTORE_OK", result.stdout)
