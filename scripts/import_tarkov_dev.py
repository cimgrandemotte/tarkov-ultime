#!/usr/bin/env python3
"""Importe les catalogues publics de Tarkov.dev. Aucune dépendance externe.

Les fichiers JSON servent à documenter Escape from Tarkov, pas à décrire du
matériel réel. Les modes sont séparés et les prix sont des relevés horodatés.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import argparse
import gzip
import json
import re
import tempfile

BASE = 'https://json.tarkov.dev/'
USER_AGENT = 'Tarkov-Ultimate-Guide/0.1 (public catalog research)'
ROOT = Path(__file__).resolve().parents[1]
MODES = {'regular': 'PvP permanent', 'pve': 'PvE Zone officiel', 'pvp-season': 'PvP saisonnier'}
FILE_NAMES = {'items': 'items.json', 'weapons': 'weapons.json', 'ammo': 'ammo.json', 'armor': 'armor.json'}
# La classe publiée est celle de la pièce, pas la classe maximale que pourrait lui donner une plaque.
DEFENSIVE = {
    'ItemPropertiesArmor': 'body-armor',
    'ItemPropertiesHelmet': 'headwear',
    'ItemPropertiesChestRig': 'rigs',
    'ItemPropertiesArmorAttachment': 'attachment',
    'ItemPropertiesGlasses': 'eyewear',
}
WEAPON_GROUPS = {
    'assault-rifle': 'assault-rifles', 'assault-carbine': 'assault-rifles',
    'smg': 'smgs', 'shotgun': 'shotguns', 'marksman-rifle': 'dmrs',
    'sniper-rifle': 'sniper-rifles', 'machinegun': 'lmgs',
    'handgun': 'pistols', 'revolver': 'pistols', 'knife': 'melee',
    'grenade-launcher': 'grenade-launchers', 'rocket-launcher': 'grenade-launchers',
}
GAME_PRICE_FIELDS = ('lastLowPrice', 'avg24hPrice', 'lastScan', 'lastOfferCount', 'minLevelForFlea')
TRADER_FIELDS = ('trader', 'price', 'priceRUB', 'currency', 'minTraderLevel', 'taskUnlock', 'buyLimit')
WEAPON_STATS = (
    'caliber', 'fireModes', 'fireRate', 'ergonomics', 'recoilVertical', 'recoilHorizontal',
    'effectiveDistance', 'sightingRange', 'maxDurability', 'centerOfImpact',
    'defaultPreset', 'defaultWidth', 'defaultHeight', 'defaultWeight', 'defaultErgonomics',
    'defaultRecoilVertical', 'defaultRecoilHorizontal', 'defaultAmmo',
    'allowedAmmo', 'presets', 'slots', 'slashDamage', 'stabDamage', 'hitRadius',
)
AMMO_STATS = (
    'caliber', 'ammoType', 'projectileCount', 'damage', 'penetrationPower', 'armorDamage',
    'fragmentationChance', 'initialSpeed', 'ricochetChance', 'penetrationChance',
    'accuracyModifier', 'recoilModifier', 'heavyBleedModifier', 'lightBleedModifier',
    'stackMaxSize', 'tracer', 'tracerColor', 'durabilityBurnFactor', 'heatFactor',
)
ARMOR_STATS = (
    'class', 'durability', 'material', 'zones', 'armorType', 'armorSlots', 'bluntThroughput',
    'speedPenalty', 'turnPenalty', 'ergoPenalty', 'repairCost', 'blindnessProtection',
    'deafening', 'blocksHeadset', 'blocksEyewear', 'blocksHeadwear', 'capacity', 'grids',
)


def fields(record, keys):
    return {key: record[key] for key in keys if key in record}


def labels(record, fr, en, fields_to_translate=('name', 'shortName')):
    """Garde les langues distinctes ; ne déguise pas une chaîne anglaise en VF."""
    out = {}
    for field in fields_to_translate:
        key = record.get(field)
        english = en.get(key)
        # Quelques valeurs sont déjà des libellés, pas des clés de traduction.
        if english is None and isinstance(key, str) and not re.match(r'^[0-9a-f]{24}\b', key):
            english = key.strip() or None
        out[field + 'En'] = english or None
        out[field + 'Fr'] = fr.get(key) or None
    return out


def get_json(path):
    url = BASE + path
    req = Request(url, headers={
        'User-Agent': USER_AGENT, 'Accept': 'application/json', 'Accept-Encoding': 'gzip',
    })
    with urlopen(req, timeout=25) as response:
        body = response.read()
        if response.headers.get('Content-Encoding') == 'gzip':
            body = gzip.decompress(body)
        result = json.loads(body)
        if not isinstance(result.get('data'), dict) or not result['data']:
            raise ValueError(f'{url}: enveloppe de données vide ou incompatible')
        provenance = {
            'url': url, 'httpStatus': response.status,
            'lastModified': response.headers.get('Last-Modified'), 'etag': response.headers.get('ETag'),
            'bytesDecoded': len(body), 'sha256Decoded': sha256(body).hexdigest(),
        }
        return result['data'], provenance


def normalise(mode, downloads):
    main, fr, en = (downloads[f'{mode}/items{suffix}'][0] for suffix in ('', '_fr', '_en'))
    categories = main['itemCategories']
    result = {kind: [] for kind in FILE_NAMES}
    records = main['items']
    if not isinstance(records, dict) or not records:
        raise ValueError(f'{mode}: catalogue items manquant')
    for item_id, row in sorted(records.items()):
        if row.get('id') != item_id:
            raise ValueError(f'{mode}: identifiant divergent {item_id}')
        p = row.get('properties') or {}
        typ = p.get('propertiesType')
        categories_for_item = row.get('categories') or []
        category = next((categories[c]['normalizedName'] for c in categories_for_item if c in categories), None)
        summary = {
            **fields(row, (
                'id', 'normalizedName', 'types', 'width', 'height', 'weight', 'wikiLink', 'link',
                'iconLink', 'gridImageLink', 'baseImageLink', 'inspectImageLink', 'image512pxLink', 'image8xLink',
            )),
            **labels(row, fr, en),
            'category': category,
        }
        offers = [fields(offer, TRADER_FIELDS) for offer in row.get('buyFromTrader') or []]
        flea = fields(row, GAME_PRICE_FIELDS)
        result['items'].append({
            **summary, 'categoryIds': categories_for_item, 'handbookCategoryIds': row.get('handbookCategories') or [],
            'propertiesType': typ, 'flea': flea,
            **fields(row, ('basePrice', 'updated', 'containsItems', 'stackMaxSize')),
        })
        if typ in ('ItemPropertiesWeapon', 'ItemPropertiesMelee'):
            result['weapons'].append({
                **summary, 'group': WEAPON_GROUPS.get(category), 'propertiesType': typ,
                'signalDevice': 'specialSlot' in (row.get('types') or []) and category == 'grenade-launcher',
                'stats': fields(p, WEAPON_STATS), 'flea': flea, 'buyFromTrader': offers,
            })
        if typ == 'ItemPropertiesAmmo':
            result['ammo'].append({**summary, 'stats': fields(p, AMMO_STATS), 'flea': flea, 'buyFromTrader': offers})
        if typ in DEFENSIVE:
            result['armor'].append({
                **summary, 'propertiesType': typ,
                'group': 'plates' if 'armorPlate' in (row.get('types') or []) else DEFENSIVE[typ],
                'stats': fields(p, ARMOR_STATS), 'flea': flea, 'buyFromTrader': offers,
            })
    for kind, rows in result.items():
        if not rows:
            raise ValueError(f'{mode}: aucun enregistrement pour {kind}; schéma à vérifier')
        if sum(bool(r['nameEn']) for r in rows) / len(rows) < .95:
            raise ValueError(f'{mode}/{kind}: plus de 5 % de libellés anglais non résolus')
    extras = {
        'items': {
            'categories': [{**fields(row, ('id', 'normalizedName', 'parent')), **labels(row, fr, en, ('name',))}
                           for _, row in sorted(categories.items())],
            'handbookCategories': [{**fields(row, ('id', 'normalizedName', 'parent')), **labels(row, fr, en, ('name',))}
                                   for _, row in sorted(main['handbookCategories'].items())],
        },
        'armor': {'materials': [{**row, **labels(row, fr, en, ('name',))} for _, row in sorted(main['armorMaterials'].items())]},
    }
    return result, extras


def map_scope(downloads):
    """Index de repérage pour le plan éditorial, pas un guide d'accès aux raids."""
    modes = {}
    for mode in MODES:
        md, mmeta = downloads[f'{mode}/maps']
        men, emeta = downloads[f'{mode}/maps_en']
        rows = []
        for map_id, row in sorted(md['maps'].items()):
            rows.append({
                'id': map_id, 'slug': row['normalizedName'], 'nameEn': men.get(row['name']),
                **fields(row, ('players', 'raidDuration', 'wiki', 'minPlayerLevel', 'maxPlayerLevel')),
                'extractEntries': len(row.get('extracts') or []),
                'bossEntries': len(row.get('bosses') or []),
            })
        modes[mode] = {'sources': [mmeta['url'], emeta['url']], 'mapRecords': rows, 'mobRecordsCount': len(md['mobs'])}
    return modes


def json_bytes(doc, pretty=False):
    return (json.dumps(doc, ensure_ascii=False, allow_nan=False,
                       indent=2 if pretty else None, separators=None if pretty else (',', ':')) + '\n').encode('utf-8')


def file_atomically(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.import-', delete=False) as temp:
        tmp_path = Path(temp.name)
        temp.write(content)
    try:
        tmp_path.replace(path)
    finally:
        tmp_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Télécharger et valider sans modifier la copie locale')
    args = parser.parse_args()
    paths = [f'{mode}/{endpoint}' for mode in MODES for endpoint in ('items', 'items_fr', 'items_en', 'maps', 'maps_en')]
    paths.insert(0, 'endpoints')
    with ThreadPoolExecutor(max_workers=4) as pool:
        downloads = dict(zip(paths, pool.map(get_json, paths)))
    if not set(MODES).issubset(downloads['endpoints'][0].get('gameModes', [])):
        raise ValueError('Le catalogue des endpoints ne contient plus tous les modes attendus.')
    observed = datetime.now(timezone.utc)
    date = observed.astimezone(ZoneInfo('Europe/Paris')).date().isoformat()
    source_list = {key: value[1] for key, value in downloads.items()}
    manifest = {
        'schemaVersion': 1, 'publisher': 'Tarkov.dev / The Hideout', 'catalogUrl': BASE + 'endpoints',
        'collectedAt': observed.isoformat(timespec='seconds'), 'dateParis': date, 'gameBuild': None,
        'notes': ['Version du jeu non inscrite dans le flux ; base communautaire, pas un export BSG certifié.',
                  'Les prix et stocks diffèrent par mode et changent après la collecte.',
                  'L’apparition d’une carte dans un fichier ne prouve pas l’accès dans ce mode.'],
        'modes': {}, 'upstream': source_list,
    }
    all_files = {}
    for mode, name in MODES.items():
        data, extras = normalise(mode, downloads)
        manifest['modes'][mode] = {'label': name, 'files': {}}
        for kind, filename in FILE_NAMES.items():
            path = (Path('js/data') if mode == 'regular' else Path('js/data') / mode) / filename
            rows = data[kind]
            source = [source_list[f'{mode}/items{suffix}']['url'] for suffix in ('', '_fr', '_en')]
            packed = json_bytes({'schemaVersion': 1, 'kind': kind, 'mode': mode, 'collectedAt': manifest['collectedAt'],
                                 'sources': source, 'records': rows, **extras.get(kind, {})})
            all_files[path] = packed
            manifest['modes'][mode]['files'][kind] = {
                'path': path.as_posix(), 'count': len(rows), 'bytes': len(packed), 'sha256': sha256(packed).hexdigest(),
                'frNameCount': sum(bool(row['nameFr']) for row in rows),
                'enNameCount': sum(bool(row['nameEn']) for row in rows),
            }
        print(f"{mode}: " + ', '.join(f'{len(rows)} {kind}' for kind, rows in data.items()))
    audit = {'schemaVersion': 1, 'collectedAt': manifest['collectedAt'],
             'usage': 'Inventaire technique, y compris variantes d’événement et de niveau ; ne prouve pas l’accès.',
             'modes': map_scope(downloads)}
    all_files[Path(f'data/snapshots/cartes-{date}.json')] = json_bytes(audit, pretty=True)
    all_files[Path('js/data/catalog-manifest.json')] = json_bytes(manifest, pretty=True)
    all_files[Path(f'data/snapshots/catalogue-{date}.json')] = all_files[Path('js/data/catalog-manifest.json')]
    # Les lectures et validations ont toutes réussi avant de remplacer une copie locale.
    if not args.check:
        for path, content in all_files.items():
            file_atomically(ROOT / path, content)
    print(f"{sum(len(data) for data in all_files.values()):,} octets · {'contrôle seulement' if args.check else 'snapshot écrit'}")


if __name__ == '__main__':
    main()
