# PROJECT_STATE — Taxo

**Підтверджений інтегрований стан: 17.11.2026.**

- Перевірена база main перед цим docs-only checkpoint: `71f5bec74f2dad469a0dc7c67be1d232db77bf89`.
- Завершений продуктовий checkpoint: **10.20-r10**.
- Product PR #487 merged / exact immutable release source: `4661c929c2056f449a30152ed7fb231b1c9ba553`.
- Final product head before merge: `c09842704889a1da1fab00e5280aa7561daa7ad6`.
- Exact-source CI: START `44086412942` (**1430/1430**), Windows `44086412912`, Win7 `44086412809`, macOS Intel/ARM `44086412799` — SUCCESS.
- Microsoft Defender і post-scan integrity — PASS.
- Release-trigger PR #488 merged: `71f5bec74f2dad469a0dc7c67be1d232db77bf89`; publisher `44087486860` — SUCCESS.
- [v10.20-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r10): Test prerelease, 4 Portable + START + SHA256, exact target `4661c929c2056f449a30152ed7fb231b1c9ba553`. Усі 6 assets завантажені та перевірені за назвами/наявністю.
- **Stable/Latest: [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5)**, повний комплект із 8 файлів; source `8a56a2da438777e1fa4549ad2a63883a2ac67e31`.
- Docs-only PR #486 merged `2aa5f104d2b74a3e23fefbee626ae9e814adec87`: форматування RELEASE_INDEX виправлено.

## Інтегрований результат 10.20-r10

- Явна заміна вибраного активного скана у «Документи» → «Скани…».
- Попередня незмінна копія зберігається, а історія показує «Замінено».
- Повна резервна копія/відновлення зберігають обидва файли та історію.
- Відмова/скасування і помилковий файл не забирають попередній скан.
- Важкі збої запису/відкату не приховують помилку і не стирають попередні байти.
- Кнопки доступні у два ряди на малих вікнах зі збільшеними шрифтами.
- Бізнес-статус документа незмінний; КЕП/e-signature, auto «підписано», physical purge, migration та нові залежності не додавались.
- Scan-filter у r10 не реалізований. Issue #289 лишається відкритим як ширший напрям.

## Активна кодова ревізія

Немає. **10.21-r1 ще не розпочата.**

## Наступна дозволена ревізія

**10.21-r1**, лише після fresh GitHub verification і визначення одного вузького кроку. Після r10 піднято minor згідно з PROJECT_RULES. Номер r10, tag і release не перевикористовувати.

## Recovery

Читати START_HERE → HANDOFF_CURRENT → private profile profile/taxo → live GitHub, включно з усіма refs. Issue #61 — журнал змін; WORKLOG — історія. Детальний аудит: [заміна сканів r10](docs/maintenance/AUDIT_DOCUMENT_SCAN_REPLACEMENT_10_20_R10.md).

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
