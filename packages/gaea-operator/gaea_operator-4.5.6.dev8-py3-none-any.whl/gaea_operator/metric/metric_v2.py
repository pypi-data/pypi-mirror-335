#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/7
# @Author  : jiangwen04
# @File    : metric_v2.py
"""
from typing import Dict

import bcelogger
from gaea_tracker import ExperimentTracker
from windmillclient.client.windmill_client import WindmillClient
from windmilltrainingv1.client.training_api_project import parse_project_name

from gaea_operator.utils import read_file, format_time, write_file, DEFAULT_METRIC_FILE_NAME
from .types.metric import BaseMetric


def update_metric_file_with_dataset(dataset_name: str, input_dir: str, file_name: str, output_dir: str):
    """
    Update metric file with dataset.
    """
    base_metric = BaseMetric(datasetName=dataset_name, updatedAt=format_time())
    metric_data = read_file(input_dir=input_dir, file_name=file_name)["tasks_metric"][0]
    metric_data.update(base_metric.dict())
    write_file(obj=metric_data, output_dir=input_dir, file_name=file_name)
    write_file(obj=metric_data, output_dir=output_dir, file_name=file_name)


def get_score_from_metric_raw(metric_data: Dict, metric_name: str):
    """
    Get metric name score from raw.
    """
    for metric in metric_data:
        # TODO 暂时如此之后更改
        if metric["name"].lower() == metric_name.lower():
            if isinstance(metric["result"], Dict):
                return list(metric["result"].values())[0]
            return metric["result"]


def update_metric_file(windmill_client: WindmillClient,
                       tracker_client: ExperimentTracker,
                       dataset_name: str,
                       model_object_name: str,
                       model_artifact_name: str):
    """
    Update metric file.
    """
    bcelogger.info(f"Model artifact name is {model_artifact_name}")
    base_metric = BaseMetric(artifactName=model_artifact_name,
                             datasetName=dataset_name,
                             updatedAt=format_time(),
                             baselineJobName=tracker_client.job_name)

    try:
        response = windmill_client.get_artifact(object_name=model_object_name, version="best")
        bcelogger.info(f"Get best artifact name {model_object_name} response {response}")
        if response.name != model_artifact_name:
            bcelogger.info(f"Get baseline model name {response.name}")
            baseline_model_name = response.name
            tags = [{"artifactName": baseline_model_name}, {"datasetName": dataset_name}]
            project_name = parse_project_name(tracker_client.project_name)
            response = windmill_client.list_job(workspace_id=project_name.workspace_id,
                                                project_name=project_name.local_name,
                                                tags=tags)
            if len(response.result) > 0:
                base_metric.baselineJobName = response.result[0]["name"]
            bcelogger.info(f"Base metric dict is {base_metric.dict()}")
    except Exception as e:
        bcelogger.error(f"Get best artifact name {model_object_name} error {e}")

    metric_dir = tracker_client.job_work_dir
    metric_data = read_file(input_dir=metric_dir, file_name=DEFAULT_METRIC_FILE_NAME)
    metric_data = metric_data['tasks_metric'][0]
    metric_data.update(base_metric.dict())
    write_file(obj=metric_data, output_dir=metric_dir, file_name=DEFAULT_METRIC_FILE_NAME)
