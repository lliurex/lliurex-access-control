#!/usr/bin/env python3

import os
import xmlrpc.client
import ssl
import sys
import syslog
import pwd
import grp
import signal
signal.signal(signal.SIGINT,signal.SIG_IGN)

class AccessControlCliManager(object):

	def __init__(self,mode):
		
		self.groupsInfo={}
		self.isAccessDenyGroupEnabled=False
		self.usersInfo={}
		self.isAccessDenyUserEnabled=False
		self.usersFilter=['root']
		self.currentUser=""
		self.unattendedMode=mode
		self.createClient('localhost')

	#def __init__


	def createClient(self,server):

		self.credentials=self.getLocalCredential()

		if self.credentials!=None:
			context=ssl._create_unverified_context()	
			self.n4dClient=xmlrpc.client.ServerProxy("https://%s:9779"%server,allow_none=True,context=context)
			self._getCurrentUser()
			self._getInfo()
		else:
			print('   [Access-Control]: You need root privilege to run this tool')
			sys.exit(1)

	#def createClient

	def getLocalCredential(self):

		try:
			with open('/etc/n4d/key','r') as fd:
				key=fd.readline().strip()
				return key
		except:
			return None

	#def getLocalCredential

	def showCurrentConfig(self,optionInfo):

		if optionInfo=="all" or optionInfo=="groups":
			print('   [Access-Control]: Current access control by group configuration')
			print('      - Access control by group activated: %s'%(str(self.isAccessDenyGroupEnabled)))
			print('      - Groups with restriced access:')
			for item in self.groupsInfo:
				print('         - %s: locked access %s'%(item,str(self.groupsInfo[item]["isLocked"])))
		
		if optionInfo=="all" or optionInfo=="users":
			print('   [Access-Control]: Current access control by user configuration')
			print('      - Access control by user activated: %s'%(str(self.isAccessDenyUserEnabled)))
			print('      - Users with restriced access:')
			if len(self.usersInfo)>0:
				for item in self.usersInfo:
					print('         - %s: locked access %s'%(item,str(self.usersInfo[item]["isLocked"])))
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

		if self.isAccessDenyGroupEnabled:
			if not self.unattendedMode:
				response=input('   [Access-Control]: Do you want to disable group access control? (yes/no)): ').lower()
			else:
				response='yes'

			if response.startswith('y'):
				self.writeLog("Changes in configuration of access control by Group:")		
				self.writeLog("- Try to disable access control by group")
				ret=self.n4dClient.disableAccessDenyGroup(self.credentials,"AccessControlManager")
				if ret["status"]:
					self.writeLog("- Disable access control by group: Change apply successful")
					print('   [Access-Control]: Action completed successfull')
					self._getGroupInfo("End")
					return 0
				else:
					self.writeLog("- Error applying changes: %s"%e.code)
					print('   [Acess-Control]: Error. Unable to disable group access control')
					return 1			
			else:
				print('   [Access-Control]: Action canceled')
				return 0
		else:
			print('   [Access-Control]: Access control by groups already disable. Nothing to do')
			return 0

	#def disableControlGroup

	def enableControlGroup(self):

		if not self.isAccessDenyGroupEnabled:
			if self._checkIfExistsLock("groups"):
				if not self.unattendedMode:
					response=input('   [Access-Control]: Do you want to enable group access control? (yes/no)): ').lower()
				else:
					response='yes'

				if response.startswith('y'):
					self.writeLog("Changes in configuration of access control by Group:")		
					self.writeLog("- Try to enable access control by group")
					ret=self.n4dClient.setGroupsInfo(self.credentials,'AccessControlManager',self.groupsInfo)
					if ret['status']:
						self.writeLog("- Enable access control by group: Change apply successful")
						print('   [Access-Control]: Action completed successfull')
						self._getGroupInfo("End")
						return 0
					else:
						self.writeLog("- Error applying changes: %s"%ret['msg'])
						print('   [Acess-Control]: Error. Unable to activate group access control')
						return 1
				else:
					print('   [Access-Control]: Action canceled')
					return 0

			else:
				print('   [Acess-Control]: There is no group with locked access. Is not possible to activate access control by group')
				return 0
		else:
			print('   [Acess-Control]: Access control by groups already enable. Nothing to do ')
			return 0
									
	#def enableControlGroup



	def lockUser(self,usersSelected):
		
		return self._changeUserStatus(usersSelected,'lock')

	#def lockUsers 

	def unlockUser(self,usersSelected):
		
		return self._changeUserStatus(usersSelected,'unlock')

	#def unlockUsers  
 
	def disableControlUser(self):

		if self.isAccessDenyUserEnabled:
			if not self.unattendedMode:
				response=input('   [Access-Control]: Do you want to disable user access control? (yes/no)): ').lower()
			else:
				response='yes'

			if response.startswith('y'):
				self.writeLog("Changes in configuration of access control by User:")		
				self.writeLog("- Try to disable access control by user")
				ret=self.n4dClient.disableAccessDenyUser(self.credentials,"AccessControlManager")
				if ret["status"]:
					self.writeLog("- Disable access control by user: Change apply successful")
					print('   [Access-Control]: Action completed successfull')
					self._getUserInfo("End")
					return 0
				else:
					self.writeLog("- Error applying changes: %s"%ret['msg'])
					print('   [Acess-Control]: Error. Unable to disable user access control')
					return 1			
			else:
				print('   [Access-Control]: Action canceled')
				return 0
		else:
			print('   [Access-Control]: Access control by users already disable. Nothing to do')
			return 0

	#def disableControlUser

	def enableControlUser(self):

		if not self.isAccessDenyUserEnabled:
			if self._checkIfExistsLock("users"):
				if not self.unattendedMode:
					response=input('   [Access-Control]: Do you want to enable user access control? (yes/no)): ').lower()
				else:
					response='yes'

				if response.startswith('y'):
					self.writeLog("Changes in configuration of access control by User:")		
					self.writeLog("- Try to enable access control by user")
					ret=self.n4dClient.setUsersInfo(self.validation,'AccessControlManager',self.usersInfo)
					if ret['status']:
						self.writeLog("- Enable access control by user: Change apply successful")
						print('   [Access-Control]: Action completed successfull')
						self._getUserInfo("End")
						return 0
					else:
						self.writeLog("- Error applying changes: %s"%ret['msg'])
						print('   [Acess-Control]: Error. Unable to activate user access control')
						return 1
				else:
					print('   [Access-Control]: Action canceled')
					return 0

			else:
				print('   [Acess-Control]: There is no users with locked access. Is not possible to activate access control by user')
				return 0
		else:
			print('   [Acess-Control]: Access control by users already enable. Nothing to do ')
			return 0

	#def enableControlUser

	def removeUserFromList(self,usersSelected):

		correctUsers=self._checkCorrectUsers(usersSelected)

		if correctUsers:
			if not self.unattendedMode:
				response=input('   [Access-Control]: Do you want to delete indicated users from users list? (yes/no)): ').lower()
			else:
				response='yes'
		
			if response.startswith('y'):
				self.writeLog("Changes in configuration of access control by User:")		
				self.writeLog("- Try to change user list")
				ret=self._applyUserChanges(usersSelected,"remove")
				if ret['status']:
					self.writeLog("- New users with locked access: Changes apply successful")
					print('   [Access-Control]: Action completed successfull')
					self._getUserInfo("End")
					return 0
				else:
					self.writeLog("- Error applying changes: %s"%ret['msg'])
					print('   [Access-Control]: Unable to delete indicated useres from users list')
					return 1
			else:
				print('   [Access-Control]: Action canceled')
				return 0
		else:
			print('   [Access-Control]: The users indicates to remove from users list are not correct. See currentconfig users to get correct users')	
			return 1

	#def removeUser

	def removeUserList(self):

		if len(self.usersInfo)>0:
			if not self.unattendedMode:
				response=input('   [Access-Control]: Do you want to delete users list? (yes/no)): ').lower()
			else:
				response='yes'

			if response.startswith('y'):
				self.writeLog("Action: Removed user list")
				self.usersInfo={}
				ret=self.n4dClient.setUsersInfo(self.credentials,"AccessControlManager",self.usersInfo)
				if ret["status"]:
					print('   [Access-Control]: Action completed successfull')
					self._getUserInfo("End")
					return 0
				else:
					self.writeLog("Error removing user list: %s"%ret["msg"])
					print('   [Acess-Control]: Unable to delete users list')
					return 1
			else:
				print('   [Access-Control]: Action canceled')
				return 0
		else:
			print('   [Access-Control]: User list not exist. Nothing to do')
			return 0			

	#def removeUserList

	def _getInfo(self):

		self._getGroupInfo()
		self._getUserInfo()

	#def _getInfo

	def _getGroupInfo(self,step="Initial"):

		self.writeLog("Access Control by Group. %s configuration:"%step)
		self.isAccessDenyGroupEnabled=self.n4dClient.isAccessDenyGroupEnabled(self.credentials,"AccessControlManager")["status"]
		self.writeLog("- Access control by group activated: %s"%(str(self.isAccessDenyGroupEnabled)))
		self.groupsInfo=self.n4dClient.getGroupsInfo(self.credentials,"AccessControlManager")["data"]
		self.writeLog("- Groups with restricted access: ")
		for item in self.groupsInfo:
			self.writeLog("  - %s: locked access %s"%(item,str(self.groupsInfo[item]["isLocked"])))

	#def _getGroupInfo

	def _getUserInfo(self,step="Initial"):

		self.writeLog("Access Control by User. %s configuration:"%step)
		self.isAccessDenyUserEnabled=self.n4dClient.isAccessDenyUserEnabled(self.credentials,"AccessControlManager")["status"]
		self.writeLog("- Access Control by User activated: %s"%(str(self.isAccessDenyUserEnabled)))
		self.usersInfo=self.n4dClient.getUsersInfo(self.credentials,"AccessControlManager")["data"]
		self.writeLog("- Users with restricted access: ")
		if len(self.usersInfo)>0:
				for item in self.usersInfo:
					self.writeLog("  - %s: locked access %s"%(item,str(self.usersInfo[item]["isLocked"])))
		else:
			self.writeLog("  - There is no user list")
	
	#def _getUserInfo

	def _changeGroupStatus(self,groupsSelected,action):

		correctGroups=self._checkCorrectGroups(groupsSelected)

		if correctGroups:
			currentStatusChanged=self._checkCurrentConfiguration('groups',groupsSelected,action)
			if currentStatusChanged:
				if not self.unattendedMode:
					response=input('   [Access-Control]: Do you want to %s access to the indicated groups? (yes/no)): '%action).lower()
				else:
					response='yes'	
				
				if response.startswith('y'):
					self.writeLog("Changes in configuration of access control by Group:")		
					self.writeLog("- Try to change group list")
					ret=self._applyGroupChanges(groupsSelected,action)
					if ret["status"]:
						self.writeLog("- New groups with locked access: Changes apply successful")
						print('   [Access-Control]: Action completed successfull')
						self._getGroupInfo("End")
						return 0
					else:
						self.writeLog("- Error applying changes: %s"%ret["msg"])
						print('   [Acess-Control]: Unable to %s access to the indicated groups'%action)
						return 1			
				else:
					print('   [Access-Control]: Action canceled')
					return 0
			else:
				print('   [Access-Control]: The indicated groups are already %sed. Nothing to do'%action)
				return 0
		else:
			print('   [Access-Control]: The groups indicates to %s their acces are not correct. See currentconfig groups to get correct groups'%action)
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
			else:
				if self._checkIfUserIsCurrentUser(usersSelected) and action=="lock":
					print('   [Access-Control]: It is not possible to lock the user with which you are configuring the access control')
					return 0
				else:	
					adminInUsers=self._checkIfUserIsLocalAdmin(usersSelected)
					if adminInUsers[0]:
						if action=="lock":
							if not self.unattendedMode:
								countAdminUsers=len(adminInUsers[1])
								count=1
								for item in adminInUsers[1]:
									if count<countAdminUsers:
										adminUsers=adminUsers+item+', '
									else:
										adminUsers=adminUsers+item
									count+=1
								response=input('   [Access-Control]: The user(s) %s are local computer administrator. Do you want to continue? (yes/no)): '%adminUsers).lower()
							else:
								response='yes'

							if not response.startswith('y'):
								print('   [Access-Control]: Action canceled')
								return 0
					else:
						print('   [Access-Control]: The indicated users that are not in the list will be added')

		
		if adminUsers!="":
			self.writeLog("Action: Added admin user to user list: %s"%adminUsers)	

		currentStatusChanged=self._checkCurrentConfiguration('users',usersSelected,action)
		
		if currentStatusChanged:
			if not self.unattendedMode:
				response=input('   [Access-Control]: Do you want to %s access to the indicated users? (yes/no)): '%action).lower()
			else:
				response='yes'	
				
			if response.startswith('y'):
				self.writeLog("Changes in configuration of access control by User:")		
				self.writeLog("- Try to change user list")
				ret=self._applyUserChanges(usersSelected,action)
				if ret["status"]:
					self.writeLog("- New users with locked access: Changes apply successful")
					print('   [Access-Control]: Action completed successfull')
					self._getUserInfo("End")
					return 0
				else:
					self.writeLog("- Error applying changes: %s"%ret["msg"])
					print('   [Acess-Control]: Unable to %s access to the indicated users'%action)
					return 1			
			else:
				print('   [Access-Control]: Action canceled')
				return 0
		else:
			print('   [Access-Control]: The indicated users are already %sed. Nothing to do'%action)
			return 0

	#def _changeUsersStatus

	def _checkCorrectUsers(self,usersSelected):

		for item in usersSelected:
			if item not in self.usersInfo.keys():
				return False
		
		return True

	#def _checkCorrectUsers

	def _checkCurrentConfiguration(self,option,newValues,action):

		match=0

		if action=="lock":
			newStatus=True
		else:
			newStatus=False

		for item in newValues:
			if option=="groups":
				if self.groupsInfo[item]["isLocked"]!=newStatus:
					match+=1
			elif option=="users":
				try:
					if self.usersInfo[item]["isLocked"]!=newStatus:
						match+=1
				except:
					match+=1
					pass
		if match>0:
			return True
		else:
			return False

	#def _checkCurrentConfiguration

	def _applyGroupChanges(self,groupsSelected,action):

		for item in self.groupsInfo:
			if item in groupsSelected:
				if action=="lock":
					self.groupsInfo[item]["isLocked"]=True
				else:
					self.groupsInfo[item]["isLocked"]=False


		return self.n4dClient.setGroupsInfo(self.credentials,"AccessControlManager",self.groupsInfo)

	#def _applyGroupChanges	

	def _applyUserChanges(self,usersSelected,action):

		if action!="remove":
			for item in self.usersInfo:
				if item in usersSelected:
					if action=="lock":
						self.usersInfo[item]["isLocked"]=True
					elif action=="unlock":
						self.usersInfo[item]["isLocked"]=False
			if action=="lock":
				for item in usersSelected:
					if item not in self.usersInfo.keys():
						self.usersInfo[item]={}
						self.usersInfo[item]["isLocked"]=True
	
		else:
			for item in usersSelected:
				if item in self.usersInfo.keys():
					del self.usersInfo[item]
		
		return self.n4dClient.setUsersInfo(self.credentials,"AccessControlManager",self.usersInfo)

	#def _applyUserChanges	

	def _checkIfUserIsLocalAdmin(self,usersSelected):

		adminGroups=["sudo","admins","adm"]
		match=0
		adminUser=[]

		for item in usersSelected:
			if item not in self.usersInfo.keys():
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
			return [True,adminUser]
		else:
			return [False,adminUser]
	
	#def _checkIfUserIsLocalAdmin

	def _getCurrentUser(self):

		sudoUser=""
		loginUser=""
		pkexecUser=""

		try:
			sudoUser=(os.environ["SUDO_USER"])
		except:
			pass
		try:
			loginUser=os.getlogin()
		except:
			pass

		try:
			cmd="id -un $PKEXEC_UID"
			p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
			pkexecUser=p.communicate()[0].decode().strip()
		except Exception as e:
			pass

		if pkexecUser!="root" and pkexecUser!="":
			self.currentUser=pkexecUser
			if pkexecUser not in self.usersFilter:
				self.usersFilter.append(pkexecUser)

		elif sudoUser!="root" and sudoUser!="":
			self.currentUser=sudoUser
			if sudoUser not in self.usersFilter:
				self.usersFilter.append(sudoUser)
		
		else:
			self.currentUser=loginUser
			if loginUser not in self.usersFilter:
				self.usersFilter.append(loginUser)

		self.writeLog("Init session in lliurex-access-control CLI")
		self.writeLog("User login in CLI: %s"%self.currentUser)
		self.writeLog("Unattended Mode:%s"%(str(self.unattendedMode)))

	#def _getCurrentUser


	def _checkIfUserIsCurrentUser(self,usersSelected):

		for item in usersSelected:
			if item in self.usersFilter:
				return True

		return False

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

	def writeLog(self,msg):

		syslog.openlog("ACCESS-CONTROL")
		syslog.syslog(msg)

	#def writeLog


#class AccessControlCliManager	



