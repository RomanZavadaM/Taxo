# Taxo — adoption dev-strategy v2 continuity

Дата: 03.11.2026

## База

Загальний стандарт: `RomanZavadaM/dev-strategy` v2 RC.  
Поточний main, прочитаний під час adoption: `2e9b1251d64d0837a1b2e45cbbe3f1f815e8b576`.  
Приватний Taxo-profile: branch `profile/taxo`, файл `TAXO_PROFILE.md`.  
Початковий commit профілю: `85d6cbd38ef37dcc429251000d7b42b8582e21ef`.

## Що Taxo приймає

- короткий `HANDOFF_CURRENT.md`;
- recovery без старого чату;
- reconciliation після обриву або невідомого результату;
- атомарні відновлювані checkpoints;
- негайне оновлення HANDOFF після merge/release/incident/owner decision;
- WORKLOG як технічна історія, а не перша сторінка нового чату;
- приватний Taxo-profile для process/security/release деталей;
- людський формат звіту власнику.

## Що не переноситься в загальну методологію

Бізнес-інваріанти Taxo:
- plan/fact;
- бланки підтвердження;
- робочий час;
- правила ролі водія;
- шляхівки;
- документи ТЗ;
- інші доменні правила.

Вони лишаються у локальних документах Taxo.

## Recovery contract

Нова сесія:
`START_HERE.md` → `HANDOFF_CURRENT.md` → private Taxo-profile → live GitHub.

Якщо чат і документи суперечать GitHub — спершу reconciliation, потім робота.

## Наступна перевірка методології

Після інтеграції continuity окремий виконавець/розробник Taxo має провести read-only review dev-strategy + Taxo-profile і дати feedback. Методологію під час review не змінювати; спочатку рішення власника.
