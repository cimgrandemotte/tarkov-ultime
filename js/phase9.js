/** Filtres locaux PHASE_9. Les listes gardent leur contenu complet sans JavaScript. */
function setCount(node, count, noun) {
  if (!node) return;
  node.textContent = `Résultats : ${count} ${noun}${count === 1 ? '' : 's'}.`;
}

function initBranchFilters(root = document) {
  for (const select of root.querySelectorAll('[data-p9-branch-filter]')) {
    const section = select.closest('.phase9-section') || root;
    const cards = [...section.querySelectorAll('[data-p9-branch-card]')];
    if (!cards.length) continue;
    const controls = select.closest('[data-p9-branch-controls]') || select.parentElement?.parentElement;
    if (controls) controls.hidden = false;
    const count = section.querySelector('[data-p9-branch-count]');
    const update = () => {
      let visible = 0;
      for (const card of cards) {
        const show = select.value === 'all' || card.dataset.p9Branch === select.value;
        card.hidden = !show;
        if (show) visible += 1;
      }
      setCount(count, visible, select.dataset.p9BranchNoun || 'guide');
    };
    select.addEventListener('change', update);
    update();
  }
}

function initModFilters(root = document) {
  const branch = root.querySelector('[data-p9-mod-branch]');
  const category = root.querySelector('[data-p9-mod-category]');
  if (!branch || !category) return;
  const section = branch.closest('.phase9-section') || root;
  const cards = [...section.querySelectorAll('[data-p9-mod-card]')];
  const controls = branch.closest('[data-p9-mod-controls]') || branch.closest('.phase9-filter-bar');
  if (controls) controls.hidden = false;
  const count = section.querySelector('[data-p9-mod-count]');
  const update = () => {
    let visible = 0;
    for (const card of cards) {
      const branchMatch = branch.value === 'all' || card.dataset.p9ModBranch === branch.value;
      const categoryMatch = category.value === 'all' || card.dataset.p9ModCategory === category.value;
      const show = branchMatch && categoryMatch;
      card.hidden = !show;
      if (show) visible += 1;
    }
    setCount(count, visible, 'fiche');
  };
  branch.addEventListener('change', update);
  category.addEventListener('change', update);
  update();
}

function initTroubleFilter(root = document) {
  for (const select of root.querySelectorAll('[data-p9-trouble-filter]')) {
    const section = select.closest('.phase9-section') || root;
    const cards = [...section.querySelectorAll('[data-p9-trouble-card]')];
    if (!cards.length) continue;
    const controls = select.closest('[data-p9-trouble-controls]') || select.parentElement?.parentElement;
    if (controls) controls.hidden = false;
    const count = section.querySelector('[data-p9-trouble-count]');
    const update = () => {
      let visible = 0;
      for (const card of cards) {
        const show = select.value === 'all' || card.dataset.p9Symptom === select.value;
        card.hidden = !show;
        if (show) visible += 1;
      }
      setCount(count, visible, 'piste');
    };
    select.addEventListener('change', update);
    update();
  }
}

function initEventFilters(root = document) {
  const toolbar = root.querySelector('[data-p9-event-filters]');
  const section = toolbar?.closest('.phase9-section');
  if (!toolbar || !section) return;
  const buttons = [...toolbar.querySelectorAll('[data-p9-event-filter]')];
  const cards = [...section.querySelectorAll('[data-p9-event-card]')];
  const count = section.querySelector('[data-p9-event-count]');
  toolbar.hidden = false;
  function select(value) {
    let visible = 0;
    for (const button of buttons) button.setAttribute('aria-pressed', String(button.dataset.p9EventFilter === value));
    for (const card of cards) {
      const show = value === 'all' || card.dataset.p9Status === value;
      card.hidden = !show;
      if (show) visible += 1;
    }
    setCount(count, visible, 'repère');
  }
  for (const button of buttons) button.addEventListener('click', () => select(button.dataset.p9EventFilter));
  select('all');
}

function initialize(root = document) {
  initBranchFilters(root);
  initModFilters(root);
  initTroubleFilter(root);
  initEventFilters(root);
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => initialize(), { once: true });
else initialize();
