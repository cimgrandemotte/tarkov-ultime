# PHASE_6 — Armures et boss

**État de livraison locale :** les 21 routes prévues sont générées et raccordées à l’accueil, à la navigation, à la recherche, au sitemap et à l’aperçu à liste blanche. Re-QA locale : **51/51 contrôles passés** (`data/snapshots/validation-phase-6.json`, `checkedAt: 2026-11-18T23:48:30.540Z`, UTC); le site des phases 2 à 6 compte 51 routes. Ce n’est pas une publication : le dépôt GitHub Pages, son propriétaire et le domaine public restent à confirmer.

## Routes

### Armures — 5

- `pages/armor/` — catalogue et filtres
- `pages/armor/body-armor.html` — gilets et plaques
- `pages/armor/helmets.html` — couvre-chefs, accessoires et eyewear
- `pages/armor/rigs.html` — portage, grilles et slots
- `pages/armor/armor-chart.html` — comparateur descriptif

### Boss — 16 routes

- `pages/bosses/` — index des rencontres
- `pages/bosses/reshala.html`
- `pages/bosses/killa.html`
- `pages/bosses/shturman.html`
- `pages/bosses/glukhar.html`
- `pages/bosses/sanitar.html`
- `pages/bosses/tagilla.html`
- `pages/bosses/kaban.html`
- `pages/bosses/kollontay.html`
- `pages/bosses/zryachiy.html`
- `pages/bosses/partisan.html`
- `pages/bosses/cultist-priest.html`
- `pages/bosses/the-goons.html`
- `pages/bosses/shadow-of-tagilla.html`
- `pages/bosses/the-wedge.html`
- `pages/bosses/vengeful-killa.html`

## Données et méthode

Le snapshot `data/snapshots/phase-6-armor-2026-11-18.json` reprend les exports locaux Tarkov.dev PvP permanent, PvE Zone et PvP Seasonal du 18 novembre 2026 : **423 enregistrements par mode**, avec groupes `headwear` 112, `rigs` 105, `attachment` 79, `body-armor` 49, `eyewear` 40 et `plates` 38. Le générateur vérifie que les IDs, noms, groupes et statistiques défensives concordent entre les modes; les données flea restent séparées par mode.

- Les plaques, les protections souples et les slots du porteur restent distincts. Les classes sont affichées par pièce/slot; aucun score ou tier global d’armure n’est calculé.
- Les zones sont des champs d’export, pas des mesures de hitbox. La compatibilité d’une plaque ou d’un accessoire ne prouve pas qu’il est monté en raid.
- Les prix flea ne s’affichent et ne participent au filtre de budget que si le scan est daté, non futur et dans le seuil de sept jours au moment de l’export. Aucun des prix du snapshot ne passe ce seuil : les valeurs sont indiquées absentes/périmées plutôt que présentées comme actuelles.
- Les informations wiki sur les lieux, comportements, équipement et santé sont attribuées à la communauté et ne sont pas des tests du client. Aucun raid client n’a été lancé pour cette phase.
- Pour Partisan, le message BSG du 9 octobre 2026 annonce **25 % de chance de base** sur Customs, Woods, Shoreline et Lighthouse. En PvP et Seasonal, le message dit que la chance finale dépend aussi des PMCs à faible karma; aucune chance finale garantie n’est affichée.
- BSG a annoncé le 12 novembre un affaiblissement de The Wedge et de ses gardes sans publier de nouveau total HP. Les 750 HP wiki sont gardés uniquement comme repère historique explicitement incertain. Aucun HP n’est affiché pour Cultist Priest faute de valeur suffisamment établie dans les pages consultées.

Les références détaillées, URL, usages et réserves sont dans `docs/sources.json`; les données éditoriales se trouvent dans `data/phase6.json`.

## Interaction et publication statique

`templates/phase6.html.in`, `scripts/phase6_pages.py`, `css/pages/phase6.css` et `js/phase6.js` produisent du HTML pré-rendu. Les tableaux et l’index de boss restent lisibles sans JavaScript; les formulaires et commandes ne sont révélés qu’après activation. Les interactions ajoutées comprennent filtres par groupe, nom, classe, zone, mode/prix, capacité et casque audio, comparaison de deux ou trois pièces du même groupe, tri numérique des rigs, onglets de mode des profils et filtres de boss par lieu. Les barres comparatives décrivent les champs, sans classement.

La recherche locale contient les 21 nouvelles pages et les objets du snapshot (**502 enregistrements** au total). Le sitemap contient les 51 routes statiques générées du site; la liste blanche `scripts/serve_home.py` autorise les nouvelles routes, le CSS/JS, les visuels Phase 6 et le snapshot. Les liens de navigation Phase 6 sont aussi intégrés aux gabarits communs.

## Limites ouvertes

- `images/armor/armor-body-plates.jpg` a été régénérée sans texte ni logo visibles, puis intégrée comme illustration générique au hero et à la galerie de `pages/armor/body-armor.html`. Le texte alternatif et les légendes précisent qu’elle n’est ni une capture de jeu ni une source de statistiques; la QA Chromium/Firefox confirme le chargement.
- Le domaine canonique HTTPS et l’hébergement restent à confirmer. Sur l’aperçu, les balises `canonical`, `og:url` et `mainEntityOfPage` sont omises; ne pas publier le sitemap d’aperçu comme sitemap public. Les observations DNS/HTTP/TLS et les étapes nécessaires sont consignées dans `docs/publication-github-pages.md`.
- Aucun test sur hébergement réel, en client EFT ou en raid n’a été réalisé. La QA PHASE_5 a également été relancée (49/49) après la refonte des vignettes et du graphique. Le workflow sépare désormais les phases de contenu livrées du blocage indépendant de publication.
