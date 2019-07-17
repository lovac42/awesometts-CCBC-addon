# -*- coding: utf-8 -*-
# Copyright (C) 2019 Lovac42
# Copyright (C) 2010-2018 Anki AwesomeTTS Development Team
# Support: https://github.com/lovac42/awesometts-CCBC-addon
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import aqt, os
from re import compile as re
from PyQt4 import QtCore, QtGui as QtWidgets, QtGui
from PyQt4.QtWebKit import QWebView

from awesometts.paths import ICONS
from awesometts.gui.common import Label
from awesometts.gui.generator import EditorGenerator
from awesometts.shared_loads import addon


ICON_FILE = ICONS+"/awesomo.png"
ICON = QtGui.QIcon(ICON_FILE)


class FakeEditor:
    def __init__(self):
        self.web = QWebView()


class AppGenerator(EditorGenerator):
    """
    Provides a Standalone program for adding media files.
    """

    def __init__(self, *args, **kwargs):
        self._editor = FakeEditor()

        super(EditorGenerator, self).__init__(
            title="A.W.E.S.O.M.-O 4000",
            addon=addon,
            alerts=aqt.utils.showWarning,
            ask=aqt.utils.getText,
            parent=None,
            *args, **kwargs
        )

        self.setWindowIcon(ICON)
        self.setWindowTitle("AWESOM-O")


    # UI Construction ########################################################

    def _ui_buttons(self):
        """
        Adjust title of the OK button.
        """
        buttons = super(AppGenerator, self)._ui_buttons()
        buttons.findChild(QtWidgets.QAbstractButton, 'okay').setText("&Save")
        buttons.findChild(QtWidgets.QAbstractButton, 'cancel').setText("&Exit")
        return buttons


    # Events #################################################################

    def accept(self):
        # now = self._get_all()
        # text_input, text_value = self._get_service_text()

        self._alerts(
            """This feature has not been implemented, 
please use the .cache folder and 
manually copy/move the file.""",
            self,
        )
