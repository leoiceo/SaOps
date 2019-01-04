#_*_coding:utf-8_*_
from django.conf.urls import include, url, patterns

urlpatterns = patterns('hosts.views',
    #主机列表
    url(r'host_list/$','host.host_list',name='host_list' ),
    #主机添加、批量、excel上传导入
    url(r'host_add/$','host.host_add',name='host_add' ),
    url(r'host_add_multi/$','host.host_add_multi',name='host_add_multi' ),
    url(r'host_add_excel/$','host.host_add_excel',name='host_add_excel' ),
    url(r'host_upload/$','host.host_upload',name='host_upload' ),
    #主机编辑
    url(r'host_edit/$','host.host_edit',name='host_edit' ),
    #主机回收
    url(r'host_recover/$','host.host_recover',name='host_recover' ),
    #主机导出、下载
    url(r'host_export_excel/$','host.host_export_excel',name='host_export_excel' ),
    url(r'host_excel_download/$','host.host_excel_download',name='host_excel_download' ),
    #SSH key管理
    url(r'sshkey_list/$','conf.sshkey_list',name='sshkey_list' ),
    url(r'sshkey_edit/$','conf.sshkey_edit',name='sshkey_edit' ),
    #发行商管理
    url(r'publisher/$','conf.publisher_manage',name='publisher' ),
    url(r'publisher_edit/$','conf.publisher_edit',name='publisher_edit' ),
    #区域管理
    url(r'area_list/$','conf.area_list',name='area_list' ),
    url(r'area_edit/$','conf.area_edit',name='area_edit' ),
    #平台管理
    url(r'plat_list/$','conf.plat_list',name='plat_list' ),
    url(r'plat_edit/$','conf.plat_edit',name='plat_edit' ),
    #用途管理
    url(r'use_list/$','conf.use_list',name='use_list' ),
    url(r'use_edit/$','conf.use_edit',name='use_edit' ),
    #域名管理
    url(r'domain_list/$','DomainInfo.domain_list',name='domain_list' ),
    #IDC管理
    url(r'idc_list/$','conf.idc_manage',name='idc_list' ),
    url(r'idc_edit/$','conf.idc_edit',name='idc_edit' ),
    #费用管理
    url(r'cost_idc_api/$','conf.cost_idc_api',name='cost_idc_api' ),
    url(r'cost_pro_api/$','conf.cost_pro_api',name='cost_pro_api' ),
    url(r'cost_list/$','conf.cost_list',name='cost_list'),
    url(r'cost_edit/$','conf.cost_edit',name='cost_edit'),
    #发布仓库管理
    url(r'repos_list/$','WareHouse.repos_list',name='repos_list'),
    url(r'repos_edit/$','WareHouse.repos_edit',name='repos_edit'),

    #报表管理
    url(r'report_list/$','ReportSystem.report_list',name='report_list'),

    url(r'iplookup/$','tools.iplookup',name='iplookup' ),
    url(r'web_ssh/$','tools.web_ssh',name='web_ssh' ),

)
