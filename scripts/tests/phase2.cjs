/* Accueil HTTP : navigateur, focus, interactions, SEO et budget de chargement. */
'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs/promises');
const { chromium } = require('playwright');
const axePath = require.resolve('axe-core/axe.min.js');
const origin = new URL(process.env.TUG_HOME_URL || 'http://127.0.0.1:4180/');
const ready = 'html[data-app-ready="true"][data-home-ready="true"]';
const trigger = '[data-site-search-trigger]';
const deck = '[data-audio-deck]';
const focus = (page, sel) => page.waitForFunction(s => document.activeElement?.matches(s), sel);
const matches = (page, sel, attr, value) => page.waitForFunction(([s,k,v]) => document.querySelector(s)?.getAttribute(k) === v, [sel,attr,value]);
const records = [], audits = [];
let initial, fastMobile;

async function group(name, test) {
  const start = Date.now();
  await test();
  records.push({ name, passed: true });
  console.log(`OK ${name} (${Date.now() - start} ms)`);
}
async function axe(page, context) {
  if (!(await page.evaluate(() => Boolean(window.axe)))) await page.addScriptTag({ path: axePath });
  const result = await page.evaluate(async () => {
    const r = await window.axe.run({runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}});
    return { violations:r.violations.map(x=>({id:x.id,selectors:x.nodes.map(y=>y.target)})),
             needsReview:r.incomplete.map(x=>({id:x.id,count:x.nodes.length})), passes:r.passes.length };
  });
  audits.push({context,...result});
  assert.deepEqual(result.violations, [], `Audit ${context}`);
}
const metricInit = () => {
  window.qaMetrics = {lcp:null, cls:0, shifts:[]};
  new PerformanceObserver(l => { for(const x of l.getEntries()) window.qaMetrics.lcp = x.startTime; }).observe({type:'largest-contentful-paint',buffered:true});
  new PerformanceObserver(l => { for(const x of l.getEntries()) if(!x.hadRecentInput) {
    window.qaMetrics.cls += x.value;
    window.qaMetrics.shifts.push({t:Math.round(x.startTime),v:x.value,sources:x.sources.map(s=>s.node?.className || s.node?.nodeName)});
  } }).observe({type:'layout-shift',buffered:true});
};
async function resources(page) {
  return page.evaluate(() => ({
    count:performance.getEntriesByType('resource').length,
    transferBytes:Math.round(performance.getEntriesByType('resource').reduce((a,x)=>a+x.transferSize,0)),
    lcpMs:Math.round(window.qaMetrics?.lcp || 0), cls:Math.round(window.qaMetrics?.cls*1000)/1000,
    ...(window.qaMetrics?.shifts.length ? {shifts: window.qaMetrics.shifts} : {}),
  }));
}
async function checkWidth(page, description) {
  const fit = await page.evaluate(() => ({ viewport:innerWidth, width:document.scrollingElement.scrollWidth }));
  assert(fit.width <= fit.viewport + 1, `${description} déborde : ${JSON.stringify(fit)}`);
}

async function main() {
  const browser = await chromium.launch();
  async function visit(options, test, { networkError = false } = {}) {
    const ctx = await browser.newContext({viewport:{width:1440,height:960},reducedMotion:'reduce', ...options});
    try {
      const page = await ctx.newPage();
      page.setDefaultTimeout(8000);
      const failures=[], requests=[];
      page.on('pageerror',e=>failures.push(e.message));
      const httpErrors=[];
      page.on('response',r=> { if(r.status()>=400) httpErrors.push(`${r.status()} ${r.url()}`); });
      page.on('request',r=>requests.push(r.url()));
      const open = async(part = './') => {
        const response = await page.goto(new URL(part,origin).href);
        assert(response.ok());
        if(options.javaScriptEnabled !== false) await page.locator(ready).waitFor();
        await page.evaluate(()=>document.fonts.ready);
      };
      await test(page, open, requests, ctx);
      assert.deepEqual(failures, [], 'Erreurs JS');
      if(!networkError) assert.deepEqual(httpErrors, [], 'Erreurs réseau');
    } finally { await ctx.close(); }
  }

  try {
    await group('Aperçu HTTP : HTML, ressources autorisées, isolement, plages MP3 et SEO', async () => {
      const home = await fetch(origin);
      assert.equal(home.status,200);
      assert.equal(home.headers.get('x-robots-tag'),'noindex, nofollow');
      assert.equal(home.headers.get('x-content-type-options'),'nosniff');
      const text = await home.text();
      const canonical = text.match(/<link rel="canonical" href="(https:\/\/[^\"]+)"/)[1];
      assert.equal((await fetch(new URL('./index.html',origin))).status,200);
      assert.match(await (await fetch(new URL('./sitemap.xml',origin))).text(), /<urlset[^>]+>\s*<url><loc>https:\/\//);
      assert((await (await fetch(new URL('./robots.txt',origin))).text()).includes(new URL('sitemap.xml', canonical).href));
      for (const ref of ['workflow.json','state_machine.json','data/home.json','docs/phase-2.md','templates/index.html.in','scripts/serve_home.py','lab/','pages/maps/index.html','js/data/items.json','images/','audio/manifest.json']) {
        assert.equal((await fetch(new URL(ref,origin))).status,404,ref);
      }
      const media = new URL('./audio/ambient/ambient_city.mp3',origin);
      const range=await fetch(media,{headers:{Range:'bytes=0-95'}});
      assert.equal(range.status,206);
      assert.equal(range.headers.get('content-type'),'audio/mpeg');
      assert.match(range.headers.get('content-range'),/^bytes 0-95\/\d+$/);
      assert.equal((await range.arrayBuffer()).byteLength,96);
      assert.equal((await fetch(media,{headers:{Range:'bytes=99999999999999-'}})).status,416);
    });
    await group('Bureau : lecture initiale sans requête MP3 ni catalogue, SEO visible et audit', () => visit({},async(page,open,requests)=>{
      await page.addInitScript(metricInit);
      await open();
      await page.waitForLoadState('networkidle');
      assert(requests.every(url => new URL(url).origin===origin.origin));
      assert(!requests.some(url => /\.mp3(?:$|\?)|search-index|fuse\.basic|(?:items|ammo|weapons|armor)\.json|comparator\.js/.test(url)));
      assert(await page.locator('h1').textContent().then(t=>t.includes('Tarkov')));
      assert.equal(await page.locator('h1').count(),1);
      assert.equal(await page.locator('html').getAttribute('lang'),'fr');
      await page.locator('.home-hero__image').evaluate(el=>el.decode());
      assert(await page.evaluate(()=>document.fonts.check('800 32px Orbitron') && document.fonts.check('400 16px Inter')));
      initial=await resources(page);
      assert(initial.lcpMs>0 && initial.lcpMs<=2500 && initial.cls<=.1, JSON.stringify(initial));
      await axe(page,'Accueil 1440 px');
    }));
    await group('Clavier : lien d’évitement, méga-menu et accès directs Premier raid et Cartes', () => visit({},async(page,open)=>{
      await open();
      await page.keyboard.press('Tab');
      await focus(page,'.skip-link');
      await page.keyboard.press('Enter');
      await focus(page,'#main');
      await page.locator('.mega-menu__summary').press('Enter');
      await page.locator('.mega-menu[open] .mega-menu__item').first().waitFor();
      await page.keyboard.press('Tab');
      await focus(page,'.mega-menu__item');
      await page.keyboard.press('Escape');
      assert.equal(await page.locator('.mega-menu[open]').count(),0);
      await focus(page,'.mega-menu__summary');
      await page.locator('.home-cta').press('Enter');
      await page.waitForURL('**/#premier-raid');
      await focus(page,'#premier-raid');
      await page.locator('[data-back-top]').waitFor();
      await page.locator('[data-back-top]').press('Enter');
      await focus(page,'#top');
      assert.equal(await page.evaluate(()=>scrollY),0);
      await page.locator('.home-secondary').press('Enter');
      await page.waitForURL('**/#cartes');
      await focus(page,'#cartes');
      const top = await page.locator('#cartes').evaluate(el=>el.getBoundingClientRect().top);
      assert(top>=await page.locator('.site-header').evaluate(el=>el.getBoundingClientRect().bottom));
    }));
    await group('Mobile 390 px : menu tactile, groupes, focus et Échap à deux niveaux', () => visit({viewport:{width:390,height:844},hasTouch:true,isMobile:true},async(page,open)=>{
      await open();
      const button = page.locator('[data-nav-toggle]');
      const nav = page.locator('.site-nav');
      assert(!(await nav.isVisible()));
      await button.tap();
      assert.equal(await button.getAttribute('aria-expanded'),'true');
      await focus(page,'.site-nav__link[aria-current]');
      await page.locator('.mega-menu__summary').press('Enter');
      await axe(page,'Menu mobile et méga-menu ouverts');
      await page.keyboard.press('Escape');
      await focus(page,'.mega-menu__summary');
      await page.keyboard.press('Escape');
      await focus(page,'[data-nav-toggle]');
      assert.equal(await button.getAttribute('aria-expanded'),'false');
      await button.tap();
      await page.getByRole('navigation',{name:'Navigation principale'}).getByRole('link',{name:'Débuter',exact:true}).tap();
      await focus(page,'#premier-raid');
      assert(!(await nav.isVisible()));
    }));
    await group('Recherche : Ctrl/⌘+K, Fuse différé, coquille, états vide, boucle et restitution du focus', () => visit({},async(page,open,requests)=>{
      await open();
      await page.locator(trigger).focus();
      await page.keyboard.press('Control+k');
      await focus(page,'#site-query');
      await matches(page,'#site-search','data-search-provider','fuse');
      assert(requests.some(x=>x.endsWith('/js/data/search-index.json')));
      const q=page.locator('#site-query');
      await q.fill('équipement');
      await page.locator('[data-search-results] a[href$="#equipement"]').waitFor();
      await q.fill('tushonkaa');
      await page.locator('[data-search-results] a[href$="#tushonka"]').waitFor();
      await page.keyboard.press('ArrowDown');
      await focus(page,'[data-search-results] a');
      await page.keyboard.press('ArrowUp');
      await focus(page,'#site-query');
      await page.keyboard.press('Shift+Tab');
      await focus(page,'[data-modal-close]');
      await page.keyboard.press('Shift+Tab');
      await focus(page,'[data-search-results] li:last-child a');
      await q.fill('zzxyzzzqq');
      await page.locator('[data-search-status]').getByText('Aucun résultat.',{exact:false}).waitFor();
      await axe(page,'Recherche ouverte sans résultat');
      await page.keyboard.press('Escape');
      await focus(page,trigger);
      await page.keyboard.press('Meta+k');
      await focus(page,'#site-query');
      await q.fill('Cartes et extractions');
      await page.locator('[data-search-results] a[href$="#cartes"]').waitFor();
      await page.keyboard.press('Enter');
      await focus(page,'#cartes');
      await page.waitForURL('**/#cartes');
    }));
    await group('Annonces : filtres, état annoncé, lien profond depuis /index.html, sans rechargement', () => visit({},async(page,open,requests)=>{
      await open('./index.html');
      const news = page.locator('[data-news-type]:not([hidden])');
      assert.equal(await news.count(),6);
      await page.locator('[data-news-view=patchs]').click();
      assert.equal(await news.count(),2);
      assert.equal(await page.locator('[data-news-count]').textContent(),'2 annonces');
      assert.equal(await page.locator('[data-news-view=patchs]').getAttribute('aria-pressed'),'true');
      await page.locator(trigger).click();
      await page.locator('#site-query').fill('City Drops');
      await page.locator('[data-search-results] a[href$="#actu-drops"]').click();
      await focus(page,'#actu-drops');
      await page.waitForURL('**/index.html#actu-drops');
      assert.equal(await news.count(),6);
      assert.equal(requests.filter(x=>x.endsWith('/index.html')).length,1);
      await page.locator('[data-news-view=studio]').click();
      assert.equal(await page.locator('[data-news-count]').textContent(),'1 annonce');
      await page.evaluate(()=>{ location.hash = '#actu-halloween'; });
      await page.locator('#actu-halloween').waitFor();
      assert.equal(await news.count(),6);
    }));
    await group('Recherche : messages d’erreur et nouvel essai ; repli sans Fuse', () => visit({},async(page,open)=>{
      await page.route('**/fuse.basic.min.mjs',r=>r.abort());
      const oneShot = '**/js/data/search-index.json';
      await page.route(oneShot,r=>r.fulfill({status:503,body:'indisponible'}));
      await open();
      await page.locator(trigger).click();
      await page.locator('[data-search-status]').getByText('Index indisponible.',{exact:false}).waitFor();
      await page.keyboard.press('Escape');
      await page.unroute(oneShot);
      await page.locator(trigger).click();
      await matches(page,'#site-search','data-search-provider','local');
      await page.locator('#site-query').fill('tushonka');
      await page.locator('[data-search-results] a[href$="#tushonka"]').waitFor();
    },{networkError:true}));
    await group('Checklist : saisie locale, conservation, remise à zéro et focus', () => visit({},async(page,open)=>{
      await open();
      const first=page.locator('[data-raid-check=kit]');
      await first.press('Space');
      await page.locator('[data-raid-check=exit]').check();
      assert.equal(await page.locator('[data-raid-progress]').textContent(),'2/3 repères prêts');
      await page.reload();
      await page.locator(ready).waitFor();
      assert(await first.isChecked());
      assert.equal(await page.locator('[data-raid-progress]').textContent(),'2/3 repères prêts');
      await page.locator('[data-raid-reset]').press('Enter');
      await focus(page,'[data-raid-check=kit]');
      assert.equal(await page.locator('[data-raid-progress]').textContent(),'0/3 repères prêts');
    }));
    await group('Modes : sélection PvE/Saisonnier, flèches, Home/End, contraste', () => visit({},async(page,open)=>{
      await open();
      await page.locator('#mode-tab-pvp').focus();
      await page.keyboard.press('ArrowRight');
      await focus(page,'#mode-tab-season');
      assert(await page.locator('#mode-season').isVisible());
      await page.keyboard.press('End');
      await focus(page,'#mode-tab-pve');
      assert(!(await page.locator('#mode-pvp').isVisible()));
      assert(await page.locator('#mode-pve').isVisible());
      await page.locator('[data-contrast-toggle]').click();
      await matches(page,'html','data-theme','contrast');
      await axe(page,'Contraste renforcé, onglet PvE et cases interactives');
      await page.reload();
      await matches(page,'html','data-theme','contrast');
      assert.equal(await page.locator('[data-contrast-toggle]').getAttribute('aria-pressed'),'true');
    }));
    await group('Audio : premier geste, état accessible, volume mémorisé et changement à l’arrêt', () => visit({},async(page,open,requests)=>{
      await open();
      const toggler=page.locator('.home-sound');
      const selection=page.locator('[data-audio-select]');
      const volume=page.locator('[data-audio-volume]');
      assert.equal(requests.some(x=>x.endsWith('.mp3')),false);
      await toggler.press('Enter');
      await matches(page,deck,'data-audio-state','playing');
      assert(requests.some(x=>x.endsWith('/ambient_city.mp3')));
      assert.match(await toggler.textContent(),/pause/);
      const old=await volume.getAttribute('aria-valuetext');
      await volume.press('ArrowRight');
      const saved=await volume.getAttribute('aria-valuetext');
      assert.notEqual(old,saved);
      await selection.selectOption('forest');
      await matches(page,deck,'data-audio-state','idle');
      assert.equal(requests.some(x=>x.endsWith('/ambient_forest.mp3')),false);
      await page.locator(`${deck} [data-audio-toggle]`).click();
      await matches(page,deck,'data-audio-state','playing');
      await page.locator(`${deck} [data-audio-toggle]`).click();
      await matches(page,deck,'data-audio-state','paused');
      await page.reload();
      await page.locator(ready).waitFor();
      assert.equal(await volume.getAttribute('aria-valuetext'),saved);
      await matches(page,deck,'data-audio-state','idle');
    }));
    await group('Audio : échec contrôlé avec message à l’emplacement du bouton', () => visit({},async(page,open)=>{
      await page.route('**/ambient_city.mp3',r=>r.fulfill({status:503,body:'indisponible'}));
      await open();
      await page.locator('.home-sound').click();
      await matches(page,deck,'data-audio-state','error');
      assert.match(await page.locator('[data-audio-error]').textContent(),/Piste introuvable/);
    },{networkError:true}));
    await group('Mouvements : effet plafonné, désactivation et prise en compte du système', () => visit({reducedMotion:'no-preference'},async(page,open)=>{
      await open();
      await matches(page,'[data-motion-hero]','data-motion-visible','true');
      await page.evaluate(()=>scrollTo(0,240));
      await page.waitForFunction(()=>parseFloat(document.querySelector('.home-hero').style.getPropertyValue('--parallax-shift'))>0);
      await page.locator('[data-motion-toggle]').click();
      assert.equal(await page.locator('[data-motion-toggle]').getAttribute('aria-pressed'),'true');
      await matches(page,'html','data-motion','reduce');
      await page.waitForFunction(()=>document.querySelector('.home-hero').style.getPropertyValue('--parallax-shift')==='0px');
      await page.locator('[data-motion-toggle]').click();
      await page.emulateMedia({reducedMotion:'reduce'});
      await page.evaluate(()=>scrollTo(0,200));
      await matches(page,'[data-motion-hero]','data-motion-visible','false');
      assert.equal(await page.locator('.particles__drop').first().evaluate(e=>getComputedStyle(e).animationName),'none');
    }));
    await group('Reflow 320 à 1440 px, agrandissement 200 %, jamais de défilement horizontal', () => visit({},async(page,open)=>{
      await open();
      for (const width of [320,375,390,576,768,831,832,1024,1440]) {
        await page.setViewportSize({width,height:900});
        await checkWidth(page,`${width}`);
        if (width<=831) {
          await page.locator('[data-nav-toggle]').click();
          await page.locator('.mega-menu__summary').press('Enter');
          await checkWidth(page,`${width} menu ouvert`);
          await page.keyboard.press('Escape');
          await page.keyboard.press('Escape');
        }
      }
      await page.addStyleTag({content:'html { font-size: 200%; }'});
      for (const width of [768,832,1024,1440]) {
        await page.setViewportSize({width,height:960});
        await checkWidth(page,`${width} police 200 %`);
      }
      await page.locator(trigger).click();
      await page.locator('[data-search-results] li').first().waitFor();
      await checkWidth(page,'Recherche à 200 %');
    }));
    await group('Sans JavaScript : navigation, toutes les annonces, modes, liens et audio natif', () => visit({javaScriptEnabled:false,viewport:{width:320,height:720}},async(page,open,requests)=>{
      await open();
      await checkWidth(page,'Mobile sans JS');
      assert(await page.locator('.site-nav').isVisible());
      assert(!(await page.locator(trigger).isVisible()));
      assert.equal(await page.locator('[data-news-type]:visible').count(),6);
      for (const id of ['pvp','season','pve']) assert(await page.locator('#mode-'+id).isVisible());
      assert(await page.locator('[data-audio-fallback]').isVisible());
      assert.equal(await page.locator('[data-audio-fallback]').getAttribute('preload'),'none');
      assert(!requests.some(x=>x.endsWith('.mp3')));
      await page.locator('.mega-menu__summary').click();
      await page.locator('.mega-menu__item[href="#cartes"]').click();
      await page.waitForURL('**/#cartes');
      await checkWidth(page,'Menu natif sans JS');
    }));
    await group('Couleurs système : repères de contrôle et navigation lisibles', () => visit({forcedColors:'active',viewport:{width:390,height:844}},async(page,open)=>{
      await open();
      assert.match(await page.evaluate(()=>String(matchMedia('(forced-colors: active)').matches)),/true/);
      assert(!(await page.locator('.home-hero__image').isVisible()));
      await page.locator('[data-news-view=evenements]').click();
      const picked = await page.locator('[data-news-view=evenements]').evaluate(el=>getComputedStyle(el).outlineStyle);
      assert.equal(picked,'solid');
      await axe(page,'Couleurs forcées à 390 px');
    }));
    await group('Chargement mobile simulé : RTT 100 ms, 4 Mbit/s descendant, CPU ×4', () => visit({viewport:{width:390,height:844},isMobile:true,hasTouch:true},async(page,open,_requests,ctx)=>{
      await page.addInitScript(metricInit);
      const cd=await ctx.newCDPSession(page);
      await cd.send('Network.enable');
      await cd.send('Network.setCacheDisabled',{cacheDisabled:true});
      await cd.send('Network.emulateNetworkConditions',{offline:false,latency:100,downloadThroughput:500000,uploadThroughput:200000,connectionType:'cellular4g'});
      await cd.send('Emulation.setCPUThrottlingRate',{rate:4});
      await open();
      await page.waitForLoadState('networkidle');
      fastMobile=await resources(page);
      assert(fastMobile.lcpMs>0 && fastMobile.lcpMs<=2500 && fastMobile.cls<=.1,JSON.stringify(fastMobile));
    }));
    const evidence={schemaVersion:1,status:'VALIDE',browser:`Chromium ${browser.version()}`,checkedAt:new Date().toISOString(),
                    results:records,audits,performance:{initial,fastMobile},widths:[320,375,390,576,768,831,832,1024,1440]};
    await fs.writeFile(process.env.TUG_QA_REPORT || path.resolve(__dirname,'../../data/snapshots/validation-phase-2.json'),JSON.stringify(evidence,null,2)+'\n');
    console.log('Performance',JSON.stringify(evidence.performance));
  } finally { await browser.close(); }
}
main().catch(error=>{console.error(error);process.exitCode=1;});
