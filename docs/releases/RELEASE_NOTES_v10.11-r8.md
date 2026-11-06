# Taxo 10.11-r8 — build/release naming без revision hardcoding

**Дата:** 06.11.2026  
**Статус:** робочий candidate slice; ще не release.  
**Stable:** без змін, `v10.10-r5`.  
**Попередній immutable candidate:** `v10.11-r7`.

## Мета

Закрити finding #10 з Issue #175: active platform workflows та installer не повинні вручну містити номер поточної ревізії у назвах пакетів, а promotion-to-stable не повинен бути прив'язаний до asset-ів конкретної stable r5.

## Зміна

- `src/taxo/release_naming.py` формує canonical candidate/checksum tokens із `VERSION.txt` і вміє записати їх у GitHub Actions environment.
- Windows, Windows 7 і macOS workflows отримують `TAXO_VERSION`, `TAXO_CANDIDATE_STEM`, `TAXO_CHECKSUM_STEM` з одного джерела.
- Версійні назви Portable/Setup/checksum формуються під час build, а не переписуються вручну між r7/r8/r9.
- `packaging/installer/Taxo.iss` більше не має fallback на конкретну ревізію: version/source/output обов'язково передає workflow.
- promotion-to-stable у `publish-current.yml` формує список 8 обов'язкових asset-ів із marker/version, а не з hardcoded `v10.10-r5`.

## Межі

Runtime/business logic, БД, UX, dependency pins і workflow action pinning не змінюються. Supply-chain hardening лишається наступним окремим slice.

## Regression

`tests/test_v10_11_r8.py` фіксує:
- identity r8;
- canonical naming tokens;
- відсутність r7 package literals у трьох active platform workflows;
- відсутність revision defaults у Inno Setup;
- відсутність hardcoded r5 asset-list у stable promotion.
