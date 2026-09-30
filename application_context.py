# -*- coding: utf-8 -*-
"""Explicit shared infrastructure for new Taxo modules.

Historically feature modules received the whole ``main`` module and therefore
could reach any global, helper or UI function.  Existing issued layers keep
that compatibility contract, but new modules should depend on this narrow
context instead whenever possible.

The context deliberately contains infrastructure only.  It must not become a
service locator for business rules.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict

from workspace import paths_for


@dataclass(frozen=True)
class WorkspaceServices:
    """Current workspace access without importing the historical main module."""

    root_provider: Callable[[], Path]

    @property
    def root(self) -> Path:
        return Path(self.root_provider())

    def paths(self) -> Dict[str, Path]:
        # Resolve every time because the user can switch workspace before App
        # construction.  Never cache DB paths in feature modules.
        return paths_for(self.root)

    @property
    def main_db_path(self) -> Path:
        return self.paths()["main_db"]

    @property
    def output_dir(self) -> Path:
        return self.paths()["output"]

    @property
    def backup_dir(self) -> Path:
        return self.paths()["backups"]

    def connect_main_db(self, **kwargs):
        """Create a fresh SQLite connection to the currently selected workspace."""
        return sqlite3.connect(self.main_db_path, **kwargs)


@dataclass(frozen=True)
class OutputServices:
    """Shared output operations available to new domain/UI modules."""

    write_file: Callable[..., Any]
    open_external: Callable[..., Any]
    report_font_candidates: Callable[..., Any]


@dataclass(frozen=True)
class ApplicationServices:
    """Stable infrastructure boundary passed to context-aware feature layers."""

    workspace: WorkspaceServices
    output: OutputServices
    version_provider: Callable[[], str]

    @property
    def app_version(self) -> str:
        return str(self.version_provider())


def build_application_services(core) -> ApplicationServices:
    """Bridge legacy ``main`` infrastructure into the narrow r8 contract.

    Only this compatibility factory knows the old module namespace. Consumers
    receive ``ApplicationServices`` and therefore do not need to import main.
    """

    return ApplicationServices(
        workspace=WorkspaceServices(lambda: Path(core.DATA_ROOT)),
        output=OutputServices(
            write_file=core.write_output_file,
            open_external=core.open_external,
            report_font_candidates=core.report_font_candidates,
        ),
        version_provider=lambda: core.APP_VERSION,
    )
