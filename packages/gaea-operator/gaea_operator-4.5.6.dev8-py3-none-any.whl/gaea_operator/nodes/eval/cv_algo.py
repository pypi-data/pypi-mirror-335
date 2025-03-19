#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/2/23
# @Author  : yanxiaodong
# @File    : eval_component.py
"""
import os
import json

from argparse import ArgumentParser

from gaea_tracker import ExperimentTracker
from bcelogger.base_logger import setup_logger
from windmilltrainingv1.client.training_api_job import parse_job_name
from windmillclient.client.windmill_client import WindmillClient

from gaea_operator.nodes.download_artifact import download_artifact
from windmillartifactv1.client.artifact_api_artifact import parse_artifact_name

from gaea_operator.metric.metric_v2 import update_metric_file
from gaea_operator.utils import write_file, get_accelerator
from v2x_model_standardization import standardize_model_api
import bcelogger
from windmilltrainingv1.client.training_api_dataset import \
    parse_dataset_name, \
    ANNOTATION_FORMAT_COCO, \
    ANNOTATION_FORMAT_IMAGENET, \
    ANNOTATION_FORMAT_CITYSCAPES, \
    ANNOTATION_FORMAT_PADDLECLAS, \
    ANNOTATION_FORMAT_PADDLEOCR, \
    ANNOTATION_FORMAT_PADDLESEG
from gaea_operator.dataset import CocoDataset, ImageNetDataset, MultiAttributeDataset, CityscapesDataset, PPOCRDataset


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
    parser.add_argument("--tracking-uri", type=str, default=os.environ.get("TRACKING_URI"))
    parser.add_argument("--experiment-name", type=str, default=os.environ.get("EXPERIMENT_NAME"))
    parser.add_argument("--experiment-kind", type=str, default=os.environ.get("EXPERIMENT_KIND"))
    parser.add_argument("--dataset-name", type=str, default=os.environ.get("DATASET_NAME"))
    parser.add_argument("--model-name", type=str, default=os.environ.get("MODEL_NAME"))

    parser.add_argument("--input-model-uri", type=str, default=os.environ.get("INPUT_MODEL_URI"))
    parser.add_argument("--output-dataset-uri", type=str, default=os.environ.get("OUTPUT_DATASET_URI"))
    parser.add_argument("--output-model-uri", type=str, default=os.environ.get("OUTPUT_MODEL_URI"))
    parser.add_argument("--output-uri", type=str, default=os.environ.get("OUTPUT_URI"))
    parser.add_argument("--accelerator", type=str,
                        default=os.environ.get("ACCELERATOR", 'A100'))
    args, _ = parser.parse_known_args()

    return args


def cv_algo_eval(args):
    """
    Eval component for ocrnet model.
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
    output_model_uri, model_name = download_artifact(windmill_client=windmill_client,
                                                     input_uri=args.input_model_uri,
                                                     artifact_name=args.model_name,
                                                     output_uri=args.output_model_uri,
                                                     is_copy=True)

    # 2. 获取模型信息
    response = windmill_client.get_artifact(name=model_name)
    raw_data = json.loads(response.raw_data)
    write_file(obj=raw_data, output_dir=output_model_uri)
    metadata = raw_data['metadata']

    # 3. 合并分片数据集
    artifact_name = parse_artifact_name(name=args.dataset_name)
    object_name = artifact_name.object_name
    dataset = parse_dataset_name(name=object_name)
    response = windmill_client.get_dataset(workspace_id=dataset.workspace_id,
                                           project_name=dataset.project_name,
                                           local_name=dataset.local_name)
    bcelogger.info(f"Get dataset {args.dataset_name} response is {response}")
    if response.annotationFormat == ANNOTATION_FORMAT_COCO:
        dataset_class = CocoDataset
    elif response.annotationFormat in [ANNOTATION_FORMAT_IMAGENET, ANNOTATION_FORMAT_PADDLECLAS]:
        dataset_class = ImageNetDataset
    elif response.annotationFormat in [ANNOTATION_FORMAT_CITYSCAPES, ANNOTATION_FORMAT_PADDLESEG]:
        dataset_class = CityscapesDataset
    elif response.annotationFormat == ANNOTATION_FORMAT_PADDLEOCR:
        dataset_class = PPOCRDataset
    elif response.annotationFormat == "MultiAttributeDataset":
        dataset_class = MultiAttributeDataset
    else:
        raise ValueError(f'Unsupported annoation format{response.annotationFormat}.')
    bcelogger.info(f"Download dataset {args.dataset_name}")
    dataset = dataset_class(windmill_client=windmill_client, work_dir=tracker_client.work_dir)

    dataset.concat_dataset(dataset_name=args.dataset_name,
                           output_dir=args.output_dataset_uri,
                           usage=dataset.usages[1],
                           save_label=True)

    # 4. 开始评估
    eval_config = _generate_eval_config(args, output_model_uri, tracker_client.job_work_dir, metadata, dataset)
    eval = standardize_model_api.ModelEvaluator()
    eval.set_parameter(eval_config)
    ret = eval.run()
    if not ret:
        bcelogger.error('eval fail.')
        exit(-1)
    else:
        bcelogger.info('eval success')

    # 5. 更新指标文件
    update_metric_file(windmill_client=windmill_client,
                       tracker_client=tracker_client,
                       dataset_name=args.dataset_name,
                       model_object_name=response.objectName,
                       model_artifact_name=response.name)

    # 6. 更新job tags
    tags = {"artifactName": response.name, "datasetName": args.dataset_name}
    job_name = parse_job_name(tracker_client.job_name)
    workspace_id, project_name, local_name = job_name.workspace_id, job_name.project_name, job_name.local_name
    bcelogger.info(f"Start update job {local_name} with tags {tags}")
    windmill_client.update_job(workspace_id=workspace_id, project_name=project_name, local_name=local_name, tags=tags)
    bcelogger.info(f"Update job {local_name} with tags {tags} success")


# TODO 生成cv_algo配置待优秀
def _generate_eval_config(args, output_model_uri, output_metric_uri, metadata, dataset):
    eval_config = {}

    eval_config['device_type'] = (get_accelerator(args.accelerator).get_kind.lower() + "-"
                                   + get_accelerator(args.accelerator).get_name.lower())
    eval_config['model_type'] = \
        f'{metadata["algorithmParameters"]["networkArchitecture"]}'
    eval_config['output_model_path'] = output_model_uri
    eval_config['output_log_path'] = args.output_uri
    eval_config['output_metric_path'] = [output_metric_uri]

    eval_config['data_load'] = {}
    usages = dataset.usages
    eval_config['data_load']["eval"] = [
        {"image_dir": "",
         "anno_path": [dataset.get_annotation_filepath(args.output_dataset_uri, usages[1])],
         "dataset_dir": "/",
         "sample_prob": 1.0,
         "label_description": ""
         }
    ]
    return eval_config


if __name__ == "__main__":
    args = parse_args()
    cv_algo_eval(args=args)
