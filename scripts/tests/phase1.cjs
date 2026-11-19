/* Validation de l'atelier servi en HTTP. Dépendances de test seulement : playwright, axe-core. */
'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs/promises');
const { chromium } = require('playwright');
const axePath = require.resolve('axe-core/axe.min.js');
const target = new URL(process.env.TUG_LAB_URL || 'http://127.0.0.1:4173/lab/');
const audits = [];
const results = [];
const assets = {};

async function section(name, test) {
  const start = Date.now();
  await test();
  results.push({ name, passed: true });
  console.log(`OK  ${name} (${Date.now() - start} ms)`);
}
async function checkAxe(page, context) {
  if (!(await page.evaluate(() => Boolean(window.axe)))) await page.addScriptTag({ path: axePath });
  const data = await page.evaluate(async () => {
    const result = await window.axe.run({ runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'] } });
    return {
      violations: result.violations.map(({ id, nodes }) => ({ id, selectors: nodes.map((n) => n.target) })),
      needsReview: result.incomplete.map(({ id, nodes }) => ({ id, count: nodes.length })),
      passes: result.passes.length,
    };
  });
  audits.push({ context, ...data });
  assert.deepEqual(data.violations, [], `axe-core : ${context}`);
}
const focused = (page, selector) => page.waitForFunction((s) => document.activeElement?.matches(s), selector);
const state = (page, selector, attr, value) => page.waitForFunction(([s, a, v]) => document.querySelector(s)?.getAttribute(a) === v, [selector, attr, value]);
const openSearch = '[data-site-search-trigger]';
const ready = ':root[data-app-ready="true"]';
const firstResult = '[data-search-results] a:first-child';
const compare = '[data-compare-open]';
const audio = '[data-audio-deck]';

async function run() {
  const browser = await chromium.launch();
  async function visit(options, test, { monitor = true } = {}) {
    const context = await browser.newContext({ viewport: { width: 1440, height: 950 }, reducedMotion: 'reduce', ...options });
    const page = await context.newPage();
    page.setDefaultTimeout(6000);
    const failures = [], requests = [];
    page.on('pageerror', (e) => failures.push(e.message));
    page.on('response', (response) => { if (response.status() >= 400) failures.push(`${response.status()} ${response.url()}`); });
    page.on('request', (request) => requests.push(request.url()));
    const open = async () => {
      await page.goto(target.href);
      if (options.javaScriptEnabled !== false) await page.locator(ready).waitFor();
      await page.evaluate(() => document.fonts.ready);
    };
    try {
      await test(page, open, requests);
      if (monitor) assert.deepEqual(failures, [], 'Erreurs d’exécution et réponses réseau');
    } finally {
      await context.close();
    }
  }

  try {
    await section('Serveur : accueil technique, ressources locales et non-indexation', async () => {
      const root = await fetch(new URL('/', target), { redirect: 'manual' });
      assert.equal(root.status, 302);
      assert.equal(root.headers.get('location'), '/lab/');
      const html = await fetch(target);
      assert.equal(html.status, 200);
      assert.equal(html.headers.get('x-robots-tag'), 'noindex, nofollow');
      assert.match(await html.text(), /name="robots" content="noindex,nofollow"/);
      assert.equal((await fetch(new URL('/workflow.json', target))).status, 404);
      assert.equal((await fetch(new URL('/pages/maps/index.html', target))).status, 404);
      const mp3 = new URL('/audio/ambient/ambient_rain.mp3', target);
      assert.equal((await fetch(mp3, { method: 'HEAD' })).headers.get('content-type'), 'audio/mpeg');
      const chunk = await fetch(mp3, { headers: { Range: 'bytes=0-31' } });
      assert.equal(chunk.status, 206);
      assert.match(chunk.headers.get('content-range'), /^bytes 0-31\/\d+$/);
      assert.equal((await chunk.arrayBuffer()).byteLength, 32);
      await visit({}, async (page, open, requests) => {
        await page.addInitScript(() => {
          window.qaMetrics = { lcp: null, cls: 0 };
          new PerformanceObserver((list) => { for (const entry of list.getEntries()) window.qaMetrics.lcp = entry.startTime; }).observe({ type: 'largest-contentful-paint', buffered: true });
          new PerformanceObserver((list) => { for (const entry of list.getEntries()) if (!entry.hadRecentInput) window.qaMetrics.cls += entry.value; }).observe({ type: 'layout-shift', buffered: true });
        });
        await open();
        await page.waitForLoadState('networkidle');
        assert(requests.every((href) => new URL(href).origin === target.origin));
        assert(!requests.some((href) => /\.mp3$|search-index|fuse\.basic|(?:ammo|items|armor|weapons)\.json$/.test(href)));
        assets.initial = await page.evaluate(() => ({
          count: performance.getEntriesByType('resource').length,
          transferBytes: Math.round(performance.getEntriesByType('resource').reduce((sum, r) => sum + r.transferSize, 0)),
          lcpMs: window.qaMetrics.lcp === null ? null : Math.round(window.qaMetrics.lcp), cls: Math.round(window.qaMetrics.cls * 1000) / 1000,
        }));
        assert(await page.evaluate(() => document.fonts.check('800 32px Orbitron') && document.fonts.check('400 16px Inter')));
        await checkAxe(page, 'Bureau 1440 px · interface initiale');
      });
    });

    await section('Clavier : évitement, méga-menu, fermeture et retour en haut', () => visit({}, async (page, open) => {
      await open();
      await page.keyboard.press('Tab');
      await focused(page, '.skip-link');
      assert(await page.locator('.skip-link').evaluate((el) => el.getBoundingClientRect().top >= 0));
      await page.keyboard.press('Enter');
      await focused(page, '#main');
      await page.locator('.mega-menu__summary').press('Enter');
      await page.locator('.mega-menu[open] .mega-menu__item').first().waitFor();
      await page.keyboard.press('Tab');
      await focused(page, '.mega-menu__item');
      await page.keyboard.press('Escape');
      await focused(page, '.mega-menu__summary');
      await page.locator('.mega-menu[open]').waitFor({ state: 'hidden' });
      await page.locator('.site-footer a[href="#sources-atelier"]').focus();
      const top = page.locator('[data-back-top]');
      await top.waitFor();
      await top.press('Enter');
      await focused(page, '#top');
      assert.equal(await page.evaluate(() => window.scrollY), 0);
    }));

    await section('Recherche : Fuse différé, accents, coquille, clavier et destinations', () => visit({}, async (page, open, requests) => {
      await open();
      await page.locator(openSearch).focus();
      await page.keyboard.press('Control+k');
      await focused(page, '#site-query');
      await state(page, '#site-search', 'data-search-provider', 'fuse');
      assert(requests.some((url) => url.endsWith('/lab/search-index.json')) && requests.some((url) => url.endsWith('/vendor/fuse.basic.min.mjs')));
      await page.locator('#site-query').fill('foret');
      await page.waitForFunction(() => document.querySelector('[data-search-results] a')?.hash === '#audio');
      await page.keyboard.press('ArrowDown');
      await focused(page, '[data-search-results] a[href$="#audio"]');
      await page.keyboard.press('Tab');
      await focused(page, '#site-search [data-modal-close]');
      await page.keyboard.press('Shift+Tab');
      await focused(page, '[data-search-results] a[href$="#audio"]');
      await checkAxe(page, 'Modale de recherche ouverte');
      await page.locator('#site-query').fill('comparteur');
      await page.waitForFunction(() => document.querySelector('[data-search-results] a')?.hash === '#catalogue');
      await page.locator('#site-query').fill('zyxyuvwzzzz');
      await page.waitForFunction(() => document.querySelector('[data-search-status]').textContent.includes('Aucun résultat'));
      assert.equal(await page.locator(firstResult).count(), 0);
      await page.keyboard.press('Escape');
      await page.locator('#site-search[open]').waitFor({ state: 'hidden' });
      await focused(page, openSearch);
      await page.locator('#catalogue-family').selectOption('smg');
      assert.equal(await page.locator('#specimen-ak74n').isVisible(), false);
      await page.locator(openSearch).click();
      await page.locator('#site-query').fill('AK-74N');
      await page.keyboard.press('Enter');
      await focused(page, '#specimen-ak74n');
      assert.equal(new URL(page.url()).hash, '#specimen-ak74n');
      assert.equal(await page.locator('#catalogue-family').inputValue(), '');
      assert(await page.locator('#specimen-ak74n').isVisible());
    }));

    await section('Recherche : dégradation sans Fuse et message si index indisponible', () => visit({}, async (page, open) => {
      await page.route('**/vendor/fuse.basic.min.mjs', (route) => route.fulfill({ status: 503, body: '' }));
      await page.route('**/lab/search-index.json', (route) => route.fulfill({ status: 503, body: '' }));
      await open();
      await page.locator(openSearch).click();
      await page.waitForFunction(() => document.querySelector('[data-search-status]').textContent.includes('Index indisponible'));
      await page.keyboard.press('Escape');
      await page.unroute('**/lab/search-index.json');
      await page.locator(openSearch).click();
      await state(page, '#site-search', 'data-search-provider', 'local');
      await page.locator('#site-query').fill('ergonomie');
      await page.waitForFunction(() => document.querySelector('[data-search-results] a')?.hash === '#dataset');
    }, { monitor: false }));

    await section('Catalogue : filtre composé, tri réel, état vide et réinitialisation', () => visit({}, async (page, open) => {
      await open();
      const count = page.locator('[data-filter-count]');
      assert.equal(await count.innerText(), '6 modèles affichés');
      await page.locator('#catalogue-query').fill('fusil a pompe');
      assert.equal(await count.innerText(), '2 modèles affichés');
      await page.locator('#catalogue-family').selectOption('smg');
      assert.equal(await count.innerText(), '0 modèles affichés');
      assert(await page.locator('[data-filter-empty]').isVisible());
      await page.locator('[data-filter-form] button[type=reset]').click();
      await page.locator('#catalogue-sort').selectOption('ergo');
      assert.equal(await page.locator('[data-filter-row]:not([hidden])').first().getAttribute('id'), 'specimen-mp5');
      await page.locator('#catalogue-sort').selectOption('');
      assert.equal(await page.locator('[data-filter-row]:not([hidden])').first().getAttribute('id'), 'specimen-ak74n');
    }));

    await section('Comparateur : deux à trois entrées, retrait, focus et tableau', () => visit({}, async (page, open) => {
      await open();
      const add = (slug) => page.locator(`[data-compare-toggle="${slug}"]`);
      const trigger = page.locator(compare);
      assert(await trigger.isDisabled());
      await add('ak74n').press('Space');
      assert.equal(await add('ak74n').getAttribute('aria-pressed'), 'true');
      await add('m4a1').press('Space');
      assert(await trigger.isEnabled());
      await add('mp5').click();
      await add('vityaz').click();
      assert.match(await page.locator('[data-compare-status]').innerText(), /Limite atteinte/);
      assert.equal(await add('vityaz').getAttribute('aria-pressed'), 'false');
      await trigger.press('Enter');
      await focused(page, '#compare-title');
      assert.equal(await page.locator('#compare-dialog th[scope=col]').count(), 4);
      assert.match(await page.locator('#compare-dialog tbody').innerText(), /800\s+c\/min/);
      assert.match(await page.locator('#compare-dialog tbody').innerText(), /2,092\s+kg/);
      await checkAxe(page, 'Comparateur ouvert · trois entrées');
      await page.keyboard.press('Escape');
      await focused(page, compare);
      await trigger.click();
      await page.locator('[data-compare-remove="mp5"]').click();
      assert.equal(await page.locator('#compare-dialog th[scope=col]').count(), 3);
      await page.locator('[data-compare-remove="m4a1"]').click();
      assert.match(await page.locator('[data-compare-output]').innerText(), /au moins deux/);
      await page.keyboard.press('Escape');
      await focused(page, '[data-compare-toggle="m4a1"]');
      await page.locator('[data-compare-clear]').click();
      await focused(page, '#catalogue-query');
      assert.match(await page.locator('[data-compare-status]').innerText(), /^0\/3/);
    }));

    await section('Onglets et accordéons au clavier ; classement local et remise à zéro', () => visit({}, async (page, open) => {
      await open();
      await page.locator('#tab-shortcuts').focus();
      await page.keyboard.press('ArrowRight');
      await focused(page, '#tab-display');
      await state(page, '#tab-display', 'aria-selected', 'true');
      assert(await page.locator('#panel-display').isVisible());
      assert(!(await page.locator('#panel-shortcuts').isVisible()));
      await page.keyboard.press('End');
      await focused(page, '#tab-storage');
      await page.keyboard.press('Home');
      await focused(page, '#tab-shortcuts');
      const detail = page.locator('#modules details').first();
      await detail.locator('summary').press('Enter');
      assert(await detail.evaluate((el) => el.open));
      await detail.locator('summary').press('Space');
      assert(!(await detail.evaluate((el) => el.open)));
      const firstTier = page.locator('[data-tier-item=first]');
      await firstTier.selectOption('D');
      assert.match(await page.locator('[data-tier-rank=D]').innerText(), /Premier raid/);
      await open();
      assert.equal(await firstTier.inputValue(), 'D');
      await page.locator('[data-tier-reset]').click();
      assert.equal(await firstTier.inputValue(), 'S');
    }));

    await section('Infobulle : au survol, sur le texte, au focus, Échap et toucher', async () => {
      await visit({}, async (page, open) => {
        await open();
        const trigger = page.locator('[data-tooltip]'), tooltip = page.locator('#tip-ergo');
        await trigger.hover();
        await tooltip.waitFor();
        const box = await tooltip.boundingBox();
        assert(box.x >= 0 && box.x + box.width <= 1440 && box.y >= 0 && box.y + box.height <= 950);
        await tooltip.hover();
        await page.waitForTimeout(190);
        assert(await tooltip.isVisible());
        await trigger.focus();
        await page.keyboard.press('Escape');
        await tooltip.waitFor({ state: 'hidden' });
        await focused(page, '[data-tooltip]');
      });
      await visit({ hasTouch: true, viewport: { width: 390, height: 820 } }, async (page, open) => {
        await open();
        await page.locator('[data-tooltip]').tap();
        await page.locator('#tip-ergo').waitFor();
        await page.locator('[data-tooltip]').tap();
        await page.locator('#tip-ergo').waitFor({ state: 'hidden' });
      });
    });

    await section('Audio : aucune requête avant action, pause, piste, volume et signal opt-in', () => visit({}, async (page, open, requests) => {
      await open();
      const play = page.locator('[data-audio-deck] [data-audio-toggle]');
      const tracks = () => requests.filter((url) => url.endsWith('.mp3'));
      assert.equal(tracks().length, 0);
      await page.locator('[data-audio-cue=click]').hover();
      assert.equal(tracks().length, 0);
      await play.press('Enter');
      await state(page, audio, 'data-audio-state', 'playing');
      assert(tracks().some((url) => url.endsWith('ambient_rain.mp3')));
      await play.press('Space');
      await state(page, audio, 'data-audio-state', 'paused');
      const beforeChange = tracks().length;
      await page.locator('[data-audio-select]').selectOption('forest');
      await state(page, audio, 'data-audio-state', 'idle');
      assert.equal(tracks().length, beforeChange);
      await play.click();
      await state(page, audio, 'data-audio-state', 'playing');
      assert(tracks().some((url) => url.endsWith('ambient_forest.mp3')));
      const range = page.locator('[data-audio-volume]');
      await range.press('ArrowRight');
      assert.equal(await range.inputValue(), '25');
      assert.equal(await page.locator('[data-audio-percent]').innerText(), '25 %');
      await play.click();
      await Promise.all([page.waitForRequest('**/ui_click.mp3'), page.locator('[data-audio-cue=click]').click()]);
      const beforeReload = tracks().length;
      await open();
      assert.equal(await range.inputValue(), '25');
      assert.equal(tracks().length, beforeReload);
      await state(page, audio, 'data-audio-state', 'idle');
    }));

    await section('Préférences : mouvement système, commande manuelle et contraste persistant', () => visit({ reducedMotion: 'no-preference' }, async (page, open) => {
      await open();
      await state(page, '[data-motion-hero]', 'data-motion-visible', 'true');
      assert.equal(await page.locator('.particles__drop').count(), 16);
      await page.evaluate(() => scrollTo(0, 135));
      await page.waitForFunction(() => parseFloat(document.querySelector('[data-motion-hero]').style.getPropertyValue('--parallax-shift')) > 0);
      await page.locator('[data-motion-toggle]').click();
      await state(page, ':root', 'data-motion', 'reduce');
      await page.waitForFunction(() => document.querySelector('[data-motion-hero]').style.getPropertyValue('--parallax-shift') === '0px');
      assert.equal(await page.locator('[data-reveal][data-aos]').count(), 0);
      await page.locator('[data-contrast-toggle]').click();
      await state(page, ':root', 'data-theme', 'contrast');
      await checkAxe(page, 'Contraste renforcé et animations réduites');
      await open();
      await state(page, ':root', 'data-motion', 'reduce');
      await state(page, ':root', 'data-theme', 'contrast');
      await page.emulateMedia({ reducedMotion: 'reduce' });
      await page.locator('[data-motion-toggle]').click();
      await state(page, ':root', 'data-motion', null);
      assert.equal(await page.locator('[data-reveal][data-aos]').count(), 0);
      assert.equal(await page.locator('.dialog').first().evaluate((el) => getComputedStyle(el).animationName), 'none');
    }));

    await section('Reflow : 320, 375, 390, 768, 832, 1024 et 1440 px, texte agrandi', async () => {
      for (const width of [320, 375, 390, 768, 832, 1024, 1440]) {
        await visit({ viewport: { width, height: 850 } }, async (page, open) => {
          await open();
          assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width, `reflow ${width}px`);
          if (width === 320) {
            await checkAxe(page, 'Mobile 320 px · interface initiale');
            await page.locator('[data-nav-toggle]').press('Enter');
            await state(page, '[data-nav-toggle]', 'aria-expanded', 'true');
            await focused(page, '#global-nav a');
            await page.keyboard.press('Escape');
            await focused(page, '[data-nav-toggle]');
            await page.locator('[data-nav-toggle]').click();
            await page.locator('.mega-menu__summary').click();
            await page.locator('.mega-menu__item[href="#catalogue"]').click();
            await focused(page, '#catalogue');
            assert.equal(await page.locator('[data-site-nav]').isVisible(), false);
            await page.locator('[data-compare-toggle="ak74n"]').click();
            await page.locator('[data-compare-toggle="m4a1"]').click();
            await page.locator(compare).click();
            const scroller = page.locator('.data-table__scroll');
            await scroller.focus();
            await page.keyboard.press('ArrowRight');
            await page.waitForFunction(() => document.querySelector('.data-table__scroll')?.scrollLeft > 0);
            assert(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth));
          }
          if (width >= 768) {
            await page.addStyleTag({ content: 'html { font-size: 200%; }' });
            assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width, 'texte 200 %');
          }
        });
      }
    });

    await section('Progressif : données, navigation, accordéons et audio natif sans JavaScript', () => visit({ javaScriptEnabled: false, viewport: { width: 390, height: 840 } }, async (page, open, requests) => {
      await open();
      assert(await page.locator('[data-site-nav]').isVisible());
      assert(await page.locator('[data-audio-fallback]').isVisible());
      assert.equal(await page.locator('[data-filter-row]').count(), 6);
      assert.equal(await page.locator('[data-filter-form]').isVisible(), false);
      assert(await page.locator('#panel-storage').isVisible());
      await page.locator('.mega-menu__summary').click();
      assert(await page.locator('.mega-menu__item[href="#catalogue"]').isVisible());
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), 390);
      assert(!requests.some((url) => url.endsWith('.mp3')));
    }));

    const versions = { browser: browser.version(), playwright: require('playwright/package.json').version, axeCore: require('axe-core/package.json').version };
    const report = { schemaVersion: 1, checkedAt: new Date().toISOString(), versions, status: 'VALIDE', results, audits, assets };
    const out = process.env.TUG_QA_REPORT || path.resolve(__dirname, '../../data/snapshots/validation-phase-1.json');
    await fs.writeFile(out, `${JSON.stringify(report, null, 2)}\n`);
    console.log(`\n${results.length} groupes de contrôles et ${audits.length} audits axe-core validés sur Chromium ${versions.browser}.`);
    console.log('A contrôler manuellement : échantillons de contraste sur arrière-plans composites et navigation avec lecteurs d’écran réels.');
  } finally {
    await browser.close();
  }
}
run().catch((error) => { console.error(error); process.exitCode = 1; });
