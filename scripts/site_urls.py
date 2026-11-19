"""Politique partagée pour ne jamais annoncer un aperçu ou une base non confirmée comme canonique."""
import os
from urllib.parse import urlsplit

_RESERVED_HOSTS = {'localhost', '127.0.0.1', '::1', 'example.com', 'example.net', 'example.org'}
_RESERVED_SUFFIXES = ('.e2b.app', '.arena.ai', '.localhost', '.test', '.example.com', '.example.net', '.example.org')


def _host(base: str) -> str:
    return (urlsplit(str(base or '')).hostname or '').lower().rstrip('.')


def is_preview_base(base: str) -> bool:
    """Hosts locaux, réservés et aperçus connus; acceptables pour un build local non publiable."""
    host = _host(base)
    return bool(host) and (host in _RESERVED_HOSTS or any(host.endswith(suffix) for suffix in _RESERVED_SUFFIXES))


def seo_base_is_public(base: str) -> bool:
    """True seulement pour HTTPS après confirmation explicite, jamais pour preview/exemple/local."""
    parsed = urlsplit(str(base or ''))
    host = _host(base)
    if parsed.scheme != 'https' or not host or host in _RESERVED_HOSTS:
        return False
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        return False
    if any(host.endswith(suffix) for suffix in _RESERVED_SUFFIXES):
        return False
    if parsed.path and not parsed.path.startswith('/'):
        return False
    # A syntactically plausible hostname is not evidence that DNS, TLS, or Pages routing works.
    # The build must be explicitly authorized only after those have been confirmed.
    return os.getenv('TUG_PUBLIC_BASE_CONFIRMED') == '1'


def canonical_link(base: str, route: str) -> str:
    if not seo_base_is_public(base):
        return ''
    from urllib.parse import urljoin
    from html import escape
    return f'<link rel="canonical" href="{escape(urljoin(base, route), quote=True)}">'


def open_graph_url_meta(base: str, route: str) -> str:
    if not seo_base_is_public(base):
        return ''
    from urllib.parse import urljoin
    from html import escape
    return f'<meta property="og:url" content="{escape(urljoin(base, route), quote=True)}">'
