# -*- coding: utf-8 -*-
"""Autonomous visual renderer for Taxo activity-attestation forms.

PDF/JPG generation intentionally does NOT depend on Microsoft Word,
LibreOffice or any other DOCX application at runtime. The static two-page
form is bundled as a PDF visual template derived from the official DOCX.
Taxo stamps only user-specific values and the selected activity.
"""
from pathlib import Path

def pdf_to_jpg_pages(pdf_path, page1_path, page2_path, dpi=180, quality=92):
    """Render the two attestation PDF pages to JPEG with PDFium.

    r9 intentionally avoids PyMuPDF/AGPL.  pypdfium2 is used only for the
    optional JPG export; ordinary PDF viewing is delegated to the OS/browser.
    """
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:
        raise RuntimeError(
            "Для створення JPG потрібен pypdfium2. Оновіть залежності через START.bat."
        ) from exc

    pdf_path = Path(pdf_path)
    page1_path = Path(page1_path)
    page2_path = Path(page2_path)
    page1_path.parent.mkdir(parents=True, exist_ok=True)
    page2_path.parent.mkdir(parents=True, exist_ok=True)

    pdf = pdfium.PdfDocument(str(pdf_path))
    try:
        if len(pdf) != 2:
            raise RuntimeError(f"Очікується 2 сторінки PDF, отримано: {len(pdf)}")
        scale = float(dpi) / 72.0
        for idx, target in ((0, page1_path), (1, page2_path)):
            page = pdf[idx]
            try:
                bitmap = page.render(scale=scale)
                try:
                    image = bitmap.to_pil()
                    image.save(str(target), format="JPEG", quality=int(quality))
                finally:
                    close = getattr(bitmap, "close", None)
                    if callable(close):
                        close()
            finally:
                close = getattr(page, "close", None)
                if callable(close):
                    close()
    finally:
        close = getattr(pdf, "close", None)
        if callable(close):
            close()
    return page1_path, page2_path


# ---------------------------------------------------------------------------
# v8.64 autonomous visual renderer
# ---------------------------------------------------------------------------
# PDF/JPG are intentionally independent from Microsoft Word / LibreOffice at
# runtime. The static two-page background is a PDF snapshot generated from the
# same official DOCX template during development. Taxo only stamps the variable
# fields and the selected activity onto that background.

_VISUAL_BASE_FONT_SIZE = 11.384199142456055


def _find_visual_font_files():
    """Return (regular, bold) system font files with Cyrillic support.

    We do NOT bundle fonts. On Windows the original DOCX font (Times New Roman)
    is preferred; Linux/macOS candidates exist for development and fallback.
    """
    import os
    regular_candidates = []
    bold_candidates = []
    if os.name == "nt":
        windir = Path(os.environ.get("WINDIR") or r"C:\Windows")
        fonts = windir / "Fonts"
        regular_candidates += [
            fonts / "times.ttf",       # Times New Roman
            fonts / "timesnewroman.ttf",
            fonts / "arial.ttf",
            fonts / "georgia.ttf",
            fonts / "cambria.ttc",
            fonts / "segoeui.ttf",
        ]
        bold_candidates += [
            fonts / "timesbd.ttf",     # Times New Roman Bold
            fonts / "timesnewromanbold.ttf",
            fonts / "arialbd.ttf",
            fonts / "georgiab.ttf",
            fonts / "cambriab.ttf",
            fonts / "segoeuib.ttf",
        ]
    regular_candidates += [
        Path("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
        Path("/usr/share/fonts/truetype/croscore/Tinos-Regular.ttf"),
        Path.home() / "Library/Fonts/Times New Roman.ttf",
        Path.home() / "Library/Fonts/Arial.ttf",
        Path("/Library/Fonts/Times New Roman.ttf"),
        Path("/Library/Fonts/Arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Times New Roman.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Times.ttc"),
    ]
    bold_candidates += [
        Path("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
        Path("/usr/share/fonts/truetype/croscore/Tinos-Bold.ttf"),
        Path.home() / "Library/Fonts/Times New Roman Bold.ttf",
        Path.home() / "Library/Fonts/Arial Bold.ttf",
        Path("/Library/Fonts/Times New Roman Bold.ttf"),
        Path("/Library/Fonts/Arial Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        Path("/System/Library/Fonts/Times.ttc"),
    ]
    regular = next((p for p in regular_candidates if p.exists()), None)
    bold = next((p for p in bold_candidates if p.exists()), None)
    if regular is None:
        raise RuntimeError(
            "Не знайдено системний шрифт з українськими літерами для PDF. "
            "На Windows очікується Times New Roman / Arial / Segoe UI."
        )
    if bold is None:
        bold = regular
    return regular, bold


def _fit_font_size(font_name, text, max_width, base_size=_VISUAL_BASE_FONT_SIZE, min_size=8.7):
    """Shrink only when a user value would leave its allotted line."""
    from reportlab.pdfbase import pdfmetrics

    text = str(text or "")
    if not text or max_width <= 0:
        return base_size
    try:
        width = pdfmetrics.stringWidth(text, font_name, base_size)
    except Exception:
        return base_size
    if width <= max_width:
        return base_size
    scaled = base_size * max_width / max(width, 1.0)
    return max(min_size, min(base_size, scaled))


def _stamp_attestation_visual(context, out_path, template_path):
    """Create PDF from the official background without PyMuPDF.

    ReportLab draws a transparent overlay and pypdf merges it over the fixed
    two-page official visual template.  Coordinates are the same calibrated
    top-left coordinates used by the previous renderer.
    """
    from io import BytesIO

    try:
        from pypdf import PdfReader, PdfWriter
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise RuntimeError(
            "Для формування PDF потрібні pypdf і reportlab. Оновіть залежності через START.bat."
        ) from exc

    template_path = Path(template_path)
    out_path = Path(out_path)
    if not template_path.exists():
        raise FileNotFoundError(f"Не знайдено візуальний шаблон PDF: {template_path}")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    regular_file, bold_file = _find_visual_font_files()
    regular_name = "TaxoAttReg"
    bold_name = "TaxoAttBold"
    registered = set(pdfmetrics.getRegisteredFontNames())
    if regular_name not in registered:
        pdfmetrics.registerFont(TTFont(regular_name, str(regular_file)))
    if bold_name not in registered:
        pdfmetrics.registerFont(TTFont(bold_name, str(bold_file)))

    reader = PdfReader(str(template_path))
    if len(reader.pages) != 2:
        raise RuntimeError(
            f"Візуальний шаблон Бланка має містити 2 сторінки, отримано: {len(reader.pages)}"
        )

    def value(key):
        return str(context.get(key) or "")

    def overlay_for(page_no, page_width, page_height):
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=(page_width, page_height))

        def y_from_top(y):
            return float(page_height) - float(y)

        def put(x, baseline, text, *, bold=True, max_width=None, size=None):
            text = str(text or "")
            if not text:
                return
            font_name = bold_name if bold else regular_name
            fs = float(size or _VISUAL_BASE_FONT_SIZE)
            if max_width is not None:
                fs = _fit_font_size(font_name, text, max_width, fs)
            c.setFillColorRGB(0, 0, 0)
            c.setFont(font_name, fs)
            c.drawString(float(x), y_from_top(baseline), text)

        def segment_width(text, bold, fs):
            font_name = bold_name if bold else regular_name
            return pdfmetrics.stringWidth(str(text or ""), font_name, fs)

        def line(x, baseline, parts, *, max_width=None):
            fs = float(_VISUAL_BASE_FONT_SIZE)
            if max_width:
                total = sum(segment_width(t, b, fs) for t, b in parts)
                if total > max_width:
                    fs = max(8.7, fs * max_width / max(total, 1.0))
            xx = float(x)
            for text, bold in parts:
                text = str(text or "")
                if not text:
                    continue
                put(xx, baseline, text, bold=bold, size=fs)
                xx += segment_width(text, bold, fs)
            return xx

        def erase(rect):
            x0, y0, x1, y1 = map(float, rect)
            c.setFillColorRGB(1, 1, 1)
            c.setStrokeColorRGB(1, 1, 1)
            c.rect(x0, page_height - y1, x1 - x0, y1 - y0, stroke=0, fill=1)

        simple = {
            0: {
                "company_name": [(62.40, 181.801, 488)],
                "company_address": [(62.40, 209.401, 488)],
                "phone": [(155.10, 237.001, 385)],
                "fax": [(139.05, 250.801, 400)],
                "email": [(162.55, 264.601, 380)],
                "signer_name": [(190.00, 292.201, 350)],
                "signer_position": [(188.25, 306.001, 350)],
                "driver_full": [(190.00, 333.601, 350)],
                "birth_date": [(158.90, 347.401, 180)],
                "period_from": [(204.05, 416.401, 330)],
                "period_to": [(210.95, 430.201, 325)],
            },
            1: {
                "company_name_en": [(186.55, 80.851, 355)],
                "company_address_en": [(62.40, 108.451, 480)],
                "phone": [(62.40, 152.401, 480)],
                "fax": [(62.40, 182.551, 480)],
                "email": [(143.35, 196.351, 400)],
                "signer_name_en": [(169.15, 223.951, 370)],
                "signer_position_en": [(195.55, 237.751, 345)],
                "driver_full_en": [(169.15, 265.351, 370)],
                "birth_date": [(62.40, 292.951, 220)],
                "license_number_en": [(305.30, 306.751, 235)],
                "employment": [(359.30, 320.551, 180)],
                "period_from": [(205.75, 348.151, 330)],
                "period_to": [(193.15, 361.951, 340)],
            },
        }
        for key, places in simple[page_no].items():
            for x, baseline, width in places:
                put(x, baseline, value(key), bold=True, max_width=width)

        if page_no == 0:
            erase((61.5, 349.7, 551.2, 392.0))
            line(62.40, 361.201, [
                ("10. Посвідчення водія: серія ", False),
                (value("license_series"), True),
                (" № ", False),
                (value("license_number"), True),
                (", видане ", False),
                (value("license_issue_date"), True),
            ], max_width=489)
            line(62.40, 375.001, [
                ("11. Почав працювати на підприємстві з ", False),
                (value("employment"), True),
                ("/серія водійського посвідчення ", False),
                (value("license_series"), True),
            ], max_width=489)
            line(62.40, 388.801, [
                ("№ ", False),
                (value("license_number"), True),
                (", виданого ", False),
                (value("license_issue_date"), True),
            ], max_width=489)

            erase((61.5, 529.4, 410.0, 543.6))
            line(62.40, 540.601, [
                ("20. Місце ", False), (value("director_place"), True),
                ("    Дата ", False), (value("form_date"), True),
            ], max_width=345)
            erase((41.5, 615.7, 390.0, 629.7))
            line(42.60, 626.801, [
                ("Місце ", False), (value("director_place"), True),
                ("    Дата ", False), (value("form_date"), True),
            ], max_width=345)
        else:
            erase((61.5, 463.9, 410.0, 477.8))
            line(62.40, 474.901, [
                ("20. Place ", False), (value("director_place_en"), True),
                ("    Date ", False), (value("form_date"), True),
            ], max_width=345)
            erase((41.5, 550.0, 390.0, 564.0))
            line(42.60, 561.101, [
                ("Place ", False), (value("director_place_en"), True),
                ("    Date ", False), (value("form_date"), True),
            ], max_width=345)

        boxes = {
            0: {
                14: (78.60, 433.20, 86.78, 447.62),
                15: (78.60, 447.00, 86.78, 461.42),
                16: (78.60, 460.80, 86.78, 475.22),
                17: (78.60, 474.60, 86.78, 489.02),
                18: (78.60, 502.20, 86.78, 516.62),
                19: (78.60, 516.00, 86.78, 530.42),
            },
            1: {
                14: (78.60, 364.95, 86.78, 379.37),
                15: (78.60, 378.75, 86.78, 393.17),
                16: (78.60, 392.55, 86.78, 406.97),
                17: (78.60, 406.35, 86.78, 420.77),
                18: (78.60, 436.50, 86.78, 450.92),
                19: (78.60, 450.30, 86.78, 464.72),
            },
        }
        activity = int(context.get("activity_no") or 16)
        if activity in range(14, 20):
            x0, y0, x1, y1 = boxes[page_no][activity]
            inset = 2.0
            c.setStrokeColorRGB(0, 0, 0)
            c.setLineWidth(1.0)
            c.line(
                x0 + inset, y_from_top(y0 + inset),
                x1 - inset, y_from_top(y1 - inset),
            )
            c.line(
                x0 + inset, y_from_top(y1 - inset),
                x1 - inset, y_from_top(y0 + inset),
            )

        c.save()
        packet.seek(0)
        return PdfReader(packet).pages[0]

    writer = PdfWriter()
    for page_no, page in enumerate(reader.pages):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        overlay = overlay_for(page_no, width, height)
        page.merge_page(overlay)
        writer.add_page(page)

    if out_path.exists():
        try:
            out_path.unlink()
        except OSError:
            pass
    with out_path.open("wb") as handle:
        writer.write(handle)
    return out_path


# Override the older programmatic/reportlab implementation. Existing callers
# keep the same function name while v8.64 uses the official visual background.
def build_attestation_pdf(context, out_path, template_path=None):
    if template_path is None:
        template_path = Path(__file__).resolve().parent / "attestation_visual_template.pdf"
    return _stamp_attestation_visual(context, out_path, template_path)
