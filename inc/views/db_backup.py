#!/usr/bin/python
#_*_coding:utf-8_*_

from __future__ import absolute_import
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from inc import tasks
from cmdb import settings
from manager.views.permission import *
from hosts.models import  *
from manager.myauth import *
from inc.models import *
import os,sys,commands,time
from datetime import date
from djcelery.models import *

@login_required
@PermissionVerify()
def backup_process(request):
    header_title,nav,tip= "备份管理过程","游戏项目管理","备份管理过程"
    project = request.GET.get("project")
    action = request.GET.get("action")
    platform = request.GET.get("platform")
    zone = platform
    menu = BackupProcess.objects.filter(platform="%s"%platform)
    if action == '1':
        return render_to_response("inc/backup_status.html",locals(),context_instance=RequestContext(request))
    else:
        return render_to_response("inc/backup_process.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def inc_backup(request):
    header_title,nav,tip= "备份管理","游戏项目管理","数据库备份"
    project = "inc"
    area_name = request.GET.get("area")
    platform = request.GET.get("platform")
    nowdate = request.POST.get("date")
    subcheck = request.POST.getlist("subcheck")
    crt_backup = request.POST.get("crt_backup")

    if area_name is None:
        area_name = "国内"
    if platform is None:
        platform = "android"
    zone = area_name
    #inc_area_plat_info = {}
    #info = gameinfo.objects.all()

    if nowdate is None or len(nowdate) == 0:
        today = date.today()
    else:
        today = nowdate
    '''
    for i in info:
        platform_list = []
        area_name = i.area.area_name
        plat_name = i.platform.mini_name
        if plat_name not in platform_list:
            platform_list.append(plat_name)
        try:
            old_plat_list = inc_area_plat_info[area_name]
            platform_list = old_plat_list + platform_list
            platform_list = list(set(platform_list))
            inc_area_plat_info[area_name] = platform_list
        except Exception,e:
            inc_area_plat_info.setdefault(area_name,platform_list)
    '''
    backup_all_count = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=platform).exclude(use__use_name="战场服").exclude(use__use_name="日志服").count()
    #备份成功和失败数量
    backup_done = GamedbBackend.objects.filter(platform=platform,area_name=area_name,bak_date=today,status="ok").count()
    backup_failed = GamedbBackend.objects.filter(platform=platform,area_name=area_name,bak_date=today,status="failed").count()
    menu = GamedbBackend.objects.filter(platform=platform,area_name=area_name,bak_date=today).order_by("server_name","-bak_date","-bak_time")
    return render_to_response("inc/inc_backend.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def backup_plan(request):
    header_title,nav,tip= "备份管理","游戏项目管理","数据库备份"
    project = request.GET.get("project")
    action = request.GET.get("action")
    #备份任务名称
    task_name = request.GET.get("task_name")

    minute = request.POST.get("minute")
    hour = request.POST.get("hour")
    week = request.POST.get("week")
    date = request.POST.get("date")
    month = request.POST.get("month")

    plan_time = request.GET.get("plan_time")
    plan_name = request.GET.get("plan_name")
    print action,plan_time

    # 添加定时计划
    if minute is not None and hour is not None and week is not None and month is not None:
        plan = CrontabSchedule(minute="%s"%minute,hour="%s"%hour,day_of_week="%s"%week,day_of_month="%s"%date,month_of_year="%s"%month)
        plan.save()

    if action == "disable":
        plan = PeriodicTask.objects.filter(name="%s"%task_name)
        plan.update(enabled=0)
    elif action == "enable":
        plan = PeriodicTask.objects.filter(name="%s"%task_name)
        plan.update(enabled=1)
    elif action == "delete":
        plan = PeriodicTask.objects.filter(name="%s"%task_name)
        plan.delete()
    elif action == "add":
        minute,hour,week,date,month = plan_time.split(" ")
        crontab_id = CrontabSchedule.objects.get(minute="%s"%minute,hour="%s"%hour,day_of_week="%s"%week,day_of_month="%s"%date,month_of_year="%s"%month).id
        plan = PeriodicTask(name="%s"%plan_name,task="inc.tasks.inc_dbbackup",crontab_id=crontab_id,args="[]",kwargs="{}",enabled="1")
        plan.save()

    menu = PeriodicTask.objects.filter(task="inc.tasks.inc_dbbackup")
    back_time = CrontabSchedule.objects.all()
    return render_to_response("inc/dbbackup_plan.html",locals(),context_instance=RequestContext(request))