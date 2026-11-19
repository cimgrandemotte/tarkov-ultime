#!/usr/bin/env python3
"""Valide les dossiers éditoriaux livrés, puis les routes Cartes de PHASE_4."""
from argparse import ArgumentParser
from datetime import datetime
from hashlib import sha256
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
import json
import xml.etree.ElementTree as ET

from check_phase0 import ROOT, load, require
from check_phase1 import jpeg_q85
from check_phase2 import HomeHTML, check_artefacts as check_home
from build_home import build
from serve_home import DIRECTORY_ROUTES, PUBLIC_FILES

BEGINNER = 'pages/getting-started.html'
LORE = 'pages/lore/index.html'
ROUTES = {'index.html', BEGINNER, LORE}  # Liste PHASE_2/3 conservée telle quelle.
MAP_HUB = 'pages/maps/index.html'
MAP_ROUTES = {
    MAP_HUB,
    'pages/maps/ground-zero.html', 'pages/maps/customs.html', 'pages/maps/factory.html',
    'pages/maps/woods.html', 'pages/maps/shoreline.html', 'pages/maps/interchange.html',
    'pages/maps/reserve.html', 'pages/maps/the-lab.html', 'pages/maps/lighthouse.html',
    'pages/maps/streets-of-tarkov.html', 'pages/maps/the-labyrinth.html',
    'pages/maps/icebreaker.html', 'pages/maps/terminal.html',
}
PUBLISHED_ROUTES = ROUTES | MAP_ROUTES
PHASE5_ROUTES = {row['file'] for row in json.loads((ROOT/'data/phase5.json').read_text(encoding='utf-8'))['pages']}
PUBLISHED_ALL_ROUTES = PUBLISHED_ROUTES | PHASE5_ROUTES
RESERVE = 'images/lore/quarantine-street.jpg'
PROOFS = [
    'data/snapshots/validation-phase-3.json', 'data/snapshots/validation-phase-3-firefox.json',
    'data/snapshots/contraste-phase-3.json', 'data/snapshots/regression-accueil-phase-3.json',
    'data/snapshots/regression-accueil-firefox-phase-3.json', 'data/snapshots/regression-atelier-phase-3.json',
]
MAP_PROOFS = [
    'data/snapshots/validation-phase-4.json', 'data/snapshots/validation-phase-4-firefox.json',
    'data/snapshots/contraste-phase-4.json',
]
MAP_SLUGS = {
    'ground-zero', 'customs', 'factory', 'woods', 'shoreline', 'interchange', 'reserve',
    'the-lab', 'lighthouse', 'streets-of-tarkov', 'the-labyrinth', 'icebreaker', 'terminal',
}
MODE_IDS = {'regular', 'pve', 'pvp-season'}


class GuideHTML(HomeHTML):
    def __init__(self):
        super().__init__()
        self.count = dict.fromkeys(('steps', 'checks', 'faq', 'spoiler', 'secret', 'tabs', 'factions', 'timeline'), 0)
        self.spoiler_open = False
        self.spoiler_inside = False
        self.spoiler_text = []
        self.title = None
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        a = dict(attrs)
        cls = a.get('class', '').split()
        if tag == 'title': self.in_title = True
        for s, attr in [('checks','data-raid-check'),('faq','data-faq-item'),('tabs','data-tab')]:
            if attr in a:
                self.count[s] += 1
        for k, c in [('steps','raid-step'),('factions','lore-faction'),('timeline','lore-timeline__period')]:
            if c in cls: self.count[k] += 1
        if tag == 'details' and 'data-campaign-spoiler' in a:
            self.spoiler_open = ('open' in a)
            self.spoiler_inside = True
            self.count['spoiler'] += 1
        if 'data-nosnippet' in a and self.spoiler_inside:
            self.count['secret'] += 1
        if self.spoiler_inside:
            require('id' not in a, 'une ancre permettrait de viser directement un spoiler')
            require(not a.get('href', '').startswith('#'), 'ancre vers un texte de révélations')

    def handle_data(self, text):
        super().handle_data(text)
        if self.spoiler_inside: self.spoiler_text.append(text)
        if self.in_title: self.title = text

    def handle_endtag(self, tag):
        super().handle_endtag(tag)
        if tag == 'details': self.spoiler_inside = False
        if tag == 'title': self.in_title = False


class MapHTML(HTMLParser):
    """Parse les pages Cartes sans imposer aux miniatures décoratives un alt non vide."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1_count = 0
        self.ids = set()
        self.idrefs = []
        self.hrefs = []
        self.images = []
        self.inline = {}
        self.metas = {}
        self.canonical = None
        self.title_parts = []
        self.in_title = False
        self.script_type = None
        self.script_parts = []
        self.text_parts = []
        self.map_cards = []
        self.mode_buttons = []
        self.mode_panels = []
        self.classes = {}

    @property
    def title(self):
        return ''.join(self.title_parts).strip()

    @property
    def text(self):
        return ' '.join(self.text_parts)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if token := a.get('id'):
            require(token not in self.ids, f'id répété dans page Carte : {token}')
            self.ids.add(token)
        if tag == 'h1': self.h1_count += 1
        for key in ('for', 'aria-controls', 'aria-labelledby', 'aria-describedby', 'aria-owns'):
            self.idrefs.extend(a.get(key, '').split())
        self.hrefs.extend((tag, a[key]) for key in ('href', 'src', 'data-search-source') if a.get(key))
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = a.get('href')
        if tag == 'meta' and (name := a.get('name') or a.get('property')): self.metas[name] = a.get('content', '')
        if tag == 'img': self.images.append(a)
        if 'data-map-card' in a: self.map_cards.append(a)
        if 'data-map-mode' in a: self.mode_buttons.append(a)
        if 'data-map-mode-panel' in a: self.mode_panels.append(a)
        for name in a.get('class', '').split(): self.classes[name] = self.classes.get(name, 0) + 1
        if tag == 'title': self.in_title = True
        if tag == 'script' and a.get('type') in {'application/json', 'application/ld+json'}:
            self.script_type = a['type']
            self.script_parts = []

    def handle_data(self, value):
        if self.in_title: self.title_parts.append(value)
        if self.script_type: self.script_parts.append(value)
        else: self.text_parts.append(value)

    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
        if tag == 'script' and self.script_type:
            self.inline[self.script_type] = json.loads(''.join(self.script_parts))
            self.script_type = None
            self.script_parts = []


def local_key(absolute, base):
    path = urlsplit(absolute).path
    root = urlsplit(base).path
    require(path.startswith(root), f'chemin hors base : {absolute}')
    suffix = path.removeprefix(root)
    return DIRECTORY_ROUTES.get('/'+suffix, suffix)


def validate_map_data(data, snapshot, sources):
    require(data['schemaVersion'] == 1, 'version du schéma Cartes')
    datetime.fromisoformat(data['verifiedAt'])
    require(data['snapshot'] == 'data/snapshots/cartes-2026-11-18.json', 'snapshot Cartes inattendu')
    require({row['id'] for row in data['modes']} == MODE_IDS and len(data['modes']) == 3, 'modes d’export incomplets')
    require({row['slug'] for row in data['maps']} == MAP_SLUGS and len(data['maps']) == 13, 'liste blanche des 13 lieux modifiée')
    require({row['route'] for row in data['maps']} == MAP_ROUTES - {MAP_HUB}, 'route Cartes inconnue ou absente')
    require(len(data['variants']) == 6, 'les six variantes du snapshot doivent rester séparées')
    require(len(data['transits']) == 29, 'le relevé directionnel de transits attendu comporte 29 lignes')
    map_names = {row['name'] for row in data['maps']}
    edges = set()
    for row in data['transits']:
        edge = (row['origin'], row['destination'])
        require(edge not in edges, f'transit dupliqué : {edge}')
        edges.add(edge)
        require(row['origin'] in map_names and row['destination'] in map_names, f'lieu de transit inconnu : {edge}')
        require(row['sourceKey'] in sources and row['evidence'] in {'COMMUNAUTAIRE', 'BSG 1.1.5.0'}, f'preuve de transit absente : {edge}')
    require(sum(row['evidence'].startswith('BSG') for row in data['transits']) == 2, 'les deux confirmations BSG Icebreaker doivent être distinctes')
    shared = {'ground-zero', 'streets-of-tarkov', 'terminal'}
    require({row['slug'] for row in data['maps'] if row.get('imageStatus') == 'ambiance_reutilisee'} == shared,
            'les trois visuels partagés doivent rester explicitement signalés')
    main_records = {}
    for mode in MODE_IDS:
        rows = snapshot['modes'][mode]['mapRecords']
        require(len(rows) == 19, f'le snapshot {mode} doit contenir 19 enregistrements')
        main_records[mode] = {row['slug']: row for row in rows}
    for page in data['maps']:
        require(set(page['sources']) <= sources.keys(), f'source absente : {page["slug"]}')
        require(set(page['accessSourceKeys']) <= sources.keys(), f'source d’accès absente : {page["slug"]}')
        require(set(page.get('routeAdviceSourceKeys', [])) <= sources.keys(), f'source de conseil absente : {page["slug"]}')
        require(page['bossSourceKey'] in sources, f'source de boss absente : {page["slug"]}')
        require(page['bosses'] and all(isinstance(x, str) for x in page['bosses']) or page['bosses'] == [], f'format des boss : {page["slug"]}')
        require(all(isinstance(x, str) for x in page['eventBosses']), f'format des mentions événementielles : {page["slug"]}')
        require(not page['exitExamples'] or page.get('exitSourceKey') in sources, f'exemples de sortie sans source : {page["slug"]}')
        for example in page['exitExamples']:
            require(example.get('name') and example.get('detail'), f'exemple de sortie incomplet : {page["slug"]}')
        image = page['image']
        require(image in PUBLIC_FILES and (ROOT/image).is_file(), f'image non publiée : {image}')
        require(jpeg_q85(ROOT/image) == [1376, 768], f'JPG Cartes invalide : {image}')
        if page['slug'] in shared:
            require(image == 'images/maps/norvinsk-overlook.jpg' and 'pas un plan' in page['imageCaption'], f'ambiance partagée mal légendée : {page["slug"]}')
        else:
            require(page.get('imageStatus') == 'visuel_dedie' and image != 'images/maps/norvinsk-overlook.jpg', f'image dédiée manquante : {page["slug"]}')
        for mode in MODE_IDS:
            require(page['slug'] in main_records[mode], f'lieu absent du snapshot {mode}: {page["slug"]}')
        raw = [main_records[mode][page['slug']] for mode in ('regular', 'pve', 'pvp-season')]
        require(len({(r['players'], r['raidDuration'], r['extractEntries']) for r in raw}) == 1,
                f'écart non documenté entre exports pour {page["slug"]}')
        for transit in data['transits']:
            if transit['origin'] == page['name'] or transit['destination'] == page['name']:
                require(transit['sourceKey'] in page['sources'], f'source de transit non jointe à {page["slug"]}')
    require(set(row['sourceKey'] for row in data['transits']) <= set(data['overview']['sourceKeys']), 'source du graphe absente du hub')
    require(set(data['overview']['sourceKeys']) <= sources.keys(), 'source du hub non enregistrée')
    ice = next(row for row in data['maps'] if row['slug'] == 'icebreaker')
    require({'balance-nov', 'yt-icebreaker-wedge-1.3', 'yt-icebreaker-smoke-1.3', 'yt-icebreaker-smoke-1.3-nov12'} <= set(ice['sources']),
            'veille BSG/vidéos Icebreaker non jointe à la fiche')
    require({'balance-nov'} <= set(ice['accessSourceKeys']) and set(ice['routeAdviceSourceKeys']) <= set(ice['sources']),
            'citations d’accès ou de conseils Icebreaker incomplètes')
    require(all(token in ice['accessText'] for token in ('12/11', 'Battle Pass', 'Black Division', '100 %', 'sans numéro de patch')),
            'les changements officiels du 12/11 ne sont pas nuancés dans la fiche Icebreaker')
    require('fumée' in ice['routeAdvice'] and 'technique fiable' in ice['routeAdvice'] and 'ne la considérez pas' in ice['routeAdvice'],
            'une astuce fumée incertaine ne doit pas être recommandée')
    require('1.3.0.1' not in sources['balance-nov']['usage'] and '1.3.0.2' not in sources['balance-nov']['usage'],
            'un numéro de patch non attesté est attribué au message BSG du 12/11')


def validate_map_outputs(local_art, base, data, snapshot, sources, search_index):
    validate_map_data(data, snapshot, sources)
    expected_hub = urljoin(base, 'pages/maps/')
    hub = MapHTML(); hub.feed(local_art[MAP_HUB])
    specs = [(MAP_HUB, expected_hub, 'Cartes de Tarkov : comparateur, accès et extractions | Tarkov Ultimate Guide',
              data['overview']['description'], data['overview']['image'], hub)]
    for item in data['maps']:
        expected = urljoin(base, item['route'])
        parser = MapHTML(); parser.feed(local_art[item['route']])
        specs.append((item['route'], expected, f"{item['name']} — accès, sorties et repères | Tarkov Ultimate Guide",
                      item['description'], item['image'], parser))
    all_map_pages = {file: parser for file, _, _, _, _, parser in specs}
    for file, canonical, title, description, image, page in specs:
        text = local_art[file]
        require('<html lang="fr">' in text and '[[' not in text and page.h1_count == 1, f'HTML Cartes non compilé : {file}')
        require(page.canonical == page.metas['og:url'] == canonical, f'canonique Cartes désalignée : {file}')
        require(page.title == page.metas['og:title'] == page.metas['twitter:title'] == title, f'titre social Cartes désaligné : {file}')
        require(140 <= len(description) <= 160 and page.metas['description'] == page.metas['og:description'] == page.metas['twitter:description'] == description,
                f'description SEO Cartes hors plage : {file}')
        expected_image = urljoin(base, image)
        require(page.metas['og:image'] == page.metas['twitter:image'] == expected_image and page.metas['og:image:type'] == 'image/jpeg',
                f'image sociale Cartes désalignée : {file}')
        require(set(page.idrefs) <= page.ids, f'IDREF Cartes non résolu : {file} {set(page.idrefs)-page.ids}')
        require('data-site-search' in text, f'recherche globale absente : {file}')
        if file == MAP_HUB:
            require('maps-hub-rail' in page.classes and 'map-method' in page.ids and 'maps-hub-sources' in text,
                    'rail, méthode ou sources du hub Cartes absents')
        else:
            require('data-guide-toc' in text and 'sources' in page.ids, f'sommaire ou sources de fiche absents : {file}')
        require(all('src' in item and item['src'].endswith('.jpg') and item.get('decoding') == 'async' for item in page.images), f'image non JPG/décodée : {file}')
        if file == MAP_HUB:
            graph = page.inline['application/ld+json']
            require(graph['@type'] == 'CollectionPage' and graph['url'] == canonical and len(graph['hasPart']) == 13, 'CollectionPage Cartes invalide')
            require(len(page.images) == 14 and len(page.map_cards) == 13, 'hub Cartes : hero et treize vignettes attendus')
            hero = [img for img in page.images if 'guide-hero__image' in img.get('class', '').split()]
            require(len(hero) == 1 and local_key(urljoin(canonical, hero[0]['src']), base) == data['overview']['image'], 'hero du hub absent ou désaligné')
            require(hero[0].get('alt') and hero[0].get('fetchpriority') == 'high', 'hero du hub sans texte alternatif/priorité')
            require(all(not img.get('alt') and img.get('loading') == 'lazy' for img in page.images if img not in hero), 'vignette décorative du hub mal configurée')
            require({row.get('data-map-slug') for row in page.map_cards} == MAP_SLUGS, 'vignette manquante ou slug inconnu')
            require(len(page.mode_buttons) == 0, 'les modes du hub sont des filtres select, pas des tabs de fiche')
            card_records = {row['href']: row for row in search_index if row.get('tag') == 'Carte'}
            require(set(card_records) == {row['route'] for row in data['maps']} and len(card_records) == 13, 'index de recherche Cartes incomplet')
            for card in page.map_cards:
                stats = json.loads(card['data-map-stats'])
                require(set(stats) == MODE_IDS and all('extractEntries' in stats[m] for m in MODE_IDS), f'statistiques de comparaison manquantes : {card.get("data-map-slug")}')
            require(page.classes.get('maps-network-row') == 29, 'graphe du hub : nombre de transits incohérent')
            require(all(row['origin'] in page.text and row['destination'] in page.text for row in data['transits']), 'lien de transit absent du hub')
            require(all(row['name'] in page.text for row in data['variants']), 'variante absente du hub')
            require('map-index' in page.ids and 'compare' in page.ids and 'transit-network' in page.ids and 'variants' in page.ids and 'map-method' in page.ids,
                    'ancres du hub Cartes manquantes')
        else:
            item = next(row for row in data['maps'] if row['route'] == file)
            article, breadcrumb = page.inline['application/ld+json']['@graph']
            require(article['@type'] == 'Article' and article['mainEntityOfPage'] == canonical and article['image']['url'] == expected_image, f'Article JSON-LD : {file}')
            crumbs = [row['item'] for row in breadcrumb['itemListElement']]
            require(breadcrumb['@type'] == 'BreadcrumbList' and crumbs == [base, expected_hub, canonical], f'fil d’Ariane JSON-LD : {file}')
            require(len(page.images) == 1, f'une fiche Carte doit conserver son unique hero JPG (exception visuelle documentée) : {file}')
            hero = page.images[0]
            image_path = local_key(urljoin(canonical, hero['src']), base)
            require(image_path == item['image'] and hero.get('alt') and hero.get('fetchpriority') == 'high' and hero.get('loading') != 'lazy', f'hero Cartes invalide : {file}')
            require(jpeg_q85(ROOT/image_path) == [1376,768] == [int(hero['width']),int(hero['height'])], f'JPG Cartes mal encodé : {image_path}')
            require({'mode','acces','reperes','bosses','extractions','parcours','transits','sources'} <= page.ids, f'sections Cartes manquantes : {file}')
            require(len(page.mode_buttons) == 3 and {row.get('data-map-mode') for row in page.mode_buttons} == MODE_IDS,
                    f'contrôles de mode Cartes manquants : {file}')
            require(len(page.mode_panels) == 3 and {row.get('data-map-mode-panel') for row in page.mode_panels} == MODE_IDS,
                    f'panneaux de mode Cartes manquants : {file}')
            require(page.classes.get('map-boss-list', 0) + page.classes.get('map-boss-empty', 0) >= 1, f'section Bosses Cartes vide : {file}')
            require('#ref-wiki-bosses' in {ref for _,ref in page.hrefs}, f'citation Bosses absente : {file}')
            require(all(name in page.text for name in item['bosses'] + item['eventBosses']), f'noms de boss manquants : {file}')
            require(page.classes.get('map-transit-list', 0) + page.classes.get('map-no-transit', 0) == 1, f'section transits absente : {file}')
            if item['exitExamples']:
                require(page.classes.get('map-exit-source') == 1 and f"#ref-{item['exitSourceKey']}" in {ref for _,ref in page.hrefs},
                        f'exemples de sorties sans citation : {file}')
            else:
                require(page.classes.get('map-exit-examples--empty') == 1, f'absence de liste dynamique non expliquée : {file}')
            source_ids = {f'ref-{key}' for key in item['sources']}
            require(source_ids <= page.ids, f'référence de source absente de la fiche : {file} {source_ids-page.ids}')
    return all_map_pages


def artifacts():
    home, index = check_home()
    src = load('docs/sources.json')
    guide_data = load('data/guides.json')
    map_data = load('data/maps.json')
    map_snapshot = load(map_data['snapshot'])
    plan = load('docs/plan-editorial.json')
    sources = src['sources']
    base = home.canonical
    pages = {'index.html': home}
    local_art = build(base)
    ordered = [base]
    for spec in guide_data['pages']:
        file = spec['file']
        require(file in ROUTES, 'route ajoutée en dehors de la liste PHASE_2/3')
        require(set(spec['sources']) <= sources.keys(), 'source de dossier non consignée')
        page = GuideHTML(); text = (ROOT/file).read_text(encoding='utf-8'); page.feed(text)
        pages[file] = page
        expect = urljoin(base, spec['route'])
        ordered.append(expect)
        require(page.canonical==page.metas['og:url']==expect, f'canonique désalignée : {file}')
        require('<html lang="fr">' in text and page.h1_count==1 and '[[' not in text, f'contenu non compilé : {file}')
        require(page.title == spec['title'] == page.metas['og:title'] == page.metas['twitter:title'], f'titre métadonnées désaligné : {file}')
        desc = page.metas['description']
        require(140 <= len(desc) <= 160 and desc==spec['description']==page.metas['og:description']==page.metas['twitter:description'], f'description hors plage : {file}')
        require(page.metas['og:image']==page.metas['twitter:image']==urljoin(base,spec['image']) and page.metas['og:image:type']=='image/jpeg', f'visuel social désaligné : {file}')
        article, breadcrumb = page.inline['application/ld+json']['@graph']
        require(article['@type']=='Article' and article['mainEntityOfPage']==expect and article['image']['url']==page.metas['og:image'], 'Article JSON-LD')
        require(breadcrumb['@type']=='BreadcrumbList' and [r['item'] for r in breadcrumb['itemListElement']]==[base,expect], 'fil d’Ariane SEO')
        require(set(page.idrefs) <= page.ids, f'IDREF manquant : {set(page.idrefs)-page.ids}')
        require(len(page.media) == (3 if file == BEGINNER else 2), 'le dossier doit comporter les JPG prévus')
        for ref, attrs in page.media.items():
            path = local_key(urljoin(expect,ref),base)
            hero = path == spec['image']
            require(path in PUBLIC_FILES and path!=RESERVE, f'photo non servie : {path}')
            require(jpeg_q85(ROOT/path)==[1376,768]==[int(attrs['width']),int(attrs['height'])],f'JPEG 85 invalide : {path}')
            require((attrs.get('fetchpriority')=='high' and attrs.get('loading')!='lazy') if hero else attrs.get('loading')=='lazy',f'priorité du média : {path}')
        require('data-guide-toc' in text and 'sources' in page.ids and 'data-site-search' in text, f'gabarit incomplet : {file}')
        if file == BEGINNER:
            require(page.count['steps']==10 and page.count['checks']==6 and page.count['faq']==24 and page.count['tabs']==2,'parcours débutant incomplet')
            require({'profils','etapes','checklist','extraction','sante','commandes','faq','faq-carte','profile-pmc','profile-scav'} <= page.ids, 'ancres débutant incomplètes')
            require('Maquette non officielle' in text and 'class="health-diagram"' in text and 'Tartowers Sales Office' in text,'maquette HUD, santé ou extractions non documentées')
        else:
            require(page.count['factions'] >= 7 and page.count['timeline']==5 and {'norvinsk','factions','chronologie','chapitres','revelations'} <= page.ids, 'lore incomplet')
            require(not page.spoiler_open and page.count['spoiler']==page.count['secret']==1,'spoilers non masqués')
            for word in ['Kerman','Zubr','Debtor','Savior','Fallen','Survivor']:
                require(word in ''.join(page.spoiler_text) and text.count(word)==sum(s.count(word) for s in page.spoiler_text), f'révélation hors bloc : {word}')
    require(pages.keys()==ROUTES, 'liste PHASE_2/3 incomplète')
    map_pages = validate_map_outputs(local_art, base, map_data, map_snapshot, sources, index)
    phase5_pages = {}
    for file in PHASE5_ROUTES:
        parser = MapHTML(); parser.feed(local_art[file]); phase5_pages[file] = parser
    all_pages = {**pages, **map_pages, **phase5_pages}
    require({p for p in PUBLIC_FILES if p.endswith('.html')} == PUBLISHED_ALL_ROUTES, 'liste blanche HTML explicite incomplète ou élargie')
    require({k for k in local_art if k.endswith('.html')} == PUBLISHED_ALL_ROUTES, 'le build doit produire uniquement les routes PHASE_2–5')
    require(not (ROOT/RESERVE).relative_to(ROOT).as_posix() in PUBLIC_FILES, 'une réserve d’image est publiée')
    ordered += [urljoin(base, 'pages/maps/')]
    ordered += [urljoin(base, row['route']) for row in map_data['maps']]
    phase5_config = load('data/phase5.json')
    ordered += [urljoin(base, row['route']) for row in phase5_config['pages']]
    xml = ET.parse(ROOT/'sitemap.xml').getroot()
    require([row.text for row in xml.findall('.//{*}loc')] == ordered, 'sitemap : canonique, ordre ou liste de routes incorrects')
    require(len(index)==56 and len({row['href'] for row in index})==56, 'index de recherche attendu : 56 entrées uniques')
    p5_records = [row for row in index if row.get('tag') in {'Arsenal','Munitions'}]
    require(len(p5_records)==13 and {row['href'] for row in p5_records} == {row['route'] for row in phase5_config['pages']}, 'index PHASE_5 incomplet')
    map_hub_records = [row for row in index if row.get('tag') == 'Index des cartes']
    require(len(map_hub_records)==1 and map_hub_records[0]['href']=='pages/maps/', 'index du hub Cartes absent de la recherche')
    require(all(not any(secret in str(row).lower() for secret in ('#revelations','kerman','zubr','debtor','savior','fallen')) for row in index), 'révélation indexée')
    for file, page in all_pages.items():
        links = page.hrefs + ([('index',r['href']) for r in index] if file=='index.html' else [])
        for tag, ref in links:
            url = urlsplit(ref)
            if url.netloc:
                require(url.scheme=='https' and tag in {'a','link'}, f'URL externe non HTTPS ou ressource distante : {file} {ref}')
                continue
            require(not url.scheme and not ref.startswith('/'), f'chemin non relatif : {file} {ref}')
            target = local_key(urljoin(page.canonical,ref),base)
            require(target in PUBLIC_FILES and (ROOT/target).is_file(), f'destination hors liste blanche : {file} {ref}')
            if url.fragment:
                require(target in all_pages and url.fragment in all_pages[target].ids, f'ancre non résolue : {file} {ref}')
    prefix = build('https://guide.example.tld/tarkov/')
    require('https://guide.example.tld/tarkov/pages/maps/' in prefix['sitemap.xml'] and 'Disallow: /tarkov/lab/' in prefix['robots.txt'], 'préfixe de déploiement non reproductible')
    rows = {row['fichier']: row for row in plan['pages']}
    require(set(PUBLISHED_ALL_ROUTES) <= rows.keys(), 'route livrée absente du plan éditorial')
    require(all(not (ROOT/f).exists() for f in rows.keys()-PUBLISHED_ALL_ROUTES), 'HTML d’une phase future généré')
    require(src['revalidation_phase_3']['client_et_modes_testes'] is False and all((ROOT/row['revalidation_phase_3']).is_file() for row in src['sources'].values() if 'revalidation_phase_3' in row),'relevé Phase 3 incomplet')
    return all_pages, rows, guide_data, map_data


def qa_phase3():
    chromium, firefox, contrast, home, home_fx, lab = (load(ref) for ref in PROOFS)
    require(chromium['status']==firefox['status']=='VALIDE' and len(chromium['checks'])>=14 and all(c['passed'] for c in chromium['checks']), 'preuve Chromium/Firefox de phase 3 absente')
    require(len(chromium['audits'])>=8 and not any(a['violations'] for a in chromium['audits']) and len(firefox['checks'])>=6, 'audits du dossier incomplets')
    require(set(chromium['performance'])=={'starter','lore'} and all(0 < p['lcpMs'] <= 2500 and p['cls'] <= .1 for group in chromium['performance'].values() for p in group.values()), 'budget de chargement dossier dépassé')
    require(len(contrast['profiles'])==20 and all(m['lowestRatio']>=4.5 for m in contrast['profiles']), 'contraste sur photo non vérifié')
    require(all(m['ratio']>=m['minimum'] for m in contrast['palette']), 'contraste de contrôle insuffisant')
    require(home['status']=='VALIDE' and len(home['results'])>=16 and not any(a['violations'] for a in home['audits']) and home_fx['status']=='VALIDE' and len(home_fx['checks'])>=6, 'régression accueil ou preuve manquante')
    require(lab['status']=='VALIDE' and len(lab['results'])>=12 and not any(a['violations'] for a in lab['audits']), 'régression atelier ou preuve manquante')
    return chromium, firefox, contrast


def qa_phase4():
    chromium, firefox, contrast = (load(ref) for ref in MAP_PROOFS)
    require(chromium['status'] == firefox['status'] == 'VALIDE' and len(chromium['checks']) >= 12 and all(row['passed'] for row in chromium['checks']), 'QA Chromium PHASE_4 absente ou incomplète')
    require(len(chromium['audits']) >= 4 and not any(row['violations'] for row in chromium['audits']), 'violations axe-core sur les pages Cartes')
    require(firefox['status'] == 'VALIDE' and len(firefox['checks']) >= 6 and not firefox['errors'], 'contre-test Firefox PHASE_4 absent')
    require(len(contrast['profiles']) >= 10 and all(row['lowestRatio'] >= 4.5 for row in contrast['profiles']), 'contraste visuel des Cartes sous le seuil')
    require(all(row['ratio'] >= row['minimum'] for row in contrast['palette']), 'contraste des commandes Cartes sous le seuil')
    require(set(chromium['performance']) == {'hub','map'} and all(0 < row['lcpMs'] <= 2500 and row['cls'] <= .1 for group in chromium['performance'].values() for row in group.values()), 'budget performance PHASE_4 dépassé')
    return chromium, firefox, contrast


def state_phase4(rows, guide_data, map_data, before_transition=False):
    w, machine = load('workflow.json'), load('state_machine.json')
    s = machine['instantane']
    require(s['etat']==w['etat_global'] and s['phase_active']==w['phase_active'] and s['prochaine_phase']==w['prochaine_phase'], 'états Workflow/State machine désynchronisés')
    phases = {row['id']: row for row in w['phases']}
    p = w['production']
    require(any(row['phase']=='PHASE_3' and row['evenement']=='CONTINUE' and row['vers']=='EN_COURS' for row in machine['historique']), 'transition vers PHASE_4 absente')
    require(all(phases[f'PHASE_{i}']['statut']=='PLANIFIE' and phases[f'PHASE_{i}']['pages_generees']==0 for i in range(5,11)), 'une phase ultérieure à P4 a été publiée')
    require(all(not (ROOT/file).exists() for file in rows.keys()-PUBLISHED_ROUTES), 'une route ultérieure a été écrite')
    delivered = {row['fichier']: row for row in p['pages_livrees']}
    if before_transition:
        require(s['etat']=='EN_COURS' and s['phase_active']=='PHASE_4' and not s['attend_confirmation'], 'PHASE_4 non active avant transition')
        require(w['phases_terminees']==[f'PHASE_{i}' for i in range(4)] and phases['PHASE_4']['statut']=='EN_COURS', 'état d’entrée P4 incohérent')
        require(phases['PHASE_4']['pages_generees']==0 and p['pages_generees']==3 and delivered.keys()==ROUTES, 'inventaire avant transition incohérent')
        return
    require(w['phases_terminees']==[f'PHASE_{i}' for i in range(5)], 'phase terminée manquante ou avancée')
    require(s['etat']=='ATTENTE_CONTINUE' and s['phase_active'] is None and s['attend_confirmation'] and s['prochaine_phase']=='PHASE_5', 'garde CONTINUE de PHASE_4 absente')
    require(s['mot_de_confirmation']=='CONTINUE' and s['derniere_phase_terminee']=='PHASE_4', 'mot ou phase de confirmation erroné')
    require(phases['PHASE_4']['statut']=='TERMINE' and phases['PHASE_4']['pages_generees']==14, 'inventaire de PHASE_4 incohérent')
    require(p['pages_generees']==17 and delivered.keys()==PUBLISHED_ROUTES, '17 routes éditoriales attendues')
    require({f for f,row in rows.items() if row['statut']=='LIVREE'}==PUBLISHED_ROUTES, 'plan éditorial non synchronisé avec les routes livrées')
    require(all(delivered[file]['phase']=='PHASE_4' for file in MAP_ROUTES), 'phase incorrecte dans l’inventaire Cartes')
    expected_images={row['image'] for row in map_data['maps']} | {map_data['overview']['image']}
    for page in map_data['maps']:
        f=page['route']
        require(f in delivered and delivered[f]['images']==[page['image']], f'image de page non inventoriée : {f}')
    require(set(delivered[MAP_HUB]['images'])==expected_images, 'médias du hub non inventoriés')
    for folder, term, extension in [('images','images_creees','*.jpg'),('audio','audios_crees','*.mp3')]:
        listing={row['fichier']:row for row in p[term]}
        actual={f.relative_to(ROOT).as_posix() for f in (ROOT/folder).rglob(extension)}
        require(listing.keys()==actual, f'inventaire {folder} incomplet')
        for f,row in listing.items():
            raw=(ROOT/f).read_bytes()
            require(row['octets']==len(raw) and row['sha256']==sha256(raw).hexdigest(),f'média altéré : {f}')
        if folder=='images':
            require(sum(row['phase']=='PHASE_4' for row in listing.values())==10, '10 JPG Cartes créés attendus')
        else:
            require(sum(row['phase']=='PHASE_4' for row in listing.values())==0, 'aucun MP3 n’a été créé en PHASE_4')
    require(next(x for x in p['images_creees'] if x['fichier']==RESERVE)['statut']=='RESERVE_NON_PUBLIEE','réserve d’image non tracée')


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument('--phase4', action='store_true', help='inclure la QA navigateur Cartes et contrôler la garde de phase')
    cli.add_argument('--artefacts-seuls', action='store_true', help='vérifier les sorties statiques sans charger les preuves navigateur')
    cli.add_argument('--avant-transition', action='store_true', help='confirmer que le workflow est encore EN_COURS avant clôture')
    args = cli.parse_args()
    if args.avant_transition and not args.phase4:
        cli.error('--avant-transition nécessite --phase4')
    pages, rows, guide_data, map_data = artifacts()
    if args.artefacts_seuls:
        print('OK · 30 routes PHASE_2–5, 56 entrées de recherche, 29 transits Cartes, sources, images, sitemap et ancres')
        return
    p3 = qa_phase3()
    if not args.phase4:
        print(f'OK · gardes QA PHASE_3 rétablies · {len(p3[0]["checks"])} contrôles Chromium · {len(p3[1]["checks"])} Firefox · {len(p3[2]["profiles"])} profils contraste')
        return
    chromium, firefox, contrast = qa_phase4()
    state_phase4(rows, guide_data, map_data, args.avant_transition)
    print(f'OK · QA PHASE_3 ({len(p3[0]["checks"])} Chromium) + PHASE_4 · 30 routes PHASE_2–5 · 56 entrées · 29 transits · {len(chromium["checks"])} Chromium · {len(firefox["checks"])} Firefox · {len(contrast["profiles"])} profils contraste')

if __name__=='__main__':
    main()
