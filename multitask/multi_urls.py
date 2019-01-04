from django.conf.urls import include, url, patterns

urlpatterns = patterns('multitask.views',
    url(r'exec_cmds/$','tools.exec_cmds',name='exec_cmds' ),
    url(r'exec_cmds_process/$','tools.exec_cmds_process',name='exec_cmds_process' ),
    url(r'exec_cmds_status/$','tools.exec_cmds_status',name='exec_cmds_status' ),
    url(r'exec_cmds_result/$','tools.exec_cmds_result',name='exec_cmds_result' ),

    url(r'exec_script/$','tools.exec_script',name='exec_script' ),
    url(r'exec_script_process/$','tools.exec_script_process',name='exec_script_process' ),
    url(r'exec_script_status/$','tools.exec_script_status',name='exec_script_status' ),
    url(r'exec_script_hosts/$','tools.exec_script_hosts',name='exec_script_hosts' ),
    url(r'script_args_api/$','tools.script_args_api',name='script_args_api' ),

    url(r'file_trans/$','tools.file_trans',name='file_trans' ),
    url(r'file_trans_edit/$','tools.file_trans_edit',name='file_trans_edit' ),
    url(r'file_trans_process/$','tools.file_trans_process',name='file_trans_process' ),
    url(r'file_trans_status/$','tools.file_trans_status',name='file_trans_status' ),

    url(r'user_audit/$','tools.user_audit',name='user_audit' ),
)
