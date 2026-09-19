# Taxo — індекс опублікованих релізів

**Стан перевірено:** 19.09.2026  
**Поточний stable:** [Taxo 9.0.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.0.1)  
**Поточний candidate:** [Taxo 9.1 candidate r9.4](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.4)  
**Робочий PR:** [#29](https://github.com/RomanZavadaM/Taxo/pull/29)

> Stable `main` залишається на Taxo 9.0.1 до завершення ручного operational gate.  
> Candidate-теги є історичними контрольними точками: їх не пересувати і не перезаписувати.

## Актуальна лінія 9.x

| Tag | Статус | Пакети | Призначення |
|---|---|---|---|
| [v9.1-r9.4](https://github.com/RomanZavadaM/Taxo/releases/tag/v9.1-r9.4) | Pre-release, поточний candidate | START + SHA-256 | Передетапна стабілізація, «Аудит графіків…», П-5, архів бланків, місячний контроль |
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

## Поточна контрольна точка r9.4

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
6. Нові кодові контрольні точки після r9.4 повинні отримувати новий tag/release.

## Перед stable 9.1

Залишається ручний operational gate на реальній Windows-базі. Його чекліст зафіксовано в:
- [AUDIT_v9_1_r9_4.md](../maintenance/AUDIT_v9_1_r9_4.md);
- [NEW_CHAT_HANDOFF_v9_1_r9_4.md](../maintenance/NEW_CHAT_HANDOFF_v9_1_r9_4.md).

До завершення gate PR #29 не зливати у `main`.
