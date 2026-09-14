# Taxo v8.70 — Personnel, horaires et feuilles de route

[Українська](README.md) | [English](README.en.md) | [Deutsch](README.de.md) | [Español](README.es.md) | **Français**

Taxo est une application de bureau en ukrainien destinée à gérer le personnel d'une entreprise de transport, les horaires des conducteurs, le temps de travail, les itinéraires, les véhicules, les attestations d'activités, les feuilles de route des autobus et les relevés de tachygraphes analogiques. La version consolidée actuelle est **v8.70 r5** sur la branche `main`.

## Fonctions principales

- Registre unique du personnel avec matricules, dates d'emploi et plusieurs rôles, notamment conducteur, médecin, mécanicien, répartiteur et receveur.
- Horaires des conducteurs et relevés mensuels séparant le temps de travail planifié du temps de conduite planifié. Une journée de travail peut comporter plusieurs segments.
- Répertoires des itinéraires et des véhicules. Chaque itinéraire contient un horaire précis et peut commencer hors du dépôt, franchir minuit, inclure des périodes de repos ou une nuitée et se terminer un autre jour civil.
- Saisie simplifiée du parcours : il suffit de coller deux colonnes, `Point | Heure`, pour les sens aller et retour. Les changements de jour et les limites de l'itinéraire sont calculés automatiquement ; un éditeur détaillé reste disponible pour les cas particuliers.
- Feuilles de route d'autobus vectorielles de deux pages A4, fondées sur le formulaire n° 1-AP. Le conducteur, le véhicule, l'itinéraire et les heures planifiées proviennent de l'horaire. Les documents couvrant plusieurs jours affichent les dates civiles réelles et non les marqueurs internes `D+N`.
- Séries et plages de numéros officiels avec périodes de validité, numérotation automatique ou manuelle, historique des révisions et journal des annulations.
- Horaires de service des médecins et mécaniciens. Leurs noms peuvent être repris dans la feuille de route, tandis que les signatures manuscrites et les champs réels, de carburant ou de contrôle encore inconnus restent vides.
- Attestations d'activités aux formats DOCX, PDF et JPG, ainsi que sauvegarde et restauration des données persistantes.
- Espace de travail pour les disques de tachygraphe analogique, avec scans, intervalles d'activité et comparaison de la conduite réelle au plan. Les données réelles du tachygraphe n'écrasent pas les données planifiées.

## Exécution et stockage des données

Sous Windows, le paquet source peut être lancé avec `START.bat`. GitHub Actions produit des paquets Windows Setup et Portable ainsi que des paquets macOS natifs pour Apple Silicon et Intel aux points de contrôle exécutables.

Le programme d'installation Windows, l'archive Portable, l'archive du code source et les sommes SHA-256 actuels sont disponibles dans la [version GitHub v8.70](https://github.com/RomanZavadaM/Taxo/releases/tag/v8.70).

L'application conserve les données utilisateur en dehors du dossier du programme, sous `Documents/DriverWorktime`. Les bases SQLite et les données personnelles sont volontairement exclues du dépôt et de tous les paquets de distribution ; une mise à jour du programme ne remplace donc pas les données d'exploitation.

L'interface et les formulaires officiels générés sont actuellement en ukrainien. Cette traduction facilite la présentation internationale du projet.

## État du projet

v8.70 r5 constitue la ligne de développement consolidée et active. Les anciennes branches sont conservées comme points de contrôle historiques. Avant toute utilisation opérationnelle, l'application doit encore être validée avec des données réelles de l'entreprise et des formulaires imprimés.
