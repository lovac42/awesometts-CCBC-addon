# -*- coding: utf-8 -*-
# This file has been modified by lovac42 for CCBC, and is not the same as the original.

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

import anki
import aqt
import sys
from os.path import join
from time import time
from aqt.qt import *

from . import conversion as to, gui, paths, service, utils
from .bundle import Bundle
from .config import Config
from .player import Player
from .router import Router
from .text import Sanitizer
from .const import WEB, VERSION

from .lib.com.lovac42.anki.backend import sound as lib_sound


def get_platform_info():
    """Exception-tolerant platform information for use with AGENT."""

    implementation = system_description = "???"
    python_version = "?.?.?"

    try:
        import platform
    except:  # catch-all, pylint:disable=bare-except
        pass
    else:
        try:
            implementation = platform.python_implementation()
        except:  # catch-all, pylint:disable=bare-except
            pass

        try:
            python_version = platform.python_version()
        except:  # catch-all, pylint:disable=bare-except
            pass

        try:
            system_description = platform.platform().replace('-', ' ')
        except:  # catch-all, pylint:disable=bare-except
            pass

    return "%s %s; %s" % (implementation, python_version, system_description)


AGENT = 'AwesomeTTS/%s (Anki %s; PyQt %s; %s)' % (VERSION, anki.version,
                                                  PYQT_VERSION_STR,
                                                  get_platform_info())



# Begin core class initialization and dependency setup, pylint:disable=C0103
logger = Bundle(debug=lambda *a, **k: None, error=lambda *a, **k: None,
                info=lambda *a, **k: None, warn=lambda *a, **k: None)
# for logging output, replace `logger` with a real one, e.g.:
# import logging as logger
# logger.basicConfig(stream=sys.stdout, level=logger.DEBUG)



DEFAULT_PRESET = utils.getDefaultPreset()

sequences = {key: QKeySequence()
             for key in ['browser_generator', 'browser_stripper', 'read_text',
                         'configurator', 'editor_generator', 'templater']}

config = Config(
    db=Bundle(path=paths.CONFIG,
              table='general',
              normalize=to.normalized_ascii),
    cols=[
        ('automaticQuestions', 'integer', True, to.lax_bool, int),
        ('automaticAnswers', 'integer', True, to.lax_bool, int),
        ('automatic_questions_errors', 'integer', True, to.lax_bool, int),
        ('automatic_questions_auto_tag', 'integer', False, to.lax_bool, int),
        ('automatic_answers_errors', 'integer', True, to.lax_bool, int),
        ('automatic_answers_auto_tag', 'integer', False, to.lax_bool, int),
        ('manual_questions_errors', 'integer', True, to.lax_bool, int),
        ('manual_questions_auto_tag', 'integer', True, to.lax_bool, int),
        ('manual_answers_errors', 'integer', True, to.lax_bool, int),
        ('manual_answers_auto_tag', 'integer', True, to.lax_bool, int),
        ('cache_days', 'integer', 365, int, int),
        ('cache_location', 'text', '', str, str),
        ('delay_answers_onthefly', 'integer', 0, int, int),
        ('delay_answers_stored_ours', 'integer', 0, int, int),
        ('delay_answers_stored_theirs', 'integer', 0, int, int),
        ('delay_questions_onthefly', 'integer', 0, int, int),
        ('delay_questions_stored_ours', 'integer', 0, int, int),
        ('delay_questions_stored_theirs', 'integer', 0, int, int),
        ('ellip_note_newlines', 'integer', False, to.lax_bool, int),
        ('ellip_template_newlines', 'integer', False, to.lax_bool, int),
        ('extras', 'text', {}, to.deserialized_dict, to.compact_json),
        ('filenames', 'text', 'hash', str, str),
        ('filenames_human', 'text',
         '{{text}} ({{service}} {{voice}})', str, str),
        ('groups', 'text', {}, to.deserialized_dict, to.compact_json),
        ('lame_flags', 'text', '--quiet -q 2', str, str),
        ('last_mass_append', 'integer', True, to.lax_bool, int),
        ('last_mass_behavior', 'integer', True, to.lax_bool, int),
        ('last_mass_dest', 'text', 'Back', str, str),
        ('last_mass_source', 'text', 'Front', str, str),
        ('last_options', 'text', {}, to.deserialized_dict, to.compact_json),
        ('last_service', 'text', ('sapi5js' if 'win32' in sys.platform
                                  else 'say' if 'darwin' in sys.platform
                                  else 'yandex'), str, str),
        ('last_strip_mode', 'text', 'ours', str, str),
        ('launch_browser_generator', 'integer', Qt.ControlModifier | Qt.Key_T,
         to.nullable_key, to.nullable_int),
        ('launch_browser_stripper', 'integer', None, to.nullable_key,
         to.nullable_int),
        ('launch_configurator', 'integer', Qt.ControlModifier | Qt.Key_T,
         to.nullable_key, to.nullable_int),
        ('launch_editor_generator', 'integer', Qt.ControlModifier | Qt.Key_T,
         to.nullable_key, to.nullable_int),
        ('launch_templater', 'integer', Qt.ControlModifier | Qt.Key_T,
         to.nullable_key, to.nullable_int),
        ('launch_read_text', 'integer', Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_C,
         to.nullable_key, to.nullable_int),
        ('otf_only_revealed_cloze', 'integer', False, to.lax_bool, int),
        ('otf_remove_hints', 'integer', False, to.lax_bool, int),
        ('presets', 'text', {}, to.deserialized_dict, to.compact_json),
        ('spec_note_count', 'text', '', str, str),
        ('spec_note_count_wrap', 'integer', True, to.lax_bool, int),
        ('spec_note_ellipsize', 'text', '', str, str),
        ('spec_note_strip', 'text', '', str, str),
        ('spec_template_count', 'text', '', str, str),
        ('spec_template_count_wrap', 'integer', True, to.lax_bool, int),
        ('spec_template_ellipsize', 'text', '', str, str),
        ('spec_template_strip', 'text', '', str, str),
        ('strip_note_braces', 'integer', False, to.lax_bool, int),
        ('strip_note_brackets', 'integer', False, to.lax_bool, int),
        ('strip_note_parens', 'integer', False, to.lax_bool, int),
        ('strip_template_braces', 'integer', False, to.lax_bool, int),
        ('strip_template_brackets', 'integer', False, to.lax_bool, int),
        ('strip_template_parens', 'integer', False, to.lax_bool, int),
        ('sub_note_cloze', 'text', 'anki', str, str),
        ('sub_template_cloze', 'text', 'anki', str, str),
        ('sul_note', 'text', [], to.substitution_list, to.substitution_json),
        ('sul_template', 'text', [], to.substitution_list,
         to.substitution_json),
        ('templater_cloze', 'integer', True, to.lax_bool, int),
        ('templater_field', 'text', 'Front', str, str),
        ('templater_hide', 'text', 'normal', str, str),
        ('templater_target', 'text', 'front', str, str),
        ('background_batch_proc', 'integer', False, to.lax_bool, int),
        ('throttle_sleep', 'integer', 20, int, int),
        ('throttle_threshold', 'integer', 5, int, int),
        ('TTS_KEY_A', 'integer', Qt.Key_F4, to.nullable_key, to.nullable_int),
        ('TTS_KEY_Q', 'integer', Qt.Key_F3, to.nullable_key, to.nullable_int),
        ('updates_enabled', 'integer', True, to.lax_bool, int),
        ('updates_ignore', 'text', '', str, str),
        ('updates_postpone', 'integer', 0, int, lambda i: int(round(i))),
        ('read_text_type', 'text', '', str, str),
        ('read_text_preset', 'text', '', str, str),
    ],
    logger=logger,
    events=[
    ],
)



try: #for 2.1.20
    from aqt.sound import av_player
    from anki.sound import SoundOrVideoTag

    def append_file(self, filename: str) -> None:
        self._enqueued.append(SoundOrVideoTag(filename=filename))
        self._play_next_if_idle()

    anki.sound.play = lambda filename: append_file(av_player, filename)
except ImportError:
    pass


player = Player(
    anki=Bundle(
        mw=aqt.mw,
        native=anki.sound.play,  # need direct reference, as this gets wrapped
        sound=anki.sound,  # for accessing queue member, which is not wrapped
    ),
    blank=paths.BLANK,
    config=config,
    logger=logger,
)

router = Router(
    services=Bundle(
        mappings=[
            # ('abair', service.Abair),
            ('azure', service.Azure),
            # ('baidu', service.Baidu),
            ('bing', service.Bing),
            ('cambridge', service.Cambridge),
            ('collins', service.Collins),
            # ('duden', service.Duden),
            ('ekho', service.Ekho),
            ('espeak', service.ESpeak),
            ('festival', service.Festival),
            # ('fluencynl', service.FluencyNl),
            ('forvo', service.Forvo),
            ('google', service.Google),
            ('googletts', service.GoogleTTS),
            ('howjsay', service.Howjsay),
            # ('imtranslator', service.ImTranslator),
            ('ispeech', service.ISpeech),
            ('naver', service.Naver),
            ('neospeech', service.NeoSpeech),
            ('oddcast', service.Oddcast),
            ('oxford', service.Oxford),
            ('oxford_lrn', service.OxfordLrn),
            ('pico2wave', service.Pico2Wave),
            ('rhvoice', service.RHVoice),
            ('sapi5com', service.SAPI5COM),
            ('sapi5js', service.SAPI5JS),
            ('say', service.Say),
            ('spanishdict', service.SpanishDict),
            ('textaloud', service.TextAloud),
            ('voicetext', service.VoiceText),
            ('watsontts', service.WatsonTTS),
            ('webster', service.Webster),
            # ('wiktionary', service.Wiktionary),
            # ('yandex', service.Yandex),
            ('youdao', service.Youdao),
        ],
        dead=dict(
            ttsapicom="TTS-API.com has gone offline and can no longer be "
                      "used. Please switch to another service with English.",
        ),
        aliases=[('b', 'baidu'), ('g', 'google'), ('macosx', 'say'),
                 ('microsoft', 'sapi5js'), ('microsoftjs', 'sapi5js'),
                 ('microsoftjscript', 'sapi5js'), ('oed', 'oxford'),
                 ('osx', 'say'), ('sapi', 'sapi5js'), ('sapi5', 'sapi5js'),
                 ('sapi5jscript', 'sapi5js'), ('sapijs', 'sapi5js'),
                 ('sapijscript', 'sapi5js'), ('svox', 'pico2wave'),
                 ('svoxpico', 'pico2wave'), ('ttsapi', 'ttsapicom'),
                 ('windows', 'sapi5js'), ('windowsjs', 'sapi5js'),
                 ('windowsjscript', 'sapi5js'), ('y', 'yandex')],
        normalize=to.normalized_ascii,
        args=(),
        kwargs=dict(temp_dir=paths.TEMP,
                    lame_flags=lambda: config['lame_flags'],
                    normalize=to.normalized_ascii,
                    logger=logger,
                    ecosystem=Bundle(web=WEB, agent=AGENT)),
    ),
    cache_dir=config['cache_location'] or paths.CACHE,
    temp_dir=join(paths.TEMP, '_awesometts_scratch_' + str(int(time()))),
    logger=logger,
    config=config,
)


STRIP_TEMPLATE_POSTHTML = [
    'whitespace',
    'sounds_univ',
    'filenames',
    ('within_parens', 'strip_template_parens'),
    ('within_brackets', 'strip_template_brackets'),
    ('within_braces', 'strip_template_braces'),
    ('char_remove', 'spec_template_strip'),
    ('counter', 'spec_template_count', 'spec_template_count_wrap'),
    ('char_ellipsize', 'spec_template_ellipsize'),
    ('custom_sub', 'sul_template'),
    'ellipses',
    'whitespace',
]

addon = Bundle(
    config=config,
    downloader=Bundle(
        base=aqt.addons.GetAddons,
        superbase=aqt.addons.GetAddons.__bases__[0],
        args=[aqt.mw],
        kwargs=dict(),
        attrs=dict(
            form=Bundle(
                code=Bundle(text=lambda: '301952613'),
            ),
            mw=aqt.mw,
        ),
        fail=lambda message: aqt.utils.showCritical(message, aqt.mw),
    ),
    logger=logger,
    paths=Bundle(cache=config['cache_location'] or paths.CACHE,
                 is_link=paths.ADDON_IS_LINKED),
    player=player,
    router=router,
    strip=Bundle(
        # n.b. cloze substitution logic happens first in both modes because:
        # - we need the <span>...</span> markup in on-the-fly to identify it
        # - Anki won't recognize cloze w/ HTML beginning/ending within braces
        # - the following 'html' rule will cleanse the HTML out anyway

        # for content directly from a note field (e.g. BrowserGenerator runs,
        # prepopulating a modal input based on some note field, where cloze
        # placeholders are still in their unprocessed state)
        from_note=Sanitizer([
            ('clozes_braced', 'sub_note_cloze'),
            ('newline_ellipsize', 'ellip_note_newlines'),
            'html',
            'whitespace',
            'sounds_univ',
            'filenames',
            ('within_parens', 'strip_note_parens'),
            ('within_brackets', 'strip_note_brackets'),
            ('within_braces', 'strip_note_braces'),
            ('char_remove', 'spec_note_strip'),
            ('counter', 'spec_note_count', 'spec_note_count_wrap'),
            ('char_ellipsize', 'spec_note_ellipsize'),
            ('custom_sub', 'sul_note'),
            'ellipses',
            'whitespace',
        ], config=config, logger=logger),

        # for cleaning up already-processed HTML templates (e.g. on-the-fly,
        # where cloze is marked with <span class=cloze></span> tags)
        from_template_front=Sanitizer([
            ('clozes_rendered', 'sub_template_cloze'),
            'hint_links',
            ('hint_content', 'otf_remove_hints'),
            ('newline_ellipsize', 'ellip_template_newlines'),
            'html',
        ] + STRIP_TEMPLATE_POSTHTML, config=config, logger=logger),

        # like the previous, but for the back sides of cards
        from_template_back=Sanitizer([
            ('clozes_revealed', 'otf_only_revealed_cloze'),
            'hint_links',
            ('hint_content', 'otf_remove_hints'),
            ('newline_ellipsize', 'ellip_template_newlines'),
            'html',
        ] + STRIP_TEMPLATE_POSTHTML, config=config, logger=logger),

        # for cleaning up text from unknown sources (e.g. system clipboard);
        # n.b. clozes_revealed is not used here without the card context and
        # it would be a weird thing to apply to the clipboard content anyway
        from_unknown=Sanitizer([
            ('clozes_braced', 'sub_note_cloze'),
            ('clozes_rendered', 'sub_template_cloze'),
            'hint_links',
            ('hint_content', 'otf_remove_hints'),
            ('newline_ellipsize', 'ellip_note_newlines'),
            ('newline_ellipsize', 'ellip_template_newlines'),
            'html',
            'html',  # clipboards often have escaped HTML, so we run twice
            'whitespace',
            'sounds_univ',
            'filenames',
            ('within_parens', ['strip_note_parens', 'strip_template_parens']),
            ('within_brackets', ['strip_note_brackets',
                                 'strip_template_brackets']),
            ('within_braces', ['strip_note_braces', 'strip_template_braces']),
            ('char_remove', 'spec_note_strip'),
            ('char_remove', 'spec_template_strip'),
            ('counter', 'spec_note_count', 'spec_note_count_wrap'),
            ('counter', 'spec_template_count', 'spec_template_count_wrap'),
            ('char_ellipsize', 'spec_note_ellipsize'),
            ('char_ellipsize', 'spec_template_ellipsize'),
            ('custom_sub', 'sul_note'),
            ('custom_sub', 'sul_template'),
            'ellipses',
            'whitespace',
        ], config=config, logger=logger),

        # for direct user input (e.g. previews, EditorGenerator insertion)
        from_user=Sanitizer(rules=['ellipses', 'whitespace'], logger=logger),

        # target sounds specifically
        sounds=Bundle(
            # using Anki's method (used if we need to reproduce how Anki does
            # something, e.g. when Reviewer emulates {{FrontSide}})
            anki=lib_sound.stripSounds,

            # using AwesomeTTS's methods (which have access to precompiled re
            # objects, usable for everything else, e.g. when BrowserGenerator
            # or BrowserStripper need to remove old sounds)
            ours=Sanitizer(rules=['sounds_ours', 'filenames'], logger=logger),
            theirs=Sanitizer(rules=['sounds_theirs'], logger=logger),
            univ=Sanitizer(rules=['sounds_univ', 'filenames'], logger=logger),
        ),
    ),
    version=VERSION,
    web=WEB,
)
# End core class initialization and dependency setup, pylint:enable=C0103


reviewer=gui.Reviewer(addon=addon,
                alerts=aqt.utils.showWarning,
                mw=aqt.mw)
