import React from 'react';

function colorFor(name) {
  let h = 0;
  const s = name || '?';
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) % 360;
  return `hsl(${h} 62% 52%)`;
}

function initials(name) {
  const s = (name || '?').trim();
  if (!s) return '?';
  const parts = s.split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

export default function Avatar({ name, size = 34, me = false }) {
  return (
    <div
      className={'avatar' + (me ? ' avatar--me' : '')}
      style={{ width: size, height: size, background: colorFor(name), fontSize: size * 0.4 }}
      title={name}
    >
      {initials(name)}
    </div>
  );
}
