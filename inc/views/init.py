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
def host_init(request):
    header_title,nav,tip,zone= "服务器初始化","游戏项目管理","服务器初始化","国内"
    project = "inc"
    area_name = request.GET.get("zone")
    # 设置已初始化
    action = request.GET.get("action")
    if action == "set_host_init":
        choice_host = request.POST.getlist("choice_host")
        for h in choice_host:
            up_host = host.objects.filter(p_ip="%s"%h)
            up_host.update(host_init=1)
        return HttpResponseRedirect(reverse('inc_host_init'))

    if area_name is None:
        area_name = "国内"

    inc_area_info = []
    inc_area = host.objects.filter(project__mini_name=project)
    for i in inc_area:
        all = area_type.objects.get(area_name=i.area).area_name
        inc_area_info.append(all)
    # 当前项目地区列表，去重
    inc_area_info = list(set(inc_area_info))
    area_mini_name = area_type.objects.get(area_name=area_name).mini_name
    # 当前项目主机信息
    host_info = host.objects.filter(project__mini_name=project,area__area_name=area_name).exclude(use__use_name='中转服').order_by("host_init","id")

    public_key = []
    for key in os.listdir(settings.KEY_DIR):
        if not os.path.isfile("%s/%s"%(settings.KEY_DIR,key)):
            continue
        if "key" in key:
            continue
        public_key.append(key)
    user_key = request.POST.getlist("user_key")
    user_key_str = ''
    for keyname in user_key:
        with open("%s%s"%(settings.KEY_DIR,keyname)) as f:
            user_key_str += f.readline() + '\n'
    choice_host = request.POST.getlist("choice_host")
    if len(choice_host) == 0:
        return render_to_response("inc/host_init.html",locals(),context_instance=RequestContext(request))
    else:
        all_hosts = []
        for h in choice_host:
            host_dict = {}
            port = host.objects.get(p_ip=h).port
            passwd = host.objects.get(p_ip=h).login_pass
            if passwd is not None:
                if '$' in passwd:
                    passwd = passwd.split('$')
                else:
                    passwd = passwd
            uses = []
            use = host.objects.get(p_ip=h).use.all()
            for u in use: uses.append(u.use_name)
            uses = ','.join(uses)
            host_dict.setdefault("host",h)
            host_dict.setdefault("port",port)
            host_dict.setdefault("passwd",passwd)
            host_dict.setdefault("use",uses)
            host_dict.setdefault("area_name",area_mini_name)
            all_hosts.append(host_dict)
        # 执行初始化任务
        print all_hosts,user_key_str
        res = tasks.host_init_func.delay(all_hosts,user_key_str)
        host_process = ','.join(choice_host)

        return HttpResponseRedirect("/inc/host_init_process/?host_process=%s"% host_process,locals())
        #return render_to_response("inc/host_init.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def host_init_process(request):
    header_title,nav,tip= "服务器初始化","游戏项目管理","初始化过程"
    host_process = request.GET.get("host_process")
    host_info = host_process.split(',')
    host_list = []
    try:
        for host in host_info:
            host_dict = {}
            info = "[%s]正在生成初始化日志,请耐心等待...." % host
            host_dict.setdefault("info",info)
            if os.path.exists("/tmp/inc/host_init_%s.log"% host):
                cmd = "cat /tmp/inc/host_init_%s.log"% host
                cmd_status,init_log = commands.getstatusoutput(cmd)
                host_dict.setdefault("host",host)
                host_dict.setdefault("init_log",init_log)
            if os.path.exists("/tmp/inc/host_init_err_%s.log"% host):
                cmd = "cat /tmp/inc/host_init_err_%s.log"%host
                cmd_status,init_err_log = commands.getstatusoutput(cmd)
                host_dict.setdefault("init_err_log",init_err_log)
            host_list.append(host_dict)
    except:
        info = "正在生成初始化日志,请耐心等待...."

    return render_to_response("inc/host_init_process.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def see_init_script(request):
    header_title,nav,tip= "服务器初始化","游戏项目管理","查看初始化脚本"
    project = request.GET.get("project")
    area_name = request.GET.get("area")
    action = request.GET.get("action")
    mini_area_name = area_type.objects.get(area_name="%s"%area_name).mini_name

    if action == "save":
        code_text = request.POST.get("code_text")
        with open("%s/inc/host_init/%s/inc_init.sh"%(settings.BASH_DIR,mini_area_name),"w") as f:
            f.write(code_text)
        cmd = "dos2unix %s/inc/host_init/%s/inc_init.sh"%(settings.BASH_DIR,mini_area_name)
        os.system(cmd)
    with open("%s/inc/host_init/%s/inc_init.sh"%(settings.BASH_DIR,mini_area_name),"r") as f:
        info = f.read()

    return render_to_response("inc/see_init_script.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def db_init(request):
    header_title,nav,tip,zone= "数据库初始化","游戏项目管理","数据库初始化","国内"
    project = "inc"
    area_name = request.GET.get("zone")
    # 设置已初始化
    action = request.GET.get("action")
    if action == "set_db_init":
        choice_host = request.POST.getlist("choice_host")
        for h in choice_host:
            up_db = host.objects.filter(p_ip="%s"%h)
            up_db.update(db_init=1)
        return HttpResponseRedirect(reverse('inc_db_init'))

    if area_name is None:
        area_name = "国内"
    inc_area_info = []
    inc_area = host.objects.filter(project__mini_name=project)
    for i in inc_area:
        all = area_type.objects.get(area_name=i.area).area_name
        inc_area_info.append(all)

    # 当前项目地区列表，去重
    inc_area_info = list(set(inc_area_info))
    area_mini_name = area_type.objects.get(area_name=area_name).mini_name

    db_info = host.objects.filter(project__mini_name="%s"% project,area__area_name="%s"%area_name).exclude(db_ip='0.0.0.0').exclude(db_ip='').order_by("db_init")

    return render_to_response("inc/db_init.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def db_init_process(request):
    project = request.GET.get("project")
    area_name = request.GET.get("area")
    choice_host = request.POST.getlist("choice_host")
    db_passwd = request.POST.get("db_passwd")

    if "$" in db_passwd:
        db_pass = db_passwd.split("$")
    else:
        db_pass = db_passwd

    db_info = []
    db_dic = {}
    for h in choice_host:
        plat_type = host.objects.get(p_ip=h).platform.mini_name
        db_ipaddr = host.objects.get(p_ip=h).db_ip
        if plat_type != "qq":
            jump_host = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="中转服").p_ip
        else:
            jump_host = host.objects.get(project__mini_name=project,area__area_name=area_name,use__use_name="GM服",platform__mini_name=plat_type).p_ip

        db_dic.setdefault("db_ip",db_ipaddr)
        db_dic.setdefault("jump_host",jump_host)
        db_dic.setdefault("db_passwd",db_pass)
        db_info.append(db_dic)
    print db_info
    tasks.db_init_func.delay(db_info)

    return HttpResponseRedirect("/inc/db_init_status/?project=%s&area=%s" % (project,area_name))

@login_required
@PermissionVerify()
def db_init_status(request):
    header_title,nav,tip= "数据库初始化","游戏项目管理","初始化过程"
    project = request.GET.get("project")
    area_name = request.GET.get("area")
    action = request.GET.get("action")
    cmd = "cat /tmp/%s/db_init.log" % project
    cmd_status,cmd_out = commands.getstatusoutput(cmd)
    if action == "1":
        return render_to_response("inc/db_init_process_status.html",locals(),context_instance=RequestContext(request))
    else:
        return render_to_response("inc/db_init_process.html",locals(),context_instance=RequestContext(request))
