# Taxo — індекс опублікованих релізів

**Стан перевірено:** 19.09.2026  
**Поточний stable:** [Taxo 9.0.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0.1)  
**Поточний candidate:** Taxo 9.1 candidate r9.8 — публікується після зеленого CI  
**Робочий PR:** [#29](https://github.com/RomanZavadaM/Taxo/pull/29)

> Stable `main` залишається на Taxo 9.0.1 до завершення ручного operational gate.  
> Candidate-теги є історичними контрольними точками: їх не пересувати і не перезаписувати.

## Актуальна лінія 9.x

| Tag | Статус | Пакети | Призначення |
|---|---|---|---|
| v9.1-r9.8 | **Current candidate — pending publication after CI** | START + SHA-256 | Єдиний лікар/механік на дату+зміну у шляхівках |
| [v9.1-r9.7](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.7) | Pre-release | START + SHA-256 | «Відкрити деталізацію» у місячному графіку змінності |
| [v9.1-r9.6](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.6) | Pre-release | START + SHA-256 | ASCII/CRLF START.bat, real Windows full/incomplete preflight |
| [v9.1-r9.5](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.5) | Pre-release, **known broken START on real Windows** | START + SHA-256 | Не використовувати для manual gate; CMD parsing regression |
| [v9.1-r9.4](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.4) | Pre-release | START + SHA-256 | Передетапна стабілізація, «Аудит графіків…», П-5, архів бланків, місячний контроль |
| [v9.1-r9.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.3) | Pre-release | START + SHA-256 | П-5, архів бланків, місячний контроль |
| [v9.1-r9.2](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.2) | Pre-release | START + SHA-256 | Статуси відсутностей, попередній аудит графіків |
| [v9.1-r9.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.1) | Pre-release | START + SHA-256 | Сумісність канонічного ядра |
| [v9.1-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9) | Pre-release | START + SHA-256 | Канонічні точні інтервали та union перекриттів |
| [v9.1-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r8) | Pre-release | START + SHA-256 | Єдиний стан дня в Табелі / Графіку |
| [v9.1-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r7) | Pre-release | START + SHA-256 | Hardening планування за режимом |
| [v9.1-r6](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r6) | Pre-release | Windows Setup/Portable, macOS ARM64/Intel, START, SHA-256 | Режими робочого часу |
| [v9.1-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r5) | Pre-release | Windows Setup/Portable, macOS ARM64/Intel, START, SHA-256 | Експлуатаційний кандидат 9.1 |
| [v9.0.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0.1) | **Stable / rollback point** | Windows Setup/Portable, macOS ARM64/Intel, START, SHA-256 | Поточна стабільна експлуатаційна версія |
| [v9.0](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0) | Stable history | Windows Setup/Portable, macOS ARM64/Intel, START, SHA-256 | Базовий реліз лінії 9.x |

## Щодо r1–r4

`v9.1-r1`–`v9.1-r4` **не публікуються окремими GitHub Releases навмисно**. Це проміжні кандидатні стани з уже відомими та виправленими проблемами; їхня історія збережена в Git/PR #29. Публікувати їх заднім числом означало б створити хибні контрольні точки, тому release-лінія 9.1 починається з опублікованого `v9.1-r5`.

## Історичні 8.x Releases

GitHub також зберігає опубліковані історичні релізи:
- [v8.70-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.70-r9);
- [v8.70-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.70-r8);
- [v8.70](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.70);
- [v8.65](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.65);
- [v8.64](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.64);
- [v8.56](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.56).

Ці релізи не є поточною експлуатаційною рекомендацією. Вони зберігаються для історії та відтворюваності.

## Поточна контрольна точка r9.8

- шляхівки одного дня отримують один day-duty map;
- overnight route не підхоплює staff наступної дати;
- role+date+shift — один slot для одного АТП;
- duplicate legacy slots стають explicit conflict;
- release публікується після зеленого CI.

## Попередня контрольна точка r9.7

- у «Місячному графіку змінності водіїв» додано `Відкрити деталізацію`;
- дія формує актуальний detail PDF і одразу відкриває його;
- behavioral regression test перевіряє exporter і open_external;
- START hardening r9.6 збережено;
- release target: `8a16ef781e1b3334e664449725c217a120f9fe5d`;
- START: [Taxo_v9_1_candidate_r9_7_START.zip](https://github.com/RomanZavadaM/Taxo/releases/download/v9.1-r9.7/Taxo_v9_1_candidate_r9_7_START.zip);
- SHA-256: [SHA256SUMS_v9_1_candidate_r9_7.txt](https://github.com/RomanZavadaM/Taxo/releases/download/v9.1-r9.7/SHA256SUMS_v9_1_candidate_r9_7.txt);
- Windows/macOS: 107 regression tests — success;
- source package + publisher — success.

## Попередня контрольна точка r9.6

- START.bat: ASCII-only, без chcp, Windows CRLF;
- full-folder Windows preflight + incomplete-folder guard;
- source ZIP verification контролює encoding/line endings;
- функціональний baseline r9.4 не змінюється;
- release target: `49d36f5140986f54639835164a3ba22cf28323b7`;
- START: [Taxo_v9_1_candidate_r9_6_START.zip](https://github.com/RomanZavadaM/Taxo/releases/download/v9.1-r9.6/Taxo_v9_1_candidate_r9_6_START.zip);
- SHA-256: [SHA256SUMS_v9_1_candidate_r9_6.txt](https://github.com/RomanZavadaM/Taxo/releases/download/v9.1-r9.6/SHA256SUMS_v9_1_candidate_r9_6.txt);
- Windows/macOS: 105 regression tests — success;
- Windows full/incomplete START preflight — success;
- source package + publisher — success.

## Попередня контрольна точка r9.5

- release tag: `v9.1-r9.5`;
- release target: `f587c2cad71a22c6bded3a992fd27797c1e2c296`;
- START: [Taxo_v9_1_candidate_r9_5_START.zip](https://github.com/RomanZavadaM/Taxo/releases/download/v9.1-r9.5/Taxo_v9_1_candidate_r9_5_START.zip);
- SHA-256: [SHA256SUMS_v9_1_candidate_r9_5.txt](https://github.com/RomanZavadaM/Taxo/releases/download/v9.1-r9.5/SHA256SUMS_v9_1_candidate_r9_5.txt);
- Windows: 101 regression tests + START guard simulation — success;
- macOS ARM64: 101 regression tests — success;
- macOS Intel x86_64: 101 regression tests — success;
- source package + publisher — success.

r9.5 є пакувально-запускним hotfix поверх функціонального baseline r9.4. Для тестування ZIP потрібно спочатку повністю розпакувати.

## Попередня функціональна контрольна точка r9.4

- release tag: `v9.1-r9.4`;
- release target: `3da975ff3dc30740aeaf300d9e3471415075dbe0`;
- post-release documentation head: `c4461e779f07639042f1348d7f61e14f6dc99df3` на момент handoff;
- різниця між release target та handoff checkpoint була лише документаційною;
- Windows: 97 regression tests — success;
- macOS ARM64: 97 regression tests — success;
- macOS Intel x86_64: 97 regression tests — success;
- START package — success;
- release publisher — success.

## Політика публікації

1. Stable реліз формується лише після завершення ручної експлуатаційної перевірки.
2. Дрібні candidate-кроки публікуються як source/START, якщо немає потреби перевипускати executable packages.
3. Windows/macOS executable packages випускаються на визначених контрольних точках.
4. Старі candidate tags/releases не пересуваються, не видаляються і не перезаписуються.
5. Робочі SQLite-бази, скани, кеші та персональні документи до релізів не включаються.
6. Нові кодові контрольні точки після r9.8 повинні отримувати новий tag/release.

## Перед stable 9.1

Залишається ручний operational gate на реальній Windows-базі. Його чекліст зафіксовано в:
- [AUDIT_v9_1_r9_5.md](../maintenance/AUDIT_v9_1_r9_5.md);
- [AUDIT_v9_1_r9_4.md](../maintenance/AUDIT_v9_1_r9_4.md) — функціональний baseline;
- [NEW_CHAT_HANDOFF_v9_1_r9_4.md](../maintenance/NEW_CHAT_HANDOFF_v9_1_r9_4.md).

До завершення gate PR #29 не зливати у `main`.
