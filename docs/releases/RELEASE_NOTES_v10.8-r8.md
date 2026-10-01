# Taxo 10.8-r8 — fast-test

**Статус:** кандидат для тестування / prerelease.  
**База:** immutable `v10.8-r7`.  
**Stable:** `v10.3` не змінюється.

## Навіщо ця ревізія

Taxo буде суттєво розширюватися. Після r7 нові функціональні шари вже мають впорядковану точку композиції, але старий контракт feature-модулів усе ще давав їм увесь глобальний namespace `main`.

`10.8-r8` вводить вузький application-services context, щоб нові модулі могли отримувати тільки потрібну інфраструктуру і не нарощувати нові приховані залежності від великого `main.py`.

## Що змінено

- додано `application_context.py`;
- `WorkspaceServices` надає актуальний workspace root, paths і connection до головної SQLite DB;
- workspace paths не кешуються — після переключення сховища новий код бачить актуальну БД;
- `OutputServices` надає спільні file-output операції;
- `ApplicationServices` об'єднує інфраструктурний контракт і поточну версію;
- `FeatureLayer` підтримує explicit `uses_services=True` для нових context-aware модулів;
- старі installer signatures не змінено;
- після композиції `App.services` містить application context;
- `taxo_app.py` створює один context і передає його у feature registry;
- `START.bat` та source-package verification вимагають `application_context.py`;
- додано `tests/test_v10_8_r8.py`;
- додано `docs/maintenance/AUDIT_APPLICATION_CONTEXT_v10.8-r8.md`.

## Архітектурне правило

Application context містить лише спільну інфраструктуру. У нього не переносяться plan/fact, табель, Бланки, СТОІР, кадрові чи інші бізнес-правила. Нові великі функції мають власні domain/service/repository/UI межі й отримують infrastructure через context.

## Що НЕ змінювалося

- схема і дані робочої БД;
- формат workspace;
- backup semantics;
- історичний порядок feature layers;
- plan/fact;
- Бланки;
- роль водія;
- табель;
- СТОІР business rules;
- документи ТЗ;
- військовий облік.

## Що перевірити вручну

1. Запуск через `START.bat`.
2. Переключення/вибір робочого сховища і нормальний запуск після цього.
3. Основні розділи: Персонал, ТЗ, СТОІР, Документи, Табель.
4. Формування типових вихідних PDF/XLSX.
5. Базові сценарії Бланків і шляхових листів — поведінка має лишитися як у r7.

## Далі

Після r8 логічний наступний architecture slice — винести backup/migration orchestration з `main.py`, використовуючи вже створену explicit infrastructure boundary, без зміни формату даних або правил резервного копіювання.

## Важливо

- це fast-test checkpoint;
- поточний PR не зливається в `main` без окремої команди власника;
- після видачі `v10.8-r8` будь-яка нова кодова зміна — тільки `10.8-r9`;
- робочі БД, скани, документи користувача та кеші до пакета не входять.
