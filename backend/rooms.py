"""In-memory room + connection store with lightweight JSON persistence."""
import json
import time
import uuid
from pathlib import Path

import config

_rooms: dict = {}


class Connection:
    __slots__ = ("ws", "name", "lang", "client_id", "joined_at")

    def __init__(self, ws, name, lang, client_id):
        self.ws = ws
        self.name = name
        self.lang = lang
        self.client_id = client_id
        self.joined_at = time.time()


class Room:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.connections = set()
        self.messages = []
        self.created_at = time.time()
        self._load()

    # -- membership ----------------------------------------------------- #
    def add(self, conn: Connection):
        self.connections.add(conn)

    def remove(self, conn: Connection):
        self.connections.discard(conn)

    @property
    def members(self):
        return [
            {"client_id": c.client_id, "name": c.name, "lang": c.lang}
            for c in self.connections
        ]

    # -- messages ------------------------------------------------------- #
    def add_message(self, msg: dict):
        self.messages.append(msg)
        if len(self.messages) > config.MAX_HISTORY:
            self.messages = self.messages[-config.MAX_HISTORY :]
        self._save()

    # -- persistence ---------------------------------------------------- #
    def _path(self) -> Path:
        return config.DATA_DIR / f"{self.room_id}.json"

    def _load(self):
        try:
            p = self._path()
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8"))
                self.messages = data.get("messages", [])[: config.MAX_HISTORY]
        except Exception:
            pass

    def _save(self):
        try:
            p = self._path()
            tmp = p.with_suffix(".tmp")
            payload = {
                "messages": [
                    {
                        "id": m["id"],
                        "sender": m["sender"],
                        "senderLang": m["senderLang"],
                        "senderId": m["senderId"],
                        "text": m["text"],
                        "ts": m["ts"],
                        "translations": m.get("translations", {}),
                    }
                    for m in self.messages
                ]
            }
            tmp.write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )
            tmp.replace(p)
        except Exception:
            pass


def get_or_create_room(room_id: str) -> Room:
    if room_id not in _rooms:
        _rooms[room_id] = Room(room_id)
    return _rooms[room_id]


def room_exists(room_id: str) -> bool:
    return room_id in _rooms and len(_rooms[room_id].messages) >= 0


def new_room_id() -> str:
    """Short, URL-friendly, unique room id."""
    while True:
        rid = uuid.uuid4().hex[:8]
        if rid not in _rooms:
            return rid
