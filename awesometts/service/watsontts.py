# -*- coding: utf-8 -*-
# Copyright (C) 2019 Lovac42
# Copyright (C) 2010-2018 Anki AwesomeTTS Development Team
# Support: https://github.com/lovac42/AddonManager21
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

"""
Service implementation for Watson Text-to-Speech API
"""

import base64
import requests

from .base import Service
from .common import Trait

__all__ = ['WatsonTTS']

VOICES = [
    ("en-US_AllisonVoice","American English (en-US): Allison (female, expressive)"),
    ("en-US_AllisonV3Voice","American English (en-US): AllisonV3 (female, ednn)"),
    ("en-US_LisaVoice","American English (en-US): Lisa (female)"),
    ("en-US_LisaV3Voice","American English (en-US): LisaV3 (female, ednn)"),
    ("en-US_MichaelVoice","American English (en-US): Michael (male)"),
    ("en-US_MichaelV3Voice","American English (en-US): MichaelV3 (male, ednn)"),
    ("pt-BR_IsabelaVoice","Brazilian Portuguese (pt-BR): Isabela (female)"),
    ("pt-BR_IsabelaV3Voice","Brazilian Portuguese (pt-BR): IsabelaV3 (female, ednn)"),
    ("en-GB_KateVoice","British English (en-GB): Kate (female)"),
    ("en-GB_KateV3Voice","British English (en-GB): KateV3 (female, ednn)"),
    ("es-ES_EnriqueVoice","Castilian Spanish (es-ES): Enrique (male)"),
    ("es-ES_EnriqueV3Voice","Castilian Spanish (es-ES): EnriqueV3 (male, ednn)"),
    ("es-ES_LauraVoice","Castilian Spanish (es-ES): Laura (female)"),
    ("es-ES_LauraV3Voice","Castilian Spanish (es-ES): LauraV3 (female, ednn)"),
    ("fr-FR_ReneeVoice","French (fr-FR): Renee (female)"),
    ("fr-FR_ReneeV3Voice","French (fr-FR): ReneeV3 (female, ednn)"),
    ("de-DE_BirgitVoice","German (de-DE): Birgit (female)"),
    ("de-DE_BirgitV3Voice","German (de-DE): BirgitV3 (female, ednn)"),
    ("de-DE_DieterVoice","German (de-DE): Dieter (male)"),
    ("de-DE_DieterV3Voice","German (de-DE): DieterV3 (male, ednn)"),
    ("it-IT_FrancescaVoice","Italian (it-IT): Francesca (female)"),
    ("it-IT_FrancescaV3Voice","Italian (it-IT): FrancescaV3 (female, ednn)"),
    ("ja-JP_EmiVoice","Japanese (ja-JP): Emi (female)"),
    ("es-LA_SofiaVoice","Latin American Spanish (es-LA): Sofia (female)"),
    ("es-LA_SofiaV3Voice","Latin American Spanish (es-LA): SofiaV3 (female, ednn)"),
    ("es-US_SofiaVoice","North American Spanish (es-US): Sofia (female)"),
    ("es-US_SofiaV3Voice","North American Spanish (es-US): SofiaV3 (female, ednn)")
]


HOST = 'text-to-speech-demo.ng.bluemix.net'

BASE_URL = 'https://' + HOST

DEMO_URL = BASE_URL + '/api/v1/synthesize'



class WatsonTTS(Service):
    """
    Provides a Service-compliant implementation for Watson Text-to-Speech.
    """

    __slots__ = []

    NAME = "Watson Text-to-Speech"

    TRAITS = [Trait.INTERNET]

    def desc(self):
        """
        Returns a short, static description.
        """
        return "Watson Text-to-Speech (%d voices)." % (
            len(set(map(lambda x: x[0][:5], VOICES))))


    def options(self):
        """
        Provides access to voice only.
        """
        return [dict(
                    key='voice',
                    label="Voice",
                    values=VOICES,
                    transform=lambda value: value,
                    default='en-US_LisaV3Voice',
            )]


    def run(self, text, options, path):
        """
        Send a synthesis request to the Text-to-Speech API and
        decode the base64-encoded string into an audio file.
        """

        payload = self.net_stream(
            (DEMO_URL, dict(
                text=text, 
                voice=options['voice'],
                download="true", 
                accept="audio/mp3"
            )),
            method='GET',
            custom_headers={
                'Referer':BASE_URL,
                'Content-type': 'audio/mpeg',
                'Host':HOST
            }
        )
        with open(path, 'wb') as response_output:
            response_output.write(payload)
