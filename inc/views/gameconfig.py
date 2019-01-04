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
from manager.common import *
from hosts.models import  *
from manager.myauth import *
from inc.models import *
import os,sys,commands

@login_required
@PermissionVerify()
def inc_conf_manage(request):
    header_title,nav,tip= "平台区域选择","游戏配置管理","平台区域选择"
    project = "inc"
    area_name = request.GET.get("area")
    platform = request.GET.get("platform")

    if area_name is None:
        area_name = "国内"
    if platform is None:
        platform = "android"
    zone = area_name
    area_info = []
    area_obj = gameinfo.objects.all().values("area").distinct()
    for area in area_obj:
        single_area = area_type.objects.get(id=area["area"]).area_name
        area_info.append(single_area)
    platform_dict = {}
    platform_obj = gameinfo.objects.all().values("platform").distinct()
    for plat in platform_obj:
        single_plat = platform_type.objects.get(id=plat["platform"]).mini_name
        single_plat_name = platform_type.objects.get(id=plat["platform"]).plat_name
        platform_dict[single_plat_name] = single_plat
    #print platform_dict
    return render_to_response('inc/inc_conf_manage.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def inc_conf_edit(request):
    header_title,nav,tip= "编辑模版配置","游戏配置管理","编辑模版配置"
    project = "inc"
    area_name = request.GET.get("area")
    zone = area_name
    plat_name = request.GET.get("platform")
    game_type = request.GET.get("game_type")

    gameserver = request.POST.get("gameserver")
    dbserver = request.POST.get("dbserver")
    bfserver = request.POST.get("bfserver")
    mysqldb = request.POST.get("mysqlcfg")

    area_mini_name = area_type.objects.get(area_name=area_name).mini_name
    plat_mini_name = platform_type.objects.get(plat_name=plat_name).mini_name

    if project is not None and area_name is not None and plat_name is not None:
        project_id = Project.objects.get(mini_name=project)
        area_id = area_type.objects.get(area_name=area_name)
        platform_id = platform_type.objects.get(plat_name=plat_name)

    if len(GameConfig.objects.filter(area__area_name=area_name,platform__plat_name=plat_name,gametype=game_type,filename__name="gameserver.start")) > 0:
        if gameserver is not None:
            cfg_obj = GameConfig.objects.filter(area__area_name=area_name,platform__plat_name=plat_name,gametype=game_type,filename__name="gameserver.start")
            cfg_obj.update(contents="%s"% gameserver.strip())
        gameserver_cfg = GameConfig.objects.get(area__area_name=area_name,platform__plat_name=plat_name,gametype=game_type,filename__name="gameserver.start").contents
    else:
        if gameserver is not None:
            filename_id = FileName.objects.get(name="gameserver.start")
            add_cfg = GameConfig(project=project_id,area=area_id,platform=platform_id,gametype=game_type,filename=filename_id,contents="%s"% gameserver.strip())
            add_cfg.save()
            return HttpResponseRedirect("/inc/inc_conf_edit/?&area=%s&platform=%s&game_type=%s"%(area_name,plat_name,game_type))

    if len(GameConfig.objects.filter(area__area_name=area_name,platform__plat_name=plat_name,gametype=game_type,filename__name="dbserver.start")) > 0:
        if dbserver is not None:
            cfg_obj = GameConfig.objects.filter(area__area_name=area_name,platform__plat_name=plat_name,gametype=game_type,filename__name="dbserver.start")
            cfg_obj.update(contents="%s"% dbserver.strip())
        dbserver_cfg = GameConfig.objects.get(area__area_name=area_name,platform__plat_name=plat_name,gametype=game_type,filename__name="dbserver.start").contents
    else:
        if dbserver is not None:
            filename_id = FileName.objects.get(name="dbserver.start")
            add_cfg = GameConfig(project=project_id,area=area_id,platform=platform_id,gametype=game_type,filename=filename_id,contents="%s"% dbserver.strip())
            add_cfg.save()
            return HttpResponseRedirect("/inc/inc_conf_edit/?&area=%s&platform=%s&game_type=%s"%(area_name,plat_name,game_type))

    if len(GameConfig.objects.filter(area__area_name=area_name,platform__plat_name=plat_name,gametype=game_type,filename__name="bfserver.start.0")) > 0:
        if bfserver is not None:
            cfg_obj = GameConfig.objects.filter(area__area_name=area_name,platform__plat_name=plat_name,gametype=game_type,filename__name="bfserver.start.0")
            cfg_obj.update(contents="%s"% bfserver.strip())
        bfserver_cfg = GameConfig.objects.get(area__area_name=area_name,platform__plat_name=plat_name,gametype=game_type,filename__name="bfserver.start.0").contents
    else:
        if bfserver is not None:
            filename_id = FileName.objects.get(name="bfserver.start.0")
            add_cfg = GameConfig(project=project_id,area=area_id,platform=platform_id,gametype=game_type,filename=filename_id,contents="%s"% bfserver.strip())
            add_cfg.save()
            return HttpResponseRedirect("/inc/inc_conf_edit/?&area=%s&platform=%s&game_type=%s"%(area_name,plat_name,game_type))

    if len(GameConfig.objects.filter(area__area_name=area_name,platform__plat_name=plat_name,gametype=game_type,filename__name="mysql.db.start")) > 0:
        if mysqldb is not None:
            cfg_obj = GameConfig.objects.filter(area__area_name=area_name,platform__plat_name=plat_name,gametype=game_type,filename__name="mysql.db.start")
            cfg_obj.update(contents="%s"% mysqldb.strip())
        mysql_cfg = GameConfig.objects.get(area__area_name=area_name,platform__plat_name=plat_name,gametype=game_type,filename__name="mysql.db.start").contents
    else:
        if mysqldb is not None:
            filename_id = FileName.objects.get(name="mysql.db.start")
            add_cfg = GameConfig(project=project_id,area=area_id,platform=platform_id,gametype=game_type,filename=filename_id,contents="%s"% mysqldb.strip())
            add_cfg.save()
            return HttpResponseRedirect("/inc/inc_conf_edit/?&area=%s&platform=%s&game_type=%s"%(area_name,plat_name,game_type))

    conf_info = GameConfig.objects.filter(area__area_name=area_name,platform__plat_name=plat_name,gametype=game_type)

    for conf in conf_info:
        check_and_mkdir("%s/%s/%s" % (settings.INC_CONF_DIR,area_mini_name,plat_mini_name))

        with open("%s/%s/%s/%s" % (settings.INC_CONF_DIR,area_mini_name,plat_mini_name,conf.filename.name),"w") as f:
            for content in conf.contents.encode("utf-8"):
                f.write(content)

    return render_to_response("inc/inc_conf_edit.html",locals(),context_instance=RequestContext(request))