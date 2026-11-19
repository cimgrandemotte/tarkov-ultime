"""Rend les dossiers éditoriaux à partir de sources locales et de contenus statiques."""
from html import escape
from pathlib import PurePosixPath
import re
from urllib.parse import urljoin, urlsplit

from site_urls import seo_base_is_public, canonical_link, open_graph_url_meta

DATA = 'data/guides.json'
TEMPLATES = {'starter': 'templates/getting-started.html.in', 'lore': 'templates/lore.html.in'}
TOKEN = re.compile(r'\[\[([A-Z_]+)\]\]')
SOURCE_LABELS = {
    'primaire': 'Source officielle', 'wiki': 'Wiki communautaire', 'communautaire': 'Wiki communautaire',
    'outil_communautaire': 'Outil communautaire', 'communaute': 'Guide de joueur', 'forum': 'Retours de joueurs',
    'entretien': 'Entretien éditorial', 'donnees_communautaires': 'Données communautaires',
    'video': 'Vidéo de référence', 'presse': 'Presse spécialisée',
    'primaire_projet': 'Source primaire du projet', 'registre_paquets': 'Registre de paquets',
}


def subst(text, slots):
    return TOKEN.sub(lambda m: slots[m[1]], text)


def esc(s):
    return escape(str(s), quote=True)


def ref(key, label):
    return f'<a href="#ref-{esc(key)}" aria-label="Source : {esc(label)}">Source</a>'


def render_starter(data):
    steps = []
    for i, row in enumerate(data['steps'], 1):
        stage, title, body = map(esc, row)
        steps.append(f'<li class="raid-step"><span class="raid-step__no" aria-hidden="true">{i:02}</span><span class="raid-step__label">{stage}</span><h3>{title}</h3><p>{body}</p></li>')
    check = []
    for row in data['checklist']:
        key, label, note = map(esc, row)
        check.append(f'<label class="guide-check__row"><input type="checkbox" data-raid-check="{key}"><span><strong>{label}</strong><small>{note}</small></span></label>')
    faq, count = [], 0
    for group in data['faq']:
        key, title = esc(group['id']), esc(group['label'])
        qs = []
        for row in group['items']:
            ident, question, answer, keywords = map(esc, row)
            qs.append(f'  <details class="guide-disclosure" id="faq-{ident}" data-faq-item data-faq-keywords="{keywords}" tabindex="-1"><summary>{question}</summary><p>{answer}</p></details>')
        count += len(qs)
        faq.append(f'<section class="guide-faq__group" aria-labelledby="faq-group-{key}" data-faq-group><h3 id="faq-group-{key}">{title}</h3>\n' + '\n'.join(qs) + '\n</section>')
    return {'STEPS': '\n    '.join(steps), 'CHECKLIST': '\n      '.join(check), 'FAQ': '\n  '.join(faq), 'FAQ_COUNT': str(count)}


def render_lore(data, sources):
    cards = []
    for title, tag, body, key in data['factions']:
        cards.append(f'<article class="lore-faction"><p class="guide-kicker">{esc(tag)}</p><h3>{esc(title)}</h3><p>{esc(body)}</p><p class="guide-cite"><a href="#ref-{esc(key)}" aria-label="{esc(SOURCE_LABELS[sources[key]["type"]])} : {esc(title)}">{esc(SOURCE_LABELS[sources[key]["type"]])}</a></p></article>')
    time = []
    for period, title, body, key in data['timeline']:
        time.append(f'<li><span class="lore-timeline__period">{esc(period)}</span><h3>{esc(title)}</h3><p>{esc(body)} <span class="guide-cite">· {ref(key, title)}</span></p></li>')
    return {'FACTIONS': '\n    '.join(cards), 'TIMELINE': '\n    '.join(time)}


def render_sources(keys, sources):
    rows = []
    for key in keys:
        record = sources[key]
        url = urlsplit(record['url'])
        if url.scheme != 'https' or not url.hostname:
            raise ValueError(f'URL de source non HTTPS : {key}')
        rows.append(f'<li id="ref-{esc(key)}" tabindex="-1"><span class="guide-source__type">{esc(SOURCE_LABELS[record["type"]])}</span>'
                    f'<a href="{esc(record["url"])}">{esc(record["titre"])} <span aria-hidden="true">↗</span></a><p>{esc(record["usage"])}</p></li>')
    return '\n            '.join(rows)


def build_guides(data, sources, base, patch, review, date_long, read, compact):
    shell = read('templates/guide.html.in')
    output = {}
    for page in data['pages']:
        kind = page['kind']
        neighbor = next(p for p in data['pages'] if p['kind'] != kind)
        root = '../' * (len(PurePosixPath(page['file']).parts) - 1)
        canonical = urljoin(base, page['route']) if seo_base_is_public(base) else None
        img = urljoin(base, page['image'])
        primary, secondary = page['primary'], page['secondary']
        labels = {
            'ROOT': root, 'DESCRIPTION': page['description'], 'SEO_TITLE': page['title'], 'CANONICAL': canonical or '',
            'IMAGE': page['image'], 'OG_IMAGE': img, 'IMAGE_ALT': page['imageAlt'], 'IMAGE_CAPTION': page['imageCaption'],
            'DATE_SHORT': review.strftime('%d.%m.%Y'), 'DATE_LONG': date_long, 'VERIFIED_DAY': review.date().isoformat(), 'VERIFIED_AT': review.isoformat(),
            'KIND': kind, 'LABEL': page['label'], 'CODE': page['code'], 'HEADING': page['heading'], 'LEAD': page['lead'], 'PATCH': patch,
            'PRIMARY_ANCHOR': primary[0], 'PRIMARY_LABEL': primary[1], 'SECONDARY_ANCHOR': secondary[0], 'SECONDARY_LABEL': secondary[1],
            'HERO_NOTE': page['note'], 'SOURCE_NOTE': page['sourceNote'], 'SOURCE_CODE': f'{len(page["toc"]):02}',
            'GUIDE_NEIGHBOR_URL': root + neighbor['route'], 'GUIDE_NEIGHBOR_SHORT': neighbor['short'], 'GUIDE_NEIGHBOR_LABEL': neighbor['label'], 'GUIDE_NEIGHBOR_BLURB': neighbor['neighborBlurb'],
        }
        article = {'@type': 'Article', 'headline': page['heading'], 'description': page['description'],
                   'inLanguage': 'fr-FR', 'datePublished': review.date().isoformat(), 'dateModified': review.isoformat(),
                   'image': {'@type': 'ImageObject', 'url': img, 'width': 1376, 'height': 768},
                   'author': {'@type': 'Organization', 'name': 'Tarkov Ultimate Guide'}}
        schema = {'@context': 'https://schema.org', '@graph': [article]}
        if canonical:
            article.update({'@id': canonical + '#article', 'mainEntityOfPage': canonical})
            article['author']['url'] = base
            schema['@graph'].append({'@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Accueil', 'item': base},
                {'@type': 'ListItem', 'position': 2, 'name': page['label'], 'item': canonical},
            ]})
        quick = []
        for row in page['quick']:
            dest, no, eyebrow, label = map(esc, row)
            quick.append(f'<a class="guide-quick__link" href="#{dest}"><span class="guide-quick__no" aria-hidden="true">{no}</span><span class="guide-quick__copy"><small>{eyebrow}</small><strong>{label}</strong></span><span class="guide-quick__arrow" aria-hidden="true">↓</span></a>')
        toc = [f'<li><a href="#{esc(dest)}"><span aria-hidden="true">{i:02}</span>{esc(label)}</a></li>' for i, (dest, label) in enumerate(page['toc'], 1)]
        content_slots = render_starter(data) if kind == 'starter' else render_lore(data, sources)
        content = subst(read(TEMPLATES[kind]), {**content_slots, 'ROOT': esc(root)})
        slots = {**{k: esc(v) for k,v in labels.items()},
                 'HERO_IMAGE': (f'<img class="guide-hero__image" src="{esc(root+page["image"])}" width="1376" height="768" '
                                f'alt="{esc(page["imageAlt"])}" fetchpriority="high" decoding="async">'),
                 'IMAGE_PRELOAD': f'<link rel="preload" href="{esc(root+page["image"])}" as="image" fetchpriority="high">',
                 'CANONICAL_LINK': canonical_link(base, page['route']), 'OG_URL_META': open_graph_url_meta(base, page['route']),
                 'JSON_LD': compact(schema), 'CONTENT': content,
                 'CURRENT_STARTER': ' aria-current="page"' if kind == 'starter' else '', 'CURRENT_LORE': ' aria-current="page"' if kind == 'lore' else '',
                 'QUICK': '\n        '.join(quick), 'TOC': '\n            '.join(toc), 'SOURCE_LIST': render_sources(page['sources'], sources)}
        output[page['file']] = subst(shell, slots)
    return output
