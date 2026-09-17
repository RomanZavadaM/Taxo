# Політика гілки `main`

Починаючи з Taxo 9.0, `main` є експлуатаційною гілкою продукту.

У `main` зберігаються:

- актуальний вихідний код;
- документація для персоналу й адміністратора;
- актуальні release notes і технічні матеріали супроводу;
- build/release infrastructure;
- шаблони документів і автоматичні тести.

У `main` не зберігаються як окремі кореневі файли:

- історичні `CHECKPOINT_v8*`;
- старі `TEST_REPORT_*` і `PUBLISH_STATUS_*`;
- разові `PATCH_*`;
- ранні source ZIP/parts;
- застарілі release notes 8.x.

Повний дорелізний/розробницький стан збережено в гілці [`history/development-v8`](https://github.com/RomanZavadaM/Taxo/tree/history/development-v8).

GitHub Releases залишаються канонічним місцем для готових Setup/Portable/START пакетів стабільних версій.
