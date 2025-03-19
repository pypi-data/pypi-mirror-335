#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   label_formatter.py
"""

from typing import Union, Dict, List, Any
import ray
from ray.data import Dataset
import bcelogger

from windmillcomputev1.filesystem import init_py_filesystem
from vistudio_image_analysis.util.label import convert_annotation_labels


class LabelFormatter(object):
    """
    LabelFormatter
    """
    def __init__(
        self,
        labels: Union[List] = list,
        annotation_format: str = "",
        filesystem: Union[Dict] = None,
        annotation_set_category: str = None
    ):
        self.labels = labels
        self.annotation_format = annotation_format
        self.annotation_set_category = annotation_set_category
        if filesystem is not None:
            self._py_fs = init_py_filesystem(filesystem)

    @staticmethod
    def _get_labels_from_imagenet(ds: Dataset) -> list():
        """
        get_labels_from_imagenet
        """
        import_labels = []
        label_names = ds.select_columns(cols=['label']).unique(column='label')
        for index, label_name in enumerate(label_names):
            import_labels.append({
                "local_name": "",
                "display_name": label_name,
            })
        return import_labels

    def _get_labels_from_cityscapes(self, ds: Dataset) -> list():
        """
        get_labels_from_cityscapes
        """
        import_labels = []
        file_uris = ds.unique(column='item')
        label_color_files = [file_uri for file_uri in file_uris if file_uri.endswith(".txt")]
        label_color_series = ray.data.read_text(paths=label_color_files, filesystem=self._py_fs).to_pandas()['text']
        for label_id, label_name in label_color_series.items():
            parts = label_name.split()
            p1 = int(parts[0])
            p2 = int(parts[1])
            p3 = int(parts[2])
            if p1 == 0 and p2 == 0 and p3 == 0:
                continue
            import_labels.append({
                "local_name": str(label_id),
                "display_name": label_name.split()[-1],
            })
        return import_labels

    @staticmethod
    def _get_labels_from_coco(ds: Dataset) -> list():
        """
        get_labels_from_coco
        """
        import_labels = []
        labels_ds = ds.select_columns(cols=['categories'])
        for row in labels_ds.iter_rows():
            if type(row['categories']) == dict:
                label_id = row['categories'].get('id')
                import_labels.append({
                    "local_name": str(label_id),
                    "display_name": row['categories'].get('name'),
                })
            else:
                for label in row['categories']:
                    label_id = label.get('id')
                    import_labels.append({
                        "local_name": str(label_id),
                        "display_name": label.get('name'),
                    })
        return import_labels

    @staticmethod
    def _get_labels_from_cvat(ds: Dataset) -> list():
        """
        get_labels_from_cvat
        """
        import_labels = []
        labels_list = ds.flat_map(lambda row: row['labels']).unique(column='name')
        for index, label_name in enumerate(labels_list):
            import_labels.append({
                "local_name": "",
                "display_name": label_name,
            })
        return import_labels

    @staticmethod
    def _get_labels_from_multiattributedataset(ds: Dataset):
        """
        get_labels_from_multiattributedataset
        """
        import_labels = []
        for row in ds.iter_rows():
            label = {}
            label_name = row['task_name']
            label['display_name'] = str(label_name)
            label['parent_id'] = None
            label['anno_key'] = row['anno_key']
            label['local_name'] = str(row['anno_key'])
            import_labels.append(label)
            categories = row['categories']
            for k, v in categories.items():
                attr = {
                    'local_name': str(k),
                    'display_name': str(v),
                    'parent_name': label_name,
                    'parent_id': label['local_name']
                }
                import_labels.append(attr)
        return import_labels

    @staticmethod
    def _get_labels_from_visionstudio(ds: Dataset) -> list():
        """
        get_labels_from_visionstudio
        """
        label_ds = ds.filter(lambda row: row["data_type"] == "Label")

        import_labels = []
        labels_ds = label_ds.flat_map(lambda row: row["labels"])
        labels = labels_ds.take_all()
        bcelogger.info(f"get import labels from meta.json file: {labels}")
        for label in labels:
            import_labels.append({
                "local_name": str(label.get('id')),
                "display_name": label.get('name'),
                "parent_id": str(label.get('parent_id'))
            })
        return import_labels

    def get_import_labels(self, ds: Dataset) -> list():
        """
        get_import_labels
        """
        import_labels = []
        if self.annotation_set_category == 'Image/OCR':
            return import_labels

        method_name = f"_get_labels_from_{self.annotation_format}"
        method = getattr(self, method_name, None)

        if callable(method):
            return method(ds)

        return import_labels

    def get_need_add_labels(self, import_labels: list()) -> list():
        """
        此方法主要是根据导入的标签  和 标注集已有的标签，转换成需要插入的标签
        import_labels 和 annotation_labels 的格式为
        [
            {"local_name": "1", "display_name": "工服", "parent_id": ""},
            {"local_name": "0", "display_name": "穿工服", "parent_id": "1"},
            {"local_name": "1", "display_name": "未穿工服", "parent_id": "1"},
            {"local_name": "2", "display_name": "安全帽", "parent_id": ""},
            {"local_name": "0", "display_name": "戴安全帽", "parent_id": "2"},
            {"local_name": "1", "display_name": "未戴安全帽", "parent_id": "2"}
        ]
        """
        if import_labels is None or len(import_labels) == 0:
            return None
        need_add_labels = list()
        import_label_dict = convert_annotation_labels(import_labels)
        annotation_label_dict = convert_annotation_labels(self.labels)
        for key, value in import_label_dict.items():
            if key not in annotation_label_dict:
                # 需要新增标签
                need_add_labels.append({
                    "display_name": key,
                    "type": "label",
                    "attributes": import_label_dict.get(key).get("attributes", [])
                })

            else:
                # 不需要新增标签，但是可能需要新增相关属性
                parent_id = annotation_label_dict.get(key).get("local_name")
                annotation_label_attrs = annotation_label_dict.get(key).get("attributes", [])
                import_labels_attrs = import_label_dict.get(key).get("attributes", [])
                annotation_labels_attr_dict = {item['display_name']: item['local_name'] for item in
                                               annotation_label_attrs}
                if annotation_label_attrs is not None:
                    for attr in import_labels_attrs:
                        import_label_attr_display_name = attr.get("display_name")
                        if import_label_attr_display_name in annotation_labels_attr_dict:
                            continue
                        need_add_labels.append({
                            "display_name": attr.get("display_name"),
                            "type": "attr",
                            "parent_name": key,
                            "parent_id": parent_id
                        })

        return need_add_labels

    def labels_to_vistudio_v1(self, ds: "Dataset") -> dict():
        """
        labels_to_vistudio_v1
        """
        import_labels = self.get_import_labels(ds=ds)
        need_add_labels = self.get_need_add_labels(import_labels=import_labels)
        return {"need_add_labels": need_add_labels, "import_labels": import_labels}
