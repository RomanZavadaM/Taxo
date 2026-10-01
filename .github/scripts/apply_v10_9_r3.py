from pathlib import Path

root = Path(__file__).resolve().parents[2]

# Version identity.
(root / "VERSION.txt").write_text("Version: 10.9-r3\n", encoding="utf-8")

p = root / "main.py"
s = p.read_text(encoding="utf-8")
s = s.replace('APP_VERSION = "10.9-r2"', 'APP_VERSION = "10.9-r3"', 1)
s = s.replace(
    "    vehicle_document_warning_lines,\n",
    "    vehicle_document_warning_lines,\n    vehicle_document_warning_lines_for_period,\n",
    1,
)
old = '''        document_warnings=vehicle_document_warning_lines(
            con,row["vehicle_id"],today=row["date"]
        )'''
new = '''        document_warnings=vehicle_document_warning_lines_for_period(
            con,row["vehicle_id"],row["date"],row["end_date"]
        )'''
if old not in s:
    raise SystemExit("waybill document warning call anchor not found")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")

p = root / "vehicle_documents.py"
s = p.read_text(encoding="utf-8")
marker = "\ndef control_rows(con, active_only=True, today=None):\n"
if marker not in s:
    raise SystemExit("vehicle_documents insertion anchor not found")
addition = r'''

def _required_document_types(con, vehicle_id):
    vehicle = con.execute(
        "SELECT temporary_registration_required FROM vehicles WHERE id=?",
        (int(vehicle_id),),
    ).fetchone()
    temporary_required = bool(
        vehicle and int(vehicle["temporary_registration_required"] or 0)
    )
    required = [
        "insurance",
        "inspection",
        "registration_certificate",
        "tachograph_inspection_protocol",
    ]
    if temporary_required:
        required.append("temporary_registration")
    return required


def _document_validity_interval(row, doc_type):
    """Return an inclusive validity interval, or None for an unusable record.

    Older Taxo records may have an empty valid_from because that field was
    historically optional. For compatibility an empty start is treated as
    unknown/unbounded in operational checks. Expiry-controlled documents
    without valid_until never provide valid coverage.
    """
    try:
        start = parse_date(row["valid_from"]) if str(row["valid_from"] or "").strip() else date.min
        if str(row["valid_until"] or "").strip():
            end = parse_date(row["valid_until"])
        elif doc_type in EXPIRY_REQUIRED:
            return None
        else:
            end = date.max
    except ValueError:
        return None
    if end < start:
        return None
    return start, end


def document_coverage_for_period(con, vehicle_id, doc_type, period_start, period_end):
    """Check continuous active-document coverage for an inclusive trip period."""
    start = period_start if isinstance(period_start, date) else parse_date(period_start)
    end = period_end if isinstance(period_end, date) else parse_date(period_end)
    if start is None or end is None:
        raise ValueError("Період рейсу має містити дату початку і завершення.")
    if end < start:
        raise ValueError("Дата завершення рейсу не може бути раніше дати початку.")

    rows = active_documents_of_type(con, vehicle_id, doc_type)
    intervals = []
    for row in rows:
        interval = _document_validity_interval(row, doc_type)
        if interval is None:
            continue
        valid_from, valid_until = interval
        if valid_until < start or valid_from > end:
            continue
        intervals.append((valid_from, valid_until, row))
    intervals.sort(key=lambda item: (item[0], item[1], int(item[2]["id"])))

    cursor = start
    used = []
    for valid_from, valid_until, row in intervals:
        if valid_until < cursor:
            continue
        if valid_from > cursor:
            break
        used.append(row)
        if valid_until >= end:
            status = document_status(doc_type, row["valid_until"], today=start)
            return True, row, status, used
        cursor = date.fromordinal(valid_until.toordinal() + 1)

    chosen = used[-1] if used else (intervals[0][2] if intervals else None)
    return False, chosen, "Не діє весь рейс", used


def vehicle_document_summary_for_period(con, vehicle_id, period_start, period_end):
    """Required vehicle-document state for the complete trip period."""
    start = period_start if isinstance(period_start, date) else parse_date(period_start)
    end = period_end if isinstance(period_end, date) else parse_date(period_end)
    details = []
    for dtype in _required_document_types(con, vehicle_id):
        covered, row, status, _used = document_coverage_for_period(
            con, vehicle_id, dtype, start, end
        )
        if row is None:
            status = "Відсутній"
        elif not covered:
            status = "Не діє весь рейс"
        details.append((dtype, DOCUMENT_TYPES[dtype], row, status))

    worst = min((status_rank(item[3]) for item in details), default=3)
    overall = "Проблема" if worst <= 1 else ("Увага" if worst == 2 else "Актуально")
    return overall, details


def vehicle_document_warning_lines_for_period(con, vehicle_id, period_start, period_end):
    """Operational warnings using the full planned trip date range."""
    start = period_start if isinstance(period_start, date) else parse_date(period_start)
    end = period_end if isinstance(period_end, date) else parse_date(period_end)
    _overall, details = vehicle_document_summary_for_period(con, vehicle_id, start, end)
    warnings = []
    for _dtype, label, row, status in details:
        if status_rank(status) >= 3:
            continue
        meta = []
        if row is not None and str(row["document_no"] or "").strip():
            meta.append(f"№ {row['document_no']}")
        if row is not None and str(row["valid_from"] or "").strip():
            meta.append(f"з {display_date(row['valid_from'])}")
        if row is not None and str(row["valid_until"] or "").strip():
            meta.append(f"до {display_date(row['valid_until'])}")
        meta.append(f"рейс {start.strftime('%d.%m.%Y')}–{end.strftime('%d.%m.%Y')}")
        warnings.append(f"{label}: {status} ({', '.join(meta)})")
    return warnings
'''
s = s.replace(marker, addition + marker, 1)
p.write_text(s, encoding="utf-8")

(root / "vehicle_document_validity.py").write_text(
    '''# -*- coding: utf-8 -*-
"""Taxo 10.9-r3 runtime marker for full-trip vehicle document validity."""
APP_VERSION = "10.9-r3"


def install(core, base_app):
    core.APP_VERSION = APP_VERSION
    return base_app
''',
    encoding="utf-8",
)

p = root / "feature_layers.py"
s = p.read_text(encoding="utf-8")
s = s.replace(
    "from waybill_integrity import install as install_waybill_integrity\n",
    "from waybill_integrity import install as install_waybill_integrity\nfrom vehicle_document_validity import install as install_vehicle_document_validity\n",
    1,
)
s = s.replace(
    '    FeatureLayer("v1092-waybill-integrity", install_waybill_integrity, domain="waybills"),\n)',
    '    FeatureLayer("v1092-waybill-integrity", install_waybill_integrity, domain="waybills"),\n    FeatureLayer("v1093-vehicle-document-validity", install_vehicle_document_validity, domain="vehicles"),\n)',
    1,
)
p.write_text(s, encoding="utf-8")

p = root / "START.bat"
text = p.read_bytes().decode("ascii")
anchor = 'if not exist "waybill_integrity.py" goto :package_incomplete\r\n'
if anchor not in text:
    raise SystemExit("START.bat guard anchor not found")
text = text.replace(anchor, anchor + 'if not exist "vehicle_document_validity.py" goto :package_incomplete\r\n', 1)
p.write_bytes(text.encode("ascii"))

p = root / ".github/workflows/source-test-archive.yml"
s = p.read_text(encoding="utf-8")
anchor = "  waybill_integrity.py\n"
if anchor not in s:
    raise SystemExit("source package required-file anchor not found")
s = s.replace(anchor, anchor + "  vehicle_document_validity.py\n", 1)
p.write_text(s, encoding="utf-8")

(root / "tests/test_v10_9_r3.py").write_text(r'''import sqlite3
import unittest
from datetime import date
from pathlib import Path

import feature_layers
import vehicle_documents as docs

ROOT = Path(__file__).resolve().parents[1]


class VehicleDocumentValidityR3Tests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.execute("CREATE TABLE vehicles(id INTEGER PRIMARY KEY, temporary_registration_required INTEGER DEFAULT 0)")
        self.con.execute("INSERT INTO vehicles(id,temporary_registration_required) VALUES(1,0)")
        docs.ensure_vehicle_documents_schema(self.con)

    def tearDown(self):
        self.con.close()

    def add(self, dtype, valid_from="", valid_until="", archived=0, number="X"):
        self.con.execute(
            """INSERT INTO vehicle_documents(
                vehicle_id,doc_type,document_no,issuer,valid_from,valid_until,
                copy_path,notes,archived,created_at,updated_at
            ) VALUES(1,?,?,?,?,?,'','',?,'2026-01-01T00:00:00','2026-01-01T00:00:00')""",
            (dtype, number, "", valid_from, valid_until, archived),
        )
        self.con.commit()

    def test_valid_from_is_honoured_for_trip_start(self):
        self.add("insurance", "2026-10-03", "2027-10-03")
        covered, _row, status, _used = docs.document_coverage_for_period(
            self.con, 1, "insurance", date(2026, 10, 1), date(2026, 10, 2)
        )
        self.assertFalse(covered)
        self.assertEqual(status, "Не діє весь рейс")

    def test_expiry_before_trip_end_is_problem(self):
        self.add("inspection", "2026-01-01", "2026-10-01")
        covered, _row, status, _used = docs.document_coverage_for_period(
            self.con, 1, "inspection", date(2026, 10, 1), date(2026, 10, 2)
        )
        self.assertFalse(covered)
        self.assertEqual(status, "Не діє весь рейс")

    def test_multiple_active_same_type_documents_can_jointly_cover_trip(self):
        self.add("insurance", "2026-01-01", "2026-10-01", number="A")
        self.add("insurance", "2026-10-02", "2027-10-02", number="B")
        covered, row, _status, used = docs.document_coverage_for_period(
            self.con, 1, "insurance", date(2026, 10, 1), date(2026, 10, 3)
        )
        self.assertTrue(covered)
        self.assertEqual(row["document_no"], "B")
        self.assertEqual([r["document_no"] for r in used], ["A", "B"])

    def test_archived_document_does_not_cover_new_trip(self):
        self.add("insurance", "2026-01-01", "2027-01-01", archived=1)
        covered, row, _status, _used = docs.document_coverage_for_period(
            self.con, 1, "insurance", date(2026, 10, 1), date(2026, 10, 1)
        )
        self.assertFalse(covered)
        self.assertIsNone(row)

    def test_temporary_registration_is_required_only_when_marked(self):
        self.assertNotIn("temporary_registration", docs._required_document_types(self.con, 1))
        self.con.execute("UPDATE vehicles SET temporary_registration_required=1 WHERE id=1")
        self.con.commit()
        self.assertIn("temporary_registration", docs._required_document_types(self.con, 1))

    def test_waybill_checks_complete_trip_range(self):
        source = (ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn("vehicle_document_warning_lines_for_period", source)
        self.assertIn('con,row["vehicle_id"],row["date"],row["end_date"]', source)

    def test_r3_is_outermost_and_r2_is_preserved(self):
        ids = feature_layers.feature_layer_ids()
        self.assertIn("v1092-waybill-integrity", ids)
        self.assertEqual(ids[-1], "v1093-vehicle-document-validity")
        self.assertEqual((ROOT / "VERSION.txt").read_text(encoding="utf-8").strip(), "Version: 10.9-r3")


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")

(root / "docs/maintenance/AUDIT_VEHICLE_DOCUMENT_VALIDITY_v10.9-r3.md").write_text(
    """# AUDIT — Vehicle document validity, Taxo 10.9-r3

## Мета
Закрити наступний підтверджений пункт зовнішнього аудиту: строки дії документів ТЗ мають перевірятися не лише на дату виїзду, а на **весь плановий період рейсу**.

## Реалізація
- існуюче поле `valid_from` тепер реально бере участь в оперативній перевірці;
- `valid_until` контролюється до дати завершення рейсу;
- кілька активних документів одного типу можуть разом безперервно перекривати багатоденний рейс;
- архівні документи не підставляються для нового рейсу;
- старі записи без `valid_from` не ламаються: порожня дата початку трактується як невідома/необмежена лише для backward compatibility;
- тимчасовий реєстраційний документ лишається додатковою вимогою тільки для ТЗ, де це явно позначено;
- ДЦВ лишається необов'язковим документом;
- автоматичне архівування документів не повертається.

## Межі
Ця ревізія не змінює тахограф, відпочинок, П-5, СТОІР, накази або правила план/факт.
""",
    encoding="utf-8",
)
(root / "docs/releases/RELEASE_NOTES_v10.9-r3.md").write_text(
    """# Taxo 10.9-r3 — контроль документів ТЗ на весь рейс

- контроль обов'язкових документів ТЗ тепер використовує дату початку **і дату завершення** рейсу;
- враховано `valid_from`, тому документ, який набуде чинності пізніше, не вважається чинним на початку рейсу;
- документ, строк якого спливає до завершення рейсу, позначається проблемним;
- кілька активних документів одного типу можуть безперервно перекрити період рейсу;
- збережено ручне архівування і можливість мати кілька документів одного типу;
- додано поведінкові SQLite-тести.

Stable `v10.3` цією fast-test ревізією не змінюється. Злиття в `main` — тільки за окремою командою власника.
""",
    encoding="utf-8",
)
