# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 16.11.2026.**

- Завершений product checkpoint: **10.20-r3** (PR #454).
- Product merge commit: `42e7a1d71fbf80cc1b4c85551bb710d2f4d13496`.
- Exact product/release source SHA після PR #455: `eec360a965738ecab97f38aeaa5ab8a7452ee1dd`.
- Test prerelease [v10.20-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r3), publisher `43844149251` SUCCESS; 4 portable + START + SHA256.
- Release-trigger PR #456 merged as `fefeb885b81b54709e69010a1251051ef7faf842`.
- Stable/Latest: **v10.18-r3**, unchanged.

## Функціональний результат

10.20-r3 підключає r2 DocumentVault core до користувацького шляху. Для вибраної контрольованої prepared DOCX-редакції у каталозі є явна дія збереження у vault; immutable exact copy, provenance і SHA-256 формує чинний core поза Tk UI thread.

Додано окремий read-only список/картку DocumentVault. Користувач бачить назву, тип, дату, status, document revision, PaperDocuments/PreparedDocuments/CompanyTemplate provenance і exact content SHA-256. Дублі відхиляються; tamper/integrity помилки не маскуються. Запис у vault не означає підпис, проведення чи інший бізнес-факт.

## CI та security gates

Exact-main product/release SHA `eec360a965738ecab97f38aeaa5ab8a7452ee1dd`: START/source `43842526461` — **1385/1385 SUCCESS**; Windows `43842526290`, Win7 `43842526261`, macOS Intel/ARM `43842526193` — SUCCESS. Windows/Win7 Defender та post-scan integrity PASS. Publisher `43844149251` SUCCESS; immutable prerelease target — exact source SHA, 6 assets. GitHub Latest/Stable — v10.18-r3.

## Наступна ревізія

**10.20-r4** — інтегрувати DocumentVault у чинний агрегований каталог «Документи» як read-only source-adapter:

- показувати vault-джерело у звичайному списку документів;
- якщо exact prepared-документ уже є у PaperDocuments і DocumentVault, показувати одну логічну картку з обома походженнями;
- для dedupe використовувати source IDs/provenance, а не схожість назви або дати;
- пошкоджене vault-джерело не повинно приховувати справний PaperDocuments/інший запис.

У цей slice не змішувати:

- auto-migration чинних PaperDocuments;
- scans/originals/attachments;
- signature evidence / digital signature;
- автоматичний статус «підписано» або інші бізнес-факти;
- нове розширення Word-layout renderer.

## Recovery

Читати START_HERE.md → HANDOFF_CURRENT.md → private profile `profile/taxo` → звірити live GitHub. Issue #61 — журнал змін; `WORKLOG.md` — історія.

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
