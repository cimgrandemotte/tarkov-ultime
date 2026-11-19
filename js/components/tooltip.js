/** Bulle non interactive : survol, focus, action tactile et fermeture par Échap. */
export function initTooltips(root = document) {
  let active;
  let delay;
  let pinned = false;
  function place() {
    if (!active) return;
    const { trigger, bubble } = active;
    const b = trigger.getBoundingClientRect();
    const view = document.documentElement;
    const right = view.clientWidth - bubble.offsetWidth - 8;
    const x = Math.max(8, Math.min(right, b.left + (b.width - bubble.offsetWidth) / 2));
    const y = b.bottom + bubble.offsetHeight + 10 < view.clientHeight ? b.bottom + 7 : b.top - bubble.offsetHeight - 7;
    bubble.style.left = `${x}px`;
    bubble.style.top = `${Math.max(8, y)}px`;
  }
  function hide() {
    clearTimeout(delay);
    if (active) active.bubble.hidden = true;
    active = undefined;
    pinned = false;
  }
  function show(trigger, bubble) {
    clearTimeout(delay);
    if (active?.trigger !== trigger) { hide(); active = { trigger, bubble }; }
    bubble.hidden = false;
    place();
  }
  function soon() {
    clearTimeout(delay);
    delay = setTimeout(() => {
      if (!pinned && active && document.activeElement !== active.trigger) hide();
    }, 145);
  }
  for (const trigger of root.querySelectorAll('[data-tooltip]')) {
    const bubble = root.getElementById(trigger.getAttribute('aria-describedby') ?? '');
    if (!bubble) continue;
    trigger.hidden = false;
    trigger.addEventListener('pointerenter', (event) => { if (event.pointerType !== 'touch') show(trigger, bubble); });
    trigger.addEventListener('pointerleave', soon);
    bubble.addEventListener('pointerenter', () => clearTimeout(delay));
    bubble.addEventListener('pointerleave', soon);
    trigger.addEventListener('focus', () => show(trigger, bubble));
    trigger.addEventListener('blur', hide);
    trigger.addEventListener('click', () => {
      if (pinned && active?.trigger === trigger) hide();
      else { show(trigger, bubble); pinned = true; }
    });
  }
  root.addEventListener('pointerdown', (event) => {
    if (active && !active.trigger.contains(event.target) && !active.bubble.contains(event.target)) hide();
  });
  root.addEventListener('keydown', (event) => { if (event.key === 'Escape' && active) { hide(); event.preventDefault(); } });
  window.addEventListener('resize', place, { passive: true });
  window.addEventListener('scroll', place, { passive: true });
}
