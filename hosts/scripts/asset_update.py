#!/usr/bin/env python
#-*-coding:utf-8-*-

import threading
import sys,os,commands,paramiko,django
import Queue
import time,datetime
import json,logging
import sys
from ansible_api import *
import random, string
reload(sys)
sys.setdefaultencoding( "utf-8" )

BaseDir = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-2])
sys.path.append(BaseDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE","cmdb.settings") #环境变量
django.setup()
from cmdb import settings
from hosts.models import *

def random_sn(num):
    sn_str = ''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(num)))
    return sn_str.lower()

def get_ansible_asset_info(resource):
    ansible_instance = MyRunner(resource)
    datastructure = ansible_instance.run(module_name='setup', pattern='*')

    return datastructure

def update_asset_info(single_info,ip):
    write_log = UserAuditLog.objects.filter(p_ip=ip, log_time=log_time)
    datastructure = get_ansible_asset_info(single_info)
    try:
        data = datastructure['contacted'][ip]['ansible_facts']
    except Exception, e:
        write_log.update(result="ansible setup模块获取数据失败:%s" % e)

    try:
        write_log.update(status="10.0%",log="正在获取SN")
        sn = data["ansible_product_serial"]
        if sn == "NA":
            sn = random_sn(4) + '-' + random_sn(2) + '-' + random_sn(2) + '-' + random_sn(2) + '-' + random_sn(6)
    except Exception, e:
        write_log.update(result="ansible setup模块获取sn失败:%s" % e)
        sn = random_sn(4) + '-' + random_sn(2) + '-' + random_sn(2) + '-' + random_sn(2) + '-' + random_sn(6)


    try:
        write_log.update(status="18.0%", log="正在获取主机名")
        hostname = data["ansible_hostname"]
    except Exception, e:
        write_log.update(result="ansible setup模块获取主机名失败:%s" % e)
        hostname = "%s" % ip


    try:
        write_log.update(status="25.0%", log="正在获取物理内存容量")
        mem_total = data["ansible_memtotal_mb"]
    except Exception, e:
        write_log.update(result="ansible setup模块获取物理内存容量数据失败:%s" % e)
        mem_total = 0


    try:
        write_log.update(status="35.0%", log="正在获取交换内存容量")
        swap_total = data["ansible_swapfree_mb"]
    except Exception, e:
        write_log.update(result="ansible setup模块获取虚拟内容容量数据失败:%s" % e)
        swap_total = 0


    try:
        write_log.update(status="44.0%", log="正在获取CPU型号")
        cpu_type = data["ansible_processor"][-1]
    except Exception, e:
        write_log.update(result="ansible setup模块获取CPU型号数据失败:%s" % e)
        cpu_type = "未知"

    try:
        write_log.update(status="44.0%", log="正在获取CPU 个数")
        cpu_core = data["ansible_processor_cores"]
    except Exception, e:
        write_log.update(result="ansible setup模块获取CPU个数失败:%s" % e)
        cpu_core = 1


    try:
        write_log.update(status="56.0%", log="正在获取CPU核心数")
        cpu_total = data["ansible_processor_vcpus"]
    except Exception, e:
        write_log.update(result="ansible setup模块获取CPU核心数数据失败:%s" % e)
        cpu_total = 0


    try:

        os_type = " ".join((data["ansible_distribution"], data["ansible_distribution_version"]))
    except Exception, e:
        write_log.update(result="ansible setup模块获取操作系统类型数据失败:%s" % e)
        os_type = "未知"


    try:
        write_log.update(status="74.0%", log="正在获取硬盘信息")
        disk_total = {}
        disk_all = data["ansible_devices"]
        if disk_all:
            for disk_name, disk_info in disk_all.iteritems():
                if disk_name.startswith('sd') or disk_name.startswith('hd') or disk_name.startswith(
                        'vd') or disk_name.startswith('xvd'):
                    disk_size = disk_info.get("size", '')
                    if 'M' in disk_size:
                        disk_format = round(float(disk_size[:-2]) / 1000, 0)
                    elif 'T' in disk_size:
                        disk_format = round(float(disk_size[:-2]) * 1000, 0)
                    else:
                        disk_format = float(disk_size[:-2])
                    disk_total[disk_name] = disk_format
    except Exception, e:
        write_log.update(result="ansible setup模块获取硬盘总容量数据失败:%s" % e)
        disk_total = 0

    try:
        write_log.update(status="74.0%", log="正在获取硬盘挂载名及容量")
        disk_mount = str(
            [{"mount": i["mount"], "size": i["size_total"] / 1024 / 1024 / 1024} for i in data["ansible_mounts"]])
    except Exception, e:
        write_log.update(result="ansible setup模块获取硬盘挂载名及容量数据失败:%s" % e)
        disk_mount = "未知"

    try:
        write_log.update(status="74.0%", log="正在获取服务器型号")
        server_type = data["ansible_product_name"]
    except Exception, e:
        write_log.update(result="ansible setup模块获取服务器型号数据失败:%s" % e)
        server_type = "未知"

    try:
        write_log.update(status="74.0%", log="正在获取操作系统内核型号")
        os_kernel = data["ansible_kernel"]
    except Exception, e:
        write_log.update(result="ansible setup模块获取操作系统内核型号数据失败:%s" % e)
        os_kernel = "未知"

    try:
        write_log.update(status="74.0%", log="正在获取服务器ipv4地址")
        ipv4 = str(data["ansible_all_ipv4_addresses"])
    except Exception, e:
        write_log.update(result="ansible setup模块获取服务器ipv4地址数据失败:%s" % e)
        ipv4 = "未知"

    try:
        write_log.update(status="85.0%",log="正在获取系统平台")
        system_arch = data["ansible_architecture"]
    except Exception, e:
        write_log.update(result="ansible setup模块获取系统平台失败:%s" % e)
        system_arch = "未知"

    try:
        write_log.update(status="95.0%", log="正在获取获取MAC地址")
        mac = data["ansible_default_ipv4"]["macaddress"]
    except Exception,e:
        write_log.update(result="ansible setup模块获取MAC失败:%s" % e)
        mac = "未知"
    # 更新数据库
    #with open('/tmp/asset_update.log', "a") as f:
    #    f.write("%s %s %s %s %s %s %s %s %s %s %s %s" % ( mem_total, swap_total, cpu_type, cpu_core, cpu_total, os_type, disk_total, disk_mount, server_type, hostname, os_kernel, ipv4))

    # 资产管理员

    asset_dict = {
        "system_version": os_type,
        "cpu_type": cpu_type,
        "cpu_core": cpu_core,
        "cpu_total": cpu_total,
        "memory": mem_total,
        "disk_info": disk_total,
        "disk_mount": disk_mount,
        "server_type": server_type,
        "os_kernel": os_kernel,
        "system_arch": system_arch,
        "other_ip": ipv4,
        "mac":mac,
    }

    try:
        admin = UserAuditLog.objects.get(log_time=log_time, p_ip=ip).operator
        admin_id = UserProfile.objects.get(name=admin)
        check_asset = Asset.objects.filter(p_ip=ip)

        if len(check_asset) > 0:
            update_asset = Asset.objects.filter(p_ip=ip)
            update_asset.update(system_version=os_type,cpu_type=cpu_type,cpu_core=cpu_core,cpu_total=cpu_total,
                                memory=mem_total,disk_info=disk_total,disk_mount=disk_mount,server_type=server_type,
                                os_kernel=os_kernel,system_arch=system_arch,other_ip=ipv4,mac=mac,admin=admin_id)
            write_log.update(status="100.0%", log="资产信息更新成功",result="%s"%asset_dict)

        else:
            idc_name = host.objects.get(p_ip=ip).idc.idc_name
            idc_id = idc_list.objects.get(idc_name=idc_name)
            project = host.objects.get(p_ip=ip).project.name
            project_id = Project.objects.get(name=project)

            new_asset = Asset(asset_type=2,host_name=hostname,sn=sn,p_ip=ip,mac=mac,idc=idc_id,project=project_id,
                              other_ip=ipv4,system_version=os_type,cpu_type=cpu_type,cpu_core=cpu_core,cpu_total=cpu_total,
                              memory=mem_total, disk_info=disk_total, disk_mount=disk_mount, server_type=server_type,
                              os_kernel=os_kernel, system_arch=system_arch,admin=admin_id)
            new_asset.save()

            write_log.update(status="100.0%", log="资产信息采集成功",result="%s"%asset_dict)

        update_status=host.objects.filter(p_ip=ip)
        update_status.update(asset_status=1)

    except Exception,e:
        write_log.update(log="资产信息采集失败",result="%s"%e )


class mythread(threading.Thread):
    def __init__(self,func,args):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
    def run(self):
        apply(self.func,self.args)

if __name__ == "__main__":
    server_info = eval(sys.argv[1])
    log_time = sys.argv[2]

    #try:
    #    datastructure = get_ansible_asset_info(server_info)
    #except Exception,e:
    #    write_log.update(log="采集失败",result="%s"%e)

    threads = []

    for single_host in server_info:
        single_info = []
        single_info.append(single_host)
        ip = single_host["hostname"]
        write_log = UserAuditLog.objects.filter(log_time=log_time,p_ip=ip)
        write_log.update(log="开始执行ansible setup模块",status="12.0%")
        t = mythread(update_asset_info, (single_info,ip))
        threads.append(t)

    for i in threads:
        i.start()
    for i in threads:
        i.join()