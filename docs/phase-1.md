# PHASE 1 — Socle technique validé

**18 novembre 2026 · Prochain jalon : PHASE 2, l’accueil.** L’aperçu **Atelier Tarkov — aperçu technique** ouvre le banc d’essai à `/lab/`. Il n’est pas destiné à l’indexation ni à la diffusion du guide. Il démontre les composants partagés ; **aucune des 87 routes éditoriales n’est encore publiée**.

## À essayer dans l’atelier

1. **Rechercher** : ouvrez la recherche avec le bouton, `Ctrl` + `K` ou `⌘` + `K`. Tapez `foret` ou `comparteur` pour essayer les accents et les coquilles. Les flèches parcourent les résultats, `Entrée` ouvre le lien et `Échap` ferme la fenêtre.
2. **Comparer l’équipement** : filtrez les six modèles par famille ou par nom, triez par ergonomie ou cadence, puis incluez deux à trois modèles. Le comparateur utilise le relevé **PvP permanent** de Tarkov.dev. Ce sont des statistiques de jeu **de l’objet de base**, pas d’un preset monté, et aucun prix n’est extrapolé.
3. **Adapter l’interface** : essayez le contraste renforcé, la réduction des animations, les accordéons et le classement de priorités. Sans JS, la navigation, les six entrées, les informations et la piste de pluie restent accessibles ; la recherche et le comparateur sont des fonctions améliorées.
4. **Écouter** : choisissez une piste, puis cliquez sur **Lire**. Il n’y a **aucun chargement de MP3 au démarrage** et aucun son au survol. Changer de piste arrête la lecture sans en relancer une. Le volume, le contraste, les animations et les priorités sont mémorisés dans le navigateur.

## Fichiers livrés

| Bloc | Contenu |
|---|---|
| Design | `css/main.css`, `components.css`, `animations.css`, `responsive.css` et `pages/lab.css`. Palette sombre/ambre, quatre familles de polices locales, en-tête sticky, fil d’Ariane, méga-menu, contrastes, parallax léger et pluie décorative. |
| JavaScript | `js/main.js`, `search.js`, `audio.js`, `animations.js`, `utils.js` et sept modules d’interface : tooltip, modal, filter, comparator, tierlist, tabs et navigation. Fuse, Howler et AOS sans CDN ; versions, crédits et licences dans `vendor/`. |
| Atelier | `lab/index.html` produit par `scripts/build_lab.py` depuis le modèle HTML et le catalogue local. `lab/search-index.json` indexe huit destinations présentes dans l’atelier ; **l’index éditorial est vide** jusqu’à l’accueil. |
| Illustrations | **3 JPG** originaux générés : entrepôts sous la pluie, équipement sur un établi, radio de planque. `images/ui/design-*.jpg` : **1 376 × 768 px**, qualité JPEG 85. Ce ne sont pas des captures de jeu ni des cartes de navigation. |
| Audio | **5 MP3 originaux** : trois boucles de **60 s** (pluie et tonnerre, ventilation, forêt), un clic radio (0,27 s) et un bip (0,82 s). Stéréo 44,1 kHz, 192 kbit/s ; durées et empreintes vérifiées après encodage, voir `audio/manifest.json`. Aucun échantillon repris du jeu. |
| Traçabilité | [Relevé préalable](verifications-phase-1.md), `workflow.json` et `state_machine.json` synchronisés. Le sondage distingue le patch 1.3.0.0 et l’annonce Unity 6 ; aucun catalogue n’a été remplacé. |

## Contrôles réalisés

- **Chromium 159 : 12 groupes de vérifications passés**, dont navigation au clavier, ouverture et fermeture des modales, retour du focus, filtre combiné, absence de résultat, classement, tactile émulé, lecture sur demande et repli sans JS. Largeurs : **320, 375, 390, 768, 832, 1 024 et 1 440 px** ; agrandissement des caractères à 200 % testé de 768 à 1 440 px. Le tableau défile dans son conteneur sans faire déborder la page.
- **Firefox 159 : 6 points contrôlés à 390 px**, dont recherche, focus des modales, filtres, comparateur, lecture et pause avec une sortie audio virtuelle. Le test vérifie le comportement du lecteur, pas l’acoustique d’un appareil physique.
- **WCAG 2.1 AA : aucune violation automatique signalée par axe-core dans les 5 états audités.** Les fonds photographiques ont été vérifiés par échantillonnage sur dix profils (cinq largeurs, deux thèmes) : **7,09:1** au point testé le moins contrasté du texte du visuel principal. Contraste calculé à **5,93:1** sur le texte atténué des panneaux et **3,22:1** sur les contours de commande. Ce résultat ne certifie pas le site complet ; lecteurs d’écran, Safari et appareils physiques restent à vérifier.
- **Chargement local** : ni CDN, ni catalogue entier, ni MP3 ni index de recherche en requête initiale. L’image principale est préchargée, les autres utilisent le chargement différé ; fichiers audio servis aussi par plages d’octets pour les lecteurs natifs. Mesures locales dans `data/snapshots/validation-phase-1.json`, non extrapolables au réseau mobile.

## Rejouer les validations

Depuis la racine du projet, lancer l’atelier dans un terminal :

```sh
python3 scripts/build_lab.py
python3 scripts/serve_lab.py --port 4173
```

Avec Node.js 20+, Python et Pillow, et les navigateurs Playwright installés (les dépendances Chrome/Firefox du système sont requises) :

```sh
npm install --prefix /tmp/tarkov-qa playwright@1.65.1 axe-core@4.14.1
export PLAYWRIGHT_BROWSERS_PATH=/tmp/tarkov-browsers
export NODE_PATH=/tmp/tarkov-qa/node_modules
/tmp/tarkov-qa/node_modules/.bin/playwright install chromium firefox
node scripts/tests/phase1.cjs
node scripts/tests/phase1-colors.cjs
node scripts/tests/phase1-firefox.cjs
python3 scripts/check_phase1.py
```

Sur Linux sans périphérique audio, fournir une sortie PulseAudio virtuelle au contre-test Firefox. Pour reconstruire les pistes : `python3 scripts/create_ambiences.py` avec NumPy, SciPy et FFmpeg/libmp3lame ou `imageio-ffmpeg`. Les preuves JSON sont dans `data/snapshots/`.

**Suite :** l’accueil illustré, les actualités revalidées, les chiffres sourcés et la première route de l’index éditorial seront intégrés en PHASE 2.
