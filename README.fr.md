# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo est une application de bureau destinée à une entreprise de transport : personnel et conducteurs, plannings, temps de travail, feuilles de route, attestations d’activité, véhicules, contrôle documentaire, rapports, maintenance et tachygraphes analogiques.

> **Stable :** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3).  
> **Dernier checkpoint intégré dans `main` :** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9).  
> **Dernier checkpoint multi-plateforme complet :** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9).  
> **Stable précédente / rollback :** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).

## Téléchargements — 10.9-r9

**Windows :** [x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows_x64.exe) · [x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows_x64_Portable.zip) · [Windows 7 SP1 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows7_x64.exe) · [Windows 7 SP1 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows7_x64_Portable.zip)

**macOS :** [ARM64 / Apple Silicon](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_x86_64_Portable.zip)

**Tests/diagnostic :** [START](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_START.zip) · [Release](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9) · [Release notes](docs/releases/RELEASE_NOTES_v10.9-r9.md)

Pour l’exploitation normale, utilisez un paquet Windows/macOS prêt à l’emploi. Les bases utilisateurs, fichiers SQLite, scans, caches et documents personnels ne sont pas inclus dans les releases.

## Fonctions principales

Personnel et conducteurs avec historique, plannings individuels/périodiques, plan/réel, services fractionnés, contrôle travail/conduite/pauses/repos, registre 60 jours, véhicules et documents, maintenance, feuilles de route, attestations d’activité, tachygraphes analogiques, ordres approuvés/signés protégés, rapports PDF/Excel, sauvegardes et compatibilité du schéma SQLite.

## 10.9-r2 → 10.9-r9

La ligne intégrée ajoute l’historique immuable des feuilles de route et numéros, la validité documentaire sur tout le trajet, le renforcement travail/repos, la priorité sûre des sources factuelles, les corrections historiques personnel/P-5, l’odomètre et les prévisions de maintenance, les ordres immuables et la base SQLite via `PRAGMA user_version`.

[Release notes 10.9-r9](docs/releases/RELEASE_NOTES_v10.9-r9.md) · [Index des releases](docs/releases/RELEASE_INDEX.md)

## Développement

La documentation canonique est maintenue en ukrainien. Après `10.9-r9`, la prochaine révision de code est **10.9-r10**.

## Droit d’auteur

**Copyright © 2026 Roman Zavada (Роман Завада). Tous droits réservés.** Taxo est un logiciel propriétaire.
