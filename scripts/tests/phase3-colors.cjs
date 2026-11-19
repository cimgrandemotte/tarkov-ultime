/* Les pixels composés des visuels principaux, sans la couleur du texte lui-même. */
'use strict';
const { chromium } = require('playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const { spawnSync } = require('node:child_process');
const routes = {starter:'pages/getting-started.html',lore:'pages/lore/'};
const origin = new URL(process.env.TUG_HOME_URL || 'http://127.0.0.1:4180/');
const selectors = ['.guide-hero .guide-kicker','.guide-hero h1','.guide-hero__lead','.guide-hero__actions .button','.guide-hero__note','.guide-hero__locator'];
async function main() {
  const out = await fs.mkdtemp(path.join(os.tmpdir(),'tug-guide-colors-'));
  let browser;
  try {
    browser = await chromium.launch();
    for (const [id,route] of Object.entries(routes)) for (const width of [320,390,768,1024,1440]) for (const theme of ['standard','renforce']) {
      const page = await browser.newPage({viewport:{width,height:1000},deviceScaleFactor:1,reducedMotion:'reduce'});
      try {
        await page.goto(new URL(route,origin).href);
        await page.locator('html[data-app-ready][data-guides-ready]').waitFor();
        await page.evaluate(async theme=>{
          if(theme==='renforce')document.documentElement.dataset.theme = 'contrast';
          await Promise.all([document.fonts.ready,document.querySelector('.guide-hero__image').decode()]);
        },theme);
        const samples = await page.evaluate(selectors=> {
          const boxes=[];
          for(const sel of selectors) for(const el of document.querySelectorAll(sel)) {
            const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
            while(walker.nextNode()) {
              const text=walker.currentNode;
              if(!/[A-Za-zÀ-ÿ0-9]/.test(text.textContent) || !text.parentElement.getClientRects().length) continue;
              const range=document.createRange(); range.selectNodeContents(text);
              const rects=[...range.getClientRects()].map(r=>[r.left,r.top,r.right,r.bottom]).filter(([l,t,r,b])=>r>l&&b>t);
              if(rects.length) boxes.push({label:text.textContent.trim(),color:getComputedStyle(text.parentElement).color,rects,selector:sel});
            }
          }
          return boxes;
        },selectors);
        const fragment=selectors.flatMap(s=>[s,`${s} *`]).join(',');
        const target=path.join(out,`${id}-${width}-${theme}`);
        await fs.writeFile(`${target}.json`, JSON.stringify({route,width,theme,samples}));
        await page.addStyleTag({content:`${fragment} {color: transparent !important; text-decoration-color: transparent !important; text-shadow: none !important;}`});
        await page.screenshot({type:'jpeg',quality:100,path:`${target}.jpg`});
      } finally { await page.close(); }
    }
    const py=spawnSync(process.env.PYTHON || 'python3',[path.join(__dirname,'phase3_colors.py'),out],{stdio:'inherit'});
    if(py.error || py.status!==0)throw py.error ?? new Error(`Contraste : code ${py.status}`);
  } finally {
    await browser?.close();
    await fs.rm(out,{recursive:true,force:true});
  }
}
main().catch(error=>{console.error(error);process.exitCode=1;});
