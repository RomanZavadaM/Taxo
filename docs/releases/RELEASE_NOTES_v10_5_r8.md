# Taxo 10.5-r8 — Windows 7 / XLSX `tabId` compatibility checkpoint

## Чому з’явилась r8

Під час повного багатоплатформного checkpoint для 10.5-r7 окремий gate Python 3.8 / Windows 7 показав, що openpyxl на цій лінії формує коротший текст `TypeError`: без слова `ChildSheet`, але з тим самим `unexpected keyword argument 'tabId'`. r7 вже була видана і залишається immutable, тому виправлення оформлено новою ревізією r8.

## Виправлено

- сумісність імпорту XLSX «Шлях» з Python 3.8 / Windows 7;
- безпечний retry активується лише для `TypeError` з `unexpected keyword argument` і `tabId`;
- вихідний XLSX не переписується — очищення службового атрибута відбувається тільки в пам’яті;
- regression fixture більше не залежить від того, чи openpyxl включив назву `ChildSheet` у текст помилки.

## Не змінювалось

Бізнес-логіка r7, локальний цикл звіряння через Дію, робочі/державні snapshot реєстрів, військово-транспортна відомість і правила план/факт не змінювались.

## Release gate

Перед злиттям у `main` r8 має пройти повний regression на сучасному Windows, Windows 7 compatibility line (Python 3.8), macOS ARM64/Intel та START packaging.
