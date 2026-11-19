"""Génère l’index et les fiches de cartes avec modes, preuves et limites datées."""
from datetime import date, datetime
from html import escape
import json
from pathlib import PurePosixPath
from urllib.parse import urljoin, urlsplit

from guide_pages import esc, render_sources, subst
from site_urls import seo_base_is_public, canonical_link, open_graph_url_meta

DATA = 'data/maps.json'
SNAPSHOT = 'data/snapshots/cartes-2026-11-18.json'
HUB_TEMPLATE = 'templates/maps-hub.html.in'
MAP_TEMPLATE = 'templates/map-content.html.in'
SHELL_TEMPLATE = 'templates/guide.html.in'
MODE_NAMES = {'regular': 'PvP permanent', 'pve': 'PvE Zone', 'pvp-season': 'PvP Seasonal'}
ACCESS_LABELS = {
    'catalogue': 'Catalogue, accès non testé', 'communaute': 'Condition communautaire',
    'officiel': 'Note BSG', 'conflit': 'Sources en conflit', 'paliers': 'Palier à confirmer',
    'progression': 'Progression à vérifier', 'carte': 'Carte d’accès rapportée', 'transit': 'Transit conditionnel',
}


def read_json(path, read):
    return json.loads(read(path))


def index_by_slug(snapshot, mode):
    return {row['slug']: row for row in snapshot['modes'][mode]['mapRecords']}


def _players_label(record, page):
    if page['slug'] == 'the-labyrinth':
        return f"À revalider · API {record['players'].replace('-', '–')} / wiki 1–5"
    return record['players'].replace('-', '–')


def _duration_label(record, page):
    if page['slug'] == 'terminal':
        return f"{record['raidDuration']} min API · 45 min wiki (écart)"
    return f"{record['raidDuration']} min"


def map_stats(page, snapshot):
    rows = {}
    for mode in MODE_NAMES:
        source = index_by_slug(snapshot, mode)
        record = source.get(page['slug'])
        if record is None:
            raise ValueError(f"Carte absente de l’export {mode}: {page['slug']}")
        rows[mode] = {
            'players': record['players'],
            'playersLabel': _players_label(record, page),
            'duration': record['raidDuration'],
            'durationLabel': _duration_label(record, page),
            'extractEntries': record['extractEntries'],
        }
    return rows


def _stat_json(stats):
    return escape(json.dumps(stats, ensure_ascii=False, separators=(',', ':')), quote=True)


def render_cards(pages, snapshot, difficulty):
    cards = []
    for page in pages:
        stats = map_stats(page, snapshot)
        default = stats['regular']
        search_terms = ' '.join([
            page['name'], page['heading'], page['lead'], page['terrain'],
            *page['landmarks'], *page['risks'], page['accessText'], page['exitText'],
        ])
        interactive_url = page.get('interactiveMapUrl', '')
        parsed = urlsplit(interactive_url)
        if parsed.scheme != 'https' or parsed.hostname != 'tarkov.dev' or not parsed.path.startswith('/map/'):
            raise ValueError(f'Lien interactif Tarkov.dev invalide pour {page["slug"]}: {interactive_url!r}')
        local_route = esc(PurePosixPath(page['route']).name)
        interactive_label = esc(f'Ouvrir la carte interactive de {page["name"]} sur Tarkov.dev dans un nouvel onglet')
        cards.append(
            f'<article class="map-card" data-map-card data-map-slug="{esc(page["slug"])}" '
            f'data-map-difficulty="{esc(page["difficulty"])}" data-map-access="{esc(page["accessType"])}" '
            f'data-map-search="{esc(search_terms.lower())}" data-map-stats="{_stat_json(stats)}">'
            f'<div class="map-card__visual map-card__visual--{esc(page["slug"])}" aria-hidden="true">'
            f'<span class="map-card__visual-code">MAP / {esc(page["code"])}</span>'
            f'<span class="map-card__visual-terrain">{esc(page["terrain"])}</span>'
            f'<span class="map-card__visual-note">SCHÉMA ÉDITORIAL · PAS UN PLAN</span><i></i></div>'
            f'<div class="map-card__body"><div class="map-card__top"><span class="map-proof map-proof--{esc(page["accessType"])}">{esc(ACCESS_LABELS[page["accessType"]])}</span>'
            f'<label class="map-compare-check" hidden><input type="checkbox" value="{esc(page["slug"])}" data-map-compare aria-label="Comparer {esc(page["name"])}"><span>Comparer</span></label></div>'
            f'<h3><a href="{local_route}">{esc(page["name"])}</a></h3>'
            f'<p class="map-card__summary">{esc(page["lead"])}</p>'
            f'<dl class="map-card__facts"><div><dt>Joueurs · export</dt><dd data-map-stat="players">{esc(default["playersLabel"])}</dd></div>'
            f'<div><dt>Durée · export</dt><dd data-map-stat="duration">{esc(default["durationLabel"])}</dd></div></dl>'
            f'<div class="map-card__foot"><span class="map-difficulty" data-map-difficulty-label>{esc(difficulty[page["difficulty"]])}</span>'
            f'<div class="map-card__actions"><a href="{local_route}" class="map-card__open">Fiche locale <span aria-hidden="true">↗</span></a>'
            f'<a href="{esc(interactive_url)}" class="map-card__interactive" target="_blank" rel="noopener noreferrer" aria-label="{interactive_label}">Carte interactive <span aria-hidden="true">↗</span></a></div>'
            f'</div></div></article>'
        )
    return '\n'.join(cards)


def _mode_options(modes):
    return '\n'.join(f'<option value="{esc(row["id"])}">{esc(row["label"])}</option>' for row in modes)


def _difficulty_options(options):
    return '\n'.join(f'<option value="{esc(row["id"])}">{esc(row["label"])}</option>' for row in options)


def _transit_rows(transits, sources):
    rows = []
    for row in transits:
        source = sources[row['sourceKey']]
        evidence_class = 'official' if row['evidence'].startswith('BSG') else 'community'
        rows.append(
            f'<li class="maps-network-row maps-network-row--{evidence_class}">'
            f'<span class="maps-network-row__origin">{esc(row["origin"])}</span>'
            f'<span class="maps-network-row__arrow" aria-hidden="true">→</span>'
            f'<span class="maps-network-row__destination">{esc(row["destination"])}</span>'
            f'<span class="maps-network-row__evidence">{esc(row["evidence"])}</span>'
            f'<p>{esc(row["note"])} <a href="#ref-{esc(row["sourceKey"])}" aria-label="Source : {esc(source["titre"])}">Source</a></p></li>'
        )
    return '\n'.join(rows)


def _access_legend(rows):
    return '\n'.join(
        f'<article class="maps-access-legend__item"><span class="map-proof map-proof--{esc(row["id"])}">{esc(row["label"])}</span><p>{esc(row["description"])}</p></article>'
        for row in rows
    )


def _snapshot_record(variant, snapshot, mode):
    return index_by_slug(snapshot, mode).get(variant['slug'])


def _variant_summary(variant, snapshot):
    stats = {mode: _snapshot_record(variant, snapshot, mode) for mode in MODE_NAMES}
    present = {mode: row for mode, row in stats.items() if row}
    if not present:
        return 'Absente des exports consultés'
    players = {row['players'] for row in present.values()}
    player_label = next(iter(players)).replace('-', '–') if len(players) == 1 else 'Écart entre modes'
    durations = {}
    for mode, row in present.items():
        durations.setdefault(row['raidDuration'], []).append(MODE_NAMES[mode])
    duration_label = ' · '.join(
        f"{duration} min ({', '.join(labels)})" for duration, labels in durations.items()
    )
    return f'{player_label} · {duration_label}'


def _variant_rows(variants, snapshot, pages_by_slug):
    result = []
    for variant in variants:
        parent = pages_by_slug[variant['parent']]['name']
        result.append(
            f'<tr><th scope="row">{esc(variant["name"])}</th><td>{esc(parent)}</td>'
            f'<td>{esc(_variant_summary(variant, snapshot))}</td><td>{esc(variant["note"])}</td></tr>'
        )
    return '\n'.join(result)


def _source_ref(source_key, sources):
    return f'<a href="#ref-{esc(source_key)}" aria-label="Voir la référence : {esc(sources[source_key]["titre"])}">référence</a>'


def _landmarks(rows):
    return '\n'.join(f'<li><span aria-hidden="true">{i:02}</span><strong>{esc(name)}</strong></li>' for i, name in enumerate(rows, 1))


def _risks(rows):
    return '\n'.join(f'<li>{esc(value)}</li>' for value in rows)


def _boss_section(page, sources):
    key = page['bossSourceKey']
    citation = _source_ref(key, sources)
    if page['bosses']:
        entries = ''.join(f'<li><span aria-hidden="true">◆</span>{esc(name)}</li>' for name in page['bosses'])
        regular = f'<ul class="map-boss-list">{entries}</ul>'
    else:
        regular = ('<p class="map-boss-empty">Aucun boss de carte régulière n’est listé dans la page communautaire consultée. '
                   'Cela ne confirme pas l’absence de rencontres dans un événement, un mode ou un raid particulier.</p>')
    if page['eventBosses']:
        event_items = ''.join(f'<li>{esc(name)}</li>' for name in page['eventBosses'])
        event = f'<div class="map-boss-events"><h3>Mentions événementielles à part</h3><ul>{event_items}</ul><p>Entrées de la table événementielle communautaire ; elles ne prouvent pas que l’événement est actif.</p></div>'
    else:
        event = '<p class="map-boss-events map-boss-events--empty">Aucune mention événementielle ajoutée pour cette fiche dans ce relevé.</p>'
    return (
        '<section class="guide-section map-section" id="bosses" tabindex="-1" aria-labelledby="map-boss-title">'
        '<div class="guide-section__heading"><p class="guide-kicker"><span>04</span> Rencontres rapportées</p>'
        '<h2 id="map-boss-title">Bosses : noms communautaires, pas une promesse de spawn</h2>'
        '<p>Cette liste de lieux est reprise de la page communautaire EFT Wiki, consultée le 18/11/2026. '
        'Elle ne confirme ni le mode, ni la variante, ni la présence dans votre raid. ' + citation + '</p></div>'
        '<div class="map-boss-layout"><article class="map-boss-card"><p class="eyebrow">Boss réguliers rapportés</p>' + regular + '</article>'
        + event + '</div><p class="map-smallprint">Aucun taux de présence n’est publié ici. Les champs Tarkov.dev <code>bossEntries</code> et <code>mobRecordsCount</code> ne sont pas des nombres de boss uniques ; ils ne servent pas à produire cette liste.</p></section>'
    )


def _exit_cards(rows, source_key, sources):
    if not rows:
        return ('<div class="map-exit-examples map-exit-examples--empty"><p><strong>Aucun nom statique publié ici.</strong> '
                'Le relevé n’a pas validé une liste qui resterait fiable par faction, profil et mode. Utilisez les points de contrôle ci-dessous '
                'et la liste d’extractions de votre raid.</p></div>')
    citation = _source_ref(source_key, sources)
    return (
        '<ul class="map-exit-examples">' + ''.join(
            f'<li><strong>{esc(row["name"])}</strong><p>{esc(row["detail"])}</p></li>' for row in rows
        ) + '</ul>'
        + '<p class="map-exit-source">Exemples rapportés par la table communautaire consultée le 18/11/2026 · '
        + citation + '. Leur présence et leur condition doivent être vérifiées dans le raid.</p>'
    )


def _map_transits(page, transits, sources):
    relevant = [row for row in transits if row['origin'] == page['name'] or row['destination'] == page['name']]
    if not relevant:
        return '<p class="map-no-transit">Aucun transit spécifique n’a été corroboré pour cette fiche dans le relevé du 18/11. Cela ne prouve pas qu’il n’en existe pas.</p>'
    rows = []
    for row in relevant:
        rows.append(
            f'<li><div class="map-transit-route"><strong>{esc(row["origin"])}</strong><span aria-hidden="true">→</span><strong>{esc(row["destination"])}</strong></div>'
            f'<span class="map-proof map-proof--{("official" if row["evidence"].startswith("BSG") else "community")}">{esc(row["evidence"])}</span>'
            f'<p>{esc(row["note"])} {_source_ref(row["sourceKey"], sources)}</p></li>'
        )
    return '<ul class="map-transit-list">' + '\n'.join(rows) + '</ul>'


def _interactive_map_anchor(url, visible, accessible, class_name='map-interactive-link'):
    parsed = urlsplit(url or '')
    if parsed.scheme != 'https' or parsed.hostname != 'tarkov.dev' or not parsed.path.startswith('/map/') or parsed.query or parsed.fragment:
        raise ValueError(f'Lien interactif externe invalide : {url!r}')
    return (f'<a class="{esc(class_name)}" href="{esc(url)}" target="_blank" rel="noopener noreferrer" '
            f'aria-label="{esc(accessible)}">{esc(visible)} <span aria-hidden="true">↗</span></a>')


def _interactive_tools(page, variants):
    page_link = _interactive_map_anchor(
        page.get('interactiveMapUrl'), 'Ouvrir la carte interactive',
        f'Ouvrir la carte interactive {page["name"]} sur Tarkov.dev dans un nouvel onglet',
    )
    variant_links = []
    for variant in variants:
        url = variant.get('interactiveMapUrl')
        if url:
            variant_links.append(_interactive_map_anchor(
                url, variant['name'], f'Ouvrir la carte interactive {variant["name"]} sur Tarkov.dev dans un nouvel onglet',
                'map-interactive-link map-interactive-link--variant',
            ))
    variants_html = (
        '<p class="map-interactive-variants"><strong>Variantes cartographiées :</strong> '
        + ' · '.join(variant_links) + '</p>' if variant_links else ''
    )
    return (
        '<aside class="map-interactive-tools" aria-label="Outils de cartographie externes">'
        '<div><p class="map-interactive-tools__eyebrow">Outil communautaire · Tarkov.dev</p>'
        '<p>Ouvre une carte avec zoom et couches de repères. Son contenu et ses extractions ne sont pas validés dans le client EFT; comparez-les à l’interface de votre raid.</p></div>'
        '<div class="map-interactive-tools__actions">' + page_link
        + '<a class="map-interactive-index" href="https://tarkov.dev/maps/" target="_blank" rel="noopener noreferrer">Index et variantes <span aria-hidden="true">↗</span></a>'
        + '</div>' + variants_html + '</aside>'
    )


def _mode_detail(page, stats, modes):
    buttons, panels, table_rows = [], [], []
    for index, mode in enumerate(modes):
        row = stats[mode['id']]
        panel_id = f'map-mode-panel-{mode["id"]}'
        buttons.append(
            f'<button type="button" class="button tabs__tab" data-map-mode="{esc(mode["id"])}" '
            f'aria-pressed="{str(index == 0).lower()}" aria-controls="{panel_id}">{esc(mode["shortLabel"])}</button>'
        )
        panels.append(
            f'<article class="map-mode-panel" id="{panel_id}" data-map-mode-panel="{esc(mode["id"])}">'
            f'<p class="eyebrow">{esc(mode["label"])}</p><dl>'
            f'<div><dt>Joueurs · API</dt><dd>{esc(row["playersLabel"])}</dd></div>'
            f'<div><dt>Durée · API</dt><dd>{esc(row["durationLabel"])}</dd></div>'
            f'<div><dt>Entrées d’extraction · API</dt><dd>{row["extractEntries"]}</dd></div>'
            f'</dl><p>Entrée de catalogue uniquement ; état et conditions du raid non fournis.</p></article>'
        )
        table_rows.append(
            f'<tr><th scope="row">{esc(mode["label"])}</th><td>{esc(row["playersLabel"])}</td>'
            f'<td>{esc(row["durationLabel"])}</td><td>{row["extractEntries"]}</td></tr>'
        )
    return '\n'.join(buttons), '\n'.join(panels), '\n'.join(table_rows)


def _map_content(page, stats, modes, variants, sources, transits, snapshot_date, read):
    partial = read(MAP_TEMPLATE)
    buttons, panels, rows = _mode_detail(page, stats, modes)
    access_source_keys = page.get('accessSourceKeys') or [
        key for key in page['sources']
        if key.startswith('wiki-') and key != 'wiki-bosses'
        or key in ('patch105', 'patch115', 'patch120', 'terminal-80level')
    ]
    access_citation = ' · '.join(_source_ref(key, sources) for key in access_source_keys)
    page_variants = [row for row in variants if row['parent'] == page['slug']]
    slots = {
        'SNAPSHOT_DATE': esc(snapshot_date),
        'INTERACTIVE_TOOLS': _interactive_tools(page, page_variants),
        'MODE_BUTTONS': buttons,
        'MODE_PANELS': panels,
        'MODE_ROWS': rows,
        'VARIANT_SECTION': _variant_section_from_snapshot(page_variants, page),
        'ACCESS_TITLE': esc(page['accessTitle']),
        'ACCESS_TEXT': esc(page['accessText']),
        'ACCESS_CITATION': access_citation,
        'LANDMARKS': _landmarks(page['landmarks']),
        'RISKS': _risks(page['risks']),
        'BOSSES': _boss_section(page, sources),
        'EXIT_TITLE': esc(page['exitTitle']),
        'EXIT_TEXT': esc(page['exitText']),
        'EXIT_CARDS': _exit_cards(page['exitExamples'], page.get('exitSourceKey'), sources),
        'ROUTE_ADVICE': esc(page['routeAdvice']),
        'ROUTE_ADVICE_CITATION': (
            '<p class="map-route-cites">Sources de contexte · '
            + ' · '.join(_source_ref(key, sources) for key in page.get('routeAdviceSourceKeys', []))
            + '. Les conseils de joueurs n’ont pas été testés dans le client.</p>'
            if page.get('routeAdviceSourceKeys') else ''
        ),
        'TRANSITS': _map_transits(page, transits, sources),
    }
    return subst(partial, slots)


def _variant_section_from_snapshot(variants, page):
    if not variants:
        return ''
    # The full snapshot is attached to the page during build; this helper is replaced by its pre-rendered rows.
    rows = page.get('_variantRows', [])
    return (
        '<div class="map-table-wrap map-variant-table" role="region" aria-label="Tableau des variantes de ce lieu" tabindex="0"><table class="map-data-table">'
        '<caption>Variantes distinctes du lieu dans le snapshot</caption>'
        '<thead><tr><th scope="col">Variante</th><th scope="col">Joueurs / durée</th><th scope="col">Périmètre</th></tr></thead><tbody>'
        + ''.join(
            f'<tr><th scope="row">{esc(row["name"])}</th><td>{esc(row["statsLabel"])}</td><td>{esc(row["note"])}</td></tr>'
            for row in rows
        )
        + '</tbody></table></div>'
    )


def _hub_cards(pages, snapshot, overview, data, sources, base):
    difficulty = {row['id']: row['label'] for row in data['difficultyLegend']['options']}
    cards = render_cards(pages, snapshot, difficulty)
    transits = _transit_rows(data['transits'], sources)
    legend = _access_legend(data['accessLegend'])
    variants = []
    pages_by_slug = {row['slug']: row for row in pages}
    for row in data['variants']:
        variants.append({**row, 'statsLabel': _variant_summary(row, snapshot), 'parentName': pages_by_slug[row['parent']]['name']})
    variant_rows = ''.join(
        f'<tr><th scope="row">{esc(row["name"])}</th><td>{esc(row["parentName"])}</td>'
        f'<td>{esc(row["statsLabel"])}</td><td>{esc(row["note"])}</td></tr>' for row in variants
    )
    return cards, transits, legend, variant_rows


def _map_search_records(pages):
    return [
        {'title': page['name'], 'href': page['route'], 'tag': 'Carte',
         'summary': page['lead'], 'keywords': [page['terrain'], *page['landmarks'], *page['risks']]}
        for page in pages
    ]


def build_maps(data, snapshot, sources, base, date_long, patch, read, compact):
    pages = data['maps']
    modes = data['modes']
    map_review = datetime.fromisoformat(data['verifiedAt'])
    snapshot_date = datetime.fromisoformat(snapshot['collectedAt']).strftime('%d/%m/%Y')
    hub = data['overview']
    public_seo_base = seo_base_is_public(base)
    hub_canonical = urljoin(base, 'pages/maps/') if public_seo_base else None
    hub_image = urljoin(base, hub['image'])
    graph = {
        '@context': 'https://schema.org', '@type': 'CollectionPage',
        'name': hub['title'], 'description': hub['description'],
        'inLanguage': 'fr-FR', 'dateModified': map_review.isoformat(),
        'image': {'@type': 'ImageObject', 'url': hub_image, 'width': 1376, 'height': 768},
    }
    if hub_canonical:
        graph.update({'@id': hub_canonical, 'url': hub_canonical,
                      'hasPart': [{'@type': 'Article', 'name': row['name'], 'url': urljoin(base, row['route'])} for row in pages]})
    cards, transit_rows, legend, variant_rows = _hub_cards(pages, snapshot, hub, data, sources, base)
    root = '../../'
    hub_slots = {
        'ROOT': root,
        'DESCRIPTION': esc(hub['description']), 'SEO_TITLE': esc('Cartes de Tarkov : comparateur, accès et extractions | Tarkov Ultimate Guide'),
        'CANONICAL_LINK': canonical_link(base, 'pages/maps/'), 'OG_URL_META': open_graph_url_meta(base, 'pages/maps/'),
        'OG_IMAGE': esc(hub_image), 'IMAGE': esc(hub['image']), 'IMAGE_ALT': esc(hub['imageAlt']),
        'HEADING': esc(hub['heading']), 'LEAD': esc(hub['lead']), 'IMAGE_CAPTION': esc(hub['imageCaption']),
        'PATCH': esc(patch), 'VERIFIED_DAY': map_review.date().isoformat(), 'DATE_SHORT': map_review.strftime('%d.%m.%Y'), 'DATE_LONG': esc(date_long),
        'JSON_LD': compact(graph), 'DIFFICULTY_OPTIONS': _difficulty_options(data['difficultyLegend']['options']),
        'MODE_OPTIONS': _mode_options(modes), 'MAP_CARDS': cards, 'TRANSIT_ROWS': transit_rows,
        'VARIANT_ROWS': variant_rows, 'ACCESS_LEGEND': legend,
        'SOURCE_LIST': render_sources(list(dict.fromkeys([*hub['sourceKeys'], *(row['sourceKey'] for row in data['transits'])])), sources),
    }
    hub_html = subst(read(HUB_TEMPLATE), hub_slots)
    output = {'pages/maps/index.html': hub_html}
    shell = read(SHELL_TEMPLATE)
    partial = read(MAP_TEMPLATE)
    for index, page in enumerate(pages):
        stats = map_stats(page, snapshot)
        canonical = urljoin(base, page['route']) if public_seo_base else None
        img = urljoin(base, page['image'])
        page_variants = [row for row in data['variants'] if row['parent'] == page['slug']]
        # Attach only precomputed variant display labels; avoid using mode-specific values as a live claim.
        page['_variantRows'] = [
            {**row, 'statsLabel': _variant_summary(row, snapshot)} for row in page_variants
        ]
        content = _map_content(page, stats, modes, page_variants, sources, data['transits'], snapshot_date, read)
        next_page = pages[index + 1] if index + 1 < len(pages) else None
        neighbor_url = (root + next_page['route']) if next_page else (root + 'pages/maps/')
        neighbor_label = next_page['name'] if next_page else hub['title']
        toc = [
            ('mode', 'Joueurs, durée et variantes'), ('acces', 'Accès et modes'), ('reperes', 'Lecture du terrain'),
            ('bosses', 'Bosses rapportés'), ('extractions', 'Sorties et conditions'), ('parcours', 'Itinéraire de préparation'),
            ('transits', 'Transits'), ('sources', 'Sources'),
        ]
        quick = [('acces', '01', 'Accès', 'Vérifier le profil'), ('extractions', '02', 'Sorties', 'Lire les conditions'), ('transits', '03', 'Transits', 'Changer de lieu')]
        article = {'@type': 'Article', 'headline': page['heading'], 'description': page['description'],
                   'inLanguage': 'fr-FR', 'datePublished': map_review.date().isoformat(), 'dateModified': map_review.isoformat(),
                   'image': {'@type': 'ImageObject', 'url': img, 'width': 1376, 'height': 768},
                   'author': {'@type': 'Organization', 'name': 'Tarkov Ultimate Guide'},
                   'isPartOf': {'@type': 'CollectionPage', 'name': hub['title']}}
        schema = {'@context': 'https://schema.org', '@graph': [article]}
        if canonical:
            article.update({'@id': canonical + '#article', 'mainEntityOfPage': canonical})
            article['author']['url'] = base
            article['isPartOf']['url'] = hub_canonical
            schema['@graph'].append({'@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Accueil', 'item': base},
                {'@type': 'ListItem', 'position': 2, 'name': hub['title'], 'item': hub_canonical},
                {'@type': 'ListItem', 'position': 3, 'name': page['name'], 'item': canonical},
            ]})
        slots = {
            'ROOT': root, 'DESCRIPTION': esc(page['description']), 'SEO_TITLE': esc(f"{page['name']} — accès, sorties et repères | Tarkov Ultimate Guide"),
            'CANONICAL_LINK': canonical_link(base, page['route']), 'OG_URL_META': open_graph_url_meta(base, page['route']),
            'OG_IMAGE': esc(img), 'IMAGE': esc(page['image']), 'IMAGE_ALT': esc(page['imageAlt']),
            'HERO_IMAGE': (f'<img class="guide-hero__image" src="{esc(root+page["image"])}" width="1376" height="768" '
                           f'alt="{esc(page["imageAlt"])}" fetchpriority="high" decoding="async">'),
            'IMAGE_PRELOAD': f'<link rel="preload" href="{esc(root+page["image"])}" as="image" fetchpriority="high">',
            'IMAGE_CAPTION': esc(page['imageCaption']),
            'DATE_SHORT': map_review.strftime('%d.%m.%Y'), 'DATE_LONG': esc(date_long),
            'VERIFIED_DAY': map_review.date().isoformat(), 'VERIFIED_AT': map_review.isoformat(), 'KIND': 'map', 'LABEL': esc(page['name']),
            'CODE': esc(page['code']), 'HEADING': esc(page['heading']), 'LEAD': esc(page['lead']), 'PATCH': esc(patch),
            'PRIMARY_ANCHOR': 'acces', 'PRIMARY_LABEL': 'Accès et modes', 'SECONDARY_ANCHOR': 'extractions', 'SECONDARY_LABEL': 'Lire les sorties',
            'HERO_NOTE': 'Données du ' + snapshot_date + ' · disponibilités en raid non testées',
            'SOURCE_NOTE': 'Tarkov.dev et pages communautaires ; état client non testé. Voir la provenance de chaque fait ci-dessous.',
            'SOURCE_CODE': f'{len(toc):02}', 'GUIDE_NEIGHBOR_URL': esc(neighbor_url), 'GUIDE_NEIGHBOR_SHORT': esc(neighbor_label),
            'GUIDE_NEIGHBOR_LABEL': esc(neighbor_label), 'GUIDE_NEIGHBOR_BLURB': 'Ouvrir la fiche suivante, ou revenir à l’index des 13 lieux.',
            'JSON_LD': compact(schema), 'CONTENT': content,
            'CURRENT_STARTER': '', 'CURRENT_LORE': '',
            'QUICK': '\n'.join(
                f'<a class="guide-quick__link" href="#{dest}"><span class="guide-quick__no" aria-hidden="true">{no}</span><span class="guide-quick__copy"><small>{esc(kicker)}</small><strong>{esc(label)}</strong></span><span class="guide-quick__arrow" aria-hidden="true">↓</span></a>'
                for dest, no, kicker, label in quick
            ),
            'TOC': '\n'.join(f'<li><a href="#{dest}"><span aria-hidden="true">{i:02}</span>{esc(label)}</a></li>' for i, (dest, label) in enumerate(toc, 1)),
            'SOURCE_LIST': render_sources(page['sources'], sources),
        }
        output[page['route']] = subst(shell, slots)
    return output, _map_search_records(pages)
