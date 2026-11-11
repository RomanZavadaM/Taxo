# HANDOFF_CURRENT — Taxo

**11.11.2026 — stable r8, наступний перевірений тестовий checkpoint r9.**

## Підтверджений стан

- **Stable/Latest: [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8)**, immutable source `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`, 8 assets (2 Windows installer EXE, 4 portable, START/source, SHA256); stable promotion CI [43077702929](https://github.com/RomanZavadaM/Taxo/actions/runs/43077702929) SUCCESS. Попередня stable [v10.15-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.15-r5) збережена для rollback.
- **`main` залишається на коді 10.16-r8**, на старті цього slice HEAD `be1650cde2061bc51faa85c6087999e3efc9c34f`, після документного checkpoint оновиться лише документаційно. Платформні CI для r8 зелений.
- **Новий тестовий [v10.16-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r9)**, draft [PR #355](https://github.com/RomanZavadaM/Taxo/pull/355), exact code head/tag `53428d4287c0f4e83a55a739109c0bd209e3a623`. Винесено **картку водія** із `driver_registry_ui.py` до `driver_form_ui.py`; публічний сумісний виклик `driver_registry_ui.driver_form` і поведінку ролей, дат та SQLite збережено. Новий regression тест + START guard. CI exact-head: START/source [43085532694](https://github.com/RomanZavadaM/Taxo/actions/runs/43085532694), Windows [43085597365](https://github.com/RomanZavadaM/Taxo/actions/runs/43085597365), Win7 Python 3.8 compatibility [43085597651](https://github.com/RomanZavadaM/Taxo/actions/runs/43085597651), macOS Intel/ARM [43085597241](https://github.com/RomanZavadaM/Taxo/actions/runs/43085597241) — **всі SUCCESS**. Окремий release publisher [43086357353](https://github.com/RomanZavadaM/Taxo/actions/runs/43086357353) SUCCESS: 4 portable ZIP + START/source ZIP + SHA256, рівно 6 assets; без інсталяторів, Stable/Latest залишилась r8. Код r9 НЕ merged у main.
- Відкладена попередня неуспішна/незавершена гілка `work/v10.16-r9-order-editor-presets` exact head `6a1f03c0c397e11125c15a32c1bd339170115f5f` **не є виданою r9** і не повинна зливатися; вона виникла до зміни пріоритету власником.

## Рішення власника

- Роботу іншого ШІ над історичним архівом наказів **ігнорувати** у поточній розробці; не брати його незавершені матеріали в гілки Taxo.
- **Відкласти бібліотеку шаблонів і сховище документів** до нової команди. Їхня архітектура зафіксована в `docs/planning/`; зараз її не реалізовувати, не змінювати.
- Продовжувати **модульну структурну перебудову інших систем**, не скорочувати код заради кількості рядків, зберігати читабельність і повний захист вже робочих функцій.

## Наступна дія

1. На наступній сесії: `START_HERE.md` → HANDOFF → private Taxo-profile → live GitHub (main/PR #355/CI/release).
2. Стабільна основа для rollback — r8. Наступна **нова кодова ревізія: 10.16-r10** (r9 вже видана й не перевикористовується).
3. Вибрати безпечний наступний модульний крок **поза шаблонами та архівом документів**; повні regression/START/portable до показу тестової версії; stable не змінювати без прямої команди.

## Recovery

`START_HERE.md` → цей файл → приватний Taxo-profile → live GitHub → `PROJECT_STATE.md`.
