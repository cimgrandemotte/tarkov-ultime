#!/usr/bin/env node
/* QA PHASE_7 : 16 routes, Chromium/Firefox, axe-core, interactions, no-JS et responsive. */
const fs = require('node:fs');
const path = require('node:path');
const { chromium, firefox } = require('playwright');
const ROOT = path.resolve(__dirname, '..');
const BASE = (process.env.PHASE7_BASE_URL || 'http://127.0.0.1:4180').replace(/\/$/, '');
const OUT = path.join(ROOT, 'data/snapshots/validation-phase-7.json');
const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'js/data/phase7.json'), 'utf8'));
const axeSource = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const ROUTES = [
  'pages/traders/', 'pages/traders/prapor.html', 'pages/traders/therapist.html',
  'pages/traders/skier.html', 'pages/traders/peacekeeper.html', 'pages/traders/mechanic.html',
  'pages/traders/ragman.html', 'pages/traders/jaeger.html', 'pages/traders/fence.html',
  'pages/traders/lightkeeper.html', 'pages/traders/ref.html', 'pages/quests/',
  'pages/quests/quest-tree.html', 'pages/quests/kappa-guide.html', 'pages/hideout/',
  'pages/hideout/crafting.html',
];
const result = { schemaVersion: 1, status: 'EN_COURS', base: BASE, checkedAt: new Date().toISOString(), routes: [], checks: [], audits: [], responsive: [], browser: {}, errors: [] };
const errors = [];
let completed = false;

function persist() {
  result.errors = errors;
  result.status = errors.length ? 'ECHEC' : completed ? 'PASS' : 'EN_COURS';
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, `${JSON.stringify(result, null, 2)}\n`);
}
function record(name, passed, detail = undefined) {
  const row = { name, passed };
  if (detail !== undefined) row.detail = detail;
  result.checks.push(row);
  if (!passed) errors.push(`${name}${detail === undefined ? '' : `: ${typeof detail === 'string' ? detail : JSON.stringify(detail)}`}`);
  console.log(`${passed ? 'PASS' : 'FAIL'} · ${name}${detail === undefined ? '' : ` · ${typeof detail === 'string' ? detail : JSON.stringify(detail)}`}`);
  persist();
}
async function check(name, fn) {
  try { record(name, true, await fn()); }
  catch (error) { record(name, false, error.stack || error.message); }
}
function assert(condition, message) { if (!condition) throw new Error(message); }
function routeUrl(route) { return `${BASE}/${route.replace(/^\//, '')}`; }
async function open(browser, route, options = {}) {
  const context = await browser.newContext({
    viewport: { width: options.width || 1440, height: options.height || 1000 },
    reducedMotion: 'reduce', javaScriptEnabled: options.javaScriptEnabled !== false,
  });
  const page = await context.newPage();
  const pageErrors = [];
  const failedRequests = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));
  page.on('console', (message) => {
    if (message.type() === 'error' && !message.text().includes('favicon')) pageErrors.push(message.text());
  });
  page.on('requestfailed', (request) => failedRequests.push(`${request.url()} ${request.failure()?.errorText || ''}`));
  const response = await page.goto(routeUrl(route), { waitUntil: 'networkidle', timeout: 90000 });
  if (options.waitFor) await page.waitForSelector(options.waitFor, { timeout: 30000 });
  return { context, page, response, pageErrors, failedRequests };
}
async function inspectRoute(browser, engine, route, runAxe) {
  const { context, page, response, pageErrors, failedRequests } = await open(browser, route);
  const facts = await page.evaluate(() => {
    const hero = document.querySelector('.guide-hero__image');
    let jsonLdValid = false;
    try { JSON.parse(document.querySelector('script[type="application/ld+json"]')?.textContent || ''); jsonLdValid = true; } catch {}
    return {
      title: document.title,
      h1: document.querySelector('h1')?.textContent?.trim() || '',
      description: document.querySelector('meta[name="description"]')?.content || '',
      imageLoaded: Boolean(hero?.complete && hero.naturalWidth > 0),
      imageAlt: hero?.getAttribute('alt') || '',
      missingAlt: [...document.images].filter((image) => !image.hasAttribute('alt')).map((image) => image.src),
      jsonLdValid,
      canonical: document.querySelector('link[rel="canonical"]')?.href || '',
      phase7Css: [...document.styleSheets].some((sheet) => sheet.href?.includes('/css/pages/phase7.css')),
      phase7Script: [...document.scripts].some((script) => script.src?.includes('/js/phase7.js')),
      dataReady: Boolean(document.querySelector('[data-p7-quest-count], [data-p7-craft-count], [data-p7-hideout-count], [data-p7-trader-count], [data-p7-tree-count], [data-p7-kappa-progress]')),
      htmlChars: document.documentElement.outerHTML.length,
    };
  });
  const failures = [];
  if (!response || response.status() !== 200) failures.push(`HTTP ${response?.status() ?? 'no response'}`);
  if (!facts.h1 || !facts.title || !facts.description) failures.push('titre, H1 ou description manquant');
  if (!facts.imageLoaded || !facts.imageAlt) failures.push('visuel hero absent, non chargé ou sans texte alternatif');
  if (facts.missingAlt.length) failures.push(`images sans alt: ${facts.missingAlt.join(', ')}`);
  if (!facts.jsonLdValid) failures.push('JSON-LD absent ou invalide');
  if (!facts.phase7Css || !facts.phase7Script) failures.push('CSS ou module PHASE_7 non référencé');
  if (facts.canonical) failures.push(`canonical non autorisé en aperçu: ${facts.canonical}`);
  if (pageErrors.length) failures.push(`erreurs navigateur: ${pageErrors.slice(0, 4).join(' | ')}`);
  if (failedRequests.length) failures.push(`requêtes échouées: ${failedRequests.slice(0, 4).join(' | ')}`);
  let axe = { violations: [], review: [] };
  if (runAxe) {
    await page.addScriptTag({ content: axeSource });
    axe = await page.evaluate(async () => {
      const output = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'] } });
      return {
        violations: output.violations.map((violation) => ({ id: violation.id, impact: violation.impact, help: violation.help, targets: violation.nodes.slice(0, 12).map((node) => node.target) })),
        review: output.incomplete.filter((violation) => ['color-contrast', 'aria-prohibited-attr'].includes(violation.id)).map((violation) => ({ id: violation.id, targets: violation.nodes.slice(0, 12).map((node) => node.target) })),
      };
    });
    result.audits.push({ engine, route, ...axe });
    if (axe.violations.length) failures.push(`axe: ${axe.violations.map((violation) => `${violation.id} (${violation.targets.length})`).join(', ')}`);
  }
  result.routes.push({ engine, route, http: response?.status(), title: facts.title, htmlChars: facts.htmlChars, imageLoaded: facts.imageLoaded, canonical: facts.canonical });
  record(`${engine} · ${route} · HTML, médias, SEO d’aperçu${runAxe ? ' et axe-core' : ''}`, failures.length === 0,
    failures.length ? failures : { h1: facts.h1, htmlChars: facts.htmlChars, dataReady: facts.dataReady, axeViolations: axe.violations.length });
  await context.close();
}

async function testTraderIndex(browser) {
  const { context, page } = await open(browser, 'pages/traders/');
  await check('Traders · 16 entrées, spécialité, type et loyauté', async () => {
    const cards = page.locator('[data-p7-trader-card]');
    assert(await cards.count() === 16, `16 entrées attendues, reçu ${await cards.count()}`);
    await page.locator('[data-p7-trader-specialty]').selectOption('armes');
    assert(await page.locator('[data-p7-trader-card]:not([hidden])').count() === 2, 'le filtre Armes ne renvoie pas Prapor et Mechanic');
    await page.locator('[data-p7-trader-reset]').click();
    await page.locator('[data-p7-trader-kind]').selectOption('aux');
    assert(await page.locator('[data-p7-trader-card]:not([hidden])').count() === 6, 'six entrées auxiliaires attendues');
    await page.locator('[data-p7-trader-reset]').click();
    assert(await page.locator('[data-p7-loyalty-table] tr').count() >= 20, 'table de loyauté regular vide');
    await page.locator('[data-p7-loyalty-tier]').selectOption('4');
    assert(await page.locator('[data-p7-loyalty-table] tr').count() === 7, 'sept paliers LL4 classiques attendus, Fence séparé');
    await page.locator('[data-p7-loyalty-mode]').selectOption('pve');
    assert((await page.locator('[data-p7-loyalty-note]').innerText()).includes('PvE Zone'), 'mode PVE non annoncé dans le statut');
    return '16 fiches/auxiliaires · filtres · LL4 · mode PvE';
  });
  await context.close();
}
async function testQuests(browser) {
  const { context, page } = await open(browser, 'pages/quests/');
  await check('Quêtes · 503/499/462 tâches, recherche, progression et filtres', async () => {
    const count = page.locator('[data-p7-quest-count]');
    assert((await count.innerText()).includes('503 dans le snapshot'), '503 tâches regular non affichées');
    assert(await page.locator('[data-p7-quest-list] tr').count() === 70, `70 lignes affichées attendues, reçu ${await page.locator('[data-p7-quest-list] tr').count()}`);
    await page.locator('[data-p7-quest-search]').fill('Collector');
    assert(await page.locator('[data-p7-quest-list] tr').count() === 1, 'recherche Collector devrait trouver une tâche');
    assert((await page.locator('[data-p7-quest-list]').innerText()).includes('Collectionneur'), 'nom français de Collector absent');
    await page.locator('[data-p7-quest-search]').fill('');
    await page.locator('[data-p7-quest-kappa]').check();
    assert((await count.innerText()).includes('13 résultat'), '13 balises Kappa attendues dans regular');
    await page.locator('[data-p7-quest-reset]').click();
    const first = data.modes.regular.tasks[0];
    await page.locator('[data-p7-quest-search]').fill(first.id);
    const status = page.locator(`[data-p7-quest-list] select[data-quest-id="${first.id}"]`);
    await status.selectOption('done');
    assert(await page.locator(`[data-p7-quest-list] select[data-quest-id="${first.id}"]`).inputValue() === 'done', 'statut local non restitué après rendu');
    assert(await page.evaluate((id) => JSON.parse(localStorage.getItem('tug-p7-quest-progress:regular') || '{}')[id] === 'done', first.id), 'statut local absent de localStorage');
    await page.locator('[data-p7-quest-progress]').selectOption('done');
    assert(await page.locator('[data-p7-quest-list] tr').count() === 1, 'filtre Terminées ne conserve pas la tâche cochée');
    await page.locator('#quest-mode').selectOption('pve');
    assert((await count.innerText()).includes('499 dans le snapshot'), 'mode PvE ne charge pas 499 tâches');
    return '503 regular · 499 PvE · recherche Kappa · suivi local';
  });
  await context.close();
}
async function testTaskDeepLink(browser) {
  const task = data.modes['pvp-season'].tasks.find((row) => data.modes.regular.tasks.some((candidate) => candidate.id === row.id)) || data.modes['pvp-season'].tasks[0];
  const { context, page } = await open(browser, `pages/quests/?mode=pvp-season&task=${task.id}`);
  await check('Quêtes · deep link conserve le mode explicitement demandé', async () => {
    assert(await page.locator('#quest-mode').inputValue() === 'pvp-season', 'mode de deep link remplacé par le premier mode trouvé');
    assert(await page.locator('[data-p7-quest-list] tr').count() === 1, 'tâche du deep link non filtrée');
    return `${task.nameFr} · PvP Seasonal`;
  });
  await context.close();
}
async function testQuestTree(browser) {
  const { context, page } = await open(browser, 'pages/quests/quest-tree.html');
  await check('Arbre · Collector, prérequis, cases locales et export JSON', async () => {
    const collector = data.collectorByMode.regular;
    assert(await page.locator('[data-p7-tree-task]').inputValue() === collector.id, 'Collector devrait être sélectionnée en repli');
    assert((await page.locator('[data-p7-tree-panel]').innerText()).includes('Prérequis déclarés (5)'), 'les cinq liens directs de Collector ne sont pas indiqués');
    const dependency = collector.taskRequirements[0].taskId;
    const checkbox = page.locator(`[data-tree-state="${dependency}"]`).first();
    await checkbox.check();
    assert(await page.evaluate((id) => JSON.parse(localStorage.getItem('tug-p7-tree:regular') || '{}')[id] === 'done', dependency), 'état local de prérequis absent');
    const downloadPromise = page.waitForEvent('download');
    await page.locator('[data-p7-tree-export]').click();
    const download = await downloadPromise;
    assert(download.suggestedFilename().includes('tarkov-quetes-regular'), 'nom de fichier JSON inattendu');
    return 'Collector · 5 prérequis listés · export local';
  });
  await context.close();
}
async function testKappa(browser) {
  const { context, page } = await open(browser, 'pages/quests/kappa-guide.html');
  await check('Kappa · 44 objets FIR, mode, recherche et checklist locale', async () => {
    assert(await page.locator('[data-p7-kappa-items] .phase7-checkbox').count() === 44, '44 objectifs attendus');
    const first = page.locator('[data-p7-kappa-items] input[type="checkbox"]').first();
    const firstText = await page.locator('[data-p7-kappa-items] .phase7-checkbox strong').first().innerText();
    await first.check();
    assert((await page.locator('[data-p7-kappa-progress]').innerText()).includes('1 / 44'), 'compteur local Kappa incorrect');
    await page.locator('[data-p7-kappa-search]').fill(firstText.slice(0, 5));
    assert(await page.locator('[data-p7-kappa-items] .phase7-checkbox:not([hidden])').count() >= 1, 'recherche Kappa ne conserve pas l’objet choisi');
    await page.locator('#kappa-mode').selectOption('pve');
    assert((await page.locator('[data-p7-kappa-progress]').innerText()).includes('PvE Zone'), 'mode PvE Kappa non annoncé');
    await page.locator('[data-p7-kappa-clear]').click();
    assert((await page.locator('[data-p7-kappa-progress]').innerText()).includes('0 / 44'), 'effacement checklist Kappa inopérant');
    return '44 objectifs · mode PvE · recherche et effacement';
  });
  await context.close();
}
async function testHideout(browser) {
  const station = data.modes.regular.stations[0];
  const { context, page } = await open(browser, `pages/hideout/?mode=regular&station=${station.id}`);
  await check('Planque · 26 stations, deep link, matériaux FIR et filtres par mode', async () => {
    assert(await page.locator('[data-p7-hideout-stations] .phase7-station').count() === 26, '26 stations regular attendues');
    assert(await page.locator(`[data-station-id="${station.id}"]`).getAttribute('open') !== null, 'deep link de station ne l’ouvre pas');
    await page.locator('[data-p7-hideout-search]').fill(station.nameFr);
    assert(await page.locator('[data-p7-hideout-stations] .phase7-station').count() === 1, 'recherche station non sélective');
    await page.locator('[data-p7-hideout-search]').fill('');
    await page.locator('[data-p7-hideout-fir]').selectOption('fir');
    assert(await page.locator('[data-p7-hideout-stations] .phase7-station').count() > 0, 'aucun besoin FIR regular trouvé');
    await page.locator('[data-p7-hideout-stations] .phase7-station').first().locator(':scope > summary').click();
    await page.locator('[data-p7-hideout-stations] .phase7-level').first().locator(':scope > summary').click();
    assert((await page.locator('[data-p7-hideout-stations]').innerText()).includes('Matériaux affichés'), 'les matériaux ne reflètent pas le filtre FIR');
    await page.locator('#hideout-mode').selectOption('pvp-season');
    assert((await page.locator('[data-p7-hideout-count]').innerText()).includes('0 station(s)'), 'le filtre FIR Seasonal devrait respecter le snapshot à zéro');
    return '26 stations regular/PvE · filtre FIR · mode Seasonal distinct';
  });
  await context.close();
}
async function testCrafting(browser) {
  const { context, page } = await open(browser, 'pages/hideout/crafting.html');
  await check('Atelier · 214 recettes, estimation du lot et prix locaux', async () => {
    assert((await page.locator('[data-p7-craft-count]').innerText()).includes('214 recette'), '214 recettes regular attendues');
    const recipe = data.modes.regular.crafts.find((row) => row.ingredients.some((ingredient) => !ingredient.tool && ingredient.itemId));
    assert(recipe, 'recette avec consommable tarifable introuvable');
    await page.locator('[data-p7-craft-recipe]').selectOption(recipe.id);
    const ingredients = page.locator('[data-p7-craft-detail] input[data-craft-price]');
    assert(await ingredients.count() > 0, 'champs de prix consommables manquants');
    const outputPrice = page.locator('[data-p7-craft-detail] input[data-craft-output-price]');
    await outputPrice.fill('2000');
    const gross = (Number(recipe.output.count) || 0) * 2000;
    const grossText = await page.locator('[data-p7-craft-detail] .phase7-craft-result > div').nth(1).locator('strong').innerText();
    assert(grossText.includes(new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 }).format(gross)), 'valeur de sortie brute non calculée indépendamment du coût');
    for (let i = 0; i < await ingredients.count(); i++) await ingredients.nth(i).fill('100');
    const expectedCost = recipe.ingredients.filter((row) => !row.tool).reduce((sum, row) => sum + 100 * Number(row.count || 0), 0);
    const costText = await page.locator('[data-p7-craft-detail] .phase7-craft-result > div').nth(0).locator('strong').innerText();
    assert(costText.includes(new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 }).format(expectedCost)), `coût de lot incorrect: ${costText}`);
    await page.locator('[data-p7-craft-detail] [data-craft-fee]').fill('10');
    assert(await page.evaluate((key) => Boolean(localStorage.getItem(key)), `tug-p7-craft-prices:regular:${recipe.id}`), 'prix saisis non conservés localement');
    await page.locator('#craft-mode').selectOption('pve');
    assert((await page.locator('[data-p7-craft-count]').innerText()).includes('214 recette'), 'mode PvE ne charge pas ses 214 recettes');
    return `${recipe.output.nameFr} · coût lot ${expectedCost} ₽ · sortie ${gross} ₽`;
  });
  await context.close();
}
async function testNoJavaScript(browser) {
  for (const [route, selector, expected] of [
    ['pages/quests/', '[data-p7-quest-list] tr', 60],
    ['pages/quests/kappa-guide.html', '[data-p7-kappa-items] .phase7-checkbox', 44],
    ['pages/hideout/', '[data-p7-hideout-stations] .phase7-station', 26],
    ['pages/hideout/crafting.html', '[data-p7-static-fallback] details', 214],
  ]) {
    await check(`Sans JavaScript · ${route} · repli statique`, async () => {
      const { context, page, response } = await open(browser, route, { javaScriptEnabled: false });
      const count = await page.locator(selector).count();
      await context.close();
      assert(response?.status() === 200, 'HTTP différent de 200');
      assert(count === expected, `${expected} éléments statiques attendus, reçu ${count}`);
      return `${count} éléments lisibles sans exécuter de script`;
    });
  }
}
async function testResponsive(browser) {
  for (const [route, width] of [['pages/quests/', 375], ['pages/hideout/', 320], ['pages/traders/', 768]]) {
    const { context, page } = await open(browser, route, { width, height: 900 });
    const size = await page.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth, body: document.body.scrollWidth }));
    const passed = size.document <= size.viewport + 1 && size.body <= size.viewport + 1;
    result.responsive.push({ route, width, ...size, passed });
    record(`Reflow · ${route} · ${width}px`, passed, size);
    await context.close();
  }
}
async function main() {
  assert(ROUTES.length === 16, 'le QA doit viser exactement 16 routes');
  const chrome = await chromium.launch({ headless: true });
  result.browser.chromium = 'OK';
  for (const route of ROUTES) await inspectRoute(chrome, 'Chromium', route, true);
  await testTraderIndex(chrome);
  await testQuests(chrome);
  await testTaskDeepLink(chrome);
  await testQuestTree(chrome);
  await testKappa(chrome);
  await testHideout(chrome);
  await testCrafting(chrome);
  await testNoJavaScript(chrome);
  await testResponsive(chrome);
  await chrome.close();
  try {
    const ff = await firefox.launch({ headless: true });
    result.browser.firefox = 'OK';
    for (const route of ROUTES) await inspectRoute(ff, 'Firefox', route, false);
    await ff.close();
  } catch (error) {
    result.browser.firefox = `ECHEC: ${error.message}`;
    record('Firefox · démarrage du navigateur', false, error.stack || error.message);
  }
  completed = true;
  result.status = errors.length ? 'ECHEC' : 'PASS';
  result.summary = { routesConfigured: ROUTES.length, routeChecks: result.routes.length, checks: result.checks.length,
    axeAudits: result.audits.length, axeViolations: result.audits.reduce((n, audit) => n + audit.violations.length, 0), errors: errors.length };
  persist();
  console.log(`\n${result.status} · ${result.summary.routeChecks} contrôles de route · ${result.summary.checks} assertions · ${result.summary.axeAudits} audits axe-core · ${errors.length} échec(s)`);
  if (errors.length) process.exitCode = 1;
}
main().catch((error) => { record('QA non gérée', false, error.stack || error.message); process.exitCode = 1; });
