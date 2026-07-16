#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex,QUrl
from PySide2.QtGui import QDesktopServices
import os
import signal
import time
import sys

signal.signal(signal.SIGINT, signal.SIG_DFL)

class GatherInfo(QThread):

	infoGathered=Signal()

	def __init__(self,manager):

		super().__init__()
		self.manager=manager
	
	#def __init__
	
	def run(self,*args):
		
		time.sleep(1)
		self.manager.loadConfig()
		self.infoGathered.emit()

	#def run

#class GatherInfo

class Bridge(QObject):

	SAVE_DATA_MSG=30
	RESTORE_DATA_MSG=31

	currentStackChanged=Signal()
	currentOptionsStackChanged=Signal()
	showPopUpChanged=Signal()
	closeGuiChanged=Signal()

	def __init__(self):

		super().__init__()
		self.core=Core.Core.get_core()
		self.n4dManager=self.core.n4dManager
		self._closeGui=False
		self._showPopUp={"show":False,"msgCode":""}
		self._currentStack=0
		self._currentOptionsStack=0
		self.moveToStack=""
		self.n4dManager.setServer(sys.argv[1])

	#def __init__

	@Property(int,notify=currentStackChanged)
	def currentStack(self):

		return self._currentStack

	#def currentStack

	@currentStack.setter
	def currentStack(self,currentStack):

		if self._currentStack!=currentStack:
			self._currentStack=currentStack
			self.currentStackChanged.emit()

	#def currentStack

	@Property(int,notify=currentOptionsStackChanged)
	def currentOptionsStack(self):

		return self._currentOptionsStack

	#def currentOptionsStack

	@currentOptionsStack.setter
	def currentOptionsStack(self,currentOptionsStack):

		if self._currentOptionsStack!=currentOptionsStack:
			self._currentOptionsStack=currentOptionsStack
			self.currentOptionsStackChanged.emit()

	#def currentOptionsStack

	@Property('QVariant',notify=showPopUpChanged)
	def showPopUp(self):

		return self._showPopUp

	#def showPopUp

	@showPopUp.setter
	def showPopUp(self,showPopUp):

		if self._showPopUp!=showPopUp:
			self._showPopUp=showPopUp
			self.showPopUpChanged.emit()

	#def showPopUp

	@Property(bool,notify=closeGuiChanged)
	def closeGui(self):

		return self._closeGui

	#def closeGui	

	@closeGui.setter
	def closeGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui		
			self.closeGuiChanged.emit()

	#def closeGui	

	def initBridge(self):

		self.gatherInfoT=GatherInfo(self.n4dManager)
		self.gatherInfoT.start()
		self.gatherInfoT.infoGathered.connect(self._loadConfig)
		self.gatherInfoT.finished.connect(self.gatherInfoT.deleteLater)

	#def initBridge

	@Slot()
	def _loadConfig(self):		

		self.core.groupStack.getGroupConfig()
		self.core.userStack.getUserConfig()
		self.core.cdcStack.getCDCConfig()
		self.currentStack=1

	#def _loadConfig

	@Slot(int)
	def manageTransitions(self,stack):

		if self.currentOptionsStack!=stack:
			self.moveToStack=stack
			if self.core.groupStack.hasGroupChanges:
				self.core.groupStack.showGroupChangesDialog=True
			elif self.core.userStack.hasUserChanges:
				self.core.userStack.showUserChangesDialog=True
			elif self.core.cdcStack.hasCDCChanges:
				self.core.cdcStack.showCDCChangesDialog=True
			else:
				self.currentOptionsStack=stack
				self.moveToStack=""
	
	#def manageTransitions
	
	@Slot(str)
	def manageSettingsDialog(self,action):
		
		if action=="Accept":
			if self.core.groupStack.hasGroupChanges:
				self.core.groupStack.applyGroupChanges()
			elif self.core.userStack.hasUserChanges:
				self.core.userStack.applyUserChanges()
			elif self.core.cdcStack.hasCDCChanges:
				self.core.cdcStack.applyCDCChanges()
		elif action=="Discard":
			if self.core.groupStack.hasGroupChanges:
				self.core.groupStack.cancelGroupChanges()
			elif self.core.userStack.hasUserChanges:
				self.core.userStack.cancelUserChanges()
			elif self.core.cdcStack.hasCDCChanges:
				self.core.cdcStack.cancelCDCChanges()
		elif action=="Cancel":
			self.closeGui=False
			if self.core.groupStack.hasGroupChanges:
				self.core.groupStack.showGroupChangesDialog=False
			elif self.core.userStack.hasUserChanges:
				self.core.userStack.showUserChangesDialog=False
			elif self.core.cdcStack.hasCDCChanges:
				self.core.cdcStack.showCDCChangesDialog=False
			self.moveToStack=""

	#def manageSettingsDialog
	
	@Slot()
	def openHelp(self):

		helpUrl='https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Lliurex-Access-Control'
		QDesktopServices.openUrl(QUrl(helpUrl))

	#def openHelp

	@Slot()
	def closeApplication(self):

		self.closeGui=False
		if self.core.groupStack.hasGroupChanges:
			self.core.groupStack.showGroupChangesDialog=True
		elif self.core.userStack.hasUserChanges:
			self.core.userStack.showUserChangesDialog=True
		elif self.core.cdcStack.hasCDCChanges:
			self.core.cdcStack.showCDCChangesDialog=True
		else:
			self.closeGui=True
			self.n4dManager.writeLog("Close Session")

	#def closeApplication
	
#class Bridge

import Core

