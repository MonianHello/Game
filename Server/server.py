# -*- coding: UTF-8 -*_
import socket
import MySQLdb
import configparser
import ast
import datetime
import hashlib
import time
import ctypes
import threading
import colorama
import base64

colorama.init()
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
host = config.get('network', 'ip')
port = int(config.get('network', 'port'))

def searchchat(username = "",time="2"):
   # username 用于判断私聊，time 用于判断范围
   try:
      db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
      cursor = db.cursor()
      timedifference = datetime.datetime.now() - datetime.timedelta(hours=int(time))
      query = "SELECT datetime, sender, receiver, content FROM chat WHERE datetime >= '%s'" % (timedifference)
      cursor.execute(query)
      results = list(cursor.fetchall())
      cursor.close()
      db.close()
      outputdata = []
      for result in results:
         outputdata.append(list(result))
      results = None
      for i in outputdata:
         i[0] = str(i[0])
      return str({'mode':'searchchat','status':'success','results':base64.b64encode(str(outputdata).encode('utf-8'))}).encode('utf-8')
   except Exception as e:
      print("\n"+colorama.Fore.RED + colorama.Back.WHITE + "  SERVER DATABASE ERROR  " + colorama.Fore.RESET + colorama.Back.RESET + "\n")
      print("用户尝试查询聊天信息时，服务器发生了以下错误：")
      print(e , "\n")
      return str({'mode':'searchchat','status':'fail'}).encode('utf-8')

def insertchat(sender,receiver,content):
   try:
      current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
      cursor = db.cursor()
      sql = "INSERT INTO `chat` (`datetime`, `sender`, `receiver`, `content`) VALUES ('%s', '%s', '%s', '%s')" % (current_time,sender,receiver,content)
      try:
         cursor.execute(sql)
      except:
         return str({'mode':'insertchat','status':'fail'}).encode('utf-8')
      db.close()
      return str({'mode':'insertchat','status':'success'}).encode('utf-8')
   except Exception as e:
      print("\n"+colorama.Fore.RED + colorama.Back.WHITE + "  SERVER DATABASE ERROR  " + colorama.Fore.RESET + colorama.Back.RESET + "\n")
      print("用户尝试插入聊天信息时，服务器发生了以下错误：")
      print(e , "\n")
      return str({'mode':'insertchat','status':'fail'}).encode('utf-8')

def beep( times = 1 , duration = 500 , Hz = 1000 , breaks = 0.5 ):
   # times - 次数(次)
   # duration - 持续时间(ms)
   # Hz - 蜂鸣器频率(Hz)
   # breaks - 间隔时间(s)
   player = ctypes.windll.kernel32
   for _ in range(times):
      player.Beep(Hz,duration)
      time.sleep(breaks)

def check_string(string):
   if len(string) == 0:
      return True
   else:
      return False

def login(username,password):
   try:
      if check_string(username) or check_string(password):
         return str({'mode':'login','status':'illegal'}).encode('utf-8')
      db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
      cursor = db.cursor()
      sql = "SELECT * FROM users WHERE username=%s AND password=%s"
      cursor.execute(sql, (username, hashlib.sha256(password.encode('utf-8')).hexdigest()))
      data = cursor.fetchone()
      db.close()
      if data:
         return str({'mode':'login','status':'success'}).encode('utf-8')
      else:
         return str({'mode':'login','status':'fail'}).encode('utf-8')
   except Exception as e:
      print("\n"+colorama.Fore.RED + colorama.Back.WHITE + "  SERVER DATABASE ERROR  " + colorama.Fore.RESET + colorama.Back.RESET + "\n")
      print("用户尝试登录时，服务器发生了以下错误：")
      print(e , "\n")
      return str({'mode':'login','status':'illegal'}).encode('utf-8')

def checkinvitationcode(invitationcode):
   try:
      db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
      cursor = db.cursor()
      sql = "SELECT * FROM invitationcode WHERE code = '%s'" % (invitationcode)
      cursor.execute(sql)
      results = cursor.fetchall()
      if results:
         sql = "DELETE FROM invitationcode WHERE code = '%s'" % (invitationcode)
         cursor.execute(sql)
         db.commit()
         db.close()
         return True
      else:
         db.close()
         return False
   except Exception as e:
      print("\n"+colorama.Fore.RED + colorama.Back.WHITE + "  SERVER DATABASE ERROR  " + colorama.Fore.RESET + colorama.Back.RESET + "\n")
      print("查询邀请码是否有效时，服务器发生了以下错误：")
      print(e , "\n")
      return False

def register(username,password,code):
   try:
      if check_string(username) or check_string(password) or check_string(code):
         return str({'mode':'register','status':'illegal'}).encode('utf-8')
      if checkinvitationcode(code):
         db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
         cursor = db.cursor()
         sql = "INSERT INTO `users` (`uid`, `username`, `password`) VALUES (NULL,'%s','%s')" % (username,hashlib.sha256(password.encode('utf-8')).hexdigest())
         try:
            cursor.execute(sql)
         except:
            return str({'mode':'register','status':'fail'}).encode('utf-8')
         db.close()
         return str({'mode':'register','status':'success'}).encode('utf-8')
      else:
         return str({'mode':'register','status':'errorinvitationcode'}).encode('utf-8')
   except Exception as e:
      print("\n"+colorama.Fore.RED + colorama.Back.WHITE + "  SERVER DATABASE ERROR  " + colorama.Fore.RESET + colorama.Back.RESET + "\n")
      print("用户尝试注册时，服务器发生了以下错误：")
      print(e , "\n")
      return str({'mode':'register','status':'fail'}).encode('utf-8')
   
def news():
   try:
      with open("news.html",'r',encoding='utf-8') as f:
         content = f.read()
      return str({'mode':'news','content':base64.b64encode(content.encode('utf-8'))}).encode('utf-8')
   except Exception as e:
      print("\n"+colorama.Fore.RED + colorama.Back.WHITE + "  SERVER NEWS ERROR  " + colorama.Fore.RESET + colorama.Back.RESET + "\n")
      print("用户尝试获取新闻时，服务器发生了以下错误：")
      print(e , "\n")
      return str({'mode':'news','content':"服务器内部故障"}).encode('utf-8')

def checkpermission(username):
   try:
      if check_string(username):
         return str({'mode':'checkpermission','status':'illegal'}).encode('utf-8')
      db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
      cursor = db.cursor()
      query = "SELECT permission FROM users WHERE username='{}'".format(username)
      cursor.execute(query)
      result = cursor.fetchone()
      if result is None:
         return str({'mode':'checkpermission','status':'fail'}).encode('utf-8')
      cursor.close()
      db.close()
      return str({'mode':'checkpermission','status':'success','permission':result[0]}).encode('utf-8')
   except Exception as e:
      print("\n"+colorama.Fore.RED + colorama.Back.WHITE + "  SERVER DATABASE ERROR  " + colorama.Fore.RESET + colorama.Back.RESET + "\n")
      print("用户尝试查询用户权限时，服务器发生了以下错误：")
      print(e , "\n")
      return str({'mode':'checkpermission','status':'fail'}).encode('utf-8')

def main(clientsocket,addr):
   print()
   print("{}:{} 连接到服务器".format(addr[0],addr[1]))
   # "[",str(datetime.datetime.now())[:19],str(addr),"]",
   input = clientsocket.recv(32768).decode('utf-8')
   print("入站：",input)
   try:
      input = ast.literal_eval(input)
   except Exception as e:
      print("\n"+colorama.Fore.RED + colorama.Back.WHITE + "  INBOUND CONTENT ERROR  " + colorama.Fore.RESET + colorama.Back.RESET + "\n")
      print("尝试处理入站信息时，服务器发生了以下错误：")
      print(e , "\n")
   if input["mode"] == 'login':
      output = login(input["username"],input["password"])
      clientsocket.send(output)
      print("login:",output)
   elif input["mode"] == "register":
      output = register(input["username"],input["password"],input["invitationcode"])
      clientsocket.send(output)
      print("register:",output)
   elif input["mode"] == "news":
      output = news()
      clientsocket.send(output)
      print("news:",output)
   elif input["mode"] == "checkpermission":
      output = checkpermission(input["username"])
      clientsocket.send(output)
      print("checkpermission:",output)
   elif input["mode"] == "insertchat":
      if ast.literal_eval(login(input["username"],input["password"]).decode('utf-8'))["status"] == "success":
         output = insertchat(input["username"],input["receiver"],input["content"])
         clientsocket.send(output)
         print("insertchat:账户校验通过",input["username"])
         print("insertchat:",output)
      else:
         output = str({'mode':'insertchat','status':'illegal'}).encode('utf-8')
         clientsocket.send(output)
         print("insertchat:账户校验失败",input["username"])
         print("insertchat:",output)
   elif input["mode"] == "searchchat":
      if ast.literal_eval(login(input["username"],input["password"]).decode('utf-8'))["status"] == "success":
         output = searchchat(input["username"],input["time"])
         clientsocket.send(output)
         print("searchchat:账户校验通过",input["username"])
         print("searchchat:",output)
      else:
         output = str({'mode':'searchchat','status':'illegal'}).encode('utf-8')
         clientsocket.send(output)
         print("searchchat:账户校验失败",input["username"])
         print("searchchat:",output)
   clientsocket.close()

# 多线程：threading.Thread(target=beep, args=(3,500,2000)).start()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

while True:
   sock,addr = server.accept() # 阻塞式连接
   threading.Thread(target=main, args=(sock, addr)).start() # 启动线程 
