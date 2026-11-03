# HANDOFF_CURRENT — Taxo

**Оновлено:** 03.11.2026

Це короткий recovery-знімок для нового чату або нового виконавця. Він замінюється при критичній зміні стану й не використовується як довгий журнал.

## База
- Repository: `RomanZavadaM/Taxo`
- Stable / Latest: `v10.10-r4`
- Previous stable / rollback: `v10.9-r10`
- Наступна кодова ревізія: `10.10-r5`
- Загальна методологія: private `RomanZavadaM/dev-strategy`, branch `profile/taxo`, файл `TAXO_PROFILE.md`
- Google Drive backup: `Taxo — Розробка — резервний комплект`

## Завершено
- `v10.10-r4` прийнято власником як Stable / Latest.
- Windows 10/11: Setup + Portable.
- Windows 7: Setup + Portable.
- macOS: ARM64 + Intel.
- START/source + SHA256 опубліковані.
- README та релізні документи синхронізовані.
- Додано універсальний механізм публікації.
- На Google Drive є повний запасний stable-комплект і snapshot current main.

## Поточний slice
Adoption dev-strategy v2 continuity:
- новий чат не відновлює роботу з пам'яті;
- після критичної зміни одразу оновлюється цей HANDOFF;
- довгі технічні деталі лишаються у WORKLOG / GitHub;
- після зависання або обриву наступник спершу звіряє GitHub і HANDOFF;
- без доступу до private Taxo-profile не виконувати зміни release/build/update/security/dependency.

## Не завершено
- Локальні процесні правила Taxo ще приводяться у відповідність до private `TAXO_PROFILE.md`.
- Бізнес-правила Taxo лишаються локальними й не переносяться в загальну методологію.

## Єдина наступна дія
Завершити continuity-adoption у `START_HERE.md`, `PROJECT_RULES.md`, `PROJECT_STATE.md` та `WORKLOG.md`, потім зробити `HANDOFF_CURRENT.md` обов'язковою другою точкою читання кожної нової сесії.

## Recovery після обриву
1. Відкрити `START_HERE.md`.
2. Відкрити цей `HANDOFF_CURRENT.md`.
3. Відкрити private Taxo-profile у `dev-strategy`.
4. Звірити live GitHub.
5. Якщо HANDOFF суперечить GitHub — GitHub має пріоритет, HANDOFF одразу виправити.
6. Продовжити лише з пункту «Єдина наступна дія».

Не читати старі чати для відновлення стану, якщо потрібний факт уже є у GitHub або HANDOFF.
