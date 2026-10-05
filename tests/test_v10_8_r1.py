# -*- coding: utf-8 -*-
import re
import unittest
from pathlib import Path

import v1081_features as r1
import vehicle_documents
import v1064_features as waybill_ui
import v10710_features as document_center
import version_compat  # 10.10 stable-aware version parsing

ROOT = Path(__file__).resolve().parents[1]


def _version_tuple(text):
    match = version_compat.search_version(text)
    if not match:
        raise AssertionError("Taxo version not found: %r" % text)
    return tuple(int(part) for part in match.groups())


class VehicleFunctionalityGuardTests(unittest.TestCase):
    def test_core_vehicle_actions_are_explicit_and_complete(self):
        self.assertEqual(
            r1.VEHICLE_CORE_ACTIONS,
            (
                ("Нове авто", "vehicle_form"),
                ("Редагувати", "edit_vehicle"),
                ("Документи ТЗ", "vehicle_documents"),
                ("Контроль документів", "vehicle_document_control"),
                ("Вивести з експлуатації", "delete_vehicle"),
                ("Оновити", "load_vehicles"),
            ),
        )

    def test_critical_callbacks_remain_implemented_in_runtime_sources(self):
        sources = "\n".join(
            path.read_text("utf-8")
            for path in ROOT.glob("*.py")
        )
        for name in r1.CRITICAL_APP_METHODS:
            self.assertIn("def %s(" % name, sources, name)

    def test_vehicle_document_crud_window_is_still_complete(self):
        cls = vehicle_documents.VehicleDocumentsWindow
        for method in ("add_document", "edit_document", "archive_document", "open_copy", "load"):
            self.assertTrue(callable(getattr(cls, method, None)), method)
        source = (ROOT / "vehicle_documents.py").read_text("utf-8")
        for label in (
            "Додати документ", "Редагувати", "Архівувати",
            "Відкрити копію", "Оновити", "Показувати архів",
        ):
            self.assertIn(label, source)

    def test_vehicle_document_types_remain_available(self):
        source = (ROOT / "vehicle_documents.py").read_text("utf-8")
        for key in (
            "insurance", "additional_liability_insurance", "inspection",
            "temporary_registration", "registration_certificate",
            "tachograph_inspection_protocol",
        ):
            self.assertIn(key, source)

    def test_r1_uses_isolated_toolbar_instead_of_reusing_mixed_legacy_parent(self):
        source = (ROOT / "v1081_features.py").read_text("utf-8")
        self.assertIn('core.ttk.LabelFrame(tab, text="Картка транспортного засобу"', source)
        self.assertIn("app.vehicle_core_toolbar = frame", source)
        self.assertIn("button = core.ttk.Button(frame", source)
        self.assertNotIn("anchor.master", source)

    def test_known_legacy_geometry_conflict_remains_covered(self):
        registry = (ROOT / "v1048_features.py").read_text("utf-8")
        legacy_layout = (ROOT / "v1066_features.py").read_text("utf-8")
        # Regression signature: registry buttons were packed into the original
        # toolbar while r6 later tried to grid only the core buttons there.
        self.assertIn("parent = anchor.master", registry)
        self.assertIn("self._shlyakh_button.pack", registry)
        self.assertIn("control.pack_forget()", legacy_layout)
        self.assertIn("controls[index].grid(", legacy_layout)
        # 10.8-r1 must remain before every newer UI contract layer.
        entry = (ROOT / "taxo_app.py").read_text("utf-8")
        self.assertLess(entry.index("App = install_v10710(core, App)"), entry.index("App = install_v1081(core, App)"))
        if "App = install_v1082(core, App)" in entry:
            self.assertLess(entry.index("App = install_v1081(core, App)"), entry.index("App = install_v1082(core, App)"))


class PreservedInterfaceSurfaceTests(unittest.TestCase):
    def test_waybill_action_surface_is_preserved(self):
        self.assertEqual(
            waybill_ui.WAYBILL_ACTION_LABELS,
            (
                "Оновити", "Сформувати / видати PDF", "Відкрити PDF",
                "Перегляд у Taxo", "Анулювати номер", "Папка шляхівок",
                "Спідометр / пробіг", "Історія пробігу", "Зміни лікаря/механіка",
            ),
        )

    def test_document_center_keeps_all_subject_groups(self):
        groups = {title: actions for title, actions in document_center.DOCUMENT_CENTER_GROUPS}
        self.assertIn("Операційні документи", groups)
        self.assertIn("Транспорт", groups)
        self.assertIn("Військовий облік", groups)
        self.assertIn("Персонал", groups)
        self.assertIn(("Контроль документів ТЗ", "vehicle_document_control"), groups["Транспорт"])

    def test_sidebar_contract_is_present_in_current_sources(self):
        sources = "\n".join(
            (ROOT / name).read_text("utf-8")
            for name in ("main.py", "v1072_features.py", "v1081_features.py")
        )
        for label in r1.CRITICAL_NAV_SECTIONS:
            self.assertIn(label, sources, label)

    def test_start_archive_requires_current_runtime_layers(self):
        start = (ROOT / "START.bat").read_text("utf-8")
        workflow = (ROOT / ".github/workflows/source-test-archive.yml").read_text("utf-8")
        self.assertIn("v10710_features.py", start)
        self.assertIn("v1081_features.py", start)
        self.assertIn("v10710_features.py", workflow)
        self.assertIn("v1081_features.py", workflow)

    def test_r1_version_identity_remains_historical(self):
        self.assertEqual(r1.APP_VERSION, "10.8-r1")
        self.assertIn('APP_VERSION = "10.8-r1"', (ROOT / "v1081_features.py").read_text("utf-8"))
        current = (ROOT / "VERSION.txt").read_text("utf-8")
        self.assertGreaterEqual(_version_tuple(current), (10, 8, 1))


class ContractHelperTests(unittest.TestCase):
    def test_missing_labels_preserves_required_order(self):
        actual = ["Нове авто", "Оновити"]
        required = ["Нове авто", "Документи ТЗ", "Контроль документів", "Оновити"]
        self.assertEqual(
            r1.missing_labels(actual, required),
            ("Документи ТЗ", "Контроль документів"),
        )

    def test_missing_methods_detects_lost_callback(self):
        class Dummy:
            def one(self):
                pass
        self.assertEqual(r1.missing_methods(Dummy, ("one", "two")), ("two",))


if __name__ == "__main__":
    unittest.main()
