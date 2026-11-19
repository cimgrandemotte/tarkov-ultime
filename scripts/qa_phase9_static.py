#!/usr/bin/env python3
"""Audit statique et HTTP des sept routes PHASE_9, ressources et liste blanche."""
from collections import Counter
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import urlopen
import hashlib
import importlib.util
import json
import os
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from phase9_pages import PAGES  # noqa: E402
from PIL import Image  # noqa: E402

BASE = os.environ.get('PHASE9_BASE_URL', 'http://127.0.0.1:4180').rstrip('/')
REPORT_PATH = ROOT / 'data/snapshots/validation-phase-9-static.json'
IMAGE_FILES = {page['hero'] for page in PAGES}
SOURCE_KEYS = {key for page in PAGES for key in page['sources']}
EXPECTED_TOTAL_HTML = 84


class HTMLAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.references = []
        self.missing_alt = []
        self.phase9_images = set()
        self.titles = []
        self.meta = []
        self.jsonld = []
        self.in_title = False
        self.in_jsonld = False
        self.lang = None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'html':
            self.lang = values.get('lang')
        if values.get('id'):
            self.ids.append(values['id'])
        if tag == 'img':
            src = values.get('src', '')
            if 'alt' not in values:
                self.missing_alt.append(src or '<src absent>')
            if src:
                self.references.append(src)
                if 'images/phase9/' in src:
                    self.phase9_images.add(src)
            for candidate in values.get('srcset', '').split(','):
                candidate = candidate.strip().split(' ')[0]
                if candidate:
                    self.references.append(candidate)
                    if 'images/phase9/' in candidate:
                        self.phase9_images.add(candidate)
        if tag in ('a', 'link') and values.get('href'):
            self.references.append(values['href'])
        if tag in ('script', 'source', 'audio', 'video') and values.get('src'):
            self.references.append(values['src'])
        if tag == 'video' and values.get('poster'):
            self.references.append(values['poster'])
        if tag == 'title':
            self.titles.append('')
            self.in_title = True
        if tag == 'meta':
            self.meta.append(values)
        if tag == 'script' and values.get('type') == 'application/ld+json':
            self.jsonld.append('')
            self.in_jsonld = True

    def handle_data(self, data):
        if self.in_title:
            self.titles[-1] += data
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


def run_check(report, name, function):
    try:
        detail = function()
        report['checks'].append({'name': name, 'passed': True, 'detail': detail})
        print(f'PASS · {name} · {detail}')
    except Exception as error:
        report['checks'].append({'name': name, 'passed': False, 'detail': str(error)})
        report['errors'].append(f'{name}: {error}')
        print(f'FAIL · {name} · {error}')


def audit_pages_and_links():
    issues = []
    parsed = {}
    total_local = 0
    used_images = set()
    route_files = {page['file'] for page in PAGES}
    require(len(PAGES) == 7, f'{len(PAGES)} routes prévues, 7 attendues')
    for page in PAGES:
        path = ROOT / page['file']
        if not path.is_file():
            issues.append(f'fichier absent : {page["file"]}')
            continue
        text = path.read_text(encoding='utf-8')
        parser = HTMLAudit()
        parser.feed(text)
        parsed[page['file']] = parser
        duplicates = sorted(key for key, count in Counter(parser.ids).items() if count > 1)
        if duplicates:
            issues.append(f'{page["file"]} : IDs dupliqués {duplicates}')
        if parser.missing_alt:
            issues.append(f'{page["file"]} : images sans alt {parser.missing_alt}')
        if parser.lang != 'fr-FR':
            issues.append(f'{page["file"]} : lang inattendu {parser.lang!r}')
        if len(parser.titles) != 1 or not parser.titles[0].strip():
            issues.append(f'{page["file"]} : titre HTML absent')
        if text.count('<h1') != 1:
            issues.append(f'{page["file"]} : un H1 attendu, nombre {text.count("<h1")}')
        if 'name="description"' not in text or 'data-phase9-page=' not in text:
            issues.append(f'{page["file"]} : métadonnée SEO ou marqueur PHASE_9 absent')
        if '<meta name="robots" content="noindex,follow">' not in text:
            issues.append(f'{page["file"]} : noindex aperçu absent')
        if 'rel="canonical"' in text or 'property="og:url"' in text:
            issues.append(f'{page["file"]} : canonical public interdit dans l’aperçu')
        if 'css/pages/phase9.css' not in text or 'js/phase9.js' not in text:
            issues.append(f'{page["file"]} : CSS/JS PHASE_9 absent')
        if len(parser.jsonld) != 1:
            issues.append(f'{page["file"]} : JSON-LD Article attendu')
        else:
            try:
                schema = json.loads(parser.jsonld[0])
                if schema.get('@type') != 'Article' or schema.get('dateModified') != '2026-11-18':
                    issues.append(f'{page["file"]} : JSON-LD Article/dateModified incorrect')
            except json.JSONDecodeError as error:
                issues.append(f'{page["file"]} : JSON-LD invalide ({error})')
        if '[[' in text or '2026-11-19' in text or 'phase-9-reference-' in text:
            issues.append(f'{page["file"]} : jeton ou référence future/quarantinée')
        for ref in parser.references:
            resolved = urlsplit(urljoin(f'https://local.test/{page["file"]}', ref))
            if resolved.scheme not in ('http', 'https') or resolved.netloc != 'local.test':
                continue
            total_local += 1
            target_name = unquote(resolved.path.lstrip('/')) or 'index.html'
            target = (ROOT / target_name).resolve()
            if ROOT.resolve() not in target.parents and target != ROOT.resolve():
                issues.append(f'{page["file"]} : référence hors workspace {ref}')
                continue
            if target.is_dir():
                target = target / 'index.html'
            if not target.is_file():
                issues.append(f'{page["file"]} : cible locale absente {ref}')
                continue
            if resolved.fragment and target.suffix == '.html':
                destination = target.relative_to(ROOT).as_posix()
                target_parser = parsed.get(destination)
                if target_parser is None:
                    target_parser = HTMLAudit()
                    target_parser.feed(target.read_text(encoding='utf-8'))
                if unquote(resolved.fragment) not in set(target_parser.ids):
                    issues.append(f'{page["file"]} : fragment manquant {ref}')
        used_images.update(unquote(urlsplit(urljoin(f'https://local.test/{page["file"]}', src)).path.lstrip('/'))
                           for src in parser.phase9_images)
    expected = IMAGE_FILES
    if used_images != expected:
        issues.append(f'illustrations utilisées différentes de la liste attendue : manquantes={sorted(expected-used_images)}, extra={sorted(used_images-expected)}')
    if issues:
        raise AssertionError('; '.join(issues[:30]))
    return f'7 pages · {total_local} liens/assets/fragments locaux résolus · 7 JPG liées · IDs, alts, SEO et JSON-LD contrôlés'


def audit_images_and_sources():
    sources = json.loads((ROOT / 'docs/sources.json').read_text(encoding='utf-8'))['sources']
    missing = sorted(SOURCE_KEYS - sources.keys())
    if missing:
        raise AssertionError(f'clés de sources absentes : {missing}')
    invalid_sources = sorted(key for key in SOURCE_KEYS if not str(sources[key].get('url', '')).startswith('https://'))
    if invalid_sources:
        raise AssertionError(f'URL de source absente/non HTTPS : {invalid_sources}')
    records = []
    for name in sorted(IMAGE_FILES):
        path = ROOT / name
        if not path.is_file() or not path.read_bytes().startswith(b'\xff\xd8'):
            raise AssertionError(f'JPG absente/invalide : {name}')
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            facts = {'file': name, 'format': image.format, 'mode': image.mode, 'size': list(image.size),
                     'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        if facts['format'] != 'JPEG' or facts['mode'] != 'RGB' or facts['size'] != [1376, 768]:
            raise AssertionError(f'caractéristiques inattendues pour {name}: {facts}')
        records.append(facts)
    return {'sources': len(SOURCE_KEYS), 'sourcesDocument': len(sources), 'images': records}


def audit_search_sitemap():
    search_path = ROOT / 'js/data/search-index.json'
    search_text = search_path.read_text(encoding='utf-8')
    search = json.loads(search_text)
    hrefs = Counter(row.get('href', '') for row in search.get('records', []))
    missing = sorted(page['route'] for page in PAGES if hrefs[page['route']] != 1)
    if missing:
        raise AssertionError(f'routes absentes ou dupliquées dans l’index : {missing}')
    if search.get('updatedAt') != '2026-11-18':
        raise AssertionError(f'date de recherche inattendue : {search.get("updatedAt")}')
    xml_text = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
    sitemap = ET.fromstring(xml_text)
    locations = [node.text or '' for node in sitemap.iter() if node.tag.split('}')[-1] == 'loc']
    if len(locations) != EXPECTED_TOTAL_HTML or len(set(locations)) != EXPECTED_TOTAL_HTML:
        raise AssertionError(f'{EXPECTED_TOTAL_HTML} URLs sitemap uniques attendues, {len(locations)} trouvées')
    paths = {urlsplit(location).path.lstrip('/') for location in locations}
    missing = sorted(page['route'] for page in PAGES if page['route'] not in paths)
    if missing:
        raise AssertionError(f'routes absentes du sitemap : {missing}')
    return f'{len(search.get("records", []))} entrées de recherche · {len(locations)} URLs sitemap uniques · 7 routes PHASE_9 intégrées'


def audit_allowlist():
    spec = importlib.util.spec_from_file_location('serve_home', SCRIPTS / 'serve_home.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    expected_files = {page['file'] for page in PAGES} | IMAGE_FILES | {'css/pages/phase9.css', 'js/phase9.js'}
    missing = sorted(expected_files - set(module.PUBLIC_FILES))
    if missing:
        raise AssertionError(f'liste blanche incomplète : {missing}')
    route_directories = {
        '/pages/spt-tushonka/': 'pages/spt-tushonka/index.html',
        '/pages/arena/': 'pages/arena/index.html',
        '/pages/events/': 'pages/events/index.html',
    }
    for route, target in route_directories.items():
        if module.DIRECTORY_ROUTES.get(route) != target:
            raise AssertionError(f'route de répertoire absente/mauvaise : {route}')
    return '7 routes, 7 illustrations, CSS/JS PHASE_9 dans la liste blanche et 3 routes de répertoire'


def audit_workflow_and_plan():
    workflow = json.loads((ROOT / 'workflow.json').read_text(encoding='utf-8'))
    machine = json.loads((ROOT / 'state_machine.json').read_text(encoding='utf-8'))
    plan = json.loads((ROOT / 'docs/plan-editorial.json').read_text(encoding='utf-8'))
    expected = {page['file'] for page in PAGES}
    planned = {row['fichier'] for row in plan['pages'] if row['phase'] == 'PHASE_9'}
    delivered = {row['fichier'] for row in workflow['production']['pages_livrees'] if row.get('phase') == 'PHASE_9'}
    records = {row['fichier']: row for row in workflow['production']['pages_livrees'] if row.get('phase') == 'PHASE_9'}
    if planned != expected or delivered != expected:
        raise AssertionError(f'inventaires plan/workflow différents : plan={sorted(planned)}, livré={sorted(delivered)}')
    if any(row.get('statut') != 'LIVREE' for row in plan['pages'] if row['phase'] == 'PHASE_9'):
        raise AssertionError('une route PHASE_9 du plan reste non livrée')
    phase = next(row for row in workflow['phases'] if row['id'] == 'PHASE_9')
    if phase.get('statut') != 'TERMINE' or phase.get('pages_generees') != 7 or workflow['production']['pages_generees'] != 84:
        raise AssertionError('compteurs/statut PHASE_9 du workflow incohérents')
    if workflow.get('phase_active') is not None or workflow.get('prochaine_phase') != 'PHASE_10' or workflow.get('etat_global') != 'ATTENTE_CONTINUE':
        raise AssertionError('workflow ne place pas PHASE_10 en attente de confirmation')
    state = machine['instantane']
    if state.get('etat') != 'ATTENTE_CONTINUE' or state.get('phase_active') is not None or state.get('derniere_phase_terminee') != 'PHASE_9' or state.get('prochaine_phase') != 'PHASE_10' or not state.get('attend_confirmation'):
        raise AssertionError('state_machine non synchronisée après PHASE_9')
    image_rows = {row['fichier']: row for row in workflow['production']['images_creees'] if row.get('phase') == 'PHASE_9'}
    if set(image_rows) != IMAGE_FILES:
        raise AssertionError(f'inventaire de médias PHASE_9 incorrect : {sorted(image_rows)}')
    for image, row in image_rows.items():
        raw = (ROOT / image).read_bytes()
        if row.get('octets') != len(raw) or row.get('sha256') != hashlib.sha256(raw).hexdigest():
            raise AssertionError(f'empreinte workflow divergente : {image}')
    if not (ROOT / 'docs/phase-9.md').is_file() or not (ROOT / 'docs/verifications-phase-9.md').is_file():
        raise AssertionError('bilan ou rapport de vérification manquant')
    return '84/87 routes · PHASE_9 7/7 · 7 SHA-256 · PHASE_10 en attente de CONTINUE'


def audit_http():
    public = [page['route'] for page in PAGES] + sorted(IMAGE_FILES) + [
        'css/pages/phase9.css', 'js/phase9.js', 'js/data/search-index.json', 'sitemap.xml', 'robots.txt', 'index.html'
    ]
    failures = []
    for path in public:
        try:
            with urlopen(f'{BASE}/{path.lstrip("/")}', timeout=12) as response:
                if response.status != 200:
                    failures.append(f'{path}: HTTP {response.status}')
        except (HTTPError, URLError, TimeoutError) as error:
            failures.append(f'{path}: {error}')
    private = ['docs/sources.json', 'docs/verifications-phase-9.md', 'workflow.json', 'state_machine.json',
               'scripts/phase9_pages.py', 'scripts/qa_phase9_static.py', 'data/snapshots/validation-phase-9-static.json',
               'data/snapshots/phase-8-reference-2026-11-19.json', '../workflow.json', '%2e%2e/workflow.json']
    leaked = []
    for path in private:
        try:
            with urlopen(f'{BASE}/{path}', timeout=12) as response:
                leaked.append(f'{path}: HTTP {response.status}')
        except HTTPError as error:
            if error.code != 404:
                leaked.append(f'{path}: HTTP {error.code}, HTTP 404 attendu')
        except (URLError, TimeoutError) as error:
            failures.append(f'{path}: {error}')
    if failures or leaked:
        raise AssertionError(f'public manquant={failures[:12]} · privé exposé={leaked}')
    return f'{len(public)} ressources publiques HTTP 200 · {len(private)} chemins privés/quarantinés HTTP 404'


def main():
    report = {'schemaVersion': 1, 'phase': 'PHASE_9', 'status': 'EN_COURS', 'base': BASE,
              'checkedAt': '2026-11-18', 'checks': [], 'errors': []}
    run_check(report, 'HTML, références locales, ancres et métadonnées', audit_pages_and_links)
    run_check(report, 'Illustrations et sources PHASE_9', audit_images_and_sources)
    run_check(report, 'Recherche et sitemap', audit_search_sitemap)
    run_check(report, 'Liste blanche d’aperçu', audit_allowlist)
    run_check(report, 'Workflow, plan éditorial et empreintes enregistrées', audit_workflow_and_plan)
    run_check(report, 'HTTP local et absence d’exposition de fichiers privés', audit_http)
    report['status'] = 'ECHEC' if report['errors'] else 'PASS'
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'\nPHASE_9 static QA {report["status"]} · {len(report["checks"])} contrôles · {REPORT_PATH.relative_to(ROOT)}')
    if report['errors']:
        sys.exit(1)


if __name__ == '__main__':
    main()
