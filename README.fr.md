# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md)

Taxo est une application de bureau destinée à une entreprise de transport : personnel et conducteurs, plannings, temps de travail, feuilles de route, attestations d’activité, véhicules, contrôle documentaire, rapports et traitement sélectif des disques de tachygraphe analogiques.

> **Stable :** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3).  
> **Dernier checkpoint complet dans `main` :** [Taxo 10.5-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.5-r8).  
> **Stable précédente / rollback :** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).  
> `v10.5-r8` est un candidate/checkpoint complet et ne devient pas stable sans une décision séparée du propriétaire.

## Téléchargements 10.5-r8

[Windows x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Setup_Windows_x64.exe) · [Windows x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Windows_x64_Portable.zip) · [Windows 7 SP1 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Setup_Windows7_x64.exe) · [Windows 7 SP1 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_Windows7_x64_Portable.zip) · [macOS ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_macOS_arm64_Portable.zip) · [macOS Intel](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_macOS_x86_64_Portable.zip) · [START](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/Taxo_v10_5_candidate_r8_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.5-r8/SHA256SUMS_v10_5_r8.txt)

Les bases utilisateurs, fichiers SQLite, scans, caches et documents personnels ne sont jamais inclus dans les releases GitHub.

## Fonctions principales

- registre du personnel et des conducteurs avec rôles et historique ;
- plannings individuels et périodiques des conducteurs ;
- feuilles de temps avec services fractionnés et séparation explicite plan/réel ;
- contrôle du travail, de la conduite, des pauses et du repos ;
- bilans hebdomadaires séparés de **60:00 de travail** et **56:00 de conduite** ;
- registre d’activité sur 60 jours avec détail à la minute ;
- registre des véhicules, historique kilométrique et contrôle des documents ;
- assurance, responsabilité complémentaire, contrôle technique, documents d’immatriculation et protocole tachygraphe ;
- itinéraires et scénarios horaires ;
- feuilles de route, attestations d’activité et rapports PDF/Excel ;
- disques de tachygraphe analogiques avec vérification manuelle ;
- espace de travail configurable, sauvegardes et transfert des données.

## Registres et comptabilité militaire dans la ligne 10.5

La ligne 10.5 a ajouté le rapprochement des véhicules avec les données « Shlyakh », des valeurs de travail modifiables séparées des snapshots étatiques immuables, un registre unifié des documents salariés, un import XLSX sans perte, un état d’entreprise pour le transport militaire et un flux local Diia-first pour le rapprochement annuel du personnel.

Taxo **ne remplace pas une API étatique**. La préparation locale n’est pas considérée comme un fait officiel et l’application ne prétend pas transmettre automatiquement des données à Diia, Oberih ou Shlyakh.

## Changement dans 10.5-r8

Sous Windows 7 / Python 3.8, openpyxl peut renvoyer pour certains XLSX Shlyakh l’erreur courte `unexpected keyword argument 'tabId'` sans le mot `ChildSheet`. r8 reconnaît ce cas précis, réessaie avec une copie en mémoire et ne modifie jamais le XLSX source.

Notes complètes : [Release notes 10.5-r8](docs/releases/RELEASE_NOTES_v10_5_r8.md).

## Documentation

La documentation opérationnelle canonique est maintenue en ukrainien :

- [Index de documentation](docs/README.md)
- [Présentation du système](docs/SYSTEM_OVERVIEW.md)
- [Démarrage rapide](docs/guides/QUICK_START.md)
- [Manuel du personnel](docs/guides/USER_MANUAL.md)
- [Administration et sauvegardes](docs/guides/ADMIN_GUIDE.md)
- [Dépannage](docs/guides/TROUBLESHOOTING.md)
- [Index des releases](docs/releases/RELEASE_INDEX.md)

## État du développement

Les nouvelles sessions commencent par `START_HERE.md`, puis `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` et Issue #61.

Chaque étape terminée reçoit une nouvelle révision `r1 … r10` ; après `r10`, la version mineure augmente et la révision revient à `r1`. Les révisions publiées sont immuables. Après `10.5-r8`, la prochaine révision de code est **10.5-r9**.

## Droit d’auteur et licence

**Copyright © 2026 Roman Zavada (Роман Завада). Tous droits réservés.**

Taxo est un logiciel propriétaire. La visibilité publique du dépôt n’accorde aucune licence open source ni autorisation de redistribuer, vendre, republier ou diffuser des versions modifiées/dérivées sans autorisation écrite du titulaire des droits.

Voir [LICENSE.md](LICENSE.md), [COPYRIGHT.md](COPYRIGHT.md) et [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
