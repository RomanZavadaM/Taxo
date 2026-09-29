# -*- coding: utf-8 -*-
"""Taxo 10.7-r5 — date-aware personnel scope for historical reports.

A person who is dismissed today must still appear in a report for a period in
which that person was employed.  The older report collectors first applied the
current ``employees.active`` flag and only then checked employment dates.  That
made historical P-5/timesheet reports lose people after their dismissal.

This compatibility layer changes report collection only.  Current-personnel UI
selectors keep their existing ``active=1`` behaviour.
"""
from __future__ import annotations

APP_VERSION = "10.7-r5"


def historical_report_active_only(_requested=True):
    """Return the storage-level filter for a date-aware historical report.

    Report collectors already call ``core.employee_employed_on`` for every
    report date.  Therefore they must load both currently active and inactive
    employees first; the date-aware employment predicate performs the actual
    period membership check afterwards.
    """
    return False


def install(core, base_app):
    if getattr(core, "_TAXO_V1075_INSTALLED", False):
        return base_app

    import personnel_v91 as personnel

    original_week = personnel.collect_personnel_week_balance
    original_audit = personnel.collect_personnel_timesheet_audit
    original_p5 = personnel.collect_p5_data

    def collect_personnel_week_balance(core_arg, anchor_date, active_only=True):
        return original_week(
            core_arg,
            anchor_date,
            active_only=historical_report_active_only(active_only),
        )

    def collect_personnel_timesheet_audit(core_arg, year, month, active_only=True):
        return original_audit(
            core_arg,
            year,
            month,
            active_only=historical_report_active_only(active_only),
        )

    def collect_p5_data(
        core_arg,
        year,
        month,
        active_only=True,
        use_plan_when_fact_missing=False,
    ):
        return original_p5(
            core_arg,
            year,
            month,
            active_only=historical_report_active_only(active_only),
            use_plan_when_fact_missing=use_plan_when_fact_missing,
        )

    # Patch the module globals used by the report UI and by PDF/XLSX exporters.
    # Do not patch _all_employee_rows: current UI selectors intentionally use
    # active=1 and must not start showing dismissed people.
    personnel.collect_personnel_week_balance = collect_personnel_week_balance
    personnel.collect_personnel_timesheet_audit = collect_personnel_timesheet_audit
    personnel.collect_p5_data = collect_p5_data

    core.APP_VERSION = APP_VERSION
    core._TAXO_V1075_INSTALLED = True
    return base_app
