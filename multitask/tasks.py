#!/usr/bin/env python
#-*-coding:utf-8-*-
from __future__ import absolute_import
from django.utils.timezone import now
from celery.schedules import crontab
from datetime import timedelta
import os
from cmdb import settings
from celery import shared_task
import time,datetime,commands,platform


@shared_task
def filetrans_func(host_info):
    """
    文件分发模块
    :param host_info:
    :return:
    """

    if platform.system() == "Windows":
        pass
    else:
        cmd = """python %s/multitask/scripts/filetrans.py "%s" """ % (settings.BASE_DIR,host_info)
    print cmd
    os.system(cmd)

@shared_task
def exec_script_func(*args,**kwargs):
    """
    批量执行脚本
    :param host_list:
    :param script_name:
    :param script_type:
    :return:
    """
    if platform.system() == "Windows":
        pass
    else:
        cmd = """python %s/multitask/scripts/exec_scripts.py "%s" "%s" "%s" "%s" """ % (settings.BASE_DIR,args,kwargs)
    print cmd
    os.system(cmd)

@shared_task
def exec_pro_script_func(*args,**kwargs):
    """
    批量执行脚本
    :param host_list:
    :param script_name:
    :param script_type:
    :return:
    """
    if platform.system() == "Windows":
        pass
    else:
        cmd = """python %s/multitask/scripts/exec_pro_scripts.py "%s" "%s" """ % (settings.BASE_DIR,args,kwargs)
    print cmd
    os.system(cmd)

@shared_task
def exec_cmds_func(host_info):
    """
    批量命令模块
    :param host_info:
    :return:
    """
    if platform.system() == "Windows":
        pass
    else:
        cmd = """python %s/multitask/scripts/exec_cmds.py "%s" """ % (settings.BASE_DIR,host_info)
    print cmd
    os.system(cmd)


@shared_task
def web_site_crontrol_func(*args,**kwargs):
    """
    站点管理控制模块
    :param web_site_info:
    :return:
    """
    if platform.system() == "Windows":
        pass
    else:
        cmd = """python %s/multitask/scripts/web_crontorl.py "%s" "%s" """ %(settings.BASE_DIR,args,kwargs)
    print cmd
    os.system(cmd)


@shared_task
def web_site_update_func(*args,**kwargs):
    """
    站点更新控制模块
    :param args:
    :param kwargs:
    :return:
    """
    if platform.system() == "Windows":
        pass
    else:
        cmd = """python %s/multitask/scripts/web_update.py "%s" "%s" """ %(settings.BASE_DIR,args,kwargs)
    print cmd
    os.system(cmd)

@shared_task
def web_conf_update_func(*args,**kwargs):
    """
    网站配置更新模块
    :param args:
    :param kwargs:
    :return:
    """

    if platform.system() == "Windows":
        pass
    else:
        cmd = """python %s/multitask/scripts/web_config_update.py "%s" "%s" """ %(settings.BASE_DIR,args,kwargs)
    print cmd
    os.system(cmd)
