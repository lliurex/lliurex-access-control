#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import GroupsModel
signal.signal(signal.SIGINT, signal.SIG_DFL)

class UpdateInfo(QThread):

	def __init__(self,*args):

		QThread.__init__(self)

		self.enabledInfo=args[0]
		self.listInfo=args[1]
		self.ret=[]

	#def __init__

	def run(self,*args):
		
		time.sleep(1)
		self.ret=Bridge.n4dMan.applyGroupChanges(self.enabledInfo,self.listInfo)

	#def run

#class UpdateInfo

class Bridge(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.n4dMan=self.core.n4dManager
		self._groupsModel=GroupsModel.GroupsModel()
		self._settingsGroupChanged=False
		self._showSettingsGroupMessage=[False,"","Success"]
		self._showGroupChangesDialog=False
		self._isAccessDenyGroupEnabled=False
	
	#def __init__

	def getGroupConfig(self):

		self.isAccessDenyGroupEnabled=copy.deepcopy(Bridge.n4dMan.isAccessDenyGroupEnabled)
		self.groupsInfo=copy.deepcopy(Bridge.n4dMan.groupsInfo)
		self._updateGroupModel()
	
	#def getGroupConfig

	def _getIsAccessDenyGroupEnabled(self):

		return self._isAccessDenyGroupEnabled

	#def _getIsAccessDenyGroupEnabled

	def _setIsAccessDenyGroupEnabled(self,isAccessDenyGroupEnabled):

		if self._isAccessDenyGroupEnabled!=isAccessDenyGroupEnabled:
			self._isAccessDenyGroupEnabled=isAccessDenyGroupEnabled
			self.on_isAccessDenyGroupEnabled.emit()

	#def _setIsAccessDenyGroupEnabled

	def _getSettingsGroupChanged(self):

		return self._settingsGroupChanged

	#def _getSettingsGroupChanged

	def _setSettingsGroupChanged(self,settingsGroupChanged):

		if self._settingsGroupChanged!=settingsGroupChanged:
			self._settingsGroupChanged=settingsGroupChanged
			self.on_settingsGroupChanged.emit()

	#def _setSettingsGroupChanged

	def _getShowSettingsGroupMessage(self):

		return self._showSettingsGroupMessage

	#def _getShowSettingsGroupMessage

	def _setShowSettingsGroupMessage(self,showSettingsGroupMessage):

		if self._showSettingsGroupMessage!=showSettingsGroupMessage:
			self._showSettingsGroupMessage=showSettingsGroupMessage
			self.on_showSettingsGroupMessage.emit()

	def _getShowGroupChangesDialog(self):

		return self._showGroupChangesDialog

	#def _getShowGroupChangesDialog	

	def _setShowGroupChangesDialog(self,showGroupChangesDialog):
		
		if self._showGroupChangesDialog!=showGroupChangesDialog:
			self._showGroupChangesDialog=showGroupChangesDialog		
			self.on_showGroupChangesDialog.emit()

	#def _setShowGroupChangesDialog

	def _getGroupsModel(self):
		
		return self._groupsModel

	#def _getGroupsModel

	def _updateGroupModel(self):

		ret=self._groupsModel.clear()
		groupsEntries=Bridge.n4dMan.groupsConfigData
		for item in groupsEntries:
			self._groupsModel.appendRow(item["groupId"],item["isLocked"],item["description"])
		
	#def _updateGroupModel

	@Slot(bool)
	def manageGroupAccessControl(self,value):

		self.showSettingsGroupMessage=[False,"","Success"]
		
		if value!=self.isAccessDenyGroupEnabled:
			self.isAccessDenyGroupEnabled=value
			if self.isAccessDenyGroupEnabled!=Bridge.n4dMan.isAccessDenyGroupEnabled:
				self.settingsGroupChanged=True
			else:
				self.settingsGroupChanged=False
					
	#def manageGroupAccessControl

	@Slot('QVariantList')
	def manageGroupChecked(self,value):

		self.showSettingsGroupMessage=[False,"","Success"]
		groupId=value[0]
		groupChecked=value[1]
		thereAreGroupLocked=False
		
		if self.groupsInfo[groupId]["isLocked"]!=groupChecked:
			self.groupsInfo[groupId]["isLocked"]=groupChecked
			if self.groupsInfo!=Bridge.n4dMan.groupsInfo:
				self.settingsGroupChanged=True
			else:
				self.settingsGroupChanged=False
			
		if not Bridge.n4dMan.thereAreGroupsLocked(self.groupsInfo):
			self.isAccessDenyGroupEnabled=False	 
		
	#def manageGroupChecked

	@Slot()
	def applyGroupChanges(self):

		self.showSettingsGroupMessage=[False,"","Success"]
		self.core.mainStack.closePopUp=False
		self.showGroupChangesDialog=False
		self.updateInfoGroups=UpdateInfo(self.isAccessDenyGroupEnabled,self.groupsInfo)
		self.updateInfoGroups.start()
		self.updateInfoGroups.finished.connect(self._applyGroupChanges)

	#def applyGroupChanges	

	def _applyGroupChanges(self):

		#self.updateGroupInfo.ret=Bridge.n4dMan.applyGroupChanges(self.isAccessDenyGroupEnabled,self.groupsInfo)

		if self.updateInfoGroups.ret[0]:
			self._updateGroupConfig()
			self.showSettingsGroupMessage=[True,self.updateInfoGroups.ret[1],"Success"]
			self.core.mainStack.closeGui=True
		else:
			self.showSettingsGroupMessage=[True,self.updateInfoGroups.ret[1],"Error"]
			self.core.mainStack.closeGui=False
			self.core.mainStack.moveToStack=""

		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
			self.showSettingsGroupMessage=[False,"","Info"]
			self.core.mainStack.moveToStack=""

		self.settingsGroupChanged=False
		self.core.mainStack.closePopUp=True

	#def _applyGroupChanges

	@Slot()
	def cancelGroupChanges(self):

		self.showSettingsGroupMessage=[False,"","Success"]
		self.core.mainStack.closePopUp=False
		self.showGroupChangesDialog=False
		self._cancelGroupChanges()

	#def cancelGroupChanges

	def _cancelGroupChanges(self):

		self._updateGroupConfig()
		self.settingsGroupChanged=False
		self.core.mainStack.closePopUp=True
		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
		self.core.mainStack.moveToStack=""

		self.core.mainStack.closeGui=True

	#def _cancelGroupChanges

	def _updateGroupConfig(self):

		self.isAccessDenyGroupEnabled=copy.deepcopy(Bridge.n4dMan.isAccessDenyGroupEnabled)
		self.groupsInfo=copy.deepcopy(Bridge.n4dMan.groupsInfo)
		self._updateGroupModel()
	
	#def _updateGroupConfig
	
	on_isAccessDenyGroupEnabled=Signal()
	isAccessDenyGroupEnabled=Property(bool,_getIsAccessDenyGroupEnabled,_setIsAccessDenyGroupEnabled,notify=on_isAccessDenyGroupEnabled)
	
	on_settingsGroupChanged=Signal()
	settingsGroupChanged=Property(bool,_getSettingsGroupChanged,_setSettingsGroupChanged, notify=on_settingsGroupChanged)

	on_showSettingsGroupMessage=Signal()
	showSettingsGroupMessage=Property('QVariantList',_getShowSettingsGroupMessage,_setShowSettingsGroupMessage,notify=on_showSettingsGroupMessage)

	on_showGroupChangesDialog=Signal()
	showGroupChangesDialog=Property(bool,_getShowGroupChangesDialog,_setShowGroupChangesDialog, notify=on_showGroupChangesDialog)

	groupsModel=Property(QObject,_getGroupsModel,constant=True)

#class Bridge

import Core

