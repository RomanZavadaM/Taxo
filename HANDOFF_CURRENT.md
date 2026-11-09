# HANDOFF_CURRENT — Taxo

**Оновлено:** 09.11.2026 — стабільний випуск 10.14-r4 опубліковано й перевірено.

## Фактичний стан

- **Stable / GitHub Latest:** [v10.14-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.14-r4) — 09.11.2026, не draft, не prerelease, **8/8 canonical assets**.
- **Exact immutable release tag:** 214f714f4804cb284fdcbc5b5a26418cef40937a (продуктова логіка 10.14-r4 від 677458afa06893b4d221130db72de4045187e0c8; README й локалізації синхронізовано до видання).
- **Попередня стабільна / rollback:** [v10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10).
- **Наступна кодова ревізія:** 10.14-r5 (ще не розпочиналася). Виданий 10.14-r4 не перевикористовувати.
- **Чинні перевірки випуску:** Windows #1364, Win7 #341, macOS Intel/ARM #1266, START #2404 — SUCCESS; publisher `Promote verified historical Taxo checkpoint to stable` #3 — SUCCESS.
- **Публічна документація:** README українською, EN/DE/ES/FR/KO/JA, docs/README, release index/notes, посібники, product status актуалізовані для 10.14-r4.

## Що прийнято

- Власник 09.11 підтвердив, що загалом робота 10.14-r4 нормальна, і наказав зробити stable.
- «Експлуатація», СТОІР, масові закріплення водіїв і ТЗ, кадрова/робоча нумерація наказів, Word/PDF/JPG, перегляд, редагування та видалення наказів.
- Статус або позначка паперового підпису **не блокують** редагування/видалення: Taxo — допоміжне робоче середовище, офіційний контроль — паперові оригінали.
- Для прямого завантаження використовувати виключно реальні файли GitHub Releases (не тимчасові посилання чату).

## Резерв і межі

- GitHub Releases містить **повний стабільний комплект**, 8 файлів, SHA256SUMS.
- Google Drive: папка [03_STABLE_v10.14-r4_2026-11-09](https://drive.google.com/drive/folders/12Gf4yDjVXYVgJfhcOVcSs1cjrTPGMBYW): архіви macOS ARM/Intel і START, підтверджені.
- Повну незалежну копію **великих Windows-пакетів у Drive не підтверджено**: підключення обмежує передавання до 100 МБ. Вони збережені як immutable release assets у GitHub. Деталі: docs/maintenance/STABLE_BACKUP_MANIFEST_10.14-r4_2026-11-09.md.
- Робочі SQLite, скани, документи персоналу **не входять** до релізу. Усі майбутні втручання в дані — лише після резервного копіювання.

## Одна наступна безпечна дія

Відновити роботу з GitHub `START_HERE.md` → цей HANDOFF → private `dev-strategy/profile/taxo/TAXO_PROFILE.md` → live GitHub → PROJECT_RULES/PROJECT_STATE. Після stable **проводити експлуатаційне тестування**; нові зауваження оформлювати в backlog, розробку продовжувати лише новою 10.14-r5. Не змінювати виданий тег, не створювати методологічних копій.
