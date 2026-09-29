import unittest
from pathlib import Path
import operations_orders as ops
ROOT=Path(__file__).resolve().parents[1]
class Taxo107R7Tests(unittest.TestCase):
    def test_paragraph_text_is_escaped(self): self.assertEqual(ops._ptext('<b>A & B</b>'),'&lt;b&gt;A &amp; B&lt;/b&gt;')
    def test_operations_order_groups_are_present(self):
        required={ops.TYPE_ROAD_SAFETY,ops.TYPE_TECHNICAL_CONTROL,ops.TYPE_MAINTENANCE_REPAIR,ops.TYPE_ACCIDENT_COMMISSION,ops.TYPE_OCCUPATIONAL_SAFETY,ops.TYPE_FIRE_SAFETY}
        self.assertTrue(required.issubset(set(ops.ORDER_TYPE_LABELS)))
        for key in required: self.assertTrue(ops.DEFAULT_SUBJECTS[key]); self.assertTrue(ops.DEFAULT_PREAMBLES[key])
    def test_order_number_uses_paragraph(self):
        source=(ROOT/'operations_orders.py').read_text(encoding='utf-8')
        self.assertIn('Paragraph("<b>№ %s</b>" % _ptext(order["order_no"]), center)',source)
        self.assertNotIn('"<b>№ %s</b>" % str(order["order_no"] or "")',source)
    def test_r7_identity(self):
        self.assertIn('APP_VERSION = "10.7-r7"',(ROOT/'v1077_features.py').read_text(encoding='utf-8'))
        self.assertIn('App = install_v1077(core, App)',(ROOT/'taxo_app.py').read_text(encoding='utf-8'))
if __name__=='__main__': unittest.main()
