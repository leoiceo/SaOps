#!/usr/bin/python
#_*_coding:utf-8_*_
from __future__ import absolute_import
from django.utils.timezone import now
from hosts.models import *
from gjsj.models import *
from celery.schedules import crontab
from datetime import timedelta
import paramiko,os,socket,datetime,time,commands,platform
from celery import shared_task
from cmdb import settings
import subprocess,json


@shared_task
def asset_update_func(server_info,log_time):
    """
    资产采集任务
    :param all_hosts:
    :param user_key_str:
    :return:
    """
    cmd = """python %s/hosts/scripts/asset_update.py "%s" "%s" """ % (settings.BASE_DIR,server_info,log_time)
    os.system(cmd)
    print cmd

@shared_task
def init_hosts(all_hosts,script_name,project,start_time):
    """
    主机权限初始化
    :param all_hosts:
    :param script_name:
    :return:
    """
    cmd = """python %s/hosts/scripts/init_hosts.py "%s" "%s" "%s" "%s" """ % (settings.BASE_DIR,all_hosts,script_name,project,start_time)
    os.system(cmd)
    print cmd

@shared_task
def init_dbs(server_info, script_name, project, start_time):
    """
    数据库权限初始化
    :param all_hosts:
    :param script_name:
    :return:
    """
    cmd = """python %s/hosts/scripts/init_dbs.py "%s" "%s" "%s" "%s" """ % (settings.BASE_DIR,server_info,script_name,project,start_time)
    os.system(cmd)
    print cmd


@shared_task
def cdn_url_update(data):
    cmd = """python %s/hosts/scripts/url_update.py "%s" """ % (settings.BASE_DIR,data)
    os.system(cmd)
    print cmd