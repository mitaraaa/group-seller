from fluent.runtime import FluentLocalization, FluentResourceLoader

from database import get_user, session
from keyboards import Language

loader = FluentResourceLoader("locales/{locale}")
en = FluentLocalization(["en"], ["main.ftl"], loader)
ru = FluentLocalization(["ru"], ["main.ftl"], loader)


def set_user_language(user_id: int, language: Language) -> FluentLocalization:
    user = get_user(user_id)

    if not user:
        return en

    with session:
        user.language = language.value

        session.add(user)
        session.commit()

    return en if language.value == "en" else ru


def get_user_language(user_id: int) -> FluentLocalization | None:
    user = get_user(user_id)

    if not user:
        return None

    return en if user.language == "en" else ru
