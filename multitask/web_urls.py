#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo


from django.conf.urls import include, url, patterns

urlpatterns = patterns('multitask.views',
    url(r'site_list/$','WebManger.site_list',name='web_site_list' ),
    url(r'site_crontrol/$','WebManger.site_crontrol',name='web_site_crontrol' ),
    url(r'site_crontrol_status/$','WebManger.site_crontrol_status',name='web_site_crontrol_status' ),
    url(r'site_crontrol_log/$','WebManger.site_crontrol_log',name='web_site_crontrol_log' ),
    url(r'site_edit/$','WebManger.site_edit',name='web_site_edit' ),

    url(r'conf_list/$','WebConfig.conf_list',name='web_conf_list' ),
    url(r'conf_edit/$','WebConfig.conf_edit',name='web_conf_edit' ),

    url(r'update_file/$','WebUpdate.update_file',name='web_update_file' ),
    url(r'update_file_info/$','WebUpdate.update_file_info',name='web_update_file_info' ),
    url(r'update_file_status/$','WebUpdate.update_file_status',name='web_update_file_status' ),
    url(r'update_file_process/$','WebUpdate.update_file_process',name='web_update_file_process' ),


    url(r'update_conf/$','WebUpdate.update_conf',name='web_update_conf' ),
    url(r'update_conf_info/$','WebUpdate.update_conf_info',name='web_update_conf_info' ),
    url(r'update_conf_status/$','WebUpdate.update_conf_status',name='web_update_conf_status' ),

)
