#!/usr/bin/python3

import n4d.client
import os
import sys
import syslog
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
		self.currentUser=ticket.split(' ')[2]
		tk=n4d.client.Ticket(ticket)
		self.client=n4d.client.Client(ticket=tk)

		self.writeLog("Init session in lliurex-access-control GUI")
		self.writeLog("User login in GUI: %s"%self.currentUser)
	
	#def setServer

	def loadConfig(self):
		
		self.loadGroupConfig()
		self.loadUserConfig()

	#def loadConfig

	def loadGroupConfig(self,step="Initial"):

		self.writeLog("Access Control by Group. %s configuration:"%step)
		self.isAccessDenyGroupEnabled=self.client.AccessControlManager.isAccessDenyGroupEnabled()
		self.writeLog("- Access control by group activated: %s"%(str(self.isAccessDenyGroupEnabled)))
		self.groupsInfo=self.client.AccessControlManager.getGroupsInfo()
		self.writeLog("- Groups with restricted access: ")
		for item in self.groupsInfo:
			self.writeLog("  - %s: locked access %s"%(item,str(self.groupsInfo[item]["isLocked"])))
		self.getGroupsConfig()
		
	#def loadGroupConfig()

	def loadUserConfig(self,step="Initial"):

		self.writeLog("Access Control by User. %s configuration:"%step)
		self.isAccessDenyUserEnabled=self.client.AccessControlManager.isAccessDenyUserEnabled()
		self.writeLog("- Access Control by User activated: %s"%(str(self.isAccessDenyUserEnabled)))
		self.usersInfo=self.client.AccessControlManager.getUsersInfo()
		self.writeLog("- Users with restricted access: ")
		if len(self.usersInfo)>0:
				for item in self.usersInfo:
					self.writeLog("  - %s: locked access %s"%(item,str(self.usersInfo[item]["isLocked"])))
		else:
			self.writeLog("  - There is no user list")
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
		enableControl=False

		result=["",""]

		if groupsInfo != self.groupsInfo:
			updateGroupInfo=True

		if not groupAccessControl:
			if groupAccessControl != self.isAccessDenyGroupEnabled:
				disableControl=True
		else:
			if not self.thereAreGroupsLocked(groupsInfo):
				result=[False,N4dManager.APPLY_CHANGES_WITHOUT_GROUP]
				return result
			else:
				if not updateGroupInfo:
					enableControl=True

		self.writeLog("Changes in configuration of access control by Group:")		
		if updateGroupInfo:
			try:
				self.writeLog("- Try to change group list")
				ret=self.client.AccessControlManager.setGroupsInfo(groupsInfo)		
				self.writeLog("- New groups with locked access: Changes apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
				if disableControl:
					self.writeLog("- Try to disable access control by group")
					ret=self.client.AccessControlManager.disableAccessDenyGroup()
					self.writeLog("- Disable access control by group: Change apply successful")
					result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]

			except n4d.client.CallFailedError as e:
				self.writeLog("- Error applying changes: %s"%e.code)
				result=[False,e.code]


		if disableControl and not updateGroupInfo:
			try:
				self.writeLog("- Try to disable access control by group")
				ret=self.client.AccessControlManager.disableAccessDenyGroup()
				self.writeLog("- Disable access control by group: Changes apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				self.writeLog("- Error applying changes: %s"%e.code)
				result=[False,e.code]

		if enableControl:
			try:
				self.writeLog("- Try to enable access control by group")
				ret=self.client.AccessControlManager.setGroupsInfo(groupsInfo)		
				self.writeLog("- Enable access control by group: Changes apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				self.writeLog("- Error applying changes: %s"%e.code)
				result=[False,e.code]

		if result[0]:
			self.loadGroupConfig("End")
		return result

	#def applyGroupChanges

	def applyUsersChanges(self,userAccessControl,usersInfo):

		disableControl=False
		enableControl=False
		updateUsersInfo=False
		result=[]

		if usersInfo!=self.usersInfo:
			updateUsersInfo=True

		if not userAccessControl:
			if userAccessControl != self.isAccessDenyUserEnabled:
				disableControl=True
		else:
			if not self.thereAreUsersLocked(usersInfo):
				result=[False,N4dManager.APPLY_CHANGES_WITHOUT_USER]
				return result
			else:
				if not updateUsersInfo:
					enableControl=True

		self.writeLog("Changes in configuration of access control by User:")		

		if updateUsersInfo:
			try:
				self.writeLog("- Try to change user list")
				ret=self.client.AccessControlManager.setUsersInfo(usersInfo)
				self.writeLog("- New users with locked access: Changes apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
				if disableControl:
					self.writeLog("- Try to disable access control by user")
					ret=self.client.AccessControlManager.disableAccessDenyUser()
					self.writeLog("- Disable access control by user: Change apply successful")
					result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				self.writeLog("- Error applying changes: %s"%e.code)
				result=[False,e.code]

		if disableControl and not updateUsersInfo:
			try:
				self.writeLog("- Try to disable access control by user")
				ret=self.client.AccessControlManager.disableAccessDenyUser()
				self.writeLog("- Disable access control by user: Change apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				self.writeLog("- Error applying changes: %s"%e.code)
				result=[False,e.code]

		if enableControl:
			try:
				self.writeLog("- Try to enable access control by user")
				ret=self.client.AccessControlManager.setUsersInfo(usersInfo)
				self.writeLog("- Enable access control by user: Change apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				self.writeLog("- Error applying changes: %s"%e.code)
				result=[False,e.code]


		if result[0]:
			self.loadUserConfig("End")
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

	def checkIfUserIsCurrrentUser(self,user):

		userListFilter=[self.currentUser,'root']
		isCurrentUser=False
		
		if user in userListFilter:
			isCurrentUser=True 

		return isCurrentUser

	#def checkIfUserIsCurrrentUser 

	def writeLog(self,msg):

		syslog.openlog("ACCESS-CONTROL")
		syslog.syslog(msg)

	#def writeLog

#class N4dManager
