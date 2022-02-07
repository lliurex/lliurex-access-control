#!/usr/bin/python3
import os
import sys
from PySide2 import QtCore, QtGui, QtQml

class GroupsModel(QtCore.QAbstractListModel):

	GroupIdRole= QtCore.Qt.UserRole + 1000
	IsLockedRole = QtCore.Qt.UserRole + 1001
	DescriptionRole = QtCore.Qt.UserRole + 1002

	def __init__(self,parent=None):
		
		super(GroupsModel, self).__init__(parent)
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
			if role == GroupsModel.GroupIdRole:
				return item["groupId"]
			elif role == GroupsModel.IsLockedRole:
				return item["isLocked"]
			elif role == GroupsModel.DescriptionRole:
				return item["description"]
	#def data

	def roleNames(self):
		
		roles = dict()
		roles[GroupsModel.GroupIdRole] = b"groupId"
		roles[GroupsModel.IsLockedRole] = b"isLocked"
		roles[GroupsModel.DescriptionRole] = b"description"

		return roles

	#def roleName

	def appendRow(self,gi, il, d):
		
		self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(),self.rowCount())
		self._entries.append(dict(groupId=gi, isLocked=il, description=d))
		self.endInsertRows()

	#def appendRow

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
	
#class GroupModel
