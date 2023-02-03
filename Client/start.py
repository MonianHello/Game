import configparser
import socket
from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader
import ast
from PySide2.QtWidgets import QMessageBox
import re
import hashlib

config = configparser.ConfigParser()
config.read('config.ini')

def getnews():
    global news
    json = {'mode':'news'}
    try :
        news = clientsocket(json)["content"]
    except:
        news = "无法连接到服务器"
    return news

def check_string(string):
   if len(string) == 0:
      return True
   else:
      return False

def clientsocket(json):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = config.get('network', 'ip')
    port = int(config.get('network', 'port'))
    try:
        clientsocket.connect((host, port))
    except:
        alert.netError()
        return 0   
    clientsocket.send(str(json).encode('utf-8'))
    output = ast.literal_eval(clientsocket.recv(1024).decode('utf-8'))
    print(output)
    clientsocket.close()
    return(output)

class loginPage:

    def __init__(self):
        self.ui = QUiLoader().load('login.ui')
        self.ui.textBrowser.setText(news)
        self.ui.LoginButton.clicked.connect(self.pushButton_clicked)
        self.ui.toRegister.clicked.connect(self.toRegister)
        if config["login"]["username"]:
            self.ui.remember.setChecked(True)
        self.ui.username.setText(config.get('login', 'username'))
        self.ui.password.setText(config.get('login', 'password'))

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
            if self.ui.remember.isChecked():
                with open('config.ini', 'w') as configfile:
                    config["login"]["username"]=username
                    config["login"]["password"]=password
                    config.write(configfile)
            else:
                with open('config.ini', 'w') as configfile:
                    config["login"]["username"]=""
                    config["login"]["password"]=""
                    config.write(configfile)
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

class alert:

    def registerFail():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("用户名已存在")
        msg.setWindowTitle("注册失败")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

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
        msg.setWindowTitle("登录失败")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def loginSuccess(username):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.NoIcon)
        msg.setText("用户 "+username+" 登录成功")
        msg.setWindowTitle("登录成功")
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