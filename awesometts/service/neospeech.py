# -*- coding: utf-8 -*-
# Copyright (C) 2019 Lovac42
# Copyright (C) 2010-2018 Anki AwesomeTTS Development Team
# Support: https://github.com/lovac42/awesometts-CCBC-addon
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


"""
Service implementation for NeoSpeech's text-to-speech demo engine
"""

import json
from threading import Lock

from .base import Service
from .common import Trait

__all__ = ['NeoSpeech']


VOICES = [
    ("Arabic - male","Arabic - male"),
    ("Arabic - female","Arabic - female"),
    ("Basque - female","Basque - female"),
    ("Catalan - male","Catalan - male"),
    ("Chinese (Cantonese) - male","Chinese (Cantonese) - male"),
    ("Chinese (Cantonese) - female","Chinese (Cantonese) - female"),
    ("Chinese (Mandarin) - male","Chinese (Mandarin) - male"),
    ("Chinese (Mandarin) - female","Chinese (Mandarin) - female"),
    ("Chinese (Mandarin-Taiwan) - female","Chinese (Mandarin-Taiwan) - female"),
    ("Croatian - female","Croatian - female"),
    ("Czech - female","Czech - female"),
    ("Danish - female","Danish - female"),
    ("Dutch - male","Dutch - male"),
    ("Dutch - female","Dutch - female"),
    ("English (American) - male","English (American) - male"),
    ("English (American) - female","English (American) - female"),
    ("English (Australian) - male","English (Australian) - male"),
    ("English (British) - male","English (British) - male"),
    ("English (British) - female","English (British) - female"),
    ("English (Indian) - female","English (Indian) - female"),
    ("English (Scottish) - female","English (Scottish) - female"),
    ("English (South African) - female","English (South African) - female"),
    ("Faroese - male","Faroese - male"),
    ("Faroese - female","Faroese - female"),
    ("Farsi - male","Farsi - male"),
    ("Farsi - female","Farsi - female"),
    ("Finnish - female","Finnish - female"),
    ("Flemish - female","Flemish - female"),
    ("French - male","French - male"),
    ("French - female","French - female"),
    ("French (Belgian) - female","French (Belgian) - female"),
    ("French (Canadian) - male","French (Canadian) - male"),
    ("French (Canadian) - female","French (Canadian) - female"),
    ("Frisian - male","Frisian - male"),
    ("Galician - female","Galician - female"),
    ("German - male","German - male"),
    ("German - female","German - female"),
    ("Greek - female","Greek - female"),
    ("Hebrew - female","Hebrew - female"),
    ("Hindi - female","Hindi - female"),
    ("Hungarian - female","Hungarian - female"),
    ("Icelandic - male","Icelandic - male"),
    ("Indonesian - female","Indonesian - female"),
    ("Italian - male","Italian - male"),
    ("Italian - female","Italian - female"),
    ("Japanese - male","Japanese - male"),
    ("Japanese - female","Japanese - female"),
    ("Korean - male","Korean - male"),
    ("Korean - female","Korean - female"),
    ("Northern Sami - male","Northern Sami - male"),
    ("Northern Sami - female","Northern Sami - female"),
    ("Norwegian (Bokmål) - male","Norwegian (Bokmål) - male"),
    ("Norwegian (Bokmål) - female","Norwegian (Bokmål) - female"),
    ("Polish - male","Polish - male"),
    ("Polish - female","Polish - female"),
    ("Portuguese - male","Portuguese - male"),
    ("Portuguese - female","Portuguese - female"),
    ("Portuguese (Brazilian) - female","Portuguese (Brazilian) - female"),
    ("Romanian - female","Romanian - female"),
    ("Russian - female","Russian - female"),
    ("Slovak - female","Slovak - female"),
    ("Spanish - male","Spanish - male"),
    ("Spanish - female","Spanish - female"),
    ("Spanish (American) - male","Spanish (American) - male"),
    ("Spanish (American) - female","Spanish (American) - female"),
    ("Spanish (Mexican) - male","Spanish (Mexican) - male"),
    ("Spanish (Mexican) - female","Spanish (Mexican) - female"),
    ("Swedish - female","Swedish - female"),
    ("Swedish (Finland) - male","Swedish (Finland) - male"),
    ("Thai - female","Thai - female"),
    ("Turkish - male","Turkish - male"),
    ("Turkish - female","Turkish - female"),
    ("Valencian - female","Valencian - female"),
    ("Welsh - male","Welsh - male"),
    ("Welsh - female","Welsh - female")
]

BASE_URL = 'https://demo.readspeaker.com'

DEMO_URL = BASE_URL + '/proxy.php'

REQUIRE_MP3 = dict(mime='audio/mpeg', size=256)


class NeoSpeech(Service):
    """
    Provides a Service-compliant implementation for NeoSpeech.
    """

    __slots__ = [
        '_lock',         # download URL is tied to cookie; force serial runs
        '_cookies',      # used for all NeoSpeech requests in this Anki session
        '_last_phrase',  # last subtext we sent to NeoSpeech
        '_last_stream',  # last download we got from NeoSpeech
    ]

    NAME = "NeoSpeech"

    TRAITS = [Trait.INTERNET]

    def __init__(self, *args, **kwargs):
        self._lock = Lock()
        self._cookies = None
        self._last_phrase = None
        self._last_stream = None
        super(NeoSpeech, self).__init__(*args, **kwargs)

    def desc(self):
        """Returns name with a voice count."""
        return """NeoSpeech Demo (%d voices)

Note: Please be kind to online services and repect
the wait time limit.
""" % (len(set(map(lambda x: x[0][:5], VOICES))))


    def options(self):
        """Provides access to voice only."""
        return [dict(
                    key='voice',
                    label="Voice",
                    values=VOICES,
                    transform=lambda value: value,
                    default='English (American) - male',
            )]

    def run(self, text, options, path):
        """Requests MP3 URLs and then downloads them."""

        with self._lock:
            def fetch_piece(subtext, subpath):
                """Fetch given phrase from the API to the given path."""

                payload = self.net_stream((DEMO_URL, 
                                            dict(
                                                l="tts-software", 
                                                t=subtext.replace(' ','-'), #get around single word limits
                                                v=options['voice'],
                                                f="mp3"
                                            )),
                                            method='POST',
                                            )

                try:
                    data = json.loads(payload)
                except ValueError:
                    raise ValueError("Unable to interpret the response from "
                                     "the NeoSpeech service")

                try:
                    url = data['links']['mp3']
                except KeyError:
                    raise KeyError("Cannot find the audio URL in the response "
                                   "from the NeoSpeech service")
                assert isinstance(url, str) and len(url) > 2, \
                    "The audio URL from NeoSpeech does not seem to be valid"

                mp3_stream = self.net_stream(url)

                if self._last_phrase != subtext and \
                        self._last_stream == mp3_stream:
                    raise IOError("NeoSpeech seems to be returning the same "
                                  "MP3 file twice in a row; it may be having "
                                  "service problems.")
                self._last_phrase = subtext
                self._last_stream = mp3_stream
                with open(subpath, 'wb') as mp3_file:
                    mp3_file.write(mp3_stream)

            subtexts = self.util_split(text, 200)  # see `maxlength` on site
            if len(subtexts) == 1:
                fetch_piece(subtexts[0], path)
            else:
                intermediate_mp3s = []
                try:
                    for subtext in subtexts:
                        intermediate_mp3 = self.path_temp('mp3')
                        intermediate_mp3s.append(intermediate_mp3)
                        fetch_piece(subtext, intermediate_mp3)
                    self.util_merge(intermediate_mp3s, path)
                finally:
                    self.path_unlink(intermediate_mp3s)
