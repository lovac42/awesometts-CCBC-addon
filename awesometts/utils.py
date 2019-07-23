from anki.utils import isWin, isMac

def getDefaultPreset():
    if isWin:
        sn='sapi5com'
    elif isMac:
        sn='say'
    else:
        sn='festival'
    return {'service':sn}

