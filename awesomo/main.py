# -*- coding: utf-8 -*-
# Copyright (C) 2019 Lovac42
# Support: https://github.com/lovac42/awesometts-CCBC-addon
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import sys
from PyQt4 import QtGui
from awesomo.launcher import Launcher

def launch(path):
    app = QtGui.QApplication(sys.argv)
    launcher=Launcher()
    launcher.setPaths(path)
    launcher.show()
    sys.exit(app.exec_())
