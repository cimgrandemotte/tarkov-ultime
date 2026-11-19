const normalize = (value = '') => String(value)
  .toLocaleLowerCase('fr-FR')
  .normalize('NFD')
  .replace(/[\u0300-\u036f]/g, '')
  .replace(/[^a-z0-9]+/g, ' ')
  .trim()

const numberValue = (value) => {
  if (value === '' || value == null) return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

const fmt = (value, digits = 2) => {
  if (value == null) return '—'
  return new Intl.NumberFormat('fr-FR', { maximumFractionDigits: digits }).format(value)
}

function applyArmorFilters(form) {
  const root = form.closest('[data-p6-filter-root]') || document
  const rows = [...root.querySelectorAll('[data-p6-item-row]')]
  const query = normalize(form.querySelector('[data-p6-search]')?.value)
  const group = form.querySelector('[data-p6-group]')?.value || ''
  const classValue = form.querySelector('[data-p6-class]')?.value || ''
  const mode = form.querySelector('[data-p6-mode]')?.value || 'regular'
  const budget = numberValue(form.querySelector('[data-p6-budget]')?.value)
  const weightMax = numberValue(form.querySelector('[data-p6-weight-max]')?.value)
  const zone = form.querySelector('[data-p6-zone]')?.value || ''
  const headset = form.querySelector('[data-p6-headset]')?.value || ''
  const kind = form.dataset.filterKind
  let visible = 0

  for (const row of rows) {
    const classHit = !classValue || row.dataset.classes.split('|').includes(classValue)
    const groupHit = !group || row.dataset.group === group
    const queryHit = !query || (row.dataset.search || '').includes(query)
    const weight = numberValue(row.dataset.weight)
    const weightHit = weightMax == null || (weight != null && weight <= weightMax)
    const zoneHit = !zone || (row.dataset.zones || '').includes(zone)
    const headsetHit = !headset || row.dataset.headset === headset
    // `data-price-pvp-season` is exposed as dataset.pricePvpSeason.
    const modeKey = mode === 'pvp-season' ? 'pricePvpSeason' : mode === 'pve' ? 'pricePve' : 'priceRegular'
    const selectedPrice = numberValue(row.dataset[modeKey])
    const budgetHit = budget == null || (selectedPrice != null && selectedPrice <= budget)
    const show = queryHit && groupHit && classHit && weightHit && zoneHit && headsetHit && budgetHit
    row.hidden = !show
    if (show) visible += 1
  }
  if (kind === 'rigs') {
    const sortBy = form.querySelector('[data-p6-sort]')?.value || 'name'
    const body = root.querySelector('#p6-rigs-table tbody')
    const sorted = [...rows].sort((left, right) => {
      if (sortBy === 'name') return (left.dataset.name || '').localeCompare(right.dataset.name || '', 'fr')
      const field = sortBy === 'weight' ? 'weight' : 'capacity'
      const a = numberValue(left.dataset[field])
      const b = numberValue(right.dataset[field])
      if (a == null && b == null) return (left.dataset.name || '').localeCompare(right.dataset.name || '', 'fr')
      if (a == null) return 1
      if (b == null) return -1
      return a - b || (left.dataset.name || '').localeCompare(right.dataset.name || '', 'fr')
    })
    sorted.forEach((row) => body?.append(row))
  }
  const count = form.parentElement.querySelector('[data-p6-count]')
  if (count) count.textContent = `${visible} / ${rows.length} entrées${budget != null ? ' · prix absent ou périmé exclus' : ''}`
}

function compareCatalogueRows(root) {
  const output = root.querySelector('[data-p6-compare-output]')
  if (!output) return
  const selected = [...root.querySelectorAll('[data-p6-compare-item]:checked')]
  if (!selected.length) {
    output.replaceChildren()
    return
  }
  const rows = selected.map((input) => input.closest('[data-p6-item-row]'))
  const groups = new Set(rows.map((row) => row?.dataset.group))
  if (groups.size !== 1) {
    output.textContent = 'Pour comparer, choisissez des objets du même groupe exporté (par exemple, deux plaques).'
    return
  }
  const table = document.createElement('table')
  table.className = 'phase6-table phase6-comparison-table'
  const caption = document.createElement('caption')
  caption.textContent = `Comparaison de ${rows.length} pièce${rows.length > 1 ? 's' : ''} sélectionnée${rows.length > 1 ? 's' : ''} · aucune classe globale calculée.`
  table.append(caption)
  const head = document.createElement('thead')
  const headRow = document.createElement('tr')
  const first = document.createElement('th')
  first.scope = 'col'
  first.textContent = 'Champ exporté'
  headRow.append(first)
  rows.forEach((row) => {
    const th = document.createElement('th')
    th.scope = 'col'
    th.textContent = row.querySelector('th')?.innerText.split('\n')[0] || row.dataset.id
    headRow.append(th)
  })
  head.append(headRow)
  table.append(head)
  const body = document.createElement('tbody')
  const labels = ['Classe par pièce', 'Slots / zones exportés', 'Matériau', 'Durabilité', 'Poids', 'Grille / capacité', 'Mouvement / rotation / ergo', 'Prix flea par mode']
  const cellIndexes = [1, 2, 3, 4, 5, 6, 7, 8]
  labels.forEach((label, i) => {
    const tr = document.createElement('tr')
    const th = document.createElement('th')
    th.scope = 'row'
    th.textContent = label
    tr.append(th)
    rows.forEach((row) => {
      const td = document.createElement('td')
      td.textContent = row.children[cellIndexes[i]]?.innerText.trim().replace(/\s+/g, ' ') || '—'
      tr.append(td)
    })
    body.append(tr)
  })
  table.append(body)
  output.replaceChildren(table)
}

function activateArmorFilters() {
  document.querySelectorAll('[data-p6-filter-form]').forEach((form) => {
    form.hidden = false
    form.addEventListener('input', () => applyArmorFilters(form))
    form.addEventListener('change', () => applyArmorFilters(form))
    form.addEventListener('reset', () => requestAnimationFrame(() => applyArmorFilters(form)))
    applyArmorFilters(form)
  })
  document.querySelectorAll('[data-p6-compare-item]').forEach((input) => {
    input.addEventListener('change', () => {
      const checked = [...document.querySelectorAll('[data-p6-compare-item]:checked')]
      if (checked.length > 3) {
        input.checked = false
        const output = document.querySelector('[data-p6-compare-output]')
        if (output) output.textContent = 'Le comparateur accepte au maximum trois pièces.'
        return
      }
      compareCatalogueRows(document)
    })
  })
  document.querySelectorAll('[data-p6-clear-compare]').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('[data-p6-compare-item]:checked').forEach((input) => { input.checked = false })
      compareCatalogueRows(document)
    })
  })
}

function setMode(tab, mode) {
  const section = tab.closest('.phase6-section') || document
  const tablist = tab.closest('[role="tablist"]')
  tablist?.querySelectorAll('[data-p6-mode-tab]').forEach((button) => {
    const active = button.dataset.p6ModeTab === mode
    button.setAttribute('aria-selected', String(active))
    button.tabIndex = active ? 0 : -1
  })
  const panelId = tab.getAttribute('aria-controls')
  const panel = panelId ? document.getElementById(panelId) : section.querySelector('[data-p6-mode-panel]')
  if (panel) {
    panel.hidden = false
    panel.dataset.p6ModePanel = mode
    panel.setAttribute('aria-labelledby', tab.id)
    const text = panel.querySelector('[data-p6-mode-text]')
    if (text && tab.dataset.note) text.textContent = tab.dataset.note
    if (!text && tab.dataset.note) {
      const p = document.createElement('p')
      p.dataset.p6ModeText = ''
      p.textContent = tab.dataset.note
      panel.replaceChildren(p)
    }
  }
  const fallback = section.querySelector('[data-p6-mode-fallback]')
  if (fallback) fallback.hidden = true
  section.querySelectorAll('[data-p6-boss-row]').forEach((row) => {
    const note = row.querySelector('[data-p6-boss-note]')
    if (note) note.textContent = row.dataset[`note${mode === 'pvp-season' ? 'PvpSeason' : mode === 'pve' ? 'Pve' : 'Regular'}`] || 'Aucune note spécifique vérifiée.'
  })
}

function activateModeTabs() {
  document.querySelectorAll('[data-p6-mode-tabs]').forEach((tablist) => {
    tablist.hidden = false
    const tabs = [...tablist.querySelectorAll('[data-p6-mode-tab]')]
    tabs.forEach((tab) => {
      tab.addEventListener('click', () => setMode(tab, tab.dataset.p6ModeTab))
      tab.addEventListener('keydown', (event) => {
        if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return
        event.preventDefault()
        const current = tabs.indexOf(tab)
        const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1
          : (current + (event.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length
        tabs[next].focus()
        setMode(tabs[next], tabs[next].dataset.p6ModeTab)
      })
    })
    const active = tabs.find((tab) => tab.getAttribute('aria-selected') === 'true') || tabs[0]
    if (active) setMode(active, active.dataset.p6ModeTab)
  })
}

function activateBossFilters() {
  const controls = document.querySelector('[data-p6-boss-controls]')
  if (!controls) return
  controls.hidden = false
  const search = controls.querySelector('[data-p6-boss-search]')
  const map = controls.querySelector('[data-p6-boss-map]')
  const rows = [...document.querySelectorAll('[data-p6-boss-row]')]
  const cards = [...document.querySelectorAll('[data-p6-boss-card]')]
  const count = document.querySelector('[data-p6-boss-count]')
  const update = () => {
    const query = normalize(search?.value)
    const mapValue = map?.value || ''
    let visible = 0
    rows.forEach((row) => {
      const show = (!query || (row.dataset.search || '').includes(query)) && (!mapValue || (row.dataset.maps || '').split('|').includes(mapValue))
      row.hidden = !show
      if (show) visible += 1
    })
    cards.forEach((card) => {
      card.hidden = (!query || (card.dataset.search || '').includes(query)) && (!mapValue || (card.dataset.maps || '').split('|').includes(mapValue)) ? false : true
    })
    document.querySelectorAll('.phase6-map-group').forEach((group) => {
      const listItems = [...group.querySelectorAll('[data-p6-boss-card]')]
      group.hidden = listItems.length > 0 && listItems.every((item) => item.hidden)
    })
    if (count) count.textContent = `${visible} / ${rows.length} profils correspondant aux filtres`
  }
  search?.addEventListener('input', update)
  map?.addEventListener('change', update)
  update()
}

function chartOptions(select, sourceOptions, group, emptyLabel) {
  const current = select.value
  select.replaceChildren()
  const blank = document.createElement('option')
  blank.value = ''
  blank.textContent = emptyLabel
  select.append(blank)
  const matches = sourceOptions.filter((option) => option.dataset.group === group)
  matches.forEach((option) => select.append(option.cloneNode(true)))
  if ([...select.options].some((option) => option.value === current)) select.value = current
  return matches.length
}

function chartCard(option, mode) {
  const card = document.createElement('article')
  card.className = 'phase6-chart-card'
  const heading = document.createElement('h3')
  heading.textContent = option.dataset.name
  card.append(heading)
  const linkUrl = option.dataset.link
  if (linkUrl && /^https:\/\//i.test(linkUrl)) {
    const link = document.createElement('a')
    link.href = linkUrl
    link.target = '_blank'
    link.rel = 'noopener noreferrer'
    link.textContent = 'Ouvrir la fiche communautaire ↗'
    card.append(link)
  }
  const list = document.createElement('dl')
  const modeLabel = mode === 'pvp-season' ? 'PvP Seasonal' : mode === 'pve' ? 'PvE Zone' : 'PvP permanent'
  const fields = [
    ['ID', option.value], ['Classe par slot', option.dataset.class], ['Zones', option.dataset.zones],
    ['Matériau', option.dataset.material], ['Durabilité', option.dataset.durability],
    ['Poids', option.dataset.weight ? `${fmt(Number(option.dataset.weight))} kg` : 'Non renseigné'],
    ['Grille / capacité', option.dataset.capacity ? `${fmt(Number(option.dataset.capacity), 0)} cases` : 'Voir le détail des grilles dans le catalogue'],
    ['Mouvement / rotation / ergo', option.dataset.penalties],
    [`Prix flea · ${modeLabel}`, option.dataset[`priceLabel${mode === 'pvp-season' ? 'PvpSeason' : mode === 'pve' ? 'Pve' : 'Regular'}`] || 'Aucun prix exploitable dans l’export'],
  ]
  fields.forEach(([label, value]) => {
    const dt = document.createElement('dt')
    dt.textContent = label
    const dd = document.createElement('dd')
    dd.textContent = value || '—'
    list.append(dt, dd)
  })
  card.append(list)
  return card
}

function activateArmorChart() {
  const form = document.querySelector('[data-p6-chart-form]')
  const source = document.querySelector('[data-p6-option-source]')
  const output = document.querySelector('[data-p6-chart-output]')
  if (!form || !source || !output) return
  form.hidden = false
  const group = form.querySelector('[data-p6-chart-group]')
  const a = form.querySelector('[data-p6-chart-a]')
  const b = form.querySelector('[data-p6-chart-b]')
  const c = form.querySelector('[data-p6-chart-c]')
  const mode = form.querySelector('[data-p6-chart-mode]')
  const all = [...source.querySelectorAll('option[data-p6-option]')]
  const refresh = () => {
    ;[a, b, c].forEach((select, i) => chartOptions(select, all, group.value, i === 2 ? 'Aucun' : 'Choisir une pièce'))
    const selected = [a, b, c].filter((select) => select.value).map((select) => all.find((option) => option.value === select.value)).filter(Boolean)
    if (selected.length < 2) {
      const p = document.createElement('p')
      p.className = 'phase6-empty'
      p.textContent = `Sélectionnez au moins deux des ${all.filter((option) => option.dataset.group === group.value).length} objets de ce groupe.`
      output.replaceChildren(p)
      return
    }
    const cards = document.createElement('div')
    cards.className = 'phase6-chart-grid'
    selected.forEach((option) => cards.append(chartCard(option, mode.value)))
    const explanation = document.createElement('p')
    explanation.className = 'phase6-note'
    explanation.textContent = 'Comparaison descriptive des champs exportés uniquement. Les champs vides restent inconnus; aucune classe, performance, recommandation ou tier list n’est calculée.'
    output.replaceChildren(cards, explanation)
  }
  group.addEventListener('change', refresh)
  ;[a, b, c, mode].forEach((select) => select.addEventListener('change', refresh))
  form.addEventListener('reset', () => requestAnimationFrame(() => {
    group.selectedIndex = 0
    a.value = ''
    b.value = ''
    c.value = ''
    mode.value = 'regular'
    refresh()
  }))
  refresh()
}

document.documentElement.classList.add('phase6-js')
activateArmorFilters()
activateModeTabs()
activateBossFilters()
activateArmorChart()
