#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2025/2/24
# @Author  : yanxiaodong
# @File    : ms_swift_dataset.py
"""
import os
import json
from typing import Any, List, Union, Tuple

import bcelogger
from windmillclient.client.windmill_client import WindmillClient

from .dataset import Dataset
from gaea_operator.utils import get_filepaths_in_archive, read_file_jsonl


class MSSWIFTDataset(Dataset):
    """
     ms-swift dataset for data processing.
     https://swift2x.readthedocs.io/zh-cn/latest/Multi-Modal/internvl%E6%9C%80%E4%BD%B3%E5%AE%9E%E8%B7%B5.html
    """
    usages = [("train.jsonl", "annotation.jsonl"), ("val.jsonl", "annotation.jsonl")]

    def __init__(self, windmill_client: WindmillClient, work_dir: str, extra_work_dir: str = None):
        super().__init__(windmill_client=windmill_client, work_dir=work_dir, extra_work_dir=extra_work_dir)

    def _get_annotation(self, paths: List, base_uri: str, usage: Union[str, Tuple], work_dir: str, output_dir: str):
        annotation_file_list = []
        for idx, path in enumerate(paths):
            path = os.path.join(work_dir, path)
            annotation_file_list = get_filepaths_in_archive(path, self.decompress_output_uri, usage)

        bcelogger.info(f"Annotation file list is: {annotation_file_list}")

        raw_data_list = []
        for file in annotation_file_list:
            file_raw_data_list = read_file_jsonl(os.path.dirname(file), os.path.basename(file))
            for json_data in file_raw_data_list:
                img_list = []
                for img in json_data.get("images", []):
                    img_list.append(self._file_name_cvt_abs(img, file, base_uri, 1, work_dir))
                json_data['images'] = img_list
                raw_data_list.append(json_data)
            bcelogger.info(f"Parse annotation file {file}, image num is {len(file_raw_data_list)}")

        return raw_data_list

    def _concat_annotation(self, raw_data_list: List):
        if len(raw_data_list) >= 1:
            return raw_data_list
        else:
            raise ValueError(f"The number of annotation file is empty, please check dataset name")

    def _filter_not_exist_image(self, raw_data: Any):
        bcelogger.info(f"The image num is {len(raw_data)}")
        new_raw_data = []
        not_exist_num = 0
        for item in raw_data:
            item_images = []
            for img in item.get("images", []):
                if not os.path.exists(img):
                    not_exist_num += 1
                    break
                item_images.append(img)
            if len(item_images) == len(item.get("images")):
                item["images"] = item_images
                new_raw_data.append(item)

        assert len(new_raw_data) > 0, "All images are not exist"
        bcelogger.info(f"The image num is {len(raw_data)}, not exist num is {not_exist_num}")

        return new_raw_data

    def _write_annotation(self, output_dir: str, file_name: str, raw_data: Any):
        if raw_data is None:
            return
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, file_name)

        with open(file_path, "w") as fp:
            for item in raw_data:
                fp.write(json.dumps(item) + '\n')