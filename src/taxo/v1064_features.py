# -*- coding: utf-8 -*-
"""Taxo 10.6-r4 — адаптивні дії у вікні шляхівок.

У базовому вікні шляхівок усі команди історично розміщені одним горизонтальним
рядом. Після додавання перегляду, пробігу та змін персоналу цей ряд перестав
гарантовано вміщатися на вузьких/масштабованих екранах. Поточний runtime-шар
не змінює жодної бізнес-логіки: він лише переводить уже створені кнопки з
``pack`` у адаптивну ``grid``-розкладку в тому самому контейнері та синхронізує
ширину пояснювального тексту з фактичною шириною вікна.
"""
from __future__ import annotations

APP_VERSION = "10.6-r4"

WAYBILL_ACTION_LABELS = (
    "Оновити",
    "Сформувати / видати PDF",
    "Відкрити PDF",
    "Перегляд у Taxo",
    "Анулювати номер",
    "Папка шляхівок",
    "Спідометр / пробіг",
    "Історія пробігу",
    "Зміни лікаря/механіка",
)

WAYBILL_EXPLAIN_PREFIX = "Планові реквізити беруться безпосередньо з графіка"


def compute_wrapped_rows(widths, available_width, gap=6):
    """Повернути індекси елементів, розбиті на рядки за доступною шириною.

    Функція не залежить від Tk і тому напряму покривається regression-тестами.
    Один надширокий елемент допускається у власному рядку; жоден елемент не
    губиться і порядок не змінюється.
    """
    available = max(1, int(available_width or 1))
    rows = []
    current = []
    used = 0
    for index, raw_width in enumerate(widths):
        width = max(1, int(raw_width or 1))
        extra = width if not current else gap + width
        if current and used + extra > available:
            rows.append(tuple(current))
            current = [index]
            used = width
        else:
            current.append(index)
            used += extra
    if current:
        rows.append(tuple(current))
    return tuple(rows)


def _widget_text(widget):
    try:
        return str(widget.cget("text") or "")
    except Exception:
        return ""


def _find_waybill_actions(win):
    """Знайти існуючий action-frame без прив'язки до приватного імені поля."""
    expected = set(WAYBILL_ACTION_LABELS)
    for child in win.winfo_children():
        try:
            widgets = child.winfo_children()
        except Exception:
            continue
        by_text = {_widget_text(widget): widget for widget in widgets}
        if expected.issubset(by_text):
            return child, [by_text[label] for label in WAYBILL_ACTION_LABELS]
    return None, []


def _grid_waybill_actions(frame, buttons, available_width=None):
    """Перекомпонувати кнопки у стільки рядків, скільки реально потрібно."""
    if not frame or not buttons:
        return 0
    try:
        frame.update_idletasks()
        if available_width is None:
            available_width = frame.winfo_width()
        if not available_width or available_width <= 1:
            available_width = frame.winfo_toplevel().winfo_width() - 20
        available_width = max(320, int(available_width))
        widths = [max(1, button.winfo_reqwidth()) for button in buttons]
        rows = compute_wrapped_rows(widths, available_width, gap=6)
        for button in buttons:
            try:
                button.pack_forget()
            except Exception:
                pass
            try:
                button.grid_forget()
            except Exception:
                pass
        for row_no, row in enumerate(rows):
            for col_no, index in enumerate(row):
                buttons[index].grid(
                    row=row_no,
                    column=col_no,
                    sticky="w",
                    padx=3,
                    pady=2,
                )
        return len(rows)
    except Exception:
        # UI-polish не повинен блокувати робочий сценарій шляхівки.
        return 0


def _install_waybill_responsive_layout(win):
    if not win or getattr(win, "_taxo_waybill_actions_r4", False):
        return
    frame, buttons = _find_waybill_actions(win)
    if not frame or not buttons:
        return

    setattr(win, "_taxo_waybill_actions_r4", True)
    state = {"pending": False, "width": None}

    def reflow(event=None):
        try:
            width = int(getattr(event, "width", 0) or frame.winfo_width() or 0)
            if width <= 1:
                width = max(320, win.winfo_width() - 20)
            if state["pending"] or state["width"] == width:
                return
            state["pending"] = True

            def apply():
                state["pending"] = False
                state["width"] = width
                _grid_waybill_actions(frame, buttons, width)

            frame.after_idle(apply)
        except Exception:
            state["pending"] = False

    try:
        frame.bind("<Configure>", reflow, add="+")
    except TypeError:
        # Старі Tk-збірки можуть не прийняти keyword ``add``.
        frame.bind("<Configure>", reflow)
    frame.after_idle(reflow)

    # Жорсткий wraplength=1050 у базовому вікні міг сам підштовхувати requested
    # width за межі невеликого екрана. Знаходимо лише пояснення шляхівки.
    explainer = None
    for child in win.winfo_children():
        text = _widget_text(child)
        if text.startswith(WAYBILL_EXPLAIN_PREFIX):
            explainer = child
            break

    if explainer is not None:
        def sync_wrap(event=None):
            try:
                width = int(getattr(event, "width", 0) or win.winfo_width() or 0)
                explainer.configure(wraplength=max(360, width - 40))
            except Exception:
                pass

        try:
            win.bind("<Configure>", sync_wrap, add="+")
        except TypeError:
            win.bind("<Configure>", sync_wrap)
        win.after_idle(sync_wrap)


def install(core, base_app):
    if getattr(core, "_TAXO_1064_INSTALLED", False):
        return core.App

    core.APP_VERSION = APP_VERSION

    class Taxo1064App(base_app):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            core.APP_VERSION = APP_VERSION
            self.title("Taxo %s — Працівники, графіки та шляхівки" % core.APP_VERSION)

        def show_waybills_for_schedule(self):
            result = super().show_waybills_for_schedule()
            win = getattr(self, "waybill_win", None)
            if win is not None:
                _install_waybill_responsive_layout(win)
            return result

    Taxo1064App.__name__ = "App"
    Taxo1064App.__qualname__ = "App"
    core._TAXO_1064_INSTALLED = True
    core.App = Taxo1064App
    return Taxo1064App
