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

	KIRIGAMI_MSG_OK=0
	KIRIGAMI_MSG_ERROR=1
	KIRIGAMI_MSG_WARNING=2
	KIRIGAMI_MSG_INFO=3

	def __init__(self):

		self.debug=True
		self.groupsInfo={}
		self.groupsConfigData=[]
		self.sessionLang=""
		self.isGroupAccessControlEnabled=False
		self.usersInfo={}
		self.usersConfigData=[]
		self.isUserAccessControlEnabled=False
		self.isCDCAccessControlAllowed=False
		self.isCDCAccessControlEnabled=False
		self.cdcInfo={}
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
		self.writeLog(f"User login in GUI: {self.currentUser}")
	
	#def setServer

	def loadConfig(self):
		
		self.isCurrentUserAdmin=self._checkIfUserIsAdmin(self.currentUser)
		self.loadGroupConfig()
		self.loadUserConfig()
		self.loadCDCConfig()

	#def loadConfig

	def loadGroupConfig(self,step="Initial"):

		self.writeLog(f"Access Control by Group. {step} configuration:")
		self.isGroupAccessControlEnabled=self.client.AccessControlManager.is_access_denied_group_enabled()
		self.writeLog(f"- Access control by group activated: {self.isGroupAccessControlEnabled}")
		
		initLoad=(step=="Initial")
		self.groupsInfo=self.client.AccessControlManager.get_groups_info(initLoad)
		self.writeLog("- Groups with restricted access: ")
		
		for groupName,groupData in self.groupsInfo.items():
			self.writeLog(f"  - {groupName}: locked access {groupData.get('isLocked',False)}")
		
		self.getGroupsConfig()
		
	#def loadGroupConfig()

	def loadUserConfig(self,step="Initial"):

		self.writeLog(f"Access Control by User. {step} configuration:")
		self.isUserAccessControlEnabled=self.client.AccessControlManager.is_access_denied_user_enabled()
		self.writeLog(f"- Access Control by User activated: {self.isUserAccessControlEnabled}")
		
		self.usersInfo=self.client.AccessControlManager.get_users_info()
		self.writeLog("- Users with restricted access: ")
		
		if self.usersInfo:
			for userName,userData in self.usersInfo.items():
				self.writeLog(f"  - {userName}: locked access {userData.get('isLocked',False)}")
		else:
			self.writeLog("  - There is no user list")
		
		self.getUsersConfig()

	#def loadUserConfig

	def loadCDCConfig(self,step="Initial"):

		self.writeLog(f"Access Control by CDC. {step} configuration:")
		self.isCDCAccessControlAllowed=self.client.AccessControlManager.is_cdc_access_control_allowed()
		self.writeLog(f"- Access Control by CDC allowed: {self.isCDCAccessControlAllowed}")
		
		self.isCDCAccessControlEnabled=self.client.AccessControlManager.is_access_denied_cdc_enabled()
		self.writeLog(f"- Access Control by CDC enabled: {self.isCDCAccessControlEnabled}")
		
		self.cdcInfo=self.client.AccessControlManager.get_cdc_info()
		code=self.cdcInfo.get("code","")
		currentCode=code if code!="" else "None"
		self.writeLog(f"- Center code to control access: {currentCode}")

	#def loadCDCConfig
	
	def getSessionLang(self):

		language=os.environ.get("LANGUAGE","")
		if language!="":
			tmpLang=language.split(":")[0]
		else:
			tmpLang=os.environ.get("LANG","")
		
		if 'valencia' in tmpLang:
			self.sessionLang="ca@valencia"
		elif 'es':
			self.sessionLang="es"
		else:
			self.sessionLang="default"

	#def getSessionLang

	def getGroupsConfig(self):

		self.groupsConfigData=[]
				
		for groupId,groupData in self.groupsInfo.items():
			if groupId=="teachers" and not self.isCurrentUserAdmin:
				continue
			
			tmp={
				"groupId":groupId,
				"isLocked":groupData.get("isLocked",False),
				"description":groupData.get(self.sessionLang,"default")
			}

			self.groupsConfigData.append(tmp)

	#def getGroupsConfig 

	def getUsersConfig(self):

		self.usersConfigData=[]

		for userId,userData in self.usersInfo.items():
			if not userId:
				continue

			isProtected=self._checkIfUserIsTeacher(userId) or self._checkIfUserIsAdmin(userId)

			if isProtected and not self.isCurrentUserAdmin:
				self.enableUserConfig=False
				continue

			tmp={
				"userId":userId,
				"isLocked":userData.get("isLocked",False)
			}
			
			self.usersConfigData.append(tmp)

	#def getUsersConfig 			
			
	def applyGroupChanges(self, groupAccessControl, groupsInfo):

		isControlChanged = groupAccessControl != self.isGroupAccessControlEnabled
		enableControl = isControlChanged and groupAccessControl
		disableControl = isControlChanged and not groupAccessControl
		updateGroupInfo = groupsInfo != self.groupsInfo

		if groupAccessControl and not self.thereAreGroupsLocked(groupsInfo):
			return {
				"status": False,
				"code": N4dManager.APPLY_CHANGES_WITHOUT_GROUP,
				"type": N4dManager.KIRIGAMI_MSG_ERROR
			}

		self.writeLog("Changes in configuration of access control by Group:")		
		
		try:
			if enableControl:
				self.writeLog("- Action: enable access control by group")
				self.client.AccessControlManager.set_groups_info(groupsInfo)		
				self.writeLog("- Enable access control by group: Changes apply successful")
			
			elif updateGroupInfo:
				self.writeLog("- Action: change group list")
				self.client.AccessControlManager.set_groups_info(groupsInfo)		
				self.writeLog("- New groups with locked access: Changes apply successful")
				
			if disableControl:
				self.writeLog("- Action: disable access control by group")
				self.client.AccessControlManager.disable_access_denied_group()
				self.writeLog("- Disable access control by group: Change apply successful")
				
			self.loadGroupConfig("End")
			return {
				"status": True,
				"code": N4dManager.APPLY_CHANGES_SUCCESSFUL,
				"type": N4dManager.KIRIGAMI_MSG_OK
			}
			
		except n4d.client.CallFailedError as e:
			self.writeLog(f"- Error applying changes: {e.code}")
			return {
				"status": False,
				"code": e.code,
				"type": N4dManager.KIRIGAMI_MSG_ERROR
			}
	
	#def applyGroupChanges

	def applyUsersChanges(self,userAccessControl,usersInfo):

		isControlChanged = userAccessControl != self.isUserAccessControlEnabled
		enableControl = isControlChanged and userAccessControl
		disableControl = isControlChanged and not userAccessControl
		updateUsersInfo=usersInfo!=self.usersInfo

		if userAccessControl and not self.thereAreUsersLocked(usersInfo):
			return {
				"status":False,
				"code":N4dManager.APPLY_CHANGES_WITHOUT_USER,
				"type":N4dManager.KIRIGAMI_MSG_ERROR
			}
	
		self.writeLog("Changes in configuration of access control by User:")		

		try:
			if enableControl:
				self.writeLog("- Action: enable access control by user")
				self.client.AccessControlManager.set_users_info(usersInfo)
				self.writeLog("- Enable access control by user: Change apply successful")
			else:
				if updateUsersInfo:
						self.writeLog("- Action: change user list")
						self.client.AccessControlManager.set_users_info(usersInfo)
						self.writeLog("- New users with locked access: Changes apply successful")
			
				if disableControl:
					self.writeLog("- Action: disable access control by user")
					self.client.AccessControlManager.disable_access_denied_user()
					self.writeLog("- Disable access control by user: Change apply successful")

			self.loadUserConfig("End")
			return {
				"status":True,
				"code":N4dManager.APPLY_CHANGES_SUCCESSFUL,
				"type":N4dManager.KIRIGAMI_MSG_OK
			}

		except n4d.client.CallFailedError as e:
			self.writeLog(f"- Error applying changes: {e.code}")
			return {
				"status":False,
				"code":e.code,
				"type":N4dManager.KIRIGAMI_MSG_OK
			}

	#def applyUsersChanges

	def thereAreGroupsLocked(self,groupsInfo):

		return any(groupsInfo[item]["isLocked"] for item in groupsInfo)

	#def thereAreGroupsLocked
	
	def thereAreUsersLocked(self,usersInfo):

		return any(usersInfo[item]["isLocked"] for item in usersInfo)

	#def thereAreUsersLocked
	
	def checkIfUserIsValidGroup(self,userList):

		localAdminList = []
		teachersList = []

		adminGroupsSet = set(self.adminGroups)

		for item in userList:
			if item == self.currentUser:
				continue

			userGroups = self._getUserGroups(item)
			if any(group in adminGroupsSet for group in userGroups):
				localAdminList.append(item)

			if not self.isCurrentUserAdmin and self._checkIfUserIsTeacher(item):
				teachersList.append(item)

		isLocalAdmin = bool(localAdminList)

		return {
			"isLocalAdmin":isLocalAdmin, 
			"localAdminList":localAdminList, 
			"teachersList":teachersList
		}

	#def checkIfUserIsValidGroup

	def checkIfUserIsCurrrentUser(self,userList):

		rawList = [user for user in userList if user in [self.currentUser, 'root']]

		currentUserList = list(dict.fromkeys(rawList))
		return {
			"isCurrentUser":len(currentUserList) > 0, 
			"userList":currentUserList
		}

	#def checkIfUserIsCurrrentUser 
	
	def _checkIfUserIsTeacher(self,user):
		
		return 'teachers' in self._getUserGroups(user)
		
	#def checkIfUserIsTeacher
	
	def _checkIfUserIsAdmin(self,user):

		userGroups = self._getUserGroups(user)
		return any(item in self.adminGroups for item in userGroups)
		
	#def _checkIfUserIsAdmin

	def applyCDCChanges(self, cdcAccessControl, cdcInfo):

		if not self.isCorrectCode(cdcInfo.get("code", "")):
			return {
				"status":False, 
				"code":N4dManager.CDC_CODE_NOT_VALID,
				"type":N4dManager.KIRIGAMI_MSG_ERROR
			}

		if cdcAccessControl and cdcInfo.get("code") == "":
			return {
				"status":False, 
				"code":N4dManager.APPLY_CHANGES_WITHOUT_CODE,
				"type":N4dManager.KIRIGAMI_MSG_ERROR
			}

		currentCode = self.cdcInfo.get("code", "")
		newCode = cdcInfo.get("code", "")

		updateCDCInfo = (newCode != currentCode) and (newCode != "")

		if not cdcAccessControl and newCode == "":
			updateCDCInfo = True
			cdcInfo = {"code": ""} 

		isCcontrolChanged = cdcAccessControl != self.isCDCAccessControlEnabled
		enableControl = isCcontrolChanged and cdcAccessControl
		disableControl = isCcontrolChanged and not cdcAccessControl

		self.writeLog("Changes in configuration of access control by CDC:")

		try:
			if updateCDCInfo or enableControl:
				if updateCDCInfo:
					self.writeLog("- Action: change center code")
				if enableControl:
					self.writeLog("- Action: enable access control by CDC")
					
				self.client.AccessControlManager.set_cdc_info(cdcInfo)
				
				if updateCDCInfo:
					self.writeLog("- New center code: Changes apply successful")
				if enableControl:
					self.writeLog("- Enable access control by CDC: Changes apply successful")
					
			if disableControl:
				self.writeLog("- Action: disable access control by CDC")
				self.client.AccessControlManager.disable_access_denied_cdc(True)
				self.writeLog("- Disable access control by CDC: Changes apply successful")
				
			self.loadCDCConfig("End")
			
			return {
				"status":True, 
				"code":N4dManager.APPLY_CHANGES_SUCCESSFUL,
				"type":N4dManager.KIRIGAMI_MSG_OK
			}
			
		except n4d.client.CallFailedError as e:
			self.writeLog(f"- Error applying changes: {e.code}")
			return {
				"status":False, 
				"code":e.code,
				"type":N4dManager.KIRIGAMI_MSG_ERROR
			}

	#def applyCDCChanges

	def isCorrectCode(self,cdcCode):

		return not cdcCode or (len(cdcCode) == 8 and cdcCode.isdecimal() and cdcCode[:2] in ['03', '12', '46'])

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
	
	def writeLog(self,msg):

		syslog.openlog("ACCESS-CONTROL")
		syslog.syslog(msg)

	#def writeLog

#class N4dManager
