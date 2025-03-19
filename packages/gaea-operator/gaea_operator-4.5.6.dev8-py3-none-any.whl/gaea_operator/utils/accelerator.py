#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/27
# @Author  : yanxiaodong
# @File    : accelerator.py
"""
from typing import Dict, List
from abc import ABCMeta, abstractmethod


class Accelerator(metaclass=ABCMeta):
    """
    Accelerator
    """
    T4 = "T4"
    V100 = "V100"
    A100 = "A100"
    A10 = "A10"
    A40 = "A40"
    A800 = "A800"
    R480 = "R480"
    R200 = "R200"
    P800 = "P800"

    Atlas310P = "Atlas310P"
    Ascend910B = "Ascend910B"

    NVIDIA = "Nvidia"
    KUNLUN = "Kunlun"
    ASCEND = "Ascend"

    NVIDIA_COMMON = [T4, V100, A100, A10, A40, A800]
    NVIDIA_SPECIAL = []
    KUNLUN_COMMON = [R200]
    KUNLUN_SPECIAL = [P800, R480]
    ASCEND_COMMON = [Atlas310P, Ascend910B]
    ASCEND_SPECIAL = []

    def __init__(self, kind: str = None, name: str = "T4"):
        self.name = name
        self.image = ""
        self.args = None
        self.env = None

        self._kind = kind

    @property
    def get_name(self):
        """
        Name
        """
        if self.name is None:
            if self.get_kind == self.NVIDIA:
                self.name = self.NVIDIA_COMMON[0]
            elif self.get_kind == self.KUNLUN:
                self.name = self.KUNLUN_COMMON[0]
            elif self.get_kind == self.ASCEND:
                self.name = self.ASCEND_COMMON[0]
            else:
                raise ValueError(f"Invalid accelerator kind {self.get_kind}")
        return self.name

    def get_names(self, filter_names: List = None):
        """
        Name
        """
        names = \
            self.NVIDIA_COMMON + self.NVIDIA_SPECIAL + self.KUNLUN_COMMON + \
            self.KUNLUN_SPECIAL + self.ASCEND_COMMON + self.ASCEND_SPECIAL

        if filter_names is None:
            return names

        return list(set(names) & set(filter_names))

    @property
    def get_special_names(self):
        """
        Name
        """
        return self.NVIDIA_SPECIAL + self.KUNLUN_SPECIAL + self.ASCEND_SPECIAL

    @property
    def get_kind(self):
        """
        Kind
        """
        if self._kind is None:
            name_list = self.name.split("/", maxsplit=1)
            if len(name_list) > 1:
                self._kind = name_list[0]
            elif len(name_list) == 1:
                if self.name in self.NVIDIA_COMMON + self.NVIDIA_SPECIAL:
                    self._kind = self.NVIDIA
                elif self.name in self.KUNLUN_COMMON + self.KUNLUN_SPECIAL:
                    self._kind = self.KUNLUN
                elif self.name in self.ASCEND_COMMON + self.ASCEND_SPECIAL:
                    self._kind = self.ASCEND
                else:
                    self._kind = self.NVIDIA
                    raise ValueError(f"Invalid accelerator name {self.name}")
            else:
                self._kind = self.NVIDIA
                raise ValueError(f"Invalid accelerator name {self.name}")
        return self._kind

    def set_image(self, name_to_image: Dict = None):
        """
        Set image
        """
        if name_to_image is not None:
            self.image = name_to_image.get(self.name, self.image)

    def suggest_image(self):
        """
        Suggest image
        """
        return self.image

    def suggest_env(self):
        """
        Suggest env
        """
        return self.env

    def suggest_args(self):
        """
        Suggest args
        """
        return self.args

    @abstractmethod
    def suggest_flavours(self):
        """
        Suggest flavours
        """
        raise NotImplementedError()

    @abstractmethod
    def suggest_flavour_tips(self):
        """
        Suggest flavours
        """
        raise NotImplementedError()

    @abstractmethod
    def suggest_model_server_parameters(self):
        """
        Suggest model server parameters
        """
        raise NotImplementedError()

    @abstractmethod
    def suggest_resource_tips(self):
        """
        Suggest resource tips
        """
        raise NotImplementedError()


class NvidiaAccelerator(Accelerator):
    """
    Nvidia Accelerator
    """
    def __init__(self, kind: str = None, name: str = "T4"):
        super().__init__(kind=kind, name=name)
        self.image = \
            "iregistry.baidu-int.com/acg_aiqp_algo/triton-inference-server/triton_r22_12_nvidia_infer_trt86:1.4.6"
        self.args = {"backend-config": "tensorrt,plugins=/opt/tritonserver/lib/libmmdeploy_tensorrt_ops.so"}
        self.env = \
            {
                "LD_LIBRARY_PATH":
                    "/usr/local/cuda/compat/lib:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/opt/tritonserver/lib",
                "PATH": "/opt/tritonserver/bin:/usr/local/mpi/bin:/usr/local/nvidia/bin:/usr/local/cuda/bin:"
                        "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/ucx/bin"
            }

    def suggest_flavours(self):
        """
        Suggest flavours
        """
        flavour_list = [{"name": "c4m16gpu1", "display_name": "CPU: 4核 内存: 16Gi GPU: 1卡"},
                        {"name": "c8m32gpu1", "display_name": "CPU: 8核 内存: 32Gi GPU: 1卡"},
                        {"name": "c8m32gpu2", "display_name": "CPU: 8核 内存: 32Gi GPU: 2卡"},
                        {"name": "c16m64gpu2", "display_name": "CPU: 16核 内存: 64Gi GPU: 2卡"},
                        {"name": "c16m32gpu4", "display_name": "CPU: 16核 内存: 32Gi GPU: 4卡"},
                        {"name": "c16m64gpu4", "display_name": "CPU: 16核 内存: 64Gi GPU: 4卡"},
                        {"name": "c32m96gpu4", "display_name": "CPU: 32核 内存: 96Gi GPU: 4卡"}]

        return flavour_list

    def suggest_flavour_tips(self):
        """
        Suggest flavour tips
        """
        return "gpu"

    def suggest_model_server_parameters(self):
        """
        Suggest model server parameters
        """
        resource = {"accelerator": self.name,
                    "gpu": "7500",
                    "limits": {"cpu": "10", "mem": "10Gi"},
                    "requests": {"cpu": "100m", "mem": "50Mi"}}
        model_server_parameters = {
            "image": self.image,
            "env": self.env,
            "args": self.args,
            "resource": resource}

        return model_server_parameters

    def suggest_resource_tips(self):
        """
        Suggest resource tips
        """
        return ["config.maxResources.scalarResources.nvidia.com/gpu>1"]


class KunlunAccelerator(Accelerator):
    """
    Kunlun Accelerator
    """
    def __init__(self, kind: str = None, name: str = "R200"):
        super().__init__(kind=kind, name=name)
        self.image = "iregistry.baidu-int.com/acg_aiqp_algo/triton-inference-server/triton_r22_12_kunlun_infer:2.2.4"
        self.args = {"backend-config": "tensorrt,plugins=/opt/tritonserver/lib/libmmdeploy_tensorrt_ops.so"}
        self.env = \
            {
                "LD_LIBRARY_PATH": "/opt/tritonserver/lib",
                "XTCL_L3_SIZE": "16776192"
            }

    def suggest_flavours(self):
        """
        Suggest flavours
        """
        flavour_list = [{"name": "c4m16xpu1", "display_name": "CPU: 4核 内存: 16Gi XPU: 1卡"}]
        return flavour_list

    def suggest_flavour_tips(self):
        """
        Suggest flavour tips
        """
        if self.get_name in self.KUNLUN_COMMON:
            return "xpu"
        elif self.get_name in self.KUNLUN_SPECIAL:
            return "xpu"
        else:
            raise ValueError(f"Invalid accelerator name {self.name}")

    def suggest_model_server_parameters(self):
        """
        Suggest model server parameters
        """
        resource = {"accelerator": self.name,
                    "limits": {"cpu": "10", "mem": "10Gi"},
                    "requests": {"cpu": "100m", "mem": "50Mi"}}

        if self.get_name in self.KUNLUN_COMMON:
            resource["gpu"] = 7500
        elif self.get_name in self.KUNLUN_SPECIAL:
            resource["gpu"] = 1
        else:
            raise ValueError(f"Invalid accelerator name {self.name}")

        model_server_parameters = {
            "image": self.image,
            "env": self.env,
            "backend": self.args,
            "resource": resource}

        return model_server_parameters

    def suggest_resource_tips(self):
        """
        Suggest resource tips
        """
        if self.get_name == Accelerator.R480:
            return ["config.maxResources.scalarResources.baidu.com/xpu>1"]
        if self.get_name in self.KUNLUN_COMMON:
            return ["config.maxResources.scalarResources.baidu.com/xpu-mem>1"]
        elif self.get_name in self.KUNLUN_SPECIAL:
            return ["config.maxResources.scalarResources.kunlunxin.com/xpu>1"]
        else:
            raise ValueError(f"Invalid accelerator name {self.name}")


class AscendAccelerator(Accelerator):
    """
    Ascend Accelerator
    """

    def __init__(self, kind: str = None, name: str = "Atlas310"):
        """
        初始化一个Atlas310对象，可以指定kind和name。
            默认的kind是None，表示使用类型推导。
            默认的name是"Atlas310"。
        
        Args:
            kind (str, optional): 对象的类型，默认为None。如果不指定，则使用类型推导。
            name (str, optional): 对象的名称，默认为"Atlas310".
        
        Returns:
            None.
        """
        super().__init__(kind=kind, name=name)
        self.image = "iregistry.baidu-int.com/windmill-public/inference/ascend_arm64_model:v1.0.5"
        self.args = {}
        self.env = \
            {
                "LD_LIBRARY_PATH":
                    "/opt/tritonserver/lib",
                "PATH": "/opt/tritonserver/bin:/usr/local/mpi/bin:"
                        "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/ucx/bin"
            }

    def suggest_flavours(self):
        """
        Suggest flavours
        """
        flavour_list = [{"name": "c8m32npu1", "display_name": "CPU: 8核 内存: 32Gi NPU: 1卡"},
                        {"name": "c16m64npu2", "display_name": "CPU: 16核 内存: 64Gi NPU: 2卡"},
                        {"name": "c32m96npu4", "display_name": "CPU: 32核 内存: 96Gi NPU: 4卡"}]

        return flavour_list

    def suggest_flavour_tips(self):
        """
        Suggest flavour tips
        """
        return "npu"

    def suggest_model_server_parameters(self):
        """
        Suggest model server parameters
        """
        resource = {"accelerator": self.name,
                    "gpu": "75",
                    "limits": {"cpu": "10", "mem": "10Gi"},
                    "requests": {"cpu": "100m", "mem": "50Mi"}}
        model_server_parameters = {
            "image": self.image,
            "env": self.env,
            "args": self.args,
            "resource": resource}

        return model_server_parameters

    def suggest_resource_tips(self):
        """
        Suggest resource tips
        """
        # need modify later
        return ["config.maxResources.scalarResources.huawei.com/npu>1"]


def get_accelerator(name: str = None, kind: str = None) -> Accelerator:
    """
    Get accelerator.
    """
    if kind == Accelerator.NVIDIA:
        return NvidiaAccelerator(kind=kind, name=name)
    if kind == Accelerator.KUNLUN:
        return KunlunAccelerator(kind=kind, name=name)
    if kind == Accelerator.ASCEND:
        return AscendAccelerator(kind=kind, name=name)

    if name is None:
        return NvidiaAccelerator()

    if name in Accelerator.NVIDIA_COMMON + Accelerator.NVIDIA_SPECIAL:
        return NvidiaAccelerator(name=name)
    elif name in Accelerator.KUNLUN_COMMON + Accelerator.KUNLUN_SPECIAL:
        return KunlunAccelerator(name=name)
    elif name in Accelerator.ASCEND_COMMON + Accelerator.ASCEND_SPECIAL:
        return AscendAccelerator(name=name)
    else:
        raise Exception("Unsupported accelerator: {}".format(name))
