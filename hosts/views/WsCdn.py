#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from manager.views.permission import *
import urllib2,json
from cmdb import settings
import commands,shutil,time,os
from hosts.wscdn_api import cdn_update_api
@login_required
@PermissionVerify()
def url_update(request):
    nav, tip =  "CDN管理", "内容管理"
    cdn_type = request.GET.get("type")
    project = request.GET.get("project")

    cdn_pro_info = Project.objects.filter(mini_name__in=['09games','linksdk'])

    if cdn_type == "url":
        header_title = "URL刷新"
        cdn_info = """<p align="left">尊敬的客户: </p>
<p align="left">每个URL一行，以协议：//开头，如（http://或者mms://）开头。例如：http://static.09games.com/a.js</p>
<p align="left">注意：推送的URL需要区分大小写</p>"""
    else:
        header_title = "目录刷新"
        cdn_info = """<p align="left">尊敬的客户: </p>
<p align="left">每个目录一行，以协议：//开头，如（http://或者mms://）开头。例如：http://static.09games.com/js/</p>
<p align="left">注意：1、推送的目录需要区分大小写；2、若配置缓存host，目录刷新需推送缓存host域名才可生效，请慎重！</p>"""

    if request.method == "POST":
        url_list = request.POST.get("url_list")

        the_date = time.strftime("%Y_%m_%d")
        the_time = time.strftime("%H_%M_%S")

        cdn_dir ="/tmp/cdn_url/%s_%s" %(the_date,the_time)
        check_and_mkdir(cdn_dir)
        with open("%s/url.txt" %(cdn_dir),'a') as f:
            f.write(url_list)
        urls = []
        if len(open("%s/url.txt"%cdn_dir, 'rU').readlines()) == 1:
            status = 0
        else:
            status = 1
        for url in open("%s/url.txt"%(cdn_dir)):
            if url.count("http") > 1:
                error_log = "错误：每个URL一行，请按要求填写，谢谢^V^"
                return render_to_response("hosts/cdn_url_update.html", locals(),
                                          context_instance=RequestContext(request))
            if status == 0:
                data = url.strip('\n').strip('\r')
            else:
                urls.append(url.strip('\n').strip('\r'))
                data = ";".join(urls)

        result = cdn_update_api(data,project)
        if "success" in result:
            log = "任务提交成功,请等待5-20分钟生效^0^,列表如下:\n %s " % url_list
        else:
            error_log = "%s" %result

    return render_to_response("hosts/cdn_url_update.html", locals(), context_instance=RequestContext(request))