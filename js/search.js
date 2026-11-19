/** Recherche locale. Fuse et l'index ne sont chargés qu'à la demande. */
import { normalizeText, loadJson, sameOriginUrl, node } from './utils.js';
import { openDialog, closeDialog } from './components/modal.js';

function tidy(records, base) {
  return records.flatMap((entry) => {
    const url = sameOriginUrl(entry?.href, base);
    if (!entry?.title || !url) return [];
    return [{
      title: String(entry.title), summary: String(entry.summary ?? ''), tag: String(entry.tag ?? ''), url,
      keyTitle: normalizeText(entry.title), keySummary: normalizeText(entry.summary),
      keyTags: normalizeText([entry.tag, ...((Array.isArray(entry.keywords) ? entry.keywords : []))].join(' ')),
    }];
  });
}

export function initSearch(root = document) {
  const dialog = root.querySelector('dialog[data-site-search]');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const input = dialog.querySelector('[data-search-input]');
  const results = dialog.querySelector('[data-search-results]');
  const status = dialog.querySelector('[data-search-status]');
  const activators = [...root.querySelectorAll('[data-modal-open]')].filter((el) => el.dataset.modalOpen === dialog.id && el.matches('[data-site-search-trigger]'));
  if (!input || !results || !status || !activators.length) return;
  const keyHint = /mac/i.test(navigator.userAgentData?.platform ?? navigator.platform) ? '⌘ K' : 'Ctrl K';
  for (const el of activators) {
    const hint = el.querySelector('[data-keyhint]');
    if (hint) hint.dataset.keyhint = keyHint;
    el.hidden = false;
  }
  const base = sameOriginUrl(dialog.dataset.searchBase || document.baseURI)?.href ?? document.baseURI;
  let provider = null;
  let dataset;
  let loadState = 'not-loaded';
  let sequence = 0;

  function prepare() {
    dataset ??= Promise.all([
      loadJson(dialog.dataset.searchSource),
      import('../vendor/fuse.basic.min.mjs').then((lib) => lib.default).catch(() => null),
    ]).then(([doc, Fuse]) => {
      const records = tidy(Array.isArray(doc) ? doc : (Array.isArray(doc?.records) ? doc.records : []), base);
      if (Fuse && records.length) {
        const index = new Fuse(records, {
          keys: [{ name: 'keyTitle', weight: .57 }, { name: 'keyTags', weight: .33 }, { name: 'keySummary', weight: .10 }],
          threshold: .37, ignoreLocation: true, minMatchCharLength: 2, includeScore: true,
        });
        provider = 'fuse';
        return { records, query: (text) => index.search(text, { limit: 10 }).map(({ item }) => item) };
      }
      provider = 'local';
      return { records, query: (text) => records.filter((record) => `${record.keyTitle} ${record.keyTags} ${record.keySummary}`.includes(text)).slice(0, 10) };
    }).catch((error) => { dataset = undefined; throw error; });
    return dataset;
  }

  function navigate(event, record) {
    const destination = record.url;
    const pagePath = (p) => p.replace(/\/index\.html$/, '/');
    const sameDocument = pagePath(destination.pathname) === pagePath(location.pathname) && destination.search === location.search;
    if (sameDocument && destination.hash) {
      let key;
      try { key = decodeURIComponent(destination.hash.slice(1)); } catch { key = destination.hash.slice(1); }
      const anchor = root.getElementById(key);
      if (anchor) {
        event.preventDefault();
        closeDialog(dialog, { restoreFocus: false });
        if (location.hash !== destination.hash) history.pushState(null, '', destination.hash);
        anchor.dispatchEvent(new CustomEvent('guide:reveal-target', { bubbles: true }));
        queueMicrotask(() => {
          if (!anchor.hasAttribute('tabindex')) anchor.tabIndex = -1;
          anchor.scrollIntoView({ block: 'start' });
          anchor.focus({ preventScroll: true });
        });
        return;
      }
    }
    closeDialog(dialog, { restoreFocus: false });
  }
  function paint(matches) {
    const fragment = document.createDocumentFragment();
    for (const record of matches) {
      const item = node('li');
      const link = node('a', null, 'search-results__link');
      link.href = record.url.href;
      link.append(node('span', record.title, 'search-results__name'));
      if (record.tag) link.append(node('span', record.tag, 'search-results__tag'));
      if (record.summary) link.append(node('span', record.summary, 'search-results__summary'));
      link.addEventListener('click', (event) => {
        if (!(event.ctrlKey || event.metaKey || event.altKey || event.shiftKey)) navigate(event, record);
      });
      item.append(link);
      fragment.append(item);
    }
    results.replaceChildren(fragment);
  }
  async function render() {
    const current = ++sequence;
    if (loadState !== 'ready') {
      status.setAttribute('aria-busy', 'true');
      status.textContent = 'Chargement de l’index…';
    }
    try {
      const index = await prepare();
      loadState = 'ready';
      dialog.dataset.searchProvider = provider;
      if (current !== sequence || !dialog.open) return;
      const query = normalizeText(input.value);
      const matches = query ? (query.length >= 2 ? index.query(query) : []) : index.records.slice(0, 5);
      paint(matches);
      if (!query && matches.length) status.textContent = 'Accès rapides';
      else if (!query) status.textContent = 'Aucune page n’est encore indexée.';
      else if (query.length < 2) status.textContent = 'Saisissez au moins deux caractères.';
      else if (!matches.length) status.textContent = 'Aucun résultat. Essayez un autre terme.';
      else status.textContent = `${matches.length} résultat${matches.length === 1 ? '' : 's'}${matches.length === 10 ? ' affichés au maximum' : ''}.`;
    } catch {
      if (current !== sequence) return;
      results.replaceChildren();
      loadState = 'error';
      status.textContent = 'Index indisponible. Fermez la recherche et réessayez, ou utilisez la navigation.';
    } finally {
      if (current === sequence) status.setAttribute('aria-busy', 'false');
    }
  }
  dialog.addEventListener('guide:open', () => { input.select(); void render(); });
  input.addEventListener('input', () => { void render(); });
  dialog.addEventListener('keydown', async (event) => {
    if (event.isComposing) return;
    const links = [...results.querySelectorAll('a')];
    if (event.key === 'Enter' && event.target === input) {
      event.preventDefault();
      await render();
      if (dialog.open) results.querySelector('a')?.click();
    } else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      const i = links.indexOf(event.target);
      if (event.target !== input && i < 0) return;
      if (!links.length) return;
      event.preventDefault();
      if (event.key === 'ArrowDown') links[Math.min(i + 1, links.length - 1)].focus();
      else if (i <= 0) input.focus();
      else links[i - 1].focus();
    }
  });
  root.addEventListener('keydown', (event) => {
    if (event.defaultPrevented || event.repeat || event.isComposing || event.altKey) return;
    const shortcut = (event.ctrlKey || event.metaKey) && !event.shiftKey && event.key.toLowerCase() === 'k';
    if (shortcut) {
      if (root.querySelector('dialog[open]:not([data-site-search])')) return;
      event.preventDefault();
      if (!dialog.open) openDialog(dialog, event.target instanceof HTMLElement ? event.target : activators[0]);
      else input.focus();
    }
  });
}
