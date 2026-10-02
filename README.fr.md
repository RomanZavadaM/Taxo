# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo est une application de bureau destinée à une entreprise de transport : personnel et conducteurs, plannings, temps de travail, feuilles de route, attestations d’activité, véhicules, contrôle documentaire, rapports, maintenance et traitement sélectif des disques de tachygraphe analogiques.

> **Stable :** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3).  
> **Dernier checkpoint intégré dans `main` :** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9).  
> **Dernier checkpoint multi-plateforme complet :** [Taxo 10.9-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1).  
> **Stable précédente / rollback :** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1).  
> `v10.9-r9` ne devient pas stable automatiquement ; la promotion stable reste une décision séparée du propriétaire.

## Téléchargements

### Checkpoint intégré actuel — 10.9-r9

[START 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/SHA256SUMS_v10_9_r9.txt) · [Release 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)

10.9-r9 est le dernier checkpoint de code intégré. Un paquet START est publié ; un ensemble complet d’exécutables n’a pas été republié pour r9.

### Dernier checkpoint multi-plateforme complet — 10.9-r1

[Release 10.9-r1 avec paquets Windows/macOS](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1) · [Combined SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r1/SHA256SUMS_v10_9_r1_ALL.txt)

Pour l’exploitation normale, utilisez un paquet Windows/macOS prêt à l’emploi de `v10.9-r1`. `START.bat` est principalement destiné aux tests et au diagnostic technique ; extrayez complètement le ZIP START avant de l’exécuter.

Les bases utilisateurs, fichiers SQLite, scans, caches et documents personnels ne sont jamais inclus dans les releases GitHub.

## Fonctions principales

- registre du personnel et des conducteurs avec rôles et historique ;
- plannings individuels et périodiques des conducteurs ;
- feuilles de temps avec services fractionnés et séparation explicite plan/réel ;
- contrôle du travail, de la conduite, des pauses et du repos ;
- registre d’activité sur 60 jours sans inventer du repos à partir de temps inconnu ;
- registre des véhicules, kilométrage, maintenance et contrôle des documents ;
- feuilles de route régulières et non régulières ;
- attestations d’activité avec historique des révisions ;
- disques de tachygraphe analogiques avec vérification manuelle ;
- protection de l’historique des ordres approuvés/signés et des affectations conducteur→véhicule ;
- rapports PDF/Excel ;
- sauvegardes, transfert de l’espace de travail et contrôle de compatibilité du schéma SQLite.

## Intégré dans 10.9-r2 → 10.9-r9

La ligne intégrée ajoute un historique immuable des feuilles de route et numéros, la validation des documents du véhicule pendant tout le trajet, un contrôle renforcé travail/repos, une priorité plus sûre des sources factuelles, des corrections historiques personnel/P-5, un durcissement de l’odomètre et des prévisions de maintenance, des ordres approuvés/signés immuables et la première base explicite du schéma SQLite via `PRAGMA user_version`.

Notes complètes : [Release notes 10.9-r9](docs/releases/RELEASE_NOTES_v10.9-r9.md) · [Index des releases](docs/releases/RELEASE_INDEX.md).

## Registres étatiques et comptabilité militaire

Taxo prend en charge le rapprochement des véhicules avec « Shlyakh », des valeurs de travail modifiables séparées des snapshots étatiques immuables, le registre des documents salariés, l’import XLSX sans perte et un flux local Diia-first pour le rapprochement annuel du personnel.

Taxo **ne remplace pas une API étatique** et ne prétend pas transmettre automatiquement des données à Diia, Oberih ou Shlyakh.

## Documentation et développement

La documentation opérationnelle canonique est maintenue en ukrainien. Les nouvelles sessions commencent par `START_HERE.md`, puis `PROJECT_RULES.md`, `PROJECT_STATE.md`, `WORKLOG.md` et Issue #61. Les révisions publiées sont immuables. Après `10.9-r9`, la prochaine révision de code est **10.9-r10**.

Voir [Index de documentation](docs/README.md) · [Présentation du système](docs/SYSTEM_OVERVIEW.md) · [État du produit](docs/PRODUCT_STATUS.md) · [Démarrage rapide](docs/guides/QUICK_START.md) · [Index des releases](docs/releases/RELEASE_INDEX.md).

## Droit d’auteur et licence

**Copyright © 2026 Roman Zavada (Роман Завада). Tous droits réservés.**

Taxo est un logiciel propriétaire. La visibilité publique du dépôt n’accorde aucune licence open source ni autorisation de redistribuer, vendre, republier ou diffuser des versions modifiées/dérivées sans autorisation écrite du titulaire des droits.

Voir [LICENSE.md](LICENSE.md), [COPYRIGHT.md](COPYRIGHT.md) et [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
