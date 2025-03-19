#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/12
# @Author  : yanxiaodong
# @File    : __init__.py.py
"""
from typing import List, Dict
import json
from paddleflow.pipeline import ContainerStep
from paddleflow.pipeline import Artifact
from paddleflow.pipeline import ExtraFS

import bcelogger

from ..base_node import BaseNode, calculate_train_time
from ..types import Properties, ModelFormat
from gaea_operator.artifacts import Variable
from gaea_operator.utils import Accelerator, get_accelerator, ModelTemplate


class Train(BaseNode):
    """
    Train
    """
    NAME = "train"
    DISPLAY_NAME = "模型训练"

    def __init__(self,
                 config: Dict = None,
                 train_skip: int = -1,
                 algorithm: str = "",
                 is_pdc: bool = False,
                 accelerator: str = Accelerator.V100):
        if config is None:
            # 兼容历史产线
            model_formats = {
                Accelerator.NVIDIA: {f"{self.name()}.model_name": ["PaddlePaddle", "PyTorch"]},
                Accelerator.ASCEND: {f"{self.name()}.model_name": ["PaddlePaddle", "PyTorch"]},
            }
        else:
            model_formats = []
            for model in config["models"]:
                if "acceleratorKind" in model:
                    model_formats.append(ModelFormat(key=f'{self.name()}.{model["key"]}',
                                                     acceleratorKind=model["acceleratorKind"],
                                                     formats=model["modelFormats"]))
                elif "acceleratorName" in model:
                    model_formats.append(ModelFormat(key=f'{self.name()}.{model["key"]}',
                                                     acceleratorName=model["acceleratorName"],
                                                     formats=model["modelFormats"]))
                else:
                    raise ValueError(f"Config model acceleratorKind or acceleratorName must be specified, "
                                     f"but got {model}")

        properties = Properties(accelerator=accelerator,
                                is_pdc=is_pdc,
                                computeTips={
                                    Accelerator.NVIDIA: self.set_compute_tips(accelerator_kind=Accelerator.NVIDIA),
                                    Accelerator.KUNLUN: self.set_compute_tips(accelerator_kind=Accelerator.KUNLUN),
                                    Accelerator.ASCEND: self.set_compute_tips(accelerator_kind=Accelerator.ASCEND),
                                },
                                flavourTips={
                                    Accelerator.NVIDIA: self.set_flavour_tips(accelerator_kind=Accelerator.NVIDIA),
                                    Accelerator.KUNLUN: self.set_flavour_tips(accelerator_kind=Accelerator.KUNLUN),
                                    Accelerator.ASCEND: self.set_flavour_tips(accelerator_kind=Accelerator.ASCEND),
                                },
                                modelFormats=model_formats)

        outputs: List[Variable] = \
            [
                Variable(type="model",
                         name="output_model_uri",
                         displayName="模型训练后的模型",
                         key=f"{self.name()}.model_name",
                         value="train.output_model_uri")
            ]

        super().__init__(outputs=outputs, properties=properties)
        self.train_skip = train_skip
        self.algorithm = algorithm
        self.algorithm = algorithm

    def set_compute_tips(self, accelerator_kind: str, accelerator_name: str = None):
        """
        set compute tips
        """
        accelerator = get_accelerator(kind=accelerator_kind, name=accelerator_name)
        return ["training", "tags.usage=train"] + accelerator.suggest_resource_tips()

    def set_flavour_tips(self, accelerator_kind: str, accelerator_name: str = None):
        """
        set compute tips
        """
        accelerator = get_accelerator(kind=accelerator_kind, name=accelerator_name)
        return accelerator.suggest_flavour_tips()

    def suggest_time_profiler(self):
        """
        suggest time profiler
        """
        model_template = ModelTemplate(accelerator=self.properties.accelerator)
        time_profiler_params = model_template.suggest_time_profiler(
            key=self.properties.timeProfilerParams.networkArchitecture, kind="train", node_name=self.name())

        train_time_count = calculate_train_time(benchmark=time_profiler_params,
                                                epoch=self.properties.timeProfilerParams.epoch,
                                                image_count=self.properties.timeProfilerParams.trainImageCount,
                                                batch_size=self.properties.timeProfilerParams.batchSize,
                                                width=self.properties.timeProfilerParams.width,
                                                height=self.properties.timeProfilerParams.height,
                                                eval_size=self.properties.timeProfilerParams.evalSize,
                                                gpu_num=self.properties.timeProfilerParams.gpuNum,
                                                worker_num=self.properties.timeProfilerParams.workerNum)
        bcelogger.info(f"Train time count: {train_time_count}")

        time_profiler_params = model_template.suggest_time_profiler(
            key=self.properties.timeProfilerParams.networkArchitecture, kind="val", node_name=self.name())
        val_time_count = calculate_train_time(benchmark=time_profiler_params,
                                              epoch=1,
                                              image_count=self.properties.timeProfilerParams.valImageCount,
                                              batch_size=self.properties.timeProfilerParams.batchSize,
                                              width=self.properties.timeProfilerParams.width,
                                              height=self.properties.timeProfilerParams.height,
                                              eval_size=self.properties.timeProfilerParams.evalSize,
                                              gpu_num=self.properties.timeProfilerParams.gpuNum,
                                              worker_num=self.properties.timeProfilerParams.workerNum)
        bcelogger.info(f"Val time count: {val_time_count}")

        return train_time_count + val_time_count

    def set_train_params(self,
                         train_dataset_name: str = "",
                         val_dataset_name: str = "",
                         base_train_dataset_name: str = "",
                         base_val_dataset_name: str = "",
                         train_model_name: str = "",
                         train_model_display_name: str = ""):
        """
        set train params
        """
        train_params = {"skip": self.train_skip,
                        "train_dataset_name": train_dataset_name,
                        "val_dataset_name": val_dataset_name,
                        "base_train_dataset_name": base_train_dataset_name,
                        "base_val_dataset_name": base_val_dataset_name,
                        "model_name": train_model_name,
                        "is_early_stopping": "False",
                        "early_stopping_patience": "10",
                        "image": self.suggest_image(),
                        "pdc_params": '{"pdc_ak":"xxxx", '
                                      '"pdc_sk":"xxx",'
                                      '"algo_id":"xxxx",'
                                      '"train_group_name":"xxxx",'
                                      '"k8s_gpu_cards":"4"}',
                        "is_pdc": str(self.properties.is_pdc),
                        "model_display_name": train_model_display_name,
                        "accelerator": self.properties.accelerator,
                        "model_formats": json.dumps(self.suggest_model_formats(key=f"{self.name()}.model_name")),
                        "advanced_parameters": '{"epoch":"100",'
                                               '"lr_scheduler.learning_rate":"0.001",'
                                               '"eval_height":"512",'
                                               '"eval_width":"512",'
                                               '"batch_size":"6",'
                                               '"networkArchitecture":"ocrnet"}'}
        return train_params

    def set_train_env(self, extra_fs_mount_path: str):
        """
        set train env
        """
        train_env = {"TRAIN_DATASET_NAME": "{{train_dataset_name}}",
                     "VAL_DATASET_NAME": "{{val_dataset_name}}",
                     "BASE_TRAIN_DATASET_NAME": "{{base_train_dataset_name}}",
                     "BASE_VAL_DATASET_NAME": "{{base_val_dataset_name}}",
                     "MODEL_NAME": "{{model_name}}",
                     "IS_EARLY_STOPPING": "{{is_early_stopping}}",
                     "EARLY_STOPPING_PATIENCE": "{{early_stopping_patience}}",
                     "MODEL_DISPLAY_NAME": "{{model_display_name}}",
                     "MODEL_FORMATS": "{{model_formats}}",
                     "IS_PDC": "{{is_pdc}}",
                     "IMAGE": "{{image}}",
                     "PDC_PARAMS": "{{pdc_params}}",
                     "ACCELERATOR": "{{accelerator}}",
                     "ADVANCED_PARAMETERS": "{{advanced_parameters}}",
                     "PF_EXTRA_WORK_DIR": extra_fs_mount_path}
        return train_env

    def __call__(self,
                 base_params: dict = None,
                 base_env: dict = None,
                 extra_fs_name: str = "vistudio",
                 extra_fs_mount_path: str = "/home/paddleflow/storage/mnt/fs-root-vistudio",
                 train_dataset_name: str = "",
                 val_dataset_name: str = "",
                 base_train_dataset_name: str = "",
                 base_val_dataset_name: str = "",
                 train_model_name: str = "",
                 train_model_display_name: str = ""):
        train_params = self.set_train_params(train_dataset_name=train_dataset_name,
                                             val_dataset_name=val_dataset_name,
                                             base_train_dataset_name=base_train_dataset_name,
                                             base_val_dataset_name=base_val_dataset_name,
                                             train_model_name=train_model_name,
                                             train_model_display_name=train_model_display_name)
        train_env = self.set_train_env(extra_fs_mount_path=extra_fs_mount_path)
        train_env.update(base_env)
        train_params.update(base_params)

        train = ContainerStep(name=Train.name(),
                              docker_env=self.suggest_image(),
                              parameters=train_params,
                              env=train_env,
                              extra_fs=[ExtraFS(name=extra_fs_name, mount_path=extra_fs_mount_path)],
                              outputs={"output_model_uri": Artifact(), "output_uri": Artifact()},
                              command=f'cd /root && '
                                      f'python3 -m gaea_operator.nodes.train.cv_algo '
                                      f'--algorithm={self.algorithm} '
                                      f'--output-model-uri={{{{output_model_uri}}}} '
                                      f'--output-uri={{{{output_uri}}}} ')
        if self.train_skip > 0:
            skip_parameter = "skip"
            train.condition = f"{train.parameters[skip_parameter]} < 0"

        return train
