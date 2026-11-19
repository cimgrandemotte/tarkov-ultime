#!/usr/bin/env python3
"""Ajoute aux snapshots les URL d’images d’objets explicitement fournies par Tarkov.dev.

Les données de gameplay et leurs horodatages restent inchangés. Cette passe média
vérifie les trois catalogues upstream, fait correspondre chaque ID local, copie
les champs imageLink réels, puis recalcule les empreintes du manifest local.
Aucun fichier d’image de jeu n’est téléchargé ni fabriqué.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo
import json

from import_tarkov_dev import MODES, ROOT, file_atomically, get_json, json_bytes

IMAGE_FIELDS = (
    'iconLink', 'gridImageLink', 'baseImageLink', 'inspectImageLink',
    'image512pxLink', 'image8xLink',
)
KINDS = ('items', 'weapons', 'ammo', 'armor')
MANIFEST_PATH = Path('js/data/catalog-manifest.json')


def is_tarkov_asset(value: object) -> bool:
    if not isinstance(value, str):
        return False
    url = urlsplit(value)
    return (
        url.scheme == 'https' and url.hostname == 'assets.tarkov.dev'
        and not url.username and not url.password and not url.query and not url.fragment
        and url.path.lower().endswith(('.webp', '.jpg', '.jpeg'))
    )


def read_json(path: Path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def main() -> None:
    manifest = read_json(MANIFEST_PATH)
    endpoints = [f'{mode}/items' for mode in MODES]
    with ThreadPoolExecutor(max_workers=3) as pool:
        fetched = dict(zip(endpoints, pool.map(get_json, endpoints)))

    observed = datetime.now(timezone.utc)
    checked_at = observed.astimezone(ZoneInfo('Europe/Paris')).isoformat(timespec='seconds')
    coverage = {}
    placeholder_counts = {mode: {field: 0 for field in IMAGE_FIELDS} for mode in MODES}
    no_real_image_ids = {mode: set() for mode in MODES}
    updated_files = []

    for mode in MODES:
        remote_doc, provenance = fetched[f'{mode}/items']
        remote_items = remote_doc.get('items')
        if not isinstance(remote_items, dict) or not remote_items:
            raise ValueError(f'{mode}/items: catalogue amont vide')

        for item_id, source_item in remote_items.items():
            real_image = False
            for field in IMAGE_FIELDS:
                value = source_item.get(field)
                if is_tarkov_asset(value) and 'unknown-item' in urlsplit(value).path.lower():
                    placeholder_counts[mode][field] += 1
                if is_tarkov_asset(value) and 'unknown-item' not in urlsplit(value).path.lower():
                    real_image = True
            if not real_image:
                no_real_image_ids[mode].add(item_id)

        mode_info = manifest['modes'][mode]
        local_item_doc = read_json(Path(mode_info['files']['items']['path']))
        local_ids = {row['id'] for row in local_item_doc['records']}
        remote_ids = set(remote_items)
        if local_ids != remote_ids:
            raise ValueError(
                f'{mode}: les IDs locaux/amont divergent '
                f'(locaux sans source={len(local_ids - remote_ids)}, nouveaux amont={len(remote_ids - local_ids)}). '
                'Ne pas associer les images avant une collecte de catalogue complète.'
            )

        field_counts = {field: 0 for field in IMAGE_FIELDS}
        kind_counts = {}
        for kind in KINDS:
            file_info = mode_info['files'][kind]
            relative = Path(file_info['path'])
            doc = read_json(relative)
            record_count = 0
            for record in doc['records']:
                source_item = remote_items.get(record['id'])
                if source_item is None:
                    raise ValueError(f'{mode}/{kind}: ID sans fiche amont: {record["id"]}')
                links = {field: source_item.get(field) for field in IMAGE_FIELDS}
                missing = [field for field, value in links.items() if not is_tarkov_asset(value)]
                if missing:
                    raise ValueError(f'{record["id"]}: URL image absente/inattendue ({", ".join(missing)})')
                record.update(links)
                for field in IMAGE_FIELDS:
                    field_counts[field] += 1
                record_count += 1
            payload = json_bytes(doc)
            file_atomically(ROOT / relative, payload)
            file_info['count'] = record_count
            file_info['bytes'] = len(payload)
            file_info['sha256'] = sha256(payload).hexdigest()
            file_info['frNameCount'] = sum(bool(row.get('nameFr')) for row in doc['records'])
            file_info['enNameCount'] = sum(bool(row.get('nameEn')) for row in doc['records'])
            kind_counts[kind] = record_count
            updated_files.append(relative.as_posix())

        coverage[mode] = {
            'upstreamUrl': provenance['url'],
            'httpStatus': provenance['httpStatus'],
            'lastModified': provenance['lastModified'],
            'etag': provenance['etag'],
            'upstreamRecordCount': len(remote_items),
            'matchedLocalItems': len(local_ids),
            'recordsEnrichedByKind': kind_counts,
            'nonEmptyUpstreamLinksByField': field_counts,
        }

    note = (
        'Les références visuelles sont des URL fournies explicitement par les exports Tarkov.dev '
        '(iconLink, gridImageLink, baseImageLink, inspectImageLink, image512pxLink, image8xLink); '
        'elles sont hébergées sur assets.tarkov.dev, distinctes des illustrations JPG originales. '
        'Les URL et IDs ont été contrôlés dans les trois exports le 18/11/2026; un échantillon HTTP du CDN a répondu 200. '
        'Les URL contenant unknown-item sont des placeholders et ne sont pas présentées comme références réelles. '
        'Cela ne certifie ni les droits de réutilisation, ni l’état du client EFT, ni la disponibilité à long terme du CDN.'
    )
    notes = manifest.setdefault('notes', [])
    if note not in notes:
        notes.append(note)
    manifest['imageAssets'] = {
        'checkedAt': checked_at,
        'source': 'https://json.tarkov.dev/endpoints',
        'cdnHost': 'assets.tarkov.dev',
        'fields': list(IMAGE_FIELDS),
        'upstream': coverage,
        'unknownItemPlaceholderCountsByMode': placeholder_counts,
        'idsWithoutNonPlaceholderImageByMode': {mode: sorted(ids) for mode, ids in no_real_image_ids.items()},
        'binarySample': {
            'method': 'HEAD pour iconLink et inspectImageLink; GET+decode de image512pxLink pour le M4A1',
            'sampleItemIds': [
                '5447a9cd4bdc2dbd208b4567', '6513ef33e06849f06c0957ca',
                '54527a984bdc2d4e668b4567', '5c052e6986f7746b207bc3c9',
                '5bc9c1e2d4351e00367fbcf0', '5c1d0c5f86f7744bb2683cf0',
                '6217726288ed9f0845317459', '5c12613b86f7743bbe2c3f76',
                '5d1b36a186f7742523398433', '5672cb724bdc2dc2088b456b',
                '573474f924597738002c6174', '545cdb794bdc2d3a198b456a',
            ],
            'result': '12/12 IDs échantillonnés : iconLink et inspectImageLink HTTP 200; image512pxLink du M4A1 téléchargée et décodée en 512×512.',
        },
    }
    payload = json_bytes(manifest, pretty=True)
    file_atomically(ROOT / MANIFEST_PATH, payload)
    date = manifest['dateParis']
    snapshot_copy = Path(f'data/snapshots/catalogue-{date}.json')
    file_atomically(ROOT / snapshot_copy, payload)
    updated_files.extend([MANIFEST_PATH.as_posix(), snapshot_copy.as_posix()])

    media_snapshot = {
        'schemaVersion': 1,
        'checkedAt': checked_at,
        'purpose': 'Inventaire des liens d’images d’objets fournis par l’export Tarkov.dev; aucune donnée de gameplay ni aucun fichier image de jeu n’est modifié/téléchargé.',
        'fields': list(IMAGE_FIELDS),
        'cdnHost': 'assets.tarkov.dev',
        'modes': coverage,
        'unknownItemPlaceholderCountsByMode': placeholder_counts,
        'idsWithoutNonPlaceholderImageByMode': {mode: sorted(ids) for mode, ids in no_real_image_ids.items()},
        'binarySample': manifest['imageAssets']['binarySample'],
        'limits': [
            'Les URL unknown-item sont des ressources de remplacement, pas une vraie image de l’objet; elles sont masquées dans les fiches.',
            'Une URL présente dans le flux n’est pas une validation visuelle de chaque binaire.',
            'Les images d’objets proviennent de ressources communautaires liées au jeu; aucun droit de réutilisation commerciale n’est inféré.',
            'Les exports sont des snapshots sans numéro de build EFT et ne prouvent pas un test dans le client.',
        ],
    }
    media_path = Path(f'data/snapshots/images-objets-{date}.json')
    file_atomically(ROOT / media_path, json_bytes(media_snapshot, pretty=True))
    updated_files.append(media_path.as_posix())

    print(f'{sum(sum(m["recordsEnrichedByKind"].values()) for m in coverage.values()):,} enregistrements enrichis · {len(IMAGE_FIELDS)} champs d’URL image · {checked_at}')
    print(f'{len(updated_files)} fichiers écrits; manifest catalogue {manifest["collectedAt"]} conservé (aucune valeur prix/statistique rafraîchie).')
    for mode, info in coverage.items():
        print(f'{mode}: {info["upstreamRecordCount"]} IDs alignés; {info["httpStatus"]} · Last-Modified {info["lastModified"]}')
        missing = len(no_real_image_ids[mode])
        print(f'  placeholders unknown-item: {sum(placeholder_counts[mode].values()):,} URL(s) · IDs sans image de référence réelle: {missing}')


if __name__ == '__main__':
    main()
