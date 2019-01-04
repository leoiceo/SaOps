#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo

from manager.common import *
from manager.views.permission import *
from multitask.models import *
from multitask.forms import *
from multitask import tasks


@login_required
@PermissionVerify()
def update_conf(request):
    header_title, nav, tip = "更新管理", "站点管理", "配置更新"
    project = request.GET.get("project")

    iUser = UserProfile.objects.get(email="%s" % request.user)
    web_pro_info = iUser.project.all()
    web_info_all = iUser.ops_user.all()

    if project == "None" or project is None:
        project = web_info_all[0].project.mini_name
        web_info = web_info_all.filter(project__mini_name=project)
    else:
        web_info = iUser.ops_user.filter(project__mini_name=project)

    plat_info = web_info.values("platform").distinct()
    plat_dict = {}

    for plat in plat_info:
        ver_list = []
        plat_mini_name = platform_type.objects.get(id=plat["platform"]).plat_name
        try:
            version = WebSite.objects.filter(platform__plat_name=plat_mini_name)[0].version
        except:
            version = 0
        try:
            last_version = WebSite.objects.filter(platform__plat_name=plat_mini_name)[0].last_version
        except:
            last_version = 0

        try:
            pro_name = WebSite.objects.filter(platform__plat_name=plat_mini_name)[0].project
            project = pro_name.mini_name
        except Exception, e:
            error_log = e
            project = ''

        ver_list.append(pro_name)
        plat_dict[plat_mini_name] = ver_list

    return render_to_response("multitask/update_conf.html", locals(), context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def update_conf_info(request):
    header_title, nav, tip = "配置更新", "更新管理", "选择服务器"
    project = request.GET.get("project")
    conf_type = request.GET.get("conf_type")

    if request.method == "POST":
        platform = request.POST.get("platform")
    else:
        platform = request.GET.get("platform")

    if conf_type is None or len(conf_type) < 1:
        conf_type = 1

    web_info = WebSite.objects.filter(project__mini_name=project, platform__plat_name=platform)

    config_info = WebConfig.objects.filter(project__mini_name=project,cf_type=conf_type,platform__plat_name=platform)
    if len(config_info) == 0:
        config_status = 0

    return render_to_response("multitask/update_conf_info.html", locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def update_conf_status(request):
    header_title, nav, tip = "配置更新", "更新管理", "配置更新状态"
    project = request.GET.get("project")
    platform = request.GET.get("platform")
    cf_name_list = request.POST.getlist("filename")
    web_list = request.POST.getlist("subcheck")

    operator = UserProfile.objects.get(email="%s" % request.user).name
    update_time = int(time.time())
    web_info_list = []

    for web in web_list:
        web_info_dict = {}
        p_ip, s_ip, web_dir, id = web.split("+")
        domain = WebSite.objects.get(p_ip=p_ip, s_ip=s_ip, web_dir=web_dir, id=id).domain
        web_info_dict["p_ip"] = p_ip
        web_info_dict["domain"] = domain

        if web_info_dict not in web_info_list:
            web_info_list.append(web_info_dict)

            write_log = UserAuditLog(project=project, area_name="全球", platform=platform, p_ip=p_ip,
                                     operator=operator,log_type="网站配置更新", server_name=domain, log_time=update_time, status="5.0%",
                                     log="开始更新配置文件")
            write_log.save()


    tasks.web_conf_update_func.delay(web_info_list, cf_name_list, project, platform, update_time)
    status_info = UserAuditLog.objects.filter(log_time=update_time)

    return render_to_response("multitask/update_conf_status.html", locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def update_file(request):
    header_title, nav, tip = "更新管理", "站点管理", "网站更新"

    project = request.GET.get("project")

    iUser = UserProfile.objects.get(email="%s" % request.user)

    web_pro_info = iUser.project.all()
    web_info_all = iUser.ops_user.all()

    if project == "None" or project is None:
        project = web_info_all[0].project.mini_name
        web_info = web_info_all.filter(project__mini_name=project)
    else:
        web_info = iUser.ops_user.filter(project__mini_name=project)


    plat_info = web_info.values("platform").distinct()
    plat_dict = {}

    for plat in plat_info:
        ver_list = []
        plat_mini_name = platform_type.objects.get(id=plat["platform"]).plat_name
        try:
            version = WebSite.objects.filter(platform__plat_name=plat_mini_name)[0].version
        except:
            version = 0
        try:
            last_version = WebSite.objects.filter(platform__plat_name=plat_mini_name)[0].last_version
        except:
            last_version = 0

        try:
            pro_name = WebSite.objects.filter(platform__plat_name=plat_mini_name)[0].project
            pro_mini_name = pro_name.mini_name

        except Exception, e:
            project = ''
        ver_list.append(pro_mini_name)
        ver_list.append(version)
        ver_list.append(last_version)
        plat_dict[plat_mini_name] = ver_list

    return render_to_response("multitask/update_file.html", locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def update_file_info(request):
    header_title, nav, tip = "网站更新", "更新管理", "选择服务器"
    project = request.GET.get("project")

    if request.method == "POST":
        platform = request.POST.get("platform")
        gversion = request.POST.get("gversion")
    else:
        platform = request.GET.get("platform")
        gversion = request.GET.get("gversion")

    web_info = WebSite.objects.filter(project__mini_name=project,platform__plat_name=platform)
    platform_mini_name = platform_type.objects.get(plat_name=platform).mini_name

    ops_host = host.objects.get(use__use_name="运维平台")
    jump_host = ops_host.p_ip
    jump_port = ops_host.port
    jump_pro = ops_host.project.mini_name

    cmd = "svn info -r %s /data/scripts/%s/%s/rep/" % (gversion, project,platform_mini_name)
    keyname = KeyManager.objects.get(project__mini_name=jump_pro).name
    username = KeyManager.objects.get(project__mini_name=jump_pro).username
    keyfile = "%s/%s" % (settings.KEY_DIR, keyname)
    try:
        info_log, err_log = remote_run(host=jump_host, port=jump_port, keyfile=keyfile, username=username, cmd=cmd,
                                   password=None, timeout=None)
    except Exception,e:
        info_log = "SVN版本信息获取失败"
        err_log = "%s" %e

    if len(info_log) != 0:
        info_list = info_log.split('\n')
    if len(err_log) != 0:
        err_list = err_log.split('\n')

    return render_to_response("multitask/update_file_info.html", locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def update_file_status(request):
    header_title, nav, tip = "网站更新状态", "网站更新", "网站更新状态"
    project = request.GET.get("project")
    platform = request.GET.get("platform")
    gversion = request.GET.get("gversion")
    method = request.GET.get("method")
    web_list = request.POST.getlist("subcheck")

    ops_host = host.objects.get(use__use_name="运维平台")
    jump_host = ops_host.p_ip
    jump_port = ops_host.port
    jump_pro = ops_host.project.mini_name

    operator = UserProfile.objects.get(email="%s" % request.user).name
    update_time = int(time.time())
    web_info_list = []
    for web in web_list:
        web_info_dict = {}
        p_ip, s_ip, web_dir, id = web.split("+")
        domain = WebSite.objects.get(p_ip=p_ip,s_ip=s_ip ,web_dir=web_dir, id=id).domain
        web_info_dict["web_dir"] = web_dir
        web_info_dict["p_ip"] = p_ip
        web_info_dict["domain"] = domain

        if web_info_dict not in web_info_list:
            web_info_list.append(web_info_dict)
            try:
                current_version = WebSite.objects.filter(project__mini_name=project,platform__plat_name=platform)[0].version
            except:
                current_version = 0

            update_web = WebSite.objects.filter(project__mini_name=project,platform__plat_name=platform,p_ip=p_ip, web_dir=web_dir)
            update_web.update(version=gversion, last_version=current_version)

            if method == "heat":
                log_type = "网站更新"
            else:
                log_type = "web_update"

            write_log = UserAuditLog(project=project, area_name="全球", platform=platform, p_ip=p_ip,
                                     server_name=domain, version=gversion,
                                     log_time=update_time, status="5.0%", log="开始更新SVN:%s" % gversion,
                                     log_type=log_type, operator=operator)
            write_log.save()

    tasks.web_site_update_func.delay(web_info_list, jump_host, jump_port, gversion, method, project,platform, update_time)
    status_info = UserAuditLog.objects.filter(log_time=update_time)

    return render_to_response("multitask/update_file_status.html", locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def update_file_process(request):
    """
    查看更新状态
    :param request:
    :return:
    """
    project = request.GET.get("project")
    update_type = request.GET.get("type")
    platform = request.GET.get("platform")
    update_time = request.GET.get("update_time")

    if update_type == "file_update":
        status_info = UserAuditLog.objects.filter(log_time=update_time)
        return render_to_response("multitask/update_file_process.html",locals(),
                                  context_instance=RequestContext(request))

    elif update_type == "conf_update":
        status_info = UserAuditLog.objects.filter(log_time=update_time)
        return render_to_response("multitask/update_conf_process.html", locals(),
                                  context_instance=RequestContext(request))
