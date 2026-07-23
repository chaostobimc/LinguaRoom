// Thin API client. All paths are relative so the app works behind the
// Vite dev proxy and behind the production backend alike.

const _langCache = { value: null };

export async function getLanguages() {
  if (_langCache.value) return _langCache.value;
  const res = await fetch('/api/languages');
  const data = await res.json();
  _langCache.value = data.languages;
  return _langCache.value;
}

export async function getUI(lang) {
  const res = await fetch('/api/ui?lang=' + encodeURIComponent(lang));
  const data = await res.json();
  return data.strings;
}

export async function createRoom() {
  const res = await fetch('/api/rooms', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: '{}',
  });
  return res.json();
}

export function shareLink(roomId) {
  return `${window.location.origin}/r/${roomId}`;
}
