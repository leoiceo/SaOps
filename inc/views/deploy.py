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
import os,sys,commands

@login_required
@PermissionVerify()
def game_deploy(request):
    header_title,nav,tip,zone= "新服安装","游戏项目管理","新服安装","国内"
    project = "inc"
    area_name = request.GET.get("area")
    platform = request.GET.get("platform")
    date = request.POST.get("date")
    subcheck = request.POST.getlist("subcheck")
    crt_backup = request.POST.get("crt_backup")

    if area_name is None:
        area_name = "国内"
    if platform is None:
        platform = "android"

    inc_area_info = []
    inc_area = host.objects.filter(project__mini_name=project)
    for i in inc_area:
        all = area_type.objects.get(area_name=i.area).area_name
        inc_area_info.append(all)
    # 当前项目地区列表，去重
    inc_area_info = list(set(inc_area_info))

    publisher_info = publisher.objects.all()
    # 战场服没有DB,默认数据库已初始化
    bf_server = host.objects.filter(use__use_name="战场服")
    bf_server.update(db_init=1)
    inc_server = host.objects.filter(project__mini_name=project,area__area_name=area_name).exclude(
        #use__use_name="数据服").exclude(
        #use__use_name="登陆服").exclude(
        #use__use_name="GM服").exclude(
        use__use_name="SDK服").exclude(
        use__use_name="监控服").exclude(
        use__use_name="备份服").exclude(
        use__use_name="区服列表服").order_by("-host_init").order_by("-db_init").order_by("game_count")

    return render_to_response('inc/game_deploy.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def game_deploy_check(request):
    header_title,nav,tip= "新服安装信息确认","游戏项目管理","新服安装信息检查"
    choice_host = request.POST.get("choice_host")
    game_publisher = request.POST.get("game_publisher")
    server_name = request.POST.get("server_name")
    server_id = request.POST.get("server_id")
    zone_id = request.POST.get("zone_id")
    openserver_date = request.POST.get("date")
    game_type = request.POST.get("game_type")
    project,p_ip,s_ip,area_mini_name,plat_mini_name,db_ip = choice_host.split('+')

    if game_type == "online" or game_type == "test":
        game_id = gameinfo.objects.filter(project__mini_name=project,p_ip=p_ip).count()
        if game_id >= 0:
            game_port = 10100 + int(game_id)
        else:
            game_port = 10100
        app_dir = project + "_" + game_publisher + "_" + area_mini_name + "_" + plat_mini_name + "_" + server_id

    elif game_type == "fight":
        app_dir = project + "_" + game_publisher + "_" + area_mini_name + "_" + plat_mini_name + "_" + "bf"

    elif game_type == "log":
        app_dir = project + "_" + game_publisher + "_" + area_mini_name + "_" + plat_mini_name + "_" + "log"

    elif game_type == "gm":
        app_dir = project + "_" + game_publisher + "_" + area_mini_name + "_" + plat_mini_name + "_" + "gm"

    elif game_type == "login":
        app_dir = project + "_" + game_publisher + "_" + area_mini_name + "_" + plat_mini_name + "_" + "login"

    area_name = host.objects.get(project__mini_name=project,p_ip=p_ip).area.area_name

    if len(zone_id) == 0 or len(server_id) == 0:
        err_data = "服务器ID和大区ID不能为空"
    else:
        check_server_id = gameinfo.objects.filter(server_id=int(server_id),area__mini_name=area_mini_name,platform__mini_name=plat_mini_name)
        if len(check_server_id) != 0:
            err_data = "服务器ID: %s 在%s平台下重复了！" % (server_id,plat_mini_name)
        
    return render_to_response('inc/game_deploy_check.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def inc_add_gameinfo(request):
    project = request.GET.get("project")
    p_ip = request.GET.get("p_ip")
    s_ip = request.GET.get("s_ip")
    app_dir = request.GET.get("app_dir")
    server_id = request.GET.get("server_id")
    db_ip = request.GET.get("db_ip")
    open_time = request.GET.get("date")
    area_name = request.GET.get("area_name")
    game_type = request.GET.get("game_type")
    server_name = request.GET.get("server_name")
    zone_id = request.GET.get("zone_id")
    platform = host.objects.get(project__mini_name=project,p_ip=p_ip).platform.plat_name
    plat_mini_name = host.objects.get(project__mini_name=project,p_ip=p_ip).platform.mini_name
    use = host.objects.get(project__mini_name=project,p_ip=p_ip).use.all()
    if len(use) == 1:
        for i in use: use_name = i
    else:
        err_data = "游戏服用途必须唯一！"

    if game_type == "online" or game_type == "test":
        game_id = gameinfo.objects.filter(project__mini_name=project,p_ip=p_ip).count()
        if game_id >= 0:
            game_port = 10100 + int(game_id)
        else:
            game_port = 10100

    elif game_type == "fight":
        game_id = gameinfo.objects.filter(project__mini_name=project,p_ip=p_ip).count()
        game_port = 10300 + int(game_id)*10
        db_ip = "0.0.0.0"
    elif game_type == "log":
        game_port = 9121
        db_ip = "0.0.0.0"
    elif game_type == "gm":
        game_port = 9121
    elif game_type == "login":
        game_port = 10002

    try:
        area_id = area_type.objects.get(area_name=area_name)
        use_id = server_use.objects.get(use_name=use_name)
        project_id = Project.objects.get(mini_name=project)
        platform_id = platform_type.objects.get(plat_name=platform)
        game_count = gameinfo.objects.filter(project__mini_name=project,p_ip=p_ip).count() + 1
        if game_type == "online":
            start_time = open_time.replace("-","/")
            plat_mini_name = host.objects.get(project__mini_name=project,p_ip=p_ip).platform.mini_name
            add_serverlist = ServerList(area_name=area_name,platform=plat_mini_name,server_name=server_name,server_id=server_id,
                                    p_ip=p_ip,isopen="false",status=0,port=game_port,open_time=start_time,zone_id=zone_id)
            add_serverlist.save()
        add_game = gameinfo(project=project_id,area=area_id,platform=platform_id,use=use_id,p_ip=p_ip,
                            s_ip=s_ip,db_ip=db_ip,game_port=int(game_port),app_dir=app_dir,open_time=open_time,
                            server_id=int(server_id),server_name=server_name)
        add_game.save()

        #更新开服数量
        upcount = host.objects.filter(p_ip=p_ip)
        upcount.update(game_count=game_count)

        return HttpResponseRedirect("/inc/game_info/?project=%s&area=%s&platform=%s"%(project,area_name,plat_mini_name))

    except Exception,e:
        err_data = "%s,添加失败，Error:%s" % (p_ip,e)
        return render_to_response('inc/game_deploy_check.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def inc_install_process(request):

    project = request.GET.get("project")
    p_ip = request.GET.get("p_ip")
    s_ip = request.GET.get("s_ip")
    app_dir = request.GET.get("app_dir")
    server_id = request.GET.get("server_id")
    db_ip = request.GET.get("db_ip")
    open_time = request.GET.get("date")
    area_name = request.GET.get("area_name")
    game_type = request.GET.get("game_type")
    server_name = request.GET.get("server_name")
    zone_id = request.GET.get("zone_id")
    plat_name = request.GET.get("platform")
    use = host.objects.get(project__mini_name=project,p_ip=p_ip).use.all()
    ssh_port = host.objects.get(project__mini_name=project,p_ip=p_ip).port
    area_mini_name = area_type.objects.get(area_name=area_name).mini_name

    if len(use) == 1:
        for i in use: use_name = i
    else:
        err_data = "游戏服用途必须唯一！"

    #print project,p_ip,s_ip,db_ip,app_dir,server_id,db_ip,open_time,area_mini_name,game_type,server_name,zone_id,use_name,plat_name

    #安装信息字典
    gameinfodic = {}
    #添加监控（留空）

    gameinfodic.setdefault('p_ip',p_ip)
    gameinfodic.setdefault('server_id',server_id)
    gameinfodic.setdefault('db_ip',db_ip)
    gameinfodic.setdefault('app_dir',app_dir)
    gameinfodic.setdefault('plat_name',plat_name)
    gameinfodic.setdefault('server_name',server_name)
    gameinfodic.setdefault('area_mini_name',area_mini_name)
    gameinfodic.setdefault('ssh_port',ssh_port)
    # 游戏服安装
    if game_type == "online":
        #模版服务器，每个大区第一个服务器
        template_app_dir = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=plat_name,use__use_name="游戏服").order_by("server_id")[0].app_dir
        template_p_ip = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=plat_name,use__use_name="游戏服").order_by("server_id")[0].p_ip
        template_db_ip = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=plat_name,use__use_name="游戏服").order_by("server_id")[0].db_ip
        gameinfodic.setdefault("template_app_dir",template_app_dir)
        gameinfodic.setdefault("template_p_ip",template_p_ip)
        gameinfodic.setdefault("template_db_ip",template_db_ip)

        #判断是否一服多开
        game_id = gameinfo.objects.filter(project__mini_name=project,p_ip=p_ip).count()
        if game_id >= 0:
            game_port = 10100 + int(game_id)
        else:
            game_port = 10100
        gameinfodic.setdefault('game_port',game_port)
        #添加到区服列表
        add_serverlist = ServerList(area_name=area_name,platform=plat_name,server_name=server_name,server_id=server_id,
                                    p_ip=p_ip,isopen="false",status=0,port=game_port,open_time=open_time,zone_id=zone_id)
        add_serverlist.save()
        #开始执行安装任务
        tasks.game_install_func.delay(gameinfodic)
    # 战场服安装
    elif game_type == "fight":
        template_app_dir = gameinfo.objects.get(area__area_name=area_name,platform__mini_name=plat_name,use__use_name="战场服",server_id=0).app_dir
        template_p_ip = gameinfo.objects.get(area__area_name=area_name,platform__mini_name=plat_name,use__use_name="战场服",server_id=0).p_ip
        gameinfodic.setdefault("template_app_dir",template_app_dir)
        gameinfodic.setdefault("template_p_ip",template_p_ip)
        check_bf_count = gameinfo.objects.filter(p_ip=p_ip).count()
        game_port = 10300 + check_bf_count * 10
        bf_client_port = game_port + 1
        gameinfodic.setdefault('game_port1',game_port)
        gameinfodic.setdefault('game_port2',bf_client_port)
        tasks.bfserver_install_func.delay(gameinfodic)

    # 游戏服信息入库
    try:
        area_id = area_type.objects.get(area_name=area_name)
        use_id = server_use.objects.get(use_name=use_name)
        project_id = Project.objects.get(mini_name=project)
        platform_id = platform_type.objects.get(mini_name=plat_name)
        game_count = gameinfo.objects.filter(project__mini_name=project,p_ip=p_ip).count() + 1

        add_game = gameinfo(project=project_id,area=area_id,platform=platform_id,use=use_id,p_ip=p_ip,
                            s_ip=s_ip,db_ip=db_ip,game_port=int(game_port),app_dir=app_dir,open_time=open_time,
                            server_id=int(server_id),server_name=server_name)
        add_game.save()

        #更新开服数量
        upcount = host.objects.filter(p_ip=p_ip)
        upcount.update(game_count=game_count)
    except Exception,e:
        err_data = "%s,添加游戏信息到GameInfo失败，Error:%s" % (p_ip,e)

    return HttpResponseRedirect("/inc/inc_process_status/?gameserver=%s"% app_dir)

@login_required
@PermissionVerify()
def inc_process_status(request):
    header_title,nav,tip= "装服执行过程","游戏项目管理","装服执行过程"
    gameserver = request.GET.get("gameserver")
    action = request.GET.get("action")
    cmd = "cat /tmp/inc/%s_install.log" % gameserver
    cmd_status,cmd_out = commands.getstatusoutput(cmd)

    if action == "1":
        return render_to_response('inc/inc_install_process_status.html',locals(),context_instance=RequestContext(request))
    else:
        return render_to_response('inc/inc_install_process.html',locals(),context_instance=RequestContext(request))