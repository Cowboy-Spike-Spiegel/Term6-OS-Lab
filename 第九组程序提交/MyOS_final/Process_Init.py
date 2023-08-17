import json
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form,Option):
        Form.setObjectName("Form")
        Form.resize(500, 300)
        self.verticalLayoutWidget = QtWidgets.QWidget(Form)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(40, 40, 420, 220))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.pushButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton_4.setObjectName("pushButton_4")
        self.verticalLayout.addWidget(self.pushButton_4)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        self.pushButton.clicked.connect(lambda: click(1,Option))
        self.pushButton_2.clicked.connect(lambda: click(2,Option))
        self.pushButton_3.clicked.connect(lambda: click(3,Option))
        self.pushButton_4.clicked.connect(lambda: click(4,Option))

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Device_init"))
        self.label.setText(_translate("Form", "选择进程调度算法"))
        self.pushButton.setText(_translate("Form", "Preemptive Priority"))
        self.pushButton_2.setText(_translate("Form", "FCFS"))
        self.pushButton_3.setText(_translate("Form", "RR"))
        self.pushButton_4.setText(_translate("Form", "Non-preemptive Priority"))


def click(size,Option):
    dict=['e','f','r','p']
    if dict[size] == 'e':
        Option = "Preemptive Priority"

