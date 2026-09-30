# WORKLOG — Taxo

**Оновлено:** 30.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3` — immutable  
**Latest full multi-platform checkpoint:** Taxo **10.8-r3** / `v10.8-r3`  
**Latest integrated code checkpoint:** **10.8-r3** — `main` `50db4b0de4d37260c2031aa96317fef61d93ea90`  
**Issued source/tag:** `v10.8-r3` → `d8ec901b9b80f74b5b85cd1bda202dd58c86a7bd`  
**Active code revision:** **10.8-r4** — СТОІР / пробіг / ТО / ОТК  
**Active branch:** `work/v10.8-r4-stoir-maintenance`  
**Live ledger:** Issue #61

## ACTIVE — 10.8-r4

Тема: **окремий центр СТОІР без перевантаження існуючого розділу «Експлуатація»**.

### Реалізовано

- створено `vehicle_maintenance.py` з профілями ТО, подіями ТО/ремонту та розрахунком наступного ТО від фактичного одометра;
- джерело поточного пробігу — існуючий `vehicle_odometer_readings` зі шляхових листів, без паралельного «поточного пробігу»;
- базові профілі: легковий/автобус 5 000/20 000 км; вантажний/автобус на вантажній базі 4 000/16 000 км; передбачено індивідуальний профіль виробника;
- якщо останнє ТО невідоме, наступний пробіг ТО не вигадується;
- створено окремий UI `vehicle_maintenance_ui.py` з вкладками «Огляд», «Пробіг / одометр», «ТО і ремонти», «Технічний контроль (ОТК)»;
- у sidebar додано окремий вхід «СТОІР» поряд з «Експлуатація», а не нові вкладки в центр наказів;
- користувацьку назву `inspection` змінено на «Протокол ОТК / перевірки технічного стану», ключ БД не змінюється;
- копія протоколу ОТК лишається в «Документи ТЗ», СТОІР лише читає його чинність;
- START та source-package guard вимагають `v1084_features.py`, `vehicle_maintenance.py`, `vehicle_maintenance_ui.py`;
- додано `tests/test_v10_8_r4.py` і нормативний аудит `docs/maintenance/AUDIT_10.8-r4_STOIR_OTK.md`.

### Regression / recovery

- перший повний прогін показав, що функціональні r4-тести проходять, але історичний r3 identity test блокував законний перехід на r4;
- r3 regression відновлено до точного функціонального контракту виданого `v10.8-r3`, а його identity переведено в historical-anchor режим;
- невдалий one-shot package guard більше не є частиною branch head; актуальний package guard застосований і самовидалений;
- наступна дія: exact-head regression → draft PR → Windows/macOS gates → fast-test `v10.8-r4` лише після green.

## DONE — 10.8-r3

- PR #105 merged у `main`;
- full package run `36741933852` — success;
- Windows x64, Windows 7 x64, macOS arm64/x86_64, START і checksums опубліковані;
- stable `v10.3` не змінювався.

## NEXT

Після видачі `10.8-r4` будь-яка нова кодова зміна — тільки **10.8-r5**. Майбутні шини/АКБ/агрегати та UI-аудит планування персоналу не змішувати в r4.
