#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo


from django import forms
from multitask.models import *

class WebSiteForm(forms.ModelForm):

    class Meta:

        model = WebSite
        fields = [
            'project', 'platform', 'domain', 'p_ip', 'repos_name','s_ip', 'web_dir', 'remark','version','admin_user'
        ]



class WebConfigForm(forms.ModelForm):

    class Meta:

        model = WebConfig

        fields = [
            'project', 'platform', 'cf_type', 'cf_dir', 'cf_name', 'cf_content'
        ]