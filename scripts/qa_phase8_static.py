#!/usr/bin/env python3
"""Contrôles hors ligne et HTTP des routes PHASE_8 et des artefacts du site."""
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import urlopen
import json
import os
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('PHASE8_BASE_URL', 'http://127.0.0.1:4180').rstrip('/')
REPORT_PATH = ROOT / 'data/snapshots/validation-phase-8-static.json'
PAGES = [
    'pages/skills/index.html',
    'pages/economy/index.html', 'pages/economy/flea-market.html', 'pages/economy/money-making.html',
    'pages/strategy/index.html', 'pages/strategy/beginner-tips.html', 'pages/strategy/advanced-tactics.html',
    'pages/strategy/pvp-guide.html', 'pages/strategy/pve-guide.html', 'pages/strategy/meta-builds.html',
]
ROUTES = [
    'pages/skills/', 'pages/economy/', 'pages/economy/flea-market.html', 'pages/economy/money-making.html',
    'pages/strategy/', 'pages/strategy/beginner-tips.html', 'pages/strategy/advanced-tactics.html',
    'pages/strategy/pvp-guide.html', 'pages/strategy/pve-guide.html', 'pages/strategy/meta-builds.html',
]
IMAGES = {
    'images/phase8/skills-field-manual.jpg', 'images/phase8/skills-training-range.jpg',
    'images/phase8/economy-loot.jpg', 'images/phase8/economy-ledger.jpg', 'images/phase8/flea-market.jpg',
    'images/phase8/money-run.jpg', 'images/phase8/strategy-brief.jpg', 'images/phase8/advanced-tactics.jpg',
    'images/phase8/pvp-loadout.jpg', 'images/phase8/pve-prestige.jpg',
}
QUARANTINE = 'phase-8-reference-2026-11-19.json'


class HTMLAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.references = []
        self.images_without_alt = []
        self.used_phase8_images = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get('id'):
            self.ids.append(values['id'])
        if tag == 'img':
            src = values.get('src', '')
            if 'alt' not in values:
                self.images_without_alt.append(src or '<src absent>')
            if src:
                self.references.append(src)
                if 'images/phase8/' in src:
                    self.used_phase8_images.add(src)
            srcset = values.get('srcset', '')
            for candidate in srcset.split(','):
                candidate = candidate.strip().split(' ')[0]
                if candidate:
                    self.references.append(candidate)
                    if 'images/phase8/' in candidate:
                        self.used_phase8_images.add(candidate)
        if tag in ('a', 'link') and values.get('href'):
            self.references.append(values['href'])
        if tag in ('script', 'source', 'audio', 'video') and values.get('src'):
            self.references.append(values['src'])
        if tag == 'video' and values.get('poster'):
            self.references.append(values['poster'])


def fail(message):
    raise AssertionError(message)


def check(report, name, function):
    try:
        detail = function()
        report['checks'].append({'name': name, 'passed': True, 'detail': detail})
        print(f'PASS · {name} · {detail}')
    except Exception as exc:  # retain the full audit trail even on a failed control
        report['checks'].append({'name': name, 'passed': False, 'detail': str(exc)})
        report['errors'].append(f'{name}: {exc}')
        print(f'FAIL · {name} · {exc}')


def audit_local_html():
    issues = []
    total_references = 0
    used_images = set()
    parsed = {}
    for page_file in PAGES:
        file_path = ROOT / page_file
        if not file_path.is_file():
            issues.append(f'fichier absent : {page_file}')
            continue
        parser = HTMLAudit()
        parser.feed(file_path.read_text(encoding='utf-8'))
        parsed[page_file] = parser
        duplicates = sorted(key for key, count in Counter(parser.ids).items() if count > 1)
        if duplicates:
            issues.append(f'{page_file} : IDs dupliqués {duplicates}')
        if parser.images_without_alt:
            issues.append(f'{page_file} : images sans alt {parser.images_without_alt}')
        html = file_path.read_text(encoding='utf-8')
        for private_string in (QUARANTINE, 'data/snapshots/phase-8-reference', '19 novembre 2026', '2026-11-19'):
            if private_string in html:
                issues.append(f'{page_file} : référence privée/future {private_string}')
        used_images.update(unquote(urlsplit(urljoin(f'https://local.test/{page_file}', src)).path.lstrip('/'))
                           for src in parser.used_phase8_images)
        for reference in parser.references:
            resolved = urlsplit(urljoin(f'https://local.test/{page_file}', reference))
            if resolved.scheme not in ('http', 'https') or resolved.netloc != 'local.test':
                continue
            total_references += 1
            target_name = unquote(resolved.path.lstrip('/')) or 'index.html'
            target = (ROOT / target_name).resolve()
            if ROOT.resolve() not in target.parents and target != ROOT.resolve():
                issues.append(f'{page_file} : référence hors workspace {reference}')
                continue
            if target.is_dir():
                target = target / 'index.html'
            if not target.is_file():
                issues.append(f'{page_file} : cible locale absente {reference}')
                continue
            if resolved.fragment and target.suffix == '.html':
                fragment = unquote(resolved.fragment)
                destination = target.relative_to(ROOT).as_posix()
                if destination not in parsed:
                    target_parser = HTMLAudit()
                    target_parser.feed(target.read_text(encoding='utf-8'))
                    ids = set(target_parser.ids)
                else:
                    ids = set(parsed[destination].ids)
                if fragment not in ids:
                    issues.append(f'{page_file} : fragment manquant {reference}')
    missing_images = sorted(IMAGES - used_images)
    extra_images = sorted(used_images - IMAGES)
    for image in IMAGES:
        image_path = ROOT / image
        if not image_path.is_file() or image_path.stat().st_size < 20_000 or not image_path.read_bytes().startswith(b'\xff\xd8'):
            issues.append(f'illustration JPG absente ou invalide : {image}')
    if missing_images:
        issues.append(f'illustrations attendues non intégrées : {missing_images}')
    if extra_images:
        issues.append(f'illustrations PHASE_8 imprévues : {extra_images}')
    if issues:
        fail('; '.join(issues[:20]))
    return f'{len(PAGES)} pages · {total_references} liens/assets/ancres · {len(IMAGES)} JPG intégrées'


def audit_build_artifacts():
    search_path = ROOT / 'js/data/search-index.json'
    search = json.loads(search_path.read_text(encoding='utf-8'))
    records = search.get('records', [])
    hrefs = Counter(record.get('href', '') for record in records)
    missing_search = sorted(route for route in ROUTES if hrefs[route] != 1)
    if missing_search:
        fail(f'route absente/dupliquée dans la recherche : {missing_search}')
    if search.get('updatedAt') != '2026-11-18':
        fail(f'date de l’index inattendue : {search.get("updatedAt")}')
    if QUARANTINE in search_path.read_text(encoding='utf-8'):
        fail('référence à l’instantané quarantiné dans l’index')

    sitemap_path = ROOT / 'sitemap.xml'
    sitemap_text = sitemap_path.read_text(encoding='utf-8')
    sitemap = ET.fromstring(sitemap_text)
    locations = [node.text or '' for node in sitemap.iter() if node.tag.split('}')[-1] == 'loc']
    sitemap_paths = [urlsplit(location).path.lstrip('/') for location in locations]
    if len(locations) != 77 or len(set(locations)) != len(locations):
        fail(f'le sitemap doit comporter 77 URLs uniques, pas {len(locations)}')
    missing_sitemap = sorted(route for route in ROUTES if route not in sitemap_paths)
    if missing_sitemap:
        fail(f'route absente du sitemap : {missing_sitemap}')
    if QUARANTINE in sitemap_text or '2026-11-19' in sitemap_text:
        fail('référence à l’instantané quarantiné dans le sitemap')
    return f'{len(records)} entrées de recherche · 77 URLs uniques · 10 routes PHASE_8 dans les deux'


def audit_workflow_state():
    workflow = json.loads((ROOT / 'workflow.json').read_text(encoding='utf-8'))
    machine = json.loads((ROOT / 'state_machine.json').read_text(encoding='utf-8'))
    plan = json.loads((ROOT / 'docs/plan-editorial.json').read_text(encoding='utf-8'))
    state = machine['instantane']
    if state['etat'] != workflow['etat_global'] or state['phase_active'] != workflow['phase_active']:
        fail('états Workflow / state machine désynchronisés')
    if state['prochaine_phase'] != workflow['prochaine_phase'] or not state['attend_confirmation']:
        fail('garde de confirmation PHASE_9 désynchronisée')
    if state['derniere_phase_terminee'] != 'PHASE_8' or workflow['phase_active'] is not None:
        fail('PHASE_8 doit être achevée et PHASE_9 en attente')
    planned = {row['fichier'] for row in plan['pages']}
    existing = {route for route in planned if (ROOT / route).is_file()}
    page_records = {row['fichier']: row for row in workflow['production']['pages_livrees']}
    if len(planned) != 87 or len(existing) != 77 or workflow['production']['pages_generees'] != 77:
        fail(f'compteurs du plan/build incohérents : {len(planned)} planifiées, {len(existing)} présentes')
    if set(page_records) != existing:
        fail('inventaire des pages livrées différent des fichiers générés')
    p8_planned = {row['fichier'] for row in plan['pages'] if row['phase'] == 'PHASE_8'}
    p8_delivered = {row['fichier'] for row in workflow['production']['pages_livrees'] if row['phase'] == 'PHASE_8'}
    p8_phase = next(row for row in workflow['phases'] if row['id'] == 'PHASE_8')
    if p8_planned != set(PAGES) or p8_delivered != set(PAGES) or p8_phase['statut'] != 'TERMINE' or p8_phase['pages_generees'] != 10:
        fail('inventaire de livraison PHASE_8 incohérent')
    if any(row['statut'] != 'LIVREE' for row in plan['pages'] if row['phase'] == 'PHASE_8'):
        fail('une route PHASE_8 reste marquée PLANIFIEE')
    image_rows = [row for row in workflow['production']['images_creees'] if row['phase'] == 'PHASE_8']
    image_files = {path.relative_to(ROOT).as_posix() for path in (ROOT / 'images/phase8').glob('*.jpg')}
    if {row['fichier'] for row in image_rows} != IMAGES or image_files != IMAGES:
        fail('inventaire des dix JPG PHASE_8 désynchronisé')
    for row in image_rows:
        raw = (ROOT / row['fichier']).read_bytes()
        import hashlib
        if row.get('octets') != len(raw) or row.get('sha256') != hashlib.sha256(raw).hexdigest():
            fail(f'empreinte du média divergente : {row["fichier"]}')
    return 'workflow synchronisé · 77/87 pages · PHASE_8 10/10 · 10 JPG vérifiés'


def audit_preview_http():
    public = ROUTES + [
        'css/pages/phase8.css', 'js/phase8.js', 'js/data/search-index.json', 'sitemap.xml', 'robots.txt',
    ] + sorted(IMAGES)
    failures = []
    for path in public:
        try:
            with urlopen(f'{BASE}/{path}', timeout=15) as response:
                if response.status != 200:
                    failures.append(f'{path}: HTTP {response.status}')
        except (HTTPError, URLError, TimeoutError) as exc:
            failures.append(f'{path}: {exc}')
    private = [
        f'data/snapshots/{QUARANTINE}', 'data/snapshots/validation-phase-8.json',
        'data/snapshots/validation-phase-8-static.json', 'docs/sources.json', 'scripts/phase8_pages.py',
        '../workflow.json',
    ]
    leaked = []
    for path in private:
        try:
            with urlopen(f'{BASE}/{path}', timeout=15) as response:
                leaked.append(f'{path}: HTTP {response.status}')
        except HTTPError as exc:
            if exc.code != 404:
                leaked.append(f'{path}: HTTP {exc.code}, HTTP 404 attendu')
        except (URLError, TimeoutError) as exc:
            failures.append(f'{path}: {exc}')
    if failures or leaked:
        fail(f'public manquant={failures[:10]} · privé exposé={leaked}')
    return f'{len(public)} ressources HTTP 200 · {len(private)} chemins privés/instantanés HTTP 404'


def main():
    report = {
        'schemaVersion': 1,
        'phase': 'PHASE_8',
        'status': 'EN_COURS',
        'base': BASE,
        'checkedAt': datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'checks': [],
        'errors': [],
    }
    check(report, 'Audit statique des pages, références, ancres, alts et illustrations', audit_local_html)
    check(report, 'Index de recherche et sitemap', audit_build_artifacts)
    check(report, 'Inventaire du workflow et des médias', audit_workflow_state)
    check(report, 'Liste blanche HTTP du serveur d’aperçu et quarantaine', audit_preview_http)
    report['status'] = 'ECHEC' if report['errors'] else 'PASS'
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'\nPHASE_8 static QA {report["status"]} · {len(report["checks"])} vérifications · rapport {REPORT_PATH.relative_to(ROOT)}')
    if report['errors']:
        sys.exit(1)


if __name__ == '__main__':
    main()
