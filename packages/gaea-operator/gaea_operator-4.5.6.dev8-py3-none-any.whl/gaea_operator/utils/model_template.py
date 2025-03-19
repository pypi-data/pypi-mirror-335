#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/27
# @Author  : yanxiaodong
# @File    : algorithm.py
"""
import bcelogger
from windmillmodelv1.client.model_api_modelstore import parse_modelstore_name
from windmillclient.client.windmill_client import WindmillClient

from .accelerator import get_accelerator, Accelerator


class ModelTemplate(object):
    """
    Algorithm class
    """
    PPYOLOE_PLUS_NAME = "PPYOLOEPLUS/Model"
    CHANGE_PPYOLOE_PLUS_NAME = "ChangePPYOLOEPLUS/Model"
    RESNET_NAME = "ResNet/Model"
    OCRNET_NAME = "OCRNet/Model"
    CHANGE_OCRNET_NAME = "ChangeOCRNet/Model"
    CODETR_NAME = "CODETR/Model"
    REPVIT_NAME = "RepVit/Model"
    CONVNEXT_NAME = "ConvNext/Model"
    VITBASE_NAME = "VitBase/Model"
    DBNET_NAME = "DBNet/Model"
    SVTR_LCNET_NAME = "SVTRLCNet/Model"
    CV_RESNET_NAME = "CvResNet/Model"
    YOLOSEG_NAME = "YoloSeg/Model"
    MASKFORMER_NAME = "MaskFormer/Model"
    MLLM_NAME = "MLLM/Model"

    DEFAULT_SCENE = ""

    def __init__(self, windmill_client: WindmillClient = None,
                 model_store_name: str = None,
                 scene: str = None,
                 accelerator: str = "T4",
                 algorithm: str = "PPYOLOEPLUS/Model"):
        self.windmill_client = windmill_client
        self.scene = scene
        self.accelerator = get_accelerator(name=accelerator)
        self.algorithm = algorithm
        self.workspace_id = None
        self.model_store_name = None

        if model_store_name is not None:
            model_store = parse_modelstore_name(model_store_name)
            self.workspace_id = model_store.workspace_id
            self.model_store_name = model_store.local_name

        bcelogger.info(f"Model scene is {self.scene}")

    def suggest_network_architecture(self, key: str):
        """
        Get network architecture
        """
        network_architecture = {
            ModelTemplate.PPYOLOE_PLUS_NAME: {
                "检测模型-极速版": "ppyoloe_s",
                "检测模型-标准版": "ppyoloe_m",
                "检测模型-专业版": "ppyoloe_l",
                "检测模型-高精版": "ppyoloe_x",
            },
            ModelTemplate.CHANGE_PPYOLOE_PLUS_NAME: {
                "变化检测-极速版": "change-ppyoloe_s",
                "变化检测-标准版": "change-ppyoloe_m",
                "变化检测-专业版": "change-ppyoloe_l",
                "变化检测-高精版": "change-ppyoloe_x",
            },
            ModelTemplate.RESNET_NAME: {"图像分类-极速版": "resnet_18", "图像分类-标准版": "resnet_50"},
            ModelTemplate.OCRNET_NAME: {"语义分割-标准版": "ocrnet"},
            ModelTemplate.CHANGE_OCRNET_NAME: {"变化分割-标准版": "change-ocrnet"},
            ModelTemplate.CODETR_NAME: {"目标检测大模型": "codetr"},
            ModelTemplate.DBNET_NAME: {"文字检测-极速版": "dbnet_student", "文字检测-高精版": "dbnet_teacher"},
            ModelTemplate.SVTR_LCNET_NAME: {"文字识别-标准版": "svtr_lcnet"},
            ModelTemplate.CV_RESNET_NAME: {"图像分类多任务模型-极速版": "cvresnet_18",
                                           "图像分类多任务模型-高精版": "cvresnet_50"},
            ModelTemplate.YOLOSEG_NAME: {"实例分割-标准版": "yoloseg"},
            ModelTemplate.MASKFORMER_NAME: {"高精度语义分割-标准版": "MaskFormer"},
            ModelTemplate.MLLM_NAME: {"一见多模态大模型-Lite": "yijian-mllm-lite",
                                      "一见多模态大模型-Pro": "yijian-mllm-pro"}
        }
        return network_architecture[self.algorithm][key]

    def suggest_network_architecture_v2(self, key: str):
        """
        Get network architecture
        """
        network_architecture = {
            ModelTemplate.CODETR_NAME: {"目标检测大模型": "CoDETR"},
            ModelTemplate.MASKFORMER_NAME: {"高精度语义分割-标准版": "MaskFormer"},
            ModelTemplate.PPYOLOE_PLUS_NAME: {"检测模型-标准版": "PPYoloe-plus"},
            ModelTemplate.OCRNET_NAME: {"语义分割-标准版": "OCRNet"},
            ModelTemplate.RESNET_NAME: {"图像分类-极速版": "Resnet"},
            ModelTemplate.CV_RESNET_NAME: {"图像分类多任务模型-极速版": "CVResnet"},
        }
        return network_architecture[self.algorithm][key]

    def suggest_time_profiler(self,
                              key: str,
                              kind: str = None,
                              node_name: str = ""):
        """
        Get time profiler
        """
        time_profiler = {
            "检测模型-极速版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 1.512,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "gpu_num": 1, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "gpu_num": 1.236, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.175,
                  "kind": "val",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 0.175,
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 20 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.451,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.505,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 0.491,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 0.670,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}}
                 ],
            "检测模型-标准版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 1.523,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "gpu_num": 1, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "gpu_num": 1.236, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.183,
                  "kind": "val",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 0.183,
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 20 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.491,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.535,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 0.491,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 0.535,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}}
                 ],
            "检测模型-专业版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 1.562,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "gpu_num": 1, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "gpu_num": 1.236, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.203,
                  "kind": "val",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 0.203,
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 20 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.517,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.545,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 0.517,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 0.545,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}}
                 ],
            "检测模型-高精版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 1.682,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "gpu_num": 1, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "gpu_num": 1.236, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.221,
                  "kind": "val",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 0.221,
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 20 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.688,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 0.688,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}}
                 ],
            "变化检测-极速版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 1.512,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "gpu_num": 1, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "gpu_num": 1.236, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.175,
                  "kind": "val",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 0.175,
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 20 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.451,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.505,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 0.451,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 0.505,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}}
                 ],
            "变化检测-标准版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 1.523,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "gpu_num": 1, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "gpu_num": 1.236, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.183,
                  "kind": "val",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 0.183,
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 20 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.491,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.535,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 0.491,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 0.535,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}}
                 ],
            "变化检测-专业版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 1.562,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "gpu_num": 1, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "gpu_num": 1.236, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.203,
                  "kind": "val",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 0.203,
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 20 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.517,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.545,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 0.517,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 0.545,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}}
                 ],
            "变化检测-高精版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 1.682,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "gpu_num": 1, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "gpu_num": 1.236, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.221,
                  "kind": "val",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 0.221,
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.425, "width": 0.739, "height": 0.739, "worker_num": 1.131}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 20 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.688,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.569,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 0.688,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 0.569,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}}
                 ],
            "图像分类-极速版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.177,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 16, "width": 224, "height": 224, "gpu_num": 1, "worker_num": 2},
                  "coefficients":
                      {"batch_size": 1.886, "width": 0.571, "height": 0.571, "gpu_num": 1.073, "worker_num": 1.175}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.122,
                  "kind": "val",
                  "benchmark_params":
                      {"batch_size": 16, "width": 224, "height": 224, "worker_num": 2},
                  "coefficients":
                      {"batch_size": 1.895, "width": 0.599, "height": 0.599, "worker_num": 1.427}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 0.122,
                  "benchmark_params":
                      {"batch_size": 16, "width": 224, "height": 224, "worker_num": 2},
                  "coefficients":
                      {"batch_size": 1.895, "width": 0.599, "height": 0.599, "worker_num": 1.427}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 10 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.195,
                  "benchmark_params":
                      {"width": 224, "height": 224, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.599, "height": 0.599, "precision": 1.5}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.201,
                  "benchmark_params":
                      {"width": 224, "height": 224},
                  "coefficients":
                      {"width": 0.599, "height": 0.599}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 0.195,
                  "benchmark_params":
                      {"width": 224, "height": 224, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.599, "height": 0.599, "precision": 1.1}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 0.201,
                  "benchmark_params":
                      {"width": 224, "height": 224},
                  "coefficients":
                      {"width": 0.599, "height": 0.599}}
                 ],
            "图像分类-标准版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.161,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 16, "width": 224, "height": 224, "gpu_num": 1, "worker_num": 2},
                  "coefficients":
                      {"batch_size": 1.886, "width": 0.571, "height": 0.571, "gpu_num": 1.073, "worker_num": 1.175}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.158,
                  "kind": "val",
                  "benchmark_params":
                      {"batch_size": 16, "width": 224, "height": 224, "worker_num": 2},
                  "coefficients":
                      {"batch_size": 1.895, "width": 0.599, "height": 0.599, "worker_num": 1.427}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"batch_size": 16, "width": 224, "height": 224, "worker_num": 2},
                  "coefficients":
                      {"batch_size": 1.895, "width": 0.599, "height": 0.599, "worker_num": 1.427}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 10 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.198,
                  "benchmark_params":
                      {"width": 224, "height": 224, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.599, "height": 0.599, "precision": 1.1}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.208,
                  "benchmark_params":
                      {"width": 224, "height": 224},
                  "coefficients":
                      {"width": 0.599, "height": 0.599}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 0.198,
                  "benchmark_params":
                      {"width": 224, "height": 224, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.599, "height": 0.599, "precision": 1.1}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 0.208,
                  "benchmark_params":
                      {"width": 224, "height": 224},
                  "coefficients":
                      {"width": 0.599, "height": 0.599}}
                 ],
            "语义分割-标准版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 2.320,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 8, "width": 512, "height": 512, "gpu_num": 1},
                  "coefficients":
                      {"batch_size": 1.987, "width": 0.558, "height": 0.558, "gpu_num": 1.027}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.570,
                  "kind": "val",
                  "benchmark_params":
                      {"width": 512, "height": 512, "gpu_num": 1},
                  "coefficients":
                      {"width": 0.503, "height": 0.503, "gpu_num": 1.014}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 0.570,
                  "benchmark_params":
                      {"width": 512, "height": 512, "gpu_num": 1},
                  "coefficients":
                      {"width": 0.503, "height": 0.503, "gpu_num": 1.014}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 30 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 4.0,
                  "benchmark_params":
                      {"width": 512, "height": 512, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.551, "height": 0.551, "precision": 1.1}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 3.559,
                  "benchmark_params":
                      {"width": 512, "height": 512},
                  "coefficients":
                      {"width": 0.551, "height": 0.551}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 4.0,
                  "benchmark_params":
                      {"width": 512, "height": 512, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.551, "height": 0.551, "precision": 1.1}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 3.559,
                  "benchmark_params":
                      {"width": 512, "height": 512},
                  "coefficients":
                      {"width": 0.551, "height": 0.551}}
                 ],
            "变化分割-标准版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 2.320,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 8, "width": 512, "height": 512, "gpu_num": 1},
                  "coefficients":
                      {"batch_size": 1.987, "width": 0.558, "height": 0.558, "gpu_num": 1.027}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.570,
                  "kind": "val",
                  "benchmark_params":
                      {"width": 512, "height": 512, "gpu_num": 1},
                  "coefficients":
                      {"width": 0.503, "height": 0.503, "gpu_num": 1.014}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 0.570,
                  "benchmark_params":
                      {"width": 512, "height": 512, "gpu_num": 1},
                  "coefficients":
                      {"width": 0.503, "height": 0.503, "gpu_num": 1.014}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 40 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 4.0,
                  "benchmark_params":
                      {"width": 512, "height": 512, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.551, "height": 0.551, "precision": 1.1}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 3.559,
                  "benchmark_params":
                      {"width": 512, "height": 512},
                  "coefficients":
                      {"width": 0.551, "height": 0.551}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 4.0,
                  "benchmark_params":
                      {"width": 512, "height": 512, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.551, "height": 0.551, "precision": 1.1}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 3.559,
                  "benchmark_params":
                      {"width": 512, "height": 512},
                  "coefficients":
                      {"width": 0.551, "height": 0.551}}
                 ],
            "目标检测大模型":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 1,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 1, "width": 640, "height": 640, "gpu_num": 1},
                  "coefficients":
                      {"batch_size": 1.2, "width": 0.8, "height": 0.8, "gpu_num": 1.2}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 1,
                  "kind": "val",
                  "benchmark_params":
                      {"batch_size": 1, "width": 640, "height": 640},
                  "coefficients":
                      {"batch_size": 1.2, "width": 0.8, "height": 0.8}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"batch_size": 1, "width": 640, "height": 640},
                  "coefficients":
                      {"batch_size": 1.2, "width": 0.8, "height": 0.8}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 30 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.8, "height": 0.8, "precision": 1.5}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.8, "height": 0.8}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.8, "height": 0.8, "precision": 1.5}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.8, "height": 0.8}}
                 ],
            "文字检测-极速版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 1,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 12, "width": 640, "height": 640, "gpu_num": 1, "worker_num": 2},
                  "coefficients":
                      {"batch_size": 1.2, "width": 0.8, "height": 0.8, "gpu_num": 1.2, "worker_num": 1.6}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 1,
                  "kind": "val",
                  "benchmark_params":
                      {"batch_size": 12, "width": 640, "height": 640, "gpu_num": 1, "worker_num": 2},
                  "coefficients":
                      {"batch_size": 1.2, "width": 0.8, "height": 0.8, "gpu_num": 1.2, "worker_num": 1.6}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"batch_size": 12, "width": 640, "height": 640, "gpu_num": 1, "worker_num": 2},
                  "coefficients":
                      {"batch_size": 1.2, "width": 0.8, "height": 0.8, "gpu_num": 1.2, "worker_num": 1.6}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 30 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.8, "height": 0.8, "precision": 1.5}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.8, "height": 0.8}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.8, "height": 0.8, "precision": 1.5}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.8, "height": 0.8}}
                 ],
            "文字检测-高精版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 1,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 12, "width": 640, "height": 640, "gpu_num": 1, "worker_num": 2},
                  "coefficients":
                      {"batch_size": 1.2, "width": 0.8, "height": 0.8, "gpu_num": 1.2, "worker_num": 1.6}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 1,
                  "kind": "val",
                  "benchmark_params":
                      {"batch_size": 12, "width": 640, "height": 640, "gpu_num": 1, "worker_num": 2},
                  "coefficients":
                      {"batch_size": 1.2, "width": 0.8, "height": 0.8, "gpu_num": 1.2, "worker_num": 1.6}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"batch_size": 12, "width": 640, "height": 640, "gpu_num": 1, "worker_num": 2},
                  "coefficients":
                      {"batch_size": 1.2, "width": 0.8, "height": 0.8, "gpu_num": 1.2, "worker_num": 1.6}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 30 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.8, "height": 0.8, "precision": 1.5}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.8, "height": 0.8}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.8, "height": 0.8, "precision": 1.5}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.8, "height": 0.8}}
                 ],
            "文字识别-标准版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 1,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 32, "width": 320, "height": 48, "gpu_num": 1, "worker_num": 2},
                  "coefficients":
                      {"batch_size": 1.886, "width": 0.528, "height": 0.528, "gpu_num": 1.073, "worker_num": 1.129}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.071,
                  "kind": "val",
                  "benchmark_params":
                      {"width": 320, "height": 48},
                  "coefficients":
                      {"width": 0.528, "height": 0.528}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 0.071,
                  "benchmark_params":
                      {"width": 320, "height": 48},
                  "coefficients":
                      {"width": 0.528, "height": 0.528}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 10 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.085,
                  "benchmark_params":
                      {"width": 320, "height": 48, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.528, "height": 0.528, "precision": 1.5}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 320, "height": 48},
                  "coefficients":
                      {"width": 0.528, "height": 0.528}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 0.085,
                  "benchmark_params":
                      {"width": 320, "height": 48, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.528, "height": 0.528, "precision": 1.5}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 320, "height": 48},
                  "coefficients":
                      {"width": 0.528, "height": 0.528}}
                 ],
            "图像分类多任务模型-极速版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.122,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 8, "width": 224, "height": 224, "gpu_num": 1, "worker_num": 1},
                  "coefficients":
                      {"batch_size": 1.101, "width": 0.571, "height": 0.571, "gpu_num": 1.073, "worker_num": 3.752}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.072,
                  "kind": "val",
                  "benchmark_params":
                      {"width": 224, "height": 224, "gpu_num": 1},
                  "coefficients":
                      {"width": 0.571, "height": 0.571, "gpu_num": 1.073}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 0.072,
                  "benchmark_params":
                      {"width": 224, "height": 224, "gpu_num": 1},
                  "coefficients":
                      {"width": 0.571, "height": 0.571, "gpu_num": 1.073}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 10 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.054,
                  "benchmark_params":
                      {"width": 224, "height": 224, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.599, "height": 0.599, "precision": 1.1}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.054,
                  "benchmark_params":
                      {"width": 224, "height": 224},
                  "coefficients":
                      {"width": 0.599, "height": 0.599}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 0.054,
                  "benchmark_params":
                      {"width": 224, "height": 224, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.599, "height": 0.599, "precision": 1.1}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 0.054,
                  "benchmark_params":
                      {"width": 224, "height": 224},
                  "coefficients":
                      {"width": 0.599, "height": 0.599}}
                 ],
            "图像分类多任务模型-高精版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.242,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 8, "width": 224, "height": 224, "gpu_num": 1, "worker_num": 1},
                  "coefficients":
                      {"batch_size": 1.101, "width": 0.571, "height": 0.571, "gpu_num": 1.073, "worker_num": 3.752}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.092,
                  "kind": "val",
                  "benchmark_params":
                      {"width": 224, "height": 224, "gpu_num": 1},
                  "coefficients":
                      {"width": 0.571, "height": 0.571, "gpu_num": 1.073}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 0.092,
                  "benchmark_params":
                      {"width": 224, "height": 224, "gpu_num": 1},
                  "coefficients":
                      {"width": 0.571, "height": 0.571, "gpu_num": 1.073}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 10 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 224, "height": 224, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.599, "height": 0.599, "precision": 1.1}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 1,
                  "benchmark_params":
                      {"width": 224, "height": 224},
                  "coefficients":
                      {"width": 0.599, "height": 0.599}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 0.059,
                  "benchmark_params":
                      {"width": 224, "height": 224, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.599, "height": 0.599, "precision": 1.1}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 0.059,
                  "benchmark_params":
                      {"width": 224, "height": 224},
                  "coefficients":
                      {"width": 0.599, "height": 0.599}}
                 ],
            "实例分割-标准版":
                [{"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.499,
                  "kind": "train",
                  "benchmark_params":
                      {"batch_size": 8, "width": 640, "height": 640, "gpu_num": 1, "worker_num": 4},
                  "coefficients":
                      {"batch_size": 1.683, "width": 0.739, "height": 0.739, "gpu_num": 1.236, "worker_num": 1.951}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "train",
                  "benchmark_time": 0.482,
                  "kind": "val",
                  "benchmark_params":
                      {"width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"width": 0.739, "height": 0.739, "worker_num": 1.593}},
                 {"accelerator_name": Accelerator.V100,
                  "node_name": "eval",
                  "benchmark_time": 0.482,
                  "benchmark_params":
                      {"width": 640, "height": 640, "worker_num": 4},
                  "coefficients":
                      {"width": 0.739, "height": 0.739, "worker_num": 1.593}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform",
                  "benchmark_time": 20 * 60},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform",
                  "benchmark_time": 0},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.591,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "transform-eval",
                  "benchmark_time": 0.591,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}},
                 {"accelerator_name": Accelerator.T4,
                  "node_name": "inference",
                  "benchmark_time": 0.591,
                  "benchmark_params":
                      {"width": 640, "height": 640, "precision": "fp16"},
                  "coefficients":
                      {"width": 0.679, "height": 0.679, "precision": 1.439}},
                 {"accelerator_name": Accelerator.R200,
                  "node_name": "inference",
                  "benchmark_time": 0.591,
                  "benchmark_params":
                      {"width": 640, "height": 640},
                  "coefficients":
                      {"width": 0.679, "height": 0.679}}
                 ]
        }

        for item in time_profiler.get(key, []):
            if not (item["node_name"] == node_name and item["accelerator_name"] == self.accelerator.get_name):
                continue
            if kind is not None and item.get("kind") != kind:
                continue

            return item

        return {"benchmark_time": 1, "benchmark_params": {}, "coefficients": {}}

    def suggest_template_model(self):
        """
        Get template name for model
        """
        tags = [{"algorithm": self.algorithm}]
        if self.scene is not None and len(self.scene) > 0:
            tags.append({"scene": self.scene})
        else:
            tags.append({"scene": self.DEFAULT_SCENE})

        bcelogger.info(f"List model for workspace_id {self.workspace_id} "
                       f"model_store_name {self.model_store_name} "
                       f"and tags {tags}")
        response = self.windmill_client.list_model(workspace_id=self.workspace_id,
                                                   model_store_name=self.model_store_name,
                                                   tags=tags)
        assert len(response.result) > 0, f"No model found for tags {tags}"
        for model in response.result:
            model_accelerator = model["preferModelServerParameters"]["resource"]["accelerator"]
            if self.accelerator.get_name in \
                    Accelerator.NVIDIA_SPECIAL + Accelerator.KUNLUN_SPECIAL + Accelerator.ASCEND_SPECIAL:
                if get_accelerator(name=model_accelerator).get_name == self.accelerator.get_name:
                    bcelogger.info(f"Model {model['name']} found by {self.accelerator.get_name}")
                    return model["name"]
            else:
                if get_accelerator(name=model_accelerator).get_kind == self.accelerator.get_kind:
                    bcelogger.info(f"Model {model['name']} found by {self.accelerator.get_kind}")
                    return model["name"]
        raise ValueError(f"The model {response.result} not found for kind {self.accelerator.get_kind}")

    def suggest_template_ensemble(self):
        """
        Get template name for ensemble
        """
        if self.scene is not None and len(self.scene) > 0:
            scene_list = self.scene.rsplit("/", maxsplit=1)
            assert len(scene_list) >= 1, f"Scene {self.scene} is not valid."

            ensemble_scene = scene_list[0] + "/" + "Ensemble"
            tags = [{"scene": ensemble_scene}]
        else:
            algorithm_list = self.algorithm.rsplit("/", maxsplit=1)
            assert len(algorithm_list) >= 1, f"Algorithm {self.algorithm} is not valid."
            ensemble_algorithm = algorithm_list[0] + "/" + "Ensemble"
            tags = [{"algorithm": ensemble_algorithm, "scene": self.DEFAULT_SCENE}]

        bcelogger.info(f"List model for workspace_id {self.workspace_id} "
                       f"model_store_name {self.model_store_name} "
                       f"and tags {tags}")
        response = self.windmill_client.list_model(workspace_id=self.workspace_id,
                                                   model_store_name=self.model_store_name,
                                                   tags=tags)
        assert len(response.result) > 0, f"No model found for tags {tags}"
        for model in response.result:
            model_accelerator = model["preferModelServerParameters"]["resource"]["accelerator"]
            if self.accelerator.get_name in \
                    Accelerator.NVIDIA_SPECIAL + Accelerator.KUNLUN_SPECIAL + Accelerator.ASCEND_SPECIAL:
                if get_accelerator(name=model_accelerator).get_name == self.accelerator.get_name:
                    bcelogger.info(f"Model {model['name']} found by {self.accelerator.get_name}")
                    return model["name"]
            else:
                if get_accelerator(name=model_accelerator).get_kind == self.accelerator.get_kind:
                    bcelogger.info(f"Model {model['name']} found by {self.accelerator.get_kind}")
                    return model["name"]
        raise ValueError(f"The model {response.result} not found for kind {self.accelerator.get_kind}")

    def suggest_template_preprocess(self):
        """
        Get template name for preprocess
        """
        if self.scene is not None and len(self.scene) > 0:
            scene_list = self.scene.split("/", maxsplit=1)
            assert len(scene_list) >= 1, f"Scene {self.scene} is not valid."

            ensemble_scene = scene_list[0] + "/" + "Preprocess"
            tags = [{"scene": ensemble_scene}]
        else:
            algorithm_list = self.algorithm.split("/", maxsplit=1)
            assert len(algorithm_list) >= 1, f"Algorithm {self.algorithm} is not valid."
            ensemble_algorithm = algorithm_list[0] + "/" + "Preprocess"
            tags = [{"algorithm": ensemble_algorithm}]

        bcelogger.info(f"List model for workspace_id {self.workspace_id} "
                       f"model_store_name {self.model_store_name} "
                       f"and tags {tags}")
        response = self.windmill_client.list_model(workspace_id=self.workspace_id,
                                                   model_store_name=self.model_store_name,
                                                   tags=tags)
        assert len(response.result) > 0, f"No model found for tags {tags}"
        for model in response.result:
            model_accelerator = model["preferModelServerParameters"]["resource"]["accelerator"]
            if self.accelerator.get_name in \
                    Accelerator.NVIDIA_SPECIAL + Accelerator.KUNLUN_SPECIAL + Accelerator.ASCEND_SPECIAL:
                if get_accelerator(name=model_accelerator).get_name == self.accelerator.get_name:
                    bcelogger.info(f"Model {model['name']} found by {self.accelerator.get_name}")
                    return model["name"]
            else:
                if get_accelerator(name=model_accelerator).get_kind == self.accelerator.get_kind:
                    bcelogger.info(f"Model {model['name']} found by {self.accelerator.get_kind}")
                    return model["name"]
        raise ValueError(f"The model {response.result} not found for kind {self.accelerator.get_kind}")

    def suggest_template_postprocess(self):
        """
        Get template name for postprocess
        """
        if self.scene is not None and len(self.scene) > 0:
            scene_list = self.scene.split("/", maxsplit=1)
            assert len(scene_list) >= 1, f"Scene {self.scene} is not valid."

            ensemble_scene = scene_list[0] + "/" + "Postprocess"
            tags = [{"scene": ensemble_scene}]
        else:
            algorithm_list = self.algorithm.split("/", maxsplit=1)
            assert len(algorithm_list) >= 1, f"Algorithm {self.algorithm} is not valid."
            ensemble_algorithm = algorithm_list[0] + "/" + "Postprocess"
            tags = [{"algorithm": ensemble_algorithm}]

        bcelogger.info(f"List model for workspace_id {self.workspace_id} "
                       f"model_store_name {self.model_store_name} "
                       f"and tags {tags}")
        response = self.windmill_client.list_model(workspace_id=self.workspace_id,
                                                   model_store_name=self.model_store_name,
                                                   tags=tags)
        assert len(response.result) > 0, f"No model found for tags {tags}"
        for model in response.result:
            model_accelerator = model["preferModelServerParameters"]["resource"]["accelerator"]
            if self.accelerator.get_name in \
                    Accelerator.NVIDIA_SPECIAL + Accelerator.KUNLUN_SPECIAL + Accelerator.ASCEND_SPECIAL:
                if get_accelerator(name=model_accelerator).get_name == self.accelerator.get_name:
                    bcelogger.info(f"Model {model['name']} found by {self.accelerator.get_name}")
                    return model["name"]
            else:
                if get_accelerator(name=model_accelerator).get_kind == self.accelerator.get_kind:
                    bcelogger.info(f"Model {model['name']} found by {self.accelerator.get_kind}")
                    return model["name"]
        raise ValueError(f"The model {response.result} not found for kind {self.accelerator.get_kind}")
