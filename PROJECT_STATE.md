# PROJECT_STATE — Taxo

**Підтверджено GitHub 20.11.2026 після stable promotion 10.23-r4.**

**Stable/Latest:** [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4), exact product source `a919ced6bc8665ced70ebb4d897808e4e2618667`, 8 assets, GitHub Latest, prerelease=false.

**Поточний Test:** [10.23-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r5), exact source `dc5dcaa3aa86b4d42cfdec8019fbc73c73f2be3a`, 8 assets, prerelease=true. **Stable/Latest: 10.23-r4.** r3 був інтегрований у main, але окремий v10.23-r3 свідомо не публікувався.

## Stable 10.23-r4

- Каталог документів: пошук, фільтри, сортування, дерево «За видами / За датами / Мої папки», вкладені власні папки, сховище, скани та паперовий підпис.
- Бланки: регульована вертикальна робоча область між формою та історією.
- Каталог: регульована ширина дерева та компактні дії для меншої ширини.
- Накази: явні пари водій–ТЗ, редагування пар, ролі/примітки учасника, накопичення вибору при пошуку, тема активного наказу, перехід до закріплень.
- Перегляд наказу: адаптивні DOCX/PDF/JPG дії, стабільна нижня сітка, доступність при 760×560.
- Захист функцій: **37 strict runtime routes** з mapped / onscreen / usable / activation.

## Перевірка

Exact stable source `a919ced6bc8665ced70ebb4d897808e4e2618667`:
- START #44803423646 — SUCCESS;
- Windows #44803423874 — SUCCESS, Defender/integrity PASS;
- Windows 7 #44803423649 — SUCCESS, Defender/integrity PASS;
- macOS Intel/ARM #44803423740 — SUCCESS;
- Test publisher #44804999191 — SUCCESS;
- owner manual acceptance 20.11.2026;
- Stable promotion #44811800328 — SUCCESS.

Release v10.23-r4 перевірено: tag target = exact source, 8 assets, draft=false, prerelease=false, `releases/latest` = v10.23-r4.

## Поточний Test і наступна розробка

10.23-r5 опублікована як Test prerelease. Exact release source `dc5dcaa3aa86b4d42cfdec8019fbc73c73f2be3a`; publisher #44927558482 — SUCCESS; 8 assets. Вона додає малий viewport каталогу документів і 38-й strict live route. Stable/Latest лишається 10.23-r4.

Нормативна AI-ready архітектура документів злита в main: `docs/DOCUMENT_STORAGE_AND_AI_CLASSIFICATION.md`. Наступна кодова ревізія — **10.23-r6**, inventory/dry-run core для існуючої бази документів: лише інвентар, hash, manifest, exact duplicate detection і звіт; без move/rename/delete та без автоматичного APPLY.

#553/#556/#562 лишаються відкритими; draft #543/#395 не закривати автоматично.

Історична контрольна точка Taxo 10.3 / `v10.3`: `7d2044d2cad00acdd7d6fccdad2ffc037dc2bf60`.
