/* Contre-test Firefox mobile, notamment le focus natif et l'audio sur demande. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');
const {firefox}=require('playwright');
const origin=process.env.TUG_HOME_URL || 'http://127.0.0.1:4180/';
const focus=(p,s)=>p.waitForFunction(sel=>document.activeElement?.matches(sel),s);
const playing=(p,s)=>p.waitForFunction(state=>document.querySelector('[data-audio-deck]').dataset.audioState===state,s);

async function main() {
  const browser=await firefox.launch();
  try {
    const p=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
    p.setDefaultTimeout(15000);
    const requests=[],errors=[];
    p.on('request',r=>requests.push(r.url()));
    p.on('pageerror',e=>errors.push(e.message));
    p.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`);});
    await p.goto(origin);
    await p.locator('html[data-app-ready][data-home-ready]').waitFor();
    await p.evaluate(()=>document.fonts.ready);
    assert(await p.evaluate(()=>document.scrollingElement.scrollWidth<=innerWidth));
    await p.locator('[data-nav-toggle]').press('Enter');
    await focus(p,'a[aria-current=page]');
    await p.locator('.mega-menu__summary').press('Enter');
    await p.locator('.mega-menu__item[href="#cartes"]').press('Enter');
    await focus(p,'#cartes');
    await p.locator('[data-site-search-trigger]').press('Enter');
    await p.locator('#site-query').fill('tushonkaa');
    await p.locator('[data-search-results] a[href$="#tushonka"]').waitFor();
    await p.keyboard.press('Escape');
    await focus(p,'[data-site-search-trigger]');
    await p.locator('[data-raid-check=kit]').check();
    assert.equal(await p.locator('[data-raid-progress]').textContent(),'1/3 repère prêt');
    await p.locator('[data-news-view=patchs]').click();
    assert.equal(await p.locator('[data-news-type]:not([hidden])').count(),2);
    assert(!requests.some(x=>x.endsWith('.mp3')));
    const sound=p.locator('[data-audio-deck] [data-audio-toggle]');
    await sound.click();
    await playing(p,'playing');
    assert(requests.some(x=>x.endsWith('ambient_city.mp3')));
    await sound.click();
    await playing(p,'paused');
    assert.deepEqual(errors,[]);
    const report={schemaVersion:1,status:'VALIDE',browser:`Firefox ${browser.version()}`,checkedAt:new Date().toISOString(),viewportCssPx:390,
                 checks:['reflow','méga-menu et focus de destination','recherche Fuse et Échap','checklist','filtres éditoriaux','audio sur geste et pause']};
    await fs.writeFile(process.env.TUG_QA_REPORT || path.resolve(__dirname,'../../data/snapshots/validation-phase-2-firefox.json'),JSON.stringify(report,null,2)+'\n');
    console.log(`OK · ${report.browser} · ${report.checks.length} points à 390 px`);
  } finally { await browser.close(); }
}
main().catch(error=>{console.error(error);process.exitCode=1;});
