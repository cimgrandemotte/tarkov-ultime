/** Filtres locaux PHASE_10 : chronologie, répertoire et glossaire. */
function normalizeText(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase('fr-FR')
    .trim();
}

function setStatus(node, visible, total, label) {
  if (!node) return;
  node.textContent = `Résultats : ${visible} sur ${total} ${label}${total === 1 ? '' : 's'}.`;
}

function initTimeline(root = document) {
  const controls = root.querySelector('[data-p10-timeline-controls]');
  if (!controls) return;
  const yearSelect = controls.querySelector('[data-p10-timeline-year]');
  const kindSelect = controls.querySelector('[data-p10-timeline-kind]');
  const section = controls.closest('.phase10-section');
  const cards = [...(section || root).querySelectorAll('[data-p10-timeline-card]')];
  const count = controls.querySelector('[data-p10-timeline-count]');
  if (!cards.length) return;
  controls.hidden = false;
  const update = () => {
    let visible = 0;
    for (const card of cards) {
      const yearMatch = !yearSelect || yearSelect.value === 'all' || card.dataset.year === yearSelect.value;
      const kindMatch = !kindSelect || kindSelect.value === 'all' || card.dataset.kind === kindSelect.value;
      const show = yearMatch && kindMatch;
      card.hidden = !show;
      if (show) visible += 1;
    }
    setStatus(count, visible, cards.length, 'entrée');
  };
  yearSelect?.addEventListener('change', update);
  kindSelect?.addEventListener('change', update);
  update();
}

function initResources(root = document) {
  const controls = root.querySelector('[data-p10-resource-controls]');
  if (!controls) return;
  const purpose = controls.querySelector('[data-p10-resource-purpose]');
  const trust = controls.querySelector('[data-p10-resource-trust]');
  const query = controls.querySelector('[data-p10-resource-query]');
  const cards = [...root.querySelectorAll('[data-p10-resource-card]')];
  const count = controls.querySelector('[data-p10-resource-count]');
  if (!cards.length) return;
  controls.hidden = false;
  const update = () => {
    const needle = normalizeText(query?.value);
    let visible = 0;
    for (const card of cards) {
      const purposeMatch = !purpose || purpose.value === 'all' || card.dataset.purpose === purpose.value;
      const trustMatch = !trust || trust.value === 'all' || card.dataset.trust === trust.value;
      const searchText = normalizeText(card.dataset.search || card.textContent);
      const queryMatch = !needle || searchText.includes(needle);
      const show = purposeMatch && trustMatch && queryMatch;
      card.hidden = !show;
      if (show) visible += 1;
    }
    setStatus(count, visible, cards.length, 'ressource');
  };
  purpose?.addEventListener('change', update);
  trust?.addEventListener('change', update);
  query?.addEventListener('input', update);
  update();
}

function initGlossary(root = document) {
  const controls = root.querySelector('[data-p10-glossary-controls]');
  const alpha = root.querySelector('[data-p10-alpha]');
  const list = root.querySelector('[data-p10-glossary-list]');
  if (!controls || !alpha || !list) return;
  const query = controls.querySelector('[data-p10-glossary-query]');
  const group = controls.querySelector('[data-p10-glossary-group]');
  const reset = controls.querySelector('[data-p10-glossary-reset]');
  const count = controls.querySelector('[data-p10-glossary-count]');
  const items = [...list.querySelectorAll('[data-p10-glossary-item]')];
  const groups = [...list.querySelectorAll('[data-p10-letter-group]')];
  const buttons = [...alpha.querySelectorAll('[data-p10-letter]')];
  if (!items.length) return;
  controls.hidden = false;
  alpha.hidden = false;
  let selectedLetter = 'all';

  const update = () => {
    const needle = normalizeText(query?.value);
    let visible = 0;
    for (const item of items) {
      const letterMatch = selectedLetter === 'all' || item.dataset.letter === selectedLetter;
      const groupMatch = !group || group.value === 'all' || item.dataset.group === group.value;
      const searchable = normalizeText(item.dataset.search || item.textContent);
      const queryMatch = !needle || searchable.includes(needle);
      const show = letterMatch && groupMatch && queryMatch;
      item.hidden = !show;
      if (show) visible += 1;
    }
    for (const section of groups) {
      const anyVisible = section.querySelector('[data-p10-glossary-item]:not([hidden])');
      section.hidden = !anyVisible;
    }
    for (const button of buttons) {
      button.setAttribute('aria-pressed', String(button.dataset.p10Letter === selectedLetter));
    }
    if (count) count.textContent = `${visible} entrée${visible === 1 ? '' : 's'} sur ${items.length}.`;
  };

  for (const button of buttons) {
    button.addEventListener('click', () => {
      selectedLetter = button.dataset.p10Letter || 'all';
      update();
      if (selectedLetter !== 'all') {
        const heading = root.getElementById?.(`letter-${selectedLetter}`) || root.querySelector(`#letter-${selectedLetter}`);
        heading?.scrollIntoView({ block: 'start', behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
      }
    });
  }
  query?.addEventListener('input', update);
  group?.addEventListener('change', update);
  reset?.addEventListener('click', () => {
    if (query) query.value = '';
    if (group) group.value = 'all';
    selectedLetter = 'all';
    update();
    query?.focus();
  });
  update();
}

function initialize(root = document) {
  initTimeline(root);
  initResources(root);
  initGlossary(root);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => initialize(), { once: true });
} else {
  initialize();
}
