# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest code checkpoint in `main`:** Taxo **10.6-r10** — merged via PR #87  
**Main merge commit:** `4bc63060be9911fcf20f432b5e6535b4d8cd0155`  
**Issued r10 tag/source:** `v10.6-r10` → `0baad010d0c0d4f29db62f26c29d512c71058928`  
**Latest START:** `Taxo_v10_6_candidate_r10_START.zip`  
**Next code revision:** **10.7-r1**  
**Live ledger:** Issue #61

## DONE — 10.6-r10

Виправлено реальний збій формування офіційного табеля П-5:

`TypeError: export_p5_pdf() got multiple values for argument 'edrpou'`.

Причина: historical compatibility-layer перевіряв тільки keyword `edrpou`, тоді як актуальний Reports UI передавав ЄДРПОУ позиційно. Wrapper додавав друге значення того самого аргументу. Аналогічний latent defect існував для XLSX.

Завершено:

- `v10610_features.py` нормалізує positional/keyword ЄДРПОУ без дублювання;
- PDF та XLSX П-5 виправлені;
- явно переданий ЄДРПОУ зберігається, порожній отримує fallback з реквізитів підприємства;
- historical `v1043_features.py` не переписано;
- `VERSION.txt` і `main.APP_VERSION` синхронізовані на `10.6-r10`;
- додано regression cases для positional/keyword PDF/XLSX;
- historical release/build workflow-файли збережено як regression anchors;
- повний exact-source regression: **588/588 OK**;
- clean START verify: run `36476665666` — success;
- Windows PR gate: run `36479012210` — success;
- macOS PR gate: run `36479012232` — success;
- користувач підтвердив роботу П-5;
- PR #87 merged у `main`.

## RELEASE

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r10  
START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r10/Taxo_v10_6_candidate_r10_START.zip  
START SHA-256: `1ca7d18b5775c7ddaf424d9d650d78457c7e8451b04cbc6121fcb04fba6acfd8`

`v10.6-r10` лишається immutable: tag/release не пересувати і не перевидавати поверх іншого коду.

## PRESERVED

- stable `v10.3` не пересувається без окремого рішення власника;
- plan/fact, графіки, робочий час, тахографічні дані та БД цим hotfix не змінені;
- робочі БД, скани, кеші та персональні документи не публікуються;
- historical workflows зберігаються як release/regression anchors, а не як активні старі гілки розробки.

## NEXT

Наступна кодова ревізія — тільки **10.7-r1**. Починати її з pre-flight за `START_HERE.md` після наступного завдання власника.

## BLOCKED

Немає.
