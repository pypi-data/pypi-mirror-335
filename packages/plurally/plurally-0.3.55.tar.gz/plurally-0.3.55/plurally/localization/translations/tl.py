import gettext
import os
from pathlib import Path

from loguru import logger

locale_dir = Path(__file__).parent
domain = "merged"

TRANSLATORS = {}


def get_translator(locale):
    logger.info(f"Loading {locale} translator")
    translator = gettext.translation(domain, localedir=locale_dir, languages=[locale])
    translator.install()
    return translator


def _(key, locale=None):
    if not locale:
        locale = os.getenv("LOCALE", "fr")
    locale = locale.partition("_")[0]

    global TRANSLATORS
    if locale not in TRANSLATORS:
        TRANSLATORS[locale] = get_translator(locale)
    return TRANSLATORS[locale].gettext(key)
