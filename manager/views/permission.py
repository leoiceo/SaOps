#_*_coding:utf-8_*_
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.template import RequestContext
from manager.myauth import *
from manager.common import pages

@login_required
def NoPermission(request):
    header_title = "权限不足"
    nav = "错误页面"
    tip = "权限提示"
    kwvars = {
            'request':request,
    }
    return render_to_response('manager/permission.no.html',locals(),RequestContext(request))

def PermissionVerify():
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            iUser = UserProfile.objects.get(email="%s"% request.user)
            if not iUser.is_admin:
                if not iUser.role:
                    return HttpResponseRedirect(reverse('perm_deny'))

                role_permission = RoleList.objects.get(name=iUser.role)
                role_permission_list = role_permission.permission.all()

                matchUrl = []
                for x in role_permission_list:
                    if request.path == x.url or request.path.rstrip('/') == x.url:
                        matchUrl.append(x.url)
                    elif request.path.startswith(x.url):
                        matchUrl.append(x.url)
                    else:
                        pass

                print '%s---->matchUrl:%s' %(request.user,str(matchUrl))
                if len(matchUrl) == 0:
                    return HttpResponseRedirect(reverse('perm_deny'))

            else:
                pass

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


@login_required
@PermissionVerify()
def perm_edit(request):
    header_title= "权限管理"
    nav = "编辑权限"
    tip = "修改权限"
    
    if request.method == 'GET':
        perm_name = request.GET.get("perm_name")
    else:
        perm_name = request.POST.get("perm_name")
        perm_url = request.POST.get("perm_url")
        perm_id = request.POST.get("perm_id")

        if perm_id is not None:
            perm = PermissionList.objects.filter(id=perm_id)
            perm.update(name="%s"%perm_name,url="%s"%perm_url)
            info = "%s 更新成功" % perm_name

    perm_info = PermissionList.objects.filter(name="%s" % perm_name)

    return render_to_response('manager/perm_edit.html',locals(),RequestContext(request))

@login_required
@PermissionVerify()
def perm_list(request):
    header_title= "权限管理"
    nav = "查看权限"
    tip = "权限列表"
    
    perm_info = PermissionList.objects.all()
    if request.method == 'POST':
        action = request.POST.get("action")
    else:
        action = request.GET.get("action")

    if action == "delete":
        perm_name = request.GET.get("perm_name")
        del_perm = PermissionList.objects.filter(name="%s"%perm_name)
        del_perm.delete()
    elif action == "add":
        perm_name = request.POST.get("perm_name")
        perm_url = request.POST.get("perm_url")
        if perm_name is not None:
            check_permname = PermissionList.objects.filter(name="%s"%perm_name)
            if len(check_permname) == 1:
                error = "添加失败,%s 已存在！" % perm_name
            else:
                perm = PermissionList(name="%s"%perm_name,url="%s"%perm_url)
                perm.save()
                msg = "%s 添加成功" % perm_name

        else:
            error = "输入信息不能为空 !!!" 
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(perm_info, request)
    return render_to_response('manager/perm_list.html',locals(),RequestContext(request))
