# PHASE_9 — SP-Tushonka, Arena et événements

**État : validée localement — 7/7 routes livrées.** Le site passe à **84 routes HTML statiques**; les sept nouvelles pages sont intégrées au menu, à la recherche, au sitemap et à la liste blanche de l’aperçu. Cette validation ne constitue pas une publication.

La date de relecture éditoriale est le **18 novembre 2026** (Europe/Paris). Les pages d’aperçu portent `noindex,follow` et n’émettent pas de canonical ni d’URL Open Graph publique.

## Routes livrées

### SP-Tushonka — cinq routes

- `pages/spt-tushonka/` — distinguer le PvE officiel, la stable communautaire SPT, Bleeding Edge et Project Fika.
- `pages/spt-tushonka/installation.html` — installer une copie séparée et légitime; versions SPT 4.1.6, EFT 0.16.9.5.40743 et installateur 3.0.0.0 clairement différenciés.
- `pages/spt-tushonka/mods.html` — filtre branche × catégorie; dépendances SAIN, réserve sur la compatibilité Fika et avertissements pour SVM et le backport Icebreaker.
- `pages/spt-tushonka/fika.html` — plugin client et serveur C# traités comme composants distincts, alignement de versions, sessions privées et limites réseau.
- `pages/spt-tushonka/troubleshooting.html` — filtre par symptôme, sauvegarde des profils et diagnostic Linux/Proton présenté comme un signalement isolé, non comme une panne générale.

### Jeux et actualités — deux routes

- `pages/arena/` — onglets clavier pour BlastGang, TeamFight, CheckPoint et Last Hero; économie par manche, passerelles de progression nuancées et notes Arena distinctes d’EFT principal.
- `pages/events/` — dix repères filtrables : actifs, annoncés, archivés ou durables. Les échéances inconnues le restent; événement temporaire, campagne Twitch et contenu permanent ne sont pas confondus.

## Repères éditoriaux

- La stable SPT consultée est la **4.1.6 (40743)**, ciblant **EFT 0.16.9.5.40743**. Bleeding Edge 5.0 est réservé aux tests, non pris en charge; aucun fichier du jeu n’est redistribué.
- Project Fika est communautaire et distinct de la coopération officielle PvE. Le plugin **2.4.6** et le serveur C# **2.4.2** sont des releases séparées; les versions doivent être revérifiées ensemble. Les groupes de confiance sont préférés et les serveurs publics déconseillés.
- Les fiches The Forge sont des déclarations de mainteneurs, pas une garantie globale. SAIN 4.5.1 indique les dépendances Waypoints 1.9.0 et BigBrain 1.5.0; The Forge ne marque pas leur compatibilité Fika comme confirmée. SVM 2.2.3 recommande un nouveau profil; Icebreaker 1.2.4 est un backport fan-made et demande un addon de synchronisation Fika sur chaque nœud en coop.
- Arena reste distinct d’EFT principal. Le patch Arena 0.6.2.5 du 5 novembre 2026 est la dernière note numérotée retrouvée au relevé; une roadmap Q4 préliminaire n’est pas présentée comme un calendrier ferme.
- Au relevé du 18 novembre : Halloween était encore en cours, sa fin annoncée seulement « la semaine prochaine »; City Drops allait jusqu’au 23 novembre à 15:00 UTC (16:00 à Paris); Kord Breach avait une fin annoncée au 7 décembre sans heure. BloodLust était clos le 5 novembre. Blackout est archivé, mais sa date finale exacte n’est pas établie par les annonces BSG consultées. Icebreaker/Boreas est classé comme contenu durable parce que la note consultée ne publie pas d’échéance de retrait; l’accès actuel doit être vérifié dans le client.

Le registre `docs/sources.json` contient **250 sources**, dont **47 clés utilisées** par les sept pages. Les règles BSG, la documentation de projets, les fiches communautaires et les témoignages sont séparés; les limites de vérification sont indiquées près du contenu et dans le registre.

## Médias

Sept illustrations éditoriales originales sont intégrées depuis `images/phase9/`. Elles sont en JPG RGB **1376 × 768 px**, avec texte alternatif; leurs tailles et empreintes SHA-256 figurent dans `data/snapshots/validation-phase-9-static.json` et `workflow.json`. Elles ne sont ni des captures du jeu, ni des preuves de mécanique, de prix ou de compatibilité.

## Intégration et QA

Les générateurs et interactions sont `scripts/phase9_pages.py`, `css/pages/phase9.css` et `js/phase9.js`. `scripts/build_home.py` raccorde les routes à la recherche et au sitemap; `scripts/serve_home.py` ne sert les nouvelles pages et ressources que par liste blanche explicite. Le contenu principal reste disponible sans JavaScript.

Les contrôles locaux sont consignés dans [`verifications-phase-9.md`](verifications-phase-9.md), avec les rapports `data/snapshots/validation-phase-9-static.json` et `data/snapshots/validation-phase-9.json`.

## Publication

Aucun déploiement ni transfert en production n’a eu lieu. Le domaine public, le propriétaire/dépôt, le DNS, le TLS et le routage GitHub Pages restent à confirmer. Ne pas soumettre le sitemap d’aperçu ni retirer le `noindex` avant cette vérification.

La PHASE_9 est terminée localement. La PHASE_10 — patchs, ressources, glossaire et audit final — attend la confirmation **CONTINUE**. La publication reste un contrôle séparé.
