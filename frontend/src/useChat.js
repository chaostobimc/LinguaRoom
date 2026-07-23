import { useCallback, useEffect, useRef, useState } from 'react';

// Works in secure contexts (https/localhost) and falls back elsewhere
// (e.g. http over a LAN IP, where crypto.randomUUID is unavailable).
function makeId() {
  try {
    return crypto.randomUUID();
  } catch {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }
}

// Real-time chat hook backed by the backend WebSocket.
// The backend pushes the original message immediately and then streams a
// `translation` event per recipient language, so the UI can show the
// translated text as soon as it is ready.
export function useChat(roomId, name, lang) {
  const [messages, setMessages] = useState([]);
  const [members, setMembers] = useState([]);
  const [typing, setTyping] = useState({}); // clientId -> name
  const [status, setStatus] = useState('connecting'); // connecting | open | closed
  const [myId, setMyId] = useState(null);
  const [translation, setTranslation] = useState(null);

  const wsRef = useRef(null);
  const clientIdRef = useRef(makeId());
  const reconnectRef = useRef(null);
  const closedByUser = useRef(false);
  const seen = useRef(new Set());

  const handle = useCallback((data) => {
    switch (data.type) {
      case 'welcome':
        setMyId(data.client_id);
        setTranslation(data.translation ?? null);
        break;
      case 'history': {
        seen.current = new Set(data.messages.map((m) => m.id));
        setMessages(data.messages);
        break;
      }
      case 'message': {
        const m = data.message;
        if (seen.current.has(m.id)) return;
        seen.current.add(m.id);
        setMessages((prev) => [...prev, m]);
        break;
      }
      case 'translation':
        setMessages((prev) =>
          prev.map((m) =>
            m.id === data.message_id
              ? { ...m, translation: data.translation, translated: data.translated }
              : m
          )
        );
        break;
      case 'typing':
        setTyping((prev) => {
          const next = { ...prev };
          if (data.is_typing) next[data.client_id] = data.name;
          else delete next[data.client_id];
          return next;
        });
        break;
      case 'presence':
        setMembers(data.members);
        break;
      case 'system':
        setMessages((prev) => [
          ...prev,
          { id: 'sys-' + data.ts + '-' + Math.random().toString(36).slice(2), system: true, text: data.text },
        ]);
        break;
      default:
        break;
    }
  }, []);

  const connect = useCallback(() => {
    if (reconnectRef.current) clearTimeout(reconnectRef.current);
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const url =
      `${proto}://${window.location.host}/ws/${roomId}` +
      `?name=${encodeURIComponent(name)}&lang=${encodeURIComponent(lang)}` +
      `&client_id=${clientIdRef.current}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;
    setStatus('connecting');

    ws.onopen = () => {
      setStatus('open');
      // Send the join handshake (name / language / client id). The backend
      // also reads these from the URL query params, so this is belt-and-braces.
      try {
        ws.send(
          JSON.stringify({
            type: 'join',
            name,
            lang,
            client_id: clientIdRef.current,
          })
        );
      } catch {
        /* noop */
      }
    };
    ws.onmessage = (ev) => {
      try {
        handle(JSON.parse(ev.data));
      } catch {
        /* ignore malformed frames */
      }
    };
    ws.onclose = () => {
      setStatus('closed');
      if (!closedByUser.current) {
        reconnectRef.current = setTimeout(connect, 2500);
      }
    };
    ws.onerror = () => {
      try {
        ws.close();
      } catch {
        /* noop */
      }
    };
  }, [roomId, name, lang, handle]);

  useEffect(() => {
    closedByUser.current = false;
    connect();
    return () => {
      closedByUser.current = true;
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      try {
        wsRef.current && wsRef.current.close();
      } catch {
        /* noop */
      }
    };
  }, [connect]);

  const send = useCallback((text) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'message', text }));
    }
  }, []);

  const sendTyping = useCallback((isTyping) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'typing', is_typing: isTyping }));
    }
  }, []);

  const reconnectNow = useCallback(() => {
    closedByUser.current = false;
    try {
      wsRef.current && wsRef.current.close();
    } catch {
      /* noop */
    }
    connect();
  }, [connect]);

  return { messages, members, typing, status, myId, translation, send, sendTyping, reconnectNow };
}
