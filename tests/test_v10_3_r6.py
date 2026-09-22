# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

import main
from release_naming import start_archive_stem, version_from_file

ROOT=Path(__file__).resolve().parents[1]


class TestTaxo103R6Copyright(unittest.TestCase):
    def test_r6_checkpoint_stays_immutable_after_stable_promotion(self):
        self.assertEqual(main.APP_VERSION,version_from_file(ROOT/"VERSION.txt"))
        self.assertEqual(
            start_archive_stem("10.3-r6"),
            "Taxo_v10_3_candidate_r6_START",
        )

    def test_personal_copyright_owner_is_constant(self):
        self.assertEqual(main.COPYRIGHT_OWNER,"Roman Zavada (Роман Завада)")
        self.assertIn("© 2026 Roman Zavada",main.COPYRIGHT_NOTICE)
        self.assertNotIn("company",main.COPYRIGHT_NOTICE.lower())

    def test_legal_files_exist_and_name_owner(self):
        for name in ("LICENSE.md","COPYRIGHT.md","THIRD_PARTY_NOTICES.md"):
            path=ROOT/name
            self.assertTrue(path.is_file(),name)
            text=path.read_text("utf-8")
            self.assertIn("Roman Zavada",text)
        license_text=(ROOT/"LICENSE.md").read_text("utf-8")
        self.assertIn("proprietary",license_text.lower())
        self.assertIn("does **not** place the Software in the public domain",license_text)

    def test_about_window_displays_owner_not_company_as_copyright_holder(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertIn('("Правовласник",COPYRIGHT_OWNER)',source)
        self.assertIn('("Ліцензія",LICENSE_LABEL)',source)
        self.assertIn('text=f"{COPYRIGHT_NOTICE} · Taxo {APP_VERSION}"',source)
        self.assertNotIn('text=f"© 2026 {self._company_name_value()}',source)

    def test_help_contains_copyright_topic(self):
        source=(ROOT/"main.py").read_text("utf-8")
        self.assertIn('"Авторські права":(',source)
        self.assertIn("Публічна видимість репозиторію",source)

    def test_executable_bundle_contains_legal_notices(self):
        spec=(ROOT/"Taxo.spec").read_text("utf-8")
        for name in ("LICENSE.md","COPYRIGHT.md","THIRD_PARTY_NOTICES.md"):
            self.assertIn(f"('{name}', '.')",spec)

    def test_readme_explains_proprietary_status(self):
        readme=(ROOT/"README.md").read_text("utf-8")
        self.assertIn("Copyright © 2026 Roman Zavada",readme)
        self.assertIn("proprietary software",readme)
        self.assertIn("[LICENSE.md](LICENSE.md)",readme)

    def test_installer_uses_personal_publisher(self):
        iss=(ROOT/"installer"/"Taxo.iss").read_text("utf-8")
        self.assertIn('#define MyAppPublisher "Roman Zavada"',iss)
        self.assertIn("VersionInfoCopyright=Copyright (C) 2026 Roman Zavada",iss)


if __name__=="__main__":
    unittest.main()
