/* PHASE_4 · contre-test Firefox des cartes, des contrôles et du reflow mobile. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { firefox } = require('playwright');
const origin = process.env.TUG_HOME_URL || 'http://127.0.0.1:4180/';
const evidencePath = path.resolve(__dirname, '../../data/snapshots/validation-phase-4-firefox.json');
const ready = 'html[data-app-ready][data-maps-ready]';
const hub = 'pages/maps/';
const icebreaker = 'pages/maps/icebreaker.html';
const absolute = (ref) => new URL(ref, origin).href;
const checks = [];
async function group(name, fn) {
  await fn();
  checks.push(name);
  console.log(`OK · ${name}`);
}
async function fits(page, name) {
  const value = await page.evaluate(() => ({ page: document.documentElement.scrollWidth, viewport: innerWidth }));
  assert(value.page <= value.viewport + 1, `${name}: ${value.page}px > ${value.viewport}px`);
}
async function main() {
  const browser = await firefox.launch();
  try {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce', isMobile: true, hasTouch: true });
    page.setDefaultTimeout(12000);
    const errors = [];
    page.on('pageerror', (error) => errors.push(error.message));
    page.on('response', (response) => { if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`); });
    async function open(ref) {
      const response = await page.goto(absolute(ref));
      assert(response && (response.ok() || response.status() === 304), ref);
      await page.locator(ready).waitFor();
      await page.evaluate(() => document.fonts.ready);
    }
    await group('Hub mobile, 13 fiches et recherche accentuée', async () => {
      await open(hub);
      assert.equal(await page.locator('[data-map-card]').count(), 13);
      await page.locator('[data-map-query]').fill('icebreaker boreas');
      await page.waitForFunction(() => [...document.querySelectorAll('[data-map-card]')].filter((card) => !card.hidden).length === 1);
      assert.equal(await page.locator('[data-map-card]:not([hidden])').getAttribute('data-map-slug'), 'icebreaker');
      await page.locator('[data-map-reset]').click();
      assert.equal(await page.locator('[data-map-card]:not([hidden])').count(), 13);
    });
    await group('Filtre de lecture du terrain et synchronisation du mode', async () => {
      await page.locator('select[data-map-difficulty]').selectOption('proche');
      assert(await page.locator('[data-map-filter-status]').textContent().then((text) => text.includes('4 / 13')));
      await page.locator('[data-map-mode-select]').selectOption('pvp-season');
      assert(await page.locator('[data-map-filter-status]').textContent().then((text) => text.includes('PvP Seasonal')));
      await page.locator('[data-map-reset]').click();
    });
    await group('Comparateur mobile et limite de deux sélections', async () => {
      await page.locator('[data-map-compare][value="ground-zero"]').check();
      await page.locator('[data-map-compare][value="customs"]').check();
      await page.waitForFunction(() => document.querySelector('[data-map-compare-status]')?.textContent.includes('Comparaison prête'));
      assert.equal((await page.locator('[data-compare-cell="a-name"]').textContent()).trim(), 'Ground Zero');
      await page.locator('[data-map-compare][value="factory"]').click();
      assert.equal(await page.locator('[data-map-compare][value="factory"]').isChecked(), false);
      assert.match(await page.locator('[data-map-compare-status]').textContent(), /Deux cartes maximum/);
    });
    await group('Navigation du menu sur écran étroit et cibles de filtre utilisables', async () => {
      const toggle = page.locator('[data-nav-toggle]');
      await toggle.tap();
      assert.equal(await toggle.getAttribute('aria-expanded'), 'true');
      await page.keyboard.press('Escape');
      await page.locator('[data-map-query]').focus();
      assert.equal(await page.evaluate(() => document.activeElement.id), 'maps-query');
      await fits(page, 'hub mobile');
    });
    await group('Fiche Icebreaker : trois exports et sélection clavier', async () => {
      await open(icebreaker);
      assert.equal(await page.locator('[data-map-mode]').count(), 3);
      await page.locator('[data-map-mode="pve"]').focus();
      await page.keyboard.press('Enter');
      assert.equal(await page.locator('#map-mode-panel-pve').isVisible(), true);
      assert.equal(await page.locator('#map-mode-panel-regular').isVisible(), false);
      await page.locator('[data-map-mode="pvp-season"]').press('Space');
      assert.equal(await page.locator('[data-map-mode="pvp-season"]').getAttribute('aria-pressed'), 'true');
    });
    await group('Sources du changement BSG du 12/11 et mise en garde fumée', async () => {
      const text = await page.locator('main').textContent();
      for (const term of ['12/11', 'Battle Pass', 'Black Division', '100 %', 'sans numéro de patch', 'fumée', 'technique fiable', 'ne la considérez pas']) assert(text.includes(term), term);
      assert(await page.locator('#ref-balance-nov').count());
      assert(await page.locator('[id="ref-yt-icebreaker-smoke-1.3-nov12"]').count());
      assert(await page.locator('#sources').count());
    });
    await group('Reflow 320–1440 px : hub et fiche, sans débordement de page', async () => {
      for (const route of [hub, icebreaker]) {
        await open(route);
        for (const width of [320, 390, 576, 768, 832, 1024, 1440]) {
          await page.setViewportSize({ width, height: 960 });
          await fits(page, `${route} ${width}px`);
        }
      }
    });
    assert.deepEqual(errors, []);
    const report = {
      schemaVersion: 1, status: 'VALIDE', browser: `Firefox ${browser.version()}`,
      checkedAt: new Date().toISOString(), viewportCssPx: 390, checks, errors,
      method: 'Parcours local HTTP ; mode tactile mobile simulé ; filtres, comparaison, clavier, 320–1440 px ; console et réponses contrôlées.',
    };
    await fs.writeFile(evidencePath, JSON.stringify(report, null, 2) + '\n');
  } finally {
    await browser.close();
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
