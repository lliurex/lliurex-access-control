#!/usr/bin/python3

import os
import json
import codecs

import n4d.responses
import n4d.server.core as n4dcore

class AccessControlManager:

	DISABLE_GROUP_ACCESS_CONTROL_ERROR=-10
	SET_GROUP_ERROR=-20
	REMOVE_USERS_LIST_ERROR=-30
	DISABLE_USER_ACCESS_CONTROL_ERROR=-40
	SET_USER_ERROR=-50
	SET_USERS_LIST_ERROR=-60


	def __init__(self):

		self.core=n4dcore.Core.get_core()
		self.configPath="/etc/lliurex-access-control"
		self.groupDenyListPath=os.path.join(self.configPath,"login.group.deny")
		self.defaultGroupsFile=os.path.join(self.configPath+"/groups-lists","defaultGroups.json")
		self.userDenyListPath=os.path.join(self.configPath,"login.user.deny")
		self.userList=os.path.join(self.configPath+"/users-lists","userList")
	
	#def __init__

	def isAccessDenyGroupEnabled(self):

		isEnabled=False

		if os.path.exists(self.groupDenyListPath):
			isEnabled=True

		return n4d.responses.build_successful_call_response(isEnabled)

	#def isAccessDenyGroupEnabled

	def getDenyGroups(self):

		denyGroups=[]

		if self.isAccessDenyGroupEnabled()['return']:
			with open(self.groupDenyListPath,'r') as fd:
				lines=fd.readlines()
				for line in lines:
					denyGroups.append(line.strip())

		return n4d.responses.build_successful_call_response(denyGroups)

	#def getDenyGroups 

	def setDenyGroups(self,groupList):

		try:
			if len(groupList)>0:
				with open(self.groupDenyListPath,'w') as fd:
					for item in groupList:
						fd.write(item+"\n")

			return n4d.responses.build_successful_call_response()
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

	def getGroupList(self):

		defaultGroups={}
		if os.path.exists(self.defaultGroupsFile):
			f=open(self.defaultGroupsFile)
			defaultGroups=json.load(f)
			f.close()
			return n4d.responses.build_successful_call_response(defaultGroups)

	#def getGroupList

	def isAccessDenyUserEnabled(self):

		isEnabled=False

		if os.path.exists(self.userDenyListPath):
			isEnabled=True

		return n4d.responses.build_successful_call_response(isEnabled)

	#def isAccessDenyUserEnabled

	def getDenyUsers(self):

		denyUsers=[]

		if self.isAccessDenyUserEnabled()['return']:
			with open(self.userDenyListPath,'r') as fd:
				lines=fd.readlines()
				for line in lines:
					denyUsers.append(line.strip())

		return n4d.responses.build_successful_call_response(denyUsers)

	#def getDenyUsers 

	def setDenyUsers(self,userList):

		try:
			if len(userList)>0:
				with open(self.userDenyListPath,'w') as fd:
					for item in userList:
						fd.write(item+"\n")

			return n4d.responses.build_successful_call_response()
		except:
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

	def getUsersList(self):

		usersList=[]
		if os.path.exists(self.userList):
			with open(self.userList,'r') as fd:
				lines=fd.readlines()
				for line in lines:
					usersList.append(line.strip())

		return n4d.responses.build_successful_call_response(usersList)


	#def getUsersList

	def setUsersList(self,userList):

		try:
			if len(userList)>0:
				with open(self.userList,'w') as fd:
					for item in userList:
						fd.write(item+"\n")
			else:
				os.remove(self.userList)
			return n4d.responses.build_successful_call_response()
		except:
			return n4d.responses.build_failed_call_response(AccessControlManager.SET_USERS_LIST_ERROR)
	
	#def setDennyGroups

	
#class AccessControlManager 

