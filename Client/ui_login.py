# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login.ui'
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
        self.username = QLineEdit(Login)
        self.username.setObjectName(u"username")
        self.username.setGeometry(QRect(30, 30, 220, 40))
        font1 = QFont()
        font1.setFamily(u"Tahoma")
        font1.setPointSize(10)
        self.username.setFont(font1)
        self.username.setReadOnly(False)
        self.username.setCursorMoveStyle(Qt.LogicalMoveStyle)
        self.username.setClearButtonEnabled(False)
        self.password = QLineEdit(Login)
        self.password.setObjectName(u"password")
        self.password.setGeometry(QRect(30, 90, 220, 40))
        self.password.setFont(font1)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setReadOnly(False)
        self.password.setCursorMoveStyle(Qt.LogicalMoveStyle)
        self.password.setClearButtonEnabled(False)
        self.LoginButton = QPushButton(Login)
        self.LoginButton.setObjectName(u"LoginButton")
        self.LoginButton.setGeometry(QRect(40, 190, 80, 40))
        self.LoginButton.setFont(font1)
        self.toRegister = QPushButton(Login)
        self.toRegister.setObjectName(u"toRegister")
        self.toRegister.setGeometry(QRect(160, 190, 80, 40))
        self.toRegister.setFont(font1)
        self.remember = QCheckBox(Login)
        self.remember.setObjectName(u"remember")
        self.remember.setGeometry(QRect(100, 150, 90, 20))
        self.textBrowser = QTextBrowser(Login)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(275, 30, 190, 200))
        QWidget.setTabOrder(self.username, self.password)
        QWidget.setTabOrder(self.password, self.remember)
        QWidget.setTabOrder(self.remember, self.LoginButton)
        QWidget.setTabOrder(self.LoginButton, self.toRegister)
        QWidget.setTabOrder(self.toRegister, self.textBrowser)

        self.retranslateUi(Login)

        QMetaObject.connectSlotsByName(Login)
    # setupUi

    def retranslateUi(self, Login):
        Login.setWindowTitle(QCoreApplication.translate("Login", u"\u767b\u5f55", None))
        self.username.setInputMask("")
        self.username.setText("")
        self.username.setPlaceholderText(QCoreApplication.translate("Login", u"\u7528\u6237\u540d", None))
        self.password.setInputMask("")
        self.password.setText("")
        self.password.setPlaceholderText(QCoreApplication.translate("Login", u"\u5bc6\u7801", None))
        self.LoginButton.setText(QCoreApplication.translate("Login", u"\u767b\u5f55", None))
        self.toRegister.setText(QCoreApplication.translate("Login", u"\u6ce8\u518c", None))
        self.remember.setText(QCoreApplication.translate("Login", u"\u8bb0\u4f4f\u5bc6\u7801", None))
    # retranslateUi

