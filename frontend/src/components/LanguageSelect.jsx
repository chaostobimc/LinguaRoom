import React, { useEffect, useRef, useState } from 'react';
import { GlobeIcon } from '../icons.jsx';

export default function LanguageSelect({
  value,
  onChange,
  languages,
  placeholder = 'Select language',
  searchPlaceholder = 'Search languages…',
  align = 'left',
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const ref = useRef(null);

  useEffect(() => {
    function onDoc(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, []);

  const selected = languages.find((l) => l.code === value);
  const q = query.trim().toLowerCase();
  const filtered = q
    ? languages.filter(
        (l) =>
          l.en.toLowerCase().includes(q) ||
          l.native.toLowerCase().includes(q) ||
          l.code.toLowerCase().includes(q)
      )
    : languages;

  return (
    <div className={'langselect' + (open ? ' langselect--open' : '')} ref={ref}>
      <button
        type="button"
        className="langselect__btn"
        onClick={() => setOpen((o) => !o)}
      >
        {selected ? (
          <span className="langselect__value">
            <span className="langselect__flag">{selected.flag}</span>
            <span>{selected.native}</span>
          </span>
        ) : (
          <span className="langselect__placeholder">{placeholder}</span>
        )}
        <span className="langselect__caret">▾</span>
      </button>

      {open && (
        <div className={'langselect__pop ' + (align === 'right' ? 'langselect__pop--right' : '')}>
          <div className="langselect__search">
            <GlobeIcon className="langselect__searchicon" />
            <input
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={searchPlaceholder}
            />
          </div>
          <div className="langselect__list">
            {filtered.map((l) => (
              <button
                type="button"
                key={l.code}
                className={'langselect__opt' + (l.code === value ? ' is-active' : '')}
                onClick={() => {
                  onChange(l.code);
                  setOpen(false);
                  setQuery('');
                }}
              >
                <span className="langselect__flag">{l.flag}</span>
                <span className="langselect__opt-native">{l.native}</span>
                <span className="langselect__opt-en">{l.en}</span>
              </button>
            ))}
            {filtered.length === 0 && (
              <div className="langselect__empty">No languages found</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
