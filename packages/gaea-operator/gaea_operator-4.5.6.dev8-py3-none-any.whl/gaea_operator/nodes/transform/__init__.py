#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/12
# @Author  : yanxiaodong
# @File    : __init__.py.py
"""
from typing import Dict, List
from paddleflow.pipeline import ContainerStep
from paddleflow.pipeline import Artifact

import bcelogger

from ..base_node import BaseNode, set_node_parameters
from ..types import Properties, ModelFormat
from gaea_operator.artifacts import Variable
from gaea_operator.utils import Accelerator, get_accelerator, ModelTemplate


class Transform(BaseNode):
    """
    Transform
    """
    NAME = "transform"
    DISPLAY_NAME = "模型转换"

    def __init__(self,
                 config: Dict = None,
                 transform_skip: int = -1,
                 algorithm: str = "",
                 category: str = "",
                 accelerator: str = Accelerator.T4,
                 pre_nodes: Dict[str, ContainerStep] = None):
        if config is None:
            # 兼容历史产线
            model_formats = {
                Accelerator.NVIDIA: {f"{self.name()}.train_model_name": ["PaddlePaddle", "PyTorch"],
                                     f"{self.name()}.transform_model_name": ["TensorRT"]},
                Accelerator.KUNLUN: {f"{self.name()}.train_model_name": ["PaddlePaddle", "PyTorch"],
                                     f"{self.name()}.transform_model_name": ["PaddleLite"]},
                Accelerator.ASCEND: {f"{self.name()}.train_model_name": ["PaddlePaddle", "PyTorch"],
                                     f"{self.name()}.transform_model_name": ["Other"]},
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
                Variable(type="model",
                         name="output_model_uri",
                         displayName="模型转换后的模型",
                         key=f"{self.name()}.transform_model_name",
                         value="transform.output_model_uri")
            ]

        super().__init__(inputs=inputs, outputs=outputs, properties=properties)

        self.transform_skip = transform_skip
        self.algorithm = algorithm
        self.category = category
        self.pre_nodes = pre_nodes

    def set_compute_tips(self, accelerator_kind: str, accelerator_name: str = None):
        """
        set compute tips
        """
        if accelerator_kind == Accelerator.KUNLUN:
            return ["training"]
        accelerator = get_accelerator(kind=accelerator_kind, name=accelerator_name)
        return ["training", f"tags.accelerator={accelerator.get_name}"] + accelerator.suggest_resource_tips()

    def set_flavour_tips(self, accelerator_kind: str = None, accelerator_name: str = None):
        """
        set compute tips
        """
        if accelerator_kind == Accelerator.KUNLUN:
            return "c4m16"
        accelerator = get_accelerator(kind=accelerator_kind, name=accelerator_name)
        return accelerator.suggest_flavour_tips()

    def suggest_time_profiler(self):
        """
        suggest time profiler
        """
        model_template = ModelTemplate(accelerator=self.properties.accelerator)
        time_profiler_params = model_template.suggest_time_profiler(
            key=self.properties.timeProfilerParams.networkArchitecture, node_name=self.name())

        assert "benchmark_time" in time_profiler_params, "Benchmark time not in time profiler params"
        time_count = time_profiler_params["benchmark_time"]
        bcelogger.info(f"Transform time count: {time_count}")

        return time_count

    def __call__(self,
                 base_params: dict = None,
                 base_env: dict = None,
                 train_model_name: str = "",
                 transform_model_name: str = "",
                 transform_model_display_name: str = "",
                 advanced_parameters: str = ""):
        """
        call
        """
        transform_params = {"skip": self.transform_skip,
                            "train_model_name": train_model_name,
                            "transform_model_name": transform_model_name,
                            "transform_model_display_name": transform_model_display_name,
                            "accelerator": self.properties.accelerator,
                            "advanced_parameters": advanced_parameters}
        transform_env = {"TRAIN_MODEL_NAME": "{{train_model_name}}",
                         "TRANSFORM_MODEL_NAME": "{{transform_model_name}}",
                         "TRANSFORM_MODEL_DISPLAY_NAME": "{{transform_model_display_name}}",
                         "ACCELERATOR": "{{accelerator}}",
                         "ADVANCED_PARAMETERS": "{{advanced_parameters}}"}
        transform_env.update(base_env)
        transform_params.update(base_params)

        transform = ContainerStep(name=Transform.name(),
                                  docker_env=self.suggest_image(),
                                  env=transform_env,
                                  parameters=transform_params,
                                  outputs={"output_model_uri": Artifact(), "output_uri": Artifact()},
                                  command=f'cd /root && '
                                          f'python3 -m gaea_operator.nodes.transform.transform '
                                          f'--algorithm={self.algorithm} '
                                          f'--category={self.category} '
                                          f'--input-model-uri={{{{input_model_uri}}}} '
                                          f'--output-uri={{{{output_uri}}}} '
                                          f'--output-model-uri={{{{output_model_uri}}}}')
        set_node_parameters(skip=self.transform_skip, step=transform, inputs=self.inputs, pre_nodes=self.pre_nodes)

        return transform