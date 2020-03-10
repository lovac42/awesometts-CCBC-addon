# -*- coding: utf-8 -*-
# Copyright 2019 Lovac42
# Copyright 2006-2019 Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/CCBC

# imports are all in this file to make moving to pyside easier in the future
# fixme: make sure not to optimize imports on this file

import sip
import os

from anki.utils import isWin, isMac

sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
sip.setapi('QUrl', 2)
try:
    sip.setdestroyonexit(False)
except:
    # missing in older versions
    pass
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui as QtWidgets
from PyQt4.QtWebKit import QWebPage, QWebView, QWebSettings
from PyQt4.QtNetwork import QLocalServer, QLocalSocket
# from anki.lang import _

qtmajor = (QT_VERSION & 0xff0000) >> 16
qtminor = (QT_VERSION & 0x00ff00) >> 8
