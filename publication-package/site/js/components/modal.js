/** Modales natives : inertie d'arrière-plan, focus initial, sortie et retour. */
const returnTargets = new WeakMap();
const focusable = 'button:not([disabled]), a[href], input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), summary, [tabindex]:not([tabindex="-1"])';

export function openDialog(dialog, trigger = document.activeElement) {
  if (!globalThis.HTMLDialogElement || !(dialog instanceof HTMLDialogElement) || dialog.open || typeof dialog.showModal !== 'function') return false;
  if (document.querySelector('dialog[open]')) return false;
  returnTargets.set(dialog, trigger);
  dialog.showModal();
  dialog.querySelector('[data-modal-initial]')?.focus({ preventScroll: true });
  dialog.dispatchEvent(new CustomEvent('guide:open'));
  return true;
}
export function closeDialog(dialog, { restoreFocus = true } = {}) {
  if (!dialog?.open) return;
  if (!restoreFocus) returnTargets.delete(dialog);
  dialog.close();
}
export function initDialogs(root = document) {
  if (typeof globalThis.HTMLDialogElement?.prototype.showModal !== 'function') return;
  for (const dialog of root.querySelectorAll('dialog[data-modal]')) {
    let startedOnBackdrop = false;
    const outside = (event) => {
      const box = dialog.getBoundingClientRect();
      return event.target === dialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom);
    };
    dialog.addEventListener('pointerdown', (event) => { startedOnBackdrop = outside(event); });
    dialog.addEventListener('click', (event) => {
      if (event.target.closest('[data-modal-close]') || (startedOnBackdrop && outside(event))) closeDialog(dialog);
      startedOnBackdrop = false;
    });
    dialog.addEventListener('close', () => {
      const target = returnTargets.get(dialog);
      returnTargets.delete(dialog);
      if (target instanceof HTMLElement && target.isConnected && target.getClientRects().length && !target.matches(':disabled')) target.focus({ preventScroll: true });
    });
    // La boucle explicite évite que Tab fasse sortir le focus vers les contrôles du navigateur.
    dialog.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && !event.isComposing) {
        // Les champs type=search peuvent intercepter la première pression pour effacer le texte.
        event.preventDefault();
        closeDialog(dialog);
        return;
      }
      if (event.key !== 'Tab') return;
      const items = [...dialog.querySelectorAll(focusable)].filter((el) => el.tabIndex >= 0 && !el.closest('[hidden]') && el.getClientRects().length);
      if (!items.length) { event.preventDefault(); return; }
      const current = document.activeElement;
      const edge = event.shiftKey ? items[0] : items.at(-1);
      if (current === edge || (event.shiftKey && !items.includes(current))) {
        event.preventDefault();
        (event.shiftKey ? items.at(-1) : items[0]).focus();
      }
    });
  }
  root.addEventListener('click', (event) => {
    const trigger = event.target.closest('[data-modal-open]');
    if (!trigger || trigger.matches(':disabled')) return;
    const dialog = root.getElementById(trigger.dataset.modalOpen);
    if (openDialog(dialog, trigger)) event.preventDefault();
  });
}
