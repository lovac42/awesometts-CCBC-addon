# -*- coding: utf-8 -*-
# Copyright (C) 2019 Lovac42
# Copyright (C) 2019 Nickolay <kelciour@gmail.com>
# Copyright (C) 2010-2018 Anki AwesomeTTS Development Team
# Support: https://github.com/lovac42/awesometts-CCBC-addon
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


"""
Service implementation for Merriam-Webster API
"""

import re
import time
import base64
import requests
import string

from .base import Service
from .common import Trait

__all__ = ['Webster']

SERIAL_NUM = "My00N2I2 a9c"

VOICES = [
    ('default', 'default', 'default')
]


class Webster(Service):
    """
    Provides a Service-compliant implementation for Google Cloud Text-to-Speech.
    """

    __slots__ = []

    NAME = "Merriam-Webster"

    TRAITS = [Trait.INTERNET]


    def desc(self):
        """Returns name with a voice count."""
        return """Merriam-Webster (English only)

Note: Please be kind to online services and repect
the wait time limit.
"""

    def extras(self):
        """The requires an API key."""
        return [dict(key='key', label="API Key", required=False)]

    def options(self):
        return [
            dict(
                key='voice',
                label="Voice",
                values=[
                    ('en', "English (en)"),
                ],
                transform=lambda value: (
                    'en' if self.normalize(value).startswith('en')
                    else value
                ),
                default='en',
            ),
        ]

    def run(self, text, options, path):

        if len(text) > 80:
            raise IOError("Input text is too long for the Webster.")

        k = options['key'] or self.getSampleKey(SERIAL_NUM, text) + '1'
        url="https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}"
        r = requests.get(url.format(text,k), timeout=30)
        r.raise_for_status()
        data = r.json()

        sounds = []
        pronunciations = []
        for d in data:
            try:
                hdw = d["meta"]["id"]
                hdw = re.sub(r':\d+$', '', hdw)
            except:
                continue #no word found

            if hdw.lower() != text.lower():
                continue

            if "prs" not in d["hwi"]:
                continue

            prs = d["hwi"]["prs"]
            for p in prs:
                if p["mw"] not in pronunciations:
                    pronunciations.append(p["mw"])

            for p in prs:
                subdirectory  = ""
                if "sound" not in p:
                    continue
                audio = p["sound"]["audio"]
                if audio.startswith("bix"):
                    subdirectory = "bix"
                elif audio.startswith("gg"):
                    subdirectory = "gg"
                elif audio[0].isdigit() or audio[0] in string.punctuation:
                    subdirectory = "number"
                else:
                    subdirectory = audio[0]
                url = f"https://media.merriam-webster.com/soundc11/{subdirectory}/{audio}.wav"
                # print(url)
                if url not in sounds:
                    sounds.append(url)

        for url in sounds:
            self.net_download(path,url)

        if options['key']:
            self.net_reset()
        time.sleep(0.2)


    def getSampleKey(self, serial, text):
        time.sleep(0.8)
        k = ("OGRiZmI5Y2QtOWU0%s6-80153a63a28"%serial).split()
        return "-".join((base64.b64decode(k[0]).decode(),k[1]))
