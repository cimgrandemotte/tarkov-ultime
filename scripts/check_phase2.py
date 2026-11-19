#!/usr/bin/env python3
"""Vérifie les artefacts de l’accueil, les sources locales et la garde de phase."""
import argparse
from html.parser import HTMLParser
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from check_phase0 import ROOT, load, require
from check_phase1 import jpeg_q85
from build_home import build, DESCRIPTION, absolute_base
from serve_home import PUBLIC_FILES, DIRECTORY_ROUTES

START_HOME = 'index.html'
REPORT = 'data/snapshots/validation-phase-2.json'
FF = 'data/snapshots/validation-phase-2-firefox.json'
CONTRAST = 'data/snapshots/contraste-phase-2.json'


class HomeHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1_count = 0
        self.ids = set()
        self.idrefs = []
        self.media = {}
        self.hrefs = []
        self.inline = {}
        self.working = None
        self.metas = {}
        self.canonical = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        token = a.get('id')
        if token:
            require(token not in self.ids, f'id répété : {token}')
            self.ids.add(token)
        if tag == 'h1':
            self.h1_count += 1
        for key in ('for', 'aria-controls', 'aria-labelledby', 'aria-describedby'):
            self.idrefs.extend(a.get(key, '').split())
        self.hrefs.extend((tag, a[key]) for key in ('href', 'src', 'data-search-source') if a.get(key))
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical = a['href']
        if tag == 'meta' and (name := a.get('name') or a.get('property')):
            self.metas[name] = a['content']
        if tag == 'img':
            require(a['src'].endswith('.jpg') and a.get('alt') and a.get('decoding') == 'async', f'image non conforme : {a.get("src")}')
            require(a['src'] not in self.media, 'illustration répétée')
            self.media[a['src']] = a
        if tag == 'audio':
            require('autoplay' not in a and 'controls' in a and a.get('preload') == 'none', 'pas de repli audio silencieux')
        if tag == 'script' and a.get('type') in {'application/json', 'application/ld+json'}:
            self.working = a['type']

    def handle_data(self, value):
        if self.working:
            self.inline[self.working] = json.loads(value)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.working = None


def check_artefacts():
    page = HomeHTML()
    text = (ROOT/START_HOME).read_text(encoding='utf-8')
    page.feed(text)
    require(page.h1_count == 1 and '<html lang="fr">' in text, 'langue ou structure de titre invalide')
    require(set(page.idrefs) <= page.ids, f'référence interne non résolue : {set(page.idrefs)-page.ids}')
    require(all(path in page.ids for path in ('cartes','premier-raid','equipement','boss','sources','actualites','etat-du-jeu','tushonka')), 'dossier d’accueil manquant')
    require(absolute_base(page.canonical) == page.canonical, 'canonique non absolue')
    require(page.metas['description'] == DESCRIPTION and 150 <= len(DESCRIPTION) <= 160, 'description SEO hors cible')
    require(page.metas['og:url'] == page.canonical and page.metas['og:image'] == page.metas['twitter:image'], 'SEO désaligné')
    require(page.metas['og:image'].endswith('.jpg') and page.metas['og:image:type'] == 'image/jpeg','visuel social non JPG')
    schema = page.inline['application/ld+json']
    require(schema['@type'] == 'WebSite' and schema['url'] == page.canonical and schema['image']['url'] == page.metas['og:image'], 'données structurées inadéquates')
    artifacts = build(page.canonical)
    for file, computed in artifacts.items():
        require(computed == (ROOT/file).read_text(encoding='utf-8'), f'artefact non reproductible : {file}')
    records = load('js/data/search-index.json')['records']
    local_records = [row for row in records if row['href'].startswith('#')]
    require(len(local_records) == 15 and len(records) == len({x['href'] for x in records}), 'les 15 entrées historiques doivent rester uniques')
    for tag, ref in page.hrefs + [('index', r['href']) for r in local_records]:
        url = urlsplit(ref)
        if url.netloc:
            require(url.scheme == 'https' and tag in ('a','link'), f'lien externe non HTTPS ou ressource externe : {ref}')
        elif url.path:
            require(url.path.startswith('./'), f'chemin non relatif à l’accueil : {ref}')
            tail = url.path.removeprefix('./')
            wanted = DIRECTORY_ROUTES.get('/'+tail, tail)
            require(wanted in PUBLIC_FILES and (ROOT/wanted).is_file(), f'chemin local absent de l’aperçu : {ref}')
            require(not wanted.endswith('.html') or wanted in artifacts, f'lien vers dossier non édité : {ref}')
        elif url.fragment:
            require(url.fragment in page.ids, f'ancre introuvable : {ref}')
    urls = ET.parse(ROOT/'sitemap.xml').getroot().findall('.//{*}loc')
    require(urls and urls[0].text == page.canonical, 'accueil canonique absent du sitemap')
    home = load('data/home.json')
    require(len(set(home['maps']['locations'])) == 13 and home['patch']['nextStatus'] == 'NON_ATTESTE_AU_RELEVE', 'cartes ou statut du prochain patch incohérents')
    require(home['patch']['nextAnnounced'] == '1.3.5.0' and home['patch']['nextWindow'] == 'la seconde moitié de novembre 2026'
            and home['patch']['nextSource'] == 'https://www.escapefromtarkov.com/news/id/420',
            'fenêtre officielle de 1.3.5.0 absente ou confondue avec un déploiement')
    planned = next(row for row in home['news'] if row['id'] == 'actu-unity')
    require(planned['date'] == '2026-11-18' and 'non attesté' in planned['summary'].lower()
            and planned['url'] == home['patch']['nextSource'], 'actualité 1.3.5.0 mal datée ou trop affirmative')
    require(len(home['news']) == len({row['id'] for row in home['news']}) == 6, 'liste d’annonces incomplète')
    for row in home['news']:
        require(row['id'] in page.ids and row['date'] in text and row['url'] in text, f'annonce non rendue : {row["id"]}')
    require(len(page.media)==6, 'l’accueil doit intégrer six JPG')
    require(all(p.suffix=='.jpg' for p in (ROOT/'images').rglob('*') if p.is_file() and p.name != '.gitkeep'), 'format visuel interdit')
    for src, attrs in page.media.items():
        require(jpeg_q85(ROOT/src) == [int(attrs['width']),int(attrs['height'])] == [1376,768], 'ratio JPG ou balise invalide')
        hero = src == './images/hero/norvinsk-rain.jpg'
        require((hero and attrs.get('fetchpriority')=='high' and attrs.get('loading')!='lazy') or (not hero and attrs.get('loading')=='lazy'), 'priorités des images non conformes')
    manifest = {t['file']:t for t in load('audio/manifest.json')['tracks']}
    new_track = manifest['audio/ambient/ambient_city.mp3']
    require(new_track['seconds']==60 and new_track['loop'], 'boucle de l’accueil non consignée')
    config = page.inline['application/json']
    require(not config['cues'] and len(config['tracks'])==4, 'configuration lecteur non conforme')
    for track in config['tracks']:
        file = track['src'].removeprefix('./')
        blob = (ROOT/file).read_bytes()
        item = manifest[file]
        require(file in PUBLIC_FILES and item['loop'] and track['label']==item['title'], 'piste absente ou mal nommée')
        require(blob.startswith(b'ID3') and len(blob)==item['bytes'] and sha256(blob).hexdigest()==item['sha256'], f'MP3 altéré : {file}')
    require(all((ROOT/x).is_file() for x in PUBLIC_FILES), 'une ressource publiée est manquante')
    return page, records


def main(skip_state):
    page, records = check_artefacts()
    qa, firefox, contrast = (load(path) for path in (REPORT,FF,CONTRAST))
    require(qa['status']=='VALIDE' and len(qa['results'])>=15 and all(g['passed'] for g in qa['results']), 'parcours Chromium incomplet')
    require(len(qa['audits']) >= 5 and not any(x['violations'] for x in qa['audits']), 'violations axe-core')
    require(firefox['status']=='VALIDE' and len(firefox['checks'])>=6, 'contre-test Firefox absent')
    require(len(contrast['profiles'])==10 and all(p['lowestRatio']>=4.5 for p in contrast['profiles']), 'contraste du visuel insuffisant')
    require(all(p['ratio']>=p['minimum'] for p in contrast['palette']), 'contraste des commandes insuffisant')
    require(all(0 < m['lcpMs'] <= 2500 and m['cls'] <= .1 for m in qa['performance'].values()), 'budget de chargement dépassé')
    if not skip_state:
        workflow, machine, plan = load('workflow.json'), load('state_machine.json'), load('docs/plan-editorial.json')
        state = machine['instantane']
        production = workflow['production']
        require(state['etat']==workflow['etat_global'] and state['phase_active']==workflow['phase_active'], 'états désynchronisés')
        require('PHASE_2' in workflow['phases_terminees'], 'la phase 2 n’a pas été validée')
        require(any(event['evenement']=='PHASE_VALIDEE' and event['phase']=='PHASE_2' and event['vers']=='ATTENTE_CONTINUE' for event in machine['historique']), 'garde du jalon 2 absente')
        planned = {row['fichier']:row for row in plan['pages']}
        require(planned['index.html']['statut']=='LIVREE', 'accueil non livré')
        require({row['fichier'] for row in production['pages_livrees'] if row['phase']=='PHASE_2'}=={'index.html'},'inventaire de la phase 2 incohérent')
        if state['etat']=='ATTENTE_CONTINUE' and state['derniere_phase_terminee']=='PHASE_2':
            require(state['attend_confirmation'] and state['prochaine_phase']==workflow['prochaine_phase']=='PHASE_3' and state['mot_de_confirmation']=='CONTINUE', 'garde de la phase 2 défaillante')
            require(production['pages_generees']==1 and all(row['statut']=='PLANIFIEE' and not (ROOT/f).exists() for f,row in planned.items() if f!='index.html'), 'page future générée')
        images = {row['fichier']: row for row in production['images_creees']}
        audios = {row['fichier']: row for row in production['audios_crees']}
        for listing in (images, audios):
            for f,row in listing.items():
                if row['phase'] != 'PHASE_2': continue
                raw = (ROOT/f).read_bytes()
                require(row['octets']==len(raw) and row['sha256']==sha256(raw).hexdigest(), f'média non synchronisé : {f}')
        require(sum(v['phase']=='PHASE_2' for v in images.values())==6 and sum(v['phase']=='PHASE_2' for v in audios.values())==1, 'production de phase non tracée')
    print(f'OK · accueil · {sum(r["href"].startswith("#") for r in records)} entrées historiques · {len(page.media)} JPG · {len(qa["results"])} groupes · Firefox · {len(contrast["profiles"])} profils de contraste')


if __name__=='__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--avant-transition',action='store_true')
    cli.add_argument('--artefacts-seuls',action='store_true')
    args = cli.parse_args()
    if args.artefacts_seuls:
        check_artefacts()
        print('OK · artefacts, liens, sources et médias de l’accueil')
    else:
        main(args.avant_transition)
