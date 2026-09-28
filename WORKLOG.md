# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`  
**Main head after docs closeout:** `01c8c90d90f1be4641796f6aedcbd7c4ad7d9da4`  
**Latest issued fast-test:** Taxo **10.6-r9** / `v10.6-r9`  
**Issued r9 source/tag target:** `2705fb5c9105e21bfb669a2d40d4f29449e1a00b` — immutable by project policy  
**Work branch:** `work/v10.6-r9-vehicle-doc-header-responsive`  
**Live ledger:** Issue #61

## DONE — 10.6-r9

Причина: у картці документів транспортного засобу назва авто і довгий `summary_var` були складені в один horizontal header-row. Для довгої назви або кількох проблемних документів обидва тексти конкурували за ширину і могли обрізатися.

Виконано:

- [x] додано outer runtime layer `v1069_features.py`;
- [x] широкий header лишається в один ряд;
- [x] при нестачі ширини title + summary автоматично переходять у два рядки;
- [x] вузький summary отримує динамічний `wraplength`;
- [x] `summary_var`, розрахунок стану документів, таблиця, action-bar, архівні правила та DB semantics не змінені;
- [x] `v1069` встановлено outermost поверх `v1068`;
- [x] START packaging guard вимагає `v1069_features.py`;
- [x] regression contract: `tests/test_v10_6_r9.py`;
- [x] r8 regression переведено в historical identity mode;
- [x] exact-source regression: **578/578 OK**;
- [x] clean START verify run: `36472489549` — success;
- [x] Actions artifact: `Taxo_v10_6_candidate_r9_START`, ID `10992162136`;
- [x] prerelease publisher run: `36472783754` — success;
- [x] tag/release `v10.6-r9` вказує точно на `2705fb5c9105e21bfb669a2d40d4f29449e1a00b`;
- [x] GitHub Release asset: `Taxo_v10_6_candidate_r9_START.zip`;
- [x] Release asset SHA-256: `37a6214bb4ba5b33569804e3efb06912549625600361cf510d52808a55a0a8c4`;
- [x] checksum manifest: `SHA256SUMS_v10_6_r9.txt`;
- [x] one-shot identity/publisher workflows прибрані після успішного виконання.

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r9  
START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r9/Taxo_v10_6_candidate_r9_START.zip

## PRESERVED

- `v10.6-r9` issued source/tag не пересувається й не переписується;
- `v10.6-r8` і попередні issued fast-test також лишаються immutable;
- `v10.6-r3` лишається latest full multi-platform checkpoint у `main`;
- stable `v10.3` не пересувається;
- document status calculation, архівування, копії, plan/fact, шляхівки та тахографічні дані r9 не змінює;
- робочі БД, скани, кеші та персональні файли не входять у release.

## NEXT

Наступна кодова ревізія — тільки **10.6-r10**. Починати її після нового pre-flight/audit. Після видачі r10 наступна ревізія за загальним правилом — **10.7-r1**. `10.6-r9` у `main` не зливати без нової прямої команди власника.

## BLOCKED

Немає.
