#_*_coding:utf-8_*_
from django.db import models

# Create your models here.
from manager.myauth import *

class ScriptsManage(models.Model):
    project = models.ForeignKey(Project,default=None,blank=True,null=True,on_delete=models.SET_NULL)
    script_name = models.CharField(max_length=64)
    script_type = models.CharField(max_length=64)
    use_name = models.CharField(max_length=128)
    input_args = models.CharField(max_length=128,null=True,blank=True)
    content = models.TextField()
    create_time = models.DateTimeField(null=True,blank=True)
    modify_time = models.DateTimeField(null=True,blank=True)
    operator = models.ForeignKey(UserProfile)
    class Meta:
        verbose_name = u"脚本管理"
        verbose_name_plural = u"脚本管理"
    def __unicode__(self):
        return self.script_name


class TaskPlanRunLog(models.Model):
    project = models.ForeignKey(Project,default=None,blank=True,null=True,on_delete=models.SET_NULL)
    script_name = models.CharField(max_length=64)
    ip = models.GenericIPAddressField()
    log = models.CharField(max_length=200)
    result = models.CharField(max_length=255,blank=True,null=True)
    run_time = models.IntegerField()

    class Meta:
        verbose_name = u"计划任务日志"
        verbose_name_plural = u"计划任务日志"
    def __unicode__(self):
        return self.script_name
