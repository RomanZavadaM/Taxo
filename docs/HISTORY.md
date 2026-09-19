# Історія розвитку Taxo

Починаючи з Taxo 9.0, гілка `main` використовується як **експлуатаційна stable-гілка продукту**.

Історична розробка 8.x збережена в:
[`history/development-v8`](https://github.com/RomanZavadaM/Taxo/tree/history/development-v8)

## Stable 9.x

- **9.0** — базова експлуатаційна версія;
- **9.0.1** — hotfix версії в інтерфейсі та чистого START-пакета.

## Candidate line 9.1

Розвиток 9.1 проходив через PR #29 та immutable pre-releases:
`v9.1-r5` … `v9.1-r9.8`.

Ключові етапи:
- r7 — hardening планування;
- r8 — єдиний стан дня;
- r9 — канонічні exact intervals і union overlap;
- r9.3 — П-5, архів бланків, місячний контроль;
- r9.4 — «Аудит графіків…»;
- r9.5/r9.6 — START package і Windows CMD compatibility;
- r9.7 — «Відкрити деталізацію» у місячному графіку;
- r9.8 — один duty staff slot за role + date + shift.

r1–r4 лишилися проміжними Git-станами й навмисно не оформлювалися окремими GitHub Releases.

## Taxo 10.0

**19.09.2026** — candidate line 9.1 завершена після manual operational gate і промотована в **stable Taxo 10.0**.

10.0 включає:
- Personnel / regimes / P-5;
- canonical time intervals;
- technical schedule audit + separate №340 control;
- monthly schedule/detail workflows;
- waybill duty-staff consistency;
- Windows-safe START;
- full Windows/macOS stable packaging.

## Що використовувати зараз

Для штатної експлуатації використовуйте **`main` + GitHub Release `v10.0`**.

`v9.0.1` зберігається як попередня stable/rollback точка. Candidate releases 9.1 — історичні контрольні точки, а не актуальні пакети для експлуатації.

Повний індекс: [releases/RELEASE_INDEX.md](releases/RELEASE_INDEX.md).
