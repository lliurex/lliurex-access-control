#!/usr/bin/python3

import os
import json
import codecs

import n4d.responses
import n4d.server.core as n4dcore

class AccessControlManager:

	DISABLE_GROUP_ACCESS_CONTROL_ERROR=-10
	SET_GROUP_ERROR=-20
	DISABLE_USER_ACCESS_CONTROL_ERROR=-40
	SET_USER_ERROR=-50

	def __init__(self):

		self.core=n4dcore.Core.get_core()
		self.configPath="/etc/lliurex-access-control"
		self.groupDenyListPath=os.path.join(self.configPath,"login.group.deny")
		self.defaultGroupsFile=os.path.join(self.configPath+"/groups-lists","defaultGroups.json")
		self.userDenyListPath=os.path.join(self.configPath,"login.user.deny")
		self.usersList=os.path.join(self.configPath+"/users-lists","usersList")
	
	#def __init__

	def isAccessDenyGroupEnabled(self):

		isEnabled=False

		if os.path.exists(self.groupDenyListPath):
			isEnabled=True

		return n4d.responses.build_successful_call_response(isEnabled)

	#def isAccessDenyGroupEnabled

	def getGroupsInfo(self):

		denyGroups=self._readDenyGroupsFile()
		groupsInfo=self._readGroupsList()

		for item in groupsInfo:
			if item in denyGroups:
				groupsInfo[item]["isLocked"]=True
			else:
				groupsInfo[item]["isLocked"]=False

		return n4d.responses.build_successful_call_response(groupsInfo)

	#def getDenyGroups 

	def _readDenyGroupsFile(self):

		denyGroups=[]

		if self.isAccessDenyGroupEnabled()['return']:
			with open(self.groupDenyListPath,'r') as fd:
				lines=fd.readlines()
				for line in lines:
					denyGroups.append(line.strip())

		return denyGroups

	#def __readDenyGroupsFile

	def _readGroupsList(self):

		groupsInfo={}

		if os.path.exists(self.defaultGroupsFile):
			f=open(self.defaultGroupsFile)
			groupsInfo=json.load(f)
			f.close()

		return groupsInfo

	#def __readGroupsList


	def setGroupsInfo(self,groupsInfo):

		denyGroups=[]
		try:
			if len(groupsInfo)>0:
				for item in groupsInfo:
					if groupsInfo[item]["isLocked"]:
						denyGroups.append(item)

				if len(denyGroups)>0:
					with open(self.groupDenyListPath,'w') as fd:
						for item in denyGroups:
							fd.write(item+"\n")
					return n4d.responses.build_successful_call_response()

				else:
					return self.disableAccessDenyGroup()
		except:
			return n4d.responses.build_failed_call_response(AccessControlManager.SET_GROUP_ERROR)
	
	#def setDennyGroups

	def disableAccessDenyGroup(self):

		try:
			if self.isAccessDenyGroupEnabled()['return']:
				os.remove(self.groupDenyListPath)
		
			return n4d.responses.build_successful_call_response()
		except:
			return n4d.responses.build_failed_call_response(AccessControlManager.DISABLE_GROUP_ACCESS_CONTROL_ERROR)
	
	#def disableAccessDenyGroup

	def isAccessDenyUserEnabled(self):

		isEnabled=False

		if os.path.exists(self.userDenyListPath):
			isEnabled=True

		return n4d.responses.build_successful_call_response(isEnabled)

	#def isAccessDenyUserEnabled

	def getUsersInfo(self):

		denyUsers=[]
		usersList=[]
		usersInfo={}

		denyUsers=self._readDenyUsersFile()
		usersList=self._readUsersList()

		if len(usersList)>0:
			for item in usersList:
				usersInfo[item]={}
				if item in denyUsers:
					usersInfo[item]["isLocked"]=True
				else:
					usersInfo[item]["isLocked"]=False

		if len(denyUsers)>0:
			for item in denyUsers:
				if item not in usersList:
					usersInfo[item]={}
					usersInfo[item]["isLocked"]=True

		return n4d.responses.build_successful_call_response(usersInfo)

	#def getDenyUsers 

	def _readDenyUsersFile(self):

		denyUsers=[]

		if self.isAccessDenyUserEnabled()['return']:
			with open(self.userDenyListPath,'r') as fd:
				lines=fd.readlines()
				for line in lines:
					denyUsers.append(line.strip())

		return denyUsers

	#def _readDenyUsersFile

	def _readUsersList(self):

		usersList=[]

		if os.path.exists(self.usersList):
			with open(self.usersList,'r') as fd:
				lines=fd.readlines()
				for line in lines:
					usersList.append(line.strip())

		return usersList

	#def _readUsersList


	def setUsersInfo(self,usersInfo):

		usersList=[]
		denyUsers=[]

		try:
			if len(usersInfo)>0:
				for item in usersInfo:
					usersList.append(item)
					if usersInfo[item]["isLocked"]:
						denyUsers.append(item)
				with open(self.usersList,'w') as fd:
					for item in usersList:
						fd.write(item+"\n")
				
				if len(denyUsers)>0:
					with open(self.userDenyListPath,'w') as fd:
						for item in denyUsers:
							fd.write(item+"\n")
					return n4d.responses.build_successful_call_response()
				else:
					return self.disableAccessDenyUser()

			else:
				if os.path.exists(self.usersList):
					os.remove(self.usersList)
					
				return self.disableAccessDenyUser()
			
		except Exception as e:
			return n4d.responses.build_failed_call_response(AccessControlManager.SET_USER_ERROR)
	
	#def setDennyGroups

	def disableAccessDenyUser(self):

		try:
			if self.isAccessDenyUserEnabled()['return']:
				os.remove(self.userDenyListPath)
		
			return n4d.responses.build_successful_call_response()
		except:
			return n4d.responses.build_failed_call_response(AccessControlManager.DISABLE_USER_ACCESS_CONTROL_ERROR)
	
	#def disableAccessDenyGroup
	
#class AccessControlManager 

