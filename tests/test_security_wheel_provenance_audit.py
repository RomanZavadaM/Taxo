# -*- coding: utf-8 -*-
"""Security audit utility tests. No external network or dependency installation."""
import json
import unittest
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("dependency_audit", ROOT / "scripts" / "audit_dependency_report.py")
audit = module_from_spec(spec)
spec.loader.exec_module(audit)


def report(filename="package-1.2.3-py3-none-any.whl", sha="a" * 64, url_prefix="https://files.pythonhosted.org/packages/"):
    return {"install": [{
        "metadata": {"name": "Package", "version": "1.2.3"},
        "download_info": {
            "url": url_prefix + filename,
            "archive_info": {"hashes": {"sha256": sha}},
        },
    }]}


class WheelProvenanceAuditTests(unittest.TestCase):
    def test_wheel_is_only_a_candidate_even_with_valid_hash(self):
        output = audit.audit_report(report())
        self.assertEqual(output[0]["name"], "package")
        self.assertEqual(output[0]["sha256"], "a" * 64)

    def test_missing_or_malformed_sha_is_rejected(self):
        for hash_value in ("", "not-a-hash", "f" * 63):
            with self.subTest(hash=hash_value):
                with self.assertRaises(ValueError):
                    audit.audit_report(report(sha=hash_value))

    def test_source_distribution_and_insecure_url_are_rejected(self):
        with self.assertRaises(ValueError):
            audit.audit_report(report(filename="package-1.2.3.tar.gz"))
        with self.assertRaises(ValueError):
            audit.audit_report(report(url_prefix="http://example.test/"))

    def test_duplicate_package_records_are_rejected(self):
        item = report()["install"][0]
        with self.assertRaises(ValueError):
            audit.audit_report({"install": [item, item]})

    def test_report_without_install_entries_is_rejected(self):
        with self.assertRaises(ValueError):
            audit.audit_report({"install": []})
        with self.assertRaises(ValueError):
            audit.audit_report({})


if __name__ == "__main__":
    unittest.main()
