# PHASE 5 — Armes et munitions

**Tarkov Ultimate Guide v3.0 · 18 novembre 2026 · contenu local livré; publication publique en attente du dépôt et du domaine.**

Les **13 routes PHASE_5** sont générées et reliées à l’accueil, à la recherche et au sitemap de prévisualisation. L’aperçu complet des phases 2 à 6 compte **51 routes statiques**. Le sitemap actuel pointe vers l’aperçu E2B et ne doit pas être soumis comme sitemap public.

## Livrables

- **Arsenal** : hub, neuf pages de familles et page des modifications. Les trois exports sont sélectionnables séparément : PvP permanent, PvE Zone et PvP Seasonal. Les filtres/comparateurs exposent les champs réellement exportés; ils ne simulent pas un build complet et ne produisent pas de tier list de méta.
- **Munitions** : index et nuage de points dégâts–pénétration, avec table HTML accessible synchronisée aux filtres. Le graphique est désormais réalisé en HTML/CSS (pas en SVG); la table complète reste disponible sans JavaScript.
- **Données** : snapshots datés des catalogues, crafts et traders/Hideout. Les valeurs d’objets, offres traders et prix du flea sont séparées. Les prix datés ou incomplets ne sont pas étiquetés « live »; un export ne prouve ni prix actif, ni déblocage, ni résultat en raid.
- **Veille** : le journal BSG du 18/11 annonce des travaux techniques pour 1.3.5.0, pas une nouvelle table balistique des munitions joueur. Les changements BSG mentionnant des munitions pour The Wedge et ses gardes restent limités aux ennemis concernés. Guides commerciaux, Reddit, vidéos et code GitHub sont documentés séparément comme sources communautaires.
- **Images** : les couvertures et vignettes sont des illustrations éditoriales locales en JPG. Les références d’objets utilisent maintenant une image générique choisie par famille; elle n’est jamais présentée comme le modèle EFT exact et n’encode ni stats ni compatibilité. Aucun hotlink d’icône d’objet Tarkov.dev n’est rendu. Les liens d’images conservés dans les exports restent des métadonnées communautaires, pas des images intégrées.

Le détail des chiffres, de la fraîcheur des sources, des limites, des tests et des réserves est dans [`docs/verifications-phase-5.md`](verifications-phase-5.md). Sources et notes de veille complètes : [`docs/sources.json`](sources.json). Rapport Playwright : [`data/snapshots/validation-phase-5.json`](../data/snapshots/validation-phase-5.json).

## Validation locale

La QA navigateur a été relancée après le remplacement des vignettes distantes par des JPG génériques locaux et après la refonte du nuage de points : **49/49 contrôles passés** (`checkedAt: 2026-11-18T23:46:12.965Z`, UTC), Chromium 159.0.8154.6 et Firefox 159.0. Les 13 routes PHASE_5 ont chacune un audit axe-core Chromium sans violation détectée. La QA couvre aussi les interactions, les largeurs 320–1 440 px, le clavier, forced-colors/reduced-motion, les quatre pages principales sans JavaScript et la performance mobile simulée.

| Simulation mobile Chromium · 390 × 844 · 4G · CPU ×4 | LCP | CLS | DCL (indicatif) | Transfert du document HTML |
|---|---:|---:|---:|---:|
| `weapon-mods.html` | **1 520 ms** | **0** | 1 872 ms | 92 501 octets |
| `ammo-chart.html` | **2 028 ms** | **0** | 2 780 ms | 55 456 octets |

Seuils bloquants : **LCP ≤ 2 500 ms** et **CLS ≤ 0,1**; les deux routes les respectent. Le transfert indiqué est celui du document principal et de ses en-têtes, pas la somme de toutes les images, polices et feuilles de style. Le serveur d’aperçu compresse les réponses textuelles en gzip; l’hébergement de production devra activer gzip ou Brotli.

## Avant publication

Le propriétaire du dépôt GitHub Pages et le domaine personnalisé ne sont pas confirmés. À la dernière vérification, `gta6guide.duckdns.org` avait un enregistrement **A** vers `185.199.108.153`, aucun CNAME visible par DNS-over-HTTPS, une réponse HTTP 404 générique GitHub Pages et un certificat HTTPS qui ne correspond pas au nom d’hôte. La correspondance entre ce DNS, un dépôt Pages et son propriétaire reste donc à résoudre. Voir [`docs/publication-github-pages.md`](publication-github-pages.md).

Le build d’aperçu omet `canonical`, `og:url` et `mainEntityOfPage`. `scripts/build_home.py` exige maintenant `--confirm-public-base` pour toute base non réservée; n’utiliser cette option qu’après confirmation réelle du dépôt, du DNS, du certificat TLS et du routage GitHub Pages. Le sitemap d’aperçu ne doit pas être publié. Le suivi de cette tâche de déploiement est `BLOQUE` dans `workflow.json`, sans remettre en cause la livraison locale PHASE_5.

Aucun client EFT ni raid n’a été testé. Disponibilité par compte, prix exploitables en direct, conditions de marchand et comportement réel des munitions restent à contrôler dans le jeu.
