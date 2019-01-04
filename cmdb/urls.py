"""cmdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url, patterns
#from assets import rest_urls,urls as asset_urls
from hosts import hosts_urls,assets_urls,perm_urls,api_urls,salog_urls,cdn_urls,sdk_urls
from manager import manager_urls,help_urls
from inc import inc_urls
from multitask import multi_urls
from multitask import web_urls
from scripting import script_urls
from scripting import cron_urls

import views
from django.conf.urls import handler404, handler500

handler404 = "cmdb.views.page_not_found"
handler500 = "cmdb.views.page_error"

urlpatterns = patterns('',
       (r'^$', views.index),
       (r'^skin_config/$', views.skin_config),
       (r'^login/$', views.account_login),
       (r'^checkcode/$', views.CheckCode),
       (r'^accounts/login/$', views.account_login),
       (r'^logout/$', views.account_logout),
       (r'^monitor/$', views.monitor),
       (r'^warning/$', views.monitor),
       #(r'^monitor/mail$', views.mail),
       (r'^asset/', include(assets_urls)),
       (r'^manager/', include(manager_urls)),
       (r'^inc/', include(inc_urls)),
       (r'^hosts/', include(hosts_urls)),
       (r'^perm/', include(perm_urls)),
       (r'^multitask/', include(multi_urls)),
       (r'^web/', include(web_urls)),
       (r'^scripting/', include(script_urls)),
       (r'^crontab/', include(cron_urls)),
       (r'^api/', include(api_urls)),
       (r'^help/', include(help_urls)),
       (r'^salog/', include(salog_urls)),
       (r'^cdn/', include(cdn_urls)),
       (r'^sdk/', include(sdk_urls)),
    url(r'^personal/$', views.personal, name="personal"),
    url(r'^highchart_api/$', views.highchart_api, name="highchart_api"),
    url(r'^highchart_pie/$', views.highchart_pie, name="highchart_pie"),
)


