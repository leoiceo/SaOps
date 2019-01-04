#!/usr/bin/python
#_*_coding:utf-8_*_
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.db.models import Q
from manager.views.permission import *
import urllib2,json
from cmdb import settings
from manager.myauth import *
from hosts.models import *
from multitask.models import *
from scripting.models import *
import commands,shutil,time,codecs
from multitask import tasks
from manager.common import *
from scripting import script_api

@login_required
@PermissionVerify()
def script_list(request):
    header_title,nav,tip= "查看脚本","脚本管理","查看脚本"
    if request.GET:
        project = request.GET.get("project")
    else:
        project = request.POST.get("project")

    search_name = request.POST.get("search_name")

    log = request.GET.get("log")
    error_log = request.GET.get("error_log")

    zone = project

    if search_name is not None:
        menu_search = ScriptsManage.objects.filter(Q(script_name__icontains=search_name)|
                                            Q(use_name__icontains=search_name)|
                                            Q(operator__name__icontains=search_name))
        menu = menu_search.filter(project__mini_name=project)
    else:
        menu = ScriptsManage.objects.filter(project__mini_name=project)

    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(menu, request)

    return render_to_response('scripting/script_list.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def script_edit(request):
    project = request.GET.get("project")
    action = request.GET.get("action")
    script_dir = "%s/%s/shell_script"%(settings.BASH_DIR,project)

    operator_id = UserProfile.objects.get(email="%s" % request.user)
    project_id = Project.objects.get(mini_name=project)

    if action == "add":
        check_and_mkdir(script_dir)
        script_use = request.POST.get("script_use")
        script_name = request.POST.get("script_name")
        script_type = request.POST.get("script_type")
        upload_files = request.FILES.get('up_file', None)
        with open("%s/%s"%(script_dir,script_name),"w") as f:
            for chunk in upload_files.chunks():
                f.write(chunk)
        filename = "%s/%s"%(script_dir,script_name)
        utfFile=open(filename)
        tstr = utfFile.read()
        tstr = tstr.encode("utf-8")
        utfFile.close()
        utfFile = open(filename, 'w')
        utfFile.write(tstr)
        utfFile.close()
        os.system("dos2unix %s/%s"%(script_dir,script_name))

        check_script = ScriptsManage.objects.filter(project__mini_name=project,script_name=script_name)
        if len(check_script) != 0:
            error_log = "%s , 已经存在,不能重复添加!" % script_name
            return HttpResponseRedirect("/scripting/script_list/?project=%s&error_log=%s"%(project,error_log))
        else:
            with open("%s/%s"%(script_dir,script_name),'r') as f:
                w = ScriptsManage(project=project_id,script_name=script_name,
                              use_name=script_use,script_type=script_type,content=f.read(),
                                  create_time=time.strftime("%Y-%m-%d %H:%M:%S"),modify_time=time.strftime("%Y-%m-%d %H:%M:%S"),
                                  operator=operator_id)
                w.save()
            log = "%s,添加成功" % script_name
        return HttpResponseRedirect("/scripting/script_list/?project=%s&log=%s"%(project,log))
    elif action == "del":
        script_name = request.GET.get("script_name")
        d = ScriptsManage.objects.filter(project__mini_name=project,script_name=script_name)
        d.delete()
        try:
            os.remove("%s/%s"%(script_dir,script_name))
            log = "删除成功"
        except Exception,e:
            log = "删除错误,%s" % e
            return HttpResponseRedirect("/scripting/script_list/?project=%s&error_log=%s"%(project,log))
        return HttpResponseRedirect("/scripting/script_list/?project=%s&log=%s"%(project,log))

    elif action == "edit":
        header_title,nav,tip= "编辑脚本","脚本管理","编辑脚本"
        script_name = request.GET.get("script_name")
        use_name = ScriptsManage.objects.get(project__mini_name=project,script_name=script_name).use_name
        script_type = ScriptsManage.objects.get(project__mini_name=project,script_name=script_name).script_type
        input_args = ScriptsManage.objects.get(project__mini_name=project,script_name=script_name).input_args
        if input_args is not None:
            args = 1
            input_dict= eval("%s"%input_args)

        try:
            fp = codecs.open("%s/%s"%(script_dir,script_name),"r","utf_8_sig")
            script_file = fp.read()
            fp.close()
        except:
            script_file = ScriptsManage.objects.get(project__mini_name=project,script_name=script_name).content

        return render_to_response('scripting/script_edit.html',locals(),context_instance=RequestContext(request))
    elif action == "new":
        header_title, nav, tip = "新建脚本", "脚本管理", "新建脚本"
        env_shell = "#!/bin/bash"
        env_python = "#!/usr/bin/python"
        edit_script_use = request.POST.get("edit_script_use")
        edit_script_name = request.POST.get("edit_script_name")
        script_type = request.POST.get("script_type")
        upload_files = request.POST.get('up_file', None)
        input_list = request.POST.getlist("input[]")

        if edit_script_name is not None:

            if input_list:
                input_args = {}
                for num in range(len(input_list)):
                    arg_name = input_list[num]
                    if len(arg_name) > 0:
                        input_args["arg%s"%num] = arg_name
                    else:
                        input_args = None
            script_content = script_api.write_script(script_dir,edit_script_name,upload_files)
            up = ScriptsManage.objects.filter(project__mini_name=project, script_name=edit_script_name)
            if len(up) == 0:

                new = ScriptsManage(project=project_id, script_name=edit_script_name, use_name=edit_script_use,
                                    script_type=script_type,input_args=input_args,
                                    operator=operator_id, create_time="%s" % time.strftime("%Y-%m-%d %H:%M:%S"),
                                    content=script_content)
                new.save()
                log = "%s,添加成功" % edit_script_name
                return HttpResponseRedirect("/scripting/script_list/?project=%s&log=%s" % (project, log))
            else:
                error_log = "%s , 已经存在,不能重复添加!" % edit_script_name
                return HttpResponseRedirect("/scripting/script_list/?project=%s&error_log=%s" % (project, error_log))

        return render_to_response('scripting/script_create.html', locals(), context_instance=RequestContext(request))

    elif action == "save":
        script_name = request.GET.get("script_name")
        edit_script_use = request.POST.get("edit_script_use")
        edit_script_name = request.POST.get("edit_script_name")
        script_type = request.POST.get("script_type")
        upload_files = request.POST.get('up_file', None)
        input_list = request.POST.getlist("input[]")

        script_content = script_api.write_script(script_dir, edit_script_name, upload_files)
        up = ScriptsManage.objects.filter(project__mini_name=project, script_name=script_name)

        if input_list:
            input_args = {}
            for num in range(len(input_list)):
                arg_name = input_list[num]

                input_args["arg%s" % num] = arg_name


            up.update(script_name=edit_script_name,use_name=edit_script_use,script_type=script_type,input_args=input_args,
                    operator=operator_id,modify_time="%s"%time.strftime("%Y-%m-%d %H:%M:%S"),content=script_content)
        else:
            up.update(script_name=edit_script_name, use_name=edit_script_use, script_type=script_type,
                      operator=operator_id, modify_time="%s" % time.strftime("%Y-%m-%d %H:%M:%S"),
                      content=script_content)

        log = "保存成功"
        return HttpResponseRedirect("/scripting/script_list/?project=%s&log=%s"%(project,log))