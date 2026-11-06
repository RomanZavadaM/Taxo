# -*- coding: utf-8 -*-
"""Taxo 10.11-r5 — dependency security and Win7 pypdf mitigation."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import unittest

from pdf_engine import PdfSecurityLimitError, secure_pypdf_reader

ROOT = Path(__file__).resolve().parents[1]


def page_entry_bomb_pdf(repeats=4, extra_keys=12):
    keys = b"".join(
        (b" /K%d 0" % index) for index in range(int(extra_keys))
    )
    leaf = b"<< /Type /Page /MediaBox [0 0 9 9]" + keys + b" >>"
    kids = b" ".join(b"3 0 R" for _ in range(int(repeats)))
    pages = b"<< /Type /Pages /Kids [" + kids + b"] /Count %d >>" % int(repeats)
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        pages,
        leaf,
    ]

    data = bytearray(b"%PDF-1.7\n")
    offsets = []
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(data))
        data += b"%d 0 obj\n" % number + obj + b"\nendobj\n"

    xref_offset = len(data)
    data += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for offset in offsets:
        data += b"%010d 00000 n \n" % offset
    data += (
        b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
        % (len(objects) + 1, xref_offset)
    )
    return bytes(data)


class DependencyPinsR5Tests(unittest.TestCase):
    def test_main_line_uses_patched_pillow_and_pypdf(self):
        text = (ROOT / "requirements.txt").read_text("utf-8")
        self.assertIn("Pillow==13.0.0", text)
        self.assertIn("pypdf==6.21.4", text)
        self.assertNotIn("Pillow==11.3.0", text)
        self.assertNotIn("pypdf==6.19.0", text)

    def test_win7_keeps_python38_line_with_explicit_mitigation(self):
        text = (ROOT / "requirements-win7.txt").read_text("utf-8")
        self.assertIn("CPython 3.8.10", text)
        self.assertIn("Pillow==10.4.0", text)
        self.assertIn("pypdf==5.9.0", text)
        self.assertIn("page-tree entry-budget mitigation", text)


class PdfPageTreeSecurityR5Tests(unittest.TestCase):
    def test_normal_internal_pdf_passes_security_preflight(self):
        template = ROOT / "assets" / "attestation_visual_template.pdf"
        reader = secure_pypdf_reader(str(template), max_page_entries=1000)
        try:
            self.assertEqual(len(reader.pages), 2)
        finally:
            close = getattr(reader, "close", None)
            if callable(close):
                close()

    def test_repeated_heavy_leaf_is_rejected_before_flattening(self):
        payload = page_entry_bomb_pdf(repeats=4, extra_keys=12)
        with self.assertRaisesRegex(PdfSecurityLimitError, "безпечний ліміт"):
            secure_pypdf_reader(BytesIO(payload), max_page_entries=20)

    def test_runtime_attestation_reader_uses_security_preflight(self):
        source = (ROOT / "src" / "taxo" / "attestation_render.py").read_text("utf-8")
        self.assertIn("secure_pypdf_reader", source)
        self.assertNotIn("from pypdf import PdfReader", source)


if __name__ == "__main__":
    unittest.main()
