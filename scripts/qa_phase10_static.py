#!/usr/bin/env python3
"""Static, sitemap, source, allowlist and HTTP QA for PHASE_10."""
from collections import Counter
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import URLError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import urlopen
import json
import os
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from phase10_pages import PAGES, TIMELINE, RESOURCES, validate_phase10  # noqa: E402
from serve_home import PUBLIC_FILES, DIRECTORY_ROUTES  # noqa: E402

BASE = os.environ.get('PHASE10_BASE_URL', 'http://127.0.0.1:4190').rstrip('/')
REPORT = ROOT / 'data/snapshots/validation-phase-10-static.json'
EXPECTED_IMAGES = {
    'images/phase10/patch-archive.jpg', 'images/phase10/patch-timeline.jpg',
    'images/phase10/resources-briefing.jpg', 'images/phase10/resources-workbench.jpg',
    'images/phase10/glossary-notebook.jpg', 'images/phase10/glossary-radio.jpg',
}


class AuditHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.h1 = 0
        self.lang = None
        self.title = ''
        self.in_title = False
        self.references = []
        self.images = []
        self.jsonld = []
        self.in_jsonld = False
        self.meta = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'html':
            self.lang = values.get('lang')
        if values.get('id'):
            self.ids.append(values['id'])
        if tag == 'h1':
            self.h1 += 1
        if tag == 'title':
            self.in_title = True
        if tag == 'meta':
            self.meta.append(values)
        if tag in ('a', 'link') and values.get('href'):
            self.references.append(values['href'])
        if tag in ('script', 'img', 'source') and values.get('src'):
            self.references.append(values['src'])
        if tag == 'img':
            self.images.append(values)
        if tag == 'script' and values.get('type') == 'application/ld+json':
            self.jsonld.append('')
            self.in_jsonld = True

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_jsonld:
            self.jsonld[-1] += data

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        if tag == 'script' and self.in_jsonld:
            self.in_jsonld = False


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def route_for_file(name):
    if name == 'index.html':
        return '/'
    if name.endswith('/index.html'):
        return '/' + name[:-len('index.html')]
    return '/' + name


def file_for_url(path):
    if path in ('', '/'):
        return 'index.html'
    return DIRECTORY_ROUTES.get(path, unquote(path.lstrip('/')))


def get_html(name, cache):
    if name not in cache:
        parser = AuditHTML()
        parser.feed((ROOT / name).read_text(encoding='utf-8'))
        cache[name] = parser
    return cache[name]


def audit():
    validate_phase10()
    errors = []
    details = []
    cache = {}
    plan = json.loads((ROOT / 'docs/plan-editorial.json').read_text(encoding='utf-8'))
    planned_html = len(plan['pages'])
    public_html = [p for p in ROOT.rglob('*.html') if 'node_modules' not in p.parts and '.git' not in p.parts and 'lab' not in p.parts]
    if len(public_html) != planned_html:
        errors.append(f'HTML publics : {len(public_html)} trouvés, {planned_html} prévus.')

    phase10_routes = {page['route']: page for page in PAGES}
    for page in PAGES:
        file = page['file']
        path = ROOT / file
        if not path.is_file():
            errors.append(f'Route absente : {file}')
            continue
        text = path.read_text(encoding='utf-8')
        parser = get_html(file, cache)
        duplicates = sorted(k for k, n in Counter(parser.ids).items() if n > 1)
        if duplicates:
            errors.append(f'{file}: IDs dupliqués {duplicates}')
        if parser.lang != 'fr-FR' or parser.h1 != 1 or not parser.title.strip():
            errors.append(f'{file}: lang, titre ou H1 invalide ({parser.lang}, {parser.h1})')
        if any('alt' not in image for image in parser.images):
            errors.append(f'{file}: une image n’a pas de texte alternatif.')
        if '[[' in text or 'undefined' in text:
            errors.append(f'{file}: jeton de template résiduel.')
        if '<meta name="robots" content="noindex,follow">' not in text or 'rel="canonical"' in text or 'property="og:url"' in text:
            errors.append(f'{file}: balisage aperçu canonique/indexable incorrect.')
        if 'css/pages/phase10.css' not in text or 'js/phase10.js' not in text:
            errors.append(f'{file}: CSS ou module PHASE_10 absent.')
        if 'data-phase10-page=' not in text or '<meta name="description"' not in text:
            errors.append(f'{file}: marqueur de page ou description absente.')
        if len(parser.jsonld) != 1:
            errors.append(f'{file}: JSON-LD absent ou dupliqué.')
        else:
            try:
                schema = json.loads(parser.jsonld[0])
                if schema.get('@type') != 'Article' or schema.get('dateModified') != '2026-11-18':
                    errors.append(f'{file}: JSON-LD Article / dateModified inattendu.')
            except json.JSONDecodeError as exc:
                errors.append(f'{file}: JSON-LD invalide ({exc}).')

        for reference in parser.references:
            resolved = urlsplit(urljoin('https://qa.invalid' + route_for_file(file), reference))
            if resolved.scheme not in ('http', 'https') or resolved.netloc != 'qa.invalid':
                continue
            target_name = file_for_url(resolved.path)
            if target_name not in PUBLIC_FILES:
                errors.append(f'{file}: cible locale absente de la liste blanche : {reference} → {target_name}')
                continue
            target = ROOT / target_name
            if not target.is_file():
                errors.append(f'{file}: fichier lié absent : {reference} → {target_name}')
                continue
            if resolved.fragment and target.suffix.lower() == '.html':
                if unquote(resolved.fragment) not in set(get_html(target_name, cache).ids):
                    errors.append(f'{file}: fragment absent : {reference}')

        source_doc = json.loads((ROOT / 'docs/sources.json').read_text(encoding='utf-8'))['sources']
        for key in page['sources']:
            source = source_doc[key]
            if escape(source.get('url', ''), quote=True) not in text:
                errors.append(f'{file}: source non reliée dans la page : {key}')
        details.append({'route': page['route'], 'title': page['title'], 'html_bytes': path.stat().st_size,
                        'source_links': len(page['sources'])})

    # PHASE_9 navigation was extended with the new routes, so audit internal references site-wide.
    site_local_references = 0
    site_fragments = 0
    for path in public_html:
        file = path.relative_to(ROOT).as_posix()
        parser = get_html(file, cache)
        route = route_for_file(file)
        for reference in parser.references:
            resolved = urlsplit(urljoin('https://qa.invalid' + route, reference))
            if resolved.scheme not in ('http', 'https') or resolved.netloc != 'qa.invalid':
                continue
            site_local_references += 1
            target_name = file_for_url(resolved.path)
            if target_name not in PUBLIC_FILES or not (ROOT / target_name).is_file():
                errors.append(f'{file}: cible locale manquante/non autorisée : {reference} → {target_name}')
                continue
            if resolved.fragment and target_name.endswith('.html'):
                site_fragments += 1
                if unquote(resolved.fragment) not in set(get_html(target_name, cache).ids):
                    errors.append(f'{file}: fragment local manquant : {reference}')

    glossary = json.loads((ROOT / 'data/phase10-glossary.json').read_text(encoding='utf-8'))['terms']
    if len(glossary) < 200:
        errors.append(f'Glossaire trop court : {len(glossary)} termes.')
    search = json.loads((ROOT / 'js/data/search-index.json').read_text(encoding='utf-8'))
    counts = Counter(row.get('href', '') for row in search.get('records', []))
    for route in phase10_routes:
        if counts[route] != 1:
            errors.append(f'Index de recherche : {route} apparaît {counts[route]} fois.')
    glossary_record = next((r for r in search.get('records', []) if r.get('href') == 'pages/resources/glossary.html'), {})
    keywords = {str(k).casefold() for k in glossary_record.get('keywords', [])}
    for term in ('Extraction', 'Found in Raid (FIR)', 'Trouvé en raid (FIR)', 'Desync'):
        if term.casefold() not in keywords:
            errors.append(f'Glossaire : terme non trouvé dans la recherche : {term}')
    if search.get('updatedAt') != '2026-11-18':
        errors.append(f'Index de recherche mis à jour à une date inattendue : {search.get("updatedAt")}')

    sitemap = ET.parse(ROOT / 'sitemap.xml').getroot()
    namespace = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    sitemap_locs = {row.findtext('s:loc', namespaces=namespace) for row in sitemap.findall('s:url', namespace)}
    if len(sitemap_locs) != planned_html:
        errors.append(f'Sitemap : {len(sitemap_locs)} URL uniques, {planned_html} pages prévues.')
    sitemap_root = next((loc for loc in sitemap_locs if urlsplit(loc).path in ('', '/')), '')
    expected_locs = {urljoin(sitemap_root, route) for route in phase10_routes} if sitemap_root else set()
    if not expected_locs or not expected_locs.issubset(sitemap_locs):
        errors.append('Sitemap : une ou plusieurs routes PHASE_10 sont absentes.')

    image_facts = []
    try:
        from PIL import Image
        for name in sorted(EXPECTED_IMAGES):
            path = ROOT / name
            if not path.is_file() or not path.read_bytes().startswith(b'\xff\xd8'):
                errors.append(f'Illustration manquante ou non JPEG : {name}')
                continue
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                facts = {'file': name, 'format': image.format, 'size': list(image.size), 'mode': image.mode,
                         'bytes': path.stat().st_size}
            if facts['format'] != 'JPEG' or facts['size'] != [1376, 768]:
                errors.append(f'Caractéristiques image inattendues : {facts}')
            image_facts.append(facts)
    except ImportError as exc:
        errors.append(f'Pillow indisponible pour vérifier les JPG : {exc}')

    http_paths = ['/', '/pages/patch-notes.html', '/pages/resources/', '/pages/resources/glossary.html',
                  '/css/pages/phase10.css', '/js/phase10.js', '/js/data/search-index.json', '/sitemap.xml']
    http_paths += ['/' + image for image in sorted(EXPECTED_IMAGES)]
    http_results = []
    for path in http_paths:
        try:
            with urlopen(BASE + path, timeout=10) as response:
                response.read(256)
                http_results.append({'path': path, 'status': response.status, 'content_type': response.headers.get_content_type()})
                if response.status != 200:
                    errors.append(f'HTTP {response.status}: {path}')
        except (URLError, TimeoutError) as exc:
            errors.append(f'HTTP inaccessible {BASE + path}: {exc}')
            break

    report = {
        'phase': 'PHASE_10', 'reviewedAt': '2026-11-18', 'base': BASE,
        'siteHtmlPages': len(public_html), 'plannedHtmlPages': planned_html,
        'phase10Pages': details, 'sourceRegistryEntries': len(source_doc),
        'glossaryEntries': len(glossary), 'sitemapUrls': len(sitemap_locs),
        'siteLocalReferences': site_local_references, 'siteLocalFragments': site_fragments,
        'images': image_facts, 'httpChecks': http_results,
        'status': 'PASS' if not errors else 'FAIL', 'errors': errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'PHASE_10 static QA · {report["status"]}')
    print(f'{len(public_html)}/{planned_html} routes · {len(details)} pages livrées · {len(glossary)} entrées · {len(source_doc)} sources')
    print(f'{len(sitemap_locs)} URL sitemap · {len(http_results)} contrôles HTTP · rapport {REPORT.relative_to(ROOT)}')
    if errors:
        print('\n'.join('FAIL · ' + error for error in errors))
        raise SystemExit(1)
    print('PASS · liens, fragments, médias, sources, index, sitemap, prévisualisation non canonique et liste blanche locale.')


if __name__ == '__main__':
    audit()
