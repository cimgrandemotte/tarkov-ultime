const body = document.body;
const root = body.dataset.phase7Root || '../../';
const dataUrl = `${root}js/data/phase7.json`;

const el = (tag, attrs = {}, text = '') => {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === 'class') node.className = value;
    else if (key === 'dataset') Object.assign(node.dataset, value);
    else if (key === 'checked') node.checked = Boolean(value);
    else if (key === 'selected') node.selected = Boolean(value);
    else if (key === 'hidden') node.hidden = Boolean(value);
    else if (key === 'htmlFor') node.htmlFor = value;
    else node.setAttribute(key, value);
  }
  if (text !== '') node.textContent = text;
  return node;
};
const byId = (id) => document.getElementById(id);
const list = (value) => Array.isArray(value) ? value : [];
const modeLabels = { regular: 'PvP permanent', pve: 'PvE Zone', 'pvp-season': 'PvP Seasonal' };
const fmtNum = (value) => {
  const n = Number(value);
  return Number.isFinite(n) ? new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 }).format(n) : '—';
};
const fmtRep = (value) => {
  const n = Number(value);
  return Number.isFinite(n) ? new Intl.NumberFormat('fr-FR', { minimumFractionDigits: 1, maximumFractionDigits: 2 }).format(n) : '—';
};
const fmtDuration = (seconds) => {
  const n = Number(seconds);
  if (!Number.isFinite(n) || n < 0) return 'Durée non renseignée';
  if (n < 60) return `${Math.round(n)} s`;
  const mins = Math.round(n / 60);
  const hours = Math.floor(mins / 60);
  const rest = mins % 60;
  return hours ? `${hours} h ${String(rest).padStart(2, '0')} min` : `${mins} min`;
};
const safeStored = (key, fallback = {}) => {
  try { return JSON.parse(localStorage.getItem(key) || 'null') || fallback; }
  catch { return fallback; }
};
const saveStored = (key, value) => {
  try { localStorage.setItem(key, JSON.stringify(value)); }
  catch { /* Stockage désactivé ou plein : la page reste utilisable en mémoire. */ }
};
const removeStored = (key) => {
  try { localStorage.removeItem(key); }
  catch { /* Le stockage local est facultatif. */ }
};
const announce = (node, message) => { if (node) node.textContent = message; };
const addOption = (select, value, label, selected = false) => select.append(el('option', { value, selected }, label));
const taskLink = (task, mode) => `${root}pages/quests/?mode=${encodeURIComponent(mode)}&task=${encodeURIComponent(task.id)}`;
const tag = (text, warning = false) => el('span', { class: `phase7-tag${warning ? ' phase7-tag--warn' : ''}` }, text);
const modeForPage = (selector) => selector?.value || 'regular';

let data;
try {
  const response = await fetch(dataUrl, { cache: 'no-cache' });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  data = await response.json();
} catch (error) {
  const message = `Les données PHASE_7 ne sont pas disponibles (${error.message}). Vérifiez que js/data/phase7.json a été généré avec les snapshots datés.`;
  document.querySelectorAll('[data-p7-quest-list], [data-p7-hideout-stations], [data-p7-craft-detail], [data-p7-kappa-items], [data-p7-tree-panel], [data-p7-trader-levels]').forEach((node) => announce(node, message));
  console.error(message);
}

if (data) {
  document.querySelectorAll('[data-p7-static-fallback]').forEach((node) => { node.hidden = true; });
  const modeSelects = [...document.querySelectorAll('[data-p7-mode]')];
  modeSelects.forEach((select) => {
    const params = new URLSearchParams(location.search);
    const requestedMode = params.get('mode');
    if (requestedMode && data.modes[requestedMode]) select.value = requestedMode;
    select.addEventListener('change', () => {
      const url = new URL(location.href);
      url.searchParams.set('mode', select.value);
      history.replaceState(null, '', url);
      document.dispatchEvent(new CustomEvent('p7:mode', { detail: { mode: select.value } }));
    });
  });

  // ── Traders: LL et spécialités ──────────────────────────────────────────
  const classicTraderIds = [
    '54cb50c76803fa8b248b4571', '54cb57776803fa99248b456e',
    '58330581ace78e27b8b10cee', '5935c25fb3acc3127c3d8cd9',
    '5a7c2eca46aef81a7ca2145d', '5ac3b934156ae10c4430e83c',
    '5c0647fdd443bc2504c2d371',
  ];
  const classicPlusFence = [
    '54cb50c76803fa8b248b4571', '54cb57776803fa99248b456e',
    '579dc571d53a0658a154fbec', '58330581ace78e27b8b10cee',
    '5935c25fb3acc3127c3d8cd9', '5a7c2eca46aef81a7ca2145d',
    '5ac3b934156ae10c4430e83c', '5c0647fdd443bc2504c2d371',
  ];
  const renderTraderLevels = (tbody, mode, traderId, filter = 'all') => {
    if (!tbody) return;
    tbody.replaceChildren();
    const trader = data.modes[mode]?.traders.find((row) => row.id === traderId);
    if (!trader) {
      tbody.append(el('tr', {}, 'Aucune ligne trader dans ce snapshot.'));
      return;
    }
      const isFence = trader.normalizedName === 'fence';
      const isSpecial = ['lightkeeper','ref'].includes(trader.normalizedName);
      const rows = list(trader.levels).filter((row) => filter === 'all' || Number(row.level) >= Number(filter));
    if (!rows.length) {
      const tr = el('tr');
      tr.append(el('td', { colspan: 4 }, 'Aucun palier correspondant.'));
      tbody.append(tr);
      return;
    }
    rows.forEach((row) => {
      const tr = el('tr');
      const levelLabel = isFence ? `Fence · niveau ${row.level}` : isSpecial ? `Palier ${row.level}` : `LL${row.level}`;
      tr.append(el('th', { scope: 'row' }, levelLabel));
      tr.append(el('td', {}, row.requiredPlayerLevel == null ? '—' : fmtNum(row.requiredPlayerLevel)));
      tr.append(el('td', {}, row.requiredReputation == null ? '—' : fmtRep(row.requiredReputation)));
      tr.append(el('td', {}, row.requiredCommerce == null ? 'Non renseigné' : `${fmtNum(row.requiredCommerce)} · ${row.requiredCommerce === 0 ? 'retiré / nul dans l’export' : 'valeur exportée'}`));
      tbody.append(tr);
    });
  };

  document.querySelectorAll('[data-p7-trader-levels]').forEach((tbody) => {
    const mode = document.querySelector('[data-p7-mode]')?.value || 'regular';
    const filter = document.querySelector('[data-p7-level-filter]')?.value || 'all';
    renderTraderLevels(tbody, mode, tbody.dataset.traderId, filter);
    const note = document.querySelector('[data-p7-trader-level-note]');
    const norm = data.modes[mode]?.traders.find((row) => row.id === tbody.dataset.traderId)?.normalizedName;
    if (note) {
      note.textContent = norm === 'lightkeeper'
        ? 'Le trader endpoint ne donne ici qu’un niveau technique; il ne décrit pas les conditions de déblocage de Lightkeeper.'
        : norm === 'fence'
          ? 'Fence suit une progression Scav/réputation spécifique. Ne transposez pas ses niveaux exportés sur les LL2–LL4 classiques.'
          : norm === 'ref'
            ? 'Ref dispose de paliers dédiés dans le flux; la synchronisation Arena reste limitée au mode et à la période décrits par BSG.'
            : 'Le volume commercial est à zéro dans l’export après la refonte 1.1.0; niveau et réputation ne prouvent pas qu’un profil a déjà débloqué le palier.';
    }
  });
  document.querySelectorAll('[data-p7-mode], [data-p7-level-filter]').forEach((select) => select.addEventListener('change', () => {
    const tbody = document.querySelector('[data-p7-trader-levels]');
    if (tbody) renderTraderLevels(tbody, document.querySelector('[data-p7-mode]')?.value || 'regular', tbody.dataset.traderId, document.querySelector('[data-p7-level-filter]')?.value || 'all');
  }));

  const loyaltyTable = document.querySelector('[data-p7-loyalty-table]');
  const loyaltyMode = document.querySelector('[data-p7-loyalty-mode]');
  const loyaltyTier = document.querySelector('[data-p7-loyalty-tier]');
  const loyaltyNote = document.querySelector('[data-p7-loyalty-note]');
  const renderLoyaltyTable = () => {
    if (!loyaltyTable) return;
    const mode = modeForPage(loyaltyMode);
    const tier = loyaltyTier?.value || 'all';
    loyaltyTable.replaceChildren();
    const traders = data.modes[mode]?.traders || [];
    let count = 0;
    classicPlusFence.forEach((id) => {
      const trader = traders.find((row) => row.id === id);
      if (!trader) return;
      const profile = data.traders.find((p) => p.id === id);
      const rows = list(trader.levels).filter((r) => r.level !== 1 || trader.normalizedName === 'fence')
        .filter((r) => tier === 'all' || Number(r.level) >= Number(tier));
      rows.forEach((row) => {
        if (row.level === 1 && trader.normalizedName !== 'fence') return;
        const tr = el('tr');
        const name = profile?.name || trader.nameFr;
        tr.append(el('th', { scope: 'row' }, name));
        tr.append(el('td', {}, trader.normalizedName === 'fence' ? `Fence ${row.level}` : `LL${row.level}`));
        tr.append(el('td', {}, row.requiredPlayerLevel == null ? '—' : fmtNum(row.requiredPlayerLevel)));
        tr.append(el('td', {}, row.requiredReputation == null ? '—' : fmtRep(row.requiredReputation)));
        tr.append(el('td', {}, row.requiredCommerce == null ? '—' : fmtNum(row.requiredCommerce)));
        loyaltyTable.append(tr);
        count += 1;
      });
    });
    announce(loyaltyNote, `${modeLabels[mode]} · ${count} lignes de seuils présentes. Fence est affiché à part; ses paliers ne sont pas équivalents aux LL classiques.`);
  };
  [loyaltyMode, loyaltyTier].filter(Boolean).forEach((node) => node.addEventListener('change', renderLoyaltyTable));
  renderLoyaltyTable();

  const traderCards = [...document.querySelectorAll('[data-p7-trader-card]')];
  const specialty = document.querySelector('[data-p7-trader-specialty]');
  const kind = document.querySelector('[data-p7-trader-kind]');
  const traderCount = document.querySelector('[data-p7-trader-count]');
  const filterTraderCards = () => {
    if (!traderCards.length) return;
    const spec = specialty?.value || 'all';
    const type = kind?.value || 'all';
    let visible = 0;
    traderCards.forEach((card) => {
      const show = (spec === 'all' || card.dataset.specialty === spec) && (type === 'all' || card.dataset.traderKind === type);
      card.hidden = !show;
      if (show) visible += 1;
    });
    announce(traderCount, `${visible} interlocuteurs affichés sur ${traderCards.length}.`);
  };
  [specialty, kind].filter(Boolean).forEach((node) => node.addEventListener('change', filterTraderCards));
  document.querySelector('[data-p7-trader-reset]')?.addEventListener('click', () => {
    if (specialty) specialty.value = 'all';
    if (kind) kind.value = 'all';
    filterTraderCards();
  });
  filterTraderCards();

  document.querySelectorAll('[data-trader-card-meta]').forEach((node) => {
    const trader = data.modes.regular.traders.find((row) => row.id === node.dataset.traderId);
    const profile = data.traders.find((row) => row.id === node.dataset.traderId);
    if (trader && profile) node.textContent = profile.slug === 'lightkeeper' ? 'Accès par progression narrative · conditions à vérifier' : `${list(trader.levels).length} niveau(x) dans l’export · stock non publié`;
  });

  document.querySelectorAll('[data-p7-trader-task-list]').forEach((container) => {
    const id = container.dataset.traderId;
    const modeSelect = document.querySelector('[data-p7-mode]');
    const search = document.querySelector('[data-p7-trader-task-search]');
    const flagFilter = document.querySelector('[data-p7-trader-task-filter]');
    const count = document.querySelector('[data-p7-trader-task-count]');
    const render = () => {
      const mode = modeSelect?.value || 'regular';
      const query = (search?.value || '').trim().toLocaleLowerCase('fr');
      const flag = flagFilter?.value || 'all';
      const all = (data.modes[mode]?.tasks || []).filter((task) => task.traderId === id);
      const filtered = all.filter((task) => {
        if (flag === 'kappa' && !task.kappaRequired) return false;
        if (flag === 'lightkeeper' && !task.lightkeeperRequired) return false;
        const hay = `${task.nameFr} ${task.nameEn} ${task.mapNames.join(' ')} ${task.normalizedName}`.toLocaleLowerCase('fr');
        return !query || hay.includes(query);
      });
      container.replaceChildren();
      filtered.slice(0, 18).forEach((task) => {
        const li = el('li', { class: 'phase7-task-row' });
        const copy = el('div');
        const anchor = el('a', { href: taskLink(task, mode) }, task.nameFr);
        copy.append(anchor);
        const meta = el('div', { class: 'phase7-task-row__meta' });
        meta.append(tag(`Niveau ${task.minPlayerLevel ?? '—'}`));
        if (task.mapNames.length) meta.append(tag(task.mapNames.join(' · ')));
        if (task.kappaRequired) meta.append(tag('Kappa · export'));
        if (task.lightkeeperRequired) meta.append(tag('Lightkeeper · export', true));
        copy.append(meta);
        li.append(copy, el('span', { class: 'phase7-task-row__side' }, `${task.objectiveCount} objectif(s)`));
        container.append(li);
      });
      announce(count, `${filtered.length} tâche(s) dans le snapshot ${modeLabels[mode]}; ${Math.min(filtered.length,18)} affichée(s).`);
    };
    [modeSelect, search, flagFilter].filter(Boolean).forEach((node) => node.addEventListener('input', render));
    [modeSelect, flagFilter].filter(Boolean).forEach((node) => node.addEventListener('change', render));
    render();
  });

  // ── Quêtes: recherche, filtres et état local ────────────────────────────
  const questList = document.querySelector('[data-p7-quest-list]');
  const questMode = document.querySelector('[data-p7-mode]');
  const questSearch = document.querySelector('[data-p7-quest-search]');
  const questTrader = document.querySelector('[data-p7-quest-trader]');
  const questMap = document.querySelector('[data-p7-quest-map]');
  const questLevel = document.querySelector('[data-p7-quest-level]');
  const questProgress = document.querySelector('[data-p7-quest-progress]');
  const questKappa = document.querySelector('[data-p7-quest-kappa]');
  const questLightkeeper = document.querySelector('[data-p7-quest-lightkeeper]');
  const questCount = document.querySelector('[data-p7-quest-count]');
  const questMore = document.querySelector('[data-p7-quest-more]');
  let questRowsLimit = 70;
  const questStateKey = (mode) => `tug-p7-quest-progress:${mode}`;
  const currentQuestState = (mode) => safeStored(questStateKey(mode), {});
  const populateQuestFilters = (mode) => {
    if (!questTrader || !questMap) return;
    const oldTrader = questTrader.value;
    const oldMap = questMap.value;
    const tasks = data.modes[mode]?.tasks || [];
    const traderMap = new Map();
    const mapSet = new Set();
    tasks.forEach((task) => {
      if (task.traderId) traderMap.set(task.traderId, task.traderNameFr || 'Trader non résolu');
      task.mapNames.forEach((name) => mapSet.add(name));
    });
    questTrader.replaceChildren(); addOption(questTrader, 'all', 'Tous les traders');
    [...traderMap.entries()].sort((a,b) => a[1].localeCompare(b[1], 'fr')).forEach(([id,name]) => addOption(questTrader,id,name));
    if (traderMap.has(oldTrader)) questTrader.value = oldTrader;
    questMap.replaceChildren(); addOption(questMap, 'all', 'Toutes les cartes');
    [...mapSet].sort((a,b) => a.localeCompare(b,'fr')).forEach((name) => addOption(questMap,name,name));
    if (mapSet.has(oldMap)) questMap.value = oldMap;
  };
  const renderQuestStats = () => {
    const holder = document.querySelector('[data-p7-quest-stats]');
    if (!holder) return;
    holder.replaceChildren();
    Object.entries(data.modes).forEach(([mode,row]) => {
      const audit=row.dependencyAudit||{};
      [[row.metrics.tasks,`${modeLabels[mode]} · tâches`],[row.metrics.missingTaskReferences.length,`${modeLabels[mode]} · prérequis absents de l’export`],[audit.cycleCount??0,`${modeLabels[mode]} · cycles détectés`],[audit.tasksWithMultiplePrerequisites??0,`${modeLabels[mode]} · tâches avec plusieurs prérequis listés`]].forEach(([value,label])=>{
        const card=el('div',{class:'phase7-stat'});card.append(el('strong',{},fmtNum(value)),el('span',{},label));holder.append(card);
      });
    });
    const reg=data.modes.regular.metrics;
    const kappa=el('div',{class:'phase7-stat'});kappa.append(el('strong',{},String(reg.kappaFlagged)),el('span',{},'balises Kappa · PvP export'));holder.append(kappa);
    const missing=el('div',{class:'phase7-stat'});missing.append(el('strong',{},String(data.issue886MissingIds.length)),el('span',{},'IDs du signalement #886 absents'));holder.append(missing);
    const coverage=el('div',{class:'phase7-stat'});coverage.append(el('strong',{},`${reg.taskNamesMissingFrench}`),el('span',{},'nom français manquant · regular'));holder.append(coverage);
  };
  const renderQuests = () => {
    if (!questList) return;
    const mode = questMode?.value || 'regular';
    populateQuestFilters(mode);
    const q = (questSearch?.value || '').trim().toLocaleLowerCase('fr');
    const traderId = questTrader?.value || 'all';
    const mapName = questMap?.value || 'all';
    const levelMode = questLevel?.value || 'all';
    const progressFilter = questProgress?.value || 'all';
    const needKappa = Boolean(questKappa?.checked);
    const needLk = Boolean(questLightkeeper?.checked);
    const progress = currentQuestState(mode);
    const all = data.modes[mode]?.tasks || [];
    const filtered = all.filter((task) => {
      if (traderId !== 'all' && task.traderId !== traderId) return false;
      if (mapName !== 'all' && !task.mapNames.includes(mapName)) return false;
      if (needKappa && !task.kappaRequired) return false;
      if (needLk && !task.lightkeeperRequired) return false;
      const lvl = Number(task.minPlayerLevel);
      if (levelMode === '1' && Number.isFinite(lvl) && lvl > 10) return false;
      if (levelMode !== 'all' && levelMode !== '1' && Number.isFinite(lvl) && lvl < Number(levelMode)) return false;
      const state = progress[task.id] || 'todo';
      if (progressFilter === 'done' && state !== 'done') return false;
      if (progressFilter === 'todo' && state === 'done') return false;
      const hay = `${task.nameFr} ${task.nameEn} ${task.normalizedName} ${task.traderNameFr || ''} ${task.mapNames.join(' ')} ${task.id}`.toLocaleLowerCase('fr');
      return !q || hay.includes(q);
    });
    questList.replaceChildren();
    filtered.slice(0, questRowsLimit).forEach((task) => {
      const row = el('tr');
      const head = el('th', { scope: 'row' });
      const title = el('a', { href: task.wikiLink || taskLink(task,mode), rel: task.wikiLink ? 'noopener noreferrer' : '' }, task.nameFr);
      head.append(title, el('small', {}, task.nameEn));
      row.append(head);
      row.append(el('td', {}, task.traderNameFr || 'Non résolu'));
      row.append(el('td', {}, task.minPlayerLevel == null ? '—' : fmtNum(task.minPlayerLevel)));
      row.append(el('td', {}, task.mapNames.length ? task.mapNames.join(', ') : 'Non renseignée'));
      const badges = el('td'); const badgeWrap = el('div', { class: 'phase7-row-badges' });
      if (task.kappaRequired) badgeWrap.append(tag('Kappa', false));
      if (task.lightkeeperRequired) badgeWrap.append(tag('Lightkeeper', true));
      if (task.taskRequirements.length) badgeWrap.append(tag(`${task.taskRequirements.length} prérequis`));
      if (task.objectiveCount) badgeWrap.append(tag(`${task.objectiveCount} objectifs`));
      if (!badgeWrap.childNodes.length) badgeWrap.append(tag('Aucune balise exportée'));
      badges.append(badgeWrap); row.append(badges);
      const statusCell = el('td');
      const status = el('select', { class: 'phase7-local-status', 'aria-label': `Progression locale : ${task.nameFr}`, dataset: { questId:task.id } });
      [['todo','À faire'],['doing','En cours'],['done','Terminée']].forEach(([value,label]) => addOption(status,value,label,(progress[task.id] || 'todo')===value));
      status.addEventListener('change', () => { const next=currentQuestState(mode); if(status.value==='todo') delete next[task.id]; else next[task.id]=status.value; saveStored(questStateKey(mode),next); renderQuests(); });
      statusCell.append(status); row.append(statusCell);
      questList.append(row);
    });
    if (!filtered.length) {
      const row=el('tr'); row.append(el('td',{colspan:6},'Aucune tâche ne correspond à ces filtres dans le snapshot sélectionné.')); questList.append(row);
    }
    const shown=Math.min(filtered.length,questRowsLimit);
    announce(questCount, `${shown} tâche(s) affichée(s) sur ${filtered.length} résultat(s) · ${all.length} dans le snapshot ${modeLabels[mode]}.`);
    if (questMore) {
      questMore.hidden = shown >= filtered.length;
      questMore.textContent = `Afficher ${Math.min(70, Math.max(0, filtered.length - shown))} tâches supplémentaires`;
    }
  };
  [questMode,questSearch,questTrader,questMap,questLevel,questProgress,questKappa,questLightkeeper].filter(Boolean).forEach((node) => {
    node.addEventListener('input', () => { questRowsLimit=70; renderQuests(); });
    node.addEventListener('change', () => { questRowsLimit=70; renderQuests(); });
  });
  questMore?.addEventListener('click', () => { questRowsLimit += 70; renderQuests(); });
  document.querySelector('[data-p7-quest-reset]')?.addEventListener('click', () => {
    if (questSearch) questSearch.value='';
    if (questTrader) questTrader.value='all';
    if (questMap) questMap.value='all';
    if (questLevel) questLevel.value='all';
    if (questProgress) questProgress.value='all';
    if (questKappa) questKappa.checked=false;
    if (questLightkeeper) questLightkeeper.checked=false;
    questRowsLimit=70; renderQuests();
  });
  const params = new URLSearchParams(location.search);
  if (questList) {
    const requestedTask=params.get('task');
    const requestedMode=params.get('mode');
    const requestedTrader=params.get('trader');
    if (requestedMode && data.modes[requestedMode] && questMode) questMode.value=requestedMode;
    if (requestedTask) {
      const requestedModeHasTask=requestedMode && data.modes[requestedMode] && (data.modes[requestedMode].tasks||[]).some((task)=>task.id===requestedTask);
      const foundMode=requestedModeHasTask ? requestedMode : Object.keys(data.modes).find((mode)=>(data.modes[mode].tasks||[]).some((task)=>task.id===requestedTask));
      if (foundMode && questMode) questMode.value=foundMode;
      if (questSearch) questSearch.value=requestedTask;
    }
    if (requestedTrader && questTrader) {
      const mode=questMode?.value||'regular';
      const t=(data.modes[mode].traders||[]).find((row)=>row.normalizedName===requestedTrader);
      if (t) questTrader.value=t.id;
    }
  }
  renderQuestStats(); renderQuests();

  // ── Arbre: liens explicites, logique inconnue laissée visible ───────────
  const treeMode=document.querySelector('[data-p7-mode]');
  const treeTrader=document.querySelector('[data-p7-tree-trader]');
  const treeSearch=document.querySelector('[data-p7-tree-search]');
  const treeTaskSelect=document.querySelector('[data-p7-tree-task]');
  const treePanel=document.querySelector('[data-p7-tree-panel]');
  const treeCount=document.querySelector('[data-p7-tree-count]');
  const treeKey=(mode)=>`tug-p7-tree:${mode}`;
  const treeState=(mode)=>safeStored(treeKey(mode),{});
  const populateTreeTraders=(mode)=>{
    if(!treeTrader)return;
    const old=treeTrader.value; const rows=data.modes[mode].traders||[];
    treeTrader.replaceChildren(); addOption(treeTrader,'all','Tous');
    rows.filter((r)=>r.id && (data.modes[mode].tasks||[]).some((t)=>t.traderId===r.id)).sort((a,b)=>a.nameFr.localeCompare(b.nameFr,'fr')).forEach((r)=>addOption(treeTrader,r.id,r.nameFr));
    if([...treeTrader.options].some((o)=>o.value===old))treeTrader.value=old;
  };
  const populateTreeTasks=()=>{
    if(!treeTaskSelect)return;
    const mode=treeMode?.value||'regular'; populateTreeTraders(mode);
    const trader=treeTrader?.value||'all'; const q=(treeSearch?.value||'').trim().toLocaleLowerCase('fr');
    const all=data.modes[mode].tasks||[];
    const filtered=all.filter((t)=>(trader==='all'||t.traderId===trader)&&(!q||`${t.nameFr} ${t.nameEn} ${t.mapNames.join(' ')} ${t.id}`.toLocaleLowerCase('fr').includes(q)));
    const previous=treeTaskSelect.value;
    treeTaskSelect.replaceChildren(); addOption(treeTaskSelect,'','Choisissez une tâche');
    filtered.forEach((t)=>addOption(treeTaskSelect,t.id,`${t.nameFr} · niv. ${t.minPlayerLevel??'—'}${t.kappaRequired?' · Kappa':''}`));
    if(filtered.some((t)=>t.id===previous))treeTaskSelect.value=previous;
    announce(treeCount,`${filtered.length} tâche(s) correspondante(s) sur ${all.length} · ${modeLabels[mode]}.`);
    renderTreeTask();
  };
  const renderTreeTask=()=>{
    if(!treePanel)return;
    const mode=treeMode?.value||'regular'; const id=treeTaskSelect?.value;
    const task=data.modes[mode].tasks.find((t)=>t.id===id);
    treePanel.replaceChildren();
    if(!task){treePanel.append(el('p',{},'Sélectionnez une tâche pour afficher ses prérequis déclarés.'));return;}
    const panel=el('article',{class:'phase7-tree-node'});
    panel.append(el('h3',{},task.nameFr));
    panel.append(el('p',{},`${task.traderNameFr||'Trader non résolu'} · niveau ${task.minPlayerLevel??'—'} · ${task.mapNames.length?task.mapNames.join(', '):'lieu non renseigné'}`));
    const state=treeState(mode); const check=el('label',{class:'phase7-checkbox'});
    const input=el('input',{type:'checkbox',checked:state[task.id]==='done','aria-label':`Marquer ${task.nameFr} terminée localement`,dataset:{treeState:task.id}});
    input.addEventListener('change',()=>{const updated=treeState(mode);if(input.checked)updated[task.id]='done';else delete updated[task.id];saveStored(treeKey(mode),updated);renderTreeTask();});
    check.append(input,el('span',{},'Terminée sur mon suivi local'));
    panel.append(check);
    if(task.wikiLink)panel.append(el('a',{href:task.wikiLink,rel:'noopener noreferrer'},'Ouvrir la page communautaire liée à cette tâche ↗'));
    if(task.taskRequirements.length){
      const h=el('p',{},`Prérequis déclarés (${task.taskRequirements.length})`); panel.append(h);
      if(task.taskRequirements.length>1)panel.append(el('p',{class:'phase7-note'},'Plusieurs liens sont listés; l’opérateur ET/OU n’est pas déduit par cet outil. Vérifiez la tâche dans le client.'));
      const ul=el('ul');
      task.taskRequirements.forEach((req)=>{
        const li=el('li');
        const label=req.nameFr||`ID absent de l’export : ${req.taskId}`;
        const row=el('label',{class:'phase7-checkbox'});
        const done=treeState(mode)[req.taskId]==='done';
        const box=el('input',{type:'checkbox',checked:done,'aria-label':`Marquer ${label} terminée localement`,dataset:{treeState:req.taskId}});
        box.addEventListener('change',()=>{const updated=treeState(mode);if(box.checked)updated[req.taskId]='done';else delete updated[req.taskId];saveStored(treeKey(mode),updated);renderTreeTask();});
        row.append(box,el('span',{},label));
        li.append(row);
        if(req.status?.length)li.append(el('small',{},`Statut attendu par l’export : ${req.status.join(', ')}`));
        if(req.notes)li.append(el('small',{},`Note amont : ${req.notes}`));
        ul.append(li);
      });
      panel.append(ul);
      const allDone=task.taskRequirements.every((req)=>treeState(mode)[req.taskId]==='done');
      panel.append(el('p',{},allDone?'Tous les prérequis listés sont cochés localement; disponibilité non garantie.':'La checklist indique les liens encore non cochés, sans calculer la disponibilité en jeu.'));
    }else panel.append(el('p',{},'Aucun lien taskRequirements déclaré pour cette tâche. D’autres conditions ou paliers de loyauté peuvent s’appliquer.'));
    if(task.traderRequirements.length){
      const ul=el('ul');task.traderRequirements.forEach((req)=>ul.append(el('li',{},`${req.traderNameFr||'Trader'} · ${req.type||'condition'} ${req.compare||''} ${req.value??''}`)));panel.append(el('p',{},'Autres conditions de trader exportées:'),ul);
    }
    treePanel.append(panel);
  };
  [treeMode,treeTrader,treeSearch].filter(Boolean).forEach((node)=>{node.addEventListener('input',populateTreeTasks);node.addEventListener('change',populateTreeTasks);});
  treeTaskSelect?.addEventListener('change',renderTreeTask);
  document.querySelector('[data-p7-tree-export]')?.addEventListener('click',()=>{
    const mode=treeMode?.value||'regular'; const payload={schemaVersion:1,mode,snapshotDateReference:data.snapshotDateReference,completedTaskIds:Object.keys(treeState(mode)).filter((id)=>treeState(mode)[id]==='done')};
    const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=el('a',{href:url,download:`tarkov-quetes-${mode}.json`});document.body.append(a);a.click();a.remove();URL.revokeObjectURL(url);
  });
  document.querySelector('[data-p7-tree-clear]')?.addEventListener('click',()=>{const mode=treeMode?.value||'regular';saveStored(treeKey(mode),{});renderTreeTask();});
  if(treeTaskSelect){
    const requested=params.get('task'); const requestedMode=params.get('mode');
    if(requestedMode&&data.modes[requestedMode]&&treeMode)treeMode.value=requestedMode;
    populateTreeTasks();
    if(requested&&[...treeTaskSelect.options].some((o)=>o.value===requested)){treeTaskSelect.value=requested;renderTreeTask();}
  }

  // ── Kappa: exigences divergentes, checklist locale par mode ─────────────
  const kappaMode=document.querySelector('[data-p7-mode]');
  const kappaSummary=document.querySelector('[data-p7-kappa-summary]');
  const kappaReqs=document.querySelector('[data-p7-kappa-reqs]');
  const kappaItems=document.querySelector('[data-p7-kappa-items]');
  const kappaSearch=document.querySelector('[data-p7-kappa-search]');
  const kappaProgress=document.querySelector('[data-p7-kappa-progress]');
  const kappaKey=(mode)=>`tug-p7-kappa-items:${mode}`;
  const kappaState=(mode)=>safeStored(kappaKey(mode),{});
  const renderKappa=()=>{
    if(!kappaSummary||!kappaReqs||!kappaItems)return;
    const mode=kappaMode?.value||'regular';const collector=data.collectorByMode[mode];
    kappaSummary.replaceChildren();kappaReqs.replaceChildren();kappaItems.replaceChildren();
    if(!collector){kappaSummary.append(el('p',{},`Collector n’est pas présent dans le snapshot ${modeLabels[mode]}.`));return;}
    const llReqs=collector.traderRequirements.filter((r)=>r.type==='level'&&Number(r.value)===4);
    const fenceReq=collector.traderRequirements.find((r)=>r.type==='reputation'&&r.traderId==='579dc571d53a0658a154fbec');
    const stats=el('div',{class:'phase7-stat-grid'});
    [[collector.minPlayerLevel,'Niveau minimum du flux'],[collector.taskRequirements.length,'Tâches préalables listées'],[llReqs.length,'Traders LL4 listés'],[collector.objectives.length,'Objets à remettre']].forEach(([v,label])=>{const c=el('div',{class:'phase7-stat'});c.append(el('strong',{},String(v??'—')),el('span',{},label));stats.append(c);});
    const p=el('p',{},`Snapshot communautaire · ${modeLabels[mode]} · Fence réputation ${fenceReq?`${fenceReq.compare||'≥'} ${fenceReq.value}`:'non listée'} · ${collector.objectives.filter((o)=>o.foundInRaid).length} objectifs FIR marqués.`);
    kappaSummary.append(stats,p);
    const reqRows=[];
    collector.taskRequirements.forEach((req)=>reqRows.push({title:req.nameFr||req.taskId,detail:`Tâche préalable · statut ${req.status.join(', ')||'non renseigné'}${req.notes?` · note amont: ${req.notes}`:''}`}));
    llReqs.forEach((req)=>reqRows.push({title:req.traderNameFr||'Trader',detail:`Loyauté ${req.compare||'≥'} ${req.value}`}));
    if(fenceReq)reqRows.push({title:'Fence · réputation',detail:`Scav karma ${fenceReq.compare||'≥'} ${fenceReq.value}`});
    reqRows.forEach((row)=>{const card=el('div',{class:'phase7-req-card'});card.append(el('strong',{},row.title),el('span',{},row.detail));kappaReqs.append(card);});
    const state=kappaState(mode);const q=(kappaSearch?.value||'').trim().toLocaleLowerCase('fr');let done=0;let visible=0;
    collector.objectives.forEach((objective,index)=>{
      const itemId=objective.itemIds?.[0]||objective.id;const name=objective.itemNamesFr?.[0]||objective.descriptionFr||`Objet ${index+1}`;
      const checked=Boolean(state[itemId]);if(checked)done++;
      const label=el('label',{class:'phase7-checkbox',dataset:{kappaItem:name.toLocaleLowerCase('fr')}});
      const input=el('input',{type:'checkbox',checked,'aria-label':`Cocher ${name} dans ma checklist locale`,dataset:{kappaItemId:itemId}});
      input.addEventListener('change',()=>{const updated=kappaState(mode);if(input.checked)updated[itemId]=true;else delete updated[itemId];saveStored(kappaKey(mode),updated);renderKappa();});
      const copy=el('span');copy.append(el('strong',{},name),el('small',{},`${objective.count??1} × · ${objective.foundInRaid?'FIR requis selon l’export':'FIR non marqué'} · ID ${itemId}`));
      label.append(input,copy);
      const show=!q||`${name} ${objective.descriptionFr||''} ${itemId}`.toLocaleLowerCase('fr').includes(q);
      label.hidden=!show;if(show){kappaItems.append(label);visible++;}
    });
    announce(kappaProgress,`${done} / ${collector.objectives.length} objectifs cochés localement · ${visible} affichés · ${modeLabels[mode]}.`);
  };
  [kappaMode,kappaSearch].filter(Boolean).forEach((node)=>{node.addEventListener('input',renderKappa);node.addEventListener('change',renderKappa);});
  document.querySelector('[data-p7-kappa-clear]')?.addEventListener('click',()=>{const mode=kappaMode?.value||'regular';saveStored(kappaKey(mode),{});renderKappa();});
  renderKappa();

  // ── Hideout: stations, dépendances et checklist FIR par mode ────────────
  const hideMode=document.querySelector('[data-p7-mode]');
  const hideSearch=document.querySelector('[data-p7-hideout-search]');
  const hideFir=document.querySelector('[data-p7-hideout-fir]');
  const hideLevel=document.querySelector('[data-p7-hideout-level]');
  const hideStations=document.querySelector('[data-p7-hideout-stations]');
  const hideCount=document.querySelector('[data-p7-hideout-count]');
  const hideKey=(mode)=>`tug-p7-hideout:${mode}`;
  const hideState=(mode)=>safeStored(hideKey(mode),{});
  const clearHideout=document.querySelector('[data-p7-hideout-clear]');
  const renderHideout=()=>{
    if(!hideStations)return;
    const mode=hideMode?.value||'regular';const q=(hideSearch?.value||'').trim().toLocaleLowerCase('fr');
    const fir=hideFir?.value||'all';const lvl=hideLevel?.value||'all';const stations=data.modes[mode]?.stations||[];const state=hideState(mode);
    hideStations.replaceChildren();let visible=0;let matchedLevels=0;
    stations.forEach((station)=>{
      const stationDetail=el('details',{class:'phase7-station',dataset:{stationId:station.id}});
      const summary=el('summary');summary.append(el('span',{},station.nameFr));summary.append(el('span',{class:'phase7-station__meta'},`${station.levels.length} palier(s) · ${station.itemRequirementRows} ligne(s)`));stationDetail.append(summary);
      const levels=el('div',{class:'phase7-station__levels'});
      let stationHasMatch=false;
      station.levels.forEach((level)=>{
        const levelNum=Number(level.level)||0;
        if(lvl!=='all'&&((lvl==='4'&&levelNum<4)||(lvl!=='4'&&levelNum!==Number(lvl))))return;
        const stationNeedles=`${station.nameFr} ${station.nameEn}`.toLocaleLowerCase('fr');
        const matchesStation=Boolean(q&&stationNeedles.includes(q));
        const visibleItems=level.itemRequirements.filter((item)=>{
          if(fir==='fir'&&!item.foundInRaid)return false;
          if(fir==='not-fir'&&item.foundInRaid)return false;
          if(q&&matchesStation)return true;
          const hay=`${item.nameFr} ${item.nameEn} ${levelNum}`.toLocaleLowerCase('fr');
          return !q||hay.includes(q);
        });
        if(q&&!matchesStation&&!visibleItems.length)return;
        if(!q&&fir!=='all'&&!visibleItems.length)return;
        stationHasMatch=true;matchedLevels++;
        const d=el('details',{class:'phase7-level'});const sum=el('summary');sum.append(el('span',{},`Niveau ${levelNum}`),el('span',{},fmtDuration(level.constructionTime)));d.append(sum);
        const inner=el('div',{class:'phase7-level__body'});
        const reqs=el('div',{class:'phase7-requirement-list'});
        if(visibleItems.length){
          const heading=el('strong',{},`Matériaux affichés (${visibleItems.length} sur ${level.itemRequirements.length})`);reqs.append(heading);
          visibleItems.forEach((item,index)=>{
            const inputId=`${mode}:${level.id||station.id+'-'+levelNum}:${item.itemId}:${index}`;
            const label=el('label',{class:'phase7-checkbox'});
            const checkbox=el('input',{type:'checkbox',checked:Boolean(state[inputId]),'aria-label':`Matériau ${item.nameFr} pour ${station.nameFr} niveau ${levelNum}`,dataset:{hideoutCheck:inputId}});
            checkbox.addEventListener('change',()=>{const updated=hideState(mode);if(checkbox.checked)updated[inputId]=true;else delete updated[inputId];saveStored(hideKey(mode),updated);});
            const copy=el('span');copy.append(el('strong',{},`${fmtNum(item.count)} × ${item.nameFr}`));
            const tags=[];if(item.foundInRaid)tags.push('FIR · export');if(item.tool)tags.push('outil');if(tags.length)copy.append(el('small',{},tags.join(' · ')));
            label.append(checkbox,copy);reqs.append(label);
          });
        } else if(level.itemRequirements.length) reqs.append(el('small',{},'Aucun matériau ne correspond au filtre actif; les dépendances non matérielles restent affichées ci-dessous.'));
        else reqs.append(el('small',{},'Aucun besoin d’objet listé pour ce palier.'));
        inner.append(reqs);
        if(level.stationRequirements.length){const ul=el('ul');level.stationRequirements.forEach((r)=>ul.append(el('li',{},`${r.nameFr} niveau ${r.level}`)));inner.append(el('p',{},'Dépendances de station :'),ul);}
        if(level.traderRequirements.length){const ul=el('ul');level.traderRequirements.forEach((r)=>ul.append(el('li',{},`${r.nameFr} ${r.level?`niveau ${r.level}`:''}${r.reputation?` · réputation ${r.reputation}`:''}`)));inner.append(el('p',{},'Dépendances trader :'),ul);}
        if(level.skillRequirements.length){const ul=el('ul');level.skillRequirements.forEach((r)=>ul.append(el('li',{},`${r.skill||'Compétence'} niveau ${r.level}`)));inner.append(el('p',{},'Compétences exportées :'),ul);}
        d.append(inner);levels.append(d);
      });
      if(stationHasMatch){visible++;stationDetail.append(levels);hideStations.append(stationDetail);}
    });
    announce(hideCount,`${visible} station(s), ${matchedLevels} palier(s) affichés · ${modeLabels[mode]}. État de checklist local uniquement.`);
  };
  [hideMode,hideSearch,hideFir,hideLevel].filter(Boolean).forEach((node)=>{node.addEventListener('input',renderHideout);node.addEventListener('change',renderHideout);});
  clearHideout?.addEventListener('click',()=>{const mode=hideMode?.value||'regular';saveStored(hideKey(mode),{});renderHideout();});
  const stationParam=params.get('station');
  renderHideout();
  if(stationParam&&hideStations){const match=hideStations.querySelector(`[data-station-id="${CSS.escape(stationParam)}"]`);match?.setAttribute('open','');}

  // ── Crafts: prix saisis manuellement, outils hors coût consommé ─────────
  const craftMode=document.querySelector('[data-p7-mode]');
  const craftStation=document.querySelector('[data-p7-craft-station]');
  const craftSearch=document.querySelector('[data-p7-craft-search]');
  const craftSort=document.querySelector('[data-p7-craft-sort]');
  const craftRecipe=document.querySelector('[data-p7-craft-recipe]');
  const craftDetail=document.querySelector('[data-p7-craft-detail]');
  const craftCount=document.querySelector('[data-p7-craft-count]');
  let currentCrafts=[];
  let filteredCrafts=[];
  const craftStorageKey=(mode,recipeId)=>`tug-p7-craft-prices:${mode}:${recipeId}`;
  const populateCraftStations=(mode)=>{
    if(!craftStation)return;
    const old=craftStation.value;const stations=data.modes[mode].stations||[];
    craftStation.replaceChildren();addOption(craftStation,'all','Toutes les stations');
    stations.slice().sort((a,b)=>a.nameFr.localeCompare(b.nameFr,'fr')).forEach((s)=>addOption(craftStation,s.id,s.nameFr));
    if([...craftStation.options].some((o)=>o.value===old))craftStation.value=old;
  };
  const renderCraftOptions=()=>{
    if(!craftRecipe)return;
    const mode=craftMode?.value||'regular';currentCrafts=data.modes[mode]?.crafts||[];populateCraftStations(mode);
    const station=craftStation?.value||'all';const q=(craftSearch?.value||'').trim().toLocaleLowerCase('fr');const sort=craftSort?.value||'station';
    filteredCrafts=currentCrafts.filter((r)=>(station==='all'||r.stationId===station)&&(!q||`${r.output.nameFr} ${r.output.nameEn} ${r.stationNameFr} ${r.ingredients.map((i)=>i.nameFr).join(' ')}`.toLocaleLowerCase('fr').includes(q)));
    if(sort==='duration')filteredCrafts.sort((a,b)=>(a.duration||0)-(b.duration||0));
    if(sort==='level')filteredCrafts.sort((a,b)=>(a.level||0)-(b.level||0)||(a.duration||0)-(b.duration||0));
    if(sort==='name')filteredCrafts.sort((a,b)=>a.output.nameFr.localeCompare(b.output.nameFr,'fr'));
    if(sort==='station')filteredCrafts.sort((a,b)=>a.stationNameFr.localeCompare(b.stationNameFr,'fr')||(a.duration||0)-(b.duration||0));
    const old=craftRecipe.value;craftRecipe.replaceChildren();addOption(craftRecipe,'','Choisissez une recette');
    filteredCrafts.forEach((r)=>addOption(craftRecipe,r.id,`${r.output.nameFr} ×${r.output.count??1} · ${r.stationNameFr} niv. ${r.level??'—'} · ${fmtDuration(r.duration)}`));
    const requested=params.get('recipe');
    if(requested&&filteredCrafts.some((r)=>r.id===requested))craftRecipe.value=requested;
    else if(filteredCrafts.some((r)=>r.id===old))craftRecipe.value=old;
    announce(craftCount,`${filteredCrafts.length} recette(s) filtrée(s) sur ${currentCrafts.length} · ${modeLabels[mode]}.`);
    renderCraftDetail();
  };
  const renderCraftDetail=()=>{
    if(!craftDetail)return;
    const mode=craftMode?.value||'regular';const recipe=filteredCrafts.find((r)=>r.id===craftRecipe?.value);
    craftDetail.replaceChildren();
    if(!recipe){craftDetail.append(el('p',{},'Sélectionnez une recette pour saisir vos prix et estimer le coût du lot.'));return;}
    const stored=safeStored(craftStorageKey(mode,recipe.id),{});
    const header=el('div',{class:'phase7-craft-detail__head'});const title=el('div');title.append(el('h3',{},recipe.output.nameFr));title.append(el('p',{},`${recipe.stationNameFr} niveau ${recipe.level??'—'} · lot de sortie ×${recipe.output.count??1} · ${fmtDuration(recipe.duration)}`));header.append(title,el('span',{class:'phase7-tag'},modeLabels[mode]));craftDetail.append(header);
    if(recipe.taskUnlock){const task=(data.modes[mode].tasks||[]).find((t)=>t.id===recipe.taskUnlock);const link=el('a',{href:task?taskLink(task,mode):`${root}pages/quests/?mode=${mode}&task=${recipe.taskUnlock}`},task?`Déverrouillage de tâche : ${task.nameFr}`:`Déverrouillage par tâche · ID ${recipe.taskUnlock}`);craftDetail.append(link);}
    const ingredients=el('div',{class:'phase7-craft-ingredients'});let requiredPriceFields=[];
    recipe.ingredients.forEach((ingredient,index)=>{
      const row=el('div',{class:'phase7-craft-row'});const label=el('label');
      const name=el('span',{},`${fmtNum(ingredient.count)} × ${ingredient.nameFr}`);label.append(name);
      if(ingredient.tool){label.append(el('small',{},'Outil requis · non facturé comme consommable dans le calcul par défaut.'));row.append(label,el('span',{class:'phase7-fir'},'OUTIL'));}
      else {
        label.append(el('small',{},'Prix unitaire du consommable, en roubles (saisie manuelle).'));
        const input=el('input',{type:'number',min:'0',step:'1',inputmode:'decimal','aria-label':`Prix unitaire ${ingredient.nameFr}`,dataset:{craftPrice:ingredient.itemId||`unknown-${index}`}});
        if(stored.prices?.[ingredient.itemId]!=null)input.value=stored.prices[ingredient.itemId];
        row.append(label,input);requiredPriceFields.push({input,ingredient});
      }
      ingredients.append(row);
    });
    craftDetail.append(ingredients);
    const out=el('div',{class:'phase7-craft-output'});const outLabel=el('label');outLabel.append(el('strong',{},`${fmtNum(recipe.output.count)} × ${recipe.output.nameFr}`),el('small',{},'Prix de vente unitaire estimé, saisi par vous (₽).'));
    const outputPrice=el('input',{type:'number',min:'0',step:'1',inputmode:'decimal','aria-label':`Prix de vente unitaire de ${recipe.output.nameFr}`,dataset:{craftOutputPrice:'true'}});if(stored.outputPrice!=null)outputPrice.value=stored.outputPrice;
    out.append(outLabel,outputPrice);craftDetail.append(out);
    const fees=el('div',{class:'phase7-craft-row'});const feeLabel=el('label');feeLabel.append(el('span',{},'Frais de vente estimés'),el('small',{},'Taux manuel; laisser à zéro si inconnu.'));const feeInput=el('input',{type:'number',min:'0',max:'100',step:'0.1',inputmode:'decimal','aria-label':'Pourcentage de frais estimés',dataset:{craftFee:'true'}});if(stored.feePercent!=null)feeInput.value=stored.feePercent;else feeInput.value='0';fees.append(feeLabel,feeInput);craftDetail.append(fees);
    const results=el('div',{class:'phase7-craft-result','aria-live':'polite'});const resultNodes={};[['cost','Coût consommables'],['gross','Valeur sortie brute'],['fee','Frais estimés'],['net','Marge estimée avant autres coûts'],['unit','Coût par objet sorti']].forEach(([key,label])=>{const card=el('div');card.append(el('strong',{},'—'),el('span',{},label));results.append(card);resultNodes[key]=card.querySelector('strong');});craftDetail.append(results);
    const note=el('p',{class:'phase7-note'},'Les prix restent sur cet appareil. Le calcul exclut énergie, carburant, coûts d’opportunité, taxes non saisies, usure, délai réel et risque de vente.');craftDetail.append(note);
    const clear=el('button',{type:'button',class:'button button--quiet'},'Effacer les prix de cette recette');clear.addEventListener('click',()=>{removeStored(craftStorageKey(mode,recipe.id));renderCraftDetail();});craftDetail.append(clear);
    const compute=()=>{
      const prices={};let complete=true;let cost=0;
      requiredPriceFields.forEach(({input,ingredient})=>{const value=input.value===''?null:Number(input.value);if(value==null||!Number.isFinite(value)){complete=false;return;}prices[ingredient.itemId]=value;cost+=value*Number(ingredient.count||0);});
      const price=outputPrice.value===''?null:Number(outputPrice.value);const feePercent=feeInput.value===''?0:Number(feeInput.value);
      const outputCount=Number(recipe.output.count||0);const gross=price==null?null:price*outputCount;const fee=gross==null?null:gross*feePercent/100;
      const write=(key,value,needsComplete=true)=>{resultNodes[key].textContent=value==null||(needsComplete&&!complete)?'—':`${fmtNum(value)} ₽`;};
      write('cost',complete?cost:null,true);write('gross',gross,false);write('fee',fee,false);write('net',gross==null||!complete?null:gross-fee-cost,false);write('unit',complete&&outputCount?cost/outputCount:null,true);
      saveStored(craftStorageKey(mode,recipe.id),{prices,outputPrice:outputPrice.value,feePercent:feeInput.value});
    };
    [...requiredPriceFields.map((r)=>r.input),outputPrice,feeInput].forEach((input)=>input.addEventListener('input',compute));
    compute();
  };
  [craftMode,craftStation,craftSearch,craftSort].filter(Boolean).forEach((node)=>{node.addEventListener('input',renderCraftOptions);node.addEventListener('change',renderCraftOptions);});
  craftRecipe?.addEventListener('change',renderCraftDetail);
  renderCraftOptions();
}
