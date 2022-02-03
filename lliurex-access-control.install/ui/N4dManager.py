#!/usr/bin/python3

import n4d.client
import os
import json
import codecs

class N4dManager:

	APPLY_CHANGES_SUCCESSFUL=10
	APPLY_CHANGES_WITHOUT_GROUP=-30

	def __init__(self,ticket):

		self.debug=True
		ticket=ticket.replace('##U+0020##',' ')
		self.defaultGroupsFile="/etc/lliurex-access-control/groups-lists/defaultGroups.json"
		self.defaultGroups={}
		self.groupsConfigData=[]
		self.sessionLang=""
		self.isAccessDenyGroupEnabled=False
		self.denyGroups=[]
		self.setServer(ticket)
		self.getSessionLang()
		self.loadConfig()


	#def __init__

	def setServer(self,ticket):

		tk=n4d.client.Ticket(ticket)
		self.client=n4d.client.Client(ticket=tk)
	
	#def setServer

	def loadConfig(self):
		
		self.isAccessDenyGroupEnabled=self.client.AccessControlManager.isAccessDenyGroupEnabled()
		self.denyGroups=self.client.AccessControlManager.getDenyGroups()
		self.getGroupsConfig()

	#def _loadConfig

	def _readDefaultGroups(self):

		if os.path.exists(self.defaultGroupsFile):
			f=open(self.defaultGroupsFile)
			self.defaultGroups=json.load(f)
			f.close()

		#def _readDefaultGroups

	def getSessionLang(self):

		lang=os.environ["LANG"]
		
		if 'valencia' in lang:
			self.sessionLang="ca@valencia"
		else:
			self.sessionLang="es"

	#def getSessionLang

	def getGroupsConfig(self):

		self._readDefaultGroups()
		self.groupsConfigData=[]

		for item in self.defaultGroups:
			tmp={}
			tmp["groupId"]=item
			if item in self.denyGroups:
				tmp["isChecked"]=True
			else:
				tmp["isChecked"]=False
			tmp["description"]=self.defaultGroups[item][self.sessionLang]

			self.groupsConfigData.append(tmp)

	#def getGroupsConfig 			

	def applyChanges(self,groupAccessControl,denyGroups):

		disableControl=False
		updateDenyGroup=False
		result=[]


		if not groupAccessControl:
			if groupAccessControl != self.isAccessDenyGroupEnabled:
				disableControl=True
		else:
			if len(denyGroups)==0:
				result=[False,N4dManager.APPLY_CHANGES_WITHOUT_GROUP]
				return result
			else:
				if denyGroups != self.denyGroups:
					updateDenyGroup=True

		if disableControl:
			try:
				ret=self.client.AccessControlManager.disableAccessDenyGroup()
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				result=[False,e.code]

		if updateDenyGroup:
			try:
				ret=self.client.AccessControlManager.setDenyGroups(denyGroups)		
				result=[True,N4dManager.APPLY_CHANGES_SUCCESSFUL]
			except n4d.client.CallFailedError as e:
				result=[False,e.code]

		if result[0]:
			self.loadConfig()
		return result

	#def applyChanges

#class N4dManager
