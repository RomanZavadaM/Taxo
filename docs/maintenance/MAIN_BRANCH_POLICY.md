# Політика гілки `main`

Починаючи з Taxo 9.0, `main` є експлуатаційною гілкою продукту. Після завершення operational gate лінії 9.1 актуальна stable у `main` — **Taxo 10.0**.

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


## Правило після Taxo 10.0

- нові функціональні зміни не вносяться безпосередньо в `main`;
- робота ведеться у work branch через Pull Request;
- stable merge виконується після CI та ручної експлуатаційної перевірки;
- кожен stable release має новий immutable tag;
- GitHub Actions збирає Windows/macOS/START artifacts уже з stable commit у `main`;
- user database, scans and personal files never enter Git/release artifacts.
