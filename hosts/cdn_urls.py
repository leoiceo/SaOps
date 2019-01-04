#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo


from django.conf.urls import include, url, patterns

urlpatterns = patterns('hosts.views',
   url(r'url_update', 'WsCdn.url_update', name='cdn_url_update'),
)