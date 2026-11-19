/** Comparateur de deux à trois entrées homogènes. N'effectue aucune conversion de mode. */
import { node, numberFr, parseRecord } from '../utils.js';

export function initComparators(root = document) {
  for (const region of root.querySelectorAll('[data-compare]')) {
    const config = parseRecord(region.querySelector('[data-compare-data]'));
    const open = region.querySelector('[data-compare-open]');
    const clear = region.querySelector('[data-compare-clear]');
    const bar = region.querySelector('[data-compare-bar]');
    const status = region.querySelector('[data-compare-status]');
    const dialog = root.getElementById(open?.dataset.modalOpen ?? '');
    const output = dialog?.querySelector('[data-compare-output]');
    if (!Array.isArray(config?.records) || !Array.isArray(config?.fields) || !open || !status || !output || typeof dialog.showModal !== 'function') continue;
    const byId = new Map(config.records.map((record) => [record.id, record]));
    const choices = [...region.querySelectorAll('[data-compare-toggle]')].filter((button) => byId.has(button.dataset.compareToggle));
    const selected = new Set();
    const limit = 3;
    const close = dialog.querySelector('[data-modal-close]');
    const statusInDialog = dialog.querySelector('[data-compare-dialog-status]');

    function renderTable() {
      const picked = [...selected].map((id) => byId.get(id));
      if (picked.length < 2) {
        output.replaceChildren(node('p', 'Sélectionnez au moins deux modèles dans le catalogue.'));
        if (statusInDialog) statusInDialog.textContent = 'Il reste moins de deux modèles.';
        return;
      }
      if (statusInDialog) statusInDialog.textContent = `${picked.length} modèles comparés.`;
      const scroller = node('div', null, 'data-table__scroll');
      scroller.tabIndex = 0;
      scroller.setAttribute('role', 'region');
      scroller.setAttribute('aria-label', 'Tableau du comparateur, défilement horizontal si nécessaire');
      const table = node('table', null, 'data-table');
      table.append(node('caption', config.caption || 'Comparaison de données de jeu'));
      const head = table.createTHead().insertRow();
      const label = node('th', 'Attribut');
      label.scope = 'col';
      head.append(label);
      for (const record of picked) {
        const cell = node('th');
        cell.scope = 'col';
        const chip = node('span', null, 'compare-chip');
        const remove = node('button', 'Retirer', 'button button--quiet compare-chip__remove');
        remove.type = 'button';
        remove.dataset.compareRemove = record.id;
        remove.setAttribute('aria-label', `Retirer ${record.title} de la comparaison`);
        chip.append(node('span', record.title), remove);
        cell.append(chip);
        head.append(cell);
      }
      const body = table.createTBody();
      for (const field of config.fields) {
        const row = body.insertRow();
        const th = node('th', field.label);
        th.scope = 'row';
        row.append(th);
        for (const record of picked) {
          const val = record.metrics?.[field.key];
          const cell = row.insertCell();
          cell.textContent = val == null || val === '' ? 'Non renseigné' : typeof val === 'number' ? `${numberFr.format(val)}${field.unit ? ' ' + field.unit : ''}` : String(val);
        }
      }
      scroller.append(table);
      output.replaceChildren(scroller);
    }
    function render(message) {
      for (const button of choices) {
        const active = selected.has(button.dataset.compareToggle);
        button.setAttribute('aria-pressed', String(active));
      }
      const base = `${selected.size}/3 sélectionné${selected.size === 1 ? '' : 's'}`;
      status.textContent = message ? `${base} · ${message}` : base;
      open.disabled = selected.size < 2;
      if (clear) clear.disabled = !selected.size;
      if (dialog.open) renderTable();
    }
    for (const button of choices) {
      button.hidden = false;
      button.addEventListener('click', () => {
        const id = button.dataset.compareToggle;
        if (selected.has(id)) selected.delete(id);
        else if (selected.size < limit) selected.add(id);
        else { render('Limite atteinte. Retirez un modèle pour en ajouter un autre.'); return; }
        render();
      });
    }
    clear?.addEventListener('click', () => { selected.clear(); render('Comparateur réinitialisé.'); open.closest('[data-compare]')?.querySelector('[data-filter-input]')?.focus(); });
    dialog.addEventListener('guide:open', renderTable);
    dialog.addEventListener('click', (event) => {
      const button = event.target.closest('[data-compare-remove]');
      if (!button) return;
      selected.delete(button.dataset.compareRemove);
      const visible = (el) => el && !el.closest('[hidden]');
      const removed = choices.find((el) => el.dataset.compareToggle === button.dataset.compareRemove);
      const restore = (visible(removed) ? removed : choices.find(visible)) ?? region.querySelector('[data-filter-input]');
      render();
      (output.querySelector('[data-compare-remove]') ?? close)?.focus();
      if (open.disabled && restore) dialog.addEventListener('close', () => restore.focus({ preventScroll: true }), { once: true });
    });
    if (bar) bar.hidden = false;
    render();
  }
}
