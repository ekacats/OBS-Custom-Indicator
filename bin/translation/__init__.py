#! /usr/bin/python -I -S
"""The localization module provides regional language support."""


from gettext import find, install, translation
from logging import basicConfig, getLogger, DEBUG
from pathlib import Path


# ==============================
DOMAIN = 'messages'


# ==============================
def languages() -> tuple:
    return (
        [_('Indonesian'), 'id-ID'],
        [_('German'), 'de-DE'],
        [_('English'), 'en-US'],
        [_('Spanish'), 'es-ES'],
        [_('French'), 'fr-FR'],
        [_('Italian'), 'it-IT'],
        [_('Portuguese'), 'pt-BR'],
        [_('Turkish'), 'tr-TR'],
        [_('Russian'), 'ru-RU'],
        [_('Japanese'), 'ja-JP'],
        [_('Simplified Chinese'), 'zh-CN'],
        [_('Traditional Chinese'), 'zh-TW'],
        [_('Korean'), 'ko-KR'],
    )


# ==============================
def install_language(language='en-US'):
    """Changing languages on the fly.

        Args:
            language: Tag for language and region.
    """
    _logger = getLogger(__name__)
    _localedir = Path(__file__).parent.joinpath('locale')

    if find(DOMAIN, _localedir, [language]):
        _logger.debug(f'Installed language: {language}')
    elif language:
        _logger.debug(f'Translation file not found: {language}')
        language = 'en-US'
    else:
        _logger.debug(f'Language is not specified.')
        language = 'en-US'

    _translation = translation(
        DOMAIN,
        localedir=_localedir,
        languages=[language],
        fallback=True,
    )
    _translation.install()


# ==============================
if __name__ == '__main__':
    basicConfig(
        level=DEBUG,
        format='{levelname:<8}: <{name}, line {lineno}>  {message}',
        style='{',
    )
    install_language()
