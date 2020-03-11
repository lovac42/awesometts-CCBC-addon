# -*- coding: utf-8 -*-
# Copyright (C) 2019 Lovac42
# Copyright (C) 2010-2018 Anki AwesomeTTS Development Team
# Support: https://github.com/lovac42/awesometts-CCBC-addon
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


"""
Bing Translate
"""

import re
import json
import time
import base64
import requests
from urllib.parse import quote
from threading import Lock
from aqt import mw

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

    __slots__ = [
        '_lock',
        '_cookies',
        '_token',
        '_ig',
        '_direct_download',
    ]

    NAME = "Bing Translator"

    TRAITS = [Trait.INTERNET]

    def __init__(self, *args, **kwargs):
        self._lock = Lock()
        self._cookies = None
        self._token = None
        self._ig = None
        self._direct_download = True
        super(Bing, self).__init__(*args, **kwargs)

    def desc(self):
        """
        Returns a short, static description.
        """
        return """Bing Translator (%d voices)

Note: Please be kind to online services and repect
the wait time limit.

Note2: Takes several tries on initial load to setup cookies.
Need to fix this.
""" % len(VOICES)

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


    # def extras(self):
        # return [dict(key='key', label="Bearer Key", required=False)]

    def run(self, text, options, path):

        # if options['key']:
            # self._token=options['key']
        if not self._token:
            # token expires every 10 minutes
            self._token=self.issueToken()

        if not self._token:
            raise AttributeError("No token form Bing Translator")


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
            'Origin': 'http://www.bing.com',
            'Referer': 'http://www.bing.com/',
            'x-microsoft-outputformat': 'audio-16khz-32kbitrate-mono-mp3',
            'Cache-control': 'no-cache',
            'Authorization': 'Bearer ' + self._token
        }

        r=requests.post(DEMO_URL, data=xml.encode('utf-8'), headers=headers)
        if r.status_code==401:
            # Bearer Token Expired, expires every 10 minutes
            self._token=None
            return self.run(text, options, path)

        r.raise_for_status()
        audio_content = r.content
        with open(path, 'wb') as response_output:
            response_output.write(audio_content)

        time.sleep(1)


    def issueToken(self):
        """
        Set cookies, parse IG value from html, get token from url using IG value.
        """

        with self._lock:
            if not self._cookies:
                self._netops += 1

                res = requests.get(
                    url='http://www.bing.com/translator',
                    headers={'User-Agent': 'Mozilla/5.0'},
                    timeout=20,
                )

                if res.status_code != 200:
                    res.raise_for_status()

                self._cookies=res.cookies
                html = res.text

                # from aqt.utils import showText
                # showText(html) # I'm on windows...
                # print(html)

                extract=re.search(r'\,IG\:\"([A-Z\d]+)\"\,EventID',html)
                if extract:
                    self._ig=extract.groups(1)[0]

            if not self._ig:
                raise AttributeError("No IG form Bing Translator")

            # TODO: Not sure what IID=translator.xxx.x is, but it's in the html string.
            # data-iid="translator.5026">

            # TODO: Fix this, throws 404 errors half the time
            for n in range(5): #retry 5x on 404 errors
                r=requests.post(
                    'http://www.bing.com/tfetspktok?isVertical=1&IG=%s&IID=translator.5026.3'%(self._ig),
                    headers={
                        'Content-type': 'application/x-www-form-urlencoded',
                        'Host': 'www.bing.com',
                        'origin': 'http://www.bing.com',
                        'Referer': 'http://www.bing.com/',
                    },
                    cookies=self._cookies,
                    timeout=20,
                )

                if r.status_code == 200:
                    return r.json()['token']
                if r.status_code != 404:
                    r.raise_for_status()
                time.sleep(5)
            r.raise_for_status()
