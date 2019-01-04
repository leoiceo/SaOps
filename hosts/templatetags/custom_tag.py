#_*_coding:utf-8_*_
import datetime,json,time
from django import template
from hosts.models import *
from slg.models import *
from manager.models import LoginHistory
from django.db.models import Min,Max,Sum,Avg, F, FloatField
register = template.Library()


@register.filter
def contains(value,arg):

    print '--->str',value,arg
    if arg in value:
        return  True
    else:
        return False

@register.filter
def sum_size(data_set):
    try:
        total_val = sum([i.capacity if i.capacity else 0 for i in data_set])
    except Exception,e:
        return e
    return total_val


@register.filter
def list_count(data_set):
    try:
        data_count = len([i.capacity if i.capacity else 0 for i in data_set])
    except Exception,e:
        return e
    return data_count

@register.filter
def sum_disk(data_set):
    try:
        disk_dict = eval(data_set)
        disk_total = 0
        for k,v in disk_dict.items():
            disk_total += int(v)
    except Exception,e:
        return e
    return disk_total


@register.filter
def sum_prolog(data_set):
    try:
        pro_count = SshAuditLog.objects.filter(project__mini_name=data_set).count()
    except Exception,e:
        return e
    return pro_count

@register.filter
def get_cmd_log(date_set):
    try:
        cmd_log = SshAuditLog.objects.filter(p_ip=date_set).order_by("-log_time")[:1]
        for i in cmd_log: cmd = i.cmd_log
    except Exception,e:
        return e
    return cmd

@register.filter
def get_log_time(date_set):
    try:
        data = SshAuditLog.objects.filter(p_ip=date_set).order_by("-log_time")[:1]
        for i in data: log_time = i.log_time
    except Exception,e:
        return e
    return log_time

@register.filter
def get_login_ip(date_set):
    try:
        data = SshAuditLog.objects.filter(p_ip=date_set).order_by("-log_time")[:1]
        for i in data: login_ip = i.login_ip
    except Exception,e:
        return e
    return login_ip

@register.filter
def get_username(date_set):
    try:
        data = SshAuditLog.objects.filter(p_ip=date_set).order_by("-log_time")[:1]
        for i in data: username = i.username
    except Exception,e:
        return e
    return username

@register.filter
def get_user_login_ip(date_set):
    try:
        data = LoginHistory.objects.filter(name=date_set).order_by("-time")[:1]
        for i in data: ipaddr = i.ip

        return ipaddr
    except Exception,e:
        return e


@register.filter
def top_mem_use(data_set):
    try:
        data = ReportMem.objects.filter(p_ip=data_set).aggregate(Max('memuseprecent'))
        max_mem_use = data['memuseprecent__max']
        return max_mem_use

    except Exception,e:
        return e

@register.filter
def avg_mem_use(data_set):
    try:
        data = ReportMem.objects.filter(p_ip=data_set).aggregate(Avg('memuseprecent'))
        avg_mem_use = "%.2f" % data['memuseprecent__avg']
        return avg_mem_use

    except Exception,e:
        return e

@register.filter(name='print_time')
def print_time(value):
    try:
        x = time.localtime(float(value))
    except Exception,e:
        return e
    return time.strftime('%Y-%m-%d %H:%M:%S',x)

@register.filter(name='contrast_number')
def warning_num(data_set):
    if data_set > 60:
        return 1
    else:
        return 0
