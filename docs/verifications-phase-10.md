# Vérifications PHASE_10 — revalidation du 18 novembre 2026

**État : PASS sur le dossier staging statique.** La revalidation intègre le statut officiel vérifié de 1.3.5.0 et la checklist « Upgrade — Prepare 1.3.5.0 avant la mise à jour ». Aucun déploiement, publication distante ni push n’a eu lieu.

## QA du paquet staging

Le paquet a été reconstruit dans `publication-package/site/` et vérifié sans archive :

- **87 routes HTML**, **217 fichiers**;
- inventaire exact, **7 846 références locales** et **1 211 fragments** vérifiés, aucune cible manquante;
- 87 pages `noindex,follow`; aucun canonical ou `og:url` de production;
- aucune `sitemap.xml` ni `robots.txt` dans le staging sans base publique;
- les trois pages PHASE_10, leurs liens sources, la mention Upgrade et le statut « prévu / installation non confirmée » sont validés;
- `publication-package.zip` absent; rapport `archiveGenerated: false`.

## QA navigateur du staging

`node scripts/qa_phase10_browser.cjs` servi localement depuis le dossier staging : **PASS** — 3 routes, 3 groupes d’interactions, 15 vérifications responsive aux largeurs 320, 390, 768, 1280 et 1440 px, 3 audits axe-core sans violation et parcours sans JavaScript réussi.

- Chronologie : le filtre 2026/annonce affiche une entrée; remise à zéro : 20 entrées.
- Ressources : filtres et recherche passent de 17 ressources à 2 puis 1; remise à zéro : 17.
- Glossaire : 314 entrées, recherche, thème, index alphabétique et clavier validés; sans JavaScript, les 314 entrées restent visibles.

Rapports : `data/snapshots/validation-publication.json` et `data/snapshots/validation-phase-10.json`.

## Statut officiel vérifié

Le journal développeur BSG du **18 novembre** a été récupéré directement; il prévoit 1.3.5.0 pour la **seconde moitié de novembre**, sans jour précis ni avis d’installation dans l’article. L’index officiel des patch notes récupéré directement affiche encore **1.3.0.0 du 29 octobre** comme dernière note numérotée. Le miroir officiel Steam affiche le journal du 18/11; ce n’est pas un avis de maintenance ou d’installation. Aucune lecture du Launcher ou du client n’a été faite : le guide ne prétend donc pas connaître le build installé chez chaque joueur.

Les sources et limites sont mises à jour dans `docs/sources.json`, `docs/recherche-phase-10.md` et `docs/recherche-tarkov-2026-11-18.md`. Les discussions, wikis, vidéos et outils communautaires demeurent séparés des annonces officielles.
