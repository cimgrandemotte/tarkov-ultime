#!/usr/bin/env python3
"""Aperçu éditorial : liste blanche explicite, aucun atelier ni fichier de pilotage servi."""
from argparse import ArgumentParser
from gzip import compress
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from urllib.parse import urlsplit

from serve_lab import Lab, ROOT
from build_home import PREVIEW_PORT

PUBLIC_FILES = frozenset('''
index.html pages/getting-started.html pages/lore/index.html
pages/maps/index.html pages/maps/ground-zero.html pages/maps/customs.html pages/maps/factory.html pages/maps/woods.html pages/maps/shoreline.html pages/maps/interchange.html pages/maps/reserve.html pages/maps/the-lab.html pages/maps/lighthouse.html pages/maps/streets-of-tarkov.html pages/maps/the-labyrinth.html pages/maps/icebreaker.html pages/maps/terminal.html
pages/weapons/index.html pages/weapons/assault-rifles.html pages/weapons/smgs.html pages/weapons/shotguns.html pages/weapons/sniper-rifles.html pages/weapons/dmrs.html pages/weapons/lmgs.html pages/weapons/pistols.html pages/weapons/melee.html pages/weapons/grenade-launchers.html pages/weapons/weapon-mods.html pages/ammo/index.html pages/ammo/ammo-chart.html
pages/armor/index.html pages/armor/body-armor.html pages/armor/helmets.html pages/armor/rigs.html pages/armor/armor-chart.html
pages/bosses/index.html pages/bosses/reshala.html pages/bosses/killa.html pages/bosses/shturman.html pages/bosses/glukhar.html pages/bosses/sanitar.html pages/bosses/tagilla.html pages/bosses/kaban.html pages/bosses/kollontay.html pages/bosses/zryachiy.html pages/bosses/partisan.html pages/bosses/cultist-priest.html pages/bosses/the-goons.html pages/bosses/shadow-of-tagilla.html pages/bosses/the-wedge.html pages/bosses/vengeful-killa.html
pages/traders/index.html pages/traders/prapor.html pages/traders/therapist.html pages/traders/skier.html pages/traders/peacekeeper.html pages/traders/mechanic.html pages/traders/ragman.html pages/traders/jaeger.html pages/traders/fence.html pages/traders/lightkeeper.html pages/traders/ref.html
pages/quests/index.html pages/quests/quest-tree.html pages/quests/kappa-guide.html
pages/hideout/index.html pages/hideout/crafting.html
pages/skills/index.html
pages/economy/index.html pages/economy/flea-market.html pages/economy/money-making.html
pages/strategy/index.html pages/strategy/beginner-tips.html pages/strategy/advanced-tactics.html pages/strategy/pvp-guide.html pages/strategy/pve-guide.html pages/strategy/meta-builds.html
pages/spt-tushonka/index.html pages/spt-tushonka/installation.html pages/spt-tushonka/mods.html pages/spt-tushonka/fika.html pages/spt-tushonka/troubleshooting.html
pages/arena/index.html pages/events/index.html
pages/patch-notes.html pages/resources/index.html pages/resources/glossary.html
robots.txt sitemap.xml data/snapshots/phase-6-armor-2026-11-18.json data/snapshots/phase-7-regular-2026-11-18.json data/snapshots/phase-7-pve-2026-11-18.json data/snapshots/phase-7-pvp-season-2026-11-18.json
fonts/type.css fonts/orbitron-500-900.woff2 fonts/inter-400-700.woff2 fonts/rajdhani-600.woff2 fonts/rajdhani-700.woff2 fonts/sharetechmono-400.woff2
css/main.css css/components.css css/responsive.css css/animations.css css/pages/home.css css/pages/guides.css css/pages/maps.css css/pages/weapons.css css/pages/phase6.css css/pages/phase7.css css/pages/phase8.css css/pages/phase9.css css/pages/phase10.css
js/main.js js/utils.js js/animations.js js/audio.js js/search.js js/home.js js/guides.js js/maps.js js/weapons.js js/phase6.js js/phase7.js js/phase8.js js/phase9.js js/phase10.js js/components/checklist.js js/components/modal.js js/components/navigation.js js/components/tabs.js js/data/search-index.json js/data/phase7.json
vendor/howler.core.min.js vendor/fuse.basic.min.mjs
images/hero/norvinsk-rain.jpg images/maps/norvinsk-overlook.jpg images/maps/customs.jpg images/maps/factory.jpg images/maps/ground-zero-district.jpg images/maps/woods.jpg images/maps/shoreline.jpg images/maps/interchange.jpg images/maps/reserve.jpg images/maps/the-lab.jpg images/maps/lighthouse.jpg images/maps/streets-of-tarkov-district.jpg images/maps/the-labyrinth.jpg images/maps/icebreaker.jpg images/maps/terminal-port.jpg images/weapons/arsenal-workbench.jpg images/bosses/killa-ambience.jpg images/lore/premier-raid.jpg images/spt/tushonka-hideout.jpg
images/beginners/first-deployment.jpg images/beginners/ground-zero-interface.jpg images/beginners/raid-medical-inventory.jpg images/lore/norvinsk-bay.jpg images/lore/norvinsk-archive.jpg
images/ammo/ammo-catalogue-tray.jpg images/ammo/ammo-chart-detail.jpg images/ammo/ammo-chart-detail-640.jpg images/weapons/weapon-family-rack-640.jpg images/weapons/weapon-family-rack.jpg images/weapons/assault-rifles-detail.jpg images/weapons/dmr-field-rifle.jpg images/weapons/grenade-launcher-detail.jpg images/weapons/lmg-detail.jpg images/weapons/melee-detail.jpg images/weapons/pistols-detail.jpg images/weapons/precision-detail.jpg images/weapons/shotguns-detail.jpg images/weapons/smg-detail.jpg images/weapons/weapon-mods-inspection.jpg images/weapons/weapon-mods-inspection-640.jpg
images/armor/armor-hub.jpg images/armor/armor-body-plates.jpg images/armor/armor-helmet-visor.jpg images/armor/armor-materials.jpg images/armor/armor-rig-storage.jpg images/bosses/boss-goons.jpg images/bosses/boss-icebreaker.jpg images/bosses/boss-labyrinth.jpg images/bosses/boss-operator.jpg images/bosses/bosses-hub.jpg
images/phase7/traders-market.jpg images/phase7/quest-dossier.jpg images/phase7/hideout-crafting.jpg images/phase7/trader-ledger.jpg images/phase7/quest-board.jpg images/phase7/kappa-case.jpg images/phase7/hideout-plan.jpg images/phase7/crafting-recipe.jpg
images/phase8/skills-field-manual.jpg images/phase8/skills-training-range.jpg images/phase8/economy-loot.jpg images/phase8/economy-ledger.jpg images/phase8/flea-market.jpg images/phase8/money-run.jpg images/phase8/strategy-brief.jpg images/phase8/advanced-tactics.jpg images/phase8/pvp-loadout.jpg images/phase8/pve-prestige.jpg
images/phase9/spt-raid.jpg images/phase9/spt-install.jpg images/phase9/events-timeline.jpg images/phase9/spt-troubleshoot.jpg images/phase9/fika-coop.jpg images/phase9/spt-mods.jpg images/phase9/arena-match.jpg
images/phase10/patch-archive.jpg images/phase10/patch-timeline.jpg images/phase10/resources-briefing.jpg images/phase10/resources-workbench.jpg images/phase10/glossary-notebook.jpg images/phase10/glossary-radio.jpg
audio/ambient/ambient_city.mp3 audio/ambient/ambient_rain.mp3 audio/ambient/ambient_forest.mp3 audio/ambient/ambient_industrial.mp3
'''.split())

DIRECTORY_ROUTES = {
    '/': 'index.html', '/pages/lore/': 'pages/lore/index.html', '/pages/maps/': 'pages/maps/index.html',
    '/pages/weapons/': 'pages/weapons/index.html', '/pages/ammo/': 'pages/ammo/index.html',
    '/pages/armor/': 'pages/armor/index.html', '/pages/bosses/': 'pages/bosses/index.html',
    '/pages/traders/': 'pages/traders/index.html', '/pages/quests/': 'pages/quests/index.html',
    '/pages/hideout/': 'pages/hideout/index.html',
    '/pages/skills/': 'pages/skills/index.html',
    '/pages/economy/': 'pages/economy/index.html',
    '/pages/strategy/': 'pages/strategy/index.html',
    '/pages/spt-tushonka/': 'pages/spt-tushonka/index.html',
    '/pages/arena/': 'pages/arena/index.html',
    '/pages/events/': 'pages/events/index.html',
    '/pages/resources/': 'pages/resources/index.html',
}


class Home(Lab):
    extensions_map = {**Lab.extensions_map, '.xml': 'application/xml', '.json': 'application/json', '.html': 'text/html; charset=utf-8'}

    def end_headers(self):
        if getattr(self, '_vary_encoding', False):
            self.send_header('Vary', 'Accept-Encoding')
        super().end_headers()

    @staticmethod
    def accepts_gzip(header):
        codings = {}
        for item in header.split(','):
            parts = item.strip().lower().split(';')
            if not parts[0]:
                continue
            quality = 1.0
            for param in parts[1:]:
                key, sep, value = param.strip().partition('=')
                if sep and key.strip() == 'q':
                    try: quality = float(value)
                    except ValueError: quality = 0.0
            codings[parts[0]] = quality
        return codings.get('gzip', codings.get('*', 0.0)) > 0

    def send_head(self):
        self.remaining = None
        self._vary_encoding = False
        path = urlsplit(self.path).path
        key = DIRECTORY_ROUTES.get(path, path.removeprefix('/'))
        target = ROOT / key
        if key not in PUBLIC_FILES or not target.is_file() or target.resolve() != target:
            self.send_error(HTTPStatus.NOT_FOUND, 'Ressource non publiee')
            return None
        if target.suffix == '.mp3' and (value := self.headers.get('Range')):
            return self.audio_slice(target, value)
        if path in DIRECTORY_ROUTES:
            self.path = '/' + key
        text_types = {'.html', '.css', '.js', '.mjs', '.json', '.xml', '.txt'}
        if target.suffix in text_types:
            self._vary_encoding = True
        accept_encoding = self.headers.get('Accept-Encoding', '')
        if target.suffix in text_types and self.accepts_gzip(accept_encoding):
            raw = target.read_bytes()
            payload = compress(raw, compresslevel=6, mtime=0)
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', self.guess_type(str(target)))
            self.send_header('Content-Encoding', 'gzip')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Last-Modified', self.date_time_string(target.stat().st_mtime))
            self.end_headers()
            return BytesIO(payload)
        return SimpleHTTPRequestHandler.send_head(self)


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument('--port', default=PREVIEW_PORT, type=int)
    cli.add_argument('--host', default='0.0.0.0')
    settings = cli.parse_args()
    if not (ROOT / 'index.html').is_file():
        cli.error('Générer d’abord index.html avec scripts/build_home.py.')
    with ThreadingHTTPServer((settings.host, settings.port), Home) as server:
        print(f'Tarkov Ultimate Guide · http://{settings.host}:{settings.port}/', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
