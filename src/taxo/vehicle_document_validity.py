# -*- coding: utf-8 -*-
"""Taxo 10.9-r3 runtime marker for full-trip vehicle document validity."""
APP_VERSION = "10.9-r3"


def install(core, base_app):
    core.APP_VERSION = APP_VERSION
    return base_app
