#!/usr/bin/python3
"""
This is a tool for sending and receiving file through SSH protocol.
Need a csv file to record the server information.
Powered by Seanet.DSP / mazl@dsp.ac.cn 2023.8.22 v1.0
"""

from httpsig.requests_auth import HTTPSignatureAuth
from SSHFileManager import SFTPFileManager_Tool
from csvreader import CSVReader
from threading import Thread
import requests
import datetime
import json
import yaml
import os


def get_auth(KeyID, SecretID):
    signature_headers = ['(request-target)', 'accept', 'date']
    auth = HTTPSignatureAuth(key_id=KeyID, secret=SecretID,
                             algorithm='hmac-sha256', headers=signature_headers)
    return auth


def get_user_info(jms_url, auth):
    url = jms_url + '/api/v1/users/users/'
    gmt_form = '%a, %d %b %Y %H:%M:%S GMT'
    headers = {
        'Accept': 'application/json',
        'X-JMS-ORG': '00000000-0000-0000-0000-000000000002',
        'Date': datetime.datetime.utcnow().strftime(gmt_form)
    }

    response = requests.get(url, auth=auth, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        # 处理返回的 JSON 数据, 格式化打印
        print(json.dumps(json_data, indent=4))


def get_server_list(jms_url, auth):
    """
    调用Jumpserver api获取服务器列表
    """
    server_list = []
    # get host list with jumpserver api
    url = jms_url + '/api/v1/assets/hosts/'
    gmt_form = '%a, %d %b %Y %H:%M:%S GMT'
    params = {'platform': 'SEANet'}
    headers = {
        'Accept': 'application/json',
        'Date': datetime.datetime.utcnow().strftime(gmt_form),
        'X-JMS-ORG': '00000000-0000-0000-0000-000000000002',
    }
    response = requests.get(url, params=params, headers=headers, auth=auth)
    if response.status_code == 200:
        json_data = response.json()
        # 处理返回的 JSON 数据
        # print(json.dumps(json_data, indent=4))
        for host in json_data:
            server_list.append(host["name"])
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(response.text)
    return server_list


if __name__ == '__main__':
    csv_f = "data/test.csv"
    # get conf file
    if os.path.exists("conf_private.yml"):
        bl_conf = yaml.load(open("conf_private.yml"), Loader=yaml.FullLoader)
    else:
        bl_conf = yaml.load(open("conf.yml"), Loader=yaml.FullLoader)
    # read jumpserver ssh conf
    ssh_conf = {
        "host": bl_conf["jumpserver"]["host"],
        "port": bl_conf["jumpserver"]["port"],
        "username": bl_conf["jumpserver"]["username"],
        "pwd": bl_conf["jumpserver"]["pwd"],
        "pkey": bl_conf["jumpserver"]["pkey"]
    }
    node = bl_conf["jumpserver"]["node"]
    # get_server_list_from_jumpserver()
    jms_url = f"http://{ssh_conf['host']}"
    KeyID = bl_conf["jumpserver"]["keyid"]
    SecretID = bl_conf["jumpserver"]["secretid"]
    auth = get_auth(KeyID, SecretID)
    # get_user_info(jms_url, auth)
    sl = get_server_list(jms_url, auth)
    # upload file to server
    local_file = bl_conf["file"]["local_path"]
    mt = bl_conf["file"]["multi_thread"]
    sshtool = SFTPFileManager_Tool(**ssh_conf)
    sshtool.upload_file_via_jumpserver(local_file, node, sl, mt)
