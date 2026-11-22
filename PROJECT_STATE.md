# PROJECT_STATE — Taxo

**Підтверджено GitHub 22.11.2026 після публікації Test 10.24-r2.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, `prerelease=false`.

**Current Test:** [10.24-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r2), exact source `d07f26d8e9e9db6d33278cac5a0199e2d8ae4b50`, 8 assets, prerelease. Publisher #45064537526 — SUCCESS.

## Stable r4

Stable r4 залишається вручну прийнятою власником версією. Вона містить каталог документів, власні папки, скани/паперовий підпис, редагування учасників наказу, регульовані робочі області та адаптивний перегляд наказу. 37 strict live routes.

## Current Test 10.24-r2

r1 дав безпечний доменний реєстр incoming/outgoing з окремою нумерацією. r2 додає контрольовані вкладення:
- окремий immutable attachment store;
- SHA256/MIME/size/original filename/stable attachment ID;
- content-addressed dedupe;
- live DocumentVault links без byte copy;
- PDF/JPG/PNG/TIFF/DOCX content validation;
- macro/unsafe/symlink/orphan/missing/tampered fail-closed;
- history-only remove без фізичного видалення байтів;
- full backup/restore registry + attachments + history + numbering;
- attachment presence не змінює бізнес-стан листа.

Exact-source CI `d07f26d8e9e9db6d33278cac5a0199e2d8ae4b50`: START #45063475205, Windows #45063475214, Win7 #45063475185, macOS Intel/ARM #45063475161 — SUCCESS; Windows/Win7 Defender + post-scan integrity PASS; publisher #45064537526 — SUCCESS.

## AI-ready archive path

r6 INVENTORY → r7 batch store → r8 verified preview → r9 ANALYZE/PROPOSE → r10 REVIEW. Цикл лишається без APPLY; source, batch, DocumentVault/БД і паперовий підпис не змінюються. APPLY — тільки після окремого рішення власника.

## Наступна ревізія

**10.24-r3:** UI журналів і картка кореспонденції поверх уже перевірених r1+r2 API. Окреме вікно incoming/outgoing, пошук/дата, таблиця, детальна картка, створення/відповідь/вкладення/відкриття документа, нормальний resize і явні Close/Cancel. Ніякого автоматичного sent/received або e-mail automation. E-mail/OCR/AI/cases — пізніше.

#553/#556/#562 залишаються відкритими. Draft #543/#395 не закривати автоматично.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
