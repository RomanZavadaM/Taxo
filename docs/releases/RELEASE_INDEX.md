# Випуски Taxo

**Стан:** 14.11.2026.

| Лінія | Версія | Призначення |
|---|---|---|
| Стабільна / Latest | [10.18-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r3) | Повний випуск: 2 Windows Setup, 4 portable, START, SHA256; сортування військового обліку та СТОІР, ручне приймання 25/25 PASS. |
| Поточна тестова portable-only | [10.19-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r3) | Стабілізація редактора CompanyTemplates: Tk-дані зчитуються тільки в UI thread; 4 Portable + START + SHA256. |
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
