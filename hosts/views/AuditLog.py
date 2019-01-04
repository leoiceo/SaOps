#!/usr/bin/env python
#-*- coding: utf-8 -*-
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from manager.views.permission import *
from hosts.models import  *
from manager.myauth import *
from manager.common import *
from django.db.models import Q
import datetime


def clear_30days_ago():
    now_time = datetime.datetime.now()
    yes_time = now_time + datetime.timedelta(days=-30)
    yes_time_nyr = yes_time.strftime('%Y-%m-%d')
    try:
        del_info = SshAuditLog.objects.filter(log_time__lte="%s 00:00:00" % yes_time_nyr)
        del_info.delete()
        return True
    except:
        return False


@login_required
@PermissionVerify()
def log_list(request):
    header_title, nav, tip = "日志审计", "审计", "操作审计"

    ip = request.GET.get("ip")

    if request.method == 'GET':
        project = request.GET.get("project")

    else:
        project = request.POST.get("project")
        search_name = request.POST.get("search_name")

        try:
            if search_name:
                log_info = SshAuditLog.objects.filter(Q(p_ip__contains=search_name) |
                                                      Q(username__contains=search_name) |
                                                      Q(project__name__contains=search_name) |
                                                      Q(project__mini_name__contains=search_name) |
                                                      Q(login_ip__contains=search_name) |
                                                      Q(cmd_log__contains=search_name))

                return render_to_response('hosts/log_list.html', locals(), context_instance=RequestContext(request))
        except Exception, e:
            error = "%s"%e

    log_info = SshAuditLog.objects.filter(project__mini_name=project).order_by('-log_time')

    iUser = UserProfile.objects.get(email="%s" % request.user)

    if iUser.is_admin:
        pro_info = Project.objects.all()
    else:
        pro_info = iUser.project.all()

    clear_30days_ago

    pro_list  = []
    for pro in pro_info:
        pro_dict={}
        pro_dict['name'] = pro.name
        pro_dict['mini_name'] = pro.mini_name
        pro_dict['cmd_count'] = SshAuditLog.objects.filter(project__mini_name=project).count()
        pro_list.append(pro_dict)

    if ip is not None:
        log_info = SshAuditLog.objects.filter(p_ip=ip).order_by('-log_time')


    return render_to_response('hosts/log_list.html', locals(), context_instance=RequestContext(request))


