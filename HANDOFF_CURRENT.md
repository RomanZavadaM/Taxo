# HANDOFF_CURRENT — Taxo

**12.11.2026 — stable 10.16-r8; останній перевірений тестовий artifact-checkpoint 10.17-r2.**

## Підтверджений стан

- **Stable/Latest: [v10.16-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.16-r8)**, immutable source `115df1c48f96e1e98d6ee3ae40e4ef48f34dacc6`. Код stable, tag/release/assets не змінювалися; `main` має код 10.16-r8.
- Попередні test checkpoints: tagged `v10.16-r9` exact `53428d4287c0f4e83a55a739109c0bd209e3a623` (draft #355), artifact `10.16-r10` exact `1b39d60a7bce22843ebab575faa7173e3c818454` (draft #357), `10.17-r1` exact `fa9ba20497cd179038129cb61ad9d72df1617cc0` (draft #359).
- **Останній test checkpoint 10.17-r2**: [draft PR #361](https://github.com/RomanZavadaM/Taxo/pull/361), branch `work/v10.17-r2-navigation-consistency`, exact HEAD `eb77fa477e75daa9a9264fbab4f07adf99184d2b` (останній commit — тільки audit-документ; кодова межа `02eb7544506fd0e5b9935d0456610c0e5ed5847a`).
- За відгуком власника знімок «Єдине планування персоналу» не має видимого виходу. У прихованих сторінках **Планування, Табель, Звіти** додано «← До реєстру працівників» через існуючий `show_personnel_overview`. У окреме вікно **Експлуатація** додано кнопку «Закрити» (лише `win.destroy`). Не змінено дані, накази чи збереження.
- Первинний статичний аудит та **черга повного ручного UI-приймання**: `docs/maintenance/UI_NAVIGATION_CONSISTENCY_AUDIT_2026-11-12.md` у PR #361. Це не підтвердження, що весь інтерфейс пройдено вручну. СТОІР — наступний потенційний приклад відсутньої явної команди виходу; перевірити інші основні екрани, модальні діалоги, сортування, DPI.
- Перевірки r2: START/source на code head `02eb754…` [43201641126](https://github.com/RomanZavadaM/Taxo/actions/runs/43201641126) — SUCCESS, **1159 tests OK**. Windows [43201864503](https://github.com/RomanZavadaM/Taxo/actions/runs/43201864503), Win7 Python 3.8 compatibility [43201864597](https://github.com/RomanZavadaM/Taxo/actions/runs/43201864597), macOS Intel/ARM [43201864313](https://github.com/RomanZavadaM/Taxo/actions/runs/43201864313) на final head `eb77fa4…` — **усі SUCCESS**.
- Перевірений Windows portable із CI artifact `13935313095`: `Taxo_v10_17_candidate_r2_Windows_x64_Portable.zip`, SHA-256 `df376eb7d1de4e7b24e035c83f88c04330fa82af8d34eaacdea497d5f7844b20`, звірений із manifest. **GitHub tag/release r2 не створено**, це тестовий artifact checkpoint.
- Код r2 не merged у main. Документаційний checkpoint не змінює продукт; stable не чіпати.

## Рішення власника

- Продовжити розпочату модульну перебудову та перевірити інтерфейс на неузгодженості, особливо очевидний вихід з екранів.
- Бібліотеку шаблонів і сховище документів **не чіпати**, до їхнього проєктування повернутися лише після завершення поточного етапу та переходу в новий чат.
- Редагування коду й UI — поступово, зрозуміло людині, без штучного скорочення файлів; зберігати дані й функції.
- Stable/Latest `v10.16-r8` залишити незмінною.

## Наступна дія

1. Нова сесія: `START_HERE.md` → цей HANDOFF → private Taxo-profile → live GitHub (main / PR #361 / CI).
2. **Наступна нова кодова ревізія 10.17-r3**: продовжити вибіркову перевірку UI за audit matrix, насамперед СТОІР, інші Toplevel та повернення; не змінювати багато модулів одночасно. r2 уже видана як тестовий артефакт і не перевикористовується.
3. Після ручного приймання власником уточнювати наступні пріоритети; заморожені документні системи не починати.

## Recovery

`START_HERE.md` → цей файл → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
