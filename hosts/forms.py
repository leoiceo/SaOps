#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django import forms
from hosts.models import *


class ReposManagerForm(forms.ModelForm):

    class Meta:
        model = ReposManager

        fields = [
            'repos_name', 'project', 'repos_type', 'repos_addr', 'repos_user', 'repos_pass'
        ]


class CostMangerForm(forms.ModelForm):

    class Meta:
        model = CostManger

        fields = [
            'project','cost_type','idc','cpu','mem','disk','bandwidth','network_bill','price',
            'total','status'
        ]

class AssetForm(forms.ModelForm):

    class Meta:
        model = Asset

        fields = [
            "asset_type", "sn", "host_name", "p_ip", "mac", "idc", "project", "other_ip",
            "system_version", "cpu_type", "cpu_core", "cpu_total", "memory", "disk_info", "disk_mount", "server_type", "os_kernel",
            "system_arch", "status", "admin",
        ]


class KeyManagerForm(forms.ModelForm):

    class Meta:
        model = KeyManager

        fields = [
            "project","name","username","password","private_key","public_key","operator",
        ]

class CommonUserForm(forms.ModelForm):

    class Meta:
        model = CommonUser

        fields = [
            "project","username","password","private_key","public_key","create_user","operator",
        ]


class DomainInfoForm(forms.ModelForm):

    class Meta:
        model = DomainInfo

        fields = [
            "project","domain_name","record_type","order_key","remark","contacts","status","operator"
        ]