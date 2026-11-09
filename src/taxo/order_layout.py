# -*- coding: utf-8 -*-
"""One semantic layout for the printed order (editable DOCX and PDF).

Pure data: heading, metadata, paragraphs, assignment rows and signature.
The DOCX and PDF renderers choose page-flow only; they do not rewrite
the business wording separately. This module has no extra dependencies.
"""


def _value(row, key, default=""):
    if row is None:
        return default
    try:
        value = row[key]
        return default if value is None else value
    except (KeyError, IndexError, TypeError):
        return default


def _name(row):
    return " ".join(
        str(_value(row, key)).strip()
        for key in ("last_name", "first_name", "middle_name")
        if str(_value(row, key)).strip()
    )


def order_layout(ops, order, assignments=(), company=None, control_name=""):
    """Return identical text, table and signature content for every format."""
    company = company or {}
    company_name = str(company.get("name") or "").strip() or "Підприємство"
    signer_position = str(company.get("signer_position") or "").strip() or "Керівник"
    signer_name = str(company.get("signer_name") or "").strip()
    day = ops.display_day(_value(order, "order_date"))
    kind = str(_value(order, "order_type"))
    is_assignment = kind == ops.TYPE_VEHICLE_ASSIGNMENT
    paragraphs = []
    assignment_rows = []
    if is_assignment:
        first = assignments[0] if assignments else None
        start = ops.display_day(_value(first, "valid_from")) if first else day
        paragraphs.append(
            "1. Закріпити з %s транспортні засоби підприємства за водіями "
            "згідно з наведеною таблицею:" % start
        )
        for index, item in enumerate(assignments, 1):
            vehicle = str(_value(item, "make_model") or _value(item, "vehicle_name")).strip()
            assignment_rows.append((
                str(index), vehicle, str(_value(item, "plate")).strip(), _name(item)
            ))
    else:
        paragraphs.extend(
            p.strip() for p in str(_value(order, "body_text")).splitlines()
            if p.strip()
        )
    control = str(control_name or "").strip()
    if control:
        if is_assignment:
            paragraphs.append("2. Контроль за виконанням даного наказу покласти на %s." % control)
        else:
            paragraphs.append("Контроль за виконанням даного наказу покласти на %s." % control)
    return {
        "heading": "Н А К А З",
        "company": "по %s" % company_name,
        "date": day,
        "number": "№ %s" % str(_value(order, "order_no")).strip(),
        "place": str(_value(order, "place")).strip(),
        "subject": str(_value(order, "subject")).strip(),
        "preamble": str(_value(order, "preamble")).strip(),
        "instruction_heading": "Н А К А З У Ю:",
        "is_assignment": is_assignment,
        "table_headers": ("№", "Транспортний засіб", "Держ. номер", "Водій"),
        "assignment_rows": assignment_rows,
        "paragraphs": paragraphs,
        "signature": (signer_position, "________________", signer_name),
    }
