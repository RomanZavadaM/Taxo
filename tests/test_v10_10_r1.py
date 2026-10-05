# -*- coding: utf-8 -*-
"""Taxo 10.10-r1 — PyMuPDF removed; permissive PDF engine; license gate.

PROJECT_RULES.md §17: Taxo is proprietary, therefore runtime dependencies and
executable packages may contain only permissively licensed libraries.
PyMuPDF (AGPL-3.0 / Artifex commercial) is banned permanently.
"""
import datetime
import importlib.metadata as metadata
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "taxo"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from release_naming import version_from_file  # noqa: E402
from pdf_test_utils import open_pdf  # noqa: E402

BANNED_IMPORT = re.compile(r"^\s*(?:import|from)\s+(?:fitz|pymupdf)\b", re.M | re.I)
BANNED_REQUIREMENT = re.compile(r"^\s*(?:pymupdf|fitz)\b", re.M | re.I)
BANNED_HIDDEN_IMPORT = re.compile(r"""['"](?:fitz|pymupdf)['"]""", re.I)
FORBIDDEN_LICENSE = re.compile(r"\b(?:AGPL|SSPL|Affero)\b|(?<!L)GPL", re.I)


def _license_text(dist):
    md = dist.metadata
    parts = [md.get("License-Expression") or "", (md.get("License") or "").splitlines()[0] if md.get("License") else ""]
    parts += [c for c in (md.get_all("Classifier") or []) if c.startswith("License ::")]
    return " | ".join(p for p in parts if p)


def _requirement_names(path):
    names = []
    for line in path.read_text("utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith("-r"):
            continue
        names.append(re.split(r"[=<>!~;\s\[]", line, 1)[0])
    return names


class TestRevision(unittest.TestCase):
    def test_version_is_10_10_r1_or_later(self):
        version = version_from_file(ROOT / "VERSION.txt")
        match = re.fullmatch(r"10\.(\d+)(?:-r(\d+))?", version)
        self.assertIsNotNone(match, version)
        revision = int(match.group(2)) if match.group(2) else 999  # stable promotion
        self.assertGreaterEqual((int(match.group(1)), revision), (10, 1))
        self.assertIn(f'APP_VERSION = "{version}"', (ROOT / "main.py").read_text("utf-8"))
        self.assertIn(f"Taxo {version}", (ROOT / "START.bat").read_text("utf-8"))


class TestPyMuPDFBanned(unittest.TestCase):
    def test_no_pymupdf_imports_in_runtime_or_tests(self):
        files = [ROOT / "main.py", ROOT / "taxo_app.py", ROOT / "sitecustomize.py"]
        files += sorted(SRC.glob("*.py")) + sorted((ROOT / "tests").glob("*.py"))
        offenders = [str(p.relative_to(ROOT)) for p in files
                     if p.is_file() and BANNED_IMPORT.search(p.read_text("utf-8"))]
        self.assertEqual(offenders, [])

    def test_no_pymupdf_in_requirements(self):
        for path in sorted(ROOT.glob("requirements*.txt")):
            self.assertIsNone(BANNED_REQUIREMENT.search(path.read_text("utf-8")), path.name)

    def test_no_pymupdf_in_active_packaging(self):
        for path in sorted((ROOT / "packaging").glob("*.spec")):
            text = path.read_text("utf-8")
            self.assertIsNone(BANNED_HIDDEN_IMPORT.search(text), path.name)
            self.assertIn("collect_dynamic_libs('pypdfium2_raw')", text, path.name)
            self.assertIn("'pdf_engine'", text, path.name)

    def test_permissive_pdf_engine_declared(self):
        main_req = (ROOT / "requirements.txt").read_text("utf-8")
        win7_req = (ROOT / "requirements-win7.txt").read_text("utf-8")
        for text in (main_req, win7_req):
            self.assertIn("pypdfium2==", text)
            self.assertIn("pypdf==", text)
        notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text("utf-8")
        self.assertNotIn("PyMuPDF", notices)
        self.assertIn("pypdfium2", notices)
        self.assertIn("pypdf", notices)

    def test_project_rules_record_the_ban(self):
        rules = (ROOT / "PROJECT_RULES.md").read_text("utf-8")
        self.assertIn("Ліцензії сторонніх залежностей", rules)
        self.assertIn("PyMuPDF / `fitz` / `pymupdf` заборонений назавжди", rules)


class TestDependencyLicenses(unittest.TestCase):
    def test_installed_runtime_dependencies_are_not_copyleft(self):
        checked = 0
        offenders = []
        for name in _requirement_names(ROOT / "requirements.txt"):
            try:
                dist = metadata.distribution(name)
            except metadata.PackageNotFoundError:
                continue  # platform-specific requirement (e.g. pywin32 on Linux)
            checked += 1
            text = _license_text(dist)
            if FORBIDDEN_LICENSE.search(text):
                offenders.append(f"{name}: {text}")
        self.assertGreater(checked, 0)
        self.assertEqual(offenders, [])


def _context(**overrides):
    ctx = dict(
        company_name="ТОВ «Тест»", company_address="м. Львів, вул. Городоцька, 1",
        phone="+380 32 000 00 00", fax="+380 32 000 00 01", email="office@example.ua",
        signer_name="Іваненко Петро", signer_position="Директор",
        driver_full="Шевченко Тарас Григорович", birth_date="09.03.1984",
        period_from="01.10.2026 08:00", period_to="03.10.2026 18:30",
        company_name_en="LLC Test", company_address_en="Lviv, Horodotska 1",
        signer_name_en="Ivanenko Petro", signer_position_en="Director",
        driver_full_en="Shevchenko Taras", license_number_en="AAB 123456",
        employment="15.04.2019", license_series="ААВ", license_number="123456",
        license_issue_date="12.12.2015", director_place="Львів",
        director_place_en="Lviv", form_date="05.10.2026", activity_no=15,
    )
    ctx.update(overrides)
    return ctx


class TestAttestationWithoutPyMuPDF(unittest.TestCase):
    TEMPLATE = ROOT / "assets" / "attestation_visual_template.pdf"

    def test_form_pdf_and_jpg_are_built_by_permissive_engine(self):
        import attestation_render as ar

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "form.pdf"
            ar.build_attestation_pdf(_context(), out, self.TEMPLATE)
            with open_pdf(out) as doc:
                self.assertEqual(doc.page_count, 2)
                text = "\n".join(page.get_text() for page in doc)
                self.assertFalse(any(page.get_images(full=True) for page in doc))
            for value in ("Шевченко Тарас Григорович", "ТОВ «Тест»", "05.10.2026", "Shevchenko Taras"):
                self.assertIn(value, text)
            p1, p2 = ar.pdf_to_jpg_pages(out, Path(tmp) / "p1.jpg", Path(tmp) / "p2.jpg", dpi=72)
            from PIL import Image

            for path in (p1, p2):
                with Image.open(path) as image:
                    self.assertEqual(image.format, "JPEG")
                    self.assertGreater(image.width, 500)

    def test_default_template_resolves_in_structured_layout(self):
        import attestation_render as ar

        with tempfile.TemporaryDirectory() as tmp:
            out = ar.build_attestation_pdf(_context(activity_no=19), Path(tmp) / "f.pdf")
            self.assertTrue(Path(out).is_file())

    def test_long_values_shrink_but_stay_bounded(self):
        import attestation_render as ar
        from pdf_engine import register_ttf

        regular, _bold = ar._find_visual_font_files()
        font = register_ttf(regular, "TaxoAttReg")
        size = ar._fit_font_size(font, "Дуже довге значення " * 20, 300)
        self.assertEqual(size, 8.7)
        self.assertEqual(ar._fit_font_size(font, "Коротко", 300), ar._VISUAL_BASE_FONT_SIZE)


class TestWorkAnalysisDateStamp(unittest.TestCase):
    def test_formation_date_is_stamped_on_every_page(self):
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.pdfgen import canvas
        import v9_release

        class Core:
            @staticmethod
            def report_font_candidates():
                import attestation_render as ar

                return [str(ar._find_visual_font_files()[0])]

        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "r340.pdf"
            c = canvas.Canvas(str(pdf), pagesize=A4)
            c.drawString(72, 700, "page one")
            c.showPage()
            c.setPageSize(landscape(A4))
            c.drawString(72, 500, "page two")
            c.showPage()
            c.save()
            v9_release.stamp_work_analysis_pdf(Core, pdf, datetime.date(2026, 10, 5))
            with open_pdf(pdf) as doc:
                self.assertEqual(doc.page_count, 2)
                for page in doc:
                    self.assertIn("Дата формування: 05.10.2026", page.get_text())
            self.assertEqual(list(Path(tmp).glob("*.taxo-tmp")), [])


class TestDocumentViewerEngine(unittest.TestCase):
    def test_pdf_engine_renders_pages(self):
        from pdf_engine import PdfDocument

        template = ROOT / "assets" / "attestation_visual_template.pdf"
        with PdfDocument(template) as doc:
            self.assertEqual(len(doc), 2)
            width, height = doc.page_size(0)
            self.assertAlmostEqual(width, 595.3, places=0)
            image = doc.render(0, 0.5)
            self.assertEqual(image.mode, "RGB")
            self.assertAlmostEqual(image.width, round(width * 0.5), delta=1)

    def test_viewer_falls_back_to_system_viewer_when_engine_unavailable(self):
        import document_viewer
        from pdf_engine import PdfEngineUnavailable

        opened = []
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "doc.pdf"
            target.write_bytes((ROOT / "assets" / "attestation_visual_template.pdf").read_bytes())
            parent = mock.Mock()
            parent.tk = object()
            with mock.patch.object(document_viewer, "RasterDocumentWindow",
                                   side_effect=PdfEngineUnavailable("no engine")), \
                    mock.patch.object(document_viewer.messagebox, "showinfo") as info:
                document_viewer.open_document(parent, target, external_opener=opened.append)
            info.assert_called_once()
        self.assertEqual(opened, [target])


if __name__ == "__main__":
    unittest.main()
