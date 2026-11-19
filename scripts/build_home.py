#!/usr/bin/env python3
"""Assemble les routes éditoriales statiques, l’index et les métadonnées."""
from argparse import ArgumentParser
from datetime import datetime, date
from html import escape
import json
import os
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit
from xml.sax.saxutils import escape as xml_escape
from zoneinfo import ZoneInfo

from guide_pages import DATA as GUIDES_DATA, build_guides
from map_pages import DATA as MAPS_DATA, SNAPSHOT as MAPS_SNAPSHOT, build_maps
from weapon_pages import DATA as PHASE5_DATA, build_phase5
from phase6_pages import build_phase6
from phase7_pages import PAGES as PHASE7_PAGES, build_phase7
from phase8_pages import PAGES as PHASE8_PAGES, build_phase8
from phase9_pages import PAGES as PHASE9_PAGES, build_phase9
from phase10_pages import PAGES as PHASE10_PAGES, build_phase10
from site_urls import seo_base_is_public, is_preview_base, canonical_link, open_graph_url_meta

ROOT = Path(__file__).resolve().parents[1]
PREVIEW_PORT = 4180
IMAGE = 'images/hero/norvinsk-rain.jpg'
TEMPLATE = 'templates/index.html.in'
TITLE = 'Tarkov Ultimate Guide | Guide Escape from Tarkov FR'
DESCRIPTION = 'Préparez votre premier raid dans Escape from Tarkov : cartes, extractions, équipement, boss, actualités vérifiées et repères pour le PvE et SP‑Tushonka.'
MONTHS = 'janvier février mars avril mai juin juillet août septembre octobre novembre décembre'.split()


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('<', r'\u003c')


def fmt_day(day, year=True):
    return f'{day.day} {MONTHS[day.month-1]}' + (f' {day.year}' if year else '')


def fr_number(n):
    return f'{n:,}'.replace(',', '\u202f')


def absolute_base(value):
    url = urlsplit(value)
    if url.scheme != 'https' or not url.hostname or url.username or url.password or url.query or url.fragment or not re.fullmatch(r'(?:/[A-Za-z0-9._~-]+)*/?', url.path):
        raise ValueError('Indiquer l’URL HTTPS du guide, sans identifiants, requête ni fragment.')
    if any(segment in {'.', '..'} for segment in url.path.split('/')) or url.path.endswith('.html'):
        raise ValueError('L’URL de base doit désigner un répertoire, pas un fichier.')
    return value.rstrip('/') + '/'


def base_from_args(value):
    if value:
        return absolute_base(value)
    if env := os.getenv('TUG_PUBLIC_BASE'):
        return absolute_base(env)
    if sandbox := os.getenv('E2B_SANDBOX_ID'):
        return absolute_base(f'https://{PREVIEW_PORT}-{sandbox}.e2b.app/')
    raise ValueError('Passer --base-url avec l’origine publique HTTPS du guide.')


def audio_config(data):
    mapping = {'city': 'ambient_city', 'rain': 'ambient_rain', 'forest': 'ambient_forest', 'industrial': 'ambient_industrial'}
    library = {Path(row['file']).stem: row for row in data if row['loop']}
    return {'tracks': [{'id': id_, 'src': './' + library[name]['file'], 'label': library[name]['title']} for id_, name in mapping.items()], 'cues': []}


def render_news(item):
    a = {key: escape(str(value), quote=True) for key, value in item.items()}
    day = date.fromisoformat(item['date'])
    return (f'<li class="news-row" id="{a["id"]}" data-news-type="{a["type"]}" tabindex="-1">'
            f'<time class="news-row__date" datetime="{a["date"]}"><span class="sr-only">{fmt_day(day)}</span>'
            f'<strong aria-hidden="true">{a["day"]}</strong><span aria-hidden="true">{a["month"]}</span></time>'
            f'<article><p class="news-row__meta"><span class="news-row__type">{a["typeLabel"]}</span>'
            f'<span class="news-row__status" data-tone="{a["tone"]}">{a["status"]}</span></p>'
            f'<h3>{a["title"]}</h3><p class="news-row__summary">{a["summary"]}</p>'
            f'<a class="news-row__link" href="{a["url"]}">{a["sourceLabel"]} <span aria-hidden="true">↗</span></a></article></li>')


def build(base):
    home, manifest, audio = [json.loads(read(f)) for f in ('data/home.json', 'js/data/catalog-manifest.json', 'audio/manifest.json')]
    guides = json.loads(read(GUIDES_DATA))
    map_data = json.loads(read(MAPS_DATA))
    map_snapshot = json.loads(read(MAPS_SNAPSHOT))
    sources = json.loads(read('docs/sources.json'))['sources']
    editorial_plan = json.loads(read('docs/plan-editorial.json'))
    by_kind = {page['kind']: page for page in guides['pages']}
    counts = {name: row['count'] for name, row in manifest['modes']['regular']['files'].items()}
    local = ZoneInfo('Europe/Paris')
    collected = datetime.fromisoformat(manifest['collectedAt']).astimezone(local)
    review = datetime.fromisoformat(home['verifiedAt']).astimezone(local)
    guide_review = datetime.fromisoformat(guides['verifiedAt']).astimezone(local)
    map_review = datetime.fromisoformat(map_data['verifiedAt']).astimezone(local)
    patch = home['patch']
    maps = len(set(home['maps']['locations']))
    news = sorted(home['news'], key=lambda row: row['date'], reverse=True)
    public_seo_base = seo_base_is_public(base)
    og = urljoin(base, IMAGE)
    schema = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Tarkov Ultimate Guide',
              'inLanguage': 'fr-FR', 'description': DESCRIPTION, 'dateModified': review.isoformat(),
              'image': {'@type': 'ImageObject', 'url': og, 'width': 1376, 'height': 768}}
    if public_seo_base:
        schema['url'] = base
    metrics = [(maps, 'Lieux principaux'), (counts['weapons'], 'Armes en jeu'), (counts['ammo'], 'Munitions'),
               (counts['armor'], 'Armures & portage'), (counts['items'], 'Objets indexés')]
    values = {
        'STARTER_URL': './' + by_kind['starter']['route'], 'LORE_URL': './' + by_kind['lore']['route'],
        'DESCRIPTION': DESCRIPTION, 'SEO_TITLE': TITLE, 'BASE_URL': base, 'OG_IMAGE': og,
        'SPT_STABLE': home['tushonka']['stable'], 'SPT_BUILD': home['tushonka']['baseBuild'], 'SPT_RELEASE': home['tushonka']['release'],
        'MAP_SOURCE': home['maps']['source'], 'MAP_COUNT': str(maps), 'WEAPON_COUNT': fr_number(counts['weapons']),
        'PATCH': patch['reference'], 'PATCH_DATE': patch['publishedOn'], 'PATCH_LABEL': patch['publishedLabel'], 'PATCH_URL': patch['officialUrl'],
        'CLIENT_BUILD': patch['clientBuildWiki'], 'CLIENT_LABEL': fmt_day(date.fromisoformat(patch['clientBuildDate']), year=False),
        'CLIENT_WIKI': patch['clientBuildSource'], 'NEXT_PATCH': patch['nextAnnounced'],
        'NEXT_WINDOW': patch['nextWindow'], 'NEXT_PATCH_URL': patch['nextSource'],
        'DATE_ISO': review.isoformat(), 'DATE_SHORT': review.strftime('%d.%m.%Y'), 'DATE_LONG': fmt_day(review.date()),
        'CATALOG_DATE_ISO': collected.isoformat(), 'CATALOG_DATE': fmt_day(collected.date()) + f' à {collected.hour} h {collected.minute:02d} (Paris)',
        'NEWS_COUNT': str(len(news)),
    }
    slots = {key: escape(value, quote=True) for key, value in values.items()}
    slots.update({
        'CANONICAL_LINK': canonical_link(base, ''),
        'OG_URL_META': open_graph_url_meta(base, ''),
        'JSON_LD': compact(schema),
        'AUDIO_CONFIG': compact(audio_config(audio['tracks'])),
        'METRICS': '\n          '.join(f'<div class="home-metrics__item"><dt>{escape(label)}</dt><dd>{fr_number(n)}</dd></div>' for n, label in metrics),
        'NEWS': '\n                '.join(render_news(row) for row in news),
    })
    html = re.sub(r'\[\[([A-Z_]+)\]\]', lambda m: slots[m[1]], read(TEMPLATE))
    featured = guides['search'][:2]
    map_output, map_search = build_maps(map_data, map_snapshot, sources, base,
                                        fmt_day(map_review.date()), patch['reference'], read, compact)
    phase5_output, phase5_search, phase5_review = build_phase5(
        home, editorial_plan, sources, base, patch['reference'], read, compact)
    phase6_output, phase6_search, phase6_review = build_phase6(base, patch['reference'], compact)
    phase7_output, phase7_search, phase7_review = build_phase7(base, patch['reference'], read, compact)
    phase8_output, phase8_search, phase8_review = build_phase8(base, patch['reference'], read, compact)
    phase9_output, phase9_search, phase9_review = build_phase9(base, patch['reference'], read, compact)
    phase10_output, phase10_search, phase10_review = build_phase10(base, patch['reference'], read, compact)
    records = featured + home['search'] + guides['search'][2:] + [
        {'title': row['title'], 'href': '#' + row['id'], 'tag': row['typeLabel'], 'summary': row['summary'],
         'keywords': [row['status']]} for row in news]
    records += [
        {'title': map_data['overview']['title'], 'href': 'pages/maps/', 'tag': 'Index des cartes',
         'summary': map_data['overview']['lead'], 'keywords': [row['name'] for row in map_data['maps']]},
        *map_search,
        *phase5_search,
        *phase6_search,
        *phase7_search,
        *phase8_search,
        *phase9_search,
        *phase10_search,
    ]
    updated_day = max(review.date(), guide_review.date(), map_review.date(), phase5_review.date(), phase6_review.date(), phase7_review.date(), phase8_review, phase9_review, phase10_review)
    index = {'schemaVersion': 1, 'language': 'fr-FR', 'updatedAt': updated_day.isoformat(), 'records': records}
    rows = ([(base, review.date())]
            + [(urljoin(base, page['route']), guide_review.date()) for page in guides['pages']]
            + [(urljoin(base, 'pages/maps/'), map_review.date())]
            + [(urljoin(base, page['route']), map_review.date()) for page in map_data['maps']]
            + [(urljoin(base, page['route']), phase5_review.date()) for page in json.loads(read(PHASE5_DATA))['pages']]
            + [(urljoin(base, page['route']), phase6_review.date()) for page in json.loads(read('data/phase6.json'))['armorPages']]
            + [(urljoin(base, page['route']), phase6_review.date()) for page in [json.loads(read('data/phase6.json'))['bossHub'], *json.loads(read('data/phase6.json'))['bossProfiles']]]
            + [(urljoin(base, page['route']), phase7_review.date()) for page in PHASE7_PAGES]
            + [(urljoin(base, page['route']), phase8_review) for page in PHASE8_PAGES]
            + [(urljoin(base, page['route']), phase9_review) for page in PHASE9_PAGES]
            + [(urljoin(base, page['route']), phase10_review) for page in PHASE10_PAGES])
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + ''.join(f'  <url><loc>{xml_escape(loc)}</loc><lastmod>{day}</lastmod></url>\n' for loc, day in rows)
               + '</urlset>\n')
    robots = f'User-agent: *\nDisallow: {urlsplit(urljoin(base, "lab/")).path}\nSitemap: {urljoin(base, "sitemap.xml")}\n'
    dossier_files = build_guides(guides, sources, base, patch['reference'], guide_review, fmt_day(guide_review.date()), read, compact)
    return {'index.html': html, **dossier_files, **map_output, **phase5_output, **phase6_output, **phase7_output, **phase8_output, **phase9_output, **phase10_output, 'js/data/search-index.json': json.dumps(index, ensure_ascii=False, indent=2) + '\n',
            'sitemap.xml': sitemap, 'robots.txt': robots}


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument('--base-url', help='URL HTTPS, par défaut TUG_PUBLIC_BASE ou l’aperçu Arena')
    cli.add_argument('--confirm-public-base', action='store_true', help='autoriser canonical/og:url/mainEntityOfPage et sitemap uniquement après vérification effective du domaine, TLS et de GitHub Pages')
    cli.add_argument('--check', action='store_true', help='comparer les fichiers sans écrire')
    args = cli.parse_args()
    try:
        base = base_from_args(args.base_url)
    except ValueError as error:
        cli.error(str(error))
    if args.confirm_public_base and is_preview_base(base):
        cli.error('Un hôte d’aperçu, local ou réservé ne peut pas être confirmé comme base publique.')
    if args.confirm_public_base:
        os.environ['TUG_PUBLIC_BASE_CONFIRMED'] = '1'
    confirmed = os.getenv('TUG_PUBLIC_BASE_CONFIRMED') == '1'
    if not confirmed and not is_preview_base(base):
        cli.error('Base non reconnue comme aperçu : confirmer DNS, TLS et routage GitHub Pages, puis relancer avec --confirm-public-base.')
    artefacts = build(base)
    for name, content in artefacts.items():
        if args.check:
            if read(name) != content:
                raise SystemExit('Artefact à régénérer : ' + name)
        else:
            target = ROOT / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding='utf-8')
    print(f'{sum(name.endswith(".html") for name in artefacts)} routes statiques, recherche et SEO · {base}')


if __name__ == '__main__':
    main()
