"""Runtime configuration for the LinguaRoom backend."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# How many messages to keep per room in memory / on disk.
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "200"))

# Max concurrent translation requests (respects DeepSeek free rate limits).
TRANSLATE_CONCURRENCY = int(os.getenv("TRANSLATE_CONCURRENCY", "4"))

# Hard timeout (seconds) for a single translation call.
TRANSLATE_TIMEOUT = float(os.getenv("TRANSLATE_TIMEOUT", "45"))

# Size of the in-memory translation cache.
TRANSLATE_CACHE_SIZE = int(os.getenv("TRANSLATE_CACHE_SIZE", "2000"))

# Optional DeepSeek web auth token for the `dsk` backend.
# Leave empty to use the token-less legacy deepseek4free backend.
DEEPSEEK_TOKEN = os.getenv("DEEPSEEK_TOKEN", "")

# Master switch for AI translation. Set to "0" to disable (chat still works,
# everyone just sees the original text).
USE_DEEPSEEK = os.getenv("USE_DEEPSEEK", "1") != "0"
