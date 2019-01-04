#!/usr/bin/env python
#-*-coding:utf-8-*-
from __future__ import division

import MySQLdb.cursors
import paramiko,os,sys,threading,django
reload(sys)
sys.setdefaultencoding( "utf-8" )

BaseDir = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-2])
sys.path.append(BaseDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE","cmdb.settings") #环境变量
django.setup()

from cmdb import settings
from multitask.models import *
from hosts.models import *
from scripts_common import  *
import time

def file_func(host,port,localpath,remotepath,username,keyfile,password,trans_time):
    """
    文件分发函数
    :param host:        主机
    :param port:        端口
    :param localpath:   本地路径
    :param remotepath:  远程路径
    :param username:    用户名
    :param keyfile:     认证KEY
    :param password:    密码
    :return:
    """
    write_log = FileTransLog.objects.filter(trans_time=trans_time)
    start_trans_time = time.time()
    try:
        remote_sftp(host,port,localpath,remotepath,username,keyfile,password)
        end_time = int(time.time())
        total_time  = time.time() - start_trans_time
        write_log.update(status="100.0%",log="文件分发成功",end_time=end_time,total_time="%.f3"%total_time)

    except Exception,e:
        write_log.update(log="文件传送失败,%s"%e)

def dir_func(host,port,username,keyfile,password,trans_time):
    write_log = FileTransLog.objects.filter(trans_time=trans_time)
    sum = 0
    num = 0
    start_trans_time = time.time()
    try:
        for parent,dirnames,filenames in os.walk(package):
            sum += len(filenames)
        for parent,dirnames,filenames in os.walk(package):
            for filename in filenames:
                file = os.path.join(parent,filename)
                client_file = os.path.basename(file)
                client_endfile = os.path.dirname(file)
                fuck,shit = client_endfile.split(settings.FILE_TRANS_DIR)
                client_all_path = file.split(settings.FILE_TRANS_DIR)[1]
                localpath = file
                remotepath = "%s/%s"%(client_path,client_all_path)
                run = paramiko.SSHClient()
                run.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                key=paramiko.RSAKey.from_private_key_file(keyfile,password)
                run.connect(host,int(port),username=username, pkey=key)
                cmd = "mkdir -p %s/%s"%(client_path,shit)
                stdin,stdout,stderr = run.exec_command(cmd)
                run.close()
                remote_sftp(host,port,localpath,remotepath,username,keyfile,password)
                num += 1
                status = round(num / sum,3)*100
                # %.1f% 表示小数点保留一位
                write_log.update(status="%.1f%%"%status,log="正在上传")
        end_time = int(time.time())
        total_time = time.time() - start_trans_time
        write_log.update(status="100.0%", log="文件分发成功", end_time=end_time, total_time="%.f3" % total_time)
    except Exception,e:
        write_log.update(log="目录分发失败,%s" %e)


if __name__ == '__main__':
    base_filedir = settings.FILE_TRANS_DIR
    threads = []
    #传入的第一个参数(ip,port,filename,project,system,file_dir) file_dir:远程目录名
    host_info = eval(sys.argv[1])

    for host_dict in host_info:
        host = host_dict["host"]
        port = host_dict["host_port"]
        send_file = host_dict["send_file"]
        client_path = host_dict["file_dir"]
        project = host_dict["project"]
        os_system = host_dict["os_system"]
        trans_time = host_dict["trans_time"]

        # 判断每天类型,获得用户名
        if os_system == "Windows":
            username = "Administrator"
        else:
            username = "root"
        keyname = KeyManager.objects.get(project__mini_name=project).name
        keyfile = "%s/%s" % (settings.KEY_DIR, keyname)
        password = None
        '''
        if project == "inc":
            keyfile = settings.INC_KEY
            password = None
        '''
        package = "%s/%s"%(base_filedir,send_file)
        #print package,"........"
        if client_path[-1] == "/":
            pass
        else:
            client_path = client_path + "/"

        if os.path.isfile(package):
            localpath = package
            remotepath = "%s/%s"%(client_path,send_file)
            t = mythread(file_func,(host,port,localpath,remotepath,username,keyfile,password,trans_time))
            threads.append(t)
        else:
            t = mythread(dir_func,(host,port,username,keyfile,password,trans_time))
            threads.append(t)
    for i in threads:
        i.start()
    for i in threads:
        i.join()