#!/usr/bin/env python3
"""Génère uniquement le banc d'essai HTML à partir du snapshot local de phase 0."""
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELECTED = {
    '5644bd2b4bdc2d3b4c8b4572': ('ak74n', 'assault', 'Fusil d’assaut', 'AR', '5,45 × 39'),
    '5447a9cd4bdc2dbd208b4567': ('m4a1', 'assault', 'Fusil d’assaut', 'AR', '5,56 × 45'),
    '5926bb2186f7744b1c6c6e60': ('mp5', 'smg', 'Pistolet-mitrailleur', 'SMG', '9 × 19'),
    '59984ab886f7743e98271174': ('vityaz', 'smg', 'Pistolet-mitrailleur', 'SMG', '9 × 19'),
    '56dee2bdd2720bc8328b4567': ('mp153', 'shotgun', 'Fusil à pompe', 'SG', 'Calibre 12'),
    '576165642459773c7a400233': ('saiga12k', 'shotgun', 'Fusil à pompe', 'SG', 'Calibre 12'),
}


def safe_json(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def show(value):
    if value is None:
        return '—'
    return str(value).replace('.', ',')


def run():
    data = json.loads((ROOT / 'js/data/weapons.json').read_text(encoding='utf-8'))
    if data['mode'] != 'regular':
        raise ValueError('La maquette attend le mode PvP permanent.')
    objects = {item['id']: item for item in data['records']}
    rows, samples = [], []
    for item_id, (slug, family, title, code, caliber) in SELECTED.items():
        record = objects[item_id]
        stats = record['stats']
        label = record['shortNameFr'] or record['shortNameEn']
        full = record['nameFr'] or record['nameEn']
        # Ces labels de famille servent à la démo : pas d'offre, prix ou performance réels.
        ergo, cadence = stats.get('ergonomics'), stats.get('fireRate')
        metrics = {'family': title, 'caliber': caliber, 'ergo': ergo, 'cadence': cadence, 'recoil': stats.get('recoilVertical'), 'weight': record.get('weight')}
        samples.append({'id': slug, 'title': label, 'metrics': metrics})
        match = escape(f'{label} {full} {title} {caliber}', quote=True)
        rows.append(f'''<li class="catalogue__row" id="specimen-{slug}" tabindex="-1" data-filter-row data-family="{family}" data-filter-text="{match}" data-sort-label="{escape(label, quote=True)}" data-sort-ergo="{ergo if ergo is not None else ''}" data-sort-cadence="{cadence if cadence is not None else ''}">
                  <div class="catalogue__record"><span class="catalogue__record-code" aria-hidden="true">{code}</span><div><span class="catalogue__name">{escape(label)}</span><span class="catalogue__family">{escape(title)} · {caliber}</span></div></div>
                  <dl class="catalogue__metrics"><div><dt><span aria-hidden="true">Ergo</span><span class="sr-only">Ergonomie</span></dt><dd>{show(ergo)}</dd></div><div><dt><span aria-hidden="true">Cad.</span><span class="sr-only">Cadence en coups par minute</span></dt><dd>{show(cadence)}</dd></div></dl>
                  <button class="catalogue__toggle button button--quiet button--xs" type="button" data-compare-toggle="{slug}" aria-pressed="false" aria-label="Inclure {escape(label, quote=True)} dans la comparaison" hidden><span data-compare-mark aria-hidden="true"></span><span class="catalogue__toggle-copy" aria-hidden="true">Inclure</span></button>
                </li>''')
    config = {'caption': 'Paramètres des objets de base · données du jeu uniquement', 'records': samples,
              'fields': [{'key': k, 'label': v, 'unit': u} for k, v, u in (
                  ('family', 'Famille', None), ('caliber', 'Calibre en jeu', None), ('ergo', 'Ergonomie', None),
                  ('cadence', 'Cadence déclarée', 'c/min'), ('recoil', 'Recul vertical', None), ('weight', 'Poids de l’objet de base', 'kg'))]}
    options = []
    for key, label, start in [('first','Premier raid','S'), ('maps','Cartes','A'), ('gear','Équipement','B')]:
        dropdown = ''.join(f'<option value="{rank}"{" selected" if rank == start else ""}>{rank}</option>' for rank in 'SABCD')
        options.append(f'<label class="field">{label}<select class="field__input tiers__select" aria-label="{label} : choisir le rang" data-tier-item="{key}" data-tier-label="{label}">{dropdown}</select></label>')
    wave = ''.join(f'<i style="--bar-h:{12+(index*index*37+index*7)%84}%;--wave-delay:-{(index%8)*73}ms;--pulse:{490+(index*23)%370}ms"></i>' for index in range(40))
    audio = {'tracks': [{'id': key, 'label': label, 'src': f'../audio/ambient/ambient_{key}.mp3'} for key, label in (
        ('rain','Pluie sur les entrepôts'), ('industrial','Ventilation de la planque'), ('forest','Forêt de nuit'))],
        'cues': [{'id':'click','src':'../audio/ui/ui_click.mp3'}, {'id':'alert','src':'../audio/ui/ui_notification.mp3'}]}
    fields = {'COUNT': str(len(rows)), 'CATALOGUE': '\n                '.join(rows), 'COMPARE': safe_json(config),
              'TIER_CONTROLS': '\n                  '.join(options), 'WAVE': wave, 'AUDIO_MAP': safe_json(audio)}
    html = (ROOT / 'lab/atelier.html.in').read_text(encoding='utf-8')
    for name, value in fields.items():
        html = html.replace(f'[[{name}]]', value)
    (ROOT / 'lab/index.html').write_text(html, encoding='utf-8')
    print(f'Atelier rendu : {len(rows)} références de jeu · lab/index.html')


if __name__ == '__main__':
    run()
