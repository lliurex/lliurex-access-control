#!/usr/bin/python3

import n4d.client
import os
import json
import codecs

class N4dManager:

	APPLY_CHANGES_SUCCESSFUL=10
	APPLY_CHANGES_WITHOUT_GROUP=-70
	APPLY_CHANGES_WITHOUT_USER=-80

	def __init__(self,ticket):

		self.debug=True
		ticket=ticket.replace('##U+0020##',' ')
		self.defaultGroups={}
		self.groupsConfigData=[]
		self.sessionLang=""
		self.isAccessDenyGroupEnabled=False
		self.denyGroups=[]
		self.usersList=[]
		self.usersConfigData=[]
		self.isAccessDenyUserEnabled=False
		self.denyUsers=[]
		self.setServer(ticket)
		self.getSessionLang()
		self.loadConfig()


	#def __init__

	def setServer(self,ticket):

		tk=n4d.client.Ticket(ticket)
		self.client=n4d.client.Client(ticket=tk)
	
	#def setServer

	def loadConfig(self):
		
		self.loadGroupConfig()
		self.loadUserConfig()

	#def loadConfig

	def loadGroupConfig(self):

		self.isAccessDenyGroupEnabled=self.client.AccessControlManager.isAccessDenyGroupEnabled()
		self.denyGroups=self.client.AccessControlManager.getDenyGroups()
		self.defaultGroups=self.client.AccessControlManager.getGroupList()
		self.getGroupsConfig()
		
	#def loadGroupConfig()

	def loadUserConfig(self):
		
		self.isAccessDenyUserEnabled=self.client.AccessControlManager.isAccessDenyUserEnabled()
		self.denyUsers=self.client.AccessControlManager.getDenyUsers()
		self.usersList=self.client.AccessControlManager.getUsersList()
		self.getUsersConfig()

	#def loadUserConfig

	def getSessionLang(self):

		lang=os.environ["LANG"]
		
		if 'valencia' in lang:
			self.sessionLang="ca@valencia"
		else:
			self.sessionLang="es"

	#def getSessionLang

	def getGroupsConfig(self):

		self.groupsConfigData=[]

		for item in self.defaultGroups:
			tmp={}
			tmp["groupId"]=item
			if item in self.denyGroups:
				tmp["isChecked"]=True
			else:
				tmp["isChecked"]=False
			tmp["description"]=self.defaultGroups[item][self.sessionLang]

			self.groupsConfigData.append(tmp)

	#def getGroupsConfig 

	def getUsersConfig(self):

		#self._readDefaultGroups()
		self.usersConfigData=[]

		for item in self.usersList:
			tmp={}
			tmp["userId"]=item
			if item in self.denyUsers:
				tmp["isChecked"]=True
			else:
				tmp["isChecked"]=False
			self.usersConfigData.append(tmp)

		for item in self.denyUsers:
			tmp={}
			if item not in self.usersList:
				tmp["userId"]=item
				tmp["isChecked"]=True
				self.usersList.append(item)
				self.usersConfigData.append(tmp)

	#def getUsersConfig 			
			

	def applyGroupChanges(self,groupAccessControl,denyGroups):

		disableControl=False
		updateDenyGroup=False
		result=[]


		if not groupAccessControl:
			if groupAccessControl != self.isAccessDenyGroupEnabled:
				disableControl=True
		else:
			if len(denyGroups)==0:
				result=[False,N4dManager.APPLY_CHANGES_WITHOUT_GROUP]
				return result
			else:
				if denyGroups != self.denyGroups:
					updateDenyGroup=True

		if disableControl:
			try:
				ret=self.client.AccessControlManager.disableAccessDenyGroup()
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				result=[False,e.code]

		if updateDenyGroup:
			try:
				ret=self.client.AccessControlManager.setDenyGroups(denyGroups)		
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				result=[False,e.code]

		if result[0]:
			self.loadGroupConfig()
		return result

	#def applyGroupChanges

	def applyUsersChanges(self,userAccessControl,denyUsers,usersList):

		disableControl=False
		updateDenyUser=False
		updateUsersList=False
		result=[]

		if not userAccessControl:
			if userAccessControl != self.isAccessDenyUserEnabled:
				disableControl=True

			if usersList!=self.usersList:
					updateUsersList=True	
		else:
			if len(usersList)==0:
				result=[False,N4dManager.APPLY_CHANGES_WITHOUT_USER]
				return result
			else:
				if usersList!=self.usersList:
					updateUsersList=True

			if len(denyUsers)==0:
				result=[False,N4dManager.APPLY_CHANGES_WITHOUT_USER]
				return result
			else:
				if denyUsers != self.denyUsers:
					updateDenyUser=True

		if disableControl:
			try:
				ret=self.client.AccessControlManager.disableAccessDenyUser()
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				result=[False,e.code]

		if updateDenyUser:
			try:
				ret=self.client.AccessControlManager.setDenyUsers(denyUsers)		
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				result=[False,e.code]

		if updateUsersList:
			try:
				ret=self.client.AccessControlManager.setUsersList(usersList)
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				result=[False,e.code]
		
		if result[0]:
			self.loadUserConfig()
		return result

	#def applyUsersChanges


#class N4dManager
