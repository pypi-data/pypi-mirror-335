#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
__init__.py
"""
from gaea_operator.pipelines.ocrnet_pipeline.pipeline import pipeline as ocrnet_pipeline
from gaea_operator.pipelines.ppyoloe_plus_pipeline.pipeline import pipeline as ppyoloe_plus_pipeline
from gaea_operator.pipelines.resnet_pipeline.pipeline import pipeline as resnet_pipeline
from gaea_operator.pipelines.change_ppyoloe_plus_pipeline.pipeline import pipeline as change_ppyoloe_plus_pipeline
from gaea_operator.pipelines.change_ocrnet_pipeline.pipeline import pipeline as change_ocrnet_pipeline
from gaea_operator.pipelines.codetr_pipeline.pipeline import pipeline as codetr_pipeline
from gaea_operator.pipelines.dbnet_pipeline.pipeline import pipeline as dbnet_pipeline
from gaea_operator.pipelines.svtr_lcnet_pipeline.pipeline import pipeline as svtr_lcnet_pipeline
from gaea_operator.pipelines.cvresnet_pipeline.pipeline import pipeline as cvresnet_pipeline
from gaea_operator.pipelines.yoloseg_pipeline.pipeline import pipeline as yoloseg_pipeline
from gaea_operator.pipelines.mllm_sft_pipeline.pipeline import pipeline as mllm_sft_pipeline
from gaea_operator.pipelines.mllm_lora_pipeline.pipeline import pipeline as mllm_lora_pipeline

v2_ppls = {
    "mask_former": "v2/mask_former",
}

ppls = {
    "ocrnet": ocrnet_pipeline,
    "ppyoloe_plus": ppyoloe_plus_pipeline,
    "resnet": resnet_pipeline,
    "change_ppyoloe_plus": change_ppyoloe_plus_pipeline,
    "change_ocrnet": change_ocrnet_pipeline,
    "codetr": codetr_pipeline,
    "svtr_lcnet": svtr_lcnet_pipeline,
    "dbnet": dbnet_pipeline,
    "cvresnet": cvresnet_pipeline,
    "yoloseg": yoloseg_pipeline,
    "mllm_sft": mllm_sft_pipeline,
    "mllm_lora": mllm_lora_pipeline,
}

name_to_display_name = {
    "ocrnet": "通用语义分割模型",
    "ppyoloe_plus": "通用目标检测模型",
    "resnet": "轻量级分类模型",
    "change_ppyoloe_plus": "通用变化检测模型",
    "change_ocrnet": "通用变化分割模型",
    "codetr": "高精度目标检测模型",
    "svtr_lcnet": "文字识别模型",
    "dbnet": "文字检测模型",
    "cvresnet": "图像分类多任务模型",
    "yoloseg": "实例分割模型",
    "mask_former": "高精度语义分割模型",
    "mllm_sft": "多模态大模型精调-全量更新",
    "mllm_lora": "多模态大模型精调-LoRA"
}

name_to_local_name = {
    "ocrnet": "SemanticSegmentation",
    "ppyoloe_plus": "ObjectDetection",
    "resnet": "LightClassification",
    "change_ppyoloe_plus": "ChangeObjectDetection",
    "change_ocrnet": "ChangeSemanticSegmentation",
    "codetr": "HighPrecisionObjectDetection",
    "svtr_lcnet": "OCR",
    "dbnet": "TextDetection",
    "cvresnet": "MultiTaskClassification",
    "yoloseg": "InstanceSegmentation",
    "mask_former": "HighPrecisionSemanticSegmentation",
    "mllm_sft": "Multimodal-SFT",
    "mllm_lora": "Multimodal-LoRA"
}

name_to_category = {
    "ocrnet": "Image/SemanticSegmentation",
    "ppyoloe_plus": "Image/ObjectDetection",
    "resnet": "Image/ImageClassification/OneClass",
    "codetr": "Image/ObjectDetection",
    "svtr_lcnet": "Image/OCR",
    "dbnet": "Image/TextDetection",
    "cvresnet": "Image/ImageClassification/MultiTask",
    "yoloseg": "Image/InstanceSegmentation",
    "mask_former": "Image/SemanticSegmentation",
    "mllm_sft": "Multimodal/VQA",
    "mllm_lora": "Multimodal/VQA"
}

name_to_description = {
    "ocrnet": "",
    "ppyoloe_plus": "",
    "resnet": "",
    "codetr": "",
    "svtr_lcnet": "",
    "dbnet": "",
    "cvresnet": "",
    "yoloseg": "",
    "mask_former": "",
    "mllm_sft": "训练时会更新模型全部参数，在复杂任务上会有更好效果",
    "mllm_lora": "训练时只更新部分参数，需要的计算资源更少，速度更快"
}

base_pipeline = ["ocrnet", "ppyoloe_plus", "resnet", "svtr_lcnet", "yoloseg"]
