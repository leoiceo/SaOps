#_*_coding:utf-8_*_
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from manager.myauth import *
from manager.common import *
from permission import *

@login_required
@PermissionVerify()
def dept_list(request):
    header_title= "部门管理"
    nav = "部门信息"
    tip = "查看部门"

    data = {}
    if request.method == 'POST':
        action = request.POST.get("action")
    else:
        action = request.GET.get("action")
        dept_name = request.GET.get("dept_name")

    dept_info = DepartMent.objects.all()

    if action == "delete":
        del_dept = DepartMent.objects.filter(name="%s" % dept_name)
        del_dept.delete()

    elif action == "add":
        dept_name = request.POST.get("dept_name")
        dept_comment = request.POST.get("dept_comment")
        if len(dept_name) > 0:
            check_deptname = DepartMent.objects.filter(name="%s"%dept_name)
            if len(check_deptname) == 1 :
                error = "%s 已存在！" % dept_name
            else:
                dept = DepartMent(name="%s"%dept_name,comment="%s"%dept_comment)
                dept.save()
                add_info = "%s 添加成功" % dept_name
        else:
            error = "输入信息不能为空"

    for info in dept_info:
        users = []
        user_id = UserProfile.objects.filter(department__name="%s" % info.name)
        for uid in user_id:
            users.append(uid.name)
        data.setdefault(info.name,users)

    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(dept_info, request)
    return render_to_response('manager/dept_list.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def dept_add(request):
    header_title= "部署管理"
    nav = "部门信息"
    tip = "添加部门"

    dept_name = request.POST.get("dept_name")
    dept_comment = request.POST.get("dept_comment")
    
    if dept_name is not None:
        check_deptname = DepartMent.objects.filter(name="%s"%dept_name)
        print check_deptname,len(check_deptname)
        if len(check_deptname) == 1 :
            error = "%s 已存在！" % dept_name
        else:
            dept = DepartMent(name="%s"%dept_name,comment="%s"%dept_comment)
            dept.save()
            info = "%s 添加成功" % dept_name

    return render_to_response('manager/dept_add.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def dept_edit(request):
    header_title= "部门管理"
    nav = "部门信息"
    tip = "修改信息"

    if request.method == 'GET':
        dept_name = request.GET.get("dept_name")
    else:
        dept_name = request.POST.get("dept_name")
        dept_comment = request.POST.get("dept_comment")
        dept_id = request.POST.get("dept_id")

        if dept_id is not None:
            dept = DepartMent.objects.filter(id=dept_id)
            dept.update(name="%s"%dept_name,comment="%s"%dept_comment)
            info = "%s 更新成功" % dept_name
    dept_info = DepartMent.objects.filter(name="%s"%dept_name)

    return render_to_response('manager/dept_edit.html',locals(),context_instance=RequestContext(request))
