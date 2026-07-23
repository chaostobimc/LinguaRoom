"""Supported languages for the language picker.

`code`  -> stable identifier passed around the app
`en`    -> English name (used as the translation target hint for the AI)
`native`-> native name (shown in the picker)
`flag`  -> emoji flag (purely decorative)
"""

LANGUAGES = [
    {"code": "en", "en": "English", "native": "English", "flag": "🇬🇧"},
    {"code": "de", "en": "German", "native": "Deutsch", "flag": "🇩🇪"},
    {"code": "es", "en": "Spanish", "native": "Español", "flag": "🇪🇸"},
    {"code": "fr", "en": "French", "native": "Français", "flag": "🇫🇷"},
    {"code": "pt", "en": "Portuguese", "native": "Português", "flag": "🇵🇹"},
    {"code": "it", "en": "Italian", "native": "Italiano", "flag": "🇮🇹"},
    {"code": "nl", "en": "Dutch", "native": "Nederlands", "flag": "🇳🇱"},
    {"code": "ru", "en": "Russian", "native": "Русский", "flag": "🇷🇺"},
    {"code": "uk", "en": "Ukrainian", "native": "Українська", "flag": "🇺🇦"},
    {"code": "pl", "en": "Polish", "native": "Polski", "flag": "🇵🇱"},
    {"code": "cs", "en": "Czech", "native": "Čeština", "flag": "🇨🇿"},
    {"code": "sv", "en": "Swedish", "native": "Svenska", "flag": "🇸🇪"},
    {"code": "no", "en": "Norwegian", "native": "Norsk", "flag": "🇳🇴"},
    {"code": "da", "en": "Danish", "native": "Dansk", "flag": "🇩🇰"},
    {"code": "fi", "en": "Finnish", "native": "Suomi", "flag": "🇫🇮"},
    {"code": "tr", "en": "Turkish", "native": "Türkçe", "flag": "🇹🇷"},
    {"code": "el", "en": "Greek", "native": "Ελληνικά", "flag": "🇬🇷"},
    {"code": "ro", "en": "Romanian", "native": "Română", "flag": "🇷🇴"},
    {"code": "hu", "en": "Hungarian", "native": "Magyar", "flag": "🇭🇺"},
    {"code": "ar", "en": "Arabic", "native": "العربية", "flag": "🇸🇦"},
    {"code": "fa", "en": "Persian", "native": "فارسی", "flag": "🇮🇷"},
    {"code": "he", "en": "Hebrew", "native": "עברית", "flag": "🇮🇱"},
    {"code": "hi", "en": "Hindi", "native": "हिन्दी", "flag": "🇮🇳"},
    {"code": "ur", "en": "Urdu", "native": "اردو", "flag": "🇵🇰"},
    {"code": "bn", "en": "Bengali", "native": "বাংলা", "flag": "🇧🇩"},
    {"code": "ta", "en": "Tamil", "native": "தமிழ்", "flag": "🇮🇳"},
    {"code": "te", "en": "Telugu", "native": "తెలుగు", "flag": "🇮🇳"},
    {"code": "th", "en": "Thai", "native": "ไทย", "flag": "🇹🇭"},
    {"code": "vi", "en": "Vietnamese", "native": "Tiếng Việt", "flag": "🇻🇳"},
    {"code": "id", "en": "Indonesian", "native": "Bahasa Indonesia", "flag": "🇮🇩"},
    {"code": "ms", "en": "Malay", "native": "Bahasa Melayu", "flag": "🇲🇾"},
    {"code": "tl", "en": "Filipino", "native": "Filipino", "flag": "🇵🇭"},
    {"code": "zh", "en": "Chinese (Simplified)", "native": "中文（简体）", "flag": "🇨🇳"},
    {"code": "zh-TW", "en": "Chinese (Traditional)", "native": "中文（繁體）", "flag": "🇹🇼"},
    {"code": "ja", "en": "Japanese", "native": "日本語", "flag": "🇯🇵"},
    {"code": "ko", "en": "Korean", "native": "한국어", "flag": "🇰🇷"},
    {"code": "ne", "en": "Nepali", "native": "नेपाली", "flag": "🇳🇵"},
    {"code": "si", "en": "Sinhala", "native": "සිංහල", "flag": "🇱🇰"},
    {"code": "sw", "en": "Swahili", "native": "Kiswahili", "flag": "🇹🇿"},
    {"code": "am", "en": "Amharic", "native": "አማርኛ", "flag": "🇪🇹"},
    {"code": "yo", "en": "Yoruba", "native": "Yorùbá", "flag": "🇳🇬"},
    {"code": "ig", "en": "Igbo", "native": "Igbo", "flag": "🇳🇬"},
    {"code": "af", "en": "Afrikaans", "native": "Afrikaans", "flag": "🇿🇦"},
    {"code": "is", "en": "Icelandic", "native": "Íslenska", "flag": "🇮🇸"},
    {"code": "ga", "en": "Irish", "native": "Gaeilge", "flag": "🇮🇪"},
    {"code": "ca", "en": "Catalan", "native": "Català", "flag": "🇪🇸"},
    {"code": "eu", "en": "Basque", "native": "Euskara", "flag": "🇪🇸"},
    {"code": "hr", "en": "Croatian", "native": "Hrvatski", "flag": "🇭🇷"},
    {"code": "sr", "en": "Serbian", "native": "Српски", "flag": "🇷🇸"},
    {"code": "sk", "en": "Slovak", "native": "Slovenčina", "flag": "🇸🇰"},
    {"code": "sl", "en": "Slovenian", "native": "Slovenščina", "flag": "🇸🇮"},
    {"code": "bg", "en": "Bulgarian", "native": "Български", "flag": "🇧🇬"},
    {"code": "et", "en": "Estonian", "native": "Eesti", "flag": "🇪🇪"},
    {"code": "lv", "en": "Latvian", "native": "Latviešu", "flag": "🇱🇻"},
    {"code": "lt", "en": "Lithuanian", "native": "Lietuvių", "flag": "🇱🇹"},
    {"code": "sq", "en": "Albanian", "native": "Shqip", "flag": "🇦🇱"},
    {"code": "mk", "en": "Macedonian", "native": "Македонски", "flag": "🇲🇰"},
    {"code": "ka", "en": "Georgian", "native": "ქართული", "flag": "🇬🇪"},
    {"code": "hy", "en": "Armenian", "native": "Հայերեն", "flag": "🇦🇲"},
    {"code": "az", "en": "Azerbaijani", "native": "Azərbaycan", "flag": "🇦🇿"},
    {"code": "kk", "en": "Kazakh", "native": "Қазақша", "flag": "🇰🇿"},
    {"code": "uz", "en": "Uzbek", "native": "Oʻzbek", "flag": "🇺🇿"},
    {"code": "mn", "en": "Mongolian", "native": "Монгол", "flag": "🇲🇳"},
    {"code": "my", "en": "Burmese", "native": "မြန်မာ", "flag": "🇲🇲"},
    {"code": "km", "en": "Khmer", "native": "ខ្មែរ", "flag": "🇰🇭"},
    {"code": "lo", "en": "Lao", "native": "ລາວ", "flag": "🇱ງ"},
    {"code": "haw", "en": "Hawaiian", "native": "ʻŌlelo Hawaiʻi", "flag": "🇺🇸"},
    {"code": "cy", "en": "Welsh", "native": "Cymraeg", "flag": "🇬🇧"},
    {"code": "gl", "en": "Galician", "native": "Galego", "flag": "🇪🇸"},
    {"code": "eo", "en": "Esperanto", "native": "Esperanto", "flag": "🌍"},
    {"code": "la", "en": "Latin", "native": "Latina", "flag": "🏛️"},
]

_LANG_BY_CODE = {l["code"]: l for l in LANGUAGES}


def get_language(code: str) -> dict:
    return _LANG_BY_CODE.get(code, _LANG_BY_CODE["en"])


def language_name(code: str) -> str:
    """English name used as the target-language hint for the AI."""
    return get_language(code)["en"]
