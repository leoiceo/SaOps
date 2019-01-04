#!/usr/bin/python
#_*_coding:utf-8_*_
import datetime,xlsxwriter,csv,codecs
import sys,django,os
reload(sys)
sys.setdefaultencoding( "utf-8" )

BaseDir = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-2])
sys.path.append(BaseDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE","cmdb.settings") #环境变量
django.setup()

import xlrd
from models import *
from manager.myauth import *
from cmdb.settings import *

def host_export_file(project):
    data = []
    now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
    from manager.common import check_and_mkdir
    check_and_mkdir(EXCEL_DIR)
    title = [u'主机名', u'公网地址', u'内网地址', u'数据库地址', u'所属项目', u'地区', u'平台',
             u'IDC', u'操作系统', u'SSH端口', u'用途', u'开服数量', '备注']

    if project == "all" or project == "None":
        host_info = host.objects.all().exclude(recover=1)
    else:
        host_info = host.objects.filter(project__mini_name=project).exclude(recover=1)

    for h in host_info:
        use_list = []
        for u in h.use.all():
            use_list.append(u.use_name)

        use_all = ','.join(use_list)
        alter_dic = [h.hostname, h.p_ip, h.s_ip, h.db_ip, h.project.name, h.area.area_name, h.platform.plat_name,
                     h.idc.idc_name, h.os_type, h.port, use_all, h.game_count, h.commit]
        data.append(alter_dic)

    if host_info.count() > 5000:
        file_name = 'cmdb_excel_%s_' % project + now + '.csv'
        ret = write_csv(file_name,title,data)
    else:
        file_name = 'cmdb_excel_%s_' % project + now + '.xlsx'
        if project == "all" or project == "None":
            pro_name = "全部项目"
        else:
            pro_name = Project.objects.get(mini_name=project).name
        ret = write_excel(file_name,title,data,pro_name)

    return ret

def write_csv(file_name,title,data):
    ofile = open('%s/%s' %(EXCEL_DIR,file_name),'wb')
    ofile.write(codecs.BOM_UTF8)
    workbook = csv.writer(ofile,dialect='excel',delimiter=',',quoting=csv.QUOTE_NONE)
    workbook.writerow(title)
    try:
        for alter_list in data:
            workbook.writerow(alter_list)

        ofile.close()
        ret = (True,file_name)
        return ret
    except Exception,e:
        ret = (False, "%s" %e)
        return ret

def write_excel(file_name,title,data,project):
    """
    生成excel
    :param project:
    :return:
    """
    workbook = xlsxwriter.Workbook('%s/%s' % (EXCEL_DIR,file_name))
    worksheet = workbook.add_worksheet(u'%s 主机列表'%project)
    worksheet.set_first_sheet()
    worksheet.set_column('A:E', 15)
    worksheet.set_column('K:K', 30)
    worksheet.set_column('G:Z', 15)

    format = workbook.add_format()
    format.set_border(1)
    format.set_align('center')
    format.set_align('vcenter')
    format.set_text_wrap()

    format_title = workbook.add_format()
    format_title.set_border(1)
    format_title.set_bg_color('#cccccc')
    format_title.set_align('center')
    format_title.set_bold()

    format_ave = workbook.add_format()
    format_ave.set_border(1)
    format_ave.set_num_format('0.00')

    worksheet.write_row('A1', title, format_title)
    i = 2
    for alter_list in data:
        location = 'A' + str(i)
        worksheet.write_row(location, alter_list, format)
        i += 1

    workbook.close()
    ret = (True, file_name)
    return ret

def excel_to_db(excel_file):
    """
    add batch function
    """
    err_list = []
    right_list = []

    try:
        data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
    except Exception, e:
        return False
    else:
        table = data.sheets()[0]
        rows = table.nrows
        for row_num in range(1, rows):
            row = table.row_values(row_num)
            if row:
                hostname,p_ip,s_ip,db_ip,port,os_type,pro_name,idc_name,use_name,area_name,plat_name,login_pass,commit = row
                #print hostname,p_ip,s_ip,db_ip,port,os_type,pro_name,idc_name,use_name,area_name,plat_name,login_pass,commit,"======>DB"
                if p_ip:
                    check_host = host.objects.filter(p_ip=p_ip)
                    if len(check_host) != 0:
                        err_log = "%s 已经存在不能重复添加！" % p_ip
                        err_list.append(err_log)
                        continue
                    check_hostname = host.objects.filter(hostname=hostname)
                    if len(check_hostname) != 0:
                        err_log = "%s 已存在,不能重复" % hostname
                        err_list.append(err_log)
                        continue
                    else:
                        try:
                            platform_id = platform_type.objects.get(plat_name=plat_name)
                            project_id = Project.objects.get(name=pro_name)
                            area_id = area_type.objects.get(area_name=area_name)
                            idc_id = idc_list.objects.get(idc_name=idc_name)
                            add_host = host(hostname=hostname,
                                            p_ip=p_ip,
                                            s_ip=s_ip,
                                            db_ip=db_ip,
                                            port=int(port),
                                            os_type=os_type,
                                            platform=platform_id,
                                            project=project_id,
                                            area=area_id,
                                            idc=idc_id,
                                            login_pass=login_pass,
                                            commit=commit)
                            add_host.save()
                            for iuse in use_name.split(","):
                                use_id = server_use.objects.get(use_name=iuse)
                                host_id = host.objects.get(p_ip=p_ip)
                                host_id.use.add(use_id)
                            right_log = "添加正确: %s"% p_ip
                            right_list.append(right_log)
                            print err_list,right_list
                        except Exception,e:
                            print "error",e
        return True


def text_to_db(data):
    host_info = data.encode("utf-8").split("\r\n")
    err_list = []
    right_list = []
    for h in host_info:
        try:
            info_all = []
            host_all = h.split(" ")
            while '' in host_all:
                host_all.remove('')
            for m in host_all:
                n = m.split('\t')
                while '' in n:
                    n.remove('')
                info_all = info_all + n
            print "host_info:",info_all
            #print hostname,p_ip, s_ip,db_ip,port,os_type,pro_name,idc_name,use_name,area_name,plat_name,login_pass,commit
            hostname = info_all[0].strip("\t").strip("\xc2\xa0")
            check_hostname = host.objects.filter(hostname=hostname)
            if len(check_hostname) != 0:
                err_log = "主机名 %s 已存在,不能重复" % hostname
                err_list.append(err_log)
                continue
            p_ip = info_all[1].strip("\t").strip("\xc2\xa0")
            check_ip = host.objects.filter(p_ip=p_ip)
            if len(check_ip) != 0:
                err_log = "公网IP %s 已存在,不能重复" % p_ip
                err_list.append(err_log)
                continue
            s_ip = info_all[2].strip("\t").strip("\xc2\xa0")
            db_ip = info_all[3].strip("\t").strip("\xc2\xa0")
            port = info_all[4].strip("\t").strip("\xc2\xa0")
            os_type = info_all[5].strip("\t").strip("\xc2\xa0")
            pro_name = info_all[6].strip("\t").strip("\xc2\xa0")
            idc_name = info_all[7].strip("\t").strip("\xc2\xa0")
            use_name = info_all[8].strip("\t").strip("\xc2\xa0")
            area_name = info_all[9].strip("\t").strip("\xc2\xa0")
            plat_name = info_all[10].strip("\t").strip("\xc2\xa0")
            login_pass = info_all[11].strip("\t").strip("\xc2\xa0")
            commit = info_all[12].strip("\t").strip("\xc2\xa0")

            try:
                platform_id = platform_type.objects.get(plat_name=plat_name)
            except:
                err_log = "%s不存在" % plat_name
                err_list.append(err_log)

            try:
                project_id = Project.objects.get(name=pro_name)
            except:
                err_log = "%s不存在" % pro_name
                err_list.append(err_log)

            try:
                area_id = area_type.objects.get(area_name=area_name)
            except:
                err_log = "%s不存在" % area_name
                err_list.append(err_log)

            try:
                idc_id = idc_list.objects.get(idc_name=idc_name)
            except:
                err_log = "%s不存在" % idc_name
                err_list.append(err_log)
            print "add_host=====> to db"
            add_host = host(hostname=hostname,
                            p_ip=p_ip,
                            s_ip=s_ip,
                            db_ip=db_ip,
                            port=int(port),
                            os_type=os_type,
                            platform=platform_id,
                            project=project_id,
                            area=area_id,
                            idc=idc_id,
                            login_pass=login_pass,
                            commit=commit)
            add_host.save()
            for iuse in use_name.split(","):
                use_id = server_use.objects.get(use_name=iuse)
                host_id = host.objects.get(p_ip=p_ip)
                host_id.use.add(use_id)
            right_log = "添加正确: %s"% p_ip
            right_list.append(right_log)
        except Exception,e:
            print e
            err_log = "格式错误: %s"% h
            err_list.append(err_log)

    return right_list,err_list

def write_ssh_key(data_set,name):
    with open("%s/%s"%(KEY_DIR,name),'w') as f:
        f.write(data_set)
        f.close()
    os.system("chmod 600 %s/%s"%(KEY_DIR,name))


def file_iterator(file_name, chunk_size=512):
    with open(file_name) as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break