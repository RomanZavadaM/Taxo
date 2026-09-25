# WORKLOG — Taxo

**Оновлено:** 25.09.2026  
**Repository:** `RomanZavadaM/Taxo`

## CURRENT

**Stable:** Taxo 10.3 / `v10.3`  
**Stable target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`  
**Main base at slice start:** `ae5756da141ac1c27e7fc16034fc40b709f0761e`  
**Active candidate:** `10.3-r7`  
**Branch:** `work/v10.3-r7-backup-dialog-recovery`  
**PR:** pending  
**Live ledger:** Issue #61.

## ACTIVE SLICE — 10.3-r7

### Ціль
1. Виправити показане користувачем вікно «Резервна копія»: нижні кнопки не повинні обрізатися при Windows display scaling / обмеженій висоті.
2. Порівняти Taxo `START_HERE.md` з актуальним OVDP Hub recovery protocol і перенести корисні правила без змішування `PROJECT_STATE` та незлитого worklog.

### Критерії готовності
- `main.APP_VERSION == VERSION.txt == 10.3-r7`;
- backup dialog має окремий footer, що резервує місце для дій;
- regression test не дозволяє повернути старий clipped-footer layout;
- `START_HERE.md` явно описує ролі source-of-truth файлів та семантику «злити у main»;
- full regression suite зелений;
- immutable `v10.3-r7` prerelease містить `Taxo_v10_3_candidate_r7_START.zip`;
- PR merged у `main`;
- інтегрований стан і ledger синхронізовані.

## DOING

- [x] Відновлено стан з `START_HERE.md`, `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` та Issue #61.
- [x] Порівняно Taxo та OVDP Hub `START_HERE.md`.
- [x] Виправлено layout backup dialog.
- [x] Посилено startup/recovery protocol.
- [ ] Додати regression test і release notes.
- [ ] Відкрити PR та зафіксувати його номер.
- [ ] Запустити candidate publisher / CI.
- [ ] Перевірити prerelease asset.
- [ ] Merge у `main` і фінальна синхронізація стану.

## NEXT

Додати regression/release files, відкрити PR і запустити точний candidate gate.

## BLOCKED

Немає.
