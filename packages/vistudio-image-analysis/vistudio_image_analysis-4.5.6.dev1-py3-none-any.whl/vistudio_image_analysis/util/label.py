#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Authors: chujianfei
Date:    2024/02/22-11:56 AM
"""


def convert_annotation_labels(labels: list()) -> dict():
    """
    convert_annotation_labels, 转成map 可以通过标签名称快速找到标签id,O(1)
    原始数据：
    [
        {"local_name": "1", "display_name": "工服", "parent_id": ""},
        {"local_name": "0", "display_name": "穿工服", "parent_id": "1"},
        {"local_name": "1", "display_name": "未穿工服", "parent_id": "1"},
        {"local_name": "2", "display_name": "安全帽", "parent_id": ""},
        {"local_name": "0", "display_name": "戴安全帽", "parent_id": "2"},
        {"local_name": "1", "display_name": "未戴安全帽", "parent_id": "2"}
    ]

    转换后的数据：

    {
      '工服': {
        'local_name': '1',
        'attributes': [
          {
            'local_name': '0',
            'display_name': '穿工服'
          },
          {
            'local_name': '1',
            'display_name': '未穿工服'
          }
        ]
      },
      '安全帽': {
        'local_name': '2',
        'attributes': [
          {
            'local_name': '0',
            'display_name': '戴安全帽'
          },
          {
            'local_name': '1',
            'display_name': '未戴安全帽'
          }
        ]
      }
    }
    """
    result = {}
    for item in labels:
        display_name = item['display_name']
        parent_id = item.get("parent_id", None)
        # 需要先赋值类别，否则如果labels的list中第一个是属性，这里不会做任何处理，下面的循环会跳过
        if parent_id is None or parent_id == "":  # 如果 parent_id 为空，表示这是一个类别
            result[display_name] = {"local_name": item['local_name'], "attributes": []}
    for item in labels:
        display_name = item['display_name']
        parent_id = item.get("parent_id", None)
        if parent_id is not None or parent_id != "":
            for category, details in result.items():
                if details['local_name'] == parent_id:
                    details['attributes'].append({"local_name": item['local_name'], "display_name": display_name})
                    break

    return result


def convert_annotation_labels_id(labels: list(), ignore_parent_id: bool = False) -> dict():
    """
    _convert_annotation_labels 转成map 可以通过标签id快速找到标签name,O(1)
    原始数据：
    [
        {"local_name": "1", "display_name": "工服", "parent_id": ""},
        {"local_name": "0", "display_name": "穿工服", "parent_id": "1"},
        {"local_name": "1", "display_name": "未穿工服", "parent_id": "1"},
        {"local_name": "2", "display_name": "安全帽", "parent_id": ""},
        {"local_name": "0", "display_name": "戴安全帽", "parent_id": "2"},
        {"local_name": "1", "display_name": "未戴安全帽", "parent_id": "2"}
    ]

    转换后的数据：
    {
      '1': {
        'display_name': '工服',
        'attributes': {
          '0': '穿工服',
          '1': '未穿工服'
        }
      },
      '2': {
        'display_name': '安全帽',
        'attributes': {
          '0': '戴安全帽',
          '1': '未戴安全帽'
        }
      }
    }
    """

    category_dict = {}
    label_dict = {}
    if labels is None or len(labels) == 0:
        return category_dict
    if ignore_parent_id:
        category_dict = {item['local_name']: item['display_name'] for item in labels}
    else:
        for label in labels:
            if "parent_id" not in label or not label.get('parent_id'):
                label_dict[label['local_name']] = {"display_name": label["display_name"], "attributes": {}}
            else:
                # 如果 parent_id 存在，找到对应的类别，将其加入属性列表
                parent_id = label["parent_id"]
                if parent_id in label_dict:
                    label_dict[parent_id]["attributes"][label.get("local_name")] = label.get("display_name")

        for key, value in label_dict.items():
            # 以 category 名称为字典的键，attributes 为值
            category_dict[key] = {
                "display_name": value['display_name'],
                "attributes": value['attributes']}
    sorted_labels = {k: v for k, v in sorted(category_dict.items(), key=lambda x: int(x[0]))}

    return sorted_labels


def convert_labels_id_attr_dict(labels: list()) -> dict():
    """
    convert_annotation_labels, 转成map 可以通过标签名称快速找到标签id,O(1)
    原始数据：
    [
        {"local_name": "1", "display_name": "工服", "parent_id": ""},
        {"local_name": "0", "display_name": "穿工服", "parent_id": "1"},
        {"local_name": "1", "display_name": "未穿工服", "parent_id": "1"},
        {"local_name": "2", "display_name": "安全帽", "parent_id": ""},
        {"local_name": "0", "display_name": "戴安全帽", "parent_id": "2"},
        {"local_name": "1", "display_name": "未戴安全帽", "parent_id": "2"}
    ]

    转换后的数据：

    {
      '工服': {
        'local_name': '1',
        'attributes': [
          {
            'local_name': '0',
            'display_name': '穿工服'
          },
          {
            'local_name': '1',
            'display_name': '未穿工服'
          }
        ]
      },
      '安全帽': {
        'local_name': '2',
        'attributes': [
          {
            'local_name': '0',
            'display_name': '戴安全帽'
          },
          {
            'local_name': '1',
            'display_name': '未戴安全帽'
          }
        ]
      }
    }
    """
    result = {}
    for item in labels:
        display_name = item['display_name']
        parent_id = item.get("parent_id", None)

        if parent_id is None or parent_id == "":  # 如果 parent_id 为空，表示这是一个类别
            result[display_name] = {"local_name": item['local_name'], "attributes": []}
        else:  # 如果 parent_id 不为空，表示这是一个属性
            # 寻找对应的类别并添加属性
            for category, details in result.items():
                if details['local_name'] == parent_id:
                    details['attributes'].append({"local_name": item['local_name'], "display_name": display_name})
                    break
    for key, value in result.items():
        attrs = value.get("attributes")
        if attrs is None:
            continue
        value['attributes'] = {attr['display_name']: attr['local_name'] for attr in attrs}
    return result


def merge_labels_with_attr(labels: list(), merge_labels: dict()) -> dict():
    """
    merge_labels_with_attr
    根据merge_labels将labels中被优化的属性刨除
    """
    label_dict = convert_annotation_labels_id(labels=labels)
    if merge_labels is not None:
        for key, value in merge_labels.items():
            soure_attr_id = key.split("_")[0]
            source_label_id = key.split("_")[1]
            target_attr_id = value.split("_")[0]
            target_label_id = value.split("_")[1]
            source_label_info = label_dict.get(source_label_id)
            target_label_info = label_dict.get(target_label_id)
            if source_label_info is None:
                continue
            source_attr_dict = source_label_info.get("attributes")
            source_attr_name = source_attr_dict.get(soure_attr_id)
            if source_attr_name is None:
                continue

            target_attr_dict = target_label_info.get("attributes")
            target_attr_name = target_attr_dict.get(target_attr_id)
            if source_label_id == target_label_id and soure_attr_id == target_attr_id:
                continue
            source_attr_dict.pop(soure_attr_id, None)
            if len(source_attr_dict) == 0:
                label_dict.pop(source_label_id)
            # else:
            #     new_dict = {str(i): value for i, (_, value) in enumerate(source_attr_dict.items())}
            #     source_label_info['attributes'] = new_dict

    for key, value in label_dict.items():
        new_attributes = {str(i): value for i, (_, value) in enumerate(value.get("attributes").items())}
        value['attributes'] = new_attributes
    sorted_labels = {k: v for k, v in sorted(label_dict.items(), key=lambda x: int(x[0]))}
    return sorted_labels


def random_color():
    """生成随机的十六进制颜色代码。

    返回：
      表示十六进制颜色代码的字符串（例如 #00FF00）。
    """
    import colorsys
    import random
    h, s, v = random.uniform(0, 1), random.uniform(0.5, 1), random.uniform(0.5, 1)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    hex_color = "#" + "".join([f"{x:02x}" for x in (int(r * 255), int(g * 255), int(b * 255))])
    return hex_color


def merge_labels(labels_dict, merge_dict) -> dict():
    """
    merge_labels
    根据merge_dict合并labels_dict
    """
    if not labels_dict:
        return {}

    if not merge_dict:
        return labels_dict

    merged_labels = dict()
    for label_id, label_name in labels_dict.items():
        # 检查当前的 label_id 是否需要合并
        if label_id in merge_dict:
            target_id = merge_dict[label_id]
            merged_labels[target_id] = labels_dict[target_id]
        else:
            # 如果不需要合并，则直接添加到新字典中
            merged_labels[label_id] = label_name

    return merged_labels

