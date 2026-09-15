import json
import os
import socket
import sqlite3
import tempfile
import unittest
from pathlib import Path

import workspace


class V870R9WorkspaceTests(unittest.TestCase):
    def test_pointer_roundtrip_and_workspace_layout(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            config=root/"local-config"
            data=root/"shared"/"Taxo"
            old_config=os.environ.get(workspace.WORKSPACE_CONFIG_ENV)
            old_root=os.environ.pop(workspace.WORKSPACE_POINTER_ENV,None)
            os.environ[workspace.WORKSPACE_CONFIG_ENV]=str(config)
            try:
                pointer=workspace.save_workspace_root(data)
                self.assertEqual(workspace.load_workspace_root(),data)
                self.assertNotEqual(pointer.parent,data)
                paths=workspace.ensure_workspace(data)
                for key in ("data","backups","output","logs","tacho_scans","waybills"):
                    self.assertTrue(paths[key].is_dir(),key)
                self.assertTrue((data/workspace.MARKER_NAME).is_file())
            finally:
                if old_config is None:
                    os.environ.pop(workspace.WORKSPACE_CONFIG_ENV,None)
                else:
                    os.environ[workspace.WORKSPACE_CONFIG_ENV]=old_config
                if old_root is not None:
                    os.environ[workspace.WORKSPACE_POINTER_ENV]=old_root

    def test_workspace_lock_blocks_second_copy_and_releases_cleanly(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/"shared"
            first=workspace.WorkspaceLock(root,"test-first")
            second=workspace.WorkspaceLock(root,"test-second")
            first.acquire()
            info=workspace.read_lock_info(root)
            self.assertEqual(info["host"],socket.gethostname())
            with self.assertRaises(workspace.WorkspaceBusyError):
                second.acquire()
            self.assertTrue(first.refresh())
            self.assertTrue(first.release())
            second.acquire()
            self.assertTrue(second.release())

    def test_stale_same_machine_lock_is_recovered(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/"shared"
            workspace.ensure_workspace(root)
            (root/workspace.LOCK_NAME).write_text(json.dumps({
                "host":socket.gethostname(),"pid":99999999,
                "started_at":"2000-01-01T00:00:00+00:00",
                "heartbeat_at":"2000-01-01T00:00:00+00:00",
            }),"utf-8")
            lock=workspace.WorkspaceLock(root,"recovery")
            lock.acquire()
            self.assertTrue(lock.acquired)
            recovered=list((root/"Logs").glob("recovered_workspace_lock_*.json"))
            self.assertEqual(len(recovered),1)
            lock.release()

    def test_clone_copies_all_mutable_data_with_consistent_sqlite(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder); source=base/"source"; target=base/"target"
            src=workspace.ensure_workspace(source)
            con=sqlite3.connect(src["main_db"])
            con.execute("CREATE TABLE sample(value TEXT)")
            con.execute("INSERT INTO sample VALUES('main-data')")
            con.commit(); con.close()
            con=sqlite3.connect(src["tacho_db"])
            con.execute("CREATE TABLE discs(source_path TEXT)")
            con.execute("INSERT INTO discs VALUES('workspace://Data/TachographScans/scan.jpg')")
            con.commit(); con.close()
            (src["tacho_scans"]/"scan.jpg").write_bytes(b"scan")
            (src["waybills"]/"route.pdf").write_bytes(b"pdf")
            (src["backups"]/"manual.sqlite3").write_bytes(b"backup")

            result=workspace.clone_workspace(source,target)
            workspace.validate_sqlite(result["main_db"])
            workspace.validate_sqlite(result["tacho_db"])
            con=sqlite3.connect(result["main_db"])
            self.assertEqual(con.execute("SELECT value FROM sample").fetchone()[0],"main-data")
            con.close()
            self.assertEqual((result["tacho_scans"]/"scan.jpg").read_bytes(),b"scan")
            self.assertEqual((result["waybills"]/"route.pdf").read_bytes(),b"pdf")
            self.assertTrue(src["main_db"].exists(),"old workspace must remain as safety copy")

    def test_workspace_relative_paths_survive_different_computer_roots(self):
        with tempfile.TemporaryDirectory() as folder:
            current=Path(folder)/"Cloud"/"Taxo"
            workspace.ensure_workspace(current)
            legacy=r"C:\\Users\\FirstPC\\OneDrive\\Taxo\\Output\\Waybills\\2031\\route.pdf"
            resolved=workspace.resolved_path(legacy,current)
            self.assertEqual(resolved,current/"Output"/"Waybills"/"2031"/"route.pdf")
            portable=workspace.stored_path(resolved,current)
            self.assertEqual(portable,"workspace://Output/Waybills/2031/route.pdf")
            self.assertEqual(workspace.resolved_path(portable,current),resolved)
            self.assertIsNone(workspace.resolved_path("workspace://../../outside.txt",current))

    def test_path_fields_in_database_are_normalized(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/"Taxo"; p=workspace.ensure_workspace(root)
            target=p["waybills"]/"one.pdf"; target.write_bytes(b"pdf")
            con=sqlite3.connect(p["main_db"])
            con.execute("CREATE TABLE waybills(pdf_path TEXT)")
            con.execute("INSERT INTO waybills VALUES(?)",(str(target),))
            con.commit(); con.close()
            changed=workspace.normalize_database_paths(p["main_db"],root,{"waybills":("pdf_path",)})
            con=sqlite3.connect(p["main_db"])
            value=con.execute("SELECT pdf_path FROM waybills").fetchone()[0]
            con.close()
            self.assertEqual(changed,1)
            self.assertEqual(value,"workspace://Output/Waybills/one.pdf")

    def test_r9_release_builds_workspace_aware_packages(self):
        root=Path(__file__).resolve().parents[1]
        workflow=(root/".github"/"workflows"/"publish-v8.70-r9.yml").read_text("utf-8")
        self.assertIn("python -m py_compile main.py workspace.py",workflow)
        self.assertIn("Taxo_v8_70_TEST_r9_Setup_Windows_x64.exe",workflow)
        self.assertIn("Taxo_v8_70_TEST_r9_Windows_x64_Portable.zip",workflow)
        self.assertIn("Taxo_v8_70_TEST_r9_macOS_arm64_Portable.zip",workflow)
        self.assertIn("Taxo_v8_70_TEST_r9_macOS_x86_64_Portable.zip",workflow)
        self.assertIn("SHA256SUMS_v8_70_TEST_r9.txt",workflow)
        self.assertIn("Database unexpectedly bundled",workflow)

    def test_main_and_tachograph_follow_the_same_selected_root(self):
        import main
        import tachograph
        old_root=main.DATA_ROOT
        try:
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder)/"shared"
                main.configure_runtime_workspace(root)
                main.init_db()
                tachograph.init_tacho_db()
                self.assertEqual(main.DB_PATH,root/"Data"/"driver_worktime.sqlite3")
                self.assertEqual(tachograph.TACHO_DB,root/"Data"/"tachograph_test.sqlite3")
                self.assertEqual(tachograph.SCAN_DIR,root/"Data"/"TachographScans")
                con=main.db()
                self.assertEqual(con.execute("PRAGMA journal_mode").fetchone()[0].lower(),"delete")
                con.close()
        finally:
            main.configure_runtime_workspace(old_root)


if __name__=="__main__":
    unittest.main()
