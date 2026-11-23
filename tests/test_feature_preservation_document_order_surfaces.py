# -*- coding: utf-8 -*-
"""Additional preservation contract for post-10.18 document and order UI surfaces.

This is a structural tripwire, NOT a replacement for strict Tk runtime checks.
It catches disappearing entry points before they become silent feature losses.
"""
from pathlib import Path
import ast
import unittest


ROOT = Path(__file__).resolve().parents[1] / "src" / "taxo"

# Required existing user-facing actions; each contract pairs the visible label
# with its implementation entry point. Introduced as a first extension to
# the 29 strict runtime routes, not counted as live runtime coverage.
SURFACES = {
    "document_catalog_ui.py": (
        ("Нова папка…", "create_collection"),
        ("Перейменувати…", "rename_collection"),
        ("Перемістити папку…", "move_collection"),
        ("Архівувати папку…", "archive_collection"),
        ("Відновити з архіву…", "restore_collection"),
        ("Розмістити документ…", "set_document_collections"),
        ("Скани…", "manage_paper_scans"),
        ("Паперовий підпис…", "manage_paper_original"),
        ("Копія для редагування…", "copy_prepared_document_for_editing"),
        ("Додати редакцію DOCX…", "import_prepared_document_revision"),
        ("PDF / друк…", "build_prepared_revision_pdf"),
        ("Зберегти вибрану редакцію у сховищі", "store_selected_in_vault"),
        ("Переглянути сховище документів", "browse_document_vault"),
    ),
    "order_entities_ui.py": (
        ("Додати працівників…", "entity_picker"),
        ("Додати ТЗ…", "entity_picker"),
        ("Прибрати вибрані", "remove_order_entities"),
        ("Змінити роль / примітку…", "edit_order_entity"),
        ("Додати вибрані", "save_entities"),
    ),
    "order_preview_ui.py": (
        ("Створити DOCX", "generate_order_formats"),
        ("Створити PDF", "generate_order_formats"),
        ("Створити JPG", "generate_order_formats"),
        ("Створити все", "generate_order_formats"),
        ("Оновити зміст", "refresh_preview_content"),
    ),
}


def missing_surfaces(files):
    """Return precise missing actions for a supplied source snapshot."""
    missing = []
    for module_name, contracts in SURFACES.items():
        source = files.get(module_name)
        if source is None:
            missing.append((module_name, "<module missing>"))
            continue
        for label, target in contracts:
            if label not in source:
                missing.append((module_name, "label: " + label))
            if target not in source:
                missing.append((module_name, "target: " + target))
    return missing


# Central order toolbar is built from an action tuple rather than literal
# Button(text=...). Verify exact label-to-callback wiring so a static
# button-label-only scan cannot silently miss a removed command.
ORDER_ACTIONS = {
    "Новий наказ…": "new_order",
    "Переглянути / друк": "preview_order",
    "Нумерація наказів…": "open_numbering_settings",
    "Редагувати наказ": "edit_order",
    "Ввести в дію в Taxo": "approve_selected",
    "Історія…": "show_history",
    "Скасувати наказ": "cancel_draft",
    "Видалити наказ": "delete_selected_order",
    "Сформувати PDF": "export_selected",
    "Підпис на папері: так / ні": "mark_paper_signed",
}


def extract_order_actions(source):
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "order_actions"
            for target in node.targets
        ):
            continue
        result = {}
        for item in node.value.elts:
            label, callback = item.elts[:2]
            if not isinstance(label, ast.Constant) or not isinstance(callback, ast.Name):
                raise AssertionError("Order toolbar contains an untracked dynamic action")
            if label.value in result:
                raise AssertionError("Duplicate order toolbar label")
            result[label.value] = callback.id
        return result
    raise AssertionError("The central order toolbar action table disappeared")


class DocumentAndOrderSurfacePreservationTests(unittest.TestCase):
    def test_current_documents_and_orders_are_not_silently_removed(self):
        files = {
            name: (ROOT / name).read_text(encoding="utf-8")
            for name in SURFACES
        }
        self.assertEqual(missing_surfaces(files), [])

    def test_all_central_order_buttons_keep_their_actual_handlers(self):
        source = (ROOT / "order_register_ui.py").read_text(encoding="utf-8")
        self.assertEqual(extract_order_actions(source), ORDER_ACTIONS)

    def test_order_action_mutation_is_detected_even_when_name_remains_elsewhere(self):
        source = (ROOT / "order_register_ui.py").read_text(encoding="utf-8")
        changed = source.replace(
            '("Видалити наказ", delete_selected_order, None)',
            '("Видалити наказ", cancel_draft, None)',
        )
        self.assertNotEqual(extract_order_actions(changed), ORDER_ACTIONS)

    def test_tripwire_fails_if_a_registered_action_disappears(self):
        files = {
            name: (ROOT / name).read_text(encoding="utf-8")
            for name in SURFACES
        }
        changed = dict(files)
        changed["document_catalog_ui.py"] = changed[
            "document_catalog_ui.py"
        ].replace("Відновити з архіву…", "__DELETED_ACTION__")
        self.assertIn(
            ("document_catalog_ui.py", "label: Відновити з архіву…"),
            missing_surfaces(changed),
        )

    def test_tripwire_fails_if_implementation_entry_disappears(self):
        files = {
            name: (ROOT / name).read_text(encoding="utf-8")
            for name in SURFACES
        }
        changed = dict(files)
        changed["order_entities_ui.py"] = changed[
            "order_entities_ui.py"
        ].replace("remove_order_entities", "__DISCONNECTED_CALLBACK__")
        self.assertIn(
            ("order_entities_ui.py", "target: remove_order_entities"),
            missing_surfaces(changed),
        )


if __name__ == "__main__":
    unittest.main()
