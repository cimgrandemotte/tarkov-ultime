# Vérifications · PHASE 5 — Armes et munitions

**Données et sources vérifiées le 18/11/2026. QA navigateur relancée après les changements d’images, de graphique et de garde-fou SEO : 18/11/2026 à 23:46:12.965 UTC.**  
**Résultat : 49/49 contrôles passés.** Rapport machine courant : `data/snapshots/validation-phase-5.json` (`checkedAt: 2026-11-18T23:46:12.965Z`). Cette exécution remplace les horodatages de QA contradictoires des anciens rapports.

Ce dossier vérifie le site et ses instantanés éditoriaux, **pas le client EFT**. `[BSG]` signifie annonce de Battlestate Games; `[EXPORT]` signifie données communautaires récupérées par Tarkov.dev; `[COMMUNAUTÉ]` signifie guide, forum, vidéo ou code tiers. Aucun de ces derniers ne devient une règle officielle sans confirmation BSG. Les écrans du jeu, raids, comptes, prix live et résultats de pénétration n’ont pas été testés.

## Sources, veille et interprétation

1. **BSG, journal technique du 18/11** — [annonce Steam](https://steamcommunity.com/games/3932890/announcements/detail/719048067771269207) et [page officielle BSG](https://www.escapefromtarkov.com/news/id/420). La 1.3.5.0 est annoncée pour la seconde moitié de novembre, sans date précise ni confirmation de déploiement : Unity 6, chargement serveur en parallèle, reconnexion rapide, mémoire, stabilité et performance annoncés. DirectX 12, DLSS Frame Generation x2/x4 et Reflex sont des travaux futurs; le rework de végétation est repoussé; FSR 4 est visé avant fin 2026. Ce journal ne publie pas de rééquilibrage général des cartouches joueur.
2. **BSG, messages du 12–13/11** — [canal officiel EN, 12 novembre](https://t.me/escapefromtarkovEN/6990), [message du 13 novembre sur X](https://x.com/tarkov/status/2121284426583716242). Le message du 12/11 porte plusieurs changements Seasonal et l’affaiblissement de The Wedge et de ses gardes tous modes; les munitions citées concernent ces IA et aucune cartouche n’est nommée. Le 13/11, des mallettes contenant des documents sont ajoutées aux largages Seasonal et les offres d’équipement Black Division demandent argent ou troc dans tous les modes. Aucun de ces messages ne suffit à modifier une ligne de balistique joueur ni à dater un nouveau tableau de munitions.
3. **Exports Tarkov.dev** — [endpoints et modes](https://json.tarkov.dev/endpoints), snapshots locaux :
   - `data/snapshots/phase-5-catalogue-2026-11-18.json`, collecte `2026-11-18T16:08:28Z`;
   - `data/snapshots/phase-5-crafts-2026-11-18.json`, collecte `2026-11-18T16:59:57+01:00`;
   - `data/snapshots/phase-5-traders-hideout-2026-11-18.json`, collecte `2026-11-18T17:01:09+01:00`.
   Les routes utilisent `regular`, `pve` et `pvp-season`. Ce sont des instantanés JSON communautaires, sans version de client embarquée ni garantie d’état live.
4. **Guide communautaire/commercial** — [LFCarry, guide munitions](https://lfcarry.com/guides/tarkov-ammo-chart), daté du 17/11 et annoncé à jour pour 1.3.0.2. Il présente 31 munitions de 12 calibres et des tiers/conseils; par exemple, il affiche DVC12 à 52 pénétration/46 dégâts et DBP191 à 39/53. Ces valeurs et surtout ses rangs S/A sont des affirmations de tiers, à recouper avec les snapshots, pas une méta vérifiée par BSG ou reproduite en client.
5. **Vidéo communautaire** — [Snap and Boom Gaming, “Why Your Bullets Aren’t Working?”](https://www.youtube.com/watch?v=Z2Q-L9KyAUU), 09/10/2026, avant les derniers changements de novembre. Le contenu exploitable consulté porte surtout sur compétences/progression et conseils débutants; il ne valide ni le patch courant, ni une tier list de novembre.
6. **Retours Reddit** — [fil notes 1.3.0.0](https://www.reddit.com/r/EscapefromTarkov/comments/1xicxsn/discussion_1300_patch_notes/) et [discussion PvE](https://www.reddit.com/r/EscapeFromTarkovPvE/comments/1xidn32/discussion_1300_patch_notes/), du 29/10. Témoignages contradictoires sur bots/difficulté, antérieurs aux changements de novembre; ils ne fondent aucune statistique chiffrée sur les munitions.
7. **Méthode GitHub** — [TarkovGunsmith PR #249](https://github.com/UnderMyBed/TarkovGunsmith/pull/249), 16–17/10. Le rapport communautaire indique que la formule MOA reproduit 399/399 presets sur sa capture du 17/10; ses facteurs d’ajustement de précision/vitesse sont sans oracle. Référence de méthode, pas donnée officielle actuelle.
8. **Veille complémentaire du 18/11** — les limites et retours communautaires sur Icebreaker, Kord Breach, outils de carte, droits d’images et Unity 6 sont consignés dans `docs/recherche-tarkov-2026-11-18.md`. Reddit direct a renvoyé HTTP 403; la vidéo du 14/11 n’a pas été visionnée intégralement; aucun raid client n’a été effectué. Les témoignages et outils communautaires ne sont ni des règles BSG ni une validation en jeu.

## Intégrité des données et pages

- **Snapshot QA et registre de production :** `data/snapshots/validation-phase-5.json` est valide à **49/49**. Aucun contrôle ne signale une violation axe-core dans les 13 audits Chromium; axe-core n’est pas exécuté dans Firefox par le script.
- Les données de catalogue sont des projections des exports Tarkov.dev; mode, collecte et sommes de contrôle sont conservés dans `js/data/catalog-manifest.json`. Aucun numéro de build n’est fourni par l’export.
- Les fiches restent fondées sur les snapshots communautaires cités : mode, collecte et provenance sont conservés. Les marqueurs de loot, taux de spawn, prix et statistiques ne deviennent pas des faits officiels ou validés en jeu sans source primaire ou test documenté. Les autres pages livrées sont accessibles dans l’aperçu local, mais aucune publication publique n’est établie.

## Images et graphique après refonte

Les références d’objets dans Arsenal/Munitions n’intègrent plus les URL d’images de Tarkov.dev. Le rendu utilise des illustrations éditoriales génériques locales en JPG par famille; leurs vignettes sont décoratives (`alt=""`) et l’introduction précise qu’elles ne représentent pas l’ID EFT exact. Les URL communautaires gardées dans l’export ne sont pas chargées par le navigateur.

Audit statique du build complet après reconstruction : **51 routes HTML**, **2 283 références raster locales**, toutes en JPG/JPEG et toutes résolues; les **50 URL d’image uniques** référencées répondent HTTP 200 par le serveur à liste blanche; **54 fichiers image JPG/JPEG** (plus 11 marqueurs `.gitkeep`, qui ne sont pas des images); aucune image externe, référence manquante, ressource PNG/SVG ou balise `<svg>` inline dans le HTML/CSS audité. Le graphique balistique est un nuage HTML/CSS avec **180 points** et une table numérique accessible; aucun graphique SVG n’est généré. La QA navigateur valide toujours le filtre synchronisé et le repli sans JavaScript.

## QA automatisée

Commande ayant produit le rapport : `PLAYWRIGHT_BROWSERS_PATH=/tmp/tarkov-browsers PHASE5_BASE_URL=http://127.0.0.1:4180 node scripts/qa_phase5_browser.cjs`. Rapport détaillé : `data/snapshots/validation-phase-5.json`.

| Zone | Résultat |
|---|---|
| Chromium 159.0.8154.6 | 13 contrôles de routes (métadonnées, images, erreurs, débordements et reflow initial), interactions Arsenal/mêlée/munitions/graphique/modifications, responsive, clavier, préférences système, mobile, sans JS et accueil. |
| axe-core | **13 audits Chromium, 0 violation** sur les routes PHASE_5. Les états `incomplete` sont des éléments à revue manuelle, pas des violations. |
| Firefox 159.0 | Routes, rendu et interactions fonctionnels passés. axe-core **n’est pas exécuté dans Firefox** par le script. |
| Interactions | Filtres, modes, comparateurs, tâche/craft M855A1, synchronisation du tableau et du graphique; filtres croisés slot/famille, tri alphabétique et tri par nombre de plateformes compatibles. |
| Responsive | Quatre routes testées à 320, 375, 768, 1 024 et 1 440 px; aucun débordement de racine/corps. |
| Clavier et préférences | Premier focus visible; forced-colors et reduced-motion. Les points du graphique restent volontairement non interactifs, avec table équivalente. |
| Sans JavaScript | Hub Arsenal, modifications, hub Munitions et graphique : données/table visibles, contrôles progressifs masqués; graphique HTML/CSS avec table de secours. |

### Performance mobile — snapshot courant

Simulation Chromium : viewport 390 × 844, device scale factor 1, réseau 4G (150 ms de latence, 187 500 octets/s en téléchargement, 93 750 octets/s en envoi), CPU ×4. Seuils d’acceptation : LCP ≤ 2 500 ms, CLS ≤ 0,1.

| Route | DCL | LCP | CLS | `PerformanceNavigationTiming.transferSize` |
|---|---:|---:|---:|---:|
| `pages/weapons/weapon-mods.html` | 1 872 ms | **1 520 ms** | **0** | 92 501 octets |
| `pages/ammo/ammo-chart.html` | 2 780 ms | **2 028 ms** | **0** | 55 456 octets |

Les deux LCP restent sous le seuil de 2 500 ms; les deux CLS valent 0. DCL est consigné mais **n’est pas le seuil mobile bloquant** du script. `transferSize`/`transferBytes` mesure le document principal et ses en-têtes, pas l’ensemble des ressources. Ce sont les valeurs du snapshot courant (`2026-11-18T23:46:12.965Z` UTC), qui remplacent les métriques des exécutions antérieures.

Optimisations appliquées : gzip des réponses textuelles dans `scripts/serve_home.py`; dérivé JPEG responsive 640 × 357 de la page Mods (`images/weapons/weapon-mods-inspection-640.jpg`, 54 997 octets; original 183 540 octets) et préchargements `imagesrcset` concordants pour éviter le téléchargement simultané du grand original; `font-display: optional` pour empêcher les swaps tardifs responsables de CLS; espace réservé aux commandes mobiles masquées jusqu’à l’initialisation JS; table longue des modifications différée après la première peinture, avec repli `<noscript>` complet.

Les résultats mobiles observés correspondent au serveur d’aperçu qui compresse gzip. **Activer gzip ou Brotli sur l’hébergement de production** pour conserver un transfert équivalent; si l’hébergement sert le HTML brut, ces métriques ne sont pas transposables.

## Rejouer le build et la QA

Après confirmation effective du dépôt, du DNS, du certificat TLS et du routage GitHub Pages, remplacer `<BASE_HTTPS>` par l’URL publique du guide (avec `/` final et éventuel sous-chemin), puis fournir l’opt-in explicite :

```sh
python3 scripts/build_home.py --base-url <BASE_HTTPS> --confirm-public-base
python3 scripts/build_home.py --check --base-url <BASE_HTTPS> --confirm-public-base
python3 -m py_compile scripts/*.py
PLAYWRIGHT_BROWSERS_PATH=/tmp/tarkov-browsers PHASE5_BASE_URL=http://127.0.0.1:4180 node scripts/qa_phase5_browser.cjs
```

`--confirm-public-base` n’effectue pas de vérification réseau; il ne doit être utilisé qu’après les contrôles manuels décrits dans `docs/publication-github-pages.md`. Pour un aperçu, exécuter `python3 scripts/build_home.py` sans opt-in.

Les captures de métriques sont variables selon le processus et la machine; le snapshot versionné est la référence de cette exécution, pas une garantie de performance sur tout hébergement ou appareil.
