#!/usr/bin/python
#_*_coding:utf-8_*_
import threading
import sys,os,commands,paramiko,django
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

BaseDir = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-2])
sys.path.append(BaseDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE","cmdb.settings") #环境变量
django.setup()
from cmdb import settings
from hosts.models import *
from multitask.models import *
import time
def transfer_file_init(init_host,port,passwd):
    """
    分发初始化脚本文件
    :return:
    """
    write_log = ScriptExeclog.objects.filter(p_ip=init_host, start_time=start_time)
    try:
        socks=(init_host,port)
        t=paramiko.Transport(socks)
        t.connect(username='root',password='%s'%passwd)
        sftp=paramiko.SFTPClient.from_transport(t)

        remotepath="/root/%s" % script_name
        localpath = "%s/%s/shell_script/%s" % (settings.BASH_DIR, project,script_name)
        write_log.update(status="30.0%", log="脚本上传至目标服务器成功")
        sftp.put(localpath,remotepath)
        sftp.close()
        t.close()
    except Exception,e:
        #with open("/tmp/%s/host_init_err_%s.log"%(project,init_host),"w") as f:
        #f.write("连接%s失败,请检查服务器的端口和初始登录密码是否正确!"%init_host)
        end_time = int(time.time())
        write_log.update(status="10.0%", log="连接%s失败,请检查服务器的端口和初始登录密码是否正确"%init_host, result="%s" % e, end_time=end_time)
        sys.exit()

def exec_host_init(init_host,port,passwd,pubkey):
    """
    执行初始化脚本 主机地址，端口，密码，用途，地区
    :return:
    """
    write_log = ScriptExeclog.objects.filter(p_ip=init_host, start_time=start_time)
    transfer_file_init(init_host,port,passwd)
    #with open("/tmp/%s/host_init_err_%s.log"%(project,init_host),"w") as f:
    #    f.write("1.Transfer init.sh success.\n 2.Start exec %s %s" % (init_host,script_name))

    cmd = "/bin/bash '%s' '%s' '%s'" % (script_name,pubkey,init_host)
    write_log.update(status="50.0%", log="开始执行%s"%script_name)
    print cmd
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=init_host,port=int(port),username='root',password='%s'%passwd)
        stdin,stdout,stderr = ssh.exec_command(cmd)
        out_log = stdout.read().strip()
        err_log = stderr.read().strip()
        ssh.close()
        if len(err_log) == 0:
            run_log = "执行成功,无异常"
        else:
            run_log = "执行成功,有报错"

        end_time = int(time.time())
        write_log.update(status="100.0%", log=run_log, result="%s|%s" % (out_log, err_log), end_time=end_time)
    except Exception,e:
        end_time = int(time.time())
        write_log.update(status="50.0%", log="任务执行失败", result="%s" % e,end_time=end_time)

    host_update = host.objects.filter(p_ip=init_host)
    host_update.update(port=22022,host_init=1)

    #with open("/tmp/%s/host_init_%s.log"%(project,init_host),"a") as f:
    #    f.write("%s"%out_log)
    #with open("/tmp/%s/host_init_err_%s.log"%(project,init_host),"w") as f:
    #    f.write("%s"%err_log)


class mythread(threading.Thread):
    def __init__(self,func,args):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
    def run(self):
        apply(self.func,self.args)


if __name__ == "__main__":

    host_all = eval(sys.argv[1])
    script_name = sys.argv[2]
    project = sys.argv[3]
    start_time = sys.argv[4]
    if not os.path.exists("/tmp/%s/" %project):
        os.makedirs("/tmp/%s/"%project)
    threads = []
    for host_info in host_all:
        init_host = host_info["host"]
        port = host_info["port"]
        passwd = host_info["passwd"]
        pubkey = host_info["pubkey"]
        if type(passwd) is list:
            passwd = '$'.join(passwd)
        t = mythread(exec_host_init,(init_host,port,passwd,pubkey))
        threads.append(t)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
