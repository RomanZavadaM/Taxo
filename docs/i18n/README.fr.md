# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

> **Version stable:** [Taxo 10.14-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.14-r4) · 09.11.2026 · Windows 10/11, Windows 7, macOS Intel / Apple Silicon, START verified.
> **Version stable précédente / retour arrière:** [Taxo 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10).

## Téléchargements — 10.14-r4

**Windows 10/11 x64:** [Installateur](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Installateur](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Setup_Windows7_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_macOS_x86_64_Portable.zip)

**Sources / sommes de contrôle:** [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/SHA256SUMS_v10_14_r4.txt) · [Release notes (UK)](../releases/RELEASE_NOTES_v10.14-r4.md).

## Nouveautés depuis 10.12-r10

Interface d'exploitation et de maintenance améliorée, affectations multiples conducteurs/véhicules, numérotation séparée des ordres RH et opérationnels, aperçu, documents Word modifiables, PDF et JPG avec tableaux cohérents.

Les ordres sont des documents de travail : leur statut ou la mention de signature papier n'empêchent ni correction ni suppression. Les originaux papier restent sous le contrôle de l'utilisateur.

Les bases de données, scans, documents personnels et caches ne sont pas inclus dans le téléchargement. Sauvegardez les données avant la mise à jour.

## Documentation et développement

La documentation opérationnelle de référence est en ukrainien. Consultez le démarrage rapide et le guide d'exploitation. Prochaine révision : 10.14-r5.

[Quick Start / Швидкий старт](../guides/QUICK_START.md) · [Operations & Maintenance / Експлуатація](../guides/OPERATIONS_STOIR_GUIDE.md) · [Release Index](../releases/RELEASE_INDEX.md) · [Current State](../../PROJECT_STATE.md).

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo is proprietary software.

## Version de test 10.15-r3 — consignes et stage de conduite

Les consignes génèrent désormais un document DOCX modifiable avec le programme complet et une feuille de signatures séparée, au lieu de fichiers CSV dispersés. Une fiche de stage du conducteur et un catalogue consultable des documents Word sauvegardés dans l’espace de travail sont également disponibles (inclus dans la sauvegarde complète). La création d’un fichier ne confirme ni la formation, ni une signature, ni l’autorisation de conduite. Les scans facultatifs et le catalogue hiérarchique sont prévus séparément (#289) ; la modularisation Python relève de #290. La version stable reste 10.14-r4.
