from app.main import crud, models
from fastapi import Request
from contextvars import ContextVar
import logging

from app.main.core.config import Config
from .languages import langs

language = ContextVar("lang", default=Config.PREFERRED_LANGUAGE)


async def add_process_language_header(request: Request, call_next):
    accepted_languages = langs.keys()
    lang = Config.PREFERRED_LANGUAGE
    if "lang" in request.headers and request.headers["lang"]:
        if request.headers["lang"] in accepted_languages:
            lang = request.headers["lang"]
    if "Accept-Language" in request.headers and request.headers["Accept-Language"]:
        user_browser_languages = request.headers["Accept-Language"].split(",")
        for user_browser_language in user_browser_languages:
            user_browser_language = user_browser_language.split(";")[0].split("-")[0].lower()
            if user_browser_language in accepted_languages:
                lang = user_browser_language
                break

    language.set(lang)
    response = await call_next(request)
    return response


def get_language():
    try:
        return language.get()
    except Exception as e:
        logging.info(f"Failed get user language for language ContextVar: {e}")
        return Config.PREFERRED_LANGUAGE


def __(key: str, locale: str = None):
    try:
        lang = locale or str(get_language())

    except Exception as e:
        logging.info(f"Failed get user language: {e}")
        lang = Config.PREFERRED_LANGUAGE

    try:

        if key in langs[lang]:
            text = langs[lang][key]
        else:
            text = key
        return text

    except Exception as e:
        logging.info(f"Failed translate message: {e}")
        return key
