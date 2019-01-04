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
def task_plan(*args,**kwargs):
    """
    计划任务执行模块
    :return:
    """
    if platform.system() == "Windows":
        pass
    else:
        cmd = """python %s/scripting/scripts/task_plan.py "%s" "%s" """%(settings.BASE_DIR,args,kwargs)
    print cmd
    os.system(cmd)