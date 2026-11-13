# PROJECT_STATE — Taxo

**Дата:** 13.11.2026.

## Поточний підтверджений стан

Taxo завершив security/release cleanup на **10.18-r10**.

- Product checkpoint r10: `2c59fee9feb7464911ced273b93d015d1f5819c5`.
- Stable/Latest: **v10.18-r3**, без змін.
- Test prerelease: **v10.18-r10 — Test Portable**.
- r10 prerelease: 4 Portable + START + SHA256, без Setup.
- r8 executable publication залишається заблокованою.

## Перевірки r10

Після інтеграції в `main`:
- START/source — `43505482939` SUCCESS;
- Windows — `43505482776` SUCCESS;
- Windows 7 — `43505482728` SUCCESS;
- macOS Intel + ARM — `43505482620` SUCCESS;
- Windows і Windows 7 — Defender PASS та SHA-256 PASS після scan.

Ручний Firefox gate власником також **PASS**: новий Windows x64 Portable ZIP r10 завантажився без malware/danger блокування.

## Висновок

Security hold для поточної лінії **закрито**.

Це не переоцінює історичний r8: його Firefox verdict не оголошується false positive і r8 не перевидається.

## Release chain після виправлення

- платформи ізольовані;
- беруться тільки успішні збірки точного source SHA;
- r8 publish hold збережений;
- test release за замовчуванням Portable-only;
- Setup/full mode лише явно;
- Defender gate fail-closed;
- transient retry лише для `0x80070652`.

## Наступна продуктова ревізія

**10.19-r1.**

Пріоритет — продовження відкладеної системи шаблонів і готових документів:
- власна редагована бібліотека шаблонів;
- великі тексти, включно з інструктажами;
- підстановка дат/ПІБ/ТЗ та інших полів;
- формування Word/PDF/друк;
- окреме сховище готових документів;
- optional scan/PDF підписаного оригіналу;
- без примусового цифрового підпису;
- модульно, без перенесення великої логіки в `main.py`.

Подальший supply-chain hardening (повний dependency hash lock, provenance інструментів інсталятора) залишається технічним backlog і не блокує продуктову роботу.
