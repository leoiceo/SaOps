from django.conf.urls import include, url, patterns

urlpatterns = patterns('hosts.assets_views',
    url(r'asset_status/$','assets.asset_status',name='asset_status' ),
    url(r'asset_list/$','assets.asset_list',name='asset_list' ),
    url(r'asset_edit/$','assets.asset_edit',name='asset_edit' ),
    url(r'asset_add/$','assets.asset_add',name='asset_add' ),
    url(r'^asset_list/(\d+)/$','assets.asset_detail', name="asset_detail"),
    url(r'asset_update/$','assets.asset_update',name='asset_update' ),
    url(r'asset_update_log/$','assets.asset_update_log',name='asset_update_log' ),
    url(r'asset_update_process/$','assets.asset_update_process',name='asset_update_process' ),
)
