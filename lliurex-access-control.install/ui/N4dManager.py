#!/usr/bin/python3

import xmlrpc.client
import ssl
import os
import json
import codecs
import pwd

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

	def setServer(self,server):

		context=ssl._create_unverified_context()	
		self.client=xmlrpc.client.ServerProxy("https://%s:9779"%server,allow_none=True,context=context)
	
	#def setServer

	def validateUser(self,user,password):
		
		userValidated=False
		try:
			ret=self.client.validate_user(user,password)
		except:
			return userValidated
			
		userValidated,self.user_groups=ret
			
		if userValidated:
			self.validation=(user,password)

		return userValidated

	#def validateUser

	def loadConfig(self):
		
		self.loadGroupConfig()
		self.loadUserConfig()

	#def loadConfig

	def loadGroupConfig(self):

		self.isAccessDenyGroupEnabled=self.client.isAccessDenyGroupEnabled(self.validation,"AccessControlManager")['status']
		self.groupsInfo=self.client.getGroupsInfo(self.validation,"AccessControlManager")['data']
		self.getGroupsConfig()
		
	#def loadGroupConfig()

	def loadUserConfig(self):
		
		self.isAccessDenyUserEnabled=self.client.isAccessDenyUserEnabled(self.validation,"AccessControlManager")['status']
		self.usersInfo=self.client.getUsersInfo(self.validation,"AccessControlManager")["data"]
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
			ret=self.client.disableAccessDenyGroup(self.validation,"AccessControlManager")
			if ret['status']:
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			else:
				result=[False,ret['msg']]

		else:
			if updateGroupInfo:
				ret=self.client.setGroupsInfo(self.validation,"AccessControlManager",groupsInfo)		
				if ret['status']:
					result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
				else:
					result=[False,ret['msg']]

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
			ret=self.client.setUsersInfo(self.validation,"AccessControlManager",usersInfo)
			if ret['status']:
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
				if disableControl:
					ret=self.client.disableAccessDenyUser(self.validation,"AccessControlManager")
					if ret['status']:		
						result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
					else:		
						result=[False,ret['msg']]
			else:
				result=[False,ret['msg']]

		if disableControl and not updateUsersInfo:
	
			ret=self.client.disableAccessDenyUser(self.validation,"AccessControlManager")		
			if ret['status']:
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			else:
				result=[False,ret['msg']]

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

		localAdminPID=1000
		isLocalAdmin=False

		try:
			gid = pwd.getpwnam(user).pw_gid
			if gid==localAdminPID:
				isLocalAdmin=True 
			else:
				isLocalAdmin=False
		except:
			isLocalAdmin=False

		return isLocalAdmin

	#def checkIfUserIsLocalAdmin

#class N4dManager
