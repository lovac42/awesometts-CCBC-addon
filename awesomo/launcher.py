# -*- coding: utf-8 -*-
# Copyright (C) 2019 Lovac42
# Support: https://github.com/lovac42/awesometts-CCBC-addon
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import sys, os
from PyQt4 import QtGui


class Launcher(QtGui.QWidget):
    def __init__(self):
        super(Launcher, self).__init__()

    def setPaths(self, path):
        from awesometts import paths
        EXEC_DIR=os.path.dirname(os.path.abspath(path))
        paths.ADDON_IS_LINKED = os.path.islink(EXEC_DIR)
        paths.CONFIG = os.path.join(EXEC_DIR, 'config.db')
        CACHE=os.path.join(EXEC_DIR, '.cache')
        if not os.path.isdir(CACHE):
            os.mkdir(CACHE)
        paths.CACHE=CACHE
        paths.ADDON=EXEC_DIR

    def show(self):
        from awesomo import gui
        tts=gui.AppGenerator()
        tts.show()
