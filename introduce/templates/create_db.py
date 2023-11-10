import pymysql

mydb=pymysql.connect(host="127.0.0.1", user="xxxx", password="xxxxxx", charset="utf8")

print(mydb)

#my_cursor=mydb.cursor()

#my_cursor.execute("CREATE DATABASE users")

#my_cursor.execute("SHOW DATABASES")

#for db in my_cursor:
    #print(db)
