#_*_coding:utf-8_*_
from manager.myauth import *
from hosts.models import *
from inc.models import *
from gjsj.models import *
from slg.models import *
#from cscs.models import *
from manager.models import *
from cmdb import settings
from zsgl.models import *

def custom_proc(request):

    try:
        iUser = UserProfile.objects.get(email="%s" % request.user)
        if iUser.is_admin:
            pro_info = Project.objects.all()
        else:
            pro_info = iUser.project.all()
    except Exception,e:
        pro_info = Project.objects.all()

    idc_info = idc_list.objects.all()
    area_info = area_type.objects.all()
    use_info = server_use.objects.all()
    platform_info = platform_type.objects.all()
    tag_info = Tag.objects.all()
    # 暗黑血统
    inc_area_plat_info = {}
    info = gameinfo.objects.all()
    inc_area_info = []
    for i in info:
        platform_list = []
        area_name = i.area.area_name
        if area_name not in inc_area_info:
            inc_area_info.append(area_name)
        plat_name = i.platform.mini_name
        if plat_name not in platform_list:
            platform_list.append(plat_name)
        try:
            old_plat_list = inc_area_plat_info[area_name]
            platform_list = old_plat_list + platform_list
            platform_list = list(set(platform_list))
            inc_area_plat_info[area_name] = platform_list
        except Exception,e:
            inc_area_plat_info.setdefault(area_name,platform_list)

    # 挂机世界
    gjsj_area_plat_info = {}
    gjsj_info = GjsjGameInfo.objects.all()
    gjsj_area_info = []
    for i in gjsj_info:
        platform_list = []
        area_name = i.area.area_name
        if area_name not in gjsj_area_info:
            gjsj_area_info.append(area_name)
        plat_name = i.platform.mini_name
        if plat_name not in platform_list:
            platform_list.append(plat_name)
        try:
            old_plat_list = gjsj_area_plat_info[area_name]
            platform_list = old_plat_list + platform_list
            platform_list = list(set(platform_list))
            gjsj_area_plat_info[area_name] = platform_list
        except Exception,e:
            gjsj_area_plat_info.setdefault(area_name,platform_list)

    # slg
    slg_area_plat_info = {}
    slg_info = SlgGameInfo.objects.all()
    slg_area_info = []
    for i in slg_info:
        platform_list = []
        area_name = i.area.area_name
        if area_name not in slg_area_info:
            slg_area_info.append(area_name)
        plat_name = i.platform.mini_name
        if plat_name not in platform_list:
            platform_list.append(plat_name)
        try:
            old_plat_list = slg_area_plat_info[area_name]
            platform_list = old_plat_list + platform_list
            platform_list = list(set(platform_list))
            slg_area_plat_info[area_name] = platform_list
        except Exception, e:
            slg_area_plat_info.setdefault(area_name, platform_list)

    # zsgl
    zsgl_area_plat_info = {}
    zsgl_info = ZsglGameInfo.objects.all()
    zsgl_area_info = []
    for i in zsgl_info:
        platform_list = []
        area_name = i.area.area_name
        if area_name not in zsgl_area_info:
            zsgl_area_info.append(area_name)
        plat_name = i.platform.mini_name
        if plat_name not in platform_list:
            platform_list.append(plat_name)
        try:
            old_plat_list = zsgl_area_plat_info[area_name]
            platform_list = old_plat_list + platform_list
            platform_list = list(set(platform_list))
            zsgl_area_plat_info[area_name] = platform_list
        except Exception, e:
            zsgl_area_plat_info.setdefault(area_name, platform_list)
    #权限管理
    #iuser = UserProfile.objects.get(email="%s"% request.user)
    #role_perm = RoleList.objects.get(name=iuser.role)
    #role_perm_list = role_perm.permission.all()
    spro_info = []
    project_id = CostManger.objects.all().values('project').distinct()
    for proid in project_id:
        pro_name = Project.objects.get(id=proid['project']).name
        spro_info.append(pro_name)

    return {
        "monitor_url":settings.MONITOR_DOMAIN,
        "pro_info":pro_info,
        "spro_info":spro_info,
        "tag_info":tag_info,
        "idc_info":idc_info,
        "area_info":area_info,
        "use_info":use_info,
        "platform_info":platform_info,
        "inc_area_plat_info":inc_area_plat_info,
        "inc_area_info":inc_area_info,
        "gjsj_area_plat_info":gjsj_area_plat_info,
        "gjsj_area_info":gjsj_area_info,
        "slg_area_plat_info":slg_area_plat_info,
        "slg_area_info":slg_area_info,
        "zsgl_area_plat_info":zsgl_area_plat_info,
        "zsgl_area_info":zsgl_area_info,
    }
