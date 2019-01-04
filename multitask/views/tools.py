#!/usr/bin/python
#_*_coding:utf-8_*_
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from manager.views.permission import *
import urllib2,json,os
from cmdb import settings
from manager.myauth import *
from manager.common import *
from hosts.models import *
from multitask.models import *
import commands,shutil,time
from multitask import tasks
from scripting.models import *
from cmdb import cmdb_api


@login_required
@PermissionVerify()
def exec_cmds(request):
    header_title,nav,tip= "批量命令","批量任务","批量命令"
    project = request.GET.get("project")
    log = request.GET.get("log")
    error = request.GET.get("error")
    zone = project

    pro_info = cmdb_api.get_pro_info(request)

    if len(pro_info) == 0:
        log = "您的账号没有任何项目权限"

    if project is None:
        project = Project.objects.all()[0].mini_name

    else:
        host_info = host.objects.filter(project__mini_name=project,recover=0)
    return render_to_response('multitask/exec_cmds.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def exec_cmds_process(request):
    header_title,nav,tip= "批量命令状态","批量任务","批量命令状态"
    project = request.GET.get("project")
    bash_cmd = request.POST.get("bash_cmd")
    host_list = request.POST.getlist("host")
    operator = UserProfile.objects.get(email="%s"% request.user).name
    start_time = int(time.time())
    host_info = []

    danger_cmds = ['reboot','shutdown','rm -fr /' 'dd','test']

    if bash_cmd is None or host_list is None:
        log = "输入的指定不能为空!并选择要发送的服务器.."

        return HttpResponseRedirect('/multitask/exec_cmds/?project=%s&log=%s'%(project,log))

    elif bash_cmd in danger_cmds:
        log = "%s 是危险操作,请误批量执行" % bash_cmd
        return HttpResponseRedirect('/multitask/exec_cmds/?project=%s&error=%s' % (project, log))

    for p_ip in host_list:
        host_dict = {}

        write_log = CmdExecLog(project=project,p_ip=p_ip,cmd=bash_cmd,status="10.0%",log="开始执行",
                               total_time=0.00,start_time=start_time,operator=operator)
        write_log.save()

        host_port = host.objects.get(p_ip=p_ip).port
        host_project = host.objects.get(p_ip=p_ip).project.mini_name
        #host_system = host.objects.get(p_ip=p_ip).os_type
        #host_dict.setdefault("bash_cmd",pickle.dumps(bash_cmd))
        host_dict.setdefault("host",p_ip)
        host_dict.setdefault("host_port",host_port)
        host_dict.setdefault("project",host_project)
        #host_dict.setdefault("os_system",host_system)
        host_dict.setdefault("start_time",start_time)
        host_info.append(host_dict)

    tasks.exec_cmds_func.delay(host_info)
    status_info = CmdExecLog.objects.filter(start_time=start_time)
    return render_to_response('multitask/exec_cmds_process.html',locals(),context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def exec_cmds_status(request):
    header_title,nav,tip= "批量命令状态","批量任务","批量命令状态"
    start_time = request.GET.get("start_time")
    status_info = CmdExecLog.objects.filter(start_time=start_time)
    return render_to_response("multitask/exec_cmds_status.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def exec_cmds_result(request):

    start_time = request.GET.get("start_time")
    p_ip = request.GET.get("hosts")
    result = CmdExecLog.objects.get(start_time=start_time,p_ip=p_ip).result
    print result,"..."
    return HttpResponse(json.dumps(result), content_type='application/json')

@login_required
@PermissionVerify()
def file_trans(request):
    header_title,nav,tip= "文件分发","批量任务","文件分发"
    project = request.GET.get("project")
    log = request.GET.get("log")

    if request.method == "POST":
        upload_files = request.FILES.get('upload_file', None)
        with open("%s/%s"%(settings.FILE_TRANS_DIR,upload_files.name),"w") as f:
            for chunk in upload_files.chunks():
                f.write(chunk)
        if upload_files.name.split(".")[-1] == "zip":
            cmd = "unzip -o %s/%s -d %s;rm -rf %s/%s"%(settings.FILE_TRANS_DIR,upload_files.name,settings.FILE_TRANS_DIR,settings.FILE_TRANS_DIR,upload_files.name)
            cmd_status,cmd_result = commands.getstatusoutput(cmd)
            log = "%s 上传成功" % upload_files.name
            return HttpResponseRedirect('/multitask/file_trans/?project=%s&log=%s'%(project,log))

    file_info = {}
    # 文件源目录setting指定，遍历源目录
    check_and_mkdir(settings.FILE_TRANS_DIR)
    file_list = os.listdir(settings.FILE_TRANS_DIR)
    for i in file_list:
        if os.path.isfile("%s/%s"%(settings.FILE_TRANS_DIR,i)):
            file_info.setdefault(i,"file")
        else:
            file_info.setdefault(i,"dir")

    iUser = UserProfile.objects.get(email="%s"% request.user)
    if iUser.is_admin:
        pro_info = Project.objects.all()
    else:
        pro_info = iUser.project.all()
    if len(pro_info) == 0:
        log = "您的账号没有任何项目权限"

    zone = project
    if project is None:
        project = Project.objects.all()[0].mini_name

    else:
        host_info = host.objects.filter(project__mini_name=project,recover=0)
    return render_to_response('multitask/file_trans.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def file_trans_edit(request):
    header_title,nav,tip= "文件分发","批量任务","文件分发"
    project = request.GET.get("project")
    action = request.GET.get("action")

    if action == "delete":
        file_name = request.POST.get("file")
        if os.path.isfile("%s/%s"%(settings.FILE_TRANS_DIR,file_name)):
            # 删除文件
            os.remove("%s/%s"%(settings.FILE_TRANS_DIR,file_name))
        else:
            # 删除目录
            shutil.rmtree("%s/%s"%(settings.FILE_TRANS_DIR,file_name))
        log = "%s 删除成功"% file_name

    return HttpResponseRedirect('/multitask/file_trans/?project=%s&log=%s'%(project,log))

@login_required
@PermissionVerify()
def file_trans_process(request):
    header_title,nav,tip= "文件分发状态","批量任务","文件分发状态"
    host_list = request.POST.getlist("host")
    send_filename = request.POST.get("file")
    file_dir = request.POST.get("file_dir")
    project = request.GET.get("project")
    operator = UserProfile.objects.get(email="%s"% request.user).name
    trans_time = int(time.time())
    host_info = []

    if send_filename is None or file_dir is None or len(host_list) == 0:
        log = "请选择要发送的文件,填写目录目录!并选择要发送的服务器.."

        return HttpResponseRedirect('/multitask/file_trans/?project=%s&log=%s'%(project,log))
    for p_ip in host_list:
        host_dict = {}
        host_dict.setdefault("file_dir",file_dir)

        write_log = FileTransLog(project=project,p_ip=p_ip,filename=send_filename,remote_path=file_dir,
                                 status="0.0%",log="准备发送",trans_time=trans_time,operator=operator,total_time=0.00)
        write_log.save()

        host_port = host.objects.get(p_ip=p_ip).port
        host_project = host.objects.get(p_ip=p_ip).project.mini_name
        host_system = host.objects.get(p_ip=p_ip).os_type

        host_dict.setdefault("host",p_ip)
        host_dict.setdefault("host_port",host_port)
        host_dict.setdefault("send_file",send_filename)
        host_dict.setdefault("project",host_project)
        host_dict.setdefault("os_system",host_system)
        host_dict.setdefault("trans_time",trans_time)
        host_info.append(host_dict)

    #任务开始 task
    tasks.filetrans_func.delay(host_info)
    status_info = FileTransLog.objects.filter(trans_time=trans_time)
    return render_to_response('multitask/file_trans_process.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def file_trans_status(request):
    header_title,nav,tip= "文件分发","批量任务","文件分发"
    trans_time = request.GET.get("trans_time")
    status_info = FileTransLog.objects.filter(trans_time=trans_time)
    return render_to_response("multitask/file_trans_status.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def exec_script(request):
    header_title,nav,tip= "脚本分发","批量任务","脚本分发"
    project = request.GET.get('project')
    area_name = request.GET.get("area")
    log = request.GET.get("log")
    zone = project
    host_list = request.POST.getlist("subcheck")
    host_info = {}
    for host in host_list:
        #为了过滤备注中包含'+'
        try:
            project_mini_name,area_name,platform,p_ip,commit = host.split("+")
        except:
            project_mini_name = host.split("+")[0]
            area_name = host.split("+")[1]
            platform = host.split("+")[2]
            p_ip = host.split("+")[3]
            commit = host.split("+")[4:]

        host_info[p_ip] = host
    if project is None:
        script_obj = ScriptsManage.objects.all()
    else:
        script_obj = ScriptsManage.objects.filter(project__mini_name__in=[project,"09games"])

    return render_to_response('multitask/exec_script.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def script_args_api(request):
    if request.POST:
        script_name = request.POST.get("sname")
    try:
        input_args = ScriptsManage.objects.get(script_name=script_name).input_args
        if len(input_args) > 0:
            args_dict = eval("%s"%input_args)
            info = {"status": 1, "args_dict": args_dict}
        else:
            info = {"status": 0, "msg": "args is empty"}
    except Exception,e:
        info = {"status": 0, "msg": "args is empty"}

    return HttpResponse(json.dumps(info), content_type='application/json')

@login_required
@PermissionVerify()
def exec_script_hosts(request):
    header_title,nav,tip= "选择服务器","批量任务","脚本分发"
    project = request.GET.get("project")
    area_name = request.GET.get("area")

    project_info = cmdb_api.get_pro_info(request)

    if len(project_info) == 0:
        log = "您的账号没有任何项目权限"
    zone = project

    if project is None:
        project = Project.objects.all()[0].mini_name

    else:
        menu = host.objects.filter(project__mini_name=project,area__mini_name=area_name,recover=0).order_by("p_ip")

    if area_name is None:
        area_name = area_type.objects.all()[0].mini_name

    zone = area_name

    pro_area_info = {}
    for p in project_info:
        area_list = []
        area_obj = host.objects.filter(project__mini_name=p.mini_name).values("area").distinct()
        for z in area_obj:
            area_mini_name = area_type.objects.get(id=z["area"]).mini_name
            area_list.append(area_mini_name)
        pro_area_info.setdefault(p.mini_name,area_list)



    return render_to_response('multitask/exec_script_hosts.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def exec_script_process(request):
    header_title,nav,tip= "脚本分发执行状态","批量任务","脚本分发执行状态"
    project = request.GET.get("project")
    script_type = request.POST.get("script_type")
    script_name = request.POST.get("script_name")
    inputs = request.POST.getlist("input[]")

    host_list = request.POST.getlist("host")
    operator = UserProfile.objects.get(email="%s"% request.user).name
    # 创建原始目录
    check_and_mkdir(settings.SCRIPT_MULIT_DIR)

    if request.method == "POST":
        upload_files = request.FILES.get('up_file', None)
        if upload_files is None:
            pass
        else:
            script_name = upload_files.name
            with open("%s/%s"%(settings.SCRIPT_MULIT_DIR,upload_files.name),"w") as f:
                for chunk in upload_files.chunks():
                    f.write(chunk)
            filename = "%s/%s"%(settings.SCRIPT_MULIT_DIR,upload_files.name)
            utfFile=open(filename)
            tstr = utfFile.read()
            tstr = tstr.encode("utf-8")
            utfFile.close()
            utfFile = open(filename, 'w')
            utfFile.write(tstr)
            utfFile.close()
            os.system("dos2unix %s/%s"%(settings.SCRIPT_MULIT_DIR,upload_files.name))

    host_info = []
    start_time = int(time.time())
    for h in host_list:
        port = host.objects.get(p_ip=h).port
        hosts = project+"+"+h+"+"+str(port)
        host_info.append(hosts)
        write_log = ScriptExeclog(project=project,p_ip=h,script_name=script_name,status="5.0%",
                                  total_time=0.00,log="准备传送脚本到服务器",start_time=start_time,operator=operator)
        write_log.save()

    if script_name is not None:
        script_pro = ScriptsManage.objects.get(script_name=script_name).project.mini_name
        if inputs is not None:
            tasks.exec_pro_script_func.delay(host_info,script_name,script_type,start_time,script_pro,inputs)
        else:
            tasks.exec_pro_script_func.delay(host_info, script_name, script_type, start_time, script_pro)
    else:
        #任务
        tasks.exec_script_func.delay(host_info,script_name,script_type,start_time)

    status_info = ScriptExeclog.objects.filter(start_time=start_time)
    return render_to_response('multitask/exec_script_process.html',locals(),context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def exec_script_status(request):
    header_title,nav,tip= "文件分发","批量任务","文件分发"
    start_time = request.GET.get("start_time")
    status_info = ScriptExeclog.objects.filter(start_time=start_time)
    return render_to_response("multitask/exec_script_status.html",locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def user_audit(request):
    header_title,nav,tip= "操作记录","批量任务","操作记录"

    mulit_type = request.GET.get("type")

    if mulit_type is None or mulit_type == "script_exec":
        zone = "批量执行脚本记录"
        status_info = ScriptExeclog.objects.order_by("-start_time")[:200]
        return render_to_response('multitask/user_audit_scripts.html',locals(),context_instance=RequestContext(request))
    elif mulit_type == "file_trans":
        zone = "批量分发文件记录"
        status_info = FileTransLog.objects.order_by("-trans_time")[:200]
        return render_to_response('multitask/user_audit_files.html',locals(),context_instance=RequestContext(request))
    elif mulit_type == "cmd_exec":
        zone = "批量执行命令记录"
        status_info = CmdExecLog.objects.order_by("-start_time")[:200]
        return render_to_response('multitask/user_audit_cmds.html',locals(),context_instance=RequestContext(request))





