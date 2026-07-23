import React, { useEffect, useState } from 'react';
import { getLanguages, getUI, createRoom } from '../api.js';
import { EN } from '../i18n.js';
import LanguageSelect from './LanguageSelect.jsx';
import { SparkleIcon, GlobeIcon, UsersIcon, SendIcon } from '../icons.jsx';

// Cycling examples for the live translation demo.
const DEMO = [
  { f1: '🇫🇷', f2: '🇬🇧', a: 'Bonjour !', b: 'Hello !' },
  { f1: '🇩🇪', f2: '🇪🇸', a: 'Wie geht’s?', b: '¿Cómo estás?' },
  { f1: '🇯🇵', f2: '🇩🇪', a: 'こんにちは', b: 'Hallo' },
  { f1: '🇸🇦', f2: '🇫🇷', a: 'مرحبا', b: 'Bonjour' },
  { f1: '🇷🇺', f2: '🇬🇧', a: 'Привет', b: 'Hi' },
  { f1: '🇰🇷', f2: '🇮🇹', a: '안녕하세요', b: 'Ciao' },
];

const BUBBLES = [
  '🇩🇪', '🇪🇸', '🇫🇷', '🇯🇵', '🇨🇳', '🇷🇺',
  '🇧🇷', '🇮🇳', '🇸🇦', '🇰🇷', '🇮🇹', '🇳🇱',
];

export default function Landing({ navigate }) {
  const [languages, setLanguages] = useState([]);
  const [name, setName] = useState('');
  const [lang, setLang] = useState('en');
  const [joinCode, setJoinCode] = useState('');
  const [ui, setUi] = useState(EN);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [demo, setDemo] = useState(0);

  useEffect(() => {
    getLanguages().then(setLanguages).catch(() => {});
  }, []);

  useEffect(() => {
    getUI(lang).then(setUi).catch(() => {});
  }, [lang]);

  useEffect(() => {
    const id = setInterval(() => setDemo((d) => (d + 1) % DEMO.length), 2600);
    return () => clearInterval(id);
  }, []);

  const persist = (id, n, l) => {
    sessionStorage.setItem('lr_' + id, JSON.stringify({ name: n, lang: l }));
  };

  const enter = (id) => {
    if (!name.trim()) return setError(ui.invalidName);
    if (!lang) return setError(ui.invalidLang);
    setError('');
    persist(id, name.trim(), lang);
    navigate('/r/' + id);
  };

  const onCreate = async () => {
    if (!name.trim()) return setError(ui.invalidName);
    if (!lang) return setError(ui.invalidLang);
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

  const d = DEMO[demo];

  return (
    <div className="landing">
      <div className="landing__bg" aria-hidden="true" />
      <div className="landing__bubbles" aria-hidden="true">
        {BUBBLES.map((b, i) => (
          <span
            key={i}
            className="lbbubble"
            style={{
              left: ((i * 8.3 + 3) % 92) + '%',
              top: ((i * 13.7 + 6) % 86) + '%',
              animationDelay: (i * 0.7) + 's',
              animationDuration: (9 + (i % 4)) + 's',
            }}
          >
            {b}
          </span>
        ))}
      </div>

      <div className="landing__inner">
        <section className="hero">
          <div className="brand">
            <div className="brand__logo">
              <SparkleIcon />
            </div>
            <div>
              <h1 className="brand__name">{ui.appName}</h1>
            </div>
          </div>

          <h2 className="hero__title">{ui.heroTitle}</h2>
          <p className="hero__sub">{ui.heroSub}</p>

          <div className="hero__features">
            <div className="feature">
              <span className="feature__icon">
                <GlobeIcon />
              </span>
              <div>
                <b>{ui.feat1Title}</b>
                <br />
                <span className="feature__muted">{ui.feat1Desc}</span>
              </div>
            </div>
            <div className="feature">
              <span className="feature__icon">
                <SparkleIcon />
              </span>
              <div>
                <b>{ui.feat2Title}</b>
                <br />
                <span className="feature__muted">{ui.feat2Desc}</span>
              </div>
            </div>
            <div className="feature">
              <span className="feature__icon">
                <UsersIcon />
              </span>
              <div>
                <b>{ui.feat3Title}</b>
                <br />
                <span className="feature__muted">{ui.feat3Desc}</span>
              </div>
            </div>
          </div>

          <div className="demochat" key={demo}>
            <div className="demochat__bubble demochat__bubble--in">
              {d.a}
              <i>{d.f1}</i>
            </div>
            <div className="demochat__spark">
              <SparkleIcon />
            </div>
            <div className="demochat__bubble demochat__bubble--out">
              {d.b}
              <i>{d.f2}</i>
            </div>
          </div>
        </section>

        <section className="landing__card">
          <label className="field">
            <span className="field__label">{ui.yourName}</span>
            <input
              className="field__input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={ui.namePlaceholder}
              maxLength={40}
              autoFocus
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
        </section>
      </div>

      <p className="landing__foot">{ui.noAccount}</p>
    </div>
  );
}
