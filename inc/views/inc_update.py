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
from manager.common import *
from inc.models import *
import os,sys,commands,time
from datetime import date
import shutil

@login_required
@PermissionVerify()
def update_file(request):
    header_title,nav,tip= "服务端更新","服务端更新","选择平台"
    project = "inc"
    area_name = request.GET.get("area")

    if area_name is None:
        area_name = "国内"

    zone = area_name
    area_info = []
    gameinfo_obj = gameinfo.objects.all()

    for game in gameinfo_obj:
        game_area_name = game.area.area_name
        if game_area_name not in area_info:
            area_info.append(game_area_name)
    area_info=list(set(area_info))

    platform_menu = gameinfo.objects.filter(project__mini_name=project,area__area_name=area_name).values("platform").distinct()
    plat_dict = {}

    for plat in platform_menu:
        ver_list = []
        plat_mini_name = platform_type.objects.get(id=plat["platform"]).mini_name
        version = gameinfo.objects.filter(platform__mini_name=plat_mini_name,area__area_name=area_name,use__use_name="游戏服")[0].version
        ver_list.append(version)
        last_version = gameinfo.objects.filter(platform__mini_name=plat_mini_name,area__area_name=area_name,use__use_name="游戏服")[0].last_version
        ver_list.append(last_version)
        plat_dict[plat_mini_name] = ver_list

    print plat_dict

    return render_to_response("inc/update_file.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def update_file_info(request):
    header_title,nav,tip= "服务端更新","游戏服更新","选择服务器"
    project = "inc"
    area_name = request.GET.get("area")
    zone = area_name
    #正式、测试、提审服
    game_type = request.GET.get("game_type")

    if request.method == "POST":
        platform = request.POST.get("platform")
        gversion = request.POST.get("gversion")
    else:
        platform = request.GET.get("platform")
        gversion = request.GET.get("gversion")

    print area_name,platform
    if game_type == "正式服" or game_type is None:
        game_info = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=platform).exclude(
            use__use_name="测试服").exclude(
            use__use_name="提审服").order_by("server_id")
    elif game_type == "测试服":
        game_info = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=platform,use__use_name="测试服")
    elif game_type == "提审服":
        game_info = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=platform,use__use_name="提审服")

    jump_host = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="中转服").p_ip
    jump_port = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="中转服").port

    cmd = "svn info -r %s /data/scripts/inc/rep/Release"%gversion
    info_log,err_log = remote_run(host=jump_host,port=jump_port,keyfile=settings.INC_KEY,username="root",cmd=cmd,password=None,timeout=None)
    if len(info_log) != 0:
        info_list = info_log.split('\n')
    if len(err_log) != 0:
        err_list = err_log.split('\n')
    return render_to_response("inc/update_file_info.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def update_file_status(request):
    header_title,nav,tip= "服务端更新状态","游戏服更新","服务端更新状态"
    project = "inc"
    area_name = request.GET.get("area")
    platform = request.GET.get("platform")
    gversion = request.GET.get("gversion")
    method = request.GET.get("method")
    gamelist = request.POST.getlist("subcheck")
    jump_host = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="中转服").p_ip
    jump_port = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="中转服").port

    update_time = int(time.time())
    gameinfo_list = []
    for game in gamelist:
        gameinfo_dict = {}
        ip,gamedir,serverid = game.split("+")
        gameinfo_dict.setdefault("game_dir",gamedir)
        gameinfo_dict.setdefault("game_ip",ip)
        if gameinfo_dict not in gameinfo_list:
            gameinfo_list.append(gameinfo_dict)
            current_version = gameinfo.objects.filter(platform__mini_name=platform,area__area_name=area_name,use__use_name="游戏服")[0].version
            update_gameinfo = gameinfo.objects.filter(platform__mini_name=platform,area__area_name=area_name,
                                                      p_ip=ip,app_dir=gamedir,server_id=serverid)
            update_gameinfo.update(version=gversion,last_version=current_version)

            write_log = UpdateGameLog(area_name=area_name,platform=platform,p_ip=ip,server_name=gamedir,version=gversion,method=method,
                                      update_time=update_time,status="5.0%",log="开始更新服务端版本")
            write_log.save()

    tasks.game_update_func.delay(gameinfo_list,jump_host,jump_port,gversion,method,platform,update_time)
    status_info = UpdateGameLog.objects.filter(update_time=update_time)
    return render_to_response("inc/update_file_status.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def update_config(request):
    header_title,nav,tip= "配置文件更新","游戏服更新","选择平台"
    project = "inc"
    area_name = request.GET.get("area")

    if area_name is None:
        area_name = "国内"

    zone = area_name
    area_info = []
    gameinfo_obj = gameinfo.objects.all()

    for game in gameinfo_obj:
        game_area_name = game.area.area_name
        if game_area_name not in area_info:
            area_info.append(game_area_name)
    area_info=list(set(area_info))

    platform_menu = gameinfo.objects.filter(project__mini_name=project,area__area_name=area_name).values("platform").distinct()
    plat_list = []

    for plat in platform_menu:
        plat_mini_name = platform_type.objects.get(id=plat["platform"]).mini_name
        plat_list.append(plat_mini_name)
    print plat_list,"-"*20
    #menu = gameinfo.objects.filter(project__pname="%s"%project,zone__zname="%s"%zone)
    return render_to_response("inc/update_config.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def update_config_info(request):
    header_title,nav,tip= "配置文件更新","游戏服更新","选择服务器和配置文件"
    area_name = request.GET.get("area")
    game_type = request.GET.get("game_type")

    if request.method == "POST":
        platform = request.POST.get("platform")
    else:
        platform = request.GET.get("platform")
    zone = area_name
    if game_type == "正式服" or game_type == None:
        game_info = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=platform).exclude(
            use__use_name="测试服").exclude(
            use__use_name="提审服").exclude(
            use__use_name="日志服").exclude(
            use__use_name="登陆服").exclude(
            use__use_name="GM服").order_by("server_id")
    elif game_type == "测试服":
        game_info = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=platform,use__use_name="测试服").order_by("server_id")
    else:
        game_info = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=platform,use__use_name="提审服").order_by("server_id")

    config_info = FileName.objects.all().exclude(name="mysql.db.start")

    return render_to_response("inc/update_config_info.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def update_config_status(request):
    header_title,nav,tip= "配置文件更新状态","配置文件更新","配置文件更新状态"
    area_name = request.GET.get("area")
    platform = request.GET.get("platform")
    filename = request.POST.getlist("filename")
    gamelist = request.POST.getlist("subcheck")
    project = "inc"
    zone = area_name

    jump_host = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="中转服").p_ip
    jump_port = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="中转服").port

    update_time = int(time.time())
    gameinfo_list = []
    for game in gamelist:
        gameinfo_dict = {}
        game_use,gamedir,serverid,game_ip = game.split("+")
        game_port = gameinfo.objects.get(p_ip=game_ip,server_id=serverid).game_port
        area_mini_name = gameinfo.objects.get(p_ip=game_ip,server_id=serverid).area.mini_name
        gameinfo_dict.setdefault('gamedir',gamedir)
        gameinfo_dict.setdefault('game_ip',game_ip)
        gameinfo_dict.setdefault('serverid',serverid)
        gameinfo_dict.setdefault('game_use',game_use)
        gameinfo_dict.setdefault('game_port',game_port)
        gameinfo_list.append(gameinfo_dict)

    write_log = UpdateConfigLog(area_name=area_name,platform=platform,p_ip=game_ip,server_name=gamedir,update_time=update_time,status="5.0%",log="开始更新配置文件")
    write_log.save()

    tasks.config_update_func.delay(gameinfo_list,filename,jump_host,jump_port,area_mini_name,platform,update_time)
    #前端日志
    status_info = UpdateConfigLog.objects.filter(update_time=update_time)

    return render_to_response("inc/update_config_status.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def update_sql(request):
    header_title,nav,tip= "上传SQL文件","游戏服更新","数据库更新"
    project = "inc"
    area_name = request.GET.get("area")
    platform = request.GET.get("platform")

    if area_name is None:
        area_name = "国内"
    if platform is None:
        platform = "android"
    zone = area_name
    #区域和平台
    inc_area_plat_info = {}
    info = gameinfo.objects.all()
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

    if request.method == "POST":
        upload_files = request.FILES.getlist('file[]', None)
        check_and_mkdir("%s/%s/%s/"% (settings.INC_SQL_DIR,project,platform))
        try:
            shutil.rmtree("%s/%s/%s/" % (settings.INC_SQL_DIR,project,platform))
            check_and_mkdir("%s/%s/%s/"% (settings.INC_SQL_DIR,project,platform))
        except Exception,e:
            print e
        for upload_file in upload_files:
            print upload_file.name
            with open("%s/%s/%s/%s"%(settings.INC_SQL_DIR,project,platform,upload_file.name),"w") as f:
                for chunk in upload_file.chunks():
                    f.write(chunk)
    return render_to_response("inc/update_sql.html",locals(),context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def update_sql_info(request):
    header_title,nav,tip= "选择服务器","游戏服更新","数据库更新"
    area_name = request.GET.get("area")
    game_type = request.GET.get("game_type")
    platform = request.GET.get("platform")
    project = "inc"
    zone = area_name

    if game_type == "线上服" or game_type == None:
        game_info = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=platform).exclude(
            use__use_name="测试服").exclude(
            use__use_name="提审服").exclude(
            use__use_name="日志服").exclude(
            use__use_name="战场服").order_by("server_id")
    elif game_type == "测试服":
        game_info = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=platform,use__use_name="测试服").order_by("server_id")
    else:
        game_info = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=platform,use__use_name="提审服").order_by("server_id")

    sqlinfo_dict = {}
    sql_dir = "%s/%s/%s/"% (settings.INC_SQL_DIR,project,platform)
    check_and_mkdir(sql_dir)
    sqlfile_list = os.listdir("%s"%(sql_dir))
    for sqlfile in sqlfile_list:
        cmd = "cat %s/%s | grep DROP;cat %s/%s | grep DELETE"%(sql_dir,sqlfile,sql_dir,sqlfile)
        cmd_status,cmd_result = commands.getstatusoutput(cmd)
        sqlinfo_dict.setdefault(sqlfile,cmd_result)
    return render_to_response("inc/update_sql_info.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def update_sql_status(request):
    header_title,nav,tip= "数据库更新状态","游戏服更新","数据库更新状态"
    project = "inc"
    area_name = request.GET.get("area")
    platform = request.GET.get("platform")
    gamelist = request.POST.getlist("subcheck")
    sql_list = os.listdir("%s/%s/%s"%(settings.INC_SQL_DIR,project,platform))

    jump_host = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="中转服").p_ip
    jump_port = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="中转服").port
    update_time = int(time.time())

    gameinfo_list = []
    for game in gamelist:
        gameinfo_dict = {}
        gamedir,game_ip,db_ip = game.split("+")
        gameinfo_dict.setdefault('gamedir',gamedir)
        gameinfo_dict.setdefault('game_ip',game_ip)
        gameinfo_dict.setdefault('db_ip',db_ip)
        gameinfo_list.append(gameinfo_dict)

        write_log = UpdateSqlLog(area_name=area_name,platform=platform,db_ip=db_ip,server_name=gamedir,update_time=update_time,status="5.0%",log="开始更新SQL")
        write_log.save()
        #执行更新SQL脚本 列表+中转+平台+更新文件+更新时间
    tasks.sql_update_func.delay(gameinfo_list,jump_host,jump_port,platform,sql_list,update_time)
    status_info = UpdateSqlLog.objects.filter(update_time=update_time)
    return render_to_response("inc/update_sql_status.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def update_process(request):
    """
    查看更新状态
    :param request:
    :return:
    """
    project = request.GET.get("project")
    update_type = request.GET.get("type")
    platform = request.GET.get("platform")
    update_time = request.GET.get("update_time")

    if update_type == "config_update":
        status_info = UpdateConfigLog.objects.filter(update_time=update_time)
        return render_to_response("inc/update_config_process.html",locals(),context_instance=RequestContext(request))

    elif update_type == "sql_update":
        status_info = UpdateSqlLog.objects.filter(update_time=update_time)
        return render_to_response("inc/update_sql_process.html",locals(),context_instance=RequestContext(request))

    elif update_type == "file_update":
        status_info = UpdateGameLog.objects.filter(update_time=update_time)
        return render_to_response("inc/update_file_process.html",locals(),context_instance=RequestContext(request))
