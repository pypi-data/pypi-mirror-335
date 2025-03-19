#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2025/3/4
# @Author  : yanxiaodong
# @File    : train_args.py.py
"""
import os
from argparse import ArgumentParser


def parse_args():
    """
    Parse arguments.
    """
    parser = ArgumentParser()
    parser.add_argument("--windmill-ak", type=str, default=os.environ.get("WINDMILL_AK"))
    parser.add_argument("--windmill-sk", type=str, default=os.environ.get("WINDMILL_SK"))
    parser.add_argument("--org-id", type=str, default=os.environ.get("ORG_ID"))
    parser.add_argument("--user-id", type=str, default=os.environ.get("USER_ID"))
    parser.add_argument("--windmill-endpoint", type=str, default=os.environ.get("WINDMILL_ENDPOINT"))
    parser.add_argument("--project-name", type=str, default=os.environ.get("PROJECT_NAME"))
    parser.add_argument("--scene", type=str, default=os.environ.get("SCENE"))
    parser.add_argument("--public-model-store",
                        type=str,
                        default=os.environ.get("PUBLIC_MODEL_STORE", "workspaces/public/modelstores/default"))
    parser.add_argument("--tracking-uri", type=str, default=os.environ.get("TRACKING_URI"))
    parser.add_argument("--experiment-name", type=str, default=os.environ.get("EXPERIMENT_NAME"))
    parser.add_argument("--experiment-kind", type=str, default=os.environ.get("EXPERIMENT_KIND"))
    parser.add_argument("--train-dataset-name",
                        type=str,
                        default=os.environ.get("TRAIN_DATASET_NAME"))
    parser.add_argument("--val-dataset-name", type=str, default=os.environ.get("VAL_DATASET_NAME"))
    parser.add_argument("--base-train-dataset-name",
                        type=str,
                        default=os.environ.get("BASE_TRAIN_DATASET_NAME"))
    parser.add_argument("--base-val-dataset-name", type=str, default=os.environ.get("BASE_VAL_DATASET_NAME"))
    parser.add_argument("--model-name", type=str, default=os.environ.get("MODEL_NAME"))
    parser.add_argument("--model-display-name",
                        type=str,
                        default=os.environ.get("MODEL_DISPLAY_NAME"))
    parser.add_argument("--is-early-stopping",
                        type=str,
                        default=os.environ.get("IS_EARLY_STOPPING"))
    parser.add_argument("--early-stopping-patience",
                        type=str,
                        default=os.environ.get("EARLY_STOPPING_PATIENCE"))
    parser.add_argument("--advanced-parameters",
                        type=str,
                        default=os.environ.get("ADVANCED_PARAMETERS", "{}"))
    parser.add_argument("--accelerator", type=str, default=os.environ.get("ACCELERATOR"))

    parser.add_argument("--output-model-uri", type=str, default=os.environ.get("OUTPUT_MODEL_URI"))
    parser.add_argument("--output-uri", type=str, default=os.environ.get("OUTPUT_URI"))
    parser.add_argument("--image", type=str, default=os.environ.get("IMAGE"))
    parser.add_argument("--pdc-params", type=str, default=os.environ.get("PDC_PARAMS"))
    parser.add_argument("--is-pdc", type=str, default=os.environ.get("IS_PDC"))
    args, _ = parser.parse_known_args()

    return args