/** Point d'entrée ES modules. Chaque composant ne s'active que si son markup est présent. */
import { storageRead, storageWrite } from './utils.js';
import { initDialogs } from './components/modal.js';
import { initNavigation } from './components/navigation.js';
import { initSearch } from './search.js';
import { initAudio } from './audio.js';
import { initAnimations } from './animations.js';
import { initTabs } from './components/tabs.js';

function installPreferences(root) {
  const html = root.documentElement;
  for (const { selector, key, dataKey, activeValue, eventName } of [
    { selector: '[data-contrast-toggle]', key: 'tug:contrast:v1', dataKey: 'theme', activeValue: 'contrast', eventName: 'guide:theme-change' },
    { selector: '[data-motion-toggle]', key: 'tug:motion:v1', dataKey: 'motion', activeValue: 'reduce', eventName: 'guide:motion-change' },
  ]) {
    const buttons = [...root.querySelectorAll(selector)];
    let active = storageRead(key) === true;
    function paint(notify) {
      if (active) html.dataset[dataKey] = activeValue;
      else delete html.dataset[dataKey];
      for (const button of buttons) button.setAttribute('aria-pressed', String(active));
      if (notify) root.dispatchEvent(new CustomEvent(eventName));
    }
    for (const button of buttons) {
      button.hidden = false;
      button.addEventListener('click', () => { active = !active; storageWrite(key, active); paint(true); });
    }
    paint(false);
  }
}
function installBackToTop(root) {
  const control = root.querySelector('[data-back-top]');
  if (!control) return;
  let scheduled = false;
  function paint() { scheduled = false; control.hidden = window.scrollY < Math.min(window.innerHeight * .65, 520); }
  window.addEventListener('scroll', () => {
    if (!scheduled) { scheduled = true; requestAnimationFrame(paint); }
  }, { passive: true });
  control.addEventListener('click', (event) => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.defaultPrevented) return;
    const target = control.hash && root.getElementById(control.hash.slice(1));
    if (!target) return;
    event.preventDefault();
    if (location.hash !== control.hash) history.pushState(null, '', control.hash);
    window.scrollTo({ top: 0, behavior: 'instant' });
    target.focus({ preventScroll: true });
  });
  paint();
}
async function initialize(root = document) {
  installPreferences(root);
  initDialogs(root);
  initNavigation(root);
  initSearch(root);
  initTabs(root);
  initAudio(root);
  initAnimations(root);
  installBackToTop(root);
  const extras = [
    ['[data-tooltip]', () => import('./components/tooltip.js').then(({ initTooltips }) => initTooltips(root))],
    ['[data-filter]', () => import('./components/filter.js').then(({ initFilters }) => initFilters(root))],
    ['[data-compare]', () => import('./components/comparator.js').then(({ initComparators }) => initComparators(root))],
    ['[data-tierlist]', () => import('./components/tierlist.js').then(({ initTierLists }) => initTierLists(root))],
  ].flatMap(([selector, load]) => root.querySelector(selector) ? [load()] : []);
  if (extras.length) await Promise.allSettled(extras);
  root.documentElement.dataset.appReady = 'true';
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => initialize(), { once: true });
else initialize();
