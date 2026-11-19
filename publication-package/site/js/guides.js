/** Interactions du dossier. Révélations : seul le contrôle HTML natif ouvre le bloc. */
import { normalizeText } from './utils.js';
import { initChecklist } from './components/checklist.js';

function initFAQ(root = document) {
  const section = root.querySelector('[data-guide-faq]');
  if (!section) return;
  const filter = section.querySelector('[data-faq-filter]');
  const input = filter?.querySelector('[data-faq-query]');
  const clear = filter?.querySelector('[data-faq-clear]');
  const status = filter?.querySelector('[data-faq-status]');
  const empty = section.querySelector('[data-faq-empty]');
  const groups = [...section.querySelectorAll('[data-faq-group]')].map(group => {
    const items = [...group.querySelectorAll('[data-faq-item]')].map(item => ({ item, key: normalizeText(`${item.textContent} ${item.dataset.faqKeywords ?? ''}`) }));
    return { group, items };
  });
  if (!input || !clear || !status || !empty || !groups.length) return;
  function update() {
    const words = normalizeText(input.value).split(' ').filter(Boolean);
    let count = 0;
    for (const { group, items } of groups) {
      let visible = 0;
      for (const { item, key } of items) {
        const match = words.every(word => key.includes(word));
        item.hidden = !match;
        if (match) visible++;
      }
      group.hidden = !visible;
      count += visible;
    }
    empty.hidden = Boolean(count);
    status.textContent = `${count} réponse${count > 1 ? 's' : ''}`;
  }
  function reveal(target) {
    if (!target?.matches('[data-faq-item]') || !section.contains(target)) return false;
    if (target.hidden) { input.value = ''; update(); }
    target.open = true;
    return true;
  }
  function revealHash(scroll = false) {
    const id = location.hash.slice(1); // les ancres publiées sont en ASCII
    if (!id.startsWith('faq-')) return;
    const target = root.getElementById(id);
    if (reveal(target) && scroll) target.scrollIntoView({ block: 'start' });
  }
  input.addEventListener('input', update);
  clear.addEventListener('click', () => { input.value = ''; update(); input.focus(); });
  section.addEventListener('guide:reveal-target', event => { reveal(event.target); });
  window.addEventListener('hashchange', () => revealHash(true));
  filter.hidden = false;
  update();
  revealHash(true);
}

function initToc(root = document) {
  const links = [...root.querySelectorAll('[data-guide-toc] a')];
  if (!links.length) return;
  function showCurrent() {
    const target = root.getElementById(location.hash.slice(1));
    const id = target?.closest('.guide-section')?.id;
    for (const link of links) {
      if (link.hash === `#${id}`) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  }
  window.addEventListener('hashchange', showCurrent);
  window.addEventListener('popstate', showCurrent);
  root.addEventListener('guide:reveal-target', showCurrent);
  showCurrent();
}
function initialize() {
  initChecklist();
  initFAQ();
  initToc();
  document.documentElement.dataset.guidesReady = 'true';
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize, { once: true });
else initialize();
