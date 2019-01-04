#_*_coding:utf-8_*_
from django.db import models
from manager.myauth import *
from hosts.models import *
# Create your models here.


class FileTransLog(models.Model):
    project = models.CharField(max_length=32)
    p_ip = models.GenericIPAddressField()
    filename = models.CharField(max_length=64)
    remote_path = models.CharField(max_length=64)
    status = models.CharField(max_length=64)
    log = models.CharField(max_length=64)
    trans_time = models.IntegerField()
    end_time = models.IntegerField(blank=True, null=True)
    total_time = models.FloatField(blank=True, null=True)
    operator = models.CharField(max_length=84,blank=True,null=True)
    class Meta:
        verbose_name = u"文件分发日志"
        verbose_name_plural = u"文件分发日志"
    def __unicode__(self):
        return self.filename


class ScriptExeclog(models.Model):
    project = models.CharField(max_length=32)
    p_ip = models.GenericIPAddressField()
    script_name = models.CharField(max_length=64)
    status = models.CharField(max_length=32)
    log = models.CharField(max_length=64)
    result = models.TextField(blank=True,null=True)
    start_time = models.IntegerField()
    end_time = models.IntegerField(blank=True,null=True)
    total_time = models.FloatField(blank=True, null=True)
    operator = models.CharField(max_length=84,blank=True,null=True)

    class Meta:
        verbose_name = u"脚本分发日志"
        verbose_name_plural = u"脚本分发日志"
    def __unicode__(self):
        return self.script_name


class CmdExecLog(models.Model):
    project = models.CharField(max_length=32)
    p_ip = models.GenericIPAddressField()
    cmd = models.CharField(max_length=64)
    status = models.CharField(max_length=64)
    log = models.CharField(max_length=64)
    result = models.TextField(blank=True,null=True)
    start_time = models.IntegerField()
    end_time = models.IntegerField(blank=True,null=True)
    total_time = models.FloatField(blank=True,null=True)
    operator = models.CharField(max_length=84,blank=True,null=True)
    class Meta:
        verbose_name = u"批量命令日志"
        verbose_name_plural = u"批量命令日志"
    def __unicode__(self):
        return self.cmd


class WebSite(models.Model):
    project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL,
                                verbose_name=u"项目")
    platform = models.ForeignKey(platform_type, blank=True, null=True, on_delete=models.SET_NULL,verbose_name=u"平台")
    repos_name = models.ForeignKey(ReposManager,blank=True,null=True,on_delete=models.SET_NULL,verbose_name=u'发布仓库')
    # web_type  = models.IntegerField(verbose_name=u'类型|正式和测试')
    domain = models.CharField(u'域名',max_length=32,blank=True,null=True)
    p_ip = models.GenericIPAddressField(u'公网地址')
    s_ip = models.GenericIPAddressField(u'内网地址')
    web_dir = models.CharField(u'站点目录',max_length=64, blank=True, null=True)
    remark = models.CharField(u'备注',max_length=128, blank=True, null=True)
    version = models.IntegerField(u'当前版本',default=0)
    last_version = models.IntegerField(u'上一次版本',default=0)
    admin_user = models.ManyToManyField(UserProfile,related_name="ops_user",verbose_name=u"管理员")
    status = models.IntegerField(default=0, blank=True, null=True)
    check_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = u"站点管理"
        verbose_name_plural = u'站点管理'

        def __unicode__(self):
            return self.domain

WEB_CONFIG_TYPE=(
    (1,'Nginx虚拟主机'),
    (2,'站点配置文件'),
)
class WebConfig(models.Model):
    project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL,
                                verbose_name=u"项目")
    platform = models.ForeignKey(platform_type, blank=True, null=True, on_delete=models.SET_NULL,verbose_name=u"平台")
    cf_type = models.IntegerField(choices=WEB_CONFIG_TYPE, blank=True, null=True, verbose_name=u"配置类型")
    cf_dir = models.CharField(u'配置目录',max_length=64)
    cf_name = models.CharField(u'文件名称',max_length=32)
    cf_content = models.TextField(u'内容')

    class Meta:
        verbose_name = u"WEB配置管理"
        verbose_name_plural = u'WEB配置管理'

        def __unicode__(self):
            return self.cf_name