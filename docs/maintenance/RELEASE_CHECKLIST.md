# Release checklist

Актуальний чекліст для супроводу Taxo 10.x.

1. Зміни виконувати в окремій гілці через Pull Request.
2. **Кожен завершений крок розробки отримує нову ревізію**: `r1 ... r10`; після `r10` — наступна minor-версія з `r1` (наприклад `10.2-r10 -> 10.3-r1`). Вже видану ревізію не перевикористовувати.
3. На початку нового кроку синхронізувати ревізію в `main.APP_VERSION`, `VERSION.txt`, гілці/PR, release notes, тестах та назві архіву.
4. Кожен завершений крок закінчувати готовим START-архівом і прямим посиланням користувачу; лише commit/push/CI не означає завершення.
5. START-пакет: один ZIP -> одна коренева папка тієї самої назви; вкладений ZIP заборонений.
6. Не включати БД, скани тахокарт або персональні документи до Git/релізу.
7. Перед змінами даних перевірити резервну копію.
8. Синхронізувати `VERSION.txt`, заголовок програми, About, build/spec/installer-реквізити та release notes.
9. Виконати `py_compile` і весь `unittest discover` на Linux/source publisher.
10. Перевірити той самий source на Windows і macOS CI.
11. Перевірити START-пакет: `START.bat`, потрібні модулі, відсутність SQLite/pyc/cache.
12. Для нового candidate створювати **новий immutable tag**. Не пересувати і не перезаписувати попередні protected tags.
13. Перед публікацією переглянути release target і список assets.
14. Виконавчі Windows/macOS пакети публікувати на обраних контрольних точках, а не на кожному дрібному candidate.
15. Для stable release окремо перевірити Windows x64, macOS ARM64 та macOS Intel, SHA-256 і release notes.
16. Оновити `PROJECT_STATE.md`, `docs/PRODUCT_STATUS.md`, maintenance checkpoint та користувацькі інструкції.
17. Перед переходом до наступного етапу зафіксувати технічний аудит: що перевірено, що виправлено, що лишається ручною перевіркою.
18. `main` оновлювати тільки після експлуатаційного підтвердження кандидата.
19. Після публікації перевірити GitHub Releases: release target, assets, відсутність draft-релізів і відповідність release index.
20. Документаційні commits після immutable release не повинні пересувати tag або змінювати `VERSION.txt`; новий tag потрібен лише для нової кодової контрольної точки.
21. Перевірити активність rulesets `Protect main` і `Protect releases` перед stable merge/release.


Повні правила розробки: [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md).
