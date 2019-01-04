from django.conf.urls import include, url, patterns

urlpatterns = patterns('hosts.views',
   url(r'list', 'AuditLog.log_list', name='log_list'),
)