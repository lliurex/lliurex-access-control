#!/usr/bin/python3
import os
import sys
from PySide6 import QtCore, QtGui, QtQml

class UsersModel(QtCore.QAbstractListModel):

	UserIdRole= QtCore.Qt.UserRole + 1000
	IsLockedRole = QtCore.Qt.UserRole + 1001

	def __init__(self,parent=None):
		
		super(UsersModel, self).__init__(parent)
		self._entries =[]
	#def __init__

	def rowCount(self, parent=QtCore.QModelIndex()):
		
		if parent.isValid():
			return 0
		return len(self._entries)

	#def rowCount

	def data(self, index, role=QtCore.Qt.DisplayRole):
		
		if 0 <= index.row() < self.rowCount() and index.isValid():
			item = self._entries[index.row()]
			if role == UsersModel.UserIdRole:
				return item["userId"]
			elif role == UsersModel.IsLockedRole:
				return item["isLocked"]
	#def data

	def roleNames(self):
		
		roles = dict()
		roles[UsersModel.UserIdRole] = b"userId"
		roles[UsersModel.IsLockedRole] = b"isLocked"

		return roles

	#def roleName

	def appendRow(self,ui,il):
		
		tmpId=[]
		for item in self._entries:
			tmpId.append(item["userId"])
		tmpUI=ui.strip()
		if ui not in tmpId and ui !="" and len(tmpUI)>0:
			self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(),self.rowCount())
			self._entries.append(dict(userId=ui, isLocked=il))
			self.endInsertRows()

	#def appendRow

	def removeRow(self,index):
		self.beginRemoveRows(QtCore.QModelIndex(),index,index)
		self._entries.pop(index)
		self.endRemoveRows()
	
	#def removeRow

	def setData(self, index, param, value, role=QtCore.Qt.EditRole):
		
		if role == QtCore.Qt.EditRole:
			row = index.row()
			if param in ["isLocked"]:
				self._entries[row][param]=value
				self.dataChanged.emit(index,index)
				return True
			else:
				return False
	
	#def setData

	def clear(self):
		
		count=self.rowCount()
		self.beginRemoveRows(QtCore.QModelIndex(), 0, count)
		self._entries.clear()
		self.endRemoveRows()
	
	#def clear
	
#class UsersModel
