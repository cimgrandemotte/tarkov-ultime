/** Coche persistante, locale au navigateur et propre à chaque liste. */
import { storageRead, storageWrite } from '../utils.js';

export function initChecklist(root = document) {
  for (const region of root.querySelectorAll('[data-checklist]')) {
    const boxes = [...region.querySelectorAll('input[type="checkbox"][data-raid-check]')];
    const status = region.querySelector('[data-raid-progress]');
    const reset = region.querySelector('[data-raid-reset]');
    if (!boxes.length || !status || !reset) continue;
    const key = `tug:checklist:${region.dataset.checklist}:v1`;
    const saved = storageRead(key, {});
    for (const box of boxes) box.checked = saved?.[box.dataset.raidCheck] === true;
    function update(persist = true) {
      const count = boxes.filter((box) => box.checked).length;
      status.textContent = `${count}/${boxes.length} repère${count === 1 ? '' : 's'} prêt${count === 1 ? '' : 's'}`;
      reset.disabled = !count;
      if (persist) storageWrite(key, Object.fromEntries(boxes.map((box) => [box.dataset.raidCheck, box.checked])));
    }
    for (const box of boxes) box.addEventListener('change', () => update());
    reset.addEventListener('click', () => {
      for (const box of boxes) box.checked = false;
      update();
      boxes[0].focus();
    });
    const note = region.querySelector('[data-raid-storage-note]');
    if (note) note.hidden = false;
    status.hidden = false;
    reset.hidden = false;
    update(false);
  }
}

