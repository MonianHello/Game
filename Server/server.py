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
import random

colorama.init()
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
host = config.get('network', 'ip')
port = int(config.get('network', 'port'))

def usersearchdata(username):
   try:
      lists = []

      db1 = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db')) 
      cursor1 = db1.cursor()
      cursor1.execute("SELECT uid FROM users WHERE username = %s", (username,))
      result1 = cursor1.fetchone()
      db1.commit()
      cursor1.close()
      db1.close()
      db2 = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db')) 
      cursor2 = db2.cursor()
      cursor2.execute("SELECT items FROM useritems WHERE uid = %s", (result1[0],))
      result2 = cursor2.fetchone()
      db2.commit()
      cursor2.close()
      db2.close()

      result3 = ast.literal_eval((result2[0]))
      mysqlsearch = result3

      for item in mysqlsearch:
         db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db')) 
         id_name_type_stars_count = []
         cursor = db.cursor()
         cursor.execute("SELECT name,type,stars FROM items WHERE id = %s", (item[0],))
         result = cursor.fetchone()
         id_name_type_stars_count.append(item[0])
         id_name_type_stars_count.append(result[0])
         id_name_type_stars_count.append(result[1])
         id_name_type_stars_count.append(result[2])
         id_name_type_stars_count.append(item[1])
         lists.append(id_name_type_stars_count)
         db.commit()
         cursor.close()
         db.close()
      return str({'mode':'usersearchdata','status':'success',"results":base64.b64encode(str(lists).encode('utf-8'))}).encode('utf-8')
   except Exception as e:
      print("\n"+colorama.Fore.RED + colorama.Back.WHITE + "  SERVER DATABASE ERROR  " + colorama.Fore.RESET + colorama.Back.RESET + "\n")
      print("?????????????????????????????????????????????????????????????????????")
      print(e , "\n")
      return str({'mode':'usersearchdata','status':'fail'}).encode('utf-8')
def mysqlgacha(uid,count):
   def gacha(uid,gachatimes):
      def get_random_name(items):

         # ????????????????????????????????????????????????????????????????????????

         # ??????random.random()????????????0???1????????????????????????????????????????????????
         # ??????????????????????????????????????????????????????????????????????????????????????????
         # ??????????????????????????????????????????????????????????????????????????????
         
         cumulative_probability = 0
         for item in items:
            cumulative_probability += item[1]
            item.append(cumulative_probability)
         random_number = random.random() * cumulative_probability
         for item in items:
            if random_number < item[2]:
               return item[0]
      # print("uid",uid,"??????",gachatimes,"??????")
      from collections import Counter
      def count_items(arr):
         count_dict = dict(Counter(arr))
         return [[key, value] for key, value in count_dict.items()]
      getitems = []
      property = ast.literal_eval(config.get('gacha', 'property'))
      for i in range(gachatimes):
         getitems.append(get_random_name(property))
      return count_items(getitems)
   import json
   db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
   cursor = db.cursor()
   cursor.execute("SELECT items FROM useritems WHERE uid = %s", (uid,))
   result = cursor.fetchone()
   if result is None:
      # print("No items found for the given UID")
      pass
   else:
      items = result[0]
      items = json.loads(items)
      item_1001_found = False
      item_1001_index = -1
      for i, item in enumerate(items):
         if item[0] == 1001:
               item_1001_found = True
               item_1001_index = i
               break
      if item_1001_found:
         if items[item_1001_index][1] >= count:
               gachaget = gacha(uid,count)
               items[item_1001_index][1] -= count
               cursor.execute("UPDATE useritems SET items = %s WHERE uid = %s", (json.dumps(items), uid))
               db.commit()
               # print("Gacha successful!")
         else:
               gachaget = []
               # print("Item quantity not sufficient")
      else:
         gachaget = []
         # print("Item not found")
   cursor.close()
   db.close()
   return gachaget

def get_items(star_list):
   # ???????????????
   db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
   cursor = db.cursor()
   # ?????????????????????????????????
   item_dict = {}
   # ???????????????????????????
   for star, count in star_list:
      # ??????????????????????????????
      query = "SELECT id, name, type FROM items WHERE stars = '{}'".format(star)
      cursor.execute(query)
      items = cursor.fetchall()
      # ???????????????????????????????????????
      for i in range(count):
         item = random.choice(items)
         item_id, name, item_type = item
         key = "{}_{}".format(star, name)
         if key not in item_dict:
               item_dict[key] = [item_id, name, item_type, 0]
         item_dict[key][3] += 1
   # ?????????????????????
   db.close()
   # ??????????????????????????????????????????
   id_name_type_count = list(item_dict.values()) # [1065, '????????????', '????????????', 32]
   id_count = [i[:1] + i[3:] for i in id_name_type_count] # [1065, 32]
   return id_name_type_count

def updateusersitem(uid,id_name_type_count,artificial = False):
   # artificial????????????????????????????????????
   if not artificial:
      items = [i[:1] + i[3:] for i in id_name_type_count] # [1065, 32]
   # ???????????????
   conn = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
   cursor = conn.cursor()
   # ?????????????????????????????????
   select_sql = "SELECT items FROM useritems WHERE uid = %s"
   cursor.execute(select_sql, (uid,))
   result = cursor.fetchone()
   if result:
      # ??????????????????????????????????????????
      old_items = eval(result[0])
      for item in items:
         item_found = False
         for i in range(len(old_items)):
               if old_items[i][0] == item[0]:
                  old_items[i][1] += item[1]
                  item_found = True
                  break
         if not item_found:
               old_items.append(item)
      update_sql = "UPDATE useritems SET items = %s WHERE uid = %s"
      cursor.execute(update_sql, (str(old_items), uid))
   else:
      # ?????????????????????????????????????????????
      insert_sql = "INSERT INTO useritems (uid, items) VALUES (%s, %s)"
      cursor.execute(insert_sql, (uid, str(items)))
   # ????????????
   conn.commit()
   # ????????????
   cursor.close()
   conn.close()

def maingacha(uid,count):
   output = []
   a = mysqlgacha(uid,count)
   output.append(a)
   b = get_items(a)
   updateusersitem(uid,b)
   print("??????",uid,"?????????",count,"???????????????????????????")
   if a == []:
      print("?????????????????????????????????????????????????????????")
   else:
      print("???????????????")
      for item in a:
         print("{}??????{}???".format(item[0], item[1]))
      print("???????????????")
      for item in b:
         db1 = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db')) 
         cursor1 = db1.cursor()
         cursor1.execute("SELECT stars FROM items WHERE id = %s", (item[0],))
         result1 = cursor1.fetchone()
         db1.commit()
         cursor1.close()
         db1.close()
         item.append(result1[0])
         print("{} {}({}) {}???".format(item[0], item[1],item[2], item[3]))
   output.append(b)
   return(output)

def servergacha(username,count):
   try:
      db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
      cursor = db.cursor()
      query = "SELECT uid FROM users WHERE username = '%s'" % (username)
      cursor.execute(query)
      uid = cursor.fetchall()[0][0]
      cursor.close()
      db.close()
      return str({'mode':'gacha','status':'success','results':maingacha(uid,count)}).encode('utf-8')
   except Exception as e:
      print("\n"+colorama.Fore.RED + colorama.Back.WHITE + "  SERVER DATABASE ERROR  " + colorama.Fore.RESET + colorama.Back.RESET + "\n")
      print("?????????????????????????????????????????????????????????????????????")
      print(e , "\n")
      return str({'mode':'gacha','status':'fail'}).encode('utf-8')

def searchchat(username):
   try:
      db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
      cursor = db.cursor()
      query = "SELECT datetime, sender, receiver, content FROM chat"
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
      print("?????????????????????????????????????????????????????????????????????")
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
      print("?????????????????????????????????????????????????????????????????????")
      print(e , "\n")
      return str({'mode':'insertchat','status':'fail'}).encode('utf-8')

def beep( times = 1 , duration = 500 , Hz = 1000 , breaks = 0.5 ):
   # times - ??????(???)
   # duration - ????????????(ms)
   # Hz - ???????????????(Hz)
   # breaks - ????????????(s)
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
      print("?????????????????????????????????????????????????????????")
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
      print("??????????????????????????????????????????????????????????????????")
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
      print("?????????????????????????????????????????????????????????")
      print(e , "\n")
      return str({'mode':'register','status':'fail'}).encode('utf-8')
   
def news():
   try:
      with open("news.html",'r',encoding='utf-8') as f:
         content = f.read()
      return str({'mode':'news','content':base64.b64encode(content.encode('utf-8'))}).encode('utf-8')
   except Exception as e:
      print("\n"+colorama.Fore.RED + colorama.Back.WHITE + "  SERVER NEWS ERROR  " + colorama.Fore.RESET + colorama.Back.RESET + "\n")
      print("???????????????????????????????????????????????????????????????")
      print(e , "\n")
      return str({'mode':'news','content':"?????????????????????"}).encode('utf-8')

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
      print("?????????????????????????????????????????????????????????????????????")
      print(e , "\n")
      return str({'mode':'checkpermission','status':'fail'}).encode('utf-8')

def main(clientsocket,addr):
   print()
   print("{}:{} ??????????????????".format(addr[0],addr[1]))
   # "[",str(datetime.datetime.now())[:19],str(addr),"]",
   input = clientsocket.recv(32768).decode('utf-8')
   print("?????????",input)
   try:
      input = ast.literal_eval(input)
   except Exception as e:
      print("\n"+colorama.Fore.RED + colorama.Back.WHITE + "  INBOUND CONTENT ERROR  " + colorama.Fore.RESET + colorama.Back.RESET + "\n")
      print("???????????????????????????????????????????????????????????????")
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
         print("insertchat:??????????????????",input["username"])
         print("insertchat:",output)
      else:
         output = str({'mode':'insertchat','status':'illegal'}).encode('utf-8')
         clientsocket.send(output)
         print("insertchat:??????????????????",input["username"])
         print("insertchat:",output)
   elif input["mode"] == "searchchat":
      if ast.literal_eval(login(input["username"],input["password"]).decode('utf-8'))["status"] == "success":
         output = searchchat(input["username"])
         clientsocket.send(output)
         print("searchchat:??????????????????",input["username"])
         print("searchchat:",output)
      else:
         output = str({'mode':'searchchat','status':'illegal'}).encode('utf-8')
         clientsocket.send(output)
         print("searchchat:??????????????????",input["username"])
         print("searchchat:",output)
   elif input["mode"] == "gacha":
      if ast.literal_eval(login(input["username"],input["password"]).decode('utf-8'))["status"] == "success":
         output = servergacha(input["username"],input["count"])
         clientsocket.send(output)
         print("gacha:??????????????????",input["username"])
         print("gacha:",output)
      else:
         output = str({'mode':'gacha','status':'illegal'}).encode('utf-8')
         clientsocket.send(output)
         print("gacha:??????????????????",input["username"])
         print("gacha:",output)
   elif input["mode"] == "usersearchdata":
      if ast.literal_eval(login(input["username"],input["password"]).decode('utf-8'))["status"] == "success":
         output = usersearchdata(input["username"])
         clientsocket.send(output)
         print("usersearchdata:??????????????????",input["username"])
         print("usersearchdata:",output)
      else:
         output = str({'mode':'usersearchdata','status':'illegal'}).encode('utf-8')
         clientsocket.send(output)
         print("usersearchdata:??????????????????",input["username"])
         print("usersearchdata:",output)
   clientsocket.close()

# ????????????threading.Thread(target=beep, args=(3,500,2000)).start()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

while True:
   sock,addr = server.accept() # ???????????????
   threading.Thread(target=main, args=(sock, addr)).start() # ???????????? 
