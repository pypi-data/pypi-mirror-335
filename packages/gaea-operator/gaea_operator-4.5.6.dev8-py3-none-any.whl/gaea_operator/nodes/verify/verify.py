#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File          : verify.py
@Author        : jiangwen04
@Date          : 2024/11/19
@Description   :
"""

import os
from argparse import ArgumentParser
import bcelogger
import json
import yaml

METRIC_FILES = ["metric.jsonl", "metric.json"]

PYTORCH_MODEL_FILES = {
    "best_model": ["best_model.pth", "config.py", "config.yaml"],
    "inference": ["best_model.pth", "config.py", "config.yaml", "preprocess.yaml"],
}

PADDLE_MODEL_FILE = {
    "best_model": ["best_model.pdstates", "best_model.pdparams"],
    "inference": ["inference.pdiparams", "inference.pdmodel", "preprocess.yaml"],
}


def parse_args():
    """
    Parse arguments.
    """
    parser = ArgumentParser()
    parser.add_argument("--output-model-path", type=str, default="")
    parser.add_argument("--output-metric-path", type=str, default="")
    args, _ = parser.parse_known_args()

    return args


def verify(args):
    """
    verify 模型产出
    """
    # 获取文件路径下内容
    path_dict = _get_dir_structure(args.output_model_path)
    metric_dict = _get_dir_structure(args.output_metric_path)
    bcelogger.info("verify start")
    bcelogger.info(f"model output path: {args.output_model_path}  path_dict: {path_dict}")
    # 获取best_model及inference目录
    best_model = path_dict.get('best_model', {})
    inference_path = path_dict.get('inference', {})
    # 校验ouput_model_uri下的文件
    for file_name in METRIC_FILES:
        if file_name not in metric_dict:
            bcelogger.error(f"{file_name} not found in metric_dict")
            exit(1)
    is_pytorch = True

    for file_name in best_model:
        if '.pdparams' in file_name:
            is_pytorch = False
    if is_pytorch:
        bcelogger.info("current frame pytorch")
        _validate_model_path(best_model, inference_path, PYTORCH_MODEL_FILES)
    else:
        bcelogger.info("current frame paddle")
        _validate_model_path(best_model, inference_path, PADDLE_MODEL_FILE)
    _validate_metric_json(args)
    _validate_metric_jsonl(args)
    _validate_preprocess(args)
    bcelogger.info("verify success")


def _validate_metric_json(args):
    with open(os.path.join(args.output_metric_path, "metric.json")) as f:
        metric = json.load(f)
        if metric['total_metric'] is None or len(metric['total_metric']) == 0:
            bcelogger.error("metric.json file total_metric is empty, but total_metric must be not empty")
            exit(1)
        if metric['tasks_metric'] is None or len(metric['tasks_metric']) == 0 or \
                len(metric['tasks_metric'][0]["metrics"]) == 0:
            bcelogger.error("metric.json file task_metric metrics is empty, but task_metric must be not empty")
            exit(1)


def _validate_metric_jsonl(args):
    with open(os.path.join(args.output_metric_path, "metric.jsonl")) as f:
        for line in f:
            metric = json.loads(line)
            if metric['total_metric'] is None or len(metric['total_metric']) == 0:
                bcelogger.error("total_metric is empty")
                exit(1)


def _validate_preprocess(args):
    with open(os.path.join(args.output_model_path, "inference/preprocess.yaml")) as f:
        yaml_data = yaml.load(f, Loader=yaml.Loader)
        transforms_list = yaml_data['Preprocess'][0]['transforms']
        normalize_exist = False
        resize_exist = False
        for data in transforms_list:
            if 'Normalize' in data:
                normalize_exist = True
            if 'Resize' not in data:
                resize_exist = True
        if normalize_exist is False or resize_exist is False:
            bcelogger.error("normalize or resize not exist")
            bcelogger.info(f"preprocess.yaml must contain "
                           f"Normalize Resize ,current not contain {'' if resize_exist else 'Resize'}"
                           f"  {'' if normalize_exist else 'Normalize Resize'}")
            exit(1)


def _validate_model_path(best_model, inference_path, model_file_config):
    for file_name in model_file_config['best_model']:
        if file_name not in best_model:
            bcelogger.error(f'{file_name} not found in best_model')
            bcelogger.info(f"best_model_dir must contain {model_file_config['best_model']}"
                           f" current dir contain {''.join(best_model.keys())}")
            raise FileNotFoundError(file_name)
    for file_name in model_file_config['inference']:
        if file_name not in inference_path:
            bcelogger.error(f'{file_name} not found in inference')
            bcelogger.info(f"inference_dir must contain {model_file_config['inference']}"
                           f" current dir contain {''.join(inference_path.keys())}")
            raise FileNotFoundError(file_name)


def _get_dir_structure(rootdir):
    dir_dict = {rootdir: {}}
    rootdir_len = len(rootdir)

    for path, dirs, files in os.walk(rootdir):
        # 获取当前目录相对于rootdir的子目录
        subdir = path[rootdir_len:].strip(os.path.sep)
        parent = dir_dict
        if subdir:
            for directory in subdir.split(os.path.sep):
                parent = parent[directory]
        for dir_name in dirs:
            parent[dir_name] = {}
        for file_name in files:
            parent[file_name] = None
    return dir_dict


if __name__ == "__main__":
    args = parse_args()
    verify(args=args)
