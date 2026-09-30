import unittest
from pathlib import Path
import operations_orders as ops
ROOT=Path(__file__).resolve().parents[1]

class Taxo107R8Tests(unittest.TestCase):
    def test_every_order_type_has_exact_group(self):
        self.assertEqual(set(ops.ORDER_TYPE_LABELS),set(ops.ORDER_TYPE_GROUP))
        flattened=[]
        for group in ops.ORDER_GROUP_LABELS:
            flattened.extend(ops.ORDER_GROUP_TYPES[group])
        self.assertEqual(set(flattened),set(ops.ORDER_TYPE_LABELS))
        self.assertEqual(len(flattened),len(set(flattened)))

    def test_core_operations_groups_exist(self):
        self.assertIn(ops.TYPE_VEHICLE_ASSIGNMENT,ops.ORDER_GROUP_TYPES[ops.ORDER_GROUP_DRIVERS])
        self.assertIn(ops.TYPE_MAINTENANCE_REPAIR,ops.ORDER_GROUP_TYPES[ops.ORDER_GROUP_VEHICLES])
        self.assertIn(ops.TYPE_ROAD_SAFETY,ops.ORDER_GROUP_TYPES[ops.ORDER_GROUP_SAFETY])
        self.assertIn(ops.TYPE_FIRE_SAFETY,ops.ORDER_GROUP_TYPES[ops.ORDER_GROUP_SAFETY])

    def test_ui_has_group_filter_and_catalog(self):
        text=(ROOT/'operations_orders_ui.py').read_text(encoding='utf-8')
        self.assertIn('group_filter_var',text)
        self.assertIn('Каталог наказів',text)
        self.assertIn('Створити наказ за вибраним типом',text)
        self.assertNotIn('Розділ зарезервовано у контурі «Експлуатація»',text)

    def test_r8_identity(self):
        self.assertIn('APP_VERSION = "10.7-r8"',(ROOT/'v1078_features.py').read_text(encoding='utf-8'))
        self.assertIn('Taxo 10.7-r8',(ROOT/'docs/releases/RELEASE_NOTES_v10.7-r8.md').read_text(encoding='utf-8'))
        entry=(ROOT/'taxo_app.py').read_text(encoding='utf-8')
        self.assertIn('App = install_v1078(core, App)',entry)
        self.assertGreater(entry.index('App = install_v1078(core, App)'),entry.index('App = install_v1077(core, App)'))

if __name__=='__main__': unittest.main()
