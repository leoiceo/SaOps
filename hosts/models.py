#_*_coding:utf-8_*_
from django.db import models
from manager.myauth import *
# Create your models here.

ASSET_STATUS = (
    (1, u"已使用"),
    (2, u"未使用"),
    (3, u"已报废"),
    (4, u"已下架")
    )

ASSET_TYPE = (
    (1, u"物理机"),
    (2, u"虚拟机"),
    (3, u"交换机"),
    (4, u"路由器"),
    (5, u"防火墙"),
    (6, u"Docker"),
    (7, u"其他")
    )

RECORD_TYPE = (
    (1, u'CNAME'),
    (2, u'A')
)

COST_TYPE = (
    (1, u'云服务器'),
    (2, u'云数据库'),
    (3, u'内存存储'),
    (4, u'CDN'),
    (5, u'云硬盘')
)

REPOS_TYPE = (
    (1,u'svn'),
    (2,u'git'),
)
class ReposManager(models.Model):
    repos_name = models.CharField(u'名称或用途',max_length=64,unique=True)
    project = models.ForeignKey(Project, default=None, blank=True, null=True, on_delete=models.SET_NULL,
                                verbose_name=u"项目")
    repos_type = models.IntegerField(choices=REPOS_TYPE, blank=True, null=True, verbose_name=u"仓库类型")
    repos_addr = models.CharField(u'地址',max_length=128,blank=True,null=True)
    repos_user = models.CharField(u'认证用户',max_length=32,blank=True,null=True)
    repos_pass = models.CharField(u'认证密码',max_length=32,blank=True,null=True)

    class Meta:
        verbose_name = u'发布仓库管理'
        verbose_name_plural = u'发布仓库管理'
    def __unicode__(self):
        return self.repos_name

class server_use(models.Model):
    use_name = models.CharField(max_length=128,unique=True)
    class Meta:
        verbose_name = u'服务器用途'
        verbose_name_plural = u'服务器用途'
    def __unicode__(self):
        return self.use_name

class area_type(models.Model):
    area_name = models.CharField(max_length=64,unique=True)
    mini_name = models.CharField(max_length=32,unique=True)
    class Meta:
        verbose_name = u'地区管理'
        verbose_name_plural = u'地区管理'
    def __unicode__(self):
        return self.area_name

class idc_list(models.Model):
    idc_name = models.CharField(max_length=64,unique=True, verbose_name=u'机房名称')
    mini_name = models.CharField(max_length=32,unique=True)
    net_line = models.CharField(max_length=32,blank=True, null=True,verbose_name=u'机房线路')
    bandwidth = models.CharField(max_length=32, blank=True, null=True, default='', verbose_name=u'机房带宽')
    linkman = models.CharField(max_length=16, blank=True, null=True, default='', verbose_name=u'联系人')
    phone = models.CharField(max_length=32, blank=True, null=True, default='', verbose_name=u'联系电话')
    comment = models.CharField(max_length=128, blank=True, default='', null=True, verbose_name=u"备注")
    class Meta:
        verbose_name = u'IDC管理'
        verbose_name_plural = u'IDC管理'
    def __unicode__(self):
        return self.idc_name

class platform_type(models.Model):
    plat_name = models.CharField(max_length=64,unique=True)
    mini_name = models.CharField(max_length=32,unique=True)
    class Meta:
        verbose_name = u'平台类型管理'
        verbose_name_plural = u'平台类型管理'

    def __unicode__(self):
        return self.plat_name

class publisher(models.Model):
    name = models.CharField(max_length=128,unique=True)
    mini_name = models.CharField(max_length=32,unique=True)
    access_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = u'发行商管理'
        verbose_name_plural = u'发行商管理'

    def __unicode__(self):
        return self.name

class CostManger(models.Model):
    project = models.ForeignKey(Project,default=None,blank=True,null=True,on_delete=models.SET_NULL,verbose_name=u"项目")
    cost_type = models.IntegerField(choices=COST_TYPE, blank=True, null=True,verbose_name=u"云服务类型")
    idc = models.ForeignKey(idc_list,blank=True,null=True,on_delete=models.SET_NULL)
    cpu = models.IntegerField(u'CPU核数',blank=True,null=True)
    mem = models.IntegerField(u'内存(GB)',blank=True,null=True)
    disk = models.IntegerField(u'硬盘(GB)',blank=True,null=True)
    bandwidth = models.IntegerField(u'带宽(MB)',blank=True,null=True)
    network_bill = models.BooleanField(u'流量计费',default=False)
    price = models.CharField(u'月单价',max_length=100,blank=True,null=True)
    start_date = models.DateTimeField(u'开始时间',auto_now_add=True)
    status = models.IntegerField(choices=ASSET_STATUS,default=1)
    total = models.IntegerField(u'数量',default=1)

    class Meta:
        verbose_name = u'费用管理'
        verbose_name_plural = u'费用管理'

    def __unicode__(self):
        return self.project.name

class host(models.Model):
    hostname = models.CharField(max_length=255,unique=True,blank=True,null=True)
    p_ip = models.GenericIPAddressField(unique=True)
    s_ip = models.GenericIPAddressField(blank=True,null=True)
    db_ip = models.CharField(max_length=255,blank=True,null=True)
    port = models.IntegerField(default=22)
    os_type = models.CharField(max_length=32)
    platform = models.ForeignKey(platform_type,blank=True,null=True,on_delete=models.SET_NULL)
    project = models.ForeignKey(Project,default=None,blank=True,null=True,on_delete=models.SET_NULL)
    use = models.ManyToManyField(server_use)
    area = models.ForeignKey(area_type,blank=True,null=True,on_delete=models.SET_NULL)
    idc = models.ForeignKey(idc_list,blank=True,null=True,on_delete=models.SET_NULL)
    login_pass = models.CharField(max_length=255,null=True,blank=True)
    game_count = models.IntegerField(default=0,null=True,blank=True)
    commit = models.CharField(max_length=255,null=True,blank=True)
    host_init = models.BooleanField(default=False)
    db_init = models.BooleanField(default=False)
    asset_status = models.IntegerField(default=0,null=True,blank=True)
    online_date = models.DateTimeField(auto_now_add=True)
    recover = models.IntegerField(default=0,null=True,blank=True)
    recover_date = models.DateTimeField(blank=True,null=True)

    class Meta:
        verbose_name = u'服务器列表'
        verbose_name_plural = u'服务器列表'
    def __unicode__(self):
        return self.p_ip

class DomainInfo(models.Model):
    project = models.ForeignKey(Project,default=None,blank=True,null=True,on_delete=models.SET_NULL,verbose_name="项目")
    domain_name = models.CharField(u'域名',max_length=128)
    record_type = models.IntegerField(choices=RECORD_TYPE, blank=True, null=True, verbose_name=u"记录类型")
    order_key = models.CharField(u'记录值',max_length=128,blank=True,null=True)
    remark = models.CharField(u'备注用途',max_length=255,blank=True,null=True)
    contacts = models.CharField(u'联系人',max_length=64,blank=True,null=True)
    status = models.BooleanField(default=True)
    online_date = models.DateTimeField(auto_now_add=True)
    operator = models.ForeignKey(UserProfile, max_length=84, verbose_name="管理员")

    class Meta:
        verbose_name = u'域名信息管理'
        verbose_name_plural = u'域名信息管理'

    def __unicode__(self):
        return self.domain_name

class Asset(models.Model):
    asset_type = models.IntegerField(choices=ASSET_TYPE,blank=True, null=True, verbose_name=u"主机类型")
    sn = models.CharField(u'资产SN号', max_length=128, unique=True)
    host_name = models.CharField(u'主机名',max_length=64,blank=True,null=True)
    p_ip = models.GenericIPAddressField(u'公网IP',unique=True)
    mac = models.CharField(u'MAC地址',max_length=128,blank=True,null=True)
    idc = models.ForeignKey(idc_list, blank=True, null=True, on_delete=models.SET_NULL)
    project = models.ForeignKey(Project, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    other_ip = models.CharField(u'所有地址',max_length=255,blank=True,null=True)
    system_version = models.CharField(u'系统版本',max_length=32)
    cpu_type = models.CharField(u'CPU型号',max_length=128)
    cpu_core = models.IntegerField(u'CPU个数')
    cpu_total = models.IntegerField(u'CPU核数',)
    memory = models.CharField(u'内存',max_length=128, blank=True, null=True)
    disk_info = models.CharField(u'磁盘信息',max_length=512,blank=True,null=True)
    disk_mount = models.CharField(u'挂载分区',max_length=512,blank=True,null=True)
    server_type = models.CharField(u'服务器型号',max_length=64,blank=True,null=True)
    os_kernel = models.CharField(u'系统内核版本',max_length=255,blank=True,null=True)
    system_arch = models.CharField(u'系统平台',max_length=32,blank=True,null=True)
    status = models.IntegerField(choices=ASSET_STATUS, blank=True, null=True, default=1,verbose_name="设备状态")
    admin = models.ForeignKey(UserProfile, verbose_name=u'资产管理员', null=True, blank=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, auto_now=True)

    class Meta:
        verbose_name = '资产总表'
        verbose_name_plural = "资产总表"

    def __unicode__(self):
        return self.sn

class KeyManager(models.Model):
    project = models.ForeignKey(Project,blank=True, null=True, on_delete=models.SET_NULL,verbose_name="绑定项目")
    name = models.CharField(u'密钥名称',max_length=64,blank=True,null=True)
    username = models.CharField(u'系统用户',max_length=32,blank=True,null=True)
    password = models.CharField(u'SSH密码', max_length=64,blank=True,null=True)
    private_key = models.TextField(u'私钥内容')
    public_key = models.TextField(u'公钥内容')
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    operator = models.ForeignKey(UserProfile,max_length=84,verbose_name="管理员")

    class Meta:
        verbose_name = '超级用户管理'
        verbose_name_plural = "超级用户管理"

    def __unicode__(self):
        return self.name

class CommonUser(models.Model):
    project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="所属项目")
    username = models.CharField(u'普通用户',max_length=32,blank=True,null=True)
    password = models.CharField(u'密码',max_length=32,blank=True,null=True)
    private_key = models.TextField(u'私钥内容',blank=True,null=True)
    public_key = models.TextField(u'公钥内容',blank=True,null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    create_user = models.ForeignKey(UserProfile,max_length=64,verbose_name="创建人")
    operator = models.CharField(u'使用人',max_length=64,blank=True,null=True)

    class Meta:
        verbose_name = '普通用户管理'
        verbose_name_plural = '普通用户管理'

    def __unicode__(self):
        return self.username

class DbInitLog(models.Model):
    project = models.CharField(max_length=255,blank=True,null=True)
    area_name = models.CharField(max_length=255,blank=True,null=True)
    db_ip = models.CharField(max_length=255,blank=True,null=True)
    log = models.CharField(max_length=255)
    status = models.CharField(max_length=100)
    result = models.CharField(max_length=255,blank=True,null=True)
    init_time = models.IntegerField()
    operator = models.CharField(max_length=84,blank=True,null=True)

    class Meta:
        verbose_name = u'数据库初始化日志'
        verbose_name_plural = u'数据库初始化日志'
    def __unicode__(self):
        return self.db_ip

class UserAuditLog(models.Model):
    project = models.CharField(max_length=100)
    area_name = models.CharField(max_length=255,blank=True,null=True)
    platform = models.CharField(max_length=255,blank=True,null=True)
    p_ip = models.CharField(max_length=255,blank=True,null=True)
    server_name = models.CharField(max_length=255,blank=True,null=True)
    version = models.IntegerField(blank=True,null=True)
    log_type = models.CharField(max_length=100)
    log = models.CharField(max_length=255)
    status = models.CharField(max_length=100)
    result = models.CharField(max_length=2048,blank=True,null=True)
    log_time = models.IntegerField()
    operator = models.CharField(max_length=84,blank=True,null=True)

    class Meta:
        verbose_name = u'用户操作日志'
        verbose_name_plural = u'用户操作日志'
    def __unicode__(self):
        return self.p_ip

class SshAuditLog(models.Model):
    project = models.ForeignKey(Project, blank=True, null=True,on_delete=models.SET_NULL, verbose_name="所属项目")
    p_ip = models.GenericIPAddressField(u'公网IP',unique=False)
    username = models.CharField(u'SSH登陆用户',max_length=32)
    login_ip = models.GenericIPAddressField(u'登陆IP',unique=False)
    log_time = models.DateTimeField(u'日志时间')
    cmd_log = models.CharField(max_length=500,verbose_name="命令")
    class Meta:
        verbose_name = u'SSH操作日志'
        verbose_name_plural = u'SSH操作日志'
    def __unicode__(self):
        return self.p_ip


class SdkProject(models.Model):
    name = models.CharField(u'名称',max_length=64)
    mini_name = models.CharField(u'缩写',max_length=32)

    class Meta:
        verbose_name = u'LinkSDK项目'
        verbose_name_plural = u'LinkSDK项目'

    def __unicode__(self):
        return self.name

class ReportSystem(models.Model):
    project = models.ForeignKey(Project, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    p_ip = models.GenericIPAddressField(blank=True,null=True)
    s_ip = models.GenericIPAddressField(blank=True, null=True)
    remarks = models.CharField(max_length=32,blank=True,null=True)
    cputotal = models.IntegerField()
    load_1 = models.CharField(max_length=16)
    load_5 = models.CharField(max_length=16)
    load_15 = models.CharField(max_length=16)
    memtotal = models.IntegerField()
    memused = models.IntegerField()
    memuseprecent = models.CharField(max_length=16)
    swaptotal = models.IntegerField()
    swapused = models.IntegerField()
    swapuseprecent = models.CharField(max_length=16)
    disk_root_sise = models.CharField(max_length=32)
    disk_root_useprecent = models.CharField(max_length=32)
    disk_data_size = models.CharField(max_length=16)
    disk_data_useprecent = models.CharField(max_length=32)
    report_id = models.IntegerField()
    add_time = models.IntegerField()

    class Meta:
        verbose_name = u'报表系统'
        verbose_name_plural = u'报表系统'

    def __unicode__(self):
        return self.p_ip

class ReportMem(models.Model):
    p_ip = models.GenericIPAddressField(blank=True,null=True)
    memuseprecent = models.CharField(max_length=16)
    add_time = models.IntegerField()
    class Meta:
        verbose_name = u'报表系统内存使用率'
        verbose_name_plural = u'报表系统内存使用率'

    def __unicode__(self):
        return self.p_ip