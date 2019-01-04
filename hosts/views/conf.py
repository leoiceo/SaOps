#!/usr/bin/env python 
#-*- coding: utf-8 -*-
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required 
from django.contrib import auth
from django.db.models import Min,Max,Sum,Avg, F, FloatField
from hosts.models import  *
from manager.myauth import *
from manager.views.permission import *
from manager.common import *
from hosts.host_api import *
from hosts.forms import KeyManagerForm,CommonUserForm
from cmdb import cmdb_api
import json

@login_required
@PermissionVerify()
def publisher_manage(request):
    header_title,nav,tip= "发行商管理","主机管理","发行商管理"
    publisher_info = publisher.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get("action")
    else:
        action = request.GET.get("action")

    if action == "delete":
        name = request.GET.get("publisher_name")
        del_pub = publisher.objects.filter(name=name)
        del_pub.delete()
    elif action == "add":
        name = request.POST.get("publisher_name")
        mini_name = request.POST.get("publisher_mini")
        if name and mini_name:
            check = publisher.objects.filter(name=name)
            if len(check) != 0:
                error = "%s 已存在！" % name
            else:
                pub_add = publisher(name=name,mini_name=mini_name)
                pub_add.save()
                
                add_info = "%s 添加成功" % name
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(publisher_info, request)
    return render_to_response('hosts/publisher.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def publisher_edit(request):
    header_title,nav,tip= "发行商管理","主机管理","发行商修改"
    pub_id = request.GET.get("id")
    publisher_info = publisher.objects.filter(id=pub_id)
    
    new_name = request.POST.get("publisher_name")
    new_mini = request.POST.get("publisher_mini")
    publisher_id = request.POST.get("publisher_id")

    if publisher_id:
        pub = publisher.objects.filter(id=publisher_id)
        pub.update(name=new_name,mini_name=new_mini)
        info = "%s 更新成功" % new_name
    return render_to_response('hosts/publisher_edit.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def area_list(request):
    header_title,nav,tip= "地区管理","主机管理","查看地区"
    area_info = area_type.objects.all()

    if request.method == 'POST':
        action = request.POST.get("action")
    else:
        action = request.GET.get("action")

    if action == "delete":
        area_name = request.GET.get("name")
        del_area = area_type.objects.filter(area_name=area_name)
        del_area.delete()
        info = "%s 删除成功"%area_name

    elif action == "add":
        area_name = request.POST.get("area_name")
        mini_name = request.POST.get("area_mini")

        if area_name and mini_name:
            check = area_type.objects.filter(area_name=area_name)
            if len(check) != 0:
                info = "%s 已存在，添加失败" % area_name
            else:
                area_add = area_type(area_name=area_name,mini_name=mini_name)
                area_add.save()
                info = "%s 添加成功" % area_name
        else:
            info = "添加不能为空"

    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(area_info, request)
    return render_to_response('hosts/area_list.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def area_edit(request):
    header_title,nav,tip= "地区管理","主机管理","修改地区"
    area_id = request.GET.get("id")
    area_info = area_type.objects.filter(id=area_id)

    new_name = request.POST.get("area_name")
    new_mini = request.POST.get("area_mini")
    area_id = request.POST.get("area_id")

    if area_id:
        area = area_type.objects.filter(id=area_id)
        area.update(area_name=new_name,mini_name=new_mini)
        info = "%s 更新成功" % new_name

    return render_to_response('hosts/area_edit.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def plat_list(request):
    header_title,nav,tip= "平台管理","主机管理","查看平台"
    if request.method == 'POST':
        action = request.POST.get("action")
    else:
        action = request.GET.get("action")

    if action == "delete":
        plat_name = request.GET.get("name")
        del_plat = platform_type.objects.filter(plat_name=plat_name)
        del_plat.delete()
        info = "%s 删除成功"% plat_name
    elif action == "add":
        plat_name = request.POST.get("plat_name")
        mini_name = request.POST.get("plat_mini")

        if plat_name and mini_name:
            check = platform_type.objects.filter(plat_name=plat_name)
            if len(check) != 0:
                info = "%s 已存在，添加失败" % plat_name
            else:
                plat_add = platform_type(plat_name=plat_name,mini_name=mini_name)
                plat_add.save()
                info = "%s 添加成功" % plat_name
        else:
            info = "添加不能为空"


    return render_to_response('hosts/plat_list.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def plat_edit(request):
    header_title,nav,tip= "平台管理","主机管理","修改平台"

    plat_id = request.GET.get("id")
    platform_info = platform_type.objects.filter(id=plat_id)

    new_name = request.POST.get("plat_name")
    new_mini = request.POST.get("plat_mini")
    plat_id = request.POST.get("plat_id")

    if plat_id:
        plat = platform_type.objects.filter(id=plat_id)
        plat.update(plat_name=new_name,mini_name=new_mini)
        info = "%s 更新成功" % new_name

    return render_to_response('hosts/plat_edit.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def use_list(request):
    header_title,nav,tip= "服务器用途管理","主机管理","查看用途"
    
    if request.method == 'POST':
        action = request.POST.get("action")
    else:
        action = request.GET.get("action")

    if action == "delete":
        use_name = request.GET.get("name")
        del_use = server_use.objects.filter(use_name=use_name)
        del_use.delete()
        info = "%s 删除成功"% use_name

    elif action == "add":
        use_name = request.POST.get("use_name")

        if use_name:
            check = server_use.objects.filter(use_name=use_name)
            if len(check) != 0:
                info = "%s 已存在，添加失败" % use_name
            else:
                use_add = server_use(use_name=use_name)
                use_add.save()
                info = "%s 添加成功" % use_name
        else:
            info = "添加不能为空"

    return render_to_response('hosts/use_list.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def use_edit(request):
    header_title,nav,tip= "服务器用途管理","主机管理","修改用途"

    use_id = request.GET.get("id")
    use_info = server_use.objects.filter(id=use_id)

    new_name = request.POST.get("use_name")
    use_id = request.POST.get("use_id")

    if use_id:
        use = server_use.objects.filter(id=use_id)
        use.update(use_name=new_name)
        info = "%s 更新成功" % new_name

    return render_to_response('hosts/use_edit.html',locals(),context_instance=RequestContext(request))



@login_required
@PermissionVerify()
def idc_manage(request):
    header_title,nav,tip= "IDC管理","主机管理","查看IDC列表"
    if request.method == 'POST':
        action = request.POST.get("action")
    else:
        action = request.GET.get("action")

    if action == "delete":
        idc_name = request.GET.get("name")
        del_idc = idc_list.objects.filter(idc_name=idc_name)
        del_idc.delete()
        info = "%s 删除成功"% idc_name
    elif action == "add":
        idc_name = request.POST.get("idc_name")
        mini_name = request.POST.get("idc_mini")
        print idc_name,mini_name
        if idc_name and mini_name:
            check = idc_list.objects.filter(idc_name="%s"%idc_name)
            print len(check)
            if len(check) != 0:
                info = "%s 已存在，添加失败" % idc_name
            else:
                idc_add = idc_list(idc_name=idc_name,mini_name=mini_name)
                idc_add.save()
                info = "%s 添加成功" % idc_name
        else:
            info = "添加不能为空"
    elif action == "query":
        idc_name = request.GET.get("name")
        host_info = host.objects.filter(idc__idc_name=idc_name)

        return render_to_response('hosts/host_list.html',locals(),context_instance=RequestContext(request))

    idc_info = idc_list.objects.all()
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(idc_info, request)
    return render_to_response('hosts/idc_list.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def idc_edit(request):
    header_title,nav,tip= "IDC管理","主机管理","修改IDC"

    idc_id = request.GET.get("id")
    idc_info = idc_list.objects.filter(id=idc_id)
    new_name = request.POST.get("idc_name")
    new_mini = request.POST.get("idc_mini")
    idc_id = request.POST.get("idc_id")
    net_line = request.POST.get("net_line")
    bandwidth = request.POST.get("bandwidth")
    linkman = request.POST.get("linkman")
    phone = request.POST.get("phone")
    comment = request.POST.get("comment")

    if idc_id:
        idc = idc_list.objects.filter(id=idc_id)
        idc.update(idc_name=new_name,mini_name=new_mini,net_line=net_line,bandwidth=bandwidth,
                   linkman=linkman,phone=phone,comment=comment)
        info = "%s 更新成功" % new_name

    return render_to_response('hosts/idc_edit.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def sshkey_list(request):
    header_title, nav, tip = "SSH密钥列表", "主机权限管理", "SSH密钥列表"
    af = KeyManagerForm()

    if request.method == 'POST':
        action = request.POST.get("action")
    else:
        action = request.GET.get("action")

    if action == "delete":
        key_id  = request.GET.get("id")
        del_key = KeyManager.objects.filter(id=key_id)
        del_key.delete()

    elif action == "add":
        if request.method == 'POST':
            af_post = KeyManagerForm(request.POST)
            name = request.POST.get('name', '')
            try:
                if KeyManager.objects.filter(name=name):
                    error = u'该密钥 %s 已存在!' % name

            except Exception:
                pass

            else:
                if af_post.is_valid():
                    af_save = af_post.save(commit=False)
                    af_save.save()
                    af_post.save_m2m()
                    key_private = KeyManager.objects.get(name=name).private_key
                    write_ssh_key(key_private, name)
                else:
                    msg = "密钥 %s 添加失败" % name
    pro_info = cmdb_api.get_pro_info(request)
    pro_list = []
    for pro in pro_info:
        pro_list.append(pro.mini_name)
    sshkey_info = KeyManager.objects.filter(project__mini_name__in=pro_list)
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(sshkey_info, request)
    return render_to_response('hosts/sshkey_list.html', locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def sshkey_edit(request):
    header_title, nav, tip = "SSH密钥管理", "主机权限管理", "编辑密钥"
    key_id = request.GET.get("id")
    key_info = KeyManager.objects.get(id=key_id)
    if key_info:
        af = KeyManagerForm(instance=key_info)
    else:
        msg = "没有找到这个密钥ID： %s" % key_id

    if request.method == 'POST':
        af_post = KeyManagerForm(request.POST, instance=key_info)
        name = request.POST.get('name', '')
        try:
            key_test = KeyManager.objects.get(name=name)
            if key_test and key_id != unicode(key_test.id):
                error = u'该密钥 %s 已存在!' % name
                print error
        except Exception, e:
            pass
        else:
            if af_post.is_valid():
                af_save = af_post.save(commit=False)
                af_save.save()
                af_post.save_m2m()
                msg = "密钥 %s 修改成功" % name
                af = KeyManagerForm(instance=key_info)

                key_private = KeyManager.objects.get(id=key_id).private_key
                write_ssh_key(key_private,name)
            else:
                error = "主机 %s 修改失败" % name

    return render_to_response('hosts/sshkey_edit.html', locals(), context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def common_user(request):
    header_title, nav, tip = "普通用户", "主机管理", "普通用户"
    project = request.GET.get("project")
    af = CommonUserForm()
    iUser = UserProfile.objects.get(email="%s" % request.user)
    if iUser.is_admin:
        pro_info = Project.objects.all()
        common_info = CommonUser.objects.all()
    else:
        pro_info = iUser.project.all()
        pro_list = []
        for p in pro_info:
            pname = p.name
            pro_list.append(pname)

        common_info = CommonUser.objects.filter(project__name__in = pro_list)
    if project is not None:
        common_info = CommonUser.objects.filter(project__mini_name=project)

    if request.method == 'POST':
        action = request.POST.get("action")
    else:
        action = request.GET.get("action")

    if action == "delete":
        key_id = request.GET.get("id")
        del_key = CommonUser.objects.filter(id=key_id)
        del_key.delete()

    elif action == "add":
        if request.method == 'POST':
            af_post = CommonUserForm(request.POST)
            name = request.POST.get('username', '')
            try:
                if CommonUser.objects.filter(username=name):
                    error = u'该用户 %s 已存在!' % name
            except Exception:
                pass
            else:
                if af_post.is_valid():
                    af_save = af_post.save(commit=False)
                    af_save.save()
                    af_post.save_m2m()
                else:
                    msg = "用户信息 %s 添加失败" % name

    return render_to_response('hosts/common_user.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def common_user_edit(request):
    header_title, nav, tip = "编辑普通用户信息", "主机管理", "编辑普通用户信息"

    key_id = request.GET.get("id")
    key_info = CommonUser.objects.get(id=key_id)
    if key_info:
        af = CommonUserForm(instance=key_info)
    else:
        msg = "没有找到用户信息ID： %s" % key_id

    if request.method == 'POST':
        af_post = CommonUserForm(request.POST, instance=key_info)
        username = request.POST.get('username', '')
        # try:
        #     key_test = CommonUser.objects.get(username=username)
        #     if key_test and key_id != unicode(key_test.id):
        #         error = u'该密钥 %s 已存在!' % username
        #         print error
        # except Exception, e:
        #     pass
        # else:

        if af_post.is_valid():
            af_save = af_post.save(commit=False)
            af_save.save()
            af_post.save_m2m()
            msg = "用户信息 %s 修改成功" % username
            af = CommonUserForm(instance=key_info)
        else:
            error = "用户信息 %s 修改失败" % username

    return render_to_response('hosts/common_user_edit.html', locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def cost_list(request):
    header_title, nav, tip = "详细信息", "费用管理", "详细信息"
    project = request.GET.get("project")
    af = CostMangerForm()
    iUser = UserProfile.objects.get(email="%s" % request.user)
    if iUser.is_admin:
        pro_info = Project.objects.all()
        cost_info = CostManger.objects.all()
    else:
        pro_info = iUser.project.all()
        pro_list = []
        for p in pro_info:
            pname = p.name
            pro_list.append(pname)

            cost_info = CostManger.objects.filter(project__name__in=pro_list)
    if project is not None:
        cost_info = CostManger.objects.filter(project__mini_name=project)

    if request.method == 'POST':
        action = request.POST.get("action")
        if action == "add":
            af_post = CostMangerForm(request.POST)

            if af_post.is_valid():
                af_save = af_post.save(commit=False)
                af_save.save()
                af_post.save_m2m()

                msg = "费用信息 添加成功"
            else:
                error = "费用信息 添加失败"
    else:
        action = request.GET.get("action")
        cost_id = request.GET.get("id")

        if action == "delete":
            del_key = CostManger.objects.filter(id=cost_id)
            del_key.delete()
        elif action == "plus":
            cost_total = CostManger.objects.get(id=cost_id).total + 1
            cost_plus = CostManger.objects.filter(id=cost_id)
            cost_plus.update(total=cost_total)
        elif action == "minus":
            cost_total = CostManger.objects.get(id=cost_id).total - 1
            cost_plus = CostManger.objects.filter(id=cost_id)
            cost_plus.update(total=cost_total)

    return render_to_response('hosts/cost_list.html',locals(),context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def cost_edit(request):
    header_title, nav, tip = "编辑信息", "费用管理", "编辑信息"

    cost_id = request.GET.get("id")
    cost_info = CostManger.objects.get(id=cost_id)
    if cost_info:
        af = CostMangerForm(instance=cost_info)
    else:
        msg = "没有找到费用信息ID： %s" % cost_id

    if request.method == 'POST':
        af_post = CostMangerForm(request.POST, instance=cost_info)

        if af_post.is_valid():
            af_save = af_post.save(commit=False)
            af_save.save()
            af_post.save_m2m()
            msg = "费用信息修改成功"
            af = CostMangerForm(instance=cost_info)
        else:
            error = "费用信息修改失败"

    return render_to_response('hosts/cost_edit.html', locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def cost_idc_api(request):
    iUser = UserProfile.objects.get(email="%s" % request.user)
    if iUser.is_admin:
        pro_info = Project.objects.all()
    else:
        pro_info = iUser.project.all()
    pro_list = []
    for p in pro_info:
        pname = p.name
        pro_list.append(pname)

    cost_idc_data = []
    import time
    cur_year = time.strftime('%Y',time.localtime(time.time()))

    cost_max = CostManger.objects.filter(project__name__in=pro_list).aggregate(
        price_per_page=Max(F('price') * F('total'), output_field=FloatField()))
    cost_avg = CostManger.objects.filter(project__name__in=pro_list).aggregate(Avg('price'))
    cost_min = CostManger.objects.filter(project__name__in=pro_list).aggregate(
        price_per_page=Min(F('price') * F('total'), output_field=FloatField()))

    project_id = CostManger.objects.filter(project__name__in=pro_list).values('project').distinct()
    id_list = []
    for proid in project_id:
        id_list.append(proid['project'])

    proinfo = Project.objects.filter(id__in=id_list)
    for pro in proinfo:
        pro_dict = {}
        pro_dict["name"] = pro.name
        m_data = []
        cost_year_info = CostManger.objects.filter(project__mini_name=pro.mini_name,start_date__year=cur_year)
        for month in range(1,13):
            cost_info = cost_year_info.filter(start_date__month=month).aggregate(
                price_per_page=Sum(F('price')*F('total'),output_field=FloatField()))
            if cost_info['price_per_page'] is not None:
                m_data.append(cost_info["price_per_page"])
            else:
                m_data.append(int(0))
        pro_dict["data"] = m_data
        cost_idc_data.append(pro_dict)
    data = {
        "data" : cost_idc_data,
        "subtitle": "配置最少：%s 平均：%s 配置最高：%s" % (cost_min['price_per_page'], "%.2f"%cost_avg['price__avg'], cost_max['price_per_page'])
    }
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
@PermissionVerify()
def cost_pro_api(request):
    iUser = UserProfile.objects.get(email="%s" % request.user)
    if iUser.is_admin:
        pro_info = Project.objects.all()
    else:
        pro_info = iUser.project.all()
    pro_list = []
    for p in pro_info:
        pname = p.name
        pro_list.append(pname)

    project_id = CostManger.objects.filter(project__name__in=pro_list).values('project').distinct()
    spro_info = []
    j_data = []
    cost_sum = []
    host_sum = []
    db_sum =[]
    mem_sum = []
    for proid in project_id:
        pro_name = Project.objects.get(id=proid['project']).name
        spro_info.append(pro_name)
        #总费用
        cost_pro = CostManger.objects.filter(project__name=pro_name).aggregate(
            price_per_page=Sum(F('price') * F('total'), output_field=FloatField()))
        cost_sum.append(cost_pro['price_per_page'])
        #云主机
        cost_host = CostManger.objects.filter(project__name=pro_name,cost_type=1).aggregate(
            price_per_page=Sum(F('price') * F('total'), output_field=FloatField()))
        if cost_host['price_per_page'] is not None:
            host_sum.append(cost_host['price_per_page'])
        else:
            host_sum.append(0)
        #云数据库
        cost_db = CostManger.objects.filter(project__name=pro_name,cost_type=2).aggregate(
            price_per_page=Sum(F('price') * F('total'), output_field=FloatField()))
        if cost_db['price_per_page'] is not None:
            db_sum.append(cost_db['price_per_page'])
        else:
            db_sum.append(0)
        #云数据库
        cost_mem = CostManger.objects.filter(project__name=pro_name,cost_type=3).aggregate(
            price_per_page=Sum(F('price') * F('total'), output_field=FloatField()))
        if cost_mem['price_per_page'] is not None:
            mem_sum.append(cost_mem['price_per_page'])
        else:
            mem_sum.append(0)

    host_data = {
        'name': '云主机',
        'data':  host_sum
    }
    j_data.append(host_data)

    db_data = {
        'name': '云数据库',
        'data': db_sum
    }
    j_data.append(db_data)

    mem_data = {
        'name': '云内存存储',
        'data': mem_sum
    }
    j_data.append(mem_data)

    m_data = {
        'name' : "累计费用",
        'data' : cost_sum,
    }

    total_cost = CostManger.objects.filter(project__name__in=pro_list).aggregate(
            price_per_page=Sum(F('price') * F('total'), output_field=FloatField()))['price_per_page']
    j_data.append(m_data)
    data = {
        "project": spro_info,
        "data" : j_data,
        "subtitle": "总计: %s RMB" % total_cost
    }

    return HttpResponse(json.dumps(data),content_type='application/json')