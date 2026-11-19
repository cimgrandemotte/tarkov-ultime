/** Effets décoratifs légers, désactivables indépendamment du contenu. */
export function initAnimations(root = document) {
  const html = root.documentElement;
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  const heroes = [...root.querySelectorAll('[data-motion-hero]')];
  const reveals = [...root.querySelectorAll('[data-reveal]')];
  const seen = new Set();
  let raf = 0;
  let aosStarted = false;
  let observer;
  function reduced() { return preference.matches || html.dataset.motion === 'reduce'; }
  function render() {
    raf = 0;
    for (const el of heroes) {
      let shift = 0;
      if (!reduced() && seen.has(el)) {
        const top = el.getBoundingClientRect().top;
        shift = Math.min(33, Math.max(0, -top / 9));
      }
      el.style.setProperty('--parallax-shift', `${shift}px`);
    }
  }
  function tick() { if (!raf && !root.hidden) raf = requestAnimationFrame(render); }
  function fill() {
    for (const hero of heroes) {
      const target = hero.querySelector('[data-particles]');
      if (!target || target.childElementCount) continue;
      for (let i = 0; i < 16; ++i) {
        const drop = root.createElement('i');
        drop.className = 'particles__drop';
        drop.style.setProperty('--drop-left', `${36 + (i * 43) % 64}%`);
        drop.style.setProperty('--drop-top', `${(i * 7) % 66}%`);
        drop.style.setProperty('--drop-height', `${1.2 + .15 * (i % 6)}rem`);
        drop.style.setProperty('--fall', `${2.75 + (i % 5) * .2}s`);
        drop.style.setProperty('--delay', `${(i % 5) * .12}s`);
        target.append(drop);
      }
    }
  }
  function sync() {
    const quiet = reduced();
    observer?.disconnect();
    seen.clear();
    for (const hero of heroes) hero.dataset.motionVisible = 'false';
    for (const el of reveals) {
      el.removeAttribute('data-aos');
      el.classList.remove('aos-init', 'aos-animate', 'reveal-fallback', 'is-entering');
    }
    if (!quiet) {
      fill();
      if ('IntersectionObserver' in window) {
        observer = new IntersectionObserver((entries) => {
          if (quiet !== reduced()) return;
          for (const { target, isIntersecting } of entries) {
            if (target.hasAttribute('data-motion-hero')) {
              if (isIntersecting) seen.add(target);
              else seen.delete(target);
              target.dataset.motionVisible = String(isIntersecting);
            } else if (isIntersecting) {
              target.classList.add('is-entering');
              observer.unobserve(target);
            }
          }
          tick();
        }, { rootMargin: '0px', threshold: .06 });
        for (const el of heroes) observer.observe(el);
      }
      if (globalThis.AOS && reveals.length) {
        // Seuls les éléments décoratifs non focalisables reçoivent ces transitions.
        for (const el of reveals) el.setAttribute('data-aos', 'fade-up');
        if (!aosStarted) { globalThis.AOS.init({ duration: 400, offset: 0, once: true, disableMutationObserver: true }); aosStarted = true; }
        else globalThis.AOS.refreshHard();
      } else if (observer) {
        for (const el of reveals) { el.classList.add('reveal-fallback'); observer.observe(el); }
      }
    }
    tick();
  }
  preference.addEventListener('change', sync);
  root.addEventListener('guide:motion-change', sync);
  root.addEventListener('visibilitychange', tick);
  window.addEventListener('scroll', () => { if (!reduced() && seen.size) tick(); }, { passive: true });
  sync();
}
