#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import signal
import copy
import time

import UsersModel
signal.signal(signal.SIGINT, signal.SIG_DFL)

class UpdateInfo(QThread):

	infoUpdated=Signal(dict)

	def __init__(self,manager,accessControlEnabled,usersInfo):

		QThread.__init__(self)

		self.manager=manager
		self.accessControlEnabled=accessControlEnabled
		self.usersInfo=usersInfo

	#def __init__

	def run(self,*args):
		
		time.sleep(1)
		ret=self.manager.applyUsersChanges(self.accessControlEnabled,self.usersInfo)
		self.infoUpdated.emit(ret)

	#def run

#class UpdateInfo

class AddNewUser(QThread):

	newUserAdded=Signal(dict,dict)

	def __init__(self,manager,newUsers):

		super().__init__()

		self.manager=manager
		self.newUsers=newUsers
		
	#def __init__

	def run(self,*args):
		
		time.sleep(1)
		retCurrentUser=self.manager.checkIfUserIsCurrrentUser(self.newUsers)

		if not retCurrentUser.get("validGroup"):
			retAdminUser=self.manager.checkIfUserIsValidGroup(self.newUsers)
		else:
			if len(self.newsUser)>1:
				retAdminUser=self.manager.checkIfUserIsValidGroup(self.newUsers)
		
		self.newUserAdded.emit(retCurrentUser,retAdminUser)	
	
	#def run

#class AddUser

class Bridge(QObject):

	USER_DUPLICATE_ERROR=-90
	CURRENT_USER_ERROR=-100
	USERS_NOT_ALLOWED_ERROR=-200

	isUserAccessControlEnabledChanged=Signal()
	hasUserChangesChanged=Signal()
	showSettingsUserMessageChanged=Signal()
	showLocalAdminDialogChanged=Signal()
	showUserChangesDialogChanged=Signal()
	enableUserConfigChanged=Signal()

	def __init__(self,ticket=None):

		super().__init__()
		self.core=Core.Core.get_core()
		self.n4dManager=self.core.n4dManager
		self._usersModel=UsersModel.UsersModel()
		self._isUserAccessControlEnabled=False
		self._hasUserChanges=False
		self._showSettingsUserMessage={"show":False,"msgCode":"","type":""}
		self._showLocalAdminDialog=False
		self._showUserChangesDialog=False
		self._enableUserConfig=True
		self.tmpNewUser=[]
		self.tmpAdminUser=[]

	#def __init__

	@Property(bool,notify=isUserAccessControlEnabledChanged)
	def isUserAccessControlEnabled(self):

		return self._isUserAccessControlEnabled

	#def isUserAccessControlEnabled

	@isUserAccessControlEnabled.setter
	def isUserAccessControlEnabled(self,isUserAccessControlEnabled):

		if self._isUserAccessControlEnabled!=isUserAccessControlEnabled:
			self._isUserAccessControlEnabled=isUserAccessControlEnabled
			self.isUserAccessControlEnabledChanged.emit()

	#def isUserAccessControlEnabled

	@Property(bool,notify=hasUserChangesChanged)
	def hasUserChanges(self):

		return self._hasUserChanges

	#def hasUserChanges

	@hasUserChanges.setter
	def hasUserChanges(self,hasUserChanges):

		if self._hasUserChanges!=hasUserChanges:
			self._hasUserChanges=hasUserChanges
			self.hasUserChangesChanged.emit()

	#def hasUserChanges
	@Property(dict,notify=showSettingsUserMessageChanged)
	def showSettingsUserMessage(self):

		return self._showSettingsUserMessage

	#def showSettingsUserMessage

	@showSettingsUserMessage.setter
	def showSettingsUserMessage(self,showSettingsUserMessage):

		if self._showSettingsUserMessage!=showSettingsUserMessage:
			self._showSettingsUserMessage=showSettingsUserMessage
			self.showSettingsUserMessageChanged.emit()

	#def showSettingsUserMessage

	@Property(bool,notify=showLocalAdminDialogChanged)
	def showLocalAdminDialog(self):

		return self._showLocalAdminDialog

	#def showLocalAdminDialog

	@showLocalAdminDialog.setter
	def showLocalAdminDialog(self,showLocalAdminDialog):

		if self._showLocalAdminDialog!=showLocalAdminDialog:
			self._showLocalAdminDialog=showLocalAdminDialog
			self.showLocalAdminDialogChanged.emit()

	#def showLocalAdminDialog

	@Property(bool,notify=showUserChangesDialogChanged)
	def showUserChangesDialog(self):

		return self._showUserChangesDialog

	#def showUserChangesDialog	

	@showUserChangesDialog.setter
	def showUserChangesDialog(self,showUserChangesDialog):
		
		if self._showUserChangesDialog!=showUserChangesDialog:
			self._showUserChangesDialog=showUserChangesDialog		
			self.showUserChangesDialogChanged.emit()

	#def showUserChangesDialog

	@Property(bool,notify=enableUserConfigChanged)
	def enableUserConfig(self):

		return self._enableUserConfig

	#def enableUserConfig

	@enableUserConfig.setter
	def enableUserConfig(self,enableUserConfig):

		if self._enableUserConfig!=enableUserConfig:
			self._enableUserConfig=enableUserConfig
			self.enableUserConfigChanged.emit()

	#def enableUserConfig

	@Property(QObject,constant=True)
	def usersModel(self):
		
		return self._usersModel

	#def usersModel

	def getUserConfig(self):		

		self.isUserAccessControlEnabled=copy.deepcopy(self.n4dManager.isUserAccessControlEnabled)
		self.usersInfo=copy.deepcopy(self.n4dManager.usersInfo)
		self.enableUserConfig=self.n4dManager.enableUserConfig
		self._updateUserModel()

	#def getUserConfig

	def _updateUserModel(self):

		ret=self._usersModel.clear()
		usersEntries=self.n4dManager.usersConfigData
		for item in usersEntries:
			if item["userId"]!="":
				self._usersModel.appendRow(item["userId"],item["isLocked"])
		
	#def _updateUserModel

	@Slot(bool)
	def manageUserAccessControl(self,value):

		self.showSettingsUserMessage={"show":False,"msgCode":"","type":""}

		if value!=self.isUserAccessControlEnabled:
			self.isUserAccessControlEnabled=value
			self.hasUserChanges=(self.isUserAccessControlEnabled!=self.n4dManager.isUserAccessControlEnabled)
	
	#def manageUserAccessControl
	
	@Slot(dict)
	def manageUserChecked(self,value):

		self.showSettingsUserMessage={"show":False,"msgCode":"","type":""}
		userId=value.get("userId")
		userChecked=value.get("isLocked")

		if self.usersInfo.get(userId,{}).get("isLocked")!=userChecked:
			self.usersInfo[userId]["isLocked"]=userChecked
			if userId in self.n4dManager.usersInfo.keys():
				self.hasUserChanges=(self.usersInfo!=self.n4dManager.usersInfo)
			else:		
				self.hasUserChanges=True

		if not self.n4dManager.thereAreUsersLocked(self.usersInfo):
			self.isUserAccessControlEnabled=False
		
	#def manageUserChecked

	@Slot(str)
	def addUser(self,usersId):

		self.showSettingsUserMessage={"show":False,"msgCode":"","type":""}
		self.core.mainStack.showPopUp={"show":True,"msgCode":self.core.mainStack.SAVE_DATA_MSG}
		usersId=usersId.replace(","," ")
		self.usersId=[item.lower() for item in usersId.split(" ") if item]
		self.addNewUserT=AddNewUser(self.n4dManager,self.usersId)
		self.addNewUserT.start()
		self.addNewUserT.newUserAdded.connect(self._checkNewUser)
		self.addNewUserT.finished.connect(self.addNewUserT.deleteLater)

	#def addUser	

	@Slot()
	def _checkNewUser(self,retCurrentUser,retAdminUser):

		self.tmpNewUser=[]
		self.tmpAdminUser=[]
		
		self.usersId=[u for u in self.usersId if u not in self.usersInfo]

		if not self.usersId:
			self.showSettingsUserMessage={"show":True,"msgCode":Bridge.USER_DUPLICATE_ERROR,"type":self.n4dManager.KIRIGAMI_MSG_WARNING}
			self.core.mainStack.showPopUp={"show":False,"msgCode":""}
			return 

		self.isCurrentUser=retCurrentUser.get("isCurrentUser")
		if self.isCurrentUser:
			currentUsers=set(retCurrentUser.get("userList") if len(retCurrentUser.get("userList")) > 1 else set())
			self.usersId=[u for u in self.usersId if u not in currentUsers]

		if not self.usersId:
			self.showSettingsUserMessage={"show":True,"msgCode":Bridge.CURRENT_USER_ERROR,"type":self.n4dManager.KIRIGAMI_MSG_WARNING}
			self.core.mainStack.showPopUp={"show":False,"msgCode":""}
			return

		invalidUsers=False

		if not self.n4dManager.isCurrentUserAdmin:
			localAdminList=retAdminUser.get("localAdminList")
			teachersList=retAdminUser.get("teachersList")
			restricedAdminList=set(localAdminList+teachersList)

			originalCount=len(self.usersId)
			self.usersId=[u for u in self.usersId if u not in restricedAdminList]

			if len(self.usersId)<originalCount:
				invalidUsers=True

		if not self.usersId:
			self.showSettingsUserMessage={"show":True,"msgCode":Bridge.USERS_NOT_ALLOWED_ERROR,"type":self.n4dManager.KIRIGAMI_MSG_WARNING}
			self.core.mainStack.showPopUp={"show":False,"msgCode":""}
			return

		isLocalAdmin=retAdminUser.get("isLocalAdmin")

		if isLocalAdmin:
			self.showLocalAdminDialog=True 
			self.tmpNewUser=self.usersId
			self.tmpAdminUser=retAdminUser.get("localAdminList")
		else:
			for user in self.usersId:
				self._usersModel.appendRow(user,True)
				self._updateUserList(user,False)

			if 	self.isCurrentUser:
				self.showSettingsUserMessage={"show":True,"msgCode":Bridge.CURRENT_USER_ERROR,"type":self.n4dManager.KIRIGAMI_MSG_WARNING}
			elif invalidUsers:
				self.showSettingsUserMessage={"show":True,"msgCode":Bridge.USERS_NOT_ALLOWED_ERROR,"type":self.n4dManager.KIRIGAMI_MSG_WARNING}
						
			if not self.n4dManager.thereAreUsersLocked(self.usersInfo):
				self.isUserAccessControlEnabled=False
			
		self.core.mainStack.showPopUp={"show":False,"msgCode":""}

	#def _checkNewUser

	@Slot(str)
	def manageLocalAdminDialog(self,action):

		self.showLocalAdminDialog=False

		if action=="Accept":
			self.n4dManager.writeLog(f"Action: Added admin user to user list: {self.tmpAdminUser}")
		else:
			adminSet=set(self.tmpAdminUser)
			self.tmpNewUser=[u for u in self.tmpNewUser if u not in adminSet]
		
		if not self.tmpNewUser:
			return

		for user in self.tmpNewUser:
			self._usersModel.appendRow(user,True)
			self._updateUserList(usersEntries,False)
	
		if not self.n4dManager.thereAreUsersLocked(self.usersInfo):
			self.isUserAccessControlEnabled=False

		if self.isCurrentUser:
			self.showSettingsUserMessage={"show":True,"msgCode":Bridge.CURRENT_USER_ERROR,"type":self.n4dManager.KIRIGAMI_MSG_WARNING}

	#def manageLocalAdminDialog

	@Slot(int)
	def removeUser(self,index):

		self.showSettingsUserMessage={"show":False,"msgCode":"","type":""}
		tmpUser=self._usersModel._entries[index]
		self._usersModel.removeRow(index)
		self._updateUserList(tmpUser["userId"],True)
		if not self.n4dManager.thereAreUsersLocked(self.usersInfo):
			self.isUserAccessControlEnabled=False

	#def removeUser

	@Slot()
	def removeUserList(self):

		self.showSettingsUserMessage={"show":False,"msgCode":"","type":""}
		self._usersModel.clear()
		self.usersInfo={}
		self.isUserAccessControlEnabled=False
		if self.usersInfo!=self.n4dManager.usersInfo:
			self.hasUserChanges=True
		else:
			self.hasUserChanges=(self.isUserAccessControlEnabled!=self.n4dManager.isUserAccessControlEnabled)

		if self.hasUserChanges:
			self.n4dManager.writeLog("Action: Removed user list")

	#def removeUserList

	def _updateUserList(self,userId,delete):

		if delete:
			self.usersInfo.pop(userId,None)
		else:
			if userId not in self.usersInfo:
				self.usersInfo[userId]={"isLocked":True}

		self.hasUserChanges=(self.usersInfo!=self.n4dManager.usersInfo)
		
	#def _updateUserList

	@Slot()
	def applyUserChanges(self):

		self.showSettingsUserMessage={"show":False,"msgCode":"","type":""}
		self.core.mainStack.showPopUp={"show":True,"msgCode":self.core.mainStack.SAVE_DATA_MSG}
		self.showUserChangesDialog=False
		self.updateUserInfoT=UpdateInfo(self.n4dManager,self.isUserAccessControlEnabled,self.usersInfo)
		self.updateUserInfoT.start()
		self.updateUserInfoT.infoUpdated.connect(self._applyUserChanges)
		self.updateUserInfoT.finished.connect(self.updateUserInfoT.deleteLater)

	#def applyUserChanges	

	@Slot(dict)
	def _applyUserChanges(self,ret):

		if ret.get("status"):
			self._updateUsersConfig()
			self.core.mainStack.closeGui=True
		else:
			self.core.mainStack.closeGui=False
			self.core.mainStack.moveToStack=""

		self.showSettingsUserMessage={"show":True,"msgCode":ret.get("code"),"type":ret.get("type")}

		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
			self.showSettingsUserMessage={"show":False,"msgCode":"","type":""}
			self.core.mainStack.moveToStack=""

		self.hasUserChanges=False
		self.core.mainStack.showPopUp={"show":False,"msgCode":""}

	#def _applyUserChanges

	@Slot()
	def cancelUserChanges(self):

		self.showSettingsUserMessage={"show":False,"msgCode":"","type":""}
		self.core.mainStack.showPopUp={"show":True,"msgCode":self.core.mainStack.RESTORE_DATA_MSG}
		self.showUserChangesDialog=False
		self._cancelUserChanges()

	#def cancelUserChanges

	def _cancelUserChanges(self):

		self._updateUsersConfig()
		self.hasUserChanges=False
		self.core.mainStack.showPopUp={"show":False,"msgCode":""}
		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
		self.core.mainStack.moveToStack=""
		
		self.core.mainStack.closeGui=True

	#def _cancelUserChanges

	def _updateUsersConfig(self):

		self.isUserAccessControlEnabled=copy.deepcopy(self.n4dManager.isUserAccessControlEnabled)
		self.usersInfo=copy.deepcopy(self.n4dManager.usersInfo)
		self._updateUserModel()
	
	#def _updateUsersConfig
	
#class Bridge

import Core

