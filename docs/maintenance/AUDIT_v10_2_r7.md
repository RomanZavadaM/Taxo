# AUDIT — Taxo 10.2-r7 packaging correction

**Дата:** 21.09.2026  
**Stable:** Taxo 10.1  
**Parent checkpoint:** v10.2-r6  
**Work branch:** `work/v10.2-r7-secondary-window-style`

## Причина

Publisher 10.2-r6 створив правильний кодовий checkpoint, але ZIP-asset отримав неправильний префікс версії: `Taxo_v10_1_candidate_r6_START.zip`.

За правилом immutable revisions r6 не змінюється. Виправлення оформлено наступною ревізією r7.

## Перевірка

Новий regression test контролює:
- `APP_VERSION == 10.2-r7`;
- `VERSION.txt == 10.2-r7`;
- `start_archive_stem("10.2-r7") == Taxo_v10_2_candidate_r7_START`;
- publisher не містить помилкового `Taxo_v10_1_candidate_r7_START`;
- r6 лишається історичним і не використовується повторно.

## UI scope

UI-код r6 збережений без відкочування: 12 великих secondary windows використовують approved branded header і dynamic enterprise name.

## Release policy

Після green gate публікується `v10.2-r7` з правильним START asset. r6, r5 і stable 10.1 не змінюються.
