# -*- coding: utf-8 -*-
"""10.15-r2 — practical editable safety briefing and order templates."""
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import main
import safety_instructions_ui as brief
import safety_templates as templates

ROOT = Path(__file__).resolve().parents[1]


class SafetyTemplateR2Tests(unittest.TestCase):
    def test_r2_identity_and_start_guard(self):
        self.assertIn(main.APP_VERSION, ("10.15-r2", "10.15-r3", "10.15-r4", "10.15-r5", "10.15-r7", "10.15-r8", "10.15-r9", "10.15-r10"))
        self.assertIn("Version: " + main.APP_VERSION, (ROOT / "VERSION.txt").read_text("utf-8"))
        start=(ROOT / "START.bat").read_text("utf-8")
        self.assertIn("Taxo " + main.APP_VERSION, start)
        self.assertIn("safety_templates.py", start)

    def test_template_ids_are_unique_and_stable(self):
        briefing_ids=[row["id"] for row in templates.BRIEFING_TEMPLATES]
        self.assertEqual(len(briefing_ids),len(set(briefing_ids)))
        order_ids=[
            row["id"]
            for rows in templates.ORDER_TEXT_PRESETS.values()
            for row in rows
        ]
        self.assertEqual(len(order_ids),len(set(order_ids)))

    def test_every_visible_briefing_kind_has_a_ready_editable_template(self):
        for direction,kinds in brief.BRIEFING_KINDS.items():
            for kind in kinds:
                rows=templates.templates_for(direction,kind)
                self.assertTrue(rows, (direction,kind))
                for row in rows:
                    self.assertTrue(row["topic"].strip(), row["id"])
                    self.assertTrue(row["program"].strip(), row["id"])
                    self.assertTrue(row["source_note"].strip(), row["id"])

    def test_bus_seasonal_bdr_programs_are_present_and_winter_is_substantive(self):
        periodic={row["id"]:row for row in templates.templates_for("БДР","Періодичний (повторний)")}
        self.assertIn("bdr_autumn_winter_bus", periodic)
        self.assertIn("bdr_spring_summer_bus", periodic)
        winter=(periodic["bdr_autumn_winter_bus"]["topic"]+"\n"+periodic["bdr_autumn_winter_bus"]["program"]).lower()
        for marker in (
            "ожелед", "дистанц", "склоочис", "опален", "двер",
            "пасажир", "залізнич", "не «наздоганяти графік",
        ):
            self.assertIn(marker, winter)

    def test_occupational_safety_library_covers_intro_primary_repeat_unplanned_target(self):
        by_kind={
            kind:{row["id"] for row in templates.templates_for("Охорона праці",kind)}
            for kind in brief.BRIEFING_KINDS["Охорона праці"]
        }
        self.assertIn("osh_intro_all", by_kind["Вступний"])
        self.assertIn("osh_primary_driver_bus", by_kind["Первинний"])
        self.assertIn("osh_repeat_driver", by_kind["Повторний"])
        self.assertIn("osh_unplanned", by_kind["Позаплановий"])
        self.assertIn("osh_target", by_kind["Цільовий"])

    def test_preparation_csv_keeps_program_source_and_people_but_not_completion_claim(self):
        row=templates.template_by_id("bdr_autumn_winter_bus")
        prepared=brief.prepare_list(
            "БДР","Періодичний (повторний)","09.11.2026",
            row["topic"],["Тестовий Водій"],
            people_records=[{"id":17,"name":"Тестовий Водій","personnel_no":"017"}],
            program_text=row["program"],template_id=row["id"],source_note=row["source_note"],
        )
        self.assertNotIn("conducted", prepared)
        self.assertNotIn("signed", prepared)
        with TemporaryDirectory() as directory:
            target=Path(directory)/"winter.csv"
            brief.write_preparation_csv(target,prepared)
            with target.open("r",encoding="utf-8-sig",newline="") as stream:
                rows=list(csv.reader(stream,delimiter=";"))
        flattened="\n".join(";".join(r) for r in rows)
        self.assertIn("bdr_autumn_winter_bus", flattened)
        self.assertIn("осінньо-зим", flattened.lower())
        self.assertIn("ожелед", flattened.lower())
        self.assertIn("Тестовий Водій", flattened)
        self.assertIn("017", flattened)
        self.assertIn("Код Taxo", flattened)
        self.assertNotIn("проведено;", flattened.lower())
        self.assertNotIn("підписано;", flattened.lower())

    def test_order_presets_cover_bdr_osh_training_and_bus_seasons(self):
        road={row["id"]:row for row in templates.order_presets("road_safety")}
        osh={row["id"]:row for row in templates.order_presets("occupational_safety")}
        training={row["id"]:row for row in templates.order_presets("safety_training")}
        seasonal={row["id"]:row for row in templates.order_presets("seasonal_operation")}
        for key in ("order_bdr_system","order_bdr_winter_bus","order_bdr_summer_bus","order_bdr_special_weather"):
            self.assertIn(key,road)
        for key in ("order_osh_system","order_osh_repeat","order_osh_unplanned","order_osh_target"):
            self.assertIn(key,osh)
        self.assertIn("order_safety_programs",training)
        self.assertIn("order_seasonal_winter_bus",seasonal)
        self.assertIn("order_seasonal_summer_bus",seasonal)
        for library in (road,osh,training,seasonal):
            for row in library.values():
                self.assertTrue(row["subject"].strip())
                self.assertTrue(row["preamble"].strip())
                self.assertGreater(len(row["body"].strip()),150)

    def test_live_sources_expose_template_selection_and_editing_controls(self):
        instructions=(ROOT/"src"/"taxo"/"safety_instructions_ui.py").read_text("utf-8")
        orders=(ROOT/"src"/"taxo"/"operations_orders_ui.py").read_text("utf-8")
        orders+=(ROOT/"src"/"taxo"/"order_editor_ui.py").read_text("utf-8")
        for marker in (
            "Типова заготовка","Текст програми…",
            "_taxo_briefing_template_box","_taxo_briefing_program_var",
        ):
            self.assertIn(marker,instructions)
        for marker in (
            "Типова заготовка","Вставити заготовку",
            "_taxo_order_preset_box","ORDER_TEXT_PRESETS",
        ):
            self.assertIn(marker,orders)


if __name__=="__main__":
    unittest.main()
