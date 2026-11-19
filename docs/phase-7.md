# PHASE_7 — Traders, quêtes et planque

**État : livrée localement, 16/16 routes.** Après cette phase, le site compte **67 routes HTML statiques**, 67 URLs dans le sitemap d’aperçu et **1 284 enregistrements** dans l’index de recherche local. La QA navigateur finale est **PASS** (contrôles Chromium/Firefox, rapport détaillé dans [`verifications-phase-7.md`](verifications-phase-7.md)). Ce n’est pas une publication publique : dépôt, propriétaire, DNS, certificat TLS et routage GitHub Pages restent à confirmer.

## Routes livrées

### Traders — 11 routes

- `pages/traders/` — index des traders et interlocuteurs
- `pages/traders/prapor.html`
- `pages/traders/therapist.html`
- `pages/traders/skier.html`
- `pages/traders/peacekeeper.html`
- `pages/traders/mechanic.html`
- `pages/traders/ragman.html`
- `pages/traders/jaeger.html`
- `pages/traders/fence.html`
- `pages/traders/lightkeeper.html`
- `pages/traders/ref.html`

### Quêtes — 3 routes

- `pages/quests/` — catalogue, recherche, filtres et suivi de progression
- `pages/quests/quest-tree.html` — dépendances déclarées et export JSON local
- `pages/quests/kappa-guide.html` — progression Collector et checklist d’objets

### Hideout — 2 routes

- `pages/hideout/` — stations, niveaux, matériaux et paliers
- `pages/hideout/crafting.html` — recettes et simulateur de coût/marge avec prix saisis localement

## Données, méthode et limites

Les données sont des instantanés communautaires de Tarkov.dev / The Hideout et de Tarkov Data Manager, archivés séparément pour `regular` (PvP permanent), `pve` (PvE Zone) et `pvp-season` (PvP Seasonal). La date de référence éditoriale est le **18 novembre 2026**; la collecte effective est horodatée **2026-11-19T00:34:47Z**. Elles ne sont ni une API live ni une vérification du client. Les fichiers sources, entêtes de dernière modification, URL et réserves figurent dans `docs/sources.json` et `docs/recherche-tarkov-2026-11-18.md`.

| Mode du snapshot | Tâches | Enregistrements de quête | Balises Kappa | Balises Lightkeeper | Stations / niveaux | Lignes matériaux / FIR | Crafts | Barters |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PvP permanent (`regular`) | 503 | 138 | 13 | 0 | 26 / 68 | 317 / 76 | 214 | 888 |
| PvE Zone (`pve`) | 499 | 138 | 13 | 0 | 26 / 68 | 317 / 76 | 214 | 888 |
| PvP Seasonal (`pvp-season`) | 462 | 135 | 13 | 0 | 26 / 68 | 317 / 0 | 214 | 905 |

L’union des trois modes contient **526 tâches**. Les noms français sont renseignés pour toutes les tâches du snapshot. L’audit des dépendances détecte **zéro cycle**, aucune référence de tâche ni déverrouillage de craft manquant dans les données consultées; il compte 12 tâches à prérequis multiples en regular, 12 en PvE et 8 en PvP Seasonal. L’interface expose les prérequis déclarés; elle ne prétend pas reconstituer toute la logique du client.

### Réserves importantes

- **Collector :** l’export consulté indique le niveau 42 et cinq prérequis, tandis que la wiki communautaire Fandom consultée donne le niveau 40 et quatre. L’interface s’appuie sur la première source et affiche explicitement cette divergence; aucune validation en jeu n’a été faite.
- Le snapshot donne **44 objectifs Collector**, tous marqués Found in Raid (FIR) dans l’export. Cette balise exportée ne confirme ni le contenu actuel du client ni l’éligibilité d’une remise dans un profil donné.
- Les 13 tâches marquées Kappa et les **zéro** balises Lightkeeper sont des propriétés des champs exportés, pas une preuve d’exhaustivité ni d’absence de contenu Lightkeeper. Les neuf identifiants signalés dans l’issue communautaire #886 n’apparaissent dans aucun des trois modes interrogés; aucune conclusion d’absence n’en est tirée.
- L’export contient 16 enregistrements de traders/personnages; les pages distinguent les **10 traders** des six autres interlocuteurs. Les stocks, rotations et conditions doivent être contrôlés dans le client.
- Les seuils LL4 du tableau d’aperçu sont des valeurs d’export : Prapor niveau 36 / réputation 7,9; Therapist 37 / 5,8; Skier 38 / 5,8; Peacekeeper 37 / 6,0; Mechanic 40 / 7,6; Ragman 42 / 6,5; Jaeger 33 / 7,3. La note officielle BSG 1.1.0.0 indique que le volume d’achats ne constitue plus une exigence de loyauté; cela ne transforme pas les autres champs communautaires en validation officielle.
- Le total de lignes matériaux est une mesure d’export, non une liste d’achats recalculée selon les prix du marché. Le filtre FIR Seasonal est à zéro dans le snapshot.

## Fonctionnalités et intégration

- Index traders avec 16 cartes, filtres spécialité/type, profils liés et tableau LL4 filtrable par mode.
- Recherche et filtres de tâches par trader/mode/critères; suivi local dans `localStorage`; liens profonds qui conservent le mode demandé.
- Arbre de prérequis avec cases locales et export JSON téléchargeable; le suivi reste dans le navigateur de l’utilisateur.
- Checklist Kappa de 44 objectifs, mode, recherche, progression et effacement local.
- Hideout avec 26 stations, niveaux, liens profonds, matériaux FIR et filtres distincts par mode.
- Atelier avec 214 recettes dans chaque snapshot; prix et frais saisis par l’utilisateur, calcul de lot/marge sans connexion à un marché live.
- Contenu HTML pré-rendu : les pages de quêtes, Kappa, Hideout et crafting conservent des replis lisibles sans JavaScript.

Les huit JPG de `images/phase7/` sont des illustrations éditoriales originales et génériques (comptoir/registre, dossier/tableau de quêtes, conteneur et atelier/plan). Elles ne sont ni des captures du jeu, ni des portraits officiels, ni des sources de statistiques. Le CSS, le module `js/phase7.js`, le jeu de données `js/data/phase7.json` et les liens de navigation/recherche ont été raccordés aux gabarits communs. `scripts/serve_home.py` autorise les 16 routes, leurs ressources et les trois snapshots datés.

## Fichiers principaux

- Génération et validation des données : `scripts/phase7_pages.py`
- Sorties statiques : `pages/traders/`, `pages/quests/`, `pages/hideout/`
- Données intégrées : `js/data/phase7.json`
- Comportements et styles : `js/phase7.js`, `css/pages/phase7.css`
- QA : `scripts/qa_phase7_browser.cjs`, `data/snapshots/validation-phase-7.json`
- Sources : `docs/sources.json`, `docs/recherche-tarkov-2026-11-18.md`

## État suivant

PHASE_7 est terminée et le workflow revient à **ATTENTE_CONTINUE**. PHASE_8 n’est pas commencée. La publication réelle demeure séparément bloquée; ne pas mettre en ligne le sitemap d’aperçu, ajouter de canonical public ou lancer `--confirm-public-base` avant vérification du dépôt, du domaine, du DNS, du TLS et du routage.
