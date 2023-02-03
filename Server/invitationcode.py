import random
import MySQLdb
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

db = MySQLdb.connect(host=config.get('network', 'ip'), user=config.get('mysql', 'name'), passwd=config.get('mysql', 'password'),db=config.get('mysql', 'db'))
cursor = db.cursor()

def generate_string():
    string = 'MONIAN'
    for _ in range(14):
        string += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    string = string[0:6] + '-' + string[6:10] + '-' + string[10:14] + '-' + string[14:]
    return string

print("="*24)
print('''
邀请码格式：MONIAN-XXXX-XXXX-XXXXXX

1、从数据库中下载邀请码
2、生成邀请码并存入数据库
3、清除所有邀请码
''')
print("="*24)

choice = int(input("请选择："))

if choice == 1:
    print("="*20)
    cursor.execute("SELECT * FROM invitationcode")
    results = cursor.fetchall()
    f = open('invitationcode.txt', 'w')
    for row in results:
        print(str(row[0]))
        f.write(str(row[0])+'\n')
    f.close()
    db.close()
    print("="*20)

elif choice == 2:

    times = input("本次要生成邀请码的数量：")
    print("="*20)
    for i in range(int(times)):
        code = generate_string()
        print(code)
        with open('invitationcode.txt', 'a') as f:
            f.write(code+'\n')
        sql = "INSERT INTO `invitationcode` (`code`) VALUES ('%s')" % (code)
        cursor.execute(sql)
    db.close()
    print("="*20)
    print("操作已完成")

elif choice == 3:
    print("="*20)
    with open('invitationcode.txt', 'w') as f:
        f.write('')
    cursor.execute("TRUNCATE `game`.`invitationcode`")
    db.close()
    print("操作已完成")
    print("="*20)