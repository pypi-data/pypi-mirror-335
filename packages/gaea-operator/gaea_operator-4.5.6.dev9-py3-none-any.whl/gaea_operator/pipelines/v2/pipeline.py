#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @File    : ocrnet_pipeline.py
"""
import os
from typing import List
import yaml
from paddleflow.pipeline import Pipeline
from paddleflow.pipeline import CacheOptions
from paddleflow.pipeline import FailureOptions

from gaea_operator.artifacts import Variable
from gaea_operator.utils import Accelerator
from gaea_operator.nodes import ImageV2 as Image
from gaea_operator.nodes import Properties
from gaea_operator.nodes import Train, Eval, Transform, TransformEval, Package, Inference

config = yaml.load(open(os.path.join(os.path.dirname(__file__), "config.yaml")), Loader=yaml.FullLoader)


@Pipeline(
    name=config["pipeline"]["name"],
    cache_options=CacheOptions(enable=True, max_expired_time=604800),
    parallelism=6,
    failure_options=FailureOptions(strategy="continue"),
)
def pipeline(accelerator: str = "T4",
             train_accelerator: str = "V100",
             eval_accelerator: str = "V100",
             transform_accelerator: str = None,
             transform_eval_accelerator: str = None,
             package_accelerator: str = None,
             inference_accelerator: str = None,
             train_skip: int = -1,
             eval_skip: int = -1,
             transform_skip: int = -1,
             transform_eval_skip: int = -1,
             package_skip: int = -1,
             inference_skip: int = -1,
             eval_inputs: List[Variable] = None,
             transform_inputs: List[Variable] = None,
             transform_eval_inputs: List[Variable] = None,
             package_inputs: List[Variable] = None,
             inference_inputs: List[Variable] = None,
             extra_fs_name: str = "vistudio",
             extra_fs_mount_path: str = "/home/paddleflow/storage/mnt/fs-root-vistudio",
             windmill_ak: str = "",
             windmill_sk: str = "",
             org_id: str = "",
             user_id: str = "",
             windmill_endpoint: str = "",
             experiment_kind: str = "",
             experiment_name: str = "",
             modelstore_name: str = "",
             tracking_uri: str = "",
             project_name: str = "",
             scene: str = "",
             train_dataset_name: str = "",
             val_dataset_name: str = "",
             base_train_dataset_name: str = "",
             base_val_dataset_name: str = "",
             train_model_name: str = "",
             train_model_display_name: str = "",
             eval_dataset_name: str = "",
             eval_model_name: str = "",
             transform_input_model_name: str = "",
             transform_model_name: str = "",
             transform_model_display_name: str = "",
             transform_eval_input_model_name: str = "",
             transform_advanced_parameters: str = "",
             ensemble_model_name: str = "",
             ensemble_model_display_name: str = "",
             inference_input_model_name: str = ""):
    """
    Pipeline for training eval transform transform-eval package inference.
    """
    base_params = {"flavour": "c4m16gpu1",
                   "queue": "qtrain",
                   "windmill_ak": windmill_ak,
                   "windmill_sk": windmill_sk,
                   "org_id": org_id,
                   "user_id": user_id,
                   "windmill_endpoint": windmill_endpoint,
                   "experiment_name": experiment_name,
                   "experiment_kind": experiment_kind,
                   "tracking_uri": tracking_uri,
                   "project_name": project_name,
                   "model_store_name": modelstore_name,
                   "scene": scene,
                   "role": "false"}
    base_env = {"PF_JOB_FLAVOUR": "{{flavour}}",
                "PF_JOB_QUEUE_NAME": "{{queue}}",
                "WINDMILL_AK": "{{windmill_ak}}",
                "WINDMILL_SK": "{{windmill_sk}}",
                "ORG_ID": "{{org_id}}",
                "USER_ID": "{{user_id}}",
                "WINDMILL_ENDPOINT": "{{windmill_endpoint}}",
                "EXPERIMENT_KIND": "{{experiment_kind}}",
                "EXPERIMENT_NAME": "{{experiment_name}}",
                "TRACKING_URI": "{{tracking_uri}}",
                "PROJECT_NAME": "{{project_name}}",
                "SCENE": "{{scene}}",
                "PIPELINE_ROLE": "windmill"}

    name_to_images = {}
    for name, node in config["nodes"].items():
        name_to_images[name] = [Image(**image) for image in node["images"]]

    pre_nodes = {}
    if accelerator is None:
        accelerator = Accelerator.T4

    # 1. Train
    if train_accelerator is None:
        train_accelerator = accelerator
    train = Train(config=config["nodes"][Train.name()],
                  train_skip=train_skip,
                  algorithm=config["pipeline"]["algorithm"],
                  accelerator=train_accelerator)
    train.properties = Properties(images=name_to_images[train.name()])
    train_step = train(base_params=base_params,
                       base_env=base_env,
                       extra_fs_name=extra_fs_name,
                       extra_fs_mount_path=extra_fs_mount_path,
                       train_dataset_name=train_dataset_name,
                       val_dataset_name=val_dataset_name,
                       base_train_dataset_name=base_train_dataset_name,
                       base_val_dataset_name=base_val_dataset_name,
                       train_model_name=train_model_name,
                       train_model_display_name=train_model_display_name)
    pre_nodes[train_step.name] = train_step

    # 2. Eval
    if eval_accelerator is None:
        eval_accelerator = accelerator
    eval = Eval(config=config["nodes"][Eval.name()],
                eval_skip=eval_skip,
                algorithm=config["pipeline"]["algorithm"],
                accelerator=eval_accelerator,
                pre_nodes=pre_nodes)
    eval.inputs = eval_inputs
    eval.properties = Properties(images=name_to_images[eval.name()])
    eval_step = eval(base_params=base_params,
                     base_env=base_env,
                     eval_dataset_name=eval_dataset_name,
                     eval_model_name=eval_model_name)
    pre_nodes[eval_step.name] = eval_step

    # 3. Transform
    if transform_accelerator is None:
        transform_accelerator = accelerator
    transform = Transform(config=config["nodes"][Transform.name()],
                          transform_skip=transform_skip,
                          algorithm=config["pipeline"]["algorithm"],
                          accelerator=transform_accelerator,
                          pre_nodes=pre_nodes)
    transform.inputs = transform_inputs
    transform.properties = Properties(images=name_to_images[transform.name()])
    transform_step = transform(base_params=base_params,
                               base_env=base_env,
                               train_model_name=transform_input_model_name,
                               transform_model_name=transform_model_name,
                               transform_model_display_name=transform_model_display_name,
                               advanced_parameters=transform_advanced_parameters)
    pre_nodes[transform_step.name] = transform_step

    # 4. TransformEval
    if transform_eval_accelerator is None:
        transform_eval_accelerator = accelerator
    transform_eval = TransformEval(config=config["nodes"][TransformEval.name()],
                                   transform_eval_skip=transform_eval_skip,
                                   algorithm=config["pipeline"]["algorithm"],
                                   accelerator=transform_eval_accelerator,
                                   pre_nodes=pre_nodes)
    transform_eval.inputs = transform_eval_inputs
    transform_eval.properties = Properties(images=name_to_images[transform_eval.name()])
    transform_eval_step = transform_eval(base_params=base_params,
                                         base_env=base_env,
                                         dataset_name=eval_dataset_name,
                                         transform_model_name=transform_eval_input_model_name)
    pre_nodes[transform_eval_step.name] = transform_eval_step

    # 5. Package
    if package_accelerator is None:
        package_accelerator = accelerator
    package = Package(config=config["nodes"][Package.name()],
                      package_skip=package_skip,
                      algorithm=config["pipeline"]["algorithm"],
                      accelerator=package_accelerator,
                      pre_nodes=pre_nodes)
    package.inputs = package_inputs
    package.properties = Properties(images=name_to_images[package.name()])
    package_step = package(base_params=base_params,
                           base_env=base_env,
                           transform_model_name=transform_eval_input_model_name,
                           ensemble_model_name=ensemble_model_name,
                           sub_extra_models="",
                           ensemble_model_display_name=ensemble_model_display_name)
    pre_nodes[package_step.name] = package_step

    # 6. Inference
    if inference_accelerator is None:
        inference_accelerator = accelerator
    inference = Inference(config=config["nodes"][Inference.name()],
                          inference_skip=inference_skip,
                          algorithm=config["pipeline"]["algorithm"],
                          accelerator=inference_accelerator,
                          pre_nodes=pre_nodes)
    inference.inputs = inference_inputs
    inference.properties = Properties(images=name_to_images[inference.name()])
    inference_step = inference(base_params=base_params,
                               base_env=base_env,
                               ensemble_model_name=inference_input_model_name,
                               dataset_name=eval_dataset_name)
    pre_nodes[inference_step.name] = inference_step

    return None


if __name__ == "__main__":
    pipeline_client = pipeline(
        accelerator="T4",
        train_accelerator="V100",
        eval_accelerator="V100",
        transform_accelerator="T4",
        transform_eval_accelerator="T4",
        package_accelerator="T4",
        inference_accelerator="T4",
        windmill_ak="a1a9069e2b154b2aa1a83ed12316d163",
        windmill_sk="eefac23d2660404e93855197ce60efb3",
        windmill_endpoint="http://10.27.240.5:8340",
        experiment_kind="Aim",
        experiment_name="test",
        tracking_uri="aim://10.27.240.5:8329",
        project_name="workspaces/internal/projects/proj-o97H2oAE",
        train_dataset_name="workspaces/internal/projects/proj-o97H2oAE/datasets/ds-tQLjA9NM/versions/1",
        val_dataset_name="workspaces/internal/projects/proj-o97H2oAE/datasets/ds-tQLjA9NM/versions/1",
        eval_dataset_name="workspaces/internal/projects/proj-o97H2oAE/datasets/ds-tQLjA9NM/versions/1",
        train_model_name="workspaces/internal/modelstores/ms-6TDGY7Hv/models/ocrnet-model",
        train_model_display_name="ocrnet",
        eval_model_name="workspaces/internal/modelstores/ms-6TDGY7Hv/models/ocrnet/versions/latest",
        transform_input_model_name="workspaces/internal/modelstores/ms-6TDGY7Hv/models/ocrnet/versions/latest",
        transform_model_name="workspaces/internal/modelstores/ms-6TDGY7Hv/models/ocrnet-t4",
        transform_model_display_name="ocrnet-t4",
        transform_eval_input_model_name="workspaces/internal/modelstores/ms-6TDGY7Hv/models/ocrnet-t4/versions/latest",
        ensemble_model_name="workspaces/internal/modelstores/ms-6TDGY7Hv/models/ocrnet-ensemble",
        ensemble_model_display_name="ocrnet-ensemble",
        inference_input_model_name="workspaces/internal/modelstores/ms-6TDGY7Hv/models/ocrnet-ensemble/versions/latest"
    )
    pipeline_client.compile(save_path="pipeline.yaml")
    _, run_id = pipeline_client.run(fs_name="vistudio")
