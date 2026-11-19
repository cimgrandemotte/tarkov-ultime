# PHASE 2 — Accueil et navigation livrés

**18 novembre 2026 · Tarkov Ultimate Guide v3.0**

Ouvrez **Tarkov Ultimate Guide** dans le panneau d’aperçu Arena (port **4180**). Il s’agit de l’aperçu non indexé du guide, pas d’une mise en ligne publique sur un domaine définitif. **Une route éditoriale sur 87 est livrée : `index.html`.** L’atelier du jalon précédent reste indépendant sur le port 4173, à `/lab/`.

## Parcours disponible

- **Préparer mon premier raid** ouvre une checklist de trois étapes, mémorisée localement. **Voir les cartes** mène aux premiers repères d’extraction, avec renvoi vers l’index communautaire. Les fiches détaillées ne sont pas encore publiées.
- Le **menu Explorer** ouvre les repères cartes, équipement et boss ainsi que le choix de mode. **Ctrl + K** ou **⌘ + K** ouvre la recherche locale : 15 entrées, uniquement des sections et annonces présentes sur l’accueil. Flèches pour parcourir, Entrée pour ouvrir, Échap pour fermer.
- Les **six annonces** peuvent être filtrées par catégorie. Le relevé distingue la note de référence EFT **1.3.0.0** (29 octobre), le correctif installé le **13 novembre** et son numéro **1.3.0.2.48779** répertorié par le wiki. **1.3.5.0 et Unity 6 sont annoncés**, sans déploiement attesté dans les sources consultées. Date de clôture des Drops, état de Halloween et fin de Kord Breach ne sont pas interchangeables.
- Le pied de page **Sources et méthode** indique la date et le périmètre des chiffres. Les **13 lieux** viennent de l’index du wiki ; les **199 armes**, **200 munitions**, **423 entrées de protection et de portage** et **5 498 objets** viennent de l’instantané Tarkov.dev en **PvP permanent**. Ne pas additionner ces sous-ensembles ni lire ces compteurs comme des prix ou des disponibilités en temps réel. Les endpoints ont été revalidés sans remplacer le snapshot.
- **Écouter l’ambiance** lance la piste **Ville abandonnée** uniquement sur commande. Le bas de page donne accès aux pistes, à la pause, au volume, au contraste renforcé et à la réduction des mouvements. Pas de préchargement MP3 ni de relance automatique en changeant de piste. Le guide distingue PvE officiel, Arena et SP‑Tushonka et signale son statut de fan-site non affilié.

## Sources et médias

Le détail du [relevé avant rédaction](verifications-phase-2.md) sépare notes officielles, données communautaires, conseils de joueurs et accès impossibles. `data/home.json` conserve les données qui alimentent l’accueil ; `docs/sources.json` conserve les références.

| JPG de l’accueil | Usage |
|---|---|
| `images/hero/norvinsk-rain.jpg` | Personnage de dos dans une rue de Norvinsk sous la pluie |
| `images/maps/norvinsk-overlook.jpg` | Panorama des voies ferrées, dossier Cartes |
| `images/weapons/arsenal-workbench.jpg` | Équipement de jeu sur établi, dossier Arsenal |
| `images/bosses/killa-ambience.jpg` | Évocation de Killa dans un centre commercial |
| `images/lore/premier-raid.jpg` | Carte en papier et sac dans une planque, checklist |
| `images/spt/tushonka-hideout.jpg` | Tasse, conserve et ordinateur, dossier solo |

**Six illustrations originales générées**, 1 376 × 768 px, JPEG qualité 85 (1,12 Mo au total). Ce ne sont ni des captures d’Escape from Tarkov ni des cartes utilisables pour se repérer. **Un MP3 original créé** : `audio/ambient/ambient_city.mp3`, boucle de 60 s, stéréo 44,1 kHz/192 kbit/s, synthèse procédurale sans échantillon du jeu. Trois pistes antérieures d’ambiance sont réutilisées ; leurs empreintes et celles des nouveaux médias sont consignées.

## Validation

| Contrôle | Résultat au jalon 2 |
|---|---|
| Chromium 159 | 16 groupes passés ; tests entre 320 et 1 440 px, zoom du texte à 200 %, clavier/tactile, recherche différée, filtres, checklist, modes, audio, préférences et lecture sans JS. |
| Firefox 159 | Six contrôles à 390 px, dont focus, recherche et lecture/pause avec sortie audio virtuelle. |
| Accessibilité | Aucune violation détectée dans les cinq états audités par axe-core (WCAG 2.1 A/AA). Échantillonnage séparé des arrière-plans sur dix profils : minimum **6,84:1** pour les textes contrôlés, **4,17:1** pour les contours de commande de la palette testée. Ni certification ni test sur lecteur d’écran, Safari ou appareil physique. |
| Chargement local | LCP **0,25 s**, CLS **0,009** sur bureau. Profil mobile simulé à 390 px (RTT 100 ms, 4 Mbit/s, CPU ×4) : **1,49 s**, CLS **0**. Pas de catalogue entier, de MP3 ou d’index de recherche au chargement. Mesures propres à ce profil, pas au réseau réel d’un lecteur. |
| Publication | Une page dans le sitemap, canonique HTTPS de l’environnement d’aperçu, Open Graph, Twitter Card et `WebSite` JSON-LD. L’aperçu n’expose ni dossiers futurs, ni documents de pilotage, ni données de production. Les liens externes sont hors contrôle du guide. |
| Régression de l’atelier | L’atelier répond toujours ; ses 12 groupes Chromium et cinq états axe-core repassent avec les modifications communes. |

Preuves : `data/snapshots/validation-phase-2.json`, `data/snapshots/validation-phase-2-firefox.json` et `data/snapshots/contraste-phase-2.json`.

## Reconstruire et rejouer

Depuis la racine du projet dans Arena :

```sh
python3 scripts/build_home.py
python3 scripts/serve_home.py --port 4180
```

Pour un hébergement distinct, fournir l’URL HTTPS réelle avec `scripts/build_home.py --base-url …`. Les chemins des ressources sont relatifs. Garder les seuls fichiers d’accueil servis par l’aperçu, sans déployer le pilotage ou l’atelier. Le serveur d’aperçu met volontairement `noindex` et ne sert pas de configuration d’hébergement pour la mise en ligne définitive.

Les tests utilisent les mêmes dépendances que [les fondations](phase-1.md) (Node.js, Playwright 1.65.1, axe-core 4.14.1, Python et Pillow) :

```sh
node scripts/tests/phase2.cjs
node scripts/tests/phase2-colors.cjs
node scripts/tests/phase2-firefox.cjs
python3 scripts/check_phase0.py
python3 scripts/check_phase1.py
python3 scripts/check_phase2.py
```

Sur Linux sans sortie réelle, lancer Firefox avec un récepteur PulseAudio virtuel. La page est réassemblée depuis `templates/index.html.in` ; ne pas modifier les artefacts générés à la main. Pour réencoder la boucle urbaine, utiliser `scripts/create_home_audio.py` avec les dépendances de synthèse des fondations, puis reconstruire l’accueil.

**Prochaine étape : PHASE 3 — Guide du débutant et lore.** Elle n’est pas commencée.
