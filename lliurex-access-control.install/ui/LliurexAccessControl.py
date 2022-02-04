#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import N4dManager
import GroupsModel
import UsersModel
signal.signal(signal.SIGINT, signal.SIG_DFL)

class LliurexAccessControl(QObject):
	def __init__(self,ticket=None):

		QObject.__init__(self)
		self.n4dMan=N4dManager.N4dManager(ticket)
		self.initBridge()

	#def __init__

	def initBridge(self):

		self._groupsModel=GroupsModel.GroupsModel()
		self._usersModel=UsersModel.UsersModel()
		self._settingsGroupChanged=False
		self._showSettingsGroupMessage=[False,"","Success"]
		self._settingsUserChanged=False
		self._showSettingsUserMessage=[False,"","Success"]
		self._closeGui=False
		self._closePopUp=True
		self._showChangesDialog=False
		self._currentStack=0
		self._currentOptionsStack=0
		self._isAccessDenyGroupEnabled=False
		self._isAccessDenyUserEnabled=False
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
		self._isAccessDenyUserEnabled=self.n4dMan.isAccessDenyUserEnabled
		self.isAccessDenyUserEnabled=copy.deepcopy(self.n4dMan.isAccessDenyUserEnabled)
		self.denyUsers=copy.deepcopy(self.n4dMan.denyUsers)
		self.usersList=copy.deepcopy(self.n4dMan.usersList)
		self._updateGroupModel()
		self._updateUserModel()
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

	#def _setShowSettingsGroupMessage

	def _getIsAccessDenyUserEnabled(self):

		return self._isAccessDenyUserEnabled

	#def _getIsAccessDenyUserEnabled

	def _setIsAccessDenyUserEnabled(self,isAccessDenyUserEnabled):

		if self._isAccessDenyUserEnabled!=isAccessDenyUserEnabled:
			self._isAccessDenyUserEnabled=isAccessDenyUserEnabled
			self.on_isAccessDenyUserEnabled.emit()

	#def _setIsAccessDenyUserEnabled

	def _getSettingsUserChanged(self):

		return self._settingsUserChanged

	#def _getSettingsUserChanged

	def _setSettingsUserChanged(self,settingsUserChanged):

		if self._settingsUserChanged!=settingsUserChanged:
			self._settingsUserChanged=settingsUserChanged
			self.on_settingsUserChanged.emit()

	#def _setSettingsUserChanged

	def _getShowSettingsUserMessage(self):

		return self._showSettingsUserMessage

	#def _getShowSettingsUserMessage

	def _setShowSettingsUserMessage(self,showSettingsUserMessage):

		if self._showSettingsUserMessage!=showSettingsUserMessage:
			self._showSettingsUserMessage=showSettingsUserMessage
			self.on_showSettingsUserMessage.emit()

	#def _setShowSettingsUserMessage

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

	def _getGroupsModel(self):
		
		return self._groupsModel

	#def _getGroupsModel

	def _updateGroupModel(self):

		ret=self._groupsModel.clear()
		self._groupsModel=GroupsModel.GroupsModel()
		groupsEntries=self.n4dMan.groupsConfigData
		for item in groupsEntries:
			self._groupsModel.appendRow(item["groupId"],item["isChecked"],item["description"])
		
	#def _updateGroupModel

	def _getUsersModel(self):
		
		return self._usersModel

	#def _getUsersModel

	def _updateUserModel(self):

		ret=self._usersModel.clear()
		self._usersModel=UsersModel.UsersModel()
		usersEntries=self.n4dMan.usersConfigData
		for item in usersEntries:
			self._usersModel.appendRow(item["userId"],item["isChecked"])
		
	#def _updateUserModel

	@Slot(bool)
	def manageGroupAccessControl(self,value):

		self.showSettingsGroupMessage=[False,"","Success"]
		if value!=self.isAccessDenyGroupEnabled:
			if value!=self.n4dMan.isAccessDenyGroupEnabled:
				self.settingsGroupChanged=True
			else:
				self.settingsGroupChanged=False
			self.isAccessDenyGroupEnabled=value
		else:
			self.settingsGroupChanged=False

	#def manageGroupAccessControl

	@Slot(bool)
	def manageUserAccessControl(self,value):

		self.showSettingsUserMessage=[False,"","Success"]
		if value!=self.isAccessDenyUserEnabled:
			if value!=self.n4dMan.isAccessDenyUserEnabled:
				self.settingsUserChanged=True
			else:
				self.settingsUserChanged=False
			self.isAccessDenyUserEnabled=value
		else:
			self.settingsUserChanged=False

	#def manageUserAccessControl
	
	@Slot('QVariantList')
	def manageGroupChecked(self,value):

		self.showSettingsGroupMessage=[False,"","Success"]
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
				self.settingsGroupChanged=True
			else:
				self.settingsGroupChanged=False
			self.denyGroups=tmpGroups
		else:
			self.settingsGroupChanged=False

	#def manageGroupChecked

	@Slot('QVariantList')
	def manageUserChecked(self,value):

		self.showSettingsUserMessage=[False,"","Success"]
		userId=value[0]
		userChecked=value[1]
		tmpUsers=copy.deepcopy(self.denyUsers)

		if userId not in tmpUsers:
			if userChecked:
				tmpUsers.append(userId)
		else:
			if not userChecked:
				tmpUsers.remove(userId)

		if len(tmpUsers)==0:
			self.isAccessDenyUserEnabled=False

		if tmpUsers != self.denyUsers:
			if tmpUsers != self.n4dMan.denyUsers:
				self.settingsUserChanged=True
			else:
				self.settingsUserChanged=False
			self.denyUsers=tmpUsers
		else:
			self.settingsUserChanged=False

	#def manageUserChecked

	@Slot(str)
	def addUser(self,value):

		self._usersModel.appendRow(value,True)
		tmpUser=[value,True]
		self.manageUserChecked(tmpUser)
		self._updateUserList(value,False)

	#def addUser

	@Slot(int)
	def removeUser(self,index):

		tmpUser=self._usersModel._entries[index]
		self._usersModel.removeRow(index)
		self.manageUserChecked([tmpUser["userId"],False])
		self._updateUserList(tmpUser["userId"],True)
	
	#def removeUser

	@Slot()
	def removeUserList(self):

		self._usersModel.clear()
		self._usersModel=UsersModel.UsersModel()
		self.usersList=[]
		self.denyUsers=[]
		self.isAccessDenyUserEnabled=False
		self.settingsUserChanged=True

	#def removeUserList

	def _updateUserList(self,userId,delete):

		tmpList=copy.deepcopy(self.usersList)

		if not delete:
			if userId not in tmpList:
				tmpList.append(userId)
		else:
			if userId in tmpList:
				tmpList.remove(userId)

		if len(tmpList)==0:
			self.isAccessDenyUserEnabled=False

		if tmpList != self.usersList:
			self.usersList=tmpList

	#def _updateUserList

	@Slot()
	def applyGroupChanges(self):

		self.showSettingsGroupMessage=[False,"","Success"]
		self.closePopUp=False
		t = threading.Thread(target=self._applyGroupChanges)
		t.daemon=True
		t.start()

	#def applyGroupChanges	

	def _applyGroupChanges(self):

		ret=self.n4dMan.applyGroupChanges(self.isAccessDenyGroupEnabled,self.denyGroups)
		self.closePopUp=True

		if ret[0]:
			self._updateGroupConfig()
			self.showSettingsGroupMessage=[True,ret[1],"Success"]
			self.closeGui=True
		else:
			self.showSettingsGroupMessage=[True,ret[1],"Error"]
			self.closeGui=False

		self.settingsGroupChanged=False
		self.showChangesDialog=False

	#def _applyGroupChanges

	@Slot()
	def cancelGroupChanges(self):

		self.showSettingsGroupMessage=[False,"","Success"]
		self.closePopUp=False
		t = threading.Thread(target=self._cancelGroupChanges)
		t.daemon=True
		t.start()

	#def cancelGroupChanges

	def _cancelGroupChanges(self):

		self._updateGroupConfig()
		self.settingsChanged=False
		self.closePopUp=True
		self.showChangesDialog=False
		self.closeGui=True

	#def _cancelGroupChanges

	def _updateGroupConfig(self):

		self.isAccessDenyGroupEnabled=copy.deepcopy(self.n4dMan.isAccessDenyGroupEnabled)
		self.denyGroups=copy.deepcopy(self.n4dMan.denyGroups)
		self._updateGroupModel()
	
	#def _updateGroupConfig
	
	@Slot()
	def applyUserChanges(self):

		self.showSettingsUserMessage=[False,"","Success"]
		self.closePopUp=False
		t = threading.Thread(target=self._applyUserChanges)
		t.daemon=True
		t.start()

	#def applyUserChanges	

	def _applyUserChanges(self):

		ret=self.n4dMan.applyUsersChanges(self.isAccessDenyUserEnabled,self.denyUsers,self.usersList)
		self.closePopUp=True

		if ret[0]:
			#self._updateUsersConfig()
			self.showSettingsUserMessage=[True,ret[1],"Success"]
			self.closeGui=True
		else:
			self.showSettingsUserMessage=[True,ret[1],"Error"]
			self.closeGui=False

		self.settingsUserChanged=False
		self.showChangesDialog=False

	#def _applyGroupChanges


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

		if self.settingsGroupChanged:
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
	
	on_settingsGroupChanged=Signal()
	settingsGroupChanged=Property(bool,_getSettingsGroupChanged,_setSettingsGroupChanged, notify=on_settingsGroupChanged)

	on_showSettingsGroupMessage=Signal()
	showSettingsGroupMessage=Property('QVariantList',_getShowSettingsGroupMessage,_setShowSettingsGroupMessage,notify=on_showSettingsGroupMessage)

	on_isAccessDenyUserEnabled=Signal()
	isAccessDenyUserEnabled=Property(bool,_getIsAccessDenyUserEnabled,_setIsAccessDenyUserEnabled,notify=on_isAccessDenyUserEnabled)
	
	on_settingsUserChanged=Signal()
	settingsUserChanged=Property(bool,_getSettingsUserChanged,_setSettingsUserChanged, notify=on_settingsUserChanged)

	on_showSettingsUserMessage=Signal()
	showSettingsUserMessage=Property('QVariantList',_getShowSettingsUserMessage,_setShowSettingsUserMessage,notify=on_showSettingsUserMessage)

	on_closePopUp=Signal()
	closePopUp=Property(bool,_getClosePopUp,_setClosePopUp, notify=on_closePopUp)

	on_closeGui=Signal()
	closeGui=Property(bool,_getCloseGui,_setCloseGui, notify=on_closeGui)

	on_showChangesDialog=Signal()
	showChangesDialog=Property(bool,_getShowChangesDialog,_setShowChangesDialog, notify=on_showChangesDialog)

	groupsModel=Property(QObject,_getGroupsModel,constant=True)
	usersModel=Property(QObject,_getUsersModel,constant=True)


#class LliurexAccessControl

