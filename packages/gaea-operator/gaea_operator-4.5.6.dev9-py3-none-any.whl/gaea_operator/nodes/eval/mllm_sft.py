#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2025/3/11
# @Author  : yanxiaodong
# @File    : mllm_sft.py.py
"""
import os
import json
import time
import base64
from swift.llm import run_deploy, DeployArguments

import bcelogger
from gaea_tracker import ExperimentTracker
from bcelogger.base_logger import setup_logger
from windmilltrainingv1.client.training_api_job import parse_job_name
from windmillclient.client.windmill_client import WindmillClient
from windmillartifactv1.client.artifact_api_artifact import parse_artifact_name
from windmilltrainingv1.client.training_api_dataset import parse_dataset_name
from windmillmodelv1.client.model_api_model import parse_model_name
from windmillendpointv1.client.evaluator.evaluator import evaluator

from ..download_artifact import download_artifact
from gaea_operator.dataset import MSSWIFTDataset
from gaea_operator.metric import update_metric_file
from gaea_operator.utils import write_file, is_base64
from gaea_operator.argument.eval_args import parse_args
from gaea_operator.metric import Metric
from gaea_operator.metric import InferenceMetricAnalysisV2 as InferenceMetricAnalysis


def mllm_sft_eval(args):
    """
    Eval component for mllm model.
    """
    windmill_client = WindmillClient(ak=args.windmill_ak,
                                     sk=args.windmill_sk,
                                     endpoint=args.windmill_endpoint,
                                     context={"OrgID": args.org_id, "UserID": args.user_id})
    tracker_client = ExperimentTracker(windmill_client=windmill_client,
                                       tracking_uri=args.tracking_uri,
                                       experiment_name=args.experiment_name,
                                       experiment_kind=args.experiment_kind,
                                       project_name=args.project_name)
    setup_logger(config=dict(file_name=os.path.join(args.output_uri, "worker.log")))

    # 1. 下载模型
    args.output_model_uri = "/home/windmill/tmp/model"
    output_model_uri, model_name = download_artifact(windmill_client=windmill_client,
                                                     input_uri=args.input_model_uri,
                                                     artifact_name=args.model_name,
                                                     output_uri=args.output_model_uri,
                                                     is_copy=False)

    # 2. 获取模型信息
    artifact = windmill_client.get_artifact(name=model_name)
    write_file(obj=json.loads(artifact.raw_data), output_dir=output_model_uri)
    model_object_name = artifact.objectName,

    artifact_name = parse_artifact_name(name=model_name)
    object_name = artifact_name.object_name
    model = windmill_client.get_model(workspace_id=parse_model_name(name=object_name).workspace_id,
                                      model_store_name=parse_model_name(name=object_name).model_store_name,
                                      local_name=parse_model_name(name=object_name).local_name)
    prefer_model_server_kind = model.preferModelServerKind
    category = model.category["category"]
    bcelogger.info(f"Get model {model_name} prefer model server kind: {prefer_model_server_kind}")

    # 3. 合并分片数据集
    dataset_name = args.dataset_name
    output_dataset_uri = args.output_dataset_uri
    ms_swift_dataset = MSSWIFTDataset(windmill_client=windmill_client, work_dir=tracker_client.work_dir)
    ms_swift_dataset.concat_dataset(dataset_name=dataset_name,
                                    output_dir=output_dataset_uri,
                                    usage=MSSWIFTDataset.usages[1])
    annotation_filepath = \
        ms_swift_dataset.get_annotation_filepath(output_dataset_dir=output_dataset_uri, usages=MSSWIFTDataset.usages[1])

    # 4. 获取数据集信息
    artifact = windmill_client.get_artifact(name=dataset_name)
    instructions = artifact.metadata["instructions"]
    bcelogger.info(f"Get dataset {dataset_name} instructions: {instructions}")

    artifact_name = parse_artifact_name(name=dataset_name)
    object_name = artifact_name.object_name
    dataset = windmill_client.get_dataset(workspace_id=parse_dataset_name(name=object_name).workspace_id,
                                          project_name=parse_dataset_name(name=object_name).project_name,
                                          local_name=parse_dataset_name(name=object_name).local_name)
    annotation_format = dataset.annotationFormat
    bcelogger.info(f"Get dataset {dataset_name} annotation format: {annotation_format}")

    # 5. 评估metric初始化
    metric_analysis = InferenceMetricAnalysis(instructions=instructions)
    metric = Metric([metric_analysis], dataset_name=dataset_name)

    # 6. 解析advanced_parameters
    if is_base64(args.advanced_parameters):
        advanced_parameters = json.loads(base64.b64decode(args.advanced_parameters))
    else:
        advanced_parameters = json.loads(args.advanced_parameters)
    infer_config = \
        {
            "top_p": advanced_parameters["nucleusSampler"],
            "temperature": advanced_parameters["temperature"],
            "repetition_penalty": advanced_parameters["repetitionPenalty"]
        }

    # 6. 部署模型与评估
    with run_deploy(DeployArguments(model=output_model_uri, verbose=False)) as port:
        evaluator(endpoint=f"http://127.0.0.1:{port}",
                  dataset_uri=annotation_filepath,
                  annotation_format=annotation_format,
                  category=category,
                  model_name="model",
                  prefer_model_server_kind=prefer_model_server_kind,
                  output_uri=tracker_client.job_work_dir,
                  metric=metric,
                  infer_config=infer_config)

    # 7. 更新指标文件
    update_metric_file(windmill_client=windmill_client,
                       tracker_client=tracker_client,
                       dataset_name=dataset_name,
                       model_object_name=model_object_name,
                       model_artifact_name=model_name)

    # 8. 更新job tags
    job_name = parse_job_name(tracker_client.job_name)
    job = windmill_client.get_job(workspace_id=job_name.workspace_id,
                                  project_name=job_name.project_name,
                                  local_name=job_name.local_name)
    tags = job.tags if job.tags is not None else {}
    tags.update({"artifactName": model.name, "datasetName": dataset_name})
    bcelogger.info(f"Get job {tracker_client.job_name} tags: {tags}")
    for _ in range(5):
        windmill_client.update_job(workspace_id=job_name.workspace_id,
                                   project_name=job_name.project_name,
                                   local_name=job_name.local_name,
                                   tags=tags)
        job = windmill_client.get_job(workspace_id=job_name.workspace_id,
                                      project_name=job_name.project_name,
                                      local_name=job_name.local_name)
        update_tags = job.tags if job.tags is not None else {}
        bcelogger.info(f"Update job {tracker_client.job_name} tags: {update_tags}")
        if "artifactName" in update_tags:
            break
        time.sleep(3)
    bcelogger.info(f"Update job {tracker_client.job_name} tags: {tags}")


if __name__ == "__main__":
    args = parse_args()
    mllm_sft_eval(args=args)
