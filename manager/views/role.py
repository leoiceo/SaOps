#_*_coding:utf-8_*_
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from manager.myauth import *
from manager.common import *
from permission import *

@login_required
@PermissionVerify()
def role_list(request):
    header_title= "角色管理"
    nav = "角色列表"
    tip = "查看角色"

    if request.method == 'POST':
        action = request.POST.get("action")
    else:
        action = request.GET.get("action")

    role_info = RoleList.objects.all()
    menu = RoleList.objects.all()

    if action == "delete":
        role_name = request.GET.get("role_name")
        del_role = RoleList.objects.filter(name="%s" % role_name)
        del_role.delete()

    elif action == "add":
        role_name = request.POST.get("role_name")

        if role_name is not None:
            check_rolename = RoleList.objects.filter(name="%s"%role_name)
            if len(check_rolename) == 1 :
                error = "%s 已存在！" % role_name
            else:
                role = RoleList(name="%s"%role_name)
                role.save()
                add_info = "%s 添加成功" % role_name
        else:
            error = "输入信息不能为空"

    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(menu, request)

    return render_to_response('manager/role_list.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def role_edit(request):
    header_title= "角色管理"
    nav = "编辑角色"
    tip = "修改信息"
    urls = []
    if request.method == 'GET':
        role_id = request.GET.get("role_id")
        role_name = RoleList.objects.get(id=role_id)
        role_info = UserProfile.objects.filter(role=role_id)
    else:
        role_id = request.POST.get("role_id")
        role_name = RoleList.objects.get(id=role_id)
        urls_select = request.POST.getlist("urls_select")
        role_info = UserProfile.objects.filter(role=role_id)
        print urls_select
        if len(urls_select) != 0:
            uprole = RoleList.objects.get(id=role_id)
            uprole.permission.clear()
            for p_id in urls_select:
                uprole.permission.add(p_id)
            uprole.save()
            msg = "更新成功"
        else:
            error = "清空所有权限,请直接删除这个角色"

    role_urls = role_name.permission.all()
    all_urls = PermissionList.objects.all()
    for url in all_urls:
        if url not in role_urls:
            urls.append(url)
    
    #if len(urls_select) != 0:
    #    for url_id in urls_select:
            #print url_id
    #        userprofile = UserProfile.objects.filter(id="%s" % user_id)
    #        userprofile.update(role=role_id)

    return render_to_response('manager/role_edit.html',locals(),context_instance=RequestContext(request))
