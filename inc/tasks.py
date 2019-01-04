#!/usr/bin/python
#_*_coding:utf-8_*_
from __future__ import absolute_import
from django.utils.timezone import now
from hosts.models import *
from inc.models import *
from celery.schedules import crontab
from datetime import timedelta
import paramiko,os,socket,datetime,time,commands,platform
from celery import shared_task
from cmdb import settings
import subprocess


@shared_task
def host_init_func(all_hosts,user_key_str):
    """
    服务器初始化任务
    :param all_hosts:
    :param user_key_str:
    :return:
    """
    if platform.system() == "Windows":
        cmd = """python %s\inc\scripts\host_init.py "%s" "%s" """ % (settings.BASE_DIR,all_hosts,user_key_str)
    else:
        cmd = """python %s/inc/scripts/host_init.py "%s" "%s" """ % (settings.BASE_DIR,all_hosts,user_key_str)
    os.system(cmd)

@shared_task
def db_init_func(db_info):
    """
    数据库初始化任务
    :param args:
    :param kwargs:
    :return:
    """
    if platform.system() == "Windows":
        cmd = """python %s\inc\scripts\db_init.py "%s" """ % (settings.BASE_DIR,db_info)
    else:
        cmd = """python %s/inc/scripts/db_init.py "%s" """ % (settings.BASE_DIR,db_info)
    os.system(cmd)

@shared_task
def game_install_func(*args,**kwargs):
    """
    游戏服安装任务函数
    :param args:
    :param kwargs:
    :return:
    """
    if platform.system() == "Windows":
        cmd = '''python %s\inc\scripts\game_install.py "%s" '''%(settings.BASE_DIR,list(args))
    else:
        cmd = '''python %s/inc/scripts/game_install.py "%s" '''%(settings.BASE_DIR,list(args))
    os.system(cmd)

@shared_task
def bfserver_install_func(*args,**kwargs):
    """
    游戏服安装任务函数
    :param args:
    :param kwargs:
    :return:
    """
    if platform.system() == "Windows":
        cmd = '''python %s\inc\scripts\\bfserver_install.py "%s" '''%(settings.BASE_DIR,list(args))
    else:
        cmd = '''python %s/inc/scripts/bfserver_install.py "%s" '''%(settings.BASE_DIR,list(args))
    os.system(cmd)

@shared_task
def gameserver_crt_func(game_info,action):
    """
    游戏服开关服控制
    :param game_info:
    :param action:
    :return:
    """
    if platform.system() == "Windows":
        pass
    else:
        cmd = '''python %s/inc/scripts/gameserver_crt.py "%s" %s'''%(settings.BASE_DIR,game_info,action)
    os.system(cmd)

@shared_task
def backup_func(game_info):
    """
    数据库备份脚本
    :param game_info:
    :return:
    """
    if platform.system() == "Windows":
        pass
    else:
        cmd = '''python %s/inc/scripts/db_backup.py "%s" '''%(settings.BASE_DIR,game_info)

    os.system(cmd)

@shared_task
def game_drop_func(game_info):
    """
    删除游戏服程序和数据库脚本
    :param game_info:
    :return:
    """
    if platform.system() == "Windows":
        pass
    else:
        cmd = '''python %s/inc/scripts/game_drop.py "%s" '''%(settings.BASE_DIR,game_info)

    os.system(cmd)

@shared_task
def inc_dbbackup():
    """
    定时备份任务
    :return:
    """
    if platform.system() == "Windows":
        pass
    else:
        cmd = "python %s/inc/scripts/all_dbbackup.py"% settings.BASE_DIR

    os.system(cmd)

@shared_task
def config_update_func(*args,**kwargs):
    """
    配置文件更新
    :return:
    """
    if platform.system() == "Windows":
        pass
    else:
        cmd = """python %s/inc/scripts/config_update.py "%s" """%(settings.BASE_DIR,list(args))
    os.system(cmd)

@shared_task
def sql_update_func(*args,**kwargs):
    """
    数据库更新
    :param args:
    :param kwargs:
    :return:
    """
    if platform.system() == "Windows":
        pass
    else:
        cmd = """python %s/inc/scripts/sql_update.py "%s" """%(settings.BASE_DIR,list(args))
    os.system(cmd)


@shared_task
def game_update_func(*args,**kwargs):
    """
    游戏服务端更新
    :param args:
    :param kwargs:
    :return:
    """

    if platform.system() == "Windows":
        pass
    else:
        cmd = """python %s/inc/scripts/game_update.py "%s" """%(settings.BASE_DIR,list(args))
    os.system(cmd)

@shared_task
def send_whitelist_func(*args,**kwargs):
    """
    推送白名单和游戏公告
    :param info:
    :return:
    """

    if platform.system() == "Windows":
        pass
    else:
        cmd = """python %s/inc/scripts/send_whitelist_notice.py "%s" """%(settings.BASE_DIR,list(args))

    os.system(cmd)