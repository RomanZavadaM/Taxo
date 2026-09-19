# Релізи Taxo

**Актуальна stable:** Taxo 10.0  
**Previous stable / rollback:** Taxo 9.0.1

- **[Taxo 10.0 — release notes](RELEASE_NOTES_v10_0.md)**
- **[Повний індекс GitHub Releases](RELEASE_INDEX.md)**
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
