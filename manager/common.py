#!/usr/bin/python
#_*_coding:utf-8_*_
from __future__ import absolute_import
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response,RequestContext
from django.db.models import Min,Max,Sum,Avg, F, FloatField
from django.contrib import auth
from inc import tasks
from cmdb import settings
#from manager.views.permission import *
from hosts.models import  *
from hosts.forms import *
from manager.myauth import *
from inc.models import *
import os,sys,commands,paramiko,subprocess,json,time
from hosts.host_api import *

def page_list_return(total, current=1):

    min_page = current - 2 if current - 4 > 0 else 1
    max_page = min_page + 4 if min_page + 4 < total else total

    return range(min_page, max_page+1)


def pages(posts, r):

    contact_list = posts
    p = paginator = Paginator(contact_list, 20)
    try:
        current_page = int(r.GET.get('page', '1'))
    except ValueError:
        current_page = 1

    page_range = page_list_return(len(p.page_range), current_page)

    try:
        contacts = paginator.page(current_page)
    except (EmptyPage, InvalidPage):
        contacts = paginator.page(paginator.num_pages)
    if current_page >= 5:
        show_first = 1
    else:
        show_first = 0
    if current_page <= (len(p.page_range) - 3):
        show_end = 1
    else:
        show_end = 0

    return contact_list, p, contacts, page_range, current_page, show_first, show_end


def check_and_mkdir(dir_name):
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

def check_and_file(file_name):
    if not  os.path.exists(file_name):
        os.mknod(file_name)

def remote_sftp(host,port,keyfile,username,localpath,remotepath,password):
    ssh = paramiko.Transport(host,int(port))
    key=paramiko.RSAKey.from_private_key_file(keyfile,password)
    if username == "root":
            ssh.connect(username="root", pkey=key)
    elif username == "Administrator":
            ssh.connect(username="Administrator", pkey=key)
    sftp = paramiko.SFTPClient.from_transport(ssh)
    localpath = "%s"%localpath
    remotepath = "%s"%remotepath
    sftp.put(localpath,remotepath)
    sftp.close()
    ssh.close()

def remote_run(host,port,keyfile,username,cmd,password,timeout):
    run = paramiko.SSHClient()
    run.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key=paramiko.RSAKey.from_private_key_file(keyfile,password)
    if username == "root":
        run.connect(host,int(port),username="root", pkey=key)
    elif username == "Administrator":
        run.connect(host,int(port),username="Administrator", pkey=key)
    if timeout is None:
        stdin,stdout,stderr = run.exec_command(cmd)
    else:
        stdin,stdout,stderr = run.exec_command(cmd,timeout=int(timeout))
    out_log = stdout.read().strip()
    err_log = stderr.read().strip()
    run.close()
    return out_log,err_log

def bash(cmd):
    """执行bash命令"""
    return subprocess.call(cmd, shell=True)

def local_shell(cmd):
    p = subprocess.Popen(["%s" % cmd], shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out_log, err_log = p.communicate()
    return out_log,err_log
