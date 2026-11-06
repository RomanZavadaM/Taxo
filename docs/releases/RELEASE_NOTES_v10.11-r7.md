# Taxo 10.11-r7 — загальний regression gate для Windows 7

**Дата:** 06.11.2026  
**Статус:** робочий candidate slice; ще не release.  
**Stable:** без змін, `v10.10-r5`.  
**Попередній immutable candidate:** `v10.11-r6`.

## Мета

Закрити окремий finding Issue #175: Win7 workflow до r7 запускав лише вузькі `test_v10_11_r5` / `test_v10_11_r6`, тоді як Windows/macOS перевіряли весь regression suite.

## Зміна

На реальному CPython 3.8.10 x64, після встановлення Win7-compatible dependencies і compile-check, workflow тепер виконує:

`python -m unittest discover -s tests -v`

Лише після успішного повного suite дозволяється PyInstaller packaging Windows 7.

Це не змінює runtime-логіку, схему БД чи робочі дані. UX #164, build/release hardcoding і CI optimization #142/#152 не входять у r7.

## Перевірка

`tests/test_v10_11_r7.py` контролює:
- identity `10.11-r7`;
- наявність full discovery у Win7 workflow;
- порядок regression gate **до** packaging;
- відсутність повернення до вузького списку лише r5/r6.
