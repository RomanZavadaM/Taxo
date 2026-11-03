# -*- coding: utf-8 -*-
"""Single runtime source of the Taxo application version.

Historical feature layers keep their issued revision constants because they
are part of the recorded development history. Some of those layers assign
``core.APP_VERSION`` and set window titles while their ``__init__`` methods
run. The current application therefore pins the canonical version from
``main.APP_VERSION`` and normalizes branding text both at startup and when
later windows/widgets are mapped.
"""
import re

_TAXO_VERSION = re.compile(r"\bTaxo\s+v?\d+(?:\.\d+)+(?:-r\d+)?")
_STANDALONE_V = re.compile(r"^v\d+(?:\.\d+)+(?:-r\d+)?$")
_LABELED_VERSION = re.compile(
    r"^((?:Версія|Version|Versión|Versione|バージョン|버전)\s*:?\s*)"
    r"v?\d+(?:\.\d+)+(?:-r\d+)?$",
    re.IGNORECASE,
)


def _canonicalize_text(value, version):
    """Replace only UI branding/version fields, never historical prose."""
    text = str(value or "")
    fixed = _TAXO_VERSION.sub(f"Taxo {version}", text)
    if _STANDALONE_V.fullmatch(fixed):
        return f"v{version}"
    match = _LABELED_VERSION.fullmatch(fixed)
    if match:
        return f"{match.group(1)}{version}"
    return fixed


def _normalize_widget(widget, version):
    """Normalize one Tk-like widget without assuming a concrete toolkit class."""
    title = getattr(widget, "title", None)
    if callable(title):
        try:
            current = str(title() or "")
            fixed = _canonicalize_text(current, version)
            if fixed != current:
                title(fixed)
        except Exception:
            pass

    cget = getattr(widget, "cget", None)
    configure = getattr(widget, "configure", None)
    if callable(cget) and callable(configure):
        try:
            current = cget("text")
            fixed = _canonicalize_text(current, version)
            if fixed != current:
                configure(text=fixed)
        except Exception:
            pass


def _normalize_widget_tree(widget, version):
    _normalize_widget(widget, version)
    children = getattr(widget, "winfo_children", None)
    if not callable(children):
        return
    try:
        child_widgets = list(children())
    except Exception:
        return
    for child in child_widgets:
        _normalize_widget_tree(child, version)


def pin_application_version(core, app_cls, version):
    """Make ``version`` the single runtime/UI application version."""
    version = str(version)
    core.APP_VERSION = version
    original_init = app_cls.__init__
    if getattr(original_init, "_taxo_pinned_version", None) == version:
        return app_cls

    def __init__(self, *args, **kwargs):
        core.APP_VERSION = version
        original_init(self, *args, **kwargs)
        core.APP_VERSION = version

        _normalize_widget_tree(self, version)

        bind_all = getattr(self, "bind_all", None)
        if callable(bind_all):
            try:
                def _on_map(event):
                    core.APP_VERSION = version
                    target = getattr(event, "widget", None)
                    if target is not None:
                        _normalize_widget_tree(target, version)

                bind_all("<Map>", _on_map, add="+")
                self._taxo_version_map_handler = _on_map
            except Exception:
                pass

    __init__._taxo_pinned_version = version
    __init__.__wrapped__ = original_init
    app_cls.__init__ = __init__
    return app_cls
