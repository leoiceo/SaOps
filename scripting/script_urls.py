from django.conf.urls import include, url, patterns

urlpatterns = patterns('scripting.views',
    url(r'script_list/$','tools.script_list',name='script_list' ),
    url(r'script_edit/$','tools.script_edit',name='script_edit' ),
)