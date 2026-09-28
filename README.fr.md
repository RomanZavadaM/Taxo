# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md)

Taxo est une application de bureau destinée à une entreprise de transport : personnel et conducteurs, plannings, temps de travail, feuilles de route, attestations d’activité, véhicules, contrôle documentaire, rapports et traitement sélectif des disques de tachygraphe analogiques.

> **Stable :** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3).  
> **Dernier checkpoint complet dans `main` :** [Taxo 10.6-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.6-r3).  
> **Stable précédente / rollback :** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).  
> `v10.6-r3` est un candidate/checkpoint complet et ne devient pas stable sans une décision séparée du propriétaire.

## Téléchargements 10.6-r3

[Windows x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Setup_Windows_x64.exe) · [Windows x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Windows_x64_Portable.zip) · [Windows 7 SP1 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Setup_Windows7_x64.exe) · [Windows 7 SP1 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_Windows7_x64_Portable.zip) · [macOS ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_macOS_arm64_Portable.zip) · [macOS Intel](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_macOS_x86_64_Portable.zip) · [START](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/Taxo_v10_6_candidate_r3_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.6-r3/SHA256SUMS_v10_6_r3_FULL.txt)

Les bases utilisateurs, fichiers SQLite, scans, caches et documents personnels ne sont jamais inclus dans les releases GitHub.

## Fonctions principales

- registre du personnel et des conducteurs avec rôles et historique ;
- plannings individuels et périodiques des conducteurs ;
- feuilles de temps avec services fractionnés et séparation explicite plan/réel ;
- contrôle du travail, de la conduite, des pauses et du repos ;
- bilans hebdomadaires séparés de **60:00 de travail** et **56:00 de conduite** ;
- registre des véhicules, kilométrage et contrôle des documents ;
- itinéraires réguliers et travaux non réguliers : commandes, navettes, ville, région, interrégional et autres services ponctuels ;
- feuilles de route, attestations d’activité et rapports PDF/Excel ;
- disques de tachygraphe analogiques avec vérification manuelle ;
- sauvegardes et transfert des données.

## Checkpoint 10.6-r3

Le checkpoint comprend la correction de l’audit plan/réel, le masquage par défaut des véhicules inactifs, l’émission de feuilles de route pour des travaux non réguliers sans exiger un `route_id` du catalogue et une fenêtre « À propos » adaptative. Pour une sortie non régulière, la table d’itinéraire reste vide tandis que le médecin, le mécanicien, l’odomètre et le kilométrage réel sont conservés lorsqu’une source réelle existe dans Taxo. Les faits manquants ne sont pas inventés à partir du plan.

Notes complètes : [Release notes 10.6-r3](docs/releases/RELEASE_NOTES_v10_6_r3.md).

## Registres étatiques et comptabilité militaire

Taxo prend en charge le rapprochement des véhicules avec « Shlyakh », des valeurs de travail modifiables séparées des snapshots étatiques immuables, le registre des documents salariés, l’import XLSX sans perte, l’état d’entreprise pour le transport militaire et un flux local Diia-first pour le rapprochement annuel du personnel.

Taxo **ne remplace pas une API étatique** et ne prétend pas transmettre automatiquement des données à Diia, Oberih ou Shlyakh.

## Documentation et développement

La documentation opérationnelle canonique est maintenue en ukrainien. Les nouvelles sessions commencent par `START_HERE.md`, puis `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` et Issue #61. Les révisions publiées sont immuables. Après `10.6-r3`, la prochaine révision de code est **10.6-r4**.

Voir [Index de documentation](docs/README.md) · [Présentation du système](docs/SYSTEM_OVERVIEW.md) · [Démarrage rapide](docs/guides/QUICK_START.md) · [Index des releases](docs/releases/RELEASE_INDEX.md).

## Droit d’auteur et licence

**Copyright © 2026 Roman Zavada (Роман Завада). Tous droits réservés.**

Taxo est un logiciel propriétaire. La visibilité publique du dépôt n’accorde aucune licence open source ni autorisation de redistribuer, vendre, republier ou diffuser des versions modifiées/dérivées sans autorisation écrite du titulaire des droits.

Voir [LICENSE.md](LICENSE.md), [COPYRIGHT.md](COPYRIGHT.md) et [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
