# WORKLOG — Taxo

**Оновлено:** 29.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.6-r10** / `v10.6-r10`  
**Latest code checkpoint in `main`:** Taxo **10.6-r10** — merged via PR #87  
**Main merge commit:** `4bc63060be9911fcf20f432b5e6535b4d8cd0155`  
**Issued r10 tag/source:** `v10.6-r10` → `0baad010d0c0d4f29db62f26c29d512c71058928`  
**Full package build run:** `36485005797`  
**Binary publication run:** `36485643153` — success  
**Next code revision:** **10.7-r1**  
**Live ledger:** Issue #61

## DONE — 10.6-r10

Виправлено реальний збій формування офіційного табеля П-5:

`TypeError: export_p5_pdf() got multiple values for argument 'edrpou'`.

Завершено:

- `v10610_features.py` нормалізує positional/keyword ЄДРПОУ без дублювання;
- PDF та XLSX П-5 виправлені;
- historical `v1043_features.py` не переписано;
- `VERSION.txt` і `main.APP_VERSION` синхронізовані на `10.6-r10`;
- повний exact-source regression: **588/588 OK**;
- clean START verify: run `36476665666` — success;
- Windows PR gate: run `36479012210` — success;
- macOS PR gate: run `36479012232` — success;
- користувач підтвердив роботу П-5;
- PR #87 merged у `main`;
- з exact immutable source `0baad010d0c0d4f29db62f26c29d512c71058928` зібрано й перевірено повний пакет;
- Windows x64 Setup + Portable — success;
- Windows 7 SP1 x64 Setup + Portable — success, PE compatibility gate пройдений;
- macOS arm64 Portable — success;
- macOS x86_64 Portable — success;
- platform SHA-256 manifests і загальний `SHA256SUMS_v10_6_r10_ALL.txt` опубліковані;
- повний комплект додано до існуючого `v10.6-r10` без пересування tag.

## RELEASE

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r10  
START: `Taxo_v10_6_candidate_r10_START.zip`  
Windows x64: `Taxo_v10_6_candidate_r10_Setup_Windows_x64.exe`, `Taxo_v10_6_candidate_r10_Windows_x64_Portable.zip`  
Windows 7 SP1 x64: `Taxo_v10_6_candidate_r10_Setup_Windows7_x64.exe`, `Taxo_v10_6_candidate_r10_Windows7_x64_Portable.zip`  
macOS: `Taxo_v10_6_candidate_r10_macOS_arm64_Portable.zip`, `Taxo_v10_6_candidate_r10_macOS_x86_64_Portable.zip`  
START SHA-256: `1ca7d18b5775c7ddaf424d9d650d78457c7e8451b04cbc6121fcb04fba6acfd8`

`v10.6-r10` лишається immutable: tag/source не пересувати і не перевидавати поверх іншого коду. Додавання виконуваних assets виконано з того самого exact issued source.

## PRESERVED

- stable `v10.3` не пересувається без окремого рішення власника;
- plan/fact, графіки, робочий час, тахографічні дані та БД цим hotfix не змінені;
- робочі БД, скани, кеші та персональні документи не публікуються;
- historical workflows зберігаються як release/regression anchors.

## NEXT

Наступна кодова ревізія — тільки **10.7-r1**. Починати її з pre-flight за `START_HERE.md` після наступного завдання власника.

## BLOCKED

Немає.
