#!/usr/bin/python3
import os
import sys
from PySide2 import QtCore, QtGui, QtQml

class UsersModel(QtCore.QAbstractListModel):

	UserIdRole= QtCore.Qt.UserRole + 1000
	IsCheckedRole = QtCore.Qt.UserRole + 1001

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
			elif role == UsersModel.IsCheckedRole:
				return item["isChecked"]
	#def data

	def roleNames(self):
		
		roles = dict()
		roles[UsersModel.UserIdRole] = b"userId"
		roles[UsersModel.IsCheckedRole] = b"isChecked"

		return roles

	#def roleName

	def appendRow(self,ui, ic):
		
		tmpId=[]
		for item in self._entries:
			print(item)
			tmpId.append(item["userId"])
		print(tmpId)
		if ui not in tmpId:
			self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(),self.rowCount())
			self._entries.append(dict(userId=ui, isChecked=ic))
			print(self._entries)
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
			if param in ["isChecked"]:
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
	
#class GroupModel
