# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`  
**Main head after docs closeout:** `01c8c90d90f1be4641796f6aedcbd7c4ad7d9da4`  
**Latest issued fast-test:** Taxo **10.6-r4** / `v10.6-r4`  
**Issued r4 source/tag target:** `3961bde3708a13de6352b8c30438d2b65351110c` — immutable  
**Work branch:** `work/v10.6-r4-waybill-responsive-actions`  
**Scope:** адаптивна панель команд вікна шляхівок; UI-only  
**Live ledger:** Issue #61

## DONE — 10.6-r4

Pre-flight UI audit після 10.6-r3 знайшов конкретний дефект у `show_waybills_for_schedule`: дев'ять команд упаковувалися одним горизонтальним `pack`-рядом, хоча вікно допускає ширину 850 px. На вузькому або масштабованому екрані крайні кнопки могли виходити за видиму область. Пояснювальний текст мав фіксований `wraplength=1050`.

Виконано:

- [x] створено окремий runtime-шар `v1064_features.py`;
- [x] усі дев'ять існуючих команд та callback-и збережено;
- [x] кнопки переводяться у `grid` в тому самому контейнері й автоматично переносяться за реальною шириною;
- [x] пояснювальний текст синхронізує `wraplength` з шириною вікна;
- [x] таблиця шляхівок, вертикальна й горизонтальна прокрутка не змінені;
- [x] `v1064` встановлено зовнішнім шаром поверх історичного runtime-chain до `v1063`;
- [x] `main.APP_VERSION`, `VERSION.txt` і r4 runtime identity узгоджені;
- [x] START packaging guard вимагає `v1064_features.py`;
- [x] regression-контракти попередніх revision зроблені історичними, без заморожування поточної версії на r3;
- [x] фінальний exact-source regression: **539/539 OK**;
- [x] clean START verify/run: `36447919207` — success;
- [x] prerelease publisher: `36448277953` — success;
- [x] tag/release `v10.6-r4` вказує точно на `3961bde3708a13de6352b8c30438d2b65351110c`;
- [x] GitHub Release asset: `Taxo_v10_6_candidate_r4_START.zip`;
- [x] release asset SHA-256: `3bd3d8ce3e98e53532295cc4491167d5c8ac0e099ac8c749b8976534dab3f220`;
- [x] checksum manifest: `SHA256SUMS_v10_6_r4.txt`.

Release: https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r4  
START: https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r4/Taxo_v10_6_candidate_r4_START.zip

## PRESERVED

- issued/tag source `v10.6-r3` не пересувається;
- full checkpoint 10.6-r3 лишається у `main`;
- stable `v10.3` не пересувається;
- plan/fact, PDF payload, route validation, пробіг/спідометр і personnel-duty logic не змінені r4;
- робочі БД, скани, кеші та персональні файли не входять у release;
- post-issuance CI/docs commits можуть рухати work-branch, але **не** tag/source r4.

## NEXT

Наступна кодова ревізія — тільки **10.6-r5**. Починати її з актуального стану після окремого pre-flight/audit. `10.6-r4` у `main` не зливати без нової прямої команди власника.

## BLOCKED

Немає.
