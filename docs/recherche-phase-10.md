# Recherche PHASE_10 — 18 novembre 2026

## Périmètre et méthode

Relecture réalisée pour les routes « Notes de patch & chronologie », « Ressources & outils » et « Glossaire EFT ». Les informations officielles, les outils communautaires et les discussions de joueurs sont séparés. Les chiffres de build rapportés uniquement par un wiki, les prix volatils et les promesses de feuille de route ne sont pas présentés comme état du client.

Les pages BSG, Steam, MapGenie, Tarkov.dev, Tarkov Market, TarkovTracker, TarkovHead, KappaGuide et certains dépôts ont renvoyé une erreur de récupération directe dans l’outil. Les extraits du moteur de recherche ont été comparés aux liens primaires et, quand possible, aux publications officielles X/Telegram, Steam et GitHub. Un extrait de recherche n’est pas assimilé à une lecture intégrale. Les liens originaux sont fournis dans le registre `docs/sources.json` et dans les pages.

## Chronologie officielle — repères retenus

- **15 novembre 2025 — version 1.0** : BSG avait annoncé cette date dans son communiqué de lancement du 22 août; la fiche Steam la donne comme date de sortie. La date du communiqué n’est pas la date du lancement.
- **1er décembre 2025 — 1.0.0.2**; **11 décembre — 1.0.0.5**; **23 décembre — notes 1.0.1.0** (annonce de maintenance/installation officielle le 24 décembre). L’index officiel BSG fournit les dates des notes; la version 1.0.0.5 fait passer la saison en hiver et comporte des correctifs.
- **10 février 2026 — 1.0.2.0** : présence Steam Rich Presence, modifications du lancement des serveurs de raid, changements et correctifs publiés par BSG.
- **5 mars — 1.0.2.5** : notes officielles et annonce BSG; changements techniques et d’équilibrage, notamment sur les accessoires d’armes.
- **1.0.4.0** : note affichée le 26 mars, installation annoncée le 27 mars. **1.0.4.5** : note affichée le 19 avril, installation annoncée le 20 avril. Cette différence d’un jour entre date de page et annonce de déploiement est conservée au lieu d’être effacée.
- **19 mai — 1.0.4.9** : l’installation terminée est signalée par le compte BSG; les détails de la note n’ont pas été récupérés dans cette revue et ne sont pas résumés. **25 mai — 1.0.5.0** (Icebreaker et chapitre Boreas, lieu séparé de 1 à 3 joueurs contre l’IA, sans matchmaking aléatoire); **3 juillet — 1.0.6.0**.
- **3 août — 1.1.0.0** : Season 1 / personnage Seasonal; **1.1.5.0** : note BSG datée du 7 septembre et index/annonce le 8 septembre, refonte Lighthouse et accès à Icebreaker depuis Lighthouse/Shoreline via Sudak-tudak; **15 septembre — 1.1.5.1** : Leagues pour personnages Seasonal (annonce Steam BSG).
- **6 octobre — 1.2.0.0**; **29 octobre — 1.3.0.0**. Le flux officiel distingue EFT de Tarkov Arena.
- **12 novembre — équilibrage BSG sans numéro de patch** : changements de tâches/modes, Black Division et Wedge; les valeurs non publiées ne sont pas inventées.
- **13 novembre — mise à jour technique confirmée par le canal Telegram officiel BSG, sans numéro de version dans le message consulté**.
- **18 novembre — journal BSG sur 1.3.5.0** : l’article original BSG a été récupéré directement le 18/11. Il prévoit la mise à jour pour la seconde moitié de novembre, sans jour précis ni annonce d’installation. BSG annonce Unity 6, la connexion au serveur en parallèle du chargement de carte, la libération de RAM après raid, une stabilité serveur accrue, l’amélioration de l’enregistrement des impacts et la réduction des pertes de paquets, une meilleure fluidité et une reconnexion rapide. Au contrôle direct du même jour, l’index officiel des patch notes affichait encore 1.3.0.0 (29/10) en dernière note numérotée; le fil officiel Steam montrait le journal développeur comme annonce, pas une installation. Cela ne constitue ni une lecture du Launcher ni une preuve du build client. Ne pas qualifier 1.3.5.0 de déployée ou installée. DirectX 12, DLSS Frame Generation x2/x4 et NVIDIA Reflex sont des travaux futurs; la végétation est reportée et FSR 4 est visé avant fin 2026.

L’index BSG consulté liste encore 1.3.0.0 comme dernière note numérotée publiée au 18 novembre. Le wiki communautaire rapporte les sous-builds 1.3.0.1/1.3.0.2, mais ils ne sont pas attribués à BSG : le message officiel du 13 novembre ne donne pas de numéro. Les pages publiques disent donc « dernière note numérotée visible sur l’index BSG », et non « version installée la plus récente ». La veille n’a pas fourni de vidéo YouTube récente, vérifiable et directement liée au journal du 18 novembre; les discussions Reddit/X obtenues ne remplacent pas la source officielle et sont antérieures ou de portée différente.

## Ressources et limites constatées

- **Officiel** : site BSG, index de notes, Steam News/RSS, X, Telegram et chaîne YouTube BSG. Une publication sur un forum officiel reste un message communautaire, pas automatiquement une règle du jeu. Patchs EFT et Arena ne sont pas interchangeables.
- **Tarkov.dev** : service et données communautaires. Les endpoints JSON `json.tarkov.dev` sont le point d’entrée à privilégier pour les données structurées publiques; un incident GitHub du projet indique que l’ancien GraphQL `api.tarkov.dev` était indisponible en juillet 2026. Les exports et caches ne prouvent ni l’état live du client, ni l’accès d’un profil, ni la disponibilité d’une extraction.
- **TarkovTracker** : le projet actif se présente désormais sous `tarkovtracker.org`, avec dépôts et activité GitHub en novembre 2026. La documentation de l’équipe indique que `tarkovtracker.io` est l’ancienne instance non maintenue. Les possibilités de compte, synchronisation et import dépendent de l’outil; l’état du site peut changer.
- **MapGenie** : outil cartographique non officiel; filtres, couches, cartes et contenus payants peuvent varier. Des discussions communautaires de 2026 expriment des avis divergents sur la fraîcheur de certains marqueurs. Ne pas le qualifier d’exhaustif ou d’actuel sans vérifier chaque carte et chaque repère en raid.
- **Tarkov Market** : estimation/indication communautaire de prix; les cours bougent et ne constituent pas des prix garantis dans le client. Aucun cours n’est publié dans le guide.
- **Wiki Fandom** : projet tenu par des bénévoles malgré le libellé « Official » de son nom. La page communautaire annonce une licence CC BY-NC-SA sauf mention contraire. Ne pas réutiliser ses textes, cartes ou images sans respecter la licence et vérifier les données sensibles au patch.
- **TarkovHead, KappaGuide, Reddit, forums et vidéos de créateurs** : outils de repérage et d’explication, pas de source de vérité. Dater chaque contribution, remonter aux notes BSG, vérifier le mode et ne pas traiter une expérience de joueur comme une règle universelle.
- **The Forge** : catalogue communautaire propre à SP-Tushonka; présence d’un mod ne prouve ni compatibilité avec toutes les branches ni approbation BSG.

Les logiciels compagnons, overlays, lecteurs de journaux ou d’images restent tiers. Leur statut de sécurité ou leur compatibilité avec les règles BSG n’est pas garanti ici; ne jamais fournir ses identifiants de compte à un outil non vérifié.

## Glossaire

Le glossaire associe plus de 200 termes anglais et équivalents français. Les termes dont le sens vient de la communauté (par exemple *rat*, *chad*, *meta* ou *head-eyes*) sont étiquetés comme argot, et non comme vocabulaire officiel. Les définitions de progression, d’équipement et de modes restent qualitatives lorsque la mécanique peut varier selon le patch.
