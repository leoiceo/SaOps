#!/usr/bin/env python 
#-*- coding: utf-8 -*-
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required 
from django.contrib import auth
from django.http import StreamingHttpResponse
from manager.views.permission import *
from hosts.models import  *
from manager.myauth import *
from hosts.host_api import *
from django.db.models import Q
import time

@login_required
@PermissionVerify()
def host_list(request):
    header_title,nav,tip= "主机管理","服务器列表","查看服务器"

    if request.method == "POST":
        project = request.POST.get("project")
        search_name = request.POST.get("search_name")
        switch = request.POST.get("switch")
        ip_list = request.POST.getlist("ip_list")

        if switch is None:
            try:
                if len(search_name) > 0:
                    if project == "all" or project == "None":
                        pro_host_info = host.objects.all()
                    else:
                        pro_host_info = host.objects.filter(project__mini_name=project)

                    host_info = pro_host_info.filter(Q(project__name__contains=search_name) |
                                                    Q(project__mini_name__contains=search_name) |
                                                    Q(area__area_name__contains=search_name) |
                                                    Q(area__mini_name__contains=search_name) |
                                                    Q(idc__mini_name__contains=search_name) |
                                                    Q(idc__idc_name__contains=search_name) |
                                                    Q(platform__plat_name__contains=search_name) |
                                                    Q(platform__mini_name__contains=search_name) |
                                                    Q(os_type__contains=search_name) |
                                                    Q(p_ip__contains=search_name) |
                                                    Q(s_ip__contains=search_name) |
                                                    Q(db_ip__contains=search_name) |
                                                    Q(port__contains=search_name) |
                                                    Q(use__use_name__contains=search_name) |
                                                    Q(login_pass__contains=search_name) |
                                                    Q(commit__contains=search_name)
                                                    ).exclude(recover=1).order_by('-online_date')
                else:
                    error = "搜索输入不能为空！"
                    raise Exception(error)
            except Exception, e:
                error = "%s" % e
                if project == "all" or project is None:
                    pro_host_info = host.objects.all()
                else:
                    pro_host_info = host.objects.filter(project__mini_name=project)

                host_info = pro_host_info.exclude(recover=1).order_by('-online_date')

            
            return render_to_response('hosts/host_list.html',locals(),context_instance=RequestContext(request))
        else:

            if switch == "del":
                recover_date=time.strftime('%Y-%m-%d %X', time.localtime())
                for ip in ip_list:
                    hosts = host.objects.filter(p_ip=ip)
                    hosts.update(recover=1,recover_date=recover_date)
                    assets = Asset.objects.filter(p_ip=ip)
                    assets.update(status=3)
                info = "%s 删除成功,请在回收列表查看" %ip_list
            elif switch == "new":
                for ip in ip_list:
                    hosts = host.objects.filter(p_ip=ip)
                    hosts.update(recover=0)
                    assets = Asset.objects.filter(p_ip=ip)
                    assets.update(status=1)
                info = "%s 恢复成功，可以上线" % ip_list
            elif switch == "clear":
                for ip in ip_list:
                    hosts = host.objects.filter(p_ip=ip)
                    hosts.delete()
                info = "%s 删除成功，正式下线" % ip_list
                return HttpResponseRedirect(reverse('host_recover'))

    project = request.GET.get("project")

    iUser = UserProfile.objects.get(email="%s" % request.user)
    if iUser.is_admin:
        pro_info = Project.objects.all()
    else:
        pro_info = iUser.project.all()

    if project == "None" or project is None:
        pro_me_list = []
        for p in pro_info:
            pro_me_list.append(p.mini_name)

    if project == "None" or project is None or project == "all":
        if iUser.is_admin:
            host_info = host.objects.all().exclude(recover=1).order_by('-online_date')
        else:
            host_info = host.objects.filter(project__mini_name__in=pro_me_list).exclude(recover=1).order_by('-online_date')
    elif project is not None:
        host_info = host.objects.filter(project__mini_name=project).exclude(recover=1).order_by('-online_date')

    return render_to_response('hosts/host_list.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def host_export_excel(request):
    header_title, nav, tip = "主机管理", "服务器列表", "导出服务器列表"
    project = request.GET.get("project")
    #if project == "None":
    #    project = Project.objects.get(name="基础业务").mini_name

    if project == "all" or project == "None":
        project = "all"
        host_info = host.objects.all().exclude(recover=1)
    else:
        host_info = host.objects.filter(project__mini_name=project).exclude(recover=1)

    # # 大一1万行写csv,避免卡
    # if host_info.count() > 10000:
    #     s = write_csv(project)
    # else:
    #     s = write_excel(project)
    s = host_export_file(project)

    if s[0]:
        file_name = s[1]
        smg = u'EXCEL 文件已生成，请点击下载!'
    else:
        error=s[1]

    if project == "all" or project == "None":
        hosts = host.objects.all()

    else:
        hosts = host.objects.filter(project__mini_name=project)

    host_info = hosts.exclude(recover=1).order_by('-online_date')

    return render_to_response('hosts/host_list.html', locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def host_excel_download(request):

    filename = request.GET.get("filename")
    the_file_name = "%s/%s" % (EXCEL_DIR,filename)

    response = StreamingHttpResponse(file_iterator(the_file_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename)
    # sio = StringIO.StringIO()
    # data = xlrd.open_workbook(the_file_name)
    # data.save(sio)
    # sio.seek(0)
    # response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
    # response['Content-Disposition'] = 'attachment; filename=%s' % filename
    # response.write(sio.getvalue())
    return response

@login_required
@PermissionVerify()
def host_recover(request):
    header_title, nav, tip = "回收资源管理", "回收服务器列表", "回收服务器"
    project = request.GET.get("project")

    iUser = UserProfile.objects.get(email="%s" % request.user)
    if iUser.is_admin:
        pro_info = Project.objects.all()
    else:
        pro_info = iUser.project.all()

    if project == "None" or project is None:
        project = pro_info[0].mini_name
        host_info = host.objects.filter(project__mini_name=project,recover=1).order_by('-online_date')

    elif project is not None:
        host_info = host.objects.filter(project__name=project,recover=1).order_by('-online_date')

    return render_to_response('hosts/host_recover.html', locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def host_edit(request):
    if request.method == 'POST':
        len_table = request.POST.get('len_table')
        for i in range(int(len_table)):
            p_old_ip = "editable[" + str(i) + "][p_old_ip]"
            platform = "editable[" + str(i) + "][platform]"
            p_ip = "editable[" + str(i) + "][p_ip]"
            s_ip = "editable[" + str(i) + "][s_ip]"
            port = "editable[" + str(i) + "][port]"
            db_ip = "editable[" + str(i) + "][db_ip]"
            login_pass = "editable[" + str(i) + "][login_pass]"
            commit = "editable[" + str(i) + "][commit]"

            print p_old_ip,platform,p_ip,s_ip,port,db_ip,commit,login_pass
            try:
                p_old_ip = request.POST.get(p_old_ip).strip()
                platform = request.POST.get(platform).strip()
                p_ip = request.POST.get(p_ip).strip()
                s_ip = request.POST.get(s_ip).strip()
                port = request.POST.get(port).strip()
                db_ip = request.POST.get(db_ip).strip()
                login_pass = request.POST.get(login_pass).strip()
                commit = request.POST.get(commit).strip()
            except Exception,e:
                print e

            print p_old_ip, platform, p_ip, s_ip, port, db_ip, commit, login_pass

            platform_id = platform_type.objects.get(mini_name=platform)
            host_edit = host.objects.filter(p_ip=p_old_ip)
            host_edit.update(platform=platform_id,p_ip=p_ip,s_ip=s_ip,port=int(port),db_ip=db_ip,login_pass=login_pass,commit=commit)

            info = "%s 修改成功" % p_old_ip
    return HttpResponseRedirect(reverse("host_list"))

@login_required
@PermissionVerify()
def host_add(request):
    header_title,nav,tip= "主机管理","添加服务器","单台添加"
    p_ip = request.POST.get("p_ip")
    s_ip = request.POST.get("s_ip")
    port = request.POST.get("port")
    db_ip = request.POST.get("db_ip")
    os_type = request.POST.get("os_type")
    pro_name = request.POST.get("pro_name")
    idc_name = request.POST.get("idc_name")
    area_name = request.POST.get("area_name")
    use_name = request.POST.getlist("use_name")
    plat_name = request.POST.get("plat_name")
    login_pass = request.POST.get("login_pass")
    commit = request.POST.get("commit")

    #print p_ip,s_ip,port,db_ip,os_type,pro_name,idc_name,use_name,area_name,plat_name,login_pass,commit
    if p_ip is not None:
        check_host = host.objects.filter(p_ip=p_ip)
        if len(check_host) == 1:
            error = "%s 已经存在不能重复添加！" % p_ip
        else:
            platform_id = platform_type.objects.get(plat_name=plat_name)
            project_id = Project.objects.get(name=pro_name)
            area_id = area_type.objects.get(area_name=area_name)
            idc_id = idc_list.objects.get(idc_name=idc_name)
            add_host = host(p_ip=p_ip,s_ip=s_ip,db_ip=db_ip,port=int(port),os_type=os_type,platform=platform_id,project=project_id,area=area_id,idc=idc_id,login_pass=login_pass,commit=commit)
            add_host.save()
            for iuse in use_name:
                use_id = server_use.objects.get(use_name=iuse)
                host_id = host.objects.get(p_ip=p_ip)
                host_id.use.add(use_id)
            info = "%s 添加服务器列表成功" % p_ip

    return render_to_response('hosts/host_add.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def host_add_multi(request):
    header_title,nav,tip,zone= "主机管理","添加服务器","批量添加","文本添加"

    for id in range(1,10):
        print id,"^.^"
        try:
            host_info = host.objects.filter(id=id)
            break
        except:
            continue

    data = request.POST.get("host_multi")
    if data:
        right_list,err_list = text_to_db(data)

    return render_to_response('hosts/host_add_multi.html',locals(),context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def host_add_excel(request):
    header_title,nav,tip,zone= "主机管理","添加服务器","批量添加","导入Excel"

    return render_to_response('hosts/host_add_excel.html',locals(),context_instance=RequestContext(request))


@login_required
@PermissionVerify()
def host_upload(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('file_name', '')
        ret = excel_to_db(excel_file)
        if ret:
            smg = u'批量添加成功'
        else:
            emg = u'批量添加失败,请检查格式.'

    return render_to_response('hosts/host_add_excel.html',locals(),context_instance=RequestContext(request))
