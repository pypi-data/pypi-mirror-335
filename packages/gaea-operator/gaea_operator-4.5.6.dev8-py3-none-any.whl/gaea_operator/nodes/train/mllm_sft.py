#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/4/12
# @Author  : liyinggang
# @File    : train_component.py
"""
import os
import json
import base64

from gaea_tracker import ExperimentTracker
from bcelogger.base_logger import setup_logger
from windmillmodelv1.client.model_api_model import parse_model_name
from windmillmodelv1.client.model_api_model import ModelName
from windmillmodelv1.client.model_api_modelstore import parse_modelstore_name
from windmillclient.client.windmill_client import WindmillClient
import bcelogger

from gaea_operator.dataset import MSSWIFTDataset
from gaea_operator.config import MLLMSFTConfig, KEY_NETWORK_ARCHITECTURE, KEY_EARLY_STOPPING
from gaea_operator.metric.types.v2.train_metric import MetricName
from gaea_operator.trainer import Trainer
from gaea_operator.model import Model
from gaea_operator.metric import get_score_from_file, update_metric_file_with_dataset
from gaea_operator.utils import write_file, is_base64, ModelTemplate
from gaea_operator.argument.train_args import parse_args


def codetr_train(args):
    """
    Train component for ppyoloe_plus_m model.
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
    ms_swift_dataset = MSSWIFTDataset(windmill_client=windmill_client,
                                      work_dir=tracker_client.work_dir,
                                      extra_work_dir=tracker_client.extra_work_dir)
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
    ms_swift_dataset.concat_dataset(dataset_name=args.train_dataset_name,
                                    base_dataset_name=args.base_train_dataset_name,
                                    output_dir=dataset_uri,
                                    usage=ms_swift_dataset.usages[0])

    # 2. 合并val分片数据集
    ms_swift_dataset.concat_dataset(dataset_name=args.val_dataset_name,
                                    base_dataset_name=args.base_val_dataset_name,
                                    output_dir=dataset_uri,
                                    usage=ms_swift_dataset.usages[1])

    # 兼容json串传入
    if is_base64(args.advanced_parameters):
        train_advanced_parameters = json.loads(base64.b64decode(args.advanced_parameters))
    else:
        train_advanced_parameters = json.loads(args.advanced_parameters)
    model_template = ModelTemplate(algorithm=ModelTemplate.MLLM_NAME)
    network_architecture = train_advanced_parameters[KEY_NETWORK_ARCHITECTURE]
    train_advanced_parameters[KEY_NETWORK_ARCHITECTURE] = \
        model_template.suggest_network_architecture(train_advanced_parameters[KEY_NETWORK_ARCHITECTURE])
    bcelogger.info(f"Advanced parameters: {train_advanced_parameters}")
    # 3. 下载预训练模型
    pretrained_names = train_advanced_parameters[KEY_NETWORK_ARCHITECTURE]
    pretrain_name = ModelName(workspace_id=parse_modelstore_name(args.public_model_store).workspace_id,
                              model_store_name=parse_modelstore_name(args.public_model_store).local_name,
                              local_name=pretrained_names).get_name()
    pretrain_model_uri = "/home/windmill/tmp/pretrain"
    mllm_model = windmill_client.get_model(workspace_id=parse_model_name(pretrain_name).workspace_id,
                                           model_store_name=parse_model_name(pretrain_name).model_store_name,
                                           local_name=parse_model_name(pretrain_name).local_name)
    windmill_client.download_artifact(object_name=pretrain_name, version="latest", output_uri=pretrain_model_uri)

    # 4. 生成训练配置文件，固定名字 train_config.yaml，保存在 model_uri
    config = MLLMSFTConfig(windmill_client=windmill_client, tracker_client=tracker_client)
    config.write_train_config(dataset_uri=dataset_uri,
                              model_uri=args.output_model_uri,
                              advanced_parameters=train_advanced_parameters,
                              pretrain_model_uri=pretrain_model_uri)
    early_stopping_parameters = {"is_early_stopping": args.is_early_stopping,
                                 "early_stopping_patience": args.early_stopping_patience}
    extend_parameters = {KEY_EARLY_STOPPING: early_stopping_parameters}
    config.write_extend_config(model_uri=args.output_model_uri, extend_parameters=extend_parameters)

    # 5. 训练
    trainer = Trainer(framework="PyTorch", tracker_client=tracker_client)
    metric_names = [MetricName.loss.value, MetricName.token_accuracy.value]
    trainer.track_model_score(metric_names=metric_names)
    trainer.track_train_log(output_uri=args.output_uri)
    trainer.launch()

    # 6. 更新指标文件
    update_metric_file_with_dataset(dataset_name=args.train_dataset_name,
                                    input_dir=args.output_model_uri,
                                    file_name="metric.json")

    # 7. 创建模型
    metric_name = MetricName.token_accuracy.value
    current_score = get_score_from_file(filepath=os.path.join(args.output_model_uri, "metric.json"),
                                        metric_name=metric_name)
    best_score, version = Model(windmill_client=windmill_client). \
        get_best_model_score(model_name=args.model_name, metric_name=metric_name)
    tags = mllm_model.artifact["tags"] if mllm_model.artifact["tags"] is not None else {}
    tags.update({metric_name: str(current_score),
                        KEY_NETWORK_ARCHITECTURE: network_architecture,
                        "SFT": "Full"})
    alias = None
    if current_score >= best_score and version is not None:
        alias = ["best"]
        bcelogger.info(
            f"{metric_name.capitalize()} current score {current_score} >= {best_score}, update [best]")
        tags.update(
            {"bestReason": f"current.score({current_score}) greater than {version}.score({best_score})"})
    if version is None:
        alias = ["best"]
        bcelogger.info(f"First alias [best] score: {current_score}")
        tags.update({"bestReason": f"current.score({current_score})"})
    bcelogger.info(f"Tags: {tags}")
    prefer_model_server_parameters = mllm_model.preferModelServerParameters
    prefer_model_server_parameters["resource"]["accelerator"] = args.accelerator
    model_name = parse_model_name(args.model_name)
    workspace_id = model_name.workspace_id
    model_store_name = model_name.model_store_name
    local_name = model_name.local_name
    config.metadata['modelSize'] = mllm_model.artifact["metadata"].get("modelSize", "8B")
    response = windmill_client.create_model(workspace_id=workspace_id,
                                            model_store_name=model_store_name,
                                            local_name=local_name,
                                            display_name=args.model_display_name,
                                            prefer_model_server_parameters=prefer_model_server_parameters,
                                            prefer_model_server_kind=mllm_model.preferModelServerKind,
                                            category=mllm_model.category["category"],
                                            model_formats=mllm_model.modelFormats,
                                            artifact_alias=alias,
                                            artifact_tags=tags,
                                            artifact_metadata=config.metadata,
                                            artifact_uri=args.output_model_uri)
    bcelogger.info(f"Model {args.model_name} created response: {response}")

    # 7. 输出文件
    write_file(obj=json.loads(response.raw_data)["artifact"], output_dir=args.output_model_uri)


def remove_component_argv():
    '''
    删除组件参数，防止与训练脚本冲突
    '''
    import sys
    all_argv = sys.argv
    script_index = 0
    for i in range(1, len(all_argv)):
        if all_argv[i].endswith(".py"):
            script_index = i
            break

    if script_index > 0:
        sys.argv = all_argv[0:1] + all_argv[script_index:]


if __name__ == "__main__":
    args = parse_args()
    remove_component_argv()
    codetr_train(args=args)