#!/usr/bin/env python3
"""Sert l'atelier et ses seules ressources HTTP, sans index de répertoire."""
from argparse import ArgumentParser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PLAN = {
    'audio': {'.mp3'}, 'css': {'.css'}, 'fonts': {'.css', '.woff2'},
    'images': {'.jpg'}, 'js': {'.js', '.mjs', '.json'}, 'vendor': {'.js', '.mjs', '.css'},
}
BENCH = {Path('lab/index.html'), Path('lab/search-index.json')}


class Lab(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
                      '.js': 'application/javascript', '.mjs': 'application/javascript',
                      '.woff2': 'font/woff2', '.jpg': 'image/jpeg', '.mp3': 'audio/mpeg'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Robots-Tag', 'noindex, nofollow')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def send_head(self):
        self.remaining = None
        raw = urlsplit(self.path).path
        if raw in ('/', '/lab'):
            self.send_response(HTTPStatus.FOUND)
            self.send_header('Location', '/lab/')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return None
        if raw == '/lab/':
            self.path = '/lab/index.html'
        try:
            target = Path(self.translate_path(self.path)).resolve()
            key = target.relative_to(ROOT)
            allowed = key in BENCH or (len(key.parts) >= 2 and key.suffix in PLAN.get(key.parts[0], set()))
        except (ValueError, OSError):
            allowed = False
        if not allowed or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, 'Asset not found')
            return None
        if key.suffix == '.mp3' and (value := self.headers.get('Range')):
            return self.audio_slice(target, value)
        return super().send_head()

    def audio_slice(self, target, value):
        """Les lecteurs natifs peuvent demander une plage du flux MP3."""
        match = re.fullmatch(r'bytes=(\d{0,20})-(\d{0,20})', value.strip(), flags=re.ASCII)
        size = target.stat().st_size
        if match and (match[1] or match[2]):
            if match[1]:
                start = int(match[1])
                end = min(int(match[2]), size - 1) if match[2] else size - 1
            else:
                start, end = max(0, size - int(match[2])), size - 1
            if start <= end:
                handle = target.open('rb')
                handle.seek(start)
                self.remaining = end - start + 1
                self.send_response(HTTPStatus.PARTIAL_CONTENT)
                self.send_header('Content-Type', 'audio/mpeg')
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
                self.send_header('Content-Length', str(self.remaining))
                self.end_headers()
                return handle
        self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
        self.send_header('Content-Range', f'bytes */{size}')
        self.send_header('Content-Length', '0')
        self.end_headers()
        return None

    def copyfile(self, source, outputfile):
        if self.remaining is None:
            return super().copyfile(source, outputfile)
        while self.remaining:
            block = source.read(min(self.remaining, 64 * 1024))
            if not block:
                return
            outputfile.write(block)
            self.remaining -= len(block)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--port', default=4173, type=int)
    parser.add_argument('--host', default='0.0.0.0')
    config = parser.parse_args()
    with ThreadingHTTPServer((config.host, config.port), Lab) as http:
        print(f'Atelier Tarkov Ultimate Guide · http://{config.host}:{config.port}/lab/', flush=True)
        try:
            http.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
