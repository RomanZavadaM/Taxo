# Релізи Taxo

**Актуальна stable:** Taxo 10.1  
**Previous stable / rollback:** Taxo 10.0  
**Current prerelease:** Taxo 10.2-r4

- **[Taxo 10.0 — release notes](RELEASE_NOTES_v10_0.md)**
- [GitHub Release v10.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.0)
- [Combined SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.0/SHA256SUMS_v10_0.txt)
- **[Повний індекс GitHub Releases](RELEASE_INDEX.md)**
- **[Taxo 10.2-r4 — release notes](RELEASE_NOTES_v10_2_r4.md)**
- [GitHub prerelease v10.2-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.2-r4)
- [Taxo 9.1 candidate r9.8 — примітки](RELEASE_NOTES_v9_1_candidate_r9_8.md)
- [Taxo 9.1 candidate r9.7 — примітки](RELEASE_NOTES_v9_1_candidate_r9_7.md)
- [Taxo 9.1 candidate r9.6 — примітки](RELEASE_NOTES_v9_1_candidate_r9_6.md)
- [Taxo 9.1 candidate r9.5 — примітки](RELEASE_NOTES_v9_1_candidate_r9_5.md)
- [Taxo 9.1 candidate r9.4 — примітки](RELEASE_NOTES_v9_1_candidate_r9_4.md)
- [Taxo 9.0.1 — примітки](RELEASE_NOTES_v9_0_1.md)
- [Taxo 9.0 — примітки](RELEASE_NOTES_v9_0.md)

## Політика

- `v10.0` — stable, створюється один раз з commit у `main`;
- `v9.1-r5` … `v9.1-r9.8` — immutable історичні candidates;
- `v9.1-r9.5` має відомий historical START defect і не використовується;
- старі tags/releases не пересуваються і не перезаписуються;
- робочі БД/скани/персональні дані не включаються в releases;
- stable executable packages формуються для Windows x64, macOS ARM64 та macOS Intel.


## Stable 10.0 — published

Release target: `91c0d6365a40eb09fe40f97a2965da40b314bc15`. Windows x64 Setup/Portable, macOS ARM64/Intel, START/source та SHA-256 manifests опубліковані. Stable publisher завершився успішно; regression suite — 117 tests / OK на Windows і обох macOS архітектурах.


## Правило candidate-розробки

- Кожен завершений крок candidate отримує нову ревізію.
- Послідовність: `r1 ... r10`; після `r10` — наступна minor-версія з `r1`.
- Ревізію, для якої вже видано тестовий архів, повторно не використовувати.
- Кожен крок завершується окремим START-архівом для тестування.
- Повні правила: [../maintenance/DEVELOPMENT_RULES.md](../maintenance/DEVELOPMENT_RULES.md).
