import React from 'react';
import Avatar from './Avatar.jsx';

function fmtTime(ts) {
  if (!ts) return '';
  try {
    return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return '';
  }
}

export default function Message({ msg, mine, langMeta, ui, showOriginal, onToggleOriginal }) {
  if (msg.system) {
    return (
      <div className="sysmsg">
        <span>{msg.text}</span>
      </div>
    );
  }

  const effective = showOriginal ? msg.text : msg.translation ?? msg.text;
  const canShowOriginal = msg.translation && msg.translated && msg.translation !== msg.text;

  return (
    <div className={'msg ' + (mine ? 'msg--mine' : 'msg--other')}>
      {!mine && <Avatar name={msg.sender} size={32} />}
      <div className="msg__col">
        {!mine && (
          <div className="msg__head">
            <span className="msg__name">{msg.sender}</span>
            {langMeta ? (
              <span className="lang-badge" title={langMeta.en}>
                {langMeta.flag} {langMeta.native}
              </span>
            ) : (
              <span className="lang-badge" title={msg.senderLang}>
                {msg.senderLang}
              </span>
            )}
          </div>
        )}
        <div className="bubble">
          <p className="bubble__text">{effective}</p>
          <div className="bubble__foot">
            <span className="bubble__time">{fmtTime(msg.ts)}</span>
            {canShowOriginal && (
              <button className="bubble__orig" onClick={() => onToggleOriginal(msg.id)}>
                {showOriginal ? ui.hideOriginal : ui.showOriginal}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
