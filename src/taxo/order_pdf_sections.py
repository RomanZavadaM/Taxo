# -*- coding: utf-8 -*-
"""ReportLab rendering of Taxo's shared order layout.

Both ordinary orders and orders with appendices use this same base story.
"""
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from order_layout import order_layout


def build_order_story(ops, order, assignments, company, control_name,
                      font_name, normal, center, right, title, bold_center):
    layout = order_layout(ops, order, assignments, company, control_name)
    def para(value, style, bold=False):
        value = ops._ptext(value)
        if bold:
            value = "<b>%s</b>" % value
        return Paragraph(value, style)

    story = [
        para(layout["heading"], title, bold=True),
        para(layout["company"], center),
        Spacer(1, 7 * mm),
    ]
    meta = Table([[
        para(layout["date"], normal),
        para(layout["number"], center, bold=True),
        para(layout["place"], right),
    ]], colWidths=[55*mm, 55*mm, 55*mm])
    meta.setStyle(TableStyle([
        ("FONTNAME",(0,0),(-1,-1),font_name),
        ("FONTSIZE",(0,0),(-1,-1),11.5),
        ("ALIGN",(0,0),(0,0),"LEFT"),
        ("ALIGN",(1,0),(1,0),"CENTER"),
        ("ALIGN",(2,0),(2,0),"RIGHT"),
    ]))
    story.extend([meta, Spacer(1, 8*mm)])
    if layout["subject"]:
        story.extend([para(layout["subject"], normal, bold=True), Spacer(1, 5*mm)])
    if layout["preamble"]:
        story.extend([para(layout["preamble"], normal), Spacer(1, 6*mm)])
    story.extend([
        para(layout["instruction_heading"], bold_center, bold=True),
        Spacer(1, 5*mm),
    ])

    if layout["is_assignment"]:
        if layout["paragraphs"]:
            story.append(para(layout["paragraphs"][0], normal))
        data = [list(layout["table_headers"])]
        data.extend([list(row) for row in layout["assignment_rows"]])
        table = Table(data, colWidths=[10*mm,52*mm,38*mm,65*mm],repeatRows=1)
        table.setStyle(TableStyle([
            ("FONTNAME",(0,0),(-1,-1),font_name),
            ("FONTSIZE",(0,0),(-1,-1),10.5),
            ("GRID",(0,0),(-1,-1),0.45,colors.black),
            ("ALIGN",(0,0),(-1,0),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(-1,-1),3),
            ("RIGHTPADDING",(0,0),(-1,-1),3),
            ("TOPPADDING",(0,0),(-1,-1),3),
            ("BOTTOMPADDING",(0,0),(-1,-1),3),
        ]))
        story.extend([Spacer(1, 3*mm), table, Spacer(1, 5*mm)])
        for item in layout["paragraphs"][1:]:
            story.append(para(item, normal))
    else:
        for item in layout["paragraphs"]:
            story.extend([para(item, normal), Spacer(1, 2*mm)])

    story.append(Spacer(1, 15*mm))
    signature = Table([list(layout["signature"])],colWidths=[60*mm,45*mm,55*mm])
    signature.setStyle(TableStyle([
        ("FONTNAME",(0,0),(-1,-1),font_name),
        ("FONTSIZE",(0,0),(-1,-1),11.5),
        ("ALIGN",(0,0),(0,0),"LEFT"),
        ("ALIGN",(1,0),(1,0),"CENTER"),
        ("ALIGN",(2,0),(2,0),"RIGHT"),
    ]))
    story.append(signature)
    return story
