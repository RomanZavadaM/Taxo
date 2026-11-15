# HANDOFF_CURRENT — Taxo

**Підтверджено 15.11.2026 після live GitHub.**

## Поточний стан

- Завершена продуктова ревізія: **10.20-r1**.
- Product PR #446 merged; exact product/release source: `f80a1e583f896f4d0d8f63265e7ab0aadb657185`.
- Test prerelease: [v10.20-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r1), 6 assets (Windows, Win7, macOS Intel, macOS ARM, START, SHA256).
- Release-trigger PR #447 merged; release-trigger main commit `9fc246f335da4c3853e891a219fc7fdc8d839f6a`.
- Stable / GitHub Latest: **v10.18-r3**, без змін.

## Що зроблено в 10.20-r1

Prepared DOCX → PDF/друк тепер переносить підтримувані **inline-зображення** з конкретної контрольованої Word-редакції.

- inline image у звичайному абзаці потрапляє в PDF у порядку разом із текстом;
- inline image у клітинці таблиці також переноситься;
- базове вирівнювання image бере з Word-параграфа;
- вкладені image нормалізуються через вже наявний Pillow, без нової залежності;
- діють обмеження на кількість, compressed size та pixel count;
- зовнішні image links не завантажуються;
- PDF як і раніше є окремою output-копією і не змінює DOCX, catalog history або document/signature/business status.

Fail-closed залишено для layout, який Taxo ще не може відтворити безпечно: floating drawings, VML/legacy pictures, зображення у header/footer, nested/складні таблиці. Непідтриманий Word-layout не конвертується мовчки з втратою даних.

## Перевірки

- Final PR head: `1037f5923293ca4c265067537cd19cb6aa5ef589`.
- Product merge/release source: `f80a1e583f896f4d0d8f63265e7ab0aadb657185`.
- Exact-main START/source `43761081149` — SUCCESS, **1369/1369**.
- Windows `43761081164` — SUCCESS.
- Windows 7 `43761081155` — SUCCESS.
- macOS Intel + ARM `43761081179` — SUCCESS.
- Windows/Win7 Defender malware gates + post-scan integrity — PASS.
- Publisher `43762135252` — SUCCESS; release target exactly product SHA above, 6 assets.
- Stable/Latest через GitHub API: `v10.18-r3`.

## Що ще не зроблено

- Повний faithful Word-layout для floating drawings, header/footer images, VML/legacy objects і складних/nested таблиць.
- Окреме універсальне сховище готових/архівних документів (DocumentVault).
- Опціональні скани/оригінали та їх зв'язок із документом.
- Підписні докази / digital signature. Папір лишається первинним; цифровий підпис не нав'язувати.

## Одна наступна дія

**Наступна дозволена кодова ревізія: 10.20-r2.** Почати **DocumentVault core** окремим модулем: базова структура сховища/реєстру готових та архівних документів із provenance-посиланням на конкретну prepared-редакцію. Без auto-migration старих PaperDocuments, без сканів, без digital signature і без автоматичного статусу «підписано». Непідтриманий складний Word-layout поки лишається fail-closed.

Перед кодом: START_HERE → HANDOFF_CURRENT → private profile → live GitHub → READ/VERIFY/RECONCILE.

Через повторні `Error in input stream` у цій сесії **новий великий slice починати вже в новому чаті**.

Незмінні правила: TemplateLibrary read-only; власні шаблони — CompanyTemplates; main.py не роздувати; Stable/Latest змінюється тільки за прямою командою власника; executable не запускати для перевірки безпеки.
