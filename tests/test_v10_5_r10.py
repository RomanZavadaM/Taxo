# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
from types import SimpleNamespace

import v10510_features as r10

ROOT = Path(__file__).resolve().parents[1]


class ScheduleAuditDomainR10Tests(unittest.TestCase):
    def test_day_boundary_mismatches_are_not_treated_as_day_errors(self):
        data = {
            "findings": [
                {
                    "source_kind": "worklog",
                    "kind": "route_start_boundary_mismatch",
                    "message": "day snapshot vs live route template",
                },
                {
                    "source_kind": "worklog",
                    "kind": "route_end_boundary_mismatch",
                    "message": "day snapshot vs live route template",
                },
                {
                    "source_kind": "worklog",
                    "kind": "drive_overlap",
                    "message": "real internal day-plan input problem",
                },
            ],
            "day_findings": 3,
            "route_findings": 0,
        }
        result = r10.separate_schedule_audit_domains(data)
        self.assertEqual(len(result["findings"]), 1)
        self.assertEqual(result["findings"][0]["kind"], "drive_overlap")
        self.assertEqual(result["day_findings"], 1)
        self.assertEqual(result["suppressed_day_route_boundary_findings"], 2)

    def test_current_route_template_boundary_checks_are_preserved(self):
        data = {
            "findings": [
                {
                    "source_kind": "route",
                    "kind": "route_start_boundary_mismatch",
                    "route_id": 751,
                },
                {
                    "source_kind": "route",
                    "kind": "route_end_boundary_mismatch",
                    "route_id": 751,
                },
            ],
            "day_findings": 0,
            "route_findings": 2,
        }
        result = r10.separate_schedule_audit_domains(data)
        self.assertEqual(len(result["findings"]), 2)
        self.assertEqual(result["route_findings"], 2)
        self.assertEqual(result["suppressed_day_route_boundary_findings"], 0)

    def test_fact_fields_are_not_read_or_rewritten_by_filter(self):
        finding = {
            "source_kind": "worklog",
            "kind": "incomplete_drive",
            "fact_work_start_time": "08:10",
            "fact_work_end_time": "18:20",
        }
        data = {"findings": [finding], "day_findings": 1, "route_findings": 0}
        result = r10.separate_schedule_audit_domains(data)
        self.assertEqual(result["findings"][0]["fact_work_start_time"], "08:10")
        self.assertEqual(result["findings"][0]["fact_work_end_time"], "18:20")
        self.assertIs(result["findings"][0], finding)

    def test_installed_collector_filters_only_invalid_cross_domain_findings(self):
        original_findings = [
            {"source_kind": "worklog", "kind": "route_start_boundary_mismatch"},
            {"source_kind": "route", "kind": "route_start_boundary_mismatch"},
            {"source_kind": "worklog", "kind": "empty_segment"},
        ]

        class BaseApp:
            pass

        core = SimpleNamespace(
            App=BaseApp,
            APP_VERSION="10.5-r9",
            collect_schedule_integrity_audit=lambda *args, **kwargs: {
                "findings": list(original_findings),
                "day_findings": 2,
                "route_findings": 1,
            },
        )
        r10.install(core, BaseApp)
        result = core.collect_schedule_integrity_audit(2026, 9, work_date="2026-09-28")
        self.assertEqual(
            [(x["source_kind"], x["kind"]) for x in result["findings"]],
            [
                ("route", "route_start_boundary_mismatch"),
                ("worklog", "empty_segment"),
            ],
        )
        self.assertEqual(core.APP_VERSION, "10.5-r10")


class R10IntegrationTests(unittest.TestCase):
    def test_r10_remains_in_runtime_chain_after_later_revisions(self):
        entry = (ROOT / "taxo_app.py").read_text(encoding="utf-8")
        self.assertIn("from v10510_features import install as install_v10510", entry)
        self.assertIn("install_v10510(", entry)
        self.assertIn("install_v1059(", entry)
        # 10.5-r10 is immutable historical behavior; a newer outer layer may
        # legitimately wrap it after the 10.5-r10 -> 10.6-r1 rollover.
        if "install_v1061(" in entry:
            self.assertLess(entry.index("install_v1061("), entry.index("install_v10510("))

    def test_fix_documents_why_day_and_live_template_are_not_comparable(self):
        source = (ROOT / "v10510_features.py").read_text(encoding="utf-8")
        self.assertIn("work_segments", source)
        self.assertIn("route_stops", source)
        self.assertIn("ПОТОЧНИЙ", source)
        self.assertIn("fact_work_*", source)
        self.assertIn('APP_VERSION = "10.5-r10"', source)


if __name__ == "__main__":
    unittest.main()
