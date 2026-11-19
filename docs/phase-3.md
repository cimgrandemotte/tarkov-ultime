# PHASE 3 — Guide du débutant et lore

**Tarkov Ultimate Guide v3.0 · 18 novembre 2026**  
**3 routes éditoriales livrées sur 87 prévues.** L’atelier technique reste distinct. Ouvrez **Tarkov Ultimate Guide** dans l’aperçu Arena (port 4180, non indexé).

## Deux dossiers à lire

| Dossier | Contenu |
|---|---|
| [Guide du débutant](https://4180-i8gmoighw6d8bspep6ilb.e2b.app/pages/getting-started.html) · `pages/getting-started.html` | PvP permanent, Seasonal, PvE et entraînement ; PMC/Scav, USEC/BEAR et chapitre *Tour*. **10 étapes** du pré-raid au stash, checklist de **6 cases** conservée localement, **24 réponses** filtrables, explications des extractions et de la santé en jeu, raccourcis et repères AZERTY. |
| [Lore et univers de Tarkov](https://4180-i8gmoighw6d8bspep6ilb.e2b.app/pages/lore/) · `pages/lore/index.html` | Norvinsk, TerraGroup, **8 fiches** de factions ou groupes, chronologie des Contract Wars à la campagne et repères sur **10 chapitres**. Les issues et leurs conditions restent dans un bloc fermé, sans entrée d’index. |

Les deux routes sont accessibles depuis l’accueil et le menu **Explorer**. **Ctrl + K** ou **⌘ + K** ouvre l’index de **29 entrées**. Le sitemap annonce trois canoniques, une par route : l’alias technique `/pages/lore/index.html` ne crée pas de doublon. Aucun dossier de la phase Cartes n’est servi.

## Sources et limites

Le [journal de vérification](verifications-phase-3.md) recoupe notes de Battlestate, wiki, GitHub/TarkovTracker, transcriptions YouTube, forums, Reddit et canaux publics. **85 références** sont consignées dans `docs/sources.json`, dont des pistes et des accès limités. Les conseils de joueurs ne valent pas notes de patch. Cette phase n’a pas ouvert le client EFT : le tutoriel sur un profil existant, les conditions du raid et les variantes par mode restent à confirmer dans le jeu. Le guide ne publie pas de tarif Lighthouse en présence de sources contradictoires et ne recommande pas de réinitialiser un profil pour rejouer le tutoriel.

## Illustrations

**5 JPG intégrés** (931 888 octets) : planque, HUD annoté non officiel, inventaire de soins et schéma HTML des sept zones, baie fictive et dossier cartographique. Les photos sont originales et générées, en **1 376 × 768**, JPEG qualité 85. **1 JPG supplémentaire reste en réserve**, hors aperçu et hors sitemap ; les six nouveaux médias totalisent 1 206 964 octets. Aucun nouvel audio ; les **6 MP3** existants sont conservés. Dimensions, tailles et empreintes sont consignées dans `workflow.json`.

## Validation du web

| Contrôle | Résultat |
|---|---|
| Chromium 159.0.8154.6 | 14 groupes passés : clavier, tactile, focus, ancres, checklist, FAQ, recherche entre routes, mise en page de 320 à 1 440 px et texte agrandi à 200 %. |
| Firefox 159.0 | 6 contrôles à 390 px, dont le filtre, le passage d’un dossier à l’autre et le dévoilement volontaire. |
| Accessibilité | Aucune violation détectée dans **8 états axe-core** (WCAG 2.1 A/AA). Sans JS, le contenu et les accordéons natifs restent lisibles. Contraste des titres et textes sur les photos : minimum mesuré de **5,61:1** sur 20 profils ; minimum de **3,9:1** pour les contours de contrôle de la palette testée. Ce n’est pas une certification ; Safari, appareils physiques et lecteurs d’écran restent à tester. |
| Régressions | Accueil : 16 groupes Chromium, 5 audits et 6 contrôles Firefox, y compris lecture audio sur action. Atelier : 12 groupes Chromium et 5 audits, toujours isolé sur 4173. |
| Publication | Les trois routes répondent 200 avec `noindex, nofollow` en aperçu. Vérification des ancres, `Article` et `BreadcrumbList` JSON-LD, Open Graph et sitemap ; les fichiers de pilotage et routes futures renvoient 404. Aucun MP3, index de recherche ou catalogue lourd n’est chargé à l’ouverture des dossiers. |

Mesures locales (LCP / CLS ; mobile simulé 390 px, +100 ms RTT, 4 Mbit/s, CPU ×4) :

| Dossier | Bureau | Mobile | Transfert en mobile simulé |
|---|---:|---:|---:|
| Guide du débutant | 196 ms / 0,006 | 1 216 ms / 0 | 358 631 o / 22 ressources |
| Lore et univers | 216 ms / 0,056 | 1 260 ms / 0 | 632 651 o / 23 ressources |

Les rapports détaillés `validation-phase-3*.json`, `contraste-phase-3.json` et `regression-*-phase-3.json` sont dans `data/snapshots/`.

## Rejouer ou continuer

```sh
python3 scripts/build_home.py --check
python3 scripts/check_phase3.py
```

Voir [l’architecture](architecture.md) pour reconstruire avec une origine de déploiement différente et lancer l’aperçu. **État : `ATTENTE_CONTINUE`**. La **PHASE 4 — Cartes** n’est pas commencée.

Tapez CONTINUE pour passer à la phase suivante
