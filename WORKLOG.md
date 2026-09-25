# WORKLOG — Taxo

**Оновлено:** 25.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3`  
**Stable target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`  
**Latest published candidate:** `v10.3-r8` → `ac5b22266cdf48ff664a3d13c7e3c3ec86876cfc`  
**Candidate PR:** #66 — merged  
**Main merge:** `a513e484f8d735120a2c0e1072fe2f40cdd5a26a`  
**START asset:** `Taxo_v10_3_candidate_r8_START.zip`  
**r7 manual gate:** accepted  
**r8 manual gate:** pending macOS sidebar check  
**Live ledger:** Issue #61.

## DONE — 10.3-r8

- [x] Відновлено стан за `START_HERE.md`.
- [x] Зафіксовано прийняття manual gate 10.3-r7.
- [x] Виправлено слабку читабельність sidebar на macOS: Darwin використовує explicit-color clickable labels замість native Aqua buttons.
- [x] Додано normal/selected/hover/focus states і keyboard activation.
- [x] Windows/Linux path не змінено.
- [x] Додано regression `tests/test_v10_3_r8.py`.
- [x] Перший gate виявив stale historical r7 identity test; виправлено без зміни r7 checkpoint.
- [x] Exact-head publisher run `36105901328` — success.
- [x] Windows gate run `36105905499` — success.
- [x] macOS ARM64 + Intel gate run `36105905210` — success.
- [x] Опубліковано `v10.3-r8` з START + SHA-256.
- [x] PR #66 merged у `main`.

## NEXT

Ручно перевірити на macOS `Taxo_v10_3_candidate_r8_START.zip`: ліве меню має мати темно-синій фон, чіткий білий текст/іконки та виразний активний пункт.

Після вже виданого r8 будь-яка нова кодова зміна починається тільки як **`10.3-r9`**.

## BLOCKED

Немає.
