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
def conf_list(request):
    header_title, nav, tip = "配置管理", "站点管理", "配置列表"

    if request.method == 'POST':
        action = request.POST.get("action")
        project = request.GET.get("project")
        platform = request.GET.get("platform")
    else:
        action = request.GET.get("action")
        project = request.GET.get("project")
        platform = request.GET.get("platform")

    af = WebConfigForm()

    if action == "add":
        if request.method == 'POST':
            af_post = WebConfigForm(request.POST)
            name = request.POST.get('cf_name', '')
            try:
                if WebConfig.objects.filter(cf_name=name):
                    error = u'网站配置 %s 已存在!' % name
                    raise Exception(error)
            except Exception:
                pass
            else:
                if af_post.is_valid():
                    af_save = af_post.save(commit=False)
                    af_save.save()
                    af_post.save_m2m()
                    msg = "网站配置 %s 添加成功" % name
                else:
                    error = "网站配置 %s 添加失败" % name

    elif action == "delete":
        web_id = request.GET.get("id")
        name = WebConfig.objects.get(id=web_id).cf_name
        del_key = WebConfig.objects.filter(id=web_id)
        del_key.delete()
        msg = "网站配置 %s 删除成功" % name

    iUser = UserProfile.objects.get(email="%s" % request.user)
    if iUser.is_admin:
        pro_info = Project.objects.all()
    else:
        pro_info = iUser.project.all()

    if project == "None" or project is None:
        pro_list = []
        for pro in pro_info:
            pro_list.append(pro.name)
        web_info = WebConfig.objects.filter(project__name__in=pro_list)
    else:
        web_info = WebConfig.objects.filter(project__name=project)

    pro_plat_dict = {}
    web_pro_list = []
    for web in web_info:
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

    for conf in web_info:
        conf_dir = "%s/%s/%s/" % (settings.CONF_DIR,conf.project.mini_name,conf.platform.mini_name)
        check_and_mkdir(conf_dir)

        with open("%s/%s" % (conf_dir,conf.cf_name),"w") as f:
            for ct in conf.cf_content.encode("utf-8"):
                f.write(ct)

    return render_to_response('multitask/conf_list.html', locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def conf_edit(request):
    header_title, nav, tip = "编辑配置信息", "站点管理", "编辑配置信息"

    web_id = request.GET.get("id")
    web_info = WebConfig.objects.get(id=web_id)
    if web_info:
        af = WebConfigForm(instance=web_info)
    else:
        msg = "没有找到站点配置信息ID： %s" % web_id

    if request.method == 'POST':
        af_post = WebConfigForm(request.POST, instance=web_info)
        web_name = request.POST.get('cf_name', '')
        try:
            web_test = WebConfig.objects.get(cf_name=web_name)
            if web_test and web_id != unicode(web_test.id):
                error = u'该站点配置 %s 已存在!' % web_name
                raise Exception(error)
        except Exception, e:
            pass
        else:
            if af_post.is_valid():
                af_save = af_post.save(commit=False)
                af_save.save()
                af_post.save_m2m()
                msg = "站点配置信息 %s 修改成功" % web_name
                af = WebConfigForm(instance=web_info)
            else:
                error = "站点配置信息 %s 修改失败" % web_name

    return render_to_response('multitask/conf_edit.html', locals(), context_instance=RequestContext(request))