# -*- coding: utf-8 -*-
"""Regression contract for the 10.18-r9 Windows binary security slice."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class WindowsBinaryGateR9Tests(unittest.TestCase):
    def test_revision_identity_is_r9(self):
        version = (ROOT / "VERSION.txt").read_text(encoding="utf-8").strip()
        main_source = (ROOT / "main.py").read_text(encoding="utf-8")
        self.assertEqual(version, "Version: 10.18-r9")
        self.assertIn('APP_VERSION = "10.18-r9"', main_source)

    def test_modern_windows_spec_explicitly_disables_upx(self):
        source = (ROOT / "packaging" / "Taxo.spec").read_text(encoding="utf-8")
        self.assertNotIn("upx=True", source)
        self.assertGreaterEqual(source.count("upx=False"), 2)

    def test_defender_gate_is_fail_closed_and_non_remediating(self):
        source = (ROOT / "scripts" / "windows_malware_gate.ps1").read_text(
            encoding="utf-8"
        )
        for marker in (
            "MpCmdRun.exe",
            "-SignatureUpdate",
            "-ScanType 3",
            "-DisableRemediation",
            "throw 'Microsoft Defender MpCmdRun.exe is unavailable",
        ):
            self.assertIn(marker, source)
        self.assertNotIn("Start-Process", source)

    def test_windows_workflow_scans_before_upload_and_rechecks_hashes(self):
        source = (
            ROOT / ".github" / "workflows" / "build-windows-v8.70.yml"
        ).read_text(encoding="utf-8")

        required = (
            "scripts/windows_malware_gate.ps1",
            "Record exact Windows build provenance",
            "BUILD_PROVENANCE_v${env:TAXO_CHECKSUM_STEM}_Windows_x64.txt",
            "Mandatory Microsoft Defender malware gate",
            "Verify package integrity after malware scan",
            "Taxo-Windows-x64-run-${{ github.run_id }}",
        )
        for marker in required:
            self.assertIn(marker, source)

        checksum = source.index("      - name: Create checksums")
        provenance = source.index("      - name: Record exact Windows build provenance")
        malware = source.index("      - name: Mandatory Microsoft Defender malware gate")
        integrity = source.index("      - name: Verify package integrity after malware scan")
        upload = source.index("      - name: Upload Windows test executables")
        self.assertLess(checksum, provenance)
        self.assertLess(provenance, malware)
        self.assertLess(malware, integrity)
        self.assertLess(integrity, upload)


if __name__ == "__main__":
    unittest.main()
