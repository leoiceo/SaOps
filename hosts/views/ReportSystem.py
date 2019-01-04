#!/usr/bin/env python
#-*- coding: utf-8 -*-
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.db.models import Min,Max,Sum,Avg, F, FloatField
from hosts.models import  *
from manager.myauth import *
from manager.views.permission import *
from manager.common import *
from scripting.models import *
import json

@login_required
@PermissionVerify()
def report_list(request):
    header_title, nav, tip = "服务器性能状态", "基础资源管理", "服务器性能状态"
    nowday = datetime.datetime.now()
    yest = nowday - datetime.timedelta(days=int(7))
    yestime = yest.strftime("%Y-%m-%d %H:%M:%S")
    before_7_day = time.mktime(time.strptime(yestime, '%Y-%m-%d %H:%M:%S'))

    script_list = ["check_server.sh","check_now_server.sh","check_slg_server.sh"]
    try:
        report_id_max = ReportSystem.objects.aggregate(Max('report_id'))['report_id__max']
        report_info = TaskPlanRunLog.objects.filter(script_name__in=script_list,id__gt=report_id_max)
    except Exception,e:
        print e
        report_info = TaskPlanRunLog.objects.filter(script_name__in=script_list)

    print report_info
    for i in report_info:
        report_id = i.id
        check_id = ReportSystem.objects.filter(report_id=report_id)
        if len(check_id) > 0:
            continue
        else:
            i_info = i.result.strip('|').split(',')
            #备注
            remark = host.objects.get(p_ip=i.ip).commit
            project_id = Project.objects.get(name=i.project.name)
            add_report_system = ReportSystem(
                project = project_id,
                p_ip = i.ip,
                s_ip = i_info[0],
                remarks = remark,
                cputotal = i_info[1],
                load_1 = i_info[2],
                load_5 = i_info[3],
                load_15 = i_info[4],
                memtotal = i_info[5],
                memused = i_info[6],
                memuseprecent = "%s" % i_info[7],
                swaptotal = i_info[8],
                swapused = i_info[9],
                swapuseprecent = "%s" % i_info[10],
                disk_root_sise =  i_info[11],
                disk_root_useprecent = "%s" % i_info[12],
                disk_data_size =  i_info[14],
                disk_data_useprecent = "%s" % i_info[15],
                report_id = i.id,
                add_time = i.run_time
            )
            add_report_system.save()
    ReportSystem.objects.filter(add_time__lt=before_7_day).delete()
    report_info = ReportSystem.objects.filter(add_time__gt=before_7_day)

    return render_to_response('hosts/report_list.html', locals(), context_instance=RequestContext(request))