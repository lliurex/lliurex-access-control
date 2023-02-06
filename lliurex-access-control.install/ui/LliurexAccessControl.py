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

class UserValidation(QThread):

	def __init__(self,*args):

		QThread.__init__(self)

		self.user=args[0]
		self.password=args[1]
		self.ret=[]

	#def __init__

	def run(self, *args):

		self.ret=LliurexAccessControl.n4dMan.validateUser(self.user,self.password)

	#def run

#class UserValidation

class GatherInfo(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
	
	#def __init__
		

	def run(self,*args):
		
		time.sleep(1)
		self.manager=LliurexAccessControl.n4dMan.loadConfig()

	#def run

#class GatherInfo

class UpdateInfo(QThread):

	def __init__(self,*args):

		QThread.__init__(self)

		self.updateType=args[0]
		self.enabledInfo=args[1]
		self.listInfo=args[2]
		self.ret=[]

	#def __init__

	def run(self,*args):
		
		time.sleep(1)
		if self.updateType=="Groups":
			self.ret=LliurexAccessControl.n4dMan.applyGroupChanges(self.enabledInfo,self.listInfo)
		elif self.updateType=="Users":
			self.ret=LliurexAccessControl.n4dMan.applyUsersChanges(self.enabledInfo,self.listInfo)
		else:
			self.ret=LliurexAccessControl.n4dMan.applyCDCChanges(self.enabledInfo,self.listInfo)

	#def run

#class UpdateInfo

class AddNewUser(QThread):

	def __init__(self,*args):

		QThread.__init__(self)

		self.newUser=args[0]
		self.retCurrentUser=[False,[]]
		self.retAdminUser=[False,[],[]]

	#def __init__

	def run(self,*args):
		
		time.sleep(1)
		self.retCurrentUser=LliurexAccessControl.n4dMan.checkIfUserIsCurrrentUser(self.newUser)

		if not self.retCurrentUser[0]:
			self.retAdminUser=LliurexAccessControl.n4dMan.checkIfUserIsValidGroup(self.newUser)
		else:
			if len(self.newUser)>1:
				self.retAdminUser=LliurexAccessControl.n4dMan.checkIfUserIsValidGroup(self.newUser)
		
	#def run

#class AddUser

class LliurexAccessControl(QObject):

	USER_DUPLICATE_ERROR=-90
	CURRENT_USER_ERROR=-100
	USERS_NOT_ALLOWED_ERROR=-200

	n4dMan=N4dManager.N4dManager()

	def __init__(self):

		QObject.__init__(self)
		self.initBridge()

	#def __init__

	def initBridge(self):

		self._showLoginMessage=[False,'']
		self._runningLogin=False
		self._groupsModel=GroupsModel.GroupsModel()
		self._usersModel=UsersModel.UsersModel()
		self._settingsGroupChanged=False
		self._showSettingsGroupMessage=[False,"","Success"]
		self._settingsUserChanged=False
		self._showSettingsUserMessage=[False,"","Success"]
		self._showLocalAdminDialog=False
		self._settingsCDCChanged=False
		self._showSettingsCDCMessage=[False,"","Success"]
		self._closeGui=False
		self._closePopUp=True
		self._showGroupChangesDialog=False
		self._showUserChangesDialog=False
		self._showCDCChangesDialog=False
		self._currentStack=0
		self._currentOptionsStack=0
		self._isAccessDenyGroupEnabled=False
		self._isAccessDenyUserEnabled=False
		self._isCDCAccessControlAllowed=False
		self._isAccessDenyCDCEnabled=False
		self._cdcCode=""
		self._enableUserConfig=True
		self.tmpNewUser=[]
		self.tmpAdminUser=[]
		self.moveToStack=""
		self.correctCode=True
		QTimer.singleShot(200,self.loadLoginPanel)

	#def initBridge

	def loadLoginPanel(self):

		self.currentStack=1

	#def loadLoginPanel

	@Slot('QVariantList')
	def validate(self,value):

		self.showLoginMessage=[False,""]
		self.user=value[0]
		self.password=value[1]
		server='localhost'
		
		LliurexAccessControl.n4dMan.setServer(server)

		if not self.runningLogin:
			self.runningLogin = True
			self.userValidation=UserValidation(self.user,self.password)
			self.userValidation.start()
			self.userValidation.finished.connect(self._validate)
	
	#def validate

	def _validate(self):

		LOGIN_FAILED=-40
		FLAVOUR_LOCKED_ERROR=-50

		nextStep=False

		if self.userValidation.ret:
			group_found=False
			for g in ["sudo","admins","teachers"]:
				if g in LliurexAccessControl.n4dMan.user_groups:
					group_found=True
					break
					
			if group_found:
				if not LliurexAccessControl.n4dMan.isCurrentUserAdmin:
					if LliurexAccessControl.n4dMan.checkFlavour():
						self.runningLogin=False
						self.showLoginMessage=[True,FLAVOUR_LOCKED_ERROR]
						self.currentStack=1
					else:
						nextStep=True
				else:
					nextStep=True

				if nextStep:
					self.gatherInfo=GatherInfo()
					self.gatherInfo.start()
					self.gatherInfo.finished.connect(self._loadConfig)
			else:
				self.runningLogin=False
				self.showLoginMessage=[True,LOGIN_FAILED]
				self.currentStack=1
		else:
			self.runningLogin=False
			self.showLoginMessage=[True,LOGIN_FAILED]
			self.currentStack=1

	#def _validate	
	
	def _loadConfig(self):		

		self.isAccessDenyGroupEnabled=copy.deepcopy(LliurexAccessControl.n4dMan.isAccessDenyGroupEnabled)
		self.groupsInfo=copy.deepcopy(LliurexAccessControl.n4dMan.groupsInfo)
		self.isAccessDenyUserEnabled=copy.deepcopy(LliurexAccessControl.n4dMan.isAccessDenyUserEnabled)
		self.usersInfo=copy.deepcopy(LliurexAccessControl.n4dMan.usersInfo)
		self.isCDCAccessControlAllowed=copy.deepcopy(LliurexAccessControl.n4dMan.isCDCAccessControlAllowed)
		self.isAccessDenyCDCEnabled=copy.deepcopy(LliurexAccessControl.n4dMan.isAccessDenyCDCEnabled)
		self.cdcInfo=copy.deepcopy(LliurexAccessControl.n4dMan.cdcInfo)
		if len(self.cdcInfo)>0:
			self.cdcCode=self.cdcInfo["code"]
		self._updateGroupModel()
		self._updateUserModel()
		self.runningLogin=False
		self.currentStack=2

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

	def _getShowLoginMessage(self):

		return self._showLoginMessage

	#def _getShoLoginMessage

	def _setShowLoginMessage(self,showLoginMessage):

		if self._showLoginMessage!=showLoginMessage:
			self._showLoginMessage=showLoginMessage
			self.on_showLoginMessage.emit()

	#def _setShowLoginMessage

	def _getRunningLogin(self):

		return self._runningLogin

	#def _getRunningLogin

	def _setRunningLogin(self,runningLogin):

		if self._runningLogin!=runningLogin:
			self._runningLogin=runningLogin
			self.on_runningLogin.emit()

	#def _setRunningLogin

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

	def _getShowLocalAdminDialog(self):

		return self._showLocalAdminDialog

	#def _getShowLocalAdminDialog

	def _setShowLocalAdminDialog(self,showLocalAdminDialog):

		if self._showLocalAdminDialog!=showLocalAdminDialog:
			self._showLocalAdminDialog=showLocalAdminDialog
			self.on_showLocalAdminDialog.emit()

	#def _setShowLocalAdminDialog

	def _getIsCDCAccessControlAllowed(self):

		return self._isCDCAccessControlAllowed

	#def _getIsCDCAccessControlAllowed

	def _setIsCDCAccessControlAllowed(self,isCDCAccessControlAllowed):

		if self._isCDCAccessControlAllowed!=isCDCAccessControlAllowed:
			self._isCDCAccessControlAllowed=isCDCAccessControlAllowed
			self.on_isCDCAccessControlAllowed.emit()

	#def _setIsCDCAccessControlAllowed):

	def _getIsAccessDenyCDCEnabled(self):

		return self._isAccessDenyCDCEnabled

	#def _getIsAccessDenyCDCEnabled

	def _setIsAccessDenyCDCEnabled(self,isAccessDenyCDCEnabled):

		if self._isAccessDenyCDCEnabled!=isAccessDenyCDCEnabled:
			self._isAccessDenyCDCEnabled=isAccessDenyCDCEnabled
			self.on_isAccessDenyCDCEnabled.emit()

	#def _setIsAccessDenyCDCEnabled:

	def _getCdcCode(self):

		return self._cdcCode

	#def _getCdcCode

	def _setCdcCode(self,cdcCode):

		if self._cdcCode!=cdcCode:
			self._cdcCode=cdcCode
			self.on_cdcCode.emit()

	#def _setCdcCode

	def _getClosePopUp(self):

		return self._closePopUp

	#def _getClosePopUp	

	def _getSettingsCDCChanged(self):

		return self._settingsCDCChanged

	#def _getSettingsCDCChanged

	def _setSettingsCDCChanged(self,settingsCDCChanged):

		if self._settingsCDCChanged!=settingsCDCChanged:
			self._settingsCDCChanged=settingsCDCChanged
			self.on_settingsCDCChanged.emit()

	#def _setSettingsCDCChanged

	def _getShowSettingsCDCMessage(self):

		return self._showSettingsCDCMessage

	#def _getShowSettingsCDCMessage

	def _setShowSettingsCDCMessage(self,showSettingsCDCMessage):

		if self._showSettingsCDCMessage!=showSettingsCDCMessage:
			self._showSettingsCDCMessage=showSettingsCDCMessage
			self.on_showSettingsCDCMessage.emit()

	#def _setShowSettingsCDCMessage

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

	def _getShowGroupChangesDialog(self):

		return self._showGroupChangesDialog

	#def _getShowGroupChangesDialog	

	def _setShowGroupChangesDialog(self,showGroupChangesDialog):
		
		if self._showGroupChangesDialog!=showGroupChangesDialog:
			self._showGroupChangesDialog=showGroupChangesDialog		
			self.on_showGroupChangesDialog.emit()

	#def _setShowGroupChangesDialog

	def _getShowUserChangesDialog(self):

		return self._showUserChangesDialog

	#def _getShowUserChangesDialog	

	def _setShowUserChangesDialog(self,showUserChangesDialog):
		
		if self._showUserChangesDialog!=showUserChangesDialog:
			self._showUserChangesDialog=showUserChangesDialog		
			self.on_showUserChangesDialog.emit()

	#def _setShowUserChangesDialog
	
	def _getShowCDCChangesDialog(self):

		return self._showCDCChangesDialog

	#def _getShowCDCChangesDialog	

	def _setShowCDCChangesDialog(self,showCDCChangesDialog):
		
		if self._showCDCChangesDialog!=showCDCChangesDialog:
			self._showCDCChangesDialog=showCDCChangesDialog		
			self.on_showCDCChangesDialog.emit()

	#def _setShowCDCChangesDialog

	def _getEnableUserConfig(self):

		return self._enableUserConfig

	#def _getEnableUserConfig

	def _setEnableUserConfig(self,enableUserConfig):

		if self._enableUserConfig!=enableUserConfig:
			self._enableUserConfig=enableUserConfig
			self.on_enableUserConfig.emit()

	#def _setEnableUserConfig

	def _getGroupsModel(self):
		
		return self._groupsModel

	#def _getGroupsModel

	def _updateGroupModel(self):

		ret=self._groupsModel.clear()
		groupsEntries=LliurexAccessControl.n4dMan.groupsConfigData
		for item in groupsEntries:
			self._groupsModel.appendRow(item["groupId"],item["isLocked"],item["description"])
		
	#def _updateGroupModel

	def _getUsersModel(self):
		
		return self._usersModel

	#def _getUsersModel

	def _updateUserModel(self):

		ret=self._usersModel.clear()
		usersEntries=LliurexAccessControl.n4dMan.usersConfigData
		for item in usersEntries:
			if item["userId"]!="":
				self._usersModel.appendRow(item["userId"],item["isLocked"])
		
	#def _updateUserModel

	@Slot(bool)
	def manageGroupAccessControl(self,value):

		self.showSettingsGroupMessage=[False,"","Success"]
		
		if value!=self.isAccessDenyGroupEnabled:
			self.isAccessDenyGroupEnabled=value
			if self.isAccessDenyGroupEnabled!=LliurexAccessControl.n4dMan.isAccessDenyGroupEnabled:
				self.settingsGroupChanged=True
			else:
				self.settingsGroupChanged=False
					
	#def manageGroupAccessControl

	@Slot(bool)
	def manageUserAccessControl(self,value):

		self.showSettingsUserMessage=[False,"","Success"]

		if value!=self.isAccessDenyUserEnabled:
			self.isAccessDenyUserEnabled=value
			if self.isAccessDenyUserEnabled!=LliurexAccessControl.n4dMan.isAccessDenyUserEnabled:
				self.settingsUserChanged=True
			else:
				self.settingsUserChanged=False

	#def manageUserAccessControl
	
	@Slot('QVariantList')
	def manageGroupChecked(self,value):

		self.showSettingsGroupMessage=[False,"","Success"]
		groupId=value[0]
		groupChecked=value[1]
		thereAreGroupLocked=False
		
		if self.groupsInfo[groupId]["isLocked"]!=groupChecked:
			self.groupsInfo[groupId]["isLocked"]=groupChecked
			if self.groupsInfo!=LliurexAccessControl.n4dMan.groupsInfo:
				self.settingsGroupChanged=True
			else:
				self.settingsGroupChanged=False
			
		if not LliurexAccessControl.n4dMan.thereAreGroupsLocked(self.groupsInfo):
			self.isAccessDenyGroupEnabled=False	 
		
	#def manageGroupChecked

	@Slot('QVariantList')
	def manageUserChecked(self,value):

		self.showSettingsUserMessage=[False,"","Success"]
		userId=value[0]
		userChecked=value[1]

		if self.usersInfo[userId]["isLocked"]!=userChecked:
			self.usersInfo[userId]["isLocked"]=userChecked
			if userId in LliurexAccessControl.n4dMan.usersInfo.keys():
				if self.usersInfo!=LliurexAccessControl.n4dMan.usersInfo:
					self.settingsUserChanged=True
				else:
					self.settingsUserChanged=False
			else:		
				self.settingsUserChanged=True

		if not LliurexAccessControl.n4dMan.thereAreUsersLocked(self.usersInfo):
			self.isAccessDenyUserEnabled=False
		
	#def manageUserChecked

	@Slot(str)
	def addUser(self,userId):

		self.showSettingsUserMessage=[False,"","Success"]
		self.closePopUp=False
		tmpUserList=userId.split(" ")
		self.userId=[]

		for item in tmpUserList:
			if item !="":
				self.userId.append(item.lower())
		
		self.addNewUser=AddNewUser(self.userId)
		self.addNewUser.start()
		self.addNewUser.finished.connect(self._checkNewUser)

	#def addUser	

	def _checkNewUser(self):

		self.tmpNewUser=[]
		self.tmpAdminUser=[]
		matchDuplicateList=[]
		nextStep=False
		invalidUsers=False

		for item in range(len(self.userId)-1,-1,-1):
			if self.userId[item] in self.usersInfo.keys():
				matchDuplicateList.append(self.userId[item])
				self.userId.pop(item)

		if len(self.userId)>0:
			if self.addNewUser.retCurrentUser[0]:
				for item in range(len(self.userId)-1,-1,-1):
					try:
						if self.userId[item] in self.addNewUser.retCurrentUser[1]:
							self.userId.pop(item)
					except:
						pass
			
			if len(self.userId)>00:
				nextStep=True
				if not LliurexAccessControl.n4dMan.isCurrentUserAdmin:
					for item in range(len(self.userId)-1,-1,-1):
						try:
							if self.userId[item] in self.addNewUser.retAdminUser[1]:
								self.userId.pop(item)
								invalidUsers=True
							if self.userId[item] in self.addNewUser.retAdminUser[2]:
								self.userId.pop(item)
								invalidUsers=True
						except:
							pass

					if len(self.userId)==0:
						nextStep=False	
			else:
				nextStep=False

			if nextStep:
				isLocalAdmin=self.addNewUser.retAdminUser[0]
				if isLocalAdmin:
					self.showLocalAdminDialog=True 
					self.tmpNewUser=self.userId
					self.tmpAdminUser=self.addNewUser.retAdminUser[1]
				else:
					for item in self.userId:
						self._usersModel.appendRow(item,True)
						self._updateUserList(item,False)
					
					if self.addNewUser.retCurrentUser[0]:
						self.showSettingsUserMessage=[True,LliurexAccessControl.CURRENT_USER_ERROR,"Warning"]
					
					else:
						if invalidUsers:
							self.showSettingsUserMessage=[True,LliurexAccessControl.USERS_NOT_ALLOWED_ERROR,"Warning"]
						
					if not LliurexAccessControl.n4dMan.thereAreUsersLocked(self.usersInfo):
						self.isAccessDenyUserEnabled=False

			else:
				if not invalidUsers:
					self.showSettingsUserMessage=[True,LliurexAccessControl.CURRENT_USER_ERROR,"Warning"]
				else:
					self.showSettingsUserMessage=[True,LliurexAccessControl.USERS_NOT_ALLOWED_ERROR,"Warning"]

		else:
			self.showSettingsUserMessage=[True,LliurexAccessControl.USER_DUPLICATE_ERROR,"Warning"]
		
		self.closePopUp=True

	#def _checkNewUser

	@Slot(str)
	def manageLocalAdminDialog(self,action):

		self.showLocalAdminDialog=False

		if action=="Accept":
			LliurexAccessControl.n4dMan.writeLog("Action: Added admin user to user list: %s"%self.tmpAdminUser)
			nextStep=True
		else:
			for item in range(len(self.tmpNewUser)-1,-1,-1):
				if self.tmpNewUser[item] in self.tmpAdminUser:
					self.tmpNewUser.pop(item)

		if len(self.tmpNewUser)>0:
			for item in self.tmpNewUser:
				self._usersModel.appendRow(item,True)
				self._updateUserList(item,False)
			if not LliurexAccessControl.n4dMan.thereAreUsersLocked(self.usersInfo):
				self.isAccessDenyUserEnabled=False

		if self.addNewUser.retCurrentUser[0]:
			self.showSettingsUserMessage=[True,LliurexAccessControl.CURRENT_USER_ERROR,"Warning"]

	#def manageLocalAdminDialog

	@Slot(int)
	def removeUser(self,index):

		self.showSettingsUserMessage=[False,"","Success"]
		tmpUser=self._usersModel._entries[index]
		self._usersModel.removeRow(index)
		self._updateUserList(tmpUser["userId"],True)
		if not LliurexAccessControl.n4dMan.thereAreUsersLocked(self.usersInfo):
			self.isAccessDenyUserEnabled=False

	#def removeUser

	@Slot()
	def removeUserList(self):

		self.showSettingsUserMessage=[False,"","Success"]
		self._usersModel.clear()
		self.usersInfo={}
		self.isAccessDenyUserEnabled=False
		if self.usersInfo!=LliurexAccessControl.n4dMan.usersInfo:
			self.settingsUserChanged=True
		else:
			if self.isAccessDenyUserEnabled!=LliurexAccessControl.n4dMan.isAccessDenyUserEnabled:
				self.settingsUserChanged=True 
			else:
				self.settingsUserChanged=False

		if self.settingsUserChanged:
			LliurexAccessControl.n4dMan.writeLog("Action: Removed user list")

	#def removeUserList

	def _updateUserList(self,userId,delete):

		tmpList=copy.deepcopy(self.usersInfo)
		userIdMatch=False

		if userId in tmpList.keys():
			userIdMatch=True
		
		if userIdMatch:
			if delete:
				del tmpList[userId]
		else:
			if not delete:
				tmpList[userId]={}
				tmpList[userId]["isLocked"]=True

		if tmpList!=self.usersInfo:
			if tmpList!=LliurexAccessControl.n4dMan.usersInfo:
				self.settingsUserChanged=True
			else:
				self.settingsUserChanged=False

			self.usersInfo=tmpList

	#def _updateUserList

	@Slot(bool)
	def manageCDCAccessControl(self,value):

		self.showSettingsCDCMessage=[False,"","Success"]
		
		if value!=self.isAccessDenyCDCEnabled:
			self.isAccessDenyCDCEnabled=value
			self.cdcInfo["accessControlEnabled"]=value
			if self.isAccessDenyCDCEnabled!=LliurexAccessControl.n4dMan.isAccessDenyCDCEnabled:
				self.settingsCDCChanged=True
			else:
				self.settingsCDCChanged=False
					
	#def manageCDCAccessControl

	@Slot(str)
	def manageCDCCodeChange(self,newCode):

		self.showSettingsCDCMessage=[False,"","Success"]
		self.correctCode=LliurexAccessControl.n4dMan.isCorrectCode(newCode)
		if self.correctCode:
			if self.cdcCode!=newCode:
				self.cdcCode=newCode
				self.cdcInfo["code"]=newCode
				if self.cdcCode!=LliurexAccessControl.n4dMan.cdcInfo["code"]:
					self.settingsCDCChanged=True
				else:
					self.settingsCDCChanged=False

			if self.cdcCode=="" :
				self.isAccessDenyCDCEnabled=False
		else:
			self.showSettingsCDCMessage=[True,LliurexAccessControl.n4dMan.CDC_CODE_NOT_VALID,"Error"]

	#def manageCDCCodeChange

	@Slot()
	def applyGroupChanges(self):

		self.showSettingsGroupMessage=[False,"","Success"]
		self.closePopUp=False
		self.showGroupChangesDialog=False
		self.updateInfoGroups=UpdateInfo("Groups",self.isAccessDenyGroupEnabled,self.groupsInfo)
		self.updateInfoGroups.start()
		self.updateInfoGroups.finished.connect(self._applyGroupChanges)

	#def applyGroupChanges	

	def _applyGroupChanges(self):

		#self.updateGroupInfo.ret=LliurexAccessControl.n4dMan.applyGroupChanges(self.isAccessDenyGroupEnabled,self.groupsInfo)

		if self.updateInfoGroups.ret[0]:
			self._updateGroupConfig()
			self.showSettingsGroupMessage=[True,self.updateInfoGroups.ret[1],"Success"]
			self.closeGui=True
		else:
			self.showSettingsGroupMessage=[True,self.updateInfoGroups.ret[1],"Error"]
			self.closeGui=False
			self.moveToStack=""

		if self.moveToStack!="":
			self.currentOptionsStack=self.moveToStack
			self.showSettingsGroupMessage=[False,"","Info"]
			self.moveToStack=""

		self.settingsGroupChanged=False
		self.closePopUp=True

	#def _applyGroupChanges

	@Slot()
	def cancelGroupChanges(self):

		self.showSettingsGroupMessage=[False,"","Success"]
		self.closePopUp=False
		self.showGroupChangesDialog=False
		self._cancelGroupChanges()

	#def cancelGroupChanges

	def _cancelGroupChanges(self):

		self._updateGroupConfig()
		self.settingsGroupChanged=False
		self.closePopUp=True
		if self.moveToStack!="":
			self.currentOptionsStack=self.moveToStack
		self.moveToStack=""

		self.closeGui=True

	#def _cancelGroupChanges

	def _updateGroupConfig(self):

		self.isAccessDenyGroupEnabled=copy.deepcopy(LliurexAccessControl.n4dMan.isAccessDenyGroupEnabled)
		self.groupsInfo=copy.deepcopy(LliurexAccessControl.n4dMan.groupsInfo)
		self._updateGroupModel()
	
	#def _updateGroupConfig
	
	@Slot()
	def applyUserChanges(self):

		self.showSettingsUserMessage=[False,"","Success"]
		self.closePopUp=False
		self.showUserChangesDialog=False
		self.updateUserInfo=UpdateInfo("Users",self.isAccessDenyUserEnabled,self.usersInfo)
		self.updateUserInfo.start()
		self.updateUserInfo.finished.connect(self._applyUserChanges)

	#def applyUserChanges	

	def _applyUserChanges(self):

		if self.updateUserInfo.ret[0]:
			self._updateUsersConfig()
			time.sleep(1)
			self.showSettingsUserMessage=[True,self.updateUserInfo.ret[1],"Success"]
			self.closeGui=True
		else:
			self.showSettingsUserMessage=[True,self.updateUserInfo.ret[1],"Error"]
			self.closeGui=False
			self.moveToStack=""

		if self.moveToStack!="":
			self.currentOptionsStack=self.moveToStack
			self.showSettingsUserMessage=[False,"","Info"]
			self.moveToStack=""

		self.settingsUserChanged=False
		self.closePopUp=True


	#def _applyUserChanges

	@Slot()
	def cancelUserChanges(self):

		self.showSettingsUserMessage=[False,"","Success"]
		self.closePopUp=False
		self.showUserChangesDialog=False
		self._cancelUserChanges()

	#def cancelUserChanges

	def _cancelUserChanges(self):

		self._updateUsersConfig()
		self.settingsUserChanged=False
		self.closePopUp=True
		if self.moveToStack!="":
			self.currentOptionsStack=self.moveToStack
		self.moveToStack=""
		
		self.closeGui=True

	#def _cancelUserChanges

	def _updateUsersConfig(self):

		self.isAccessDenyUserEnabled=copy.deepcopy(LliurexAccessControl.n4dMan.isAccessDenyUserEnabled)
		self.usersInfo=copy.deepcopy(LliurexAccessControl.n4dMan.usersInfo)
		self._updateUserModel()
	
	#def _updateUsersConfig

	@Slot()
	def applyCDCChanges(self):

		self.showSettingsCDCMessage=[False,"","Success"]
		if self.correctCode or not self.isAccessDenyCDCEnabled:
			self.correctCode=True
			self.closePopUp=False
			self.showCDCChangesDialog=False
			self.updateCDCInfo=UpdateInfo("CDC",self.isAccessDenyCDCEnabled,self.cdcInfo)
			self.updateCDCInfo.start()
			self.updateCDCInfo.finished.connect(self._applyCDCChanges)
		else:
			self.showSettingsCDCMessage=[True,LliurexAccessControl.n4dMan.CDC_CODE_NOT_VALID,"Error"]
	
	#def applyCdcChanges

	def _applyCDCChanges(self):

		if self.updateCDCInfo.ret[0]:
			self._updateCDCConfig()
			time.sleep(1)
			self.showSettingsCDCMessage=[True,self.updateCDCInfo.ret[1],"Success"]
			self.closeGui=True
		else:
			self.showSettingsCDCMessage=[True,self.updateCDCInfo.ret[1],"Error"]
			self.closeGui=False
			self.moveToStack=""

		if self.moveToStack!="":
			self.currentOptionsStack=self.moveToStack
			self.showSettingsCDCMessage=[False,"","Info"]
			self.moveToStack=""

		self.settingsCDCChanged=False
		self.closePopUp=True

	#def _applyCDCChanges

	@Slot()
	def cancelCDCChanges(self):

		self.showSettingsCDCMessage=[False,"","Success"]
		self.correctCode=True
		self.closePopUp=False
		self.showCDCChangesDialog=False
		self._cancelCDCChanges()

	#def cancelUserChanges

	def _cancelCDCChanges(self):

		self._updateCDCConfig()
		self.settingsCDCChanged=False
		self.closePopUp=True
		if self.moveToStack!="":
			self.currentOptionsStack=self.moveToStack
		self.moveToStack=""
		
		self.closeGui=True

	#def _cancelCDCChanges

	def _updateCDCConfig(self):

		self.isAccessDenyCDCEnabled=copy.deepcopy(LliurexAccessControl.n4dMan.isAccessDenyCDCEnabled)
		self.cdcInfo=copy.deepcopy(LliurexAccessControl.n4dMan.cdcInfo)
		self.cdcCode=""
		self.cdcCode=self.cdcInfo["code"]
	
	#def _updateUsersConfig

	@Slot(int)
	def manageTransitions(self,stack):

		if self.currentOptionsStack!=stack:
			self.moveToStack=stack
			if self.settingsGroupChanged:
				self.showGroupChangesDialog=True
			elif self.settingsUserChanged:
				self.showUserChangesDialog=True
			elif self.settingsCDCChanged:
				self.showCDCChangesDialog=True
			else:
				self.currentOptionsStack=stack
				self.moveToStack=""
	
	#def manageTransitions

	@Slot(str)
	def manageSettingsDialog(self,action):
		
		if action=="Accept":
			if self.settingsGroupChanged:
				self.applyGroupChanges()
			elif self.settingsUserChanged:
				self.applyUserChanges()
			elif self.settingsCDCChanged:
				self.applyCDCChanges()
		elif action=="Discard":
			if self.settingsGroupChanged:
				self.cancelGroupChanges()
			elif self.settingsUserChanged:
				self.cancelUserChanges()
			elif self.settingsCDCChanged:
				self.cancelCDCChanges()
		elif action=="Cancel":
			self.closeGui=False
			if self.settingsGroupChanged:
				self.showGroupChangesDialog=False
			elif self.settingsUserChanged:
				self.showUserChangesDialog=False
			elif self.settingsCDCChanged:
				self.showCDCChangesDialog=False
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
		if self.settingsGroupChanged:
			self.showGroupChangesDialog=True
		elif self.settingsUserChanged:
			self.showUserChangesDialog=True
		elif self.settingsCDCChanged:
			self.showCDCChangesDialog=True
		else:
			self.closeGui=True
			LliurexAccessControl.n4dMan.writeLog("Close Session")

	#def closeApplication
	
	on_currentStack=Signal()
	currentStack=Property(int,_getCurrentStack,_setCurrentStack, notify=on_currentStack)
	
	on_currentOptionsStack=Signal()
	currentOptionsStack=Property(int,_getCurrentOptionsStack,_setCurrentOptionsStack, notify=on_currentOptionsStack)

	on_showLoginMessage=Signal()
	showLoginMessage=Property('QVariantList',_getShowLoginMessage,_setShowLoginMessage, notify=on_showLoginMessage)

	on_runningLogin=Signal()
	runningLogin=Property(bool,_getRunningLogin,_setRunningLogin, notify=on_runningLogin)

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

	on_showLocalAdminDialog=Signal()
	showLocalAdminDialog=Property(bool,_getShowLocalAdminDialog,_setShowLocalAdminDialog,notify=on_showLocalAdminDialog)

	on_isCDCAccessControlAllowed=Signal()
	isCDCAccessControlAllowed=Property(bool,_getIsCDCAccessControlAllowed,_setIsCDCAccessControlAllowed,notify=on_isCDCAccessControlAllowed)

	on_isAccessDenyCDCEnabled=Signal()
	isAccessDenyCDCEnabled=Property(bool,_getIsAccessDenyCDCEnabled,_setIsAccessDenyCDCEnabled,notify=on_isAccessDenyCDCEnabled)
	
	on_cdcCode=Signal()
	cdcCode=Property(str,_getCdcCode,_setCdcCode,notify=on_cdcCode)
	
	on_settingsCDCChanged=Signal()
	settingsCDCChanged=Property(bool,_getSettingsCDCChanged,_setSettingsCDCChanged, notify=on_settingsCDCChanged)

	on_showSettingsCDCMessage=Signal()
	showSettingsCDCMessage=Property('QVariantList',_getShowSettingsCDCMessage,_setShowSettingsCDCMessage,notify=on_showSettingsCDCMessage)
	
	on_closePopUp=Signal()
	closePopUp=Property(bool,_getClosePopUp,_setClosePopUp, notify=on_closePopUp)

	on_closeGui=Signal()
	closeGui=Property(bool,_getCloseGui,_setCloseGui, notify=on_closeGui)

	on_showGroupChangesDialog=Signal()
	showGroupChangesDialog=Property(bool,_getShowGroupChangesDialog,_setShowGroupChangesDialog, notify=on_showGroupChangesDialog)

	on_showUserChangesDialog=Signal()
	showUserChangesDialog=Property(bool,_getShowUserChangesDialog,_setShowUserChangesDialog, notify=on_showUserChangesDialog)

	on_showCDCChangesDialog=Signal()
	showCDCChangesDialog=Property(bool,_getShowCDCChangesDialog,_setShowCDCChangesDialog, notify=on_showCDCChangesDialog)

	on_enableUserConfig=Signal()
	enableUserConfig=Property(bool,_getEnableUserConfig,_setEnableUserConfig,notify=on_enableUserConfig)

	groupsModel=Property(QObject,_getGroupsModel,constant=True)
	usersModel=Property(QObject,_getUsersModel,constant=True)


#class LliurexAccessControl

