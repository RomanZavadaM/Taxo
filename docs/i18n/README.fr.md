# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo est un système de bureau pour une seule entreprise de transport : personnel et conducteurs, plannings, suivi du temps de travail, feuilles de route, formulaires d'attestation d'activité, véhicules, contrôle documentaire, maintenance, rapports et contrôle des disques de chronotachygraphe analogique.

> **Stable:** [Taxo 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10) — approuvée par le propriétaire comme stable ; checkpoint r10 exact vérifié sous Windows 10/11, Windows 7, macOS Intel et Apple Silicon
> **Remplacée:** [Taxo 10.10-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r4) — déconseillée sur macOS en raison d’un échec de démarrage confirmé
> **Stable précédente / retour arrière:** [Taxo 10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5)
> **Retour arrière plus ancien:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10)
> **Ancien retour arrière:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)

## Téléchargements — Taxo 10.9-r10 (retour arrière plus ancien)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/SHA256SUMS_v10_9_r10.txt) · [Notes de version 10.9-r10 (ukrainien)](../releases/RELEASE_NOTES_v10.9-r10.md) · [Index des versions](../releases/RELEASE_INDEX.md)

## Téléchargements — Taxo 10.12-r10 (stable)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Setup_Windows7_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/SHA256SUMS_v10_12_r10.txt)

Les bases de données de travail, fichiers SQLite, numérisations, caches et documents personnels ne sont pas inclus dans les versions GitHub. La mise à jour ne nécessite pas de ressaisir les données de travail.

## Contenu de la stable précédente 10.9-r10

- historique permanent des feuilles de route et numéros émis ; la rétention ne supprime jamais les faits liés
- validité des documents du véhicule pour tout le trajet prévu
- contrôle renforcé travail/repos : chevauchements, 3+9, repos hebdomadaire et bihebdomadaire
- registre de 60 jours sans repos inventé ; priorité aux sources réelles
- bilan du personnel / P-5, régimes 2/2 et 3/3
- maintenance : chronologie du compteur et prévision d'entretien
- ordres approuvés/signés et affectations conducteur→véhicule immuables
- contrôle de compatibilité du schéma SQLite
- code structuré sans modification de la logique métier

## Ligne 10.10

[10.10-r1 … r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r3) sont des préversions antérieures. **10.10-r5** a corrigé le démarrage macOS et constitue désormais la stable précédente / version de retour. **10.12-r10 est la stable actuelle**.

## Développement

La documentation opérationnelle de référence est tenue en ukrainien. Commencez par [`START_HERE.md`](../../START_HERE.md). La stable actuelle est `10.12-r10` ; la version plus récente `10.13-r1` est intégrée dans `main`, mais n’est pas stable. La prochaine révision est `10.13-r2`.

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo est un logiciel propriétaire.
