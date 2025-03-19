#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/17
# @Author  : yanxiaodong
# @File    : transform.py
"""
import os
import shutil

import bcelogger

from gaea_operator.utils import DEFAULT_TRANSFORM_CONFIG_FILE_NAME, Accelerator
from .cvt_copy_model import cvt_copy_model


class Transform(object):
    """
    Transform model class.
    """
    def __init__(self, windmill_client, accelerator: str = None):
        self.windmill_client = windmill_client
        self.accelerator = accelerator

    def transform(self, transform_config_dir: str, src_model_uri: str, dst_model_uri: str):
        """
        Transform the model from src_model_uri to dst_model_uri.
        """
        if self.accelerator == Accelerator.P800:
            if not os.path.exists(dst_model_uri):
                os.makedirs(dst_model_uri, exist_ok=True)
            shutil.copytree(os.path.join(src_model_uri, "inference"), dst_model_uri, dirs_exist_ok=True)
            bcelogger.info("Transform for P800 is implemented.")
            return

        transform_config_filepath = os.path.join(transform_config_dir, DEFAULT_TRANSFORM_CONFIG_FILE_NAME)
        cvt_copy_model(transform_config_filepath, src_model_uri, dst_model_uri)