#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo


import paramiko
from sshtunnel import SSHTunnelForwarder





def sshtunnel_proxy(proxy_host,proxy_port,proxy_keyfile,proxy_username,remote_host,remote_port,remote_keyfile,remote_username,cmd):
    """
    通过跳板机访问服务器
    :param proxy_host:
    :param proxy_port:
    :param proxy_keyfile:
    :param proxy_username:
    :param remote_host:
    :param remote_port:
    :param remote_keyfile:
    :param remote_username:
    :param cmd:
    :return:
    """
    #跳板机
    REMOTE_SERVER_IP=proxy_host
    #目标机
    PRIVATE_SERVER_IP=remote_host

    with SSHTunnelForwarder(
        (REMOTE_SERVER_IP, proxy_port),
        ssh_username=proxy_username,
        ssh_pkey=proxy_username,
        ssh_private_key_password="",
        remote_bind_address=(PRIVATE_SERVER_IP, remote_port),
        local_bind_address=('0.0.0.0', 10022)
    ) as tunnel:
        client = paramiko.SSHClient()
        #client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client_key = paramiko.RSAKey.from_private_key_file(remote_keyfile)  # keypasswd (keyfile,password)
        client.connect('127.0.0.1', 10022,username=remote_username, pkey=client_key)
        # do some operations with client session
        stdout,stderr = client.exec_command(cmd)
        print stdout.read()
        client.close()

    return  stdout,stderr