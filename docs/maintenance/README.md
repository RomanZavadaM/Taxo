# Супровід Taxo 9.x

Цей розділ містить технічні документи, потрібні для супроводу актуальної стабільної лінії, але не для щоденної роботи персоналу.

- [Поточний технічний стан](PROJECT_STATE.md)
- [Поточна контрольна точка](CHECKPOINT_CURRENT.md)
- [Політика гілки main](MAIN_BRANCH_POLICY.md)
- [Чекліст випуску](RELEASE_CHECKLIST.md)
- [Поточний аудит candidate r9.6 — Windows START compatibility](AUDIT_v9_1_r9_6.md)
- [Аудит candidate r9.5 — START package hotfix](AUDIT_v9_1_r9_5.md)
- [Передетапний функціональний аудит candidate r9.4](AUDIT_v9_1_r9_4.md)
- [GitHub publication summary r9.4](GITHUB_PUBLICATION_SUMMARY_v9_1_r9_4.md)
- [Handoff для нового чату](NEW_CHAT_HANDOFF_v9_1_r9_4.md)

Stable Taxo 9.0.1 лишається експлуатаційною точкою відкату. Поточна перевірочна лінія — Taxo 9.1 candidate r9.6 у PR #29.

Історія розробки версій 8.x винесена з `main` у гілку [`history/development-v8`](https://github.com/RomanZavadaM/Taxo/tree/history/development-v8).


## Поточний gate

r9.5 виявився непридатним для manual gate через Windows CMD parsing regression. r9.6 прибирає UTF-8/chcp із BAT і проходить додатковий Windows preflight gate; після його публікації повторити запуск START і продовжити manual operational gate на реальній Windows-базі. До його завершення `main` і stable 9.0.1 не змінюються.
