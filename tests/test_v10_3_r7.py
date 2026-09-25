# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

import main
from release_naming import start_archive_stem, version_from_file


ROOT=Path(__file__).resolve().parents[1]


class TestTaxo103R7BackupDialogRecovery(unittest.TestCase):
    def test_r7_checkpoint_stays_immutable_after_later_revisions(self):
        self.assertEqual(main.APP_VERSION,version_from_file(ROOT/"VERSION.txt"))
        self.assertEqual(
            start_archive_stem("10.3-r7"),
            "Taxo_v10_3_candidate_r7_START",
        )
        notes=(ROOT/"docs"/"releases"/"RELEASE_NOTES_v10_3_r7.md").read_text("utf-8")
        self.assertIn("Taxo 10.3-r7",notes)

    def test_backup_dialog_reserves_visible_footer(self):
        source=(ROOT/"main.py").read_text("utf-8")
        start=source.index("    def manual_backup(self):")
        end=source.index("    def open_data_folder",start)
        section=source[start:end]

        self.assertIn(
            "fit_window_to_screen(win,760,560,660,500)",
            section,
        )
        self.assertIn("shell=ttk.Frame(win)",section)
        self.assertIn("shell.rowconfigure(0,weight=1)",section)
        self.assertIn(
            'buttons=ttk.Frame(shell,padding=(16,8,16,14))',
            section,
        )
        self.assertIn(
            'buttons.grid(row=1,column=0,sticky="ew")',
            section,
        )
        self.assertNotIn(
            'buttons.pack(fill="x",side="bottom"',
            section,
        )

    def test_backup_content_and_actions_remain_unchanged(self):
        source=(ROOT/"main.py").read_text("utf-8")
        start=source.index("    def manual_backup(self):")
        end=source.index("    def open_data_folder",start)
        section=source[start:end]

        for text in (
            "Копії документів транспортних засобів",
            "Скани тахографів",
            "Шляхівки, бланки, звіти й архіви з папки Output",
            'text="Скасувати"',
            'text="Створити копію"',
            "create_workspace_backup_archive(",
        ):
            self.assertIn(text,section)

    def test_start_here_has_stronger_recovery_contract(self):
        text=(ROOT/"START_HERE.md").read_text("utf-8")
        self.assertIn("Джерела істини та їхня роль",text)
        self.assertIn("Команда власника «злити у main»",text)
        self.assertIn("інтегрувати PR у main",text)
        self.assertIn("VERSION.txt",text)
        self.assertIn("main.APP_VERSION",text)

    def test_permanent_rules_define_full_main_checkpoint(self):
        text=(ROOT/"PROJECT_RULES.md").read_text("utf-8")
        self.assertIn("## 15. Команда власника «злити у main»",text)
        self.assertIn("повний релізний checkpoint",text)


if __name__=="__main__":
    unittest.main()
