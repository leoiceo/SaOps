#_*_coding:utf-8_*_
from django.db import models
from manager.myauth import *
from hosts.models import *


class gameinfo(models.Model):
    project = models.ForeignKey(Project,default=None,blank=True,null=True,on_delete=models.SET_NULL)
    area = models.ForeignKey(area_type,blank=True,null=True,on_delete=models.SET_NULL)
    platform = models.ForeignKey(platform_type,blank=True,null=True,on_delete=models.SET_NULL)
    use = models.ForeignKey(server_use,blank=True,null=True,on_delete=models.SET_NULL)
    p_ip = models.GenericIPAddressField(unique=False)
    s_ip = models.GenericIPAddressField(blank=True,null=True)
    db_ip = models.GenericIPAddressField(blank=True,null=True)
    game_port = models.IntegerField(default=22)
    app_dir = models.CharField(max_length=255)
    status = models.IntegerField(default=0,null=True,blank=True)
    check_time = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    open_time = models.DateField(null=True,blank=True)
    server_id = models.IntegerField()
    server_name = models.CharField(max_length=128)
    version = models.IntegerField(null=True,blank=True)
    last_version = models.IntegerField(null=True,blank=True)

    class Meta:
        verbose_name = u'游戏服信息列表'
        verbose_name_plural = u'游戏服信息列表'
    def __unicode__(self):
        return self.p_ip

class FileName(models.Model):
    name = models.CharField(max_length=128)
    comment = models.CharField(max_length=200,blank=True,null=True)

    class Meta:
        verbose_name = u'配置文件名称列表'
        verbose_name_plural = u'配置文件名称列表'

    def __unicode__(self):
        return self.name

class GameConfig(models.Model):
    project = models.ForeignKey(Project,blank=True,null=True,on_delete=models.SET_NULL)
    area = models.ForeignKey(area_type,blank=True,null=True,on_delete=models.SET_NULL)
    platform = models.ForeignKey(platform_type,blank=True,null=True,on_delete=models.SET_NULL)
    gametype = models.CharField(default="online",max_length=64)
    filename = models.ForeignKey(FileName)
    contents = models.TextField()

    class Meta:
        verbose_name = u'游戏服配置文件'
        verbose_name_plural = u'游戏服配置文件'
    def __unicode__(self):
        return self.filename.name

class BackupProcess(models.Model):
    platform = models.CharField(max_length=100)
    p_ip = models.GenericIPAddressField()
    db_ip = models.GenericIPAddressField()
    server_name = models.CharField(max_length=100)
    backup_time = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    status = models.CharField(max_length=255)
    log = models.CharField(max_length=255)

    class Meta:
        verbose_name = u'游戏服备份日志'
        verbose_name_plural = u'游戏服备份日志'
    def __unicode__(self):
        return self.db_ip

class GamedbBackend(models.Model):
    p_ip = models.GenericIPAddressField()
    server_name = models.CharField(max_length=255)
    area_name = models.CharField(max_length=255)
    platform = models.CharField(max_length=255)
    bak_date = models.DateField(null=True,blank=True)
    bak_time = models.TimeField(blank=True,null=True)
    status = models.CharField(max_length=255,blank=True,null=True)
    filename = models.CharField(max_length=255,blank=True,null=True)
    filesize = models.CharField(max_length=255,blank=True,null=True)
    log = models.CharField(max_length=255,blank=True,null=True)
    class Meta:
        verbose_name= u"数据库备份管理"
        verbose_name_plural= u"数据库备份管理"
    def __unicode__(self):
        return self.server_name

class GameDropLog(models.Model):
    area_name = models.CharField(max_length=100)
    platform = models.CharField(max_length=100)
    p_ip = models.GenericIPAddressField()
    db_ip = models.GenericIPAddressField()
    server_name = models.CharField(max_length=200)
    delete_time = models.IntegerField(null=True,blank=True)
    status = models.CharField(max_length=100)
    log = models.CharField(max_length=255)

    class Meta:
        verbose_name = u"删除游戏服日志"
        verbose_name_plural = u"删除游戏服日志"
    def __unicode__(self):
        return self.server_name

class UpdateConfigLog(models.Model):
    area_name = models.CharField(max_length=128)
    platform = models.CharField(max_length=100)
    p_ip = models.GenericIPAddressField()
    server_name = models.CharField(max_length=200)
    update_time = models.IntegerField(null=True,blank=True)
    status = models.CharField(max_length=64)
    log = models.CharField(max_length=255)
    class Meta:
        verbose_name = u"更新配置日志"
        verbose_name_plural = u"更新配置日志"
    def __unicode__(self):
        return self.server_name

class UpdateSqlLog(models.Model):
    area_name = models.CharField(max_length=128)
    platform = models.CharField(max_length=100)
    db_ip = models.GenericIPAddressField()
    server_name = models.CharField(max_length=200)
    update_time = models.IntegerField(null=True,blank=True)
    status = models.CharField(max_length=64)
    log = models.CharField(max_length=255)
    class Meta:
        verbose_name = u"数据库更新日志"
        verbose_name_plural = u"数据库更新日志"
    def __unicode__(self):
        return self.server_name

class UpdateGameLog(models.Model):
    area_name = models.CharField(max_length=128)
    platform = models.CharField(max_length=100)
    p_ip = models.GenericIPAddressField()
    server_name = models.CharField(max_length=200)
    version = models.CharField(max_length=255)
    method = models.CharField(max_length=255)
    update_time = models.IntegerField(null=True,blank=True)
    status = models.CharField(max_length=64)
    log = models.CharField(max_length=255)
    class Meta:
        verbose_name = u"服务端更新日志"
        verbose_name_plural = u"服务端更新日志"
    def __unicode__(self):
        return self.server_name


class ServerList(models.Model):
    area_name = models.CharField(max_length=64)
    platform = models.CharField(max_length=100)
    server_name = models.CharField(max_length=100)
    server_id = models.IntegerField()
    p_ip = models.CharField(unique=False,max_length=100)
    isopen = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    port = models.IntegerField()
    open_time = models.CharField(max_length=100)
    zone_id = models.IntegerField()

    class Meta:
        verbose_name = u"游戏区服列表"
        verbose_name_plural = u"游戏区服列表"
    def __unicode__(self):
        return self.server_name


class ZoneList(models.Model):
    area_name = models.CharField(max_length=64)
    platform = models.CharField(max_length=100)
    maxzoneingroup = models.IntegerField()
    minzoneingroup = models.IntegerField()
    zonegroupid = models.IntegerField()
    zonegroupname = models.CharField(max_length=100)

    class Meta:
        verbose_name = u"游戏大区列表"
        verbose_name_plural = u"游戏大区列表"
    def __unicode__(self):
        return self.zonegroupname

class WhiteList(models.Model):
    area_name = models.CharField(max_length=64)
    ip = models.GenericIPAddressField(max_length=100)
    state = models.CharField(max_length=100)
    commit = models.CharField(max_length=100)
    class Meta:
        verbose_name = u"白名单列表"
        verbose_name_plural = u"白名单列表"
    def __unicode__(self):
        return self.commit


class GameNotice(models.Model):
    area_name = models.CharField(max_length=64)
    platform = models.CharField(max_length=64)
    filename = models.CharField(max_length=100)
    content = models.TextField()
    class Meta:
        verbose_name = u"游戏服公告"
        verbose_name_plural = u"游戏服公告"
    def __unicode__(self):
        return self.filename

class GameListFileDir(models.Model):
    area_name = models.CharField(max_length=64)
    platform = models.CharField(max_length=64)
    dirname = models.CharField(max_length=255)

    class Meta:
        verbose_name = u"列表存放路径"
        verbose_name_plural = u"列表存放路径"

    def __unicode__(self):
        return self.area_name


