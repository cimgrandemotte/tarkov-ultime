# PHASE_8 — Compétences, économie et stratégies

**État : validée localement — 10/10 routes livrées.** Le site compte désormais **77 routes HTML statiques**; recherche et sitemap contiennent chacun les dix nouvelles pages. Ce jalon n’est pas une publication : la base publique, le dépôt, le DNS, le TLS et le routage Pages restent à confirmer.

La date de référence de la relecture éditoriale est le **18 novembre 2026**. L’instantané communautaire du 19 novembre est ultérieur à cette relecture : il reste quarantiné, le générateur ne le lit pas et le serveur d’aperçu ne l’expose pas.

## Routes

### Compétences — une route

- `pages/skills/` — changements confirmés, limites des multiplicateurs et journal d’observations local par mode.

### Économie — trois routes

- `pages/economy/` — hub économie et comparaisons de modes.
- `pages/economy/flea-market.html` — vente au Flea Market, distinctions entre patch, mode et offre courante.
- `pages/economy/money-making.html` — choix de boucles et scénarios de revenu avec hypothèses saisies par le joueur.

### Stratégies — six routes

- `pages/strategy/` — hub et filtre de contexte.
- `pages/strategy/beginner-tips.html` — **61 astuces**, recherche par thème et favoris dans le navigateur.
- `pages/strategy/advanced-tactics.html` — tactiques présentées comme conseils, non comme règles garanties.
- `pages/strategy/pvp-guide.html` — PvP permanent et Seasonal différenciés.
- `pages/strategy/pve-guide.html` — PvE officiel, Prestige et checklist locale par palier.
- `pages/strategy/meta-builds.html` — critères de comparaison, coûts saisis et budget; aucun classement universel d’armes.

## Provenance et réserves éditoriales

Les pages renvoient aux notes BSG et aux sources communautaires correspondantes. Le manifest complet, les identifiants utilisés, les URLs, dates, provenances et réserves sont conservés dans [`sources.json`](sources.json) et [`recherche-tarkov-2026-11-18.md`](recherche-tarkov-2026-11-18.md).

- Les notes BSG **1.1.0.0** décrivent notamment des changements moyens de prix chez les traders et un changement de commission du Flea Market de 3 % à 5 %. Ce texte de patch ne donne ni cours actuel par objet, ni frais effectifs universels; aucune cotation live n’est copiée dans ces pages.
- BSG indique une progression des compétences **jusqu’à** 60 % plus rapide selon les changements annoncés, et non un bonus garanti de 60 % pour chaque action ou compétence. Le patch **1.3.0.0** décrit des changements ciblés de Métabolisme et des skills Seasonal, sans publier leurs coefficients complets.
- Le patch **1.2.0.0** annonce six niveaux de Prestige PvE et un reset du profil PvE; certaines catégories de progression peuvent être conservées jusqu’à 50 %. Les exigences chiffrées de chaque palier ne sont pas inventées : le guide renvoie au client.
- Le journal technique BSG **1.3.5.0** du 18 novembre annonce une fenêtre de planification, pas la preuve d’un déploiement. TarCoin est décrite comme devise de l’Expansions Hub, non comme roubles ou valeur Flea.
- Tarkov.dev et Tarkov Market sont traités comme des outils/agrégateurs communautaires, non comme des API BSG ni comme des cours garantis. La page n’embarque aucun prix trouvé dans le snapshot quarantiné ou sur un graphique volatil.
- L’exemple vidéo de Pestily sur les caisses d’Interchange est explicitement une expérience personnelle — environ 15 raids, sept heures et cinq bitcoins dans le récit — et non un rendement représentatif ou reproductible.

Les tableaux et calculateurs n’ajoutent aucun multiplicateur de compétence, prix prérempli, rendement fixe, taux de réussite ou build « meilleur pour tous ». Les calculs sont des scénarios locaux fondés sur les nombres entrés par l’utilisateur; ils n’interrogent ni le jeu ni un marché en direct. L’illustration du marché, du butin et des équipements est éditoriale et ne constitue pas une source de prix, de statistique ou de compatibilité.

## Intégration et contrôle local

Le générateur raccorde les routes à la navigation, à la recherche locale, au sitemap et à la liste blanche du serveur. Le jeu d’illustrations compte dix JPG génériques de 1376 × 768 px dans `images/phase8/`. Les styles sont dans `css/pages/phase8.css`; les interactions optionnelles et les calculateurs sont dans `js/phase8.js`. Les pages restent lisibles sans JavaScript.

Les commandes et résultats du build, de l’audit statique, des contrôles HTTP et de la QA navigateur sont consignés dans [`verifications-phase-8.md`](verifications-phase-8.md), avec les rapports machine-lisibles `data/snapshots/validation-phase-8-static.json` et `data/snapshots/validation-phase-8.json`.

## Fichiers principaux

- Générateur et validation des sources : `scripts/phase8_pages.py`
- Routes statiques : `pages/skills/`, `pages/economy/`, `pages/strategy/`
- CSS / JavaScript : `css/pages/phase8.css`, `js/phase8.js`
- Build, recherche et sitemap : `scripts/build_home.py`, `js/data/search-index.json`, `sitemap.xml`
- Liste blanche d’aperçu : `scripts/serve_home.py`
- QA : `scripts/qa_phase8_static.py`, `scripts/qa_phase8_browser.cjs`

## Suite du workflow

PHASE_8 est validée localement. La PHASE_9 — SP-Tushonka, Arena et événements — reste en attente d’une confirmation **CONTINUE**. La publication réelle reste séparément bloquée; ne pas promouvoir le sitemap ou les métadonnées de l’aperçu en production avant confirmation du dépôt, du domaine, du DNS, du TLS et du routage.
