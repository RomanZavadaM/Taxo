# -*- coding: utf-8 -*-
"""Taxo 10.7-r4 — editable order appendices with change history."""
from __future__ import annotations

import operations_orders as ops
import v1073_features as r3

APP_VERSION = "10.7-r4"


def _row_dict(row):
    if row is None:
        return {}
    try:
        return {key: row[key] for key in row.keys()}
    except Exception:
        return dict(row)


def install(core, base_app):
    if getattr(core, "_TAXO_1074_APPENDIX_HISTORY_INSTALLED", False):
        return base_app

    original_save = r3.save_appendix
    original_delete = r3.delete_appendix

    def save_appendix(con, order_id, *, title, content, note="", appendix_id=None, sequence_no=None):
        before = None
        if appendix_id:
            before = con.execute(
                "SELECT * FROM operations_order_appendices WHERE id=? AND order_id=?",
                (int(appendix_id), int(order_id)),
            ).fetchone()
        result = original_save(
            con,
            order_id,
            title=title,
            content=content,
            note=note,
            appendix_id=appendix_id,
            sequence_no=sequence_no,
        )
        after = con.execute(
            "SELECT * FROM operations_order_appendices WHERE id=? AND order_id=?",
            (int(result), int(order_id)),
        ).fetchone()
        ops._write_history(
            con,
            "appendix",
            int(result),
            "update" if before is not None else "create",
            _row_dict(before),
            _row_dict(after),
            "Виправлення додатка до наказу" if before is not None else "Створення додатка до наказу",
        )
        return result

    def delete_appendix(con, order_id, appendix_id):
        before = con.execute(
            "SELECT * FROM operations_order_appendices WHERE id=? AND order_id=?",
            (int(appendix_id), int(order_id)),
        ).fetchone()
        original_delete(con, order_id, appendix_id)
        if before is not None:
            ops._write_history(
                con,
                "appendix",
                int(appendix_id),
                "delete",
                _row_dict(before),
                {},
                "Видалення додатка до наказу",
            )

    r3.save_appendix = save_appendix
    r3.delete_appendix = delete_appendix
    core.APP_VERSION = APP_VERSION
    core._TAXO_1074_APPENDIX_HISTORY_INSTALLED = True
    return base_app
