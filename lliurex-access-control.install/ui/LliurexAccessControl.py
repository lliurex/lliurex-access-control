#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import N4dManager
import GroupsModel
signal.signal(signal.SIGINT, signal.SIG_DFL)

class LliurexAccessControl(QObject):
	def __init__(self,ticket=None):

		QObject.__init__(self)
		self.n4dMan=N4dManager.N4dManager(ticket)
		self.initBridge()

	#def __init__

	def initBridge(self):

		self._model=GroupsModel.GroupsModel()
		self._settingsChanged=False
		self._showSettingsMessage=[False,"","Success"]
		self._closeGui=False
		self._closePopUp=True
		self._showChangesDialog=False
		self._currentStack=0
		self._currentOptionsStack=0
		self._isAccessDenyGroupEnabled=False
		self.loadConfig()

	#def initBridge

	def loadConfig(self):

		t = threading.Thread(target=self._loadConfig)
		t.daemon=True
		t.start()
	
	#def loadConfig

	def _loadConfig(self):		

		self._isAccessDenyGroupEnabled=self.n4dMan.isAccessDenyGroupEnabled
		self.isAccessDenyGroupEnabled=copy.deepcopy(self.n4dMan.isAccessDenyGroupEnabled)
		self.denyGroups=copy.deepcopy(self.n4dMan.denyGroups)
		self._updateGroupModel()
		time.sleep(2)
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

	def _getIsAccessDenyGroupEnabled(self):

		return self._isAccessDenyGroupEnabled

	#def _getIsAccessDenyGroupEnabled

	def _setIsAccessDenyGroupEnabled(self,isAccessDenyGroupEnabled):

		if self._isAccessDenyGroupEnabled!=isAccessDenyGroupEnabled:
			self._isAccessDenyGroupEnabled=isAccessDenyGroupEnabled
			self.on_isAccessDenyGroupEnabled.emit()

	#def _setIsAccessDenyGroupEnabled

	def _getSettingsChanged(self):

		return self._settingsChanged

	#def _getSettingsChanged

	def _setSettingsChanged(self,settingsChanged):

		if self._settingsChanged!=settingsChanged:
			self._settingsChanged=settingsChanged
			self.on_settingsChanged.emit()

	#def _setSettingsChanged

	def _getShowSettingsMessage(self):

		return self._showSettingsMessage

	#def _getShowSettingsMessage

	def _setShowSettingsMessage(self,showSettingsMessage):

		if self._showSettingsMessage!=showSettingsMessage:
			self._showSettingsMessage=showSettingsMessage
			self.on_showSettingsMessage.emit()

	#def _setShowSettingsMessage

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

	def _getShowChangesDialog(self):

		return self._showChangesDialog

	#def _getShowChangesDialog	

	def _setShowChangesDialog(self,showChangesDialog):
		
		if self._showChangesDialog!=showChangesDialog:
			self._showChangesDialog=showChangesDialog		
			self.on_showChangesDialog.emit()

	#def _setShowChangesDialog

	def _getModel(self):
		
		return self._model

	#def _getModel

	def _updateGroupModel(self):

		ret=self._model.clear()
		self._model=GroupsModel.GroupsModel()
		entries=self.n4dMan.groupsConfigData
		for item in entries:
			self._model.appendRow(item["groupId"],item["isChecked"],item["description"])
		
	#def _updateGroupModel

	@Slot(bool)
	def manageGroupAccessControl(self,value):

		self.showSettingsMessage=[False,"","Success"]
		if value!=self.isAccessDenyGroupEnabled:
			if value!=self.n4dMan.isAccessDenyGroupEnabled:
				self.settingsChanged=True
			else:
				self.settingsChanged=False
			self.isAccessDenyGroupEnabled=value
		else:
			self.settingsChanged=False

	#def manageGroupAccessControl
	
	@Slot('QVariantList')
	def manageGroupChecked(self,value):

		self.showSettingsMessage=[False,"","Success"]
		groupId=value[0]
		groupChecked=value[1]
		tmpGroups=copy.deepcopy(self.denyGroups)

		if groupId not in tmpGroups:
			if groupChecked:
				tmpGroups.append(groupId)
		else:
			if not groupChecked:
				tmpGroups.remove(groupId)

		if len(tmpGroups)==0:
			self.isAccessDenyGroupEnabled=False

		if tmpGroups != self.denyGroups:
			if tmpGroups != self.n4dMan.denyGroups:
				self.settingsChanged=True
			else:
				self.settingsChanged=False
			self.denyGroups=tmpGroups
		else:
			self.settingsChanged=False

	#def manageGroupChecked

	@Slot()
	def applyChanges(self):

		self.showSettingsMessage=[False,"","Success"]
		self.closePopUp=False
		t = threading.Thread(target=self._applyChanges)
		t.daemon=True
		t.start()

	#def applyChanges	

	def _applyChanges(self):

		ret=self.n4dMan.applyChanges(self.isAccessDenyGroupEnabled,self.denyGroups)
		self.closePopUp=True

		if ret[0]:
			self._updateConfig()
			self.showSettingsMessage=[True,ret[1],"Success"]
			self.closeGui=True
		else:
			self.showSettingsMessage=[True,ret[1],"Error"]
			self.closeGui=False

		self.settingsChanged=False
		self.showChangesDialog=False

	#def applyChanges

	@Slot()
	def cancelChanges(self):

		self.showSettingsMessage=[False,"","Success"]
		self.closePopUp=False
		t = threading.Thread(target=self._cancelChanges)
		t.daemon=True
		t.start()

	#def cancelChanges

	def _cancelChanges(self):

		self._updateConfig()
		self.settingsChanged=False
		self.closePopUp=True
		self.showChangesDialog=False
		self.closeGui=True

	#def _cancelChanges

	def _updateConfig(self):

		self.isAccessDenyGroupEnabled=copy.deepcopy(self.n4dMan.isAccessDenyGroupEnabled)
		self.denyGroups=copy.deepcopy(self.n4dMan.denyGroups)
		self._updateGroupModel()
	
	#def_updateConfig

	@Slot(str)
	def manageSettingsDialog(self,action):
		
		if action=="Accept":
			self.applyChanges()
		elif action=="Discard":
			self.cancelChanges()
		elif action=="Cancel":
			self.closeGui=False
			self.showChangesDialog=False

	#def manageSettingsDialog

	@Slot()
	def openHelp(self):
		lang=os.environ["LANG"]
		print(lang)
		if 'valencia' in lang:
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

		if self.settingsChanged:
			self.closeGui=False
			self.showChangesDialog=True
		else:
			self.closeGui=True

	#def closeApplication
	
	on_currentStack=Signal()
	currentStack=Property(int,_getCurrentStack,_setCurrentStack, notify=on_currentStack)
	
	on_currentOptionsStack=Signal()
	currentOptionsStack=Property(int,_getCurrentOptionsStack,_setCurrentOptionsStack, notify=on_currentOptionsStack)

	on_isAccessDenyGroupEnabled=Signal()
	isAccessDenyGroupEnabled=Property(bool,_getIsAccessDenyGroupEnabled,_setIsAccessDenyGroupEnabled,notify=on_isAccessDenyGroupEnabled)
	
	on_settingsChanged=Signal()
	settingsChanged=Property(bool,_getSettingsChanged,_setSettingsChanged, notify=on_settingsChanged)

	on_showSettingsMessage=Signal()
	showSettingsMessage=Property('QVariantList',_getShowSettingsMessage,_setShowSettingsMessage,notify=on_showSettingsMessage)

	on_closePopUp=Signal()
	closePopUp=Property(bool,_getClosePopUp,_setClosePopUp, notify=on_closePopUp)

	on_closeGui=Signal()
	closeGui=Property(bool,_getCloseGui,_setCloseGui, notify=on_closeGui)

	on_showChangesDialog=Signal()
	showChangesDialog=Property(bool,_getShowChangesDialog,_setShowChangesDialog, notify=on_showChangesDialog)

	model=Property(QObject,_getModel,constant=True)


#class LliurexAccessControl

