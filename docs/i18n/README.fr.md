# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo est un système de bureau pour une entreprise de transport : personnel et conducteurs, plannings, temps de travail, feuilles de route, attestations d’activité, véhicules, documents, maintenance, rapports et tachygraphes analogiques.

> **Stable :** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)  
> **Dernier checkpoint intégré dans `main` :** **Taxo 10.9-r10**  
> **Dernière release multi-plateforme complète publiée :** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)  
> **Prochaine révision de code :** `10.10-r1`

`10.9-r10` est déjà intégré dans `main`, mais n’a pas été publié comme une release publique multi-plateforme complète séparée. Pour les paquets Windows/macOS prêts à l’emploi, utilisez `v10.9-r9`.

## Téléchargements — 10.9-r9

**Windows 10/11 :** [x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows_x64.exe) · [x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows_x64_Portable.zip)

**Windows 7 SP1 :** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows7_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows7_x64_Portable.zip)

**macOS :** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_x86_64_Portable.zip)

**Tests/source :** [START 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_START.zip) · [Notes 10.9-r10](../releases/RELEASE_NOTES_v10.9-r10.md) · [Index des releases](../releases/RELEASE_INDEX.md)

Les bases utilisateurs, fichiers SQLite, scans, caches et documents personnels ne sont pas inclus dans les releases GitHub.

## Changements dans 10.9-r10

Le dépôt a été réorganisé sans modifier la logique métier : les modules runtime ont été déplacés dans `src/taxo/`, les modèles dans `assets/` et les définitions actives de packaging dans `packaging/`. Aucune migration de données utilisateur n’a été introduite.

## Fonctions principales

Personnel et conducteurs avec historique ; plannings individuels/périodiques ; plan/réel et services fractionnés ; contrôle travail/conduite/pauses/repos ; registre 60 jours ; véhicules, kilométrage, maintenance et documents ; feuilles de route ; attestations d’activité ; tachygraphes analogiques ; ordres et affectations conducteur→véhicule protégés ; rapports PDF/Excel ; sauvegardes et compatibilité SQLite.

## Développement

La documentation canonique est maintenue en ukrainien. Point d’entrée : [`START_HERE.md`](../../START_HERE.md). Après `10.9-r10`, le nouveau code commence avec `10.10-r1` depuis le `main` actuel. Les révisions publiées sont immuables.

**Copyright © 2026 Roman Zavada (Роман Завада). Tous droits réservés.** Taxo est un logiciel propriétaire.
