#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys

signal.signal(signal.SIGINT, signal.SIG_DFL)

class GatherInfo(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
	
	#def __init__
		

	def run(self,*args):
		
		time.sleep(1)
		self.manager=Bridge.n4dMan.loadConfig()

	#def run

#class GatherInfo

class Bridge(QObject):


	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.n4dMan=self.core.n4dManager
		self._closeGui=False
		self._closePopUp=True
		self._currentStack=0
		self._currentOptionsStack=0
		self.moveToStack=""
		Bridge.n4dMan.setServer(sys.argv[1])

	#def __init__

	def initBridge(self):

		self.gatherInfo=GatherInfo()
		self.gatherInfo.start()
		self.gatherInfo.finished.connect(self._loadConfig)

	#def initBridge

	def _loadConfig(self):		

		self.core.groupStack.getGroupConfig()
		self.core.userStack.getUserConfig()
		self.core.cdcStack.getCDCConfig()
		self.currentStack=1

	#def _loadConfig

	def _getCurrentStack(self):

		return self._currentStack

	#def _getCurrentStack

	def _setCurrentStack(self,currentStack):

		if self._currentStack!=currentStack:
			self._currentStack=currentStack
			self.on_currentStack.emit()

	#def _setCurrentStack

	def _getCurrentOptionsStack(self):

		return self._currentOptionsStack

	#def _getCurrentOptionsStack

	def _setCurrentOptionsStack(self,currentOptionsStack):

		if self._currentOptionsStack!=currentOptionsStack:
			self._currentOptionsStack=currentOptionsStack
			self.on_currentOptionsStack.emit()

	#def _setCurrentOptionsStack

	
	def _getClosePopUp(self):

		return self._closePopUp

	#def _getClosePopUp

	def _setClosePopUp(self,closePopUp):
		
		if self._closePopUp!=closePopUp:
			self._closePopUp=closePopUp		
			self.on_closePopUp.emit()

	#def _setClosePopUp		

	def _getCloseGui(self):

		return self._closeGui

	#def _getCloseGui	

	def _setCloseGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui		
			self.on_closeGui.emit()

	#def _setCloseGui	

	@Slot(int)
	def manageTransitions(self,stack):

		if self.currentOptionsStack!=stack:
			self.moveToStack=stack
			if self.core.groupStack.settingsGroupChanged:
				self.core.groupStack.showGroupChangesDialog=True
			elif self.core.userStack.settingsUserChanged:
				self.core.userStack.showUserChangesDialog=True
			elif self.core.cdcStack.settingsCDCChanged:
				self.core.cdcStack.showCDCChangesDialog=True
			else:
				self.currentOptionsStack=stack
				self.moveToStack=""
	
	#def manageTransitions
	
	@Slot(str)
	def manageSettingsDialog(self,action):
		
		if action=="Accept":
			if self.core.groupStack.settingsGroupChanged:
				self.core.groupStack.applyGroupChanges()
			elif self.core.userStack.settingsUserChanged:
				self.core.userStack.applyUserChanges()
			elif self.core.cdcStack.settingsCDCChanged:
				self.core.cdcStack.applyCDCChanges()
		elif action=="Discard":
			if self.core.groupStack.settingsGroupChanged:
				self.core.groupStack.cancelGroupChanges()
			elif self.core.userStack.settingsUserChanged:
				self.core.userStack.cancelUserChanges()
			elif self.core.cdcStack.settingsCDCChanged:
				self.core.cdcStack.cancelCDCChanges()
		elif action=="Cancel":
			self.closeGui=False
			if self.core.groupStack.settingsGroupChanged:
				self.core.groupStack.showGroupChangesDialog=False
			elif self.core.userStack.settingsUserChanged:
				self.core.userStack.showUserChangesDialog=False
			elif self.core.cdcStack.settingsCDCChanged:
				self.core.cdcStack.showCDCChangesDialog=False
			self.moveToStack=""

	#def manageSettingsDialog
	
	@Slot()
	def openHelp(self):
		
		if 'valencia' in self.n4dMan.sessionLang:
			self.help_cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Lliurex-Access-Control.'
		else:
			self.help_cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Lliurex-Access-Control'
		
		self.open_help_t=threading.Thread(target=self._openHelp)
		self.open_help_t.daemon=True
		self.open_help_t.start()

	#def openHelp

	def _openHelp(self):

		os.system(self.help_cmd)

	#def _openHelp

	@Slot()
	def closeApplication(self):

		self.closeGui=False
		if self.core.groupStack.settingsGroupChanged:
			self.core.groupStack.showGroupChangesDialog=True
		elif self.core.userStack.settingsUserChanged:
			self.core.userStack.showUserChangesDialog=True
		elif self.core.cdcStack.settingsCDCChanged:
			self.core.cdcStack.showCDCChangesDialog=True
		else:
			self.closeGui=True
			Bridge.n4dMan.writeLog("Close Session")

	#def closeApplication
	
	on_currentStack=Signal()
	currentStack=Property(int,_getCurrentStack,_setCurrentStack, notify=on_currentStack)
	
	on_currentOptionsStack=Signal()
	currentOptionsStack=Property(int,_getCurrentOptionsStack,_setCurrentOptionsStack, notify=on_currentOptionsStack)

	on_closePopUp=Signal()
	closePopUp=Property(bool,_getClosePopUp,_setClosePopUp, notify=on_closePopUp)

	on_closeGui=Signal()
	closeGui=Property(bool,_getCloseGui,_setCloseGui, notify=on_closeGui)

#class Bridge

import Core

