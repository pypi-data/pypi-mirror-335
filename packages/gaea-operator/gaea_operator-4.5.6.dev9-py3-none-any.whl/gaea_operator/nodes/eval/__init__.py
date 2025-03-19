#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/12
# @Author  : yanxiaodong
# @File    : __init__.py.py
"""
from typing import List, Dict
from paddleflow.pipeline import ContainerStep
from paddleflow.pipeline import Artifact

import bcelogger

from ..base_node import BaseNode, set_node_parameters, calculate_train_time
from ..types import Properties, ModelFormat
from gaea_operator.artifacts import Variable
from gaea_operator.utils import Accelerator, get_accelerator, ModelTemplate


class Eval(BaseNode):
    """
    Train
    """
    NAME = "eval"
    DISPLAY_NAME = "模型评估"

    def __init__(self,
                 config: Dict = None,
                 eval_skip: int = -1,
                 algorithm: str = "",
                 accelerator: str = Accelerator.V100,
                 pre_nodes: Dict[str, ContainerStep] = None):
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

        inputs: List[Variable] = \
            [
                Variable(type="model", name="input_model_uri", value="train.output_model_uri")
            ]
        outputs: List[Variable] = \
            [
                Variable(type="dataset",
                         name="output_dataset_uri",
                         displayName="模型评估的数据集",
                         value="eval.output_dataset_uri"),
                Variable(type="model",
                         name="output_model_uri",
                         displayName="模型评估后的模型",
                         key=f"{self.name()}.model_name",
                         value="eval.output_model_uri")
            ]

        super().__init__(inputs=inputs, outputs=outputs, properties=properties)
        self.eval_skip = eval_skip
        self.algorithm = algorithm
        self.pre_nodes = pre_nodes

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
            key=self.properties.timeProfilerParams.networkArchitecture, node_name=self.name())

        time_count = calculate_train_time(benchmark=time_profiler_params,
                                          epoch=1,
                                          image_count=self.properties.timeProfilerParams.evalImageCount,
                                          batch_size=self.properties.timeProfilerParams.batchSize,
                                          width=self.properties.timeProfilerParams.width,
                                          height=self.properties.timeProfilerParams.height,
                                          eval_size=self.properties.timeProfilerParams.evalSize,
                                          gpu_num=self.properties.timeProfilerParams.gpuNum,
                                          worker_num=self.properties.timeProfilerParams.workerNum)
        bcelogger.info(f"Eval time count: {time_count}")

        return time_count

    def __call__(self,
                 base_params: dict = None,
                 base_env: dict = None,
                 eval_dataset_name: str = "",
                 eval_model_name: str = ""):
        eval_params = {"skip": self.eval_skip,
                       "dataset_name": eval_dataset_name,
                       "accelerator": self.properties.accelerator,
                       "model_name": eval_model_name}
        eval_env = {"DATASET_NAME": "{{dataset_name}}",
                    "ACCELERATOR": "{{accelerator}}",
                    "MODEL_NAME": "{{model_name}}"}
        eval_env.update(base_env)
        eval_params.update(base_params)

        eval = ContainerStep(name=Eval.name(),
                             docker_env=self.suggest_image(),
                             parameters=eval_params,
                             env=eval_env,
                             outputs={"output_uri": Artifact(),
                                      "output_dataset_uri": Artifact(),
                                      "output_model_uri": Artifact()},
                             command=f'cd /root && '
                                     f'python3 -m gaea_operator.nodes.eval.cv_algo '
                                     f'--input-model-uri={{{{input_model_uri}}}} '
                                     f'--output-uri={{{{output_uri}}}} '
                                     f'--output-dataset-uri={{{{output_dataset_uri}}}} '
                                     f'--output-model-uri={{{{output_model_uri}}}} ')
        set_node_parameters(skip=self.eval_skip, step=eval, inputs=self.inputs, pre_nodes=self.pre_nodes)

        return eval