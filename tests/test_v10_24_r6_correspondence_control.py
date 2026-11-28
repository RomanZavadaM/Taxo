# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

import function_registry
import runtime_reachability


EXPECTED_CORRESPONDENCE_ROUTES = {
    "correspondence.center",
    "correspondence.new_incoming",
    "correspondence.new_outgoing",
    "correspondence.reply",
    "correspondence.attachments",
    "correspondence.open_document",
    "correspondence.mark_received",
    "correspondence.mark_sent",
    "correspondence.status_transition",
    "correspondence.state_history",
    "correspondence.case_create",
    "correspondence.case_assign",
    "correspondence.case_edit",
    "correspondence.case_archive",
    "correspondence.case_thread_add",
    "correspondence.case_open_letter",
    "correspondence.case_remove_letter",
}


class CorrespondenceControlR6Tests(unittest.TestCase):
    def test_candidate_identity(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "VERSION.txt").read_text("utf-8"),
            "Version: 10.25-r6\n",
        )
        self.assertIn(
            'APP_VERSION = "10.25-r6"',
            (root / "main.py").read_text("utf-8"),
        )
        self.assertIn(
            "Taxo 10.25-r6 - START",
            (root / "START.bat").read_text("utf-8"),
        )
        self.assertEqual(
            (root / ".release" / "full-current").read_text("utf-8"),
            "10.25-r6\n",
        )

    def test_correspondence_routes_are_complete_and_runtime_mapped(self):
        routes = tuple(function_registry.FUNCTION_ROUTES)
        # r6 froze the correspondence contract at 17 routes. Later revisions
        # may add strict routes for other modules, so the global route count is
        # intentionally a floor while the correspondence set stays exact.
        self.assertGreaterEqual(len(routes), 55)
        correspondence = {
            route.function_id
            for route in routes
            if route.function_id.startswith("correspondence.")
        }
        self.assertEqual(correspondence, EXPECTED_CORRESPONDENCE_ROUTES)
        for route in routes:
            if route.function_id in EXPECTED_CORRESPONDENCE_ROUTES:
                self.assertTrue(route.required, route.function_id)
                self.assertTrue(route.runtime_smoke, route.function_id)
        self.assertEqual(
            {
                route_id
                for route_id in runtime_reachability.RUNTIME_ROUTE_TEST_MODULES
                if route_id.startswith("correspondence.")
            },
            EXPECTED_CORRESPONDENCE_ROUTES,
        )


if __name__ == "__main__":
    unittest.main()
