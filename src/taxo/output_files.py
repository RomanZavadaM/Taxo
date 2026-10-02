# -*- coding: utf-8 -*-
"""File-output helpers extracted from the historical main module.

This module owns platform opening, report-font discovery and the common
"locked output file" UX.  It intentionally contains no Taxo business rules.
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


def open_external(path):
    """Open a file or directory with the platform's default application."""
    target = str(path)
    if os.name == "nt":
        os.startfile(target)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", target])
    else:
        subprocess.Popen(["xdg-open", target])


def report_font_candidates():
    """System fonts suitable for Ukrainian text in generated PDF reports."""
    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
    ]
    if sys.platform == "darwin":
        candidates.extend([
            str(Path.home() / "Library/Fonts/Arial.ttf"),
            "/Library/Fonts/Arial.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        ])
    candidates.append("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return candidates


def is_file_access_error(exc, path=None):
    """Return True for common file-lock / access failures."""
    if isinstance(exc, PermissionError):
        return True
    if not isinstance(exc, OSError):
        return False
    if getattr(exc, "winerror", None) in (5, 32, 33):
        return True
    if getattr(exc, "errno", None) in (1, 13, 16):
        return True
    return False


def next_output_copy_path(path):
    """Choose a readable unique output name next to a busy file."""
    path = Path(path)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    candidate = path.with_name(f"{path.stem}_{stamp}{path.suffix}")
    if not candidate.exists():
        return candidate
    for n in range(2, 1000):
        candidate = path.with_name(f"{path.stem}_{stamp}_{n}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError("Не вдалося підібрати вільну назву вихідного файла.")


def ask_locked_file_action(parent, path, kind="файл"):
    """Modal locked-file choice: retry / copy / cancel."""
    result = {"value": "cancel"}
    win = tk.Toplevel(parent) if parent is not None else tk.Toplevel()
    win.title("Файл використовується іншою програмою")
    win.resizable(False, False)
    if parent is not None:
        try:
            win.transient(parent)
        except Exception:
            pass
    body = ttk.Frame(win, padding=16)
    body.pack(fill="both", expand=True)
    ttk.Label(
        body,
        text=f"Не вдалося перезаписати {kind}:",
        font=("TkDefaultFont", 10, "bold"),
    ).pack(anchor="w")
    ttk.Label(
        body,
        text=str(path),
        wraplength=620,
        justify="left",
    ).pack(anchor="w", pady=(6, 10))
    ttk.Label(
        body,
        text=(
            "Найчастіше це означає, що файл зараз відкритий у PDF-переглядачі, "
            "Excel або іншій програмі. Закрийте його і натисніть «Повторити».\n\n"
            "Якщо не хочете закривати відкритий файл, Taxo може створити нову копію "
            "поруч із ним з унікальною назвою."
        ),
        wraplength=620,
        justify="left",
    ).pack(anchor="w")

    buttons = ttk.Frame(body)
    buttons.pack(fill="x", pady=(16, 0))

    def choose(value):
        result["value"] = value
        win.destroy()

    ttk.Button(buttons, text="Скасувати", command=lambda: choose("cancel")).pack(
        side="right", padx=(6, 0)
    )
    ttk.Button(buttons, text="Створити копію", command=lambda: choose("copy")).pack(
        side="right", padx=6
    )
    ttk.Button(buttons, text="Повторити", command=lambda: choose("retry")).pack(side="right")
    win.protocol("WM_DELETE_WINDOW", lambda: choose("cancel"))
    try:
        win.grab_set()
        win.update_idletasks()
        if parent is not None:
            x = parent.winfo_rootx() + max(0, (parent.winfo_width() - win.winfo_reqwidth()) // 2)
            y = parent.winfo_rooty() + max(0, (parent.winfo_height() - win.winfo_reqheight()) // 2)
            win.geometry(f"+{x}+{y}")
    except Exception:
        pass
    win.wait_window()
    return result["value"]


def friendly_file_error(exc, path, kind="файл"):
    path = Path(path)
    if isinstance(exc, FileNotFoundError):
        return f"Не знайдено файл або папку для створення {kind}:\n{path}"
    if isinstance(exc, IsADirectoryError):
        return f"Замість файла вибрано папку:\n{path}"
    if isinstance(exc, OSError) and getattr(exc, "errno", None) == 28:
        return f"Недостатньо вільного місця для створення {kind}:\n{path}"
    if is_file_access_error(exc, path):
        return (
            f"Немає доступу до {kind}:\n{path}\n\n"
            "Перевірте права доступу до папки або закрийте програму, яка використовує файл."
        )
    return f"Не вдалося створити {kind}:\n{path}\n\n{type(exc).__name__}: {exc}"


def write_output_file(
    writer,
    target_path,
    parent=None,
    kind="файл",
    error_title="Помилка файла",
    append_error_log=None,
):
    """Run writer(path) with the shared locked-file recovery flow."""
    current = Path(target_path)
    while True:
        try:
            current.parent.mkdir(parents=True, exist_ok=True)
            writer(current)
            return current
        except Exception as exc:
            locked_existing = current.exists() and is_file_access_error(exc, current)
            if locked_existing:
                action = ask_locked_file_action(parent, current, kind)
                if action == "retry":
                    continue
                if action == "copy":
                    current = next_output_copy_path(current)
                    continue
                return None
            log_path = None
            if append_error_log is not None:
                log_path = append_error_log(f"Створення {kind}: {current}", exc)
            msg = friendly_file_error(exc, current, kind)
            if log_path is not None:
                msg += f"\n\nТехнічні подробиці записано у:\n{log_path}"
            messagebox.showerror(error_title, msg, parent=parent)
            return None
