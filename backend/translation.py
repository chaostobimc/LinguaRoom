"""AI translation service built on top of the deepseek4free project.

We use the unofficial, free DeepSeek client from the deepseek4free repo:
    https://github.com/xtekky/deepseek4free   (the ``dsk`` package)

This is NOT the official/paid DeepSeek API. The ``dsk`` client talks to
chat.deepseek.com's free web endpoint and requires a free DeepSeek web-account
token (``DEEPSEEK_TOKEN``). See README.md for setup.

Design goals matching the brief:
  * FAST        -> response cache keyed by (text, target_language) plus a
                   bounded concurrency semaphore so we never hammer the free
                   endpoint.
  * Only translate -> strict system prompt; no answering, no commentary.
  * Questions stay questions -> explicit prompt rule.
  * Names / URLs / code preserved -> placeholders protect them before the
                   model sees the text and are restored afterwards.

If the ``dsk`` backend (or its token) is unavailable, the service degrades
gracefully: ``translate`` returns the original text so the chat keeps working.
"""
import asyncio
import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, Optional

import config

logger = logging.getLogger("linguaroom.translation")

# Things we must never translate: URLs, emails, @mentions, #hashtags,
# `inline code` and [markdown](links).
PROTECT_RE = re.compile(
    r"(https?://[^\s]+|www\.[^\s]+|"
    r"[\w.+-]+@[\w-]+\.[\w.-]+|"
    r"#\w+|@[\w\u00C0-\uFFFF]+|"
    r"`[^`]*`|\[[^\]]+\]\([^)]+\))"
)

# Private-use sentinels wrapping a protected snippet.
_OPEN = ""
_CLOSE = ""


def extract_json(text: Optional[str]) -> Optional[dict]:
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except Exception:
        return None


class Translator:
    def __init__(self) -> None:
        self._client = None
        self._kind: Optional[str] = None
        self._session_id: Optional[str] = None
        self._sema = asyncio.Semaphore(config.TRANSLATE_CONCURRENCY)
        self._cache: Dict[tuple, str] = {}
        self._init_client()

    # ------------------------------------------------------------------ #
    # Backend initialisation (uses the deepseek4free ``dsk`` package)
    # ------------------------------------------------------------------ #
    def _init_client(self) -> None:
        if not config.USE_DEEPSEEK:
            logger.warning("AI translation disabled via USE_DEEPSEEK=0")
            return

        # Allow dropping the repo's `dsk/` folder into backend/vendor/dsk.
        vendor = Path(__file__).resolve().parent / "vendor" / "dsk"
        if vendor.exists():
            sys.path.insert(0, str(vendor.parent))

        try:
            from dsk.api import DeepSeekAPI  # type: ignore
        except Exception as exc:  # pragma: no cover - depends on env
            logger.warning(
                "deepseek4free `dsk` package not found (%s). "
                "Translation disabled — chat still works. See README to enable.",
                exc,
            )
            return

        if not config.DEEPSEEK_TOKEN:
            logger.warning(
                "DEEPSEEK_TOKEN is not set. Get a free DeepSeek web token "
                "(see README) and restart to enable AI translation."
            )
            return

        try:
            self._client = DeepSeekAPI(config.DEEPSEEK_TOKEN)
            self._kind = "dsk"
            logger.info("Translation backend: deepseek4free (dsk) ready")
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to init DeepSeekAPI: %s", exc)

    @property
    def available(self) -> bool:
        return self._client is not None

    # ------------------------------------------------------------------ #
    # Prompt construction
    # ------------------------------------------------------------------ #
    def _protect(self, text: str, store: list):
        def repl(m):
            store.append(m.group(0))
            return f"{_OPEN}{len(store) - 1}{_CLOSE}"

        return PROTECT_RE.sub(repl, text)

    def _restore(self, text: str, store: list) -> str:
        def repl(m):
            idx = int(m.group(1))
            return store[idx] if 0 <= idx < len(store) else m.group(0)

        return re.sub(rf"{_OPEN}(\d+){_CLOSE}", repl, text)

    @staticmethod
    def _prompt(masked_text: str, target_lang: str) -> str:
        return (
            "You are a strict translation engine. Translate the user's text "
            f"into {target_lang}.\n\n"
            "HARD RULES:\n"
            "1. Translate ONLY. Do not answer, explain, greet, or add any extra text.\n"
            "2. If the input is a question, the output MUST also be a question in "
            f"{target_lang}. Never answer the question.\n"
            "3. Do NOT translate names, people, places, brands, URLs, links, email "
            "addresses, @mentions, #hashtags, code, or commands. Keep them exactly "
            "as written. They appear wrapped in special markers N -- leave those "
            "markers and their contents untouched.\n"
            "4. Preserve emojis, line breaks, formatting and tone.\n"
            "5. Output exactly the translated text and nothing else. No quotes, no "
            "prefixes, no commentary.\n\n"
            f"Text to translate:\n{masked_text}"
        )

    # ------------------------------------------------------------------ #
    # Low level model call (synchronous, runs in a worker thread)
    # ------------------------------------------------------------------ #
    def _ensure_session(self) -> str:
        if self._session_id is None:
            self._session_id = self._client.create_chat_session()
        return self._session_id

    def _call_model(self, prompt: str) -> Optional[str]:
        if self._client is None:
            return None
        try:
            chat_id = self._ensure_session()
            parts = []
            for chunk in self._client.chat_completion(
                chat_id, prompt, thinking_enabled=False, search_enabled=False
            ):
                if isinstance(chunk, dict) and chunk.get("type") == "text":
                    parts.append(chunk.get("content", ""))
            return "".join(parts)
        except Exception as exc:  # pragma: no cover
            # Session may have expired -- drop it and retry once.
            self._session_id = None
            logger.error("Model call failed: %s", exc)
            return None

    @staticmethod
    def _clean(raw: Optional[str]) -> Optional[str]:
        if not raw:
            return None
        text = raw.strip()
        # Strip a single layer of wrapping quotes if the whole output is quoted.
        if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
            text = text[1:-1].strip()
        # Drop a stray "Translation:" / "German:" style prefix.
        m = re.match(r"^(translation|target|result)\s*[:\-]\s*", text, re.I)
        if m:
            text = text[m.end():].strip()
        return text or None

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def _do(self, text: str, target_lang: str) -> Optional[str]:
        store: list = []
        masked = self._protect(text, store)
        raw = self._call_model(self._prompt(masked, target_lang))
        cleaned = self._clean(raw)
        if cleaned is None:
            return None
        return self._restore(cleaned, store).strip()

    async def _raw_async(self, prompt: str) -> Optional[str]:
        async with self._sema:
            try:
                return await asyncio.wait_for(
                    asyncio.to_thread(self._call_model, prompt),
                    timeout=config.TRANSLATE_TIMEOUT,
                )
            except Exception as exc:  # pragma: no cover
                logger.error("Raw call error: %s", exc)
                return None

    async def translate(self, text: str, target_lang: str) -> str:
        """Translate ``text`` into ``target_lang`` (English name).

        Returns the original text unchanged if translation is unavailable or
        results in an empty string -- the chat never breaks.
        """
        if not text or not text.strip():
            return text
        if target_lang in ("en", "English", "auto"):
            return text
        key = (text.strip(), target_lang)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        async with self._sema:
            try:
                result = await asyncio.wait_for(
                    asyncio.to_thread(self._do, text.strip(), target_lang),
                    timeout=config.TRANSLATE_TIMEOUT,
                )
            except Exception as exc:  # pragma: no cover
                logger.error("Translate error: %s", exc)
                result = None

        if not result:
            # Cache the failure so we don't retry the same doomed text.
            self._cache[key] = text
            return text
        if len(self._cache) > config.TRANSLATE_CACHE_SIZE:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = result
        return result

    async def translate_json(self, source: Dict[str, str], target_lang: str) -> Dict[str, str]:
        """Translate a dict of UI labels into ``target_lang`` as one JSON blob."""
        if not self.available or not target_lang:
            return dict(source)
        lines = "\n".join(f"{k} = {v}" for k, v in source.items())
        prompt = (
            f"Translate the UI labels on the right of '=' into {target_lang}. "
            "Return ONLY a minified JSON object whose keys are identical to the "
            "left-hand identifiers and whose values are the translations. "
            "Do not translate the brand name 'LinguaRoom'. Keep punctuation.\n"
            + lines
        )
        raw = await self._raw_async(prompt)
        parsed = extract_json(raw)
        if parsed:
            return {k: parsed.get(k, v) for k, v in source.items()}
        return dict(source)


# Module level singleton.
translator = Translator()
