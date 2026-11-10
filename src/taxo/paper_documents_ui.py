# -*- coding: utf-8 -*-
"""Compatibility entry point for the combined document catalog."""
from __future__ import annotations

from document_catalog_ui import open_document_catalog


def open_paper_document_catalog(parent, core, workspace_root):
    return open_document_catalog(parent, core, workspace_root)
