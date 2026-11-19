# Architecture · Dossier de fondation

## Produit

- **87 routes HTML planifiées.** Les contenus essentiels, le sommaire, la navigation et les tableaux d’introduction sont lisibles sans JS. Les scripts ajoutent les interactions ; ils ne sont pas nécessaires pour accéder à un guide.
- **Site statique en français.** Les noms propres et termes du jeu restent reconnaissables (anglais en regard au besoin). `docs/plan-editorial.json` fait foi pour les routes. Les pages à construire ne doivent pas produire de liens cassés en prévisualisation : masquer le lien ou indiquer « à venir » sans lien.
- **Un seul jeu, des contextes distincts.** PvP permanent, PvE officiel et PvP saisonnier ont des jeux de données séparés. Arena et Tushonka font l’objet de dossiers séparés. Un événement reçoit une date et un statut, pas un badge « actif » permanent.

## Arborescence et responsabilités

| Emplacement | Responsabilité |
|---|---|
| `lab/` | Banc d’essai indépendant (`noindex`), sans liens éditoriaux ni compte dans les pages livrées. Exclure de la distribution publique. |
| `index.html`, `pages/*.html`, `pages/*/*.html` | Pages distinctes. En-tête, pied de page et fil d’Ariane cohérents. Routes et métadonnées dérivées du manifest lors de la production. |
| `css/main.css` | Reset limité, tokens, grilles, styles typographiques et base d’accessibilité. |
| `css/components.css` | BEM : `.site-header`, `.mega-menu`, `.guide-card`, `.data-table`, modales, accordéons, tooltips, onglets et états vide/erreur. |
| `css/animations.css`, `css/responsive.css`, `css/pages/` | Effets contrôlés (pluie, parallax plafonné, transitions), adaptations mobile, styles par dossier quand nécessaires. |
| `js/main.js`, `js/search.js` | Navigation, agréments clavier, recherche Fuse.js locale insensible aux accents et index des seules routes publiées. |
| `js/audio.js`, `js/animations.js` | Audio Howler.js, arrêt et volume accessibles ; révélations AOS ou repli natif, animations décoratives suspendues hors écran. |
| `js/components/` | Composants opt-in : tooltip, modal, filter, comparator, tierlist. Sur une modal : focus initial, boucle clavier, Échap, retour au déclencheur. |
| `js/data/` | JSON locaux, chargés par section et mode, pas de gros catalogue sur l’accueil. Graphique Chart.js local uniquement sur les pages qui l’utilisent. |
| `images/{hero,beginners,maps,weapons,bosses,armor,items,traders,hideout,lore,spt,ui}` | JPG haute définition, crédits et légendes ; distinction entre illustrations IA et captures ou cartes vérifiées. |
| `audio/{ambient,ui,themes}` | MP3 d’ambiance originaux ; son jamais requis pour comprendre le contenu. |
| `docs/`, `data/snapshots/`, `scripts/` | Manifest éditorial, sources et vérifications, relevés datés et import reproductible. Ne pas exposer les scripts de production comme routes au lecteur. |

## Direction artistique et parcours

- Noir `#0a0a0a`, ambre `#c8aa6e`, olive `#4a7c59` et ambiances pluvieuses. Les couleurs de rareté ou de danger sont accompagnées de mots et d’icônes ; les gris faibles servent aux décors, pas au texte informatif.
- Orbitron pour les titres d’ambiance, Rajdhani pour les labels, Inter pour la lecture, Share Tech Mono pour les chiffres. Polices locales WOFF2 avec licence vérifiée, `font-display: swap` et polices de repli. Pas de dépendance impérative à un CDN, y compris en prévisualisation.
- Trois entrées prioritaires : **premier raid**, **choix de carte/extraction**, **comparaison d’équipement**. Pied de page avec crédits, méthodologie, accessibilité et mention explicite du caractère non officiel.
- Les mots-clés, icônes, ancres et compatibilités demeurent lisibles en petit écran. Afficher l’unité, le mode et la date près d’une donnée variable. Les annonces de version et les statistiques du jeu ne sont pas des instructions pour du matériel réel.

## Critères techniques

**Accessibilité.** WCAG 2.1 AA est une cible à vérifier, pas une certification déjà acquise. Lien d’évitement, ordre des titres, `:focus-visible` et libellés visibles, contrastes ≥ 4,5:1 pour le texte courant, navigation au clavier/tactile, zoom à 200 %, préférence de mouvements réduits. Les tables ont des en-têtes `scope`, les graphiques une alternative tabulaire. Pas de fonction uniquement au survol ; pas de réorganisation des tier lists exclusivement par glissement.

**Performance.** Visuel hero prioritaire et préchargé pour le LCP ; tailles intrinsèques sur toutes les balises `img`, `loading="lazy"` hors du premier écran. JPG compressés après contrôle visuel, environ qualité 85, versions dimensionnées selon l’usage. Éviter les fichiers superflus et charger les catalogues et scripts spécialisés à la demande. Cibles de contrôle : navigation utilisable à 320/375, 768, 1024 et 1440 px, pas de rupture du layout, LCP ≤ 2,5 s et CLS ≤ 0,1 dans un profil documenté. Ne pas promettre que le résultat sur un proxy reproduit chaque réseau réel.

**SEO.** Titre, description distincte de 150–160 caractères, Open Graph, Twitter Card et JSON-LD `WebSite` ou `Article`, `FAQPage` uniquement pour les FAQ visibles. URL canonique, sitemap et métadonnées absolues générés une fois l’origine publique connue ; pas de faux domaine éditorial. Liens relatifs utilisables sous un sous-répertoire et sans API privée.

**Médias.** Au moins deux JPG pertinents par page ; prioriser les panoramas propres aux lieux et les portraits propres aux personnages majeurs. En phase chargée, mutualiser la seconde illustration thématique quand le contexte le justifie. Une carte annotée se base sur des coordonnées vérifiées ou un fond dont l’autorisation est documentée : les rendus de fiction ne font pas office de carte factuelle. Les listes et les schémas HTML complètent les JPG. Maximum de 10 créations JPG et 10 créations MP3 par réponse, suivis dans le workflow ; pas d’archive ni de PDF. Les MP3 d’ambiance seront des créations originales, sans échantillons repris au jeu ; silence par défaut, démarrage par action explicite et pas de sons de survol imposés.

## Mise à jour et assurance qualité

1. **Avant chaque rédaction :** lire les sources principales de la page, chercher changements récents, recouper les mécaniques (indicateurs du jeu, wiki, trackers) et dater les preuves. Reddit, Discord, X et YouTube servent à repérer et documenter les retours ; ne pas citer une discussion privée ou un résultat non vérifiable comme preuve.
2. **Données :** actualiser l’export Tarkov.dev à la phase concernée. Ne pas effacer un relevé valide en cas de réponse amont invalide. Les valeurs nulles et les désaccords restent signalés. Les prix n’ont pas de mention « temps réel » hors dispositif fraîcheur validé.
3. **Contrôle avant passage de phase :** valider les liens et médias publiés, tester au clavier, tester filtres/tri, états vides et zoom mobile. Mettre les pages et fichiers livrés à jour dans `workflow.json` et synchroniser `state_machine.json`.
4. **Fonctions de phase 1 :** poser les tokens/BEM, composants sémantiques, navigation et index de démonstration, vérifications de clavier et de contraste, puis ambiances MP3 et repli sans JS. La vraie page d’accueil et sa preview arrivent en phase 2.

## Assemblage, aperçu et prévisualisation

- `data/home.json` et `templates/index.html.in` alimentent l’accueil. `data/guides.json`, `docs/sources.json`, `templates/guide.html.in` et les deux corps de dossier alimentent les routes `pages/getting-started.html` et `pages/lore/index.html`. `scripts/build_home.py` et `scripts/guide_pages.py` assemblent les pages, l’index global et le sitemap ; ne pas éditer les artefacts à la main. Les compteurs du catalogue restent dérivés de `js/data/catalog-manifest.json`.
- **SEO.** `canonical`, `og:url` et `mainEntityOfPage` ne sont générés que pour une base HTTPS explicitement confirmée; ils sont omis sur toute prévisualisation, hôte local ou domaine réservé/non confirmé. Le CLI exige `--confirm-public-base` pour une origine non reconnue comme aperçu; cet opt-in ne teste pas DNS/TLS et ne doit être passé qu’après vérification du dépôt Pages, de son propriétaire, du DNS et du certificat. Exemple après confirmation : `python3 scripts/build_home.py --base-url https://votre-domaine.fr/tarkov/ --confirm-public-base`. Sinon, le build utilise l’aperçu Arena, sans canonical/`og:url`/`mainEntityOfPage`; son sitemap absolu est privé à l’aperçu et ne doit pas être soumis. `--check` détecte les artefacts divergents sans les réécrire.
- **Navigation et recherche.** Tous les liens locaux restent relatifs. `data-search-base` donne le niveau de résolution des résultats des trois routes (alias `/` ↔ `/index.html` et `/pages/lore/` ↔ `/pages/lore/index.html`). Fuse et l’index sont chargés à l’ouverture du dialogue. Les réponses ciblées de la FAQ peuvent être révélées sur navigation d’ancre. Le bloc de révélations de la campagne, en `<details>` fermé par défaut, n’a ni ancre intérieure ni entrée de recherche ; `data-nosnippet` marque son corps. Ce masquage éditorial ne constitue ni un contrôle d’accès ni une garantie de comportement de tous les moteurs.
- **Progressif.** Le sommaire et les sections sont du HTML ; sans JS, les deux panneaux PMC/Scav et les accordéons restent lisibles. `js/components/checklist.js` réutilise la procédure locale avec deux clés distinctes : `tug:checklist:premier-raid:v1` et `tug:checklist:starter-raid:v1`. `js/guides.js` ajoute le filtre de FAQ, la mise à jour du sommaire et l’ouverture d’une question ciblée, pas l’ouverture des révélations de campagne.
- **Aperçu.** `python3 scripts/serve_home.py --host 0.0.0.0 --port 4180` sert les seules routes et ressources autorisées. MIME contrôlés, plages MP3, `X-Robots-Tag: noindex, nofollow`. Aucun rapport interne, catalogue lourd, route promise, JPG de réserve ou fichier de pilotage n’est servi. Pour héberger publiquement le guide, déployer seulement les fichiers de la liste `PUBLIC_FILES` (et la résolution des index de répertoire), avec la configuration SEO du véritable hébergeur.
- **Atelier séparé.** `python3 scripts/serve_lab.py` ouvre `/lab/` (4173). Voir [le bilan des fondations](phase-1.md) et `data/snapshots/validation-phase-1*.json`. Les six objets de démonstration viennent du mode `regular`, distincts des presets et des prix.
- **Validation.** `python3 scripts/check_phase3.py` vérifie le troisième jalon ; `--artefacts-seuls` contrôle le résultat HTML, les ancres, le référencement et la liste blanche sans exiger l’état de clôture. Les tests `scripts/tests/phase{1,2,3}*.cjs` documentent le clavier, l’audio sur commande, le rendu mobile et les régressions. L’option `TUG_QA_REPORT` permet de conserver les preuves historiques de l’accueil et de l’atelier au lieu de les écraser.
