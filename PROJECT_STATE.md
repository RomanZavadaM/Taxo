## Оновлення 14.11.2026 — r7 опубліковано

Taxo **10.19-r7** завершено. Product PR #434 merged, exact source `0cfccee73eec9bcf0fbb07afc64c5d7a7949dfcc`. Test prerelease [v10.19-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.19-r7) опубліковано (publisher `43627285299` SUCCESS), 4 Portable + START + SHA256.

Результати exact-main CI: START `43625038373`, Windows `43625038453`, Win7 `43625038422`, macOS Intel+ARM `43625038460` — SUCCESS; Defender і post-scan integrity Windows/Win7 PASS.

Додано DOCX renderer/export виключно із перевіреного immutable snapshot-а, з exact provenance в metadata/footer; у preview DOCX доступний лише після успішного збереження snapshot-а. Немає PDF/print, final archive, scan/signature чи автоматичного business fact. TemplateLibrary read-only; CompanyTemplates для власних шаблонів. Stable/Latest **v10.18-r3**, без змін.

**Наступна ревізія 10.19-r8** — окремий PDF/print slice; DocumentArchive пізніше. Перед початком перевірити live GitHub.

---

# PROJECT_STATE — Taxo

**Дата:** 14.11.2026.

## Поточний підтверджений стан

Taxo інтегрував і опублікував **10.19-r6**.

- Exact product / release source: `eca31f5d61fc382cebc4663ec511619b9dcd69e7`.
- Stable/Latest: **v10.18-r3**, без змін.
- Current Test prerelease: **v10.19-r6 — Test Portable**.
- 6 assets: Windows, Windows 7, macOS Intel, macOS ARM, START, SHA256.
- Product PR #431 merged; release trigger PR #432 merged.
- Publisher `43622926821` SUCCESS.

## Реалізовано у r6

- explicit save з preview у immutable prepared snapshot;
- окреме workspace storage `Data/PreparedDocuments`;
- exact source provenance: company template ID, SHA-256 та edit revision;
- normalized facts + rendered structured content + rendered text у snapshot;
- immutable ID та відсутність update/delete API у r6;
- SHA-256/size integrity index і fail-closed перевірки вмісту;
- atomic file replacement;
- backup/restore coverage для `PreparedDocuments`;
- UI worker не читає Tk state у background thread;
- жодного автоматичного наказу/інструктажу, DOCX/PDF, final archive, scan/signature side effect;
- `TemplateLibrary` лишається read-only, `CompanyTemplates` — користувацька зона;
- feature-логіка винесена в окремі модулі, `main.py` отримав тільки version identity.

## Exact-source CI

Для `eca31f5d61fc382cebc4663ec511619b9dcd69e7`:
- START `43622027078` SUCCESS;
- Windows `43622027016` SUCCESS;
- Windows 7 `43622027066` SUCCESS;
- macOS Intel/ARM `43622027010` SUCCESS;
- Windows/Win7 Defender + post-scan integrity PASS;
- publisher `43622926821` SUCCESS;
- immutable `v10.19-r6` target = exact product source.

## Recovery / reconciliation

На початку recovery документи ще показували завершену r5, але live GitHub уже містив незавершену r6-гілку. r6 не перевикористовувалась і не починалась заново. Виявлені після обриву застарілі version/START regression guards були виправлені; snapshot design і release/security механізми не переписувалися. Final branch head `1535bd7f92facf2d636f9dc7e656653a6eea1a24` пройшов повний CI, після чого PR #431 merged.

## Наступна продуктова ревізія

**10.19-r7** — DOCX renderer/export з immutable prepared snapshot-а.

r7 має:
- брати дані з exact prepared snapshot;
- зберігати provenance snapshot/template revision;
- генерувати editable DOCX окремим модулем;
- не додавати в цей slice PDF/print;
- не створювати final DocumentArchive, scan/signature state чи автоматичний business fact.

Подальші окремі slices: PDF/print path → DocumentArchive.

## Історичний якір

Taxo 10.3 / `v10.3`, exact source `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
