# -*- coding: utf-8 -*-
"""Cooperate when paper-document files are saved or copied in this process.

This mutex does not replace the workspace lock between application processes.
"""
import os
import threading

_guard = threading.Lock()
_locks = {}


def paper_documents_lock(root):
    """Return the same reentrant lock for equivalent local workspace paths."""
    key = os.path.normcase(os.path.realpath(os.path.abspath(os.fspath(root))))
    with _guard:
        lock = _locks.get(key)
        if lock is None:
            lock = threading.RLock()
            _locks[key] = lock
        return lock
