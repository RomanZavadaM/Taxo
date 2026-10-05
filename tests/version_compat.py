# -*- coding: utf-8 -*-
"""Version parsing for historical regression tests (candidate and stable).

Historical tests asserted "current version >= X.Y-rN" with regexes that only
accepted candidate identities such as ``10.9-r9``. A stable promotion carries
a plain identity such as ``10.10`` (precedent: stable ``10.3``). A stable
promotion ranks after every candidate revision of its line, so the missing
revision is reported as ``STABLE_REVISION``.

The helpers return match-like objects with ``groups()`` / ``group(n)`` so the
historical assertions keep their original shape.
"""
import re

STABLE_REVISION = "999"
_CORE = r"(\d+)\.(\d+)(?:-r(\d+))?"


class VersionMatch:
    def __init__(self, groups):
        self._groups = tuple(groups)

    def groups(self):
        return self._groups

    def group(self, index=0):
        if index == 0:
            return ".".join(g for g in self._groups if g is not None)
        return self._groups[index - 1]


def _wrap(match, revision_index=2):
    if match is None:
        return None
    groups = list(match.groups())
    if groups[revision_index] is None:
        groups[revision_index] = STABLE_REVISION
    return VersionMatch(groups)


def search_version_line(text):
    """``Version: 10.9-r9`` or ``Version: 10.10`` inside VERSION.txt text."""
    return _wrap(re.search(r"Version:\s*" + _CORE, text))


def search_version(text):
    """First ``X.Y-rN`` or ``X.Y`` identity anywhere in ``text``."""
    return _wrap(re.search(_CORE, text))


def search_app_version(source):
    """``APP_VERSION = "..."`` assignment in main.py source."""
    return _wrap(re.search(r'APP_VERSION\s*=\s*"' + _CORE + '"', source))


def fullmatch_version(value):
    return _wrap(re.fullmatch(_CORE, str(value)))


def fullmatch_version4(value):
    """``X.Y-rN[.M]`` or stable ``X.Y``; returns four groups."""
    return _wrap(re.fullmatch(r"(\d+)\.(\d+)(?:-r(\d+)(?:\.(\d+))?)?", str(value)))
