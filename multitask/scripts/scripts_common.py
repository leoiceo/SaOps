#!/usr/bin/python
#_*_coding:utf-8_*_
from django.core.mail import send_mail
import paramiko,os,sys,threading
from manager.common import *

class mythread(threading.Thread):
    def __init__(self,func,args):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
    def run(self):
        apply(self.func,self.args)


def my_send_mail(subject,context):

    send_mail(
    subject,context,
     'nagios@imdst.com',
    ['leoiceo@qq.com'], fail_silently=False)

def remote_sftp(ip,port,localpath,remotepath,username,keyfile,password):
    ssh = paramiko.Transport((ip,int(port)))
    key=paramiko.RSAKey.from_private_key_file(keyfile,password)
    ssh.connect(username=username, pkey=key)
    sftp = paramiko.SFTPClient.from_transport(ssh)
    localpath = "%s"%localpath
    remotepath = "%s"%remotepath
    sftp.put(localpath,remotepath)
    sftp.close()
    ssh.close()

def remote_sftp_new(host,port,keyfile,username,localpath,remotepath,password):
    ssh = paramiko.Transport((host,int(port)))
    key=paramiko.RSAKey.from_private_key_file(keyfile,password)
    if username == "root":
        ssh.connect(username="root", pkey=key)
    elif username == "Administrator":
        ssh.connect(username="Administrator", pkey=key)
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




def exec_shell(cmd):
    out_log, err_log = local_shell(cmd)
    if len(err_log) > 0:
        raise Exception("Fuck,Error:%s" % err_log)