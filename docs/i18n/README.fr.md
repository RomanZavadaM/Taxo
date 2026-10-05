# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo est un système de bureau pour une seule entreprise de transport : personnel et conducteurs, plannings, suivi du temps de travail, feuilles de route, formulaires d'attestation d'activité, véhicules, contrôle documentaire, maintenance, rapports et contrôle des disques de chronotachygraphe analogique.

> **Stable:** [Taxo 10.10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10) — 2026-10-05
> **Stable précédente / retour arrière:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)
> **Prochaine révision du code:** `10.10-r4`

## Téléchargements — Taxo 10.10 (stable)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/SHA256SUMS_v10_10.txt) · [Notes de version 10.10 (ukrainien)](../releases/RELEASE_NOTES_v10_10.md) · [Index des versions](../releases/RELEASE_INDEX.md)

Les bases de données de travail, fichiers SQLite, numérisations, caches et documents personnels ne sont pas inclus dans les versions GitHub. La mise à jour ne nécessite pas de ressaisir les données de travail.

## Nouveautés de 10.10

- **Sans PyMuPDF.** Le formulaire d'attestation d'activité (PDF/JPG), le tampon de date du rapport n° 340 ainsi que l'affichage/l'impression PDF utilisent des bibliothèques sous licences permissives (pypdfium2, reportlab, pypdf) ; le rendu est identique au pixel près à la version précédente.
- **Version correcte affichée** — titre de la fenêtre, boîte « À propos », en-têtes PDF et manifeste de sauvegarde.
- **Les sauvegardes** avertissent explicitement lorsqu'elles ne contiennent que les bases de données.
- **Infrastructure :** workflows de publication obsolètes désactivés, tests isolés du stockage de travail, contrôle des licences dans chaque build.
- Inclut toute la ligne 10.4 … 10.9 : validité des documents du véhicule pour tout le trajet, protection des feuilles de route et numéros émis, contrôle renforcé travail/repos, registre de 60 jours, bilan du personnel, maintenance, ordres signés immuables, compatibilité du schéma SQLite.

## Fonctions principales

Historique du personnel et des conducteurs ; plannings individuels et périodiques ; temps de travail prévu/réel et services fractionnés ; contrôle du travail, de la conduite, des pauses et du repos ; registre d'activité de 60 jours ; véhicules, kilométrage, maintenance et documents ; feuilles de route régulières et non régulières ; formulaires d'attestation d'activité ; contrôle de chronotachygraphe analogique ; ordres protégés et affectations conducteur→véhicule ; rapports PDF/Excel ; sauvegardes et contrôle de compatibilité SQLite.

## Développement

La documentation opérationnelle de référence est tenue en ukrainien. Commencez par [`START_HERE.md`](../../START_HERE.md). Après la stable 10.10, le nouveau code commence à `10.10-r4` depuis le `main` actuel. Les révisions publiées sont immuables.

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo est un logiciel propriétaire.
