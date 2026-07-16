#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import signal
import copy
import time
signal.signal(signal.SIGINT, signal.SIG_DFL)

class UpdateInfo(QThread):

	infoUpdated=Signal(dict)

	def __init__(self,manager,enableCDCControl,cdcInfo):

		super().__init__()

		self.manager=manager
		self.enableCDCControl=enableCDCControl
		self.cdcInfo=cdcInfo

	#def __init__

	def run(self,*args):
		
		time.sleep(1)
		ret=self.manager.applyCDCChanges(self.enableCDCControl,self.cdcInfo)
		self.infoUpdated.emit(ret)

	#def run

#class UpdateInfo

class Bridge(QObject):

	isCDCAccessControlAllowedChanged=Signal()
	isCDCAccessControlEnabledChanged=Signal()
	cdcCodeChanged=Signal()
	hasCDCChangesChanged=Signal()
	showSettingsCDCMessageChanged=Signal()
	showCDCChangesDialogChanged=Signal()


	def __init__(self):

		super().__init__()
		self.core=Core.Core.get_core()
		self.n4dManager=self.core.n4dManager
		self._isCDCAccessControlEnabled=False
		self._hasCDCChanges=False
		self._showSettingsCDCMessage={"show":False,"msgCode":"","type":""}
		self._showCDCChangesDialog=False
		self._isCDCAccessControlAllowed=False
		self._cdcCode=""
		self.correctCode=True

	#def __init__

	@Property(bool,notify=isCDCAccessControlAllowedChanged)
	def isCDCAccessControlAllowed(self):

		return self._isCDCAccessControlAllowed

	#def isCDCAccessControlAllowed

	@isCDCAccessControlAllowed.setter
	def isCDCAccessControlAllowed(self,isCDCAccessControlAllowed):

		if self._isCDCAccessControlAllowed!=isCDCAccessControlAllowed:
			self._isCDCAccessControlAllowed=isCDCAccessControlAllowed
			self.isCDCAccessControlAllowedChanged.emit()

	#def isCDCAccessControlAllowed)

	@Property(bool,notify=isCDCAccessControlEnabledChanged)
	def isCDCAccessControlEnabled(self):

		return self._isCDCAccessControlEnabled

	#def isCDCAccessControlEnabled

	@isCDCAccessControlEnabled.setter
	def isCDCAccessControlEnabled(self,isCDCAccessControlEnabled):

		if self._isCDCAccessControlEnabled!=isCDCAccessControlEnabled:
			self._isCDCAccessControlEnabled=isCDCAccessControlEnabled
			self.isCDCAccessControlEnabledChanged.emit()

	#def isCDCAccessControlEnabled:

	@Property(str,notify=cdcCodeChanged)
	def cdcCode(self):

		return self._cdcCode

	#def cdcCode

	@cdcCode.setter
	def cdcCode(self,cdcCode):

		if self._cdcCode!=cdcCode:
			self._cdcCode=cdcCode
			self.cdcCodeChanged.emit()

	#def cdcCode

	@Property(bool, notify=hasCDCChangesChanged)
	def hasCDCChanges(self):

		return self._hasCDCChanges

	#def hasCDCChanges

	@hasCDCChanges.setter
	def hasCDCChanges(self,hasCDCChanges):

		if self._hasCDCChanges!=hasCDCChanges:
			self._hasCDCChanges=hasCDCChanges
			self.hasCDCChangesChanged.emit()

	#def hasCDCChanges

	@Property(dict,notify=showSettingsCDCMessageChanged)
	def showSettingsCDCMessage(self):

		return self._showSettingsCDCMessage

	#def showSettingsCDCMessage

	@showSettingsCDCMessage.setter
	def showSettingsCDCMessage(self,showSettingsCDCMessage):

		if self._showSettingsCDCMessage!=showSettingsCDCMessage:
			self._showSettingsCDCMessage=showSettingsCDCMessage
			self.showSettingsCDCMessageChanged.emit()

	#def showSettingsCDCMessage

	@Property(bool,notify=showCDCChangesDialogChanged)
	def showCDCChangesDialog(self):

		return self._showCDCChangesDialog

	#def showCDCChangesDialog	

	@showCDCChangesDialog.setter
	def showCDCChangesDialog(self,showCDCChangesDialog):
		
		if self._showCDCChangesDialog!=showCDCChangesDialog:
			self._showCDCChangesDialog=showCDCChangesDialog		
			self.showCDCChangesDialogChanged.emit()

	#def showCDCChangesDialog

	def getCDCConfig(self):

		self.isCDCAccessControlAllowed=self.n4dManager.isCDCAccessControlAllowed
		self.isCDCAccessControlEnabled=self.n4dManager.isCDCAccessControlEnabled
		self.cdcInfo=copy.deepcopy(self.n4dManager.cdcInfo)
		self.cdcCode=self.cdcInfo.get("code","")

	#def getCdcConfig


	@Slot(bool)
	def manageCDCAccessControl(self,value):

		self.showSettingsCDCMessage={"show":False,"msgCode":"","type":""}
		
		if value!=self.isCDCAccessControlEnabled:
			self.isCDCAccessControlEnabled=value
			self.cdcInfo["accessControlEnabled"]=value
			self.hasCDCChanges=(self.isCDCAccessControlEnabled!=self.n4dManager.isCDCAccessControlEnabled)
					
	#def manageCDCAccessControl

	@Slot(str)
	def manageCDCCodeChange(self,newCode):

		self.showSettingsCDCMessage={"show":False,"msgCode":"","type":""}
		self.correctCode=self.n4dManager.isCorrectCode(newCode)

		if self.correctCode:
			if self.cdcCode!=newCode:
				self.cdcCode=newCode
				self.cdcInfo["code"]=newCode
				self.hasCDCChanges=(self.cdcCode!=self.n4dManager.cdcInfo.get("code"))
			
			if self.cdcCode=="" :
				self.isCDCAccessControlEnabled=False
		else:
			self.showSettingsCDCMessage={"show":True,"msgCode":self.n4dManager.CDC_CODE_NOT_VALID,"type":self.n4dManager.KIRIGAMI_MSG_ERROR}

	#def manageCDCCodeChange

	@Slot()
	def applyCDCChanges(self):

		self.showSettingsCDCMessage={"show":False,"msgCode":"","type":""}

		if self.correctCode or not self.isCDCAccessControlEnabled:
			self.correctCode=True
			self.core.mainStack.showPopUp={"show":True,"msgCode":self.core.mainStack.SAVE_DATA_MSG}
			self.showCDCChangesDialog=False
			self.updateCDCInfoT=UpdateInfo(self.n4dManager,self.isCDCAccessControlEnabled,self.cdcInfo)
			self.updateCDCInfoT.start()
			self.updateCDCInfoT.infoUpdated.connect(self._applyCDCChanges)
			self.updateCDCInfoT.finished.connect(self.updateCDCInfoT.deleteLater)
		else:
			self.showSettingsCDCMessage={"show":True,"msgCode":self.n4dManager.CDC_CODE_NOT_VALID,"type":self.n4dManager.KIRIGAMI_MSG_ERROR}
	
	#def applyCdcChanges

	@Slot(dict)
	def _applyCDCChanges(self,ret):

		if ret.get("status"):
			self._updateCDCConfig()
			self.core.mainStack.closeGui=True
		else:
			self.core.mainStack.closeGui=False
			self.core.mainStack.moveToStack=""

		self.showSettingsCDCMessage={"show":True,"msgCode":ret.get("code"),"type":ret.get("type")}

		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
			self.showSettingsCDCMessage={"show":False,"msgCode":"","type":""}
			self.core.mainStack.moveToStack=""

		self.hasCDCChanges=False
		self.core.mainStack.showPopUp={"show":False,"msgCode":""}

	#def _applyCDCChanges

	@Slot()
	def cancelCDCChanges(self):

		self.showSettingsCDCMessage={"show":False,"msgCode":"","type":""}
		self.correctCode=True
		self.core.mainStack.showPopUp={"show":True,"msgCode":self.core.mainStack.RESTORE_DATA_MSG}
		self.showCDCChangesDialog=False
		self._cancelCDCChanges()

	#def cancelUserChanges

	def _cancelCDCChanges(self):

		self._updateCDCConfig()
		self.hasCDCChanges=False
		self.core.mainStack.showPopUp={"show":False,"msgCode":""}
		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
		self.core.mainStack.moveToStack=""
		
		self.core.mainStack.closeGui=True

	#def _cancelCDCChanges

	def _updateCDCConfig(self):

		self.isCDCAccessControlEnabled=copy.deepcopy(self.n4dManager.isCDCAccessControlEnabled)
		self.cdcInfo=copy.deepcopy(self.n4dManager.cdcInfo)
		self.cdcCode=""
		self.cdcCode=self.cdcInfo.get("code")
	
	#def _updateCDCConfig
	

#class Bridge

import Core

