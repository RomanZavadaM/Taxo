import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import application_context
import feature_layers


ROOT = Path(__file__).resolve().parents[1]


class ApplicationContextR8Tests(unittest.TestCase):
    def test_workspace_services_follow_runtime_workspace_switch(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            state = {"root": Path(first)}
            services = application_context.WorkspaceServices(lambda: state["root"])
            self.assertEqual(services.root, Path(first))
            self.assertEqual(services.main_db_path, Path(first) / "Data" / "driver_worktime.sqlite3")
            state["root"] = Path(second)
            self.assertEqual(services.root, Path(second))
            self.assertEqual(services.output_dir, Path(second) / "Output")

    def test_context_opens_fresh_connection_to_current_workspace(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "Data").mkdir()
            services = application_context.WorkspaceServices(lambda: root)

            con = services.connect_main_db()
            try:
                con.execute("CREATE TABLE sample(value TEXT)")
                con.execute("INSERT INTO sample(value) VALUES ('ok')")
                con.commit()
            finally:
                con.close()

            check = sqlite3.connect(services.main_db_path)
            try:
                self.assertEqual(check.execute("SELECT value FROM sample").fetchone()[0], "ok")
            finally:
                check.close()

    def test_builder_exposes_infrastructure_without_business_rules(self):
        fake_core = SimpleNamespace(
            DATA_ROOT=Path("/tmp/taxo-context-test"),
            APP_VERSION="10.8-r8",
            write_output_file=lambda *args, **kwargs: None,
            open_external=lambda path: path,
            report_font_candidates=lambda: ["font"],
        )
        services = application_context.build_application_services(fake_core)
        self.assertEqual(services.app_version, "10.8-r8")
        self.assertIs(services.output.write_file, fake_core.write_output_file)
        self.assertFalse(hasattr(services, "plan"))
        self.assertFalse(hasattr(services, "timesheet"))
        self.assertFalse(hasattr(services, "attestation"))

    def test_context_aware_layer_receives_services_without_changing_legacy_signature(self):
        calls = []
        services = object()

        def bootstrap(core):
            calls.append(("legacy-bootstrap", core))
            return type("Base", (), {})

        def context_layer(core, app_cls, received_services):
            calls.append(("context", core, received_services))
            return type("Extended", (app_cls,), {})

        layers = (
            feature_layers.FeatureLayer("base", bootstrap, bootstrap=True),
            feature_layers.FeatureLayer("future", context_layer, uses_services=True, domain="future"),
        )
        app_cls = feature_layers.install_feature_layers("CORE", layers=layers, services=services)
        self.assertEqual([call[0] for call in calls], ["legacy-bootstrap", "context"])
        self.assertIs(calls[1][2], services)
        self.assertIs(app_cls.services, services)

    def test_context_aware_layer_fails_fast_without_services(self):
        def bootstrap(core):
            return type("Base", (), {})

        def context_layer(core, app_cls, services):
            return app_cls

        layers = (
            feature_layers.FeatureLayer("base", bootstrap, bootstrap=True),
            feature_layers.FeatureLayer("future", context_layer, uses_services=True),
        )
        with self.assertRaisesRegex(RuntimeError, "requires application services"):
            feature_layers.install_feature_layers("CORE", layers=layers)

    def test_runtime_entrypoint_builds_and_exposes_services(self):
        source = (ROOT / "taxo_app.py").read_text(encoding="utf-8")
        self.assertIn("from application_context import build_application_services", source)
        self.assertIn("SERVICES = build_application_services(core)", source)
        self.assertIn("install_feature_layers(core, services=SERVICES)", source)


if __name__ == "__main__":
    unittest.main()
