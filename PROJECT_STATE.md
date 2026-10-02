# PROJECT_STATE — Taxo

**Дата:** 02.10.2026  
**Repository:** `RomanZavadaM/Taxo`

## Поточний підтверджений стан

- **Stable:** Taxo 10.3 / `v10.3` — immutable; stable tag не пересувався.
- **Stable tag target:** `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
- **Latest integrated code checkpoint in `main`:** **Taxo 10.9-r9**.
- **Main integration:** PR #128 — cumulative 10.9-r2 → 10.9-r9.
- **Main merge commit:** `3f59544b8737cd4715d84f786e32378d87d1dd99`.
- **Exact issued r9 source/tag:** `v10.9-r9` → `a368bf3bdfd4a16cc099844b830379c5e2646c2d` — immutable.
- **r9 START:** `Taxo_v10_9_candidate_r9_START.zip`.
- **r9 START SHA-256:** `9c30bf70e8c7adc4f2560a22e2bdfa2c26d698573982de01aafa4b34bbcd62d4`.
- **r9 exact-head gates:** Windows run `36919102579` — success; macOS run `36919102540` — success.
- **Latest full multi-platform published checkpoint:** **10.9-r1 / `v10.9-r1`**.
- **Open stacked PRs from r2…r8:** closed as historical/superseded after cumulative merge.
- **Next code revision:** **10.9-r10**.
- **Live ledger:** Issue #61.

`main` тепер є єдиною канонічною кодовою лінією розвитку. Історичні fast-test tags/releases `v10.9-r2` … `v10.9-r9` не пересуваються і не перевидаються; вони зберігаються лише як immutable checkpoints. Нову роботу починати тільки від актуального `main`.

## Що інтегровано 10.9-r2 → 10.9-r9

- **10.9-r2:** незворотна історія виданих шляхівок і номерів; retention не може видалити пов'язаний факт.
- **10.9-r3:** чинність обов'язкових документів ТЗ перевіряється на весь плановий період рейсу; допускається безперервне перекриття кількома документами.
- **10.9-r4:** посилений контроль робочого часу/відпочинку, boundary gaps, overlaps, 3+9, weekly-rest spacing і двотижневий контроль.
- **10.9-r5:** 60-денний реєстр не вигадує відпочинок із невідомих хвилин; непідтверджений тахограф має нижчий пріоритет.
- **10.9-r6:** баланс персоналу/П-5, employment-aware historical selection, коректна семантика вихідних і циклів 2/2 та 3/3.
- **10.9-r7:** СТОІР — надійна хронологія одометра, fallback `work_date`, прогноз від останнього факту та захист від очевидних одиничних стрибків.
- **10.9-r8:** незмінність затверджених/підписаних наказів, безпечне оновлення відповідального, захист закріплень водій→ТЗ.
- **10.9-r9:** explicit SQLite schema compatibility baseline через `PRAGMA user_version`; future-schema guard від r9 і далі.

## Репозиторій після cleanup

- PR #128 — єдина кумулятивна точка інтеграції r2…r9 у `main`.
- PR #121–#127 закриті як historical/superseded; окремо їх більше не зливати.
- Старі work/candidate refs, tags і releases не є джерелом актуального коду.
- Історичні tags/releases залишаються незмінними для відтворюваності та rollback/audit history.
- Поточний інтегрований код береться тільки з `main`.

## Чинні інваріанти

- plan і fact зберігаються окремо;
- факт не підміняється планом без явного підтвердження там, де така підстановка дозволена;
- Бланки підтвердження діяльності є фактичними документами;
- невідомий/ручний час не перетворюється автоматично на роботу чи відпочинок;
- роль водія має датовані періоди і не дорівнює факту працевлаштування;
- видана шляхівка та історично використаний номер захищені від тихого фізичного знищення/повторного використання;
- робочі БД, SQLite, скани, кеші та персональні документи не входять у repository/release;
- historical tag/release checkpoints immutable;
- вже видана ревізія не перевикористовується; після `10.9-r9` наступна кодова ревізія — `10.9-r10`.

## Право та власність

Taxo — proprietary software.  
Правовласник: **Roman Zavada (Роман Завада), фізична особа**.  
**Copyright © 2026 Roman Zavada. All rights reserved.**

Канонічні файли: `LICENSE.md`, `COPYRIGHT.md`, `THIRD_PARTY_NOTICES.md`.

## Джерело істини при новій сесії

`START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → live GitHub state → Issue #61.

При суперечності документації з live GitHub перемагає фактичний GitHub state.
