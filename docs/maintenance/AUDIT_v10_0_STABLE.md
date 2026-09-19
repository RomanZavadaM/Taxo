# Фінальний аудит Taxo 10.0 stable

**Дата:** 19.09.2026  
**Підстава:** ручне підтвердження завершення operational gate після candidate v9.1-r9.8.  
**Попередня stable:** 9.0.1  
**Нова stable:** 10.0

## Рішення

Лінія 9.1 завершена як перевірочна. Користувач підтвердив коректний результат останнього ручного сценарію та прямо дозволив:
- злити робочу гілку в `main`;
- підняти версію до 10.0;
- оформити stable release;
- побудувати виконувані пакети для Windows і обох macOS архітектур.

## Що перевірено в останньому циклі

- Windows START запускається з повністю розпакованого пакета;
- помилковий запуск неповного START-пакета обробляється контрольовано;
- місячний графік змінності має пряме відкриття PDF деталізації;
- шляхівки однієї дати/зміни використовують одну пару чергових лікаря/механіка;
- нічний рейс через 00:00 не підміняє персонал наступним днем;
- технічний «Аудит графіків…» відокремлений від «Контролю №340»;
- stable main не змінювався до явного підтвердження користувача.

## Інваріанти, які зберігаємо

- Plan != Fact;
- точні інтервали є джерелом тривалості, якщо вони задані;
- duration-only не вигадує часові межі;
- перекриття рахується union і не подвоює час;
- нові конфлікти блокуються, історія не переписується мовчки;
- відсутність не видаляє історичний план;
- П-5 не підставляє план без запиту оператора;
- робочі БД/скани/персональні файли не входять у GitHub artifacts;
- старі version tags/releases не пересуваються.

## Stable release gate — результат

Усі пункти виконані:
1. PR #29 — green і merged.
2. Release-pipeline hardening PR #30/#31 — green і merged.
3. Stable publisher run — success.
4. Source verify — **117 tests / OK**.
5. Windows — **117 tests / OK**, Setup + Portable зібрані.
6. macOS ARM64 — **117 tests / OK**, native Taxo.app зібрано й перевірено.
7. macOS Intel x86_64 — **117 tests / OK**, native Taxo.app зібрано й перевірено.
8. START/source verification — success.
9. Combined і per-platform SHA-256 manifests — success.
10. GitHub Release `v10.0` — published.

### Release identity

- tag: `v10.0`;
- target: `91c0d6365a40eb09fe40f97a2965da40b314bc15`;
- draft: no;
- prerelease: no;
- assets: 10;
- previous stable/rollback: `v9.0.1`.

Перші два publisher attempts виявили лише технічні помилки release pipeline (шлях до installer artifact і wildcard, що захоплював каталог). Самі source tests та OS executable builds у цих спробах були green. Обидві помилки виправлено окремими PR #30/#31 до фінальної успішної публікації.

## Після релізу

`main` і `v10.0` є stable source of truth. Candidate r9.8 та попередні releases лишаються історією/rollback reference; тег 9.0.1 теж не змінюється.
