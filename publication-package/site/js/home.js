/** Interactions éditoriales propres à l'accueil, en amélioration progressive. */
import { initChecklist } from './components/checklist.js';

export function initNews(root = document) {
  const feed = root.querySelector('[data-news]');
  const controls = feed?.querySelector('[data-news-filters]');
  const count = feed?.querySelector('[data-news-count]');
  if (!controls || !count) return;
  const buttons = [...controls.querySelectorAll('[data-news-view]')];
  const rows = [...feed.querySelectorAll('[data-news-type]')];
  if (!buttons.length || !rows.length) return;
  function show(view) {
    const filtered = rows.filter((row) => view === 'all' || row.dataset.newsType === view);
    for (const row of rows) row.hidden = !filtered.includes(row);
    for (const button of buttons) button.setAttribute('aria-pressed', String(button.dataset.newsView === view));
    count.textContent = `${filtered.length} annonce${filtered.length === 1 ? '' : 's'}`;
  }
  for (const button of buttons) button.addEventListener('click', () => show(button.dataset.newsView));
  feed.addEventListener('guide:reveal-target', (event) => {
    if (rows.some((row) => row.hidden && row.contains(event.target))) show('all');
  });
  window.addEventListener('hashchange', () => {
    const row = rows.find((item) => '#' + item.id === location.hash);
    if (!row?.hidden) return;
    show('all');
    row.scrollIntoView({ block: 'start' });
  });
  controls.hidden = false;
}

function initialize() {
  initNews();
  initChecklist();
  document.documentElement.dataset.homeReady = 'true';
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize, { once: true });
else initialize();
