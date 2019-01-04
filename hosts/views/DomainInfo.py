#!/usr/bin/env python
#-*- coding: utf-8 -*-

from manager.common import *
from manager.views.permission import *

@login_required
@PermissionVerify()
def domain_list(request):
    header_title, nav, tip = "域名信息管理", "域名列表", "域名信息管理"

    af = DomainInfoForm()

    if request.method == 'POST':
        action = request.POST.get("action")
    else:
        action = request.GET.get("action")

    if action == "delete":
        key_id = request.GET.get("id")
        del_key = DomainInfo.objects.filter(id=key_id)
        del_key.delete()

    elif action == "add":
        if request.method == 'POST':
            af_post = DomainInfoForm(request.POST)
            domain_name = request.POST.get('domain_name', '')
            try:
                if DomainInfo.objects.filter(domain_name=domain_name):
                    error = u'域名 %s 已存在!' % domain_name
            except Exception:
                pass

            else:
                if af_post.is_valid():
                    af_save = af_post.save(commit=False)
                    af_save.save()
                    af_post.save_m2m()
                else:
                    msg = "域名 %s 添加失败" % domain_name

    iUser = UserProfile.objects.get(email="%s" % request.user)
    if iUser.is_admin:
        domain_info = DomainInfo.objects.all()
    else:
        project_info = iUser.project.all()
        pro_list = []
        for i in project_info:
            mini_name = i.mini_name
            pro_list.append(mini_name)

        domain_info = DomainInfo.objects.filter(project__mini_name__in=pro_list)

    return render_to_response('hosts/domain_list.html', locals(), context_instance=RequestContext(request))




