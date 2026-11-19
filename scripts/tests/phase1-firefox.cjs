/* Contre-test ciblé de l'atelier sur Firefox ; Chromium exécute la suite complète. */
'use strict';
const assert = require('node:assert/strict');
const { firefox } = require('playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const target = process.env.TUG_LAB_URL || 'http://127.0.0.1:4173/lab/';

async function main() {
  const browser = await firefox.launch();
  const page = await browser.newPage({ viewport: { width: 390, height: 850 }, reducedMotion: 'reduce' });
  page.setDefaultTimeout(7000);
  const requests = [], errors = [];
  page.on('request', (r) => requests.push(r.url()));
  page.on('pageerror', (e) => errors.push(e.message));
  try {
    await page.goto(target);
    await page.waitForSelector(':root[data-app-ready=true]');
    await page.evaluate(() => document.fonts.ready);
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    assert(!requests.some((r) => r.endsWith('.mp3')));
    await page.locator('[data-site-search-trigger]').press('Enter');
    await page.locator('#site-query').fill('foret');
    await page.waitForFunction(() => document.querySelector('[data-search-results] a')?.hash === '#audio');
    await page.keyboard.press('Escape');
    await page.waitForFunction(() => document.activeElement?.hasAttribute('data-site-search-trigger'));
    await page.locator('#catalogue-family').selectOption('smg');
    assert.equal(await page.locator('[data-filter-row]:not([hidden])').count(), 2);
    await page.locator('[data-compare-toggle=mp5]').click();
    await page.locator('[data-compare-toggle=vityaz]').click();
    await page.locator('[data-compare-open]').press('Enter');
    await page.waitForFunction(() => document.activeElement?.id === 'compare-title');
    assert.equal(await page.locator('#compare-dialog thead th').count(), 3);
    await page.keyboard.press('Escape');
    await page.waitForFunction(() => document.activeElement?.hasAttribute('data-compare-open'));
    const playback = page.locator('[data-audio-deck] [data-audio-toggle]');
    await playback.click();
    await page.waitForFunction(() => document.querySelector('[data-audio-deck]').dataset.audioState === 'playing');
    assert(requests.some((r) => r.endsWith('ambient_rain.mp3')));
    await playback.click();
    await page.waitForFunction(() => document.querySelector('[data-audio-deck]').dataset.audioState === 'paused');
    assert.deepEqual(errors, []);
    const result = { schemaVersion: 1, status: 'VALIDE', browser: `Firefox ${browser.version()}`, checkedAt: new Date().toISOString(), viewportCssPx: 390,
      checks: ['reflow', 'recherche avec accents', 'Échap et restitution du focus', 'filtres', 'comparateur', 'audio opt-in et pause'] };
    await fs.writeFile(path.resolve(__dirname, '../../data/snapshots/validation-phase-1-firefox.json'), JSON.stringify(result, null, 2) + '\n');
    console.log(`OK · ${result.browser} · ${result.checks.length} points du parcours à 390 px`);
  } finally { await browser.close(); }
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
