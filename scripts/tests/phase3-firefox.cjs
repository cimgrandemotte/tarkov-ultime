/* Contre-test des nouvelles pages sur Firefox (viewport mobile CSS). */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');
const { firefox }=require('playwright');
const origin=process.env.TUG_HOME_URL || 'http://127.0.0.1:4180/';
const starter='pages/getting-started.html', lore='pages/lore/';
const ready='html[data-app-ready][data-guides-ready]';
const abs=(target)=>new URL(target,origin).href;
const checks=[];
async function group(name,fn){ await fn(); checks.push(name); console.log(`OK · ${name}`); }
async function main(){
  const browser=await firefox.launch();
  try {
    const page=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
    page.setDefaultTimeout(12000);
    const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`);});
    async function open(ref){ assert((await page.goto(abs(ref))).ok()); await page.locator(ready).waitFor(); await page.evaluate(()=>document.fonts.ready); }
    await group('Débutant, reflow mobile et éléments d’introduction',async()=>{
      await open(starter);
      assert(await page.evaluate(()=>document.scrollingElement.scrollWidth<=innerWidth));
      assert.equal(await page.locator('.raid-step').count(),10);
    });
    await group('Onglets PMC/Scav au clavier',async()=>{
      await page.locator('#profile-pmc-tab').press('ArrowRight');
      await page.waitForFunction(()=>document.activeElement.id==='profile-scav-tab');
      assert(await page.locator('#profile-scav').isVisible());
      await page.keyboard.press('Home');
      assert(await page.locator('#profile-pmc').isVisible());
    });
    await group('Check locale, rechargement et restauration',async()=>{
      await page.locator('[data-raid-check=goal]').press('Space');
      await page.reload(); await page.locator(ready).waitFor();
      assert(await page.locator('[data-raid-check=goal]').isChecked());
      await page.locator('[data-raid-reset]').press('Enter');
      assert(!(await page.locator('[data-raid-check=goal]').isChecked()));
    });
    await group('FAQ : accents, filtre et accordéon',async()=>{
      await page.locator('#faq-query').fill('securise');
      const item=page.locator('[data-faq-item]:visible');
      assert.equal(await item.count(),1);
      await item.locator('summary').press('Space');
      assert(await item.locator('p').isVisible());
    });
    await group('Recherche interpage depuis le bouton',async()=>{
      await page.locator('[data-site-search-trigger]').press('Enter');
      await page.locator('#site-query').fill('Norvinsk et TerraGroup');
      await page.locator('[data-search-results] a[href$="/pages/lore/#norvinsk"]').press('Enter');
      await page.waitForURL(abs(lore+'#norvinsk'));
      await page.locator(ready).waitFor();
      assert(await page.evaluate(()=>document.scrollingElement.scrollWidth<=innerWidth));
    });
    await group('Lore : spoilers fermés, ouverture volontaire au clavier puis fermeture',async()=>{
      const panel=page.locator('[data-campaign-spoiler]'), body=panel.locator('[data-nosnippet]');
      assert(!(await body.isVisible()));
      await panel.locator('summary').press('Space'); assert(await body.isVisible());
      await panel.locator('summary').press('Enter'); assert(!(await body.isVisible()));
    });
    assert.deepEqual(errors,[]);
    const report={schemaVersion:1,status:'VALIDE',browser:`Firefox ${browser.version()}`,checkedAt:new Date().toISOString(),viewportCssPx:390,checks};
    await fs.writeFile(path.resolve(__dirname,'../../data/snapshots/validation-phase-3-firefox.json'),JSON.stringify(report,null,2)+'\n');
  } finally {await browser.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
