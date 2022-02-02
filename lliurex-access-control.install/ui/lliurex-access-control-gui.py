#!/usr/bin/python3

from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QUrl
from PySide2.QtGui import QIcon
from PySide2.QtQml import QQmlApplicationEngine

import sys
import LliurexAccessControl

app = QApplication()
engine = QQmlApplicationEngine()
engine.clearComponentCache()
context=engine.rootContext()
accessControlBridge=LliurexAccessControl.LliurexAccessControl(sys.argv[1])
context.setContextProperty("accessControlBridge", accessControlBridge)

url = QUrl("/usr/share/lliurex-access-control/rsrc/lliurex-access-control.qml")

engine.load(url)
if not engine.rootObjects():
	sys.exit(-1)

engine.quit.connect(QApplication.quit)
app.setWindowIcon(QIcon("/usr/share/icons/hicolor/scalable/apps/lliurex-access-control.svg"));
ret=app.exec_()
del engine
del app
sys.exit(ret)

