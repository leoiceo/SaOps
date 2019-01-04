#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo

import threading
import sys,os,commands,paramiko,django
import Queue
import time
import socket
import json
import base64
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

BaseDir = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-2])
sys.path.append(BaseDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE","cmdb.settings") #环境变量
django.setup()

from manager.common import *
from hosts.models import *
from scripts_common import *
from multitask.models import *

def get_web_file():
    """
    拉取SVN版本
    :return:
    """
    update_log = UserAuditLog.objects.filter(log_time=update_time, platform=platform)
    update_log.update(status="10.0%", log="开始从SVN检出%s版本" % gversion)

    source_path = "/data/scripts/%s/%s/rep/" % (project, platform_mini_name)
    export_path = "/data/scripts/%s/%s/src/%s" % (project, platform_mini_name, gversion)

    try:
        cmd = "svn update -q -r %s %s"%(gversion,source_path)
        exec_shell(cmd)

        update_log.update(status="15.0%")

        cmd = "rm -fr %s && svn export %s/ %s" % (export_path,source_path,export_path)
        exec_shell(cmd)

        update_log.update(status="20.0%", log="检出%s成功" % gversion)
        cmd = "echo '%s' > %s/version && chown www.www %s -R" % (gversion, export_path, export_path)
        exec_shell(cmd)

        update_log.update(status="30.0%",log="检出%s成功" % gversion)

        #强制更新文件时间
        cmd = "find %s -type f|xargs touch" %(export_path)
        exec_shell(cmd)

        update_log.update(status="40.0%",log="开始推送到服务器")
    except Exception,e:
        update_log.update(log="<font class='red-fonts'>检出版本%s失败，请检查</font>" % gversion,result="%s"%e)
        sys.exit()

def myfunc(web_dir,web_addr,domain):
    update_log = UserAuditLog.objects.filter(p_ip=web_addr, platform=platform, log_time=update_time)

    export_path = "/data/scripts/%s/%s/src/%s/%s/" % (project, platform_mini_name, gversion,domain)
    exclude_file = "/data/scripts/%s/%s/conf/%s.exclude.list" % (project, platform_mini_name,domain)

    try:
        check_and_file(exclude_file)
        cmd = "/usr/bin/rsync -auqz -zrtopg --delete --progress --exclude-from='%s' -e 'ssh -i %s -o StrictHostKeyChecking=no -o PasswordAuthentication=no -p %s' %s root@%s:%s" % (
            exclude_file, keyfile, port, export_path, web_addr, web_dir)
        out_log, err_log = local_shell(cmd)

        if len(err_log) == 0:
            log_info = "<font class='green-fonts'>新版本推送完毕，无异常</font>"
        else:
            raise Exception("新版本推送失败，有异常%s" % err_log)

        if method == "heat":
            update_log.update(status="95.0%", log=log_info)
            update_log.update(status="100.0%", result="%s|%s" % (out_log, err_log))
    except Exception, e:
        update_log.update(log="<font class='red-fonts'>推送更新未成功，请检查</font>", result="%s" % e)
        sys.exit(1)

if __name__ == "__main__":
    info = eval(sys.argv[1])
    web_info_list,jump_host,jump_port,gversion,method,project,platform,update_time = info
    #游戏服字典，中转服IP和端口，SVN版本，更新方式，平台，更新时间
    threads = []
    platform_mini_name = platform_type.objects.get(plat_name=platform).mini_name

    port = 22022
    keyname = KeyManager.objects.get(project__mini_name=project).name
    username = KeyManager.objects.get(project__mini_name=project).username
    keyfile = "%s/%s" % (settings.KEY_DIR, keyname)

    #from svn export file
    get_web_file()

    for web_info in web_info_list:
        web_addr = web_info["p_ip"]  #公网地址
        web_dir = web_info["web_dir"]
        domain = web_info["domain"]
        t = mythread(myfunc,(web_dir,web_addr,domain))
        threads.append(t)
    for i in threads:
        i.start()
    for i in threads:
        i.join()