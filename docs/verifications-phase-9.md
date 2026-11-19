# Vérifications PHASE_9 — SP-Tushonka, Arena et événements

**Résultat final : PASS.** Les sept routes sont générées et intégrées; build sans écart, audit statique et HTTP réussis, 39/39 contrôles navigateur PASS, sept audits axe-core sans violation. Aucun déploiement n’a eu lieu.

## Résultats

| Contrôle | Résultat |
|---|---|
| Validation des sources / générateur | 7 routes planifiées; 7 JPG valides; chaque clé `sources.json` référencée existe |
| Build | `python3 scripts/build_home.py` puis `python3 scripts/build_home.py --check` réussis; 84 routes HTML statiques |
| Recherche | 1 301 entrées; les sept nouvelles routes apparaissent une fois chacune |
| Sitemap | 84 URLs uniques, dont les sept routes PHASE_9 |
| Audit HTML local | 7 pages; 401 liens, ressources et fragments locaux résolus; zéro ID dupliqué ou image sans alt |
| SEO aperçu | `noindex,follow` présent; aucun canonical ni `og:url` public; JSON-LD Article valide |
| Sources et médias | 47 clés de source utilisées sur 250; 7 JPG RGB, 1376 × 768, correctement intégrées et empreintes SHA-256 calculées |
| Liste blanche d’aperçu | 7 routes, 7 images, CSS et module JS PHASE_9; trois routes dossier mappées explicitement |
| Vérification HTTP | 20 ressources publiques testées en HTTP 200; 10 chemins privés, rapports, scripts et quarantaine en HTTP 404 |
| Rendus navigateur | 14 rendus : 7 routes en Chromium et Firefox; titres, H1, hero, scripts, erreurs et JSON-LD contrôlés |
| axe-core | Sept audits Chromium; **zéro violation** détectée |
| Responsive | 8 routes (7 nouvelles + accueil) à 375, 768 et 1440 px; aucun débordement horizontal |
| Sans JavaScript | Les sept routes gardent leurs sections et navigation; dix entrées d’événements et les quatre descriptions Arena restent lisibles |
| Interactions | **39/39 PASS** : filtres SPT/installation/mods/dépannage/événements, onglets clavier Arena, recherche locale, liens PHASE_9 sur l’accueil et depuis les pages PHASE_8, et menu mobile |

La recherche « City Drops » renvoie la chronologie. Le filtre d’événements conserve 10 repères puis renvoie 3 actifs, 1 annoncé, 5 archivés et 1 contenu durable. Les tests de filtres sont locaux; ils n’interrogent pas le jeu.

## Relecture factuelle et réserves

Les fiches The Forge SAIN 4.5.1, SVM 2.2.3, Icebreaker Backport 1.2.4, Waypoints 1.9.0 et BigBrain 1.5.0 ont été consultées directement le 18 novembre. Les pages de City Drops Steam, du patch Arena 0.6.2.5, du patch 0.6.0 et du support Arena sont également consultées directement. Le suivi Halloween BSG du 16 novembre confirme une clôture annoncée seulement « la semaine prochaine »; aucun jour précis n’a été extrapolé.

- Les publications Reddit, vidéos et issue Proton sont des pistes/anecdotes, pas des preuves de compatibilité ou d’une panne générale.
- Blackout est indiqué comme archivé, mais sa clôture finale exacte n’est pas vérifiée par une annonce primaire récupérée; la page conserve explicitement cette incertitude.
- Une compatibilité déclarée par The Forge ne vaut pas certification globale ni compatibilité Fika. Les dépendances et la sauvegarde de profil sont signalées.
- Les dates sont un relevé éditorial daté, pas un flux live. Les événements peuvent changer après le 18 novembre.

## Aperçu et confidentialité

Le serveur de prévisualisation répond 404 pour `docs/sources.json`, `workflow.json`, `state_machine.json`, scripts internes, rapports QA, instantanés de référence et chemins de traversal testés. Les routes utilisent la base temporaire `https://4180-i8gmoighw6d8bspep6ilb.e2b.app/`; elles portent `noindex,follow` sans canonical ni URL Open Graph publique. Le sitemap et `robots.txt` de l’aperçu ne sont pas des artefacts de production.

La présence de ces routes dans l’aperçu ne vérifie ni un dépôt public, ni un nom de domaine, ni le DNS, TLS ou GitHub Pages. Aucun déploiement n’a été déclenché.

## Commandes de reproduction

Depuis `/home/user/tarkov-ultimate-guide` :

```sh
python3 -m py_compile scripts/phase9_pages.py scripts/build_home.py scripts/serve_home.py scripts/qa_phase9_static.py
python3 scripts/phase9_pages.py
python3 scripts/build_home.py
python3 scripts/build_home.py --check
```

Avec l’aperçu en cours sur le port 4180 :

```sh
PHASE9_BASE_URL=http://127.0.0.1:4180 python3 scripts/qa_phase9_static.py
PHASE9_BASE_URL=http://127.0.0.1:4180 node scripts/qa_phase9_browser.cjs
```

## Rapports et fichiers de référence

- `data/snapshots/validation-phase-9-static.json`
- `data/snapshots/validation-phase-9.json`
- `scripts/phase9_pages.py`
- `scripts/qa_phase9_static.py`
- `scripts/qa_phase9_browser.cjs`
- `css/pages/phase9.css`, `js/phase9.js`
- `scripts/build_home.py`, `scripts/serve_home.py`, `templates/index.html.in`

Ces résultats valident uniquement la génération et l’aperçu local; ils n’attestent pas une publication.
