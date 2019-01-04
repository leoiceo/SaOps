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

@login_required
@PermissionVerify()
def game_info(request):
    header_title,nav,tip= "游戏服管理","游戏项目管理","游戏服管理"
    project = "inc"
    area_name = request.GET.get("area")
    platform = request.GET.get("platform")
    game_type = request.GET.get("game_type")
    status = request.GET.get("status")
    if area_name is None:
        area_name = "国内"
    if platform is None:
        platform = "android"
    area_mini_name = area_type.objects.get(area_name=area_name).mini_name
    zone = area_name
    if game_type == "qc":
        menu = gameinfo.objects.filter(project__mini_name=project,area__area_name=area_name,platform__mini_name=platform,use__use_name="测试服")
    elif game_type == "ts":
        menu = gameinfo.objects.filter(project__mini_name=project,area__area_name=area_name,platform__mini_name=platform,use__use_name="提审服")
    else:
        if status is None:
            menu = gameinfo.objects.filter(project__mini_name=project,area__area_name=area_name,platform__mini_name=platform).exclude(use__use_name="测试服").exclude(use__use_name="提审服")
        else:
            menu = gameinfo.objects.filter(project__mini_name=project,area__area_name=area_name,platform__mini_name=platform,status=status).exclude(use__use_name="测试服").exclude(use__use_name="提审服")

    #区域和平台
    return render_to_response('inc/game_info.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def gameinfo_edit(request):
    len_table = request.GET.get("len_table")
    for i in range(int(len_table)):
        app_dir_id = "editable[" + str(i) + "][app_dir_id]"
        server_name = "editable[" + str(i) + "][server_name]"
        game_port = "editable[" + str(i) + "][game_port]"
        app_dir = "editable[" + str(i) + "][app_dir]"
        server_id = "editable[" + str(i) + "][server_id]"

        app_dir_id = request.GET.get(app_dir_id).strip()
        app_olddir,serv_oldid = app_dir_id.split("+")

        server_name = request.GET.get(server_name).strip()
        game_port = request.GET.get(game_port).strip()
        app_dir = request.GET.get(app_dir).strip()
        server_id = request.GET.get(server_id).strip()
        upgameinfo = gameinfo.objects.filter(app_dir=app_olddir,server_id="%s"%serv_oldid)
        upgameinfo.update(server_name=server_name,game_port=int(game_port),app_dir=app_dir,server_id=int(server_id))

    return HttpResponseRedirect(reverse('inc_game_info'))

@login_required
@PermissionVerify()
def game_crontrol(request):
    header_title,nav,tip= "游戏服管理","游戏项目管理","游戏服管理"
    project = "inc"
    game_list = request.POST.getlist('subcheck')
    action = request.POST.get('switch') #开关,操作选项
    area_name = request.GET.get('area')
    platform = request.GET.get("platform")

    #print action,area_name,platform,game_list,"=="*20
    result = []
    game_info = []

    #开始游戏服
    if action == "1":
        zone = "开启游戏服"
        for game_id in game_list:
            single_game  = {}
            p_ip,app_dir,server_id = game_id.split('+')
            game_use = gameinfo.objects.get(p_ip=p_ip,app_dir=app_dir,server_id=server_id,platform__mini_name=platform).use.use_name
            check_time = time.strftime("%Y-%m-%d %H:%M:%S")
            single_game.setdefault("server_ip",p_ip)
            single_game.setdefault("app_dir",app_dir)
            single_game.setdefault("server_id",server_id)
            single_game.setdefault("game_use",game_use)
            single_game.setdefault("platform",platform)
            game_info.append(single_game)
            result.append("执行开启中,请查看服务器状态...")
            gamestats = gameinfo.objects.filter(p_ip=p_ip,app_dir=app_dir,server_id=server_id,platform__mini_name=platform)
            gamestats.update(check_time=check_time,status=1)
        tasks.gameserver_crt_func.delay(game_info,"open")
        return render_to_response('inc/game_crontrol.html',locals(),context_instance=RequestContext(request))

    elif action == "2":
        zone = "关闭游戏服"
        for game_id in game_list:
            single_game = {}
            p_ip,app_dir,server_id = game_id.split('+')
            game_use = gameinfo.objects.get(p_ip=p_ip,app_dir=app_dir,server_id=server_id,platform__mini_name=platform).use.use_name
            check_time = time.strftime("%Y-%m-%d %H:%M:%S")
            single_game.setdefault("server_ip",p_ip)
            single_game.setdefault("app_dir",app_dir)
            single_game.setdefault("server_id",server_id)
            single_game.setdefault("game_use",game_use)
            single_game.setdefault("platform",platform)
            game_info.append(single_game)
            result.append("执行关闭中,请查看服务器状态...")
            gamestats = gameinfo.objects.filter(p_ip=p_ip,app_dir=app_dir,server_id=server_id,platform__mini_name=platform)
            gamestats.update(check_time=check_time,status=0)
        tasks.gameserver_crt_func.delay(game_info,"close")
        return render_to_response('inc/game_crontrol.html',locals(),context_instance=RequestContext(request))

    elif action == "3":
        '''
        删除游戏服和目录
        '''
        running_list = []
        delete_time = int(time.time())
        for game_id in game_list:
            single_game = {}
            p_ip,app_dir,server_id = game_id.split('+')
            game_status = gameinfo.objects.get(p_ip=p_ip,app_dir=app_dir,server_id=server_id,platform__mini_name=platform).status
            if int(game_status) > 0:
                running_list.append(app_dir)
            else:
                game_use = gameinfo.objects.get(p_ip=p_ip,app_dir=app_dir,server_id=server_id,platform__mini_name=platform).use.use_name
                db_ip = gameinfo.objects.get(p_ip=p_ip,app_dir=app_dir,server_id=server_id,platform__mini_name=platform).db_ip
                single_game.setdefault("server_ip",p_ip)
                single_game.setdefault("app_dir",app_dir)
                single_game.setdefault("server_id",server_id)
                single_game.setdefault("db_host",db_ip)
                single_game.setdefault("platform",platform)
                single_game.setdefault("delete_time",delete_time)
                game_info.append(single_game)

                #装服数据量
                game_count = gameinfo.objects.filter(project__mini_name=project,p_ip=p_ip).count()
                up_host = host.objects.filter(p_ip=p_ip)
                up_host.update(game_count=game_count)

                del_gameinfo = gameinfo.objects.filter(p_ip=p_ip,app_dir=app_dir,server_id=server_id,platform__mini_name=platform)
                del_gameinfo.delete()
                del_log = GameDropLog(area_name=area_name,platform=platform,p_ip=p_ip,delete_time=delete_time,
                                      db_ip=db_ip,server_name=app_dir,status="0.0%",log="游戏服正在删除中...")
                del_log.save()
        tasks.game_drop_func.delay(game_info)
        if len(running_list) == 0:
            return HttpResponseRedirect('/inc/gamedrop_process/?project=%s&area=%s&platform=%s&delete_time=%s'%(project,area_name,platform,delete_time))
        else:
            runinfo = ','.join(running_list)
            return HttpResponseRedirect('/inc/gamedrop_process/?project=%s&area=%s&platform=%s&runinfo=%s&delete_time=%s'%(project,area_name,platform,runinfo,delete_time))

    elif action == "4":
        '''
        停服清档
        '''
        for game_id in game_list:
            single_game = {}
            p_ip,app_dir,server_id = game_id.split('+')
            game_use = gameinfo.objects.get(p_ip=p_ip,app_dir=app_dir,server_id=server_id,platform__mini_name=platform).use.use_name
            db_ip = gameinfo.objects.get(p_ip=p_ip,app_dir=app_dir,server_id=server_id,platform__mini_name=platform).db_ip
            single_game.setdefault("server_ip",p_ip)
            single_game.setdefault("app_dir",app_dir)
            single_game.setdefault("server_id",server_id)
            single_game.setdefault("game_use",game_use)
            single_game.setdefault("db_host",db_ip)
            single_game.setdefault("platform",platform)
            game_info.append(single_game)
            with open("/tmp/inc/clear_game.log","w") as f:
                f.write("正在清档")
        tasks.gameserver_crt_func.delay(game_info,"clear")
        return HttpResponseRedirect('/inc/clear_gamedb/?platform=%s&area=%s'%(platform,area_name))

    elif action == "5":
        '''
        游戏服备份
        '''
        clear_history = BackupProcess.objects.filter(platform=platform)
        clear_history.delete()

        for game_id in game_list:
            single_game = {}
            p_ip,app_dir,server_id = game_id.split('+')
            game_use = gameinfo.objects.get(p_ip=p_ip,app_dir=app_dir,server_id=server_id,platform__mini_name=platform).use.use_name
            if game_use == "战场服" or game_use == "数据服":
                pass
            else:
                db_ip = gameinfo.objects.get(p_ip=p_ip,app_dir=app_dir,server_id=server_id,platform__mini_name=platform).db_ip
                single_game.setdefault("server_ip",p_ip)
                single_game.setdefault("app_dir",app_dir)
                single_game.setdefault("server_id",server_id)
                single_game.setdefault("game_use",game_use)
                single_game.setdefault("db_host",db_ip)
                single_game.setdefault("platform",platform)
                game_info.append(single_game)
                back = BackupProcess(platform=platform,p_ip=p_ip,server_name=app_dir,db_ip=db_ip,status="0.0%",log="备份正在进行中...")
                back.save()
        tasks.backup_func.delay(game_info)
        return HttpResponseRedirect('/inc/backup_process/?project=%s&platform=%s'%(project,platform))

    elif action == "6":
        '''
        删除游戏服信息
        '''
        server_list = []
        for game_id in game_list:
            p_ip,app_dir,server_id = game_id.split('+')
            server_list.append(app_dir)
            del_gameinfo = gameinfo.objects.filter(p_ip=p_ip,server_id=server_id,platform__mini_name=platform)
            del_gameinfo.delete()

            game_count = gameinfo.objects.filter(project__mini_name=project,p_ip=p_ip).count()
            up_host = host.objects.filter(p_ip=p_ip)
            up_host.update(game_count=game_count)

        log = "%s 信息已删除"%(','.join(server_list))
        return HttpResponseRedirect('/inc/game_info/?project=%s&area=%s&platform=%s'%(project,area_name,platform))


@login_required
@PermissionVerify()
def clear_gamedb(request):
    header_title,nav,tip= "游戏服清档日志","游戏项目管理","游戏服清档日志"
    project = "inc"
    platform = request.GET.get("platform")
    area_name = request.GET.get("area")
    action = request.GET.get("action")
    zone = area_name
    cmd = "cat /tmp/inc/clear_game.log"
    cmd_status,cmd_result = commands.getstatusoutput(cmd)
    if action == "1":
        return render_to_response("inc/clear_gamedb_status.html",locals(),context_instance=RequestContext(request))
    else:
        return render_to_response("inc/clear_gamedb.html",locals(),context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def gamedrop_process(request):
    header_title,nav,tip= "删除游戏服日志","游戏服管理","删除游戏服日志"
    project = request.GET.get("project")
    area_name = request.GET.get("area")
    zone = area_name
    platform = request.GET.get("platform")
    runinfo = request.GET.get("runinfo")
    delete_time = request.GET.get("delete_time")
    action = request.GET.get("action")

    menu = GameDropLog.objects.filter(delete_time=delete_time,area_name=area_name,platform=platform)
    if action == "1":
        return render_to_response("inc/game_drop_status.html",locals(),context_instance=RequestContext(request))
    else:
        return render_to_response("inc/game_drop.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def graph_status(request):
    header_title,nav,tip= "游戏服状态图象","游戏服管理","游戏服状态图象"
    project = "inc"
    area_name = request.GET.get('area')
    platform = request.GET.get("platform")

    if area_name is None:
        area_name = "国内"
    if platform is None:
        platform = "android"
    zone = area_name
    #区域和平台

    count_num = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=platform).exclude(
        use__use_name="提审服").exclude(use__use_name="测试服").count()
    up_num = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=platform,status=1).exclude(
        use__use_name="提审服").exclude(use__use_name="测试服").count()
    down_num = gameinfo.objects.filter(area__area_name=area_name,platform__mini_name=platform,status=0).exclude(
        use__use_name="提审服").exclude(use__use_name="测试服").count()

    return render_to_response("inc/graph_status.html",locals(),context_instance=RequestContext(request))