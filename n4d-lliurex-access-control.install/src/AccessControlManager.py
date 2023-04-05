#!/usr/bin/python3

import os
import json
import codecs

import n4d.responses
import n4d.server.core as n4dcore

class AccessControlManager:

	DISABLE_GROUP_ACCESS_CONTROL_ERROR=-10
	SET_GROUP_ERROR=-20
	DISABLE_USER_ACCESS_CONTROL_ERROR=-30
	SET_USER_ERROR=-40
	DISABLE_CDC_ACCESS_CONTROL_ERROR=-50
	SET_CDC_ERROR=-60

	def __init__(self):

		self.core=n4dcore.Core.get_core()
		self.configPath="/etc/lliurex-access-control"
		self.dataPath="/usr/share/lliurex-access-control-config/GroupsLists"
		self.groupTemplatePath=os.path.join(self.dataPath,"defaultGroups.json")
		self.groupDenyListPath=os.path.join(self.configPath,"login.group.deny")
		self.defaultGroupsFile=os.path.join(self.configPath+"/groups-lists","defaultGroups.json")
		self.userDenyListPath=os.path.join(self.configPath,"login.user.deny")
		self.usersList=os.path.join(self.configPath+"/users-lists","usersList.json")
		self.sssdConfigPath="/etc/sssd/sssd.conf"
		self.cdcInfo=os.path.join(self.configPath+"/cdc-info","cdc.json")
		self.cdcAllowListPath=os.path.join(self.configPath,"login.cdc.allow")
	
	#def __init__

	def isAccessDenyGroupEnabled(self):

		isEnabled=False

		if os.path.exists(self.groupDenyListPath):
			isEnabled=True

		return n4d.responses.build_successful_call_response(isEnabled)

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

		return n4d.responses.build_successful_call_response(groupsInfo)

	#def getGroupsInfo 

	def _readDenyGroupsFile(self):

		denyGroups=[]

		if self.isAccessDenyGroupEnabled()['return']:
			with open(self.groupDenyListPath,'r') as fd:
				lines=fd.readlines()
				for line in lines:
					denyGroups.append(line.strip())

		return denyGroups

	#def _readDenyGroupsFile

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

		return n4d.responses.build_successful_call_response(usersList)

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

	def _writeDefaultGroupFile(self,data):

		with open(self.defaultGroupsFile,'w') as fd:
			json.dump(data,fd)
	
	#def _writeDefaultGroupFile

	def isCDCAccessControlAllowed(self):

		isAllowed=False
		
		if os.path.exists(self.sssdConfigPath):
			isAllowed=True
		
		return n4d.responses.build_successful_call_response(isAllowed)

	#def isCdcAccessControlAllowed

	def isAccessDenyCDCEnabled(self):

		isEnabled=False
		if os.path.exists(self.cdcAllowListPath):
			isEnabled=True

		return n4d.responses.build_successful_call_response(isEnabled)
		
	#def isAccessDenyCdcEnabled

	def getCDCInfo(self):

		currentCode=self._readAllowCDCFile()
		cdcInfo=self._readCDCInfo()

		if len(cdcInfo)>0:
			if currentCode!="":
				if not cdcInfo["accessControlEnabled"]:
					cdcInfo["accessControlEnabled"]=True
				if cdcInfo["code"]!=currentCode:
					cdcInfo["code"]=currentCode
			else:
				if cdcInfo["accessControlEnabled"]:
					cdcInfo["accessControlEnabled"]=False

		else:
			if currentCode!="":
				cdcInfo["accessControlEnabled"]=True
				cdcInfo["code"]=currentCode
			else:
				cdcInfo["accessControlEnabled"]=False
				cdcInfo["code"]=""
				
		return n4d.responses.build_successful_call_response(cdcInfo)

	#def getCdcInfo

	def setCDCInfo(self,cdcInfo):

		currentCode=[]

		try:
			if len(cdcInfo)>0:
				with open(self.cdcInfo,'w') as fd:
					json.dump(cdcInfo,fd)

				if cdcInfo["accessControlEnabled"]:
					currentCode.append('GRP_%s'%cdcInfo["code"])
					currentCode.append('AdminSai')
					currentCode.append('sudo')

					with open(self.cdcAllowListPath,'w') as fd:
						for item in currentCode:
							fd.write(item+"\n")

					return n4d.responses.build_successful_call_response()

				else:
					return self.disableAccessDenyCDC()
			else:
				if os.path.exists(self.cdcInfo):
					os.remove(self.cdcInfo)
					return self.disableAccessDenyCDC()
		except:
			return n4d.responses.build_failed_call_response(AccessControlManager.SET_CDC_ERROR)
	
	#def setCdcInfo

	def _readCDCInfo(self):

		cdcInfo={}

		if os.path.exists(self.cdcInfo):
			with open(self.cdcInfo,'r') as fd:
				cdcInfo=json.load(fd)

		return cdcInfo

	#def _readCDCInfo

	def _readAllowCDCFile(self):

		allowCDC=""

		if self.isAccessDenyCDCEnabled()['return']:
			with open(self.cdcAllowListPath,'r') as fd:
				line=fd.readline()
				allowCDC=line.split("GRP_")[1].strip()

		return allowCDC

	#def _readAllowCDCFile

	def disableAccessDenyCDC(self,updateCDCInfo=False):

		try:
			if updateCDCInfo:
				try:
					cdcInfo=self._readCDCInfo()
					if len(cdcInfo)>0:
						if cdcInfo["accessControlEnabled"]:
							cdcInfo["accessControlEnabled"]=False
							with open(self.cdcInfo,'w') as fd:
								json.dump(cdcInfo,fd)
				except:
					pass
			if self.isAccessDenyCDCEnabled()['return']:
				os.remove(self.cdcAllowListPath)

			return n4d.responses.build_successful_call_response()
		except:
			return n4d.responses.build_failed_call_response(AccessControlManager.DISABLE_CDC_ACCESS_CONTROL_ERROR)
	
	#def disableAccessDenyCDC

#class AccessControlManager 

