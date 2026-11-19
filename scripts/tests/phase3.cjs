/* Dossiers Phase 3 : contrôle Chromium HTTP, clavier, mobile, SEO, repli et QA. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const { chromium }=require('playwright');
const axePath=require.resolve('axe-core/axe.min.js');
const origin=new URL(process.env.TUG_HOME_URL || 'http://127.0.0.1:4180/');
const out=new URL('../../data/snapshots/validation-phase-3.json',`file://${__filename}`);
const starter='pages/getting-started.html', lore='pages/lore/', alias='pages/lore/index.html';
const guideReady='html[data-app-ready][data-guides-ready]';
const trigger='[data-site-search-trigger]';
const results='[data-search-results] a';
const campaign='[data-campaign-spoiler]';
const widths=[320,390,576,768,831,832,1024,1440];
const checks=[], audits=[], performance={};
const url=ref=>new URL(ref,origin).href;
const focus=(page,selector)=>page.waitForFunction(sel=>document.activeElement?.matches(sel),selector);
const qaAttr=(page,sel,key,expected)=>page.waitForFunction(([s,k,v])=>document.querySelector(s)?.getAttribute(k)===v,[sel,key,expected]);

async function group(name,fn) {
  const start=Date.now();
  await fn();
  checks.push({name,passed:true});
  console.log(`OK ${name} (${Date.now()-start} ms)`);
}
async function axe(page,context) {
  if (!(await page.evaluate(()=>Boolean(window.axe)))) await page.addScriptTag({path:axePath});
  const result=await page.evaluate(async()=>{
    const r=await window.axe.run({runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}});
    return {violations:r.violations.map(x=>({id:x.id,nodes:x.nodes.map(n=>n.target)})),review:r.incomplete.map(x=>({id:x.id,nodes:x.nodes.map(n=>n.target)})),passes:r.passes.length};
  });
  audits.push({context,...result});
  assert.deepEqual(result.violations,[],context);
}
async function fits(page, context) {
  const {width,viewport}=await page.evaluate(()=>({width:document.scrollingElement.scrollWidth,viewport:innerWidth}));
  assert(width<=viewport+1,`${context}: ${width}px > ${viewport}px`);
}
async function visibleAnchor(page, selector) {
  const [y,bottom]=await page.evaluate(sel=>[document.querySelector(sel).getBoundingClientRect().top,document.querySelector('.site-header').getBoundingClientRect().bottom],selector);
  assert(y>=bottom-1, `${selector} masqué par l’en-tête (ancre ${y}, en-tête ${bottom})`);
}
async function openSearch(page) {
  await page.locator(trigger).focus();
  await page.keyboard.press('Control+k');
  await focus(page,'#site-query');
  await qaAttr(page,'#site-search','data-search-provider','fuse');
  return page.locator('#site-query');
}
async function decodeMedia(page) {
  await page.evaluate(async()=>{ for(const img of document.images) img.loading='eager'; await Promise.all([...document.images].map(i=>i.decode())); });
}
const observeMetrics=()=>{
  window.qa={lcp:0,cls:0};
  new PerformanceObserver(list=>{for(const e of list.getEntries()) window.qa.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});
  new PerformanceObserver(list=>{for(const e of list.getEntries()) if(!e.hadRecentInput)window.qa.cls+=e.value;}).observe({type:'layout-shift',buffered:true});
};
async function metric(page) {
  await page.waitForLoadState('networkidle');
  const m=await page.evaluate(()=>{
    const list=performance.getEntriesByType('resource');
    return {lcpMs:Math.round(window.qa.lcp),cls:Math.round(window.qa.cls*1000)/1000,resources:list.length,transferBytes:list.reduce((a,p)=>a+p.transferSize,0)};
  });
  assert(m.lcpMs>0 && m.lcpMs<=2500 && m.cls<=.1, JSON.stringify(m));
  return m;
}

async function main() {
  const browser=await chromium.launch();
  async function visit(options,fn) {
    const ctx=await browser.newContext({viewport:{width:1440,height:960},reducedMotion:'reduce',...options});
    try {
      const page=await ctx.newPage();
      page.setDefaultTimeout(8500);
      const errors=[],requests=[];
      page.on('pageerror',e=>errors.push(e.message));
      page.on('response',r=>{ if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`); });
      page.on('request',r=>requests.push(r.url()));
      async function open(ref,ready=guideReady) {
        const response=await page.goto(url(ref));
        if(response) assert(response.ok(),ref);
        else assert.equal(page.url(),url(ref));
        if(options.javaScriptEnabled!==false) await page.locator(ready).waitFor();
        await page.evaluate(()=>document.fonts.ready);
      }
      await fn(page,open,requests,ctx);
      assert.deepEqual(errors,[]);
      assert(requests.every(r=>new URL(r).origin===origin.origin),requests);
    } finally { await ctx.close(); }
  }
  try {
    await group('HTTP : trois routes, alias lore, MIME, référencement et liste blanche', async()=>{
      const routes=['',starter,lore,alias];
      const canonical=[];
      for(const ref of routes){
        const r=await fetch(url(ref),{method:'HEAD'});
        assert.equal(r.status,200,ref);
        assert.equal(r.headers.get('content-type'),'text/html; charset=utf-8',ref);
        assert.equal(r.headers.get('x-robots-tag'),'noindex, nofollow',ref);
        const t=await (await fetch(url(ref))).text();
        const c=t.match(/canonical" href="(https:\/\/[^\"]+)"/)[1];
        canonical.push(c);
        if(ref) {
          const graph=JSON.parse(t.match(/<script type="application\/ld\+json">(.+)<\/script>/)[1])['@graph'];
          assert.deepEqual(graph.map(s=>s['@type']),['Article','BreadcrumbList']);
          assert.equal(graph[0].mainEntityOfPage,c);
          assert.equal(graph[1].itemListElement[1].item,c);
        }
      }
      assert.equal(canonical[2],canonical[3]);
      const sitemap=await (await fetch(url('sitemap.xml'))).text();
      assert.deepEqual([...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m=>m[1]),canonical.slice(0,3));
      for(const forbidden of ['lab/','pages/maps/index.html','pages/maps/terminal.html','pages/lore/characters.html','js/data/items.json','workflow.json','docs/sources.json','data/guides.json','templates/guide.html.in','images/lore/quarantine-street.jpg']) {
        assert.equal((await fetch(url(forbidden))).status,404,forbidden);
      }
      const index=await (await fetch(url('js/data/search-index.json'))).json();
      assert.equal(index.records.length,29);
      const dump=JSON.stringify(index);
      assert.doesNotMatch(dump,/(?:#revelations|Kerman|Zubr|Debtor|Savior|Fallen|Icebreaker archive)/i);
    });
    for(const [id,ref,images] of [['starter',starter,3],['lore',lore,2]]) {
      await group(`Bureau : ${id}, médias décodés, chargement léger, audit`,()=>visit({},async(page,open,requests)=>{
        await page.addInitScript(observeMetrics);
        await open(ref);
        performance[id]={initial:await metric(page)};
        assert.equal(await page.locator('h1').count(),1);
        assert.equal(await page.locator('html').getAttribute('lang'),'fr');
        assert(!requests.some(r=>/\.(mp3|m3u8)$|search-index|fuse\.basic|(?:items|armor|ammo|weapons)\.json/.test(r)));
        await decodeMedia(page);
        assert.equal(await page.locator('img').count(),images);
        assert.equal(await page.locator('[data-guide-toc] a').count(),id==='starter'?7:6);
        await axe(page,`${id} 1440 px, état initial`);
      }));
    }
    await group('Clavier : lien d’évitement, sommaire, retour en haut et onglets PMC/Scav',()=>visit({},async(page,open)=>{
      await open(starter);
      await page.keyboard.press('Tab'); await focus(page,'.skip-link');
      await page.keyboard.press('Enter'); await focus(page,'#main');
      await page.locator('[data-guide-toc] a[href="#profils"]').press('Enter');
      await focus(page,'#profils'); await page.waitForURL(url(starter+'#profils')); await visibleAnchor(page,'#profils');
      await qaAttr(page,'[data-guide-toc] a[aria-current=location]','href','#profils');
      assert.equal(await page.locator('.raid-step').count(),10);
      const pmc=page.locator('#profile-pmc-tab'),scav=page.locator('#profile-scav-tab');
      await pmc.press('ArrowRight'); await focus(page,'#profile-scav-tab');
      assert.equal(await scav.getAttribute('aria-selected'),'true');
      assert(!(await page.locator('#profile-pmc').isVisible()));
      assert(await page.locator('#profile-scav').isVisible());
      await page.keyboard.press('Tab'); await focus(page,'#profile-scav');
      await scav.press('Home'); await focus(page,'#profile-pmc-tab');
      await page.keyboard.press('End'); await focus(page,'#profile-scav-tab');
      await axe(page,'Profil Scav sélectionné');
      await page.locator('[data-back-top]').press('Enter'); await focus(page,'#top');
      assert.equal(await page.evaluate(()=>scrollY),0);
    }));
    await group('Checklist locale : six cases, conservation, remise à zéro et isolation de l’accueil',()=>visit({},async(page,open)=>{
      await open(starter+'#checklist');
      const first=page.locator('[data-raid-check=profile]');
      await first.press('Space');
      await page.locator('[data-raid-check=exit]').check();
      assert.equal(await page.locator('#checklist [data-raid-progress]').textContent(),'2/6 repères prêts');
      await open('./','html[data-app-ready][data-home-ready]');
      assert.equal(await page.locator('[data-raid-progress]').textContent(),'0/3 repères prêts');
      await open(starter+'#checklist');
      assert(await first.isChecked());
      await page.locator('[data-raid-reset]').press('Enter'); await focus(page,'[data-raid-check=profile]');
      assert.equal(await page.locator('#checklist [data-raid-progress]').textContent(),'0/6 repères prêts');
      assert(!(await first.isChecked()));
    }));
    await group('FAQ : 24, recherche accentuée, état vide, remise à zéro et ancre directe',()=>visit({},async(page,open)=>{
      await open(starter+'#faq');
      const input=page.locator('#faq-query');
      const visible=page.locator('[data-faq-item]:visible');
      assert.equal(await visible.count(),24);
      await input.fill('securise');
      assert.equal(await visible.count(),1);
      await visible.locator('summary').press('Enter');
      assert(await visible.locator('p').isVisible());
      await axe(page,'FAQ filtrée et réponse ouverte');
      await input.fill('zzqqzzqx');
      assert.equal(await visible.count(),0);
      assert(await page.locator('[data-faq-empty]').isVisible());
      await page.locator('[data-faq-clear]').press('Enter'); await focus(page,'#faq-query');
      assert.equal(await visible.count(),24);
      await open(starter+'#faq-carte');
      await page.locator('#faq-carte p').waitFor();
    }));
    await group('Recherche globale : accueil → débutant → lore, retour à une ancre sur l’accueil',()=>visit({},async(page,open)=>{
      await open('./','html[data-app-ready][data-home-ready]');
      let q=await openSearch(page);
      await q.fill('saignement lourd');
      await page.locator(`${results}[href$="${starter}#sante"]`).click();
      await page.waitForURL(url(starter+'#sante'));
      assert(await page.locator('#sante').isVisible());
      assert.equal(await page.locator('dialog[open]').count(),0);
      q=await openSearch(page);
      await q.fill('Contract Wars');
      await page.locator(`${results}[href$="/pages/lore/#chronologie"]`).click();
      await page.waitForURL(url(lore+'#chronologie'));
      assert(await page.locator('#chronologie').isVisible());
      q=await openSearch(page);
      await q.fill('cartes et extractions');
      await page.locator(`${results}[href$="/#cartes"]`).click();
      await page.waitForURL(url('#cartes'));
      assert(await page.locator('#cartes').isVisible());
    }));
    await group('Recherche locale : question masquée réaffichée, alias du lore sans rechargement',()=>visit({},async(page,open,requests)=>{
      await open(starter);
      await page.locator('#faq-query').fill('zzqqzzqq');
      const q=await openSearch(page);
      await q.fill('route unknown');
      await page.locator(`${results}[href$="#faq-carte"]`).click();
      await focus(page,'#faq-carte');
      assert(await page.locator('#faq-carte p').isVisible());
      assert.equal(await page.locator('#faq-query').inputValue(),'');
      assert.equal(requests.filter(r=>r===url(starter)).length,1);
      await open(alias);
      const query=await openSearch(page);
      await query.fill('chronologie');
      await page.locator(`${results}[href$="#chronologie"]`).click();
      await focus(page,'#chronologie');
      await page.waitForURL(url(alias+'#chronologie'));
      assert.equal(requests.filter(r=>r===url(alias)).length,1);
    }));
    await group('Lore : divulgation explicite, réponse refermable, non persistée et hors résultats',()=>visit({},async(page,open)=>{
      await open(lore+'#revelations');
      const d=page.locator(campaign),s=d.locator('summary'),body=d.locator('[data-nosnippet]');
      assert(!(await body.isVisible()));
      await s.press('Enter');
      assert(await body.isVisible());
      assert.match(await body.textContent(),/Savior/);
      await axe(page,'Révélations ouvertes sur activation');
      await s.press('Space');
      assert(!(await body.isVisible()));
      await s.press('Enter');
      await page.reload(); await page.locator(guideReady).waitFor();
      assert(!(await body.isVisible()));
      const q=await openSearch(page);
      await q.fill('Zubr Debtor');
      await page.locator('[data-search-status]').getByText('Aucun résultat.',{exact:false}).waitFor();
      assert(!(await body.isVisible()));
      await page.keyboard.press('Escape'); await focus(page,trigger);
    }));
    await group('Mobile tactile : parcours accueil–lore–débutant, menu et cibles',()=>visit({viewport:{width:390,height:844},isMobile:true,hasTouch:true},async(page,open)=>{
      await open('./','html[data-app-ready][data-home-ready]');
      await page.locator('.home-published a[href$="/lore/"]').tap();
      await page.waitForURL(url(lore));
      await page.locator(guideReady).waitFor();
      const toggle=page.locator('[data-nav-toggle]');
      await toggle.tap(); await focus(page,'.site-nav__link');
      await page.locator('.mega-menu__summary').tap();
      await axe(page,'Lore, menu mobile ouvert');
      await page.keyboard.press('Escape'); await focus(page,'.mega-menu__summary');
      await page.keyboard.press('Escape'); await focus(page,'[data-nav-toggle]');
      await toggle.tap();
      await page.getByRole('navigation',{name:'Navigation principale'}).getByRole('link',{name:'Débuter',exact:true}).tap();
      await page.waitForURL(url(starter)); await page.locator(guideReady).waitFor();
      await page.locator('.guide-quick__link[href="#checklist"]').tap();
      await page.waitForURL(url(starter+'#checklist'));
      await visibleAnchor(page,'#checklist');
      await page.locator('.guide-check__row').first().tap();
      assert(await page.locator('[data-raid-check=profile]').isChecked());
      await fits(page,'mobile, checklist');
    }));
    await group('Reflow 320–1440 px, texte 200 %, pas de débordement hors région de tableau',()=>visit({},async(page,open)=>{
      for(const ref of [starter,lore]) {
        await open(ref);
        for(const width of widths){
          await page.setViewportSize({width,height:960});
          await fits(page,`${ref} à ${width}px`);
        }
        const enlarged=await page.addStyleTag({content:'html {font-size:200%}'});
        for(const width of [390,768,1024,1440]) {
          await page.setViewportSize({width,height:960});
          await fits(page,`${ref} à ${width}px, texte 200 %`);
        }
        await enlarged.evaluate(el=>el.remove());
      }
    }));
    await group('Préférences : contraste partagé, couleurs système, contenus et clavier',()=>visit({forcedColors:'active',viewport:{width:390,height:844}},async(page,open)=>{
      await open(starter);
      assert(await page.evaluate(()=>matchMedia('(forced-colors: active)').matches));
      await page.locator('[data-contrast-toggle]').click();
      await qaAttr(page,'html','data-theme','contrast');
      await page.locator('[data-motion-toggle]').click();
      await qaAttr(page,'html','data-motion','reduce');
      await axe(page,'Débutant sous couleurs système');
      await open(lore+'#revelations');
      await qaAttr(page,'html','data-theme','contrast');
      await qaAttr(page,'html','data-motion','reduce');
      await page.locator(`${campaign} summary`).press('Enter');
      await axe(page,'Lore ouvert sous couleurs système');
    }));
    await group('Sans JS : navigation, 10 étapes, FAQ native, tous les profils et bloc de révélations',()=>visit({javaScriptEnabled:false,viewport:{width:320,height:800}},async(page,open,requests)=>{
      await open(starter);
      for(const sel of ['.site-nav','#profile-pmc','#profile-scav','#etapes','#sante','.health-diagram','noscript small']) assert(await page.locator(sel).isVisible(),sel);
      assert.equal(await page.locator('.raid-step:visible').count(),10);
      assert.equal(await page.locator('[data-faq-item]:visible').count(),24);
      assert(!(await page.locator('[data-faq-filter]').isVisible()));
      assert(!(await page.locator(trigger).isVisible()));
      await page.locator('#faq-fir summary').press('Enter');
      assert(await page.locator('#faq-fir p').isVisible());
      await fits(page,'débutant sans JS');
      await page.locator('.guide-rail__foot a').click();
      await page.waitForURL(url(lore));
      assert(!(await page.locator(`${campaign} [data-nosnippet]`).isVisible()));
      await page.locator(`${campaign} summary`).press('Enter');
      assert(await page.locator(`${campaign} [data-nosnippet]`).isVisible());
      await fits(page,'lore sans JS avec révélations');
      assert(!requests.some(r=>/\.mp3|search-index|fuse\.basic/.test(r)));
    }));
    await group('Mobile simulé : LCP et CLS des deux dossiers (+100 ms, 4 Mbit/s, CPU ×4)',()=>visit({viewport:{width:390,height:844},isMobile:true,hasTouch:true},async(page,open,_requests,ctx)=>{
      const cd=await ctx.newCDPSession(page);
      await page.addInitScript(observeMetrics);
      await cd.send('Network.enable');
      await cd.send('Network.setCacheDisabled',{cacheDisabled:true});
      await cd.send('Network.emulateNetworkConditions',{offline:false,latency:100,downloadThroughput:500000,uploadThroughput:200000,connectionType:'cellular4g'});
      await cd.send('Emulation.setCPUThrottlingRate',{rate:4});
      for(const [id,ref] of [['starter',starter],['lore',lore]]){
        await open(ref);
        performance[id].mobile=await metric(page);
      }
    }));
    const evidence={schemaVersion:1,status:'VALIDE',browser:`Chromium ${browser.version()}`,checkedAt:new Date().toISOString(),checks,audits,widths,performance};
    await fs.writeFile(out,JSON.stringify(evidence,null,2)+'\n');
    console.log('Performance',JSON.stringify(performance));
  } finally { await browser.close(); }
}
main().catch(error=>{console.error(error);process.exitCode=1;});
