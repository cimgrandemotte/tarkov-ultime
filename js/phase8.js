/* PHASE_8 — filtres, calculateurs explicites et outils locaux optionnels. */
const body = document.body;
if (body?.matches('[data-phase8-page]')) {
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const modes = { regular: 'PvP permanent', pve: 'PvE Zone', 'pvp-season': 'PvP Seasonal' };
  const number = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 });
  const modeName = (id) => modes[id] || id || 'mode non précisé';
  const fmt = (value) => number.format(Number.isFinite(value) ? value : 0);
  const cleanText = (value) => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();

  function storageRead(key, fallback) {
    try {
      const value = JSON.parse(localStorage.getItem(key) || 'null');
      return value ?? fallback;
    } catch { return fallback; }
  }
  function storageWrite(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); return true; }
    catch { return false; }
  }
  function storageRemove(key) {
    try { localStorage.removeItem(key); } catch { /* Le stockage local est facultatif. */ }
  }
  function announce(node, text) { if (node) node.textContent = text; }
  function result(node, heading, paragraphs = []) {
    if (!node) return;
    node.replaceChildren();
    const strong = document.createElement('strong');
    strong.textContent = heading;
    node.append(strong);
    for (const text of paragraphs) {
      const p = document.createElement('p');
      p.textContent = text;
      node.append(p);
    }
  }
  function fail(form, output, message, field) {
    $$('input, select, textarea', form).forEach((control) => control.removeAttribute('aria-invalid'));
    if (field) {
      field.setAttribute('aria-invalid', 'true');
      field.focus();
    }
    if (output?.tagName === 'P') announce(output, `Vérifie les données saisies : ${message}`);
    else result(output, 'Vérifie les données saisies.', [message]);
  }
  function readNumber(form, key, { required = true, min = 0, max = Infinity } = {}) {
    const field = $(`[data-p8-input="${key}"]`, form);
    if (!field) return { ok: false, field: null, value: null, message: 'Champ manquant dans le formulaire.' };
    field.removeAttribute('aria-invalid');
    const raw = field.value.trim();
    if (!raw && !required) return { ok: true, field, value: null };
    const value = raw === '' ? NaN : Number(raw);
    if (!Number.isFinite(value)) return { ok: false, field, value: null, message: 'Saisis une valeur numérique pour poursuivre.' };
    if (value < min || value > max) return { ok: false, field, value: null, message: `La valeur doit être comprise entre ${fmt(min)} et ${max === Infinity ? 'sans plafond' : fmt(max)}.` };
    return { ok: true, field, value };
  }
  function localName(date = new Date()) {
    return new Intl.DateTimeFormat('fr-FR', { dateStyle: 'medium' }).format(date);
  }

  // Filtres de sujets de compétences : les notes sans script restent intégralement visibles.
  const skillFilter = $('[data-p8-skill-filter]');
  const skillCards = $$('[data-p8-skill-topic]');
  const skillCount = $('[data-p8-skill-topic-count]');
  function filterSkillTopics() {
    if (!skillFilter || !skillCards.length) return;
    const value = skillFilter.value;
    const visible = skillCards.filter((card) => value === 'all' || card.dataset.p8SkillTopic === value);
    skillCards.forEach((card) => { card.hidden = !visible.includes(card); });
    announce(skillCount, `${visible.length} sujet${visible.length === 1 ? '' : 's'} affiché${visible.length === 1 ? '' : 's'}.`);
  }
  skillFilter?.addEventListener('change', filterSkillTopics);
  filterSkillTopics();

  // Journal personnel sans coefficients calculés; les entrées restent sur cet appareil.
  const logForm = $('[data-p8-skill-log-form]');
  if (logForm) {
    const key = 'tug:p8:skill-log:v1';
    const list = $('[data-p8-log-list]');
    const status = $('[data-p8-log-status]');
    const skillField = $('[data-p8-log-skill]', logForm);
    const modeField = $('[data-p8-log-mode]', logForm);
    const noteField = $('[data-p8-log-note]', logForm);
    let entries = storageRead(key, []);
    if (!Array.isArray(entries)) entries = [];
    function renderLog(message = '') {
      if (!list) return;
      list.replaceChildren();
      entries.forEach((entry) => {
        const li = document.createElement('li');
        const title = document.createElement('strong');
        title.textContent = `${entry.skill} · ${modeName(entry.mode)}`;
        const detail = document.createElement('p');
        detail.textContent = [entry.date, entry.note].filter(Boolean).join(' · ') || 'Aucune note de contexte.';
        const remove = document.createElement('button');
        remove.type = 'button';
        remove.className = 'button button--quiet button--xs';
        remove.dataset.p8LogRemove = entry.id;
        remove.textContent = 'Supprimer cette note';
        remove.setAttribute('aria-label', `Supprimer la note ${entry.skill}`);
        li.append(title, detail, remove);
        list.append(li);
      });
      announce(status, message || (entries.length ? `${entries.length} note${entries.length === 1 ? '' : 's'} enregistrée${entries.length === 1 ? '' : 's'} sur cet appareil.` : 'Journal local vide.'));
    }
    logForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const skill = skillField?.value.trim() || '';
      if (!skill) { fail(logForm, status, 'Indique le nom affiché dans le client.', skillField); return; }
      const entry = {
        id: (globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2)}`),
        skill: skill.slice(0, 100), mode: modeField?.value || 'regular',
        note: (noteField?.value || '').trim().slice(0, 500), date: localName(),
      };
      entries = [entry, ...entries].slice(0, 50);
      const saved = storageWrite(key, entries);
      renderLog(saved ? 'Note ajoutée au journal de cet appareil.' : 'Note ajoutée jusqu’à la fermeture de la page; le stockage local est indisponible.');
      skillField.value = '';
      if (noteField) noteField.value = '';
      skillField.focus();
    });
    list?.addEventListener('click', (event) => {
      const button = event.target.closest('[data-p8-log-remove]');
      if (!button) return;
      entries = entries.filter((entry) => entry.id !== button.dataset.p8LogRemove);
      storageWrite(key, entries);
      renderLog('Note supprimée.');
    });
    $('[data-p8-log-clear]')?.addEventListener('click', () => {
      entries = [];
      storageRemove(key);
      renderLog('Journal local effacé.');
    });
    renderLog();
  }

  // Calculateurs : toutes les valeurs proviennent des champs utilisateur.
  $$('[data-p8-calc]').forEach((form) => {
    const type = form.dataset.p8Calc;
    const output = $(`[data-p8-result="${type}"]`, form);
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const get = (key, opts) => readNumber(form, key, opts);
      if (type === 'economy') {
        const gross = get('gross'); const fee = get('fee', { min: 0, max: 100 }); const cost = get('cost'); const minutes = get('minutes', { required: false, min: 0.1 });
        const invalid = [gross, fee, cost, minutes].find((item) => !item.ok);
        if (invalid) return fail(form, output, invalid.message, invalid.field);
        const net = gross.value * (1 - fee.value / 100) - cost.value;
        const detail = [`Estimation simplifiée : ${fmt(gross.value)} × (1 − ${fmt(fee.value)} %) − ${fmt(cost.value)} = ${fmt(net)} ₽.`,
          minutes.value == null ? 'Durée non saisie : aucun résultat par heure.' : `À ${fmt(minutes.value)} min par tentative : ${fmt(net * 60 / minutes.value)} ₽/h, simple extrapolation des valeurs saisies.`,
          'Le taux effectif est ta propre hypothèse; ce résultat ne reproduit pas la commission du jeu.'];
        return result(output, `${net < 0 ? 'Solde négatif estimé' : 'Solde estimé'} : ${fmt(net)} ₽`, detail);
      }
      if (type === 'flea') {
        const ask = get('ask'); const rate = get('rate', { min: 0, max: 100 }); const trader = get('trader'); const basis = get('basis', { required: false });
        const invalid = [ask, rate, trader, basis].find((item) => !item.ok);
        if (invalid) return fail(form, output, invalid.message, invalid.field);
        const acquisition = basis.value ?? 0;
        const fleaNet = ask.value * (1 - rate.value / 100) - acquisition;
        const traderNet = trader.value - acquisition;
        const winner = fleaNet === traderNet ? 'Résultats égaux selon les valeurs saisies.' : fleaNet > traderNet ? 'Le Flea donne le net estimé le plus élevé selon tes hypothèses.' : 'L’offre trader donne le net estimé le plus élevé selon tes hypothèses.';
        return result(output, winner, [`Flea simplifié : ${fmt(ask.value)} − ${fmt(ask.value * rate.value / 100)} de frais supposés − ${fmt(acquisition)} de coût = ${fmt(fleaNet)} ₽.`,
          `Trader : ${fmt(trader.value)} − ${fmt(acquisition)} de coût = ${fmt(traderNet)} ₽.`,
          basis.value == null ? 'Coût d’acquisition non saisi : traité comme 0 ₽ pour les deux options.' : 'Le même coût d’acquisition est déduit des deux options.',
          'Le taux effectif est saisi par toi; vérifie le frais réel dans le client.']);
      }
      if (type === 'money') {
        const haul = get('haul'); const survival = get('survival', { min: 0, max: 100 }); const recovery = get('recovery');
        const kit = get('kit'); const fixed = get('fixed'); const time = get('time', { min: 0.1 });
        const invalid = [haul, survival, recovery, kit, fixed, time].find((item) => !item.ok);
        if (invalid) return fail(form, output, invalid.message, invalid.field);
        const p = survival.value / 100;
        const expected = p * haul.value + (1 - p) * recovery.value - kit.value - fixed.value;
        return result(output, `${expected < 0 ? 'Solde attendu négatif selon tes hypothèses' : 'Solde attendu selon tes hypothèses'} : ${fmt(expected)} ₽ par tentative`, [
          `Formule : (${fmt(survival.value)} % × ${fmt(haul.value)} ₽) + (${fmt(100 - survival.value)} % × ${fmt(recovery.value)} ₽) − ${fmt(kit.value)} ₽ − ${fmt(fixed.value)} ₽.`,
          `Extrapolation par durée saisie (${fmt(time.value)} min) : ${fmt(expected * 60 / time.value)} ₽/h.`,
          'Probabilité, valeur en cas de retour/échec, durée et coûts sont tes entrées; le site ne fournit aucun taux de survie ni rendement attendu.',
        ]);
      }
      if (type === 'build') {
        const costs = $$('[data-p8-build-cost]', form).map((field) => {
          const raw = field.value.trim();
          if (!raw) return { ok: true, value: 0, omitted: true, field };
          const value = Number(raw);
          return { ok: Number.isFinite(value) && value >= 0, value, omitted: false, field };
        });
        const invalid = costs.find((item) => !item.ok);
        const budget = $('[data-p8-build-budget]', form);
        const budgetValue = budget?.value.trim() ? Number(budget.value) : null;
        if (invalid) return fail(form, output, 'Chaque coût doit être un nombre positif ou nul.', invalid.field);
        if (budgetValue != null && (!Number.isFinite(budgetValue) || budgetValue < 0)) return fail(form, output, 'Le budget doit être un nombre positif ou nul.', budget);
        const entered = costs.filter((item) => !item.omitted).length;
        if (!entered) return fail(form, output, 'Saisis au moins un coût affiché pour ce mode.', costs[0]?.field);
        const total = costs.reduce((sum, item) => sum + item.value, 0);
        const mode = modeName($('[data-p8-build-mode]', form)?.value);
        const budgetLine = budgetValue == null ? 'Aucun budget plafond saisi.' : total <= budgetValue ? `Sous le budget saisi de ${fmt(budgetValue)} ₽ (marge ${fmt(budgetValue - total)} ₽).` : `Au-dessus du budget saisi de ${fmt(budgetValue)} ₽ (dépassement ${fmt(total - budgetValue)} ₽).`;
        return result(output, `Total des lignes incluses : ${fmt(total)} ₽`, [`Profil choisi : ${mode}.`, budgetLine,
          'Les champs vides sont exclus du total; ils ne représentent ni des prix nuls ni des cotations. Le calcul ne vérifie pas la compatibilité, l’accès trader ou les stats en jeu.']);
      }
    });
    form.addEventListener('reset', () => {
      window.setTimeout(() => {
        $$('input, select, textarea', form).forEach((control) => control.removeAttribute('aria-invalid'));
        result(output, 'En attente de vos données.', ['Aucun prix, taux ou résultat n’est prérempli.']);
      }, 0);
    });
  });

  // Filtres de profils, avec tous les contenus présents en HTML sans JS.
  function installCardFilter(selectSelector, cardSelector, statusSelector, label) {
    const select = $(selectSelector); const cards = $$(cardSelector); const status = $(statusSelector);
    if (!select || !cards.length) return;
    const apply = () => {
      const value = select.value;
      const visible = cards.filter((card) => value === 'all' || card.dataset.p8ModeCard === value || card.dataset.p8PvpPanel === value);
      cards.forEach((card) => { card.hidden = !visible.includes(card); });
      announce(status, `${visible.length} ${label}${visible.length === 1 ? '' : 's'} affiché${visible.length === 1 ? '' : 's'}.`);
    };
    select.addEventListener('change', apply);
    apply();
  }
  installCardFilter('[data-p8-strategy-mode]', '[data-p8-mode-card]', '[data-p8-mode-count]', 'contexte');
  installCardFilter('[data-p8-pvp-mode]', '[data-p8-pvp-panel]', '[data-p8-pvp-count]', 'profil');

  // Checklist indicative de Prestige, locale à l’appareil et sans validation de prérequis.
  const prestigeTier = $('[data-p8-prestige-tier]');
  const prestigeChecks = $$('[data-p8-prestige-check]');
  const prestigeStatus = $('[data-p8-prestige-status]');
  if (prestigeTier && prestigeChecks.length) {
    const keyFor = (tier) => `tug:p8:prestige:${tier}:v1`;
    function paintPrestige(message = '') {
      const tier = prestigeTier.value;
      const saved = storageRead(keyFor(tier), []);
      const done = Array.isArray(saved) ? saved : [];
      prestigeChecks.forEach((input) => { input.checked = done.includes(input.value); });
      announce(prestigeStatus, message || `Checklist locale — Prestige PvE ${tier} · ${done.length}/${prestigeChecks.length} repères cochés. Ces cases ne vérifient pas le client.`);
    }
    prestigeChecks.forEach((input) => input.addEventListener('change', () => {
      const done = prestigeChecks.filter((item) => item.checked).map((item) => item.value);
      storageWrite(keyFor(prestigeTier.value), done);
      paintPrestige();
    }));
    prestigeTier.addEventListener('change', () => paintPrestige());
    $('[data-p8-prestige-reset]')?.addEventListener('click', () => {
      storageRemove(keyFor(prestigeTier.value));
      paintPrestige(`Suivi local du Prestige PvE ${prestigeTier.value} effacé.`);
    });
    paintPrestige();
  }

  // Astuces : filtres, favoris et état des boutons accessibles.
  const tipCards = $$('[data-p8-tip]');
  if (tipCards.length) {
    const key = 'tug:p8:tip-favorites:v1';
    const search = $('[data-p8-tip-search]');
    const category = $('[data-p8-tip-category]');
    const onlyFavorites = $('[data-p8-only-favorites]');
    const status = $('[data-p8-tip-count]');
    let favorites = storageRead(key, []);
    if (!Array.isArray(favorites)) favorites = [];
    const buttons = new Map($$('[data-p8-favorite]').map((button) => [button.dataset.p8Favorite, button]));
    function paintFavorite(button, active) {
      button.setAttribute('aria-pressed', String(active));
      const icon = button.firstChild;
      if (icon?.nodeType === Node.TEXT_NODE) icon.textContent = `${active ? '★' : '☆'} `;
      const label = $('span', button);
      if (label) label.textContent = 'Favori';
      const card = button.closest('[data-p8-tip]');
      const title = $('h3', card)?.textContent?.trim() || 'cette astuce';
      button.setAttribute('aria-label', `${active ? 'Retirer des' : 'Ajouter aux'} favoris : ${title} — Favori`);
    }
    function filterTips() {
      const query = cleanText(search?.value || '');
      const group = category?.value || 'all';
      let visible = 0;
      tipCards.forEach((card) => {
        const id = card.id;
        const favorite = favorites.includes(id);
        const matches = (!query || cleanText(card.dataset.p8Text || card.textContent).includes(query))
          && (group === 'all' || card.dataset.p8Category === group)
          && (!onlyFavorites?.checked || favorite);
        card.hidden = !matches;
        if (matches) visible += 1;
      });
      announce(status, `${visible} astuce${visible === 1 ? '' : 's'} affichée${visible === 1 ? '' : 's'}. ${favorites.length} favori${favorites.length === 1 ? '' : 's'} local${favorites.length === 1 ? '' : 'ux'}.`);
    }
    buttons.forEach((button, id) => {
      paintFavorite(button, favorites.includes(id));
      button.addEventListener('click', () => {
        favorites = favorites.includes(id) ? favorites.filter((entry) => entry !== id) : [...favorites, id];
        storageWrite(key, favorites);
        paintFavorite(button, favorites.includes(id));
        filterTips();
      });
    });
    [search, category, onlyFavorites].filter(Boolean).forEach((control) => control.addEventListener('input', filterTips));
    category?.addEventListener('change', filterTips);
    $('[data-p8-clear-favorites]')?.addEventListener('click', () => {
      favorites = [];
      storageRemove(key);
      if (onlyFavorites) onlyFavorites.checked = false;
      buttons.forEach((button) => paintFavorite(button, false));
      filterTips();
      announce(status, 'Favoris locaux effacés; la liste est actualisée.');
    });
    filterTips();
  }
}
