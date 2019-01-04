#_*_coding:utf-8_*_
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from manager.myauth import *
from manager.common import *
from permission import *

@login_required
@PermissionVerify()
def pro_list(request):
    header_title= "项目管理"
    nav = "项目信息"
    tip = "查看项目"

    data = {}
    if request.method == 'POST':
        action = request.POST.get("action")
    else:
        action = request.GET.get("action")
        pro_name = request.GET.get("pro_name")

    pro_info = Project.objects.all()

    if action == "delete":
        del_pro = Project.objects.filter(name="%s" % pro_name)
        del_pro.delete()

    elif action == "add":
        pro_name = request.POST.get("pro_name")
        pro_mini = request.POST.get("pro_mini")
        if pro_name is not None:
            check_proname = Project.objects.filter(name="%s"%pro_name)
            if len(check_proname) == 1 :
                error = "%s 已存在！" % pro_name
            else:
                pro = Project(name="%s"%pro_name,mini_name="%s"%pro_mini)
                pro.save()
                add_info = "%s 添加成功" % pro_name
        else:
            error = "输入信息不能为空"

    for info in pro_info:
        users = []
        user_id = UserProfile.objects.filter(project__name="%s" % info.name)
        for uid in user_id:
            users.append(uid.name)
        data.setdefault(info.name,users)

    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(pro_info, request)
    return render_to_response('manager/pro_list.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def pro_edit(request):
    header_title= "项目管理"
    nav = "项目信息"
    tip = "修改项目"

    if request.method == 'GET':
        pro_name = request.GET.get("pro_name")
    else:
        pro_name = request.POST.get("pro_name")
        pro_mini = request.POST.get("pro_mini")
        pro_id = request.POST.get("pro_id")

        if pro_id is not None:
            pro = Project.objects.filter(id=pro_id)
            pro.update(name="%s"%pro_name,mini_name="%s"%pro_mini)
            info = "%s 更新成功" % pro_name
    pro_info = Project.objects.filter(name="%s"%pro_name)

    return render_to_response('manager/pro_edit.html',locals(),context_instance=RequestContext(request))
