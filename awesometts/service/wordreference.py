# -*- coding: utf-8 -*-
# Copyright (C) 2019-2020 Lovac42
# Copyright (C) 2010-2018 Anki AwesomeTTS Development Team
# Support: https://github.com/lovac42/awesometts-CCBC-addon
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


"""
Service implementation for WordReference
"""

import json
import time
import requests

from .base import Service
from .common import Trait

__all__ = ['WordReference']


VOICES = [
    # UNIQUE_NAME, LANG, ACCENT, SEARCH_URL, VOICE_INDEX
    ('ENG_US', 'English', 'US', 'definition', 0),
    ('ENG_UK', 'English', 'UK', 'definition', 1),
    ('ENG_UKRP', 'English', 'UK-RP', 'definition', 2),
    ('ENG_UKY', 'English', 'UK-Yorkshire', 'definition', 3),
    ('ENG_IR', 'English', 'Irish', 'definition', 4),
    ('ENG_SCOT', 'English', 'Scottish', 'definition', 5),
    ('ENG_USS', 'English', 'US Southern', 'definition', 6),
    ('ENG_JAM', 'English', 'Jamaican', 'definition', 7),
    ('FR_FR', 'French', 'France', 'fren', 0),
    ('FR_CA', 'French', 'Canada', 'fren', 1),
    ('SP_MX', 'Spanish', 'Mexico', 'definicion', 0),
    ('SP_ES', 'Spanish', 'Espana', 'definicion', 1),
    ('SP_AG', 'Spanish', 'Argentia', 'definicion', 2),
    ('IT_IT', 'Italian', 'Italian', 'definizione', 0),
]

BASE_URL = "https://www.wor" + "dreference.com"

REFERER = BASE_URL + "/"




from html.parser import HTMLParser

class HTML_Lister(HTMLParser):
    """Accumulate all found MP3s into `sounds` member."""

    # set self.accent

    def reset(self):
        HTMLParser.reset(self)
        self.sounds = []
        self.prev_tag = ""

    def handle_starttag(self, tag, attrs):
        if tag == "source" and self.prev_tag == "audio":
            snd = [v for k, v in attrs if k == "src"]
            if snd:
                self.sounds.extend(snd)
                self.prev_tag = ""

        if tag == "audio":
            for k,v in attrs:
                if k=='id' and v==self.accent:
                    self.prev_tag = tag





class WordReference(Service):

    """
    Provides a Service-compliant implementation for WordReference.
    """

    __slots__ = []

    NAME = "WordReference"

    TRAITS = [Trait.INTERNET]

    def desc(self):
        """Returns name with a voice count."""
        return """WordReference (%d voices)

Note: Please be kind to online services and repect
the wait time limit.
""" % len(VOICES)


    def options(self):
        """Provides access to voice only."""
        return [dict(key='voice',
                    label="Voice",
                    values=[(name, "%s (%s)"%(language,accent))
                            for name, language, accent, a, b in VOICES],
                    transform=lambda value: value,
                    default='ENG_US',
                )]


    def run(self, text, options, path):
        """Requests MP3 URLs and then downloads them."""

        text = text.strip()
        if " " in text:
            raise IOError("Invalid text for WordReference.")

        if len(text) > 50:
            raise IOError("Input text is too long for WordReference.")

        url_path = aud_idx = ""
        for name,l,a,u,i in VOICES: #TODO: rewrite to use maps
            if name==options['voice']:
                url_path = u
                aud_idx = i
                break;
        else:
            return

        self._netops += 1

        search_url = "%s/%s/%s"%(BASE_URL,url_path,text)

        r = requests.get(
            search_url,
            headers={
                'Referer': REFERER,
            },
            timeout=20,
        )
        r.raise_for_status()

        parser = HTML_Lister()
        parser.accent = "aud%d"%aud_idx
        parser.feed(r.text)
        parser.close()

        if len(parser.sounds) > 0:
            sound_url = BASE_URL + parser.sounds[0]

            self.net_download(
                path, sound_url,
                custom_headers={
                    'Referer': search_url,
                    'Content-type': 'audio/mpeg',
                },
                # require=dict(mime='audio/mpeg', size=1024),
            )

        time.sleep(0.2)
