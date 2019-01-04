#!/usr/bin/env python
#-*-coding:utf-8-*-

import MySQLdb.cursors
import threading
import Queue
import time
import socket
import json
import base64
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import StringIO  
import pycurl  
import sys  
import os  
import json

class Http_Test:  
    def __init__(self):
        self.contents = ''
    def body_callback(self,buf):
        self.contents = self.contents + buf

def Check_Url(input_url):  
    t = Http_Test()
    c = pycurl.Curl()
    c.setopt(pycurl.WRITEFUNCTION,t.body_callback)
    c.setopt(pycurl.ENCODING, 'gzip')
    c.setopt(pycurl.URL,input_url)
    c.perform()
    http_code = c.getinfo(pycurl.HTTP_CODE)
    
    return http_code

class mythread(threading.Thread):
    def __init__(self,func,args):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
    def run(self):
        apply(self.func,self.args)


#数据库操作函数
def dbconnect(host,port,user,passwd,db,cmd):
    db = MySQLdb.connect(host="%s"%host,port=port,user="%s"%user,passwd="%s"%passwd,db="%s"%db,charset="utf8",cursorclass = MySQLdb.cursors.DictCursor)
    cursor = db.cursor()
    sql = "%s"%cmd
    cursor.execute(sql)
    data = cursor.fetchall()
    db.commit()

    collect = []
    for result in data:
        collect.append(result)
    return collect
    db.close()

def daemonize(stdin='/dev/null',stdout='/dev/null',stderr='/dev/null'):
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError,e:
        sys.stderr.write("fork #1 failed:(%d) %s\n"%(e.errno,e.strerror))
        sys.exit(1)

    os.chdir("/")
    os.umask(0)
    os.setsid()
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError,e:
        sys.stderr.write("fork #2 failed:(%d) %s\n"%(e.errno,e.strerror))
        sys.exit(1)
    for f in sys.stdout,sys.stderr:f.flush()
    si = file(stdin,'r')
    so = file(stdout,'a+')
    se = file(stderr,'a+',0)
    os.dup2(si.fileno(),sys.stdin.fileno())
    os.dup2(so.fileno(),sys.stdout.fileno())
    os.dup2(se.fileno(),sys.stderr.fileno())

def sql_exec(server_data):
    check_time = time.strftime("%Y-%m-%d %H:%M:%S")
    domain = server_data["domain"]
    web_status = server_data["status"]
    cmd = "update multitask_website set status = %d,check_time = '%s' where domain = '%s';"%(web_status,check_time,domain)
    print cmd
    dbconnect(host,port,user,passwd,dbname,cmd)

def worker():
    while True:
        if tasks.empty():
            break
        task = tasks.get(timeout=1)
        server_data = {}
        domain = task['domain']
        server_data.setdefault("domain",domain)
        http_code = Check_Url(domain)
        print http_code
        if http_code in [200,301]:
            server_data.setdefault("status",1)
        else:
            server_data.setdefault("status",0)

        sql_exec(server_data)

def check_exec():
    #查询所有游戏服
    #print os.getpid()
    #sys.stdout.write('daemon started with pid %d\n'%os.getpid())
    pid = os.getpid()
    with open(process_pid,"w") as f:
        f.write("%d"%pid)
    cmd = "select * from multitask_website;"
    data_result = dbconnect(host,port,user,passwd,dbname,cmd)
    for result in data_result:
        tasks.put(result)
        if tasks.qsize() > 1:
            mythread(worker,()).start()

def main():
    while 1:
        sys.stdout.flush()
        check_exec()
        sleep_time = 120
        time.sleep(sleep_time)

if __name__ == '__main__':
    host = "127.0.0.1"
    port =3306
    user = "root"
    passwd = "redhat"
    dbname= "cmdb_imdst_com"

    tasks = Queue.Queue(maxsize=4)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    process_pid = "%s/%s.pid"%(BASE_DIR,sys.argv[0].strip(".py"))
    process_log = "%s/%s.log"%(BASE_DIR,sys.argv[0].strip(".py"))
    if len(sys.argv) != 2:
        print "参数数目输入错误,ps:python %s start|stop|restart"%sys.argv[0]
    elif sys.argv[1] != "start" and sys.argv[1] != "stop" and sys.argv[1] != "restart":
        print "参数输入错误,ps:start|stop|restart"
    elif sys.argv[1] == "start":
        print "the process is start"
        daemonize('/dev/null',process_log,process_log)
        main()
    elif sys.argv[1] == "stop":
        with open(process_pid,"r") as f:
            pid = f.read()
        os.kill(int(pid),9)
        print "the process is stop"
    elif sys.argv[1] == "restart":
        try:
            with open(process_pid,"r") as f:
                pid = f.read()
                os.kill(int(pid),9)
            print "the process is stop"
            print "the process is start"
            daemonize('/dev/null',process_log,process_log)
            main()
        except OSError,e:
            print e
            print "the process is start"
            daemonize('/dev/null',process_log,process_log)
            main()
        except:
            print "error"
