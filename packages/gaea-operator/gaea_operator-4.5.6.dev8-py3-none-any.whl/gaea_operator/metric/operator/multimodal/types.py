#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2025/3/11
# @Author  : yanxiaodong
# @File    : types.py
"""
from enum import Enum


class InstructionKind(Enum):
    """
    InstructionKind enum class
    """
    image_recognition = "ImageRecognition"
    object_detection = "ObjectDetection"