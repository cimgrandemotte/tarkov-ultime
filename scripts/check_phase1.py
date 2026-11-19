#!/usr/bin/env python3
"""Contrôle hors ligne des fichiers, liens et preuves du socle technique."""
import argparse
from hashlib import sha256
from html.parser import HTMLParser
from io import BytesIO
import json
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image

from build_lab import SELECTED
from check_phase0 import load, require, ROOT

CSS = ('main', 'components', 'animations', 'responsive', 'pages/lab')
JS = ('main', 'utils', 'search', 'audio', 'animations',
      'components/tooltip', 'components/modal', 'components/filter',
      'components/comparator', 'components/tierlist', 'components/tabs', 'components/navigation')


class Bench(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.paths = []
        self.described = []
        self.scripts = {}
        self.inline = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if token := a.get('id'):
            require(token not in self.ids, f'id non unique : {token}')
            self.ids.add(token)
        for key in ('for', 'aria-labelledby', 'aria-describedby', 'aria-controls'):
            self.described.extend(a.get(key, '').split())
        for key in ('href', 'src'):
            if a.get(key):
                self.paths.append(a[key])
        if tag == 'img':
            require(bool(a.get('alt')) and a.get('loading') == 'lazy' and a.get('decoding') == 'async', 'image sans alt ou lazy')
            require(a.get('width') and a.get('height'), 'image sans dimensions intrinsèques')
        if tag == 'audio':
            require('autoplay' not in a and a.get('preload') == 'none' and 'controls' in a, 'repli audio actif sans geste')
        if tag == 'script' and a.get('type') == 'application/json':
            self.inline = next((k for k in a if k.startswith('data-')), None)

    def handle_data(self, value):
        if self.inline:
            self.scripts[self.inline] = json.loads(value)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.inline = None


def jpeg_q85(path):
    stream = BytesIO()
    Image.new('RGB', (16, 16)).save(stream, format='JPEG', quality=85)
    stream.seek(0)
    with Image.open(stream) as sample:
        expected = sample.quantization
    with Image.open(path) as photo:
        photo.load()
        require(photo.format == 'JPEG' and photo.quantization == expected, f'JPEG q85 non conforme : {path.name}')
        require(photo.width >= 1300 and photo.height >= 700, f'illustration trop petite : {path.name}')
        return list(photo.size)


def main(skip_state=False):
    for directory, suffix, files in (('css', 'css', CSS), ('js', 'js', JS)):
        for file in files:
            require((ROOT / directory / f'{file}.{suffix}').stat().st_size > 250, f'composant absent : {file}')

    lab = Bench()
    html = (ROOT / 'lab/index.html').read_text(encoding='utf-8')
    lab.feed(html)
    require('name="robots" content="noindex,nofollow"' in html and '[[' not in html, 'atelier indexable ou template non compilé')
    require(set(lab.described) <= lab.ids, 'référence ARIA orpheline')
    for ref in lab.paths + [r['href'] for r in load('lab/search-index.json')['records']]:
        url = urlsplit(ref)
        if url.netloc:
            require(url.scheme == 'https', f'lien externe non HTTPS : {ref}')
        elif url.path:
            require((ROOT / 'lab' / url.path).resolve().is_relative_to(ROOT), f'lien local hors projet : {ref}')
            require((ROOT / 'lab' / url.path).is_file(), f'ressource manquante : {ref}')
        elif url.fragment:
            require(url.fragment in lab.ids, f'ancre manquante : {ref}')

    src = load('js/data/weapons.json')
    require(src['mode'] == 'regular', 'mode de la source incorrect')
    source = {r['id']: r for r in src['records']}
    catalogue = {r['id']: r for r in lab.scripts['data-compare-data']['records']}
    require(len(catalogue) == len(SELECTED), 'catalogue ne correspond pas à la sélection')
    for id_, (slug, _family, _title, _code, _caliber) in SELECTED.items():
        record = source[id_]
        view = catalogue[slug]
        lookup = {'ergo': record['stats']['ergonomics'], 'cadence': record['stats']['fireRate'],
                  'recoil': record['stats']['recoilVertical'], 'weight': record['weight']}
        require(all(view['metrics'][k] == v for k, v in lookup.items()), f'valeurs de démo divergentes : {slug}')

    image_path = ROOT / 'images'
    visual_paths = {f.relative_to(ROOT).as_posix() for f in image_path.glob('ui/design-*.jpg')}
    images = {name: jpeg_q85(ROOT / name) for name in visual_paths}
    require(len(images) == 3, 'le banc d’essai attend trois illustrations')
    require(all(f.suffix == '.jpg' for f in image_path.rglob('*') if f.is_file() and f.name != '.gitkeep'), 'format d’image interdit')
    audio_tags = lab.scripts['data-audio-map']
    tracks = {e['src'].removeprefix('../') for e in audio_tags['tracks'] + audio_tags['cues']}
    media = [t for t in load('audio/manifest.json')['tracks'] if t['file'] in tracks]
    require({t['file'] for t in media} == tracks and len(tracks) == 5 and sum(t['loop'] and t['seconds'] == 60 for t in media) == 3, 'lots MP3 de l’atelier désynchronisés')
    for t in media:
        raw = (ROOT / t['file']).read_bytes()
        require(len(raw) == t['bytes'] and sha256(raw).hexdigest() == t['sha256'] and raw[:3] == b'ID3', f'MP3 altéré : {t["file"]}')
    require(all(f.suffix == '.mp3' for f in (ROOT / 'audio').rglob('*') if f.is_file() and f.name not in {'manifest.json','.gitkeep'}), 'format audio interdit')
    vendor = load('vendor/manifest.json')
    for item in vendor['libraries'].values():
        for file, digest in item['files'].items():
            require(sha256((ROOT / 'vendor' / file).read_bytes()).hexdigest() == digest, f'bibliothèque tierce altérée : {file}')
    for file, item in vendor['fonts'].items():
        require(sha256((ROOT / 'fonts' / file).read_bytes()).hexdigest() == item['sha256'], f'police altérée : {file}')

    qa = load('data/snapshots/validation-phase-1.json')
    require(qa['status'] == 'VALIDE' and all(x['passed'] for x in qa['results']) and len(qa['results']) >= 12, 'tests navigateur non validés')
    require(len(qa['audits']) == 5 and not any(x['violations'] for x in qa['audits']), 'échec axe-core')
    ffx = load('data/snapshots/validation-phase-1-firefox.json')
    require(ffx['status'] == 'VALIDE', 'contre-test Firefox absent')
    colors = load('data/snapshots/contraste-phase-1.json')
    require(len(colors['hero']) == 10 and all(x['lowestRatio'] >= 4.5 for x in colors['hero']), 'contraste photographique insuffisant')
    require(all(x['ratio'] >= x['minimum'] for x in colors['palette']), 'contraste du thème insuffisant')

    if not skip_state:
        state = load('state_machine.json')['instantane']
        workflow = load('workflow.json')
        production = workflow['production']
        require(workflow['etat_global'] == state['etat'] and workflow['phase_active'] == state['phase_active'], 'états divergents')
        require('PHASE_1' in workflow['phases_terminees'], 'phase 1 non clôturée')
        if state['etat'] == 'ATTENTE_CONTINUE' and state['derniere_phase_terminee'] == 'PHASE_1':
            require(workflow['prochaine_phase'] == state['prochaine_phase'] == 'PHASE_2' and state['mot_de_confirmation'] == 'CONTINUE', 'jalon suivant absent')
            require(production['pages_generees'] == 0 and not (ROOT / 'index.html').exists() and not load('js/data/search-index.json')['records'], 'page publique prématurée')
        require({r['fichier'] for r in production['images_creees'] if r['phase'] == 'PHASE_1'} == images.keys(), 'inventaire JPG de l’atelier non synchronisé')
        require({r['fichier'] for r in production['audios_crees'] if r['phase'] == 'PHASE_1'} == tracks, 'inventaire MP3 de l’atelier non synchronisé')
        require(production['ateliers_techniques'][0]['fichier'] == 'lab/index.html', 'maquette non consignée')
    print(f'OK · {len(CSS)} CSS · {len(JS)} modules JS · {len(images)} JPG · {len(tracks)} MP3 · {len(qa["results"])} tests Chromium · Firefox ciblé · contrastes')


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--avant-transition', action='store_true', help='validations techniques sans exiger la clôture de phase')
    main(cli.parse_args().avant_transition)
