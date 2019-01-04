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

def myfunc(web_addr,domain):
    update_log = UserAuditLog.objects.filter(p_ip=web_addr, platform=platform, log_time=update_time)

    conf_dir = "%s/%s/%s/" % (settings.CONF_DIR, project, platform_mini_name)
    for cf_name in cf_name_list:
        cf_dir = WebConfig.objects.get(project__mini_name=project,platform__plat_name=platform,
                                            cf_name=cf_name).cf_dir
        local_path = "%s/%s" %(conf_dir,cf_name)
        os.system("dos2unix %s" % local_path)
        remote_path = "%s/%s" %(cf_dir,cf_name)
        update_log.update(status="40.0%", server_name=remote_path,log="开始推送%s到服务器"%cf_name)
        print remote_path
        try:
            remote_sftp_new(host=web_addr,port=port,keyfile=keyfile,username=username,
                            localpath=local_path,remotepath=remote_path,password=None)
            update_log.update(log="<font class='green-fonts'>配置文件更新成功</font>", status="100.0%")
        except Exception, e:
            update_log.update(log="<font class='red-fonts'>配置文件更新失败</font>", result="%s" % e)


if __name__ == "__main__":
    info = eval(sys.argv[1])
    web_info_list, cf_name_list, project, platform, update_time = info

    threads = []
    port = 22022

    keyname = KeyManager.objects.get(project__mini_name=project).name
    username = KeyManager.objects.get(project__mini_name=project).username
    keyfile = "%s/%s" % (settings.KEY_DIR, keyname)

    platform_mini_name = platform_type.objects.get(plat_name=platform).mini_name

    for web_info in web_info_list:
        web_addr = web_info["p_ip"]  #公网地址
        domain = web_info["domain"]
        t = mythread(myfunc,(web_addr,domain))
        threads.append(t)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
