#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo


from django.conf.urls import include, url, patterns

urlpatterns = patterns('hosts.views',
   url(r'sdk_pay/$', 'SdkView.sdk_pay', name='sdk_pay'),
   url(r'sdk_pay_api/$', 'SdkView.sdk_pay_api', name='sdk_pay_api'),
)