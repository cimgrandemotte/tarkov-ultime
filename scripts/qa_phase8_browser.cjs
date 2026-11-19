#!/usr/bin/env node
/* QA PHASE_8 : dix routes, Chromium/Firefox, axe, filtres, calculateurs, stockage et no-JS. */
const fs = require('node:fs');
const path = require('node:path');
const { chromium, firefox } = require('playwright');
const ROOT = path.resolve(__dirname, '..');
const BASE = (process.env.PHASE8_BASE_URL || 'http://127.0.0.1:4180').replace(/\/$/, '');
const OUT = path.join(ROOT, 'data/snapshots/validation-phase-8.json');
const axeSource = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const ROUTES = [
  'pages/skills/', 'pages/economy/', 'pages/economy/flea-market.html', 'pages/economy/money-making.html',
  'pages/strategy/', 'pages/strategy/beginner-tips.html', 'pages/strategy/advanced-tactics.html',
  'pages/strategy/pvp-guide.html', 'pages/strategy/pve-guide.html', 'pages/strategy/meta-builds.html',
];
const report = { schemaVersion: 1, phase: 'PHASE_8', status: 'EN_COURS', base: BASE, checkedAt: new Date().toISOString(), routes: [], checks: [], audits: [], responsive: [], noJs: [], errors: [] };
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
  const pageErrors = [];
  const failedRequests = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));
  page.on('console', (message) => {
    if (message.type() === 'error' && !message.text().toLowerCase().includes('favicon')) pageErrors.push(message.text());
  });
  page.on('requestfailed', (request) => {
    if (!request.url().toLowerCase().includes('favicon')) failedRequests.push(`${request.url()} ${request.failure()?.errorText || ''}`);
  });
  const response = await page.goto(url(route), { waitUntil: 'networkidle', timeout: 90000 });
  await page.waitForTimeout(60);
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
      description: document.querySelector('meta[name="description"]')?.content || '',
      imageLoaded: Boolean(hero?.complete && hero.naturalWidth > 0),
      imageAlt: hero?.getAttribute('alt') || '',
      missingAlt: [...document.images].filter((image) => !image.hasAttribute('alt')).map((image) => image.src),
      duplicateIds,
      jsonLdValid,
      canonical: document.querySelector('link[rel="canonical"]')?.href || '',
      phase8Css: [...document.styleSheets].some((sheet) => sheet.href?.includes('/css/pages/phase8.css')),
      phase8Script: [...document.scripts].some((script) => script.src?.includes('/js/phase8.js')),
      appReady: document.documentElement.dataset.appReady === 'true',
      searchSource: document.querySelector('[data-site-search]')?.dataset.searchSource || '',
      htmlChars: document.documentElement.outerHTML.length,
      topLevelHeadings: [...document.querySelectorAll('h1')].length,
    };
  });
  const failures = [];
  if (!response || response.status() !== 200) failures.push(`HTTP ${response?.status() ?? 'no response'}`);
  if (!facts.h1 || !facts.title || !facts.description) failures.push('titre, H1 ou description manquant');
  if (facts.topLevelHeadings !== 1) failures.push(`${facts.topLevelHeadings} H1 trouvés`);
  if (!facts.imageLoaded || !facts.imageAlt) failures.push('visuel hero absent, non chargé ou sans texte alternatif');
  if (facts.missingAlt.length) failures.push(`images sans alt: ${facts.missingAlt.join(', ')}`);
  if (facts.duplicateIds.length) failures.push(`IDs dupliqués: ${facts.duplicateIds.join(', ')}`);
  if (!facts.jsonLdValid) failures.push('JSON-LD absent ou invalide');
  if (!facts.phase8Css || !facts.phase8Script || !facts.appReady) failures.push('CSS, module PHASE_8 ou initialisation manquant');
  if (!facts.searchSource.endsWith('js/data/search-index.json')) failures.push(`source de recherche invalide: ${facts.searchSource}`);
  if (facts.canonical) failures.push(`canonical public non autorisé en aperçu: ${facts.canonical}`);
  if (pageErrors.length) failures.push(`erreurs navigateur: ${pageErrors.slice(0, 5).join(' | ')}`);
  if (failedRequests.length) failures.push(`requêtes échouées: ${failedRequests.slice(0, 5).join(' | ')}`);
  let axe = { violations: [], review: [] };
  if (runAxe) {
    await page.addScriptTag({ content: axeSource });
    axe = await page.evaluate(async () => {
      const output = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'] } });
      return {
        violations: output.violations.map((violation) => ({ id: violation.id, impact: violation.impact, help: violation.help, targets: violation.nodes.slice(0, 16).map((node) => node.target) })),
        review: output.incomplete.filter((violation) => ['color-contrast', 'aria-prohibited-attr'].includes(violation.id)).map((violation) => ({ id: violation.id, targets: violation.nodes.slice(0, 16).map((node) => node.target) })),
      };
    });
    report.audits.push({ engine, route, ...axe });
    if (axe.violations.length) failures.push(`axe: ${axe.violations.map((item) => `${item.id} (${item.targets.length})`).join(', ')}`);
  }
  report.routes.push({ engine, route, http: response?.status(), title: facts.title, htmlChars: facts.htmlChars, imageLoaded: facts.imageLoaded, canonical: facts.canonical });
  record(`${engine} · ${route} · HTML, médias et aperçu${runAxe ? ' + axe-core' : ''}`, failures.length === 0,
    failures.length ? failures : { appReady: facts.appReady, htmlChars: facts.htmlChars, axeViolations: axe.violations.length });
  await context.close();
}
async function check(name, fn) {
  try { record(name, true, await fn()); }
  catch (error) { record(name, false, error.stack || error.message); }
}
async function testSearch(browser) {
  const { context, page } = await open(browser, 'pages/skills/');
  await check('Recherche globale · index PHASE_8 et lien Flea', async () => {
    const trigger = page.locator('[data-site-search-trigger]');
    assert(await trigger.isVisible(), 'bouton de recherche non initialisé');
    await trigger.click();
    const input = page.locator('[data-search-input]');
    await input.fill('Flea Market');
    await page.waitForFunction(() => document.querySelector('[data-search-results]')?.innerText.includes('Flea Market'));
    const hrefs = await page.locator('[data-search-results] a').evaluateAll((links) => links.map((link) => link.getAttribute('href')));
    assert(hrefs.some((href) => href?.includes('pages/economy/flea-market.html')), `route Flea absente: ${hrefs.join(', ')}`);
    return 'Requête Flea Market renvoie la route dédiée';
  });
  await context.close();
}
async function testSkills(browser) {
  const { context, page } = await open(browser, 'pages/skills/');
  await check('Compétences · filtre de patch et journal local', async () => {
    assert(await page.locator('[data-p8-skill-topic]').count() === 4, 'quatre thèmes officiels attendus');
    await page.locator('[data-p8-skill-filter]').selectOption('metabolism');
    assert(await page.locator('[data-p8-skill-topic]:visible').count() === 1, 'filtre Métabolisme ne conserve pas un thème');
    await page.locator('[data-p8-skill-filter]').selectOption('all');
    await page.locator('[data-p8-log-skill]').fill('Métabolisme');
    await page.locator('[data-p8-log-mode]').selectOption('pve');
    await page.locator('[data-p8-log-note]').fill('Test manuel après un raid; aucune formule appliquée.');
    await page.locator('[data-p8-skill-log-form] button[type="submit"]').click();
    assert(await page.locator('[data-p8-log-list] li').count() === 1, 'note non rendue');
    assert((await page.locator('[data-p8-log-list]').innerText()).includes('PvE Zone'), 'mode non sauvegardé');
    assert(await page.evaluate(() => JSON.parse(localStorage.getItem('tug:p8:skill-log:v1') || '[]').length === 1), 'journal absent du stockage local');
    await page.locator('[data-p8-log-list] button[data-p8-log-remove]').click();
    assert(await page.locator('[data-p8-log-list] li').count() === 0, 'suppression individuelle inopérante');
    return 'filtre, ajout et retrait d’une note locale vérifiés';
  });
  await context.close();
}
async function testCalculators(browser) {
  const { context, page } = await open(browser, 'pages/economy/');
  await check('Économie · calculateur hypothèses utilisateur + reset', async () => {
    const form = page.locator('[data-p8-calc="economy"]');
    await form.locator('[data-p8-input="gross"]').fill('100000');
    await form.locator('[data-p8-input="fee"]').fill('5');
    await form.locator('[data-p8-input="cost"]').fill('20000');
    await form.locator('[data-p8-input="minutes"]').fill('30');
    await form.locator('button[type="submit"]').click();
    const result = await form.locator('[data-p8-result="economy"]').innerText();
    assert(result.includes('75') && result.includes('150'), `résultat inattendu: ${result}`);
    await form.locator('button[type="reset"]').click();
    assert(await form.locator('[data-p8-input="gross"]').inputValue() === '', 'reset ne vide pas le champ');
    return '100000 × (1−5 %) − 20000 = 75000; mise à l’échelle 30 min = 150000/h; reset OK';
  });
  await context.close();

  const flea = await open(browser, 'pages/economy/flea-market.html');
  await check('Flea · net simplifié contre trader, sans taux prérempli', async () => {
    const form = flea.page.locator('[data-p8-calc="flea"]');
    assert(await form.locator('input').evaluateAll((nodes) => nodes.every((node) => node.value === '')), 'un prix ou un taux est prérempli');
    await form.locator('[data-p8-input="ask"]').fill('1000');
    await form.locator('[data-p8-input="rate"]').fill('5');
    await form.locator('[data-p8-input="trader"]').fill('800');
    await form.locator('[data-p8-input="basis"]').fill('100');
    await form.locator('button[type="submit"]').click();
    const text = await form.locator('[data-p8-result="flea"]').innerText();
    assert(text.includes('850') && text.includes('700'), `comparaison inattendue: ${text}`);
    return 'Flea 850 ₽ contre trader 700 ₽ selon les entrées; champ frais manuel';
  });
  await flea.context.close();

  const money = await open(browser, 'pages/economy/money-making.html');
  await check('Roubles · estimation de scénario explicitement probabiliste', async () => {
    const form = money.page.locator('[data-p8-calc="money"]');
    for (const [key, value] of Object.entries({ haul: '100000', survival: '50', recovery: '0', kit: '20000', fixed: '10000', time: '30' })) {
      await form.locator(`[data-p8-input="${key}"]`).fill(value);
    }
    await form.locator('button[type="submit"]').click();
    const text = await form.locator('[data-p8-result="money"]').innerText();
    assert(text.includes('20') && text.includes('40'), `scénario inattendu: ${text}`);
    assert(text.includes('tes entrées'), 'hypothèses utilisateur insuffisamment explicites');
    return '50 % × 100000 + 50 % × 0 − 20000 − 10000 = 20000; 30 min = 40000/h';
  });
  await money.context.close();

  const build = await open(browser, 'pages/strategy/meta-builds.html');
  await check('Build · addition des coûts et plafond de budget', async () => {
    const form = build.page.locator('[data-p8-calc="build"]');
    await form.locator('[data-p8-build-mode]').selectOption('pve');
    await form.locator('[data-p8-build-budget]').fill('100000');
    await form.locator('[data-p8-build-cost="weapon"]').fill('50000');
    await form.locator('[data-p8-build-cost="ammo"]').fill('10000');
    await form.locator('button[type="submit"]').click();
    const text = await form.locator('[data-p8-result="build"]').innerText();
    assert(text.includes('60') && text.includes('100'), `total ou budget absent: ${text}`);
    assert(text.includes('PvE Zone'), 'mode non signalé');
    return '60000 ₽, sous budget utilisateur 100000 ₽; coûts vides explicités';
  });
  await build.context.close();
}
async function testFiltersAndChecklist(browser) {
  const strategies = await open(browser, 'pages/strategy/');
  await check('Stratégies · filtre de profil', async () => {
    await strategies.page.locator('[data-p8-strategy-mode]').selectOption('pve');
    assert(await strategies.page.locator('[data-p8-mode-card]:visible').count() === 1, 'filtre PvE doit afficher un seul contexte');
    assert((await strategies.page.locator('[data-p8-mode-count]').innerText()).includes('1 contexte'), 'compteur du filtre absent');
    return 'filtre PvE et statut de résultat corrects';
  });
  await strategies.context.close();

  const pvp = await open(browser, 'pages/strategy/pvp-guide.html');
  await check('PvP · comparaison Permanent / Seasonal', async () => {
    await pvp.page.locator('[data-p8-pvp-mode]').selectOption('pvp-season');
    assert(await pvp.page.locator('[data-p8-pvp-panel]:visible').count() === 1, 'filtre Seasonal doit afficher une seule carte');
    assert((await pvp.page.locator('[data-p8-pvp-panel]:visible').innerText()).includes('assurance'), 'règle Seasonal absente');
    return 'filtre Seasonal laisse visible sa carte et sa règle d’assurance';
  });
  await pvp.context.close();

  const beginner = await open(browser, 'pages/strategy/beginner-tips.html');
  await check('Astuces · recherche, favori et état local', async () => {
    const page = beginner.page;
    assert(await page.locator('[data-p8-tip]').count() === 61, `61 astuces attendues, obtenu ${await page.locator('[data-p8-tip]').count()}`);
    await page.locator('[data-p8-tip-search]').fill('assurance');
    assert(await page.locator('[data-p8-tip]:visible').count() >= 1, 'recherche assurance ne renvoie rien');
    const button = page.locator('[data-p8-tip]:visible [data-p8-favorite]').first();
    await button.click();
    assert(await button.getAttribute('aria-pressed') === 'true', 'favori non activé');
    await page.locator('[data-p8-tip-search]').fill('');
    await page.locator('[data-p8-only-favorites]').check();
    assert(await page.locator('[data-p8-tip]:visible').count() === 1, 'filtre favoris ne conserve pas le favori');
    assert(await page.evaluate(() => JSON.parse(localStorage.getItem('tug:p8:tip-favorites:v1') || '[]').length === 1), 'favori absent du stockage local');
    await page.locator('[data-p8-clear-favorites]').click();
    assert(await page.locator('[data-p8-tip]:visible').count() === 61, 'effacement des favoris ne restaure pas toutes les astuces');
    return '61 astuces, recherche, étoile aria-pressed et reset favoris';
  });
  await beginner.context.close();

  const pve = await open(browser, 'pages/strategy/pve-guide.html');
  await check('Prestige PvE · checklist locale séparée par palier', async () => {
    const first = pve.page.locator('[data-p8-prestige-check]').first();
    await first.check();
    assert((await pve.page.locator('[data-p8-prestige-status]').innerText()).includes('1/6'), 'compteur local incorrect');
    await pve.page.locator('[data-p8-prestige-tier]').selectOption('2');
    assert(await pve.page.locator('[data-p8-prestige-check]').first().isChecked() === false, 'les états de deux paliers sont confondus');
    await pve.page.locator('[data-p8-prestige-reset]').click();
    return 'case stockée par palier; rappel indique qu’elle ne vérifie pas le client';
  });
  await pve.context.close();
}
async function testNavigation(browser) {
  const { context, page } = await open(browser, '');
  await check('Accueil · méga-menu vers les nouvelles routes', async () => {
    const summary = page.locator('.home-mega > summary');
    await summary.click();
    const links = await page.locator('.home-mega__panel a').evaluateAll((nodes) => nodes.map((node) => node.getAttribute('href')));
    assert(links.includes('./pages/skills/'), 'lien Compétences absent de l’accueil');
    assert(links.includes('./pages/economy/flea-market.html'), 'lien Flea absent de l’accueil');
    assert(links.includes('./pages/strategy/pve-guide.html'), 'lien PvE absent de l’accueil');
    return `${links.length} liens dans le méga-menu; Compétences, Flea et PvE présents`;
  });
  await context.close();
}
async function testNoJs(browser, route) {
  const { context, page, response } = await open(browser, route, { javaScriptEnabled: false, width: 1280 });
  const data = await page.evaluate(() => ({
    title: document.title,
    h1: document.querySelector('h1')?.textContent?.trim(),
    mainVisible: Boolean(document.querySelector('#main')?.getClientRects().length),
    navVisible: Boolean(document.querySelector('[data-site-nav]')?.getClientRects().length),
    visibleTips: [...document.querySelectorAll('[data-p8-tip]')].filter((el) => !el.hidden && el.getClientRects().length).length,
    visibleSkillTopics: [...document.querySelectorAll('[data-p8-skill-topic]')].filter((el) => !el.hidden && el.getClientRects().length).length,
    tableRows: document.querySelectorAll('.phase8-table tbody tr').length,
    introVisible: Boolean(document.querySelector('.phase8-intro')?.getClientRects().length),
  }));
  const failures = [];
  if (!response || response.status() !== 200) failures.push(`HTTP ${response?.status()}`);
  if (!data.title || !data.h1 || !data.mainVisible || !data.navVisible || !data.introVisible) failures.push('structure HTML principale absente');
  if (route.includes('beginner-tips') && data.visibleTips !== 61) failures.push(`61 astuces HTML visibles attendues, obtenu ${data.visibleTips}`);
  if (route.includes('skills/') && data.visibleSkillTopics !== 4) failures.push(`4 thèmes visibles attendus, obtenu ${data.visibleSkillTopics}`);
  if (route.includes('economy/') && !route.includes('money-making') && data.tableRows !== 3) failures.push(`3 lignes de mode statiques attendues, obtenu ${data.tableRows}`);
  report.noJs.push({ route, ...data });
  record(`Sans JavaScript · ${route} · contenu et navigation statiques`, failures.length === 0, failures.length ? failures : data);
  await context.close();
}
async function testResponsive(browser, route) {
  const { context, page, response } = await open(browser, route, { width: 375, height: 812 });
  await page.waitForTimeout(80);
  const sizes = [];
  for (const viewport of [{ width: 375, height: 812 }, { width: 768, height: 1024 }, { width: 1440, height: 900 }]) {
    await page.setViewportSize(viewport);
    const m = await page.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth, body: document.body.scrollWidth }));
    sizes.push(m);
  }
  const failures = sizes.filter((row) => row.document > row.viewport + 1 || row.body > row.viewport + 1);
  report.responsive.push({ route, sizes });
  record(`Responsive · ${route} · 375/768/1440 px`, Boolean(response?.status() === 200 && failures.length === 0), failures.length ? failures : sizes);
  await context.close();
}
async function main() {
  const chrome = await chromium.launch({ headless: true });
  const fox = await firefox.launch({ headless: true });
  try {
    for (const route of ROUTES) await inspectRoute(chrome, 'Chromium', route, true);
    for (const route of ROUTES) await inspectRoute(fox, 'Firefox', route, false);
    for (const route of ROUTES) await testResponsive(chrome, route);
    for (const route of ['pages/skills/', 'pages/economy/', 'pages/economy/flea-market.html', 'pages/economy/money-making.html', 'pages/strategy/beginner-tips.html', 'pages/strategy/pve-guide.html', 'pages/strategy/meta-builds.html']) await testNoJs(chrome, route);
    await testSearch(chrome);
    await testSkills(chrome);
    await testCalculators(chrome);
    await testFiltersAndChecklist(chrome);
    await testNavigation(chrome);
  } finally {
    await chrome.close();
    await fox.close();
  }
  complete = errors.length === 0;
  persist();
  console.log(`\nPHASE_8 QA ${report.status} · ${report.checks.filter((x) => x.passed).length}/${report.checks.length} checks · ${report.routes.length} browser renders · ${report.audits.length} axe audits · ${report.responsive.length} responsive routes · ${report.noJs.length} no-JS fallbacks`);
  if (errors.length) process.exitCode = 1;
}
main().catch((error) => {
  errors.push(error.stack || error.message);
  persist();
  console.error(error);
  process.exitCode = 1;
});
