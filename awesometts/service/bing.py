# -*- coding: utf-8 -*-
# Copyright (C) 2019 Lovac42
# Copyright (C) 2010-2018 Anki AwesomeTTS Development Team
# Support: https://github.com/lovac42/awesometts-CCBC-addon
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


"""
Bing Translate
"""

import json
import base64
import requests
from urllib.parse import quote

from .base import Service
from .common import Trait

__all__ = ['Bing']


# There could be more alternative options in the list,
# only the demo voices from bing translator is listed here.

VOICES = [
    ("ar-SA","Male","ar-SA-Naayf"),
    ("bg-BG","Male","bg-BG-Ivan"),
    ("ca-ES","Female","ca-ES-HerenaRUS"),
    ("cs-CZ","Male","cs-CZ-Jakub"),
    ("da-DK","Female","da-DK-HelleRUS"),
    ("de-DE","Female","de-DE-Hedda"),
    ("el-GR","Male","el-GR-Stefanos"),
    ("en-US","Female","en-US-JessaRUS"),
    ("es-ES","Female","es-ES-Laura-Apollo"),
    ("fi-FI","Female","fi-FI-HeidiRUS"),
    ("fr-FR","Female","fr-FR-Julie-Apollo"),
    ("he-IL","Male","he-IL-Asaf"),
    ("hi-IN","Female","hi-IN-Kalpana-Apollo"),
    ("hr-HR","Male","hr-HR-Matej"),
    ("hu-HU","Male","hu-HU-Szabolcs"),
    ("id-ID","Male","id-ID-Andika"),
    ("it-IT","Male","it-IT-Cosimo-Apollo"),
    ("ja-JP","Female","ja-JP-Ayumi-Apollo"),
    ("ko-KR","Female","ko-KR-HeamiRUS"),
    ("ms-MY","Male","ms-MY-Rizwan"),
    ("nl-NL","Female","nl-NL-HannaRUS"),
    ("nb-NO","Female","nb-NO-HuldaRUS"),
    ("pl-PL","Female","pl-PL-PaulinaRUS"),
    ("pt-PT","Female","pt-PT-HeliaRUS"),
    ("ro-RO","Male","ro-RO-Andrei"),
    ("ru-RU","Female","ru-RU-Irina-Apollo"),
    ("sk-SK","Male","sk-SK-Filip"),
    ("sl-SL","Male","sl-SI-Lado"),
    ("sv-SE","Female","sv-SE-HedvigRUS"),
    ("ta-IN","Female","ta-IN-Valluvar"),
    ("te-IN","Male","te-IN-Chitra"),
    ("th-TH","Male","th-TH-Pattara"),
    ("tr-TR","Female","tr-TR-SedaRUS"),
    ("vi-VN","Male","vi-VN-An"),
    ("zh-CN","Female","zh-CN-HuihuiRUS"),
    ("zh-HK","Female","zh-HK-Tracy-Apollo")
]



#https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/regions#standard-and-neural-voices

ISSUEHOST = 'eastus2.api.cognitive.microsoft.com'

ISSUETOKEN = 'https://'+ISSUEHOST+'/sts/v1.0/issueToken'

HOST = 'eastus2.tts.speech.microsoft.com'

BASE_URL = 'https://' + HOST

DEMO_URL = BASE_URL + '/cognitiveservices/v1'


class Bing(Service):
    """
    Provides a Service-compliant implementation for Google Cloud Text-to-Speech.
    """

    __slots__ = []

    NAME = "Bing Translator"

    TRAITS = [Trait.INTERNET]

    def desc(self):
        """
        Returns a short, static description.
        """
        return """Bing Translator (%d voices)

Token expires every 10 mins,

Go to: https://bing.com/translator

Type in console: SpeechServiceHelper.authToken
""" % len(VOICES)

    def extras(self):
        """
            Grab the token from bing translate.
            Look at the packet header "Authorization: Bearer ...",
            expires every 10 mins.
        """
        return [dict(key='key', label="Bearer Token", required=True)]


    def options(self):
        """
        Provides access to voice only.
        """
        return [dict(
            key='voice',
            label="Voice",
            values=[
                (name, "%s (%s)" % (name, gender))
                for code, gender, name in VOICES
            ],
            transform=lambda value: value,
            default='en-US-JessaRUS',
            )
        ]


    def run(self, text, options, path):

        token =  options['key'] # Temp solution
        # token = self.issueToken() #TODO:

        lang="en-US"
        gender="Female"
        name=options['voice']
        for c,g,n in VOICES: #TODO: rewrite to use maps
            if n==name:
                lang=c
                gender=g
                break;

        xml="""<speak version='1.0' xml:lang='%s'>
<voice xml:lang='%s' xml:gender='%s' name='%s'>%s</voice>
</speak>"""%(lang,lang,gender,name,text)

        headers={
            'Charset': 'utf-8',
            'Content-type': 'application/ssml+xml',
            'Origin': 'https://www.bing.com',
            'Referer': 'https://www.bing.com/',
            'x-microsoft-outputformat': 'audio-16khz-32kbitrate-mono-mp3',
            'Cache-control': 'no-cache',
            'Authorization': 'Bearer ' + token
        }

        r=requests.post(DEMO_URL, data=xml.encode('utf-8'), headers=headers)
        if r.status_code==401:
            print("Bing TTS: Bearer Token Expired")
        r.raise_for_status()

        audio_content = r.content
        with open(path, 'wb') as response_output:
            response_output.write(audio_content)



    def issueToken(self):
        # TODO: API KEY options

        # Requires api key, which requires signing up
        headers={
            'Ocp-Apim-Subscription-Key': 'XXXXXXXXXXXX',
            'Content-type': 'application/x-www-form-urlencoded',
            'Host': ISSUEHOST
            # 'Content-Length': "56",
        }
        r=requests.post(ISSUETOKEN, headers=headers)
        r.raise_for_status()
        # print(r.json())
        return r.json()
