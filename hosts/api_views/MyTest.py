#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo

from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib import auth
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.mail import send_mail,send_mass_mail
#from assets.models import UserProfile,Asset
import StringIO
import json
import sys,os
from cmdb import settings
from hosts.models import *


def PostData(request):
    '''
    测试 POST GET API
    :param request:
    :return:
    '''
    if request.method == 'POST':

        try:
            content = request.body.decode()
            content = json.loads(content)
            name = content['name']
        except:
            name = request.POST.get("name")

    elif request.method == "GET":
        name = request.GET.get("name")

    result = {
        'status': 'ok',
        'name': name,
        'type': request.method
    }

    # 获取头部信息
    fp = open('/tmp/out.txt', 'w')
    fp.write('request:%s\n' % str(request.META.get('HTTP_CONTENT_TYPE','unknow')))
    fp.write('request:%s\n' % str(request.META))
    fp.close()

    return HttpResponse(json.dumps(result), content_type='application/json')

def PostFile(request):
    '''
    文件上传
    :param request:
    :return:
    '''
    rtype = request.method
    if request.method == "POST":
        upload_files = request.FILES.get('filename', None)
        with open("%s/%s"%(settings.FILE_TRANS_DIR,upload_files.name),"w") as f:
            for chunk in upload_files.chunks():
                f.write(chunk)
        status = "ok"
        filename = upload_files.name
    else:
        status = "other"
        filename = "test"
    result = {
        'status': status,
        'name': filename,
        'type': '%s'%rtype
    }

    return HttpResponse(json.dumps(result), content_type='application/json')