from django.conf.urls import include, url, patterns

urlpatterns = patterns('hosts.api_views',

                       url(r'public_ipv4$', 'IpInfo.public_ipv4', name='public_ipv4'),
                       url(r'ssh_audit$', 'UserAudit.ssh_audit', name='ssh_audit'),
                       url(r'get_ssl', 'UserAudit.get_ssl', name='get_ssl'),
                       url(r'mail$', 'Sender.mail', name='mail'),
                       url(r'mytest$', 'MyTest.PostData', name='mytest'),
                       url(r'test_upload$', 'MyTest.PostFile', name='test_upload'),
                       )