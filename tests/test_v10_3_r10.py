# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

import main
from release_naming import start_archive_stem, version_from_file

ROOT=Path(__file__).resolve().parents[1]

class TestTaxo103R10Windows7(unittest.TestCase):
    def test_r10_checkpoint_stays_immutable_after_later_revisions(self):
        self.assertEqual(main.APP_VERSION,version_from_file(ROOT/"VERSION.txt"))
        self.assertEqual(start_archive_stem("10.3-r10"),"Taxo_v10_3_candidate_r10_START")
        notes=(ROOT/"docs"/"releases"/"RELEASE_NOTES_v10_3_r10.md").read_text("utf-8")
        self.assertIn("Taxo 10.3-r10",notes)

    def test_win7_requirements_are_python38_compatible_line(self):
        text=(ROOT/"requirements-win7.txt").read_text("utf-8")
        for item in ("python-docx==1.1.2","reportlab==4.3.0","Pillow==10.4.0","PyMuPDF==1.24.11","opencv-python-headless==4.10.0.84","pywin32==306"):
            self.assertIn(item,text)

    def test_win7_pyinstaller_spec_avoids_modern_analysis_arguments(self):
        text=(ROOT/"Taxo_win7.spec").read_text("utf-8")
        self.assertNotIn("optimize=",text)
        self.assertIn("LICENSE.md",text)
        self.assertIn("COPYRIGHT.md",text)
        self.assertIn("THIRD_PARTY_NOTICES.md",text)

    def test_win7_installer_requires_sp1(self):
        text=(ROOT/"installer"/"Taxo_v10_3_r10_win7.iss").read_text("utf-8")
        self.assertIn("MinVersion=6.1sp1",text)
        self.assertIn("Taxo_v10_3_candidate_r10_Setup_Windows7_x64",text)

    def test_release_notes_record_exact_loader_failure(self):
        text=(ROOT/"docs"/"releases"/"RELEASE_NOTES_v10_3_r10.md").read_text("utf-8")
        self.assertIn("api-ms-win-core-path-l1-1-0.dll",text)
        self.assertIn("CPython 3.8.10",text)

if __name__=="__main__":
    unittest.main()
