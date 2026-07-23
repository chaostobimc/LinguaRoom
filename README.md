# LinguaRoom 🌍💬

Eine minimalistische, WhatsApp‑style Chat‑Plattform mit **automatischer KI‑Übersetzung**.
Jeder Teilnehmer wählt beim Beitreten seine eigene Sprache – alle Nachrichten
werden in Echtzeit in die jeweils gewählte Sprache übersetzt. Namen, Links,
E‑Mail‑Adressen und Code bleiben unverändert. Fragen bleiben Fragen (die KI
beantwortet sie nicht).

> Die Übersetzung läuft ausschließlich über das **deepseek4free**‑Projekt
> ([github.com/xtekky/deepseek4free](https://github.com/xtekky/deepseek4free)) –
> es wird **keine** offizielle/bezahlte API verwendet.

---

## ✨ Features

- **WhatsApp‑Style UI** – modern, elegant, minimalistisch, mit sanften Animationen.
- **Räume erstellen** – Name + Sprache wählen, Raum‑Link teilen.
- **Website wird automatisch übersetzt** – sobald eine Sprache gewählt ist,
  werden alle Oberflächentexte in diese Sprache übersetzt (für ~14 Sprachen
  sofort, für alle anderen on‑demand über die KI).
- **Auto‑Übersetzung pro Person** – jeder sieht die Nachrichten in *seiner*
  Sprache; das Original kann jederzeit eingeblendet werden.
- **~70 Sprachen** wählbar (Suche im Sprach‑Picker).
- **Namens‑/URL‑Schutz** – durch Platzhalter werden Eigennamen, Links,
  E‑Mails, `@mentions`, `#hashtags` und Code vor der Übersetzung geschützt.
- **Fragen bleiben Fragen** – die KI übersetzt nur, sie antwortet nicht.
- **Schnell** – Übersetzungen werden gecacht und concurrency‑begrenzt.
- **Robust** – ist die KI (oder das Token) nicht verfügbar, läuft der Chat
  trotzdem weiter und zeigt den Originaltext.

---

## 🧱 Tech‑Stack

| Bereich   | Technologie                              |
|-----------|------------------------------------------|
| Backend   | Python · FastAPI · WebSocket · `deepseek4free` (`dsk`) |
| Frontend  | React · Vite · reines CSS (keine UI‑Lib nötig)      |
| Echtzeit  | WebSocket pro Raum, Server pusht Original + Übersetzung |

---

## 🚀 Schnellstart

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --port 8000
```

### 2. Frontend (Entwicklung)

```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

Das Frontend (Vite, Port 5173) leitet `/api` und `/ws` automatisch an das
Backend (Port 8000) weiter.

### 3. Produktion (Backend serviert das gebaute Frontend)

```bash
cd frontend && npm install && npm run build
cd ../backend && source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
# Öffne http://localhost:8000  (SPA‑Fallback inklusive /r/<code>)
```

Oder einfach: `./start.sh` (installiert beide Seiten und startet den Server).

---

## 🤖 KI‑Übersetzung einrichten (deepseek4free)

Die Übersetzung nutzt den inoffiziellen, kostenlosen DeepSeek‑Client aus dem
deepseek4free‑Repo – **das `dsk`‑Paket ist bereits in `backend/vendor/dsk`
eingebunden**, du musst das Repo also nicht separat klonen. Es wird lediglich
ein **kostenloser DeepSeek‑Web‑Account‑Token** benötigt (kein bezahlter API‑Key).

1. **Abhängigkeiten installieren** (nur für die KI‑Übersetzung):
   ```bash
   pip install -r backend/requirements-ai.txt
   ```
2. **Token besorgen**:
   - Auf [chat.deepseek.com](https://chat.deepseek.com) einloggen.
   - DevTools → Console → ausführen:
     ```js
     JSON.parse(localStorage.getItem("userToken")).value
     ```
   - Den Wert kopieren.
3. **Token setzen** in `backend/.env`:
   ```ini
   DEEPSEEK_TOKEN=euer_token_hier
   ```
4. Backend neu starten. `GET /api/health` sollte dann
   `{"translation": true, "backend": "dsk"}` liefern.

> **Ohne Token** funktioniert die App trotzdem – es werden dann einfach die
> Originalnachrichten angezeigt (keine Übersetzung).

Um die Übersetzung komplett zu deaktivieren: `USE_DEEPSEEK=0` in der `.env`.

---

## 📁 Projektstruktur

```
LinguaRoom/
├── backend/
│   ├── main.py            # FastAPI: REST + WebSocket Chat
│   ├── translation.py     # deepseek4free‑Wrapper (Cache, Platzhalter, Prompt)
│   ├── ui_strings.py      # UI‑Übersetzungen (14 Sprachen + KI‑Fallback)
│   ├── languages.py       # ~70 Sprachen
│   ├── rooms.py           # Raum‑Speicher (In‑Memory + JSON)
│   ├── config.py          # Einstellungen
│   ├── requirements.txt
│   └── data/              # Raum‑Verlauf (automatisch, nicht committet)
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx, main.jsx, api.js, useChat.js, i18n.js, styles.css
│       └── components/  (Landing, ChatRoom, Message, LanguageSelect, …)
├── start.sh
└── README.md
```

---

## 🧠 Wie die Übersetzung funktioniert

1. Ein Client sendet eine Nachricht → der Server broadcastet sofort den
   **Originaltext** an alle (schnelle Wahrnehmung).
2. Der Server übersetzt den Text **einmal pro Zielsprache** (aller Teilnehmer)
   und pusht danach ein `translation`‑Event nur an die passenden Clients.
3. Übersetzungen werden gecacht (`text + Zielsprache`) → wiederholte Sätze
   sind sofort da.
4. Der strikte Prompt sorgt dafür, dass die KI **nur übersetzt**, Fragen als
   Fragen belässt und Namen/URLs/Code unangetastet lässt.

---

## ✅ Status

- Backend‑Logik (Räume, WebSocket, Presence, Typing, Übersetzungs‑Push,
  UI‑Lokalisierung, SPA‑Fallback) ist per Tests verifiziert.
- Live‑Übersetzung erfordert das deepseek4free‑Setup (siehe oben). Ohne Token
  läuft die App fehlerfrei mit Originaltexten weiter.
