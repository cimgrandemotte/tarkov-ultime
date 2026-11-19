/* PHASE_5 : filtres, mode explicite et comparateur. Le HTML initial reste la référence sans JS. */
const MODE_NAMES = {
  regular: 'PvP permanent',
  pve: 'PvE Zone',
  'pvp-season': 'PvP saisonnier',
};
const numberFr = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 });
const clean = (value) => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
const readJson = (value, fallback = {}) => {
  try { return JSON.parse(value || ''); } catch { return fallback; }
};
const make = (tag, text, className) => {
  const el = document.createElement(tag);
  if (text !== undefined && text !== null) el.textContent = String(text);
  if (className) el.className = className;
  return el;
};
function formatValue(value, unit = '') {
  if (value === null || value === undefined || value === '') return 'Non renseigné';
  return `${typeof value === 'number' ? numberFr.format(value) : value}${unit ? ` ${unit}` : ''}`;
}
function modeDataFor(row, mode) {
  return readJson(row.dataset.modeValues, {})[mode] || {};
}
function offerSummary(data) {
  const offers = Array.isArray(data.offers) ? data.offers : [];
  if (!offers.length) return 'Aucune offre renseignée dans buyFromTrader pour cet export';
  const visible = offers.slice(0, 2).map((offer) => {
    const level = offer.level == null ? '' : ` LL${offer.level}`;
    const cost = offer.price == null ? 'prix non renseigné' : `${numberFr.format(offer.price)} ${offer.currency || ''}`.trim();
    const gated = offer.taskUnlock ? ' · verrou de tâche indiqué' : '';
    return `${offer.trader || 'Trader non résolu'}${level} · ${cost}${gated}`;
  });
  if (offers.length > visible.length) visible.push(`+ ${offers.length - visible.length} autre(s) offre(s)`);
  return visible.join(' ; ');
}
function fleaSummary(data) {
  return data.flea?.label || 'Pas de relevé exploitable dans cet export';
}
function craftSummary(data) {
  const recipes = Array.isArray(data.recipes) ? data.recipes : [];
  if (!recipes.length) return 'Aucune recette liée à cet identifiant dans le snapshot';
  return recipes.map((recipe) => {
    const station = recipe.station || 'Station non résolue';
    const level = recipe.level == null ? '' : ` · niveau ${recipe.level}`;
    const duration = recipe.durationLabel ? ` · ${recipe.durationLabel}` : '';
    const taskName = recipe.task?.name ? ` · tâche : ${recipe.task.name}${recipe.task.faction ? ` (${recipe.task.faction})` : ''}` : recipe.taskUnlock ? ' · déblocage de tâche indiqué' : '';
    return `${recipe.count || 1} recette(s) · ${station}${level}${duration}${taskName}`;
  }).join(' ; ');
}
function renderOffersCell(cell, data) {
  const offers = Array.isArray(data.offers) ? data.offers : [];
  if (!offers.length) {
    cell.replaceChildren(make('span', 'Aucune offre renseignée dans buyFromTrader pour cet export', 'phase5-value-muted'));
    return;
  }
  const details = make('details', undefined, 'phase5-disclosure');
  details.append(make('summary', `${offers.length} offre(s) rapportée(s)`));
  const body = make('div', undefined, 'phase5-disclosure__body');
  const list = make('ul');
  for (const offer of offers) {
    const li = make('li');
    const level = offer.level == null ? 'niveau non précisé' : `LL ${offer.level}`;
    const price = offer.price == null ? 'prix non renseigné' : `${numberFr.format(offer.price)} ${offer.currency || ''}`.trim();
    li.textContent = `${offer.trader || 'Trader non résolu'} · ${level} · ${price}${offer.taskUnlock ? ' · déblocage de tâche indiqué' : ''}`;
    list.append(li);
  }
  body.append(list, make('p', 'Snapshot communautaire; à vérifier dans l’interface du marchand.'));
  details.append(body);
  cell.replaceChildren(details);
}
function renderCraftsCell(cell, data) {
  const recipes = Array.isArray(data.recipes) ? data.recipes : [];
  if (!recipes.length) {
    cell.replaceChildren(make('span', 'Aucune recette liée à cet identifiant dans le snapshot', 'phase5-value-muted'));
    return;
  }
  const fragment = document.createDocumentFragment();
  for (const recipe of recipes) {
    const summary = `${recipe.count || 1} produit(s) · ${recipe.station || 'Station non résolue'}${recipe.level == null ? '' : ` ${recipe.level}`}${recipe.durationLabel ? ` · ${recipe.durationLabel}` : ''}`;
    const details = make('details', undefined, 'phase5-disclosure');
    details.append(make('summary', summary));
    const body = make('div', undefined, 'phase5-disclosure__body');
    body.append(make('p', 'Ingrédients du snapshot :'));
    const list = make('ul');
    for (const item of recipe.requiredItems || []) {
      list.append(make('li', `${item.count ?? '—'} × ${item.name || 'ID non résolu'}${item.tool ? ' (outil indiqué)' : ''}`));
    }
    if (!list.children.length) list.append(make('li', 'Ingrédients non détaillés dans cet enregistrement'));
    body.append(list);
    const task = recipe.task?.name
      ? `Tâche associée : ${recipe.task.name}${recipe.task.faction ? ` · variante ${recipe.task.faction}` : ''} (ID ${recipe.taskUnlock}).`
      : recipe.taskUnlock ? `ID de déblocage non résolu : ${recipe.taskUnlock}.` : 'Aucun déblocage de tâche indiqué.';
    body.append(make('p', `Durée, station, ingrédients et déblocage viennent de l’export; non vérifiés dans le client. ${task}`));
    details.append(body);
    fragment.append(details);
  }
  cell.replaceChildren(fragment);
}
function setModeCell(cell, row, mode) {
  const data = modeDataFor(row, mode);
  const field = cell.dataset.modeField;
  if (field === 'offers') renderOffersCell(cell, data);
  else if (field === 'flea') cell.textContent = fleaSummary(data);
  else if (field === 'craft') renderCraftsCell(cell, data);
}
function currentPrice(modeData) {
  const values = (modeData.offers || []).map((entry) => entry.priceRUB).filter((value) => typeof value === 'number' && Number.isFinite(value));
  return values.length ? Math.min(...values) : null;
}
function setActiveMode(region, mode) {
  region.dataset.activeMode = mode;
  for (const button of region.querySelectorAll('[data-mode-set]')) {
    const active = button.dataset.modeSet === mode;
    button.setAttribute('aria-pressed', String(active));
  }
  for (const label of region.querySelectorAll('[data-mode-name]')) label.textContent = MODE_NAMES[mode] || mode;
  for (const row of region.querySelectorAll('[data-p5-row]')) {
    const data = modeDataFor(row, mode);
    for (const cell of row.querySelectorAll('[data-mode-field]')) setModeCell(cell, row, mode);
    row.dataset.traderNames = (data.offers || []).map((entry) => clean(entry.trader)).join(' ');
    const price = currentPrice(data);
    row.dataset.currentPriceRub = price === null ? '' : String(price);
  }
}
function compareFields(kind) {
  if (kind === 'ammo') return [
    ['caliber', 'Calibre', ''], ['ammoType', 'Type', ''], ['damage', 'Dégâts exportés', ''],
    ['penetrationPower', 'Pénétration exportée', ''], ['armorDamage', 'Dégâts d’armure exportés', '%'],
    ['fragmentationChance', 'Fragmentation exportée', '%'], ['initialSpeed', 'Vitesse initiale exportée', 'm/s'],
    ['projectileCount', 'Projectiles par objet', ''],
  ];
  return [
    ['family', 'Famille exportée', ''], ['caliber', 'Calibre', ''], ['fireRate', 'Cadence catalogue', 'coups/min'],
    ['ergonomics', 'Ergonomie arme seule', ''], ['recoilVertical', 'Recul vertical arme seule', ''],
    ['recoilHorizontal', 'Recul horizontal arme seule', ''], ['weight', 'Masse arme seule', 'kg'],
    ['preset', 'Preset par défaut lié', ''], ['presetWeight', 'Masse du preset référencé', 'kg'],
    ['allowedAmmoCount', 'Munitions autorisées (IDs)', ''],
  ];
}
function compareValue(record, field, modeData) {
  if (field === 'offers') return offerSummary(modeData);
  if (field === 'flea') return fleaSummary(modeData);
  if (field === 'craft') return craftSummary(modeData);
  const value = record.metrics?.[field];
  if (field === 'fragmentationChance' && typeof value === 'number') return `${numberFr.format(value * 100)} %`;
  const unit = ({ armorDamage: '%', initialSpeed: 'm/s', weight: 'kg', fireRate: 'coups/min' })[field] || '';
  return formatValue(value, unit);
}
function renderCompare(region, selected, kind) {
  const output = region.querySelector('[data-p5-compare-output]');
  const status = region.querySelector('[data-p5-compare-status]');
  if (!output || !status) return;
  const rows = [...selected].map((id) => region.querySelector(`[data-p5-row][data-id="${CSS.escape(id)}"]`)).filter(Boolean);
  if (rows.length < 2) {
    output.replaceChildren();
    status.textContent = `${rows.length}/3 sélectionné${rows.length === 1 ? '' : 's'} · cochez au moins deux objets.`;
    return;
  }
  const mode = region.dataset.activeMode || 'regular';
  const meleeOnly = kind === 'weapon' && rows.every((row) => row.dataset.group === 'melee');
  const fields = kind === 'ammo'
    ? [...compareFields('ammo'), ['offers', 'Offres de trader · mode choisi', ''], ['flea', 'Marché flea · fraîcheur', ''], ['craft', 'Crafts · mode choisi', '']]
    : [...compareFields('weapon'), ...(meleeOnly ? [['slashDamage', 'Dégâts slash exportés', ''], ['stabDamage', 'Dégâts stab exportés', '']] : []), ['offers', 'Offres de trader · mode choisi', ''], ['flea', 'Marché flea · fraîcheur', '']];
  const scroller = make('div', undefined, 'phase5-table-scroll');
  scroller.tabIndex = 0;
  scroller.setAttribute('role', 'region');
  scroller.setAttribute('aria-label', `Comparaison de ${rows.length} objets en ${MODE_NAMES[mode]}`);
  const table = make('table', undefined, 'phase5-table');
  table.append(make('caption', `Comparaison · ${MODE_NAMES[mode]} · les lignes de prix ne sont pas comparées entre modes`));
  const head = table.createTHead().insertRow();
  const corner = make('th', 'Attribut'); corner.scope = 'col'; head.append(corner);
  const records = [];
  for (const row of rows) {
    const metrics = readJson(row.dataset.metrics, {});
    records.push({ row, metrics, modeData: modeDataFor(row, mode) });
    const th = make('th'); th.scope = 'col'; th.textContent = row.dataset.itemName || row.dataset.id; head.append(th);
  }
  const body = table.createTBody();
  for (const [key, label, unit] of fields) {
    const tr = body.insertRow();
    const th = make('th', label); th.scope = 'row'; tr.append(th);
    for (const record of records) {
      const td = tr.insertCell();
      td.textContent = key === 'fragmentationChance'
        ? compareValue({ metrics: record.metrics }, key, record.modeData)
        : key === 'offers' || key === 'flea' || key === 'craft'
          ? compareValue({ metrics: record.metrics }, key, record.modeData)
          : formatValue(record.metrics[key], unit);
    }
  }
  scroller.append(table);
  output.replaceChildren(scroller);
  status.textContent = `${rows.length}/3 sélectionnés · ${MODE_NAMES[mode]} · comparaison intra-mode.`;
}
function initModeAndCatalog(region, kind) {
  const rows = [...region.querySelectorAll('[data-p5-row]')];
  const selected = new Set();
  const form = region.querySelector('[data-p5-filter-form]');
  const status = region.querySelector('[data-p5-count]');
  const empty = region.querySelector('[data-p5-empty]');
  const table = region.querySelector('[data-p5-table-body]');
  const compareStatus = region.querySelector('[data-p5-compare-status]');
  const clear = region.querySelector('[data-p5-compare-clear]');
  const countText = (count) => `${count} ${count === 1 ? 'objet' : 'objets'}`;
  let previousSort = null;

  function filter() {
    const mode = region.dataset.activeMode || 'regular';
    const search = clean(form?.querySelector('[data-p5-search]')?.value).split(/\s+/).filter(Boolean);
    const caliber = form?.querySelector('[data-p5-caliber]')?.value || '';
    const family = form?.querySelector('[data-p5-family]')?.value || '';
    const type = form?.querySelector('[data-p5-type]')?.value || '';
    const trader = clean(form?.querySelector('[data-p5-trader]')?.value || '');
    const maxLevelValue = form?.querySelector('[data-p5-level]')?.value || '';
    const maxLevel = maxLevelValue ? Number(maxLevelValue) : null;
    const maxBudgetInput = form?.querySelector('[data-p5-budget]')?.value || '';
    const maxBudget = maxBudgetInput ? Number(maxBudgetInput) : null;
    const minRateInput = form?.querySelector('[data-p5-rate]')?.value || '';
    const minRate = minRateInput ? Number(minRateInput) : null;
    const minErgoInput = form?.querySelector('[data-p5-ergo]')?.value || '';
    const minErgo = minErgoInput ? Number(minErgoInput) : null;
    let shown = 0;
    for (const row of rows) {
      const data = modeDataFor(row, mode);
      const haystack = clean(row.dataset.search);
      const tokensOk = search.every((token) => haystack.includes(token));
      const caliberOk = !caliber || row.dataset.caliber === caliber;
      const familyOk = !family || row.dataset.group === family;
      const typeOk = !type || row.dataset.ammoType === type;
      const offerFiltersActive = Boolean(trader || maxLevel !== null || maxBudget !== null);
      const offerOk = !offerFiltersActive || (data.offers || []).some((offer) => {
        const traderMatch = !trader || clean(offer.trader) === trader;
        const levelMatch = maxLevel === null || (offer.level != null && Number(offer.level) <= maxLevel);
        const price = typeof offer.priceRUB === 'number' ? offer.priceRUB : null;
        const budgetMatch = maxBudget === null || (price !== null && price <= maxBudget);
        return traderMatch && levelMatch && budgetMatch;
      });
      const rateValue = row.dataset.rate;
      const rate = rateValue === '' ? null : Number(rateValue);
      const rateOk = minRate === null || (rate !== null && Number.isFinite(rate) && rate >= minRate);
      const ergoValue = row.dataset.ergo;
      const ergo = ergoValue === '' ? null : Number(ergoValue);
      const ergoOk = minErgo === null || (ergo !== null && Number.isFinite(ergo) && ergo >= minErgo);
      const active = tokensOk && caliberOk && familyOk && typeOk && offerOk && rateOk && ergoOk;
      row.hidden = !active;
      if (active) shown += 1;
    }
    if (status) status.textContent = `${countText(shown)} · ${MODE_NAMES[mode]}`;
    if (empty) empty.hidden = shown > 0;
    const sortBy = form?.querySelector('[data-p5-sort]');
    const sort = sortBy?.value || '';
    if (sort && table) {
      const sortField = sortBy.selectedOptions[0]?.dataset.sortField || sort;
      const sorted = [...rows].sort((a, b) => {
        if (sortField === 'name') return clean(a.dataset.sortName).localeCompare(clean(b.dataset.sortName), 'fr') || Number(a.dataset.originalIndex) - Number(b.dataset.originalIndex);
        const readSort = (row) => {
          if (sortField === 'price') return currentPrice(modeDataFor(row, mode));
          const raw = row.dataset[sortField];
          return raw === '' || raw === undefined ? null : Number(raw);
        };
        const aValue = readSort(a);
        const bValue = readSort(b);
        if (aValue === null && bValue === null) return Number(a.dataset.originalIndex) - Number(b.dataset.originalIndex);
        if (aValue === null) return 1;
        if (bValue === null) return -1;
        return bValue - aValue || Number(a.dataset.originalIndex) - Number(b.dataset.originalIndex);
      });
      sorted.forEach((row) => table.append(row));
      previousSort = sort;
    } else if (!sort && previousSort && table) {
      rows.sort((a, b) => Number(a.dataset.originalIndex) - Number(b.dataset.originalIndex)).forEach((row) => table.append(row));
      previousSort = null;
    }
    if (compareStatus) renderCompare(region, selected, kind);
  }

  for (const button of region.querySelectorAll('[data-mode-set]')) {
    button.addEventListener('click', () => {
      if (!MODE_NAMES[button.dataset.modeSet]) return;
      setActiveMode(region, button.dataset.modeSet);
      filter();
    });
  }
  for (const [index, row] of rows.entries()) row.dataset.originalIndex = String(index);
  for (const cell of region.querySelectorAll('[data-mode-field]')) setModeCell(cell, cell.closest('[data-p5-row]'), region.dataset.activeMode || 'regular');
  setActiveMode(region, region.dataset.activeMode || 'regular');

  if (form instanceof HTMLFormElement) {
    form.addEventListener('submit', (event) => { event.preventDefault(); filter(); });
    form.addEventListener('input', filter);
    form.addEventListener('change', filter);
    form.addEventListener('reset', () => setTimeout(filter, 0));
    form.hidden = false;
  }
  for (const checkbox of region.querySelectorAll('[data-compare-pick]')) {
    checkbox.hidden = false;
    checkbox.addEventListener('change', () => {
      const id = checkbox.value;
      if (checkbox.checked && selected.size >= 3) {
        checkbox.checked = false;
        if (compareStatus) compareStatus.textContent = `${selected.size}/3 sélectionnés · limite atteinte, retirez une sélection.`;
        return;
      }
      if (checkbox.checked) selected.add(id); else selected.delete(id);
      renderCompare(region, selected, kind);
    });
  }
  clear?.addEventListener('click', () => {
    selected.clear();
    region.querySelectorAll('[data-compare-pick]').forEach((checkbox) => { checkbox.checked = false; });
    renderCompare(region, selected, kind);
  });
  const controls = region.querySelector('[data-mode-controls]');
  if (controls) controls.hidden = false;
  const compareTools = region.querySelector('[data-p5-compare-tools]');
  if (compareTools) compareTools.hidden = false;
  filter();
}
async function initModCatalog(region) {
  const fallback = region.querySelector('[data-mod-fallback]');
  const host = region.querySelector('[data-mod-table-host]');
  const loading = region.querySelector('[data-mod-loading]');
  if (fallback && host) {
    if (loading) loading.hidden = false;
    // Let the hero and first viewport paint before parsing 1,391 fallback rows.
    await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    const template = document.createElement('template');
    template.innerHTML = fallback.textContent;
    const wrapper = template.content.querySelector('.phase5-table-scroll');
    if (!wrapper || !wrapper.querySelector('[data-p5-table-body]')) throw new Error('Table de compatibilités impossible à hydrater.');
    host.replaceChildren(wrapper);
    fallback.remove();
    if (loading) loading.hidden = true;
  }
  const form = region.querySelector('[data-mod-filter-form]');
  const rows = [...region.querySelectorAll('[data-mod-row]')];
  // Build the same search key from visible cells once, instead of duplicating
  // ~225 KB of per-row data-search attributes in the generated HTML.
  const searchByRow = new Map(rows.map((row) => [
    row,
    clean([...row.cells].filter((_, index) => index !== 3).map((cell) => cell.textContent).join(' ')),
  ]));
  const nameByRow = new Map(rows.map((row) => [row, clean(row.querySelector('.phase5-item-name')?.textContent)]));
  const slotKeysByRow = new Map(rows.map((row) => [
    row,
    row.cells[2]?.querySelector('code')?.textContent.split(' · ').filter(Boolean) || [],
  ]));
  const status = region.querySelector('[data-mod-count]');
  const empty = region.querySelector('[data-mod-empty]');
  const list = region.querySelector('[data-p5-table-body]');
  let previousSort = null;
  function render() {
    const query = clean(form?.querySelector('[data-mod-search]')?.value).split(/\s+/).filter(Boolean);
    const slot = form?.querySelector('[data-mod-slot]')?.value || '';
    const family = form?.querySelector('[data-mod-family]')?.value || '';
    let count = 0;
    for (const row of rows) {
      const text = searchByRow.get(row) || '';
      const active = query.every((word) => text.includes(word))
        && (!slot || slotKeysByRow.get(row)?.includes(slot))
        && (!family || row.dataset.families.split(' ').includes(family));
      row.hidden = !active;
      if (active) count += 1;
    }
    if (status) status.textContent = `${numberFr.format(count)} modification(s) compatible(s) avec le filtre`;
    if (empty) empty.hidden = count > 0;
    const sortBy = form?.querySelector('[data-mod-sort]');
    const sort = sortBy?.value || '';
    if (sort !== previousSort && list) {
      const field = sortBy?.selectedOptions[0]?.dataset.sortField || sort;
      const sorted = [...rows].sort((a, b) => {
        if (field === 'name') return (nameByRow.get(a) || '').localeCompare(nameByRow.get(b) || '', 'fr') || Number(a.dataset.originalIndex) - Number(b.dataset.originalIndex);
        return Number(b.dataset[field] || 0) - Number(a.dataset[field] || 0) || Number(a.dataset.originalIndex) - Number(b.dataset.originalIndex);
      });
      sorted.forEach((row) => list.append(row));
      previousSort = sort;
    }
  }
  rows.forEach((row, index) => { row.dataset.originalIndex = String(index); });
  if (form instanceof HTMLFormElement) {
    form.hidden = false;
    form.addEventListener('submit', (event) => { event.preventDefault(); render(); });
    form.addEventListener('input', render);
    form.addEventListener('change', render);
    form.addEventListener('reset', () => setTimeout(render, 0));
  }
  render();
}
function initChart(region) {
  const form = region.querySelector('[data-p5-chart-filter]');
  const points = [...region.querySelectorAll('[data-chart-point]')];
  const status = region.querySelector('[data-chart-count]');
  const chartEmpty = region.querySelector('[data-chart-empty]');
  const tableRegion = document.querySelector('[data-p5-ammo]');
  function render() {
    const search = clean(form?.querySelector('[data-chart-search]')?.value).split(/\s+/).filter(Boolean);
    const caliber = form?.querySelector('[data-chart-caliber]')?.value || '';
    let count = 0;
    for (const point of points) {
      const active = search.every((word) => clean(point.dataset.search).includes(word))
        && (!caliber || point.dataset.caliber === caliber);
      if (active) point.removeAttribute('hidden'); else point.setAttribute('hidden', '');
      if (active) count += 1;
    }
    if (status) status.textContent = `${numberFr.format(count)} points de type bullet · stats communes aux exports du 18/11`;
    if (chartEmpty) chartEmpty.hidden = count > 0;
    if (tableRegion) {
      const tableForm = tableRegion.querySelector('[data-p5-filter-form]');
      const tableSearch = tableForm?.querySelector('[data-p5-search]');
      const tableCaliber = tableForm?.querySelector('[data-p5-caliber]');
      if (tableSearch) tableSearch.value = form?.querySelector('[data-chart-search]')?.value || '';
      if (tableCaliber) tableCaliber.value = caliber;
      tableForm?.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }
  if (form instanceof HTMLFormElement) {
    form.hidden = false;
    form.addEventListener('submit', (event) => { event.preventDefault(); render(); });
    form.addEventListener('input', render);
    form.addEventListener('change', render);
    form.addEventListener('reset', () => setTimeout(render, 0));
  }
  render();
}
async function enhanceFamilies() {
  for (const region of document.querySelectorAll('[data-p5-catalog]')) initModeAndCatalog(region, 'weapon');
  for (const region of document.querySelectorAll('[data-p5-ammo]')) initModeAndCatalog(region, 'ammo');
  for (const region of document.querySelectorAll('[data-p5-chart]')) initChart(region);
  for (const region of document.querySelectorAll('[data-p5-mods]')) await initModCatalog(region);
  document.documentElement.dataset.phase5Ready = 'true';
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', enhanceFamilies, { once: true });
else enhanceFamilies();
