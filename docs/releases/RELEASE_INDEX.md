# Випуски Taxo

**Стан:** 16.11.2026.

| Лінія | Версія | Призначення |
|---|---|---|
| Стабільна / Latest | [10.18-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r3) | Повний випуск: 2 Windows Setup, 4 portable, START, SHA256; сортування військового обліку та СТОІР, ручне приймання 25/25 PASS. |
| Поточна тестова portable-only | [10.20-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r2) | DocumentVault core: immutable exact prepared DOCX, provenance/hash, ready/archive status і fail-closed integrity; без UI/сканів/підписів; 4 Portable + START + SHA256. |\n| Попередня тестова portable-only | [10.20-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r1) | Inline-зображення з контрольованої prepared Word-редакції переходять у PDF/print; unsupported complex layout fail-closed; 4 Portable + START + SHA256. |
| Попередня тестова portable-only | [10.19-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r10) | Назва підприємства з БД як default чернетки; PDF/preview/print із вибраної prepared Word-редакції; 4 Portable + START + SHA256. |
| Попередня тестова portable-only | [10.19-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r9) | Повторне відкриття PreparedDocuments та контрольована історія Word-редакцій r1/r2/r3 без перезапису; 4 Portable + START + SHA256. |
| Попередня тестова portable-only | [10.19-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r8) | Явне збереження DOCX з prepared snapshot у каталог Taxo; source provenance, 4 Portable + START + SHA256. |
| Попередня тестова portable-only | [10.19-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r7) | DOCX export лише з immutable snapshot-а, exact provenance, 4 Portable + START + SHA256. |
| Попередня тестова portable-only | [10.19-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r6) | Immutable PreparedDocuments snapshot заповненої CompanyTemplates-чернетки: exact source provenance, integrity index, atomic storage і backup/restore; 4 Portable + START + SHA256. |
| Попередня тестова portable-only | [10.19-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r5) | Registry-backed typed fact UI + read-only in-memory draft preview; pair invariant aligned with current assignment rules; 4 Portable + START + SHA256. |
| Попередня тестова portable-only | [10.19-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r4) | Typed fact validation + structural in-memory preview; 4 Portable + START + SHA256. |
| Попередня тестова portable-only | [10.19-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r3) | Стабілізація editor threading. |
| Попередня тестова portable-only | [10.19-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r2) | Редактор власних CompanyTemplates: структуровані текстові поля, великі тексти, immutable власні редакції, optimistic concurrency; superseded r3 через UI-thread fix. |
| Попередня тестова portable-only | [10.19-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r1) | Перший slice CompanyTemplates: власна копія read-only vendor template, provenance/integrity, backup; 4 Portable + START + SHA256. |
| Попередня тестова portable-only | [10.18-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r10) | Security-hardened test checkpoint після Firefox incident: isolated publisher, Defender gate, post-scan SHA256. |
| Попередня стабільна / rollback | [10.17-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.17-r10) | Попередній перевірений повний stable, тег та 8 файлів збережено. |
| Старіша стабільна | [10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8) | Додаткова точка повернення. |
| Старіша стабільна | [10.15-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r5) | Додаткова точка повернення. |
| Попередня тестова portable-only | [10.16-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r7) | Попередній незлитий структурний checkpoint, portable-only. |
| Старіша тестова | [10.15-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r3) | Інструктажі, лист стажування та початковий каталог. |
| Архівна | [10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10) | Варіант повернення. |
| Архівна | [10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) | Попередній контрольний випуск. |

[Усі випуски та файли](https://github.com/RomanZavadaM/Taxo/releases) · [Примітки stable 10.18-r3](RELEASE_NOTES_v10.18-r3.md) · [Поточний стан](../../PROJECT_STATE.md).

Номери виданих ревізій і теги не перевикористовуються. Призначення stable змінюється лише окремим рішенням власника. Детальна історія попередніх контрольних точок збережена у приватній гілці проєктного профілю та в історії Git.

Архівні контрольні точки: Taxo 10.4-r7 — `9f397a092fe828570927bc39cef7a3a467e2aff0` (immutable); [v9.0.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0.1) — historical rollback.
