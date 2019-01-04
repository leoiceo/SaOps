#!/usr/bin/python
#_*_coding:utf-8_*_

from __future__ import division
import threading
import sys,os,commands,paramiko,django,time,datetime
reload(sys)
sys.setdefaultencoding( "utf-8" )

BaseDir = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-1])
sys.path.append(BaseDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE","cmdb.settings") #环境变量
django.setup()
from cmdb import settings
from hosts.models import *
from inc.models import *



def create_serverlist(area_name,area_mini_name,platform):
    work_dir = "%s/%s/%s/"%(settings.INC_GAMELIST_DIR,area_mini_name,platform)
    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)
    damodir = settings.INC_GAMELIST_DIR

    os.system("\cp %s/main.ini %s/mother.ini %s" % (damodir,damodir,work_dir))
    os.system("rm -f %s/summary.ini" % work_dir)

    serverlist_info = ServerList.objects.filter(area_name=area_name,platform=platform)

    for num in serverlist_info:
        with open("%s/mother.ini"%work_dir,"r") as f:
            first = f.read()

        with open("%s/single.ini" %work_dir,'w') as f:
            f.write(first)

        with open("%s/single.ini" %work_dir,'r') as f:
            base_file = f.read()
        base_file = base_file.replace("serverid",str(num.server_id))
        base_file = base_file.replace("ip",str(num.p_ip))
        base_file = base_file.replace("gamename",str(num.server_name))
        base_file = base_file.replace("isopen",str(num.isopen))
        base_file = base_file.replace("status",str(num.status))
        base_file = base_file.replace("port",str(num.port))
        base_file = base_file.replace("serverstartdate",str(num.open_time))
        base_file = base_file.replace("zoneid",str(num.zone_id))

        with open("%s/summary.ini" %work_dir,'a') as f:
            f.write(base_file)

    with open("%s/main.ini"%work_dir,'r') as f:
        main_file = f.read()

    with open("%s/summary.ini" % work_dir,'r') as f:
        all_info = f.read()

    main_file = main_file.replace("ALLINFO",str(all_info))

    with open("%s/server_list.ini" % work_dir,'w') as f:
        f.write(main_file)


def create_zonelist(area_name,area_mini_name,platform):
    work_dir = "%s/%s/%s/"%(settings.INC_GAMELIST_DIR,area_mini_name,platform)
    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)
    damodir = settings.INC_GAMELIST_DIR

    os.system("\cp %s/main.ini %s/zone_mother.ini %s" % (damodir,damodir,work_dir))
    os.system("rm -f %s/summary.ini" % work_dir)

    zonelist_info = ZoneList.objects.filter(area_name=area_name,platform=platform)
    for num in zonelist_info:

        with open("%s/zone_mother.ini"%work_dir,"r") as f:
            first = f.read()

        with open("%s/single.ini" %work_dir,'w') as f:
            f.write(first)

        with open("%s/single.ini" %work_dir,'r') as f:
            base_file = f.read()
        base_file = base_file.replace("maxzoneingroup",str(num.maxzoneingroup))
        base_file = base_file.replace("minzoneingroup",str(num.minzoneingroup))
        base_file = base_file.replace("zonegroupid",str(num.zonegroupid))
        base_file = base_file.replace("zonegroupname",str(num.zonegroupname))

        with open("%s/summary.ini" %work_dir,'a') as f:
            f.write(base_file)

    with open("%s/main.ini"%work_dir,'r') as f:
        main_file = f.read()

    with open("%s/summary.ini" % work_dir,'r') as f:
        all_info = f.read()

    main_file = main_file.replace("ALLINFO",str(all_info))

    with open("%s/zone_list.ini" % work_dir,'w') as f:
        f.write(main_file)

def create_whitelist(area_name,area_mini_name,platform):
    work_dir = "%s/%s/%s/"%(settings.INC_GAMELIST_DIR,area_mini_name,platform)
    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)
    damodir = settings.INC_GAMELIST_DIR

    os.system("\cp %s/main.ini %s/white_mother.ini %s" % (damodir,damodir,work_dir))
    os.system("rm -f %s/summary.ini" % work_dir)
    whitelist_info = WhiteList.objects.filter(area_name=area_name)

    for num in whitelist_info:
        with open("%s/white_mother.ini"%work_dir,"r") as f:
            first = f.read()

        with open("%s/single.ini" %work_dir,'w') as f:
            f.write(first)

        with open("%s/single.ini" %work_dir,'r') as f:
            base_file = f.read()

        base_file = base_file.replace("server",str(num.ip))
        base_file = base_file.replace("state",str(num.state))

        with open("%s/summary.ini" %work_dir,'a') as f:
            f.write(base_file)

    with open("%s/main.ini"%work_dir,'r') as f:
        main_file = f.read()

    with open("%s/summary.ini" % work_dir,'r') as f:
        all_info = f.read()

    main_file = main_file.replace("ALLINFO",str(all_info))

    with open("%s/white_list.ini" % work_dir,'w') as f:
        f.write(main_file)

if __name__ == "__main__":
    #create_serverlist("国内","cn","android")
    #create_zonelist("国内","cn","android")
    create_whitelist("国内","cn","android")