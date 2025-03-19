#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2025/2/28
# @Author  : jiangwen04
# @File    : pdc_launch.py
"""
import bcelogger
import sys
import os
import json
import base64
import shutil

from gaea_tracker import ExperimentTracker
from windmilltrainingv1.client.training_api_job import parse_job_name
from windmillcomputev1.client.compute_api_filesystem import parse_filesystem_name

from gaea_operator.trainer.pdc.config.afs_config import write_afs_config
from gaea_operator.utils import is_base64

CONFIG_INI = "config.ini"
COPY_LOG_FILE_SH = "cmd/copy_log_file.sh"
JOB_STATUS_CHECK_FILE_SH = "cmd/job_status_check_file.sh"


class PDCLaunch:
    """
        Trainer for PDC
    """

    def __init__(self, track_client: ExperimentTracker, framework):
        """
            Initialize the PDC trainer
        Args:
            pdc_config (dict): Configuration dictionary for PDC
        """
        self.framework = framework
        self.track_client = track_client

    def __call__(self):
        """
            Train the PDC model
        Returns:
            None
        """

        windmill_client = self.track_client.windmill_client
        shell_dir = "/tmp/run_shell"
        filesystem = self.get_filesystem(windmill_client)
        self.write_mount_config(filesystem, shell_dir)
        remove_component_argv()
        pdc_params = os.environ["PDC_PARAMS"]
        if is_base64(pdc_params):
            pdc_parameter = json.loads(base64.b64decode(pdc_params))
        else:
            pdc_parameter = json.loads(pdc_params)
        args = sys.argv
        submit_job_command = self.create_runshell_cmd(args, pdc_parameter, shell_dir)
        bcelogger.info(f"submit job command: {submit_job_command}")
        import subprocess
        result = subprocess.run(submit_job_command,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise Exception(result.stderr.decode())
        bcelogger.info(f"submit job success, job_name: {self.track_client.experiment_name}")
        job_status_check_command = (f"sh {shell_dir}/job_status_check_file.sh {pdc_parameter['pdc_ak']}"
                                    f" {pdc_parameter['pdc_sk']} "
                                    f" {parse_job_name(self.track_client.job_name).local_name}")
        result = subprocess.run(job_status_check_command,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise Exception(result.stderr.decode())

    def create_runshell_cmd(self, args, pdc_parameter, shell_dir):
        """
        Create the command to run the PDC
        """
        self.create_job_shell_file(args, shell_dir)
        config_ini_path = os.path.join(shell_dir, CONFIG_INI)
        write_afs_config(config_ini_path)
        submit_job_command = f"paddlecloud job --ak {pdc_parameter['pdc_ak']} --sk {pdc_parameter['pdc_sk']} \
        train --job-name {parse_job_name(self.track_client.job_name).local_name} \
        --job-conf {config_ini_path}\
        --group-name {pdc_parameter['train_group_name']} \
        --file-dir {shell_dir} \
        --job-version paddle-fluid-custom  \
        --k8s-gpu-cards {pdc_parameter['k8s_gpu_cards']} \
        --k8s-priority normal \
        --image-addr {os.environ['IMAGE']} \
        --is-standalone 1 \
        --algo-id {pdc_parameter['algo_id']} \
        --start-cmd  'sh run_shell/run_task.sh' "
        return submit_job_command

    def create_job_shell_file(self, args, shell_dir):
        """
        create the shell file for the job
        """
        mount_cmd = (f"cd /root/paddlejob/workspace/env_run/run_shell/ &&"
                     f" mkdir -p {self.track_client.work_dir} && nohup pfs-fuse-bns mount"
                     f" --mount-point={self.track_client.work_dir} --meta-cache-expire=24000h --meta-cache-driver=disk "
                     f" --entry-cache-expire=1h --meta-cache-path=/var/cache/meta-cache/ "
                     f" --config=/root/paddlejob/workspace/env_run/run_shell/mount_config.config "
                     f" --reuse-meta-cache=true & \n ")
        output_uri = os.environ["OUTPUT_URI"]
        if self.framework == 'PaddlePaddle':
            train_cmd = f"python3 -m paddle.distributed.launch {' '.join(args)}"
        else:
            train_cmd = f"python3 -m torch.distributed.run..main {' '.join(args)}"
        train_cmd = 'sleep 10 && ' + train_cmd + "\n"
        env_cmd = (f"export WINDMILL_EXPERIMENT_WORK_DIR={self.track_client.job_work_dir}"
                   f"  && export WINDMILL_EXPERIMENT_RUN_ID={self.track_client.run_id} \n")
        copy_log_file_cmd = f"nohup sh run_shell/copy_log_file.sh {output_uri} & \n"
        shutil.copy(os.path.dirname(os.path.abspath(__file__)) + "/" + COPY_LOG_FILE_SH, shell_dir)
        shutil.copy(os.path.dirname(os.path.abspath(__file__)) + "/" + JOB_STATUS_CHECK_FILE_SH, shell_dir)
        finale_copy_file = f"\\cp -rf `pwd`/log/* {output_uri}"
        with open(shell_dir + "/run_task.sh", "w") as f:
            f.write(env_cmd)
            f.write(mount_cmd)
            f.write(copy_log_file_cmd)
            f.write(train_cmd)
            f.write(finale_copy_file)

    def write_mount_config(self, filesystem, shell_dir):
        """
        Write the mount configuration file for the filesystem
        """
        credential = filesystem.credential
        endpoint = filesystem.endpoint
        bucket = endpoint.split('/')[0]
        sub_path = endpoint.replace(bucket, '')
        credential['region'] = filesystem.config['region']
        credential['bucket'] = bucket
        credential['endpoint'] = filesystem.host
        credential[
            'bns'] = ("group.bos-B-nginx-bjlsh.BCE.all,group.bos-B-nginx-bjdd.BCE.all,group.bos-B-nginx-bjga.BCE.all,"
                      "group.bos-B-nginx-bjyz.BCE.all")
        mount_config = {"type": filesystem.kind, "subPath": sub_path, "properties": credential}
        if os.path.exists(shell_dir) is False:
            os.mkdir(shell_dir)
        with open(shell_dir + "/mount_config.config", "w") as f:
            json.dump(mount_config, f)

    def get_filesystem(self, windmill_client):
        """
        Get the filesystem from the windmill client
        """
        job_name = parse_job_name(self.track_client.job_name)
        response = windmill_client.get_job(workspace_id=job_name.workspace_id,
                                           project_name=job_name.project_name,
                                           local_name=job_name.local_name)
        fileSystemName = response.fileSystemName
        filesystem = parse_filesystem_name(fileSystemName)
        filesystem = windmill_client.get_filesystem_credential(workspace_id=filesystem.workspace_id,
                                                               local_name=filesystem.local_name)
        return filesystem


def remove_component_argv():
    '''
    删除组件参数，防止与训练脚本冲突
    '''
    all_argv = sys.argv
    script_index = 0
    for i in range(1, len(all_argv)):
        if all_argv[i].endswith(".py"):
            script_index = i
            break
    # 默认单机多卡 必须指定 nproc-per-node
    if script_index > 0:
        sys.argv = all_argv[script_index:]
