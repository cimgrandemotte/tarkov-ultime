/** Des sections lisibles sans JS deviennent un tablist une fois améliorées. */
export function initTabs(root = document) {
  for (const component of root.querySelectorAll('[data-tabs]')) {
    const nav = component.querySelector('[data-tabs-nav]');
    const buttons = [...(nav?.querySelectorAll('[data-tab]') ?? [])];
    const panels = buttons.map((button) => root.getElementById(button.dataset.tab));
    if (!nav || !buttons.length || panels.some((el) => !el)) continue;
    function select(index, focus = false) {
      for (const [i, button] of buttons.entries()) {
        button.setAttribute('aria-selected', String(i === index));
        button.tabIndex = i === index ? 0 : -1;
        panels[i].hidden = i !== index;
      }
      if (focus) buttons[index].focus();
    }
    nav.setAttribute('role', 'tablist');
    for (const [i, button] of buttons.entries()) {
      button.setAttribute('role', 'tab');
      button.setAttribute('aria-controls', panels[i].id);
      panels[i].setAttribute('role', 'tabpanel');
      panels[i].setAttribute('aria-labelledby', button.id);
      panels[i].tabIndex = 0;
      button.addEventListener('click', () => select(i));
    }
    nav.addEventListener('keydown', (event) => {
      const index = buttons.indexOf(event.target);
      if (index < 0) return;
      const next = { ArrowRight: (index + 1) % buttons.length, ArrowLeft: (index - 1 + buttons.length) % buttons.length, Home: 0, End: buttons.length - 1 }[event.key];
      if (next !== undefined) { event.preventDefault(); select(next, true); }
    });
    select(0);
    nav.hidden = false;
  }
}
