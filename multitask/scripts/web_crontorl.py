#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo

import os,django
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



def main(host,port):
    write_log = UserAuditLog.objects.filter(log_time=log_time, p_ip=host)

    if action == "start_nginx":
        cmd = "/sbin/service nginx start"
    elif action == "stop_nginx":
        cmd = "/sbin/service nginx stop"
    elif action == "restart_nginx":
        cmd = "/sbin/service nginx reload"
    elif action == "restart_phpfpm":
        cmd = "/sbin/service php-fpm restart"

    try:
        write_log.update(status="50.0%",log="执行中......")

        out_log,err_log = remote_run(host,port,keyfile,username=username,cmd=cmd,password=None,timeout=None)

        if len(err_log) == 0:
            run_log = "执行成功,无异常"
        else:
            run_log = "执行成功,有报错"

        write_log.update(status="100.0%",log=run_log,result="%s|%s"%(out_log,err_log))
    except Exception,e:
        write_log.update(log="异常退出",result="%s"%e)

if __name__ == '__main__':
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    info = eval(sys.argv[1]) #{"action":action,log_time":log_time,"project":project}
    game_info = info[0] #{gameinfo}
    project = info[1]["project"]
    action = info[1]["action"]
    log_time = info[1]["log_time"]
    keyname = KeyManager.objects.get(project__mini_name=project).name
    username = KeyManager.objects.get(project__mini_name=project).username
    keyfile = "%s/%s" % (settings.KEY_DIR, keyname)
    threads = []
    for t in game_info:
        host,port,web_dir = t.split("+")
        i = mythread(main,(host,port))
        threads.append(i)
    for m in threads:
        m.start()
    for m in threads:
        m.join()