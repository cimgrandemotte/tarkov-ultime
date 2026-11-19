# Vérifications · PHASE 4 — Cartes

**Relevé du 18 novembre 2026.** Préparation éditoriale, pas un test du client EFT : aucun écran de sélection, menu d’extraction, raid, prix, accès ou disponibilité en direct n’a été vérifié. Les pages publiées doivent dater leurs données et séparer le fait officiel, le relevé communautaire, le conseil éditorial et l’état en raid. `[CONFIRME]` ne s’applique qu’au fait explicitement attesté par la source indiquée ; `[COMMUNAUTAIRE]` n’est pas une règle de Battlestate Games ; `[A_REVALIDER]` signifie que l’interface en raid fait foi.

## Hiérarchie des sources et méthode

1. **Notes BSG Steam** pour les changements de patch : [1.0.5.0](https://steamcommunity.com/games/3932890/announcements/detail/703268976281519055), [1.1.5.0](https://steamcommunity.com/games/3932890/announcements/detail/712285688032135503), [1.2.0.0](https://store.steampowered.com/news/app/3932890/view/708910525152495848). Elles décrivent des changements précis, pas un tableau exhaustif des sorties actives dans chaque profil.
2. **Tarkov.dev JSON** : [endpoints](https://json.tarkov.dev/endpoints), puis exports `regular/maps`, `pve/maps` et `pvp-season/maps`. Le snapshot local est `data/snapshots/cartes-2026-11-18.json`, collecté le **18/11 à 12:20:26 UTC (13:20:26 Paris)**. Il n’embarque pas de build client et ne prouve ni l’ouverture d’une carte au compte, ni une extraction active dans le raid.
3. **Wiki communautaire EFT hébergée sur Fandom** : [index des lieux](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov) et pages dédiées des 13 cartes (voir `docs/sources.json`). Utile pour noms, repères, tableaux d’extractions et conditions rapportées ; peut diverger d’un patch, d’un mode ou de l’interface actuelle.
4. **Cartes et guides tiers** : MapGenie consulté (12 cartes, sans Terminal, certaines couches PRO), TarkovTracker et guides vidéo. Ils sont des pistes d’orientation seulement. Le PR [TarkovTracker #1401](https://github.com/tarkovtracker-org/TarkovTracker/pull/1401) rappelle que les JSON publics ne suffisent pas pour restituer toutes les exigences, coûts, hauteurs, états de mode ou disponibilités live ; ses captures de novembre sont datées et ne sont pas un flux en raid.

**Conception éditoriale :** ne reprendre aucun fond, tuile ou coordonnée tierce. Les visuels du guide sont des illustrations originales, pas des captures ni des plans de jeu. Un schéma produit par le guide devra porter « schéma indicatif, non à l’échelle » et ne jamais se faire passer pour une carte de navigation vérifiée.

## Veille officielle et communautaire du 18 novembre

- **Battlestate Games, journal technique du 18/11** ([article officiel](https://www.escapefromtarkov.com/news/id/420)) : 1.3.5.0 est prévue pour la seconde moitié de novembre, sans jour précis, avec migration Unity 6 et objectifs de chargement/reconnexion, stabilité et performance. Cela n’atteste pas que 1.3.5.0 soit installé. DirectX 12, Frame Generation/DLSS, Reflex, FSR 4 et les changements de végétation sont des travaux ultérieurs ou reportés, pas des fonctions live attestées par cette page. Aucun changement d’extraction n’y est annoncé.
- **Battlestate Games, message du 12/11** ([canal EN](https://t.me/s/escapefromtarkovEN/6990)) : il ne donne **aucun numéro de patch**. En Seasonal, l’apparition de Black Division est réglée à 100 % sur les lieux concernés, les récompenses de tâches opérationnelles incluent davantage de kits Sudak-tudak, et la liste Seasonal d’Icebreaker reçoit davantage de documents Battle Pass. Les documents médicaux du Battle Pass sont indiqués comme disponibles sur Icebreaker. Tous modes, la réaction, la précision et la santé des parties du corps de The Wedge et de ses gardes baissent et leurs munitions changent. Le message ne publie pas de tableau de spawn par carte ni de taux de butin par raid ; ne pas attribuer ces changements à 1.3.0.1/1.3.0.2 sur la seule base du changelog communautaire.
- **Vidéos communautaires, 12–13/11** ([12/11](https://www.youtube.com/watch?v=eTDtCdLF69Y), [13/11](https://www.youtube.com/watch?v=Menwvj4YT7Q)) : les auteurs présentent des tirs à travers la fumée comme une interaction non prévue de vision IA et mentionnent des échecs de reproduction. Ces vidéos ne constituent pas une preuve indépendante ou un test stable ; la fiche ne recommande pas cette exploitation. Le guide de joueur du 04/11 sur Wedge précède l’équilibrage BSG du 12/11 et ses chiffres ne sont pas repris comme règle actuelle.
- **Recontrôle Tarkov.dev le 18/11 vers 16 h Paris** : un téléchargement frais des six exports de cartes (`regular`, `pve`, `pvp-season`, avec traductions) donne les mêmes 19 enregistrements, mêmes champs résumés par carte et mêmes compteurs d’ennemis que `data/snapshots/cartes-2026-11-18.json` ; aucun delta de carte n’est constaté. Snapshot inchangé : son horodatage reste 12:20:26 UTC ; il ne constitue pas un état du client.
- **Pistes communautaires** : Reddit direct renvoie HTTP 403 pour le fil consulté ; les recherches Reddit ciblées n’apportent pas de preuve exploitable. GitHub distingue `sayser/TarkovTracker` (cartographie/suivi) de `tarkovtracker-org/TarkovTracker` (progression/quêtes). L’endpoint public documente `regular`, `pve` et `pvp-season`; l’export direct `regular/maps` a aussi répondu HTTP 403 lors d’une consultation antérieure. Ces outils ne remplacent pas l’écran d’extraction du client.

## Inventaire technique — ne pas confondre lieux et variantes

Le snapshot contient **19 enregistrements de cartes par mode**, dont les **13 lieux principaux** répertoriés par le wiki. Les six enregistrements supplémentaires sont des variantes : Night Factory, Ground Zero 21+, Ground Zero Tutorial, The Lab (Dark), Infected Lab et Infected Factory. Ce ne sont pas six nouveaux lieux principaux.

Les nombres **48 regular, 50 PvE et 51 PvP Seasonal** dans le snapshot désignent `mobRecordsCount`, pas des nombres de cartes ni des boss uniques. `bossEntries` inclut des entrées de variantes et d’ennemis ; aucun de ces compteurs ne doit devenir une statistique éditoriale de « boss uniques » ou de taux de spawn.

| Lieu canonique | `players` / `raidDuration` Tarkov.dev | `extractEntries` regular / PvE / Seasonal | Réserve de rédaction |
|---|---:|---:|---|
| Factory | 7–8 / 20 min | 10 / 10 / 10 | Night Factory reste une variante à part : 5–6 joueurs, 25 min, 9 entrées dans chaque export. |
| Customs | 10–12 / 35 min | 28 / 28 / 28 | Patch officiel 1.2.0.0 : sorties PMC/Scav ajustées et nouvelles sorties ajoutées, sans leurs noms dans la note. Ne pas figer une liste héritée. |
| Woods | 10–14 / 35 min | 20 / 20 / 20 | Aucun état d’extraction actif disponible dans le snapshot. |
| Shoreline | 10–14 / 45 min | 19 / 19 / 19 | Ne pas confondre sorties et transits vers d’autres lieux. |
| Interchange | 11–15 / 40 min | 9 / 9 / 9 | Patch 1.2.0.0 : nouveautés de loot et corrections géométriques ; la note ne donne pas une liste d’extractions. |
| Reserve | 9–11 / 40 min | 11 / 11 / 11 | Déclencheurs et limitations PMC/Scav à vérifier dans le raid. |
| The Lab | 8–10 / 30 min | 7 / 7 / 7 | Une entrée d’export n’est pas une garantie d’accès ; accès par carte selon la wiki. |
| Lighthouse | 10–12 / 40 min | 12 / 12 / 12 | Refonte officielle 1.1.5.0 ; le transit Icebreaker est distinct d’une extraction de retour au stash. |
| Streets of Tarkov | 12–16 / 40 min | 19 / 19 / 19 | PR cartographique tiers : les hauteurs et coordonnées ne sont pas toutes des relevés de terrain indépendants. |
| Ground Zero, groupe débutant | 9–10 / 30 min | 9 / 9 / 9 | La wiki décrit le seuil <21 ; ne pas étendre cette règle à chaque profil sans confirmation client. |
| Ground Zero, groupe expérimenté | 9–12 / 30 min | 6 / 6 / 6 | Variante distincte 21+ dans le flux ; les champs de niveau API ne sont pas la preuve de la règle de matchmaking. |
| The Labyrinth | API : 5–5 / 30 min ; wiki : 1–5 | 2 / 2 / 2 | **Contradiction de taille de groupe** ; ne publier aucune plage avant revalidation dans le client. |
| Icebreaker | 1–3 / 50 min | 1 / 1 / 1 | Taille/durée recoupées par BSG ; l’unique entrée d’extraction ne suffit pas à nommer une sortie live. |
| Terminal | API : 1–5 / 50 min ; wiki : 1–5 / 45 min | 0 / 0 / 0 | **Durée contradictoire (50/45)** et zéro entrée d’extraction dans le JSON malgré un Zubr rapporté par l’entretien/wiki. Ne pas convertir le zéro API en « aucune sortie ». |

Pour chacun des 13 lieux canoniques, les champs `players`, `raidDuration` et le nombre brut d’entrées d’extraction du snapshot sont identiques entre `regular`, `pve` et `pvp-season`. Cela **ne prouve pas** que les sorties, coûts, exigences, horaires, accès ou états en raid soient identiques. L’API ne fournit pas la matrice live recherchée.

### Variantes à maintenir à part

- **Ground Zero Tutorial** : 9–12 / 30 min et 0 entrée d’extraction dans chacun des exports. Ne pas compter comme lieu principal ni comme preuve qu’un tutoriel est accessible à tous les profils.
- **The Lab (Dark)** : 8–10 joueurs ; 30 min en regular et Seasonal, 35 min en PvE ; 0 entrée d’extraction.
- **Infected Lab** : 8–10 joueurs ; 30 min en regular/Seasonal, 25 min en PvE ; 0 entrée d’extraction.
- **Infected Factory** : 4–6 joueurs ; 20 min en regular/Seasonal, 15 min en PvE ; 0 entrée d’extraction.
- Les règles d’événement et de matchmaking peuvent changer. Une variante d’API ne prouve pas qu’elle est actuellement sélectionnable.

## Bosses — relevé communautaire distinct des compteurs API

La page [EFT Wiki — Bosses](https://escapefromtarkov.fandom.com/wiki/Bosses) a été relue le 18/11/2026. Le tableau ci-dessous ne fait que restituer les lieux qu’elle associe aux noms; ce n’est ni une confirmation BSG, ni une disponibilité par mode, variante, patch ou raid. Les taux de présence sont volontairement omis.

| Lieu | Boss réguliers nommés par la page communautaire | Mention d’événement séparée |
|---|---|---|
| Ground Zero | Aucun boss de carte régulière listé dans la table consultée | Santa Claus listé pour Ground Zero 21+ |
| Customs | Big Pipe, Birdeye, Knight, Partisan, Reshala | Santa Claus |
| Factory | Tagilla | Santa Claus |
| Woods | Big Pipe, Birdeye, Knight, Partisan, Shturman | Santa Claus |
| Shoreline | Big Pipe, Birdeye, Knight, Partisan, Sanitar | Santa Claus |
| Interchange | Killa, Tagilla | Santa Claus |
| Reserve | Glukhar | Santa Claus |
| The Lab | Aucun boss de carte régulière listé dans la table consultée | Aucune mention retenue |
| Lighthouse | Big Pipe, Birdeye, Knight, Partisan, Zryachiy | Santa Claus |
| Streets of Tarkov | Kaban, Kollontay | Santa Claus |
| The Labyrinth | Shadow of Tagilla, Vengeful Killa | Aucune mention retenue |
| Icebreaker | The Wedge, Knight | Aucune mention retenue |
| Terminal | Glukhar, Killa, Reshala, Sanitar, Tagilla | Aucune mention retenue |

Cette liste est un résumé de lieu de la page communautaire, pas un inventaire complet des menaces; le groupe des Rogues/guards est visible dans la source mais n’est pas recompté ici. L’événement peut être inactif ou varier par mode. Les valeurs `mobRecordsCount` et `bossEntries` de Tarkov.dev ne sont jamais interprétées comme des nombres de cartes ou de boss uniques; elles ne produisent ni le tableau ci-dessus ni un taux de spawn.

## Accès, extractions et transitions par lieu

| Lieu | État sourcé au relevé | Ce que la fiche peut affirmer | Ce qu’elle ne doit pas prétendre |
|---|---|---|---|
| **Factory** | Wiki communautaire : table de sorties PMC/Scav et de transits ; exemples relevés : Gate 3, Gate 0, Camera Bunker Door, Office Window, Cellars/Med Tent sous clé, et Smugglers’ Passage conditionnel. | Donner quelques exemples avec faction/condition et un avertissement « noms et état à contrôler sur l’écran d’extraction ». Night Factory est une variante. | Que toutes ces options sont actives pour le profil ou raid courant ; reprendre la table comme une règle BSG. |
| **Customs** | `[CONFIRME · BSG 1.2.0.0]` les extractions PMC et Scav ont été ajustées et de nouvelles ajoutées ; la note ne les énumère pas. Discussion Reddit du 09/10 et REƎMR sur X divergent sur des noms/conditions. | Alerte de révision récente, puis consultation de la liste du raid. Cartographier les repères sans valider de sortie par faction. | Publier comme officiel Railroad to Reserve, Reserve Checkpoint, Old Gas Station ou RUAF sur la seule base des posts ; garantir tarif, faction ou activation. |
| **Woods** | Wiki communautaire : limites, mines/snipers, sorties et secteurs de scierie. La ligne ZB-014 la liste PMC, associe une clé ZB-014 et indique « Green flares = Open » ; le relevé ne prouve pas que ces deux conditions se cumulent. Snapshot : 10–14 / 35 et 20 entrées. | Expliquer repérage et dangers signalés ; pour ZB-014, mentionner la clé et le signal comme rapportés, puis faire confirmer leurs conditions dans le raid. | Inventer des coordonnées ou inférer disponibilité depuis les 20 entrées ; transformer la note de wiki en règle BSG. |
| **Shoreline** | Wiki : Resort, côte et progression via Tour/direct selection selon page consultée ; accès Terminal/Labyrinth/Icebreaker conditionnel. Patch 1.1.5.0 confirme Lighthouse → Icebreaker ; la wiki décrit aussi Shoreline → Icebreaker. | Identifier les embranchements avec leur niveau de preuve ; préciser que transit et sortie finale ne sont pas synonymes. | Présenter horaires/objet d’accès aux destinations comme une règle BSG générale sans test client. |
| **Interchange** | Wiki : Saferoom, Power Station et autres extractions conditionnelles. Patch 1.2.0.0 : changements de loot et géométrie, pas de tableau exhaustif d’extractions. | Décrire la logique des conditions à titre communautaire ; vérifier l’état et l’alimentation en raid. | Afficher un coût statique ou une liste exhaustive comme actuelle. |
| **Reserve** | Wiki et trackers tiers décrivent bunker, train, sorties conditionnelles et limitations de profil. Le PR #1401 signale plusieurs exigences non présentes dans le JSON public. | Expliquer les familles de conditions et diriger vers le contrôle en raid. | Déduire les exigences complètes, un coût ou une disponibilité du seul JSON/API. |
| **The Lab** | Wiki : accès par carte d’accès ; la page répertorie portes et sorties activables. Le snapshot contient 7 entrées par mode. | Avertir de préparer l’accès ; distinguer porte de butin et sortie ; afficher aucune tarification dynamique. | Confondre The Lab avec The Lab (Dark) ou Infected Lab ; prétendre que l’API confirme l’accès du compte. |
| **Lighthouse** | `[CONFIRME · BSG 1.1.5.0]` Rogues déplacés vers les chalets ; armes fixes et mines retirées de la station de traitement de l’eau seulement ; route principale couverte et itinéraires retravaillés ; BTR avec parcours multiples, passages souterrains ; transit Icebreaker au quai des maisons d’eau. | Dater la refonte et circonscrire exactement le retrait des mines à la station. | Étendre « mines retirées » à Lighthouse entier ou figer la route aléatoire du BTR. |
| **Streets of Tarkov** | Wiki et cartographie communautaire ; export 12–16 / 40 et 19 entrées. Aucun contrôle d’élévation en jeu. | Donner des repères de quartier et rappeler les étages ; tout dessin de ce guide est schématique. | Faire croire qu’un marqueur/une flèche tiers ou généré indique une coordonnée certifiée. |
| **Ground Zero** | Wiki communautaire : matchmaking débutant <21 / expérimenté 21+ ; groupe évalué par son membre de plus haut niveau. Le tableau page mentionne notamment Emercom, Mira Ave (fusée verte), Nakatani Basement Stairs et Police Cordon V-Ex. | Séparer variantes et présenter des exemples d’extraction datés, sans prix ; avertir que la règle de niveau/mode n’a pas été testée. | Généraliser les seuils au PvE, Seasonal, tutoriel ou à tout le groupe sans vérifier l’interface. Les tarifs, même vus dans une PR, peuvent varier. |
| **The Labyrinth** | Wiki communautaire : transit depuis le sous-sol de l’aile ouest du Resort ; Knossos LLC facility key pour la porte et Labrys access keycard pour le transit. API/wikis divergent sur le nombre de joueurs. | Indiquer ces conditions comme « wiki, à confirmer », signaler les pièges et l’assurance rapportée comme points de risque. | Confirmer accès, groupe, sorties ou règles d’assurance comme universels ou officiels. |
| **Icebreaker** | `[CONFIRME · BSG 1.0.5.0]` lieu séparé de 1–3 joueurs, dans tous les modes officiels, contre l’IA, seul ou en groupe, sans matchmaking aléatoire. `[CONFIRME · BSG 1.1.5.0]` accès depuis Shoreline et Lighthouse ; roubles remplacés par un kit marin « Sudak-tudak » à usage unique. `[CONFIRME · BSG, 12/11 sans numéro de patch]` documents médicaux du Battle Pass disponibles sur Icebreaker ; davantage de documents Battle Pass dans la liste Seasonal d’Icebreaker ; The Wedge et ses gardes affaiblis et munitions modifiées dans tous les modes. La même annonce règle l’apparition Seasonal de Black Division à 100 % sur les lieux concernés, sans fournir ici un taux propre à Icebreaker. La wiki ajoute progression Boreas/Stick to It et déverrouillage de sélection directe. | La qualifier de carte PvE-orientée, pas d’exclusive PvE. Dater les changements du 12/11 séparément des numéros de patch ; ne promettre ni récompense ni spawn par raid et distinguer le détail wiki. | Reprendre les anciens tarifs en roubles, garantir l’accès direct ou une récompense de Battle Pass identique dans chaque mode/raid, attribuer le taux Black Division à Icebreaker sans source par carte, ou assimiler au PvE Zone. |
| **Terminal** | Entretien développeur publié par 80 Level le 16/11, consulté auparavant : aboutissement de campagne, transit Shoreline à fenêtre limitée, Zubr décrit comme issue. La wiki rapporte 21:00–06:00 et item à l’intercom. Direct fetch de l’article 80 Level le 18/11 : 404. API : 50 min/0 extraction ; wiki : 45 min et Zubr. | Avertir des spoilers ; marquer accès et sortie comme rapportés par entretien/wiki, durée non résolue. Reprendre la source d’entretien avec réserve de disponibilité de l’URL. | Affirmer que `extractEntries=0` signifie aucune sortie, ou que la fenêtre et l’objet sont une règle de patch vérifiée dans tous les modes. |

### Transits publiés — 29 liens directionnels relevés, couverture partielle

Les tables de transit des dix pages communautaires indiquées ci-dessous ont été relues le 18/11/2026 ; la note BSG 1.1.5.0 confirme spécifiquement les deux accès à Icebreaker. Les flèches transcrivent une direction indiquée par la source, pas un aller-retour. Les mentions d’une minute, d’un objet ou d’une fenêtre restent des informations rapportées : aucune présence, disponibilité, limite de profil ou règle de raid n’a été testée dans le client.

| Origine → destination | Provenance | Réserve éditoriale |
|---|---|---|
| Factory → Customs | Wiki Factory | Transit partagé, après 1 min selon la table. |
| Factory → The Lab | Wiki Factory | Transit PMC ; carte d’accès The Lab par joueur indiquée ; détails non testés. |
| Factory → Woods | Wiki Factory | Transit partagé, après 1 min selon la table. |
| Customs → Factory | Wiki Customs | Transit partagé, après 1 min selon la table. |
| Customs → Interchange | Wiki Customs | Transit partagé, après 1 min selon la table. |
| Customs → Reserve | Wiki Customs | Transit partagé, après 1 min selon la table. |
| Customs → Shoreline | Wiki Customs | Transit partagé, après 1 min selon la table. |
| Ground Zero → Streets of Tarkov | Wiki Ground Zero | Transit partagé, après 1 min selon la table. |
| Interchange → Customs | Wiki Interchange | Transit partagé, après 1 min selon la table. |
| Interchange → Streets of Tarkov | Wiki Interchange | Transit partagé, après 1 min selon la table. |
| The Lab → Streets of Tarkov | Wiki The Lab | Transit rapporté après 1 min ; point près du dôme orange selon la page. |
| Lighthouse → Icebreaker | BSG 1.1.5.0 | Accès confirmé depuis Lighthouse ; kit marin à usage unique confirmé. |
| Lighthouse → Reserve | Wiki Lighthouse | Transit partagé, après 1 min selon la table. |
| Lighthouse → Shoreline | Wiki Lighthouse | Transit partagé, après 1 min selon la table. |
| Lighthouse → Woods | Wiki Lighthouse | Transit partagé, après 1 min selon la table. |
| Reserve → Customs | Wiki Reserve | Transit partagé, après 1 min selon la table. |
| Reserve → Lighthouse | Wiki Reserve | Transit partagé, après 1 min selon la table. |
| Reserve → Woods | Wiki Reserve | Transit partagé, après 1 min selon la table. |
| Shoreline → Icebreaker | BSG 1.1.5.0 | Accès confirmé depuis Shoreline ; kit marin à usage unique confirmé. |
| Shoreline → The Labyrinth | Wiki Shoreline / Labyrinth | Sous-sol de l’aile ouest du Resort ; clés Knossos et Labrys rapportées, non testées. |
| Shoreline → Lighthouse | Wiki Shoreline | Transit partagé, après 1 min selon la table. |
| Shoreline → Terminal | Wiki Terminal | La page rapporte une fenêtre 21 h–6 h, un délai et un objet présenté à l’intercom ; non testés. |
| Streets of Tarkov → Ground Zero | Wiki Streets | Transit partagé, après 1 min selon la table. |
| Streets of Tarkov → Interchange | Wiki Streets | Transit partagé, après 1 min selon la table. |
| Streets of Tarkov → The Lab | Wiki Streets | Transit PMC ; carte d’accès The Lab par joueur rapportée, non testée. |
| Woods → Customs | Wiki Woods | Transit partagé, après 1 min selon la table. |
| Woods → Factory | Wiki Woods | Transit partagé, après 1 min selon la table. |
| Woods → Lighthouse | Wiki Woods | Transit partagé, après 1 min selon la table. |
| Woods → Reserve | Wiki Woods | Transit partagé, après 1 min selon la table. |

Le graphe livré est limité aux lignes relevées dans ces pages et n’affirme pas qu’aucune autre transition n’existe. Il ne transcrit pas une carte, des coordonnées ou un itinéraire à l’échelle. **Un transit n’est pas une extraction vers la planque** ; un graphe exhaustif et l’état du raid exigeraient une vérification client datée.

## Décisions de publication des 14 routes

- Afficher **13 lieux principaux** ; conserver les six variantes de snapshot dans un encart distinct, non dans le compte des cartes.
- Dans le comparateur, préciser « données Tarkov.dev du 18/11/2026 » et nommer les colonnes `players` / `raidDuration` en tant que **métadonnées d’export**. Ne pas étiqueter `extractEntries` comme nombre de sorties disponibles.
- Le hub peut filtrer par mode d’export, mais explique que les 13 entrées apparaissent dans chaque export et que cela ne prouve pas disponibilité/accessibilité. Afficher les écarts connus pour les variantes, pas des fausses différences de mode des cartes principales.
- Les fiches détaillent d’abord les repères, chemins d’apprentissage, types de sorties conditionnelles et transits établis. Les listes de noms venant du wiki portent leur provenance et date ; pour Customs, ne pas figer les sorties ajoutées en 1.2.0.0.
- Conserver quatre niveaux de preuve : `[CONFIRME · BSG]`, `[DONNÉES · Tarkov.dev]`, `[COMMUNAUTAIRE · Wiki/outil]`, `[À VÉRIFIER EN RAID]`. Aucun coût, prix live, état de bouton, pourcentage de spawn ou accès de compte n’est inventé.
- **Pas de client/modes testés** : `client_et_modes_testes: false`. La validation P4 couvre l’accessibilité et le fonctionnement du comparateur web, pas le jeu.

## Contrôle de livraison du 18 novembre 2026

La publication a été vérifiée sur l’aperçu local : **17 routes canoniques**, sitemap, 43 entrées de recherche, 29 transits, images et ancres ; les routes prévues pour les phases ultérieures restent absentes. Les validations statiques `python3 scripts/check_phase2.py --artefacts-seuls` et `python3 scripts/check_phase3.py --phase4 --artefacts-seuls` passent.

- **Chromium 159.0.8154.6** : 13 groupes de tests, cinq audits axe-core sans violation ; les états incomplets à examiner manuellement ne sont pas des violations. Le reflow 320–1 440 px et le texte agrandi à 200 %, les couleurs système, le clavier, le tactile et le repli sans JS passent.
- **Firefox 159.0** : sept contrôles, aucune erreur, y compris filtres, comparateur, navigation clavier et reflow 320–1 440 px.
- **Contraste** : 20 profils de heroes, minimum texte 5,10:1 ; minimum des huit paires de palette 8,82:1. Cette mesure n’est pas une certification complète.
- **Performance mobile simulée** : LCP 1 540 ms / CLS 0 pour le hub ; 1 268 ms / CLS 0 pour Icebreaker, sous RTT 100 ms, débit 4 Mbit/s et CPU ×4.

Résultats détaillés : `data/snapshots/validation-phase-4.json`, `data/snapshots/validation-phase-4-firefox.json` et `data/snapshots/contraste-phase-4.json`. Le bilan éditorial et la transition d’état sont dans `docs/phase-4.md`.
