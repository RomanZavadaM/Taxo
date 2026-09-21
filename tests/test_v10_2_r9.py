# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

import main
from release_naming import start_archive_stem, version_from_file

ROOT = Path(__file__).resolve().parents[1]


class TestTaxo102R9LegalCommercialHardening(unittest.TestCase):
    def test_version_is_r9_everywhere(self):
        self.assertEqual(main.APP_VERSION, "10.2-r9")
        self.assertEqual(version_from_file(ROOT / "VERSION.txt"), "10.2-r9")
        self.assertEqual(
            start_archive_stem("10.2-r9"),
            "Taxo_v10_2_candidate_r9_START",
        )

    def test_pymupdf_is_not_runtime_or_build_dependency(self):
        names = (
            "requirements.txt",
            "document_viewer.py",
            "attestation_render.py",
            "Taxo.spec",
            "Taxo_macos.spec",
        )
        text = "\n".join((ROOT / name).read_text("utf-8") for name in names).lower()
        self.assertNotIn("pymupdf", text)
        self.assertNotIn("import fitz", text)

    def test_pdf_preview_external_generation_preserved(self):
        viewer = (ROOT / "document_viewer.py").read_text("utf-8")
        renderer = (ROOT / "attestation_render.py").read_text("utf-8")
        self.assertIn('if kind == "pdf":\n        return opener(target)', viewer)
        self.assertIn("from pypdf import PdfReader, PdfWriter", renderer)
        self.assertIn("import pypdfium2 as pdfium", renderer)
        self.assertIn("def build_attestation_pdf", renderer)
        self.assertIn("def pdf_to_jpg_pages", renderer)

    def test_owner_and_proprietary_files_exist(self):
        license_text = (ROOT / "LICENSE").read_text("utf-8")
        copyright_text = (ROOT / "COPYRIGHT").read_text("utf-8")
        self.assertIn("Roman Zavada", license_text)
        self.assertIn("Роман Завада", copyright_text)
        self.assertIn("proprietary", license_text.lower())

    def test_sbom_and_notices_exclude_pymupdf(self):
        sbom = (ROOT / "SBOM.cdx.json").read_text("utf-8").lower()
        notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text("utf-8").lower()
        self.assertIn('"pypdf"', sbom)
        self.assertIn('"pypdfium2"', sbom)
        self.assertNotIn('"pymupdf"', sbom)
        self.assertIn("pymupdf", notices)
        self.assertIn("intentionally not", notices)


if __name__ == "__main__":
    unittest.main()
