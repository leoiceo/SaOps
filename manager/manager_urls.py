from django.conf.urls import include, url, patterns

urlpatterns = patterns('manager.views',
    url(r'user_list/$','users.user_list',name='user_list' ),
    #url(r'user_list/modity_privil/$','users.user_modity_privil',name='user_modity_privil' ),
    url(r'user_add/$','users.user_add',name='user_add' ),
    url(r'user_eye/$','users.user_eye',name='user_eye' ),
    url(r'user_edit/$','users.user_edit',name='user_edit' ),

    url(r'dept_list/$','department.dept_list',name='dept_list' ),
    url(r'dept_add/$','department.dept_add',name='dept_add' ),
    url(r'dept_edit/$','department.dept_edit',name='dept_edit' ),

    url(r'pro_list/$','project.pro_list',name='pro_list' ),
    url(r'pro_edit/$','project.pro_edit',name='pro_edit' ),

    url(r'role_list/$','role.role_list',name='role_list' ),
    url(r'role_edit/$','role.role_edit',name='role_edit' ),

    url(r'perm_deny/$','permission.NoPermission',name='perm_deny' ),
    url(r'perm_list/$','permission.perm_list',name='perm_list' ),
    url(r'perm_edit/$','permission.perm_edit',name='perm_edit' ),
)
