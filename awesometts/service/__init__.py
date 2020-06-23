# -*- coding: utf-8 -*-

# AwesomeTTS text-to-speech add-on for Anki
# Copyright (C) 2010-Present  Anki AwesomeTTS Development Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This file has been modified by lovac42 and may not be the same as the original.

"""
Service classes for AwesomeTTS
"""

from .common import Trait

from .abair import Abair
from .azure import Azure
from .baidu import Baidu
from .bing import Bing
from .cambridge import Cambridge
from .collins import Collins
from .duden import Duden
from .ekho import Ekho
from .espeak import ESpeak
from .festival import Festival
from .fluencynl import FluencyNl
from .forvo import Forvo
from .google import Google
from .googletts import GoogleTTS
from .howjsay import Howjsay
from .imtranslator import ImTranslator
from .ispeech import ISpeech
from .naver import Naver
from .neospeech import NeoSpeech
from .oddcast import Oddcast
from .oxford import Oxford
from .oxford_lrn import OxfordLrn
from .pico2wave import Pico2Wave
from .rhvoice import RHVoice
from .sapi5com import SAPI5COM
from .sapi5js import SAPI5JS
from .say import Say
from .spanishdict import SpanishDict
from .textaloud import TextAloud
from .voicetext import VoiceText
from .watsontts import WatsonTTS
from .webster import Webster
from .wiktionary import Wiktionary
from .wordreference import WordReference
from .yandex import Yandex
from .youdao import Youdao


__all__ = [
    # common
    'Trait',

    # services
    'Abair',
    'Azure',
    'Baidu',
    'Bing',
    'Cambridge',
    'Collins',
    'Duden',
    'Ekho',
    'ESpeak',
    'Festival',
    'FluencyNl',
    'Forvo',
    'Google',
    'GoogleTTS',
    'Howjsay',
    'ImTranslator',
    'ISpeech',
    'Naver',
    'NeoSpeech',
    'Oddcast',
    'Oxford',
    'OxfordLrn',
    'Pico2Wave',
    'RHVoice',
    'SAPI5COM',
    'SAPI5JS',
    'Say',
    'SpanishDict',
    'TextAloud',
    'VoiceText',
    'WatsonTTS',
    'Webster',
    'Wiktionary',
    'WordReference',
    'Yandex',
    'Youdao',
]
