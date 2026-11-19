#!/usr/bin/env python3
"""Collecte datée et construction des 16 routes PHASE_7 (traders, quêtes, Hideout)."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
from html import escape
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import argparse
import json
import sys

from site_urls import canonical_link, open_graph_url_meta, seo_base_is_public

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://json.tarkov.dev/'
DATE = '2026-11-18'  # date de référence locale; collectedAtUtc conserve l'heure réelle de collecte.
MODES = {'regular': 'PvP permanent', 'pve': 'PvE Zone', 'pvp-season': 'PvP Seasonal'}
ENDPOINTS = ('tasks', 'tasks_fr', 'tasks_en', 'traders', 'traders_fr', 'traders_en',
             'hideout', 'hideout_fr', 'hideout_en', 'crafts', 'barters')
USER_AGENT = 'Tarkov-Ultimate-Guide/0.1 (public game-data research)'
MISSING_ISSUE_IDS = [
    '625d700cc48e6c62a440fab5', '6391d912f8e5dd32bf4e3ab2',
    '6391d9144b15ca31f76bc323', '626148334149f1149b5b12ca',
    '62614836f7308432be1d44cc', '6261483ac48e6c62a440fab7',
    '6261483dc4874104f230c0cd', '626148251ed3bb5bcc5bd9ed',
    '6261482fa4eb80027c4f2e11',
]

TRADER_PROFILES = [
    {'slug':'prapor','id':'54cb50c76803fa8b248b4571','name':'Prapor','nameFr':'Prapor','role':'Armes et logistique','specialty':'armes','lead':'Armes, munitions et tâches de progression. Comparez le niveau PMC et la réputation; le volume d’achats n’est plus la condition de loyauté depuis 1.1.0.','strategy':'Regroupez les objectifs compatibles par carte et relisez les conditions depuis le menu du mode ouvert. Les offres affichées ici ne représentent pas le stock courant.'},
    {'slug':'therapist','id':'54cb57776803fa99248b456e','name':'Therapist','nameFr':'La Toubib','role':'Soins et services médicaux','specialty':'soins','lead':'Soins, assurances, objets médicaux et tâches de collecte. Les tarifs et services varient; vérifiez toujours les valeurs visibles dans le client.','strategy':'Avant une remise, vérifiez si l’objet est nécessaire à une tâche ou à une amélioration proche. Ne traitez pas un export comme la disponibilité de votre compte.'},
    {'slug':'skier','id':'58330581ace78e27b8b10cee','name':'Skier','nameFr':'Skier','role':'Équipement et embranchements','specialty':'équipement','lead':'Équipement et tâches pouvant s’inscrire dans des branches ou événements. Distinguez les tâches permanentes des chaînes limitées dans le temps.','strategy':'Lisez les choix, récompenses et éventuels effets sur la réputation dans le client avant de valider une étape irréversible.'},
    {'slug':'peacekeeper','id':'5935c25fb3acc3127c3d8cd9','name':'Peacekeeper','nameFr':'Peacekeeper','role':'Dollars et équipement occidental','specialty':'équipement','lead':'Un profil orienté dollars et équipements occidentaux. Les seuils de loyauté ne sont pas des prix de conversion ni un catalogue de stock.','strategy':'Gardez une réserve de dollars pour vos objectifs immédiats. Depuis la refonte 1.1.0, dépenser davantage n’augmente plus la loyauté.'},
    {'slug':'mechanic','id':'5a7c2eca46aef81a7ca2145d','name':'Mechanic','nameFr':'Le Mécano','role':'Modifications et Gunsmith','specialty':'armes','lead':'Modifications d’armes, réparations et tâches Gunsmith. BSG indique que Weapon Build est accessible sans attendre une amélioration de l’établi.','strategy':'Contrôlez la compatibilité de chaque pièce dans le preset du client; une ancienne liste d’assemblage peut être dépassée par un patch.'},
    {'slug':'ragman','id':'5ac3b934156ae10c4430e83c','name':'Ragman','nameFr':'Ragman','role':'Vêtements, portage et protection','specialty':'protection','lead':'Vêtements tactiques, sacs, rigs et matériel de protection. Collector réclame Ragman LL4 dans le snapshot communautaire consulté.','strategy':'Gardez séparés équipements, objets de quête et matériaux de planque; vérifiez les besoins du mode actif avant une remise.'},
    {'slug':'jaeger','id':'5c0647fdd443bc2504c2d371','name':'Jaeger','nameFr':'Jaeger','role':'Survie, chasse et services','specialty':'survie','lead':'Tâches de survie et de chasse, équipements spécialisés et services dont les conditions changent selon le mode.','strategy':'Planifiez les objectifs de terrain ensemble, mais relisez contraintes d’arme, distance, extraction et disponibilité dans la tâche active. BSG indique que l’assurance de Jaeger n’est pas disponible en PvP Seasonal.'},
    {'slug':'fence','id':'579dc571d53a0658a154fbec','name':'Fence','nameFr':'Fence','role':'Scav, réputation et Collector','specialty':'scav','lead':'Fence relie les activités Scav et la réputation. Collector est aussi une tâche de Fence dans l’export, mais ses conditions de fin de jeu divergent entre sources communautaires.','strategy':'Gardez distincts réputation Fence, sept traders LL4, prérequis de tâches et objets FIR. Les valeurs de cette page ne confirment pas la disponibilité sur votre profil.'},
    {'slug':'lightkeeper','id':'638f541a29ffd1183d187f57','name':'Lightkeeper','nameFr':'Lightkeeper','role':'Progression narrative et Lighthouse','specialty':'histoire','lead':'Lightkeeper est un interlocuteur à accès narratif, pas un profil de loyauté classique. L’export ne marque aucune tâche avec lightkeeperRequired; ce zéro ne prouve pas l’absence de contenu lié.','strategy':'Vérifiez les conditions d’accès dans le client et les notes BSG récentes. N’appliquez pas une ancienne checklist à votre mode sans revalidation.'},
    {'slug':'ref','id':'6617beeaa9cfa777ca915b7c','name':'Ref','nameFr':'Ref','role':'Arena et offres dédiées','specialty':'arena','lead':'Ref est lié à EFT: Arena. Les règles de transfert dépendent du mode et de la période; BSG décrit une synchronisation Arena vers PvP Seasonal, pas un transfert général bidirectionnel.','strategy':'Avant un transfert, vérifiez le profil, la saison et la période d’acquisition des ressources. Les notes 1.1.0 priment sur les guides Arena plus anciens.'},
]

AUXILIARY_TRADERS = {
    'taran':('Taran','Interlocuteur de l’histoire'),
    'radio-station':('Station radio','Lieu / interface'),
    'btr-driver':('Conducteur du BTR','Service de terrain'),
    'mr-kerman':('M. Kerman','Interlocuteur'),
    'voevoda':('Voevoda','Interlocuteur'),
    'survivor':('Survivor','Interlocuteur'),
}

PAGE_SOURCES = {
    'traders-index':['bsg-patch-110','bsg-patch-130','tdev-endpoints','tdev-traders'],
    'trader-profile':['bsg-patch-110','tdev-endpoints','tdev-traders','tdev-tasks','tracker-community'],
    'fence-profile':['tdev-endpoints','tdev-tasks','tarkov-advisor-collector','fandom-collector','github-886'],
    'lightkeeper-profile':['tdev-endpoints','tdev-tasks','github-886','bsg-patch-115'],
    'ref-profile':['bsg-patch-110','tdev-endpoints','tdev-traders','arena-ref-2024'],
    'quests-index':['bsg-patch-110','tdev-endpoints','tdev-tasks','github-886'],
    'quest-tree':['bsg-patch-110','tdev-endpoints','tdev-tasks','github-886'],
    'kappa-guide':['tdev-endpoints','tdev-tasks','tarkov-advisor-collector','fandom-collector','github-886'],
    'hideout-index':['bsg-patch-110','bsg-patch-130','tdev-endpoints','tdev-hideout'],
    'crafting':['bsg-patch-110','tdev-endpoints','tdev-crafts','reddit-hideout'],
}


def _page(file, route, kind, title, label, code, lead, hero, hero_alt, secondary, secondary_alt, quick, source_key, trader=None):
    return {'file':file,'route':route,'kind':kind,'title':title,'label':label,'code':code,'lead':lead,
            'hero':hero,'heroAlt':hero_alt,'secondary':secondary,'secondaryAlt':secondary_alt,
            'quick':quick,'sourcesKey':source_key,'trader':trader}

PAGES = [_page(
    'pages/traders/index.html','pages/traders/','traders-index','Traders & interlocuteurs','Traders','P–01',
    'Choisissez un profil, comparez les seuils de loyauté et distinguez commerçants, services et personnages d’histoire.',
    'images/phase7/traders-market.jpg','Comptoir de marché fictif, caisses et éclairage d’atelier.',
    'images/phase7/trader-ledger.jpg','Registre de comptoir fictif, sans portrait ni inventaire officiel.',
    [('profils','16 entrées amont','Parcourir'),('loyalty','LL et réputation','Comparer'),('method-note','Modes et sources','Comprendre')],'traders-index')]
for i, profile in enumerate(TRADER_PROFILES, start=2):
    PAGES.append(_page(
        f"pages/traders/{profile['slug']}.html",f"pages/traders/{profile['slug']}.html",'trader-profile',
        profile['name'] if profile['name']==profile['nameFr'] else f"{profile['name']} · {profile['nameFr']}",
        profile['nameFr'],f'P–{i:02d}',profile['lead'],
        'images/phase7/traders-market.jpg','Comptoir de marché fictif; illustration éditoriale originale.',
        'images/phase7/trader-ledger.jpg','Registre fictif; aucun portrait ni stock exact du jeu.',
        [('loyalty','Seuils par mode','Comparer'),('tasks','Tâches associées','Parcourir'),('limits','Conseils et limites','Lire')],
        'fence-profile' if profile['slug']=='fence' else 'lightkeeper-profile' if profile['slug']=='lightkeeper' else 'ref-profile' if profile['slug']=='ref' else 'trader-profile',
        profile['slug']))
PAGES += [
    _page('pages/quests/index.html','pages/quests/','quests-index','Quêtes de Tarkov','Quêtes','Q–01',
          'Recherchez les tâches de l’export communautaire en gardant PvP permanent, PvE Zone et PvP Seasonal séparés.',
          'images/phase7/quest-dossier.jpg','Dossier de terrain fictif, sans texte d’interface du jeu.',
          'images/phase7/quest-board.jpg','Tableau de planification fictif; les objectifs réels viennent des données datées.',
          [('quest-filter','Explorer les tâches','Filtrer'),('quest-stats','Couverture des données','Vérifier'),('progress-tools','Arbre et Kappa','Ouvrir')],'quests-index'),
    _page('pages/quests/quest-tree.html','pages/quests/quest-tree.html','quest-tree','Arbre des quêtes','Arbre des quêtes','Q–02',
          'Remontez les prérequis déclarés par le snapshot et suivez une progression locale sans supposer la logique du client.',
          'images/phase7/quest-board.jpg','Tableau de planification fictif, sans carte de jeu.',
          'images/phase7/quest-dossier.jpg','Dossier de mission fictif.',
          [('tree-tool','Explorer un prérequis','Ouvrir'),('tree-state','Progression locale','Gérer'),('method','Méthode et limites','Lire')],'quest-tree'),
    _page('pages/quests/kappa-guide.html','pages/quests/kappa-guide.html','kappa-guide','Guide du conteneur Kappa','Kappa / Collector','Q–03',
          'Comparez les conditions communautaires de Collector et suivez les objectifs FIR du snapshot sans confondre export et client.',
          'images/phase7/kappa-case.jpg','Conteneur de rangement fictif dans une planque; image non officielle.',
          'images/phase7/quest-dossier.jpg','Dossier de quête fictif.',
          [('requirements','Conditions d’accès','Vérifier'),('kappa-items','Objets Collector','Cocher'),('kappa-method','Désaccord des sources','Lire')],'kappa-guide'),
    _page('pages/hideout/index.html','pages/hideout/','hideout-index','Planque (Hideout)','Planque','H–01',
          'Choisissez le mode, explorez les stations et distinguez besoins exportés, dépendances et prix saisis par vous.',
          'images/phase7/hideout-crafting.jpg','Atelier improvisé dans une planque fictive, outils sous une lampe.',
          'images/phase7/hideout-plan.jpg','Plan dessiné d’une planque modulaire fictive, non à l’échelle.',
          [('hideout-stations','Stations et paliers','Parcourir'),('hideout-filter','Filtrer les ressources','Filtrer'),('method','Modes et coûts','Comprendre')],'hideout-index'),
    _page('pages/hideout/crafting.html','pages/hideout/crafting.html','crafting','Atelier & recettes','Atelier & recettes','H–02',
          'Comparez les recettes par mode et estimez leur coût avec vos prix manuels; aucun cours flea n’est prérempli.',
          'images/phase7/crafting-recipe.jpg','Recette d’atelier fictive et composants sous une lampe.',
          'images/phase7/hideout-crafting.jpg','Atelier improvisé dans une planque fictive.',
          [('craft-tool','Calculer une recette','Choisir'),('craft-results','Résultats estimés','Comparer'),('craft-method','Coûts et prudence','Lire')],'crafting'),
]


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def write_json(path, data):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def esc(value):
    return escape(str(value if value is not None else ''), quote=True)


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _fetch_one(mode_endpoint):
    mode, endpoint = mode_endpoint
    url = f'{BASE}{mode}/{endpoint}'
    request = Request(url, headers={'User-Agent':USER_AGENT,'Accept':'application/json'})
    with urlopen(request, timeout=90) as response:
        raw = response.read()
        payload = json.loads(raw)
        data = payload.get('data', payload)
        meta = {'url':url,'httpStatus':response.status,'lastModified':response.headers.get('Last-Modified'),
                'etag':response.headers.get('ETag'),'bytesDecoded':len(raw),'sha256Decoded':sha256(raw).hexdigest()}
    return mode, endpoint, data, meta


def fetch_all():
    requested = [(mode,endpoint) for mode in MODES for endpoint in ENDPOINTS]
    data, metadata = {mode:{} for mode in MODES}, {mode:{} for mode in MODES}
    errors = []
    with ThreadPoolExecutor(max_workers=15) as pool:
        futures = {pool.submit(_fetch_one,item):item for item in requested}
        for future in as_completed(futures):
            mode, endpoint = futures[future]
            try:
                _, _, payload, meta = future.result()
                data[mode][endpoint] = payload
                metadata[mode][endpoint] = meta
                print(f"OK {mode}/{endpoint}: {meta['bytesDecoded']:,} octets · {meta.get('lastModified') or 'Last-Modified absent'}")
            except Exception as error:
                errors.append(f'{mode}/{endpoint}: {error!r}')
                print(f'ERREUR {mode}/{endpoint}: {error}',file=sys.stderr)
    if errors:
        raise RuntimeError('Collecte incomplète; aucun snapshot écrit: ' + '; '.join(errors))
    return data, metadata


def _translated(bundle, key, fallback=''):
    if not key:
        return fallback
    value = bundle.get(key)
    if isinstance(value,str) and value.strip() and value != key:
        clean = value.strip()
        if clean.lower() not in {'<inconnu>','<unknown>','unknown','inconnu'}:
            return clean
    return fallback or (value.strip() if isinstance(value,str) and value.strip() and not value.startswith('<') else '')


def _item_name(items, item_id, lang='fr'):
    item = items.get(item_id) or {}
    value = item.get('nameFr' if lang=='fr' else 'nameEn') or item.get('shortNameFr' if lang=='fr' else 'shortNameEn')
    return value or item.get('normalizedName') or item_id or 'Objet non résolu'


def _task_rows(mode, raw, map_names, items):
    task_root = _dict(raw.get('tasks'))
    raw_tasks = _dict(task_root.get('tasks'))
    fr, en = _dict(raw.get('tasks_fr')), _dict(raw.get('tasks_en'))
    traders = _dict(raw.get('traders'))
    trfr, tren = _dict(raw.get('traders_fr')), _dict(raw.get('traders_en'))
    rows = []
    for task_id, task in raw_tasks.items():
        if not isinstance(task,dict):
            continue
        name_key = task.get('name')
        name_fr = _translated(fr,name_key,task.get('normalizedName') or task_id)
        name_en = _translated(en,name_key,task.get('normalizedName') or task_id)
        trader_id = task.get('trader')
        trader_record = traders.get(trader_id) or {}
        trader_name_fr = _translated(trfr,trader_record.get('name'),'') or None
        trader_name_en = _translated(tren,trader_record.get('name'),'') or None
        map_ids = []
        if isinstance(task.get('map'),str):
            map_ids.append(task['map'])
        elif isinstance(task.get('map'),dict):
            map_ids.extend([task['map'].get('id'),task['map'].get('map')])
        objectives = []
        for objective in _list(task.get('objectives')):
            if not isinstance(objective,dict):
                continue
            zone_maps = [zone.get('map') for zone in _list(objective.get('zones')) if isinstance(zone,dict)]
            obj_maps = _list(objective.get('maps')) + zone_maps
            map_ids.extend(x for x in obj_maps if isinstance(x,str))
            item_ids = [x for x in _list(objective.get('items')) if isinstance(x,str)]
            objectives.append({'type':objective.get('type'),'count':objective.get('count'),'optional':bool(objective.get('optional')),
                'foundInRaid':objective.get('foundInRaid'),'itemIds':item_ids,
                'itemNamesFr':[_item_name(items,iid,'fr') for iid in item_ids[:8]],
                'mapIds':list(dict.fromkeys(x for x in obj_maps if isinstance(x,str))),
                'descriptionFr':_translated(fr,objective.get('description'),'')})
        map_ids = list(dict.fromkeys(x for x in map_ids if isinstance(x,str)))
        requirements = []
        for req in _list(task.get('taskRequirements')):
            if isinstance(req,dict) and req.get('task'):
                requirements.append({'taskId':req['task'],'status':_list(req.get('status')),'notes':req.get('notes')})
        trader_requirements = []
        for req in _list(task.get('traderRequirements')):
            if isinstance(req,dict):
                trader = traders.get(req.get('trader')) or {}
                trader_requirements.append({'traderId':req.get('trader'),'traderNameFr':_translated(trfr,trader.get('name'),'') or None,
                    'type':req.get('requirementType'),'compare':req.get('compareMethod'),'value':req.get('value')})
        other_requirements = []
        for req in _list(task.get('otherRequirements')):
            if isinstance(req,dict):
                other_requirements.append({k:req.get(k) for k in ('type','compareMethod','value','variableId') if req.get(k) is not None})
        finish = _dict(task.get('finishRewards'))
        standing = [{'traderId':row.get('trader'),'standing':row.get('standing')} for row in _list(finish.get('traderStanding')) if isinstance(row,dict)]
        rows.append({'id':task_id,'nameFr':name_fr,'nameEn':name_en,'normalizedName':task.get('normalizedName') or '',
            'traderId':trader_id,'traderNameFr':trader_name_fr,'traderNameEn':trader_name_en,'wikiLink':task.get('wikiLink'),
            'minPlayerLevel':task.get('minPlayerLevel'),'kappaRequired':bool(task.get('kappaRequired')),
            'lightkeeperRequired':bool(task.get('lightkeeperRequired')),'factionName':task.get('factionName'),
            'mapIds':map_ids,'mapNames':[map_names[mid] for mid in map_ids if mid in map_names],
            'taskRequirements':requirements,'traderRequirements':trader_requirements,'otherRequirements':other_requirements,
            'objectives':objectives,'objectiveCount':len(objectives),'finishTraderStanding':standing})
    by_id = {row['id']:row for row in rows}
    for row in rows:
        for req in row['taskRequirements']:
            required = by_id.get(req['taskId'])
            req['present'] = bool(required)
            req['nameFr'] = required['nameFr'] if required else None
            req['nameEn'] = required['nameEn'] if required else None
    rows.sort(key=lambda row:(row['minPlayerLevel'] if isinstance(row['minPlayerLevel'],(int,float)) else 999,row['nameFr'].casefold(),row['id']))
    missing_fr = sum(1 for task in raw_tasks.values() if isinstance(task,dict) and task.get('name') not in fr)
    return rows, task_root, missing_fr


def _make_snapshot(mode, raw, endpoint_metadata, local_items, map_names, collected_at):
    tasks, task_root, missing_fr = _task_rows(mode,raw,map_names,local_items)
    task_by_id = {task['id']:task for task in tasks}
    trader_raw = _dict(raw.get('traders'))
    trader_fr, trader_en = _dict(raw.get('traders_fr')),_dict(raw.get('traders_en'))
    traders = []
    for trader_id, trader in trader_raw.items():
        if not isinstance(trader,dict):
            continue
        name_key = trader.get('name')
        levels = [{key:level.get(key) for key in ('level','requiredPlayerLevel','requiredReputation','requiredCommerce','payRate','insuranceRate','repairCostMultiplier')}
                  for level in _list(trader.get('levels'))]
        reputation_levels = [{key:row.get(key) for key in ('minimumReputation','scavCooldownModifier','scavCaseTimeModifier','extractPriceModifier','priceModifier','hostileBosses','hostileScavs','availableScavExtracts') if key in row}
                             for row in _list(trader.get('reputationLevels'))]
        traders.append({'id':trader_id,'normalizedName':trader.get('normalizedName') or '',
            'nameFr':_translated(trader_fr,name_key,trader.get('normalizedName') or trader_id),
            'nameEn':_translated(trader_en,name_key,trader.get('normalizedName') or trader_id),
            'descriptionFr':_translated(trader_fr,trader.get('description'),''),'descriptionEn':_translated(trader_en,trader.get('description'),''),
            'currency':trader.get('currency'),'levels':levels,'reputationLevels':reputation_levels})
    traders.sort(key=lambda row:row['nameFr'].casefold())
    trader_by_id = {row['id']:row for row in traders}
    for task in tasks:
        task['traderNameFr'] = trader_by_id.get(task.get('traderId'),{}).get('nameFr') or task.get('traderNameFr')
        task['traderNameEn'] = trader_by_id.get(task.get('traderId'),{}).get('nameEn') or task.get('traderNameEn')
        for req in task['traderRequirements']:
            req['traderNameFr'] = trader_by_id.get(req.get('traderId'),{}).get('nameFr') or req.get('traderNameFr')

    stations_raw = _dict(raw.get('hideout'))
    hideout_fr, hideout_en = _dict(raw.get('hideout_fr')),_dict(raw.get('hideout_en'))
    stations = []
    for station_id, station in stations_raw.items():
        if not isinstance(station,dict):
            continue
        levels=[]; item_total=0; item_fir=0
        for level in _list(station.get('levels')):
            item_requirements=[]
            for req in _list(level.get('itemRequirements')):
                if not isinstance(req,dict):
                    continue
                item_id=req.get('item'); attributes=_dict(req.get('attributes')); fir=bool(attributes.get('foundInRaid'))
                item_requirements.append({'itemId':item_id,'nameFr':_item_name(local_items,item_id,'fr'),'nameEn':_item_name(local_items,item_id,'en'),
                    'count':req.get('count'),'foundInRaid':fir,'tool':bool(attributes.get('tool'))})
                item_total+=1; item_fir+=int(fir)
            station_reqs=[{'stationId':row.get('station'),'level':row.get('level')} for row in _list(level.get('stationLevelRequirements')) if isinstance(row,dict)]
            trader_reqs=[{'traderId':row.get('trader'),'level':row.get('level'),'reputation':row.get('reputation')} for row in _list(level.get('traderRequirements')) if isinstance(row,dict)]
            skill_reqs=[{'skill':row.get('skill'),'level':row.get('level')} for row in _list(level.get('skillRequirements')) if isinstance(row,dict)]
            bonuses=[{key:row.get(key) for key in ('type','value','passive','production','skill')} for row in _list(level.get('bonuses')) if isinstance(row,dict)]
            levels.append({'id':level.get('id'),'level':level.get('level'),'constructionTime':level.get('constructionTime'),
                'itemRequirements':item_requirements,'stationRequirements':station_reqs,'traderRequirements':trader_reqs,'skillRequirements':skill_reqs,'bonuses':bonuses})
        name_key=station.get('name')
        stations.append({'id':station_id,'nameFr':_translated(hideout_fr,name_key,station.get('normalizedName') or station_id),
            'nameEn':_translated(hideout_en,name_key,station.get('normalizedName') or station_id),'normalizedName':station.get('normalizedName'),
            'areaType':station.get('areaType'),'levels':levels,'itemRequirementRows':item_total,'firRequirementRows':item_fir})
    station_by_id={row['id']:row for row in stations}
    for station in stations:
        for level in station['levels']:
            for req in level['stationRequirements']:
                req['nameFr']=station_by_id.get(req['stationId'],{}).get('nameFr') or req.get('stationId') or 'Station non résolue'
            for req in level['traderRequirements']:
                req['nameFr']=trader_by_id.get(req['traderId'],{}).get('nameFr') or req.get('traderId') or 'Trader non résolu'
    stations.sort(key=lambda row:row['nameFr'].casefold())

    crafts=[]
    for recipe in _list(raw.get('crafts')):
        if not isinstance(recipe,dict):
            continue
        station_id=recipe.get('station'); product=_dict(recipe.get('productItem')); ingredients=[]
        for req in _list(recipe.get('requiredItems')):
            if not isinstance(req,dict):
                continue
            item_id=req.get('item')
            ingredients.append({'itemId':item_id,'nameFr':_item_name(local_items,item_id,'fr'),'nameEn':_item_name(local_items,item_id,'en'),
                'count':req.get('count'),'tool':bool(_dict(req.get('attributes')).get('tool'))})
        output_id=product.get('item')
        crafts.append({'id':recipe.get('id'),'stationId':station_id,'stationNameFr':station_by_id.get(station_id,{}).get('nameFr') or station_id or 'Station non résolue',
            'stationNameEn':station_by_id.get(station_id,{}).get('nameEn') or station_id or 'Unknown station','level':recipe.get('level'),
            'duration':recipe.get('duration'),'taskUnlock':recipe.get('taskUnlock'),'requiredQuestItems':_list(recipe.get('requiredQuestItems'),),
            'ingredients':ingredients,'output':{'itemId':output_id,'nameFr':_item_name(local_items,output_id,'fr'),'nameEn':_item_name(local_items,output_id,'en'),'count':product.get('count')}})
    crafts.sort(key=lambda row:(row['stationNameFr'].casefold(),row.get('level') or 0,row.get('duration') or 0,row.get('id') or ''))

    collector=next((task for task in tasks if task.get('normalizedName')=='collector'),None)
    missing_task_refs=sorted({req['taskId'] for task in tasks for req in task['taskRequirements'] if not req['present']})
    missing_unlocks=sorted({recipe['taskUnlock'] for recipe in crafts if recipe.get('taskUnlock') and recipe['taskUnlock'] not in task_by_id})
    metrics={'tasks':len(tasks),'taskNamesMissingFrench':missing_fr,'questItems':len(set(_dict(task_root.get('questItems')))),
        'kappaFlagged':sum(1 for task in tasks if task['kappaRequired']),'lightkeeperFlagged':sum(1 for task in tasks if task['lightkeeperRequired']),
        'traders':len(traders),'stations':len(stations),'stationLevels':sum(len(row['levels']) for row in stations),
        'hideoutItemRequirementRows':sum(row['itemRequirementRows'] for row in stations),'hideoutFirRequirementRows':sum(row['firRequirementRows'] for row in stations),
        'crafts':len(crafts),'barters':len(_list(raw.get('barters'))),'missingTaskReferences':missing_task_refs,'missingCraftUnlockTasks':missing_unlocks,
        'issue886MissingIds':[qid for qid in MISSING_ISSUE_IDS if qid not in task_by_id],
        'collectorObjectives':len(collector['objectives']) if collector else 0,
        'collectorFoundInRaidObjectives':sum(1 for row in collector['objectives'] if row.get('foundInRaid')) if collector else 0}
    return {'schemaVersion':1,'snapshotDateReference':DATE,'collectedAtUtc':collected_at,'mode':mode,'modeLabel':MODES[mode],
        'publisher':'Tarkov.dev / the-hideout/tarkov-data-manager · source communautaire non officielle',
        'sourceUrl':BASE+mode,'upstream':endpoint_metadata,'metrics':metrics,'traders':traders,'tasks':tasks,'stations':stations,'crafts':crafts,
        'notes':['Modes conservés séparément; ne pas fusionner les listes.','Descriptions complètes des objectifs non recopiées; seules les clés utiles à la navigation sont conservées.','Prix flea, offres de stock et résultats de raid exclus.']}


def collect_snapshots():
    collected_at=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
    raw,metadata=fetch_all()
    local_items={row['id']:row for row in _list(read_json('js/data/items.json').get('records')) if isinstance(row,dict) and row.get('id')}
    map_snapshot=read_json('data/snapshots/cartes-2026-11-18.json')
    map_names={row.get('id'):row.get('nameEn') for row in map_snapshot['modes']['regular']['mapRecords'] if row.get('id') and row.get('nameEn')}
    snapshots={mode:_make_snapshot(mode,raw[mode],metadata[mode],local_items,map_names,collected_at) for mode in MODES}
    ids_by_mode={mode:{task['id'] for task in snapshots[mode]['tasks']} for mode in MODES}
    union=set().union(*ids_by_mode.values())
    comparison={'unionTaskIds':len(union),'missingInMode':{mode:len(union-ids_by_mode[mode]) for mode in MODES},
                'missingIssue886ByMode':{mode:snapshots[mode]['metrics']['issue886MissingIds'] for mode in MODES}}
    return snapshots,comparison


def _snapshot_path(mode):
    return f'data/snapshots/phase-7-{mode}-{DATE}.json'


def _load_snapshots():
    paths={mode:_snapshot_path(mode) for mode in MODES}
    missing=[path for path in paths.values() if not (ROOT/path).is_file()]
    if missing:
        raise FileNotFoundError('Snapshots PHASE_7 absents: '+', '.join(missing)+'; lancer --fetch.')
    return {mode:read_json(paths[mode]) for mode in MODES}


def _task_dependency_audit(tasks):
    by_id={task['id']:task for task in tasks}
    graph={task_id:[req['taskId'] for req in task.get('taskRequirements',[]) if req.get('taskId') in by_id] for task_id,task in by_id.items()}
    missing=sorted({req['taskId'] for task in tasks for req in task.get('taskRequirements',[]) if req.get('taskId') not in by_id})
    multi=[task for task in tasks if len(task.get('taskRequirements',[]))>1]
    color={}; stack=[]; cycles=set()
    def visit(task_id):
        color[task_id]=1; stack.append(task_id)
        for req_id in graph.get(task_id,[]):
            if color.get(req_id)==1:
                cycle=stack[stack.index(req_id):]
                cycles.add(min(tuple(cycle[i:]+cycle[:i]) for i in range(len(cycle))))
            elif color.get(req_id,0)==0:
                visit(req_id)
        stack.pop(); color[task_id]=2
    for task_id in graph:
        if color.get(task_id,0)==0: visit(task_id)
    return {'taskCount':len(tasks),'edgeCount':sum(len(edges) for edges in graph.values()),'missingReferenceIds':missing,
        'cycleCount':len(cycles),'cycles':[[*cycle,cycle[0]] for cycle in sorted(cycles)],
        'tasksWithMultiplePrerequisites':len(multi),'multiplePrerequisiteExamples':[{'id':row['id'],'nameFr':row['nameFr'],'requirements':[r.get('nameFr') or r['taskId'] for r in row['taskRequirements']]} for row in multi[:12]],
        'logicNotInferred':True}


def build_data():
    snapshots=_load_snapshots()
    modes={mode:{'label':MODES[mode],'metrics':snapshots[mode]['metrics'],'dependencyAudit':_task_dependency_audit(snapshots[mode]['tasks']),
        'traders':snapshots[mode]['traders'],'tasks':snapshots[mode]['tasks'],'stations':snapshots[mode]['stations'],'crafts':snapshots[mode]['crafts']} for mode in MODES}
    collector_by_mode={mode:next((task for task in modes[mode]['tasks'] if task['normalizedName']=='collector'),None) for mode in MODES}
    return {'schemaVersion':1,'snapshotDateReference':DATE,'publisher':'Tarkov.dev / the-hideout/tarkov-data-manager · communautaire',
        'traders':[{'slug':row['slug'],'id':row['id'],'name':row['name'],'nameFr':row['nameFr']} for row in TRADER_PROFILES],
        'modes':modes,'collectorByMode':collector_by_mode,'issue886MissingIds':MISSING_ISSUE_IDS,
        'notes':['Données statiques datées, non-live; vérifier tâches, stock et conditions dans le client.',
            'Collector : Fandom consulté indique niveau 40 et quatre prérequis, contre niveau 42 et cinq dans Tarkov.dev/Tarkov Advisor.',
            'Balises kappaRequired/lightkeeperRequired à zéro et tâches manquantes ne prouvent pas une absence de contenu.']}


def sync_sources():
    path=ROOT/'docs/sources.json'
    doc=json.loads(path.read_text(encoding='utf-8'))
    manifest_path=ROOT/f'data/snapshots/phase-7-manifest-{DATE}.json'
    manifest=json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.is_file() else {}
    observed={mode:{endpoint:manifest.get('modes',{}).get(mode,{}).get('upstream',{}).get(endpoint,{}).get('lastModified')
        for endpoint in ('tasks','traders','hideout','crafts','barters')} for mode in MODES}
    doc['releve_le']=DATE
    doc['revalidation_phase_7']={'date':DATE,'snapshot_date_reference':DATE,'collected_at_utc':manifest.get('collectedAtUtc'),
        'observed_upstream_last_modified':observed,'snapshots':{mode:_snapshot_path(mode) for mode in MODES},
        'notes':'Tarkov.dev, source communautaire, archivé séparément par mode. L’heure UTC de collecte est conservée indépendamment de la date de référence locale. Collector diverge de Fandom; issue #886 observée ouverte. Reddit direct a répondu HTTP 403; la vidéo YouTube n’a pas été visionnée intégralement.'}
    path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def fmt_num(value):
    try: return f'{int(value):,}'.replace(',','\u202f')
    except (TypeError,ValueError): return '—'


def fmt_rep(value):
    try: return f'{float(value):.2f}'.replace('.',',')
    except (TypeError,ValueError): return '—'


def fmt_duration(value):
    try:
        seconds=max(0,int(value))
    except (TypeError,ValueError):
        return 'Durée non renseignée'
    minutes=round(seconds/60); hours,rest=divmod(minutes,60)
    return f'{hours} h {rest:02d} min' if hours else f'{minutes} min'


def _item_figure(path,alt,caption,root):
    return f'<figure class="phase7-support-figure"><img src="{esc(root+path)}" width="1376" height="768" loading="lazy" decoding="async" alt="{esc(alt)}"><figcaption>{esc(caption)}</figcaption></figure>'


def _source_html(keys):
    sources=read_json('docs/sources.json').get('sources',{})
    rows=[]
    for key in keys:
        row=sources.get(key)
        if not row: continue
        rows.append(f'<li><span class="phase7-source-type">{esc(row.get("type","source"))}</span><a href="{esc(row.get("url","#"))}" rel="noopener noreferrer">{esc(row.get("titre",key))} <span aria-hidden="true">↗</span></a><span>{esc(row.get("usage",""))}</span></li>')
    return ''.join(rows)


def _tag(text,warn=False):
    return f'<span class="phase7-tag{" phase7-tag--warn" if warn else ""}">{esc(text)}</span>'


def _task_url(task,mode,root='../../'):
    return f'{root}pages/quests/?mode={mode}&task={task["id"]}'


def _static_quest_row(task,mode):
    href=task.get('wikiLink') or _task_url(task,mode)
    rel=' rel="noopener noreferrer"' if task.get('wikiLink') else ''
    badges=[]
    if task.get('kappaRequired'): badges.append(_tag('Kappa · export'))
    if task.get('lightkeeperRequired'): badges.append(_tag('Lightkeeper · export',True))
    if task.get('taskRequirements'): badges.append(_tag(f'{len(task["taskRequirements"])} prérequis'))
    if task.get('objectiveCount'): badges.append(_tag(f'{task["objectiveCount"]} objectifs'))
    if not badges: badges.append(_tag('Aucune balise exportée'))
    return (f'<tr><th scope="row"><a href="{esc(href)}"{rel}>{esc(task["nameFr"])}</a><small>{esc(task.get("nameEn",""))}</small></th>'
            f'<td>{esc(task.get("traderNameFr") or "Non résolu")}</td><td>{esc(task.get("minPlayerLevel") if task.get("minPlayerLevel") is not None else "—")}</td>'
            f'<td>{esc(", ".join(task.get("mapNames",[])) or "Non renseignée")}</td><td><div class="phase7-row-badges">{"".join(badges)}</div></td>'
            f'<td><span class="phase7-muted">Suivi local disponible avec JavaScript.</span></td></tr>')


def _static_trader_levels(trader,profile):
    rows=[]
    for level in trader.get('levels',[]):
        is_fence=profile['slug']=='fence'
        label=f"Fence · niveau {level.get('level')}" if is_fence else f"Palier {level.get('level')}" if profile['slug'] in ('lightkeeper','ref') else f"LL{level.get('level')}"
        commerce=level.get('requiredCommerce')
        commerce_text='Non renseigné' if commerce is None else f'{fmt_num(commerce)} · export'
        rows.append(f'<tr><th scope="row">{esc(label)}</th><td>{esc(fmt_num(level.get("requiredPlayerLevel")))}</td><td>{esc(fmt_rep(level.get("requiredReputation")))}</td><td>{esc(commerce_text)}</td></tr>')
    return ''.join(rows) or '<tr><td colspan="4">Aucun palier détaillé dans ce snapshot.</td></tr>'


def _static_trader_tasks(data,trader_id,mode='regular',limit=12):
    tasks=[task for task in data['modes'][mode]['tasks'] if task.get('traderId')==trader_id]
    parts=[]
    for task in tasks[:limit]:
        tags=[_tag(f'Niveau {task.get("minPlayerLevel") if task.get("minPlayerLevel") is not None else "—"}')]
        if task.get('mapNames'): tags.append(_tag(' · '.join(task['mapNames'])))
        if task.get('kappaRequired'): tags.append(_tag('Kappa · export'))
        parts.append(f'<li class="phase7-task-row"><div><a href="{esc(_task_url(task,mode))}">{esc(task["nameFr"])}</a><div class="phase7-task-row__meta">{"".join(tags)}</div></div><span>{task.get("objectiveCount",0)} objectif(s)</span></li>')
    return ''.join(parts) or '<li>Aucune tâche associée à cet ID dans ce snapshot; cela ne prouve pas l’absence de tâche dans le client.</li>'


def _static_loyalty_rows(data):
    ids=['54cb50c76803fa8b248b4571','54cb57776803fa99248b456e','58330581ace78e27b8b10cee','5935c25fb3acc3127c3d8cd9',
         '5a7c2eca46aef81a7ca2145d','5ac3b934156ae10c4430e83c','5c0647fdd443bc2504c2d371','579dc571d53a0658a154fbec']
    mode=data['modes']['regular'];names={row['id']:row['nameFr'] for row in mode['traders']};rows=[]
    for trader_id in ids:
        trader=next((row for row in mode['traders'] if row['id']==trader_id),None)
        if not trader: continue
        for level in trader.get('levels',[]):
            if level.get('level',1)<2 and trader['normalizedName']!='fence': continue
            label=f"Fence {level.get('level')}" if trader['normalizedName']=='fence' else f"LL{level.get('level')}"
            rows.append(f'<tr><th scope="row">{esc(names.get(trader_id,trader["nameFr"]))}</th><td>{esc(label)}</td><td>{esc(fmt_num(level.get("requiredPlayerLevel")))}</td><td>{esc(fmt_rep(level.get("requiredReputation")))}</td><td>{esc(fmt_num(level.get("requiredCommerce")))}</td></tr>')
    return ''.join(rows)


def _profile_content(page,data,root):
    profile=next(row for row in TRADER_PROFILES if row['slug']==page['trader'])
    trader=next((row for row in data['modes']['regular']['traders'] if row['id']==profile['id']),{'levels':[]})
    image=_item_figure(page['secondary'],page['secondaryAlt'],'Illustration éditoriale originale; ni portrait ni stock du jeu.',root)
    note=('Fence suit une progression Scav/réputation spécifique; ses niveaux exportés ne sont pas des LL2–LL4 classiques.' if profile['slug']=='fence' else
          'Lightkeeper n’est pas comparable aux commerçants classiques. Un palier technique exporté ne décrit pas les conditions d’accès.' if profile['slug']=='lightkeeper' else
          'Ref possède des paliers dédiés. La synchronisation Arena dépend du mode et de la période décrits par BSG.' if profile['slug']=='ref' else
          'Le volume commercial est retiré comme condition de loyauté selon BSG 1.1.0. Le niveau et la réputation exportés ne prouvent pas le déblocage sur un compte.')
    return f'''<section class="phase7-intro" id="method" tabindex="-1"><div class="phase7-intro__copy"><p class="guide-kicker">REPÈRE / {esc(profile['role'])}</p><h2>Rôle, progression et vérification</h2><p>{esc(profile['lead'])}</p><p>{esc(profile['strategy'])}</p><p class="phase7-note"><strong>Lecture des données :</strong> seuils communautaires datés; aucune offre n’est présentée comme stock temps réel.</p></div>{image}</section>
<section class="guide-section phase7-section" id="loyalty" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> Progression</p><h2>Seuils exportés par mode</h2><p>La table compare niveau PMC, réputation et volume tel que fourni par Tarkov.dev. Les seuils doivent être relus dans le client.</p></div><div class="phase7-controls"><label class="field" for="trader-mode">Mode<select class="field__input" id="trader-mode" data-p7-mode><option value="regular">PvP permanent</option><option value="pve">PvE Zone</option><option value="pvp-season">PvP Seasonal</option></select></label><label class="field" for="trader-level">Afficher le palier<select class="field__input" id="trader-level" data-p7-level-filter><option value="all">Tous les paliers</option><option value="2">LL2 et plus</option><option value="3">LL3 et plus</option><option value="4">LL4</option></select></label></div><div class="phase7-table-wrap" role="region" aria-label="Seuils exportés, défilement horizontal" tabindex="0"><table class="phase7-table"><caption>Seuils communautaires · {esc(profile['name'])} · regular par défaut</caption><thead><tr><th scope="col">Loyauté</th><th scope="col">Niveau PMC</th><th scope="col">Réputation</th><th scope="col">Volume</th></tr></thead><tbody data-p7-trader-levels data-trader-id="{esc(profile['id'])}">{_static_trader_levels(trader,profile)}</tbody></table></div><p class="phase7-note" data-p7-trader-level-note role="status">{esc(note)}</p></section>
<section class="guide-section phase7-section" id="tasks" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>02</span> Tâches</p><h2>Tâches associées au profil</h2><p>Extrait trié selon le niveau minimum déclaré dans le snapshot; ce n’est pas la liste actuellement disponible pour un compte.</p></div><div class="phase7-task-controls"><label class="field" for="trader-task-search">Rechercher un nom<input class="field__input" id="trader-task-search" type="search" data-p7-trader-task-search placeholder="Nom, carte ou trader"></label><label class="field" for="trader-task-status">Balise<select class="field__input" id="trader-task-status" data-p7-trader-task-filter><option value="all">Toutes</option><option value="kappa">Kappa · export</option><option value="lightkeeper">Lightkeeper · export</option></select></label></div><p class="phase7-result-count" data-p7-trader-task-count aria-live="polite"></p><ol class="phase7-task-list" data-p7-trader-task-list data-trader-id="{esc(profile['id'])}">{_static_trader_tasks(data,profile['id'])}</ol><a class="button button--quiet" href="{esc(root+'pages/quests/')}?trader={esc(profile['slug'])}">Ouvrir le filtre complet des quêtes <span aria-hidden="true">↗</span></a></section>
<section class="guide-section phase7-section" id="limits" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>03</span> Vérification terrain</p><h2>Conseil de progression</h2><p>{esc(profile['strategy'])}</p></div><div class="phase7-callout"><strong>Ne partez pas sur une checklist ancienne.</strong><p>Les tâches et offres ont évolué. Relisez les conditions depuis le journal du mode sélectionné et confirmez l’objectif avant d’entrer en raid.</p></div></section>'''


def _traders_index_content(data,root):
    regular=data['modes']['regular'];by_norm={row['normalizedName']:row for row in regular['traders']};cards=[]
    for profile in TRADER_PROFILES:
        cards.append(f'<article class="phase7-card" data-p7-trader-card data-specialty="{esc(profile["specialty"])}" data-trader-kind="profile"><p class="phase7-card__eyebrow">Profil · {esc(profile["role"])}</p><h3><a href="{esc(root+"pages/traders/"+profile["slug"]+".html")}">{esc(profile["nameFr"])} <span aria-hidden="true">↗</span></a></h3><p>{esc(profile["lead"])}</p><p class="phase7-card__meta" data-trader-card-meta data-trader-id="{esc(profile["id"])}">Niveaux du snapshot · regular</p></article>')
    for normalized,(name,kind) in AUXILIARY_TRADERS.items():
        if normalized not in by_norm: continue
        trader=by_norm[normalized]
        cards.append(f'<article class="phase7-card phase7-card--aux" data-p7-trader-card data-specialty="autres" data-trader-kind="aux"><p class="phase7-card__eyebrow">{esc(kind)} · entrée amont</p><h3>{esc(name)}</h3><p>Répertorié dans l’endpoint des traders; ne pas le traiter comme un marchand au stock standard.</p><p class="phase7-card__meta">{len(trader.get("levels",[]))} palier(s) technique(s) · rôle à vérifier en jeu</p></article>')
    m=regular['metrics'];cards_static=''.join(cards)
    image=_item_figure('images/phase7/trader-ledger.jpg','Registre de comptoir et caisses dans un bunker fictif.','Illustrations originales; aucun portrait ou inventaire exact des traders.',root)
    return f'''<section class="phase7-intro" id="method" tabindex="-1"><div class="phase7-intro__copy"><p class="guide-kicker">INDEX / COMMERCE & PROGRESSION</p><h2>Dix profils dédiés, six entrées auxiliaires</h2><p>L’endpoint regular retourne {m['traders']} enregistrements. Les huit traders classiques, Lightkeeper et Ref ont une fiche; les autres sont distingués comme interlocuteurs, services ou lieux.</p><p>Les seuils sont des valeurs de catalogue communautaire. Prix, rotations et disponibilité réels ne sont pas un flux live.</p></div>{image}</section>
<section class="guide-section phase7-section" id="profils" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> Profils</p><h2>Choisir un interlocuteur</h2><p>Filtrez par spécialité ou type; les services et offres sont à confirmer dans le mode ouvert.</p></div><div class="phase7-controls"><label class="field" for="trader-specialty">Spécialité<select class="field__input" id="trader-specialty" data-p7-trader-specialty><option value="all">Toutes</option><option value="armes">Armes</option><option value="soins">Soins</option><option value="équipement">Équipement</option><option value="protection">Protection</option><option value="survie">Survie</option><option value="scav">Scav</option><option value="histoire">Histoire</option><option value="arena">Arena</option><option value="autres">Autres entrées</option></select></label><label class="field" for="trader-kind">Type<select class="field__input" id="trader-kind" data-p7-trader-kind><option value="all">Tous</option><option value="profile">Fiche détaillée</option><option value="aux">Service / interlocuteur</option></select></label><button class="button button--quiet" type="button" data-p7-trader-reset>Réinitialiser</button></div><p class="phase7-result-count" data-p7-trader-count aria-live="polite"></p><div class="phase7-card-grid" data-p7-trader-cards>{cards_static}</div></section>
<section class="guide-section phase7-section" id="loyalty" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>02</span> Loyauté</p><h2>Seuils LL2–LL4 et réputation Fence</h2><p>La table conserve les huit traders classiques et Fence dans une ligne distincte; Lightkeeper et Ref ont des progressions différentes.</p></div><div class="phase7-controls"><label class="field" for="loyalty-mode">Mode<select class="field__input" id="loyalty-mode" data-p7-loyalty-mode><option value="regular">PvP permanent</option><option value="pve">PvE Zone</option><option value="pvp-season">PvP Seasonal</option></select></label><label class="field" for="loyalty-tier">Palier<select class="field__input" id="loyalty-tier" data-p7-loyalty-tier><option value="all">Tous</option><option value="2">LL2 / niveau 2 et plus</option><option value="3">LL3 et plus</option><option value="4">LL4</option></select></label></div><div class="phase7-table-wrap" role="region" aria-label="Seuils traders, défilement horizontal" tabindex="0"><table class="phase7-table"><caption>Seuils exportés · regular par défaut</caption><thead><tr><th scope="col">Trader</th><th scope="col">Loyauté</th><th scope="col">Niveau PMC</th><th scope="col">Réputation</th><th scope="col">Volume</th></tr></thead><tbody data-p7-loyalty-table>{_static_loyalty_rows(data)}</tbody></table></div><p class="phase7-note" data-p7-loyalty-note role="status">Les seuils ne prouvent pas le déblocage sur un compte. Depuis 1.1.0, le volume d’achat n’est plus une condition de loyauté.</p></section>
<section class="guide-section phase7-section" id="method-note" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>03</span> Périmètre</p><h2>Stock variable et sources séparées</h2><p>BSG documente les règles générales; Tarkov.dev fournit un export communautaire utile aux seuils, tâches et dépendances. Aucune rotation de stock n’est publiée ici.</p></div><div class="phase7-callout"><strong>Conseil sûr :</strong><p>À chaque nouvelle loyauté, rouvrez les menus du trader et des tâches dans le profil courant. La mise à jour 1.1.0 a modifié les offres et organisé la majorité des tâches secondaires en groupes de loyauté.</p></div></section>'''


def _quest_stats_html(data):
    parts=[]
    for mode,row in data['modes'].items():
        metrics=row['metrics'];audit=row['dependencyAudit']
        for value,label in [(metrics['tasks'],f'{MODES[mode]} · tâches'),(len(metrics['missingTaskReferences']),f'{MODES[mode]} · prérequis absents de l’export'),
                            (audit['cycleCount'],f'{MODES[mode]} · cycles détectés'),(audit['tasksWithMultiplePrerequisites'],f'{MODES[mode]} · tâches à prérequis multiples')]:
            parts.append(f'<div class="phase7-stat"><strong>{esc(value)}</strong><span>{esc(label)}</span></div>')
    parts.append(f'<div class="phase7-stat"><strong>{len(MISSING_ISSUE_IDS)}</strong><span>IDs signalés dans l’issue #886 absents des trois listes interrogées</span></div>')
    return ''.join(parts)


def _quests_index_content(data,root):
    totals=' · '.join(f'{MODES[mode]} : {data["modes"][mode]["metrics"]["tasks"]} tâches' for mode in MODES)
    tasks=data['modes']['regular']['tasks']
    rows=''.join(_static_quest_row(task,'regular') for task in tasks[:60])
    img=_item_figure('images/phase7/quest-board.jpg','Dossiers de terrain et planification fictive, sans interface du jeu.','Illustration éditoriale; objectifs réels à relire dans le client.',root)
    return f'''<section class="phase7-intro" id="method" tabindex="-1"><div class="phase7-intro__copy"><p class="guide-kicker">INDEX / PROGRESSION</p><h2>Choisissez le mode avant le prochain raid</h2><p>Les tâches sont importées séparément pour PvP permanent, PvE Zone et PvP Seasonal; les listes et prérequis divergent.</p><p class="phase7-note">Comptage des snapshots : {esc(totals)}. Les noms français sont disponibles pour les tâches renvoyées par les trois réponses.</p></div>{img}</section>
<section class="guide-section phase7-section" id="quest-filter" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> Recherche</p><h2>Filtrer les tâches de l’export</h2><p>La recherche couvre le nom, le trader, la carte et l’identifiant. Les filtres ne font pas apparaître les tâches absentes de la source.</p></div><div class="phase7-filter-grid"><label class="field" for="quest-mode">Mode<select class="field__input" id="quest-mode" data-p7-mode><option value="regular">PvP permanent</option><option value="pve">PvE Zone</option><option value="pvp-season">PvP Seasonal</option></select></label><label class="field" for="quest-search">Nom, trader, carte ou ID<input class="field__input" id="quest-search" type="search" data-p7-quest-search placeholder="Ex. Customs, Prapor, Collector"></label><label class="field" for="quest-trader">Trader<select class="field__input" id="quest-trader" data-p7-quest-trader><option value="all">Tous les traders</option></select></label><label class="field" for="quest-map">Carte<select class="field__input" id="quest-map" data-p7-quest-map><option value="all">Toutes les cartes</option></select></label><label class="field" for="quest-level">Niveau minimum<select class="field__input" id="quest-level" data-p7-quest-level><option value="all">Tous</option><option value="1">Jusqu’au niveau 10</option><option value="10">10 et plus</option><option value="20">20 et plus</option><option value="30">30 et plus</option><option value="40">40 et plus</option></select></label><label class="field" for="quest-progress">Progression locale<select class="field__input" id="quest-progress" data-p7-quest-progress><option value="all">Toutes</option><option value="todo">À faire / en cours</option><option value="done">Terminées localement</option></select></label></div><div class="phase7-check-row"><label><input type="checkbox" data-p7-quest-kappa> Balise Kappa dans l’export</label><label><input type="checkbox" data-p7-quest-lightkeeper> Balise Lightkeeper dans l’export</label><button class="button button--quiet" type="button" data-p7-quest-reset>Effacer les filtres</button></div><p class="phase7-result-count" data-p7-quest-count aria-live="polite">Snapshot regular · 60 premières tâches affichées.</p><div class="phase7-table-wrap" role="region" aria-label="Tâches, défilement horizontal" tabindex="0"><table class="phase7-table phase7-table--quests"><caption>Tâches du snapshot regular · repli sans JavaScript : 60 premières entrées triées par niveau</caption><thead><tr><th scope="col">Tâche</th><th scope="col">Trader</th><th scope="col">Niveau</th><th scope="col">Carte(s)</th><th scope="col">Repères exportés</th><th scope="col">Progression</th></tr></thead><tbody data-p7-quest-list>{rows}</tbody></table></div><button class="button button--quiet" type="button" data-p7-quest-more hidden>Afficher davantage</button><p class="phase7-note">Les statuts sont enregistrés dans ce navigateur uniquement; ils ne synchronisent pas le profil EFT et ne confirment pas la disponibilité d’une tâche.</p><noscript><p class="phase7-note">JavaScript est désactivé : les 60 premières tâches restent consultables ci-dessus; les snapshots complets par mode sont liés dans la navigation latérale.</p></noscript></section>
<section class="guide-section phase7-section" id="quest-stats" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>02</span> Couverture</p><h2>Ce que l’export contient — et ne contient pas</h2><p>Le dépôt communautaire signale neuf tâches absentes, dont Getting Acquainted et huit tâches Make Amends. Elles restent introuvables dans les trois réponses contrôlées; l’état du client n’a pas été testé.</p></div><div class="phase7-stat-grid" data-p7-quest-stats>{_quest_stats_html(data)}</div><div class="phase7-callout"><strong>Une balise à zéro n’est pas une preuve d’absence.</strong><p>Le champ <code>lightkeeperRequired</code> vaut zéro dans les trois snapshots; certaines tâches peuvent ne pas être marquées ou listées. Confirmez le journal dans le jeu.</p></div></section>
<section class="guide-section phase7-section" id="progress-tools" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>03</span> Outils</p><h2>Arbre et fin de jeu</h2><p>Étudiez les liens connus ou comparez les conditions de Collector sans mélanger les sources.</p></div><div class="phase7-link-grid"><a class="phase7-link-card" href="{esc(root+'pages/quests/quest-tree.html')}"><strong>Arbre des quêtes</strong><span>Liens déclarés et suivi local.</span></a><a class="phase7-link-card" href="{esc(root+'pages/quests/kappa-guide.html')}"><strong>Guide Kappa / Collector</strong><span>Conditions divergentes et 44 objectifs FIR de l’export.</span></a></div></section>'''


def _quest_tree_content(data,root):
    mode=data['modes']['regular'];collector=next((task for task in mode['tasks'] if task['normalizedName']=='collector'),None)
    selected=collector['id'] if collector else ''
    options=''.join(f'<option value="{esc(task["id"])}"{" selected" if task["id"]==selected else ""}>{esc(task["nameFr"])} · niv. {esc(task.get("minPlayerLevel") if task.get("minPlayerLevel") is not None else "—")}</option>' for task in mode['tasks'])
    fallback=''
    if collector:
        reqs=''.join(f'<li>{esc(req.get("nameFr") or req["taskId"])} · statut exporté {esc(", ".join(req.get("status",[])) or "non renseigné")}</li>' for req in collector['taskRequirements'])
        fallback=f'<article class="phase7-tree-node"><h3>{esc(collector["nameFr"])}</h3><p>Prérequis directement listés par Tarkov.dev; la logique ET/OU n’est pas déduite.</p><ul>{reqs}</ul></article>'
    img=_item_figure('images/phase7/quest-dossier.jpg','Dossier de mission fictif accompagné d’une carte abstraite.','Les dépendances exportées ne valident pas les conditions du client.',root)
    return f'''<section class="phase7-intro" id="method" tabindex="-1"><div class="phase7-intro__copy"><p class="guide-kicker">OUTIL / PRÉREQUIS</p><h2>Une carte de liens connus, pas un déverrouillage garanti</h2><p>Chaque lien vient de <code>taskRequirements</code>. Plusieurs exigences ne prouvent pas qu’elles sont toutes simultanées : l’opérateur ET/OU n’est pas inféré.</p><p>Les cases sont locales à ce navigateur; elles ne mettent pas à jour votre compte.</p></div>{img}</section>
<section class="guide-section phase7-section" id="tree-tool" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> Explorateur</p><h2>Choisir une tâche et remonter ses prérequis</h2><p>Le panneau affiche les liens directs et les conditions de trader exportées.</p></div><div class="phase7-filter-grid"><label class="field" for="tree-mode">Mode<select class="field__input" id="tree-mode" data-p7-mode><option value="regular">PvP permanent</option><option value="pve">PvE Zone</option><option value="pvp-season">PvP Seasonal</option></select></label><label class="field" for="tree-trader">Trader<select class="field__input" id="tree-trader" data-p7-tree-trader><option value="all">Tous</option></select></label><label class="field" for="tree-search">Recherche<input class="field__input" id="tree-search" type="search" data-p7-tree-search placeholder="Nom de tâche ou de carte"></label><label class="field" for="tree-task">Tâche<select class="field__input" id="tree-task" data-p7-tree-task><option value="">Choisissez une tâche</option>{options}</select></label></div><div class="phase7-tree-panel" data-p7-tree-panel aria-live="polite">{fallback or '<p>Sélectionnez une tâche pour afficher ses prérequis.</p>'}</div><div class="phase7-tree-actions"><button class="button button--quiet" type="button" data-p7-tree-export>Exporter ma progression JSON</button><button class="button button--quiet" type="button" data-p7-tree-clear>Effacer mes statuts locaux</button><span class="phase7-result-count" data-p7-tree-count aria-live="polite">Snapshot regular · tâches chargées.</span></div><noscript><p class="phase7-note">Le panneau statique montre les liens directs de Collector. Le sélecteur et le suivi local demandent JavaScript.</p></noscript></section>
<section class="guide-section phase7-section" id="tree-state" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>02</span> Progression</p><h2>Cases locales et conditions réelles</h2><p>Les tâches cochées sont stockées par mode et n’envoient aucune donnée à un serveur.</p></div><div class="phase7-callout"><strong>Ne déduisez pas la disponibilité d’une seule arête.</strong><p>Depuis 1.1.0, la plupart des tâches secondaires sont distribuées par paliers de loyauté en petits groupes; les chaînes et conditions d’événement subsistent. Le graphe exporté n’est pas le journal du jeu.</p></div></section>'''


def _kappa_content(data,root):
    regular=data['modes']['regular'];collector=data['collectorByMode']['regular']
    objectives=collector['objectives'] if collector else []
    items=[]
    for index,obj in enumerate(objectives):
        item_id=(obj.get('itemIds') or [f'objective-{index+1}'])[0]
        name=(obj.get('itemNamesFr') or [obj.get('descriptionFr') or f'Objectif {index+1}'])[0]
        items.append(f'<label class="phase7-checkbox"><input type="checkbox" aria-label="Cocher {esc(name)} dans ma checklist locale"><span><strong>{esc(name)}</strong><small>{esc(obj.get("count") or 1)} × · {"FIR requis selon l’export" if obj.get("foundInRaid") else "FIR non marqué"} · ID {esc(item_id)}</small></span></label>')
    reqs=[]
    if collector:
        for req in collector['taskRequirements']:
            reqs.append(f'<div class="phase7-req-card"><strong>{esc(req.get("nameFr") or req["taskId"])}</strong><span>Tâche préalable · statut {esc(", ".join(req.get("status",[])) or "non renseigné")}</span></div>')
        for req in collector['traderRequirements']:
            if req.get('type')=='level' and req.get('value')==4:
                reqs.append(f'<div class="phase7-req-card"><strong>{esc(req.get("traderNameFr") or "Trader")}</strong><span>Loyauté ≥ {esc(req.get("value"))} · export</span></div>')
        for req in collector['traderRequirements']:
            if req.get('type')=='reputation':
                reqs.append(f'<div class="phase7-req-card"><strong>Fence · réputation</strong><span>{esc(req.get("compare") or "≥")} {esc(req.get("value"))} · export</span></div>')
    img=_item_figure('images/phase7/quest-dossier.jpg','Dossier de quête sur une table de planification fictive.','La checklist locale ne confirme ni l’accès ni la remise dans le client.',root)
    level=collector.get('minPlayerLevel') if collector else '—'
    pcount=len(collector.get('taskRequirements',[])) if collector else 0
    return f'''<section class="phase7-intro" id="method" tabindex="-1"><div class="phase7-intro__copy"><p class="guide-kicker">ENDGAME / COLLECTOR</p><h2>Préparez les conditions avant de garder des objets</h2><p>Dans le snapshot regular, Collector est indexée au niveau {esc(level)}, avec {pcount} prérequis de tâche, sept exigences de loyauté LL4, Fence réputation ≥ 3 et {len(objectives)} objectifs.</p><p>Fandom consulté indique niveau 40 et quatre prérequis; Tarkov.dev et Tarkov Advisor indiquent 42 et cinq. Aucune vérification en client n’a résolu le désaccord.</p></div>{img}</section>
<section class="guide-section phase7-section" id="requirements" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> Conditions</p><h2>Collector · exigences par snapshot</h2><p>Changez de mode pour relire ses propres données; ne fusionnez pas les listes.</p></div><div class="phase7-controls"><label class="field" for="kappa-mode">Mode<select class="field__input" id="kappa-mode" data-p7-mode><option value="regular">PvP permanent</option><option value="pve">PvE Zone</option><option value="pvp-season">PvP Seasonal</option></select></label></div><div class="phase7-kappa-summary" data-p7-kappa-summary><div class="phase7-stat-grid"><div class="phase7-stat"><strong>{esc(level)}</strong><span>Niveau minimum · export regular</span></div><div class="phase7-stat"><strong>{pcount}</strong><span>Tâches préalables listées</span></div><div class="phase7-stat"><strong>7</strong><span>Traders LL4 listés</span></div><div class="phase7-stat"><strong>{len(objectives)}</strong><span>Objectifs d’objets</span></div></div></div><div class="phase7-kappa-reqs" data-p7-kappa-reqs>{''.join(reqs)}</div><div class="phase7-callout phase7-callout--warning"><strong>Désaccord communautaire non résolu.</strong><p>Fandom : niveau 40 et quatre tâches (Chemical – Part 3, Sew it Good – Part 2, Shooter Born in Heaven, The Tarkov Shooter – Part 4). Tarkov.dev/Tarkov Advisor : niveau 42 et cinq, avec Postman Pat – Part 2. Confirmez dans le client.</p></div></section>
<section class="guide-section phase7-section" id="kappa-items" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>02</span> Collection</p><h2>Objets Found in Raid</h2><p>Liste du snapshot régularisé par mode; chaque objectif reste une ligne distincte. Confirmez le statut FIR et le compteur du client avant toute remise.</p></div><p class="phase7-result-count" data-p7-kappa-progress role="status">0 / {len(objectives)} cochés localement · regular</p><div class="phase7-kappa-toolbar"><label class="field" for="kappa-search">Filtrer un objet<input class="field__input" id="kappa-search" type="search" data-p7-kappa-search placeholder="Nom de l’objet"></label><button class="button button--quiet" type="button" data-p7-kappa-clear>Effacer ma checklist locale</button></div><div class="phase7-kappa-grid" data-p7-kappa-items>{''.join(items)}</div><p class="phase7-note">Les prix flea, spawns exacts et probabilités d’apparition ne sont pas fournis; ils changent selon le patch, la carte et le mode.</p></section>
<section class="guide-section phase7-section" id="kappa-method" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>03</span> Stratégie prudente</p><h2>Éviter les objets manquants et les mauvaises hypothèses</h2><p>Gardez les objets rares potentiellement requis jusqu’à ce que la tâche soit visible. Les valeurs FIR affichées sont des données communautaires, pas une vérification en jeu.</p></div><div class="phase7-step-grid"><article><span>01</span><h3>Verrouiller le mode</h3><p>Choisissez le profil concerné avant de suivre un prérequis.</p></article><article><span>02</span><h3>Valider les exigences</h3><p>Vérifiez niveau, Fence, sept traders et tâches préalables dans le journal.</p></article><article><span>03</span><h3>Cocher après extraction</h3><p>Confirmez le statut Found in Raid dans l’inventaire.</p></article></div></section>'''


def _static_hideout(stations,mode):
    station_parts=[]
    for station in stations:
        levels=[]
        for level in station['levels']:
            requirements=[]
            for index,item in enumerate(level['itemRequirements']):
                item_key=f'{mode}:{level.get("id") or station["id"]+"-"+str(level.get("level"))}:{item.get("itemId")}:{index}'
                badge=' · FIR export' if item.get('foundInRaid') else ''
                if item.get('tool'): badge+=' · outil'
                requirements.append(f'<label class="phase7-checkbox"><input type="checkbox"><span><strong>{esc(item.get("count") or 0)} × {esc(item["nameFr"])}</strong><small>{esc(item_key)}{esc(badge)}</small></span></label>')
            dependencies=[]
            for row in level['stationRequirements']: dependencies.append(f'<li>{esc(row.get("nameFr") or row.get("stationId"))} niveau {esc(row.get("level"))}</li>')
            for row in level['traderRequirements']: dependencies.append(f'<li>{esc(row.get("nameFr") or row.get("traderId"))} · niveau {esc(row.get("level"))} · réputation {esc(row.get("reputation"))}</li>')
            requirements_html=''.join(requirements) or '<p>Aucun matériau objet listé pour ce palier.</p>'
            dep_html=f'<p>Dépendances</p><ul>{"".join(dependencies)}</ul>' if dependencies else ''
            levels.append(f'<details class="phase7-level"><summary>Niveau {esc(level.get("level"))} · {esc(fmt_duration(level.get("constructionTime")))}</summary><div class="phase7-level__body"><div class="phase7-requirement-list"><strong>Matériaux ({len(level["itemRequirements"])})</strong>{requirements_html}</div>{dep_html}</div></details>')
        station_parts.append(f'<details class="phase7-station" data-station-id="{esc(station["id"])}"><summary><span>{esc(station["nameFr"])}</span><span class="phase7-station__meta">{len(station["levels"])} palier(s)</span></summary><div class="phase7-station__levels">{"".join(levels)}</div></details>')
    return ''.join(station_parts)


def _hideout_content(data,root):
    regular=data['modes']['regular']; m=regular['metrics']
    image=_item_figure('images/phase7/hideout-plan.jpg','Plan dessiné d’une planque modulaire fictive, sans mesures de jeu.','Schéma d’ambiance non à l’échelle; dépendances issues d’un export communautaire.',root)
    return f'''<section class="phase7-intro" id="method" tabindex="-1"><div class="phase7-intro__copy"><p class="guide-kicker">PLANQUE / CONSTRUCTION</p><h2>Choisissez le mode; suivez les dépendances</h2><p>Snapshot regular : {m['stations']} stations, {m['stationLevels']} paliers, {m['hideoutItemRequirementRows']} lignes de besoins, dont {m['hideoutFirRequirementRows']} marquées FIR dans l’export. PvE et Seasonal restent séparés.</p><p>BSG 1.1.0 indique des exigences simplifiées et le retrait de FIR pour certains besoins. La colonne exportée n’est pas une preuve du client.</p></div>{image}</section>
<section class="guide-section phase7-section" id="hideout-stations" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> Stations</p><h2>Stations, paliers et matériaux</h2><p>Dépliez un niveau pour voir matériaux, dépendances de station, traders et compétences. Les outils restent distingués des consommables.</p></div><div class="phase7-filter-grid"><label class="field" for="hideout-mode">Mode<select class="field__input" id="hideout-mode" data-p7-mode><option value="regular">PvP permanent</option><option value="pve">PvE Zone</option><option value="pvp-season">PvP Seasonal</option></select></label><label class="field" for="hideout-search">Station ou matériau<input class="field__input" id="hideout-search" type="search" data-p7-hideout-search placeholder="Ex. générateur, câble"></label><label class="field" for="hideout-fir">Found in Raid<select class="field__input" id="hideout-fir" data-p7-hideout-fir><option value="all">Toutes les exigences</option><option value="fir">FIR marqué par l’export</option><option value="not-fir">Sans FIR marqué</option></select></label><label class="field" for="hideout-level">Niveau station<select class="field__input" id="hideout-level" data-p7-hideout-level><option value="all">Tous</option><option value="1">Niveau 1</option><option value="2">Niveau 2</option><option value="3">Niveau 3</option><option value="4">Niveau 4 et plus</option></select></label><button class="button button--quiet" type="button" data-p7-hideout-clear>Effacer ma checklist locale</button></div><p class="phase7-result-count" data-p7-hideout-count aria-live="polite">26 stations · snapshot regular.</p><div class="phase7-station-grid" data-p7-hideout-stations>{_static_hideout(regular['stations'],'regular')}</div><noscript><p class="phase7-note">La liste regular reste consultable; le filtre de mode, les recherches et la sauvegarde locale demandent JavaScript.</p></noscript></section>
<section class="guide-section phase7-section" id="hideout-filter" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>02</span> Priorités et coûts</p><h2>Suivre une dépendance, pas un classement de rentabilité</h2><p>Priorisez une station si elle débloque une tâche, une autre station ou une recette dont vous avez besoin. Aucun prix live, taxe ou ROI fixe n’est publié ici.</p></div><div class="phase7-step-grid"><article><span>01</span><h3>Partir d’un objectif</h3><p>Repérez les paliers utiles et les matériaux FIR signalés par le flux.</p></article><article><span>02</span><h3>Comparer les ressources</h3><p>Considérez votre stash, le temps de jeu et les besoins de tâche; l’export n’est pas un prix.</p></article><article><span>03</span><h3>Vérifier le mode</h3><p>Les exigences PvP permanent, PvE et Seasonal ne doivent pas être fusionnées.</p></article></div><div class="phase7-callout"><strong>BSG 1.3.0.0 :</strong><p>La note annonce des personnalisations cosmétiques de planque; elle n’établit pas que les coûts de construction ou recettes ont été refaits.</p></div></section>
<section class="guide-section phase7-section" id="hideout-crafts-link" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>03</span> Production</p><h2>Comparer les recettes sans prix préremplis</h2><p>Saisissez vos propres valeurs dans l’atelier de recettes; aucun prix flea courant n’est fourni.</p></div><a class="button button--primary" href="{esc(root+'pages/hideout/crafting.html')}">Ouvrir Atelier & recettes <span aria-hidden="true">↗</span></a></section>'''


def _static_crafts(crafts):
    rows=[]
    for recipe in crafts:
        ingredients=''.join(f'<li>{esc(row.get("count") or 0)} × {esc(row["nameFr"])}{" · outil réutilisable" if row.get("tool") else " · consommable"}</li>' for row in recipe['ingredients']) or '<li>Aucun ingrédient listé.</li>'
        rows.append(f'<details><summary>{esc(recipe["output"]["nameFr"])} ×{esc(recipe["output"].get("count") or 1)} · {esc(recipe["stationNameFr"])} niveau {esc(recipe.get("level") or "—")} · {esc(fmt_duration(recipe.get("duration")))}</summary><ul>{ingredients}</ul></details>')
    return ''.join(rows)


def _crafting_content(data,root):
    regular=data['modes']['regular'];craft_count=regular['metrics']['crafts']
    image=_item_figure('images/phase7/hideout-crafting.jpg','Atelier improvisé dans une planque fictive, outils sous une lampe.','Aucun coût ou délai réel n’est encodé dans l’illustration.',root)
    return f'''<section class="phase7-intro" id="method" tabindex="-1"><div class="phase7-intro__copy"><p class="guide-kicker">OUTIL / PRODUCTION</p><h2>Calculez avec vos chiffres, pas avec un prix périmé</h2><p>L’export regular compte {craft_count} recettes; durée, déverrouillage et ingrédients sont propres au snapshot de chaque mode. Aucun cours flea ni barème de frais n’est inclus.</p><p>Les consommables sont additionnés au coût du lot; les outils requis sont listés à part. Le résultat n’est ni recommandation d’achat ni promesse de marge.</p></div>{image}</section>
<section class="guide-section phase7-section" id="craft-tool" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>01</span> Sélection</p><h2>Choisir une recette</h2><p>Filtrez par mode, station et objet; renseignez les prix unitaires en roubles pour estimer votre lot.</p></div><div class="phase7-filter-grid"><label class="field" for="craft-mode">Mode<select class="field__input" id="craft-mode" data-p7-mode><option value="regular">PvP permanent</option><option value="pve">PvE Zone</option><option value="pvp-season">PvP Seasonal</option></select></label><label class="field" for="craft-station">Station<select class="field__input" id="craft-station" data-p7-craft-station><option value="all">Toutes les stations</option></select></label><label class="field" for="craft-search">Recette ou objet<input class="field__input" id="craft-search" type="search" data-p7-craft-search placeholder="Nom de recette ou d’ingrédient"></label><label class="field" for="craft-sort">Trier<select class="field__input" id="craft-sort" data-p7-craft-sort><option value="station">Station puis durée</option><option value="duration">Durée croissante</option><option value="level">Niveau requis</option><option value="name">Nom du résultat</option></select></label><label class="field" for="craft-recipe">Recette<select class="field__input" id="craft-recipe" data-p7-craft-recipe><option value="">Choisissez une recette</option></select></label></div><p class="phase7-result-count" data-p7-craft-count aria-live="polite">{craft_count} recettes · regular.</p><div class="phase7-craft-detail" data-p7-craft-detail><p>Sélectionnez une recette avec JavaScript pour saisir vos prix et estimer le coût du lot.</p></div><details class="guide-disclosure" data-p7-static-fallback><summary>Catalogue statique de référence · PvP permanent · {craft_count} recettes</summary><div class="phase7-task-list">{_static_crafts(regular['crafts'])}</div></details><noscript><p class="phase7-note">Le catalogue regular ci-dessus reste consultable sans JavaScript. Le calculateur et les autres modes demandent JavaScript.</p></noscript></section>
<section class="guide-section phase7-section" id="craft-results" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>02</span> Calcul</p><h2>Coût, durée et marge manuelle</h2><p>Le coût additionne quantité × prix unitaire des consommables. La sortie et les frais sont saisis par vous; énergie, carburant, taxes non saisies, usure et risque de vente sont exclus.</p></div><div class="phase7-callout"><strong>Les temps de jeu peuvent différer.</strong><p>La durée provient du flux. Bonus de compétences, état de la planque et calendrier du mode peuvent modifier le temps observé; vérifiez le client.</p></div></section>
<section class="guide-section phase7-section" id="craft-method" tabindex="-1"><div class="guide-section__heading"><p class="guide-kicker"><span>03</span> Méthode</p><h2>Ce que le simulateur inclut</h2><p>Prix laissés vides par défaut; vos saisies sont locales à ce navigateur. Les outils réutilisables ne sont pas facturés comme consommables.</p></div><a class="button button--quiet" href="{esc(root+'pages/hideout/')}">Retour au guide Planque <span aria-hidden="true">↗</span></a></section>'''


def _render_page(page,data,base,patch,review_iso,review_long):
    root='../../'
    parent_route='pages/traders/' if page['kind'] in ('traders-index','trader-profile') else 'pages/quests/' if page['kind'] in ('quests-index','quest-tree','kappa-guide') else 'pages/hideout/'
    parent_name='Traders' if page['kind'] in ('traders-index','trader-profile') else 'Quêtes' if page['kind'] in ('quests-index','quest-tree','kappa-guide') else 'Planque'
    if page['kind']=='traders-index': content=_traders_index_content(data,root)
    elif page['kind']=='trader-profile': content=_profile_content(page,data,root)
    elif page['kind']=='quests-index': content=_quests_index_content(data,root)
    elif page['kind']=='quest-tree': content=_quest_tree_content(data,root)
    elif page['kind']=='kappa-guide': content=_kappa_content(data,root)
    elif page['kind']=='hideout-index': content=_hideout_content(data,root)
    elif page['kind']=='crafting': content=_crafting_content(data,root)
    else: raise ValueError('Type de page inconnu: '+page['kind'])
    if page['kind']=='trader-profile':
        source_key='fence-profile' if page['trader']=='fence' else 'lightkeeper-profile' if page['trader']=='lightkeeper' else 'ref-profile' if page['trader']=='ref' else 'trader-profile'
    else: source_key=page['sourcesKey']
    sources=_source_html(PAGE_SOURCES.get(source_key,[]))
    quick=''.join(f'<a href="#{esc(anchor)}"><span>{esc(title)}</span><small>{esc(label)}</small></a>' for anchor,title,label in page['quick'])
    nav=''.join(f'<li><a href="{esc(root+p["route"])}"{" aria-current=\"page\"" if p["file"]==page["file"] else ""}>{esc(p["label"])}</a></li>' for p in PAGES)
    canonical=canonical_link(base,page['route']); og_url=open_graph_url_meta(base,page['route'])
    schema={'@context':'https://schema.org','@type':'WebPage','name':page['title'],'inLanguage':'fr-FR','description':page['lead'],
            'dateModified':review_iso,'isPartOf':{'@type':'WebSite','name':'Tarkov Ultimate Guide'}}
    if seo_base_is_public(base): schema['url']=urljoin(base,page['route'])
    jsonld=json.dumps(schema,ensure_ascii=False,separators=(',',':')).replace('<',r'\u003c')
    hero_url=root+page['hero'];og_image=urljoin(base,page['hero'])
    return f'''<!doctype html>
<html lang="fr-FR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page['title'])} · Guide Tarkov | Tarkov Ultimate Guide</title><meta name="description" content="{esc(page['lead'])}"><meta name="theme-color" content="#111411">
<link rel="preload" href="{root}fonts/inter-400-700.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="{root}fonts/type.css"><link rel="stylesheet" href="{root}css/main.css"><link rel="stylesheet" href="{root}css/components.css"><link rel="stylesheet" href="{root}css/animations.css"><link rel="stylesheet" href="{root}css/responsive.css"><link rel="stylesheet" href="{root}css/pages/home.css"><link rel="stylesheet" href="{root}css/pages/guides.css"><link rel="stylesheet" href="{root}css/pages/phase6.css"><link rel="stylesheet" href="{root}css/pages/phase7.css">
{canonical}<meta property="og:title" content="{esc(page['title'])} · Tarkov Ultimate Guide"><meta property="og:description" content="{esc(page['lead'])}"><meta property="og:type" content="article">{og_url}<meta property="og:image" content="{esc(og_image)}"><script type="application/ld+json">{jsonld}</script><script src="{root}js/main.js" type="module"></script><script src="{root}js/phase7.js" type="module"></script></head>
<body class="home-page guide-page phase7-page" data-phase7-page="{esc(page['kind'])}" data-phase7-root="{root}" data-phase7-route="{esc(page['route'])}" data-phase7-review="{esc(review_iso)}" data-phase7-patch="{esc(patch)}"{f' data-phase7-trader="{esc(page["trader"])}"' if page.get('trader') else ''}>
<a class="skip-link" href="#main">Aller au contenu</a><header class="site-header home-header" data-site-header><div class="shell site-header__inner"><a class="brand" href="{root}"><span class="brand__mark" aria-hidden="true"></span><span><span class="brand__word">TARKOV</span><span class="brand__descriptor">Ultimate Guide</span></span><span class="sr-only">, accueil</span></a>
<nav class="site-nav" id="global-nav" aria-label="Navigation principale" data-site-nav><a class="site-nav__link" href="{root}">Accueil</a><a class="site-nav__link" href="{root}pages/maps/">Cartes</a><a class="site-nav__link" href="{root}pages/weapons/">Arsenal</a><a class="site-nav__link" href="{root}pages/ammo/">Munitions</a><a class="site-nav__link" href="{root}pages/armor/">Protection</a><a class="site-nav__link" href="{root}pages/bosses/">Bosses</a><details class="mega-menu home-mega" data-nav-disclosure><summary class="mega-menu__summary">Progression</summary><div class="mega-menu__panel home-mega__panel phase7-mega__panel"><div class="home-mega__group"><p class="eyebrow">Échanges</p><a class="mega-menu__item" href="{root}pages/traders/"><strong>Traders</strong><span>Profils et seuils par mode</span></a><a class="mega-menu__item" href="{root}pages/traders/ref.html"><strong>Ref</strong><span>Arena et Seasonal</span></a></div><div class="home-mega__group"><p class="eyebrow">Tâches</p><a class="mega-menu__item" href="{root}pages/quests/"><strong>Quêtes</strong><span>Recherche et suivi local</span></a><a class="mega-menu__item" href="{root}pages/quests/quest-tree.html"><strong>Arbre des quêtes</strong><span>Liens déclarés par l’export</span></a><a class="mega-menu__item" href="{root}pages/quests/kappa-guide.html"><strong>Kappa / Collector</strong><span>Conditions et objets FIR</span></a></div><div class="home-mega__group"><p class="eyebrow">Planque</p><a class="mega-menu__item" href="{root}pages/hideout/"><strong>Stations & matériaux</strong><span>Exigences par mode</span></a><a class="mega-menu__item" href="{root}pages/hideout/crafting.html"><strong>Atelier & recettes</strong><span>Coûts saisis manuellement</span></a></div></div></details></nav>
<div class="site-header__utilities"><a class="badge badge--live home-header__patch" href="{root}#etat-du-jeu" aria-label="Patch de référence {esc(patch)}">{esc(patch)}</a><button type="button" class="button button--quiet home-header__search" data-modal-open="site-search" data-site-search-trigger aria-label="Rechercher dans le guide" aria-haspopup="dialog" aria-controls="site-search" aria-keyshortcuts="Control+K Meta+K" hidden><i class="icon icon--search" aria-hidden="true"></i><span class="button__text">Rechercher</span><kbd class="search-key" data-keyhint="Ctrl K" aria-hidden="true"></kbd></button><button type="button" class="button button--icon" data-nav-toggle aria-label="Menu de navigation" aria-controls="global-nav" aria-expanded="false" hidden><i class="icon icon--menu" aria-hidden="true"></i></button></div></div></header>
<main id="main" tabindex="-1"><div class="guide-crumbbar"><div class="shell guide-crumbbar__inner"><nav class="breadcrumb" aria-label="Fil d’Ariane"><ol><li><a href="{root}">Accueil</a></li><li><a href="{root}{parent_route}">{esc(parent_name)}</a></li><li aria-current="page">{esc(page['label'])}</li></ol></nav><p class="guide-crumbbar__meta">Snapshot de référence du <time datetime="{esc(review_iso[:10])}">{esc(review_long)}</time></p></div></div>
<section class="guide-hero phase6-hero phase7-hero" id="top" tabindex="-1" aria-labelledby="phase7-h1" data-motion-hero><img class="guide-hero__image" src="{esc(hero_url)}" width="1376" height="768" alt="{esc(page['heroAlt'])}" fetchpriority="high" decoding="async"><div class="shell guide-hero__inner"><div class="guide-hero__copy"><p class="guide-kicker"><span>{esc(page['code'])}</span> PHASE_7 · {esc(page['label'])}</p><h1 id="phase7-h1">{esc(page['title'])}</h1><p class="guide-hero__lead">{esc(page['lead'])}</p><div class="guide-hero__actions"><a class="button button--primary" href="#{esc(page['quick'][0][0])}">{esc(page['quick'][0][2])} <span aria-hidden="true">↓</span></a><a class="button button--quiet" href="#{esc(page['quick'][-1][0])}">{esc(page['quick'][-1][2])} <span aria-hidden="true">↘</span></a></div><p class="guide-hero__note">Sources officielles et communautaires séparées · snapshots datés par mode · aucun prix live</p></div><p class="guide-hero__locator" aria-hidden="true">Illustration éditoriale locale · JPG</p></div></section>
<div class="guide-quick phase7-quick" role="group" aria-label="Accès rapide au dossier"><div class="shell guide-quick__inner">{quick}</div></div><div class="shell guide-layout phase6-layout phase7-layout"><aside class="guide-rail" aria-label="Navigation Progression"><p class="guide-rail__tag">PHASE_7 / Dossiers</p><h2>Explorer</h2><nav aria-label="Pages Traders, Quêtes et Planque"><ol>{nav}</ol></nav><div class="guide-rail__foot"><span>Snapshot de référence</span><a href="{root}data/snapshots/phase-7-regular-{DATE}.json">regular · {DATE} <span aria-hidden="true">↗</span></a></div></aside><article class="guide-content phase6-content phase7-content" aria-label="{esc(page['title'])}">{content}<section class="guide-section guide-sources phase6-sources phase7-sources" id="sources" tabindex="-1" aria-labelledby="phase7-sources-title"><div class="guide-section__heading"><p class="guide-kicker"><span>REF</span> Sources</p><h2 id="phase7-sources-title">Sources et limites</h2><p>BSG, exports communautaires et outils restent distingués. Référence {DATE}; prix, disponibilité de quête, spawns et progression de compte non testés dans le client.</p></div><ul class="guide-sources__items phase6-sources__items">{sources}</ul></section><div class="guide-next phase6-next"><div><p class="guide-kicker">À lire ensuite</p><h2>Continuer dans {esc(parent_name)}</h2><p>Ouvrir une autre fiche et garder le même mode de référence.</p></div><a class="button button--quiet" href="{root}{parent_route}">Revenir au dossier <span aria-hidden="true">↗</span></a></div></article></div></main>
<footer class="home-footer guide-footer"><div class="shell guide-footer__inner"><div><a class="brand" href="{root}"><span class="brand__mark" aria-hidden="true"></span><span><span class="brand__word">TARKOV</span><span class="brand__descriptor">Ultimate Guide</span></span><span class="sr-only">, accueil</span></a><p>Fan-site francophone indépendant de Battlestate Games. Illustrations originales générées; elles ne sont ni captures ni portraits officiels.</p></div><div class="guide-footer__controls"><a href="{root}">Retour à l’accueil <span aria-hidden="true">↗</span></a><div class="home-footer__settings"><button type="button" class="button button--quiet button--xs" data-contrast-toggle aria-pressed="false" hidden>Contraste renforcé</button><button type="button" class="button button--quiet button--xs" data-motion-toggle aria-pressed="false" hidden>Réduire les animations</button></div></div></div></footer><a class="button button--icon back-top" data-back-top href="#top" aria-label="Retour rapide en haut" hidden></a>
<dialog id="site-search" class="dialog home-search" data-modal data-site-search data-search-base="{root}" data-search-source="{root}js/data/search-index.json" aria-labelledby="search-title"><header class="dialog__head"><div><p class="eyebrow">Index du guide</p><h2 class="dialog__title" id="search-title">Rechercher dans Tarkov Ultimate Guide</h2></div><button type="button" class="button button--icon" data-modal-close aria-label="Fermer la recherche"><i class="icon icon--close" aria-hidden="true"></i></button></header><div class="dialog__body"><label for="site-query" class="field">Sujet, équipement ou quête<span class="field__wrap"><i class="icon icon--search" aria-hidden="true"></i><input class="field__input field__input--search" id="site-query" type="search" placeholder="Ex. Collector, Prapor, planque" autocomplete="off" data-modal-initial data-search-input></span></label><p class="dialog__hint search-status" role="status" data-search-status></p><ul class="search-results" data-search-results aria-label="Résultats de recherche"></ul><p class="search-dialog__foot"><span><kbd>↑</kbd> <kbd>↓</kbd> Parcourir</span><span><kbd>Entrée</kbd> Ouvrir</span><span>Échap Fermer</span></p></div></dialog></body></html>'''


def _search_records(data):
    records=[]
    for page in PAGES:
        records.append({'title':page['title'],'href':page['route'],'tag':'PHASE_7 · '+page['label'],'summary':page['lead'],'keywords':[page['kind'],page.get('trader',''),page['label']]})
    seen_tasks=set()
    for mode in MODES:
        for task in data['modes'][mode]['tasks']:
            if task['id'] in seen_tasks: continue
            seen_tasks.add(task['id'])
            modes=[MODES[m] for m in MODES if any(row['id']==task['id'] for row in data['modes'][m]['tasks'])]
            records.append({'title':task['nameFr'],'href':f'pages/quests/?mode={mode}&task={task["id"]}','tag':'Quête · '+(task.get('traderNameFr') or 'Inconnu'),
                'summary':'Mode(s) : '+', '.join(modes)+' · niveau exporté '+str(task.get('minPlayerLevel') or '—'),
                'keywords':[task['nameEn'],task.get('traderNameFr') or '',*task.get('mapNames',[]),'Kappa' if task.get('kappaRequired') else '']})
    for station in data['modes']['regular']['stations']:
        records.append({'title':station['nameFr'],'href':'pages/hideout/?mode=regular&station='+station['id'],'tag':'Planque · station',
            'summary':f'{len(station["levels"])} palier(s), exigences du snapshot','keywords':[station['nameEn'],station.get('normalizedName',''),'matériaux','Hideout']})
    seen_recipes=set()
    for mode in MODES:
        for recipe in data['modes'][mode]['crafts']:
            if recipe['id'] in seen_recipes: continue
            seen_recipes.add(recipe['id'])
            records.append({'title':recipe['output']['nameFr'],'href':f'pages/hideout/crafting.html?mode={mode}&recipe={recipe["id"]}',
                'tag':'Recette · '+recipe['stationNameFr'],'summary':f'Sortie ×{recipe["output"].get("count") or 1}; mode {MODES[mode]}; niveau de station {recipe.get("level") or "—"}',
                'keywords':[recipe['output']['nameEn'],recipe['stationNameEn'],*[row['nameFr'] for row in recipe['ingredients'][:4]]]})
    return records


def build_phase7(base,patch,read,compact):
    data=build_data(); _load_snapshots()
    # La date éditoriale est la date de référence locale; l’instant UTC réel est conservé dans le manifeste.
    review_dt=datetime.fromisoformat(DATE).replace(tzinfo=ZoneInfo('Europe/Paris'))
    months='janvier février mars avril mai juin juillet août septembre octobre novembre décembre'.split()
    review_iso=review_dt.isoformat(timespec='seconds');review_long=f'{review_dt.day} {months[review_dt.month-1]} {review_dt.year}'
    output={'js/data/phase7.json':json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n'}
    for page in PAGES:
        output[page['file']]=_render_page(page,data,base,patch,review_iso,review_long)
    return output,_search_records(data),review_dt


def build_local():
    data=build_data();patch=read_json('data/home.json')['patch']['reference']
    def read(path): return (ROOT/path).read_text(encoding='utf-8')
    def compact(value): return json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('<',r'\u003c')
    output,_,_=build_phase7('https://example.com/',patch,read,compact)
    for name,content in output.items():
        target=ROOT/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(content,encoding='utf-8')
    print('PHASE_7 générée. Pour actualiser recherche et sitemap locaux, lancer scripts/build_home.py avec une base d’aperçu.')
    return data


def fetch_command():
    snapshots,comparison=collect_snapshots()
    for mode,snapshot in snapshots.items():
        path=_snapshot_path(mode);write_json(path,snapshot)
        print(f"Écrit {path} · {snapshot['metrics']['tasks']} tâches, {snapshot['metrics']['stations']} stations, {snapshot['metrics']['crafts']} recettes")
    manifest={'schemaVersion':1,'snapshotDateReference':DATE,'collectedAtUtc':next(iter(snapshots.values()))['collectedAtUtc'],
        'publisher':'Tarkov.dev / the-hideout/tarkov-data-manager',
        'modes':{mode:{'path':_snapshot_path(mode),'metrics':snapshots[mode]['metrics'],'upstream':snapshots[mode]['upstream']} for mode in MODES},
        'comparison':comparison,'issue886':{'url':'https://github.com/the-hideout/tarkov-data-manager/issues/886','statusObserved':'OPEN','missingIds':MISSING_ISSUE_IDS}}
    write_json(f'data/snapshots/phase-7-manifest-{DATE}.json',manifest);sync_sources()
    return snapshots,manifest


def check_phase7():
    snapshots=_load_snapshots();data=build_data();errors=[]
    if len(PAGES)!=16 or len({page['file'] for page in PAGES})!=16: errors.append('16 routes uniques attendues')
    if sum(page['kind']=='trader-profile' for page in PAGES)!=10: errors.append('10 fiches traders attendues')
    manifest_path=ROOT/f'data/snapshots/phase-7-manifest-{DATE}.json'
    if not manifest_path.is_file(): errors.append('manifeste multi-mode absent')
    else:
        manifest=read_json(f'data/snapshots/phase-7-manifest-{DATE}.json')
        for mode in MODES:
            upstream=manifest.get('modes',{}).get(mode,{}).get('upstream',{})
            if len(upstream)!=len(ENDPOINTS): errors.append(f'{mode}: {len(upstream)}/{len(ENDPOINTS)} endpoints dans le manifeste')
            if any(row.get('httpStatus')!=200 for row in upstream.values()): errors.append(f'{mode}: endpoint non-200 dans le manifeste')
    for mode,snapshot in snapshots.items():
        if snapshot.get('mode')!=mode or snapshot.get('snapshotDateReference')!=DATE: errors.append(f'{mode}: mode ou date du snapshot incorrect')
        if snapshot['metrics']['taskNamesMissingFrench']: errors.append(f'{mode}: noms français manquants')
        if snapshot['metrics']['missingTaskReferences']: errors.append(f'{mode}: prérequis absents des tâches exportées')
        audit=data['modes'][mode]['dependencyAudit']
        if audit['cycleCount']: errors.append(f'{mode}: {audit["cycleCount"]} cycle(s) dans les prérequis')
    collector=data['collectorByMode']['regular']
    if not collector or len(collector['objectives'])!=44 or sum(bool(row.get('foundInRaid')) for row in collector['objectives'])!=44:
        errors.append('Collector regular: 44 objectifs FIR attendus dans ce snapshot')
    for page in PAGES:
        if not (ROOT/page['file']).is_file(): errors.append('route absente: '+page['file'])
        for image in (page['hero'],page['secondary']):
            if not (ROOT/image).is_file(): errors.append('image absente: '+image)
    if not (ROOT/'css/pages/phase7.css').is_file(): errors.append('CSS PHASE_7 absent')
    if not (ROOT/'js/phase7.js').is_file(): errors.append('JavaScript PHASE_7 absent')
    if errors:
        print('\n'.join(errors),file=sys.stderr);return 1
    total=len(set().union(*({task['id'] for task in snapshots[mode]['tasks']} for mode in MODES)))
    print(f'PHASE_7 sources OK · 16 routes · 3 snapshots séparés · union {total} tâches · {len(data["modes"]["regular"]["stations"])} stations')
    return 0


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch',action='store_true',help='collecter et archiver les 11 endpoints pour chaque mode')
    parser.add_argument('--build',action='store_true',help='générer les 16 routes PHASE_7 et js/data/phase7.json')
    parser.add_argument('--check',action='store_true',help='valider snapshots, manifeste, routes et images sans écrire')
    args=parser.parse_args()
    if args.fetch: fetch_command()
    if args.build: build_local()
    if args.check: return check_phase7()
    if not (args.fetch or args.build or args.check): parser.print_help()
    return 0

if __name__=='__main__':
    raise SystemExit(main())
