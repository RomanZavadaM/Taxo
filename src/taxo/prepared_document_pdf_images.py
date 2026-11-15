# -*- coding: utf-8 -*-
"""Safe inline-image extraction for prepared DOCX -> PDF rendering.

This slice intentionally supports inline pictures in the document body and
table cells. Floating drawings, VML/legacy pictures and header/footer drawings
remain fail-closed until their layout can be preserved deliberately.
"""
from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from PIL import Image as PillowImage

MAX_INLINE_IMAGES = 100
MAX_IMAGE_BLOB_BYTES = 32 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000
MAX_NORMALIZED_IMAGE_BYTES = 64 * 1024 * 1024
_EMU_PER_POINT = 12700.0


@dataclass(frozen=True)
class ParagraphFragment:
    kind: str
    value: object


def _local_name(element):
    return element.tag.rsplit("}", 1)[-1]


def _drawing_nodes(element):
    return element.xpath(".//w:drawing")


def ensure_supported_drawing_scope(document):
    """Reject drawing layouts this renderer cannot preserve faithfully yet."""
    if document.element.body.xpath(".//wp:anchor"):
        raise ValueError(
            "DOCX містить плаваюче зображення/об'єкт. "
            "Taxo поки переносить у PDF лише inline-зображення."
        )
    if document.element.body.xpath(".//w:pict"):
        raise ValueError(
            "DOCX містить legacy/VML-зображення. "
            "Для точного друку використайте Word."
        )

    seen_parts = set()
    for section in document.sections:
        for story in (
            section.header,
            section.first_page_header,
            section.even_page_header,
            section.footer,
            section.first_page_footer,
            section.even_page_footer,
        ):
            part = story.part
            key = str(getattr(part, "partname", id(part)))
            if key in seen_parts:
                continue
            seen_parts.add(key)
            element = story._element
            if element.xpath(".//w:drawing") or element.xpath(".//w:pict"):
                raise ValueError(
                    "DOCX містить зображення у колонтитулі. "
                    "Цей layout Taxo поки не переносить у PDF без втрат."
                )


def _extent_points(drawing, pixel_width, pixel_height):
    extents = drawing.xpath(".//wp:inline/wp:extent")
    if extents:
        try:
            width = int(extents[0].get("cx")) / _EMU_PER_POINT
            height = int(extents[0].get("cy")) / _EMU_PER_POINT
            if width > 0 and height > 0:
                return width, height
        except (TypeError, ValueError):
            pass
    # Conservative fallback when the DOCX extent is absent/malformed.
    return max(1.0, pixel_width * 0.75), max(1.0, pixel_height * 0.75)


def _normalize_image(blob):
    if not isinstance(blob, (bytes, bytearray)):
        raise ValueError("Некоректні дані зображення у DOCX")
    blob = bytes(blob)
    if not blob or len(blob) > MAX_IMAGE_BLOB_BYTES:
        raise ValueError("Зображення у DOCX має недопустимий розмір файла")

    try:
        with PillowImage.open(io.BytesIO(blob)) as image:
            width, height = image.size
            if (
                type(width) is not int
                or type(height) is not int
                or width < 1
                or height < 1
                or width * height > MAX_IMAGE_PIXELS
            ):
                raise ValueError("Зображення у DOCX має недопустимі розміри")
            image.load()
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGBA" if "transparency" in image.info else "RGB")
            output = io.BytesIO()
            image.save(output, format="PNG")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(
            "Вкладене зображення DOCX пошкоджене або має непідтриманий формат"
        ) from exc

    payload = output.getvalue()
    if not payload or len(payload) > MAX_NORMALIZED_IMAGE_BYTES:
        raise ValueError("Нормалізоване зображення для PDF завелике")
    return payload, width, height


def _image_fragment(drawing, part, image_budget, max_width_pt, max_height_pt):
    image_budget["count"] += 1
    if image_budget["count"] > MAX_INLINE_IMAGES:
        raise ValueError("DOCX містить забагато вкладених зображень")

    blips = drawing.xpath(".//a:blip")
    if len(blips) != 1:
        raise ValueError(
            "DOCX містить складний drawing-об'єкт, який Taxo поки не переносить у PDF"
        )
    blip = blips[0]
    if blip.get(qn("r:link")):
        raise ValueError(
            "DOCX містить зовнішнє посилання на зображення; "
            "Taxo не завантажує зовнішній вміст під час PDF-export."
        )
    rel_id = blip.get(qn("r:embed"))
    if not rel_id:
        raise ValueError("DOCX drawing не містить вбудованого зображення")
    try:
        related = part.related_parts[rel_id]
        blob = related.blob
    except Exception as exc:
        raise ValueError("Не вдалося прочитати вкладене зображення DOCX") from exc

    png, pixel_width, pixel_height = _normalize_image(blob)
    width, height = _extent_points(drawing, pixel_width, pixel_height)
    scale = min(
        1.0,
        float(max_width_pt) / width,
        float(max_height_pt) / height,
    )
    width *= scale
    height *= scale

    from reportlab.platypus import Image as PdfImage

    stream = io.BytesIO(png)
    flowable = PdfImage(stream, width=width, height=height)
    # ReportLab may load image data lazily; retain the stream with the flowable.
    flowable._taxo_source_stream = stream
    return flowable


def _text_from_run_element(run_element):
    result = []
    for child in run_element.iterchildren():
        local = _local_name(child)
        if local == "t":
            result.append(child.text or "")
        elif local == "tab":
            result.append("\t")
        elif local in ("br", "cr"):
            result.append("\n")
        elif local == "drawing":
            result.append(None)
        elif local == "pict":
            raise ValueError(
                "DOCX містить legacy/VML-зображення. Для точного друку використайте Word."
            )
    return result


def paragraph_fragments(
    paragraph,
    image_budget,
    *,
    max_width_pt,
    max_height_pt,
):
    """Return ordered text/image fragments for one Word paragraph."""
    drawings = _drawing_nodes(paragraph._p)
    legacy = paragraph._p.xpath(".//w:pict")
    if not drawings and not legacy:
        return [ParagraphFragment("text", paragraph.text or "")]
    if legacy:
        raise ValueError(
            "DOCX містить legacy/VML-зображення. Для точного друку використайте Word."
        )

    fragments = []
    text_buffer = []

    def flush_text():
        if text_buffer:
            fragments.append(
                ParagraphFragment("text", "".join(text_buffer))
            )
            text_buffer[:] = []

    def visit(container):
        for child in container.iterchildren():
            local = _local_name(child)
            if local == "r":
                for run_child in child.iterchildren():
                    run_local = _local_name(run_child)
                    if run_local == "t":
                        text_buffer.append(run_child.text or "")
                    elif run_local == "tab":
                        text_buffer.append("\t")
                    elif run_local in ("br", "cr"):
                        text_buffer.append("\n")
                    elif run_local == "drawing":
                        flush_text()
                        fragments.append(
                            ParagraphFragment(
                                "image",
                                _image_fragment(
                                    run_child,
                                    paragraph.part,
                                    image_budget,
                                    max_width_pt,
                                    max_height_pt,
                                ),
                            )
                        )
                    elif run_local == "pict":
                        raise ValueError(
                            "DOCX містить legacy/VML-зображення. "
                            "Для точного друку використайте Word."
                        )
            elif local == "hyperlink":
                visit(child)

    visit(paragraph._p)
    flush_text()
    return fragments


def apply_paragraph_image_alignment(flowable, paragraph):
    alignment = paragraph.alignment
    if alignment == WD_ALIGN_PARAGRAPH.CENTER:
        flowable.hAlign = "CENTER"
    elif alignment == WD_ALIGN_PARAGRAPH.RIGHT:
        flowable.hAlign = "RIGHT"
    else:
        flowable.hAlign = "LEFT"
    return flowable
