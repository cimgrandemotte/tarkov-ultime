#!/usr/bin/env python3
"""PHASE_8 : pages Compétences, Économie/Flea et Stratégies, sourcées et statiques."""
from datetime import date
from html import escape
import json
from urllib.parse import urljoin

from site_urls import seo_base_is_public, canonical_link, open_graph_url_meta

ROOT = __import__('pathlib').Path(__file__).resolve().parents[1]
REVIEW = '2026-11-18'
REVIEW_DATE = '18 novembre 2026'
MODES = {'regular': 'PvP permanent', 'pve': 'PvE Zone', 'pvp-season': 'PvP Seasonal'}

PAGES = [
    {'id':'skills','file':'pages/skills/index.html','route':'pages/skills/','title':'Compétences (Skills)','label':'Compétences','code':'S–01',
     'lead':'Lire les compétences sans confondre progression, bonus, profil et hypothèses de guides anciens.',
     'hero':'images/phase8/skills-field-manual.jpg','alt':'Carnet de terrain, gants et chronomètre sur un établi de planque fictif.',
     'secondary':'images/phase8/skills-training-range.jpg','secondary_alt':'Opérateur fictif courant avec un sac dans une cour industrielle pluvieuse.',
     'sources':['bsg-patch-130-official-p8','bsg-skill-speed-oct2'],
     'quick':[('skills-filter','Catalogue','Filtrer'),('skills-patch','Changements confirmés','Comparer'),('skills-routine','Journal local','Suivre')]},
    {'id':'economy','file':'pages/economy/index.html','route':'pages/economy/','title':'Économie & Flea Market','label':'Économie','code':'E–01',
     'lead':'Comparer vente, conservation, fabrication et coût du risque avec vos propres prix et votre mode.',
     'hero':'images/phase8/economy-loot.jpg','alt':'Sac de raid ouvert avec des objets de récupération génériques, sans logo ni interface de jeu.',
     'secondary':'images/phase8/economy-ledger.jpg','secondary_alt':'Registre illisible, crayon et calculatrice dans une planque fictive.',
     'sources':['bsg-patch-110-official-p8','bsg-expansion-tarcoin','tarkov-market-economy-p8','github-data-pr896-p8'],
     'quick':[('economy-decide','Décider quoi faire','Comparer'),('economy-mode-data','Par mode','Vérifier'),('economy-calc','Estimation','Calculer')]},
    {'id':'flea','file':'pages/economy/flea-market.html','route':'pages/economy/flea-market.html','title':'Guide du Flea Market','label':'Flea Market','code':'E–02',
     'lead':'Contrôler les règles et estimer une vente avec un taux effectif saisi — sans cours ni commission inventés.',
     'hero':'images/phase8/flea-market.jpg','alt':'Comptoir de troc souterrain fictif dans un entrepôt reconverti.',
     'secondary':'images/phase8/economy-ledger.jpg','secondary_alt':'Registre fictif et calculatrice fermée, avec marques illisibles.',
     'sources':['bsg-patch-110-official-p8','tarkov-market-economy-p8','github-data-pr896-p8'],
     'quick':[('flea-rules','Règles & différences','Lire'),('flea-calc','Comparer une offre','Calculer'),('flea-check','Avant de publier','Vérifier')]},
    {'id':'money','file':'pages/economy/money-making.html','route':'pages/economy/money-making.html','title':'Gagner des roubles','label':'Gagner des roubles','code':'E–03',
     'lead':'Choisir une boucle selon votre mode, votre objectif et le coût que vous acceptez de risquer.',
     'hero':'images/phase8/money-run.jpg','alt':'Survivant fictif à la lisière d’une cour urbaine détrempée, observant une sortie lointaine.',
     'secondary':'images/phase8/economy-loot.jpg','secondary_alt':'Objets de récupération génériques rangés dans un sac après un raid fictif.',
     'sources':['bsg-patch-110-official-p8','tarkov-market-economy-p8','youtube-interchange-nov-p8','github-data-pr896-p8'],
     'quick':[('money-loops','Boucles possibles','Choisir'),('money-calc','Votre scénario','Estimer'),('money-sources','Témoignages','Recouper')]},
    {'id':'strategy','file':'pages/strategy/index.html','route':'pages/strategy/','title':'Stratégies & méta en jeu','label':'Stratégies','code':'T–01',
     'lead':'Choisir une routine, un guide et un équipement en fonction du mode et de votre profil.',
     'hero':'images/phase8/strategy-brief.jpg','alt':'Table de briefing de raid fictive avec carte abstraite, boussole et jetons de planification.',
     'secondary':'images/phase8/pvp-loadout.jpg','secondary_alt':'Équipements tactiques génériques alignés sur un établi sans statistiques ni marques.',
     'sources':['bsg-patch-110-official-p8','bsg-patch-120-official-p8','bsg-patch-130-official-p8','bsg-technical-diary-135'],
     'quick':[('strategy-mode','Choisir son mode','Filtrer'),('strategy-guides','Guides','Explorer'),('strategy-date','État des sources','Vérifier')]},
    {'id':'beginner','file':'pages/strategy/beginner-tips.html','route':'pages/strategy/beginner-tips.html','title':'61 astuces pour débuter','label':'Astuces débutant','code':'T–02',
     'lead':'Des habitudes de préparation, navigation, combat, économie et bilan — avec favoris conservés sur cet appareil.',
     'hero':'images/phase8/skills-training-range.jpg','alt':'Opérateur fictif en entraînement de déplacement sous la pluie.',
     'secondary':'images/phase8/strategy-brief.jpg','secondary_alt':'Table de briefing fictive avec carte abstraite et boussole.',
     'sources':['bsg-patch-110-official-p8','bsg-patch-120-official-p8','bsg-patch-130-official-p8','bsg-skill-speed-oct2'],
     'quick':[('tips-controls','Filtrer les astuces','Filtrer'),('tips-list','Les 61 repères','Parcourir'),('tips-sources','Méthode','Lire')]},
    {'id':'advanced','file':'pages/strategy/advanced-tactics.html','route':'pages/strategy/advanced-tactics.html','title':'Tactiques avancées en jeu','label':'Tactiques avancées','code':'T–03',
     'lead':'Planifier un raid, gérer les informations de jeu et choisir quand poursuivre, temporiser ou rompre le contact.',
     'hero':'images/phase8/advanced-tactics.jpg','alt':'Deux opérateurs fictifs progressant sur des côtés opposés d’une rue pluvieuse, avec couvert et visibilité.',
     'secondary':'images/phase8/strategy-brief.jpg','secondary_alt':'Brief de raid fictif avec grille abstraite et jetons.',
     'sources':['bsg-patch-120-official-p8','bsg-patch-130-official-p8','bsg-technical-diary-135'],
     'quick':[('tactics-loop','Boucle de décision','Lire'),('tactics-scenarios','Scénarios','Ouvrir'),('tactics-ai','IA et limites','Recouper')]},
    {'id':'pvp','file':'pages/strategy/pvp-guide.html','route':'pages/strategy/pvp-guide.html','title':'Guide PvP','label':'PvP','code':'T–04',
     'lead':'Préparer une session PvP permanent ou Seasonal sans confondre profils, assurance et progression.',
     'hero':'images/phase8/pvp-loadout.jpg','alt':'Trois niveaux d’équipement fictifs, simples et non marqués, posés sur un établi.',
     'secondary':'images/phase8/advanced-tactics.jpg','secondary_alt':'Deux opérateurs fictifs se repositionnant sur une rue urbaine.',
     'sources':['bsg-patch-110-official-p8','bsg-patch-130-official-p8','bsg-skill-speed-oct2'],
     'quick':[('pvp-mode','Permanent / Seasonal','Comparer'),('pvp-kit','Préparer le kit','Choisir'),('pvp-review','Bilan après contact','Apprendre')]},
    {'id':'pve','file':'pages/strategy/pve-guide.html','route':'pages/strategy/pve-guide.html','title':'Guide PvE & Prestige','label':'PvE & Prestige','code':'T–05',
     'lead':'Distinguer les changements officiels de l’IA, les retours de joueurs et les conditions de Prestige affichées par le client.',
     'hero':'images/phase8/pve-prestige.jpg','alt':'Carnet, sac et objets conservés dans un coin de planque fictif avant un nouveau départ.',
     'secondary':'images/phase8/strategy-brief.jpg','secondary_alt':'Table de préparation de raid fictive et plan abstrait.',
     'sources':['bsg-patch-120-official-p8','bsg-patch-130-official-p8','youtube-pve-prestige-nov-p8'],
     'quick':[('pve-ai','IA après 1.2 / 1.3','Lire'),('pve-prestige','Prestige','Vérifier'),('pve-checklist','Votre préparation','Cocher')]},
    {'id':'builds','file':'pages/strategy/meta-builds.html','route':'pages/strategy/meta-builds.html','title':'Builds par budget & méta','label':'Builds & méta','code':'T–06',
     'lead':'Comparer des configurations selon leur usage, leurs déblocages et vos prix réels — pas selon une tier list intemporelle.',
     'hero':'images/phase8/pvp-loadout.jpg','alt':'Configurations génériques d’équipement disposées sur un établi, sans noms ni statistiques.',
     'secondary':'images/phase8/economy-ledger.jpg','secondary_alt':'Registre de budget fictif à annotations illisibles.',
     'sources':['bsg-patch-110-official-p8','bsg-patch-130-official-p8','github-gunsmith-pr243-p8','github-data-pr896-p8','tarkov-market-economy-p8'],
     'quick':[('build-rubric','Critères S–D','Comprendre'),('build-tool','Calculer son kit','Estimer'),('build-examples','Profils d’usage','Comparer')]},
]

NAV_PAGES = [
    ('pages/skills/','Compétences'),('pages/economy/','Économie'),('pages/economy/flea-market.html','Flea Market'),
    ('pages/economy/money-making.html','Gagner des roubles'),('pages/strategy/','Stratégies'),
    ('pages/strategy/beginner-tips.html','Astuces débutant'),('pages/strategy/advanced-tactics.html','Tactiques avancées'),
    ('pages/strategy/pvp-guide.html','Guide PvP'),('pages/strategy/pve-guide.html','PvE & Prestige'),('pages/strategy/meta-builds.html','Builds & méta'),
]
RELATED = {
 'skills':['economy','strategy','pve'], 'economy':['flea','money','skills'], 'flea':['economy','money','builds'],
 'money':['economy','flea','beginner'], 'strategy':['beginner','pvp','pve','builds'], 'beginner':['strategy','money','advanced'],
 'advanced':['pvp','pve','beginner'], 'pvp':['builds','advanced','economy'], 'pve':['skills','beginner','strategy'],
 'builds':['pvp','economy','flea'],
}

TIPS = [
 ('preparer','Choisis un objectif principal','Une quête, une carte à apprendre ou un run de ressources suffit. Les objectifs secondaires restent facultatifs.'),
 ('preparer','Vérifie le mode et le profil','PvP permanent, PvE et Seasonal ont des profils/règles distincts; vérifie le personnage avant de préparer le kit.'),
 ('preparer','Ouvre la carte avant le raid','Repère l’extraction possible pour ton personnage, puis identifie un point de repère de départ.'),
 ('preparer','Fais une mini-checklist de sortie','Note l’objectif, l’extraction prévue et un itinéraire de secours; la sortie affichée en jeu reste la référence.'),
 ('preparer','Inspecte les commandes essentielles','Contrôle soin, rechargement, posture et interaction dans les réglages. Les touches personnalisées varient.'),
 ('preparer','Teste un kit que tu comprends','Connais l’arme, son chargeur et ses soins avant d’ajouter des accessoires ou une deuxième mission.'),
 ('preparer','Vérifie les munitions, pas seulement le modèle','La cartouche chargée et sa disponibilité par mode/trader font partie du kit; contrôle les valeurs dans les guides datés et le client.'),
 ('preparer','Emporte les soins dont tu sais te servir','Lis les objets de soin dans le client et garde un plan simple pour les blessures probables de ton raid.'),
 ('preparer','Prends en compte ton budget de remplacement','Le prix du kit est une dépense que tu peux perdre en jeu; n’utilise pas le prix d’un autre mode ou d’une vieille tier list.'),
 ('preparer','Vérifie l’assurance dans le mode choisi','Les notes BSG 1.1 indiquent que l’assurance est désactivée en PvP Seasonal; ne transpose pas une règle d’un profil à l’autre.'),
 ('preparer','Distingue tâche, Hideout et vente','Avant de vendre un objet, vérifie si tu en as besoin pour une tâche ou une station; un prix élevé n’est pas toujours la bonne priorité.'),
 ('preparer','Fais une place pour le retour','Un sac plein et des objets non triés compliquent le retour; décide avant le départ ce que tu gardes et ce que tu vendras.'),
 ('repere','Apprends une carte à la fois','Répète une carte familière jusqu’à reconnaître les sorties et les repères sans parcourir tout l’inventaire de cartes.'),
 ('repere','Mémorise un repère visible par secteur','Un bâtiment, une route ou une silhouette t’aide à te réorienter; croise plusieurs repères au lieu de suivre un seul souvenir.'),
 ('repere','Confirme ton extraction sur le terrain','Les sorties changent selon le profil, le spawn et les conditions. Compare la liste en raid avec ta carte externe.'),
 ('repere','Prévoyez une route de secours','Une sortie fermée ou un contact peut invalider le plan initial. Garde une alternative que tu peux réellement atteindre.'),
 ('repere','Utilise le sprint avec intention','Le sprint gagne du temps mais consomme de l’endurance et fait du bruit; privilégie-le quand l’exposition ou l’urgence le justifie.'),
 ('repere','Ralentis pour écouter quand l’information vaut le détour','Un arrêt bref peut révéler des indices audio; la portée et le mixage dépendent du jeu, du casque et des réglages.'),
 ('repere','Repère les surfaces bruyantes','Apprends en jeu comment bois, métal, verre ou végétation sonnent; ne suppose pas que ton retour audio est identique à celui des autres.'),
 ('repere','Traverse les zones découvertes avec un plan','Choisis le prochain couvert et le trajet avant d’entrer dans une zone exposée, plutôt que de t’y arrêter pour ouvrir l’inventaire.'),
 ('repere','Ne confonds pas vitesse et précipitation','Une progression posée peut réduire l’incertitude; une traversée rapide peut aussi être préférable si rester exposé est pire.'),
 ('repere','Observe les indices de ton itinéraire','Tirs, portes ouvertes et conteneurs fouillés donnent un contexte imparfait, pas une carte exacte des joueurs.'),
 ('repere','Garde une marge de stamina','Si tu utilises toute ton endurance avant un passage risqué, tu réduis tes options de déplacement. Regarde la barre en jeu.'),
 ('repere','Apprends les spawns à partir de tes propres raids','Après une rencontre précoce, note ton spawn et les directions possibles; les cartes/outils communautaires doivent rester datés.'),
 ('combat','Décide pourquoi tu prends un combat','Protection d’une quête, défense d’une sortie ou occasion claire sont des raisons; un bruit seul n’oblige pas à poursuivre.'),
 ('combat','Utilise un couvert qui bloque vraiment la ligne de tir','Un écran visuel ou un buisson n’est pas forcément un obstacle solide. Appuie-toi sur la géométrie du jeu connue.'),
 ('combat','Change de situation après avoir révélé ta position','Déplace-toi, attends ou change d’angle au lieu de répéter automatiquement le même peek.'),
 ('combat','Évite de rester immobile pendant un duel prolongé','Rester figé rend ton prochain mouvement prévisible; repositionne-toi uniquement quand ton information et la carte le permettent.'),
 ('combat','Garde le viseur près des zones d’entrée plausibles','La préparation du viseur réduit le mouvement nécessaire, mais ne garantit ni détection ni victoire.'),
 ('combat','Vérifie le chargeur après le contact','Rechargement, cartouches restantes et chargeur choisi doivent être contrôlés avant un nouveau déplacement.'),
 ('combat','Éloigne-toi avant de soigner si tu peux','Soigner en plein champ coûte du temps et de l’attention; trouve un couvert de jeu et garde une issue.'),
 ('combat','Ne confonds pas bruit et nombre d’ennemis','Un seul événement audio ne confirme pas le nombre, la distance ou la direction exacte d’un adversaire.'),
 ('combat','Évite de looter immédiatement un corps','Un combat peut attirer d’autres joueurs ou IA. Écoute, sécurise et décide ensuite si le corps vaut le risque.'),
 ('combat','Sépare le risque PvP et le risque PvE','Les bots PvE ont été modifiés en 1.2 et 1.3; les anecdotes de comportement ne garantissent pas leur prochaine réaction.'),
 ('combat','Apprends un outil à la fois','Entraîne-toi à contrôler une arme/une lunette avant d’empiler plusieurs changements de sensibilité ou de pièces.'),
 ('combat','N’utilise pas une tier list comme prédiction de duel','La munition, l’armure portée, la zone touchée et l’état des objets changent l’issue; vérifie le client et les données du patch.'),
 ('loot','Compare la valeur aux besoins du profil','Un objet utile à la tâche ou à la planque peut valoir plus pour ta progression qu’un prix flea élevé.'),
 ('loot','Renseigne tes propres prix récents','Les prix communautaires sont volatils et les marchés sont distincts; saisis une estimation datée du bon mode.'),
 ('loot','Regarde le coût par case comme un repère','Diviser une valeur saisie par les cases occupées aide à arbitrer, mais ne tient pas compte du risque, des restrictions ou de la demande.'),
 ('loot','Ne laisse pas l’inventaire décider seul','Remplace les objets de faible priorité uniquement si tu connais la quête, le prix et l’espace que tu sacrifies.'),
 ('loot','Traite un run Scav comme une occasion, pas un salaire','Le coût d’équipement peut être faible, mais le résultat et le retour ne sont pas garantis.'),
 ('loot','Pense à l’extraction avant un sac plein','La valeur ne devient utile qu’après le retour et la vente ou l’usage. Réévalue l’itinéraire quand ton sac change.'),
 ('loot','Fais une petite rotation avant une route complexe','Un circuit connu à risque tolérable vaut parfois mieux qu’une destination à butin élevé mais mal maîtrisée.'),
 ('loot','Compare vendeur et marché avec les frais inclus','Le prix affiché n’est pas ton gain net; le calculateur Flea demande un taux effectif que tu saisis.'),
 ('loot','Sépare ₽, devises et TarCoin','TarCoin sert à l’Expansions Hub selon BSG; ne le traite pas comme un cours de roubles.'),
 ('loot','Ne crois pas un revenu par heure sans protocole','Mode, route, nombre de tentatives, survivabilité, prix et date doivent être connus pour comparer deux exemples.'),
 ('loot','Intègre les frais et consommables à tes tests','Munitions, soins, entrée, marché et coûts de remplacement appartiennent au scénario que tu mesures.'),
 ('loot','Vérifie la réputation et la limite d’offres dans le client','Les outils de données donnent des repères; l’interface du Flea et l’état du compte font foi.'),
 ('loot','Considère les clés comme un capital risqué','Un prix d’achat, des usages restants et le risque d’accès doivent être inclus avant de choisir une salle.'),
 ('loot','N’investis pas tout le stash dans une seule idée','Garde une réserve que tu es prêt à perdre sans bloquer tes objectifs suivants.'),
 ('apres','Note le point de décision, pas seulement la mort','Écris où tu étais, ce que tu savais et l’alternative que tu aurais pu choisir.'),
 ('apres','Regarde les faits avant de changer tout ton kit','Une mort peut venir de la route, de l’angle, d’une cartouche ou d’une mauvaise info; isole une variable.'),
 ('apres','Vérifie les tâches après extraction','Les objectifs partagés ou les conditions de remise peuvent différer; le journal client confirme la progression.'),
 ('apres','Trie par prochaines actions','Sépare objets à rendre, à garder pour Hideout et à vendre; réévalue après un patch ou un changement de mode.'),
 ('apres','Garde un historique des prix que tu observes','Date, mode, source et prix réellement vendu rendent ton propre journal plus utile qu’un chiffre isolé.'),
 ('apres','Révise ton plan quand le patch change le système','Les posts BSG cités ici ne donnent pas toujours les multiplicateurs ou les formules; attends une mesure avant de faire un guide chiffré.'),
 ('apres','Compare plusieurs raids, pas un loot exceptionnel','Un échantillon court peut refléter un spawn chanceux, un événement ou un joueur très expérimenté.'),
 ('apres','Demande le mode avant de copier une route','Une vidéo PvE, PvP ou Seasonal n’implique pas le même marché, les mêmes profils ni les mêmes adversaires.'),
 ('apres','Utilise une vidéo comme démonstration, pas comme contrat','Note la date, le patch et le créateur; vérifie les portes, clés, prix et objectifs dans le client.'),
 ('apres','Supprime un favori devenu obsolète','La checklist locale suit tes préférences, pas l’état du jeu; un repère favori n’est pas une règle vérifiée.'),
 ('apres','Accepte les raids d’apprentissage','Un objectif d’extraction ou une carte mieux comprise peut être un bon résultat même sans combat ni gros butin.'),
]


def e(value):
    return escape(str(value if value is not None else ''), quote=True)


def _fig(src, alt, caption, root):
    return (f'<figure class="phase8-figure"><img src="{e(root+src)}" width="1376" height="768" alt="{e(alt)}" loading="lazy" decoding="async">'
            f'<figcaption>{e(caption)}</figcaption></figure>')


def _source_html(keys, sources):
    rows=[]
    for key in keys:
        item=sources.get(key)
        if not item:
            raise ValueError(f'Source PHASE_8 absente de docs/sources.json: {key}')
        title=item.get('titre') or key
        url=item.get('url') or ''
        kind=item.get('type') or 'source'
        note=item.get('usage_phase_8') or item.get('usage') or item.get('revalidation_phase_7') or 'Contexte documentaire; vérifier dans le client si la donnée évolue.'
        date=item.get('date_releve_phase_8') or 'Relevé : 18 novembre 2026'
        rows.append(f'<li><span class="phase8-source__type">{e(kind.replace("_", " "))}</span><div><a href="{e(url)}" rel="noopener noreferrer">{e(title)} <span aria-hidden="true">↗</span></a><p>{e(note)}</p><small>{e(date)}</small></div></li>')
    return ''.join(rows)


def _nav(root, current):
    groups=[
      ('Échanges & progression',[('pages/traders/','Traders'),('pages/quests/','Quêtes & Kappa'),('pages/hideout/','Planque & crafts')]),
      ('Compétences & économie',[('pages/skills/','Compétences'),('pages/economy/','Économie'),('pages/economy/flea-market.html','Flea Market'),('pages/economy/money-making.html','Gagner des roubles')]),
      ('Stratégies',[('pages/strategy/','Hub stratégies'),('pages/strategy/beginner-tips.html','Astuces débutant'),('pages/strategy/advanced-tactics.html','Tactiques avancées'),('pages/strategy/pvp-guide.html','PvP'),('pages/strategy/pve-guide.html','PvE & Prestige'),('pages/strategy/meta-builds.html','Builds & méta')]),
    ]
    html_groups=[]
    for heading,links in groups:
        html_groups.append('<div class="home-mega__group"><p class="eyebrow">'+e(heading)+'</p>'+''.join(f'<a class="mega-menu__item" href="{e(root+route)}"'+(' aria-current="page"' if route==current else '')+f'><strong>{e(label)}</strong><span>Guide et outils locaux, sourcés par date et mode.</span></a>' for route,label in links)+'</div>')
    html_groups.append('<div class="home-mega__group"><p class="eyebrow">Jeux & événements</p>'+''.join(f'<a class="mega-menu__item" href="{e(root+route)}"'+(' aria-current="page"' if route==current else '')+f'><strong>{e(label)}</strong><span>{e(summary)}</span></a>' for route,label,summary in [('pages/spt-tushonka/','SP-Tushonka','Guide, installation, mods, Fika et dépannage.'),('pages/arena/','Escape from Tarkov: Arena','Modes, notes et boutique.'),('pages/events/','Événements','État 2026, échéances et chronologie.')])+'</div>')
    return (f'<nav class="site-nav" id="global-nav" aria-label="Navigation principale" data-site-nav><a class="site-nav__link" href="{root}">Accueil</a>'
            f'<a class="site-nav__link" href="{root}pages/maps/">Cartes</a><a class="site-nav__link" href="{root}pages/weapons/">Arsenal</a>'
            f'<a class="site-nav__link" href="{root}pages/ammo/">Munitions</a><a class="site-nav__link" href="{root}pages/armor/">Protection</a>'
            f'<details class="mega-menu home-mega" data-nav-disclosure><summary class="mega-menu__summary">Progression & stratégies</summary>'
            f'<div class="mega-menu__panel home-mega__panel phase8-mega">{"".join(html_groups)}</div></details></nav>')


def _source_refs(keys):
    return ''.join(f'<a class="phase8-ref" href="#sources">{e(key)}</a>' for key in keys)


def _quick(page):
    return ''.join(
        f'<a class="guide-quick__link" href="#{e(anchor)}"><span class="guide-quick__no" aria-hidden="true">{i:02d}</span>'
        f'<span class="guide-quick__copy"><strong>{e(title)}</strong><small>{e(label)}</small></span>'
        f'<span class="guide-quick__arrow" aria-hidden="true">↘</span></a>'
        for i, (anchor, title, label) in enumerate(page['quick'], 1)
    )


def _cards(ids, root):
    cards=[]
    by_id={p['id']:p for p in PAGES}
    for ident in ids:
        page=by_id[ident]
        cards.append(f'<a class="phase8-link-card" href="{e(root+page["route"])}"><strong>{e(page["title"])}</strong><span>{e(page["lead"])}</span><span class="phase8-link-card__arrow" aria-hidden="true">↗</span></a>')
    return '<div class="phase8-card-grid">'+''.join(cards)+'</div>'


def _mode_table():
    rows = [
        ('PvP permanent', 'Personnage PvP Zone non saisonnier.',
         'Les changements économiques du patch 1.1.0.0 sont annoncés pour tous les modes.',
         'Offre trader, restrictions de l’item et commission indiquées dans le client.'),
        ('PvE Zone', 'Profil PvE distinct; Prestige réinitialise la progression de ce profil.',
         'Le patch 1.1.0.0 inclut aussi le PvE dans ses changements économiques.',
         'Offre, limite ou item vendable à confirmer sur ce profil dans le client.'),
        ('PvP Seasonal', 'Personnage distinct; règles globales et modificateurs personnels saisonniers.',
         'Le patch 1.1.0.0 inclut le PvP Season dans ses changements économiques.',
         'L’assurance est désactivée en PvP Season selon BSG; les modificateurs actifs sont affichés en jeu.'),
    ]
    return ''.join(
        f'<tr><th scope="row">{e(mode)}</th><td>{e(profile)}</td><td>{e(economy)}</td><td>{e(check)}</td></tr>'
        for mode, profile, economy, check in rows
    )


def _skills_content(root):
    topics = [
        ('metabolism', 'Métabolisme', 'Le patch 1.3.0.0 dit que la progression dépend de la quantité d’énergie ou d’hydratation restaurée. Les notes ne donnent ni taux par action ni formule complète.'),
        ('seasonal', 'Profil Seasonal', 'BSG indique que toutes les compétences progressent nettement plus vite en Seasonal. Le taux exact et la comparaison chiffrée avec chaque autre profil ne sont pas publiés.'),
        ('returns', 'Diminishing returns', 'Les diminishing returns ont été rééquilibrés dans 1.3.0.0; aucun nouveau plafond, délai de remise à zéro ou coefficient n’est fourni dans ces notes.'),
        ('weapons', 'Compétences d’armes', 'Le correctif 1.3.0.0 aligne leur vitesse de progression sur celle des autres compétences. Le post officiel du 2 octobre annonce jusqu’à 60 % plus vite toutes compétences confondues — « jusqu’à » n’est pas un bonus garanti.'),
    ]
    cards = ''.join(
        f'<article class="phase8-card" data-p8-skill-topic="{e(topic)}"><p class="phase8-card__eyebrow">Note de patch vérifiée</p><h3>{e(title)}</h3><p>{e(text)}</p></article>'
        for topic, title, text in topics
    )
    options = ''.join(f'<option value="{e(topic)}">{e(title)}</option>' for topic, title, _ in topics)
    return f'''<section class="phase8-intro" id="skills-intro" tabindex="-1"><div><p class="guide-kicker">PROGRESSION · NOTES BSG 1.3.0.0</p><h2>Ce qui est confirmé — sans inventer de multiplicateur</h2><p>Les annonces officielles d’octobre décrivent plusieurs changements de progression, mais ne publient pas un tableau de taux pour chaque compétence. Ce guide présente les règles explicitement nommées et renvoie à l’écran de compétences du client pour le profil et la progression réels.</p><p><strong>Portée éditoriale :</strong> aucune formule issue d’un ancien guide, aucun identifiant d’export non vérifié et aucun gain par action ne sont présentés comme état actuel.</p></div>{_fig('images/phase8/skills-training-range.jpg','Opérateur fictif en entraînement de déplacement sous la pluie.','Illustration éditoriale originale; pas une capture ou une mesure de progression EFT.',root)}</section>
<section class="guide-section phase8-section" id="skills-filter" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> Changements confirmés</p><h2>Filtrer par sujet</h2><p>Les libellés reprennent les thèmes des notes officielles, pas une taxonomie complète de chaque compétence.</p></div><label class="field phase8-mode-select" for="p8-skill-topic-filter">Sujet<select class="field__input" id="p8-skill-topic-filter" data-p8-skill-filter><option value="all">Tous les sujets</option>{options}</select></label><div class="phase8-card-grid" data-p8-skill-topic-list>{cards}</div><p class="phase8-result-count" role="status" aria-live="polite" data-p8-skill-topic-count>4 changements officiels présentés.</p><noscript><p class="phase8-note">JavaScript désactivé : les quatre sujets restent visibles; seul le filtre est indisponible.</p></noscript></section>
<section class="guide-section phase8-section" id="skills-patch" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>02</span> Lire les chiffres correctement</p><h2>« Jusqu’à 60 % plus vite » n’est pas un taux garanti</h2><p>Le compte officiel BSG a annoncé le 2 octobre un gain allant jusqu’à 60 % dans tous les modes, ainsi qu’un ajustement des limites de progression en raid. Puis le patch 1.3.0.0 du 29 octobre a détaillé des changements ciblés, sans publier la formule des diminishing returns.</p></div><div class="phase8-callout phase8-callout--warning"><strong>Ne recopie pas un ancien reset, plafond ou bonus par niveau comme valeur actuelle.</strong><p>Les notes accessibles ne donnent pas les coefficients par compétence, les valeurs d’action ni une nouvelle table de seuils. Si un guide affirme un chiffre exact, vérifie sa date et compare-le au client après 1.3.0.0.</p></div></section>
<section class="guide-section phase8-section" id="skills-routine" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>03</span> Journal personnel, local</p><h2>Suivre tes observations sans supposer la formule</h2><p>Enregistre une compétence telle qu’elle apparaît en jeu, le mode et une note libre avant/après. Les entrées restent dans le stockage local de ce navigateur; elles ne sont ni envoyées ni synchronisées.</p></div><form class="phase8-form" data-p8-skill-log-form novalidate><div class="phase8-form__grid"><label class="field" for="p8-log-skill">Compétence telle qu’affichée<input class="field__input" id="p8-log-skill" type="text" maxlength="100" autocomplete="off" required data-p8-log-skill placeholder="Nom lu dans le client"></label><label class="field" for="p8-log-mode">Mode observé<select class="field__input" id="p8-log-mode" data-p8-log-mode>{''.join(f'<option value="{e(k)}">{e(v)}</option>' for k, v in MODES.items())}</select></label><label class="field phase8-field--wide" for="p8-log-note">Action, contexte ou repère avant/après<textarea class="field__input" id="p8-log-note" rows="3" maxlength="500" data-p8-log-note placeholder="Note libre; aucun calcul automatique."></textarea></label></div><div class="phase8-form__actions"><button class="button button--primary" type="submit">Ajouter au journal local</button><button class="button button--quiet" type="button" data-p8-log-clear>Effacer le journal</button></div><p class="phase8-result-count" role="status" aria-live="polite" data-p8-log-status>Journal local vide.</p><ol class="phase8-log-list" data-p8-log-list></ol></form><noscript><p class="phase8-note">JavaScript désactivé : les notes officielles restent lisibles; le journal personnel ne peut pas être enregistré.</p></noscript>{_cards(['strategy','pve','beginner'],root)}</section>'''

def _eco_form():
    return '''<form class="phase8-form" data-p8-calc="economy" novalidate><div class="phase8-form__grid"><label class="field" for="eco-gross">Valeur brute de sortie estimée · ₽<input class="field__input" id="eco-gross" type="number" min="0" step="1" inputmode="numeric" data-p8-input="gross" placeholder="Votre estimation"></label><label class="field" for="eco-fee">Frais effectifs supposés · %<input class="field__input" id="eco-fee" type="number" min="0" max="100" step="0.1" inputmode="decimal" data-p8-input="fee" placeholder="Saisie manuelle"></label><label class="field" for="eco-cost">Kit, consommables et autres coûts · ₽<input class="field__input" id="eco-cost" type="number" min="0" step="1" inputmode="numeric" data-p8-input="cost" placeholder="Votre coût total"></label><label class="field" for="eco-minutes">Durée du scénario · minutes<input class="field__input" id="eco-minutes" type="number" min="0.1" step="0.1" inputmode="decimal" data-p8-input="minutes" placeholder="Votre durée"></label></div><div class="phase8-form__actions"><button class="button button--primary" type="submit">Calculer le scénario</button><button class="button button--quiet" type="reset">Effacer</button></div><div class="phase8-output" aria-live="polite" data-p8-result="economy"><strong>En attente de vos données.</strong><p>Le résultat estimera uniquement les valeurs saisies.</p></div></form>'''


def _economy_content(root):
    rows = _mode_table()
    return f'''<section class="phase8-intro" id="economy-intro" tabindex="-1"><div><p class="guide-kicker">ÉCONOMIE EN JEU · NOTES BSG 1.1.0.0</p><h2>Comparer l’usage, le mode et le coût d’opportunité</h2><p>Les prix des objets, la demande Flea et les offres de chaque profil évoluent. Cette page ne précharge aucun cours; le calculateur utilise uniquement tes propres entrées.</p><p>Le patch 1.1.0.0 du 3 août 2026 annonce des changements moyens de prix et de commission. Ce ne sont ni un cours garanti ni une marge bénéficiaire par objet.</p></div>{_fig('images/phase8/economy-ledger.jpg','Registre fictif et crayon sur un bureau de planque.','Illustration éditoriale; aucune donnée de prix réelle.',root)}</section>
<section class="guide-section phase8-section" id="economy-decide" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> Arbre de décision</p><h2>Vendre, garder, échanger ou fabriquer ?</h2><p>Compare le gain net et la valeur de progression pour le profil actif.</p></div><div class="phase8-card-grid"><article class="phase8-card"><p class="phase8-card__eyebrow">Vendeur</p><h3>Encaisser simplement</h3><p>Compare l’offre du trader affichée à la vente Flea après le frais réellement annoncé par le client. BSG a retiré le volume de ventes requis pour les niveaux de loyauté dans 1.1.0.0.</p></article><article class="phase8-card"><p class="phase8-card__eyebrow">Flea Market</p><h3>Vérifier une offre comparable</h3><p>Regarde le profil, l’objet, la quantité, l’état et les restrictions. Prix demandé, prix réalisé et gain net sont trois choses différentes.</p></article><article class="phase8-card"><p class="phase8-card__eyebrow">Progression</p><h3>Réserver un objet utile</h3><p>La valeur pour une tâche ou une amélioration de Hideout peut dépasser le gain immédiat. Vérifie tes besoins dans le journal et le client avant de vendre.</p></article><article class="phase8-card"><p class="phase8-card__eyebrow">Production</p><h3>Calculer le coût complet</h3><p>Ajoute les ingrédients, la durée, les coûts de vente et l’occasion de revendre les composants. Le prix affiché n’est pas un bénéfice.</p></article></div></section>
<section class="guide-section phase8-section" id="economy-mode-data" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>02</span> Portée des règles par mode</p><h2>Les ajustements d’économie annoncés pour les trois profils</h2><p>Le tableau résume les notes officielles du patch 1.1.0.0; il ne présente aucun prix d’objet ni stock courant.</p></div><div class="phase8-table-wrap" tabindex="0" role="region" aria-label="Périmètre économique officiel par mode"><table class="phase8-table"><caption>Règles BSG publiées le 3 août 2026 · les offres et frais d’une annonce se vérifient dans le client.</caption><thead><tr><th scope="col">Mode</th><th scope="col">Profil</th><th scope="col">Patch 1.1.0.0</th><th scope="col">À confirmer dans le jeu</th></tr></thead><tbody>{rows}</tbody></table></div><div class="phase8-callout phase8-callout--warning"><strong>Les 5 % annoncés ne sont pas un prix net garanti.</strong><p>BSG décrit une hausse de la commission Flea de 3 % à 5 %, ainsi qu’une hausse moyenne de 25 % des prix d’achat chez les traders et une baisse moyenne de 20 % de leurs offres de rachat. Les moyennes de patch ne déterminent pas le gain d’un objet ou le frais final d’une annonce. Lis l’offre et le frais dans le client.</p></div><p class="phase8-note"><strong>TarCoin n’est pas un cours de roubles :</strong> BSG dit que cette devise sert exclusivement dans l’Expansions Hub et que les pièces ramenées après extraction y sont créditées. <a href="https://www.escapefromtarkov.com/news/id/403?lang=en" rel="noopener noreferrer">Annonce officielle sur TarCoin <span aria-hidden="true">↗</span></a></p></section>
<section class="guide-section phase8-section" id="economy-calc" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>03</span> Calculateur indicatif</p><h2>Estimer un scénario avec tes hypothèses</h2><p>Formule explicitement simplifiée : valeur brute × (1 − taux effectif saisi) − coûts saisis. Elle ne calcule pas la commission réelle, la demande future, le risque de vente ou les pertes que tu n’as pas entrées.</p></div>{_eco_form()}<noscript><p class="phase8-note">JavaScript désactivé : la méthode et les règles officielles restent consultables; le calculateur ne s’exécute pas.</p></noscript>{_cards(['flea','money','builds'],root)}</section>'''


def _flea_calc():
    return '''<form class="phase8-form" data-p8-calc="flea" novalidate><div class="phase8-form__grid"><label class="field" for="flea-ask">Prix demandé au Flea · ₽<input class="field__input" id="flea-ask" type="number" min="0" step="1" inputmode="numeric" data-p8-input="ask" placeholder="Votre prix"></label><label class="field" for="flea-rate">Taux effectif estimé · %<input class="field__input" id="flea-rate" type="number" min="0" max="100" step="0.1" inputmode="decimal" data-p8-input="rate" placeholder="Vérifiez le client"></label><label class="field" for="flea-trader">Offre du trader · ₽<input class="field__input" id="flea-trader" type="number" min="0" step="1" inputmode="numeric" data-p8-input="trader" placeholder="Votre valeur"></label><label class="field" for="flea-basis">Coût d’acquisition à déduire · ₽<input class="field__input" id="flea-basis" type="number" min="0" step="1" inputmode="numeric" data-p8-input="basis" placeholder="Optionnel, votre coût"></label></div><div class="phase8-form__actions"><button class="button button--primary" type="submit">Comparer les nets simplifiés</button><button class="button button--quiet" type="reset">Effacer</button></div><div class="phase8-output" aria-live="polite" data-p8-result="flea"><strong>En attente de vos données.</strong><p>Aucun prix ou taux n’est prérempli.</p></div></form>'''


def _flea_content(root):
    rows = _mode_table()
    return f'''<section class="phase8-intro" id="flea-intro" tabindex="-1"><div><p class="guide-kicker">FLEA MARKET · PRIX NON PRÉCHARGÉS</p><h2>Compare la vente nette, pas le prix affiché</h2><p>Les notes BSG 1.1.0.0 du 3 août 2026 annoncent que la commission du Flea passe de 3 % à 5 %. Le même patch indique que les offres moyennes des traders ont évolué — achats +25 % en moyenne, rachats −20 % en moyenne — et que le changement économique concerne PvP Season, PvP Zone et PvE Zone.</p></div>{_fig('images/phase8/flea-market.jpg','Comptoir de troc souterrain fictif avec étagères génériques et éclairage industriel.','Image d’ambiance originale; aucun prix ou item EFT précis.',root)}</section>
<section class="guide-section phase8-section" id="flea-rules" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> Conditions et frais</p><h2>Ce que les notes établissent — et ce qu’elles ne calculent pas</h2><p>Les règles globales du patch sont sourcées; le client reste nécessaire pour le profil, l’annonce et l’offre actuelle.</p></div><div class="phase8-card-grid"><article class="phase8-card"><h3>Commission annoncée</h3><p>BSG annonce un changement de 3 % à 5 %. Ne transforme pas ce chiffre de patch en frais net universel de chaque annonce : lis le montant facturé par le client.</p></article><article class="phase8-card"><h3>Offres traders</h3><p>Les notes parlent de moyennes d’achats et de rachats, pas d’une variation identique pour chaque objet. Compare les offres actuelles du profil.</p></article><article class="phase8-card"><h3>Objets et accès</h3><p>Ce guide ne publie ni un niveau d’accès ni une règle FIR issue d’un export daté hors de la période de relecture. Vérifie les prérequis et restrictions de l’objet dans le client.</p></article><article class="phase8-card"><h3>Mode</h3><p>Les notes de patch incluent les trois profils dans le changement d’économie. Les disponibilités, conditions personnelles et offres doivent toujours être lues sur le bon personnage.</p></article></div><div class="phase8-table-wrap" tabindex="0" role="region" aria-label="Portée des règles Flea par mode"><table class="phase8-table"><caption>Portée d’après le patch BSG 1.1.0.0 · aucun cours live n’est publié ici.</caption><thead><tr><th scope="col">Mode</th><th scope="col">Profil</th><th scope="col">Changement économique</th><th scope="col">Contrôle</th></tr></thead><tbody>{rows}</tbody></table></div><div class="phase8-callout phase8-callout--warning"><strong>Le calculateur ci-dessous n’est pas un simulateur officiel de commission.</strong><p>Il applique seulement le taux effectif que tu saisis à ton prix demandé. Si le client affiche le frais exact, utilise ce montant directement pour comparer le net.</p></div><p class="phase8-note">BSG a aussi retiré le volume de ventes trader requis pour les niveaux de loyauté dans le patch 1.1.0.0. Cela ne permet pas de déduire une condition actuelle du Flea ou d’un compte précis.</p></section>
<section class="guide-section phase8-section" id="flea-calc" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>02</span> Comparateur simplifié</p><h2>Flea contre trader</h2><p>Renseigne le taux effectif que tu veux tester et l’offre trader affichée. Le coût d’acquisition est soustrait des deux résultats; laisse-le à zéro si tu veux comparer les produits nets.</p></div>{_flea_calc()}<p class="phase8-note">Hypothèse du modèle : prix Flea × taux saisi. Le modèle n’établit pas la commission du jeu et ne tire aucun taux par défaut.</p></section>
<section class="guide-section phase8-section" id="flea-check" tabindex="-1"><div class="phase8-section__heading"><p class="guide-kicker"><span>03</span> Avant de publier</p><h2>Une routine en cinq contrôles</h2></div><ol class="phase8-steps"><li>Confirme le personnage et le mode actifs.</li><li>Vérifie que l’objet peut être listé et que l’état/quantité est accepté par le client.</li><li>Compare les offres équivalentes; vérifie la quantité, la durée et le prix réellement demandé.</li><li>Relève le frais total affiché par le client, puis compare le gain net et la valeur de remplacement.</li><li>Après la vente, note le prix réalisé et la date; ne prends pas un cours passé comme promesse pour demain.</li></ol>{_cards(['economy','money','builds'],root)}</section>'''


def _money_calc():
    return '''<form class="phase8-form" data-p8-calc="money" novalidate><div class="phase8-form__grid"><label class="field" for="money-haul">Valeur nette récupérée si extraction réussie · ₽<input class="field__input" id="money-haul" type="number" min="0" step="1" inputmode="numeric" data-p8-input="haul" placeholder="Votre échantillon"></label><label class="field" for="money-survival">Probabilité de retour estimée par vous · %<input class="field__input" id="money-survival" type="number" min="0" max="100" step="1" inputmode="numeric" data-p8-input="survival" placeholder="Votre hypothèse"></label><label class="field" for="money-recovery">Valeur récupérée si échec · ₽<input class="field__input" id="money-recovery" type="number" min="0" step="1" inputmode="numeric" data-p8-input="recovery" placeholder="0 si inconnue"></label><label class="field" for="money-kit">Coût du kit par tentative · ₽<input class="field__input" id="money-kit" type="number" min="0" step="1" inputmode="numeric" data-p8-input="kit" placeholder="Votre coût"></label><label class="field" for="money-fixed">Consommables, assurance, accès et frais par tentative · ₽<input class="field__input" id="money-fixed" type="number" min="0" step="1" inputmode="numeric" data-p8-input="fixed" placeholder="Votre total"></label><label class="field" for="money-time">Durée d’une tentative · minutes<input class="field__input" id="money-time" type="number" min="0.1" step="0.1" inputmode="decimal" data-p8-input="time" placeholder="Votre mesure"></label></div><div class="phase8-form__actions"><button class="button button--primary" type="submit">Estimer mon scénario</button><button class="button button--quiet" type="reset">Effacer</button></div><div class="phase8-output" aria-live="polite" data-p8-result="money"><strong>En attente de vos données.</strong><p>Aucune probabilité ou valeur n’est fournie par le guide.</p></div></form>'''


def _money_content(root):
    return f'''<section class="phase8-intro" id="money-intro" tabindex="-1"><div><p class="guide-kicker">BOUCLES DE LOOT · RISQUE MESURÉ PAR TOI</p><h2>Le bon run est celui que tu peux répéter et extraire</h2><p>Choisis un circuit selon ta carte connue, ton mode, ton objectif et le coût que tu es prêt à risquer. Aucune route ne garantit un butin, une extraction ou un revenu par heure.</p></div>{_fig('images/phase8/money-run.jpg','Survivant fictif évaluant une route entre des bâtiments urbains détrempés.','Illustration originale, non une carte ou une sortie réelle.',root)}</section>
<section class="guide-section phase8-section" id="money-loops" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> Choisir une boucle</p><h2>Trois profils à tester selon ton stade</h2><p>Les cartes et points d’intérêt doivent être revérifiés pour le patch et le mode affichés dans le client.</p></div><div class="phase8-card-grid"><article class="phase8-card"><p class="phase8-card__eyebrow">Découverte / budget</p><h3>Scav sur une carte reconnue</h3><p>Choisis quelques repères et une sortie connue; évite d’ajouter un combat à l’objectif d’apprentissage. Le Scav réduit le coût d’équipement du profil PMC, mais le retour et le butin ne sont pas garantis.</p><ul><li>Priorité : apprendre orientation, inventaire et sortie.</li><li>Mesure : valeur effectivement rapportée, pas valeur trouvée.</li><li>Arrêt : extraire quand le sac ou l’objectif est suffisant.</li></ul></article><article class="phase8-card"><p class="phase8-card__eyebrow">PMC / progression</p><h3>Une route compatible avec une tâche</h3><p>Combine une tâche, des points de loot et une sortie de secours; ne traverse pas la carte pour un prix théorique. Les règles de profil et les coûts diffèrent.</p><ul><li>Priorité : compléter une tâche ou un objectif de planque.</li><li>Mesure : tentatives, coût du kit, extraction et ventes réelles.</li><li>Arrêt : abandonne un détour si le risque change.</li></ul></article><article class="phase8-card"><p class="phase8-card__eyebrow">Clé / forte valeur</p><h3>Inclure le coût d’entrée et le risque</h3><p>Une salle verrouillée ou une carte risquée n’est intéressante que si le coût, les usages restants, la concurrence et une sortie viable entrent dans ton budget.</p><ul><li>Priorité : connaître l’accès et l’itinéraire de retour.</li><li>Mesure : coût de clé, temps, extractions et pertes sur plusieurs raids.</li><li>Arrêt : ne risque pas un investissement que tu ne peux pas reperdre.</li></ul></article></div><div class="phase8-note"><strong>Exemple de créateur, pas rendement de référence :</strong> dans sa vidéo Interchange du 11 novembre 2026, Pestily décrit une session personnelle d’environ sept heures / quinze raids et cinq bitcoins. C’est un récit individuel; le mode et les prix ne sont pas une espérance représentative ni une promesse de profit.</div></section>
<section class="guide-section phase8-section" id="money-calc" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>02</span> Estimation utilisateur</p><h2>Comparer tes propres résultats</h2><p>Modèle : (p × valeur nette rapportée si extraction) + ((1−p) × valeur récupérée après échec) − kit − coûts fixes. La probabilité est ta supposition ou ta mesure, jamais une statistique du jeu.</p></div>{_money_calc()}<div class="phase8-callout phase8-callout--warning"><strong>Pour comparer honnêtement</strong><p>Note le mode, la carte, la période, PMC/Scav, les tentatives, les retours, les coûts et les prix réalisés. Sépare les événements et les gros butins; un seul raid ne donne pas une espérance.</p></div><noscript><p class="phase8-note">JavaScript désactivé : les boucles et les hypothèses restent consultables; le calcul ne s’exécute pas.</p></noscript>{_cards(['flea','economy','beginner'],root)}</section>
<section class="guide-section phase8-section" id="money-sources" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>03</span> Une observation attribuable</p><h2>Prendre l’idée, pas le montant</h2><p>La vidéo Pestily montre une route de caisses d’Interchange publiée le 11 novembre. Le parcours, les clés et les prix peuvent changer; la description et le transcript reflètent une session personnelle, pas un protocole contrôlé.</p></div><p class="phase8-note">Pour faire ton propre test, consigne plusieurs tentatives du même profil, puis note la valeur réellement extraite, les pertes, le temps et les frais. Ne recopie pas la quantité de bitcoins de la vidéo comme rendement attendu.</p></section>'''


def _strategy_content(root):
    options=''.join(f'<option value="{e(k)}">{e(v)}</option>' for k,v in {'all':'Tous les profils','regular':'PvP permanent','pvp-season':'PvP Seasonal','pve':'PvE Zone'}.items())
    cards=[
      ('regular','Profil permanent','Missions, cartes et coûts d’un profil PvP Zone. Vérifie le marché et les règles de ton personnage actuel.'),
      ('pvp-season','Saison KORD BREACH','Profil Seasonal séparé; les règles globales/personnelles varient. BSG indique notamment que l’assurance est désactivée en PvP Season.'),
      ('pve','PvE Zone','Raids PvE et profil distinct; patch 1.2.0.0 a ajouté Prestige PvE et modifié les bots, puis 1.3.0.0 a ajouté des PMC difficiles sur des lieux de haut niveau.'),
    ]
    modecards=''.join(f'<article class="phase8-card" data-p8-mode-card="{e(mode)}"><p class="phase8-card__eyebrow">{e(mode.upper())}</p><h3>{e(title)}</h3><p>{e(text)}</p></article>' for mode,title,text in cards)
    return f'''<section class="phase8-intro" id="strategy-intro" tabindex="-1"><div><p class="guide-kicker">CHOISIR UN PROFIL · RELECTURE DU 18 NOVEMBRE</p><h2>La meilleure stratégie dépend du mode, du but et de ton expérience</h2><p>Les dossiers ci-dessous séparent objectifs, PvP permanent, PvP Seasonal et PvE. Les citations d’expérience de joueurs restent des conseils, non une confirmation de mécanique.</p></div>{_fig('images/phase8/pvp-loadout.jpg','Équipements génériques de différentes tailles sur un établi fictif.','Aucun objet, coût ou statistique EFT n’est représenté.',root)}</section>
<section class="guide-section phase8-section" id="strategy-mode" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> Mode de jeu</p><h2>Filtrer le contexte</h2><p>Les trois cartes sont visibles sans JavaScript. Le filtre améliore la lecture si le script est activé.</p></div><label class="field phase8-mode-select" for="p8-strategy-mode">Afficher<select class="field__input" id="p8-strategy-mode" data-p8-strategy-mode>{options}</select></label><div class="phase8-card-grid" data-p8-mode-list>{modecards}</div><p class="phase8-result-count" aria-live="polite" data-p8-mode-count>3 contextes listés.</p></section>
<section class="guide-section phase8-section" id="strategy-guides" tabindex="-1"><div class="phase8-section__heading"><p class="guide-kicker"><span>02</span> Guides</p><h2>Choisis la question du prochain raid</h2></div>{_cards(['beginner','advanced','pvp','pve','builds','money'],root)}</section>
<section class="guide-section phase8-section" id="strategy-date" tabindex="-1"><div class="phase8-section__heading"><p class="guide-kicker"><span>03</span> Ce qui peut changer</p><h2>Vérification de patch et de provenance</h2></div><div class="phase8-callout"><strong>1.3.5.0 : dernière annonce officielle relevée</strong><p>Le journal BSG du 18 novembre décrit 1.3.5.0 comme planifié pour la seconde moitié de novembre. Il annonce des améliorations techniques et une transition Unity 6; ce journal constitue une annonce de planification, pas une confirmation de déploiement.</p></div><p class="phase8-note">Les sources officielles fixent les règles publiées. Les API et trackers communautaires donnent un relevé utile mais agrégé; Reddit, vidéos et tier lists reflètent des expériences datées et parfois contradictoires. Revalide les offres et la disponibilité en jeu.</p></section>'''


def _tips_content(root):
    category_labels={'all':'Toutes','preparer':'Préparer','repere':'Se repérer','combat':'Contact','loot':'Loot & budget','apres':'Après raid'}
    options=''.join(f'<option value="{e(k)}">{e(v)}</option>' for k,v in category_labels.items())
    cards=[]
    for i,(category,title,text) in enumerate(TIPS,1):
        ident=f'tip-{i:02d}'
        cards.append(f'<article class="phase8-tip" data-p8-tip data-p8-category="{e(category)}" data-p8-text="{e((title+" "+text).lower())}" id="{ident}"><div class="phase8-tip__number">{i:02d}</div><div class="phase8-tip__copy"><p class="phase8-tip__group">{e(category_labels[category])}</p><h3>{e(title)}</h3><p>{e(text)}</p></div><button type="button" class="phase8-favorite" data-p8-favorite="{ident}" aria-pressed="false" aria-label="Ajouter aux favoris : {e(title)} — Favori">☆ <span>Favori</span></button></article>')
    return f'''<section class="phase8-intro" id="tips-intro" tabindex="-1"><div><p class="guide-kicker">61 REPÈRES · 5 THÈMES</p><h2>Des habitudes utiles, pas des règles universelles</h2><p>Ces conseils sont des repères éditoriaux de préparation et d’apprentissage, pas des règles officielles. Ils ne garantissent ni extraction, ni victoire, ni revenu. Les favoris sont enregistrés uniquement dans ce navigateur.</p></div>{_fig('images/phase8/strategy-brief.jpg','Table de briefing fictive, carte abstraite et jetons.','Illustration originale sans repère de carte de jeu.',root)}</section>
<section class="guide-section phase8-section" id="tips-controls" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> Filtrer</p><h2>Rechercher un repère</h2><p>La liste complète reste présente dans le document; la recherche et les favoris sont des améliorations locales.</p></div><div class="phase8-filter-grid"><label class="field" for="p8-tip-search">Mot-clé<input class="field__input" id="p8-tip-search" type="search" placeholder="Ex. sortie, son, frais…" data-p8-tip-search></label><label class="field" for="p8-tip-category">Thème<select class="field__input" id="p8-tip-category" data-p8-tip-category>{options}</select></label><label class="field phase8-check-label"><input type="checkbox" data-p8-only-favorites> Mes favoris uniquement</label><button class="button button--quiet" type="button" data-p8-clear-favorites>Effacer les favoris locaux</button></div><p class="phase8-result-count" aria-live="polite" data-p8-tip-count>{len(TIPS)} astuces affichées.</p></section>
<section class="guide-section phase8-section" id="tips-list" tabindex="-1"><div class="phase8-tip-list">{''.join(cards)}</div><noscript><p class="phase8-note">JavaScript désactivé : les {len(TIPS)} astuces restent visibles; filtre et favoris sont indisponibles.</p></noscript></section>
<section class="guide-section phase8-section" id="tips-sources" tabindex="-1"><div class="phase8-section__heading"><p class="guide-kicker"><span>02</span> Méthode</p><h2>Utiliser les conseils avec discernement</h2><p>Ces repères peuvent être adaptés à ton style. Les avis sur le sprint, l’audio, le combat et la route « optimale » divergent; aucune préférence n’est présentée comme une loi mécanique.</p></div><p class="phase8-note">Le patch BSG 1.1.0.0 confirme l’indépendance des profils Seasonal, et précise que l’assurance est désactivée en PvP Season. Les notes 1.2/1.3 ont modifié les bots PvE; les anecdotes d’IA d’avant ces patchs ne sont donc pas une base actuelle. Vérifie chaque système dans le client.</p>{_cards(['strategy','advanced','pvp'],root)}</section>'''


def _advanced_content(root):
    return f'''<section class="phase8-intro" id="tactics-intro" tabindex="-1"><div><p class="guide-kicker">TACTIQUES DE JEU · DÉCISION SOUS INCERTITUDE</p><h2>Lire l’information avant d’engager une action</h2><p>Les tactiques ci-dessous décrivent des décisions dans Escape from Tarkov, pas des règles garanties de moteur. Son, IA, visibilité et réseau peuvent évoluer avec les mises à jour.</p></div>{_fig('images/phase8/strategy-brief.jpg','Brief fictif avec grille de rue illisible, boussole et jetons.','Illustration abstraite, pas une carte EFT.',root)}</section>
<section class="guide-section phase8-section" id="tactics-loop" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> Boucle de décision</p><h2>Avant, pendant et après un contact</h2></div><div class="phase8-steps-grid"><article class="phase8-card"><span class="phase8-step-index">01</span><h3>Choisir une priorité</h3><p>Définis l’objectif de raid, l’issue minimale acceptable et le risque de perdre ton kit.</p></article><article class="phase8-card"><span class="phase8-step-index">02</span><h3>Préserver les options</h3><p>Avant une zone risquée, garde stamina, une voie de repli et assez d’information pour changer de route.</p></article><article class="phase8-card"><span class="phase8-step-index">03</span><h3>Mettre à jour le plan</h3><p>Un tir, une silhouette ou un bruit modifie l’estimation; ce n’est pas une preuve de nombre, distance ou intention.</p></article><article class="phase8-card"><span class="phase8-step-index">04</span><h3>Décider, puis vérifier</h3><p>Engager, attendre, contourner ou extraire sont des choix. Après le raid, compare le résultat à l’objectif initial.</p></article></div></section>
<section class="guide-section phase8-section" id="tactics-scenarios" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>02</span> Scénarios</p><h2>Explorer les alternatives</h2><p>Les accordéons restent disponibles au clavier; les scénarios ne sont pas des scripts de victoire.</p></div><div class="phase8-disclosures"><details class="phase8-disclosure"><summary>Tu entends un bruit mais ne vois personne</summary><div><p>Arrête le déplacement si tu as un couvert et que l’information compte; compare le son avec le matériau, l’intérieur/extérieur et ton propre équipement. Si tu es exposé, rejoindre un abri peut être plus sûr que rester immobile.</p><p><strong>Alternative :</strong> poursuivre si ton objectif est urgent et que la voie est dégagée. Ne déduis pas un nombre exact d’adversaires d’un seul son.</p></div></details><details class="phase8-disclosure"><summary>Tu gagnes un duel mais un autre bruit arrive</summary><div><p>Ne confonds pas victoire et zone sécurisée. Recharge ou soigne dans un endroit protégé si possible, puis choisis un nouvel angle ou quitte la zone avant de fouiller.</p><p><strong>Alternative :</strong> si le butin est nécessaire, limite-toi à un objet prioritaire et garde le plan d’extraction.</p></div></details><details class="phase8-disclosure"><summary>Tu es en infériorité ou tu ignores la taille du groupe</summary><div><p>Évite de rester visible depuis plusieurs voies. Cherche une séparation par la géométrie du jeu, contourne ou romps le contact si ton objectif le permet.</p><p><strong>Alternative :</strong> tenir un angle peut convenir si tu contrôles l’accès et sais où sortir; répéter le même peek après avoir été repéré est une autre décision.</p></div></details><details class="phase8-disclosure"><summary>Tu as trouvé un objet utile mais l’extraction s’éloigne</summary><div><p>Compare la valeur pour la tâche, le risque de détour et ta capacité à atteindre une autre sortie. Le prix affiché ne vaut rien tant que l’objet n’est pas ramené.</p><p><strong>Alternative :</strong> abandonner le détour peut être rationnel si la survie est la priorité.</p></div></details><details class="phase8-disclosure"><summary>Tu joues en PvE et un PMC bot apparaît</summary><div><p>Les notes 1.2.0.0 indiquent des bots plus mobiles vers les points d’intérêt et tâches; 1.3.0.0 ajoute des bots à haute difficulté sur des lieux de haut niveau et corrige leur hostilité envers les joueurs. Les notes ne publient pas de liste complète de lieux, de distance ou de taux.</p><p><strong>Alternative :</strong> traite les vidéos et commentaires de joueurs comme des observations datées, pas comme une prédiction reproductible.</p></div></details></div></section>
<section class="guide-section phase8-section" id="tactics-ai" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>03</span> Limites techniques</p><h2>Audio, stamina, IA et réseau</h2><p>Les sources officielles changent le comportement du jeu, mais ne publient pas toujours les coefficients. N’intègre pas un seuil exact d’audio, un délai de fatigue ou une garantie de reconnexion sans mesure du patch en client.</p></div><div class="phase8-callout"><strong>1.3.5.0 est encore « planifié » dans le journal BSG du 18 novembre.</strong><p>Ce journal décrit une transition Unity 6 et des changements techniques à venir. Au relevé du 19 novembre, on ne le traite pas comme un patch déployé.</p></div>{_cards(['skills','pve','pvp'],root)}</section>'''


def _pvp_content(root):
    modes=[
      ('regular','PvP permanent','Profil permanent distinct du personnage Seasonal. Choisis une carte et un objectif selon tes tâches et ton budget.'),
      ('pvp-season','PvP Seasonal · KORD BREACH','Profil Seasonal indépendant des profils PvP Zone et PvE Zone. Les notes BSG 1.1.0.0 indiquent que l’assurance est désactivée en PvP Season; vérifie aussi les modificateurs personnels/globalement actifs.'),
    ]
    panels=''.join(f'<article class="phase8-card" data-p8-pvp-panel="{e(mode)}"><p class="phase8-card__eyebrow">{e(mode.upper())}</p><h3>{e(title)}</h3><p>{e(text)}</p></article>' for mode,title,text in modes)
    select=''.join(f'<option value="{e(k)}">{e(v)}</option>' for k,v in {'all':'Les deux profils','regular':'PvP permanent','pvp-season':'PvP Seasonal'}.items())
    return f'''<section class="phase8-intro" id="pvp-intro" tabindex="-1"><div><p class="guide-kicker">PVP · PROFIL ET PRÉPARATION</p><h2>Une bonne session commence avant la file d’attente</h2><p>Les rencontres entre joueurs sont imprévisibles. Ce guide privilégie les objectifs, les budgets et la revue des décisions, sans promettre un taux de victoire ni un build optimal.</p></div>{_fig('images/phase8/advanced-tactics.jpg','Deux opérateurs fictifs utilisent les côtés d’une rue urbaine comme couvert.','Scène de fiction, sans recommandations hors du jeu.',root)}</section>
<section class="guide-section phase8-section" id="pvp-mode" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> Choix du profil</p><h2>PvP permanent et Seasonal ne sont pas interchangeables</h2><p>Les notes BSG 1.1.0.0 définissent des profils séparés et des règles Seasonal; le guide ne transpose pas les paramètres d’assurance d’un profil à l’autre.</p></div><label class="field phase8-mode-select" for="p8-pvp-mode">Comparer<select class="field__input" id="p8-pvp-mode" data-p8-pvp-mode>{select}</select></label><div class="phase8-card-grid">{panels}</div><p class="phase8-result-count" aria-live="polite" data-p8-pvp-count>Deux contextes documentés.</p><div class="phase8-callout phase8-callout--warning"><strong>Règle Seasonal importante</strong><p>Dans les notes officielles 1.1.0.0, l’assurance s’applique au PvP Zone et au PvE Zone, et est désactivée en PvP Season. Un chargement sauvegardé ou un vieux guide ne suffit pas : regarde le mode affiché avant d’investir dans un kit.</p></div></section>
<section class="guide-section phase8-section" id="pvp-kit" tabindex="-1"><div class="phase8-section__heading"><p class="guide-kicker"><span>02</span> Choix du kit</p><h2>Trois profils de préparation, sans prix fixe</h2><p>Remplace les cases par les articles réellement disponibles chez toi et vérifie les compatibilités dans le client.</p></div><div class="phase8-card-grid"><article class="phase8-card"><p class="phase8-card__eyebrow">Coût contenu</p><h3>Une arme maîtrisée, une sortie familière</h3><p>Choisis une plateforme accessible, les munitions que tu peux obtenir dans le mode et les protections que tu peux remplacer. Pas de liste d’objets figée ici : stocks et prix changent.</p></article><article class="phase8-card"><p class="phase8-card__eyebrow">Quête</p><h3>Construire autour de l’objectif</h3><p>Vérifie le matériel requis dans le journal. Réduis les options non essentielles si l’objectif est de survivre et d’extraire plutôt que de chercher le combat.</p></article><article class="phase8-card"><p class="phase8-card__eyebrow">Entraînement PvP</p><h3>Mesurer un seul axe</h3><p>Utilise plusieurs raids pour tester une carte, une arme ou un choix de distance. Enregistre les résultats; ne juge pas un setup sur un seul duel.</p></article></div></section>
<section class="guide-section phase8-section" id="pvp-review" tabindex="-1"><div class="phase8-section__heading"><p class="guide-kicker"><span>03</span> Bilan</p><h2>Après le contact</h2></div><ol class="phase8-steps"><li>Quelles informations as-tu réellement eues avant de tirer ?</li><li>Quelle ressource a changé la décision : couverture, santé, stamina, chargeur, coéquipier ou sortie ?</li><li>As-tu révélé ta position, puis répété l’angle ? Était-ce nécessaire ?</li><li>La dépense et la perte du kit étaient-elles compatibles avec ton budget ?</li><li>Après plusieurs raids, quel seul changement veux-tu tester au prochain ?</li></ol>{_cards(['builds','advanced','money'],root)}</section>'''


def _pve_content(root):
    tiers=''.join(f'<option value="{i}">Prestige PvE {i}</option>' for i in range(1,7))
    categories=[('level','Niveau du personnage'),('tasks','Tâches'),('hideout','Zones de la planque'),('story','Histoire principale'),('items','Objets et montant de roubles'),('skills','Niveaux de compétence')]
    checks=''.join(f'<label class="phase8-check"><input type="checkbox" value="{e(k)}" data-p8-prestige-check><span>{e(v)}</span></label>' for k,v in categories)
    return f'''<section class="phase8-intro" id="pve-intro" tabindex="-1"><div><p class="guide-kicker">PVE ZONE · OFFICIEL, EXPORT ET TÉMOIGNAGE SÉPARÉS</p><h2>Coopération PvE ne signifie pas mode hors ligne</h2><p>Ce dossier couvre le PvE Zone officiel. L’IA et Prestige ont évolué dans les patches 1.2.0.0 et 1.3.0.0; les anecdotes vidéo/Reddit indiquent une expérience individuelle, pas une mécanique garantie.</p></div>{_fig('images/phase8/pve-prestige.jpg','Sac et objets de progression conservés dans une planque fictive avant un nouveau départ.','Illustration originale, pas un écran ou une récompense du jeu.',root)}</section>
<section class="guide-section phase8-section" id="pve-ai" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> PMC bots</p><h2>Changements officiels des patches 1.2 et 1.3</h2><p>Les notes de patch documentent des changements; elles ne donnent pas tous les lieux, taux ou distances.</p></div><div class="phase8-card-grid"><article class="phase8-card"><p class="phase8-card__eyebrow">Patch 1.2.0.0 · 6 octobre 2026</p><h3>Spawn et mouvement</h3><p>Les PMC bots sont présents au début d’un raid de lieu, leurs nombres varient moins, leurs apparitions sont plus étalées et ils se dirigent davantage vers les points d’intérêt et les tâches. Des PMC bots ont aussi été ajoutés à The Labyrinth.</p></article><article class="phase8-card"><p class="phase8-card__eyebrow">Patch 1.2.0.0 · équipement</p><h3>Factions et niveaux</h3><p>Les bots USEC/BEAR se coordonnent plus souvent; leur équipement, leurs armes et leur difficulté dépendent du niveau et de la faction. Les notes ne permettent pas de prédire chaque rencontre ou le comportement de chaque squad.</p></article><article class="phase8-card"><p class="phase8-card__eyebrow">Patch 1.3.0.0 · 29 octobre 2026</p><h3>Hostilité et difficulté élevée</h3><p>Des PMC bots à haute difficulté peuvent apparaître sur des lieux de haut niveau. Une correction indique que les PMC bots considèrent désormais les joueurs comme hostiles. BSG ne nomme pas ici toutes les cartes ou tous les taux de spawn.</p></article></div><div class="phase8-callout phase8-callout--warning"><strong>Ne copie pas un comportement de bot depuis une vieille vidéo</strong><p>Les témoignages 2024 et les descriptions pré-1.2 précèdent ces changements. Même les retours post-patch reflètent un échantillon et peuvent différer par lieu, difficulté et version.</p></div></section>
<section class="guide-section phase8-section" id="pve-prestige" tabindex="-1"><div class="phase8-section__heading"><p class="guide-kicker"><span>02</span> Prestige</p><h2>Six paliers PvE, réinitialisation volontaire</h2><p>Selon les notes BSG 1.2.0.0, chaque palier réinitialise la progression du profil PvE uniquement. Certains équipements, compétences et maîtrises d’armes peuvent être conservés, jusqu’à 50 %.</p></div><div class="phase8-callout"><strong>Les notes officielles ne donnent pas ici les exigences numériques de chaque palier ni le pourcentage exact conservé.</strong><p>Elles citent les catégories possibles : niveau, tâches, zones de la planque, histoire principale, objets/argent et compétences. Lis les exigences en jeu pour le palier choisi; ce sélecteur ne les devine pas.</p></div><label class="field phase8-mode-select" for="p8-prestige-tier">Palier que tu envisages<select class="field__input" id="p8-prestige-tier" data-p8-prestige-tier>{tiers}</select></label><p class="phase8-result-count" aria-live="polite" data-p8-prestige-status>Checklist locale — Prestige PvE 1.</p><div class="phase8-check-grid" data-p8-prestige-list>{checks}</div><div class="phase8-form__actions"><button class="button button--quiet" type="button" data-p8-prestige-reset>Effacer le suivi local de ce palier</button></div><p class="phase8-note">Ces cases sont un aide-mémoire dans ce navigateur seulement; aucune case ne vérifie le profil ou n’autorise l’action. Le reset est une décision du jeu, pas une sauvegarde transférée par ce guide.</p></section>
<section class="guide-section phase8-section" id="pve-checklist" tabindex="-1"><div class="phase8-section__heading"><p class="guide-kicker"><span>03</span> Avant de confirmer</p><h2>Contrôles de prudence</h2></div><ol class="phase8-steps"><li>Capture ou relève la liste exacte du palier affiché dans ton client.</li><li>Vérifie les objets et les roubles exigés; ne te base pas sur une tier list ou un guide ancien.</li><li>Décide quelles progressions, équipements et missions tu acceptes de réinitialiser.</li><li>Vérifie que tu es bien dans le profil PvE; les notes BSG décrivent une réinitialisation limitée à la PvE Zone.</li><li>Si tu hésites, ne confirme pas le reset; demande une source officielle actuelle avant de consommer les prérequis.</li></ol><p class="phase8-note">Une vidéo du 10 novembre montre une progression personnelle après Prestige; elle est utile pour voir une session, mais ne remplace pas les exigences du client. <a href="https://www.youtube.com/watch?v=lnf9w_KkIzU" rel="noopener noreferrer">Voir le témoignage vidéo <span aria-hidden="true">↗</span></a></p>{_cards(['skills','beginner','money'],root)}</section>'''


def _build_calc():
    rows=[('weapon','Arme et pièces'),('ammo','Munitions'),('armor','Protection'),('rig','Gilet/sac'),('headset','Casque audio'),('medical','Soins'),('other','Autres coûts')]
    fields=''.join(f'<label class="field" for="build-{e(key)}">{e(label)} · ₽<input class="field__input" id="build-{e(key)}" type="number" min="0" step="1" inputmode="numeric" data-p8-build-cost="{e(key)}" placeholder="Prix du mode actif"></label>' for key,label in rows)
    return f'''<form class="phase8-form" data-p8-calc="build" novalidate><div class="phase8-form__grid"><label class="field" for="build-mode">Mode<select class="field__input" id="build-mode" data-p8-build-mode>{''.join(f'<option value="{e(k)}">{e(v)}</option>' for k,v in MODES.items())}</select></label><label class="field" for="build-budget">Budget maximum · ₽<input class="field__input" id="build-budget" type="number" min="0" step="1" inputmode="numeric" data-p8-build-budget placeholder="Ton budget"></label>{fields}</div><div class="phase8-form__actions"><button class="button button--primary" type="submit">Calculer les coûts saisis</button><button class="button button--quiet" type="reset">Effacer</button></div><div class="phase8-output" aria-live="polite" data-p8-result="build"><strong>En attente de prix saisis.</strong><p>Aucune pièce, compatibilité ou cotation n’est préremplie.</p></div></form>'''


def _build_content(root):
    return f'''<section class="phase8-intro" id="builds-intro" tabindex="-1"><div><p class="guide-kicker">BUILDS · META · 18 NOVEMBRE 2026</p><h2>Un build est un compromis de mode, disponibilité et scénario</h2><p>Ce guide ne publie pas de classement de modèles : aucune tier list communautaire ne prouve à elle seule un « meilleur » fusil pour chaque profil, prix, patch ou style de jeu.</p></div>{_fig('images/phase8/economy-ledger.jpg','Registre de coûts fictif sur un établi de planque.','Illustration éditoriale; aucune cotation ou pièce réelle n’est fournie.',root)}</section>
<section class="guide-section phase8-section" id="build-rubric" tabindex="-1"><div class="phase8-section__heading"><p class="guide-kicker"><span>01</span> Rubrique S–D</p><h2>Critères éditoriaux pour classer un preset</h2><p>Cette échelle est notre outil de décision, non un rang officiel ou une statistique du jeu.</p></div><div class="phase8-table-wrap" tabindex="0" role="region" aria-label="Critères éditoriaux de classement des builds"><table class="phase8-table"><caption>Évaluer pour un profil, un mode, un patch et une fourchette de budget donnés.</caption><thead><tr><th scope="col">Tier</th><th scope="col">Interprétation éditoriale</th><th scope="col">Contrôle requis</th></tr></thead><tbody><tr><th scope="row">S</th><td>Très bon ajustement à ce scénario</td><td>Compatibilité, disponibilité, coût et munitions confirmés pour le mode.</td></tr><tr><th scope="row">A</th><td>Bon choix, un compromis acceptable</td><td>Au moins une alternative de pièce ou de plateforme vérifiée.</td></tr><tr><th scope="row">B</th><td>Situationnel</td><td>Fonctionne avec une carte, distance ou progression particulière.</td></tr><tr><th scope="row">C</th><td>Coûteux ou difficile à justifier ici</td><td>Un profil moins cher peut remplir le même rôle.</td></tr><tr><th scope="row">D</th><td>Inadapté à ce scénario</td><td>Incompatible, indisponible ou hors budget selon les valeurs saisies.</td></tr></tbody></table></div><p class="phase8-note">Sans feuille de patch, données d’items par mode et prix datés, nous ne donnons pas de rang S–D à un modèle d’arme. Les valeurs d’ergonomie/recul ne remplacent pas la compatibilité ou l’accès au trader.</p></section>
<section class="guide-section phase8-section" id="build-examples" tabindex="-1"><div class="phase8-section__heading"><p class="guide-kicker"><span>02</span> Profils d’usage</p><h2>Trois plans de kit sans prix inventé</h2></div><div class="phase8-card-grid"><article class="phase8-card"><p class="phase8-card__eyebrow">Économique</p><h3>Pièces déjà disponibles</h3><p>Choisis une arme et des munitions que tu peux alimenter dans ton mode, puis un minimum de protection et de soins adaptés à l’objectif. Préserve le budget pour les répétitions.</p></article><article class="phase8-card"><p class="phase8-card__eyebrow">Mission</p><h3>Compatible avec le journal</h3><p>Vérifie le type d’arme, l’emplacement et les objets de mission dans le client avant d’acheter des mods. N’ajoute que les améliorations utiles à ta distance de combat.</p></article><article class="phase8-card"><p class="phase8-card__eyebrow">Engagement précis</p><h3>Construis autour de la distance</h3><p>Choisis la maniabilité et l’optique selon le terrain et l’accès aux munitions; contrôle la stat affichée après chaque pièce. Le build d’un créateur est un point de départ, pas une garantie.</p></article></div></section>
<section class="guide-section phase8-section" id="build-tool" tabindex="-1"><div class="phase8-section__heading"><p class="guide-kicker"><span>03</span> Calculateur local</p><h2>Additionner les coûts que tu vois</h2><p>Le total ne vérifie ni compatibilité, ni stats, ni achat possible, ni restrictions du mode. Saisis les valeurs affichées dans le client ou un marché correspondant au même mode.</p></div>{_build_calc()}<noscript><p class="phase8-note">JavaScript désactivé : les profils et critères restent lisibles; le calcul n’est pas disponible.</p></noscript><p class="phase8-note">Tarkov.dev agrège des données de jeu et de communauté; TarkovGunsmith documente des essais de placement de presets sur un snapshot d’octobre. Aucun ne prouve qu’un preset soit optimal ou disponible au prix annoncé aujourd’hui.</p>{_cards(['pvp','flea','economy'],root)}</section>'''


def _content(page, root):
    ident=page['id']
    if ident=='skills': return _skills_content(root)
    if ident=='economy': return _economy_content(root)
    if ident=='flea': return _flea_content(root)
    if ident=='money': return _money_content(root)
    if ident=='strategy': return _strategy_content(root)
    if ident=='beginner': return _tips_content(root)
    if ident=='advanced': return _advanced_content(root)
    if ident=='pvp': return _pvp_content(root)
    if ident=='pve': return _pve_content(root)
    if ident=='builds': return _build_content(root)
    raise ValueError('Page PHASE_8 non reconnue: '+ident)


def _render_page(page, sources, base, patch):
    root='../../'
    canonical=canonical_link(base,page['route'])
    og_url=open_graph_url_meta(base,page['route'])
    og_image=urljoin(base,page['hero'])
    review_dt=date.fromisoformat(REVIEW)
    schema={'@context':'https://schema.org','@type':'WebPage','name':page['title'],'inLanguage':'fr-FR','description':page['lead'],
            'dateModified':review_dt.isoformat(),'isPartOf':{'@type':'WebSite','name':'Tarkov Ultimate Guide'}}
    if seo_base_is_public(base): schema['url']=urljoin(base,page['route'])
    jsonld=json.dumps(schema,ensure_ascii=False,separators=(',',':')).replace('<',r'\u003c')
    nav=_nav(root,page['route'])
    sidebar=''.join(f'<li><a href="{e(root+route)}"'+(' aria-current="page"' if route==page['route'] else '')+f'>{e(label)}</a></li>' for route,label in NAV_PAGES)
    content=_content(page,root)
    sources_html=_source_html(page['sources'],sources)
    related=_cards(RELATED[page['id']],root)
    return f'''<!doctype html>
<html lang="fr-FR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(page['title'])} · Guide Tarkov | Tarkov Ultimate Guide</title><meta name="description" content="{e(page['lead'])}"><meta name="theme-color" content="#111411">
<link rel="preload" href="{root}fonts/inter-400-700.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="{root}fonts/type.css"><link rel="stylesheet" href="{root}css/main.css"><link rel="stylesheet" href="{root}css/components.css"><link rel="stylesheet" href="{root}css/animations.css"><link rel="stylesheet" href="{root}css/responsive.css"><link rel="stylesheet" href="{root}css/pages/home.css"><link rel="stylesheet" href="{root}css/pages/guides.css"><link rel="stylesheet" href="{root}css/pages/phase6.css"><link rel="stylesheet" href="{root}css/pages/phase7.css"><link rel="stylesheet" href="{root}css/pages/phase8.css">
{canonical}<meta property="og:title" content="{e(page['title'])} · Tarkov Ultimate Guide"><meta property="og:description" content="{e(page['lead'])}"><meta property="og:type" content="article">{og_url}<meta property="og:image" content="{e(og_image)}"><script type="application/ld+json">{jsonld}</script><script src="{root}js/main.js" type="module"></script><script src="{root}js/phase8.js" type="module"></script></head>
<body class="home-page guide-page phase8-page" data-phase8-page="{e(page['id'])}" data-phase8-root="{root}" data-phase8-route="{e(page['route'])}" data-phase8-review="{e(REVIEW)}" data-phase8-patch="{e(patch)}">
<a class="skip-link" href="#main">Aller au contenu</a><header class="site-header home-header" data-site-header><div class="shell site-header__inner"><a class="brand" href="{root}"><span class="brand__mark" aria-hidden="true"></span><span><span class="brand__word">TARKOV</span><span class="brand__descriptor">Ultimate Guide</span></span><span class="sr-only">, accueil</span></a>{nav}
<div class="site-header__utilities"><a class="badge badge--live home-header__patch" href="{root}#etat-du-jeu" aria-label="Patch de référence {e(patch)}">{e(patch)}</a><button type="button" class="button button--quiet home-header__search" data-modal-open="site-search" data-site-search-trigger aria-label="Rechercher dans le guide" aria-haspopup="dialog" aria-controls="site-search" aria-keyshortcuts="Control+K Meta+K" hidden><i class="icon icon--search" aria-hidden="true"></i><span class="button__text">Rechercher</span><kbd class="search-key" data-keyhint="Ctrl K" aria-hidden="true"></kbd></button><button type="button" class="button button--icon" data-nav-toggle aria-label="Menu de navigation" aria-controls="global-nav" aria-expanded="false" hidden><i class="icon icon--menu" aria-hidden="true"></i></button></div></div></header>
<main id="main" tabindex="-1"><nav class="phase8-breadcrumb" aria-label="Fil d’Ariane"><a href="{root}">Accueil</a><span aria-hidden="true">/</span><a href="{e(root+('pages/skills/' if page['id']=='skills' else 'pages/economy/' if page['id'] in ('economy','flea','money') else 'pages/strategy/'))}">{e('Compétences' if page['id']=='skills' else 'Économie' if page['id'] in ('economy','flea','money') else 'Stratégies')}</a><span aria-hidden="true">/</span><span aria-current="page">{e(page['label'])}</span></nav>
<section class="guide-hero phase6-hero phase7-hero phase8-hero" id="top" tabindex="-1" aria-labelledby="phase8-h1" data-motion-hero><img class="guide-hero__image" src="{e(root+page['hero'])}" width="1376" height="768" alt="{e(page['alt'])}" fetchpriority="high" decoding="async"><div class="shell guide-hero__inner"><div class="guide-hero__copy"><p class="guide-kicker"><span>{e(page['code'])}</span> PHASE_8 · {e(page['label'])}</p><h1 id="phase8-h1">{e(page['title'])}</h1><p class="guide-hero__lead">{e(page['lead'])}</p><div class="guide-hero__actions"><a class="button button--primary" href="#{e(page['quick'][0][0])}">{e(page['quick'][0][2])} <span aria-hidden="true">↓</span></a><a class="button button--quiet" href="#sources">Sources datées <span aria-hidden="true">↘</span></a></div><p class="guide-hero__note">Relu le {e(REVIEW_DATE)} · sources officielles, outils communautaires et témoignages séparés</p></div><p class="guide-hero__locator" aria-hidden="true">Illustration éditoriale originale · JPG</p></div></section>
<div class="guide-quick phase7-quick phase8-quick" role="group" aria-label="Accès rapide au dossier"><div class="shell guide-quick__inner">{_quick(page)}</div></div><div class="shell guide-layout phase6-layout phase7-layout phase8-layout"><aside class="guide-rail phase8-rail" aria-label="Navigation compétences, économie et stratégies"><p class="guide-rail__tag">PHASE_8 / 10 routes</p><h2>Explorer</h2><nav aria-label="Pages de la PHASE_8"><ol>{sidebar}</ol></nav><div class="guide-rail__foot"><span>Dernière relecture</span><span>{e(REVIEW_DATE)}</span></div></aside><article class="guide-content phase6-content phase7-content phase8-content" aria-label="{e(page['title'])}">{content}<section class="guide-section guide-sources phase6-sources phase7-sources phase8-sources" id="sources" tabindex="-1" aria-labelledby="phase8-sources-title"><div class="guide-section__heading"><p class="guide-kicker"><span>REF</span> Relecture du 18 novembre</p><h2 id="phase8-sources-title">Sources, modes et limites</h2><p>Les notes BSG établissent les règles publiées; les outils communautaires sont des références secondaires; les vidéos et discussions montrent des expériences datées. Aucun prix courant, rendement fixe ou taux de victoire n’est présenté comme vérifié.</p></div><ul class="phase8-source-list">{sources_html}</ul></section><div class="guide-next phase6-next"><div><p class="guide-kicker">À lire ensuite</p><h2>Continuer le dossier</h2><p>Comparer les sujets liés à la même progression ou au même mode.</p></div>{related}</div></article></div></main>
<footer class="home-footer guide-footer"><div class="shell guide-footer__inner"><div><a class="brand" href="{root}"><span class="brand__mark" aria-hidden="true"></span><span><span class="brand__word">TARKOV</span><span class="brand__descriptor">Ultimate Guide</span></span><span class="sr-only">, accueil</span></a><p>Fan-site francophone indépendant de Battlestate Games. Illustrations originales générées; elles ne sont ni captures ni représentations officielles.</p></div><div class="guide-footer__controls"><a href="{root}">Retour à l’accueil <span aria-hidden="true">↗</span></a><div class="home-footer__settings"><button type="button" class="button button--quiet button--xs" data-contrast-toggle aria-pressed="false" hidden>Contraste renforcé</button><button type="button" class="button button--quiet button--xs" data-motion-toggle aria-pressed="false" hidden>Réduire les animations</button></div></div></div></footer><a class="button button--icon back-top" data-back-top href="#top" aria-label="Retour rapide en haut" hidden></a>
<dialog id="site-search" class="dialog home-search" data-modal data-site-search data-search-base="{root}" data-search-source="{root}js/data/search-index.json" aria-labelledby="search-title"><header class="dialog__head"><div><p class="eyebrow">Index du guide</p><h2 class="dialog__title" id="search-title">Rechercher dans Tarkov Ultimate Guide</h2></div><button type="button" class="button button--icon" data-modal-close aria-label="Fermer la recherche"><i class="icon icon--close" aria-hidden="true"></i></button></header><div class="dialog__body"><label for="site-query" class="field">Sujet, équipement ou compétence<span class="field__wrap"><i class="icon icon--search" aria-hidden="true"></i><input class="field__input field__input--search" id="site-query" type="search" placeholder="Ex. Flea, Métabolisme, extraction" autocomplete="off" data-modal-initial data-search-input></span></label><p class="dialog__hint search-status" role="status" data-search-status></p><ul class="search-results" data-search-results aria-label="Résultats de recherche"></ul><p class="search-dialog__foot"><span><kbd>↑</kbd> <kbd>↓</kbd> Parcourir</span><span><kbd>Entrée</kbd> Ouvrir</span><span>Échap Fermer</span></p></div></dialog></body></html>'''


def build_phase8(base, patch, read, compact):
    # Pages, index de recherche et date éditoriale au format date-only.
    source_doc = json.loads(read('docs/sources.json'))
    sources = source_doc['sources']
    review_date = date.fromisoformat(REVIEW)
    output = {}
    search = []
    for page in PAGES:
        output[page['file']] = _render_page(page, sources, base, patch)
        search.append({'title': page['title'], 'href': page['route'], 'tag': 'PHASE_8 · ' + page['label'],
                       'summary': page['lead'],
                       'keywords': [page['id'], page['label'], 'compétences', 'économie', 'Flea', 'PvE', 'PvP', 'Seasonal', 'stratégie']})
    return output, search, review_date


def validate_phase8():
    errors = []
    source_doc = json.loads((ROOT / 'docs/sources.json').read_text(encoding='utf-8'))
    sources = source_doc['sources']
    snapshot_path = ROOT / 'data/snapshots/phase-8-reference-2026-11-19.json'
    snapshot = json.loads(snapshot_path.read_text(encoding='utf-8'))
    snapshot_date = date.fromisoformat(snapshot['retrieved_at_europe_paris'][:10])
    if len(PAGES) != 10:
        errors.append(f'10 pages attendues, obtenu {len(PAGES)}')
    if len(TIPS) != 61:
        errors.append(f'61 astuces attendues, obtenu {len(TIPS)}')
    if snapshot_date <= date.fromisoformat(REVIEW):
        errors.append('Le snapshot qui porte une date future doit rester explicitement quarantiné; revalider sa provenance.')
    status = source_doc.get('revalidation_phase_8', {}).get('snapshot_status', '')
    if not status.startswith('QUARANTAINE'):
        errors.append('Le snapshot futur n’est pas marqué QUARANTAINE dans docs/sources.json.')
    if any(key.startswith('tdev-items-') for page in PAGES for key in page['sources']):
        errors.append('Une source items Tarkov.dev quarantinée est encore citée sur une page.')
    expected_images = {
        'skills-field-manual.jpg','skills-training-range.jpg','economy-loot.jpg','economy-ledger.jpg','flea-market.jpg',
        'money-run.jpg','strategy-brief.jpg','advanced-tactics.jpg','pvp-loadout.jpg','pve-prestige.jpg'
    }
    actual_images = {p.name for p in (ROOT / 'images/phase8').glob('*.jpg')}
    if actual_images != expected_images:
        errors.append(f'Lot d’images PHASE_8 incorrect: {sorted(actual_images ^ expected_images)}')
    for page in PAGES:
        hero = ROOT / page['hero']
        if not hero.is_file(): errors.append('Hero JPG absent: ' + page['hero'])
        if hero.suffix.lower() != '.jpg': errors.append('Hero non JPG: ' + page['hero'])
        for key in page['sources']:
            if key not in sources: errors.append(f'Source {key} absente pour {page["id"]}')
    if len({(x['file'], x['route']) for x in PAGES}) != 10:
        errors.append('Fichiers/routes dupliqués.')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PHASE_8 source OK · {len(PAGES)} routes · {len(TIPS)} astuces · snapshot 19/11 quarantiné')

if __name__=='__main__':
    validate_phase8()
