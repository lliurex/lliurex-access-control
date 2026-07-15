#!/usr/bin/env python3

import os
import subprocess
import n4d.client
import sys
import syslog
import pwd
import grp
import getpass
import signal
signal.signal(signal.SIGINT,signal.SIG_IGN)

class AccessControlCliManager(object):

	def __init__(self,mode,skipAdmin):
		
		self.groupsInfo={}
		self.isGroupAccessControlEnabled=False
		self.usersInfo={}
		self.isUserAccessControlEnabled=False
		self.usersFilter=['root']
		self.currentUser=""
		self.unattendedMode=mode
		self.skipAdmin=skipAdmin
		self.groupsUnLockedCount=0
		self.usersUnLockedCount=0
		self.cdcInfo={}
		self.cdcCode=""
		self.isCDCAccessControlAllowed=False
		self.isCDCAccessControlEnabled=False
		self.n4dClient=n4d.client.Client()
		self._getCurrentUser()
		self._getInfo()

	#def __init__


	def createClient(self):

		if self.currentUser!="":
			password=getpass.getpass('   [Access-Control]: Enter your password:')
			client=n4d.client.Client("https://localhost:9779",self.currentUser,password)
			
			try:
				ticket=client.get_ticket()
				self.n4dClient=n4d.client.Client(ticket=ticket)
			except Exception as e:
				msg="Authentication failed. Unable to execute action"
				self._writeLog(msg)
				print(f"   [Access-Control]: {msg}")
				sys.exit(1)
		else:
			masterKey=n4d.client.Key.master_key()
			
			if masterKey.valid():
				self.n4dClient=n4d.client.Client(key=masterKey)
			else:
				print('   [Access-Control]: You need root privilege to run this tool')

	#def createClient

	def showCurrentConfig(self,optionInfo):

		self._writeLog(f"- Action: get information about {optionInfo}")
		self.createClient()

		if optionInfo=="all" or optionInfo=="groups":
			print('   [Access-Control]: Current access control by group configuration')
			print(f'      - Access control by group activated: {self.isGroupAccessControlEnabled}')
			print(f'      - Groups with restriced access:')
			for group,groupData in self.groupsInfo.items():
				print(f'         - {group}: locked access {groupData.get("isLocked")}')
		
		if optionInfo=="all" or optionInfo=="users":
			print('   [Access-Control]: Current access control by user configuration')
			print(f'      - Access control by user activated: {self.isUserAccessControlEnabled}')
			print('      - Users with restriced access:')
			if len(self.usersInfo)>0:
				for user,userData in self.usersInfo.items():
					print(f'         - {user}: locked access {userData.get("isLocked")}')
			else:
				print('         - There is no user in users list')
		
		return 0
	
	#def showCurrentConfig

	def lockGroup(self,groupsSelected):

		return self._changeGroupStatus(groupsSelected,'lock')
	
	#def lockGroup

	def unlockGroup(self,groupsSelected):

		return self._changeGroupStatus(groupsSelected,'unlock')

	#def unlockGroup

	def disableControlGroup(self):

		if not self.isGroupAccessControlEnabled:
			print('   [Access-Control]: Access control by groups already disable. Nothing to do')
			return 0

		if not self.unattendedMode:
			response=input('   [Access-Control]: Do you want to disable group access control? (yes/no)): ').lower()
		else:
			response='yes'

		if not response.startswith('y'):
			print('   [Access-Control]: Action canceled')
			return 0

		try:
			self._writeLog("Changes in configuration of access control by Group:")		
			self._writeLog("- Action: disable access control by group")
			self.createClient()
			ret=self.n4dClient.AccessControlManager.disable_access_denied_group()
			self._writeLog("- Disable access control by group: Change apply successful")
			print('   [Access-Control]: Action completed successfull')
			self._getGroupInfo("End")
			return 0
		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}")
			print('   [Access-Control]: Error. Unable to disable group access control')
			return 1			

	#def disableControlGroup

	def enableControlGroup(self):

		if self.isGroupAccessControlEnabled:
			print('   [Access-Control]: Access control by groups already enable. Nothing to do ')
			return 0
		
		if not self._checkIfExistsLock("groups"):
			print('   [Access-Control]: There is no group with locked access. Is not possible to activate access control by group')
			return 0

		if not self.unattendedMode:
			response=input('   [Access-Control]: Do you want to enable group access control? (yes/no)): ').lower()
		else:
			response='yes'

		if not response.startswith('y'):
			print('   [Access-Control]: Action canceled')
			return 0

		try:
			self._writeLog("Changes in configuration of access control by Group:")		
			self._writeLog("- Action: enable access control by group")
			self.createClient()
			ret=self.n4dClient.AccessControlManager.set_groups_info(self.groupsInfo)
			self._writeLog("- Enable access control by group: Change apply successful")
			print('   [Access-Control]: Action completed successfull')
			self._getGroupInfo("End")
			return 0
		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}")
			print('   [Access-Control]: Error. Unable to activate group access control')
			return 1
									
	#def enableControlGroup

	def lockUser(self,usersSelected):
		
		return self._changeUserStatus(usersSelected,'lock')

	#def lockUsers 

	def unlockUser(self,usersSelected):
		
		return self._changeUserStatus(usersSelected,'unlock')

	#def unlockUsers  
 
	def disableControlUser(self):

		if not self.isUserAccessControlEnabled:
			print('   [Access-Control]: Access control by users already disable. Nothing to do')
			return 0

		if not self.unattendedMode:
			response=input('   [Access-Control]: Do you want to disable user access control? (yes/no)): ').lower()
		else:
			response='yes'

		if not response.startswith('y'):
			print('   [Access-Control]: Action canceled')
			return 0

		try:
			self._writeLog("Changes in configuration of access control by User:")		
			self._writeLog("- Action: disable access control by user")
			self.createClient()
			ret=self.n4dClient.AccessControlManager.disable_access_denied_user()
			self._writeLog("- Disable access control by user: Change apply successful")
			print('   [Access-Control]: Action completed successfull')
			self._getUserInfo("End")
			return 0
		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}")
			print('   [Acess-Control]: Error. Unable to disable user access control')
			return 1			

	#def disableControlUser

	def enableControlUser(self):

		if self.isUserAccessControlEnabled:
			print('   [Access-Control]: Access control by users already enable. Nothing to do ')
			return 0

		if not self._checkIfExistsLock("users"):
			print('   [Access-Control]: There is no users with locked access. Is not possible to activate access control by user')
			return 0

		if not self.unattendedMode:
			response=input('   [Access-Control]: Do you want to enable user access control? (yes/no)): ').lower()
		else:
			response='yes'

		if not response.startswith('y'):
			print('   [Access-Control]: Action canceled')
			return 0

		try:
			self._writeLog("Changes in configuration of access control by User:")		
			self._writeLog("- Action: enable access control by user")
			self.createClient()
			ret=self.n4dClient.AccessControlManager.set_users_info(self.usersInfo)
			self._writeLog("- Enable access control by user: Change apply successful")
			print('   [Access-Control]: Action completed successfull')
			self._getUserInfo("End")
			return 0
		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}")
			print('   [Access-Control]: Error. Unable to activate user access control')

	#def enableControlUser

	def removeUserFromList(self,usersSelected):

		correctUsers=self._checkCorrectUsers(usersSelected)

		if not correctUsers:
			print('   [Access-Control]: The users indicates to remove from users list are not correct. See currentconfig users to get correct users')	
			return 1

		if (len(usersSelected)==len(self.usersInfo)) and self.isUserAccessControlEnabled:
			print('   [Access-Control]: This action will be disable access control by user')
		else:
			if (len(usersSelected)<len(self.usersInfo)) and not self.isUserAccessControlEnabled:
				print('   [Access-Control]: This action will be enable access control by user')

		if not self.unattendedMode:
			response=input('   [Access-Control]: Do you want to delete indicated users from users list? (yes/no)): ').lower()
		else:
			response='yes'

		if not response.startswith('y'):
			print('   [Access-Control]: Action canceled')
			return 0

		try:
			self._writeLog("Changes in configuration of access control by User:")		
			self._writeLog("- Action: remove user from list")
			self.createClient()
			ret=self._applyUserChanges(usersSelected,"remove")
			self._writeLog("- New users with locked access: Changes apply successful")
			print('   [Access-Control]: Action completed successfull')
			self._getUserInfo("End")
			return 0
		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}")
			print('   [Access-Control]: Unable to delete indicated useres from users list')
			return 1

	#def removeUser

	def removeUserList(self):

		if not len(self.usersInfo)>0:
			print('   [Access-Control]: User llist not exist. Nothing to do')
			return 0			

		if self.isUserAccessControlEnabled:
			print('   [Access-Control]: This action will be disable access control by user')
		
		if not self.unattendedMode:
			response=input('   [Access-Control]: Do you want to delete users list? (yes/no)): ').lower()
		else:
			response='yes'

		if not response.startswith('y'):
			print('   [Access-Control]: Action canceled')
			return 0

		try:
			self._writeLog("Action: Removed user list")
			self.createClient()				
			self.usersInfo={}
			ret=self.n4dClient.AccessControlManager.set_users_info(self.usersInfo)
			print('   [Access-Control]: Action completed successfull')
			self._getUserInfo("End")
			return 0
		except n4d.client.CallFailedError as e:
			self._writeLog(f"Error removing user list: {e.code}")
			print('   [Access-Control]: Unable to delete users list')
			return 1

	#def removeUserList

	def setCenter(self,cdcCode):

		return self._changeCDCCode('set',cdcCode)
	
	#def setCenter

	def removeCenter(self):

		return self._changeCDCCode('remove')
	
	#def removeCenter

	def disableControlCenter(self):

		if not self.isCDCAccessControlAllowed:
			print('      - Access control by center is currently not allowed')
			return 0

		if not self.isCDCAccessControlEnabled:
			print('   [Access-Control]: Access control by center already disable. Nothing to do')
			return 0

		if not self.unattendedMode:
			response=input('   [Access-Control]: Do you want to disable center access control? (yes/no)): ').lower()
		else:
			response='yes'

		if not response.startswith('y'):
			print('   [Access-Control]: Action canceled')
			return 0

		try:
			self._writeLog("Changes in configuration of access control by CDC:")		
			self._writeLog("- Action: disable access control by CDC")
			self.createClient()
			ret=self.n4dClient.AccessControlManager.disable_access_denied_cdc(True)
			self._writeLog("- Disable access control by CDC: Change apply successful")
			print('   [Access-Control]: Action completed successfull')
			self._getCDCInfo("End")
			return 0
		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}")
			print('   [Acess-Control]: Error. Unable to disable CDC access control')
			return 1			

	#def disableControlCenter

	def enableControlCenter(self):

		if not self.isCDCAccessControlAllowed:
			print('      - Access control by center is currently not allowed')
			return 1

		if self.isCDCAccessControlEnabled:
			print('   [Access-Control]: Access control by center already enable. Nothing to do ')
			return 0


		if not self.cdcCode:
			print('   [Access-Control]: There is no center code in previous configuration. Is not possible to activate access control by center')
			return 0

		if not self.unattendedMode:
			response=input('   [Access-Control]: Do you want to enable center access control? (yes/no)): ').lower()
		else:
			response='yes'

		if not response.startswith('y'):
			print('   [Access-Control]: Action canceled')
			return 0

		try:
			self._writeLog("Changes in configuration of access control by CDC:")		
			self._writeLog("- Action: enable access control by CDC")
			self.createClient()
			self.cdcInfo["accessControlEnabled"]=True
			ret=self.n4dClient.AccessControlManager.set_cdc_info(self.cdcInfo)
			self._writeLog("- Enable access control by CDC: Change apply successful")
			print('   [Access-Control]: Action completed successfull')
			self._getCDCInfo("End")
			return 0
		except n4d.client.CallFailedError as e:
			self._writeLog("- Error applying changes: %s"%e.code)
			print('   [Access-Control]: Error. Unable to activate center access control')
			return 1
	
	#def enableControlCenter

	def _getInfo(self):

		self._getGroupInfo()
		self._getUserInfo()
		self._getCDCInfo()

	#def _getInfo

	def _getGroupInfo(self,step="Initial"):

		self._writeLog(f"Access Control by Group.{step} configuration:")
		self.isGroupAccessControlEnabled=self.n4dClient.AccessControlManager.is_access_denied_group_enabled()
		self._writeLog(f"- Access control by group activated: {self.isGroupAccessControlEnabled}")
		if step=="Initial":
			initLoad=True 
		else:
			initLoad=False
		self.groupsInfo=self.n4dClient.AccessControlManager.get_groups_info(initLoad)
		self._writeLog("- Groups with restricted access: ")
		for group,groupData in self.groupsInfo.items():
			self._writeLog(f"  - {group}: locked access {groupData.get("isLocked")}")

	#def _getGroupInfo

	def _getUserInfo(self,step="Initial"):

		self._writeLog(f"Access Control by User. {step} configuration:")
		self.isUserAccessControlEnabled=self.n4dClient.AccessControlManager.is_access_denied_user_enabled()
		self._writeLog(f"- Access Control by User activated: {self.isUserAccessControlEnabled}")
		self.usersInfo=self.n4dClient.AccessControlManager.get_users_info()
		self._writeLog("- Users with restricted access: ")
		if len(self.usersInfo)>0:
			for user,userData in self.usersInfo.items():
				self._writeLog(f"  - {user}: locked access {userData.get("isLocked")}")
		else:
			self._writeLog("  - There is no user list")
	
	#def _getUserInfo

	def _getCDCInfo(self,step="Initial"):

		self._writeLog(f"Access Control by Center. {step} configuration:")
		self.isCDCAccessControlAllowed=self.n4dClient.AccessControlManager.is_cdc_access_control_allowed()
		self._writeLog(f"- Access Control by CDC allowed: {self.isCDCAccessControlAllowed}")
		self.isCDCAccessControlEnabled=self.n4dClient.AccessControlManager.is_access_denied_cdc_enabled()
		self._writeLog(f"- Access Control by CDC enabled: {self.isCDCAccessControlEnabled}")
		self.cdcInfo=self.n4dClient.AccessControlManager.get_cdc_info()
		if self.cdcInfo["code"]:
			self.cdcCode=self.cdcInfo.grt("code")
			currentCode=self.cdcCode
		else:
			currentCode=None
		self._writeLog(f"- Center code to control access: {currentCode}")

	#def _getCDCInfo

	def _changeGroupStatus(self,groupsSelected,action):

		correctGroups=self._checkCorrectGroups(groupsSelected)

		if not correctGroups:
			print('   [Access-Control]: The groups indicates to %s their acces are not correct. See currentconfig groups to get correct groups'%action)
			return 1

		currentStatusChanged=self._checkCurrentConfiguration('groups',groupsSelected,action)
		
		if not currentStatusChanged:
			print('   [Access-Control]: The indicated groups are already %sed. Nothing to do'%action)
			return 0

		if action=="lock" and not self.isGroupAccessControlEnabled:
			print('   [Access-Control]: This action will be activate access control by group')
		elif action=="unlock" and (self.groupsUnLockedCount<len(self.groupsInfo)) and not self.isGroupAccessControlEnabled:
			print('   [Access-Control]: This action will be activate access control by group')
		elif action=="unlock" and (self.groupsUnLockedCount==len(self.groupsInfo)) and self.isGroupAccessControlEnabled:
			print('   [Access-Control]: This action will be disable access control by group')

		if not self.unattendedMode:
			response=input('   [Access-Control]: Do you want to %s access to the indicated groups? (yes/no)): '%action).lower()
		else:
			response='yes'	

		if not response.startswith('y'):
			print('   [Access-Control]: Action canceled')
			return 0

		try:
			self._writeLog("Changes in configuration of access control by Group:")		
			self._writeLog(f"- Action: change group list {action}")
			self.createClient()
			ret=self._applyGroupChanges(groupsSelected,action)
			self._writeLog("- New groups with locked access: Changes apply successful")
			print('   [Access-Control]: Action completed successfull')
			self._getGroupInfo("End")
			return 0
		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}")
			print(f'   [Access-Control]: Unable to {action} access to the indicated groups')
			return 1			
	
	#def _changeGroupStatus
	
	def _checkCorrectGroups(self,groupsSelected):

		for item in groupsSelected:
			if item not in self.groupsInfo.keys():
				return False

		return True

	#def _checkCorrectGroups

	def _changeUserStatus(self,usersSelected,action):

		correctUsers=self._checkCorrectUsers(usersSelected)
		adminUsers=""

		if not correctUsers:
			if action=="unlock":
				print('   [Access-Control]: The users indicates to %s their acces are not correct. See currentconfig users to get correct users'%action)
				return 1
			
			ret=self._checkIfUserIsCurrentUser(usersSelected)
			if ret.get("currentUser"):
				usersSelected=[u for u in usersSelected if u not in ret.get("usersList")]
	
				if len(usersSelected)==0 and action=="lock":
					print('   [Access-Control]: It is not possible to lock the user with which you are configuring the access control')
					return 0

			adminInUsers=self._checkIfUserIsLocalAdmin(usersSelected)
			if adminInUsers.get("localAdmin"):
				if action=="lock":
					adminUsers=", ".join(adminInUsers.get("adminList"))
					if not self.unattendedMode:
						response=input(f'   [Access-Control]: The user(s) {adminUsers} are local computer administrator. Do you want to add them to the list? (yes/no)): ').lower()
					else:
						response='no' if self.skipAdmin else 'yes'

					if not response.startswith('y'):
						usersSelected=[u for u in usersSelected if u not in adminInUsers.get("adminList")]
						if len(usersSelected)==0:
							if ret.get("currentUser"):
								print('   [Access-Control]: It is not possible to lock the user with which you are configuring the access control')
							print('   [Access-Control]: Action canceled')
							return 0

		if action=="lock":
			if not correctUsers and ret.get("currentUser"):
				print('   [Access-Control]: The user with which you are configuring the access control will not be locked')
			
			print('   [Access-Control]: The indicated users that are not in the list will be added')
			if adminUsers and response.startswith('y'):
				self._writeLog(f"Action: Added admin user to user list: {adminUsers}")	

		currentStatusChanged=self._checkCurrentConfiguration('users',usersSelected,action)
		
		if not currentStatusChanged:
			print('   [Access-Control]: The indicated users are already %sed. Nothing to do'%action)
			return 0

		if action=="lock" and not self.isUserAccessControlEnabled:
			print('   [Access-Control]: This action will be activate access control by user')
		elif action=="unlock" and (self.usersUnLockedCount<len(self.usersInfo)) and not self.isUserAccessControlEnabled:
			print('   [Access-Control]: This action will be activate access control by user')
		elif action=="unlock" and (self.usersUnLockedCount==len(self.usersInfo)) and self.isUserAccessControlEnabled:
			print('   [Access-Control]: This action will be disable access control by user')
				
		if not self.unattendedMode:
			response=input(f'   [Access-Control]: Do you want to {action} access to the indicated users? (yes/no)): ').lower()
		else:
			response='yes'	
				
		if not response.startswith('y'):
			print('   [Access-Control]: Action canceled')
			return 0

		try:
			self._writeLog("Changes in configuration of access control by User:")		
			self._writeLog(f"- Action: change user list {action}")
			self.createClient()
			ret=self._applyUserChanges(usersSelected,action)
			self._writeLog("- New users with locked access: Changes apply successful")
			print('   [Access-Control]: Action completed successfull')
			self._getUserInfo("End")
			return 0
		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}")
			print(f'   [Access-Control]: Unable to {action} access to the indicated users')
			return 1			

	#def _changeUsersStatus

	def _checkCorrectUsers(self,usersSelected):

		for item in usersSelected:
			if item not in self.usersInfo:
				return False
		
		return True

	#def _checkCorrectUsers

	def _changeCDCCode(self,action,cdcCode=""):

		if not self.isCDCAccessControlAllowed:
			print('      - Access control by center is currently not allowed')
			return 0

		correctCode=self._checkCorrectCode(action,cdcCode)

		if not correctCode:
			if action=="set":
				print(f'   [Access-Control]: The center code indicates to {action} is not correct.')
			else:
				print(f'   [Access-Control]: The center code indicates to {action} is not correct.See currentconfig center to get correct center code')
			
			return 1

		currentStatusChanged=self._checkCurrentCDCConfiguration(action,cdcCode)
		if not currentStatusChanged:
			if action=="set":
				print(f'   [Access-Control]: The indicated center code are already {action}ted. Nothing to do')
			else:
				print('   [Access-Control]: There is no center code configured. Nothing to do')
			return 0

		if action=="set" and not self.isCDCAccessControlEnabled:
			print('   [Access-Control]: This action will be activate access control by center')
		elif action=="set" and self.isCDCAccessControlEnabled:
			print('   [Access-Control]: This action will be update the currently center code')
		elif action=="remove" and self.isCDCAccessControlEnabled:
			print('   [Access-Control]: This action will be disable access control by center')
					
		if not self.unattendedMode:
			response=input('   [Access-Control]: Do you want to %s center code to control access by center? (yes/no)): '%action).lower()
		else:
			response='yes'	
					
		if not response.startswith('y'):
			print('   [Access-Control]: Action canceled')
			return 0
		
		try:
			self._writeLog("Changes in configuration of access control by Center:")		
			self._writeLog(f"- Action: change center code {action}")
			self.createClient()
			ret=self._applyCDCChanges(action,cdcCode)
			self._writeLog("- New center code: Changes apply successful")
			print('   [Access-Control]: Action completed successfull')
			self._getCDCInfo("End")
			return 0
		except n4d.client.CallFailedError as e:
			self._writeLog(f"- Error applying changes: {e.code}")
			print(f'   [Access-Control]: Unable to {action} center code')
			return 1			
	
	#def _changeCDCCode
	
	def _checkCorrectCode(self,action,cdcCode=""):

		if action!="set":
			return True

		if not cdcCode:
			return False
		
		if len(cdcCode)==8:
			if cdcCode.isdecimal():
				head=cdcCode[0:2]
				if head in ['03','12','46']:
					return True
		return False

	#def _checkCorrectCode

	def _checkCurrentConfiguration(self,option,newValues,action):

		match=0
		self.groupsUnLockedCount=0
		self.usersUnLockedCount=0

		newStatus=(action == "lock")

		infoDict=self.groupsInfo if option=="groups" else self.usersInfo

		for item in newValues:
			currentStatus=infoDict.get(item,{}).get("isLocked")

			if currentStatus is None:
				match+=1
			elif currentStatus!=newStatus:
				match+=1

		if not newStatus:
			unlockerCount=sum(1 for item in infoDict if infoDict[item].get("isLocked",False))
			
			if option=="groups":
				self.groupsUnLockedCount=unlockerCount
			elif option=="users":
				self.usersUnLockedCount=unlockerCount

		return match >0

	#def _checkCurrentConfiguration

	def _checkCurrentCDCConfiguration(self,action,newValue=""):

		if action=="set":
			if newValue!=self.cdcCode:
				return True
			return False
		elif action=="remove":
			if self.cdcCode!="":
				return True
			else:
				return False
	
	#def _checkCurrentCDCConfiguration
		
	def _applyGroupChanges(self,groupsSelected,action):

		isLocked=(action == "lock")
		for item in self.groupsInfo:
			if item in groupsSelected:
				self.groupsInfo[item]["isLocked"]=isLocked

		return self.n4dClient.AccessControlManager.set_groups_info(self.groupsInfo)

	#def _applyGroupChanges	

	def _applyUserChanges(self,usersSelected,action):

		if action=="remove":
			for item in usersSelected:
				if item in self.usersInfo:
					del self.usersInfo[item]
		else:
			isLocked=(action == "lock")
			for item in usersSelected:
				if item not in self.usersInfo:
					self.usersInfo[item]={"isLocked":isLocked}
				else:
					self.usersInfo[item]["isLocked"]=isLocked
	
		return self.n4dClient.AccessControlManager.set_users_info(self.usersInfo)

	#def _applyUserChanges	

	def _checkIfUserIsLocalAdmin(self,usersSelected):

		adminGroups=["sudo","admins","adm"]
		match=0
		adminUser=[]

		for item in usersSelected:
			if item not in self.usersInfo:
				try:
					gid = pwd.getpwnam(item).pw_gid
					groups_gid=os.getgrouplist(item,gid)
					user_groups=[grp.getgrgid(x).gr_name for x in groups_gid]
					for element in user_groups:
						if element in adminGroups:
							match+=1
							adminUser.append(item)
							break
				except:
					pass

		if match>0:
			return {"localAdmin":True,"adminList":adminUser}
		else:
			return {"localAdmin":False,"adminList":adminUser}
	
	#def _checkIfUserIsLocalAdmin

	def _applyCDCChanges(self,action,cdcCode=""):

		if action=="set":
			if not self.cdcInfo["accessControlEnabled"]:
				self.cdcInfo["accessControlEnabled"]=True
			self.cdcInfo["code"]=cdcCode
		elif action=="remove":
			self.cdcInfo={}

		return self.n4dClient.AccessControlManager.set_cdc_info(self.cdcInfo)

	#def _applyCDCChanges

	def _getCurrentUser(self):

		sudoUser=os.environ.get("SUDO_USER","")
		loginUser=""
		pkexecUser=""

		try:
			loginUser=os.getlogin()
		except:
			pass

		pkexec_uid=os.environ.get("PKEXEC_UID")
		if pkexec_uid:
			try:
				pkexecUser=subprocess.check_output(["id", "-un", pkexec_uid]).decode().strip()
			except:
				pass

		if pkexecUser and pkexecUser !="root":
			self.currentUser=pkexecUser

		elif sudoUser and sudoUser!="root":
			self.currentUser=sudoUser
			
		else:
			self.currentUser=loginUser

		if self.currentUser not in self.usersFilter:
			self.usersFilter.append(self.currentUser)

		self._writeLog("Init session in lliurex-access-control- CLI")
		if loginUser:
			self._writeLog(f"User login in CLI: {self.currentUser}")
		else:
			self._writeLog("User login in CLI: No current user detected. A script may have been executed at login")

		if self.unattendedMode:
			self.currentUser=""
			
		self._writeLog(f"Unattended Mode:{self.unattendedMode}")
		self._writeLog(f"Skip Admin: {self.skipAdmin}")

	#def _getCurrentUser


	def _checkIfUserIsCurrentUser(self,usersSelected):

		currentUserList=[]
		for item in usersSelected:
			if item in self.usersFilter:
				currentUserList.append(item)

		if len(currentUserList)>0:
				return {"currentUser":True,"usersList":currentUserList}
		else:
			return {"currentUser":False,"usersList":currentUserList}

	#def _checkIfUserIsCurrentUser

	def _checkIfExistsLock(self,option):

		if option=="groups":
			data=self.groupsInfo
		else:
			data=self.usersInfo

		for item in data:
			if data[item]["isLocked"]:
				return True

		return False

	#def _checkIfExistsLock	

	def _writeLog(self,msg):

		syslog.openlog("ACCESS-CONTROL")
		syslog.syslog(msg)

	#def _writeLog

#class AccessControlCliManager	



