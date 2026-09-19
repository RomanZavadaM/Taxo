# Taxo — поточна контрольна точка

**Stable:** Taxo 9.0.1 · 17.09.2026.
**Current candidate:** Taxo 9.1 candidate r9.8 · 19.09.2026.
**Development PR:** #29.

Stable 9.0.1 залишається експлуатаційною точкою відкату. Candidate r9.8 опублікований як окремий GitHub Pre-release і не оголошується stable до завершення реальної перевірки.

## Що входить у r9.5

- модуль «Персонал», режими робочого часу і тижневий баланс;
- актуалізована типова форма № П-5 у PDF/XLSX;
- явний вибір перед підстановкою плану замість відсутнього факту;
- канонічний розрахунок часових інтервалів як union без подвійного рахунку перекриттів;
- превентивне блокування нових перекриттів у днях, маршрутах і копіюванні;
- фільтри архіву бланків підтвердження діяльності;
- розширена панель місячного контролю водія з деталізацією;
- центр **«Аудит графіків…»** з областями день / місяць / шаблони маршрутів / місяць+маршрути;
- перевірка legacy exact worklog, порожніх частин і активних маршрутів без часового сценарію;
- синхронізовані build/spec/installer-реквізити поточного кандидата.

## Дані

r9.4 не виконує масового переписування історичних worklog/work_segments. Нові поля П-5 додаються до схеми адитивно. Робочі бази, тахокарти, скани та персональні документи не входять у GitHub-релізи.

## Релізна політика

- попередні теги r9/r9.1/r9.2/r9.3 незмінні;
- r9.4 отримує новий окремий immutable tag;
- для r9.4 достатній START/source pre-release; виконувані пакети не формуються на кожній дрібній кандидатній точці;
- main не зливається до ручної перевірки.

## Автоматична перевірка

97 regression tests успішно пройдено на Windows, macOS ARM64 та macOS Intel. START/source package workflow також проходить.

## Перед наступним етапом

Повний технічний аудит зафіксований у [AUDIT_v9_1_r9_4.md](AUDIT_v9_1_r9_4.md). Після зелених CI і ручного тесту реальних сценаріїв приймається окреме рішення про наступний stable.

## GitHub publication checkpoint

- `v9.1-r9.4` опублікований і залишається pinned до `3da975ff3dc30740aeaf300d9e3471415075dbe0`;
- усі підготовлені 9.x releases опубліковані; draft-релізів немає;
- r1–r4 навмисно не публікуються як окремі Releases, бо були проміжними станами з відомими виправленими проблемами;
- повний список: [RELEASE_INDEX.md](../releases/RELEASE_INDEX.md);
- зведення публікації: [GITHUB_PUBLICATION_SUMMARY_v9_1_r9_4.md](GITHUB_PUBLICATION_SUMMARY_v9_1_r9_4.md).

Після release r9.4 допускаються документаційні commits без зміни `VERSION.txt`; вони не рухають історичний tag і не створюють нову кодову версію.


## Hotfix r9.5

r9.5 виправляє START-пакет: запуск прямо з ZIP тепер блокується зрозумілим повідомленням, додано `00_README_START.txt`, виправлено імена dotted candidate archives та додано Windows regression simulation. Функціональна поведінка r9.4 збережена.


## GitHub release r9.5

- `v9.1-r9.5` опублікований;
- immutable target: `f587c2cad71a22c6bded3a992fd27797c1e2c296`;
- START + SHA-256 доступні в GitHub Release;
- Windows/macOS: 101 regression tests — success;
- START guard simulation на Windows — success.


## Hotfix r9.6

r9.5 виявився непридатним для manual gate на реальному Windows через CMD parsing regression. r9.6 переводить START.bat у ASCII-only/CRLF, прибирає chcp і додає реальні Windows full/incomplete preflight tests. r9.5 залишається immutable історичним release.


## GitHub release r9.6

- `v9.1-r9.6` опублікований;
- immutable target: `49d36f5140986f54639835164a3ba22cf28323b7`;
- START + SHA-256 доступні в GitHub Release;
- Windows/macOS: 105 regression tests — success;
- Windows full/incomplete START preflight — success;
- r9.5 не використовувати для manual gate.


## Candidate r9.7

- у місячному графіку додано `Відкрити деталізацію`;
- кнопка формує актуальний detail PDF і одразу відкриває його;
- додано behavioral regression test;
- START hardening r9.6 не змінено.


## GitHub release r9.7

- `v9.1-r9.7` опублікований;
- immutable target: `8a16ef781e1b3334e664449725c217a120f9fe5d`;
- START + SHA-256 доступні;
- Windows/macOS: 107 regression tests — success;
- нова кнопка «Відкрити деталізацію» покрита regression test.


## Candidate r9.8

- one ATP: role+date+shift = one duty slot;
- шляхівки використовують staff дати графіка, а не всього рейсового інтервалу;
- night route next-day contamination усунено;
- legacy duplicate slots блокують видачу до ручного виправлення.


## GitHub release r9.8

- `v9.1-r9.8` опублікований;
- immutable target: `c13e3dfc8b2934876e2068809123b65d729b58b9`;
- START + SHA-256 доступні;
- Windows/macOS: 111 tests — success;
- overnight duty-staff regression і legacy duplicate conflict tests — success.
