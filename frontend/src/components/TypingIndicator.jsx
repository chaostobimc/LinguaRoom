import React from 'react';

export default function TypingIndicator({ names }) {
  const list = Object.values(names || {});
  if (list.length === 0) return null;
  const label =
    list.length === 1
      ? `${list[0]} is typing`
      : list.length === 2
      ? `${list[0]} and ${list[1]} are typing`
      : `${list.length} people are typing`;
  return (
    <div className="typingbar">
      <span className="typingbar__dots">
        <i />
        <i />
        <i />
      </span>
      <span className="typingbar__label">{label}…</span>
    </div>
  );
}
