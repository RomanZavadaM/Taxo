# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

import main
from release_naming import start_archive_stem, version_from_file


ROOT=Path(__file__).resolve().parents[1]


class TestTaxo102R9AttestationAndLegal(unittest.TestCase):
    def test_version_is_r9_everywhere(self):
        self.assertEqual(main.APP_VERSION,"10.2-r9")
        self.assertEqual(version_from_file(ROOT/"VERSION.txt"),"10.2-r9")
        self.assertEqual(start_archive_stem("10.2-r9"),"Taxo_v10_2_candidate_r9_START")

    def test_new_attestation_is_selected_after_creation(self):
        source=(ROOT/"main.py").read_text("utf-8")
        marker="# r9: after creating a new blank, select exactly that new record."
        self.assertIn(marker,source)
        start=source.index(marker)
        snippet=source[start:start+1200]
        self.assertIn('str(values[0]) == str(att_id)',snippet)
        self.assertIn("selection_set(iid)",snippet)
        self.assertIn("focus(iid)",snippet)
        self.assertIn("see(iid)",snippet)

    def test_docx_generator_still_uses_form_period_values_directly(self):
        source=(ROOT/"main.py").read_text("utf-8")
        start=source.index("def fill_attestation")
        end=source.index("def _attestation_render_context",start)
        snippet=source[start:end]
        self.assertIn('(period_from, True)',snippet)
        self.assertIn('(period_to, True)',snippet)
        self.assertIn("doc.save(str(out_path))",snippet)

    def test_pymupdf_removed(self):
        req=(ROOT/"requirements.txt").read_text("utf-8")
        viewer=(ROOT/"document_viewer.py").read_text("utf-8")
        self.assertNotIn("PyMuPDF",req)
        self.assertNotIn("import fitz",viewer)
        self.assertNotIn("fitz.",viewer)

    def test_pdf_preview_delegates_to_external_viewer(self):
        source=(ROOT/"document_viewer.py").read_text("utf-8")
        self.assertIn('if kind == "pdf":',source)
        self.assertIn("return opener(target)",source)

    def test_proprietary_legal_files_present(self):
        for path in ("LICENSE","COPYRIGHT","THIRD_PARTY_NOTICES.md","docs/legal/ASSET_PROVENANCE.md"):
            self.assertTrue((ROOT/path).exists(),path)
        license_text=(ROOT/"LICENSE").read_text("utf-8")
        self.assertIn("Roman Zavada",license_text)
        self.assertIn("NOT licensed as open-source software",license_text)


if __name__=="__main__":
    unittest.main()
