# Taxo — технічний стан: stable 9.0.1 / candidate 9.1 r9.6

Канонічний технічний стан експлуатаційної лінії: **stable 9.0.1**. Поточна гілка перевірки — **Taxo 9.1 candidate r9.6**, PR #29.

## Головний принцип

Stable 9.0.1 лишається точкою відкату. Кандидат r9.6 не зливається в main до завершення ручної експлуатаційної перевірки. Історичні дані користувача не переписуються автоматично заради виправлення старих конфліктів.

## Ключові зміни лінії 9.1

- окремий модуль персоналу, ролі та режими робочого часу;
- масове планування і масові відсутності;
- канонічні інтервали водійського графіка;
- П-5 PDF/XLSX з явним рішенням щодо плану замість факту;
- місячний контроль і деталізація;
- фільтрований архів бланків;
- аудит часових помилок у графіках і маршрутах.

## r9.4 — стабілізація аудиту графіків

- «Перевірити графіки» замінено на зрозумілий «Аудит графіків…»;
- результат поточного дня видно прямо на добовому графіку;
- область аудиту вибирається користувачем;
- legacy exact worklog без work_segments також перевіряються;
- у результатах дня показується маршрут;
- порожні часові частини і активні маршрути без сценарію виявляються;
- технічний аудит чітко відділено від нормативного контролю №340.

## Build/release audit

- `taxo_app.py`, `v91_features.py`, `personnel_v91.py`, `Taxo.spec`, `Taxo_macos.spec` синхронізовані з r9.4;
- `installer/Taxo.iss`, BUILD_WINDOWS/BUILD_MACOS/BUILD_INSTALLER синхронізовані з r9.4;
- поточні Windows/macOS workflow-артефакти більше не називаються v8.70/r11;
- release source workflow має створювати новий immutable tag, а не рухати попередній;
- START-пакет перевіряється на відсутність SQLite/кешів.

## Тести

Основні регресійні набори: `tests/test_v9_1*.py`, включно з `tests/test_v9_1_r9_4.py` для областей аудиту, legacy exact rows, маршрутних перекриттів, порожніх частин та маршрутів без сценарію.

## Відомі межі

- технічний аудит графіків не замінює контроль Положення №340;
- GUI layout/зручність остаточно підтверджуються ручною перевіркою на робочому Windows-середовищі;
- автоматична корекція історичних конфліктів навмисно відсутня;
- stable main не оновлюється автоматично після успішного CI.

Повний передетапний звіт: [AUDIT_v9_1_r9_4.md](AUDIT_v9_1_r9_4.md).

## Публікаційний стан

GitHub оформлено і перевірено після r9.4:
- release `v9.1-r9.4` опублікований із START + SHA-256;
- release target — `3da975ff3dc30740aeaf300d9e3471415075dbe0`;
- усі підготовлені 9.x release-контрольні точки опубліковані;
- `Protect main` і `Protect releases` активні;
- post-release documentation commits не змінюють код r9.4;
- manual operational gate лишається відкритим.

Деталі: [GITHUB_PUBLICATION_SUMMARY_v9_1_r9_4.md](GITHUB_PUBLICATION_SUMMARY_v9_1_r9_4.md) та [RELEASE_INDEX.md](../releases/RELEASE_INDEX.md).


## r9.5 — START package hotfix

- рання перевірка `requirements.txt` / `taxo_app.py` у START;
- явне пояснення помилки запуску з ZIP;
- `00_README_START.txt` у корені пакета;
- `release_naming.py` для коректних назв r9.4/r9.5;
- source package перевіряє обов'язкові файли;
- Windows CI відтворює неповне extraction-середовище;
- функціональний код r9.4 не змінено.

Деталі: [AUDIT_v9_1_r9_5.md](AUDIT_v9_1_r9_5.md).


## r9.6 — Windows CMD compatibility (published)

- r9.5 manual test показав parsing corruption самого BAT у повністю розпакованій папці;
- START.bat тепер ASCII-only + CRLF, без chcp;
- Windows CI запускає full-folder preflight і incomplete-folder guard;
- source package CI контролює encoding/line endings;
- r9.5 не використовувати для manual gate;
- функціональна логіка r9.4 не змінена.


### r9.6 publication

- release target — `49d36f5140986f54639835164a3ba22cf28323b7`;
- START + SHA-256 published;
- 105 tests OK on Windows, macOS ARM64, macOS Intel;
- Windows complete/incomplete START preflight OK;
- `main` remains 9.0.1.
