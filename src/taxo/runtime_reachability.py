# -*- coding: utf-8 -*-
"""Strict runtime reachability gate for critical Taxo UI routes.

A critical route is not preserved merely because a label/callback exists in
source. Its live test must prove that the action is mapped, physically on-screen,
usable and activatable.
"""
from __future__ import annotations

from functools import wraps
import importlib
from threading import local

MANDATORY_RUNTIME_CHECKS = frozenset(("mapped", "onscreen", "usable", "activation"))

RUNTIME_ROUTE_TEST_MODULES = {
    "personnel.data_center": "test_function_reachability_r2",
    "personnel.registry_import": "test_v10_12_r6",
    "personnel.working_data": "test_v10_12_r6",
    "personnel.card_documents": "test_v10_12_r6",
    "personnel.document_register": "test_v10_12_r6",
    "personnel.simple_month_schedule": "test_function_reachability_r2",
    "personnel.document_control": "test_v10_12_r6",
    "personnel.registry_bulk": "test_v10_12_r6",
    "personnel.diia_cycle": "test_v10_12_r6",
    "personnel.military": "test_v10_12_r6",
    "personnel.bulk_replan": "test_v10_12_r5",
    "drivers.report_selection": "test_v10_12_r9",
    "timesheet.plan_to_fact": "test_v10_12_r10",
    "vehicles.core": "test_v10_8_r2",
    "vehicles.military": "test_function_reachability_r2",
    "vehicles.military.statement": "test_v10_12_r4",
    "operations.center": "test_v10_12_r4",
    "operations.assignment_bulk": "test_v10_14_r6",
    "operations.instructions": "test_v10_14_r7",
    "maintenance.stoir": "test_function_reachability_r2",
    "documents.center": "test_v10_12_r7",
    "waybills.actions": "test_v10_12_r5",
    "tachograph.main": "test_v10_12_r8",
    "reports.home": "test_v10_12_r8",
    "settings.main": "test_v10_12_r8",
}

_registered_tests = {}
_state = local()


def _evidence():
    value = getattr(_state, "evidence", None)
    if value is None:
        raise AssertionError("Reachability evidence recorded outside @runtime_routes test")
    return value


def _record(route_id, *checks):
    evidence = _evidence()
    if route_id not in evidence:
        raise AssertionError("Runtime route %r is not declared by this test" % (route_id,))
    evidence[route_id].update(checks)


def runtime_routes(*route_ids):
    """Declare exactly which critical routes one live test proves."""
    route_ids = tuple(route_ids)
    if not route_ids or len(route_ids) != len(set(route_ids)):
        raise RuntimeError("runtime_routes requires unique route ids")

    def decorate(func):
        test_id = "%s.%s" % (func.__module__, func.__qualname__)
        for route_id in route_ids:
            previous = _registered_tests.get(route_id)
            if previous and previous != test_id:
                raise RuntimeError(
                    "Runtime route %s registered by both %s and %s" %
                    (route_id, previous, test_id)
                )
            _registered_tests[route_id] = test_id

        @wraps(func)
        def wrapped(*args, **kwargs):
            previous = getattr(_state, "evidence", None)
            _state.evidence = {route_id: set() for route_id in route_ids}
            try:
                result = func(*args, **kwargs)
                missing = {
                    route_id: sorted(MANDATORY_RUNTIME_CHECKS - checks)
                    for route_id, checks in _state.evidence.items()
                    if MANDATORY_RUNTIME_CHECKS - checks
                }
                if missing:
                    raise AssertionError(
                        "Runtime reachability proof incomplete: %r" % (missing,)
                    )
                return result
            finally:
                _state.evidence = previous

        wrapped._taxo_runtime_routes = route_ids
        return wrapped
    return decorate


def _update_geometry(widget):
    try:
        top = widget.winfo_toplevel()
        top.update_idletasks()
    except Exception:
        pass


def _state_is_usable(widget):
    try:
        state = widget.state()
        if "disabled" in state:
            return False
    except Exception:
        pass
    try:
        value = str(widget.cget("state"))
        if value.lower() == "disabled":
            return False
    except Exception:
        pass
    return True


def assert_widget_reachable(widget, route_id, container=None, tolerance=2):
    """Prove a live widget is mapped, non-zero, on-screen and usable."""
    if widget is None:
        raise AssertionError("%s: widget is missing" % route_id)
    try:
        if not widget.winfo_exists():
            raise AssertionError("%s: widget no longer exists" % route_id)
    except Exception as exc:
        if isinstance(exc, AssertionError):
            raise
        raise AssertionError("%s: widget existence cannot be verified" % route_id)

    _update_geometry(widget)
    if not widget.winfo_ismapped():
        raise AssertionError("%s: widget exists but is not mapped" % route_id)
    width = int(widget.winfo_width())
    height = int(widget.winfo_height())
    if width <= 1 or height <= 1:
        raise AssertionError("%s: widget has no usable size (%sx%s)" % (route_id, width, height))
    _record(route_id, "mapped")

    top = widget.winfo_toplevel()
    boundary = container
    wx1, wy1 = int(widget.winfo_rootx()), int(widget.winfo_rooty())
    wx2, wy2 = wx1 + width, wy1 + height
    if boundary is None and widget is top:
        # A separate dialog only needs to be reachable on the screen; it does
        # not have to stay inside the parent application's rectangle.
        bx1, by1 = 0, 0
        bx2, by2 = int(widget.winfo_screenwidth()), int(widget.winfo_screenheight())
    else:
        boundary = boundary or top
        _update_geometry(boundary)
        bx1, by1 = int(boundary.winfo_rootx()), int(boundary.winfo_rooty())
        bx2 = bx1 + int(boundary.winfo_width())
        by2 = by1 + int(boundary.winfo_height())
    if (wx1 < bx1 - tolerance or wy1 < by1 - tolerance or
            wx2 > bx2 + tolerance or wy2 > by2 + tolerance):
        raise AssertionError(
            "%s: widget is outside accessible bounds widget=%r container=%r" %
            (route_id, (wx1, wy1, wx2, wy2), (bx1, by1, bx2, by2))
        )
    _record(route_id, "onscreen")

    if not _state_is_usable(widget):
        raise AssertionError("%s: widget is disabled" % route_id)
    _record(route_id, "usable")
    return widget


def activate_widget(widget, route_id, container=None):
    """Reach and activate a widget, recording activation only after success."""
    assert_widget_reachable(widget, route_id, container=container)
    invoke = getattr(widget, "invoke", None)
    if callable(invoke):
        result = invoke()
    else:
        binding = widget.bind("<Button-1>")
        if not binding:
            raise AssertionError("%s: widget has no invokable action" % route_id)
        widget.event_generate("<Button-1>", x=1, y=1)
        result = None
    _record(route_id, "activation")
    return result


def mark_activation(route_id):
    _record(route_id, "activation")


def registered_runtime_routes():
    return dict(_registered_tests)


def validate_runtime_coverage(routes):
    """Meta-gate: every registry runtime-smoke route must own a strict live test."""
    runtime_ids = {route.function_id for route in routes if route.runtime_smoke}
    declared_ids = set(RUNTIME_ROUTE_TEST_MODULES)
    if runtime_ids != declared_ids:
        raise AssertionError(
            "Runtime route manifest mismatch: missing=%r extra=%r" %
            (sorted(runtime_ids - declared_ids), sorted(declared_ids - runtime_ids))
        )
    for module_name in sorted(set(RUNTIME_ROUTE_TEST_MODULES.values())):
        importlib.import_module(module_name)
    registered_ids = set(_registered_tests)
    if runtime_ids != registered_ids:
        raise AssertionError(
            "Runtime live-test registration mismatch: missing=%r extra=%r" %
            (sorted(runtime_ids - registered_ids), sorted(registered_ids - runtime_ids))
        )
    for route_id, module_name in RUNTIME_ROUTE_TEST_MODULES.items():
        test_id = _registered_tests[route_id]
        if not test_id.startswith(module_name + "."):
            raise AssertionError(
                "%s must be covered by %s, got %s" % (route_id, module_name, test_id)
            )
    return True
