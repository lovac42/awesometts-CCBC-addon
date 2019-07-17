# -*- coding: utf-8 -*-
# Copyright (C) 2019 Lovac42
# Copyright (C) 2010-2018 Anki AwesomeTTS Development Team
# Support: https://github.com/lovac42/awesometts-CCBC-addon
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


"""
Service implementation for Oxford Dictionary
"""

import re
from html.parser import HTMLParser

from .base import Service
from .common import Trait

__all__ = ['Oxford']


RE_WHITESPACE = re.compile(r'[-\0\s_]+', re.UNICODE)

# n.b. The OED has words with periods (e.g. "Capt."), so we preserve those,
# but other punctuation can generally be dropped. The re.UNICODE flag here is
# important so that accented characters are not filtered out.
RE_DISCARD = re.compile(r'[^-.\s\w]+', re.UNICODE)


class OxfordLister(HTMLParser):
    """Accumulate all found MP3s into `sounds` member."""

    def reset(self):
        HTMLParser.reset(self)
        self.sounds = []
        self.prev_tag = ""

    def handle_starttag(self, tag, attrs):
        if tag == "audio" and self.prev_tag == "a":
            snd = [v for k, v in attrs if k == "src"]
            if snd:
                self.sounds.extend(snd)
        if tag == "a" and ("class", "speaker") in attrs:
            self.prev_tag = tag


class Oxford(Service):
    """
    Provides a Service-compliant implementation for Oxford Dictionary.
    """

    __slots__ = []

    NAME = "Oxford Dictionary (Lexico)"

    TRAITS = [Trait.INTERNET, Trait.DICTIONARY]

    def desc(self):
        """
        Returns a short, static description.
        """

        return "Lexico Dictionary (British only now, get over it); " \
            "dictionary words only, with (optional) fuzzy matching"

    def options(self):
        """
        Provides access to voice and fuzzy matching switch.
        """

        voice_lookup = dict([
            # aliases for English, British ("default" for the OED)
            (self.normalize(alias), 'en-GB')
            for alias in ['British', 'British English', 'English, British',
                          'English', 'en', 'en-EU', 'en-UK', 'EU', 'GB', 'UK']
        ])

        def transform_voice(value):
            """Normalize and attempt to convert to official code."""
            normalized = self.normalize(value)
            if normalized in voice_lookup:
                return voice_lookup[normalized]
            return value

        return [
            dict(
                key='voice',
                label="Voice",
                values=[('en-GB', "English, British (en-GB)")],
                default='en-GB',
                transform=transform_voice,
            ),
            dict(
                key='fuzzy',
                label="Fuzzy matching",
                values=[(True, 'Enabled'), (False, 'Disabled')],
                default=True,
                transform=bool
            )
        ]

    def modify(self, text):
        """
        OED generally represents words with spaces using a dash between
        the words. Case usually doesn't matter, but sometimes it does,
        so we do not normalize it (e.g. "United-Kingdom" works but
        "united-kingdom" does not).
        """

        return RE_WHITESPACE.sub('-', RE_DISCARD.sub('', text)).strip('-')

    def run(self, text, options, path):
        """
        Download web page for given word
        Then extract mp3 path and download it
        """

        if len(text) > 100:
            raise IOError("Input text is too long for the Oxford Dictionary")

        from urllib.parse import quote
        dict_url = 'https://www.lexico.com/%s/definition/%s' % (
            'en' if options['voice'] == 'en-GB' else '',
            quote(text.encode('utf-8'))
        )

        try:
            html_payload = self.net_stream(dict_url, allow_redirects=options['fuzzy'])
        except IOError as io_error:
            if getattr(io_error, 'code', None) == 404:
                raise IOError(
                    "The Oxford Dictionary does not recognize this phrase. "
                    "While most single words are recognized, many multi-word "
                    "phrases are not."
                    if text.count('-')
                    else "The Oxford Dictionary does not recognize this word."
                )
            else:
                raise
        except ValueError as error:
            if str(error) == "Request has been redirected":
                raise IOError(
                    "The Oxford Dictionary has no exact match for your input. "
                    "You can enable fuzzy-matching in options."
                )
            raise error

        parser = OxfordLister()
        parser.feed(html_payload.decode('utf-8'))
        parser.close()

        if len(parser.sounds) > 0:
            sound_url = parser.sounds[0]

            self.net_download(
                path,
                sound_url,
                require=dict(mime='audio/mpeg', size=1024),
            )
        else:
            raise IOError(
                "The Oxford Dictionary does not currently seem to be "
                "advertising American English pronunciation. You may want to "
                "consider either using a different service or switching to "
                "British English."
                if options['voice'] == 'en-US'

                else
                "The Oxford Dictionary has no recorded audio for your input."
            )
