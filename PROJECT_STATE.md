# PROJECT_STATE — Taxo

**Дата:** 13.11.2026.

## Поточний підтверджений стан

Taxo зараз на **10.18-r10**. Security/release cleanup реалізований і перевірений.

- `main`: `19f6b9d6c2a776d9a4e4fe5acd1873f651b0f925`.
- Product checkpoint r10: `2c59fee9feb7464911ced273b93d015d1f5819c5`.
- Stable/Latest: **v10.18-r3**, без змін.
- Test prerelease: **v10.18-r10 — Test Portable**.
- r10 prerelease містить рівно 6 assets: 4 Portable, START, SHA256; Setup відсутні.
- r8 executable publication залишається заблокованою.

## Перевірки r10 після інтеграції в main

- START/source — `43505482939` SUCCESS.
- Windows — `43505482776` SUCCESS.
- Windows 7 — `43505482728` SUCCESS.
- macOS Intel + ARM — `43505482620` SUCCESS.
- Windows і Windows 7: Defender scan PASS для збірок; після scan SHA-256 PASS.

## Що виправлено в release chain

- платформи більше не змішуються під час складання release;
- беруться тільки успішні збірки точного source SHA;
- r8 має явний publish hold;
- тестовий release за замовчуванням Portable-only;
- Setup/full mode тільки явно;
- Defender update retry дозволений лише для відомого Windows Installer conflict `0x80070652`, з обмеженою кількістю спроб;
- інші помилки Defender або malware detection блокують upload/release.

## Невирішений останній gate

Потрібна перевірка **реакції Firefox саме на завантаження нового r10 Windows Portable ZIP**.

Запуск програми для цього не потрібен.

До результату цього тесту нову продуктову функціональність не починати.

## Відкладено

- Повний функціонал бібліотеки шаблонів.
- Створення кінцевого документа з шаблону.
- Word/PDF/друк/сховище/optional scan.
- Подальше dependency/supply-chain hardening (повний hash lock, installer tool provenance) — окремий технічний backlog, не змішувати з продуктом.

## Орієнтир після security gate

Після фіксації результату Firefox:
1. закрити security hold або продовжити vendor/reputation investigation;
2. тільки після цього повернутися до продуктової черги;
3. Stable v10.18-r3 не змінювати без прямої команди власника.

Історичні деталі збережені в Git, Issue #61 і приватному Taxo-профілі; цей файл навмисно тримається коротким.
