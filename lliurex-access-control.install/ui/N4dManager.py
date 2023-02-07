#!/usr/bin/python3

import xmlrpc.client
import ssl
import os
import subprocess
import shutil
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
		self.adminGroups=["sudo","admins","adm"]
		self.enableUserConfig=True

		self.clearCache()
		self.getSessionLang()

	#def __init__

	def clearCache(self):

		clear=False
		user=os.environ["USER"]
		versionFile="/home/%s/.config/lliurex-access-control.conf"%user
		cachePath="/home/%s/.cache/lliurex-access-control-gui.py"%user
		installedVersion=self.getPackageVersion()

		if not os.path.exists(versionFile):
			with open(versionFile,'w') as fd:
				fd.write(installedVersion)
				fd.close()

			clear=True

		else:
			with open(versionFile,'r') as fd:
				fileVersion=fd.readline()
				fd.close()

			if fileVersion!=installedVersion:
				with open(versionFile,'w') as fd:
					fd.write(installedVersion)
					fd.close()
				clear=True
		
		if clear:
			if os.path.exists(cachePath):
				shutil.rmtree(cachePath)

	#def clearCache

	def getPackageVersion(self):

		command = "LANG=C LANGUAGE=en apt-cache policy lliurex-access-control"
		p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE)
		installed = None
		for line in iter(p.stdout.readline,b""):
			if type(line) is bytes:
				line=line.decode()

			stripedline = line.strip()
			if stripedline.startswith("Installed"):
				installed = stripedline.replace("Installed: ","")

		return installed

	#def getPackageVersion

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
			self.isCurrentUserAdmin=self._checkIfUserIsAdmin(user)
			self.validation=(user,password)
			self.currentUser=user
			self.writeLog("Init session in lliurex-access-control GUI")
			self.writeLog("User login in GUI: %s"%self.currentUser)

		return userValidated

	#def validateUser

	def loadConfig(self):
		
		self.loadGroupConfig()
		self.loadUserConfig()
		self.loadCDCConfig()
	
	#def loadConfig

	def loadGroupConfig(self,step="Initial"):

		self.writeLog("Access Control by Group. %s configuration:"%step)
		self.isAccessDenyGroupEnabled=self.client.isAccessDenyGroupEnabled(self.validation,"AccessControlManager")['status']
		self.writeLog("- Access control by group activated: %s"%(str(self.isAccessDenyGroupEnabled)))
		if step=="Initial":
			initLoad=True
		else:
			initLoad=False
		self.groupsInfo=self.client.getGroupsInfo(self.validation,"AccessControlManager",initLoad)['data']
		self.writeLog("- Groups with restricted access: ")
		for item in self.groupsInfo:
			self.writeLog("  - %s: locked access %s"%(item,str(self.groupsInfo[item]["isLocked"])))
		self.getGroupsConfig()
		
	#def loadGroupConfig()

	def loadUserConfig(self,step="Initial"):
		
		self.writeLog("Access Control by User. %s configuration:"%step)
		self.isAccessDenyUserEnabled=self.client.isAccessDenyUserEnabled(self.validation,"AccessControlManager")['status']
		self.writeLog("- Access Control by User activated: %s"%(str(self.isAccessDenyUserEnabled)))
		self.usersInfo=self.client.getUsersInfo(self.validation,"AccessControlManager")["data"]
		if len(self.usersInfo)>0:
			for item in self.usersInfo:
				self.writeLog("  - %s: locked access %s"%(item,str(self.usersInfo[item]["isLocked"])))
		else:
			self.writeLog("  - There is no user list")

		self.getUsersConfig()

	#def loadUserConfig

	def loadCDCConfig(self,step="Initial"):

		self.writeLog("Access Control by CDC. %s configuration:"%step)
		self.isCDCAccessControlAllowed=self.client.isCDCAccessControlAllowed(self.validation,"AccessControlManager")["status"]
		self.writeLog("- Access Control by CDC allowed: %s"%(str(self.isCDCAccessControlAllowed)))
		self.isAccessDenyCDCEnabled=self.client.isAccessDenyCDCEnabled(self.validation,"AccessControlManager")["status"]
		self.writeLog("- Access Control by CDC enabled: %s"%(str(self.isAccessDenyCDCEnabled)))
		self.cdcInfo=self.client.getCDCInfo(self.validation,"AccessControlManager")["data"]
		if self.cdcInfo["code"]!="":
			currentCode=self.cdcInfo["code"]
		else:
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
			if item=="teachers":
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
			self.writeLog("- Action: change group list")
			ret=self.client.setGroupsInfo(self.validation,"AccessControlManager",groupsInfo)		
			if ret['status']:
				self.writeLog("- New groups with locked access: Changes apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
				if disableControl:
					self.writeLog("- Action: disable access control by group")
					ret=self.client.disableAccessDenyGroup(self.validation,"AccessControlManager")
					if ret['status']:
						self.writeLog("- Disable access control by group: Change apply successful")
						result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
					else:
						self.writeLog("- Error applying changes: %s"%ret['msg'])
						result=[False,ret['msg']]
			else:
				self.writeLog("- Error applying changes: %s"%ret['msg'])
				result=[False,ret['msg']]


		if disableControl and not updateGroupInfo:
			self.writeLog("- Action: disable access control by group")
			ret=self.client.disableAccessDenyGroup(self.validation,"AccessControlManager")
			if ret['status']:
				self.writeLog("- Disable access control by group: Change apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			else:
				self.writeLog("- Error applying changes: %s"%ret['msg'])
				result=[False,ret['msg']]

		
		if enableControl:
			self.writeLog("- Action: enable access control by group")
			ret=self.client.setGroupsInfo(self.validation,"AccessControlManager",groupsInfo)		
			if ret['status']:
				self.writeLog("- Enable access control by group: Changes apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			else:
				self.writeLog("- Error applying changes: %s"%ret['msg'])
				result=[False,ret['msg']]

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
			self.writeLog("- Action: change user list")
			ret=self.client.setUsersInfo(self.validation,"AccessControlManager",usersInfo)
			if ret['status']:
				self.writeLog("- New users with locked access: Changes apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
				if disableControl:
					self.writeLog("- Action: disable access control by user")
					ret=self.client.disableAccessDenyUser(self.validation,"AccessControlManager")
					if ret['status']:
						self.writeLog("- Disable access control by user: Change apply successful")
						result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
					else:
						self.writeLog("- Error applying changes: %s"%ret['msg'])
						result=[False,ret['msg']]
			else:
				self.writeLog("- Error applying changes: %s"%ret['msg'])
				result=[False,ret['msg']]

		if disableControl and not updateUsersInfo:
			self.writeLog("- Action: disable access control by user")
			ret=self.client.disableAccessDenyUser(self.validation,"AccessControlManager")		
			if ret['status']:
				self.writeLog("- Disable access control by user: Change apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			else:
				self.writeLog("- Error applying changes: %s"%ret['msg'])
				result=[False,ret['msg']]

		if enableControl:
			self.writeLog("- Action: enable access control by user")
			ret=self.client.setUsersInfo(self.validation,"AccessControlManager",usersInfo)
			if ret['status']:
				self.writeLog("- Enable access control by user: Change apply successful")
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			else:
				self.writeLog("- Error applying changes: %s"%ret['msg'])
				result=[False,ret['msg']]

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
				self.writeLog("- Action: change center code")
				ret=self.client.setCDCInfo(self.validation,"AccessControlManager",cdcInfo)		
				if ret["status"]:
					self.writeLog("- New center code: Changes apply successful")
					result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
					if disableControl:
						self.writeLog("- Action: disable access control by CDC")
						ret=self.client.disableAccessDenyCDC(self.validation,"AccessControlManager")
						if ret["status"]:
							self.writeLog("- Disable access control by CDC: Change apply successful")
							result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
						else:
							self.writeLog("- Error applying changes: %s"%ret["msg"])
							result=[False,ret["msg"]]
					
				else:
					self.writeLog("- Error applying changes: %s"%ret["msg"])
					result=[False,ret["msg"]]

			if disableControl and not updateCDCInfo:
				self.writeLog("- Action: disable access control by CDC")
				ret=self.client.disableAccessDenyCDC(self.validation,"AccessControlManager",True)
				if ret["status"]:
					self.writeLog("- Disable access control by CDC: Changes apply successful")
					result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
				else:
					self.writeLog("- Error applying changes: %s"%ret["msg"])
					result=[False,ret["msg"]]

			if enableControl:
				self.writeLog("- Action: enable access control by CDC")
				ret=self.client.setCDCInfo(self.validation,"AccessControlManager",cdcInfo)		
				if ret["status"]:
					self.writeLog("- Enable access control by CDC: Changes apply successful")
					result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
				else:
					self.writeLog("- Error applying changes: %s"%ret["msg"])
					result=[False,ret["msg"]]

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

	def checkFlavour(self):

		cmd='lliurex-version -v'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]
		lockFlavour=False

		if type(result) is bytes:
			result=result.decode()
		flavours = [ x.strip() for x in result.split(',') ]	
		
		
		for item in flavours:
			if 'server' in item or 'client' in item:
				lockFlavour=True
				break
							
		return lockFlavour

	#def checkFlavour

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
