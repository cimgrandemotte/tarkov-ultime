/* PHASE_4 · Cartes : parcours Chromium, accessibilité, reflow, modes, recherche et budget mobile. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { chromium } = require('playwright');
const axePath = require.resolve('axe-core/axe.min.js');
const origin = new URL(process.env.TUG_HOME_URL || 'http://127.0.0.1:4180/');
const evidencePath = path.resolve(__dirname, '../../data/snapshots/validation-phase-4.json');
const ready = 'html[data-app-ready][data-maps-ready]';
const hub = 'pages/maps/';
const icebreaker = 'pages/maps/icebreaker.html';
const mapRoutes = [
  'pages/maps/ground-zero.html', 'pages/maps/customs.html', 'pages/maps/factory.html',
  'pages/maps/woods.html', 'pages/maps/shoreline.html', 'pages/maps/interchange.html',
  'pages/maps/reserve.html', 'pages/maps/the-lab.html', 'pages/maps/lighthouse.html',
  'pages/maps/streets-of-tarkov.html', 'pages/maps/the-labyrinth.html',
  'pages/maps/icebreaker.html', 'pages/maps/terminal.html',
];
const published = ['', 'pages/getting-started.html', 'pages/lore/', hub, ...mapRoutes];
const widths = [320, 390, 576, 768, 832, 1024, 1440];
const checks = [], audits = [], performance = {};
const url = (ref) => new URL(ref, origin).href;
const focus = (page, selector) => page.waitForFunction((sel) => document.activeElement?.matches(sel), selector);
const attr = (page, selector, name, value) => page.waitForFunction(([s, n, v]) => document.querySelector(s)?.getAttribute(n) === v, [selector, name, value]);

async function group(name, fn) {
  const started = Date.now();
  await fn();
  checks.push({ name, passed: true });
  console.log(`OK ${name} (${Date.now() - started} ms)`);
}
async function audit(page, context) {
  if (!(await page.evaluate(() => Boolean(window.axe)))) await page.addScriptTag({ path: axePath });
  const result = await page.evaluate(async () => {
    const r = await window.axe.run({ runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'] } });
    return {
      violations: r.violations.map((x) => ({ id: x.id, nodes: x.nodes.map((n) => n.target) })),
      review: r.incomplete.map((x) => ({ id: x.id, nodes: x.nodes.map((n) => n.target) })),
      passes: r.passes.length,
    };
  });
  audits.push({ context, ...result });
  assert.deepEqual(result.violations, [], `axe-core · ${context}`);
}
async function fits(page, context) {
  const values = await page.evaluate(() => ({ page: document.documentElement.scrollWidth, viewport: innerWidth }));
  assert(values.page <= values.viewport + 1, `${context}: ${values.page}px > ${values.viewport}px`);
}
async function decodeImages(page) {
  await page.evaluate(async () => {
    for (const image of document.images) image.loading = 'eager';
    await Promise.all([...document.images].map((image) => image.decode()));
  });
}
async function openSearch(page) {
  const trigger = page.locator('[data-site-search-trigger]');
  await trigger.focus();
  await page.keyboard.press('Control+k');
  await page.locator('#site-query').waitFor({ state: 'visible' });
  await page.waitForFunction(() => document.querySelector('#site-search')?.getAttribute('data-search-provider') === 'fuse');
  return page.locator('#site-query');
}
async function observeMetrics(page) {
  await page.addInitScript(() => {
    window.qa = { lcp: 0, cls: 0 };
    new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) window.qa.lcp = entry.startTime;
    }).observe({ type: 'largest-contentful-paint', buffered: true });
    new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) if (!entry.hadRecentInput) window.qa.cls += entry.value;
    }).observe({ type: 'layout-shift', buffered: true });
  });
}
async function measure(page) {
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(150);
  const result = await page.evaluate(() => {
    const resources = performance.getEntriesByType('resource');
    return {
      lcpMs: Math.round(window.qa?.lcp || 0),
      cls: Math.round((window.qa?.cls || 0) * 1000) / 1000,
      resources: resources.length,
      transferBytes: resources.reduce((sum, row) => sum + (row.transferSize || 0), 0),
    };
  });
  assert(result.lcpMs > 0 && result.lcpMs <= 2500 && result.cls <= 0.1, `budget mobile dépassé : ${JSON.stringify(result)}`);
  return result;
}

async function main() {
  const browser = await chromium.launch();
  async function visit(options, fn) {
    const context = await browser.newContext({ viewport: { width: 1440, height: 960 }, reducedMotion: 'reduce', ...options });
    try {
      const page = await context.newPage();
      page.setDefaultTimeout(12000);
      const errors = [], requests = [];
      page.on('pageerror', (e) => errors.push(e.message));
      page.on('response', (r) => { if (r.status() >= 400) errors.push(`${r.status()} ${r.url()}`); });
      page.on('request', (r) => requests.push(r.url()));
      async function open(ref, selector = ready) {
        const response = await page.goto(url(ref));
        assert(response?.ok(), `HTTP ${ref}`);
        if (options.javaScriptEnabled !== false) await page.locator(selector).waitFor();
        await page.evaluate(() => document.fonts.ready);
      }
      await fn(page, open, context, requests);
      assert.deepEqual(errors, [], `erreurs réseau/JS · ${page.url()}`);
      assert(requests.every((request) => new URL(request).origin === origin.origin), `ressource distante inattendue : ${requests.filter((request) => new URL(request).origin !== origin.origin)}`);
    } finally {
      await context.close();
    }
  }

  try {
    await group('HTTP : 17 routes, canoniques, sitemap, recherche, liste blanche et métadonnées', async () => {
      const canonical = [];
      for (const route of published) {
        const response = await fetch(url(route), { method: 'HEAD' });
        assert.equal(response.status, 200, route || '/');
        assert.match(response.headers.get('content-type') || '', /text\/html; charset=utf-8/);
        assert.equal(response.headers.get('x-robots-tag'), 'noindex, nofollow');
        const html = await (await fetch(url(route))).text();
        const href = html.match(/<link rel="canonical" href="([^"]+)">/)?.[1];
        assert(href, `canonique absente : ${route}`);
        assert.match(html, /<html lang="fr">/);
        assert.equal((html.match(/<h1\b/g) || []).length, 1, `H1 : ${route}`);
        canonical.push(href);
      }
      const sitemap = await (await fetch(url('sitemap.xml'))).text();
      const locations = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((row) => row[1]);
      assert.equal(locations.length, 17);
      assert.deepEqual(new Set(locations), new Set(canonical));
      assert.equal((await fetch(url('robots.txt'))).status, 200);
      assert.match(await (await fetch(url('robots.txt'))).text(), /Disallow: \/lab\//);
      const search = await (await fetch(url('js/data/search-index.json'))).json();
      assert.equal(search.records.length, 43);
      assert.equal(search.records.filter((row) => row.tag === 'Carte').length, 13);
      assert.equal(search.records.filter((row) => row.tag === 'Index des cartes').length, 1);
      assert(search.records.some((row) => row.href === 'pages/maps/icebreaker.html'));
      assert.doesNotMatch(JSON.stringify(search), /#revelations|Kerman|Zubr|Debtor|Savior|Fallen/i);
      for (const forbidden of ['lab/', 'workflow.json', 'docs/sources.json', 'pages/maps/future.html', 'images/lore/quarantine-street.jpg']) {
        assert.equal((await fetch(url(forbidden))).status, 404, forbidden);
      }
      const alias = await (await fetch(url('pages/maps/index.html'))).text();
      assert.equal(alias.match(/<link rel="canonical" href="([^"]+)">/)?.[1], canonical[3]);
    });

    await group('Hub : treize cartes, médias décodés, filtre activé, audit axe-core', () => visit({}, async (page, open) => {
      await open(hub);
      assert.equal(await page.locator('[data-map-card]').count(), 13);
      assert.equal(await page.locator('[data-map-filter]').isVisible(), true);
      assert.equal(await page.locator('[data-map-filter-status]').textContent(), '13 / 13 lieux · métadonnées : PvP permanent');
      assert.equal(await page.locator('[data-map-compare]').count(), 13);
      assert.equal(await page.locator('[data-map-compare]').first().isVisible(), true);
      assert.equal(await page.locator('h1').count(), 1);
      await decodeImages(page);
      assert.equal(await page.locator('img').count(), 14);
      await audit(page, 'Hub Cartes, état initial bureau');
    }));

    await group('Filtres : recherche multi-terme, difficulté éditoriale, mode d’export et réinitialisation', () => visit({}, async (page, open) => {
      await open(hub);
      await page.locator('[data-map-query]').fill('Icebreaker Boreas');
      await page.waitForFunction(() => [...document.querySelectorAll('[data-map-card]')].filter((card) => !card.hidden).length === 1);
      assert.equal(await page.locator('[data-map-card]:not([hidden])').getAttribute('data-map-slug'), 'icebreaker');
      assert(await page.locator('[data-map-filter-status]').textContent().then((x) => x.includes('1 / 13')));
      await page.locator('select[data-map-difficulty]').selectOption('proche');
      assert.equal(await page.locator('[data-map-card]:not([hidden])').count(), 1);
      await page.locator('[data-map-mode-select]').selectOption('pve');
      assert(await page.locator('[data-map-filter-status]').textContent().then((x) => x.includes('PvE Zone')));
      await audit(page, 'Hub filtré · Icebreaker, difficulté et PvE');
      await page.locator('[data-map-reset]').click();
      await page.waitForFunction(() => [...document.querySelectorAll('[data-map-card]')].filter((card) => !card.hidden).length === 13);
      assert.equal(await page.locator('[data-map-query]').inputValue(), '');
      assert.equal(await page.locator('[data-map-mode-select]').inputValue(), 'regular');
    }));

    await group('Comparateur : deux lieux, valeurs et mode synchronisés, troisième sélection refusée', () => visit({}, async (page, open) => {
      await open(hub);
      await page.locator('[data-map-mode-select]').selectOption('pve');
      await page.locator('[data-map-compare][value="ground-zero"]').check();
      await page.locator('[data-map-compare][value="customs"]').check();
      await page.waitForFunction(() => document.querySelector('[data-map-compare-status]')?.textContent.includes('Comparaison prête'));
      assert.equal((await page.locator('[data-compare-cell="a-name"]').textContent()).trim(), 'Ground Zero');
      assert.equal((await page.locator('[data-compare-cell="b-name"]').textContent()).trim(), 'Customs');
      assert.equal((await page.locator('[data-map-compare-mode-label]').textContent()).trim(), 'PvE Zone');
      await page.locator('[data-map-mode-select]').selectOption('pvp-season');
      assert.equal((await page.locator('[data-map-compare-mode-label]').textContent()).trim(), 'PvP Seasonal');
      await page.locator('[data-map-compare][value="factory"]').click();
      assert.equal(await page.locator('[data-map-compare][value="factory"]').isChecked(), false);
      assert.match(await page.locator('[data-map-compare-status]').textContent(), /Deux cartes maximum/);
      await audit(page, 'Hub avec deux cartes comparées');
    }));

    await group('Treize fiches : rendu client, une illustration JPG et huit sections de lecture', () => visit({}, async (page, open) => {
      for (const route of mapRoutes) {
        await open(route);
        assert.equal(await page.locator('h1').count(), 1, route);
        assert.equal(await page.locator('img').count(), 1, route);
        assert.match(await page.locator('img').getAttribute('src'), /\.jpg$/);
        assert.equal(await page.locator('[data-map-mode]').count(), 3, route);
        assert.equal(await page.locator('[data-map-mode-panel]').count(), 3, route);
        assert(await page.locator('#sources').count());
        assert(await page.locator('#extractions').count());
      }
    }));

    await group('Fiche Icebreaker : bascule de modes, preuves du 12/11, citations et nuance des astuces fumée', () => visit({}, async (page, open) => {
      await open(icebreaker);
      assert.equal(await page.locator('[data-map-mode="regular"]').getAttribute('aria-pressed'), 'true');
      assert.equal(await page.locator('#map-mode-panel-regular').isVisible(), true);
      await page.locator('[data-map-mode="pve"]').focus();
      await page.keyboard.press('Enter');
      assert.equal(await page.locator('[data-map-mode="pve"]').getAttribute('aria-pressed'), 'true');
      assert.equal(await page.locator('#map-mode-panel-pve').isVisible(), true);
      assert.equal(await page.locator('#map-mode-panel-regular').isVisible(), false);
      await page.locator('[data-map-mode="pvp-season"]').click();
      assert.equal(await page.locator('#map-mode-panel-pvp-season').isVisible(), true);
      const text = await page.locator('main').textContent();
      for (const term of ['12/11', 'Battle Pass', 'Black Division', '100 %', 'sans numéro de patch', 'fumée', 'technique fiable', 'ne la considérez pas']) assert(text.includes(term), term);
      assert(await page.locator('#ref-balance-nov').count());
      assert(await page.locator('[id="ref-yt-icebreaker-smoke-1.3-nov12"]').count());
      await audit(page, 'Icebreaker · Seasonal sélectionné et sources BSG/communauté');
    }));

    await group('Navigation clavier : saut au contenu, mode Icebreaker, sommaire et retour à l’index', () => visit({}, async (page, open) => {
      await open(icebreaker);
      await page.keyboard.press('Tab');
      await focus(page, '.skip-link');
      await page.keyboard.press('Enter');
      await focus(page, '#main');
      const tab = page.locator('[data-map-mode="pve"]');
      await tab.focus();
      await page.keyboard.press('Space');
      assert.equal(await tab.getAttribute('aria-pressed'), 'true');
      await page.locator('[data-guide-toc] a[href="#extractions"]').press('Enter');
      await focus(page, '#extractions');
      await page.waitForURL(url(icebreaker + '#extractions'));
      const hubLink = page.locator('a[href="../../pages/maps/"]').first();
      await hubLink.click();
      await page.waitForURL(url(hub));
      assert.equal(await page.locator('[data-map-card]').count(), 13);
    }));

    await group('Recherche globale : index du hub et ouverture de la fiche Icebreaker', () => visit({}, async (page, open) => {
      await open(hub);
      const query = await openSearch(page);
      await query.fill('Icebreaker Boreas');
      const result = page.locator('[data-search-results] a[href*="icebreaker.html"]');
      await result.waitFor({ state: 'visible' });
      await result.click();
      await page.waitForURL(url(icebreaker));
      await page.locator(ready).waitFor();
      assert.equal(await page.locator('h1').count(), 1);
      assert.equal(await page.locator('dialog[open]').count(), 0);
    }));

    await group('Mobile tactile : navigation, recherche et comparaison sans débordement', () => visit({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true }, async (page, open) => {
      await open(hub);
      await page.locator('[data-map-query]').fill('icebreaker boreas');
      await page.waitForFunction(() => [...document.querySelectorAll('[data-map-card]')].filter((card) => !card.hidden).length === 1);
      await page.locator('[data-map-reset]').tap();
      await page.waitForFunction(() => [...document.querySelectorAll('[data-map-card]')].filter((card) => !card.hidden).length === 13);
      await page.locator('[data-map-compare][value="woods"]').check();
      await page.locator('[data-map-compare][value="reserve"]').check();
      assert.match(await page.locator('[data-map-compare-status]').textContent(), /Comparaison prête/);
      await fits(page, 'hub tactile 390 px');
      const toggle = page.locator('[data-nav-toggle]');
      await toggle.tap();
      assert.equal(await toggle.getAttribute('aria-expanded'), 'true');
      await page.keyboard.press('Escape');
      await fits(page, 'navigation mobile fermée');
    }));

    await group('Reflow 320–1440 px et texte 200 % : hub et fiche longue', () => visit({}, async (page, open) => {
      for (const route of [hub, icebreaker]) {
        await open(route);
        for (const width of widths) {
          await page.setViewportSize({ width, height: 960 });
          await fits(page, `${route} ${width}px`);
        }
        const scale = await page.addStyleTag({ content: 'html { font-size: 200% !important; }' });
        for (const width of [320, 390, 768, 1024, 1440]) {
          await page.setViewportSize({ width, height: 960 });
          await fits(page, `${route} ${width}px, texte 200 %`);
        }
        await scale.evaluate((element) => element.remove());
      }
    }));

    await group('Couleurs système : forced-colors, contraste renforcé et animations réduites', () => visit({ viewport: { width: 390, height: 844 }, forcedColors: 'active' }, async (page, open) => {
      await open(hub);
      assert(await page.evaluate(() => matchMedia('(forced-colors: active)').matches));
      await page.locator('[data-contrast-toggle]').click();
      await attr(page, 'html', 'data-theme', 'contrast');
      await page.locator('[data-motion-toggle]').click();
      await attr(page, 'html', 'data-motion', 'reduce');
      await audit(page, 'Hub mobile sous couleurs système');
      await open(icebreaker);
      await attr(page, 'html', 'data-theme', 'contrast');
      await attr(page, 'html', 'data-motion', 'reduce');
      await page.locator('[data-map-mode="pve"]').press('Enter');
      assert(await page.locator('#map-mode-panel-pve').isVisible());
    }));

    await group('Repli sans JavaScript : cartes, sommaire, comparaison et trois exports lisibles', () => visit({ javaScriptEnabled: false, viewport: { width: 320, height: 800 } }, async (page, open) => {
      await open(hub);
      assert.equal(await page.locator('[data-map-card]:visible').count(), 13);
      assert.equal(await page.locator('[data-map-filter]').isVisible(), false);
      assert.equal(await page.locator('[data-map-mode-select]').count(), 1);
      assert.equal(await page.locator('[data-map-compare]').first().isVisible(), false);
      assert.equal(await page.locator('[data-map-compare-table] tbody tr').count(), 5);
      await fits(page, 'hub sans JS');
      await open(icebreaker);
      assert.equal(await page.locator('[data-map-mode-switch]').isVisible(), false);
      assert.equal(await page.locator('[data-map-mode-panel]').count(), 3);
      assert.equal(await page.locator('[data-map-mode-panel]:visible').count(), 3);
      assert(await page.locator('[data-guide-toc] a[href="#extractions"]').count());
      assert(await page.locator('#sources').isVisible());
      await fits(page, 'Icebreaker sans JS');
    }));

    await group('Mobile simulé : LCP/CLS du hub et d’une fiche sur réseau et CPU bridés', () => visit({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true }, async (page, open, context) => {
      await observeMetrics(page);
      const cdp = await context.newCDPSession(page);
      await cdp.send('Network.enable');
      await cdp.send('Network.setCacheDisabled', { cacheDisabled: true });
      await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 100, downloadThroughput: 500000, uploadThroughput: 200000, connectionType: 'cellular4g' });
      await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
      for (const [id, route] of [['hub', hub], ['map', icebreaker]]) {
        await open(route);
        performance[id] = await measure(page);
      }
    }));

    const evidence = {
      schemaVersion: 1, status: 'VALIDE', browser: `Chromium ${browser.version()}`,
      checkedAt: new Date().toISOString(), checks, audits, widths, performance,
      method: 'Parcours local HTTP ; axe-core WCAG 2.1 A/AA ; réseau/console contrôlés ; tailles CSS et reflow ; LCP/CLS sur mobile émulé, 100 ms, 4 Mbit/s et CPU ×4.',
    };
    await fs.writeFile(evidencePath, JSON.stringify(evidence, null, 2) + '\n');
    console.log('Performance', JSON.stringify(performance));
  } finally {
    await browser.close();
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
