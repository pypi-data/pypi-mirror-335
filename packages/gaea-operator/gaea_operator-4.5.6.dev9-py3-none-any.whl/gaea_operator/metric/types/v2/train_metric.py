#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2025/3/13
# @Author  : yanxiaodong
# @File    : train_metric.py
"""
from enum import Enum


class MetricName(Enum):
    """
    Metric
    """
    loss = "Loss"

    token_accuracy = "TokenAccuracy"