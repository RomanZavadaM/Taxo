import unittest
from pathlib import Path

import feature_layers


ROOT = Path(__file__).resolve().parents[1]


class FeatureLayerRegistryR7Tests(unittest.TestCase):
    def test_registry_has_one_bootstrap_and_unique_ids(self):
        feature_layers.validate_feature_layers()
        ids = feature_layers.feature_layer_ids()
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids[0], "work-analysis-r10")
        self.assertEqual(ids[-1], "v1085-stoir")
        self.assertTrue(feature_layers.FEATURE_LAYERS[0].bootstrap)
        self.assertFalse(any(layer.bootstrap for layer in feature_layers.FEATURE_LAYERS[1:]))

    def test_historical_install_order_anchors_are_preserved(self):
        ids = feature_layers.feature_layer_ids()
        expected = (
            "work-analysis-r10",
            "activity-register-60",
            "v9-release",
            "hotfix-901",
            "v91-features",
            "personnel-v91",
            "v1043",
            "military-accounting-ui",
            "v10510",
            "v1063",
            "v1074-appendix-history",
            "v10710",
            "v1081",
            "v1084-stoir",
            "v1085-stoir",
        )
        positions = [ids.index(item) for item in expected]
        self.assertEqual(positions, sorted(positions))

    def test_registry_composes_layers_in_declared_order(self):
        calls = []

        def bootstrap(core):
            calls.append(("bootstrap", core))
            return type("App0", (), {})

        def extend_a(core, app_cls):
            calls.append(("a", core, app_cls.__name__))
            return type("AppA", (app_cls,), {})

        def extend_b(core, app_cls):
            calls.append(("b", core, app_cls.__name__))
            return type("AppB", (app_cls,), {})

        layers = (
            feature_layers.FeatureLayer("bootstrap", bootstrap, bootstrap=True),
            feature_layers.FeatureLayer("a", extend_a),
            feature_layers.FeatureLayer("b", extend_b),
        )
        result = feature_layers.install_feature_layers("CORE", layers)
        self.assertEqual(result.__name__, "AppB")
        self.assertEqual([item[0] for item in calls], ["bootstrap", "a", "b"])

    def test_entrypoint_is_not_a_nested_version_install_chain_anymore(self):
        source = (ROOT / "taxo_app.py").read_text(encoding="utf-8")
        self.assertIn("from feature_layers import install_feature_layers", source)
        self.assertIn("App = install_feature_layers(core)", source)
        self.assertNotIn("install_v1085(core, App)", source)
        self.assertNotIn("install_v1063(\n", source)

    def test_domains_are_metadata_not_cross_domain_business_coupling(self):
        by_id = {layer.feature_id: layer.domain for layer in feature_layers.FEATURE_LAYERS}
        self.assertEqual(by_id["personnel-v91"], "personnel")
        self.assertEqual(by_id["military-accounting-ui"], "military-accounting")
        self.assertEqual(by_id["v1084-stoir"], "maintenance")
        self.assertEqual(by_id["v1085-stoir"], "maintenance")


if __name__ == "__main__":
    unittest.main()
