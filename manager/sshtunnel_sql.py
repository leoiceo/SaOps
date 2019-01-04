#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo

import MySQLdb
from sshtunnel import SSHTunnelForwarder
import MySQLdb.cursors


def dbconnect_ssh(ssh_host,ssh_port,keyfile,ssh_user,db_host,db_name,sql,db_port,db_user,db_passwd):
    with SSHTunnelForwarder(
            (ssh_host, ssh_port),
            #ssh_password="sshpasswd",
            ssh_pkey=keyfile,
            ssh_username=ssh_user,
            remote_bind_address=(db_host, db_port)
    ) as server:

        db = MySQLdb.connect(
            host='127.0.0.1',
            port=server.local_bind_port,
            user=db_user,
            passwd=db_passwd,
            db=db_name,
            charset="utf8",
            cursorclass=MySQLdb.cursors.DictCursor)

        cursor = db.cursor()

        try:
            cursor.execute(sql)
            data = cursor.fetchall()
            db.commit()
        except:
            db.rollback()

        collect = []
        for result in data:
            collect.append(result)

        db.close()
        cursor.close()

        return collect


def dbconnect(db_host,db_name,cmd,port,db_user,db_passwd):

    try:
        db = MySQLdb.connect(host="%s"%db_host,port=port,user=db_user,passwd=db_passwd,db="%s"%db_name,charset="utf8",cursorclass = MySQLdb.cursors.DictCursor)
        cursor = db.cursor()
    except Exception,e:
        print "db connect failed: %s" % e

    sql = "%s"%cmd
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        db.commit()
    except:
        db.rollback()

    collect = []

    for result in data:
        collect.append(result)

    db.close()
    cursor.close()

    return collect