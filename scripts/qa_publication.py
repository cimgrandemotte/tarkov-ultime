#!/usr/bin/env python3
"""Check a staging or public Pages package without serving or publishing it."""
from argparse import ArgumentParser
from collections import Counter
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from build_home import absolute_base  # noqa: E402
from serve_home import DIRECTORY_ROUTES, PUBLIC_FILES  # noqa: E402
from site_urls import is_preview_base  # noqa: E402
from phase10_pages import PAGES as PHASE10_PAGES, validate_phase10  # noqa: E402

STAGING_OMISSIONS = {'robots.txt', 'sitemap.xml'}
FORBIDDEN_STAGING = ('e2b.app', 'example.org')
REPORT_PATH = ROOT / 'data/snapshots/validation-publication.json'


class PageAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.h1_count = 0
        self.lang = ''
        self.title = ''
        self.in_title = False
        self.references = []
        self.images = []
        self.meta = []
        self.links = []
        self.jsonld = []
        self.in_jsonld = False

    def handle_starttag(self, tag, attrs):
        values = {key.lower(): value or '' for key, value in attrs}
        if tag == 'html':
            self.lang = values.get('lang', '')
        if values.get('id'):
            self.ids.append(values['id'])
        if tag == 'h1':
            self.h1_count += 1
        if tag == 'title':
            self.in_title = True
        if tag == 'meta':
            self.meta.append(values)
        if tag == 'link':
            self.links.append(values)
        if tag in {'a', 'link'} and values.get('href'):
            self.references.append(values['href'])
        if tag in {'img', 'script', 'source', 'audio', 'video', 'track', 'iframe'} and values.get('src'):
            self.references.append(values['src'])
        if tag == 'img':
            self.images.append(values)
            for candidate in values.get('srcset', '').split(','):
                candidate = candidate.strip().split()
                if candidate:
                    self.references.append(candidate[0])
        if tag == 'video' and values.get('poster'):
            self.references.append(values['poster'])
        if tag == 'object' and values.get('data'):
            self.references.append(values['data'])
        if tag == 'script' and values.get('type', '').lower() == 'application/ld+json':
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


def route_for_file(name):
    if name == 'index.html':
        return '/'
    if name.endswith('/index.html'):
        return '/' + name[:-len('index.html')]
    return '/' + name


def file_for_url(path):
    if path in ('', '/'):
        return 'index.html'
    if path in DIRECTORY_ROUTES:
        return DIRECTORY_ROUTES[path]
    name = unquote(path.lstrip('/'))
    if name.endswith('/'):
        name += 'index.html'
    return name


def local_target(page, reference):
    resolved = urlsplit(urljoin('https://qa.invalid' + route_for_file(page), reference))
    if resolved.scheme not in {'http', 'https'} or resolved.netloc != 'qa.invalid':
        return None, resolved
    return file_for_url(resolved.path), resolved


def walk_strings(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_strings(item)
    elif isinstance(value, str):
        yield value


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument('--mode', choices=('staging', 'public'), default='staging')
    cli.add_argument('--site-root', default=str(ROOT / 'publication-package' / 'site'))
    cli.add_argument('--base-url', help='base HTTPS attendue en mode public')
    args = cli.parse_args()

    errors = []
    checks = []
    try:
        site_root = Path(args.site_root).resolve()
        if not site_root.is_dir():
            raise ValueError(f'Dossier de site absent : {site_root}')
        validate_phase10()
        if args.mode == 'public':
            if not args.base_url:
                raise ValueError('Le mode public exige --base-url.')
            base = absolute_base(args.base_url)
            if is_preview_base(base):
                raise ValueError('La base publique ne peut pas être locale, réservée ou E2B.')
            omissions = set()
        else:
            if args.base_url:
                raise ValueError('Ne passez pas --base-url pour l’audit staging.')
            base = None
            omissions = STAGING_OMISSIONS

        expected = set(PUBLIC_FILES - omissions)
        actual = {path.relative_to(site_root).as_posix() for path in site_root.rglob('*') if path.is_file()}
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing or extra:
            errors.append(f'Inventaire fichiers incorrect : absents={missing[:12]}, inattendus={extra[:12]}')
        else:
            checks.append(f'{len(actual)} fichiers du paquet, inventaire exact')

        html_files = sorted(name for name in actual if name.endswith('.html'))
        if len(html_files) != 87:
            errors.append(f'87 routes HTML attendues, {len(html_files)} trouvées.')
        else:
            checks.append('87 routes HTML présentes')

        cache = {}
        def page(name):
            if name not in cache:
                audit = PageAudit()
                audit.feed((site_root / name).read_text(encoding='utf-8'))
                cache[name] = audit
            return cache[name]

        local_refs = 0
        fragments = 0
        metadata_pages_validated = 0
        for name in html_files:
            metadata_errors_before = len(errors)
            path = site_root / name
            text = path.read_text(encoding='utf-8')
            lower = text.lower()
            audit = page(name)
            if audit.lang not in {'fr', 'fr-FR'} or audit.h1_count != 1 or not audit.title.strip():
                errors.append(f'{name}: langue, titre ou H1 invalide ({audit.lang}, H1={audit.h1_count}).')
            duplicates = [key for key, count in Counter(audit.ids).items() if count > 1]
            if duplicates:
                errors.append(f'{name}: identifiants HTML dupliqués : {duplicates[:8]}')
            if any('alt' not in image for image in audit.images):
                errors.append(f'{name}: image sans attribut alt.')
            if '[[' in text:
                errors.append(f'{name}: jeton de template non remplacé.')
            if not audit.jsonld:
                errors.append(f'{name}: JSON-LD absent.')
            schemas = []
            for block in audit.jsonld:
                try:
                    schemas.append(json.loads(block))
                except json.JSONDecodeError as exc:
                    errors.append(f'{name}: JSON-LD invalide ({exc}).')
            for schema in schemas:
                joined = '\n'.join(walk_strings(schema)).lower()
                if any(host in joined for host in FORBIDDEN_STAGING):
                    errors.append(f'{name}: base de prévisualisation/réservée dans JSON-LD.')

            robots = [m for m in audit.meta if m.get('name', '').lower() == 'robots']
            canonicals = [l for l in audit.links if 'canonical' in l.get('rel', '').lower().split()]
            og_urls = [m for m in audit.meta if m.get('property', '').lower() == 'og:url']
            og_images = [m for m in audit.meta if m.get('property', '').lower().startswith('og:image')]
            twitter_images = [m for m in audit.meta if m.get('name', '').lower().startswith('twitter:image')]
            if args.mode == 'staging':
                if len(robots) != 1 or robots[0].get('content', '').lower() != 'noindex,follow':
                    errors.append(f'{name}: staging doit porter exactement noindex,follow.')
                if canonicals or og_urls or any('mainentityofpage' in '\\n'.join(walk_strings(schema)).lower() for schema in schemas):
                    errors.append(f'{name}: métadonnée canonique publique interdite en staging.')
                if og_images or twitter_images:
                    errors.append(f'{name}: métadonnée d’image sociale liée à un hôte en staging.')
                leaked = [host for host in FORBIDDEN_STAGING if host in lower]
                if leaked:
                    errors.append(f'{name}: hôte réservé/aperçu dans le HTML : {leaked}')
            else:
                if robots:
                    errors.append(f'{name}: le paquet public contient encore une directive robots {robots[0].get("content", "")}.')
                route = route_for_file(name)
                expected_url = urljoin(base, route.lstrip('/'))
                if len(canonicals) != 1 or canonicals[0].get('href') != expected_url:
                    errors.append(f'{name}: canonical absent ou différent de {expected_url}.')
                if len(og_urls) != 1 or og_urls[0].get('content') != expected_url:
                    errors.append(f'{name}: og:url absent ou différent de {expected_url}.')
                for meta in og_images + twitter_images:
                    image_url = meta.get('content', '')
                    if not image_url.startswith(base):
                        errors.append(f'{name}: image sociale hors de la base publique : {image_url}')
                if any(host in lower for host in FORBIDDEN_STAGING):
                    errors.append(f'{name}: hôte aperçu/réservé dans la version publique.')
                for schema in schemas:
                    if any(host in '\n'.join(walk_strings(schema)).lower() for host in FORBIDDEN_STAGING):
                        errors.append(f'{name}: hôte aperçu/réservé dans JSON-LD public.')

            if len(errors) == metadata_errors_before:
                metadata_pages_validated += 1
            for reference in audit.references:
                target_name, resolved = local_target(name, reference)
                if target_name is None:
                    continue
                local_refs += 1
                if target_name not in expected or not (site_root / target_name).is_file():
                    errors.append(f'{name}: cible locale absente/non autorisée : {reference} → {target_name}')
                    continue
                if resolved.fragment and target_name.endswith('.html'):
                    fragments += 1
                    if unquote(resolved.fragment) not in set(page(target_name).ids):
                        errors.append(f'{name}: fragment local absent : {reference}')

        if metadata_pages_validated == len(html_files):
            if args.mode == 'staging':
                checks.append('87 pages: noindex, sans canonical/og:url/mainEntityOfPage ni URL de prévisualisation')
            else:
                checks.append('87 pages: canonical et og:url alignés sur la base publique confirmée')

        source_registry = json.loads((ROOT / 'docs/sources.json').read_text(encoding='utf-8'))['sources']
        verified_source_facts = {
            'bsg-technical-diary-135': ('18/11/2026', '1.3.5.0', 'seconde moitié de novembre',
                                        'sans jour précis', 'ni annonce d’installation'),
            'bsg-news-index': ('18/11/2026', '1.3.0.0', 'dernière note de patch numérotée'),
        }
        for source_key, required_facts in verified_source_facts.items():
            record = source_registry.get(source_key, {})
            evidence = ' '.join(str(record.get(field, '')) for field in ('usage_phase_10', 'date_releve_phase_10')).casefold()
            missing_facts = [fact for fact in required_facts if fact.casefold() not in evidence]
            if missing_facts:
                errors.append(f'Registre sources : état/date vérifié manquant pour {source_key} : {missing_facts}')
        if not any('Registre sources :' in error for error in errors):
            checks.append('Registre sources : contrôle du journal BSG du 18/11 et de l’index (1.3.0.0 dernière note numérotée)')
        for phase_page in PHASE10_PAGES:
            file = phase_page['file']
            path = site_root / file
            if not path.is_file():
                errors.append(f'Route PHASE_10 absente du paquet : {file}')
                continue
            text = path.read_text(encoding='utf-8')
            if ('css/pages/phase10.css' not in text or 'js/phase10.js' not in text
                    or f'data-phase10-page="{phase_page["id"]}"' not in text):
                errors.append(f'{file}: CSS, module ou marqueur de page PHASE_10 absent.')
            for key in phase_page['sources']:
                source = source_registry[key]
                if escape(source.get('url', ''), quote=True) not in text:
                    errors.append(f'{file}: source éditoriale non reliée au paquet : {key}')
        patch_page = site_root / 'pages/patch-notes.html'
        if patch_page.is_file():
            patch_text = patch_page.read_text(encoding='utf-8')
            required_patch_facts = ('1.3.0.0', '1.3.5.0', 'seconde moitié de novembre',
                                    'sans jour précis', 'aucune annonce bsg d’installation',
                                    '18 novembre 2026', 'upgrade', '1.3.5.0 avant la mise à jour',
                                    'DirectX 12', 'DLSS Frame Generation x2/x4', 'NVIDIA Reflex', 'FSR 4')
            absent_facts = [fact for fact in required_patch_facts if fact.casefold() not in patch_text.casefold()]
            if absent_facts:
                errors.append(f'Notes de patch : mention/version officielle manquante ou statut incomplet : {absent_facts}')
            elif not any('Notes de patch' in item for item in errors):
                checks.append('PHASE_10 : 3 routes, sources liées et statut 1.3.5.0 distingué du déploiement')

        home_path = site_root / 'index.html'
        if home_path.is_file():
            home_text = home_path.read_text(encoding='utf-8')
            required_home_facts = ('Upgrade — Prepare 1.3.5.0 avant la mise à jour',
                                   'aucune installation confirmée au 18/11',
                                   'news/id/420?lang=en')
            absent_home_facts = [fact for fact in required_home_facts if fact.casefold() not in home_text.casefold()]
            if absent_home_facts:
                errors.append(f'Accueil : mention Upgrade/statut 1.3.5.0 ou source BSG manquante : {absent_home_facts}')
            else:
                checks.append('Accueil : mention Upgrade, date de vérification et source BSG reliées')

        if args.mode == 'public':
            sitemap_path = site_root / 'sitemap.xml'
            robots_path = site_root / 'robots.txt'
            try:
                root = ET.parse(sitemap_path).getroot()
                locations = [node.text or '' for node in root.iter() if node.tag.split('}')[-1] == 'loc']
                expected_urls = {urljoin(base, route_for_file(name).lstrip('/')) for name in html_files}
                if len(locations) != 87 or set(locations) != expected_urls:
                    errors.append(f'Sitemap incorrect : {len(locations)} URLs, 87 attendues pour la base publique.')
                else:
                    checks.append('sitemap.xml : 87 URL publiques exactes')
            except (OSError, ET.ParseError) as exc:
                errors.append(f'sitemap.xml absent/invalide : {exc}')
            try:
                robots_text = robots_path.read_text(encoding='utf-8')
                if f'Sitemap: {urljoin(base, "sitemap.xml")}' not in robots_text or 'e2b.app' in robots_text.lower():
                    errors.append('robots.txt : URL sitemap incorrecte ou lien E2B résiduel.')
                else:
                    checks.append('robots.txt référence uniquement le sitemap de la base publique')
            except OSError as exc:
                errors.append(f'robots.txt absent : {exc}')
        else:
            if (site_root / 'sitemap.xml').exists() or (site_root / 'robots.txt').exists():
                errors.append('Le paquet staging ne doit contenir ni sitemap.xml ni robots.txt.')
            else:
                checks.append('aucun sitemap.xml/robots.txt E2B dans le paquet staging')

        if local_refs and not any('cible locale' in error or 'fragment local' in error for error in errors):
            checks.append(f'{local_refs:,} références locales et {fragments:,} fragments vérifiés')

        archive_path = ROOT / 'publication-package.zip'
        archive_present = archive_path.exists() or archive_path.is_symlink()
        if archive_present:
            errors.append('publication-package.zip présent; l’archive doit rester absente selon la demande utilisateur.')
        else:
            checks.append('QA du dossier uniquement; publication-package.zip absent et aucune archive générée')

        report = {
            'schemaVersion': 1,
            'task': 'publication-package',
            'mode': args.mode,
            'status': 'FAIL' if errors else 'PASS',
            'base': base,
            'files': len(actual),
            'htmlRoutes': len(html_files),
            'localReferences': local_refs,
            'localFragments': fragments,
            'archiveGenerated': False,
            'archivePresent': archive_present,
            'checks': checks,
            'errors': errors,
        }
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'Publication package QA {report["status"]} · mode={args.mode} · {len(html_files)} routes · {len(actual)} fichiers')
        for check in checks:
            print(f'  PASS  {check}')
        for error in errors[:50]:
            print(f'  FAIL  {error}')
        print(f'Rapport JSON : {REPORT_PATH.relative_to(ROOT)}')
        return 1 if errors else 0
    except (OSError, ValueError) as exc:
        cli.error(str(exc))


if __name__ == '__main__':
    raise SystemExit(main())
