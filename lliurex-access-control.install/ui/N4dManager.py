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
	APPLY_CHANGES_WITHOUT_CODE=-90
	CDC_CODE_NOT_VALID=-101

	def __init__(self):

		self.debug=True
		self.groupsInfo={}
		self.groupsConfigData=[]
		self.sessionLang=""
		self.isAccessDenyGroupEnabled=False
		self.usersInfo={}
		self.usersConfigData=[]
		self.isAccessDenyUserEnabled=False
		self.isCDCAccessControlAllowed=False
		self.isAccessDenyCDCEnabled=False
		self.cdcInfo={}
		self.defaultCDCCode=""
		self.getSessionLang()
		self.adminGroups=["sudo","admins","adm"]
		self.enableUserConfig=True

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
		
		self.isCurrentUserAdmin=self._checkIfUserIsAdmin(self.currentUser)
		self.loadGroupConfig()
		self.loadUserConfig()
		self.loadCDCConfig()

	#def loadConfig

	def loadGroupConfig(self,step="Initial"):

		self.writeLog("Access Control by Group. %s configuration:"%step)
		self.isAccessDenyGroupEnabled=self.client.AccessControlManager.isAccessDenyGroupEnabled()
		self.writeLog("- Access control by group activated: %s"%(str(self.isAccessDenyGroupEnabled)))
		if step=="Initial":
			initLoad=True 
		else:
			initLoad=False
		self.groupsInfo=self.client.AccessControlManager.getGroupsInfo(initLoad)
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

	def loadCDCConfig(self,step="Initial"):

		self.writeLog("Access Control by CDC. %s configuration:"%step)
		self.isCDCAccessControlAllowed=self.client.AccessControlManager.isCDCAccessControlAllowed()
		self.writeLog("- Access Control by CDC allowed: %s"%(str(self.isCDCAccessControlAllowed)))
		self.isAccessDenyCDCEnabled=self.client.AccessControlManager.isAccessDenyCDCEnabled()
		self.writeLog("- Access Control by CDC enabled: %s"%(str(self.isAccessDenyCDCEnabled)))
		self.cdcInfo=self.client.AccessControlManager.getCDCInfo()
		if self.cdcInfo["code"]!="":
			currentCode=self.cdcInfo["code"]
		else:
			self.defaultCDCCode=self._getCurrentUserCDCCode()
			currentCode="None"
		self.writeLog("- Center code to control access: %s"%(str(currentCode)))

	#def loadCDCConfig
	
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
			hide=False
			if item == 'teachers':
				if not self.isCurrentUserAdmin:
					hide=True
			if not hide:
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
			hide=False
			if item !="":
				if self._checkIfUserIsTeacher(item) or self._checkIfUserIsAdmin(item):
					if not self.isCurrentUserAdmin:
						hide=True
						self.enableUserConfig=False
				if not hide:
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
				self.writeLog("- Action: change group list")
				ret=self.client.AccessControlManager.setGroupsInfo(groupsInfo)		
				self.writeLog("- New groups with locked access: Changes apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
				if disableControl:
					self.writeLog("- Action: disable access control by group")
					ret=self.client.AccessControlManager.disableAccessDenyGroup()
					self.writeLog("- Disable access control by group: Change apply successful")
					result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]

			except n4d.client.CallFailedError as e:
				self.writeLog("- Error applying changes: %s"%e.code)
				result=[False,e.code]


		if disableControl and not updateGroupInfo:
			try:
				self.writeLog("- Action: disable access control by group")
				ret=self.client.AccessControlManager.disableAccessDenyGroup()
				self.writeLog("- Disable access control by group: Changes apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				self.writeLog("- Error applying changes: %s"%e.code)
				result=[False,e.code]

		if enableControl:
			try:
				self.writeLog("- Action: enable access control by group")
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
				self.writeLog("- Action: change user list")
				ret=self.client.AccessControlManager.setUsersInfo(usersInfo)
				self.writeLog("- New users with locked access: Changes apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
				if disableControl:
					self.writeLog("- Action: disable access control by user")
					ret=self.client.AccessControlManager.disableAccessDenyUser()
					self.writeLog("- Disable access control by user: Change apply successful")
					result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				self.writeLog("- Error applying changes: %s"%e.code)
				result=[False,e.code]

		if disableControl and not updateUsersInfo:
			try:
				self.writeLog("- Action: disable access control by user")
				ret=self.client.AccessControlManager.disableAccessDenyUser()
				self.writeLog("- Disable access control by user: Change apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				self.writeLog("- Error applying changes: %s"%e.code)
				result=[False,e.code]

		if enableControl:
			try:
				self.writeLog("- Action: enable access control by user")
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
	
	def checkIfUserIsValidGroup(self,userList):

		#adminGroups=["sudo","admins","adm"]
		isLocalAdmin=False
		localAdminList=[]
		isTeacher=False
		teachersList=[]
	
		for item in userList:
			if item != self.currentUser:
				userGroups=self._getUserGroups(item)
				for element in userGroups:
					if element in self.adminGroups:
						localAdminList.append(item) 
				
				if not self.isCurrentUserAdmin:
					if self._checkIfUserIsTeacher(item):
						teachersList.append(item)

		if len(localAdminList)>0:
			isLocalAdmin=True
		
		return [isLocalAdmin,localAdminList,teachersList]

	#def checkIfUserIsValidGroup

	def checkIfUserIsCurrrentUser(self,userList):

		userListFilter=[self.currentUser,'root']
		isCurrentUser=False
		currentUserList=[]

		for user in userList:
			if user in userListFilter:
				currentUserList.append(user)

		if len(currentUserList)>0:
			isCurrentUser=True

		return [isCurrentUser,currentUserList]

	#def checkIfUserIsCurrrentUser 
	
	def _checkIfUserIsTeacher(self,user):
		
		userGroups=self._getUserGroups(user)
		
		if 'teachers' in userGroups:
			return True
		
		return False
		
	#def checkIfUserIsTeacher
	
	def _checkIfUserIsAdmin(self,user):
		
		userGroups=self._getUserGroups(user)
		ret=False
		for item in userGroups:
			if item in self.adminGroups:
				ret=True
				break
		
		return ret
		
	#def _checkIfUserIsAdmin

	def applyCDCChanges(self,cdcAccessControl,cdcInfo):

		disableControl=False
		enableControl=False
		updateCDCInfo=False
		result=[]

		if self.isCorrectCode(cdcInfo["code"]):
			if (cdcInfo["code"]!=self.cdcInfo["code"]) and (cdcInfo["code"]!=""):
				updateCDCInfo=True

			if not cdcAccessControl:
				if cdcInfo["code"]=="":
					cdcInfo={}
					updateCDCInfo=True
				else:
					if cdcAccessControl != self.isAccessDenyCDCEnabled:
						disableControl=True
			else:
				if cdcInfo["code"]=="":
					result=[False,N4dManager.APPLY_CHANGES_WITHOUT_CODE]
					return result
				else:
					if not updateCDCInfo:
						enableControl=True

			self.writeLog("Changes in configuration of access control by CDC:")		
			if updateCDCInfo:
				try:
					self.writeLog("- Action: change center code")
					ret=self.client.AccessControlManager.setCDCInfo(cdcInfo)		
					self.writeLog("- New center code: Changes apply successful")
					result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
					if disableControl:
						self.writeLog("- Action: disable access control by CDC")
						ret=self.client.AccessControlManager.disableAccessDenyCDC()
						self.writeLog("- Disable access control by CDC: Change apply successful")
						result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]

				except n4d.client.CallFailedError as e:
					self.writeLog("- Error applying changes: %s"%e.code)
					result=[False,e.code]

			if disableControl and not updateCDCInfo:
				try:
					self.writeLog("- Action: disable access control by CDC")
					ret=self.client.AccessControlManager.disableAccessDenyCDC(True)
					self.writeLog("- Disable access control by CDC: Changes apply successful")
					result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
				except n4d.client.CallFailedError as e:
					self.writeLog("- Error applying changes: %s"%e.code)
					result=[False,e.code]

			if enableControl:
				try:
					self.writeLog("- Action: enable access control by CDC")
					ret=self.client.AccessControlManager.setCDCInfo(cdcInfo)		
					self.writeLog("- Enable access control by CDC: Changes apply successful")
					result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
				except n4d.client.CallFailedError as e:
					self.writeLog("- Error applying changes: %s"%e.code)
					result=[False,e.code]

			if result[0]:
				self.loadCDCConfig("End")
		else:
			result=[False,N4dManager.CDC_CODE_NOT_VALID]
		
		return result

	#def applyCDCChanges

	def isCorrectCode(self,cdcCode):

		if cdcCode!="":
			if len(cdcCode)==8:
				if cdcCode.isdecimal():
					head=cdcCode[0:2]
					if head in ['03','12','46']:
						return True
			return False
		else:
			return True

	#def isCorrectCode
	
	def _getUserGroups(self,user):
		
		userGroups=[]
		try:
			gid = pwd.getpwnam(user).pw_gid
			groupsGid=os.getgrouplist(user,gid)
			userGroups=[grp.getgrgid(x).gr_name for x in groupsGid]			
		except Exception as e:
			pass
			
		return userGroups		
	
	#def _getUserGroups

	def _getCurrentUserCDCCode(self):

		cdcCode=""
		userGroups=self._getUserGroups(self.currentUser)

		if len(userGroups)>0:
			for item in userGroups:
				if item.startswith("GRP_"):
					cdcCode=item.split("GRP_")[1].strip()
					if self.isCorrectCode(cdcCode):
						return cdcCode
		return cdcCode

	#def _getCurrentUserCDCCode

	def writeLog(self,msg):

		syslog.openlog("ACCESS-CONTROL")
		syslog.syslog(msg)

	#def writeLog

#class N4dManager
