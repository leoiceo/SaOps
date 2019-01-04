#!/usr/bin/python
#_*_coding:utf-8_*_
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from manager.views.permission import *
import urllib2,json
from cmdb import settings
from manager.myauth import *
from hosts.models import *
from hosts import tasks
from scripting.models import *
from multitask.models import *
import commands,shutil,time,os


@login_required
@PermissionVerify()
def iplookup(request):
    header_title,nav,tip,zone= "IP地址查询","搜索","IP归属地","查询结果"
    ip = request.GET.get("search")
    if ip is None or ip == "None":
        pass
    else:
        try:
            url = 'http://apis.baidu.com/apistore/iplookupservice/iplookup?ip=%s'%ip
            req = urllib2.Request(url)
            req.add_header("apikey", "6f5140b842fccae1620ebb1c3d25b405")
            resp = urllib2.urlopen(req)
            content = resp.read()
            content = json.loads(content)
            if(content):
                data = content["retData"]
        except Exception,e:
            error = "可能是查询接口失效了. %s" %e
    return render_to_response("hosts/iplookup.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def web_ssh(request):
    header_title,nav,tip= "Web SSH","运维工具","Web SSH"


    return render_to_response("hosts/web_ssh.html",locals(),context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def init_hosts(request):
    header_title, nav, tip = "主机初始化", "权限管理", "主机初始化"

    project = request.GET.get("project")
    # 设置已初始化
    action = request.GET.get("action")
    script_name = request.POST.get("script_name")
    operator = UserProfile.objects.get(email="%s" % request.user).name

    if action == "set_host_init":
        choice_host = request.POST.getlist("choice_host")
        for h in choice_host:
            up_host = host.objects.filter(p_ip="%s" % h)
            up_host.update(host_init=1)
        return HttpResponseRedirect(reverse('init_hosts'))

    choice_host = request.POST.getlist("choice_host")

    if len(choice_host) == 0:

        if project is None:
            project = "09games"

        host_info = host.objects.filter(project__mini_name=project).order_by("host_init")
        script_list = ScriptsManage.objects.filter(project__mini_name=project)

        return render_to_response("hosts/init_hosts.html", locals(), context_instance=RequestContext(request))
    else:
        try:
            public_key = KeyManager.objects.get(project__mini_name=project).public_key
        except:
            error = "请先添加该相目的权限信息及密钥"
            return render_to_response("hosts/init_hosts.html", locals(), context_instance=RequestContext(request))

        all_hosts = []
        start_time = int(time.time())
        for h in choice_host:
            host_dict = {}
            port = host.objects.get(p_ip=h).port
            passwd = host.objects.get(p_ip=h).login_pass
            if passwd is not None:
                if '$' in passwd:
                    passwd = passwd.split('$')
                else:
                    passwd = passwd
            host_dict.setdefault("host", h)
            host_dict.setdefault("port", port)
            host_dict.setdefault("passwd", passwd)
            host_dict.setdefault("pubkey", public_key)
            write_log = ScriptExeclog(project=project, p_ip=h, script_name=script_name, status="5.0%", log="准备传送脚本到服务器",
                                      start_time=start_time, operator=operator)
            write_log.save()
            all_hosts.append(host_dict)

        # 执行初始化任务
        tasks.init_hosts.delay(all_hosts, script_name,project,start_time)
        status_info = ScriptExeclog.objects.filter(start_time=start_time)
        return render_to_response('multitask/exec_script_process.html', locals(),context_instance=RequestContext(request))

        #host_process = ','.join(choice_host)
        #return render_to_response("hosts/init_hosts.html", locals(), context_instance=RequestContext(request))
        #return HttpResponseRedirect("/perm/init_hosts_status/?host_process=%s&project=%s" % (host_process, project),locals())


@login_required
@PermissionVerify()
def init_dbs(request):
    header_title, nav, tip = "数据库初始化", "权限管理", "数据库初始化"
    project = request.GET.get("project")
    # 设置已初始化
    action = request.GET.get("action")
    script_name = request.POST.get("script_name")
    db_passwd = request.POST.get("db_passwd")
    operator = UserProfile.objects.get(email="%s" % request.user).name

    if action == "set_db_init":
        choice_host = request.POST.getlist("choice_host")
        for h in choice_host:
            up_host = host.objects.filter(p_ip="%s" % h)
            up_host.update(db_init=1)
        return HttpResponseRedirect(reverse('init_dbs'))

    choice_host = request.POST.getlist("choice_host")

    if len(choice_host) == 0:

        if project is None:
            project = "09games"

        db_info = host.objects.filter(project__mini_name=project).exclude(db_ip="none").order_by("db_init")

        for dbs in db_info:
            check_db = host.objects.filter(db_ip=dbs.db_ip)
            for db_status in check_db:
                if db_status.db_init == 1:
                    check_db.update(db_init=1)
        info = "部分重复使用的DB，已经自动初始化完毕"
        script_list = ScriptsManage.objects.filter(project__mini_name=project)

        return render_to_response("hosts/init_dbs.html", locals(), context_instance=RequestContext(request))
    else:
        start_time = int(time.time())
        server_info = []
        for p_ip in choice_host:
            server_dic = {}
            db_ip = host.objects.get(p_ip=p_ip).db_ip
            port = host.objects.get(p_ip=p_ip).port
            if "$" in db_passwd:
                db_pass = db_passwd.split("$")
            else:
                db_pass = db_passwd
            server_dic.setdefault("db_ip", db_ip)
            server_dic.setdefault("p_ip", p_ip)
            server_dic.setdefault("passwd", db_pass)
            server_dic.setdefault("port", port)
            # 写入日志
            write_log = ScriptExeclog(project=project, p_ip=p_ip, script_name=script_name, status="5.0%", log="准备传送脚本到服务器",
                                      start_time=start_time, operator=operator)
            write_log.save()
            server_info.append(server_dic)
        # 执行初始化任务
        tasks.init_dbs.delay(server_info, script_name, project, start_time)
        status_info = ScriptExeclog.objects.filter(start_time=start_time)
        return render_to_response('multitask/exec_script_process.html', locals(),context_instance=RequestContext(request))




            #return render_to_response("hosts/init_dbs.html", locals(), context_instance=RequestContext(request))


'''
@login_required
@PermissionVerify()
def init_hosts_status(request):
    header_title,nav,tip= "服务器初始化","游戏项目管理","初始化过程"
    host_process = request.GET.get("host_process")
    project = request.GET.get("project")
    host_info = host_process.split(',')
    host_list = []
    try:
        for host in host_info:
            host_dict = {}
            info = "[%s]正在生成初始化日志,请耐心等待...." % host
            host_dict.setdefault("info",info)
            if os.path.exists("/tmp/%s/host_init_%s.log"% (project,host)):
                cmd = "cat /tmp/%s/host_init_%s.log"% (project,host)
                cmd_status,init_log = commands.getstatusoutput(cmd)
                host_dict.setdefault("host",host)
                host_dict.setdefault("init_log",init_log)
            if os.path.exists("/tmp/%s/host_init_err_%s.log"%(project,host)):
                cmd = "cat /tmp/%s/host_init_err_%s.log"%(project,host)
                cmd_status,init_err_log = commands.getstatusoutput(cmd)
                host_dict.setdefault("init_err_log",init_err_log)
            host_list.append(host_dict)
    except:
        info = "正在生成初始化日志,请耐心等待...."

    return render_to_response("hosts/init_hosts_status.html",locals(),context_instance=RequestContext(request))
'''