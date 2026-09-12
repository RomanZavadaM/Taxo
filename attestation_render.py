# -*- coding: utf-8 -*-
"""Autonomous visual renderer for Taxo activity-attestation forms.

PDF/JPG generation intentionally does NOT depend on Microsoft Word,
LibreOffice or any other DOCX application at runtime. The static two-page
form is bundled as a PDF visual template derived from the official DOCX.
Taxo stamps only user-specific values and the selected activity.
"""
from pathlib import Path

def pdf_to_jpg_pages(pdf_path, page1_path, page2_path, dpi=180, quality=92):
    """Render exactly the first two PDF pages to JPEG without Word/LibreOffice."""
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise RuntimeError(
            "Для JPG потрібен PyMuPDF. Оновіть залежності через START.bat."
        ) from exc

    pdf_path = Path(pdf_path)
    page1_path = Path(page1_path)
    page2_path = Path(page2_path)
    page1_path.parent.mkdir(parents=True, exist_ok=True)
    page2_path.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    try:
        if len(doc) != 2:
            raise RuntimeError(f"Очікується 2 сторінки PDF, отримано: {len(doc)}")
        matrix = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        for idx, target in ((0, page1_path), (1, page2_path)):
            pix = doc[idx].get_pixmap(matrix=matrix, alpha=False)
            pix.save(str(target), output="jpeg", jpg_quality=int(quality))
    finally:
        doc.close()
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
        Path("/Library/Fonts/Times New Roman.ttf"),
        Path("/System/Library/Fonts/Times.ttc"),
    ]
    bold_candidates += [
        Path("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
        Path("/usr/share/fonts/truetype/croscore/Tinos-Bold.ttf"),
        Path("/Library/Fonts/Times New Roman Bold.ttf"),
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


def _fit_font_size(font, text, max_width, base_size=_VISUAL_BASE_FONT_SIZE, min_size=8.7):
    """Shrink only when a user value would leave its allotted line."""
    text = str(text or "")
    if not text or max_width <= 0:
        return base_size
    try:
        width = font.text_length(text, fontsize=base_size)
    except Exception:
        return base_size
    if width <= max_width:
        return base_size
    scaled = base_size * max_width / max(width, 1.0)
    return max(min_size, min(base_size, scaled))


def _stamp_attestation_visual(context, out_path, template_path):
    """Create PDF from the fixed official-form background + variable values.

    No office package is started. The template already contains all static
    formatting, borders, headings and notes. Only data fields are stamped.
    """
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("Для PDF/JPG потрібен PyMuPDF. Оновіть залежності Taxo.") from exc

    template_path = Path(template_path)
    out_path = Path(out_path)
    if not template_path.exists():
        raise FileNotFoundError(f"Не знайдено візуальний шаблон PDF: {template_path}")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    regular_file, bold_file = _find_visual_font_files()
    doc = fitz.open(str(template_path))
    if len(doc) != 2:
        doc.close()
        raise RuntimeError(f"Візуальний шаблон Бланка має містити 2 сторінки, отримано: {len(doc)}")

    try:
        for page in doc:
            page.insert_font(fontname="TaxoAttReg", fontfile=str(regular_file))
            page.insert_font(fontname="TaxoAttBold", fontfile=str(bold_file))
        font_regular = fitz.Font(fontfile=str(regular_file))
        font_bold = fitz.Font(fontfile=str(bold_file))

        def value(key):
            return str(context.get(key) or "")

        def put(page_no, x, baseline, text, *, bold=True, max_width=None, size=None):
            page = doc[page_no]
            text = str(text or "")
            if not text:
                return
            font = font_bold if bold else font_regular
            fs = size or _VISUAL_BASE_FONT_SIZE
            if max_width is not None:
                fs = _fit_font_size(font, text, max_width, fs)
            page.insert_text(
                (float(x), float(baseline)), text,
                fontsize=float(fs),
                fontname="TaxoAttBold" if bold else "TaxoAttReg",
                color=(0, 0, 0), overlay=True,
            )

        def segment_width(text, bold, fs):
            font = font_bold if bold else font_regular
            return font.text_length(str(text or ""), fontsize=fs)

        def line(page_no, x, baseline, parts, *, max_width=None):
            fs = _VISUAL_BASE_FONT_SIZE
            if max_width:
                total = sum(segment_width(t, b, fs) for t, b in parts)
                if total > max_width:
                    fs = max(8.7, fs * max_width / max(total, 1.0))
            xx = float(x)
            for text, bold in parts:
                text = str(text or "")
                if not text:
                    continue
                put(page_no, xx, baseline, text, bold=bold, size=fs)
                xx += segment_width(text, bold, fs)
            return xx

        def erase(page_no, rect):
            # Keep the official frame itself untouched: rectangles stay inside
            # the table border and cover only the line being rebuilt.
            page = doc[page_no]
            page.draw_rect(fitz.Rect(*rect), color=(1, 1, 1), fill=(1, 1, 1), overlay=True)

        # Stable one-value positions measured from the same DOCX visual template.
        simple = {
            "company_name": [(0, 62.40, 181.801, 488)],
            "company_address": [(0, 62.40, 209.401, 488)],
            "phone": [(0, 155.10, 237.001, 385), (1, 62.40, 152.401, 480)],
            "fax": [(0, 139.05, 250.801, 400), (1, 62.40, 182.551, 480)],
            "email": [(0, 162.55, 264.601, 380), (1, 143.35, 196.351, 400)],
            "signer_name": [(0, 190.00, 292.201, 350)],
            "signer_position": [(0, 188.25, 306.001, 350)],
            "driver_full": [(0, 190.00, 333.601, 350)],
            "birth_date": [(0, 158.90, 347.401, 180), (1, 62.40, 292.951, 220)],
            "period_from": [(0, 204.05, 416.401, 330), (1, 205.75, 348.151, 330)],
            "period_to": [(0, 210.95, 430.201, 325), (1, 193.15, 361.951, 340)],
            "company_name_en": [(1, 186.55, 80.851, 355)],
            "company_address_en": [(1, 62.40, 108.451, 480)],
            "signer_name_en": [(1, 169.15, 223.951, 370)],
            "signer_position_en": [(1, 195.55, 237.751, 345)],
            "driver_full_en": [(1, 169.15, 265.351, 370)],
            "license_number_en": [(1, 305.30, 306.751, 235)],
            "employment": [(1, 359.30, 320.551, 180)],
        }
        for key, places in simple.items():
            for page_no, x, baseline, width in places:
                put(page_no, x, baseline, value(key), bold=True, max_width=width)

        # Ukrainian composite driving-licence lines. Blank background has the
        # static suffixes collapsed, so rebuild these lines completely.
        erase(0, (61.5, 349.7, 551.2, 392.0))
        line(0, 62.40, 361.201, [
            ("10. Посвідчення водія: серія ", False),
            (value("license_series"), True),
            (" № ", False),
            (value("license_number"), True),
            (", видане ", False),
            (value("license_issue_date"), True),
        ], max_width=489)
        line(0, 62.40, 375.001, [
            ("11. Почав працювати на підприємстві з ", False),
            (value("employment"), True),
            ("/серія водійського посвідчення ", False),
            (value("license_series"), True),
        ], max_width=489)
        line(0, 62.40, 388.801, [
            ("№ ", False),
            (value("license_number"), True),
            (", виданого ", False),
            (value("license_issue_date"), True),
        ], max_width=489)

        # Places and form date: redraw the whole line so "Date" follows the
        # actual place width just as it does in the DOCX.
        erase(0, (61.5, 529.4, 410.0, 543.6))
        line(0, 62.40, 540.601, [
            ("20. Місце ", False), (value("director_place"), True),
            ("    Дата ", False), (value("form_date"), True),
        ], max_width=345)
        erase(0, (41.5, 615.7, 390.0, 629.7))
        line(0, 42.60, 626.801, [
            ("Місце ", False), (value("director_place"), True),
            ("    Дата ", False), (value("form_date"), True),
        ], max_width=345)

        erase(1, (61.5, 463.9, 410.0, 477.8))
        line(1, 62.40, 474.901, [
            ("20. Place ", False), (value("director_place_en"), True),
            ("    Date ", False), (value("form_date"), True),
        ], max_width=345)
        erase(1, (41.5, 550.0, 390.0, 564.0))
        line(1, 42.60, 561.101, [
            ("Place ", False), (value("director_place_en"), True),
            ("    Date ", False), (value("form_date"), True),
        ], max_width=345)

        # Selected activity: the empty square is already part of the official
        # template. Draw only the two diagonals inside it.
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
            for page_no in (0, 1):
                r = fitz.Rect(*boxes[page_no][activity])
                inset = 2.0
                doc[page_no].draw_line(
                    (r.x0 + inset, r.y0 + inset), (r.x1 - inset, r.y1 - inset),
                    color=(0, 0, 0), width=1.0, overlay=True,
                )
                doc[page_no].draw_line(
                    (r.x0 + inset, r.y1 - inset), (r.x1 - inset, r.y0 + inset),
                    color=(0, 0, 0), width=1.0, overlay=True,
                )

        if out_path.exists():
            try:
                out_path.unlink()
            except OSError:
                pass
        doc.save(str(out_path), garbage=4, deflate=True)
    finally:
        doc.close()
    return out_path


# Override the older programmatic/reportlab implementation. Existing callers
# keep the same function name while v8.64 uses the official visual background.
def build_attestation_pdf(context, out_path, template_path=None):
    if template_path is None:
        template_path = Path(__file__).resolve().parent / "attestation_visual_template.pdf"
    return _stamp_attestation_visual(context, out_path, template_path)
