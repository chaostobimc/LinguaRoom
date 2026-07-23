"""LinguaRoom backend — FastAPI + WebSocket real-time translation chat."""
import json
import logging
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

import config
import languages
import rooms
import translation
import ui_strings

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("linguaroom")

FRONTEND_DIST = config.BASE_DIR.parent / "frontend" / "dist"

app = FastAPI(title="LinguaRoom", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------- #
# REST endpoints
# ---------------------------------------------------------------------- #
@app.get("/api/health")
async def health():
    return {"status": "ok", **translation_status()}


@app.get("/api/translate-test")
async def translate_test(text: str = "Hello, how are you?", target: str = "German"):
    """Self-diagnosis: try a real translation with the configured backend."""
    status = translation_status()
    if not status["available"]:
        return {**status, "source": text, "target": target, "result": None}
    try:
        result = await translation.translator.translate(text, target)
        return {
            **status,
            "source": text,
            "target": target,
            "result": result,
            "translated": result != text,
        }
    except Exception as exc:
        logger.error("translate-test failed: %s", exc)
        return {**status, "source": text, "target": target, "result": None, "error": str(exc)}


@app.get("/api/languages")
async def list_languages():
    return {"languages": languages.LANGUAGES}


@app.get("/api/ui")
async def get_ui(lang: str = "en"):
    return {"lang": lang, "strings": await ui_strings.get_ui(lang)}


@app.post("/api/rooms")
async def create_room(payload: dict = None):
    payload = payload or {}
    room_id = rooms.new_room_id()
    rooms.get_or_create_room(room_id)
    return {"room_id": room_id}


@app.get("/api/rooms/{room_id}")
async def room_info(room_id: str):
    room = rooms.get_or_create_room(room_id)
    return {
        "exists": True,
        "room_id": room_id,
        "members": room.members,
        "message_count": len(room.messages),
    }


# ---------------------------------------------------------------------- #
# WebSocket chat
# ---------------------------------------------------------------------- #
async def _send(ws, payload):
    try:
        await ws.send_json(payload)
    except Exception:
        return False
    return True


async def broadcast(room: rooms.Room, payload: dict, skip=None, lang_filter=None):
    dead = []
    for c in list(room.connections):
        if c is skip:
            continue
        if lang_filter and c.lang != lang_filter:
            continue
        if not await _send(c.ws, payload):
            dead.append(c)
    for c in dead:
        room.remove(c)


async def send_presence(room: rooms.Room):
    await broadcast(room, {"type": "presence", "members": room.members})


async def send_system(room: rooms.Room, text: str):
    await broadcast(
        room,
        {"type": "system", "text": text, "ts": int(time.time() * 1000)},
    )


async def send_history(room: rooms.Room, conn: rooms.Connection):
    out = []
    for m in room.messages:
        t = m["translations"].get(conn.lang)
        if t is None:
            t = await translation.translator.translate(m["text"], conn.lang)
            m["translations"][conn.lang] = t
        out.append(
            {
                "id": m["id"],
                "sender": m["sender"],
                "senderLang": m["senderLang"],
                "senderId": m["senderId"],
                "text": m["text"],
                "ts": m["ts"],
                "translation": t,
                "translated": t != m["text"],
            }
        )
    await _send(conn.ws, {"type": "history", "messages": out})


async def handle_message(room: rooms.Room, conn: rooms.Connection, text: str):
    msg_id = uuid.uuid4().hex
    ts = int(time.time() * 1000)
    msg = {
        "id": msg_id,
        "sender": conn.name,
        "senderLang": conn.lang,
        "senderId": conn.client_id,
        "text": text,
        "ts": ts,
        "translations": {},
    }
    room.add_message(msg)

    # 1) Broadcast the original immediately to everyone (fast perceived speed).
    await broadcast(
        room,
        {
            "type": "message",
            "message": {
                "id": msg_id,
                "sender": conn.name,
                "senderLang": conn.lang,
                "senderId": conn.client_id,
                "text": text,
                "ts": ts,
                "translation": None,
                "translated": False,
            },
        },
    )

    # 2) Translate once per distinct target language and push updates.
    distinct_langs = {c.lang for c in room.connections}
    for lang in distinct_langs:
        translation_text = await translation.translator.translate(text, lang)
        msg["translations"][lang] = translation_text
        await broadcast(
            room,
            {
                "type": "translation",
                "message_id": msg_id,
                "lang": lang,
                "translation": translation_text,
                "translated": translation_text != text,
            },
            lang_filter=lang,
        )


def translation_status() -> dict:
    """Summarise whether AI translation is active and why not if disabled."""
    t = translation.translator
    if not config.USE_DEEPSEEK:
        return {"available": False, "backend": None, "note": "disabled (USE_DEEPSEEK=0)"}
    if t._client is None:
        note = (
            "DEEPSEEK_TOKEN not set"
            if not config.DEEPSEEK_TOKEN
            else "dsk not importable — install backend/requirements-ai.txt"
        )
        return {"available": False, "backend": None, "note": note}
    return {"available": True, "backend": t._kind, "note": "ok"}


@app.websocket("/ws/{room_id}")
async def ws_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    # Name / language / client id arrive as WebSocket URL query params (the
    # frontend puts them there). Reading them directly avoids blocking on a
    # first frame and ensures names/languages are correct from the start.
    qp = websocket.query_params
    name = (qp.get("name") or "Guest").strip()[:40] or "Guest"
    lang = (qp.get("lang") or "en").strip() or "en"
    client_id = qp.get("client_id") or uuid.uuid4().hex

    room = rooms.get_or_create_room(room_id)
    conn = rooms.Connection(websocket, name, lang, client_id)
    room.add(conn)

    await _send(
        websocket,
        {
            "type": "welcome",
            "client_id": client_id,
            "room_id": room_id,
            "you": {"name": name, "lang": lang},
            "translation": translation_status(),
        },
    )
    await send_presence(room)
    await send_history(room, conn)
    await send_system(room, f"{name} joined")

    try:
        while True:
            msg = await websocket.receive_json()
            t = msg.get("type")
            if t == "message":
                text = (msg.get("text") or "").strip()
                if not text:
                    continue
                if len(text) > 4000:
                    text = text[:4000]
                await handle_message(room, conn, text)
            elif t == "typing":
                await broadcast(
                    room,
                    {
                        "type": "typing",
                        "client_id": client_id,
                        "name": name,
                        "is_typing": bool(msg.get("is_typing")),
                    },
                    skip=conn,
                )
            elif t == "rename":
                new_name = (msg.get("name") or "").strip()[:40]
                if new_name:
                    conn.name = new_name
                    await send_presence(room)
            elif t == "ping":
                await _send(websocket, {"type": "pong"})
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        logger.warning("WS error in room %s: %s", room_id, exc)
    finally:
        room.remove(conn)
        await send_presence(room)
        await send_system(room, f"{name} left")


# ---------------------------------------------------------------------- #
# SPA fallback (serve built frontend if present)
# ---------------------------------------------------------------------- #
@app.get("/{full_path:path}")
async def spa(full_path: str):
    if FRONTEND_DIST.exists():
        candidate = FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(str(candidate))
        index = FRONTEND_DIST / "index.html"
        if index.exists():
            return FileResponse(str(index))
    return JSONResponse(
        {
            "detail": "LinguaRoom API. Frontend not built yet — run `npm run build` in frontend/.",
            "endpoints": ["/api/languages", "/api/ui?lang=en", "/api/rooms", "/ws/{room_id}"],
        },
        status_code=200,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
