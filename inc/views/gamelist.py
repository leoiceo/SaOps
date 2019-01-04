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
from inc.public import create_serverlist,create_zonelist,create_whitelist

@login_required
@PermissionVerify()
def zone_list(request):
    header_title,nav,tip= "大区列表管理","游戏列表和公告","大区列表管理"
    project = "inc"

    area_name  = request.GET.get("area")
    platform = request.GET.get("platform")
    data_log = request.GET.get("data_log")
    error_log = request.GET.get("error_log")

    if area_name is None:
        area_name = "国内"

    if platform is None:
        platform = "android"

    zone = area_name

    menu = ZoneList.objects.filter(area_name=area_name,platform=platform)
    return render_to_response("inc/zone_list.html",locals(),context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def zone_list_print(request):
    header_title,nav,tip= "生成区服列表","区服列表管理","生成区服列表"
    project = "inc"
    area_name = request.GET.get("area")
    platform = request.GET.get("platform")
    area_mini_name = area_type.objects.get(area_name=area_name).mini_name
    zone = area_name
    try:
        dirname = GameListFileDir.objects.get(area_name=area_name,platform=platform).dirname
    except Exception,e:
        dirname = "当前路径为空,请填写绝对路径..."

    # public.py 公共模块
    try:
        create_zonelist(area_name,area_mini_name,platform)
        with open("%s/%s/%s/zone_list.ini"%(settings.INC_GAMELIST_DIR,area_mini_name,platform),"r") as f:
            cmd_result = f.read().strip()
    except Exception,e:
        cmd_result = "%s" % e

    return render_to_response("inc/zone_list_print.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def zone_list_edit(request):
    header_title,nav,tip= "大区列表管理","游戏列表和公告","大区列表管理"
    platform = request.GET.get("platform")
    area_name = request.GET.get("area")
    server_group = request.POST.getlist("server_group")
    action = request.GET.get("action")

    if action == "add":
        maxzoneingroup = request.POST.get("n_maxzoneingroup")
        minzoneingroup = request.POST.get("n_minzoneingroup")
        zonegroupid = request.POST.get("n_zonegroupid")
        zonegroupname = request.POST.get("n_zonegroupname")

        if len(maxzoneingroup) < 1 or len(minzoneingroup) < 1 or len(zonegroupid) < 1 or len(zonegroupname) < 1:
            error_log = "填入信息不能为空"
            return HttpResponseRedirect("/inc/zone_list/?area=%s&platform=%s&error_log=%s"%(area_name,platform,error_log))
        else:
            check_zonegroupid = ZoneList.objects.filter(area_name=area_name,platform=platform,zonegroupid=zonegroupid)
            if len(check_zonegroupid) != 0:
                error_log = "%s 已存在,请勿重复添加"%(zonegroupid)
                return HttpResponseRedirect("/inc/zone_list/?area=%s&platform=%s&error_log=%s"%(area_name,platform,error_log))
            else:
                add = ZoneList(area_name=area_name,platform=platform,maxzoneingroup=maxzoneingroup,
                               minzoneingroup=minzoneingroup,zonegroupid=zonegroupid,
                               zonegroupname=zonegroupname)
                add.save()
            data_log = "%s %s添加成功"%(zonegroupid,zonegroupname)

            return HttpResponseRedirect("/inc/zone_list/?area=%s&platform=%s&data_log=%s"%(area_name,platform,data_log))
    elif action == "delete":
        logs = ""
        for server in server_group:
            zonegroupid,zonegroupname = server.split("+")
            d = ZoneList.objects.filter(area_name=area_name,platform=platform,
                                          zonegroupid=zonegroupid,zonegroupname=zonegroupname)
            d.delete()
            logs = logs + "%s," % zonegroupname
        data_log = "删除成功:" + logs
        return HttpResponseRedirect("/inc/zone_list/?area=%s&platform=%s&data_log=%s"%(area_name,platform,data_log))

    elif action == "modify":
        len_table = request.GET.get("len_table")
        for i in range(int(len_table)):
            server_group = "editable[" + str(i) + "][server_group]"
            maxzoneingroup = "editable[" + str(i) + "][maxzoneingroup]"
            minzoneingroup = "editable[" + str(i) + "][minzoneingroup]"
            zonegroupid = "editable[" + str(i) + "][zonegroupid]"
            zonegroupname = "editable[" + str(i) + "][zonegroupname]"

            server_group = request.GET.get(server_group).strip()
            old_zonegroupid,old_zonegroupname = server_group.split("+")

            maxzoneingroup = request.GET.get(maxzoneingroup).strip()
            minzoneingroup = request.GET.get(minzoneingroup).strip()
            zonegroupid = request.GET.get(zonegroupid).strip()
            zonegroupname = request.GET.get(zonegroupname).strip()
            print old_zonegroupid,old_zonegroupname,"..."*20
            m = ZoneList.objects.filter(area_name=area_name,platform=platform,zonegroupid=old_zonegroupid,zonegroupname=old_zonegroupname)
            print m
            m.update(maxzoneingroup=maxzoneingroup,minzoneingroup=minzoneingroup,
                     zonegroupid=zonegroupid,zonegroupname=zonegroupname)

        data_log = "修改成功"

        return HttpResponseRedirect("/inc/zone_list/?area=%s&platform=%s&data_log=%s"%(area_name,platform,data_log))


@login_required
@PermissionVerify()
def zone_list_send(request):
    project = "inc"
    platform = request.GET.get("platform")
    area_name = request.GET.get("area")
    senddir = request.POST.get("senddir")
    area_mini_name = area_type.objects.get(area_name=area_name).mini_name
    zone = area_name
    # 路径补全
    if senddir[-1] == "/":
        pass
    else:
        senddir = senddir + "/"

    # 保存推送路径
    menu = GameListFileDir.objects.filter(area_name=area_name,platform=platform)
    if len(menu) == 0:
        glfd = GameListFileDir(area_name=area_name,platform=platform,dirname=senddir)
        glfd.save()
    else:
        menu.update(dirname=senddir)

    try:
        p_ip = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="区服列表服").p_ip
        port = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="区服列表服").port
        localpath = "%s/%s/%s/zone_list.ini"% (settings.INC_GAMELIST_DIR,area_mini_name,platform)
        remotepath = "%s/zone_list.ini"%senddir
        remote_sftp(host=p_ip,port=port,keyfile=settings.INC_KEY,username="root",localpath=localpath,remotepath=remotepath,password=None)
        cmd = "chown -R www:www %sserver_list.ini"%senddir
        remote_run(host=p_ip,port=port,keyfile=settings.INC_KEY,username="root",cmd=cmd,password=None,timeout=None)
        data_log = "推送成功"
    except:
        error_log = "%s地区,区服列表服务器无法连接,推送失败!请检查该地服务器是否正常" % area_name
        return HttpResponseRedirect("/inc/zone_list/?platform=%s&area=%s&error_log=%s"%(platform,area_name,error_log))

    return HttpResponseRedirect("/inc/zone_list/?platform=%s&data_log=%s&area=%s"%(platform,data_log,area_name))


@login_required
@PermissionVerify()
def server_list(request):
    header_title,nav,tip= "区服列表管理","游戏列表和公告","区服列表管理"
    project = "inc"

    area_name  = request.GET.get("area")
    platform = request.GET.get("platform")
    data_log = request.GET.get("data_log")
    error_log = request.GET.get("error_log")

    if area_name is None:
        area_name = "国内"

    if platform is None:
        platform = "android"

    zone = area_name

    menu = ServerList.objects.filter(area_name=area_name,platform=platform).order_by("server_id")

    return render_to_response("inc/server_list.html",locals(),context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def server_list_edit(request):
    header_title,nav,tip= "区服列表管理","游戏列表和公告","区服列表管理"
    project = "inc"

    area_name  = request.GET.get("area")
    platform = request.GET.get("platform")
    server_group = request.POST.getlist("server_group")
    action = request.GET.get("action")
    server_state = request.POST.get("server_state")
    zone = area_name

    #print server_state,"...."
    if server_state is not None and server_state.isdigit():
        for num in server_group:
            old_server_name,old_server_id= num.split("+")
            m = ServerList.objects.filter(area_name=area_name,platform=platform,server_name=old_server_name,server_id=old_server_id)
            m.update(status=int(server_state))
        data_log = "服务器状态修改成功"

    if action == "add":
        '''此段代码已失效'''
        server_name = request.POST.get("server_name")
        server_id = request.POST.get("server_id")
        p_ip = request.POST.get("p_ip")
        isopen = request.POST.get("isopen")
        status = request.POST.get("status")
        port = request.POST.get("port")
        open_time = request.POST.get("open_time")
        zone_id = request.POST.get("zone_id")
        if server_name is not None and server_id is not None and p_ip is not None:
            check_ip = ServerList.objects.filter(p_ip=p_ip)
            if len(check_ip) == 0:
                w = ServerList(area_name=area_name,platform=platform,server_name=server_name,
                           server_id=int(server_id),p_ip=p_ip,isopen=isopen,status=status,
                           port=int(port),open_time=open_time,zone_id=int(zone_id))
                w.save()
                data_log = "%s添加成功" % server_name
            else:
                error_log = "添加失败，列表信息出现重复"
                return HttpResponseRedirect("/inc/server_list/?platform=%s&error_log=%s&area=%s"%(platform,error_log,area_name))
        else:
            error_log = "添加失败，信息不能为空"
            return HttpResponseRedirect("/inc/server_list/?platform=%s&error_log=%s&area=%s"%(platform,error_log,area_name))
    elif action == "delete":
        data_log = ""
        for num in server_group:
            server_name,server_id = num.split("+")
            d = ServerList.objects.filter(area_name=area_name,platform=platform,server_name=server_name,server_id=server_id)
            d.delete()
            data_log = data_log + server_name + ","
        data_log = "删除成功:" + data_log

    elif action == "modify":
        len_table = request.GET.get("len_table")
        for i in range(int(len_table)):
            server_group = "editable[" + str(i) + "][server_group]"
            server_name = "editable[" + str(i) + "][server_name]"
            server_id = "editable[" + str(i) + "][server_id]"
            p_ip = "editable[" + str(i) + "][p_ip]"
            isopen = "editable[" + str(i) + "][isopen]"
            port = "editable[" + str(i) + "][port]"
            open_time = "editable[" + str(i) + "][open_time]"
            zone_id = "editable[" + str(i) + "][zone_id]"
            status = "editable[" + str(i) + "][status]"

            server_group = request.GET.get(server_group).strip()
            server_name = request.GET.get(server_name).strip()
            server_id = request.GET.get(server_id).strip()
            p_ip = request.GET.get(p_ip).strip()
            isopen = request.GET.get(isopen).strip()
            port = request.GET.get(port).strip()
            open_time = request.GET.get(open_time).strip()
            zone_id = request.GET.get(zone_id).strip()
            status = request.GET.get(status).strip()

            if server_group == "new":
                check_ip = ServerList.objects.filter(server_id=server_id)
                if len(check_ip) != 0:
                    error_log = "服务器名或者ID,不能重复"
                    return HttpResponseRedirect("/inc/server_list/?platform=%s&error_log=%s&area=%s" % (platform, error_log, area_name))
                else:
                    w = ServerList(area_name=area_name, platform=platform, server_name=server_name,
                                   server_id=int(server_id), p_ip=p_ip, isopen=isopen, status=status,
                                   port=int(port), open_time=open_time, zone_id=int(zone_id))
                    w.save()
                    data_log = "%s添加成功" % server_name
            else:
                old_server_name,old_server_id= server_group.split("+")
                m = ServerList.objects.filter(area_name=area_name,platform=platform,server_name=old_server_name,server_id=old_server_id)
                m.update(server_name=server_name,server_id=int(server_id),p_ip=p_ip,isopen=isopen,port=int(port),open_time=open_time,zone_id=int(zone_id))

    data_log = "服务器状态修改成功"
    return HttpResponseRedirect("/inc/server_list/?platform=%s&data_log=%s&area=%s"%(platform,data_log,area_name))


@login_required
@PermissionVerify()
def server_list_print(request):
    header_title,nav,tip= "生成区服列表","区服列表管理","生成区服列表"
    project = "inc"
    area_name = request.GET.get("area")
    platform = request.GET.get("platform")
    area_mini_name = area_type.objects.get(area_name=area_name).mini_name
    zone = area_name
    try:
        dirname = GameListFileDir.objects.get(area_name=area_name,platform=platform).dirname
    except Exception,e:
        dirname = "当前路径为空,请填写绝对路径..."

    # public.py 公共模块
    create_serverlist(area_name,area_mini_name,platform)

    with open("%s/%s/%s/server_list.ini"%(settings.INC_GAMELIST_DIR,area_mini_name,platform),"r") as f:
        cmd_result = f.read().strip()


    return render_to_response("inc/server_list_print.html",locals(),context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def server_list_send(request):
    project = "inc"
    platform = request.GET.get("platform")
    area_name = request.GET.get("area")
    senddir = request.POST.get("senddir")
    area_mini_name = area_type.objects.get(area_name=area_name).mini_name
    zone = area_name
    # 路径补全
    if senddir[-1] == "/":
        pass
    else:
        senddir = senddir + "/"

    # 保存推送路径
    menu = GameListFileDir.objects.filter(area_name=area_name,platform=platform)
    if len(menu) == 0:
        glfd = GameListFileDir(area_name=area_name,platform=platform,dirname=senddir)
        glfd.save()
    else:
        menu.update(dirname=senddir)

    try:
        p_ip = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="区服列表服").p_ip
        port = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="区服列表服").port
        localpath = "%s/%s/%s/server_list.ini"% (settings.INC_GAMELIST_DIR,area_mini_name,platform)
        remotepath = "%s/server_list.ini"%senddir
        remote_sftp(host=p_ip,port=port,keyfile=settings.INC_KEY,username="root",localpath=localpath,remotepath=remotepath,password=None)
        cmd = "chown -R www:www %sserver_list.ini"%senddir
        remote_run(host=p_ip,port=port,keyfile=settings.INC_KEY,username="root",cmd=cmd,password=None,timeout=None)
        data_log = "推送成功"
    except:
        error_log = "%s地区,区服列表服务器无法连接,推送失败!请检查该地服务器是否正常" % area_name
        return HttpResponseRedirect("/inc/server_list/?platform=%s&area=%s&error_log=%s"%(platform,area_name,error_log))

    return HttpResponseRedirect("/inc/server_list/?platform=%s&data_log=%s&area=%s"%(platform,data_log,area_name))


@login_required
@PermissionVerify()
def white_list(request):
    header_title,nav,tip= "白名单和公告管理","游戏列表和公告","白名单和公告管理"
    project = "inc"
    area_name  = request.GET.get("area")
    data_log = request.GET.get("data_log")
    error_log = request.GET.get("error_log")

    if area_name is None:
        area_name = "国内"

    zone = area_name

    menu = WhiteList.objects.filter(area_name=area_name)

    return render_to_response("inc/white_list.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def white_list_edit(request):
    header_title,nav,tip= "生成白名单和公告管理","游戏列表和公告","生成白名单和公告管理"
    project = "inc"
    area_name  = request.GET.get("area")
    action = request.GET.get("action")
    ip = request.POST.get("ip")
    iplist = request.POST.getlist("subcheck")

    try:
        if action == "del":
            for ip in iplist:
                d = WhiteList.objects.filter(area_name=area_name,ip=ip)
                d.delete()
            data_log = "%s 删除成功"%iplist
            return HttpResponseRedirect("/inc/white_list/?area=%s&data_log=%s"%(area_name,data_log))
        elif action == "edit":
            len_table = request.GET.get("len_table")
            for i in range(int(len_table)):
                white_name = "editable[" + str(i) + "][white_name]"
                ip = "editable[" + str(i) + "][ip]"
                commit = "editable[" + str(i) + "][commit]"
                state = "editable[" + str(i) + "][state]"

                white_name = request.GET.get(white_name).strip()
                ip = request.GET.get(ip).strip()
                commit = request.GET.get(commit).strip()
                state = request.GET.get(state).strip()

                if white_name == "new":
                    w = WhiteList(area_name=area_name,ip=ip,state=state,commit=commit)
                    w.save()
                else:
                    u = WhiteList.objects.filter(area_name=area_name,ip=white_name)
                    u.update(ip=ip,state=state,commit=commit)
                data_log = "修改成功"

            return HttpResponseRedirect("/inc/white_list/?area=%s&data_log=%s"%(area_name,data_log))
    except Exception,e:
        error_log = "出错了...%s" % e
        return  HttpResponseRedirect("/inc/white_list/?area=%s&error_log=%s"%(area_name,error_log))

@login_required
@PermissionVerify()
def white_list_print(request):
    header_title,nav,tip= "生成白名单和公告修改","白名单和公告管理","生成白名单和公告修改"
    project = "inc"
    area_name  = request.GET.get("area")
    platform = request.GET.get("platform")
    data_log = request.GET.get("data_log")
    error_log = request.GET.get("error_log")

    if area_name is None:
        area_name = "国内"
    if platform is None:
        platform = "android"

    zone = area_name

    area_mini_name = area_type.objects.get(area_name=area_name).mini_name
    create_whitelist(area_name,area_mini_name,platform)

    with open("%s/%s/%s/white_list.ini"%(settings.INC_GAMELIST_DIR,area_mini_name,platform),"r") as f:
        cmd_result = f.read().strip()

    gamelistdir = GameListFileDir.objects.filter(area_name=area_name)
    try:
        maintain_announcement = GameNotice.objects.get(area_name=area_name,platform=platform,filename="maintain_announcement.ini").content
        maintain_content = GameNotice.objects.get(area_name=area_name,platform=platform,filename="maintain_content.ini").content
        version_announcement = GameNotice.objects.get(area_name=area_name,platform=platform,filename="version_announcement.ini").content
    except:
        pass
    return render_to_response("inc/white_list_print.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def gamelist_dir_edit(request):
    project = "inc"
    area_name  = request.GET.get("area")
    platform = request.GET.get("platform")
    action = request.GET.get("action")
    subcheck = request.POST.getlist("subcheck")

    if action == "del":
        for num in subcheck:
            d = GameListFileDir.objects.filter(area_name=area_name,platform=num)
            d.delete()
    elif action == "delete":
        d = GameListFileDir.objects.filter(area_name=area_name,platform=platform)
        d.delete()
    elif action == "edit":
        len_table = request.GET.get("len_table")
        for i in range(int(len_table)):
                group = "editable[" + str(i) + "][group]"
                area_name = "editable[" + str(i) + "][area_name]"
                platform = "editable[" + str(i) + "][platform]"
                dirname = "editable[" + str(i) + "][dirname]"

                group = request.GET.get(group).strip()
                area_name = request.GET.get(area_name).strip()
                platform = request.GET.get(platform).strip()
                dirname = request.GET.get(dirname).strip()

                if group == "new":
                    n = GameListFileDir(area_name=area_name,platform=platform,dirname=dirname)
                    n.save()
                else:
                    e = GameListFileDir.objects.filter(area_name=area_name,platform=group)
                    e.update(dirname=dirname,platform=platform)

    return HttpResponseRedirect("/inc/white_list_print/?area_name=%s&platform=%s"%(area_name,platform))

@login_required
@PermissionVerify()
def white_list_send(request):
    project = "inc"
    area_name  = request.GET.get("area")
    area_mini_name = area_type.objects.get(area_name=area_name).mini_name
    #platform = request.GET.get("platform")
    # 推送平台
    subcheck = request.POST.getlist("subcheck")
    # 公告列表
    notice_file_list = request.POST.getlist("notice_file")

    # 公告文件内容
    maintain = request.POST.get("maintain")
    maintain_content = request.POST.get("maintain_content")
    version_announcement = request.POST.get("version_announcement")
    platform_dir_dict = {}
    try:
        p_ip = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="区服列表服").p_ip
        port = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="区服列表服").port
        for platform in subcheck:
            dirname = GameListFileDir.objects.get(area_name=area_name,platform=platform).dirname
            if dirname[-1] == "/":
                pass
            else:
                dirname = dirname + "/"
            platform_dir_dict["%s"%platform] = dirname

        for notice_file in notice_file_list:

            notice_text = request.POST.get("%s"%notice_file)

            for platform in subcheck:
                with open("%s/%s/%s/%s.ini"%(settings.INC_GAMELIST_DIR,area_mini_name,platform,notice_file),'w') as f:
                    f.write(notice_text)

                if notice_file == "maintain_announcement":
                    m = GameNotice.objects.filter(area_name=area_name,platform=platform,filename="maintain_announcement.ini")
                    if len(m) == 0:
                        new = GameNotice(area_name=area_name,platform=platform,filename="maintain_announcement.ini",content=notice_text)
                        new.save()
                    else:
                        m.update(content=notice_text)
                elif notice_file == "maintain_content":
                    m = GameNotice.objects.filter(area_name=area_name,platform=platform,filename="maintain_content.ini")
                    if len(m) == 0:
                        new = GameNotice(area_name=area_name,platform=platform,filename="maintain_content.ini",content=notice_text)
                        new.save()
                    else:
                        m.update(content=notice_text)
                elif notice_file == "version_announcement":
                    m = GameNotice.objects.filter(area_name=area_name,platform=platform,filename="version_announcement.ini")
                    if len(m) == 0:
                        new = GameNotice(area_name=area_name,platform=platform,filename="version_announcement.ini",content=notice_text)
                        new.save()
                    else:
                        m.update(content=notice_text)

    except Exception,e:
        error_log = "%s" %e
        return HttpResponseRedirect("/inc/inc_white_list/?area=%s&error_log=%s"%(area_name,error_log))
    info = {}
    info["platform_dir_dict"] = platform_dir_dict
    info["notice_file_list"] = notice_file_list
    info["host"] = p_ip
    info["port"] = port
    info["area_name"] = area_mini_name
    tasks.send_whitelist_func.delay(info)

    data_log = "推送成功"
    return HttpResponseRedirect("/inc/inc_white_list/?area=%s&data_log=%s"%(area_name,data_log))