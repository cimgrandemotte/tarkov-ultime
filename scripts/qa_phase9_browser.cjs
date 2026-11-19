#!/usr/bin/env node
/* QA navigateur PHASE_9 : 7 routes, Chromium/Firefox, axe, filtres, navigation, recherche, responsive et no-JS. */
const fs = require('node:fs');
const path = require('node:path');
const { chromium, firefox } = require('playwright');
const ROOT = path.resolve(__dirname, '..');
const BASE = (process.env.PHASE9_BASE_URL || 'http://127.0.0.1:4180').replace(/\/$/, '');
const OUT = path.join(ROOT, 'data/snapshots/validation-phase-9.json');
const axeSource = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const ROUTES = [
  'pages/spt-tushonka/', 'pages/spt-tushonka/installation.html', 'pages/spt-tushonka/mods.html',
  'pages/spt-tushonka/fika.html', 'pages/spt-tushonka/troubleshooting.html', 'pages/arena/', 'pages/events/',
];
const report = { schemaVersion: 1, phase: 'PHASE_9', status: 'EN_COURS', base: BASE, checkedAt: '2026-11-18',
  routes: [], checks: [], audits: [], responsive: [], noJs: [], errors: [] };
const errors = [];
let complete = false;
function persist() {
  report.errors = errors;
  report.status = errors.length ? 'ECHEC' : complete ? 'PASS' : 'EN_COURS';
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, `${JSON.stringify(report, null, 2)}\n`);
}
function record(name, passed, detail) {
  const row = { name, passed };
  if (detail !== undefined) row.detail = detail;
  report.checks.push(row);
  if (!passed) errors.push(`${name}${detail === undefined ? '' : `: ${typeof detail === 'string' ? detail : JSON.stringify(detail)}`}`);
  console.log(`${passed ? 'PASS' : 'FAIL'} · ${name}${detail === undefined ? '' : ` · ${typeof detail === 'string' ? detail : JSON.stringify(detail)}`}`);
  persist();
}
function assert(condition, message) { if (!condition) throw new Error(message); }
function url(route) { return `${BASE}/${route.replace(/^\//, '')}`; }
async function open(browser, route, options = {}) {
  const context = await browser.newContext({
    viewport: { width: options.width || 1440, height: options.height || 960 },
    reducedMotion: 'reduce', javaScriptEnabled: options.javaScriptEnabled !== false,
  });
  const page = await context.newPage();
  page.setDefaultTimeout(15000);
  const pageErrors = [];
  const failedRequests = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));
  page.on('console', (message) => {
    if (message.type() === 'error' && !message.text().toLowerCase().includes('favicon')) pageErrors.push(message.text());
  });
  page.on('requestfailed', (request) => {
    if (!request.url().toLowerCase().includes('favicon')) failedRequests.push(`${request.url()} ${request.failure()?.errorText || ''}`);
  });
  const response = await page.goto(url(route), { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(80);
  return { context, page, response, pageErrors, failedRequests };
}
async function inspectRoute(browser, engine, route, runAxe) {
  const { context, page, response, pageErrors, failedRequests } = await open(browser, route);
  const facts = await page.evaluate(() => {
    const hero = document.querySelector('.guide-hero__image');
    const ids = [...document.querySelectorAll('[id]')].map((node) => node.id);
    const duplicateIds = ids.filter((id, index) => ids.indexOf(id) !== index);
    let jsonLdValid = false;
    try { JSON.parse(document.querySelector('script[type="application/ld+json"]')?.textContent || ''); jsonLdValid = true; } catch {}
    return {
      title: document.title,
      h1: document.querySelector('h1')?.textContent?.trim() || '',
      h1Count: document.querySelectorAll('h1').length,
      description: document.querySelector('meta[name="description"]')?.content || '',
      language: document.documentElement.lang,
      heroLoaded: Boolean(hero?.complete && hero.naturalWidth > 0),
      heroAlt: hero?.getAttribute('alt') || '',
      missingAlt: [...document.images].filter((image) => !image.hasAttribute('alt')).map((image) => image.src),
      duplicateIds,
      jsonLdValid,
      robots: document.querySelector('meta[name="robots"]')?.content || '',
      canonical: document.querySelector('link[rel="canonical"]')?.href || '',
      phase9Css: [...document.styleSheets].some((sheet) => sheet.href?.includes('/css/pages/phase9.css')),
      phase9Script: [...document.scripts].some((script) => script.src?.includes('/js/phase9.js')),
      appReady: document.documentElement.dataset.appReady === 'true',
      searchSource: document.querySelector('[data-site-search]')?.dataset.searchSource || '',
      htmlChars: document.documentElement.outerHTML.length,
    };
  });
  const failures = [];
  if (!response || response.status() !== 200) failures.push(`HTTP ${response?.status() ?? 'no response'}`);
  if (!facts.h1 || !facts.title || !facts.description || facts.h1Count !== 1) failures.push('titre, description ou H1 absent/non unique');
  if (facts.language !== 'fr-FR') failures.push(`lang=${facts.language}`);
  if (!facts.heroLoaded || !facts.heroAlt) failures.push('hero absent, non chargé ou sans texte alternatif');
  if (facts.missingAlt.length) failures.push(`images sans alt: ${facts.missingAlt.join(', ')}`);
  if (facts.duplicateIds.length) failures.push(`IDs dupliqués: ${facts.duplicateIds.join(', ')}`);
  if (!facts.jsonLdValid) failures.push('JSON-LD absent ou invalide');
  if (!facts.phase9Css || !facts.phase9Script || !facts.appReady) failures.push('CSS, module PHASE_9 ou initialisation manquant');
  if (!facts.searchSource.endsWith('js/data/search-index.json')) failures.push(`source de recherche invalide: ${facts.searchSource}`);
  if (facts.canonical || facts.robots !== 'noindex,follow') failures.push(`SEO aperçu incorrect: canonical=${facts.canonical}, robots=${facts.robots}`);
  if (pageErrors.length) failures.push(`erreurs navigateur: ${pageErrors.slice(0, 5).join(' | ')}`);
  if (failedRequests.length) failures.push(`requêtes échouées: ${failedRequests.slice(0, 5).join(' | ')}`);
  let axe = { violations: [], review: [] };
  if (runAxe) {
    await page.addScriptTag({ content: axeSource });
    axe = await page.evaluate(async () => {
      const output = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'] } });
      return {
        violations: output.violations.map((violation) => ({ id: violation.id, impact: violation.impact, help: violation.help,
          targets: violation.nodes.slice(0, 16).map((node) => node.target) })),
        review: output.incomplete.filter((violation) => ['color-contrast', 'aria-prohibited-attr'].includes(violation.id))
          .map((violation) => ({ id: violation.id, targets: violation.nodes.slice(0, 16).map((node) => node.target) })),
      };
    });
    report.audits.push({ engine, route, ...axe });
    if (axe.violations.length) failures.push(`axe: ${axe.violations.map((item) => `${item.id} (${item.targets.length})`).join(', ')}`);
  }
  report.routes.push({ engine, route, http: response?.status(), title: facts.title, htmlChars: facts.htmlChars, heroLoaded: facts.heroLoaded });
  record(`${engine} · ${route} · rendu, médias et modules${runAxe ? ' + axe-core' : ''}`, failures.length === 0,
    failures.length ? failures : { appReady: facts.appReady, htmlChars: facts.htmlChars, axeViolations: axe.violations.length });
  await context.close();
}
async function check(name, fn) {
  try { record(name, true, await fn()); }
  catch (error) { record(name, false, error.stack || error.message); }
}
async function testBranchFilters(browser) {
  const spt = await open(browser, 'pages/spt-tushonka/');
  await check('SP-Tushonka · filtre Stable / BE / Fika', async () => {
    const page = spt.page;
    assert(await page.locator('[data-p9-branch-controls]').isVisible(), 'filtre de branche non activé');
    const select = page.locator('#p9-spt-branch');
    assert(await page.locator('[data-p9-branch-card]:visible').count() === 5, 'cinq liens/branches au départ attendus');
    await select.selectOption('stable');
    assert(await page.locator('[data-p9-branch-card]:visible').count() === 3, 'la stable doit afficher trois guides');
    assert((await page.locator('[data-p9-branch-count]').innerText()).includes('3 guides'), 'compteur Stable incorrect');
    await select.selectOption('fika');
    assert(await page.locator('[data-p9-branch-card]:visible').count() === 1, 'Fika doit afficher une seule fiche');
    await select.selectOption('be');
    assert(await page.locator('[data-p9-branch-card]:visible').count() === 1, 'BE doit afficher un seul avertissement');
    await select.selectOption('all');
    assert(await page.locator('[data-p9-branch-card]:visible').count() === 5, 'réinitialisation du filtre SPT incorrecte');
    return '5 → 3 stable / 1 Fika / 1 BE → 5; compteurs aria-live vérifiés';
  });
  await spt.context.close();

  const install = await open(browser, 'pages/spt-tushonka/installation.html');
  await check('Installation · filtre de parcours stable / expérimental', async () => {
    const page = install.page;
    const select = page.locator('#p9-install-branch');
    assert(await page.locator('[data-p9-branch-card]:visible').count() === 2, 'les deux branches doivent être visibles par défaut');
    await select.selectOption('stable');
    assert(await page.locator('[data-p9-branch-card]:visible').count() === 1, 'seul le parcours stable doit rester');
    assert((await page.locator('[data-p9-branch-count]').innerText()).includes('1 option'), 'compteur singulier incorrect');
    assert((await page.locator('[data-p9-branch-card]:visible').innerText()).includes('SPT 4.1.6'), 'parcours stable absent');
    await select.selectOption('be');
    assert(await page.locator('[data-p9-branch-card]:visible').count() === 1, 'seul le parcours BE doit rester');
    assert((await page.locator('[data-p9-branch-card]:visible').innerText()).includes('Bleeding Edge 5.0'), 'avertissement BE absent');
    await select.selectOption('all');
    assert(await page.locator('[data-p9-branch-card]:visible').count() === 2, 'retour aux deux parcours incorrect');
    return 'le filtre masque/affiche les sections entières et garde les ancres actives';
  });
  await install.context.close();
}
async function testModsAndTroubleshooting(browser) {
  const mods = await open(browser, 'pages/spt-tushonka/mods.html');
  await check('Mods · filtre branche et catégorie', async () => {
    const page = mods.page;
    assert(await page.locator('[data-p9-mod-card]:visible').count() === 4, 'quatre fiches initiales attendues');
    await page.locator('#p9-mod-branch').selectOption('be');
    assert(await page.locator('[data-p9-mod-card]:visible').count() === 1, 'branche BE doit avoir une seule fiche');
    await page.locator('#p9-mod-category').selectOption('ai');
    assert(await page.locator('[data-p9-mod-card]:visible').count() === 0, 'catégorie IA ne doit pas se présenter comme une compatibilité BE');
    await page.locator('#p9-mod-branch').selectOption('stable');
    await page.locator('#p9-mod-category').selectOption('content');
    assert(await page.locator('[data-p9-mod-card]:visible').count() === 1, 'le backport Icebreaker doit être filtrable');
    assert((await page.locator('[data-p9-mod-count]').innerText()).includes('1 fiche'), 'compteur de fiches incorrect');
    await page.locator('#p9-mod-branch').selectOption('all');
    await page.locator('#p9-mod-category').selectOption('all');
    assert(await page.locator('[data-p9-mod-card]:visible').count() === 4, 'réinitialisation des filtres mods incorrecte');
    return 'branche × catégorie, y compris résultat zéro et reset vérifiés';
  });
  await mods.context.close();

  const trouble = await open(browser, 'pages/spt-tushonka/troubleshooting.html');
  await check('Dépannage · filtre par symptôme', async () => {
    const page = trouble.page;
    assert(await page.locator('[data-p9-trouble-card]:visible').count() === 4, 'quatre pistes initiales attendues');
    await page.locator('#p9-trouble-filter').selectOption('linux');
    assert(await page.locator('[data-p9-trouble-card]:visible').count() === 1, 'Linux doit isoler une piste');
    assert((await page.locator('[data-p9-trouble-card]:visible').innerText()).includes('issue #24'), 'signalement Linux non affiché');
    await page.locator('#p9-trouble-filter').selectOption('all');
    assert(await page.locator('[data-p9-trouble-card]:visible').count() === 4, 'reset du dépannage incorrect');
    return '4 pistes → Linux/Proton isolé → 4 pistes';
  });
  await trouble.context.close();
}
async function testEventsAndArena(browser) {
  const events = await open(browser, 'pages/events/');
  await check('Événements · filtres actif / annoncé / archivé / durable', async () => {
    const page = events.page;
    assert(await page.locator('[data-p9-event-card]:visible').count() === 10, 'dix entrées initiales attendues');
    for (const [state, expected] of [['active', 3], ['announced', 1], ['archived', 5], ['durable', 1]]) {
      await page.locator(`[data-p9-event-filter="${state}"]`).click();
      const actual = await page.locator('[data-p9-event-card]:visible').count();
      assert(actual === expected, `${state}: ${expected} cartes attendues, ${actual} affichées`);
      assert((await page.locator('[data-p9-event-count]').innerText()).includes(`${expected} repère`), `compteur ${state} incorrect`);
    }
    await page.locator('[data-p9-event-filter="all"]').click();
    assert(await page.locator('[data-p9-event-card]:visible').count() === 10, 'reset de la chronologie incorrect');
    await page.locator('#events-filter').focus();
    return '10 → actif 3 / annoncé 1 / archivé 5 / durable 1 → 10; ancre du filtre présente';
  });
  await events.context.close();

  const arena = await open(browser, 'pages/arena/');
  await check('Arena · onglets accessibles et navigation clavier', async () => {
    const page = arena.page;
    const nav = page.locator('[data-tabs-nav]');
    assert(await nav.isVisible(), 'navigation d’onglets non révélée');
    assert(await page.locator('[role="tabpanel"]:visible').count() === 1, 'un panneau actif attendu');
    const teamTab = page.locator('#p9-arena-tab-team');
    await teamTab.click();
    assert((await page.locator('[role="tabpanel"]:visible').innerText()).includes('TeamFight'), 'TeamFight non sélectionné');
    await teamTab.focus();
    await teamTab.press('ArrowRight');
    assert(await page.locator('#p9-arena-tab-check').getAttribute('aria-selected') === 'true', 'flèche droite ne change pas d’onglet');
    assert((await page.locator('[role="tabpanel"]:visible').innerText()).includes('CheckPoint'), 'panneau clavier incorrect');
    return 'onglet CheckPoint activable par clic et flèche droite; un panneau visible';
  });
  await arena.context.close();
}
async function testSearchAndNavigation(browser) {
  const events = await open(browser, 'pages/events/');
  await check('Recherche globale · route PHASE_9 indexée', async () => {
    const trigger = events.page.locator('[data-site-search-trigger]');
    assert(await trigger.isVisible(), 'bouton recherche non activé');
    await trigger.click();
    const input = events.page.locator('[data-search-input]');
    await input.fill('City Drops');
    await events.page.waitForFunction(() => [...document.querySelectorAll('[data-search-results] a')]
      .some((link) => link.href.includes('/pages/events/')), { timeout: 20000 });
    const hrefs = await events.page.locator('[data-search-results] a').evaluateAll((links) => links.map((link) => link.getAttribute('href')));
    assert(hrefs.some((href) => href?.includes('/pages/events/')), `route événements absente des résultats: ${hrefs.join(', ')}`);
    return `index local chargé; requête « City Drops » renvoie la chronologie`;
  });
  await events.context.close();

  const home = await open(browser, '');
  await check('Accueil · liens directs Arena/Événements et méga-menu communautaire', async () => {
    const page = home.page;
    const arena = page.locator('.site-nav > a.site-nav__link[href="./pages/arena/"]');
    const news = page.locator('.site-nav > a.site-nav__link[href="./pages/events/"]');
    assert(await arena.count() === 1 && await news.count() === 1, 'liens directs Arena/Événements absents');
    await page.locator('.home-mega > summary').click();
    const menuLinks = await page.locator('.home-mega__panel a').evaluateAll((nodes) => nodes.map((node) => node.getAttribute('href')));
    assert(menuLinks.includes('./pages/spt-tushonka/'), 'SP-Tushonka absent du méga-menu accueil');
    assert(menuLinks.includes('./pages/arena/'), 'Arena absent du méga-menu accueil');
    assert(menuLinks.includes('./pages/events/'), 'Événements absents du méga-menu accueil');
    return `${menuLinks.length} liens menu; SP-Tushonka, Arena et Événements présents`;
  });
  await home.context.close();

  const phase8 = await open(browser, 'pages/skills/');
  await check('PHASE_8 · méga-menu vers les nouvelles routes', async () => {
    await phase8.page.locator('.home-mega > summary').click();
    const hrefs = await phase8.page.locator('.home-mega__panel a').evaluateAll((nodes) => nodes.map((node) => node.getAttribute('href')));
    for (const route of ['pages/spt-tushonka/', 'pages/arena/', 'pages/events/']) {
      assert(hrefs.some((href) => href?.includes(route)), `lien PHASE_9 absent du menu PHASE_8: ${route}`);
    }
    return `liens relatifs depuis PHASE_8 présents pour ${hrefs.filter((href) => href?.includes('pages/')).length} entrées`;
  });
  await phase8.context.close();
}
async function testNoJs(browser, route) {
  const { context, page, response } = await open(browser, route, { javaScriptEnabled: false, width: 1280 });
  const data = await page.evaluate(() => ({
    title: document.title,
    h1: document.querySelector('h1')?.textContent?.trim(),
    mainVisible: Boolean(document.querySelector('#main')?.getClientRects().length),
    navVisible: Boolean(document.querySelector('[data-site-nav]')?.getClientRects().length),
    contentVisible: [...document.querySelectorAll('.phase9-section')].filter((el) => el.getClientRects().length).length,
    eventCards: document.querySelectorAll('.phase9-event-card').length,
    tabPanels: document.querySelectorAll('.phase9-tabs__panel').length,
    phaseSections: [...document.querySelectorAll('.phase9-section')].filter((el) => el.getClientRects().length).length,
  }));
  const failures = [];
  if (!response || response.status() !== 200) failures.push(`HTTP ${response?.status()}`);
  if (!data.title || !data.h1 || !data.mainVisible || !data.navVisible) failures.push('structure principale/navigation statique absente');
  if (route.includes('events/') && data.eventCards !== 10) failures.push(`10 événements statiques attendus, obtenu ${data.eventCards}`);
  if (route.includes('arena/') && data.tabPanels !== 4) failures.push(`4 descriptions sans JS attendues, obtenu ${data.tabPanels}`);
  if (route.includes('spt-tushonka/') && data.phaseSections === 0) failures.push('aucune section SPT visible sans JS');
  report.noJs.push({ route, ...data });
  record(`Sans JavaScript · ${route} · contenu et navigation statiques`, failures.length === 0, failures.length ? failures : data);
  await context.close();
}
async function testResponsive(browser, route) {
  const { context, page, response } = await open(browser, route, { width: 375, height: 812 });
  const sizes = [];
  for (const viewport of [{ width: 375, height: 812 }, { width: 768, height: 1024 }, { width: 1440, height: 900 }]) {
    await page.setViewportSize(viewport);
    await page.waitForTimeout(40);
    const result = await page.evaluate(() => ({ width: innerWidth, client: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth }));
    sizes.push(result);
  }
  const failures = [];
  if (!response || response.status() !== 200) failures.push(`HTTP ${response?.status()}`);
  for (const size of sizes) if (size.scroll > size.client + 1) failures.push(`${size.width}px overflow: ${size.scroll} > ${size.client}`);
  report.responsive.push({ route, sizes });
  record(`Responsive · ${route} · 375/768/1440 px`, failures.length === 0, failures.length ? failures : sizes);
  await context.close();
}
async function testMobileNavigation(browser) {
  const { context, page } = await open(browser, 'pages/spt-tushonka/', { width: 375, height: 812 });
  await check('Mobile · navigation compacte ouvrable au clavier', async () => {
    const toggle = page.locator('[data-nav-toggle]');
    assert(await toggle.isVisible(), 'bouton menu mobile invisible');
    assert(await toggle.getAttribute('aria-expanded') === 'true', 'la navigation mobile doit préserver son état initial sans saut');
    const nav = page.locator('#global-nav');
    await toggle.click();
    assert(await toggle.getAttribute('aria-expanded') === 'false', 'le bouton ne replie pas la navigation');
    await toggle.click();
    assert(await toggle.getAttribute('aria-expanded') === 'true', 'le bouton ne rouvre pas la navigation');
    assert((await nav.innerText()).includes('Événements'), 'lien événements absent en mobile');
    await toggle.press('Escape').catch(() => {});
    return 'état initial conservé, repli/dépli, liens PHASE_9 et aria-expanded testés';
  });
  await context.close();
}
async function run() {
  let chromiumBrowser;
  let firefoxBrowser;
  try {
    chromiumBrowser = await chromium.launch({ headless: true });
    firefoxBrowser = await firefox.launch({ headless: true });
    for (const route of ROUTES) {
      await inspectRoute(chromiumBrowser, 'Chromium', route, true);
      await inspectRoute(firefoxBrowser, 'Firefox', route, false);
      await testResponsive(chromiumBrowser, route);
      await testNoJs(chromiumBrowser, route);
    }
    await testResponsive(chromiumBrowser, '/');
    await testBranchFilters(chromiumBrowser);
    await testModsAndTroubleshooting(chromiumBrowser);
    await testEventsAndArena(chromiumBrowser);
    await testSearchAndNavigation(chromiumBrowser);
    await testMobileNavigation(chromiumBrowser);
    complete = true;
    persist();
    console.log(`\nPHASE_9 browser QA ${report.status} · ${report.checks.filter((row) => row.passed).length}/${report.checks.length} contrôles · ${report.audits.length} audits axe-core`);
    if (errors.length) process.exitCode = 1;
  } catch (error) {
    errors.push(`Fatal: ${error.stack || error.message}`);
    record('Arrêt contrôlé de la QA', false, error.stack || error.message);
    process.exitCode = 1;
  } finally {
    if (chromiumBrowser) await chromiumBrowser.close();
    if (firefoxBrowser) await firefoxBrowser.close();
    persist();
  }
}
run();
