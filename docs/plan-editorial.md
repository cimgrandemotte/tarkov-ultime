# Plan éditorial · Tarkov Ultimate Guide

87 routes HTML distinctes sont planifiées. **67 routes sont livrées localement dans les phases 2 à 7** (16 routes PHASE_7 incluses); 20 restent planifiées en PHASE_8–10. La QA PHASE_7 passe **46 contrôles groupés**, 32 rendus Chromium/Firefox et 16 audits axe-core sans violation (`docs/verifications-phase-7.md`). La publication publique reste bloquée par l’accès au dépôt et la configuration du domaine.

Les pages reçoivent des sources datées, un mode explicite quand il est pertinent et un fil d’Ariane. Les images sont des JPG locaux; les vignettes génériques PHASE_5 et les illustrations de protection sont clairement distinguées des objets/stats exacts. Les graphiques et schémas sont en HTML/CSS, sans SVG ni PNG générés. Les liens pointent vers des sources, pas vers des pages encore vides.

| Phase | Dossier | Pages |
|---|---|---:|
| 2 | Accueil et navigation | 1 |
| 3 | Guide du débutant et lore | 2 |
| 4 | Cartes | 14 |
| 5 | Armes et munitions | 13 |
| 6 | Armures et boss | 21 |
| 7 | Traders, quêtes et planque | 16 |
| 8 | Compétences, économie et stratégies | 10 |
| 9 | SP-Tushonka, Arena et événements | 7 |
| 10 | Patchs, ressources, glossaire et finalisation | 3 |

## Phase 2 — Accueil et navigation

### Tarkov Ultimate Guide

`index.html` · **Livrée** ([bilan de phase](phase-2.md)) · Faire trouver une réponse en deux clics, que l’on débute ou que l’on revienne après un patch.

**Sections :** Hero cinématique et appels « Premier raid » / « Cartes » · Cartes illustrées vers les grands dossiers · Compteurs tirés des catalogues publiés · Dernier patch, actualités confirmées, guides en vedette et avertissement fan-site.

**Interaction :** Méga-menu accessible, recherche au clavier avec Ctrl/K, ambiance volontaire et effets compatibles reduced-motion.

**JPG envisagés :** PMC et rues de Tarkov sous la pluie (hero 16:9) · Panorama aérien urbain · Arsenal en jeu sur établi · Silhouette de boss dans la brume.

**Vérification :** Contrôler les annonces du jour ; n’afficher comme navigables que les pages effectivement livrées.

**Sources cibles :** [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [steam-news](https://steamcommunity.com/app/3932890/announcements/), [bsg-social](https://t.me/s/escapefromtarkovEN), [tdev](https://json.tarkov.dev/endpoints), [spt-release](https://github.com/SP-Tushonka/build/releases/tag/4.1.6).


## Phase 3 — Guide du débutant et lore

### Guide du débutant

`pages/getting-started.html` · **Livrée** ([bilan de phase](phase-3.md)) · Préparer et réussir son premier raid sans supposer que le lecteur connaît le jeu.

**Sections :** Modes, USEC/BEAR et tutoriel · Pré-raid, raid, extraction, bilan et stash · Santé du PMC, saignements et soins dans l’interface du jeu · Réglages et raccourcis, avec alternatives de touches · Survie en 10 étapes, checklist et FAQ de 20+ questions.

**Interaction :** Checklist locale, sommaire à ancres, FAQ en accordéons et onglets PMC/Scav.

**JPG envisagés :** Maquette HUD annotée (pas une capture officielle) · PMC et équipement dans la planque · Schéma santé du personnage.

**Vérification :** Recouper contrôles et état Survived avec le wiki et le client ; tester la progression du tutoriel selon le mode.

**Sources cibles :** [steam](https://store.steampowered.com/app/3932890/Escape_from_Tarkov/), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [yt-beginner](https://www.youtube.com/watch?v=P5hyxI-cbb4), [reddit-eft](https://www.reddit.com/r/EscapefromTarkov/).

### Lore & univers de Tarkov

`pages/lore/index.html` · **Livrée** ([bilan de phase](phase-3.md)) · Situer la région fictive, les factions et les chapitres sans divulgâcher par défaut.

**Sections :** Norvinsk et son enclave · TerraGroup, USEC, BEAR, Scavs et autres factions · Chronologie des Contract Wars au récit de la 1.0 · Liens entre lieux et chapitres ; spoiler protégé.

**Interaction :** Chronologie, fiches de factions et dévoilement explicite des spoilers.

**JPG envisagés :** Tarkov et la baie au crépuscule · Dossier cartographique de Norvinsk fictif.

**Vérification :** Séparer texte canonique, allusions et interprétations ; vérifier les noms des chapitres.

**Sources cibles :** [steam](https://store.steampowered.com/app/3932890/Escape_from_Tarkov/), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [terminal](https://t.me/s/escapefromtarkovEN/7001), [patch105](https://steamcommunity.com/games/3932890/announcements/detail/703268976281519055), [yt-dev](https://youtu.be/w8ro-u_H8-8).


## Phase 4 — Cartes · **Livrée** ([bilan de phase](phase-4.md))

**14 routes publiées dans ce dossier :** le hub canonique et treize fiches. Les variantes restent distinctes des 13 lieux principaux ; les schémas sont illustratifs et non à l’échelle.

### Cartes de Tarkov

`pages/maps/index.html` · **Livrée** ([bilan de phase](phase-4.md)) · Choisir un emplacement compatible avec son niveau, sa quête et son mode de jeu.

**Sections :** Treize emplacements principaux, variantes et zones d’événement distinctes · Durée, joueurs, difficulté éditoriale, boss et accès · Tableau des transitions et du risque en jeu · Renvois vers guides et quêtes.

**Interaction :** Filtre difficulté/mode, comparaison de deux cartes, légende d’accès et tableau de secours.

**JPG livré :** `images/maps/norvinsk-overlook.jpg` (panorama de PHASE_2 réutilisé).

**Vérification :** Valider présence, accès effectif, date et mode ; aucun compteur basé sur les seuls enregistrements API.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-maps](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov), [mapgenie](https://mapgenie.io/tarkov), [patch115](https://steamcommunity.com/games/3932890/announcements/detail/712285688032135503), [patch120](https://store.steampowered.com/news/app/3932890/view/708910525152495848), [terminal](https://t.me/s/escapefromtarkovEN/7001).

### Factory

`pages/maps/factory.html` · **Livrée** ([bilan de phase](phase-4.md)) · Usine, échelle compacte et différences jour/nuit.

**Sections :** Contexte et accès : mode, durée, joueurs et restrictions · Bureaux, escaliers, sorties conditionnelles et scène Tagilla. · Extractions PMC/Scav, transits et conditions ; liste alternative à la carte · Apparitions en jeu et boss (mode, date, déclencheur), dangers et points de vue · Clés, loot et routes de quêtes par niveau ; conseils PvP/PvE propres à ce terrain.

**Interaction :** Carte filtrable avec navigation clavier et listes par type ; onglets de mode ; liens de quête et de boss.

**JPG livré :** `images/maps/factory.jpg` (illustration d’ambiance, pas un plan navigable).

**Vérification :** Relever les variantes jour/nuit, clés de sortie, événements et statistiques par variante.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-maps](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov), [mapgenie](https://mapgenie.io/tarkov), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [halloween](https://x.com/tarkov/status/2122283819667464473).

### Customs

`pages/maps/customs.html` · **Livrée** ([bilan de phase](phase-4.md)) · Carte des premières quêtes et traversées entre douanes, dortoirs et entrepôts.

**Sections :** Contexte et accès : mode, durée, joueurs et restrictions · Dortoirs, Reshala, transits et secteurs revus en 1.2. · Extractions PMC/Scav, transits et conditions ; liste alternative à la carte · Apparitions en jeu et boss (mode, date, déclencheur), dangers et points de vue · Clés, loot et routes de quêtes par niveau ; conseils PvP/PvE propres à ce terrain.

**Interaction :** Carte filtrable avec navigation clavier et listes par type ; onglets de mode ; liens de quête et de boss.

**JPG livré :** `images/maps/customs.jpg` (illustration d’ambiance, pas un plan navigable).

**Vérification :** Vérifier les changements d’extractions et de loot de 1.2.0.0 et les quêtes d’introduction.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-maps](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov), [mapgenie](https://mapgenie.io/tarkov), [patch120](https://store.steampowered.com/news/app/3932890/view/708910525152495848), [tracker](https://tarkovtracker.io), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses).

### Woods

`pages/maps/woods.html` · **Livrée** ([bilan de phase](phase-4.md)) · S’orienter dans les bois et repérer le bord jouable.

**Sections :** Contexte et accès : mode, durée, joueurs et restrictions · Scierie, points hauts en jeu, caches, Shturman et chemin vers les tâches Jaeger. · Extractions PMC/Scav, transits et conditions ; liste alternative à la carte · Apparitions en jeu et boss (mode, date, déclencheur), dangers et points de vue · Clés, loot et routes de quêtes par niveau ; conseils PvP/PvE propres à ce terrain.

**Interaction :** Carte filtrable avec navigation clavier et listes par type ; onglets de mode ; liens de quête et de boss.

**JPG livré :** `images/maps/woods.jpg` (illustration d’ambiance, pas un plan navigable).

**Vérification :** Comparer les couches dangers, marqueurs et positions de la quête d’accès à Jaeger.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-maps](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov), [mapgenie](https://mapgenie.io/tarkov), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [tracker](https://tarkovtracker.io).

### Shoreline

`pages/maps/shoreline.html` · **Livrée** ([bilan de phase](phase-4.md)) · Le Resort, la côte et les transitions d’histoire.

**Sections :** Contexte et accès : mode, durée, joueurs et restrictions · Ailes du Resort, Sanitar, clés et bifurcations vers le Labyrinth, Terminal et Icebreaker. · Extractions PMC/Scav, transits et conditions ; liste alternative à la carte · Apparitions en jeu et boss (mode, date, déclencheur), dangers et points de vue · Clés, loot et routes de quêtes par niveau ; conseils PvP/PvE propres à ce terrain.

**Interaction :** Carte filtrable avec navigation clavier et listes par type ; onglets de mode ; liens de quête et de boss.

**JPG livré :** `images/maps/shoreline.jpg` (illustration d’ambiance, pas un plan navigable).

**Vérification :** Vérifier les règles de transit et les corrections d’accès, et distinguer les loot rooms par aile.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-maps](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov), [mapgenie](https://mapgenie.io/tarkov), [patch105](https://steamcommunity.com/games/3932890/announcements/detail/703268976281519055), [patch115](https://steamcommunity.com/games/3932890/announcements/detail/712285688032135503), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [terminal](https://t.me/s/escapefromtarkovEN/7001).

### Interchange

`pages/maps/interchange.html` · **Livrée** ([bilan de phase](phase-4.md)) · Naviguer dans ULTRA, ses magasins et ses parkings.

**Sections :** Contexte et accès : mode, durée, joueurs et restrictions · Électricité, magasins Tech, étages et périmètre de Killa en jeu. · Extractions PMC/Scav, transits et conditions ; liste alternative à la carte · Apparitions en jeu et boss (mode, date, déclencheur), dangers et points de vue · Clés, loot et routes de quêtes par niveau ; conseils PvP/PvE propres à ce terrain.

**Interaction :** Carte filtrable avec navigation clavier et listes par type ; onglets de mode ; liens de quête et de boss.

**JPG livré :** `images/maps/interchange.jpg` (illustration d’ambiance, pas un plan navigable).

**Vérification :** Reprendre les modifications de loot et de géométrie puis distinguer les variantes de boss.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-maps](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov), [mapgenie](https://mapgenie.io/tarkov), [patch120](https://store.steampowered.com/news/app/3932890/view/708910525152495848), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses).

### Reserve

`pages/maps/reserve.html` · **Livrée** ([bilan de phase](phase-4.md)) · Lier les bâtiments de la base militaire aux bunkers.

**Sections :** Contexte et accès : mode, durée, joueurs et restrictions · Souterrains, hermétique, train, défis d’extractions et fiches Glukhar/Raiders. · Extractions PMC/Scav, transits et conditions ; liste alternative à la carte · Apparitions en jeu et boss (mode, date, déclencheur), dangers et points de vue · Clés, loot et routes de quêtes par niveau ; conseils PvP/PvE propres à ce terrain.

**Interaction :** Carte filtrable avec navigation clavier et listes par type ; onglets de mode ; liens de quête et de boss.

**JPG livré :** `images/maps/reserve.jpg` (illustration d’ambiance, pas un plan navigable).

**Vérification :** Confirmer les déclencheurs, les limites PMC/Scav et les prérequis conditionnels.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-maps](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov), [mapgenie](https://mapgenie.io/tarkov), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [tracker](https://tarkovtracker.io).

### The Lab

`pages/maps/the-lab.html` · **Livrée** ([bilan de phase](phase-4.md)) · Séparer les accès du laboratoire permanent et ceux de ses variantes.

**Sections :** Contexte et accès : mode, durée, joueurs et restrictions · Keycards, sorties conditionnelles, Raiders, archives The Lab (Dark) et renvoi Infected Lab. · Extractions PMC/Scav, transits et conditions ; liste alternative à la carte · Apparitions en jeu et boss (mode, date, déclencheur), dangers et points de vue · Clés, loot et routes de quêtes par niveau ; conseils PvP/PvE propres à ce terrain.

**Interaction :** Carte filtrable avec navigation clavier et listes par type ; onglets de mode ; liens de quête et de boss.

**JPG livré :** `images/maps/the-lab.jpg` (illustration d’ambiance, pas un plan navigable).

**Vérification :** Vérifier assurance et accès par mode, séparer Blackout et Halloween des spawns permanents.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-maps](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov), [mapgenie](https://mapgenie.io/tarkov), [halloween](https://x.com/tarkov/status/2122283819667464473), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875).

### Lighthouse

`pages/maps/lighthouse.html` · **Livrée** ([bilan de phase](phase-4.md)) · Reprendre les itinéraires de la carte réorganisée en 1.1.5.0.

**Sections :** Contexte et accès : mode, durée, joueurs et restrictions · Chalets Rogues, Water Treatment, BTR, tunnels, péninsule et Icebreaker. · Extractions PMC/Scav, transits et conditions ; liste alternative à la carte · Apparitions en jeu et boss (mode, date, déclencheur), dangers et points de vue · Clés, loot et routes de quêtes par niveau ; conseils PvP/PvE propres à ce terrain.

**Interaction :** Carte filtrable avec navigation clavier et listes par type ; onglets de mode ; liens de quête et de boss.

**JPG livré :** `images/maps/lighthouse.jpg` (illustration d’ambiance, pas un plan navigable).

**Vérification :** Contrôler bornes jouables et danger résiduel, règles USEC/BEAR et accès Lightkeeper.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-maps](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov), [mapgenie](https://mapgenie.io/tarkov), [patch115](https://steamcommunity.com/games/3932890/announcements/detail/712285688032135503), [patch120](https://store.steampowered.com/news/app/3932890/view/708910525152495848), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses).

### Streets of Tarkov

`pages/maps/streets-of-tarkov.html` · **Livrée** ([bilan de phase](phase-4.md)) · Lire les quartiers et bâtiments d’une grande carte urbaine.

**Sections :** Contexte et accès : mode, durée, joueurs et restrictions · LexOs, zones de Kollontay, clés, repères de quartiers et itinéraires de quêtes. · Extractions PMC/Scav, transits et conditions ; liste alternative à la carte · Apparitions en jeu et boss (mode, date, déclencheur), dangers et points de vue · Clés, loot et routes de quêtes par niveau ; conseils PvP/PvE propres à ce terrain.

**Interaction :** Carte filtrable avec navigation clavier et listes par type ; onglets de mode ; liens de quête et de boss.

**JPG livré :** `images/maps/norvinsk-overlook.jpg` (panorama de PHASE_2 réutilisé).

**Vérification :** Vérifier les sorties et changements de spawn ; éviter les vieilles cartes de quartiers.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-maps](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov), [mapgenie](https://mapgenie.io/tarkov), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [tracker](https://tarkovtracker.io), [tarkovhead](https://www.tarkovhead.com/en).

### Ground Zero

`pages/maps/ground-zero.html` · **Livrée** ([bilan de phase](phase-4.md)) · Différencier tutoriel, rotation débutant et variante 21+.

**Sections :** Contexte et accès : mode, durée, joueurs et restrictions · Reconnaissance des bâtiments, premières quêtes et condition des rencontres selon variante. · Extractions PMC/Scav, transits et conditions ; liste alternative à la carte · Apparitions en jeu et boss (mode, date, déclencheur), dangers et points de vue · Clés, loot et routes de quêtes par niveau ; conseils PvP/PvE propres à ce terrain.

**Interaction :** Carte filtrable avec navigation clavier et listes par type ; onglets de mode ; liens de quête et de boss.

**JPG livré :** `images/maps/norvinsk-overlook.jpg` (panorama de PHASE_2 réutilisé).

**Vérification :** Comparer identifiants, niveaux, présence de Kollontay/Cultistes et régimes par mode.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-maps](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov), [mapgenie](https://mapgenie.io/tarkov), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [tracker](https://tarkovtracker.io).

### The Labyrinth

`pages/maps/the-labyrinth.html` · **Livrée** ([bilan de phase](phase-4.md)) · Expliquer le transit et les chambres de l’instance souterraine.

**Sections :** Contexte et accès : mode, durée, joueurs et restrictions · Clés Labrys/Knossos à contrôler ; chambres, puzzles et séquence Shadow of Tagilla → Vengeful Killa. · Extractions PMC/Scav, transits et conditions ; liste alternative à la carte · Apparitions en jeu et boss (mode, date, déclencheur), dangers et points de vue · Clés, loot et routes de quêtes par niveau ; conseils PvP/PvE propres à ce terrain.

**Interaction :** Carte filtrable avec navigation clavier et listes par type ; onglets de mode ; liens de quête et de boss.

**JPG livré :** `images/maps/the-labyrinth.jpg` (illustration d’ambiance, pas un plan navigable).

**Vérification :** Vérifier règles d’accès et distinguer apparition conditionnelle d’un taux de spawn.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-maps](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov), [mapgenie](https://mapgenie.io/tarkov), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses).

### Icebreaker

`pages/maps/icebreaker.html` · **Livrée** ([bilan de phase](phase-4.md)) · Présenter l’expédition Boreas par pont sans la qualifier d’exclusivité PvE Zone.

**Sections :** Contexte et accès : mode, durée, joueurs et restrictions · Conditions d’accès et kit marin à vérifier ; progression, salles, The Wedge, Knight et groupes privés. · Extractions PMC/Scav, transits et conditions ; liste alternative à la carte · Apparitions en jeu et boss (mode, date, déclencheur), dangers et points de vue · Clés, loot et routes de quêtes par niveau ; conseils PvP/PvE propres à ce terrain.

**Interaction :** Carte filtrable avec navigation clavier et listes par type ; onglets de mode ; liens de quête et de boss.

**JPG livré :** `images/maps/icebreaker.jpg` (illustration d’ambiance, pas un plan navigable).

**Vérification :** Revalider après les équilibrages de novembre et vérifier les modes et conditions de l’hélicoptère.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-maps](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov), [mapgenie](https://mapgenie.io/tarkov), [patch105](https://steamcommunity.com/games/3932890/announcements/detail/703268976281519055), [patch115](https://steamcommunity.com/games/3932890/announcements/detail/712285688032135503), [patch120](https://store.steampowered.com/news/app/3932890/view/708910525152495848), [balance-nov](https://t.me/s/escapefromtarkovEN/6990), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses).

### Terminal

`pages/maps/terminal.html` · **Livrée** ([bilan de phase](phase-4.md)) · Documenter le lieu d’exfiltration de l’histoire et ses conditions spécifiques.

**Sections :** Contexte et accès : mode, durée, joueurs et restrictions · Port, accès narratif et sections avec avertissement de spoilers. · Extractions PMC/Scav, transits et conditions ; liste alternative à la carte · Apparitions en jeu et boss (mode, date, déclencheur), dangers et points de vue · Clés, loot et routes de quêtes par niveau ; conseils PvP/PvE propres à ce terrain.

**Interaction :** Carte filtrable avec navigation clavier et listes par type ; onglets de mode ; liens de quête et de boss.

**JPG livré :** `images/maps/norvinsk-overlook.jpg` (panorama de PHASE_2 réutilisé).

**Vérification :** Vérifier conditions de transit, temps de raid divergent et effets narratifs avant publication.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-maps](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov), [mapgenie](https://mapgenie.io/tarkov), [terminal](https://t.me/s/escapefromtarkovEN/7001), [patch120](https://store.steampowered.com/news/app/3932890/view/708910525152495848), [tracker](https://tarkovtracker.io).

## Phase 5 — Armes et munitions

### Arsenal

`pages/weapons/index.html` · **Livrée** ([bilan](phase-5.md), [vérifications](verifications-phase-5.md)) · Trouver et comparer les objets de l’arsenal EFT selon ses contraintes en jeu.

**Sections :** Catalogue par famille avec tags de couverture · Stats nues contre preset stock et compatibilité calibre · Exemples budget/haut de gamme, disponibilité par trader · Lecture des statistiques exportées, sans tier list ni classement de méta.

**Interaction :** Filtres catégorie, calibre, trader/LL, budget, cadence et ergo ; comparaison de 2 à 3 objets.

**Illustrations JPG utilisées :** JPG local générique par famille; aucune correspondance exacte avec un ID EFT et aucune statistique inférée depuis l’image.

**Vérification :** Recharger les trois modes ; vérifier prix, presets effectifs et entrées de signalement distinctes.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/).

### Fusils d’assaut

`pages/weapons/assault-rifles.html` · **Livrée** ([bilan](phase-5.md), [vérifications](verifications-phase-5.md)) · Assault rifles et carbines : disponibilité et coût total.

**Sections :** Rôle et périmètre du catalogue · Sous-catégories rifles/carbines, AK et M4A1, paliers de traders et configurations stock. · Table triable : caractéristiques disponibles, traders et devises · Comparaison descriptive des champs exportés, sans classement de méta ni preset complet validé en jeu.

**Interaction :** Filtre et comparaison par identifiant, bascule modèle nu/preset, renvoi vers la table de munitions.

**Illustrations JPG utilisées :** JPG local générique par famille; aucune correspondance exacte avec un ID EFT et aucune statistique inférée depuis l’image.

**Vérification :** Vérifier regroupement carabines, calibres et coût des presets complets.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/), [tracker](https://tarkovtracker.io).

### Pistolets-mitrailleurs (SMG)

`pages/weapons/smgs.html` · **Livrée** ([bilan](phase-5.md), [vérifications](verifications-phase-5.md)) · Comparer les SMG pour les cartes et contextes jeu à courte distance.

**Sections :** Rôle et périmètre du catalogue · Familles MP5/MP7/PP et alternatives, calibre, chargeurs et contraintes d’acquisition. · Table triable : caractéristiques disponibles, traders et devises · Comparaison descriptive des champs exportés, sans classement de méta ni preset complet validé en jeu.

**Interaction :** Filtre et comparaison par identifiant, bascule modèle nu/preset, renvoi vers la table de munitions.

**Illustrations JPG utilisées :** JPG local générique par famille; aucune correspondance exacte avec un ID EFT et aucune statistique inférée depuis l’image.

**Vérification :** Vérifier les chargeurs réellement compatibles ainsi que les restrictions Flea.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/), [tracker](https://tarkovtracker.io).

### Fusils à pompe

`pages/weapons/shotguns.html` · **Livrée** ([bilan](phase-5.md), [vérifications](verifications-phase-5.md)) · Distinguer manuels et semi-auto, usages de quêtes et profils de munitions.

**Sections :** Rôle et périmètre du catalogue · Pompes, semi-auto et variantes ; projectile unique et chevrotine dans le modèle du jeu. · Table triable : caractéristiques disponibles, traders et devises · Comparaison descriptive des champs exportés, sans classement de méta ni preset complet validé en jeu.

**Interaction :** Filtre et comparaison par identifiant, bascule modèle nu/preset, renvoi vers la table de munitions.

**Illustrations JPG utilisées :** JPG local générique par famille; aucune correspondance exacte avec un ID EFT et aucune statistique inférée depuis l’image.

**Vérification :** Recouper catégories, cadence renseignée et multiplicité des projectiles.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/), [tracker](https://tarkovtracker.io).

### Fusils de précision

`pages/weapons/sniper-rifles.html` · **Livrée** ([bilan](phase-5.md), [vérifications](verifications-phase-5.md)) · Bien lire les paramètres d’un fusil à verrou du jeu.

**Sections :** Rôle et périmètre du catalogue · Fusils à verrou et variantes ; poids, ergonomie, munitions et quêtes concernées. · Table triable : caractéristiques disponibles, traders et devises · Comparaison descriptive des champs exportés, sans classement de méta ni preset complet validé en jeu.

**Interaction :** Filtre et comparaison par identifiant, bascule modèle nu/preset, renvoi vers la table de munitions.

**Illustrations JPG utilisées :** JPG local générique par famille; aucune correspondance exacte avec un ID EFT et aucune statistique inférée depuis l’image.

**Vérification :** S’assurer que le classement ne mélange pas les DMR et que les profils de munitions sont datés.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/), [tracker](https://tarkovtracker.io).

### Fusils de tireur désigné (DMR)

`pages/weapons/dmrs.html` · **Livrée** ([bilan](phase-5.md), [vérifications](verifications-phase-5.md)) · Distinguer coût, ergonomie et cadence des DMR dans EFT.

**Sections :** Rôle et périmètre du catalogue · Plateformes 7,62 et autres groupes, versions, optiques équipables en jeu et commerce. · Table triable : caractéristiques disponibles, traders et devises · Comparaison descriptive des champs exportés, sans classement de méta ni preset complet validé en jeu.

**Interaction :** Filtre et comparaison par identifiant, bascule modèle nu/preset, renvoi vers la table de munitions.

**Illustrations JPG utilisées :** JPG local générique par famille; aucune correspondance exacte avec un ID EFT et aucune statistique inférée depuis l’image.

**Vérification :** Vérifier la disponibilité du preset et la différence arme de base/preset.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/), [tracker](https://tarkovtracker.io).

### Mitrailleuses légères (LMG)

`pages/weapons/lmgs.html` · **Livrée** ([bilan](phase-5.md), [vérifications](verifications-phase-5.md)) · Comparer les modèles en tenant compte du poids et de l’inventaire.

**Sections :** Rôle et périmètre du catalogue · RPK, familles PK et autres ; cadence, alimentation, coût in-game et rôle jeu. · Table triable : caractéristiques disponibles, traders et devises · Comparaison descriptive des champs exportés, sans classement de méta ni preset complet validé en jeu.

**Interaction :** Filtre et comparaison par identifiant, bascule modèle nu/preset, renvoi vers la table de munitions.

**Illustrations JPG utilisées :** JPG local générique par famille; aucune correspondance exacte avec un ID EFT et aucune statistique inférée depuis l’image.

**Vérification :** Distinguer armes fixes et objets transportables ; contrôler les objets de boss non achetables.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/), [tracker](https://tarkovtracker.io).

### Pistolets et revolvers

`pages/weapons/pistols.html` · **Livrée** ([bilan](phase-5.md), [vérifications](verifications-phase-5.md)) · Trouver une arme de poing accessible à la progression du joueur.

**Sections :** Rôle et périmètre du catalogue · Pistolets et revolvers, cadence de jeu, encombrement et tâches dédiées. · Table triable : caractéristiques disponibles, traders et devises · Comparaison descriptive des champs exportés, sans classement de méta ni preset complet validé en jeu.

**Interaction :** Filtre et comparaison par identifiant, bascule modèle nu/preset, renvoi vers la table de munitions.

**Illustrations JPG utilisées :** JPG local générique par famille; aucune correspondance exacte avec un ID EFT et aucune statistique inférée depuis l’image.

**Vérification :** Distinguer les dispositifs de signalement des armes de poing de combat en jeu.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/), [tracker](https://tarkovtracker.io).

### Armes de mêlée

`pages/weapons/melee.html` · **Livrée** ([bilan](phase-5.md), [vérifications](verifications-phase-5.md)) · Identifier valeurs de jeu, objets rares et usage d’accès.

**Sections :** Rôle et périmètre du catalogue · Dégâts in-game, quêtes et échange ; distinguer Red Rebel en tant que prérequis d’extraction. · Table triable : caractéristiques disponibles, traders et devises · Comparaison descriptive des champs exportés, sans classement de méta ni preset complet validé en jeu.

**Interaction :** Filtre et comparaison par identifiant, bascule modèle nu/preset, renvoi vers la table de munitions.

**Illustrations JPG utilisées :** JPG local générique par famille; aucune correspondance exacte avec un ID EFT et aucune statistique inférée depuis l’image.

**Vérification :** Classer les objets de mêlée sans extrapoler les valeurs à du matériel réel.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/), [tracker](https://tarkovtracker.io).

### Lanceurs en jeu

`pages/weapons/grenade-launchers.html` · **Livrée** ([bilan](phase-5.md), [vérifications](verifications-phase-5.md)) · Classer les lanceurs portés, fragments de catalogue et accessoires.

**Sections :** Rôle et périmètre du catalogue · Lanceurs autonomes, accessoires sous canon, signaux et identifiants de munitions jeu. · Table triable : caractéristiques disponibles, traders et devises · Comparaison descriptive des champs exportés, sans classement de méta ni preset complet validé en jeu.

**Interaction :** Filtre et comparaison par identifiant, bascule modèle nu/preset, renvoi vers la table de munitions.

**Illustrations JPG utilisées :** JPG local générique par famille; aucune correspondance exacte avec un ID EFT et aucune statistique inférée depuis l’image.

**Vérification :** Recouper les faux positifs du tag gun, les dispositifs de signalement et les catégories API.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/), [tracker](https://tarkovtracker.io).

### Modifications d’armes

`pages/weapons/weapon-mods.html` · **Livrée** ([bilan](phase-5.md), [vérifications](verifications-phase-5.md)) · Comprendre l’interface de presets et les dépendances d’accessoires EFT.

**Sections :** Rôle et périmètre du catalogue · Nœuds et slots du système Gunsmith, incompatibilités par ID, ergo/recul et budget du preset. · Table triable : caractéristiques disponibles, traders et devises · Comparaison descriptive des champs exportés, sans classement de méta ni preset complet validé en jeu.

**Interaction :** Filtre et comparaison par identifiant, bascule modèle nu/preset, renvoi vers la table de munitions.

**Illustrations JPG utilisées :** JPG local générique par famille; aucune correspondance exacte avec un ID EFT et aucune statistique inférée depuis l’image.

**Vérification :** Recouper données ItemPropertiesWeaponMod, slots, exclusions et tâches Gunsmith ; in-game uniquement.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/), [tracker](https://tarkovtracker.io).

### Munitions & balistique en jeu

`pages/ammo/index.html` · **Livrée** ([bilan](phase-5.md), [vérifications](verifications-phase-5.md)) · Apprendre à lire les chiffres EFT sans confondre les valeurs et probabilités.

**Sections :** Dégâts de chair, pénétration, usure et fragmentation : unités du jeu · Cartouches, paquets et variantes · Exemples par budget, mode et disponibilité · Lien au tableau exhaustif du flux et contexte des classes d’armure.

**Interaction :** Sélecteur de calibre, recommandations par budget et nuage de points avec table accessible.

**Illustrations JPG utilisées :** JPG local générique par famille; aucune correspondance exacte avec un ID EFT et aucune statistique inférée depuis l’image.

**Vérification :** Vérifier les unités de chaque champ et les écarts de documentation sur la fragmentation.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/).

### Tableau balistique interactif

`pages/ammo/ammo-chart.html` · **Livrée** ([bilan](phase-5.md), [vérifications](verifications-phase-5.md)) · Filtrer et comparer les lignes du flux par mode et calibre.

**Sections :** Table nom/calibre/dégâts/pénétration/fragmentation/vitesse · Disponibilité trader et craft à dater · Graphique dégâts ↔ pénétration et matrice d’efficacité explicitement indicative · Données inconnues et provenance.

**Interaction :** Chart.js local par chargement différé ; filtres, tri, libellés texte et équivalent tabulaire à la couleur.

**Illustrations JPG utilisées :** JPG local générique par famille; aucune correspondance exacte avec un ID EFT et aucune statistique inférée depuis l’image.

**Vérification :** Actualiser tarifs, crafts et notes par mode ; ne pas inventer un calcul exact de pénétration.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/).

## Phase 6 — Armures et boss

### Armures & protection en jeu

`pages/armor/index.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Comprendre la couverture réelle dans le modèle d’armure EFT.

**Sections :** Classes, zones, armures souples, plaques, casques et rigs · État, réparation, poids et pénalités · Recommandations par slot et niveau de budget.

**Interaction :** Comparaison à deux colonnes, filtre pièce/mode/classe avec texte, renvois casque/plaque/rig.

**JPG envisagés :** Matériel EFT posé dans un vestiaire · Schéma de couverture du modèle de jeu.

**Vérification :** Vérifier les zones dans le client et préserver les classes par pièce/plaque, pas de classe agrégée trompeuse.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/).

### Gilets & plaques

`pages/armor/body-armor.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Distinguer le porte-plaques, les inserts et la protection intégrée.

**Sections :** Formats et compatibilité des inserts · Zones et classes par emplacement · Durabilité, matériaux et réparation.

**Interaction :** Comparer couvertures et filtrer par classe/poids.

**Illustration JPG utilisée :** porte-plaques et plaques fictifs, vierges de texte et de marque; l’image n’encode aucune classe, valeur ni compatibilité EFT.

**Vérification :** Ne pas attribuer une classe aux emplacements vides ; vérifier le kit vendu par défaut.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/).

### Casques & visières

`pages/armor/helmets.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Repérer les protections compatibles avec les pièces portées.

**Sections :** Zones de tête couvertes · Visières, accessoires et conflits de slots · Vision, son et pénalités en jeu.

**Interaction :** Filtrer par zones, classe et compatibilité casque de communication.

**JPG envisagés :** Casque et visière du jeu · Planche de zones tête.

**Vérification :** Vérifier par emplacement les protections, classes et incompatibilités.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/).

### Rigs tactiques

`pages/armor/rigs.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Comparer capacité d’inventaire et protection sans confondre rigs et armures.

**Sections :** Armored rigs et gilets simples · Nombre, disposition et limites de stockage des cases · Comparatif budget et poids.

**Interaction :** Afficher une grille de cases avec liste textuelle ; trier poids/capacité.

**JPG envisagés :** Gilet tactique EFT · Schéma de capacité de rig.

**Vérification :** Distinguer cases utiles, classe intégrée, et pièces compatibles.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/).

### Comparateur d’armures

`pages/armor/armor-chart.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Comparer des objets de même slot sur les valeurs du flux.

**Sections :** Table de valeurs · Choix du mode et des emplacements · Interprétation et source.

**Interaction :** Sélection côte à côte ; barres et valeurs numériques ; liens permanents à la fiche.

**JPG envisagés :** Présentation catalogue EFT · Graphique explicatif matériau/durabilité.

**Vérification :** Tester les valeurs nulles et l’absence de référence de plaque.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/).

### Boss de Tarkov

`pages/bosses/index.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Identifier une rencontre et son contexte sans réduire le jeu à un pourcentage fixe.

**Sections :** Boss uniques, groupes, gardes, Raiders/Rogues et variantes à distinguer · Carte de présence et filtre par mode · Table HP, équipement notable et difficulté éditoriale · Liens vers profils, vidéos corroborées et aides en jeu.

**Interaction :** Comparaison des profils, onglets PvP/PvE/Seasonal et grille par lieu.

**JPG envisagés :** Reshala et dortoirs · Killa dans ULTRA · Tagilla dans Factory · The Goons, trio.

**Vérification :** Réconcilier noms et variantes : ne pas compter chaque enregistrement de mob comme boss distinct.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [balance-nov](https://t.me/s/escapefromtarkovEN/6990), [halloween](https://x.com/tarkov/status/2122283819667464473).

### Reshala

`pages/bosses/reshala.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Préparer cette rencontre dans EFT : Customs.

**Sections :** Identification et lieux vérifiés (mode, variante et date) · Dortoirs et zones alternatives ; comportement et rôle des gardes ; Golden TT à contrôler. · HP par zone et équipement de jeu quand attestés ; gardes et comportement IA · Loot, quêtes liées et stratégie propre au fonctionnement du raid.

**Interaction :** Onglets par mode et renvois carte/quête ; fiche comparateur issue du hub.

**JPG envisagés :** Reshala : portrait illustratif · Reshala : localisation ou équipement notable dans le jeu.

**Vérification :** Vérifier la fiche dédiée Reshala, ses entrées Tarkov.dev et leur validité pour Customs ; ne pas reprendre les taux du brief.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875).

### Killa

`pages/bosses/killa.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Préparer cette rencontre dans EFT : Interchange.

**Sections :** Identification et lieux vérifiés (mode, variante et date) · Tenue et visière ; présence par secteurs d’ULTRA ; distinguer son pendant du Labyrinth. · HP par zone et équipement de jeu quand attestés ; gardes et comportement IA · Loot, quêtes liées et stratégie propre au fonctionnement du raid.

**Interaction :** Onglets par mode et renvois carte/quête ; fiche comparateur issue du hub.

**JPG envisagés :** Killa : portrait illustratif · Killa : localisation ou équipement notable dans le jeu.

**Vérification :** Vérifier la fiche dédiée Killa, ses entrées Tarkov.dev et leur validité pour Interchange ; ne pas reprendre les taux du brief.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [halloween](https://x.com/tarkov/status/2122283819667464473).

### Shturman

`pages/bosses/shturman.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Préparer cette rencontre dans EFT : Woods.

**Sections :** Identification et lieux vérifiés (mode, variante et date) · Scierie et gardes ; clé de cache et probabilités de Red Rebel si sourcées. · HP par zone et équipement de jeu quand attestés ; gardes et comportement IA · Loot, quêtes liées et stratégie propre au fonctionnement du raid.

**Interaction :** Onglets par mode et renvois carte/quête ; fiche comparateur issue du hub.

**JPG envisagés :** Shturman : portrait illustratif · Shturman : localisation ou équipement notable dans le jeu.

**Vérification :** Vérifier la fiche dédiée Shturman, ses entrées Tarkov.dev et leur validité pour Woods ; ne pas reprendre les taux du brief.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875).

### Glukhar

`pages/bosses/glukhar.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Préparer cette rencontre dans EFT : Reserve / variantes.

**Sections :** Identification et lieux vérifiés (mode, variante et date) · Groupes de gardes et positions sur la base ; confirmer autres lieux séparément. · HP par zone et équipement de jeu quand attestés ; gardes et comportement IA · Loot, quêtes liées et stratégie propre au fonctionnement du raid.

**Interaction :** Onglets par mode et renvois carte/quête ; fiche comparateur issue du hub.

**JPG envisagés :** Glukhar : portrait illustratif · Glukhar : localisation ou équipement notable dans le jeu.

**Vérification :** Vérifier la fiche dédiée Glukhar, ses entrées Tarkov.dev et leur validité pour Reserve / variantes ; ne pas reprendre les taux du brief.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875).

### Sanitar

`pages/bosses/sanitar.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Préparer cette rencontre dans EFT : Shoreline.

**Sections :** Identification et lieux vérifiés (mode, variante et date) · Resort, jetée et cottages ; soins IA et équipement notable en jeu. · HP par zone et équipement de jeu quand attestés ; gardes et comportement IA · Loot, quêtes liées et stratégie propre au fonctionnement du raid.

**Interaction :** Onglets par mode et renvois carte/quête ; fiche comparateur issue du hub.

**JPG envisagés :** Sanitar : portrait illustratif · Sanitar : localisation ou équipement notable dans le jeu.

**Vérification :** Vérifier la fiche dédiée Sanitar, ses entrées Tarkov.dev et leur validité pour Shoreline ; ne pas reprendre les taux du brief.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875).

### Tagilla

`pages/bosses/tagilla.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Préparer cette rencontre dans EFT : Factory.

**Sections :** Identification et lieux vérifiés (mode, variante et date) · Reconnaître le masque et l’agression de l’IA ; variantes Infected et Terminal isolées. · HP par zone et équipement de jeu quand attestés ; gardes et comportement IA · Loot, quêtes liées et stratégie propre au fonctionnement du raid.

**Interaction :** Onglets par mode et renvois carte/quête ; fiche comparateur issue du hub.

**JPG envisagés :** Tagilla : portrait illustratif · Tagilla : localisation ou équipement notable dans le jeu.

**Vérification :** Vérifier la fiche dédiée Tagilla, ses entrées Tarkov.dev et leur validité pour Factory ; ne pas reprendre les taux du brief.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [halloween](https://x.com/tarkov/status/2122283819667464473).

### Kaban

`pages/bosses/kaban.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Préparer cette rencontre dans EFT : Streets of Tarkov.

**Sections :** Identification et lieux vérifiés (mode, variante et date) · LexOs, gardes et zone ; clés et quêtes liées. · HP par zone et équipement de jeu quand attestés ; gardes et comportement IA · Loot, quêtes liées et stratégie propre au fonctionnement du raid.

**Interaction :** Onglets par mode et renvois carte/quête ; fiche comparateur issue du hub.

**JPG envisagés :** Kaban : portrait illustratif · Kaban : localisation ou équipement notable dans le jeu.

**Vérification :** Vérifier la fiche dédiée Kaban, ses entrées Tarkov.dev et leur validité pour Streets of Tarkov ; ne pas reprendre les taux du brief.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875).

### Kollontay

`pages/bosses/kollontay.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Préparer cette rencontre dans EFT : Streets / Ground Zero à vérifier.

**Sections :** Identification et lieux vérifiés (mode, variante et date) · Variantes de lieu, gardes et effets in-game ; conditions de la carte débutant. · HP par zone et équipement de jeu quand attestés ; gardes et comportement IA · Loot, quêtes liées et stratégie propre au fonctionnement du raid.

**Interaction :** Onglets par mode et renvois carte/quête ; fiche comparateur issue du hub.

**JPG envisagés :** Kollontay : portrait illustratif · Kollontay : localisation ou équipement notable dans le jeu.

**Vérification :** Vérifier la fiche dédiée Kollontay, ses entrées Tarkov.dev et leur validité pour Streets / Ground Zero à vérifier ; ne pas reprendre les taux du brief.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875).

### Zryachiy

`pages/bosses/zryachiy.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Préparer cette rencontre dans EFT : Lighthouse.

**Sections :** Identification et lieux vérifiés (mode, variante et date) · Péninsule, accès à Lightkeeper et conséquences en jeu ; état actualisé. · HP par zone et équipement de jeu quand attestés ; gardes et comportement IA · Loot, quêtes liées et stratégie propre au fonctionnement du raid.

**Interaction :** Onglets par mode et renvois carte/quête ; fiche comparateur issue du hub.

**JPG envisagés :** Zryachiy : portrait illustratif · Zryachiy : localisation ou équipement notable dans le jeu.

**Vérification :** Vérifier la fiche dédiée Zryachiy, ses entrées Tarkov.dev et leur validité pour Lighthouse ; ne pas reprendre les taux du brief.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875).

### Partisan

`pages/bosses/partisan.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Préparer cette rencontre dans EFT : Plusieurs cartes.

**Sections :** Identification et lieux vérifiés (mode, variante et date) · Présence et karma PMC, fix 1.3.0.0 et mises à jour récentes ; taux nominal vs conditionnel. · HP par zone et équipement de jeu quand attestés ; gardes et comportement IA · Loot, quêtes liées et stratégie propre au fonctionnement du raid.

**Interaction :** Onglets par mode et renvois carte/quête ; fiche comparateur issue du hub.

**JPG envisagés :** Partisan : portrait illustratif · Partisan : localisation ou équipement notable dans le jeu.

**Vérification :** Vérifier la fiche dédiée Partisan, ses entrées Tarkov.dev et leur validité pour Plusieurs cartes ; ne pas reprendre les taux du brief.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875).

### Cultist Priest

`pages/bosses/cultist-priest.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Préparer cette rencontre dans EFT : Variantes nocturnes.

**Sections :** Identification et lieux vérifiés (mode, variante et date) · Séparer Priest, combattants associés et événements ; fenêtres horaires en jeu. · HP par zone et équipement de jeu quand attestés ; gardes et comportement IA · Loot, quêtes liées et stratégie propre au fonctionnement du raid.

**Interaction :** Onglets par mode et renvois carte/quête ; fiche comparateur issue du hub.

**JPG envisagés :** Cultist Priest : portrait illustratif · Cultist Priest : localisation ou équipement notable dans le jeu.

**Vérification :** Vérifier la fiche dédiée Cultist Priest, ses entrées Tarkov.dev et leur validité pour Variantes nocturnes ; ne pas reprendre les taux du brief.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875).

### The Goons

`pages/bosses/the-goons.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Préparer cette rencontre dans EFT : Plusieurs cartes.

**Sections :** Identification et lieux vérifiés (mode, variante et date) · Knight, Big Pipe et Birdeye : tableaux distincts, groupe et rotations validées ; Knight sur Icebreaker séparé. · HP par zone et équipement de jeu quand attestés ; gardes et comportement IA · Loot, quêtes liées et stratégie propre au fonctionnement du raid.

**Interaction :** Onglets par mode et renvois carte/quête ; fiche comparateur issue du hub.

**JPG envisagés :** The Goons : portrait illustratif · The Goons : localisation ou équipement notable dans le jeu.

**Vérification :** Vérifier la fiche dédiée The Goons, ses entrées Tarkov.dev et leur validité pour Plusieurs cartes ; ne pas reprendre les taux du brief.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [patch105](https://steamcommunity.com/games/3932890/announcements/detail/703268976281519055), [balance-nov](https://t.me/s/escapefromtarkovEN/6990).

### Shadow of Tagilla

`pages/bosses/shadow-of-tagilla.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Préparer cette rencontre dans EFT : The Labyrinth.

**Sections :** Identification et lieux vérifiés (mode, variante et date) · Accès, équipement Labrys et déclenchement de la rencontre suivante. · HP par zone et équipement de jeu quand attestés ; gardes et comportement IA · Loot, quêtes liées et stratégie propre au fonctionnement du raid.

**Interaction :** Onglets par mode et renvois carte/quête ; fiche comparateur issue du hub.

**JPG envisagés :** Shadow of Tagilla : portrait illustratif · Shadow of Tagilla : localisation ou équipement notable dans le jeu.

**Vérification :** Vérifier la fiche dédiée Shadow of Tagilla, ses entrées Tarkov.dev et leur validité pour The Labyrinth ; ne pas reprendre les taux du brief.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875).

### The Wedge

`pages/bosses/the-wedge.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Préparer cette rencontre dans EFT : Icebreaker / The Lab (Dark).

**Sections :** Identification et lieux vérifiés (mode, variante et date) · Identifiants distincts, groupe Black Division et correctifs du 12 novembre. · HP par zone et équipement de jeu quand attestés ; gardes et comportement IA · Loot, quêtes liées et stratégie propre au fonctionnement du raid.

**Interaction :** Onglets par mode et renvois carte/quête ; fiche comparateur issue du hub.

**JPG envisagés :** The Wedge : portrait illustratif · The Wedge : localisation ou équipement notable dans le jeu.

**Vérification :** Vérifier la fiche dédiée The Wedge, ses entrées Tarkov.dev et leur validité pour Icebreaker / The Lab (Dark) ; ne pas reprendre les taux du brief.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [patch105](https://steamcommunity.com/games/3932890/announcements/detail/703268976281519055), [balance-nov](https://t.me/s/escapefromtarkovEN/6990).

### Vengeful Killa

`pages/bosses/vengeful-killa.html` · **Livrée** ([bilan](phase-6.md), [vérifications](verifications-phase-6.md)) · Préparer cette rencontre dans EFT : The Labyrinth.

**Sections :** Identification et lieux vérifiés (mode, variante et date) · Apparition après Shadow of Tagilla ; profil, loot et déclencheur à distinguer du Killa standard. · HP par zone et équipement de jeu quand attestés ; gardes et comportement IA · Loot, quêtes liées et stratégie propre au fonctionnement du raid.

**Interaction :** Onglets par mode et renvois carte/quête ; fiche comparateur issue du hub.

**JPG envisagés :** Vengeful Killa : portrait illustratif · Vengeful Killa : localisation ou équipement notable dans le jeu.

**Vérification :** Vérifier la fiche dédiée Vengeful Killa, ses entrées Tarkov.dev et leur validité pour The Labyrinth ; ne pas reprendre les taux du brief.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki-bosses](https://escapefromtarkov.fandom.com/wiki/Bosses), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875).


## Phase 7 — Traders, quêtes et planque · **Livrée localement**

**Bilan :** 16/16 routes locales; snapshot par mode daté, HTML statique, recherche et sitemap raccordés; QA finale PASS. Voir [`docs/phase-7.md`](phase-7.md) et [`docs/verifications-phase-7.md`](verifications-phase-7.md). Les huit visuels livrés sont des JPG éditoriaux partagés et génériques, non des portraits officiels ni des captures du jeu.

### Traders & interlocuteurs

`pages/traders/index.html` · **Livrée localement** · Choisir quel profil suivre selon son besoin et le mode de partie.

**Sections :** Dix traders mis en avant ; autres interlocuteurs/PNJ distingués · Loyauté, déblocage et inventaire représentatif · Quêtes et réputation depuis la refonte 1.1.0.0.

**Interaction :** Filtres spécialité/mode et navigation par niveau de loyauté ; champs non applicables explicites.

**JPG retenus à la livraison :** images partagées `traders-market.jpg` et `trader-ledger.jpg` — comptoir et registre fictifs, sans portrait ni inventaire exact.

**Contrôle livré :** 16 enregistrements répartis entre 10 traders et six interlocuteurs; les filtres et la table LL4 sont testés. Stocks et rotations ne sont pas live.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [patch115](https://steamcommunity.com/games/3932890/announcements/detail/712285688032135503), [tracker](https://tarkovtracker.io).

### Prapor

`pages/traders/prapor.html` · **Livrée localement** · Progression d’armes russes et premières chaînes.

**Sections :** Profil et condition de mise à disposition · Offres de départ, quêtes initiales et objets à conserver. · Table de réputation/niveau et offres datées · Ordre des quêtes, inventaire et alternatives accessibles.

**Interaction :** Filtre par LL et mode, ancres vers guides de quêtes et items à garder.

**JPG retenus à la livraison :** images partagées `traders-market.jpg` et `trader-ledger.jpg` — comptoir et registre fictifs, sans portrait ni inventaire exact.

**Contrôle livré :** Profil, conditions et LL recoupés sur l’export daté; offres et rotations restent communautaires et non vérifiées dans le client.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [tracker](https://tarkovtracker.io).

### Therapist

`pages/traders/therapist.html` · **Livrée localement** · Soins et ressources de départ.

**Sections :** Profil et condition de mise à disposition · Déblocages médicaux, service post-raid et chaînes de remise. · Table de réputation/niveau et offres datées · Ordre des quêtes, inventaire et alternatives accessibles.

**Interaction :** Filtre par LL et mode, ancres vers guides de quêtes et items à garder.

**JPG retenus à la livraison :** images partagées `traders-market.jpg` et `trader-ledger.jpg` — comptoir et registre fictifs, sans portrait ni inventaire exact.

**Contrôle livré :** Profil, conditions et LL recoupés sur l’export daté; offres et rotations restent communautaires et non vérifiées dans le client.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [tracker](https://tarkovtracker.io).

### Skier

`pages/traders/skier.html` · **Livrée localement** · Équipement, devises et quêtes à embranchements.

**Sections :** Profil et condition de mise à disposition · Arbitrages de réputation et distinguer quêtes permanentes de la branche Halloween. · Table de réputation/niveau et offres datées · Ordre des quêtes, inventaire et alternatives accessibles.

**Interaction :** Filtre par LL et mode, ancres vers guides de quêtes et items à garder.

**JPG retenus à la livraison :** images partagées `traders-market.jpg` et `trader-ledger.jpg` — comptoir et registre fictifs, sans portrait ni inventaire exact.

**Contrôle livré :** Profil, conditions et LL recoupés sur l’export daté; la branche Halloween n’est pas assimilée à la progression permanente.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [tracker](https://tarkovtracker.io).

### Peacekeeper

`pages/traders/peacekeeper.html` · **Livrée localement** · Dollars et équipement occidental.

**Sections :** Profil et condition de mise à disposition · Conversion et disponibilité par mode, déblocage de la chaîne de quêtes. · Table de réputation/niveau et offres datées · Ordre des quêtes, inventaire et alternatives accessibles.

**Interaction :** Filtre par LL et mode, ancres vers guides de quêtes et items à garder.

**JPG retenus à la livraison :** images partagées `traders-market.jpg` et `trader-ledger.jpg` — comptoir et registre fictifs, sans portrait ni inventaire exact.

**Contrôle livré :** Profil, conditions et LL recoupés sur l’export daté; disponibilité et stocks restent à vérifier dans le client.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [tracker](https://tarkovtracker.io).

### Mechanic

`pages/traders/mechanic.html` · **Livrée localement** · Presets, accessoires et progression Gunsmith.

**Sections :** Profil et condition de mise à disposition · Pièces par niveau, réparations en jeu et accès Lightkeeper. · Table de réputation/niveau et offres datées · Ordre des quêtes, inventaire et alternatives accessibles.

**Interaction :** Filtre par LL et mode, ancres vers guides de quêtes et items à garder.

**JPG retenus à la livraison :** images partagées `traders-market.jpg` et `trader-ledger.jpg` — comptoir et registre fictifs, sans portrait ni inventaire exact.

**Contrôle livré :** Profil et LL recoupés sur l’export daté; Gunsmith et accès Lightkeeper ne sont pas présentés comme vérifiés en client.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [tracker](https://tarkovtracker.io).

### Ragman

`pages/traders/ragman.html` · **Livrée localement** · Vêtements, gilets et gestion de l’inventaire.

**Sections :** Profil et condition de mise à disposition · Équipement par LL, personnalisation et synchronisation à vérifier. · Table de réputation/niveau et offres datées · Ordre des quêtes, inventaire et alternatives accessibles.

**Interaction :** Filtre par LL et mode, ancres vers guides de quêtes et items à garder.

**JPG retenus à la livraison :** images partagées `traders-market.jpg` et `trader-ledger.jpg` — comptoir et registre fictifs, sans portrait ni inventaire exact.

**Contrôle livré :** Profil, conditions et LL recoupés sur l’export daté; vêtements, stocks et rotations restent à vérifier dans le client.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [tracker](https://tarkovtracker.io).

### Jaeger

`pages/traders/jaeger.html` · **Livrée localement** · Déblocage et progression de ses quêtes.

**Sections :** Profil et condition de mise à disposition · Chaîne d’accès et premiers barters ; exceptions de réputation. · Table de réputation/niveau et offres datées · Ordre des quêtes, inventaire et alternatives accessibles.

**Interaction :** Filtre par LL et mode, ancres vers guides de quêtes et items à garder.

**JPG retenus à la livraison :** images partagées `traders-market.jpg` et `trader-ledger.jpg` — comptoir et registre fictifs, sans portrait ni inventaire exact.

**Contrôle livré :** Profil, conditions et LL recoupés sur l’export daté; exceptions et stocks restent à vérifier dans le client.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [tracker](https://tarkovtracker.io).

### Fence

`pages/traders/fence.html` · **Livrée localement** · Relation entre karma Scav, transactions et Collector.

**Sections :** Profil et condition de mise à disposition · Seuils de karma, effets à vérifier, progression de la quête Collector. · Table de réputation/niveau et offres datées · Ordre des quêtes, inventaire et alternatives accessibles.

**Interaction :** Filtre par LL et mode, ancres vers guides de quêtes et items à garder.

**JPG retenus à la livraison :** images partagées `traders-market.jpg` et `trader-ledger.jpg` — comptoir et registre fictifs, sans portrait ni inventaire exact.

**Contrôle livré :** Profil et données de progression recoupés sur les exports; les effets de karma restent attribués à la source communautaire.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [tracker](https://tarkovtracker.io).

### Lightkeeper

`pages/traders/lightkeeper.html` · **Livrée localement** · Accès narratif et périmètre Lighthouse.

**Sections :** Profil et condition de mise à disposition · Vérifier To the Light, exceptions de LL et post-refonte de la péninsule. · Table de réputation/niveau et offres datées · Ordre des quêtes, inventaire et alternatives accessibles.

**Interaction :** Filtre par LL et mode, ancres vers guides de quêtes et items à garder.

**JPG retenus à la livraison :** images partagées `traders-market.jpg` et `trader-ledger.jpg` — comptoir et registre fictifs, sans portrait ni inventaire exact.

**Contrôle livré :** Profil et exigences proviennent de sources export/wiki; les conditions d’accès sont explicitement à confirmer dans le client.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [tracker](https://tarkovtracker.io), [patch115](https://steamcommunity.com/games/3932890/announcements/detail/712285688032135503).

### Ref

`pages/traders/ref.html` · **Livrée localement** · Séparer Arena, PvP et PvE côté transferts et récompenses.

**Sections :** Profil et condition de mise à disposition · Monnaies, Lega Medals, inventaire et règles de synchronisation par mode. · Table de réputation/niveau et offres datées · Ordre des quêtes, inventaire et alternatives accessibles.

**Interaction :** Filtre par LL et mode, ancres vers guides de quêtes et items à garder.

**JPG retenus à la livraison :** images partagées `traders-market.jpg` et `trader-ledger.jpg` — comptoir et registre fictifs, sans portrait ni inventaire exact.

**Contrôle livré :** Données de Ref séparées par mode; transferts et synchronisation restent des champs communautaires, non validés en client.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [tracker](https://tarkovtracker.io), [arena](https://arena.tarkov.com/news/category/patchnotes).

### Quêtes de Tarkov

`pages/quests/index.html` · **Livrée localement** · Savoir quoi entreprendre et emporter selon le mode et le prérequis réel.

**Sections :** Quêtes par trader, histoire et événements · Prérequis, objectifs, récompenses, cartes et objets · Routes de progression et priorités débutant · Arbre et Kappa : données et limites.

**Interaction :** Filtre trader/carte/mode/autres critères, recherche et progression stockée localement.

**JPG retenus à la livraison :** `quest-board.jpg`, `quest-dossier.jpg` ou `kappa-case.jpg` selon la page — illustrations fictives, sans capture ni interface officielle.

**Contrôle livré :** Trois snapshots comparés : 503/499/462 tâches et 138/138/135 enregistrements de quête; lacunes et divergences sont documentées, sans validation client.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [tracker](https://tarkovtracker.io), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [patch120](https://store.steampowered.com/news/app/3932890/view/708910525152495848), [balance-nov](https://t.me/s/escapefromtarkovEN/6990).

### Arbre des quêtes

`pages/quests/quest-tree.html` · **Livrée localement** · Voir le prochain objectif réalisable et les chaînes qui le bloquent.

**Sections :** Graphe des prérequis, ET/OU et niveau · Cartes, objets et liens par quête · Statut local et méthode de calcul.

**Interaction :** Graphe et liste accessibles, filtre par trader/mode et statut persistant avec export JSON local.

**JPG retenus à la livraison :** `quest-board.jpg`, `quest-dossier.jpg` ou `kappa-case.jpg` selon la page — illustrations fictives, sans capture ni interface officielle.

**Contrôle livré :** Audit des dépendances : 222/221/184 arêtes déclarées et zéro cycle par mode; aucune logique complète du client n’est inférée.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [tracker](https://tarkovtracker.io), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki).

### Guide du conteneur Kappa

`pages/quests/kappa-guide.html` · **Livrée localement** · Suivre Collector et ses exigences réelles selon le mode.

**Sections :** Accès à Collector et prérequis datés · Checklist d’objets et condition Found in Raid · Quêtes obligatoires et différences de progression par mode · Budget de stash et erreurs fréquentes.

**Interaction :** Suivi sauvegardé localement, filtres et liens vers objets et quêtes.

**JPG retenus à la livraison :** `quest-board.jpg`, `quest-dossier.jpg` ou `kappa-case.jpg` selon la page — illustrations fictives, sans capture ni interface officielle.

**Contrôle livré :** 44 objectifs Collector affichés et balises FIR provenant de l’export; divergence niveau 42/cinq prérequis contre 40/quatre documentée.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [tracker](https://tarkovtracker.io), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [kappaguide](https://kappaguide.com/maps).

### Planque (Hideout)

`pages/hideout/index.html` · **Livrée localement** · Investir les ressources selon les déblocages et le temps de jeu.

**Sections :** Stations, niveaux et dépendances · Liste de matériaux et statut Found in Raid par mode · Paliers de priorité, Bitcoin Farm et ROI scénarisé · Alimentation et coûts récurrents en jeu.

**Interaction :** Arbre de stations, comparaison de paliers et checklist locale.

**JPG retenus à la livraison :** `hideout-plan.jpg`, `hideout-crafting.jpg` et `crafting-recipe.jpg` selon la page — ambiance fictive, sans mesure de jeu ni coût encodé.

**Contrôle livré :** 26 stations et 68 niveaux par mode; 317 lignes matériaux, dont 76 FIR en regular/PvE et zéro en Seasonal.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [tracker](https://tarkovtracker.io), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [market](https://tarkov-market.com/).

### Atelier & recettes

`pages/hideout/crafting.html` · **Livrée localement** · Estimer un gain de craft en explicitant les coûts en jeu.

**Sections :** Ingrédients, station et durée par recette · Coût des consommables, frais et coûts d’opportunité · Alternatives pour objets de quête et temps par session.

**Interaction :** Tri coût/durée et simulateur de marge, ajustement manuel d’un prix sans connexion.

**JPG retenus à la livraison :** `hideout-plan.jpg`, `hideout-crafting.jpg` et `crafting-recipe.jpg` selon la page — ambiance fictive, sans mesure de jeu ni coût encodé.

**Contrôle livré :** 214 recettes par snapshot; calcul de lot/marge testé avec prix saisis localement, sans marché live ni promesse de rentabilité.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [tracker](https://tarkovtracker.io), [market](https://tarkov-market.com/), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki).


## Phase 8 — Compétences, économie et stratégies

### Compétences (Skills)

`pages/skills/index.html` · Interpréter la progression et choisir des activités normales en jeu par compétence.

**Sections :** Compétences physiques, mentales, pratiques et d’armes · Actions, diminishing returns et tableaux par niveau si sourcés · Metabolism 1.3 et comparaison Seasonal/Standard.

**Interaction :** Filtrer par groupe, afficher le contexte de jeu et les sources de chaque formule.

**JPG envisagés :** Journal de compétences EFT · Diagramme de progression du personnage.

**Vérification :** Valider unités, multiplicateurs et chiffres confirmés ; aucun taux inventé.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [reddit-eft](https://www.reddit.com/r/EscapefromTarkov/).

### Économie & Flea Market

`pages/economy/index.html` · Mesurer les gains de raid et choisir entre vendre, stocker, échanger et crafter.

**Sections :** Marché par mode, traders, devises et TarCoin · Frais, offres et volatilité des prix · Routes de profit et coût du risque en jeu.

**Interaction :** Simulateur de revenu en roubles et liens vers marchés externes datés.

**JPG envisagés :** Objet de loot EFT et roubles de jeu · Table de suivi financier fictive.

**Vérification :** Vérifier restrictions, mode, libellé des devises, source et péremption des prix.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [market](https://tarkov-market.com/), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [tarcoin](https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/1836506165581325), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki).

### Guide du Flea Market

`pages/economy/flea-market.html` · Optimiser les décisions de mise en vente sans promesse de cours en direct.

**Sections :** Déblocage et interdits par mode · Offres, frais et réputation de marché · Exemples comparés de gain net.

**Interaction :** Calculatrice avec frais saisis ou version documentée et historique daté.

**JPG envisagés :** Illustration du Flea Market EFT · Schéma de vente et frais.

**Vérification :** Valider plafonds, catégories et disponibilité ; jamais appliquer un prix d’un autre mode.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [market](https://tarkov-market.com/), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki).

### Gagner des roubles

`pages/economy/money-making.html` · Choisir une boucle de loot en fonction du temps, de la progression et de la carte.

**Sections :** Rotation débutant et boucle PMC/Scav · Valeur par case, clés et coût d’entrée · Exemples de routes in-game avec issues de secours et risque.

**Interaction :** Comparateur de rentabilité avec temps estimé et valeurs éditables ; filtre carte/mode.

**JPG envisagés :** Sacs de loot du jeu · Planche de cases d’inventaire.

**Vérification :** Chiffrer sur un échantillon daté, pas de promesse de rendement fixe.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [market](https://tarkov-market.com/), [mapgenie](https://mapgenie.io/tarkov), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [reddit-eft](https://www.reddit.com/r/EscapefromTarkov/).

### Stratégies & méta en jeu

`pages/strategy/index.html` · Choisir des pratiques et kits adaptés au mode et au niveau du joueur.

**Sections :** Astuces débutant, routines et erreurs · PvP permanent, Seasonal et PvE/Prestige · Presets classés par budget et contraintes de progression.

**Interaction :** Onglets par mode et sélecteur de profil pour les guides.

**JPG envisagés :** PMC et menu de préparation EFT · Planche de brief de raid fictive.

**Vérification :** Séparer conseils opinatifs, expérience vidéo et faits datés ; éviter les données de la beta si 1.0+.

**Sources cibles :** [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch120](https://store.steampowered.com/news/app/3932890/view/708910525152495848), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [balance-nov](https://t.me/s/escapefromtarkovEN/6990), [tdev](https://json.tarkov.dev/endpoints), [reddit-eft](https://www.reddit.com/r/EscapefromTarkov/).

### 50+ astuces débutant

`pages/strategy/beginner-tips.html` · Proposer des automatismes utilisables dès les premiers raids.

**Sections :** Checklist du stash · 50+ conseils groupés : interface, cartes, soin et extraction · Pièges d’assurance et progression par mode.

**Interaction :** Liste filtrable et favoris locaux.

**JPG envisagés :** Rack de planque · Repère d’exfiltration EFT.

**Vérification :** Vérifier chaque mécanique susceptible d’avoir changé (assurance, contrôles, niveaux).

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [patch120](https://store.steampowered.com/news/app/3932890/view/708910525152495848), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [balance-nov](https://t.me/s/escapefromtarkovEN/6990), [reddit-eft](https://www.reddit.com/r/EscapefromTarkov/).

### Tactiques avancées en jeu

`pages/strategy/advanced-tactics.html` · Lire et organiser un raid en maîtrisant interfaces, bruit de jeu et ressources.

**Sections :** Choix d’objectif et fenêtres de raid · Mécaniques de stamina, audio et IA · Exemples sur les cartes du jeu.

**Interaction :** Scénarios et alternatives en accordéon.

**JPG envisagés :** Rue de Tarkov en raid · Diagramme de choix en match.

**Vérification :** Sourcer les interactions dans le moteur de jeu, sans extrapolation à la réalité.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [patch120](https://store.steampowered.com/news/app/3932890/view/708910525152495848), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [balance-nov](https://t.me/s/escapefromtarkovEN/6990), [reddit-eft](https://www.reddit.com/r/EscapefromTarkov/).

### Guide PvP

`pages/strategy/pvp-guide.html` · Préparer une session PvP en distinguant progression permanente et saisonnière.

**Sections :** Objectifs et choix de carte · Équipement en jeu selon budget · Analyse d’erreurs de jeu et post-raid.

**Interaction :** Onglets PvP Zone / Seasonal et checklists.

**JPG envisagés :** Opérateur fictif PvP · Planche de presets du jeu.

**Vérification :** Relire changements d’équilibrage et différences d’assurance, de trader et de Flea.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [patch120](https://store.steampowered.com/news/app/3932890/view/708910525152495848), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [balance-nov](https://t.me/s/escapefromtarkovEN/6990), [reddit-eft](https://www.reddit.com/r/EscapefromTarkov/).

### Guide PvE & Prestige

`pages/strategy/pve-guide.html` · Expliquer le mode BSG et les effets d’un Prestige sans le confondre avec Tushonka.

**Sections :** PvE officiel, solo et groupe · Bots, événements et raids côté serveur · Prestige : conditions, pertes et conservation.

**Interaction :** Sélecteur de palier de Prestige et avertissements avant reset.

**JPG envisagés :** Raid PvE illustratif · Chronologie graphique de Prestige.

**Vérification :** Vérifier la progression de l’histoire, les prérequis et les six niveaux réellement annoncés.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [patch120](https://store.steampowered.com/news/app/3932890/view/708910525152495848), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [balance-nov](https://t.me/s/escapefromtarkovEN/6990), [reddit-eft](https://www.reddit.com/r/EscapefromTarkov/).

### Builds par budget & méta

`pages/strategy/meta-builds.html` · Comparer des presets fonctionnels dans EFT et montrer pourquoi ils sont classés.

**Sections :** Critères S–D explicites · Kits budget/intermédiaire/haut de gamme · Compatibilité, marché et disponibilité · Comparaison par scénario de raid.

**Interaction :** Comparateur avec mode, budget saisi, patch de référence et alternative par slot.

**JPG envisagés :** Établi et variantes de preset EFT · Planche comparative ergo/recul du jeu.

**Vérification :** Tester les slots et coûts dans le système de preset du jeu ; noter la date de chaque build.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [patch120](https://store.steampowered.com/news/app/3932890/view/708910525152495848), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [balance-nov](https://t.me/s/escapefromtarkovEN/6990), [reddit-eft](https://www.reddit.com/r/EscapefromTarkov/).


## Phase 9 — SP-Tushonka, Arena et événements

### Single Player Tushonka

`pages/spt-tushonka/index.html` · Choisir entre EFT PvE officiel, Tushonka stable, branche de test et Fika.

**Sections :** Ancienne équipe SPT, arrêt d’infrastructure et successeur communautaire · Matrice build EFT / SPT / runtime et statut stable ou Bleeding Edge · Profils locaux, Forge, mods, Fika et dépannage · Questions fréquentes, possession du jeu et avertissements de version.

**Interaction :** Comparatif de modes, filtre par branche et liens d’installation à la source du projet.

**JPG envisagés :** PMC solo dans un raid fictif · Maquette illustrative du lanceur · Objets évoquant des mods.

**Vérification :** Relever latest et tags, compatibilité de l’installateur et provenance des packages ; pas de lien vers copie du jeu non autorisée.

**Sources cibles :** [spt-build](https://api.github.com/repos/SP-Tushonka/build/releases/latest), [spt-release](https://github.com/SP-Tushonka/build/releases/tag/4.1.6), [spt-be](https://github.com/SP-Tushonka/wiki/blob/main/SPT_50/bleeding-edge-install-instructions.md), [spt-nuget](https://www.nuget.org/packages/SPTushonka.Server.Core/5.0.0-pre.202611061606), [spt-history](https://insider-gaming.com/sp-tarkov-shutting-down-legal-action-battlestate-games/), [spt-transition](https://extraction-compass.com/en/blog/single-player-tarkov-is-back), [forge](https://sp-mod.com/), [fika](https://github.com/project-fika/Fika-Plugin/releases/tag/v2.4.6), [yt-dev](https://youtu.be/w8ro-u_H8-8).

### Installer SP-Tushonka

`pages/spt-tushonka/installation.html` · Suivre la documentation adaptée à une copie légitime sans modifier l’installation live.

**Sections :** Préparer une copie et sauvegarder le profil · Installation recommandée pour la stable ; contrôles de build et runtime · Validation du lancement, erreurs et différence Bleeding Edge.

**Interaction :** Checklist selon la branche et liens directs source par étape.

**JPG envisagés :** Maquette installateur face A · Maquette de vérification après lancement.

**Vérification :** Contrôler jeu installé, canal Steam/BSG, systèmes et version du wiki ; aucun binaire redistribué.

**Sources cibles :** [spt-release](https://github.com/SP-Tushonka/build/releases/tag/4.1.6), [spt-wiki](https://wiki.sp-tushonka.com/en/SPT_4x/Updating_SPT), [spt-be](https://github.com/SP-Tushonka/wiki/blob/main/SPT_50/bleeding-edge-install-instructions.md), [forge](https://sp-mod.com/).

### Mods & The Forge

`pages/spt-tushonka/mods.html` · Choisir des mods selon leur fiabilité et leurs compatibilités déclarées.

**Sections :** Forge et filtre par version · Mods de qualité de vie, IA et autres catégories · Dépendances, sauvegarde et essais contrôlés.

**Interaction :** Filtre stable/BE, catégorie et dernière vérification.

**JPG envisagés :** Atelier de mods illustratif · Diagramme de dépendances entre mods.

**Vérification :** Vérifier chaque fiche auprès du mainteneur ; vieux mods non certifiés comme compatibles.

**Sources cibles :** [forge](https://sp-mod.com/), [spt-release](https://github.com/SP-Tushonka/build/releases/tag/4.1.6), [reddit-tushonka](https://www.reddit.com/r/sptushonka/), [spt-be](https://github.com/SP-Tushonka/wiki/blob/main/SPT_50/bleeding-edge-install-instructions.md).

### Coopératif avec Project Fika

`pages/spt-tushonka/fika.html` · Différencier le jeu local moddé de la coop officielle.

**Sections :** Versions client, serveur et SPT · Principes d’une session privée, profils et mods partagés · Dépannage et limites des tests.

**Interaction :** Matrice des versions et checklist de compatibilité.

**JPG envisagés :** Duo de personnages en raid fictif · Diagramme client/serveur pour un groupe privé.

**Vérification :** Relever les releases côté serveur et client et les incompatibilités ; privilégier réseau privé sécurisé.

**Sources cibles :** [fika](https://github.com/project-fika/Fika-Plugin/releases/tag/v2.4.6), [forge](https://sp-mod.com/), [spt-release](https://github.com/SP-Tushonka/build/releases/tag/4.1.6), [spt-wiki](https://wiki.sp-tushonka.com/en/SPT_4x/Updating_SPT).

### Dépanner SP-Tushonka

`pages/spt-tushonka/troubleshooting.html` · Isoler les problèmes courants sans perdre un profil.

**Sections :** Symptômes et messages de version · Dépendances .NET, logs et conflit mod · Retour à une copie propre et sauvegardes.

**Interaction :** Arbre de diagnostic local avec codes d’erreur connus.

**JPG envisagés :** Journal de lancement illustratif · Guide visuel de profil sauvegardé.

**Vérification :** Vérifier chaque erreur dans la doc du projet ; ne pas inciter à désactiver les protections du système.

**Sources cibles :** [spt-wiki](https://wiki.sp-tushonka.com/en/SPT_4x/Updating_SPT), [spt-release](https://github.com/SP-Tushonka/build/releases/tag/4.1.6), [forge](https://sp-mod.com/), [reddit-tushonka](https://www.reddit.com/r/sptushonka/).

### Escape from Tarkov: Arena

`pages/arena/index.html` · Comprendre les modes, le classement et la synchronisation de ce jeu distinct.

**Sections :** BlastGang, TeamFight et autres modes à la date du patch · Boutique et progression ; transferts par mode · Compétition, entraînement et guides sur les cartes d’Arena · Journal de patchs spécifique, sans importer les annonces Unity d’EFT.

**Interaction :** Onglets par mode et tableau de synchronisation.

**JPG envisagés :** Arène EFT illustrée · Schéma de cycle de manche.

**Vérification :** Contrôler version courante, compétitions et séparations statistiques ; vérification départ Arena, pas EFT.

**Sources cibles :** [arena](https://arena.tarkov.com/news/category/patchnotes), [arena-modes](https://arena.tarkov.com/news/patch-060), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [bsg-social](https://t.me/s/escapefromtarkovEN).

### Événements de Tarkov 2026

`pages/events/index.html` · Distinguer contenus archivés, déploiements durables, événements actifs à la date du relevé et Drops.

**Sections :** Halloween : variantes Infected, quêtes Skier/Therapist et fin annoncée · Blackout, Icebreaker/Boreas, Full Speed Ahead, Wild Woods et Duckov · Kord Breach, récompenses et campagnes de Drops distinctes · Table dates/modes/statut et sources des objectifs.

**Interaction :** Timeline événementielle avec filtres actifs/archives/annoncés et marqueurs de date.

**JPG envisagés :** Infected Factory cinématique · Icebreaker dans le golfe fictif · Entrepôt obscur de Blackout.

**Vérification :** Chercher annonces d’ouverture et clôture, récompenses par mode et événements supplémentaires depuis la phase 0.

**Sources cibles :** [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [halloween](https://x.com/tarkov/status/2122283819667464473), [patch105](https://steamcommunity.com/games/3932890/announcements/detail/703268976281519055), [season-end](https://t.me/s/escapefromtarkovEN/6985), [bsg-social](https://t.me/s/escapefromtarkovEN), [drops](https://store.steampowered.com/news/app/3932890/view/677389277779199054), [market](https://tarkov-market.com/), [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki).


## Phase 10 — Patchs, ressources, glossaire et finalisation

### Notes de patch & chronologie

`pages/patch-notes.html` · Séparer publications, hotfixes et projets de roadmap de novembre 2025 à la version de référence.

**Sections :** Timeline 1.0 → 1.3.0.0 et correctifs officiels postérieurs · Dates, modes, changement principal et impact éditorial justifié · Unity 6 et annonces à distinguer des déploiements · Liens originaux et historique de révision.

**Interaction :** Filtres par période et catégorie, liens de détail et libellés non chromatiques.

**JPG envisagés :** Archives de transmissions du jeu · Frise chronologique illustrée.

**Vérification :** Reconstituer l’archive officielle, vérifier latest et dater les notes sans numéro.

**Sources cibles :** [steam](https://store.steampowered.com/app/3932890/Escape_from_Tarkov/), [steam-news](https://steamcommunity.com/app/3932890/announcements/), [steam-rss](https://store.steampowered.com/feeds/news/app/3932890/?l=english), [bsg-social](https://t.me/s/escapefromtarkovEN), [patch106](https://steamcommunity.com/games/3932890/announcements/detail/708901647665861072), [patch105](https://steamcommunity.com/games/3932890/announcements/detail/703268976281519055), [patch110](https://steamcommunity.com/games/3932890/announcements/detail/686386819418294181), [patch115](https://steamcommunity.com/games/3932890/announcements/detail/712285688032135503), [patch120](https://store.steampowered.com/news/app/3932890/view/708910525152495848), [patch130](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875), [patched](https://patched.gg/games/escape-from-tarkov).

### Ressources & outils

`pages/resources/index.html` · Aider à choisir un outil fiable selon la tâche et la fraîcheur des données.

**Sections :** Données, cartes, économie, suivi de progression · Chaînes, forums et communautés ; critères, langue et statut · Crédits, licences, méthodologie et mentions de fan-site.

**Interaction :** Filtres par usage et par niveau de confiance, liens externes vérifiés.

**JPG envisagés :** Dossier d’outils du joueur · Illustration de table de briefing.

**Vérification :** Tester liens, licences, auteur des cartes et annonces Discord/YouTube ; ne pas copier les ressources protégées.

**Sources cibles :** [tdev](https://json.tarkov.dev/endpoints), [mapgenie](https://mapgenie.io/tarkov), [market](https://tarkov-market.com/), [tracker](https://tarkovtracker.io), [tarkovhead](https://www.tarkovhead.com/en), [kappaguide](https://kappaguide.com/maps), [reddit-eft](https://www.reddit.com/r/EscapefromTarkov/), [forum](https://forum.escapefromtarkov.com/), [forge](https://sp-mod.com/), [yt-dev](https://youtu.be/w8ro-u_H8-8).

### Glossaire EFT

`pages/resources/glossary.html` · Donner au moins 200 entrées bilingues pour lire le jeu et ses guides.

**Sections :** Abréviations, économie et progression · Argot de communauté, modes et cartes · Munitions nommées, objets et accessoires du jeu · Liens contextuels et variantes de traduction.

**Interaction :** Recherche sans accents, regroupement A–Z et ancres par terme.

**JPG envisagés :** Lexique annoté de Tarkov · Radio et carnet de raid fictifs.

**Vérification :** Recouper les sens variables et éviter de présenter le jargon communautaire comme officiel.

**Sources cibles :** [wiki](https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki), [tdev](https://json.tarkov.dev/endpoints), [steam](https://store.steampowered.com/app/3932890/Escape_from_Tarkov/), [reddit-eft](https://www.reddit.com/r/EscapefromTarkov/), [tracker](https://tarkovtracker.io).
