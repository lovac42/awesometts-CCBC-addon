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

"""
Add-on package initialization
"""

from os.path import join
import sys
from time import time

from PyQt5.QtGui import QKeySequence

import anki
import aqt

from .shared_loads import *
from . import conversion as to, gui, paths, service
from .bundle import Bundle
from .config import Config
from .player import Player
from .router import Router
from .text import Sanitizer


__all__ = ['browser_menus', 'cards_button', 'config_menu', 'editor_button',
           'reviewer_hooks', 'sound_tag_delays', 'update_checker',
           'window_shortcuts']




# GUI interaction with Anki
# n.b. be careful wrapping methods that have return values (see anki.hooks);
#      in general, only the 'before' mode absolves us of responsibility

# These are all called manually from the __init__.py loader so that if there
# is some sort of breakage with a specific component, it could be possibly
# disabled easily by users who are not utilizing that functionality.


def browser_menus():
    """
    Gives user access to mass generator, MP3 stripper, and the hook that
    disables and enables it upon selection of items.
    """

    from PyQt5 import QtWidgets

    def on_setup_menus(browser):
        """Create an AwesomeTTS menu and add browser actions to it."""

        menu = QtWidgets.QMenu("Awesome&TTS", browser.form.menubar)
        browser.form.menubar.addMenu(menu)

        gui.Action(
            target=Bundle(
                constructor=gui.BrowserGenerator,
                args=(),
                kwargs=dict(browser=browser,
                            addon=addon,
                            alerts=aqt.utils.showWarning,
                            ask=aqt.utils.getText,
                            parent=browser),
            ),
            text="&Add Audio to Selected...",
            sequence=sequences['browser_generator'],
            parent=menu,
        )
        gui.Action(
            target=Bundle(
                constructor=gui.BrowserStripper,
                args=(),
                kwargs=dict(browser=browser,
                            addon=addon,
                            alerts=aqt.utils.showWarning,
                            parent=browser),
            ),
            text="&Remove Audio from Selected...",
            sequence=sequences['browser_stripper'],
            parent=menu,
        )

    def update_title_wrapper(browser):
        """Enable/disable AwesomeTTS menu items upon selection."""

        enabled = bool(browser.form.tableView.selectionModel().selectedRows())
        for action in browser.findChildren(gui.Action):
            action.setEnabled(enabled)

    anki.hooks.addHook(
        'browser.setupMenus',
        on_setup_menus,
    )

    aqt.browser.Browser.updateTitle = anki.hooks.wrap(
        aqt.browser.Browser.updateTitle,
        update_title_wrapper,
        'before',
    )


def cache_control():
    """Registers a hook to handle cache control on session exits."""

    def on_unload_profile():
        """
        Finds MP3s in the cache directory older than the user's
        configured cache limit and attempts to remove them.
        """

        from os import listdir, unlink

        cache = paths.CACHE

        try:
            filenames = listdir(cache)
        except:  # allow silent failure, pylint:disable=bare-except
            return
        if not filenames:
            return

        prospects = (join(cache, filename) for filename in filenames)

        if config['cache_days']:
            from os.path import getmtime

            limit = time() - 86400 * config['cache_days']
            targets = (prospect for prospect in prospects
                       if getmtime(prospect) < limit)
        else:
            targets = prospects

        for target in targets:
            try:
                unlink(target)
            except:  # skip broken files, pylint:disable=bare-except
                pass

    anki.hooks.addHook('unloadProfile', on_unload_profile)


def cards_button():
    """Provides access to the templater helper."""

    from aqt import clayout

    clayout.CardLayout.setupButtons = anki.hooks.wrap(
        clayout.CardLayout.setupButtons,
        lambda card_layout: card_layout.buttons.insertWidget(
            # Now, the card layout for regular notes has 7 buttons/stretchers
            # and the one for cloze notes has 6 (as it lacks a "Flip" button);
            # position 3 puts our button after "Add Field", but in the event
            # that the form suddenly has a different number of buttons, let's
            # just fallback to the far left position

            3 if card_layout.buttons.count() in [6, 7] else 0,
            gui.Button(
                text="Add &TTS",
                tooltip="Insert a tag for on-the-fly playback w/ AwesomeTTS",
                sequence=sequences['templater'],
                target=Bundle(
                    constructor=gui.Templater,
                    args=(),
                    kwargs=dict(card_layout=card_layout,
                                addon=addon,
                                alerts=aqt.utils.showWarning,
                                ask=aqt.utils.getText,
                                parent=card_layout),
                ),
            ),
        ),
        'after',  # must use 'after' so that 'buttons' attribute is set
    )


def config_menu():
    """
    Adds a menu item to the Tools menu in Anki's main window for
    launching the configuration dialog.
    """

    gui.Action(
        target=Bundle(
            constructor=gui.Configurator,
            args=(),
            kwargs=dict(addon=addon, sul_compiler=to.substitution_compiled,
                        alerts=aqt.utils.showWarning,
                        ask=aqt.utils.getText,
                        parent=aqt.mw),
        ),
        text="Awesome&TTS...",
        sequence=sequences['configurator'],
        parent=aqt.mw.form.menuTools,
    )


def editor_button():
    """
    Enable the generation of a single audio clip through the editor,
    which is present in the "Add" and browser windows.
    """

    anki.hooks.addHook(
        'setupEditorButtons',
        lambda buttons, editor: gui.HTMLButton(
            buttons, editor,
            link_id='awesometts_btn',
            tooltip="Record and insert an audio clip here w/ AwesomeTTS",
            sequence=sequences['editor_generator'],
            target=Bundle(
                constructor=gui.EditorGenerator,
                args=(),
                kwargs=dict(editor=editor,
                            addon=addon,
                            alerts=aqt.utils.showWarning,
                            ask=aqt.utils.getText,
                            parent=editor.parentWindow),
            )
        ).buttons
    )

    anki.hooks.addHook(
        'setupEditorShortcuts',
        lambda shortcuts, editor: shortcuts.append(
            (
                sequences['editor_generator'].toString(),
                editor._links['awesometts_btn']
            )
        )
    )

    # TODO: Editor buttons are now in the WebView, not sure how (and if)
    # we should implement muzzling. Please see:
    # https://github.com/dae/anki/commit/a001553f66efe75e660eb0702cd29a9d62503fc4
    """
    aqt.editor.Editor.enableButtons = anki.hooks.wrap(
        aqt.editor.Editor.enableButtons,
        lambda editor, val=True: (
            editor.widget.findChild(gui.Button).setEnabled(val),

            # Temporarily disable any AwesomeTTS menu shortcuts in the Browser
            # window so that if a shortcut combination has been re-used
            # between the editor button and those, the "local" shortcut works.
            # Has no effect on "Add" window (the child list will be empty).
            [action.muzzle(val) for action
             in editor.parentWindow.findChildren(gui.Action)],
        ),
        'before',
    )
    """


def reviewer_hooks():
    """
    Enables support for AwesomeTTS to automatically play text-to-speech
    tags and to also do playback on-demand via shortcut keys and the
    context menu.
    """

    from PyQt5.QtCore import QEvent
    from PyQt5.QtWidgets import QMenu

    reviewer = gui.Reviewer(addon=addon,
                            alerts=aqt.utils.showWarning,
                            mw=aqt.mw)

    # automatic playback

    anki.hooks.addHook(
        'showQuestion',
        lambda: reviewer.card_handler('question', aqt.mw.reviewer.card),
    )

    anki.hooks.addHook(
        'showAnswer',
        lambda: reviewer.card_handler('answer', aqt.mw.reviewer.card),
    )

    # shortcut-triggered playback

    reviewer_filter = gui.Filter(
        relay=lambda event: reviewer.key_handler(
            key_event=event,
            state=aqt.mw.reviewer.state,
            card=aqt.mw.reviewer.card,
            replay_audio=aqt.mw.reviewer.replayAudio,
        ),

        when=lambda event: (aqt.mw.state == 'review' and
                            event.type() == QEvent.KeyPress and
                            not event.isAutoRepeat() and
                            not event.spontaneous()),

        parent=aqt.mw,  # prevents filter from being garbage collected
    )

    aqt.mw.installEventFilter(reviewer_filter)

    # context menu playback

    strip = Sanitizer([('newline_ellipsize', 'ellip_template_newlines')] +
                      STRIP_TEMPLATE_POSTHTML, config=config, logger=logger)

    def on_context_menu(web_view, menu):
        """Populate context menu, given the context/configuration."""

        window = web_view.window()

        try:  # this works for web views embedded in editor windows
            atts_button = web_view.editor.widget.findChild(gui.Button)
        except AttributeError:
            atts_button = None

        say_text = config['presets'] and strip(web_view.selectedText())

        tts_card = tts_side = None
        tts_shortcuts = False
        try:  # this works for web views in the reviewer and template dialog
            if window is aqt.mw and aqt.mw.state == 'review':
                tts_card = aqt.mw.reviewer.card
                tts_side = aqt.mw.reviewer.state
                tts_shortcuts = True
            elif web_view.objectName() == 'mainText':  # card template dialog
                parent_name = web_view.parentWidget().objectName()
                tts_card = window.card
                tts_side = ('question' if parent_name == 'groupBox'
                            else 'answer' if parent_name == 'groupBox_2'
                            else None)
        except Exception:  # just in case, pylint:disable=broad-except
            pass

        tts_question = tts_card and tts_side and \
            reviewer.has_tts('question', tts_card)
        tts_answer = tts_card and tts_side == 'answer' and \
            reviewer.has_tts('answer', tts_card)

        if not (atts_button or say_text or tts_question or tts_answer):
            return

        submenu = QMenu("Awesome&TTS", menu)
        submenu.setIcon(gui.ICON)

        needs_separator = False

        if atts_button:
            submenu.addAction(
                "Add MP3 to the Note",
                lambda: atts_button.click() if atts_button.isEnabled()
                else aqt.utils.showWarning(
                    "Select the note field to which you want to add an MP3.",
                    window,
                )
            )
            needs_separator = True

        if say_text:
            say_display = (say_text if len(say_text) < 25
                           else say_text[0:20].rstrip(' .') + "...")

            if config['presets']:
                if needs_separator:
                    submenu.addSeparator()
                else:
                    needs_separator = True

                def preset_glue(name, preset):
                    """Closure for callback handler to access `preset`."""
                    submenu.addAction(
                        'Say "%s" w/ %s' % (say_display, name),
                        lambda: reviewer.selection_handler(say_text,
                                                           preset,
                                                           window),
                    )
                for item in sorted(config['presets'].items(),
                                   key=lambda item: item[0].lower()):
                    preset_glue(item[0],item[1])

            if config['groups']:
                if needs_separator:
                    submenu.addSeparator()
                else:
                    needs_separator = True

                def group_glue(name, group):
                    """Closure for callback handler to access `group`."""
                    submenu.addAction(
                        'Say "%s" w/ %s' % (say_display, name),
                        lambda: reviewer.selection_handler_group(say_text,
                                                                 group,
                                                                 window),
                    )
                for item in sorted(config['groups'].items(),
                                   key=lambda item: item[0].lower()):
                    group_glue(item[0],item[1])

        if tts_question or tts_answer:
            if needs_separator:
                submenu.addSeparator()

            if tts_question:
                submenu.addAction(
                    "Play On-the-Fly TTS from Question Side",
                    lambda: reviewer.nonselection_handler('question', tts_card,
                                                          window),
                    tts_shortcuts and config['tts_key_q'] or 0,
                )

            if tts_answer:
                submenu.addAction(
                    "Play On-the-Fly TTS from Answer Side",
                    lambda: reviewer.nonselection_handler('answer', tts_card,
                                                          window),
                    tts_shortcuts and config['tts_key_a'] or 0,
                )

        menu.addMenu(submenu)

    anki.hooks.addHook('AnkiWebView.contextMenuEvent', on_context_menu)
    anki.hooks.addHook('EditorWebView.contextMenuEvent', on_context_menu)
    anki.hooks.addHook('Reviewer.contextMenuEvent',
                       lambda reviewer, menu:
                       on_context_menu(reviewer.web, menu))


def sound_tag_delays():
    """
    Enables support for the following sound delay configuration options:

    - delay_questions_stored_ours (AwesomeTTS MP3s on questions)
    - delay_questions_stored_theirs (non-AwesomeTTS MP3s on questions)
    - delay_answers_stored_ours (AwesomeTTS MP3s on answers)
    - delay_answers_stored_theirs (non-AwesomeTTS MP3s on answers)
    """

    anki.sound.play = player.native_wrapper


def temp_files():
    """Remove temporary files upon session exit."""

    def on_unload_profile():
        """
        Finds scratch directories in the temporary path, removes their
        files, then removes the directories themselves.
        """

        from os import listdir, unlink, rmdir
        from os.path import isdir

        temp = paths.TEMP

        try:
            subdirs = [join(temp, filename) for filename in listdir(temp)
                       if filename.startswith('_awesometts_scratch')]
        except:  # allow silent failure, pylint:disable=bare-except
            return
        if not subdirs:
            return

        for subdir in subdirs:
            if isdir(subdir):
                for filename in listdir(subdir):
                    try:
                        unlink(join(subdir, filename))
                    except:  # skip busy files, pylint:disable=bare-except
                        pass
                try:
                    rmdir(subdir)
                except:  # allow silent failure, pylint:disable=bare-except
                    pass

    anki.hooks.addHook('unloadProfile', on_unload_profile)



def window_shortcuts():
    """Enables shortcuts to launch windows."""

    def on_sequence_change(new_config):
        """Update sequences on configuration changes."""
        for key, sequence in sequences.items():
            new_sequence = QKeySequence(new_config['launch_' + key] or None)
            sequence.swap(new_sequence)

        try:
            aqt.mw.form.menuTools.findChild(gui.Action). \
                setShortcut(sequences['configurator'])
        except AttributeError:  # we do not have a config menu
            pass

    on_sequence_change(config)  # set config menu if created before we ran
    config.bind(['launch_' + key for key in sequences.keys()],
                on_sequence_change)
