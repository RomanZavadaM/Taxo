# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`  
**Latest issued fast-test:** Taxo **10.6-r9** / `v10.6-r9`  
**Issued r9 source/tag target:** `2705fb5c9105e21bfb669a2d40d4f29449e1a00b` — immutable  
**Active revision:** **10.6-r10**  
**Work branch:** `work/v10.6-r10-p5-edrpou-fix`  
**Base:** post-r9 hygiene state `650260963b9a060f940e5c077180377c008dd98c`  
**Live ledger:** Issue #61

## DOING — 10.6-r10

Під час реального формування офіційного табеля П-5 користувач отримав:

`TypeError: export_p5_pdf() got multiple values for argument 'edrpou'`.

Root cause підтверджено: compatibility-layer `v1043_features.py` перевіряв тільки keyword `edrpou`, тоді як актуальний Reports UI передає ЄДРПОУ позиційно. Wrapper додавав друге значення того самого аргументу. Аналогічний latent defect був у XLSX exporter.

Виконано:

- [x] створено `v10610_features.py`;
- [x] positional і keyword EDRPOU нормалізуються так, щоб exporter отримував параметр рівно один раз;
- [x] явно переданий ЄДРПОУ має пріоритет; порожній отримує fallback з реквізитів підприємства;
- [x] виправлення застосоване до PDF і XLSX П-5;
- [x] старий buggy v1043 wrapper обходиться без переписування його historical source;
- [x] r10 встановлено outermost у `taxo_app.py`;
- [x] `VERSION.txt` і `main.APP_VERSION` синхронізовані на `10.6-r10`;
- [x] додано `tests/test_v10_6_r10.py` з positional/keyword regression cases;
- [x] r9 regression identity переведено в historical mode;
- [x] START packaging guard вимагає `v10610_features.py`;
- [x] перша повна suite після синхронізації версії пройшла (`source-test-archive` run `36476217667` — success);
- [x] під час hygiene cleanup виявлено, що historical publisher workflows є regression anchors; їх відновлено;
- [x] hygiene audit виправлено відповідно до фактичного regression contract.

## PRESERVED

- розрахунки табеля П-5 не змінюються;
- plan/fact, графіки, робочий час і тахографічні дані не змінюються;
- схема/дані БД не змінюються;
- видані `v10.6-r9` та попередні tags/releases не пересуваються;
- stable `v10.3` і full checkpoint `v10.6-r3` не пересуваються;
- historical workflow-файли зберігаються як release/regression anchors, а не як дозвіл перевидавати старі релізи.

## NEXT

1. Дочекатися clean START verify на фінальному r10 head.
2. Опублікувати immutable prerelease `v10.6-r10` з `Taxo_v10_6_candidate_r10_START.zip` і SHA-256.
3. Зафіксувати exact issued source, verify/publisher runs, release notes та Issue #61.
4. Після issuance наступна кодова ревізія — тільки **10.7-r1**.

`10.6-r10` не зливати у `main` без окремої прямої команди власника.

## BLOCKED

Немає; очікуються фінальні CI/package gates.
