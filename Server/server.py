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

colorama.init()
# 多线程：threading.Thread(target=beep, args=(3,500,2000)).start()

config = configparser.ConfigParser()
config.read('config.ini')
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = config.get('network', 'ip')
port = int(config.get('network', 'port'))
serversocket.bind((host, port))
serversocket.listen(48)

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
      sql = "SELECT * FROM users WHERE username='%s' AND password='%s'" % (username, hashlib.sha256(password.encode('utf-8')).hexdigest())
      cursor.execute(sql)
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
      return str({'mode':'news','content':content}).encode('utf-8')
   except Exception as e:
      print("\n"+colorama.Fore.RED + colorama.Back.WHITE + "  SERVER NEWS ERROR  " + colorama.Fore.RESET + colorama.Back.RESET + "\n")
      print("用户尝试获取新闻时，服务器发生了以下错误：")
      print(e , "\n")
      return str({'mode':'news','content':"服务器内部故障"}).encode('utf-8')

def main():
   while True:
      clientsocket,addr = serversocket.accept()
      # "[",str(datetime.datetime.now())[:19],str(addr),"]",
      input = clientsocket.recv(1024).decode('utf-8')
      print("入站：",input)
      try:
         input = ast.literal_eval(input)
      except Exception as e:
         print("\n"+colorama.Fore.RED + colorama.Back.WHITE + "  INBOUND CONTENT ERROR  " + colorama.Fore.RESET + colorama.Back.RESET + "\n")
         print("尝试处理入站信息时，服务器发生了以下错误（入站信息非法）：")
         print(e , "\n")
      if input["mode"] == 'login':
         output = login(input["username"],input["password"])
         clientsocket.send(output)
         print("出站：",output)
      elif input["mode"] == "register":
         output = register(input["username"],input["password"],input["invitationcode"])
         clientsocket.send(output)
         print("出站：",output)
      elif input["mode"] == "news":
         output = news()
         clientsocket.send(output)
         print("出站：",output)
      clientsocket.close()


main()