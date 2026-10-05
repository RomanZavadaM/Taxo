# -*- coding: utf-8 -*-
"""Permissively licensed PDF engine for Taxo.

Taxo is proprietary software, therefore PDF handling uses only libraries with
permissive licenses (PROJECT_RULES.md §17):

* rendering / rasterization  -> pypdfium2 (Apache-2.0 / BSD-3-Clause, PDFium BSD-3)
* drawing text / shapes      -> reportlab (BSD)
* placing drawings on a page -> pypdf (BSD-3-Clause)

PyMuPDF (AGPL-3.0) is banned permanently and must never be reintroduced.

Coordinates passed to drawing callbacks use the top-left origin with y growing
downwards (points), the same convention the historical form layouts were
measured in. ``TopLeftCanvas`` converts them to the PDF bottom-left origin.
"""
from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path


class PdfEngineUnavailable(RuntimeError):
    """The PDF rendering engine cannot be loaded on this system."""


def _pdfium():
    try:
        import pypdfium2 as pdfium
    except Exception as exc:  # ImportError or a native-library load failure
        raise PdfEngineUnavailable(
            "Вбудований PDF-рушій недоступний на цьому комп'ютері. "
            "Документ можна відкрити системною програмою."
        ) from exc
    return pdfium


def pdf_engine_available():
    try:
        _pdfium()
    except PdfEngineUnavailable:
        return False
    return True


class PdfDocument:
    """Small read/render wrapper around a PDFium document."""

    def __init__(self, path):
        pdfium = _pdfium()
        self.path = Path(path)
        self._doc = pdfium.PdfDocument(str(self.path))

    def __len__(self):
        return len(self._doc)

    def page_size(self, index):
        page = self._doc[index]
        try:
            width, height = page.get_size()
        finally:
            page.close()
        return float(width), float(height)

    def render(self, index, scale):
        """Return the page as an RGB PIL image rendered at ``scale`` (1.0 = 72 dpi)."""
        page = self._doc[index]
        try:
            bitmap = page.render(scale=float(scale))
            try:
                image = bitmap.to_pil().convert("RGB")
            finally:
                bitmap.close()
        finally:
            page.close()
        return image

    def close(self):
        if self._doc is not None:
            self._doc.close()
            self._doc = None

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()


def render_pdf_pages(path, scale):
    """Yield every page of ``path`` as an RGB PIL image."""
    with PdfDocument(path) as doc:
        for index in range(len(doc)):
            yield doc.render(index, scale)


def register_ttf(font_file, prefix="TaxoFont"):
    """Register a TrueType/TrueType-collection file in reportlab once."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font_file = Path(font_file)
    digest = hashlib.sha1(str(font_file).encode("utf-8")).hexdigest()[:10]
    name = f"{prefix}-{digest}"
    if name not in pdfmetrics.getRegisteredFontNames():
        if font_file.suffix.lower() == ".ttc":
            pdfmetrics.registerFont(TTFont(name, str(font_file), subfontIndex=0))
        else:
            pdfmetrics.registerFont(TTFont(name, str(font_file)))
    return name


def text_width(text, font_name, size):
    from reportlab.pdfbase import pdfmetrics

    return pdfmetrics.stringWidth(str(text or ""), font_name, float(size))


class TopLeftCanvas:
    """reportlab canvas page addressed with top-left coordinates."""

    def __init__(self, canvas, height):
        self.c = canvas
        self.h = float(height)

    def text(self, x, baseline, value, font_name, size, color=(0, 0, 0)):
        self.c.setFillColorRGB(*color)
        self.c.setFont(font_name, float(size))
        self.c.drawString(float(x), self.h - float(baseline), str(value))

    def white_rect(self, x0, y0, x1, y1, line_width=1.0):
        # Same geometry as a filled + stroked white rectangle.
        self.c.setFillColorRGB(1, 1, 1)
        self.c.setStrokeColorRGB(1, 1, 1)
        self.c.setLineWidth(float(line_width))
        self.c.rect(float(x0), self.h - float(y1), float(x1) - float(x0), float(y1) - float(y0),
                    stroke=1, fill=1)

    def line(self, x0, y0, x1, y1, width=1.0, color=(0, 0, 0)):
        self.c.setStrokeColorRGB(*color)
        self.c.setLineWidth(float(width))
        self.c.line(float(x0), self.h - float(y0), float(x1), self.h - float(y1))


def stamp_pdf(source_path, out_path, draw_page):
    """Draw on top of every page of ``source_path`` and write ``out_path`` atomically.

    ``draw_page(tl_canvas, page_index, width, height)`` receives a
    ``TopLeftCanvas`` sized exactly like the source page.
    """
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas as rl_canvas

    source_path = Path(source_path)
    out_path = Path(out_path)
    reader = PdfReader(str(source_path))
    sizes = []
    for page in reader.pages:
        box = page.mediabox
        sizes.append((float(box.left), float(box.bottom), float(box.width), float(box.height)))

    overlay_buffer = io.BytesIO()
    canvas = rl_canvas.Canvas(overlay_buffer)
    for index, (_left, _bottom, width, height) in enumerate(sizes):
        canvas.setPageSize((width, height))
        draw_page(TopLeftCanvas(canvas, height), index, width, height)
        canvas.showPage()
    canvas.save()
    overlay_buffer.seek(0)
    overlay = PdfReader(overlay_buffer)

    writer = PdfWriter()
    for index, page in enumerate(reader.pages):
        left, bottom, _w, _h = sizes[index]
        stamp = overlay.pages[index]
        if left or bottom:
            from pypdf import Transformation

            page.merge_transformed_page(stamp, Transformation().translate(left, bottom))
        else:
            page.merge_page(stamp)
        writer.add_page(page)
    for page in writer.pages:
        page.compress_content_streams()
    try:
        writer.compress_identical_objects()
    except AttributeError:  # older pypdf on the Windows 7 line
        pass

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_name(out_path.name + ".taxo-tmp")
    with open(tmp_path, "wb") as handle:
        writer.write(handle)
    os.replace(tmp_path, out_path)
    return out_path
