# PHASE 4 — Cartes

**Tarkov Ultimate Guide v3.0 · 18 novembre 2026 · état : `ATTENTE_CONTINUE`**  
**14 routes Cartes livrées** — le hub et ses 13 fiches ; **17 routes sur 87** sont maintenant publiées au total. La PHASE 5 n’a pas commencé.

Ouvrir le [hub Cartes](https://4180-i8gmoighw6d8bspep6ilb.e2b.app/pages/maps/) ou l’[accueil](https://4180-i8gmoighw6d8bspep6ilb.e2b.app/). L’aperçu reste en `noindex, nofollow`.

## Livrables

- **Hub canonique** `pages/maps/` : 13 lieux principaux, six variantes séparées, recherche et filtres par difficulté éditoriale/mode d’export, comparateur limité à deux cartes, réseau de **29 transits dirigés**, sources et tableau de secours. `pages/maps/index.html` sert d’alias au même contenu canonique.
- **13 fiches** : Ground Zero, Customs, Factory, Woods, Shoreline, Interchange, Reserve, The Lab, Lighthouse, Streets of Tarkov, The Labyrinth, Icebreaker et Terminal. Elles distinguent les données d’export des conditions effectivement affichées par le client ; les modes, accès, limites, références et sommaires restent lisibles sans JavaScript.
- **Recherche et SEO** : 17 routes HTML canoniques, sitemap de 17 URL, 43 entrées de recherche et réponses 404 conservées pour les routes futures ou privées. Données et liens d’ancres validés.
- **Images** : 10 nouveaux JPG originaux de 1 376 × 768, qualité JPEG 85, pour **2 520 496 octets** au total ; un panorama de PHASE 2 est réutilisé. Les fiches ont chacune une illustration d’ambiance. Les schémas de repères/transits sont éditoriaux, non à l’échelle et ne prétendent pas être des cartes tactiques.

## Actualité et limites éditoriales

Le relevé du 18/11 différencie l’annonce BSG d’une mise à jour déjà déployée : la fenêtre 1.3.5.0 est annoncée pour la seconde moitié de novembre, sans jour précis. Pour Icebreaker, le message BSG du 12/11 est consigné sans lui attribuer un numéro de patch ni transformer les documents Battle Pass en butin garanti. Les changements rapportés pour The Wedge, Black Division et Icebreaker sont distingués selon leur périmètre. Les vidéos de novembre sur fumée/IA sont qualifiées d’incertaines et non reproductibles : elles ne sont pas recommandées comme technique fiable.

**Aucun client EFT ni raid n’a été lancé.** Disponibilité par compte, état réel des sorties, coûts, conditions, rencontres et itinéraires restent à vérifier dans le client. Les exports Tarkov.dev et les pages communautaires ne valent pas état de raid ; leurs limites sont consignées dans [`docs/verifications-phase-4.md`](verifications-phase-4.md) et [`docs/sources.json`](sources.json).

## Validation

| Contrôle | Résultat |
|---|---|
| Build et validations statiques | Build CLI : 17 routes. `check_phase2.py --artefacts-seuls` et `check_phase3.py --phase4 --artefacts-seuls` réussissent ; 17 routes, 43 entrées, 29 transits, sources, images, sitemap et ancres conformes. |
| Chromium 159.0.8154.6 | **13 groupes passés** : routes/métadonnées, hub, filtres, comparateur, 13 fiches, Icebreaker, clavier, recherche, tactile, reflow et texte à 200 %, couleurs système, repli sans JS et performance mobile. Cinq états axe-core : **0 violation** ; les éléments signalés `incomplete` restent archivés pour revue manuelle, sans être des violations. |
| Firefox 159.0 | **7 contrôles passés**, aucune erreur : recherche, filtres, comparateur, menu tactile, clavier sur Icebreaker, sources et reflow de 320 à 1 440 px. |
| Contraste des heroes | **20 profils** (2 pages × 5 largeurs × 2 thèmes), ratio de texte minimum **5,10:1**. Les huit paires de la palette mesurées dépassent 4,5:1 ; minimum **8,82:1**. Mesure sur capture, pas une certification générale d’accessibilité. |
| Performance mobile simulée | Réseau à 4 Mbit/s, RTT 100 ms, CPU ×4 ; budget LCP ≤ 2 500 ms et CLS ≤ 0,1 respecté pour le hub et Icebreaker. |

| Page | LCP | CLS | Ressources | Transfert mesuré |
|---|---:|---:|---:|---:|
| Hub Cartes | 1 540 ms | 0 | 23 | 642 988 octets |
| Icebreaker | 1 268 ms | 0 | 24 | 487 200 octets |

Les rapports détaillés sont dans `data/snapshots/validation-phase-4.json`, `data/snapshots/validation-phase-4-firefox.json` et `data/snapshots/contraste-phase-4.json`.

## Rejouer les contrôles

```sh
python3 scripts/build_home.py --check --base-url https://4180-i8gmoighw6d8bspep6ilb.e2b.app/
python3 scripts/check_phase2.py --artefacts-seuls
python3 scripts/check_phase3.py --phase4 --artefacts-seuls
```

## État du workflow

PHASE 4 est validée et le projet attend la confirmation de transition. **Tapez `CONTINUE` pour commencer PHASE 5 — Armes et munitions.**
