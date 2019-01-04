#!/usr/bin/python
#_*_coding:utf-8_*_
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

def mail(request):
    """
    邮件报警接口
    :param request:
    :return:
    """
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    try:
        check_ip = host.objects.get(p_ip=ip)
    except Exception,e:
        error = {"error": e}
        return HttpResponse(json.dumps(error), content_type='application/json')

    if request.POST:
        content = request.POST.get("content")
        tos = request.POST.get("tos")
        subject = request.POST.get("subject")
        try:
            if ',' not in tos:
                send_mail(subject, content, '%s'%settings.EMAIL_HOST_USER, ['%s'%tos], fail_silently=False)
            else:
                mail_list = list(tos.split(','))
                send_mail(subject, content, '%s'%settings.EMAIL_HOST_USER, mail_list, fail_silently=False )
            log = {"log":"ok"}
            return HttpResponse(json.dumps(log),content_type='application/json')
        except Exception,e:
            error = {"error": e}
            return HttpResponse(json.dumps(error),content_type='application/json')
    else:
        error = {"error":404}
        return HttpResponse(json.dumps(error),content_type='application/json')