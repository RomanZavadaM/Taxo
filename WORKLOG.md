# WORKLOG — Taxo

**Оновлено:** 28.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full checkpoint in `main`:** Taxo **10.6-r3** / `v10.6-r3`  
**Main head after docs closeout:** `01c8c90d90f1be4641796f6aedcbd7c4ad7d9da4`  
**Active development:** Taxo **10.6-r4**  
**Work branch:** `work/v10.6-r4-waybill-responsive-actions`  
**Scope:** адаптивна панель команд вікна шляхівок; UI-only  
**Live ledger:** Issue #61

## ACTIVE — 10.6-r4

Pre-flight UI audit після 10.6-r3 знайшов конкретний дефект у `show_waybills_for_schedule`: дев'ять команд упаковувалися одним горизонтальним `pack`-рядом, хоча вікно допускає ширину 850 px. На вузькому або масштабованому екрані крайні кнопки могли виходити за видиму область. Пояснювальний текст мав фіксований `wraplength=1050`.

Поточний r4-крок:

- [x] створено окремий runtime-шар `v1064_features.py`;
- [x] усі дев'ять існуючих команд збережено;
- [x] кнопки переводяться у `grid` в тому самому контейнері й автоматично переносяться за реальною шириною;
- [x] пояснювальний текст синхронізує `wraplength` з шириною вікна;
- [x] таблиця шляхівок, вертикальна й горизонтальна прокрутка не змінені;
- [x] `v1064` встановлено зовнішнім шаром поверх `v1063`;
- [x] `VERSION.txt` піднято до `10.6-r4`;
- [x] START packaging guard вимагає `v1064_features.py`;
- [x] додано regression `tests/test_v10_6_r4.py`;
- [ ] повний regression suite success на фінальному code/docs head;
- [ ] чистий START archive перевірено;
- [ ] `v10.6-r4` prerelease/tag на exact issued source;
- [ ] пряме посилання на GitHub Release asset зафіксовано в Issue #61.

## PRESERVED FROM 10.6-r3

- issued/tag source `97e646936d14d163faf93882daf7894f5bb38ab6` не пересувається;
- full checkpoint 10.6-r3 лишається у `main`;
- stable `v10.3` не пересувається;
- plan/fact, PDF payload, route validation, пробіг/спідометр і personnel-duty logic не змінюються r4;
- робочі БД, скани, кеші та персональні файли не входять у release.

## NEXT

Завершити regression/package gate, видати **10.6-r4** як окремий immutable fast-test checkpoint у GitHub Releases. Після видачі наступна кодова ревізія — тільки **10.6-r5**. У `main` r4 не зливати без нової прямої команди власника.

## BLOCKED

Немає.
