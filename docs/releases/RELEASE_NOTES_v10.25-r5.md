# Taxo 10.25-r5 — наскрізне контрольне приймання Інструктажів

**Статус:** Test candidate. Stable/Latest залишається 10.24-r9 до окремого прямого рішення власника.

## Призначення

10.25-r5 не додає нових бізнес-правил. Це фінальний контрольний етап лінії 10.25, який одним synthetic workspace зв'язує функціонал r1–r4 і перевіряє його після повного backup/restore.

## Наскрізний сценарій

- program revision 1;
- regular planned session із frozen працівниками;
- exact prepared DOCX у PaperDocuments + session link + SHA-256;
- program revision 2 без переписування старого planned session;
- повне повторне читання planning/output stores з диска;
- event session на revision 2 з обов'язковою підставою;
- event prepared DOCX;
- explicit manual conducted fact з фактичною датою і paper evidence note;
- regular planned session не закривається event-ом і як похідний стан стає overdue;
- quarter view відкриває exact r1 для regular plan і exact r2 для event;
- full workspace backup → restore у чистий root;
- повна рівність planning state, prepared-output links і PaperDocuments records;
- побайтовий SHA-256 обох DOCX після restore;
- повтор того самого regular plan після restore не створює третій session або третій DOCX;
- generated DOCX / paper_signed=false ніколи автоматично не створює conducted fact.

## Віртуальне приймання до candidate

- 2/2 нових r5 end-to-end controls PASS;
- повний prep START: **1734/1734 PASS**;
- Windows, Windows 7 Python 3.8, macOS Intel/ARM — SUCCESS;
- Defender/integrity PASS;
- реальна база власника не відкривалась.

Candidate повторно проходить START/Windows/Win7/macOS + Defender/integrity, після merge — exact-source CI і лише потім окремий immutable `v10.25-r5` Test release.

## Після r5

Після Test release потрібне ручне owner acceptance UI. Лише після цього вирішувати, чи закривати Issue #237 і переходити до наступного великого блоку — єдиного сховища документів.

Не входять у r5: КЕП, автоматичне `conducted`, OCR/AI APPLY, автоматичне визначення законодавчої періодичності, фізичне видалення історії, СТОІР/склад, поштові чи зовнішні синхронізації.
