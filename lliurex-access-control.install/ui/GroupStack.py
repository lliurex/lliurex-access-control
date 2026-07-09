#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import signal
import copy
import time
import GroupsModel
signal.signal(signal.SIGINT, signal.SIG_DFL)

class UpdateInfo(QThread):

	infoUpdated=Signal(dict)

	def __init__(self,manager,controlEnable,groupsInfo):

		super().__init__()

		self.manager=manager
		self.controlEnable=controlEnable
		self.groupsInfo=groupsInfo

	#def __init__

	def run(self,*args):
		
		time.sleep(1)
		ret=self.manager.applyGroupChanges(self.controlEnable,self.groupsInfo)
		self.infoUpdated.emit(ret)

	#def run

#class UpdateInfo

class Bridge(QObject):

	isGroupAccessControlEnabledChanged=Signal()
	hasGroupChangesChanged=Signal()
	showSettingsGroupMessageChanged=Signal()
	showGroupChangesDialogChanged=Signal()

	def __init__(self):

		super().__init__()
		self.core=Core.Core.get_core()
		self.n4dManager=self.core.n4dManager
		self._groupsModel=GroupsModel.GroupsModel()
		self._hasGroupChanges=False
		self._showSettingsGroupMessage={"show":False,"msgCode":"","type":""}
		self._showGroupChangesDialog=False
		self._isGroupAccessControlEnabled=False
	
	#def __init__

	@Property(bool,notify=isGroupAccessControlEnabledChanged)
	def isGroupAccessControlEnabled(self):

		return self._isGroupAccessControlEnabled

	#def isGroupAccessControlEnabled

	@isGroupAccessControlEnabled.setter
	def isGroupAccessControlEnabled(self,isGroupAccessControlEnabled):

		if self._isGroupAccessControlEnabled!=isGroupAccessControlEnabled:
			self._isGroupAccessControlEnabled=isGroupAccessControlEnabled
			self.isGroupAccessControlEnabledChanged.emit()

	#def isGroupAccessControlEnabled

	@Property(bool,notify=hasGroupChangesChanged)
	def hasGroupChanges(self):

		return self._hasGroupChanges

	#def hasGroupChanges

	@hasGroupChanges.setter
	def hasGroupChanges(self,hasGroupChanges):

		if self._hasGroupChanges!=hasGroupChanges:
			self._hasGroupChanges=hasGroupChanges
			self.hasGroupChangesChanged.emit()

	#def hasGroupChanges

	@Property(dict,notify=showSettingsGroupMessageChanged)
	def showSettingsGroupMessage(self):

		return self._showSettingsGroupMessage

	#def showSettingsGroupMessage

	@showSettingsGroupMessage.setter
	def showSettingsGroupMessage(self,showSettingsGroupMessage):

		if self._showSettingsGroupMessage!=showSettingsGroupMessage:
			self._showSettingsGroupMessage=showSettingsGroupMessage
			self.showSettingsGroupMessageChanged.emit()

	#def showSettingsGroupMessage

	@Property(bool,notify=showGroupChangesDialogChanged)
	def showGroupChangesDialog(self):

		return self._showGroupChangesDialog

	#def showGroupChangesDialog	

	@showGroupChangesDialog.setter
	def showGroupChangesDialog(self,showGroupChangesDialog):
		
		if self._showGroupChangesDialog!=showGroupChangesDialog:
			self._showGroupChangesDialog=showGroupChangesDialog		
			self.showGroupChangesDialogChanged.emit()

	#def showGroupChangesDialog

	@Property(QObject,constant=True)
	def groupsModel(self):
		
		return self._groupsModel

	#def groupsModel

	def getGroupConfig(self):

		self.isGroupAccessControlEnabled=self.n4dManager.isGroupAccessControlEnabled
		self.groupsInfo=copy.deepcopy(self.n4dManager.groupsInfo)
		self._updateGroupModel()
	
	#def getGroupConfig
	
	def _updateGroupModel(self):

		ret=self._groupsModel.clear()
		groupsEntries=self.n4dManager.groupsConfigData
		for item in groupsEntries:
			self._groupsModel.appendRow(item["groupId"],item["isLocked"],item["description"])
		
	#def _updateGroupModel

	@Slot(bool)
	def manageGroupAccessControl(self,value):

		self.showSettingsGroupMessage={"show":False,"msgCode":"","type":""}
		
		if value!=self.isGroupAccessControlEnabled:
			self.isGroupAccessControlEnabled=value
			self.hasGroupChanges=(self.isGroupAccessControlEnabled!=self.n4dManager.isGroupAccessControlEnabled)
						
	#def manageGroupAccessControl

	@Slot(dict)
	def manageGroupChecked(self,value):

		self.showSettingsGroupMessage={"show":False,"msgCode":"","type":""}
		groupId=value.get("groupId")
		groupChecked=value.get("isLocked")
		
		if self.groupsInfo.get(groupId,{}).get("isLocked")!=groupChecked:
			self.groupsInfo[groupId]["isLocked"]=groupChecked
			
			self.hasGroupChanges=(self.groupsInfo!= self.n4dManager.groupsInfo)
				
		if not self.n4dManager.thereAreGroupsLocked(self.groupsInfo):
			self.isGroupAccessControlEnabled=False	 
		
	#def manageGroupChecked

	@Slot()
	def applyGroupChanges(self):

		self.showSettingsGroupMessage={"show":False,"msgCode":"","type":""}
		self.showGroupChangesDialog=False
		self.core.mainStack.closePopUp=False
		self.core.mainStack.closeGui=False
		self.updateInfoGroupsT=UpdateInfo(self.n4dManager,self.isGroupAccessControlEnabled,self.groupsInfo)
		self.updateInfoGroupsT.start()
		self.updateInfoGroupsT.infoUpdated.connect(self._applyGroupChanges)
		self.updateInfoGroupsT.finished.connect(self.updateInfoGroupsT.deleteLater)

	#def applyGroupChanges	

	@Slot(dict)
	def _applyGroupChanges(self,ret):

		if ret.get("status"):
			self._updateGroupConfig()
			self.core.mainStack.closeGui=True
		else:
			self.core.mainStack.closeGui=False
			self.core.mainStack.moveToStack=""

		self.showSettingsGroupMessage={"show":True,"msgCode":ret.get("code"),"type":ret.get("type")}

		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
			self.showSettingsGroupMessage={"show":False,"msgCode":"","type":""}
			self.core.mainStack.moveToStack=""

		self.hasGroupChanges=False
		self.core.mainStack.closePopUp=True

	#def _applyGroupChanges

	@Slot()
	def cancelGroupChanges(self):

		self.showSettingsGroupMessage={"show":False,"msgCode":"","type":""}
		self.core.mainStack.closePopUp=False
		self.core.mainStack.closeGui=False
		self.showGroupChangesDialog=False
		self._cancelGroupChanges()

	#def cancelGroupChanges

	def _cancelGroupChanges(self):

		self._updateGroupConfig()
		self.hasGroupChanges=False

		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
		self.core.mainStack.moveToStack=""

		self.core.mainStack.closePopUp=True
		self.core.mainStack.closeGui=True

	#def _cancelGroupChanges

	def _updateGroupConfig(self):

		self.isGroupAccessControlEnabled=copy.deepcopy(self.n4dManager.isGroupAccessControlEnabled)
		self.groupsInfo=copy.deepcopy(self.n4dManager.groupsInfo)
		self._updateGroupModel()
	
	#def _updateGroupConfig
	
#class Bridge

import Core

