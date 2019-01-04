from django.conf.urls import include, url, patterns

urlpatterns = patterns('manager.help_views',
    url(r'index/$','helps.index',name='help_index' ),
    url(r'detail/$','helps.detail',name='help_detail' ),
    url(r'edit/$','helps.edit',name='help_edit' ),
    url(r'new_article/$','helps.new_article',name='new_article' ),
)
