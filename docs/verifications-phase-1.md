# Phase 1 · Relevé préalable à l’atelier

**Sondage du 18 novembre 2026, vers 13 h 36 à Paris (12 h 36 UTC).** Ce complément ne remplace ni le [journal de cadrage](verifications-2026-11-18.md) ni l’export de données effectué en phase 0. Il sert à dater le badge du banc d’essai. Aucune nouvelle page éditoriale n’a été publiée.

| Source relue | Constat au relevé |
|---|---|
| [Flux Steam des annonces de Battlestate Games](https://store.steampowered.com/feeds/news/app/3932890/?l=english) | En tête, l’annonce *Tarkov City Drops* du 16 novembre (15:08:57 UTC). La [note 1.3.0.0](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), datée du 29 octobre, reste le patch numéroté le plus récent repéré dans ce flux. Le texte y annonce 1.3.5.0 pour la migration Unity 6 ; il ne dit pas que la migration a eu lieu. |
| [Canal EN public de Battlestate Games](https://t.me/s/escapefromtarkovEN) | Dernière entrée visible datée du 18 novembre à 11:07:12 UTC, à propos de Terminal. Aucun message de déploiement 1.3.5.0 trouvé dans la vue consultée. Les hotfixes et annonces sans nouveau numéro ne sont pas assimilés à des sorties de patch. |
| [Exports JSON Tarkov.dev](https://json.tarkov.dev/endpoints) | Documentation des trois segments `regular`, `pve`, `pvp-season` toujours accessible. Pas de réimport ni de changement de date de collecte des catalogues. |
| [Tarkov.dev, ticket #481](https://github.com/the-hideout/tarkov-api/issues/481) | Ticket clos le 17 novembre. La réponse du mainteneur distingue un objet `gun` de base d’un `preset` vendu monté. L’atelier ne déduit donc pas de prix ou d’offre de trader à partir des seules entrées de base. |
| [Release stable Tushonka — API](https://api.github.com/repos/SP-Tushonka/build/releases/latest) · [Release Fika Plugin — API](https://api.github.com/repos/project-fika/Fika-Plugin/releases/latest) | Les réponses indiquent respectivement `4.1.6` et `v2.4.6`. Pas de nouvelle vérification de compatibilité ni de réinterprétation de 5.0 Bleeding Edge. |

Des recherches complémentaires ont porté sur X, Reddit, YouTube et un ancien fil du forum EFT. Les vues communautaires ne fournissaient pas de preuve de sortie de 1.3.5.0 ; certains résultats étaient hors date, et des vidéos ont été repérées sans visionnage intégral. Les discussions Discord non publiques ne sont pas utilisées pour établir l’état du jeu.

## Références de mise en œuvre

- [WAI-ARIA APG : modales](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) et [navigation à disclosures](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/examples/disclosure-navigation/) : inertie, focus initial et retour, navigation HTML sans rôles `menu` inutiles.
- [WCAG 2.1, raccourcis caractère seul](https://www.w3.org/WAI/WCAG21/Understanding/character-key-shortcuts.html) et [contraste non textuel](https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html) : recherche sur Ctrl/⌘+K, contraste des contours et des indicateurs d’état.
- [Fuse.js, recherche approximative](https://www.fusejs.io/fuzzy-search.html) : pondération, tolérance aux coquilles et normalisation des accents. Howler, AOS, versions et licences dans `vendor/manifest.json`.

**À revalider avant l’accueil :** note de patch effectivement déployée, échéances et modes des événements, chiffres propres à chaque mode, distinction entre annonces et sorties. Pour chaque future fiche, appliquer le contrôle par sujet du [plan éditorial](plan-editorial.md).
