# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`  
**Main head after docs closeout:** `01c8c90d90f1be4641796f6aedcbd7c4ad7d9da4`  
**Latest issued fast-test:** Taxo **10.6-r8** / `v10.6-r8`  
**Issued r8 source/tag target:** `09f0e6e6cf3809b6d0efc6c9cdad7937a44d78d3` — immutable by project policy  
**Work branch:** `work/v10.6-r8-vehicle-document-form-responsive`  
**Live ledger:** Issue #61

## DONE — 10.6-r8

Причина: форма додавання/редагування документа ТЗ мала багато вертикальних рядків, fixed `wraplength=520` і нижню кнопку «Зберегти». На невисоких/масштабованих екранах нижня дія могла притискатися або обрізатися, а пояснювальний текст — виходити за фактичну ширину правої колонки.

Виконано:

- [x] додано outer runtime layer `v1068_features.py`;
- [x] на висоті <620 px стандартні вертикальні відступи форми ущільнюються;
- [x] поле «Примітка» у compact mode зменшується з 4 до 3 рядків;
- [x] пояснення про архівацію та поточну копію отримують динамічний `wraplength` 240…520 px;
- [x] при нормальній висоті початкові відступи й висота примітки відновлюються;
- [x] вікно лишається resizeable;
- [x] існуючий `_form()` і його `save()` closure не переписуються;
- [x] `EXPIRY_REQUIRED`, перевірка дат, `archive_current_document_slot()`, `copy_document_file()`, SQL і DB semantics не змінені;
- [x] `v1068` встановлено outermost поверх `v1067`;
- [x] START packaging guard вимагає `v1068_features.py`;
- [x] regression contract: `tests/test_v10_6_r8.py`;
- [x] історичний r7 regression виправлено: r7 identity перевіряється як historical layer, а не як вічно поточна версія;
- [x] exact-source regression: **570/570 OK**;
- [x] clean START verify run: `36469618323` — success;
- [x] Actions artifact: `Taxo_v10_6_candidate_r8_START`, ID `10990373762`;
- [x] prerelease publisher run: `36469958643` — success;
- [x] tag/release `v10.6-r8` вказує точно на `09f0e6e6cf3809b6d0efc6c9cdad7937a44d78d3`;
- [x] GitHub Release asset: `Taxo_v10_6_candidate_r8_START.zip`;
- [x] Release asset SHA-256: `90e04c065a157aa1453e2aa50024ca3f4093de37db30be23ae007114531eb7ec`;
- [x] checksum manifest: `SHA256SUMS_v10_6_r8.txt`;
- [x] one-shot identity/publisher workflows прибрані після успішного виконання.

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r8  
START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r8/Taxo_v10_6_candidate_r8_START.zip

## PRESERVED

- `v10.6-r8` issued source/tag не пересувається й не переписується;
- `v10.6-r7` і попередні issued fast-test також лишаються immutable;
- `v10.6-r3` лишається latest full multi-platform checkpoint у `main`;
- stable `v10.3` не пересувається;
- document save/business logic, plan/fact, шляхівки та тахографічні дані r8 не змінює;
- робочі БД, скани, кеші та персональні файли не входять у release.

## NEXT

Наступна кодова ревізія — тільки **10.6-r9**. Починати її після нового pre-flight/audit. `10.6-r8` у `main` не зливати без нової прямої команди власника.

## BLOCKED

Немає.
