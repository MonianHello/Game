import socket
# import datetime
import MySQLdb
import configparser
import ast
import re
import base64

config = configparser.ConfigParser()
config.read('config.ini')
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = config.get('network', 'ip')
port = int(config.get('network', 'port'))
serversocket.bind((host, port))
serversocket.listen(48)

def check_string(string):
   pattern = re.compile('[^a-zA-Z0-9@.]')
   if pattern.search(string):
      return True
   elif len(string) == 0:
      return True
   else:
      return False

def login(username,password):
   if check_string(username) or check_string(password):
      print(str({'mode':'login','status':'illegal'}).encode('utf-8'))
      return str({'mode':'login','status':'illegal'}).encode('utf-8')
   db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
   cursor = db.cursor()
   sql = "SELECT * FROM users WHERE username='%s' AND password='%s'" % (username, password)
   cursor.execute(sql)
   data = cursor.fetchone()
   db.close()
   if data:
      print(str({'mode':'login','status':'success'}).encode('utf-8'))
      return str({'mode':'login','status':'success'}).encode('utf-8')
   else:
      print(str({'mode':'login','status':'fail'}).encode('utf-8'))
      return str({'mode':'login','status':'fail'}).encode('utf-8')


def register(username,password,email):
   if check_string(username) or check_string(password) or check_string(email):
      print(str({'mode':'register','status':'illegal'}).encode('utf-8'))
      return str({'mode':'register','status':'illegal'}).encode('utf-8')
   db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
   cursor = db.cursor()
   sql = "INSERT INTO `users` (`uid`, `username`, `password`, `email`) VALUES (NULL,'%s','%s','%s')" % (username, password,email)
   try:
      cursor.execute(sql)
   except:
      print(str({'mode':'register','status':'fail'}).encode('utf-8'))
      return str({'mode':'register','status':'fail'}).encode('utf-8')
   db.close()
   print(str({'mode':'register','status':'success'}).encode('utf-8'))
   return str({'mode':'register','status':'success'}).encode('utf-8')

def news():
   with open("news.html",'r',encoding='utf-8') as f:
      content = f.read()
   print(str({'mode':'news','content':content}).encode('utf-8'))
   return str({'mode':'news','content':content}).encode('utf-8')

while True:
# 建立客户端连接
   clientsocket,addr = serversocket.accept()
   print("%s 已连接到服务器" % str(addr))
   # msg="\r\n"
   # "[",str(datetime.datetime.now())[:19],"]",
   input = clientsocket.recv(1024).decode('utf-8')
   print(input)
   try:
      input = ast.literal_eval(input)
   except Exception as e:
      print("ERROR:",e)
      continue
   print(input)
   if input["mode"] == 'login':
      clientsocket.send(login(input["username"],input["password"]))
   elif input["mode"] == "register":
      clientsocket.send(register(input["username"],input["password"],input["email"]))
   elif input["mode"] == "news":
      clientsocket.send(news())
   clientsocket.close()

