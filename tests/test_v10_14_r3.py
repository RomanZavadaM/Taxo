# -*- coding: utf-8 -*-
"""10.14-r3 — unrestricted editing/removing auxiliary orders with audit."""
import sqlite3
from pathlib import Path
import unittest

import main
import operations_orders as ops
from order_edit_actions import delete_order
from v1098_orders_immutability import (
    ensure_schema_on_connection, update_order,
    set_paper_original_signed, approve_order, cancel_order,
)


class FreeOrderEditingR3Tests(unittest.TestCase):
    def setUp(self):
        self.con=sqlite3.connect(":memory:")
        self.con.row_factory=sqlite3.Row
        self.con.execute("PRAGMA foreign_keys=ON")
        self.con.executescript("""
        CREATE TABLE employees(
            id INTEGER PRIMARY KEY,last_name TEXT,first_name TEXT,middle_name TEXT,
            position TEXT,birth_date TEXT,actual_address TEXT,registered_address TEXT
        );
        CREATE TABLE vehicles(id INTEGER PRIMARY KEY,name TEXT,plate TEXT,make_model TEXT);
        CREATE TABLE employee_military_profile(
            employee_id INTEGER PRIMARY KEY,military_specialty TEXT,military_rank TEXT
        );
        INSERT INTO employees VALUES(1,'Іваненко','Іван','','Водій','','','');
        INSERT INTO vehicles VALUES(10,'Автобус','ВС0010АА','MAN');
        """)
        ensure_schema_on_connection(self.con)

    def tearDown(self):
        self.con.close()

    def make_order(self, number, status=ops.ORDER_DRAFT, signed=False):
        cursor=self.con.execute("""
          INSERT INTO operations_orders(
            order_type,order_no,order_date,place,subject,preamble,body_text,
            control_employee_id,status,approved_at,cancelled_at,note,
            paper_original_signed,paper_original_signed_at,created_at,updated_at
          ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,(ops.TYPE_GENERIC,str(number),"2026-11-09","","Перед виправленням","","",
             None,status,"2026-11-09" if status==ops.ORDER_APPROVED else "",
             "2026-11-09" if status==ops.ORDER_CANCELLED else "",
             "",1 if signed else 0,"2026-11-09" if signed else "","2026-11-09","2026-11-09"))
        return int(cursor.lastrowid)

    def test_version_and_package_guard(self):
        self.assertIn(main.APP_VERSION,("10.14-r3","10.14-r4","10.14-r5", "10.14-r6", "10.14-r7", "10.14-r8", "10.14-r9", "10.14-r10", "10.15-r1", "10.15-r2", "10.15-r3", "10.15-r4", "10.15-r5", "10.15-r7", "10.15-r8", "10.15-r9", "10.15-r10", "10.16-r1", "10.16-r2", "10.16-r3", "10.16-r4"))
        start=Path("START.bat").read_text(encoding="utf-8")
        self.assertIn("Taxo "+main.APP_VERSION,start)
        self.assertIn("order_edit_actions.py",start)

    def test_every_status_may_be_edited_and_deleted(self):
        for index,(status,signed) in enumerate((
            (ops.ORDER_DRAFT,False),(ops.ORDER_DRAFT,True),
            (ops.ORDER_APPROVED,False),(ops.ORDER_APPROVED,True),
            (ops.ORDER_CANCELLED,False),(ops.ORDER_CANCELLED,True),
        ),1):
            oid=self.make_order(index,status,signed)
            result=update_order(self.con,oid,subject="Виправлено %d" % index)
            self.assertEqual(result["subject"],"Виправлено %d" % index)
            old=delete_order(self.con,oid)
            self.assertEqual(old["order"]["subject"],"Виправлено %d" % index)
            self.assertIsNone(ops.get_order(self.con,oid))
            logs=self.con.execute(
              "SELECT before_json FROM operations_change_log "
              "WHERE entity_type='order' AND entity_id=? AND action='delete'",
              (oid,),
            ).fetchall()
            self.assertEqual(len(logs),1)

    def test_signature_is_reversible_even_after_approval(self):
        oid=self.make_order("7",ops.ORDER_APPROVED,True)
        unsigned=set_paper_original_signed(self.con,oid,False)
        self.assertEqual(unsigned["paper_original_signed"],0)
        signed=set_paper_original_signed(self.con,oid,True)
        self.assertEqual(signed["paper_original_signed"],1)

    def test_approval_after_cancel_is_allowed(self):
        oid=self.make_order("8",ops.ORDER_CANCELLED)
        again=approve_order(self.con,oid)
        self.assertEqual(again["status"],ops.ORDER_APPROVED)
        cancel_order(self.con,oid)
        self.assertEqual(ops.get_order(self.con,oid)["status"],ops.ORDER_CANCELLED)

    def test_delete_removes_own_links_but_preserves_master_cards(self):
        oid=self.make_order("9",ops.ORDER_APPROVED,True)
        self.con.execute("""
          INSERT INTO vehicle_driver_assignments(
            order_id,vehicle_id,employee_id,valid_from,valid_until,
            sequence_no,note,created_at,updated_at
          ) VALUES(?,?,?,?,?,?,?,?,?)
        """,(oid,10,1,"2026-11-09","",1,"","2026-11-09","2026-11-09"))
        deleted=delete_order(self.con,oid)
        self.assertEqual(len(deleted["assignments"]),1)
        self.assertEqual(self.con.execute(
          "SELECT count(*) FROM vehicle_driver_assignments WHERE order_id=?",(oid,)
        ).fetchone()[0],0)
        self.assertEqual(self.con.execute("SELECT count(*) FROM employees").fetchone()[0],1)
        self.assertEqual(self.con.execute("SELECT count(*) FROM vehicles").fetchone()[0],1)

    def test_ui_actions_exist_without_status_guard(self):
        source=Path("src/taxo/operations_orders_ui.py").read_text(encoding="utf-8")
        source+=Path("src/taxo/order_register_ui.py").read_text(encoding="utf-8")
        self.assertIn('"Видалити наказ"',source)
        self.assertIn('"Скасувати наказ"',source)
        self.assertIn('signed=not bool(',source)
        self.assertIn("def delete_selected_order():",source)
        self.assertNotIn("Затверджений або підписаний наказ незмінний",source)


if __name__=="__main__":
    unittest.main()
