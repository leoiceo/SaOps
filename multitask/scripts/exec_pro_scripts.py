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
from scripts_common import *
from hosts.models import *


def main(ip,port,username,keyfile,password):
    write_log = ScriptExeclog.objects.filter(p_ip=ip,start_time=start_time)
    localpath = "%s/%s"%(script_dir,script_name)
    remotepath = "/tmp/%s"%script_name
    start_exec_time = time.time()
    try:
        remote_sftp(ip,port,localpath,remotepath,username,keyfile,password)
        write_log.update(status="50.0%",log="脚本上传至目标服务器成功")
        if script_type == ".py":
            cmd = "python /tmp/%s"%script_name
            out_log,err_log = remote_run(ip,port,keyfile,username,cmd,password,timeout=None)
        elif script_type == ".sh":
            if args_num > 0:
                cmd = "/bin/bash /tmp/%s %s && rm -f /tmp/%s" % (script_name,' '.join(inputs), script_name)
            else:
                cmd = "/bin/bash /tmp/%s  && rm -f /tmp/%s"%(script_name,script_name)
            out_log,err_log = remote_run(ip,port,keyfile,username,cmd,password,timeout=None)
        if len(err_log) == 0:
            run_log = "<font class='green-fonts'>执行成功,无异常</font>"
        else:
            run_log = "<font class='red-fonts'>执行成功,有报错</font>"
        end_time = int(time.time())
        total_time = time.time() - start_exec_time
        write_log.update(status="100.0%",log=run_log,result="%s|%s"%(out_log,err_log),total_time="%.3f" % total_time,end_time=end_time)
    except Exception,e:
        write_log.update(log="任务执行失败!",result="%s"%e)

if __name__ == '__main__':
    info = eval(sys.argv[1])
    if len(info) > 5:
        host_list, script_name, script_type, start_time, project, inputs = info
        args_num = len(inputs)
    else:
        host_list, script_name, script_type, start_time, project = info
    # host_list = eval(sys.argv[1])
    # script_name = sys.argv[2]
    # script_type = sys.argv[3]
    # start_time = sys.argv[4]
    # project = sys.argv[5]
    script_dir = "%s/%s/shell_script"%(settings.BASH_DIR,project)
    threads = []
    password = None
    for host in host_list:
        project,ip,port = host.split("+")
        keyname = KeyManager.objects.get(project__mini_name=project).name
        username = KeyManager.objects.get(project__mini_name=project).username
        keyfile = "%s/%s" % (settings.KEY_DIR, keyname)
        '''
        if project == "inc":
            username = "root"
            keyfile = settings.INC_KEY

        else:
            username = "root"
            keyfile = settings.INC_KEY
        '''
        t = mythread(main,(ip,port,username,keyfile,password))
        threads.append(t)
    for i in threads:
        i.start()
    for i in threads:
        i.join()