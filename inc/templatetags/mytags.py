#!/usr/bin/python
#_*_coding:utf-8_*_

from django import template
from hosts.models import *
from inc.models import *
import time
import datetime
register = template.Library()

@register.filter(name='status_diff')
def status_diff(value):
    try:
        now_time = time.strftime("%Y-%m-%d %H:%M:%S")
        last_time = value
        date1 = time.strptime(now_time,"%Y-%m-%d %H:%M:%S")
        date2 = time.strptime(last_time,"%Y-%m-%d %H:%M:%S")
        date1=datetime.datetime(date1[0],date1[1],date1[2],date1[3],date1[4],date1[5])
        date2=datetime.datetime(date2[0],date2[1],date2[2],date2[3],date2[4],date2[5])
        num = date1 - date2
        if num.seconds <= 300:
            return 1
        else:
            return 0
    except:
        return 0


@register.filter(name='print_time')
def print_time(value):
    try:
        x = time.localtime(float(value))
    except Exception,e:
        return e
    return time.strftime('%Y-%m-%d %H:%M:%S',x)

@register.filter(name='gamelist_state')
def gamelist_state(value):
    value = int(value)
    if value == 0:
        state = "空"
    elif value == 2:
        state = "新服"
    elif value == 3:
        state = "爆满"
    elif value == 4:
        state = "维护"
    elif value == 5:
        state = "推荐"
    else:
        state = "未知"
    return state

@register.filter(name='gameserver_status')
def gameserver_status(value):
    value = int(value)
    if value == 1:
        status = "已开启"
    elif value == 0:
        status = "已关闭"
    elif value == 2:
        status = "已合服"
    else:
        status = "未知"
    return status

@register.filter(name='gjsj_gamelist_state')
def gamelist_state(value):
    value = int(value)
    if value == 0:
        state = "热"
    elif value == 2:
        state = "新服"
    elif value == 3:
        state = "热"
    elif value == 4:
        state = "维护"
    elif value == 5:
        state = "推荐"
    else:
        state = "未知"
    return state

@register.filter(name='get_data_log')
def get_data_log(date_set):
    try:
        data_log = date_set.split('|')[0]
    except:
        data_log = date_set
    return data_log

@register.filter(name='get_error_log')
def get_error_log(date_set):
    try:
        data_log = date_set.split('|')[1]
    except:
        data_log = date_set
    return data_log


@register.filter(name='zsgl_gamelist_state')
def gamelist_state(value):
    value = int(value)
    if value == 0:
        state = "维护"
    elif value == 1:
        state = "普通"
    elif value == 2:
        state = "火爆"
    elif value == 3:
        state = "新服"
    else:
        state = "未知"
    return state

@register.filter(name='web_status')
def web_status(value):
    value = int(value)
    if value == 1:
        status = "正常"
    elif value == 0:
        status = "异常"

    return status