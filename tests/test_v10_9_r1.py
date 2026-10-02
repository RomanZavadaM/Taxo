import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import application_context
import data_access
import main


ROOT = Path(__file__).resolve().parents[1]


def _revision_tuple(version):
    text = str(version or "").strip().removeprefix("Version: ")
    base, sep, rev = text.partition("-r")
    major, minor = (int(part) for part in base.split(".", 1))
    return major, minor, int(rev) if sep else 0


class DataAccessR1Tests(unittest.TestCase):
    def test_r1_identity_is_historical_anchor_not_current_version_lock(self):
        current_file = (ROOT / "VERSION.txt").read_text(encoding="utf-8").strip()
        self.assertGreaterEqual(_revision_tuple(current_file), (10, 9, 1))
        self.assertGreaterEqual(_revision_tuple(main.APP_VERSION), (10, 9, 1))
        source = (ROOT / "docs/releases/RELEASE_NOTES_v10.9-r1.md").read_text(encoding="utf-8")
        self.assertIn("10.9-r1", source)

    def test_data_access_commits_successful_write(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db.sqlite3"
            con = sqlite3.connect(path)
            con.execute("CREATE TABLE sample(value TEXT)")
            con.commit()
            con.close()

            access = data_access.DataAccess(lambda: sqlite3.connect(path))
            self.assertEqual(access.execute("INSERT INTO sample(value) VALUES (?)", ("ok",)), 1)
            self.assertEqual(access.fetch_one("SELECT value FROM sample")[0], "ok")

    def test_transaction_rolls_back_as_one_unit(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db.sqlite3"
            con = sqlite3.connect(path)
            con.execute("CREATE TABLE sample(value TEXT UNIQUE)")
            con.commit()
            con.close()

            access = data_access.DataAccess(lambda: sqlite3.connect(path))
            with self.assertRaises(sqlite3.IntegrityError):
                with access.transaction() as con:
                    con.execute("INSERT INTO sample(value) VALUES ('same')")
                    con.execute("INSERT INTO sample(value) VALUES ('same')")
            self.assertEqual(access.fetch_all("SELECT value FROM sample"), [])

    def test_application_services_follow_workspace_switch_for_data_access(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            state = {"root": Path(first)}
            for root, value in ((Path(first), "first"), (Path(second), "second")):
                (root / "Data").mkdir()
                con = sqlite3.connect(root / "Data" / "driver_worktime.sqlite3")
                con.execute("CREATE TABLE marker(value TEXT)")
                con.execute("INSERT INTO marker(value) VALUES (?)", (value,))
                con.commit()
                con.close()

            core = SimpleNamespace(
                DATA_ROOT=state["root"],
                APP_VERSION="10.9-r1",
                write_output_file=lambda *args, **kwargs: None,
                open_external=lambda path: path,
                report_font_candidates=lambda: [],
            )
            services = application_context.ApplicationServices(
                workspace=application_context.WorkspaceServices(lambda: state["root"]),
                output=application_context.OutputServices(
                    write_file=core.write_output_file,
                    open_external=core.open_external,
                    report_font_candidates=core.report_font_candidates,
                ),
                data=None,
                version_provider=lambda: core.APP_VERSION,
            )
            access = data_access.DataAccess(services.workspace.connect_main_db)
            self.assertEqual(access.fetch_one("SELECT value FROM marker")[0], "first")
            state["root"] = Path(second)
            self.assertEqual(access.fetch_one("SELECT value FROM marker")[0], "second")

    def test_data_access_module_has_no_ui_or_domain_dependencies(self):
        source = (ROOT / "data_access.py").read_text(encoding="utf-8")
        self.assertNotIn("tkinter", source)
        self.assertNotIn("messagebox", source)
        self.assertNotIn("vehicle_", source)
        self.assertNotIn("personnel_", source)

    def test_application_context_uses_database_runtime_policy(self):
        source = (ROOT / "application_context.py").read_text(encoding="utf-8")
        self.assertIn("from database_runtime import connect_database", source)
        self.assertIn("return connect_database(self.main_db_path)", source)
        self.assertIn("data=DataAccess(workspace.connect_main_db)", source)


if __name__ == "__main__":
    unittest.main()
