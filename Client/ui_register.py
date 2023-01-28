# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'register.ui'
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
        Login.setCursor(QCursor(Qt.ArrowCursor))
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
        self.RegisterButton = QPushButton(Login)
        self.RegisterButton.setObjectName(u"RegisterButton")
        self.RegisterButton.setEnabled(True)
        self.RegisterButton.setGeometry(QRect(40, 200, 80, 40))
        self.RegisterButton.setFont(font1)
        self.RegisterButton.setAcceptDrops(False)
        self.RegisterButton.setCheckable(False)
        self.email = QLineEdit(Login)
        self.email.setObjectName(u"email")
        self.email.setGeometry(QRect(30, 150, 220, 40))
        self.email.setFont(font1)
        self.email.setEchoMode(QLineEdit.Normal)
        self.email.setReadOnly(False)
        self.email.setCursorMoveStyle(Qt.LogicalMoveStyle)
        self.email.setClearButtonEnabled(False)
        self.textBrowser = QTextBrowser(Login)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(275, 30, 190, 200))
        self.BackButton = QPushButton(Login)
        self.BackButton.setObjectName(u"BackButton")
        self.BackButton.setGeometry(QRect(160, 200, 80, 40))
        self.BackButton.setFont(font1)
        QWidget.setTabOrder(self.username, self.password)
        QWidget.setTabOrder(self.password, self.email)
        QWidget.setTabOrder(self.email, self.RegisterButton)
        QWidget.setTabOrder(self.RegisterButton, self.BackButton)
        QWidget.setTabOrder(self.BackButton, self.textBrowser)

        self.retranslateUi(Login)

        QMetaObject.connectSlotsByName(Login)
    # setupUi

    def retranslateUi(self, Login):
        Login.setWindowTitle(QCoreApplication.translate("Login", u"\u6ce8\u518c", None))
        self.username.setInputMask("")
        self.username.setText("")
        self.username.setPlaceholderText(QCoreApplication.translate("Login", u"\u7528\u6237\u540d", None))
        self.password.setInputMask("")
        self.password.setText("")
        self.password.setPlaceholderText(QCoreApplication.translate("Login", u"\u5bc6\u7801", None))
        self.RegisterButton.setText(QCoreApplication.translate("Login", u"\u63d0\u4ea4", None))
        self.email.setInputMask("")
        self.email.setText("")
        self.email.setPlaceholderText(QCoreApplication.translate("Login", u"\u90ae\u7bb1", None))
        self.BackButton.setText(QCoreApplication.translate("Login", u"\u8fd4\u56de", None))
    # retranslateUi

