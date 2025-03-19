# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2024/2/27 16:16
# @Author : yangtingyu01
# @Email: yangtingyu01@baidu.com
# @File : mock.py
# @Software: PyCharm
"""
from flask import Flask, jsonify, request
import threading
import time
import socket
from baidubce.bce_response import BceResponse

app = Flask(__name__)


def get_mock_server():
    """
    return windmill mock server url
    :return:
    """
    port = find_port()
    server_thread = threading.Thread(target=app.run, kwargs={"port": port})
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1)  # Give the server time to start
    return f"http://127.0.0.1:{port}"


def find_port():
    """
    find a port
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def get_bce_response(response):
    """
    get_bce_response
    """
    bce_response = BceResponse()  # 实例化 BceResponse
    bce_response.__dict__.update(response)
    return bce_response



