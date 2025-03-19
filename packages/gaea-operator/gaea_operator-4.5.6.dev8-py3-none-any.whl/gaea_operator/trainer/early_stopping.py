#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2025/2/8
# @Author  : jiangwen04
# @File    : early_stopping.py
"""

import numbers
import numpy as np
import bcelogger


class EarlyStopping:
    """Stop training when the given monitor stopped improving during evaluation
    by setting `model.stop_training=True`.

    Args:
        monitor(str): Quantity to be monitored. Default: 'loss'.
        mode(str|None): Mode should be one of 'auto', 'min' or 'max'. In 'min'
            mode, training will stop until monitored quantity stops decreasing.
            In 'max' mode, training will stop until monitored quantity stops
            increasing. In 'auto' mode, exact mode can be inferred by the name
            of monitor. If 'acc' in monitor, the mode will be considered as
            'max', otherwise the mode will be set to 'min'. Default: 'auto'.
        patience(int): Number of epochs with no improvement after which
            training will be stopped. Default: 0.
        min_delta(int|float): The minimum change of monitored quantity. If
            the change is less than min_delta, model could be considered as no
            improvement. Default: 0.

    """

    def __init__(
            self,
            monitor='accuracy',
            patience=0,
            min_delta=0
    ):
        super().__init__()
        self.stop_training = False
        self.monitor = monitor
        self.patience = patience
        self.min_delta = abs(min_delta)
        self.wait_epoch = 0
        self.monitor_op = np.greater
        if self.monitor_op == np.greater:
            self.min_delta *= 1
        else:
            self.min_delta *= -1

    def train_begin(self, logs=None):
        """
        train begin
        """
        self.wait_epoch = 0
        self.best_value = np.inf if self.monitor_op == np.less else -np.inf

    def eval_end(self, logs=None):
        """
        eval end
        """
        if logs is None or self.monitor not in logs:
            bcelogger.info(
                'Monitor of EarlyStopping should be loss or metric name.'
            )
            return
        bcelogger.info(f"log:{logs}, monitor:{logs[self.monitor]}, best_value:{self.best_value}")
        current = logs[self.monitor]
        if isinstance(current, (list, tuple, np.ndarray)):
            current = current[0]
        elif isinstance(current, numbers.Number):
            current = current
        else:
            return

        if self.monitor_op(current - self.min_delta, self.best_value):
            self.best_value = current
            self.wait_epoch = 0
        else:
            self.wait_epoch += 1
        if self.wait_epoch >= self.patience:
            self.stop_training = True
