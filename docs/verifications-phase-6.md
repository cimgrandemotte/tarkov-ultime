# Vérification — PHASE_6

**Relevé éditorial :** 18 novembre 2026 · **QA locale relancée : VALIDE** (`checkedAt: 2026-11-18T23:48:30.540Z`, UTC) · **publication publique : bloquée** (dépôt, propriétaire, DNS et TLS non confirmés).

## Résultats

| Contrôle | Résultat |
|---|---:|
| Routes Phase 6 générées, uniques et servies par l’aperçu à liste blanche | **21/21** |
| Rendu Chromium | **21 routes** · HTTP 200 · titre, H1, JSON-LD, image principale, aucune erreur navigateur ou ressource échouée |
| Rendu Firefox | **8 routes représentatives** · HTTP 200 · aucune erreur navigateur ou ressource échouée |
| Audit axe-core Chromium | **21 audits, 0 violation** |
| Interactions Chromium/Firefox | **filtres d’armures, prix conservateurs, comparaison 2–3 pièces, zones casque, tri des rigs, modes boss et recherche** — valides |
| Progression sans JavaScript | **5 routes représentatives** — contenu statique et filtres masqués correctement |
| Reflow | **5 pages à 320, 375, 768, 1 024 et 1 440 px** — aucun débordement du document |
| Routes / assets dans l’aperçu | **21 liens internes et 3 ressources contrôlés : HTTP 200** |
| Sitemap | **51 URLs statiques** après ajout des 21 routes Phase 6 |
| Total rapport navigateur Phase 6 | **51/51 contrôles VALIDE** |

Les détails, versions de navigateur et résultats individuels sont conservés dans `data/snapshots/validation-phase-6.json`.

## Contrôles de build et données

- `python3 -m py_compile scripts/site_urls.py scripts/build_home.py scripts/guide_pages.py scripts/map_pages.py scripts/weapon_pages.py scripts/phase6_pages.py scripts/serve_home.py` — OK.
- `node --check js/phase6.js` et `node --check scripts/qa_phase6_browser.cjs` — OK.
- `python3 scripts/tests/test_site_urls.py` — 3 tests réussis : base non confirmée refusée, opt-in explicite testé, hôtes preview/réservés toujours exclus.
- `python3 scripts/phase6_pages.py --check-snapshot` — snapshot conforme aux exports et au manifeste locaux.
- `python3 scripts/build_home.py --check` — **51 routes statiques**, recherche et SEO conformes aux générateurs sur la base d’aperçu courante.
- L’audit des 51 pages trouve zéro `canonical`, `og:url` ou `mainEntityOfPage` d’aperçu; les URLs absolues du sitemap et de `robots.txt` restent celles de l’aperçu et ne doivent pas être soumises à un moteur de recherche.
- Audit global médias : les **2 283 références raster** relevées dans le HTML sont locales, en JPG/JPEG et résolues; les **50 URL d’image uniques** référencées répondent HTTP 200 par le serveur à liste blanche. Le dossier contient **54 images JPG/JPEG** et 11 marqueurs `.gitkeep` non-images. Aucune balise SVG inline, image externe ou référence cassée. L’image `armor-body-plates.jpg` est désormais autorisée et chargée dans la fiche Gilets & plaques.
- Données défensives : **423 IDs dans chacun des trois modes**, mêmes IDs et statistiques de protection concordants au moment de la construction; aucun prix flea n’est assez récent pour le seuil de sept jours.

## Réserves et périmètre

Les HP et détails de boss issus de la wiki restent communautaires et non testés en jeu. La chance de Partisan de 25 % est une chance de base BSG, pas un taux final garanti en PvP/Seasonal. La baisse de santé de The Wedge annoncée par BSG ne donne pas de nouveau total; 750 HP est affiché uniquement comme repère wiki historique incertain. Cultist Priest n’a pas de total HP affiché.

`images/armor/armor-body-plates.jpg` a été régénérée sans texte ni logo visibles et intégrée à `pages/armor/body-armor.html` comme illustration éditoriale générique; la QA Chromium/Firefox a confirmé le chargement et l’absence d’erreur média. La PHASE_5 a aussi été re-testée après la refonte des vignettes et du graphique : **49/49 contrôles** dans `data/snapshots/validation-phase-5.json`. Aucun raid/client EFT ni hébergement public n’a été testé. Le dépôt, le propriétaire Pages et le domaine restent à confirmer (voir `docs/publication-github-pages.md`); le sitemap de l’aperçu ne doit pas être publié.
