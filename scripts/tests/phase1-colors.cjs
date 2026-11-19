/* Contrastes du texte sur le hero : échantillonnage local, avec Pillow côté Python. */
'use strict';
const { chromium } = require('playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const { spawnSync } = require('node:child_process');
const selector = '.lab-hero .breadcrumb li,.lab-hero .eyebrow,.lab-hero__heading,.lab-hero__intro,.lab-hero__transmit,.lab-hero__meta';

async function main() {
  const destination = await fs.mkdtemp(path.join(os.tmpdir(), 'tug-contrast-'));
  let browser;
  try {
    browser = await chromium.launch();
    for (const width of [320, 390, 768, 1024, 1440]) for (const contrast of [false, true]) {
      const page = await browser.newPage({ viewport: { width, height: 960 }, reducedMotion: 'reduce', deviceScaleFactor: 1 });
      await page.goto(process.env.TUG_LAB_URL || 'http://127.0.0.1:4173/lab/');
      await page.locator(':root[data-app-ready]').waitFor();
      await page.evaluate(() => document.fonts.ready);
      if (contrast) await page.evaluate(() => { document.documentElement.dataset.theme = 'contrast'; });
      const text = await page.evaluate((s) => {
        const samples = new Map();
        for (const el of document.querySelectorAll(s)) {
          const visitor = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
          while (visitor.nextNode()) {
            const item = visitor.currentNode;
            const label = item.data.trim();
            if (!label || samples.has(item) || !item.parentElement.getClientRects().length) continue;
            const range = new Range();
            range.selectNodeContents(item);
            const rects = [...range.getClientRects()].map((r) => [r.left, r.top, r.right, r.bottom]).filter(([x, y, r, b]) => r > x && b > y);
            if (rects.length) samples.set(item, { label, color: getComputedStyle(item.parentElement).color, rects });
          }
        }
        return [...samples.values()];
      }, selector);
      const stem = `${width}-${contrast ? 'renforce' : 'standard'}`;
      await fs.writeFile(path.join(destination, `${stem}.json`), JSON.stringify(text));
      const css = selector.split(',').flatMap((sel) => [sel, `${sel} *`]).join(',');
      await page.addStyleTag({ content: `${css} { color: transparent!important; }` });
      await page.screenshot({ type: 'jpeg', path: path.join(destination, `${stem}.jpg`), quality: 100 });
      await page.close();
    }
    const helper = path.resolve(__dirname, 'phase1_colors.py');
    const run = spawnSync(process.env.PYTHON || 'python3', [helper, destination], { stdio: 'inherit' });
    if (run.error || run.status !== 0) throw run.error ?? new Error(`Contraste : sortie ${run.status}`);
  } finally {
    await browser?.close();
    await fs.rm(destination, { force: true, recursive: true });
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
