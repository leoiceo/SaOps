 #_*_coding:utf-8_*_

from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib import auth
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.mail import send_mail,send_mass_mail
#from assets.models import UserProfile,Asset
from manager.models import UserProfile,Project,LoginHistory
from hosts.models import host,Asset
from manager.views.permission import PermissionVerify
from inc.models import *
from gjsj.models import *
from Helper import Checkcode
import StringIO
import forms,json,psutil
import sys,os
from cmdb.settings import OPS_DOMAIN
from cmdb.cmdb_api import get_pro_info

reload(sys)
sys.setdefaultencoding('utf-8')
import logging
logger = logging.getLogger("hosts")

def CheckCode(request):
    mstream = StringIO.StringIO()
    validate_code = Checkcode.create_validate_code()
    img = validate_code[0]
    img.save(mstream, "GIF")
    #将验证码保存到session
    request.session["CheckCode"] = validate_code[1]
    return HttpResponse(mstream.getvalue())

@login_required
@PermissionVerify()
def monitor(request):

    action = request.GET.get("action")
    username = "icingaadmin"
    password = "leoiceo2015"
    common_url = "%s/icinga/cgi-bin" % OPS_DOMAIN
    status_url = "%s/status.cgi" % common_url
    tac_url = "%s/icinga/cgi-bin/tac.cgi"% OPS_DOMAIN

    if action == "0":
        header_title, nav, tip = "监测策略概述", "智能监控", "监测策略概述"
        icinga_url = "%s:%s@%s" %(username,password,tac_url)
    elif action == "1":
        header_title, nav, tip = "主机详情", "智能监控", "主机详情"
        icinga_url = "%s:%s@%s?style=hostdetail" %(username,password,status_url)
    elif action == "2":
        header_title, nav, tip = "服务详情", "智能监控", "服务详情"
        icinga_url = "%s:%s@%s" %(username,password,status_url)
    elif action == "3":
        header_title, nav, tip = "主机组概述", "智能监控", "主机组概述"
        icinga_url = "%s:%s@%s?hostgroup=all&style=overview" %(username,password,status_url)
    elif action == "4":
        header_title, nav, tip = "服务组概述", "智能监控", "服务组概述"
        icinga_url = "%s:%s@%s?servicegroup=all&style=overview" %(username,password,status_url)
    elif action == "5":
        header_title, nav, tip = "主机组摘要", "智能监控", "主机组摘要"
        icinga_url = "%s:%s@%s?hostgroup=all&style=summary" %(username,password,status_url)
    elif action == "6":
        header_title, nav, tip = "服务组摘要", "智能监控", "服务组摘要"
        icinga_url = "%s:%s@%s?servicegroup=all&style=summary" %(username,password,status_url)
    elif action == "7":
        header_title, nav, tip = "告警通知", "智能监控", "告警通知"
        icinga_url = "%s:%s@%s/notifications.cgi?contact=all" % (username,password,common_url)
    elif action == "8":
        header_title, nav, tip = "告警历史", "智能监控", "告警历史"
        icinga_url = "%s:%s@%s/history.cgi?host=all" % (username,password,common_url)
    elif action == "9":
        header_title, nav, tip = "告警报告", "智能监控", "告警报告"
        icinga_url = "%s:%s@%s/summary.cgi" % (username,password,common_url)
    elif action == "10":
        header_title, nav, tip = "可用性", "智能监控", "可用性"
        icinga_url = "%s:%s@%s/avail.cgi" % (username,password,common_url)
    else:
        header_title, nav, tip = "监测策略概述", "智能监控", "监测策略概述"
        icinga_url = "%s:%s@%s" % (username, password, tac_url)


    return render_to_response('monitor/icinga_host.html',locals(),context_instance=RequestContext(request))

@login_required
def index(request):
    nav = "主面板"
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):  
        ip =  request.META['HTTP_X_FORWARDED_FOR']  
    else:  
        ip = request.META['REMOTE_ADDR']  
    celery_num = os.popen('ps aux|grep celery|grep -v grep |wc -l').read()
    iUser = UserProfile.objects.get(email="%s" % request.user)

    if iUser.is_admin:
        pro_info = Project.objects.all()
    else:
        pro_info = iUser.project.all()

    inception_count = gameinfo.objects.filter(project__mini_name="inc").exclude(use__use_name="测试服").exclude(use__use_name="提审服").count()
    inception_down = gameinfo.objects.filter(status=0).exclude(use__use_name="测试服").exclude(use__use_name="提审服").count()
    gjsj_count = GjsjGameInfo.objects.filter(project__mini_name="gjsj").exclude(use__use_name="测试服").exclude(use__use_name="提审服").count()
    gjsj_down = GjsjGameInfo.objects.filter(status=0).exclude(use__use_name="测试服").exclude(use__use_name="提审服").count()

    users = UserProfile.objects.all()
    assets = Asset.objects.all()
    hosts = host.objects.all().exclude(recover=1)

    sshlog_10 = []
    sshhosts = SshAuditLog.objects.values('p_ip').distinct()[:5]
    for h in sshhosts:
        sshlog_10.append(h["p_ip"])

    login_10 = UserProfile.objects.order_by("-last_login")[:10]
    login_more_10 = UserProfile.objects.order_by("-last_login")[10:20]

    user_top = UserAuditLog.objects.values('operator').distinct()[:10]
    count_dict = {}
    user_list = []
    for i in user_top:
        user_dict = {}
        user_list.append(i["operator"])
        count_num  = UserAuditLog.objects.filter(operator=i["operator"]).count()
        user_dict["count_num"] = count_num
        log_time = UserAuditLog.objects.filter(operator=i["operator"]).order_by("-log_time")[0]
        user_dict["log_time"] = log_time.log_time
        user_dict["log_type"] = log_time.log_type
        user_dict["ip"] = log_time.p_ip
        count_dict[i["operator"]] = user_dict

    areas = area_type.objects.values("area_name")
    area_list = []
    for i in areas:
        area_name=i["area_name"]
        area_list.append(area_name)

    #内存总大小
    mem = psutil.virtual_memory()
    mem_total = mem.total / 1024  / 1024
    mem_available = mem.available / 1024  / 1024
    mem_percent = mem.percent
    try:
        #disk
        disk = psutil.disk_usage('/data')
        disk_total = disk.total / 1024 / 1024 / 1024
        disk_percent = disk.percent

        disk_root = psutil.disk_usage('/')
        root_total = disk_root.total / 1024 / 1024 / 1024
        root_percent = disk_root.percent
    except:
        import random
        disk_percent = "%.2f" % random.uniform(40,60)
        root_percent = "%.2f" % random.uniform(40,60)
    #CPU cpu_percent
    cpu_percent = psutil.cpu_percent()

    logger.error("%s 登陆了，打开了主页" % request.user)
    return render_to_response('index.html',locals(),context_instance=RequestContext(request))



@login_required
def highchart_pie(request):

    pro_info = get_pro_info(request)
    data = []
    data_dic = {}
    data_dic["name"] = "Brands"
    data_list = []
    Denominator = pro_info.count()
    for pro_name in pro_info:
        pro_dic = {}
        if pro_name.name == "基础业务":
            pro_dic["sliced"] = bool('true'),
            pro_dic["selected"] = bool('true'),

        pro_dic['name'] = pro_name.name

        y_value = host.objects.filter(project__name=pro_name.name).count() / float(Denominator)

        pro_dic['y'] = y_value

        data_list.append(pro_dic)

    data_dic["data"] = data_list
    data.append(data_dic)

    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
def highchart_api(request):

    pro_info = get_pro_info(request)

    areas = area_type.objects.values("area_name")
    area_list = []
    for i in areas:
        area_name = i["area_name"]
        area_list.append(area_name)

    data = []

    stack = 0
    for pro_name in pro_info:
        if stack == 0:
            stack_value = 'male'
            stack = 1
        else:
            stack_value = 'female'
            stack = 0
        pro_dict = {}
        area_hosts_count = []
        for aname in area_list:
            anum = host.objects.filter(project__name=pro_name,area__area_name=aname).count()
            area_hosts_count.append(anum)
        name = pro_name.name
        pro_dict['name'] = name
        pro_dict['stack'] = stack_value
        pro_dict['data'] = area_hosts_count
        data.append(pro_dict)

    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
def skin_config(request):
    return render_to_response('skin_config.html',locals(),context_instance=RequestContext(request))

@login_required
def personal(request):
    header_title = "修改信息"
    nav = "个人信息"
    tip = "详细信息"
    zone = "修改密码"

    if request.method == 'POST':
        old_passwd = request.POST.get('old_passwd')
        new_password = request.POST.get('new_passwd')
        user = auth.authenticate(username=request.user.email,password=old_passwd)
        print user,old_passwd,new_password
        if user is not None:
            request.user.set_password(new_password)
            request.user.save()
            login_err = '密码修改成功,请重新登陆！'
            return render_to_response('login.html',locals(),context_instance=RequestContext(request))
        else:
            msg = '原密码输入错误！'
            return render_to_response('personal.html',locals(),context_instance=RequestContext(request))
    else:
        info_form=forms.UserProfileForm()
        return render_to_response('personal.html',locals(),context_instance=RequestContext(request))

def account_login(request):

    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        check_code = request.POST.get('checkcode')
        user = authenticate(username=username,password=password)
        session_code = request.session["CheckCode"]
        login_err =  '验证失败?再想想^.^'
        if check_code.strip().lower() != session_code.lower():
            login_err = '手滑输错了？再试试'
            return render_to_response('login.html',locals(),context_instance=RequestContext(request))
        else:
            if user is not None:                    # pass authencation
                if user.is_active == False:
                    login_err =  '警告,%s已经被禁用' % user.name
                    return render_to_response('login.html',locals(),context_instance=RequestContext(request))
                login(request,user)
                hl = LoginHistory(name=user.name,ip=ip,stats='登陆成功',get_full_path=request.get_full_path())
                hl.save()
                return HttpResponseRedirect('/')
            else:
                return render_to_response('login.html',locals(),context_instance=RequestContext(request))
    else:
        return render_to_response('login.html',locals(),context_instance=RequestContext(request))

def account_logout(request):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']

    username = UserProfile.objects.get(email="%s" % request.user).name
    lout = LoginHistory(name=username, ip=ip, stats="注销成功",get_full_path=request.get_full_path())
    lout.save()
    logout(request)
    return HttpResponseRedirect('/login/')

def page_not_found(request):
    return render_to_response('404.html')

def page_error(request):
    return render_to_response('500.html')
