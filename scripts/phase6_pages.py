#!/usr/bin/env python3
"""Construit les routes PHASE_6 et son snapshot défensif daté."""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlsplit
from zoneinfo import ZoneInfo
from site_urls import seo_base_is_public
import argparse
import hashlib
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = 'data/phase6.json'
TEMPLATE = 'templates/phase6.html.in'
MODES = {
    'regular': 'PvP permanent',
    'pve': 'PvE Zone',
    'pvp-season': 'PvP Seasonal',
}
GROUP_LABELS = {
    'body-armor': 'Gilets / armures', 'plates': 'Plaques', 'headwear': 'Casques / tête',
    'rigs': 'Rigs', 'attachment': 'Accessoires', 'eyewear': 'Lunettes',
}
SOURCE_LABELS = {
    'primaire': 'Annonce officielle BSG', 'wiki': 'Wiki communautaire',
    'donnees_communautaires': 'Export communautaire', 'outil_communautaire': 'Outil communautaire',
    'communaute': 'Retour communautaire', 'video': 'Vidéo communautaire', 'forum': 'Forum communautaire',
}
MAP_ROUTES = {
    'Customs':'customs.html','Woods':'woods.html','Shoreline':'shoreline.html','Lighthouse':'lighthouse.html',
    'Factory':'factory.html','Interchange':'interchange.html','Reserve':'reserve.html','Streets of Tarkov':'streets-of-tarkov.html',
    'Terminal':'terminal.html','Icebreaker':'icebreaker.html','The Labyrinth':'the-labyrinth.html','The Lab':'the-lab.html',
    'Ground Zero':'ground-zero.html',
}
SLOT_LABELS = {
    'Front_plate':'Plaque avant amovible','Back_plate':'Plaque arrière amovible',
    'Left_side_plate':'Plaque latérale gauche','Right_side_plate':'Plaque latérale droite',
    'Soft_armor_front':'Couche souple avant','Soft_armor_back':'Couche souple arrière',
    'Soft_armor_left':'Couche souple latérale gauche','Soft_armor_right':'Couche souple latérale droite',
    'Groin':'Protection bassin / aine','Helmet_top':'Casque · sommet','Helmet_back':'Casque · arrière',
    'Helmet_ears':'Casque · oreilles','Helmet_face':'Casque · visage','Helmet_jaw':'Casque · mâchoire',
    'Helmet_eyes':'Casque · yeux','Helmet_nape':'Casque · nuque','Helmet_chin':'Casque · menton',
}
ZONE_LABELS = {
    'Armor Zone Plate_Granit_SAPI_chest':'Emplacement de plaque avant (thorax)',
    'Armor Zone Plate_Granit_SAPI_back':'Emplacement de plaque arrière',
    'Armor Zone Plate_Granit_SSAPI_side_left_low':'Emplacement de plaque latérale gauche basse',
    'Armor Zone Plate_Granit_SSAPI_side_right_low':'Emplacement de plaque latérale droite basse',
    'RibcageUp':'Thorax supérieur','RibcageLow':'Thorax inférieur','SpineTop':'Dos supérieur',
    'SpineDown':'Dos inférieur','Pelvis':'Bassin','LeftSideChestDown':'Flanc gauche inférieur',
    'RightSideChestDown':'Flanc droit inférieur','LeftUpperArm':'Bras supérieur gauche',
    'RightUpperArm':'Bras supérieur droit','NeckFront':'Cou avant','NeckBack':'Cou arrière',
    'HeadCommon':'Tête','ParietalHead':'Sommet du crâne','BackHead':'Arrière du crâne',
    'Ears':'Oreilles','Eyes':'Yeux','Jaw':'Mâchoire','Nape':'Nuque','HeadTop':'Sommet du crâne',
}


def read_json(path: str | Path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def esc(value):
    return escape(str(value if value is not None else ''), quote=True)


def js_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).replace('<', r'\\u003c').replace('>', r'\\u003e').replace('&', r'\\u0026')


def norm(value):
    value = str(value or '').lower()
    value = ''.join(ch for ch in __import__('unicodedata').normalize('NFD', value) if __import__('unicodedata').category(ch) != 'Mn')
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', value).split())


def fmt_num(value, digits=3):
    if value is None or value == '':
        return '—'
    if isinstance(value, bool):
        return 'Oui' if value else 'Non'
    try:
        n = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(n):
        return '—'
    if n.is_integer():
        return f'{int(n):,}'.replace(',', '\u202f')
    return f'{n:,.{digits}f}'.replace(',', '\u202f').replace('.', ',')


def fmt_money(value):
    return '—' if value is None else f'{fmt_num(value, 0)} ₽'


def fmt_day(value):
    day = value.date() if isinstance(value, datetime) else value
    months = 'janvier février mars avril mai juin juillet août septembre octobre novembre décembre'.split()
    return f'{day.day} {months[day.month - 1]} {day.year}'


def fmt_short(day: date):
    return day.strftime('%d.%m.%Y')


def group_label(group):
    return GROUP_LABELS.get(group, group or 'Groupe non résolu')


def zone_label(value):
    raw = str(value or '')
    if raw.startswith('Armor Zone '):
        return ZONE_LABELS.get(raw, raw.replace('Armor Zone ', 'Zone plaque · ').replace('_', ' '))
    if raw.startswith('Collider Type '):
        tail = raw.removeprefix('Collider Type ')
        return ZONE_LABELS.get(tail, tail.replace('_', ' '))
    return ZONE_LABELS.get(raw, raw.replace('_', ' '))


def slot_label(slot):
    key = str(slot.get('nameId') or slot.get('name') or '')
    return SLOT_LABELS.get(key, key.replace('_', ' ').strip().capitalize() or 'Slot non nommé')


def record_stats(record):
    return record.get('stats') or {}


def slot_classes(stats):
    slots = stats.get('armorSlots') or []
    found = []
    for slot in slots:
        cls = slot.get('class')
        if isinstance(cls, (int, float)) and cls > 0:
            found.append(str(int(cls) if float(cls).is_integer() else cls))
    if not found:
        cls = stats.get('class')
        if isinstance(cls, (int, float)) and cls > 0:
            found.append(str(int(cls) if float(cls).is_integer() else cls))
    return sorted(set(found), key=lambda x: float(x))


def class_text(stats):
    slots = stats.get('armorSlots') or []
    rows = []
    for slot in slots:
        label = slot_label(slot)
        cls = slot.get('class')
        if isinstance(cls, (int, float)) and cls > 0:
            rows.append(f'{label} : classe {fmt_num(cls, 0)}')
        elif slot.get('allowedPlates'):
            rows.append(f'{label} : insert amovible; {len(slot["allowedPlates"])} IDs de compatibilité exportés')
        elif 'plate' in str(slot.get('nameId') or '').lower():
            rows.append(f'{label} : classe de la plaque insérée non déduite du porteur')
    if not rows:
        cls = stats.get('class')
        if isinstance(cls, (int, float)) and cls > 0:
            rows.append(f'Classe {fmt_num(cls, 0)} au niveau de l’objet exporté')
    return rows or ['Aucune classe renseignée dans ce champ d’export']


def protection_details(stats):
    slots = stats.get('armorSlots') or []
    all_zones = list(dict.fromkeys(stats.get('zones') or []))
    if not all_zones:
        for slot in slots:
            all_zones.extend(slot.get('zones') or [])
        all_zones = list(dict.fromkeys(all_zones))
    details = []
    if slots:
        for slot in slots:
            label = slot_label(slot)
            zones = ', '.join(zone_label(z) for z in (slot.get('zones') or [])) or 'zone non listée'
            cls = slot.get('class')
            durability = slot.get('durability')
            material = slot.get('armorMaterial') or slot.get('material')
            bits = []
            if isinstance(cls, (int, float)) and cls > 0:
                bits.append(f'classe {fmt_num(cls, 0)}')
            elif slot.get('allowedPlates'):
                bits.append(f'insert amovible · {len(slot["allowedPlates"])} compatibilités par ID dans l’export')
            if durability is not None:
                bits.append(f'{fmt_num(durability, 1)} durabilité exportée')
            if material:
                bits.append(f'matériau {material}')
            details.append(f'<li><strong>{esc(label)}</strong> · {esc("; ".join(bits) or "classe non listée")} · {esc(zones)}</li>')
    if all_zones:
        details.append('<li><strong>Zones listées au niveau de l’objet</strong> · ' + esc(', '.join(zone_label(z) for z in all_zones)) + '</li>')
    if not details:
        return '<span class="phase6-muted">Zones de protection non renseignées.</span>'
    return '<details class="phase6-disclosure"><summary>Lire les slots et zones exportés</summary><ul>' + ''.join(details) + '</ul><p>Une zone listée n’est pas une mesure de hitbox en client.</p></details>'


def slot_materials(stats):
    slots = stats.get('armorSlots') or []
    rows = []
    for slot in slots:
        material = slot.get('armorMaterial') or slot.get('material')
        if material:
            rows.append(f'{slot_label(slot)} : {material}')
    if rows:
        return ' · '.join(dict.fromkeys(rows))
    return str(stats.get('material') or 'Non renseigné dans l’export')


def durability_text(stats):
    slots = stats.get('armorSlots') or []
    rows = [f'{slot_label(slot)} : {fmt_num(slot.get("durability"), 1)}' for slot in slots if slot.get('durability') is not None]
    if rows:
        return ' · '.join(rows)
    return fmt_num(stats.get('durability'), 1)


def grids_text(stats, record):
    capacity = stats.get('capacity')
    grids = stats.get('grids') or []
    dims = Counter((g.get('width'), g.get('height')) for g in grids if g.get('width') and g.get('height'))
    dims_text = ', '.join(f'{w} × {h}' + (f' ({n})' if n > 1 else '') for (w, h), n in sorted(dims.items()))
    overall = f'{fmt_num(capacity, 0)} cases · ' if capacity is not None else ''
    if dims_text:
        return overall + f'{len(grids)} grille(s) : {dims_text}'
    if capacity is not None:
        return overall.rstrip(' ·')
    return f'Taille d’objet exportée : {record.get("width", "—")} × {record.get("height", "—")}'


def penalties_text(stats):
    values = [stats.get('speedPenalty'), stats.get('turnPenalty'), stats.get('ergoPenalty')]
    if all(v is None for v in values):
        return 'Non renseigné'
    return ' / '.join(fmt_num(v, 4) for v in values) + ' · valeurs brutes exportées'


def material_groups(stats):
    material = stats.get('material')
    slots = stats.get('armorSlots') or []
    mats = list(dict.fromkeys(s.get('armorMaterial') or s.get('material') for s in slots if s.get('armorMaterial') or s.get('material')))
    if material:
        mats.insert(0, material)
    return list(dict.fromkeys(mats))


def headset_state(stats):
    value = stats.get('blocksHeadset')
    if value is True:
        return 'bloque'
    if value is False:
        return 'compatible'
    return 'inconnu'


def market_price(item, mode, collected_at, threshold_days):
    raw = (item.get('pricesByMode') or {}).get(mode) or {}
    price, scan = raw.get('lastLowPrice'), raw.get('lastScan')
    scan_date = None
    age = None
    if scan:
        try:
            parsed = datetime.fromisoformat(str(scan).replace('Z', '+00:00'))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            scan_date = parsed.astimezone(ZoneInfo('Europe/Paris')).date()
            age = (collected_at - parsed.astimezone(timezone.utc)).total_seconds() / 86400
        except (ValueError, TypeError):
            scan_date = None
    if price is not None and scan_date and age is not None and 0 <= age <= threshold_days:
        return {'fresh': True, 'value': float(price), 'label': f'{fmt_money(price)} · scan {scan_date.strftime("%d.%m.%Y")}'}
    if scan_date and age is not None and age > threshold_days:
        return {'fresh': False, 'value': None, 'label': f'Périmé · dernier scan {scan_date.strftime("%d.%m.%Y")}'}
    if scan_date and price is None:
        return {'fresh': False, 'value': None, 'label': f'Prix absent · scan {scan_date.strftime("%d.%m.%Y")}'}
    if scan_date and age is not None and age < 0:
        return {'fresh': False, 'value': None, 'label': f'Scan postérieur à la collecte · {scan_date.strftime("%d.%m.%Y")}'}
    return {'fresh': False, 'value': None, 'label': 'Aucun prix exploitable dans cet export'}


def _slim_flea(record):
    flea = record.get('flea') or {}
    return {k: flea.get(k) for k in ('lastLowPrice', 'avg24hPrice', 'lastScan', 'lastOfferCount', 'minLevelForFlea')}


def build_snapshot():
    manifest = read_json('js/data/catalog-manifest.json')
    mode_data = {mode: read_json({'regular':'js/data/armor.json','pve':'js/data/pve/armor.json','pvp-season':'js/data/pvp-season/armor.json'}[mode]) for mode in MODES}
    maps = {mode: {row['id']: row for row in bundle['records']} for mode, bundle in mode_data.items()}
    id_sets = {mode: set(rows) for mode, rows in maps.items()}
    if len({frozenset(ids) for ids in id_sets.values()}) != 1:
        raise ValueError('Les identifiants d’armures diffèrent entre les trois exports.')
    expected = manifest['modes']['regular']['files']['armor']['count']
    if len(maps['regular']) != expected or expected != 423:
        raise ValueError(f'Nombre inattendu d’enregistrements défensifs : {len(maps["regular"])} / {expected}')
    fields = ('nameEn','nameFr','shortNameEn','shortNameFr','normalizedName','category','group','weight','width','height','stats')
    for id_ in sorted(id_sets['regular']):
        ref = maps['regular'][id_]
        for mode in ('pve','pvp-season'):
            other = maps[mode][id_]
            for field in fields:
                if ref.get(field) != other.get(field):
                    raise ValueError(f'Donnée défensive non concordante entre les modes pour {id_}: {field} ({mode})')
    collected = manifest['collectedAt']
    items = []
    for id_ in sorted(id_sets['regular']):
        record = maps['regular'][id_]
        prices = {mode: _slim_flea(maps[mode][id_]) for mode in MODES}
        items.append({
            'id': id_, 'normalizedName': record.get('normalizedName'),
            'nameEn': record.get('nameEn'), 'nameFr': record.get('nameFr'),
            'shortNameEn': record.get('shortNameEn'), 'shortNameFr': record.get('shortNameFr'),
            'category': record.get('category'), 'group': record.get('group'),
            'width': record.get('width'), 'height': record.get('height'), 'weight': record.get('weight'),
            'link': record.get('link'), 'stats': record.get('stats') or {}, 'pricesByMode': prices,
        })
    group_counts = dict(sorted(Counter(row.get('group') or 'unknown' for row in items).items()))
    checksums = {mode: manifest['modes'][mode]['files']['armor']['sha256'] for mode in MODES}
    return {
        'schemaVersion': 1,
        'publisher': manifest.get('publisher', 'Tarkov.dev / The Hideout'),
        'collectedAt': collected,
        'dateParis': manifest.get('dateParis', collected[:10]),
        'gameBuild': manifest.get('gameBuild'),
        'modes': {mode: {'label': MODES[mode], 'count': len(maps[mode]), 'source': mode_data[mode].get('sources', []), 'sha256': checksums[mode]} for mode in MODES},
        'count': len(items), 'groupCounts': group_counts,
        'notes': [
            'Instantané communautaire sélectionné dans les exports Tarkov.dev du 18/11/2026; aucun build EFT n’est fourni par le manifeste.',
            'Les identifiants, noms, groupes et statistiques défensives concordent entre regular, pve et pvp-season lors du contrôle de génération; les valeurs flea restent par mode.',
            'Les prix sont masqués dans les pages si leur scan dépasse sept jours au moment de la collecte, s’il manque ou s’il est postérieur à l’instantané.',
            'La présence d’un objet dans l’export ne prouve pas son acquisition, sa disponibilité dans un mode ou ses performances en client.',
        ],
        'items': items,
    }


def write_snapshot():
    snapshot = build_snapshot()
    target = ROOT / 'data/snapshots/phase-6-armor-2026-11-18.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{target.relative_to(ROOT)} · {snapshot["count"]} items · groupes {snapshot["groupCounts"]}')


def verify_snapshot(snapshot):
    expected = build_snapshot()
    if snapshot != expected:
        raise ValueError('Le snapshot Phase 6 ne correspond plus aux exports et au manifeste locaux; reconstruire ou documenter un nouveau relevé.')


def external_link(url, label, attrs=''):
    parsed = urlsplit(str(url or ''))
    if parsed.scheme != 'https' or not parsed.hostname:
        return esc(label)
    return f'<a href="{esc(url)}"{attrs}>{esc(label)} <span aria-hidden="true">↗</span></a>'


def source_list(keys, sources):
    rows=[]
    for key in keys:
        if key not in sources:
            raise ValueError(f'Source absente de docs/sources.json : {key}')
        record=sources[key]
        parsed=urlsplit(record.get('url',''))
        if parsed.scheme!='https' or not parsed.hostname:
            raise ValueError(f'URL de source non HTTPS : {key}')
        kind=SOURCE_LABELS.get(record.get('type'),'Source consultée')
        rows.append(
            f'<li id="ref-{esc(key)}" tabindex="-1"><span class="guide-source__type">{esc(kind)}</span>'
            f'<a href="{esc(record["url"])}" target="_blank" rel="noopener noreferrer">{esc(record["titre"])} <span aria-hidden="true">↗</span><span class="sr-only"> (nouvel onglet)</span></a>'
            f'<p>{esc(record["usage"])}</p></li>'
        )
    return '\n'.join(rows) or '<li>Aucune référence précise n’est disponible; aucun fait test client n’est revendiqué.</li>'


def price_cell(item, threshold_days, collected_day):
    parts=[]
    for mode,label in MODES.items():
        state=market_price(item,mode,collected_day,threshold_days)
        parts.append(f'<span class="phase6-price" data-price-mode="{mode}"><strong>{esc(label)} :</strong> {esc(state["label"])}</span>')
    return '<div class="phase6-prices">' + ''.join(parts) + '</div>'


def armor_row(item, threshold_days, collected_day, selectable=False):
    stats=record_stats(item)
    name=item.get('nameFr') or item.get('nameEn') or item['id']
    group=item.get('group') or 'unknown'
    classes=slot_classes(stats)
    class_list='|'.join(classes)
    zones=list(dict.fromkeys(stats.get('zones') or []))
    for slot in stats.get('armorSlots') or []:
        zones.extend(slot.get('zones') or [])
    zones=list(dict.fromkeys(zones))
    searchable=norm(' '.join([name,item.get('nameEn') or '',item.get('shortNameFr') or '',item.get('shortNameEn') or '',item['id'],group,item.get('category') or '',*zones]))
    mode_data={mode:market_price(item,mode,collected_day,threshold_days) for mode in MODES}
    attrs=(f'id="p6-item-{esc(item["id"])}" data-p6-item-row data-id="{esc(item["id"])}" '
           f'data-group="{esc(group)}" data-name="{esc(norm(name))}" data-search="{esc(searchable)}" '
           f'data-classes="{esc(class_list)}" data-zones="{esc(norm(" ".join(zone_label(z) for z in zones)))}" '
           f'data-headset="{headset_state(stats)}" data-weight="{esc(item.get("weight") if item.get("weight") is not None else "")}" '
           f'data-capacity="{esc(stats.get("capacity") if stats.get("capacity") is not None else "")}" '
           + ' '.join(f'data-price-{mode}="{esc(state["value"] if state["fresh"] else "")}"' for mode,state in mode_data.items()) + '>')
    class_html='<ul class="phase6-compact-list">'+''.join(f'<li>{esc(row)}</li>' for row in class_text(stats))+'</ul>'
    material=slot_materials(stats)
    dur=durability_text(stats)
    grid=grids_text(stats,item)
    link=external_link(item.get('link'),name,' target="_blank" rel="noopener noreferrer"')
    compare=f'<td class="phase6-select"><label><input type="checkbox" value="{esc(item["id"])}" data-p6-compare-item aria-label="Comparer {esc(name)}"></label></td>' if selectable else ''
    return (
        f'<tr {attrs}'
        f'<th scope="row"><span class="phase6-item-name">{link}</span><span class="phase6-muted">{esc(group_label(group))} · ID {esc(item["id"])}</span></th>'
        f'<td>{class_html}</td><td>{protection_details(stats)}</td><td>{esc(material)}</td><td>{esc(dur)}</td>'
        f'<td data-sort-weight="{esc(item.get("weight") if item.get("weight") is not None else "")}">{esc(fmt_num(item.get("weight"),2))} kg</td>'
        f'<td data-sort-capacity="{esc(stats.get("capacity") if stats.get("capacity") is not None else "")}">{esc(grid)}</td>'
        f'<td>{esc(penalties_text(stats))}</td><td>{price_cell(item,threshold_days,collected_day)}</td>{compare}</tr>'
    )


def armor_table(items, title, threshold_days, collected_day, selectable=False, table_id=None):
    if not items:
        return '<p class="phase6-empty">Aucun enregistrement ne correspond au groupe de données du snapshot.</p>'
    rows='\n'.join(armor_row(item,threshold_days,collected_day,selectable) for item in items)
    caption=f'{title} · {len(items)} entrées · snapshot {collected_day.strftime("%d.%m.%Y")}.'
    width='<th scope="col">Comparer</th>' if selectable else ''
    return (
        f'<div class="phase6-table-wrap" role="region" aria-label="{esc(title)}, défilement horizontal" tabindex="0">'
        f'<table class="phase6-table"'+(f' id="{esc(table_id)}"' if table_id else '')+f'><caption>{esc(caption)}</caption>'
        '<thead><tr><th scope="col">Objet / source</th><th scope="col">Classe par pièce</th><th scope="col">Slots / zones exportés</th><th scope="col">Matériau</th><th scope="col">Durabilité</th><th scope="col">Poids</th><th scope="col">Grille / capacité</th><th scope="col">Mouvement / rotation / ergo</th><th scope="col">Prix flea par mode</th>'+width+'</tr></thead>'
        f'<tbody>{rows}</tbody></table></div>'
    )


def classes_options():
    return ''.join(f'<option value="{n}">Classe {n} sur au moins une pièce</option>' for n in range(1,7))


def render_filter_form(kind, items, threshold_days):
    if kind=='armor-index':
        groups=sorted({item.get('group') or 'unknown' for item in items})
        opts=''.join(f'<option value="{esc(group)}">{esc(group_label(group))}</option>' for group in groups)
        return (
          '<form class="phase6-toolbar" data-p6-filter-form data-filter-kind="armor-index" hidden>'
          '<label class="phase6-control">Nom, catégorie ou ID<input type="search" data-p6-search autocomplete="off" placeholder="Ex. AVS, casque, ID"></label>'
          '<label class="phase6-control">Type d’objet<select data-p6-group><option value="">Tous les groupes</option>'+opts+'</select></label>'
          '<label class="phase6-control">Prix flea de référence<select data-p6-mode><option value="regular">PvP permanent</option><option value="pve">PvE Zone</option><option value="pvp-season">PvP Seasonal</option></select></label>'
          '<label class="phase6-control">Classe présente<select data-p6-class><option value="">Toutes</option>'+classes_options()+'</select></label>'
          '<label class="phase6-control">Prix flea maximum (₽)<input type="number" min="0" step="1000" inputmode="numeric" data-p6-budget placeholder="Aucun plafond"></label>'
          '<button type="reset" class="button button--quiet button--xs">Effacer</button></form>'
          f'<p class="phase6-result-count" role="status" aria-live="polite" data-p6-count>{len(items)} objets · prix anciens/manquants exclus d’un filtre budget.</p>'
        )
    if kind=='body-armor':
        return (
          '<form class="phase6-toolbar" data-p6-filter-form data-filter-kind="body-armor" hidden>'
          '<label class="phase6-control">Nom ou ID<input type="search" data-p6-search autocomplete="off" placeholder="Ex. AVS, SAPI"></label>'
          '<label class="phase6-control">Classe présente<select data-p6-class><option value="">Toutes</option>'+classes_options()+'</select></label>'
          '<label class="phase6-control">Poids maximum (kg)<input type="number" min="0" step="0.1" inputmode="decimal" data-p6-weight-max placeholder="Aucun plafond"></label>'
          '<button type="reset" class="button button--quiet button--xs">Effacer</button></form>'
          f'<p class="phase6-result-count" role="status" aria-live="polite" data-p6-count>{len(items)} objets dans les groupes Gilets / armures et Plaques.</p>'
        )
    if kind=='helmets':
        all_zones=sorted({zone_label(z) for item in items for z in (record_stats(item).get('zones') or [])},key=norm)
        zone_opts=''.join(f'<option value="{esc(norm(zone))}">{esc(zone)}</option>' for zone in all_zones)
        return (
          '<form class="phase6-toolbar" data-p6-filter-form data-filter-kind="helmets" hidden>'
          '<label class="phase6-control">Nom ou ID<input type="search" data-p6-search autocomplete="off" placeholder="Ex. FAST, visière"></label>'
          '<label class="phase6-control">Classe présente<select data-p6-class><option value="">Toutes</option>'+classes_options()+'</select></label>'
          '<label class="phase6-control">Zone reportée<select data-p6-zone><option value="">Toutes les zones</option>'+zone_opts+'</select></label>'
          '<label class="phase6-control">Casque audio selon l’export<select data-p6-headset><option value="">Toutes</option><option value="compatible">Non bloqué (export)</option><option value="bloque">Bloqué (export)</option><option value="inconnu">Non renseigné</option></select></label>'
          '<button type="reset" class="button button--quiet button--xs">Effacer</button></form>'
          f'<p class="phase6-result-count" role="status" aria-live="polite" data-p6-count>{len(items)} entrées headwear / accessoire / eyewear.</p>'
        )
    if kind=='rigs':
        return (
          '<form class="phase6-toolbar" data-p6-filter-form data-filter-kind="rigs" hidden>'
          '<label class="phase6-control">Nom ou ID<input type="search" data-p6-search autocomplete="off" placeholder="Ex. AVS, 6B13"></label>'
          '<label class="phase6-control">Trier les lignes<select data-p6-sort><option value="name">Nom</option><option value="weight">Poids croissant</option><option value="capacity">Capacité croissante</option></select></label>'
          '<button type="reset" class="button button--quiet button--xs">Effacer / réinitialiser</button></form>'
          f'<p class="phase6-result-count" role="status" aria-live="polite" data-p6-count>{len(items)} rigs · capacité et géométrie gardées distinctes.</p>'
        )
    return ''


def quick_links(rows):
    return ''.join(f'<a class="guide-quick__link" href="#{esc(anchor)}"><span class="guide-quick__no" aria-hidden="true">{i:02}</span><span class="guide-quick__copy"><small>{esc(kicker)}</small><strong>{esc(label)}</strong></span><span class="guide-quick__arrow" aria-hidden="true">↓</span></a>' for i,(anchor,kicker,label) in enumerate(rows,1))


def gallery_html(gallery):
    if not gallery:
        return ''
    rows=[]
    for image in gallery:
        src=image['src']
        if not (ROOT/src).is_file():
            raise ValueError(f'Visuel local absent : {src}')
        rows.append(f'<figure><img src="../../{esc(src)}" width="1376" height="768" loading="lazy" decoding="async" alt="{esc(image["alt"])}"><figcaption>{esc(image["caption"])}</figcaption></figure>')
    return '<div class="phase6-gallery">'+'\n'.join(rows)+'</div>'


def table_section(section_id, kicker, title, summary, items, threshold, day, selectable=False, table_id=None):
    return (
      f'<section class="phase6-subsection" id="{esc(section_id)}" data-p6-anchor aria-labelledby="{esc(section_id)}-title">'
      f'<div class="phase6-section__head"><p class="guide-kicker"><span>{esc(kicker)}</span> {len(items)} entrées</p>'
      f'<h3 id="{esc(section_id)}-title">{esc(title)}</h3><p>{esc(summary)}</p></div>'
      + armor_table(items,title,threshold,day,selectable,table_id) + '</section>'
    )


def method_section(verified_at, mode_counts=True):
    return (
      '<section class="phase6-section" id="methode" data-p6-anchor aria-labelledby="p6-method-title">'
      '<div class="phase6-section__head"><p class="guide-kicker"><span>MÉTHODE / LIMITES</span> Snapshot du 18.11.2026</p>'
      '<h2 id="p6-method-title">Comment lire ces données</h2>'
      '<p>Les statistiques d’objet, les prix flea et les observations de wiki n’ont pas le même niveau de preuve. Les prix affichés sont par mode et seulement si le dernier scan date de moins de sept jours au moment de la collecte; les autres sont marqués périmés ou absents. Aucun champ de l’export ne constitue un test en client.</p></div>'
      '<div class="phase6-grid">'
      '<div class="phase6-card"><p class="phase6-card__eyebrow">Données communes</p><h3>423 enregistrements par mode</h3><p>Les identifiants, noms, groupes et statistiques des trois exports concordent dans le snapshot du 18 novembre 2026. Les prix flea, eux, restent attachés à PvP permanent, PvE Zone ou PvP Seasonal.</p></div>'
      '<div class="phase6-card"><p class="phase6-card__eyebrow">Ce qui reste à vérifier</p><h3>Client, disponibilité et impact</h3><p>Compatibilité, emplacement exact de hitbox, état d’usure, pénétration, disponibilité en raid et probabilités de spawn n’ont pas été testés. Les pages Wiki sont communautaires et peuvent être en retard sur un correctif.</p></div>'
      '</div><p class="phase6-note">Relevé éditorial : '+esc(fmt_day(datetime.fromisoformat(verified_at).date()))+'. Le manifeste Tarkov.dev ne déclare aucun build client pour ces données.</p></section>'
    )


def armor_index(page, data, threshold, verified_at):
    items=data['items']
    day=date.fromisoformat(data['dateParis'])
    groups=Counter(item.get('group') or 'unknown' for item in items)
    group_cards=''.join(f'<div class="phase6-card"><p class="phase6-card__eyebrow">{esc(group_label(k))}</p><h3>{v} fiches</h3><p>Entrées du sous-ensemble défensif exporté.</p></div>' for k,v in groups.items())
    content=(
      '<section class="phase6-section" id="catalogue" data-p6-anchor aria-labelledby="p6-catalogue-title">'
      '<div class="phase6-section__head"><p class="guide-kicker"><span>ARMURES / CATALOGUE</span> 18.11.2026</p><h2 id="p6-catalogue-title">Filtrer par pièce, mode et classe</h2>'
      '<p>Comparez les protections listées dans l’export sans transformer le gilet, ses emplacements de plaques et ses couches souples en une classe globale. Les champs inconnus restent absents; le filtre de classe signifie « présente sur au moins une pièce ».</p></div>'
      '<div class="phase6-note"><strong>Couverture :</strong> une plaque compatible n’est pas nécessairement montée. Les zones, classes et durabilités restent attachées à chaque slot. Le tableau ne calcule ni score d’armure, ni pénétration, ni probabilité de survie.</div>'
      f'<div class="phase6-grid phase6-summary-grid">{group_cards}</div>'
      + render_filter_form('armor-index',items,threshold)
      + '<div class="phase6-compare-tools"><p>Sélectionnez jusqu’à trois objets du même groupe pour comparer leurs valeurs exportées.</p><button type="button" class="button button--quiet button--xs" data-p6-clear-compare>Effacer la comparaison</button></div>'
      + armor_table(items,'Catalogue défensif Tarkov.dev · 3 modes',threshold,day,True,'armor-catalogue')
      + '<div class="phase6-compare-output" data-p6-compare-output aria-live="polite"></div>'
      + '<p class="phase6-note">Les prix flea sont masqués si le scan est absent, postérieur à l’export ou âgé de plus de sept jours. Le marché a pu changer depuis le 18/11/2026; la date de chaque scan est affichée.</p></section>'
      + '<section class="phase6-section" id="parcours" data-p6-anchor><div class="phase6-section__head"><p class="guide-kicker"><span>REPÈRES</span> Protection par fonction</p><h2>Choisir la bonne fiche</h2><p>La classe d’une plaque ne se substitue pas à celle des protections souples; les rigs et les accessoires de casque ont leurs propres limites.</p></div>'
      '<div class="phase6-grid">'
      '<a class="phase6-card phase6-card--link" href="../../pages/armor/body-armor.html"><p class="phase6-card__eyebrow">A–01</p><h3>Gilets & plaques</h3><p>Porter, insérer, comparer les slots et les zones reportées.</p></a>'
      '<a class="phase6-card phase6-card--link" href="../../pages/armor/helmets.html"><p class="phase6-card__eyebrow">A–02</p><h3>Casques & visières</h3><p>Zones de tête, protections modulaires et casque audio.</p></a>'
      '<a class="phase6-card phase6-card--link" href="../../pages/armor/rigs.html"><p class="phase6-card__eyebrow">A–03</p><h3>Rigs tactiques</h3><p>Grilles de rangement distinctes des protections intégrées.</p></a>'
      '<a class="phase6-card phase6-card--link" href="../../pages/armor/armor-chart.html"><p class="phase6-card__eyebrow">A–04</p><h3>Comparateur</h3><p>Deux ou trois pièces d’un même groupe, sans score de tier list.</p></a>'
      '</div></section>'
      + method_section(verified_at)
    )
    return content


def armor_body(page,data,threshold,verified_at):
    day=date.fromisoformat(data['dateParis'])
    items=[i for i in data['items'] if i.get('group') in ('body-armor','plates')]
    vests=[i for i in items if i.get('group')=='body-armor']
    plates=[i for i in items if i.get('group')=='plates']
    return (
      '<section class="phase6-section" id="gilets" data-p6-filter-root data-p6-anchor aria-labelledby="p6-body-title">'
      '<div class="phase6-section__head"><p class="guide-kicker"><span>A–01 / SLOTS DÉFENSIFS</span> Porteur et insert</p><h2 id="p6-body-title">Un gilet, une couche souple et une plaque</h2>'
      '<p>Le porte-plaques fournit des emplacements; la plaque fournit sa propre protection quand elle est montée. Certains gilets ont aussi des couches souples. Lisez les champs par pièce, sans classe cumulée.</p></div>'
      '<div class="phase6-grid"><div class="phase6-card"><p class="phase6-card__eyebrow">Porteur</p><h3>Emplacements et couches souples</h3><p>Les slots avant, arrière, latéraux ou bassin sont décrits séparément lorsqu’ils sont exportés. Une liste d’IDs compatibles ne prouve pas qu’une plaque est équipée.</p></div>'
      '<div class="phase6-card"><p class="phase6-card__eyebrow">Insert</p><h3>Classe attachée à la pièce</h3><p>La classe d’une plaque n’est pas appliquée automatiquement à tout le gilet. Confirmez les inserts, dimensions et zones dans l’inventaire du jeu.</p></div></div>'
      '<div class="phase6-note"><strong>Filtres :</strong> classe présente sur au moins un slot et poids maximum. Les valeurs de pénalité sont conservées dans leur forme brute exportée; aucune unité supplémentaire n’est supposée.</div>'
      + render_filter_form('body-armor',items,threshold)
      + table_section('gilets-table','PORTEURS','Gilets et armures', 'Protections portées, slots de plaques et couches souples selon l’export; les classes restent par pièce.',vests,threshold,day,False,'p6-vests')
      + table_section('plaques-table','INSERTS','Plaques balistiques', 'Plaques individuelles à comparer à l’emplacement compatible; elles ne sont pas comptées comme montées.',plates,threshold,day,False,'p6-plates')
      + '</section>'
      '<section class="phase6-section" id="liaisons" data-p6-anchor><div class="phase6-section__head"><h2>Compléter l’équipement sans fusionner les slots</h2></div><div class="phase6-grid">'
      '<a class="phase6-card phase6-card--link" href="../../pages/armor/helmets.html"><h3>Casques & visières</h3><p>Comparer zones de tête, accessoires et audio.</p></a>'
      '<a class="phase6-card phase6-card--link" href="../../pages/armor/rigs.html"><h3>Rigs tactiques</h3><p>Voir rangement et protections intégrées séparément.</p></a>'
      '<a class="phase6-card phase6-card--link" href="../../pages/armor/armor-chart.html"><h3>Comparer deux pièces</h3><p>Comparer valeurs et modes de prix.</p></a></div></section>'
      + method_section(verified_at)
    )


def armor_helmets(page,data,threshold,verified_at):
    day=date.fromisoformat(data['dateParis'])
    items=[i for i in data['items'] if i.get('group') in ('headwear','attachment','eyewear')]
    head=[i for i in items if i.get('group')=='headwear']
    accessories=[i for i in items if i.get('group')=='attachment']
    eyewear=[i for i in items if i.get('group')=='eyewear']
    return (
      '<section class="phase6-section" id="headwear" data-p6-filter-root data-p6-anchor aria-labelledby="p6-helmets-title">'
      '<div class="phase6-section__head"><p class="guide-kicker"><span>A–02 / HEADWEAR</span> Coques et accessoires</p><h2 id="p6-helmets-title">Lire la protection de tête par pièce</h2>'
      '<p>Coque, visière, protège-oreilles, masque et accessoire monté peuvent couvrir des zones différentes. Le tableau indique ce que l’export liste; il ne simule ni les collisions, ni l’atténuation sonore en client.</p></div>'
      '<div class="phase6-grid"><div class="phase6-card"><p class="phase6-card__eyebrow">Zones</p><h3>Une classe ne couvre pas toute la tête</h3><p>Inspectez les protections par slot et vérifiez si la visière ou le mod est réellement monté.</p></div>'
      '<div class="phase6-card"><p class="phase6-card__eyebrow">Casque audio</p><h3>Compatibilité rapportée</h3><p>Le filtre casque audio s’appuie sur le champ `blocksHeadset` de l’export. « Inconnu » ne signifie pas compatible.</p></div></div>'
      '<div class="phase6-note"><strong>Lunettes et accessoires :</strong> ces entrées sont listées dans leur groupe exporté; leur présence dans cette page ne signifie pas qu’elles constituent un casque ou une protection balistique.</div>'
      + render_filter_form('helmets',items,threshold)
      + table_section('casques-table','COUVRE-CHEFS','Casques et protections de tête', 'Les zones, classes par slot, durabilités et compatibilités proviennent de l’export du 18/11.',head,threshold,day,False,'p6-headwear')
      + table_section('accessoires-table','MODULARITÉ','Accessoires et pièces rapportés', 'Composants défensifs ou de montage; compatibilité à vérifier sur l’objet dans le client.',accessories,threshold,day,False,'p6-headwear-accessories')
      + table_section('lunettes-table','EYEWEAR','Lunettes et protections oculaires', 'Groupe distinct des casques. Ne pas assimiler une zone eyewear à une protection du crâne.',eyewear,threshold,day,False,'p6-eyewear')
      + '<p class="phase6-note">La wiki communautaire décrit zones de protection, atténuation sonore et modularité; le niveau de bruit et la compatibilité exacts ne sont pas vérifiés dans le build client.</p></section>'
      + method_section(verified_at)
    )


def armor_rigs(page,data,threshold,verified_at):
    day=date.fromisoformat(data['dateParis'])
    items=[i for i in data['items'] if i.get('group')=='rigs']
    return (
      '<section class="phase6-section" id="rigs" data-p6-filter-root data-p6-anchor aria-labelledby="p6-rigs-title">'
      '<div class="phase6-section__head"><p class="guide-kicker"><span>A–03 / PORTAGE</span> Stockage et protection</p><h2 id="p6-rigs-title">Un rig peut ranger sans protéger</h2>'
      '<p>Comparez le poids, la capacité et les dimensions de grille. Si un armored rig comporte des slots de protection, leurs classes restent liées à ces pièces; les cases d’inventaire ne sont pas une classe d’armure.</p></div>'
      '<div class="phase6-grid"><div class="phase6-card"><p class="phase6-card__eyebrow">Rangement</p><h3>Capacité et géométrie</h3><p>La capacité totale et les grilles exportées sont montrées séparément. Les restrictions de forme et la place d’un objet ne sont pas simulées par le comparateur.</p></div>'
      '<div class="phase6-card"><p class="phase6-card__eyebrow">Protection</p><h3>Slots de plaques ou couche souple</h3><p>La classe d’un slot de plaque vide est laissée à la plaque insérée; ne lisez pas la classe d’un seul sous-slot comme celle de tout le rig.</p></div></div>'
      '<div class="phase6-note"><strong>Tri :</strong> poids ou capacité numérique quand le champ existe. Les cases aux formes différentes ne sont pas équivalentes; le tri ne constitue pas une recommandation de kit.</div>'
      + render_filter_form('rigs',items,threshold)
      + armor_table(items,'Rigs tactiques · capacité et slots',threshold,day,False,'p6-rigs-table')
      + '<p class="phase6-note">Le snapshot inclut 105 entrées du groupe « rigs ». La wiki communautaire indique que certains chest rigs reçoivent des plaques; l’export et le client restent les références de compatibilité.</p></section>'
      + method_section(verified_at)
    )


def item_option(item,threshold,day):
    stats=record_stats(item)
    name=item.get('nameFr') or item.get('nameEn') or item['id']
    classes=', '.join(class_text(stats))
    zones=', '.join(dict.fromkeys(zone_label(z) for z in (stats.get('zones') or []))) or 'Zones non listées'
    prices={m:market_price(item,m,day,threshold) for m in MODES}
    attrs={
      'data-p6-option':'','value':item['id'],'data-name':name,'data-group':item.get('group') or 'unknown',
      'data-class':classes,'data-material':slot_materials(stats),'data-durability':durability_text(stats),
      'data-zones':zones,'data-weight':str(item.get('weight') if item.get('weight') is not None else ''),
      'data-capacity':str(stats.get('capacity') if stats.get('capacity') is not None else ''),
      'data-penalties':penalties_text(stats),'data-link':item.get('link') or '',
    }
    for mode, state in prices.items():
        attrs[f'data-price-{mode}']=str(state['value']) if state['fresh'] else ''
        attrs[f'data-price-label-{mode}']=state['label']
    attr_text=' '.join(f'{k}="{esc(v)}"' for k,v in attrs.items())
    return f'<option {attr_text}>{esc(name)} · {esc(item["id"][:8])}</option>'


def armor_chart(page,data,threshold,verified_at):
    day=date.fromisoformat(data['dateParis'])
    items=data['items']
    grouped=Counter(i.get('group') or 'unknown' for i in items)
    options=''.join(f'<optgroup label="{esc(group_label(group))}">'+''.join(item_option(i,threshold,day) for i in items if (i.get('group') or 'unknown')==group)+'</optgroup>' for group in sorted(grouped))
    groups=''.join(f'<option value="{esc(group)}">{esc(group_label(group))} · {count}</option>' for group,count in sorted(grouped.items()))
    return (
      '<section class="phase6-section" id="comparateur" data-p6-anchor aria-labelledby="p6-chart-title">'
      '<div class="phase6-section__head"><p class="guide-kicker"><span>A–04 / COMPARATEUR</span> Par groupe et ID</p><h2 id="p6-chart-title">Comparer deux ou trois pièces</h2>'
      '<p>Choisissez des objets du même groupe. Les barres visualisent seulement l’échelle numérique relative des objets sélectionnés; elles ne classent pas une armure et ne promettent pas une protection supérieure.</p></div>'
      '<div class="phase6-note"><strong>Calcul :</strong> aucun score additionné. Les classes et durabilités restent par slot; les prix flea sont ceux du mode choisi et seuls les scans de moins de sept jours au moment de l’export sont utilisables.</div>'
      '<form class="phase6-toolbar phase6-chart-form" data-p6-chart-form hidden>'
      '<label class="phase6-control">Groupe<select data-p6-chart-group>'+groups+'</select></label>'
      '<label class="phase6-control">Objet A<select data-p6-chart-a><option value="">Choisir une pièce</option></select></label>'
      '<label class="phase6-control">Objet B<select data-p6-chart-b><option value="">Choisir une pièce</option></select></label>'
      '<label class="phase6-control">Objet C (facultatif)<select data-p6-chart-c><option value="">Aucun</option></select></label>'
      '<label class="phase6-control">Mode de prix<select data-p6-chart-mode><option value="regular">PvP permanent</option><option value="pve">PvE Zone</option><option value="pvp-season">PvP Seasonal</option></select></label>'
      '<button type="reset" class="button button--quiet button--xs">Réinitialiser</button></form>'
      '<select class="phase6-option-source" data-p6-option-source aria-label="Données statiques des objets" hidden>'+options+'</select>'
      '<div class="phase6-compare-output" data-p6-chart-output aria-live="polite"><p class="phase6-empty">Activez JavaScript pour construire la comparaison; les tableaux complets, valeurs et IDs sont aussi disponibles dans <a href="../../pages/armor/">le catalogue Armures</a>.</p></div>'
      '<noscript><p class="phase6-note">Le comparateur côte à côte nécessite JavaScript. Le catalogue statique conserve les champs exportés et reste consultable sans interaction.</p></noscript></section>'
      '<section class="phase6-section" id="lecture" data-p6-anchor><div class="phase6-section__head"><h2>À quoi correspondent les barres ?</h2><p>Pour le poids et la capacité, la barre est proportionnelle au maximum parmi les objets sélectionnés. Elle n’implique pas que plus lourd ou plus grand soit préférable. Les classes n’additionnent jamais les slots.</p></div></section>'
      + method_section(verified_at)
    )


def boss_map_anchor(map_name, root):
    if map_name not in MAP_ROUTES:
        return esc(map_name)
    return f'<a href="{root}pages/maps/{esc(MAP_ROUTES[map_name])}">{esc(map_name)}</a>'


def boss_mode_tabs(mode_notes, prefix='boss'):
    names={'regular':'PvP permanent','pve':'PvE Zone','pvp-season':'PvP Seasonal'}
    tabs=''.join(f'<button type="button" role="tab" id="{prefix}-tab-{m}" aria-controls="{prefix}-panel" aria-selected="{str(i==0).lower()}" tabindex="{0 if i==0 else -1}" data-p6-mode-tab="{m}" data-note="{esc(mode_notes.get(m,"Aucune note spécifique à ce mode n’a été vérifiée."))}">{label}</button>' for i,(m,label) in enumerate(names.items()))
    fallback=''.join(f'<details class="phase6-mode-detail"'+(' open' if i==0 else '')+f'><summary>{label}</summary><p>{esc(mode_notes.get(m,"Aucune note spécifique à ce mode n’a été vérifiée."))}</p></details>' for i,(m,label) in enumerate(names.items()))
    panel_text=esc(mode_notes.get('regular','Aucune note spécifique à ce mode n’a été vérifiée.'))
    return (
      f'<div class="phase6-mode-tabs" role="tablist" aria-label="Notes par mode" data-p6-mode-tabs hidden>{tabs}</div>'
      f'<div id="{prefix}-panel" class="phase6-mode-panel" role="tabpanel" aria-labelledby="{prefix}-tab-regular" data-p6-mode-panel="regular" hidden><p data-p6-mode-text>{panel_text}</p></div>'
      f'<div class="phase6-mode-fallback" data-p6-mode-fallback><p class="phase6-muted">Notes communautaires / officielles séparées par mode :</p>{fallback}</div>'
    )


def boss_hub(page, data, root):
    profiles=data['bossProfiles']
    maps=sorted({m for p in profiles for m in p.get('maps',[])},key=norm)
    map_options=''.join(f'<option value="{esc(norm(m))}">{esc(m)}</option>' for m in maps)
    table_rows=[]
    for p in profiles:
        route=root+p['route']
        map_links=', '.join(boss_map_anchor(m,root) for m in p['maps'])
        note=p['modeNotes'].get('regular','')
        health=p.get('health')
        if p['id']=='the-wedge':
            health_text='Historique wiki 750 HP · BSG a annoncé une baisse, nouveau total inconnu'
        else:
            health_text=f'{health["total"]} HP · wiki, non vérifié' if health else 'Non repris'
        row_search=norm(' '.join([p['label'],p.get('group',''),p.get('faction',''),*p['maps']]))
        table_rows.append(
          f'<tr data-p6-boss-row data-search="{esc(row_search)}" data-maps="{esc("|".join(norm(m) for m in p["maps"]))}" '
          f'data-note-regular="{esc(p["modeNotes"].get("regular",""))}" data-note-pve="{esc(p["modeNotes"].get("pve",""))}" data-note-pvp-season="{esc(p["modeNotes"].get("pvp-season",""))}">'
          f'<th scope="row"><a href="{esc(route)}">{esc(p["label"])}</a><span class="phase6-muted">{esc(p.get("group",""))}</span></th>'
          f'<td>{map_links}</td><td>{esc(p.get("faction",""))}</td><td>{esc(p.get("escorts",""))}</td>'
          f'<td data-p6-boss-note>{esc(note)}</td><td>{esc(health_text)}</td></tr>'
        )
    grouped=[]
    for map_name in maps:
        matching=[p for p in profiles if map_name in p['maps']]
        cards=''.join(f'<li data-p6-boss-card data-search="{esc(norm(" ".join([p["label"],p.get("group",""),*p["maps"]])))}" data-maps="{esc("|".join(norm(m) for m in p["maps"]))}"><a href="{esc(root+p["route"])}"><strong>{esc(p["label"])}</strong><small>{esc(p.get("group",""))}</small></a></li>' for p in matching)
        grouped.append(f'<section class="phase6-map-group"><h3>{boss_map_anchor(map_name,root)}</h3><ul class="phase6-boss-list">{cards}</ul></section>')
    mode_notes={'regular':'Les pages de boss communautaires ne garantissent pas un spawn par raid. Les lieux sont indiqués séparément et les notes BSG ne valent que pour le changement cité.',
                'pve':'Ne déduisez pas la présence PvE d’un lieu listé par une wiki ou un export. Vérifiez l’événement et le client.',
                'pvp-season':'Les taux et changements Seasonal ne se généralisent pas au PvP permanent ou au PvE. Les fiches signalent les exceptions officielles.'}
    return (
      '<section class="phase6-section" id="profils" data-p6-anchor aria-labelledby="p6-boss-list-title">'
      '<div class="phase6-section__head"><p class="guide-kicker"><span>B–00 / INDEX DES RENCONTRES</span> 15 profils</p><h2 id="p6-boss-list-title">Comparer les profils par lieu et par mode</h2>'
      '<p>Les lieux sont des repères de wiki communautaire. Les messages officiels sont datés et limités à leur texte; aucun taux final n’est déduit de la liste des cartes.</p></div>'
      '<div class="phase6-note"><strong>Partisan :</strong> BSG annonce 25 % de chance de base sur quatre cartes, puis une modulation en PvP/Seasonal selon les PMCs à faible karma. <strong>The Wedge :</strong> BSG annonce un affaiblissement le 12 novembre, sans publier de nouvelle valeur HP.</div>'
      '<div class="phase6-boss-controls" data-p6-boss-controls hidden>'
      '<label class="phase6-control">Boss, groupe ou carte<input type="search" data-p6-boss-search autocomplete="off" placeholder="Ex. Woods, Killa, Labyrinth"></label>'
      '<label class="phase6-control">Lieu<select data-p6-boss-map><option value="">Tous les lieux</option>'+map_options+'</select></label>'
      '<div class="phase6-mode-tabs" role="tablist" aria-label="Mode de référence" data-p6-mode-tabs hidden>'+''.join(f'<button type="button" role="tab" id="boss-hub-tab-{m}" aria-controls="boss-hub-panel" aria-selected="{str(i==0).lower()}" tabindex="{0 if i==0 else -1}" data-p6-mode-tab="{m}" data-note="{esc(mode_notes.get(m,"Aucune note vérifiée."))}">{label}</button>' for i,(m,label) in enumerate(MODES.items()))+'</div></div>'
      '<div id="boss-hub-panel" class="phase6-mode-panel" role="tabpanel" aria-labelledby="boss-hub-tab-regular" data-p6-mode-panel="regular" hidden><p data-p6-mode-text>'+esc(mode_notes['regular'])+'</p></div>'
      '<div class="phase6-mode-fallback" data-p6-mode-fallback><p class="phase6-muted">Consulter les limites des trois modes :</p>'+''.join(f'<details class="phase6-mode-detail"'+(' open' if i==0 else '')+f'><summary>{label}</summary><p>{esc(mode_notes[m])}</p></details>' for i,(m,label) in enumerate(MODES.items()))+'</div>'
      '<p class="phase6-result-count" role="status" aria-live="polite" data-p6-boss-count>15 profils</p>'
      '<div class="phase6-table-wrap" role="region" aria-label="Comparaison des profils de boss, défilement horizontal" tabindex="0"><table class="phase6-table phase6-boss-table"><caption>Profils communautaires; la colonne de mode se met à jour après activation des commandes.</caption><thead><tr><th scope="col">Boss / groupe</th><th scope="col">Lieux rapportés</th><th scope="col">Faction rapportée</th><th scope="col">Gardes</th><th scope="col">Note du mode</th><th scope="col">Santé wiki</th></tr></thead><tbody>'+''.join(table_rows)+'</tbody></table></div>'
      '<div class="phase6-section__head"><h3>Grille par lieu</h3><p>Un boss peut être associé à plusieurs cartes; le lien ouvre le profil complet et la carte locale lorsqu’elle existe.</p></div>'
      '<div class="phase6-map-grid">'+''.join(grouped)+'</div>'
      '<section class="phase6-section" id="annonces" data-p6-anchor aria-labelledby="p6-boss-announcements-title"><div class="phase6-section__head"><p class="guide-kicker"><span>BSG / NOTES DATÉES</span> Source primaire</p><h3 id="p6-boss-announcements-title">Annonces BSG récentes</h3><p>Repères limités aux messages publiés; les notes originales indiquent le détail et la portée par mode.</p></div>'
      '<div class="phase6-grid"><div class="phase6-card"><p class="phase6-card__eyebrow">Annonce BSG · 9 octobre</p><h3>Partisan</h3><p>Chance de base de 25 % sur quatre cartes; chance finale modulée en PvP/Seasonal par la présence de PMCs à faible karma.</p><a href="'+esc(root+'pages/bosses/partisan.html')+'">Ouvrir le profil Partisan</a></div>'
      '<div class="phase6-card"><p class="phase6-card__eyebrow">Annonce BSG · 12 novembre</p><h3>The Wedge</h3><p>Réaction, précision et santé abaissées avec les gardes dans tous les modes; la note ne publie aucun nouveau total.</p><a href="'+esc(root+'pages/bosses/the-wedge.html')+'">Ouvrir le profil The Wedge</a></div></div></section>'
      '<noscript><p class="phase6-note">Le filtrage et les onglets demandent JavaScript. L’index complet, les liens et les limites par mode restent visibles ci-dessus.</p></noscript></section>'
      + method_section(data['verifiedAt'])
    )


def quest_link(profile, sources, root):
    # Link to the community source's quest section without inventing a named quest or reward.
    ignored={'bsg-partisan-2026-10','bsg-zryachiy-2026-10','wiki-bosses','wiki-labyrinth','wiki-icebreaker'}
    key=next((k for k in profile.get('sources',[]) if k not in ignored and k in sources and sources[k].get('type')=='wiki'),None)
    if not key:
        return '<p class="phase6-muted">Aucun renvoi de quête n’a été vérifié pour ce profil.</p>'
    url=sources[key]['url'].rstrip('/')+'#Quests'
    link = external_link(url, 'Ouvrir la section des tâches de la source communautaire', ' target="_blank" rel="noopener noreferrer"')
    return f'<p>Les tâches éventuelles sont à contrôler dans le client. {link}</p>'


def boss_profile(profile, sources, root):
    maps=''.join(f'<a class="phase6-chip" href="{root}pages/maps/{esc(MAP_ROUTES[m])}">{esc(m)}</a>' if m in MAP_ROUTES else f'<span class="phase6-chip">{esc(m)}</span>' for m in profile.get('maps',[]))
    locations=''.join(f'<article class="phase6-card"><p class="phase6-card__eyebrow">{boss_map_anchor(loc["map"],root)}</p><p>{esc(loc["detail"])}</p></article>' for loc in profile.get('locations',[]))
    tactics=''.join(f'<li>{esc(text)}</li>' for text in profile.get('tactics',[]))
    official=''
    if profile.get('officialNotes'):
        official='<section class="phase6-section" id="annonces" data-p6-anchor><div class="phase6-section__head"><p class="guide-kicker"><span>BSG / NOTE DATÉE</span> Fait limité au message</p><h2>Changements officiellement annoncés</h2></div><div class="phase6-grid">'
        for note in profile['officialNotes']:
            record=sources.get(note['key'])
            label=record.get('titre',note['key']) if record else note['key']
            official+=f'<article class="phase6-card"><p class="phase6-card__eyebrow">{esc(label)}</p><p>{esc(note["text"])}</p></article>'
        official+='</div><p class="phase6-note">Une annonce technique n’indique pas que le boss sera présent dans votre raid ni que ses autres caractéristiques sont inchangées.</p></section>'
    health=''
    if profile.get('health'):
        h=profile['health']
        health=(f'<section class="phase6-section" id="sante" data-p6-anchor><div class="phase6-section__head"><p class="guide-kicker"><span>WIKI / VALEUR RAPPORTÉE</span> Pas un relevé client</p><h2>Santé communautaire rapportée</h2>'
                f'<p>{esc(h.get("label","Valeur transcrite d’une page communautaire; non vérifiée en client."))}</p></div><div class="phase6-card phase6-health-card"><p class="phase6-card__eyebrow">Total indiqué dans la source communautaire</p><strong>{esc(h["total"])} HP</strong><p>Cette valeur n’est pas présentée comme un total actuel certifié par BSG.</p></div></section>')
    mode_notes=profile.get('modeNotes') or {}
    modes=boss_mode_tabs(mode_notes,'boss-profile')
    gallery=gallery_html(profile.get('gallery') or [])
    return (
      '<section class="phase6-section" id="profil" data-p6-anchor aria-labelledby="p6-profile-title">'
      f'<div class="phase6-section__head"><p class="guide-kicker"><span>{esc(profile["code"])} / PROFIL DE BOSS</span> {esc(profile.get("group",""))}</p>'
      f'<h2 id="p6-profile-title">{esc(profile["label"])} : repères et niveau de preuve</h2><p>{esc(profile["lead"])}</p></div>'
      '<div class="phase6-profile-hero"><div class="phase6-card phase6-profile-facts"><p class="phase6-card__eyebrow">Fiche communautaire · points à vérifier en raid</p>'
      f'<dl><dt>Groupe</dt><dd>{esc(profile.get("group",""))}</dd><dt>Faction</dt><dd>{esc(profile.get("faction",""))}</dd>'
      f'<dt>Gardes rapportés</dt><dd>{esc(profile.get("escorts",""))}</dd><dt>Équipement rapporté</dt><dd>{esc(profile.get("signature",""))}</dd>'
      f'<dt>Rôle décrit</dt><dd>{esc(profile.get("role",""))}</dd></dl><div class="phase6-map-chips" aria-label="Lieux rapportés">{maps}</div></div>'
      '<div class="phase6-card phase6-profile-modes"><p class="phase6-card__eyebrow">Notes par mode</p><h3>Ne pas transposer les taux</h3>'+modes+'</div></div>'
      '<section class="phase6-subsection" id="lieux" data-p6-anchor><div class="phase6-section__head"><h3>Lieux rapportés</h3><p>Repères de sources communautaires, pas des points de spawn garantis.</p></div><div class="phase6-grid">'+locations+'</div></section>'
      '<section class="phase6-subsection" id="approche" data-p6-anchor><div class="phase6-section__head"><p class="guide-kicker"><span>PRUDENCE</span> Pas une route garantie</p><h3>Repères avant l’engagement</h3><p>Conseils généraux de couverture et de vérification, pas un script d’IA testé.</p></div>'
      f'<ol class="phase6-tactics">{tactics}</ol><div class="phase6-card"><p class="phase6-card__eyebrow">Progression / quête</p><h3>Vérifier les tâches associées</h3>{quest_link(profile,sources,root)}</div>{gallery}</section>'
      + health + official + '</section>'
    )


def nav_pages(page, phase_data):
    ptype=page.get('type') or 'boss-profile'
    if ptype.startswith('armor-') or ptype=='armor-chart':
        return phase_data['armorPages']
    return [phase_data['bossHub'],*phase_data['bossProfiles']]


def render_page_nav(page, phase_data, root):
    pages=nav_pages(page,phase_data)
    current=page['route']
    rows=[]
    for p in pages:
        route=p['route']
        rows.append(f'<li><a href="{esc(root+route)}" class="phase6-rail-link"'+(' aria-current="page"' if route==current else '')+f'>{esc(p["label"])}<small>{esc(p.get("code",""))}</small></a></li>')
    return ''.join(rows)


def canonical_is_public(base):
    return seo_base_is_public(base)


def render_page(page, phase_data, snapshot, sources, base, patch, compact):
    template=(ROOT/TEMPLATE).read_text(encoding='utf-8')
    route=page['route']
    file=page['file']
    root='../'*(len(PurePosixPath(file).parts)-1)
    ptype=page.get('type') or 'boss-profile'
    gallery=page.get('gallery') or []
    hero_image=page.get('image') or (gallery[0]['src'] if gallery else 'images/bosses/bosses-hub.jpg')
    hero_alt=page.get('imageAlt') or (gallery[0]['alt'] if gallery else 'Illustration originale d’ambiance, sans représentation d’un boss précis.')
    hero_caption=page.get('imageCaption') or (gallery[0]['caption'] if gallery else 'Illustration d’ambiance originale · pas une capture du jeu')
    verified_at=phase_data['verifiedAt']
    dt=datetime.fromisoformat(verified_at)
    if dt.tzinfo is None:
        dt=dt.replace(tzinfo=ZoneInfo('Europe/Paris'))
    date_short=fmt_short(dt.astimezone(ZoneInfo('Europe/Paris')).date())
    date_long=fmt_day(dt.astimezone(ZoneInfo('Europe/Paris')).date())
    parent_is_armor=ptype.startswith('armor-') or ptype=='armor-chart'
    parent_url=root+('pages/armor/' if parent_is_armor else 'pages/bosses/')
    parent_label='Armures' if parent_is_armor else 'Boss'
    threshold=int(read_json('data/phase5.json').get('thresholdFleaDays',7))
    if ptype=='armor-index':
        content=armor_index(page,snapshot,threshold,verified_at)
        quick=quick_links([('catalogue','Catalogue','423 entrées'),('parcours','Parcours','Choisir une fiche'),('methode','Méthode','Prix et limites')])
        primary_anchor,primary_label,secondary_anchor,secondary_label='catalogue','Filtrer les armures','methode','Méthode & limites'
    elif ptype=='armor-body':
        content=armor_body(page,snapshot,threshold,verified_at)
        quick=quick_links([('gilets','Porteurs','Gilets'),('plaques-table','Inserts','Plaques'),('methode','Méthode','Limites')])
        primary_anchor,primary_label,secondary_anchor,secondary_label='gilets','Comparer les pièces','methode','Méthode & limites'
    elif ptype=='armor-helmets':
        content=armor_helmets(page,snapshot,threshold,verified_at)
        quick=quick_links([('casques-table','Casques','Headwear'),('accessoires-table','Mods','Accessoires'),('lunettes-table','Eye','Lunettes')])
        primary_anchor,primary_label,secondary_anchor,secondary_label='casques-table','Lire les zones','methode','Méthode & limites'
    elif ptype=='armor-rigs':
        content=armor_rigs(page,snapshot,threshold,verified_at)
        quick=quick_links([('rigs','Portage','Grilles'),('methode','Méthode','Limites'),('sources','Sources','Références')])
        primary_anchor,primary_label,secondary_anchor,secondary_label='rigs','Trier les rigs','methode','Méthode & limites'
    elif ptype=='armor-chart':
        content=armor_chart(page,snapshot,threshold,verified_at)
        quick=quick_links([('comparateur','Comparer','Deux pièces'),('lecture','Lire les barres','Échelle'),('sources','Sources','Références')])
        primary_anchor,primary_label,secondary_anchor,secondary_label='comparateur','Lancer le comparateur','lecture','Lire les barres'
    elif ptype=='boss-index':
        content=boss_hub(page,phase_data,root)
        quick=quick_links([('profils','Profils','15 boss'),('annonces','Annonces','BSG datées'),('methode','Méthode','Limites')])
        primary_anchor,primary_label,secondary_anchor,secondary_label='profils','Comparer les profils','methode','Méthode & limites'
    else:
        content=boss_profile(page,sources,root)
        quick=quick_links([('profil','Profil','Repères'),('lieux','Lieux','Cartes'),('approche','Avant le raid','Prudence')])
        primary_anchor,primary_label,secondary_anchor,secondary_label='profil','Lire le profil','sources','Sources & limites'
    # Keep page-level research summary visible even when all JavaScript is unavailable.
    source_html=source_list(page.get('sources',[]),sources)
    next_obj=page.get('next') or {}
    if next_obj:
        next_url=root+next_obj['url']; next_label=next_obj['label']; next_blurb=next_obj['blurb']
    elif ptype=='boss-profile':
        next_url=root+'pages/bosses/'; next_label='Index des boss'; next_blurb='Revenir à la comparaison par lieu et par mode.'
    else:
        next_url=root+'pages/bosses/'; next_label='Profils de boss'; next_blurb='Ouvrir les rencontres et changements BSG datés.'
    public_canonical=canonical_is_public(base)
    canonical=urljoin(base,route) if public_canonical else None
    og_image=urljoin(base,hero_image)
    schema={
        '@context':'https://schema.org','@type':'Article','headline':page['seoTitle'],
        'description':page['description'],'dateModified':verified_at,'inLanguage':'fr-FR',
        'image':og_image,'author':{'@type':'Organization','name':'Tarkov Ultimate Guide'},
        'publisher':{'@type':'Organization','name':'Tarkov Ultimate Guide'},
    }
    if canonical:
        schema['mainEntityOfPage']={'@type':'WebPage','@id':canonical}
        schema['url']=canonical
    slots={
      'DESCRIPTION':esc(page['description']),'SEO_TITLE':esc(page['seoTitle']),
      'CANONICAL_LINK':f'<link rel="canonical" href="{esc(canonical)}">' if canonical else '',
      'OG_URL_META':f'<meta property="og:url" content="{esc(canonical)}">' if canonical else '',
      'OG_IMAGE':esc(og_image),'IMAGE_ALT':esc(hero_alt),'VERIFIED_AT':esc(verified_at),
      'JSON_LD':compact(schema).replace('<',r'\\u003c'),
      'ROOT':esc(root),'IMAGE':esc(hero_image),'PAGE_TYPE':esc(ptype),
      'NAV_ARMOR_CURRENT':' aria-current="page"' if parent_is_armor else '',
      'NAV_BOSSES_CURRENT':' aria-current="page"' if not parent_is_armor else '',
      'PATCH':esc(patch),'PARENT_URL':esc(parent_url),'PARENT_LABEL':esc(parent_label),
      'LABEL':esc(page['label']),'VERIFIED_DAY':dt.date().isoformat(),'DATE_SHORT':date_short,'DATE_LONG':date_long,
      'CODE':esc(page['code']),'HEADING':esc(page['heading']),'LEAD':esc(page['lead']),'IMAGE_CAPTION':esc(hero_caption),
      'PRIMARY_ANCHOR':primary_anchor,'PRIMARY_LABEL':esc(primary_label),'SECONDARY_ANCHOR':secondary_anchor,'SECONDARY_LABEL':esc(secondary_label),
      'QUICK':quick,'PAGE_NAV':render_page_nav(page,phase_data,root),'CONTENT':content,
      'SOURCE_CODE':esc(page['code']),'SOURCE_LIST':source_html,
      'NEXT_LABEL':esc(next_label),'NEXT_BLURB':esc(next_blurb),'NEXT_URL':esc(next_url),
    }
    for key,value in slots.items():
        template=template.replace(f'[[{key}]]',str(value))
    if re.search(r'\[\[[A-Z_]+\]\]',template):
        missing=sorted(set(re.findall(r'\[\[([A-Z_]+)\]\]',template)))
        raise ValueError(f'Placeholders non remplacés dans {file}: {missing}')
    if not (ROOT/hero_image).is_file():
        raise ValueError(f'Image hero absente pour {route}: {hero_image}')
    return template


def search_records(phase_data,snapshot,threshold):
    records=[]
    for page in [*phase_data['armorPages'],phase_data['bossHub'],*phase_data['bossProfiles']]:
        tag='Armures' if page['file'].startswith('pages/armor/') else 'Boss'
        keywords=[page.get('label',''),page.get('type',''),*page.get('maps',[]),*page.get('sources',[])]
        records.append({'title':page['label'],'href':page['route'],'tag':tag,'summary':page['description'],'keywords':keywords})
    day=date.fromisoformat(snapshot['dateParis'])
    for item in snapshot['items']:
        stats=record_stats(item)
        name=item.get('nameFr') or item.get('nameEn') or item['id']
        classes=','.join(slot_classes(stats))
        record={'title':name,'href':f'pages/armor/#{"p6-item-"+item["id"]}','tag':group_label(item.get('group')),
                'summary':f'{group_label(item.get("group"))} · ID {item["id"]} · classe par slot {classes or "non indiquée"} · export {day.strftime("%d.%m.%Y")}',
                'keywords':[item['id'],item.get('nameEn',''),item.get('shortNameFr',''),item.get('shortNameEn',''),item.get('group',''),'PvP permanent','PvE Zone','PvP Seasonal']}
        records.append(record)
    return records


def build_phase6(base, patch, compact):
    phase_data=read_json(DATA)
    snapshot=read_json(phase_data['armorSnapshot'])
    verify_snapshot(snapshot)
    sources=read_json('docs/sources.json')['sources']
    pages=[*phase_data['armorPages'],phase_data['bossHub'],*phase_data['bossProfiles']]
    if len(pages)!=21 or len({p['file'] for p in pages})!=21:
        raise ValueError(f'PHASE_6 doit produire exactement 21 routes uniques, reçu {len(pages)}')
    output={page['file']:render_page(page,phase_data,snapshot,sources,base,patch,compact) for page in pages}
    verified=datetime.fromisoformat(phase_data['verifiedAt']).astimezone(ZoneInfo('Europe/Paris'))
    threshold=int(read_json('data/phase5.json').get('thresholdFleaDays',7))
    return output,search_records(phase_data,snapshot,threshold),verified


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--write-snapshot',action='store_true',help='créer le snapshot depuis les trois exports locaux')
    cli.add_argument('--check-snapshot',action='store_true',help='comparer le snapshot aux exports locaux sans écrire')
    args=cli.parse_args()
    if args.write_snapshot:
        write_snapshot(); return
    snapshot=read_json(read_json(DATA)['armorSnapshot'])
    if args.check_snapshot:
        verify_snapshot(snapshot)
        print('Snapshot Phase 6 conforme aux trois exports et au manifeste.')
    else:
        print(f'{len(read_json(DATA)["armorPages"])+1+len(read_json(DATA)["bossProfiles"])} routes configurées; elles sont construites par scripts/build_home.py.')

if __name__=='__main__':
    main()
