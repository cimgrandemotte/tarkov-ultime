# Vérifications PHASE_8 — Compétences, économie et stratégies

**Résultat final : PASS.** Génération, intégration, liens, contrôles HTTP, interactions, repli sans JavaScript, accessibilité automatisée et responsive sont validés en local. Aucun déploiement n’a été effectué.

## Résultats

| Contrôle | Résultat |
|---|---|
| Validation des sources | 10 routes; 61 astuces; instantané du 19/11 quarantiné |
| Build statique | 77 routes; `build_home.py --check` sans artefact à régénérer |
| Recherche et sitemap | 1 294 enregistrements de recherche; 77 URLs uniques; les 10 routes PHASE_8 sont présentes dans chacun |
| Audit statique PHASE_8 | 10 pages; 624 liens, ressources et fragments locaux résolus; aucune ID dupliquée ou image sans texte alternatif |
| Workflow et inventaire | 77/87 pages prévues présentes; PHASE_8 10/10; 10 JPG et empreintes cohérentes |
| Illustrations | 10 JPG attendues, présentes et référencées par les pages |
| Liste blanche HTTP | 25 ressources publiques testées en HTTP 200; 6 chemins privés/quarantinés testés en HTTP 404 |
| Rendus navigateur | 20 rendus : dix routes dans Chromium et dix dans Firefox; titres, H1, médias, scripts et erreurs contrôlés |
| axe-core | Dix audits Chromium; zéro violation détectée |
| Responsive | Dix routes testées à 375, 768 et 1440 px; aucun débordement horizontal |
| JavaScript désactivé | Sept routes représentatives; contenu principal, navigation et tableaux/listes restent lisibles |
| Contrôles groupés navigateur | **48/48 PASS**; recherche, filtres, calculatrices, journal, favoris, modes et checklist testés |

Les calculateurs ont été testés avec des nombres contrôlés uniquement pour valider leur arithmétique. Ces valeurs d’essai ne sont pas des données ou prix du jeu. Le navigateur confirme notamment l’absence de préremplissage du prix ou du taux de commission Flea.

### Contrôle transversal hors gate PHASE_8

`python3 scripts/check_phase0.py` a aussi été essayé, mais ne passe pas : il signale que les 14 entrées PHASE_4 de cartes ne déclarent qu’une illustration chacune, alors que cette ancienne validation exige au moins deux illustrations spécifiées par page. C’est une incohérence de l’inventaire éditorial hérité, pas un défaut du build ni des dix pages PHASE_8; elle n’a pas été masquée ni modifiée dans le cadre de ce jalon. Les vérifications PHASE_8 et la synchronisation de son workflow passent.

## Quarantaine et aperçu

- Le générateur `scripts/phase8_pages.py` valide les enregistrements sources; il ne lit pas `data/snapshots/phase-8-reference-2026-11-19.json`.
- Le snapshot du 19 novembre ne figure ni dans les pages produites, ni dans l’index de recherche, ni dans le sitemap. Les cours tirés de cet instantané n’ont pas été publiés.
- Le serveur de prévisualisation répond 404 pour le snapshot, le manifest privé, les scripts internes, les rapports QA et un chemin de traversal essayé.
- La base utilisée pour les métadonnées de build et le sitemap est un hôte temporaire d’aperçu. Les pages d’aperçu n’émettent pas de canonical public; le sitemap et `robots.txt` de cet hôte ne doivent pas être soumis ou déployés comme production.

## Commandes de reproduction

Depuis la racine `tarkov-ultimate-guide` :

```sh
python3 -m py_compile scripts/phase8_pages.py scripts/build_home.py scripts/serve_home.py scripts/qa_phase8_static.py
python3 scripts/phase8_pages.py
python3 scripts/build_home.py --base-url "$PREVIEW_BASE_URL"
python3 scripts/build_home.py --check --base-url "$PREVIEW_BASE_URL"
python3 scripts/serve_home.py --host 0.0.0.0 --port 4180
```

Avec le serveur actif dans un autre processus :

```sh
PHASE8_BASE_URL=http://127.0.0.1:4180 python3 scripts/qa_phase8_static.py
PHASE8_BASE_URL=http://127.0.0.1:4180 node scripts/qa_phase8_browser.cjs
```

Rapports générés :

- `data/snapshots/validation-phase-8-static.json`
- `data/snapshots/validation-phase-8.json`

La QA valide un build d’aperçu seulement; elle n’atteste ni DNS, ni TLS, ni la configuration GitHub Pages. La publication nécessite une base de production confirmée et une reconstruction propre avant tout envoi en ligne.
