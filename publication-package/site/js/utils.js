/** Utilitaires partagés sans dépendance de l'atelier. */
export function normalizeText(value) {
  return String(value ?? '').normalize('NFKD').replace(/\p{M}/gu, '').replace(/œ/gi, 'oe').toLocaleLowerCase('fr').replace(/\s+/g, ' ').trim();
}

export const numberFr = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 3 });
export const sortFr = new Intl.Collator('fr', { sensitivity: 'base', numeric: true });

export function storageRead(key, fallback = null) {
  try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; }
}
export function storageWrite(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* navigation privée ou système de fichiers en lecture seule */ }
}
export function parseRecord(script, fallback = null) {
  if (!script) return fallback;
  try { return JSON.parse(script.textContent); } catch { return fallback; }
}
export function sameOriginUrl(href, base = document.baseURI) {
  if (typeof href !== 'string' || !href.trim()) return null;
  try {
    const url = new URL(href, base);
    return url.origin === location.origin && /^(https?:)$/.test(url.protocol) && !url.username && !url.password ? url : null;
  } catch { return null; }
}
export async function loadJson(href) {
  const url = sameOriginUrl(href);
  if (!url) throw new Error('Source locale introuvable.');
  const response = await fetch(url, { credentials: 'same-origin' });
  if (!response.ok) throw new Error(`Source indisponible (${response.status}).`);
  return response.json();
}
export function node(tag, text, className) {
  const el = document.createElement(tag);
  if (text != null) el.textContent = String(text);
  if (className) el.className = className;
  return el;
}
