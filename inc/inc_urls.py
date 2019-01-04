#!/usr/bin/python
#_*_coding:utf-8_*_
from django.conf.urls import include, url, patterns

urlpatterns = patterns('inc.views',
    url(r'host_init/$','init.host_init',name='inc_host_init' ),
    url(r'host_init_process/$','init.host_init_process',name='host_init_process' ),
    url(r'see_init_script/$','init.see_init_script',name='see_init_script' ),

    url(r'db_init/$','init.db_init',name='inc_db_init' ),
    url(r'db_init_process/$','init.db_init_process',name='db_init_process' ),
    url(r'db_init_status/$','init.db_init_status',name='db_init_status' ),

    url(r'game_deploy/$','deploy.game_deploy',name='game_deploy' ),
    url(r'game_deploy_check/$','deploy.game_deploy_check',name='game_deploy_check' ),
    url(r'inc_add_gameinfo/$','deploy.inc_add_gameinfo',name='inc_add_gameinfo' ),
    url(r'install_process/$','deploy.inc_install_process',name='inc_install_process' ),
    url(r'process_status/$','deploy.inc_process_status',name='inc_process_status' ),

    url(r'game_info/$','gameinfo.game_info',name='inc_game_info' ),
    url(r'game_crontrol/$','gameinfo.game_crontrol',name='inc_game_crontrol' ),
    url(r'clear_gamedb/$','gameinfo.clear_gamedb',name='inc_clear_gamedb' ),
    url(r'gameinfo_edit/$','gameinfo.gameinfo_edit',name='inc_gameinfo_edit' ),
    url(r'gamedrop_process/$','gameinfo.gamedrop_process',name='inc_gamedrop_process' ),
    url(r'graph_status/$','gameinfo.graph_status',name='inc_graph_status' ),

    url(r'conf_manage/$','gameconfig.inc_conf_manage',name='inc_conf_manage' ),
    url(r'conf_edit/$','gameconfig.inc_conf_edit',name='inc_conf_edit' ),

    url(r'backup_plan/$','db_backup.backup_plan',name='inc_backup_plan' ),
    url(r'inc_backup/$','db_backup.inc_backup',name='inc_backup' ),
    url(r'backup_process/$','db_backup.backup_process',name='inc_backup_process' ),

    url(r'update_file/$','inc_update.update_file',name='inc_update_file' ),
    url(r'update_file_info/$','inc_update.update_file_info',name='inc_update_file_info' ),
    url(r'update_file_status/$','inc_update.update_file_status',name='inc_update_file_info' ),

    url(r'update_sql/$','inc_update.update_sql',name='inc_update_sql' ),
    url(r'update_sql_info/$','inc_update.update_sql_info',name='inc_update_sql_info' ),
    url(r'update_sql_status/$','inc_update.update_sql_status',name='inc_update_sql_status' ),

    url(r'update_config/$','inc_update.update_config',name='inc_update_config' ),
    url(r'update_process/$','inc_update.update_process',name='inc_update_process' ),
    url(r'update_config_info/$','inc_update.update_config_info',name='inc_update_config_info' ),
    url(r'update_config_status/$','inc_update.update_config_status',name='inc_update_config_status' ),

    url(r'zone_list/$','gamelist.zone_list',name='inc_zone_list' ),
    url(r'zone_list_print/$','gamelist.zone_list_print',name='inc_zone_list_print' ),
    url(r'zone_list_edit/$','gamelist.zone_list_edit',name='inc_zone_list_edit' ),
    url(r'zone_list_send/$','gamelist.zone_list_send',name='inc_zone_list_send' ),

    url(r'server_list/$','gamelist.server_list',name='inc_server_list' ),
    url(r'server_list_edit/$','gamelist.server_list_edit',name='inc_server_list_edit' ),
    url(r'server_list_print/$','gamelist.server_list_print',name='inc_server_list_print' ),
    url(r'server_list_send/$','gamelist.server_list_send',name='inc_server_list_send' ),

    url(r'white_list/$','gamelist.white_list',name='inc_white_list' ),
    url(r'white_list_print/$','gamelist.white_list_print',name='inc_white_list_print' ),
    url(r'white_list_edit/$','gamelist.white_list_edit',name='inc_white_list_edit' ),
    url(r'white_list_send/$','gamelist.white_list_send',name='inc_white_list_send' ),
    url(r'gamelist_dir_edit/$','gamelist.gamelist_dir_edit',name='inc_gamelist_dir_edit' ),


)
