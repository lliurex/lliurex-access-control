#!/usr/bin/python3

import n4d.client
import os
import json
import codecs
import pwd
import grp

class N4dManager:

	APPLY_CHANGES_SUCCESSFUL=10
	APPLY_CHANGES_WITHOUT_GROUP=-70
	APPLY_CHANGES_WITHOUT_USER=-80

	def __init__(self):

		self.debug=True
		self.groupsInfo={}
		self.groupsConfigData=[]
		self.sessionLang=""
		self.isAccessDenyGroupEnabled=False
		self.usersInfo={}
		self.usersConfigData=[]
		self.isAccessDenyUserEnabled=False
		self.getSessionLang()

	#def __init__

	def setServer(self,ticket):
		
		ticket=ticket.replace('##U+0020##',' ')
		tk=n4d.client.Ticket(ticket)
		self.client=n4d.client.Client(ticket=tk)
	
	#def setServer

	def loadConfig(self):
		
		self.loadGroupConfig()
		self.loadUserConfig()

	#def loadConfig

	def loadGroupConfig(self):

		self.isAccessDenyGroupEnabled=self.client.AccessControlManager.isAccessDenyGroupEnabled()
		self.groupsInfo=self.client.AccessControlManager.getGroupsInfo()
		self.getGroupsConfig()
		
	#def loadGroupConfig()

	def loadUserConfig(self):
		
		self.isAccessDenyUserEnabled=self.client.AccessControlManager.isAccessDenyUserEnabled()
		self.usersInfo=self.client.AccessControlManager.getUsersInfo()
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

		for item in self.groupsInfo:
			tmp={}
			tmp["groupId"]=item
			tmp["isLocked"]=self.groupsInfo[item]["isLocked"]
			tmp["description"]=self.groupsInfo[item][self.sessionLang]
			self.groupsConfigData.append(tmp)

	#def getGroupsConfig 

	def getUsersConfig(self):

		#self._readDefaultGroups()
		self.usersConfigData=[]

		for item in self.usersInfo:
			if item !="":
				tmp={}
				tmp["userId"]=item
				tmp["isLocked"]=self.usersInfo[item]["isLocked"]
				self.usersConfigData.append(tmp)

	#def getUsersConfig 			
			

	def applyGroupChanges(self,groupAccessControl,groupsInfo):

		disableControl=False
		updateGroupInfo=False
		result=[]


		if not groupAccessControl:
			if groupAccessControl != self.isAccessDenyGroupEnabled:
				disableControl=True
		else:
			if not self.thereAreGroupsLocked(groupsInfo):
				result=[False,N4dManager.APPLY_CHANGES_WITHOUT_GROUP]
				return result
			else:
				if groupsInfo != self.groupsInfo:
					updateGroupInfo=True

		if disableControl:
			try:
				ret=self.client.AccessControlManager.disableAccessDenyGroup()
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				result=[False,e.code]

		else:
			if updateGroupInfo:
				try:
					ret=self.client.AccessControlManager.setGroupsInfo(groupsInfo)		
					result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
				except n4d.client.CallFailedError as e:
					result=[False,e.code]

		if result[0]:
			self.loadGroupConfig()
		return result

	#def applyGroupChanges

	def applyUsersChanges(self,userAccessControl,usersInfo):

		disableControl=False
		updateUsersInfo=False
		result=[]

		if usersInfo!=self.usersInfo:
			updateUsersInfo=True

		if userAccessControl != self.isAccessDenyUserEnabled:
			if userAccessControl and not self.thereAreUsersLocked(usersInfo):
				result=[False,N4dManager.APPLY_CHANGES_WITHOUT_USER]
				return result
			else:
				if not userAccessControl:
					disableControl=True
	
		if updateUsersInfo:
			try:
				ret=self.client.AccessControlManager.setUsersInfo(usersInfo)
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
				if disableControl:
					ret=self.client.AccessControlManager.disableAccessDenyUser()		
					result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				result=[False,e.code]

		if disableControl and not updateUsersInfo:
			try:
				ret=self.client.AccessControlManager.disableAccessDenyUser()		
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				result=[False,e.code]

		if result[0]:
			self.loadUserConfig()
		return result

	#def applyUsersChanges

	def thereAreGroupsLocked(self,groupsInfo):

		thereAreGroupLocked=False

		for item in groupsInfo:
			if groupsInfo[item]["isLocked"]:
				thereAreGroupLocked=True
				break

		return thereAreGroupLocked

	#def thereAreGroupsLocked
	
	def thereAreUsersLocked(self,usersInfo):

		thereAreUsersLocked=False

		for item in usersInfo:
			if usersInfo[item]["isLocked"]:
				thereAreUsersLocked=True
				break

		return thereAreUsersLocked

	#def thereAreUsersLocked
	
	def checkIfUserIsLocalAdmin(self,user):

		adminGroups=["sudo","admins","adm"]
		isLocalAdmin=False

		try:
			gid = pwd.getpwnam(user).pw_gid
			groups_gid=os.getgrouplist(user,gid)
			user_groups=[grp.getgrgid(x).gr_name for x in groups_gid]			
			for element in user_groups:
				if element in adminGroups:
					isLocalAdmin=True 
					break
		except:
			isLocalAdmin=False

		return isLocalAdmin

	#def checkIfUserIsLocalAdmin

#class N4dManager
