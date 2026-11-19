/* PHASE_4 · captures de fond des heroes pour mesurer le texte posé sur l’image. */
'use strict';
const { chromium } = require('playwright');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const origin = new URL(process.env.TUG_HOME_URL || 'http://127.0.0.1:4180/');
const pages = { hub: 'pages/maps/', map: 'pages/maps/icebreaker.html' };
const selectors = ['.guide-hero .guide-kicker', '.guide-hero h1', '.guide-hero__lead', '.guide-hero__actions .button', '.guide-hero__note', '.guide-hero__locator'];
async function main() {
  const scratch = await fs.mkdtemp(path.join(os.tmpdir(), 'tug-map-colors-'));
  const browser = await chromium.launch();
  try {
    for (const [id, route] of Object.entries(pages)) {
      for (const width of [320, 390, 768, 1024, 1440]) {
        for (const theme of ['standard', 'renforce']) {
          const page = await browser.newPage({ viewport: { width, height: 1000 }, deviceScaleFactor: 1, reducedMotion: 'reduce' });
          try {
            const response = await page.goto(new URL(route, origin).href);
            if (!response?.ok()) throw new Error(`HTTP ${route}`);
            await page.locator('html[data-app-ready][data-maps-ready]').waitFor();
            await page.evaluate(async (contrast) => {
              if (contrast) document.documentElement.dataset.theme = 'contrast';
              await Promise.all([document.fonts.ready, document.querySelector('.guide-hero__image').decode()]);
            }, theme === 'renforce');
            const samples = await page.evaluate((targets) => {
              const result = [];
              for (const selector of targets) {
                for (const element of document.querySelectorAll(selector)) {
                  const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
                  while (walker.nextNode()) {
                    const node = walker.currentNode;
                    if (!/[A-Za-zÀ-ÿ0-9]/.test(node.textContent) || !node.parentElement.getClientRects().length) continue;
                    const range = document.createRange();
                    range.selectNodeContents(node);
                    const rects = [...range.getClientRects()].map((r) => [r.left, r.top, r.right, r.bottom]).filter(([l, t, r, b]) => r > l && b > t);
                    if (rects.length) result.push({ label: node.textContent.trim(), color: getComputedStyle(node.parentElement).color, rects, selector });
                  }
                }
              }
              return result;
            }, selectors);
            if (!samples.length) throw new Error(`Aucun échantillon texte : ${id} ${width} ${theme}`);
            const tag = path.join(scratch, `${id}-${width}-${theme}`);
            await fs.writeFile(`${tag}.json`, JSON.stringify({ route, width, theme, samples }));
            const text = selectors.flatMap((selector) => [selector, `${selector} *`]).join(',');
            await page.addStyleTag({ content: `${text} { color: transparent !important; text-decoration-color: transparent !important; text-shadow: none !important; }` });
            await page.screenshot({ type: 'jpeg', quality: 100, path: `${tag}.jpg` });
          } finally {
            await page.close();
          }
        }
      }
    }
    const python = spawnSync(process.env.PYTHON || 'python3', [path.join(__dirname, 'phase4_colors.py'), scratch], { stdio: 'inherit' });
    if (python.error || python.status !== 0) throw python.error ?? new Error(`Mesure de contraste interrompue, code ${python.status}`);
  } finally {
    await browser.close();
    await fs.rm(scratch, { recursive: true, force: true });
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
