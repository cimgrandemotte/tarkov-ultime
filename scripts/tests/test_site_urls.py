#!/usr/bin/env python3
"""Small regression test for the explicit public-base confirmation gate."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_urls import canonical_link, is_preview_base, open_graph_url_meta, seo_base_is_public  # noqa: E402


class PublicBaseGateTests(unittest.TestCase):
    def test_unconfirmed_https_host_is_not_public(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop('TUG_PUBLIC_BASE_CONFIRMED', None)
            base = 'https://gta6guide.duckdns.org/'
            self.assertFalse(seo_base_is_public(base))
            self.assertEqual(canonical_link(base, 'pages/'), '')
            self.assertEqual(open_graph_url_meta(base, 'pages/'), '')

    def test_explicit_confirmation_allows_a_real_base(self):
        with patch.dict(os.environ, {'TUG_PUBLIC_BASE_CONFIRMED': '1'}):
            base = 'https://guide.example.tld/tarkov/'
            self.assertTrue(seo_base_is_public(base))
            self.assertIn('rel="canonical"', canonical_link(base, 'pages/'))
            self.assertIn('property="og:url"', open_graph_url_meta(base, 'pages/'))

    def test_preview_and_reserved_hosts_never_become_public(self):
        with patch.dict(os.environ, {'TUG_PUBLIC_BASE_CONFIRMED': '1'}):
            for base in (
                'https://4180-sandbox.e2b.app/',
                'https://example.test/',
                'https://localhost/',
                'https://127.0.0.1/',
            ):
                self.assertTrue(is_preview_base(base))
                self.assertFalse(seo_base_is_public(base), base)
                self.assertEqual(canonical_link(base, ''), '')
                self.assertEqual(open_graph_url_meta(base, ''), '')


if __name__ == '__main__':
    unittest.main(verbosity=2)
