# HANDOFF_CURRENT — Taxo

**Підтверджено 17.11.2026 після звірки live GitHub.**

## Поточний стан

- Перевірена база main перед цим docs-only checkpoint: `71f5bec74f2dad469a0dc7c67be1d232db77bf89`; checkpoint змінює лише документацію.
- **10.20-r10 завершена, інтегрована й опублікована.**
- Product PR #487 merged / exact immutable release source: `4661c929c2056f449a30152ed7fb231b1c9ba553`.
- Final product head: `c09842704889a1da1fab00e5280aa7561daa7ad6`.
- Exact-source CI: START `44086412942` — **1430/1430**; Windows `44086412912`; Win7 `44086412809`; macOS Intel/ARM `44086412799` — SUCCESS.
- Microsoft Defender та post-scan integrity — PASS для Windows/Win7.
- Release-trigger PR #488 merged: `71f5bec74f2dad469a0dc7c67be1d232db77bf89`; publisher `44087486860` — SUCCESS.
- [v10.20-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r10) — Test prerelease, рівно 6 завантажених файлів: 4 Portable + START + SHA256; tag target `4661c929c2056f449a30152ed7fb231b1c9ba553`.
- **Stable / GitHub Latest:** [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5), 8 файлів, без змін.
- Docs-only PR #486 виправив буквальний перенос рядка у RELEASE_INDEX; merged `2aa5f104d2b74a3e23fefbee626ae9e814adec87`, усі перевірки SUCCESS.

## Що завершено в r10

У «Документи» → «Скани…» можна явно **«Замінити…»** вибраний активний скан. Нова копія стає активною; попередній незмінний файл зберігається у workspace/full backup, а «Історія…» показує дію **«Замінено»**. Скасування, відмова й помилковий файл не забирають попередній скан. Кнопки вміщуються у два ряди; Tk-перевірка малого вікна/збільшеного шрифту PASS.

## Важливе для recovery

Попередній HANDOFF/промпт помилково казав «r10 не розпочата». Перевірка всіх refs знайшла незавершену `work/v10.20-r10-paper-scan-replace` на `6b798332c18c1adbe2ad299020c7b06e16867b70`. Її збережено й завершено; повторна реалізація не створювалась. Не трактувати таку розбіжність як доказ іншого виконавця.

Початкові відмови: незавершені version guards і несумісний з Python 3.8 виклик у новому тесті. Обидва виправлені; final head та exact source повністю зелені.

## Одна наступна дія

**10.21-r1 ще не розпочата.** У новій сесії виконати fresh GitHub verification, включно з відкритими PR та всіма refs, і лише тоді вибрати один наступний вузький крок з Issue #289. Пропозиція фільтра за наявністю сканів відкладена; її не вважати реалізованою або наперед затвердженим наступним кроком.

Не перевикористовувати r10/tag/release. Без КЕП/e-signature, auto-signed, physical purge, migration або нових бізнес-статусів «заодно». TemplateLibrary read-only; власні шаблони — CompanyTemplates. Stable/Latest змінюється тільки за прямою командою власника. Працювати через GitHub/хмарні перевірки; executable вручну не запускати.
