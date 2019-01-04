#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo

from hosts.models import *

def get_pro_info(request):
    iUser = UserProfile.objects.get(email="%s" % request.user)
    if iUser.is_admin:
        pro_info = Project.objects.all()
    else:
        pro_info = iUser.project.all()

    return pro_info