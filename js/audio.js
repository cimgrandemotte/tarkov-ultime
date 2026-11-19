/** Contrôleur Howler opt-in. Aucun chargement MP3 ni lecture avant une action. */
import { parseRecord, sameOriginUrl, storageRead, storageWrite } from './utils.js';

export function initAudio(root = document) {
  const deck = root.querySelector('[data-audio-deck]');
  const Howl = globalThis.Howl;
  if (!deck || typeof Howl !== 'function') return;
  const manifest = parseRecord(deck.querySelector('[data-audio-map]'));
  const controls = deck.querySelector('[data-audio-controls]');
  const select = deck.querySelector('[data-audio-select]');
  const output = deck.querySelector('[data-audio-status]');
  const range = deck.querySelector('[data-audio-volume]');
  const percent = deck.querySelector('[data-audio-percent]');
  if (!manifest || !controls || !select || !range || !output) return;
  const allowed = (records = []) => new Map(records.flatMap((track) => {
    const url = sameOriginUrl(track.src);
    return url && url.pathname.toLowerCase().endsWith('.mp3') ? [[track.id, { ...track, url }]] : [];
  }));
  const tracks = allowed(manifest.tracks);
  const cues = allowed(manifest.cues);
  const toggles = [...root.querySelectorAll('[data-audio-toggle]')];
  const errors = [...root.querySelectorAll('[data-audio-error]')];
  if (!tracks.has(select.value) || !toggles.length) return;
  let selected = tracks.get(select.value);
  let howl;
  let cueHowl;
  let loadTimer;
  let requested = false;
  let state = 'idle';
  const storageKey = 'tug:audio-volume:v1';
  const saved = storageRead(storageKey, 24);
  range.value = String(Number.isFinite(saved) && saved >= 0 && saved <= 100 ? saved : 24);
  function volume() { return Number(range.value) / 100; }
  function announceVolume() {
    const label = `${range.value} %`;
    if (percent) percent.textContent = label;
    range.setAttribute('aria-valuetext', label);
  }
  function paint(next, message) {
    state = next;
    deck.dataset.audioState = state;
    for (const button of toggles) {
      button.dataset.audioState = state;
      const text = button.querySelector('[data-audio-toggle-text]');
      if (text) text.textContent = state === 'playing' ? (button.dataset.pauseLabel || 'Mettre en pause') : state === 'loading' ? (button.dataset.waitLabel || 'Annuler le chargement') : (button.dataset.playLabel || 'Lire l’ambiance');
    }
    output.textContent = message || `${selected.label} · prêt à écouter.`;
    for (const region of errors) region.textContent = next === 'error' ? message : '';
  }
  function discard() {
    clearTimeout(loadTimer);
    requested = false;
    const old = howl;
    howl = undefined;
    old?.unload();
  }
  function fail(sound, message) {
    if (sound !== howl) return;
    discard();
    paint('error', message);
  }
  function start() {
    requested = true;
    paint('loading', `Chargement : ${selected.label}…`);
    if (!howl) {
      try {
        const sound = new Howl({ src: [selected.url.href], format: ['mp3'], loop: true, preload: true, volume: volume(),
          onplay() {
            if (sound !== howl || !requested) { sound.stop(); return; }
            clearTimeout(loadTimer);
            paint('playing', `En lecture : ${selected.label}.`);
          },
          onloaderror() { fail(sound, 'Piste introuvable ou illisible. Sélectionnez une autre ambiance.'); },
          onplayerror() { fail(sound, 'Lecture empêchée par le navigateur. Réessayez après avoir activé le son.'); },
        });
        howl = sound;
      } catch { requested = false; paint('error', 'Le lecteur n’a pas pu charger cette piste.'); return; }
    }
    const pending = howl;
    clearTimeout(loadTimer);
    loadTimer = setTimeout(() => fail(pending, 'La lecture n’a pas démarré. Vérifiez la sortie audio ou réessayez.'), 12000);
    howl.volume(volume());
    howl.play();
  }
  for (const button of toggles) {
    button.hidden = false;
    button.addEventListener('click', () => {
      if (state === 'loading') { discard(); paint('idle', 'Chargement annulé.'); }
      else if (state === 'playing') {
        requested = false;
        howl?.pause();
        paint('paused', `${selected.label} · en pause.`);
      } else start();
    });
  }
  select.addEventListener('change', () => {
    const next = tracks.get(select.value);
    if (!next) return;
    discard();
    selected = next;
    paint('idle');
  });
  range.addEventListener('input', () => {
    announceVolume();
    howl?.volume(volume());
    cueHowl?.volume(Math.min(.55, volume()));
    storageWrite(storageKey, Number(range.value));
  });
  for (const button of deck.querySelectorAll('[data-audio-cue]')) {
    const cue = cues.get(button.dataset.audioCue);
    if (!cue) continue;
    button.addEventListener('click', () => {
      cueHowl?.unload();
      // Les signaux d'exemple ne sont jamais déclenchés au survol ni par une notification système.
      cueHowl = new Howl({ src: [cue.url.href], format: ['mp3'], volume: Math.min(.55, volume()), onloaderror: () => { output.textContent = 'Signal indisponible.'; } });
      cueHowl.play();
    });
  }
  announceVolume();
  deck.querySelector('[data-audio-fallback]')?.setAttribute('hidden', '');
  controls.hidden = false;
  paint('idle');
  window.addEventListener('pagehide', () => {
    discard();
    cueHowl?.unload();
    cueHowl = undefined;
    paint('idle');
  });
}
