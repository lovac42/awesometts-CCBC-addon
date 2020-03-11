# -*- coding: utf-8 -*-
# Copyright (C) 2019 Lovac42
# Copyright (C) 2010-2018 Anki AwesomeTTS Development Team
# Support: https://github.com/lovac42/awesometts-CCBC-addon
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


"""
Service implementation for Watson Text-to-Speech API
"""

import time
import base64
import requests

from .base import Service
from .common import Trait

__all__ = ['WatsonTTS']

VOICES = [
    ("en-US_AllisonVoice","American English (en-US): Allison (female, expressive, transformable)"),
    ("en-US_AllisonV3Voice","American English (en-US): AllisonV3 (female, enhanced dnn)"),
    ("en-US_LisaVoice","American English (en-US): Lisa (female, transformable)"),
    ("en-US_LisaV3Voice","American English (en-US): LisaV3 (female, enhanced dnn)"),
    ("en-US_MichaelVoice","American English (en-US): Michael (male, transformable)"),
    ("en-US_MichaelV3Voice","American English (en-US): MichaelV3 (male, enhanced dnn)"),
    ("ar-AR_OmarVoice","Arabic (ar-AR): Omar (male)"),
    ("pt-BR_IsabelaVoice","Brazilian Portuguese (pt-BR): Isabela (female)"),
    ("pt-BR_IsabelaV3Voice","Brazilian Portuguese (pt-BR): IsabelaV3 (female, enhanced dnn)"),
    ("en-GB_KateVoice","British English (en-GB): Kate (female)"),
    ("en-GB_KateV3Voice","British English (en-GB): KateV3 (female, enhanced dnn)"),
    ("es-ES_EnriqueVoice","Castilian Spanish (es-ES): Enrique (male)"),
    ("es-ES_EnriqueV3Voice","Castilian Spanish (es-ES): EnriqueV3 (male, enhanced dnn)"),
    ("es-ES_LauraVoice","Castilian Spanish (es-ES): Laura (female)"),
    ("es-ES_LauraV3Voice","Castilian Spanish (es-ES): LauraV3 (female, enhanced dnn)"),
    ("zh-CN_LiNaVoice","Chinese, Mandarin (zh-CN): LiNa (female)"),
    ("zh-CN_WangWeiVoice","Chinese, Mandarin (zh-CN): WangWei (Male)"),
    ("zh-CN_ZhangJingVoice","Chinese, Mandarin (zh-CN): ZhangJing (female)"),
    ("nl-NL_EmmaVoice","Dutch (nl-NL): Emma (female)"),
    ("nl-NL_LiamVoice","Dutch (nl-NL): Liam (male)"),
    ("fr-FR_ReneeVoice","French (fr-FR): Renee (female)"),
    ("fr-FR_ReneeV3Voice","French (fr-FR): ReneeV3 (female, enhanced dnn)"),
    ("de-DE_BirgitVoice","German (de-DE): Birgit (female)"),
    ("de-DE_BirgitV3Voice","German (de-DE): BirgitV3 (female, enhanced dnn)"),
    ("de-DE_DieterVoice","German (de-DE): Dieter (male)"),
    ("de-DE_DieterV3Voice","German (de-DE): DieterV3 (male, enhanced dnn)"),
    ("it-IT_FrancescaVoice","Italian (it-IT): Francesca (female)"),
    ("it-IT_FrancescaV3Voice","Italian (it-IT): FrancescaV3 (female, enhanced dnn)"),
    ("ja-JP_EmiVoice","Japanese (ja-JP): Emi (female)"),
    ("ja-JP_EmiV3Voice","Japanese (ja-JP): EmiV3 (female, enhanced dnn)"),
    ("es-LA_SofiaVoice","Latin American Spanish (es-LA): Sofia (female)"),
    ("es-LA_SofiaV3Voice","Latin American Spanish (es-LA): SofiaV3 (female, enhanced dnn)"),
    ("es-US_SofiaVoice","North American Spanish (es-US): Sofia (female)"),
    ("es-US_SofiaV3Voice","North American Spanish (es-US): SofiaV3 (female, enhanced dnn)")
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
        return """Watson Text-to-Speech (%d voices).

Note: Please be kind to online services and repect
the wait time limit.
""" % (len(VOICES))


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
                'Content-type': 'audio/mp3',
                'Host':HOST
            }
        )
        with open(path, 'wb') as response_output:
            response_output.write(payload)

        time.sleep(1)
