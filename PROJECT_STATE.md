# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 16.11.2026.**

- Завершений product checkpoint: **10.20-r2** (PR #449).
- Product merge commit: `1519ebda983649a524a03fe0d14c8924d53fe2ff`.
- Exact product/release source SHA після PR #450: `21eb1f668fbd6e915321afe40e2c78d105cdd48b`.
- Test prerelease [v10.20-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r2), publisher `43834523785` SUCCESS; 4 portable + START + SHA256.
- Release-trigger PR #451 merged as `8ec2d07c4e7332748e419e9c7fad1eb6384888df`.
- Stable/Latest: **v10.18-r3**, unchanged.

## Функціональний результат

10.20-r2 додає `document_vault_store.py` — окремий core для `Data/DocumentVault`. Exact prepared DOCX-редакція реєструється лише явним викликом і копіюється як незмінний object. Index зберігає повне походження від PaperDocuments/PreparedDocuments/CompanyTemplates, document family/revision, точний content hash і керований статус `ready` або `archived`.

Core fail-closed: відхиляє дублі, невідомі/пошкоджені записи, підміну index/object, orphan-файли та невідповідність source/hash. Автоматичної міграції старих документів, сканів, підписних доказів чи implicit «підписано» немає.

UI-шлях у цьому checkpoint ще не підключений. Користувацьку дію та read-only перегляд сховища винесено в наступний bounded slice.

## CI та security gates

Exact-main product SHA `21eb1f668fbd6e915321afe40e2c78d105cdd48b`: START/source `43832998489` — 1379/1379 SUCCESS; Windows `43832998423`, Win7 `43832998510`, macOS Intel/ARM `43832998365` — SUCCESS. Windows/Win7 Defender та post-scan integrity PASS. Publisher `43834523785` SUCCESS; immutable release target — exact product SHA, 6 assets. GitHub Latest/Stable — v10.18-r3.

## Наступна ревізія

**10.20-r3** — UI-міст для DocumentVault окремим модулем:

- явна дія для вибраної prepared DOCX-редакції;
- read-only список і картка запису;
- видимі title/kind/date/status, document revision, source provenance та SHA-256;
- зрозумілі повідомлення про дублі й порушення цілісності.

У цей slice не змішувати:

- auto-migration чинних PaperDocuments;
- scans/originals;
- digital signature / підписні докази;
- автоматичний статус «підписано»;
- нове розширення Word-layout renderer.

## Recovery

Читати START_HERE.md → HANDOFF_CURRENT.md → private profile `profile/taxo` → звірити live GitHub. Issue #61 — журнал змін; `WORKLOG.md` — історія.

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
