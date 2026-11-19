/* Fonds photographiques et dégradés de l'accueil : boîtes de texte + prélèvement couleur. */
'use strict';
const { chromium } = require('playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const { spawnSync } = require('node:child_process');
const selectors = ['.home-hero__kicker','.home-hero__title','.home-hero__tagline','.home-hero__intro','.home-hero__actions .button',
  '.home-hero__signals','.home-hero__locator','.home-metrics__item','.dossier-tile__label','.dossier-tile__body h3','.dossier-tile__body p',
  '.home-section__head','.patch-panel h3','.patch-panel__eyebrow','.patch-panel__version','.patch-panel__date','.patch-panel__rows',
  '.patch-panel__link','.patch-panel__note','.first-raid__visual figcaption','.news-feed__pills','.news-row__status'];
async function main() {
  const out = await fs.mkdtemp(path.join(os.tmpdir(),'tug-home-colors-'));
  let browser;
  try {
    browser = await chromium.launch();
    for (const width of [320,390,768,1024,1440]) for(const high of [false,true]) {
      const page = await browser.newPage({viewport:{width,height:960},reducedMotion:'reduce',deviceScaleFactor:1});
      await page.goto(process.env.TUG_HOME_URL || 'http://127.0.0.1:4180/');
      await page.locator('html[data-app-ready][data-home-ready]').waitFor();
      await page.evaluate(async high=>{
        if(high)document.documentElement.dataset.theme='contrast';
        const photos=[...document.images];
        for(const img of photos)img.loading='eager';
        await Promise.all([document.fonts.ready,...photos.map(el=>el.decode())]);
      }, high);
      const snapshot=await page.evaluate(selectors=>{
        const seen=new Set();
        const samples=[];
        for(const selector of selectors) for(const el of document.querySelectorAll(selector)) {
          const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
          while(walker.nextNode()) {
            const node=walker.currentNode;
            const label=node.textContent.trim();
            if(seen.has(node) || !/[A-Za-zÀ-ÿ0-9]/.test(label))continue;
            if(node.parentElement.closest('.sr-only') || !node.parentElement.getClientRects().length) continue;
            const range=document.createRange();
            range.selectNodeContents(node);
            const rects=[...range.getClientRects()].map(r=>[r.left,r.top+scrollY,r.right,r.bottom+scrollY]).filter(([x,y,r,b])=>r>x&&b>y);
            if(!rects.length)continue;
            seen.add(node);
            samples.push({selector,label,color:getComputedStyle(node.parentElement).color,rects});
          }
        }
        return samples;
      },selectors);
      const fragment=selectors.flatMap(s=>[s,`${s} *`]).join(',');
      const name=path.join(out,`${width}-${high?'renforce':'standard'}`);
      await fs.writeFile(`${name}.json`,JSON.stringify(snapshot));
      await page.addStyleTag({content:`${fragment} {color: transparent !important; text-decoration-color: transparent !important; text-shadow: none !important;}`});
      await page.screenshot({type:'jpeg',quality:100,fullPage:true,path:`${name}.jpg`});
      await page.close();
    }
    const py=spawnSync(process.env.PYTHON || 'python3',[path.join(__dirname,'phase2_colors.py'),out],{stdio:'inherit'});
    if(py.error || py.status!==0)throw py.error ?? new Error(`Contraste : code ${py.status}`);
  } finally {
    await browser?.close();
    await fs.rm(out,{recursive:true,force:true});
  }
}
main().catch(error=>{console.error(error);process.exitCode=1;});
