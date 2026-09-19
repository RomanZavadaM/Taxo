# Release checklist

Актуальний чекліст для супроводу Taxo 9.x.

1. Зміни виконувати в окремій гілці через Pull Request.
2. Не включати БД, скани тахокарт або персональні документи до Git/релізу.
3. Перед змінами даних перевірити резервну копію.
4. Синхронізувати `VERSION.txt`, заголовок програми, About, build/spec/installer-реквізити та release notes.
5. Виконати `py_compile` і весь `unittest discover` на Linux/source publisher.
6. Перевірити той самий source на Windows і macOS CI.
7. Перевірити START-пакет: `START.bat`, потрібні модулі, відсутність SQLite/pyc/cache.
8. Для нового candidate створювати **новий immutable tag**. Не пересувати і не перезаписувати попередні protected tags.
9. Перед публікацією переглянути release target і список assets.
10. Виконавчі Windows/macOS пакети публікувати на обраних контрольних точках, а не на кожному дрібному candidate.
11. Для stable release окремо перевірити Windows x64, macOS ARM64 та macOS Intel, SHA-256 і release notes.
12. Оновити `PROJECT_STATE.md`, `docs/PRODUCT_STATUS.md`, maintenance checkpoint та користувацькі інструкції.
13. Перед переходом до наступного етапу зафіксувати технічний аудит: що перевірено, що виправлено, що лишається ручною перевіркою.
14. `main` оновлювати тільки після експлуатаційного підтвердження кандидата.
15. Після публікації перевірити GitHub Releases: release target, assets, відсутність draft-релізів і відповідність release index.
16. Документаційні commits після immutable release не повинні пересувати tag або змінювати `VERSION.txt`; новий tag потрібен лише для нової кодової контрольної точки.
17. Перевірити активність rulesets `Protect main` і `Protect releases` перед stable merge/release.
