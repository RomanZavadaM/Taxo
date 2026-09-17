# Taxo 9.0 — технічний стан

Канонічний детальний технічний стан перенесено з кореня репозиторію до цього розділу під час очищення `main` від історичних артефактів.

Актуальна експлуатаційна база: **Taxo 9.0 stable**. Для повного історичного стану перед очищенням використовуйте гілку [`history/development-v8`](https://github.com/RomanZavadaM/Taxo/tree/history/development-v8), де збережено оригінальний `PROJECT_STATE.md` разом з усіма checkpoint/test/publish-файлами.

Основні актуальні модулі: `taxo_app.py`, `main.py`, `workspace.py`, `tachograph.py`, `waybill.py`, `attestation_render.py`, `work_analysis_ext.py`, `activity_register_60.py`, `v9_release.py`.

Поточна політика: експлуатація, наповнення реальної бази, локальні виправлення відтворюваних проблем, пріоритет цілісності даних і відсутності регресій над новими функціями.

Повний опис актуального функціоналу: [../SYSTEM_OVERVIEW.md](../SYSTEM_OVERVIEW.md). Дані та сховище: [../DATA_MODEL_AND_STORAGE.md](../DATA_MODEL_AND_STORAGE.md).