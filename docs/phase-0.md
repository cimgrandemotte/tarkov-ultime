# TARKOV ULTIMATE GUIDE

## Phase 0 · Initialisation et planification

**Terminée le 18 novembre 2026 · 87 pages prévues · En attente de `CONTINUE`**

L’arborescence, la machine à états et le plan par page sont en place. Cette livraison prépare le site : aucune page HTML, illustration ou piste audio n’a encore été produite. Les fondations commencent en phase 1 ; l’accueil et sa prévisualisation arrivent en phase 2.

### Ce que la vérification change

| Sujet | Décision éditoriale |
|---|---|
| **Patch de référence** | La [note Battlestate Games du 29 octobre](https://steamcommunity.com/games/3932890/announcements/detail/719046160957833875) confirme **1.3.0.0**. Unity 6 est annoncé pour **1.3.5.0**, mais aucun déploiement de ce patch n’a été trouvé dans les canaux officiels consultés au 18 novembre. Les [équilibrages de novembre](https://t.me/s/escapefromtarkovEN/6990) seront traités séparément. |
| **Cartes** | Le guide passe de 12 à **13 emplacements principaux** avec [Terminal](https://t.me/s/escapefromtarkovEN/7001). Les variantes jour/nuit, tutoriel et événement restent rattachées à leur contexte ; elles ne gonflent pas ce total. |
| **Icebreaker** | La carte et le chapitre *Boreas* ont été introduits le **25 mai 2026**, au [patch 1.0.5.0](https://steamcommunity.com/games/3932890/announcements/detail/703268976281519055). C’est une expédition contre l’IA accessible depuis les modes officiels, pas une exclusivité du profil PvE Zone. |
| **SP‑Tushonka** | La [stable 4.1.6](https://github.com/SP-Tushonka/build/releases/tag/4.1.6) cible EFT `0.16.9.5.40743`. La version `5.0.0‑pre.202611061606` est attestée comme [paquet serveur NuGet](https://www.nuget.org/packages/SPTushonka.Server.Core/5.0.0-pre.202611061606), pas comme distribution jouable vérifiée. |

### Données disponibles localement

| Jeu de données | PvP permanent | PvE officiel | PvP saisonnier |
|---|---:|---:|---:|
| Objets | 5 498 | 5 498 | 5 498 |
| Armes, mêlée et dispositifs de signalement | 199 | 199 | 199 |
| Munitions à propriétés balistiques en jeu | 200 | 200 | 200 |
| Équipement défensif et rigs | 423 | 423 | 423 |

Import effectué via les [exports JSON de Tarkov.dev](https://json.tarkov.dev/endpoints), après un échec HTTP 422 de GraphQL. Les nombres par catégorie sont des sous-ensembles du catalogue d’objets. Le relevé inclut les libellés FR/EN et la provenance ; il ne certifie ni un build exact d’EFT ni des prix en temps réel. Les fichiers des trois modes sont séparés.

### Dossiers et livrables

| Fichier | Rôle |
|---|---|
| `workflow.json` et `state_machine.json` | Phases, compteurs, critères, livrables et prochaine transition. |
| [Plan éditorial](plan-editorial.md) · `docs/plan-editorial.json` | 87 routes, chacune avec ses sections, interactions, illustrations prévues et vérifications. |
| [Vérifications datées](verifications-2026-11-18.md) · `docs/sources.json` | Constat sur les versions, corrections du cahier et références utiles pour la rédaction. |
| [Architecture](architecture.md) | Conventions HTML/CSS/JS, direction artistique, accessibilité, performance et politique de médias. |
| `js/data/catalog-manifest.json` · `data/snapshots/` | Relevés sourcés, métadonnées de collecte, empreintes et index des cartes. |
| `scripts/import_tarkov_dev.py` · `scripts/check_phase0.py` | Import relançable et validation locale, sans dépendance Python externe. |

Le contrôle local a validé les **87 routes planifiées**, les **12 catalogues** et la cohérence des fichiers de suivi. La prochaine phase prépare les composants partagés (CSS, navigation, recherche, filtres, comparateurs et lecteur audio) et les premières ambiances MP3.
