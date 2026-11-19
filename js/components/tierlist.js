/** Tier list éditable au clavier via les sélecteurs, sans dépendre du glisser-déposer. */
import { storageRead, storageWrite, node } from '../utils.js';

export function initTierLists(root = document) {
  for (const component of root.querySelectorAll('[data-tierlist]')) {
    const controls = component.querySelector('[data-tier-controls]');
    const status = component.querySelector('[data-tier-status]');
    const selectors = [...component.querySelectorAll('select[data-tier-item]')];
    const lanes = new Map([...component.querySelectorAll('[data-tier-rank]')].map((lane) => [lane.dataset.tierRank, lane]));
    if (!controls || !selectors.length || !lanes.size) continue;
    const key = `tug:tierlist:v1:${component.dataset.tierlist}`;
    const defaults = Object.fromEntries(selectors.map((select) => [select.dataset.tierItem, select.value]));
    const saved = storageRead(key, {});
    function print() {
      for (const lane of lanes.values()) lane.replaceChildren();
      for (const select of selectors) lanes.get(select.value)?.append(node('li', select.dataset.tierLabel, 'tiers__item'));
      for (const list of lanes.values()) if (!list.childElementCount) list.append(node('li', 'Aucun élément', 'copy-muted'));
    }
    function save() {
      storageWrite(key, Object.fromEntries(selectors.map((select) => [select.dataset.tierItem, select.value])));
    }
    for (const select of selectors) {
      const savedRank = saved?.[select.dataset.tierItem];
      if (lanes.has(savedRank)) select.value = savedRank;
      select.addEventListener('change', () => {
        save();
        print();
        if (status) status.textContent = `${select.dataset.tierLabel} déplacé au rang ${select.value}.`;
      });
    }
    component.querySelector('[data-tier-reset]')?.addEventListener('click', () => {
      for (const select of selectors) select.value = defaults[select.dataset.tierItem];
      print();
      save();
      if (status) status.textContent = 'Priorités réinitialisées.';
    });
    print();
    controls.hidden = false;
  }
}
