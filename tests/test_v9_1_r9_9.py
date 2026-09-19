from datetime import date
import unittest

import taxo_app


class _LabelVar:
    def __init__(self):
        self.value = None

    def set(self, value):
        self.value = value


class _Tree:
    def __init__(self):
        self.rows = {}
        self._counter = 0

    def winfo_exists(self):
        return True

    def get_children(self):
        return list(self.rows.keys())

    def delete(self, item):
        self.rows.pop(item, None)

    def insert(self, _parent, _where, values):
        self._counter += 1
        iid = f"i{self._counter}"
        self.rows[iid] = tuple(values)
        return iid


def _waybill_row(driver, doctor, mechanic):
    return {
        "driver": driver,
        "route": "674 / Test",
        "vehicle": "BAZ / BC0000AA",
        "planned_departure": "07:55",
        "planned_return": "19:40",
        "odometer_start": None,
        "odometer_end": None,
        "planned_distance_km": 400,
        "doctor_1": doctor,
        "doctor_2": "",
        "mechanic_1": mechanic,
        "mechanic_2": "",
        "staff_conflicts": [],
        "work_hours": 8.5,
        "driving_hours": 7.5,
        "schedule_conflict": False,
        "schedule_conflict_minutes": 0,
        "waybill_no": "",
        "waybill_status": "",
        "waybill_revision": 0,
        "start_location": "АТП",
        "end_location": "АТП",
        "outbound_stop_count": 2,
        "return_stop_count": 2,
    }


class TestR99FinalRuntimeWaybillStaffInvariant(unittest.TestCase):
    def test_final_taxo_app_normalizes_two_different_rows_to_one_day_duty(self):
        app = object.__new__(taxo_app.App)
        app.waybill_tree = _Tree()
        app.waybill_date_label = _LabelVar()
        app.waybill_date = date(2026, 9, 20)
        app.waybill_rows = {}

        upstream_rows = [
            _waybill_row("Driver One", "Doctor A", "Mechanic A"),
            _waybill_row("Driver Two", "Doctor B", "Mechanic B"),
        ]
        canonical = {
            "doctor_1": "Doctor Canonical",
            "doctor_2": "",
            "mechanic_1": "Mechanic Canonical",
            "mechanic_2": "",
            "staff_conflicts": [],
        }

        app._waybill_schedule_rows = lambda _day: upstream_rows
        app._duty_staff_for_work_date = lambda _day: canonical

        taxo_app.App.refresh_waybill_issue_list(app)

        displayed = list(app.waybill_tree.rows.values())
        self.assertEqual(len(displayed), 2)
        self.assertEqual([row[6] for row in displayed], ["Doctor Canonical"] * 2)
        self.assertEqual([row[7] for row in displayed], ["Mechanic Canonical"] * 2)

        self.assertEqual(
            {row["doctor_1"] for row in app.waybill_rows.values()},
            {"Doctor Canonical"},
        )
        self.assertEqual(
            {row["mechanic_1"] for row in app.waybill_rows.values()},
            {"Mechanic Canonical"},
        )

    def test_runtime_method_is_on_final_taxo_app_class(self):
        self.assertTrue(hasattr(taxo_app.App, "refresh_waybill_issue_list"))
        self.assertTrue(hasattr(taxo_app.App, "_duty_staff_for_work_date"))


if __name__ == "__main__":
    unittest.main()
