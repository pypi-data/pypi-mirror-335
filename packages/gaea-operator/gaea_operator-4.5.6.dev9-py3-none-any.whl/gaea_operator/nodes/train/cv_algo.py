#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/2/23
# @Author  : yanxiaodong
# @File    : classify.py
"""
import copy
import os
import json
from argparse import ArgumentParser
import base64
import threading
import time
import re

from gaea_tracker import ExperimentTracker
from bcelogger.base_logger import setup_logger
from windmillmodelv1.client.model_api_model import parse_model_name
from windmillmodelv1.client.model_api_modelstore import parse_modelstore_name
from windmillclient.client.windmill_client import WindmillClient
import bcelogger
from windmillmodelv1.client.model_api_model import ModelMetadata, InputSize
from windmillartifactv1.client.artifact_api_artifact import parse_artifact_name
from v2x_model_standardization import standardize_model_api
from windmilltrainingv1.client.training_api_dataset import \
    parse_dataset_name, \
    ANNOTATION_FORMAT_COCO, \
    ANNOTATION_FORMAT_IMAGENET, \
    ANNOTATION_FORMAT_CITYSCAPES, \
    ANNOTATION_FORMAT_PADDLECLAS, \
    ANNOTATION_FORMAT_PADDLEOCR, \
    ANNOTATION_FORMAT_PADDLESEG

from gaea_operator.config import KEY_NETWORK_ARCHITECTURE
from gaea_operator.metric.metric_v2 import get_score_from_metric_raw, update_metric_file_with_dataset
from gaea_operator.model import Model
from gaea_operator.metric import get_score_from_file
from gaea_operator.utils import write_file, is_base64, ModelTemplate, read_file_jsonl, read_yaml_file, get_accelerator
from gaea_operator.utils.cv_algo_config import ALGORITH_TO_METRIC, ALGORITH_TO_METRICS
from gaea_operator.metric.types.metric import LOSS_METRIC_NAME
from gaea_operator.dataset import CocoDataset, ImageNetDataset, MultiAttributeDataset, CityscapesDataset, PPOCRDataset

training_exit_flag = False


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
    parser.add_argument("--train-dataset-name", type=str, default=os.environ.get("TRAIN_DATASET_NAME"))
    parser.add_argument("--val-dataset-name", type=str, default=os.environ.get("VAL_DATASET_NAME"))
    parser.add_argument("--base-train-dataset-name",
                        type=str,
                        default=os.environ.get("BASE_TRAIN_DATASET_NAME"))
    parser.add_argument("--base-val-dataset-name", type=str, default=os.environ.get("BASE_VAL_DATASET_NAME"))
    parser.add_argument("--model-name", type=str, default=os.environ.get("MODEL_NAME"))
    parser.add_argument("--model-display-name", type=str, default=os.environ.get("MODEL_DISPLAY_NAME"))
    parser.add_argument("--advanced-parameters", type=str, default=os.environ.get("ADVANCED_PARAMETERS", "{}"))

    parser.add_argument("--output-model-uri", type=str, default=os.environ.get("OUTPUT_MODEL_URI"))
    parser.add_argument("--output-uri", type=str, default=os.environ.get("OUTPUT_URI"))
    parser.add_argument("--algorithm", type=str, default=os.environ.get("ALGORITHM", ModelTemplate.MASKFORMER_NAME))
    parser.add_argument("--model-formats", type=str,
                        default=os.environ.get("MODEL_FORMATS", '["PaddlePaddle"]'))
    parser.add_argument("--accelerator", type=str,
                        default=os.environ.get("ACCELERATOR", "A100"))
    args, _ = parser.parse_known_args()

    bcelogger.info(f"Get args: {args}")

    return args


def train(args):
    """
    Train component for classify model.
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

    dataset_uri = "/home/windmill/tmp/dataset"
    artifact_name = parse_artifact_name(name=args.train_dataset_name)
    object_name = artifact_name.object_name
    dataset = parse_dataset_name(name=object_name)
    response = windmill_client.get_dataset(workspace_id=dataset.workspace_id,
                                           project_name=dataset.project_name,
                                           local_name=dataset.local_name)
    bcelogger.info(f"Get dataset {args.train_dataset_name} response is {response}")
    category = response.category['category']
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
    bcelogger.info(f"Download dataset {args.train_dataset_name}")
    dataset = dataset_class(windmill_client=windmill_client, work_dir=tracker_client.work_dir)

    if args.scene is not None and len(args.scene) > 0:
        bcelogger.info(f"Scene: {args.scene}")
        tags = [{"scene": args.scene}]
        response = windmill_client.list_model(workspace_id=parse_modelstore_name(args.public_model_store).workspace_id,
                                              model_store_name=parse_modelstore_name(
                                                  args.public_model_store).local_name,
                                              tags=tags)
        if len(response.result) == 0:
            bcelogger.warning(f"No model found with tags: {tags}")
        for model in response.result:
            model_name = model["name"]
            bcelogger.info(f"Model: {model_name}")
            if "baseDatasetName" in model["artifact"]["tags"]:
                args.base_train_dataset_name = model["artifact"]["tags"]["baseDatasetName"]
                args.base_val_dataset_name = model["artifact"]["tags"]["baseDatasetName"]
    # 1. 合并train分片数据集
    dataset.concat_dataset(dataset_name=args.train_dataset_name,
                           base_dataset_name=args.base_train_dataset_name,
                           output_dir=dataset_uri,
                           usage=dataset.usages[0])

    # 2. 合并val分片数据集
    dataset.concat_dataset(dataset_name=args.val_dataset_name,
                           base_dataset_name=args.base_val_dataset_name,
                           output_dir=dataset_uri,
                           usage=dataset.usages[1])
    # 兼容json串传入
    if is_base64(args.advanced_parameters):
        train_advanced_parameters = json.loads(base64.b64decode(args.advanced_parameters))
    else:
        train_advanced_parameters = json.loads(args.advanced_parameters)
    model_template = ModelTemplate(algorithm=args.algorithm)
    train_advanced_parameters[KEY_NETWORK_ARCHITECTURE] = \
        model_template.suggest_network_architecture_v2(train_advanced_parameters[KEY_NETWORK_ARCHITECTURE])
    bcelogger.info(f"Advanced parameters: {train_advanced_parameters}")

    # 只用来记录日志
    track_model_score(ALGORITH_TO_METRICS[args.algorithm], os.path.join(args.output_model_uri, 'metric.jsonl'),
                      tracker_client)

    try:
        train_config = _generate_train_config(args, train_advanced_parameters, dataset, dataset_uri)
        train = standardize_model_api.Trainer()
        train.set_parameter(train_config)
        ret = train.run()
        if not ret:
            bcelogger.error('train fail.')
            exit(-1)
        else:
            bcelogger.info('train & export success')

        eval_parameter = copy.deepcopy(train_config)

        bcelogger.info('begin eval ...')
        evaluator = standardize_model_api.ModelEvaluator()
        evaluator.set_parameter(eval_parameter)
        ret = evaluator.run()
        if not ret:
            bcelogger.error('eval fail.')
            exit(-1)
        else:
            bcelogger.info('eval success')
    except  Exception as e:
        bcelogger.error(f"train or eval fail {e}")
        exit(-1)
    finally:
        global training_exit_flag
        training_exit_flag = True

    # 7. 创建模型
    update_metric_file_with_dataset(dataset_name=args.train_dataset_name,
                                    input_dir=args.output_model_uri,
                                    file_name="metric.json", output_dir=tracker_client.job_work_dir)
    # TODO best metric 指标暂时采用该方式，之后进行修改
    metric_name = ALGORITH_TO_METRIC[args.algorithm]
    current_score = get_score_from_file(filepath=os.path.join(args.output_model_uri, "metric.json"),
                                        metric_name=metric_name)
    best_score, version = Model(windmill_client=windmill_client).get_best_model_score(
        model_name=args.model_name, metric_name=metric_name)
    tags = {metric_name: str(current_score)}
    alias = None
    if current_score >= best_score and version is not None:
        alias = ["best"]
        bcelogger.info(
            f"{metric_name.capitalize()} current score {current_score} >= {best_score}, update [best]")
        tags.update(
            {f"bestReason": f"current.score({current_score}) greater than {version}.score({best_score})"})
    if version is None:
        alias = ["best"]
        bcelogger.info(f"First alias [best] score: {current_score}")
        tags.update({f"bestReason": f"current.score({current_score})"})

    meta_data = _model_metadata(args, train_advanced_parameters, tracker_client, dataset.labels)

    model_name = parse_model_name(args.model_name)
    workspace_id = model_name.workspace_id
    model_store_name = model_name.model_store_name
    local_name = model_name.local_name
    response = windmill_client.create_model(workspace_id=workspace_id,
                                            model_store_name=model_store_name,
                                            local_name=local_name,
                                            display_name=args.model_display_name,
                                            category=category,
                                            model_formats=json.loads(args.model_formats),
                                            artifact_alias=alias,
                                            artifact_tags=tags,
                                            artifact_metadata=meta_data,
                                            artifact_uri=args.output_model_uri)

    bcelogger.info(f"Model {args.model_name} created response: {response}")

    # 7. 输出文件
    write_file(obj=json.loads(response.raw_data)["artifact"], output_dir=args.output_model_uri)


def _model_metadata(args, train_advanced_parameters, tracker_client, labels):
    """
    create metadata
    """
    meta_data = ModelMetadata(experimentName=tracker_client.experiment_name,
                              jobName=tracker_client.job_name,
                              jobDisplayName=tracker_client.job_display_name,
                              algorithmParameters={},
                              experimentRunID=tracker_client.run_id)
    meta_data.labels = labels

    yaml_data = read_yaml_file(args.output_model_uri + "/inference/", "preprocess.yaml")
    transforms_list = yaml_data['Preprocess'][0]['transforms']
    for data in transforms_list:
        if 'Normalize' in data:
            normalize = data['Normalize']
            normalize_dict = {}
            for key, value in normalize.items():
                if isinstance(value, (int, float, str, bool)):
                    normalize_dict[key] = value
                else:
                    normalize_dict[key] = json.dumps(value)
            meta_data.algorithmParameters.update(normalize_dict)
        if 'Resize' in data:
            resize_data = data['Resize']['target_size']
            input_size = InputSize(width=resize_data[0],
                                   height=resize_data[1])
            meta_data.inputSize = input_size

    meta_data.algorithmParameters[KEY_NETWORK_ARCHITECTURE] = train_advanced_parameters[KEY_NETWORK_ARCHITECTURE]
    return meta_data.dict()


# TODO 生成cv_algo配置待优秀
def _generate_train_config(args, train_advanced_parameters, dataset, dataset_uri):

    train_config = copy.deepcopy(train_advanced_parameters)
    train_config = _nested_dict(train_config)
    # TODO 自动根据参数生成
    train_config['learning_rate'] = float(train_config["lr_scheduler.learning_rate"])

    train_config['device_type'] = (get_accelerator(args.accelerator).get_kind.lower() + "-"
                                   + get_accelerator(args.accelerator).get_name.lower())
    train_config['model_type'] = \
        f'{train_advanced_parameters[KEY_NETWORK_ARCHITECTURE]}'
    train_config['output_model_path'] = args.output_model_uri
    train_config['output_log_path'] = args.output_uri
    train_config['output_metric_path'] = [args.output_model_uri]

    train_config['data_load'] = {}
    if 'eval_height' in train_config and 'eval_width' in train_config:
        input_size = [train_config['eval_width'], train_config['eval_height']]
        train_config['input_size'] = input_size
    usages = dataset.usages
    train_config['data_load']["train"] = [
        {"image_dir": "",
         "anno_path": [dataset.get_annotation_filepath(dataset_uri, usages[0])],
         "dataset_dir": "/",
         "sample_prob": 1.0,
         "label_description": ""
         }
    ]
    train_config['data_load']["eval"] = [
        {"image_dir": "",
         "anno_path": [dataset.get_annotation_filepath(dataset_uri, usages[1])],
         "dataset_dir": "/",
         "sample_prob": 1.0,
         "label_description": ""
         }
    ]
    return train_config

def _nested_dict(input_dict):
    new_dict = {}
    for key, value in input_dict.items():
        value = _convert_str(value)
        if '.' in key:
            sub_keys = key.split('.')
            temp_dict = new_dict
            for sub_key in sub_keys[:-1]:
                if sub_key not in temp_dict:
                    temp_dict[sub_key] = {}
                temp_dict = temp_dict[sub_key]
            temp_dict[sub_keys[-1]] = value
        new_dict[key] = value
    return new_dict

def _convert_str(s):
    if re.match(r'^-?\d+$', s):  # 匹配整数
        return int(s)
    elif re.match(r'^-?\d+\.\d+$', s) or re.match(r'^-?\d+e-?\d+$', s):  # 匹配浮点数
        return float(s)
    else:
        return s
def track_model_score(metric_names, metric_filepath, tracker_client):
    """
    Track the score of model.
    """
    thread = threading.Thread(target=_track_thread, args=(metric_names, metric_filepath, tracker_client))
    thread.start()


def _track_thread(metric_names, metric_filepath, tracker_client):
    bcelogger.info(f"Track metric {metric_filepath} ")
    last_epoch, last_step = -1, -1
    while True:
        if training_exit_flag:
            bcelogger.info(f"Training exit flag is True, stop tracking. last_epoch {last_epoch}, last_step {last_step}")
            _, _ = _track_metric_by_file(metric_filepath, metric_names, last_epoch, last_step, tracker_client)
            break
        last_epoch, last_step = _track_metric_by_file(metric_filepath,
                                                      metric_names, last_epoch, last_step, tracker_client)
        time.sleep(10)


def _track_metric_by_file(filepath, metric_names, last_epoch, last_step, tracker_client):
    """
    track metric jsonl
    """

    if os.path.exists(filepath):
        try:
            metric_data_list = read_file_jsonl(input_dir=os.path.dirname(filepath),
                                               file_name=os.path.basename(filepath))

            for data in metric_data_list:
                metric_data = data['total_metric']
                metric_data = metric_data + data['tasks_metric'][0]['metrics'] \
                    if data['tasks_metric'][0]['metrics'] is not None else metric_data
                epoch = get_score_from_metric_raw(metric_data=metric_data, metric_name='epoch')
                step = get_score_from_metric_raw(metric_data=metric_data, metric_name='step')

                for name in metric_names:
                    metric = get_score_from_metric_raw(metric_data=metric_data, metric_name=name)

                    if metric is not None:
                        # Loss指标写入后更新 step 评价指标更新后，更新epoch
                        if step > last_step and name == LOSS_METRIC_NAME:
                            bcelogger.info(f"Track metric {name} with value: {metric} on step {step}")
                            tracker_client.log_metrics(metrics={name: metric}, step=step)
                            last_step = step
                        if epoch > last_epoch and name != LOSS_METRIC_NAME:
                            bcelogger.info(f"Track metric {name} with value: {metric} on epoch {epoch}")
                            tracker_client.log_metrics(metrics={name: metric}, step=epoch, epoch=epoch)
                            last_epoch = epoch
            return last_epoch, last_step
        except Exception as e:
            bcelogger.error(f"Track metric failed: {e}")
            return last_epoch, last_step
    return last_epoch, last_step


if __name__ == "__main__":
    args = parse_args()
    train(args=args)
