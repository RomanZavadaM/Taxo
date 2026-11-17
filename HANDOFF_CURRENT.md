# HANDOFF_CURRENT — Taxo

**Підтверджено 17.11.2026 після recovery з live GitHub.**

## Підтверджена база

- 10.20-r9 завершена, інтегрована й опублікована. Exact release source `a607024d25557136b92c5de4a91ee1d6c7e8b1e1`, START/Windows/Win7/macOS SUCCESS, 1419/1419, Defender/integrity PASS.
- Test prerelease [v10.20-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r9): 6 файлів.
- Stable/Latest [v10.20-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5): 8 файлів.
- Recovery PR #485 merged `116774c94cf0ea6cddd70204b95f14e72bac83bb`; private log `5ae12d9a00d3c3ea0f9266518ad134ab8cffcd3e`.
- Docs-only PR #486 виправив буквальний `\\n` у RELEASE_INDEX; усі head checks SUCCESS, merged `2aa5f104d2b74a3e23fefbee626ae9e814adec87`.

## Фактична незавершена робота

Під час перевірки всіх Git refs знайдено вже існуючу гілку **`work/v10.20-r10-paper-scan-replace`**, head перед відновленням `6b798332c18c1adbe2ad299020c7b06e16867b70`. Це новіший факт за попередній HANDOFF/промпт «r10 не розпочата». Не повторювати реалізацію і не робити висновків про іншого виконавця.

Один slice #289: явна заміна вибраного активного скана, старі незмінні байти та історія «Замінено» зберігаються у workspace/backup. Поточний commit завершує legacy version guards, зберігає правку #486 і додає перевірки безпечної відмови/скасування/малих вікон. Попередній START `44079152262` FAILED тільки на 35 старих version guards; 7 r10 tests пройшли.

**10.20-r10 ще не merged і не опублікована.** Результати нового CI поки UNKNOWN. Запропонований scan-filter не реалізований і відкладений.

## Одна наступна дія

Звірити head/PR гілки r10 та результати START/Windows/Win7/macOS. Усунути конкретні помилки до інтеграції, потім завершити Test prerelease та recovery. Не змінювати Stable/Latest.

Без КЕП/e-signature, auto-signed, physical purge, migration, нових бізнес-статусів або залежностей. TemplateLibrary read-only. Працювати через GitHub/хмарні перевірки, executable вручну не запускати.
