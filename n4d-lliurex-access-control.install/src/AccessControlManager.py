import os
import json
import codecs

class AccessControlManager:

	DISABLE_GROUP_ACCESS_CONTROL_ERROR=-10
	SET_GROUP_ERROR=-20
	DISABLE_USER_ACCESS_CONTROL_ERROR=-30
	SET_USER_ERROR=-40


	def __init__(self):

		self.configPath="/etc/lliurex-access-control"
		self.dataPath="/usr/share/lliurex-access-control-config/GroupsLists"
		self.groupTemplatePath=os.path.join(self.dataPath,"defaultGroups.json")
		self.groupDenyListPath=os.path.join(self.configPath,"login.group.deny")
		self.defaultGroupsFile=os.path.join(self.configPath+"/groups-lists","defaultGroups.json")
		self.userDenyListPath=os.path.join(self.configPath,"login.user.deny")
		self.usersList=os.path.join(self.configPath+"/users-lists","usersList.json")
	
	#def __init__

	def isAccessDenyGroupEnabled(self):

		isEnabled=False

		if os.path.exists(self.groupDenyListPath):
			isEnabled=True

		return {'status':isEnabled,'msg':'','data':''}

	#def isAccessDenyGroupEnabled

	def getGroupsInfo(self,initLoad=True):

		denyGroups=self._readDenyGroupsFile()
		groupsInfo=self._readGroupsList(initLoad)

		
		if len(denyGroups)>0:
			for item in groupsInfo:
				if item in denyGroups:
					groupsInfo[item]["isLocked"]=True
				else:
					groupsInfo[item]["isLocked"]=False

		return {'status':True, 'msg':'','data':groupsInfo}

	#def getGroupsInfo 

	def _readDenyGroupsFile(self):

		denyGroups=[]

		if self.isAccessDenyGroupEnabled()['status']:
			with open(self.groupDenyListPath,'r') as fd:
				lines=fd.readlines()
				for line in lines:
					denyGroups.append(line.strip())

		return denyGroups

	#def __readDenyGroupsFile

	def _readGroupsList(self,initLoad):

		templateGroups={}
		currentGroups={}

		if initLoad:

			with open(self.groupTemplatePath) as fd:
				templateGroups=json.load(fd)

			for item in templateGroups:
				templateGroups[item]["isLocked"]=False

			if not os.path.exists(self.defaultGroupsFile):
				self._writeDefaultGroupFile(templateGroups)
				return templateGroups

			else:
				with open(self.defaultGroupsFile) as fd:
					currentGroups=json.load(fd)

				if templateGroups.keys()!=currentGroups.keys():
					match=0
					for item in templateGroups:
						if item not in currentGroups.keys():
							match+=1
							currentGroups[item]={}
							currentGroups[item]=templateGroups[item]

					if match>0:
						self._writeDefaultGroupFile(currentGroups)

		else:
			if os.path.exists(self.defaultGroupsFile):
				with open(self.defaultGroupsFile) as fd:
					currentGroups=json.load(fd)
			
		return currentGroups

	#def _readGroupsList

	def setGroupsInfo(self,groupsInfo):

		denyGroups=[]
		try:
			if len(groupsInfo)>0:
				for item in groupsInfo:
					item=item.lower()
					if groupsInfo[item]["isLocked"]:
						denyGroups.append(item)

				self._writeDefaultGroupFile(groupsInfo)

				if len(denyGroups)>0:
					with open(self.groupDenyListPath,'w') as fd:
						for item in denyGroups:
							fd.write(item+"\n")
					return {'status':True,'msg':'Group info update successful','data':''}
				else:
					return self.disableAccessDenyGroup()
		except:
			return {'status':False,'msg':AccessControlManager.SET_GROUP_ERROR,'data':''}
	
	#def setDennyGroups

	def disableAccessDenyGroup(self):

		try:
			if self.isAccessDenyGroupEnabled()['status']:
				os.remove(self.groupDenyListPath)
		
			return {'status':True,'msg':'','data':''}
		except:
			return {'status':False,'msg':AccessControlManager.DISABLE_GROUP_ACCESS_CONTROL_ERROR,'data':''}
	
	#def disableAccessDenyGroup

	def isAccessDenyUserEnabled(self):

		isEnabled=False

		if os.path.exists(self.userDenyListPath):
			isEnabled=True

		return {'status':isEnabled,'msg':'','data':''}

	#def isAccessDenyUserEnabled

	def getUsersInfo(self):

		denyUsers=[]
		usersList={}

		denyUsers=self._readDenyUsersFile()
		usersList=self._readUsersList()

		if len(usersList)>0:
			if len(denyUsers)>0:
				for item in usersList:
					item=item.lower()
					if item in denyUsers:
						usersList[item]["isLocked"]=True
					else:
						usersList[item]["isLocked"]=False

		if len(denyUsers)>0:
			for item in denyUsers:
				item=item.lower()
				if item not in usersList:
					usersList[item]={}
					usersList[item]["isLocked"]=True

		return {'status':True,'msg':'','data':usersList}

	#def getDenyUsers 

	def _readDenyUsersFile(self):

		denyUsers=[]

		if self.isAccessDenyUserEnabled()['status']:
			with open(self.userDenyListPath,'r') as fd:
				lines=fd.readlines()
				for line in lines:
					denyUsers.append(line.strip())

		return denyUsers

	#def _readDenyUsersFile

	def _readUsersList(self):

		usersList={}

		if os.path.exists(self.usersList):
			with open(self.usersList,'r') as fd:
				usersList=json.load(fd)

		return usersList

	#def _readUsersList


	def setUsersInfo(self,usersInfo):

		denyUsers=[]

		try:
			if len(usersInfo)>0:
				for item in usersInfo:
					item=item.lower()
					if usersInfo[item]["isLocked"]:
						denyUsers.append(item)
				with open(self.usersList,'w') as fd:
					json.dump(usersInfo,fd)
				
				if len(denyUsers)>0:
					with open(self.userDenyListPath,'w') as fd:
						for item in denyUsers:
							fd.write(item+"\n")
					return {'status':True,'msg':'Users info updated successfull','data':''}
				else:
					return self.disableAccessDenyUser()

			else:
				if os.path.exists(self.usersList):
					os.remove(self.usersList)
					
				return self.disableAccessDenyUser()
			
		except Exception as e:
			return {'status':False,'msg':AccessControlManager.SET_USER_ERROR,'data':''}
	
	#def setDennyGroups

	def disableAccessDenyUser(self):

		try:
			if self.isAccessDenyUserEnabled()['status']:
				os.remove(self.userDenyListPath)
		
			return {'status':True,'msg':'','data':''}
		except:
			return {'status':False,'msg':AccessControlManager.DISABLE_USER_ACCESS_CONTROL_ERROR,'data':''}
	
	#def disableAccessDenyGroup

	def _writeDefaultGroupFile(self,data):

		with open(self.defaultGroupsFile,'w') as fd:
			json.dump(data,fd)
	
	#def _writeDefaultGroupFile

	
#class AccessControlManager 

