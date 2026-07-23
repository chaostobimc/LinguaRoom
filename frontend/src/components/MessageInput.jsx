import React, { useEffect, useRef, useState } from 'react';
import { SendIcon } from '../icons.jsx';

export default function MessageInput({ onSend, onTyping, ui }) {
  const [text, setText] = useState('');
  const taRef = useRef(null);
  const stopRef = useRef(null);

  useEffect(() => {
    const ta = taRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 140) + 'px';
  }, [text]);

  const submit = () => {
    const v = text.trim();
    if (!v) return;
    onSend(v);
    setText('');
    if (stopRef.current) {
      clearTimeout(stopRef.current);
      stopRef.current = null;
    }
    onTyping(false);
  };

  const onChange = (e) => {
    setText(e.target.value);
    onTyping(true);
    if (stopRef.current) clearTimeout(stopRef.current);
    stopRef.current = setTimeout(() => onTyping(false), 1500);
  };

  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="composer">
      <textarea
        ref={taRef}
        className="composer__input"
        rows={1}
        value={text}
        placeholder={ui.messagePlaceholder}
        onChange={onChange}
        onKeyDown={onKey}
      />
      <button
        className="composer__send"
        onClick={submit}
        disabled={!text.trim()}
        aria-label={ui.send}
        title={ui.send}
      >
        <SendIcon />
      </button>
    </div>
  );
}
