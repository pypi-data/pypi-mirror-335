# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2022 Baidu.com, Inc. All Rights Reserved
#
"""
modify input train parameter yaml
Authors: wanggaofei(wanggaofei03@baidu.com)
Date:    2023-02-29
"""
import os
import yaml
import bcelogger

from gaea_operator.config.config import KEY_NETWORK_ARCHITECTURE
from gaea_operator.utils import write_yaml_file

KEY_EPOCH = "num_train_epochs"
KEY_BATCH_SIZE = "per_device_train_batch_size"
KEY_WORKER_NUM = "dataloader_num_workers"


def generate_train_config(
        advanced_parameters: dict,
        pretrain_model_uri: str,
        train_config_name: str
):
    """
    modify parameter by template config
    """
    config_file_name = 'parameter.yaml'
    config_raw = \
        yaml.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file_name), Loader=yaml.FullLoader)

    # 1. modify uncertain parameters
    network_architecture2model_type = {"yijian-mllm-lite": "internvl2"}
    network_architecture = advanced_parameters.pop(KEY_NETWORK_ARCHITECTURE)
    assert network_architecture in network_architecture2model_type, \
        "network_architecture {} is not supported".format(network_architecture)
    advanced_parameters["model_type"] = network_architecture2model_type[network_architecture]
    advanced_parameters["model"] = pretrain_model_uri

    # 2. save yaml
    config_raw.update(advanced_parameters)
    bcelogger.info('begin to save yaml. {}'.format(train_config_name))
    write_yaml_file(config_raw, os.path.dirname(train_config_name), os.path.basename(train_config_name))
    bcelogger.info('write train config finish.')