#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
signal.signal(signal.SIGINT, signal.SIG_DFL)

class UpdateInfo(QThread):

	def __init__(self,*args):

		QThread.__init__(self)

		self.enabledInfo=args[0]
		self.listInfo=args[1]
		self.ret=[]

	#def __init__

	def run(self,*args):
		
		time.sleep(1)
		self.ret=Bridge.n4dMan.applyCDCChanges(self.enabledInfo,self.listInfo)

	#def run

#class UpdateInfo

class Bridge(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.n4dMan=self.core.n4dManager
		self._isAccessDenyCDCEnabled=False
		self._settingsCDCChanged=False
		self._showSettingsCDCMessage=[False,"","Success"]
		self._showCDCChangesDialog=False
		self._isCDCAccessControlAllowed=False
		self._cdcCode=""
		self.correctCode=True

	#def __init__

	def getCDCConfig(self):

		self.isCDCAccessControlAllowed=copy.deepcopy(Bridge.n4dMan.isCDCAccessControlAllowed)
		self.isAccessDenyCDCEnabled=copy.deepcopy(Bridge.n4dMan.isAccessDenyCDCEnabled)
		self.cdcInfo=copy.deepcopy(Bridge.n4dMan.cdcInfo)
		if len(self.cdcInfo)>0:
			self.cdcCode=self.cdcInfo["code"]

	#def getCdcConfig

	def _getIsCDCAccessControlAllowed(self):

		return self._isCDCAccessControlAllowed

	#def _getIsCDCAccessControlAllowed

	def _setIsCDCAccessControlAllowed(self,isCDCAccessControlAllowed):

		if self._isCDCAccessControlAllowed!=isCDCAccessControlAllowed:
			self._isCDCAccessControlAllowed=isCDCAccessControlAllowed
			self.on_isCDCAccessControlAllowed.emit()

	#def _setIsCDCAccessControlAllowed):

	def _getIsAccessDenyCDCEnabled(self):

		return self._isAccessDenyCDCEnabled

	#def _getIsAccessDenyCDCEnabled

	def _setIsAccessDenyCDCEnabled(self,isAccessDenyCDCEnabled):

		if self._isAccessDenyCDCEnabled!=isAccessDenyCDCEnabled:
			self._isAccessDenyCDCEnabled=isAccessDenyCDCEnabled
			self.on_isAccessDenyCDCEnabled.emit()

	#def _setIsAccessDenyCDCEnabled:

	def _getCdcCode(self):

		return self._cdcCode

	#def _getCdcCode

	def _setCdcCode(self,cdcCode):

		if self._cdcCode!=cdcCode:
			self._cdcCode=cdcCode
			self.on_cdcCode.emit()

	#def _setCdcCode

	def _getSettingsCDCChanged(self):

		return self._settingsCDCChanged

	#def _getSettingsCDCChanged

	def _setSettingsCDCChanged(self,settingsCDCChanged):

		if self._settingsCDCChanged!=settingsCDCChanged:
			self._settingsCDCChanged=settingsCDCChanged
			self.on_settingsCDCChanged.emit()

	#def _setSettingsCDCChanged

	def _getShowSettingsCDCMessage(self):

		return self._showSettingsCDCMessage

	#def _getShowSettingsCDCMessage

	def _setShowSettingsCDCMessage(self,showSettingsCDCMessage):

		if self._showSettingsCDCMessage!=showSettingsCDCMessage:
			self._showSettingsCDCMessage=showSettingsCDCMessage
			self.on_showSettingsCDCMessage.emit()

	#def _setShowSettingsCDCMessage

	def _getShowCDCChangesDialog(self):

		return self._showCDCChangesDialog

	#def _getShowCDCChangesDialog	

	def _setShowCDCChangesDialog(self,showCDCChangesDialog):
		
		if self._showCDCChangesDialog!=showCDCChangesDialog:
			self._showCDCChangesDialog=showCDCChangesDialog		
			self.on_showCDCChangesDialog.emit()

	#def _setShowCDCChangesDialog

	@Slot(bool)
	def manageCDCAccessControl(self,value):

		self.showSettingsCDCMessage=[False,"","Success"]
		
		if value!=self.isAccessDenyCDCEnabled:
			self.isAccessDenyCDCEnabled=value
			self.cdcInfo["accessControlEnabled"]=value
			if self.isAccessDenyCDCEnabled!=Bridge.n4dMan.isAccessDenyCDCEnabled:
				self.settingsCDCChanged=True
			else:
				self.settingsCDCChanged=False
					
	#def manageCDCAccessControl

	@Slot(str)
	def manageCDCCodeChange(self,newCode):

		self.showSettingsCDCMessage=[False,"","Success"]
		self.correctCode=Bridge.n4dMan.isCorrectCode(newCode)
		if self.correctCode:
			if self.cdcCode!=newCode:
				self.cdcCode=newCode
				self.cdcInfo["code"]=newCode
				if self.cdcCode!=Bridge.n4dMan.cdcInfo["code"]:
					self.settingsCDCChanged=True
				else:
					self.settingsCDCChanged=False

			if self.cdcCode=="" :
				self.isAccessDenyCDCEnabled=False
		else:
			self.showSettingsCDCMessage=[True,Bridge.n4dMan.CDC_CODE_NOT_VALID,"Error"]

	#def manageCDCCodeChange

	@Slot()
	def applyCDCChanges(self):

		self.showSettingsCDCMessage=[False,"","Success"]
		if self.correctCode or not self.isAccessDenyCDCEnabled:
			self.correctCode=True
			self.core.mainStack.closePopUp=False
			self.showCDCChangesDialog=False
			self.updateCDCInfo=UpdateInfo(self.isAccessDenyCDCEnabled,self.cdcInfo)
			self.updateCDCInfo.start()
			self.updateCDCInfo.finished.connect(self._applyCDCChanges)
		else:
			self.showSettingsCDCMessage=[True,Bridge.n4dMan.CDC_CODE_NOT_VALID,"Error"]
	
	#def applyCdcChanges

	def _applyCDCChanges(self):

		if self.updateCDCInfo.ret[0]:
			self._updateCDCConfig()
			time.sleep(1)
			self.showSettingsCDCMessage=[True,self.updateCDCInfo.ret[1],"Success"]
			self.core.mainStack.closeGui=True
		else:
			self.showSettingsCDCMessage=[True,self.updateCDCInfo.ret[1],"Error"]
			self.core.mainStack.closeGui=False
			self.core.mainStack.moveToStack=""

		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
			self.showSettingsCDCMessage=[False,"","Info"]
			self.core.mainStack.moveToStack=""

		self.settingsCDCChanged=False
		self.core.mainStack.closePopUp=True

	#def _applyCDCChanges

	@Slot()
	def cancelCDCChanges(self):

		self.showSettingsCDCMessage=[False,"","Success"]
		self.correctCode=True
		self.core.mainStack.closePopUp=False
		self.showCDCChangesDialog=False
		self._cancelCDCChanges()

	#def cancelUserChanges

	def _cancelCDCChanges(self):

		self._updateCDCConfig()
		self.settingsCDCChanged=False
		self.core.mainStack.closePopUp=True
		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
		self.core.mainStack.moveToStack=""
		
		self.core.mainStack.closeGui=True

	#def _cancelCDCChanges

	def _updateCDCConfig(self):

		self.isAccessDenyCDCEnabled=copy.deepcopy(Bridge.n4dMan.isAccessDenyCDCEnabled)
		self.cdcInfo=copy.deepcopy(Bridge.n4dMan.cdcInfo)
		self.cdcCode=""
		self.cdcCode=self.cdcInfo["code"]
	
	#def _updateCDCConfig
	
	on_isCDCAccessControlAllowed=Signal()
	isCDCAccessControlAllowed=Property(bool,_getIsCDCAccessControlAllowed,_setIsCDCAccessControlAllowed,notify=on_isCDCAccessControlAllowed)

	on_isAccessDenyCDCEnabled=Signal()
	isAccessDenyCDCEnabled=Property(bool,_getIsAccessDenyCDCEnabled,_setIsAccessDenyCDCEnabled,notify=on_isAccessDenyCDCEnabled)
	
	on_cdcCode=Signal()
	cdcCode=Property(str,_getCdcCode,_setCdcCode,notify=on_cdcCode)
	
	on_settingsCDCChanged=Signal()
	settingsCDCChanged=Property(bool,_getSettingsCDCChanged,_setSettingsCDCChanged, notify=on_settingsCDCChanged)

	on_showSettingsCDCMessage=Signal()
	showSettingsCDCMessage=Property('QVariantList',_getShowSettingsCDCMessage,_setShowSettingsCDCMessage,notify=on_showSettingsCDCMessage)
	
	on_showCDCChangesDialog=Signal()
	showCDCChangesDialog=Property(bool,_getShowCDCChangesDialog,_setShowCDCChangesDialog, notify=on_showCDCChangesDialog)

#class Bridge

import Core

