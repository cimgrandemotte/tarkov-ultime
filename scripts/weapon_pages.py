#!/usr/bin/env python3
"""Génère les 13 routes PHASE_5 depuis les exports et snapshots locaux datés."""
from __future__ import annotations
from datetime import datetime, timezone
from html import escape
from pathlib import PurePosixPath
from urllib.parse import urljoin
from zoneinfo import ZoneInfo
import json
import math
import re

from pathlib import Path
from site_urls import seo_base_is_public, canonical_link, open_graph_url_meta
ROOT = Path(__file__).resolve().parents[1]
DATA = 'data/phase5.json'
TEMPLATE = 'templates/phase5.html.in'
MODES = {
    'regular': 'PvP permanent',
    'pve': 'PvE Zone',
    'pvp-season': 'PvP saisonnier',
}
GROUP_LABELS = {
    'assault-rifles': 'Fusils d’assaut et carabines', 'smgs': 'Pistolets-mitrailleurs (SMG)',
    'shotguns': 'Fusils à pompe', 'sniper-rifles': 'Fusils de précision', 'dmrs': 'Fusils DMR',
    'lmgs': 'Mitrailleuses légères', 'pistols': 'Pistolets et revolvers', 'melee': 'Armes de mêlée',
    'grenade-launchers': 'Lanceurs, roquettes et signaux',
}
GROUP_SHORT = {
    'assault-rifles': 'Fusil / carabine', 'smgs': 'SMG', 'shotguns': 'Fusil à pompe',
    'sniper-rifles': 'Fusil précision', 'dmrs': 'DMR', 'lmgs': 'Mitrailleuse',
    'pistols': 'Pistolet / revolver', 'melee': 'Mêlée', 'grenade-launchers': 'Lanceur / signal',
}
CALIBERS = {
    'Caliber556x45NATO': '5,56 × 45 NATO', 'Caliber545x39': '5,45 × 39',
    'Caliber762x39': '7,62 × 39', 'Caliber762x51': '7,62 × 51 NATO',
    'Caliber762x54R': '7,62 × 54 R', 'Caliber762x25TT': '7,62 × 25 TT',
    'Caliber9x18PM': '9 × 18 Makarov', 'Caliber9x18PMM': '9 × 18 PMM',
    'Caliber9x19PARA': '9 × 19 Parabellum', 'Caliber9x21': '9 × 21',
    'Caliber9x39': '9 × 39', 'Caliber9x33R': '.357 Magnum / 9 × 33 R',
    'Caliber1143x23ACP': '.45 ACP', 'Caliber366TKM': '.366 TKM',
    'Caliber12g': '12 gauge', 'Caliber20g': '20 gauge', 'Caliber20x1mm': '20 × 1 mm',
    'Caliber23x75': '23 × 75 mm', 'Caliber26x75': '26 × 75 mm',
    'Caliber40mmRU': '40 mm (RU)', 'Caliber40x46': '40 × 46 mm',
    'Caliber46x30': '4,6 × 30 HK', 'Caliber57x28': '5,7 × 28 FN',
    'Caliber58x42': '5,8 × 42', 'Caliber68x51': '6,8 × 51',
    'Caliber762x35': '7,62 × 35 / .300 BLK', 'Caliber784x49': '7,84 × 49',
    'Caliber86x70': '.338 Lapua Magnum / 8,6 × 70', 'Caliber93x64': '9,3 × 64',
    'Caliber127x33': '.50 AE / 12,7 × 33', 'Caliber127x55': '12,7 × 55',
    'Caliber127x99': '.50 BMG / 12,7 × 99', 'Caliber725': '72,5 mm (roquette)',
}
AMMO_TYPES = {'bullet': 'Balle', 'buckshot': 'Chevrotine / projectile de fusil', 'grenade': 'Grenade', 'flashbang': 'Flash'}
TRADER_LABELS = {
    'prapor': 'Prapor', 'therapist': 'Therapist', 'fence': 'Fence', 'skier': 'Skier',
    'peacekeeper': 'Peacekeeper', 'mechanic': 'Mechanic', 'ragman': 'Ragman', 'jaeger': 'Jaeger',
    'lightkeeper': 'Lightkeeper', 'ref': 'Ref', 'btr-driver': 'Conducteur du BTR',
    'taran': 'Taran', 'radio-station': 'Radio Station', 'mr-kerman': 'Mr. Kerman',
    'voevoda': 'Voevoda', 'survivor': 'Survivor',
}
SLOT_LABELS = {
    'mod_pistol_grip': 'Poignée pistolet', 'mod_pistolgrip': 'Poignée pistolet',
    'mod_magazine': 'Chargeur', 'mod_reciever': 'Boîtier', 'mod_stock': 'Crosse',
    'mod_charge': 'Culasse', 'mod_barrel': 'Canon', 'mod_muzzle': 'Bouche / frein',
    'mod_sight_rear': 'Hausse', 'mod_sight_front': 'Guidon', 'mod_handguard': 'Garde-main',
    'mod_mount': 'Montage', 'mod_mount_000': 'Montage', 'mod_mount_001': 'Montage secondaire',
    'mod_mount_002': 'Montage secondaire', 'mod_mount_004': 'Montage secondaire',
    'mod_scope': 'Optique', 'mod_gas_block': 'Bloc de gaz', 'mod_launcher': 'Lanceur sous-canon',
    'mod_tactical': 'Dispositif tactique', 'mod_tactical_000': 'Dispositif tactique',
    'mod_tactical_001': 'Dispositif tactique', 'mod_tactical_002': 'Dispositif tactique',
    'mod_foregrip': 'Poignée avant', 'mod_bipod': 'Bipied', 'mod_trigger': 'Détente',
    'mod_hammer': 'Chien', 'mod_catch': 'Arrêtoir', 'mod_pistol_grip_akms': 'Poignée AKMS',
    'mod_stock_akms': 'Crosse AKMS', 'mod_stock_000': 'Crosse', 'mod_stock_001': 'Crosse',
    'mod_charge_001': 'Culasse', 'mod_pistolgrip_000': 'Poignée pistolet', 'mod_muzzle_000': 'Bouche / frein',
}
SOURCE_LABELS = {
    'primaire': 'Source officielle BSG', 'wiki': 'Wiki communautaire',
    'donnees_communautaires': 'Export communautaire', 'outil_communautaire': 'Outil communautaire',
    'communaute': 'Guide communautaire commercial', 'forum': 'Discussion communautaire',
    'video': 'Vidéo communautaire', 'presse': 'Presse / guide tiers',
}

def read(path: str):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def esc(value):
    return escape(str(value if value is not None else ''), quote=True)

def fmt_num(value, digits=2):
    if value is None or value == '': return '—'
    if isinstance(value, bool): return 'Oui' if value else 'Non'
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value): return '—'
        if float(value).is_integer(): return f'{int(value):,}'.replace(',', '\u202f')
        return f'{value:,.{digits}f}'.replace(',', '\u202f').replace('.', ',')
    return str(value)

def js_json(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')).replace('<', r'\u003c').replace('>', r'\u003e').replace('&', r'\u0026')

def date_fr(value):
    months = 'janvier février mars avril mai juin juillet août septembre octobre novembre décembre'.split()
    return f'{value.day} {months[value.month - 1]} {value.year}'

def time_fr(value):
    local = value.astimezone(ZoneInfo('Europe/Paris'))
    return f'{date_fr(local)} à {local.hour:02d} h {local.minute:02d} (Paris)'

def root_for(file):
    return '../' * (len(PurePosixPath(file).parts) - 1)

def ref(key, label='Source'):
    return f'<span class="guide-cite"><a href="#ref-{esc(key)}" aria-label="Référence : {esc(label)}">{esc(label)}</a></span>'

def citation_label(key):
    labels = {
        'tdev-phase5-catalog': 'Tarkov.dev · catalogue', 'tdev-phase5-crafts': 'Tarkov.dev · crafts',
        'tdev-phase5-traders': 'Tarkov.dev · marchands', 'tdev-drip-out-bear': 'Tarkov.dev · Drip-Out Bear',
        'tdev-drip-out-usec': 'Tarkov.dev · Drip-Out USEC', 'tdev-special-equipment': 'Tarkov.dev · tâche',
        'bsg-balance-nov': 'BSG · 12 novembre', 'wiki-ammo-2026': 'TarkovWiki · munitions',
        'wiki-m855a1-2026': 'TarkovWiki · M855A1', 'lfcarry-ammo-2026': 'LFCarry · guide tiers',
        'ascheron-ammo-2026': 'Ascheron · graphique', 'patch110': 'BSG · 1.1.0.0',
        'patch120': 'BSG · 1.2.0.0', 'patch130': 'BSG · 1.3.0.0',
    }
    return labels.get(key, key)

def source_list(keys, sources):
    rows=[]
    for key in keys:
        item=sources[key]
        label=SOURCE_LABELS.get(item.get('type'), 'Source consultée')
        rows.append(
            f'<li id="ref-{esc(key)}" class="phase5-source-card" tabindex="-1">'
            f'<span class="guide-source__type">{esc(label)}</span>'
            f'<a href="{esc(item["url"])}">{esc(item["titre"])} <span aria-hidden="true">↗</span></a>'
            f'<p>{esc(item["usage"])}</p></li>')
    return '\n'.join(rows)

def group_label(group):
    return GROUP_LABELS.get(group, group or 'Non classé')

def caliber_label(value):
    return CALIBERS.get(value, value if value else '—')

def trader_name(identifier, snapshot_mode):
    row=(snapshot_mode or {}).get(identifier, {})
    normalized=row.get('normalizedName', '')
    return TRADER_LABELS.get(normalized, normalized.replace('-', ' ').title() if normalized else 'Trader non résolu')

def prepare_crafts(crafts_snapshot, item_map, hideout_snapshot, quest_names=None):
    stations={}
    for ident, area in hideout_snapshot.get('data', {}).items():
        name=area.get('normalizedName') or area.get('name') or ident
        stations[ident]=name.replace('-', ' ').title()
    stations.setdefault('5d484fda654e7600681d9315', 'Workbench')
    quest_names=quest_names or {}
    by_mode={}
    for mode, bundle in crafts_snapshot['modes'].items():
        recipes={}
        for row in bundle['records']:
            product=row.get('productItem') or {}
            product_id=product.get('item')
            if not product_id: continue
            inputs=[]
            for required in row.get('requiredItems') or []:
                item=item_map.get(required.get('item'), {})
                inputs.append({
                    'name': item.get('nameFr') or item.get('nameEn') or required.get('item'),
                    'count': required.get('count'), 'tool': bool((required.get('attributes') or {}).get('tool')),
                })
            station_id=row.get('station')
            duration=int(row.get('duration') or 0)
            h, rem=divmod(duration, 3600); minutes=rem//60
            duration_label=(f'{h} h {minutes:02d}' if h else f'{minutes} min')
            task_id=row.get('taskUnlock')
            recipes.setdefault(product_id, []).append({
                'count': product.get('count'), 'station': stations.get(station_id, 'Station non résolue'),
                'stationId': station_id, 'level': row.get('level'), 'duration': duration,
                'durationLabel': duration_label, 'taskUnlock': task_id,
                'task': quest_names.get(task_id),
                'requiredItems': inputs, 'requiredQuestItems': row.get('requiredQuestItems') or [],
            })
        by_mode[mode]=recipes
    return by_mode

def flea_data(item, collected_at, threshold_days):
    flea=item.get('flea') or {}
    scan=flea.get('lastScan')
    price=flea.get('lastLowPrice')
    if not scan:
        label='Aucun horodatage flea · prix non exploitable'
        age=None
    else:
        parsed=datetime.fromisoformat(scan.replace('Z','+00:00'))
        age=(collected_at-parsed).total_seconds()/86400
        if age < 0:
            label='Horodatage postérieur à la collecte · valeur non affichée'
        elif age > threshold_days:
            label=f'Dernier scan il y a {fmt_num(age,1)} j · seuil éditorial {threshold_days} j dépassé'
        elif price is None:
            label=f'Scan il y a {fmt_num(age,1)} j · prix absent dans le champ lastLowPrice'
        else:
            label=f'Dernier bas exporté {fmt_num(price)} ₽ · scan il y a {fmt_num(age,1)} j'
    usable=bool(scan and price is not None and age is not None and 0 <= age <= threshold_days)
    return {'lastScan':scan,'ageDays':age,'price':price,'priceFresh':usable,'label':label}

def mode_values(item_by_mode, id_, collected_at, threshold_days, trader_snapshots, recipe_modes=None):
    result={}
    for mode in MODES:
        item=item_by_mode.get(mode, {}).get(id_, {})
        trader_map=trader_snapshots.get(mode, {})
        offers=[]
        for offer in item.get('buyFromTrader') or []:
            offers.append({
                'trader': trader_name(offer.get('trader'), trader_map),
                'level': offer.get('minTraderLevel'), 'price': offer.get('price'),
                'currency': offer.get('currency'), 'priceRUB': offer.get('priceRUB'),
                'taskUnlock': offer.get('taskUnlock'), 'buyLimit': offer.get('buyLimit'),
            })
        offers.sort(key=lambda row: (row.get('priceRUB') if isinstance(row.get('priceRUB'), (int,float)) else float('inf'), row['trader']))
        result[mode]={
            'offers':offers,
            'flea':flea_data(item, collected_at, threshold_days),
            'recipes':(recipe_modes or {}).get(mode, {}).get(id_, []),
        }
    return result

def render_offers(data):
    offers=data.get('offers') or []
    if not offers:
        return '<span class="phase5-value-muted">Aucune offre renseignée dans buyFromTrader pour cet export.</span>'
    summary=f'{len(offers)} offre(s) rapportée(s)'
    body=[]
    for offer in offers:
        level='niveau non précisé' if offer.get('level') is None else f'LL {esc(offer["level"])}'
        price='prix non renseigné' if offer.get('price') is None else f'{fmt_num(offer.get("price"))} {esc(offer.get("currency") or "")}'.strip()
        extra=[]
        if offer.get('buyLimit') is not None: extra.append(f'limite exportée : {fmt_num(offer["buyLimit"])}')
        if offer.get('taskUnlock'): extra.append('un déblocage de tâche est indiqué; son nom n’est pas résolu ici')
        body.append(f'<li><strong>{esc(offer.get("trader"))}</strong> · {level} · {price}' + (f' · {esc("; ".join(extra))}' if extra else '') + '</li>')
    return '<details class="phase5-disclosure"><summary>' + esc(summary) + '</summary><div class="phase5-disclosure__body"><ul>' + ''.join(body) + '</ul><p>Snapshot de l’export choisi; à vérifier dans l’interface du marchand.</p></div></details>'

def render_crafts(data):
    recipes=data.get('recipes') or []
    if not recipes:
        return '<span class="phase5-value-muted">Aucune recette liée à cet identifiant dans le snapshot.</span>'
    details=[]
    for rec in recipes:
        summary=f'{fmt_num(rec.get("count"))} produit(s) · {rec.get("station", "Station non résolue")}'
        if rec.get('level') is not None: summary += f' {rec["level"]}'
        if rec.get('durationLabel'): summary += f' · {rec["durationLabel"]}'
        required=[]
        for item in rec.get('requiredItems') or []:
            marker=' (outil indiqué)' if item.get('tool') else ''
            required.append(f'<li>{fmt_num(item.get("count"))} × {esc(item.get("name"))}{marker}</li>')
        quest='; objets de quête requis mentionnés' if rec.get('requiredQuestItems') else ''
        task=rec.get('task') or {}
        if rec.get('taskUnlock') and task.get('name'):
            faction=f' · variante {task["faction"]}' if task.get('faction') else ''
            unlock=f'; tâche associée : {task["name"]}{faction} (ID {rec["taskUnlock"]})'
        elif rec.get('taskUnlock'):
            unlock=f'; ID de déblocage non résolu : {rec["taskUnlock"]}'
        else:
            unlock='; aucun déblocage de tâche indiqué'
        details.append('<details class="phase5-disclosure"><summary>' + esc(summary) + '</summary><div class="phase5-disclosure__body"><p>Ingrédients du snapshot :</p><ul>' + ''.join(required or ['<li>Ingrédients non détaillés dans cet enregistrement</li>']) + '</ul><p>Le tag d’outil, l’identifiant de déblocage et la durée sont des champs d’export, pas un contrôle du client.' + esc(quest+unlock) + '</p></div></details>')
    return ''.join(details)

def metric_for_weapon(weapon, item_map):
    stats=weapon.get('stats') or {}
    preset_id=stats.get('defaultPreset')
    preset=item_map.get(preset_id) if preset_id else None
    allowed=stats.get('allowedAmmo') or []
    return {
        'family':group_label(weapon.get('group')),
        'caliber':caliber_label(stats.get('caliber')),
        'fireRate':stats.get('fireRate'), 'ergonomics':stats.get('ergonomics'),
        'recoilVertical':stats.get('recoilVertical'), 'recoilHorizontal':stats.get('recoilHorizontal'),
        'weight':weapon.get('weight'),
        'preset':(preset.get('nameFr') or preset.get('nameEn')) if preset else ('Référence présente; objet non résolu' if preset_id else None),
        'presetWeight':preset.get('weight') if preset else None,
        'allowedAmmoCount':len(allowed),
        'slashDamage':stats.get('slashDamage'), 'stabDamage':stats.get('stabDamage'),
        'signalDevice':bool(weapon.get('signalDevice')),
    }

def metric_for_ammo(ammo):
    stats=ammo.get('stats') or {}
    return {
        'caliber':caliber_label(stats.get('caliber')), 'ammoType':AMMO_TYPES.get(stats.get('ammoType'),stats.get('ammoType') or 'Non renseigné'),
        'damage':stats.get('damage'), 'penetrationPower':stats.get('penetrationPower'),
        'armorDamage':stats.get('armorDamage'), 'fragmentationChance':stats.get('fragmentationChance'),
        'initialSpeed':stats.get('initialSpeed'), 'projectileCount':stats.get('projectileCount'),
    }

def weapon_search(weapon, metrics, ammo_name_map):
    stats=weapon.get('stats') or {}
    compatible=' '.join(ammo_name_map.get(x,'') for x in stats.get('allowedAmmo') or [])
    return ' '.join(str(x or '') for x in [weapon.get('nameFr'),weapon.get('nameEn'),weapon.get('shortNameFr'),weapon.get('shortNameEn'),weapon.get('category'),weapon.get('group'),metrics['caliber'],compatible])

def ammo_search(ammo, metrics):
    return ' '.join(str(x or '') for x in [ammo.get('nameFr'),ammo.get('nameEn'),ammo.get('shortNameFr'),ammo.get('shortNameEn'),metrics['caliber'],metrics['ammoType']])

def table_mode_cell(field, values, mode='regular'):
    mode_data=values.get(mode,{})
    if field=='offers': return f'<td data-mode-field="offers">{render_offers(mode_data)}</td>'
    if field=='flea': return f'<td data-mode-field="flea">{esc(flea_data_label(mode_data))}</td>'
    if field=='craft': return f'<td data-mode-field="craft">{render_crafts(mode_data)}</td>'
    return '<td>—</td>'

def flea_data_label(mode_data):
    return (mode_data.get('flea') or {}).get('label','Pas de relevé exploitable dans cet export')

def mode_attr(values):
    return esc(js_json(values))

def object_image_markup(item_id, label, item_map):
    item=item_map.get(item_id)
    if not item:
        raise ValueError(f'Objet de catalogue sans enregistrement résolu : {item_id}')

    category=(item.get('category') or '').lower()
    art_by_category={
        'ammo':'ammo/ammo-chart-detail-640.jpg',
        'ammo-container':'ammo/ammo-catalogue-tray.jpg',
        'assault-rifle':'weapons/assault-rifles-detail.jpg',
        'assault-carbine':'weapons/assault-rifles-detail.jpg',
        'smg':'weapons/smg-detail.jpg',
        'shotgun':'weapons/shotguns-detail.jpg',
        'marksman-rifle':'weapons/dmr-field-rifle.jpg',
        'sniper-rifle':'weapons/precision-detail.jpg',
        'machinegun':'weapons/lmg-detail.jpg',
        'handgun':'weapons/pistols-detail.jpg',
        'revolver':'weapons/pistols-detail.jpg',
        'knife':'weapons/melee-detail.jpg',
        'grenade-launcher':'weapons/grenade-launcher-detail.jpg',
        'rocket-launcher':'weapons/grenade-launcher-detail.jpg',
    }
    # These are locally generated category illustrations, not item renders or game UI.
    # Never hotlink the community image CDN or imply that a vignette depicts this exact ID.
    art='../../images/'+art_by_category.get(category,'weapons/weapon-mods-inspection-640.jpg')
    return (f'<span class="phase5-object-image-frame" aria-hidden="true">'
            f'<img class="phase5-object-image" src="{esc(art)}" width="64" height="64" '
            f'alt="" loading="lazy" decoding="async"></span>')

def mode_box():
    buttons=[]
    for key,label in MODES.items():
        pressed=' aria-pressed="true"' if key=='regular' else ' aria-pressed="false"'
        buttons.append(f'<button type="button" class="button button--quiet button--xs" data-mode-set="{key}"{pressed}>{esc(label)}</button>')
    return ('<div class="phase5-mode-box" data-mode-controls hidden><p><strong>Mode de référence des offres / recettes :</strong> '
            '<span data-mode-name>PvP permanent</span></p><div class="phase5-mode-controls" role="group" aria-label="Choisir le mode de données">'
            + ''.join(buttons) + '</div><p class="phase5-mode-note">Les exports sont séparés. Un changement de bouton affiche uniquement le snapshot choisi; il ne valide pas une comparaison de prix entre modes.</p></div>'
            '<p class="phase5-fallback">Sans JavaScript, les champs variables affichent l’export PvP permanent par défaut.</p>')

def option(label,value,selected=False, extra=''):
    return f'<option value="{esc(value)}"{(" selected" if selected else "")}{extra}>{esc(label)}</option>'

def filter_form(config, rows, traders, kind, groups, id_suffix):
    calibers=sorted({(r.get('stats') or {}).get('caliber') for r in rows if (r.get('stats') or {}).get('caliber')}, key=lambda x: caliber_label(x).casefold())
    fields=[f'<label class="field" for="p5-search-{id_suffix}">Nom, calibre, tag ou identifiant<span class="field__wrap"><input class="field__input" type="search" id="p5-search-{id_suffix}" placeholder="Ex. M4A1, 5,56, AP" autocomplete="off" data-p5-search></span></label>']
    fields.append(f'<label class="field" for="p5-caliber-{id_suffix}">Calibre<span class="field__wrap"><select class="field__input" id="p5-caliber-{id_suffix}" data-p5-caliber>{option("Tous les calibres","")}' + ''.join(option(caliber_label(c),c) for c in calibers) + '</select></span></label>')
    if kind=='weapon':
        if config.get('type')=='weapon-index':
            fields.append(f'<label class="field" for="p5-family-{id_suffix}">Famille<span class="field__wrap"><select class="field__input" id="p5-family-{id_suffix}" data-p5-family>{option("Toutes les familles","")}' + ''.join(option(GROUP_LABELS[k],k) for k in GROUP_LABELS) + '</select></span></label>')
        fields.append(f'<label class="field" for="p5-trader-{id_suffix}">Trader avec offre renseignée<span class="field__wrap"><select class="field__input" id="p5-trader-{id_suffix}" data-p5-trader>{option("Tous les traders","")}' + ''.join(option(t, t) for t in traders) + '</select></span></label>')
        fields.append(f'<label class="field" for="p5-level-{id_suffix}">Niveau trader maximal · LL<span class="field__wrap"><select class="field__input" id="p5-level-{id_suffix}" data-p5-level>{option("Tous les niveaux","")}' + ''.join(option(f"LL {level}",str(level)) for level in range(1,5)) + '</select></span></label>')
        if config.get('type')=='weapon-index':
            fields.append(f'<label class="field" for="p5-budget-{id_suffix}">Plafond indicatif · prix RUB exporté<span class="field__wrap"><input class="field__input" id="p5-budget-{id_suffix}" data-p5-budget inputmode="numeric" type="number" min="0" step="1000" placeholder="Laisser vide"></span></label>')
            fields.append(f'<label class="field" for="p5-rate-{id_suffix}">Cadence minimale · export<span class="field__wrap"><input class="field__input" id="p5-rate-{id_suffix}" data-p5-rate inputmode="numeric" type="number" min="0" step="25" placeholder="Toutes"></span></label>')
            fields.append(f'<label class="field" for="p5-ergo-{id_suffix}">Ergonomie minimale · export<span class="field__wrap"><input class="field__input" id="p5-ergo-{id_suffix}" data-p5-ergo inputmode="numeric" type="number" min="0" step="1" placeholder="Toutes"></span></label>')
        fields.append(f'<label class="field" for="p5-sort-{id_suffix}">Trier par<span class="field__wrap"><select class="field__input" id="p5-sort-{id_suffix}" data-p5-sort>{option("Ordre du catalogue","",True)}{option("Nom","name",extra=" data-sort-field=\"name\"")}{option("Cadence la plus élevée","rate",extra=" data-sort-field=\"rate\"")}{option("Ergonomie la plus élevée","ergo",extra=" data-sort-field=\"ergo\"")}{option("Masse la plus élevée","weight",extra=" data-sort-field=\"weight\"")}{option("Prix RUB exporté le plus bas","price",extra=" data-sort-field=\"price\"")}</select></span></label>')
    else:
        types=sorted({(r.get('stats') or {}).get('ammoType') for r in rows if (r.get('stats') or {}).get('ammoType')},key=str.casefold)
        fields.append(f'<label class="field" for="p5-type-{id_suffix}">Type d’objet ammo<span class="field__wrap"><select class="field__input" id="p5-type-{id_suffix}" data-p5-type>{option("Tous les types","")}' + ''.join(option(AMMO_TYPES.get(t,t),t) for t in types) + '</select></span></label>')
        fields.append(f'<label class="field" for="p5-trader-{id_suffix}">Trader avec offre renseignée<span class="field__wrap"><select class="field__input" id="p5-trader-{id_suffix}" data-p5-trader>{option("Tous les traders","")}' + ''.join(option(t,t) for t in traders) + '</select></span></label>')
        fields.append(f'<label class="field" for="p5-level-{id_suffix}">Niveau trader maximal · LL<span class="field__wrap"><select class="field__input" id="p5-level-{id_suffix}" data-p5-level>{option("Tous les niveaux","")}' + ''.join(option(f"LL {level}",str(level)) for level in range(1,5)) + '</select></span></label>')
        fields.append(f'<label class="field" for="p5-sort-{id_suffix}">Trier par<span class="field__wrap"><select class="field__input" id="p5-sort-{id_suffix}" data-p5-sort>{option("Ordre du catalogue","",True)}{option("Nom","name",extra=" data-sort-field=\"name\"")}{option("Dégâts","damage",extra=" data-sort-field=\"damage\"")}{option("Pénétration","penetration",extra=" data-sort-field=\"penetration\"")}{option("Vitesse initiale","speed",extra=" data-sort-field=\"speed\"")}</select></span></label>')
    return ('<form class="phase5-filter-box" data-p5-filter-form hidden><div class="phase5-controls-grid">' + ''.join(fields) + '</div>'
            '<div class="phase5-control-actions"><button class="button button--quiet button--xs" type="reset">Effacer les filtres</button>'
            f'<p class="phase5-status" role="status" aria-live="polite" data-p5-count>{len(rows)} entrées · PvP permanent</p></div></form>')

def weapon_table_rows(rows_by_mode, group_filter, item_map, ammo_name_map, traders_by_mode, collected_at, threshold):
    ref_records=rows_by_mode['regular']
    offers_union=set()
    for mode in MODES:
        for row in rows_by_mode[mode]:
            for offer in row.get('buyFromTrader') or []:
                offers_union.add(trader_name(offer.get('trader'),traders_by_mode.get(mode,{})))
    traders=sorted(offers_union,key=str.casefold)
    output=[]
    for index, base in enumerate(ref_records):
        if group_filter and base.get('group') != group_filter: continue
        id_=base['id']; metrics=metric_for_weapon(base,item_map)
        values=mode_values({m:{r['id']:r for r in rows_by_mode[m]}[id_] for m in MODES},id_,collected_at,threshold,traders_by_mode)
        group=base.get('group') or 'other'
        stats=base.get('stats') or {}
        preset_id=stats.get('defaultPreset'); preset=item_map.get(preset_id) if preset_id else None
        label=base.get('nameFr') or base.get('nameEn') or id_
        short=base.get('shortNameFr') or base.get('shortNameEn') or base.get('nameEn') or ''
        image_markup=object_image_markup(id_,label,item_map)
        category=base.get('category') or 'Non classé'
        search=weapon_search(base,metrics,ammo_name_map)
        rate=stats.get('fireRate'); ergo=stats.get('ergonomics'); weight=base.get('weight')
        data_attrs=(f'data-p5-row data-id="{esc(id_)}" data-group="{esc(group)}" data-caliber="{esc(stats.get("caliber") or "")}" '
                    f'data-rate="{esc(rate if rate is not None else "")}" data-ergo="{esc(ergo if ergo is not None else "")}" '
                    f'data-weight="{esc(weight if weight is not None else "")}" data-damage="{esc(stats.get("slashDamage") or "")}" '
                    f'data-penetration="{esc(stats.get("recoilVertical") or "")}" data-speed="" data-search="{esc(search)}" '
                    f'data-sort-name="{esc(label)}" data-item-name="{esc(label)}" data-metrics="{esc(js_json(metrics))}" data-mode-values="{mode_attr(values)}"')
        row=[f'<tr {data_attrs}>']
        row.append(f'<td><input class="phase5-compare-check" type="checkbox" value="{esc(id_)}" data-compare-pick hidden aria-label="Ajouter {esc(label)} à la comparaison"></td>')
        row.append(f'<th scope="row"><span class="phase5-item-identity">{image_markup}<span class="phase5-item-copy"><span class="phase5-item-name">{esc(label)}</span><span class="phase5-item-sub">{esc(short)} · <code>{esc(id_)}</code></span></span></span></th>')
        row.append(f'<td>{esc(group_label(group))}<span class="phase5-small">{esc(category)}{(" · signalDevice" if base.get("signalDevice") else "")}</span></td>')
        row.append(f'<td>{esc(metrics["caliber"])}</td>')
        if group_filter=='melee':
            row.append(f'<td>{fmt_num(stats.get("slashDamage"))}</td>')
            row.append(f'<td>{fmt_num(stats.get("stabDamage"))}</td>')
        row.append(f'<td data-sort-value="{esc(rate if rate is not None else "")}">{fmt_num(rate)}<span class="phase5-small">coups/min · export</span></td>')
        row.append(f'<td>{fmt_num(ergo)}</td>')
        row.append(f'<td>{fmt_num(stats.get("recoilVertical"))} / {fmt_num(stats.get("recoilHorizontal"))}<span class="phase5-small">vertical / horizontal</span></td>')
        row.append(f'<td>{fmt_num(weight)}<span class="phase5-small">kg · objet</span></td>')
        preset_text=(preset.get('nameFr') or preset.get('nameEn')) if preset else ('ID non résolu' if preset_id else 'Aucun lié')
        preset_weight=preset.get('weight') if preset else None
        row.append(f'<td>{esc(preset_text)}<span class="phase5-small">masse liée : {fmt_num(preset_weight)} kg; stats assemblées non fournies</span></td>')
        row.append(f'<td data-mode-field="offers">{render_offers(values["regular"])}</td>')
        row.append(f'<td data-mode-field="flea">{esc(values["regular"]["flea"]["label"])}</td>')
        row.append('</tr>'); output.append(''.join(row))
    return ''.join(output), traders

def ammo_table_rows(ammo_by_mode, item_map, traders_by_mode, recipe_modes, collected_at, threshold, detailed=True):
    base_rows=ammo_by_mode['regular']; traders_union=set(); output=[]
    id_maps={m:{r['id']:r for r in ammo_by_mode[m]} for m in MODES}
    for mode in MODES:
        for row in ammo_by_mode[mode]:
            for offer in row.get('buyFromTrader') or []:
                traders_union.add(trader_name(offer.get('trader'),traders_by_mode.get(mode,{})))
    for index, base in enumerate(base_rows):
        id_=base['id']; stats=base.get('stats') or {}; metrics=metric_for_ammo(base)
        values=mode_values({m:id_maps[m][id_] for m in MODES},id_,collected_at,threshold,traders_by_mode,recipe_modes)
        label=base.get('nameFr') or base.get('nameEn') or id_
        short=base.get('shortNameFr') or base.get('shortNameEn') or base.get('nameEn') or ''
        image_markup=object_image_markup(id_,label,item_map)
        ammo_type=stats.get('ammoType') or ''
        search=ammo_search(base,metrics)
        attrs=(f'data-p5-row data-id="{esc(id_)}" data-ammo-type="{esc(ammo_type)}" data-group="ammo" '
               f'data-caliber="{esc(stats.get("caliber") or "")}" data-damage="{esc(stats.get("damage") if stats.get("damage") is not None else "")}" '
               f'data-penetration="{esc(stats.get("penetrationPower") if stats.get("penetrationPower") is not None else "")}" '
               f'data-speed="{esc(stats.get("initialSpeed") if stats.get("initialSpeed") is not None else "")}" data-rate="" data-ergo="" data-weight="" '
               f'data-sort-name="{esc(label)}" data-item-name="{esc(label)}" data-search="{esc(search)}" data-metrics="{esc(js_json(metrics))}" data-mode-values="{mode_attr(values)}"')
        row=[f'<tr {attrs}>']
        row.append(f'<td><input class="phase5-compare-check" type="checkbox" value="{esc(id_)}" data-compare-pick hidden aria-label="Ajouter {esc(label)} à la comparaison"></td>')
        row.append(f'<th scope="row"><span class="phase5-item-identity">{image_markup}<span class="phase5-item-copy"><span class="phase5-item-name">{esc(label)}</span><span class="phase5-item-sub">{esc(short)} · <code>{esc(id_)}</code></span></span></span></th>')
        row.append(f'<td>{esc(AMMO_TYPES.get(ammo_type,ammo_type or "Non renseigné"))}</td>')
        row.append(f'<td>{esc(metrics["caliber"])}</td>')
        row.append(f'<td>{fmt_num(stats.get("damage"))}</td>')
        row.append(f'<td>{fmt_num(stats.get("penetrationPower"))}</td>')
        row.append(f'<td>{fmt_num(stats.get("armorDamage"))}%</td>')
        frag=stats.get('fragmentationChance')
        row.append(f'<td>{fmt_num(frag*100 if frag is not None else None)}%</td>')
        row.append(f'<td>{fmt_num(stats.get("initialSpeed"))} m/s</td>')
        row.append(f'<td>{fmt_num(stats.get("projectileCount"))}</td>')
        row.append(f'<td data-mode-field="offers">{render_offers(values["regular"])}</td>')
        row.append(f'<td data-mode-field="craft">{render_crafts(values["regular"])}</td>')
        row.append(f'<td data-mode-field="flea">{esc(values["regular"]["flea"]["label"])}</td>')
        row.append('</tr>'); output.append(''.join(row))
    return ''.join(output), sorted(traders_union,key=str.casefold)

def table_wrapper(caption, headings, rows, body_id, width_label):
    th=''.join(f'<th scope="col">{esc(label)}</th>' for label in headings)
    return (f'<div class="phase5-table-scroll" role="region" aria-label="{esc(width_label)}" tabindex="0">'
            f'<table class="phase5-table" data-p5-table><caption>{esc(caption)}</caption><thead><tr>{th}</tr></thead>'
            f'<tbody id="{esc(body_id)}" data-p5-table-body>{rows}</tbody></table></div>')

def mode_controls_section(region_attrs='data-p5-catalog'):
    return mode_box()

def section(id_, number, kicker, title, paragraph, inner):
    return (f'<section class="guide-section phase5-section" id="{esc(id_)}" tabindex="-1" aria-labelledby="{esc(id_)}-title">'
            f'<div class="guide-section__heading"><p class="guide-kicker"><span>{esc(number)}</span> {esc(kicker)}</p>'
            f'<h2 id="{esc(id_)}-title">{esc(title)}</h2><p>{paragraph}</p></div>{inner}</section>')

def source_cite_line(page):
    keys=page.get('sources') or []
    if not keys: return ''
    return ' · '.join(ref(key,citation_label(key)) for key in keys[:3])

def render_introduction(page, root, page_date):
    inner=(f'<div class="phase5-intro"><p>{esc(page["intro"])}</p>'
           f'<p class="phase5-source-note">Instantané : {esc(page_date)}. Les noms, identifiants et propriétés numériques sont repris du flux communautaire; aucun test client/raid n’est attribué à ce relevé.</p>'
           f'<p class="phase5-image-note">Les vignettes sont des illustrations éditoriales générées, locales et au format JPG, choisies par famille. Elles ne représentent pas le modèle exact d’un objet EFT et ne remplacent ni l’ID ni ses statistiques exportées. Aucune icône d’objet distante n’est chargée.</p>'
           f'<div role="note" class="phase5-callout"><strong>À retenir</strong><p>{esc(page["note"])} {source_cite_line(page)}</p></div></div>')
    return section('perimetre','01','Périmètre','Avant de comparer', 'Trois exports de jeu, un même catalogue communautaire : le mode sélectionné est indiqué près de chaque champ variable.', inner)

def quick_facts(items):
    return '<ul class="phase5-quick-facts">'+''.join(f'<li><strong>{esc(value)}</strong><span>{esc(label)}</span></li>' for value,label in items)+'</ul>'

def page_nav(pages, current, root, weapon_counts):
    rows=[]; groups=[('Arsenal',['pages/weapons/index.html','pages/weapons/assault-rifles.html','pages/weapons/smgs.html','pages/weapons/shotguns.html','pages/weapons/sniper-rifles.html','pages/weapons/dmrs.html','pages/weapons/lmgs.html','pages/weapons/pistols.html','pages/weapons/melee.html','pages/weapons/grenade-launchers.html','pages/weapons/weapon-mods.html']),('Munitions',['pages/ammo/index.html','pages/ammo/ammo-chart.html'])]
    byfile={p['file']:p for p in pages}
    for group_name, files in groups:
        rows.append(f'<li class="phase5-rail-group" aria-hidden="true">{esc(group_name)}</li>')
        for file in files:
            p=byfile[file]
            count=''
            if p.get('group') in weapon_counts: count=fmt_num(weapon_counts[p['group']])
            elif p['type']=='weapon-index': count='199'
            elif p['type'] in {'ammo-index','ammo-chart'}: count='200'
            href=root+p['route']
            aria=' aria-current="page"' if file==current else ''
            rows.append(f'<li><a class="phase5-rail-link" href="{esc(href)}"{aria}><span>{esc(p["label"])}</span><small>{esc(count)}</small></a></li>')
    return ''.join(rows)

def catalog_section(page, root, rows_by_mode, item_map, ammo_name_map, trader_snapshots, collected_at, threshold, groups):
    group_filter=page.get('group') if page['type']=='weapon-family' else None
    selected=[r for r in rows_by_mode['regular'] if not group_filter or r.get('group')==group_filter]
    row_html,traders=weapon_table_rows(rows_by_mode,group_filter,item_map,ammo_name_map,trader_snapshots,collected_at,threshold)
    region_attr='data-p5-catalog data-active-mode="regular"'
    config_section=(mode_box()+filter_form(page,selected,traders,'weapon',groups,page['code'].replace('–','').replace(' ','').lower()))
    headings=['Comparer','Objet · ID','Groupe · catégorie','Calibre']
    if group_filter=='melee': headings += ['Dégâts slash · export','Dégâts stab · export']
    headings += ['Cadence · coups/min','Ergo','Recul V/H','Masse · kg','Preset lié','Offres · mode choisi','Flea · fraîcheur']
    if page.get('type')=='weapon-index':
        title='Catalogue des objets classés armes'; intro='Filtrez par famille, calibre, trader, niveau LL, cadence, ergonomie ou plafond priceRUB. Le filtre budget porte sur l’offre exportée de l’objet seul, pas sur un preset complet.'
        facts=[('199','entrées armes dans chacun des trois exports'),('164','presets par défaut liés à un objet du catalogue'),('1 391','IDs autorisés recensés dans les slots')]
    else:
        title=f'Catalogue · {group_label(group_filter)}'; intro=f'{len(selected)} entrées dans ce groupe de l’export. Les colonnes « arme » et « preset » restent séparées; sélectionnez un mode pour afficher l’instantané d’offres correspondant.'
        facts=[(fmt_num(len(selected)),'entrées dans ce groupe'),(fmt_num(sum(bool((r.get('stats') or {}).get('defaultPreset')) for r in selected)),'presets par défaut référencés'),('3','exports séparés')]
    table=table_wrapper('Le tableau initial affiche l’export PvP permanent; les modes et champs variables se mettent à jour avec le sélecteur.',headings,row_html,'weapon-rows-'+page['code'].replace('–','').replace(' ','').lower(),'Catalogue des armes, défilement horizontal si nécessaire')
    compare=(f'<div class="phase5-compare-tools" data-p5-compare-tools hidden><p data-p5-compare-status role="status" aria-live="polite">0/3 sélectionné · cochez jusqu’à trois lignes.</p>'
             '<button class="button button--quiet button--xs" type="button" data-p5-compare-clear>Effacer la comparaison</button></div>'
             '<div class="phase5-compare-output" data-p5-compare-output aria-live="polite"></div>'
             '<p class="phase5-table-note">Sans JavaScript, le tableau reste complet dans le mode par défaut; les filtres, changements de mode et comparateur sont des améliorations progressives.</p>')
    inner=(quick_facts(facts)+f'<p class="phase5-table-note">{esc(intro)}</p>'+config_section+table
           +'<p class="phase5-status phase5-empty" data-p5-empty hidden>Aucun objet ne correspond à ces critères. Modifiez ou effacez les filtres.</p>')
    compare_section=section('comparaison','03','Comparer','Comparer de deux à trois objets','Les lignes de comparaison sont calculées uniquement dans le mode choisi; aucun prix n’est comparé entre modes.',compare)
    return f'<div {region_attr}>{section("catalogue","02","Catalogue",title,"Les noms et champs ci-dessous viennent de l’export arrêté au "+time_fr(collected_at)+".",inner)}{compare_section}</div>'

def family_catalog_content(page, root, rows_by_mode, item_map, ammo_name_map, trader_snapshots, collected_at, threshold, groups):
    catalog_html=catalog_section(page,root,rows_by_mode,item_map,ammo_name_map,trader_snapshots,collected_at,threshold,groups)
    # catalog_section contains the comparison section inside its catalog wrapper; remove any extra references handled in wrapper.
    method=weapon_method_section(page, collected_at)
    return render_introduction(page,root,time_fr(collected_at))+catalog_html+method

def weapon_method_section(page, collected_at):
    group=page.get('group')
    if group=='melee':
        cards=[('Slash / stab','slashDamage et stabDamage sont des champs du jeu, pas une mesure réelle.'),('Accès','Red Rebel reste une entrée de mêlée; les conditions d’extraction doivent être lues dans le raid.'),('Absence','Une cellule vide signifie non renseigné ou non applicable, pas zéro.')]
    elif group=='grenade-launchers':
        cards=[('Périmètre','Le groupe de dix inclut huit `signalDevice`; la catégorie seule ne suffit pas.'),('Munition','Consultez le tableau ammo; le type et le nombre de projectiles font partie du périmètre.'),('IDs','Le nom et l’identifiant sont conservés pour distinguer lanceurs et objets de signal.')]
    elif group=='assault-rifles':
        cards=[('Familles','53 entrées assault-rifle et 10 assault-carbine dans ce groupe de 63.'),('Calibre','Le calibre n’est pas une liste exhaustive de chargeurs compatibles.'),('Exemples','M4A1, AK-74N et QBZ-191 sont des lignes de lecture, pas un classement.')]
    else:
        cards=[('Arme seule','Ergonomie et recul appartiennent à l’objet de base tel qu’exporté.'),('Preset','Le preset par défaut peut être lié et pesé, mais ses stats assemblées ne sont pas fournies.'),('Choix','Aucun tier ranking : la page n’a ni test client ni preuve reproductible de méta.')]
    content='<div class="phase5-method-grid">'+''.join(f'<article><h3>{esc(title)}</h3><p>{esc(text)}</p></article>' for title,text in cards)+'</div>'
    note='<div role="note" class="phase5-callout phase5-callout--warning"><strong>Prix et disponibilité</strong><p>Les offres affichées appartiennent au snapshot sélectionné et ne prouvent pas le stock actuel du marchand. Le marché flea n’est affiché que si le prix existe et que son horodatage est à sept jours ou moins; les données plus anciennes ou sans date restent explicitement non exploitables.</p></div>'
    return section('methode','04','Méthode','Lire les colonnes sans surinterpréter',f'Collecte catalogue : {time_fr(collected_at)}. Le build client n’est pas inscrit dans l’API.',content+note)

def render_weapon_index(page, root, rows_by_mode, item_map, ammo_name_map, trader_snapshots, collected_at, threshold, groups, pages, weapon_counts):
    fam_cards=[]
    for group, label in GROUP_LABELS.items():
        target=next(p for p in pages if p.get('group')==group)
        fam_cards.append(f'<a class="phase5-family-card" href="{esc(root+target["route"])}"><strong>{esc(label)}</strong><span>{fmt_num(weapon_counts.get(group,0))} entrées · filtre par calibre et offre</span></a>')
    cats=quick_facts([('199','armes exportées par mode'),('164','presets par défaut reliés à un item'),('987','slots analysés dans les stats d’armes')])
    family_inner='<div class="phase5-family-grid">'+''.join(fam_cards)+'</div>'
    family_section=section('familles','02','Familles','Entrer par type d’objet','Les groupes sont définis par le champ `group` du catalogue; le filtre et les pages conservent les limites de chaque catégorie.',cats+family_inner)
    catalog=catalog_section(page,root,rows_by_mode,item_map,ammo_name_map,trader_snapshots,collected_at,threshold,groups)
    # la section catalogue de l’index inclut déjà le comparateur.
    official=(f'<div class="phase5-callout phase5-callout--quiet"><strong>Ce que BSG a effectivement annoncé</strong>'
      f'<p>Le 12 novembre, BSG a indiqué que les munitions utilisées par The Wedge et ses gardes avaient changé dans tous les modes; aucune cartouche n’est nommée. Cette note concerne leurs équipements/IA et ne donne pas les stats des cartouches de joueur. {ref("bsg-balance-nov")}</p>'
      f'<p>Le carnet BSG du 18 novembre annonce la 1.3.5.0 pour la seconde moitié du mois, avec Unity 6 et des travaux techniques de chargement et de stabilité serveur. Il ne publie pas de nouvelle table d’armes ou de munitions de joueur; revalider les exports après déploiement sans présumer de changements non annoncés. {ref("bsg-135-diary")}</p>'
      f'<p>Le patch 1.1.0.0 du 3 août a abaissé d’un niveau certaines offres et réduit les prix de cinq types de munitions. Ce contexte historique ne valide pas une offre aujourd’hui ni un prix actuel par profil. {ref("patch110")}</p>'
      f'<p>Les notes 1.2.0.0 et 1.3.0.0 consultées ne contiennent pas de tableau général des stats de munitions de joueur; cela ne prouve pas l’absence de changement non publié. {ref("patch120")} {ref("patch130")}</p></div>')
    return render_introduction(page,root,time_fr(collected_at))+family_section+catalog+weapon_method_section(page,collected_at)+section('infos-bsg','05','Veille','Notes officielles et périmètre', 'Patch notes et annonce officielle relus avant rédaction.', official)

def ammo_filters_and_table(page, root, ammo_by_mode, item_map, traders_by_mode, recipes, collected_at, threshold, groups, id_suffix, chart_mode=False):
    base=ammo_by_mode['regular']
    rows,traders=ammo_table_rows(ammo_by_mode,item_map,traders_by_mode,recipes,collected_at,threshold)
    region='data-p5-ammo data-active-mode="regular"'
    config=mode_box()+filter_form(page,base,traders,'ammo',groups,id_suffix)
    headings=['Comparer','Munition · ID','Type','Calibre','Dégâts','Pénétration','Dégâts armure','Fragmentation','Vitesse','Projectiles','Offres · mode choisi','Crafts · mode choisi','Flea · fraîcheur']
    table=table_wrapper('Export initial PvP permanent; choisissez un mode pour les offres, recettes et statuts flea.',headings,rows,'ammo-rows-'+id_suffix,'Tableau complet des munitions, défilement horizontal si nécessaire')
    compare=(f'<div class="phase5-compare-tools" data-p5-compare-tools hidden><p data-p5-compare-status role="status" aria-live="polite">0/3 sélectionné · cochez jusqu’à trois lignes.</p>'
             '<button class="button button--quiet button--xs" type="button" data-p5-compare-clear>Effacer la comparaison</button></div>'
             '<div class="phase5-compare-output" data-p5-compare-output aria-live="polite"></div>')
    return f'<div {region}>{config}{table}<p class="phase5-status phase5-empty" data-p5-empty hidden>Aucune entrée ne correspond. Modifiez ou réinitialisez les filtres.</p>{compare}</div>'

def render_ammo_index(page, root, ammo_by_mode, item_map, traders_by_mode, recipes, collected_at, threshold, groups, pages):
    totals={'bullet':0,'buckshot':0,'grenade':0,'flashbang':0}
    for row in ammo_by_mode['regular']: totals[(row.get('stats') or {}).get('ammoType')]+=1
    facts=quick_facts([(fmt_num(len(ammo_by_mode['regular'])),'enregistrements ammo, pas 200 cartouches de fusil'),(fmt_num(totals['bullet']),'type bullet'),(fmt_num(totals['buckshot']),'type buckshot')])
    inner=facts+f'<p class="phase5-table-note">Répartition complète : {totals["bullet"]} bullet · {totals["buckshot"]} buckshot · {totals["grenade"]} grenade · {totals["flashbang"]} flashbang. La page communautaire consultée annonce 199 rounds; les périmètres de l’API et du tableau ne sont pas réconciliés. {ref("wiki-ammo-2026")}</p>'
    inter=ammo_filters_and_table(page,root,ammo_by_mode,item_map,traders_by_mode,recipes,collected_at,threshold,groups,'ammo-hub')
    # Données phares vérifiées par identifiant, pas par nom seul.
    target_id='54527ac44bdc2d36668b4567'
    m855=next(x for x in ammo_by_mode['regular'] if x['id']==target_id)
    st=m855['stats']
    recipe=recipes['regular'].get(target_id,[])
    craft_markup=render_crafts({'recipes':recipe})
    example=(f'<div class="phase5-method-grid"><article><h3>Valeurs de l’export</h3><p>5.56x45mm M855A1 · dégâts {fmt_num(st.get("damage"))} · pénétration {fmt_num(st.get("penetrationPower"))} · dégâts d’armure {fmt_num(st.get("armorDamage"))}% · fragmentation {fmt_num(st.get("fragmentationChance",0)*100)}% · vitesse initiale {fmt_num(st.get("initialSpeed"))} m/s · {fmt_num(st.get("projectileCount"))} projectile.</p><p>Ces valeurs du relevé sont concordantes avec la fiche TarkovWiki consultée; ce n’est pas un essai client. {ref("tdev-phase5-catalog")} {ref("wiki-m855a1-2026")}</p></article>'
      f'<article><h3>Craft trouvé dans les trois snapshots</h3><p>Le produit M855A1 est référencé avec {fmt_num(recipe[0].get("count") if recipe else None)} cartouches, Workbench niveau {fmt_num(recipe[0].get("level") if recipe else None)}, durée {esc(recipe[0].get("durationLabel") if recipe else "non renseignée")}.</p>{craft_markup}<p>L’export ne contient que l’ID de déblocage; le nom « Special Equipment » a été résolu séparément sur la page de tâche Tarkov.dev. {ref("tdev-special-equipment")}</p></article></div>')
    conflict='<div role="note" class="phase5-source-warning"><strong>Offres traders : conflit non résolu.</strong><p>Le champ `buyFromTrader` de l’export retenu est vide pour cette entrée, tandis que la fiche communautaire TarkovWiki affiche des offres de marchands. La page n’en déduit ni l’absence ni le prix d’une offre dans votre mode; contrôlez l’interface du marchand. Pas de comparaison de prix entre modes.</p></div>'
    official='<div role="note" class="phase5-callout"><strong>Ajustement IA ≠ table balistique joueur</strong><p>Le 12/11/2026, BSG a annoncé un changement des munitions utilisées par The Wedge et ses gardes dans tous les modes sans préciser lesquelles. Aucune cartouche de joueur ne peut en être déduite. '+ref('bsg-balance-nov')+'</p><p>Le carnet BSG du 18/11 annonce la 1.3.5.0 pour la seconde moitié de novembre, centrée sur Unity 6 et les améliorations techniques. Il ne publie pas de nouvelle table de munitions joueur; revalider le snapshot après déploiement. '+ref('bsg-135-diary')+'</p></div>'
    meth='<div class="phase5-method-grid"><article><h3>Dégâts et pénétration</h3><p>Deux champs distincts. Le tableau n’assigne pas une classe d’armure déterministe : le wiki consulté qualifie l’estimation depuis la pénétration d’heuristique.</p></article><article><h3>Flea et prix</h3><p>Dans cet instantané, les relevés d’ammo PvP/PvE sont très anciens et Seasonal n’a pas d’horodatage. Aucune valeur manquante ne devient zéro ni « prix actuel ».</p></article><article><h3>Économie datée</h3><p>La note BSG 1.1.0.0 a changé certains paliers et prix de munitions en août; elle n’est pas un inventaire d’offres du 18 novembre.</p></article><article><h3>Pas de classement</h3><p>Un guide commercial du 17/11 propose des tiers; ils ne sont pas repris comme vérité officielle ou preuve de méta actuelle.</p></article></div>'
    return render_introduction(page,root,time_fr(collected_at))+section('catalogue','02','Catalogue','Filtrer les munitions exportées','Le mode sélectionné porte sur les offres, recettes et relevés de marché; les propriétés balistiques concordent entre les exports inspectés.',inter)+section('exemple','03','Exemple sourcé','M855A1 : chiffres et craft vérifiés', 'Exemple d’identifiant contrôlé; un homonyme d’un autre calibre existe dans le catalogue.',example+conflict)+section('methode','04','Lecture','Ce que le tableau permet — et ne permet pas', 'Une donnée de jeu n’est pas une simulation complète de pénétration ou de combat.',meth+official)

def render_craft_page_rows(recipe_modes, ammo_id_map, item_map, hideout_snapshot):
    rows=[]
    base=recipe_modes['regular']
    for product_id, recipes in base.items():
        if product_id not in ammo_id_map: continue
        ammo=ammo_id_map[product_id]
        for rec in recipes:
            inputs=', '.join(f'{fmt_num(x.get("count"))} × {x.get("name")}' + (' (outil indiqué)' if x.get('tool') else '') for x in rec.get('requiredItems',[]))
            rows.append((ammo.get('nameFr') or ammo.get('nameEn') or product_id, rec.get('station'), rec.get('level'), rec.get('durationLabel'), fmt_num(rec.get('count')), inputs, rec.get('task'), rec.get('taskUnlock')))
    rows.sort(key=lambda x: (str(x[0]).casefold(),str(x[1]).casefold(),x[2] or 0))
    return rows

def render_ammo_chart(page, root, ammo_by_mode, item_map, traders_by_mode, recipes, collected_at, threshold, groups, pages):
    bullets=[r for r in ammo_by_mode['regular'] if (r.get('stats') or {}).get('ammoType')=='bullet' and (r.get('stats') or {}).get('damage') is not None and (r.get('stats') or {}).get('penetrationPower') is not None]
    max_pen=max((r['stats']['penetrationPower'] for r in bullets),default=1)
    max_damage=max((r['stats']['damage'] for r in bullets),default=1)
    x_max=max(10,math.ceil(max_pen/10)*10); y_max=max(50,math.ceil(max_damage/50)*50)
    x_label_step=max(20,math.ceil((x_max/6)/10)*10)
    x_labels=list(range(0,x_max+1,x_label_step))
    if x_labels[-1]!=x_max: x_labels.append(x_max)
    y_step=50
    y_labels=list(range(0,y_max+1,y_step))
    grid=[]
    for tick in range(10,x_max,10):
        x=100*tick/x_max
        grid.append(f'<span class="chart-grid-line chart-grid-line--vertical" style="--chart-position:{x:.3f}%"></span>')
    for tick in range(y_step,y_max,y_step):
        y=100-100*tick/y_max
        grid.append(f'<span class="chart-grid-line chart-grid-line--horizontal" style="--chart-position:{y:.3f}%"></span>')
    points=[]
    for row in bullets:
        st=row['stats']; x=100*st['penetrationPower']/x_max; y=100-100*st['damage']/y_max
        name=row.get('nameFr') or row.get('nameEn') or row['id']
        short=row.get('shortNameFr') or row.get('shortNameEn') or ''
        search=ammo_search(row,metric_for_ammo(row))
        title=f'{name} ({short}) · dégâts {fmt_num(st["damage"])} · pénétration {fmt_num(st["penetrationPower"])}'
        points.append(f'<span class="chart-point" data-chart-point data-id="{esc(row["id"])}" data-caliber="{esc(st.get("caliber") or "")}" data-search="{esc(search)}" style="--chart-x:{x:.3f}%;--chart-y:{y:.3f}%" title="{esc(title)}"></span>')
    y_tick_markup=''.join(f'<span>{tick}</span>' for tick in reversed(y_labels))
    x_tick_markup=''.join(f'<span style="--chart-position:{100*tick/x_max:.3f}%">{tick}</span>' for tick in x_labels)
    chart=(f'<div class="phase5-chart" role="img" aria-label="Nuage de points : dégâts et pénétration des objets bullet">'
           f'<span class="phase5-chart__y-label" aria-hidden="true">Dégâts · export</span>'
           f'<div class="phase5-chart__y-ticks" aria-hidden="true">{y_tick_markup}</div>'
           f'<div class="phase5-chart__plot" aria-hidden="true">{"".join(grid)}{"".join(points)}</div>'
           f'<div class="phase5-chart__x-ticks" aria-hidden="true">{x_tick_markup}</div>'
           f'<span class="phase5-chart__x-label" aria-hidden="true">Puissance de pénétration · export</span></div>'
           '<p class="phase5-chart-alt">Chaque point reprend un objet bullet de l’export communautaire. La table suivante fournit les valeurs numériques et tous les types d’ammo; aucune classe d’armure ni tier n’est déduit du graphique.</p>')
    chart_form=('<form class="phase5-filter-box" data-p5-chart-filter hidden><div class="phase5-controls-grid">'
      '<label class="field" for="chart-search">Nom ou calibre<span class="field__wrap"><input class="field__input" id="chart-search" type="search" data-chart-search placeholder="Ex. M855A1, 5,56" autocomplete="off"></span></label>'
      '<label class="field" for="chart-caliber">Calibre<span class="field__wrap"><select class="field__input" id="chart-caliber" data-chart-caliber>'+option('Tous les calibres','')+''.join(option(caliber_label(c),c) for c in sorted({r['stats'].get('caliber') for r in bullets},key=lambda c:caliber_label(c).casefold()))+'</select></span></label>'
      '<button class="button button--quiet button--xs" type="reset">Réinitialiser le graphique</button></div>'
      '<p class="phase5-status" role="status" aria-live="polite" data-chart-count>180 points de type bullet · stats communes aux exports du 18/11</p></form>')
    chart_inner=('<div data-p5-chart>'+chart_form+f'<div class="phase5-chart-layout">{chart}<div class="phase5-chart-key"><span>Entrée bullet du catalogue</span><span>Survolez un point pour afficher le nom et les valeurs; la table complète reste disponible.</span></div></div><p class="phase5-status phase5-empty" data-chart-empty hidden>Aucun point ne correspond à ces filtres.</p><p class="phase5-table-note">Les 13 buckshot, 6 grenades et 1 flashbang ne figurent pas sur le nuage; ils restent dans la table complète. La couleur unique ne code aucun tier.</p></div>')
    content_intro=render_introduction(page,root,time_fr(collected_at))
    table=ammo_filters_and_table(page,root,ammo_by_mode,item_map,traders_by_mode,recipes,collected_at,threshold,groups,'ammo-chart')
    craft_rows=render_craft_page_rows(recipes,{r['id']:r for r in ammo_by_mode['regular']},item_map,{})
    craft_body=''.join(f'<tr><th scope="row">{esc(name)}</th><td>{esc(station)}</td><td>{fmt_num(level)}</td><td>{esc(duration)}</td><td>{esc(count)}</td><td>{esc(inputs)}</td><td>{esc((task.get("name") + (" · " + task["faction"] if task.get("faction") else "") + " · " + task_id) if task else ("ID " + task_id + " · nom non résolu" if task_id else "Non indiqué"))}</td></tr>' for name,station,level,duration,count,inputs,task,task_id in craft_rows)
    craft_table=table_wrapper('Recettes d’ammo dans le snapshot communautaire PvP permanent; le contrôle croisé PvE/Seasonal est dans le rapport de vérification.', ['Produit','Station','Niveau','Durée','Sortie','Ingrédients du snapshot','Tâche'],craft_body,'ammo-craft-rows','Recettes ammo, défilement horizontal si nécessaire')
    mode_note=(f'<div role="note" class="phase5-callout"><strong>Le graphique n’est pas une tier list.</strong><p>Il n’assigne aucune classe d’armure. TarkovWiki avertit que l’estimation de classe à partir de la pénétration est heuristique; les plates et leur état ne sont pas modélisés ici. {ref("wiki-ammo-2026")}</p><p>Le guide LFCarry du 17/11 publie des rangs S/A et des seuils de progression; c’est une source commerciale et communautaire, non une annonce BSG ni une preuve de méta actuelle. Nous ne reprenons pas ces rangs. {ref("lfcarry-ammo-2026")}</p></div>')
    recipes_overview=quick_facts([(fmt_num(len(bullets)),'points bullet affichés'),(fmt_num(len(ammo_by_mode['regular'])),'lignes dans la table complète'),(fmt_num(len(recipes['regular'])),'produits ammo avec recette dans le snapshot')])
    craft_section=section('craft','05','Hideout','Recettes de munitions recensées','Les champs de station, niveau, durée, ingrédients, sortie et déblocage sont exposés dans l’instantané; ils ne prouvent pas le stock ou l’état actuel du client.',recipes_overview+craft_table+'<p class="phase5-table-note">`tool` est conservé comme attribut d’ingrédient. Le snapshot conserve des IDs de tâche seulement; ceux qui figurent dans les exemples ont été résolus séparément sur les pages de tâches Tarkov.dev. Les noms et conditions restent communautaires, sans test client. Les recettes ammo comparées entre les trois modes ne montrent pas d’écart de contenu; détails et limites dans le rapport.</p>')
    return content_intro+section('graphique','02','Visualisation','Dégâts exportés ↔ pénétration exportée','Le nuage limité aux 180 entrées `bullet`; les filtres ne modifient pas la table principale si JavaScript est désactivé.',chart_inner)+section('table','03','Données','Table complète par calibre et type','Valeurs et champs de prix/craft restent séparés; utilisez le sélecteur de mode pour lire l’instantané correspondant.',table)+section('methode','04','Interprétation','Une balistique de jeu n’est pas un calcul de plaque', 'La table documente des propriétés exportées; elle ne simule pas une rencontre.',mode_note+craft_section)

def render_mods_page(page, root, weapons, items, rows_by_mode, collected_at, pages):
    item_map={r['id']:r for r in items}
    allowed_by_item={}; weapons_by_item={}; slots_by_weapon={}; group_by_weapon={}
    slot_counts={}; slot_allowed={}
    for weapon in weapons:
        wid=weapon['id']; group=weapon.get('group') or 'other'; group_by_weapon[wid]=group
        slots=(weapon.get('stats') or {}).get('slots') or []
        rows=[]
        for slot in slots:
            sid=slot.get('nameId') or 'slot-inconnu'
            allowed=(slot.get('filters') or {}).get('allowedItems') or []
            slot_counts[sid]=slot_counts.get(sid,0)+1
            slot_allowed[sid]=slot_allowed.get(sid,0)+len(set(allowed))
            rows.append({'id':sid,'name':SLOT_LABELS.get(sid,sid.replace('_',' ')),'required':bool(slot.get('required')),'count':len(set(allowed))})
            for item_id in set(allowed):
                allowed_by_item.setdefault(item_id,set()).add(sid)
                weapons_by_item.setdefault(item_id,set()).add(wid)
        slots_by_weapon[wid]=rows
    catalog=[]
    for item_id, slot_ids in allowed_by_item.items():
        item=item_map.get(item_id)
        if not item: continue
        groups_set={group_by_weapon.get(wid) for wid in weapons_by_item.get(item_id,set())}
        weapon_names=sorted({(next((w.get('nameFr') for w in weapons if w['id']==wid),None) or next((w.get('nameEn') for w in weapons if w['id']==wid),wid)) for wid in weapons_by_item.get(item_id,set())},key=str.casefold)
        cat=item.get('category') or ', '.join(item.get('types') or [])
        catalog.append({'id':item_id,'item':item,'slots':sorted(slot_ids),'groups':sorted(g for g in groups_set if g),'weapons':weapon_names,'cat':cat})
    catalog.sort(key=lambda row:(-(len(row['weapons'])),str(row['item'].get('nameFr') or row['item'].get('nameEn') or '').casefold(),row['id']))
    slot_options=sorted(slot_counts,key=lambda sid:SLOT_LABELS.get(sid,sid).casefold())
    form=('<form class="phase5-filter-box" data-mod-filter-form hidden><div class="phase5-controls-grid">'
      '<label class="field" for="mod-search">Nom, ID ou type<span class="field__wrap"><input class="field__input" id="mod-search" type="search" data-mod-search placeholder="Ex. poignée, 55d4…" autocomplete="off"></span></label>'
      '<label class="field" for="mod-slot">Slot<span class="field__wrap"><select class="field__input" id="mod-slot" data-mod-slot>'+option('Tous les slots','')+''.join(option(SLOT_LABELS.get(s,s.replace('_',' ')),s) for s in slot_options)+'</select></span></label>'
      '<label class="field" for="mod-family">Famille compatible<span class="field__wrap"><select class="field__input" id="mod-family" data-mod-family>'+option('Toutes les familles','')+''.join(option(GROUP_LABELS[g],g) for g in GROUP_LABELS)+'</select></span></label>'
      '<label class="field" for="mod-sort">Trier par<span class="field__wrap"><select class="field__input" id="mod-sort" data-mod-sort>'+option('Compatibilité la plus large','weapons',True,' data-sort-field="weapons"')+option('Nom','name',extra=' data-sort-field="name"')+'</select></span></label>'
      '</div><div class="phase5-control-actions"><button class="button button--quiet button--xs" type="reset">Effacer les filtres</button><p class="phase5-status" role="status" aria-live="polite" data-mod-count>1 391 modifications</p></div></form>')
    mod_rows=[]
    for idx,entry in enumerate(catalog):
        item=entry['item']; name=item.get('nameFr') or item.get('nameEn') or entry['id']
        en=item.get('nameEn') or ''
        image_markup=object_image_markup(entry['id'],name,item_map)
        slot_text=', '.join(SLOT_LABELS.get(s,s.replace('_',' ')) for s in entry['slots'])
        family_text=', '.join(GROUP_LABELS.get(g,g) for g in entry['groups'])
        platforms=', '.join(esc(w) for w in entry['weapons'])
        compatible_html='<details class="phase5-disclosure"><summary>'+fmt_num(len(entry['weapons']))+' plateformes</summary><div class="phase5-disclosure__body"><p class="phase5-disclosure__platforms">'+platforms+'</p></div></details>'
        mod_rows.append(f'<tr data-mod-row data-families="{esc(" ".join(entry["groups"]))}" data-weapons="{len(entry["weapons"])}"><th scope="row"><span class="phase5-item-identity">{image_markup}<span class="phase5-item-copy"><span class="phase5-item-name">{esc(name)}</span><span class="phase5-item-sub">{esc(en)} · <code>{esc(entry["id"])}</code></span></span></span></th><td>{esc(entry["cat"])}</td><td>{esc(slot_text)}<span class="phase5-small"><code>{esc(" · ".join(entry["slots"]))}</code></span></td><td>{compatible_html}</td><td>{esc(family_text)}</td></tr>')
    slot_table=[]
    for sid in slot_options:
        slot_table.append(f'<tr><th scope="row">{esc(SLOT_LABELS.get(sid,sid.replace("_"," ")))}</th><td><code>{esc(sid)}</code></td><td>{fmt_num(slot_counts[sid])}</td><td>{fmt_num(slot_allowed[sid])}</td></tr>')
    table=table_wrapper('Chaque ligne est un ID de modification autorisé par au moins un slot d’arme; ouvrir « plateformes » pour voir les armes résolues.', ['Modification · ID','Catégorie export','Slots autorisés','Plateformes compatibles','Familles'],''.join(mod_rows),'mod-rows','Index des modifications par ID, défilement horizontal si nécessaire')
    table_markup='<p class="phase5-status" role="status" data-mod-loading hidden>Préparation de l’index des modifications…</p><div data-mod-table-host></div><noscript data-mod-fallback>'+table+'</noscript>'
    slot_table_html=table_wrapper('Résumé des slots tels que nommés dans les filtres d’export; les noms sont normalisés pour la lecture française.', ['Slot normalisé','nameId export','Occurrences de slots','IDs autorisés cumulés'],' '.join([]).join(slot_table),'slot-summary-rows','Résumé des slots, défilement horizontal si nécessaire')
    stats_slots=sum(len(rows) for rows in slots_by_weapon.values())
    all_allowed=len(allowed_by_item); resolved=len(set(allowed_by_item)&item_map.keys())
    note=(f'<div role="note" class="phase5-callout phase5-callout--warning"><strong>Ce n’est pas un calculateur de build.</strong><p>Dans l’export utilisé, le catalogue réduit ne fournit pas les propriétés complètes de chaque mod ni toutes les offres traders. Les champs de preset assemblé ergonomie/recul/poids sont nuls; le coût total et les stats finales ne sont donc pas calculés. Compatibilité = présence de l’ID dans une liste de slot, à vérifier dans le client.</p></div>')
    content=render_introduction(page,root,time_fr(collected_at))+section('slots','02','Slots','Lire les compatibilités déclarées','L’export conserve des `nameId`, un indicateur required et des listes d’IDs allow-listed.',quick_facts([(fmt_num(stats_slots),'slots trouvés dans les stats d’armes'),(fmt_num(all_allowed),'IDs uniques allow-listed'),(fmt_num(resolved),'IDs résolus dans items.json')])+slot_table_html)+section('mod-catalogue','03','Index','Rechercher une modification par ID','La table agrège le nombre d’armes et les familles qui autorisent chaque ID; elle n’affirme pas que les pièces sont toutes achetables ou montables en un clic.',form+table_markup+'<p class="phase5-status phase5-empty" data-mod-empty hidden>Aucun ID ne correspond à ce filtre.</p>')+section('methode','04','Limites','Prix, ergo et recul d’un build', 'La compatibilité ne décrit pas la performance finale d’une arme assemblée.',note+'<p class="phase5-table-note">Les listes de slots et leurs propriétés de base concordent entre les trois exports de catalogues comparés le 18/11/2026. La preuve détaillée et les critères de comparaison sont dans le rapport de vérification.</p>')
    return '<div data-p5-mods>'+content+'</div>'

def render_ammo_method(page, collected_at):
    return ''

def build_content(page, root, all_data):
    kind=page['type']; d=all_data
    if kind=='weapon-index':
        return render_weapon_index(page,root,d['weapons'],d['items'],d['ammoNameMap'],d['traders'],d['collectedAt'],d['threshold'],d['groups'],d['pages'],d['weaponCounts'])
    if kind=='weapon-family':
        return family_catalog_content(page,root,d['weapons'],d['items'],d['ammoNameMap'],d['traders'],d['collectedAt'],d['threshold'],d['groups'])
    if kind=='weapon-mods':
        return render_mods_page(page,root,d['weapons']['regular'],d['itemRows'],d['weapons'],d['collectedAt'],d['pages'])
    if kind=='ammo-index':
        return render_ammo_index(page,root,d['ammo'],d['items'],d['traders'],d['recipes'],d['collectedAt'],d['threshold'],d['groups'],d['pages'])
    if kind=='ammo-chart':
        return render_ammo_chart(page,root,d['ammo'],d['items'],d['traders'],d['recipes'],d['collectedAt'],d['threshold'],d['groups'],d['pages'])
    raise ValueError(f'type de page PHASE_5 inconnu : {kind}')

def build_phase5(data, plan, sources, base, patch, read_text, compact):
    config=json.loads((ROOT/DATA).read_text(encoding='utf-8'))
    template=read_text(TEMPLATE)
    phase_pages=[row for row in plan['pages'] if row.get('phase')=='PHASE_5']
    if {row['fichier'] for row in phase_pages}!={row['file'] for row in config['pages']}:
        raise ValueError('La configuration PHASE_5 ne correspond pas aux 13 routes du plan editorial.')
    manifest=read('js/data/catalog-manifest.json')
    collected_at=datetime.fromisoformat(manifest['collectedAt'].replace('Z','+00:00'))
    verified=datetime.fromisoformat(config['verifiedAt'])
    public_seo_base=seo_base_is_public(base)
    page_date=time_fr(collected_at)
    weapon_bundles={}; ammo_bundles={}; item_bundles={}
    for mode in MODES:
        prefix='' if mode=='regular' else mode+'/'
        weapon_bundles[mode]=read('js/data/'+prefix+'weapons.json')['records']
        ammo_bundles[mode]=read('js/data/'+prefix+'ammo.json')['records']
        item_bundles[mode]=read('js/data/'+prefix+'items.json')['records']
    item_rows=item_bundles['regular']; item_map={row['id']:row for row in item_rows}
    ammo_name_map={row['id']:row.get('nameEn') or '' for row in ammo_bundles['regular']}
    crafts=read(config['craftsSnapshot']); trader_snapshot=read(config['tradersSnapshot'])
    traders={mode:trader_snapshot['modes'][mode]['traders'] for mode in MODES}
    recipes=prepare_crafts(crafts,item_map,trader_snapshot['hideout'],config.get('questNames'))
    weapon_counts={group:sum(r.get('group')==group for r in weapon_bundles['regular']) for group in GROUP_LABELS}
    # Aliases par mode, utilisés pour une recherche comparative, sans fusionner les prix.
    all_data={
        'weapons':weapon_bundles,'ammo':ammo_bundles,'items':item_map,'itemRows':item_rows,
        'ammoNameMap':ammo_name_map,'traders':traders,'recipes':recipes,'collectedAt':collected_at,
        'threshold':int(config.get('thresholdFleaDays',7)),'groups':GROUP_LABELS,'weaponCounts':weapon_counts,
        'pages':config['pages'],
    }
    local_html={}; search=[]
    nav=page_nav(config['pages'],None,'',weapon_counts)
    for page in config['pages']:
        root=root_for(page['file'])
        parent_label,parent_url=(('Équipement',root+'#equipement') if page['type'] in {'weapon-index','ammo-index'} else
                                 ('Arsenal',root+'pages/weapons/') if page['type'].startswith('weapon') else
                                 ('Munitions',root+'pages/ammo/'))
        nav_w=(' aria-current="page"' if page['type']=='weapon-index' else ' aria-current="location"' if page['type'].startswith('weapon') else '')
        nav_a=(' aria-current="page"' if page['type']=='ammo-index' else ' aria-current="location"' if page['type'].startswith('ammo') else '')
        canonical=urljoin(base,page['route']) if public_seo_base else None
        image_abs=urljoin(base,page['image'])
        mobile_image=str(PurePosixPath(page['image']).with_suffix(''))+'-640.jpg'
        if (ROOT/mobile_image).is_file():
            image_candidates=f'{esc(root+mobile_image)} 640w, {esc(root+page["image"])} 1376w'
            image_srcset=f'srcset="{image_candidates}" sizes="100vw"'
            image_preload=(f'<link rel="preload" href="{esc(root+page["image"])}" as="image" '
                           f'imagesrcset="{image_candidates}" imagesizes="100vw" fetchpriority="high">')
        else:
            image_srcset=''
            image_preload=f'<link rel="preload" href="{esc(root+page["image"])}" as="image" fetchpriority="high">'
        breadcrumb_parent=urljoin(base,parent_url) if canonical else None
        toc=[]
        for i,row in enumerate(page['quick'],1):
            dest,label,short=row
            toc.append(f'<a class="guide-quick__link" href="#{esc(dest)}"><span class="guide-quick__no" aria-hidden="true">{i:02d}</span><span class="guide-quick__copy"><small>{esc(short)}</small><strong>{esc(label)}</strong></span><span class="guide-quick__arrow" aria-hidden="true">↓</span></a>')
        sources_used=[sources[key] for key in page['sources']]
        content=build_content(page,root,all_data)
        next_page=next((p for p in config['pages'] if p['type']=='ammo-index'),config['pages'][0]) if page['type'].startswith('weapon') else next(p for p in config['pages'] if p['type']=='weapon-index')
        next_blurb='Comparer les propriétés des armes dans un mode explicite.' if page['type'].startswith('ammo') else 'Lire le catalogue des munitions sans assimiler pénétration et résultat de raid.'
        article={'@type':'Article','headline':page['title'],'description':page['description'],'inLanguage':'fr-FR','datePublished':verified.date().isoformat(),'dateModified':verified.isoformat(),'image':{'@type':'ImageObject','url':image_abs,'width':1376,'height':768},'author':{'@type':'Organization','name':'Tarkov Ultimate Guide'}}
        schema={'@context':'https://schema.org','@graph':[article]}
        if canonical:
            article.update({'@id':canonical+'#article','mainEntityOfPage':canonical})
            article['author']['url']=base
            schema['@graph'].append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Accueil','item':base},{'@type':'ListItem','position':2,'name':parent_label,'item':breadcrumb_parent},{'@type':'ListItem','position':3,'name':page['label'],'item':canonical}]})
        slots={
          'ROOT':esc(root),'DESCRIPTION':esc(page['description']),'SEO_TITLE':esc(page['seoTitle']),
          'CANONICAL_LINK':canonical_link(base,page['route']),'OG_URL_META':open_graph_url_meta(base,page['route']),
          'OG_IMAGE':esc(image_abs),'IMAGE':esc(page['image']),'IMAGE_SRCSET':image_srcset,'IMAGE_PRELOAD':image_preload,'IMAGE_ALT':esc(page['imageAlt']),
          'IMAGE_CAPTION':esc(page['imageCaption']),'VERIFIED_AT':esc(verified.isoformat()),'VERIFIED_DAY':esc(verified.date().isoformat()),
          'DATE_SHORT':esc(verified.strftime('%d.%m.%Y')),'DATE_LONG':esc(date_fr(verified.date())),
          'PATCH':esc(patch),'LABEL':esc(page['label']),'CODE':esc(page['code']),'HEADING':esc(page['title']),'LEAD':esc(page['lead']),
          'PARENT_URL':esc(parent_url),'PARENT_LABEL':esc(parent_label),'NAV_WEAPONS_CURRENT':nav_w,'NAV_AMMO_CURRENT':nav_a,
          'PRIMARY_ANCHOR':esc(page['quick'][0][0]),'PRIMARY_LABEL':esc(page['quick'][0][1]),'SECONDARY_ANCHOR':esc(page['quick'][1][0]),'SECONDARY_LABEL':esc(page['quick'][1][1]),
          'QUICK':'\n'.join(toc),'PAGE_NAV':page_nav(config['pages'],page['file'],root,weapon_counts),'CONTENT':content,
          'SOURCE_LIST':source_list(page['sources'],sources),'SOURCE_CODE':f'{len(page["sources"]):02}',
          'NEXT_LABEL':esc(next_page['label']),'NEXT_BLURB':esc(next_blurb),'NEXT_URL':esc(root+next_page['route']),
          'JSON_LD':compact(schema),
        }
        html=re.sub(r'\[\[([A-Z_]+)\]\]',lambda m:slots[m[1]],template)
        if '[[' in html: raise ValueError(f'Token non remplacé dans {page["file"]}')
        local_html[page['file']]=html
        search.append({'title':page['title'],'href':page['route'],'tag':'Arsenal' if page['type'].startswith('weapon') else 'Munitions','summary':page['description'],'keywords':[page['label'],page['type'],*page['sources'],*list(MODES.values())]})
    return local_html,search,verified
