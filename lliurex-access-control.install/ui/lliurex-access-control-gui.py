#!/usr/bin/python3

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QUrl
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine

import sys
import Core
c=Core.Core.get_core()

app = QApplication()
engine = QQmlApplicationEngine()
engine.clearComponentCache()
context=engine.rootContext()
mainStackBridge=c.mainStack
groupStackBridge=c.groupStack
userStackBridge=c.userStack
cdcStackBridge=c.cdcStack
context.setContextProperty("mainStackBridge", mainStackBridge)
context.setContextProperty("groupStackBridge", groupStackBridge)
context.setContextProperty("userStackBridge", userStackBridge)
context.setContextProperty("cdcStackBridge", cdcStackBridge)


url = QUrl("/usr/share/lliurex-access-control/rsrc/lliurex-access-control.qml")

engine.load(url)
if not engine.rootObjects():
	sys.exit(-1)

engine.quit.connect(QApplication.quit)
app.setWindowIcon(QIcon("/usr/share/icons/hicolor/scalable/apps/lliurex-access-control.svg"));
ret=app.exec()
del engine
del app
sys.exit(ret)

