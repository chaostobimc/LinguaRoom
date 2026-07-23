import React, { useEffect, useState } from 'react';
import { getLanguages, getUI, createRoom } from '../api.js';
import { EN } from '../i18n.js';
import LanguageSelect from './LanguageSelect.jsx';
import { SparkleIcon } from '../icons.jsx';

export default function Landing({ navigate }) {
  const [languages, setLanguages] = useState([]);
  const [name, setName] = useState('');
  const [lang, setLang] = useState('en');
  const [joinCode, setJoinCode] = useState('');
  const [ui, setUi] = useState(EN);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getLanguages().then(setLanguages).catch(() => {});
  }, []);

  useEffect(() => {
    getUI(lang).then(setUi).catch(() => {});
  }, [lang]);

  const persist = (id, n, l) => {
    sessionStorage.setItem('lr_' + id, JSON.stringify({ name: n, lang: l }));
  };

  const enter = (id) => {
    if (!name.trim()) {
      setError(ui.invalidName);
      return;
    }
    if (!lang) {
      setError(ui.invalidLang);
      return;
    }
    setError('');
    persist(id, name.trim(), lang);
    navigate('/r/' + id);
  };

  const onCreate = async () => {
    if (!name.trim()) {
      setError(ui.invalidName);
      return;
    }
    if (!lang) {
      setError(ui.invalidLang);
      return;
    }
    setBusy(true);
    try {
      const { room_id } = await createRoom();
      persist(room_id, name.trim(), lang);
      navigate('/r/' + room_id);
    } catch {
      setError('Could not create room. Is the backend running?');
      setBusy(false);
    }
  };

  const onJoin = () => {
    const code = joinCode.trim();
    if (!code) return;
    enter(code);
  };

  return (
    <div className="landing">
      <div className="landing__bg" aria-hidden="true" />
      <div className="landing__card">
        <div className="brand">
          <div className="brand__logo">
            <SparkleIcon />
          </div>
          <div>
            <h1 className="brand__name">{ui.appName}</h1>
            <p className="brand__tag">{ui.tagline}</p>
          </div>
        </div>

        <label className="field">
          <span className="field__label">{ui.yourName}</span>
          <input
            className="field__input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={ui.namePlaceholder}
            maxLength={40}
          />
        </label>

        <div className="field">
          <span className="field__label">{ui.selectLanguage}</span>
          <LanguageSelect
            value={lang}
            onChange={setLang}
            languages={languages}
            placeholder={ui.selectLanguage}
            searchPlaceholder={ui.languagePlaceholder}
          />
        </div>

        {error && <div className="field__error">{error}</div>}

        <button className="btn btn--primary" onClick={onCreate} disabled={busy}>
          {busy ? '…' : ui.createRoom}
        </button>

        <div className="divider">
          <span>{ui.joinRoom}</span>
        </div>

        <div className="joinrow">
          <input
            className="field__input"
            value={joinCode}
            onChange={(e) => setJoinCode(e.target.value)}
            placeholder={ui.roomCode}
            onKeyDown={(e) => {
              if (e.key === 'Enter') onJoin();
            }}
          />
          <button className="btn btn--ghost" onClick={onJoin}>
            {ui.joinCta}
          </button>
        </div>
        <p className="hint">{ui.joinSubtitle}</p>
      </div>
    </div>
  );
}
