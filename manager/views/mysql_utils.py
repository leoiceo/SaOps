#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo

import MySQLdb

class db_operate:
    def mysql_command(self,conn,sql_cmd):
        try:
            ret = []
            conn=MySQLdb.connect(host=conn["host"],user=conn["user"],passwd=conn["password"],db=conn["database"],port=conn["port"],charset="utf8")
            cursor = conn.cursor()
            n = cursor.execute(sql_cmd)
            for row in cursor.fetchall():
                for i in row:
                    ret.append(i)
        except MySQLdb.Error,e:
            ret.append(e)

        return ret

    def select_table(self,conn,sql_cmd,parmas):
        try:
            ret = []
            conn=MySQLdb.connect(host=conn["host"],user=conn["user"],passwd=conn["password"],db=conn["database"],port=conn["port"],charset="utf8")
            cursor = conn.cursor()
            n = cursor.execute(sql_cmd,parmas)
            for row in cursor.fetchall():
                for i in row:
                    ret.append(i)
        except MySQLdb.Error,e:
            ret.append(e)

        return ret

if __name__ == "__main__":
    mydb = db_operate()
    mysql_conf= {"host": "127.0.0.1",
               "port": 3306,
               "database": "ycm",
               "user": "root",
               "password": "redhat"
                }
    sql = "show databases;"
    #sql = "create database py_mysql_test;"
    #ret = mydb.mysql_command(mysql_conf,sql)
    #print ret

    # ret = []
    # for i in range(1,100):
    #     sql = 'select id from table where uid="%s"'
    #     result = mydb.select_table(mysql_conf, sql, str(i))
    #     ret.append(result)
    # print ret