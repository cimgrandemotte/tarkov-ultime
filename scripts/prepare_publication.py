#!/usr/bin/env python3
"""Build an isolated, portable Pages package without touching the preview build."""
from argparse import ArgumentParser
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
sys.path.insert(0, str(SCRIPTS))

from build_home import absolute_base, build  # noqa: E402
from serve_home import PUBLIC_FILES  # noqa: E402
from site_urls import is_preview_base  # noqa: E402

STAGING_BASE = 'https://example.org/'
STAGING_OMISSIONS = {'robots.txt', 'sitemap.xml'}
TAG_RE = re.compile(r'<(?P<tag>meta|link)\b[^>]*>', re.I)
ATTR_RE = re.compile(r'''([^\s=/>]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))''')
JSONLD_RE = re.compile(
    r'(<script\b(?=[^>]*\btype=["\']application/ld\+json["\'])[^>]*>)(.*?)(</script\s*>)',
    re.I | re.S,
)
ROBOTS_RE = re.compile(r'<meta\b(?=[^>]*\bname=["\']robots["\'])[^>]*>', re.I)
HEAD_RE = re.compile(r'<head\b[^>]*>', re.I)


class _TagAttrs(HTMLParser):
    def __init__(self, tag):
        super().__init__(convert_charrefs=True)
        self.tag = tag
        self.attrs = {}

    def handle_starttag(self, tag, attrs):
        if tag.lower() == self.tag.lower():
            self.attrs = {key.lower(): value or '' for key, value in attrs}


def attrs_for_tag(tag_text):
    parser = _TagAttrs('meta' if tag_text[:5].lower() == '<meta' else 'link')
    parser.feed(tag_text)
    return parser.attrs


def remove_domain_bound_meta(html):
    def replace(match):
        tag = match.group(0)
        attrs = attrs_for_tag(tag)
        tag_name = match.group('tag').lower()
        if tag_name == 'link' and 'canonical' in attrs.get('rel', '').lower().split():
            return ''
        if tag_name == 'meta':
            identity = (attrs.get('property') or attrs.get('name') or '').strip().lower()
            if identity in {'og:url', 'twitter:url'} or identity.startswith(('og:image', 'twitter:image')):
                return ''
        return tag
    return TAG_RE.sub(replace, html)


def _scrub_schema(value):
    if isinstance(value, list):
        return [_scrub_schema(item) for item in value]
    if not isinstance(value, dict):
        return value
    cleaned = {}
    for key, item in value.items():
        if key in {'image', 'mainEntityOfPage'}:
            continue
        if key in {'url', '@id'} and isinstance(item, str) and ('example.org' in item.lower() or STAGING_BASE in item):
            continue
        cleaned[key] = _scrub_schema(item)
    return cleaned


def remove_staging_schema_urls(html):
    def replace(match):
        try:
            schema = json.loads(match.group(2))
        except json.JSONDecodeError as exc:
            raise ValueError(f'JSON-LD invalide dans la sortie générée : {exc}') from exc
        sanitized = _scrub_schema(schema)
        payload = json.dumps(sanitized, ensure_ascii=False, separators=(',', ':')).replace('<', r'\\u003c')
        return match.group(1) + payload + match.group(3)
    return JSONLD_RE.sub(replace, html)


def add_staging_noindex(html):
    matches = list(ROBOTS_RE.finditer(html))
    exact = '<meta name="robots" content="noindex,follow">'
    if matches:
        first = True
        def replace(_match):
            nonlocal first
            if first:
                first = False
                return exact
            return ''
        return ROBOTS_RE.sub(replace, html)
    head = HEAD_RE.search(html)
    if not head:
        raise ValueError('Balise <head> absente dans une page de préproduction.')
    return html[:head.end()] + '\n  ' + exact + html[head.end():]


def stage_html(html, relative_path):
    html = remove_domain_bound_meta(html)
    html = remove_staging_schema_urls(html)
    html = add_staging_noindex(html)
    lowered = html.lower()
    forbidden = ('e2b.app', 'example.org', 'rel="canonical"', "rel='canonical'", 'property="og:url"',
                 "property='og:url'", '"mainentityofpage"')
    leaked = [token for token in forbidden if token in lowered]
    if leaked:
        raise ValueError(f'Métadonnées de prévisualisation dans {relative_path}: {leaked}')
    return html


def verify_public_base(base):
    """Require a live, TLS-valid site for this project before emitting public SEO URLs."""
    request = Request(base, headers={'User-Agent': 'TarkovUltimateGuide-publication-preflight/1.0'})
    try:
        with urlopen(request, timeout=18) as response:
            status = response.status
            final_url = response.geturl()
            body = response.read(128_000).decode('utf-8', errors='replace')
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise ValueError(f'Précontrôle HTTPS du domaine échoué : {exc}') from exc
    requested = urlsplit(base)
    final = urlsplit(final_url)
    if status != 200:
        raise ValueError(f'Le domaine public répond HTTP {status}, HTTP 200 attendu.')
    if (final.scheme != 'https' or (final.hostname or '').lower() != (requested.hostname or '').lower()
            or final.path.rstrip('/') != requested.path.rstrip('/')):
        raise ValueError(f'La réponse redirige vers une autre origine ou un autre chemin : {final_url}')
    if 'tarkov ultimate guide' not in body.lower():
        raise ValueError('La page HTTPS répond, mais ne contient pas la signature attendue « Tarkov Ultimate Guide ».')
    return final_url


def package_readme(mode, base, route_count, site_file_count):
    if mode == 'staging':
        status = '''## État du paquet : préproduction portable

Ce paquet est volontairement **non indexable** tant que le dépôt et l’URL publique ne sont pas confirmés : les 87 pages HTML portent `noindex,follow`; `robots.txt` et `sitemap.xml` sont absents; les canoniques, `og:url`, `mainEntityOfPage` et les URL d’images sociales/données structurées liées à un hôte sont omis. Aucun domaine, propriétaire, `CNAME` ou workflow de déploiement n’est inventé.

N’utilisez pas ce paquet comme version SEO finale. Après avoir choisi l’URL, configuré Pages et vérifié que la page de ce site répond en HTTPS avec un certificat valide et sans 404, retournez à la racine du projet source et régénérez le paquet :

```sh
python3 scripts/prepare_publication.py --mode public --base-url 'https://URL-CONFIRMEE/' --confirm-public-base
python3 scripts/qa_publication.py --mode public --base-url 'https://URL-CONFIRMEE/'
```

Le générateur public vérifie à nouveau la réponse HTTPS, crée les métadonnées SEO et le sitemap pour cette base, mais ne publie ni ne déploie rien. L’explication complète se trouve dans `docs/publication-github-pages.md` du projet source.'''
    else:
        status = f'''## État du paquet : SEO public préparé

Base confirmée et testée par requête HTTPS au moment de la génération : `{base}`. Les canoniques, Open Graph, JSON-LD, `robots.txt` et `sitemap.xml` utilisent cette base. Vérifiez à nouveau le domaine et les routes après publication.'''
    return f'''<!-- AUTO-GENERATED by scripts/prepare_publication.py; do not edit this copy. -->
# Tarkov Ultimate Guide — paquet de publication

Le dossier `site/` est la racine web statique à transmettre à l’hébergeur. Il contient **{route_count} routes HTML** et **{site_file_count} fichiers de site**. Aucun ZIP n’est généré : les fichiers restent dans le workspace. Il n’y a ni code serveur ni dépendances de construction. La génération ne publie, ne déploie et ne pousse rien.

{status}

## Publication manuelle avec GitHub Pages

1. Créez ou choisissez vous-même le dépôt et déterminez son URL Pages exacte. Pour un site de projet, elle prend généralement la forme `https://OWNER.github.io/REPOSITORY/`; pour un dépôt utilisateur, `https://OWNER.github.io/`.
2. Choisissez la source de publication dans **Settings → Pages**. Pour un workflow GitHub Actions personnalisé, l’artefact statique doit pointer vers `publication-package/site`, avec les permissions Pages requises.
3. Transférez **le contenu de `site/`**, pas le dossier de documentation du paquet. Ce fichier README n’est pas dans la racine web.
4. Contrôlez les routes, le certificat TLS et l’origine finale dans un navigateur. Si l’adresse ou le chemin de dépôt change, reconstruisez avec la base exacte avant d’utiliser les métadonnées SEO publiques.

Le projet source contient les commandes, les limites connues et les contrôles détaillés dans `docs/publication-github-pages.md`. Aucun dépôt Git distant ni workflow n’a été configuré par ce générateur.
'''


def _prepare_output_dir(output_dir):
    output_dir = output_dir.resolve()
    if output_dir == ROOT or ROOT.is_relative_to(output_dir):
        raise ValueError('Le dossier de sortie ne peut pas être la racine du projet ni un de ses parents.')
    site_dir = output_dir / 'site'
    if site_dir.is_symlink():
        raise ValueError('Le dossier site/ ne peut pas être un lien symbolique.')
    if site_dir.exists():
        marker = output_dir / 'README-PUBLICATION.md'
        if not marker.is_file() or 'AUTO-GENERATED by scripts/prepare_publication.py' not in marker.read_text(encoding='utf-8'):
            raise ValueError(f'{site_dir} existe sans marqueur de paquet généré; refus de le supprimer.')
        shutil.rmtree(site_dir)
    site_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir, site_dir


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument('--mode', choices=('staging', 'public'), default='staging',
                     help='staging: noindex sans sitemap/robots; public: exige base HTTPS vérifiée et opt-in explicite')
    cli.add_argument('--base-url', help='base HTTPS exacte; requise en mode public')
    cli.add_argument('--confirm-public-base', action='store_true',
                     help='confirme que dépôt, routage Pages et domaine sont ceux attendus (ne remplace pas le précontrôle HTTPS)')
    cli.add_argument('--output-dir', default=str(ROOT / 'publication-package'))
    args = cli.parse_args()

    try:
        if args.mode == 'staging':
            if args.confirm_public_base or args.base_url:
                raise ValueError('En mode staging, ne passez ni --base-url ni --confirm-public-base.')
            base = STAGING_BASE
            public_confirmed = False
            omitted = STAGING_OMISSIONS
        else:
            if not args.base_url or not args.confirm_public_base:
                raise ValueError('Le mode public exige --base-url et --confirm-public-base après vérification du domaine.')
            base = absolute_base(args.base_url)
            if is_preview_base(base):
                raise ValueError('Une base locale, réservée ou E2B ne peut pas être utilisée en mode public.')
            verify_public_base(base)
            public_confirmed = True
            omitted = set()

        previous_confirmation = os.environ.pop('TUG_PUBLIC_BASE_CONFIRMED', None)
        if public_confirmed:
            os.environ['TUG_PUBLIC_BASE_CONFIRMED'] = '1'
        try:
            artifacts = build(base)
        finally:
            os.environ.pop('TUG_PUBLIC_BASE_CONFIRMED', None)
            if previous_confirmation is not None:
                os.environ['TUG_PUBLIC_BASE_CONFIRMED'] = previous_confirmation

        expected_html = {name for name in PUBLIC_FILES if name.endswith('.html')}
        generated_html = {name for name in artifacts if name.endswith('.html')}
        if generated_html != expected_html:
            missing = sorted(expected_html - generated_html)
            extra = sorted(generated_html - expected_html)
            raise ValueError(f'Inventaire de routes différent : absentes={missing[:12]}, inattendues={extra[:12]}')

        required_generated = expected_html | {'js/data/search-index.json'} | ({'robots.txt', 'sitemap.xml'} - omitted)
        missing_artifacts = sorted(required_generated - artifacts.keys())
        if missing_artifacts:
            raise ValueError(f'Fichiers générés attendus absents : {missing_artifacts}')

        output_dir, site_dir = _prepare_output_dir(Path(args.output_dir))
        selected = sorted(PUBLIC_FILES - omitted)
        for relative in selected:
            destination = site_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative in artifacts:
                content = artifacts[relative]
                if relative.endswith('.html') and args.mode == 'staging':
                    content = stage_html(content, relative)
                destination.write_text(content, encoding='utf-8')
            else:
                source = ROOT / relative
                if not source.is_file() or source.is_symlink():
                    raise ValueError(f'Fichier statique autorisé absent ou lien symbolique : {relative}')
                shutil.copyfile(source, destination)

        route_count = len(expected_html)
        site_file_count = len(selected)
        readme = package_readme(args.mode, base if public_confirmed else None, route_count, site_file_count)
        (output_dir / 'README-PUBLICATION.md').write_text(readme, encoding='utf-8')
        print(f'Paquet {args.mode} prêt : {route_count} routes HTML · {site_file_count} fichiers site')
        print(f'Dossier : {output_dir}')
        print('Aucune archive ZIP générée.')
        if args.mode == 'staging':
            print('Garde-fous : noindex sur chaque route · pas de canonical/og:url/mainEntityOfPage · pas de sitemap.xml ni robots.txt')
        else:
            print(f'Base publique testée et utilisée : {base}')
        return 0
    except (OSError, ValueError) as exc:
        cli.error(str(exc))


if __name__ == '__main__':
    raise SystemExit(main())
