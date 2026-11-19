#!/usr/bin/env node
/** Local Chromium, responsive, no-JS, interaction and axe-core QA for PHASE_10. */
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

const BASE = (process.env.PHASE10_BASE_URL || 'http://127.0.0.1:4190').replace(/\/$/, '');
const ROOT = path.resolve(__dirname, '..');
const REPORT = path.join(ROOT, 'data/snapshots/validation-phase-10.json');
const AXE = require.resolve('axe-core/axe.min.js');
const routes = [
  { id: 'patches', url: '/pages/patch-notes.html', title: 'Notes de patch & chronologie' },
  { id: 'resources', url: '/pages/resources/', title: 'Ressources & outils' },
  { id: 'glossary', url: '/pages/resources/glossary.html', title: 'Glossaire EFT — anglais / français' },
];
const report = { phase: 'PHASE_10', base: BASE, routes: [], interactions: [], responsive: [], accessibility: [], noJavaScript: null, errors: [] };

function assert(condition, message) { if (!condition) throw new Error(message); }
function record(collection, name, detail) { collection.push({ name, ...detail }); }

async function main() {
  const browser = await chromium.launch({ headless: true });
  try {
    for (const route of routes) {
      const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
      const pageErrors = [];
      const failed = [];
      page.on('pageerror', error => pageErrors.push(error.message));
      page.on('console', message => { if (message.type() === 'error') pageErrors.push(`console: ${message.text()}`); });
      page.on('requestfailed', request => failed.push(`${request.method()} ${request.url()} · ${request.failure()?.errorText}`));
      const response = await page.goto(BASE + route.url, { waitUntil: 'networkidle' });
      assert(response && response.status() === 200, `${route.id}: HTTP ${response?.status() ?? 'no response'}`);
      assert((await page.locator('h1').count()) === 1, `${route.id}: exactly one H1 expected`);
      assert((await page.locator('h1').innerText()).includes(route.title), `${route.id}: H1/title mismatch`);
      assert((await page.locator('html').getAttribute('lang')) === 'fr-FR', `${route.id}: lang should be fr-FR`);
      assert((await page.locator('meta[name="description"]').count()) === 1, `${route.id}: description missing`);
      assert((await page.locator('meta[name="robots"]').getAttribute('content')) === 'noindex,follow', `${route.id}: preview should be noindex`);
      assert((await page.locator('link[rel="canonical"]').count()) === 0, `${route.id}: preview must not contain canonical`);
      assert(await page.locator('.guide-hero__image').evaluate(img => img.complete && img.naturalWidth > 0 && !!img.alt), `${route.id}: hero failed to load or lacks alt`);
      record(report.routes, route.id, { status: response.status(), title: route.title, heroLoaded: true });

      if (route.id === 'patches') {
        const year = page.locator('[data-p10-timeline-year]');
        const kind = page.locator('[data-p10-timeline-kind]');
        await year.selectOption('2026');
        await kind.selectOption('roadmap');
        let count = await page.locator('[data-p10-timeline-card]:visible').count();
        assert(count === 1, `timeline 2026/roadmap should show one card, got ${count}`);
        const status = await page.locator('[data-p10-timeline-count]').innerText();
        assert(status.includes('1 sur 20'), `timeline live status unexpected: ${status}`);
        await year.selectOption('all');
        await kind.selectOption('all');
        count = await page.locator('[data-p10-timeline-card]:visible').count();
        assert(count === 20, `timeline reset should show 20 cards, got ${count}`);
        record(report.interactions, 'timeline filters', { filtered: 1, reset: count, status });
      }

      if (route.id === 'resources') {
        const purpose = page.locator('[data-p10-resource-purpose]');
        const trust = page.locator('[data-p10-resource-trust]');
        const query = page.locator('[data-p10-resource-query]');
        await purpose.selectOption('maps');
        let count = await page.locator('[data-p10-resource-card]:visible').count();
        assert(count === 2, `maps filter should show two resources, got ${count}`);
        await trust.selectOption('community-tool');
        count = await page.locator('[data-p10-resource-card]:visible').count();
        assert(count === 1, `map + community tool should show one resource, got ${count}`);
        await query.fill('MapGenie');
        count = await page.locator('[data-p10-resource-card]:visible').count();
        assert(count === 1, `MapGenie search should show one resource, got ${count}`);
        const status = await page.locator('[data-p10-resource-count]').innerText();
        await purpose.selectOption('all'); await trust.selectOption('all'); await query.fill('');
        const reset = await page.locator('[data-p10-resource-card]:visible').count();
        assert(reset === 17, `resource reset should show 17, got ${reset}`);
        record(report.interactions, 'resource purpose/trust/search/reset', { maps: 2, combined: 1, query: count, reset, status });
      }

      if (route.id === 'glossary') {
        const query = page.locator('[data-p10-glossary-query]');
        const group = page.locator('[data-p10-glossary-group]');
        const reset = page.locator('[data-p10-glossary-reset]');
        let count = await page.locator('[data-p10-glossary-item]:visible').count();
        assert(count === 314, `glossary should start with 314 visible terms, got ${count}`);
        await query.fill('desync');
        count = await page.locator('[data-p10-glossary-item]:visible').count();
        assert(count > 0 && count < 314, `desync search returned ${count}`);
        await query.fill('');
        await group.selectOption({ label: 'Armes & combat' });
        const groupCount = await page.locator('[data-p10-glossary-item]:visible').count();
        assert(groupCount === 65, `Armes & combat should have 65 terms, got ${groupCount}`);
        await reset.click();
        count = await page.locator('[data-p10-glossary-item]:visible').count();
        assert(count === 314, `glossary reset should show 314, got ${count}`);
        const t = page.locator('[data-p10-letter="T"]');
        await t.focus(); await page.keyboard.press('Enter');
        const letterCount = await page.locator('[data-p10-glossary-item]:visible').count();
        assert(letterCount === 17, `letter T should show 17 terms, got ${letterCount}`);
        assert(await t.getAttribute('aria-pressed') === 'true', 'alphabet button must expose its pressed state');
        await page.locator('[data-p10-letter="all"]').click();
        count = await page.locator('[data-p10-glossary-item]:visible').count();
        assert(count === 314, `alphabet reset should show 314, got ${count}`);
        record(report.interactions, 'glossary search/group/reset/keyboard alphabet', { initial: 314, search: 'desync', group: groupCount, letterT: letterCount, reset: count });
      }

      for (const width of [320, 390, 768, 1280, 1440]) {
        await page.setViewportSize({ width, height: 900 });
        const dimensions = await page.evaluate(() => ({ client: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth }));
        assert(dimensions.scroll <= dimensions.client + 1, `${route.id}: horizontal overflow at ${width}px (${JSON.stringify(dimensions)})`);
        record(report.responsive, `${route.id} · ${width}px`, dimensions);
      }

      await page.setViewportSize({ width: 1440, height: 1000 });
      await page.addScriptTag({ path: AXE });
      const axe = await page.evaluate(async () => {
        const result = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'] } });
        return result.violations.map(v => ({ id: v.id, impact: v.impact, help: v.help, targets: v.nodes.slice(0, 12).map(n => n.target) }));
      });
      assert(axe.length === 0, `${route.id}: axe violations: ${axe.map(v => v.id).join(', ')}`);
      record(report.accessibility, route.id, { engine: 'axe-core', violations: axe.length });
      assert(pageErrors.length === 0, `${route.id}: browser errors: ${pageErrors.slice(0, 5).join(' | ')}`);
      assert(failed.length === 0, `${route.id}: failed requests: ${failed.slice(0, 5).join(' | ')}`);
      await page.close();
    }

    report.noJavaScript = [];
    const noJsExpectations = [
      { route: '/pages/patch-notes.html', selector: '[data-p10-timeline-card]', expected: 20, controls: '[data-p10-timeline-controls]' },
      { route: '/pages/resources/', selector: '[data-p10-resource-card]', expected: 17, controls: '[data-p10-resource-controls]' },
      { route: '/pages/resources/glossary.html', selector: '[data-p10-glossary-item]', expected: 314, controls: '[data-p10-glossary-controls]' },
    ];
    for (const item of noJsExpectations) {
      const noJs = await browser.newPage({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
      const noJsResponse = await noJs.goto(BASE + item.route, { waitUntil: 'networkidle' });
      assert(noJsResponse && noJsResponse.status() === 200, `no-JS ${item.route} HTTP ${noJsResponse?.status()}`);
      const visible = await noJs.locator(`${item.selector}:visible`).count();
      assert(visible === item.expected, `no-JS ${item.route} should display ${item.expected} entries, got ${visible}`);
      assert(await noJs.locator(item.controls).isHidden(), `no-JS ${item.route} filters should stay hidden`);
      if (item.route.includes('glossary')) assert(await noJs.locator('[data-p10-alpha]').isHidden(), 'no-JS alphabet controls should stay hidden');
      report.noJavaScript.push({ route: item.route, visible, expected: item.expected, filtersHidden: true });
      await noJs.close();
    }
  } catch (error) {
    report.errors.push(error.stack || error.message);
  } finally {
    await browser.close();
  }

  report.status = report.errors.length ? 'FAIL' : 'PASS';
  fs.mkdirSync(path.dirname(REPORT), { recursive: true });
  fs.writeFileSync(REPORT, JSON.stringify(report, null, 2) + '\n');
  console.log(`PHASE_10 browser QA · ${report.status}`);
  console.log(`${report.routes.length} routes · ${report.interactions.length} interaction groups · ${report.responsive.length} responsive checks · ${report.accessibility.length} axe audits · no-JS ${report.noJavaScript ? 'PASS' : 'FAIL'}`);
  console.log(`Report: ${path.relative(ROOT, REPORT)}`);
  if (report.errors.length) { for (const error of report.errors) console.error(error); process.exitCode = 1; }
}

main().catch(error => { console.error(error); process.exit(1); });
