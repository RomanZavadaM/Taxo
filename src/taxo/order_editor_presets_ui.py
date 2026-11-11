# -*- coding: utf-8 -*-
"""Typical text presets for the order editor.

This component owns the preset selector and the *explicit* text replacement
confirmation. It never persists an order; the general order editor retains
ownership of its fields and its save transaction.
"""
from __future__ import annotations


class OrderEditorPresetsSection:
    """Manage editable order-text presets without overwriting user work silently."""

    def __init__(
        self,
        *,
        core,
        ops,
        dialog,
        frame,
        initial_type,
        force_type,
        type_var,
        type_by_label,
        subject_var,
        preamble,
        body_text,
    ):
        self.core = core
        self.ops = ops
        self.dialog = dialog
        self.force_type = force_type
        self.type_var = type_var
        self.type_by_label = type_by_label
        self.subject_var = subject_var
        self.preamble = preamble
        self.body_text = body_text
        self.preset_rows = []
        self.preset_var = core.tk.StringVar(value="")

        self.frame = core.ttk.Frame(frame)
        self.frame.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(3, 2),
        )
        self.frame.columnconfigure(1, weight=1)
        core.ttk.Label(
            self.frame,
            text="Типова заготовка",
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.preset_box = core.ttk.Combobox(
            self.frame,
            textvariable=self.preset_var,
            values=(),
            state="readonly",
        )
        self.preset_box.grid(row=0, column=1, sticky="ew")
        core.ttk.Label(
            self.frame,
            text=(
                "Заготовка змінює тему, вступ і пункти лише після "
                "кнопки «Вставити заготовку»."
            ),
            style="Muted.TLabel",
            wraplength=760,
            justify="left",
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(2, 0),
        )

        # Existing live-test references are preserved for the order editor.
        dialog._taxo_order_preset_box = self.preset_box
        dialog._taxo_order_preset_var = self.preset_var
        self.refresh(initial_type, select_first=True)

    @staticmethod
    def _title(row):
        return str(row.get("title") or row.get("id") or "Заготовка")

    def refresh(self, order_type, select_first=True):
        """Update choices for an order type without replacing editable text."""
        self.preset_rows[:] = list(
            getattr(self.ops, "ORDER_TEXT_PRESETS", {}).get(order_type, ())
        )
        titles = [self._title(row) for row in self.preset_rows]
        self.preset_box.configure(values=titles)
        if titles:
            self.frame.grid()
            if select_first or self.preset_var.get() not in titles:
                self.preset_var.set(titles[0])
        else:
            self.preset_var.set("")
            self.frame.grid_remove()

    def apply(self):
        """Apply the chosen preset only after confirming destructive edits."""
        order_type = self.force_type or self.type_by_label.get(
            self.type_var.get(), self.ops.TYPE_GENERIC
        )
        selected_title = self.preset_var.get()
        preset = next(
            (row for row in self.preset_rows if self._title(row) == selected_title),
            None,
        )
        if preset is None:
            template = self.ops.DEFAULT_BODY_TEMPLATES.get(order_type, "")
            if not template:
                self.core.messagebox.showinfo(
                    "Типова заготовка",
                    "Для цього типу наказу заготовку не задано.",
                    parent=self.dialog,
                )
                return False
            preset = {
                "subject": self.ops.DEFAULT_SUBJECTS.get(order_type, ""),
                "preamble": self.ops.DEFAULT_PREAMBLES.get(order_type, ""),
                "body": template,
            }

        new_subject = str(preset.get("subject") or self.subject_var.get())
        new_preamble = str(preset.get("preamble") or "")
        new_body = str(preset.get("body") or "")
        current_body = self.body_text.get("1.0", "end-1c").strip()
        current_preamble = self.preamble.get("1.0", "end-1c").strip()

        changed = (
            (current_body and current_body != new_body.strip())
            or (current_preamble and current_preamble != new_preamble.strip())
            or (
                self.subject_var.get().strip()
                and self.subject_var.get().strip() != new_subject.strip()
            )
        )
        if changed and not self.core.messagebox.askyesno(
            "Вставити заготовку?",
            (
                "Поточні тема, вступ і текст пунктів будуть замінені "
                "вибраною заготовкою. Продовжити?"
            ),
            parent=self.dialog,
        ):
            return False

        self.subject_var.set(new_subject)
        self.preamble.delete("1.0", "end")
        self.preamble.insert("1.0", new_preamble)
        self.body_text.delete("1.0", "end")
        self.body_text.insert("1.0", new_body)
        return True


def install_order_editor_presets(**kwargs):
    """Attach the preset section to one editor and return its controller."""
    return OrderEditorPresetsSection(**kwargs)
