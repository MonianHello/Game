# -*- coding: UTF-8 -*_
import configparser
import socket
from PySide2.QtWidgets import QApplication,QMessageBox,QTableWidget, QTableWidgetItem
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QTextCursor
from PySide2.QtCore import QThread, Signal
import ast
import os
import hashlib
import base64
import time
from datetime import datetime

autoUpdateFrequency = 5

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
    stop_signal = Signal()
    autoRefreshChat_signal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stop_requested = False

    def run(self):
        global autoUpdateFrequency
        while not self.stop_requested:
            autoChatMessages = str(mainPage.searchChat(mainPage,username,password))
            self.autoRefreshChat_signal.emit(str(autoChatMessages))
            time.sleep(autoUpdateFrequency)
        self.stop_signal.emit()

    def stop(self):
        self.stop_requested = True


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

    isAutoRefreshChat = True

    def __init__(self):
        self.ui = QUiLoader().load('main.ui')
        self.ui.usernamelabel.setText(username)
        mainPage.checkpermission(username)
        self.ui.permissionlabel.setText(userpermission)
        self.ui.sendButton.clicked.connect(self.send)
        self.ui.autoRefreshChatButton.clicked.connect(self.isAutoRefreshChatButton)
        self.ui.refreshChatButton.clicked.connect(self.refreshChat)
        self.ui.autoUpdateFrequencySpinBox.valueChanged.connect(self.handleValueChange)
        
        self.ui.gacha1Button.clicked.connect(lambda:self.gacha(1))
        self.ui.gacha10Button.clicked.connect(lambda:self.gacha(10))
        self.ui.gacha100Button.clicked.connect(lambda:self.gacha(100))
        self.ui.gacha1000Button.clicked.connect(lambda:self.gacha(1000))
        self.ui.gacha10000Button.clicked.connect(lambda:self.gacha(10000))


        # if userpermission == "admin":
        #     pass
        # else:
        #     self.ui.tabWidget.removeTab(1)
            
        self.thread = autoRefreshChatThread()
        self.thread.stop_signal.connect(self.thread.quit)
        self.thread.autoRefreshChat_signal.connect(self.updateChatMessages)
        self.thread.start()

    def gacha(self,count):
        json = {'mode':'gacha','username':username,'password':hashlib.sha256(password.encode('utf-8')).hexdigest(),'count':count}
        output = clientsocket(json)
        self.ui.gachaReturnTextBrowser.setHtml(str(output))

    def handleValueChange(self, value):
        global autoUpdateFrequency
        autoUpdateFrequency = value
    
    def isAutoRefreshChatButton(self):
        if self.isAutoRefreshChat:
            self.ui.autoRefreshChatButton.setText("启用自动刷新")
            self.thread.stop()
            self.isAutoRefreshChat = False
        else:
            self.ui.autoRefreshChatButton.setText("禁用自动刷新")
            self.thread = autoRefreshChatThread()
            self.thread.stop_signal.connect(self.thread.quit)
            self.thread.autoRefreshChat_signal.connect(self.updateChatMessages)
            self.thread.start()
            self.isAutoRefreshChat = True

    def updateChatMessages(self, autoChatMessages):
        self.ui.chatmessages.setHtml(autoChatMessages)
        cursor = self.ui.chatmessages.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.ui.chatmessages.setTextCursor(cursor)

    def searchChat(self,username,password):
        json = {'mode':'searchchat','username':username,'password':hashlib.sha256(password.encode('utf-8')).hexdigest()}
        output = clientsocket(json)
        if output["status"] == "success":
            messages = ast.literal_eval(base64.b64decode(output["results"]).decode('utf-8'))
            outputmessages = ""
            def get_day_of_message(date_str):
                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                # now = datetime.now()
                now = datetime.combine(datetime.now().date(), datetime.max.time())
                delta = now - date
                if delta.days == 0:
                    return "今天"
                elif delta.days == 1:
                    return "昨天"
                elif delta.days == 2:
                    return "前天"
                else:
                    return date.strftime("%Y年%m月%d日")
            day_of_messages = {}
            for message in messages:
                day = get_day_of_message(message[0])
                if day not in day_of_messages:
                    day_of_messages[day] = []
                day_of_messages[day].append(message)

            for day, messages in day_of_messages.items():
                formatted_result = '<font color="#FF0000">{}</font>'.format(day)
                outputmessages += (formatted_result + "<br>")
                for message in messages:
                    datetimes, sender, receiver, content = message
                    datetimes = datetime.strptime(datetimes,'%Y-%m-%d %H:%M:%S').strftime('%H:%M')
                    formatted_result = '<font color="#8b9999">[{}]</font> <font color="#008080">{}</font>:<font color="#000000"> {}</font>'.format(datetimes, sender, content)
                    outputmessages += (formatted_result + "<br>")
            return outputmessages
        elif output["status"] == "fail":
            alert.illegal()
            return ""

    def refreshChat(self):
        self.ui.chatmessages.setHtml(self.searchChat(username,password))
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