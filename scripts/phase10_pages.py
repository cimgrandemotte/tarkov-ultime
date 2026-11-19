#!/usr/bin/env python3
"""PHASE_10 — chronologie sourcée, répertoire d’outils et glossaire bilingue."""
from datetime import date
from html import escape
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urljoin

from phase9_pages import _nav as shared_nav
from site_urls import seo_base_is_public, canonical_link, open_graph_url_meta

ROOT = Path(__file__).resolve().parents[1]
REVIEW = '2026-11-18'
REVIEW_DATE = '18 novembre 2026'

PAGES = [
    {'id':'patches','file':'pages/patch-notes.html','route':'pages/patch-notes.html','title':'Notes de patch & chronologie',
     'label':'Notes de patch','code':'P–01','lead':'Une chronologie datée des notes officielles, correctifs et annonces — sans confondre le numéro publié, le hotfix et la version réellement installée.',
     'hero':'images/phase10/patch-archive.jpg','alt':'Carnet de terrain et feuilles de transmission vierges sur une table d’atelier sombre, éclairée par une lampe ambrée.',
     'quick':[('patch-timeline','Chronologie','Parcourir'),('patch-roadmap','Annonces à venir','Distinguer'),('patch-prep','Préparer l’upgrade','Agir'),('patch-method','Méthode & limites','Vérifier')],
     'sources':['bsg-news-index','steam-news','steam-rss','steam','bsg-release-100','bsg-patch-1002','bsg-patch-1005','bsg-patch-1010','bsg-patch-1020','bsg-patch-1025','bsg-patch-1040','bsg-patch-1045','bsg-patch-1049','patch105','patch106','bsg-patch-110','bsg-patch-115','bsg-patch-1151','patch120','bsg-patch-120-official-p8','patch130','bsg-patch-130-official-p8','bsg-expansion-hub-403','balance-nov','hotfix-13nov','bsg-technical-diary-135','wiki-changelog','patched']},
    {'id':'resources','file':'pages/resources/index.html','route':'pages/resources/','title':'Ressources & outils',
     'label':'Ressources','code':'R–01','lead':'Choisir un outil selon le besoin et la fraîcheur de ses données, en séparant les annonces BSG des cartes, bases et conseils communautaires.',
     'hero':'images/phase10/resources-briefing.jpg','alt':'Carte topographique fictive, carnet, boussole et radio rangés sur une table de briefing, sans texte lisible.',
     'quick':[('resource-directory','Répertoire','Filtrer'),('resource-method','Confiance & licences','Comparer'),('resource-glossary','Glossaire bilingue','Consulter')],
     'sources':['bsg-news-index','steam-news','steam-rss','bsg-social','bsg-youtube','bsg-game-rules','tdev','tdev-status','tdev-api-doc-phase8','mapgenie','market','tracker','tarkovtracker-org','tarkovtracker-guide','tarkovtracker-github','tarkovtracker-pr1496','wiki','wiki-portal-license','tarkovhead','kappaguide','reddit-eft','reddit-tracker-apr2026','reddit-map-alternatives-may2026','forum','forge','yt-dev','yt-community-hotfix-nov14']},
    {'id':'glossary','file':'pages/resources/glossary.html','route':'pages/resources/glossary.html','title':'Glossaire EFT — anglais / français',
     'label':'Glossaire EFT','code':'R–02','lead':'Plus de 200 termes anglais et français pour décoder les menus, les guides et l’argot communautaire — avec une recherche sans accents.',
     'hero':'images/phase10/glossary-notebook.jpg','alt':'Carnet de poche ouvert, crayon et radio de terrain sur une surface métallique dans une lumière cinématographique.',
     'quick':[('glossary-index','Index A–Z','Rechercher'),('glossary-groups','Par thèmes','Parcourir'),('sources','Sources & vocabulaire','Recouper')],
     'sources':['wiki','wiki-portal-license','tdev','steam-news','reddit-eft','tarkovtracker-org','bsg-game-rules']},
]

TIMELINE = [
 {'date':'2025-11-15','date_label':'15 novembre 2025 · sortie','version':'1.0.0.0','kind':'release','status':'Sortie officielle','scope':'EFT · version 1.0','summary':'Date de sortie annoncée par BSG en août 2025 et confirmée par la fiche Steam. Le communiqué du 22 août est une annonce préalable, pas une note publiée le jour du lancement.','sources':['bsg-release-100','steam']},
 {'date':'2025-12-01','date_label':'1 décembre 2025','version':'1.0.0.2','kind':'patch','status':'Notes officielles','scope':'EFT · patch','summary':'Premier correctif numéroté retenu après la sortie 1.0. La chronologie s’appuie sur l’index et le lien BSG; ouvrir les notes originales pour le détail complet plutôt que reprendre des spéculations de joueurs.','sources':['bsg-patch-1002','bsg-news-index']},
 {'date':'2025-12-11','date_label':'11 décembre 2025','version':'1.0.0.5','kind':'patch','status':'Notes officielles','scope':'EFT · patch','summary':'Bascule de saison vers l’hiver et série de correctifs post-lancement. La liste exhaustive et les cas corrigés sont dans l’annonce Steam BSG.','sources':['bsg-patch-1005']},
 {'date':'2025-12-23','date_label':'23 décembre · notes / 24 décembre · installation annoncée','version':'1.0.1.0','kind':'patch','status':'Notes officielles · événement daté','scope':'EFT · PvP / PvE selon l’événement','summary':'Améliorations de retour sur le matchmaking, arrivée du M110 et événement Kolotun. BSG distingue la date de la note de celle de l’annonce d’installation; l’événement est décrit dans les notes originales.','sources':['bsg-patch-1010','bsg-news-index']},
 {'date':'2026-02-10','date_label':'10 février 2026','version':'1.0.2.0','kind':'patch','status':'Notes officielles','scope':'EFT · patch','summary':'Rich Presence Steam, ajustements de lancement des serveurs de raid et changements de contenu/équilibrage. Une note de patch n’implique pas que chaque correction se comporte de façon identique sur chaque machine.','sources':['bsg-patch-1020','bsg-news-index']},
 {'date':'2026-03-05','date_label':'5 mars 2026','version':'1.0.2.5','kind':'patch','status':'Notes officielles','scope':'EFT · patch','summary':'Nouvelles optimisations des processus de raid et du retour post-raid, ainsi que des ajustements d’armes et corrections. Consulter la note BSG pour les détails par mode.','sources':['bsg-patch-1025','bsg-news-index']},
 {'date':'2026-03-26','date_label':'26 mars · note / 27 mars · installation annoncée','version':'1.0.4.0','kind':'patch','status':'Notes et maintenance datées séparément','scope':'EFT · patch','summary':'L’index BSG date l’article du 26 mars; le compte officiel a annoncé l’installation le 27 mars. La ligne conserve ces deux dates sans résumer des détails qui doivent être vérifiés dans la note originale.','sources':['bsg-patch-1040','bsg-news-index']},
 {'date':'2026-04-19','date_label':'19 avril · note / 20 avril · installation annoncée','version':'1.0.4.5','kind':'patch','status':'Notes et maintenance datées séparément','scope':'EFT · patch','summary':'Optimisations des écrans hors raid et du retour de raid, changements de culling sur certains lieux, protection de progression en PvE local et deuxième étape de rééquilibrage de pièces d’armes. Les gains de performance dépendent du PC et des réglages.','sources':['bsg-patch-1045','bsg-news-index']},
 {'date':'2026-05-19','date_label':'19 mai 2026 · date d’index','version':'1.0.4.9','kind':'patch','status':'Note indexée · détails non récupérés','scope':'EFT · patch','summary':'L’index BSG liste la note 1.0.4.9 au 19 mai; l’installation a été annoncée terminée ce jour-là. Les détails de la note n’ont pas été récupérés dans cette revue : ne pas en déduire de bonus ni d’impact gameplay.','sources':['bsg-patch-1049','bsg-patch-1049-install','bsg-news-index']},
 {'date':'2026-05-25','date_label':'25 mai 2026','version':'1.0.5.0','kind':'patch','status':'Notes officielles · nouveau lieu','scope':'EFT · tous modes selon la note','summary':'Ajout d’Icebreaker et du chapitre Boreas : lieu séparé pour 1 à 3 joueurs contre l’IA, en solo ou en groupe préformé, sans matchmaking aléatoire. La note contient aussi des ajustements de tâches et des correctifs.','sources':['patch105','bsg-news-index']},
 {'date':'2026-07-03','date_label':'3 juillet 2026','version':'1.0.6.0','kind':'patch','status':'Notes officielles','scope':'EFT · patch','summary':'Préparation technique de l’Expansion Hub et recherche de tâches ajoutée à l’interface. BSG précise que le Hub n’est pas disponible immédiatement après l’installation de cette version.','sources':['patch106','bsg-news-index']},
 {'date':'2026-07-08','date_label':'8 juillet 2026','version':'Annonce séparée · Expansion Hub','kind':'platform','status':'Annonce officielle séparée du patch','scope':'EFT · service / boutique en jeu','summary':'Annonce BSG distincte qui décrit l’arrivée de l’Expansion Hub et de TarCoin. Ne pas confondre la préparation du patch 1.0.6.0 avec la mise en service annoncée ensuite.','sources':['bsg-expansion-hub-403']},
 {'date':'2026-08-03','date_label':'3 août 2026','version':'1.1.0.0','kind':'patch','status':'Notes officielles · saison','scope':'EFT · Seasonal et progression','summary':'Ajout du personnage Seasonal et lancement de Season 1, Kord Breach, avec des règles distinctes des personnages PvP/PvE permanents. Les resets et récompenses sont ceux de la note de saison.','sources':['bsg-patch-110','bsg-news-index']},
 {'date':'2026-09-07','date_label':'7 septembre · note / 8 septembre · index et installation','version':'1.1.5.0','kind':'patch','status':'Notes et maintenance datées séparément','scope':'EFT · Lighthouse / Icebreaker','summary':'Refonte de Lighthouse et accès à Icebreaker depuis Shoreline ou Lighthouse au moyen du kit Sudak-tudak à usage unique. La page BSG est datée du 7 septembre; l’index et l’annonce d’installation situent le déploiement au 8.','sources':['bsg-patch-115','bsg-lighthouse-x','bsg-news-index']},
 {'date':'2026-09-15','date_label':'15 septembre 2026','version':'1.1.5.1','kind':'patch','status':'Notes officielles','scope':'EFT · personnages Seasonal','summary':'Annonce Steam BSG des Leagues pour personnages saisonniers. Ne pas appliquer automatiquement ce système aux personnages permanents ou au PvE.','sources':['bsg-patch-1151','bsg-news-index']},
 {'date':'2026-10-06','date_label':'6 octobre 2026','version':'1.2.0.0','kind':'patch','status':'Notes officielles','scope':'EFT · cartes, tâches et IA','summary':'BSG signale des extractions PMC/Scav ajustées, des changements de loot et de clés à Customs, de nouveaux emplacements de loot et corrections de géométrie à Interchange, et un audio environnemental revu à Shoreline. La note ne nomme pas toutes les extractions concernées.','sources':['patch120','bsg-patch-120-official-p8','bsg-news-index']},
 {'date':'2026-10-29','date_label':'29 octobre 2026','version':'1.3.0.0','kind':'patch','status':'Dernière note numérotée listée au relevé','scope':'EFT · événements, progression et correctifs','summary':'Patch officiel associé à l’événement Halloween et à des changements de progression/compétences. Cette mention situe la dernière note numérotée vue dans l’index BSG au 18 novembre; elle ne certifie pas le build installé.','sources':['patch130','bsg-patch-130-official-p8','bsg-news-index']},
 {'date':'2026-11-12','date_label':'12 novembre 2026','version':'Aucun numéro publié dans le message','kind':'balance','status':'Publication officielle sans numéro','scope':'EFT · ajustements de modes et d’ennemis','summary':'BSG annonce des ajustements d’équilibrage, dont des changements de tâches saisonnières, Black Division et Wedge. Les valeurs non indiquées par BSG ne sont ni déduites ni inventées.','sources':['balance-nov']},
 {'date':'2026-11-13','date_label':'13 novembre 2026','version':'Mise à jour technique · numéro non indiqué','kind':'technical','status':'Installation confirmée par BSG','scope':'EFT · message du canal Telegram officiel','summary':'Le canal Telegram EN de BSG confirme une mise à jour technique et invite à la télécharger via le Launcher. Le message consulté ne donne pas de numéro; un numéro observé sur un wiki communautaire n’est pas attribué à BSG.','sources':['hotfix-13nov','wiki-changelog']},
 {'date':'2026-11-18','date_label':'18 novembre 2026 · journal développeur','version':'1.3.5.0 · annoncée, installation non confirmée','kind':'roadmap','status':'Seconde moitié de novembre · aucun jour/installation annoncés','scope':'EFT · annonce officielle, pas une note de patch','summary':'Vérification du 18 novembre 2026 : le journal développeur BSG daté du 18/11 prévoit 1.3.5.0 pour la seconde moitié de novembre, sans jour précis ni annonce d’installation. L’index officiel des notes récupéré directement conserve 1.3.0.0 (29 octobre) comme dernière note numérotée. BSG annonce Unity 6, la connexion au serveur en parallèle du chargement, une meilleure libération de RAM après raid, une stabilité serveur accrue, une meilleure fluidité et une reconnexion rapide. DirectX 12, DLSS Frame Generation x2/x4 et NVIDIA Reflex sont futurs; la végétation est reportée et FSR 4 visé avant fin 2026.','sources':['bsg-technical-diary-135','bsg-news-index']},
]

RESOURCES = [
 {'id':'bsg-index','title':'Notes de patch BSG','key':'bsg-news-index','purpose':'updates','trust':'official','trust_label':'Officiel · source primaire','description':'Index des notes numérotées et annonces EFT. C’est le meilleur point de départ pour dater les patchs; la page ne prouve pas le build reçu par votre client.'},
 {'id':'bsg-steam','title':'Battlestate Games sur Steam','key':'steam-news','purpose':'updates','trust':'official','trust_label':'Officiel · source primaire','description':'Flux officiel des annonces EFT. Distinguer les annonces du jeu principal de celles d’Arena et lire les dates sur l’article original.'},
 {'id':'bsg-rss','title':'Flux RSS officiel Steam','key':'steam-rss','purpose':'updates','trust':'official','trust_label':'Officiel · source primaire','description':'Surveiller les titres, dates et liens de publications BSG. Les correctifs annoncés uniquement sur les réseaux peuvent nécessiter une vérification complémentaire.'},
 {'id':'bsg-social','title':'Canaux sociaux BSG','key':'bsg-social','purpose':'updates','trust':'official','trust_label':'Officiel · source primaire','description':'X et Telegram servent parfois à confirmer un déploiement ou annoncer un ajustement sans numéro de patch. L’absence de numéro doit rester explicite.'},
 {'id':'bsg-video','title':'Chaîne YouTube Battlestate Games','key':'bsg-youtube','purpose':'video','trust':'official','trust_label':'Officiel · média BSG','description':'Journaux de développeurs et vidéos officielles. Une feuille de route en vidéo reste une annonce : vérifier ensuite la note de patch pour confirmer ce qui a été livré.'},
 {'id':'tarkovdev','title':'Tarkov.dev — base communautaire et endpoints JSON','key':'tdev','purpose':'data','trust':'community-data','trust_label':'Communautaire · données agrégées','description':'Items, tâches, traders, planque et exports par mode. Privilégier le catalogue JSON public; les caches n’attestent ni l’état live, ni la disponibilité de votre profil.'},
 {'id':'tracker','title':'TarkovTracker.org — suivi de progression','key':'tarkovtracker-org','purpose':'progress','trust':'community-tool','trust_label':'Communautaire · outil tiers','description':'Suivi des tâches, objets requis et Hideout. Le statut du projet indique .org comme instance maintenue et .io comme ancienne instance; vérifier le mode et l’import utilisé.'},
 {'id':'mapgenie','title':'MapGenie — cartes interactives','key':'mapgenie','purpose':'maps','trust':'community-tool','trust_label':'Communautaire · carte interactive','description':'Filtres et marqueurs de carte pour préparer une route. Les couches, contenus payants et marqueurs évoluent; ne présumez pas qu’une carte est exhaustive ou à jour.'},
 {'id':'wiki','title':'Wiki communautaire Fandom','key':'wiki','purpose':'maps','trust':'community-data','trust_label':'Communautaire · wiki bénévole','description':'Référence pour noms, objets et pages de carte. Malgré son titre « Official », il est tenu par la communauté; vérifier la date de l’article et la licence avant de réutiliser quoi que ce soit.'},
 {'id':'market','title':'Tarkov Market — prix et outils','key':'market','purpose':'economy','trust':'community-tool','trust_label':'Communautaire · estimation de marché','description':'Outil tiers pour consulter des offres et estimations. Les cours changent avec le mode, l’heure et les données mises en cache; aucun tarif du guide n’est garanti.'},
 {'id':'tarkovhead','title':'TarkovHead — actualités et base','key':'tarkovhead','purpose':'community','trust':'community-data','trust_label':'Communautaire · agrégateur','description':'Utile pour découvrir une annonce ou comparer des résumés. Remonter systématiquement à BSG pour une règle ou un déploiement.'},
 {'id':'kappaguide','title':'KappaGuide — progression et cartes','key':'kappaguide','purpose':'progress','trust':'community-data','trust_label':'Communautaire · guide secondaire','description':'Point de départ pour explorer les sujets de progression. Les conditions et compteurs peuvent diverger; vérifier dans le jeu et les notes officielles.'},
 {'id':'reddit','title':'Reddit — r/EscapefromTarkov','key':'reddit-eft','purpose':'community','trust':'community-discussion','trust_label':'Communauté · témoignages','description':'Discussions, retours et découverte d’outils. Une observation de joueur est datée et subjective; elle ne prouve pas une règle globale.'},
 {'id':'forum','title':'Forums EFT','key':'forum','purpose':'community','trust':'community-discussion','trust_label':'Communauté · discussions sur forum BSG','description':'Le forum est hébergé sur le domaine EFT, mais les contributions restent des messages communautaires. Utiliser les fils pour repérer une question, pas comme note officielle.'},
 {'id':'yt-community','title':'Analyse YouTube communautaire du 14 novembre','key':'yt-community-hotfix-nov14','purpose':'video','trust':'community-discussion','trust_label':'Communauté · analyse vidéo datée','description':'Exemple de débrief d’un équilibrage BSG récent. Pratique pour entendre une interprétation, mais la publication BSG citée reste la source des faits.'},
 {'id':'forge','title':'The Forge — mods SP-Tushonka','key':'forge','purpose':'modding','trust':'community-tool','trust_label':'Communautaire · catalogue de mods','description':'Catalogue de mods pour la branche communautaire SP-Tushonka. Filtrer par version, lire les dépendances et vérifier avec les mainteneurs; présence au catalogue ne garantit pas compatibilité ou approbation BSG.'},
 {'id':'rules','title':'Règles officielles et propriété intellectuelle BSG','key':'bsg-game-rules','purpose':'community','trust':'official','trust_label':'Officiel · règles et licences','description':'Référence à consulter pour les règles d’utilisation et les droits sur les contenus. La licence MIT du code d’un outil tiers ne concède pas les images ou éléments du jeu.'},
]

PURPOSE_LABELS={'updates':'Actualités','data':'Données','maps':'Cartes','economy':'Économie','progress':'Progression','community':'Communautés','video':'Vidéos','modding':'Modding'}
TRUST_LABELS={'official':'Officiel','community-data':'Données communautaires','community-tool':'Outil communautaire','community-discussion':'Discussion communautaire'}


def e(value):
    return escape(str(value), quote=True)


def _root(page):
    return '../' if page['id']=='patches' else '../../'


def _section(anchor, n, eyebrow, title, intro, content):
    return (f'<section class="guide-section phase9-section phase10-section" id="{e(anchor)}" tabindex="-1" aria-labelledby="{e(anchor)}-title">'
            f'<div class="phase9-section__heading"><p class="guide-kicker"><span>{e(n)}</span> {e(eyebrow)}</p>'
            f'<h2 id="{e(anchor)}-title">{e(title)}</h2><p>{e(intro)}</p></div>{content}</section>')


def _fig(src, alt, caption, root):
    return (f'<figure class="phase9-figure phase10-figure"><img src="{e(root+src)}" width="1376" height="768" loading="lazy" decoding="async" alt="{e(alt)}">'
            f'<figcaption>{e(caption)}</figcaption></figure>')


def _source_note(source):
    return (source.get('usage_phase_10') or source.get('usage') or
            source.get('usage_phase_8') or source.get('usage_phase_9') or
            'Consulter la source d’origine et vérifier sa date, son mode et son statut avant réutilisation.')


def _source_list(keys, sources):
    rows=[]
    for key in keys:
        item=sources.get(key)
        if not item: raise ValueError(f'Source PHASE_10 absente de docs/sources.json : {key}')
        title=item.get('titre') or key
        url=item.get('url') or ''
        kind=item.get('type') or 'source'
        note=_source_note(item)
        when=item.get('date_releve_phase_10') or item.get('revalidation_phase_10') or 'Fiche du registre; revalider le lien et l’état du service à la lecture.'
        rows.append(f'<li><span class="phase9-source__type">{e(kind.replace("_"," "))}</span><div><a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(title)} <span aria-hidden="true">↗</span></a><p>{e(note)}</p><small>{e(when)}</small></div></li>')
    return ''.join(rows)


def _source_anchor(key, sources):
    item=sources[key]
    return f'<a class="phase10-source-link" href="{e(item.get("url",""))}" target="_blank" rel="noopener noreferrer">{e(item.get("titre",key))} <span aria-hidden="true">↗</span></a>'


def _timeline_cards(sources):
    out=[]
    for row in TIMELINE:
        year=row['date'][:4]
        links=' '.join(_source_anchor(k,sources) for k in row['sources'])
        out.append(f'''<article class="phase10-timeline-card" data-p10-timeline-card data-kind="{e(row['kind'])}" data-year="{year}">
<div class="phase10-timeline-card__date"><time datetime="{e(row['date'])}">{e(row['date_label'])}</time><span class="phase10-timeline-card__version">{e(row['version'])}</span></div>
<div class="phase10-timeline-card__body"><div class="phase10-timeline-card__meta"><span class="phase10-kind">{e(row['status'])}</span><span>{e(row['scope'])}</span></div><p>{e(row['summary'])}</p><div class="phase10-timeline-card__sources">{links}</div></div></article>''')
    return ''.join(out)


def _patch_content(root, sources):
    current='''<div class="phase9-callout phase9-callout--warning"><strong>Vérification du 18 novembre 2026 — annonces, pas lecture du client.</strong>
<p>L’index officiel des notes BSG, récupéré directement, affiche 1.3.0.0 (29 octobre) comme dernière note numérotée. Le journal développeur BSG daté du 18/11 prévoit 1.3.5.0 pour la seconde moitié de novembre, sans jour précis ni annonce d’installation : c’est une fenêtre annoncée, pas une confirmation que le patch est sorti ou installé. BSG avait aussi confirmé une mise à jour technique le 13 novembre sans numéro. Vérifier l’annonce de maintenance, le Launcher et l’écran de version avant d’appliquer un conseil.</p></div>'''
    controls='''<div class="phase10-filter-bar" data-p10-timeline-controls hidden><label class="field">Période<select class="field__input" data-p10-timeline-year><option value="all">Toutes les années</option><option value="2025">2025</option><option value="2026">2026</option></select></label>
<label class="field">Type de publication<select class="field__input" data-p10-timeline-kind><option value="all">Tous les types</option><option value="release">Sortie</option><option value="patch">Patch numéroté</option><option value="platform">Service / plateforme</option><option value="balance">Équilibrage sans numéro</option><option value="technical">Correctif technique</option><option value="roadmap">Annonce / feuille de route</option></select></label>
<p class="phase10-result-count" data-p10-timeline-count role="status" aria-live="polite">Résultats : toutes les entrées sont affichées.</p></div>'''
    timeline=controls+'<div class="phase10-timeline" aria-label="Chronologie des notes et annonces">'+_timeline_cards(sources)+'</div><noscript><p class="phase9-note">Sans JavaScript, la chronologie complète reste visible; seuls les filtres sont désactivés.</p></noscript>'
    s1=_section('patch-timeline','01','Jalons officiels et publications datées','Chronologie 1.0 → annonces 1.3.5.0','Sélection des jalons et annonces BSG vérifiés jusqu’au 18 novembre 2026. Les notes, journaux développeur, dates de publication et installations sont distingués; le statut du client n’est pas inféré.',current+timeline+_fig('images/phase10/patch-timeline.jpg','Radio et fiches vierges composent une frise de suivi sur une table de briefing.','Frise éditoriale originale; les dates et numéros sont ceux des sources liées.',root))
    roadmap='''<div class="phase9-card-grid phase9-card-grid--three"><article class="phase9-card"><p class="phase9-card__eyebrow">Dernière note numérotée affichée · 29 octobre</p><h3>1.3.0.0</h3><p>L’index BSG récupéré directement le 18 novembre la présente toujours comme la plus récente note de patch numérotée. Cela ne confirme pas à lui seul le build installé sur chaque client.</p></article>
<article class="phase9-card phase9-card--warning"><p class="phase9-card__eyebrow">Message officiel · 13 novembre</p><h3>Mise à jour technique sans numéro</h3><p>Le canal BSG confirme l’installation, mais le message cité ne donne aucun identifiant de version. Les numéros publiés par un wiki restent communautaires.</p></article>
<article class="phase9-card"><p class="phase9-card__eyebrow">Journal développeur · 18 novembre</p><h3>1.3.5.0 annoncée, date et installation non confirmées</h3><p>BSG la prévoit pour la seconde moitié de novembre, sans jour précis. Unity 6, la connexion au serveur en parallèle du chargement, la libération de RAM après raid, la stabilité serveur, une meilleure fluidité et une reconnexion rapide sont annoncés. DirectX 12, DLSS Frame Generation x2/x4 et NVIDIA Reflex sont des travaux futurs; la végétation est reportée et FSR 4 visé avant fin 2026. À la vérification du 18/11, aucune annonce BSG d’installation n’a été trouvée.</p></article></div>
<div class="phase9-callout"><strong>Annonce ≠ déploiement ≠ build installé.</strong><p>Une fenêtre prévue, un journal développeur, une maintenance sans numéro et un numéro de build communautaire sont quatre éléments différents. Les étiquettes de cette page les séparent explicitement.</p></div>'''
    s2=_section('patch-roadmap','02','Annonces et versions','Ce qui est prévu, installé ou seulement rapporté','La roadmap sert à préparer la veille, pas à décrire des fonctionnalités déjà présentes dans le jeu.',roadmap)
    prep='''<div class="phase9-callout phase9-callout--warning"><strong>Point de départ au 18 novembre 2026</strong><p>Le journal BSG donne seulement une fenêtre — seconde moitié de novembre. Il ne publie ni jour/heure de maintenance, ni taille de téléchargement, ni prérequis système ou procédure spéciale de préparation. Les étapes ci-dessous sont des précautions pratiques du guide, pas des exigences BSG.</p></div>
<div class="phase9-card-grid phase9-card-grid--three"><article class="phase9-card"><p class="phase9-card__eyebrow">Avant l’annonce de maintenance</p><h3>Préparez vos repères</h3><p>Surveillez les notes BSG et le Launcher officiel. Notez ou capturez vos réglages graphiques et raccourcis actuels pour pouvoir les comparer après la mise à jour. Gardez l’espace libre requis par le Launcher; aucun chiffre de stockage n’est fourni dans le journal.</p></article>
<article class="phase9-card"><p class="phase9-card__eyebrow">Pendant l’installation</p><h3>Utilisez la source officielle</h3><p>Attendez l’annonce de maintenance et installez uniquement avec le Launcher officiel. Ne prenez pas un numéro de build de wiki ou de vidéo pour confirmation BSG; aucune réinstallation, purge de cache ou modification de pilote n’est donnée comme prérequis.</p></article>
<article class="phase9-card"><p class="phase9-card__eyebrow">Après la mise à jour</p><h3>Vérifiez avant de conclure</h3><p>Confirmez la version affichée par le Launcher/client et lisez la note de patch BSG. Comparez la fluidité avec vos réglages habituels et changez une variable à la fois si vous faites des essais; les gains annoncés ne sont pas une garantie identique sur chaque PC.</p></article></div>
<div class="phase9-callout"><strong>Ne préparez pas une fonction qui n’est pas annoncée comme livrée.</strong><p>DirectX 12, DLSS Frame Generation x2/x4 et NVIDIA Reflex relèvent des travaux futurs du journal; la nouvelle végétation est reportée. Ne modifiez pas vos réglages pour les considérer comme disponibles dans 1.3.5.0.</p></div>'''
    s3=_section('patch-prep','03','Mise à niveau · conseils pratiques','Upgrade — Prepare 1.3.5.0 avant la mise à jour','Une checklist prudente, distincte des consignes BSG : aucun jour de sortie ni installation de 1.3.5.0 n’est confirmé dans les sources vérifiées au 18 novembre 2026.',prep)
    method='''<div class="phase9-card-grid phase9-card-grid--two"><article class="phase9-card"><h3>Source primaire</h3><p>Pour les dates et changements annoncés, ouvrir les notes BSG/Steam ou le message officiel associé. Une note prouve ce qui a été publié, pas nécessairement le résultat sur chaque machine.</p></article>
<article class="phase9-card"><h3>Source communautaire</h3><p>Le wiki EFT rapporte des builds 1.3.0.1/1.3.0.2. Le message BSG du 13 novembre ne nomme pas le build. Ces numéros ne sont donc pas attribués à BSG ici.</p></article></div>
<p class="phase9-note">Certains résultats donnent la date de l’article un jour avant l’annonce de maintenance. La chronologie conserve cette différence; elle n’infère pas l’heure du déploiement.</p>'''
    s4=_section('patch-method','04','Méthode','Comment lire ces dates','Les filtres réduisent l’affichage sans supprimer les lignes de la page lorsque JavaScript est désactivé.',method)
    return current+s1+s2+s3+s4


def _resource_cards(sources):
    cards=[]
    for row in RESOURCES:
        source=sources[row['key']]
        url=source.get('url','')
        cards.append(f'''<article class="phase10-resource-card" data-p10-resource-card data-purpose="{e(row['purpose'])}" data-trust="{e(row['trust'])}" data-search="{e(' '.join([row['title'],row['description'],row['trust_label'],PURPOSE_LABELS[row['purpose']]]))}">
<div class="phase10-resource-card__meta"><span class="phase10-purpose">{e(PURPOSE_LABELS[row['purpose']])}</span><span class="phase10-trust" data-trust="{e(row['trust'])}">{e(row['trust_label'])}</span></div>
<h3>{e(row['title'])}</h3><p>{e(row['description'])}</p><a class="phase10-resource-card__link" href="{e(url)}" target="_blank" rel="noopener noreferrer">Ouvrir la ressource <span aria-hidden="true">↗</span></a></article>''')
    return ''.join(cards)


def _resources_content(root, sources):
    intro='''<div class="phase9-callout"><strong>Règle simple : pour une mécanique actuelle, partir de BSG puis vérifier le mode et le client.</strong><p>Les outils communautaires accélèrent la recherche, mais leur cache, leur couverture et leurs marqueurs peuvent être en retard ou incomplets. Le niveau de confiance affiché décrit le type de source, pas une note de qualité absolue.</p></div>'''
    controls='''<div class="phase10-filter-bar phase10-filter-bar--resources" data-p10-resource-controls hidden>
<label class="field">Usage<select class="field__input" data-p10-resource-purpose><option value="all">Tous les usages</option><option value="updates">Actualités</option><option value="data">Données</option><option value="maps">Cartes</option><option value="economy">Économie</option><option value="progress">Progression</option><option value="community">Communautés</option><option value="video">Vidéos</option><option value="modding">Modding</option></select></label>
<label class="field">Type de source<select class="field__input" data-p10-resource-trust><option value="all">Tous les types</option><option value="official">Officiel</option><option value="community-data">Données communautaires</option><option value="community-tool">Outil communautaire</option><option value="community-discussion">Discussion communautaire</option></select></label>
<label class="field phase10-resource-search">Recherche<input class="field__input" type="search" data-p10-resource-query placeholder="Nom, usage ou réserve" autocomplete="off"></label>
<p class="phase10-result-count" data-p10-resource-count role="status" aria-live="polite">Résultats : toutes les ressources sont affichées.</p></div>'''
    directory=controls+'<div class="phase10-resource-grid">'+_resource_cards(sources)+'</div><noscript><p class="phase9-note">Sans JavaScript, toutes les fiches de ressources restent visibles; seul le filtrage est désactivé.</p></noscript>'
    s1=_section('resource-directory','01','Répertoire vérifié au relevé','Outils classés par usage et type de source','Les cartes renvoient aux sites originaux; le statut de service, la couverture et les licences peuvent évoluer.',intro+directory+_fig('images/phase10/resources-workbench.jpg','Deux mains comparent une carte papier à un ordinateur dont l’écran est flou et sans texte lisible.','Illustration éditoriale originale; aucun outil tiers ou écran de jeu n’est reproduit.',root))
    method='''<div class="phase9-card-grid phase9-card-grid--three"><article class="phase9-card"><h3>Officiel</h3><p>Notes BSG, Steam News, X, Telegram et vidéos BSG. Un post officiel sans numéro ne doit pas recevoir un numéro supposé.</p></article>
<article class="phase9-card"><h3>Données / outils communautaires</h3><p>Tarkov.dev, TarkovTracker, MapGenie et les bases de marché sont des projets tiers. Vérifier la date, le mode, la source amont et la disponibilité du service.</p></article>
<article class="phase9-card"><h3>Forums, wikis et vidéos</h3><p>Utiles pour découvrir un problème ou une piste. Une expérience, un tutoriel ou un wiki ne remplace pas le client et les notes de patch.</p></article></div>
<div class="phase9-callout phase9-callout--warning"><strong>Confidentialité et sécurité des outils compagnons</strong><p>Les lecteurs de journaux, overlays et scanners sont des logiciels tiers. Cette page ne garantit ni leur innocuité ni leur compatibilité avec les règles de BSG. Vérifier le code, les permissions et la politique de confidentialité; ne transmettre aucun mot de passe, code MFA ou identifiant de compte.</p></div>
<div class="phase9-callout"><strong>Licences et crédits</strong><p>Le wiki Fandom annonce une licence CC BY-NC-SA sauf indication contraire; le code MIT de Tarkov.dev ne concède pas les assets du jeu. Les cartes, images, textes et marques ne sont pas copiés dans ce guide. Voir les règles BSG et chaque licence avant toute réutilisation. Ce guide est un fan-site indépendant, non affilié à Battlestate Games.</p></div>'''
    s2=_section('resource-method','02','Confiance, sécurité et réutilisation','Évaluer avant de dépendre d’un outil','La date de relecture de cette fiche n’est pas une garantie de disponibilité future.',method)
    glossary=f'''<div class="phase9-link-card"><strong>Un terme vous échappe ?</strong><span>Le glossaire bilingue regroupe {len(json.loads((ROOT/'data/phase10-glossary.json').read_text(encoding='utf-8'))['terms'])} termes anglais et français et permet une recherche sans accents.</span><a href="{e(root+'pages/resources/glossary.html')}">Ouvrir le glossaire EFT ↗</a></div>'''
    s3=_section('resource-glossary','03','Repère linguistique','Glossaire EFT anglais / français','Comprendre les termes ne suffit pas à confirmer une mécanique : les définitions sensibles au patch sont volontairement qualitatives.',glossary)
    return intro+s1+s2+s3


def _slug(text):
    value=unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode('ascii').lower()
    value=re.sub(r'[^a-z0-9]+','-',value).strip('-')
    return value or 'terme'


def _letter(text):
    value=unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode('ascii')
    match=re.search(r'[A-Za-z]',value)
    return match.group(0).upper() if match else '#'


def _glossary_groups(terms):
    grouped={}
    used_ids=set()
    for term in sorted(terms,key=lambda item:(item['en'].casefold(),item['fr'].casefold())):
        letter=_letter(term['en'])
        grouped.setdefault(letter,[])
        slug=_slug(term['en'])
        term_id='term-'+slug
        if term_id in used_ids:
            raise ValueError('ID de glossaire dupliqué : '+term_id)
        used_ids.add(term_id)
        text=' '.join((term['en'],term['fr'],term['definition'],term['group']))
        grouped[letter].append(f'''<article class="phase10-term" id="{term_id}" data-p10-glossary-item data-letter="{letter}" data-group="{e(term['group'])}" data-search="{e(text)}">
<div class="phase10-term__heading"><h3>{e(term['en'])}</h3><span class="phase10-term__language">EN</span></div><p class="phase10-term__translation"><span>FR</span>{e(term['fr'])}</p><p class="phase10-term__definition">{e(term['definition'])}</p><span class="phase10-term__group">{e(term['group'])}</span></article>''')
    sections=[]
    for letter in sorted(grouped):
        sections.append(f'<section class="phase10-letter-group" id="letter-{letter}" data-p10-letter-group aria-labelledby="letter-{letter}-title"><h3 id="letter-{letter}-title" class="phase10-letter-heading">{letter}</h3><div class="phase10-term-grid">{"".join(grouped[letter])}</div></section>')
    return ''.join(sections),sorted(grouped)


def _glossary_content(root, terms, sources):
    groups,letters=_glossary_groups(terms)
    options=''.join(f'<option value="{e(group)}">{e(group)}</option>' for group in sorted({t["group"] for t in terms}))
    alphabet=''.join(f'<button type="button" class="phase10-alpha__button" data-p10-letter="{letter}" aria-pressed="false">{letter}</button>' for letter in letters)
    controls=f'''<div class="phase10-glossary-controls" data-p10-glossary-controls hidden><label class="field phase10-glossary-search">Rechercher un terme<input class="field__input" type="search" data-p10-glossary-query placeholder="Ex. extraction, desync, FIR" autocomplete="off"></label>
<label class="field">Thème<select class="field__input" data-p10-glossary-group><option value="all">Tous les thèmes</option>{options}</select></label>
<button type="button" class="button button--quiet" data-p10-glossary-reset>Effacer les filtres</button><p class="phase10-result-count" data-p10-glossary-count role="status" aria-live="polite">{len(terms)} entrées bilingues.</p></div>
<nav class="phase10-alpha" aria-label="Index alphabétique" data-p10-alpha hidden><button type="button" class="phase10-alpha__button" data-p10-letter="all" aria-pressed="true">Tout l’alphabet</button>{alphabet}</nav>'''
    intro=f'''<div class="phase9-callout"><strong>{len(terms)} entrées anglais → français.</strong><p>Le terme anglais est conservé lorsqu’il est employé dans les menus ou dans la communauté. Les équivalents français facilitent la lecture; l’argot est étiqueté comme communautaire et n’est pas présenté comme vocabulaire BSG.</p></div>'''
    s1=_section('glossary-index','01','Index bilingue','Rechercher ou filtrer par lettre','La recherche ignore les accents et cherche dans les termes anglais, français, le thème et la définition. Sans JavaScript, toutes les entrées restent consultables.',controls+'<div class="phase10-glossary-list" data-p10-glossary-list>'+groups+'</div><noscript><p class="phase9-note">JavaScript désactivé : le glossaire complet reste affiché dans l’ordre alphabétique.</p></noscript>')
    topics='''<div class="phase9-card-grid phase9-card-grid--three"><article class="phase9-card"><h3>Modes & factions</h3><p>PvP, PvE, Seasonal, PMC, Scav et projets tiers. Une même abréviation peut changer de portée selon le mode.</p></article><article class="phase9-card"><h3>Progression & économie</h3><p>Tâches, réputation, FIR, marché, planque et crafts. Les valeurs chiffrées restent dans des fiches datées.</p></article><article class="phase9-card"><h3>Argot & technique</h3><p>Les termes comme « rat », « meta » ou « desync » décrivent un usage communautaire, pas une règle officielle.</p></article></div>'''
    s2=_section('glossary-groups','02','Thèmes','Repères pour naviguer dans le vocabulaire','Les descriptions restent qualitatives lorsque les règles sont sensibles à une version ou un mode.',topics+_fig('images/phase10/glossary-radio.jpg','Radio de terrain, cartes vierges et carnet posés dans un espace de travail sombre.','Illustration éditoriale originale; aucun texte de wiki ou capture de jeu reproduit.',root))
    return intro+s1+s2


def _content(page, root, sources, terms):
    if page['id']=='patches': return _patch_content(root,sources)
    if page['id']=='resources': return _resources_content(root,sources)
    if page['id']=='glossary': return _glossary_content(root,terms,sources)
    raise ValueError('Route PHASE_10 inconnue : '+page['id'])


def _render_page(page, sources, terms, base, patch):
    root=_root(page)
    route=page['route']
    canonical=canonical_link(base,route)
    og_url=open_graph_url_meta(base,route)
    og_image=urljoin(base,page['hero'])
    schema={'@context':'https://schema.org','@type':'Article','headline':page['title'],'description':page['lead'],'inLanguage':'fr-FR',
            'dateModified':REVIEW,'isPartOf':{'@type':'WebSite','name':'Tarkov Ultimate Guide'}}
    if seo_base_is_public(base): schema['url']=urljoin(base,route)
    jsonld=json.dumps(schema,ensure_ascii=False,separators=(',',':')).replace('<',r'\u003c')
    robots='' if seo_base_is_public(base) else '<meta name="robots" content="noindex,follow">'
    nav=shared_nav(root,route)
    sidebar=''.join(f'<li><a href="{e(root+p["route"])}"'+(' aria-current="page"' if p['route']==route else '')+f'>{e(p["label"])}</a></li>' for p in PAGES)
    content=_content(page,root,sources,terms)
    sources_html=_source_list(page['sources'],sources)
    crumb='Notes & versions' if page['id']=='patches' else 'Ressources' if page['id']=='resources' else 'Ressources'
    crumb_parent='' if page['id'] in ('patches','resources') else f'<a href="{e(root+"pages/resources/")}">Ressources</a><span aria-hidden="true">/</span>'
    page_id='phase10-h1'
    patch_text=f'''<a class="badge badge--live home-header__patch phase10-patch-badge" href="{e(root+'pages/patch-notes.html')}" aria-label="Dernière note numérotée BSG au relevé : {e(patch)}; build client non vérifié">{e(patch)}</a>'''
    return f'''<!doctype html>
<html lang="fr-FR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(page['title'])} · Guide Tarkov | Tarkov Ultimate Guide</title><meta name="description" content="{e(page['lead'])}"><meta name="theme-color" content="#111411">{robots}
<link rel="preload" href="{root}fonts/inter-400-700.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="{root}fonts/type.css"><link rel="stylesheet" href="{root}css/main.css"><link rel="stylesheet" href="{root}css/components.css"><link rel="stylesheet" href="{root}css/animations.css"><link rel="stylesheet" href="{root}css/responsive.css"><link rel="stylesheet" href="{root}css/pages/home.css"><link rel="stylesheet" href="{root}css/pages/guides.css"><link rel="stylesheet" href="{root}css/pages/phase6.css"><link rel="stylesheet" href="{root}css/pages/phase7.css"><link rel="stylesheet" href="{root}css/pages/phase8.css"><link rel="stylesheet" href="{root}css/pages/phase9.css"><link rel="stylesheet" href="{root}css/pages/phase10.css">
{canonical}<meta property="og:title" content="{e(page['title'])} · Tarkov Ultimate Guide"><meta property="og:description" content="{e(page['lead'])}"><meta property="og:type" content="article">{og_url}<meta property="og:image" content="{e(og_image)}"><script type="application/ld+json">{jsonld}</script><script src="{root}js/main.js" type="module"></script><script src="{root}js/phase10.js" type="module"></script></head>
<body class="home-page guide-page phase9-page phase10-page" data-phase10-page="{e(page['id'])}" data-phase10-root="{root}" data-phase10-route="{e(route)}" data-phase10-review="{REVIEW}" data-phase10-patch="{e(patch)}">
<a class="skip-link" href="#main">Aller au contenu</a><header class="site-header home-header" data-site-header><div class="shell site-header__inner"><a class="brand" href="{root}"><span class="brand__mark" aria-hidden="true"></span><span><span class="brand__word">TARKOV</span><span class="brand__descriptor">Ultimate Guide</span></span><span class="sr-only">, accueil</span></a>{nav}
<div class="site-header__utilities">{patch_text}<button type="button" class="button button--quiet home-header__search" data-modal-open="site-search" data-site-search-trigger aria-label="Rechercher dans le guide" aria-haspopup="dialog" aria-controls="site-search" aria-keyshortcuts="Control+K Meta+K" hidden><i class="icon icon--search" aria-hidden="true"></i><span class="button__text">Rechercher</span><kbd class="search-key" data-keyhint="Ctrl K" aria-hidden="true"></kbd></button><button type="button" class="button button--icon" data-nav-toggle aria-label="Menu de navigation" aria-controls="global-nav" aria-expanded="false" hidden><i class="icon icon--menu" aria-hidden="true"></i></button></div></div></header>
<main id="main" tabindex="-1"><nav class="phase9-breadcrumb" aria-label="Fil d’Ariane"><a href="{root}">Accueil</a><span aria-hidden="true">/</span>{crumb_parent}<span aria-current="page">{e(crumb if page['id']!='glossary' else page['label'])}</span></nav>
<section class="guide-hero phase9-hero phase10-hero" id="top" tabindex="-1" aria-labelledby="{page_id}" data-motion-hero><img class="guide-hero__image" src="{e(root+page['hero'])}" width="1376" height="768" alt="{e(page['alt'])}" fetchpriority="high" decoding="async"><div class="shell guide-hero__inner"><div class="guide-hero__copy"><p class="guide-kicker"><span>{e(page['code'])}</span> PHASE_10 · {e(page['label'])}</p><h1 id="{page_id}">{e(page['title'])}</h1><p class="guide-hero__lead">{e(page['lead'])}</p><div class="guide-hero__actions"><a class="button button--primary" href="#{e(page['quick'][0][0])}">{e(page['quick'][0][2])} <span aria-hidden="true">↓</span></a><a class="button button--quiet" href="#sources">Sources datées <span aria-hidden="true">↘</span></a></div><p class="guide-hero__note">Relu le {REVIEW_DATE} · sources officielles et communautaires séparées</p></div><p class="guide-hero__locator" aria-hidden="true">Illustration éditoriale originale · JPG</p></div></section>
<div class="guide-quick phase9-quick phase10-quick" role="group" aria-label="Accès rapide au dossier"><div class="shell guide-quick__inner">{''.join(f'<a class="guide-quick__link" href="#{e(anchor)}"><span class="guide-quick__no" aria-hidden="true">{i:02d}</span><span class="guide-quick__copy"><strong>{e(title)}</strong><small>{e(label)}</small></span><span class="guide-quick__arrow" aria-hidden="true">↘</span></a>' for i,(anchor,title,label) in enumerate(page['quick'],1))}</div></div>
<div class="shell guide-layout phase9-layout phase10-layout"><aside class="guide-rail phase9-rail phase10-rail" aria-label="Navigation des dossiers PHASE_10"><p class="guide-rail__tag">PHASE_10 / 3 routes</p><h2>Explorer</h2><nav aria-label="Pages patchs et ressources"><ol>{sidebar}</ol></nav><div class="guide-rail__foot"><span>Dernière relecture</span><span>{REVIEW_DATE}</span></div></aside><article class="guide-content phase9-content phase10-content" aria-label="{e(page['title'])}">{content}
<section class="guide-section guide-sources phase9-sources phase10-sources" id="sources" tabindex="-1" aria-labelledby="phase10-sources-title"><div class="phase9-section__heading"><p class="guide-kicker"><span>REF</span> Relecture du 18 novembre</p><h2 id="phase10-sources-title">Sources, types et limites</h2><p>Les liens BSG/Steam servent à établir les notes et annonces. Les wikis, outils, forums, réseaux de joueurs et vidéos sont secondaires et ne prouvent pas à eux seuls l’état du client.</p></div><ul class="phase9-source-list">{sources_html}</ul></section>
<div class="guide-next phase9-next phase10-next"><div><p class="guide-kicker">À lire ensuite</p><h2>Notes, outils et vocabulaire</h2><p>Passer d’une chronologie officielle à un outil communautaire ou à une définition bilingue.</p></div><div class="phase9-card-grid phase9-card-grid--three">{''.join(f'<a class="phase9-link-card" href="{e(root+p["route"])}"><strong>{e(p["label"])}</strong><span>{e(p["lead"][:120])}…</span><span class="phase9-link-card__arrow" aria-hidden="true">↗</span></a>' for p in PAGES if p['id']!=page['id'])}</div></div></article></div></main>
<footer class="home-footer guide-footer"><div class="shell guide-footer__inner"><div><a class="brand" href="{root}"><span class="brand__mark" aria-hidden="true"></span><span><span class="brand__word">TARKOV</span><span class="brand__descriptor">Ultimate Guide</span></span><span class="sr-only">, accueil</span></a><p>Fan-site francophone indépendant de Battlestate Games. Escape from Tarkov et les noms associés appartiennent à leurs ayants droit. Les illustrations sont originales et non officielles.</p></div><div class="guide-footer__controls"><a href="{root}">Retour à l’accueil <span aria-hidden="true">↗</span></a><div class="home-footer__settings"><button type="button" class="button button--quiet button--xs" data-contrast-toggle aria-pressed="false" hidden>Contraste renforcé</button><button type="button" class="button button--quiet button--xs" data-motion-toggle aria-pressed="false" hidden>Réduire les animations</button></div></div></div><a class="button button--icon back-top" data-back-top href="#top" aria-label="Retour rapide en haut" hidden></a></footer>
<dialog id="site-search" class="dialog home-search" data-modal data-site-search data-search-base="{root}" data-search-source="{root}js/data/search-index.json" aria-labelledby="search-title"><header class="dialog__head"><div><p class="eyebrow">Index du guide</p><h2 class="dialog__title" id="search-title">Rechercher dans Tarkov Ultimate Guide</h2></div><button type="button" class="button button--icon" data-modal-close aria-label="Fermer la recherche"><i class="icon icon--close" aria-hidden="true"></i></button></header><div class="dialog__body"><label for="site-query" class="field">Sujet, patch ou terme<span class="field__wrap"><i class="icon icon--search" aria-hidden="true"></i><input class="field__input field__input--search" id="site-query" type="search" placeholder="Ex. 1.3.5.0, MapGenie, FIR" autocomplete="off" data-modal-initial data-search-input></span></label><p class="dialog__hint search-status" role="status" data-search-status></p><ul class="search-results" data-search-results aria-label="Résultats de recherche"></ul><p class="search-dialog__foot"><span><kbd>↑</kbd> <kbd>↓</kbd> Parcourir</span><span><kbd>Entrée</kbd> Ouvrir</span><span>Échap Fermer</span></p></div></dialog></body></html>'''


def build_phase10(base, patch, read, compact):
    validate_phase10()
    source_doc=json.loads(read('docs/sources.json'))
    sources=source_doc['sources']
    glossary_doc=json.loads(read('data/phase10-glossary.json'))
    terms=glossary_doc['terms']
    output={}
    search=[]
    for page in PAGES:
        for key in page['sources']:
            if key not in sources: raise ValueError(f'Source {key} absente pour {page["id"]}')
        output[page['file']]=_render_page(page,sources,terms,base,patch)
        keywords=[page['label'],page['id'],'Escape from Tarkov','EFT','PHASE_10']
        if page['id']=='patches': keywords += [row['version'] for row in TIMELINE]+['patch','hotfix','Unity 6','1.3.5.0','notes BSG','build client']
        elif page['id']=='resources': keywords += [row['title'] for row in RESOURCES]+['Tarkov.dev','MapGenie','TarkovTracker.org','wiki','Reddit','licence','données communautaires']
        else: keywords += [term['en'] for term in terms]+[term['fr'] for term in terms]
        search.append({'title':page['title'],'href':page['route'],'tag':'PHASE_10 · '+page['label'],'summary':page['lead'],'keywords':keywords})
    return output,search,date.fromisoformat(REVIEW)


def validate_phase10():
    errors=[]
    expected={'pages/patch-notes.html','pages/resources/index.html','pages/resources/glossary.html'}
    if len(PAGES)!=3 or {p['file'] for p in PAGES}!=expected: errors.append('Les trois routes PHASE_10 ne correspondent pas au plan.')
    plan=json.loads((ROOT/'docs/plan-editorial.json').read_text(encoding='utf-8'))
    planned={p['fichier'] for p in plan['pages'] if p.get('phase')=='PHASE_10'}
    if planned!=expected: errors.append('Le plan éditorial PHASE_10 ne correspond pas aux trois routes attendues.')
    data=json.loads((ROOT/'data/phase10-glossary.json').read_text(encoding='utf-8'))
    terms=data.get('terms',[])
    if len(terms)<200: errors.append(f'Le glossaire doit contenir au moins 200 entrées, obtenu {len(terms)}.')
    if len({row['en'].casefold() for row in terms})!=len(terms): errors.append('Un terme anglais est dupliqué dans le glossaire.')
    groups={row.get('group') for row in terms}
    if len(groups)!=6: errors.append(f'Le glossaire doit conserver six groupes, obtenu {len(groups)}.')
    malformed=[i for i,row in enumerate(terms,1) if not all(str(row.get(field,'')).strip() for field in ('en','fr','group','definition'))]
    if malformed: errors.append('Entrées de glossaire incomplètes : '+', '.join(map(str,malformed[:12])))
    source_doc=json.loads((ROOT/'docs/sources.json').read_text(encoding='utf-8'))
    all_source_keys={key for page in PAGES for key in page['sources']}
    all_source_keys.update(key for row in TIMELINE for key in row['sources'])
    missing=sorted(key for key in all_source_keys if key not in source_doc['sources'])
    if missing: errors.append('Sources absentes : '+', '.join(missing))
    bad_urls=sorted(key for key in all_source_keys if key in source_doc['sources'] and not str(source_doc['sources'][key].get('url','')).startswith('https://'))
    if bad_urls: errors.append('Sources sans URL HTTPS : '+', '.join(bad_urls))
    for page in PAGES:
        image=ROOT/page['hero']
        if not image.is_file() or image.suffix.lower()!='.jpg' or not image.read_bytes().startswith(b'\xff\xd8'):
            errors.append('Illustration JPG absente ou invalide : '+page['hero'])
    expected_images={'patch-archive.jpg','patch-timeline.jpg','resources-briefing.jpg','resources-workbench.jpg','glossary-notebook.jpg','glossary-radio.jpg'}
    actual={p.name for p in (ROOT/'images/phase10').glob('*.jpg')}
    if actual!=expected_images: errors.append('Lot d’images PHASE_10 incorrect : '+str(sorted(actual ^ expected_images)))
    if len({row['version'] for row in TIMELINE})!=len(TIMELINE): errors.append('Version/titre dupliqué dans la chronologie.')
    if errors: raise SystemExit('\n'.join(errors))
    print(f'PHASE_10 source OK · {len(PAGES)} routes · {len(terms)} entrées bilingues · 6 JPG · relecture {REVIEW_DATE}')

if __name__=='__main__':
    validate_phase10()
