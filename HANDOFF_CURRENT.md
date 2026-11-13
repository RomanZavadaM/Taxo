# HANDOFF_CURRENT — Taxo

**13.11.2026 — Stable/Latest: v10.18-r3 (підтверджено). Перевірений тестовий кандидат: 10.18-r5 (не merged, не tagged, GitHub Pre-release ще не опубліковано). Наступний новий номер коду після r5 — 10.18-r6.**

## Підтверджена база

- **Stable/Latest** — [v10.18-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r3), незмінна; immutable tag/source `65bc80ecae85793cb7c2c14edd4d3eabaa2b4470`, 8 assets, 25/25 прийнято вручну.
- **Rollback Stable** — [v10.17-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.17-r10), незмінна.
- **Публічний кодовий `main` перед цим docs-only checkpoint** — `c108bc02a64698556ebaa5cdaab59f49d46dc4ca`. r4/r5 у `main` **не merged**.
- **10.18-r4** — попередній перевірений code head `eb762664dbd85650d3b8e5a6a59a7f3dfb4ea551`, [draft PR #393](https://github.com/RomanZavadaM/Taxo/pull/393); type-aware сортування тахографа, 1229 PASS, 4 платформи CI PASS.
- **10.18-r5** — новий окремий перевірений code head `7ee89f3f0dcb731c4b2fd416b6ddb630e3ebe7d2`, branch `work/v10.18-r5-template-library-reader`, [draft PR #396](https://github.com/RomanZavadaM/Taxo/pull/396), створений **від exact r4 head**. Новий документований, read-only `src/taxo/template_library_reader.py`, 13 синтетичних тестів. Немає інтеграції в UI/`main.py` (окрім номера версії), змін SQLite, vault, backup, інсталяторів чи реальних користувацьких матеріалів.
- **Exact-head r5 CI:** [START/source 43428732476](https://github.com/RomanZavadaM/Taxo/actions/runs/43428732476) SUCCESS, **1242/1242**; [Windows 43428739892](https://github.com/RomanZavadaM/Taxo/actions/runs/43428739892) SUCCESS; [Win7 43428739920](https://github.com/RomanZavadaM/Taxo/actions/runs/43428739920) SUCCESS; [macOS Intel/ARM64 43428739821](https://github.com/RomanZavadaM/Taxo/actions/runs/43428739821) SUCCESS обидві job.
- **Тестові CI artifacts r5:** START `14038129439` (назва `Taxo_v10_18_candidate_r5_START`); Windows x64 `14037529861`; Windows7 x64 `14037969420`; macOS Intel `14038424881`; macOS ARM64 `14038930161`.
- **GitHub release/tag v10.18-r5:** не створювався. Збірки **лише CI artifacts**, їх не називати GitHub Pre-release.

## Новий напрям: бібліотека шаблонів і сховище документів

- Рішення власника 13.11: **варіант Б** — каталог шаблонів матиме власний приватний source repo, але UI поки лише у Taxo; окрема програма пізніше за рішенням. Приватний repo **ще не створено**.
- Шлях за замовчуванням — **всередині вибраного Taxo workspace**, можна перемістити налаштуванням. Ніколи не зберігати в EXE install dir.
- **Одна програма інструктажів підприємства на 24 місяці** з тематичною ротацією та призначеннями тем категоріям людей; ротація не замінює нормативну періодичність.
- Документи: DOCX/PDF, довгі інструкції, вкладення, скани, цифрові підписи з окремим станом перевірки. Не плутати `paper_signed` чи скан з перевіреним КЕП.
- **Жодного розростання `main.py`**: тільки інтерфейс-підключення, логіка в окремих документованих модулях. Повторно використовувати `workspace.py`, `paper_document_store.py`, `document_catalog.py`, попередню архітектуру `DocumentVault`.
- [Docs-only draft PR #395](https://github.com/RomanZavadaM/Taxo/pull/395) містить архітектуру, сервісний контракт, JSON schema manifest та опис пакета. Не merged, без змін робочого коду.

## Не завершено

- r5 **не tagged / не GitHub Pre-release / не merged у main / не Stable**. Вимога власника: **r5 — GitHub Portable Pre-release з усіма 4 portable платформами, START і SHA256**. `docs/releases/RELEASE_NOTES_v10.18-r5.md` вже існує у r5 code head.
- Підключення бібліотеки до UI, інсталятор, корпоративні редакції, реальне сховище, перевірка підписів, навчальний календар і приватний репозиторій — ще не реалізовані. Наявний r5 reader лише читає встановлений data-only каталог.
- Спеціалізоване ручне Windows DPI 100/125/150 %, фокус/табуляція, scrollbar/кнопки, double-click і повторне відкриття для неперевірених UI-сценаріїв залишається pending; не підміняти CI.

## Одна наступна дія

**Опублікувати immutable `v10.18-r5` як GitHub Pre-release із exact r5 code head `7ee89f3f0dcb731c4b2fd416b6ddb630e3ebe7d2`**, перевірити 8 release assets, назви та checksums і `prerelease=true`. Існуючий `.github/workflows/publish-current.yml` підтримує `workflow_dispatch`, але підключені GitHub tool actions **не мають дії workflow dispatch / create release**. Для безпечного запуску через GitHub UI: Actions → **Publish current Taxo release** → Run workflow → branch `work/v10.18-r5-template-library-reader`. Перед запуском повторно звірити точний head та CI; не міняти цей head. Відсутність доступного виклику не обходити небезпечним patch release workflow. Після фактичного успішного tag/release зафіксувати у GitHub recovery. Стабільну v10.18-r3 не просувати без рішення власника.

Після повного r5 checkpoint **наступна кодова ревізія — 10.18-r6**, з перевіреного r5 exact head; не перевикористовувати `r5`.

## Recovery

`START_HERE.md` → цей файл → живий GitHub main/PR #395/#396/CI/releases → private Taxo-profile `RomanZavadaM/dev-strategy`/`profile/taxo` → `PROJECT_RULES.md`, `PROJECT_STATE.md`. Issue #61 містить хронологію. Якщо GitHub змінився — спочатку reconcile.
