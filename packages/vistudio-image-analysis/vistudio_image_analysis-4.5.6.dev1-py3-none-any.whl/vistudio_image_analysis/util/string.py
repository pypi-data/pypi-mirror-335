#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Authors: chujianfei
Date:    2024/02/22-11:56 AM
"""
import base64
import random
import string
import json
import xxhash


def decode_from_base64(base64_string):
    """
    将 Base64 字符串解码为字符串
    :param base64_string:
    :return:
    """
    # 将 Base64 字符串解码为字节对象
    base64_bytes = base64_string.encode('utf-8')

    # 使用 base64 解码
    decoded_bytes = base64.b64decode(base64_bytes)

    # 将字节对象解码为字符串
    decoded_string = decoded_bytes.decode('utf-8')

    return decoded_string


def generate_md5(data):
    """
    生成md5
    :param data:
    :return:
    """
    hash64 = xxhash.xxh64(data).hexdigest()
    return hash64


def generate_random_digits(length=6):
    """
    生成指定长度的随机数字字符串。

    参数：
    length (int): 生成的字符串长度，默认为 6。

    返回：
    str: 生成的随机数字字符串。
    """
    # 定义包含数字 0 到 9 的字符串
    digits = string.digits

    # 使用 random 模块生成指定长度的随机数字字符串
    random_string = ''.join(random.choice(digits) for _ in range(length))

    return random_string


def generate_random_string(length):
    """
    生成随机字符串
    :param length:
    :return:
    """
    # 定义字符集合
    characters = string.ascii_letters + string.digits

    # 生成随机字符串
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def split_string_list(s):
    """
    将字符串转换为 list
    :param s:
    :return:
    """
    return s.strip("'").split(",")


def extract_json(input_string):
    """
    提取可以解析的json
    """
    json_success = False
    try:
        # 找到最左边的 '{' 和最右边的 '}' 的索引
        start_index = input_string.find('{')
        end_index = input_string.rfind('}')

        if start_index == -1 or end_index == -1:
            return json_success, input_string

        # 提取出含大括号之间的内容，尝试解析为 JSON
        json_string = input_string[start_index:end_index + 1]
        parsed_json = json.loads(json_string)

        # 解析成功，但是空字典，返回原始字符串
        if isinstance(parsed_json, dict) and not parsed_json:
            return json_success, input_string

        json_success = True
        return json_success, json.dumps(parsed_json, ensure_ascii=False)
    except (json.JSONDecodeError, ValueError):
        return json_success, input_string
