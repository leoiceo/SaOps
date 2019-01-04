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


def remote_sftp(host,port,keyfile,username,localpath,remotepath,password):
    ssh = paramiko.Transport((host,int(port)))
    key=paramiko.RSAKey.from_private_key_file(keyfile,password)
    if username == "root":
            ssh.connect(username="root", pkey=key)
    elif username == "Administrator":
            ssh.connect(username="Administrator", pkey=key)
    sftp = paramiko.SFTPClient.from_transport(ssh)
    sftp.put(localpath,remotepath)
    sftp.close()
    ssh.close()

def remote_run(host,port,keyfile,username,cmd,password,timeout):
    run = paramiko.SSHClient()
    run.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key=paramiko.RSAKey.from_private_key_file(keyfile,password)
    if username == "root":
        run.connect(host,int(port),username="root", pkey=key)
    elif username == "Administrator":
        run.connect(host,int(port),username="Administrator", pkey=key)
    if timeout is None:
        stdin,stdout,stderr = run.exec_command(cmd)
    else:
        stdin,stdout,stderr = run.exec_command(cmd,timeout=int(timeout))
    out_log = stdout.read().strip()
    err_log = stderr.read().strip()
    run.close()
    return out_log,err_log


def transfer_file_init(init_host,port):
    """
    分发初始化脚本文件
    :return:
    """
    write_log = ScriptExeclog.objects.filter(p_ip=init_host, start_time=start_time)
    write_log.update(status="20.0%", log="开始上传脚本%s" % script_name)
    localpath = "%s/%s/shell_script/%s" % (settings.BASH_DIR, project, script_name)
    remotepath = "/tmp/%s" % script_name
    try:
        remote_sftp(init_host, port, keyfile, username, localpath, remotepath, password=None)
        write_log.update(status="30.0%", log="脚本上传完毕%s" % script_name)
    except Exception,e:
        end_time = int(time.time())
        write_log.update(status="10.0%", log="连接%s失败,请检查服务器的端口是否正确"%init_host, result="%s" % e, end_time=end_time)
        sys.exit()

def exec_host_init(init_host,port,db_passwd,db_ip):
    """
    执行初始化脚本 主机地址，端口，密码，用途，地区
    :return:
    """
    start_exec_time = time.time()
    write_log = ScriptExeclog.objects.filter(p_ip=init_host, start_time=start_time)
    transfer_file_init(init_host,port)
    cmd = "/bin/bash '/tmp/%s' '%s' '%s' && rm -f '/tmp/%s' " % (script_name,db_ip,db_passwd,script_name)
    write_log.update(status="50.0%", log="开始执行%s"%script_name)
    print cmd
    try:
        out_log, err_log = remote_run(init_host, port, keyfile, username, cmd=cmd, password=None, timeout=None)
        end_time = int(time.time())
        total_time = time.time() - start_exec_time
        if len(err_log) == 0:
            run_log = "执行成功,无异常"
        else:
            run_log = "执行成功,有报错"
        write_log.update(status="100.0%", log=run_log, result="%s|%s" % (out_log, err_log), total_time="%.3f" % total_time ,end_time=end_time)

    except Exception,e:
        end_time = int(time.time())
        write_log.update(status="50.0%", log="任务执行失败", result="%s" % e,end_time=end_time)

    db_update = host.objects.filter(p_ip=init_host,db_ip=db_ip)
    db_update.update(db_init=1)

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

    keyname = KeyManager.objects.get(project__mini_name=project).name
    username = KeyManager.objects.get(project__mini_name=project).username
    keyfile = "%s/%s" % (settings.KEY_DIR, keyname)

    threads = []
    for host_info in host_all:
        init_host = host_info["p_ip"]
        port = host_info["port"]
        db_ip = host_info["db_ip"]
        db_passwd = host_info["passwd"]
        if type(db_passwd) is list:
            db_passwd = '$'.join(db_passwd)

        t = mythread(exec_host_init,(init_host,port,db_passwd,db_ip))
        threads.append(t)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
