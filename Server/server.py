import socket
import MySQLdb
import configparser
import ast
import datetime

config = configparser.ConfigParser()
config.read('config.ini')
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = config.get('network', 'ip')
port = int(config.get('network', 'port'))
serversocket.bind((host, port))
serversocket.listen(48)

def check_string(string):
   if len(string) == 0:
      return True
   else:
      return False

def login(username,password):
   if check_string(username) or check_string(password):
      return str({'mode':'login','status':'illegal'}).encode('utf-8')
   db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
   cursor = db.cursor()
   sql = "SELECT * FROM users WHERE username='%s' AND password='%s'" % (username, password)
   cursor.execute(sql)
   data = cursor.fetchone()
   db.close()
   if data:
      return str({'mode':'login','status':'success'}).encode('utf-8')
   else:
      return str({'mode':'login','status':'fail'}).encode('utf-8')

def checkinvitationcode(invitationcode):
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

def register(username,password,code):
   if check_string(username) or check_string(password) or check_string(code):
      return str({'mode':'register','status':'illegal'}).encode('utf-8')
   if checkinvitationcode(code):
      db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
      cursor = db.cursor()
      sql = "INSERT INTO `users` (`uid`, `username`, `password`) VALUES (NULL,'%s','%s')" % (username,password)
      try:
         cursor.execute(sql)
      except:
         return str({'mode':'register','status':'fail'}).encode('utf-8')
      db.close()
      return str({'mode':'register','status':'success'}).encode('utf-8')
   else:
      return str({'mode':'register','status':'errorinvitationcode'}).encode('utf-8')

def news():
   with open("news.html",'r',encoding='utf-8') as f:
      content = f.read()
   return str({'mode':'news','content':content}).encode('utf-8')

while True:
   clientsocket,addr = serversocket.accept()
   # "[",str(datetime.datetime.now())[:19],str(addr),"]",
   input = clientsocket.recv(1024).decode('utf-8')
   print("入站：",input)
   try:
      input = ast.literal_eval(input)
   except Exception as e:
      print("错误：",e)
      continue
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

