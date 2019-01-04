#!/usr/bin/env python
#-*-coding:utf-8-*-
from __future__ import division

import MySQLdb.cursors
import paramiko,os,sys,threading,django,time
reload(sys)
sys.setdefaultencoding( "utf-8" )

BaseDir = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-2])
sys.path.append(BaseDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE","cmdb.settings") #环境变量
django.setup()
from cmdb import settings
from multitask.models import *
from scripts_common import  *
from hosts.models import *
import pickle


def main(ip,port,cmd,username,keyfile,password,start_time):
    write_log = CmdExecLog.objects.filter(p_ip=ip,start_time=start_time)
    start_exec_time = time.time()
    try:
        write_log.update(log="开始执行:%s"%cmd,status="40.0%")
        out_log,err_log = remote_run(ip,port,keyfile,username,cmd,password,timeout=None)
        if len(err_log) == 0:
            run_log = "<font class='green-fonts'>执行成功,无异常</font>"
        else:
            run_log = "<font class='red-fonts'>执行成功,有报错</font>"
        end_time = int(time.time())
        total_time = time.time() - start_exec_time
        write_log.update(log=run_log,status="100.0%",result="%s|%s"%(out_log,err_log),end_time=end_time,total_time="%.3f"%total_time)
    except Exception,e:
        write_log.update(log="执行异常",result="%s"%e)

if __name__ == '__main__':
    threads = []
    #传入的第一个参数(ip,port,bash_cmd,project,system) file_dir:远程目录名

    host_info = eval(sys.argv[1])

    for host_dict in host_info:
        host = host_dict["host"]
        port = host_dict["host_port"]
        #cmd = host_dict["bash_cmd"]
        project = host_dict["project"]
        #os_system = host_dict["os_system"]
        start_time = host_dict["start_time"]
        cmd = CmdExecLog.objects.get(p_ip=host,start_time=start_time).cmd
        # 判断每天类型,获得用户名
        keyname=KeyManager.objects.get(project__mini_name=project).name
        username=KeyManager.objects.get(project__mini_name=project).username
        keyfile = "%s/%s" % (settings.KEY_DIR, keyname)
        password = None
        '''
        if project == "inc":
            keyfile = settings.INC_KEY
            password = None
        elif project == "gjsj":
            keyfile = settings.GJSJ_KEY
            password = None
        '''
        t = mythread(main,(host,port,cmd,username,keyfile,password,start_time))
        threads.append(t)

    for i in threads:
        i.start()
    for i in threads:
        i.join()


