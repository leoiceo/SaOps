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
from hosts import tasks
from hosts.forms import *
import time,json

@login_required
@PermissionVerify()
def asset_status(request):
    header_title, nav, tip = "采集资产信息", "资产管理", "待采集资产列表"
    project = request.GET.get("project")

    iUser = UserProfile.objects.get(email="%s" % request.user)
    if iUser.is_admin:
        pro_info = Project.objects.all()
    else:
        pro_info = iUser.project.all()

    if project == "None" or project is None:
        project = pro_info[0].mini_name
        host_info = host.objects.filter(project__mini_name=project).exclude(recover=1).exclude(asset_status=1).order_by('-online_date')

    elif project is not None:
        host_info = host.objects.filter(project__mini_name=project).exclude(recover=1).exclude(asset_status=1).order_by('-online_date')
    zone = project
    return render_to_response('assets/asset_status.html', locals(), context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def asset_update(request):
    header_title, nav, tip = "采集资产信息", "资产管理", "采集状态"
    choice_host = request.POST.getlist("choice_host")
    operator = UserProfile.objects.get(email="%s" % request.user).name
    project = request.GET.get("project")
    log_time = int(time.time())
    update_host = request.GET.get("update_host")
    server_info = []

    if update_host is not None:
        server_dic = {}
        port = host.objects.get(p_ip=update_host).port
        area_name = host.objects.get(p_ip=update_host).area
        platform = host.objects.get(p_ip=update_host).platform.mini_name
        server_dic["hostname"] = update_host
        server_dic["port"] = port
        server_dic["username"] = "root"
        server_dic["ssh_key"] = "%s/%s.key" % (settings.KEY_DIR, project)
        write_log = UserAuditLog(project=project, area_name=area_name,platform=platform, p_ip=update_host, log_type="更新资产", log="开始执行更新任务",
                                 status="5.0%", log_time=log_time, operator=operator)
        write_log.save()
        server_info.append(server_dic)
        tasks.asset_update_func.delay(server_info, log_time)
        status_info = UserAuditLog.objects.filter(project=project, log_time=log_time, operator=operator)
        return render_to_response('assets/asset_update.html', locals(), context_instance=RequestContext(request))

    if choice_host is not None:
        for p_ip in choice_host:
            server_dic = {}
            port = host.objects.get(p_ip=p_ip).port
            area_name = host.objects.get(p_ip=p_ip).area
            platform = host.objects.get(p_ip=p_ip).platform.mini_name
            server_dic["hostname"] = p_ip
            server_dic["port"] = port
            server_dic["username"] = "root"
            server_dic["ssh_key"] = "%s/%s.key" % (settings.KEY_DIR,project)
            write_log = UserAuditLog(project=project,area_name=area_name,platform=platform,p_ip=p_ip,log_type="资产采集",
                                     log="开始执行采集任务",status="5.0%",log_time=log_time,operator=operator)
            write_log.save()
            server_info.append(server_dic)

    #print server_info
        tasks.asset_update_func.delay(server_info,log_time)
        status_info = UserAuditLog.objects.filter(project=project,log_time=log_time,operator=operator)
        return render_to_response('assets/asset_update.html', locals(), context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('asset_status'))

@login_required
@PermissionVerify()
def asset_update_process(request):
    header_title, nav, tip = "采集资产信息", "资产管理", "采集状态"
    project = request.GET.get("project")
    log_time = request.GET.get("log_time")
    status_info = UserAuditLog.objects.filter(project=project, log_time=log_time)
    return render_to_response('assets/asset_update_process.html', locals(), context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def asset_list(request):
    header_title, nav, tip = "设备管理", "资产管理", "设备列表"
    project = request.GET.get("project")
    asset_id = request.GET.get("id")
    action = request.GET.get("action")

    iUser = UserProfile.objects.get(email="%s" % request.user)
    if action == "del":
        ip = Asset.objects.get(id=asset_id).p_ip
        del_asset = Asset.objects.filter(id=asset_id)
        del_asset.delete()
        update_status = host.objects.filter(p_ip=ip)
        update_status.update(asset_status=0)

    if iUser.is_admin:
        pro_info = Project.objects.all()
    else:
        pro_info = iUser.project.all()
    pro_list = []
    for pro in pro_info:
        pro_list.append(pro.mini_name)

    if project == "None" or project is None:
        project = pro_info[0].mini_name
        asset_info = Asset.objects.filter(project__mini_name__in=pro_list)
    elif project is not None:
        asset_info = Asset.objects.filter(project__name=project)
    zone = project

    return render_to_response('assets/asset_list.html', locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def asset_detail(request,asset_id):
    header_title, nav, tip, zone = "资产详细信息", "资产列表", "资产ID","详细信息"

    if request.method == "GET":
        try:
            asset_obj = Asset.objects.get(id=asset_id)
            disk_info = eval(asset_obj.disk_info)
            disk_total = 0
            disk_count = 0
            for k,v in disk_info.items():
                disk_total += v
                disk_count += 1
            disk_mount = eval(asset_obj.disk_mount)
            other_ip = eval(asset_obj.other_ip)

            log_list = UserAuditLog.objects.filter(log_type__in=["资产采集","资产更新"],p_ip=asset_obj.p_ip).order_by("id")

        except Exception, e:
            return render(request, 'assets/asset_detail.html', {'error': e})

        return render_to_response('assets/asset_detail.html', locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def asset_update_log(request):
    header_title, nav, tip, zone = "变更记录", "资产管理", "变更记录", "详细信息"

    status_info = UserAuditLog.objects.filter(log_type__in=["资产采集","更新资产"]).order_by('-id')
    return render_to_response('assets/asset_update_log.html', locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def asset_edit(request):
    header_title, nav, tip = "修改资产", "资产管理", "修改资产"
    asset_id = request.GET.get("id")
    asset_info = Asset.objects.get(id=asset_id)
    if asset_info:
        af = AssetForm(instance=asset_info)
    else:
        msg = "没有找到这个资产ID： %s" % asset_id
    if request.method == 'POST':
        af_post = AssetForm(request.POST, instance=asset_info)
        p_ip = request.POST.get('p_ip', '')

        try:
            asset_test = Asset.objects.get(p_ip=p_ip)
            if asset_test and asset_id != unicode(asset_test.id):
                emg = u'该主机 %s 已存在!' % p_ip
        except Exception,e:
            pass
        else:
            if af_post.is_valid():
                af_save = af_post.save(commit=False)
                af_save.save()
                af_post.save_m2m()
                msg = "主机 %s 修改成功" % p_ip
                af = AssetForm(instance=asset_info)
            else:
                print "aaaaaa"
                msg = "主机 %s 修改失败" % p_ip

    return render_to_response('assets/asset_edit.html', locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def asset_add(request):
    header_title, nav, tip = "添加资产", "资产管理", "添加资产"
    af = AssetForm()
    if request.method == 'POST':
        af_post = AssetForm(request.POST)
        p_ip = request.POST.get('p_ip', '')
        try:
            if Asset.objects.filter(p_ip=p_ip):
                error = u'该主机 %s 已存在!' % p_ip

        except Exception:
            pass
        else:
            if af_post.is_valid():
                af_save = af_post.save(commit=False)
                af_save.save()
                af_post.save_m2m()
                return HttpResponseRedirect(reverse('asset_list'))
            else:
                print "aaaaaa"
                msg = "主机 %s 添加失败" % p_ip

    return render_to_response('assets/asset_add.html', locals(), context_instance=RequestContext(request))