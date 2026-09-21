# Фінальний аудит Taxo 10.1 stable

**Дата:** 21.09.2026  
**Попередня stable:** Taxo 10.0  
**Перевірений кандидат:** v10.1-r5  
**Candidate target:** `146d00916cb953efbcf7d3b167b7f5547d67f0b0`

## Рішення
Після ручної Windows-перевірки користувач прямо підтвердив merge у `main`, promotion до **Taxo 10.1 stable**, multi-platform build, START/source, SHA-256, GitHub Release і документацію.

## Ручний Windows gate
У r4 було виявлено циклічне відкриття повного branded-вікна через «Звіти». У r5 «Звіти» переведено у головний workspace, «Працівники» повертає реєстр, детальний табель став single-instance, а дубльований sidebar прибрано. Після повторної перевірки користувач підтвердив stable promotion.

## Автоматичний candidate gate
- source/START — **157 tests / OK**;
- Windows — **157 tests / OK** + START preflight OK;
- macOS ARM64 — **157 tests / OK**;
- macOS Intel x86_64 — **157 tests / OK**.

## Stable gate
Stable publisher повинен повторно виконати suite з `Version: 10.1`, зібрати Windows Setup/Portable, macOS ARM64/Intel, START/source, перевірити відсутність БД, сформувати SHA-256 і опублікувати immutable `v10.1`.

## Інваріанти
- Plan != Fact;
- exact intervals > duration-only;
- historical conflicts не переписуються автоматично;
- П-5 не підставляє план без явного рішення оператора;
- employment state != driver role;
- user DB не входить у release;
- старі tags/releases не пересуваються.
