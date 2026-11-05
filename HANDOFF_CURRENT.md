# HANDOFF_CURRENT — Taxo

**Оновлено:** 05.11.2026 (після офіційного prerelease 10.11-r2)

## База
- **Stable / Latest:** [v10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5) — підтверджена stable/rollback.
- **Current candidate line:** Taxo **10.11-r2**.
- **Виданий кандидат:** [v10.11-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.11-r2) — **prerelease**, exact issued source `68d7459b28e4ae68d97b6dd43cc92ead695a80bb`.
- Release містить **8 assets**: Windows Setup/Portable, Windows 7 Setup/Portable, macOS ARM64/Intel, START і SHA256SUMS. Tag/release не пересувати й не перезаписувати.
- Успішний publisher: workflow **#42086984364**. Release-trigger PR #172 merged; trigger main `e7bf8cdf5d61980bcd093643c20a08d4285bf6a0`.
- **Наступна кодова ревізія:** **10.11-r3**.
- Google Drive: `02_CURRENT_MAIN/Taxo_CURRENT_MAIN_v10.11-r2_2026-11-05_START.zip` завантажено і повторно підтверджено.
- CI optimization PR #142/#152 — окремий напрямок; не змішувати з UX.

## Підтверджено в 10.11-r2
- «Простий місячний графік роботи» зберігається з назвою виду `Простий_графік_роботи_YYYY-MM_<вибірка>.pdf/.xlsx`.
- Для одного працівника ім'я файлу містить прізвище та ім'я; для групи — читабельну вибірку та стабільний короткий код; для всіх — `усі-працівники`.
- Колонку **«Роль» прибрано лише з PDF** простого графіка; Excel і кадрові дані ролі зберігають.
- Не змінено plan/fact, графік водіїв, робочі БД, історію, документи та резервування.
- Regression перевіряє 30/31 день, довгі ПІБ, 1/кілька/всі працівники, різні групи та landscape A4.
- Exact-main `68d7459b`: START #42085643768, Windows #42085643914, Windows 7 #42085644022, macOS #42085643987 — **SUCCESS**.
- Логи Windows/Win7/macOS підтверджують r2-назви пакетів і відсутність активних `candidate_r1`.

## Важливий release-інцидент
Перша спроба publisher #42084574084 **правильно зупинилась до створення tag/release**: label artifact був r2, але активні build-файли ще формували внутрішні пакети `candidate_r1`. Окремий build-only PR #171 виправив назви, після чого повний CI повторено. Некоректний `v10.11-r2` не видавався.

## Єдина наступна дія
Власник тестує опублікований 10.11-r2 на реальних робочих даних. Нові виправлення — тільки з **10.11-r3**. Подальше системне спрощення інтерфейсу залишається в Issue #164; stable `v10.10-r5` не змінювати без окремого рішення власника.

## Recovery
`START_HERE.md` → цей HANDOFF → `dev-strategy/profile/taxo/TAXO_PROFILE.md` → фактичний GitHub → `PROJECT_STATE.md`. Деталі: `WORKLOG.md`, Issue #61, UX Issue #164.
