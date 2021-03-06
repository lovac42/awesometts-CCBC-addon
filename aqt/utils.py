# -*- coding: utf-8 -*-
# Copyright 2019 Lovac42
# Copyright 2006-2019 Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/CCBC

from aqt.qt import *
import aqt, re, os, sys, subprocess
import urllib.request, urllib.parse, urllib.error
from anki.sound import stripSounds
from anki.utils import isWin, isMac, invalidFilename, noBundledLibs, platDesc, versionWithBuild
# from anki.lang import _


def openHelp(section):
    pass

def openLink(link):
    tooltip(_("Loading..."), period=1000)
    QDesktopServices.openUrl(QUrl(link))

def showWarning(text, parent=None, help="", title="Anki", textFormat=None):
    "Show a small warning with an OK button."
    return showInfo(text, parent, help, "warning", title=title, textFormat=textFormat)

def showCritical(text, parent=None, help="", title="Anki", textFormat=None):
    "Show a small critical error with an OK button."
    return showInfo(text, parent, help, "critical", title=title, textFormat=textFormat)

def showInfo(text, parent=False, help="", type="info", title="Anki", textFormat=None):
    "Show a small info window with an OK button."
    if parent is False:
        parent = aqt.mw.app.activeWindow() or aqt.mw
    if type == "warning":
        icon = QMessageBox.Warning
    elif type == "critical":
        icon = QMessageBox.Critical
    else:
        icon = QMessageBox.Information
    mb = QMessageBox(parent)
    if textFormat == "plain":
        mb.setTextFormat(Qt.PlainText)
    elif textFormat == "rich":
        mb.setTextFormat(Qt.RichText)
    elif textFormat is not None:
        raise Exception("unexpected textFormat type")
    mb.setText(text)
    mb.setIcon(icon)
    mb.setWindowTitle(title)
    b = mb.addButton(QMessageBox.Ok)
    b.setDefault(True)
    if help:
        b = mb.addButton(QMessageBox.Help)
        b.clicked.connect(lambda: openHelp(help))
        b.setAutoDefault(False)
    return mb.exec_()

def showText(txt, parent=None, type="text", run=True, geomKey=None, \
        minWidth=500, minHeight=400, title="Anki", copyBtn=False):
    if not parent:
        parent = aqt.mw.app.activeWindow() or aqt.mw
    diag = QDialog(parent)
    diag.setWindowTitle(title)
    layout = QVBoxLayout(diag)
    diag.setLayout(layout)
    text = QTextBrowser()
    text.setOpenExternalLinks(True)
    if type == "text":
        text.setPlainText(txt)
    else:
        text.setHtml(txt)
    layout.addWidget(text)
    box = QDialogButtonBox(QDialogButtonBox.Close)
    layout.addWidget(box)
    if copyBtn:
        def onCopy():
            QApplication.clipboard().setText(text.toPlainText())
        btn = QPushButton(_("Copy to Clipboard"))
        btn.clicked.connect(onCopy)
        box.addButton(btn, QDialogButtonBox.ActionRole)
    def onReject():
        if geomKey:
            saveGeom(diag, geomKey)
        QDialog.reject(diag)
    box.rejected.connect(onReject)
    def onFinish():
        if geomKey:
            saveGeom(diag, geomKey)
    box.accepted.connect(onFinish)
    diag.setMinimumHeight(minHeight)
    diag.setMinimumWidth(minWidth)
    if geomKey:
        restoreGeom(diag, geomKey)
    if run:
        diag.exec_()
    else:
        return diag, box

def askUser(text, parent=None, help="", defaultno=False, msgfunc=None, title="Anki"):
    "Show a yes/no question. Return true if yes."
    if not parent:
        parent = aqt.mw.app.activeWindow()
    if not msgfunc:
        msgfunc = QMessageBox.question
    sb = QMessageBox.Yes | QMessageBox.No
    while 1:
        if defaultno:
            default = QMessageBox.No
        else:
            default = QMessageBox.Yes

        r = msgfunc(parent, title, text, sb, default)
        if r == QMessageBox.Help:
            pass
        else:
            break
    return r == QMessageBox.Yes

class ButtonedDialog(QMessageBox):

    def __init__(self, text, buttons, parent=None, help="", title="Anki"):
        QDialog.__init__(self, parent)
        self.buttons = []
        self.setWindowTitle(title)
        self.setIcon(QMessageBox.Warning)
        self.setText(text)
        for b in buttons:
            self.buttons.append(
                self.addButton(b, QMessageBox.AcceptRole))

    def run(self):
        self.exec_()
        but = self.clickedButton().text()
        return self.clickedButton().text()

    def setDefault(self, idx):
        self.setDefaultButton(self.buttons[idx])

def askUserDialog(text, buttons, parent=None, help="", title="Anki"):
    if not parent:
        parent = aqt.mw
    diag = ButtonedDialog(text, buttons, parent, help, title=title)
    return diag

class GetTextDialog(QDialog):

    def __init__(self, parent, question, help=None, edit=None, default=u"", \
                 title="Anki", minWidth=400):
        QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        self.question = question
        self.qlabel = QLabel(question)
        self.setMinimumWidth(minWidth)
        v = QVBoxLayout()
        v.addWidget(self.qlabel)
        if not edit:
            edit = QLineEdit()
        self.l = edit
        if default:
            self.l.setText(default)
            self.l.selectAll()
        v.addWidget(self.l)
        buts = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        b = QDialogButtonBox(buts)
        v.addWidget(b)
        self.setLayout(v)
        b.button(QDialogButtonBox.Ok).clicked.connect(self.accept)
        b.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)

    def accept(self):
        return QDialog.accept(self)

    def reject(self):
        return QDialog.reject(self)

    def helpRequested(self):
        pass

def getText(prompt, parent=None, help=None, edit=None, default=u"", title="Anki"):
    if not parent:
        parent = aqt.mw.app.activeWindow() or aqt.mw
    d = GetTextDialog(parent, prompt, help=help, edit=edit,
                      default=default, title=title)
    d.setWindowModality(Qt.WindowModal)
    ret = d.exec_()
    return (d.l.text(), ret)

def getOnlyText(*args, **kwargs):
    (s, r) = getText(*args, **kwargs)
    if r:
        return s
    else:
        return u""

# fixme: these utilities could be combined into a single base class
def chooseList(prompt, choices, startrow=0, parent=None):
    if not parent:
        parent = aqt.mw.app.activeWindow()
    d = QDialog(parent)
    d.setWindowModality(Qt.WindowModal)
    l = QVBoxLayout()
    d.setLayout(l)
    t = QLabel(prompt)
    l.addWidget(t)
    c = QListWidget()
    c.addItems(choices)
    c.setCurrentRow(startrow)
    l.addWidget(c)
    bb = QDialogButtonBox(QDialogButtonBox.Ok)
    bb.accepted.connect(d.accept)
    l.addWidget(bb)
    d.exec_()
    return c.currentRow()

def getTag(parent, deck, question, tags="user", **kwargs):
    from aqt.tagedit import TagEdit
    te = TagEdit(parent)
    te.setCol(deck)
    ret = getText(question, parent, edit=te, **kwargs)
    te.hideCompleter()
    return ret

# File handling
######################################################################

def getFile(parent, title, cb, filter="*.*", dir=None, key=None, multi=False):
    "Ask the user for a file."
    assert not dir or not key
    if not dir:
        dirkey = key+"Directory"
        dir = aqt.mw.pm.profile.get(dirkey, "")
    else:
        dirkey = None
    d = QFileDialog(parent)
    mode = QFileDialog.ExistingFiles if multi else QFileDialog.ExistingFile
    d.setFileMode(mode)
    if os.path.exists(dir):
        d.setDirectory(dir)
    d.setWindowTitle(title)
    d.setNameFilter(filter)
    ret = []
    def accept():
        files = list(d.selectedFiles())
        if dirkey:
            dir = os.path.dirname(files[0])
            aqt.mw.pm.profile[dirkey] = dir
        result = files if multi else files[0]
        if cb:
            cb(result)
        ret.append(result)
    d.accepted.connect(accept)
    if key:
        restoreState(d, key)
    d.exec_()
    if key:
        saveState(d, key)
    return ret and ret[0]


def getSaveFile(parent, title, dir_description, key, ext, fname=None):
    """Ask the user for a file to save. Use DIR_DESCRIPTION as config
    variable. The file dialog will default to open with FNAME."""
    config_key = dir_description + 'Directory'
    base = aqt.mw.pm.profile.get(config_key, aqt.mw.pm.base)
    path = os.path.join(base, fname)
    file = QFileDialog.getSaveFileName(
        parent, title, path, u"{0} (*{1})".format(key, ext),
        options=QFileDialog.DontConfirmOverwrite)
    if file:
        # add extension
        if not file.lower().endswith(ext):
            file += ext
        # save new default
        dir = os.path.dirname(file)
        aqt.mw.pm.profile[config_key] = dir
        # check if it exists
        if os.path.exists(file):
            if not askUser(
                _("This file exists. Are you sure you want to overwrite it?"),
                parent):
                return None
    return file

def saveGeom(widget, key):
    key += "Geom"
    aqt.mw.pm.profile[key] = widget.saveGeometry()

def restoreGeom(widget, key, offset=None, adjustSize=False):
    key += "Geom"
    if aqt.mw.pm.profile.get(key):
        widget.restoreGeometry(aqt.mw.pm.profile[key])
        if isMac and offset:
            if qtminor > 6:
                # bug in osx toolkit
                s = widget.size()
                widget.resize(s.width(), s.height()+offset*2)
    else:
        if adjustSize:
            widget.adjustSize()

def saveState(widget, key):
    key += "State"
    aqt.mw.pm.profile[key] = widget.saveState()

def restoreState(widget, key):
    key += "State"
    if aqt.mw.pm.profile.get(key):
        widget.restoreState(aqt.mw.pm.profile[key])

def saveSplitter(widget, key):
    key += "Splitter"
    aqt.mw.pm.profile[key] = widget.saveState()

def restoreSplitter(widget, key):
    key += "Splitter"
    if aqt.mw.pm.profile.get(key):
        widget.restoreState(aqt.mw.pm.profile[key])

def saveHeader(widget, key):
    key += "Header"
    aqt.mw.pm.profile[key] = widget.saveState()

def restoreHeader(widget, key):
    key += "Header"
    if aqt.mw.pm.profile.get(key):
        widget.restoreState(aqt.mw.pm.profile[key])

def mungeQA(col, txt):
    txt = col.media.escapeImages(txt)
    txt = stripSounds(txt)
    # osx webkit doesn't understand font weight 600
    txt = re.sub("font-weight: *600", "font-weight:bold", txt)
    if isMac:
        # custom fonts cause crashes on osx at the moment
        txt = txt.replace("font-face", "invalid")

    return txt

def applyStyles(widget):
    p = os.path.join(aqt.mw.pm.base, "style.css")
    if os.path.exists(p):
        widget.setStyleSheet(open(p).read())

def getBase(col):
    base = None
    mdir = col.media.dir()
    if isWin and not mdir.startswith("\\\\"):
        prefix = u"file:///"
    else:
        prefix = u"file://"
    mdir = mdir.replace("\\", "/")
    base = prefix + urllib.parse.quote(mdir) + "/"
    return '<base href="%s">' % base

def openFolder(path):
    if isWin:
        subprocess.Popen(["explorer", "file://"+path])
    else:
        with noBundledLibs():
            QDesktopServices.openUrl(QUrl("file://" + path))

def shortcut(key):
    if isMac:
        return re.sub("(?i)ctrl", "Command", key)
    return key

def maybeHideClose(bbox):
    if isMac:
        b = bbox.button(QDialogButtonBox.Close)
        if b:
            bbox.removeButton(b)

def addCloseShortcut(widg):
    if not isMac:
        return
    widg._closeShortcut = QShortcut(QKeySequence("Ctrl+W"), widg)
    widg._closeShortcut.activated.connect(widg.reject)


def downArrow():
    if isWin:
        return u"▼"
    # windows 10 is lacking the smaller arrow on English installs
    return u"▾"

# Tooltips
######################################################################

_tooltipTimer = None
_tooltipLabel = None

def tooltip(msg, period=3000, parent=None):
    global _tooltipTimer, _tooltipLabel
    class CustomLabel(QLabel):
        def mousePressEvent(self, evt):
            evt.accept()
            self.hide()
    closeTooltip()
    aw = parent or aqt.mw.app.activeWindow() or aqt.mw
    lab = CustomLabel("""\
<table cellpadding=10>
<tr>
<td><img src=":/icons/help-hint.png"></td>
<td>%s</td>
</tr>
</table>""" % msg, aw)
    lab.setFrameStyle(QFrame.Panel)
    lab.setLineWidth(2)
    lab.setWindowFlags(Qt.ToolTip)
    p = QPalette()
    p.setColor(QPalette.Window, QColor("#feffc4"))
    p.setColor(QPalette.WindowText, QColor("#000000"))
    lab.setPalette(p)
    lab.move(
        aw.mapToGlobal(QPoint(0, -100 + aw.height())))
    lab.show()
    _tooltipTimer = aqt.mw.progress.timer(
        period, closeTooltip, False)
    _tooltipLabel = lab

def closeTooltip():
    global _tooltipLabel, _tooltipTimer
    if _tooltipLabel:
        try:
            _tooltipLabel.deleteLater()
        except:
            # already deleted as parent window closed
            pass
        _tooltipLabel = None
    if _tooltipTimer:
        _tooltipTimer.stop()
        _tooltipTimer = None

# true if invalid; print warning
def checkInvalidFilename(str, dirsep=True):
    bad = invalidFilename(str, dirsep)
    if bad:
        showWarning(_("The following character can not be used: %s") %
                    bad)
        return True
    return False



# Menus
######################################################################

class MenuList:
    def __init__(self):
        self.children = []

    def addItem(self, title, func):
        item = MenuItem(title, func)
        self.children.append(item)
        return item

    def addSeparator(self):
        self.children.append(None)

    def addMenu(self, title):
        submenu = SubMenu(title)
        self.children.append(submenu)
        return submenu

    def addChild(self, child):
        self.children.append(child)

    def renderTo(self, qmenu):
        for child in self.children:
            if child is None:
                qmenu.addSeparator()
            elif isinstance(child, QAction):
                qmenu.addAction(child)
            else:
                child.renderTo(qmenu)

    def popupOver(self, widget):
        qmenu = QMenu()
        self.renderTo(qmenu)
        qmenu.exec_(widget.mapToGlobal(QPoint(0,0)))

    # Chunking
    ######################################################################

    chunkSize = 30

    def chunked(self):
        if len(self.children) <= self.chunkSize:
            return self

        newList = MenuList()
        oldItems = self.children[:]
        while oldItems:
            chunk = oldItems[:self.chunkSize]
            del oldItems[:self.chunkSize]
            label = self._chunkLabel(chunk)
            menu = newList.addMenu(label)
            menu.children = chunk
        return newList

    def _chunkLabel(self, items):
        start = items[0].title
        end = items[-1].title
        prefix = os.path.commonprefix([start.upper(), end.upper()])
        n = len(prefix)+1
        return "{}-{}".format(start[:n].upper(), end[:n].upper())

class SubMenu(MenuList):
    def __init__(self, title):
        super().__init__()
        self.title = title

    def renderTo(self, menu):
        submenu = menu.addMenu(self.title)
        super().renderTo(submenu)

class MenuItem:
    def __init__(self, title, func):
        self.title = title
        self.func = func

    def renderTo(self, qmenu):
        a = qmenu.addAction(self.title)
        a.triggered.connect(self.func)

def qtMenuShortcutWorkaround(qmenu):
    if qtminor < 10:
        return
    for act in qmenu.actions():
        act.setShortcutVisibleInContextMenu(True)

######################################################################

def supportText():
    import platform
    from aqt import mw

    if isWin:
        platname = "Windows " + platform.win32_ver()[0]
    elif isMac:
        platname = "Mac " + platform.mac_ver()[0]
    else:
        platname = "Linux"

    def schedVer():
        try:
            return mw.col.schedVer()
        except:
            return "?"

    return """\
Anki {} Python {} Qt {} PyQt {}
Platform: {}
Flags: frz={} ao={} sv={}
""".format(versionWithBuild(), platform.python_version(),
           QT_VERSION_STR, PYQT_VERSION_STR, platname,
           getattr(sys, "frozen", False),
           mw.addonManager.dirty, schedVer())

######################################################################

# adapted from version detection in qutebrowser
def opengl_vendor():
    old_context = QOpenGLContext.currentContext()
    old_surface = None if old_context is None else old_context.surface()

    surface = QOffscreenSurface()
    surface.create()

    ctx = QOpenGLContext()
    ok = ctx.create()
    if not ok:
        return None

    ok = ctx.makeCurrent(surface)
    if not ok:
        return None

    try:
        if ctx.isOpenGLES():
            # Can't use versionFunctions there
            return None

        vp = QOpenGLVersionProfile()
        vp.setVersion(2, 0)

        try:
            vf = ctx.versionFunctions(vp)
        except ImportError as e:
            return None

        if vf is None:
            return None

        return vf.glGetString(vf.GL_VENDOR)
    finally:
        ctx.doneCurrent()
        if old_context and old_surface:
            old_context.makeCurrent(old_surface)

def gfxDriverIsBroken():
    driver = opengl_vendor()
    return driver == "nouveau"
