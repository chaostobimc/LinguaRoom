"""Smoke test for the LinguaRoom backend (no AI required)."""
import json
import sys

from fastapi.testclient import TestClient

import main  # noqa: E402

client = TestClient(main.app)


def test_languages():
    r = client.get("/api/languages")
    assert r.status_code == 200
    langs = r.json()["languages"]
    assert any(l["code"] == "de" for l in langs)
    print(f"[ok] /api/languages -> {len(langs)} languages")


def test_ui():
    r = client.get("/api/ui?lang=de")
    assert r.status_code == 200
    s = r.json()["strings"]
    assert s["send"] == "Senden", s["send"]
    print("[ok] /api/ui?lang=de -> send =", s["send"])


def recv_until(ws, want, max_msgs=12):
    """Receive messages, discarding others, until one of ``want`` arrives."""
    for _ in range(max_msgs):
        m = ws.receive_json()
        if m["type"] in want:
            return m
    raise AssertionError(f"did not receive {want}")


def test_room_and_ws():
    r = client.post("/api/rooms", json={})
    assert r.status_code == 200
    room_id = r.json()["room_id"]
    print("[ok] created room", room_id)

    with client.websocket_connect(f"/ws/{room_id}?name=Maria&lang=de&client_id=A") as a, \
         client.websocket_connect(f"/ws/{room_id}?name=Yuki&lang=ja&client_id=B") as b:
        # Name/lang/client_id arrive via URL query params (like the real
        # frontend). The server sends 'welcome' immediately with the right info.
        aw = a.receive_json()
        bw = b.receive_json()
        assert aw["type"] == "welcome" and bw["type"] == "welcome"
        assert aw["you"]["name"] == "Maria" and aw["you"]["lang"] == "de"
        assert bw["you"]["name"] == "Yuki" and bw["you"]["lang"] == "ja"

        # Wait until both see each other in presence.
        for ws in (a, b):
            p = recv_until(ws, {"presence"})
            while len(p["members"]) < 2:
                p = recv_until(ws, {"presence"})
            assert len(p["members"]) == 2, p["members"]

        # Maria sends a message
        a.send_json({"type": "message", "text": "Hallo, wie geht es dir?"})

        # Both should receive the raw 'message'
        ma = recv_until(a, {"message"})
        mb = recv_until(b, {"message"})
        assert ma["message"]["text"] == "Hallo, wie geht es dir?"
        assert mb["message"]["text"] == "Hallo, wie geht es dir?"
        print("[ok] both clients received the original message")

        # translation events (fallback = original since no AI backend)
        ta = recv_until(a, {"translation"})
        tb = recv_until(b, {"translation"})
        assert ta["type"] == "translation" and tb["type"] == "translation"
        assert tb["lang"] == "ja" and ta["lang"] == "de"
        print("[ok] translation events pushed per language:", tb["lang"], "/", ta["lang"])

        # typing broadcast
        a.send_json({"type": "typing", "is_typing": True})
        mt = recv_until(b, {"typing"})
        assert mt["is_typing"] is True
        print("[ok] typing indicator broadcast")


def test_fallback_translate():
    import asyncio

    out = asyncio.run(main.translation.translator.translate("Hello world", "French"))
    # No AI backend -> returns original
    assert out == "Hello world", out
    print("[ok] translator fallback returns original when AI unavailable")


if __name__ == "__main__":
    test_languages()
    test_ui()
    test_room_and_ws()
    test_fallback_translate()
    print("\nALL BACKEND SMOKE TESTS PASSED")
