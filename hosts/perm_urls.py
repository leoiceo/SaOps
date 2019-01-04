from django.conf.urls import include, url, patterns

urlpatterns = patterns('hosts.views',

   url(r'common_user/$', 'conf.common_user', name='common_user'),
   url(r'common_user_edit/$', 'conf.common_user_edit', name='common_user_edit'),

   url(r'sshkey_list/$', 'conf.sshkey_list', name='sshkey_list'),
   url(r'sshkey_edit/$', 'conf.sshkey_edit', name='sshkey_edit'),

   url(r'init_hosts/$', 'tools.init_hosts', name='init_hosts'),
   url(r'init_dbs/$', 'tools.init_dbs', name='init_dbs'),
   #url(r'init_hosts_status/$', 'tools.init_hosts_status', name='init_hosts_status'),
)