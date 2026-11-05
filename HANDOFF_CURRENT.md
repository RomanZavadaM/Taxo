# HANDOFF_CURRENT — Taxo

**Оновлено:** 05.11.2026

## База
- Stable / Latest: **v10.10-r5** (не змінювалася).
- Current main: **10.10-r9**, merge commit `66882a2164bea1a72a30ec1db74d36d1613d0c68`.
- Наступна кодова ревізія: **10.10-r10**.
- CI optimization PR #152 — окрема робота; не змішувати.
- Google Drive stable backup r5 збережений; окремий current-main r9 snapshot ще належить оновити.

## Що завершено
- r6: єдиний центр «Дані / Дія / документи», масові державні оновлення.
- r7: обов'язковість і строки документів для конкретного працівника, workspace backup.
- r8: місячний графік для вибраних працівників із PDF/XLSX.
- r9: за скриншотами власника виправлено розбіжність водійського графіка з переглядом персоналу, захист від дублювання плану для посади «Водій автотранспортних засобів», аварію коригування відсутностей. PR #160 merged.

## Перевірка
- PR #160: Windows, Windows 7, macOS ARM64/Intel — SUCCESS.
- Exact-main r9: START #42041201788, Windows #42041201831, Windows 7 #42041202075, macOS #42041201978 — **SUCCESS**. Windows Portable/Installer та macOS/Win7 artifacts наявні.
- Збірки r9 не є новим stable. Ручне приймання на реальних даних ще не проведене.
- Виданий стабільний r5 залишається rollback.

## Єдина наступна дія
Передати власнику зібраний Windows Portable r9 та прийняти ручну звірку основного водійського табеля з новим графіком/PDF (зокрема 02.11 і 14–16.11); зафіксувати результати, окремо оновити Drive current-main snapshot.

## Recovery
`START_HERE.md` → цей HANDOFF → private Taxo-profile → live GitHub → `PROJECT_STATE.md`.
