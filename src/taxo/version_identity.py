# -*- coding: utf-8 -*-
"""Single runtime source of the Taxo application version (10.10-r3).

Historical feature layers assign ``core.APP_VERSION`` to their own issued
revision while installing and again inside their ``__init__`` (the last one,
``v1085``, used to leave the running application at "10.8-r5"). Those layers
are immutable issued code, so the canonical version from ``main.APP_VERSION``
is pinned once the layer chain is composed:

* immediately after composition (install-time value);
* before the application window is built, so the base UI sees it;
* after every layer ``__init__`` has run, including the window title.
"""
import re

_TITLE_VERSION = re.compile(r"^(Taxo)\s+\S+")


def pin_application_version(core, app_cls, version):
    """Make ``version`` the only runtime application version and return ``app_cls``."""
    version = str(version)
    core.APP_VERSION = version
    original_init = app_cls.__init__
    if getattr(original_init, "_taxo_pinned_version", None) == version:
        return app_cls

    def __init__(self, *args, **kwargs):
        core.APP_VERSION = version
        original_init(self, *args, **kwargs)
        core.APP_VERSION = version
        title_getter = getattr(self, "title", None)
        if callable(title_getter):
            try:
                title = str(title_getter() or "")
                fixed = _TITLE_VERSION.sub(lambda m: f"{m.group(1)} {version}", title, count=1)
                if fixed != title:
                    title_getter(fixed)
            except Exception:
                # The title is cosmetic; never block application start-up.
                pass

    __init__._taxo_pinned_version = version
    __init__.__wrapped__ = original_init
    app_cls.__init__ = __init__
    return app_cls
