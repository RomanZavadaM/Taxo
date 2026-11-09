# -*- coding: utf-8 -*-
"""10.14-r4: printed order format parity, real tables, appendix and preview route."""
import tempfile
import unittest
from pathlib import Path

import main
import operations_orders as ops
from docx import Document
from pypdf import PdfReader

from order_layout import order_layout
from order_document_formats import build_order_docx


class OrderLayoutR4Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir=Path(self.tmp.name)
        self.order={
            "order_no":"25",
            "order_date":"2026-11-08",
            "order_type":ops.TYPE_VEHICLE_ASSIGNMENT,
            "subject":"Про закріплення автотранспортних засобів",
            "preamble":"Для виконання виробничих завдань",
            "place":"с. Муроване",
            "body_text":"Цей текст не замінює таблицю",
        }
        self.company={
            "name":'Приватне підприємство "АТП - Завада"',
            "signer_position":"директор",
            "signer_name":"Завада Роман Михайлович",
        }
        self.drivers=[
            {
                "valid_from":"2026-11-08",
                "make_model":"БАЗ А079.04",
                "vehicle_name":"Автобус",
                "plate":"BC2884AA",
                "last_name":"Дробот",
                "first_name":"Олег",
                "middle_name":"Богданович",
            },
            {
                "valid_from":"2026-11-08",
                "make_model":"Mercedes",
                "vehicle_name":"Автобус",
                "plate":"BC1234AA",
                "last_name":"Петренко",
                "first_name":"Петро",
                "middle_name":"Іванович",
            },
        ]

    def test_version_and_start_module_guards(self):
        self.assertEqual(main.APP_VERSION,"10.14-r4")
        start=Path("START.bat").read_text(encoding="utf-8")
        for name in ("order_document_formats.py","order_layout.py","order_pdf_sections.py"):
            self.assertIn(name,start)

    def test_one_semantic_layout_drives_word_and_pdf(self):
        data=order_layout(
            ops,self.order,self.drivers,self.company,"Завада Тарас Йосипович"
        )
        self.assertEqual(data["number"],"№ 25")
        self.assertEqual(data["place"],"с. Муроване")
        self.assertEqual(len(data["assignment_rows"]),2)
        self.assertEqual(data["assignment_rows"][0][2],"BC2884AA")
        self.assertIn("згідно з наведеною таблицею",data["paragraphs"][0])

        docx=self.dir/"order.docx"
        pdf=self.dir/"order.pdf"
        build_order_docx(
            docx,ops,self.order,self.drivers,(),self.company,"Завада Тарас Йосипович"
        )
        ops.export_order_pdf(
            pdf,self.order,self.drivers,self.company,"Завада Тарас Йосипович"
        )
        self.assertTrue(docx.exists())
        self.assertTrue(pdf.exists())
        word=Document(docx)
        self.assertGreaterEqual(len(word.tables),3)
        meta=word.tables[0]
        self.assertIn("№ 25",meta.cell(0,1).text)
        self.assertIn("с. Муроване",meta.cell(0,2).text)
        assignment_table=word.tables[1]
        self.assertEqual(len(assignment_table.rows),3)
        self.assertEqual(
            [cell.text for cell in assignment_table.rows[0].cells],
            list(data["table_headers"]),
        )
        self.assertEqual(
            [cell.text for cell in assignment_table.rows[1].cells],
            list(data["assignment_rows"][0]),
        )
        self.assertEqual(
            [cell.text for cell in assignment_table.rows[2].cells],
            list(data["assignment_rows"][1]),
        )
        self.assertEqual(
            [cell.text for cell in word.tables[2].rows[0].cells],
            list(data["signature"]),
        )
        self.assertGreaterEqual(len(PdfReader(str(pdf)).pages),1)

    def test_generic_order_and_appendix_are_editable_in_docx(self):
        generic=dict(self.order)
        generic["order_type"]=ops.TYPE_GENERIC
        generic["body_text"]="1. Перевірити реєстри.\n2. Підготувати документи."
        target=self.dir/"generic.docx"
        build_order_docx(
            target,ops,generic,(),(),self.company,"",
            appendices=[{"sequence_no":1,"title":"Додаток про зміни",
                         "content":"Перший рядок\nДругий рядок"}],
        )
        word=Document(target)
        text="\n".join(p.text for p in word.paragraphs)
        self.assertIn("1. Перевірити реєстри.",text)
        self.assertIn("2. Підготувати документи.",text)
        self.assertIn("Додаток про зміни",text)
        self.assertIn("Перший рядок",text)

    def test_both_pdf_paths_and_order_preview_use_shared_layout(self):
        base=Path("src/taxo/operations_orders.py").read_text(encoding="utf-8")
        advanced=Path("src/taxo/v1073_features.py").read_text(encoding="utf-8")
        word=Path("src/taxo/order_document_formats.py").read_text(encoding="utf-8")
        ui=Path("src/taxo/operations_orders_ui.py").read_text(encoding="utf-8")
        self.assertIn("build_order_story(",base)
        self.assertIn("build_order_story(",advanced)
        self.assertIn("order_layout(",word)
        self.assertIn('matching_pdf=generated.get("pdf",())',ui)
        self.assertIn("open_order_format(core,paths,dlg,external=True)",ui)

if __name__=="__main__":
    unittest.main()
