#_*_coding:utf-8_*_
from django.db import models

# Create your models here.
from myauth import UserProfile,Project



class CateGory(models.Model):
    name = models.CharField(u'类名',max_length=64)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = "分类"

    def __unicode__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(u'标签名',max_length=32)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = "标签"

    def __unicode__(self):
        return self.name

class Article(models.Model):
    name = models.CharField(u'标题',max_length=128)
    content = models.TextField(u'内容')
    category = models.ForeignKey(CateGory,blank=True,null=True,verbose_name='分类')
    tag = models.ForeignKey(Tag,blank=True,null=True,verbose_name='标签')
    create_date = models.DateTimeField(auto_now_add=True)
    change_date = models.DateTimeField(auto_now_add=True)
    create_user = models.ForeignKey(UserProfile,blank=True,null=True,verbose_name='创建人')

    class Meta:
        verbose_name = '平台文档'
        verbose_name_plural = "平台文档"

    def __unicode__(self):
        return self.name

class LoginHistory(models.Model):
    name = models.CharField(max_length=64,blank=True,null=True)
    ip = models.GenericIPAddressField(blank=True,null=True)
    time = models.DateTimeField(auto_now_add=True)
    stats = models.CharField(max_length=32,blank=True,null=True)
    get_full_path = models.CharField(max_length=255,blank=True,null=True)

    class Meta:
        verbose_name = '登陆历史记录'
        verbose_name_plural = '登陆历史记录'

    def __unicode__(self):
        return self.name