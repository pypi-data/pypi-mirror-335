#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2025/3/12
# @Author  : zhoubohan
# @File    : upload.py
"""
import os
import re
import tarfile
from argparse import ArgumentParser

from jobv1.client.job_api_event import EventKind
from jobv1.client.job_api_job import parse_job_name
from jobv1.client.job_api_metric import MetricLocalName, MetricKind, CounterKind, DataType
from jobv1.client.job_client import JobClient
from jobv1.tracker.tracker import Tracker
from windmillclient.client.windmill_client import WindmillClient
from windmillcomputev1.filesystem import upload_by_filesystem


def parse_args():
    """
    Parse arguments.
    """
    parser = ArgumentParser()
    parser.add_argument("--name", required=True, type=str, default=None)
    parser.add_argument("--dest_uri", required=True, type=str, default=None)
    parser.add_argument("--source_uri", required=False, type=str, default=".")


    args, _ = parser.parse_known_args()

    return args


def extract_workspace_id(name):
    """
    extract workspace id from path.
    """
    match = re.search(r'workspaces/([^/]+)', name)
    return match.group(1) if match else None


def run():
    """
    upload file.
    """
    job_name = os.getenv("JOB_NAME")
    task_name = os.getenv("PF_STEP_NAME")
    error_msg = ""
    tracker = None
    try:
        org_id = os.getenv("ORG_ID")
        user_id = os.getenv("USER_ID")
        windmill_endpoint = os.getenv("WINDMILL_ENDPOINT")

        args = parse_args()
        context = {"OrgID": org_id, "UserID": user_id}

        windmill_client = WindmillClient(endpoint=windmill_endpoint,
                                         context=context)

        if job_name is not None:
            parsed_job_name = parse_job_name(job_name)
            job_client = JobClient(endpoint=windmill_endpoint, context=context)
            tracker = Tracker(
                client=job_client,
                job_name=parsed_job_name.local_name,
                workspace_id=parsed_job_name.workspace_id,
                task_name=task_name
            )

            tracker.log_metric(
                local_name=MetricLocalName.Total,
                kind=MetricKind.Counter,
                counter_kind=CounterKind.Cumulative,
                data_type=DataType.Int,
                value=[str(1)],
            )



        workspace_id = extract_workspace_id(args.name)

        filesystem = windmill_client.suggest_first_filesystem(
            workspace_id=workspace_id,
            guest_name=args.name,
        )

        file_path = os.path.join(args.source_uri, os.path.basename(args.dest_uri))
        extension = os.path.splitext(file_path)[1]

        if extension == ".tar":
            with tarfile.open(file_path, "w:") as tar:
                tar.add(args.source_uri, arcname=os.path.basename(args.source_uri))


        upload_by_filesystem(filesystem=filesystem, file_path=file_path, dest_path=args.dest_uri)

        print(f"Upload File Success {args}")
        metric_name = MetricLocalName.Success
    except Exception as e:
        print(f"Upload File Failed {args}: {e}")
        error_msg = str(e)
        metric_name = MetricLocalName.Failed


    if job_name is not None:
        tracker.log_metric(
            local_name=metric_name,
            kind=MetricKind.Counter,
            counter_kind=CounterKind.Cumulative,
            data_type=DataType.Int,
            value=[str(1)],
        )
        
        tracker.log_metric(
            local_name=metric_name,
            kind=MetricKind.Counter,
            counter_kind=CounterKind.Cumulative,
            data_type=DataType.Int,
            value=[str(1)],
            task_name=""
        )

        if metric_name == MetricLocalName.Failed:
            tracker.log_event(
                kind=EventKind.Failed,
                reason=f"文件上传失败",
                message=error_msg[:500],
            )

            tracker.log_event(
                kind=EventKind.Failed,
                reason=f"文件上传失败",
                message=error_msg[:500],
                task_name=""
            )

if __name__ == "__main__":
    run()
