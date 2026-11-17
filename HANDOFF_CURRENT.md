# HANDOFF_CURRENT — Taxo

**Підтверджено 17.11.2026 після live GitHub verification.**

## Підтверджений стан

- Docs-only PR #486 закритий: `2aa5f104d2b74a3e23fefbee626ae9e814adec87`; усі перевірки SUCCESS.
- **Product PR #487 / 10.20-r10 merged:** `4661c929c2056f449a30152ed7fb231b1c9ba553`.
- Final product head: `c09842704889a1da1fab00e5280aa7561daa7ad6`.
- Final-head CI: START `44085368379` — 1430/1430; Windows `44085368368`, Win7 `44085368359`, macOS Intel/ARM `44085368357` — SUCCESS. Defender та post-scan integrity PASS.
- r10: явна «Замінити…» для вибраного скана; попередні байти та історія «Замінено» зберігаються у workspace/full backup.
- Відновлено вже існуючу гілку r10; не повторювати реалізацію. Scan-filter не реалізовано й відкладено.
- Stable/Latest: [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5), 8 файлів; останній опублікований Test: [v10.20-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r9), 6 файлів.

## Ще не завершено

**v10.20-r10 ще не опублікований; exact-main CI на `4661c929c2056f449a30152ed7fb231b1c9ba553` виконується.** Усі результати exact-main перевірити фактично. Нову кодову ревізію до публікації й повного recovery не починати.

Ця release-trigger гілка змінює тільки HANDOFF і кінцевий перенос рядка у `.release/stable-current`. Семантичний Stable marker лишається `10.20-r5`, механізм публікації не змінюється. При merge publisher використовує попередній main SHA як exact release source.

## Одна наступна дія

Перевірити exact-main CI на `4661c929c2056f449a30152ed7fb231b1c9ba553` і checks release-trigger PR. Лише після повного SUCCESS інтегрувати trigger, перевірити publisher, tag та 6 assets r10, а тоді закрити public/private recovery.

Без КЕП/e-signature, auto-signed, physical purge, migration, нових бізнес-статусів або залежностей. TemplateLibrary read-only. Не змінювати Stable/Latest і не запускати executable вручну.
