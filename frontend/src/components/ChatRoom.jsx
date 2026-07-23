import React, { useEffect, useMemo, useRef, useState } from 'react';
import { getLanguages, getUI, shareLink } from '../api.js';
import { EN } from '../i18n.js';
import { useChat } from '../useChat.js';
import Avatar from './Avatar.jsx';
import LanguageSelect from './LanguageSelect.jsx';
import Message from './Message.jsx';
import TypingIndicator from './TypingIndicator.jsx';
import MessageInput from './MessageInput.jsx';
import {
  BackIcon,
  ShareIcon,
  CopyIcon,
  CheckIcon,
  GlobeIcon,
  SparkleIcon,
} from '../icons.jsx';

export default function ChatRoom({ roomId, navigate }) {
  const [profile, setProfile] = useState(() => {
    try {
      return JSON.parse(sessionStorage.getItem('lr_' + roomId) || 'null');
    } catch {
      return null;
    }
  });
  const [languages, setLanguages] = useState([]);

  useEffect(() => {
    getLanguages().then(setLanguages).catch(() => {});
  }, []);

  if (!profile) {
    return (
      <JoinPanel
        roomId={roomId}
        languages={languages}
        onJoin={(n, l) => {
          sessionStorage.setItem('lr_' + roomId, JSON.stringify({ name: n, lang: l }));
          setProfile({ name: n, lang: l });
        }}
      />
    );
  }

  return (
    <ChatRoomInner
      roomId={roomId}
      name={profile.name}
      lang={profile.lang}
      languages={languages}
      navigate={navigate}
    />
  );
}

function JoinPanel({ roomId, languages, onJoin }) {
  const [name, setName] = useState('');
  const [lang, setLang] = useState('en');
  const [ui, setUi] = useState(EN);
  const [error, setError] = useState('');

  useEffect(() => {
    getUI(lang).then(setUi).catch(() => {});
  }, [lang]);

  const submit = () => {
    if (!name.trim()) return setError(ui.invalidName);
    if (!lang) return setError(ui.invalidLang);
    setError('');
    onJoin(name.trim(), lang);
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
            <p className="brand__tag">
              {ui.joinTitle} · #{roomId}
            </p>
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

        <button className="btn btn--primary" onClick={submit}>
          {ui.joinCta}
        </button>
        <p className="hint">{ui.joinSubtitle}</p>
      </div>
    </div>
  );
}

function ChatRoomInner({ roomId, name, lang, languages, navigate }) {
  const [ui, setUi] = useState(EN);
  const [copied, setCopied] = useState(false);
  const [showOriginal, setShowOriginal] = useState(() => new Set());

  const chat = useChat(roomId, name, lang);

  useEffect(() => {
    getUI(lang).then(setUi).catch(() => {});
  }, [lang]);

  const langMap = useMemo(() => {
    const m = {};
    languages.forEach((l) => (m[l.code] = l));
    return m;
  }, [languages]);

  const endRef = useRef(null);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat.messages, chat.typing]);

  const copyLink = async () => {
    const link = shareLink(roomId);
    try {
      await navigator.clipboard.writeText(link);
    } catch {
      const ta = document.createElement('textarea');
      ta.value = link;
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand('copy');
      } catch {
        /* noop */
      }
      ta.remove();
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  const leave = () => {
    sessionStorage.removeItem('lr_' + roomId);
    navigate('/');
  };

  const toggleOriginal = (id) => {
    setShowOriginal((prev) => {
      const n = new Set(prev);
      if (n.has(id)) n.delete(id);
      else n.add(id);
      return n;
    });
  };

  const myLangMeta = langMap[lang];

  return (
    <div className="chat">
      <header className="chat__header">
        <button className="iconbtn" onClick={leave} title={ui.leave} aria-label={ui.leave}>
          <BackIcon />
        </button>
        <div className="chat__title">
          <div className="chat__room">
            {ui.appName} · #{roomId}
          </div>
          <div className="chat__sub">
            {chat.members.length} {ui.members.toLowerCase()}
            {myLangMeta && (
              <>
                {' · '}
                {myLangMeta.flag} {myLangMeta.native}
              </>
            )}
          </div>
        </div>
        <div className="chat__members">
          {chat.members.slice(0, 5).map((m) => (
            <Avatar
              key={m.client_id}
              name={m.name}
              size={30}
              me={m.client_id === chat.myId}
            />
          ))}
          {chat.members.length > 5 && (
            <span className="chat__more">+{chat.members.length - 5}</span>
          )}
        </div>
        <button className="iconbtn" onClick={copyLink} title={ui.copyLink} aria-label={ui.copyLink}>
          {copied ? <CheckIcon /> : <ShareIcon />}
        </button>
      </header>

      {chat.status === 'closed' && (
        <div className="connbar">
          <span>{ui.disconnected}</span>
          <button className="btn btn--tiny" onClick={chat.reconnectNow}>
            {ui.reconnect}
          </button>
        </div>
      )}
      {chat.status === 'connecting' && (
        <div className="connbar connbar--muted">{ui.connecting}</div>
      )}

      <div className="chat__body">
        <div className="chat__intro">
          <div className="chat__intro-logo">
            <GlobeIcon />
          </div>
          <h2>{ui.welcome}</h2>
          <p>{ui.shareHint}</p>
          <button className="btn btn--ghost btn--sm" onClick={copyLink}>
            {copied ? (
              <>
                <CheckIcon /> {ui.copied}
              </>
            ) : (
              <>
                <ShareIcon /> {ui.copyLink}
              </>
            )}
          </button>
        </div>

        {chat.messages.map((m) => (
          <Message
            key={m.id}
            msg={m}
            mine={m.senderId === chat.myId}
            langMeta={langMap[m.senderLang]}
            ui={ui}
            showOriginal={showOriginal.has(m.id)}
            onToggleOriginal={toggleOriginal}
          />
        ))}

        <TypingIndicator names={chat.typing} />
        <div ref={endRef} />
      </div>

      <MessageInput onSend={chat.send} onTyping={chat.sendTyping} ui={ui} />
    </div>
  );
}
