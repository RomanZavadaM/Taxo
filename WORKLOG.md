# WORKLOG — Taxo

**Оновлено:** 25.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3`  
**Stable target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`  
**Latest published candidate:** `v10.3-r7` → `3bcdb93b9ceffecd07705e3d2a9e6d8b6864e420`  
**Candidate PR:** #64 — merged  
**Main merge:** `398b0831fcdf11f71032c041d98413b4cac26a30`  
**START asset:** `Taxo_v10_3_candidate_r7_START.zip`  
**Live ledger:** Issue #61.

## DONE — 10.3-r7

- [x] Виправлено обрізані кнопки у вікні «Резервна копія»: дії мають окремий зарезервований footer.
- [x] Логіка складу backup і робочі дані не змінені.
- [x] Taxo `START_HERE.md` посилено за актуальним recovery-підходом OVDP Hub.
- [x] У `PROJECT_RULES.md` зафіксовано: «злити у main» = повний релізний checkpoint; простий merge = «інтегрувати PR у main».
- [x] Додано regression `tests/test_v10_3_r7.py`.
- [x] Перший gate виявив 3 застарілі stable-test assumptions; їх виправлено без зміни stable 10.3 metadata.
- [x] Exact-head candidate `3bcdb93b...` пройшов full source regression.
- [x] Windows PR gate run `36104150013` — success.
- [x] macOS ARM64 + Intel PR gate run `36104150024` — success.
- [x] Опубліковано immutable candidate `v10.3-r7` з START + SHA-256.
- [x] PR #64 merged у `main`.

## NEXT

Ручно перевірити `Taxo_v10_3_candidate_r7_START.zip`, зокрема повну видимість і роботу кнопок «Створити копію» / «Скасувати» у вікні резервної копії.

Після вже виданого r7 будь-яка нова кодова зміна починається тільки як **`10.3-r8`**.

## BLOCKED

Немає.
