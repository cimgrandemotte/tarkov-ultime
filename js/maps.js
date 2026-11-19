import { normalizeText } from './utils.js';

const modeNames = {
  regular: 'PvP permanent',
  pve: 'PvE Zone',
  'pvp-season': 'PvP Seasonal',
};

function initMapModes(root = document) {
  const switcher = root.querySelector('[data-map-mode-switch]');
  if (!switcher) return;
  const buttons = [...switcher.querySelectorAll('[data-map-mode]')];
  const panels = [...root.querySelectorAll('[data-map-mode-panel]')];
  if (!buttons.length || !panels.length) return;

  function select(mode) {
    for (const button of buttons) {
      button.setAttribute('aria-pressed', String(button.dataset.mapMode === mode));
    }
    for (const panel of panels) {
      panel.hidden = panel.dataset.mapModePanel !== mode;
    }
  }

  switcher.addEventListener('click', event => {
    const button = event.target.closest('[data-map-mode]');
    if (button && switcher.contains(button)) select(button.dataset.mapMode);
  });
  switcher.hidden = false;
  select(buttons.find(button => button.dataset.mapMode === 'regular')?.dataset.mapMode ?? buttons[0].dataset.mapMode);
}

function initHub(root = document) {
  const form = root.querySelector('[data-map-filter]');
  if (!form) return;
  const grid = root.querySelector('[data-map-grid]');
  const cards = [...(grid?.querySelectorAll('[data-map-card]') ?? [])];
  const query = form.querySelector('[data-map-query]');
  const difficulty = form.querySelector('[data-map-difficulty]');
  const modeSelect = form.querySelector('[data-map-mode-select]');
  const status = form.querySelector('[data-map-filter-status]');
  const empty = root.querySelector('[data-map-empty]');
  const compareStatus = root.querySelector('[data-map-compare-status]');
  const compareTable = root.querySelector('[data-map-compare-table]');
  const checkboxes = [...root.querySelectorAll('[data-map-compare]')];
  if (!grid || !cards.length || !query || !difficulty || !modeSelect || !status || !empty) return;

  const cardBySlug = new Map(cards.map(card => [card.dataset.mapSlug, card]));
  const parsedStats = new Map();
  for (const card of cards) {
    try {
      parsedStats.set(card.dataset.mapSlug, JSON.parse(card.dataset.mapStats));
    } catch {
      parsedStats.set(card.dataset.mapSlug, {});
    }
  }

  function activeMode() {
    return modeNames[modeSelect.value] ? modeSelect.value : 'regular';
  }

  function updateCardStats() {
    const mode = activeMode();
    for (const card of cards) {
      const values = parsedStats.get(card.dataset.mapSlug)?.[mode];
      if (!values) continue;
      const player = card.querySelector('[data-map-stat="players"]');
      const duration = card.querySelector('[data-map-stat="duration"]');
      if (player) player.textContent = values.playersLabel;
      if (duration) duration.textContent = values.durationLabel;
    }
  }

  function setCompareCell(name, value) {
    const cell = compareTable?.querySelector(`[data-compare-cell="${name}"]`);
    if (cell) cell.textContent = value || '—';
  }

  function updateComparison(message = '') {
    if (!compareTable) return;
    const selected = checkboxes.filter(input => input.checked).slice(0, 2);
    const mode = activeMode();
    const modeLabel = compareTable.querySelector('[data-map-compare-mode-label]');
    if (modeLabel) modeLabel.textContent = modeNames[mode];

    for (const side of ['a', 'b']) {
      const input = selected[side === 'a' ? 0 : 1];
      const card = input ? cardBySlug.get(input.value) : null;
      const values = card ? parsedStats.get(card.dataset.mapSlug)?.[mode] : null;
      const nameCell = compareTable.querySelector(`[data-compare-cell="${side}-name"]`);
      if (nameCell) nameCell.textContent = card?.querySelector('h3')?.textContent.trim() || '—';
      setCompareCell(`${side}-players`, values?.playersLabel);
      setCompareCell(`${side}-duration`, values?.durationLabel);
      setCompareCell(`${side}-extracts`, values ? String(values.extractEntries) : '—');
      setCompareCell(`${side}-access`, card?.querySelector('.map-proof')?.textContent.trim() || '—');
      const heading = compareTable.querySelector(`[data-compare-heading="${side}"]`);
      if (heading) heading.textContent = card?.querySelector('h3')?.textContent.trim() || `Lieu ${side.toUpperCase()}`;
    }

    if (message) {
      compareStatus.textContent = message;
    } else if (selected.length === 2) {
      compareStatus.textContent = `Comparaison prête · ${selected[0].value} / ${selected[1].value} · ${modeNames[mode]}.`;
    } else if (selected.length === 1) {
      compareStatus.textContent = '1 lieu sélectionné sur 2. Choisissez une seconde carte.';
    } else {
      compareStatus.textContent = 'Choisissez deux lieux pour les comparer.';
    }
  }

  function updateFilters() {
    const words = normalizeText(query.value).split(' ').filter(Boolean);
    const selectedDifficulty = difficulty.value;
    let visible = 0;
    for (const card of cards) {
      const haystack = normalizeText(`${card.dataset.mapSearch ?? ''} ${card.textContent}`);
      const matchesText = words.every(word => haystack.includes(word));
      const matchesDifficulty = selectedDifficulty === 'all' || card.dataset.mapDifficulty === selectedDifficulty;
      const show = matchesText && matchesDifficulty;
      card.hidden = !show;
      if (show) visible++;
    }
    empty.hidden = visible > 0;
    const mode = activeMode();
    const label = modeNames[mode];
    status.textContent = `${visible} / ${cards.length} lieux · métadonnées : ${label}`;
    updateCardStats();
    updateComparison();
  }

  for (const checkbox of checkboxes) {
    checkbox.addEventListener('change', () => {
      const checked = checkboxes.filter(input => input.checked);
      if (checked.length > 2) {
        checkbox.checked = false;
        updateComparison('Deux cartes maximum. Décochez un lieu avant d’en choisir un autre.');
        return;
      }
      updateComparison();
    });
    const label = checkbox.closest('.map-compare-check');
    if (label) label.hidden = false;
  }

  query.addEventListener('input', updateFilters);
  difficulty.addEventListener('change', updateFilters);
  modeSelect.addEventListener('change', updateFilters);
  form.addEventListener('reset', () => window.setTimeout(updateFilters, 0));
  form.hidden = false;
  updateFilters();
}

function initialize() {
  initMapModes();
  initHub();
  document.documentElement.dataset.mapsReady = 'true';
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initialize, { once: true });
} else {
  initialize();
}
