#!/usr/bin/python
#_*_coding:utf-8_*_
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.db.models import Q
from manager.views.permission import *
import urllib2,json
from cmdb import settings
from manager.myauth import *
from hosts.models import *
from multitask.models import *
from scripting.models import *
import commands,shutil,time,codecs
from datetime import datetime
from multitask import tasks
from manager.common import *
from djcelery.models import *
from threading import Thread

def async_func():
    cmd = "supervisorctl reload celery-MainProcess"
    os.system(cmd)

@login_required
@PermissionVerify()
def task_plan(request):
    """
    project = models.CharField(_('project name'),max_length=200,null=True)
    script_name = models.CharField(_('script name'),max_length=200,null=True)
    create_user = models.CharField(_('create user'),max_length=200,null=True)
    motify_user = models.CharField(_('motify user'),max_length=200,null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    :param request:
    :return:
    """
    header_title,nav,tip= "任务列表","计划任务","任务列表"
    project = request.GET.get("project")
    zone = Project.objects.get(mini_name=project).name
    log = request.GET.get("log")
    err = request.GET.get("err")
    search_name = request.POST.get("search_name")

    script_files = ScriptsManage.objects.filter(project__mini_name=project)
    back_time = CrontabSchedule.objects.all()

    if search_name is not None:
       menu = PeriodicTask.objects.filter(Q(project__icontains=search_name)|Q(script_name__icontains=search_name)|
                                          Q(name__icontains=search_name)|Q(create_user__icontains=search_name))
    else:
        menu = PeriodicTask.objects.filter(project=project)

    return render_to_response('scripting/task_plan.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def task_plan_eye(request):
    header_title,nav,tip= "任务详细信息","计划任务","任务列表"
    project = request.GET.get("project")
    zone = Project.objects.get(mini_name=project).name
    plan_id = request.GET.get("id")
    menu = PeriodicTask.objects.filter(id=plan_id)
    script_name = PeriodicTask.objects.get(id=plan_id).script_name
    plan_info = TaskPlanRunLog.objects.filter(project__mini_name=project,script_name=script_name).order_by("-run_time")[:1000]

    return render_to_response('scripting/task_plan_eye.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def task_plan_manage(request):
    """
    任务计划管理
    :param request:
    :return:
    """
    project = request.GET.get("project")
    action = request.GET.get("action")
    script_use = request.GET.get("script_use")
    script_name = request.GET.get("script_name")

    if action == "save":
        script_use = request.POST.get("script_use")
        script_name = request.POST.get("script_name")
        minute = request.POST.get("minute")
        hour = request.POST.get("hour")
        week = request.POST.get("week")
        date = request.POST.get("date")
        month = request.POST.get("month")
        if minute is not None and hour is not None and week is not None and month is not None:
            check_script_use = PeriodicTask.objects.filter(name="%s"%script_use,project="%s"%project)
            if len(check_script_use) != 0:
                err = "定时任务名称重复:%s"%script_use
                return HttpResponseRedirect("/crontab/task_plan/?project=%s&err=%s"%(project,err))
            else:
                cs= CrontabSchedule(minute="%s"%minute,hour="%s"%hour,day_of_week="%s"%week,
                                    day_of_month="%s"%date,month_of_year="%s"%month)
                cs.save()
                crontab_id = cs.id
                thisuser = UserProfile.objects.get(email="%s"%request.user).name
                kwargs = {
                    "script_name":"%s"%script_name,
                    "task_name":"%s"% script_use,
                    "project":"%s"%project,
                    "email": "%s" % request.user
                }
                pt = PeriodicTask(name="%s"%script_use,task="scripting.tasks.task_plan",crontab_id=crontab_id,
                                  args="[]",kwargs=json.dumps(kwargs),enabled="0",project=project,
                                  script_name=script_name,create_user=thisuser,motify_user=thisuser,
                                  create_date=datetime.now())
                pt.save()
                log = "添加成功:%s"%script_use
                return HttpResponseRedirect("/crontab/task_plan/?project=%s&log=%s"%(project,log))

    elif action == "motify":
        new_script_use = request.POST.get("new_script_use")
        new_script_name = request.POST.get("new_script_name")
        # 计划任务周期
        minute = request.POST.get("minute")
        hour = request.POST.get("hour")
        week = request.POST.get("week")
        date = request.POST.get("date")
        month = request.POST.get("month")

        check_script_use = PeriodicTask.objects.filter(script_name=new_script_name,project=project)
        pt = PeriodicTask.objects.get(project=project,name=script_use,script_name=script_name).crontab
        if len(check_script_use) > 1:
            err = "定时任务名称重复:%s"%new_script_use
        else:
            pt_id = pt.id
            cs = CrontabSchedule.objects.filter(id=pt_id)
            cs.update(minute=minute,hour=hour,day_of_week=week,day_of_month=date,month_of_year=month)
            uppt = PeriodicTask.objects.filter(name=script_use,script_name=script_name,project=project)
            uppt.update(name=new_script_use,script_name=new_script_name)
            log = "%s修改成功"%new_script_use
            thr = Thread(target=async_func,args=[])
            thr.start()
            return HttpResponseRedirect("/crontab/task_plan/?project=%s&log=%s"%(project,log))

    elif action == "switch":
        pt = PeriodicTask.objects.filter(project=project,name=script_use,script_name=script_name)
        dk_status = pt.get().enabled
        if dk_status:
            pt.update(enabled=False)
            log = "%s : 已停止该任务"%script_use
        else:
            pt.update(enabled=True)
            log = "%s : 已启用该任务"%script_use
        thr = Thread(target=async_func,args=[])
        thr.start()
        return HttpResponseRedirect("/crontab/task_plan/?project=%s&log=%s"%(project,log))

    elif action == "del":
        pt = PeriodicTask.objects.get(project=project,name=script_use,script_name=script_name).crontab
        pt.delete()
        pt = PeriodicTask.objects.filter(project=project,name=script_use,script_name=script_name)
        pt.delete()
        log = "已删除任务:%s"%script_use
        thr = Thread(target=async_func,args=[])
        thr.start()
        return HttpResponseRedirect("/crontab/task_plan/?project=%s&log=%s"%(project,log))

    elif action == "edit":
        header_title,nav,tip= "编辑任务","计划任务","任务列表"
        dk = PeriodicTask.objects.get(project="%s"%project,name="%s"%script_use,script_name="%s"%script_name).crontab
        return render_to_response("scripting/task_plan_edit.html",locals(),context_instance=RequestContext(request))

    else:
        log = "未知的参数"
        return HttpResponseRedirect("/crontab/task_plan/?project=%s&log=%s"%(project,log))

@login_required
@PermissionVerify()
def task_plan_hosts(request):
    """
    选择计划任务服务器
    按项目,地区,平台划分
    :param request:
    :return:
    """
    header_title,nav,tip= "选择服务器","计划任务","任务列表"
    project = request.GET.get("project")

    script_use = request.GET.get("script_use")
    script_name = request.GET.get("script_name")
    area_name = request.GET.get("area")
    action = request.GET.get("action")
    if action == "save":
        subcheck = request.POST.getlist("subcheck")
        pt = PeriodicTask.objects.filter(project=project,name=script_use,script_name=script_name)
        pt.update(args=json.dumps(subcheck))
        thr = Thread(target=async_func,args=[])
        thr.start()
        return HttpResponseRedirect("/crontab/check_task_hosts/?project=%s&script_use=%s&script_name=%s"%(project,script_use,script_name))

    iUser = UserProfile.objects.get(email="%s"% request.user)
    if iUser.is_admin:
        project_info = Project.objects.filter(mini_name=project)
    else:
        project_info = iUser.project.filter(mini_name=project)

    if project is None:
        project = project_info[0].mini_name
    zone = project
    if project is None:
        #project = Project.objects.all()[0].mini_name
        log = "您的账号没有任何项目权限"
    else:
        menu = host.objects.filter(project__mini_name=project,area__mini_name=area_name).order_by("p_ip")

    if area_name is None:
        area_name = area_type.objects.all()[0].mini_name

    zone = area_name

    pro_area_info = {}
    for p in project_info:
        area_list = []
        area_obj = host.objects.filter(project__mini_name=p.mini_name).values("area").distinct()
        for z in area_obj:
            area_mini_name = area_type.objects.get(id=z["area"]).mini_name
            area_list.append(area_mini_name)
        pro_area_info.setdefault(p.mini_name,area_list)

    return render_to_response('scripting/task_plan_hosts.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def check_task_hosts(request):
    header_title,nav,tip= "已选服务器","计划任务","任务列表"
    project = request.GET.get("project")
    script_use = request.GET.get("script_use")
    script_name = request.GET.get("script_name")
    action = request.GET.get("action")
    if action == "save":
        subcheck = request.POST.getlist("subcheck")
        try:
            pt = PeriodicTask.objects.filter(project=project,name=script_use,script_name=script_name)
            pt.update(args=json.dumps(subcheck))
            thr = Thread(target=async_func,args=[])
            thr.start()
            data_log = "保存成功"
        except Exception,e:
            error_log = "保存失败,%s" %e

    menu = eval(PeriodicTask.objects.get(project=project,name=script_use,script_name=script_name).args)

    return render_to_response("scripting/check_task_hosts.html",locals(),context_instance=RequestContext(request))