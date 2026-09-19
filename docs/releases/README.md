# Релізи

Актуальна стабільна версія: **Taxo 9.0.1**.

Актуальний перевірочний кандидат: **Taxo 9.1 candidate r9.6** (GitHub Pre-release; stable `main` не змінюється до завершення manual operational gate).

- **[Повний індекс усіх опублікованих релізів](RELEASE_INDEX.md)**
- [Taxo 9.1 candidate r9.6 — примітки](RELEASE_NOTES_v9_1_candidate_r9_6.md)
- [Taxo 9.1 candidate r9.5 — примітки](RELEASE_NOTES_v9_1_candidate_r9_5.md)
- [Taxo 9.1 candidate r9.4 — примітки](RELEASE_NOTES_v9_1_candidate_r9_4.md)
- [Taxo 9.1 candidate r9.3 — примітки](RELEASE_NOTES_v9_1_candidate_r9_3.md)
- [Taxo 9.1 candidate r9.2 — примітки](RELEASE_NOTES_v9_1_candidate_r9_2.md)
- [Taxo 9.1 candidate r9.1 — примітки](RELEASE_NOTES_v9_1_candidate_r9_1.md)
- [Примітки до Taxo 9.0.1](RELEASE_NOTES_v9_0_1.md)
- [Примітки до Taxo 9.0](RELEASE_NOTES_v9_0.md)
- [Стабільний реліз Taxo 9.0.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0.1)

Кандидатні теги не пересуваються після публікації. Кожна нова контрольна точка отримує окремий tag/release.

Історичні релізні матеріали версій 8.x винесені в гілку [`history/development-v8`](https://github.com/RomanZavadaM/Taxo/tree/history/development-v8).

## Поточна публікаційна політика

- `v9.0.1` — stable і rollback point;
- `v9.1-r9.6` — поточний candidate для ручної перевірки;
- усі підготовлені 9.x releases опубліковані; draft-релізів немає;
- candidate tags/releases не пересуваються і не перезаписуються;
- новий код після r9.6 потребує нового candidate tag/release;
- docs-only commits не змінюють release target r9.5.

- `v9.1-r9.5` зберігається як immutable історичний release, але має відомий START.bat / Windows CMD parsing defect і не рекомендується для ручного тестування.
