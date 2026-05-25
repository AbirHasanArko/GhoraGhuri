"""
GhoraGhuri — Internationalization (i18n) Utility
Loads locale files and provides translation helper.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_locales: dict[str, dict[str, str]] = {}

LOCALES_DIR = Path(__file__).parent.parent.parent / "locales"


def load_locales() -> None:
    """Load all locale JSON files at startup."""
    global _locales

    for lang_file in LOCALES_DIR.glob("*.json"):
        lang_code = lang_file.stem  # 'en', 'bn'
        try:
            with open(lang_file, encoding="utf-8") as f:
                _locales[lang_code] = json.load(f)
            logger.info(f"Loaded locale: {lang_code} ({len(_locales[lang_code])} keys)")
        except Exception as e:
            logger.error(f"Failed to load locale {lang_code}: {e}")


def t(key: str, lang: str = "en", **kwargs: Any) -> str:
    """
    Translate a key to the specified language.

    Args:
        key: Translation key (e.g., 'otp_sent')
        lang: Language code ('en' or 'bn')
        **kwargs: Substitution variables (e.g., amount=2)

    Returns:
        Translated string with variables substituted
    """
    if lang not in _locales:
        lang = "en"

    text = _locales.get(lang, {}).get(key, key)

    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass

    return text


def get_bilingual(key: str, **kwargs: Any) -> tuple[str, str]:
    """Get both English and Bangla translations."""
    return t(key, "en", **kwargs), t(key, "bn", **kwargs)
