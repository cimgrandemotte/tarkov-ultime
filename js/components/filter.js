/** Filtrage et tri progressifs de listes déjà rendues dans le HTML. */
import { normalizeText, sortFr } from '../utils.js';

export function initFilters(root = document) {
  for (const region of root.querySelectorAll('[data-filter]')) {
    const form = region.querySelector('[data-filter-form]');
    const list = region.querySelector('[data-filter-list]');
    const status = region.querySelector('[data-filter-count]');
    const empty = region.querySelector('[data-filter-empty]');
    if (!(form instanceof HTMLFormElement) || !list || !status) continue;
    const query = form.querySelector('[data-filter-input]');
    const sortBy = form.querySelector('[data-filter-sort]');
    const fields = [...form.querySelectorAll('[data-filter-key]')];
    const rows = [...list.querySelectorAll(':scope > [data-filter-row]')].map((el, index) => ({ el, index, label: el.dataset.sortLabel ?? '', text: normalizeText(el.dataset.filterText ?? el.textContent) }));
    const selectCount = (count) => `${count} ${count === 1 ? (region.dataset.filterSingular ?? 'entrée') : (region.dataset.filterPlural ?? 'entrées')}`;
    let previousSort = null;

    function render() {
      const search = normalizeText(query?.value).split(' ').filter(Boolean);
      let count = 0;
      for (const { el, text } of rows) {
        const active = search.every((word) => text.includes(word)) && fields.every((field) => !field.value || el.dataset[field.dataset.filterKey] === field.value);
        el.hidden = !active;
        if (active) count += 1;
      }
      const sort = sortBy?.value ?? '';
      if (sort !== previousSort) {
        const order = [...rows];
        if (sort === 'label') order.sort((a, b) => sortFr.compare(a.label, b.label) || a.index - b.index);
        else if (sort) {
          const key = sortBy.selectedOptions[0]?.dataset.metric;
          const numeric = ({ el }) => el.dataset[key] !== undefined && el.dataset[key] !== '' ? Number(el.dataset[key]) : -Infinity;
          if (key) order.sort((a, b) => (numeric(b) - numeric(a)) || a.index - b.index);
        }
        for (const { el } of order) list.append(el);
        previousSort = sort;
      }
      if (status.textContent !== selectCount(count)) status.textContent = selectCount(count);
      if (empty) empty.hidden = count > 0;
    }
    form.addEventListener('submit', (event) => { event.preventDefault(); render(); });
    form.addEventListener('input', render);
    form.addEventListener('change', render);
    form.addEventListener('reset', () => queueMicrotask(render));
    region.addEventListener('guide:reveal-target', (event) => {
      if (list.contains(event.target) && event.target.closest('[hidden]')) form.reset();
    });
    form.hidden = false;
    render();
  }
}
