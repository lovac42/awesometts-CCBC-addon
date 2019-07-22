# -*- coding: utf-8 -*-
# Copyright (C) 2019 Lovac42
# Copyright (C) 2010-2018 Anki AwesomeTTS Development Team
# Support: https://github.com/lovac42/awesometts-CCBC-addon
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


"""
Service implementation for TextAloud's text-to-speech
"""

import json
from .base import Service
from .common import Trait

__all__ = ['TextAloud']


VOICES = [
    ('cy-GB', 'female', 'Gwyneth'),
    ('da-DK', 'female', 'Naja'),
    ('da-DK', 'male', 'Mads'),
    ('de-DE', 'female', 'Vicki'),
    ('de-DE', 'female', 'Marlene'),
    ('de-DE', 'male', 'Hans'),
    ('en-AU', 'female', 'Nicole'),
    ('en-AU', 'male', 'Russell'),
    ('en-GB', 'female', 'Emma'),
    ('en-GB', 'female', 'Amy'),
    ('en-GB', 'male', 'Brian'),
    ('en-GB-WLS', 'male', 'Geraint'),
    ('en-IN', 'female', 'Aditi'),
    ('en-IN', 'female', 'Raveena'),
    ('en-US', 'female', 'Ivy'),
    ('en-US', 'female', 'Joanna'),
    ('en-US', 'female', 'Kendra'),
    ('en-US', 'female', 'Kimberly'),
    ('en-US', 'female', 'Salli'),
    ('en-US', 'male', 'Joey'),
    ('en-US', 'male', 'Justin'),
    ('en-US', 'male', 'Matthew'),
    ('es-ES', 'female', 'Conchita'),
    ('es-ES', 'male', 'Enrique'),
    ('es-US', 'female', 'Penelope'),
    ('es-US', 'male', 'Miguel'),
    ('fr-FR', 'female', 'Celine'),
    ('fr-FR', 'male', 'Mathieu'),
    ('fr-CA', 'female', 'Chantal'),
    ('is-IS', 'female', 'Dora'),
    ('is-IS', 'male', 'Karl'),
    ('it-IT', 'female', 'Carla'),
    ('it-IT', 'male', 'Giorgio'),
    ('ja-JP', 'female', 'Mizuki'),
    ('ja-JP', 'male', 'Takumi'),
    ('ko-KR', 'female', 'Seoyeon'),
    ('nb-NO', 'female', 'Liv'),
    ('nl-NL', 'female', 'Lotte'),
    ('nl-NL', 'male', 'Ruben'),
    ('pl-PL', 'female', 'Ewa'),
    ('pl-PL', 'female', 'Maja'),
    ('pl-PL', 'male', 'Jacek'),
    ('pl-PL', 'male', 'Jan'),
    ('pt-BR', 'female', 'Vitoria'),
    ('pt-BR', 'male', 'Ricardo'),
    ('pt-PT', 'female', 'Ines'),
    ('pt-PT', 'male', 'Cristiano'),
    ('ro-RO', 'female', 'Carmen'),
    ('ru-RU', 'female', 'Tatyana'),
    ('ru-RU', 'male',   'Maxim'),
    ('sv-SE', 'female', 'Astrid'),
    ('tr-TR', 'female', 'Filiz')
]

BASE_URL = 'https://www.textaloud.com'

REFERER=BASE_URL + "/index.shtml"

GET_URL = BASE_URL + '/php/nextup-polly/CreateSpeech/CreateSpeechGet3.php'


class TextAloud(Service):
    """
    Provides a Service-compliant implementation for TextAloud.
    """

    __slots__ = []

    NAME = "TextAloud TTS (Polly)"

    TRAITS = [Trait.INTERNET]

    def desc(self):
        """Returns name with a voice count."""
        return "TextAloud NextUp Polly (%d voices)" % len(VOICES)

    def options(self):
        """Provides access to voice only."""
        voice_lookup = {self.normalize(name): name
                        for language, gender, name in VOICES}

        def transform_voice(value):
            """Fixes whitespace and casing errors only."""
            normal = self.normalize(value)
            return voice_lookup[normal] if normal in voice_lookup else value

        return [dict(key='voice',
                    label="Voice",
                    values=[(name, "%s (%s %s)" % (name, gender, language))
                            for language, gender, name in VOICES],
                    transform=transform_voice,
                    default='Salli',
                )]


    def run(self, text, options, path):
        """Requests MP3 URLs and then downloads them."""

        language="en-US"
        for lang,gen,name in VOICES: #TODO: rewrite to use maps
            if name==options['voice']:
                language=lang
                break;

        url=self.net_stream((GET_URL, dict(
                    voice=options['voice'],
                    language=language,
                    text=text
                    )),
                    method='GET',
                    custom_headers={
                        'Referer':REFERER,
                        'Content-type': 'text/html',
                    }
                )

        self.net_download(
                    path, (url.decode(), dict()),
                    custom_headers={
                        'Referer':REFERER,
                        'Content-type': 'audio/mpeg',
                    },
                    # require=dict(mime='audio/mpeg', size=1024),
        )
