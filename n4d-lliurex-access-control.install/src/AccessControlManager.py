#!/usr/bin/python3

import os
import n4d.responses
import n4d.server.core as n4dcore

class AccessControlManager:

	DISABLE_ACCESS_CONTROL_ERROR=-10
	SET_GROUP_ERROR=-20

	def __init__(self):

		self.core=n4dcore.Core.get_core()
		self.configPath="/etc/lliurex-access-control"
		self.groupListPath=os.path.join(self.configPath,"login.group.deny")

	#def __init__

	def isAccessDenyGroupEnabled(self):

		isEnabled=False

		if os.path.exists(self.groupListPath):
			isEnabled=True

		return n4d.responses.build_successful_call_response(isEnabled)

	#def isAccessDenyGroupEnabled

	def getDenyGroups(self):

		denyGroups=[]

		if self.isAccessDenyGroupEnabled()['return']:
			with open(self.groupListPath,'r') as fd:
				lines=fd.readlines()
				for line in lines:
					denyGroups.append(line.strip())

		return n4d.responses.build_successful_call_response(denyGroups)

	#def getDenyGroups 

	def setDenyGroups(self,groupList):

		try:
			if len(groupList)>0:
				with open(self.groupListPath,'w') as fd:
					for item in groupList:
						fd.write(item+"\n")

			return n4d.responses.build_successful_call_response()
		except:
			return n4d.responses.build_failed_call_response(AccessControlManager.SET_GROUP_ERROR)
	
	#def setDennyGroups

	def disableAccessDenyGroup(self):

		try:
			if self.isAccessDenyGroupEnabled()['return']:
				os.remove(self.groupListPath)
		
			return n4d.responses.build_successful_call_response()
		except:
			return n4d.responses.build_failed_call_response(AccessControlManager.DISABLE_ACCESS_CONTROL_ERROR)
	
	#def disableAccessDenyGroup

#class ComputerAccessControlManager 

