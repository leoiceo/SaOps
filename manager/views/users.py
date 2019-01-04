#_*_coding:utf-8_*_
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from manager.myauth import *
from manager.common import *
from cmdb import settings
import time
from permission import *
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

@login_required
@PermissionVerify()
def user_list(request):
    header_title,nav,tip= "用户列表","系统配置","用户管理"

    users = UserProfile.objects.all()
    msg = request.GET.get("log")

    if request.method == 'POST':
        user_id = request.POST.get("user_id")
    else:
        user_id = request.GET.get("user_id")
    action = request.GET.get("action")

    if action is not None:
        userprofile = UserProfile.objects.filter(id="%s"%user_id)
        if action.encode("utf-8") == "delete":
            userprofile.delete()
        elif action.encode("utf-8") == "disable":
            userprofile.update(is_active=0)
        elif action.encode("utf-8") == "enable":
            userprofile.update(is_active=1)

    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(users, request)
    return render_to_response('manager/user_all.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def user_eye(request):
    header_title,nav,tip = "用户信息","系统配置","查看用户"

    if request.method == 'GET':
        user_id = request.GET.get("user_id")
    user_info = UserProfile.objects.filter(id=user_id)

    return render_to_response('manager/user_eye.html',locals(),context_instance=RequestContext(request))
#def user_modity_privil(request):
#    if request.method == 'POST':
#        user_id = request.POST.get("user_id")
#        role_id = request.POST.get("role_id")

@login_required
@PermissionVerify()
def user_edit(request):
    header_title= "用户管理"
    nav = "编辑用户"
    tip = "查看信息"
    zone = "修改信息"
    
    user_id = request.GET.get("user_id")

    user_info = UserProfile.objects.filter(id=user_id)

    dept_info = DepartMent.objects.all()
    role_info = RoleList.objects.all()
    pro_info = Project.objects.all()

    email = request.POST.get("username")
    name = request.POST.get("name")
    token = request.POST.get("token")
    mobile = request.POST.get("mobile")
    tel = phone = request.POST.get("tel")
    is_admin = request.POST.get("is_admin")
    dept_name = request.POST.get("dept_name")
    role_name = request.POST.get("role_name")
    project = request.POST.getlist("project")
    
    if email is not None:
        dept_id = DepartMent.objects.get(name="%s"%dept_name)

        if role_name == "超级管理员":
            up_user = UserProfile.objects.filter(email=email)
            up_user.update(name=name,token=token,mobile=mobile,tel=tel,is_admin=int(is_admin),department=dept_id)
        else:
            role_id = RoleList.objects.get(name="%s"%role_name)
            up_user = UserProfile.objects.filter(email=email)
            up_user.update(name=name,token=token,mobile=mobile,tel=tel,is_admin=int(is_admin),department=dept_id,role=role_id)
        user = UserProfile.objects.get(email=email)
        if len(project) != 0:
            user.project.clear()
        for proname in project:
            pro = Project.objects.get(name=proname)
            user.project.add(pro)
            user.save()
            msg = "%s 用户信息修改成功" % name
        return HttpResponseRedirect(reverse('user_list'))
    return render_to_response('manager/user_edit.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def user_add(request):
    header_title= "用户管理"
    nav = "查看用户"
    tip = "添加用户"
    zone = "填写用户信息"
    
    dept_info = DepartMent.objects.all()
    pro_info = Project.objects.all()
    role_info = RoleList.objects.all()

    email = request.POST.get("username")
    password = request.POST.get("password")
    name = request.POST.get("name")
    dept_name = request.POST.get("dept_name")
    role_name = request.POST.get("role_name")
    project = request.POST.getlist("project")
    mobile = request.POST.get("mobile")
    date_joined = time.strftime("%Y-%m-%d %H:%M:%S")
    is_admin = request.POST.get("is_admin")

    message='''
    hi,%s:
    欢迎使用云起互娱运维平台，您的账号已创建成功，账号：%s, 初始密码：%s
平台地址： https://%s. (登陆前请安装客户端SSL密钥)
1. SSL密钥下载地址： http://%s/api/get_ssl
2. 下载到client.p12 后双击安装密钥，输入密码 "redhat"
3. 安装成功后即可访问运维平台，请及时修改密码!

(注：此邮件系统自动发出，请勿回复)''' % (name,email,password,settings.OPS_DOMAIN,settings.OPS_DOMAIN)

    if email and password is not None:
        password = make_password(password, None, 'pbkdf2_sha256')
        try:
            dept_id = DepartMent.objects.get(name="%s"%dept_name)
            role_id = RoleList.objects.get(name="%s"%role_name)
        except:
            error = "%s 部门和角色不能为空,请添加!" % name
            return render_to_response('manager/user_add.html',locals(),context_instance=RequestContext(request))
        
        check_email = UserProfile.objects.filter(email=email)
        if len(check_email) == 1:
            error = "%s 用户已经存在，不能重复添加" % name
        else:
            add_user = UserProfile(email=email,password=password,name=name,department=dept_id,role=role_id,mobile="%s"%mobile,is_active=1,is_admin=int(is_admin),date_joined=date_joined)
            add_user.save()
            for proname in project:
                pro = Project.objects.get(name=proname)
                user = UserProfile.objects.get(email=email)
                user.project.add(pro)
            msg = "%s 用户添加成功" % name

            try:
                send_mail('运维平台添加用户成功提醒', message, '%s'%settings.EMAIL_HOST_USER,['%s'%email], fail_silently=False)
            except Exception,e:
                msg = "%s"%e
            return HttpResponseRedirect("/manager/user_list/?log=%s" % msg)

    return render_to_response('manager/user_add.html',locals(),context_instance=RequestContext(request))
