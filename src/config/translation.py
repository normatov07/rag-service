from django.core.cache import cache
from django.utils.translation import get_language
from rest_framework.exceptions import APIException

from apps.references.models.translations import Translation
from config.settings import CACHE_TIMEOUT


def t(key: str, lang: str = None, **params) -> str:
    lang = lang or get_language()
    cache_key = f"i18n:{lang}:{key}"

    text = cache.get(cache_key)

    if text is None:
        try:
            obj = Translation.objects.filter(key=key).first()
            if obj:
                text = obj.safe_translation_getter(
                    "name",
                    language_code=lang,
                    any_language=True
                )
            else:
                obj = Translation.objects.create(
                    key = key
                )
                text = obj.key
        except Exception as e:
            raise APIException(str(e))

        cache.set(cache_key, text, CACHE_TIMEOUT)

    try:
        return text % params if params else text
    except KeyError:
        return text
