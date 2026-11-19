# Vérification — PHASE_7

**QA navigateur locale : PASS** · `checkedAt: 2026-11-19T00:58:54.228Z` (UTC) · rapport machine : `data/snapshots/validation-phase-7.json`. L’aperçu est servi par la liste blanche locale; cette vérification ne vaut pas test d’hébergement public, de client EFT ou de raid.

## Résultats navigateur

| Contrôle | Résultat |
|---|---:|
| Routes PHASE_7 configurées | **16/16** |
| Contrôles HTTP/rendu des routes | **32/32** — 16 routes Chromium et 16 Firefox, HTTP 200 |
| Contrôles groupés du rapport | **46**, zéro échec |
| Audits axe-core Chromium | **16**, zéro violation détectée |
| Titres, H1, descriptions, JSON-LD, image principale, ressources CSS/JS et SEO d’aperçu | **16/16 par navigateur**; pas de canonical d’aperçu |
| Interactions | Traders, LL4/modes, recherche et suivi des quêtes, deep links, arbre/JSON, checklist Kappa, filtre FIR du Hideout et calculateur de craft — **PASS** |
| Repli sans JavaScript | **4 pages**; 60 lignes de quêtes, 44 objectifs Kappa, 26 stations et 214 recettes lisibles |
| Reflow responsive | **3 mesures représentatives** : 375 px (Quêtes), 320 px (Hideout) et 768 px (Traders), sans débordement horizontal |
| Erreurs JavaScript, requêtes échouées ou violation axe | **0**; le navigateur demande aussi `/favicon.ico`, non fourni et non audité (404 non bloquant) |

La QA contrôle les 16 routes dans Chromium et Firefox; axe-core est exécuté sur les 16 pages Chromium. Les tests responsive sont des points de contrôle représentatifs, pas une certification de tous les appareils, navigateurs ou dimensions.

Les scénarios d’interaction couvrent notamment les filtres de spécialité/type et LL4, le chargement des modes regular/PvE/Seasonal, l’état local des tâches, la conservation d’un mode dans un lien profond, l’export JSON de l’arbre, la recherche/effacement de la checklist Kappa, les matériaux FIR et la persistance locale des prix de craft.

## Build, données et serveur d’aperçu

- `python3 -m py_compile scripts/phase7_pages.py scripts/build_home.py scripts/serve_home.py` — OK.
- `node --check js/phase7.js` et `node --check scripts/qa_phase7_browser.cjs` — OK.
- `python3 scripts/phase7_pages.py --check` — OK : 16 routes, trois snapshots séparés, union de 526 tâches, 26 stations.
- `python3 scripts/build_home.py --check --base-url <base d’aperçu>` — OK : **67 routes statiques**, sitemap et index de recherche conformes; le sitemap d’aperçu contient 67 URLs et l’index **1 284 enregistrements**.
- Réponses HTTP 200 contrôlées sous le serveur local pour les routes principales, le CSS/JS PHASE_7, `js/data/phase7.json`, les huit JPG et les snapshots; la liste blanche `scripts/serve_home.py` inclut les routes et assets traders/quêtes/Hideout ainsi que les mappings de répertoires.
- Le rapport détaillé contient les résultats route par route, les tailles HTML, navigateurs, audits axe-core, interactions et mesures responsive.

## Réserves

Les tests de données valident les snapshots communautaires et les comportements statiques; ils ne prouvent ni stock de trader en direct, ni prix actuel, ni condition complète de quête dans le client. La divergence Collector (niveau 42/cinq prérequis dans l’export contre 40/quatre dans Fandom) et les identifiants absents de l’issue #886 restent documentés dans `docs/phase-7.md` et `docs/sources.json`.

Les canonical, `og:url` et `mainEntityOfPage` sont volontairement absents des pages d’aperçu. Le domaine, le certificat TLS et la configuration GitHub Pages n’étant pas confirmés, l’URL et le sitemap de prévisualisation ne doivent pas être publiés ni soumis aux moteurs de recherche.
