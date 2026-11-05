# HANDOFF_CURRENT — Taxo

**Оновлено:** 05.11.2026

Це короткий recovery-знімок для нового чату або нового виконавця. Він замінюється при критичній зміні стану й не використовується як довгий журнал.

## База
- Repository: `RomanZavadaM/Taxo`
- Актуальний `main`: `1f6a397fdd7b218a21ffc10f3fd87d5aad566d36`
- Stable / Latest: `v10.10-r4`
- Previous stable / rollback: `v10.9-r10`
- Наступна кодова ревізія: `10.10-r5`
- Загальна методологія: private `RomanZavadaM/dev-strategy`, branch `profile/taxo`, файл `TAXO_PROFILE.md`
- Google Drive backup: `Taxo — Розробка — резервний комплект`

## Live reconciliation 05.11.2026
Після закриття сесії 03.11 у GitHub з'явився окремий draft PR #151:
- `fix(macOS): prevent startup crash in personnel navigation`;
- branch `fix/macos-personnel-navigation-command-20261104`;
- CI Windows / Windows 7 / macOS — success;
- це окрема кодова лінія для майбутньої `10.10-r5`; вона **не входить** у CI optimization slice і не змінює stable `v10.10-r4`.

Старий draft PR #142 лишається довідкою і **не зливається автоматично**.

## Активна робота
Окремий CI optimization slice розпочато від актуального `main`.

- Branch: `ci/docs-only-optimization-20261105`
- Base: `1f6a397fdd7b218a21ffc10f3fd87d5aad566d36`
- Мета: звичайні documentation-only зміни не повинні запускати важкі Windows / Windows 7 / macOS збірки.
- Повні перевірки мають зберігатися для коду, dependencies, packaging, scripts/security, workflow і release змін.
- Перед release фінальний повний контроль не послаблюється.
- Stable/version не змінюються: це process/CI maintenance, не продуктова ревізія.

## Уже перевірено
- Фактичний `main`, відкриті PR та останні Actions звірені.
- Підтверджено проблему: docs-only PR 03.11 запускав Windows, Windows 7 і macOS.
- Прочитані `START_HERE.md`, цей HANDOFF, private Taxo-profile, `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md`, Issue #61.
- PR #142 переглянуто лише як історичну довідку; його зміни не копіюються без звірки з актуальним `main`.

## Єдина наступна дія
Завершити і перевірити нові CI-фільтри на branch `ci/docs-only-optimization-20261105`, відкрити окремий draft PR і підтвердити матрицю:
1. docs-only PR — без важких платформних збірок;
2. code/workflow/security/release change — повний набір відповідних перевірок;
3. main docs-only push — без зайвих платформних/START збірок;
4. release checkpoint — повний контроль збережено.

Після підтвердження — оновити WORKLOG / Issue #61 і вирішувати інтеграцію окремо. Не змішувати з PR #151.

## Recovery після обриву
1. Відкрити `START_HERE.md`.
2. Відкрити цей `HANDOFF_CURRENT.md`.
3. Відкрити private Taxo-profile у `dev-strategy`.
4. Звірити live GitHub.
5. Якщо HANDOFF суперечить GitHub — GitHub має пріоритет, HANDOFF одразу виправити.
6. Продовжити лише з пункту «Єдина наступна дія».
