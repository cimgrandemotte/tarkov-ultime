/** Navigation par liens et disclosures natifs, sans faux rôles de menu desktop. */
export function initNavigation(root = document) {
  for (const header of root.querySelectorAll('[data-site-header]')) {
    const nav = header.querySelector('[data-site-nav]');
    const toggle = header.querySelector('[data-nav-toggle]');
    if (!nav || !toggle) continue;
    const narrow = matchMedia('(max-width: 51.99rem)');
    const disclosures = [...nav.querySelectorAll('[data-nav-disclosure]')];
    // On mobile, keep the no-JS layout stable until the user opens/closes the
    // disclosure; collapsing it during late module startup would shift the page.
    let expanded = narrow.matches;
    function paint() {
      toggle.hidden = !narrow.matches;
      toggle.setAttribute('aria-expanded', String(narrow.matches && expanded));
      nav.hidden = narrow.matches && header.dataset.enhanced === 'true' && !expanded;
    }
    function dismiss(focus = false) {
      for (const el of disclosures) el.open = false;
      if (narrow.matches) header.dataset.enhanced = 'true';
      expanded = false;
      paint();
      if (focus && narrow.matches) toggle.focus();
    }
    if (!narrow.matches) header.dataset.enhanced = 'true';
    toggle.addEventListener('click', () => {
      if (expanded) dismiss();
      else {
        if (narrow.matches) header.dataset.enhanced = 'true';
        expanded = true;
        paint();
        nav.querySelector('a, summary')?.focus();
      }
    });
    for (const disclosure of disclosures) {
      disclosure.addEventListener('toggle', () => {
        if (disclosure.open) for (const other of disclosures) if (other !== disclosure) other.open = false;
      });
    }
    root.addEventListener('pointerdown', (event) => { if (!header.contains(event.target)) dismiss(); });
    header.addEventListener('keydown', (event) => {
      if (event.key !== 'Escape') return;
      const open = disclosures.find((el) => el.open);
      if (open) { open.open = false; open.querySelector('summary')?.focus(); event.preventDefault(); }
      else if (expanded && narrow.matches) { dismiss(true); event.preventDefault(); }
    });
    header.addEventListener('focusout', (event) => {
      if (event.relatedTarget && !header.contains(event.relatedTarget)) dismiss();
    });
    nav.addEventListener('click', (event) => {
      const link = event.target.closest('a[href]');
      if (!link || event.metaKey || event.altKey || event.shiftKey || event.ctrlKey) return;
      dismiss();
      if (!link.getAttribute('href').startsWith('#')) return;
      const anchor = root.getElementById(link.hash.slice(1));
      if (anchor) requestAnimationFrame(() => {
        if (!anchor.hasAttribute('tabindex')) anchor.tabIndex = -1;
        anchor.focus({ preventScroll: true });
      });
    });
    // L'en-tête peut occuper deux lignes si la taille du texte est augmentée.
    if ('ResizeObserver' in window) new ResizeObserver(() => {
      const sticky = getComputedStyle(header).position === 'sticky';
      root.documentElement.style.setProperty('--site-header-offset', `${sticky ? header.offsetHeight : 0}px`);
    }).observe(header);
    narrow.addEventListener('change', () => {
      const hasNavFocus = nav.contains(root.activeElement);
      dismiss(narrow.matches && hasNavFocus);
    });
    paint();
  }
}
