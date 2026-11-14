# HANDOFF_CURRENT — Taxo

**Актуально на 14.11.2026.**

## Поточний стан

- Поточний продуктовий checkpoint: **10.19-r1**.
- Exact release source: `c1357d6ba84e521bfa332f99024fbc85c8304ec3`.
- **Stable / Latest:** `v10.18-r3` — без змін.
- **Поточний тестовий реліз:** `v10.19-r1 — Test Portable`.
- r1 prerelease містить 6 assets: Windows x64 Portable, Windows 7 x64 Portable, macOS Intel Portable, macOS ARM Portable, START і SHA256.
- Після product commit у `main` є лише release/recovery/documentation maintenance; код r1 не змінювався.

## 10.19-r1 — що завершено

1. Початкова `TemplateLibrary` лишається read-only.
2. Користувач може явно створити власну копію шаблону в `CompanyTemplates`.
3. Власна копія зберігає походження: package/template/revision/SHA-256.
4. Випадкове дублювання тієї самої редакції блокується.
5. Пошкодження власної копії або індексу виявляється перевіркою цілісності.
6. `TemplateLibrary` і `CompanyTemplates` входять у повну резервну копію; symlink у цих зонах відхиляється.
7. Storage/business-логіка лишається поза `main.py`.
8. Редактор власної копії, формування Word/PDF і архів готових документів у r1 **ще не реалізовані**.

## Перевірки exact release source

Для `c1357d6ba84e521bfa332f99024fbc85c8304ec3`:
- START/source — `43592182090` SUCCESS;
- Windows — `43592182079` SUCCESS;
- Windows 7 — `43592182138` SUCCESS;
- macOS Intel + ARM — `43592182091` SUCCESS;
- Windows і Windows 7 — Microsoft Defender PASS;
- після malware scan — integrity/hash verification PASS.

Publisher:
- `43592683925` — SUCCESS;
- immutable tag/release: `v10.19-r1`;
- release target = exact product source `c1357d6ba84e521bfa332f99024fbc85c8304ec3`.

Історичний Firefox verdict для 10.18-r8 не переоцінюється: r8 не перевидавати.

## Нове правило релізів від 14.11.2026

Якщо для нової ревізії вже успішно виконано повний набір збірок на одному exact source SHA — START, Windows, Windows 7, macOS Intel і macOS ARM — і security/integrity gates пройдені, таку ревізію не залишати лише внутрішнім checkpoint: **опублікувати immutable Test prerelease з готових exact-SHA артефактів**.

- Повторно збирати ті самі артефакти лише заради публікації не потрібно.
- Це правило не переводить реліз у Stable.
- **Stable/Latest змінюється тільки за прямим рішенням власника.**
- Якщо для ревізії вже існує immutable release, службові docs/release commits з тим самим номером не створюють другий реліз.

## Одна наступна дія

**Наступна кодова ревізія — 10.19-r2.**

Перший slice: редактор **власної** копії шаблону в `CompanyTemplates`:
- початковий vendor template не редагувати;
- підтримати великі тексти;
- Save / Cancel / X з контролем незбережених змін;
- зберегти модульність і не переносити редактор/storage-логіку в `main.py`;
- Word/PDF/DocumentArchive поки не змішувати в цей slice.

## Незмінні правила

- Виданий номер ревізії не переписувати й не використовувати повторно.
- Не просити власника вручну запускати CI/build, якщо це можна виконати через GitHub.
- Код має бути модульним, читабельним для людини; скорочення коду не є ціллю.
- Recovery: `START_HERE.md` → цей файл → `PROJECT_STATE.md` → live GitHub → Issue #61.
