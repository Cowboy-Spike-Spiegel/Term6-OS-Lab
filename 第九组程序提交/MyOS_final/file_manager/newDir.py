# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newDir.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_new_dir_dlg(object):
    def setupUi(self, new_dir_dlg):
        new_dir_dlg.setObjectName("new_dir_dlg")
        new_dir_dlg.setWindowModality(QtCore.Qt.WindowModal)
        new_dir_dlg.resize(431, 382)
        new_dir_dlg.setMinimumSize(QtCore.QSize(431, 382))
        new_dir_dlg.setMaximumSize(QtCore.QSize(431, 382))
        new_dir_dlg.setModal(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(new_dir_dlg)
        self.verticalLayout.setContentsMargins(0, 9, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.filename_widget = QtWidgets.QWidget(new_dir_dlg)
        self.filename_widget.setObjectName("filename_widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.filename_widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.filename_label = QtWidgets.QLabel(self.filename_widget)
        self.filename_label.setObjectName("filename_label")
        self.horizontalLayout.addWidget(self.filename_label)
        self.filename_lineedit = QtWidgets.QLineEdit(self.filename_widget)
        self.filename_lineedit.setObjectName("filename_lineedit")
        self.horizontalLayout.addWidget(self.filename_lineedit)
        self.verticalLayout.addWidget(self.filename_widget)
        self.btn_widget = QtWidgets.QWidget(new_dir_dlg)
        self.btn_widget.setObjectName("btn_widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.btn_widget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.certain_btn = QtWidgets.QPushButton(self.btn_widget)
        self.certain_btn.setObjectName("certain_btn")
        self.horizontalLayout_2.addWidget(self.certain_btn)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.cancel_btn = QtWidgets.QPushButton(self.btn_widget)
        self.cancel_btn.setObjectName("cancel_btn")
        self.horizontalLayout_2.addWidget(self.cancel_btn)
        self.verticalLayout.addWidget(self.btn_widget)

        self.retranslateUi(new_dir_dlg)
        QtCore.QMetaObject.connectSlotsByName(new_dir_dlg)

    def retranslateUi(self, new_dir_dlg):
        _translate = QtCore.QCoreApplication.translate
        new_dir_dlg.setWindowTitle(_translate("new_dir_dlg", "新建文件夹"))
        self.filename_label.setText(_translate("new_dir_dlg", "文件名称"))
        self.certain_btn.setText(_translate("new_dir_dlg", "确定"))
        self.cancel_btn.setText(_translate("new_dir_dlg", "取消"))
