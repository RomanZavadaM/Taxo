# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`  
**Latest issued fast-test:** Taxo **10.6-r10** / `v10.6-r10`  
**Issued r10 source/tag target:** `0baad010d0c0d4f29db62f26c29d512c71058928` — immutable by project policy  
**Work branch:** `work/v10.6-r10-p5-edrpou-fix`  
**Live ledger:** Issue #61

## DONE — 10.6-r10

Реальне формування офіційного табеля П-5 падало з:

`TypeError: export_p5_pdf() got multiple values for argument 'edrpou'`.

Root cause: historical compatibility-layer `v1043_features.py` перевіряв лише keyword `edrpou`, а актуальний Reports UI передавав ЄДРПОУ позиційно. Wrapper додавав друге значення того самого аргументу. Аналогічний latent defect існував для XLSX.

Виконано:

- [x] додано `v10610_features.py` як outer compatibility layer;
- [x] positional і keyword EDRPOU нормалізуються так, щоб exporter отримував параметр рівно один раз;
- [x] явно переданий ЄДРПОУ має пріоритет, порожній отримує fallback з реквізитів підприємства;
- [x] виправлено PDF і XLSX П-5;
- [x] historical `v1043_features.py` не переписано;
- [x] r10 встановлено outermost у `taxo_app.py`;
- [x] `VERSION.txt` і `main.APP_VERSION` синхронізовані на `10.6-r10`;
- [x] додано regression cases для positional/keyword PDF/XLSX;
- [x] r9 identity переведено в historical mode;
- [x] START guard вимагає `v10610_features.py`;
- [x] historical publisher/build workflows, потрібні regression suite як release anchors, відновлено після надто агресивного cleanup;
- [x] full exact-source regression у publisher: **588/588 OK**;
- [x] clean START verify run `36476665666` — success;
- [x] prerelease `v10.6-r10` опублікований на exact source `0baad010d0c0d4f29db62f26c29d512c71058928`;
- [x] GitHub Release asset: `Taxo_v10_6_candidate_r10_START.zip`;
- [x] START SHA-256: `1ca7d18b5775c7ddaf424d9d650d78457c7e8451b04cbc6121fcb04fba6acfd8`;
- [x] checksum asset: `SHA256SUMS_v10_6_r10.txt`;
- [x] publisher run `36476665890`: tests/build/release publication succeeded; only its final local verification command failed because newly-created tag had not been fetched into that checkout. GitHub API independently confirms the exact tag target and both assets;
- [x] one-shot r10 publisher removed from post-issuance branch state without touching issued tag/source.

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r10  
START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r10/Taxo_v10_6_candidate_r10_START.zip

## PRESERVED

- розрахунок табеля П-5 та його коди не змінюються;
- plan/fact, графіки, робочий час і тахографічні дані не змінюються;
- схема/дані БД не змінюються;
- stable `v10.3`, full checkpoint `v10.6-r3`, `v10.6-r9` і всі попередні issued tags/releases не пересуваються;
- historical workflow-файли зберігаються як regression/release anchors, а не як дозвіл перевидавати старі релізи.

## NEXT

Наступна кодова ревізія — тільки **10.7-r1**. Починати її з нового pre-flight/audit після наступного завдання власника.

`10.6-r10` у `main` не зливати без окремої прямої команди власника.

## BLOCKED

Немає.
