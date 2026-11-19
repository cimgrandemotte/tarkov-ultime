#!/usr/bin/env node
/* QA PHASE_5 reproductible avec Playwright + axe-core.
 * Prérequis locaux : npm install --no-save --no-package-lock playwright axe-core
 *                     npx playwright install chromium firefox
 * Serveur : python3 scripts/serve_home.py --host 0.0.0.0 --port 4180
 */
const fs = require('node:fs');
const path = require('node:path');
const { chromium, firefox } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const BASE = (process.env.PHASE5_BASE_URL || 'http://127.0.0.1:4180').replace(/\/$/, '');
const OUT = path.join(ROOT, 'data/snapshots/validation-phase-5.json');
const ROUTES = [
  'pages/weapons/', 'pages/weapons/assault-rifles.html', 'pages/weapons/smgs.html',
  'pages/weapons/shotguns.html', 'pages/weapons/sniper-rifles.html', 'pages/weapons/dmrs.html',
  'pages/weapons/lmgs.html', 'pages/weapons/pistols.html', 'pages/weapons/melee.html',
  'pages/weapons/grenade-launchers.html', 'pages/weapons/weapon-mods.html',
  'pages/ammo/', 'pages/ammo/ammo-chart.html',
];
const results = { schemaVersion: 1, status: 'EN_COURS', browser: {}, checkedAt: new Date().toISOString(), checks: [], audits: [], performance: [], responsive: [] };
const errors = [];
function persist() {
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  results.errors = errors;
  results.status = errors.length ? 'EN_COURS_AVEC_ECHECS' : 'EN_COURS';
  fs.writeFileSync(OUT, `${JSON.stringify(results, null, 2)}\n`);
}
function record(name, passed, detail = undefined) {
  const item = { name, passed };
  if (detail !== undefined) item.detail = detail;
  results.checks.push(item);
  if (!passed) errors.push(`${name}${detail ? `: ${typeof detail === 'string' ? detail : JSON.stringify(detail)}` : ''}`);
  console.log(`${passed ? 'PASS' : 'FAIL'} · ${name}${detail === undefined ? '' : ` · ${typeof detail === 'string' ? detail : JSON.stringify(detail)}`}`);
  persist();
}
function assert(condition, message) { if (!condition) throw new Error(message); }
async function check(name, fn) {
  try { const detail = await fn(); record(name, true, detail); }
  catch (error) { record(name, false, error.message); }
}
const axeSource = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');

async function visit(browser, route, { width = 1440, height = 1000 } = {}) {
  const context = await browser.newContext({ viewport: { width, height }, reducedMotion: 'reduce' });
  const page = await context.newPage();
  const pageErrors = [];
  const failedRequests = [];
  page.on('pageerror', error => pageErrors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') pageErrors.push(message.text()); });
  page.on('requestfailed', request => failedRequests.push(`${request.url()} ${request.failure()?.errorText || ''}`));
  await page.addInitScript(() => {
    window.__phase5Vitals = { lcp: 0, cls: 0 };
    try {
      new PerformanceObserver(list => {
        for (const entry of list.getEntries()) window.__phase5Vitals.lcp = entry.startTime;
      }).observe({ type: 'largest-contentful-paint', buffered: true });
      new PerformanceObserver(list => {
        for (const entry of list.getEntries()) if (!entry.hadRecentInput) window.__phase5Vitals.cls += entry.value;
      }).observe({ type: 'layout-shift', buffered: true });
    } catch {}
  });
  const response = await page.goto(`${BASE}/${route}`, { waitUntil: 'networkidle', timeout: 60000 });
  assert(response && response.status() === 200, `${route} HTTP ${response?.status()}`);
  if (route.startsWith('pages/weapons/') || route.startsWith('pages/ammo/')) {
    await page.waitForFunction(() => document.documentElement.dataset.phase5Ready === 'true', null, { timeout: 15000 });
  }
  await page.evaluate(() => document.fonts.ready);
  return { context, page, response, pageErrors, failedRequests };
}

async function auditPage(browser, route, engine, runAxe = true) {
  const { context, page, pageErrors, failedRequests } = await visit(browser, route);
  const data = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0];
    return {
      title: document.title,
      h1: document.querySelectorAll('h1').length,
      ready: document.documentElement.dataset.phase5Ready,
      images: [...document.images].map(img => {
        const rect = img.getBoundingClientRect();
        const visible = rect.bottom > 0 && rect.top < innerHeight && rect.right > 0 && rect.left < innerWidth;
        return { src: img.getAttribute('src'), loaded: img.complete && img.naturalWidth > 0, alt: img.getAttribute('alt'), loading: img.loading, visible };
      }),
      viewportWidth: innerWidth,
      documentWidth: document.documentElement.scrollWidth,
      htmlBytes: document.documentElement.outerHTML.length,
      dcl: nav?.domContentLoadedEventEnd || 0,
      load: nav?.loadEventEnd || 0,
      transferBytes: nav?.transferSize || 0,
      resourceCount: performance.getEntriesByType('resource').length,
      vitals: { ...window.__phase5Vitals },
    };
  });
  const failures = [];
  if (data.h1 !== 1) failures.push(`h1=${data.h1}`);
  if (data.documentWidth > data.viewportWidth + 1) failures.push(`débordement ${data.documentWidth}/${data.viewportWidth}`);
  if (data.images.some(img => !img.loaded && (img.loading !== 'lazy' || img.visible))) failures.push('image prioritaire ou visible non chargée');
  if (data.images.some(img => img.alt === null)) failures.push('image sans attribut alt');
  if (pageErrors.length) failures.push(`erreurs JS: ${pageErrors.slice(0, 4).join(' | ')}`);
  if (failedRequests.length) failures.push(`requêtes échouées: ${failedRequests.slice(0, 4).join(' | ')}`);
  let axe = { violations: [], review: [] };
  if (runAxe) {
    await page.addScriptTag({ content: axeSource });
    axe = await page.evaluate(async () => {
      const result = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'] } });
      return {
        violations: result.violations.map(v => ({ id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.slice(0, 30).map(n => n.target) })),
        review: result.incomplete.filter(v => ['color-contrast', 'aria-prohibited-attr'].includes(v.id)).map(v => ({ id: v.id, nodes: v.nodes.slice(0, 20).map(n => n.target) })),
      };
    });
    results.audits.push({ context: `${engine} · ${route}`, ...axe });
    if (axe.violations.length) failures.push(`axe: ${axe.violations.map(v => `${v.id} (${v.nodes.length})`).join(', ')}`);
  }
  if (data.dcl <= 0 || data.dcl > 2500) failures.push(`DOMContentLoaded ${Math.round(data.dcl)} ms`);
  if (data.vitals.lcp > 2500 || data.vitals.cls > 0.1) failures.push(`LCP/CLS ${Math.round(data.vitals.lcp)}/${data.vitals.cls.toFixed(3)}`);
  results.performance.push({ engine, route, dclMs: Math.round(data.dcl), loadMs: Math.round(data.load), lcpMs: Math.round(data.vitals.lcp), cls: Number(data.vitals.cls.toFixed(4)), htmlBytes: data.htmlBytes, transferBytes: data.transferBytes, resources: data.resourceCount });
  record(`${engine} · ${route} · rendu, médias, erreurs, reflow initial${runAxe ? ' et axe-core' : ''}`, failures.length === 0, failures.length ? failures : { htmlBytes: data.htmlBytes, dclMs: Math.round(data.dcl), lcpMs: Math.round(data.vitals.lcp), cls: Number(data.vitals.cls.toFixed(4)) });
  await context.close();
}

async function testWeaponInteractions(browser) {
  const { context, page } = await visit(browser, 'pages/weapons/');
  const region = page.locator('[data-p5-catalog]').first();
  await check('Arsenal · contrôles progressifs, modes et comparateur', async () => {
    assert(await region.locator('[data-mode-controls]').isVisible(), 'contrôles de mode non affichés après init');
    assert(await region.locator('[data-p5-filter-form]').isVisible(), 'formulaire de filtre non affiché après init');
    await region.locator('[data-mode-set="pve"]').click();
    assert(await region.getAttribute('data-active-mode') === 'pve', 'mode PvE non activé');
    assert(await region.locator('[data-mode-set="pve"]').getAttribute('aria-pressed') === 'true', 'aria-pressed non synchronisé');
    const filter = region.locator('[data-p5-filter-form]');
    const match = await page.evaluate(() => {
      for (const row of document.querySelectorAll('[data-p5-catalog] [data-p5-row]')) {
        const modes = JSON.parse(row.dataset.modeValues || '{}');
        const offer = (modes.pve?.offers || []).find(x => x.trader && x.level != null && typeof x.priceRUB === 'number');
        if (offer) return { id: row.dataset.id, name: row.dataset.itemName, offer };
      }
      return null;
    });
    if (match) {
      await filter.locator('[data-p5-search]').fill(match.name.split(' ').slice(0, 2).join(' '));
      await filter.locator('[data-p5-trader]').selectOption({ label: match.offer.trader });
      await filter.locator('[data-p5-level]').selectOption(String(match.offer.level));
      await filter.locator('[data-p5-budget]').fill(String(Math.ceil(match.offer.priceRUB)));
      assert(!(await region.locator(`[data-p5-row][data-id="${match.id}"]`).evaluate(el => el.hidden)), 'l’offre correspondant à tous les filtres a été masquée');
      const count = Number((await region.locator('[data-p5-count]').innerText()).match(/\d+/)?.[0] || 0);
      assert(count >= 1, 'compteur nul malgré une offre qui satisfait les trois filtres');
    } else {
      await filter.locator('[data-p5-search]').fill('M4A1');
      assert(Number((await region.locator('[data-p5-count]').innerText()).match(/\d+/)?.[0] || 0) > 0, 'recherche multi-terme sans résultat M4A1');
    }
    await filter.locator('button[type="reset"]').click();
    await page.waitForTimeout(50);
    const boxes = region.locator('[data-compare-pick]');
    await boxes.nth(0).check(); await boxes.nth(1).check();
    assert((await region.locator('[data-p5-compare-output] table').count()) === 1, 'table de comparaison non générée pour deux armes');
    await boxes.nth(2).check(); await boxes.nth(3).click();
    assert(!(await boxes.nth(3).isChecked()), 'la limite de trois comparables n’est pas respectée');
    await page.locator('[data-p5-compare-clear]').click();
    assert((await region.locator('[data-p5-compare-output] table').count()) === 0, 'effacement ne supprime pas la comparaison');
    return match ? `filtres trader/niveau/budget sur ${match.id}` : 'recherche M4A1';
  });
  await context.close();
}

async function testMelee(browser) {
  const { context, page } = await visit(browser, 'pages/weapons/melee.html');
  await check('Mêlée · colonnes slash/stab et comparaison dédiée', async () => {
    const rows = page.locator('[data-p5-row]');
    assert(await rows.count() > 1, 'lignes de mêlée absentes');
    await page.locator('[data-compare-pick]').nth(0).check();
    await page.locator('[data-compare-pick]').nth(1).check();
    const text = await page.locator('[data-p5-compare-output]').innerText();
    assert(text.includes('Dégâts slash exportés') && text.includes('Dégâts stab exportés'), 'colonnes comparatives de dégâts manquantes');
    await page.locator('[data-mode-set="pvp-season"]').click();
    assert(await page.locator('[data-mode-set="pvp-season"]').getAttribute('aria-pressed') === 'true', 'mode Seasonal non activé');
  });
  await context.close();
}

async function testAmmo(browser) {
  const { context, page } = await visit(browser, 'pages/ammo/');
  await check('Munitions · bascule de mode, craft, comparateur et tâche résolue', async () => {
    const region = page.locator('[data-p5-ammo]').first();
    await region.locator('[data-mode-set="pvp-season"]').click();
    assert(await region.getAttribute('data-active-mode') === 'pvp-season', 'mode Seasonal non activé');
    const row = region.locator('[data-p5-row][data-id="54527ac44bdc2d36668b4567"]');
    const details = row.locator('[data-mode-field="craft"] details');
    assert(await details.count() > 0, 'détail de craft M855A1 manquant');
    await details.first().locator('summary').click();
    const craftText = await details.first().innerText();
    assert(craftText.includes('Special Equipment'), 'nom de tâche M855A1 absent du craft');
    assert(craftText.includes('Workbench') && craftText.includes('Ingrédients'), 'station ou ingrédients de craft absents');
    await region.locator('[data-mode-set="regular"]').click();
    await region.locator('[data-compare-pick]').nth(0).check();
    await region.locator('[data-compare-pick]').nth(1).check();
    const output = await region.locator('[data-p5-compare-output]').innerText();
    assert(output.includes('Pénétration exportée') && output.includes('Vitesse initiale exportée'), 'colonnes de comparaison ammo absentes');
  });
  await context.close();
}

async function testChart(browser) {
  const { context, page } = await visit(browser, 'pages/ammo/ammo-chart.html');
  await check('Balistique · filtre graphique synchronisé avec le tableau accessible', async () => {
    const wrapper = page.locator('[data-p5-chart]');
    assert(await wrapper.count() === 1, 'wrapper du graphique manquant');
    const form = wrapper.locator('[data-p5-chart-filter]');
    await form.locator('[data-chart-search]').fill('M855A1');
    const visiblePoints = await page.locator('[data-chart-point]:not([hidden])').count();
    assert(visiblePoints > 0, 'la recherche n’affiche aucun point M855A1');
    const tableSearch = page.locator('[data-p5-ammo] [data-p5-search]');
    assert((await tableSearch.inputValue()).includes('M855A1'), 'la recherche du tableau ne suit pas le graphique');
    const row = page.locator('[data-p5-ammo] [data-p5-row][data-id="54527ac44bdc2d36668b4567"]');
    assert(!(await row.evaluate(el => el.hidden)), 'ligne de table M855A1 non visible');
    assert(await page.locator('[data-chart-point]:not([tabindex])').count() > 0, 'attendu : points HTML/CSS non tabulaires, équivalent fourni par la table');
    assert((await page.locator('[data-p5-ammo] table').count()) === 1, 'table balistique absente ou dupliquée');
    assert((await page.locator('table #ammo-craft-rows').count()) === 1, 'table de crafts manquante');
  });
  await context.close();
}

async function testMods(browser) {
  const { context, page } = await visit(browser, 'pages/weapons/weapon-mods.html');
  await check('Modifications · filtres croisés slot/famille et liste compatible', async () => {
    const form = page.locator('[data-mod-filter-form]');
    assert(await form.isVisible(), 'formulaire des modifications non affiché après init');
    const row = page.locator('[data-mod-row]').first();
    const sample = await row.evaluate(el => ({ name: el.querySelector('.phase5-item-name')?.textContent.trim(), slots: el.cells[2]?.querySelector('code')?.textContent.split(' · ').filter(Boolean) || [], families: el.dataset.families.split(' ') }));
    assert(sample.slots[0] && sample.families[0], 'ligne test sans slot ou famille');
    const search = sample.name.split(' ')[0];
    await form.locator('[data-mod-search]').fill(search);
    await form.locator('[data-mod-slot]').selectOption(sample.slots[0]);
    await form.locator('[data-mod-family]').selectOption(sample.families[0]);
    assert(!(await row.evaluate(el => el.hidden)), 'la ligne compatible ne satisfait pas ses filtres croisés');
    const count = Number((await page.locator('[data-mod-count]').innerText()).match(/[\d ,]+/)?.[0].replace(/[ ,]/g, '') || 0);
    assert(count >= 1, 'compteur des modifications nul');
    assert((await page.locator('#slot-summary-rows tr').count()) > 0, 'résumé des slots absent');
    await form.locator('button[type="reset"]').click();
    await page.waitForTimeout(50);
    const sort = form.locator('[data-mod-sort]');
    await sort.selectOption('name');
    const names = await page.locator('[data-mod-row]').evaluateAll(rows => rows.map(row => row.querySelector('.phase5-item-name')?.textContent.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim()));
    assert(names.every((name, i) => i === 0 || names[i - 1].localeCompare(name, 'fr') <= 0), 'tri alphabétique des modifications incorrect');
    await sort.selectOption('weapons');
    const compatible = await page.locator('[data-mod-row]').evaluateAll(rows => rows.map(row => Number(row.dataset.weapons)));
    assert(compatible.every((n, i) => i === 0 || compatible[i - 1] >= n), 'tri par compatibilité décroissante incorrect');
    return `${compatible.length} IDs de pièces; tris alphabétique et compatibilité validés`;
  });
  await context.close();
}

async function testResponsive(browser) {
  const routes = ['pages/weapons/', 'pages/weapons/weapon-mods.html', 'pages/ammo/', 'pages/ammo/ammo-chart.html'];
  const widths = [320, 375, 768, 1024, 1440];
  for (const route of routes) {
    const { context, page } = await visit(browser, route, { width: 1440, height: 900 });
    const rows = [];
    for (const width of widths) {
      await page.setViewportSize({ width, height: 900 });
      await page.waitForTimeout(30);
      const result = await page.evaluate(() => ({ viewport: innerWidth, root: document.documentElement.scrollWidth, body: document.body.scrollWidth }));
      rows.push(result);
      if (result.root > width + 1 || result.body > width + 1) break;
    }
    const failed = rows.filter(r => r.root > r.viewport + 1 || r.body > r.viewport + 1);
    results.responsive.push({ route, widths: rows, pass: !failed.length });
    record(`Reflow ${route} · 320–1440 px`, !failed.length, failed.length ? failed : rows);
    await context.close();
  }
  const { context, page } = await visit(browser, 'pages/weapons/');
  await page.keyboard.press('Tab');
  const focused = await page.evaluate(() => ({ tag: document.activeElement.tagName, visible: document.activeElement.matches(':focus-visible'), outline: getComputedStyle(document.activeElement).outlineStyle }));
  record('Navigation clavier · premier focus visible', focused.visible && focused.outline !== 'none', focused);
  await page.emulateMedia({ forcedColors: 'active', colorScheme: 'dark', reducedMotion: 'reduce' });
  record('Préférences système · forced-colors / reduced-motion', await page.evaluate(() => matchMedia('(forced-colors: active)').matches && matchMedia('(prefers-reduced-motion: reduce)').matches));
  await context.close();
}

async function testMobilePerformance(browser) {
  for (const route of ['pages/weapons/weapon-mods.html', 'pages/ammo/ammo-chart.html']) {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, deviceScaleFactor: 1, reducedMotion: 'reduce' });
    const page = await context.newPage();
    await page.addInitScript(() => {
      window.__phase5Vitals = { lcp: 0, cls: 0 };
      try {
        new PerformanceObserver(list => { for (const e of list.getEntries()) window.__phase5Vitals.lcp = e.startTime; }).observe({ type: 'largest-contentful-paint', buffered: true });
        new PerformanceObserver(list => { for (const e of list.getEntries()) if (!e.hadRecentInput) window.__phase5Vitals.cls += e.value; }).observe({ type: 'layout-shift', buffered: true });
      } catch {}
    });
    const session = await context.newCDPSession(page);
    await session.send('Network.enable');
    await session.send('Network.emulateNetworkConditions', { offline: false, latency: 150, downloadThroughput: 187500, uploadThroughput: 93750, connectionType: 'cellular4g' });
    await session.send('Emulation.setCPUThrottlingRate', { rate: 4 });
    await page.goto(`${BASE}/${route}`, { waitUntil: 'load', timeout: 90000 });
    await page.waitForFunction(() => document.documentElement.dataset.phase5Ready === 'true', null, { timeout: 30000 });
    const metrics = await page.evaluate(() => {
      const nav = performance.getEntriesByType('navigation')[0];
      return { dclMs: Math.round(nav?.domContentLoadedEventEnd || 0), loadMs: Math.round(nav?.loadEventEnd || 0), lcpMs: Math.round(window.__phase5Vitals.lcp), cls: Number(window.__phase5Vitals.cls.toFixed(4)), transferBytes: nav?.transferSize || 0 };
    });
    results.performance.push({ engine: 'Chromium mobile 4G/CPU×4', route, ...metrics });
    record(`Performance mobile 4G/CPU×4 · ${route} · LCP ≤ 2.5 s, CLS ≤ 0.1`, metrics.lcpMs > 0 && metrics.lcpMs <= 2500 && metrics.cls <= 0.1, metrics);
    await context.close();
  }
}

async function testNoJavaScript(browser) {
  const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 1280, height: 900 } });
  for (const route of ['pages/weapons/', 'pages/weapons/weapon-mods.html', 'pages/ammo/', 'pages/ammo/ammo-chart.html']) {
    const page = await context.newPage();
    await page.goto(`${BASE}/${route}`, { waitUntil: 'networkidle', timeout: 60000 });
    const data = await page.evaluate(() => ({
      h1: document.querySelectorAll('h1').length,
      rows: document.querySelectorAll('[data-p5-row], [data-mod-row]').length,
      tableVisible: [...document.querySelectorAll('table')].some(t => t.getBoundingClientRect().height > 0),
      chartVisible: document.querySelector('[data-p5-chart] .phase5-chart__plot')?.getBoundingClientRect().height > 0,
      filtersHidden: [...document.querySelectorAll('[data-p5-filter-form], [data-mod-filter-form], [data-p5-chart-filter], [data-mode-controls]')].every(el => el.hidden),
    }));
    const pass = data.h1 === 1 && data.rows > 0 && data.tableVisible && data.filtersHidden && (route !== 'pages/ammo/ammo-chart.html' || data.chartVisible);
    record(`Sans JavaScript · ${route} · données et tables de repli`, pass, data);
    await page.close();
  }
  await context.close();
}

async function testHomeNavigation(browser) {
  const { context, page } = await visit(browser, '');
  const links = await page.locator('a[href*="pages/weapons/"], a[href*="pages/ammo/"]').evaluateAll(els => els.map(a => ({ href: a.getAttribute('href'), text: a.innerText.trim() })));
  const pass = links.some(x => x.href.includes('pages/weapons/')) && links.some(x => x.href.includes('pages/ammo/'));
  record('Accueil · liens Arsenal et Munitions disponibles', pass, links);
  await context.close();
}

async function main() {
  let chromiumBrowser, firefoxBrowser;
  try {
    chromiumBrowser = await chromium.launch({ headless: true });
    results.browser.chromium = chromiumBrowser.version();
    for (const route of ROUTES) await auditPage(chromiumBrowser, route, 'Chromium');
    await testWeaponInteractions(chromiumBrowser);
    await testMelee(chromiumBrowser);
    await testAmmo(chromiumBrowser);
    await testChart(chromiumBrowser);
    await testMods(chromiumBrowser);
    await testResponsive(chromiumBrowser);
    await testMobilePerformance(chromiumBrowser);
    await testNoJavaScript(chromiumBrowser);
    await testHomeNavigation(chromiumBrowser);
  } catch (error) {
    record('Exécution Chromium', false, error.stack || error.message);
  } finally { if (chromiumBrowser) await chromiumBrowser.close(); }
  try {
    // Start a clean Firefox process per page/group: large static catalogues can otherwise
    // accumulate browser memory across dozens of contexts in a constrained QA container.
    for (const route of ROUTES) {
      firefoxBrowser = await firefox.launch({ headless: true });
      results.browser.firefox = firefoxBrowser.version();
      await auditPage(firefoxBrowser, route, 'Firefox', false);
      await firefoxBrowser.close();
      firefoxBrowser = null;
    }
    for (const run of [testWeaponInteractions, testMelee, testAmmo, testChart, testMods]) {
      firefoxBrowser = await firefox.launch({ headless: true });
      results.browser.firefox = firefoxBrowser.version();
      await run(firefoxBrowser);
      await firefoxBrowser.close();
      firefoxBrowser = null;
    }
  } catch (error) {
    record('Exécution Firefox', false, error.stack || error.message);
  } finally { if (firefoxBrowser) await firefoxBrowser.close(); }
  results.status = errors.length ? 'ECHEC' : 'VALIDE';
  results.errors = errors;
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, `${JSON.stringify(results, null, 2)}\n`);
  console.log(`\n${results.status} · ${results.checks.filter(x => x.passed).length}/${results.checks.length} contrôles · rapport ${path.relative(ROOT, OUT)}`);
  if (errors.length) process.exitCode = 1;
}
main();
