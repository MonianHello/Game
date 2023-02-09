# -*- coding: UTF-8 -*_
import configparser
import socket
from PySide2.QtWidgets import QApplication,QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QTextCursor
from PySide2.QtCore import QThread, Signal
import ast
import os
import hashlib
import base64
import time

intervalCounter = 12

# Initialize configuration file
try:
    with open("config.ini", "r", encoding='utf-8') as file:
        pass
except FileNotFoundError:
    with open("config.ini", "w", encoding='utf-8') as file:
        file.write('''[network]\nip = 127.0.0.1\nport = 7711\n\n[login]\nusername = \npassword = \n''')

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

def getnews():
    global news
    json = {'mode':'news'}
    try :
        news = base64.b64decode(clientsocket(json)["content"]).decode('utf-8')
    except:
        news = "无法连接到服务器"
    return news

def check_string(string):
   if len(string) == 0:
      return True
   else:
      return False

def clientsocket(jsons):
    
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        host = config.get('network', 'ip')
        port = int(config.get('network', 'port'))
    except:
        alert.configError()
        return 0   
    try:
        clientsocket.connect((host, port))
    except:
        alert.netError()
        return 0   
    clientsocket.send(str(jsons).encode('utf-8'))
    output = ast.literal_eval(clientsocket.recv(32768).decode('utf-8'))
    # output = json.loads(clientsocket.recv(32768).decode('utf-8'))
    print(output)
    clientsocket.close()
    return(output)

class autoRefreshChatThread(QThread):
    autoRefreshChat_signal = Signal(str)

    def __init__(self):
        QThread.__init__(self)

    def run(self):
        autoChatMessages = ""
        while True:
            autoChatMessages = str(mainPage.searchChat(mainPage,username,password,intervalCounter))
            self.autoRefreshChat_signal.emit(str(autoChatMessages))
            time.sleep(5)

class loginPage:

    def __init__(self):

        self.ui = QUiLoader().load('login.ui')
        self.ui.textBrowser.setText(news)
        self.ui.LoginButton.clicked.connect(self.pushButton_clicked)
        self.ui.toRegister.clicked.connect(self.toRegister)
        self.ui.remember.clicked.connect(self.rememberChecked)
        if config["login"]["username"]:
            self.ui.remember.setChecked(True)
        try:
            self.ui.username.setText(config.get('login', 'username'))
            self.ui.password.setText(config.get('login', 'password'))
        except:
            alert.configError()
            return 0
        
    def rememberChecked(self):
        global username,password
        username = self.ui.username.text()
        password = self.ui.password.text()
        if self.ui.remember.isChecked():
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config["login"]["username"]=username
                config["login"]["password"]=password
                config.write(configfile)
        else:
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config["login"]["username"]=""
                config["login"]["password"]=""
                config.write(configfile)

    def toRegister(self):
        global register
        register = registerPage()
        register.ui.show()
        self.ui.close()

    def pushButton_clicked(self):
        global username,password,main
        username = self.ui.username.text()
        password = self.ui.password.text()
        if check_string(username) or check_string(password):
            alert.illegal()
            return 0
        json = {'mode':'login','username':username,'password':hashlib.sha256(password.encode('utf-8')).hexdigest()}
        output = clientsocket(json)
        if output["status"] == "success":
            alert.loginSuccess(username)
            loginPage.rememberChecked(self)
            main = mainPage()
            main.ui.show()
            login.ui.close()
        elif output["status"] == "fail":
            alert.loginFail()
        elif output["status"] == "illegal":
            alert.illegal()

class registerPage:
     
    def __init__(self):
        self.ui = QUiLoader().load('register.ui')
        self.ui.textBrowser.setText(news)
        self.ui.RegisterButton.clicked.connect(self.pushButton_clicked)
        self.ui.BackButton.clicked.connect(self.back)

    def back(self):
        global login
        login = loginPage()
        login.ui.show()
        self.ui.close()

    def pushButton_clicked(self):
        global username,password,main,login
        username = self.ui.username.text()
        password = self.ui.password.text()
        invitationcode = self.ui.invitationcode.text()
        if check_string(username) or check_string(password) or check_string(invitationcode):
            alert.illegal()
            return 0
        json = {'mode':'register','username':username,'password':hashlib.sha256(password.encode('utf-8')).hexdigest(),'invitationcode':invitationcode}
        output = clientsocket(json)
        if output["status"] == "success":
            alert.registerSuccess(username)
            login = loginPage()
            login.ui.show()
            register.ui.close()
        elif output["status"] == "fail":
            alert.registerFail()
        elif output["status"] == "illegal":
            alert.illegal()
        elif output["status"] == "errorinvitationcode":
            alert.errorinvitationcode()

class mainPage:

    def __init__(self):
        self.ui = QUiLoader().load('main.ui')
        self.ui.usernamelabel.setText(username)
        mainPage.checkpermission(username)
        self.ui.permissionlabel.setText(userpermission)
        self.ui.sendButton.clicked.connect(self.send)
        self.ui.refreshChatButton.clicked.connect(self.refreshChat)
        self.autoRefreshChat_thread = autoRefreshChatThread()
        self.autoRefreshChat_thread.autoRefreshChat_signal.connect(self.updateChatMessages)
        self.autoRefreshChat_thread.start()

    def updateChatMessages(self, autoChatMessages):
        self.ui.chatmessages.setHtml(autoChatMessages)
        cursor = self.ui.chatmessages.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.ui.chatmessages.setTextCursor(cursor)

    def searchChat(self,username,password,time):
        json = {'mode':'searchchat','username':username,'password':hashlib.sha256(password.encode('utf-8')).hexdigest(),'time':time}
        output = clientsocket(json)
        if output["status"] == "success":
            chatmessages = ast.literal_eval(base64.b64decode(output["results"]).decode('utf-8'))
            outputmessages = ""
            for result in chatmessages:
                datetime = result[0]
                sender = result[1]
                receiver = result[2]
                content = result[3]
                # formatted_result = '<font color="#FF0000">{}</font> {} : {}'.format(datetime, sender, content)
                formatted_result = '<font color="#FF0000">{}</font>: {}'.format(sender, content)
                outputmessages += (formatted_result + "<br>")
            return outputmessages
        elif output["status"] == "fail":
            alert.illegal()
            return ""

    def refreshChat(self):
        self.ui.chatmessages.setHtml(self.searchChat(username,password,intervalCounter))
        cursor = self.ui.chatmessages.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.ui.chatmessages.setTextCursor(cursor)

    def send(self):
        message = self.ui.sendmessage.toPlainText()
        if message == "":
            return 0
        mainPage.insertchat("",message)
        self.ui.sendmessage.clear()
        self.refreshChat()

    def insertchat(receiver = "",content = ""):
        json = {'mode':'insertchat','username':username,'password':hashlib.sha256(password.encode('utf-8')).hexdigest(),'receiver':receiver,'content':content}
        output = clientsocket(json)
        if output["status"] == "success":
            pass
        elif output["status"] == "fail":
            alert.illegal()
        elif output["status"] == "illegal":
            alert.illegal()

    def checkpermission(username):
        global userpermission
        try:
            json = {'mode':'checkpermission','username':username}
            output = clientsocket(json)
            if output["status"] == "success":
                userpermission = output["permission"]
            else:
                userpermission = ""
        except:
            userpermission = ""

class alert:

    def registerFail():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("用户名已存在")
        msg.setWindowTitle("注册失败")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def configError():
        os.remove("config.ini")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("config.ini错误，请重启程序")
        msg.setWindowTitle("配置文件错误")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        exit(1)

    def registerSuccess(username):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.NoIcon)
        msg.setText("用户 "+username+" 注册成功")
        msg.setWindowTitle("注册成功")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def loginFail():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("用户名或密码错误")
        msg.setWindowTitle("校验失败")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def loginSuccess(username):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.NoIcon)
        msg.setText("用户 "+username+" 登录成功")
        msg.setWindowTitle("校验成功")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def illegal():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("非法操作")
        msg.setWindowTitle("非法操作")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def netError():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("无法连接到服务器")
        msg.setWindowTitle("连接失败")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def errorinvitationcode():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("此邀请码无效或已被使用")
        msg.setWindowTitle("验证失败")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

if __name__ == '__main__':
    app = QApplication([])
    getnews()
    login = loginPage()
    login.ui.show()
    app.exec_()