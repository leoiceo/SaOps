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
def site_list(request):
    header_title, nav, tip = "网站节点", "站点管理", "节点列表"

    if request.method == 'POST':
        action = request.POST.get("action")
        project = request.GET.get("project")
        platform = request.GET.get("platform")
    else:
        action = request.GET.get("action")
        project = request.GET.get("project")
        platform = request.GET.get("platform")

    af = WebSiteForm()

    if action == "add":
        if request.method == 'POST':
            af_post = WebSiteForm(request.POST)
            name = request.POST.get('domain', '')
            try:
                if WebSite.objects.filter(domain=name):
                    error = u'网站 %s 已存在!' % name
                    raise Exception(error)
            except Exception:
                pass
            else:
                if af_post.is_valid():
                    af_save = af_post.save(commit=False)
                    af_save.save()
                    af_post.save_m2m()
                    msg = "网站 %s 添加成功" % name
                else:
                    error = "网站 %s 添加失败" % name
    elif action == "delete":
        web_id = request.GET.get("id")
        name = WebSite.objects.get(id=web_id).domain
        del_key = WebSite.objects.filter(id=web_id)
        del_key.delete()
        msg = "网站 %s 删除成功" % name

    iUser = UserProfile.objects.get(email="%s" % request.user)
    if iUser.is_admin:
        pro_info = Project.objects.all()
        if project == "None" or project is None:
            pro_list = []
            for pro in pro_info:
                pro_list.append(pro.name)
            web_info = WebSite.objects.filter(project__name__in=pro_list)
        else:
            web_info = WebSite.objects.filter(project__name=project)

    else:
        #pro_info = iUser.project.all()
        if project == "None" or project is None:
            web_info = iUser.ops_user.all()
        else:
            web_info = iUser.ops_user.filter(project__name=project)

    pro_plat_dict = {}
    web_pro_list = []
    web_info_all = iUser.ops_user.all()
    for web in web_info_all:
        if web.project.name not in web_pro_list:
            web_pro_list.append(web.project.name)

        plat_list = []
        if web.platform.plat_name not in plat_list:
            plat_list.append(web.platform.plat_name)

        try:
            old_plat_list = pro_plat_dict[web.project.name]
            plat_list = old_plat_list + plat_list
            plat_list = list(set(plat_list))
            pro_plat_dict[web.project.name] = plat_list
        except:

            pro_plat_dict[web.project.name] = plat_list

    if platform is not None:
        web_info = web_info.filter(platform__plat_name=platform)
    else:
        try:
            platform = plat_list[0]
            project = web_pro_list[0]
        except Exception,e:
            pass

    return render_to_response('multitask/site_list.html', locals(), context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def site_edit(request):
    header_title, nav, tip = "编辑站点信息", "站点管理", "编辑站点信息"

    web_id = request.GET.get("id")
    web_info = WebSite.objects.get(id=web_id)
    if web_info:
        af = WebSiteForm(instance=web_info)
    else:
        msg = "没有找到站点信息ID： %s" % web_id

    if request.method == 'POST':
        af_post = WebSiteForm(request.POST, instance=web_info)
        web_name = request.POST.get('domain', '')
        try:
            web_test = WebSite.objects.get(domain=web_name)
            if web_test and web_id != unicode(web_test.id):
                error = u'该站点 %s 已存在!' % web_name
                raise Exception(error)
        except Exception, e:
            pass
        else:
            if af_post.is_valid():
                af_save = af_post.save(commit=False)
                af_save.save()
                af_post.save_m2m()
                msg = "站点信息 %s 修改成功" % web_name
                af = WebSiteForm(instance=web_info)
            else:
                error = "站点信息 %s 修改失败" % web_name
    return render_to_response('multitask/site_edit.html', locals(), context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def site_crontrol(request):
    header_title, nav, tip = "网站操作日志", "站点管理", "网站操作日志"
    project = request.GET.get("project")
    web_list = request.POST.getlist('subcheck')
    platform = request.GET.get("platform")
    action = request.POST.get("switch")
    operator = UserProfile.objects.get(email="%s" % request.user).name

    project = Project.objects.get(name=project).mini_name

    log_time = int(time.time())
    web_site_info = []
    for web in web_list:
        single_game = {}
        p_ip, web_dir, domain = web.split('+')
        port = host.objects.get(p_ip=p_ip).port
        web_site_info.append("%s+%s+%s" % (p_ip, port, web_dir))
        write_log = UserAuditLog(project=project, area_name='全球', server_name=domain,platform=platform,
                                 p_ip=p_ip, log_type=action, log="开始执行", status="5.0%",
                                 log_time=log_time, operator=operator)
        write_log.save()

    tasks.web_site_crontrol_func.delay(web_site_info, {"action": action, "log_time": log_time,"project": project})

    status_info = UserAuditLog.objects.filter(log_time=log_time)

    return render_to_response('multitask/site_crontrol.html', locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def site_crontrol_status(request):
    header_title, nav, tip = "网站操作日志", "站点管理", "网站操作日志"
    project = request.GET.get("project")
    action = request.GET.get("action")
    log_time = request.GET.get("log_time")

    if log_time is not None and log_time != "None":
        status_info = UserAuditLog.objects.filter(project=project, log_type=action,log_time=log_time)
    else:
        status_info = UserAuditLog.objects.filter(project=project,area_name="全球")

    return render_to_response('multitask/site_crontrol_status.html', locals(), context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def site_crontrol_log(request):
    header_title, nav, tip = "网站操作日志", "站点管理", "网站操作日志"
    project = request.GET.get("project")
    action = request.GET.get("action")
    log_time = request.GET.get("log_time")

    if log_time is not None and log_time != "None":
        status_info = UserAuditLog.objects.filter(project=project, log_type=action,log_time=log_time)
    else:
        status_info = UserAuditLog.objects.filter(project=project,area_name="全球")

    return render_to_response('multitask/site_crontrol.html', locals(), context_instance=RequestContext(request))