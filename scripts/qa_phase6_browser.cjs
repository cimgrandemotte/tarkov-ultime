#!/usr/bin/env node
/* QA locale PHASE_6 : routes, progressive enhancement, filtres, modes, recherche, reflow et axe-core. */
const fs = require('node:fs');
const path = require('node:path');
const { chromium, firefox } = require('playwright');
const ROOT = path.resolve(__dirname, '..');
const BASE = (process.env.PHASE6_BASE_URL || 'http://127.0.0.1:4180').replace(/\/$/, '');
const OUT = path.join(ROOT, 'data/snapshots/validation-phase-6.json');
const phase = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/phase6.json'), 'utf8'));
const routes = [...phase.armorPages, phase.bossHub, ...phase.bossProfiles].map((p) => p.route);
const axeSource = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const result = { schemaVersion: 1, status: 'EN_COURS', base: BASE, checkedAt: new Date().toISOString(), routes: [], checks: [], audits: [], responsive: [], browser: {}, errors: [] };
const errors = [];

function persist() {
  result.errors = errors;
  result.status = errors.length ? 'EN_COURS_AVEC_ECHECS' : 'EN_COURS';
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
function assert(condition, message) { if (!condition) throw new Error(message); }
async function check(name, fn) {
  try { record(name, true, await fn()); }
  catch (error) { record(name, false, error.stack || error.message); }
}
async function visit(browser, route, options = {}) {
  const context = await browser.newContext({ viewport: { width: options.width || 1440, height: options.height || 1000 }, reducedMotion: 'reduce', javaScriptEnabled: options.javaScriptEnabled !== false });
  const page = await context.newPage();
  const pageErrors = [];
  const failedRequests = [];
  page.on('pageerror', (e) => pageErrors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') pageErrors.push(m.text()); });
  page.on('requestfailed', (r) => failedRequests.push(`${r.url()} ${r.failure()?.errorText || ''}`));
  const response = await page.goto(`${BASE}/${route}`, { waitUntil: 'networkidle', timeout: 60000 });
  assert(response && response.status() === 200, `${route} HTTP ${response?.status()}`);
  if (options.javaScriptEnabled !== false) {
    await page.waitForFunction(() => document.documentElement.dataset.appReady === 'true', null, { timeout: 12000 });
  }
  await page.evaluate(() => document.fonts?.ready);
  return { context, page, response, pageErrors, failedRequests };
}

async function auditRoute(browser, route, engine, runAxe) {
  const { context, page, pageErrors, failedRequests, response } = await visit(browser, route);
  const facts = await page.evaluate(() => {
    const mainImage = document.querySelector('.guide-hero__image');
    const ld = [...document.querySelectorAll('script[type="application/ld+json"]')].map((node) => {
      try { return JSON.parse(node.textContent); } catch { return null; }
    });
    return {
      status: document.readyState,
      title: document.title,
      h1: [...document.querySelectorAll('h1')].map((n) => n.innerText.trim()),
      description: document.querySelector('meta[name="description"]')?.content || '',
      canonical: document.querySelector('link[rel="canonical"]')?.href || null,
      htmlWidth: document.documentElement.scrollWidth,
      bodyWidth: document.body.scrollWidth,
      viewportWidth: innerWidth,
      mainImage: mainImage ? { src: mainImage.getAttribute('src'), loaded: mainImage.complete && mainImage.naturalWidth > 0, alt: mainImage.getAttribute('alt') } : null,
      imageAltMissing: [...document.images].filter((image) => !image.hasAttribute('alt')).map((image) => image.getAttribute('src')),
      emptyLabelButtons: [...document.querySelectorAll('button')].filter((button) => !button.innerText.trim() && !button.getAttribute('aria-label')).length,
      jsonLdCount: ld.length,
      jsonLdValid: ld.length > 0 && ld.every(Boolean),
      canonicals: [...document.querySelectorAll('link[rel="canonical"]')].length,
      htmlChars: document.documentElement.outerHTML.length,
      phase6Tables: document.querySelectorAll('.phase6-table').length,
      armorRows: document.querySelectorAll('[data-p6-item-row]').length,
      bossRows: document.querySelectorAll('[data-p6-boss-row]').length,
      formsHidden: [...document.querySelectorAll('[data-p6-filter-form],[data-p6-chart-form],[data-p6-boss-controls]')].filter((x) => x.hidden).length,
    };
  });
  let failures = [];
  if (facts.h1.length !== 1) failures.push(`h1=${facts.h1.length}`);
  if (!facts.title || facts.title.length < 15) failures.push('title absent/court');
  if (facts.htmlWidth > facts.viewportWidth + 1 || facts.bodyWidth > facts.viewportWidth + 1) failures.push(`débordement ${facts.htmlWidth}/${facts.viewportWidth}`);
  if (!facts.mainImage?.loaded || !facts.mainImage?.alt) failures.push('visuel principal absent, non chargé ou sans texte alternatif');
  if (facts.imageAltMissing.length) failures.push(`images sans alt: ${facts.imageAltMissing.join(', ')}`);
  if (facts.emptyLabelButtons) failures.push(`${facts.emptyLabelButtons} boutons sans nom accessible`);
  if (!facts.jsonLdValid) failures.push('JSON-LD manquant ou invalide');
  if (facts.canonical) failures.push(`canonical vers ${facts.canonical} alors que le domaine public n’est pas confirmé`);
  if (pageErrors.length) failures.push(`erreurs navigateur: ${pageErrors.slice(0, 4).join(' | ')}`);
  if (failedRequests.length) failures.push(`requêtes échouées: ${failedRequests.slice(0, 4).join(' | ')}`);
  let axe = { violations: [], review: [] };
  if (runAxe) {
    await page.addScriptTag({ content: axeSource });
    axe = await page.evaluate(async () => {
      const output = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'] } });
      return {
        violations: output.violations.map((v) => ({ id: v.id, impact: v.impact, help: v.help, targets: v.nodes.slice(0, 20).map((n) => n.target) })),
        review: output.incomplete.filter((v) => ['color-contrast', 'aria-prohibited-attr'].includes(v.id)).map((v) => ({ id: v.id, targets: v.nodes.slice(0, 20).map((n) => n.target) })),
      };
    });
    result.audits.push({ engine, route, ...axe });
    if (axe.violations.length) failures.push(`axe: ${axe.violations.map((v) => `${v.id} (${v.targets.length})`).join(', ')}`);
  }
  result.routes.push({ engine, route, http: response.status(), title: facts.title, htmlChars: facts.htmlChars, armorRows: facts.armorRows, bossRows: facts.bossRows, imageLoaded: Boolean(facts.mainImage?.loaded), canonical: facts.canonical });
  record(`${engine} · ${route} · HTML, SEO, media, reflow${runAxe ? ' et axe-core' : ''}`, failures.length === 0, failures.length ? failures : { htmlChars: facts.htmlChars, armorRows: facts.armorRows, bossRows: facts.bossRows });
  await context.close();
}

async function testArmorFilters(browser) {
  const { context, page } = await visit(browser, 'pages/armor/');
  await check('Armures · index, recherche, groupe, classe, budget périmé et comparaison', async () => {
    const form = page.locator('[data-p6-filter-form][data-filter-kind="armor-index"]');
    assert(await form.isVisible(), 'filtres non activés');
    const all = page.locator('[data-p6-item-row]');
    assert(await all.count() === 423, `423 lignes attendues, reçu ${await all.count()}`);
    await form.locator('[data-p6-group]').selectOption('plates');
    assert(await page.locator('[data-p6-item-row]:not([hidden])').count() === 38, 'filtre Plaques ne renvoie pas 38 pièces');
    const first = page.locator('[data-p6-item-row]:not([hidden])').first();
    const sample = await first.evaluate((row) => ({ id: row.dataset.id, query: row.dataset.name, classes: row.dataset.classes.split('|').filter(Boolean) }));
    await form.locator('[data-p6-search]').fill(sample.query.split(' ').slice(0, 2).join(' '));
    assert(!(await page.locator(`[data-p6-item-row][data-id="${sample.id}"]`).evaluate((row) => row.hidden)), 'recherche masque son propre résultat');
    await form.locator('[data-p6-search]').fill('');
    if (sample.classes.length) {
      await form.locator('[data-p6-class]').selectOption(sample.classes[0]);
      const visibleClasses = await page.locator('[data-p6-item-row]:not([hidden])').evaluateAll((rows) => rows.map((row) => row.dataset.classes.split('|')));
      assert(visibleClasses.length > 0 && visibleClasses.every((classes) => classes.includes(sample.classes[0])), 'filtre de classe mal appliqué');
    }
    await form.locator('[data-p6-class]').selectOption('');
    await form.locator('[data-p6-group]').selectOption('');
    await form.locator('[data-p6-budget]').fill('1000000000');
    assert(await page.locator('[data-p6-item-row]:not([hidden])').count() === 0, 'un budget maximum inclut un prix absent ou périmé');
    assert((await page.locator('[data-p6-count]').innerText()).includes('périmé'), 'note sur les prix absents/périmés manquante');
    await form.locator('button[type="reset"]').click();
    await page.waitForTimeout(50);
    await form.locator('[data-p6-group]').selectOption('body-armor');
    const picks = page.locator('[data-p6-item-row][data-group="body-armor"]:not([hidden]) [data-p6-compare-item]');
    await picks.nth(0).check(); await picks.nth(1).check();
    assert(await page.locator('[data-p6-compare-output] table').count() === 1, 'comparaison deux objets non rendue');
    await picks.nth(2).check();
    assert(await page.locator('[data-p6-compare-output] table').count() === 1, 'comparaison trois objets non rendue');
    await picks.nth(3).click();
    assert(!(await picks.nth(3).isChecked()), 'limite de 3 comparables non respectée');
    await page.locator('[data-p6-clear-compare]').click();
    assert(await page.locator('[data-p6-compare-output] table').count() === 0, 'effacement de comparaison inopérant');
    return '423 entrées; filtre 38 plaques; classe; budget strictement récent; comparaisons 2–3 pièces';
  });
  await context.close();
}

async function testArmorSubpages(browser) {
  {
    const { context, page } = await visit(browser, 'pages/armor/body-armor.html');
    await check('Gilets et plaques · classes par pièce et filtre de poids', async () => {
      const form = page.locator('[data-p6-filter-form][data-filter-kind="body-armor"]');
      assert(await form.isVisible(), 'filtres gilets non visibles');
      assert(await page.locator('#p6-vests tbody tr').count() === 49, '49 gilets attendus');
      assert(await page.locator('#p6-plates tbody tr').count() === 38, '38 plaques attendues');
      const input = form.locator('[data-p6-class]');
      await input.selectOption('6');
      const rows = await page.locator('[data-p6-item-row]:not([hidden])').evaluateAll((els) => els.map((el) => el.dataset.classes.split('|')));
      assert(rows.length && rows.every((classes) => classes.includes('6')), 'le filtre ne conserve pas les lignes de classe 6');
      await form.locator('button[type="reset"]').click();
      await page.waitForTimeout(40);
      return `${rows.length} lignes avec la classe sélectionnée; 49 gilets et 38 plaques statiques`;
    });
    await context.close();
  }
  {
    const { context, page } = await visit(browser, 'pages/armor/helmets.html');
    await check('Casques · zone, classe et compatibilité audio reportées', async () => {
      const form = page.locator('[data-p6-filter-form][data-filter-kind="helmets"]');
      assert(await form.isVisible(), 'filtres casques non visibles');
      await form.locator('[data-p6-zone]').selectOption({ index: 1 });
      let visible = await page.locator('[data-p6-item-row]:not([hidden])').count();
      assert(visible > 0 && visible < 231, 'filtre de zone vide ou non sélectif');
      await form.locator('button[type="reset"]').click(); await page.waitForTimeout(40);
      await form.locator('[data-p6-headset]').selectOption('bloque');
      visible = await page.locator('[data-p6-item-row]:not([hidden])').count();
      assert(visible === 2, `2 obstructions audio exportées attendues, reçu ${visible}`);
      return `${visible} objets marqués blocksHeadset=true dans l’export`;
    });
    await context.close();
  }
  {
    const { context, page } = await visit(browser, 'pages/armor/rigs.html');
    await check('Rigs · tri numérique poids/capacité sans fusionner le stockage et les slots', async () => {
      const form = page.locator('[data-p6-filter-form][data-filter-kind="rigs"]');
      assert(await form.isVisible(), 'contrôles de tri non visibles');
      const sort = form.locator('[data-p6-sort]');
      await sort.selectOption('weight');
      const weights = await page.locator('#p6-rigs-table tbody tr').evaluateAll((rows) => rows.map((row) => Number(row.dataset.weight)).filter(Number.isFinite));
      assert(weights.length > 2 && weights.every((n, i) => i === 0 || weights[i - 1] <= n), 'tri poids croissant incorrect');
      await sort.selectOption('capacity');
      const caps = await page.locator('#p6-rigs-table tbody tr').evaluateAll((rows) => rows.map((row) => row.dataset.capacity === '' ? null : Number(row.dataset.capacity)).filter((n) => n != null));
      assert(caps.length > 2 && caps.every((n, i) => i === 0 || caps[i - 1] <= n), 'tri capacité croissant incorrect');
      return `${weights.length} rigs avec poids; ${caps.length} capacités numériques`;
    });
    await context.close();
  }
}

async function testArmorChart(browser) {
  const { context, page } = await visit(browser, 'pages/armor/armor-chart.html');
  await check('Comparateur armures · groupe homogène, champs exportés et prix par mode', async () => {
    const form = page.locator('[data-p6-chart-form]');
    assert(await form.isVisible(), 'comparateur non activé');
    await form.locator('[data-p6-chart-group]').selectOption('body-armor');
    const a = form.locator('[data-p6-chart-a]');
    const b = form.locator('[data-p6-chart-b]');
    await a.selectOption({ index: 1 });
    await b.selectOption({ index: 2 });
    assert(await page.locator('[data-p6-chart-output] .phase6-chart-card').count() === 2, 'deux fiches côte à côte attendues');
    const text = await page.locator('[data-p6-chart-output]').innerText();
    assert(text.includes('Classe par slot') && text.includes('Durabilité') && text.includes('Prix flea'), 'champs comparés manquants');
    assert(text.includes('aucun score') || text.includes('aucune classe'), 'limite de non-calcul manquante');
    await form.locator('[data-p6-chart-mode]').selectOption('pve');
    assert((await page.locator('[data-p6-chart-output]').innerText()).includes('PvE Zone'), 'mode de marché PvE non affiché');
    return '2 porte-plaques, comparaison descriptive, mode PvE sélectionné';
  });
  await context.close();
}

async function testBossHub(browser) {
  const { context, page } = await visit(browser, 'pages/bosses/');
  await check('Boss · filtre lieux, onglets PvE et lignes de santé nuancées', async () => {
    const controls = page.locator('[data-p6-boss-controls]');
    assert(await controls.isVisible(), 'commandes boss non activées');
    assert(await page.locator('[data-p6-boss-row]').count() === 15, '15 profils attendus');
    const search = controls.locator('[data-p6-boss-search]');
    const map = controls.locator('[data-p6-boss-map]');
    await search.fill('Killa');
    assert(await page.locator('[data-p6-boss-row]:not([hidden])').count() >= 2, 'recherche Killa ne montre pas les variantes');
    await map.selectOption({ label: 'Interchange' });
    assert(await page.locator('[data-p6-boss-row]:not([hidden])').count() === 1, 'filtre Interchange n’isole pas Killa classique');
    await search.fill(''); await map.selectOption('');
    await controls.locator('[data-p6-mode-tab="pve"]').click();
    const panel = page.locator('#boss-hub-panel');
    assert(await panel.isVisible() && (await panel.innerText()).includes('PvE'), 'panneau PvE non activé');
    const wedge = page.locator('[data-p6-boss-row]').filter({ hasText: 'The Wedge' });
    assert((await wedge.innerText()).includes('nouveau total inconnu'), 'HP historique du Wedge non nuancé dans le tableau');
    assert(!(await page.locator('[data-p6-boss-row]').filter({ hasText: 'Cultist Priest' }).innerText()).includes('850 HP'), 'HP non vérifié du Priest reste affiché');
    return '15 profils; filtres Killa/Interchange; mode PvE; Wedge et Priest correctement nuancés';
  });
  await context.close();
}

async function testBossProfile(browser) {
  const { context, page } = await visit(browser, 'pages/bosses/partisan.html');
  await check('Partisan · 25 % base, 4 cartes, condition de karma et onglet Seasonal', async () => {
    const text = await page.locator('main').innerText();
    assert(text.includes('25 %') && text.includes('chance de base'), 'la chance BSG de base est absente ou présentée sans qualification');
    assert(text.includes('Customs') && text.includes('Woods') && text.includes('Shoreline') && text.includes('Lighthouse'), 'les quatre cartes BSG ne sont pas toutes listées');
    assert(text.includes('faible karma'), 'condition de karma faible absente');
    assert(await page.locator('#boss-profile-panel').isVisible(), 'panneau de mode non visible après JS');
    await page.locator('[data-p6-mode-tab="pvp-season"]').click();
    assert((await page.locator('#boss-profile-panel').innerText()).includes('Seasonal'), 'la note Seasonal ne dit pas que le taux final est modulé');
    const rawHealth = await page.locator('#sante').innerText();
    assert(rawHealth.includes('950 HP') && rawHealth.includes('n’a pas été vérifié dans le client'), 'HP wiki pas attribué comme tel');
    return 'chance BSG et HP communautaire séparés; mode Seasonal explicite';
  });
  await context.close();
}

async function testSearch(browser) {
  const { context, page } = await visit(browser, '');
  await check('Recherche globale · index Phase 6 consultable depuis l’accueil', async () => {
    const trigger = page.locator('[data-site-search-trigger]');
    assert(await trigger.isVisible(), 'bouton de recherche non activé');
    await trigger.click();
    const dialog = page.locator('#site-search');
    await dialog.locator('[data-search-input]').fill('Partisan');
    await page.waitForFunction(() => document.querySelectorAll('[data-search-results] a').length > 0, null, { timeout: 10000 });
    const names = await dialog.locator('[data-search-results] .search-results__name').allInnerTexts();
    assert(names.some((name) => name.includes('Partisan')), `résultat Boss Partisan absent: ${names.join(', ')}`);
    return `recherche locale retournant ${names.length} résultats`;
  });
  await context.close();
}

async function testNoJavaScript(browser) {
  const representative = ['pages/armor/', 'pages/armor/body-armor.html', 'pages/bosses/', 'pages/bosses/partisan.html', 'pages/armor/armor-chart.html'];
  for (const route of representative) {
    try {
      const { context, page } = await visit(browser, route, { javaScriptEnabled: false });
      const data = await page.evaluate(() => ({
        h1: document.querySelectorAll('h1').length,
        armorRows: document.querySelectorAll('[data-p6-item-row]').length,
        bosses: document.querySelectorAll('[data-p6-boss-row]').length,
        filterHidden: [...document.querySelectorAll('[data-p6-filter-form],[data-p6-chart-form],[data-p6-boss-controls]')].every((el) => el.hidden),
        fallbackVisible: [...document.querySelectorAll('[data-p6-mode-fallback]')].every((el) => !el.hidden && getComputedStyle(el).display !== 'none'),
        canonical: Boolean(document.querySelector('link[rel="canonical"]')),
      }));
      const pass = data.h1 === 1 && data.filterHidden && data.fallbackVisible && !data.canonical && (route.includes('bosses') ? data.bosses === 15 || data.bosses === 0 : data.armorRows > 0 || route.includes('armor-chart'));
      record(`Sans JavaScript · ${route} · HTML et commandes non trompeuses`, pass, data);
      await context.close();
    } catch (error) { record(`Sans JavaScript · ${route}`, false, error.message); }
  }
}

async function testResponsive(browser) {
  const representative = ['pages/armor/', 'pages/armor/body-armor.html', 'pages/armor/helmets.html', 'pages/bosses/', 'pages/bosses/partisan.html'];
  for (const route of representative) {
    const { context, page } = await visit(browser, route, { width: 1440, height: 900 });
    const widths = [];
    for (const width of [320, 375, 768, 1024, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      await page.waitForTimeout(35);
      widths.push(await page.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth, body: document.body.scrollWidth })));
    }
    const failed = widths.filter((x) => x.document > x.viewport + 1 || x.body > x.viewport + 1);
    result.responsive.push({ route, widths, pass: failed.length === 0 });
    record(`Reflow ${route} · 320–1440 px`, !failed.length, failed.length ? failed : widths);
    await context.close();
  }
}

async function testNoPreviewCanonicalAndLinks(browser) {
  const { context, page } = await visit(browser, 'pages/bosses/');
  await check('Routes Phase 6 · mêmes origines et ressources servies par liste blanche', async () => {
    const paths = await page.evaluate(() => [...document.querySelectorAll('a[href]')].map((a) => new URL(a.href).href).filter((url) => url.startsWith(location.origin)).map((url) => new URL(url).pathname).filter((url) => url.includes('/pages/armor/') || url.includes('/pages/bosses/')));
    const unique = [...new Set(paths)];
    for (const pathname of unique) {
      const response = await page.request.get(`${BASE}${pathname}`);
      assert(response.status() === 200, `${pathname} → ${response.status()}`);
    }
    for (const asset of ['/css/pages/phase6.css', '/js/phase6.js', '/data/snapshots/phase-6-armor-2026-11-18.json']) {
      const response = await page.request.get(`${BASE}${asset}`);
      assert(response.status() === 200, `${asset} → ${response.status()}`);
    }
    return `${unique.length} liens internes et 3 ressources servies`;
  });
  await context.close();
}

async function main() {
  let c, f;
  try {
    c = await chromium.launch({ headless: true });
    result.browser.chromium = c.version();
    for (const route of routes) await auditRoute(c, route, 'Chromium', true);
    await testArmorFilters(c);
    await testArmorSubpages(c);
    await testArmorChart(c);
    await testBossHub(c);
    await testBossProfile(c);
    await testSearch(c);
    await testNoJavaScript(c);
    await testResponsive(c);
    await testNoPreviewCanonicalAndLinks(c);
  } catch (error) { record('Exécution Chromium', false, error.stack || error.message); }
  finally { if (c) await c.close(); }
  try {
    f = await firefox.launch({ headless: true });
    result.browser.firefox = f.version();
    for (const route of ['pages/armor/', 'pages/armor/body-armor.html', 'pages/armor/helmets.html', 'pages/armor/rigs.html', 'pages/armor/armor-chart.html', 'pages/bosses/', 'pages/bosses/partisan.html', 'pages/bosses/the-wedge.html']) await auditRoute(f, route, 'Firefox', false);
    await testArmorFilters(f);
    await testArmorChart(f);
    await testBossHub(f);
  } catch (error) { record('Exécution Firefox', false, error.stack || error.message); }
  finally { if (f) await f.close(); }
  result.status = errors.length ? 'ECHEC' : 'VALIDE';
  result.errors = errors;
  result.finishedAt = new Date().toISOString();
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, `${JSON.stringify(result, null, 2)}\n`);
  console.log(`\n${result.status} · ${result.checks.filter((item) => item.passed).length}/${result.checks.length} contrôles · ${routes.length} routes Chromium + 8 Firefox · ${path.relative(ROOT, OUT)}`);
  if (errors.length) process.exitCode = 1;
}
main();
