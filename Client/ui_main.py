# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Login(object):
    def setupUi(self, Login):
        if not Login.objectName():
            Login.setObjectName(u"Login")
        Login.resize(500, 260)
        font = QFont()
        font.setFamily(u"Tahoma")
        Login.setFont(font)
        Login.setModal(False)
        self.ExitButton = QPushButton(Login)
        self.ExitButton.setObjectName(u"ExitButton")
        self.ExitButton.setGeometry(QRect(410, 200, 61, 41))

        self.retranslateUi(Login)
        self.ExitButton.clicked.connect(Login.close)

        QMetaObject.connectSlotsByName(Login)
    # setupUi

    def retranslateUi(self, Login):
        Login.setWindowTitle(QCoreApplication.translate("Login", u"\u4e3b\u9875\u9762", None))
        self.ExitButton.setText(QCoreApplication.translate("Login", u"\u9000\u51fa", None))
    # retranslateUi

