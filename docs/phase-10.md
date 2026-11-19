# PHASE_10 — Notes de patch, ressources et glossaire

**État : livrée et validée localement le 18 novembre 2026.** Aucune publication ni aucun déploiement n’a été effectué ou autorisé.

## Livrables

- `pages/patch-notes.html` — chronologie sourcée des notes et annonces EFT. Elle distingue les notes BSG, dates d’installation, messages sans numéro, versions communautaires rapportées et éléments annoncés mais non confirmés déployés.
- `pages/resources/index.html` — 17 ressources présentées par usage et type de source, avec réserves sur la fraîcheur, la sécurité, les licences et l’absence d’affiliation.
- `pages/resources/glossary.html` — 314 termes anglais–français, répartis en six groupes, avec recherche sans accents, index alphabétique et filtre par thème.
- Six illustrations JPG originales dans `images/phase10/`.
- Navigation, pied de page, recherche, sitemap, générateur, CSS/JS et liste blanche de l’aperçu mis à jour. Trois liens d’ancre préexistants dans des dossiers PHASE_6/7 ont aussi été corrigés après l’audit de liens du site.
- Registre de sources datées mis à jour : 272 entrées.

## État documentaire conservé

Au relevé du 18 novembre 2026, l’index BSG consulté liste 1.3.0.0 comme dernière note numérotée. Le message BSG du 13 novembre confirme une mise à jour technique sans numéro; les sous-builds consignés par le wiki restent communautaires. 1.3.5.0 est annoncée pour la seconde moitié de novembre, sans confirmation de son installation au moment de la revue. Les détails de 1.0.4.9 n’ont pas été récupérés et ne sont pas extrapolés.

Les outils, bases, wikis, forums et retours de joueurs sont étiquetés comme communautaires. Le wiki Fandom est présenté comme un projet de bénévoles avec licence CC BY-NC-SA sauf exception propre à une page ou un fichier. Aucun texte, carte ou asset tiers n’est reproduit.

## Validation

Les résultats reproductibles figurent dans `docs/verifications-phase-10.md` et dans :

- `data/snapshots/validation-phase-10-static.json`
- `data/snapshots/validation-phase-10.json`

Le site reste un aperçu local/non canonique. Le domaine, le DNS, le TLS et l’hébergement réel n’ont pas été confirmés; aucun artifact de publication n’a été produit.
