#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time

import UsersModel
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
		self.ret=Bridge.n4dMan.applyUsersChanges(self.enabledInfo,self.listInfo)

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
		self.retCurrentUser=Bridge.n4dMan.checkIfUserIsCurrrentUser(self.newUser)

		if not self.retCurrentUser[0]:
			self.retAdminUser=Bridge.n4dMan.checkIfUserIsValidGroup(self.newUser)
		else:
			if len(self.newUser)>1:
				self.retAdminUser=Bridge.n4dMan.checkIfUserIsValidGroup(self.newUser)
		
	#def run

#class AddUser

class Bridge(QObject):

	USER_DUPLICATE_ERROR=-90
	CURRENT_USER_ERROR=-100
	USERS_NOT_ALLOWED_ERROR=-200
	
	def __init__(self,ticket=None):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.n4dMan=self.core.n4dManager
		self._usersModel=UsersModel.UsersModel()
		self._isAccessDenyUserEnabled=False
		self._settingsUserChanged=False
		self._showSettingsUserMessage=[False,"","Success"]
		self._showLocalAdminDialog=False
		self._showUserChangesDialog=False
		self._enableUserConfig=True
		self.tmpNewUser=[]
		self.tmpAdminUser=[]

	#def __init__

	def getUserConfig(self):		

		self.isAccessDenyUserEnabled=copy.deepcopy(Bridge.n4dMan.isAccessDenyUserEnabled)
		self.usersInfo=copy.deepcopy(Bridge.n4dMan.usersInfo)
		self.enableUserConfig=Bridge.n4dMan.enableUserConfig
		self._updateUserModel()

	#def getUserConfig

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

	def _getShowUserChangesDialog(self):

		return self._showUserChangesDialog

	#def _getShowUserChangesDialog	

	def _setShowUserChangesDialog(self,showUserChangesDialog):
		
		if self._showUserChangesDialog!=showUserChangesDialog:
			self._showUserChangesDialog=showUserChangesDialog		
			self.on_showUserChangesDialog.emit()

	#def _setShowUserChangesDialog
	
	def _getEnableUserConfig(self):

		return self._enableUserConfig

	#def _getEnableUserConfig

	def _setEnableUserConfig(self,enableUserConfig):

		if self._enableUserConfig!=enableUserConfig:
			self._enableUserConfig=enableUserConfig
			self.on_enableUserConfig.emit()

	#def _setEnableUserConfig

	def _getUsersModel(self):
		
		return self._usersModel

	#def _getUsersModel

	def _updateUserModel(self):

		ret=self._usersModel.clear()
		usersEntries=Bridge.n4dMan.usersConfigData
		for item in usersEntries:
			if item["userId"]!="":
				self._usersModel.appendRow(item["userId"],item["isLocked"])
		
	#def _updateUserModel

	@Slot(bool)
	def manageUserAccessControl(self,value):

		self.showSettingsUserMessage=[False,"","Success"]

		if value!=self.isAccessDenyUserEnabled:
			self.isAccessDenyUserEnabled=value
			if self.isAccessDenyUserEnabled!=Bridge.n4dMan.isAccessDenyUserEnabled:
				self.settingsUserChanged=True
			else:
				self.settingsUserChanged=False

	#def manageUserAccessControl
	
	@Slot('QVariantList')
	def manageUserChecked(self,value):

		self.showSettingsUserMessage=[False,"","Success"]
		userId=value[0]
		userChecked=value[1]

		if self.usersInfo[userId]["isLocked"]!=userChecked:
			self.usersInfo[userId]["isLocked"]=userChecked
			if userId in Bridge.n4dMan.usersInfo.keys():
				if self.usersInfo!=Bridge.n4dMan.usersInfo:
					self.settingsUserChanged=True
				else:
					self.settingsUserChanged=False
			else:		
				self.settingsUserChanged=True

		if not Bridge.n4dMan.thereAreUsersLocked(self.usersInfo):
			self.isAccessDenyUserEnabled=False
		
	#def manageUserChecked

	@Slot(str)
	def addUser(self,userId):

		self.showSettingsUserMessage=[False,"","Success"]
		self.core.mainStack.closePopUp=False
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

			if len(self.userId)>0:
				nextStep=True
				if not Bridge.n4dMan.isCurrentUserAdmin:
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
						self.showSettingsUserMessage=[True,Bridge.CURRENT_USER_ERROR,"Warning"]
				
					else:
						if invalidUsers:
							self.showSettingsUserMessage=[True,Bridge.USERS_NOT_ALLOWED_ERROR,"Warning"]
						
					if not Bridge.n4dMan.thereAreUsersLocked(self.usersInfo):
						self.isAccessDenyUserEnabled=False
				
			else:
				if not invalidUsers:
					self.showSettingsUserMessage=[True,Bridge.CURRENT_USER_ERROR,"Warning"]
				else:
					self.showSettingsUserMessage=[True,Bridge.USERS_NOT_ALLOWED_ERROR,"Warning"]

		else:
			self.showSettingsUserMessage=[True,Bridge.USER_DUPLICATE_ERROR,"Warning"]
		
		self.core.mainStack.closePopUp=True

	#def _checkNewUser

	@Slot(str)
	def manageLocalAdminDialog(self,action):

		self.showLocalAdminDialog=False

		if action=="Accept":
			Bridge.n4dMan.writeLog("Action: Added admin user to user list: %s"%self.tmpAdminUser)
			nextStep=True
		else:
			for item in range(len(self.tmpNewUser)-1,-1,-1):
				if self.tmpNewUser[item] in self.tmpAdminUser:
					self.tmpNewUser.pop(item)

		if len(self.tmpNewUser)>0:
			for item in self.tmpNewUser:
				self._usersModel.appendRow(item,True)
				self._updateUserList(item,False)
			if not Bridge.n4dMan.thereAreUsersLocked(self.usersInfo):
				self.isAccessDenyUserEnabled=False

		if self.addNewUser.retCurrentUser[0]:
			self.showSettingsUserMessage=[True,Bridge.CURRENT_USER_ERROR,"Warning"]

	#def manageLocalAdminDialog

	@Slot(int)
	def removeUser(self,index):

		self.showSettingsUserMessage=[False,"","Success"]
		tmpUser=self._usersModel._entries[index]
		self._usersModel.removeRow(index)
		self._updateUserList(tmpUser["userId"],True)
		if not Bridge.n4dMan.thereAreUsersLocked(self.usersInfo):
			self.isAccessDenyUserEnabled=False

	#def removeUser

	@Slot()
	def removeUserList(self):

		self.showSettingsUserMessage=[False,"","Success"]
		self._usersModel.clear()
		self.usersInfo={}
		self.isAccessDenyUserEnabled=False
		if self.usersInfo!=Bridge.n4dMan.usersInfo:
			self.settingsUserChanged=True
		else:
			if self.isAccessDenyUserEnabled!=Bridge.n4dMan.isAccessDenyUserEnabled:
				self.settingsUserChanged=True 
			else:
				self.settingsUserChanged=False

		if self.settingsUserChanged:
			Bridge.n4dMan.writeLog("Action: Removed user list")

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
			if tmpList!=Bridge.n4dMan.usersInfo:
				self.settingsUserChanged=True
			else:
				self.settingsUserChanged=False

			self.usersInfo=tmpList

	#def _updateUserList

	@Slot()
	def applyUserChanges(self):

		self.showSettingsUserMessage=[False,"","Success"]
		self.core.mainStack.closePopUp=False
		self.showUserChangesDialog=False
		self.updateUserInfo=UpdateInfo(self.isAccessDenyUserEnabled,self.usersInfo)
		self.updateUserInfo.start()
		self.updateUserInfo.finished.connect(self._applyUserChanges)

	#def applyUserChanges	

	def _applyUserChanges(self):

		if self.updateUserInfo.ret[0]:
			self._updateUsersConfig()
			self.showSettingsUserMessage=[True,self.updateUserInfo.ret[1],"Success"]
			self.core.mainStack.closeGui=True
		else:
			self.showSettingsUserMessage=[True,self.updateUserInfo.ret[1],"Error"]
			self.core.mainStack.closeGui=False
			self.core.mainStack.moveToStack=""

		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
			self.showSettingsUserMessage=[False,"","Info"]
			self.core.mainStack.moveToStack=""

		self.settingsUserChanged=False
		self.core.mainStack.closePopUp=True


	#def _applyUserChanges

	@Slot()
	def cancelUserChanges(self):

		self.showSettingsUserMessage=[False,"","Success"]
		self.core.mainStack.closePopUp=False
		self.showUserChangesDialog=False
		self._cancelUserChanges()

	#def cancelUserChanges

	def _cancelUserChanges(self):

		self._updateUsersConfig()
		self.settingsUserChanged=False
		self.core.mainStack.closePopUp=True
		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
		self.core.mainStack.moveToStack=""
		
		self.core.mainStack.closeGui=True

	#def _cancelUserChanges

	def _updateUsersConfig(self):

		self.isAccessDenyUserEnabled=copy.deepcopy(Bridge.n4dMan.isAccessDenyUserEnabled)
		self.usersInfo=copy.deepcopy(Bridge.n4dMan.usersInfo)
		self._updateUserModel()
	
	#def _updateUsersConfig

	on_isAccessDenyUserEnabled=Signal()
	isAccessDenyUserEnabled=Property(bool,_getIsAccessDenyUserEnabled,_setIsAccessDenyUserEnabled,notify=on_isAccessDenyUserEnabled)
	
	on_settingsUserChanged=Signal()
	settingsUserChanged=Property(bool,_getSettingsUserChanged,_setSettingsUserChanged, notify=on_settingsUserChanged)

	on_showSettingsUserMessage=Signal()
	showSettingsUserMessage=Property('QVariantList',_getShowSettingsUserMessage,_setShowSettingsUserMessage,notify=on_showSettingsUserMessage)

	on_showLocalAdminDialog=Signal()
	showLocalAdminDialog=Property(bool,_getShowLocalAdminDialog,_setShowLocalAdminDialog,notify=on_showLocalAdminDialog)

	on_showUserChangesDialog=Signal()
	showUserChangesDialog=Property(bool,_getShowUserChangesDialog,_setShowUserChangesDialog, notify=on_showUserChangesDialog)

	on_enableUserConfig=Signal()
	enableUserConfig=Property(bool,_getEnableUserConfig,_setEnableUserConfig,notify=on_enableUserConfig)

	usersModel=Property(QObject,_getUsersModel,constant=True)

#class Bridge

import Core

