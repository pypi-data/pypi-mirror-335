#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2025/2/24
# @Author  : yanxiaodong
# @File    : mllm.py
"""
import os
import copy
from typing import Dict

from gaea_tracker import ExperimentTracker
from windmillclient.client.windmill_client import WindmillClient
from windmillmodelv1.client.model_api_model import ModelMetadata

from gaea_operator.utils import DEFAULT_TRAIN_CONFIG_FILE_NAME, read_yaml_file, write_yaml_file
from ..config import Config, \
    KEY_WORKER_NUM_STANDARD, \
    KEY_BATCH_SIZE_STANDARD, \
    KEY_EPOCH_STANDARD
from .template.modify_train_parameter import (generate_train_config, KEY_BATCH_SIZE,
                                              KEY_WORKER_NUM, KEY_EPOCH)


class MLLMLoRAConfig(Config):
    """
    Config write for train, eval.
    """

    def __init__(self, windmill_client: WindmillClient, tracker_client: ExperimentTracker, metadata: Dict = {}):
        super().__init__(windmill_client=windmill_client, tracker_client=tracker_client, metadata=metadata)
        self.labels = []

    def write_train_config(self,
                           dataset_uri: str,
                           model_uri: str,
                           advanced_parameters: dict,
                           pretrain_model_uri: str):
        """
        Config write for train of ppyoloe_plus_m model.
        """
        new_advanced_parameters = copy.deepcopy(advanced_parameters)

        # 1. 修改key，这几个key必须是固定的
        if KEY_WORKER_NUM_STANDARD in advanced_parameters:
            new_advanced_parameters[KEY_WORKER_NUM] = new_advanced_parameters.pop(KEY_WORKER_NUM_STANDARD)
        if KEY_BATCH_SIZE_STANDARD in advanced_parameters:
            new_advanced_parameters[KEY_BATCH_SIZE] = new_advanced_parameters.pop(KEY_BATCH_SIZE_STANDARD)
        if KEY_EPOCH_STANDARD in advanced_parameters:
            new_advanced_parameters[KEY_EPOCH] = new_advanced_parameters.pop(KEY_EPOCH_STANDARD)

        # 2. dataset路径处理
        new_advanced_parameters["dataset"] = os.path.join(dataset_uri, "train.jsonl")
        new_advanced_parameters["val_dataset"] = os.path.join(dataset_uri, "val.jsonl")

        # 3. generate train config file
        if not os.path.exists(model_uri):
            os.makedirs(model_uri, exist_ok=True)
        self._update_train_metadata(advanced_parameters=new_advanced_parameters)

        generate_train_config(new_advanced_parameters,
                              pretrain_model_uri,
                              os.path.join(model_uri, DEFAULT_TRAIN_CONFIG_FILE_NAME))

    def write_eval_config(self, dataset_uri: str, model_uri: str, ):
        """
        Config write for eval of ppyoloe_plus_m model.
        """
        pass

    def _update_train_metadata(self, advanced_parameters: Dict):
        """
        Update train metadata.
        """
        super()._update_train_metadata(advanced_parameters=advanced_parameters)
        model_meta = ModelMetadata(**self._metadata)

        advanced_parameters = {"max_length": advanced_parameters.get("max_length", 2048)}
        model_meta.algorithmParameters = advanced_parameters

        self._metadata = model_meta.dict()