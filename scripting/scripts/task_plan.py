#!/usr/bin/env python
#coding:utf-8

from __future__ import division
import threading
import sys,os,commands,paramiko,django,time,datetime
reload(sys)
sys.setdefaultencoding( "utf-8" )

BaseDir = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-2])
sys.path.append(BaseDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE","cmdb.settings") #环境变量
django.setup()
from django.core.mail import send_mail
from cmdb import settings
from scripting.models import  *
from manager.myauth import  *
from hosts.models import *

def remote_sftp(host,port,keyfile,username,localpath,remotepath,password):
    ssh = paramiko.Transport((host,int(port)))
    key=paramiko.RSAKey.from_private_key_file(keyfile,password)
    ssh.connect(username=username, pkey=key)
    sftp = paramiko.SFTPClient.from_transport(ssh)
    localpath = "%s"%localpath
    remotepath = "%s"%remotepath
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


class mythread(threading.Thread):
    def __init__(self,func,args):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
    def run(self):
        apply(self.func,self.args)

def myfunc(host,port,os_type):
    run_time = int(time.time())
    project_id = Project.objects.get(mini_name=project)
    write_log = TaskPlanRunLog(project=project_id,script_name=script_file,ip=host,log="开始执行",run_time=run_time)
    write_log.save()

    localpath = "%s/%s/shell_script/%s"%(settings.BASH_DIR,project,script_file)
    remotepath = "/tmp/%s"%script_file

    # if os_type == "Windows":
    #     username = "Administrator"
    # else:
    #     username = "root"

    if script_file.split(".")[1] == "py":
            cmd = "python %s"%remotepath
    elif script_file.split(".")[1] == "sh":
            cmd = "/bin/bash %s"%remotepath
    #print cmd

    update_log = TaskPlanRunLog.objects.filter(ip=host,script_name=script_file,run_time=run_time)

    try:
        update_log.update(log="开始上传脚本")
        remote_sftp(host,port,keyfile,username,localpath,remotepath,password=None)
        update_log.update(log="开始执行脚本")
        out_log,err_log = remote_run(host,port,keyfile,username,cmd,password=None,timeout=None)
        if len(err_log) == 0:
            update_log.update(log="执行完成,无异常",result="%s|%s" % (out_log,err_log))
        else:
            update_log.update(log="执行完成,出现异常", result="%s|%s" % (out_log, err_log))
    except Exception,e:
        update_log.update(log="出现异常",result="%s"%e)

def main():
    threads = []
    for i in server_info:
        host,port,os_type = i.split("+")
        t = mythread(myfunc,(host,port,os_type))
        threads.append(t)
    for i in threads:
        i.start()
    for i in threads:
        i.join()

def task_alter_mail(user_email):
    """
    先不用这个功能先，设置提醒开关后再发提醒
    :param user_email:
    :return:
    """
    message = '''
        %s,于原定计划时间执行成功
    ''' % task_name
    try:
        send_mail('【计划任务】执行成功', message, '%s' % settings.EMAIL_HOST_USER, ['%s' % user_email], fail_silently=False)
    except:
        pass

if __name__ == "__main__":
    server_info = eval(sys.argv[1])
    info = eval(sys.argv[2])
    project = info["project"]
    script_file = info["script_name"]
    try:
        user_email = info["email"]
        task_name = info["task_name"]
    except Exception,e:
        pass

    keyname = KeyManager.objects.get(project__mini_name=project).name
    username = KeyManager.objects.get(project__mini_name=project).username
    keyfile = "%s/%s" % (settings.KEY_DIR, keyname)
    #keyfile = "%s/%s/scripts/%s.key"%(settings.BASE_DIR,project,project)
    os.system("chmod 600 %s"%keyfile)
    main()