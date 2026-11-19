# Vérification du paquet de publication

**Contrôle local final : 18 novembre 2026 (Europe/Paris). Aucun déploiement, publication distante ni push.** Le paquet conservé est un dossier staging uniquement; aucune archive ZIP n’a été créée, même temporairement.

## Résultat final

- **87 routes HTML** et **217 fichiers de site** reconstruits dans `publication-package/site/`.
- QA du dossier statique : **PASS** — inventaire exact, **7 846 références locales** et **1 211 fragments** contrôlés; aucune cible locale manquante.
- Chaque route staging porte `noindex,follow`. Aucun canonical, `og:url`, `mainEntityOfPage`, URL d’image sociale liée à un hôte public, `robots.txt` ou `sitemap.xml` n’est inclus sans base publique confirmée.
- Les trois pages PHASE_10 et leurs sources sont liées et vérifiées. La mention « Upgrade — Prepare 1.3.5.0 avant la mise à jour » figure sur l’accueil et la page Notes de patch; sa checklist est explicitement présentée comme conseil pratique, pas comme prérequis BSG.
- **Aucune archive ZIP** : `publication-package.zip` est absent. Le rapport machine indique `archiveGenerated: false` et `archivePresent: false`.
- **1.3.5.0 reste annoncée, pas confirmée installée au relevé du 18 novembre.** L’article BSG du 18/11 prévoit la seconde moitié de novembre, sans jour précis ni annonce d’installation. L’index des notes BSG récupéré directement affiche 1.3.0.0 (29/10) en dernière note numérotée; cela ne prouve pas le build présent sur le client de chaque joueur. La préparation recommandée est prudente et ne prétend pas être une consigne officielle.

## Contrôles exécutés

| Contrôle | Résultat |
|---|---|
| `python3 scripts/prepare_publication.py --mode staging` | PASS — 87 routes, 217 fichiers; dossier seul, sans ZIP |
| `python3 scripts/qa_publication.py --mode staging` | **PASS** — inventaire, métadonnées staging, liens/fragments, sources, mention Upgrade et absence de ZIP |
| `python3 scripts/phase10_pages.py --check` | PASS — 3 routes, 314 termes bilingues, 6 JPG |
| `python3 -m py_compile scripts/*.py scripts/tests/*.py` | PASS |
| `python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v` | PASS — 3/3 tests |
| `node --check` sur les fichiers `.js`, `.mjs` et `.cjs` sous `js/` et `scripts/` | PASS |
| QA navigateur `scripts/qa_phase10_browser.cjs` servi depuis le dossier staging | PASS — 3 routes, 3 groupes d’interactions, 15 contrôles responsive, 3 audits axe-core, parcours sans JavaScript réussi |

### Rapports machine

- QA du paquet : `data/snapshots/validation-publication.json` — `PASS`, 87 routes, 217 fichiers, 7 846 références locales, 1 211 fragments, `archiveGenerated: false`, `archivePresent: false`.
- QA navigateur PHASE_10 : `data/snapshots/validation-phase-10.json`.

## Vérification des informations de mise à jour

Le journal officiel [BSG du 18 novembre](https://www.escapefromtarkov.com/news/id/420?lang=en) et son relais [Steam](https://steamcommunity.com/games/3932890/announcements/detail/719048067771269207) ont été récupérés directement; l’[index officiel des patch notes](https://www.escapefromtarkov.com/news?type=2) a aussi été contrôlé directement. Le journal prévoit 1.3.5.0 pour la seconde moitié de novembre, sans jour exact et sans avis d’installation. Unity 6 et les améliorations techniques indiquées dans le journal sont distingués des travaux futurs (DirectX 12, DLSS Frame Generation x2/x4, NVIDIA Reflex, végétation reportée; FSR 4 visé avant fin 2026). Aucune lecture du Launcher ou du client n’a été faite; le guide ne conclut donc pas que le patch est présent ou absent sur chaque installation.

Les détails, réserves et références communautaires sont consignés dans `docs/recherche-tarkov-2026-11-18.md`, `docs/recherche-phase-10.md` et `docs/sources.json`. Les conseils d’autres joueurs, wikis, forums, vidéos et outils restent identifiés comme communautaires et ne sont pas utilisés pour confirmer un déploiement BSG.

## Publication manuelle — reste à faire par l’utilisateur

Le site reste volontairement en `noindex` : la destination de publication n’est pas connue. Aucun dépôt Git distant, propriétaire Pages, domaine final, DNS ou workflow n’a été configuré. Le domaine précédemment testé, `gta6guide.duckdns.org`, ne répondait pas comme un site Pages valide et avait un problème TLS; il n’est pas utilisé comme base.

Le dossier transférable est `publication-package/site/`. La génération et le QA ne publient, ne déploient ni ne poussent rien. Après avoir vous-même choisi et configuré une URL HTTPS valide, la construction SEO publique peut être préparée avec `scripts/prepare_publication.py --mode public --base-url 'https://URL-CONFIRMEE/' --confirm-public-base`, puis auditée avec `scripts/qa_publication.py --mode public --base-url 'https://URL-CONFIRMEE/'`. Ces commandes travaillent elles aussi sur un dossier et ne génèrent aucune archive.
